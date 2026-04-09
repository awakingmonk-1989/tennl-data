# Task: Batch settings architecture, insight orchestrator, and domain records

**Date:** 2026-04-08  

**Goal:** Centralize application and insight-card configuration under typed settings, align the insight-card LlamaIndex orchestrator with workflow-style `AppSettings.shared`, improve logging and CLI ergonomics, split LLM config into a dedicated settings subpackage, and isolate internal `@dataclass` records in a `domain` package—with all imports verified across `workflows` and `generator`.

---

## What was accomplished

- Introduced **`tennl.batch.settings`** as the primary settings layer (YAML + env + Pydantic), with subpackages for articles (prompt templates + content types), insight cards (generation + prompt packs), LLM provider models, and utilities (YAML merge load, provider pick, deep merge).
- Wired **packaged** `resources/insight-cards/insight-card-settings.yaml` into **`AppSettings`** as **`insight_cards`** so insight generation uses the same precedence as the rest of the app.
- Refactored **`insight_card_llamaindex_orchestrator`**: packaged defaults only (no `--config` / `--seed` file overrides), **`--output-file`** override, **`AppSettings.shared`** only (no `--provider`; provider via **`TENNL_LLM_PROVIDER`** before process start), structured logging.
- Moved **LLM** Pydantic models from **`settings/articles/llm.py`** to top-level **`settings/llm/`** package (`models.py` + `__init__.py`).
- Added **`tennl.batch.domain`** for internal dataclasses; moved **`InsightCard`** out of the orchestrator module.
- Left **`workflows/settings.py`** as a **backward-compatible re-export** shim to **`tennl.batch.settings`**.
- Fixed **`BaseSampler`** (`abc` / typing imports) so the orchestrator module imports cleanly.
- Verified recursive imports for **`tennl.batch.workflows`** and **`tennl.batch.generator`**, plus workflow CLIs and the insight orchestrator module.

---

## Summary of changes (by area)

### Insight card orchestrator (`generator/insight_cards/insight_card_llamaindex_orchestrator.py`)

- Loads **seed JSON** only from packaged **`resources/insight-cards/insight_card_config.json`** (`load_packaged_seed_config`).
- Loads **insight YAML** only via **`AppSettings.shared.insight_cards`** (merged in settings YAML loader).
- **CLI:** removed `--config`, `--seed`, `--provider`; added **`--output-file`**; retained `--mode`, `--count`, `--workers`, `--version`, `--dry-run`.
- **Settings access:** always **`app = AppSettings.shared`**, **`llm = app.llm`**, **`ic_settings = app.insight_cards`**.
- **Logging:** `logging.basicConfig` in `main`; `print` → `logger.info` / `logger.warning`; LLM failures use `logger.exception` and `error=str(e)` on the card.
- **`InsightCard`:** removed from this file; imported from **`tennl.batch.domain`**; removed unused **`hashlib`** (fingerprint lives on domain model).
- **Imports:** `AppSettings` from **`tennl.batch.settings`**.

### Settings package (`tennl.batch.settings`)

- **`settings/__init__.py`:** exports `AppSettings`, article prompt types, `InsightCard*` Pydantic settings, LLM types, util helpers; assigns **`AppSettings.shared = _shared_settings()`**.
- **`settings/app_settings.py`:** `BaseSettings` subclass, `llm_config` / `prompts` / `insight_cards`, `llm_provider` + `llm` properties, custom YAML source calling **`load_yaml_settings`**.
- **`settings/articles/`:** `ContentType`, `LongArticlePromptTemplate`, `LongArticlePromptSettings` (names per current codebase); **no** LLM models here after refactor.
- **`settings/insight_cards/`:** Pydantic `InsightCardGenerationSettings`, `InsightCardPromptPack`, `InsightCardSettings` with **`prompt_templates(version)`**.
- **`settings/llm/`:** package with **`models.py`** (`ProviderName`, `LlmProviderConfig`, `LlmSettings`) and **`__init__.py`** re-exports.
- **`settings/util/`:** `yaml_settings.py` (`load_yaml_settings` merges `app.yaml`, `prompts.yaml`, `insight-cards/insight-card-settings.yaml` under `insight_cards`), `providers.py` (`pick_provider`), `merge.py` (`deep_merge_dicts`).

