# Workflow Technical Low-Level Design (TLD)
## Content Generation Agentic Workflow — Runtime Implementation Guide
### Version 1.0 · March 2026

---

## 1. DOCUMENT PURPOSE

This is the Technical Low-Level Design document for the content generation
agentic workflow. It bridges the gap between the framework-agnostic HLD and
a concrete runtime implementation.

**This document is runtime-generic.** It defines the implementation patterns,
interfaces, and contracts that ANY runtime must implement. Runtime-specific
sections are marked with `[RUNTIME: TBD]` placeholders to be filled when
a target framework is selected.

**Companion documents:**
- Agent Workflow Spec (`/workflow/specs/agent_workflow_spec.md`) — the contract
- Workflow HLD (`/workflow/design/workflow_hld.md`) — architecture
- Data Model Spec (`/workflow/specs/workflow_data_model_spec.md`) — persistence

---

## 2. IMPLEMENTATION ARCHITECTURE

### 2.1 Layer Decomposition

```
┌───────────────────────────────────────────┐
│  Layer 1: INTERFACE LAYER                  │
│  (API endpoint, CLI handler, SDK entry)    │
│  Accepts workflow_input, returns output    │
└───────────────────────┬───────────────────┘
                        │
┌───────────────────────▼───────────────────┐
│  Layer 2: ORCHESTRATION LAYER              │
│  (Workflow engine / state machine)          │
│  Owns: sequencing, routing, loop control   │
└───────────────────────┬───────────────────┘
                        │
┌───────────────────────▼───────────────────┐
│  Layer 3: STAGE LAYER                      │
│  (Individual stage implementations)         │
│  Each stage: pure function(input) → output │
└───────────────────────┬───────────────────┘
                        │
┌───────────────────────▼───────────────────┐
│  Layer 4: PROVIDER LAYER                   │
│  (LLM provider, tool integrations)          │
│  Abstracts: model calls, web search, etc.  │
└───────────────────────┬───────────────────┘
                        │
┌───────────────────────▼───────────────────┐
│  Layer 5: PERSISTENCE LAYER                │
│  (Workflow + execution data storage)        │
│  Abstracts: database, file system, cloud   │
└───────────────────────────────────────────┘
```

---

## 3. INTERFACE DEFINITIONS

### 3.1 Stage Interface (all stages implement this)

```
Interface: WorkflowStage

Properties:
  stage_id: string            // unique identifier, matches node ID from spec
  stage_name: string          // human-readable name
  stage_type: enum            // "gate" | "processor" | "evaluator" | "router" | "terminal"

Methods:
  execute(input: StageInput) → StageOutput
    // Synchronous or async depending on runtime
    // MUST NOT have side effects beyond its output
    // MUST NOT read global/shared state
    // MAY call LLM provider through provider layer

  validate_input(input: StageInput) → ValidationResult
    // Pre-execution input validation
    // Returns errors without executing

Types:
  StageInput:
    payload: object           // stage-specific input data
    context: ExecutionContext  // workflow-level context (run_id, runtime settings, etc.)

  StageOutput:
    result: "PASS" | "FAIL" | "SKIPPED"
    payload: object           // stage-specific output data
    execution_record: StageExecutionRecord

  StageExecutionRecord:
    stage_id: string
    started_at: ISO8601
    finished_at: ISO8601
    duration_ms: integer
    result: string
    output_summary: string
    error: ErrorInfo | null
```

### 3.2 Orchestrator Interface

```
Interface: WorkflowOrchestrator

Methods:
  run(input: WorkflowInput, runtime_settings: RuntimeSettings) → WorkflowOutput
    // Entry point — executes the full workflow
    // Returns terminal output (success or failure)
    // Handles all internal routing and loop control

  get_status(run_id: string) → RunStatus
    // Returns current status of an in-progress or completed run

Internal state (per run):
  run_id: string
  current_node: string
  refine_attempts: integer
  execution_trace: [StageExecutionRecord]
  started_at: ISO8601
```

### 3.3 Provider Interface

