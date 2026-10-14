import json
from types import SimpleNamespace

import pytest

from src.execution.environments.postgres import PGEnv
from src.execution.history.metrics import MetricFrame
from src.execution.history.records import (
    CapturedRecords,
    FrozenHistoricalRecordStore,
    HistoricalCoverage,
    HistoricalIntervalRecord,
    HistoricalPointRecord,
    HistoricalRecordSource,
)
from src.execution.history.timeline import FrozenHistoryMetricProvider, FrozenHistoricalTimeline
from src.execution.history.sql_archive import FrozenHistoricalSqlArchive
from src.execution.postgres_history import PgStatementKey, snapshot_from_rows


BASE_MS = 1_700_000_000_000


def _spec(*sources):
    return SimpleNamespace(
        record_sources=tuple(sources),
        max_history_records_per_response=20,
    )


def _timeline(source=HistoricalRecordSource.COMPONENT_LOG):
    frame = MetricFrame(
        metric="cpu",
        query_target=None,
        step_seconds=2,
        series={"postgres": {"percent": (10.0, 20.0)}},
        timestamps_ms={"postgres": (BASE_MS, BASE_MS + 2_000)},
    )
    provider = FrozenHistoryMetricProvider(
        frames=(frame,),
        visible_start_ms=BASE_MS,
        visible_end_ms=BASE_MS + 2_000,
        base_step_seconds=2,
        overview_step_seconds=2,
        max_points_per_series=20,
        max_scalar_samples_per_response=20,
    )
    if source is HistoricalRecordSource.COMPONENT_LOG:
        payload = {"level": "WARNING", "component": "postgres", "message": "target"}
    else:
        payload = {
            "event_type": "quota_revision",
            "entity": "entity_2",
            "actor": "fault_injector",
            "new_quota_cores": 0.45,
            "message": "bounded CPU policy revision applied",
        }
    records = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        point_records=(HistoricalPointRecord(
            source=source,
            target="postgres",
            timestamp_ms=BASE_MS + 1_000,
            payload=payload,
        ),),
        coverage=(HistoricalCoverage(
            source=source,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 2_000,
        ),),
    ))
    return FrozenHistoricalTimeline(
        schema_version=1,
        visible_start_ms=BASE_MS,
        visible_end_ms=BASE_MS + 2_000,
        base_step_seconds=2,
        overview_step_seconds=2,
        metric_provider=provider,
        record_store=records,
        audit={"history_sha256": "lifecycle-test"},
    )


def _env():
    env = PGEnv(deployment=SimpleNamespace(container_name="pg-history-test", resources={}))
    env._case = SimpleNamespace(case_id="pg-history", frozen_history=_spec(HistoricalRecordSource.COMPONENT_LOG))
    env._history_timeline = _timeline()
    env._metric_service.bind_history(env._history_timeline.metric_provider)
    return env


def _operation_event_env():
    env = PGEnv(deployment=SimpleNamespace(container_name="pg-history-event-test", resources={}))
    env._case = SimpleNamespace(case_id="pg-history-event", frozen_history=_spec(HistoricalRecordSource.OPERATION_EVENT))
    env._history_timeline = _timeline(HistoricalRecordSource.OPERATION_EVENT)
    env._metric_service.bind_history(env._history_timeline.metric_provider)
    return env


def test_frozen_history_tool_surface_tracks_knowledge_profile_and_history_contract():
    for profile, expected_knowledge in (
        ("general_knowledge", "query_knowledge_base"),
        ("hierarchical_knowledge", "query_knowledge_base"),
        ("no_knowledge", None),
    ):
        env = PGEnv(deployment=SimpleNamespace(container_name="pg", resources={}), tool_profile=profile)
        env._configure_tools(env._frozen_history_public_tools())
        names = {spec.alias for spec in env.get_tool_specs()}
        assert "query_metrics" in names
        assert "query_history" not in names
        assert "query_history" not in {
            schema["function"]["name"] for schema in env.get_tool_schemas()
        }
        assert json.loads(env._execute_tool("query_history", {}))["status"] == "error"
        assert (expected_knowledge in names) is (expected_knowledge is not None)
        if expected_knowledge is None:
            assert "query_knowledge_base" not in names


def test_frozen_history_tool_surface_appends_db_gpt_diagnostic_tools():
    env = PGEnv(deployment=SimpleNamespace(container_name="pg", resources={}), tool_profile="db_gpt")
    env._configure_tools(env._frozen_history_public_tools())
    names = {spec.alias for spec in env.get_tool_specs()}
    assert {
        "whether_is_abnormal_metric",
        "match_diagnose_knowledge",
        "optimize_index_selection",
        "query_metrics",
        "execute_sql",
        "manage_instance",
        "read_log",
    } <= names
    assert "query_knowledge_base" not in names


