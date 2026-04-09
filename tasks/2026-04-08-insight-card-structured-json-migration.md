# Insight Card Structured JSON Migration

- Date: 2026-04-08
- Goal: Migrate the insight card LlamaIndex orchestrator from free-form text parsing to structured JSON generation using Pydantic output models, and persist enriched result records with runtime metadata.

## What Is Accomplished
- Replaced manual `TITLE:` / `CATEGORY:` / body parsing with LlamaIndex structured output using `llm.as_structured_llm(InsightCard)`.
- Introduced a strict Pydantic output model `InsightCard` for the LLM response.
- Introduced a second persisted result model `InsightCardResult` with runtime metadata fields:
  - `provider`
  - `raw`
  - `error`
- Updated prompt templates so every prompt version requests clean JSON with the exact required fields:
  - `title`
  - `category`
  - `content`
  - `tone`
  - `emotional_register`
  - `title_style`
  - `hook_type`
  - `opening_word_class`
- Mapped `tone` and `emotional_register` from the existing sampled `register` value without adding a new config axis.
- Updated dry-run and live generation paths to emit the new persisted JSON shape.
- Added tests covering variable mapping, structured success, structured failure, runtime failure, dedupe behavior, and dry-run handling.
- Verified the implementation with:
  - unit tests via `unittest`
  - dry-run CLI execution
  - live Azure Foundry generation run

## Summary Of Changes

### 1. Domain model changes
- File: `python/tennl/batch/src/tennl/batch/domain/insight_cards.py`
- Replaced the old dataclass-based `InsightCard` with a strict Pydantic `BaseModel`.
- New `InsightCard` fields:
  - `title`
  - `category`
  - `content`
  - `tone`
  - `emotional_register`
  - `title_style`
  - `hook_type`
  - `opening_word_class`
- Added `InsightCardResult` as a separate persisted model with:
  - all `InsightCard` content fields
  - `provider`
  - `raw`
  - `error`
- Preserved helper behavior at the result layer:
  - `is_valid()` now checks `title`, `content`, and absence of `error`
  - `fingerprint()` now hashes `title + content`

### 2. Orchestrator changes
- File: `python/tennl/batch/src/tennl/batch/generator/insight_cards/insight_card_llamaindex_orchestrator.py`
- Removed the old `parse_output()` logic that:
  - scanned lines manually
  - extracted `TITLE:` and `CATEGORY:`
  - treated the rest as `body`
  - stripped sentence-slot artifacts with regex
- Switched the generation path to structured LlamaIndex output:
  - uses `llm.as_structured_llm(output_cls=InsightCard)`
  - sends prompts as chat messages
  - reads parsed structured output from the LlamaIndex response
- Added structured helper functions to:
  - coerce parsed output into `InsightCard`
  - extract raw textual JSON from the LlamaIndex response
  - construct `InsightCardResult`
  - create empty error results on failure
  - omit blank system messages from the message list
- Updated the dry-run path to return `InsightCardResult` with:
  - preview prompt content in `raw`
  - placeholder-safe structured fields
  - provider information
- Updated sequential and parallel runners to use `InsightCardResult`.
- Updated dedupe/logging to work against the new result shape.
- Updated output serialization to use `model_dump()` instead of `asdict()`.

### 3. Prompt changes
- File: `python/tennl/batch/src/tennl/batch/resources/insight-cards/insight-card-settings.yaml`
- Rewrote all supported prompt variants:
  - `mini`
  - `large`
  - `small`
  - `moe`
- Each prompt now instructs the model to return valid JSON only.
- Removed all prior output instructions that depended on:
  - `TITLE:`
  - `CATEGORY:`
  - prose-only trailing body content
- Aligned prompt wording with the new output schema.
- Passed prompt control fields explicitly through the prompt as both constraints and expected echoed output fields:
  - `tone`
  - `emotional_register`
  - `title_style`
  - `hook_type`
  - `opening_word_class`
- Replaced `body` references with `content`.

### 4. Variable sampling changes
- File: `python/tennl/batch/src/tennl/batch/generator/insight_cards/insight_card_llamaindex_orchestrator.py`
- Kept the existing seed config unchanged.
- Added derived prompt variables:
  - `tone = register`
  - `emotional_register = register`
- No new `tone` pool or config key was introduced.

### 5. Test coverage added
- File: `python/tennl/batch/tests/test_insight_card_orchestrator.py`
- Added tests for:
  - tone/register mapping
  - successful structured generation path
  - invalid structured payload handling
  - runtime LLM exception handling
  - dedupe behavior using `title + content`
  - dry-run prompt preview behavior
  - omission of empty system prompt messages

### 6. Validation and verification
- Dry-run verified successfully through the CLI orchestrator.
- Live generation verified successfully with the configured Azure Foundry provider and model.
- Output file now persists flattened structured JSON records with runtime metadata.

## Summary Of Change Log

### Before
- The orchestrator generated free-form text.
- Output parsing depended on handwritten logic that searched for:
  - `TITLE:`
  - `CATEGORY:`
  - remaining text as `body`
- The persisted object shape mixed generated content and runtime metadata in a single dataclass.
- `body` was the primary text field.
- Prompt variants asked for human-readable formatted text rather than strict JSON.
- `tone` did not exist as a first-class output field.
- `emotional_register` existed only as a prompt control concept via `register`.
- Dedupe fingerprinting was based on `title + body`.
- Dry-run output preview was stored in the old `body` field.

### After
- The orchestrator generates structured output via LlamaIndex Pydantic parsing.
- The LLM output is validated against a strict Pydantic `InsightCard` schema.
- Persisted output is represented by `InsightCardResult`, which adds:
  - `provider`
  - `raw`
  - `error`
- `content` replaces `body` as the primary text field.
- Prompts now require valid JSON only and align exactly to the structured schema.
- `tone` and `emotional_register` are both included in the output shape.
- `tone` is derived from the sampled `register`, avoiding config churn.
- Dedupe fingerprinting now uses `title + content`.
- Dry-run preview is stored in `raw`, matching the new result contract.
- Output JSON files now contain flattened structured result records suitable for downstream consumption and debugging.

## Files Changed
- `python/tennl/batch/src/tennl/batch/domain/insight_cards.py`
- `python/tennl/batch/src/tennl/batch/domain/__init__.py`
- `python/tennl/batch/src/tennl/batch/generator/insight_cards/insight_card_llamaindex_orchestrator.py`
- `python/tennl/batch/src/tennl/batch/resources/insight-cards/insight-card-settings.yaml`
- `python/tennl/batch/tests/test_insight_card_orchestrator.py`

## Verification Run Notes
- Unit tests:
  - `UV_PROJECT_ENVIRONMENT=".venv" uv run python -m unittest tests.test_insight_card_orchestrator tests.test_imports`
- Dry run:
  - completed successfully
  - wrote structured output to `/tmp/insight_cards_structured_dry_run.json`
- Live run:
  - completed successfully against Azure Foundry
  - wrote structured output to `/tmp/insight_cards_structured_live.json`
