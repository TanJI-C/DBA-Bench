from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .manifest import validate_identifier
from .models import RunRecord, TERMINAL_STATUSES
from .store import ExperimentStore, atomic_write_json, atomic_write_text


DATASET_SCHEMA_VERSION = 2
DATASET_LOCK_SCHEMA_VERSION = 2
INFRASTRUCTURE_FAILURE_CATEGORIES = {
    "admission",
    "process_start",
    "trace_export",
    "evaluator",
    "timeout",
    "interrupted",
    "provider",
    "protocol",
    "quota",
    "workload_setup",
    "database_startup",
}
SUMMARY_FIELDS = (
    "scenario_id",
    "agent_id",
    "runs",
    "valid_runs",
    "execution_failures",
    "infrastructure_failure_rate",
    "diagnosis_pass_rate",
    "outcome_pass_rate",
    "safe_pass_rate",
)


@dataclass(frozen=True)
class DatasetRunSelection:
    experiment_id: str
    run_id: str
    baseline_id: str


@dataclass(frozen=True)
class DatasetSpec:
    dataset_id: str
    runs: tuple[DatasetRunSelection, ...]
    metric_contract: str
    data_status: str
    source_path: Path

    @property
    def experiment_ids(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(selection.experiment_id for selection in self.runs))


@dataclass(frozen=True)
class AnalysisRecord:
    experiment_id: str
    run_id: str
    scenario_id: str
    case_id: str
    agent_id: str
    agent_mode: str
    model: str | None
    repetition: int
    seed: int
    status: str
    attempt: int
    failure_category: str | None
    diagnosis_pass: bool | None
    outcome_pass: bool | None
    safe_pass: bool | None
    valid_for_aggregate: bool


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_spec_path(datasets_root: Path, dataset_id: str) -> Path:
    return datasets_root / f"{validate_identifier(dataset_id, 'dataset_id')}.yaml"


def dataset_lock_path(spec: DatasetSpec) -> Path:
    return spec.source_path.with_suffix(".lock.json")


def create_dataset_spec(
    datasets_root: Path,
    dataset_id: str,
    runs: list[dict[str, str]],
    metric_contract: str,
    data_status: str,
) -> Path:
    dataset_id = validate_identifier(dataset_id, "dataset_id")
    selections = [_parse_run_selection(run, f"dataset_id={dataset_id!r}") for run in runs]
    if not selections:
        raise ValueError("A dataset requires at least one selected run")
    run_ids = [selection.run_id for selection in selections]
    if len(set(run_ids)) != len(run_ids):
        raise ValueError(f"Dataset contains duplicate run_id selections: {run_ids}")
    if not metric_contract.strip():
        raise ValueError("metric_contract must be a non-empty string")
    if data_status not in {"provisional", "audited"}:
        raise ValueError(
            f"data_status must be provisional or audited, got {data_status!r}"
        )
    path = dataset_spec_path(datasets_root, dataset_id)
    if path.exists():
        raise FileExistsError(f"Dataset definition already exists: {path}")
    rendered = yaml.safe_dump(
        {
            "schema_version": DATASET_SCHEMA_VERSION,
            "dataset_id": dataset_id,
            "runs": [
                {
                    "experiment_id": selection.experiment_id,
                    "run_id": selection.run_id,
                    "baseline_id": selection.baseline_id,
                }
                for selection in selections
            ],
            "metric_contract": metric_contract.strip(),
            "data_status": data_status,
        },
        allow_unicode=True,
        sort_keys=False,
    )
    atomic_write_text(path, rendered)
    return path


def _parse_run_selection(data: Any, context: str) -> DatasetRunSelection:
    expected = {"experiment_id", "run_id", "baseline_id"}
    if not isinstance(data, dict) or set(data) != expected:
        fields = sorted(data) if isinstance(data, dict) else type(data).__name__
        raise ValueError(
            f"Dataset run selection fields must be exactly {sorted(expected)}: "
            f"{context}, fields={fields}"
        )
    return DatasetRunSelection(
        experiment_id=validate_identifier(str(data["experiment_id"]), "experiment_id"),
        run_id=_validate_run_id(str(data["run_id"])),
        baseline_id=validate_identifier(str(data["baseline_id"]), "baseline_id"),
    )


