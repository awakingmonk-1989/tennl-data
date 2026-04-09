from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import PydanticBaseSettingsSource

from tennl.batch.settings.articles import ContentType, LongArticlePromptSettings
from tennl.batch.settings.llm import LlmProviderConfig, LlmSettings
from tennl.batch.settings.insight_cards import InsightCardSettings
from tennl.batch.settings.util import load_yaml_settings, pick_provider


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
    prompts: LongArticlePromptSettings = Field(default_factory=LongArticlePromptSettings)
    insight_cards: InsightCardSettings = Field(default_factory=InsightCardSettings)

    shared: ClassVar["AppSettings"]

    @property
    def llm_provider(self) -> LlmProviderConfig:
        preferred = os.environ.get("TENNL_LLM_PROVIDER")
        return pick_provider(self.llm_config.providers, preferred)

    @property
    def llm(self):
        from tennl.batch.workflows.llm_factory import build_llm

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
                    return load_yaml_settings()
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
    return AppSettings()
