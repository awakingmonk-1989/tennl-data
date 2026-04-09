"""Backward-compatible re-exports. Prefer :mod:`tennl.batch.settings`."""

from tennl.batch.settings import (
    AppSettings,
    ContentType,
    InsightCardGenerationSettings,
    InsightCardPromptPack,
    InsightCardSettings,
    LlmProviderConfig,
    LlmSettings,
    LongArticlePromptTemplate,
    LongArticlePromptSettings,
    ProviderName,
    deep_merge_dicts,
    load_yaml_settings,
    pick_provider,
)

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
