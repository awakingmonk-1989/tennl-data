from __future__ import annotations

from typing import Literal

from ..models import EvalDecision, MergedEvalReport, ModerationReport, QualityAndSchemaBundle


Decision = Literal["PROCEED", "REFINE", "FAIL"]


def merge_and_route(
    moderation_report: ModerationReport,
    quality_bundle: QualityAndSchemaBundle,
    refine_attempts: int,
    max_refine_attempts: int,
) -> MergedEvalReport:
    mod_pass = moderation_report.result == "PASS"
    qual_pass = quality_bundle.result == "PASS"

    if mod_pass and qual_pass:
        decision: EvalDecision = EvalDecision.PROCEED
    elif refine_attempts < max_refine_attempts:
        decision = EvalDecision.REFINE
    else:
        decision = EvalDecision.FAIL

    return MergedEvalReport(decision=decision, moderation=moderation_report, quality=quality_bundle)

