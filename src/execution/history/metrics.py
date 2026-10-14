"""Database-independent metric history contracts and rendering."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from src.agent_language import agent_text


UTC = timezone.utc
METRIC_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
_MILLISECONDS = 1000
_PEAK_FIELDS = frozenset({
    "lock_manager_waiters",
    "waiter_ms_per_sec",
    "slowpath_backends",
    "p95_ms",
    "p99_ms",
    "cl_waiting",
    "maxwait_sec",
    "maxwait_ms",
})


def metric_variant_sort_key(variant: tuple[str, str | None]) -> tuple[str, int, str]:
    metric, target = variant
    return metric, 0 if target is None else 1, target or ""


@dataclass(frozen=True, slots=True, kw_only=True)
class MetricDefinition:
    name: str
    value_fields: tuple[str, ...]
    lookback_seconds: int
    source_step_seconds: int
    lower_bound: float | None
    upper_bound: float | None

    def __post_init__(self) -> None:
        if not self.name or not self.value_fields:
            raise ValueError(f"Metric definition requires name and fields: definition={self!r}")
        if len(set(self.value_fields)) != len(self.value_fields):
            raise ValueError(f"Metric definition has duplicate fields: definition={self!r}")
        if self.lookback_seconds < 0 or self.source_step_seconds <= 0:
            raise ValueError(f"Metric timing values are invalid: definition={self!r}")
        if self.lower_bound is not None and self.upper_bound is not None and self.lower_bound > self.upper_bound:
            raise ValueError(f"Metric bounds are reversed: definition={self!r}")


class MetricCatalog(Protocol):
    """System adapter contract for metric identity and target semantics."""

    system: object

    @property
    def metric_names(self) -> frozenset[str]:
        ...

    def definition(self, metric: str) -> MetricDefinition:
        ...

    def target_variants(self, metric: str, deployment: object) -> tuple[str | None, ...]:
        ...

    def validate_target(self, metric: str, target: str | None, deployment: object) -> None:
        ...

    def fingerprint(self) -> str:
        ...


def validate_metric_query(query: "MetricQuery", catalog: MetricCatalog) -> None:
    catalog.definition(query.metric)


@dataclass(frozen=True, slots=True, kw_only=True)
class MetricQuery:
    metric: str
    target: str | None = None
    start_epoch_ms: int | None = None
    end_epoch_ms: int | None = None
    step_seconds: int | None = None
    rate_window_seconds: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.metric, str) or not self.metric:
            raise ValueError(f"MetricQuery metric must be non-empty: metric={self.metric!r}")
        object.__setattr__(self, "metric", self.metric.casefold())
        for name in ("start_epoch_ms", "end_epoch_ms"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, int) or isinstance(value, bool)):
                raise TypeError(
                    f"MetricQuery {name} must be an integer epoch millisecond value: "
                    f"metric={self.metric!r}, {name}={value!r}"
                )
        if (self.start_epoch_ms is None) != (self.end_epoch_ms is None):
            raise ValueError(
                "MetricQuery start_epoch_ms and end_epoch_ms must be provided together: "
                f"metric={self.metric!r}, start={self.start_epoch_ms!r}, end={self.end_epoch_ms!r}"
            )
        if self.start_epoch_ms is not None and self.start_epoch_ms > self.end_epoch_ms:
            raise ValueError(
                f"MetricQuery window is reversed: metric={self.metric!r}, "
                f"start={self.start_epoch_ms}, end={self.end_epoch_ms}"
            )
        if self.step_seconds is not None:
            if not isinstance(self.step_seconds, int) or isinstance(self.step_seconds, bool):
                raise TypeError(f"MetricQuery step_seconds must be an integer: query={self!r}")
            if self.step_seconds <= 0:
                raise ValueError(f"MetricQuery step_seconds must be positive: query={self!r}")
        if self.rate_window_seconds is not None:
            if not isinstance(self.rate_window_seconds, int) or isinstance(self.rate_window_seconds, bool):
                raise TypeError(f"MetricQuery rate_window_seconds must be an integer: query={self!r}")
            if self.rate_window_seconds <= 0:
                raise ValueError(f"MetricQuery rate_window_seconds must be positive: query={self!r}")


@dataclass(frozen=True, slots=True, kw_only=True)
class MetricFrame:
    metric: str
    query_target: str | None
    step_seconds: int
    series: Mapping[str, Mapping[str, tuple[float, ...]]]
    timestamps_ms: Mapping[str, tuple[int, ...]]

    def __post_init__(self) -> None:
        if not isinstance(self.metric, str) or not self.metric:
            raise ValueError(f"MetricFrame metric must be non-empty: metric={self.metric!r}")
        if not isinstance(self.step_seconds, int) or isinstance(self.step_seconds, bool) or self.step_seconds <= 0:
            raise ValueError(f"MetricFrame step_seconds must be positive: frame={self!r}")
        if not self.series:
            raise ValueError(
                f"MetricFrame must contain at least one series: metric={self.metric!r}, query_target={self.query_target!r}"
            )
        if set(self.series) != set(self.timestamps_ms):
            raise ValueError(
                "MetricFrame series/timestamp targets differ: "
                f"metric={self.metric!r}, series={sorted(self.series)!r}, timestamps={sorted(self.timestamps_ms)!r}"
            )
        expected_fields: set[str] | None = None
        normalized_series: dict[str, Mapping[str, tuple[float, ...]]] = {}
        normalized_timestamps: dict[str, tuple[int, ...]] = {}
        for raw_target, raw_fields in self.series.items():
            target = str(raw_target)
            timestamps = tuple(self._timestamp(value, target) for value in self.timestamps_ms[raw_target])
            if any(current <= previous for previous, current in zip(timestamps, timestamps[1:])):
                raise ValueError(
                    f"MetricFrame timestamps must be strictly increasing: metric={self.metric!r}, "
                    f"series_target={target!r}, timestamps={timestamps!r}"
                )
            fields = set(raw_fields)
            if expected_fields is None:
                expected_fields = fields
            elif fields != expected_fields:
                raise ValueError(
                    "MetricFrame series fields differ: "
                    f"metric={self.metric!r}, series_target={target!r}, expected={sorted(expected_fields)!r}, "
                    f"actual={sorted(fields)!r}"
                )
            normalized_fields: dict[str, tuple[float, ...]] = {}
            for field, raw_values in raw_fields.items():
                values = tuple(float(value) for value in raw_values)
                if len(values) != len(timestamps):
                    raise ValueError(
                        f"MetricFrame field length differs from timestamps: metric={self.metric!r}, "
                        f"series_target={target!r}, field={field!r}, points={len(timestamps)}, values={len(values)}"
                    )
                if any(not math.isfinite(value) for value in values):
                    raise ValueError(
                        f"MetricFrame contains non-finite value: metric={self.metric!r}, "
                        f"series_target={target!r}, field={field!r}, values={values!r}"
                    )
                normalized_fields[str(field)] = values
            normalized_series[target] = MappingProxyType(normalized_fields)
            normalized_timestamps[target] = timestamps
        object.__setattr__(self, "metric", self.metric.casefold())
        object.__setattr__(self, "series", MappingProxyType(normalized_series))
        object.__setattr__(self, "timestamps_ms", MappingProxyType(normalized_timestamps))

    @staticmethod
    def _timestamp(value: object, target: str) -> int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"MetricFrame timestamp must be an integer epoch millisecond: target={target!r}, value={value!r}")
        if value < 0:
            raise ValueError(f"MetricFrame timestamp must be non-negative: target={target!r}, value={value!r}")
        return value

    @property
    def point_count(self) -> int:
        counts = {len(timestamps) for timestamps in self.timestamps_ms.values()}
        if len(counts) != 1:
            raise ValueError(
                f"MetricFrame series have different point counts: metric={self.metric!r}, counts={sorted(counts)!r}"
            )
        return counts.pop()

    def slice(self, start_epoch_ms: int, end_epoch_ms: int) -> "MetricFrame":
        if start_epoch_ms > end_epoch_ms:
            raise ValueError(
                f"MetricFrame slice window is reversed: metric={self.metric!r}, "
                f"start={start_epoch_ms}, end={end_epoch_ms}"
            )
        sliced_series: dict[str, dict[str, tuple[float, ...]]] = {}
        sliced_timestamps: dict[str, tuple[int, ...]] = {}
        for target, timestamps in self.timestamps_ms.items():
            indices = [
                index
                for index, timestamp in enumerate(timestamps)
                if start_epoch_ms <= timestamp <= end_epoch_ms
            ]
            sliced_timestamps[target] = tuple(timestamps[index] for index in indices)
            sliced_series[target] = {
                field: tuple(values[index] for index in indices)
                for field, values in self.series[target].items()
            }
        return MetricFrame(
            metric=self.metric,
            query_target=self.query_target,
            step_seconds=self.step_seconds,
            series=sliced_series,
            timestamps_ms=sliced_timestamps,
        )

    def resample(self, step_seconds: int, start_epoch_ms: int, end_epoch_ms: int) -> "MetricFrame":
        if step_seconds <= 0 or step_seconds % self.step_seconds:
            raise ValueError(
                f"MetricFrame resample step must be a positive multiple of base step: metric={self.metric!r}, "
                f"base_step={self.step_seconds}, requested_step={step_seconds}"
            )
        window = self.slice(start_epoch_ms, end_epoch_ms)
        selected_series: dict[str, dict[str, tuple[float, ...]]] = {}
        selected_timestamps: dict[str, tuple[int, ...]] = {}
        for target, timestamps in window.timestamps_ms.items():
            indices = [
                index
                for index, timestamp in enumerate(timestamps)
                if (timestamp - start_epoch_ms) % (step_seconds * _MILLISECONDS) == 0
            ]
            selected_timestamps[target] = tuple(timestamps[index] for index in indices)
            fields = {}
            for field, values in window.series[target].items():
                if field not in _PEAK_FIELDS:
                    fields[field] = tuple(values[index] for index in indices)
                    continue
                fields[field] = tuple(
                    max(
                        values[index]
                        for index, timestamp in enumerate(timestamps)
                        if bucket_start <= timestamp < bucket_start + step_seconds * _MILLISECONDS
                    )
                    for bucket_start in selected_timestamps[target]
                )
            selected_series[target] = fields
        return MetricFrame(
            metric=self.metric,
            query_target=self.query_target,
            step_seconds=step_seconds,
            series=selected_series,
            timestamps_ms=selected_timestamps,
        )


def validate_metric_frame(
    frame: MetricFrame,
    catalog: MetricCatalog,
    deployment: object | None = None,
) -> None:
    definition = catalog.definition(frame.metric)
    expected_fields = set(definition.value_fields)
    for target, fields in frame.series.items():
        if set(fields) != expected_fields:
            raise ValueError(
                f"MetricFrame fields differ from catalog: metric={frame.metric!r}, target={target!r}, "
                f"expected={definition.value_fields!r}, actual={tuple(fields)!r}"
            )
        if deployment is not None:
            catalog.validate_target(frame.metric, frame.query_target, deployment)
        for field, values in fields.items():
            if definition.lower_bound is not None and any(value < definition.lower_bound for value in values):
                raise ValueError(
                    f"MetricFrame value is below catalog bound: metric={frame.metric!r}, target={target!r}, "
                    f"field={field!r}, lower_bound={definition.lower_bound}, values={values!r}"
                )
            if definition.upper_bound is not None and any(value > definition.upper_bound for value in values):
                raise ValueError(
                    f"MetricFrame value is above catalog bound: metric={frame.metric!r}, target={target!r}, "
                    f"field={field!r}, upper_bound={definition.upper_bound}, values={values!r}"
                )


def parse_utc_timestamp(value: str, parameter: str = "timestamp") -> int:
    if not isinstance(value, str):
        raise ValueError(f"{parameter} must use UTC {METRIC_TIMESTAMP_FORMAT}, got {value!r}")
    try:
        parsed = datetime.strptime(value, METRIC_TIMESTAMP_FORMAT).replace(tzinfo=UTC)
    except ValueError as exc:
        raise ValueError(
            f"{parameter} must use UTC {METRIC_TIMESTAMP_FORMAT}, got {value!r}"
        ) from exc
    return int(parsed.timestamp() * _MILLISECONDS)


def format_utc_timestamp(epoch_ms: int) -> str:
    if not isinstance(epoch_ms, int):
        raise TypeError(f"UTC epoch must be an integer millisecond value: epoch_ms={epoch_ms!r}")
    return datetime.fromtimestamp(epoch_ms / _MILLISECONDS, tz=UTC).strftime(METRIC_TIMESTAMP_FORMAT)


class MetricProvider(Protocol):
    def query(self, query: MetricQuery) -> MetricFrame:
        ...


class MetricService:
    """Expose frozen public history and trusted live observations separately."""

    def __init__(self, *, catalog: MetricCatalog, live: MetricProvider) -> None:
        self.catalog = catalog
        self.live = live
        self.history: MetricProvider | None = None

    def _query(self, provider: MetricProvider, query: MetricQuery) -> MetricFrame:
        validate_metric_query(query, self.catalog)
        frame = provider.query(query)
        validate_metric_frame(frame, self.catalog)
        return frame

    def query_public(self, query: MetricQuery) -> MetricFrame:
        return self._query(self.history or self.live, query)

    def query_live(self, query: MetricQuery) -> MetricFrame:
        return self._query(self.live, query)

    def bind_history(self, provider: MetricProvider) -> None:
        if self.history is not None:
            raise RuntimeError("Metric history is already bound; detach/replace is not supported")
        frames = getattr(provider, "frames")
        for frame in frames:
            validate_metric_frame(frame, self.catalog)
        self.history = provider


def render_metric_frame(
    frame: MetricFrame,
    *,
    available_start_ms: int,
    available_end_ms: int,
    requested_start_ms: int,
    requested_end_ms: int,
    step_seconds: int,
    max_points: int | None = None,
) -> str:
    selected = frame if step_seconds == frame.step_seconds else frame.resample(step_seconds, requested_start_ms, requested_end_ms)
    series: dict[str, dict[str, list[Any]]] = {}
    point_count = 0
    scalar_samples = 0
    for target, timestamps in selected.timestamps_ms.items():
        if max_points is not None and max_points > 0 and len(timestamps) > max_points:
            # `limit` is a per-target response budget. Keep the newest points,
            # which are the most useful observations for diagnosis.
            start = len(timestamps) - max_points
            timestamps = timestamps[start:]
            selected_values = {
                field: values[start:]
                for field, values in selected.series[target].items()
            }
        else:
            selected_values = selected.series[target]
        points = len(timestamps)
        point_count += points
        fields = {field: list(values) for field, values in selected_values.items()}
        # Long overview frames use a fixed UTC grid. Represent that grid once
        # per series instead of repeating thousands of identical timestamp
        # strings; all sampled values remain present and explicit 2-second
        # windows retain the raw timestamp list.
        if step_seconds >= 20 and points > 512:
            timestamp_value: object = {
                "start": format_utc_timestamp(timestamps[0]),
                "end": format_utc_timestamp(timestamps[-1]),
                "step_seconds": step_seconds,
                "count": points,
            }
        else:
            timestamp_value = [format_utc_timestamp(value) for value in timestamps]
        fields = {"timestamps": timestamp_value, **fields}
        scalar_samples += points * len(selected.series[target])
        series[target] = fields
    payload = {
        "status": "success",
        "metric": selected.metric,
        "kind": "series",
        "window": {
            "available_start": format_utc_timestamp(available_start_ms),
            "available_end": format_utc_timestamp(available_end_ms),
            "requested_start": format_utc_timestamp(requested_start_ms),
            "requested_end": format_utc_timestamp(requested_end_ms),
            "step_seconds": step_seconds,
        },
        "series": series,
        "counts": {
            "series": len(series),
            "points": point_count,
            "scalar_samples": scalar_samples,
        },
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


QUERY_METRICS_RESULT_MAX_CHARS = 60_000
QUERY_METRICS_TRUNCATION_HINT = (
    "本次 query_metrics 返回超出单次字符上限，已从最早端丢弃观测点（最新观测点完整保留）；"
    "请缩小 start_timestamp/end_timestamp 查询窗口，或增大 step_seconds 降低采样密度后重新查询。"
)
QUERY_METRICS_BOUND_CONTRACT = (
    f"返回整体不超过 {QUERY_METRICS_RESULT_MAX_CHARS} 字符；超出时从最早端丢弃观测点并置 "
    "truncated=true（附 truncation.hint），请缩小 start_timestamp/end_timestamp 窗口或增大 "
    "step_seconds 后重新查询。"
)
QUERY_METRICS_TRUNCATION_HINT_EN = (
    "This query_metrics result exceeded the per-response character limit, so observation points were dropped from the "
    "oldest end (the newest observation points are kept intact); narrow the start_timestamp/end_timestamp query window, "
    "or increase step_seconds to lower the sampling density, and query again."
)
QUERY_METRICS_BOUND_CONTRACT_EN = (
    f"The whole result is at most {QUERY_METRICS_RESULT_MAX_CHARS} characters; beyond that, observation points are "
    "dropped from the oldest end and truncated=true is set (with truncation.hint); narrow the "
    "start_timestamp/end_timestamp window or increase step_seconds and query again."
)


def _series_point_count(fields: dict[str, Any]) -> int:
    timestamps = fields["timestamps"]
    if isinstance(timestamps, dict):
        return timestamps["count"]
    return len(timestamps)


def _drop_oldest_series_points(fields: dict[str, Any], drop: int) -> None:
    timestamps = fields["timestamps"]
    if isinstance(timestamps, dict):
        timestamps["start"] = format_utc_timestamp(
            parse_utc_timestamp(timestamps["start"], "start") + drop * timestamps["step_seconds"] * _MILLISECONDS
        )
        timestamps["count"] -= drop
    else:
        fields["timestamps"] = timestamps[drop:]
    for field, values in fields.items():
        if field != "timestamps":
            fields[field] = values[drop:]


def bound_metric_result(result_json: str, *, max_chars: int = QUERY_METRICS_RESULT_MAX_CHARS) -> str:
    """Agent-facing query_metrics 响应预算：超限的 series 丢弃最早观测点并标记 truncated。

    低于预算的结果原样返回；显式窗口的完整证据序列由窗口/step 合同控制，
    本函数只在窗口选择过大导致响应超出模型上下文预算时收缩。非 series
    响应（records/snapshot）自身由查询的 LIMIT 合同约束，不做处理。
    """
    if len(result_json) <= max_chars:
        return result_json
    payload = json.loads(result_json)
    if payload.get("kind") != "series":
        return result_json
    series = payload["series"]
    original_points = sum(_series_point_count(fields) for fields in series.values())
    payload["truncated"] = True
    payload["truncation"] = {
        "limit_chars": max_chars,
        "original_chars": len(result_json),
        "dropped_points": 0,
        "hint": agent_text(zh=QUERY_METRICS_TRUNCATION_HINT, en=QUERY_METRICS_TRUNCATION_HINT_EN),
    }
    while True:
        kept_points = sum(_series_point_count(fields) for fields in series.values())
        if kept_points <= len(series):
            break
        if len(json.dumps(payload, ensure_ascii=False, separators=(",", ":"))) <= max_chars:
            break
        for fields in series.values():
            target_points = _series_point_count(fields)
            if target_points <= 1:
                continue
            _drop_oldest_series_points(fields, target_points - max(1, target_points * 3 // 4))
        payload["truncation"]["dropped_points"] = original_points - sum(
            _series_point_count(fields) for fields in series.values()
        )
    payload["counts"]["points"] = sum(_series_point_count(fields) for fields in series.values())
    payload["counts"]["scalar_samples"] = sum(
        _series_point_count(fields) * (len(fields) - 1) for fields in series.values()
    )
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
