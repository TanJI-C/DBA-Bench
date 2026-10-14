import json
from dataclasses import replace

import pytest

from src.execution.history.metrics import MetricDefinition, MetricFrame, MetricQuery, parse_utc_timestamp, format_utc_timestamp, render_metric_frame
from src.execution.history.records import CapturedRecords, HistoricalCoverage, HistoricalPointRecord, HistoricalRecordSource
from src.execution.history.timeline import FrozenHistoryMetricProvider
from src.scenarios.runtime.metric_history import CapturedHistoryInputs, HistoryAssembler, NormalHistoryCapture
from src.scenarios.frozen_history import DecoyDirection, DecoyKind, HistoryDecoySpec, FrozenHistorySpec


BASE_MS = 1_700_000_000_000


class StubMetricCatalog:
    system = "stub"

    @property
    def metric_names(self):
        return frozenset({"qps"})

    def definition(self, metric):
        if metric != "qps":
            raise ValueError(f"unknown stub metric: {metric!r}")
        return MetricDefinition(
            name="qps",
            value_fields=("queries_per_second",),
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        )

    def target_variants(self, metric, deployment):
        self.definition(metric)
        return (None, "secondary")

    def validate_target(self, metric, target, deployment):
        if target not in self.target_variants(metric, deployment):
            raise ValueError(f"unknown stub target: metric={metric!r}, target={target!r}")

    def fingerprint(self):
        return "stub-catalog-v1"


def _frame(values, *, query_target=None, series_target="postgres", start_ms=BASE_MS):
    timestamps = tuple(start_ms + index * 2_000 for index in range(len(values)))
    return MetricFrame(
        metric="qps",
        query_target=query_target,
        step_seconds=2,
        series={series_target: {"queries_per_second": tuple(float(value) for value in values)}},
        timestamps_ms={series_target: timestamps},
    )


def _spec():
    return FrozenHistorySpec(
        schema_version=1,
        duration_seconds=40,
        normal_capture_seconds=24,
        fault_capture_seconds=16,
        base_step_seconds=2,
        overview_step_seconds=4,
        block_min_seconds=4,
        block_max_seconds=8,
        transition_seconds=2,
        target_age_seconds_range=(16, 20),
        required_metrics=("qps",),
        record_sources=(HistoricalRecordSource.COMPONENT_LOG,),
        decoys=(HistoryDecoySpec(
            decoy_id="normal-spike",
            kind=DecoyKind.METRIC_ONLY,
            metric="qps",
            field="queries_per_second",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=4,
            amplitude_mad=1.0,
        ),),
        max_points_per_series=100,
        max_scalar_samples_per_response=100,
        max_history_records_per_response=20,
    )


def _captured(start_ms, count, target="postgres"):
    return CapturedRecords(
        point_records=tuple(
            HistoricalPointRecord(
                source=HistoricalRecordSource.COMPONENT_LOG,
                target=target,
                timestamp_ms=start_ms + index * 2_000,
                payload={"level": "INFO", "component": "database", "message": f"sample-{index}"},
            )
            for index in range(count)
        ),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.COMPONENT_LOG,
            target=target,
            start_ms=start_ms,
            end_ms=start_ms + (count - 1) * 2_000,
        ),),
    )


def test_metric_frame_contract_is_database_independent_and_utc_is_explicit():
    frame = _frame((1, 2))
    StubMetricCatalog().definition(frame.metric)
    assert format_utc_timestamp(parse_utc_timestamp("2023-11-14 22:13:20")) == "2023-11-14 22:13:20"
    with pytest.raises(ValueError, match="UTC"):
        parse_utc_timestamp("2023/11/14 22:13:20")
    with pytest.raises(ValueError, match="non-finite"):
        MetricFrame(
            metric="qps",
            query_target=None,
            step_seconds=2,
            series={"postgres": {"queries_per_second": (float("nan"),)}},
            timestamps_ms={"postgres": (BASE_MS,)},
        )


