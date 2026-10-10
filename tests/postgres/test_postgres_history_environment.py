import json
from types import SimpleNamespace

from src.execution.history.metrics import MetricFrame
from src.execution.history.records import (
    CapturedRecords,
    FrozenHistoricalRecordStore,
    HistoricalCoverage,
    HistoricalPointRecord,
    HistoricalRecordSource,
)
from src.execution.history.timeline import FrozenHistoryMetricProvider, FrozenHistoricalTimeline
from src.execution.environment import PGEnv


BASE_MS = 1_700_000_000_000


def _timeline():
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
        max_points_per_series=10,
        max_scalar_samples_per_response=10,
    )
    records = FrozenHistoricalRecordStore.from_captured(CapturedRecords())
    return FrozenHistoricalTimeline(
        schema_version=1,
        visible_start_ms=BASE_MS,
        visible_end_ms=BASE_MS + 2_000,
        base_step_seconds=2,
        overview_step_seconds=2,
        metric_provider=provider,
        record_store=records,
        audit={"history_sha256": "history-test"},
    )


def _env():
    return PGEnv(deployment=SimpleNamespace(container_name="pg-history-test", resources={}))


def test_history_snapshot_capacity_keeps_sampler_warmup_before_capture_window():
    spec = SimpleNamespace(
        normal_capture_seconds=600,
        fault_capture_seconds=360,
        transition_seconds=60,
    )

    assert PGEnv._history_snapshot_capacity(spec, 1) == 662
    assert PGEnv._history_snapshot_capacity(spec, 2) == 332


def test_public_query_metrics_uses_frozen_history_and_observe_metric_uses_live_provider():
    env = _env()
    timeline = _timeline()
    env._metric_service.bind_history(timeline.metric_provider)
    env._history_timeline = timeline
    frozen = json.loads(env.query_metrics(
        "cpu",
        start_timestamp="2023-11-14 22:13:20",
        end_timestamp="2023-11-14 22:13:22",
    ))
    assert frozen["series"]["postgres"]["percent"] == [10.0, 20.0]

    for index in range(2):
        values = {
            "cpu": {"percent": 30.0 + index},
            "memory": {"percent": 30.0 + index},
            "disk_io": {"read_mb_per_second": 1.0, "write_mb_per_second": 2.0},
            "qps": {"queries_per_second": 3.0},
            "active_connections": {"connections": 4.0},
            "cache_hit_ratio": {"percent": 90.0},
        }
        env._metric_service.live.append_sample(BASE_MS + index * 2_000, values)
    live = json.loads(env.observe_metric("cpu"))
    assert live["series"]["postgres"]["percent"] == [30.0, 31.0]


def test_frozen_scenario_metrics_apply_overview_step_and_relation_target_filter():
    relation_series = {
        table: {
            "updated_tps": values,
            "deleted_tps": (0, 0, 0, 0, 0, 0),
            "inserted_tps": (0, 0, 0, 0, 0, 0),
            "hot_update_ratio": (1, 1, 1, 1, 1, 1),
        }
        for table, values in (("orders", (1, 2, 3, 4, 5, 6)), ("payments", (6, 5, 4, 3, 2, 1)))
    }
    timestamps = {
        table: tuple(BASE_MS + index * 2_000 for index in range(6))
        for table in relation_series
    }
    frame = MetricFrame(
        metric="relation_churn",
        query_target=None,
        step_seconds=2,
        series=relation_series,
        timestamps_ms=timestamps,
    )
    provider = FrozenHistoryMetricProvider(
        frames=(frame,),
        visible_start_ms=BASE_MS,
        visible_end_ms=BASE_MS + 10_000,
        base_step_seconds=2,
        overview_step_seconds=4,
        max_points_per_series=20,
        max_scalar_samples_per_response=100,
    )
    env = _env()
    env._case = SimpleNamespace(case_id="hc1", frozen_history=object())
    env.bind_metric_history(FrozenHistoricalTimeline(
        schema_version=1,
        visible_start_ms=BASE_MS,
        visible_end_ms=BASE_MS + 10_000,
        base_step_seconds=2,
        overview_step_seconds=4,
        metric_provider=provider,
        record_store=FrozenHistoricalRecordStore.from_captured(CapturedRecords()),
        audit={"history_sha256": "hc1-history"},
    ))

    class Provider:
        metric_names = frozenset({"relation_churn"})

        def query(self, *_args):
            raise AssertionError("frozen catalog metrics must not use the scenario provider path")

    env.attach_scenario_metric_provider(Provider())
    overview = json.loads(env.query_metrics("relation_churn"))
    assert overview["window"]["step_seconds"] == 4
    assert set(overview["series"]) == {"orders", "payments"}
    assert len(overview["series"]["orders"]["timestamps"]) == 3

    targeted = json.loads(env.query_metrics(
        "relation_churn",
        target="orders",
        start_timestamp="2023-11-14 22:13:20",
        end_timestamp="2023-11-14 22:13:30",
        step_seconds=2,
    ))
    assert targeted["window"]["step_seconds"] == 2
    assert set(targeted["series"]) == {"orders"}
    assert targeted["series"]["orders"]["updated_tps"] == [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]


