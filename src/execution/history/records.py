"""Database-independent historical records, coverage, and bounded queries."""

from __future__ import annotations

import json
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from src.execution.history.metrics import format_utc_timestamp


class HistoricalRecordSource(str, Enum):
    COMPONENT_LOG = "component_log"
    OPERATION_EVENT = "operation_event"
    TOPSQL = "topsql"
    SLOW_QUERIES = "slow_queries"


@dataclass(frozen=True, slots=True, kw_only=True)
class HistoricalPointRecord:
    source: HistoricalRecordSource
    target: str
    timestamp_ms: int
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        if not self.target:
            raise ValueError(f"Historical point target must be non-empty: record={self!r}")
        if not isinstance(self.timestamp_ms, int) or isinstance(self.timestamp_ms, bool) or self.timestamp_ms < 0:
            raise ValueError(f"Historical point timestamp must be a non-negative integer: record={self!r}")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


@dataclass(frozen=True, slots=True, kw_only=True)
class HistoricalIntervalRecord:
    source: HistoricalRecordSource
    target: str
    start_ms: int
    end_ms: int
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        if not self.target:
            raise ValueError(f"Historical interval target must be non-empty: record={self!r}")
        if (
            not isinstance(self.start_ms, int)
            or isinstance(self.start_ms, bool)
            or not isinstance(self.end_ms, int)
            or isinstance(self.end_ms, bool)
            or self.start_ms < 0
            or self.start_ms >= self.end_ms
        ):
            raise ValueError(f"Historical interval must have a positive integer range: record={self!r}")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


@dataclass(frozen=True, slots=True, kw_only=True)
class HistoricalCoverage:
    source: HistoricalRecordSource
    target: str | None
    start_ms: int
    end_ms: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.start_ms, int)
            or isinstance(self.start_ms, bool)
            or not isinstance(self.end_ms, int)
            or isinstance(self.end_ms, bool)
            or self.start_ms < 0
            or self.start_ms >= self.end_ms
        ):
            raise ValueError(f"Historical coverage must have a positive integer range: coverage={self!r}")