def test_no_knowledge_frozen_history_tool_surface_has_no_diagnostic_tools():
    env = PGEnv(deployment=SimpleNamespace(container_name="pg", resources={}), tool_profile="no_knowledge")
    env._configure_tools(env._frozen_history_public_tools())
    names = {spec.alias for spec in env.get_tool_specs()}
    assert "whether_is_abnormal_metric" not in names
    assert "match_diagnose_knowledge" not in names
    assert "optimize_index_selection" not in names


def test_all_postgres_frozen_history_environments_exclude_query_history_from_agent_schema():
    from src.execution.backup_rpo import RpoPGEnv, RpoTopology
    from src.execution.postgres_replica_fleet import PgReplicaFleetDeployment, PgReplicaFleetEnv
    from src.scenarios.postgres.resource_governance.container_cpu_budget import CpuBudgetPGEnv

    environments = (
        PGEnv(deployment=SimpleNamespace(container_name="pg", resources={})),
        RpoPGEnv(topology=RpoTopology.for_run(run_id="history-schema-rpo", case_id="throughput_gap")),
        PgReplicaFleetEnv(deployment=PgReplicaFleetDeployment(identity="history-schema-fleet")),
        CpuBudgetPGEnv(deployment=SimpleNamespace(container_name="history-schema-cpu", resources={})),
    )
    for env in environments:
        env._configure_tools(env._frozen_history_public_tools())
        specs = env.get_tool_specs()
        aliases = {spec.alias for spec in specs}
        tool_ids = {spec.tool_id for spec in specs}
        schema_names = {schema["function"]["name"] for schema in env.get_tool_schemas()}
        assert "query_history" not in aliases
        assert "query_history" not in tool_ids
        assert "query_history" not in schema_names
        assert "read_log" in aliases


def test_query_history_returns_frozen_records_with_complete_coverage():
    env = _env()
    result = json.loads(env.query_history(
        source="component_log",
        start_timestamp="2023-11-14 22:13:20",
        end_timestamp="2023-11-14 22:13:22",
        limit=10,
    ))
    assert result["status"] == "success"
    assert result["coverage"] == "complete"
    assert result["records"][0]["message"] == "target"


def test_frozen_history_reuses_execute_sql_and_read_log_surfaces():
    env = _env()
    env._history_sql_archive = FrozenHistoricalSqlArchive(
        env._history_timeline.record_store,
        max_rows=20,
        visible_start_ms=BASE_MS,
        visible_end_ms=BASE_MS + 2_000,
        sql_dialect="postgres",
        require_time_bounds=True,
    )
    sql_result = json.loads(env.execute_sql(
        "SELECT * FROM statement_summary "
        "WHERE event_start_utc < '2023-11-14 22:13:22' "
        "AND event_end_utc >= '2023-11-14 22:13:20'",
        target="history",
    ))
    assert sql_result["status"] == "success"
    log_result = json.loads(env.read_log(
        "pg_log",
        start_timestamp="2023-11-14 22:13:20",
        end_timestamp="2023-11-14 22:13:22",
    ))
    assert log_result["status"] == "success"
    assert "target" in log_result["content"]
    assert json.loads(env.execute_sql("DELETE FROM statement_summary", target="history"))["status"] == "error"
    assert json.loads(env.execute_sql("SELECT * FROM statement_summary", target="history"))["status"] == "error"


