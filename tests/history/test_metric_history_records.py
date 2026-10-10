import pytest

from src.execution.history.records import CapturedRecords, FrozenHistoricalRecordStore, HistoricalCoverage, HistoricalIntervalRecord, HistoricalPointRecord, HistoricalRecordSource
from src.scenarios.runtime.metric_history import _records_in_range


BASE_MS = 1_700_000_000_000


def test_frozen_history_shifts_event_details_and_hides_marker_identity():
    records = CapturedRecords(
        point_records=(
            HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                timestamp_ms=BASE_MS,
                payload={
                    "event_type": "marker_commit",
                    "correlation_id": "marker-secret",
                    "details": {
                        "marker_id": "marker-secret",
                        "checksum": "checksum-secret",
                        "committed_at": "2023-11-14T22:13:20+00:00",
                    },
                },
            ),
            HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                timestamp_ms=BASE_MS + 1_000,
                payload={
                    "event_type": "archive_attempt",
                    "details": {"start_ms": BASE_MS + 1_000, "end_ms": BASE_MS + 2_000},
                },
            ),
        ),
    )

    shifted = _records_in_range(records, BASE_MS, BASE_MS + 1_000, 4_000)

    marker, archive = shifted
    assert marker.timestamp_ms == BASE_MS + 4_000
    assert "correlation_id" not in marker.payload
    assert marker.payload["details"] == {}
    assert archive.payload["details"] == {
        "start_ms": BASE_MS + 5_000,
        "end_ms": BASE_MS + 6_000,
    }


def test_record_store_filters_orders_and_reports_truncation():
    records = CapturedRecords(
        point_records=(
            HistoricalPointRecord(
                source=HistoricalRecordSource.COMPONENT_LOG,
                target="postgres",
                timestamp_ms=BASE_MS + 1_000,
                payload={"level": "WARN", "component": "postgres", "message": "target slow"},
            ),
            HistoricalPointRecord(
                source=HistoricalRecordSource.COMPONENT_LOG,
                target="postgres",
                timestamp_ms=BASE_MS + 2_000,
                payload={"level": "INFO", "component": "postgres", "message": "normal"},
            ),
        ),
        interval_records=(
            HistoricalIntervalRecord(
                source=HistoricalRecordSource.TOPSQL,
                target="postgres",
                start_ms=BASE_MS,
                end_ms=BASE_MS + 2_000,
                payload={"digest": "slow", "sql_text": "select target", "sum_latency": 20, "exec_count": 2},
            ),
            HistoricalIntervalRecord(
                source=HistoricalRecordSource.TOPSQL,
                target="postgres",
                start_ms=BASE_MS + 2_000,
                end_ms=BASE_MS + 4_000,
                payload={"digest": "fast", "sql_text": "select other", "sum_latency": 5, "exec_count": 1},
            ),
        ),
        coverage=(
            HistoricalCoverage(source=HistoricalRecordSource.COMPONENT_LOG, target="postgres", start_ms=BASE_MS, end_ms=BASE_MS + 10_000),
            HistoricalCoverage(source=HistoricalRecordSource.TOPSQL, target="postgres", start_ms=BASE_MS, end_ms=BASE_MS + 10_000),
        ),
    )
    store = FrozenHistoricalRecordStore.from_captured(records)
    logs = store.query(
        source=HistoricalRecordSource.COMPONENT_LOG,
        start_ms=BASE_MS,
        end_ms=BASE_MS + 10_000,
        target="postgres",
        filters={"level": "warn"},
        limit=1,
    )
    assert logs["matched_records"] == 1
    topsql = store.query(
        source=HistoricalRecordSource.TOPSQL,
        start_ms=BASE_MS,
        end_ms=BASE_MS + 4_000,
        target="postgres",
        filters={"order_by": "sum_latency"},
        limit=1,
    )
    assert topsql["truncated"] is True
    assert topsql["records"][0]["digest"] == "slow"


def test_operation_event_filters_search_event_payload():
    store = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        point_records=(HistoricalPointRecord(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            timestamp_ms=BASE_MS + 1_000,
            payload={
                "event_type": "quota_revision",
                "entity": "entity_2",
                "actor": "fault_injector",
                "new_quota_cores": 0.45,
                "message": "bounded CPU policy revision applied",
            },
        ),),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 10_000,
        ),),
    ))

    result = store.query(
        source=HistoricalRecordSource.OPERATION_EVENT,
        start_ms=BASE_MS,
        end_ms=BASE_MS + 10_000,
        target="postgres",
        filters={"event_type": "QUOTA_REVISION", "entity": "ENTITY_2", "contains": "0.45"},
        limit=10,
        max_window_seconds=20,
    )

    assert result["matched_records"] == 1
    assert result["records"][0]["actor"] == "fault_injector"


