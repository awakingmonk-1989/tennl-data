from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    # .../src/tennl/batch/workflows/runtime_assets.py -> repo root (tennl-data/)
    return Path(__file__).resolve().parents[7]


def article_asset_path(section: str, filename: str) -> Path:
    """Return a path under runtime_assets/article for prompts/specs/skills."""
    if section not in {"prompts", "specs", "skills"}:
        raise ValueError(f"Unsupported article asset section: {section}")
    return repo_root() / "runtime_assets" / "article" / section / filename


def read_article_asset(section: str, filename: str) -> str:
    return article_asset_path(section, filename).read_text(encoding="utf-8")
