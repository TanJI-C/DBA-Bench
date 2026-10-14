from types import SimpleNamespace
import json
from datetime import datetime, timedelta, timezone

import pytest

from src.execution.environments.tidb import TiDBEnv
from src.execution.tidb_metrics import CASE_ONLY_METRICS, TIDB_METRIC_CATALOG
from src.workloads.specs import SessionSetupBehavior, WorkloadProfile


PUBLIC_TIDB_TOOLS = {
    "query_metrics",
    "execute_sql",
    "manage_cluster",
    "read_log",
    "search_knowledge",
    "help",
    "submit",
    "exit",
}


def test_trusted_region_health_combines_environment_and_deployment_observations(monkeypatch):
    deployment = FakeDeployment()
    deployment.stores = SimpleNamespace(
        region_health_observation=lambda: {"pending_peers": 0, "down_peers": 0},
    )
    env = TiDBEnv(deployment=deployment)
    monkeypatch.setattr(env, "_region_health_snapshot", lambda: {"region_count": 16})

    assert json.loads(env.observe_metric("region_health")) == {
        "status": "success",
        "metric": "region_health",
        "kind": "snapshot",
        "snapshot": {"region_count": 16, "pending_peers": 0, "down_peers": 0},
    }


class FakeDeployment:
    run_id = "unit"
    project_name = "aiopsbench-unit"
    prometheus_port = 4999
    primary_tidb_endpoint = ("127.0.0.1", 4000)
    warm_tidb_readiness_timeout_sec = 47
    NODES = {
        "pd/pd-0": "pd-0",
        "tikv/tikv-0": "tikv-0",
        "tidb/tidb-0": "tidb-0",
    }
    tidb_endpoints = {"tidb/tidb-0": ("127.0.0.1", 4000)}
    database_nodes = ("pd/pd-0", "tikv/tikv-0", "tidb/tidb-0")
    node_cpu_limits = {
        "pd/pd-0": 0.5,
        "tikv/tikv-0": 1.0,
        "tidb/tidb-0": 1.0,
    }

    def __init__(self):
        self.network = SimpleNamespace(allow_pd_network=self.allow_pd_network, inspect_pd_network=self.inspect_pd_network)
        self.actions = []
        self.waits = []
        self.pd_requests = []
        self.removed_regions = []
        self.network_inspections = []

    def list_nodes(self):
        return list(self.NODES)

    def node_states(self):
        return {
            "pd/pd-0": {"running": True, "container_id": "hidden-pd"},
            "tikv/tikv-0": {"running": True, "container_id": "hidden-tikv"},
            "tidb/tidb-0": {"running": True, "container_id": "hidden-tidb"},
        }

    def read_logs(self, target, lines=200):
        return "setup line\nvisible line"

    def start_component(self, target):
        self.actions.append(("start", target))

    def restart_component(self, target):
        self.actions.append(("restart", target))

    def stop_component(self, target):
        self.actions.append(("stop", target))

    def _check_pd(self):
        self.actions.append(("check_pd",))

    def _check_tikv_target(self, service):
        self.actions.append(("check_tikv", service))

    def _wait(self, label, check, timeout):
        self.waits.append((label, timeout))

    def wait_for_target(self, target, timeout):
        self.waits.append((target, timeout))

    def pd_request(self, method, path, body=None):
        self.pd_requests.append((method, path, body))
        if path == "/pd/api/v1/stores":
            return {
                "stores": [
                    {
                        "store": {
                            "id": 7,
                            "address": "tikv-0:20160",
                            "state_name": "Offline",
                        },
                        "status": {"region_count": 2, "leader_count": 0},
                    }
                ]
            }
        if path == "/pd/api/v1/config":
            if method == "GET":
                return {"schedule": {"enable-replace-offline-replica": "true"}}
            return {"updated": body}
        if path == "/pd/api/v1/regions/store/7":
            return {"regions": [{"id": 42, "peers": [{"store_id": 7}]}]}
        if path == "/pd/api/v1/region/id/42":
            return {"id": 42, "peers": [{"store_id": 1}, {"store_id": 7}, {"store_id": 13}]}
        if path == "/pd/api/v1/operators":
            return [{"kind": "admin"}]
        if path == "/pd/api/v1/schedulers":
            return ["balance-region-scheduler"]
        raise AssertionError(path)

    def remove_region_peer(self, region_id, store_id):
        self.removed_regions.append((region_id, store_id))
        return {"scheduled": {"region_id": region_id, "store_id": store_id}}

    def inspect_pd_network(self, target):
        self.network_inspections.append(target)
        return {"target": target, "pd_access": "allowed"}

    def allow_pd_network(self, target):
        self.actions.append(("allow_pd_network", target))


