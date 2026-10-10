from pathlib import Path

import pytest

from src.benchmark.run_table import _pass_metrics, load_scenario_attributes


def test_scenario_attribute_registry_has_all_postgresql_cases():
    cases = load_scenario_attributes(Path.cwd())
    postgres_cases = {
        key: case for key, case in cases.items() if key[0] == "postgresql"
    }
    tidb_cases = {key: case for key, case in cases.items() if key[0] == "tidb"}

    assert {case["_annotation_status"] for case in cases.values()} == {"provisional"}
    assert len(postgres_cases) == 50
    assert len(tidb_cases) == 60
    assert {case["category"] for case in postgres_cases.values()} == {
        "query_perf",
        "system_failure",
        "health_check",
        "business_change",
        "resource_governance",
    }
    assert {case["category"] for case in tidb_cases.values()} == {
        "business_change",
        "query_perf",
        "resource_governance",
        "system_failure",
        "health_check",
    }


def test_invalid_run_has_null_pass_fields():
    assert _pass_metrics({"valid_for_aggregate": False}) == {
        "outcome_pass": None,
        "diagnosis_pass": None,
        "safe_pass": None,
    }


def test_valid_run_requires_explicit_pass_results():
    with pytest.raises(ValueError, match="lacks required DP/OP/SP results"):
        _pass_metrics({
            "run_id": "run-1",
            "valid_for_aggregate": True,
            "diagnosis_pass": True,
            "outcome_pass": None,
            "safe_pass": None,
        })


def test_safe_pass_keeps_dimensions_independent():
    metrics = _pass_metrics({
        "run_id": "run-safe-only",
        "valid_for_aggregate": True,
        "diagnosis_pass": True,
        "outcome_pass": False,
        "safe_pass": True,
    })

    assert metrics == {
        "outcome_pass": False,
        "diagnosis_pass": True,
        "safe_pass": True,
    }
