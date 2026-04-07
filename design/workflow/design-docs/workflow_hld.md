# Workflow High-Level Design (HLD)
## Content Generation Agentic Workflow
### Version 1.0 · March 2026

---

## 1. DOCUMENT PURPOSE

This is the High-Level Design document for the content generation agentic
workflow. It describes the architecture, component boundaries, data flow,
and design decisions at a level sufficient for any engineering team to
understand the system before diving into runtime-specific implementation.

**Audience:** Engineers, architects, and agents translating this design
into runtime-specific implementations.

**Companion documents:**
- Agent Workflow Spec (`/design/workflow/specs/agent_workflow_spec.md`) — the contract
- Data Model Spec (`/design/workflow/specs/workflow_data_model_spec.md`) — persistence
- Flow Diagram (`/design/workflow/diagrams/content_gen_workflow_flow.md`) — visual

---

## 2. SYSTEM CONTEXT

```
┌──────────────────────────────────────────────────────────┐
│                    CALLER / TRIGGER                       │
│  (CLI, API endpoint, cron job, parent workflow, agent)    │
└──────────────────────┬───────────────────────────────────┘
                       │ workflow_input
                       ▼
┌──────────────────────────────────────────────────────────┐
│              WORKFLOW ORCHESTRATOR                         │
│                                                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │  INPUT   │→ │CONTENT  │→ │  EVAL   │→ │ OUTPUT  │    │
│  │VALIDATOR │  │GENERATOR│  │  GATE   │  │ GATE    │    │
│  └─────────┘  └─────────┘  └────┬────┘  └─────────┘    │
│                                  │                        │
│                    ┌─────────────┼─────────────┐          │
│                    ▼             │             ▼          │
│              ┌──────────┐       │       ┌──────────┐     │
│              │MODERATION│       │       │ QUALITY  │     │
│              │EVALUATOR │       │       │EVALUATOR │     │
│              └──────────┘       │       └──────────┘     │
│                                  │                        │
│                    ┌─────────────┘                        │
│                    ▼                                      │
│              ┌──────────┐                                │
│              │ REFINER  │ ← (max 1 loop)                 │
│              └──────────┘                                │
│                                                           │
│  ┌──────────────────────────────────────────────┐        │
│  │           EXECUTION TRACKER                    │        │
│  │  (traces, timing, token usage, run metadata)   │        │
│  └──────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────┘
                       │
                       ▼ workflow_output
┌──────────────────────────────────────────────────────────┐
│                    CONSUMER                                │
│  (storage, API response, downstream workflow, UI render)  │
└──────────────────────────────────────────────────────────┘
```

---

## 2A. NOMENCLATURE & COMPOSABILITY STRATEGY (NON-NEGOTIABLE)

- **Article = Page**: full composed content unit.
- **Section = Post**: section-level units are also independently renderable posts.
- **Deep Dive**: child content only under sections/posts.

This decomposition is intentional so the app can either:
- render full page/article, or
- render independent posts only.

Hard workflow rules:
- No deep dives in main intro section.
- No section/post missing required deep dives.
- No prose-only blob when content tree requires bullets/sub-sections.

---

## 3. ARCHITECTURAL PRINCIPLES

1. **Stage isolation** — Each stage is a self-contained unit with defined input/output
   contracts. No stage reads global state. All data flows through explicit parameters.

2. **Framework agnosticism** — The orchestrator is an abstract coordination layer.
   It does not depend on any specific LLM provider, orchestration framework, or
   programming language.

3. **Fail-fast, fail-loud** — Safety failures stop the pipeline immediately. Every
   failure produces a structured reason. No silent swallowing of errors.

4. **Bounded iteration** — The refine loop has a hard ceiling (`max_refine_attempts`).
   The system guarantees termination.

5. **Observability by default** — Every stage execution is traced with timestamps,
   duration, and result. Token consumption is tracked at workflow level.

6. **Separation of concerns:**
   - **Orchestrator** owns sequencing and routing
   - **Stages** own domain logic (generation, evaluation, refinement)
   - **Tracker** owns execution metadata and audit
   - **Data model** owns persistence

---

## 4. COMPONENT ARCHITECTURE

### 4.1 Workflow Orchestrator

**Responsibility:** Manage the lifecycle of a single workflow run.

**Capabilities:**
- Initialize workflow run with unique `run_id`
- Execute stages in defined order
- Handle stage routing (conditional edges, loops)
- Manage refine loop counter
- Dispatch parallel or sequential evaluation
- Collect execution traces from all stages
- Produce terminal output (success or failure)
- Handle timeouts and unhandled errors

**Does NOT:**
- Contain any content generation or evaluation logic
- Make LLM calls directly
- Persist data (delegates to data model layer)

### 4.2 Input Validator

