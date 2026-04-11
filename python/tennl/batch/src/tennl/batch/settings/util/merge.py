from typing import Any


def deep_merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge override into base (override wins)."""
    out: dict[str, Any] = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge_dicts(out[k], v)
        else:
            out[k] = v
    return out
