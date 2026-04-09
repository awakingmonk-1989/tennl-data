# Insight card batching — implementation detail

**Purpose:** Single source of truth for how insight-card batch generation works after the 2026-04 session (category-scoped batches, sampling, CLI, outputs, parallel behavior, and verification). Written for future agents and operators.

**Related code:** [`python/tennl/batch/src/tennl/batch/generator/insight_cards/insight_card_llamaindex_orchestrator.py`](../../python/tennl/batch/src/tennl/batch/generator/insight_cards/insight_card_llamaindex_orchestrator.py)  
**Shell driver (multi-category, `_batch_seq`):** [`scripts/insight_cards/insight_card_batch_gen_batch_seq.sh`](../../scripts/insight_cards/insight_card_batch_gen_batch_seq.sh) (§6)  
**Run monitor (optional):** [`scripts/insight_cards/monitor_gemini_batch_runs.sh`](../../scripts/insight_cards/monitor_gemini_batch_runs.sh) (§6.8)  
**UI / layout spec:** [`insight_card_ui_skeleton_spec.md`](./insight_card_ui_skeleton_spec.md)  
**Seed data (categories, themes, pools):** packaged `tennl.batch` resource `resources/insight-cards/insight_card_config.json`  
**Prompts / generation defaults:** packaged `resources/insight-cards/insight-card-settings.yaml` via `AppSettings.shared.insight_cards`

---

## 1. Session outcomes and non-negotiables

### 1.1 Product decisions (stakeholder)

- **One CLI process = one seed category.** There is **no** rotation across multiple `categories` keys inside a single orchestrator invocation.
- **`--category` is mandatory** for every run. There is **no** YAML default and **no** auto-pick when multiple categories exist. Omitting or misspelling category → **fail fast** with a logged error and **non-zero exit** (after seed load + validation).
- **Multi-category coverage** is **out of scope for the Python CLI** in this design: use **external orchestration** (shell loop, CI matrix, etc.) with **one invocation per category**.
- **Existing global sampling axes** (`hook_type`, `register` / tone, `opening_word_class`, `title_style`, `avoid_titles`) keep the **`SlotRotator` + `worker_id` offset** pattern: long-lived rotators on the sampler instance, **`.next()` on every `sample()`**.
- **`theme` and `human_context`** use **long-lived** `SlotRotator` instances over **that category’s** `themes` and `human_contexts` arrays, with **`.next()` every `sample()`**, so they **advance across cards** within a batch (unlike the pre-change behavior of a fresh rotator + single `next()` per sample).
- **No merging** of category pools: themes/contexts always come from the **selected** category’s object in JSON only.

### 1.2 Concurrency and thread safety

- **`SlotRotator` is not thread-safe** (mutable counter on the instance).
- **No locks** in current design: **each parallel future** builds its **own** `InsightCardVariableSampler` and never shares it across threads.
- **Do not** share one sampler across threads; if code is refactored to pool workers differently, add synchronization or per-thread samplers.

### 1.3 Uniqueness / collisions (prompt variables)

- Variable tuples are built from **independent modular rotations** per slot (indices modulo list lengths). This is **not** a guarantee of enumerating the full Cartesian product of all pools.
- **Expect repeated prompt vectors** when `count` is large relative to pool sizes or when offsets align modulo lengths.
- **Output deduplication** (`_log_card`): dedupes **successful** cards by **fingerprint** (`title` + `content` hash), not by input variables. LLM could still produce different titles for similar prompts.
- **Dry-run** cards often share the same fingerprint (`[DRY RUN]`, empty `content`) → only one may appear in the returned **unique success list** even when `count > 1`; generation still ran `count` times (check logs / variables if needed).

### 1.4 Removed / not written

- **No aggregate** `insight_cards_output.json` (or configurable `generation.output_file`) write from the orchestrator; per-card artifacts only (see §4).
- **Python orchestrator** has **no** multi-category flag (`--categories A,B,C`); multi-category runs use **external** drivers. The repo provides **[`scripts/insight_cards/insight_card_batch_gen_batch_seq.sh`](../../scripts/insight_cards/insight_card_batch_gen_batch_seq.sh)** (see §6) — still **one** `uv`/`python` process per category, never overlapping categories at the shell level.

