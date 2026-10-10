"""Deterministic assembly of database metric captures into frozen history."""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from statistics import median
from typing import Mapping

from src.execution.history.metrics import (
    MetricCatalog,
    MetricFrame,
    metric_variant_sort_key,
    validate_metric_frame,
)
from src.execution.history.records import (
    CapturedRecords,
    FrozenHistoricalRecordStore,
    HistoricalCoverage,
    HistoricalIntervalRecord,
    HistoricalPointRecord,
    HistoricalRecordSource,
)
from src.execution.history.timeline import (
    FrozenHistoricalTimeline,
    FrozenHistoryMetricProvider,
    build_history_hash,
)
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)


GENERATOR_VERSION = "frozen-history-procedural-history-v6"


@dataclass(frozen=True, slots=True, kw_only=True)
class NormalHistoryCapture:
    capture_id: str
    metrics: tuple[MetricFrame, ...]
    records: CapturedRecords


@dataclass(frozen=True, slots=True, kw_only=True)
class CapturedHistoryInputs:
    """Captured history inputs.

    Callers either pass the multi-capture bundle (``normal_captures``) or the
    single-capture shorthand (``normal_metrics`` + ``normal_records``). Cases
    whose contract declares a real post-incident recovery pass the optional
    ``aftermath_metrics``/``aftermath_records`` capture.
    """

    target_metrics: tuple[MetricFrame, ...]
    target_records: CapturedRecords
    spec: FrozenHistorySpec
    seed: int
    normal_captures: tuple[NormalHistoryCapture, ...] | None = None
    normal_metrics: tuple[MetricFrame, ...] | None = None
    normal_records: CapturedRecords | None = None
    aftermath_metrics: tuple[MetricFrame, ...] | None = None
    aftermath_records: CapturedRecords | None = None
    decoy_lightning_job_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if len(self.decoy_lightning_job_ids) != self.spec.decoy_lightning_job_count:
            raise ValueError(
                "CapturedHistoryInputs decoy lightning job ids differ from the Case contract: "
                f"declared_count={self.spec.decoy_lightning_job_count}, "
                f"actual_count={len(self.decoy_lightning_job_ids)}"
            )
        if self.normal_captures is None:
            if self.normal_metrics is None or self.normal_records is None:
                raise TypeError(
                    "CapturedHistoryInputs requires normal_captures or normal_metrics+normal_records"
                )
            object.__setattr__(self, "normal_captures", (
                NormalHistoryCapture(
                    capture_id="normal-0",
                    metrics=self.normal_metrics,
                    records=self.normal_records,
                ),
            ))
        if (self.aftermath_metrics is None) != (self.aftermath_records is None):
            raise TypeError(
                "CapturedHistoryInputs aftermath capture requires metrics and records together: "
                f"aftermath_metrics={self.aftermath_metrics!r}, aftermath_records={self.aftermath_records!r}"
            )
        if self.aftermath_metrics is not None and self.spec.aftermath != "RETURN_TO_NORMAL":
            raise ValueError(
                "Frozen-history aftermath capture requires RETURN_TO_NORMAL: "
                f"aftermath={self.spec.aftermath!r}"
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class HistoryWindow:
    window_id: str
    role: str
    start_ms: int
    end_ms: int
    source_id: str | None = None
    decoy_id: str | None = None
    source_start_index: int | None = None
    source_end_index: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class HistoryAssemblyResult:
    timeline: FrozenHistoricalTimeline
    windows: tuple[HistoryWindow, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class _GridFrame:
    frame: MetricFrame
    origin_ms: int
    values: Mapping[tuple[str, str], Mapping[int, float]]
    max_offset: int


class HistoryAssembler:
    """Build a history once; the resulting timeline has no mutation API."""

    _LIGHTNING_ACTIVITY_FIELDS = {
        "lightning_progress": {
            "required": ("estimated_chunks",),
            "activity": ("finished_chunks", "written_bytes", "imported_bytes", "progress_percent"),
        },
        "lightning_throughput": {
            "required": (),
            "activity": ("read_mb_per_second", "deliver_mb_per_second", "ingest_mb_per_second"),
        },
        "lightning_workers": {
            "required": (),
            "activity": ("idle_region", "idle_io", "idle_closed_engine", "open_engines"),
        },
    }

    def __init__(self, catalog: MetricCatalog) -> None:
        self.catalog = catalog

    def assemble(self, inputs: CapturedHistoryInputs, agent_start_candidate_ms: int) -> HistoryAssemblyResult:
        spec = inputs.spec
        spec.validate()
        if not isinstance(inputs.seed, int):
            raise TypeError(f"History seed must be an integer: seed={inputs.seed!r}")
        base_step_ms = spec.base_step_seconds * 1000
        visible_end_ms = (agent_start_candidate_ms // base_step_ms) * base_step_ms
        visible_start_ms = visible_end_ms - spec.duration_seconds * 1000 + base_step_ms
        point_count = spec.duration_seconds // spec.base_step_seconds
        if len(inputs.normal_captures) != spec.normal_capture_count:
            raise ValueError(
                "Frozen-history history normal capture count differs from Case contract: "
                f"expected={spec.normal_capture_count}, actual={len(inputs.normal_captures)}"
            )
        capture_ids = [capture.capture_id for capture in inputs.normal_captures]
        if len(capture_ids) != len(set(capture_ids)) or any(not capture_id for capture_id in capture_ids):
            raise ValueError(f"Frozen-history normal capture IDs must be non-empty and unique: capture_ids={capture_ids!r}")
        normal_captures = tuple(
            (capture, self._prepare_frames(capture.metrics, spec, f"normal capture {capture.capture_id!r}"))
            for capture in inputs.normal_captures
        )
        normal_frames = normal_captures[0][1]
        target_frames = self._prepare_frames(inputs.target_metrics, spec, "target")
        aftermath_frames = (
            self._prepare_frames(inputs.aftermath_metrics, spec, "aftermath")
            if inputs.aftermath_metrics is not None
            else None
        )
        frame_keys = tuple(sorted(normal_frames, key=metric_variant_sort_key))
        target_frame_keys = tuple(sorted(target_frames, key=metric_variant_sort_key))
        if frame_keys != target_frame_keys:
            raise ValueError(
                "Normal and target captures have different metric variants: "
                f"normal={frame_keys!r}, target={target_frame_keys!r}"
            )
        if aftermath_frames is not None:
            aftermath_frame_keys = tuple(sorted(aftermath_frames, key=metric_variant_sort_key))
            if aftermath_frame_keys != frame_keys:
                raise ValueError(
                    "Normal and aftermath captures have different metric variants: "
                    f"normal={frame_keys!r}, aftermath={aftermath_frame_keys!r}"
                )
            self._validate_frame_shape(aftermath_frames, normal_frames, "aftermath capture")
        for _, capture_frames in normal_captures:
            capture_keys = tuple(sorted(capture_frames, key=metric_variant_sort_key))
            if capture_keys != frame_keys:
                raise ValueError(
                    "Normal captures have different metric variants: "
                    f"expected={frame_keys!r}, actual={capture_keys!r}"
                )
            self._validate_frame_shape(capture_frames, normal_frames, "normal capture")
        self._validate_frame_shape(target_frames, normal_frames, "target capture")
        normal_points = spec.normal_capture_seconds // spec.base_step_seconds
        target_points = spec.fault_capture_seconds // spec.base_step_seconds
        aftermath_points = spec.aftermath_capture_seconds // spec.base_step_seconds
        if aftermath_frames is not None and aftermath_points <= 0:
            raise ValueError(
                "Frozen-history aftermath capture requires aftermath_capture_seconds: "
                f"aftermath_capture_seconds={spec.aftermath_capture_seconds}"
            )
        normal_available = {
            capture.capture_id: {
                key: frame.max_offset + 1 for key, frame in capture_frames.items()
            }
            for capture, capture_frames in normal_captures
        }
        if any(
            frame.max_offset + 1 < normal_points
            for _, capture_frames in normal_captures
            for frame in capture_frames.values()
        ):
            raise ValueError(
                "Normal capture does not cover its required base grid: "
                f"required_points={normal_points}, available={normal_available!r}"
            )
        if any(frame.max_offset + 1 < target_points for frame in target_frames.values()):
            raise ValueError(
                "Target capture does not cover its required base grid: "
                f"required_points={target_points}, available={ {key: frame.max_offset + 1 for key, frame in target_frames.items()}!r}"
            )
        if aftermath_frames is not None and any(
            frame.max_offset + 1 < aftermath_points for frame in aftermath_frames.values()
        ):
            raise ValueError(
                "Aftermath capture does not cover its required base grid: "
                f"required_points={aftermath_points}, available={ {key: frame.max_offset + 1 for key, frame in aftermath_frames.items()}!r}"
            )
        target_activity = self._validate_target_lightning_activity(target_frames, spec)
        rng = random.Random(inputs.seed)
        output = self._empty_output(normal_frames, point_count)
        records: list[HistoricalPointRecord | HistoricalIntervalRecord] = []
        # The pre-incident strip pins its records to the assembled normal
        # blocks immediately before the target window, so the target placement
        # must be drawn before the normal background fills (only specs that
        # declare a strip take this branch; the default draw order is
        # unchanged for every other spec).
        strip_points = spec.pre_incident_strip_seconds // spec.base_step_seconds
        strip_start_index: int | None = None
        pre_drawn_target_start_index: int | None = None
        if strip_points:
            pre_drawn_target_start_index = self._draw_target_start_index(spec, rng, point_count)
            strip_start_index = pre_drawn_target_start_index - strip_points
        blocks, block_records = self._fill_normal_background(
            output=output,
            normal_captures=normal_captures,
            point_count=point_count,
            normal_points=normal_points,
            spec=spec,
            rng=rng,
            visible_start_ms=visible_start_ms,
            strip_start_index=strip_start_index,
            strip_end_index=pre_drawn_target_start_index,
        )
        records.extend(block_records)
        crossfade_sample_count = self._apply_crossfade(
            output,
            blocks,
            spec.transition_seconds // spec.base_step_seconds,
        )
        seam_sample_count = self._stitch_seam_steps(output, blocks)
        if pre_drawn_target_start_index is not None:
            target_start_index = pre_drawn_target_start_index
        else:
            target_age_steps = rng.randint(
                spec.target_age_seconds_range[0] // spec.base_step_seconds,
                spec.target_age_seconds_range[1] // spec.base_step_seconds,
            )
            target_start_index = point_count - 1 - target_age_steps
            if aftermath_frames is not None:
                target_start_index = self._anchor_target_to_overview_grid(
                    target_start_index,
                    target_points,
                    point_count,
                    spec,
                )
        if target_start_index < 0 or target_start_index + target_points > point_count:
            raise ValueError(
                "Target bundle does not fit visible history: "
                f"target_start_index={target_start_index}, target_points={target_points}, point_count={point_count}"
            )
        if aftermath_frames is not None and target_start_index + target_points + aftermath_points > point_count:
            raise ValueError(
                "Frozen-history aftermath bundle does not fit visible history: "
                f"target_start_index={target_start_index}, target_points={target_points}, "
                f"aftermath_points={aftermath_points}, point_count={point_count}"
            )
        target_records, target_window, plateau_sample_count = self._insert_target_bundle(
            output=output,
            target_frames=target_frames,
            target_records=inputs.target_records,
            target_points=target_points,
            target_start_index=target_start_index,
            visible_start_ms=visible_start_ms,
            base_step_ms=base_step_ms,
            spec=spec,
        )
        records.extend(target_records)
        aftermath_window = None
        aftermath_sample_count = 0
        aftermath_end_index = target_start_index + target_points
        if aftermath_frames is not None:
            aftermath_records, aftermath_window, aftermath_sample_count = self._insert_aftermath_bundle(
                output=output,
                aftermath_frames=aftermath_frames,
                aftermath_records=inputs.aftermath_records,
                aftermath_points=aftermath_points,
                aftermath_start_index=aftermath_end_index,
                visible_start_ms=visible_start_ms,
                base_step_ms=base_step_ms,
            )
            records.extend(aftermath_records)
            aftermath_end_index += aftermath_points
        return_to_normal_sample_count = self._count_present_samples(
            output, aftermath_end_index, point_count
        )
        if not strip_points:
            records.extend(self._place_normal_operation_events(
                normal_records=inputs.normal_captures[0].records,
                normal_origin_ms=next(iter(normal_frames.values())).origin_ms,
                normal_points=normal_points,
                target_start_index=target_start_index,
                visible_start_ms=visible_start_ms,
                base_step_ms=base_step_ms,
            ))
        # Real aftermath captures reserve the pre-onset strip for the normal
        # operation events: the decoy segments must never contaminate the last
        # normal regime that directly precedes the incident.
        strip_reserve_points = (
            normal_points
            if aftermath_frames is not None
            else 0
        )
        valley_decoys = tuple(
            decoy for decoy in spec.decoys if decoy.kind is DecoyKind.CANDIDATE_VALLEY
        )
        metric_decoys = tuple(
            decoy for decoy in spec.decoys if decoy.kind is not DecoyKind.CANDIDATE_VALLEY
        )
        valley_windows = self._place_candidate_valleys(
            output=output,
            normal_frames=normal_frames,
            target_frames=target_frames,
            target_records=inputs.target_records,
            valleys=valley_decoys,
            target_start_index=target_start_index,
            target_points=target_points,
            normal_points=normal_points,
            strip_reserve_points=strip_reserve_points,
            spec=spec,
            rng=rng,
            visible_start_ms=visible_start_ms,
            base_step_ms=base_step_ms,
        )
        decoy_windows = [*valley_windows, *self._place_decoys(
            output=output,
            normal_frames=normal_frames,
            normal_records=inputs.normal_captures[0].records,
            decoys=metric_decoys,
            target_start_index=target_start_index,
            post_segment_start=aftermath_end_index + spec.transition_seconds // spec.base_step_seconds,
            point_count=point_count,
            normal_points=normal_points,
            strip_reserve_points=strip_reserve_points,
            spec=spec,
            rng=rng,
            visible_start_ms=visible_start_ms,
            base_step_ms=base_step_ms,
        )]
        decoy_windows = [*decoy_windows, *self._place_decoy_lightning_clones(
            output=output,
            decoy_lightning_job_ids=inputs.decoy_lightning_job_ids,
            occupied_windows=[target_window, *(window for window, _, _ in decoy_windows)],
            target_start_index=target_start_index,
            target_points=target_points,
            point_count=point_count,
            strip_reserve_points=strip_reserve_points,
            spec=spec,
            rng=rng,
            visible_start_ms=visible_start_ms,
            base_step_ms=base_step_ms,
        )]
        metric_only_sample_count = 0
        valley_sample_count = 0
        for window, window_records, sample_count in decoy_windows:
            records.extend(window_records)
            if window.source_id.startswith("candidate_valley"):
                valley_sample_count += sample_count
            else:
                metric_only_sample_count += sample_count
        records = self._deduplicate_records(records)
        self._validate_output(output, normal_frames, spec, visible_start_ms, visible_end_ms)
        frames = self._output_frames(output, normal_frames, visible_start_ms, spec.base_step_seconds)
        for frame in frames:
            validate_metric_frame(frame, self.catalog)
        record_store = self._build_record_store(
            records,
            tuple(capture.records for capture in inputs.normal_captures),
            inputs.target_records,
            spec,
            visible_start_ms,
            visible_end_ms,
        )
        generated_sample_count = (
            crossfade_sample_count
            + seam_sample_count
            + plateau_sample_count
            + metric_only_sample_count
            + valley_sample_count
        )
        present_sample_count = sum(
            1
            for channels in output.values()
            for fields in channels.values()
            for values in fields.values()
            for value in values
            if value is not None
        )
        if generated_sample_count > present_sample_count:
            raise ValueError(
                "History audit generated sample count exceeds present output samples: "
                f"generated_sample_count={generated_sample_count}, present_sample_count={present_sample_count}"
            )
        metadata = {
            "schema_version": spec.schema_version,
            "generator_version": GENERATOR_VERSION,
            "seed": inputs.seed,
            "visible_start_ms": visible_start_ms,
            "visible_end_ms": visible_end_ms,
            "base_step_seconds": spec.base_step_seconds,
            "overview_step_seconds": spec.overview_step_seconds,
            "aftermath": spec.aftermath,
            "catalog_sha256": self.catalog.fingerprint(),
            "metric_count": len(frames),
            "point_count": sum(sum(len(values) for values in frame.timestamps_ms.values()) for frame in frames),
            "source_record_counts": {
                source.value: sum(
                    1 for record in records
                    if record.source is source
                )
                for source in spec.record_sources
            },
            "block_count": len(blocks),
            "normal_capture_count": len(normal_captures),
            "normal_capture_origins": [
                {
                    "capture_id": capture.capture_id,
                    "start_ms": min(grid.origin_ms for grid in capture_frames.values()),
                    "end_ms": max(
                        grid.origin_ms + grid.max_offset * base_step_ms
                        for grid in capture_frames.values()
                    ),
                }
                for capture, capture_frames in normal_captures
            ],
            "normal_blocks": [
                {
                    "window_id": f"normal-{block['index']}",
                    "role": "normal",
                    "source_id": block["source_capture_id"],
                    "start_ms": visible_start_ms + int(block["start"]) * base_step_ms,
                    "end_ms": visible_start_ms + (int(block["end"]) - 1) * base_step_ms,
                    "source_capture_index": block["source_capture_index"],
                    "source_start_index": block["source_start"],
                    "source_end_index": block["source_end"] - 1,
                    "record_bearing": block["record_bearing"],
                    "crossfade": block["crossfade"],
                }
                for block in blocks
            ],
            "target_window": {
                "start_ms": target_window.start_ms,
                "end_ms": target_window.end_ms,
            },
            "decoy_windows": [
                {
                    "decoy_id": window.decoy_id,
                    "start_ms": window.start_ms,
                    "end_ms": window.end_ms,
                    "source_start_index": window.source_start_index,
                    "source_end_index": window.source_end_index,
                }
                for window, _, _ in decoy_windows
            ],
            "crossfade_sample_count": crossfade_sample_count,
            "plateau_sample_count": plateau_sample_count,
            "aftermath_sample_count": aftermath_sample_count,
            "return_to_normal_sample_count": return_to_normal_sample_count,
            "metric_only_sample_count": metric_only_sample_count,
            "valley_sample_count": valley_sample_count,
            "valley_window_count": len(valley_windows),
            "generated_sample_count": generated_sample_count,
            "real_sample_count": present_sample_count - generated_sample_count,
            "target_lightning_activity": target_activity,
        }
        if aftermath_window is not None:
            metadata["aftermath_window"] = {
                "start_ms": aftermath_window.start_ms,
                "end_ms": aftermath_window.end_ms,
            }
        used_capture_ids = {str(block["source_capture_id"]) for block in blocks}
        if used_capture_ids != set(capture_ids):
            raise ValueError(
                "Frozen-history history normal background did not use every real capture: "
                f"expected={capture_ids!r}, used={sorted(used_capture_ids)!r}"
            )
        metadata["normal_source_capture_ids"] = sorted(used_capture_ids)
        history_hash = build_history_hash(frames, record_store, metadata)
        window_roles = [
            {
                "window_id": target_window.window_id,
                "role": target_window.role,
                "source_id": target_window.source_id,
                "start_ms": target_window.start_ms,
                "end_ms": target_window.end_ms,
            },
            *([
                {
                    "window_id": aftermath_window.window_id,
                    "role": aftermath_window.role,
                    "source_id": aftermath_window.source_id,
                    "start_ms": aftermath_window.start_ms,
                    "end_ms": aftermath_window.end_ms,
                },
            ] if aftermath_window is not None else []),
            *[
                {
                    "window_id": window.window_id,
                    "role": window.role,
                    "decoy_id": window.decoy_id,
                    "source_id": window.source_id,
                    "start_ms": window.start_ms,
                    "end_ms": window.end_ms,
                }
                for window, _, _ in decoy_windows
            ],
        ]
        audit = {
            **metadata,
            "history_sha256": history_hash,
            "window_roles": window_roles,
            "normal_block_count": len(blocks),
            "normal_source_capture_ids": sorted({str(block["source_capture_id"]) for block in blocks}),
            "crossfade_count": sum(1 for block in blocks if block["crossfade"]),
            "reverse_count": sum(
                1
                for window, _, _ in decoy_windows
                if window.source_id == "metric_only_reverse"
            ),
            "missing_sample_count": sum(
                1
                for channels in output.values()
                for fields in channels.values()
                for values in fields.values()
                for value in values
                if value is None
            ),
        }
        provider = FrozenHistoryMetricProvider(
            frames=frames,
            visible_start_ms=visible_start_ms,
            visible_end_ms=visible_end_ms,
            base_step_seconds=spec.base_step_seconds,
            overview_step_seconds=spec.overview_step_seconds,
            max_points_per_series=spec.max_points_per_series,
            max_scalar_samples_per_response=spec.max_scalar_samples_per_response,
        )
        timeline = FrozenHistoricalTimeline(
            schema_version=spec.schema_version,
            visible_start_ms=visible_start_ms,
            visible_end_ms=visible_end_ms,
            base_step_seconds=spec.base_step_seconds,
            overview_step_seconds=spec.overview_step_seconds,
            metric_provider=provider,
            record_store=record_store,
            audit=audit,
        )
        windows = (target_window, *(window for window, _, _ in decoy_windows))
        if aftermath_window is not None:
            windows = (target_window, aftermath_window, *(window for window, _, _ in decoy_windows))
        return HistoryAssemblyResult(timeline=timeline, windows=windows)

    @staticmethod
    def _anchor_target_to_overview_grid(
        target_start_index: int,
        target_points: int,
        point_count: int,
        spec: FrozenHistorySpec,
    ) -> int:
        """Shift the target window so one overview grid point falls inside it.

        A self-contained incident whose evidence lives only inside the target
        window would be invisible on the coarse overview grid when the window
        fits between two grid points. Anchoring the window start into the band
        ``[overview_step - window_span + 1, overview_step - window_span + window_span // 2)``
        guarantees exactly one overview sample carries the anomaly — in the
        late half of the window, where the symptom is fully developed — without
        revealing its position among the other grid points.
        """
        overview_points = spec.overview_step_seconds // spec.base_step_seconds
        window_points = target_points
        if window_points >= overview_points:
            return target_start_index
        band_start = overview_points - window_points + 1
        band_end = band_start + window_points // 2
        offset = target_start_index % overview_points
        if band_start <= offset < band_end:
            return target_start_index
        shifted = target_start_index + (band_start - offset) % overview_points
        if shifted + target_points > point_count:
            raise ValueError(
                "Frozen-history overview-anchored target does not fit visible history: "
                f"target_start_index={target_start_index}, shifted={shifted}, target_points={target_points}, "
                f"point_count={point_count}, overview_points={overview_points}"
            )
        return shifted

    def _validate_target_lightning_activity(
        self,
        target_frames: Mapping[tuple[str, str | None], _GridFrame],
        spec: FrozenHistorySpec,
    ) -> dict[str, object]:
        required_metrics = {str(metric).casefold() for metric in spec.required_metrics}
        activity: dict[str, object] = {}
        for metric, fields in self._LIGHTNING_ACTIVITY_FIELDS.items():
            if metric not in required_metrics:
                continue
            grids = [grid for (frame_metric, _), grid in target_frames.items() if frame_metric == metric]
            if len(grids) != 1:
                raise ValueError(
                    "Frozen-history target capture must contain exactly one Lightning job frame: "
                    f"metric={metric!r}, frames={tuple(target_frames)!r}"
                )
            grid = grids[0]
            selected_fields = (*fields["required"], *fields["activity"])
            values = {
                field: tuple(
                    sample
                    for channel, samples in grid.values.items()
                    if channel[1] == field
                    for sample in samples.values()
                )
                for field in selected_fields
            }
            missing_fields = [field for field in selected_fields if not values[field]]
            if missing_fields:
                raise ValueError(
                    "Frozen-history target capture has no samples for required Lightning activity fields: "
                    f"metric={metric!r}, missing_fields={missing_fields!r}, "
                    f"query_target={grid.frame.query_target!r}"
                )
            zero_required = [
                field for field in fields["required"]
                if not any(float(sample) > 0 for sample in values[field])
            ]
            if zero_required:
                raise ValueError(
                    "Frozen-history target capture has no active Lightning baseline: "
                    f"metric={metric!r}, fields={zero_required!r}, "
                    f"query_target={grid.frame.query_target!r}"
                )
            active_fields = [
                field for field in fields["activity"]
                if any(float(sample) > 0 for sample in values[field])
            ]
            if not active_fields:
                raise ValueError(
                    "Frozen-history target capture has no active Lightning samples: "
                    f"metric={metric!r}, activity_fields={fields['activity']!r}, "
                    f"query_target={grid.frame.query_target!r}"
                )
            activity[metric] = {
                "query_target": grid.frame.query_target,
                "active_fields": active_fields,
                "maxima": {
                    field: max(float(sample) for sample in values[field])
                    for field in selected_fields
                },
            }
        return activity

    def _prepare_frames(self, frames: tuple[MetricFrame, ...], spec: FrozenHistorySpec, label: str) -> dict[tuple[str, str | None], _GridFrame]:
        result: dict[tuple[str, str | None], _GridFrame] = {}
        capture_origins: set[int] = set()
        for frame in frames:
            validate_metric_frame(frame, self.catalog)
            key = (frame.metric, frame.query_target)
            if key in result:
                raise ValueError(f"{label.title()} capture has duplicate metric variant: key={key!r}")
            if frame.step_seconds != spec.base_step_seconds:
                raise ValueError(
                    f"{label.title()} capture step differs from history base: key={key!r}, "
                    f"frame_step={frame.step_seconds}, base_step={spec.base_step_seconds}"
                )
            origin_ms = min(timestamp for timestamps in frame.timestamps_ms.values() for timestamp in timestamps)
            capture_origins.add(origin_ms)
            values: dict[tuple[str, str], dict[int, float]] = {}
            max_offset = 0
            for series_target, timestamps in frame.timestamps_ms.items():
                for field, samples in frame.series[series_target].items():
                    channel = {}
                    for timestamp_ms, value in zip(timestamps, samples, strict=True):
                        offset_ms = timestamp_ms - origin_ms
                        base_step_ms = spec.base_step_seconds * 1000
                        if offset_ms < 0 or offset_ms % base_step_ms:
                            raise ValueError(
                                f"{label.title()} capture timestamp is not on base grid: key={key!r}, "
                                f"timestamp_ms={timestamp_ms}, origin_ms={origin_ms}, base_step_seconds={spec.base_step_seconds}"
                            )
                        offset = offset_ms // base_step_ms
                        channel[offset] = value
                        max_offset = max(max_offset, offset)
                    values[(series_target, field)] = channel
            result[key] = _GridFrame(frame=frame, origin_ms=origin_ms, values=values, max_offset=max_offset)
        if not result:
            raise ValueError(f"{label.title()} capture must contain metric frames")
        if len(capture_origins) != 1:
            raise ValueError(
                f"{label.title()} metric variants do not share one capture origin: "
                f"origins={sorted(capture_origins)!r}"
            )
        for key, grid in result.items():
            if label == "normal":
                expected_offsets = set(range(grid.max_offset + 1))
                for channel, samples in grid.values.items():
                    missing = sorted(expected_offsets - set(samples))
                    if missing:
                        raise ValueError(
                            f"{label.title()} capture has holes in a metric channel: "
                            f"key={key!r}, channel={channel!r}, missing_offsets={missing[:10]!r}, "
                            f"missing_count={len(missing)}"
                        )
        return result

    @staticmethod
    def _validate_frame_shape(
        actual: Mapping[tuple[str, str | None], _GridFrame],
        expected: Mapping[tuple[str, str | None], _GridFrame],
        label: str,
    ) -> None:
        for key in expected:
            expected_frame = expected[key].frame
            actual_frame = actual[key].frame
            if set(expected_frame.series) != set(actual_frame.series):
                raise ValueError(
                    f"{label.title()} captures have different series targets: key={key!r}, "
                    f"expected={sorted(expected_frame.series)!r}, actual={sorted(actual_frame.series)!r}"
                )
            for series_target in expected_frame.series:
                expected_fields = set(expected_frame.series[series_target])
                actual_fields = set(actual_frame.series[series_target])
                if expected_fields != actual_fields:
                    raise ValueError(
                        f"{label.title()} captures have different metric fields: key={key!r}, "
                        f"series_target={series_target!r}, expected={sorted(expected_fields)!r}, "
                        f"actual={sorted(actual_fields)!r}"
                    )

    @staticmethod
    def _empty_output(normal_frames: Mapping[tuple[str, str | None], _GridFrame], point_count: int) -> dict[tuple[str, str | None], dict[str, dict[str, list[float | None]]]]:
        output = {}
        for key, grid in normal_frames.items():
            output[key] = {
                target: {
                    field: [None] * point_count
                    for field in fields
                }
                for target, fields in grid.frame.series.items()
            }
        return output

    def _draw_target_start_index(
        self,
        spec: FrozenHistorySpec,
        rng: random.Random,
        point_count: int,
    ) -> int:
        target_age_steps = rng.randint(
            spec.target_age_seconds_range[0] // spec.base_step_seconds,
            spec.target_age_seconds_range[1] // spec.base_step_seconds,
        )
        return point_count - 1 - target_age_steps

    def _fill_normal_background(
        self,
        *,
        output: dict,
        normal_captures: tuple[tuple[NormalHistoryCapture, Mapping[tuple[str, str | None], _GridFrame]], ...],
        point_count: int,
        normal_points: int,
        spec: FrozenHistorySpec,
        rng: random.Random,
        visible_start_ms: int,
        strip_start_index: int | None = None,
        strip_end_index: int | None = None,
    ) -> tuple[list[dict[str, object]], list[HistoricalPointRecord | HistoricalIntervalRecord]]:
        blocks: list[dict[str, object]] = []
        records: list[HistoricalPointRecord | HistoricalIntervalRecord] = []
        cursor = 0
        block_index = 0
        transition_points = spec.transition_seconds // spec.base_step_seconds
        while cursor < point_count:
            remaining = point_count - cursor
            max_length = min(spec.block_max_seconds // spec.base_step_seconds, remaining)
            min_length = min(spec.block_min_seconds // spec.base_step_seconds, max_length)
            if max_length <= 0:
                raise ValueError(f"Normal block layout cannot cover history: cursor={cursor}, point_count={point_count}")
            length = rng.randint(min_length, max_length)
            capture_index = block_index % len(normal_captures)
            capture, normal_frames = normal_captures[capture_index]
            source_start = rng.randint(0, normal_points - length)
            for key, grid in normal_frames.items():
                for series_target, fields in output[key].items():
                    for field in fields:
                        source_channel = grid.values[(series_target, field)]
                        for offset in range(length):
                            source_value = source_channel.get(source_start + offset)
                            output[key][series_target][field][cursor + offset] = source_value
            source_start_ms = next(iter(normal_frames.values())).origin_ms + source_start * spec.base_step_seconds * 1000
            destination_start_ms = visible_start_ms + cursor * spec.base_step_seconds * 1000
            block_records = _records_in_range(
                capture.records,
                source_start_ms,
                source_start_ms + (length - 1) * spec.base_step_seconds * 1000,
                destination_start_ms - source_start_ms,
            )
            if strip_start_index is not None and strip_end_index is not None:
                # Strip-declaring specs publish captured records under the
                # strip contract: strip-pinned records may only surface inside
                # the pre-incident strip, every other captured record replays
                # with its block as captured.
                strip_start_ms = visible_start_ms + strip_start_index * spec.base_step_seconds * 1000
                strip_end_ms = visible_start_ms + strip_end_index * spec.base_step_seconds * 1000
                block_records = [
                    record for record in block_records
                    if not _is_strip_pinned(record, spec)
                    or strip_start_ms <= record_timestamp_ms(record) < strip_end_ms
                ]
            else:
                # Operation events describe one real action. Normal blocks replay
                # metric context only; the events are strip-placed once before the
                # target window instead of being multiplied across every block.
                block_records = [
                    record
                    for record in block_records
                    if record.source is not HistoricalRecordSource.OPERATION_EVENT
                ]
            records.extend(block_records)
            blocks.append({
                "index": block_index,
                "start": cursor,
                "end": cursor + length,
                "source_capture_id": capture.capture_id,
                "source_capture_index": capture_index,
                "source_start": source_start,
                "source_end": source_start + length,
                "crossfade": False,
                "record_bearing": bool(block_records),
                "transition_points": transition_points,
            })
            cursor += length
            block_index += 1
        for left, right in zip(blocks, blocks[1:]):
            left["crossfade"] = not left["record_bearing"] and not right["record_bearing"]
            left["boundary"] = right["start"]
        return blocks, records

    def _insert_target_bundle(
        self,
        *,
        output: dict,
        target_frames: Mapping[tuple[str, str | None], _GridFrame],
        target_records: CapturedRecords,
        target_points: int,
        target_start_index: int,
        visible_start_ms: int,
        base_step_ms: int,
        spec: FrozenHistorySpec,
    ) -> tuple[list[HistoricalPointRecord | HistoricalIntervalRecord], HistoryWindow, int]:
        for key, channels in output.items():
            for series_target, fields in channels.items():
                for values in fields.values():
                    for index in range(target_start_index, target_start_index + target_points):
                        values[index] = None
                target_grid = target_frames[key]
                for field in fields:
                    source_channel = target_grid.values.get((series_target, field), {})
                    for offset in range(target_points):
                        if offset in source_channel:
                            values = fields[field]
                            values[target_start_index + offset] = source_channel[offset]
        target_origin_ms = next(iter(target_frames.values())).origin_ms
        destination_start_ms = visible_start_ms + target_start_index * base_step_ms
        records = _records_in_range(
            target_records,
            target_origin_ms,
            target_origin_ms + (target_points - 1) * base_step_ms,
            destination_start_ms - target_origin_ms,
        )
        target_window = HistoryWindow(
            window_id="target",
            role="target",
            start_ms=destination_start_ms,
            end_ms=destination_start_ms + (target_points - 1) * base_step_ms,
            source_id="target_capture",
        )
        plateau_start = target_start_index + target_points
        plateau_sample_count = 0
        if spec.aftermath == "PERSIST":
            # The persistent target state remains visible after the captured
            # onset: a still-ongoing incident keeps its symptom at the tail.
            for channels in output.values():
                for fields in channels.values():
                    for values in fields.values():
                        last = next((values[index] for index in range(target_start_index + target_points - 1, target_start_index - 1, -1) if values[index] is not None), None)
                        if last is not None:
                            for index in range(plateau_start, len(values)):
                                values[index] = last
                                plateau_sample_count += 1
        return records, target_window, plateau_sample_count

    def _insert_aftermath_bundle(
        self,
        *,
        output: dict,
        aftermath_frames: Mapping[tuple[str, str | None], _GridFrame],
        aftermath_records: CapturedRecords,
        aftermath_points: int,
        aftermath_start_index: int,
        visible_start_ms: int,
        base_step_ms: int,
    ) -> tuple[list[HistoricalPointRecord | HistoricalIntervalRecord], HistoryWindow, int]:
        """Insert the real captured post-incident recovery window.

        The capture is taken from this run's real environment after the fault
        was physically resolved, so the return to normal is a replayed real
        convergence (for example an archive backlog draining) instead of a
        fabricated instant step back to baseline.
        """
        for key, channels in output.items():
            for series_target, fields in channels.items():
                for values in fields.values():
                    for index in range(aftermath_start_index, aftermath_start_index + aftermath_points):
                        values[index] = None
                aftermath_grid = aftermath_frames[key]
                for field in fields:
                    source_channel = aftermath_grid.values.get((series_target, field), {})
                    for offset in range(aftermath_points):
                        if offset in source_channel:
                            values = fields[field]
                            values[aftermath_start_index + offset] = source_channel[offset]
        aftermath_origin_ms = next(iter(aftermath_frames.values())).origin_ms
        destination_start_ms = visible_start_ms + aftermath_start_index * base_step_ms
        records = _records_in_range(
            aftermath_records,
            aftermath_origin_ms,
            aftermath_origin_ms + (aftermath_points - 1) * base_step_ms,
            destination_start_ms - aftermath_origin_ms,
        )
        aftermath_window = HistoryWindow(
            window_id="aftermath",
            role="aftermath",
            start_ms=destination_start_ms,
            end_ms=destination_start_ms + (aftermath_points - 1) * base_step_ms,
            source_id="aftermath_capture",
        )
        sample_count = self._count_present_samples(
            output, aftermath_start_index, aftermath_start_index + aftermath_points
        )
        return records, aftermath_window, sample_count

    @staticmethod
    def _count_present_samples(
        output: dict,
        start_index: int,
        end_index: int,
    ) -> int:
        return sum(
            1
            for channels in output.values()
            for fields in channels.values()
            for values in fields.values()
            for value in values[start_index:end_index]
            if value is not None
        )

    @staticmethod
    def _place_normal_operation_events(
        *,
        normal_records: CapturedRecords,
        normal_origin_ms: int,
        normal_points: int,
        target_start_index: int,
        visible_start_ms: int,
        base_step_ms: int,
    ) -> list[HistoricalPointRecord]:
        """Keep real normal operation events in the normal strip before the fault."""
        placed: list[HistoricalPointRecord] = []
        for record in normal_records.point_records:
            if record.source is not HistoricalRecordSource.OPERATION_EVENT:
                continue
            offset_ms = record.timestamp_ms - normal_origin_ms
            if offset_ms < 0:
                continue
            # Operation events carry wall-clock timestamps and need not land
            # exactly on the metric sampler's aligned grid.
            source_index = int(round(offset_ms / base_step_ms))
            if source_index >= normal_points:
                continue
            distance_from_capture_end = normal_points - source_index
            destination_index = target_start_index - distance_from_capture_end
            if destination_index < 0 or destination_index >= target_start_index:
                continue
            placed.append(HistoricalPointRecord(
                source=record.source,
                target=record.target,
                timestamp_ms=visible_start_ms + destination_index * base_step_ms,
                payload=record.payload,
            ))
        return placed

    def _place_candidate_valleys(
        self,
        *,
        output: dict,
        normal_frames: Mapping[tuple[str, str | None], _GridFrame],
        target_frames: Mapping[tuple[str, str | None], _GridFrame],
        target_records: CapturedRecords,
        valleys: tuple[HistoryDecoySpec, ...],
        target_start_index: int,
        target_points: int,
        normal_points: int,
        strip_reserve_points: int,
        spec: FrozenHistorySpec,
        rng: random.Random,
        visible_start_ms: int,
        base_step_ms: int,
    ) -> list[tuple[HistoryWindow, list[HistoricalPointRecord], int]]:
        """Place candidate valleys that replay the real capture's own shapes.

        Each valley copies the target window's channel values with the same
        depth, duration, and metric signature, so coarse-overview and
        mid-granularity statistics cannot separate it from the buried incident
        window. The composition only scrambles or truncates the ordered
        causality (or the record completeness), which keeps every valley
        excludable by the formal evidence channels: operation-event sequences
        and the wal-burst -> delivery-stall -> backlog-climb ordering. Every
        valley anchors exactly one overview grid point inside its own span, so
        each one competes as a coarse candidate next to the target window.
        """
        if not valleys:
            return []
        gap_points = spec.transition_seconds // spec.base_step_seconds
        segment_end = target_start_index - gap_points - strip_reserve_points
        overview_points = spec.overview_step_seconds // spec.base_step_seconds
        valley_points = target_points
        if valley_points >= overview_points:
            raise ValueError(
                "Frozen-history candidate valleys must stay shorter than the overview step to anchor "
                f"a competing grid point: valley_points={valley_points}, overview_points={overview_points}"
            )
        band_start = overview_points - valley_points + 1
        target_origin_ms = next(iter(target_frames.values())).origin_ms
        result = []
        cursor = segment_end
        for decoy in reversed(valleys):
            desired_start = cursor - valley_points
            shift = ((desired_start % overview_points) - band_start) % overview_points
            start = desired_start - shift
            if start < 0:
                raise ValueError(
                    "Frozen-history candidate valleys cannot fit before the target window with their "
                    f"overview anchor: decoy={decoy!r}, start={start}, segment_end={segment_end}"
                )
            cursor = start - gap_points
            baseline_source_start = rng.randrange(normal_points)
            for key, channels in output.items():
                target_grid = target_frames[key]
                baseline_metric = str(key[0]).casefold() in {
                    str(metric).casefold() for metric in decoy.baseline_metrics
                }
                for series_target, fields in channels.items():
                    for field, values in fields.items():
                        if baseline_metric:
                            source_channel = normal_frames[key].values[(series_target, field)]
                            for dest_offset in range(valley_points):
                                source_offset = (baseline_source_start + dest_offset) % normal_points
                                values[start + dest_offset] = source_channel.get(source_offset)
                            continue
                        source_channel = target_grid.values[(series_target, field)]
                        for dest_offset in range(valley_points):
                            source_offset = dest_offset
                            if decoy.valley_profile == "scrambled_order":
                                third = valley_points // 3
                                deep = valley_points - 2 * third
                                if dest_offset < third:
                                    source_offset = dest_offset
                                elif dest_offset < third + deep:
                                    source_offset = 2 * third + (dest_offset - third)
                                else:
                                    source_offset = third + (dest_offset - third - deep)
                            values[start + dest_offset] = source_channel[source_offset]
            records: list[HistoricalPointRecord] = []
            if decoy.record_event_types:
                allowed_event_types = {str(event_type) for event_type in decoy.record_event_types}
                valley_start_ms = visible_start_ms + start * base_step_ms
                for record in _records_in_range(
                    target_records,
                    target_origin_ms,
                    target_origin_ms + (valley_points - 1) * base_step_ms,
                    valley_start_ms - target_origin_ms,
                ):
                    if record.payload.get("event_type") not in allowed_event_types:
                        continue
                    payload = dict(record.payload)
                    payload.pop("correlation_id", None)
                    details = dict(payload.get("details", {}))
                    for identity_key in ("segment", "sha256"):
                        details.pop(identity_key, None)
                    payload["details"] = details
                    records.append(HistoricalPointRecord(
                        source=record.source,
                        target=record.target,
                        timestamp_ms=record.timestamp_ms,
                        payload=payload,
                    ))
            sample_count = self._count_present_samples(output, start, start + valley_points)
            result.append((
                HistoryWindow(
                    window_id=f"decoy-{decoy.decoy_id}-1",
                    role="decoy",
                    decoy_id=decoy.decoy_id,
                    start_ms=visible_start_ms + start * base_step_ms,
                    end_ms=visible_start_ms + (start + valley_points - 1) * base_step_ms,
                    source_id=f"candidate_valley:{decoy.valley_profile}",
                ),
                records,
                sample_count,
            ))
        result.reverse()
        return result

    def _place_decoys(
        self,
        *,
        output: dict,
        normal_frames: Mapping[tuple[str, str | None], _GridFrame],
        normal_records: CapturedRecords,
        decoys: tuple[HistoryDecoySpec, ...],
        target_start_index: int,
        post_segment_start: int,
        point_count: int,
        normal_points: int,
        strip_reserve_points: int,
        spec: FrozenHistorySpec,
        rng: random.Random,
        visible_start_ms: int,
        base_step_ms: int,
    ) -> list[tuple[HistoryWindow, list[HistoricalPointRecord | HistoricalIntervalRecord], int]]:
        units = [
            (decoy, count)
            for decoy in decoys
            for count in range(decoy.count)
        ]
        rng.shuffle(units)
        gap_points = spec.transition_seconds // spec.base_step_seconds
        result = []
        result.extend(self._place_decoy_segment(
            output=output,
            normal_frames=normal_frames,
            normal_records=normal_records,
            units=[unit for unit in units if not unit[0].after_target],
            segment_start=0,
            segment_end=target_start_index - gap_points - strip_reserve_points,
            normal_points=normal_points,
            spec=spec,
            rng=rng,
            visible_start_ms=visible_start_ms,
            base_step_ms=base_step_ms,
            decoys=decoys,
        ))
        result.extend(self._place_decoy_segment(
            output=output,
            normal_frames=normal_frames,
            normal_records=normal_records,
            units=[unit for unit in units if unit[0].after_target],
            segment_start=post_segment_start,
            segment_end=point_count,
            normal_points=normal_points,
            spec=spec,
            rng=rng,
            visible_start_ms=visible_start_ms,
            base_step_ms=base_step_ms,
            decoys=decoys,
        ))
        return result

    def _place_decoy_segment(
        self,
        *,
        output: dict,
        normal_frames: Mapping[tuple[str, str | None], _GridFrame],
        normal_records: CapturedRecords,
        units: list[tuple[HistoryDecoySpec, int]],
        segment_start: int,
        segment_end: int,
        normal_points: int,
        spec: FrozenHistorySpec,
        rng: random.Random,
        visible_start_ms: int,
        base_step_ms: int,
        decoys: tuple[HistoryDecoySpec, ...],
    ) -> list[tuple[HistoryWindow, list[HistoricalPointRecord | HistoricalIntervalRecord], int]]:
        if not units:
            return []
        aligned_post = bool(
            units[0][0].after_target
            and all(decoy.alignment_group is not None for decoy, _ in units)
        )
        total_points = (
            max(decoy.duration_seconds // spec.base_step_seconds for decoy, _ in units)
            if aligned_post
            else sum(decoy.duration_seconds // spec.base_step_seconds for decoy, _ in units)
        )
        gap_points = spec.transition_seconds // spec.base_step_seconds
        required = total_points + (0 if aligned_post else max(len(units) - 1, 0) * gap_points)
        available = segment_end - segment_start
        if required > available:
            placement = "after target" if units[0][0].after_target else "before target"
            raise ValueError(
                f"Decoy windows cannot fit {placement}: required_points={required}, available_points={available}, "
                f"segment=({segment_start},{segment_end}), decoys={decoys!r}"
            )
        slack = available - required
        if units[0][0].after_target:
            # A post-target decoy models a later benign symptom and stays in
            # the visible tail, flush against the end of history.
            cursor = segment_end - required
        elif spec.decoys_adjacent_to_target:
            # Keep captured competitors immediately before the fault bundle.
            cursor = segment_start + slack
        else:
            cursor = segment_start + (rng.randint(0, slack) if slack else 0)
        aligned_start = cursor if aligned_post else None
        aligned_source_start = None
        aligned_baseline_copied = False
        if aligned_post:
            aligned_source_start = rng.randrange(normal_points)
        used_benign_ranges: dict[tuple[str, str, str | None], list[tuple[int, int]]] = {}
        result = []
        for decoy, ordinal in units:
            duration_points = decoy.duration_seconds // spec.base_step_seconds
            start = aligned_start if aligned_start is not None else cursor
            end = start + duration_points
            destination_start_ms = visible_start_ms + start * base_step_ms
            reverse = False
            source_start = None
            if decoy.kind is DecoyKind.CAPTURED_BENIGN:
                source_key = (decoy.metric, decoy.field, decoy.target)
                source_ranges = used_benign_ranges.setdefault(source_key, [])
                source_start = self._select_benign_source(
                    normal_frames,
                    decoy,
                    duration_points,
                    normal_points,
                    excluded_ranges=tuple(source_ranges),
                )
                source_ranges.append((source_start, source_start + duration_points))
                source_start_ms = next(iter(normal_frames.values())).origin_ms + source_start * base_step_ms
                records = _records_in_range(
                    normal_records,
                    source_start_ms,
                    source_start_ms + (duration_points - 1) * base_step_ms,
                    destination_start_ms - source_start_ms,
                )
                # Captured-benign decoys copy raw metric observations only.
                # Replaying a normal block must not manufacture another copy
                # of an operation event at a new timestamp.
                records = [
                    record
                    for record in records
                    if record.source is not HistoricalRecordSource.OPERATION_EVENT
                ]
                reverse = bool(
                    decoy.allow_reverse
                    and not records
                    and self._reverse_eligible(normal_frames, source_start, duration_points)
                    and rng.getrandbits(1)
                )
                self._copy_normal_window(
                    output,
                    normal_frames,
                    source_start,
                    start,
                    duration_points,
                    reverse=reverse,
                )
            else:
                if aligned_post and decoy.kind is DecoyKind.METRIC_ONLY:
                    # Aligned decoys form one window. Copy the baseline once so
                    # later field mutations accumulate instead of erasing
                    # earlier mutations.
                    if not aligned_baseline_copied:
                        self._copy_repeated_normal_window(
                            output,
                            normal_frames,
                            aligned_source_start,
                            start,
                            total_points,
                            normal_points,
                        )
                        aligned_baseline_copied = True
                    source_start = aligned_source_start
                elif duration_points <= normal_points:
                    source_start = rng.randint(0, normal_points - duration_points)
                    reverse = bool(
                        decoy.allow_reverse
                        and self._reverse_eligible(normal_frames, source_start, duration_points)
                        and rng.getrandbits(1)
                    )
                    self._copy_normal_window(
                        output,
                        normal_frames,
                        source_start,
                        start,
                        duration_points,
                        reverse=reverse,
                    )
                else:
                    # Long metric-only windows are synthetic noise over a
                    # repeated normal baseline; captured-benign windows still
                    # require a complete real normal capture.
                    source_start = rng.randrange(normal_points)
                    reverse = False
                    self._copy_repeated_normal_window(
                        output,
                        normal_frames,
                        source_start,
                        start,
                        duration_points,
                        normal_points,
                    )
                generated_sample_count = self._apply_metric_only(
                    output,
                    normal_frames,
                    decoy,
                    start,
                    end,
                    spec,
                )
                records = []
            if decoy.kind is DecoyKind.CAPTURED_BENIGN:
                generated_sample_count = 0
            result.append((
                HistoryWindow(
                    window_id=f"decoy-{decoy.decoy_id}-{ordinal}",
                    role="decoy",
                    decoy_id=decoy.decoy_id,
                    start_ms=destination_start_ms,
                    end_ms=destination_start_ms + (duration_points - 1) * base_step_ms,
                    source_id=(
                        "metric_only_reverse"
                        if reverse
                        else "metric_only"
                        if decoy.kind is DecoyKind.METRIC_ONLY
                        else "captured_benign"
                    ),
                    source_start_index=(
                        source_start
                        if decoy.kind is DecoyKind.CAPTURED_BENIGN
                        else None
                    ),
                    source_end_index=(
                        source_start + duration_points - 1
                        if decoy.kind is DecoyKind.CAPTURED_BENIGN and source_start is not None
                        else None
                    ),
                ),
                records,
                generated_sample_count,
            ))
            if aligned_start is None:
                cursor = end + gap_points
        return result

    @staticmethod
    def _reverse_eligible(
        normal_frames: Mapping[tuple[str, str | None], _GridFrame],
        source_start: int,
        length: int,
    ) -> bool:
        """Reverse only complete, locally stable blocks across every channel."""
        for grid in normal_frames.values():
            for samples in grid.values.values():
                window = [samples.get(source_start + offset) for offset in range(length)]
                if any(value is None for value in window):
                    return False
                numeric = [float(value) for value in window]
                center = median(samples.values())
                mad = median(abs(value - center) for value in samples.values())
                if mad == 0:
                    if numeric[0] != numeric[-1]:
                        return False
                    continue
                if abs(numeric[-1] - numeric[0]) / mad > 0.5:
                    return False
        return True

    @staticmethod
    def _copy_normal_window(
        output: dict,
        normal_frames: Mapping,
        source_start: int,
        destination_start: int,
        length: int,
        *,
        reverse: bool = False,
    ) -> None:
        for key, channels in output.items():
            grid = normal_frames[key]
            for series_target, fields in channels.items():
                for field, values in fields.items():
                    source_channel = grid.values[(series_target, field)]
                    for offset in range(length):
                        source_offset = source_start + (length - 1 - offset if reverse else offset)
                        values[destination_start + offset] = source_channel.get(source_offset)

    @staticmethod
    def _copy_repeated_normal_window(
        output: dict,
        normal_frames: Mapping,
        source_start: int,
        destination_start: int,
        length: int,
        normal_points: int,
    ) -> None:
        for key, channels in output.items():
            grid = normal_frames[key]
            for series_target, fields in channels.items():
                for field, values in fields.items():
                    source_channel = grid.values[(series_target, field)]
                    for offset in range(length):
                        source_offset = (source_start + offset) % normal_points
                        values[destination_start + offset] = source_channel.get(source_offset)

    @staticmethod
    def _select_benign_source(
        normal_frames: Mapping,
        decoy: HistoryDecoySpec,
        duration_points: int,
        normal_points: int,
        excluded_ranges: tuple[tuple[int, int], ...] = (),
    ) -> int:
        selected_channels = []
        for key, grid in normal_frames.items():
            if key[0] != decoy.metric:
                continue
            for (series_target, field), values in grid.values.items():
                if field != decoy.field:
                    continue
                if decoy.target is not None and decoy.target not in {key[1], series_target}:
                    continue
                selected_channels.append(values)
        if not selected_channels:
            raise ValueError(f"No normal channel matches captured_benign decoy: decoy={decoy!r}")
        channel = selected_channels[0]
        values = [channel[index] for index in range(normal_points) if index in channel]
        if len(values) < duration_points:
            raise ValueError(f"Normal channel is shorter than captured_benign decoy: decoy={decoy!r}, points={len(values)}")
        center = median(values)
        mad = median(abs(value - center) for value in values)
        # The declared deviation scale is the channel MAD; a sparse real
        # capture with zero MAD falls back to its observed peak, which bounds
        # every normalized deviation by 1.0.
        scale = mad if mad > 0 else max(abs(value - center) for value in values)
        best_start: int | None = None
        best_deviation = 0.0
        for start in range(0, normal_points - duration_points + 1):
            if any(start < excluded_end and excluded_start < start + duration_points for excluded_start, excluded_end in excluded_ranges):
                continue
            window = [channel[index] for index in range(start, start + duration_points) if index in channel]
            if len(window) != duration_points:
                continue
            deviation = (sum(window) / len(window) - center) / scale if scale > 0 else 0.0
            directed = deviation if decoy.direction is DecoyDirection.SPIKE else -deviation
            if best_start is None or directed > best_deviation:
                best_start = start
                best_deviation = directed
        if best_start is None:
            raise ValueError(f"No complete normal window for captured_benign decoy: decoy={decoy!r}")
        return best_start

    def _place_decoy_lightning_clones(
        self,
        *,
        output: dict,
        decoy_lightning_job_ids: tuple[str, ...],
        occupied_windows: list[HistoryWindow],
        target_start_index: int,
        target_points: int,
        point_count: int,
        strip_reserve_points: int,
        spec: FrozenHistorySpec,
        rng: random.Random,
        visible_start_ms: int,
        base_step_ms: int,
    ) -> list[tuple[HistoryWindow, list, int]]:
        """Give every seeded batch decoy job its own frozen lightning history.

        Each decoy receives a time-shifted, amplitude-scaled clone of the real
        target capture's lightning series under the decoy job id. Only the
        real freeze window coincides with the captured frontend SLO storm and
        TiKV write pressure, so binding a paused job to its history requires
        the cross-metric temporal reasoning the Case contract declares; job
        ids, series availability, and window ages carry no signal on their own.
        """
        if not decoy_lightning_job_ids:
            return []
        lightning_keys = [key for key in output if key[0].startswith("lightning_")]
        real_keys = {}
        for key in lightning_keys:
            job_channels = [channel for channel in output[key] if channel.startswith("lightning-job/")]
            if len(job_channels) != 1:
                raise ValueError(
                    f"Lightning clone placement expects one real job channel: key={key!r}, "
                    f"channels={sorted(output[key])!r}"
                )
            real_keys[key] = job_channels[0]
        occupied = []
        for window in occupied_windows:
            start_index = (window.start_ms - visible_start_ms) // base_step_ms
            end_index = (window.end_ms - visible_start_ms) // base_step_ms + 1
            occupied.append((start_index, end_index))
        occupied.append((point_count - target_points, point_count))
        gap = spec.transition_seconds // spec.base_step_seconds
        search_high = target_start_index - target_points - gap
        clone_windows = []
        scales = (0.6, 0.75, 0.9, 1.05, 1.2, 1.3, 1.4, 0.7)
        for index, job_id in enumerate(decoy_lightning_job_ids):
            scale = scales[index % len(scales)]
            clone_start = None
            for _ in range(64):
                candidate = rng.randint(point_count // 40, max(search_high, point_count // 40))
                if all(candidate + target_points + gap <= start or end + gap <= candidate for start, end in occupied):
                    clone_start = candidate
                    break
            if clone_start is None:
                raise ValueError(
                    "Frozen-history lightning clone placement found no free window: "
                    f"job_id={job_id!r}, target_start_index={target_start_index}, point_count={point_count}"
                )
            occupied.append((clone_start, clone_start + target_points))
            clone_end_ms = visible_start_ms + (clone_start + target_points - 1) * base_step_ms
            sample_count = 0
            for key in lightning_keys:
                real_values = output[key][real_keys[key]]
                output[key][job_id] = {
                    field: [None] * point_count for field in real_values
                }
                for field, values in output[key][job_id].items():
                    for offset in range(target_points):
                        source = real_values[field][target_start_index + offset]
                        if source is not None:
                            values[clone_start + offset] = source * scale
                            sample_count += 1
            clone_windows.append((HistoryWindow(
                window_id=f"decoy-lightning-{index + 1}",
                role="decoy",
                start_ms=visible_start_ms + clone_start * base_step_ms,
                end_ms=clone_end_ms,
                source_id="lightning_series_clone",
                decoy_id=job_id,
                source_start_index=target_start_index,
                source_end_index=target_start_index + target_points - 1,
            ), [], sample_count))
        return clone_windows

    def _apply_metric_only(self, output: dict, normal_frames: Mapping, decoy: HistoryDecoySpec, start: int, end: int, spec: FrozenHistorySpec) -> int:
        changed = 0
        for key, channels in output.items():
            if key[0] != decoy.metric:
                continue
            grid = normal_frames[key]
            for series_target, fields in channels.items():
                if decoy.target is not None and decoy.target not in {key[1], series_target}:
                    continue
                source_channel = grid.values[(series_target, decoy.field)]
                source_values = [value for value in source_channel.values()]
                center = median(source_values)
                mad = median([abs(value - center) for value in source_values])
                if mad <= 0:
                    # A metric-only decoy is synthetic by contract.  A flat
                    # real channel still needs a finite scale; use the
                    # catalog's smallest meaningful unit instead of failing
                    # the whole capture during a short normal window.
                    mad = max(max(abs(value - center) for value in source_values), 1.0)
                values = fields[decoy.field]
                for index in range(start, end):
                    if values[index] is None:
                        continue
                    u = (index - start) / max(end - start - 1, 1)
                    # The symmetric smoothstep above peaks at the middle and returns to zero.
                    centered = 2 * u if u <= 0.5 else 2 * (1 - u)
                    envelope = 3 * centered * centered - 2 * centered * centered * centered
                    delta = float(decoy.amplitude_mad) * mad * envelope
                    mutated = values[index] + (delta if decoy.direction is DecoyDirection.SPIKE else -delta)
                    definition = self.catalog.definition(decoy.metric)
                    if definition.lower_bound is not None and mutated < definition.lower_bound:
                        raise ValueError(f"metric_only decoy violates lower catalog bound: decoy={decoy!r}, value={mutated}")
                    if definition.upper_bound is not None and mutated > definition.upper_bound:
                        raise ValueError(f"metric_only decoy violates upper catalog bound: decoy={decoy!r}, value={mutated}")
                    values[index] = mutated
                    changed += 1
        if changed == 0:
            raise ValueError(f"metric_only decoy did not match any present channel: decoy={decoy!r}")
        return changed

    @staticmethod
    def _apply_crossfade(output: dict, blocks: list[dict[str, object]], transition_points: int) -> int:
        if transition_points <= 0:
            raise ValueError(f"Crossfade transition_points must be positive: transition_points={transition_points}")
        changed = 0
        for left, right in zip(blocks, blocks[1:]):
            if not left["crossfade"]:
                continue
            boundary = int(right["start"])
            start = max(int(left["start"]) + 1, boundary - transition_points // 2)
            end = min(int(right["end"]) - 1, boundary + transition_points // 2)
            if end <= start:
                continue
            for channels in output.values():
                for fields in channels.values():
                    for values in fields.values():
                        left_value = values[start]
                        right_value = values[end]
                        if left_value is None or right_value is None:
                            continue
                        for index in range(start, end + 1):
                            u = (index - start) / (end - start)
                            weight = 3 * u * u - 2 * u * u * u
                            values[index] = (1 - weight) * left_value + weight * right_value
                            changed += 1
        return changed

    @staticmethod
    def _stitch_seam_steps(output: dict, blocks: list[dict[str, object]]) -> int:
        """Remove single-tick step artifacts at block seams.

        A block seam that lands inside a held policy window would otherwise
        render one bogus dip/raise point on step-shaped channels (quota,
        weights), handing the Agent a count-the-flickers shortcut. Real
        policy changes hold for the whole window, so where the right block
        reverts to the left value within a couple of points, the seam point
        inherits the left value.
        """
        changed = 0
        for left, right in zip(blocks, blocks[1:]):
            boundary = int(right["start"])
            if boundary <= int(left["start"]) or boundary >= int(right["end"]):
                continue
            for channels in output.values():
                for fields in channels.values():
                    for values in fields.values():
                        left_value = values[boundary - 1]
                        right_value = values[boundary]
                        if left_value is None or right_value is None or left_value == right_value:
                            continue
                        lookahead = values[boundary + 1: boundary + 3]
                        if lookahead and all(item == left_value for item in lookahead if item is not None):
                            values[boundary] = left_value
                            changed += 1
        return changed

    @staticmethod
    def _deduplicate_records(records: list[HistoricalPointRecord | HistoricalIntervalRecord]) -> list[HistoricalPointRecord | HistoricalIntervalRecord]:
        """Do not replay one point operation into every normal history block."""
        seen: set[tuple] = set()
        unique: list[HistoricalPointRecord | HistoricalIntervalRecord] = []
        for record in records:
            payload = json.dumps(dict(record.payload), sort_keys=True, separators=(",", ":"), default=str)
            if isinstance(record, HistoricalPointRecord):
                # Operation events describe one real action. Normal metric
                # blocks may replay the same captured event, but distinct
                # events at different times must remain visible so agents can
                # reason about maintenance followed by the fault revision.
                key = ("point", record.source.value, record.target, record.timestamp_ms, payload)
            else:
                key = ("interval", record.source.value, record.target, record.start_ms, record.end_ms, payload)
            if key in seen:
                continue
            seen.add(key)
            unique.append(record)
        return unique

    def _validate_output(self, output: dict, normal_frames: Mapping, spec: FrozenHistorySpec, visible_start_ms: int, visible_end_ms: int) -> None:
        expected_points = spec.duration_seconds // spec.base_step_seconds
        if visible_end_ms - visible_start_ms != (expected_points - 1) * spec.base_step_seconds * 1000:
            raise ValueError(f"History visible grid has wrong point span: start={visible_start_ms}, end={visible_end_ms}, expected_points={expected_points}")
        for key, channels in output.items():
            definition = self.catalog.definition(key[0])
            for series_target, fields in channels.items():
                if set(fields) != set(definition.value_fields):
                    raise ValueError(f"History output fields differ from catalog: key={key!r}, target={series_target!r}")
                for field, values in fields.items():
                    if len(values) != expected_points:
                        raise ValueError(f"History output has wrong length: key={key!r}, target={series_target!r}, field={field!r}, length={len(values)}, expected={expected_points}")
                    for value in values:
                        if value is not None and not math.isfinite(value):
                            raise ValueError(f"History output contains non-finite value: key={key!r}, target={series_target!r}, field={field!r}, value={value!r}")
                        if value is not None and definition.lower_bound is not None and value < definition.lower_bound:
                            raise ValueError(f"History output violates lower catalog bound: key={key!r}, field={field!r}, value={value!r}")
                        if value is not None and definition.upper_bound is not None and value > definition.upper_bound:
                            raise ValueError(f"History output violates upper catalog bound: key={key!r}, field={field!r}, value={value!r}")

    @staticmethod
    def _output_frames(output: dict, normal_frames: Mapping, visible_start_ms: int, base_step_seconds: int) -> tuple[MetricFrame, ...]:
        frames = []
        for key in sorted(output, key=metric_variant_sort_key):
            series: dict[str, dict[str, tuple[float, ...]]] = {}
            timestamps: dict[str, tuple[int, ...]] = {}
            for series_target, fields in output[key].items():
                present = [
                    index
                    for index in range(len(next(iter(fields.values()))))
                    if all(fields[field][index] is not None for field in fields)
                ]
                if not present:
                    continue
                timestamps[series_target] = tuple(visible_start_ms + index * base_step_seconds * 1000 for index in present)
                series[series_target] = {
                    field: tuple(float(fields[field][index]) for index in present)
                    for field in fields
                }
            if not series:
                raise ValueError(f"History output frame has no present series: key={key!r}")
            frames.append(MetricFrame(metric=key[0], query_target=key[1], step_seconds=base_step_seconds, series=series, timestamps_ms=timestamps))
        return tuple(frames)

    @staticmethod
    def _build_record_store(
        records: list,
        normal_records: tuple[CapturedRecords, ...],
        target_records: CapturedRecords,
        spec: FrozenHistorySpec,
        visible_start_ms: int,
        visible_end_ms: int,
    ) -> FrozenHistoricalRecordStore:
        allowed_sources = set(spec.record_sources)
        filtered = [record for record in records if record.source in allowed_sources]
        coverage = []
        for source in spec.record_sources:
            normal_coverage = [
                item
                for capture in normal_records
                for item in capture.coverage
                if item.source is source
            ]
            if not normal_coverage:
                raise ValueError(
                    f"History source has no normal capture coverage: source={source.value!r}"
                )
            target_coverage = [item for item in target_records.coverage if item.source is source]
            if not target_coverage:
                raise ValueError(
                    f"History source has no target capture coverage: source={source.value!r}"
                )
            source_coverage = [*normal_coverage, *target_coverage]
            targets = {item.target for item in source_coverage}
            for target in targets or {None}:
                coverage.append(HistoricalCoverage(source=source, target=target, start_ms=visible_start_ms, end_ms=visible_end_ms))
        return FrozenHistoricalRecordStore.from_captured(CapturedRecords(
            point_records=tuple(record for record in filtered if isinstance(record, HistoricalPointRecord)),
            interval_records=tuple(record for record in filtered if isinstance(record, HistoricalIntervalRecord)),
            coverage=tuple(coverage),
        ))


def _is_strip_pinned(record: HistoricalPointRecord | HistoricalIntervalRecord, spec: FrozenHistorySpec) -> bool:
    """Whether this record may only be published inside the pre-incident strip."""
    if not spec.strip_pinned_record_actions:
        return False
    payload = getattr(record, "payload", {})
    return (str(payload.get("event_type")), str(payload.get("action"))) in {
        (event_type, action) for event_type, action in spec.strip_pinned_record_actions
    }


def record_timestamp_ms(record: HistoricalPointRecord | HistoricalIntervalRecord) -> int:
    """Start timestamp of a point or interval record."""
    if isinstance(record, HistoricalIntervalRecord):
        return record.start_ms
    return record.timestamp_ms


def _records_in_range(captured: CapturedRecords, start_ms: int, end_ms: int, delta_ms: int) -> list[HistoricalPointRecord | HistoricalIntervalRecord]:
    records: list[HistoricalPointRecord | HistoricalIntervalRecord] = []
    for record in captured.point_records:
        if start_ms <= record.timestamp_ms <= end_ms:
            payload = dict(record.payload)
            if payload.get("event_type") == "marker_commit":
                payload.pop("correlation_id", None)
                details = dict(payload.get("details", {}))
                details.pop("marker_id", None)
                details.pop("checksum", None)
                details.pop("committed_at", None)
                payload["details"] = details
            elif isinstance(payload.get("details"), dict):
                payload["details"] = {
                    key: value + delta_ms if key in {"start_ms", "end_ms"} else value
                    for key, value in payload["details"].items()
                }
            records.append(HistoricalPointRecord(source=record.source, target=record.target, timestamp_ms=record.timestamp_ms + delta_ms, payload=payload))
    for record in captured.interval_records:
        if record.end_ms >= start_ms and record.start_ms <= end_ms:
            records.append(HistoricalIntervalRecord(source=record.source, target=record.target, start_ms=record.start_ms + delta_ms, end_ms=record.end_ms + delta_ms, payload=record.payload))
    return records
