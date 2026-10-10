"""TiDB historical record parsers and the MySQL public SQL guard."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Mapping

from src.execution.history.records import (
    HistoricalIntervalRecord,
    HistoricalPointRecord,
    HistoricalRecordSource,
)


_DOCKER_TIMESTAMP_RE = re.compile(r"^(?P<timestamp>[^\s]+)\s+(?P<message>.*)$")
_COMPOSE_PREFIX_RE = re.compile(r"^[^\s]+\s+\|\s+(?P<line>.*)$")
_LOG_LEVEL_RE = re.compile(
    r"^(?:\[(?P<bracket>[A-Z]+)\]|(?P<plain>[A-Z]+))\s+(?P<rest>.*)$",
    re.DOTALL,
)
_LOG_COMPONENT_RE = re.compile(
    r"^(?P<component>[A-Za-z0-9_.-]+):\s*(?P<message>.*)$",
    re.DOTALL,
)


def _timestamp_to_ms(value: object, field: str) -> int:
    if isinstance(value, datetime):
        parsed = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return int(parsed.timestamp() * 1000)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return int(float(value) * (1000 if float(value) < 100_000_000_000 else 1))
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        normalized = re.sub(r"(\.\d{6})\d+(?=[+-]\d\d:\d\d$)", r"\1", normalized)
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError(f"Cannot parse historical timestamp: field={field!r}, value={value!r}") from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return int(parsed.timestamp() * 1000)
    raise TypeError(f"Historical timestamp must be datetime, number, or ISO string: field={field!r}, value={value!r}")


def parse_docker_log_records(raw: str, target: str, start_ms: int, end_ms: int) -> tuple[HistoricalPointRecord, ...]:
    """Parse Docker's RFC3339-prefixed TiDB log output."""
    entries: list[tuple[int, str, str]] = []
    for line_number, line in enumerate(raw.splitlines(), start=1):
        compose_match = _COMPOSE_PREFIX_RE.match(line)
        if compose_match is not None:
            line = compose_match.group("line")
        match = _DOCKER_TIMESTAMP_RE.match(line)
        raw_timestamp = match.group("timestamp") if match is not None else ""
        timestamped = (
            "T" in raw_timestamp
            and ("Z" in raw_timestamp or "+" in raw_timestamp or "-" in raw_timestamp[10:])
        )
        if not timestamped:
            if "T" in raw_timestamp:
                raise ValueError(
                    "Docker log timestamp must be RFC3339 with an explicit timezone: "
                    f"target={target!r}, line_number={line_number}, timestamp={raw_timestamp!r}"
                )
            if entries:
                entry_line, entry_timestamp, entry_message = entries[-1]
                entries[-1] = (entry_line, entry_timestamp, f"{entry_message}\n{line}")
                continue
            raise ValueError(
                "Docker log starts with a continuation line before any RFC3339 timestamp: "
                f"target={target!r}, line_number={line_number}, line={line!r}"
            )
        entries.append((line_number, raw_timestamp, match.group("message")))

    records = []
    for line_number, raw_timestamp, message in entries:
        timestamp_ms = _timestamp_to_ms(raw_timestamp, f"docker_log[{line_number}]")
        if not start_ms <= timestamp_ms <= end_ms:
            raise ValueError(
                f"Docker log timestamp falls outside capture window: target={target!r}, line_number={line_number}, "
                f"timestamp_ms={timestamp_ms}, window=({start_ms},{end_ms})"
            )
        payload: dict[str, object] = {"message": message}
        level_match = _LOG_LEVEL_RE.match(message)
        if level_match is not None:
            payload["level"] = level_match.group("bracket") or level_match.group("plain")
            message = level_match.group("rest")
            payload["message"] = message
        component_match = _LOG_COMPONENT_RE.match(message)
        if component_match is not None:
            payload["component"] = component_match.group("component")
            payload["message"] = component_match.group("message")
        records.append(HistoricalPointRecord(
            source=HistoricalRecordSource.COMPONENT_LOG,
            target=target,
            timestamp_ms=timestamp_ms,
            payload=payload,
        ))
    return tuple(records)


