# Novelty Mode — Progress & Handoff Guide
## `tennl.batch.workflows.novelty_pool_cli`
### Last updated: 2 April 2026

---

## Governing Spec

> **[`specs/novelty_pool_cli_spec.md`](../../../specs/novelty_pool_cli_spec.md)**
>
> Contains: control model, input contract, rotation logic, output strategy,
> PostgreSQL schema (7-column), parallel execution design, execution flow,
> file map, and verification commands.
> **Read the spec first for full design context.**

---

## Current Phase: Parallel Batch Implemented + Verified (N=2 + N=10) — Pending Scale Run (N=1000)

The novelty-pool CLI is functional for **single-run**, **sequential batch**,
and **parallel batch (thread pool)** execution with:
- `--num-workers` (default 1) to enable/disable parallel mode
- Thread-safe PG inserts via `psycopg_pool.ConnectionPool`
- Thread-safe buffer flush via `threading.Lock`
- Hardened future exception handling (`as_completed()` + categorized failures)
execution with full creative control fields, prompt validation, local artifact
output, PostgreSQL persistence, and Azure Storage persistence.

**Batch mode** is verified end-to-end with:
- 25-run in-memory buffer with flush to `specs/data/batch_{timestamp}/`
- Per-run PostgreSQL INSERT (success + failure rows)
- Per-run Azure persist (if env var set)
- Pool rotation across invocations
- Verified with N=2 batch runs (success + failure paths)

**Workflow logging** has been hardened:
- All workflow nodes log to `logs/workflow_run.log` (rolling plain-text)
- Moderation violations, quality scores, schema failures logged verbosely
- All exception handlers use `exc_info=True` for full stack traces
- Duplicate N2 generation bug fixed

**Remaining**: scale validation at large batch size (N=1000) with higher worker count.

---

## What Is Done

### 1. WorkflowInput extended with creative control fields

| Change | File | What |
|--------|------|------|
| Added pool fields to `WorkflowInput` | `src/tennl/batch/workflows/models.py` | `intent_profile`, `content_mode_pool`, `angle_pool`, `tone_pool`, `hook_style_pool`, `quality_constraints` |
| Added runtime selection fields | `src/tennl/batch/workflows/models.py` | `content_mode`, `angle`, `tone`, `hook_style` |
| All fields have defaults | — | Empty lists / empty strings so original `cli.py` is unaffected |

### 2. Generator prompt path updated

| Change | File | What |
|--------|------|------|
| Direct field access | `src/tennl/batch/workflows/stages/generator.py` | Replaced `getattr(inp, ...)` fallbacks with direct `inp.field` access |
| Prompt field validation | `src/tennl/batch/workflows/stages/generator.py` | Added empty-field check on merged dict before rendering — raises `ValueError` listing empty fields |

### 3. Workflow sub_topic_description fix

| Change | File | What |
|--------|------|------|
| Removed hardcoded description | `src/tennl/batch/workflows/workflow.py` | `sub_topic_description` now uses `inp.sub_topic` instead of `"Explore ideas for styling real living spaces."` |

### 4. Novelty Pool CLI created

| Change | File | What |
|--------|------|------|
| New CLI module | `src/tennl/batch/workflows/novelty_pool_cli.py` | Two subcommands: `single` and `batch` |
| Pool constants | `novelty_pool_cli.py` | Hardcoded `INTENT_PROFILE`, `CONTENT_MODE_POOL`, `ANGLE_POOL`, `TONE_POOL`, `HOOK_STYLE_POOL` |
| Quality constraints | `novelty_pool_cli.py` | `QUALITY_CONSTRAINTS` always sent in full (`must_include` + `avoid`) |
| Batch rotation | `novelty_pool_cli.py` | `pool[i % len(pool)]` for each dimension; topics cycled from JSON |
| Topics loader | `novelty_pool_cli.py` | `_load_topics()` — accepts root list or dict-with-list; requires `topic` + `subtopic` keys |
| Batch accumulation | `novelty_pool_cli.py` | 25-run buffer, flush to `specs/data/batch_{ts}/`, no per-run `out/` writes |
| Batch PG persist | `novelty_pool_cli.py` | `_handle_batch_result` calls `insert_article` for both success and failure |

