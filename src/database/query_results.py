"""Business query truth and latency statistics."""

import json
import time
from collections.abc import Callable
from hashlib import sha256

from src.database.sql import parse_json_object, require_success_payload


RESULT_TRUTH_SAMPLE_SIZE = 50


def capture_query_result_truth(
    payload: object,
    *,
    ordered: bool,
    sample_size: int = RESULT_TRUTH_SAMPLE_SIZE,
) -> dict[str, object]:
    columns, rows = _result_columns_and_rows(
        parse_json_object(payload, "capture query result truth")
    )
    canonical_rows = _canonical_rows(rows, ordered=ordered)
    truth = {
        "columns": columns,
        "row_count": len(canonical_rows),
        "ordered": ordered,
    }
    if len(canonical_rows) <= sample_size:
        truth["rows"] = canonical_rows
        return truth
    positions = _sample_positions(len(canonical_rows), sample_size)
    truth.update({
        "sample_positions": positions,
        "sample_rows": [canonical_rows[position] for position in positions],
        "digest": _result_digest(columns, canonical_rows),
    })
    return truth


def query_result_truth_row_count(truth: dict) -> int:
    _validate_result_truth(truth)
    return truth["row_count"]


def query_result_truth_mismatch(
    truth: dict,
    columns: object,
    rows: object,
) -> str | None:
    expected_columns, expected_row_count, ordered = _validate_result_truth(truth)
    if not isinstance(rows, list):
        raise TypeError(f"candidate query result rows must be a list: rows={rows!r}")
    if len(rows) != expected_row_count:
        return "result row count differs from the captured business result"
    if columns != expected_columns:
        return "result columns differ from the captured business result"
    candidate_rows = _canonical_rows(rows, ordered=ordered)
    if "rows" in truth:
        if candidate_rows != truth["rows"]:
            return "result values or row order differ from the captured business result"
        return None
    positions = truth["sample_positions"]
    if [candidate_rows[position] for position in positions] != truth["sample_rows"]:
        return "result sampled values or row order differ from the captured business result"
    if _result_digest(expected_columns, candidate_rows) != truth["digest"]:
        return "result digest differs from the captured business result"
    return None


def _result_columns_and_rows(payload: dict) -> tuple[list[str], list]:
    columns = payload.get("columns")
    rows = payload.get("result")
    if not isinstance(columns, list) or not all(isinstance(column, str) for column in columns):
        raise ValueError(f"query result must include string column labels: payload={payload!r}")
    if not isinstance(rows, list):
        raise TypeError(f"query result rows must be a list: payload={payload!r}")
    _validate_rows(rows, columns)
    return columns, rows


def _validate_result_truth(truth: dict) -> tuple[list[str], int, bool]:
    if not isinstance(truth, dict):
        raise TypeError(f"query result truth must be a mapping: truth={truth!r}")
    columns = truth.get("columns")
    row_count = truth.get("row_count")
    ordered = truth.get("ordered")
    if not isinstance(columns, list) or not all(isinstance(column, str) for column in columns):
        raise ValueError(f"query result truth columns must be string labels: truth={truth!r}")
    if not isinstance(row_count, int) or row_count < 0:
        raise ValueError(f"query result truth row_count must be non-negative: truth={truth!r}")
    if not isinstance(ordered, bool):
        raise ValueError(f"query result truth ordered flag must be boolean: truth={truth!r}")
    if "rows" in truth:
        rows = truth["rows"]
        if not isinstance(rows, list) or len(rows) != row_count:
            raise ValueError(f"query result truth rows do not match row_count: truth={truth!r}")
        _validate_rows(rows, columns)
    else:
        positions = truth.get("sample_positions")
        sample_rows = truth.get("sample_rows")
        digest = truth.get("digest")
        if (
            not isinstance(positions, list)
            or not isinstance(sample_rows, list)
            or len(positions) != len(sample_rows)
            or not isinstance(digest, str)
        ):
            raise ValueError(f"sampled query result truth is incomplete: truth={truth!r}")
        if any(not isinstance(position, int) or position < 0 or position >= row_count for position in positions):
            raise ValueError(f"sampled query result truth has invalid positions: truth={truth!r}")
        _validate_rows(sample_rows, columns)
    return columns, row_count, ordered


def _validate_rows(rows: list, columns: list[str]) -> None:
    if not all(isinstance(row, (list, tuple)) and len(row) == len(columns) for row in rows):
        raise ValueError(f"query result rows do not match columns: columns={columns!r}, rows={rows!r}")


def _canonical_rows(rows: list, *, ordered: bool) -> list[list]:
    canonical_rows = [list(row) for row in rows]
    return canonical_rows if ordered else sorted(canonical_rows, key=_canonical_json)


def _sample_positions(row_count: int, sample_size: int) -> list[int]:
    if sample_size < 2:
        raise ValueError(f"sample_size must be at least two: sample_size={sample_size}")
    if row_count <= sample_size:
        return list(range(row_count))
    return [index * (row_count - 1) // (sample_size - 1) for index in range(sample_size)]


def _result_digest(columns: list[str], rows: list[list]) -> str:
    digest = sha256()
    digest.update(_canonical_json(columns))
    for row in rows:
        digest.update(_canonical_json(row))
    return digest.hexdigest()


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")

import math


def nearest_rank_percentile(samples: list[float], percentile: float) -> float:
    if not samples:
        raise ValueError("percentile requires at least one sample")
    if not 0 < percentile <= 1:
        raise ValueError(f"percentile must be in (0, 1]: percentile={percentile!r}")
    ordered = sorted(samples)
    return ordered[math.ceil(len(ordered) * percentile) - 1]


def latency_summary(samples: list[float]) -> dict[str, float]:
    if not samples:
        raise ValueError("latency summary requires at least one sample")
    return {
        "min_ms": min(samples),
        "p50_ms": nearest_rank_percentile(samples, 0.50),
        "p90_ms": nearest_rank_percentile(samples, 0.90),
        "p95_ms": nearest_rank_percentile(samples, 0.95),
        "max_ms": max(samples),
    }


def measure_latency_profile(
    execute_sql: Callable[[str], object],
    sql: str,
    *,
    warmup_samples: int,
    measured_samples: int,
    context: str,
) -> dict[str, object]:
    def timed_query_ms() -> float:
        started = time.perf_counter()
        require_success_payload(execute_sql(sql), context)
        return (time.perf_counter() - started) * 1000

    warmup = [timed_query_ms() for _ in range(warmup_samples)]
    samples = [timed_query_ms() for _ in range(measured_samples)]
    return {
        "warmup_samples_ms": tuple(warmup),
        "samples_ms": tuple(samples),
        **latency_summary(samples),
    }
