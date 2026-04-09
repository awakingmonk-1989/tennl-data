from __future__ import annotations

from typing import Optional

from tennl.batch.settings.llm import LlmProviderConfig


def pick_provider(providers: list[LlmProviderConfig], preferred: Optional[str]) -> LlmProviderConfig:
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