### Workflows compatibility

- **`workflows/settings.py`:** thin re-exports from **`tennl.batch.settings`** (`__all__` preserved for existing names).
- **`workflows/__init__.py`:** imports `AppSettings`, `InsightCardSettings` from **`tennl.batch.settings`**.
- **`workflows/llm_factory.py`:** `LlmProviderConfig` from **`tennl.batch.settings`**.

### Domain package (`tennl.batch.domain`)

- **`domain/insight_cards.py`:** **`InsightCard`** `@dataclass` with `is_valid`, `fingerprint`, typed **`variables: dict[str, Any]`**.
- **`domain/__init__.py`:** exports **`InsightCard`**.

### Base / misc

- **`base/sampler.py`:** added **`import abc`** and **`Any`** typing so **`BaseSampler`** is valid.

---

## Changelog: before → after

| Aspect | Before | After |
|--------|--------|--------|
| **Insight YAML** | Loaded from CLI **`--config`** path (default cwd file) | Loaded only from packaged YAML merged into **`AppSettings.insight_cards`** |
| **Seed JSON** | CLI **`--seed`** path (default cwd file) | Packaged **`insight_card_config.json`** only |
| **Insight settings typing** | Untyped dict from `yaml.safe_load` in orchestrator | **`InsightCardSettings`** (Pydantic) on **`AppSettings`** |
| **Orchestrator `AppSettings`** | **`AppSettings()`** or mixed with `.shared`; **`--provider`** mutated env + fresh instance | **`AppSettings.shared`** only; provider via **`TENNL_LLM_PROVIDER`** before import/start |
| **CLI overrides** | `--config`, `--seed`, `--provider` | **`--output-file`** plus existing count/workers/version/mode/dry-run |
| **Logging** | `print`, empty `logger.error("")` | **`logging`**, `logger.exception` on LLM errors |
| **Settings module location** | Monolithic **`workflows/settings.py`** | Primary **`tennl.batch.settings`** tree; **`workflows/settings.py`** = shim |
| **LLM config module** | Under **`settings/articles/llm.py`** then **`settings/llm.py`** | **`settings/llm/`** package (**`models.py`** + **`__init__.py`**) |
| **`InsightCard` definition** | In orchestrator module | **`tennl.batch.domain.insight_cards.InsightCard`** |
| **`BaseSampler`** | Broken (`abc` not imported) | Imports fixed |
| **YAML loading for app** | Only `app.yaml` + `prompts.yaml` (when monolithic) | Same plus **`insight-cards/insight-card-settings.yaml`** → **`insight_cards`** key |
| **Import path for `AppSettings` (orchestrator)** | **`tennl.batch.workflows.settings`** | **`tennl.batch.settings`** |
| **`llm_factory` `LlmProviderConfig`** | **`workflows.settings`** | **`tennl.batch.settings`** |

---

## Files touched (reference)

*New / notable paths:*

- `python/tennl/batch/src/tennl/batch/settings/` (package tree: `__init__.py`, `app_settings.py`, `articles/`, `insight_cards/`, `llm/`, `util/`)
- `python/tennl/batch/src/tennl/batch/domain/` (`__init__.py`, `insight_cards.py`)

*Updated:*

- `python/tennl/batch/src/tennl/batch/workflows/settings.py` (shim)
- `python/tennl/batch/src/tennl/batch/workflows/__init__.py`
- `python/tennl/batch/src/tennl/batch/workflows/llm_factory.py`
- `python/tennl/batch/src/tennl/batch/generator/insight_cards/insight_card_llamaindex_orchestrator.py`
- `python/tennl/batch/src/tennl/batch/base/sampler.py`

*Removed (superseded by package layout):*

- `settings/llm.py` (single file) replaced by **`settings/llm/`** package
- `settings/articles/llm.py` (after LLM lifted to top-level **`settings/llm`**)

---

## Follow-ups (optional)

- Update **`docs/specs/uv_build_env_config_spec.md`** (and similar) if they still cite **`tennl.batch.workflows.settings`** as the config entrypoint; canonical entrypoint is **`tennl.batch.settings`**.
- **`workflows/models.py`** remains Pydantic-only; future internal dataclasses can live under **`tennl.batch.domain`**.
