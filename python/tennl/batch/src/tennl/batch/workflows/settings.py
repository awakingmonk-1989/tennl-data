from __future__ import annotations

import logging
from functools import lru_cache
import importlib.resources as ir
import os
from typing import Any, ClassVar, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import PydanticBaseSettingsSource


ContentType = Literal["articles", "jokes", "short_reads", "long_reads"]
ProviderName = Literal["openai", "litellm", "azure-foundry-openai", "anthropic", "openai_like"]

logger = logging.getLogger(__name__)

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


class PromptTemplate(BaseModel):
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
    def _check_blocks_populated(self) -> "PromptTemplate":
        if not self.name:
            return self
        missing = [k for k in self._REQUIRED_BLOCKS if not getattr(self, k, "").strip()]
        if missing:
            raise ValueError(
                f"PromptTemplate '{self.name}' has empty required blocks: {sorted(missing)}"
            )
        return self


class PromptSettings(BaseModel):
    model_config = ConfigDict(extra="allow")
    content_gen_base: PromptTemplate = Field(default_factory=PromptTemplate)
    content_gen_novelty_v1: PromptTemplate = Field(default_factory=PromptTemplate)


def _deep_merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge override into base (override wins)."""
    out: dict[str, Any] = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge_dicts(out[k], v)
        else:
            out[k] = v
    return out


def _load_yaml_settings(config_file: str = "app.yaml") -> dict[str, Any]:
    """Load settings from packaged YAML files shipped with the wheel.

    Reads ``app.yaml`` (main config) and ``prompts.yaml`` (prompt templates).
    Both are resolved via ``importlib.resources`` so they work identically
    from source checkout and from an installed wheel.
    """
    try:
        text = ir.files("tennl.batch").joinpath("resources", config_file).read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Unable to load config file. Error: {e!s}", exc_info=True)
        return {}

    raw = yaml.safe_load(text) or {}
    if not isinstance(raw, dict):
        raise ValueError("Invalid YAML root object in packaged app.yaml")

    try:
        prompts_text = ir.files("tennl.batch").joinpath("resources", "prompts.yaml").read_text(encoding="utf-8")
        prompts_raw = yaml.safe_load(prompts_text) or {}
        if isinstance(prompts_raw, dict):
            raw["prompts"] = prompts_raw
    except Exception as e:
        logger.error(f"Unable to load prompt config file. Error: {e!s}", exc_info=True)
        pass

    return raw


def _pick_provider(providers: list[LlmProviderConfig], preferred: Optional[str]) -> LlmProviderConfig:
    if not providers:
        raise ValueError("No providers configured under llm.providers")

    if preferred:
        for p in providers:
            if p.name == preferred:
                return p
        raise ValueError(f"Provider '{preferred}' not found in llm.providers")

    # Default to azure for this project unless overridden.
    for p in providers:
        if p.name == "azure-foundry-openai":
            return p
    return providers[0]


class AppSettings(BaseSettings):
    """Application settings with deterministic precedence.

    Precedence:
    1) OS env
    2) .env
    3) YAML (packaged app.yaml)
    4) defaults

    Access via `AppSettings.shared`.
    """

    model_config = SettingsConfigDict(
        extra="forbid",
        env_prefix="TENNL_",
        env_nested_delimiter="__",
        env_file=(".env",),
        case_sensitive=False,
    )

    content_type: ContentType = "articles"
    content_types: list[ContentType] = Field(default_factory=lambda: ["articles", "jokes", "short_reads", "long_reads"])

    llm_config: LlmSettings = Field(default_factory=LlmSettings, validation_alias="llm")
    prompts: PromptSettings = Field(default_factory=PromptSettings)

    shared: ClassVar["AppSettings"]

    @property
    def llm_provider(self) -> LlmProviderConfig:
        preferred = os.environ.get("TENNL_LLM_PROVIDER")
        return _pick_provider(self.llm_config.providers, preferred)

    @property
    def llm(self):
        from .llm_factory import build_llm

        return build_llm(self.llm_provider)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        class _YamlSettingsSource(PydanticBaseSettingsSource):
            def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
                raise NotImplementedError()

            def __call__(self) -> dict[str, Any]:
                try:
                    return _load_yaml_settings()
                except Exception:
                    # Keep imports/tooling resilient; runtime will surface issues
                    # when settings are actually accessed.
                    return {}

        # Order is precedence (earlier wins)
        return (
            env_settings,
            dotenv_settings,
            _YamlSettingsSource(settings_cls),
            init_settings,
        )


@lru_cache(maxsize=1)
def _shared_settings() -> AppSettings:
    # Creation is cheap, but keep a stable singleton in-process.
    return AppSettings()


AppSettings.shared = _shared_settings()

