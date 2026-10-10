"""PostgreSQL value parsers used by the HTAP instance capabilities."""

from __future__ import annotations

import re


def interval_seconds(value: str) -> float:
    """Parse a PostgreSQL duration string ('500ms', '30s', '1min', '2h', '1d').

    A bare number is interpreted as seconds. Unknown formats raise so the
    caller sees the raw value instead of a silently wrong timeout.
    """
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(ms|s|min|h|d)?\s*", value, re.IGNORECASE)
    if match is None:
        raise ValueError(f"Unsupported PostgreSQL interval value: value={value!r}")
    amount = float(match.group(1))
    unit = (match.group(2) or "s").casefold()
    multipliers = {"ms": 0.001, "s": 1.0, "min": 60.0, "h": 3600.0, "d": 86400.0}
    return amount * multipliers[unit]