def test_frozen_metric_provider_enforces_grid_and_scalar_budget():
    frame = _frame(range(20))
    provider = FrozenHistoryMetricProvider(
        frames=(frame,),
        visible_start_ms=BASE_MS,
        visible_end_ms=BASE_MS + 38_000,
        base_step_seconds=2,
        overview_step_seconds=4,
        max_points_per_series=20,
        max_scalar_samples_per_response=20,
    )
    overview = provider.query(MetricQuery(metric="qps"))
    assert overview.step_seconds == 4
    assert overview.series["postgres"]["queries_per_second"] == tuple(float(index) for index in range(0, 20, 2))
    with pytest.raises(ValueError, match="align to base grid"):
        provider.query(MetricQuery(metric="qps", start_epoch_ms=BASE_MS + 1_000, end_epoch_ms=BASE_MS + 5_000))
    with pytest.raises(ValueError, match="scalar sample budget"):
        FrozenHistoryMetricProvider(
            frames=(frame,),
            visible_start_ms=BASE_MS,
            visible_end_ms=BASE_MS + 38_000,
            base_step_seconds=2,
            overview_step_seconds=4,
            max_points_per_series=20,
            max_scalar_samples_per_response=2,
        ).query(MetricQuery(metric="qps", start_epoch_ms=BASE_MS, end_epoch_ms=BASE_MS + 8_000))


def test_overview_resampling_preserves_short_peak_fields():
    frame = MetricFrame(
        metric="replica_lwlock",
        query_target=None,
        step_seconds=2,
        series={"replica_0": {
            "lock_manager_waiters": (0, 0, 4, 0),
            "waiter_ms_per_sec": (0, 0, 12, 0),
            "slowpath_backends": (0, 0, 8, 0),
        }},
        timestamps_ms={"replica_0": tuple(BASE_MS + index * 2_000 for index in range(4))},
    )
    overview = frame.resample(4, BASE_MS, BASE_MS + 6_000)
    assert overview.series["replica_0"]["lock_manager_waiters"] == (0.0, 4.0)
    assert overview.series["replica_0"]["waiter_ms_per_sec"] == (0.0, 12.0)
    assert overview.series["replica_0"]["slowpath_backends"] == (0.0, 8.0)


def test_long_overview_keeps_values_and_compacts_fixed_grid_timestamps():
    frame = _frame(range(6_000))
    rendered = json.loads(render_metric_frame(
        frame,
        available_start_ms=BASE_MS,
        available_end_ms=BASE_MS + 11_998_000,
        requested_start_ms=BASE_MS,
        requested_end_ms=BASE_MS + 11_998_000,
        step_seconds=20,
    ))
    timestamps = rendered["series"]["postgres"]["timestamps"]
    assert timestamps == {
        "start": "2023-11-14 22:13:20",
        "end": "2023-11-15 01:33:00",
        "step_seconds": 20,
        "count": 600,
    }
    assert rendered["series"]["postgres"]["queries_per_second"] == [float(index) for index in range(0, 6_000, 10)]


def test_frozen_overview_downsamples_to_shared_scalar_budget():
    frame = _frame(range(20))
    provider = FrozenHistoryMetricProvider(
        frames=(frame,),
        visible_start_ms=BASE_MS,
        visible_end_ms=BASE_MS + 38_000,
        base_step_seconds=2,
        overview_step_seconds=4,
        max_points_per_series=20,
        max_scalar_samples_per_response=4,
    )
    overview = provider.query(MetricQuery(metric="qps"))
    assert overview.step_seconds > 4
    assert overview.point_count <= 4


