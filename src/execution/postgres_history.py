"""PostgreSQL historical records, statement deltas, logs, and SQL guard."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Mapping

from src.execution.history.records import HistoricalIntervalRecord, HistoricalPointRecord, HistoricalRecordSource


@dataclass(frozen=True, slots=True, kw_only=True, order=True)
class PgStatementKey:
    userid: int
    dbid: int
    queryid: int


@dataclass(frozen=True, slots=True, kw_only=True)
class PgStatementCounters:
    query: str
    calls: int
    total_exec_time_ms: float
    rows: int
    shared_blks_hit: int
    shared_blks_read: int
    shared_blks_written: int
    temp_blks_read: int
    temp_blks_written: int


@dataclass(frozen=True, slots=True, kw_only=True)
class PgStatementSnapshot:
    timestamp_ms: int
    counters: Mapping[PgStatementKey, PgStatementCounters]

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp_ms, int) or isinstance(self.timestamp_ms, bool) or self.timestamp_ms < 0:
            raise TypeError(f"PostgreSQL statement snapshot timestamp must be an epoch millisecond integer: timestamp_ms={self.timestamp_ms!r}")
        object.__setattr__(self, "counters", MappingProxyType(dict(self.counters)))


ADDITIVE_COUNTER_FIELDS = (
    "calls",
    "total_exec_time_ms",
    "rows",
    "shared_blks_hit",
    "shared_blks_read",
    "shared_blks_written",
    "temp_blks_read",
    "temp_blks_written",
)


PG_STATEMENT_SNAPSHOT_SQL = """
SELECT userid, dbid, queryid, query, calls, total_exec_time, rows,
       shared_blks_hit, shared_blks_read, shared_blks_written,
       temp_blks_read, temp_blks_written
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
"""


def snapshot_from_rows(timestamp_ms: int, rows: list[tuple[object, ...]]) -> PgStatementSnapshot:
    counters: dict[PgStatementKey, PgStatementCounters] = {}
    for row_number, row in enumerate(rows, start=1):
        if len(row) != 12:
            raise ValueError(f"PostgreSQL statement snapshot row has unexpected shape: row_number={row_number}, row={row!r}")
        userid, dbid, queryid, query, calls, total_exec_time, rows_count, shared_hit, shared_read, shared_written, temp_read, temp_written = row
        if queryid is None:
            raise ValueError(f"PostgreSQL statement snapshot queryid is null: row_number={row_number}, row={row!r}")
        key = PgStatementKey(userid=int(userid), dbid=int(dbid), queryid=int(queryid))
        counters[key] = PgStatementCounters(
            query=str(query),
            calls=int(calls or 0),
            total_exec_time_ms=float(total_exec_time or 0.0),
            rows=int(rows_count or 0),
            shared_blks_hit=int(shared_hit or 0),
            shared_blks_read=int(shared_read or 0),
            shared_blks_written=int(shared_written or 0),
            temp_blks_read=int(temp_read or 0),
            temp_blks_written=int(temp_written or 0),
        )
    return PgStatementSnapshot(timestamp_ms=timestamp_ms, counters=counters)


def capture_statement_snapshot(connection, timestamp_ms: int) -> PgStatementSnapshot:
    with connection.cursor() as cursor:
        cursor.execute(PG_STATEMENT_SNAPSHOT_SQL)
        rows = cursor.fetchall()
    return snapshot_from_rows(timestamp_ms, rows)


def build_topsql_delta_records(
    previous: PgStatementSnapshot,
    current: PgStatementSnapshot,
    *,
    target: str = "postgres",
    excluded_queryids: frozenset[int] = frozenset(),
) -> tuple[HistoricalIntervalRecord, ...]:
    if previous.timestamp_ms >= current.timestamp_ms:
        raise ValueError(
            f"PostgreSQL statement snapshots must be increasing: previous_timestamp_ms={previous.timestamp_ms}, "
            f"current_timestamp_ms={current.timestamp_ms}"
        )
    missing_keys = sorted(
        key for key in previous.counters
        if key not in current.counters and any(getattr(previous.counters[key], field) != 0 for field in ADDITIVE_COUNTER_FIELDS)
    )
    if missing_keys:
        raise RuntimeError(
            "PostgreSQL pg_stat_statements key disappeared between snapshots: "
            f"previous_timestamp_ms={previous.timestamp_ms}, current_timestamp_ms={current.timestamp_ms}, "
            f"keys={missing_keys!r}"
        )
    records = []
    zero = PgStatementCounters(
        query="",
        calls=0,
        total_exec_time_ms=0.0,
        rows=0,
        shared_blks_hit=0,
        shared_blks_read=0,
        shared_blks_written=0,
        temp_blks_read=0,
        temp_blks_written=0,
    )
    for key, current_counter in sorted(current.counters.items(), key=lambda item: (item[0].userid, item[0].dbid, item[0].queryid)):
        if key.queryid in excluded_queryids:
            continue
        previous_counter = previous.counters.get(key, zero)
        deltas = {
            field: getattr(current_counter, field) - getattr(previous_counter, field)
            for field in ADDITIVE_COUNTER_FIELDS
        }
        decreasing = {field: delta for field, delta in deltas.items() if delta < 0}
        if decreasing:
            raise RuntimeError(
                "PostgreSQL pg_stat_statements counter moved backwards: "
                f"query_key={key!r}, previous_timestamp_ms={previous.timestamp_ms}, "
                f"current_timestamp_ms={current.timestamp_ms}, fields={decreasing!r}"
            )
        if deltas["calls"] <= 0:
            continue
        total_latency = float(deltas["total_exec_time_ms"])
        records.append(HistoricalIntervalRecord(
            source=HistoricalRecordSource.TOPSQL,
            target=target,
            start_ms=previous.timestamp_ms,
            end_ms=current.timestamp_ms,
            payload={
                "digest": str(key.queryid),
                "sql_text": current_counter.query,
                "exec_count": deltas["calls"],
                "sum_latency": total_latency,
                "avg_latency": total_latency / deltas["calls"],
                "rows": deltas["rows"],
                "shared_blks_hit": deltas["shared_blks_hit"],
                "shared_blks_read": deltas["shared_blks_read"],
                "shared_blks_written": deltas["shared_blks_written"],
                "temp_blks_read": deltas["temp_blks_read"],
                "temp_blks_written": deltas["temp_blks_written"],
            },
        ))
    return tuple(records)


_PG_LOG_ENTRY_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d\d-\d\d[ T]\d\d:\d\d:\d\d(?:\.\d+)?(?:Z| UTC| GMT| ?[+-]\d\d(?::?\d\d)?))\s+"
    r"\[(?P<pid>\d+)\]\s+"
    r"(?:(?:app=(?P<application>\S*)\s+user=(?P<user>\S*)\s+db=(?P<database>\S*)\s+))?"
    r"(?P<level>[A-Z]+):\s?(?P<message>.*)$"
)
_PG_LEGACY_LOG_ENTRY_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d\d-\d\d[ T]\d\d:\d\d:\d\d(?:\.\d+)?(?:Z| UTC| GMT| ?[+-]\d\d(?::?\d\d)?))\s+"
    r"\[(?P<pid>\d+)\]\s+(?P<level>[A-Z]+):\s?(?P<message>.*)$"
)
_PG_LOG_TIMESTAMP_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d\d-\d\d[ T]\d\d:\d\d:\d\d(?:\.\d+)?(?:Z| UTC| GMT| ?[+-]\d\d(?::?\d\d)?))\s+"
)

_DOCKER_LOG_TIMESTAMP_RE = re.compile(
    r"^(?P<docker_timestamp>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z)\s+(?P<payload>.*)$"
)
_PG_LOG_TIMESTAMP_CANDIDATE_RE = re.compile(r"^\d{4}-\d\d-\d\d[ T]\d\d:\d\d:\d\d")


def _parse_pg_timestamp(raw: str, line_number: int) -> int:
    normalized = raw.strip().replace(" UTC", "+00:00").replace(" GMT", "+00:00").replace("Z", "+00:00")
    if "T" not in normalized:
        normalized = normalized.replace(" ", "T", 1)
    if re.search(r" [+-]\d\d\d\d$", normalized):
        normalized = normalized[:-5] + normalized[-5:-2] + ":" + normalized[-2:]
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
                raise ValueError(f"PostgreSQL log invalid timestamp: line_number={line_number}, timestamp={raw!r}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"PostgreSQL log timestamp lacks explicit timezone: line_number={line_number}, timestamp={raw!r}")
    return int(parsed.timestamp() * 1000)


def parse_postgres_log_records(raw: str, start_epoch_ms: int, end_epoch_ms: int) -> tuple[HistoricalPointRecord, ...]:
    records = []
    current: dict[str, object] | None = None
    discarding_malformed_entry = False

    def finish(entry: dict[str, object] | None) -> None:
        if entry is None:
            return
        timestamp_ms = int(entry["timestamp_ms"])
        if start_epoch_ms <= timestamp_ms <= end_epoch_ms:
            records.append(HistoricalPointRecord(
                source=HistoricalRecordSource.COMPONENT_LOG,
                target="postgres",
                timestamp_ms=timestamp_ms,
                payload={
                    "level": entry["level"],
                    "component": "postgres",
                    "message": entry["message"],
                    "application_name": entry["application_name"],
                    "pid": entry["pid"],
                    "user": entry["user"],
                    "database": entry["database"],
                },
            ))

    for line_number, line in enumerate(raw.splitlines(), start=1):
        docker_match = _DOCKER_LOG_TIMESTAMP_RE.match(line)
        if docker_match is not None:
            line = docker_match.group("payload")
        match = _PG_LOG_ENTRY_RE.match(line)
        legacy_match = None if match is not None else _PG_LEGACY_LOG_ENTRY_RE.match(line)
        if match is None:
            if legacy_match is not None:
                finish(current)
                current = {
                    "timestamp_ms": _parse_pg_timestamp(legacy_match.group("timestamp"), line_number),
                    "pid": int(legacy_match.group("pid")),
                    "application_name": "",
                    "user": "",
                    "database": "",
                    "level": legacy_match.group("level"),
                    "message": legacy_match.group("message"),
                }
                discarding_malformed_entry = False
                continue
            timestamp_match = _PG_LOG_TIMESTAMP_RE.match(line)
            if timestamp_match is not None:
                finish(current)
                current = None
                discarding_malformed_entry = False
                timestamp_ms = _parse_pg_timestamp(timestamp_match.group("timestamp"), line_number)
                if start_epoch_ms <= timestamp_ms <= end_epoch_ms:
                    raise ValueError(
                        f"PostgreSQL log entry has an invalid prefix: line_number={line_number}, line={line!r}"
                    )
                discarding_malformed_entry = True
                continue
            if _PG_LOG_TIMESTAMP_CANDIDATE_RE.match(line) is not None:
                raise ValueError(
                    f"PostgreSQL log entry has an invalid timestamp or prefix: line_number={line_number}, line={line!r}"
                )
            if discarding_malformed_entry:
                continue
            if current is None:
                raise ValueError(f"PostgreSQL log starts with a continuation line: line_number={line_number}, line={line!r}")
            current["message"] = f"{current['message']}\n{line}"
            continue
        finish(current)
        current = {
            "timestamp_ms": _parse_pg_timestamp(match.group("timestamp"), line_number),
            "pid": int(match.group("pid")),
            "application_name": match.group("application") or "",
            "user": match.group("user") or "",
            "database": match.group("database") or "",
            "level": match.group("level"),
            "message": match.group("message"),
        }
    finish(current)
    return tuple(sorted(records, key=lambda record: record.timestamp_ms))


def build_operation_event_records_from_logs(
    log_records: tuple[HistoricalPointRecord, ...],
) -> tuple[HistoricalPointRecord, ...]:
    """Project ordinary PostgreSQL log entries into the public event source.

    The projection keeps the original event details but exposes only stable
    operational fields. It deliberately does not attach fault, target, or
    expected-action labels; those relationships remain an Agent inference.
    """
    records = []
    for record in log_records:
        message = str(record.payload.get("message", ""))
        lowered = message.casefold()
        application = str(record.payload.get("application_name", "") or "")
        pid = str(record.payload.get("pid", "") or "")
        if "checkpoint" in lowered:
            event_type = "checkpoint"
            entity_type = "database"
            entity = "postgres"
            action = "start" if "starting" in lowered else "finish"
        elif "archive" in lowered or "archiver" in lowered:
            event_type = "archive_attempt"
            entity_type = "repository"
            entity = "archive_repository"
            action = "retry" if "retry" in lowered else "attempt"
        elif "base backup" in lowered or "pg_basebackup" in lowered or "backup" in lowered:
            event_type = "backup_run"
            entity_type = "backup"
            entity = application or "base_backup"
            action = "run"
        elif "duration:" in lowered and application:
            event_type = "job_run"
            entity_type = "workload"
            entity = application
            action = "execute"
        else:
            continue
        status = "failed" if any(term in lowered for term in ("failed", "error", "fatal")) else (
            "running" if any(term in lowered for term in ("starting", "begin", "running")) else "success"
        )
        correlation_id = f"{application or entity}:{pid}" if pid else application or entity
        records.append(HistoricalPointRecord(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target=record.target,
            timestamp_ms=record.timestamp_ms,
            payload={
                "event_type": event_type,
                "entity_type": entity_type,
                "entity": entity,
                "action": action,
                "status": status,
                "correlation_id": correlation_id,
                "details": message,
            },
        ))
    return tuple(records)


_DURATION_RE = re.compile(
    r"duration:\s*(?P<duration>\d+(?:\.\d+)?)\s*ms(?:\s+(?:statement|execute)\s*:?\s*(?P<sql>.*))?$",
    re.IGNORECASE | re.DOTALL,
)


def build_slow_query_records_from_logs(log_records: tuple[HistoricalPointRecord, ...]) -> tuple[HistoricalPointRecord, ...]:
    records = []
    for record in log_records:
        match = _DURATION_RE.search(str(record.payload["message"]))
        if match is None:
            continue
        sql_text = (match.group("sql") or "").strip()
        digest = hashlib.sha256(" ".join(sql_text.split()).casefold().encode()).hexdigest()[:16]
        payload = {
            "digest": digest,
            "sql_text": sql_text,
            "query_time_ms": float(match.group("duration")),
            "application_name": record.payload["application_name"],
            "pid": record.payload["pid"],
            "user": record.payload["user"],
            "database": record.payload["database"],
        }
        records.append(HistoricalPointRecord(
            source=HistoricalRecordSource.SLOW_QUERIES,
            target=record.target,
            timestamp_ms=record.timestamp_ms,
            payload=payload,
        ))
    return tuple(records)


HISTORICAL_FUNCTION_NAMES = frozenset({
    "pg_stat_statements_reset",
    "pg_read_file",
    "pg_read_binary_file",
    "pg_ls_logdir",
})
HISTORICAL_RELATION_NAMES = frozenset({"pg_stat_statements", "pg_stat_statements_info"})
_ALTER_SYSTEM_COMMAND = re.compile(
    r"^\s*ALTER\s+SYSTEM\s+(?:SET|RESET)\s+[A-Za-z_][A-Za-z0-9_.]*\b.*$",
    re.IGNORECASE | re.DOTALL,
)

# sqlglot represents PostgreSQL ALTER ROLE syntax as Command. Keep the public
# history surface usable for the bounded role-level governance action while
# rejecting arbitrary command text and multi-statement payloads.
_SAFE_ROLE_CONNECTION_LIMIT_RE = re.compile(
    r"\A\s*ALTER\s+(?:ROLE|USER)\s+"
    r"(?P<role>[A-Za-z_][A-Za-z0-9_$]*)\s+"
    r"CONNECTION\s+LIMIT\s+(?P<limit>-?\d+)\s*;?\s*\Z",
    re.IGNORECASE,
)


def _is_safe_public_postgres_command(statement: object) -> bool:
    """Allow current-state configuration and bounded role commands only."""
    from sqlglot import exp

    if not isinstance(statement, exp.Command):
        return False
    if _SAFE_ROLE_CONNECTION_LIMIT_RE.fullmatch(str(statement).strip()) is not None:
        return True
    return _ALTER_SYSTEM_COMMAND.fullmatch(statement.sql(dialect="postgres")) is not None


def reject_postgres_public_historical_sql(
    sql_query: str,
    *,
    protected_relations: frozenset[str] = frozenset(),
    protected_relation_names: tuple[str, ...] = (),
) -> None:
    from sqlglot import exp, parse
    from sqlglot.errors import ParseError

    try:
        statements = parse(sql_query, read="postgres")
    except ParseError as exc:
        raise ValueError(f"Cannot parse SQL for PostgreSQL historical-query validation: query={sql_query!r}, error={exc}") from exc
    if not statements:
        raise ValueError("PostgreSQL historical-query validation received an empty SQL statement")
    if len(statements) != 1:
        raise ValueError(
            "PostgreSQL historical-query validation rejects multi-statement commands that could reach "
            "physical historical telemetry: "
            f"query={sql_query!r}"
        )
    for statement in statements:
        if isinstance(statement, exp.Command):
            if _is_safe_public_postgres_command(statement):
                continue
            raise ValueError(
                "PostgreSQL historical-query validation rejects uninspectable SQL commands: "
                f"statement={statement!r}, query={sql_query!r}"
            )
        protected_names = {
            str(relation).strip().casefold()
            for relation in (*protected_relations, *protected_relation_names)
            if str(relation).strip()
        }
        for table in statement.find_all(exp.Table):
            table_name = str(table.name).casefold()
            schema_name = str(getattr(table, "db", "") or "").casefold()
            qualified_name = f"{schema_name}.{table_name}" if schema_name else table_name
            if table_name in HISTORICAL_RELATION_NAMES:
                raise ValueError(
                    "PostgreSQL frozen-history Case forbids physical historical telemetry access: "
                    f"relation={table.name!r}, use=query_metrics or execute_sql(target='history'), query={sql_query!r}"
                )
            if table_name in protected_names or qualified_name in protected_names:
                raise ValueError(
                    "PostgreSQL frozen-history Case forbids physical historical telemetry access to a protected runtime relation: "
                    f"relation={qualified_name!r}, use=the declared public tool contract, query={sql_query!r}"
                )
        for node in statement.walk():
            name = str(getattr(node, "name", "") or getattr(node, "this", "")).casefold()
            if name in HISTORICAL_FUNCTION_NAMES or node.__class__.__name__.casefold() in HISTORICAL_FUNCTION_NAMES:
                raise ValueError(
                    "PostgreSQL frozen-history Case forbids physical historical telemetry access: "
                    f"function={name!r}, use=query_metrics or execute_sql(target='history'), query={sql_query!r}"
                )


__all__ = [
    "ADDITIVE_COUNTER_FIELDS",
    "PgStatementCounters",
    "PgStatementKey",
    "PgStatementSnapshot",
    "PG_STATEMENT_SNAPSHOT_SQL",
    "build_slow_query_records_from_logs",
    "build_operation_event_records_from_logs",
    "build_topsql_delta_records",
    "capture_statement_snapshot",
    "parse_postgres_log_records",
    "reject_postgres_public_historical_sql",
    "snapshot_from_rows",
]
