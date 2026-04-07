"""
insight_card_llamaindex_orchestrator.py

Insight card generator using LlamaIndex SimpleChatEngine.
- LLM configuration is loaded from the shared app.yaml via AppSettings / llm_factory
- Each card gets a FRESH chat engine — no shared session, no follow-up contamination
- Two run modes: sequential and parallel (configurable max workers)
- Prompt templates loaded from insight-card-settings.yaml; seed variables from JSON

Usage:
    python insight_card_llamaindex_orchestrator.py
    python insight_card_llamaindex_orchestrator.py --mode parallel
    python insight_card_llamaindex_orchestrator.py --mode sequential --count 5
    python insight_card_llamaindex_orchestrator.py --dry-run
    python insight_card_llamaindex_orchestrator.py --provider anthropic
"""

import json
import logging
import os
import re
import argparse
import hashlib
import concurrent.futures
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Any

import yaml

from tennl.batch.workflows.settings import AppSettings
from tennl.batch.workflows.llm_factory import build_llm as _build_llm_from_config

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Config loader
# ─────────────────────────────────────────────────────────────

def load_insight_card_settings(path: str) -> dict:
    """Load insight-card-specific settings (generation params + prompt templates)."""
    with open(path) as f:
        return yaml.safe_load(f)


def load_seed_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────
# Variable sampler — stateless round-robin
# ─────────────────────────────────────────────────────────────

class SlotRotator:
    def __init__(self, values: list, offset: int = 0):
        self._values = values
        self._offset = offset
        self._counter = 0

    def next(self) -> str:
        idx = (self._counter + self._offset) % len(self._values)
        self._counter += 1
        return self._values[idx]


class VariableSampler:
    """
    Each worker gets its own sampler with a unique offset.
    Slots rotate independently — combination space is multiplicative.

    Themes and human_contexts are sampled from the selected category's
    pool (per-category arrays in the seed config), not from a global list.
    """

    def __init__(self, seed: dict[str, Any], worker_id: int = 0):
        ts = seed["title_style_hints"]
        categories = seed["categories"]  # dict keyed by category name
        category_names = list(categories.keys())

        self._categories = categories
        self._category_rotator = SlotRotator(category_names, worker_id)

        self._global_rotators = {
            "hook_type":          SlotRotator(seed["hook_types"],           worker_id + 1),
            "register":           SlotRotator(seed["registers"],            worker_id + 2),
            "opening_word_class": SlotRotator(seed["opening_word_classes"], worker_id + 3),
            "title_style":        SlotRotator(ts["styles"],                worker_id + 8),
        }
        self._avoid_titles = ts.get("avoid", [])
        self._worker_id = worker_id

    def sample(self) -> dict[str, Any]:
        category = self._category_rotator.next()
        cat_pool = self._categories[category]

        # Per-category rotators — built fresh each sample so offset advances
        theme_rotator = SlotRotator(cat_pool["themes"], self._worker_id)
        context_rotator = SlotRotator(cat_pool["human_contexts"], self._worker_id)

        v = {k: r.next() for k, r in self._global_rotators.items()}
        v["category"] = category
        v["theme"] = theme_rotator.next()
        v["human_context"] = context_rotator.next()
        v["topic"] = f"{v['theme']} in the context of {v['human_context']}"
        v["avoid_titles"] = "Avoid titles like: " + ", ".join(
            f'"{t}"' for t in self._avoid_titles
        )
        return v


# ─────────────────────────────────────────────────────────────
# Chat engine factory — fresh instance per card generation
# ─────────────────────────────────────────────────────────────

def build_chat_engine(llm, system_prompt: str):
    """
    Creates a fresh SimpleChatEngine with no prior chat history.
    Each call is a new isolated session — no state leaks between cards.
    """
    from llama_index.core.chat_engine import SimpleChatEngine

    return SimpleChatEngine.from_defaults(
        llm=llm,
        system_prompt=system_prompt if system_prompt.strip() else None,
    )


# ─────────────────────────────────────────────────────────────
# Prompt renderer
# ─────────────────────────────────────────────────────────────

