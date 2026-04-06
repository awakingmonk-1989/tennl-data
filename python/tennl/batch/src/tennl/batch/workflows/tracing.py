from __future__ import annotations

import contextvars
import json
import logging
import threading
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional

from llama_index.core.instrumentation import get_dispatcher
from llama_index.core.instrumentation.events import BaseEvent
from llama_index.core.instrumentation.event_handlers import BaseEventHandler
from llama_index.core.instrumentation.span_handlers import SimpleSpanHandler


DEFAULT_TRACE_PATH = Path("logs/workflow_traces.jsonl")
DEFAULT_RUN_LOG_PATH = Path("logs/workflow_run.log")

_PLAIN_LOG_FMT = (
    "%(asctime)s %(levelname)-8s [%(threadName)s] "
    "%(name)s.%(funcName)s:%(lineno)d — %(message)s"
)
_PLAIN_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def setup_rolling_jsonl_logger(
    path: Path = DEFAULT_TRACE_PATH,
    max_bytes: int = 5_000_000,
    backup_count: int = 5,
) -> logging.Logger:
    path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("tennl.workflow.trace")
    logger.setLevel(logging.INFO)

    if any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        return logger

    handler = RotatingFileHandler(
        path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def setup_rolling_run_logger(
    path: Path = DEFAULT_RUN_LOG_PATH,
    max_bytes: int = 10_000_000,
    backup_count: int = 5,
) -> logging.Logger:
    """Plain-text rolling logger for human-readable workflow diagnostics.

    Verbose on failures (exc_info, full context), terse on success.
    Format includes threadName, module, funcName, lineno for traceability.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("tennl.workflow.run")
    logger.setLevel(logging.DEBUG)

    if any(
        isinstance(h, RotatingFileHandler) and str(path) in str(getattr(h, "baseFilename", ""))
        for h in logger.handlers
    ):
        return logger

    handler = RotatingFileHandler(
        path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(_PLAIN_LOG_FMT, datefmt=_PLAIN_DATE_FMT))
    logger.addHandler(handler)

    # Console handler for live visibility during CLI execution.
    # Enabled by default unless explicitly disabled.
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console = logging.StreamHandler(stream=sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(_PLAIN_LOG_FMT, datefmt=_PLAIN_DATE_FMT))
        logger.addHandler(console)

    logger.propagate = False
    return logger


def safe_summary(value: Any, max_len: int = 240) -> str:
    s = str(value)
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def tokens_used_from_llama_index_instrumentation(_maybe: Any) -> Optional[int]:
    return None


_current_run_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("tennl_run_id", default=None)


class RunContext:
    def __init__(self, run_id: str):
        self._token = None
        self._run_id = run_id

    def __enter__(self) -> None:
        self._token = _current_run_id.set(self._run_id)

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._token is not None:
            _current_run_id.reset(self._token)


class _RollingFileEventHandler(BaseEventHandler):
    logger_name: str = "tennl.workflow.trace"

    @classmethod
    def class_name(cls) -> str:
        return "RollingFileEventHandler"

    def handle(self, event: BaseEvent, **kwargs: Any) -> Any:
        logger = logging.getLogger(self.logger_name)
        run_id = _current_run_id.get()
        payload = {
            "event_type": "llamaindex_event",
            "run_id": run_id,
            "event_class": event.__class__.__name__,
            "event": event.model_dump(),
        }
        logger.info(json.dumps(payload, ensure_ascii=False))
        return None


_install_lock = threading.Lock()
_installed_once: bool = False


def install_llamaindex_instrumentation_logging() -> None:
    """One-time install of global LlamaIndex instrumentation sinks."""
    setup_rolling_jsonl_logger()
    with _install_lock:
        global _installed_once
        if _installed_once:
            return
        d = get_dispatcher()
        d.add_event_handler(_RollingFileEventHandler())
        # SimpleSpanHandler enables standard span tracking in the dispatcher.
        # Events already include span_id; for local JSONL, logging events is sufficient.
        d.add_span_handler(SimpleSpanHandler())
        _installed_once = True


async def log_workflow_event_stream(handler: Any, *, run_id: str, logger: logging.Logger) -> None:
    """Consume workflow handler stream events and log them to our JSONL sink."""
    async for ev in handler.stream_events():
        record = {
            "event_type": "workflow_stream_event",
            "run_id": run_id,
            "event_class": ev.__class__.__name__,
            "event": getattr(ev, "model_dump", lambda: {"repr": repr(ev)})(),
        }
        logger.info(json.dumps(record, ensure_ascii=False))