class DmlCursor:
    description = None
    rowcount = 1

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def execute(self, sql):
        self.sql = sql


class DmlConnection:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def begin(self):
        return None

    def cursor(self):
        return DmlCursor()

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def _aliases(env):
    return {spec.alias for spec in env.get_tool_specs()}


def test_tidb_workload_profile_reports_affected_rows_for_dml():
    env = TiDBEnv(deployment=FakeDeployment())
    connection = DmlConnection()

    result = env.execute_workload_profile(
        connection,
        WorkloadProfile(
            name="controller",
            sql="UPDATE benchops.controller SET state = 'stable'",
            commit=True,
        ),
    )

    assert result["result_rows"] == 1
    assert connection.commits == 1
    assert connection.rollbacks == 0


class SessionSetupCursor:
    description = None
    rowcount = 0

    def __init__(self):
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def execute(self, sql):
        self.executed.append(sql)

    def fetchall(self):
        return [(1,)]


class SessionSetupConnection:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def begin(self):
        return None

    def cursor(self):
        return SessionSetupCursor()

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_tidb_workload_profile_lazily_initializes_session_setup_state():
    env = TiDBEnv(deployment=FakeDeployment())
    connection = SessionSetupConnection()
    profile = WorkloadProfile(
        name="qp05_fp_07",
        sql="SELECT 1",
        session_setup=SessionSetupBehavior(
            config_query="SELECT 1",
            statement="SET @aiopsbench_qp05_request_fingerprint = 'qp05_fp_07'",
            statement_count=lambda _configuration, _checkout_number: 1,
        ),
    )

    result = env.execute_workload_profile(connection, profile)

    assert result["session_setup_statements"] == 1
    assert id(connection) in env._workload_session_setups
    assert env._workload_session_setups[id(connection)]["configuration"] == (1,)


def test_tidb_env_exposes_one_unified_public_tool_contract():
    env = TiDBEnv(deployment=FakeDeployment())

    assert _aliases(env) == PUBLIC_TIDB_TOOLS


def test_tidb_env_can_limit_an_entrypoint_to_existing_public_tools():
    env = TiDBEnv(
        deployment=FakeDeployment(),
        enabled_tools=(
            "query_metrics",
            "execute_sql",
            "manage_cluster",
            "read_log",
            "search_knowledge",
            "help",
            "submit",
            "exit",
        ),
    )

    assert _aliases(env) == {
        "query_metrics",
        "execute_sql",
        "manage_cluster",
        "read_log",
        "search_knowledge",
        "help",
        "submit",
        "exit",
    }
    assert not {
        "inspect_backup_archive",
        "repair_backup_archive",
        "run_isolated_restore",
        "inspect_isolated_restore",
    } & _aliases(env)


def test_tidb_env_connections_use_case_sql_timeout(monkeypatch):
    env = TiDBEnv(deployment=FakeDeployment())
    env.sql_timeout_seconds = 600
    primary_calls = []
    replica_calls = []

    class Connection:
        pass

    monkeypatch.setattr(
        env,
        "_connect",
        lambda database, **kwargs: primary_calls.append((database, kwargs)) or Connection(),
    )
    monkeypatch.setattr(
        env,
        "_connect_at",
        lambda host, port, **kwargs: replica_calls.append((host, port, kwargs)) or Connection(),
    )

    env._ensure_connection()
    env.configure_secondary_endpoint("127.0.0.1", 4001, "")
    env._ensure_connection("replica")

    assert primary_calls == [(env.dbname, {"timeout_seconds": 600})]
    assert replica_calls == [
        (
            "127.0.0.1",
            4001,
            {
                "database": env.dbname,
                "read_timeout": 600,
                "write_timeout": 600,
                "password": "",
            },
        )
    ]


