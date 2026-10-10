from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.benchmark.dataset import (
    aggregate_dataset,
    dataset_lock_path,
    load_dataset_lock,
    load_dataset_spec,
    load_live_entries,
    records_from_entries,
)
class DatasetIndex:
    def __init__(
        self,
        datasets_root: str | Path,
        experiments_root: str | Path,
        project_root: str | Path,
    ):
        self.datasets_root = Path(datasets_root).resolve()
        self.experiments_root = Path(experiments_root).resolve()
        self.project_root = Path(project_root).resolve()

    def _spec_path(self, dataset_id: str) -> Path:
        path = (self.datasets_root / f"{dataset_id}.yaml").resolve()
        path.relative_to(self.datasets_root)
        if not path.is_file():
            raise FileNotFoundError(
                f"Dataset definition does not exist: dataset_id={dataset_id!r}, path={path}"
            )
        return path

    def _spec(self, dataset_id: str):
        return load_dataset_spec(self._spec_path(dataset_id))

    def _live_artifact_path(self, value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            resolved = path.resolve()
        else:
            parts = path.parts
            if "artifacts" in parts:
                path = Path(*parts[parts.index("artifacts"):])
            resolved = (self.project_root / path).resolve()
        resolved.relative_to(self.project_root)
        return resolved

    def _entries(self, spec) -> tuple[str, list[dict[str, Any]]]:
        if dataset_lock_path(spec).is_file():
            return "frozen", load_dataset_lock(spec)["runs"]
        return "live", load_live_entries(spec, self.experiments_root)

    def list_datasets(self) -> list[dict[str, Any]]:
        if not self.datasets_root.is_dir():
            return []
        datasets = []
        for path in sorted(self.datasets_root.glob("*.yaml")):
            spec = load_dataset_spec(path)
            state, entries = self._entries(spec)
            records = records_from_entries(entries)
            summary = aggregate_dataset(records)["summary"]
            datasets.append(
                {
                    "dataset_id": spec.dataset_id,
                    "state": state,
                    "data_status": spec.data_status,
                    "metric_contract": spec.metric_contract,
                    "source_experiments": list(spec.experiment_ids),
                    **summary,
                }
            )
        return datasets

    @staticmethod
    def _cell_status(runs: list[Any]) -> str:
        statuses = {run.status for run in runs}
        if len(statuses) == 1:
            return next(iter(statuses))
        if "running" in statuses:
            return "running"
        if "pending" in statuses:
            return "pending"
        return "mixed"

    def dataset(self, dataset_id: str) -> dict[str, Any]:
        spec = self._spec(dataset_id)
        state, entries = self._entries(spec)
        records = records_from_entries(entries)
        aggregate = aggregate_dataset(records)
        scenario_cases = sorted(
            {(record.scenario_id, record.case_id) for record in records}
        )
        agents = list(dict.fromkeys(entry["baseline_id"] for entry in entries))
        cells: dict[tuple[str, str, str], list[Any]] = defaultdict(list)
        for record in records:
            cells[(record.agent_id, record.scenario_id, record.case_id)].append(record)

        matrix_rows = []
        for agent_id in agents:
            row_cells = []
            for scenario_id, case_id in scenario_cases:
                selected = cells[(agent_id, scenario_id, case_id)]
                valid = [
                    record
                    for record in selected
                    if record.valid_for_aggregate
                ]
                row_cells.append(
                    {
                        "scenario_case_id": f"{scenario_id}::{case_id}",
                        "status": self._cell_status(selected) if selected else "not_planned",
                        "diagnosis_pass_rate": (
                            sum(record.diagnosis_pass is True for record in valid if record.diagnosis_pass is not None)
                            / sum(record.diagnosis_pass is not None for record in valid)
                            if any(record.diagnosis_pass is not None for record in valid) else None
                        ),
                        "outcome_pass_rate": sum(record.outcome_pass is True for record in valid) / len(valid) if valid else None,
                        "safe_pass_rate": sum(record.safe_pass is True for record in valid) / len(valid) if valid else None,
                        "runs": [
                            {
                                "experiment_id": record.experiment_id,
                                "run_id": record.run_id,
                                "repetition": record.repetition,
                                "attempt": record.attempt,
                                "status": record.status,
                                "valid_for_aggregate": record.valid_for_aggregate,
                                "diagnosis_pass": record.diagnosis_pass,
                                "outcome_pass": record.outcome_pass,
                                "safe_pass": record.safe_pass,
                            }
                            for record in selected
                        ],
                    }
                )
            matrix_rows.append({"agent_id": agent_id, "cells": row_cells})

        return {
            "dataset_id": spec.dataset_id,
            "state": state,
            "data_status": spec.data_status,
            "metric_contract": spec.metric_contract,
            "source_experiments": list(spec.experiment_ids),
            "summary": aggregate["summary"],
            "scenario_cases": [
                {
                    "id": f"{scenario_id}::{case_id}",
                    "scenario_id": scenario_id,
                    "case_id": case_id,
                    "label": f"{scenario_id} / {case_id}",
                }
                for scenario_id, case_id in scenario_cases
            ],
            "matrix": {"rows": matrix_rows},
            "scenario_agents": aggregate["scenario_agents"],
        }

    def run_detail(
        self,
        dataset_id: str,
        run_id: str,
        attempt: int,
    ) -> dict[str, Any]:
        spec = self._spec(dataset_id)
        state, entries = self._entries(spec)
        matches = [
            entry
            for entry in entries
            if entry["run_id"] == run_id and entry["attempt"] == attempt
        ]
        if len(matches) != 1:
            raise FileNotFoundError(
                f"Dataset does not select run attempt: dataset_id={dataset_id!r}, "
                f"run_id={run_id!r}, attempt={attempt}"
            )
        entry = matches[0]
        run = entry["run"]
        if state == "frozen":
            evaluator_artifact = entry["artifacts"]["evaluator"]
            evaluator_path = (
                None
                if evaluator_artifact is None
                else (self.project_root / evaluator_artifact["path"]).resolve()
            )
        else:
            attempts = [
                item for item in run["attempts"] if item["attempt"] == attempt
            ]
            if len(attempts) != 1:
                raise ValueError(
                    f"Run attempt metadata is missing or duplicated: run_id={run_id!r}, "
                    f"attempt={attempt}"
                )
            evaluator_value = attempts[0]["evaluator_path"]
            evaluator_path = (
                None
                if evaluator_value is None
                else self._live_artifact_path(evaluator_value)
            )
        evaluator = None
        if evaluator_path is not None:
            evaluator_path.relative_to(self.project_root)
            if not evaluator_path.is_file():
                raise FileNotFoundError(
                    f"Selected evaluator artifact does not exist: dataset_id={dataset_id!r}, "
                    f"run_id={run_id!r}, attempt={attempt}, path={evaluator_path}"
                )
            evaluator = json.loads(evaluator_path.read_text(encoding="utf-8"))
        return {
            "dataset_id": dataset_id,
            "state": state,
            "selection": {
                "experiment_id": entry["experiment_id"],
                "run_id": run_id,
                "attempt": attempt,
            },
            "run": run,
            "evaluator_available": evaluator is not None,
            "evaluator": evaluator,
        }