### 1.5 Parallel futures robustness (implemented)

- Each completed future uses **`Future.result(timeout=...)`** (default **120 s**, override **`--future-result-timeout-s`**).
- **CancelledError**, **TimeoutError**, and other **BaseException** paths are logged with worker index; summary line when any failures occur.

---

## 2. Data sources

| Source | Role |
|--------|------|
| **`insight_card_config.json`** (packaged) | `categories` map: each key is a valid `--category`. Per category: `themes[]`, `human_contexts[]`. Global pools: `hook_types`, `registers`, `opening_word_classes`, `title_style_hints.styles`, etc. |
| **`insight-card-settings.yaml`** (packaged, merged in `AppSettings`) | `generation.count`, `max_workers`, `prompt_version`, formatter + prompt templates. |
| **`app.yaml` + env** | LLM provider; active provider via `TENNL_LLM_PROVIDER` (see repo docs). |

Category names must match JSON keys **exactly** (e.g. `Urban Life`, `Finance`). Validation lists known keys on error.

---

## 3. Batching logic (deep dive)

### 3.1 Entrypoint and validation

1. Load optional `secrets.txt` into environment (repo root discovery).
2. Parse CLI (see §5).
3. **`load_packaged_seed_config()`** → dict.
4. **`validate_insight_card_category(seed, args.category)`** → raises `ValueError` if unknown → **`main` logs and `sys.exit(1)`**.
5. **`allowed_categories = [args.category]`** (length 1) passed into **`run_sequential`** or **`run_parallel`**.

### 3.2 `InsightCardVariableSampler`

**Constructor:** `InsightCardVariableSampler(seed, worker_id=0, *, allowed_categories: list[str])`

- **Requires** `len(allowed_categories) == 1` and that name exists under `seed["categories"]`.
- **Stores** `self._fixed_category` = that name.
- **Global rotators** (one `SlotRotator` each, all advance on each `sample()`):
  - `hook_type` ← `hook_types`, offset `worker_id + 1`
  - `register` ← `registers`, offset `worker_id + 2`
  - `opening_word_class` ← `opening_word_classes`, offset `worker_id + 3`
  - `title_style` ← `title_style_hints.styles`, offset `worker_id + 8`
- **Per-category rotators** (from **fixed** category’s pools):
  - `_theme_rotator` ← `themes`, offset `worker_id`
  - `_context_rotator` ← `human_contexts`, offset `worker_id`

**`sample()`:**

1. Advance all global rotators once each; build `v` with keys `hook_type`, `register`, `opening_word_class`, `title_style` (mapped to tone fields per existing rules).
2. Set `v["category"] = self._fixed_category`.
3. `v["theme"] = self._theme_rotator.next()`, `v["human_context"] = self._context_rotator.next()`.
4. `v["topic"] = f"{theme} in the context of {human_context}"`.
5. `avoid_titles` string from config.

**`SlotRotator` behavior** (see `tennl.batch.util.slot_rotater`): `next()` returns `values[(counter + offset) % len(values)]` and increments `counter`.

### 3.3 Sequential mode — `run_sequential`

- **One** `InsightCardVariableSampler(seed, worker_id=0, allowed_categories=...)`.
- Loop **`i` in `range(count)`**: `variables = sampler.sample()` → **`generate_one_card(...)`**.
- Effect: **same** `worker_id` for all cards → global + theme + context **all advance** monotonically across the batch (as intended).

### 3.4 Parallel mode — `run_parallel`

- **`ThreadPoolExecutor(max_workers=max_workers)`**.
- For each **`i` in `range(count)`**: submit **`task(i)`** where `task` builds **`InsightCardVariableSampler(seed, worker_id=i, allowed_categories=...)`**, **`sample()` once**, then **`generate_one_card`**.
- **Completion order** is nondeterministic (`as_completed`); **variables** for card `i` depend only on **`i`**, not on completion order.
- Each task: **one** `sample()` → theme/context are **first step** of that worker’s rotators; diversity across the batch comes from **different `i`**, not from multiple samples on the same sampler.

### 3.5 Single card pipeline — `generate_one_card`

- Merges `static_vars` (layout library blocks from formatter) with `variables`, renders prompts, calls **`llm.chat`** (not structured wrapper in this path), parses JSON to **`InsightCard`**, layout soft-validation, token metadata in `result.metadata`.
- Errors → **`InsightCardResult`** with `error` set; **no** exception escaping for normal LLM/parse failures.

