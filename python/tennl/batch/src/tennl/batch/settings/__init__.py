"""Central application settings (YAML, env, ``AppSettings.shared``)."""

from tennl.batch.settings.app_settings import AppSettings, _shared_settings
from tennl.batch.settings.articles import (
    ContentType,
    LongArticlePromptTemplate,
    LongArticlePromptSettings,
)
from tennl.batch.settings.llm import LlmProviderConfig, LlmSettings, ProviderName
from tennl.batch.settings.insight_cards import (
    InsightCardGenerationSettings,
    InsightCardPromptPack,
    InsightCardSettings,
)
from tennl.batch.settings.util import deep_merge_dicts, load_yaml_settings, pick_provider

AppSettings.shared = _shared_settings()

__all__ = [
    "AppSettings",
    "ContentType",
    "InsightCardGenerationSettings",
    "InsightCardPromptPack",
    "InsightCardSettings",
    "LlmProviderConfig",
    "LlmSettings",
    "LongArticlePromptTemplate",
    "LongArticlePromptSettings",
    "ProviderName",
    "deep_merge_dicts",
    "load_yaml_settings",
    "pick_provider",
]