def test_tidb_env_rejects_hc04_tools_outside_restore_runtime():
    env = TiDBEnv(deployment=FakeDeployment())

    result = json.loads(env._execute_tool("inspect_isolated_restore", {}))

    assert result == {
        "status": "error",
        "error": "Unknown API: inspect_isolated_restore",
    }


def test_tidb_env_does_not_retain_scenario_specific_tool_profiles_or_old_tools():
    env = TiDBEnv(deployment=FakeDeployment())

    assert not hasattr(env, "select_tool_profile")
    assert not hasattr(env, "TOOL_PROFILES")
    for name in (
        "manage_instance",
        "manage_pd",
        "manage_network",
        "query_import_status",
        "manage_import",
        "run_br_backup",
        "query_replication",
        "manage_replication",
        "query_migration",
        "manage_migration",
        "execute_upstream_sql",
        "execute_downstream_sql",
        "read_migration_log",
    ):
        assert not hasattr(env, name)


def test_tidb_query_metrics_is_limited_to_basic_time_series():
    assert TiDBEnv.TIME_SERIES_METRICS - CASE_ONLY_METRICS == frozenset({
        "cpu",
        "memory",
        "disk_io",
        "disk_usage",
        "network_io",
        "qps",
        "query_latency",
        "active_connections",
    })
    assert TiDBEnv.TIME_SERIES_METRICS == TIDB_METRIC_CATALOG.metric_names


def test_tidb_explicit_metric_window_accepts_visibility_boundary_second():
    env = TiDBEnv(deployment=FakeDeployment())
    env._visible_since = datetime(
        2026, 8, 10, 21, 15, 30, 564000, tzinfo=timezone.utc
    ).timestamp()

    start = datetime(2026, 8, 10, 21, 15, 30)
    end = datetime(2026, 8, 10, 21, 15, 44)

    assert env._prometheus_range(start, end) == (start.timestamp(), end.timestamp())

    with pytest.raises(ValueError, match="precedes the TiDB metric visibility boundary"):
        env._prometheus_range(datetime(2026, 8, 10, 21, 15, 29), end)


def test_tidb_query_latency_default_window_preserves_metric_visibility_boundary(monkeypatch):
    env = TiDBEnv(deployment=FakeDeployment())
    env._visible_since = 1_700_000_000.75
    calls = []

    def prometheus_query(query, start, end):
        calls.append((start, end))
        return [1.0], [0.01]

    monkeypatch.setattr(env, "_prometheus_query_at_range", prometheus_query)

    result = json.loads(env._latency_metric(None, None, None))

    assert result["status"] == "success"
    assert len(calls) == 3
    assert all(start >= env._visible_since for start, _ in calls)


@pytest.mark.parametrize(
    "metric",
    [
        "slow_queries",
        "topsql",
        "cluster_info",
        "node_health",
        "region_count",
        "region_health",
        "pd_scheduling",
        "workload_activity",
        "placement_progress",
        "ticdc_progress",
        "ticdc_pipeline",
        "gc_progress",
        "replication",
    ],
)
def test_tidb_query_metrics_rejects_sql_or_control_plane_backed_shortcuts(metric):
    result = json.loads(TiDBEnv(deployment=FakeDeployment()).query_metrics(metric))

    assert result["status"] == "error"
    assert "Unknown TiDB metric_type" in result["error"]