def _validate_run_id(value: str) -> str:
    if (
        not value
        or not value[0].isalnum()
        or not value[0].isascii()
        or any(
            not (character.isascii() and (character.isalnum() or character in "_-"))
            for character in value
        )
    ):
        raise ValueError(
            f"run_id must be an ASCII path component containing only letters, digits, "
            f"'_' or '-': value={value!r}"
        )
    return value


def load_dataset_spec(path: str | Path) -> DatasetSpec:
    source_path = Path(path).resolve()
    data = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Dataset definition must be a mapping: path={source_path}")
    expected = {
        "schema_version",
        "dataset_id",
        "runs",
        "metric_contract",
        "data_status",
    }
    if set(data) != expected:
        raise ValueError(
            f"Dataset definition fields must be exactly {sorted(expected)}: "
            f"path={source_path}, fields={sorted(data)}"
        )
    if data["schema_version"] != DATASET_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported dataset schema_version={data['schema_version']!r}: path={source_path}"
        )
    selected_runs = data["runs"]
    if not isinstance(selected_runs, list) or not selected_runs:
        raise ValueError(f"runs must be a non-empty list: path={source_path}")
    runs = tuple(
        _parse_run_selection(selection, f"path={source_path}")
        for selection in selected_runs
    )
    run_ids = [selection.run_id for selection in runs]
    if len(set(run_ids)) != len(run_ids):
        raise ValueError(f"Dataset contains duplicate run_id selections: path={source_path}")
    metric_contract = data["metric_contract"]
    if not isinstance(metric_contract, str) or not metric_contract.strip():
        raise ValueError(f"metric_contract must be a non-empty string: path={source_path}")
    data_status = data["data_status"]
    if data_status not in {"provisional", "audited"}:
        raise ValueError(
            f"data_status must be provisional or audited: path={source_path}, "
            f"value={data_status!r}"
        )
    return DatasetSpec(
        dataset_id=validate_identifier(str(data["dataset_id"]), "dataset_id"),
        runs=runs,
        metric_contract=metric_contract.strip(),
        data_status=data_status,
        source_path=source_path,
    )


def logical_cell(record: AnalysisRecord, baseline_id: str) -> tuple[Any, ...]:
    return (
        record.scenario_id,
        record.case_id,
        baseline_id,
        record.repetition,
        record.seed,
    )


def load_live_entries(spec: DatasetSpec, experiments_root: Path) -> list[dict[str, Any]]:
    records_by_experiment: dict[str, dict[str, dict[str, Any]]] = {}
    for experiment_id in spec.experiment_ids:
        store = ExperimentStore(experiments_root, experiment_id)
        if not store.root.is_dir():
            raise FileNotFoundError(
                f"Dataset source experiment does not exist: dataset_id={spec.dataset_id!r}, "
                f"experiment_id={experiment_id!r}, path={store.root}"
            )
        source_records = {
            path.parent.name: json.loads(path.read_text(encoding="utf-8"))
            for path in store.runs_dir.glob("*/run.json")
        }
        if not source_records:
            raise ValueError(
                f"Dataset source experiment contains no run records: "
                f"dataset_id={spec.dataset_id!r}, experiment_id={experiment_id!r}"
            )
        records_by_experiment[experiment_id] = source_records
    entries = []
    for selection in spec.runs:
        source_records = records_by_experiment[selection.experiment_id]
        if selection.run_id not in source_records:
            raise FileNotFoundError(
                f"Dataset selected run does not exist: dataset_id={spec.dataset_id!r}, "
                f"experiment_id={selection.experiment_id!r}, run_id={selection.run_id!r}"
            )
        run = source_records[selection.run_id]
        record = analysis_record(run, selection.baseline_id)
        if record.experiment_id != selection.experiment_id:
            raise ValueError(
                f"Selected run experiment identity mismatch: dataset_id={spec.dataset_id!r}, "
                f"run_id={selection.run_id!r}, selection={selection.experiment_id!r}, "
                f"record={record.experiment_id!r}"
            )
        entries.append(
            {
                "experiment_id": selection.experiment_id,
                "run_id": selection.run_id,
                "baseline_id": selection.baseline_id,
                "attempt": record.attempt,
                "run": run,
                "artifacts": None,
            }
        )
    seen: dict[tuple[Any, ...], str] = {}
    matrix: dict[tuple[str, str, str], int] = {}
    for entry in entries:
        record = analysis_record(entry["run"], entry["baseline_id"])
        cell = logical_cell(record, entry["baseline_id"])
        if cell in seen:
            raise ValueError(
                f"Dataset source experiments contain duplicate logical cell={cell}: "
                f"run_ids={[seen[cell], record.run_id]}"
            )
        seen[cell] = record.run_id
        matrix[(record.scenario_id, record.case_id, entry["baseline_id"])] = 1
    scenario_cases = {
        (entry["run"]["scenario_id"], entry["run"]["case_id"])
        for entry in entries
    }
    baseline_ids = {entry["baseline_id"] for entry in entries}
    missing = sorted(
        (scenario_id, case_id, baseline_id)
        for scenario_id, case_id in scenario_cases
        for baseline_id in baseline_ids
        if (scenario_id, case_id, baseline_id) not in matrix
    )
    if missing:
        raise ValueError(
            f"Dataset run selections do not form a complete scenario_case x baseline matrix: "
            f"dataset_id={spec.dataset_id!r}, missing={missing}"
        )
    return entries


