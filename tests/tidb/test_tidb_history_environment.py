import json
from types import SimpleNamespace

import pytest

from src.execution.environments.tidb import TiDBEnv
from src.execution.history.records import (
    FrozenHistoricalRecordStore,
    HistoricalCoverage,
    HistoricalIntervalRecord,
    HistoricalRecordSource,
)
from src.execution.history.timeline import FrozenHistoricalTimeline, FrozenHistoryMetricProvider
from src.execution.history.metrics import MetricFrame, MetricQuery
from tests.tidb.test_tidb_environment import FakeDeployment


def _timeline():
    start_ms = 1_700_000_000_000
    end_ms = start_ms + 18_000
    frame = MetricFrame(
        metric="qps",
        query_target=None,
        step_seconds=2,
        series={"cluster": {"queries_per_second": tuple(float(value) for value in range(10))}},
        timestamps_ms={"cluster": tuple(start_ms + index * 2_000 for index in range(10))},
    )
    provider = FrozenHistoryMetricProvider(
        frames=(frame,),
        visible_start_ms=start_ms,
        visible_end_ms=end_ms,
        base_step_seconds=2,
        overview_step_seconds=4,
        max_points_per_series=20,
        max_scalar_samples_per_response=20,
    )
    records = FrozenHistoricalRecordStore(
        point_records={},
        interval_records={("topsql", "tidb/tidb-0"): (HistoricalIntervalRecord(
            source=HistoricalRecordSource.TOPSQL,
            target="tidb/tidb-0",
            start_ms=start_ms,
            end_ms=end_ms,
            payload={"instance": "tidb/tidb-0", "digest": "digest-test", "sql_text": "SELECT 1"},
        ),)},
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.COMPONENT_LOG,
            target="tidb/tidb-0",
            start_ms=start_ms,
            end_ms=end_ms,
        ), HistoricalCoverage(
            source=HistoricalRecordSource.TOPSQL,
            target="tidb/tidb-0",
            start_ms=start_ms,
            end_ms=end_ms,
        )),
    )
    return FrozenHistoricalTimeline(
        schema_version=1,
        visible_start_ms=start_ms,
        visible_end_ms=end_ms,
        base_step_seconds=2,
        overview_step_seconds=4,
        metric_provider=provider,
        record_store=records,
        audit={"history_sha256": "test-history-hash", "seed": 7},
    )


def _bind_env(monkeypatch):
    env = TiDBEnv(deployment=FakeDeployment())
    spec = SimpleNamespace(
        required_metrics=("qps",),
        metric_targets={"qps": (None,)},
        metric_rate_windows={},
        record_sources=(HistoricalRecordSource.COMPONENT_LOG,),
        max_history_records_per_response=100,
    )
    env._case = SimpleNamespace(case_id="history-case", frozen_history=spec)
    live_frame = MetricFrame(
        metric="qps",
        query_target=None,
        step_seconds=2,
        series={"cluster": {"queries_per_second": (99.0,)}},
        timestamps_ms={"cluster": (1_700_000_100_000,)},
    )
    monkeypatch.setattr(env._metric_service.live, "query", lambda query: live_frame)
    env.bind_metric_history(_timeline())
    return env