def test_prometheus_range_tolerates_internal_visibility_rounding_only():
    env = TiDBEnv(deployment=FakeDeployment())
    start = datetime(2026, 8, 11, 18, 22, 54, 123456)
    env._visible_since = start.timestamp() + 0.5e-6

    actual_start, actual_end = env._prometheus_range(start, start + timedelta(seconds=1))

    assert actual_start == env._visible_since
    assert actual_end == (start + timedelta(seconds=1)).timestamp()


def test_prometheus_range_still_rejects_a_real_pre_visibility_window():
    env = TiDBEnv(deployment=FakeDeployment())
    start = datetime(2026, 8, 11, 18, 22, 54)
    env._visible_since = start.timestamp() + 1

    with pytest.raises(ValueError, match="precedes the TiDB metric visibility boundary"):
        env._prometheus_range(start, start + timedelta(seconds=1))


def test_manage_cluster_service_list_omits_container_ids():
    env = TiDBEnv(deployment=FakeDeployment())

    result = json.loads(env.manage_cluster("service", "list"))

    assert result["status"] == "success"
    assert set(result["result"]["nodes"]) == set(FakeDeployment.NODES)
    assert all("container_id" not in node for node in result["result"]["nodes"].values())


def test_manage_cluster_service_start_uses_warm_readiness_timeout():
    deployment = FakeDeployment()
    env = TiDBEnv(deployment=deployment)

    result = json.loads(env.manage_cluster("service", "start", target="pd/pd-0"))

    assert result["status"] == "success"
    assert result["resource"] == "service"
    assert result["operation"] == "start"
    assert deployment.actions == [("start", "pd/pd-0")]
    assert deployment.waits == [("pd/pd-0", 47)]


def test_manage_cluster_pd_config_update_accepts_schedule_boolean_string():
    deployment = FakeDeployment()
    env = TiDBEnv(deployment=deployment)

    result = json.loads(
        env.manage_cluster(
            "config",
            "update",
            target="pd",
            parameters={
                "key": "schedule.enable-replace-offline-replica",
                "value": "false",
            },
        )
    )

    assert result["status"] == "success"
    assert deployment.pd_requests == [
        ("POST", "/pd/api/v1/config", {"schedule.enable-replace-offline-replica": "false"})
    ]


def test_tidb_env_reads_and_updates_tikv_io_rate_limit_with_runtime_units():
    deployment = FakeDeployment()
    calls = []
    configs = iter((
        {
            "storage": {
                "io-rate-limit": {
                    "max-bytes-per-sec": "0MiB",
                    "mode": "write-only",
                    "strict": True,
                },
            },
        },
        {},
        {
            "storage": {
                "io-rate-limit": {
                    "max-bytes-per-sec": "1KiB",
                    "mode": "write-only",
                    "strict": True,
                },
            },
        },
    ))

    def exec_tikv(target, command):
        calls.append((target, command))
        return json.dumps(next(configs))

    deployment.exec = exec_tikv
    env = TiDBEnv(deployment=deployment)

    baseline = env.tikv_io_rate_limit("tikv/tikv-0")
    observed = env.set_tikv_io_rate_limit("tikv/tikv-0", "1KiB")

    assert baseline == {
        "max-bytes-per-sec": "0MiB",
        "mode": "write-only",
        "strict": True,
    }
    assert observed == {
        "max-bytes-per-sec": "1KiB",
        "mode": "write-only",
        "strict": True,
    }
    assert len(calls) == 3
    assert calls[1][0] == "tikv/tikv-0"
    assert "storage.io-rate-limit.max-bytes-per-sec" in calls[1][1][-2]
    assert "1KiB" in calls[1][1][-2]


def test_manage_cluster_region_remove_requires_prior_generic_observation():
    deployment = FakeDeployment()
    env = TiDBEnv(deployment=deployment)

    unobserved = json.loads(
        env.manage_cluster(
            "region",
            "remove",
            target="tikv/tikv-0",
            parameters={"region_id": 42},
        )
    )
    assert unobserved["status"] == "error"
    assert "observed before removal" in unobserved["error"]

    observed = json.loads(env.manage_cluster("region", "list", target="tikv/tikv-0"))
    assert observed["status"] == "success"

    removed = json.loads(
        env.manage_cluster(
            "region",
            "remove",
            target="tikv/tikv-0",
            parameters={"region_id": 42},
        )
    )
    assert removed["status"] == "success"
    assert removed["result"] == {"scheduled": {"region_id": 42, "store_id": 7}}


