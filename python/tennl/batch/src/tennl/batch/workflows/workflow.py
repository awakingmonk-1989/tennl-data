from __future__ import annotations

import datetime as dt
import logging
import time
import traceback
import uuid
from typing import Optional

from llama_index.core.workflow import Context, Workflow, step
from llama_index.core.workflow.events import StartEvent, StopEvent

from .events import (
    EvalMerged,
    FinalValidated,
    GeneratedContent,
    ModerationEvaluated,
    QualityEvaluated,
    RefinementDirectivesBuilt,
    ValidatedInput,
    WorkflowFailed,
    WorkflowSucceeded,
)
from .models import (
    EvalDecision,
    FailureReason,
    ModerationReport,
    QualityAndSchemaBundle,
    QualityReport,
    RunState,
    SchemaReport,
    TraceEntry,
    WorkflowError,
    WorkflowInput,
    WorkflowOutput,
)
from .stages.eval_merge import merge_and_route
from .stages.final_validation import final_validate
from .stages.generator import generate_article_with_llm
from .stages.input_validation import validate_input
from .stages.moderation_eval import run_moderation_checks, run_moderation_with_llm
from .stages.quality_eval import run_quality_and_schema_eval, run_quality_with_llm
from .stages.refiner import build_refinement_directives
from .stages.schema_validation import validate_article_schema
from .runtime_assets import read_article_asset
from .tracing import safe_summary, setup_rolling_run_logger

_log = logging.getLogger("tennl.workflow.run")


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


async def _append_trace(
    ctx: Context[RunState],
    *,
    node_id: str,
    node_name: str,
    started_at: str,
    finished_at: str,
    duration_ms: int,
    result: str,
    output_summary: str,
    tokens_used: Optional[int] = None,
) -> None:
    trace = await ctx.store.get("execution_trace", default=[])
    trace.append(
        TraceEntry(
            node_id=node_id,
            node_name=node_name,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            result=result,  # type: ignore[arg-type]
            output_summary=output_summary,
            tokens_used=tokens_used,
        ).model_dump()
    )
    await ctx.store.set("execution_trace", trace)


async def _get_trace(ctx: Context[RunState]) -> list[TraceEntry]:
    raw = await ctx.store.get("execution_trace", default=[])
    out: list[TraceEntry] = []
    for item in raw:
        try:
            out.append(TraceEntry.model_validate(item))
        except Exception as e :
            print(f"Error while fetching trace. Reason: {e!s}")
            continue
    return out


