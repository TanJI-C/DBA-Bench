"""NodeSpec expansion and deployment-plan tests (pure, no docker)."""

from pathlib import Path
from types import SimpleNamespace

import yaml

from src.execution.tidb_persistent_deployment import (
    PORT_RANGE,
    PersistentTiDBNodePlan,
    TiDBPersistentDeployment,
    build_port_plan,
)
from src.persistent_scenarios.model.spec import (
    NodeSpec,
    NodeVolume,
    PersistentScenarioEnvironmentSpec,
    PersistentScenarioResourceSpec,
)
from src.persistent_scenarios.backend.tidb import expand_topology

PD_IMAGE = "pingcap/pd@sha256:78f5de9dc59abd02c99056294fb51f29da39ed932eb92cb2570ad57fe0774e80"
TIKV_IMAGE = "pingcap/tikv@sha256:0b9d00f2b4f60cd3f91b55720a737136643e17bfb4de82a3c30ca532430374a5"
TIDB_IMAGE = "pingcap/tidb@sha256:ee98d7d09ea2dcdc76dd683de3c3cdd63f052b33a91f5645ab75609df3648501"
TIFLASH_IMAGE = "docker.m.daocloud.io/pingcap/tiflash@sha256:251e3e2b76482fe2f5c2b82311c9cce24f240a1ad66f1eeda3438e66da3a18ec"
TICDC_IMAGE = "pingcap/ticdc@sha256:7832063b5215b3107d33b7280b2653a79667e9ba54e4b0596ed1092b4a486015"
MYSQL_IMAGE = "mysql@sha256:43bd9764df60666fb2ba2cf8217dd17b3d2414c150005d2fdd07a0cd73d3b7f5"

RELEASE_IMAGES = {
    "pd": PD_IMAGE,
    "tikv": TIKV_IMAGE,
    "tidb": TIDB_IMAGE,
    "tiflash": TIFLASH_IMAGE,
    "ticdc": TICDC_IMAGE,
    "downstream": MYSQL_IMAGE,
}


_NODE_SEQUENCE: dict[str, int] = {}


def _node(role: str, *, cpus: float = 1.0, memory_mb: int = 2048, caps=(), volumes=()) -> NodeSpec:
    index = _NODE_SEQUENCE.get(role, 0)
    _NODE_SEQUENCE[role] = index + 1
    return NodeSpec(
        node_id=f"{role}-spec-{index}",
        role=role,
        resources=PersistentScenarioResourceSpec(
            worker_physical_cores=max(1, int(cpus)),
            worker_memory_mb=memory_mb,
            container_cpu_limit=cpus,
            container_memory_mb=memory_mb,
        ),
        docker_caps=caps,
        volumes=volumes,
    )


def _environment_spec(nodes: tuple[NodeSpec, ...]) -> SimpleNamespace:
    return SimpleNamespace(environment=PersistentScenarioEnvironmentSpec(
        workload="portfolio", scale=1, base_image="unused", nodes=nodes,
    ))


def _contract_topology_environment() -> SimpleNamespace:
    return _environment_spec((
        _node("pd"), _node("pd"), _node("pd"),
        _node("tikv"), _node("tikv"), _node("tikv"),
        _node("tidb"), _node("tidb"),
        _node("tiflash"),
        _node("ticdc"),
        _node("downstream", memory_mb=4096),
    ))


def _deployment(tmp_path: Path, environment, run_id="tidb5-backend-test", port_base=26000) -> TiDBPersistentDeployment:
    topology = expand_topology(environment, release_images=RELEASE_IMAGES, data_dir=str(tmp_path / "data" / run_id))
    return TiDBPersistentDeployment(
        run_id=run_id, port_base=port_base, topology=topology, data_root=tmp_path / "data",
    )


def test_expand_topology_assigns_services_and_images():
    topology = expand_topology(_contract_topology_environment(), release_images=RELEASE_IMAGES, data_dir="/tmp/x")
    assert topology.role_services("pd") == ("pd-0", "pd-1", "pd-2")
    assert topology.role_services("tikv") == ("tikv-0", "tikv-1", "tikv-2")
    assert topology.role_services("tidb") == ("tidb-0", "tidb-1")
    assert topology.role_services("tiflash") == ("tiflash-0",)
    assert topology.role_services("ticdc") == ("ticdc-0",)
    assert topology.role_services("downstream") == ("downstream-0",)
    pd_node = topology.service("pd-0")
    assert pd_node.image == PD_IMAGE
    assert pd_node.cpus == 1.0
    assert topology.service("tidb-0").image == TIDB_IMAGE