@dataclass(frozen=True, slots=True, kw_only=True)
class CapturedRecords:
    point_records: tuple[HistoricalPointRecord, ...] = ()
    interval_records: tuple[HistoricalIntervalRecord, ...] = ()
    coverage: tuple[HistoricalCoverage, ...] = ()

    def __post_init__(self) -> None:
        points = tuple(sorted(self.point_records, key=lambda record: (record.source.value, record.target, record.timestamp_ms)))
        intervals = tuple(sorted(self.interval_records, key=lambda record: (record.source.value, record.target, record.start_ms, record.end_ms)))
        coverage = tuple(sorted(self.coverage, key=lambda item: (item.source.value, item.target or "", item.start_ms, item.end_ms)))
        object.__setattr__(self, "point_records", points)
        object.__setattr__(self, "interval_records", intervals)
        object.__setattr__(self, "coverage", coverage)

    def shift(self, delta_ms: int) -> "CapturedRecords":
        return CapturedRecords(
            point_records=tuple(
                HistoricalPointRecord(
                    source=record.source,
                    target=record.target,
                    timestamp_ms=record.timestamp_ms + delta_ms,
                    payload=record.payload,
                )
                for record in self.point_records
            ),
            interval_records=tuple(
                HistoricalIntervalRecord(
                    source=record.source,
                    target=record.target,
                    start_ms=record.start_ms + delta_ms,
                    end_ms=record.end_ms + delta_ms,
                    payload=record.payload,
                )
                for record in self.interval_records
            ),
            coverage=tuple(
                HistoricalCoverage(
                    source=item.source,
                    target=item.target,
                    start_ms=item.start_ms + delta_ms,
                    end_ms=item.end_ms + delta_ms,
                )
                for item in self.coverage
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class FrozenHistoricalRecordStore:
    point_records: Mapping[tuple[str, str], tuple[HistoricalPointRecord, ...]]
    interval_records: Mapping[tuple[str, str], tuple[HistoricalIntervalRecord, ...]]
    coverage: tuple[HistoricalCoverage, ...]

    def __post_init__(self) -> None:
        normalized_points: dict[tuple[str, str], tuple[HistoricalPointRecord, ...]] = {}
        for raw_key, records in self.point_records.items():
            key = (str(raw_key[0]), str(raw_key[1]))
            sorted_records = tuple(sorted(records, key=lambda item: item.timestamp_ms))
            if any(record.source.value != key[0] or record.target != key[1] for record in sorted_records):
                raise ValueError(f"Point record key does not match records: key={key!r}, records={sorted_records!r}")
            normalized_points[key] = sorted_records
        normalized_intervals: dict[tuple[str, str], tuple[HistoricalIntervalRecord, ...]] = {}
        for raw_key, records in self.interval_records.items():
            key = (str(raw_key[0]), str(raw_key[1]))
            sorted_records = tuple(sorted(records, key=lambda item: (item.start_ms, item.end_ms)))
            if any(record.source.value != key[0] or record.target != key[1] for record in sorted_records):
                raise ValueError(f"Interval record key does not match records: key={key!r}, records={sorted_records!r}")
            normalized_intervals[key] = sorted_records
        object.__setattr__(self, "point_records", MappingProxyType(normalized_points))
        object.__setattr__(self, "interval_records", MappingProxyType(normalized_intervals))
        object.__setattr__(self, "coverage", tuple(sorted(
            self.coverage,
            key=lambda item: (item.source.value, item.target or "", item.start_ms, item.end_ms),
        )))

    @classmethod
    def from_captured(cls, captured: CapturedRecords) -> "FrozenHistoricalRecordStore":
        points: dict[tuple[str, str], list[HistoricalPointRecord]] = {}
        for record in captured.point_records:
            points.setdefault((record.source.value, record.target), []).append(record)
        intervals: dict[tuple[str, str], list[HistoricalIntervalRecord]] = {}
        for record in captured.interval_records:
            intervals.setdefault((record.source.value, record.target), []).append(record)
        return cls(
            point_records={key: tuple(records) for key, records in points.items()},
            interval_records={key: tuple(records) for key, records in intervals.items()},
            coverage=captured.coverage,
        )

    def _coverage_complete(self, source: HistoricalRecordSource, target: str | None, start_ms: int, end_ms: int) -> bool:
        candidates = [
            item
            for item in self.coverage
            if item.source is source and item.start_ms <= start_ms and item.end_ms >= end_ms
        ]
        if target is not None:
            return any(item.target is None or item.target == target for item in candidates)
        if any(item.target is None for item in candidates):
            return True
        targets = {item.target for item in self.coverage if item.source is source}
        return bool(targets) and all(
            any(item.target == covered_target for item in candidates)
            for covered_target in targets
        )

    def find_matching_evidence(
        self,
        *,
        source: HistoricalRecordSource,
        target: str,
        payload: Mapping[str, object],
        point_timestamp_ms: int | None = None,
        interval_start_ms: int | None = None,
        interval_end_ms: int | None = None,
    ) -> tuple[HistoricalPointRecord | HistoricalIntervalRecord, ...]:
        """Return frozen records with the requested identity and raw payload."""
        has_point = point_timestamp_ms is not None
        has_interval = interval_start_ms is not None or interval_end_ms is not None
        if has_point == has_interval or (has_interval and interval_end_ms is None):
            raise ValueError(
                "Historical evidence matching requires exactly one point or interval selector: "
                f"point_timestamp_ms={point_timestamp_ms!r}, interval_start_ms={interval_start_ms!r}, "
                f"interval_end_ms={interval_end_ms!r}"
            )
        candidates = tuple(
            record
            for key, records in self.point_records.items()
            if key == (source.value, target)
            for record in records
        ) + tuple(
            record
            for key, records in self.interval_records.items()
            if key == (source.value, target)
            for record in records
        )
        if has_point:
            selected = tuple(
                record
                for record in candidates
                if isinstance(record, HistoricalPointRecord)
                and record.timestamp_ms == point_timestamp_ms
            )
        else:
            if interval_start_ms >= interval_end_ms:
                raise ValueError(
                    "Historical evidence interval must be positive: "
                    f"interval_start_ms={interval_start_ms}, interval_end_ms={interval_end_ms}"
                )
            selected = tuple(
                record
                for record in candidates
                if isinstance(record, HistoricalIntervalRecord)
                and record.start_ms == interval_start_ms
                and record.end_ms == interval_end_ms
            )
        return tuple(
            record
            for record in selected
            if all(record.payload.get(key) == value for key, value in payload.items())
        )

    def query(
        self,
        *,
        source: HistoricalRecordSource,
        start_ms: int,
        end_ms: int,
        target: str | None,
        filters: Mapping[str, object] | None,
        limit: int,
        max_window_seconds: int | None = None,
        max_response_chars: int | None = None,
    ) -> dict[str, object]:
        if start_ms >= end_ms:
            raise ValueError(f"Historical query window must be positive: start_ms={start_ms}, end_ms={end_ms}")
        if max_window_seconds is not None and end_ms - start_ms > max_window_seconds * 1000:
            raise ValueError(
                f"Historical query window exceeds budget: window_seconds={(end_ms - start_ms) / 1000:g}, "
                f"max_window_seconds={max_window_seconds}"
            )
        if limit <= 0:
            raise ValueError(f"Historical query limit must be positive: source={source.value!r}, limit={limit}")
        selected_filters = dict(filters or {})
        allowed_filters = {
            HistoricalRecordSource.COMPONENT_LOG: {"level", "component", "contains"},
            HistoricalRecordSource.OPERATION_EVENT: {
                "event_type", "operation", "entity_type", "entity", "action", "status",
                "correlation_id", "actor", "contains", "order_by",
            },
            HistoricalRecordSource.TOPSQL: {"resource_group", "digest", "sql_contains", "min_exec_count", "order_by"},
            HistoricalRecordSource.SLOW_QUERIES: {"digest", "sql_contains", "min_query_time_ms", "order_by"},
        }[source]
        unknown = sorted(set(selected_filters) - allowed_filters)
        if unknown:
            raise ValueError(f"Unknown historical query filter: source={source.value!r}, filters={unknown!r}")
        if "order_by" in selected_filters:
            order_by = str(selected_filters["order_by"])
            allowed_order = {
                HistoricalRecordSource.TOPSQL: {"sum_latency", "avg_latency", "exec_count"},
                HistoricalRecordSource.SLOW_QUERIES: {"query_time", "process_time", "wait_time"},
                HistoricalRecordSource.COMPONENT_LOG: set(),
                HistoricalRecordSource.OPERATION_EVENT: {
                    "duration_ms", "bytes", "requests_per_sec", "waiter_ms_per_sec",
                },
            }[source]
            if order_by not in allowed_order:
                raise ValueError(
                    f"Unknown historical order_by: source={source.value!r}, order_by={order_by!r}, "
                    f"allowed={sorted(allowed_order)!r}"
                )
        if not self._coverage_complete(source, target, start_ms, end_ms):
            coverage_ends = [
                item.end_ms
                for item in self.coverage
                if item.source is source
                and (target is None or item.target == target)
            ]
            latest_covered = max(coverage_ends, default=None)
            if latest_covered is not None and 0 < end_ms - latest_covered <= 60_000:
                end_ms = latest_covered
        if not self._coverage_complete(source, target, start_ms, end_ms):
            raise ValueError(
                f"Historical source has no complete coverage: source={source.value!r}, target={target!r}, "
                f"start_ms={start_ms}, end_ms={end_ms}"
            )
        records: list[HistoricalPointRecord | HistoricalIntervalRecord] = []
        keys = sorted(
            key
            for key in set(self.point_records) | set(self.interval_records)
            if key[0] == source.value and (target is None or key[1] == target)
        )
        for key in keys:
            point_records = self.point_records.get(key, ())
            interval_records = self.interval_records.get(key, ())
            timestamps = [record.timestamp_ms for record in point_records]
            records.extend(point_records[bisect_left(timestamps, start_ms):bisect_right(timestamps, end_ms)])
            records.extend(
                record
                for record in interval_records
                if record.end_ms >= start_ms and record.start_ms <= end_ms
            )
        scanned_records = len(records)
        matched = [record for record in records if _record_matches(record, selected_filters)]
        if "order_by" in selected_filters:
            matched.sort(key=lambda record: _order_value(record, str(selected_filters["order_by"])), reverse=True)
        else:
            matched.sort(key=_record_sort_key)
        returned = matched[:limit]
        if max_response_chars is not None and max_response_chars <= 0:
            raise ValueError(f"Historical response character budget must be positive: max_response_chars={max_response_chars}")
        truncated_by_size = False
        if max_response_chars is not None:
            while returned and len(json.dumps({
                "status": "success", "source": source.value,
                "window": {"start_timestamp": format_utc_timestamp(start_ms), "end_timestamp": format_utc_timestamp(end_ms)},
                "coverage": "complete", "scanned_records": scanned_records, "scanned": scanned_records,
                "matched_records": len(matched), "matched": len(matched), "returned_records": len(returned),
                "truncated": True, "records": [_record_payload(record) for record in returned],
            }, ensure_ascii=False, separators=(",", ":"), default=str)) > max_response_chars:
                returned = returned[:-1]
                truncated_by_size = True
        result = {
            "status": "success",
            "source": source.value,
            "window": {
                "start_timestamp": format_utc_timestamp(start_ms),
                "end_timestamp": format_utc_timestamp(end_ms),
            },
            "coverage": "complete",
            "scanned_records": scanned_records,
            "scanned": scanned_records,
            "matched_records": len(matched),
            "matched": len(matched),
            "returned_records": len(returned),
            "truncated": truncated_by_size or len(matched) > limit,
            "truncation_reason": "response_chars" if truncated_by_size else ("record_limit" if len(matched) > limit else None),
            "response_budget_chars": max_response_chars,
            "records": [_record_payload(record) for record in returned],
        }
        if returned and truncated_by_size:
            result["returned_window"] = {
                "start_timestamp": format_utc_timestamp(returned[0].timestamp_ms if isinstance(returned[0], HistoricalPointRecord) else returned[0].start_ms),
                "end_timestamp": format_utc_timestamp(returned[-1].timestamp_ms if isinstance(returned[-1], HistoricalPointRecord) else returned[-1].end_ms),
            }
        result["response_chars"] = 0
        for _ in range(3):
            result["response_chars"] = len(json.dumps(result, ensure_ascii=False, separators=(",", ":"), default=str))
        return result


def _record_sort_key(record: HistoricalPointRecord | HistoricalIntervalRecord) -> tuple[int, int, str]:
    if isinstance(record, HistoricalPointRecord):
        return record.timestamp_ms, record.timestamp_ms, record.target
    return record.start_ms, record.end_ms, record.target


def _payload_text(payload: Mapping[str, object]) -> str:
    return json.dumps(dict(payload), ensure_ascii=False, default=str).casefold()


def _record_matches(record: HistoricalPointRecord | HistoricalIntervalRecord, filters: Mapping[str, object]) -> bool:
    payload = record.payload
    if "level" in filters and str(payload.get("level", "")).casefold() != str(filters["level"]).casefold():
        return False
    if "component" in filters and str(payload.get("component", "")).casefold() != str(filters["component"]).casefold():
        return False
    for field in ("event_type", "operation", "entity_type", "entity", "action", "status", "correlation_id", "actor"):
        if field in filters and str(payload.get(field, "")).casefold() != str(filters[field]).casefold():
            return False
    if "contains" in filters and str(filters["contains"]).casefold() not in (
        _payload_text(payload) if record.source is HistoricalRecordSource.OPERATION_EVENT
        else str(payload.get("message", ""))
    ).casefold():
        return False
    if "digest" in filters and str(payload.get("digest", "")) != str(filters["digest"]):
        return False
    if "resource_group" in filters and str(payload.get("resource_group", "")).casefold() != str(filters["resource_group"]).casefold():
        return False
    if "sql_contains" in filters and str(filters["sql_contains"]).casefold() not in str(payload.get("sql_text", "")).casefold():
        return False
    if "min_exec_count" in filters and float(payload.get("exec_count", 0)) < float(filters["min_exec_count"]):
        return False
    if "min_query_time_ms" in filters and float(payload.get("query_time_ms", payload.get("query_time", 0))) < float(filters["min_query_time_ms"]):
        return False
    return True


def _order_value(record: HistoricalPointRecord | HistoricalIntervalRecord, order_by: str) -> float:
    payload = record.payload
    field = {
        "sum_latency": "sum_latency",
        "avg_latency": "avg_latency",
        "exec_count": "exec_count",
        "query_time": "query_time_ms",
        "process_time": "process_time_ms",
        "wait_time": "wait_time_ms",
        "duration_ms": "duration_ms",
        "bytes": "bytes",
        "requests_per_sec": "requests_per_sec",
        "waiter_ms_per_sec": "waiter_ms_per_sec",
    }[order_by]
    return float(payload.get(field, payload.get(field.removesuffix("_ms"), 0)))


def _record_payload(record: HistoricalPointRecord | HistoricalIntervalRecord) -> dict[str, object]:
    if isinstance(record, HistoricalPointRecord):
        return {"target": record.target, "timestamp": format_utc_timestamp(record.timestamp_ms), **dict(record.payload)}
    return {
        "target": record.target,
        "start_timestamp": format_utc_timestamp(record.start_ms),
        "end_timestamp": format_utc_timestamp(record.end_ms),
        **dict(record.payload),
    }


def source_is_operation_event(record: HistoricalPointRecord | HistoricalIntervalRecord) -> bool:
    return record.source is HistoricalRecordSource.OPERATION_EVENT
