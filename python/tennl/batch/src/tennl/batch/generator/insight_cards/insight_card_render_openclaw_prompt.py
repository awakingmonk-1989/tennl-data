"""Render packaged insight-card prompts for external CLI agents (stdin JSON → stdout).

Expected stdin JSON::

    {"variables": {...}, "prompt_version": "large"}

Stdout: leading newline, rendered system template, two blank lines, rendered user template,
trailing newline (single blob for agents without separate system support).
"""

from __future__ import annotations

import json
import sys

from tennl.batch.generator.insight_cards.insight_card_llamaindex_orchestrator import (
    build_static_vars,
    render_prompt,
)
from tennl.batch.settings import AppSettings


def main() -> None:
    payload = json.load(sys.stdin)
    variables: dict = payload["variables"]
    version = payload.get("prompt_version", "large")
    app = AppSettings.shared
    ic = app.insight_cards
    system_tpl, user_tpl = ic.prompt_templates(version)
    static = build_static_vars(ic.formatter)
    merged = {**static, **variables}
    sys_m = render_prompt(system_tpl, merged)
    usr_m = render_prompt(user_tpl, merged)
    sys.stdout.write(f"\n{sys_m}\n\n\n{usr_m}\n")


if __name__ == "__main__":
    main()
