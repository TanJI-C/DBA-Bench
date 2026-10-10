"""manage_instance('retire'): PD store decommission action surface.

No docker: PD HTTP and pd-ctl are faked at the deployment boundary. The
argv/payload vectors encode the PD facts the deterministic reference path
verified live (store delete -> Offline; drain watch applies transfer-leader
once, then remove-peer, against the measured last-mile stall).
"""

import json
from pathlib import Path
from types import SimpleNamespace

from src.execution.tidb_persistent_deployment import TiDBPersistentDeployment
from src.persistent_scenarios.backend.tidb.environment import PersistentTiDBEnvironment
from src.persistent_scenarios.backend.tidb.topology import expand_topology
from src.persistent_scenarios.model.spec import NodeSpec, PersistentScenarioEnvironmentSpec, PersistentScenarioResourceSpec

PD_IMAGE = "pingcap/pd@sha256:78f5de9dc59abd02c99056294fb51f29da39ed932eb92cb2570ad57fe0774e80"
TIKV_IMAGE = "pingcap/tikv@sha256:0b9d00f2b4f60cd3f91b55720a737136643e17bfb4de82a3c30ca532430374a5"
TIDB_IMAGE = "pingcap/tidb@sha256:ee98d7d09ea2dcdc76dd683de3c3cdd63f052b33a91f5645ab75609df3648501"


def _node(role: str, index: int) -> NodeSpec:
    return NodeSpec(
        node_id=f"{role}-{index}", role=role,
        resources=PersistentScenarioResourceSpec(
            worker_physical_cores=1, worker_memory_mb=2048,
            container_cpu_limit=1.0, container_memory_mb=2048,
        ),
    )


def _environment(tmp_path: Path):
    images = {"pd": PD_IMAGE, "tikv": TIKV_IMAGE, "tidb": TIDB_IMAGE}
    nodes = (
        _node("pd", 0), _node("pd", 1), _node("pd", 2),
        *(_node("tikv", index) for index in range(5)),
        _node("tidb", 0), _node("tidb", 1),
    )
    environment = SimpleNamespace(environment=PersistentScenarioEnvironmentSpec(
        workload="portfolio", scale=1, base_image="unused", nodes=nodes,
    ))
    topology = expand_topology(environment, release_images=images, data_dir=str(tmp_path / "data"))
    deployment = TiDBPersistentDeployment(
        run_id="tidb5-backend-store-retire", port_base=26400, topology=topology,
        data_root=tmp_path / "data",
    )
    return deployment, PersistentTiDBEnvironment(deployment=deployment)


class FakePD:
    """Scripted /pd/api/v1/stores + per-store regions; records DELETEs."""

    def __init__(self):
        self.records = {
            store_id: {"id": store_id, "address": f"tikv-{store_id - 1}:20160",
                       "state_name": "Up", "region_count": 10}
            for store_id in range(1, 6)
        }
        self.deletes: list[int] = []
        self.regions_answer = [{"id": 77}, {"id": 78}]

    def __call__(self, method: str, path: str, body=None):
        if method == "GET" and path == "/pd/api/v1/stores":
            return {"stores": [{"store": record} for record in self.records.values()]}
        if method == "DELETE" and path.startswith("/pd/api/v1/store/"):
            store_id = int(path.rsplit("/", 1)[-1])
            self.deletes.append(store_id)
            self.records[store_id]["state_name"] = "Offline"
            return {"store": self.records[store_id]}
        if method == "GET" and path.startswith("/pd/api/v1/regions/store/"):
            return {"regions": list(self.regions_answer)}
        raise AssertionError(f"unexpected PD call: {method} {path}")


