from __future__ import annotations

import logging
from enum import StrEnum, Enum
from pathlib import Path
from typing import Any

import tenacity
from openai import APIConnectionError, APITimeoutError, InternalServerError, RateLimitError

from .settings import LlmProviderConfig

logger = logging.getLogger(__name__)

class LLMType(StrEnum):
    OPENAI = "openai"
    AZURE_FOUNDRY_OPENAI = "azure-openai"
    LITELLM = "lite_llm"

_TRANSIENT_LLM_ERRORS = (
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
)

_LLM_BACKOFF = tenacity.retry(
    retry=tenacity.retry_if_exception_type(_TRANSIENT_LLM_ERRORS),
    wait=tenacity.wait_random_exponential(min=4, max=120),
    stop=tenacity.stop_after_attempt(8),
    before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
    reraise=True,
)


@_LLM_BACKOFF
async def acomplete_with_backoff(llm: Any, prompt: str) -> Any:
    """llm.acomplete wrapped with exponential backoff for transient API errors."""
    return await llm.acomplete(prompt)


def _repo_root() -> Path:
    # .../tennl-data/python/tennl/batch/src/tennl/batch/workflows/llm_factory.py -> repo root is 7 parents up
    return Path(__file__).resolve().parents[7]


def _load_secret_token() -> str | None:
    """Load an LLM auth token from repo-root `secrets.txt`.

    Historical note: this repo originally used `secrets.txt` as a single-line token.
    It later evolved into a shell `KEY=VALUE` file (e.g. Azure storage connection
    string). We must *never* treat the whole file as a bearer token, otherwise the
    OpenAI/AzureOpenAI client will emit an invalid Authorization header.
    """
    p = _repo_root() / "secrets.txt"
    if not p.exists():
        return None
    raw = p.read_text(encoding="utf-8").strip()
    if not raw:
        return None

    # If the file looks like a shell env file, try extracting common LLM keys.
    if "\n" in raw or "=" in raw:
        for key in ("TENNL_AZURE_OPENAI_API_KEY", "OPENAI_API_KEY"):
            for line in raw.splitlines():
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                if k.strip() != key:
                    continue
                v = v.strip().strip('"').strip("'").strip()
                return v or None
        return None

    # Legacy single-line token form.
    return raw


def _optional_kwargs(cfg: LlmProviderConfig) -> dict[str, Any]:
    """Collect optional generation params that are set on the config."""
    kwargs: dict[str, Any] = {}
    if cfg.temperature is not None:
        kwargs["temperature"] = cfg.temperature
    if cfg.max_retries is not None:
        kwargs["max_retries"] = cfg.max_retries
    return kwargs


def build_llm(cfg: LlmProviderConfig):
    """
    Build a LlamaIndex LLM instance from YAML config.

    Config contract (minimum):
    - url: string
    - auth_token: string

    We also accept optional keys (e.g., model, engine, api_version,
    temperature, max_retries, context_window) and will extend this over time.
    """
    name = cfg.name
    opts = _optional_kwargs(cfg)

    if name == "openai":
        # Official OpenAI: `OpenAI(api_key=..., model=...)`
        # OpenAI-compatible gateway: prefer `OpenAILike(api_base=..., api_key=...)`
        if cfg.url:
            from llama_index.llms.openai_like import OpenAILike

            like_kwargs: dict[str, Any] = {}
            if cfg.context_window is not None:
                like_kwargs["context_window"] = cfg.context_window
            if cfg.is_chat_model is not None:
                like_kwargs["is_chat_model"] = cfg.is_chat_model
            if cfg.is_function_calling_model is not None:
                like_kwargs["is_function_calling_model"] = cfg.is_function_calling_model
            return OpenAILike(
                model=cfg.model,
                api_base=cfg.url,
                api_key=cfg.auth_token or None,
                **opts,
                **like_kwargs,
            )

        from llama_index.llms.openai import OpenAI

        return OpenAI(model=cfg.model, api_key=cfg.auth_token or None, **opts)

    if name == "litellm":
        from llama_index.llms.litellm import LiteLLM

        return LiteLLM(
            model=cfg.model,
            api_base=cfg.url or None,
            api_key=cfg.auth_token or None,
            **opts,
        )

    if name == "anthropic":
        from llama_index.llms.anthropic import Anthropic

        return Anthropic(
            model=cfg.model,
            api_key=cfg.auth_token or None,
            **opts,
        )

    if name == "openai_like":
        from llama_index.llms.openai_like import OpenAILike

        like_kwargs = {}
        if cfg.context_window is not None:
            like_kwargs["context_window"] = cfg.context_window
        if cfg.is_chat_model is not None:
            like_kwargs["is_chat_model"] = cfg.is_chat_model
        if cfg.is_function_calling_model is not None:
            like_kwargs["is_function_calling_model"] = cfg.is_function_calling_model
        return OpenAILike(
            model=cfg.model,
            api_base=cfg.url or None,
            api_key=cfg.auth_token or None,
            **opts,
            **like_kwargs,
        )

    if name == "azure-foundry-openai":
        import os

        from llama_index.llms.azure_openai import AzureOpenAI

        azure_kwargs: dict[str, Any] = {}
        if cfg.api_version:
            azure_kwargs["api_version"] = cfg.api_version
        engine = cfg.engine
        if not engine:
            engine = os.environ.get("TENNL_AZURE_OPENAI_ENGINE", "").strip() or None
        if not engine:
            raise ValueError(
                "azure-foundry-openai provider requires `engine` (Azure deployment name) "
                "in app.yaml or TENNL_AZURE_OPENAI_ENGINE env var"
            )
        azure_kwargs["engine"] = engine
        azure_api_key = os.environ.get("TENNL_AZURE_OPENAI_API_KEY", "").strip() or None

        return AzureOpenAI(
            model=cfg.model,
            azure_endpoint=cfg.url or None,
            api_key=azure_api_key or cfg.auth_token or _load_secret_token(),
            max_retries=opts.get("max_retries", 8),
            timeout=120.0,
            **{k: v for k, v in opts.items() if k != "max_retries"},
            **azure_kwargs,
        )

    raise ValueError(f"Unknown LLM provider: {name}")