def test_history_assembler_is_deterministic_and_preserves_target_records():
    spec = _spec()
    normal_values = (10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)
    target_values = (100, 102, 104, 106, 108, 110, 112, 114)
    inputs = CapturedHistoryInputs(
        normal_captures=(NormalHistoryCapture(
            capture_id="normal-0",
            metrics=(_frame(normal_values),),
            records=_captured(BASE_MS, len(normal_values)),
        ),),
        target_metrics=(_frame(target_values, start_ms=BASE_MS + 100_000),),
        target_records=_captured(BASE_MS + 100_000, len(target_values)),
        spec=spec,
        seed=33,
    )
    first = HistoryAssembler(StubMetricCatalog()).assemble(inputs, agent_start_candidate_ms=BASE_MS + 500_000)
    second = HistoryAssembler(StubMetricCatalog()).assemble(inputs, agent_start_candidate_ms=BASE_MS + 500_000)
    assert first.timeline.history_sha256 == second.timeline.history_sha256
    assert first.timeline.audit["catalog_sha256"] == "stub-catalog-v1"
    target = next(window for window in first.windows if window.role == "target")
    rendered = json.loads(render_metric_frame(
        first.timeline.metric_provider.query(MetricQuery(
            metric="qps", start_epoch_ms=target.start_ms, end_epoch_ms=target.end_ms,
        )),
        available_start_ms=first.timeline.visible_start_ms,
        available_end_ms=first.timeline.visible_end_ms,
        requested_start_ms=target.start_ms,
        requested_end_ms=target.end_ms,
        step_seconds=2,
    ))
    assert rendered["series"]["postgres"]["queries_per_second"] == list(target_values)
    assert "role" not in rendered
    assert first.timeline.audit["plateau_sample_count"] == 0
    assert first.timeline.audit["return_to_normal_sample_count"] > 0
    tail = json.loads(render_metric_frame(
        first.timeline.metric_provider.query(MetricQuery(
            metric="qps",
            start_epoch_ms=target.end_ms + 2_000,
            end_epoch_ms=first.timeline.visible_end_ms,
        )),
        available_start_ms=first.timeline.visible_start_ms,
        available_end_ms=first.timeline.visible_end_ms,
        requested_start_ms=target.end_ms + 2_000,
        requested_end_ms=first.timeline.visible_end_ms,
        step_seconds=2,
    ))
    assert all(value != target_values[-1] for value in tail["series"]["postgres"]["queries_per_second"])


def test_history_assembler_can_place_captured_competitors_adjacent_to_target():
    spec = replace(_spec(), decoys_adjacent_to_target=True)
    normal_values = (10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)
    target_values = (100, 102, 104, 106, 108, 110, 112, 114)
    result = HistoryAssembler(StubMetricCatalog()).assemble(
        CapturedHistoryInputs(
            normal_captures=(NormalHistoryCapture(
                capture_id="normal-0",
                metrics=(_frame(normal_values),),
                records=_captured(BASE_MS, len(normal_values)),
            ),),
            target_metrics=(_frame(target_values, start_ms=BASE_MS + 100_000),),
            target_records=_captured(BASE_MS + 100_000, len(target_values)),
            spec=spec,
            seed=33,
        ),
        agent_start_candidate_ms=BASE_MS + 500_000,
    )
    target = next(window for window in result.windows if window.role == "target")
    decoys = [window for window in result.windows if window.role == "decoy"]
    # Window ends are inclusive; the next sample starts after one base step.
    assert max(window.end_ms for window in decoys) + (spec.transition_seconds + spec.base_step_seconds) * 1000 == target.start_ms
    assert min(window.start_ms for window in decoys) >= target.start_ms - spec.target_age_seconds_range[1] * 1000


