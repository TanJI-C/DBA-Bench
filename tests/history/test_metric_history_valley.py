"""Candidate-valley assembly contract for the shared frozen-history runtime."""

from __future__ import annotations

import json

import pytest

from src.execution.history.metrics import MetricDefinition, MetricFrame, MetricQuery, render_metric_frame
from src.execution.history.records import (
    CapturedRecords,
    HistoricalCoverage,
    HistoricalPointRecord,
    HistoricalRecordSource,
)
from src.scenarios.runtime.metric_history import CapturedHistoryInputs, HistoryAssembler
from src.scenarios.frozen_history import DecoyDirection, DecoyKind, HistoryDecoySpec, FrozenHistorySpec


BASE_MS = 1_700_000_000_000

_METRIC_FIELDS = {
    "wal": ("rate",),
    "delivery": ("rate",),
    "backlog": ("age",),
}


class MultiMetricStubCatalog:
    system = "stub"

    @property
    def metric_names(self):
        return frozenset(_METRIC_FIELDS)

    def definition(self, metric):
        if metric not in _METRIC_FIELDS:
            raise ValueError(f"unknown stub metric: {metric!r}")
        return MetricDefinition(
            name=metric,
            value_fields=_METRIC_FIELDS[metric],
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        )

    def target_variants(self, metric, deployment):
        self.definition(metric)
        return (None,)

    def validate_target(self, metric, target, deployment):
        if target not in self.target_variants(metric, deployment):
            raise ValueError(f"unknown stub target: metric={metric!r}, target={target!r}")

    def fingerprint(self):
        return "stub-catalog-valley-v1"


def _frames(values_by_metric, *, start_ms):
    frames = []
    for metric, values in values_by_metric.items():
        timestamps = tuple(start_ms + index * 2_000 for index in range(len(values)))
        frames.append(MetricFrame(
            metric=metric,
            query_target=None,
            step_seconds=2,
            series={"postgres": {field: tuple(float(value) for value in values) for field in _METRIC_FIELDS[metric]}},
            timestamps_ms={"postgres": timestamps},
        ))
    return tuple(frames)


def _operation_records(start_ms, count):
    records = []
    for index in range(count):
        event_type = "marker_commit" if index % 2 == 0 else "archive_attempt"
        records.append(HistoricalPointRecord(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            timestamp_ms=start_ms + index * 2_000,
            payload={
                "event_type": event_type,
                "entity_type": "repository",
                "entity": "archive_repository",
                "action": "archive",
                "status": "failed" if event_type == "archive_attempt" else "success",
                "correlation_id": f"corr-{index}",
                "details": {"segment": f"seg-{index}", "sha256": f"hash-{index}"},
            },
        ))
    return CapturedRecords(
        point_records=tuple(records),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            start_ms=start_ms,
            end_ms=start_ms + (count - 1) * 2_000,
        ),),
    )


def _valley_spec(decoys):
    return FrozenHistorySpec(
        schema_version=1,
        duration_seconds=160,
        normal_capture_seconds=24,
        fault_capture_seconds=16,
        base_step_seconds=2,
        overview_step_seconds=20,
        block_min_seconds=4,
        block_max_seconds=8,
        transition_seconds=2,
        target_age_seconds_range=(46, 52),
        required_metrics=("wal", "delivery", "backlog"),
        record_sources=(HistoricalRecordSource.OPERATION_EVENT,),
        decoys=decoys,
        max_points_per_series=200,
        max_scalar_samples_per_response=400,
        max_history_records_per_response=50,
        max_history_query_seconds=900,
        decoys_adjacent_to_target=True,
    )


_SHADOW = HistoryDecoySpec(
    decoy_id="valley-shadow-stall",
    kind=DecoyKind.CANDIDATE_VALLEY,
    metric="delivery",
    field="rate",
    target=None,
    direction=DecoyDirection.SPIKE,
    count=1,
    duration_seconds=16,
    valley_profile="shadow_copy",
    record_event_types=("archive_attempt",),
)
_SCRAMBLED = HistoryDecoySpec(
    decoy_id="valley-scrambled-order",
    kind=DecoyKind.CANDIDATE_VALLEY,
    metric="backlog",
    field="age",
    target=None,
    direction=DecoyDirection.SPIKE,
    count=1,
    duration_seconds=16,
    valley_profile="scrambled_order",
)

_NORMAL_VALUES = {
    "wal": (10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8),
    "delivery": (12, 14, 13, 11, 15, 19, 17, 16, 14, 12, 10, 8),
    "backlog": (8, 10, 9, 13, 11, 18, 16, 14, 12, 10, 9, 7),
}
_TARGET_VALUES = {
    "wal": (900, 900, 900, 300, 300, 300, 300, 300),
    "delivery": (0, 0, 0, 0, 0, 0, 0, 0),
    "backlog": (0, 2, 4, 6, 8, 10, 12, 14),
}


def _assemble(spec):
    inputs = CapturedHistoryInputs(
        normal_metrics=_frames(_NORMAL_VALUES, start_ms=BASE_MS),
        normal_records=CapturedRecords(coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 23_000,
        ),)),
        target_metrics=_frames(_TARGET_VALUES, start_ms=BASE_MS + 100_000),
        target_records=_operation_records(BASE_MS + 100_000, 8),
        spec=spec,
        seed=33,
    )
    return HistoryAssembler(MultiMetricStubCatalog()).assemble(inputs, agent_start_candidate_ms=BASE_MS + 500_000)


def _series(result, window, metric, field):
    rendered = json.loads(render_metric_frame(
        result.timeline.metric_provider.query(MetricQuery(
            metric=metric, start_epoch_ms=window.start_ms, end_epoch_ms=window.end_ms,
        )),
        available_start_ms=result.timeline.visible_start_ms,
        available_end_ms=result.timeline.visible_end_ms,
        requested_start_ms=window.start_ms,
        requested_end_ms=window.end_ms,
        step_seconds=2,
    ))
    return rendered["series"]["postgres"][field]


