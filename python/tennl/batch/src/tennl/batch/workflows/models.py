from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ContentVariant(str, Enum):
    CURATED_WEB_WITH_IMAGES = "CURATED_WEB_WITH_IMAGES"
    CURATED_WEB_NO_IMAGES = "CURATED_WEB_NO_IMAGES"
    AI_GENERATED = "AI_GENERATED"


class EvalMode(str, Enum):
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"


class WorkflowInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: str
    sub_topic: str
    content_variant: ContentVariant

    eval_mode: EvalMode = EvalMode.PARALLEL
    max_refine_attempts: int = Field(default=1, ge=0, le=1)

    # Creative control pools (Layer 1 — base metadata)
    intent_profile: list[str] = Field(default_factory=list)
    content_mode_pool: list[str] = Field(default_factory=list)
    angle_pool: list[str] = Field(default_factory=list)
    tone_pool: list[str] = Field(default_factory=list)
    hook_style_pool: list[str] = Field(default_factory=list)
    quality_constraints: "QualityConstraints" = Field(default_factory=lambda: QualityConstraints())

    # Runtime selections (Layer 2 — exactly 1 from each pool)
    content_mode: str = ""
    angle: str = ""
    tone: str = ""
    hook_style: str = ""


# ---------------------------------------------------------------------------
# Prompt runtime input — typed contract for prompt template rendering
# ---------------------------------------------------------------------------

class QualityConstraints(BaseModel):
    model_config = ConfigDict(frozen=True)

    must_include: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)


class PromptRuntimeInput(BaseModel):
    """Typed, immutable input for prompt template rendering.

    Constructed once per generation call via ``build_prompt_runtime_input()``.
    Pool-membership validation is performed externally before rendering.
    """

    model_config = ConfigDict(frozen=True)

    topic: str
    sub_topic: str
    sub_topic_description: str
    content_variant: str

    intent_profile: list[str] = Field(default_factory=list)
    content_mode_pool: list[str] = Field(default_factory=list)
    angle_pool: list[str] = Field(default_factory=list)
    tone_pool: list[str] = Field(default_factory=list)
    hook_style_pool: list[str] = Field(default_factory=list)
    quality_constraints: QualityConstraints = Field(default_factory=QualityConstraints)

    content_mode: str = ""
    angle: str = ""
    tone: str = ""
    hook_style: str = ""

    sample_md: Optional[str] = None
    sample_json: Optional[str] = None
    prompt: str = ""
    content_spec: str = ""
    narration_spec: str = ""
    schema_spec: str = ""
    skill_gen: str = ""


class FailureReason(str, Enum):
    INPUT_VALIDATION_FAILED = "INPUT_VALIDATION_FAILED"
    EVALUATION_CRITERIA_NOT_MET = "EVALUATION_CRITERIA_NOT_MET"
    FINAL_VALIDATION_FAILED = "FINAL_VALIDATION_FAILED"
    RUNTIME_ERROR = "RUNTIME_ERROR"


class WorkflowError(BaseModel):
    failure_reason: FailureReason
    error_node: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None


StageResult = Literal["PASS", "FAIL", "SKIPPED", "ERROR", "TIMEOUT"]


class ModerationCheck(BaseModel):
    check_id: str
    ok: bool
    message: str


class ModerationReport(BaseModel):
    result: Literal["PASS", "FAIL"]
    checks: list[ModerationCheck] = Field(default_factory=list)
    violations: list[ModerationCheck] = Field(default_factory=list)


class QualityReport(BaseModel):
    result: Literal["PASS", "FAIL", "SKIPPED"]
    dimensions: dict[str, float] = Field(default_factory=dict)
    avg: float = 0.0
    min_dimension: float = 0.0
    thresholds: dict[str, float] = Field(default_factory=dict)


class SchemaFailure(BaseModel):
    path: str
    message: str


class SchemaReport(BaseModel):
    result: Literal["PASS", "FAIL", "SKIPPED"]
    failures: list[SchemaFailure] = Field(default_factory=list)


class QualityAndSchemaBundle(BaseModel):
    result: Literal["PASS", "FAIL"]
    quality_report: QualityReport
    schema_report: SchemaReport
    skipped_due_to: Optional[str] = None


class EvalDecision(str, Enum):
    PROCEED = "PROCEED"
    REFINE = "REFINE"
    FAIL = "FAIL"


class MergedEvalReport(BaseModel):
    decision: EvalDecision
    moderation: ModerationReport
    quality: QualityAndSchemaBundle


class RegenerationMode(str, Enum):
    FULL = "FULL"
    TARGETED = "TARGETED"


class RefinementDirectives(BaseModel):
    regeneration_mode: RegenerationMode
    directives: dict[str, Any] = Field(default_factory=dict)


class TraceEntry(BaseModel):
    node_id: str
    node_name: str
    started_at: str
    finished_at: str
    duration_ms: int
    result: StageResult
    output_summary: str
    tokens_used: Optional[int] = None


class StageCompletedPayload(BaseModel):
    """Structured payload for trace sink stage completion events."""

    model_config = ConfigDict(extra="forbid")

    node_id: str
    node_name: str
    result: StageResult
    duration_ms: int

    output_summary: Optional[str] = None
    attempt_number: Optional[int] = None
    violations_count: Optional[int] = None
    decision: Optional[str] = None
    regeneration_mode: Optional[str] = None
    error: Optional[dict[str, Any]] = None


class WorkflowOutput(BaseModel):
    article_md: str
    article_json: dict[str, Any]
    status: Literal["GENERATED", "FAILED_WITH_REASON"]
    run_id: str
    execution_trace: list[TraceEntry] = Field(default_factory=list)
    error: Optional[WorkflowError] = None


class RunState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Workflows requires typed state to be default-constructible.
    run_id: str = ""
    refine_attempts: int = 0

    workflow_input: Optional[dict[str, Any]] = None
    execution_trace: list[dict[str, Any]] = Field(default_factory=list)

    last_article_md: Optional[str] = None
    last_article_json: Optional[dict[str, Any]] = None

    moderation_report: Optional[ModerationReport] = None
    quality_bundle: Optional[QualityAndSchemaBundle] = None
    merged_eval: Optional[MergedEvalReport] = None
    refinement_directives: Optional[RefinementDirectives] = None