### 5. PostgreSQL persistence

| Change | File | What |
|--------|------|------|
| `pg_storage.py` created | `src/tennl/batch/workflows/pg_storage.py` | `insert_article()` with keyword args, graceful failure, `ON CONFLICT DO NOTHING` |
| `psycopg[binary]>=3.2.0` added | `pyproject.toml` | Installed: psycopg 3.3.3 |
| `psycopg_pool>=3.2.0` added | `pyproject.toml` | Installed: psycopg-pool 3.3.0 (for future thread-pool parallel mode) |
| Database created | `content_gen` on `localhost:5432` | User: `devansh`, no password (Homebrew postgresql@18) |
| Table created | `content_gen_article` | 7 columns: id, run_id, article_md, article_json, status, reason, error_message |
| Setup SQL | `python/scripts/setup_content_gen_pg.sql` | Idempotent `CREATE TABLE IF NOT EXISTS` |
| DSN overridable | `pg_storage.py` | `CONTENT_GEN_PG_DSN` env var; default `postgresql://devansh@localhost:5432/content_gen` |

**Schema:**

```sql
CREATE TABLE content_gen_article (
    id              UUID    PRIMARY KEY,
    run_id          TEXT    NOT NULL,
    article_md      TEXT,
    article_json    JSONB,
    status          TEXT,       -- "success" | "failed"
    reason          TEXT,       -- failure reason (NULL on success)
    error_message   TEXT        -- error detail ≤2000 chars (NULL on success)
);
```

### 6. Spec file restored

| Change | File | What |
|--------|------|------|
| Restored filename | `specs/content_gen_spec.md` | Copied from `specs/content_gen_spec_v3.md` — code references the unversioned name |

### 7. Verification scripts

| Change | File | What |
|--------|------|------|
| Single-run script | `python/scripts/verify_novelty_cli.sh` | Requires `AZURE_STORAGE_ACCOUNT_KEY` env var |
| Batch dry-run script | `python/scripts/verify_novelty_batch.sh` | N=2 default, topics JSON path, PG verification query, batch dir listing, summary |
| PG setup SQL | `python/scripts/setup_content_gen_pg.sql` | Idempotent table creation |

### 8. Duplicate N2 generation bug fix

| Change | File | What |
|--------|------|------|
| Extracted `_do_content_generation()` | `src/tennl/batch/workflows/workflow.py` | Shared generation logic as a non-step method |
| `n2_content_generation` now accepts only `ValidatedInput` | `workflow.py` | Was `ValidatedInput \| RefinementDirectivesBuilt` — caused duplicate dispatch |
| `n8_regeneration` calls `_do_content_generation` | `workflow.py` | Was calling `self.n2_content_generation(ctx, ev)` which double-triggered |

**Root cause:** LlamaIndex Workflows dispatches events to ALL steps that accept
that event type. Both `n2_content_generation` (accepted `RefinementDirectivesBuilt`)
and `n8_regeneration` (accepted `RefinementDirectivesBuilt`) fired concurrently
on every refine cycle, producing two parallel generations per refine attempt.

### 9. Workflow logging hardened — all nodes

| Change | File | What |
|--------|------|------|
| Added `_log` module logger | `workflow.py` | `logging.getLogger("tennl.workflow.run")` used in every node |
| N1: verbose failure logging | `workflow.py` | `logger.error(..., exc_info=True)` on input validation failure |
| N2: start + completion logging | `workflow.py` | Logs attempt number on start, word count + duration on PASS, full exception on ERROR |
| N4: moderation violation details | `workflow.py` | On FAIL: logs every `check_id` + `message` for violations AND all checks; on PASS after quality: logs quality avg, schema result, structural failures |
| N6: enriched decision trace | `workflow.py` | Trace summary now includes `moderation=X, quality=X, schema=X, refine_attempts=N/M`; logs at INFO/WARNING/ERROR by decision |
| N7: trace entries for all paths | `workflow.py` | PROCEED and FAIL paths now get trace entries (were missing); FAIL logs full moderation violations, quality scores, schema failures |
| N9: upstream failure logging | `workflow.py` | Logs failure reason, node, error message on upstream `WorkflowFailed`; logs `exc_info=True` on runtime errors |

