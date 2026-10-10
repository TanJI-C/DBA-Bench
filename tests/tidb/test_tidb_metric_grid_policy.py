"""Grid tolerance policy shared by PG and TiDB samplers, and the TiDB
metric-capture grid alignment built on it."""

from src.execution.environment import TiDBEnv
from src.execution.history.metrics import MetricFrame
from src.execution.sampler_grid import (
    SAMPLER_LAG_STRIKES_LIMIT,
    SamplerGridStrikes,
)


def test_strike_limit_raises_on_sustained_degradation():
    strikes = SamplerGridStrikes()
    for _ in range(SAMPLER_LAG_STRIKES_LIMIT - 1):
        strikes.strike()
    assert strikes.strikes == SAMPLER_LAG_STRIKES_LIMIT - 1
    try:
        strikes.strike()
    except RuntimeError as exc:
        assert f"strikes={SAMPLER_LAG_STRIKES_LIMIT}" in str(exc)
    else:
        raise AssertionError("strike limit did not raise")


def test_decay_floors_at_zero():
    strikes = SamplerGridStrikes()
    strikes.decay()
    assert strikes.strikes == 0


def _grid_env():
    """The aligner only touches restart detection and padding audit, so a
    minimal stand-in exercises the real alignment logic."""

    class _GridHost:
        # No restarts recorded: every gap is jitter-attributed.
        def _restart_padded_target_started_at_ms(self, series_target, grid_start_ms, grid_end_ms):
            return None

        _metric_capture_tolerance_ms = staticmethod(TiDBEnv._metric_capture_tolerance_ms)
        _contiguous_index_runs = staticmethod(TiDBEnv._contiguous_index_runs)

        def __init__(self):
            self.padding_events = []

        def _record_metric_capture_padding(self, **event):
            self.padding_events.append(event)

    return _GridHost()


def _frame(expected_ms, observed_ms, step_seconds=2):
    values = tuple(float(i) for i in range(len(observed_ms)))
    return MetricFrame(
        metric="cpu",
        query_target=None,
        step_seconds=step_seconds,
        series={"tidb-0": {"percent": values}},
        timestamps_ms={"tidb-0": tuple(observed_ms)},
    ), expected_ms


def _multi_series_frame(expected_ms, gap_indices_per_series, step_seconds=2):
    """Build one frame per container series, each missing its own grid slots."""
    series = {}
    timestamps = {}
    for series_target, gap_indices in gap_indices_per_series.items():
        observed = [ts for ts in expected_ms]
        for index in gap_indices:
            del observed[index]
        series[series_target] = {"percent": tuple(float(i) for i in range(len(observed)))}
        timestamps[series_target] = tuple(observed)
    return MetricFrame(
        metric="cpu",
        query_target=None,
        step_seconds=step_seconds,
        series=series,
        timestamps_ms=timestamps,
    ), expected_ms


def test_aligner_tolerates_isolated_missing_slot():
    expected = list(range(1000, 1000 + 20 * 2000, 2000))
    observed = [ts for ts in expected]
    del observed[5]
    host = _grid_env()
    frame, expected_ms = _frame(expected, observed)
    aligned = TiDBEnv._align_metric_capture_to_grid(
        host, frame, tuple(expected_ms), run_id="r", metric="cpu", query_target=None
    )
    assert aligned.timestamps_ms["tidb-0"] == tuple(expected_ms)
    assert aligned.series["tidb-0"]["percent"][5] == 0.0
    assert len(host.padding_events) == 1
    assert host.padding_events[0]["reason"] == "jitter"


def test_aligner_tolerates_separated_gap_events_and_decays():
    expected = list(range(1000, 1000 + 40 * 2000, 2000))
    observed = [ts for ts in expected]
    # Three separated single-slot gaps with >=3 anchored slots between them.
    for index in (2, 12, 30):
        del observed[index]
    host = _grid_env()
    frame, expected_ms = _frame(expected, observed)
    aligned = TiDBEnv._align_metric_capture_to_grid(
        host, frame, tuple(expected_ms), run_id="r", metric="cpu", query_target=None
    )
    assert len(aligned.timestamps_ms["tidb-0"]) == len(expected_ms)
    assert len(host.padding_events) == 3


def test_aligner_fails_only_on_sustained_gap_runs():
    expected = list(range(1000, 1000 + 60 * 2000, 2000))
    observed = [ts for ts in expected]
    # Ten separated gap events close enough to prevent decay: the tenth strike
    # exceeds the shared limit.
    for index in (1, 3, 6, 9, 12, 15, 18, 21, 24, 27):
        del observed[index]
    host = _grid_env()
    frame, expected_ms = _frame(expected, observed)
    try:
        TiDBEnv._align_metric_capture_to_grid(
            host, frame, tuple(expected_ms), run_id="r", metric="cpu", query_target=None
        )
    except RuntimeError as exc:
        assert f"strikes={SAMPLER_LAG_STRIKES_LIMIT}" in str(exc)
    else:
        raise AssertionError("sustained gap runs did not fail the capture")


def test_aligner_skips_beyond_tolerance_sample_without_failing():
    expected = list(range(1000, 1000 + 10 * 2000, 2000))
    observed = [ts for ts in expected]
    # The last sample lands far beyond the 4-step tolerance: skipped, padded.
    observed[9] = expected[9] + 60_000
    host = _grid_env()
    frame, expected_ms = _frame(expected, observed)
    aligned = TiDBEnv._align_metric_capture_to_grid(
        host, frame, tuple(expected_ms), run_id="r", metric="cpu", query_target=None
    )
    assert aligned.series["tidb-0"]["percent"][9] == 0.0


def test_aligner_correlated_gaps_across_series_do_not_share_one_strike_budget():
    # One Prometheus-side scrape outage leaves the same tight gap cluster in
    # every container series at once. Each series carries its own strike
    # budget, so correlated outages count once per series instead of
    # multiplying into a shared counter (a shared budget would raise at the
    # second series with these gaps).
    expected = list(range(1000, 1000 + 30 * 2000, 2000))
    gaps = [1, 3, 5, 7, 9, 11]
    host = _grid_env()
    frame, expected_ms = _multi_series_frame(
        expected, {f"tidb/tidb-{index}": list(gaps) for index in range(8)}
    )
    aligned = TiDBEnv._align_metric_capture_to_grid(
        host, frame, tuple(expected_ms), run_id="r", metric="cpu", query_target=None
    )
    for index in range(8):
        assert aligned.timestamps_ms[f"tidb/tidb-{index}"] == tuple(expected_ms)
    assert len(host.padding_events) == 8 * len(gaps)
