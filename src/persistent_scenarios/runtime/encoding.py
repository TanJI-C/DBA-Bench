"""Canonical JSON encoding for trace and ledger artifacts."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
from collections.abc import Mapping
from typing import Any


def jsonable(value: Any) -> Any:
    """Convert dataclasses/enums/mappings into strictly JSON-serializable shapes."""
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {
            field.name: jsonable(getattr(value, field.name))
            for field in fields(value)
            if field.name != "provider_handle"
        }
    if isinstance(value, Mapping):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value
