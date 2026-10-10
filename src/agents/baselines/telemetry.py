"""Shared metric response parsing and timestamp alignment for baselines."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True, slots=True, kw_only=True)
class ParsedMetricSeries:
    metric: str
    query_target: str | None
    series_target: str
    field: str
    timestamps_ms: tuple[int, ...]
    values: tuple[float, ...]
    step_seconds: int


def metric_names_from_tools(tools: list[Mapping[str, Any]]) -> tuple[str, ...]:
    """Discover the metric catalog exposed by the concrete environment tools."""
    names: set[str] = set()
    marker = "调用定义(JSON):"
    for tool in tools:
        function = tool.get("function", tool)
        if not isinstance(function, Mapping):
            continue
        description = str(function.get("description", ""))
        if marker in description:
            encoded = description.split(marker, 1)[1].lstrip()
            definition, _ = json.JSONDecoder().raw_decode(encoded)
            names.update(
                str(metric["name"])
                for metric in definition.get("capabilities", {}).get("metrics", [])
            )
        properties = function.get("parameters", {}).get("properties", {})
        metric_type = properties.get("metric_type", {}) if isinstance(properties, Mapping) else {}
        names.update(str(metric) for metric in metric_type.get("enum", []))
    if not names:
        raise ValueError(f"query_metrics tool definitions expose no metric names: tool_count={len(tools)}")
    return tuple(sorted(names))


def is_tidb_history_tool_surface(tools: list[Mapping[str, Any]]) -> bool:
    """Identify TiDB only from the system-specific management capability."""
    names = {
        str((tool.get("function", tool) or {}).get("name", ""))
        for tool in tools
        if isinstance(tool, Mapping)
    }
    has_cluster_management = "manage_cluster" in names
    has_instance_management = "manage_instance" in names
    if has_cluster_management and has_instance_management:
        raise ValueError(
            "History tool surface has conflicting database management capabilities: "
            f"tools={sorted(names)!r}"
        )
    if has_cluster_management:
        return True
    if has_instance_management:
        return False
    raise ValueError(
        "History tool surface lacks a database-specific management capability: "
        f"tools={sorted(names)!r}"
    )


def parse_metric_response(
    raw_result: str | Mapping[str, Any],
    *,
    metric: str | None = None,
    query_target: str | None = None,
    default_step_seconds: int | None = None,
) -> tuple[ParsedMetricSeries, ...]:
    data = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
    if not isinstance(data, Mapping):
        raise ValueError(f"Metric response must be an object: metric={metric!r}, response_type={type(data).__name__}")
    if data.get("status") == "error":
        raise ValueError(f"Metric response is an error: metric={metric or data.get('metric')!r}, error={data.get('error')!r}")
    if data.get("kind") != "series" or not isinstance(data.get("series"), Mapping):
        raise ValueError(f"Metric response lacks canonical series shape: metric={metric or data.get('metric')!r}, response={data!r}")
    response_metric = str(metric or data.get("metric") or "")
    if not response_metric:
        raise ValueError(f"Metric response does not identify a metric: response={data!r}")
    parsed: list[ParsedMetricSeries] = []
    for series_target, raw_series in data["series"].items():
        if not isinstance(raw_series, Mapping):
            raise ValueError(f"Metric series must be an object: metric={response_metric!r}, target={series_target!r}")
        if "timestamps" not in raw_series:
            raise ValueError(f"Metric series lacks timestamps: metric={response_metric!r}, target={series_target!r}")
        timestamps = tuple(_timestamp_ms(value, response_metric, str(series_target)) for value in raw_series["timestamps"])
        if any(current <= previous for previous, current in zip(timestamps, timestamps[1:])):
            raise ValueError(f"Metric timestamps are not strictly increasing: metric={response_metric!r}, target={series_target!r}, timestamps={timestamps!r}")
        step_seconds = _infer_step_seconds(timestamps, default_step_seconds, response_metric, str(series_target))
        fields = [field for field in raw_series if field != "timestamps"]
        if not fields:
            raise ValueError(f"Metric series has no value fields: metric={response_metric!r}, target={series_target!r}")
        for field in fields:
            raw_values = raw_series[field]
            if len(raw_values) != len(timestamps):
                raise ValueError(f"Metric field is not timestamp-aligned: metric={response_metric!r}, target={series_target!r}, field={field!r}, timestamps={len(timestamps)}, values={len(raw_values)}")
            values = tuple(float(value) for value in raw_values)
            if any(not math.isfinite(value) for value in values):
                raise ValueError(f"Metric field contains non-finite values: metric={response_metric!r}, target={series_target!r}, field={field!r}")
            parsed.append(ParsedMetricSeries(
                metric=response_metric,
                query_target=query_target,
                series_target=str(series_target),
                field=str(field),
                timestamps_ms=timestamps,
                values=values,
                step_seconds=step_seconds,
            ))
    if not parsed:
        raise ValueError(f"Metric response contains no series fields: metric={response_metric!r}")
    return tuple(parsed)


def align_series(left: ParsedMetricSeries, right: ParsedMetricSeries) -> tuple[tuple[int, float, float], ...]:
    if left.metric == right.metric and left.series_target == right.series_target and left.field == right.field:
        raise ValueError(f"Cannot correlate a series with itself: series={left!r}")
    right_values = dict(zip(right.timestamps_ms, right.values, strict=True))
    aligned = tuple(
        (timestamp, value, right_values[timestamp])
        for timestamp, value in zip(left.timestamps_ms, left.values, strict=True)
        if timestamp in right_values
    )
    if not aligned:
        raise ValueError(
            "Metric series have no common timestamps: "
            f"left=({left.metric!r},{left.series_target!r},{left.field!r}), "
            f"right=({right.metric!r},{right.series_target!r},{right.field!r})"
        )
    return aligned


def candidate_window(
    series: ParsedMetricSeries,
    *,
    timestamp_ms: int,
    radius_seconds: int,
    visible_start_ms: int | None = None,
    visible_end_ms: int | None = None,
) -> tuple[int, int]:
    if radius_seconds <= 0:
        raise ValueError(f"Candidate window radius must be positive: radius_seconds={radius_seconds}")
    start_ms = timestamp_ms - radius_seconds * 1000
    end_ms = timestamp_ms + radius_seconds * 1000
    if visible_start_ms is not None:
        start_ms = max(start_ms, visible_start_ms)
    if visible_end_ms is not None:
        end_ms = min(end_ms, visible_end_ms)
    if start_ms >= end_ms:
        raise ValueError(f"Candidate window is empty after visible-range clipping: start_ms={start_ms}, end_ms={end_ms}, series={series!r}")
    return start_ms, end_ms


def stl_period_samples(period_seconds: int, step_seconds: int) -> int:
    if period_seconds <= 0 or step_seconds <= 0:
        raise ValueError(f"STL period and metric step must be positive: period_seconds={period_seconds}, step_seconds={step_seconds}")
    if period_seconds % step_seconds:
        raise ValueError(f"STL period must be divisible by metric step: period_seconds={period_seconds}, step_seconds={step_seconds}")
    period_samples = period_seconds // step_seconds
    if period_samples < 2:
        raise ValueError(f"STL period must contain at least two samples: period_seconds={period_seconds}, step_seconds={step_seconds}")
    return period_samples


def _infer_step_seconds(timestamps_ms: tuple[int, ...], default: int | None, metric: str, target: str) -> int:
    if len(timestamps_ms) < 2:
        if default is None or default <= 0:
            raise ValueError(f"Cannot infer metric step from one sample: metric={metric!r}, target={target!r}, default_step_seconds={default!r}")
        return default
    diffs = tuple(current - previous for previous, current in zip(timestamps_ms, timestamps_ms[1:]))
    if any(diff != diffs[0] for diff in diffs):
        raise ValueError(f"Metric timestamps have inconsistent steps: metric={metric!r}, target={target!r}, diffs_ms={diffs!r}")
    if diffs[0] % 1000:
        raise ValueError(f"Metric timestamp step is not a whole second: metric={metric!r}, target={target!r}, diff_ms={diffs[0]}")
    return diffs[0] // 1000


def _timestamp_ms(value: object, metric: str, target: str) -> int:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"Metric timestamp is non-finite: metric={metric!r}, target={target!r}, value={value!r}")
        return int(number * (1000 if number < 100_000_000_000 else 1))
    if not isinstance(value, str):
        raise ValueError(f"Metric timestamp must be an epoch or string: metric={metric!r}, target={target!r}, value={value!r}")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)