**Responsibility:** Validate raw workflow input before any LLM invocation.

**Design decisions:**
- Runs synchronously, no LLM calls
- Strict schema validation — rejects unknown fields
- Returns structured error on validation failure
- Zero tolerance — any invalid field fails the entire input

### 4.3 Content Generator

**Responsibility:** Produce article markdown and JSON from validated input.

**Design decisions:**
- Encapsulates the Content Generation skill
- Accepts optional `refinement_context` for refine passes
- On first pass: `refinement_context` is null
- On refine pass: `refinement_context` contains directives from N7
- Tracks `attempt_number` for tracing
- Returns structured output — never raw LLM text

**LLM interaction:** This is the primary LLM-calling component. It issues one or
more LLM calls to produce the article. The exact call pattern depends on the
runtime and provider.

### 4.4 Evaluation Gate (Router)

**Responsibility:** Dispatch generated content to evaluation passes.

**Design decisions:**
- Stateless router — no logic beyond dispatch
- In parallel mode: fans out to both evaluators simultaneously
- In sequential mode: runs moderation first, quality second
- Fail-fast: in sequential mode, if moderation fails, quality is skipped

### 4.5 Moderation Evaluator (Eval Pass 1)

**Responsibility:** Safety and content moderation.

**Design decisions (strictly mandatory evaluator criteria):**
- Runs structural guard checks:
  - No deep dives in main intro section
  - Sections/posts missing deep dives are disallowed
  - No prose-only blobs: convert to bullet items or organized sub-sections
    per content tree when required
- Runs safety/guard-rail checks:
  - Hard safety flags
  - Topic exclusions
  - Deny-list topics (configurable in prompt)
  - Additional guard rails (configurable JSON policy shared as part of prompt)
  - Real person policy
  - Controversy check
  - Negativity & bias scan
  - Humour evaluation
  - Source exclusions
  - Copyright compliance
  - Image safety
  - JSON safety flags
- Binary result: PASS or FAIL (no partial pass)
- Any single violation = FAIL for the entire pass
- Returns structured check-by-check report
- May use LLM for nuanced checks (controversy, bias) or rule-based for structural checks

### 4.6 Quality Evaluator (Eval Pass 2)

**Responsibility:** Narrative quality + structural schema validation.

**Design decisions (strictly mandatory evaluator criteria):**
- Composed of two sub-evaluations:
  1. Creativity & Narration (LLM-based, scored 1–5 across 8 dimensions)
  2. Schema Validation (rule-based, deterministic)
- Enforces composition checks:
  - No deep dives in main intro section
  - Sections/posts missing deep dives are disallowed
  - No prose-only blobs: convert to bullet items or organized sub-sections
    per content tree when required
  - Nomenclature integrity: Article = Page (composition), Section = Post
  - Composability intent: sections must be independently renderable as posts
    while still composing into a full page/article
- Enforces Creativity & Narration checks:
  - Hook quality
  - Title quality
  - Three-beat structure
  - Sentence rhythm & voice
  - Content option visual rhythm
  - Deep dive quality
  - India warmth & specificity
  - Quick reference quality
- Enforces Schema Validation checks:
  - Root envelope
  - Word count meta
  - Hero, hook, sections
  - Body schemas per option
  - Deep dives, quick reference
  - Narrative metadata
  - Sources, images
- Both sub-evaluations must pass for the overall pass
- Creativity threshold: avg >= 3.5, all dimensions >= 3
- Schema threshold: zero failures
- Returns detailed scores and failure details for refinement

### 4.7 Evaluation Merger

**Responsibility:** Merge results from both eval passes and decide routing.

**Design decisions:**
- Stateless decision function
- Three possible outcomes: PROCEED, REFINE, FAIL
- Consults `refine_attempts` counter to decide REFINE vs FAIL
- Produces merged eval summary for tracing

### 4.8 Refiner

**Responsibility:** Analyse evaluation failures and produce refinement directives.

**Design decisions:**
- Does NOT regenerate content itself — produces directives for the generator
- Categorises failures: safety, quality, structural
- Determines regeneration strategy: FULL (safety violation) or TARGETED (quality/structural)
- Identifies elements from previous attempt to preserve (TARGETED mode only)
- Directives are structured data, not free-form text

### 4.9 Final Validator

**Responsibility:** Last integrity check before declaring success.

**Design decisions:**
- Lightweight, deterministic checks (no LLM calls)
- Validates output completeness and hard constraints
- Acts as a safety net for edge cases that might slip through eval passes

### 4.10 Execution Tracker

**Responsibility:** Record execution metadata for every stage.

**Design decisions:**
- Cross-cutting concern — every stage reports to the tracker
- Records: node_id, start_time, end_time, duration, result, output_summary
- Tracks total token consumption at workflow level
- Produces the `execution_trace` array in workflow output
- Non-blocking — tracker failures must not fail the workflow

