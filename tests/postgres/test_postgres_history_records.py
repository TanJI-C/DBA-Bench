import pytest

from src.execution.history.records import HistoricalRecordSource
from src.execution.postgres_history import (
    PgStatementKey,
    build_operation_event_records_from_logs,
    build_slow_query_records_from_logs,
    build_topsql_delta_records,
    parse_postgres_log_records,
    snapshot_from_rows,
)


BASE_MS = 1_700_000_000_000


def _row(key, query, calls, total_ms, rows=1):
    return (
        key.userid,
        key.dbid,
        key.queryid,
        query,
        calls,
        total_ms,
        rows,
        10,
        2,
        1,
        0,
        0,
    )


def test_pg_stat_statements_delta_handles_new_query_and_zero_calls():
    old_key = PgStatementKey(userid=1, dbid=2, queryid=10)
    new_key = PgStatementKey(userid=1, dbid=2, queryid=11)
    previous = snapshot_from_rows(BASE_MS, [_row(old_key, "SELECT old", 4, 40.0)])
    current = snapshot_from_rows(BASE_MS + 2_000, [
        _row(old_key, "SELECT old", 6, 60.0),
        _row(new_key, "SELECT new", 2, 12.0),
        _row(PgStatementKey(userid=1, dbid=2, queryid=12), "SELECT zero", 0, 0.0),
    ])
    records = build_topsql_delta_records(previous, current)
    assert [record.payload["digest"] for record in records] == ["10", "11"]
    assert records[0].payload["exec_count"] == 2
    assert records[0].payload["sum_latency"] == 20.0
    assert records[1].source is HistoricalRecordSource.TOPSQL
    assert records[1].payload["sql_text"] == "SELECT new"


def test_pg_stat_statements_counter_reset_and_disappearance_fail_loudly():
    key = PgStatementKey(userid=1, dbid=2, queryid=10)
    previous = snapshot_from_rows(BASE_MS, [_row(key, "SELECT old", 5, 40.0)])
    reset = snapshot_from_rows(BASE_MS + 2_000, [_row(key, "SELECT old", 4, 30.0)])
    with pytest.raises(RuntimeError, match="counter moved backwards"):
        build_topsql_delta_records(previous, reset)
    with pytest.raises(RuntimeError, match="key disappeared"):
        build_topsql_delta_records(previous, snapshot_from_rows(BASE_MS + 2_000, []))


def test_postgres_log_parser_supports_docker_prefix_and_multiline_entries():
    raw = (
        "2023-11-14T22:13:20.000000000Z "
        "2023-11-14 22:13:20.000+00:00 [12] app=workload user=postgres db=testdb LOG: "
        "duration: 12.5 ms statement: SELECT 1\n"
        "  FROM orders\n"
        "2023-11-14 22:13:22.000 UTC [13] app=postgres user=postgres db=testdb WARNING: lock wait\n"
    )
    records = parse_postgres_log_records(raw, BASE_MS, BASE_MS + 4_000)
    assert len(records) == 2
    assert records[0].payload["pid"] == 12
    assert records[0].payload["application_name"] == "workload"
    assert "FROM orders" in records[0].payload["message"]
    slow = build_slow_query_records_from_logs(records)
    assert len(slow) == 1
    assert slow[0].payload["query_time_ms"] == 12.5
    assert slow[0].payload["sql_text"] == "SELECT 1\n  FROM orders"


def test_postgres_log_parser_supports_valid_backend_log_without_connection_prefix():
    raw = "2023-11-14 22:13:20.123 UTC [67] LOG: checkpoint complete: wrote 42 buffers"
    records = parse_postgres_log_records(raw, BASE_MS, BASE_MS + 2_000)
    assert len(records) == 1
    assert records[0].timestamp_ms == BASE_MS + 123
    assert records[0].payload["pid"] == 67
    assert records[0].payload["application_name"] == ""
    assert records[0].payload["user"] == ""
    assert records[0].payload["database"] == ""
    assert records[0].payload["message"] == "checkpoint complete: wrote 42 buffers"

