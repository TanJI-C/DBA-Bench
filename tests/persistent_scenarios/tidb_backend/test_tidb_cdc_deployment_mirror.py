"""cdc deployment mirror: the deployed mechanism carries the payload facts.

The schema_release payload publishes two deployment-config mechanism facts
(``gc_pin_release_seconds=600``, ``upstream_gc_life_time="30m0s"``; not SO
budgets). On the pinned pingcap/ticdc:v8.1.0 build the changefeed-level
``gc-ttl`` no longer exists — the GC manager takes its TTL from the server
config (``pkg/txnutil/gc/gc_manager.go``: ``gcTTL: serverConfig.GcTTL``) — so
the pin-release mirror is the ticdc server ``--gc-ttl`` in the persistent
deployment compose command, and the retention mirror is the bootstrap
``SET GLOBAL tidb_gc_life_time`` on the upstream.

No docker: the compose spec is rendered pure and the bootstrap SQL is recorded
at the environment boundary.
"""

import json
from pathlib import Path
from types import SimpleNamespace

from src.execution.tidb_persistent_deployment import (
    MYSQL_IMAGE,
    TICDC_IMAGE,
    TiDBPersistentDeployment,
)
from src.persistent_scenarios.backend.tidb.assembly import _bootstrap_cdc
from src.persistent_scenarios.backend.tidb.capabilities.cdc.safepoint import (
    GC_LIFE_TIME_BASELINE_SECONDS,
    PIN_RELEASE_STALL_SECONDS,
    format_gc_duration,
    parse_gc_duration,
)
from src.persistent_scenarios.backend.tidb.topology import expand_topology
from src.persistent_scenarios.model.spec import NodeSpec, PersistentScenarioEnvironmentSpec, PersistentScenarioResourceSpec

PD_IMAGE = "pingcap/pd@sha256:78f5de9dc59abd02c99056294fb51f29da39ed932eb92cb2570ad57fe0774e80"
TIKV_IMAGE = "pingcap/tikv@sha256:0b9d00f2b4f60cd3f91b55720a737136643e17bfb4de82a3c30ca532430374a5"
TIDB_IMAGE = "pingcap/tidb@sha256:ee98d7d09ea2dcdc76dd683de3c3cdd63f052b33a91f5645ab75609df3648501"

SCHEMA_RELEASE_GC_PAYLOAD = {
    "gc_pin_release_seconds": 600,
    "upstream_gc_life_time": "30m0s",
}


def _node(role: str, index: int) -> NodeSpec:
    return NodeSpec(
        node_id=f"{role}-{index}", role=role,
        resources=PersistentScenarioResourceSpec(
            worker_physical_cores=1, worker_memory_mb=2048,
            container_cpu_limit=1.0, container_memory_mb=2048,
        ),
    )


def _deployment(tmp_path: Path) -> TiDBPersistentDeployment:
    images = {"pd": PD_IMAGE, "tikv": TIKV_IMAGE, "tidb": TIDB_IMAGE,
              "ticdc": TICDC_IMAGE, "downstream": MYSQL_IMAGE}
    roles = (("pd", 0), ("tikv", 0), ("tidb", 0), ("ticdc", 0), ("ticdc", 1))
    nodes = tuple(_node(role, index) for role, index in roles)
    environment = SimpleNamespace(environment=PersistentScenarioEnvironmentSpec(
        workload="portfolio", scale=1, base_image="unused", nodes=nodes,
    ))
    topology = expand_topology(environment, release_images=images, data_dir=str(tmp_path / "data"))
    return TiDBPersistentDeployment(
        run_id="tidb5-backend-cdcmirror", port_base=26000, topology=topology,
        data_root=tmp_path / "data",
    )


def test_ticdc_server_gc_ttl_mirrors_the_pin_release_payload_fact(tmp_path):
    spec = _deployment(tmp_path).render_compose_spec()
    ticdc_commands = [
        service["command"] for name, service in spec["services"].items()
        if name.startswith("ticdc-")
    ]
    assert len(ticdc_commands) == 2
    expected_ttl = f"--gc-ttl={int(SCHEMA_RELEASE_GC_PAYLOAD['gc_pin_release_seconds'])}"
    for command in ticdc_commands:
        assert expected_ttl in command
    # The deployment value and the capability mechanism constant are the same fact.
    assert int(SCHEMA_RELEASE_GC_PAYLOAD["gc_pin_release_seconds"]) == PIN_RELEASE_STALL_SECONDS


def test_gc_duration_round_trips_the_deploy_baseline():
    baseline = format_gc_duration(GC_LIFE_TIME_BASELINE_SECONDS)
    assert baseline == SCHEMA_RELEASE_GC_PAYLOAD["upstream_gc_life_time"]
    assert parse_gc_duration(baseline) == GC_LIFE_TIME_BASELINE_SECONDS


class _RecordingCursor:
    def __init__(self, sink):
        self._sink = sink

    def execute(self, statement, *args):
        self._sink.append(statement)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _RecordingConnection:
    def __init__(self, sink):
        self._sink = sink

    def cursor(self):
        return _RecordingCursor(self._sink)

    def commit(self):
        pass

    def close(self):
        pass


class _RecordingAdmin:
    def __init__(self):
        self.argvs: list[list[str]] = []

    def create(self, changefeed_id, sink_uri, start_ts=None):
        self.argvs.append(["create", changefeed_id, sink_uri])
        return {"changefeed_id": changefeed_id, "state": "normal", "checkpoint_tso": 1, "error": None}

    def query(self, changefeed_id):
        return {"changefeed_id": changefeed_id, "state": "normal", "checkpoint_tso": 1, "error": None}


class _FakeBootstrapEnvironment:
    def __init__(self):
        self.upstream_sql: list[str] = []
        self.downstream_sql: list[str] = []
        self.admin = _RecordingAdmin()

    def connect(self):
        return _RecordingConnection(self.upstream_sql)

    def connect_downstream(self):
        return _RecordingConnection(self.downstream_sql)

    def changefeed_admin(self):
        return self.admin

    @property
    def deployment(self):
        return SimpleNamespace(topology=SimpleNamespace(role_services=lambda role: ["mysql-0"]))


def test_cdc_bootstrap_secures_the_upstream_gc_retention_baseline():
    environment = _FakeBootstrapEnvironment()
    _bootstrap_cdc(environment, spec=None)
    assert "SET GLOBAL tidb_gc_life_time = '30m0s'" in environment.upstream_sql
    # The retention baseline is deploy configuration: it is in place before the
    # changefeed is created (bootstrap order, not a runtime repair action).
    assert environment.upstream_sql.index("SET GLOBAL tidb_gc_life_time = '30m0s'") < len(
        environment.upstream_sql
    )
    assert environment.admin.argvs and environment.admin.argvs[0][0] == "create"
    assert environment.admin.argvs[0][1] == "cdc-freshness"
    assert json.dumps(SCHEMA_RELEASE_GC_PAYLOAD["upstream_gc_life_time"]) == '"30m0s"'