def build_topsql_records(rows: list[Mapping[str, object]], target: str, start_ms: int, end_ms: int) -> tuple[HistoricalIntervalRecord, ...]:
    records = []
    seen = set()
    for row_number, row in enumerate(rows, start=1):
        begin = _row_value(row, ("SUMMARY_BEGIN_TIME", "summary_begin_time"), row_number, "SUMMARY_BEGIN_TIME")
        end = _row_value(row, ("SUMMARY_END_TIME", "summary_end_time"), row_number, "SUMMARY_END_TIME")
        begin_ms = _timestamp_to_ms(begin, f"topsql[{row_number}].SUMMARY_BEGIN_TIME")
        end_ms_value = _timestamp_to_ms(end, f"topsql[{row_number}].SUMMARY_END_TIME")
        if begin_ms >= end_ms_value:
            raise ValueError(f"TopSQL interval is not positive: target={target!r}, row_number={row_number}, row={row!r}")
        if end_ms_value < start_ms or begin_ms > end_ms:
            continue
        key = (
            str(row.get("INSTANCE", row.get("instance", ""))),
            str(row.get("RESOURCE_GROUP", row.get("resource_group", ""))),
            str(row.get("DIGEST", row.get("digest", ""))),
            str(row.get("PLAN_DIGEST", row.get("plan_digest", ""))),
            begin_ms,
            end_ms_value,
        )
        if key in seen:
            continue
        seen.add(key)
        payload = {
            "instance": row.get("INSTANCE", row.get("instance")),
            "resource_group": row.get("RESOURCE_GROUP", row.get("resource_group")),
            "digest": row.get("DIGEST", row.get("digest")),
            "plan_digest": row.get("PLAN_DIGEST", row.get("plan_digest")),
            "sql_text": row.get("DIGEST_TEXT", row.get("digest_text")),
            "exec_count": row.get("EXEC_COUNT", row.get("exec_count")),
            "avg_latency": row.get("AVG_LATENCY", row.get("avg_latency")),
            "sum_latency": row.get("SUM_LATENCY", row.get("sum_latency")),
            "avg_total_keys": row.get("AVG_TOTAL_KEYS", row.get("avg_total_keys")),
            "avg_processed_keys": row.get("AVG_PROCESSED_KEYS", row.get("avg_processed_keys")),
            "avg_mem": row.get("AVG_MEM", row.get("avg_mem")),
            "max_mem": row.get("MAX_MEM", row.get("max_mem")),
            "avg_disk": row.get("AVG_DISK", row.get("avg_disk")),
            "max_disk": row.get("MAX_DISK", row.get("max_disk")),
        }
        records.append(HistoricalIntervalRecord(
            source=HistoricalRecordSource.TOPSQL,
            target=target,
            start_ms=begin_ms,
            end_ms=end_ms_value,
            payload=payload,
        ))
    return tuple(sorted(records, key=lambda item: (item.start_ms, item.end_ms, item.target)))


def build_slow_query_records(rows: list[Mapping[str, object]], target: str, start_ms: int, end_ms: int) -> tuple[HistoricalPointRecord, ...]:
    records = []
    for row_number, row in enumerate(rows, start=1):
        timestamp = _row_value(row, ("TIME", "time"), row_number, "TIME")
        timestamp_ms = _timestamp_to_ms(timestamp, f"slow_queries[{row_number}].TIME")
        if not start_ms <= timestamp_ms <= end_ms:
            continue
        payload = {
            "instance": row.get("INSTANCE", row.get("instance")),
            "digest": row.get("DIGEST", row.get("digest")),
            "sql_text": row.get("QUERY", row.get("query")),
            "query_time_ms": row.get("QUERY_TIME", row.get("query_time_ms")),
            "process_time_ms": row.get("PROCESS_TIME", row.get("process_time_ms")),
            "wait_time_ms": row.get("WAIT_TIME", row.get("wait_time_ms")),
            "backoff_time_ms": row.get("BACKOFF_TIME", row.get("backoff_time_ms")),
            "total_keys": row.get("TOTAL_KEYS", row.get("total_keys")),
            "process_keys": row.get("PROCESS_KEYS", row.get("process_keys")),
            "mem_max": row.get("MEM_MAX", row.get("mem_max")),
            "disk_max": row.get("DISK_MAX", row.get("disk_max")),
        }
        records.append(HistoricalPointRecord(
            source=HistoricalRecordSource.SLOW_QUERIES,
            target=target,
            timestamp_ms=timestamp_ms,
            payload=payload,
        ))
    return tuple(sorted(records, key=lambda item: (item.timestamp_ms, item.target)))