def test_history_assembler_uses_sparse_observed_peak_for_metric_only_decoy():
    normal_values = (0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    target_values = (10, 11, 12, 13, 14, 15, 16, 17)
    result = HistoryAssembler(StubMetricCatalog()).assemble(
        CapturedHistoryInputs(
            normal_metrics=(_frame(normal_values),),
            normal_records=_captured(BASE_MS, len(normal_values)),
            target_metrics=(_frame(target_values, start_ms=BASE_MS + 100_000),),
            target_records=_captured(BASE_MS + 100_000, len(target_values)),
            spec=_spec(),
            seed=33,
        ),
        agent_start_candidate_ms=BASE_MS + 500_000,
    )
    assert result.timeline.audit["metric_only_sample_count"] > 0
    assert any(window.source_id == "metric_only" for window in result.windows)


def test_captured_benign_can_anchor_to_a_real_event_when_metric_mad_is_zero():
    spec = replace(
        _spec(),
        record_sources=(HistoricalRecordSource.OPERATION_EVENT,),
        decoys=(HistoryDecoySpec(
            decoy_id="captured-window",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="qps",
            field="queries_per_second",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=4,
            minimum_deviation_mad=2.0,
            record_event_type="benign_window",
        ),),
    )
    normal_records = CapturedRecords(
        point_records=(HistoricalPointRecord(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            timestamp_ms=BASE_MS + 4_000,
            payload={"event_type": "benign_window", "status": "success"},
        ),),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            start_ms=BASE_MS,
            end_ms=BASE_MS + 22_000,
        ),),
    )
    target_records = CapturedRecords(coverage=(HistoricalCoverage(
        source=HistoricalRecordSource.OPERATION_EVENT,
        target="postgres",
        start_ms=BASE_MS + 100_000,
        end_ms=BASE_MS + 114_000,
    ),))
    result = HistoryAssembler(StubMetricCatalog()).assemble(
        CapturedHistoryInputs(
            normal_metrics=(_frame((5,) * 12),),
            normal_records=normal_records,
            target_metrics=(_frame((9,) * 8, start_ms=BASE_MS + 100_000),),
            target_records=target_records,
            spec=spec,
            seed=33,
        ),
        agent_start_candidate_ms=BASE_MS + 500_000,
    )
    decoy = next(window for window in result.windows if window.role == "decoy")
    assert decoy.source_id == "captured_benign"


def test_captured_benign_decoy_audit_keeps_normal_source_indices():
    spec = replace(
        _spec(),
        decoys=(HistoryDecoySpec(
            decoy_id="captured-spike",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="qps",
            field="queries_per_second",
            target="postgres",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=4,
            minimum_deviation_mad=0.5,
        ),),
    )
    result = HistoryAssembler(StubMetricCatalog()).assemble(
        CapturedHistoryInputs(
            normal_metrics=(_frame((10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)),),
            normal_records=_captured(BASE_MS, 12),
            target_metrics=(_frame((100, 102, 104, 106, 108, 110, 112, 114), start_ms=BASE_MS + 100_000),),
            target_records=_captured(BASE_MS + 100_000, 8),
            spec=spec,
            seed=33,
        ),
        agent_start_candidate_ms=BASE_MS + 500_000,
    )
    decoy = next(window for window in result.windows if window.role == "decoy")
    assert decoy.source_id == "captured_benign"
    assert decoy.source_start_index is not None
    assert decoy.source_end_index == decoy.source_start_index + 1
    audited = next(item for item in result.timeline.audit["decoy_windows"] if item["decoy_id"] == "captured-spike")
    assert audited["source_start_index"] == decoy.source_start_index
    assert audited["source_end_index"] == decoy.source_end_index


def test_history_assembler_returns_to_normal_after_target_bundle():
    spec = replace(_spec(), aftermath="RETURN_TO_NORMAL")
    inputs = CapturedHistoryInputs(
        normal_metrics=(_frame((10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)),),
        normal_records=_captured(BASE_MS, 12),
        target_metrics=(_frame((100, 102, 104, 106, 108, 110, 112, 114), start_ms=BASE_MS + 100_000),),
        target_records=_captured(BASE_MS + 100_000, 8),
        spec=spec,
        seed=33,
    )
    result = HistoryAssembler(StubMetricCatalog()).assemble(inputs, agent_start_candidate_ms=BASE_MS + 500_000)
    target = next(window for window in result.windows if window.role == "target")
    after_target = result.timeline.metric_provider.query(MetricQuery(
        metric="qps",
        start_epoch_ms=target.end_ms + 2_000,
        end_epoch_ms=result.timeline.visible_end_ms,
    ))
    assert all(value < 100 for value in after_target.series["postgres"]["queries_per_second"])
    assert result.timeline.audit["aftermath"] == "RETURN_TO_NORMAL"


