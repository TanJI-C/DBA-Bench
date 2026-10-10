import json
from types import SimpleNamespace

import pytest

from src.execution.history.metrics import MetricFrame, validate_metric_frame
from src.execution.metric_catalog import metric_catalog_for_system
from src.execution.postgres_metrics import POSTGRES_METRIC_CATALOG, POSTGRES_QUERY_METRICS_TOOL_DEFINITION
from src.scenarios.base import DatabaseSystem


def test_postgres_catalog_declares_all_series_and_bounds():
    expected = {
        "cpu": (("percent",), 0.0, 100.0),
        "memory": (("percent",), 0.0, 100.0),
        "disk_io": (("read_mb_per_second", "write_mb_per_second"), 0.0, None),
        "qps": (("queries_per_second",), 0.0, None),
        "active_connections": (("connections",), 0.0, None),
        "cache_hit_ratio": (("percent",), 0.0, 100.0),
        "relation_churn": (("updated_tps", "deleted_tps", "inserted_tps", "hot_update_ratio"), 0.0, None),
        "vacuum_cleanup": (("removed_tps", "active_workers", "heap_blocks_scanned_per_sec"), 0.0, None),
        "dead_tuple_backlog": (("estimated_dead_tuples", "estimated_live_tuples"), 0.0, None),
        "maintenance_io": (("read_mb_per_sec", "write_mb_per_sec", "io_time_ms_per_sec"), 0.0, None),
        "oltp_service": (("transactions_per_sec", "p99_ms", "success_ratio"), 0.0, None),
        "xmin_horizon": (("oldest_xmin_age_sec", "blocked_vacuum_workers"), 0.0, None),
    }
    assert POSTGRES_METRIC_CATALOG.metric_names == set(expected)
    for metric, (fields, lower, upper) in expected.items():
        definition = POSTGRES_METRIC_CATALOG.definition(metric)
        assert definition.value_fields == fields
        assert definition.lower_bound == lower
        assert definition.upper_bound == upper
        assert POSTGRES_METRIC_CATALOG.target_variants(metric, object()) == (None,)
        POSTGRES_METRIC_CATALOG.validate_target(metric, None, object())
        if metric not in {"cpu", "memory", "disk_io", "qps", "active_connections", "cache_hit_ratio"}:
            POSTGRES_METRIC_CATALOG.validate_target(metric, "selected", object())
        else:
            with pytest.raises(ValueError, match="must be None"):
                POSTGRES_METRIC_CATALOG.validate_target(metric, "postgres", object())


def test_postgres_catalog_validates_one_postgres_series_target():
    frame = MetricFrame(
        metric="disk_io",
        query_target=None,
        step_seconds=2,
        series={"postgres": {"read_mb_per_second": (1.0, 2.0), "write_mb_per_second": (3.0, 4.0)}},
        timestamps_ms={"postgres": (1_700_000_000_000, 1_700_000_002_000)},
    )
    validate_metric_frame(frame, POSTGRES_METRIC_CATALOG)
    assert metric_catalog_for_system(DatabaseSystem.POSTGRESQL) is POSTGRES_METRIC_CATALOG


def test_postgres_metric_tool_definition_is_generated_from_catalog():
    metric_definitions = {
        item["metric_name"]: item
        for item in POSTGRES_QUERY_METRICS_TOOL_DEFINITION["metric_definitions"]
    }
    assert set(metric_definitions) == set(POSTGRES_METRIC_CATALOG.metric_names)
    for metric, item in metric_definitions.items():
        definition = POSTGRES_METRIC_CATALOG.definition(metric)
        if metric in {"relation_churn", "vacuum_cleanup", "dead_tuple_backlog"}:
            assert item["target_scope"]["query_target"] == "relation|null"
            assert item["target_scope"]["series_target"] == "relation"
        elif metric == "oltp_service":
            assert item["target_scope"]["query_target"] == "checkout|null"
            assert item["target_scope"]["series_target"] == "checkout"
        elif metric in {"maintenance_io", "xmin_horizon"}:
            assert item["target_scope"]["query_target"] == "postgres|null"
            assert item["target_scope"]["series_target"] == "postgres"
        else:
            assert item["target_scope"]["query_target"] is None
            assert item["target_scope"]["series_target"] == "postgres"
        assert item["target_scope"]["fields"] == list(definition.value_fields)
        assert item["target_scope"]["lower_bound"] == definition.lower_bound
        assert item["target_scope"]["upper_bound"] == definition.upper_bound
    parameter = next(item for item in POSTGRES_QUERY_METRICS_TOOL_DEFINITION["parameter_definitions"] if item["parameter_name"] == "metric_type")
    assert set(parameter["allowed_values"]) == set(POSTGRES_METRIC_CATALOG.metric_names)


def test_postgres_catalog_fingerprint_changes_when_snapshot_sql_contract_changes(monkeypatch):
    original = POSTGRES_METRIC_CATALOG.fingerprint()
    monkeypatch.setattr(
        "src.execution.postgres_metrics.PG_STATEMENT_SNAPSHOT_SQL",
        "SELECT changed_collector_sql",
    )
    assert POSTGRES_METRIC_CATALOG.fingerprint() != original
