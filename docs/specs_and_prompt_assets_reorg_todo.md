# Specs and Prompt Assets Reorganization TODO

Purpose: reorganize the repo's Markdown/YAML content assets without changing content behavior.

Scope: specs, prompt docs, skill docs, design docs, generated batch-output locations, and runtime asset path updates. Keep `AGENTS.md` and `CLAUDE.md` in the project root.

## Non-Negotiables

- Do not move `AGENTS.md`; root-level agent instructions are the repo standard.
- Do not move `CLAUDE.md`; root-level Claude instructions are the repo standard.
- Do not change prompt/spec wording during the first pass; only move files and update paths.
- Do not delete archived/versioned docs in the first pass; move them to `docs/archive/...`.
- Preserve runtime behavior for the article workflow.
- Run verification after each phase that touches Python code.

## Current Runtime-Read Files

These files are directly read by active Python code and need path updates if moved:

- `prompts/conten_gen_prompt_page_post.md`
- `prompts/eval_pass1_moderation_prompt.md`
- `prompts/eval_pass2_quality_prompt.md`
- `prompts/refine_prompt.md`
- `specs/content_gen_spec.md`
- `specs/narration_flow_spec_v1.1.md`
- `specs/json_schema_spec_v1.md`
- `skills/skill_content_generation.md`
- `skills/skill_content_moderation.md`
- `skills/skill_creativity_narration.md`
- `python/tennl/batch/src/tennl/batch/resources/sample_output_reference.md`
- `python/tennl/batch/src/tennl/batch/resources/app.yaml`
- `python/tennl/batch/src/tennl/batch/resources/prompts.yaml`
- `python/tennl/batch/src/tennl/batch/resources/insight-cards/insight-card-settings.yaml`

## Proposed Target Structure

```text
runtime_assets/
  article/
    prompts/
      conten_gen_prompt_page_post.md
      eval_pass1_moderation_prompt.md
      eval_pass2_quality_prompt.md
      refine_prompt.md
    specs/
      content_gen_spec.md
      narration_flow_spec_v1.1.md
      json_schema_spec_v1.md
    skills/
      skill_content_generation.md
      skill_content_moderation.md
      skill_creativity_narration.md
      skill_schema_validation.md
      skill_html_generation.md
design/
  jokes/
    specs/
      content_spec.md
    prompts/
      markdown/
        sample_batch_prompt.md
        sample_batch_prompt_2.md
      yaml/
        joke_prompt.yaml
        joke_batch_prompt.yaml
    config/
      updated_heuristics_pool.json

docs/
  design/
    content/
      novelty/
        content_gen_novelty_spec.md
        novelty_pool_cli_spec.md
    python/
      uv_build_env_config_spec.md
    workflow/
      workflow_traceid_spanid.md
    azure/
      azure-table-storage-workflow-index-design.md
      azure_storage_content_gen_pipeline_progress.md
      azure_store_strategy_and_recovery_design.md
  handoff/
    agent_workflow_progress.md
    novelty_mode_progress.md
  archive/
    specs/
      article/
        content_gen_spec_v3.md
      v2/
        content_gen_prompt_page_post_v2.md
        content_gen_spec_v3_updated.md
        json_schema_spec_v1_updated.md
        narration_flow_spec_v1.1_updated.md
      v3/
        article_compact_guideline.md
        moderation_pass_guideline.md
    prompts/
      markdown/
        article_compact_guideline.md
        content_gen_compact_jsonspec.md
        eval_compact_prompt.md
        moderation_compact_prompt.md
        refine_compact_prompt.md
      yaml/
        content_gen_compact_prompt1.yaml
        eval_prompt.yaml
        eval_quality_compact_prompt.yaml
        refine_prompt.yaml
    jokes/
      sample_batch_prompt.md
      sample_batch_prompt_2.md
    version/
      content_agent_spec_posts_page_v2.md
      content_gen_posts_page_v1.md
      content_generation_prompt.md
      content_generation_prompt.yaml
      narration_flow_spec_v1.md
      workflow_tld.md
```

## Agent 1: Active Article Runtime Assets

Goal: move active article prompts/specs/skills into `runtime_assets/article/...` and update Python path reads.

Moves:

- `prompts/conten_gen_prompt_page_post.md` -> `runtime_assets/article/prompts/conten_gen_prompt_page_post.md`
- `prompts/eval_pass1_moderation_prompt.md` -> `runtime_assets/article/prompts/eval_pass1_moderation_prompt.md`
- `prompts/eval_pass2_quality_prompt.md` -> `runtime_assets/article/prompts/eval_pass2_quality_prompt.md`
- `prompts/refine_prompt.md` -> `runtime_assets/article/prompts/refine_prompt.md`
- `specs/content_gen_spec.md` -> `runtime_assets/article/specs/content_gen_spec.md`
- `specs/narration_flow_spec_v1.1.md` -> `runtime_assets/article/specs/narration_flow_spec_v1.1.md`
- `specs/json_schema_spec_v1.md` -> `runtime_assets/article/specs/json_schema_spec_v1.md`
- `skills/skill_content_generation.md` -> `runtime_assets/article/skills/skill_content_generation.md`
- `skills/skill_content_moderation.md` -> `runtime_assets/article/skills/skill_content_moderation.md`
- `skills/skill_creativity_narration.md` -> `runtime_assets/article/skills/skill_creativity_narration.md`
- `skills/skill_schema_validation.md` -> `runtime_assets/article/skills/skill_schema_validation.md`
- `skills/skill_html_generation.md` -> `runtime_assets/article/skills/skill_html_generation.md`

