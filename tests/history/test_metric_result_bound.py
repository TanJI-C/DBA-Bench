import json

from src.execution.history.metrics import (
    QUERY_METRICS_BOUND_CONTRACT,
    QUERY_METRICS_RESULT_MAX_CHARS,
    QUERY_METRICS_TRUNCATION_HINT,
    MetricFrame,
    bound_metric_result,
    format_utc_timestamp,
    parse_utc_timestamp,
    render_metric_frame,
)
from src.execution.postgres_metrics import (
    POSTGRES_METRIC_CATALOG,
    POSTGRES_QUERY_METRICS_TOOL_DEFINITION,
    postgres_query_metrics_tool_definition,
)
from src.execution.tidb_tool_definitions import TIDB_TOOL_DEFINITIONS


BASE_MS = 1_700_000_000_000
BOUND_CHARS = 5_000


def _series_frame(values, *, step_seconds=2):
    timestamps = tuple(BASE_MS + index * step_seconds * 1_000 for index in range(len(values)))
    return MetricFrame(
        metric="qps",
        query_target=None,
        step_seconds=step_seconds,
        series={"postgres": {"queries_per_second": tuple(float(value) for value in values)}},
        timestamps_ms={"postgres": timestamps},
    )


def _render_explicit_window(points):
    frame = _series_frame(range(points))
    return render_metric_frame(
        frame,
        available_start_ms=BASE_MS,
        available_end_ms=BASE_MS + (points - 1) * 2_000,
        requested_start_ms=BASE_MS,
        requested_end_ms=BASE_MS + (points - 1) * 2_000,
        step_seconds=2,
    )


def test_bound_metric_result_returns_small_payloads_unchanged():
    rendered = _render_explicit_window(100)
    assert bound_metric_result(rendered) is rendered


def test_bound_metric_result_keeps_newest_points_within_budget():
    rendered = _render_explicit_window(20_000)
    original = json.loads(rendered)
    bounded_json = bound_metric_result(rendered, max_chars=BOUND_CHARS)
    assert len(bounded_json) <= BOUND_CHARS
    bounded = json.loads(bounded_json)
    assert bounded["status"] == "success"
    assert bounded["truncated"] is True
    truncation = bounded["truncation"]
    assert truncation["limit_chars"] == BOUND_CHARS
    assert truncation["original_chars"] == len(rendered)
    assert truncation["dropped_points"] == original["counts"]["points"] - bounded["counts"]["points"]
    assert truncation["hint"] == QUERY_METRICS_TRUNCATION_HINT
    for target, fields in bounded["series"].items():
        original_fields = original["series"][target]
        assert fields["timestamps"][-1] == original_fields["timestamps"][-1]
        assert fields["queries_per_second"][-1] == original_fields["queries_per_second"][-1]
        assert len(fields["timestamps"]) == len(fields["queries_per_second"])
    assert bounded["counts"]["points"] == sum(len(fields["timestamps"]) for fields in bounded["series"].values())
    assert bounded["counts"]["scalar_samples"] == bounded["counts"]["points"]


def test_bound_metric_result_advances_compact_grid_start_when_dropping_oldest_points():
    frame = _series_frame(range(60_000))
    rendered = render_metric_frame(
        frame,
        available_start_ms=BASE_MS,
        available_end_ms=BASE_MS + 119_998_000,
        requested_start_ms=BASE_MS,
        requested_end_ms=BASE_MS + 119_998_000,
        step_seconds=20,
    )
    original = json.loads(rendered)
    bounded = json.loads(bound_metric_result(rendered, max_chars=BOUND_CHARS))
    original_timestamps = original["series"]["postgres"]["timestamps"]
    timestamps = bounded["series"]["postgres"]["timestamps"]
    assert timestamps["step_seconds"] == 20
    assert timestamps["end"] == original_timestamps["end"]
    dropped = original_timestamps["count"] - timestamps["count"]
    assert dropped > 0
    assert timestamps["start"] == format_utc_timestamp(
        parse_utc_timestamp(original_timestamps["start"]) + dropped * 20_000
    )
    values = bounded["series"]["postgres"]["queries_per_second"]
    assert len(values) == timestamps["count"]
    assert values[-1] == original["series"]["postgres"]["queries_per_second"][-1]
    assert bounded["counts"]["points"] == timestamps["count"]
    assert bounded["truncation"]["dropped_points"] == dropped


def test_bound_metric_result_leaves_non_series_payloads_untouched():
    payload = json.dumps({
        "status": "success",
        "metric": "slow_queries",
        "kind": "records",
        "records": ["x" * 10_000],
    }, ensure_ascii=False)
    assert bound_metric_result(payload, max_chars=BOUND_CHARS) == payload


def test_query_metrics_definitions_document_the_bound_contract():
    assert QUERY_METRICS_BOUND_CONTRACT in POSTGRES_QUERY_METRICS_TOOL_DEFINITION["result_description"]
    public_definition = postgres_query_metrics_tool_definition(POSTGRES_METRIC_CATALOG)
    assert QUERY_METRICS_BOUND_CONTRACT in public_definition["result_description"]
    assert QUERY_METRICS_BOUND_CONTRACT in TIDB_TOOL_DEFINITIONS["query_metrics"]["result_description"]
    assert str(QUERY_METRICS_RESULT_MAX_CHARS) in QUERY_METRICS_BOUND_CONTRACT
