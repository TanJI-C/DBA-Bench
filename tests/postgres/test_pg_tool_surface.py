import json
import subprocess
from collections import deque
from types import SimpleNamespace

import pytest

from src.execution.environments.postgres import PGEnv
from src.execution.postgres_replica_fleet import PgReplicaFleetEnv

REMOVED_METRICS = (
    "slow_queries",
    "topsql",
    "dead_tuples",
)


def _env():
    return PGEnv(deployment=SimpleNamespace(container_name="pg-tool-test", resources={}))


def test_agent_query_metrics_schema_contains_only_non_sql_observation_arguments():
    env = _env()
    spec = next(spec for spec in env.get_tool_specs() if spec.alias == "query_metrics")

    assert spec.method_name == "_query_metrics_for_agent"
    assert {parameter.name for parameter in spec.parameters} == {
        "metric_type", "target", "limit", "start_timestamp", "end_timestamp", "step_seconds",
    }
    assert all(metric not in spec.description for metric in REMOVED_METRICS)
    assert all(metric not in spec.parameters[0].description for metric in REMOVED_METRICS)
    assert {
        "cpu", "memory", "disk_io", "active_connections", "disk_usage",
        "qps", "cache_hit_ratio",
    } <= PGEnv.AGENT_METRICS
    assert "execute_sql" in spec.description


def test_agent_query_metrics_help_includes_scenario_contract_when_registered():
    env = _env()

    class Provider:
        def agent_contract(self):
            return {"case_id": "filesystem_cleanup_pressure", "metrics": {"filesystem_io": {}}}

    env.attach_scenario_metric_provider(Provider())

    result = json.loads(env.execute_action("help", {"tool_name": "query_metrics"}))

    assert result["definition"]["case_contract"]["case_id"] == "filesystem_cleanup_pressure"
    assert "filesystem_io" in result["definition"]["case_contract"]["metrics"]


def test_agent_query_metrics_still_exposes_container_sampler(monkeypatch):
    env = _env()
    monkeypatch.setattr(env, "query_metrics", lambda **kwargs: json.dumps({
        "status": "success", "metric": kwargs["metric_type"],
    }))

    for metric in ("cpu", "qps", "cache_hit_ratio"):
        result = json.loads(env.execute_action("query_metrics", {"metric_type": metric}))
        assert result == {"status": "success", "metric": metric}


def test_agent_query_metrics_accepts_current_case_catalog_metrics(monkeypatch):
    env = _env()
    env._metric_catalog = SimpleNamespace(metric_names={"wal_generation"})
    monkeypatch.setattr(env, "query_metrics", lambda **kwargs: json.dumps({
        "status": "success", "metric": kwargs["metric_type"],
    }))

    result = json.loads(env._query_metrics_for_agent("wal_generation"))

    assert result == {"status": "success", "metric": "wal_generation"}


def test_catalog_metric_does_not_require_legacy_provider_query(monkeypatch):
    env = _env()
    env._scenario_metric_provider = SimpleNamespace()
    env._metric_catalog = SimpleNamespace(metric_names={"filesystem_io"})
    monkeypatch.setattr(env, "_ensure_connection", lambda: False)
    monkeypatch.setattr(env, "_metric_time_range", lambda *_args: (None, None))
    monkeypatch.setattr(env, "_raise_sampler_failure", lambda: None)
    monkeypatch.setattr(env._metric_service, "query_public", lambda _query: (_ for _ in ()).throw(
        ValueError("metric service reached")
    ))

    result = json.loads(env._query_metrics_for_agent("filesystem_io"))

    assert result["status"] == "error"
    assert result["error"] == "metric service reached"


def test_agent_active_connections_returns_raw_sampler_series(monkeypatch):
    env = _env()
    monkeypatch.setattr(env, "query_metrics", lambda **kwargs: json.dumps({
        "status": "success",
        "metric": kwargs["metric_type"],
        "kind": "series",
        "series": {"postgres": {"timestamps": [], "connections": []}},
    }))

    result = json.loads(
        env.execute_action("query_metrics", {"metric_type": "active_connections"})
    )

    assert result["metric"] == "active_connections"