### 10. Rolling plain-text log file — `logs/workflow_run.log`

| Change | File | What |
|--------|------|------|
| `setup_rolling_run_logger()` | `src/tennl/batch/workflows/tracing.py` | 10MB max, 5 backup rotations |
| Format | `tracing.py` | `%(asctime)s %(levelname)-8s [%(threadName)s] %(name)s.%(funcName)s:%(lineno)d — %(message)s` |
| Initialized per run | `novelty_pool_cli.py` | `setup_rolling_run_logger()` called in `_execute_single_run()` |

**Logging strategy:**
- **Success path**: terse — one INFO line per node (run_id prefix, node, result, key metrics)
- **Failure path**: verbose — WARNING/ERROR with full violation lists, quality dimension scores,
  schema failure paths, exception stack traces (`exc_info=True`)
- **Two log files**: `workflow_traces.jsonl` (structured JSONL for programmatic analysis),
  `workflow_run.log` (human-readable plain text for debugging)

---

## Verified Runs (2 Apr 2026)

### Run 1 — Single mode, no Azure

```
run_id:   dfea6b72-5963-4f4f-9807-fa832409a973
topic:    Home & Living
sub:      Daily Living Hacks
pools:    guide / practical_breakdown / calm / practical_problem
result:   GENERATED — 5 stages PASS, ~1297 words, 4 sections, 4 deep dives
output:   out/dfea6b72-5963-4f4f-9807-fa832409a973/article.{md,json}
azure:    skipped (no AZURE_STORAGE_CONNECTION_STRING)
pgsql:    N/A (single mode — no PG)
duration: ~35s
```

### Run 2 — Single mode, with Azure

```
run_id:   ebe02df8-1ee6-4311-bc91-a97cc5c950f3
topic:    Home & Living
sub:      Daily Living Hacks
pools:    guide / practical_breakdown / calm / practical_problem
result:   GENERATED — 5 stages PASS, ~1153 words, 4 sections, 4 deep dives
output:   out/ebe02df8-1ee6-4311-bc91-a97cc5c950f3/article.{md,json}
azure:    blob written + workflowentityindex + categoryentityindex upserted
blob_url: https://devworkflow.blob.core.windows.net/content/articles/home%26living/dailylivinghacks/articles_workflow_1775080728593/articles_devans_1775080728593.json
pgsql:    N/A (single mode — no PG)
duration: ~36s
```

### Run 3 — Batch mode N=2, first E2E validation (pre-logging fix)

```
batch_dir: specs/data/batch_20260401_224604/
run 1/2:   7582725e-921e-4534-8e59-a215e6611a1b
  topic:   Money & Life / Personal Finance Reality
  pools:   story / personal_experience / honest / observation
  result:  GENERATED — 6 stages PASS, ~1162 words, 4 sections, 4 deep dives
  pgsql:   INSERT success (status=success)
run 2/2:   118376df-ab2b-4392-9545-52e4e5480a84
  topic:   Food & Life / Affordable Everyday Food / Smart Eating
  pools:   analysis / decision_support / encouraging / contrarian
  result:  FAILED — moderation FAIL × 2, refine exhausted
  pgsql:   INSERT success (status=failed, reason=EVALUATION_CRITERIA_NOT_MET)
  note:    Duplicate N2 generation observed (2 × "attempt 3") — bug confirmed
batch_files: 1 .md + 1 .json (success run only)
duration: ~91s total
```

### Run 4 — Batch mode N=2, post-logging fix (duplicate N2 fixed)