def test_captured_benign_sources_do_not_reuse_the_same_normal_window():
    spec = replace(_spec(), decoys=())
    decoy = HistoryDecoySpec(
        decoy_id="captured",
        kind=DecoyKind.CAPTURED_BENIGN,
        metric="qps",
        field="queries_per_second",
        target=None,
        direction=DecoyDirection.SPIKE,
        count=1,
        duration_seconds=4,
        minimum_deviation_mad=0.5,
    )
    assembler = HistoryAssembler(StubMetricCatalog())
    normal_frames = assembler._prepare_frames(
        (_frame((10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)),),
        spec,
        "normal",
    )
    first = assembler._select_benign_source(normal_frames, decoy, 2, 12)
    second = assembler._select_benign_source(
        normal_frames,
        decoy,
        2,
        12,
        excluded_ranges=((first, first + 2),),
    )
    assert second != first


def test_captured_benign_count_times_duration_must_fit_the_normal_capture():
    spec = replace(
        _spec(),
        duration_seconds=160,
        normal_capture_seconds=36,
        target_age_seconds_range=(60, 80),
        decoys=(HistoryDecoySpec(
            decoy_id="captured",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="qps",
            field="queries_per_second",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=2,
            duration_seconds=24,
            minimum_deviation_mad=0.5,
        ),),
    )
    with pytest.raises(ValueError, match="count times duration cannot exceed normal_capture_seconds"):
        spec.validate(None)


def test_captured_benign_repeated_units_replay_disjoint_normal_windows():
    spec = replace(
        _spec(),
        duration_seconds=160,
        normal_capture_seconds=36,
        target_age_seconds_range=(60, 80),
        decoys=(HistoryDecoySpec(
            decoy_id="captured",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="qps",
            field="queries_per_second",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=2,
            duration_seconds=12,
            minimum_deviation_mad=0.5,
        ),),
    )
    result = HistoryAssembler(StubMetricCatalog()).assemble(
        CapturedHistoryInputs(
            normal_metrics=(_frame((10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8, 11, 13, 12, 14, 11, 9)),),
            normal_records=_captured(BASE_MS, 18),
            target_metrics=(_frame((100, 102, 104, 106, 108, 110, 112, 114), start_ms=BASE_MS + 100_000),),
            target_records=_captured(BASE_MS + 100_000, 8),
            spec=spec,
            seed=33,
        ),
        agent_start_candidate_ms=BASE_MS + 500_000,
    )
    spans = sorted(
        (window.source_start_index, window.source_end_index)
        for window in result.windows
        if window.role == "decoy"
    )
    assert len(spans) == 2
    assert spans[0][1] < spans[1][0]


def test_captured_benign_selects_the_highest_directed_deviation_window():
    spec = replace(_spec(), decoys=())
    decoy = HistoryDecoySpec(
        decoy_id="sparse-captured",
        kind=DecoyKind.CAPTURED_BENIGN,
        metric="qps",
        field="queries_per_second",
        target=None,
        direction=DecoyDirection.SPIKE,
        count=1,
        duration_seconds=4,
        minimum_deviation_mad=0.5,
    )
    assembler = HistoryAssembler(StubMetricCatalog())
    normal_frames = assembler._prepare_frames(
        (_frame((0, 0, 0, 0, 10, 10, 0, 0, 0, 0, 0, 0)),),
        spec,
        "normal",
    )

    # MAD normalization picks the window whose mean deviates most in the
    # declared direction (the 10,10 spike pair), not merely the first
    # complete window.
    assert assembler._select_benign_source(normal_frames, decoy, 2, 12) == 4


def test_history_assembler_requires_normal_and_target_source_coverage():
    spec = _spec()
    normal_values = (10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)
    target_values = (100, 102, 104, 106, 108, 110, 112, 114)
    with pytest.raises(ValueError, match="target capture coverage"):
        HistoryAssembler(StubMetricCatalog()).assemble(
            CapturedHistoryInputs(
                normal_captures=(NormalHistoryCapture(
                    capture_id="normal-0",
                    metrics=(_frame(normal_values),),
                    records=_captured(BASE_MS, len(normal_values)),
                ),),
                target_metrics=(_frame(target_values, start_ms=BASE_MS + 100_000),),
                target_records=CapturedRecords(),
                spec=spec,
                seed=33,
            ),
            agent_start_candidate_ms=BASE_MS + 500_000,
        )