def test_custom_history_capture_does_not_require_generic_sampler():
    env = _env()
    frame = MetricFrame(
        metric="relation_churn",
        query_target=None,
        step_seconds=2,
        series={
            "orders": {
                "updated_tps": (1.0, 2.0),
                "deleted_tps": (0.0, 0.0),
                "inserted_tps": (0.0, 0.0),
                "hot_update_ratio": (1.0, 1.0),
            }
        },
        timestamps_ms={"orders": (BASE_MS, BASE_MS + 2_000)},
    )

    class Provider:
        metric_names = frozenset({"relation_churn"})

        def capture_history(self, metrics, start_ms, end_ms, step_seconds):
            assert metrics == ("relation_churn",)
            assert (start_ms, end_ms, step_seconds) == (BASE_MS, BASE_MS + 2_000, 2)
            return (frame,)

    env.attach_scenario_metric_provider(Provider())
    captured = env.capture_metric_history(
        ("relation_churn",),
        BASE_MS,
        BASE_MS + 2_000,
        2,
    )
    assert captured == (frame,)


def test_capture_history_records_uses_deployment_range_api_and_real_duration_logs():
    calls = []
    raw = (
        "2023-11-14 22:13:20 UTC [12] app=workload user=postgres db=testdb LOG: "
        "duration: 12.5 ms statement SELECT 1\n"
    )
    deployment = SimpleNamespace(
        container_name="pg-history-test",
        resources={},
        read_logs_at_range=lambda start, end: calls.append((start, end)) or raw,
    )
    env = PGEnv(deployment=deployment)
    captured = env.capture_history_records(
        (HistoricalRecordSource.COMPONENT_LOG, HistoricalRecordSource.SLOW_QUERIES),
        BASE_MS,
        BASE_MS + 2_000,
    )
    assert calls == [(BASE_MS, BASE_MS + 2_000)]
    assert captured.coverage == tuple(sorted(captured.coverage, key=lambda item: (item.source.value, item.target or "", item.start_ms, item.end_ms)))
    assert len(captured.point_records) == 2
    assert {record.source for record in captured.point_records} == {HistoricalRecordSource.COMPONENT_LOG, HistoricalRecordSource.SLOW_QUERIES}


def test_capture_history_records_captures_operation_events_once():
    calls = []
    event = HistoricalPointRecord(
        source=HistoricalRecordSource.OPERATION_EVENT,
        target="postgres",
        timestamp_ms=BASE_MS,
        payload={"event_type": "quota_revision"},
    )

    class Provider:
        def capture_history_records(self, sources, start_ms, end_ms):
            calls.append((sources, start_ms, end_ms))
            return CapturedRecords(
                point_records=(event,),
                coverage=(HistoricalCoverage(
                    source=HistoricalRecordSource.OPERATION_EVENT,
                    target="postgres",
                    start_ms=start_ms,
                    end_ms=end_ms,
                ),),
            )

    env = _env()
    env.attach_scenario_metric_provider(Provider())
    captured = env.capture_history_records(
        (HistoricalRecordSource.OPERATION_EVENT,),
        BASE_MS,
        BASE_MS + 2_000,
    )
    assert calls == [((HistoricalRecordSource.OPERATION_EVENT,), BASE_MS, BASE_MS + 2_000)]
    assert captured.point_records == (event,)
    assert len(captured.coverage) == 1


def test_normal_pg_surface_does_not_expose_query_history():
    names = {spec.alias for spec in _env().get_tool_specs()}
    assert "query_history" not in names


def test_frozen_history_bind_preserves_profile_knowledge_tool():
    for profile, expected_method in (
        ("general_knowledge", "query_general_knowledge_base"),
        ("hierarchical_knowledge", "query_hierarchical_knowledge_base"),
    ):
        env = PGEnv(
            deployment=SimpleNamespace(container_name="pg-history-test", resources={}),
            tool_profile=profile,
        )
        env._case = SimpleNamespace(case_id="history-case", frozen_history=object())
        env.bind_metric_history(_timeline())
        knowledge_spec = next(
            spec for spec in env.get_tool_specs() if spec.alias == "query_knowledge_base"
        )
        assert knowledge_spec.method_name == expected_method
