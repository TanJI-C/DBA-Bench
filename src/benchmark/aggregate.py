from __future__ import annotations

import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import yaml

from .models import RunRecord
from .store import ExperimentStore, atomic_write_json, atomic_write_text


def logical_cell(record: RunRecord) -> tuple:
    if record.scenario_kind == "persistent":
        return (
            record.scenario_id,
            record.agent_id,
            record.model,
            record.repetition,
            record.seed,
        )
    return (
        record.scenario_id,
        record.case_id,
        record.agent_id,
        record.model,
        record.repetition,
        record.seed,
    )


def load_records(stores: list[ExperimentStore]) -> list[RunRecord]:
    records = []
    for store in stores:
        if not store.root.is_dir():
            raise FileNotFoundError(f"Experiment artifacts do not exist: {store.root}")
        source_records = store.records()
        if not source_records:
            raise ValueError(f"Experiment contains no run records: {store.root}")
        records.extend(source_records)
    counts = Counter(logical_cell(record) for record in records)
    duplicates = sorted(cell for cell, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(f"Combined experiments contain duplicate logical cells: {duplicates}")
    return records


def write_combined_records(
    root: Path,
    experiment_id: str,
    source_experiments: list[str],
    records: list[RunRecord],
) -> None:
    if root.exists():
        raise FileExistsError(f"Combined experiment already exists: {root}")
    root.mkdir(parents=True)
    sources = {
        "experiment_id": experiment_id,
        "source_experiments": source_experiments,
        "logical_run_count": len(records),
    }
    atomic_write_text(
        root / "sources.yaml",
        yaml.safe_dump(sources, allow_unicode=True, sort_keys=False),
    )
    atomic_write_text(
        root / "runs.jsonl",
        "\n".join(json.dumps(record.as_dict(), ensure_ascii=False) for record in records) + "\n",
    )


def _stats(records: list[RunRecord]) -> dict:
    valid = [record for record in records if record.valid_for_aggregate]
    diagnosis_valid = [record for record in valid if record.diagnosis_pass is not None]
    execution_failures = sum(record.status != "succeeded" for record in records)
    return {
        "runs": len(records),
        "valid_runs": len(valid),
        "execution_failures": execution_failures,
        "infrastructure_failure_rate": execution_failures / len(records) if records else 0.0,
        "diagnosis_pass_rate": sum(record.diagnosis_pass is True for record in diagnosis_valid) / len(diagnosis_valid) if diagnosis_valid else None,
        "outcome_pass_rate": sum(record.outcome_pass is True for record in valid) / len(valid) if valid else None,
        "safe_pass_rate": sum(record.safe_pass is True for record in valid) / len(valid) if valid else None,
    }


def _persistent_scenario_stats(records: list[RunRecord]) -> dict:
    valid = [record for record in records if record.valid_for_aggregate]
    def rate(field: str):
        values = [getattr(record, field) for record in valid if getattr(record, field) is not None]
        return sum(value is True for value in values) / len(values) if values else None

    model_failure_count = sum(
        record.evaluation.get("model_failure") is True
        for record in valid
    )
    objective_rates: dict[str, dict[str, float | None]] = {}
    for record in valid:
        for objective in record.evaluation.get("objective_results", ()):
            load_class = objective.get("load_class")
            if load_class is None:
                continue
            bucket = objective_rates.setdefault(load_class, {"denominator": 0, "passed": 0})
            bucket["denominator"] += 1
            bucket["passed"] += 1 if objective.get("pass") is True else 0
    objective_pass_rates = {
        load_class: (bucket["passed"] / bucket["denominator"] if bucket["denominator"] else None)
        for load_class, bucket in sorted(objective_rates.items())
    }
    return {
        "runs": len(records),
        "valid_runs": len(valid),
        "execution_failures": sum(record.status != "succeeded" for record in records),
        "infrastructure_failure_rate": (
            sum(record.status != "succeeded" for record in records) / len(records)
            if records else 0.0
        ),
        "diagnosis_pass_rate": rate("diagnosis_pass"),
        "outcome_pass_rate": rate("outcome_pass"),
        "safe_pass_rate": rate("safe_pass"),
        "service_objectives_pass_rate": rate("service_objectives_pass"),
        "data_integrity_pass_rate": rate("data_integrity_pass"),
        "required_state_pass_rate": rate("required_state_pass"),
        "model_failure_count": model_failure_count,
        "model_failure_rate": model_failure_count / len(valid) if valid else None,
        "objective_pass_rates": objective_pass_rates,
    }


def aggregate(records: Iterable[RunRecord]) -> dict:
    all_records = list(records)
    scenario_kinds = {record.scenario_kind for record in all_records}
    if len(scenario_kinds) > 1:
        raise ValueError(f"Cannot aggregate mixed Scenario kinds: scenario_kinds={sorted(scenario_kinds)!r}")
    if all_records and all_records[0].scenario_kind == "persistent":
        by_scenario_agent: dict[tuple[str | None, str], list[RunRecord]] = defaultdict(list)
        by_agent: dict[str, list[RunRecord]] = defaultdict(list)
        for record in all_records:
            by_scenario_agent[(record.scenario_id, record.agent_id)].append(record)
            by_agent[record.agent_id].append(record)
        scenario_agents = [
            {"scenario_id": scenario_id, "agent_id": agent_id, **_persistent_scenario_stats(items)}
            for (scenario_id, agent_id), items in sorted(by_scenario_agent.items())
        ]
        agents = [{"agent_id": agent_id, **_persistent_scenario_stats(items)} for agent_id, items in sorted(by_agent.items())]
        return {
            "scenario_kind": "persistent",
            "summary": _persistent_scenario_stats(all_records),
            "agents": agents,
            "scenario_agents": scenario_agents,
        }
    by_scenario_agent: dict[tuple[str, str], list[RunRecord]] = defaultdict(list)
    by_agent: dict[str, list[RunRecord]] = defaultdict(list)
    for record in all_records:
        by_scenario_agent[(record.scenario_id, record.agent_id)].append(record)
        by_agent[record.agent_id].append(record)

    groups = [
        {"scenario_id": scenario, "agent_id": agent, **_stats(items)}
        for (scenario, agent), items in sorted(by_scenario_agent.items())
    ]
    agents = [{"agent_id": agent_id, **_stats(items)} for agent_id, items in sorted(by_agent.items())]
    return {"scenario_kind": "bounded", "summary": _stats(all_records), "agents": agents, "scenario_agents": groups}


def write_aggregate(root: Path, result: dict) -> None:
    atomic_write_json(root / "aggregate.json", result)
    output = io.StringIO()
    if result.get("scenario_kind") == "persistent":
        fields = [
            "scenario_id", "agent_id", "runs", "valid_runs", "execution_failures",
            "infrastructure_failure_rate", "diagnosis_pass_rate", "outcome_pass_rate",
            "safe_pass_rate", "service_objectives_pass_rate", "data_integrity_pass_rate",
            "required_state_pass_rate", "model_failure_count", "model_failure_rate",
        ]
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(result["scenario_agents"])
        atomic_write_text(root / "aggregate.csv", output.getvalue())
        return
    fields = [
        "scenario_id", "agent_id", "runs", "valid_runs", "execution_failures",
        "infrastructure_failure_rate", "diagnosis_pass_rate", "outcome_pass_rate",
        "safe_pass_rate",
    ]
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(result["scenario_agents"])
    atomic_write_text(root / "aggregate.csv", output.getvalue())
