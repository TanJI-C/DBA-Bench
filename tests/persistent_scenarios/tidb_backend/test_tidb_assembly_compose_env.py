"""Assembly-side compose/exec routes through the deployment single-path env.

``DeferredTiKVStore`` must not build a parallel compose command line or a
parallel child environment: every assembly-side compose invocation (the
deferred-store ``rm``/``create``/``start`` lifecycle) goes through
``TiDBPersistentDeployment.run_compose``, which builds the command with
``self._compose`` (lazily loading ``DOCKER_ROOT_DIR`` for the cadvisor volume
interpolation) and runs the child with ``env=self._env``.
"""

from pathlib import Path
from types import SimpleNamespace

from src.execution.tidb_persistent_deployment import TiDBPersistentDeployment
from src.persistent_scenarios.backend.tidb.assembly import DeferredTiKVStore
from src.persistent_scenarios.backend.tidb.topology import expand_topology
from src.persistent_scenarios.model.spec import NodeSpec, PersistentScenarioEnvironmentSpec, PersistentScenarioResourceSpec

PD_IMAGE = "pingcap/pd@sha256:78f5de9dc59abd02c99056294fb51f29da39ed932eb92cb2570ad57fe0774e80"
TIKV_IMAGE = "pingcap/tikv@sha256:0b9d00f2b4f60cd3f91b55720a737136643e17bfb4de82a3c30ca532430374a5"
TIDB_IMAGE = "pingcap/tidb@sha256:ee98d7d09ea2dcdc76dd683de3c3cdd63f052b33a91f5645ab75609df3648501"

_IMAGES = {"pd": PD_IMAGE, "tikv": TIKV_IMAGE, "tidb": TIDB_IMAGE}


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
        run_id="tidb5-backend-integration-compose-env", port_base=26000, topology=topology,
        data_root=tmp_path / "data", enable_monitoring=enable_monitoring,
    )


def test_deferred_store_compose_runs_child_with_the_deployment_env(tmp_path, monkeypatch):
    monkeypatch.delenv("DOCKER_ROOT_DIR", raising=False)
    deployment = _deployment(tmp_path, enable_monitoring=True)
    calls: list[tuple[list[str], dict[str, str] | None]] = []

    def fake_run(cmd, **kwargs):
        calls.append((list(cmd), kwargs["env"]))
        if cmd[:2] == ["docker", "info"]:
            return SimpleNamespace(returncode=0, stdout="/var/lib/docker\n", stderr="")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("src.execution.tidb_persistent_deployment.subprocess.run", fake_run)

    deferred = DeferredTiKVStore(deployment)
    deferred.compose("rm", "--force", "tikv-3")

    compose_calls = [(cmd, env) for cmd, env in calls if cmd[:2] == ["docker", "compose"]]
    assert len(compose_calls) == 1
    cmd, env = compose_calls[0]
    # The child env IS the deployment env, with the lazily loaded
    # DOCKER_ROOT_DIR present; the command is the deployment's own compose line.
    assert env is deployment._env
    assert env["DOCKER_ROOT_DIR"] == "/var/lib/docker"
    assert cmd[:6] == ["docker", "compose", "--project-name", deployment.project_name,
                       "--file", str(deployment.compose_file)]
    assert cmd[6:] == ["rm", "--force", "tikv-3"]