def test_manage_cluster_network_update_is_generic_and_observable():
    deployment = FakeDeployment()
    env = TiDBEnv(deployment=deployment)

    result = json.loads(
        env.manage_cluster(
            "network",
            "update",
            target="tidb/tidb-0",
            parameters={"access": "allow"},
        )
    )

    assert result["status"] == "success"
    assert result["result"] == {"target": "tidb/tidb-0", "pd_access": "allowed"}
    assert deployment.actions == [
        ("allow_pd_network", "tidb/tidb-0"),
    ]


def test_read_log_uses_target_first_contract_and_visible_line_boundary():
    env = TiDBEnv(deployment=FakeDeployment())
    env._log_visible_lines["tikv/tikv-0"] = 1

    result = json.loads(env.read_log("tikv/tikv-0", lines=20))

    assert result == {
        "status": "success",
        "target": "tikv/tikv-0",
        "total_lines": 1,
        "start_line": 1,
        "end_line": 1,
        "page_limit": 20,
        "content": "visible line",
    }


def test_read_log_supports_line_ranges_and_match_context():
    env = TiDBEnv(deployment=FakeDeployment())
    env.deployment.read_logs = lambda target, lines=10000: "\n".join(
        f"line-{index}" for index in range(1, 8)
    )

    ranged = json.loads(
        env.read_log("tikv/tikv-0", lines=20, start_line=3, end_line=5)
    )
    assert ranged["start_line"] == 3
    assert ranged["end_line"] == 5
    assert ranged["content"].splitlines() == ["line-3", "line-4", "line-5"]

    matched = json.loads(
        env.read_log("tikv/tikv-0", lines=20, match_key="LINE-4")
    )
    assert matched["match_key"] == "LINE-4"
    assert matched["matched_lines"] == [4]
    assert matched["start_line"] == 3
    assert matched["end_line"] == 6
    assert matched["content"].splitlines() == [
        "line-3",
        "line-4",
        "line-5",
        "line-6",
    ]


def test_read_log_help_exposes_range_and_match_parameters():
    env = TiDBEnv(deployment=FakeDeployment())

    definition = json.loads(env.help("read_log"))["definition"]
    assert {
        parameter["name"] for parameter in definition["parameters"]
    } == {"target", "lines", "start_line", "end_line", "match_key", "start_timestamp", "end_timestamp"}


def test_help_reports_the_unified_contract():
    env = TiDBEnv(deployment=FakeDeployment())

    result = json.loads(env.help())

    assert result["status"] == "success"
    assert {tool["name"] for tool in result["tools"]} == PUBLIC_TIDB_TOOLS


def test_help_returns_structured_definitions_for_every_tidb_public_tool():
    env = TiDBEnv(deployment=FakeDeployment())

    for tool_name in PUBLIC_TIDB_TOOLS:
        result = json.loads(env.help(tool_name))

        assert result["status"] == "success"
        assert result["definition"]["name"] == tool_name
        assert set(result["definition"]) == {
            "name",
            "description",
            "parameters",
            "result",
            "capabilities",
            "runtime",
        }
        assert set(result["definition"]["capabilities"]) == {
            "metrics",
            "resources",
        }


