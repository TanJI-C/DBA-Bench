"""PostgreSQL PersistentScenario target adapter for benchmark planning and commands."""

from __future__ import annotations

import sys
from pathlib import Path

from src.persistent_scenarios.api import build_postgres_backend, build_tidb_backend
from src.persistent_scenarios.model.calibration import require_validated_calibration
from src.database.system import DatabaseSystem
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.project_paths import CALIBRATION_ARTIFACT_ROOT, SOURCE_ROOT, persistent_scenario_definition_roots

from ..manifest import ExperimentManifest
from ..models import PersistentScenarioRunSpec, ScenarioKind


def persistent_scenario_definition_path(scenario_id: str, project_root: Path = SOURCE_ROOT) -> Path:
    candidates = [
        root / f"{scenario_id}.yaml"
        for root in persistent_scenario_definition_roots(project_root)
    ]
    existing = [path for path in candidates if path.is_file()]
    if len(existing) != 1:
        raise FileNotFoundError(
            "PersistentScenario definition must exist in exactly one system root: "
            f"scenario_id={scenario_id!r}, candidates={[str(path) for path in candidates]}"
        )
    return existing[0]


def validate_persistent_scenario_target(persistent_scenario, manifest: ExperimentManifest) -> None:
    if manifest.runtime.run_mode == "formal":
        require_validated_calibration(persistent_scenario, CALIBRATION_ARTIFACT_ROOT)
    if persistent_scenario.system is DatabaseSystem.TIDB:
        build_tidb_backend(persistent_scenario)  # validate_spec runs inside
    elif persistent_scenario.system is DatabaseSystem.POSTGRESQL:
        build_postgres_backend(persistent_scenario).validate_spec(persistent_scenario)
    else:
        raise ValueError(
            "PersistentScenario benchmark adapter has no backend capability validator for system: "
            f"scenario_id={persistent_scenario.scenario_id!r}, system={persistent_scenario.system.value!r}"
        )


def plan_persistent_scenario_runs(manifest: ExperimentManifest) -> list[PersistentScenarioRunSpec]:
    if manifest.benchmark.scenario_kind is not ScenarioKind.PERSISTENT:
        raise ValueError(
            "plan_persistent_scenario_runs requires scenario_kind=persistent: "
            f"scenario_kind={manifest.benchmark.scenario_kind.value!r}"
        )
    runs = []
    index = 0
    for scenario_id in manifest.benchmark.scenarios:
        path = persistent_scenario_definition_path(scenario_id)
        persistent_scenario = load_persistent_scenario(path)
        validate_persistent_scenario_target(persistent_scenario, manifest)
        backend = (build_tidb_backend(persistent_scenario) if persistent_scenario.system is DatabaseSystem.TIDB
                   else build_postgres_backend(persistent_scenario))
        host_ports = backend.environment.host_ports(persistent_scenario)
        for agent in manifest.agents:
            for repetition, seed in enumerate(manifest.seeds, start=1):
                run_id = "__".join((
                    manifest.experiment_id,
                    "persistent-scenario",
                    persistent_scenario.scenario_id,
                    agent.id,
                    f"r{repetition:03d}",
                ))
                runs.append(PersistentScenarioRunSpec(
                    experiment_id=manifest.experiment_id,
                    run_id=run_id,
                    scenario_id=persistent_scenario.scenario_id,
                    system=persistent_scenario.system,
                    agent=agent,
                    repetition=repetition,
                    seed=seed,
                    port=manifest.runtime.port_base + index,
                    resources=persistent_scenario.environment.nodes[0].resources,
                    host_ports=host_ports,
                ))
                index += 1
    if not runs:
        raise ValueError("PersistentScenario benchmark plan contains no runs")
    return runs


def build_persistent_scenario_command(
    spec: PersistentScenarioRunSpec,
    manifest: ExperimentManifest,
    project_root: Path = SOURCE_ROOT,
) -> list[str]:
    persistent_scenario_path = persistent_scenario_definition_path(spec.scenario_id, project_root)
    command = [
        sys.executable,
        "-m",
        "src.cli",
        "persistent-scenario",
        "run",
        str(persistent_scenario_path),
        "--agent",
        spec.agent.mode,
        "--run-id",
        spec.run_id,
        "--port",
        str(spec.port),
    ]
    if spec.agent.model:
        command.extend(["--model", spec.agent.model])
    command.extend(["--llm-config", manifest.runtime.llm_config])
    command.extend(["--max-turns", str(spec.agent.max_turns)])
    if spec.agent.max_output_tokens is not None:
        command.extend(["--max-output-tokens", str(spec.agent.max_output_tokens)])
    if spec.agent.reasoning_effort is not None:
        command.extend(["--reasoning-effort", spec.agent.reasoning_effort])
    command.extend(["--run-mode", manifest.runtime.run_mode])
    command.extend(["--time-scale", str(manifest.runtime.time_scale)])
    return command
