"""Focused tests for the public TiDB Persistent Scenario entry wiring.

Covers ``api.build_tidb_backend``, the benchmark adapter's tidb dispatch, the
manifest schema's ``real-model`` agent mode and the CLI ``real-model`` mode.
No Docker: backend assembly and spec validation are pure composition.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.benchmark.adapters.persistent_scenario import validate_persistent_scenario_target
from src.benchmark.manifest import BenchmarkSpec, ExperimentManifest, load_manifest
from src.benchmark.models import AgentSpec, RuntimeSpec, ScenarioKind
from src.cli import run_persistent_scenario_command
from src.persistent_scenarios.api import build_tidb_backend
from src.persistent_scenarios.backend.tidb.assembly import TiDBPersistentScenarioBackend
from src.persistent_scenarios.model.enums import DatabaseSystem
from src.persistent_scenarios.model.loader import load_persistent_scenario

WORKTREE = Path(__file__).resolve().parents[2]
HOTSPOT_YAML = WORKTREE / "src" / "persistent_scenarios" / "tidb" / "tidb_oltp_hotspot_resilience.yaml"


def _development_manifest(scenario_ids: tuple[str, ...]) -> ExperimentManifest:
    return ExperimentManifest(
        experiment_id="tidb5-backend-entry-test",
        benchmark=BenchmarkSpec(
            scenario_kind=ScenarioKind.PERSISTENT,
            systems=(),
            categories=(),
            scenarios=scenario_ids,
        ),
        agents=(AgentSpec(
            id="real-model-a", mode="real-model", model="test-model-a", max_turns=60
        ),),
        exclude_cells=frozenset(),
        repetitions=1,
        seeds=(20260920,),
        runtime=RuntimeSpec(run_mode="development", time_scale=1.0),
        source_path=WORKTREE,
        raw={},
    )


def test_api_build_tidb_backend_assembles_and_validates_instance_spec():
    spec = load_persistent_scenario(HOTSPOT_YAML)

    backend = build_tidb_backend(spec)

    assert isinstance(backend, TiDBPersistentScenarioBackend)
    # validate_spec runs inside build_tidb_backend: a non-tidb spec of the same
    # instance must fail there. Main's spec validation rejects the TB- citation
    # tag against system=postgresql before the backend-specific tidb check.
    with pytest.raises(ValueError, match="citation_tag system prefix mismatch"):
        build_tidb_backend(replace(spec, system=DatabaseSystem.POSTGRESQL))


def test_validate_persistent_scenario_target_dispatches_tidb():
    spec = load_persistent_scenario(HOTSPOT_YAML)

    validate_persistent_scenario_target(spec, _development_manifest((spec.scenario_id,)))


def test_validate_persistent_scenario_target_rejects_unsupported_system():
    unsupported = SimpleNamespace(
        scenario_id="foreign_instance", system=SimpleNamespace(value="mysql")
    )

    with pytest.raises(ValueError, match="system='mysql'"):
        validate_persistent_scenario_target(
            unsupported, _development_manifest(("tidb_oltp_hotspot_resilience",))
        )


def test_manifest_accepts_llm_agent_mode(tmp_path):
    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text(
        """
experiment_id: tidb5-backend-entry-manifest
benchmark:
  scenario_kind: persistent
  scenarios: [tidb_oltp_hotspot_resilience]
agents:
  - id: llm-a
    mode: llm
    model: test-model-a
    max_turns: 60
repetitions: 1
seeds: [20260922]
runtime:
  concurrency: 1
  timeout_seconds: 14400
  port_base: 26300
  run_mode: development
  time_scale: 1
  llm_config: /tmp/llm_config.json
""".strip(),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)

    assert manifest.agents[0].mode == "llm"
    assert manifest.agents[0].model == "test-model-a"
    assert manifest.agents[0].max_turns == 60


def test_cli_llm_mode_builds_agent_and_hands_factory_to_engine(monkeypatch, tmp_path):
    built = {}
    stub_client = SimpleNamespace()
    stub_agent = SimpleNamespace()
    captured = {}

    def fake_llm_agent(**kwargs):
        built["args"] = kwargs
        return stub_client

    def fake_from_llm_client(client, *, max_turns):
        built["max_turns"] = max_turns
        return stub_agent

    def fake_build_engine(spec, backend, agent_factory, **kwargs):
        captured["backend"] = backend
        captured["agent_factory"] = agent_factory
        captured["kwargs"] = kwargs
        return SimpleNamespace()

    monkeypatch.setattr("src.agents.agent.LLMAgent", fake_llm_agent)
    monkeypatch.setattr(
        "src.agents.persistent_scenario_agent.LLMPersistentScenarioAgent.from_llm_client",
        staticmethod(fake_from_llm_client),
    )
    monkeypatch.setattr("src.persistent_scenarios.api.build_persistent_scenario_engine", fake_build_engine)
    monkeypatch.setattr("src.cli._run_persistent_scenario_engine", lambda engine, output_dir: {"valid": True})

    exit_code = run_persistent_scenario_command(
        HOTSPOT_YAML,
        agent_name="llm",
        run_id="tidb5-backend-entry-test-run",
        port=26100,
        output_dir=tmp_path / "trace",
        max_turns=60,
        model="test-model-a",
        llm_config="/tmp/llm_config.json",
    )

    assert exit_code == 0
    assert isinstance(captured["backend"], TiDBPersistentScenarioBackend)
    assert captured["agent_factory"](None) is stub_agent
    assert built["args"]["config_path"] == "/tmp/llm_config.json"
    assert built["args"]["model"] == "test-model-a"
    assert built["max_turns"] == 60
    assert captured["kwargs"]["run_id"] == "tidb5-backend-entry-test-run"
    assert captured["kwargs"]["port"] == 26100
    assert captured["kwargs"]["output_dir"] == str(tmp_path / "trace")
    assert captured["kwargs"]["run_mode"] == "development"
    assert captured["kwargs"]["time_scale"] == 1.0
