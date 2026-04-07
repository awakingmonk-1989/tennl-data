# Workflow Data Model Design Document
## Content Generation Agentic Workflow — Persistence Design
### Version 1.0 · March 2026

---

## 1. DOCUMENT PURPOSE

This document provides the design-level view of the workflow data model.
It covers entity relationships, indexing strategy, storage considerations,
and implementation guidance for any persistence backend.

**Companion:** Workflow Data Model Spec (`/design/workflow/specs/workflow_data_model_spec.md`)
defines the authoritative schemas. This document explains the design rationale.

---

## 2. ENTITY RELATIONSHIP DIAGRAM

```
┌─────────────────────┐       1
│     WORKFLOW          │───────────┐
│─────────────────────│           │
│ workflow_id (PK)     │           │
│ name                 │           │
│ version              │           │  references
│ created_ts           │           │
│ updated_ts           │           │
│ is_active            │           │
│ tags (array)         │           │
└─────────────────────┘           │
                                   │ *
                        ┌──────────▼──────────┐
                        │ WORKFLOW_EXECUTION    │
                        │──────────────────────│
                        │ run_id (PK)           │
                        │ workflow_id (FK)       │
                        │ workflow_name          │
                        │ status                 │
                        │ created_ts             │
                        │ finished_ts            │
                        │ execution_time_ms      │
│ inputs_ref             │
│ output_ref             │
                        │ provider_name          │
                        │ tokens                 │
                        │ error (JSON)           │
                        │ execution_trace (JSON) │
                        └───────────────────────┘
```

**Relationship:** One workflow → many executions (1:N).

---

## 3. DESIGN DECISIONS

### 3.1 Denormalized `workflow_name` in Execution

**Decision:** Store `workflow_name` directly on the execution record even though
it can be derived by joining to the workflow table.

**Rationale:**
- Most queries display the workflow name alongside execution data
- Avoids a join on every execution list query
- Workflow name changes (via new version) should not retroactively change
  historical execution records — the name at execution time is the truth

### 3.2 JSON Columns for `error`, `execution_trace`

**Decision:** Store these as JSON/JSONB columns rather than normalized tables.

**Rationale:**
- These are run-local payloads read mostly as a unit
- No need to query individual fields within these objects (except for advanced analytics)
- Normalizing execution_trace entries into a separate table adds complexity
  without meaningful query benefit for the current use case
- JSON storage preserves exact structure without schema migration overhead

**Note:** Full workflow `inputs` and `output` payloads are intentionally not stored inline
in primary DB rows. They are persisted in cold storage and referenced by `inputs_ref` /
`output_ref` in `workflow_execution`.

### 3.3 Soft Delete via `is_active`

**Decision:** Never hard-delete workflow definitions. Use `is_active = false`.

**Rationale:**
- Workflow executions reference workflows by `workflow_id`
- Hard-deleting a workflow would orphan its execution history
- Audit requirements mandate retaining all definitions
- Inactive workflows can be filtered out in listing queries

### 3.4 No Separate Execution Trace Table

**Decision:** Embed `execution_trace` as a JSON array within the execution record.

**Rationale:**
- Execution trace entries are always read together with the parent execution
- No use case currently requires querying across trace entries of different runs
- If analytics on trace data becomes a requirement, a materialized view or
  separate analytics table can be added without changing the core model

**Future consideration:** If stage-level analytics become important (e.g.,
"average duration of N4 across all runs"), extract trace entries into a separate
table or analytics pipeline.

### 3.5 `tokens` as Single Integer

**Decision:** Store total token count as a single integer, not a breakdown.

**Rationale:**
- Per-stage token breakdown is available in `execution_trace[].tokens_used`
- The top-level `tokens` field serves as a quick cost indicator
- Detailed breakdown queries can sum from `execution_trace` if needed
- Keeps the execution record compact

---

## 4. INDEXING STRATEGY

### 4.1 Primary Keys

| Table | Primary Key |
|---|---|
| workflow | `workflow_id` |
| workflow_execution | `run_id` |

### 4.2 Recommended Indexes

| Table | Index | Columns | Purpose |
|---|---|---|---|
| workflow | `idx_workflow_active` | `is_active, name` | List active workflows |
| workflow | `idx_workflow_name_version` | `name, version` | Find specific version |
| workflow_execution | `idx_exec_workflow` | `workflow_id, created_ts DESC` | Run history per workflow |
| workflow_execution | `idx_exec_status` | `status, created_ts DESC` | Find failed/running runs |
| workflow_execution | `idx_exec_created` | `created_ts DESC` | Recent executions |

### 4.3 Index Notes

- All time-based indexes are DESC because most queries want "most recent first"
- `status` index is a low-cardinality column (3 values) — consider composite index
  with `created_ts` rather than standalone
- For high-volume systems, consider partitioning `workflow_execution` by `created_ts`

---

## 5. STORAGE SIZING ESTIMATES

### 5.1 Per-Record Size Estimates

