# Agentic Workflow — Progress & Handoff Guide
## `tennl.batch.workflows`
### Last updated: 2 April 2026

---

## Current Phase: Backend Dev — Workflow Creation (Phase 1 complete)

The LlamaIndex-based agentic content generation workflow is **functional
end-to-end**. It generates articles with deep dives, evaluates them via
LLM + deterministic checks, supports a bounded refine loop, and writes
output artifacts to disk. No persistence layer or structured logging
beyond the rolling JSONL trace file exists yet.

---

## What Is Done

### 1. Project scaffold & environment

| Item | Status | Notes |
|------|--------|-------|
| Monorepo layout (`python/tennl/batch/`) | Done | uv-managed, Python 3.13 strict |
| Virtualenv at `python/tennl/batch/.venv` | Done | `UV_PROJECT_ENVIRONMENT` required |
| `pyproject.toml` with all deps | Done | llama-index-core, llms-azure-openai, etc. |
| Package namespace `tennl.batch.workflows` | Done | Importable, CLI-runnable |

### 2. LLM provider factory

| Item | Status | Notes |
|------|--------|-------|
| `resources/llms.yaml` config | Done | openai, litellm, azure-foundry-openai |
| `AppSettings.shared` singleton | Done | YAML-driven, env-var overridable |
| `llm_factory.py` | Done | Builds LlamaIndex LLM per provider config |
| Azure OpenAI default | Done | `gpt-5.4-mini` deployment, key from `secrets.txt` |

### 3. Workflow stages (LlamaIndex Workflows)

All stages implemented in `python/tennl/batch/workflows/`:

| Stage | Node | File | What it does |
|-------|------|------|--------------|
| Input validation | N1 | `stages/input_validation.py` | Pydantic validation of topic/sub_topic/variant |
| Content generation | N2 | `stages/generator.py` | Real LLM call with full prompt + specs + sample reference |
| Evaluation gate | N3 | `workflow.py` (inline) | Routes to moderation eval |
| Moderation eval | N4 | `stages/moderation_eval.py` | LLM safety check (Pass 1) |
| Quality + schema eval | N5 | `stages/quality_eval.py` + `stages/schema_validation.py` | LLM quality scoring + deterministic schema + structural checks |
| Eval merge | N6 | `stages/eval_merge.py` | PROCEED / REFINE / FAIL routing |
| Refiner | N7 | `stages/refiner.py` | Builds typed `RefinementDirectives` |
| Regeneration | N8 | `workflow.py` (reuses N2) | Re-generates with directives + original prompt |
| Final validation | N9 | `stages/final_validation.py` | Output integrity + schema re-check |

### 4. Typed event & model system

| Item | Status | Notes |
|------|--------|-------|
| Pydantic models for all reports | Done | `models.py` — ModerationReport, QualityReport, SchemaReport, MergedEvalReport, RefinementDirectives |
| LlamaIndex Event subclasses | Done | `events.py` — typed payloads, no loose dicts |
| RunState (workflow context) | Done | Tracks articles, reports, refine attempts |

### 5. Prompts & prompt template system

| Prompt | File | Purpose |
|--------|------|---------|
| Content generation (legacy) | `prompts/conten_gen_prompt_page_post.md` | Full article generation prompt (loaded via `{prompt}` placeholder in `content_gen_base` template) |
| Content generation (novelty) | `resources/prompts.yaml` → `content_gen_novelty_v1` | Self-contained inline prompt (Parts 0-8) with creative controls + anti-drift rules |
| Moderation eval | `prompts/eval_pass1_moderation_prompt.md` | Safety evaluation prompt |
| Quality eval | `prompts/eval_pass2_quality_prompt.md` | Narrative quality scoring |
| Refinement | `prompts/refine_prompt.md` | Regeneration with failure context |

**Prompt template system** (added 2 Apr 2026):