def test_history_assembler_deduplicates_replayed_operation_events():
    records = [
        HistoricalPointRecord(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            timestamp_ms=BASE_MS,
            payload={"event_type": "quota_revision", "entity": "entity_3", "new_quota_cores": 1.8},
        ),
        HistoricalPointRecord(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            timestamp_ms=BASE_MS,
            payload={"event_type": "quota_revision", "entity": "entity_3", "new_quota_cores": 1.8},
        ),
        HistoricalPointRecord(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            timestamp_ms=BASE_MS + 2_000,
            payload={"event_type": "quota_revision", "entity": "entity_3", "new_quota_cores": 1.8},
        ),
    ]
    deduplicated = HistoryAssembler._deduplicate_records(records)
    assert len(deduplicated) == 2
    assert deduplicated[0].timestamp_ms == BASE_MS
    assert deduplicated[1].timestamp_ms == BASE_MS + 2_000


def test_history_assembler_keeps_normal_operation_events_before_target():
    records = CapturedRecords(
        point_records=(HistoricalPointRecord(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            timestamp_ms=BASE_MS + 20_000,
            payload={"event_type": "quota_revision", "actor": "scheduler"},
        ),),
    )
    placed = HistoryAssembler._place_normal_operation_events(
        normal_records=records,
        normal_origin_ms=BASE_MS,
        normal_points=12,
        target_start_index=100,
        visible_start_ms=BASE_MS + 1_000_000,
        base_step_ms=2_000,
    )
    assert len(placed) == 1
    assert placed[0].timestamp_ms == BASE_MS + 1_000_000 + (100 - 2) * 2_000


def test_history_assembler_places_after_target_decoy_in_visible_tail():
    base_spec = _spec()
    spec = replace(
        base_spec,
        target_age_seconds_range=(24, 28),
        decoys=(replace(base_spec.decoys[0], after_target=True),),
    )
    values = (10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)
    target = (100, 102, 104, 106, 108, 110, 112, 114)
    result = HistoryAssembler(StubMetricCatalog()).assemble(
        CapturedHistoryInputs(
            normal_metrics=(_frame(values),),
            normal_records=_captured(BASE_MS, len(values)),
            target_metrics=(_frame(target, start_ms=BASE_MS + 100_000),),
            target_records=_captured(BASE_MS + 100_000, len(target)),
            spec=spec,
            seed=33,
        ),
        agent_start_candidate_ms=BASE_MS + 500_000,
    )
    target_window = next(window for window in result.windows if window.role == "target")
    decoy_window = next(window for window in result.windows if window.decoy_id == "normal-spike")
    assert decoy_window.start_ms > target_window.end_ms
    assert decoy_window.end_ms == result.timeline.visible_end_ms
    assert result.timeline.audit["generator_version"].endswith("v6")


def test_history_spec_counts_aligned_post_target_decoys_once():
    base_spec = _spec()
    first_decoy = replace(
        base_spec.decoys[0],
        decoy_id="aligned-long",
        duration_seconds=8,
        after_target=True,
        alignment_group="incident-tail",
    )
    second_decoy = replace(
        base_spec.decoys[0],
        decoy_id="aligned-short",
        duration_seconds=4,
        after_target=True,
        alignment_group="incident-tail",
    )
    spec = replace(
        base_spec,
        target_age_seconds_range=(24, 28),
        decoys=(first_decoy, second_decoy),
    )
    values = (10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)
    target = (100, 102, 104, 106, 108, 110, 112, 114)
    result = HistoryAssembler(StubMetricCatalog()).assemble(
        CapturedHistoryInputs(
            normal_metrics=(_frame(values),),
            normal_records=_captured(BASE_MS, len(values)),
            target_metrics=(_frame(target, start_ms=BASE_MS + 100_000),),
            target_records=_captured(BASE_MS + 100_000, len(target)),
            spec=spec,
            seed=33,
        ),
        agent_start_candidate_ms=BASE_MS + 500_000,
    )
    assert {
        window.decoy_id
        for window in result.windows
        if window.decoy_id is not None
    } == {"aligned-long", "aligned-short"}
    assert max(window.end_ms for window in result.windows) == result.timeline.visible_end_ms