def test_postgres_log_parser_supports_legacy_prefix_inside_capture_window():
    raw = (
        "2023-11-14 22:13:20 UTC [12] ERROR: canceling statement due to statement timeout\n"
        "DETAIL: query exceeded the configured limit\n"
        "2023-11-14 22:13:22 UTC [13] app=postgres user=postgres db=testdb WARNING: recovered\n"
    )
    records = parse_postgres_log_records(raw, BASE_MS, BASE_MS + 4_000)
    assert len(records) == 2
    assert records[0].payload["pid"] == 12
    assert records[0].payload["application_name"] == ""
    assert "DETAIL" in records[0].payload["message"]


def test_postgres_log_parser_accepts_gmt_timezone_prefix():
    raw = "2023-11-14 22:13:20.000 GMT [12] app=a user=u db=d LOG: inside\n"
    records = parse_postgres_log_records(raw, BASE_MS, BASE_MS + 4_000)
    assert len(records) == 1
    assert records[0].payload["message"] == "inside"


def test_postgres_log_parser_rejects_malformed_new_entry_and_first_continuation():
    with pytest.raises(ValueError, match="starts with a continuation"):
        parse_postgres_log_records("continuation", BASE_MS, BASE_MS + 1_000)
    raw = "2023-11-14 22:13:20 UTC [12] app=a user=u db=d LOG: ok\n2023-99-14 22:13:21 UTC [12] app=a user=u db=d LOG: bad"
    with pytest.raises(ValueError, match="invalid timestamp"):
        parse_postgres_log_records(raw, BASE_MS, BASE_MS + 4_000)


def test_postgres_log_parser_drops_entries_outside_capture_window():
    raw = (
        "2023-11-14 22:13:19 UTC [12] app=a user=u db=d LOG: before\n"
        "2023-11-14 22:13:20 UTC [12] app=a user=u db=d LOG: inside\n"
        "2023-11-14 22:13:23 UTC [12] app=a user=u db=d LOG: after"
    )
    records = parse_postgres_log_records(raw, BASE_MS, BASE_MS + 2_000)
    assert [record.payload["message"] for record in records] == ["inside"]


def test_operation_event_projection_keeps_operational_fields_without_answer_labels():
    raw = (
        "2023-11-14 22:13:20 UTC [12] app=postgres user=postgres db=testdb LOG: checkpoint starting: immediate flush\n"
        "2023-11-14 22:13:22 UTC [12] app=postgres user=postgres db=testdb LOG: checkpoint complete: wrote 3 buffers\n"
        "2023-11-14 22:13:24 UTC [13] app=archive_worker user=postgres db=testdb ERROR: archive command failed for file 000000010000000000000001\n"
        "2023-11-14 22:13:26 UTC [14] app=warehouse_refresh_simple user=postgres db=testdb LOG: duration: 4.0 ms statement: INSERT INTO events VALUES (1)\n"
    )
    logs = parse_postgres_log_records(raw, BASE_MS, BASE_MS + 8_000)
    events = build_operation_event_records_from_logs(logs)

    assert [record.payload["event_type"] for record in events] == [
        "checkpoint", "checkpoint", "archive_attempt", "job_run",
    ]
    assert events[0].payload["action"] == "start"
    assert events[0].payload["status"] == "running"
    assert events[2].payload["status"] == "failed"
    assert events[3].payload["entity"] == "warehouse_refresh_simple"
    assert "root_cause" not in events[2].payload
    assert "is_fault" not in events[2].payload


def test_postgres_log_parser_ignores_legacy_prefix_outside_capture_window():
    raw = (
        "2023-11-14 22:13:19 UTC [12] LOG: legacy startup line\n"
        "legacy startup continuation\n"
        "2023-11-14 22:13:20 UTC [12] app=a user=u db=d LOG: inside\n"
    )
    records = parse_postgres_log_records(raw, BASE_MS, BASE_MS + 2_000)
    assert [record.payload["message"] for record in records] == ["inside"]
