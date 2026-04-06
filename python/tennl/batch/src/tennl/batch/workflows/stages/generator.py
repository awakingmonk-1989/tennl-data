from __future__ import annotations

import json
import importlib.resources as ir
from pathlib import Path
from typing import Any, Optional

from ..models import PromptRuntimeInput, QualityConstraints, WorkflowInput
from ..settings import AppSettings, PromptTemplate


def _repo_root() -> Path:
    # .../src/tennl/batch/workflows/stages/generator.py -> repo root (tennl-data/) is 8 parents up
    return Path(__file__).resolve().parents[8]


def _pkg_resources() -> Path:
    # Source layout: `src/resources/` (kept out of the python package directory),
    # but packaged into the wheel at `tennl/batch/resources/` via Hatchling shared-data.
    return Path(ir.files("tennl.batch").joinpath("resources"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Prompt formatting helpers
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    """Escape braces so str.format() treats them as literal."""
    return text.replace("{", "{{").replace("}", "}}")


def normalize_prompt_value(value: Any) -> str:
    """Serialize list/dict values to stable JSON; pass scalars through as str."""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def optional_named_block(name: str, content: str | None) -> str:
    """Wrap *content* in a named block header, or return empty string if absent."""
    if not content:
        return ""
    return f"[{name}]\n{content}\n"


def validate_runtime(inp: PromptRuntimeInput) -> None:
    """Check that selected creative controls belong to their pools.

    Skipped when pools are empty (e.g. content_gen_base which has no
    creative-control fields).  Lifted from version/content_prompt_loader.py.
    """
    checks: list[tuple[str, str, list[str]]] = [
        ("content_mode", inp.content_mode, inp.content_mode_pool),
        ("angle", inp.angle, inp.angle_pool),
        ("tone", inp.tone, inp.tone_pool),
        ("hook_style", inp.hook_style, inp.hook_style_pool),
    ]
    for field, value, pool in checks:
        if pool and value and value not in pool:
            raise ValueError(
                f"Selected {field} '{value}' not in {field}_pool {pool}"
            )


def format_prompt(template: PromptTemplate, inp: PromptRuntimeInput) -> str:
    """Assemble the 4 template blocks from a typed *inp*.

    Block order: system_prompt -> runtime_input_block -> output_block -> attachments_block.
    Empty blocks are silently dropped.
    """
    sample_markdown_block = optional_named_block("SAMPLE_MARKDOWN", inp.sample_md)
    sample_json_block = optional_named_block("SAMPLE_JSON", inp.sample_json)

    merged: dict[str, str] = {
        "topic": normalize_prompt_value(inp.topic),
        "sub_topic": normalize_prompt_value(inp.sub_topic),
        "sub_topic_description": normalize_prompt_value(inp.sub_topic_description),
        "content_variant": normalize_prompt_value(inp.content_variant),
        "intent_profile": normalize_prompt_value(inp.intent_profile),
        "content_mode_pool": normalize_prompt_value(inp.content_mode_pool),
        "angle_pool": normalize_prompt_value(inp.angle_pool),
        "tone_pool": normalize_prompt_value(inp.tone_pool),
        "hook_style_pool": normalize_prompt_value(inp.hook_style_pool),
        "must_include": normalize_prompt_value(inp.quality_constraints.must_include),
        "avoid": normalize_prompt_value(inp.quality_constraints.avoid),
        "content_mode": normalize_prompt_value(inp.content_mode),
        "angle": normalize_prompt_value(inp.angle),
        "tone": normalize_prompt_value(inp.tone),
        "hook_style": normalize_prompt_value(inp.hook_style),
        "sample_markdown_block": sample_markdown_block,
        "sample_json_block": sample_json_block,
        "prompt": normalize_prompt_value(inp.prompt),
        "content_spec": normalize_prompt_value(inp.content_spec),
        "narration_spec": normalize_prompt_value(inp.narration_spec),
        "schema_spec": normalize_prompt_value(inp.schema_spec),
        "skill_gen": normalize_prompt_value(inp.skill_gen),
    }

    empty_fields = sorted(k for k, v in merged.items() if not v.strip())
    if empty_fields:
        raise ValueError(
            f"Prompt has empty required fields: {empty_fields}. "
            "All prompt input fields must be populated before rendering."
        )

    parts = [
        template.system_prompt.format(**merged).strip(),
        template.runtime_input_block.format(**merged).strip(),
        template.output_block.format(**merged).strip(),
        template.attachments_block.format(**merged).strip(),
    ]
    return "\n\n".join(part for part in parts if part)


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def _load_shared_assets() -> dict[str, str]:
    """Load all spec/skill/sample files shared across prompt variants."""
    root = _repo_root()
    assets = {
        "prompt": _esc(_read_text(root / "prompts" / "conten_gen_prompt_page_post.md")),
        "content_spec": _esc(_read_text(root / "specs" / "content_gen_spec.md")),
        "narration_spec": _esc(_read_text(root / "specs" / "narration_flow_spec_v1.1.md")),
        "schema_spec": _esc(_read_text(root / "specs" / "json_schema_spec_v1.md")),
        "skill_gen": _esc(_read_text(root / "skills" / "skill_content_generation.md")),
    }

    sample_md_path = _pkg_resources() / "sample_output_reference.md"
    sample_json_path = _pkg_resources() / "sample_output_reference.json"
    assets["sample_md"] = _esc(_read_text(sample_md_path)) if sample_md_path.exists() else ""
    assets["sample_json"] = _esc(_read_text(sample_json_path)) if sample_json_path.exists() else ""

    return assets


def build_prompt_runtime_input(
    inp: WorkflowInput,
    *,
    sub_topic_description: str,
    assets: dict[str, str],
) -> PromptRuntimeInput:
    """Map WorkflowInput + loaded assets into a typed, frozen PromptRuntimeInput.

    Lifted from version/content_prompt_loader.py, adapted to use our
    _esc()'d asset dict and pydantic PromptRuntimeInput.
    """
    return PromptRuntimeInput(
        topic=inp.topic,
        sub_topic=inp.sub_topic,
        sub_topic_description=sub_topic_description,
        content_variant=inp.content_variant.value,
        intent_profile=inp.intent_profile,
        content_mode_pool=inp.content_mode_pool,
        angle_pool=inp.angle_pool,
        tone_pool=inp.tone_pool,
        hook_style_pool=inp.hook_style_pool,
        quality_constraints=QualityConstraints(
            must_include=inp.quality_constraints.must_include,
            avoid=inp.quality_constraints.avoid,
        ),
        content_mode=inp.content_mode,
        angle=inp.angle,
        tone=inp.tone,
        hook_style=inp.hook_style,
        sample_md=assets.get("sample_md") or None,
        sample_json=assets.get("sample_json") or None,
        prompt=assets.get("prompt", ""),
        content_spec=assets.get("content_spec", ""),
        narration_spec=assets.get("narration_spec", ""),
        schema_spec=assets.get("schema_spec", ""),
        skill_gen=assets.get("skill_gen", ""),
    )


def _build_generation_prompt(inp: WorkflowInput, *, sub_topic_description: str) -> str:
    assets = _load_shared_assets()
    runtime_input = build_prompt_runtime_input(
        inp, sub_topic_description=sub_topic_description, assets=assets,
    )
    validate_runtime(runtime_input)
    template = AppSettings.shared.prompts.content_gen_base
    return format_prompt(template, runtime_input)


def _build_refine_prompt(
    inp: WorkflowInput,
    *,
    previous_article_md: str,
    previous_article_json: dict[str, Any],
    merged_eval: dict[str, Any],
    original_prompt_text: str,
) -> str:
    root = _repo_root()
    refine_template = _read_text(root / "prompts" / "refine_prompt.md")
    content_spec = _read_text(root / "specs" / "content_gen_spec.md")
    narration_spec = _read_text(root / "specs" / "narration_flow_spec_v1.1.md")
    schema_spec = _read_text(root / "specs" / "json_schema_spec_v1.md")
    skill_gen = _read_text(root / "skills" / "skill_content_generation.md")

    sample_json_path = _pkg_resources() / "sample_output_reference.json"
    sample_json = _read_text(sample_json_path) if sample_json_path.exists() else ""

    return (
        f"{refine_template}\n\n"
        "================================================================================\n"
        "ORIGINAL CONTENT GENERATION PROMPT (must be preserved)\n"
        "================================================================================\n"
        f"{original_prompt_text}\n\n"
        "================================================================================\n"
        "RUNTIME INPUT\n"
        "================================================================================\n"
        f"topic: {inp.topic}\nsub_topic: {inp.sub_topic}\ncontent_variant: {inp.content_variant.value}\n\n"
        "================================================================================\n"
        "PREVIOUS OUTPUT\n"
        "================================================================================\n"
        f"article_md:\n{previous_article_md}\n\n"
        f"article_json:\n{json.dumps(previous_article_json, ensure_ascii=False)}\n\n"
        "================================================================================\n"
        "EVALUATION FAILURES (authoritative)\n"
        "================================================================================\n"
        f"{json.dumps(merged_eval, ensure_ascii=False, indent=2)}\n\n"
        + (
            "================================================================================\n"
            "REFERENCE SAMPLE JSON (correct structure — every post has sub_sections with deep dives)\n"
            "================================================================================\n"
            f"{sample_json}\n\n"
            if sample_json else ""
        )
        + "================================================================================\n"
        "OUTPUT FORMAT (strict)\n"
        "================================================================================\n"
        "Produce the refined article exactly as described in Part 7 of the original prompt:\n"
        "  1. Complete article body in clean markdown (including deep dives inline)\n"
        "  2. Complete JSON object in a ```json fenced block at the end\n"
        "CRITICAL: every section MUST include a deep dive. Target 600-900 words.\n\n"
        "================================================================================\n"
        "ATTACHMENTS (specs + skill)\n"
        "================================================================================\n"
        f"[CONTENT_SPEC]\n{content_spec}\n\n"
        f"[NARRATION_FLOW_SPEC]\n{narration_spec}\n\n"
        f"[JSON_SCHEMA_SPEC]\n{schema_spec}\n\n"
        f"[SKILL_CONTENT_GENERATION]\n{skill_gen}\n"
    )


def _extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        first_nl = text.find("\n")
        last_fence = text.rfind("```", first_nl)
        if first_nl != -1 and last_fence > first_nl:
            text = text[first_nl + 1 : last_fence].strip()

    decoder = json.JSONDecoder()
    merged: dict[str, Any] = {}
    idx = 0
    while idx < len(text):
        next_brace = text.find("{", idx)
        if next_brace == -1:
            break
        try:
            obj, end = decoder.raw_decode(text, next_brace)
            if isinstance(obj, dict):
                merged.update(obj)
            idx = end
        except json.JSONDecodeError:
            idx = next_brace + 1

    if not merged:
        raise ValueError("LLM response does not contain a JSON object")
    return merged


async def generate_article_with_llm(
    inp: WorkflowInput,
    *,
    sub_topic_description: str,
    refinement: Optional[dict[str, Any]] = None,
    previous_article_md: str = "",
    previous_article_json: Optional[dict[str, Any]] = None,
    original_prompt_text: str = "",
) -> tuple[str, dict[str, Any]]:
    settings = AppSettings.shared
    llm = settings.llm

    if refinement is None:
        prompt = _build_generation_prompt(inp, sub_topic_description=sub_topic_description)
        print("**********GENERATOR PROMPT***************- START \n\n")
        print("PROMPT\n")
        print(prompt)
        print("\n\n**********GENERATOR PROMPT***************- END \n\n")
    else:
        prompt = _build_refine_prompt(
            inp,
            previous_article_md=previous_article_md,
            previous_article_json=previous_article_json or {},
            merged_eval=refinement,
            original_prompt_text=original_prompt_text,
        )

        print("**********REFINE PROMPT***************- START \n\n")
        print("PROMPT\n")
        print(prompt)
        print("\n\n**********REFINE PROMPT***************- END \n\n")


    from ..llm_factory import acomplete_with_backoff

    resp = await acomplete_with_backoff(llm, prompt)
    raw = str(resp)

    article_md, article_json = _split_md_and_json(raw)
    return article_md, article_json


def _split_md_and_json(raw: str) -> tuple[str, dict[str, Any]]:
    """Extract article_md and article_json from the LLM response.

    Handles multiple response shapes:
    1. Single JSON: {"article_md": "...", "article_json": {...}}
    2. article_md contains embedded ```json block with the article JSON
    3. Markdown followed by a bare JSON object
    """
    try:
        obj = _extract_json_object(raw)
    except ValueError:
        obj = {}

    if "article_md" in obj and "article_json" in obj:
        md = obj["article_md"]
        aj = obj["article_json"]
        if isinstance(aj, str):
            aj = json.loads(aj)
        return md, aj

    md_text = obj.get("article_md", raw)
    if not isinstance(md_text, str):
        md_text = raw

    json_block = _extract_fenced_json(md_text)
    if json_block is not None:
        md_clean = _remove_trailing_json_fence(md_text)
        return md_clean, json_block

    json_block = _extract_trailing_json(md_text)
    if json_block is not None:
        idx = md_text.rfind("{")
        md_clean = md_text[:idx].rstrip()
        return md_clean, json_block

    raise ValueError(
        "Could not extract article_md + article_json from LLM response. "
        f"Top-level keys: {list(obj.keys()) if obj else '(not JSON)'}"
    )


def _extract_fenced_json(text: str) -> dict[str, Any] | None:
    """Find the last ```json ... ``` block and parse it."""
    marker = "```json"
    idx = text.rfind(marker)
    if idx == -1:
        marker = "```"
        idx = text.rfind(marker)
        inner_start = idx + len(marker)
        rest = text[inner_start:]
        if not rest.lstrip().startswith("{"):
            return None
    else:
        inner_start = idx + len(marker)

    fence_end = text.find("```", inner_start)
    if fence_end == -1:
        snippet = text[inner_start:]
    else:
        snippet = text[inner_start:fence_end]

    snippet = snippet.strip()
    if not snippet.startswith("{"):
        return None
    try:
        return json.loads(snippet)
    except json.JSONDecodeError:
        return None


def _remove_trailing_json_fence(text: str) -> str:
    """Remove the last ```json...``` block from markdown text."""
    marker = "```json"
    idx = text.rfind(marker)
    if idx == -1:
        idx = text.rfind("```")
    if idx == -1:
        return text
    return text[:idx].rstrip()


def _extract_trailing_json(text: str) -> dict[str, Any] | None:
    """Try to parse a JSON object from the tail of the text."""
    idx = text.rfind("{")
    if idx == -1:
        return None
    snippet = text[idx:]
    try:
        decoder = json.JSONDecoder()
        obj, _ = decoder.raw_decode(snippet)
        if isinstance(obj, dict) and len(obj) > 2:
            return obj
    except json.JSONDecodeError:
        pass
    return None