def test_candidate_valleys_replay_target_depth_and_anchor_one_overview_point():
    result = _assemble(_valley_spec((_SHADOW, _SCRAMBLED)))
    target = next(window for window in result.windows if window.role == "target")
    valleys = [window for window in result.windows if window.role == "decoy"]
    assert [window.decoy_id for window in valleys] == [_SHADOW.decoy_id, _SCRAMBLED.decoy_id]
    target_span = target.end_ms - target.start_ms
    placed = sorted(valleys, key=lambda window: window.start_ms)
    for window in valleys:
        # Same duration as the buried incident window.
        assert window.end_ms - window.start_ms == target_span
        # No overlap with the target or between valleys.
        assert window.end_ms < target.start_ms
        assert window.source_id.startswith("candidate_valley")
        # Exactly one overview grid point falls inside each valley span.
        step_ms = 20_000
        first_grid = ((window.start_ms // step_ms) + 1) * step_ms
        inside = [ts for ts in range(first_grid, window.end_ms + 1, step_ms)]
        assert len(inside) == 1
    assert placed[0].end_ms < placed[1].start_ms
    # The shadow valley is metrically indistinguishable from the incident
    # window: identical values, identical order, on every channel.
    for metric, fields in _METRIC_FIELDS.items():
        for field in fields:
            assert _series(result, next(w for w in valleys if w.decoy_id == _SHADOW.decoy_id), metric, field) == (
                _series(result, target, metric, field)
            )
    assert result.timeline.audit["valley_window_count"] == 2
    assert result.timeline.audit["valley_sample_count"] > 0


def test_scrambled_valley_keeps_depth_but_breaks_ordered_causality():
    result = _assemble(_valley_spec((_SHADOW, _SCRAMBLED)))
    target = next(window for window in result.windows if window.role == "target")
    scrambled = next(window for window in result.windows if window.decoy_id == _SCRAMBLED.decoy_id)
    target_backlog = _series(result, target, "backlog", "age")
    scrambled_backlog = _series(result, scrambled, "backlog", "age")
    # Same values, same depth: statistics cannot separate the valley.
    assert sorted(scrambled_backlog) == sorted(target_backlog)
    # Delivery stays collapsed across the whole scrambled valley.
    assert all(value == 0.0 for value in _series(result, scrambled, "delivery", "rate"))
    # Ordered causality is broken: the backlog falls again inside the valley
    # while delivery remains collapsed, which a sustained stall cannot do.
    assert max(scrambled_backlog) > scrambled_backlog[-1]
    assert target_backlog[-1] == max(target_backlog)


def test_shadow_valley_records_look_relevant_but_are_incomplete():
    result = _assemble(_valley_spec((_SHADOW, _SCRAMBLED)))
    store = result.timeline.record_store
    shadow = next(window for window in result.windows if window.decoy_id == _SHADOW.decoy_id)
    target = next(window for window in result.windows if window.role == "target")
    valley_query = store.query(
        source=HistoricalRecordSource.OPERATION_EVENT,
        start_ms=shadow.start_ms,
        end_ms=shadow.end_ms,
        target="postgres",
        filters={},
        limit=50,
    )
    valley_records = valley_query["records"]
    assert valley_records
    assert all(record["event_type"] == "archive_attempt" for record in valley_records)
    assert all(record["status"] == "failed" for record in valley_records)
    # The replayed attempts look incident-like but carry no segment identity,
    # no checksum, and no correlation id; and no marker continuity exists.
    for record in valley_records:
        assert "correlation_id" not in record
        assert "segment" not in record["details"]
        assert "sha256" not in record["details"]
    target_query = store.query(
        source=HistoricalRecordSource.OPERATION_EVENT,
        start_ms=target.start_ms,
        end_ms=target.end_ms,
        target="postgres",
        filters={},
        limit=50,
    )
    target_types = {record["event_type"] for record in target_query["records"]}
    assert "marker_commit" in target_types
    assert "marker_commit" not in {record["event_type"] for record in valley_records}


def test_missing_precursor_valley_flattens_only_the_baseline_metrics():
    valley = HistoryDecoySpec(
        decoy_id="valley-missing-precursor",
        kind=DecoyKind.CANDIDATE_VALLEY,
        metric="wal",
        field="rate",
        target=None,
        direction=DecoyDirection.SPIKE,
        count=1,
        duration_seconds=16,
        valley_profile="missing_precursor",
        baseline_metrics=("wal",),
    )
    result = _assemble(_valley_spec((valley,)))
    target = next(window for window in result.windows if window.role == "target")
    precursor = next(window for window in result.windows if window.decoy_id == valley.decoy_id)
    # The delivery collapse and backlog climb keep the incident depth.
    assert all(value == 0.0 for value in _series(result, precursor, "delivery", "rate"))
    assert _series(result, precursor, "backlog", "age") == _series(result, target, "backlog", "age")
    # The WAL channels stay on the normal regime: no generating burst precedes
    # the collapse, so the causal chain is incomplete.
    precursor_wal = _series(result, precursor, "wal", "rate")
    assert max(precursor_wal) < 100.0
    assert max(_series(result, target, "wal", "rate")) == 900.0


def test_valley_placement_requires_headroom_for_the_overview_anchor():
    tight = _valley_spec((_SHADOW, _SCRAMBLED))
    from dataclasses import replace

    with pytest.raises(ValueError, match="cannot fit before the earliest target window"):
        replace(tight, target_age_seconds_range=(24, 30)).validate()
