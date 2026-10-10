from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest

SCENARIO_PATH = Path("src/persistent_scenarios/postgres/pg_continuous_ops_smoke.yaml")


def test_persistent_scenario_gate_requires_worker_cpuset_and_storage(monkeypatch):
    cli = importlib.import_module("src.cli")
    from src.persistent_scenarios.api import load_definition

    spec = load_definition(SCENARIO_PATH)
    monkeypatch.delenv("AIOPS_CPUSET_CPUS", raising=False)
    monkeypatch.delenv("AIOPS_CPUSET_MEMS", raising=False)
    monkeypatch.delenv("AIOPS_POSTGRES_STORAGE_ROOT", raising=False)

    with pytest.raises(RuntimeError, match="explicit worker resource contract"):
        cli._configure_persistent_scenario_gate_resources(
            spec, cpuset_cpus=None, cpuset_mems=None, postgres_storage_root=None,
        )


def test_persistent_scenario_gate_exports_declared_container_limits(monkeypatch):
    cli = importlib.import_module("src.cli")
    from src.persistent_scenarios.api import load_definition

    spec = load_definition(SCENARIO_PATH)
    monkeypatch.setattr(cli, "_run_persistent_scenario_engine", lambda engine, output_dir: {
        "valid": True, "BaselinePass": True, "gate_result": {"sequence_pass": True},
    })

    code = cli.validate_persistent_scenario_gate(
        SCENARIO_PATH,
        gate="healthy",
        run_id="gate-resources-test",
        port=25300,
        time_scale=30.0,
        cpuset_cpus="2-5",
        cpuset_mems="0",
        postgres_storage_root="/tmp/pg5r-gate",
    )

    assert code == 0
    assert os.environ["AIOPS_CPUSET_CPUS"] == "2-5"
    assert os.environ["AIOPS_POSTGRES_STORAGE_ROOT"] == "/tmp/pg5r-gate"
    assert os.environ["AIOPS_CPU_LIMIT"] == "2.0"
    assert os.environ["AIOPS_MEMORY_MB"] == "2048"