def analysis_record(run: dict[str, Any], baseline_id: str) -> AnalysisRecord:
    return AnalysisRecord(
        experiment_id=run["experiment_id"],
        run_id=run["run_id"],
        scenario_id=run["scenario_id"],
        case_id=run["case_id"],
        agent_id=baseline_id,
        agent_mode=run["agent_mode"],
        model=run["model"],
        repetition=run["repetition"],
        seed=run["seed"],
        status=run["status"],
        attempt=run["attempt"],
        failure_category=run["failure_category"],
        diagnosis_pass=run["diagnosis_pass"],
        outcome_pass=run["outcome_pass"],
        safe_pass=run["safe_pass"],
        valid_for_aggregate=run["valid_for_aggregate"],
    )


def record_for_analysis(entry: dict[str, Any]) -> AnalysisRecord:
    return analysis_record(entry["run"], entry["baseline_id"])


def records_from_entries(entries: list[dict[str, Any]]) -> list[AnalysisRecord]:
    return [record_for_analysis(entry) for entry in entries]


def load_live_records(spec: DatasetSpec, experiments_root: Path) -> list[AnalysisRecord]:
    return records_from_entries(load_live_entries(spec, experiments_root))


def _artifact_entry(project_root: Path, path: Path) -> dict[str, str]:
    resolved = path.resolve()
    resolved.relative_to(project_root.resolve())
    if not resolved.is_file():
        raise FileNotFoundError(f"Dataset artifact does not exist: path={resolved}")
    return {
        "path": resolved.relative_to(project_root.resolve()).as_posix(),
        "sha256": sha256(resolved),
    }


def _artifact_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        resolved = path.resolve()
    else:
        parts = path.parts
        if "artifacts" in parts:
            path = Path(*parts[parts.index("artifacts"):])
        elif "logs" in parts:
            path = Path(*parts[parts.index("logs"):])
        resolved = (project_root / path).resolve()
    resolved.relative_to(project_root.resolve())
    return resolved


