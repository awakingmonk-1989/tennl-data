# Novelty Pool CLI — Mode Execution Spec
## `tennl.batch.workflows.novelty_pool_cli`
### Version 1.0 · 2 April 2026

---

## 1. Purpose

The Novelty Pool CLI is the runtime entry point for content generation with
**creative control rotation** as defined in the
[Standalone Content Agent Spec](content_gen_novelty_spec.md). It supports two
execution modes:

- **Single run** — one article with explicit pool selections via CLI flags.
- **Batch run** — N articles with automated pool-value rotation and topic
  cycling from an external JSON file.

Both modes use the same underlying `ContentGenWorkflow` (LlamaIndex Workflows)
and the same evaluation pipeline (moderation → quality/schema → eval merge →
optional refine loop).

**Progress & handoff guide:**
[`python/tennl/batch/novelty_mode_progress.md`](../python/tennl/batch/novelty_mode_progress.md)

---

## 2. Control Model (from novelty spec)

### Layer 1 — Base Metadata (pools + constraints)

Defined as module-level constants in `novelty_pool_cli.py`. These are the
**creative boundaries** — the full set of allowed values for each dimension.

| Field | Type | Values |
|-------|------|--------|
| `intent_profile` | `list[str]` | `["relatable", "useful", "hopeful", "grounded"]` |
| `content_mode_pool` | `list[str]` | `["story", "analysis", "guide", "reflection", "comparison"]` |
| `angle_pool` | `list[str]` | `["personal_experience", "decision_support", "mistake_recovery", "trend_interpretation", "myth_busting", "practical_breakdown"]` |
| `tone_pool` | `list[str]` | `["honest", "encouraging", "calm", "grounded"]` |
| `hook_style_pool` | `list[str]` | `["observation", "contrarian", "practical_problem", "small_truth", "unexpected_pattern"]` |

### Layer 2 — Runtime Selections (exactly 1 from each pool)

Before each generation call, the orchestrator picks exactly one value from each
pool. These are passed as **mandatory guidance** to the LLM.

| Field | Constraint |
|-------|-----------|
| `content_mode` | Must be in `content_mode_pool` |
| `angle` | Must be in `angle_pool` |
| `tone` | Must be in `tone_pool` |
| `hook_style` | Must be in `hook_style_pool` |

### Quality Constraints (always sent in full)

```json
{
  "must_include": ["specific_scenario", "realistic_takeaway", "non_generic_language"],
  "avoid": ["clickbait", "template_openings", "generic_motivation", "repetitive_listicle_style"]
}
```

These are **never optional** and are sent with every invocation (single or batch).

---

## 3. Input Contract

### 3.1 Single Run

CLI flags map directly to `WorkflowInput` fields:

```
novelty_pool_cli single \
  --topic "Home & Living" \
  --sub-topic "Daily Living Hacks" \
  --content-variant AI_GENERATED \
  --content-mode guide \
  --angle practical_breakdown \
  --tone calm \
  --hook-style practical_problem \
  [--eval-mode sequential] \
  [--max-refine-attempts 1] \
  [--timeout 300]
```

- `--content-mode`, `--angle`, `--tone`, `--hook-style` are **required** and
  validated against their respective pools (argparse `choices`).
- `intent_profile` is always the full list (not user-selectable).
- `quality_constraints` is always the full set.

### 3.2 Batch Run

```
novelty_pool_cli batch \
  --invocations 10 \
  --topics-json /absolute/path/to/topics.json \
  [--content-variant AI_GENERATED] \
  [--eval-mode sequential] \
  [--max-refine-attempts 1] \
  [--timeout 300] \
  [--num-workers 1] \
  [--future-result-timeout-s 120]
```

- `--invocations` (`-n`): number of workflow invocations.
- `--topics-json`: absolute path to a JSON file containing topic entries.
  Each entry must have `topic` and `subtopic` keys. Extra keys
  (`rank`, `best_fit_formats`, `why_it_makes_the_cut_now`) are ignored.
- Topics cycle: `topics[i % len(topics)]` for invocation `i`.
- Pool values rotate: `pool[i % len(pool)]` for each pool independently.
- `sub_topic_description` is set to the `subtopic` value (no separate field).
- `--num-workers`: thread-pool workers for parallel batch. Default 1 preserves
  the sequential async loop behaviour.
- `--future-result-timeout-s`: timeout used when retrieving completed future
  results (parallel mode). Default 120.

### 3.3 Topics JSON Shape