def test_sql_contains_matches_only_sql_text():
    store = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        interval_records=(HistoricalIntervalRecord(
            source=HistoricalRecordSource.TOPSQL,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 2_000,
            payload={"digest": "needle-in-digest", "sql_text": "select actual_sql"},
        ),),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.TOPSQL,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 10_000,
        ),),
    ))
    result = store.query(
        source=HistoricalRecordSource.TOPSQL,
        start_ms=BASE_MS,
        end_ms=BASE_MS + 2_000,
        target="postgres",
        filters={"sql_contains": "needle-in-digest"},
        limit=10,
    )
    assert result["matched_records"] == 0


def test_operation_event_contains_matches_event_details_case_insensitively():
    store = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        point_records=(
            HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                timestamp_ms=BASE_MS,
                payload={
                    "event_type": "vacuum",
                    "entity_type": "table",
                    "entity": "hc_mf01_orders",
                    "action": "finish",
                    "status": "success",
                    "message": "planned vacuum completed for orders",
                },
            ),
            HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                timestamp_ms=BASE_MS + 1_000,
                payload={
                    "event_type": "churn_job",
                    "entity_type": "table",
                    "entity": "hc_mf01_decoy",
                    "action": "update",
                    "status": "success",
                    "message": "normal write burst completed",
                },
            ),
        ),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 10_000,
        ),),
    ))
    result = store.query(
        source=HistoricalRecordSource.OPERATION_EVENT,
        start_ms=BASE_MS,
        end_ms=BASE_MS + 2_000,
        target="postgres",
        filters={"contains": "ORDERS"},
        limit=10,
        max_window_seconds=20,
    )
    assert result["matched_records"] == 1
    assert result["records"][0]["entity"] == "hc_mf01_orders"


def test_operation_event_filters_are_bounded_and_search_details():
    store = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        point_records=(
            HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                timestamp_ms=BASE_MS + 1_000,
                payload={
                    "event_type": "archive_attempt",
                    "entity_type": "repository",
                    "entity": "archive_repository",
                    "action": "archive",
                    "status": "success",
                    "correlation_id": "archive-1",
                    "details": {"durability_result": "persisted", "bytes": 128},
                },
            ),
            HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                timestamp_ms=BASE_MS + 2_000,
                payload={
                    "event_type": "backup_run",
                    "entity_type": "repository",
                    "entity": "base_backup_repository",
                    "action": "verify",
                    "status": "success",
                    "correlation_id": "backup-1",
                    "details": {"validation": "pg_verifybackup"},
                },
            ),
        ),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 10_000,
        ),),
    ))
    result = store.query(
        source=HistoricalRecordSource.OPERATION_EVENT,
        start_ms=BASE_MS,
        end_ms=BASE_MS + 10_000,
        target="postgres",
        filters={"event_type": "archive_attempt", "contains": "persisted"},
        limit=1,
        max_window_seconds=20,
    )
    assert result["scanned"] == 2
    assert result["matched"] == 1
    assert result["records"][0]["correlation_id"] == "archive-1"


def test_empty_records_are_valid_when_source_coverage_is_complete():
    store = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.SLOW_QUERIES,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 10_000,
        ),),
    ))
    result = store.query(
        source=HistoricalRecordSource.SLOW_QUERIES,
        start_ms=BASE_MS,
        end_ms=BASE_MS + 10_000,
        target="postgres",
        filters=None,
        limit=10,
    )
    assert result["coverage"] == "complete"
    assert result["records"] == []


def test_operation_event_filters_are_bounded_and_case_insensitive():
    store = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        point_records=(
            HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                timestamp_ms=BASE_MS + 1_000,
                payload={
                    "event_type": "archive_attempt",
                    "entity_type": "archive_target",
                    "entity": "archive_a",
                    "action": "retry",
                    "status": "failed",
                    "correlation_id": "a-1",
                },
            ),
            HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                timestamp_ms=BASE_MS + 2_000,
                payload={
                    "event_type": "job_batch",
                    "entity_type": "write_job",
                    "entity": "job_a",
                    "action": "write",
                    "status": "completed",
                    "correlation_id": "j-1",
                },
            ),
        ),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 10_000,
        ),),
    ))
    result = store.query(
        source=HistoricalRecordSource.OPERATION_EVENT,
        start_ms=BASE_MS,
        end_ms=BASE_MS + 10_000,
        target="postgres",
        filters={"event_type": "ARCHIVE_ATTEMPT", "status": "FAILED"},
        limit=10,
        max_window_seconds=20,
    )
    assert result["matched_records"] == 1
    assert result["records"][0]["entity"] == "archive_a"