```
Interface: LLMProvider

Methods:
  generate(prompt: string, config: ProviderConfig) → LLMResponse
    // Single LLM call
    // Returns structured response + token usage

  generate_structured(prompt: string, schema: object, config: ProviderConfig) → StructuredResponse
    // LLM call with structured output / JSON mode
    // Returns parsed object conforming to schema

Types:
  ProviderConfig:
    model: string             // model identifier
    temperature: float        // 0.0–1.0
    max_tokens: integer
    timeout_ms: integer

  LLMResponse:
    content: string
    tokens_used: { input: integer, output: integer, total: integer }
    model: string
    latency_ms: integer

  StructuredResponse extends LLMResponse:
    parsed: object            // parsed JSON output
```

### 3.4 Persistence Interface

```
Interface: WorkflowPersistence

Methods:
  save_workflow(workflow: WorkflowDefinition) → void
  get_workflow(workflow_id: string) → WorkflowDefinition | null
  list_workflows(filter: WorkflowFilter) → [WorkflowDefinition]
  deactivate_workflow(workflow_id: string) → void  // soft delete

  save_execution(execution: WorkflowExecution) → void
  get_execution(run_id: string) → WorkflowExecution | null
  list_executions(filter: ExecutionFilter) → [WorkflowExecution]
```

---

## 4. STAGE IMPLEMENTATION DETAILS

### 4.1 N1 — Input Validator

```
Implementation type: Pure function (no LLM calls)

Logic:
  1. Parse raw input as JSON
  2. Check required fields: topic, sub_topic, content_variant
  3. Validate types and constraints:
     - topic: string, 1–100 chars
     - sub_topic: string, 1–200 chars
     - content_variant: exact match against enum set
  4. Reject unknown fields (strict mode)
  5. Return validated input or structured errors

Dependencies: None
LLM calls: 0
Expected latency: < 10ms
```

### 4.2 N2 / N8 — Content Generator

```
Implementation type: LLM-calling processor

Logic:
  1. Build generation prompt from:
     - Validated input (topic, sub_topic, content_variant)
     - Content Generation skill instructions
     - Refinement context (if refine pass)
  2. Issue LLM call with structured output mode
  3. Parse response into article_md + article_json
  4. Validate basic output structure (non-empty, parseable)
  5. Return structured output

Dependencies: LLM Provider, Content Gen Skill spec
LLM calls: 1–2 (depending on structured output support)
Expected latency: 30–90 seconds
Token estimate: 3000–8000 input, 2000–5000 output

Prompt construction:
  [RUNTIME: TBD — prompt template format depends on provider]

  Base prompt includes:
  - System instructions from content_gen_spec
  - Narration flow rules from narration_flow_spec
  - JSON schema requirements from json_schema_spec
  - Input parameters (topic, sub_topic, content_variant)
  - Refinement directives (if applicable)
```

### 4.3 N4 — Moderation Evaluator

```
Implementation type: Hybrid (rule-based + LLM-based checks)

Logic:
  Structural guard checks:
  - No deep dives in main intro section
  - No missing required deep dives in sections/posts
  - No prose-only blobs when content tree requires bullets/sub-sections

  Checks 1–3, 7–10: Rule-based (regex, field checks, enum validation)
  Checks 4–6: LLM-based (controversy detection, bias scan, humour eval)
  Policy checks: configurable guard-rail JSON + configurable deny-list topics

  1. Run all rule-based checks first (fast, deterministic)
  2. If any rule-based check fails: short-circuit, skip LLM checks
  3. Run LLM-based checks
  4. Aggregate all results

Dependencies: LLM Provider (for checks 4–6), Content Moderation Skill spec
LLM calls: 0–1 (0 if rule-based checks fail first)
Expected latency: 5–30 seconds
```

### 4.4 N5 — Quality Evaluator