| Field | Estimated Size |
|---|---|
| Fixed fields (IDs, timestamps, status, etc.) | ~500 bytes |
| `inputs_ref` string | ~80–200 bytes |
| `output_ref` string | ~80–200 bytes |
| `execution_trace` JSON | ~2–10 KB |
| `error` JSON (when present) | ~500 bytes–2 KB |

**Typical success record:** ~3–15 KB
**Typical failure record:** ~3–12 KB

**Cold storage note:** Article payload size (MD + JSON output) is moved out of primary DB.

### 5.2 Volume Projections

| Scenario | Executions/day | Storage/day | Storage/month |
|---|---|---|---|
| Development | 10–50 | 1–8 MB | 30–240 MB |
| Production (moderate) | 100–500 | 10–80 MB | 300 MB–2.4 GB |
| Production (high) | 1000–5000 | 100–800 MB | 3–24 GB |

---

## 6. MIGRATION STRATEGY

### 6.1 Schema Versioning

- Schema changes are versioned and tracked
- Additive changes (new nullable columns) are preferred over breaking changes
- Breaking changes require data migration scripts

### 6.2 Backwards Compatibility

- New fields added to JSON columns (`execution_trace`, `error`) do not require
  schema migration — JSON storage is schema-flexible.
- Consumers of execution payload references (`inputs_ref`, `output_ref`) MUST
  handle missing/not-yet-populated references gracefully during transition.
- The `version` field on workflow definitions tracks schema compatibility.

### 6.3 TODO — Cold Storage Migration Window

- TODO: Any residual inline persistence of workflow `inputs` / `output` in primary DB
  must be migrated to `inputs_ref` / `output_ref` cold-storage references.
- Target window: complete migration within the next **1–2 releases**.
- TODO: Workflow metadata artifacts (e.g., config snapshots, node graph exports)
  should remain out of primary workflow tables and be stored in cold storage only.

---

## 7. BACKEND-SPECIFIC NOTES

### 7.1 PostgreSQL

```sql
-- Workflow table
CREATE TABLE workflow (
    workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) NOT NULL,
    created_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    tags TEXT[] DEFAULT '{}'
);

-- Workflow execution table
CREATE TABLE workflow_execution (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow(workflow_id),
    workflow_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),
    created_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_ts TIMESTAMPTZ,
    execution_time_ms INTEGER,
    inputs_ref TEXT NOT NULL,
    output_ref TEXT,
    provider_name VARCHAR(255) NOT NULL,
    tokens INTEGER,
    error JSONB,
    execution_trace JSONB DEFAULT '[]'
);

-- Indexes
CREATE INDEX idx_workflow_active ON workflow(is_active, name);
CREATE INDEX idx_workflow_name_version ON workflow(name, version);
CREATE INDEX idx_exec_workflow ON workflow_execution(workflow_id, created_ts DESC);
CREATE INDEX idx_exec_status ON workflow_execution(status, created_ts DESC);
CREATE INDEX idx_exec_created ON workflow_execution(created_ts DESC);
```

### 7.2 SQLite (Development / Embedded)

- Use TEXT columns for JSON fields (no native JSONB)
- Use TEXT for UUID fields
- Use TEXT for timestamps (ISO8601 format)
- JSON queries via `json_extract()` function

### 7.3 File-Based (Development Only)

```
/data/workflows/
  ├── {workflow_id}.json
  └── ...
/data/executions/
  ├── {run_id}.json
  └── ...
/data/indexes/
  ├── by_workflow.json     // workflow_id → [run_ids]
  ├── by_status.json       // status → [run_ids]
  └── recent.json          // [run_ids] ordered by created_ts DESC
```

- One JSON file per record
- Separate index files for query support
- Suitable for development and testing only
- No concurrent write safety

---

## 8. MONITORING QUERIES

### 8.1 Success Rate (last 24h)

```sql
SELECT
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as pct
FROM workflow_execution
WHERE created_ts > NOW() - INTERVAL '24 hours'
GROUP BY status;
```

### 8.2 Average Execution Time (last 7 days)

```sql
SELECT
    DATE(created_ts) as day,
    AVG(execution_time_ms) as avg_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms) as p95_ms
FROM workflow_execution
WHERE status = 'SUCCESS'
  AND created_ts > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_ts)
ORDER BY day DESC;
```

### 8.3 Token Consumption (last 7 days)

```sql
SELECT
    DATE(created_ts) as day,
    SUM(tokens) as total_tokens,
    AVG(tokens) as avg_tokens_per_run,
    COUNT(*) as runs
FROM workflow_execution
WHERE created_ts > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_ts)
ORDER BY day DESC;
```

### 8.4 Common Failure Reasons

```sql
SELECT
    error->>'failure_reason' as reason,
    COUNT(*) as count
FROM workflow_execution
WHERE status = 'FAILED'
  AND created_ts > NOW() - INTERVAL '30 days'
GROUP BY error->>'failure_reason'
ORDER BY count DESC;
```

---

## 9. VERSIONING

| Field | Value |
|---|---|
| Document version | 1.0 |
| Created | 2026-03-31 |
| Last updated | 2026-03-31 |
| Status | Active |
