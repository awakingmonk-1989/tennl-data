from __future__ import annotations

from typing import Any

from .schema_validation import validate_article_schema


def final_validate(article_md: str, article_json: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []

    if not article_md.strip():
        failures.append({"check": "article_md_nonempty", "message": "article_md is empty"})
    if not isinstance(article_json, dict) or not article_json:
        failures.append({"check": "article_json_nonempty", "message": "article_json is empty"})

    schema = validate_article_schema(article_json)
    if schema.result != "PASS":
        failures.append(
            {
                "check": "schema_validation",
                "message": "Schema validation failed",
                "details": schema.model_dump(),
            }
        )

    return {"result": "PASS" if not failures else "FAIL", "failures": failures}