Python files to update:

- `python/tennl/batch/src/tennl/batch/workflows/stages/generator.py`
- `python/tennl/batch/src/tennl/batch/workflows/stages/moderation_eval.py`
- `python/tennl/batch/src/tennl/batch/workflows/stages/quality_eval.py`
- `python/tennl/batch/src/tennl/batch/workflows/workflow.py`

Implementation guidance:

- Add one helper for runtime asset paths instead of repeating `root / "runtime_assets" / ...`.
- Preserve all existing prompt assembly behavior.
- In `workflow.py`, update the original prompt read for refinement from root `prompts/...` to the new article prompt path.

Verification:

```bash
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run --project python/tennl/batch python -m pytest python/tennl/batch/tests
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run --project python/tennl/batch python -m tennl.batch.workflows --topic "Home & Living" --sub-topic "Interior Styling Ideas" --content-variant AI_GENERATED --eval-mode sequential --timeout 300
```

## Agent 2: Specs Archive and Design Docs

Goal: move non-runtime spec/design Markdown into docs folders.

Moves:

- `specs/content_gen_novelty_spec.md` -> `docs/design/content/novelty/content_gen_novelty_spec.md`
- `specs/novelty_pool_cli_spec.md` -> `docs/design/content/novelty/novelty_pool_cli_spec.md`
- `specs/content_gen_spec_v3.md` -> `docs/archive/specs/article/content_gen_spec_v3.md`
- `specs/uv_build_env_config_spec.md` -> `docs/design/python/uv_build_env_config_spec.md`
- `specs/workflow_traceid_spanid.md` -> `docs/design/workflow/workflow_traceid_spanid.md`
- `specs/v2/content_gen_prompt_page_post_v2.md` -> `docs/archive/specs/v2/content_gen_prompt_page_post_v2.md`
- `specs/v2/content_gen_spec_v3_updated.md` -> `docs/archive/specs/v2/content_gen_spec_v3_updated.md`
- `specs/v2/json_schema_spec_v1_updated.md` -> `docs/archive/specs/v2/json_schema_spec_v1_updated.md`
- `specs/v2/narration_flow_spec_v1.1_updated.md` -> `docs/archive/specs/v2/narration_flow_spec_v1.1_updated.md`
- `specs/v3/article_compact_guideline.md` -> `docs/archive/specs/v3/article_compact_guideline.md`
- `specs/v3/moderation_pass_guideline.md` -> `docs/archive/specs/v3/moderation_pass_guideline.md`
- `data/data/azure/azure-table-storage-workflow-index-design.md` -> `docs/design/azure/azure-table-storage-workflow-index-design.md`
- `data/data/azure/azure_storage_content_gen_pipeline_progress.md` -> `docs/design/azure/azure_storage_content_gen_pipeline_progress.md`
- `data/data/azure/azure_store_strategy_and_recovery_design.md` -> `docs/design/azure/azure_store_strategy_and_recovery_design.md`
- `python/tennl/batch/agent_workflow_progress.md` -> `docs/handoff/agent_workflow_progress.md`
- `python/tennl/batch/novelty_mode_progress.md` -> `docs/handoff/novelty_mode_progress.md`

Python files to update:

- `python/tennl/batch/src/tennl/batch/workflows/novelty_pool_cli.py` only if comments/help strings should point to the new novelty spec location.

Verification:

```bash
rg -n "specs/content_gen_novelty_spec|specs/novelty_pool_cli_spec|python/tennl/batch/agent_workflow_progress|python/tennl/batch/novelty_mode_progress|data/data/azure" .
```

## Agent 3: Joke Assets

Goal: move joke specs/prompts/config into the joke feature design folder, then decide whether to wire `joke_generator.py` to load YAML prompts or leave embedded prompt strings for now.

Moves:

- `specs/jokes/content_spec.md` -> `design/jokes/specs/content_spec.md`
- `specs/jokes/joke_prompt.yaml` -> `design/jokes/prompts/yaml/joke_prompt.yaml`
- `specs/jokes/joke_batch_prompt.yaml` -> `design/jokes/prompts/yaml/joke_batch_prompt.yaml`
- `specs/jokes/updated_heuristics_pool.json` -> `design/jokes/config/updated_heuristics_pool.json`
- `specs/jokes/sample_batch_prompt.md` -> `design/jokes/prompts/markdown/sample_batch_prompt.md`
- `specs/jokes/sample_batch_prompt_2.md` -> `design/jokes/prompts/markdown/sample_batch_prompt_2.md`

