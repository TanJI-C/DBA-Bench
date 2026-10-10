"""Narrow public composition API for PostgreSQL Persistent Scenario runs."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .backend.contracts import PersistentScenarioBackend
    from .backend.postgres.backend import PostgresPersistentScenarioBackend
    from .backend.tidb.assembly import TiDBPersistentScenarioBackend

from .evaluation import PersistentScenarioEvaluator
from .model.loader import load_persistent_scenario
from .model.spec import PersistentScenarioSpec
from .runtime.clock import Clock, RealClock
from .runtime.engine import PersistentScenarioEngine


def load_definition(path: str | Path) -> PersistentScenarioSpec:
    return load_persistent_scenario(path)


def build_postgres_backend(
    spec: PersistentScenarioSpec | None = None,
    *,
    evidence_root: str | Path | None = None,
) -> "PostgresPersistentScenarioBackend":
    from .backend.postgres.backend import PostgresPersistentScenarioBackend

    return PostgresPersistentScenarioBackend(spec, evidence_root=evidence_root)


def build_tidb_backend(spec: "PersistentScenarioSpec") -> "TiDBPersistentScenarioBackend":
    """Assemble the TiDB Persistent Scenario backend for one instance spec.

    Divergence from ``build_postgres_backend``: no ``evidence_root`` parameter —
    the TiDB assembly keeps run evidence (trusted ledgers) under the deployment
    data root, so it has no consumer for one.
    """
    from src.execution.tidb_persistent_deployment import DATA_ROOT as TIDB_PERSISTENT_DATA_ROOT

    from .backend.tidb.assembly import (
        TiDBAssemblyEnvironmentProvider,
        build_tidb_backend as build_assembly_tidb_backend,
    )

    # The public entry is agent-facing: query_metrics needs the Prometheus
    # monitoring stack, so monitoring is always enabled here.
    provider = TiDBAssemblyEnvironmentProvider(
        data_root=TIDB_PERSISTENT_DATA_ROOT, enable_monitoring=True
    )
    return build_assembly_tidb_backend(spec, environment_provider=provider)


def build_persistent_scenario_evaluator() -> PersistentScenarioEvaluator:
    return PersistentScenarioEvaluator()


def build_real_clock() -> Clock:
    return RealClock()


def build_persistent_scenario_engine(
    spec: PersistentScenarioSpec,
    backend: "PersistentScenarioBackend",
    agent_factory: Callable,
    *,
    run_id: str,
    port: int,
    clock: Clock,
    output_dir: str | None = None,
    run_mode: str = "development",
    time_scale: float = 1.0,
    event_activation: bool = True,
    evaluation_mode: str = "persistent_scenario",
    gate_name: str | None = None,
    trusted_checkpoint_observer=None,
) -> PersistentScenarioEngine:
    return PersistentScenarioEngine(
        spec,
        backend,
        agent_factory,
        evaluation_provider=build_persistent_scenario_evaluator(),
        run_id=run_id,
        port=port,
        clock=clock,
        output_dir=output_dir,
        run_mode=run_mode,
        time_scale=time_scale,
        event_activation=event_activation,
        evaluation_mode=evaluation_mode,
        gate_name=gate_name,
        trusted_checkpoint_observer=trusted_checkpoint_observer,
    )


__all__ = (
    "build_persistent_scenario_engine",
    "build_persistent_scenario_evaluator",
    "build_postgres_backend",
    "build_tidb_backend",
    "build_real_clock",
    "load_definition",
)