```json
{
  "india_broad_audience_safe_global_top_10": [
    { "rank": 1, "topic": "Money & Life", "subtopic": "Personal Finance Reality", ... },
    { "rank": 2, "topic": "Food & Life", "subtopic": "Affordable Everyday Food / Smart Eating", ... }
  ]
}
```

The loader accepts a root-level list or a dict with a single list value.
Only `topic` and `subtopic` are consumed; all other fields are ignored.

---

## 4. Rotation Logic (Batch Mode)

For invocation `i` (0-indexed):

```
topic       = topics_list[i % len(topics_list)]["topic"]
sub_topic   = topics_list[i % len(topics_list)]["subtopic"]
content_mode = CONTENT_MODE_POOL[i % 5]
angle        = ANGLE_POOL[i % 6]
tone         = TONE_POOL[i % 4]
hook_style   = HOOK_STYLE_POOL[i % 5]
```

Pool sizes differ, so combinations diverge across runs — the LCM of
(5, 6, 4, 5) = 60, meaning full combinatorial coverage repeats every
60 invocations (before considering topic cycling).

---

## 5. Prompt Field Validation

All prompt input fields are **required and non-empty**. Validation is enforced
in `format_prompt()` in `stages/generator.py`:

```python
empty_fields = sorted(k for k, v in merged.items() if not v.strip())
if empty_fields:
    raise ValueError(
        f"Prompt has empty required fields: {empty_fields}. "
        "All prompt input fields must be populated before rendering."
    )
```

This checks every key in the merged template dict. If any value is an empty
string after stripping, the workflow fails immediately with a clear error
listing the missing fields.

---

## 6. WorkflowInput Model

`WorkflowInput` in `models.py` carries all creative control fields:

```python
class WorkflowInput(BaseModel):
    topic: str
    sub_topic: str
    content_variant: ContentVariant
    eval_mode: EvalMode = EvalMode.PARALLEL
    max_refine_attempts: int = Field(default=1, ge=0, le=1)

    # Creative control pools (Layer 1)
    intent_profile: list[str] = Field(default_factory=list)
    content_mode_pool: list[str] = Field(default_factory=list)
    angle_pool: list[str] = Field(default_factory=list)
    tone_pool: list[str] = Field(default_factory=list)
    hook_style_pool: list[str] = Field(default_factory=list)
    quality_constraints: QualityConstraints = Field(default_factory=...)

    # Runtime selections (Layer 2)
    content_mode: str = ""
    angle: str = ""
    tone: str = ""
    hook_style: str = ""
```

All fields have defaults (empty lists / empty strings) so the original
`cli.py` continues to work without passing creative controls. The novelty
CLI always populates all fields.

---

## 7. Output Strategy

### 7.1 Single Mode

- Local artifacts: `out/{run_id}/article.md` + `article.json`
- Azure Storage: blob + table index writes (if `AZURE_STORAGE_CONNECTION_STRING` set)
- PostgreSQL: **not used** in single mode

### 7.2 Batch Mode (target design)

- **Local file accumulation**: results are buffered in memory. Every 25
  completed runs, the buffer is flushed to `specs/data/batch_{timestamp}/`
  as individual `{run_id}.md` + `{run_id}.json` files. Remaining buffer
  (<25) is flushed after the loop ends. One directory per batch invocation.
  No per-run `out/{run_id}/` writes in batch mode.
- **Azure Storage**: per-run blob + table writes (unchanged, if env var set).
- **PostgreSQL**: per-run INSERT into `content_gen_article` (see §8).

**Memory note (large batches):**

For large batches (N≈1000+), avoid retaining the full `article_md` / `article_json`
payloads for all invocations in memory. The implementation keeps only:
- a bounded flush buffer (default 25) of successful runs for disk writes, and
- lightweight per-run summaries (run_id, status, failure reason) for reporting.
This ensures flush-to-disk actually releases memory, rather than keeping content
alive via a long-lived `results` list.

---

## 8. PostgreSQL Persistence (Batch Mode Only)

### 8.1 Database & Table

| Property | Value |
|----------|-------|
| Host | `localhost:5432` |
| User | `postgres` |
| Password | (none — trust/peer auth) |
| Database | `content_gen` |
| Table | `content_gen_article` |

### 8.2 Schema

```sql
CREATE TABLE IF NOT EXISTS content_gen_article (
    id              UUID    PRIMARY KEY,
    run_id          TEXT    NOT NULL,
    article_md      TEXT,
    article_json    JSONB,
    status          TEXT,
    reason          TEXT,
    error_message   TEXT
);
```