```
Implementation type: Hybrid (LLM-based scoring + rule-based schema validation)

Sub-evaluation 1: Creativity & Narration (LLM-based)
  1. Build evaluation prompt with article content
  2. Issue LLM call requesting scores for 8 dimensions
  3. Parse dimension scores and notes
  4. Calculate overall average
  5. Determine PASS/REVISION_RECOMMENDED

Sub-evaluation 2: Schema Validation (rule-based)
  1. Walk JSON structure against all 15 validation blocks
  2. Check every rule deterministically
  3. Collect all failures (do not stop at first)
  4. Determine PASS/FAIL

  These two sub-evaluations MAY run in parallel within this stage.

Mandatory composition checks in this stage:
  - No deep dives in main intro section
  - No missing required deep dives in sections/posts
  - No prose-only blobs when content tree requires bullets/sub-sections
  - Nomenclature integrity (Article=Page, Section=Post, Deep Dive as child only)
  - Composability integrity (sections independently renderable)

Dependencies: LLM Provider, Creativity Skill spec, Schema Validation Skill spec
LLM calls: 1 (for creativity evaluation)
Expected latency: 10–40 seconds
```

### 4.5 N7 — Refiner

```
Implementation type: LLM-based analysis

Logic:
  1. Receive eval results from both passes
  2. Build analysis prompt:
     - Previous article content
     - Moderation violations (if any)
     - Quality dimension scores and notes
     - Schema validation failures
  3. Issue LLM call to produce structured refinement directives
  4. Determine regeneration strategy:
     - Any moderation violation → FULL
     - Quality/structural only → TARGETED
  5. Return refinement directive

Dependencies: LLM Provider
LLM calls: 1
Expected latency: 10–30 seconds
```

---

## 5. ORCHESTRATOR STATE MACHINE

```
States:
  INITIALIZED    → run created, not yet started
  VALIDATING     → input validation in progress
  GENERATING     → content generation in progress
  EVALUATING     → evaluation passes in progress
  REFINING       → refine pass in progress
  REGENERATING   → refined content generation in progress
  FINALIZING     → final validation in progress
  COMPLETED      → terminal state (success)
  FAILED         → terminal state (failure)

Transitions:
  INITIALIZED    → VALIDATING       (always)
  VALIDATING     → GENERATING       (input valid)
  VALIDATING     → FAILED           (input invalid)
  GENERATING     → EVALUATING       (generation complete)
  GENERATING     → FAILED           (runtime error)
  EVALUATING     → FINALIZING       (both evals pass)
  EVALUATING     → REFINING         (any eval fail, attempts < max)
  EVALUATING     → FAILED           (any eval fail, attempts >= max)
  REFINING       → REGENERATING     (directives produced)
  REFINING       → FAILED           (runtime error)
  REGENERATING   → EVALUATING       (regeneration complete)
  REGENERATING   → FAILED           (runtime error)
  FINALIZING     → COMPLETED        (output valid)
  FINALIZING     → FAILED           (output invalid)

Terminal states: COMPLETED, FAILED
```

---

## 6. ERROR HANDLING IMPLEMENTATION

### 6.1 Per-Stage Error Wrapping

Every stage execution is wrapped in a try/catch at the orchestrator level:

```
Pseudocode:

function execute_stage(stage, input):
  record = new StageExecutionRecord(stage.stage_id, now())
  try:
    output = stage.execute(input)
    record.finish(now(), output.result)
    return output
  catch TimeoutError:
    record.finish(now(), "TIMEOUT")
    return fail_output("TIMEOUT", stage.stage_id, error)
  catch Error as e:
    record.finish(now(), "ERROR")
    return fail_output("RUNTIME_ERROR", stage.stage_id, e)
  finally:
    execution_trace.append(record)
```

### 6.2 Timeout Strategy

| Level | Timeout | Action on Breach |
|---|---|---|
| Per-stage | `timeout_per_stage_ms` (default 120s) | Kill stage, record timeout, route to T_FAIL_RUNTIME |
| Per-workflow | `timeout_total_workflow_ms` (default 600s) | Kill active stage, produce failure output |
| LLM call | Provider-level timeout | Propagated as stage timeout |

---

## 7. TOKEN TRACKING

Token consumption is tracked at two levels:

### 7.1 Per-LLM-Call
Each call through the provider layer returns `tokens_used: { input, output, total }`.

### 7.2 Per-Workflow-Run
The orchestrator aggregates all LLM call tokens into a workflow-level total:

