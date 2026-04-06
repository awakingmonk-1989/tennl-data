from __future__ import annotations

from typing import Any

from ..models import MergedEvalReport, RefinementDirectives, RegenerationMode

def build_refinement_directives(merged_eval: MergedEvalReport) -> RefinementDirectives:
    moderation = merged_eval.moderation
    quality = merged_eval.quality

    if moderation.result == "FAIL":
        return RefinementDirectives(
            regeneration_mode=RegenerationMode.FULL,
            directives={
            "reason": "Moderation violation(s) detected; full regeneration required.",
            "violations": [v.model_dump() for v in moderation.violations],
            "patch": {
                # Keep this minimal: real implementation would produce structured,
                # section-level directives.
                "hook": {
                    "type": "bold_lede",
                    "text": "Rewritten hook to comply with safety and structure requirements.",
                }
            },
            },
        )

    return RefinementDirectives(
        regeneration_mode=RegenerationMode.TARGETED,
        directives={
        "reason": "Quality/schema issues detected; targeted regeneration suggested.",
        "quality": quality.quality_report.model_dump(),
        "schema": quality.schema_report.model_dump(),
        "patch": {
            "quick_reference": {
                "title": "If you only do 3 things (refined)",
                "bullets": [
                    "Choose one tiny target",
                    "Work in short cycles",
                    "Add friction to distractions",
                ],
            }
        }},
    )