```
batch_dir: specs/data/batch_20260401_230703/
run 1/2:   1752bb7c-c2e1-4246-ba2b-497d0eb2df8e
  topic:   Money & Life / Personal Finance Reality
  pools:   story / personal_experience / honest / observation
  result:  GENERATED — 6 stages PASS, ~1351 words, quality avg=4.12
  pgsql:   INSERT success (status=success)
run 2/2:   9655f410-2f44-48df-8d63-b501bc1f1447
  topic:   Food & Life / Affordable Everyday Food / Smart Eating
  pools:   analysis / decision_support / encouraging / contrarian
  result:  GENERATED — 6 stages PASS, ~1275 words, quality avg=4.25
  pgsql:   INSERT success (status=success)
batch_files: 2 .md + 2 .json
duration: ~68s total
logs:     logs/workflow_run.log verified — all nodes logged, format correct
```

---

## TODOs (for next agent — ordered by priority)

### P0: Complete — E2E batch validation + logging

- [x] **Batch dry run N=2** — verified PG rows (success + failure), batch dir files, pool rotation
- [x] **Query PG after dry run** — both success and failure rows present with correct fields
- [x] **Create `python/scripts/verify_novelty_batch.sh`** — batch dry-run script with PG verification
- [x] **Fix duplicate N2 generation** — `n2_content_generation` no longer accepts `RefinementDirectivesBuilt`
- [x] **Add trace entries for N7 PROCEED/FAIL paths** — were missing, now logged
- [x] **Log moderation violations, quality/schema failures** — verbose in trace + run log
- [x] **Add rolling plain-text log** — `logs/workflow_run.log` with threadName, funcName, lineno, exc_info

### P1: Parallel execution (thread pool)

- [x] **Add `--num-workers` CLI arg** to `novelty_pool_cli batch` (default: 1 = sequential)
- [x] **Implement `ThreadPoolExecutor(num_workers)`** — each thread runs `asyncio.run()`
  for one workflow invocation. Pre-warm the pool at batch start.
- [x] **Replace PG connects with `psycopg_pool.ConnectionPool` for parallel mode** —
  `ConnectionPool(conninfo=PG_DSN, min_size=num_workers, max_size=num_workers)`.
  Created once at batch start, passed to inserts per-thread.
- [x] **Add `threading.Lock` around buffer append + `_flush_buffer`** — serialize file I/O
- [x] **Batch result collection** — use `concurrent.futures.as_completed()`; categorize/log
  cancelled/timeout/exception failures with end-of-batch summary.
- [x] **Azure Table upsert fix** — normalize `categoryentityindex` partition keys for Azure
  Table key restrictions (prevents 400 Bad Request).
- [x] **Console run logger** — `logs/workflow_run.log` also emitted to stdout for live visibility
- [x] **Mitigate noisy httpx shutdown warnings** — suppress the specific "event loop is closed"
  task warning in worker event loop (without hiding real failures).

### P2: Scale verification

- [x] **Verify N=10** — confirm parallel execution works, PG rows correct, files flushed
- [ ] **Verify N=25** — confirm flush-at-25 boundary fires correctly
- [ ] **Verify N=30** — confirm partial flush (25 + 5 remainder)
- [~] **Run N=1000** (target min batch size) — IN PROGRESS. First attempt completed 609/1000
  (408 success, 201 failed, ~67% success rate) before being killed to apply retry fixes.
  Second run launched with retry improvements — monitor and verify to completion.
- [ ] **Run N=1500** (target max batch size) — same monitoring, ~87 minutes at 10 workers.

### P2.1: Known scale risk (pre-flight)

- [x] **Memory pressure from accumulating `results` list** — refactored `run_batch()` to
  keep only lightweight per-run summaries in memory (run_id/status/failure metadata),
  while the bounded flush buffer (25 successes) is the only structure holding full
  `article_md`/`article_json` for disk writes. This prevents N=1000 runs from keeping
  all content resident in RAM.

### P2.2: LLM retry hardening (added 2 Apr 2026)