def test_frozen_history_environment_exposes_only_dynamic_tools_and_separates_live_trusted_observation(monkeypatch):
    env = _bind_env(monkeypatch)
    assert {spec.alias for spec in env.get_tool_specs()} == {
        "query_metrics", "execute_sql", "manage_cluster", "read_log",
        "search_knowledge", "help", "submit", "exit",
    }
    sql_help = json.loads(env.help("execute_sql"))
    assert sql_help["definition"]["runtime"]["connection_surfaces"][-1] == {
        "name": "history",
        "kind": "frozen_history",
        "database": "aiops_metric_history",
        "description": "当前 Case 的只读冻结历史；UTC 时间轴与 query_metrics 一致。只能查询 statement_summary 和 slow_query。",
        "query_examples": [
            "SELECT * FROM statement_summary WHERE event_start_utc < '2030-01-01 00:10:00' AND event_end_utc >= '2030-01-01 00:00:00'",
            "SELECT * FROM slow_query WHERE event_time_utc >= '2030-01-01 00:00:00' AND event_time_utc < '2030-01-01 00:10:00'",
        ],
        "write_policy": "read_only",
    }
    assert sql_help["definition"]["runtime"]["timezone"] == "UTC"
    public = json.loads(env.query_metrics("qps"))
    assert public["series"]["cluster"]["queries_per_second"] == [0.0, 2.0, 4.0, 6.0, 8.0]
    trusted = json.loads(env.observe_metric("qps"))
    assert trusted["series"]["cluster"]["queries_per_second"] == [99.0]
    history_sql = json.loads(env.execute_sql(
        "SELECT * FROM slow_query WHERE event_time_utc >= '2023-11-14 22:13:20' AND event_time_utc < '2023-11-14 22:13:28'",
        target="history",
    ))
    assert history_sql["status"] == "success"
    assert history_sql["row_count"] == 0
    full_history_sql = json.loads(env.execute_sql(
        "SELECT digest FROM statement_summary",
        target="history",
    ))
    assert full_history_sql["status"] == "success"
    assert full_history_sql["result"] == [["digest-test"]]

    history_log = json.loads(env.read_log(
        "tidb/tidb-0",
        start_timestamp="2023-11-14 22:13:20",
        end_timestamp="2023-11-14 22:13:28",
    ))
    assert history_log["status"] == "success"
    assert history_log["target"] == "tidb/tidb-0"


def test_frozen_history_environment_blocks_physical_history_sql_but_does_not_change_current_sql_contract(monkeypatch):
    env = _bind_env(monkeypatch)
    blocked = json.loads(env.execute_sql("SELECT * FROM information_schema.cluster_statements_summary_history"))
    assert blocked["status"] == "error"
    assert "physical historical telemetry" in blocked["error"]
    malformed = json.loads(env.execute_sql("SELECT FROM"))
    assert malformed["status"] == "error"
    assert "parse SQL" in malformed["error"] or "SQL failed" in malformed["error"]


_CAPTURE_START_MS = 1_700_000_000_000
_CAPTURE_STEP_SECONDS = 2
_CAPTURE_POINTS = 9
_EXPECTED_GRID = tuple(
    _CAPTURE_START_MS + index * _CAPTURE_STEP_SECONDS * 1000 for index in range(_CAPTURE_POINTS)
)


def _capture_env(monkeypatch, observed_timestamps, values, series_target="cluster"):
    env = TiDBEnv(deployment=FakeDeployment())
    live_frame = MetricFrame(
        metric="qps",
        query_target=None,
        step_seconds=_CAPTURE_STEP_SECONDS,
        series={series_target: {"queries_per_second": values}},
        timestamps_ms={series_target: observed_timestamps},
    )
    monkeypatch.setattr(env._metric_service.live, "query", lambda query: live_frame)
    return env


def _capture_qps(env):
    return env.capture_metric_history(
        ("qps",),
        _CAPTURE_START_MS,
        _CAPTURE_START_MS + (_CAPTURE_POINTS - 1) * _CAPTURE_STEP_SECONDS * 1000,
        _CAPTURE_STEP_SECONDS,
        metric_targets={"qps": (None,)},
    )


def test_capture_reanchors_shifted_samples_within_tolerance_without_raising(monkeypatch):
    shifted = tuple(timestamp + 300 for timestamp in _EXPECTED_GRID)
    values = tuple(float(index) for index in range(_CAPTURE_POINTS))
    env = _capture_env(monkeypatch, shifted, values)

    frames = _capture_qps(env)

    assert len(frames) == 1
    assert frames[0].timestamps_ms["cluster"] == _EXPECTED_GRID
    assert frames[0].series["cluster"]["queries_per_second"] == values
    assert env.metric_capture_padding_events == ()