### 3.6 Result aggregation and dedup

- **`_log_card(card, idx, seen, results)`**: on error, log warning; on success, fingerprint dedup; append unique successes to **`results`**.
- **`_log_batch_summary`**: token totals over **logged** results (unique successes).

### 3.7 When artifacts are written

- **`save_card_artifacts(result, output_dir)`** is called only when **`output_dir`** is set and **`not card.error`** (and after parallel future success path / sequential iteration).

---

## 4. Output directory and file naming (authoritative)

**This section is the canonical description of on-disk outputs.**

### 4.1 Base directory

- **Default:** `output/insight_cards` (relative to the **process current working directory** when the script runs).
- **Override:** CLI **`--output-dir <path>`** (any string path; created if missing).

**Typical run:** from `python/tennl/batch` so outputs land under **`python/tennl/batch/output/insight_cards`** unless you pass an absolute path or run from another cwd.

### 4.1.1 Shell batch driver output layout (differs from orchestrator default)

The **[`insight_card_batch_gen_batch_seq.sh`](../../scripts/insight_cards/insight_card_batch_gen_batch_seq.sh)** driver does **not** use `python/tennl/batch/output` as the root for card triples. It passes an **absolute** `--output-dir` per category under **repository-root** `output/`:

- **Parent:** `{REPO_ROOT}/output/gemini_batch_runs` (override with env **`GEMINI_BATCH_RUNS_PARENT`**).
- **Per script invocation:** one subdirectory **`run_<YYYYMMDD_HHMMSS>/`** (timestamp generated once at startup; second resolution).
- **Inside each run:** `insight_batch_logs_batch_seq/` (category logs) and `insight_cards_<slug>/` (card triples per seed category), same file naming as §4.3–§4.4.

So a full multi-category batch produces one isolated tree, e.g. `output/gemini_batch_runs/run_20260409_040538/insight_cards_Psychology/`, without mixing prior runs.

### 4.2 When files are created

- **Only when** `output_dir` is set **and** `not card.error` (includes **dry-run**, which sets `error=None`).
- To avoid writing files during dry-run, **omit `--output-dir`** (or point to a throwaway path you delete afterward). There is no separate `--no-save` flag today.

### 4.3 Triple per card (shared prefix)

For each saved card, **three files** share one **prefix**:

| File | Suffix | Contents |
|------|--------|----------|
| Card JSON | `{prefix}.json` | `InsightCardResult.model_dump()` **excluding** `raw`, `metadata`, `provider`, `error` (structured card fields for UI/pipeline). |
| Raw LLM | `{prefix}_raw.json` | `metadata["raw_response"]` (serialized provider response). |
| Tokens | `{prefix}_tokens.json` | `metadata["token_usage"]` (prompt/completion/total, provider-specific shape). |

### 4.4 Prefix construction (exact algorithm)

From **`save_card_artifacts`**:

1. `model_label = result.metadata.get("model", "unknown")` if metadata else `"unknown"`.
2. `safe_model = re.sub(r"[^a-zA-Z0-9_]", "_", model_label)` — non-alphanumeric → underscore.
3. `ts_ms = int(time.time() * 1000)` — **milliseconds** at write time (cards written in quick succession can differ; parallel writes may collide in theory if same ms and model — rare).
4. **`prefix = f"insight_card_{safe_model}_{ts_ms}"`**

**Examples:**

- `insight_card_gpt_4o_1775654123456.json`
- `insight_card_gpt_4o_1775654123456_raw.json`
- `insight_card_gpt_4o_1775654123456_tokens.json`

(Log line format: `Saved 3 artifacts: {output_dir}/{prefix}{.json,_raw.json,_tokens.json}`)

---

## 5. CLI reference

| Argument | Required | Description |
|----------|----------|-------------|
| **`--category`** | **Yes** | Exact key under `categories` in seed JSON. |
| `--mode` | No | `sequential` (default) or `parallel`. |
| `--count` | No | Overrides packaged YAML `generation.count`. |
| `--workers` | No | Overrides `generation.max_workers` (parallel only). |
| `--output-dir` | No | Base directory for triples (default `output/insight_cards`). |
| `--future-result-timeout-s` | No | Parallel only; default `120`. |
| `--version` | No | Insight prompt pack version (e.g. `large`). |
| `--dry-run` | Flag | No LLM call; prompt preview in `result.raw`. |

