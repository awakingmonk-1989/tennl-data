from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LongArticlePromptTemplate(BaseModel):
    """A single prompt split into declarative blocks.

    YAML is static template text; Python handles optional-block assembly,
    normalization, and substitution.
    """

    model_config = ConfigDict(extra="allow")

    name: str = ""
    version: int = 1
    system_prompt: str = ""
    runtime_input_block: str = ""
    output_block: str = ""
    attachments_block: str = ""

    _REQUIRED_BLOCKS = {"system_prompt", "runtime_input_block", "output_block", "attachments_block"}

    @model_validator(mode="after")
    def _check_blocks_populated(self) -> LongArticlePromptTemplate:
        if not self.name:
            return self
        missing = [k for k in self._REQUIRED_BLOCKS if not getattr(self, k, "").strip()]
        if missing:
            raise ValueError(
                f"PromptTemplate '{self.name}' has empty required blocks: {sorted(missing)}"
            )
        return self


class LongArticlePromptSettings(BaseModel):
    model_config = ConfigDict(extra="allow")
    content_gen_base: LongArticlePromptTemplate = Field(default_factory=LongArticlePromptTemplate)
    content_gen_novelty_v1: LongArticlePromptTemplate = Field(default_factory=LongArticlePromptTemplate)