def test_lightning_capture_frames_stay_anonymous_at_the_variant_level(monkeypatch):
    from src.execution.deployments.tidb import lightning_job_id
    from src.execution.tidb_metrics import TiDBMetricCatalog

    job_id = lightning_job_id("frozen-history-unit")
    env = TiDBEnv(deployment=FakeDeployment())
    live_frame = MetricFrame(
        metric="lightning_progress",
        query_target=job_id,
        step_seconds=_CAPTURE_STEP_SECONDS,
        series={job_id: {
            field: (1.0,) * _CAPTURE_POINTS
            for field in TiDBMetricCatalog().definition("lightning_progress").value_fields
        }},
        timestamps_ms={job_id: _EXPECTED_GRID},
    )
    monkeypatch.setattr(env._metric_service.live, "query", lambda query: live_frame)

    frames = env.capture_metric_history(
        ("lightning_progress",),
        _CAPTURE_START_MS,
        _CAPTURE_START_MS + (_CAPTURE_POINTS - 1) * _CAPTURE_STEP_SECONDS * 1000,
        _CAPTURE_STEP_SECONDS,
    )

    assert len(frames) == 1
    # 帧级 target 必须匿名：冻结历史的报错枚举逐字暴露帧 target，
    # 挂 job id 等于把事故身份递给一次失败查询。
    assert frames[0].query_target is None
    assert set(frames[0].series) == {job_id}


def test_capture_tolerates_edge_sample_within_ten_second_floor_but_rejects_beyond_it(monkeypatch):
    values = tuple(float(index) for index in range(_CAPTURE_POINTS))
    late_tail = _EXPECTED_GRID[:-1] + (_EXPECTED_GRID[-1] + 9_000,)
    env = _capture_env(monkeypatch, late_tail, values)
    frames = _capture_qps(env)
    assert frames[0].timestamps_ms["cluster"] == _EXPECTED_GRID
    assert frames[0].series["cluster"]["queries_per_second"] == values

    too_late = _EXPECTED_GRID[:-1] + (_EXPECTED_GRID[-1] + 11_000,)
    env = _capture_env(monkeypatch, too_late, values)
    with pytest.raises(RuntimeError, match="deviation_ms=11000, tolerance_ms=10000"):
        _capture_qps(env)


def test_capture_raises_for_empty_series_without_padding(monkeypatch):
    env = _capture_env(monkeypatch, (), ())
    with pytest.raises(RuntimeError, match="no observed samples"):
        _capture_qps(env)


def test_capture_raises_for_missing_samples_without_container_restart(monkeypatch):
    values = tuple(float(index) for index in range(_CAPTURE_POINTS - 1))
    gapped = _EXPECTED_GRID[:4] + _EXPECTED_GRID[5:]
    env = _capture_env(monkeypatch, gapped, values)

    with pytest.raises(RuntimeError, match="without a container restart") as excinfo:
        _capture_qps(env)

    assert str(_EXPECTED_GRID[4]) in str(excinfo.value)
    assert env.metric_capture_padding_events == ()


def test_capture_pads_restart_gap_deterministically_and_keeps_metadata(monkeypatch):
    values = tuple(float(index) for index in (0, 1, 2, 5, 6, 7, 8))
    gapped = _EXPECTED_GRID[:3] + _EXPECTED_GRID[5:]
    env = _capture_env(monkeypatch, gapped, values, series_target="tidb/tidb-0")
    restarted_at = _CAPTURE_START_MS + 7_000
    monkeypatch.setattr(env, "_restart_padded_target_started_at_ms", lambda *args: restarted_at)

    frames = _capture_qps(env)

    assert len(frames) == 1
    assert frames[0].timestamps_ms["tidb/tidb-0"] == _EXPECTED_GRID
    assert frames[0].series["tidb/tidb-0"]["queries_per_second"] == (0.0, 1.0, 2.0, 0.0, 0.0, 5.0, 6.0, 7.0, 8.0)
    events = env.metric_capture_padding_events
    assert len(events) == 1
    event = events[0]
    assert event["metric"] == "qps"
    assert event["series_target"] == "tidb/tidb-0"
    assert event["padded_timestamps_ms"] == (_EXPECTED_GRID[3], _EXPECTED_GRID[4])
    assert event["fill_value"] == 0.0
    assert event["container_started_at_ms"] == restarted_at


def test_capture_restart_padding_requires_container_start_inside_capture_window(monkeypatch):
    values = tuple(float(index) for index in range(_CAPTURE_POINTS - 1))
    gapped = _EXPECTED_GRID[:4] + _EXPECTED_GRID[5:]
    env = _capture_env(monkeypatch, gapped, values, series_target="pd/pd-0")
    monkeypatch.setattr(env, "_restart_padded_target_started_at_ms", lambda *args: None)

    with pytest.raises(RuntimeError, match="pd/pd-0"):
        _capture_qps(env)
    assert env.metric_capture_padding_events == ()