def test_expand_topology_rejects_unknown_role_and_missing_core():
    bad = _environment_spec((_node("pd"), _node("tikv"), _node("tidb"), _node("proxy")))
    try:
        expand_topology(bad, release_images=RELEASE_IMAGES, data_dir="/tmp/x")
    except ValueError as exc:
        assert "proxy" in str(exc)
    else:
        raise AssertionError("unknown role must fail")

    missing = _environment_spec((_node("pd"), _node("tikv")))
    try:
        expand_topology(missing, release_images=RELEASE_IMAGES, data_dir="/tmp/x")
    except ValueError as exc:
        assert "tidb" in str(exc)
    else:
        raise AssertionError("missing tidb node must fail")


def test_expand_topology_maps_caps_and_volumes(tmp_path: Path):
    environment = _environment_spec((
        _node("pd"), _node("pd"), _node("pd"),
        _node("tikv"), _node("tikv"), _node("tikv"),
        _node("tidb"), _node("tidb"),
        _node("tiflash", caps=("NET_ADMIN",), volumes=(NodeVolume(name="flashdata", mount_path="/flash-data"),)),
    ))
    topology = expand_topology(environment, release_images=RELEASE_IMAGES, data_dir=str(tmp_path / "run"))
    tiflash = topology.service("tiflash-0")
    assert tiflash.cap_add == ("NET_ADMIN",)
    assert tiflash.volumes == ((f"{tmp_path}/run/volumes/flashdata", "/flash-data"),)


def test_port_plan_allocates_inside_lease():
    topology = expand_topology(_contract_topology_environment(), release_images=RELEASE_IMAGES, data_dir="/tmp/x")
    ports = build_port_plan(topology, 26000)
    assert ports.tidb_sql == {"tidb-0": 26000, "tidb-1": 26002}
    assert ports.tidb_status == {"tidb-0": 26001, "tidb-1": 26003}
    assert ports.prometheus == 26004
    assert ports.downstream == {"downstream-0": 26005}
    assert ports.ticdc == {"ticdc-0": 26006}
    assert all(PORT_RANGE[0] <= port <= PORT_RANGE[1] for port in ports.host_ports)


def test_deployment_rejects_wrong_lease_prefix_and_port():
    topology = expand_topology(_contract_topology_environment(), release_images=RELEASE_IMAGES, data_dir="/tmp/x")
    for run_id in ("pg5-backend-test", "tidb5-Backend-test"):
        try:
            TiDBPersistentDeployment(run_id=run_id, port_base=26000, topology=topology, data_root="/tmp")
        except ValueError:
            pass
        else:
            raise AssertionError(f"run_id {run_id!r} must fail")
    try:
        TiDBPersistentDeployment(run_id="tidb5-backend-test", port_base=25000, topology=topology, data_root="/tmp")
    except ValueError as exc:
        assert "26000" in str(exc)
    else:
        raise AssertionError("port outside lease must fail")
    try:
        TiDBPersistentDeployment(run_id="tidb5-backend-test", port_base=26499, topology=topology, data_root="/tmp")
    except ValueError as exc:
        assert "lease" in str(exc)
    else:
        raise AssertionError("port_base too close to the range end must fail")


def test_deployment_accepts_runner_format_run_id_and_rejects_charset_violations():
    topology = expand_topology(_contract_topology_environment(), release_images=RELEASE_IMAGES, data_dir="/tmp/x")
    run_id = "tidb5-backend-reference__persistent-scenario__tidb_cdc_downstream_freshness__real-model-llm02__r001"
    assert len(run_id) == 99
    deployment = TiDBPersistentDeployment(run_id=run_id, port_base=26000, topology=topology, data_root="/tmp")
    assert deployment.run_id == run_id
    for bad in (run_id.replace("reference", "Reference", 1), "tidb5-backend--pilot"):
        try:
            TiDBPersistentDeployment(run_id=bad, port_base=26000, topology=topology, data_root="/tmp")
        except ValueError:
            pass
        else:
            raise AssertionError(f"run_id {bad!r} must fail")