- [x] **Application-level tenacity retry wrapper** — `acomplete_with_backoff()` in
  `llm_factory.py` wraps all `llm.acomplete()` calls with `tenacity.retry`:
  `wait_random_exponential(min=4, max=120)`, `stop_after_attempt(8)`, retries on
  `RateLimitError`, `APIConnectionError`, `APITimeoutError`, `InternalServerError`.
- [x] **Bumped AzureOpenAI constructor params** — `max_retries=8, timeout=120.0`
  (was default `max_retries=3, timeout=60.0`).
- [x] **Updated 3 call sites** — `generator.py`, `moderation_eval.py`, `quality_eval.py`
  all use `acomplete_with_backoff(llm, prompt)` instead of `llm.acomplete(prompt)`.

**Why two retry layers:**
The LlamaIndex `llm_retry_decorator` has a hardcoded `stop_after_delay_seconds=60`
that cannot be changed without monkey-patching. With Azure's `Retry-After: 30` header,
the inner layer gets at most ~2 retries before the 60s wall. The outer application
layer provides a longer retry window (8 attempts × up to 120s wait) with jitter to
desynchronize thundering-herd retries across 50 concurrent workers.

**Observed failure modes at N=1000 / 50 workers:**
1. `RateLimitError (429)` — Azure OpenAI TPM/RPM limits. Inner retry waits 30s per
   `Retry-After` header; outer retry adds jittered exponential backoff.
2. `APIConnectionError` — Azure drops TCP connections under load (`httpcore.ReadError`).
   Inner retry handles this but exhausts within 60s. Outer retry now catches it too.
3. `EVALUATION_CRITERIA_NOT_MET` — schema validation failures (missing `$.hero`,
   `$.hook`, etc.) — these are LLM output quality issues, not transient errors.

### P3: Quality of life

- [ ] **CLI support for prompt template selection** — `--prompt-template` flag to switch
  between `content_gen_base` and `content_gen_novelty_v1`. Currently always uses
  `content_gen_base`.
- [ ] **Batch resume** — if batch fails at invocation 40/100, ability to resume from 41
  without re-running 1–40. Needs checkpoint file or PG-based progress tracking.
- [ ] **Consider PG metadata columns** — topic, sub_topic, content_mode, angle, tone,
  hook_style, created_at timestamp. Only if query patterns require it.

---

## Architecture Decisions

### Why pool constants are hardcoded (not config-driven)

Per user instruction: "for now lets assume constants for each pool with list
of str values." Moving to config-driven pools (YAML or JSON) is a natural
next step but was deferred to keep the initial implementation simple.

### Why sub_topic_description = sub_topic

The original code had a hardcoded description string. The topics JSON does
not carry a separate description field (`why_it_makes_the_cut_now` and
`best_fit_formats` are not related to content generation). Using `sub_topic`
as the description is the correct minimal approach.

### Why prompt field validation is a simple truthiness check

The user explicitly requested a simple check over the merged dict rather than
regex-based template placeholder detection. The check is:
```python
empty_fields = sorted(k for k, v in merged.items() if not v.strip())
```
Every field in the merged dict must have a non-empty value.

### Why Azure persist is per-run (not batched)

Azure Blob is the source of truth per the store strategy spec. Writing
per-run ensures each article is durable immediately. If the batch crashes
at run 40/100, runs 1–39 are already persisted.

### Why PostgreSQL persists both success and failure

Failure rows (status="failed", reason, error_message) enable failure-rate
analysis and debugging without parsing JSONL logs. The `article_md` and
`article_json` columns are nullable so failed runs store only error metadata.

### Why thread pool (not asyncio.gather) for parallel execution

The LlamaIndex workflow is async, but each invocation is independent and
self-contained. Running each in its own `asyncio.run()` inside a thread
avoids sharing event loops across concurrent workflows. `psycopg.pool.ConnectionPool`
provides thread-safe PG connections out of the box. The thread pool model is
simpler to reason about than nested async concurrency with shared state.

### Why 25-run buffer flush size

