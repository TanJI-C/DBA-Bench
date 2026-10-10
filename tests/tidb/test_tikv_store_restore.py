import json

from src.execution.deployment import TiDBDockerDeployment


def _deployment_with_deleted_container(calls, monkeypatch):
    monkeypatch.setattr(
        TiDBDockerDeployment, "_compose", property(lambda self: ["docker", "compose"])
    )
    monkeypatch.setattr(
        TiDBDockerDeployment, "persistent_storage_enabled", property(lambda self: False)
    )
    deployment = TiDBDockerDeployment.__new__(TiDBDockerDeployment)
    deployment.NODES = {
        "pd/pd-0": "pd-0",
        "tidb/tidb-0": "tidb-0",
        "tikv/tikv-0": "tikv-0",
    }
    deployment._container_ids = {"pd-0": "live-pd", "tidb-0": "live-tidb", "tikv-0": "dead-tikv"}
    deployment.active_tikv_services = {"tikv-0"}
    deployment._persistent_run_dir = None
    deployment.bootstrap_data_paths = {("tikv", "tikv-0"): "/tmp/aiops-test-tikv-0"}

    def run(cmd, component="cluster"):
        calls.append(tuple(cmd))
        if cmd[:2] == ["docker", "inspect"]:
            raise RuntimeError(
                f"TiDB command failed: component={component!r}, command={cmd!r}, "
                f"returncode=1, stderr='error: no such object: {cmd[-1]}'"
            )
        return ""

    deployment._run = run
    return deployment


def test_service_state_reports_missing_container(monkeypatch):
    calls = []
    deployment = _deployment_with_deleted_container(calls, monkeypatch)
    state = TiDBDockerDeployment._service_state(deployment, "tikv/tikv-0")
    assert state["missing"] is True
    assert state["running"] is False
    assert state["status"] == "missing"


def test_service_state_reraises_other_inspect_failures(monkeypatch):
    calls = []
    deployment = _deployment_with_deleted_container(calls, monkeypatch)

    def run(cmd, component="cluster"):
        raise RuntimeError(f"docker daemon unreachable: {cmd!r}")

    deployment._run = run
    try:
        TiDBDockerDeployment._service_state(deployment, "tikv/tikv-0")
    except RuntimeError as exc:
        assert "docker daemon unreachable" in str(exc)
    else:
        raise AssertionError("expected RuntimeError for non-missing inspect failure")


def test_restore_rebuilds_deleted_case_container_without_wipe(monkeypatch):
    calls = []
    deployment = _deployment_with_deleted_container(calls, monkeypatch)
    deployment._pd_stores = lambda: [
        {
            "store": {"address": "tikv-0:20160", "state_name": "Down"},
            "status": {},
        }
    ]
    deployment._control = lambda action, target: calls.append((action, target))
    deployment.start_component = lambda target: calls.append(("start", target))
    deployment.restart_component = lambda target: calls.append(("restart", target))
    deployment._wait_store_state = lambda target, state, timeout: None

    TiDBDockerDeployment.restore_tikv_stores(deployment, ("tikv/tikv-0",))

    commands = [call for call in calls if isinstance(call, tuple) and call[0] == "docker"]
    assert ("docker", "compose", "create", "tikv-0") in commands
    assert not any("rm" in command for command in commands)
    assert not any("rmtree" in str(command) for command in commands)
    actions = [call for call in calls if isinstance(call, tuple) and call[0] in ("start", "restart", "stop")]
    assert ("start", "tikv/tikv-0") in actions