def test_render_compose_spec_pure_expansion(tmp_path: Path):
    deployment = _deployment(tmp_path, _contract_topology_environment())
    spec = deployment.render_compose_spec()
    services = spec["services"]
    expected = {"pd-0", "pd-1", "pd-2", "tikv-0", "tikv-1", "tikv-2", "tidb-0", "tidb-1", "tiflash-0", "ticdc-0", "downstream-0", "prometheus", "cadvisor"}
    assert set(services) == expected
    assert spec["networks"]["default"] == {"name": deployment.network_name, "external": True}
    tidb0 = services["tidb-0"]
    assert f"{PORT_RANGE[0]}:4000" in tidb0["ports"]
    assert any(port.endswith(":10080") for port in tidb0["ports"])
    assert "--path=pd-0:2379,pd-1:2379,pd-2:2379" in tidb0["command"]
    pd0 = services["pd-0"]
    assert str(deployment.data_dir / "pd" / "pd-0") + ":/data/pd" in pd0["volumes"]
    assert pd0["user"] == f"{pd0['user'].split(':')[0]}:{pd0['user'].split(':')[1]}"
    downstream = services["downstream-0"]
    assert f"{deployment.ports.downstream['downstream-0']}:3306" in downstream["ports"]
    assert str(deployment.data_dir / "downstream" / "downstream-0") + ":/var/lib/mysql" in downstream["volumes"]
    assert "tmpfs" not in downstream
    ticdc = services["ticdc-0"]
    assert any(arg == "--pd=http://pd-0:2379,http://pd-1:2379,http://pd-2:2379" for arg in ticdc["command"])
    assert str(deployment.data_dir / "ticdc" / "ticdc-0") + ":/data" in ticdc["volumes"]


def test_render_compose_spec_contains_prometheus_targets(tmp_path: Path):
    deployment = _deployment(tmp_path, _contract_topology_environment())
    deployment.render_compose_spec()
    prometheus_config = yaml.safe_load((deployment.runtime_dir / "prometheus.yml").read_text())
    jobs = {job["job_name"]: job for job in prometheus_config["scrape_configs"]}
    assert set(jobs) == {"pd", "tikv", "tidb", "tiflash", "ticdc", "cadvisor"}
    assert jobs["tikv"]["static_configs"][0]["targets"] == ["tikv-0:20180", "tikv-1:20180", "tikv-2:20180"]


def test_node_plan_role_validation():
    try:
        PersistentTiDBNodePlan(service="x-0", role="pg_primary", node_id="x", image="img", cpus=1.0, memory_mb=100)
    except ValueError as exc:
        assert "role" in str(exc)
    else:
        raise AssertionError("unknown role must fail")


def test_topology_service_lookup_error():
    topology = expand_topology(_contract_topology_environment(), release_images=RELEASE_IMAGES, data_dir="/tmp/x")
    try:
        topology.service("tidb-9")
    except ValueError as exc:
        assert "tidb-9" in str(exc)
    else:
        raise AssertionError("unknown service lookup must fail")


def test_expand_topology_requires_core_roles():
    environment = _environment_spec((_node("pd"), _node("tidb")))
    try:
        expand_topology(environment, release_images=RELEASE_IMAGES, data_dir="/tmp/x")
    except ValueError as exc:
        assert "tikv" in str(exc)
    else:
        raise AssertionError("topology without tikv must fail at expansion")


def test_expand_topology_accepts_contract_two_tiflash():
    environment = _environment_spec((
        _node("pd"), _node("pd"), _node("pd"),
        _node("tikv"), _node("tikv"), _node("tikv"),
        _node("tidb"), _node("tidb"),
        _node("tiflash"), _node("tiflash"),
    ))
    topology = expand_topology(environment, release_images=RELEASE_IMAGES, data_dir="/tmp/x")
    assert topology.role_services("tiflash") == ("tiflash-0", "tiflash-1")
    assert topology.service("tiflash-0").image == TIFLASH_IMAGE
    assert topology.service("tiflash-1").image == TIFLASH_IMAGE


