from __future__ import annotations

from pydantic import ValidationError

from ..models import WorkflowInput


def validate_input(raw: dict) -> WorkflowInput:
    try:
        return WorkflowInput.model_validate(raw)
    except ValidationError as e:
        raise ValueError(e.json()) from e
