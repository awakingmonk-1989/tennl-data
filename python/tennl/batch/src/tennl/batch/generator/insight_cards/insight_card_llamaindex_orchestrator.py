"""
insight_card_llamaindex_orchestrator.py

Insight card generator using LlamaIndex structured output.
- LLM configuration is loaded from the shared app.yaml via ``tennl.batch.settings.AppSettings`` / llm_factory
- Insight card prompts and batch params from packaged YAML on AppSettings.shared.insight_cards
- Each card gets a fresh structured LLM invocation
- Two run modes: sequential and parallel (configurable max workers)
- Seed variables from packaged resources/insight-cards/insight_card_config.json
- Successful cards are written as triples under ``--output-dir``: ``prefix.json``,
  ``prefix_raw.json``, ``prefix_tokens.json``

Usage:
    python insight_card_llamaindex_orchestrator.py --category Finance --dry-run
    python insight_card_llamaindex_orchestrator.py --category Technology --mode parallel --count 5
    python insight_card_llamaindex_orchestrator.py --category Finance --output-dir output/gemini_live_test

    ``--category`` must match a key under ``categories`` in packaged ``insight_card_config.json``.
    LLM provider: set TENNL_LLM_PROVIDER before launch (see app.yaml llm.providers).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import importlib.resources as ir
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from llama_index.core.llms import ChatMessage
from pydantic import ValidationError

from tennl.batch.base.sampler import BaseSampler
from tennl.batch.domain import InsightCard, InsightCardResult, LiteLLMGeminiTokenUsage
from tennl.batch.settings import AppSettings
from tennl.batch.settings.insight_cards import InsightCardFormatterSettings
from tennl.batch.util.slot_rotater import SlotRotator

logger = logging.getLogger(__name__)

# Parallel mode: safety cap on ``Future.result()`` (same default as novelty batch CLI).
INSIGHT_CARD_FUTURE_RESULT_TIMEOUT_S_DEFAULT = 120


# ─────────────────────────────────────────────────────────────
# Packaged seed JSON
# ─────────────────────────────────────────────────────────────


def load_packaged_seed_config() -> dict[str, Any]:
    text = ir.files("tennl.batch").joinpath(
        "resources", "insight-cards", "insight_card_config.json"
    ).read_text(encoding="utf-8")
    return json.loads(text)


def validate_insight_card_category(seed: dict[str, Any], category: str) -> str:
    """Return ``category`` if present under ``seed['categories']``; else raise ``ValueError``."""
    categories = seed.get("categories") or {}
    if category not in categories:
        known = ", ".join(sorted(categories.keys()))
        raise ValueError(f"Unknown category {category!r}; known: {known}")
    return category


# ─────────────────────────────────────────────────────────────
# Variable sampler — single category per batch, rotating slots
# ─────────────────────────────────────────────────────────────
class InsightCardVariableSampler(BaseSampler):
    """
    Exactly one seed category per batch (``allowed_categories`` length 1).

    Global slots use ``worker_id`` offsets; ``theme`` and ``human_context`` use
    long-lived rotators so they advance on every ``sample()``. Do not share one
    sampler across threads — ``SlotRotator`` is not thread-safe.
    """

    def __init__(
        self,
        seed: dict[str, Any],
        worker_id: int = 0,
        *,
        allowed_categories: list[str],
    ):
        if not allowed_categories:
            raise ValueError("allowed_categories must be non-empty")
        if len(allowed_categories) != 1:
            raise ValueError(
                f"Exactly one category per batch is required; got {len(allowed_categories)}"
            )
        categories = seed["categories"]
        name = allowed_categories[0]
        if name not in categories:
            raise ValueError(f"Category {name!r} not in seed['categories']")

        cat_pool = categories[name]
        ts = seed["title_style_hints"]

        self._fixed_category = name
        self._global_rotators = {
            "hook_type":          SlotRotator(seed["hook_types"], worker_id + 1),
            "register":           SlotRotator(seed["registers"], worker_id + 2),
            "opening_word_class": SlotRotator(seed["opening_word_classes"], worker_id + 3),
            "title_style":        SlotRotator(ts["styles"], worker_id + 8),
        }
        self._theme_rotator = SlotRotator(cat_pool["themes"], worker_id)
        self._context_rotator = SlotRotator(cat_pool["human_contexts"], worker_id)
        self._avoid_titles = ts.get("avoid", [])
        self._worker_id = worker_id

    def sample(self) -> dict[str, Any]:
        v = {k: r.next() for k, r in self._global_rotators.items()}
        v["category"] = self._fixed_category
        v["theme"] = self._theme_rotator.next()
        v["human_context"] = self._context_rotator.next()
        v["topic"] = f"{v['theme']} in the context of {v['human_context']}"
        v["tone"] = v["register"]
        v["emotional_register"] = v["register"]
        v["avoid_titles"] = "Avoid titles like: " + ", ".join(
            f'"{t}"' for t in self._avoid_titles
        )
        return v


# ─────────────────────────────────────────────────────────────
# Prompt renderer
# ─────────────────────────────────────────────────────────────

def render_prompt(template: str, variables: dict) -> str:
    """Simple {key} substitution. Missing keys left as-is."""
    try:
        return template.format(**variables)
    except KeyError:
        # Graceful fallback — don't crash on missing optional keys
        result = template
        for k, v in variables.items():
            result = result.replace("{" + k + "}", str(v))
        return result


# ─────────────────────────────────────────────────────────────
# Static prompt variable injection (layout library)
# ─────────────────────────────────────────────────────────────

def build_static_vars(formatter: InsightCardFormatterSettings | None) -> dict[str, str]:
    """Extract prompt_blocks from formatter settings for injection into prompt templates.

    Returns a dict with keys: layout_library, selection_table, slot_sizing.
    These are merged into every card's variables dict before prompt rendering.
    If formatter is None (backward compat), returns empty strings for all keys.
    """
    if formatter is None:
        return {"layout_library": "", "selection_table": "", "slot_sizing": ""}
    pb = formatter.prompt_blocks
    return {
        "layout_library": pb.layout_library,
        "selection_table": pb.selection_table,
        "slot_sizing": pb.slot_sizing,
    }


def validate_layout(
    card: InsightCard,
    formatter: InsightCardFormatterSettings | None,
) -> list[str]:
    """Soft-validate layout and content_blocks against formatter config.

    Returns a list of warning messages (empty if all OK). Never raises.
    """
    if formatter is None:
        return []
    warnings: list[str] = []

    if card.layout not in formatter.templates:
        warnings.append(
            f"layout {card.layout!r} not in valid templates: {formatter.templates}"
        )

    expected_keys = formatter.block_schemas.get(card.layout)
    if expected_keys is not None:
        actual_keys = set(card.content_blocks.keys())
        expected_set = set(expected_keys)
        if actual_keys != expected_set:
            warnings.append(
                f"content_blocks keys {sorted(actual_keys)} do not match "
                f"expected {sorted(expected_set)} for layout {card.layout!r}"
            )

    bullets = card.content_blocks.get("bullets")
    if bullets is not None:
        if not isinstance(bullets, list):
            warnings.append(f"bullets should be a list, got {type(bullets).__name__}")
        elif not (2 <= len(bullets) <= 4):
            warnings.append(f"bullets should have 2-4 items, got {len(bullets)}")

    for key, value in card.content_blocks.items():
        if key == "bullets":
            continue
        if not isinstance(value, str) or not value.strip():
            warnings.append(f"content_blocks[{key!r}] is empty or not a string")

    return warnings


# ─────────────────────────────────────────────────────────────
# Structured response helpers
# ─────────────────────────────────────────────────────────────


def _empty_result(provider_name: str, raw: str = "", error: str | None = None) -> InsightCardResult:
    return InsightCardResult(provider=provider_name, raw=raw, error=error)


def _coerce_structured_card(parsed: Any) -> InsightCard:
    if isinstance(parsed, InsightCard):
        return parsed
    if hasattr(parsed, "model_dump"):
        return InsightCard.model_validate(parsed.model_dump())
    if isinstance(parsed, dict):
        return InsightCard.model_validate(parsed)
    raise TypeError(
        f"Expected structured InsightCard output, got {type(parsed).__name__}"
    )


def _extract_raw_text(response: Any) -> str:
    if response is None:
        return ""

    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()

    raw = getattr(response, "raw", None)
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    if raw is not None and hasattr(raw, "model_dump_json"):
        return raw.model_dump_json(indent=2)
    if raw is not None and hasattr(raw, "model_dump"):
        return json.dumps(raw.model_dump(), ensure_ascii=False, indent=2)
    if isinstance(raw, dict):
        return json.dumps(raw, ensure_ascii=False, indent=2)

    message = getattr(response, "message", None)
    content = getattr(message, "content", None)
    if isinstance(content, str) and content.strip():
        return content.strip()

    rendered = str(response).strip()
    return "" if rendered == "None" else rendered


def _build_result(
    card: InsightCard,
    provider_name: str,
    raw_text: str,
    error: str | None = None,
) -> InsightCardResult:
    return InsightCardResult(**card.model_dump(), provider=provider_name, raw=raw_text, error=error)


def _build_messages(system_prompt: str, user_prompt: str) -> list[ChatMessage]:
    messages = []
    if system_prompt.strip():
        messages.append(ChatMessage.from_str(system_prompt, role="system"))
    messages.append(ChatMessage.from_str(user_prompt, role="user"))
    return messages


# ─────────────────────────────────────────────────────────────
# Single card generation — one fresh engine per call
# ─────────────────────────────────────────────────────────────

def _safe_serialize(obj: Any) -> Any:
    """Best-effort JSON-safe serialisation of an arbitrary object."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _safe_serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_safe_serialize(v) for v in obj]
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return {k: _safe_serialize(v) for k, v in obj.__dict__.items()
                if not k.startswith("_")}
    return str(obj)


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences wrapping JSON content."""
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def _extract_litellm_token_metadata(response: Any) -> dict[str, Any]:
    """Extract token usage from LiteLLM ModelResponse via response.raw['usage'].

    response.additional_kwargs is always {} for LiteLLM due to a bug in the
    LlamaIndex wrapper (_get_response_token_counts checks isinstance(raw, dict)
    which fails for Pydantic ModelResponse).  Read from response.raw instead.
    """
    zeros: dict[str, Any] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    raw = getattr(response, "raw", None)
    if raw is None:
        return zeros

    usage = None
    try:
        usage = raw["usage"]
    except (KeyError, TypeError, IndexError):
        usage = getattr(raw, "usage", None)
    if usage is None:
        return zeros

    usage_dict = _safe_serialize(usage)
    if not isinstance(usage_dict, dict):
        return zeros

    try:
        return LiteLLMGeminiTokenUsage.model_validate(usage_dict).model_dump()
    except Exception:
        logger.warning("Failed to validate LiteLLM token usage, returning raw dict")
        return usage_dict


def _extract_default_token_metadata(response: Any) -> dict[str, Any]:
    """Extract token usage from response.additional_kwargs (OpenAI-like providers)."""
    kwargs = getattr(response, "additional_kwargs", {}) or {}
    return {
        "prompt_tokens": kwargs.get("prompt_tokens", 0),
        "completion_tokens": kwargs.get("completion_tokens", 0),
        "total_tokens": kwargs.get("total_tokens", 0),
    }


def _extract_token_metadata(response: Any, provider_name: str) -> dict[str, Any]:
    """Dispatch to the appropriate token extractor based on provider."""
    if provider_name == "litellm":
        return _extract_litellm_token_metadata(response)
    return _extract_default_token_metadata(response)


def generate_one_card(
    llm,
    system_prompt_tpl: str,
    user_prompt_tpl: str,
    variables: dict,
    provider_name: str,
    dry_run: bool,
    model_name: str = "",
    static_vars: dict[str, str] | None = None,
    formatter: InsightCardFormatterSettings | None = None,
) -> InsightCardResult:
    """
    Sends one isolated chat request, parses the card JSON from the response
    content, extracts token usage, and returns an InsightCardResult with full
    metadata (raw_response + token_usage stored in ``result.metadata``).
    """
    merged = {**(static_vars or {}), **variables}
    system_prompt = render_prompt(system_prompt_tpl, merged)
    user_prompt = render_prompt(user_prompt_tpl, merged)

    if dry_run:
        preview = f"[SYSTEM]\n{system_prompt}\n\n[USER]\n{user_prompt}"
        return InsightCardResult(
            title="[DRY RUN]",
            category=variables.get("category", ""),
            content="",
            tone=variables.get("tone", ""),
            emotional_register=variables.get("emotional_register", ""),
            title_style=variables.get("title_style", ""),
            hook_type=variables.get("hook_type", ""),
            opening_word_class=variables.get("opening_word_class", ""),
            provider=provider_name,
            raw=preview,
            error=None,
            metadata={
                "timestamp": time.time(),
                "provider": provider_name,
                "model": model_name or "dry-run",
                "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            },
        )

    response = None
    raw_text = ""

    try:
        response = llm.chat(_build_messages(system_prompt, user_prompt))

        content = getattr(response.message, "content", None) or ""
        json_str = _strip_code_fences(content)
        card = InsightCard.model_validate_json(json_str)

        layout_warnings = validate_layout(card, formatter)
        for w in layout_warnings:
            logger.warning("Layout validation: %s", w)

        token_usage = _extract_token_metadata(response, provider_name)
        logger.info(
            "Token usage — prompt: %d, completion: %d, total: %d",
            token_usage.get("prompt_tokens", 0),
            token_usage.get("completion_tokens", 0),
            token_usage.get("total_tokens", 0),
        )

        raw_text = _extract_raw_text(response)
        result = _build_result(card=card, provider_name=provider_name, raw_text=raw_text)
        result.metadata = {
            "timestamp": time.time(),
            "provider": provider_name,
            "model": model_name,
            "token_usage": token_usage,
            "raw_response": _safe_serialize(getattr(response, "raw", None)),
        }
        return result

    except (ValidationError, TypeError, ValueError) as e:
        raw_text = raw_text or _extract_raw_text(response)
        logger.exception(
            "Insight card structured parsing failed (provider=%s)",
            provider_name,
        )
        return _empty_result(provider_name=provider_name, raw=raw_text, error=str(e))
    except Exception as e:
        raw_text = raw_text or _extract_raw_text(response)
        logger.exception(
            "Insight card LLM call failed (provider=%s)",
            provider_name,
        )
        return _empty_result(provider_name=provider_name, raw=raw_text, error=str(e))


# ─────────────────────────────────────────────────────────────
# Per-card file output
# ─────────────────────────────────────────────────────────────

def save_card_artifacts(
    result: InsightCardResult,
    output_dir: str = "output/insight_cards",
) -> list[Path]:
    """Write triple-file output per card: .json, _raw.json, _tokens.json.

    All three files share the same prefix ``insight_card_{model}_{epoch_ms}``
    so they can be correlated after the fact.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    meta = result.metadata or {}
    model_label = meta.get("model", "unknown")
    safe_model = re.sub(r"[^a-zA-Z0-9_]", "_", model_label)
    ts_ms = int(time.time() * 1000)
    prefix = f"insight_card_{safe_model}_{ts_ms}"
    paths: list[Path] = []

    card_data = {
        k: v for k, v in result.model_dump().items()
        if k not in ("raw", "metadata", "provider", "error")
    }
    card_path = out / f"{prefix}.json"
    card_path.write_text(
        json.dumps(card_data, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    paths.append(card_path)

    raw_path = out / f"{prefix}_raw.json"
    raw_path.write_text(
        json.dumps(meta.get("raw_response", {}), indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    paths.append(raw_path)

    tokens_path = out / f"{prefix}_tokens.json"
    tokens_path.write_text(
        json.dumps(meta.get("token_usage", {}), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    paths.append(tokens_path)

    logger.info("Saved 3 artifacts: %s/%s{.json,_raw.json,_tokens.json}", output_dir, prefix)
    return paths


# ─────────────────────────────────────────────────────────────
# Batch runner — sequential and parallel modes
# ─────────────────────────────────────────────────────────────

def _log_batch_summary(results: list[InsightCardResult], output_dir: str | None) -> None:
    """Log aggregated token usage across all results in a batch."""
    totals = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    for r in results:
        if r.metadata and "token_usage" in r.metadata:
            tu = r.metadata["token_usage"]
            totals["prompt_tokens"] += tu.get("prompt_tokens", 0)
            totals["completion_tokens"] += tu.get("completion_tokens", 0)
            totals["total_tokens"] += tu.get("total_tokens", 0)

    logger.info("=" * 60)
    logger.info("Batch Summary")
    logger.info("  Cards generated     : %d", len(results))
    logger.info("  Total prompt tokens : %s", f"{totals['prompt_tokens']:,}")
    logger.info("  Total compl. tokens : %s", f"{totals['completion_tokens']:,}")
    logger.info("  Total tokens        : %s", f"{totals['total_tokens']:,}")
    if output_dir:
        logger.info("  Per-card output dir : %s", output_dir)
    logger.info("=" * 60)


def run_sequential(
    llm,
    system_prompt_tpl: str,
    user_prompt_tpl: str,
    seed: dict,
    provider_name: str,
    count: int,
    dry_run: bool,
    allowed_categories: list[str],
    output_dir: str | None = None,
    model_name: str = "",
    static_vars: dict[str, str] | None = None,
    formatter: InsightCardFormatterSettings | None = None,
) -> list[InsightCardResult]:
    results = []
    seen = set()

    sampler = InsightCardVariableSampler(
        seed, worker_id=0, allowed_categories=allowed_categories
    )
    for i in range(count):
        variables = sampler.sample()

        card = generate_one_card(
            llm, system_prompt_tpl, user_prompt_tpl,
            variables, provider_name, dry_run, model_name,
            static_vars=static_vars, formatter=formatter,
        )
        if output_dir and not card.error:
            save_card_artifacts(card, output_dir)
        _log_card(card, i, seen, results)

    _log_batch_summary(results, output_dir)
    return results


def run_parallel(
    llm,
    system_prompt_tpl: str,
    user_prompt_tpl: str,
    seed: dict,
    provider_name: str,
    count: int,
    max_workers: int,
    dry_run: bool,
    allowed_categories: list[str],
    output_dir: str | None = None,
    model_name: str = "",
    static_vars: dict[str, str] | None = None,
    formatter: InsightCardFormatterSettings | None = None,
    future_result_timeout_s: int = INSIGHT_CARD_FUTURE_RESULT_TIMEOUT_S_DEFAULT,
) -> list[InsightCardResult]:
    results = []
    seen = set()

    def task(worker_id: int) -> InsightCardResult:
        sampler = InsightCardVariableSampler(
            seed, worker_id=worker_id, allowed_categories=allowed_categories
        )
        variables = sampler.sample()
        return generate_one_card(
            llm, system_prompt_tpl, user_prompt_tpl,
            variables, provider_name, dry_run, model_name,
            static_vars=static_vars, formatter=formatter,
        )

    cancelled: list[tuple[int, BaseException]] = []
    timed_out: list[tuple[int, BaseException]] = []
    failed_futures: list[tuple[int, BaseException]] = []
    ok_futures = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures: dict[concurrent.futures.Future[InsightCardResult], int] = {
            executor.submit(task, i): i for i in range(count)
        }
        t0 = time.monotonic()
        for fut in concurrent.futures.as_completed(futures):
            idx = futures[fut]
            try:
                card = fut.result(timeout=future_result_timeout_s)
            except concurrent.futures.CancelledError as e:
                cancelled.append((idx, e))
                logger.warning(
                    "Insight card future cancelled: worker_index=%s",
                    idx,
                    exc_info=True,
                )
                continue
            except concurrent.futures.TimeoutError as e:
                timed_out.append((idx, e))
                logger.error(
                    "Insight card future timed out retrieving result: worker_index=%s timeout_s=%s",
                    idx,
                    future_result_timeout_s,
                    exc_info=True,
                )
                continue
            except BaseException as e:
                failed_futures.append((idx, e))
                logger.error(
                    "Insight card future failed: worker_index=%s error=%s",
                    idx,
                    type(e).__name__,
                    exc_info=True,
                )
                continue

            ok_futures += 1
            if output_dir and not card.error:
                save_card_artifacts(card, output_dir)
            _log_card(card, idx, seen, results)

        elapsed_s = time.monotonic() - t0

        if cancelled or timed_out or failed_futures:
            logger.error(
                "Insight card batch futures summary: submitted=%s futures_ok=%s "
                "cards_logged=%s failed=%s cancelled=%s timeout=%s elapsed_s=%.2f",
                count,
                ok_futures,
                len(results),
                len(failed_futures),
                len(cancelled),
                len(timed_out),
                elapsed_s,
            )
            for widx, e in timed_out:
                logger.error(
                    "Insight card future timeout detail: worker_index=%s message=%s",
                    widx,
                    str(e),
                    exc_info=True,
                )
            for widx, e in cancelled:
                logger.error(
                    "Insight card future cancelled detail: worker_index=%s message=%s",
                    widx,
                    str(e),
                    exc_info=True,
                )
            for widx, e in failed_futures:
                logger.error(
                    "Insight card future failure detail: worker_index=%s error=%s message=%s",
                    widx,
                    type(e).__name__,
                    str(e),
                    exc_info=True,
                )

    _log_batch_summary(results, output_dir)
    return results


def _log_card(card: InsightCardResult, idx: int, seen: set, results: list):
    if card.error:
        logger.warning("worker %s: %s", idx, card.error)
        return
    fp = card.fingerprint()
    if fp in seen:
        logger.info("dedup skipped duplicate: %s", card.title)
        return
    seen.add(fp)
    results.append(card)
    logger.info("ok %s | %s | %s", card.provider, card.category, card.title)


# ─────────────────────────────────────────────────────────────
# Secrets loader
# ─────────────────────────────────────────────────────────────

def _find_repo_root() -> Path | None:
    """Walk up from this file until we find a directory with .git or secrets.txt."""
    p = Path(__file__).resolve().parent
    for _ in range(12):
        if (p / ".git").exists() or (p / "secrets.txt").exists():
            return p
        if p == p.parent:
            break
        p = p.parent
    return None


def _load_secrets_env(secrets_path: str | Path | None = None) -> int:
    """Read KEY=VALUE pairs from secrets.txt and inject into os.environ.

    Skips blank lines and comments (#). Values may be optionally quoted.
    Returns the number of variables loaded.
    """
    if secrets_path is None:
        root = _find_repo_root()
        if root is None:
            return 0
        candidate = root / "secrets.txt"
        if not candidate.exists():
            return 0
        secrets_path = candidate
    else:
        secrets_path = Path(secrets_path)
        if not secrets_path.exists():
            logger.warning("Secrets file not found: %s", secrets_path)
            return 0

    loaded = 0
    for line in secrets_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value
            loaded += 1
            logger.debug("Loaded env %s from secrets.txt", key)
    return loaded


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    n_secrets = _load_secrets_env()
    if n_secrets:
        logger.info("Loaded %d env vars from secrets.txt", n_secrets)

    parser = argparse.ArgumentParser(description="Insight card orchestrator (LlamaIndex)")
    parser.add_argument("--mode",     default="sequential", choices=["sequential", "parallel"])
    parser.add_argument("--count",    type=int, default=None,  help="Override count from config")
    parser.add_argument("--workers",  type=int, default=None,  help="Override max_workers from config")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for per-card JSON files (default: output/insight_cards)",
    )
    parser.add_argument(
        "--future-result-timeout-s",
        type=int,
        default=INSIGHT_CARD_FUTURE_RESULT_TIMEOUT_S_DEFAULT,
        help=(
            "Parallel mode only: max seconds to wait for each Future.result() "
            "(cancellation / stuck threads surface as timeout or cancel logs)"
        ),
    )
    parser.add_argument("--version",  default=None,            help="Override prompt_version from config")
    parser.add_argument("--dry-run",  action="store_true",     help="Print prompts without calling LLM")
    parser.add_argument(
        "--category",
        required=True,
        help="Seed category name (exact key under categories in insight_card_config.json)",
    )
    args = parser.parse_args()

    seed = load_packaged_seed_config()
    try:
        validate_insight_card_category(seed, args.category)
    except ValueError as e:
        logger.error("%s", e)
        sys.exit(1)
    allowed_categories = [args.category]

    app = AppSettings.shared
    ic_settings = app.insight_cards

    llm_cfg = app.llm_provider
    provider_name = llm_cfg.name
    llm = app.llm

    gen = ic_settings.generation
    prompt_version = args.version or gen.prompt_version
    count = args.count if args.count is not None else gen.count
    max_workers = args.workers if args.workers is not None else gen.max_workers

    system_tpl, user_tpl = ic_settings.prompt_templates(prompt_version)

    formatter = ic_settings.formatter
    static_vars = build_static_vars(formatter)

    output_dir = args.output_dir or "output/insight_cards"

    logger.info("Insight card orchestrator (LlamaIndex)")
    logger.info("  category   : %s", args.category)
    logger.info("  provider   : %s", provider_name)
    logger.info("  model      : %s", llm_cfg.model)
    logger.info("  version    : %s", prompt_version)
    logger.info("  formatter  : %s", "enabled" if formatter else "disabled")
    logger.info("  mode       : %s", args.mode)
    logger.info("  count      : %s", count)
    logger.info("  workers    : %s", max_workers if args.mode == "parallel" else 1)
    logger.info("  output-dir : %s (per-card *.json, *_raw.json, *_tokens.json)", output_dir)
    if args.mode == "parallel":
        logger.info("  future-result-timeout-s : %s", args.future_result_timeout_s)
    logger.info("  dry-run    : %s", args.dry_run)

    if args.mode == "sequential":
        cards = run_sequential(
            llm, system_tpl, user_tpl, seed,
            provider_name, count, args.dry_run, allowed_categories,
            output_dir=output_dir,
            model_name=llm_cfg.model,
            static_vars=static_vars, formatter=formatter,
        )
    else:
        cards = run_parallel(
            llm, system_tpl, user_tpl, seed,
            provider_name, count, max_workers, args.dry_run, allowed_categories,
            output_dir=output_dir,
            model_name=llm_cfg.model,
            static_vars=static_vars, formatter=formatter,
            future_result_timeout_s=args.future_result_timeout_s,
        )

    logger.info("Batch finished: %s unique successful card(s) recorded (see output-dir for files)", len(cards))

    if args.dry_run and cards:
        logger.info("--- Dry run prompt preview (card 0) ---\n%s", cards[0].raw)


if __name__ == "__main__":
    main()