| Column | Type | Nullable | Purpose |
|--------|------|----------|---------|
| `id` | UUID | NOT NULL (PK) | Workflow `run_id` as UUID — primary key |
| `run_id` | TEXT | NOT NULL | Same `run_id` as plain string for easy querying without UUID casts |
| `article_md` | TEXT | YES | Full article markdown. NULL for failed runs. PostgreSQL TEXT is unbounded (up to 1 GB). |
| `article_json` | JSONB | YES | Full article JSON. NULL for failed runs. JSONB supports indexing, containment queries, GIN indexes. |
| `status` | TEXT | YES | `"success"` for generated articles, `"failed"` for failures |
| `reason` | TEXT | YES | Failure reason (e.g. `EVALUATION_CRITERIA_NOT_MET`, `RUNTIME_ERROR`). NULL on success. |
| `error_message` | TEXT | YES | Error detail (truncated to 2000 chars). NULL on success. |

Design rationale:

- Both success and failure runs are persisted — enables failure rate analysis
  and debugging without parsing logs.
- `article_md` and `article_json` are nullable because failed runs have no
  content (or only partial content from a failed refine loop).
- `run_id` is stored as both UUID (`id`) and TEXT (`run_id`) — the UUID is
  the canonical PK; the text form avoids `::uuid` casts in ad-hoc queries.
- Metadata (topic, sub_topic, pool selections, timestamps) is **not** stored
  in PostgreSQL yet — it lives in the execution trace (JSONL), Azure Table
  indexes, and the batch directory filenames.

### 8.4 Connection & Driver

- Python driver: `psycopg` v3 (modern async-capable, but used synchronously
  in the current sequential batch loop).
- Dependency: `psycopg[binary]>=3.2.0` in `pyproject.toml`.
- Connection string: `postgresql://devansh@localhost:5432/content_gen`
  (overridable via `CONTENT_GEN_PG_DSN` env var).
- Failure handling: try/except with log — a PostgreSQL failure does NOT stop
  the batch. Same pattern as Azure persist.

**Parallel mode note:** uses `psycopg_pool.ConnectionPool` created once at batch
start with `min_size=num_workers, max_size=num_workers`, then passed to per-run
inserts. Each worker checks out its own connection.

### 8.5 Persistence behaviour

| Run outcome | `status` | `article_md` | `article_json` | `reason` | `error_message` |
|-------------|----------|-------------|----------------|----------|-----------------|
| Success | `"success"` | Full markdown | Full JSON | NULL | NULL |
| Failure | `"failed"` | NULL | NULL | Failure reason enum | Error detail (≤2000 chars) |

Both success and failure rows use the same `run_id` as UUID PK. `ON CONFLICT
(id) DO NOTHING` ensures idempotency on retries.

### 8.6 Setup

```bash
psql -d postgres -c "CREATE DATABASE content_gen" 2>/dev/null || true
psql -d content_gen -f python/scripts/setup_content_gen_pg.sql
```

On macOS with Homebrew `postgresql@18`, the default user is your OS username.

### 8.7 Parallel execution (implemented)

For batch sizes of 1000–1500, sequential execution is too slow (~35s per run
= ~10 hours for 1000). Parallel execution is required.

**Design & implementation:**

- Add `--num-workers` CLI arg to `novelty_pool_cli batch` (default: 1).
- Use a thread pool (`concurrent.futures.ThreadPoolExecutor`) with
  `num_workers` threads. Each thread runs its own `asyncio.run()` loop
  for a single workflow invocation.
- Pre-warm the thread pool at batch start.
- Use `psycopg_pool.ConnectionPool(min_size=num_workers, max_size=num_workers)`
  for thread-safe PG connections. Each thread checks out its own connection.
- Azure persist remains per-run per-thread (stateless HTTP calls).
- File buffer flush uses a lock to serialize writes to the batch directory.
- Target: 1000 min, 1500 max batch size. Verify at N=10 first, then scale.

**Hardening notes:**
- Futures are collected with `as_completed()`; failures (cancelled/timeout/exception)
  are categorized and logged with `exc_info=True`, with an end-of-batch summary.
- Worker crash path persists a `"failed"` PG row (`reason="RUNTIME_ERROR"`) even if
  the workflow result dict is never produced.
- Azure Table keys are normalized for `categoryentityindex` partition keys to
  satisfy Azure Table key restrictions.