Provider: **`TENNL_LLM_PROVIDER`** + `app.yaml` (see batch package docs).

---

## 6. Shell batch driver — `insight_card_batch_gen_batch_seq.sh`

**Path (repo root relative):** [`scripts/insight_cards/insight_card_batch_gen_batch_seq.sh`](../../scripts/insight_cards/insight_card_batch_gen_batch_seq.sh)

**Suffix `_batch_seq` meaning:** **Sequential at the category level** — the script starts **at most one** insight-card orchestrator **process** at a time. When category *A* finishes (success or failure recorded), the script starts category *B*. It does **not** spawn *N* parallel shell jobs for *N* categories (avoids many processes hammering disk with triple-writes and reduces risk of IO-related loss under heavy concurrent writes).

**Rationale (operational):** Per-card persistence is **inside** the orchestrator (`save_card_artifacts` per successful card). Overlapping **multiple** full batch processes (one per category) in parallel can stress disk and complicate failure analysis. **Within** each category run, the orchestrator still uses **`--mode parallel --workers W`** so LLM calls are concurrent; only **cross-category** execution is serialized by this script.

### 6.1 How categories are discovered (`jq`)

- **Config file read by the script (source of truth for the list):**  
  `{REPO_ROOT}/python/tennl/batch/src/tennl/batch/resources/insight-cards/insight_card_config.json`
- **Query:** `jq -r '.categories | keys[]' "$CONFIG_JSON"`
- **Semantics:** In JSON, **`categories`** is an **object**. Each **property name** (key) is a **category** name — e.g. `Finance`, `Urban Life`. Those keys are exactly what you pass to the Python CLI as **`--category`**.
- **Categories vs “topics”:** In this codebase, **seed “topics” for batching** are these **category keys**. The string **`Topic:`** inside the prompt is a **different** concept: `"{theme} in the context of {human_context}"` sampled from that category’s pools (see §11 Glossary). Do not confuse with article workflow `topics.json`.

### 6.2 Does the script iterate all categories?

**Yes**, when you **do not** pass a positional category:

1. After parsing flags, **`SINGLE_CATEGORY`** is empty.
2. The script fills **`CATEGORIES`** by reading **every line** from `jq -r '.categories | keys[]'`.
3. It runs **`for cat in "${CATEGORIES[@]}"; do run_one_category "$cat"; done`**, waiting for each orchestrator run to exit before starting the next.

**If you pass one positional argument** (e.g. `Finance`), only that category is run — useful for spot checks or reruns.

**Order of categories:** `jq`’s **`keys`** operator returns keys in **lexicographic sort order**, not necessarily the order keys appear in the file. To preserve JSON insertion order you would change the script to use **`keys_unsorted`** (not the default today).

**Count of categories:** The number of categories is **whatever** the JSON contains (e.g. **11** keys in a recent snapshot: Culture, Finance, History, Life, Mindfulness, Psychology, Science, Technology, Travel, Urban Life, Wellness). **Re-run** `jq -r '.categories | keys[]'` after editing the seed file.

**Portability:** The script avoids **`mapfile`** so it runs on **macOS bash 3.2**; it uses a **`while read`** loop over process substitution.

### 6.2.1 Category exclusions (shell driver)

When **no** positional category is passed, the script **filters** the `jq` list using an in-script bash array **`EXCLUDE_CATEGORIES`** (exact string match to JSON keys, including spaces such as `Urban Life`).

- **Purpose:** Skip a fixed subset of seed categories on “run all” without editing `insight_card_config.json`.
- **Current defaults (edit the script to change):** `Culture`, `Finance`, `History`, `Life`, `Mindfulness`. The remaining keys (e.g. Psychology, Science, Technology, Travel, Urban Life, Wellness) are processed in `jq` order.
- **Positional override:** If you pass **one** category on the CLI, exclusions are **not** applied — you can still run an excluded category by name.
- If every category is excluded, the script exits with an error (`no categories left after exclusions`).

