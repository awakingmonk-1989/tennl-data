# Workflow Data Model Spec
## Content Generation Agentic Workflow — Data Persistence
### Version 1.0 · March 2026

---

## 1. PURPOSE

This spec defines the data models for persisting workflow definitions and
workflow execution records. Any persistence implementation (SQL, NoSQL,
file-based) MUST conform to these schemas.

**Two core entities:**
1. **Workflow** — the definition of a workflow (metadata, versioning)
2. **Workflow Execution** — one run of a workflow (input/output refs, trace, status)

**Primary DB policy (critical):** Do not flood primary DB tables with lengthy
descriptive metadata or runtime payloads. Large payloads belong in cold storage.

---

## 2. ENTITY: WORKFLOW

The workflow entity represents a workflow definition — not an execution.
There is currently one workflow type (content generation), but the model
supports multiple workflow types.

### 2.1 Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `workflow_id` | string (UUID) | yes | Unique identifier for this workflow definition |
| `name` | string | yes | Human-readable name (e.g., "content_generation_v1") |
| `description` | string | no | Brief description of what the workflow does |
| `version` | string (semver) | yes | Semantic version of this workflow definition |
| `created_ts` | ISO8601 datetime | yes | When this workflow definition was created |
| `updated_ts` | ISO8601 datetime | yes | When this workflow definition was last updated |
| `is_active` | boolean | yes | Soft delete flag. `false` = logically deleted, retained for audit |
| `tags` | array[string] | no | Freeform tags for filtering/grouping |

### 2.2 Constraints

- `workflow_id` is globally unique and immutable once created
- `version` follows semver format: `MAJOR.MINOR.PATCH`
- `updated_ts` >= `created_ts`
- `is_active` defaults to `true` on creation
- When `is_active` is set to `false`, the record is NEVER hard-deleted
- Multiple versions of the same logical workflow are stored as separate records
  with different `workflow_id` and `version` values but the same `name`

### 2.3 Example

```json
{
  "workflow_id": "wf_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "content_generation_v1",
  "description": "Agentic content generation workflow with 2 eval passes and 1 refine loop",
  "version": "1.0.0",
  "created_ts": "2026-03-31T10:00:00Z",
  "updated_ts": "2026-03-31T10:00:00Z",
  "is_active": true,
  "tags": ["content", "generation", "v1"]
}
```

**TODO (future enhancement):** If workflow definition metadata such as config
snapshots or node graph exports must be retained, store them in cold storage and
persist only a pointer/reference. Do not store large workflow metadata in the
primary `workflow` table.

---

## 3. ENTITY: WORKFLOW EXECUTION

The workflow execution entity represents one complete run of a workflow.
Created when a run starts, updated when it finishes.

### 3.1 Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `run_id` | string (UUID) | yes | Unique identifier for this execution run |
| `workflow_id` | string (UUID) | yes | FK to the workflow definition that was executed |
| `workflow_name` | string | yes | Denormalized workflow name (for convenience in queries/display) |
| `status` | enum | yes | `"RUNNING"`, `"SUCCESS"`, `"FAILED"` |
| `created_ts` | ISO8601 datetime | yes | When the run was initiated |
| `finished_ts` | ISO8601 datetime | conditional | When the run completed (null while RUNNING) |
| `execution_time_ms` | integer | conditional | Total wall-clock duration in ms (null while RUNNING) |
| `inputs_ref` | string | yes | Cold storage reference for workflow input payload |
| `output_ref` | string | conditional | Cold storage reference for workflow output payload |
| `provider_name` | string | yes | Name of the LLM provider used (from provider config) |
| `tokens` | integer | conditional | Total tokens consumed across all LLM calls in this run |
| `error` | object (JSON) | conditional | Error details if status is FAILED |
| `execution_trace` | array[object] | no | Ordered list of stage execution records |

### 3.2 Constraints

- `run_id` is globally unique and immutable once created
- `workflow_id` must reference an existing workflow (active or inactive)
- `status` transitions: `RUNNING → SUCCESS` or `RUNNING → FAILED` (one-way, no rollback)
- `finished_ts` MUST be non-null when `status` is `SUCCESS` or `FAILED`
- `finished_ts` MUST be null when `status` is `RUNNING`
- `execution_time_ms` = `finished_ts - created_ts` (computed on completion)
- `inputs_ref` is immutable after creation — never modified during or after the run
- `output_ref` is set exactly once when the run completes
- `tokens` is the aggregate total; per-stage breakdown is in `execution_trace`
- `provider_name` is read from provider config at run start and stored for audit

Cold storage policy:
- Full workflow inputs/outputs should not be stored inline in primary DB rows.
- Primary DB stores references (`inputs_ref`, `output_ref`) to cold storage objects.
- TODO: Inline input/output persistence, if still present in current implementations,
  must be migrated to cold storage within the next 1–2 releases.

### 3.3 Status Enum

| Value | Meaning |
|---|---|
| `RUNNING` | Workflow is currently executing |
| `SUCCESS` | Workflow completed successfully, `output_ref` points to article payload |
| `FAILED` | Workflow terminated with a failure |

### 3.4 Error Object Schema (when status = FAILED)