---

## 13. Verification Utilities (scripts)

Parallel smoke + scale scripts:

- `python/scripts/verify_novelty_parallel_n2.sh`
- `python/scripts/verify_novelty_parallel_n10.sh`

Batch run verifier (local + PG + Azure tables + Azure blobs, time-window based):

- `python/scripts/verify_novelty_batch_run_artifacts.py`

Notes:
- Scripts source `secrets.txt` to load env vars (no values echoed).
- Azure blob verification allows a configurable clock skew window.


---

## 9. Execution Flow — Batch Mode

```
Batch start
  → create specs/data/batch_{timestamp}/ directory
  → initialize in-memory buffer (list)

For each invocation i = 0..N-1:
  1. Pick topic[i % topics], rotate pool values
  2. Run workflow (LLM generation → eval → optional refine)
  3. If GENERATED:
     a. Azure persist (per-run, if enabled)
     b. PostgreSQL INSERT (per-run)
     c. Append (run_id, article_md, article_json) to buffer
  4. If buffer length == 25:
     a. Write 25 .md + 25 .json files to batch directory
     b. Clear buffer

After loop:
  → Flush remaining buffer to batch directory
  → Print batch summary (total / succeeded / failed)
```

---

## 10. File Map

```
python/tennl/batch/
├── src/tennl/batch/workflows/
│   ├── novelty_pool_cli.py          # Novelty CLI (single + batch modes)
│   ├── pg_storage.py                # PostgreSQL insert_article (NEW — pending)
│   ├── cli.py                       # Original CLI (unchanged, no creative controls)
│   ├── workflow.py                   # ContentGenWorkflow (sub_topic_description fix)
│   ├── models.py                    # WorkflowInput with creative control fields
│   ├── stages/generator.py          # Prompt field validation + direct field access
│   └── ...
├── novelty_mode_progress.md         # Progress & handoff guide
└── pyproject.toml                   # + psycopg[binary] (pending)

specs/
├── novelty_pool_cli_spec.md         # ← this file
├── content_gen_novelty_spec.md      # Standalone content agent spec (source of truth)
└── data/
    └── batch_{timestamp}/           # Batch output directories (created at runtime)

python/scripts/
├── setup_content_gen_pg.sql         # PostgreSQL setup (pending)
└── verify_novelty_cli.sh            # Single-run verification script
```

---

## 11. Verification

### Single run (verified 2 Apr 2026)

```bash
bash python/scripts/verify_novelty_cli.sh
```

Expected: all 5 stages PASS, `out/{run_id}/` written, Azure blob + table
written (if `AZURE_STORAGE_ACCOUNT_KEY` set).

### Batch run (pending)

```bash
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run --project python/tennl/batch \
  python -m tennl.batch.workflows.novelty_pool_cli batch \
  --invocations 5 \
  --topics-json /Users/devansh/tennl-data/contetn_gen_topics_india.json
```

Expected: 5 runs with rotated pool values, output in `specs/data/batch_{ts}/`,
PostgreSQL rows inserted, batch summary printed.

---

## 12. Open Items

### Done

- [x] `pg_storage.py` — success + failure persistence with 7-column schema
- [x] 25-run buffer accumulation in `run_batch`
- [x] `psycopg[binary]` in `pyproject.toml`
- [x] `setup_content_gen_pg.sql`
- [x] PostgreSQL 18 started, database + table created

### Next (for next agent)

- [ ] **End-to-end batch dry run (N=2)** — verify PG inserts + file accumulation + Azure
- [ ] **Create batch dry run script** — `python/scripts/verify_novelty_batch.sh`
- [ ] **Add `--num-workers` CLI arg** — default 1 (sequential), >1 enables thread pool
- [ ] **Implement thread-pool parallel execution** — `ThreadPoolExecutor(num_workers)`,
      each thread runs `asyncio.run()` for one workflow invocation
- [ ] **Thread-safe PG connections** — `psycopg.pool.ConnectionPool(min_size=N, max_size=N)`,
      pre-warmed at batch start, one connection per thread
- [ ] **File flush lock** — `threading.Lock` around `_flush_buffer` for thread safety
- [ ] **Verify at N=10** — confirm parallel execution, PG rows, batch directory
- [ ] **Scale to N=1000** — target min batch size; monitor LLM rate limits, PG throughput
- [ ] **Scale to N=1500** — target max batch size
- [ ] Consider metadata columns in PostgreSQL (topic, sub_topic, pool selections, timestamp)