The banner prints **`excluded:`** and the final **`categories:`** list for each invocation.

### 6.3 Script arguments and defaults

| Input | Meaning |
|--------|---------|
| **(positional)** optional `CATEGORY` | If present, **only** this category; must match a `categories` key exactly (orchestrator validates). |
| **`-n` / `--count` N** | Cards per category; default **100**. |
| **`-w` / `--workers` W** | Passed to orchestrator **`--workers`**; default **5**. Orchestrator **`--mode parallel`** is always used by the script. |
| **`--dry-run`** | Forwarded to orchestrator; no LLM calls. |
| **`-h` / `--help`** | Prints script header comment block. |

**Flag / positional ordering:** Both `./script.sh Finance -n 10` and `./script.sh -n 10 Finance` work: the parser consumes flags and assigns the first non-flag token to the single category.

**Dependencies:** `bash`, **`jq`**, **`uv`**. **`UV_PROJECT_ENVIRONMENT`** defaults to **`{REPO_ROOT}/python/tennl/batch/.venv`** if unset.

### 6.4 Environment variables (shell driver)

| Variable | Behavior |
|----------|----------|
| **`TENNL_LLM_PROVIDER`** | The script **`export`s `litellm`** by default. Without this, `AppSettings.pick_provider()` can fall back to **`azure-foundry-openai`** when the env var is unset elsewhere — so the driver pins LiteLLM for batch runs. Gemini model and temperature come from packaged **`app.yaml`** under the `litellm` provider (currently **`gemini/gemini-3.1-flash-lite-preview`**, **`temperature: 1`** for Gemini 3.x). |
| **`GEMINI_BATCH_RUNS_PARENT`** | Parent directory for **`run_<stamp>/`** trees. Default: **`{REPO_ROOT}/output/gemini_batch_runs`**. |
| **`UV_PROJECT_ENVIRONMENT`** | Virtualenv for `uv run`; default **`{REPO_ROOT}/python/tennl/batch/.venv`**. |

### 6.5 Paths resolved by the script

| Variable | Value |
|----------|--------|
| **`REPO_ROOT`** | From script location: `scripts/insight_cards/../../` (repository root). |
| **`BATCH_DIR`** | `{REPO_ROOT}/python/tennl/batch` — **`cd`** here before **`uv run`**. |
| **`GEMINI_BATCH_RUNS_PARENT`** | Default `{REPO_ROOT}/output/gemini_batch_runs` (see §6.4). |
| **`RUN_STAMP`** | `date +%Y%m%d_%H%M%S` — computed **once** per script invocation. |
| **`RUN_ROOT`** | `{GEMINI_BATCH_RUNS_PARENT}/run_{RUN_STAMP}` — root for **this** batch run. |
| **`LOG_DIR`** | `{RUN_ROOT}/insight_batch_logs_batch_seq`. |
| **Per-category `--output-dir`** | `{RUN_ROOT}/insight_cards_<slug>` where **`slug`** = category with spaces → underscores (`Urban Life` → `Urban_Life` in the folder name: `insight_cards_Urban_Life`). |
| **Per-category log file** | `{LOG_DIR}/{slug}_YYYYMMDD_HHMMSS.log` — **new file each category** (timestamp in filename). |

Artifact **triples** under each `insight_cards_<slug>/` follow §4.3–§4.4 (`insight_card_{safe_model}_{ts_ms}.json`, `_raw.json`, `_tokens.json`).

**Operator note:** For long runs, it is common to **`tee`** driver stdout to e.g. `output/gemini_batch_runs/driver_n100_w5_<stamp>.log`; the script does not create that file by itself.

### 6.6 What the script passes to the orchestrator (each category)

Each invocation is equivalent to:

```text
export TENNL_LLM_PROVIDER=litellm   # default; omitted if already set in environment
cd python/tennl/batch
uv run python -m tennl.batch.generator.insight_cards.insight_card_llamaindex_orchestrator \
  --category "<CategoryName>" \
  --count <COUNT> \
  --mode parallel \
  --workers <WORKERS> \
  --output-dir "<RUN_ROOT>/insight_cards_<slug>" \
  --future-result-timeout-s 120 \
  [--dry-run]
```

`<RUN_ROOT>` is the absolute path to `run_<YYYYMMDD_HHMMSS>/` for that script invocation (see §6.5).