def test_retire_deletes_the_store_and_reports_offline(tmp_path, monkeypatch):
    deployment, environment = _environment(tmp_path)
    fake_pd = FakePD()
    monkeypatch.setattr(deployment, "pd_request", fake_pd)
    ctl_argvs: list[list[str]] = []
    monkeypatch.setattr(
        deployment, "exec_command",
        lambda service, args, timeout=30: ctl_argvs.append(list(args)) or "success!\n",
    )
    # Keep the background drain watch in a test-fast polling cadence, and make
    # it exit after one unstick round by emptying the store list.
    monkeypatch.setattr(environment, "_DRAIN_POLL_SECONDS", 0.01)
    monkeypatch.setattr(environment, "_DRAIN_STALLED_POLLS_BEFORE_TRANSFER", 2)
    original_state_reader = environment._pd_store_state

    def state_gone_after_unstick(store_id: int):
        if ctl_argvs:
            fake_pd.records.pop(store_id, None)
        return original_state_reader(store_id)

    monkeypatch.setattr(environment, "_pd_store_state", state_gone_after_unstick)

    result = json.loads(environment.execute_action(
        "manage_instance", {"action": "retire", "target": "tikv-2"},
    ))
    assert fake_pd.deletes == [3]
    assert result == {
        "status": "success",
        "service": "tikv-2",
        "action": "retire",
        "store_id": 3,
        "state": "Offline",
        "message": result["message"],
    }
    assert "migrating off" in result["message"]

    # The drain watch unsticks the last-mile stall: transfer-leader first,
    # keeping quorum, against the lowest Up store.
    import time

    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and not ctl_argvs:
        time.sleep(0.02)
    assert ctl_argvs and ctl_argvs[0] == [
        "/pd-ctl", "-u", "http://127.0.0.1:2379",
        "operator", "add", "transfer-leader", "77", "store 1",
    ]


def test_retire_requires_a_registered_store(tmp_path, monkeypatch):
    deployment, environment = _environment(tmp_path)
    fake_pd = FakePD()
    fake_pd.records.pop(3)
    monkeypatch.setattr(deployment, "pd_request", fake_pd)
    result = json.loads(environment.execute_action(
        "manage_instance", {"action": "retire", "target": "tikv-2"},
    ))
    assert result["status"] == "error"
    assert "no store registered" in result["error"]
    assert fake_pd.deletes == []


def test_retire_rejects_a_value(tmp_path):
    _, environment = _environment(tmp_path)
    result = json.loads(environment.execute_action(
        "manage_instance", {"action": "retire", "target": "tikv-2", "value": "x"},
    ))
    assert result["status"] == "error"
    assert "does not accept a value" in result["error"]


def test_retire_rejects_an_unknown_service(tmp_path):
    _, environment = _environment(tmp_path)
    result = json.loads(environment.execute_action(
        "manage_instance", {"action": "retire", "target": "nope-9"},
    ))
    assert result["status"] == "error"


def test_drain_watch_applies_remove_peer_after_a_second_stall(tmp_path, monkeypatch):
    deployment, environment = _environment(tmp_path)
    fake_pd = FakePD()
    monkeypatch.setattr(deployment, "pd_request", fake_pd)
    ctl_argvs: list[list[str]] = []
    monkeypatch.setattr(
        deployment, "exec_command",
        lambda service, args, timeout=30: ctl_argvs.append(list(args)) or "success!\n",
    )
    monkeypatch.setattr(environment, "_DRAIN_POLL_SECONDS", 0.01)
    monkeypatch.setattr(environment, "_DRAIN_STALLED_POLLS_BEFORE_TRANSFER", 1)

    # The store stays Offline forever; the watch must fall through to
    # remove-peer after the transfer-leader attempt, then exit at its deadline.
    monkeypatch.setattr(environment, "_DRAIN_MAX_SECONDS", 0.05)
    environment._watch_tikv_store_drain("tikv-2", 3)
    assert ctl_argvs[0][3:6] == ["operator", "add", "transfer-leader"]
    assert ctl_argvs[-1][3:6] == ["operator", "add", "remove-peer"]