def freeze_dataset(
    spec: DatasetSpec,
    project_root: Path,
    experiments_root: Path,
) -> Path:
    lock_path = dataset_lock_path(spec)
    if lock_path.exists():
        raise FileExistsError(
            f"Frozen dataset is immutable and already exists: dataset_id={spec.dataset_id!r}, "
            f"path={lock_path}"
        )
    selected_entries = load_live_entries(spec, experiments_root)
    entries = []
    for selected_entry in selected_entries:
        run = selected_entry["run"]
        baseline_id = selected_entry["baseline_id"]
        record = analysis_record(run, baseline_id)
        if record.status not in TERMINAL_STATUSES or record.attempt < 1:
            raise ValueError(
                f"Cannot freeze non-terminal run: dataset_id={spec.dataset_id!r}, "
                f"run_id={record.run_id!r}, status={record.status!r}, attempt={record.attempt}"
            )
        attempts = [attempt for attempt in run["attempts"] if attempt["attempt"] == record.attempt]
        if len(attempts) != 1:
            raise ValueError(
                f"Selected attempt metadata is missing or duplicated: run_id={record.run_id!r}, "
                f"attempt={record.attempt}, matches={len(attempts)}"
            )
        attempt = attempts[0]
        artifacts: dict[str, dict[str, str] | None] = {
            "stdout": _artifact_entry(
                project_root,
                _artifact_path(project_root, attempt["stdout_path"]),
            ),
            "trace": None,
            "evaluator": None,
        }
        if record.valid_for_aggregate:
            if attempt["trace_path"] is None or attempt["evaluator_path"] is None:
                raise FileNotFoundError(
                    f"Valid run is missing trace or evaluator artifact metadata: "
                    f"run_id={record.run_id!r}, attempt={record.attempt}"
                )
            artifacts["trace"] = _artifact_entry(
                project_root,
                _artifact_path(project_root, attempt["trace_path"]),
            )
            artifacts["evaluator"] = _artifact_entry(
                project_root,
                _artifact_path(project_root, attempt["evaluator_path"]),
            )
        entries.append(
            {
                "experiment_id": record.experiment_id,
                "run_id": record.run_id,
                "baseline_id": baseline_id,
                "attempt": record.attempt,
                "logical_cell": list(logical_cell(record, baseline_id)),
                "run": run,
                "artifacts": artifacts,
            }
        )
    lock = {
        "schema_version": DATASET_LOCK_SCHEMA_VERSION,
        "dataset_id": spec.dataset_id,
        "metric_contract": spec.metric_contract,
        "data_status": spec.data_status,
        "experiment_ids": list(spec.experiment_ids),
        "frozen_at": now_iso(),
        "runs": entries,
    }
    atomic_write_json(lock_path, lock)
    return lock_path


def load_dataset_lock(spec: DatasetSpec) -> dict[str, Any]:
    path = dataset_lock_path(spec)
    lock = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "schema_version",
        "dataset_id",
        "metric_contract",
        "data_status",
        "experiment_ids",
        "frozen_at",
        "runs",
    }
    if set(lock) != expected:
        raise ValueError(
            f"Dataset lock fields must be exactly {sorted(expected)}: "
            f"path={path}, fields={sorted(lock)}"
        )
    if lock["schema_version"] != DATASET_LOCK_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported dataset lock schema_version={lock['schema_version']!r}: path={path}"
        )
    if lock["dataset_id"] != spec.dataset_id:
        raise ValueError(
            f"Dataset lock identity mismatch: spec={spec.dataset_id!r}, "
            f"lock={lock['dataset_id']!r}, path={path}"
        )
    if lock["metric_contract"] != spec.metric_contract:
        raise ValueError(
            f"Dataset metric contract mismatch: spec={spec.metric_contract!r}, "
            f"lock={lock['metric_contract']!r}, path={path}"
        )
    if lock["data_status"] != spec.data_status:
        raise ValueError(
            f"Dataset data status mismatch: spec={spec.data_status!r}, "
            f"lock={lock['data_status']!r}, path={path}"
        )
    return lock


def verify_dataset_lock(spec: DatasetSpec, project_root: Path) -> None:
    lock = load_dataset_lock(spec)
    for entry in lock["runs"]:
        for artifact_name, artifact in entry["artifacts"].items():
            if artifact is None:
                continue
            path = (project_root / artifact["path"]).resolve()
            path.relative_to(project_root.resolve())
            actual = sha256(path)
            if actual != artifact["sha256"]:
                raise ValueError(
                    f"Dataset artifact hash mismatch: dataset_id={spec.dataset_id!r}, "
                    f"run_id={entry['run_id']!r}, attempt={entry['attempt']}, "
                    f"artifact={artifact_name!r}, expected={artifact['sha256']!r}, "
                    f"actual={actual!r}, path={path}"
                )


def records_from_lock(spec: DatasetSpec) -> list[AnalysisRecord]:
    lock = load_dataset_lock(spec)
    return records_from_entries(lock["runs"])


