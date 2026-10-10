"""Database SQL response and literal helpers."""

"""Shared JSON response validation for environment and SQL tools."""

import json
from collections.abc import Callable
from typing import Any


def parse_json_object(raw: Any, context: str) -> dict[str, Any]:
    payload = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(payload, dict):
        raise TypeError(f"{context} expected a JSON object, got {type(payload).__name__}: response={raw!r}")
    return payload


def require_success_payload(raw: Any, context: str) -> dict[str, Any]:
    payload = parse_json_object(raw, context)
    if payload.get("status") != "success":
        raise RuntimeError(f"{context} failed: response={payload!r}")
    return payload


def require_result_rows(raw: Any, context: str) -> list:
    payload = require_success_payload(raw, context)
    rows = payload.get("result")
    if not isinstance(rows, list):
        raise TypeError(f"{context} returned invalid result rows: response={payload!r}")
    return rows


def require_one_result_row(rows: list, context: str) -> list:
    if len(rows) != 1 or not isinstance(rows[0], (list, tuple)):
        raise ValueError(f"{context} expected one result row: rows={rows!r}")
    return list(rows[0])


def execute_json_payload(execute: Callable[[str], Any], sql: str, context: str) -> dict[str, Any]:
    return require_success_payload(execute(sql), f"{context}: sql={sql!r}")


def execute_result_rows(execute: Callable[[str], Any], sql: str, context: str) -> list:
    return require_result_rows(execute(sql), f"{context}: sql={sql!r}")

"""Shared SQL string-literal rendering."""


def sql_escape(value: object) -> str:
    return str(value).replace("'", "''")


def sql_literal(value: object) -> str:
    return "'" + sql_escape(value) + "'"


def sequence_row_source(rows: int) -> str:
    """Deterministic subquery producing n = 1..rows as column `n`.

    Two-level recursion keeps each CTE under TiDB's default cte_max_recursion_depth
    (1000) and avoids catalog cross joins whose intermediate result TiDB cancels
    with memory error 8176.
    """
    if rows <= 0:
        raise ValueError(f"sequence row count must be positive: rows={rows}")
    tail = 200
    head = (rows + tail - 1) // tail
    return (
        "SELECT n "
        "FROM (WITH RECURSIVE head(h) AS (SELECT 1 UNION ALL SELECT h + 1 FROM head WHERE h < {head}), "
        "tail(t) AS (SELECT 1 UNION ALL SELECT t + 1 FROM tail WHERE t < {tail}) "
        "SELECT (head.h - 1) * 200 + tail.t AS n FROM head CROSS JOIN tail "
        "WHERE (head.h - 1) * 200 + tail.t <= {rows}) source"
    ).format(head=head, tail=tail, rows=rows)