def test_expand_topology_rejects_beyond_contract_tiflash():
    environment = _environment_spec((
        _node("pd"), _node("pd"), _node("pd"),
        _node("tikv"), _node("tikv"), _node("tikv"),
        _node("tidb"),
        _node("tiflash"), _node("tiflash"), _node("tiflash"),
    ))
    try:
        expand_topology(environment, release_images=RELEASE_IMAGES, data_dir="/tmp/x")
    except ValueError as exc:
        assert "TiFlash" in str(exc) and "contract" in str(exc)
    else:
        raise AssertionError("topology beyond the contract TiFlash count must fail")


def test_node_cpu_limit_primitive_apply_observe_release(tmp_path: Path, monkeypatch):
    environment = _environment_spec((
        _node("pd"), _node("pd"), _node("pd"),
        _node("tikv"), _node("tikv"), _node("tikv"),
        _node("tidb"),
        _node("tiflash", cpus=2.0), _node("tiflash", cpus=2.0),
    ))
    deployment = _deployment(tmp_path, environment)
    commands: list[list[str]] = []
    current = {"nano_cpus": 2_000_000_000}

    def fake_run(cmd, *, component="cluster", timeout=None):
        commands.append(list(cmd))
        if cmd[:2] == ["docker", "update"]:
            current["nano_cpus"] = int(float(cmd[cmd.index("--cpus") + 1]) * 1_000_000_000)
            return ""
        return f"{current['nano_cpus']} 100000 100000"

    monkeypatch.setattr(deployment, "_run", fake_run)
    monkeypatch.setattr(deployment, "service_container_id", lambda service: f"cid-{service}")

    applied = deployment.set_node_cpu_limit("tiflash-1", 0.4)
    assert applied["action"] == "applied"
    assert applied["target"] == "tiflash/tiflash-1"
    assert applied["service"] == "tiflash-1"
    assert applied["requested_cpus"] == 0.4
    assert applied["spec_cpus"] == 2.0
    assert applied["nano_cpus"] == 400_000_000
    assert applied["cpus"] == 0.4
    assert commands[-2][:4] == ["docker", "update", "--cpus", "0.4"]
    assert deployment.node_cpu_limits["tiflash/tiflash-1"] == 0.4

    observed = deployment.node_cpu_limit("tiflash-1")
    assert observed["action"] == "observed"
    assert observed["nano_cpus"] == 400_000_000

    released = deployment.clear_node_cpu_limit("tiflash-1")
    assert released["action"] == "released"
    assert released["restored_cpus"] == 2.0
    assert released["cpus"] == 2.0
    assert commands[-2][:4] == ["docker", "update", "--cpus", "2.0"]
    assert deployment.node_cpu_limits["tiflash/tiflash-1"] == 2.0


def test_node_cpu_limit_primitive_strict_failures(tmp_path: Path, monkeypatch):
    environment = _environment_spec((
        _node("pd"), _node("pd"), _node("pd"),
        _node("tikv"), _node("tikv"), _node("tikv"),
        _node("tidb"), _node("tiflash"),
    ))
    deployment = _deployment(tmp_path, environment)
    try:
        deployment.set_node_cpu_limit("tiflash-0", 0.0)
    except ValueError as exc:
        assert "positive" in str(exc)
    else:
        raise AssertionError("non-positive CPU limit must fail")

    try:
        deployment.set_node_cpu_limit("tiflash-9", 1.0)
    except ValueError as exc:
        assert "tiflash-9" in str(exc)
    else:
        raise AssertionError("unknown service must fail")

    updates: list[list[str]] = []
    stale = {"calls": 0}

    def fake_run(cmd, *, component="cluster", timeout=None):
        if cmd[:2] == ["docker", "update"]:
            updates.append(list(cmd))
            return ""
        stale["calls"] += 1
        # the applied limit never lands in the container HostConfig
        return "2000000000 100000 100000"

    monkeypatch.setattr(deployment, "_run", fake_run)
    monkeypatch.setattr(deployment, "service_container_id", lambda service: f"cid-{service}")
    try:
        deployment.set_node_cpu_limit("tiflash-0", 0.4)
    except Exception as exc:
        assert "did not take effect" in str(exc)
    else:
        raise AssertionError("unapplied CPU limit must fail")
    assert len(updates) == 1
    assert deployment.node_cpu_limits["tiflash/tiflash-0"] == 1.0