def _stats(records: list[AnalysisRecord | RunRecord]) -> dict[str, Any]:
    valid = [record for record in records if record.valid_for_aggregate]
    for record in valid:
        if None in (record.outcome_pass, record.safe_pass):
            raise ValueError(
                f"Valid run lacks DP/OP/SP results: run_id={record.run_id!r}, "
                f"outcome_pass={record.outcome_pass!r}, safe_pass={record.safe_pass!r}"
            )
    infrastructure_failures = sum(
        record.failure_category in INFRASTRUCTURE_FAILURE_CATEGORIES
        for record in records
    )
    return {
        "runs": len(records),
        "valid_runs": len(valid),
        "execution_failures": sum(record.status != "succeeded" for record in records),
        "infrastructure_failure_rate": (
            infrastructure_failures / len(records) if records else 0.0
        ),
        "diagnosis_pass_rate": (
            sum(record.diagnosis_pass is True for record in valid if record.diagnosis_pass is not None)
            / sum(record.diagnosis_pass is not None for record in valid)
            if any(record.diagnosis_pass is not None for record in valid) else None
        ),
        "outcome_pass_rate": (
            sum(record.outcome_pass is True for record in valid) / len(valid)
            if valid else None
        ),
        "safe_pass_rate": (
            sum(record.safe_pass is True for record in valid) / len(valid)
            if valid else None
        ),
    }


def aggregate_dataset(records: list[AnalysisRecord | RunRecord]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[AnalysisRecord | RunRecord]] = {}
    for record in records:
        groups.setdefault((record.scenario_id, record.agent_id), []).append(record)
    scenario_agents = [
        {
            "scenario_id": scenario_id,
            "agent_id": agent_id,
            **_stats(items),
        }
        for (scenario_id, agent_id), items in sorted(groups.items())
    ]
    return {"summary": _stats(records), "scenario_agents": scenario_agents}


def build_dataset_outputs(
    spec: DatasetSpec,
    project_root: Path,
    output_root: Path,
) -> Path:
    verify_dataset_lock(spec, project_root)
    lock = load_dataset_lock(spec)
    records = records_from_entries(lock["runs"])
    from .run_table import build_run_rows, write_runs_csv

    run_rows = build_run_rows(spec, project_root)
    root = output_root / spec.dataset_id
    root.mkdir(parents=True, exist_ok=True)
    atomic_write_text(
        root / "runs.jsonl",
        "\n".join(json.dumps(row, ensure_ascii=False) for row in run_rows) + "\n",
    )
    write_runs_csv(root / "runs.csv", run_rows)

    aggregate = aggregate_dataset(records)
    atomic_write_json(root / "aggregate.json", aggregate)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=SUMMARY_FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(aggregate["scenario_agents"])
    atomic_write_text(root / "scenario_agent_summary.csv", output.getvalue())
    atomic_write_json(
        root / "provenance.json",
        {
            "dataset_id": spec.dataset_id,
            "metric_contract": spec.metric_contract,
            "data_status": spec.data_status,
            "dataset_lock_sha256": sha256(dataset_lock_path(spec)),
            "built_at": now_iso(),
        },
    )
    return root


def diff_dataset_locks(before: DatasetSpec, after: DatasetSpec) -> dict[str, Any]:
    before_entries = {
        tuple(entry["logical_cell"]): entry for entry in load_dataset_lock(before)["runs"]
    }
    after_entries = {
        tuple(entry["logical_cell"]): entry for entry in load_dataset_lock(after)["runs"]
    }
    before_cells = set(before_entries)
    after_cells = set(after_entries)
    replaced = []
    for cell in sorted(before_cells & after_cells):
        left = before_entries[cell]
        right = after_entries[cell]
        if (
            left["experiment_id"],
            left["run_id"],
            left["attempt"],
            json.dumps(left["run"], sort_keys=True),
        ) != (
            right["experiment_id"],
            right["run_id"],
            right["attempt"],
            json.dumps(right["run"], sort_keys=True),
        ):
            replaced.append(
                {
                    "logical_cell": list(cell),
                    "before": {
                        "experiment_id": left["experiment_id"],
                        "run_id": left["run_id"],
                        "attempt": left["attempt"],
                    },
                    "after": {
                        "experiment_id": right["experiment_id"],
                        "run_id": right["run_id"],
                        "attempt": right["attempt"],
                    },
                }
            )
    return {
        "before": before.dataset_id,
        "after": after.dataset_id,
        "added": [list(cell) for cell in sorted(after_cells - before_cells)],
        "removed": [list(cell) for cell in sorted(before_cells - after_cells)],
        "replaced": replaced,
    }