def test_history_assembler_orders_metric_variants_by_query_target():
    spec = _spec()
    values = (10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)
    target = (100, 102, 104, 106, 108, 110, 112, 114)
    normal_metrics = (
        _frame(values, query_target="secondary", series_target="secondary"),
        _frame(values),
    )
    target_metrics = (
        _frame(target, query_target="secondary", series_target="secondary", start_ms=BASE_MS + 100_000),
        _frame(target, start_ms=BASE_MS + 100_000),
    )
    result = HistoryAssembler(StubMetricCatalog()).assemble(
        CapturedHistoryInputs(
            normal_captures=(NormalHistoryCapture(
                capture_id="normal-0",
                metrics=normal_metrics,
                records=_captured(BASE_MS, len(values)),
            ),),
            target_metrics=target_metrics,
            target_records=_captured(BASE_MS + 100_000, len(target)),
            spec=spec,
            seed=33,
        ),
        agent_start_candidate_ms=BASE_MS + 500_000,
    )
    assert [frame.query_target for frame in result.timeline.metric_provider.frames] == [None, "secondary"]


def _aftermath_spec():
    return replace(
        _spec(),
        duration_seconds=80,
        target_age_seconds_range=(44, 52),
        decoys=(),
        aftermath="RETURN_TO_NORMAL",
        aftermath_capture_seconds=8,
    )


def test_history_assembler_inserts_real_aftermath_capture_and_keeps_normal_tail():
    spec = _aftermath_spec()
    result = HistoryAssembler(StubMetricCatalog()).assemble(
        CapturedHistoryInputs(
            normal_metrics=(_frame((10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)),),
            normal_records=_captured(BASE_MS, 12),
            target_metrics=(_frame((100, 102, 104, 106, 108, 110, 112, 114), start_ms=BASE_MS + 100_000),),
            target_records=_captured(BASE_MS + 100_000, 8),
            aftermath_metrics=(_frame((90, 70, 50, 40), start_ms=BASE_MS + 200_000),),
            aftermath_records=_captured(BASE_MS + 200_000, 4),
            spec=spec,
            seed=33,
        ),
        agent_start_candidate_ms=BASE_MS + 500_000,
    )
    audit = result.timeline.audit
    target = next(window for window in result.windows if window.role == "target")
    aftermath = next(window for window in result.windows if window.role == "aftermath")
    assert aftermath.start_ms == target.end_ms + 2_000
    assert audit["aftermath"] == "RETURN_TO_NORMAL"
    assert audit["aftermath_window"]["start_ms"] == aftermath.start_ms
    assert audit["plateau_sample_count"] == 0
    assert audit["aftermath_sample_count"] == 4
    assert audit["return_to_normal_sample_count"] > 0
    assert any(item["role"] == "aftermath" for item in audit["window_roles"])
    rendered = json.loads(render_metric_frame(
        result.timeline.metric_provider.query(MetricQuery(
            metric="qps", start_epoch_ms=aftermath.start_ms, end_epoch_ms=aftermath.end_ms,
        )),
        available_start_ms=result.timeline.visible_start_ms,
        available_end_ms=result.timeline.visible_end_ms,
        requested_start_ms=aftermath.start_ms,
        requested_end_ms=aftermath.end_ms,
        step_seconds=2,
    ))
    assert rendered["series"]["postgres"]["queries_per_second"] == [90.0, 70.0, 50.0, 40.0]
    tail = result.timeline.metric_provider.query(MetricQuery(
        metric="qps",
        start_epoch_ms=aftermath.end_ms + 2_000,
        end_epoch_ms=result.timeline.visible_end_ms,
    ))
    assert all(value < 100 for value in tail.series["postgres"]["queries_per_second"])