Balances memory usage against disk I/O reduction. At ~7KB per article
(md + json), 25 articles ≈ 175KB in memory — negligible. Writing 50 files
at once (25 md + 25 json) amortizes directory metadata overhead.

### Why n2_content_generation only accepts ValidatedInput (not RefinementDirectivesBuilt)

LlamaIndex Workflows dispatches events to ALL steps whose type annotation
matches the emitted event. Previously both `n2_content_generation` and
`n8_regeneration` accepted `RefinementDirectivesBuilt`, causing two
concurrent generation calls per refine cycle. Fix: `n2_content_generation`
accepts only `ValidatedInput`; `n8_regeneration` handles
`RefinementDirectivesBuilt` and calls `_do_content_generation()` (shared
non-step method). This is a framework-level constraint of LlamaIndex
Workflows event routing.

### Why two log files (JSONL + plain text)

`workflow_traces.jsonl` is structured (machine-parseable) for programmatic
analysis, dashboards, and aggregation. `workflow_run.log` is human-readable
with `threadName`, `funcName`, `lineno`, `exc_info` for interactive debugging.
Both are rolling files. The plain-text log is verbose on failure (full violation
lists, quality dimensions, schema failure paths, stack traces) and terse on
success (one INFO line per node).

---

## File Map

```
python/tennl/batch/
├── src/tennl/batch/
│   ├── resources/
│   │   ├── app.yaml
│   │   ├── prompts.yaml
│   │   ├── sample_output_reference.md
│   │   └── sample_output_reference.json
│   └── workflows/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py                       # Original CLI (unchanged)
│       ├── novelty_pool_cli.py          # Novelty CLI (single + batch)
│       ├── pg_storage.py                # PostgreSQL storage (done — 7-column schema)
│       ├── workflow.py                  # ContentGenWorkflow (dup-gen fix + verbose logging)
│       ├── events.py
│       ├── models.py                    # WorkflowInput with creative control fields
│       ├── settings.py
│       ├── llm_factory.py
│       ├── azure_storage.py
│       ├── tracing.py                   # JSONL trace logger + plain-text run logger
│       └── stages/
│           ├── generator.py             # Prompt validation + direct field access
│           ├── input_validation.py
│           ├── moderation_eval.py
│           ├── quality_eval.py
│           ├── schema_validation.py
│           ├── eval_merge.py
│           ├── refiner.py
│           └── final_validation.py
├── novelty_mode_progress.md             # ← this file
├── agent_workflow_progress.md           # Original workflow progress (Phase 1)
└── pyproject.toml                       # psycopg[binary]>=3.2.0 + psycopg_pool>=3.2.0

specs/
├── novelty_pool_cli_spec.md             # Novelty CLI spec (governing design doc)
├── content_gen_novelty_spec.md          # Standalone content agent spec
├── content_gen_spec.md                  # Content gen spec (restored copy)
├── content_gen_spec_v3.md               # Content gen spec (versioned original)
├── narration_flow_spec_v1.1.md
├── json_schema_spec_v1.md
└── data/
    └── batch_{timestamp}/               # Batch output dirs (created at runtime)

python/scripts/
├── verify_novelty_cli.sh               # Single-run verification script
├── verify_novelty_batch.sh             # Batch dry-run script (done)
└── setup_content_gen_pg.sql            # PostgreSQL setup (done)

logs/
├── workflow_traces.jsonl               # Structured JSONL trace (rolling, 5MB × 5)
└── workflow_run.log                    # Plain-text run log (rolling, 10MB × 5)
```

---

## How to Run (quick start for next agent)

### Prerequisites

```bash
# 1. Start PostgreSQL (if not running)
brew services start postgresql@18

# 2. Create database + table (idempotent)
psql -d postgres -c "CREATE DATABASE content_gen" 2>/dev/null || true
psql -d content_gen -f python/scripts/setup_content_gen_pg.sql

# 3. Verify
psql -d content_gen -c "\d content_gen_article"
```

### Single run

```bash
export AZURE_STORAGE_ACCOUNT_KEY="..."  # optional
bash python/scripts/verify_novelty_cli.sh
```

