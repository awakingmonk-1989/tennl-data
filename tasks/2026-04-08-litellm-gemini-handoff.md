# LiteLLM Gemini Integration — Session Handoff
## Agent Session: April 8, 2026

---

## What Was Done This Session

### 1. Dependency verification
- Confirmed `litellm` and `llama-index-llms-litellm` are installed in the uv-managed venv at `python/tennl/batch/.venv/`
- Both were already declared in `pyproject.toml` (`llama-index-llms-litellm>=0.7.1`); `uv sync` resolved them

### 2. app.yaml — litellm provider configured for Gemini
- Changed `python/tennl/batch/src/tennl/batch/resources/app.yaml` litellm provider model from `anthropic/claude-sonnet-4-20250514` to `gemini/gemini-2.5-flash`
- Activate with `TENNL_LLM_PROVIDER=litellm`

### 3. InsightCardResult — added `metadata` field
- `python/tennl/batch/src/tennl/batch/domain/insight_cards.py`
- Added `metadata: Optional[dict[str, Any]] = Field(default=None)` to `InsightCardResult`
- Changed `model_config` from `extra="forbid"` to `extra="allow"` to support metadata

### 4. Orchestrator — fully implemented
- `python/tennl/batch/src/tennl/batch/generator/insight_cards/insight_card_llamaindex_orchestrator.py`
- **Added `_safe_serialize()`** — best-effort JSON-safe serialization of arbitrary objects (Pydantic models, dicts, etc.)
- **Added `_find_repo_root()` / `_load_secrets_env()`** — reads `secrets.txt` KEY=VALUE pairs into `os.environ` at runtime; walks up from `__file__` to find repo root via `.git` marker
- **Added `_strip_code_fences()`** — removes markdown code fences from Gemini JSON output before parsing
- **Added `--output-dir` CLI arg** — controls per-card file output directory
- **Added `save_card_artifacts()`** — writes triple-file output per card: `_card.json`, `_raw.json`, `_tokens.json` (replaced earlier placeholder `save_result_to_file`)
- **Added `_extract_litellm_token_metadata()`** — reads `response.raw["usage"]` into `LiteLLMGeminiTokenUsage` Pydantic model
- **Added `_extract_default_token_metadata()`** — reads `response.additional_kwargs` (for OpenAI-like providers)
- **Added `_extract_token_metadata()`** — provider-aware dispatcher
- **Added `_log_batch_summary()`** — aggregates token usage across batch results and logs totals
- **Updated `generate_one_card()`** — uses `llm.chat()` + `_strip_code_fences()` + `InsightCard.model_validate_json()` + token extraction + per-card logging; all inspection scaffolding removed
- **Updated `run_sequential` / `run_parallel`** — accept `output_dir` and `model_name`, call `save_card_artifacts`, call `_log_batch_summary`
- **Updated `main()`** — calls `_load_secrets_env()` at startup, passes `output_dir` and `model_name=llm_cfg.model` through

### 5. Domain models — token usage Pydantic types
- `python/tennl/batch/src/tennl/batch/domain/insight_cards.py`
- Added `CompletionTokensDetails` — maps `reasoning_tokens`, `text_tokens` from `usage.completion_tokens_details`
- Added `PromptTokensDetails` — maps `text_tokens`, `audio_tokens`, `cached_tokens`, `image_tokens`, `video_tokens` from `usage.prompt_tokens_details`
- Added `LiteLLMGeminiTokenUsage` — full token usage model: top-level counts + nested detail models + `cache_read_input_tokens`
- All three exported from `domain/__init__.py`

### 6. Investigation — LlamaIndex + LiteLLM response object hierarchy
Conducted thorough investigation of how token data flows through the stack. Key findings documented in `tasks/2026-04-08-litellm-gemini-spec.md`.

### 7. Live tests performed
- **Initial dry run** (`--dry-run --count 2`): confirmed prompts render correctly, metadata structure populates
- **Initial live Gemini run** (`--count 1`): confirmed LLM call succeeds, raw response dumped to `output/response_raw_dump.json`; token fields were `0` due to reading from `response.additional_kwargs` (always `{}` for LiteLLM — see spec)
- **Final dry run** (`--dry-run --count 2`): validated triple-file output (6 files), correct card/token/raw structure
- **Final live Gemini run** (`--count 2`): 6 output files, token counts fully populated including `reasoning_tokens`:
  - Card 1: prompt=382, completion=673 (reasoning=462, text=211), total=1055
  - Card 2: prompt=382, completion=1336 (reasoning=1094, text=242), total=1718
  - Batch summary: 764 prompt, 2009 completion, 2773 total

---

## Implementation Complete (All Steps Executed)

### Step 1 — Domain models for token usage (DONE)
Added `CompletionTokensDetails`, `PromptTokensDetails`, `LiteLLMGeminiTokenUsage` to `domain/insight_cards.py`. Exported from `domain/__init__.py`.

### Step 2 — Provider-aware token extractors (DONE)
Implemented in the orchestrator:
- `_extract_litellm_token_metadata()` — reads `response.raw["usage"]` into `LiteLLMGeminiTokenUsage`
- `_extract_default_token_metadata()` — reads `response.additional_kwargs` (works for OpenAI)
- `_extract_token_metadata()` — dispatcher based on `provider_name`