def test_history_assembler_anchors_target_window_to_the_overview_grid():
    spec = replace(_aftermath_spec(), overview_step_seconds=20)
    result = HistoryAssembler(StubMetricCatalog()).assemble(
        CapturedHistoryInputs(
            normal_metrics=(_frame((10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)),),
            normal_records=_captured(BASE_MS, 12),
            target_metrics=(_frame((100, 102, 104, 106, 108, 110, 112, 114), start_ms=BASE_MS + 100_000),),
            target_records=_captured(BASE_MS + 100_000, 8),
            aftermath_metrics=(_frame((90, 70, 50, 40), start_ms=BASE_MS + 200_000),),
            aftermath_records=_captured(BASE_MS + 200_000, 4),
            spec=spec,
            seed=33,
        ),
        agent_start_candidate_ms=BASE_MS + 500_000,
    )
    target = next(window for window in result.windows if window.role == "target")
    start_index = (target.start_ms - result.timeline.visible_start_ms) // 2_000
    span_points = (target.end_ms - target.start_ms) // 2_000 + 1
    overview_points = spec.overview_step_seconds // spec.base_step_seconds
    offset = start_index % overview_points
    # Exactly one overview grid point falls inside the window, in its late
    # half where the captured symptom is fully developed.
    assert overview_points - offset <= span_points
    assert overview_points - offset > span_points // 2


def test_history_assembler_reserves_the_pre_onset_strip_for_normal_operation_events():
    spec = replace(
        _aftermath_spec(),
        duration_seconds=120,
        target_age_seconds_range=(64, 72),
        overview_step_seconds=40,
        decoys=(HistoryDecoySpec(
            decoy_id="pre-onset-decoy",
            kind=DecoyKind.METRIC_ONLY,
            metric="qps",
            field="queries_per_second",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=8,
            amplitude_mad=1.0,
        ),),
        decoys_adjacent_to_target=True,
    )
    result = HistoryAssembler(StubMetricCatalog()).assemble(
        CapturedHistoryInputs(
            normal_metrics=(_frame((10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)),),
            normal_records=_captured(BASE_MS, 12),
            target_metrics=(_frame((100, 102, 104, 106, 108, 110, 112, 114), start_ms=BASE_MS + 100_000),),
            target_records=_captured(BASE_MS + 100_000, 8),
            aftermath_metrics=(_frame((90, 70, 50, 40), start_ms=BASE_MS + 200_000),),
            aftermath_records=_captured(BASE_MS + 200_000, 4),
            spec=spec,
            seed=33,
        ),
        agent_start_candidate_ms=BASE_MS + 500_000,
    )
    target = next(window for window in result.windows if window.role == "target")
    decoys = [window for window in result.windows if window.role == "decoy"]
    assert decoys
    strip_start = target.start_ms - spec.normal_capture_seconds * 1000
    for decoy in decoys:
        assert decoy.end_ms < strip_start or decoy.start_ms >= target.start_ms


def test_history_assembler_keeps_persist_plateau_for_persistent_contracts():
    spec = replace(_spec(), aftermath="PERSIST")
    result = HistoryAssembler(StubMetricCatalog()).assemble(
        CapturedHistoryInputs(
            normal_metrics=(_frame((10, 12, 11, 15, 13, 20, 18, 16, 14, 12, 10, 8)),),
            normal_records=_captured(BASE_MS, 12),
            target_metrics=(_frame((100, 102, 104, 106, 108, 110, 112, 114), start_ms=BASE_MS + 100_000),),
            target_records=_captured(BASE_MS + 100_000, 8),
            spec=spec,
            seed=33,
        ),
        agent_start_candidate_ms=BASE_MS + 500_000,
    )
    assert result.timeline.audit["plateau_sample_count"] > 0
    assert result.timeline.audit["aftermath"] == "PERSIST"
    target = next(window for window in result.windows if window.role == "target")
    tail = result.timeline.metric_provider.query(MetricQuery(
        metric="qps",
        start_epoch_ms=target.end_ms + 2_000,
        end_epoch_ms=result.timeline.visible_end_ms,
    ))
    assert all(value == 114 for value in tail.series["postgres"]["queries_per_second"])
