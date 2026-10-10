from __future__ import annotations

import json

from src.visualization.trace_index import TraceIndex, parse_trace_filename, trace_summary


def test_parse_canonical_experiment_filename():
    result = parse_trace_filename(
        "run_pilot__pg_query_perf_missing_index__default__agent1__r003__a002.json"
    )

    assert result == {
        "filename_status": "valid",
        "filename_format": "experiment_v1",
        "experiment_id": "pilot",
        "run_id": "pilot__pg_query_perf_missing_index__default__agent1__r003",
        "scenario_id": "pg_query_perf_missing_index",
        "case_id": "default",
        "agent_id": "agent1",
        "repetition": 3,
        "attempt": 2,
    }


def test_parse_persistent_scenario_filename():
    result = parse_trace_filename(
        "run_pilot__persistent-scenario__pg_continuous_ops_smoke__agent2__r001__a002.json"
    )

    assert result == {
        "filename_status": "valid",
        "filename_format": "persistent_scenario_v1",
        "scenario_kind": "persistent",
        "experiment_id": "pilot",
        "run_id": "pilot__persistent-scenario__pg_continuous_ops_smoke__agent2__r001",
        "scenario_id": "pg_continuous_ops_smoke",
        "agent_id": "agent2",
        "repetition": 1,
        "attempt": 2,
    }


def test_parse_legacy_filename_from_right_hand_fields():
    result = parse_trace_filename(
        "run_PgQueryPerfMissingIndexScenario_LLMAgent_2026-07-06_16_34_26.json"
    )

    assert result["scenario"] == "PgQueryPerfMissingIndexScenario"
    assert result["agent_type"] == "LLMAgent"
    assert result["filename_status"] == "valid"


def test_trace_summary_marks_invalid_json(tmp_path):
    path = tmp_path / "run_bad.json"
    path.write_text("{broken", encoding="utf-8")

    summary = trace_summary(path)

    assert summary["parse_status"] == "invalid_json"
    assert "line 1" in summary["parse_error"]


def test_trace_summary_reads_persistent_scenario_schema(tmp_path):
    path = tmp_path / (
        "run_pilot__persistent-scenario__pg_continuous_ops_smoke__agent2__r001__a001.json"
    )
    path.write_text(json.dumps({
        "$schema": "persistent_scenario_trace_v2",
        "metadata": {
            "scenario_kind": "persistent",
            "scenario_id": "pg_continuous_ops_smoke",
            "experiment_id": "pilot",
            "run_id": "pilot__persistent-scenario__pg_continuous_ops_smoke__agent2__r001",
            "timestamp_end_wall": 12.0,
            "agent_id": "agent2",
        },
        "persistent_scenario_evaluation": {
            "DiagnosisPass": True,
            "OutcomePass": False,
            "SafePass": True,
        },
        "diagnostic_structure": {"type": "persistent"},
        "formal_eligible": False,
    }), encoding="utf-8")

    summary = trace_summary(path)

    assert summary["parse_status"] == "valid"
    assert summary["schema"] == "persistent_scenario_trace_v2"
    assert summary["scenario_kind"] == "persistent"
    assert summary["scenario_id"] == "pg_continuous_ops_smoke"
    assert summary["agent_id"] == "agent2"
    assert summary["diagnosis_pass"] is True
    assert summary["outcome_pass"] is False
    assert summary["safe_pass"] is True
    assert summary["formal_eligible"] is False


def test_trace_index_filters_searches_sorts_and_paginates(tmp_path):
    for index, (scenario, agent, score, success) in enumerate([
        ("missing_index", "LLMAgent", 80, True),
        ("sort_spill", "DbotAgent", 40, False),
        ("missing_index", "DbotAgent", 60, True),
    ]):
        path = tmp_path / f"run_Scenario{index}_{agent}_2026-07-0{index + 1}_10_00_00.json"
        path.write_text(json.dumps({
            "$schema": "run_trace_v3",
            "metadata": {"scenario_name": scenario, "agent_type": agent, "timestamp_end": index + 1},
            "evaluation": {
                "DiagnosisPass": success,
                "OutcomePass": success,
                "SafePass": success,
            },
            "diagnostic_structure": {"type": "linear"},
        }), encoding="utf-8")

    index = TraceIndex(tmp_path)
    result = index.query({"q": ["missing"], "agent": ["DbotAgent"], "limit": ["10"]})
    failed = index.query({"evaluation": ["failed"], "limit": ["10"]})

    assert result["total"] == 1
    assert result["items"][0]["safe_pass"] is True
    assert failed["total"] == 1
    assert failed["items"][0]["scenario"] == "sort_spill"
