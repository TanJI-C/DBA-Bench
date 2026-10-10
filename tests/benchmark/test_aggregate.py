from __future__ import annotations

import json

import pytest
import yaml

from src.benchmark.aggregate import load_records, write_combined_records
from src.benchmark.models import RunRecord
from src.benchmark.store import ExperimentStore


def make_record(experiment_id: str, run_id: str, scenario_id: str = "scenario") -> RunRecord:
    return RunRecord(
        experiment_id=experiment_id,
        run_id=run_id,
        system="postgresql",
        scenario_id=scenario_id,
        case_id="case",
        category="query_perf",
        script="scenario.py",
        agent_id="agent",
        agent_mode="llm",
        model="model",
        repetition=1,
        seed=11,
        port=19000,
        status="succeeded",
        diagnosis_pass=True,
        outcome_pass=True,
        safe_pass=True,
        valid_for_aggregate=True,
    )


def make_store(root, experiment_id: str, record: RunRecord) -> ExperimentStore:
    store = ExperimentStore(root, experiment_id)
    store.initialize({"experiment_id": experiment_id}, {"git_commit": "abc"})
    store.save(record)
    return store


def test_combines_disjoint_experiments_without_overwriting_sources(tmp_path):
    first = make_store(tmp_path, "first", make_record("first", "run-1", "scenario-a"))
    second = make_store(tmp_path, "second", make_record("second", "run-2", "scenario-b"))
    records = load_records([first, second])
    output = tmp_path / "combined"

    write_combined_records(output, "combined", ["first", "second"], records)

    assert yaml.safe_load((output / "sources.yaml").read_text(encoding="utf-8")) == {
        "experiment_id": "combined",
        "source_experiments": ["first", "second"],
        "logical_run_count": 2,
    }
    lines = (output / "runs.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["run_id"] for line in lines] == ["run-1", "run-2"]
    with pytest.raises(FileExistsError, match="already exists"):
        write_combined_records(output, "combined", ["first", "second"], records)


def test_rejects_duplicate_logical_cells_across_experiments(tmp_path):
    first = make_store(tmp_path, "first", make_record("first", "run-1"))
    second = make_store(tmp_path, "second", make_record("second", "run-2"))

    with pytest.raises(ValueError, match="duplicate logical cells"):
        load_records([first, second])


def test_rejects_missing_experiment_artifacts(tmp_path):
    store = ExperimentStore(tmp_path, "missing")

    with pytest.raises(FileNotFoundError, match="missing"):
        load_records([store])
