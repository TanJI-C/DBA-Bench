"""Stable public API for benchmark manifests, planning, execution and artifacts."""

from .aggregate import aggregate, load_records, write_aggregate
from .dataset import (
    aggregate_dataset,
    build_dataset_outputs,
    create_dataset_spec,
    dataset_lock_path,
    dataset_spec_path,
    diff_dataset_locks,
    freeze_dataset,
    load_dataset_spec,
    load_live_records,
    records_from_lock,
    sha256,
    verify_dataset_lock,
)
from .manifest import ExperimentManifest, load_manifest, validate_identifier
from .models import BoundedScenarioRunSpec, PersistentScenarioRunSpec, RunRecord, ScenarioKind
from .planner import plan_runs, select_specs
from .runner import ExperimentRunner, validate_execution_plan
from .store import ExperimentStore

__all__ = (
    "BoundedScenarioRunSpec",
    "ExperimentManifest",
    "ExperimentRunner",
    "ExperimentStore",
    "RunRecord",
    "PersistentScenarioRunSpec",
    "ScenarioKind",
    "aggregate",
    "aggregate_dataset",
    "build_dataset_outputs",
    "create_dataset_spec",
    "dataset_lock_path",
    "dataset_spec_path",
    "diff_dataset_locks",
    "freeze_dataset",
    "load_dataset_spec",
    "load_live_records",
    "load_manifest",
    "load_records",
    "plan_runs",
    "records_from_lock",
    "select_specs",
    "sha256",
    "validate_execution_plan",
    "validate_identifier",
    "verify_dataset_lock",
    "write_aggregate",
)