def test_execute_sql_help_discovers_runtime_registered_connection_surfaces():
    env = TiDBEnv(deployment=FakeDeployment())
    env.register_sql_connection_surface(
        "order_source",
        database="order_source",
        description="订单业务源端数据库。",
        query_examples=(
            "SELECT TABLE_NAME FROM information_schema.tables",
            "SHOW CREATE TABLE <observed_table>",
        ),
    )

    result = json.loads(env.help("execute_sql"))
    definition = result["definition"]
    surfaces = {
        surface["name"]: surface
        for surface in definition["runtime"]["connection_surfaces"]
    }

    assert result["status"] == "success"
    assert "connection_surface_lookup" not in result
    assert surfaces["order_source"] == {
        "name": "order_source",
        "kind": "database",
        "database": "order_source",
        "description": "订单业务源端数据库。",
        "query_examples": [
            "SELECT TABLE_NAME FROM information_schema.tables",
            "SHOW CREATE TABLE <observed_table>",
        ],
    }
    assert "dm_control" not in surfaces
    assert "dm_upstream" not in json.dumps(result["definition"], ensure_ascii=False)
    assert "registered_database_surface" not in json.dumps(result["definition"], ensure_ascii=False)


def test_execute_sql_dispatches_registered_surface_and_removes_it_on_unregister(monkeypatch):
    env = TiDBEnv(deployment=FakeDeployment())
    env.register_sql_connection_surface(
        "order_source",
        database="order_source",
        description="订单业务源端数据库。",
        query_examples=("SHOW CREATE TABLE <observed_table>",),
    )
    seen = []

    class Connection:
        def close(self):
            seen.append("close")

    connection = Connection()
    monkeypatch.setattr(
        env,
        "_connect",
        lambda database=None: seen.append(database) or connection,
    )
    monkeypatch.setattr(
        env,
        "_execute_sql_on_connection",
        lambda current_connection, sql_query, *, bound_result: json.dumps({
            "status": "success",
            "database": seen[0],
            "sql": sql_query,
        }),
    )

    result = json.loads(env.execute_sql("SHOW CREATE TABLE orders", target="order_source"))

    assert result == {
        "status": "success",
        "database": "order_source",
        "sql": "SHOW CREATE TABLE orders",
    }
    assert seen == ["order_source", "close"]

    env.unregister_sql_connection_surface("order_source")
    help_result = json.loads(env.help("execute_sql"))
    assert "order_source" not in {
        surface["name"]
        for surface in help_result["definition"]["runtime"]["connection_surfaces"]
    }
    missing = json.loads(env.execute_sql("SELECT 1", target="order_source"))
    assert missing["status"] == "error"
    assert "order_source" in missing["error"]


def test_dm_action_write_policy_is_visible_and_blocks_control_plane_bypass(monkeypatch):
    env = TiDBEnv(deployment=FakeDeployment())
    env.register_sql_connection_surface(
        "dm_control",
        database="dm_control",
        description="DM control plane.",
        query_examples=("SELECT ... FROM <observed_control_table>",),
    )
    env.set_sql_connection_surface_write_policy("dm_control", "dm_action")

    surface = next(
        item
        for item in json.loads(env.help("execute_sql"))["definition"]["runtime"]["connection_surfaces"]
        if item["name"] == "dm_control"
    )
    assert surface["write_policy"] == "dm_action"

    class Connection:
        def close(self):
            pass

    monkeypatch.setattr(env, "_connect", lambda database=None: Connection())
    monkeypatch.setattr(
        env,
        "_execute_sql_on_connection",
        lambda connection, sql_query, *, bound_result: json.dumps({"status": "success", "sql": sql_query}),
    )

    assert json.loads(
        env.execute_sql(
            "SELECT * FROM dm_task_status WHERE task_name = 'admission-replace'",
            target="dm_control",
        )
    )["status"] == "success"
    assert json.loads(
        env.execute_sql(
            "INSERT INTO dm_actions(task_name, action, replacement_sql, status, error_message, created_at) "
            "VALUES ('admission-replace', 'replace', 'ALTER TABLE dm_replace_events ADD COLUMN new_col INT; "
            "ALTER TABLE dm_replace_events ADD UNIQUE KEY (new_col)', 'pending', '', NOW())",
            target="dm_control",
        )
    )["status"] == "success"

    bypass = json.loads(
        env.execute_sql(
            "INSERT INTO dm_actions(task_name, action, replacement_sql, status, error_message, created_at) "
            "VALUES ('admission-replace', 'replace', '', 'pending', '', NOW()); "
            "UPDATE dm_task_status SET stage = 'Running'",
            target="dm_control",
        )
    )
    assert bypass["status"] == "error"
    assert "only a single INSERT INTO dm_actions is writable" in bypass["error"]

    qualified_bypass = json.loads(
        env.execute_sql(
            "UPDATE dm_control.dm_task_status SET stage = 'Running'",
            target="primary",
        )
    )
    assert qualified_bypass["status"] == "error"
    assert "only a single INSERT INTO dm_actions is writable" in qualified_bypass["error"]

    database_bypass = json.loads(
        env.execute_sql("DROP DATABASE IF EXISTS dm_control", target="primary")
    )
    assert database_bypass["status"] == "error"
    assert "only a single INSERT INTO dm_actions is writable" in database_bypass["error"]