```
workflow_tokens = {
  total: sum(all_calls.total),
  breakdown: {
    generation: sum(generation_calls.total),
    evaluation: sum(eval_calls.total),
    refinement: sum(refine_calls.total)
  }
}
```

This total is stored in the workflow execution record.

---

## 8. RUNTIME SETTINGS RESOLUTION

Runtime settings are resolved in this priority order (highest to lowest):

1. **Per-run overrides** — `workflow_input.runtime_overrides`
2. **Provider config** — `provider_config.json` in project root
3. **Defaults** — hardcoded defaults from Agent Workflow Spec

```
Pseudocode:

function resolve_runtime_settings(run_overrides, provider_config):
  settings = DEFAULT_SETTINGS
  settings.merge(provider_config)
  settings.merge(run_overrides)
  return settings
```

---

## 9. PROVIDER ABSTRACTION

### 9.1 Provider Config File

```json
{
  "provider_name": "[RUNTIME: TBD]",
  "provider_type": "llm",
  "model": "[RUNTIME: TBD]",
  "api_base": "[RUNTIME: TBD]",
  "temperature": 0.7,
  "max_tokens": 8192,
  "timeout_ms": 120000,
  "supports_structured_output": true,
  "supports_parallel_calls": true
}
```

### 9.2 Provider Selection

The workflow reads provider configuration from a `provider_config.json` file.
The `provider_name` from this config is recorded in the workflow execution record
for traceability.

[RUNTIME: TBD — Provider initialization and authentication mechanism depends
on the selected framework and LLM provider.]

---

## 10. RUNTIME-SPECIFIC SECTIONS

The following sections are placeholders. Each is filled when a target runtime
is selected for implementation.

### 10.1 Framework Selection
```
[RUNTIME: TBD]
Options under consideration:
- LangGraph (Python)
- Claude Agent SDK (Python/TypeScript)
- CrewAI (Python)
- Custom orchestrator (any language)
- Temporal / Inngest (durable execution)
```

### 10.2 Deployment Model
```
[RUNTIME: TBD]
Options:
- Serverless function (AWS Lambda, Cloud Functions)
- Long-running service (container, VM)
- CLI tool (local execution)
- Hybrid (orchestrator as service, stages as functions)
```

### 10.3 Persistence Implementation
```
[RUNTIME: TBD]
Options:
- PostgreSQL (structured data)
- SQLite (local / embedded)
- DynamoDB / Firestore (serverless)
- File system (JSON files, development only)
```

### 10.4 Observability Stack
```
[RUNTIME: TBD]
Options:
- Structured logging (JSON logs)
- OpenTelemetry tracing
- Custom dashboard
- Provider-native observability (e.g., LangSmith)
```

---

## 11. TESTING STRATEGY

### 11.1 Unit Tests (per stage)

Each stage must have unit tests that verify:
- Valid input → expected output
- Invalid input → expected error
- Edge cases (empty strings, boundary values, null refinement context)

### 11.2 Integration Tests (stage chains)

Test stage-to-stage data flow:
- N1 → N2: validated input flows correctly to generator
- N2 → N4/N5: generated content flows to evaluators
- N6 → N7 → N8: refine loop round-trip

### 11.3 End-to-End Tests

Test complete workflow paths:
- Happy path (no refinement needed)
- One refinement loop
- Input validation failure
- Eval failure after max retries
- Timeout handling

### 11.4 Mock Strategy

- LLM calls: mock with recorded responses for deterministic testing
- Provider layer: mockable interface for all tests except E2E
- Persistence: in-memory implementation for tests

---

## 12. IMPLEMENTATION CHECKLIST

When implementing against this TLD, ensure:

- [ ] All 5 layers implemented (interface, orchestration, stage, provider, persistence)
- [ ] All stage interfaces conform to Section 3.1
- [ ] State machine transitions match Section 5
- [ ] Error wrapping follows Section 6.1 pattern
- [ ] Timeouts implemented at both stage and workflow level
- [ ] Token tracking aggregated per Section 7
- [ ] Configuration resolution follows priority order in Section 8
- [ ] Provider config externalized per Section 9
- [ ] All [RUNTIME: TBD] sections filled for chosen runtime
- [ ] Test coverage per Section 11
