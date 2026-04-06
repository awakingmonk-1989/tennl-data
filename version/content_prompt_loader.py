from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class QualityConstraints:
    must_include: list[str]
    avoid: list[str]


@dataclass(frozen=True)
class PromptRuntimeInput:
    topic: str
    sub_topic: str
    sub_topic_description: str
    content_variant: str

    intent_profile: list[str]
    content_mode_pool: list[str]
    angle_pool: list[str]
    tone_pool: list[str]
    hook_style_pool: list[str]
    quality_constraints: QualityConstraints

    content_mode: str
    angle: str
    tone: str
    hook_style: str

    sample_md: str | None = None
    sample_json: str | None = None
    content_spec: str = ""
    narration_spec: str = ""
    schema_spec: str = ""
    skill_gen: str = ""


class ContentPromptTemplate:
    REQUIRED_KEYS = {
        "system_prompt",
        "runtime_input_block",
        "output_block",
        "attachments_block",
    }

    def __init__(self, template: dict[str, Any]) -> None:
        missing = self.REQUIRED_KEYS - set(template.keys())
        if missing:
            raise ValueError(f"Prompt YAML missing required keys: {sorted(missing)}")
        self.template = template

    @classmethod
    def from_yaml_file(cls, path: str | Path) -> "ContentPromptTemplate":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError("Prompt YAML root must be a mapping/object")
        return cls(data)

    @staticmethod
    def _normalize(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    @staticmethod
    def _optional_named_block(name: str, content: str | None) -> str:
        if not content:
            return ""
        return f"[{name}]\n{content.strip()}\n"

    @staticmethod
    def _validate_runtime(inp: PromptRuntimeInput) -> None:
        if inp.content_mode not in inp.content_mode_pool:
            raise ValueError(
                f"Selected content_mode '{inp.content_mode}' not in content_mode_pool"
            )
        if inp.angle not in inp.angle_pool:
            raise ValueError(f"Selected angle '{inp.angle}' not in angle_pool")
        if inp.tone not in inp.tone_pool:
            raise ValueError(f"Selected tone '{inp.tone}' not in tone_pool")
        if inp.hook_style not in inp.hook_style_pool:
            raise ValueError(
                f"Selected hook_style '{inp.hook_style}' not in hook_style_pool"
            )

    def render(self, inp: PromptRuntimeInput) -> str:
        self._validate_runtime(inp)

        sample_markdown_block = self._optional_named_block(
            "SAMPLE_MARKDOWN", inp.sample_md
        )
        sample_json_block = self._optional_named_block(
            "SAMPLE_JSON", inp.sample_json
        )

        values: dict[str, str] = {
            "topic": self._normalize(inp.topic),
            "sub_topic": self._normalize(inp.sub_topic),
            "sub_topic_description": self._normalize(inp.sub_topic_description),
            "content_variant": self._normalize(inp.content_variant),

            "intent_profile": self._normalize(inp.intent_profile),
            "content_mode_pool": self._normalize(inp.content_mode_pool),
            "angle_pool": self._normalize(inp.angle_pool),
            "tone_pool": self._normalize(inp.tone_pool),
            "hook_style_pool": self._normalize(inp.hook_style_pool),
            "must_include": self._normalize(inp.quality_constraints.must_include),
            "avoid": self._normalize(inp.quality_constraints.avoid),

            "content_mode": self._normalize(inp.content_mode),
            "angle": self._normalize(inp.angle),
            "tone": self._normalize(inp.tone),
            "hook_style": self._normalize(inp.hook_style),

            "sample_markdown_block": sample_markdown_block.strip(),
            "sample_json_block": sample_json_block.strip(),

            "content_spec": self._normalize(inp.content_spec),
            "narration_spec": self._normalize(inp.narration_spec),
            "schema_spec": self._normalize(inp.schema_spec),
            "skill_gen": self._normalize(inp.skill_gen),
        }

        parts = [
            self.template["system_prompt"].format(**values).strip(),
            self.template["runtime_input_block"].format(**values).strip(),
            self.template["output_block"].format(**values).strip(),
            self.template["attachments_block"].format(**values).strip(),
        ]
        return "\n\n".join(part for part in parts if part)


def build_prompt_runtime_input(
    inp,
    sub_topic_description: str,
    content_spec: str,
    narration_spec: str,
    schema_spec: str,
    skill_gen: str,
    sample_md: str | None,
    sample_json: str | None,
) -> PromptRuntimeInput:
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

        sample_md=sample_md,
        sample_json=sample_json,
        content_spec=content_spec,
        narration_spec=narration_spec,
        schema_spec=schema_spec,
        skill_gen=skill_gen,
    )


# Example usage:
# prompt_template = ContentPromptTemplate.from_yaml_file("content_generation_prompt.yaml")
# runtime_input = build_prompt_runtime_input(
#     inp=inp,
#     sub_topic_description=sub_topic_description,
#     content_spec=content_spec,
#     narration_spec=narration_spec,
#     schema_spec=schema_spec,
#     skill_gen=skill_gen,
#     sample_md=sample_md,
#     sample_json=sample_json,
# )
# final_prompt = prompt_template.render(runtime_input)