def test_deferred_store_prepare_routes_rm_and_create_through_run_compose(tmp_path, monkeypatch):
    deployment = _deployment(tmp_path, enable_monitoring=False)
    deferred = DeferredTiKVStore(deployment)

    stores_payloads = [
        {"stores": [{"store": {"id": "5", "address": "tikv-3:20160", "state_name": "Up"}}]},
        {"stores": [{"store": {"id": "5", "address": "tikv-3:20160", "state_name": "Tombstone"}}]},
    ]
    pd_calls: list[tuple[str, str]] = []
    compose_args: list[tuple[str, ...]] = []
    exec_calls: list[tuple[str, list[str]]] = []
    manage_calls: list[tuple[str, str]] = []

    def fake_pd_request(method, path, body=None):
        pd_calls.append((method, path))
        if method == "GET":
            return stores_payloads.pop(0)
        return {}

    monkeypatch.setattr(deployment, "pd_request", fake_pd_request)
    monkeypatch.setattr(deployment, "run_compose", lambda *args, timeout=120: compose_args.append(args) or "")
    monkeypatch.setattr(
        deployment, "exec_command",
        lambda service, command, timeout=30: exec_calls.append((service, command)) or "",
    )
    monkeypatch.setattr(
        deployment, "manage_service",
        lambda action, service: manage_calls.append((action, service)) or None,
    )

    result = deferred.prepare("tikv-3")

    assert result == {"service": "tikv-3", "old_store_id": 5, "state": "deferred"}
    assert compose_args == [("rm", "--force", "tikv-3"), ("create", "tikv-3")]
    assert manage_calls == [("stop", "tikv-3")]
    assert [(service, command[0]) for service, command in exec_calls] == [("pd-0", "/pd-ctl")]


def test_deferred_tikv_start_is_idempotent_when_agent_started_the_service() -> None:
    """The agent may lawfully start the reserved service through its own
    instance-manage surface before the arrival event. The event must reuse
    the live store, re-apply the zone label, and wait for Up — not fail."""
    from src.persistent_scenarios.backend.tidb.assembly import DeferredTiKVStore

    class _FakeTopology:
        @staticmethod
        def role_services(role):
            return ["tikv-0", "tikv-1", "tikv-2", "tikv-3"]

    class _FakeDeployment:
        topology = _FakeTopology()

        def __init__(self):
            self.stores_payload = {"stores": [
                {"store": {"id": 7, "address": "tikv-3:20160", "state_name": "Up",
                            "labels": [{"key": "zone", "value": "zone4"}]}},
            ]}
            self.compose_calls = []
            self.label_calls = []

        def pd_request(self, method, path, body=None):
            if method == "GET" and path == "/pd/api/v1/stores":
                return self.stores_payload
            if method == "POST" and "/label" in path:
                self.label_calls.append(path)
                return {}
            raise AssertionError(f"unexpected pd_request: {method} {path}")

        def run_compose(self, *args, timeout=120):
            self.compose_calls.append(args)
            return ""

    deployment = _FakeDeployment()
    deferred = DeferredTiKVStore(deployment)  # type: ignore[arg-type]
    deferred._prepared.add("tikv-3")
    result = deferred.start("tikv/tikv-3")
    assert result == {"target": "tikv/tikv-3", "state": "Up", "store_id": 7}
    assert deployment.compose_calls == [], "a running store must not be started again"
    assert deployment.label_calls, "the zone label must be re-applied"


def test_deferred_tikv_start_starts_when_no_store_registered() -> None:
    from src.persistent_scenarios.backend.tidb.assembly import DeferredTiKVStore

    class _FakeTopology:
        @staticmethod
        def role_services(role):
            return ["tikv-0", "tikv-1", "tikv-2", "tikv-3"]

    class _FakeDeployment:
        topology = _FakeTopology()

        def __init__(self):
            self.stores_payload = {"stores": []}
            self.compose_calls = []

        def pd_request(self, method, path, body=None):
            if method == "GET" and path == "/pd/api/v1/stores":
                return self.stores_payload
            if method == "POST" and "/label" in path:
                return {}
            raise AssertionError(f"unexpected pd_request: {method} {path}")

        def run_compose(self, *args, timeout=120):
            self.compose_calls.append(args)
            self.stores_payload = {"stores": [
                {"store": {"id": 8, "address": "tikv-3:20160", "state_name": "Up",
                            "labels": [{"key": "zone", "value": "zone4"}]}},
            ]}
            return ""

    deployment = _FakeDeployment()
    deferred = DeferredTiKVStore(deployment)  # type: ignore[arg-type]
    deferred._prepared.add("tikv-3")
    result = deferred.start("tikv/tikv-3")
    assert result == {"target": "tikv/tikv-3", "state": "Up", "store_id": 8}
    assert ("start", "tikv-3") in deployment.compose_calls
