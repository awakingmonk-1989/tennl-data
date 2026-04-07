from __future__ import annotations

import json
from typing import Any

from .schema_validation import validate_article_schema
from ..models import QualityAndSchemaBundle, QualityReport, SchemaReport
from ..runtime_assets import read_article_asset
from ..settings import AppSettings


DIMENSIONS = [
    "hook_quality",
    "title_quality",
    "three_beat_structure",
    "sentence_rhythm_voice",
    "content_option_visual_rhythm",
    "deep_dive_quality",
    "india_warmth_specificity",
    "quick_reference_quality",
]


def _heuristic_quality_scores(article_md: str, article_json: dict[str, Any]) -> dict[str, float]:
    # Deterministic placeholder scorer (LLM-based scorer can replace later).
    scores: dict[str, float] = {}
    base = 4.0
    if len(article_md.strip()) < 200:
        base = 3.0
    if not article_json.get("quick_reference"):
        base = 2.5

    for d in DIMENSIONS:
        scores[d] = base
    return scores


def run_quality_and_schema_eval(article_md: str, article_json: dict[str, Any]) -> QualityAndSchemaBundle:
    schema = validate_article_schema(article_json)
    scores = _heuristic_quality_scores(article_md, article_json)
    avg = sum(scores.values()) / len(scores) if scores else 0.0
    min_dim = min(scores.values()) if scores else 0.0

    quality_pass = avg >= 3.5 and min_dim >= 3.0
    schema_pass = schema.result == "PASS"

    q = QualityReport(
        result="PASS" if quality_pass else "FAIL",
        dimensions=scores,
        avg=round(avg, 2),
        min_dimension=round(min_dim, 2),
        thresholds={"avg_gte": 3.5, "all_dimensions_gte": 3.0},
    )
    return QualityAndSchemaBundle(
        result="PASS" if (quality_pass and schema_pass) else "FAIL",
        quality_report=q,
        schema_report=schema,
    )


def _extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        first_nl = text.find("\n")
        last_fence = text.rfind("```", first_nl)
        if first_nl != -1 and last_fence > first_nl:
            text = text[first_nl + 1 : last_fence].strip()

    start = text.find("{")
    if start == -1:
        raise ValueError("LLM response does not contain a JSON object")

    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text, start)
    if not isinstance(obj, dict):
        raise ValueError(f"Expected a JSON object, got {type(obj).__name__}")
    return obj


async def run_quality_with_llm(article_md: str, article_json: dict[str, Any]) -> QualityReport:
    prompt = read_article_asset("prompts", "eval_pass2_quality_prompt.md")
    narration_spec = read_article_asset("specs", "narration_flow_spec_v1.1.md")
    skill_creativity = read_article_asset("skills", "skill_creativity_narration.md")

    full = (
        f"{prompt}\n\n"
        "=== INPUT ===\n"
        f"article_md:\n{article_md}\n\n"
        f"article_json:\n{json.dumps(article_json, ensure_ascii=False)}\n\n"
        "=== ATTACHMENTS ===\n"
        f"[NARRATION_FLOW_SPEC]\n{narration_spec}\n\n"
        f"[SKILL_CREATIVITY_NARRATION]\n{skill_creativity}\n"
    )

    from ..llm_factory import acomplete_with_backoff

    llm = AppSettings.shared.llm
    resp = await acomplete_with_backoff(llm, full)
    obj = _extract_json_object(str(resp))
    bundle_like = QualityAndSchemaBundle.model_validate(
        {
            "result": obj["result"],
            "quality_report": obj["quality_report"],
            # dummy schema; caller will overwrite deterministically
            "schema_report": {"result": "PASS", "failures": []},
        }
    )
    return bundle_like.quality_report
