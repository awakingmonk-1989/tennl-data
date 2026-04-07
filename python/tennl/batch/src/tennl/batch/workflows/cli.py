from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
import uuid
import asyncio

from .azure_storage import generate_entity_id, generate_workflow_execution_id, write_to_azure_storage
from .settings import AppSettings
from .workflow import ContentGenWorkflow
from .tracing import RunContext, install_llamaindex_instrumentation_logging, log_workflow_event_stream, setup_rolling_jsonl_logger

logger = logging.getLogger(__name__)


def _write_artifacts(run_id: str, article_md: str, article_json: dict) -> Path:
    out_dir = Path("out") / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "article.md").write_text(article_md, encoding="utf-8")
    (out_dir / "article.json").write_text(
        json.dumps(article_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
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
    has_dd_in_md = "**Deep dive" in article_md or "Deep dive —" in article_md
    print(f"  Deep dives in markdown: {'YES' if has_dd_in_md else 'NO (MISSING!)'}")


async def arun_from_cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="tennl.batch.workflows")
    p.add_argument("--topic", required=True)
    p.add_argument("--sub-topic", required=True)
    p.add_argument(
        "--content-variant",
        required=True,
        choices=["CURATED_WEB_WITH_IMAGES", "CURATED_WEB_NO_IMAGES", "AI_GENERATED"],
    )
    p.add_argument("--eval-mode", default="parallel", choices=["parallel", "sequential"])
    p.add_argument("--max-refine-attempts", type=int, default=1, choices=[0, 1])
    p.add_argument("--timeout", type=int, default=300)
    args = p.parse_args(argv)

    run_id = str(uuid.uuid4())
    trace_logger = setup_rolling_jsonl_logger()
    install_llamaindex_instrumentation_logging()

    w = ContentGenWorkflow(timeout=args.timeout, verbose=False)
    handler = w.run(
        topic=args.topic,
        sub_topic=args.sub_topic,
        content_variant=args.content_variant,
        eval_mode=args.eval_mode,
        max_refine_attempts=args.max_refine_attempts,
        run_id=run_id,
    )
    stream_task = asyncio.create_task(log_workflow_event_stream(handler, run_id=run_id, logger=trace_logger))

    with RunContext(run_id):
        result = await handler

    await stream_task

    status = result["status"]

    _print_trace_summary(result)

    if status == "GENERATED":
        out_dir = _write_artifacts(run_id, result["article_md"], result["article_json"])
        print(f"GENERATED run_id={run_id} out_dir={out_dir}")
        _print_article_summary(result["article_md"], result["article_json"])

        conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
        if conn_str:
            settings = AppSettings()
            ct = settings.content_type
            wf_exec_id = generate_workflow_execution_id(ct)
            ent_id = generate_entity_id(ct)
            info = write_to_azure_storage(
                connection_string=conn_str,
                container_name="content",
                content_type=ct,
                category=args.topic.lower().replace(" ", ""),
                sub_category=args.sub_topic.lower().replace(" ", ""),
                workflow_execution_id=wf_exec_id,
                entity_id=ent_id,
                article_md=result["article_md"],
                article_json=result["article_json"],
            )
            print(f"  Azure blob: {info['blob_url']}")
            print(f"  wfExecId:   {info['workflow_execution_id']}")
            print(f"  entityId:   {info['entity_id']}")
        else:
            logger.info("AZURE_STORAGE_CONNECTION_STRING not set — skipping Azure persistence")

        return 0

    err = result.get("error") or {}
    print(f"FAILED run_id={run_id} reason={err.get('failure_reason')} node={err.get('error_node')}")
    if err.get("error_message"):
        print(f"  message: {err['error_message'][:300]}")
    return 2


def main() -> None:
    import asyncio

    raise SystemExit(asyncio.run(arun_from_cli()))

