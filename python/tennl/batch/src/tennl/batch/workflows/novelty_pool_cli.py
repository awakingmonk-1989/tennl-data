"""Novelty-pool CLI — single-run and batch-run with creative control rotation.

Single run:
    UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run python -m tennl.batch.workflows.novelty_pool_cli single \
        --topic "Home & Living" --sub-topic "Daily Living Hacks" \
        --content-mode guide --angle practical_breakdown --tone calm --hook-style practical_problem

Batch run:
    UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run python -m tennl.batch.workflows.novelty_pool_cli batch \
        --invocations 5 --topics-json /absolute/path/to/topics.json
"""

from __future__ import annotations

import argparse
import asyncio
import concurrent.futures
import json
import logging
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .azure_storage import (
    generate_entity_id,
    generate_workflow_execution_id,
    write_to_azure_storage,
)
from .settings import AppSettings
from .workflow import ContentGenWorkflow
from .tracing import (
    RunContext,
    install_llamaindex_instrumentation_logging,
    log_workflow_event_stream,
    setup_rolling_jsonl_logger,
    setup_rolling_run_logger,
)

logger = logging.getLogger(__name__)

BATCH_FUTURE_RESULT_TIMEOUT_S_DEFAULT = 120

# ---------------------------------------------------------------------------
# Pool constants (content_gen_novelty_spec §2–§3)
# ---------------------------------------------------------------------------

INTENT_PROFILE: list[str] = [
    "relatable",
    "useful",
    "hopeful",
    "grounded",
]

CONTENT_MODE_POOL: list[str] = [
    "story",
    "analysis",
    "guide",
    "reflection",
    "comparison",
]

ANGLE_POOL: list[str] = [
    "personal_experience",
    "decision_support",
    "mistake_recovery",
    "trend_interpretation",
    "myth_busting",
    "practical_breakdown",
]

TONE_POOL: list[str] = [
    "honest",
    "encouraging",
    "calm",
    "grounded",
]

HOOK_STYLE_POOL: list[str] = [
    "observation",
    "contrarian",
    "practical_problem",
    "small_truth",
    "unexpected_pattern",
]

