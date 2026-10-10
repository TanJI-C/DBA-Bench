"""Strict JSON serialization for authoritative benchmark artifacts."""

from __future__ import annotations

import json
import math
from decimal import Decimal
from typing import Any


def _json_default(value: Any) -> int | float:
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _reject_non_finite(value: Any, path: str = "$", seen: set[int] | None = None) -> None:
    seen = set() if seen is None else seen
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"Non-finite JSON number at {path}: value={value!r}")
        return
    if isinstance(value, dict):
        identity = id(value)
        if identity in seen:
            raise ValueError(f"Cyclic artifact value at {path}")
        seen.add(identity)
        for key, item in value.items():
            _reject_non_finite(item, f"{path}.{key}", seen)
        seen.remove(identity)
    elif isinstance(value, (list, tuple)):
        identity = id(value)
        if identity in seen:
            raise ValueError(f"Cyclic artifact value at {path}")
        seen.add(identity)
        for index, item in enumerate(value):
            _reject_non_finite(item, f"{path}[{index}]", seen)
        seen.remove(identity)


def strict_json_dumps(value: Any, *, indent: int | None = None, sort_keys: bool = False) -> str:
    _reject_non_finite(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        indent=indent,
        sort_keys=sort_keys,
        default=_json_default,
    )


def strict_json_loads(text: str, *, context: str) -> Any:
    def reject_constant(token: str) -> None:
        raise ValueError(f"Non-standard JSON constant at {context}: token={token!r}")

    value = json.loads(text, parse_constant=reject_constant)
    _reject_non_finite(value, context)
    return value


def validate_trace_document(value: Any, *, schema: str, context: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"Trace must be a JSON object: context={context!r}, type={type(value).__name__}")
    if value.get("$schema") != schema:
        raise ValueError(f"Trace schema mismatch: context={context!r}, expected={schema!r}, got={value.get('$schema')!r}")
    metadata = value.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"Trace metadata must be an object: context={context!r}")
    missing = {field for field in ("run_id", "scenario_id") if not metadata.get(field)}
    if missing:
        raise ValueError(f"Trace metadata is incomplete: context={context!r}, missing={sorted(missing)}")
