"""Agent tool surface tests without docker: schemas, routing, validation."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.execution.history.metrics import MetricFrame
from src.execution.tidb_persistent_deployment import TiDBPersistentDeployment
from src.persistent_scenarios.backend.tidb.environment import (
    PersistentTiDBEnvironment,
    _parse_timeout_seconds,
)
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


def _deployment(tmp_path: Path) -> TiDBPersistentDeployment:
    environment = SimpleNamespace(environment=PersistentScenarioEnvironmentSpec(
        workload="portfolio", scale=1, base_image="unused",
        nodes=(_node("pd", 0), _node("pd", 1), _node("pd", 2), _node("tikv", 0), _node("tikv", 1), _node("tikv", 2), _node("tidb", 0), _node("tidb", 1)),
    ))
    topology = expand_topology(environment, release_images=_IMAGES, data_dir=str(tmp_path / "data"))
    return TiDBPersistentDeployment(run_id="tidb5-backend-tools", port_base=26000, topology=topology, data_root=tmp_path / "data")


def test_tool_schemas_shape(tmp_path):
    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))
    schemas = environment.get_tool_schemas()
    names = [schema["function"]["name"] for schema in schemas]
    assert names == ["execute_sql", "query_metrics", "manage_instance", "manage_changefeed", "read_log", "help"]
    for schema in schemas:
        assert schema["type"] == "function"
        assert "description" in schema["function"]


def test_execute_action_unknown_api_is_error_json(tmp_path):
    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))

    result = json.loads(environment.execute_action("manage_cluster", {}))
    assert result["status"] == "error"
    assert "Unknown API" in result["error"]


def test_execute_sql_argument_validation(tmp_path):
    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))

    result = json.loads(environment.execute_action("execute_sql", {"sql_query": ""}))
    assert result["status"] == "error"
    result = json.loads(environment.execute_action("execute_sql", {}))
    assert result["status"] == "error"


def test_manage_instance_validation(tmp_path):
    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))

    result = json.loads(environment.execute_action("manage_instance", {"action": "restart", "target": "tidb-9"}))
    assert result["status"] == "error"
    assert "tidb-9" in result["error"]
    result = json.loads(environment.execute_action("manage_instance", {"action": "destroy", "target": "tidb-0"}))
    assert result["status"] == "error"
    assert "allowed" in result["error"]


def test_read_log_validation(tmp_path):
    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))

    result = json.loads(environment.execute_action("read_log", {"log_type": "kafka"}))
    assert result["status"] == "error"
    result = json.loads(environment.execute_action("read_log", {"log_type": "tikv", "target": "tidb-0"}))
    assert result["status"] == "error"
    result = json.loads(environment.execute_action("read_log", {"log_type": "tikv", "lines": 0}))
    assert result["status"] == "error"
    result = json.loads(environment.execute_action("read_log", {"log_type": "tiflash"}))
    assert result["status"] == "error"  # topology has no tiflash node
    assert "no service" in result["error"]


def test_help_tool_lists_tools(tmp_path):
    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))

    result = json.loads(environment.execute_action("help", {}))
    assert result["status"] == "success"
    assert {tool["name"] for tool in result["tools"]} == {"execute_sql", "query_metrics", "manage_instance", "manage_changefeed", "read_log", "help"}
    result = json.loads(environment.execute_action("help", {"tool_name": "execute_sql"}))
    assert result["definition"]["name"] == "execute_sql"
    result = json.loads(environment.execute_action("help", {"tool_name": "nope"}))
    assert result["status"] == "error"


def test_query_metrics_unknown_metric_is_error(tmp_path):
    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))

    result = json.loads(environment.execute_action("query_metrics", {"metric_type": "no_such_metric"}))
    assert result["status"] == "error"
    result = json.loads(environment.execute_action("query_metrics", {"metric_type": "cpu", "start_timestamp": "2026-09-18 00:00:00"}))
    assert result["status"] == "error"
    assert "together" in result["error"]


def test_agent_sql_timeout_spec_parsing():
    assert _parse_timeout_seconds("60s", "statement_timeout") == 60.0
    assert _parse_timeout_seconds("500ms", "statement_timeout") == 0.5
    with pytest.raises(ValueError):
        _parse_timeout_seconds("60min", "statement_timeout")


def test_query_metrics_unavailable_metric_is_error_payload(tmp_path):
    """Catalog-advertised metrics whose Case provider is absent in the persistent
    assembly return an agent-visible error payload instead of killing the
    session."""
    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))
    expected_marker = {
        "workload_profile": "requires the Case WorkloadRunner",
        "statistics_state": "requires a Case sampler",
        "pd_region_inventory": "requires a Case sampler",
    }
    for metric, marker in expected_marker.items():
        result = json.loads(environment.execute_action("query_metrics", {"metric_type": metric}))
        assert result["status"] == "error", (metric, result)
        assert result["metric"] == metric
        assert "no provider in this environment" in result["error"], (metric, result)
        assert marker in result["error"], (metric, result)


def test_query_metrics_prometheus_unreachable_is_error_payload(tmp_path, monkeypatch):
    """InvalidURL from a missing Prometheus port (persistent assembly) becomes an
    agent-visible error payload instead of killing the session."""
    deployment = _deployment(tmp_path)
    monkeypatch.setattr(deployment, "prometheus_port", None)
    environment = PersistentTiDBEnvironment(deployment=deployment)

    result = json.loads(environment.execute_action("query_metrics", {"metric_type": "query_latency"}))
    assert result["status"] == "error"
    assert result["metric"] == "query_latency"
    assert "prometheus unreachable" in result["error"]
    assert "nonnumeric port" in result["error"]


def test_query_metrics_internal_provider_error_still_raises(tmp_path, monkeypatch):
    """RuntimeErrors outside the known provider-missing / data-missing signatures
    are provider implementation defects and must propagate, not become agent payloads."""

    def _raise(query):
        raise RuntimeError("provider exploded unexpectedly: run_id='stub'")

    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))
    monkeypatch.setattr(environment._metrics, "query", _raise)
    with pytest.raises(RuntimeError):
        environment.execute_action("query_metrics", {"metric_type": "cpu"})


def test_query_metrics_success_path_unaffected(tmp_path, monkeypatch):
    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))
    frame = MetricFrame(
        metric="cpu",
        query_target="tidb/tidb-0",
        step_seconds=2,
        series={"tidb/tidb-0": {"percent": (1.0, 2.0)}},
        timestamps_ms={"tidb/tidb-0": (1000, 3000)},
    )
    monkeypatch.setattr(environment._metrics, "query", lambda query: frame)

    result = json.loads(environment.execute_action("query_metrics", {"metric_type": "cpu", "target": "tidb/tidb-0"}))
    assert result["status"] == "success"
    assert result["metric"] == "cpu"
    assert result["target"] == "tidb/tidb-0"
    assert result["series"][0]["fields"] == {"percent": [1.0, 2.0]}


def test_query_metrics_missing_series_is_error_payload(tmp_path, monkeypatch):
    """A throttled/removed store stops exporting, so a single-target query finds
    no Prometheus series; fault episodes make this routine, not session-fatal."""

    def _empty_range(query, start_epoch_ms, end_epoch_ms, step_seconds):
        return []

    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))
    monkeypatch.setattr(environment._metrics, "_request_range", _empty_range)

    result = json.loads(environment.execute_action("query_metrics", {"metric_type": "cpu", "target": "tidb/tidb-0"}))
    assert result["status"] == "error"
    assert result["metric"] == "cpu"
    assert "prometheus has no series" in result["error"]
    assert "must return one series" in result["error"]


def test_query_metrics_missing_database_services_is_error_payload(tmp_path, monkeypatch):
    """Aggregate resource metrics require every database service's series; with
    tikv-1 removed, the cpu aggregate reports the missing service as a payload."""
    services = ("pd-0", "pd-1", "pd-2", "tikv-0", "tikv-2", "tidb-0", "tidb-1")  # tikv-1 removed

    def _range_without_tikv1(query, start_epoch_ms, end_epoch_ms, step_seconds):
        return [
            {
                "metric": {"container_label_com_docker_compose_service": service},
                "values": [[str(ms / 1000), "0.5"] for ms in range(start_epoch_ms, end_epoch_ms + 1, step_seconds * 1000)],
            }
            for service in services
        ]

    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))
    monkeypatch.setattr(environment._metrics, "_request_range", _range_without_tikv1)

    result = json.loads(environment.execute_action("query_metrics", {"metric_type": "cpu"}))
    assert result["status"] == "error"
    assert result["metric"] == "cpu"
    assert "missing database services" in result["error"]
    assert "tikv-1" in result["error"]


def test_query_metrics_multi_series_success_path_unaffected(tmp_path, monkeypatch):
    """The full cpu aggregate across all database services still succeeds through
    the real provider pipeline (range parse, per-service split, frame validation)."""
    services = ("pd-0", "pd-1", "pd-2", "tikv-0", "tikv-1", "tikv-2", "tidb-0", "tidb-1")

    def _full_range(query, start_epoch_ms, end_epoch_ms, step_seconds):
        return [
            {
                "metric": {"container_label_com_docker_compose_service": service},
                "values": [[str(ms / 1000), "0.5"] for ms in range(start_epoch_ms, end_epoch_ms + 1, step_seconds * 1000)],
            }
            for service in services
        ]

    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))
    monkeypatch.setattr(environment._metrics, "_request_range", _full_range)

    result = json.loads(environment.execute_action("query_metrics", {"metric_type": "cpu"}))
    assert result["status"] == "success"
    assert result["metric"] == "cpu"
    assert {series["target"] for series in result["series"]} == {
        "pd/pd-0", "pd/pd-1", "pd/pd-2",
        "tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2",
        "tidb/tidb-0", "tidb/tidb-1",
    }


def test_agent_sql_timeouts_round_trip(tmp_path):
    environment = PersistentTiDBEnvironment(deployment=_deployment(tmp_path))
    assert environment.agent_statement_timeout == "60s"
    environment.set_agent_sql_timeouts("30s", "5s")
    assert environment.agent_statement_timeout == "30s"
    assert environment.agent_lock_wait_timeout == "5s"
    environment.reset_agent_sql_timeouts()
    assert environment.agent_statement_timeout == "60s"
    assert environment.agent_lock_wait_timeout == "10s"