def _row_value(row: Mapping[str, object], names: tuple[str, ...], row_number: int, field: str) -> object:
    for name in names:
        if name in row:
            return row[name]
    raise KeyError(f"Historical record row lacks required field: field={field!r}, row_number={row_number}, row={row!r}")


HISTORICAL_TABLE_NAMES = frozenset({
    "information_schema.cluster_slow_query",
    "information_schema.slow_query",
    "information_schema.cluster_statements_summary",
    "information_schema.cluster_statements_summary_history",
    "information_schema.statements_summary",
    "information_schema.statements_summary_history",
})
HISTORICAL_UNQUALIFIED_TABLE_NAMES = frozenset(
    name.rsplit(".", 1)[-1] for name in HISTORICAL_TABLE_NAMES
)


def reject_tidb_public_historical_sql(sql_query: str) -> None:
    """Reject physical TiDB historical telemetry reads from the Agent SQL surface."""

    from sqlglot import exp, parse
    from sqlglot.errors import ParseError, TokenError

    try:
        statements = parse(sql_query, read="mysql")
    except (ParseError, TokenError) as exc:
        raise ValueError(f"Cannot parse SQL for TiDB historical-query validation: query={sql_query!r}, error={exc}") from exc
    if not statements:
        raise ValueError("TiDB historical-query validation received an empty SQL statement")
    for statement in statements:
        if isinstance(statement, exp.Command):
            command_name = str(statement.this or "").strip().upper()
            command_rest = str(statement.expression or "").strip().upper()
            # Resource-control repair and TiKV backup-budget repair are the
            # sanctioned remediations for frozen-history resource-governance
            # Cases; they touch no telemetry table, and the Case safety rules
            # scope which groups and settings may be altered.  SHOW CONFIG is
            # the matching read-only current-config surface.  DROP TRIGGER is
            # the sanctioned sink-capacity remediation for the frozen-history
            # timezone-DDL backpressure Case.  ALTER TABLE ... NOCACHE is the
            # sanctioned cached-table remediation for the frozen-history table
            # cache lease Case.  The Case safety rules scope which objects each
            # remediation may touch.
            sanctioned_remediation = (
                command_name == "ALTER" and command_rest.startswith("RESOURCE GROUP")
            ) or (command_name == "SET" and command_rest.startswith("CONFIG TIKV")) or (
                command_name == "SHOW" and command_rest.startswith("CONFIG")
            ) or (command_name == "DROP" and command_rest.startswith("TRIGGER")) or (
                command_name == "ALTER"
                and command_rest.startswith("TABLE")
                and command_rest.endswith("NOCACHE")
            )
            if not sanctioned_remediation:
                raise ValueError(
                    "TiDB historical-query validation rejects uninspectable SQL commands: "
                    f"statement={statement!r}, query={sql_query!r}"
                )
        if isinstance(statement, exp.Use):
            raise ValueError(
                "TiDB frozen-history SQL history guard rejects USE because it changes SQL name resolution: "
                f"statement={statement!r}, query={sql_query!r}"
            )
        for table in statement.find_all(exp.Table):
            table_name = str(table.name).casefold()
            database = str(table.db or "").casefold()
            qualified = f"{database}.{table_name}" if database else table_name
            if qualified in HISTORICAL_TABLE_NAMES or table_name in HISTORICAL_UNQUALIFIED_TABLE_NAMES:
                raise ValueError(
                    "Historical-query access forbids physical historical telemetry table access: "
                    f"table={qualified!r}; use execute_sql(target='history') for frozen historical SQL records, query={sql_query!r}"
                )
        for node in statement.walk():
            if node.__class__.__name__.casefold() in {"tableversion", "version"}:
                raise ValueError(
                    f"Historical-query access forbids temporal SQL history reads: query={sql_query!r}, node={node!r}"
                )


__all__ = [
    "build_slow_query_records",
    "build_topsql_records",
    "parse_docker_log_records",
    "reject_tidb_public_historical_sql",
]