| Component | File | What it does |
|-----------|------|--------------|
| `PromptTemplate` model | `settings.py` | Pydantic model for 4-block prompt structure (`system_prompt`, `runtime_input_block`, `output_block`, `attachments_block`). `model_validator` enforces all blocks non-empty when `name` is set. |
| `PromptSettings` | `settings.py` | Holds named template variants (`content_gen_base`, `content_gen_novelty_v1`). Loaded via `AppSettings` with env > .env > YAML > defaults precedence. |
| `prompts.yaml` | `resources/prompts.yaml` | Declarative YAML prompt templates. `content_gen_base` uses `{prompt}` placeholder for the legacy `.md` file. `content_gen_novelty_v1` is fully self-contained with inline Parts 0-8 and anti-drift/control-interpretation rules in `runtime_input_block`. |
| `QualityConstraints` | `models.py` | Frozen pydantic model: `must_include` + `avoid` lists for creative control constraints. |
| `PromptRuntimeInput` | `models.py` | Frozen pydantic model: typed, immutable input contract for prompt rendering. Replaces raw `dict[str, Any]`. Fields: topic metadata, pool lists, selected creative controls, file-loaded assets (specs, skills, samples). |
| `validate_runtime()` | `stages/generator.py` | Pool-membership checks (content_mode, angle, tone, hook_style vs their pools). Skips silently when pools are empty. |
| `build_prompt_runtime_input()` | `stages/generator.py` | Factory: maps `WorkflowInput` + `_esc()`'d file assets → frozen `PromptRuntimeInput`. |
| `format_prompt()` | `stages/generator.py` | Assembles 4 template blocks from typed `PromptRuntimeInput`. Normalizes values, builds optional sample blocks, applies `str.format()`. |
| `_esc()` | `stages/generator.py` | Escapes `{`/`}` in file-loaded content to prevent `str.format()` collisions. |

**Data flow (generation path):**
```
WorkflowInput → _load_shared_assets() → build_prompt_runtime_input() → PromptRuntimeInput (frozen)
  → validate_runtime() (pool checks) → format_prompt(template, inp) → final prompt string
```

### 6. Reference samples

| File | Purpose |
|------|---------|
| `resources/sample_output_reference.md` | Sample article markdown (with deep dives) |
| `resources/sample_output_reference.json` | Sample article JSON (stripped of post_html_content) |

Both are included in generation + refinement prompts as structural anchors.

### 7. Tracing

| Item | Status | Notes |
|------|--------|-------|
| Rolling JSONL logger | Done | `logs/workflow_traces.jsonl` (5 MB rotate, 5 backups) |
| Per-stage trace entries | Done | node_id, duration_ms, result, output_summary |
| LlamaIndex instrumentation | Done | Span enter/exit/drop + event forwarding |

### 8. CLI & output

```bash
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run python -m tennl.batch.workflows \
  --topic "Home & Living" \
  --sub-topic "Interior Styling Ideas" \
  --content-variant AI_GENERATED \
  --eval-mode sequential
```

Outputs: `out/{run_id}/article.md` + `out/{run_id}/article.json`

CLI prints execution trace summary + article stats (word count, sections,
deep dive count) after each run.

---

## Known Limitations (current state)

1. **No persistence** — run state, execution history, and articles exist
   only on the filesystem (`out/`, `logs/`). No DB, no structured query.
2. **No structured logging** — only the rolling JSONL trace file. No log
   levels, no correlation IDs beyond run_id, no external sink.
3. **Quality eval is partially heuristic** — the LLM quality scorer runs
   but the deterministic heuristic scorer (`_heuristic_quality_scores`)
   is still a placeholder that assigns flat scores.
4. **No retry / circuit-breaker on LLM calls** — a single transient API
   failure fails the entire run.
5. **sub_topic_description is hardcoded** — the generator passes a fixed
   string; should be looked up from a topic registry or input payload.
6. **Structural checks are lenient** — `sections` accepted as alias for
   `posts`; `deep_dives` not required as a separate root key (LLM puts
   them inside `sub_sections`).
7. **`content_gen_base` still references external `.md` prompt** — the
   `{prompt}` placeholder loads `prompts/conten_gen_prompt_page_post.md`
   at runtime. `content_gen_novelty_v1` is fully self-contained.
8. **`WorkflowInput` lacks creative control fields** — `intent_profile`,
   `content_mode_pool`, `angle_pool`, `tone_pool`, `hook_style_pool`,
   `content_mode`, `angle`, `tone`, `hook_style` are not yet on
   `WorkflowInput`. `build_prompt_runtime_input()` uses `getattr()`
   defaults until CLI and `WorkflowInput` are extended.
9. **CLI not yet updated for prompt template selection** — the workflow
   always uses `content_gen_base`. Switching to `content_gen_novelty_v1`
   requires CLI + `WorkflowInput` changes (deferred per user instruction).

---

## Next Steps (TODOs for next agent)

### Immediate: End-to-end dry run

- [ ] **Run the full workflow end-to-end** — execute the CLI command below,
  verify all 9 stages complete without errors, and confirm output artifacts
  (`out/{run_id}/article.md` + `article.json`) are written correctly.