### Step 3 — Triple-file output per card (DONE)
Replaced `save_result_to_file` with `save_card_artifacts`:
- `insight_card_{model}_{epoch}.json` — structured card fields only
- `insight_card_{model}_{epoch}_raw.json` — full `ChatResponse.raw` serialized
- `insight_card_{model}_{epoch}_tokens.json` — token usage Pydantic model

### Step 4 — Finalize `generate_one_card` (DONE)
- Removed all inspection scaffolding
- Uses `llm.chat()` + `_strip_code_fences()` + `InsightCard.model_validate_json()`
- Calls `_extract_token_metadata()`, logs per-card usage, sets `result.metadata`

### Step 5 — Batch aggregation verified (DONE)
`_log_batch_summary` reads `result.metadata["token_usage"]` and pulls top-level `prompt_tokens`, `completion_tokens`, `total_tokens`. Compatible with both LiteLLM and default extractors.

### Step 6 — Live test passed (DONE)
Run `--count 2` with `TENNL_LLM_PROVIDER=litellm` (Gemini 2.5 Flash):
- 6 output files produced (3 per card)
- Card 1: prompt=382, completion=673 (reasoning=462, text=211), total=1055
- Card 2: prompt=382, completion=1336 (reasoning=1094, text=242), total=1718
- Batch summary: 764 prompt, 2009 completion, 2773 total

### Step 7 — Handoff doc (this document)

---

## How To Run

```bash
cd /Users/devansh/tennl-data/python/tennl/batch

# Dry run (no LLM call)
TENNL_LLM_PROVIDER=litellm UV_PROJECT_ENVIRONMENT="/Users/devansh/tennl-data/python/tennl/batch/.venv" \
  uv run --python 3.13 python -m tennl.batch.generator.insight_cards.insight_card_llamaindex_orchestrator \
  --dry-run --count 2 --output-dir /Users/devansh/tennl-data/output/dry_run_test

# Live Gemini run
TENNL_LLM_PROVIDER=litellm UV_PROJECT_ENVIRONMENT="/Users/devansh/tennl-data/python/tennl/batch/.venv" \
  uv run --python 3.13 python -m tennl.batch.generator.insight_cards.insight_card_llamaindex_orchestrator \
  --count 2 --output-dir /Users/devansh/tennl-data/output/gemini_live_test
```

**Note:** `--python 3.13` is required because the system default uv Python is 3.14, but the project requires `==3.13.*`.

`GEMINI_API_KEY` is loaded automatically from `secrets.txt` by `_load_secrets_env()`.

---

## Key Files

| File | State | Notes |
|------|-------|-------|
| `python/tennl/batch/src/tennl/batch/generator/insight_cards/insight_card_llamaindex_orchestrator.py` | Complete | Inspection scaffolding removed, all extractors + triple-file output working |
| `python/tennl/batch/src/tennl/batch/domain/insight_cards.py` | Complete | `metadata` field + `CompletionTokensDetails`, `PromptTokensDetails`, `LiteLLMGeminiTokenUsage` added |
| `python/tennl/batch/src/tennl/batch/domain/__init__.py` | Complete | All new models exported |
| `python/tennl/batch/src/tennl/batch/resources/app.yaml` | Modified | litellm provider → `gemini/gemini-2.5-flash` |
| `python/tennl/batch/output/response_raw_dump.json` | Reference artifact | Full LiteLLM ModelResponse from live Gemini call — DO NOT DELETE |
| `tasks/2026-04-08-litellm-gemini-spec.md` | New | LiteLLM technical spec with response structure details |

---

## Agent Prompt for Next Session

```
Read the handoff doc at tasks/2026-04-08-litellm-gemini-handoff.md and the LiteLLM spec
at tasks/2026-04-08-litellm-gemini-spec.md for full context.

The LiteLLM + Gemini integration for insight card generation is COMPLETE and tested.
All 7 plan steps were executed. The orchestrator at
python/tennl/batch/src/tennl/batch/generator/insight_cards/insight_card_llamaindex_orchestrator.py
is clean and functional. Live test with count=2 passed with proper token tracking.

Key architecture decisions already implemented:
- llm.chat() used directly (not as_structured_llm) to preserve token data in response.raw
- Code fence stripping via _strip_code_fences() + InsightCard.model_validate_json()
- Provider-aware token extraction: _extract_litellm_token_metadata reads response.raw["usage"],
  _extract_default_token_metadata reads response.additional_kwargs (for OpenAI)
- Triple-file output per card: .json (card), _raw.json (full ModelResponse), _tokens.json (token usage)
- LiteLLMGeminiTokenUsage Pydantic model captures all Gemini token fields including reasoning_tokens

Possible next steps:
- Add error recovery / retry logic for transient Gemini API failures
- Add prompt caching support (Gemini context caching)
- Integrate with the main workflow pipeline (tennl.batch.workflows)
- Add cost tracking using LiteLLM's completion_cost() utility
- Support parallel mode testing with Gemini rate limits in mind

Reference artifacts:
- python/tennl/batch/output/response_raw_dump.json — live ModelResponse sample
- output/gemini_live_test/ — 6 files from successful count=2 live test
```