def test_postgres_history_archive_maps_sql_records_and_accepts_bounded_explain():
    store = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        interval_records=(HistoricalIntervalRecord(
            source=HistoricalRecordSource.TOPSQL,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 2_000,
            payload={
                "digest": "42",
                "sql_text": "SELECT * FROM orders",
                "exec_count": 3,
                "sum_latency": 12.5,
                "rows": 9,
                "shared_blks_hit": 7,
            },
        ),),
        point_records=(HistoricalPointRecord(
            source=HistoricalRecordSource.SLOW_QUERIES,
            target="postgres",
            timestamp_ms=BASE_MS + 1_000,
            payload={
                "digest": "slow-42",
                "sql_text": "SELECT pg_sleep(1)",
                "query_time_ms": 1000.0,
                "application_name": "checkout",
                "pid": 123,
                "user": "app",
                "database": "testdb",
            },
        ),),
    ))
    archive = FrozenHistoricalSqlArchive(
        store,
        max_rows=20,
        visible_start_ms=BASE_MS,
        visible_end_ms=BASE_MS + 2_000,
        sql_dialect="postgres",
        require_time_bounds=True,
    )
    columns, rows, count, truncated = archive.execute(
        "SELECT digest, rows, shared_blks_hit FROM statement_summary "
        "WHERE event_start_utc < '2023-11-14 22:13:22' "
        "AND event_end_utc >= '2023-11-14 22:13:20'"
    )
    assert columns == ["digest", "rows", "shared_blks_hit"]
    assert rows == [("42", 9.0, 7.0)]
    assert count == 1
    assert truncated is False
    slow_columns, slow_rows, _, _ = archive.execute(
        "SELECT application_name, pid, user_name, database_name FROM slow_query "
        "WHERE event_time_utc BETWEEN '2023-11-14 22:13:20' AND '2023-11-14 22:13:22'"
    )
    assert slow_columns == ["application_name", "pid", "user_name", "database_name"]
    assert slow_rows == [("checkout", 123, "app", "testdb")]
    explain_columns, explain_rows, _, _ = archive.execute(
        "EXPLAIN SELECT * FROM slow_query "
        "WHERE event_time_utc >= '2023-11-14 22:13:20' "
        "AND event_time_utc < '2023-11-14 22:13:22'"
    )
    assert explain_columns
    assert explain_rows
    archive.close()
    archive.close()
    with pytest.raises(RuntimeError, match="closed"):
        archive.execute("SELECT * FROM slow_query WHERE event_time_utc BETWEEN '2023-11-14 22:13:20' AND '2023-11-14 22:13:22'")


@pytest.mark.parametrize("sql", (
    "INSERT INTO statement_summary(event_start_utc, event_end_utc, instance) VALUES ('a', 'b', 'c')",
    "SELECT * FROM sqlite_master",
    "SELECT * FROM statement_summary; SELECT * FROM slow_query",
    "PRAGMA table_info(statement_summary)",
))
def test_postgres_history_archive_rejects_non_readonly_or_non_whitelisted_sql(sql):
    archive = FrozenHistoricalSqlArchive(
        FrozenHistoricalRecordStore.from_captured(CapturedRecords()),
        max_rows=20,
        visible_start_ms=BASE_MS,
        visible_end_ms=BASE_MS + 2_000,
        sql_dialect="postgres",
        require_time_bounds=True,
    )
    with pytest.raises(ValueError):
        archive.execute(sql)


def test_postgres_history_archive_enforces_row_and_response_budgets():
    store = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        interval_records=tuple(
            HistoricalIntervalRecord(
                source=HistoricalRecordSource.TOPSQL,
                target="postgres",
                start_ms=BASE_MS,
                end_ms=BASE_MS + 2_000,
                payload={"digest": str(index), "sql_text": "x" * 80},
            )
            for index in range(3)
        ),
    ))
    bounded = FrozenHistoricalSqlArchive(
        store,
        max_rows=1,
        visible_start_ms=BASE_MS,
        visible_end_ms=BASE_MS + 2_000,
        sql_dialect="postgres",
        require_time_bounds=True,
    )
    _, rows, count, truncated = bounded.execute(
        "SELECT digest FROM statement_summary "
        "WHERE event_start_utc < '2023-11-14 22:13:22' "
        "AND event_end_utc >= '2023-11-14 22:13:20' ORDER BY digest"
    )
    assert rows == [("0",)]
    assert count == 1
    assert truncated is True

    tiny = FrozenHistoricalSqlArchive(
        store,
        max_rows=20,
        visible_start_ms=BASE_MS,
        visible_end_ms=BASE_MS + 2_000,
        sql_dialect="postgres",
        require_time_bounds=True,
        max_response_bytes=20,
    )
    with pytest.raises(ValueError, match="first row exceeds response budget"):
        tiny.execute(
            "SELECT sql_text FROM statement_summary "
            "WHERE event_start_utc < '2023-11-14 22:13:22' "
            "AND event_end_utc >= '2023-11-14 22:13:20'"
        )


