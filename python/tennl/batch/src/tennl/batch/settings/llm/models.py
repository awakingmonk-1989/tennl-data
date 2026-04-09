from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ProviderName = Literal["openai", "litellm", "azure-foundry-openai", "anthropic", "openai_like"]


class LlmProviderConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: ProviderName
    url: str = ""
    auth_token: str = ""

    # Optional fields (we’ll expand over time as needed).
    model: str = "gpt-4o-mini"
    engine: Optional[str] = None  # Azure OpenAI often requires this
    api_version: Optional[str] = None

    # LLM generation parameters
    temperature: Optional[float] = None
    max_retries: Optional[int] = None
    context_window: Optional[int] = None
    is_chat_model: Optional[bool] = None
    is_function_calling_model: Optional[bool] = None


class LlmSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    providers: list[LlmProviderConfig] = Field(default_factory=list)
