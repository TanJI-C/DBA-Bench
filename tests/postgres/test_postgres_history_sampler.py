import json
import threading
from types import SimpleNamespace

import pytest

from src.execution.history.metrics import MetricQuery, render_metric_frame
from src.execution.postgres_metrics import LivePostgresSamplerMetricProvider, POSTGRES_METRIC_CATALOG
from src.execution.environments.postgres import PGEnv, _bounded_cpu_percent


BASE_MS = 1_700_000_000_000


def _values(index):
    return {
        "cpu": {"percent": 10.0 + index},
        "memory": {"percent": 20.0 + index},
        "disk_io": {"read_mb_per_second": 1.0 + index, "write_mb_per_second": 2.0 + index},
        "qps": {"queries_per_second": 3.0 + index},
        "active_connections": {"connections": 4.0 + index},
        "cache_hit_ratio": {"percent": 90.0 - index},
    }


def _provider():
    provider = LivePostgresSamplerMetricProvider(sample_interval_sec=2, max_points=8)
    for index in range(4):
        provider.append_sample(BASE_MS + index * 2_000, _values(index))
    return provider


def test_cgroup_cpu_percent_is_bounded_to_catalog_range():
    assert _bounded_cpu_percent(101_180, 1_000_000, 1.0) == 10.12
    assert _bounded_cpu_percent(1_001_800, 1_000_000, 1.0) == 100.0


def test_sampler_uses_aligned_epoch_ms_and_postgres_target_scope():
    provider = _provider()
    frame = provider.query(MetricQuery(metric="cpu", start_epoch_ms=BASE_MS, end_epoch_ms=BASE_MS + 6_000))
    assert frame.query_target is None
    assert frame.timestamps_ms["postgres"] == tuple(BASE_MS + index * 2_000 for index in range(4))
    rendered = json.loads(render_metric_frame(
        frame,
        available_start_ms=BASE_MS,
        available_end_ms=BASE_MS + 6_000,
        requested_start_ms=BASE_MS,
        requested_end_ms=BASE_MS + 6_000,
        step_seconds=2,
    ))
    assert rendered["series"]["postgres"]["timestamps"][0] == "2023-11-14 22:13:20"


def test_capture_copies_one_complete_boundary_for_all_requested_metrics():
    provider = _provider()
    frames = provider.capture(
        ("cpu", "memory", "disk_io", "qps", "active_connections", "cache_hit_ratio"),
        BASE_MS,
        BASE_MS + 6_000,
        2,
    )
    assert [frame.metric for frame in frames] == [
        "cpu", "memory", "disk_io", "qps", "active_connections", "cache_hit_ratio",
    ]
    assert {frame.timestamps_ms["postgres"] for frame in frames} == {
        tuple(BASE_MS + index * 2_000 for index in range(4))
    }
    assert frames[2].series["postgres"].keys() == {"read_mb_per_second", "write_mb_per_second"}


def test_capture_fails_on_missing_sample_without_interpolation_or_fill():
    provider = LivePostgresSamplerMetricProvider(sample_interval_sec=2)
    for index in range(3):
        values = _values(index)
        if index == 1:
            values.pop("qps")
        provider.append_sample(BASE_MS + index * 2_000, values)
    with pytest.raises(RuntimeError, match="missing or extra samples"):
        provider.capture(("qps",), BASE_MS, BASE_MS + 4_000, 2)


def test_contiguous_start_skips_sampler_startup_gap_without_filling_it():
    provider = LivePostgresSamplerMetricProvider(sample_interval_sec=2)
    for index in (0, 1, 4, 5, 6, 7):
        provider.append_sample(BASE_MS + index * 2_000, _values(index))
    assert provider.contiguous_start_ms(("cpu", "memory"), minimum_samples=4) == BASE_MS + 8_000
    assert provider.contiguous_start_ms(("cpu", "memory"), minimum_samples=5) is None


def test_sampler_rejects_non_aligned_timestamp_and_wrong_target():
    provider = LivePostgresSamplerMetricProvider(sample_interval_sec=2)
    with pytest.raises(ValueError, match="fixed grid"):
        provider.append_sample(BASE_MS + 1, _values(0))
    provider.append_sample(BASE_MS, _values(0))
    with pytest.raises(ValueError, match="target must be None"):
        provider.query(MetricQuery(metric="cpu", target="postgres"))


def test_disk_io_fields_are_added_atomically_and_timestamp_mismatch_is_rejected_by_frame_contract():
    provider = LivePostgresSamplerMetricProvider(sample_interval_sec=2)
    provider.append_sample(BASE_MS, {"disk_io": {"read_mb_per_second": 1.0, "write_mb_per_second": 2.0}})
    frame = provider.query(MetricQuery(metric="disk_io"))
    assert frame.timestamps_ms["postgres"] == (BASE_MS,)
    with pytest.raises(ValueError, match="timestamps"):
        from src.execution.history.metrics import MetricFrame
        MetricFrame(
            metric="disk_io",
            query_target=None,
            step_seconds=2,
            series={
                "postgres": {
                    "read_mb_per_second": (1.0, 2.0),
                    "write_mb_per_second": (1.0,),
                },
            },
            timestamps_ms={"postgres": (BASE_MS, BASE_MS + 2_000)},
        )


def test_reset_removes_all_live_samples_and_capture_rejects_empty_provider():
    provider = _provider()
    provider.reset()
    with pytest.raises(RuntimeError, match="has no data"):
        provider.query(MetricQuery(metric="cpu"))


def test_pg_environment_capture_waits_for_sampler_tick_commit(monkeypatch):
    env = PGEnv(deployment=SimpleNamespace(container_name="pg-history-test", resources={}))
    env._sampler_thread = object()
    env._sampler_stop.clear()
    capture_called = threading.Event()

    def fake_capture(*args, **kwargs):
        capture_called.set()
        return ("captured",)

    monkeypatch.setattr(env._metric_service.live, "capture", fake_capture)
    result = []
    capture_thread = threading.Thread(
        target=lambda: result.append(env.capture_metric_history(("cpu",), BASE_MS, BASE_MS + 2_000, 2)),
    )
    capture_thread.start()
    assert not capture_called.wait(0.05)
    with env._sampler_condition:
        env._sampler_last_timestamp_ms = BASE_MS + 2_000
        env._sampler_condition.notify_all()
    capture_thread.join(timeout=1)
    assert not capture_thread.is_alive()
    assert result == [("captured",)]