```json
{
  "failure_reason": "INPUT_VALIDATION_FAILED | EVALUATION_CRITERIA_NOT_MET | FINAL_VALIDATION_FAILED | RUNTIME_ERROR",
  "error_node": "string — node ID where failure occurred",
  "error_type": "string — error class/type name",
  "error_message": "string — human-readable error description",
  "stack_trace": "string | null"
}
```

### 3.5 Execution Trace Entry Schema

```json
{
  "node_id": "string",
  "node_name": "string",
  "started_at": "ISO8601",
  "finished_at": "ISO8601",
  "duration_ms": "integer",
  "result": "PASS | FAIL | SKIPPED | ERROR | TIMEOUT",
  "output_summary": "string — brief description of what the stage produced",
  "tokens_used": "integer | null"
}
```

### 3.6 Example

```json
{
  "run_id": "run_f1e2d3c4-b5a6-7890-fedc-ba0987654321",
  "workflow_id": "wf_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "workflow_name": "content_generation_v1",
  "status": "SUCCESS",
  "created_ts": "2026-03-31T14:00:00Z",
  "finished_ts": "2026-03-31T14:02:35Z",
  "execution_time_ms": 155000,
  "inputs_ref": "cold://workflow-inputs/run_f1e2d3c4-b5a6-7890-fedc-ba0987654321.json",
  "output_ref": "cold://workflow-outputs/run_f1e2d3c4-b5a6-7890-fedc-ba0987654321.json",
  "provider_name": "anthropic_claude_opus",
  "tokens": 18500,
  "error": null,
  "execution_trace": [
    {
      "node_id": "N1",
      "node_name": "INPUT_VALIDATION",
      "started_at": "2026-03-31T14:00:00.100Z",
      "finished_at": "2026-03-31T14:00:00.105Z",
      "duration_ms": 5,
      "result": "PASS",
      "output_summary": "Input validated: topic=Life Hacks, sub_topic=Focus & Attention",
      "tokens_used": null
    },
    {
      "node_id": "N2",
      "node_name": "CONTENT_GENERATION",
      "started_at": "2026-03-31T14:00:00.110Z",
      "finished_at": "2026-03-31T14:01:15.000Z",
      "duration_ms": 74890,
      "result": "PASS",
      "output_summary": "Generated article: 4 posts, 2 deep dives, 847 words",
      "tokens_used": 12000
    },
    {
      "node_id": "N4",
      "node_name": "EVAL_MODERATION",
      "started_at": "2026-03-31T14:01:15.100Z",
      "finished_at": "2026-03-31T14:01:35.000Z",
      "duration_ms": 19900,
      "result": "PASS",
      "output_summary": "All 10 checks passed, 0 violations",
      "tokens_used": 3000
    },
    {
      "node_id": "N5",
      "node_name": "EVAL_QUALITY",
      "started_at": "2026-03-31T14:01:35.100Z",
      "finished_at": "2026-03-31T14:02:30.000Z",
      "duration_ms": 54900,
      "result": "PASS",
      "output_summary": "Creativity avg 4.2/5, schema 0 failures",
      "tokens_used": 3500
    },
    {
      "node_id": "N9",
      "node_name": "FINAL_VALIDATION",
      "started_at": "2026-03-31T14:02:30.100Z",
      "finished_at": "2026-03-31T14:02:30.200Z",
      "duration_ms": 100,
      "result": "PASS",
      "output_summary": "Output integrity verified",
      "tokens_used": null
    }
  ]
}
```

---

## 4. PAYLOAD STORAGE POLICY

To keep primary DB rows small and query-efficient:
- Do not store verbose workflow metadata (`config`, `node_graph`) in workflow tables.
- Do not store full execution payloads (`inputs`, `output`) inline in execution rows.
- Store payloads in cold storage and persist only references in primary tables.

Recommended cold storage paths:
- `cold://workflow-inputs/{run_id}.json`
- `cold://workflow-outputs/{run_id}.json`
- `cold://workflow-metadata/{workflow_id}.json` (optional future use)

---

## 5. QUERY PATTERNS

Implementations SHOULD support these query patterns efficiently:

| Query | Fields Used | Purpose |
|---|---|---|
| Get workflow by ID | `workflow_id` | Load workflow definition |
| List active workflows | `is_active = true` | List available workflows |
| Get execution by run ID | `run_id` | Load specific run |
| List executions for workflow | `workflow_id`, `created_ts` | Run history for a workflow |
| List executions by status | `status`, `created_ts` | Find failed/running runs |
| List recent executions | `created_ts DESC` | Dashboard / monitoring |
| Get execution by workflow + latest | `workflow_id`, `created_ts DESC LIMIT 1` | Latest run |

---

## 6. RETENTION AND AUDIT

- Workflow definitions are NEVER hard-deleted. Use `is_active = false` for soft delete.
- Workflow executions are retained indefinitely for audit purposes.
- `inputs_ref` and `output_ref` provide reproducibility context via cold storage.
- `execution_trace` provides stage-by-stage audit trail.
- `provider_name` tracks which LLM provider was used for each run.
- `tokens` tracks resource consumption per run.

---

## 7. VERSIONING

| Field | Value |
|---|---|
| Spec version | 1.0 |
| Created | 2026-03-31 |
| Last updated | 2026-03-31 |
| Status | Active |