def test_record_store_requires_target_coverage_and_shift_preserves_payload():
    captured = CapturedRecords(
        point_records=(HistoricalPointRecord(
            source=HistoricalRecordSource.COMPONENT_LOG,
            target="postgres",
            timestamp_ms=BASE_MS,
            payload={"message": "x"},
        ),),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.COMPONENT_LOG,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 10_000,
        ),),
    )
    shifted = captured.shift(2_000)
    assert shifted.point_records[0].timestamp_ms == BASE_MS + 2_000
    assert shifted.point_records[0].payload == captured.point_records[0].payload
    store = FrozenHistoricalRecordStore.from_captured(captured)
    try:
        store.query(
            source=HistoricalRecordSource.COMPONENT_LOG,
            start_ms=BASE_MS,
            end_ms=BASE_MS + 2_000,
            target="tikv",
            filters=None,
            limit=10,
        )
    except ValueError as exc:
        assert "no complete coverage" in str(exc)
    else:
        raise AssertionError("missing target coverage must fail")


def test_operation_event_filters_match_structured_public_history_fields_and_ordering():
    store = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        point_records=(
            HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                timestamp_ms=BASE_MS + 1_000,
                payload={
                    "event_type": "vacuum",
                    "operation": "vacuum",
                    "entity_type": "relation",
                    "entity": "orders",
                    "action": "vacuum",
                    "status": "completed",
                    "correlation_id": "run:vacuum:orders",
                    "tuples_removed": 120,
                    "waiter_ms_per_sec": 2.0,
                },
            ),
            HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                timestamp_ms=BASE_MS + 2_000,
                payload={
                    "event_type": "churn_job",
                    "operation": "update",
                    "entity_type": "relation",
                    "entity": "orders",
                    "action": "update",
                    "status": "committed",
                    "correlation_id": "run:churn:1",
                    "committed_rows": 20,
                    "waiter_ms_per_sec": 9.0,
                },
            ),
        ),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 10_000,
        ),),
    ))
    result = store.query(
        source=HistoricalRecordSource.OPERATION_EVENT,
        start_ms=BASE_MS,
        end_ms=BASE_MS + 10_000,
        target="postgres",
        filters={
            "event_type": "vacuum",
            "operation": "vacuum",
            "entity": "orders",
            "status": "completed",
            "contains": "tuples_removed",
        },
        limit=10,
        max_window_seconds=20,
    )
    assert result["matched_records"] == 1
    assert result["records"][0]["correlation_id"] == "run:vacuum:orders"
    ordered = store.query(
        source=HistoricalRecordSource.OPERATION_EVENT,
        start_ms=BASE_MS,
        end_ms=BASE_MS + 10_000,
        target="postgres",
        filters={"event_type": "churn_job", "operation": "update", "order_by": "waiter_ms_per_sec"},
        limit=10,
        max_window_seconds=20,
    )
    assert ordered["coverage"] == "complete"
    assert ordered["matched_records"] == 1
    assert ordered["records"][0]["correlation_id"] == "run:churn:1"
    with pytest.raises(ValueError, match="Unknown historical order_by"):
        store.query(
            source=HistoricalRecordSource.OPERATION_EVENT,
            start_ms=BASE_MS,
            end_ms=BASE_MS + 10_000,
            target="postgres",
            filters={"order_by": "timestamp"},
            limit=10,
            max_window_seconds=20,
        )
def test_operation_event_filters_are_bounded_and_case_insensitive():
    store = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        point_records=(HistoricalPointRecord(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            timestamp_ms=BASE_MS + 1_000,
            payload={
                "event_type": "archive_attempt",
                "entity_type": "repository",
                "entity": "archive_repository",
                "action": "retry",
                "status": "failed",
                "correlation_id": "archive_worker:12",
                "details": "archive command failed",
            },
        ),),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 2_000,
        ),),
    ))

    result = store.query(
        source=HistoricalRecordSource.OPERATION_EVENT,
        start_ms=BASE_MS,
        end_ms=BASE_MS + 2_000,
        target="postgres",
        filters={"event_type": "ARCHIVE_ATTEMPT", "status": "FAILED", "contains": "command"},
        limit=10,
        max_window_seconds=10,
    )

    assert result["matched_records"] == 1
    assert result["records"][0]["entity"] == "archive_repository"