- [ ] **Verify Azure Storage persistence** — if the Azure storage integration
  from the previous dry run (see `specs/data/azure/azure_storage_content_gen_pipeline_progress.md`)
  is still wired in, confirm blob + table entities are written.
- [ ] **Test with `content_gen_novelty_v1` template** — once CLI supports
  template selection, run with the novelty template and verify creative
  controls flow through correctly.

### Phase 2: Persistence & Logging

- [ ] **Design persistence layer** — decide on SQLite vs Postgres for
  `Workflow`, `WorkflowExecution`, `Article` tables. Reference the
  original HLD data model spec at
  `workflow/specs/workflow_data_model_spec.md`.
- [ ] **Implement run history store** — persist run_id, status, input,
  output refs, execution trace, timestamps. Query past runs.
- [ ] **Cold storage for artifacts** — move `out/{run_id}/` artifacts to
  a configured cold store (local filesystem for dev, S3/GCS for prod).
- [ ] **Structured logging** — replace print statements with proper
  Python logging (structured JSON, log levels, correlation via run_id).
  Consider integrating with OpenTelemetry for spans.
- [ ] **Observability dashboard** — surface run success rate, avg
  duration per stage, refine loop frequency, common failure reasons.

### Phase 3: Quality & Robustness

- [ ] **Replace heuristic quality scorer** — wire the LLM quality eval
  as the sole quality signal; remove the placeholder heuristic scorer.
- [ ] **LLM call resilience** — add retry with exponential backoff,
  timeout per call, circuit breaker on repeated failures.
- [ ] **Topic registry** — load sub_topic_description from a config or
  API rather than hardcoding.
- [ ] **Batch runner** — accept a list of (topic, sub_topic) pairs and
  run them sequentially or with concurrency controls.
- [ ] **Prompt versioning** — track prompt file hashes in generation_meta
  so output is reproducible.

### Phase 4: Integration & Deployment

- [ ] **API layer** — expose the workflow as an HTTP endpoint (FastAPI or
  similar) for triggering runs from external systems.
- [ ] **CI/CD** — automated tests, lint, type-check in pipeline.
- [ ] **Config per environment** — dev / staging / prod configs for LLM
  provider, persistence backend, artifact storage.

---

## File Map

```
python/tennl/batch/
├── src/tennl/batch/
│   ├── resources/
│   │   ├── app.yaml                 # main LLM / provider config
│   │   ├── prompts.yaml             # declarative prompt templates (content_gen_base, content_gen_novelty_v1)
│   │   ├── sample_output_reference.md   # sample article markdown
│   │   └── sample_output_reference.json # sample article JSON
│   └── workflows/
│       ├── __init__.py              # exports ContentGenWorkflow, AppSettings
│       ├── __main__.py              # entry point for `python -m`
│       ├── cli.py                   # CLI arg parsing + output writing + trace summary
│       ├── workflow.py              # ContentGenWorkflow (LlamaIndex Workflow)
│       ├── events.py                # typed Event subclasses
│       ├── models.py                # pydantic models (RunState, reports, PromptRuntimeInput, QualityConstraints)
│       ├── settings.py              # AppSettings singleton, PromptTemplate, PromptSettings, YAML config loader
│       ├── llm_factory.py           # builds LlamaIndex LLM from provider config
│       ├── tracing.py               # rolling JSONL trace + LlamaIndex instrumentation
│       └── stages/
│           ├── input_validation.py  # N1
│           ├── generator.py         # N2 + N8 (prompt building, validation, rendering, LLM call)
│           ├── moderation_eval.py   # N4 (LLM safety + structural checks)
│           ├── quality_eval.py      # N5 (LLM quality + heuristic + schema)
│           ├── schema_validation.py # deterministic JSON structure checks
│           ├── eval_merge.py        # N6 (PROCEED / REFINE / FAIL router)
│           ├── refiner.py           # N7 (builds RefinementDirectives)
│           └── final_validation.py  # N9 (output integrity)
├── agent_workflow_progress.md       # ← this file
└── pyproject.toml                   # uv project config
```

---

## How to Run (quick start for next agent)

```bash
# From repo root
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run python -m tennl.batch.workflows \
  --topic "Home & Living" \
  --sub-topic "Interior Styling Ideas" \
  --content-variant AI_GENERATED \
  --eval-mode sequential \
  --timeout 300
```

Azure OpenAI key is read from `secrets.txt` at repo root.
LLM config is in `resources/llms.yaml`.
Sample reference articles are in `resources/sample_output_reference.{md,json}`.
