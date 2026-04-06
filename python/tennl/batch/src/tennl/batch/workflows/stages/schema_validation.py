from __future__ import annotations

from typing import Any

from ..models import SchemaFailure, SchemaReport


REQUIRED_ROOT_KEYS = [
    "hero",
    "hook",
    "quick_reference",
    "word_count_meta",
]

POSTS_ALIASES = ("posts", "sections")


def validate_article_schema(article_json: dict[str, Any]) -> SchemaReport:
    failures: list[SchemaFailure] = []

    for k in REQUIRED_ROOT_KEYS:
        if k not in article_json:
            failures.append(SchemaFailure(path=f"$.{k}", message="Missing required key"))

    posts = None
    posts_key = None
    for alias in POSTS_ALIASES:
        if alias in article_json:
            posts = article_json[alias]
            posts_key = alias
            break

    if posts is None or not isinstance(posts, list) or not posts:
        failures.append(SchemaFailure(path="$.posts|sections", message="Must be a non-empty list"))
    else:
        for i, p in enumerate(posts):
            if not isinstance(p, dict):
                failures.append(SchemaFailure(path=f"$.{posts_key}[{i}]", message="Must be an object"))
                continue
            if "section_id" not in p:
                failures.append(SchemaFailure(path=f"$.{posts_key}[{i}].section_id", message="Missing section_id"))
            if "title" not in p:
                failures.append(SchemaFailure(path=f"$.{posts_key}[{i}].title", message="Missing title"))

    result = "PASS" if not failures else "FAIL"
    return SchemaReport(result=result, failures=failures)