Python files to update:

- `data/generator/joke_generator.py` only if replacing embedded prompt constants with YAML-loaded prompt/config files.

Suggested refactor:

- Add CLI args `--prompt-file` and `--heuristics-file`.
- Default them to the new `design/jokes/...` locations, or promote those files into `runtime_assets/jokes/...` first if we decide they should become runtime dependencies.
- Keep the current embedded prompt as fallback for one iteration if safety is preferred.

Verification:

```bash
python data/generator/joke_generator.py --help
```

## Agent 4: Prompt Drafts and Version Archives

Goal: move inactive prompt drafts and prototype `version/` content out of active-looking top-level folders.

Moves:

- `prompts/article_compact_guideline.md` -> `design/article/prompts/markdown/article_compact_guideline.md`
- `prompts/content_gen_compact_jsonspec.md` -> `design/article/prompts/markdown/content_gen_compact_jsonspec.md`
- `prompts/content_gen_compact_prompt1.yaml` -> `design/article/prompts/yaml/content_gen_compact_prompt1.yaml`
- `prompts/eval_compact_prompt.md` -> `design/article/prompts/markdown/eval_compact_prompt.md`
- `prompts/eval_prompt.yaml` -> `design/article/prompts/yaml/eval_prompt.yaml`
- `prompts/eval_quality_compact_prompt.yaml` -> `design/article/prompts/yaml/eval_quality_compact_prompt.yaml`
- `prompts/moderation_compact_prompt.md` -> `design/article/prompts/markdown/moderation_compact_prompt.md`
- `prompts/refine_compact_prompt.md` -> `design/article/prompts/markdown/refine_compact_prompt.md`
- `prompts/refine_prompt.yaml` -> `design/article/prompts/yaml/refine_prompt.yaml`
- `version/content_agent_spec_posts_page_v2.md` -> `docs/archive/version/content_agent_spec_posts_page_v2.md`
- `version/content_gen_posts_page_v1.md` -> `docs/archive/version/content_gen_posts_page_v1.md`
- `version/content_generation_prompt.md` -> `docs/archive/version/content_generation_prompt.md`
- `version/content_generation_prompt.yaml` -> `docs/archive/version/content_generation_prompt.yaml`
- `version/narration_flow_spec_v1.md` -> `docs/archive/version/narration_flow_spec_v1.md`
- `version/workflow_tld.md` -> `docs/archive/version/workflow_tld.md`

Python files to update:

- `version/content_prompt_loader.py` if this prototype remains in source control and its example comment should point to the archived YAML.

Verification:

```bash
rg -n "prompts/article_compact|prompts/content_gen_compact|prompts/eval_compact|prompts/refine_prompt.yaml|version/content_generation_prompt" . -g '!design/article/prompts/**' -g '!docs/archive/**'
```

## Agent 5: Novelty Batch Output Location

Goal: stop writing generated batch artifacts under `specs/data`.

Proposed output move:

- From `specs/data/batch_{timestamp}/`
- To `out/novelty_batches/batch_{timestamp}/`

Python files to update:

- `python/tennl/batch/src/tennl/batch/workflows/novelty_pool_cli.py`
- `python/scripts/verify_novelty_batch_run_artifacts.py`

Verification:

```bash
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run --project python/tennl/batch python -m tennl.batch.workflows.novelty_pool_cli batch --help
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run --project python/tennl/batch python/scripts/verify_novelty_batch_run_artifacts.py --help
```

## Agent 6: Insight Cards Resource Cleanup

Goal: make insight-card runtime resources consistent with Python package naming and loading.

Current issue:

- Python package path is `generator/insight_cards`.
- Resource folder is `resources/insight-cards`.
- Orchestrator default config is `insight-card-settings.yaml`, which is relative to the current working directory and may not resolve to the packaged resource.

Proposed changes:

- Rename `python/tennl/batch/src/tennl/batch/resources/insight-cards/` to `python/tennl/batch/src/tennl/batch/resources/insight_cards/`.
- Update `insight_card_llamaindex_orchestrator.py` to load defaults via `importlib.resources`.
- Keep `--config` and `--seed` CLI overrides for local experimentation.

Python files to update:

- `python/tennl/batch/src/tennl/batch/generator/insight_cards/insight_card_llamaindex_orchestrator.py`

Verification:

```bash
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run --project python/tennl/batch python python/tennl/batch/src/tennl/batch/generator/insight_cards/insight_card_llamaindex_orchestrator.py --dry-run --count 1
```

## Final Repo-Wide Checks

Run after all phases:

```bash
rg -n "root / \"specs\"|root / \"prompts\"|root / \"skills\"|specs/data|specs/content_gen|specs/narration_flow|specs/json_schema|prompts/conten_gen|prompts/eval_pass|prompts/refine_prompt|skills/skill_content" . -g '!docs/archive/**' -g '!out/**' -g '!**/.venv/**' -g '!python/tennl/batch/python/**'
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run --project python/tennl/batch python -m pytest python/tennl/batch/tests
git status --short
```
