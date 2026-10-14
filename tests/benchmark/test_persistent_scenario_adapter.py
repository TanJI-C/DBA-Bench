from __future__ import annotations

import json
import sys
from pathlib import Path

from src.database.system import DatabaseSystem
from src.benchmark.isolation import derive_worker_demand
from src.benchmark.aggregate import aggregate, write_aggregate
from src.benchmark.manifest import load_manifest
from src.benchmark.models import (
    AgentSpec,
    IsolationPolicySpec,
    PersistentScenarioRunSpec,
    RunRecord,
)
from src.benchmark.planner import plan_runs
from src.benchmark.runner import ExperimentRunner, build_command
from src.benchmark.store import ExperimentStore


def _manifest(tmp_path: Path):
    path = tmp_path / "persistent_scenario-experiment.yaml"
    path.write_text(
        """
experiment_id: persistent_scenario-pilot
benchmark:
  scenario_kind: persistent
  scenarios: [pg_continuous_ops_smoke]
agents:
  - id: mock
    mode: mock
repetitions: 1
seeds: [11]
runtime:
  run_mode: development
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return load_manifest(path)


def _spec() -> PersistentScenarioRunSpec:
    return PersistentScenarioRunSpec(
        experiment_id="persistent_scenario-pilot",
        run_id="persistent_scenario-pilot__persistent-scenario__pg_continuous_ops_smoke__mock__r001",
        scenario_id="pg_continuous_ops_smoke",
        system=DatabaseSystem.POSTGRESQL,
        agent=AgentSpec(id="mock", mode="mock", max_turns=7),
        repetition=1,
        seed=11,
        port=25300,
    )


def _trace(evaluation: dict[str, object], *, schema: str = "persistent_scenario_trace_v2") -> str:
    return json.dumps(
        {"$schema": schema, "persistent_scenario_evaluation": evaluation},
        ensure_ascii=False,
    )


def _run_with_trace(tmp_path: Path, monkeypatch, evaluation: dict[str, object], *, return_code: int = 0, schema: str = "persistent_scenario_trace_v2"):
    manifest = _manifest(tmp_path)
    spec = _spec()
    store = ExperimentStore(tmp_path / "artifacts", manifest.experiment_id)
    store.initialize(manifest.raw, {"git_commit": "test"})
    store.save(RunRecord.from_spec(spec))
    trace_text = _trace(evaluation, schema=schema)
    child = (
        "import os; from pathlib import Path; "
        "Path(os.environ['AIOPS_TRACE_OUTPUT_DIR'], os.environ['AIOPS_TRACE_FILENAME'])"
        f".write_text({trace_text!r}, encoding='utf-8'); "
        f"raise SystemExit({return_code})"
    )
    monkeypatch.setattr(
        "src.benchmark.runner.build_command",
        lambda run_spec, experiment: [sys.executable, "-c", child, "--port", str(run_spec.port)],
    )
    runner = ExperimentRunner(manifest, store)
    return runner._execute(spec), store


def _valid_evaluation(*, model_failure: bool, valid: bool = True, classification: str | None = None):
    passes = not model_failure
    return {
        "$schema": "persistent_scenario_evaluation_v2",
        "schema_version": 2,
        "DiagnosisPass": None,
        "OutcomePass": passes,
        "SafePass": passes,
        "ServiceObjectivesPass": passes,
        "DataIntegrityPass": True,
        "RequiredStatePass": passes,
        "objective_results": [
            {
                "objective_id": "trade_good_fraction",
                "load_class": "oltp",
                "service_id": "trade",
                "pass": passes,
            }
        ],
        "valid": valid,
        "model_failure": model_failure,
        "failure_classification": classification,
    }


def test_persistent_scenario_command_uses_v2_cli_and_manifest_runtime(tmp_path):
    manifest = _manifest(tmp_path)

    command = build_command(_spec(), manifest)

    assert command[:3] == [sys.executable, "-m", "src.cli"]
    assert command[3:5] == ["persistent-scenario", "run"]
    assert command[command.index("--agent") + 1] == "mock"
    assert command[command.index("--run-id") + 1] == _spec().run_id
    assert command[command.index("--max-turns") + 1] == "7"
    assert command[command.index("--run-mode") + 1] == "development"
    assert command[command.index("--time-scale") + 1] == "1.0"


def test_persistent_scenario_plan_carries_declared_node_resources(tmp_path):
    manifest = _manifest(tmp_path)
    specs = plan_runs(manifest)

    assert len(specs) == 1
    assert specs[0].resources is not None
    assert specs[0].resources.worker_physical_cores == 2
    assert specs[0].resources.worker_memory_mb == 2048
    assert specs[0].resources.container_cpu_limit == 2.0
    assert specs[0].resources.container_memory_mb == 2048
    assert derive_worker_demand(
        specs,
        IsolationPolicySpec(numa_policy="separate"),
    ).memory_mb_per_worker == 2048


def test_valid_agent_failure_with_nonzero_process_is_a_valid_model_result(tmp_path, monkeypatch):
    record, store = _run_with_trace(
        tmp_path,
        monkeypatch,
        _valid_evaluation(model_failure=True, classification="agent_failure"),
        return_code=7,
    )

    assert record.status == "succeeded"
    assert record.return_code == 7
    assert record.failure_category == "model_failure"
    assert record.valid_for_aggregate is True
    assert record.diagnosis_pass is None
    assert record.outcome_pass is False
    assert record.safe_pass is False
    assert record.service_objectives_pass is False
    assert store.load(record.run_id).valid_for_aggregate is True


def test_valid_process_crash_after_evaluation_is_not_reported_as_success(tmp_path, monkeypatch):
    record, store = _run_with_trace(
        tmp_path,
        monkeypatch,
        _valid_evaluation(model_failure=False),
        return_code=7,
    )

    assert record.status == "failed"
    assert record.failure_category == "persistent_scenario_process"
    assert record.return_code == 7
    assert record.valid_for_aggregate is False
    assert record.evaluation["valid"] is True
    assert record.diagnosis_pass is None
    assert record.outcome_pass is True
    assert record.safe_pass is True
    assert store.load(record.run_id).valid_for_aggregate is False


def test_invalid_provider_run_keeps_evaluation_but_is_excluded(tmp_path, monkeypatch):
    record, store = _run_with_trace(
        tmp_path,
        monkeypatch,
        _valid_evaluation(
            model_failure=False,
            valid=False,
            classification="agent_provider_failure",
        )
        | {"OutcomePass": None, "SafePass": None, "failure": "provider unavailable"},
        return_code=7,
    )

    assert record.status == "failed"
    assert record.failure_category == "agent_provider_failure"
    assert record.valid_for_aggregate is False
    assert record.evaluation["failure"] == "provider unavailable"
    assert store.load(record.run_id).evaluation["failure"] == "provider unavailable"


def test_invalid_environment_run_is_excluded_from_persistent_scenario_aggregate(tmp_path, monkeypatch):
    record, _ = _run_with_trace(
        tmp_path,
        monkeypatch,
        _valid_evaluation(
            model_failure=False,
            valid=False,
            classification="invalid_environment",
        ),
        return_code=3,
    )

    assert record.status == "failed"
    assert record.failure_category == "invalid_environment"
    assert record.valid_for_aggregate is False


def test_unknown_persistent_scenario_trace_schema_is_rejected(tmp_path, monkeypatch):
    record, store = _run_with_trace(
        tmp_path,
        monkeypatch,
        _valid_evaluation(model_failure=False),
        schema="persistent_scenario_trace_v1",
    )

    assert record.status == "failed"
    assert record.failure_category == "trace_schema"
    assert record.valid_for_aggregate is False
    assert record.evaluation == {}
    assert not Path(store.root / record.evaluator_path).is_file()


def test_old_persistent_scenario_evaluation_schema_is_rejected(tmp_path, monkeypatch):
    legacy = _valid_evaluation(model_failure=False)
    legacy["$schema"] = "persistent_scenario_evaluation_v1"
    del legacy["schema_version"]
    legacy["PersistentScenarioSLOPass"] = True
    record, _ = _run_with_trace(tmp_path, monkeypatch, legacy)

    assert record.status == "failed"
    assert record.failure_category == "trace_schema"
    assert record.valid_for_aggregate is False


def test_persistent_scenario_aggregate_uses_v2_fields(tmp_path):
    base = dict(
        experiment_id="persistent_scenario-pilot",
        system="postgresql",
        scenario_id="pg_continuous_ops_smoke",
        case_id=None,
        category=None,
        script=None,
        agent_id="mock",
        agent_mode="mock",
        model=None,
        repetition=1,
        seed=11,
        port=25300,
        scenario_kind="persistent",
        status="succeeded",
        valid_for_aggregate=True,
    )
    passed = RunRecord(
        run_id="passed",
        diagnosis_pass=None,
        outcome_pass=True,
        safe_pass=True,
        service_objectives_pass=True,
        data_integrity_pass=True,
        required_state_pass=True,
        evaluation={
            "model_failure": False,
            "objective_results": [{"objective_id": "trade", "load_class": "oltp", "pass": True}],
        },
        **base,
    )
    model_failed = RunRecord(
        run_id="model-failed",
        diagnosis_pass=False,
        outcome_pass=False,
        safe_pass=True,
        service_objectives_pass=False,
        data_integrity_pass=True,
        required_state_pass=True,
        evaluation={
            "model_failure": True,
            "objective_results": [{"objective_id": "trade", "load_class": "oltp", "pass": False}],
        },
        **{**base, "seed": 22},
    )
    invalid = RunRecord(
        run_id="invalid-provider",
        failure_category="agent_provider_failure",
        evaluation={"model_failure": False},
        **{**base, "seed": 33, "status": "failed", "valid_for_aggregate": False},
    )

    result = aggregate([passed, model_failed, invalid])

    summary = result["summary"]
    assert summary["runs"] == 3
    assert summary["valid_runs"] == 2
    assert summary["diagnosis_pass_rate"] == 0.0  # one N/A excluded, one applicable failure
    assert summary["outcome_pass_rate"] == 0.5
    assert summary["safe_pass_rate"] == 1.0
    assert summary["service_objectives_pass_rate"] == 0.5
    assert summary["data_integrity_pass_rate"] == 1.0
    assert summary["required_state_pass_rate"] == 1.0
    assert summary["model_failure_count"] == 1
    assert summary["model_failure_rate"] == 0.5
    assert summary["objective_pass_rates"] == {"oltp": 0.5}

    aggregate_root = tmp_path / "aggregate"
    aggregate_root.mkdir()
    write_aggregate(aggregate_root, result)
    csv_header = (aggregate_root / "aggregate.csv").read_text(encoding="utf-8").splitlines()[0]
    assert "diagnosis_pass_rate" in csv_header
    assert "service_objectives_pass_rate" in csv_header
    assert "required_state_pass_rate" in csv_header
    assert "persistent_scenario_slo_pass_rate" not in csv_header