### Batch run (sequential — verified)

```bash
bash python/scripts/verify_novelty_batch.sh        # default N=2
bash python/scripts/verify_novelty_batch.sh 5       # custom N
```

Or manually:

```bash
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run --project python/tennl/batch \
  python -m tennl.batch.workflows.novelty_pool_cli batch \
  --invocations 2 \
  --topics-json /Users/devansh/tennl-data/contetn_gen_topics_india.json \
  --content-variant AI_GENERATED \
  --eval-mode sequential

# Verify PG rows
psql -d content_gen -c "SELECT id, run_id, status, reason FROM content_gen_article"

# Check logs
tail -50 logs/workflow_run.log
```

### Batch run (parallel — NOT YET IMPLEMENTED)

### Batch run (parallel — implemented)

```bash
bash python/scripts/verify_novelty_parallel_n2.sh
bash python/scripts/verify_novelty_parallel_n10.sh
```

Or manually:

```bash
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run --project python/tennl/batch \
  python -m tennl.batch.workflows.novelty_pool_cli batch \
  --invocations 10 \
  --topics-json /Users/devansh/tennl-data/contetn_gen_topics_india.json \
  --num-workers 10
```

---

## Next Agent Handoff (copy/paste prompt)

You are picking up the novelty-pool CLI for the tennl content generation platform.

Context files (source of truth):
- `python/tennl/batch/novelty_mode_progress.md`
- `specs/novelty_pool_cli_spec.md`

Current state:
- Parallel batch mode is implemented and verified at N=2 and N=10.
- Azure persist + PG persist + local batch dir artifacts work in parallel mode.
- `run_batch()` has been refactored to avoid retaining full article payloads in memory
  across large batches (keeps only lightweight per-run summaries + bounded flush buffer).
- **LLM retry hardening done** — `acomplete_with_backoff()` in `llm_factory.py` wraps all
  3 `llm.acomplete()` call sites (generator, moderation_eval, quality_eval) with tenacity
  `wait_random_exponential(min=4, max=120)`, retries on `RateLimitError`, `APIConnectionError`,
  `APITimeoutError`, `InternalServerError` (8 attempts). AzureOpenAI constructor also bumped
  to `max_retries=8, timeout=120.0`.
- **N=1000 scale run attempted** — first run (pre-retry-fix) reached 609/1000 (67% success).
  A second run with retry fixes is currently in progress (PID 34365, batch dir
  `specs/data/batch_20260402_010217`). PG baseline before this run: 742 rows.
- **Primary bottleneck is Azure OpenAI rate limits (429) and connection drops** — not
  PG or Azure Storage. At 50 workers the LLM API is saturated.

Your tasks:
1) **Monitor the in-progress N=1000 run** — check PG row count growth, `logs/workflow_run.log`
   for errors, and whether the retry fixes reduced the failure rate vs the first run (67%).
   If the run has completed, record final wall time, success/failure counts, and success rate.
2) **Verify PG row count** — this run's rows = `(SELECT count(*) FROM content_gen_article) - 742`.
   Success + failed should equal 1000. Batch dir should have `2 × successes` files (.md + .json).
3) **If failure rate is still high (>20%)**, the bottleneck is Azure OpenAI rate limits.
   Consider reducing `--num-workers` to 20–30 to stay within TPM/RPM. The optimal worker
   count balances throughput vs rate-limit pressure.
4) **If `APIConnectionError` failures persist** after retry fix, the httpx connection pool
   may need tuning (`reuse_client=False` on AzureOpenAI) or worker count reduction.
5) **P2 remaining** — verify N=25 (flush boundary), N=30 (partial flush), then N=1500.

Constraints:
- Do not modify prompts/spec files unless user confirms.
- Python is uv-managed: `UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv"`.
- The LlamaIndex `llm_retry_decorator` has a hardcoded `stop_after_delay_seconds=60`
  that cannot be changed. Our outer `acomplete_with_backoff` compensates for this.