def render_prompt(template: str, variables: dict) -> str:
    """Simple {key} substitution. Missing keys left as-is."""
    try:
        return template.format(**variables)
    except KeyError as e:
        # Graceful fallback — don't crash on missing optional keys
        result = template
        for k, v in variables.items():
            result = result.replace("{" + k + "}", str(v))
        return result


# ─────────────────────────────────────────────────────────────
# Output parser
# ─────────────────────────────────────────────────────────────

@dataclass
class InsightCard:
    title: str
    category: str
    body: str
    provider: str
    prompt_version: str
    variables: dict = field(default_factory=dict)
    raw: str = ""
    error: Optional[str] = None

    def is_valid(self) -> bool:
        return bool(self.title and self.body and not self.error)

    def fingerprint(self) -> str:
        return hashlib.md5(f"{self.title}{self.body}".encode()).hexdigest()[:10]


def parse_output(
    raw: str,
    provider: str,
    version: str,
    variables: dict,
) -> InsightCard:
    raw = raw.strip()
    title, category, body = "", "", ""
    body_lines = []

    for line in raw.splitlines():
        upper = line.upper()
        if upper.startswith("TITLE:"):
            title = line.split(":", 1)[1].strip().strip("[]")
        elif upper.startswith("CATEGORY:"):
            category = line.split(":", 1)[1].strip().strip("[]")
        else:
            body_lines.append(line)

    # Strip v3 sentence slot artifacts
    body = "\n".join(body_lines).strip()
    body = re.sub(r"^Sentence \d[\s—–-]+", "", body, flags=re.MULTILINE).strip()

    error = None
    if not title:
        error = "missing TITLE"
    elif not body:
        error = "missing body"

    return InsightCard(
        title=title,
        category=category or variables.get("category", ""),
        body=body,
        provider=provider,
        prompt_version=version,
        variables=variables,
        raw=raw,
        error=error,
    )


# ─────────────────────────────────────────────────────────────
# Single card generation — one fresh engine per call
# ─────────────────────────────────────────────────────────────

def generate_one_card(
    llm,
    system_prompt_tpl: str,
    user_prompt_tpl: str,
    variables: dict,
    provider_name: str,
    prompt_version: str,
    dry_run: bool,
) -> InsightCard:
    """
    Builds a fresh chat engine, sends one message, tears it down.
    No session reuse — diversity is guaranteed at the engine level.
    """
    system_prompt = render_prompt(system_prompt_tpl, variables)
    user_prompt = render_prompt(user_prompt_tpl, variables)

    if dry_run:
        return InsightCard(
            title="[DRY RUN]",
            category=variables.get("category", ""),
            body=f"[SYSTEM]\n{system_prompt}\n\n[USER]\n{user_prompt}",
            provider=provider_name,
            prompt_version=prompt_version,
            variables=variables,
            raw="[dry run]",
        )

    try:
        engine = build_chat_engine(llm, system_prompt)
        response = engine.chat(user_prompt)
        raw_text = str(response).strip()
    except Exception as e:
        logger.error("")
        return InsightCard(
            title="", category="", body="",
            provider=provider_name, prompt_version=prompt_version,
            variables=variables, raw="", error=str(e),
        )

    return parse_output(raw_text, provider_name, prompt_version, variables)


# ─────────────────────────────────────────────────────────────
# Batch runner — sequential and parallel modes
# ─────────────────────────────────────────────────────────────

def run_sequential(
    llm,
    system_prompt_tpl: str,
    user_prompt_tpl: str,
    seed: dict,
    provider_name: str,
    prompt_version: str,
    count: int,
    dry_run: bool,
) -> list[InsightCard]:
    results = []
    seen = set()

    for i in range(count):
        sampler = VariableSampler(seed, worker_id=i)
        variables = sampler.sample()

        card = generate_one_card(
            llm, system_prompt_tpl, user_prompt_tpl,
            variables, provider_name, prompt_version, dry_run,
        )
        _log_card(card, i, seen, results)

    return results