### 6.7 Progress monitoring (inside the script)

- The orchestrator runs as a **background subprocess**; **stdout/stderr** are appended to the **category log file**.
- A **second background loop** runs while the orchestrator PID is alive: **every 5 seconds** it prints a **timestamp**, the **category name** and **PID**, and the **last 15 lines** of the log (or “log empty yet”).
- After the orchestrator exits, the script prints **exit code** and the **last 40 lines** of the log.

### 6.8 External monitor helper — `monitor_gemini_batch_runs.sh`

**Path:** [`scripts/insight_cards/monitor_gemini_batch_runs.sh`](../../scripts/insight_cards/monitor_gemini_batch_runs.sh)

- Resolves the **latest** `run_*` under **`GEMINI_BATCH_RUNS_PARENT`** (default `{REPO_ROOT}/output/gemini_batch_runs`) unless you pass a run directory explicitly.
- Prints per-folder counts of **main** card JSON files (excludes `*_raw.json` / `*_tokens.json`), a hint if batch/orchestrator PIDs are running, and optionally **`tail`** of the newest category log in that run.

```bash
# From repo root — one snapshot
./scripts/insight_cards/monitor_gemini_batch_runs.sh

# Refresh every 10 seconds
./scripts/insight_cards/monitor_gemini_batch_runs.sh -w 10

# Snapshot + last 20 lines of newest category log
./scripts/insight_cards/monitor_gemini_batch_runs.sh -t 20

# Watch a specific run directory
./scripts/insight_cards/monitor_gemini_batch_runs.sh -w 15 output/gemini_batch_runs/run_20260409_040538
```

### 6.9 Exit behavior

- If **any** category run returns non-zero, the script **continues** remaining categories but sets a **failure flag** and exits **1** at the end.
- If **all** succeed, exits **0**.

### 6.10 Known limitations (see also tasks doc)

- **No automatic retries** for provider **rate limits** or transient API errors in the script or orchestrator; failures surface in logs; operator must rerun or add tooling later ([`tasks/2026-04-09-insight-card-batch-next-steps.md`](../../tasks/2026-04-09-insight-card-batch-next-steps.md)).

### 6.11 Example script invocations

```bash
# Repo root — all categories from jq after EXCLUDE_CATEGORIES filter, 100 cards, 5 workers
./scripts/insight_cards/insight_card_batch_gen_batch_seq.sh

# Same with explicit counts / workers
./scripts/insight_cards/insight_card_batch_gen_batch_seq.sh -n 100 -w 4

# Single category (exclusions NOT applied)
./scripts/insight_cards/insight_card_batch_gen_batch_seq.sh -n 50 -w 5 Technology

# Smoke: filtered “all” list, 1 card each, no API
./scripts/insight_cards/insight_card_batch_gen_batch_seq.sh -n 1 --dry-run

# Long run with driver log on disk (optional)
./scripts/insight_cards/insight_card_batch_gen_batch_seq.sh -n 100 -w 5 2>&1 | tee output/gemini_batch_runs/driver_$(date +%Y%m%d_%H%M%S).log

# Inspect raw jq keys (before script exclusions)
jq -r '.categories | keys[]' python/tennl/batch/src/tennl/batch/resources/insight-cards/insight_card_config.json
```

---

## 7. Direct orchestrator commands (without the shell driver)

Use when debugging a **single** category or bypassing the script.

**Environment (repo convention):**

```bash
cd /Users/devansh/tennl-data/python/tennl/batch
export UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv"   # or absolute path to .venv
```

**Module invocation (sequential orchestrator mode):**

```bash
uv run python -m tennl.batch.generator.insight_cards.insight_card_llamaindex_orchestrator \
  --category Finance \
  --count 10 \
  --mode sequential \
  --output-dir output/insight_cards_finance
```

**Parallel inside orchestrator (e.g. 4 workers):**

```bash
uv run python -m tennl.batch.generator.insight_cards.insight_card_llamaindex_orchestrator \
  --category Technology \
  --count 50 \
  --mode parallel \
  --workers 4 \
  --output-dir output/insight_cards_technology \
  --future-result-timeout-s 120
```

**Dry-run (smoke, no API cost):**

