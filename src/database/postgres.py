"""PostgreSQL plan and catalog helpers."""

"""Shared helpers for parsing PostgreSQL EXPLAIN ANALYZE plan output.

Both the MissingIndex evaluator and the fault injector need to extract
``Execution Time`` from a plan result that may be a JSON string, a dict,
or a list (e.g. ``{"result": [[[{... "Execution Time": 31280.932}]]]}``).

This module centralises the walker so the two call sites stay in sync.
"""
import json
import re
from typing import Any, Iterator, Optional

import psycopg2


def connect_postgres_role(env, role: str, application_name: str):
    """Open an authenticated login without inheriting the Agent's SQL session settings."""
    return psycopg2.connect(
        host=env.host, port=env.port, dbname=env.dbname,
        user=role, password=env.password, connect_timeout=3,
        application_name=application_name,
    )


def postgres_work_mem_bytes(cursor) -> int:
    """Read PostgreSQL's canonical kB value, including login configuration precedence."""
    cursor.execute("SELECT setting::bigint * 1024 FROM pg_settings WHERE name = 'work_mem'")
    return cursor.fetchone()[0]


def postgres_stored_work_mem_bytes(cursor, *, database: str | None, role: str | None) -> int | None:
    """Read one exact catalog scope; normalize with PostgreSQL inside a rollback-only transaction.

    None means this scope has no stored work_mem. The caller owns the transaction and must
    roll it back: set_config below is only for interpreting PostgreSQL units, not a repair.
    """
    cursor.execute(
        "SELECT split_part(cfg, '=', 2) FROM pg_db_role_setting s, unnest(s.setconfig) cfg "
        "WHERE s.setdatabase = CASE WHEN %s IS NULL THEN 0 "
        "ELSE (SELECT oid FROM pg_database WHERE datname = %s) END "
        "AND s.setrole = CASE WHEN %s IS NULL THEN 0 "
        "ELSE (SELECT oid FROM pg_roles WHERE rolname = %s) END "
        "AND cfg LIKE 'work_mem=%%'",
        (database, database, role, role),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    cursor.execute("SELECT set_config('work_mem', %s, true)", (row[0],))
    return postgres_work_mem_bytes(cursor)


# The text-form regex is used only for the fallback below; structured
# EXPLAIN (FORMAT JSON) output is walked by `_walk_json_values`.
_EXEC_TIME_RE_TEXT = re.compile(r"Execution Time:\s*([0-9.]+)\s*ms", re.IGNORECASE)
_EXEC_TIME_RE_JSON_QUOTED = re.compile(r'"Execution Time"\s*:\s*([0-9.]+)', re.IGNORECASE)


def _walk_json_values(value: Any) -> Iterator[Any]:
    """Yield ``value`` and every nested dict/list value, depth-first."""
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk_json_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_json_values(child)


def _json_execution_time_ms(raw_result: Any) -> Optional[float]:
    """Find ``Execution Time`` (ms) inside a structured EXPLAIN JSON payload."""
    if isinstance(raw_result, str):
        try:
            raw_result = json.loads(raw_result)
        except (json.JSONDecodeError, TypeError, ValueError):
            return None
    for value in _walk_json_values(raw_result):
        if isinstance(value, dict) and "Execution Time" in value:
            try:
                return float(value["Execution Time"])
            except (TypeError, ValueError):
                return None
    return None


def execution_time_seconds(raw_result: Any) -> Optional[float]:
    """Return plan ``Execution Time`` in seconds, or None if not parseable.

    Tries structured JSON first, then falls back to the textual
    ``Execution Time: N ms`` form. Returns None when neither is found.
    """
    ms = _json_execution_time_ms(raw_result)
    if ms is not None:
        return ms / 1000.0
    if isinstance(raw_result, str):
        match = _EXEC_TIME_RE_TEXT.search(raw_result)
        if match:
            return float(match.group(1)) / 1000.0
        match = _EXEC_TIME_RE_JSON_QUOTED.search(raw_result)
        if match:
            return float(match.group(1)) / 1000.0
    return None

from dataclasses import dataclass

from sqlglot import exp, parse_one


POSTGRES_INDEX_CATALOG_SQL = (
    "SELECT schemaname, tablename, indexname, indexdef, i.indisvalid "
    "FROM pg_indexes x JOIN pg_class c ON c.relname = x.indexname "
    "JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = x.schemaname "
    "JOIN pg_index i ON i.indexrelid = c.oid "
    "WHERE schemaname NOT IN ('pg_catalog', 'information_schema') "
    "ORDER BY 1, 2, 3"
)


@dataclass(frozen=True, slots=True)
class PostgresIndexSignature:
    schema: str
    table: str
    expression: str
    included_columns: tuple[str, ...] = ()

    def matches(self, row: tuple | list) -> bool:
        if len(row) < 5:
            raise ValueError(f"PostgreSQL index catalog row must have five columns: row={row!r}")
        return (
            str(row[0]).casefold() == self.schema.casefold()
            and str(row[1]).casefold() == self.table.casefold()
            and self.matches_definition(str(row[3]))
        )

    def matches_definition(self, definition: str) -> bool:
        statement = parse_one(definition, read="postgres")
        if not isinstance(statement, exp.Create) or str(statement.args.get("kind", "")).upper() != "INDEX":
            return False
        index = statement.this
        if not isinstance(index, exp.Index):
            return False
        if index.args.get("unique"):
            return False
        table = index.args.get("table")
        if not isinstance(table, exp.Table) or table.name.casefold() != self.table.casefold():
            return False
        if table.db and table.db.casefold() != self.schema.casefold():
            return False
        parameters = index.args.get("params")
        if type(parameters).__name__ != "IndexParameters":
            return False
        using = parameters.args.get("using")
        if using is not None and using.name.casefold() != "btree":
            return False
        include = parameters.args.get("include") or ()
        actual_include = tuple(
            item.name.casefold()
            for item in include
            if isinstance(item, exp.Identifier)
        )
        if len(actual_include) != len(include):
            return False
        expected_include = tuple(column.casefold() for column in self.included_columns)
        if actual_include != expected_include:
            return False
        if parameters.args.get("where"):
            return False
        columns = parameters.args.get("columns") or ()
        if len(columns) != 1 or not isinstance(columns[0], exp.Ordered):
            return False
        return self._canonical_expression(columns[0].this) == self._canonical_expression(
            parse_one(self.expression, read="postgres")
        )

    @staticmethod
    def _canonical_expression(expression: exp.Expression) -> exp.Expression:
        def unwrap(node):
            if isinstance(node, exp.Paren):
                return node.this
            if (
                isinstance(node, exp.Cast)
                and node.to.sql(dialect="postgres").casefold() == "text"
            ):
                return node.this
            return node

        current = expression.copy()
        while True:
            normalized = current.transform(unwrap)
            if normalized == current:
                return normalized
            current = normalized

    def as_dict(self) -> dict[str, str]:
        return {
            "schema": self.schema,
            "table": self.table,
            "expression": self.expression,
            "included_columns": list(self.included_columns),
        }
