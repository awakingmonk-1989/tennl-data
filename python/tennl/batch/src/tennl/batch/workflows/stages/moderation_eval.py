from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..settings import AppSettings
from ..models import ModerationCheck, ModerationReport


def _no_deep_dives_in_intro(article_json: dict[str, Any]) -> tuple[bool, str]:
    # We treat hook/hero as intro area; deep dives must be separate objects.
    # Fail if hook contains "deep_dive" objects accidentally.
    hook = article_json.get("hook")
    if isinstance(hook, dict) and ("deep_dive" in hook or "deep_dives" in hook):
        return False, "Hook/intro contains deep-dive content."
    return True, "OK"


def _get_posts(article_json: dict[str, Any]) -> list[dict[str, Any]] | None:
    for key in ("posts", "sections"):
        val = article_json.get(key)
        if isinstance(val, list) and val:
            return val
    return None


def _posts_have_deep_dives(article_json: dict[str, Any]) -> tuple[bool, str]:
    posts = _get_posts(article_json)
    if not posts:
        return True, "OK (no posts/sections to check)"

    deep_dives = article_json.get("deep_dives")
    if not isinstance(deep_dives, list) or not deep_dives:
        return True, "OK (deep_dives not present as separate root key — may be inline)"

    dd_by_post: dict[str, int] = {}
    for dd in deep_dives:
        if isinstance(dd, dict):
            psid = dd.get("post_section_id")
            if isinstance(psid, str):
                dd_by_post[psid] = dd_by_post.get(psid, 0) + 1

    missing = []
    for p in posts:
        if not isinstance(p, dict):
            continue
        sid = p.get("section_id")
        if isinstance(sid, str) and dd_by_post.get(sid, 0) <= 0:
            missing.append(sid)

    if missing:
        return False, f"Posts missing deep dives: {missing}"
    return True, "OK"


def _no_prose_only_blobs(article_json: dict[str, Any]) -> tuple[bool, str]:
    posts = _get_posts(article_json)
    if not posts:
        return True, "OK (no posts/sections to check)"
    for p in posts:
        if not isinstance(p, dict):
            continue
        body = p.get("body")
        if isinstance(body, str):
            return False, f"Post {p.get('section_id')} body is prose-only string."
    return True, "OK"


def run_moderation_checks(article_json: dict[str, Any]) -> ModerationReport:
    checks: list[ModerationCheck] = []

    for check_id, fn in [
        ("no_deep_dives_in_intro", _no_deep_dives_in_intro),
        ("posts_have_deep_dives", _posts_have_deep_dives),
        ("no_prose_only_blobs", _no_prose_only_blobs),
    ]:
        ok, msg = fn(article_json)
        checks.append(ModerationCheck(check_id=check_id, ok=ok, message=msg))

    violations = [c for c in checks if not c.ok]
    return ModerationReport(
        result="PASS" if not violations else "FAIL",
        checks=checks,
        violations=violations,
    )


def _repo_root() -> Path:
    # .../src/tennl/batch/workflows/stages/moderation_eval.py -> repo root (tennl-data/) is 8 parents up
    return Path(__file__).resolve().parents[8]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


async def run_moderation_with_llm(article_md: str, article_json: dict[str, Any]) -> ModerationReport:
    root = _repo_root()
    prompt = _read_text(root / "prompts" / "eval_pass1_moderation_prompt.md")
    content_spec = _read_text(root / "specs" / "content_gen_spec.md")
    skill_mod = _read_text(root / "skills" / "skill_content_moderation.md")

    # Runtime evaluator rules (do not edit prompt files).
    md_upper = (article_md or "").upper()
    is_ai_generated = "AI GENERATED" in md_upper or "AI_GENERATED" in md_upper
    rules = (
        "=== RUNTIME RULE OVERRIDES (EVALUATOR) ===\n"
        "- If `images` is an empty list (`images=[]`) and the content is AI-generated or otherwise no-images, "
        "treat image-safety metadata as NOT APPLICABLE (PASS). Do NOT fail purely because images[] has no entries.\n"
        "- For content_safety flags: if `is_adult_content` / `is_child_inappropriate` are missing, treat them as False.\n"
        f"- Detected content label: {'AI_GENERATED' if is_ai_generated else 'UNKNOWN'}\n"
        "=== END OVERRIDES ===\n\n"
    )

    full = (
        f"{rules}"
        f"{prompt}\n\n"
        "=== INPUT ===\n"
        f"article_md:\n{article_md}\n\n"
        f"article_json:\n{json.dumps(article_json, ensure_ascii=False)}\n\n"
        "=== ATTACHMENTS ===\n"
        f"[CONTENT_SPEC]\n{content_spec}\n\n"
        f"[SKILL_CONTENT_MODERATION]\n{skill_mod}\n"
    )

    from ..llm_factory import acomplete_with_backoff

    llm = AppSettings.shared.llm
    resp = await acomplete_with_backoff(llm, full)
    obj = _extract_json_object(str(resp))
    report = ModerationReport.model_validate(obj)
    # Ensure violations are consistent.
    report.violations = [c for c in report.checks if not c.ok]
    return report