```bash
uv run python -m tennl.batch.generator.insight_cards.insight_card_llamaindex_orchestrator \
  --category Finance \
  --count 2 \
  --dry-run
```

**Manual multi-category loop (prefer `_batch_seq.sh` instead):** derive the list from **`jq`** so it never drifts from the JSON. If you mirror the driver’s layout, use a shared **`RUN_ROOT`** and paths as in §6.5 instead of `python/tennl/batch/output/...`:

```bash
CONFIG="python/tennl/batch/src/tennl/batch/resources/insight-cards/insight_card_config.json"
COUNT=100
WORKERS=4
while IFS= read -r cat; do
  [[ -z "$cat" ]] && continue
  safe="${cat// /_}"
  ( cd python/tennl/batch && UV_PROJECT_ENVIRONMENT=".venv" uv run python -m tennl.batch.generator.insight_cards.insight_card_llamaindex_orchestrator \
    --category "$cat" --count "$COUNT" --mode parallel --workers "$WORKERS" \
    --output-dir "output/insight_cards_${safe}" --future-result-timeout-s 120 )
done < <(jq -r '.categories | keys[]' "$CONFIG")
```

---

## 8. Verification performed (session)

- **Unit tests:** `uv run python -m unittest tests.test_insight_card_orchestrator -v` (batch package root).
- **Unknown category:** `--category NotRealCategory` → exit non-zero and error listing valid names.
- **Sequential sampling:** two `sample()` calls on one sampler with `allowed_categories=["Finance"]` showed advancing `theme`/`human_context`; Technology used its own `human_contexts` ordering for the second draw.
- **Dry-run:** CLI runs with `--dry-run` for Finance/Technology.
- **Shell script:** `insight_card_batch_gen_batch_seq.sh` exercised with `-n 1 --dry-run` for a single category and for the **filtered** all-categories list (`EXCLUDE_CATEGORIES` when no positional category); confirms **sequential iteration** (see §6.2, §6.2.1). Outputs under **`output/gemini_batch_runs/run_<stamp>/`** (§4.1.1, §6.5).

---

## 9. Tests and documentation touched (codebase)

- **Tests:** [`python/tennl/batch/tests/test_insight_card_orchestrator.py`](../../python/tennl/batch/tests/test_insight_card_orchestrator.py) — `allowed_categories`, `_tech_sampler` helper, `FakeLLM.chat` / chat response shape, `InsightCard` includes `layout` + `content_blocks` where needed.
- **Doc:** [`python/tennl/batch/docs/LITELLM_GEMINI_INTEGRATION_GUIDE.md`](../../python/tennl/batch/docs/LITELLM_GEMINI_INTEGRATION_GUIDE.md) — example updated to new sampler constructor.

---

## 10. Code module map (orchestrator)

| Symbol | Role |
|--------|------|
| `load_packaged_seed_config` | Packaged JSON seed. |
| `validate_insight_card_category` | CLI category validation. |
| `InsightCardVariableSampler` | Variable generation for one category batch. |
| `generate_one_card` | One LLM round-trip + parse. |
| `save_card_artifacts` | Write triple JSON files. |
| `run_sequential` / `run_parallel` | Batch loops. |
| `main` | CLI, wiring, logging. |

---

## 11. Glossary

- **Category (seed):** Key in `insight_card_config.json` → `categories`; passed as **`--category`**; **not** the article workflow `topics.json`.
- **Topic (prompt variable):** String `"{theme} in the context of {human_context}"` built from sampled slots.
- **Allowed categories:** Internal list of length 1; same as CLI category for production runs.

---

## 12. Optional future work (not implemented here)

- In-process multi-category driver / manifest file.
- Per-run correlation IDs in logs; optional JSON sidecar on parallel future failure.
- Thread-pool pre-warm; extended batch summary (submitted vs deduped vs LLM errors).
- **PostgreSQL loader** and **Azure Blob upload** for artifact triples — see [`tasks/2026-04-09-insight-card-batch-next-steps.md`](../../tasks/2026-04-09-insight-card-batch-next-steps.md).

---

*Document version: 2026-04-09 (rev. §4.1.1 + §6) — orchestrator, `output/gemini_batch_runs/run_<stamp>/`, LiteLLM default, exclusions, `monitor_gemini_batch_runs.sh`.*
