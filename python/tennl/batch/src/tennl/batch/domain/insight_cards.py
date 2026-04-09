"""Internal insight-card models used by the orchestrator."""

from __future__ import annotations

import hashlib
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class InsightCard(BaseModel):
    """Structured LLM output for one generated insight card."""

    model_config = ConfigDict(extra="forbid")

    title: str
    category: str
    content: str
    layout: str
    content_blocks: dict[str, str | list[str]]
    tone: str
    emotional_register: str
    title_style: str
    hook_type: str
    opening_word_class: str


class CompletionTokensDetails(BaseModel):
    """Detailed breakdown of completion tokens (LiteLLM/Gemini)."""

    model_config = ConfigDict(extra="allow")

    reasoning_tokens: int = 0
    text_tokens: int = 0


class PromptTokensDetails(BaseModel):
    """Detailed breakdown of prompt tokens (LiteLLM/Gemini)."""

    model_config = ConfigDict(extra="allow")

    text_tokens: Optional[int] = None
    audio_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None
    image_tokens: Optional[int] = None
    video_tokens: Optional[int] = None


class LiteLLMGeminiTokenUsage(BaseModel):
    """Full token usage from a LiteLLM ModelResponse.usage for Gemini calls.

    Maps every field from the ``usage`` section of a LiteLLM ``ModelResponse``
    (see ``response_raw_dump.json`` for a live sample).
    """

    model_config = ConfigDict(extra="allow")

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    completion_tokens_details: Optional[CompletionTokensDetails] = None
    prompt_tokens_details: Optional[PromptTokensDetails] = None
    cache_read_input_tokens: Optional[int] = None


class InsightCardResult(BaseModel):
    """Persisted card result with runtime metadata."""

    model_config = ConfigDict(extra="allow")

    title: str = Field(default="")
    category: str = Field(default="")
    content: str = Field(default="")
    layout: Optional[str] = Field(default=None)
    content_blocks: Optional[dict[str, str | list[str]]] = Field(default=None)
    tone: str = Field(default="")
    emotional_register: str = Field(default="")
    title_style: str = Field(default="")
    hook_type: str = Field(default="")
    opening_word_class: str = Field(default="")

    provider: str = Field(default="")
    raw: str = Field(default="")
    error: Optional[str] = Field(default=None)

    metadata: Optional[dict[str, Any]] = Field(default=None)

    def is_valid(self) -> bool:
        return bool(self.title and self.content and not self.error)

    def fingerprint(self) -> str:
        return hashlib.md5(f"{self.title}{self.content}".encode()).hexdigest()[:10]
