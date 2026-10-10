"""Frozen metric timeline and deterministic history hashing."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from src.execution.history.metrics import MetricFrame, MetricQuery, metric_variant_sort_key
from src.execution.history.records import FrozenHistoricalRecordStore


class FrozenHistoryMetricProvider:
    """Immutable metric provider backed by a complete frozen timeline."""

    def __init__(
        self,
        *,
        frames: tuple[MetricFrame, ...],
        visible_start_ms: int,
        visible_end_ms: int,
        base_step_seconds: int,
        overview_step_seconds: int,
        max_points_per_series: int,
        max_scalar_samples_per_response: int,
    ) -> None:
        if visible_start_ms >= visible_end_ms:
            raise ValueError(f"Frozen history visible range must be positive: start={visible_start_ms}, end={visible_end_ms}")
        if base_step_seconds <= 0 or overview_step_seconds <= 0 or overview_step_seconds % base_step_seconds:
            raise ValueError(
                f"Frozen history steps are invalid: base_step_seconds={base_step_seconds}, "
                f"overview_step_seconds={overview_step_seconds}"
            )
        if max_points_per_series <= 0 or max_scalar_samples_per_response <= 0:
            raise ValueError("Frozen history response budgets must be positive")
        frame_map: dict[tuple[str, str | None], MetricFrame] = {}
        for frame in frames:
            key = (frame.metric, frame.query_target)
            if key in frame_map:
                raise ValueError(f"Frozen history has duplicate metric variant: key={key!r}")
            if frame.step_seconds != base_step_seconds:
                raise ValueError(
                    f"Frozen history frame step differs from base: key={key!r}, "
                    f"frame_step={frame.step_seconds}, base_step={base_step_seconds}"
                )
            frame_map[key] = frame
        if not frame_map:
            raise ValueError("Frozen history requires at least one metric frame")
        self._frames = MappingProxyType(frame_map)
        self.visible_start_ms = visible_start_ms
        self.visible_end_ms = visible_end_ms
        self.base_step_seconds = base_step_seconds
        self.overview_step_seconds = overview_step_seconds
        self.max_points_per_series = max_points_per_series
        self.max_scalar_samples_per_response = max_scalar_samples_per_response

    @property
    def frames(self) -> tuple[MetricFrame, ...]:
        return tuple(self._frames.values())

    def _resolve_query(self, query: MetricQuery) -> tuple[MetricFrame, int, int, int]:
        key = (query.metric, query.target)
        try:
            frame = self._frames[key]
        except KeyError as exc:
            # A catalog metric can expose several series (for example one per
            # relation) while the capture remains a single query variant.
            # Select that series from the query_target=None frame instead of
            # forcing each relation to become a private history variant.
            aggregate = self._frames.get((query.metric, None)) if query.target is not None else None
            if aggregate is None or query.target not in aggregate.series:
                raise ValueError(
                    f"Frozen history metric variant is unavailable: metric={query.metric!r}, target={query.target!r}, "
                    f"available={sorted(self._frames, key=metric_variant_sort_key)!r}"
                ) from exc
            frame = MetricFrame(
                metric=aggregate.metric,
                query_target=query.target,
                step_seconds=aggregate.step_seconds,
                series={query.target: aggregate.series[query.target]},
                timestamps_ms={query.target: aggregate.timestamps_ms[query.target]},
            )
        explicit_window = query.start_epoch_ms is not None
        start_ms = query.start_epoch_ms if explicit_window else self.visible_start_ms
        end_ms = query.end_epoch_ms if explicit_window else self.visible_end_ms
        step = query.step_seconds or (self.base_step_seconds if explicit_window else self.overview_step_seconds)
        # Agents commonly derive the end timestamp from wall clock time.  The
        # frozen capture can lag that clock by one sampler tick; absorb only
        # that narrow drift while preserving hard history boundaries.
        if end_ms > self.visible_end_ms and end_ms - self.visible_end_ms <= self.base_step_seconds * 1000:
            end_ms = self.visible_end_ms
        if start_ms < self.visible_start_ms or end_ms > self.visible_end_ms:
            raise ValueError(
                f"Frozen history query is outside visible range: metric={query.metric!r}, target={query.target!r}, "
                f"requested=({start_ms},{end_ms}), available=({self.visible_start_ms},{self.visible_end_ms})"
            )
        if (start_ms - self.visible_start_ms) % (self.base_step_seconds * 1000) or (end_ms - self.visible_start_ms) % (self.base_step_seconds * 1000):
            raise ValueError(
                f"Frozen history query must align to base grid: metric={query.metric!r}, target={query.target!r}, "
                f"start_ms={start_ms}, end_ms={end_ms}, visible_start_ms={self.visible_start_ms}, "
                f"base_step_seconds={self.base_step_seconds}"
            )
        if step <= 0 or step % self.base_step_seconds:
            raise ValueError(
                f"Frozen history step must be a positive base-step multiple: metric={query.metric!r}, "
                f"step_seconds={step}, base_step_seconds={self.base_step_seconds}"
            )
        return frame, start_ms, end_ms, step

    def query(self, query: MetricQuery) -> MetricFrame:
        frame, start_ms, end_ms, step = self._resolve_query(query)
        selected = frame.slice(start_ms, end_ms)
        if step != self.base_step_seconds:
            selected = selected.resample(step, start_ms, end_ms)
        explicit_window = query.start_epoch_ms is not None
        while True:
            point_overages = [
                (target, len(timestamps))
                for target, timestamps in selected.timestamps_ms.items()
                if len(timestamps) > self.max_points_per_series
            ]
            scalar_samples = sum(
                len(timestamps) * len(selected.series[target])
                for target, timestamps in selected.timestamps_ms.items()
            )
            if not point_overages and scalar_samples <= self.max_scalar_samples_per_response:
                break
            if explicit_window:
                if point_overages:
                    target, points = point_overages[0]
                    minimum_step = step
                    while math.ceil(points / (minimum_step // self.base_step_seconds)) > self.max_points_per_series:
                        minimum_step += self.base_step_seconds
                    raise ValueError(
                        f"Frozen history query exceeds point budget: metric={query.metric!r}, target={target!r}, "
                        f"points={points}, max_points_per_series={self.max_points_per_series}, "
                        f"minimum_viable_step_seconds={minimum_step}"
                    )
                raise ValueError(
                    f"Frozen history query exceeds scalar sample budget: metric={query.metric!r}, "
                    f"scalar_samples={scalar_samples}, max_scalar_samples={self.max_scalar_samples_per_response}"
                )
            # A no-window query is the coarse overview path. Preserve the
            # complete frozen timeline but choose the smallest coarser step
            # that fits the shared response budgets for wide relation metrics.
            next_step = step + self.base_step_seconds
            if next_step > max(end_ms - start_ms, self.base_step_seconds):
                raise ValueError(
                    f"Frozen history overview cannot fit response budget: metric={query.metric!r}, "
                    f"scalar_samples={scalar_samples}, max_scalar_samples={self.max_scalar_samples_per_response}"
                )
            step = next_step
            selected = frame.slice(start_ms, end_ms).resample(step, start_ms, end_ms)
        return selected


@dataclass(frozen=True, slots=True, kw_only=True)
class FrozenHistoricalTimeline:
    schema_version: int
    visible_start_ms: int
    visible_end_ms: int
    base_step_seconds: int
    overview_step_seconds: int
    metric_provider: FrozenHistoryMetricProvider
    record_store: FrozenHistoricalRecordStore
    audit: Mapping[str, object]

    def __post_init__(self) -> None:
        if self.audit.get("history_sha256") is None:
            raise ValueError("Frozen history audit must contain history_sha256")
        object.__setattr__(self, "audit", MappingProxyType(dict(self.audit)))

    @property
    def history_sha256(self) -> str:
        return str(self.audit["history_sha256"])


def build_history_hash(
    frames: tuple[MetricFrame, ...],
    records: FrozenHistoricalRecordStore,
    metadata: Mapping[str, object],
) -> str:
    def frame_payload(frame: MetricFrame) -> dict[str, object]:
        return {
            "metric": frame.metric,
            "query_target": frame.query_target,
            "step_seconds": frame.step_seconds,
            "timestamps_ms": {target: list(values) for target, values in frame.timestamps_ms.items()},
            "series": {
                target: {field: list(values) for field, values in fields.items()}
                for target, fields in frame.series.items()
            },
        }

    payload = {
        "metadata": dict(metadata),
        "frames": [frame_payload(frame) for frame in frames],
        "point_records": {
            f"{source}:{target}": [
                {"timestamp_ms": record.timestamp_ms, "payload": dict(record.payload)}
                for record in records_list
            ]
            for (source, target), records_list in records.point_records.items()
        },
        "interval_records": {
            f"{source}:{target}": [
                {"start_ms": record.start_ms, "end_ms": record.end_ms, "payload": dict(record.payload)}
                for record in records_list
            ]
            for (source, target), records_list in records.interval_records.items()
        },
        "coverage": [
            {
                "source": item.source.value,
                "target": item.target,
                "start_ms": item.start_ms,
                "end_ms": item.end_ms,
            }
            for item in records.coverage
        ],
    }
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()
