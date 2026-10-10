"""Changefeed lifecycle action surface: cli argv contract, agent api, classifier.

No docker: the cli runner and PD request are faked at the deployment boundary.
The argv vectors encode the pinned pingcap/ticdc:v8.1.0 cli facts verified
live: binary at /cdc, create/resume accept --no-confirm, pause/remove do
not (pause flags are only -c/--changefeed-id and -n/--namespace).
"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.execution.tidb_persistent_deployment import (
    MYSQL_IMAGE,
    TICDC_IMAGE,
    TiDBPersistentDeployment,
    TiDBPersistentDeploymentError,
)
from src.persistent_scenarios.backend.tidb.changefeed import CdcChangefeedAdmin, TICDC_CLI
from src.persistent_scenarios.backend.tidb.classifier import TiDBActionClassifier
from src.persistent_scenarios.backend.tidb.environment import PersistentTiDBEnvironment
from src.persistent_scenarios.backend.tidb.topology import expand_topology
from src.persistent_scenarios.model.spec import NodeSpec, PersistentScenarioEnvironmentSpec, PersistentScenarioResourceSpec

PD_IMAGE = "pingcap/pd@sha256:78f5de9dc59abd02c99056294fb51f29da39ed932eb92cb2570ad57fe0774e80"
TIKV_IMAGE = "pingcap/tikv@sha256:0b9d00f2b4f60cd3f91b55720a737136643e17bfb4de82a3c30ca532430374a5"
TIDB_IMAGE = "pingcap/tidb@sha256:ee98d7d09ea2dcdc76dd683de3c3cdd63f052b33a91f5645ab75609df3648501"

SIMPLE_PAYLOAD = {
    "upstream_id": 7687212255842846230,
    "namespace": "default",
    "id": "gate1-feed",
    "state": "normal",
    "checkpoint_tso": 469190266227785742,
    "checkpoint_time": "2026-09-19 11:53:46.686",
    "error": None,
}


def _node(role: str, index: int) -> NodeSpec:
    return NodeSpec(
        node_id=f"{role}-{index}", role=role,
        resources=PersistentScenarioResourceSpec(
            worker_physical_cores=1, worker_memory_mb=2048,
            container_cpu_limit=1.0, container_memory_mb=2048,
        ),
    )


def _deployment(tmp_path: Path, *roles: tuple[str, int]) -> TiDBPersistentDeployment:
    images = {"pd": PD_IMAGE, "tikv": TIKV_IMAGE, "tidb": TIDB_IMAGE,
              "ticdc": TICDC_IMAGE, "downstream": MYSQL_IMAGE}
    nodes = tuple(_node(role, index) for role, index in roles)
    environment = SimpleNamespace(environment=PersistentScenarioEnvironmentSpec(
        workload="portfolio", scale=1, base_image="unused", nodes=nodes,
    ))
    topology = expand_topology(environment, release_images=images, data_dir=str(tmp_path / "data"))
    return TiDBPersistentDeployment(
        run_id="tidb5-backend-cdcadmin", port_base=26000, topology=topology,
        data_root=tmp_path / "data",
    )


class FakeCliRunner:
    """Records argv vectors; answers query --simple with the scripted payload."""

    def __init__(self, payload: dict | None = None):
        self.argvs: list[list[str]] = []
        self.payload = payload if payload is not None else SIMPLE_PAYLOAD

    def __call__(self, argv: list[str]) -> str:
        self.argvs.append(list(argv))
        if "query" in argv and "--simple" in argv:
            return json.dumps(self.payload)
        return "cli ok"

    def command_argv(self, index: int) -> list[str]:
        return self.argvs[index]


def test_cli_binary_is_the_pinned_image_path():
    assert TICDC_CLI == "/cdc"


def test_create_argv_and_observation():
    runner = FakeCliRunner()
    admin = CdcChangefeedAdmin(cli_runner=runner, pd_address="http://pd-0:2379")
    result = admin.create("gate1-feed", "mysql://root:@downstream-0:3306/", start_ts=469190263225974790)
    assert runner.command_argv(0) == [
        TICDC_CLI, "cli", "changefeed", "create",
        "--pd=http://pd-0:2379",
        "--changefeed-id=gate1-feed",
        "--sink-uri=mysql://root:@downstream-0:3306/",
        "--start-ts=469190263225974790",
        "--no-confirm",
    ]
    assert len(runner.argvs) == 2
    assert result == {
        "changefeed_id": "gate1-feed",
        "state": "normal",
        "checkpoint_tso": 469190266227785742,
        "error": None,
    }


def test_create_without_start_ts_uses_current_tso():
    runner = FakeCliRunner()
    admin = CdcChangefeedAdmin(cli_runner=runner, pd_address="http://pd-0:2379")
    admin.create("feed", "mysql://root:@downstream-0:3306/")
    assert "--start-ts=469190263225974790" not in runner.command_argv(0)


def test_pause_has_no_noconfirm_flag():
    runner = FakeCliRunner(payload={**SIMPLE_PAYLOAD, "state": "stopped"})
    admin = CdcChangefeedAdmin(cli_runner=runner, pd_address="http://pd-0:2379")
    result = admin.pause("gate1-feed")
    assert runner.command_argv(0) == [
        TICDC_CLI, "cli", "changefeed", "pause",
        "--pd=http://pd-0:2379",
        "--changefeed-id=gate1-feed",
    ]
    assert result["state"] == "stopped"


def test_resume_carries_noconfirm():
    runner = FakeCliRunner()
    admin = CdcChangefeedAdmin(cli_runner=runner, pd_address="http://pd-0:2379")
    result = admin.resume("gate1-feed")
    assert runner.command_argv(0) == [
        TICDC_CLI, "cli", "changefeed", "resume",
        "--pd=http://pd-0:2379",
        "--changefeed-id=gate1-feed",
        "--no-confirm",
    ]
    assert result["state"] == "normal"


def test_remove_returns_removed_state_without_query():
    runner = FakeCliRunner()
    admin = CdcChangefeedAdmin(cli_runner=runner, pd_address="http://pd-0:2379")
    result = admin.remove("gate1-feed")
    assert runner.command_argv(0) == [
        TICDC_CLI, "cli", "changefeed", "remove",
        "--pd=http://pd-0:2379",
        "--changefeed-id=gate1-feed",
    ]
    assert len(runner.argvs) == 1
    assert result == {"changefeed_id": "gate1-feed", "state": "removed", "detail": "cli ok"}


def test_query_uses_simple_shape():
    runner = FakeCliRunner()
    admin = CdcChangefeedAdmin(cli_runner=runner, pd_address="http://pd-0:2379")
    result = admin.query("gate1-feed")
    assert runner.command_argv(0) == [
        TICDC_CLI, "cli", "changefeed", "query",
        "--changefeed-id=gate1-feed", "--simple",
    ]
    assert result["checkpoint_tso"] == 469190266227785742
    assert result["error"] is None


def test_admin_rejects_non_http_pd_address():
    with pytest.raises(ValueError, match="pd_address"):
        CdcChangefeedAdmin(cli_runner=FakeCliRunner(), pd_address="pd-0:2379")


def _cdc_environment(tmp_path: Path):
    deployment = _deployment(
        tmp_path,
        ("pd", 0), ("pd", 1), ("pd", 2),
        ("tikv", 0), ("tidb", 0),
        ("ticdc", 0), ("ticdc", 1),
    )
    return deployment, PersistentTiDBEnvironment(deployment=deployment)


def test_manage_changefeed_api_query_contract(tmp_path):
    deployment, environment = _cdc_environment(tmp_path)
    runner = FakeCliRunner()
    deployment.exec_command = lambda service, args, timeout=30: runner([service, *args])
    result = json.loads(environment.execute_action("manage_changefeed", {"action": "query", "changefeed_id": "gate1-feed"}))
    assert result["state"] == "normal"
    assert result["checkpoint_tso"] == 469190266227785742
    assert runner.argvs[0][0] == "ticdc-0"

    json.loads(environment.execute_action("manage_changefeed", {
        "action": "query", "changefeed_id": "gate1-feed", "capture_target": "ticdc-1",
    }))
    assert runner.argvs[-1][0] == "ticdc-1"


def test_manage_changefeed_cli_failure_is_error_json(tmp_path):
    deployment, environment = _cdc_environment(tmp_path)

    def failing_exec(service, args, timeout=30):
        raise TiDBPersistentDeploymentError(
            f"TiDB persistent docker command failed: run_id={deployment.run_id!r}, component={service!r}, "
            f"command={args!r}, returncode=1"
        )

    deployment.exec_command = failing_exec
    result = json.loads(environment.execute_action("manage_changefeed", {"action": "pause", "changefeed_id": "nope"}))
    assert result["status"] == "error"
    assert "cdc cli failed" in result["error"]
    assert result["action"] == "pause"


def test_manage_changefeed_argument_validation(tmp_path):
    _, environment = _cdc_environment(tmp_path)
    cases = [
        ({"action": "destroy", "changefeed_id": "f"}, "action"),
        ({"action": "query"}, "changefeed_id"),
        ({"action": "query", "changefeed_id": "f", "capture_target": "tidb-0"}, "capture_target"),
        ({"action": "create", "changefeed_id": "f"}, "sink_uri"),
        ({"action": "create", "changefeed_id": "f", "sink_uri": "mysql://x", "start_ts": "123"}, "start_ts"),
    ]
    for args, fragment in cases:
        result = json.loads(environment.execute_action("manage_changefeed", args))
        assert result["status"] == "error", args
        assert fragment in result["error"], args


def test_changefeed_surface_requires_ticdc_topology(tmp_path):
    deployment = _deployment(tmp_path, ("pd", 0), ("tikv", 0), ("tidb", 0))
    environment = PersistentTiDBEnvironment(deployment=deployment)
    result = json.loads(environment.execute_action("manage_changefeed", {"action": "query", "changefeed_id": "f"}))
    assert result["status"] == "error"
    assert "ticdc" in result["error"]


def test_gc_safepoint_list_uses_pd_service_endpoint(tmp_path):
    deployment, environment = _cdc_environment(tmp_path)
    payload = {
        "service_gc_safe_points": [
            {"service_id": "gc_worker", "expired_at": 9223372036854775807, "safe_point": 469190000000000000},
            {"service_id": "ticdc", "expired_at": 1758288000000000000, "safe_point": 469190263225974790},
        ],
        "min_service_gc_safe_point": 469190263225974790,
        "gc_safe_point": 469190000000000000,
    }
    calls = []

    def fake_pd_request(method, path, body=None):
        calls.append((method, path))
        return payload

    deployment.pd_request = fake_pd_request
    assert environment.gc_safepoint_list() == payload
    assert calls == [("GET", "/pd/api/v1/gc/safepoint")]


def test_classifier_covers_manage_changefeed():
    classification = TiDBActionClassifier()(
        "manage_changefeed", {"action": "remove", "changefeed_id": "gate1-feed"}, None,
    )
    assert classification.action_class == "cdc_admin"
    assert classification.objects == ("gate1-feed",)
    assert classification.details["action"] == "remove"


def test_tool_schemas_include_manage_changefeed(tmp_path):
    _, environment = _cdc_environment(tmp_path)
    names = [schema["function"]["name"] for schema in environment.get_tool_schemas()]
    assert "manage_changefeed" in names