class ContentGenWorkflow(Workflow):
    def __init__(self, *, timeout: int = 300, verbose: bool = False) -> None:
        super().__init__(timeout=timeout, verbose=verbose)

    @step
    async def n1_input_validation(self, ctx: Context[RunState], ev: StartEvent) -> ValidatedInput | WorkflowFailed:
        node_id, node_name = "N1", "INPUT_VALIDATION"
        started = time.time()
        started_at = _now_iso()

        run_id = ev.get("run_id") or str(uuid.uuid4())
        async with ctx.store.edit_state() as s:
            s.run_id = run_id

        try:
            raw = dict(ev)
            raw.pop("run_id", None)
            inp = validate_input(raw)

            finished_at = _now_iso()
            duration_ms = int((time.time() - started) * 1000)
            summary = f"Input validated: topic={inp.topic}, sub_topic={inp.sub_topic}"
            await _append_trace(
                ctx,
                node_id=node_id,
                node_name=node_name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                result="PASS",
                output_summary=summary,
                tokens_used=None,
            )
            _log.info("[%s] %s %s PASS — %s", run_id[:8], node_id, node_name, summary)
            return ValidatedInput(input=inp)
        except Exception as e:
            finished_at = _now_iso()
            duration_ms = int((time.time() - started) * 1000)
            err = WorkflowError(
                failure_reason=FailureReason.INPUT_VALIDATION_FAILED,
                error_node=node_id,
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
            )
            summary = f"Input validation failed: {e}"
            await _append_trace(
                ctx,
                node_id=node_id,
                node_name=node_name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                result="FAIL",
                output_summary=summary,
                tokens_used=None,
            )
            _log.error("[%s] %s %s FAIL — %s", run_id[:8], node_id, node_name, summary, exc_info=True)
            return WorkflowFailed(error=err)

    async def _do_content_generation(
        self, ctx: Context[RunState], ev: ValidatedInput | RefinementDirectivesBuilt,
    ) -> GeneratedContent | WorkflowFailed:
        """Shared generation logic for initial and refinement attempts."""
        node_id, node_name = "N2", "CONTENT_GENERATION"
        started = time.time()
        started_at = _now_iso()
        state = await ctx.store.get_state()
        run_id = state.run_id

        try:
            if isinstance(ev, ValidatedInput):
                inp = ev.input
                directives = None
                attempt = 1
                async with ctx.store.edit_state() as s:
                    s.workflow_input = inp.model_dump()
            else:
                inp = WorkflowInput.model_validate(state.workflow_input or {})
                directives = ev.directives.model_dump()
                attempt = state.refine_attempts + 2

            sub_topic_description = inp.sub_topic
            original_prompt_text = read_article_asset("prompts", "conten_gen_prompt_page_post.md")

            prev_md = state.last_article_md or ""
            prev_json = state.last_article_json or {}

            _log.info("[%s] %s %s starting attempt %d", run_id[:8], node_id, node_name, attempt)

            article_md, article_json = await generate_article_with_llm(
                inp,
                sub_topic_description=sub_topic_description,
                refinement=directives,
                previous_article_md=prev_md,
                previous_article_json=prev_json,
                original_prompt_text=original_prompt_text,
            )

            async with ctx.store.edit_state() as s:
                s.last_article_md = article_md
                s.last_article_json = article_json

            finished_at = _now_iso()
            duration_ms = int((time.time() - started) * 1000)
            words = len(article_md.split()) if article_md else 0
            summary = f"Generated article attempt {attempt} (~{words} words, {duration_ms}ms)"
            await _append_trace(
                ctx,
                node_id=node_id,
                node_name=node_name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                result="PASS",
                output_summary=summary,
                tokens_used=None,
            )
            _log.info("[%s] %s %s PASS — %s", run_id[:8], node_id, node_name, summary)
            return GeneratedContent(attempt_number=attempt, article_md=article_md, article_json=article_json)
        except Exception as e:
            finished_at = _now_iso()
            duration_ms = int((time.time() - started) * 1000)
            err = WorkflowError(
                failure_reason=FailureReason.RUNTIME_ERROR,
                error_node=node_id,
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
            )
            summary = f"Generation runtime error: {type(e).__name__}: {e}"
            await _append_trace(
                ctx,
                node_id=node_id,
                node_name=node_name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                result="ERROR",
                output_summary=summary,
                tokens_used=None,
            )
            _log.error("[%s] %s %s ERROR — %s", run_id[:8], node_id, node_name, summary, exc_info=True)
            return WorkflowFailed(error=err)

    @step
    async def n2_content_generation(
        self, ctx: Context[RunState], ev: ValidatedInput
    ) -> GeneratedContent | WorkflowFailed:
        return await self._do_content_generation(ctx, ev)

    @step
    async def n3_evaluation_gate(
        self, ctx: Context[RunState], ev: GeneratedContent
    ) -> ModerationEvaluated | WorkflowFailed:
        # N3 is a router; we implement moderation + quality as separate stages N4/N5
        # to preserve trace granularity. Here, we just forward.
        # Carry the article payload via Context state to keep event types clean.
        async with ctx.store.edit_state() as s:
            s.last_article_md = ev.article_md
            s.last_article_json = ev.article_json
        # Placeholder report used only for type routing into N4; actual moderation
        # report is produced in N4.
        return ModerationEvaluated(report=ModerationReport(result="PASS"))

    @step
    async def n4_moderation_eval(
        self, ctx: Context[RunState], ev: ModerationEvaluated
    ) -> QualityEvaluated | WorkflowFailed:
        node_id, node_name = "N4", "EVAL_MODERATION"
        started = time.time()
        started_at = _now_iso()
        state = await ctx.store.get_state()
        run_id = state.run_id

        try:
            article_md = state.last_article_md or ""
            article_json = state.last_article_json or {}

            moderation_report = await run_moderation_with_llm(article_md, article_json)
            async with ctx.store.edit_state() as s:
                s.moderation_report = moderation_report

            finished_at = _now_iso()
            duration_ms = int((time.time() - started) * 1000)
            result = "PASS" if moderation_report.result == "PASS" else "FAIL"

            violations_detail = ""
            if moderation_report.violations:
                viol_parts = [f"{v.check_id}: {v.message}" for v in moderation_report.violations]
                violations_detail = "; ".join(viol_parts)

            summary = f"Moderation {result}"
            if violations_detail:
                summary += f" — violations: [{violations_detail}]"

            await _append_trace(
                ctx,
                node_id=node_id,
                node_name=node_name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                result=result,
                output_summary=summary,
                tokens_used=None,
            )

            if result == "PASS":
                _log.info("[%s] %s %s PASS (%dms)", run_id[:8], node_id, node_name, duration_ms)
            else:
                _log.warning(
                    "[%s] %s %s FAIL (%dms) — violations: %s | checks: %s",
                    run_id[:8], node_id, node_name, duration_ms,
                    violations_detail,
                    "; ".join(f"{c.check_id}={'OK' if c.ok else 'FAIL'}: {c.message}" for c in moderation_report.checks),
                )

            state = await ctx.store.get_state()
            inp = WorkflowInput.model_validate(state.workflow_input or {})
            if inp.eval_mode.value == "sequential" and moderation_report.result != "PASS":
                bundle = QualityAndSchemaBundle(
                    result="FAIL",
                    quality_report=QualityReport(result="SKIPPED"),
                    schema_report=SchemaReport(result="SKIPPED"),
                    skipped_due_to="moderation_failed",
                )
                async with ctx.store.edit_state() as s:
                    s.quality_bundle = bundle
                _log.info("[%s] Sequential mode — quality eval skipped due to moderation failure", run_id[:8])
                return QualityEvaluated(bundle=bundle)

            llm_quality = await run_quality_with_llm(article_md, article_json)
            schema = validate_article_schema(article_json)

            structural = run_moderation_checks(article_json)
            if structural.violations:
                from .models import SchemaFailure
                for v in structural.violations:
                    schema.failures.append(SchemaFailure(path=f"$.structural.{v.check_id}", message=v.message))
                if schema.result == "PASS":
                    schema.result = "FAIL"
                _log.warning(
                    "[%s] Structural moderation failures: %s",
                    run_id[:8],
                    "; ".join(f"{v.check_id}: {v.message}" for v in structural.violations),
                )

            quality_bundle = QualityAndSchemaBundle(
                result="PASS" if (llm_quality.result == "PASS" and schema.result == "PASS") else "FAIL",
                quality_report=llm_quality,
                schema_report=schema,
            )
            async with ctx.store.edit_state() as s:
                s.quality_bundle = quality_bundle

            if quality_bundle.result != "PASS":
                _log.warning(
                    "[%s] Quality bundle FAIL — quality=%s (avg=%.2f, min=%.2f, dims=%s), schema=%s (failures=%s)",
                    run_id[:8],
                    llm_quality.result, llm_quality.avg, llm_quality.min_dimension,
                    llm_quality.dimensions,
                    schema.result,
                    "; ".join(f"{f.path}: {f.message}" for f in schema.failures) or "none",
                )
            else:
                _log.info("[%s] Quality bundle PASS — quality avg=%.2f, schema=PASS", run_id[:8], llm_quality.avg)

            return QualityEvaluated(bundle=quality_bundle)
        except Exception as e:
            finished_at = _now_iso()
            duration_ms = int((time.time() - started) * 1000)
            err = WorkflowError(
                failure_reason=FailureReason.RUNTIME_ERROR,
                error_node=node_id,
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
            )
            summary = f"Moderation eval runtime error: {type(e).__name__}: {e}"
            await _append_trace(
                ctx,
                node_id=node_id,
                node_name=node_name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                result="ERROR",
                output_summary=summary,
                tokens_used=None,
            )
            _log.error("[%s] %s %s ERROR — %s", run_id[:8], node_id, node_name, summary, exc_info=True)
            return WorkflowFailed(error=err)

    @step
    async def n6_eval_merge(
        self, ctx: Context[RunState], ev: QualityEvaluated
    ) -> EvalMerged | WorkflowFailed:
        node_id, node_name = "N6", "EVAL_MERGE"
        started = time.time()
        started_at = _now_iso()
        state = await ctx.store.get_state()
        run_id = state.run_id

        try:
            inp = WorkflowInput.model_validate(state.workflow_input or {})
            moderation_report = state.moderation_report or ModerationReport(
                result="FAIL",
                checks=[],
                violations=[],
            )
            merged = merge_and_route(
                moderation_report=moderation_report,
                quality_bundle=ev.bundle,
                refine_attempts=state.refine_attempts,
                max_refine_attempts=inp.max_refine_attempts,
            )
            async with ctx.store.edit_state() as s:
                s.merged_eval = merged

            finished_at = _now_iso()
            duration_ms = int((time.time() - started) * 1000)
            result = "PASS" if merged.decision == EvalDecision.PROCEED else "FAIL"

            summary = (
                f"Decision: {merged.decision.value} "
                f"(moderation={moderation_report.result}, "
                f"quality={ev.bundle.quality_report.result}, "
                f"schema={ev.bundle.schema_report.result}, "
                f"refine_attempts={state.refine_attempts}/{inp.max_refine_attempts})"
            )
            await _append_trace(
                ctx,
                node_id=node_id,
                node_name=node_name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                result=result,
                output_summary=summary,
                tokens_used=None,
            )

            if merged.decision == EvalDecision.PROCEED:
                _log.info("[%s] %s %s — %s", run_id[:8], node_id, node_name, summary)
            elif merged.decision == EvalDecision.REFINE:
                _log.warning("[%s] %s %s — %s", run_id[:8], node_id, node_name, summary)
            else:
                _log.error("[%s] %s %s — %s", run_id[:8], node_id, node_name, summary)

            return EvalMerged(report=merged)
        except Exception as e:
            finished_at = _now_iso()
            duration_ms = int((time.time() - started) * 1000)
            err = WorkflowError(
                failure_reason=FailureReason.RUNTIME_ERROR,
                error_node=node_id,
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
            )
            summary = f"Eval merge runtime error: {type(e).__name__}: {e}"
            await _append_trace(
                ctx,
                node_id=node_id,
                node_name=node_name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                result="ERROR",
                output_summary=summary,
                tokens_used=None,
            )
            _log.error("[%s] %s %s ERROR — %s", run_id[:8], node_id, node_name, summary, exc_info=True)
            return WorkflowFailed(error=err)

    @step
    async def n7_refiner(
        self, ctx: Context[RunState], ev: EvalMerged
    ) -> RefinementDirectivesBuilt | WorkflowFailed | WorkflowSucceeded:
        node_id, node_name = "N7", "REFINER"
        started = time.time()
        started_at = _now_iso()
        state = await ctx.store.get_state()
        run_id = state.run_id

        try:
            if ev.report.decision == EvalDecision.PROCEED:
                finished_at = _now_iso()
                duration_ms = int((time.time() - started) * 1000)
                summary = "All evals passed — proceeding to final validation"
                await _append_trace(
                    ctx,
                    node_id=node_id,
                    node_name=node_name,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                    result="PASS",
                    output_summary=summary,
                    tokens_used=None,
                )
                _log.info("[%s] %s %s PASS — %s", run_id[:8], node_id, node_name, summary)
                article_md = state.last_article_md or ""
                article_json = state.last_article_json or {}
                return WorkflowSucceeded(article_md=article_md, article_json=article_json, merged_report=ev.report)

            if ev.report.decision == EvalDecision.FAIL:
                finished_at = _now_iso()
                duration_ms = int((time.time() - started) * 1000)

                mod_violations = "; ".join(
                    f"{v.check_id}: {v.message}" for v in ev.report.moderation.violations
                ) or "none"
                qual_detail = (
                    f"quality={ev.report.quality.quality_report.result} "
                    f"(avg={ev.report.quality.quality_report.avg:.2f}), "
                    f"schema={ev.report.quality.schema_report.result}"
                )
                schema_failures = "; ".join(
                    f"{f.path}: {f.message}" for f in ev.report.quality.schema_report.failures
                ) or "none"

                summary = (
                    f"Evaluation criteria not met after max refine attempts. "
                    f"moderation_violations=[{mod_violations}], "
                    f"{qual_detail}, schema_failures=[{schema_failures}]"
                )
                await _append_trace(
                    ctx,
                    node_id=node_id,
                    node_name=node_name,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                    result="FAIL",
                    output_summary=summary,
                    tokens_used=None,
                )
                _log.error("[%s] %s %s FAIL — %s", run_id[:8], node_id, node_name, summary)

                err = WorkflowError(
                    failure_reason=FailureReason.EVALUATION_CRITERIA_NOT_MET,
                    error_node=node_id,
                    error_type="EvalCriteriaNotMet",
                    error_message=summary,
                    stack_trace=None,
                )
                return WorkflowFailed(error=err)

            directives = build_refinement_directives(ev.report)
            async with ctx.store.edit_state() as s:
                s.refinement_directives = directives
                s.refine_attempts += 1

            finished_at = _now_iso()
            duration_ms = int((time.time() - started) * 1000)
            summary = f"Built directives ({directives.regeneration_mode.value}), refine_attempt={state.refine_attempts + 1}"
            await _append_trace(
                ctx,
                node_id=node_id,
                node_name=node_name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                result="PASS",
                output_summary=summary,
                tokens_used=None,
            )
            _log.info("[%s] %s %s — %s", run_id[:8], node_id, node_name, summary)
            return RefinementDirectivesBuilt(directives=directives)
        except Exception as e:
            finished_at = _now_iso()
            duration_ms = int((time.time() - started) * 1000)
            err = WorkflowError(
                failure_reason=FailureReason.RUNTIME_ERROR,
                error_node=node_id,
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
            )
            summary = f"Refiner runtime error: {type(e).__name__}: {e}"
            await _append_trace(
                ctx,
                node_id=node_id,
                node_name=node_name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                result="ERROR",
                output_summary=summary,
                tokens_used=None,
            )
            _log.error("[%s] %s %s ERROR — %s", run_id[:8], node_id, node_name, summary, exc_info=True)
            return WorkflowFailed(error=err)

    @step
    async def n8_regeneration(
        self, ctx: Context[RunState], ev: RefinementDirectivesBuilt
    ) -> GeneratedContent | WorkflowFailed:
        return await self._do_content_generation(ctx, ev)

    @step
    async def n9_final_validation(
        self, ctx: Context[RunState], ev: WorkflowSucceeded | WorkflowFailed
    ) -> StopEvent:
        node_id, node_name = "N9", "FINAL_VALIDATION"
        started = time.time()
        started_at = _now_iso()
        state = await ctx.store.get_state()
        run_id = state.run_id

        if isinstance(ev, WorkflowFailed):
            _log.error(
                "[%s] %s %s — workflow failed upstream: reason=%s node=%s error=%s",
                run_id[:8], node_id, node_name,
                ev.error.failure_reason.value if ev.error else "?",
                ev.error.error_node if ev.error else "?",
                ev.error.error_message[:500] if ev.error and ev.error.error_message else "?",
            )
            trace = await _get_trace(ctx)
            out = WorkflowOutput(
                article_md=state.last_article_md or "",
                article_json=state.last_article_json or {},
                status="FAILED_WITH_REASON",
                run_id=state.run_id,
                execution_trace=trace,
                error=ev.error,
            )
            return StopEvent(result=out.model_dump())

        try:
            report = final_validate(ev.article_md, ev.article_json)
            finished_at = _now_iso()
            duration_ms = int((time.time() - started) * 1000)
            result = "PASS" if report["result"] == "PASS" else "FAIL"

            summary = "Output integrity verified" if result == "PASS" else f"Final validation failed: {report}"
            await _append_trace(
                ctx,
                node_id=node_id,
                node_name=node_name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                result=result,
                output_summary=summary,
                tokens_used=None,
            )

            trace = await _get_trace(ctx)
            if result == "PASS":
                _log.info("[%s] %s %s PASS — GENERATED successfully", run_id[:8], node_id, node_name)
                out = WorkflowOutput(
                    article_md=ev.article_md,
                    article_json=ev.article_json,
                    status="GENERATED",
                    run_id=state.run_id,
                    execution_trace=trace,
                    error=None,
                )
                return StopEvent(result=out.model_dump())

            _log.error("[%s] %s %s FAIL — %s", run_id[:8], node_id, node_name, summary)
            err = WorkflowError(
                failure_reason=FailureReason.FINAL_VALIDATION_FAILED,
                error_node=node_id,
                error_type="FinalValidationFailed",
                error_message=str(report),
                stack_trace=None,
            )
            out = WorkflowOutput(
                article_md=ev.article_md,
                article_json=ev.article_json,
                status="FAILED_WITH_REASON",
                run_id=state.run_id,
                execution_trace=trace,
                error=err,
            )
            return StopEvent(result=out.model_dump())
        except Exception as e:
            summary = f"Final validation runtime error: {type(e).__name__}: {e}"
            _log.error("[%s] %s %s ERROR — %s", run_id[:8], node_id, node_name, summary, exc_info=True)
            err = WorkflowError(
                failure_reason=FailureReason.RUNTIME_ERROR,
                error_node=node_id,
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
            )
            trace = await _get_trace(ctx)
            out = WorkflowOutput(
                article_md=state.last_article_md or "",
                article_json=state.last_article_json or {},
                status="FAILED_WITH_REASON",
                run_id=state.run_id,
                execution_trace=trace,
                error=err,
            )
            return StopEvent(result=out.model_dump())