def run_parallel(
    llm,
    system_prompt_tpl: str,
    user_prompt_tpl: str,
    seed: dict,
    provider_name: str,
    prompt_version: str,
    count: int,
    max_workers: int,
    dry_run: bool,
) -> list[InsightCard]:
    results = []
    seen = set()

    def task(worker_id: int) -> InsightCard:
        sampler = VariableSampler(seed, worker_id=worker_id)
        variables = sampler.sample()
        return generate_one_card(
            llm, system_prompt_tpl, user_prompt_tpl,
            variables, provider_name, prompt_version, dry_run,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(task, i): i for i in range(count)}
        for future in concurrent.futures.as_completed(futures):
            card = future.result()
            _log_card(card, futures[future], seen, results)



    return results


def _log_card(card: InsightCard, idx: int, seen: set, results: list):
    if card.error:
        print(f"  [error] worker {idx}: {card.error}")
        return
    fp = card.fingerprint()
    if fp in seen:
        print(f"  [dedup] skipped duplicate: {card.title}")
        return
    seen.add(fp)
    results.append(card)
    print(f"  [ok] {card.provider} | {card.category} | {card.title}")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Insight card orchestrator (LlamaIndex)")
    parser.add_argument("--config",   default="insight-card-settings.yaml")
    parser.add_argument("--seed",     default="insight_card_config.json")
    parser.add_argument("--mode",     default="sequential", choices=["sequential", "parallel"])
    parser.add_argument("--count",    type=int, default=None,  help="Override count from config")
    parser.add_argument("--workers",  type=int, default=None,  help="Override max_workers from config")
    parser.add_argument("--provider", default=None,            help="Override active_provider (uses app.yaml providers)")
    parser.add_argument("--version",  default=None,            help="Override prompt_version from config")
    parser.add_argument("--dry-run",  action="store_true",     help="Print prompts without calling LLM")
    args = parser.parse_args()

    cfg  = load_insight_card_settings(args.config)
    seed = load_seed_config(args.seed)

    # LLM is resolved from the shared app.yaml via AppSettings.
    # --provider overrides TENNL_LLM_PROVIDER env var for this run.
    if args.provider:
        os.environ["TENNL_LLM_PROVIDER"] = args.provider

    app_settings   = AppSettings()
    llm_cfg        = app_settings.llm_provider
    provider_name  = llm_cfg.name
    llm            = _build_llm_from_config(llm_cfg)

    prompt_version = args.version  or cfg["generation"]["prompt_version"]
    count          = args.count    or cfg["generation"]["count"]
    max_workers    = args.workers  or cfg["generation"]["max_workers"]
    output_file    = cfg["generation"]["output_file"]

    prompt_cfg     = cfg["prompts"][prompt_version]
    system_tpl     = prompt_cfg.get("system_prompt", "")
    user_tpl       = prompt_cfg["user_prompt"]

    print(f"\nInsight card orchestrator (LlamaIndex)")
    print(f"  provider : {provider_name}")
    print(f"  model    : {llm_cfg.model}")
    print(f"  version  : {prompt_version}")
    print(f"  mode     : {args.mode}")
    print(f"  count    : {count}")
    print(f"  workers  : {max_workers if args.mode == 'parallel' else 1}")
    print(f"  dry-run  : {args.dry_run}\n")

    if args.mode == "sequential":
        cards = run_sequential(
            llm, system_tpl, user_tpl, seed,
            provider_name, prompt_version, count, args.dry_run,
        )
    else:
        cards = run_parallel(
            llm, system_tpl, user_tpl, seed,
            provider_name, prompt_version, count, max_workers, args.dry_run,
        )

    print(f"\nGenerated: {len(cards)} cards")

    Path(output_file).write_text(
        json.dumps([asdict(c) for c in cards], indent=2, ensure_ascii=False)
    )
    print(f"Saved to: {output_file}")

    if args.dry_run and cards:
        print("\n--- Dry run prompt preview (card 0) ---")
        print(cards[0].body)


if __name__ == "__main__":
    main()