def test_agent_disk_usage_returns_container_filesystem_snapshot(monkeypatch):
    env = _env()
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="Used Avail Use%\n1048576 2097152 33%\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = json.loads(
        env.execute_action("query_metrics", {"metric_type": "disk_usage"})
    )

    assert result == {
        "status": "success",
        "metric": "disk_usage",
        "kind": "snapshot",
        "snapshot": {
            "filesystem": "/",
            "used_mb": 1.0,
            "available_mb": 2.0,
            "usage_percent": 33.0,
            "source": "container_df",
        },
    }
    assert calls[0][0] == [
        "docker", "exec", "pg-tool-test", "df",
        "--output=used,avail,pcent", "-B1", "/",
    ]


def test_sql_derived_metrics_are_not_available_from_agent_query_metrics():
    env = _env()

    for metric in REMOVED_METRICS:
        assert metric not in PGEnv.AGENT_METRICS
        result = json.loads(
            env.execute_action("query_metrics", {"metric_type": metric})
        )
        assert result["status"] == "error"


def test_replica_fleet_uses_pg_agent_surface_for_generic_metrics():
    env = PgReplicaFleetEnv.__new__(PgReplicaFleetEnv)
    env.deployment = SimpleNamespace(container_name="pg-fleet-tool-test")
    env.query_metrics = lambda **kwargs: json.dumps({"status": "success", "metric": kwargs["metric_type"]})
    result = json.loads(env._query_metrics_for_agent("active_connections"))
    assert result == {"status": "success", "metric": "active_connections"}


def test_validate_backup_is_delegated_to_the_rpo_controller():
    env = _env()

    class Controller:
        def handle_manage_instance(self, action, target, value):
            return json.dumps({"status": "success", "action": action, "target": target})

    env._rpo_controller = Controller()

    result = json.loads(env.manage_instance("validate_backup", "/aiopsbench/basebackups/base"))

    assert result == {
        "status": "success",
        "action": "validate_backup",
        "target": "/aiopsbench/basebackups/base",
    }


def test_validate_backup_checks_manifest_files_and_wal_chain(monkeypatch):
    env = _env()
    manifest = {
        "backup_id": "backup-1",
        "base_backup_path": "/var/lib/postgresql/backup/base",
        "archive_dir": "/var/lib/postgresql/backup/archive",
        "backup_stop_time": "2026-08-09T00:00:00Z",
        "requested_recovery_target_time": "2026-08-09T00:05:00Z",
        "files": [{"path": "base.tar", "size_bytes": 10}],
        "wal_chain": [{"sequence": 1, "wal_file": "000000010000000000000001", "end_time": "2026-08-09T00:05:00Z"}],
    }
    env._docker_read_text = lambda _path: json.dumps(manifest)
    env._docker_file_size = lambda _path: 10
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, stdout="", stderr=""),
    )

    result = json.loads(env.manage_instance("validate_backup", "/var/lib/postgresql/backup/base"))

    assert result["validation_status"] == "passed"
    assert result["base_backup_ok"] is True
    assert result["archive_chain_ok"] is True
    assert result["recoverable"] is True


def test_terminate_process_controls_container_os_processes(monkeypatch):
    env = _env()
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="123\n124\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = json.loads(env.manage_instance("terminate_process", "stress-ng"))

    assert result["status"] == "success"
    assert result["action"] == "terminate_process"
    assert result["killed_pids"] == ["123", "124"]
    assert calls[0][:4] == ["docker", "exec", "pg-tool-test", "bash"]
    assert "stress-ng" in calls[0][-1]


def test_terminate_process_refuses_the_postgresql_server():
    env = _env()

    result = json.loads(env.manage_instance("terminate_process", "postgres"))

    assert result["status"] == "error"
    assert "PostgreSQL server process" in result["error"]


def test_manage_instance_description_separates_os_and_database_termination():
    env = _env()
    spec = next(spec for spec in env.get_tool_specs() if spec.alias == "manage_instance")

    assert "非 PostgreSQL OS 进程" in spec.description
    assert "pg_terminate_backend" in spec.description
    assert "备份/RPO" in spec.description