def test_unknown_sql_connection_surface_points_to_runtime_help():
    env = TiDBEnv(deployment=FakeDeployment())

    result = json.loads(env.execute_sql("SELECT 1", target="unknown_surface"))

    assert result["status"] == "error"
    assert "help('execute_sql')" in result["error"]


def test_manage_cluster_definition_covers_the_runtime_operation_surface():
    env = TiDBEnv(deployment=FakeDeployment())
    definition = json.loads(env.help("manage_cluster"))["definition"]

    expected = {
        "service": {"list", "get", "start", "stop", "restart", "scale_out", "scale_in", "replace_disk", "resize", "upgrade", "rollback"},
        "store": {"list", "get", "update"},
        "region": {"list", "get", "remove"},
        "mvcc_lock": {"list", "resolve"},
        "changefeed_diagnostics": {"get", "list"},
        "gc_safepoint": {"list", "remove"},
        "gc_status": {"get"},
        "storage_maintenance": {"preflight", "apply"},
        "unsafe_recovery": {"get", "start"},
        "operator": {"list", "get"},
        "scheduler": {"list", "get", "remove"},
        "config": {"get", "update"},
        "network": {"get", "update"},
        "router": {"get", "update", "drain"},
        "changefeed": {"get", "update", "pause", "resume", "recreate"},
        "job": {"get", "check", "update", "wait", "refresh_binding", "start", "observe", "release_prefix_quarantine"},
        "release": {"get", "prepare", "snapshot", "verify", "upgrade", "rollback"},
        "monitoring": {"get"},
        "pd_recovery": {"inspect", "execute"},
    }

    actual = {
        resource["name"]: {
            operation["name"]
            for operation in resource["operations"]
        }
        for resource in definition["capabilities"]["resources"]
    }
    assert actual == expected


def test_structured_definition_is_embedded_in_native_tool_schema():
    env = TiDBEnv(deployment=FakeDeployment())
    schema = next(
        schema
        for schema in env.get_tool_schemas()
        if schema["function"]["name"] == "manage_cluster"
    )

    marker = "调用定义(JSON): "
    description = schema["function"]["description"]
    assert marker in description
    embedded = json.loads(description.split(marker, 1)[1])
    assert embedded["name"] == "manage_cluster"
    assert len(embedded["capabilities"]["resources"]) == 19


def test_help_native_schema_keeps_a_generic_tool_description():
    env = TiDBEnv(deployment=FakeDeployment())
    schema = next(
        schema
        for schema in env.get_tool_schemas()
        if schema["function"]["name"] == "help"
    )

    description = schema["function"]["description"]
    assert "当前环境可用工具" in description
    assert "execute_sql" not in description
    assert "connection_surfaces" not in description


def test_execute_sql_help_exposes_dynamic_connection_surfaces():
    env = TiDBEnv(deployment=FakeDeployment())

    result = json.loads(env.help("execute_sql"))

    assert result["status"] == "success"
    assert result["definition"]["name"] == "execute_sql"
    assert {surface["name"] for surface in result["definition"]["runtime"]["connection_surfaces"]} == {
        "primary",
        "tidb/tidb-0",
    }
