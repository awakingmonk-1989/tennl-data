from __future__ import annotations

from typing import Any, Literal, Optional

from llama_index.core.workflow.events import Event

from .models import (
    EvalDecision,
    MergedEvalReport,
    ModerationReport,
    QualityAndSchemaBundle,
    RefinementDirectives,
    RegenerationMode,
    SchemaReport,
    WorkflowError,
    WorkflowInput,
)


class WorkflowStart(Event):
    input: WorkflowInput


class ValidatedInput(Event):
    input: WorkflowInput


class GeneratedContent(Event):
    attempt_number: int
    article_md: str
    article_json: dict[str, Any]


class ModerationEvaluated(Event):
    report: ModerationReport


class QualityEvaluated(Event):
    bundle: QualityAndSchemaBundle


class EvalMerged(Event):
    report: MergedEvalReport


class RefinementDirectivesBuilt(Event):
    directives: RefinementDirectives


class FinalValidated(Event):
    result: Literal["PASS", "FAIL"]
    report: dict[str, Any]


class WorkflowFailed(Event):
    error: WorkflowError


class WorkflowSucceeded(Event):
    article_md: str
    article_json: dict[str, Any]
    merged_report: Optional[MergedEvalReport] = None
