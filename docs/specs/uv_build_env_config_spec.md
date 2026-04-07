# uv Build + Environment Config Spec
## tennl-data (batch workflow) — Version 1.0 · April 2026

This spec describes the **Python build + runtime environment** setup for the `tennl-batch` project under `python/tennl/batch/`, and the supported configuration override rules (env, `.env`, YAML defaults).

---

## Scope
- **Project**: `python/tennl/batch/`
- **Package**: `tennl.batch` (source under `python/tennl/batch/src/tennl/batch/`)
- **Config entrypoint**: `tennl.batch.workflows.settings.AppSettings`

---

## Python + uv (strict)
- **Python**: `3.13.*` (enforced by `python/tennl/batch/pyproject.toml`)
- **Virtualenv**: `python/tennl/batch/.venv/`
- **Runner**: use `uv` for execution and dependency management.

### Standard run command
From repo root:

```bash
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" \
uv run --project python/tennl/batch \
python -m tennl.batch.workflows.sample_workflow
```

From `python/tennl/batch/`:

```bash
UV_PROJECT_ENVIRONMENT="/absolute/path/to/python/tennl/batch/.venv" \
uv run python -m tennl.batch.workflows.sample_workflow
```

---

## Build system (Hatchling)
- **Build backend**: Hatchling
- **Project file**: `python/tennl/batch/pyproject.toml`

### Resource sync hook (build-time)
We keep **canonical resources** in:
- `python/tennl/batch/src/resources/`

But runtime code reads **package resources** from:
- `python/tennl/batch/src/tennl/batch/resources/`

To keep this clean and consistent, a Hatch build hook syncs resources during build:
- **Hook file**: `python/tennl/batch/hatch_build.py`
- **Behavior**: copies `src/resources/*` → `src/tennl/batch/resources/*`

This supports the industry-standard Python model of “classpath resources” via `importlib.resources`.

---

## Makefile utilities
Location: `python/tennl/batch/Makefile`

Targets:
- **`make sync-resources`**: sync `src/resources/` → `src/tennl/batch/resources/`
- **`make build`**: build distributions (and run sync hook)
- **`make run`**: run sample workflow via `uv`

---

## Configuration model (AppSettings)
`AppSettings` is implemented as **Pydantic v2 `BaseSettings`** using `pydantic-settings`.

### Precedence (highest → lowest)
1. **OS environment variables** (including inline `FOO=bar uv run ...`)
2. **`.env` file** (loaded by Pydantic settings)
3. **YAML defaults** (`app.yaml` packaged inside the python package)
4. **Class field defaults**

### YAML defaults
- **File**: `app.yaml`
- **Read mechanism**: `importlib.resources` (package resource stream-style loading)
- **Rationale**: avoids hardcoded repo filesystem paths and works for installed wheels.

### Environment variable conventions
- **Prefix**: `TENNL_`
- **Nested delimiter**: `__` (double underscore)
  - Example: `TENNL_LLM__PROVIDERS__0__ENGINE=...`
- **Reason**: `.` is not portable for env var identifiers across shells and deployment systems; `__` is the common convention.

---

## Supported knobs (examples)
- Choose provider:

```bash
TENNL_LLM_PROVIDER=openai uv run --project python/tennl/batch python -c "from tennl.batch.workflows.settings import AppSettings; print(AppSettings().llm_provider.name)"
```

- Override nested config (example shape; depends on model fields):

```bash
TENNL_LLM__PROVIDERS__2__ENGINE="my-deployment" \
uv run --project python/tennl/batch python -c "from tennl.batch.workflows.settings import AppSettings; print(AppSettings().llm_provider.engine)"
```

---

## Non-goals / intentionally omitted
- No runtime YAML override/merge via env (kept simple by design).
- No reliance on repo-relative `Path(__file__).parents[...]` for config discovery.

