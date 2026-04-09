from __future__ import annotations

import importlib.resources as ir
import logging
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def load_yaml_settings(config_file: str = "app.yaml") -> dict[str, Any]:
    """Load settings from packaged YAML files shipped with the wheel.

    Reads ``app.yaml`` (main config), ``prompts.yaml`` (workflow prompts), and
    ``insight-cards/insight-card-settings.yaml`` (merged under ``insight_cards``).
    Resolved via ``importlib.resources`` for source checkout and installed wheels.
    """
    try:
        text = ir.files("tennl.batch").joinpath("resources", config_file).read_text(encoding="utf-8")
    except Exception as e:
        logger.error("Unable to load config file. Error: %s", e, exc_info=True)
        return {}

    raw = yaml.safe_load(text) or {}
    if not isinstance(raw, dict):
        raise ValueError("Invalid YAML root object in packaged app.yaml")

    try:
        prompts_text = ir.files("tennl.batch").joinpath("resources", "prompts.yaml").read_text(encoding="utf-8")
        prompts_raw = yaml.safe_load(prompts_text) or {}
        if isinstance(prompts_raw, dict):
            raw["prompts"] = prompts_raw
    except Exception as e:
        logger.error("Unable to load prompt config file. Error: %s", e, exc_info=True)

    try:
        ic_path = ir.files("tennl.batch").joinpath(
            "resources", "insight-cards", "insight-card-settings.yaml"
        )
        ic_raw = yaml.safe_load(ic_path.read_text(encoding="utf-8")) or {}
        if isinstance(ic_raw, dict):
            raw["insight_cards"] = ic_raw
    except Exception as e:
        logger.error("Unable to load insight card settings YAML. Error: %s", e, exc_info=True)

    return raw
