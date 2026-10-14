from __future__ import annotations

from pathlib import Path

from src.database.system import DatabaseSystem
from src.benchmark.dataset import (
    aggregate_dataset,
    create_dataset_spec,
    diff_dataset_locks,
    freeze_dataset,
    load_dataset_spec,
    verify_dataset_lock,
)
from src.benchmark.models import AgentSpec, RunRecord, BoundedScenarioRunSpec
from src.benchmark.store import ExperimentStore, atomic_write_json


def write_completed_run(
    project_root: Path,
    experiment_id: str,
    run_id: str,
    scenario_id: str,
    case_id: str,
    agent_id: str,
    passes: tuple[bool, bool, bool],
    *,
    failure_category: str | None = None,
) -> RunRecord:
    store = ExperimentStore(project_root / "artifacts" / "experiments", experiment_id)
    store.initialize({"experiment_id": experiment_id}, {"git_commit": "abc"})
    spec = BoundedScenarioRunSpec(
        experiment_id=experiment_id,
        run_id=run_id,
        system=DatabaseSystem.POSTGRESQL,
        scenario_id=scenario_id,
        script="scenario.py",
        category="query_perf",
        case_id=case_id,
        agent=AgentSpec(id=agent_id, mode="mock"),
        repetition=1,
        seed=11,
        port=19000,
    )
    record = RunRecord.from_spec(spec)
    record.attempt = 1
    record.status = "failed" if failure_category else "succeeded"
    record.failure_category = failure_category
    if not failure_category:
        record.diagnosis_pass, record.outcome_pass, record.safe_pass = passes
        record.evaluator = "TestEvaluatorCase"
        record.case_no = 0
        record.evaluation = {
            "DiagnosisPass": record.diagnosis_pass,
            "OutcomePass": record.outcome_pass,
            "SafePass": record.safe_pass,
            "evaluator": record.evaluator,
            "case_no": record.case_no,
        }
    record.valid_for_aggregate = failure_category is None
    attempt_dir = store.attempt_dir(run_id, 1)
    attempt_dir.mkdir(parents=True)
    (attempt_dir / "stdout.log").write_text("stdout", encoding="utf-8")
    if record.valid_for_aggregate:
        atomic_write_json(attempt_dir / "trace.json", {"evaluation": record.evaluation})
        atomic_write_json(attempt_dir / "evaluator.json", record.evaluation)
        record.trace_path = str((attempt_dir / "trace.json").relative_to(project_root))
        record.evaluator_path = str((attempt_dir / "evaluator.json").relative_to(project_root))
    record.stdout_path = str((attempt_dir / "stdout.log").relative_to(project_root))
    record.attempts.append(
        {
            "attempt": 1,
            "status": record.status,
            "trace_path": record.trace_path,
            "evaluator_path": record.evaluator_path,
            "stdout_path": record.stdout_path,
        }
    )
    store.save_attempt(record)
    store.save(record)
    return record


def test_dataset_freeze_verify_and_diff(tmp_path):
    first = write_completed_run(
        tmp_path,
        "experiment-a",
        "run-a",
        "scenario-a",
        "case-a",
        "agent-a",
        (True, True, True),
    )
    datasets_root = tmp_path / "datasets"
    before_path = create_dataset_spec(
        datasets_root,
        "paper-v1",
        [{
            "experiment_id": "experiment-a",
            "run_id": first.run_id,
            "baseline_id": "agent-a",
        }],
        "evaluation-v1",
        "audited",
    )
    before = load_dataset_spec(before_path)
    freeze_dataset(before, tmp_path, tmp_path / "artifacts" / "experiments")
    verify_dataset_lock(before, tmp_path)
    summary = aggregate_dataset([first])
    assert summary["scenario_agents"][0]["safe_pass_rate"] == 1.0

    second = write_completed_run(
        tmp_path,
        "experiment-b",
        "run-b",
        "scenario-b",
        "case-b",
        "agent-a",
        (True, True, True),
    )
    after_path = create_dataset_spec(
        datasets_root,
        "paper-v2",
        [
            {
                "experiment_id": "experiment-a",
                "run_id": first.run_id,
                "baseline_id": "agent-a",
            },
            {
                "experiment_id": "experiment-b",
                "run_id": second.run_id,
                "baseline_id": "agent-a",
            },
        ],
        "evaluation-v1",
        "audited",
    )
    after = load_dataset_spec(after_path)
    freeze_dataset(after, tmp_path, tmp_path / "artifacts" / "experiments")

    diff = diff_dataset_locks(before, after)
    assert diff["added"] == [list((second.scenario_id, second.case_id, "agent-a", 1, 11))]
    assert diff["removed"] == []
    assert diff["replaced"] == []
    assert first.run_id == "run-a"


def test_dataset_aggregation_separates_execution_and_infrastructure_failures(tmp_path):
    succeeded = write_completed_run(
        tmp_path,
        "experiment-a",
        "run-ok",
        "scenario-a",
        "case-a",
        "agent-a",
        (True, True, True),
    )
    scenario_failure = write_completed_run(
        tmp_path,
        "experiment-b",
        "run-scenario-failure",
        "scenario-a",
        "case-b",
        "agent-a",
        (False, False, False),
        failure_category="scenario_process",
    )
    infrastructure_failure = write_completed_run(
        tmp_path,
        "experiment-c",
        "run-timeout",
        "scenario-a",
        "case-c",
        "agent-a",
        (False, False, False),
        failure_category="timeout",
    )

    result = aggregate_dataset([succeeded, scenario_failure, infrastructure_failure])
    row = result["scenario_agents"][0]

    assert row["runs"] == 3
    assert row["valid_runs"] == 1
    assert row["execution_failures"] == 2
    assert row["infrastructure_failure_rate"] == 1 / 3
    assert row["diagnosis_pass_rate"] == 1.0
    assert row["outcome_pass_rate"] == 1.0
    assert row["safe_pass_rate"] == 1.0


def test_dataset_aggregation_keeps_safe_pass_independent_from_outcome_pass(tmp_path):
    safe_only = write_completed_run(
        tmp_path,
        "experiment-safe-only",
        "run-safe-only",
        "scenario-a",
        "case-a",
        "agent-a",
        (True, False, True),
    )
    full = write_completed_run(
        tmp_path,
        "experiment-full",
        "run-full",
        "scenario-a",
        "case-b",
        "agent-a",
        (True, True, True),
    )

    row = aggregate_dataset([safe_only, full])["scenario_agents"][0]

    assert row["outcome_pass_rate"] == 0.5
    assert row["safe_pass_rate"] == 1.0