def test_history_response_character_budget_is_deterministic_and_explicit():
    records = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        point_records=tuple(
            HistoricalPointRecord(
                source=HistoricalRecordSource.COMPONENT_LOG,
                target="postgres",
                timestamp_ms=BASE_MS + index * 2_000,
                payload={"level": "LOG", "component": "postgres", "message": "x" * 180},
            )
            for index in range(20)
        ),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.COMPONENT_LOG,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 38_000,
        ),),
    ))

    def query():
        return records.query(
            source=HistoricalRecordSource.COMPONENT_LOG,
            start_ms=BASE_MS,
            end_ms=BASE_MS + 38_000,
            target="postgres",
            filters=None,
            limit=20,
            max_window_seconds=60,
            max_response_chars=1_400,
        )

    first = query()
    second = query()
    encoded = json.dumps(first, ensure_ascii=False, separators=(",", ":"))
    assert first == second
    assert len(encoded) <= 1_400
    assert first["truncated"] is True
    assert first["truncation_reason"] == "response_chars"
    assert first["returned_records"] < first["matched_records"]
    assert first["response_chars"] == len(encoded)
    assert first["returned_window"]["start_timestamp"] == "2023-11-14 22:13:20"


def test_read_log_returns_structured_operation_events_with_payload_filters():
    env = _operation_event_env()
    result = json.loads(env.read_log(
        log_type="operation_event",
        start_timestamp="2023-11-14 22:13:20",
        end_timestamp="2023-11-14 22:13:22",
        filters={"event_type": "quota_revision", "entity": "entity_2", "contains": "0.45"},
        lines=10,
    ))

    assert result["status"] == "success"
    assert result["log_type"] == "operation_event"
    assert result["source"] == "operation_event"
    assert result["records"][0]["actor"] == "fault_injector"


def test_metrics_hidden_surfaces_sampler_and_log_failures_without_downgrade(monkeypatch):
    env = PGEnv(deployment=SimpleNamespace(container_name="pg", resources={}))
    monkeypatch.setattr(env, "_capture_pgss_snapshot", lambda: (_ for _ in ()).throw(RuntimeError("snapshot failed")))
    with pytest.raises(RuntimeError, match="snapshot failed"):
        with env.metrics_hidden():
            pass

    class AliveThread:
        def is_alive(self):
            return True

        def join(self, timeout):
            return None

    env._sampler_thread = AliveThread()
    with pytest.raises(RuntimeError, match="did not stop"):
        env._stop_sampler()


def test_metrics_hidden_rejects_counter_decrease():
    env = PGEnv(deployment=SimpleNamespace(container_name="pg", resources={}))
    key = PgStatementKey(userid=1, dbid=2, queryid=3)
    enter = snapshot_from_rows(BASE_MS, [(1, 2, 3, "SELECT 1", 5, 10.0, 1, 1, 1, 0, 0, 0)])
    exit_snapshot = snapshot_from_rows(BASE_MS + 2_000, [(1, 2, 3, "SELECT 1", 4, 9.0, 1, 1, 1, 0, 0, 0)])
    env._pgss_baseline = enter
    with pytest.raises(RuntimeError, match="counter moved backwards"):
        env._absorb_pgss_delta(enter, exit_snapshot)


def test_metrics_hidden_reports_multiple_disappeared_statement_keys():
    env = PGEnv(deployment=SimpleNamespace(container_name="pg", resources={}))
    enter = snapshot_from_rows(
        BASE_MS,
        [
            (2, 2, 3, "SELECT 2", 1, 1.0, 1, 0, 0, 0, 0, 0),
            (1, 2, 3, "SELECT 1", 1, 1.0, 1, 0, 0, 0, 0, 0),
        ],
    )
    exit_snapshot = snapshot_from_rows(BASE_MS + 2_000, [])
    env._pgss_baseline = enter

    with pytest.raises(RuntimeError, match="key disappeared"):
        env._absorb_pgss_delta(enter, exit_snapshot)


def test_pg_teardown_cleans_deployment_after_sampler_failure(monkeypatch):
    calls = []
    deployment = SimpleNamespace(
        container_name="pg-history-teardown-test",
        resources={},
        teardown=lambda: calls.append("deployment"),
    )
    env = PGEnv(deployment=deployment)
    env._history_sql_archive = SimpleNamespace(close=lambda: calls.append("archive"))
    monkeypatch.setattr(env, "_stop_sampler", lambda: (_ for _ in ()).throw(RuntimeError("sampler failed")))
    monkeypatch.setattr(env, "_stop_workload_runner", lambda: calls.append("workload"))
    monkeypatch.setattr(env, "clear_pgbouncer_endpoint", lambda: calls.append("endpoint"))

    with pytest.raises(RuntimeError, match="sampler failed"):
        env.teardown()

    assert calls == ["archive", "workload", "endpoint", "deployment"]
