"""Deferred-store compose commands run through the deployment env.

Assembly-side compose invocations must not build a parallel environment:
without ``DOCKER_ROOT_DIR`` in the child env the compose interpolation fails
with ``required variable DOCKER_ROOT_DIR is missing a value``. The single
path is ``TiDBPersistentDeployment.run_compose`` — it builds the command with
``self._compose`` (which lazily loads ``DOCKER_ROOT_DIR`` when monitoring is
enabled) and executes it with ``env=self._env``.
"""

from pathlib import Path
from types import SimpleNamespace

import pytest

from src.execution.tidb_persistent_deployment import (
    TiDBPersistentDeployment,
    TiDBPersistentDeploymentError,
)
from src.persistent_scenarios.backend.tidb.topology import expand_topology
from src.persistent_scenarios.model.spec import NodeSpec, PersistentScenarioEnvironmentSpec, PersistentScenarioResourceSpec

PD_IMAGE = "pingcap/pd@sha256:78f5de9dc59abd02c99056294fb51f29da39ed932eb92cb2570ad57fe0774e80"
TIKV_IMAGE = "pingcap/tikv@sha256:0b9d00f2b4f60cd3f91b55720a737136643e17bfb4de82a3c30ca532430374a5"
TIDB_IMAGE = "pingcap/tidb@sha256:ee98d7d09ea2dcdc76dd683de3c3cdd63f052b33a91f5645ab75609df3648501"

_IMAGES = {"pd": PD_IMAGE, "tikv": TIKV_IMAGE, "tidb": TIDB_IMAGE}

_COMPOSE_STDERR = (
    "error while interpolating services.cadvisor.volumes.[]: required variable "
    "DOCKER_ROOT_DIR is missing a value: DOCKER_ROOT_DIR is required"
)


def _node(role: str, index: int) -> NodeSpec:
    return NodeSpec(
        node_id=f"{role}-{index}", role=role,
        resources=PersistentScenarioResourceSpec(
            worker_physical_cores=1, worker_memory_mb=2048,
            container_cpu_limit=1.0, container_memory_mb=2048,
        ),
    )


def _deployment(tmp_path: Path, *, enable_monitoring: bool) -> TiDBPersistentDeployment:
    environment = SimpleNamespace(environment=PersistentScenarioEnvironmentSpec(
        workload="portfolio", scale=1, base_image="unused",
        nodes=(
            _node("pd", 0),
            *(_node("tikv", index) for index in range(4)),
            _node("tidb", 0),
        ),
    ))
    topology = expand_topology(environment, release_images=_IMAGES, data_dir=str(tmp_path / "data"))
    return TiDBPersistentDeployment(
        run_id="tidb5-backend-compose-env", port_base=26000, topology=topology,
        data_root=tmp_path / "data", enable_monitoring=enable_monitoring,
    )


def _fake_docker(monkeypatch, *, info_stdout: str = "/var/lib/docker\n", returncode: int = 0):
    calls: list[tuple[list[str], dict[str, str] | None]] = []

    def fake_run(cmd, **kwargs):
        env = kwargs["env"]
        calls.append((list(cmd), env))
        if cmd[:2] == ["docker", "info"]:
            return SimpleNamespace(returncode=0, stdout=info_stdout, stderr="")
        return SimpleNamespace(returncode=returncode, stdout="", stderr=_COMPOSE_STDERR)

    monkeypatch.setattr("src.execution.tidb_persistent_deployment.subprocess.run", fake_run)
    return calls


def test_run_compose_deferred_store_rm_start_child_env_carries_docker_root_dir(tmp_path, monkeypatch):
    monkeypatch.delenv("DOCKER_ROOT_DIR", raising=False)
    deployment = _deployment(tmp_path, enable_monitoring=True)
    calls = _fake_docker(monkeypatch)

    deployment.run_compose("rm", "--force", "tikv-3")
    deployment.run_compose("start", "tikv-3")

    compose_calls = [(cmd, env) for cmd, env in calls if cmd[:2] == ["docker", "compose"]]
    assert [cmd[6:] for cmd, _ in compose_calls] == [
        ["rm", "--force", "tikv-3"],
        ["start", "tikv-3"],
    ]
    for cmd, env in compose_calls:
        assert cmd[:6] == ["docker", "compose", "--project-name", deployment.project_name,
                           "--file", str(deployment.compose_file)]
        # The child env IS the deployment env (never a parallel one) and the
        # lazily loaded DOCKER_ROOT_DIR is present for the cadvisor volume
        # interpolation.
        assert env is deployment._env
        assert env["DOCKER_ROOT_DIR"] == "/var/lib/docker"
    assert sum(1 for cmd, _ in calls if cmd[:2] == ["docker", "info"]) == 1


def test_run_compose_without_monitoring_requires_no_docker_root_dir(tmp_path, monkeypatch):
    monkeypatch.delenv("DOCKER_ROOT_DIR", raising=False)
    deployment = _deployment(tmp_path, enable_monitoring=False)
    calls = _fake_docker(monkeypatch)

    deployment.run_compose("rm", "--force", "tikv-3")
    deployment.run_compose("start", "tikv-3")

    # No monitoring stack in the compose file: no docker info lookup and no
    # DOCKER_ROOT_DIR requirement anywhere on the path.
    assert all(cmd[:2] != ["docker", "info"] for cmd, _ in calls)
    for cmd, env in calls:
        assert cmd[:2] == ["docker", "compose"]
        assert "DOCKER_ROOT_DIR" not in env
        assert env is deployment._env


def test_run_compose_failure_names_command_and_project(tmp_path, monkeypatch):
    monkeypatch.delenv("DOCKER_ROOT_DIR", raising=False)
    deployment = _deployment(tmp_path, enable_monitoring=True)
    _fake_docker(monkeypatch, returncode=1)

    with pytest.raises(TiDBPersistentDeploymentError) as excinfo:
        deployment.run_compose("rm", "--force", "tikv-3")
    message = str(excinfo.value)
    assert repr(("rm", "--force", "tikv-3")) in message
    assert deployment.project_name in message
    assert "DOCKER_ROOT_DIR is missing a value" in message
