"""Read-only SQL view over a frozen history record store."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from sqlglot import exp, parse
from sqlglot.errors import ParseError

from src.execution.history.records import (
    FrozenHistoricalRecordStore,
    HistoricalRecordSource,
)


def _sql_timestamp(timestamp_ms: int) -> str:
    return datetime.fromtimestamp(timestamp_ms / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")


_ALLOWED_TABLES = frozenset({"statement_summary", "slow_query"})
_TIME_COLUMNS = {
    "statement_summary": frozenset({"event_start_utc", "event_end_utc"}),
    "slow_query": frozenset({"event_time_utc"}),
}
_DENIED_SQLITE_ACTIONS = frozenset(
    action
    for action in (
        getattr(sqlite3, name, None)
        for name in (
            "SQLITE_ALTER_TABLE",
            "SQLITE_ANALYZE",
            "SQLITE_ATTACH",
            "SQLITE_CREATE_INDEX",
            "SQLITE_CREATE_TABLE",
            "SQLITE_CREATE_TEMP_INDEX",
            "SQLITE_CREATE_TEMP_TABLE",
            "SQLITE_CREATE_TEMP_TRIGGER",
            "SQLITE_CREATE_TEMP_VIEW",
            "SQLITE_CREATE_TRIGGER",
            "SQLITE_CREATE_VIEW",
            "SQLITE_DELETE",
            "SQLITE_DETACH",
            "SQLITE_DROP_INDEX",
            "SQLITE_DROP_TABLE",
            "SQLITE_DROP_TEMP_INDEX",
            "SQLITE_DROP_TEMP_TABLE",
            "SQLITE_DROP_TEMP_TRIGGER",
            "SQLITE_DROP_TEMP_VIEW",
            "SQLITE_DROP_TRIGGER",
            "SQLITE_DROP_VIEW",
            "SQLITE_INSERT",
            "SQLITE_PRAGMA",
            "SQLITE_REINDEX",
            "SQLITE_TRANSACTION",
            "SQLITE_UPDATE",
        )
    )
    if action is not None
)


class FrozenHistoricalSqlArchive:
    """Materialize SQL records into a private, bounded, read-only SQLite view."""

    def __init__(
        self,
        record_store: FrozenHistoricalRecordStore,
        max_rows: int,
        visible_start_ms: int,
        visible_end_ms: int,
        *,
        sql_dialect: str = "mysql",
        require_time_bounds: bool = False,
        max_response_bytes: int = 128 * 1024,
    ) -> None:
        if not isinstance(max_rows, int) or isinstance(max_rows, bool) or max_rows <= 0:
            raise ValueError(f"history SQL max_rows must be a positive integer: max_rows={max_rows!r}")
        if not isinstance(max_response_bytes, int) or isinstance(max_response_bytes, bool) or max_response_bytes <= 0:
            raise ValueError(
                "history SQL max_response_bytes must be a positive integer: "
                f"max_response_bytes={max_response_bytes!r}"
            )
        if visible_start_ms >= visible_end_ms:
            raise ValueError(
                "history SQL visible range must be positive: "
                f"visible_start_ms={visible_start_ms}, visible_end_ms={visible_end_ms}"
            )
        self.max_rows = max_rows
        self.max_response_bytes = max_response_bytes
        self.visible_start_ms = visible_start_ms
        self.visible_end_ms = visible_end_ms
        self.sql_dialect = sql_dialect
        self.require_time_bounds = require_time_bounds
        self._closed = False
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self._create_tables()
        self._insert_records(record_store)
        self.connection.execute("PRAGMA query_only = ON")
        self.connection.set_authorizer(self._authorize)

    def _create_tables(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE statement_summary (
                event_start_utc TEXT NOT NULL,
                event_end_utc TEXT NOT NULL,
                instance TEXT NOT NULL,
                resource_group TEXT,
                digest TEXT,
                plan_digest TEXT,
                sql_text TEXT,
                exec_count REAL,
                avg_latency REAL,
                sum_latency REAL,
                avg_total_keys REAL,
                avg_processed_keys REAL,
                avg_mem REAL,
                max_mem REAL,
                avg_disk REAL,
                max_disk REAL,
                rows REAL,
                shared_blks_hit REAL,
                shared_blks_read REAL,
                shared_blks_written REAL,
                temp_blks_read REAL,
                temp_blks_written REAL
            );
            CREATE INDEX idx_statement_time ON statement_summary(event_start_utc, event_end_utc);
            CREATE INDEX idx_statement_digest ON statement_summary(digest);
            CREATE TABLE slow_query (
                event_time_utc TEXT NOT NULL,
                instance TEXT NOT NULL,
                digest TEXT,
                sql_text TEXT,
                query_time_ms REAL,
                process_time_ms REAL,
                wait_time_ms REAL,
                backoff_time_ms REAL,
                total_keys REAL,
                process_keys REAL,
                mem_max REAL,
                disk_max REAL,
                application_name TEXT,
                pid INTEGER,
                user_name TEXT,
                database_name TEXT
            );
            CREATE INDEX idx_slow_time ON slow_query(event_time_utc);
            CREATE INDEX idx_slow_digest ON slow_query(digest);
            """
        )

    def _insert_records(self, store: FrozenHistoricalRecordStore) -> None:
        for records in store.interval_records.values():
            for record in records:
                if record.source is not HistoricalRecordSource.TOPSQL:
                    continue
                p = dict(record.payload)
                self.connection.execute(
                    "INSERT INTO statement_summary VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (_sql_timestamp(record.start_ms), _sql_timestamp(record.end_ms), p.get("instance") or record.target,
                     p.get("resource_group"), p.get("digest"), p.get("plan_digest"), p.get("sql_text"),
                     p.get("exec_count"), p.get("avg_latency"), p.get("sum_latency"), p.get("avg_total_keys"),
                     p.get("avg_processed_keys"), p.get("avg_mem"), p.get("max_mem"), p.get("avg_disk"), p.get("max_disk"),
                     p.get("rows"), p.get("shared_blks_hit"), p.get("shared_blks_read"), p.get("shared_blks_written"),
                     p.get("temp_blks_read"), p.get("temp_blks_written")),
                )
        for records in store.point_records.values():
            for record in records:
                if record.source is not HistoricalRecordSource.SLOW_QUERIES:
                    continue
                p = dict(record.payload)
                self.connection.execute(
                    "INSERT INTO slow_query VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (_sql_timestamp(record.timestamp_ms), p.get("instance") or record.target, p.get("digest"), p.get("sql_text"),
                     p.get("query_time_ms"), p.get("process_time_ms"), p.get("wait_time_ms"), p.get("backoff_time_ms"),
                     p.get("total_keys"), p.get("process_keys"), p.get("mem_max"), p.get("disk_max"),
                     p.get("application_name"), p.get("pid"), p.get("user"), p.get("database")),
                )
        self.connection.commit()

    @staticmethod
    def _authorize(action: int, _arg1: str | None, _arg2: str | None, _database: str | None, _trigger: str | None) -> int:
        return sqlite3.SQLITE_DENY if action in _DENIED_SQLITE_ACTIONS else sqlite3.SQLITE_OK

    @staticmethod
    def _comparison_bounds(statement: exp.Expression, time_columns: frozenset[str]) -> tuple[bool, bool]:
        def is_bound_value(node: exp.Expression) -> bool:
            return not any(True for _ in node.find_all(exp.Column))

        lower = False
        upper = False
        for node in statement.walk():
            if isinstance(node, exp.Between):
                subject = node.this
                if (
                    isinstance(subject, exp.Column)
                    and subject.name.casefold() in time_columns
                    and is_bound_value(node.args["low"])
                    and is_bound_value(node.args["high"])
                ):
                    lower = True
                    upper = True
                continue
            if not isinstance(node, (exp.GT, exp.GTE, exp.LT, exp.LTE)):
                continue
            left = node.this
            right = node.expression
            left_is_time = isinstance(left, exp.Column) and left.name.casefold() in time_columns
            right_is_time = isinstance(right, exp.Column) and right.name.casefold() in time_columns
            if left_is_time == right_is_time:
                continue
            bound_value = right if left_is_time else left
            if not is_bound_value(bound_value):
                continue
            if left_is_time:
                lower = lower or isinstance(node, (exp.GT, exp.GTE))
                upper = upper or isinstance(node, (exp.LT, exp.LTE))
            else:
                lower = lower or isinstance(node, (exp.LT, exp.LTE))
                upper = upper or isinstance(node, (exp.GT, exp.GTE))
        return lower, upper

    def _validate_time_bounds(self, statement: exp.Expression, tables: frozenset[str]) -> None:
        time_columns = frozenset(
            column
            for table in tables
            for column in _TIME_COLUMNS[table]
        )
        lower, upper = self._comparison_bounds(statement, time_columns)
        if not lower or not upper:
            raise ValueError(
                "history SQL requires explicit lower and upper UTC time bounds: "
                f"tables={sorted(tables)!r}, time_columns={sorted(time_columns)!r}"
            )

    def _parse_statement(self, sql: str) -> tuple[exp.Expression, bool]:
        try:
            statements = parse(sql, read=self.sql_dialect)
        except ParseError as exc:
            raise ValueError(f"cannot parse history SQL: dialect={self.sql_dialect!r}, error={exc}") from exc
        if len(statements) != 1:
            raise ValueError(f"history SQL accepts exactly one statement: statement_count={len(statements)}")
        statement = statements[0]
        if statement.key == "select":
            return statement, False
        if statement.key == "describe" and isinstance(statement.this, exp.Select):
            return statement.this, True
        if statement.key == "command" and str(statement.this).casefold() == "explain":
            inner_sql = str(statement.expression.this)
            try:
                inner_statements = parse(inner_sql, read=self.sql_dialect)
            except ParseError as exc:
                raise ValueError(f"cannot parse history EXPLAIN query: dialect={self.sql_dialect!r}, error={exc}") from exc
            if len(inner_statements) == 1 and inner_statements[0].key == "select":
                return inner_statements[0], True
        raise ValueError("history SQL is read-only and accepts only SELECT or EXPLAIN SELECT")

    def execute(self, sql: str) -> tuple[list[str], list[tuple[object, ...]], int, bool]:
        if self._closed:
            raise RuntimeError("history SQL archive is closed")
        statement, _is_explain = self._parse_statement(sql)
        cte_names = frozenset(
            str(cte.alias_or_name).casefold()
            for cte in statement.find_all(exp.CTE)
        )
        tables = frozenset(
            table.name.casefold()
            for table in statement.find_all(exp.Table)
            if table.name.casefold() not in cte_names
        )
        if not tables or not tables <= _ALLOWED_TABLES:
            raise ValueError(f"history SQL may query only statement_summary or slow_query: tables={sorted(tables)!r}")
        if self.require_time_bounds:
            self._validate_time_bounds(statement, tables)
        try:
            cursor = self.connection.execute(sql)
        except sqlite3.DatabaseError as exc:
            raise ValueError(f"history SQL execution failed: {exc}") from exc
        rows = cursor.fetchmany(self.max_rows + 1)
        truncated = len(rows) > self.max_rows
        rows = rows[: self.max_rows]
        bounded_rows: list[tuple[object, ...]] = []
        encoded_bytes = 2
        for row in rows:
            candidate = tuple(row)
            row_bytes = len(json.dumps(candidate, ensure_ascii=False, default=str).encode("utf-8")) + 1
            if bounded_rows and encoded_bytes + row_bytes > self.max_response_bytes:
                truncated = True
                break
            if not bounded_rows and row_bytes > self.max_response_bytes:
                raise ValueError(
                    "history SQL first row exceeds response budget: "
                    f"row_bytes={row_bytes}, max_response_bytes={self.max_response_bytes}"
                )
            bounded_rows.append(candidate)
            encoded_bytes += row_bytes
        return [column[0] for column in cursor.description], bounded_rows, len(bounded_rows), truncated

    def close(self) -> None:
        if self._closed:
            return
        self.connection.close()
        self._closed = True
