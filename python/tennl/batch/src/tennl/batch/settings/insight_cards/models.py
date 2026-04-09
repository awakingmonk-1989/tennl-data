from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class InsightCardGenerationSettings(BaseModel):
    """Batch parameters for insight-card generation (LlamaIndex orchestrator)."""

    model_config = ConfigDict(extra="allow")

    prompt_version: str = "large"
    count: int = 10
    max_workers: int = 4
    max_tokens: int = 600
    output_file: str = "insight_cards_output.json"


class InsightCardPromptPack(BaseModel):
    """One prompt version (mini / large / small / moe, etc.)."""

    model_config = ConfigDict(extra="forbid")

    system_prompt: str = ""
    user_prompt: str

    def templates(self) -> tuple[str, str]:
        return self.system_prompt, self.user_prompt


class InsightCardPromptBlocks(BaseModel):
    """Pre-written prompt text injected into the system prompt at runtime.

    These strings are read from the YAML ``formatter.prompt_blocks`` section
    and substituted into the system prompt via ``{layout_library}``,
    ``{selection_table}``, and ``{slot_sizing}`` placeholders.
    """

    model_config = ConfigDict(extra="forbid")

    layout_library: str
    selection_table: str
    slot_sizing: str


class InsightCardFormatterSettings(BaseModel):
    """Layout templates, block schemas, and prompt injection blocks.

    Lives under the ``formatter:`` key in ``insight-card-settings.yaml``.
    """

    model_config = ConfigDict(extra="forbid")

    templates: list[str]
    block_schemas: dict[str, list[str]]
    prompt_blocks: InsightCardPromptBlocks


class InsightCardSettings(BaseModel):
    """Insight card YAML (`resources/insight-cards/insight-card-settings.yaml`)."""

    model_config = ConfigDict(extra="forbid")

    generation: InsightCardGenerationSettings = Field(default_factory=InsightCardGenerationSettings)
    formatter: Optional[InsightCardFormatterSettings] = Field(default=None)
    prompts: dict[str, InsightCardPromptPack] = Field(default_factory=dict)

    def prompt_templates(self, version: str) -> tuple[str, str]:
        if version not in self.prompts:
            raise KeyError(
                f"Unknown insight card prompt_version {version!r}; "
                f"known: {sorted(self.prompts.keys())}"
            )
        return self.prompts[version].templates()