QUALITY_CONSTRAINTS: dict[str, list[str]] = {
    "must_include": [
        "specific_scenario",
        "realistic_takeaway",
        "non_generic_language",
    ],
    "avoid": [
        "clickbait",
        "template_openings",
        "generic_motivation",
        "repetitive_listicle_style",
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rotate_pick(pool: list[str], index: int) -> str:
    """Pick pool[index % len(pool)]."""
    return pool[index % len(pool)]


def _load_topics(path: str) -> list[dict[str, str]]:
    """Load topics list from a JSON file.

    Accepts both a root-level list and a dict with a single list value.
    Each entry must have ``topic`` and ``subtopic`` keys.
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, list):
        entries = raw
    elif isinstance(raw, dict):
        lists = [v for v in raw.values() if isinstance(v, list)]
        if not lists:
            raise ValueError(f"No list found in topics JSON: {path}")
        entries = lists[0]
    else:
        raise ValueError(f"Unexpected root type in topics JSON: {type(raw).__name__}")

    for i, e in enumerate(entries):
        if "topic" not in e or "subtopic" not in e:
            raise ValueError(f"Entry {i} missing 'topic' or 'subtopic': {e}")
    return entries


def _write_artifacts(run_id: str, article_md: str, article_json: dict) -> Path:
    out_dir = Path("out") / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "article.md").write_text(article_md, encoding="utf-8")
    (out_dir / "article.json").write_text(
        json.dumps(article_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return out_dir


def _print_trace_summary(result: dict) -> None:
    traces = result.get("execution_trace", [])
    if not traces:
        return
    print("\n--- Execution Trace ---")
    for t in traces:
        node = t.get("node_id", "?")
        name = t.get("node_name", "?")
        res = t.get("result", "?")
        ms = t.get("duration_ms", 0)
        summary = t.get("output_summary", "")
        print(f"  {node} {name}: {res} ({ms}ms) — {summary}")
    print("--- End Trace ---\n")


def _print_article_summary(article_md: str, article_json: dict) -> None:
    words = len(article_md.split())
    sections = article_json.get("sections", article_json.get("posts", []))
    dd_count = sum(1 for s in sections if isinstance(s, dict) and s.get("sub_sections"))
    hero = article_json.get("hero", {})
    print(f"  Title: {hero.get('title_line_1', '?')} — {hero.get('title_line_2', '')}")
    print(f"  Words: ~{words}  |  Sections: {len(sections)}  |  Deep dives: {dd_count}")


def _try_azure_persist(args_topic: str, args_sub_topic: str, result: dict) -> None:
    conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
    if not conn_str:
        logger.info("AZURE_STORAGE_CONNECTION_STRING not set — skipping Azure persistence")
        return
    settings = AppSettings()
    ct = settings.content_type
    wf_exec_id = generate_workflow_execution_id(ct)
    ent_id = generate_entity_id(ct)
    info = write_to_azure_storage(
        connection_string=conn_str,
        container_name="content",
        content_type=ct,
        category=args_topic.lower().replace(" ", ""),
        sub_category=args_sub_topic.lower().replace(" ", ""),
        workflow_execution_id=wf_exec_id,
        entity_id=ent_id,
        article_md=result["article_md"],
        article_json=result["article_json"],
    )
    print(f"  Azure blob: {info['blob_url']}")
    print(f"  wfExecId:   {info['workflow_execution_id']}")
    print(f"  entityId:   {info['entity_id']}")


# ---------------------------------------------------------------------------
# Core run helper (shared by single + batch)
# ---------------------------------------------------------------------------

async def _execute_single_run(
    *,
    topic: str,
    sub_topic: str,
    content_variant: str,
    content_mode: str,
    angle: str,
    tone: str,
    hook_style: str,
    eval_mode: str,
    max_refine_attempts: int,
    timeout: int,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Execute one workflow run with full novelty-pool inputs. Returns result dict."""
    run_id = run_id or str(uuid.uuid4())
    trace_logger = setup_rolling_jsonl_logger()
    setup_rolling_run_logger()
    install_llamaindex_instrumentation_logging()

    w = ContentGenWorkflow(timeout=timeout, verbose=False)
    handler = w.run(
        topic=topic,
        sub_topic=sub_topic,
        content_variant=content_variant,
        eval_mode=eval_mode,
        max_refine_attempts=max_refine_attempts,
        run_id=run_id,
        intent_profile=INTENT_PROFILE,
        content_mode_pool=CONTENT_MODE_POOL,
        angle_pool=ANGLE_POOL,
        tone_pool=TONE_POOL,
        hook_style_pool=HOOK_STYLE_POOL,
        quality_constraints=QUALITY_CONSTRAINTS,
        content_mode=content_mode,
        angle=angle,
        tone=tone,
        hook_style=hook_style,
    )
    stream_task = asyncio.create_task(
        log_workflow_event_stream(handler, run_id=run_id, logger=trace_logger)
    )

    with RunContext(run_id):
        result = await handler

    await stream_task

    # If any libraries scheduled background tasks (e.g., HTTP client shutdown),
    # ensure they are awaited before the event loop closes (important when this
    # coroutine is executed under `asyncio.run()` inside a worker thread).
    try:
        await asyncio.sleep(0)
        pending = [
            t
            for t in asyncio.all_tasks()
            if t is not asyncio.current_task() and not t.done()
        ]
        if pending:
            await asyncio.wait_for(
                asyncio.gather(*pending, return_exceptions=True), timeout=2.0
            )
    except Exception as e:
        logger.error(f"Background task drain failed (non-fatal). Reason: {e!s}", exc_info=True)

    result["_run_id"] = run_id
    result["_topic"] = topic
    result["_sub_topic"] = sub_topic
    result["_content_mode"] = content_mode
    result["_angle"] = angle
    result["_tone"] = tone
    result["_hook_style"] = hook_style
    return result


def _handle_single_result(result: dict[str, Any]) -> int:
    """Single-mode: print summary, write to out/, attempt Azure persist."""
    run_id = result["_run_id"]
    topic = result["_topic"]
    sub_topic = result["_sub_topic"]
    status = result["status"]

    _print_trace_summary(result)

    if status == "GENERATED":
        out_dir = _write_artifacts(run_id, result["article_md"], result["article_json"])
        print(f"GENERATED run_id={run_id} out_dir={out_dir}")
        print(f"  pool: content_mode={result['_content_mode']}  angle={result['_angle']}  tone={result['_tone']}  hook_style={result['_hook_style']}")
        _print_article_summary(result["article_md"], result["article_json"])
        _try_azure_persist(topic, sub_topic, result)
        return 0

    err = result.get("error") or {}
    print(f"FAILED run_id={run_id} reason={err.get('failure_reason')} node={err.get('error_node')}")
    if err.get("error_message"):
        print(f"  message: {err['error_message'][:300]}")
    return 2


def _handle_batch_result(result: dict[str, Any]) -> int:
    """Batch-mode: print summary, Azure persist, PG insert. No per-run file writes."""
    from .pg_storage import insert_article

    pg_pool = result.get("_pg_pool")
    run_id = result["_run_id"]
    topic = result["_topic"]
    sub_topic = result["_sub_topic"]
    status = result["status"]

    _print_trace_summary(result)

    if status == "GENERATED":
        print(f"GENERATED run_id={run_id}")
        print(f"  pool: content_mode={result['_content_mode']}  angle={result['_angle']}  tone={result['_tone']}  hook_style={result['_hook_style']}")
        _print_article_summary(result["article_md"], result["article_json"])
        _try_azure_persist(topic, sub_topic, result)
        insert_article(
            run_id=run_id,
            article_md=result["article_md"],
            article_json=result["article_json"],
            status="success",
            pool=pg_pool,
        )
        return 0

    err = result.get("error") or {}
    failure_reason = err.get("failure_reason", "UNKNOWN")
    error_msg = err.get("error_message", "")
    print(f"FAILED run_id={run_id} reason={failure_reason} node={err.get('error_node')}")
    if error_msg:
        print(f"  message: {error_msg[:300]}")
    insert_article(
        run_id=run_id,
        status="failed",
        reason=failure_reason,
        error_message=error_msg[:2000] if error_msg else None,
        pool=pg_pool,
    )
    return 2


BATCH_FLUSH_SIZE = 25


def _flush_buffer(buffer: list[dict[str, Any]], batch_dir: Path) -> None:
    """Write buffered articles to batch directory and clear the buffer."""
    for item in buffer:
        run_id = item["_run_id"]
        (batch_dir / f"{run_id}.md").write_text(item["article_md"], encoding="utf-8")
        (batch_dir / f"{run_id}.json").write_text(
            json.dumps(item["article_json"], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    print(f"  >> Flushed {len(buffer)} articles to {batch_dir}")
    buffer.clear()


def _buffer_success_and_maybe_flush(
    *,
    buffer: list[dict[str, Any]],
    buffer_item: dict[str, Any],
    batch_dir: Path,
    lock: threading.Lock,
) -> None:
    with lock:
        buffer.append(buffer_item)
        if len(buffer) >= BATCH_FLUSH_SIZE:
            _flush_buffer(buffer, batch_dir)


# ---------------------------------------------------------------------------
# Single-run entry
# ---------------------------------------------------------------------------

async def run_single_cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="novelty_pool_cli single")
    p.add_argument("--topic", required=True)
    p.add_argument("--sub-topic", required=True)
    p.add_argument("--content-variant", default="AI_GENERATED",
                   choices=["CURATED_WEB_WITH_IMAGES", "CURATED_WEB_NO_IMAGES", "AI_GENERATED"])
    p.add_argument("--content-mode", required=True, choices=CONTENT_MODE_POOL)
    p.add_argument("--angle", required=True, choices=ANGLE_POOL)
    p.add_argument("--tone", required=True, choices=TONE_POOL)
    p.add_argument("--hook-style", required=True, choices=HOOK_STYLE_POOL)
    p.add_argument("--eval-mode", default="sequential", choices=["parallel", "sequential"])
    p.add_argument("--max-refine-attempts", type=int, default=1, choices=[0, 1])
    p.add_argument("--timeout", type=int, default=300)
    args = p.parse_args(argv)

    result = await _execute_single_run(
        topic=args.topic,
        sub_topic=args.sub_topic,
        content_variant=args.content_variant,
        content_mode=args.content_mode,
        angle=args.angle,
        tone=args.tone,
        hook_style=args.hook_style,
        eval_mode=args.eval_mode,
        max_refine_attempts=args.max_refine_attempts,
        timeout=args.timeout,
    )
    return _handle_single_result(result)


# ---------------------------------------------------------------------------
# Batch-run entry
# ---------------------------------------------------------------------------

async def run_batch(
    *,
    invocations: int,
    topics_json_path: str,
    content_variant: str = "AI_GENERATED",
    eval_mode: str = "sequential",
    max_refine_attempts: int = 1,
    timeout: int = 300,
    num_workers: int = 1,
    future_result_timeout_s: int = BATCH_FUTURE_RESULT_TIMEOUT_S_DEFAULT,
) -> list[dict[str, Any]]:
    """Run *invocations* workflow calls, rotating pool values and cycling topics.

    File output is buffered: every 25 successful runs, the buffer is flushed
    to ``specs/data/batch_{timestamp}/`` as individual ``{run_id}.md`` +
    ``{run_id}.json`` files. Remaining buffer is flushed after the loop.

    PostgreSQL inserts happen per-run (inside ``_handle_batch_result``).
    Azure persist also happens per-run (unchanged).

    Returns the list of result dicts (one per invocation).
    """
    topics = _load_topics(topics_json_path)
    # Keep only lightweight summaries in memory; do not retain full article payloads.
    results: list[dict[str, Any]] = []

    # Ensure the run log handler is installed even if we crash before threads spin up.
    setup_rolling_run_logger()

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    batch_dir = Path("specs/data") / f"batch_{ts}"
    batch_dir.mkdir(parents=True, exist_ok=True)
    print(f"Batch output directory: {batch_dir}")

    buffer: list[dict[str, Any]] = []
    buffer_lock = threading.Lock()

    if num_workers <= 1:
        # Keep the existing sequential async loop (no thread pool overhead).
        for i in range(invocations):
            entry = topics[i % len(topics)]
            topic = entry["topic"]
            sub_topic = entry["subtopic"]
            content_mode = _rotate_pick(CONTENT_MODE_POOL, i)
            angle = _rotate_pick(ANGLE_POOL, i)
            tone = _rotate_pick(TONE_POOL, i)
            hook_style = _rotate_pick(HOOK_STYLE_POOL, i)

            print(f"\n{'='*72}")
            print(f"BATCH [{i+1}/{invocations}]  topic={topic!r}  sub_topic={sub_topic!r}")
            print(f"  content_mode={content_mode}  angle={angle}  tone={tone}  hook_style={hook_style}")
            print(f"{'='*72}")

            result = await _execute_single_run(
                topic=topic,
                sub_topic=sub_topic,
                content_variant=content_variant,
                content_mode=content_mode,
                angle=angle,
                tone=tone,
                hook_style=hook_style,
                eval_mode=eval_mode,
                max_refine_attempts=max_refine_attempts,
                timeout=timeout,
            )
            exit_code = _handle_batch_result(result)

            # Buffer only what we need for disk flush.
            if result["status"] == "GENERATED":
                buffer_item = {
                    "_run_id": result["_run_id"],
                    "article_md": result["article_md"],
                    "article_json": result["article_json"],
                }
                _buffer_success_and_maybe_flush(
                    buffer=buffer,
                    buffer_item=buffer_item,
                    batch_dir=batch_dir,
                    lock=buffer_lock,
                )

            # Keep a lightweight summary only (avoid retaining full content in RAM).
            err = result.get("error") or {}
            results.append(
                {
                    "_run_id": result["_run_id"],
                    "status": result["status"],
                    "_batch_index": i,
                    "_batch_exit_code": exit_code,
                    "failure_reason": err.get("failure_reason"),
                    "error_node": err.get("error_node"),
                }
            )
    else:
        # Parallel execution (spec §8.7): one asyncio.run() per thread.
        from psycopg_pool import ConnectionPool
        from .pg_storage import PG_DSN

        with ConnectionPool(
            conninfo=PG_DSN, min_size=num_workers, max_size=num_workers
        ) as pg_pool:
            # Pre-warm the thread pool.
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=num_workers
            ) as executor:
                warm_futs = [executor.submit(lambda: None) for _ in range(num_workers)]
                for f in concurrent.futures.as_completed(warm_futs):
                    # If this ever fails, we want it in logs immediately.
                    try:
                        f.result()
                    except Exception:
                        logger.exception("Thread pool pre-warm future failed", exc_info=True)
                        raise

                def _run_one(invocation_index: int) -> dict[str, Any]:
                    run_id = str(uuid.uuid4())
                    entry = topics[invocation_index % len(topics)]
                    topic = entry["topic"]
                    sub_topic = entry["subtopic"]
                    content_mode = _rotate_pick(CONTENT_MODE_POOL, invocation_index)
                    angle = _rotate_pick(ANGLE_POOL, invocation_index)
                    tone = _rotate_pick(TONE_POOL, invocation_index)
                    hook_style = _rotate_pick(HOOK_STYLE_POOL, invocation_index)

                    async def _run_with_loop_handler() -> dict[str, Any]:
                        # Mitigate noisy shutdown warnings when httpx schedules
                        # AsyncClient.aclose() after the loop begins closing.
                        loop = asyncio.get_running_loop()

                        def _exc_handler(_loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
                            exc = context.get("exception")
                            msg = str(context.get("message", ""))
                            if isinstance(exc, RuntimeError) and "Event loop is closed" in str(exc):
                                if "Task exception was never retrieved" in msg or "exception was never retrieved" in msg:
                                    return
                            _loop.default_exception_handler(context)

                        loop.set_exception_handler(_exc_handler)
                        return await _execute_single_run(
                            topic=topic,
                            sub_topic=sub_topic,
                            content_variant=content_variant,
                            content_mode=content_mode,
                            angle=angle,
                            tone=tone,
                            hook_style=hook_style,
                            eval_mode=eval_mode,
                            max_refine_attempts=max_refine_attempts,
                            timeout=timeout,
                            run_id=run_id,
                        )

                    try:
                        result = asyncio.run(_run_with_loop_handler())
                        # Attach pool so _handle_batch_result can do thread-safe PG insert.
                        result["_pg_pool"] = pg_pool
                        exit_code = _handle_batch_result(result)

                        if result["status"] == "GENERATED":
                            buffer_item = {
                                "_run_id": result["_run_id"],
                                "article_md": result["article_md"],
                                "article_json": result["article_json"],
                            }
                            _buffer_success_and_maybe_flush(
                                buffer=buffer,
                                buffer_item=buffer_item,
                                batch_dir=batch_dir,
                                lock=buffer_lock,
                            )

                        err = result.get("error") or {}
                        return {
                            "_run_id": result["_run_id"],
                            "status": result["status"],
                            "_batch_index": invocation_index,
                            "_batch_exit_code": exit_code,
                            "failure_reason": err.get("failure_reason"),
                            "error_node": err.get("error_node"),
                        }
                    except Exception as e:
                        # This is a "future failed" path (no workflow result dict). Persist
                        # a failure row and then re-raise so the Future captures the error.
                        from .pg_storage import insert_article

                        logger.exception(
                            "Batch worker crashed: invocation_index=%s run_id=%s topic=%r sub_topic=%r",
                            invocation_index,
                            run_id,
                            topic,
                            sub_topic,
                            exc_info=True,
                        )
                        insert_article(
                            run_id=run_id,
                            status="failed",
                            reason="RUNTIME_ERROR",
                            error_message=str(e)[:2000] if str(e) else None,
                            pool=pg_pool,
                        )
                        raise

                futures: dict[concurrent.futures.Future[dict[str, Any]], int] = {}
                for i in range(invocations):
                    entry = topics[i % len(topics)]
                    topic = entry["topic"]
                    sub_topic = entry["subtopic"]
                    content_mode = _rotate_pick(CONTENT_MODE_POOL, i)
                    angle = _rotate_pick(ANGLE_POOL, i)
                    tone = _rotate_pick(TONE_POOL, i)
                    hook_style = _rotate_pick(HOOK_STYLE_POOL, i)
                    print(f"\n{'='*72}")
                    print(f"BATCH [submit {i+1}/{invocations}]  topic={topic!r}  sub_topic={sub_topic!r}")
                    print(f"  content_mode={content_mode}  angle={angle}  tone={tone}  hook_style={hook_style}")
                    print(f"{'='*72}")

                    futures[executor.submit(_run_one, i)] = i

                cancelled: list[tuple[int, BaseException]] = []
                timed_out: list[tuple[int, BaseException]] = []
                failed_futures: list[tuple[int, BaseException]] = []
                ok_count = 0

                t0 = time.monotonic()
                for fut in concurrent.futures.as_completed(futures):
                    idx = futures[fut]
                    try:
                        res = fut.result(timeout=future_result_timeout_s)
                        results.append(res)
                        ok_count += 1
                    except concurrent.futures.CancelledError as e:
                        cancelled.append((idx, e))
                        logger.warning(
                            "Batch future cancelled: invocation_index=%s",
                            idx,
                            exc_info=True,
                        )
                    except concurrent.futures.TimeoutError as e:
                        # This shouldn't normally happen with as_completed(), but we
                        # categorize it explicitly so we never lose the signal.
                        timed_out.append((idx, e))
                        logger.error(
                            "Batch future timed out retrieving result: invocation_index=%s timeout_s=%s",
                            idx,
                            future_result_timeout_s,
                            exc_info=True,
                        )
                    except BaseException as e:
                        failed_futures.append((idx, e))
                        logger.error(
                            "Batch future failed: invocation_index=%s error=%s",
                            idx,
                            type(e).__name__,
                            exc_info=True,
                        )

                elapsed_s = time.monotonic() - t0
                if cancelled or timed_out or failed_futures:
                    logger.error(
                        "Batch futures summary: total=%s ok=%s failed=%s cancelled=%s timeout=%s elapsed_s=%.2f",
                        invocations,
                        ok_count,
                        len(failed_futures),
                        len(cancelled),
                        len(timed_out),
                        elapsed_s,
                    )
                    for idx, e in timed_out:
                        logger.error(
                            "Batch future timeout detail: invocation_index=%s message=%s",
                            idx,
                            str(e),
                            exc_info=True,
                        )
                    for idx, e in cancelled:
                        logger.error(
                            "Batch future cancelled detail: invocation_index=%s message=%s",
                            idx,
                            str(e),
                            exc_info=True,
                        )
                    for idx, e in failed_futures:
                        logger.error(
                            "Batch future failure detail: invocation_index=%s error=%s message=%s",
                            idx,
                            type(e).__name__,
                            str(e),
                            exc_info=True,
                        )

    if buffer:
        with buffer_lock:
            if buffer:
                _flush_buffer(buffer, batch_dir)

    succeeded = sum(1 for r in results if r.get("status") == "GENERATED")
    failed = len(results) - succeeded
    print(f"\n{'='*72}")
    print(f"BATCH COMPLETE  total={invocations}  succeeded={succeeded}  failed={failed}")
    print(f"  output: {batch_dir}")
    print(f"{'='*72}")

    return results


async def run_batch_cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="novelty_pool_cli batch")
    p.add_argument("--invocations", "-n", type=int, required=True, help="Number of workflow invocations")
    p.add_argument("--topics-json", required=True, help="Absolute path to topics JSON file")
    p.add_argument("--content-variant", default="AI_GENERATED",
                   choices=["CURATED_WEB_WITH_IMAGES", "CURATED_WEB_NO_IMAGES", "AI_GENERATED"])
    p.add_argument("--eval-mode", default="sequential", choices=["parallel", "sequential"])
    p.add_argument("--max-refine-attempts", type=int, default=1, choices=[0, 1])
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--num-workers", type=int, default=1, help="Parallel workers (default 1 = sequential)")
    p.add_argument("--future-result-timeout-s", type=int, default=BATCH_FUTURE_RESULT_TIMEOUT_S_DEFAULT, help="Future result timeout seconds (parallel mode)")
    args = p.parse_args(argv)

    results = await run_batch(
        invocations=args.invocations,
        topics_json_path=args.topics_json,
        content_variant=args.content_variant,
        eval_mode=args.eval_mode,
        max_refine_attempts=args.max_refine_attempts,
        timeout=args.timeout,
        num_workers=args.num_workers,
        future_result_timeout_s=args.future_result_timeout_s,
    )
    failed = sum(1 for r in results if r["status"] != "GENERATED")
    return 2 if failed else 0


# ---------------------------------------------------------------------------
# Top-level dispatch
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(prog="novelty_pool_cli", description="Novelty-pool CLI with creative control rotation")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("single", help="Single run with explicit pool selections")
    sub.add_parser("batch", help="Batch run — rotate pool values across N invocations")

    args, remaining = parser.parse_known_args()

    if args.command == "single":
        raise SystemExit(asyncio.run(run_single_cli(remaining)))
    elif args.command == "batch":
        raise SystemExit(asyncio.run(run_batch_cli(remaining)))
    else:
        parser.print_help()
        raise SystemExit(1)


if __name__ == "__main__":
    main()