---

## 5. DATA FLOW

### 5.1 Happy Path (No Refinement Needed)

```
Input → InputValidator → ContentGenerator → EvalGate
     → [ModerationEval ∥ QualityEval] → EvalMerger(PROCEED)
     → FinalValidator → Success Output
```

**Token budget estimate:** 1 generation call + 2 eval calls = ~3 LLM invocations

### 5.2 One Refinement Loop

```
Input → InputValidator → ContentGenerator → EvalGate
     → [ModerationEval ∥ QualityEval] → EvalMerger(REFINE)
     → Refiner → ContentGeneratorRefined → EvalGate
     → [ModerationEval ∥ QualityEval] → EvalMerger(PROCEED)
     → FinalValidator → Success Output
```

**Token budget estimate:** 2 generation calls + 4 eval calls + 1 refine call = ~7 LLM invocations

### 5.3 Failure After Max Retries

```
Input → InputValidator → ContentGenerator → EvalGate
     → [ModerationEval ∥ QualityEval] → EvalMerger(REFINE)
     → Refiner → ContentGeneratorRefined → EvalGate
     → [ModerationEval ∥ QualityEval] → EvalMerger(FAIL)
     → Failure Output
```

---

## 6. ERROR HANDLING STRATEGY

| Error Type | Handling | Terminal State |
|---|---|---|
| Invalid input | Reject at N1 with structured errors | T_FAIL_INPUT |
| LLM generation failure | Catch, wrap as runtime error | T_FAIL_RUNTIME |
| LLM timeout | Catch at orchestrator level per stage timeout | T_FAIL_RUNTIME |
| Moderation violation | Route through refine loop (bounded) | T_FAIL_EVAL if exhausted |
| Quality below threshold | Route through refine loop (bounded) | T_FAIL_EVAL if exhausted |
| Schema validation failure | Route through refine loop (bounded) | T_FAIL_EVAL if exhausted |
| Final validation failure | Direct terminal failure | T_FAIL_SCHEMA |
| Unhandled exception | Global catch, capture stack, route to T_FAIL_RUNTIME | T_FAIL_RUNTIME |
| Workflow timeout | Orchestrator-level timeout kills active stage | T_FAIL_RUNTIME |

---

## 7. CONCURRENCY MODEL

### 7.1 Within a Single Run

- **Eval passes** may run concurrently (N4 ∥ N5)
- All other stages are sequential
- No concurrent writes to workflow state — orchestrator owns state transitions

### 7.2 Across Runs

- Multiple workflow runs MAY execute concurrently
- Each run has its own isolated state (identified by `run_id`)
- No shared mutable state between runs
- Token/rate limits at the LLM provider level are the main concurrency constraint

---

## 8. OBSERVABILITY

### 8.1 Execution Trace

Every workflow run produces an `execution_trace` — an ordered array of stage
execution records. This enables:
- Performance profiling (which stages are slow)
- Debugging failures (which stage failed and why)
- Cost analysis (token usage per stage)

### 8.2 Workflow Execution Record

Every completed run (success or failure) produces a workflow execution record
with: `run_id`, `workflow_id`, timestamps, status, inputs, outputs, provider
info, and token consumption. See Data Model Spec for schema.

---

## 9. SECURITY CONSIDERATIONS

1. **Input sanitization** — N1 validates inputs strictly. No raw user input reaches LLM prompts without validation.
2. **No credential storage** — Workflow does not store API keys. Credentials are injected by the runtime environment.
3. **Output safety** — Content moderation (N4) runs on every generation pass, including refinements.
4. **Audit trail** — All workflow executions are recorded with full input/output for audit.
5. **Soft delete** — Workflow definitions use `is_active` flag, never hard delete, preserving audit history.

---

## 10. DESIGN DECISIONS LOG

| Decision | Rationale | Alternatives Considered |
|---|---|---|
| Max 1 refine attempt | Balance quality improvement with token cost; most failures are fixable in 1 pass | 0 (no refine), 2+ (diminishing returns, high cost) |
| Moderation before quality in sequential mode | Safety is non-negotiable; no point evaluating quality of unsafe content | Quality first (would waste tokens on unsafe content) |
| Refiner produces directives, not content | Separation of concerns; generator owns generation logic | Refiner patches content directly (harder to trace, breaks idempotency) |
| FULL regen on safety violation | Patching safety issues risks missing related violations | TARGETED regen (too risky for safety) |
| Execution trace in output | Enables debugging and cost analysis without external tooling | Separate logging system (adds infrastructure dependency) |
| Framework-agnostic design | Multiple runtime targets anticipated | Lock to one framework (limits portability) |
