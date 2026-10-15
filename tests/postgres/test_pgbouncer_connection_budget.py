import json
import queue
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.execution.environments.postgres import PGEnv
from src.scenarios.postgres.resource_governance import pgbouncer_connection_budget as pgbouncer_module
from src.scenarios import ALL_SCENARIOS
from src.scenarios.base import CaseRun, InjectionRecord
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.postgres.resource_governance.pgbouncer_connection_budget import (
    PGBOUNCER_FAULT_IMAGE_PREFIX,
    PGBOUNCER_PORTS,
    PgBouncerConnectionBudgetInjector,
    PgBouncerMetricHistoryProvider,
    PgResourceGovernancePgbouncerConnectionBudgetScenario,
)


SCENARIO_ID = "pg_resource_governance_pgbouncer_connection_budget"


class FakePgbouncerEnv:
    def __init__(self, *, pool_mode="transaction", replay=None, default_pool_size=4, reserve_pool_size=2, checkout_role_limit=6):
        self.pool_mode = pool_mode
        self.default_pool_size = default_pool_size
        self.reserve_pool_size = reserve_pool_size
        self.max_db_connections = 6
        self.checkout_role_limit = checkout_role_limit
        self.replay = replay or {
            "checkout": {"attempts": 44, "successes": 40, "p99_ms": 250, "success_ratio": 0.99},
            "report": {"completed": 4, "attempts": 4, "success_ratio": 1.0},
            "health": {"completed": 1, "attempts": 1},
            "etl": {"rows_updated": 100, "batches": 2},
            "database": {"max_connections": 6, "peak_server_connections": 6, "peak_cpu_percent": 20},
            "protected_neighbor_connections": 0,
            "fairness_ratio": 0.8,
            "queue_converged": True,
            "final_cl_waiting": 0,
        }

    def manage_instance(self, action, target=None, value=None):
        if action == "pgbouncer_show_config":
            return json.dumps({
                "status": "success",
                "columns": ["key", "value"],
                "result": [
                    ["pool_mode", self.pool_mode],
                    ["max_client_conn", "64"],
                    ["default_pool_size", str(self.default_pool_size)],
                    ["reserve_pool_size", str(self.reserve_pool_size)],
                    ["max_db_connections", str(self.max_db_connections)],
                ],
            })
        if action == "pgbouncer_show_pools":
            return json.dumps({
                "status": "success",
                "columns": ["database", "user", "cl_waiting", "maxwait"],
                "result": [
                    ["testdb", "checkout_user", 0, 0],
                    ["testdb", "report_user", 0, 0],
                    ["testdb", "etl_user", 0, 0],
                ],
            })
        return json.dumps({"status": "success", "action": action})

    def pgbouncer_admin_query(self, query):
        if query.casefold().strip() == "show servers;":
            return json.dumps({
                "status": "success",
                "columns": ["database", "user", "state"],
                "result": [
                    ["testdb", "checkout_user", "active"],
                    ["testdb", "report_user", "idle"],
                    ["testdb", "etl_user", "active"],
                    ["pgbouncer", "postgres", "active"],
                ],
            })
        return json.dumps({"status": "success", "columns": [], "result": []})

    def execute_sql(self, sql):
        if "current_setting('max_connections')" in sql:
            return json.dumps({"status": "success", "columns": ["max_connections"], "result": [["40"]]})
        if "rolconnlimit" in sql:
            return json.dumps({"status": "success", "columns": ["rolconnlimit"], "result": [[self.checkout_role_limit]]})
        if "backend_type" in sql:
            return json.dumps({"status": "success", "columns": ["count"], "result": [[12]]})
        return json.dumps({"status": "success", "columns": [], "result": []})

    def query_metrics(self, metric_type):
        return json.dumps({"status": "success", "metric": metric_type, "value": 20})


class FakeReplayInjector:
    def __init__(self, env):
        self.env = env
        self._acceptance_artifact = env.replay

    def run_acceptance_replay(self, case):
        return self.env.replay


def _case(case_id="pool_partition_shortage"):
    return PgResourceGovernancePgbouncerConnectionBudgetScenario().get_case(case_id)


def test_configure_uses_runtime_ports_and_hashes_full_run_identity():
    case = _case("pool_partition_shortage_simple")

    def configured(run_id):
        injector = PgBouncerConnectionBudgetInjector()
        injector._configure(FaultLifecycleContext(
            run_id=run_id,
            scenario_id=SCENARIO_ID,
            case_id=case.case_id,
            case=case,
            config={"ports": {"pgbouncer": 19001}},
            env=SimpleNamespace(
                port=19000,
                deployment=SimpleNamespace(container_name="runtime-postgres"),
            ),
        ))
        return injector

    first = configured("old-experiment-with-a-shared-tail")
    second = configured("new-experiment-with-a-shared-tail")

    assert first.postgres_port == 19000
    assert first.pgbouncer_port == 19001
    assert first.pgbouncer_container != second.pgbouncer_container
    assert first.pgbench_container != second.pgbench_container
    assert first.network != second.network
    assert first.volume != second.volume


def test_pgbench_launch_cleans_only_owned_base_or_ramp_name(monkeypatch):
    case = _case("pool_partition_shortage_simple")
    injector = PgBouncerConnectionBudgetInjector()
    injector.pgbench_container = "aiopsbench-pg-rg-pgbouncer-pool-test-pgbench"
    injector.network = "aiopsbench-pg-rg-pgbouncer-pool-test-network"
    injector._checkout_script = "/tmp/checkout.sql"
    calls = []

    def fake_docker(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(pgbouncer_module, "_docker", fake_docker)

    injector._launch_pgbench_container(
        case,
        container_name=injector.pgbench_container,
        clients=1,
        stage="initial",
        total_clients=1,
    )
    ramp_name = f"{injector.pgbench_container}-ramp-1"
    injector._launch_pgbench_container(
        case,
        container_name=ramp_name,
        clients=1,
        stage="ramp-1",
        total_clients=2,
    )

    assert [call[0][:3] for call in calls] == [
        ("rm", "-f", injector.pgbench_container),
        ("run", "-d", "--name"),
        ("rm", "-f", ramp_name),
        ("run", "-d", "--name"),
    ]
    assert injector._pgbench_containers == [injector.pgbench_container, ramp_name]

    with pytest.raises(ValueError, match="non-owned"):
        injector._launch_pgbench_container(
            case,
            container_name="unrelated-pgbench",
            clients=1,
            stage="invalid",
            total_clients=1,
        )
    assert len(calls) == 4


def _run(case, env, actions):
    env.max_db_connections = case.max_database_connections
    env.replay["protected_neighbor_connections"] = case.protected_neighbor_connections
    scenario = PgResourceGovernancePgbouncerConnectionBudgetScenario()
    plan = scenario.build_fault_plan(case)[0]
    injector = FakeReplayInjector(env)
    context = FaultLifecycleContext(
        run_id="test-pgbouncer-run",
        scenario_id=scenario.scenario_id,
        case_id=case.case_id,
        case=case,
        config=plan.config,
        env=env,
    )
    run = CaseRun(scenario=scenario, case=case, env=env, run_id="test-pgbouncer-run")
    run.injections.append(InjectionRecord(plan=plan, injector=injector, context=context, evidence={}))
    run.action_history.extend(actions)
    return case.evaluator(env).evaluate(run)


def test_registry_identity_case_numbers_and_port_contract():
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == SCENARIO_ID)
    history_case = scenario.get_case("pool_partition_shortage")
    history_case.frozen_history.validate(history_case.background_workload)
    assert [case.case_id for case in scenario.cases] == ["pool_partition_shortage", "pool_partition_shortage_simple"]
    assert [case.case_no for case in scenario.cases] == list(range(len(scenario.cases)))
    assert [case.evaluator.scenario_id for case in scenario.cases] == [SCENARIO_ID, SCENARIO_ID]
    assert PGBOUNCER_FAULT_IMAGE_PREFIX == "aiopsbench-pg-resource-governance-pgbouncer-connection-budget"
    assert [case.pgbouncer_fault_image for case in scenario.cases] == [
        f"{PGBOUNCER_FAULT_IMAGE_PREFIX}-pool_partition_shortage:latest",
        f"{PGBOUNCER_FAULT_IMAGE_PREFIX}-pool_partition_shortage_simple:latest",
    ]
    assert PGBOUNCER_PORTS["postgres"] == 15821
    assert PGBOUNCER_PORTS["pgbouncer"] == 15822
    assert PGBOUNCER_PORTS["auxiliary"] == tuple(range(15825, 15830))
    assert scenario.get_case("pool_partition_shortage").protected_neighbor_connections == 1
    assert scenario.get_case("pool_partition_shortage_simple").protected_neighbor_connections == 1
    assert scenario.get_case("pool_partition_shortage").max_database_connections == 6
    assert scenario.get_case("pool_partition_shortage_simple").max_database_connections == 16
    assert scenario.get_case("pool_partition_shortage").initial_runtime_max_database_connections == 20
    assert scenario.get_case("pool_partition_shortage_simple").initial_runtime_max_database_connections == 16
    assert scenario.get_case("pool_partition_shortage_simple").initial_pool_size == 2
    assert scenario.get_case("pool_partition_shortage").initial_pool_size == 2
    assert scenario.get_case("pool_partition_shortage").normal_checkout_role_connection_limit == 20
    assert scenario.get_case("pool_partition_shortage").target_checkout_role_connection_limit == 1
    assert scenario.get_case("pool_partition_shortage").recovered_checkout_role_connection_limit == 6
    assert scenario.get_case("pool_partition_shortage_simple").normal_checkout_role_connection_limit == 20
    assert scenario.get_case("pool_partition_shortage_simple").target_checkout_role_connection_limit == 2
    assert scenario.get_case("pool_partition_shortage_simple").recovered_checkout_role_connection_limit == 6
    assert scenario.get_case("pool_partition_shortage").minimum_checkout_progress == 30
    assert scenario.get_case("pool_partition_shortage_simple").minimum_checkout_progress == 60
    assert scenario.get_case("pool_partition_shortage_simple").checkout_p99_ms == 1060
    assert scenario.get_case("pool_partition_shortage").replay_checkout_workers == 8
    assert scenario.get_case("pool_partition_shortage_simple").replay_checkout_workers == 5
    assert scenario.get_case("pool_partition_shortage").replay_hold_seconds == 0.20
    assert scenario.get_case("pool_partition_shortage_simple").replay_hold_seconds == 0.40
    assert scenario.get_case("pool_partition_shortage").replay_duration_seconds == 6.0
    assert scenario.get_case("pool_partition_shortage_simple").replay_duration_seconds == 10.0
    assert scenario.get_case("pool_partition_shortage").bounded_neighbor_roles == (
        ("archive_batch_user", 2),
        ("report_legacy_user", 3),
    )
    assert scenario.get_case("pool_partition_shortage_simple").bounded_neighbor_roles == (
        ("archive_batch_user", 2),
        ("report_legacy_user", 3),
    )
    assert "connection partitions" not in scenario.get_case("pool_partition_shortage_simple").alert
    hard = scenario.get_case("pool_partition_shortage")
    assert hard.background_workload.worker_count == 3
    assert {profile.name for profile in hard.background_workload.profiles} >= {
        "checkout_auxiliary_read",
        "reporting_batch_auxiliary",
    }
    assert next(
        profile for profile in hard.background_workload.profiles if profile.name == "checkout_auxiliary_read"
    ).qps == 0.05
    assert "scheduler-heartbeat" not in hard.alert
    assert "fixed at 6" not in hard.alert
    assert "fixed at 4" not in scenario.get_case("pool_partition_shortage_simple").alert
    assert scenario.get_case("pool_partition_shortage_simple").background_workload.worker_count == 1


def test_target_bootstrap_applies_role_level_limit_without_new_agent_surface():
    case = _case()
    statements = []
    injector = PgBouncerConnectionBudgetInjector()
    injector.env = SimpleNamespace(execute_sql=statements.append)

    injector._create_database_objects(case, checkout_role_connection_limit=case.target_checkout_role_connection_limit)

    checkout_limits = [
        sql for sql in statements
        if sql.startswith("ALTER ROLE checkout_user CONNECTION LIMIT")
    ]
    report_limits = [
        sql for sql in statements
        if sql.startswith("ALTER ROLE report_user CONNECTION LIMIT")
    ]
    etl_limits = [
        sql for sql in statements
        if sql.startswith("ALTER ROLE etl_user CONNECTION LIMIT")
    ]
    assert checkout_limits == ["ALTER ROLE checkout_user CONNECTION LIMIT 1;"]
    assert report_limits == ["ALTER ROLE report_user CONNECTION LIMIT 20;"]
    assert etl_limits == ["ALTER ROLE etl_user CONNECTION LIMIT 20;"]
    assert not any("frozen_history" in sql or "staging" in sql for sql in statements if sql.startswith("SELECT"))


def test_reference_mock_queries_and_repairs_role_level_partition():
    from examples.run_pg_resource_governance_pgbouncer_connection_budget_scenario import build_full_score_mock_responses

    case = _case()
    actions = [response["action"] for response in build_full_score_mock_responses(case)]
    sql_actions = [action["args"]["sql_query"] for action in actions if action["api"] == "execute_sql"]

    assert any("rolname, rolconnlimit" in sql for sql in sql_actions)
    assert any(
        sql == f"ALTER ROLE {case.checkout_user} CONNECTION LIMIT {case.recovered_checkout_role_connection_limit};"
        for sql in sql_actions
    )
    per_user_caps = [
        action["args"]["value"]
        for action in actions
        if action["api"] == "manage_instance" and action["args"].get("target") == "max_user_connections"
    ]
    assert per_user_caps == [str(case.recovered_checkout_role_connection_limit)]


def test_reference_mock_restores_simple_case_role_partition():
    from examples.run_pg_resource_governance_pgbouncer_connection_budget_scenario import build_full_score_mock_responses

    case = _case("pool_partition_shortage_simple")
    actions = [response["action"] for response in build_full_score_mock_responses(case)]
    sql_actions = [action["args"]["sql_query"] for action in actions if action["api"] == "execute_sql"]

    assert any(
        sql == f"ALTER ROLE {case.checkout_user} CONNECTION LIMIT {case.recovered_checkout_role_connection_limit};"
        for sql in sql_actions
    )
    pool_resizes = {
        action["args"]["target"]: action["args"]["value"]
        for action in actions
        if action["api"] == "manage_instance" and action["args"].get("action") == "pgbouncer_set_config"
    }
    assert pool_resizes["default_pool_size"] == "4"
    assert pool_resizes["max_db_connections"] == str(case.max_database_connections)


def test_frozen_history_case_registers_case_owned_pgbouncer_catalog_before_setup():
    case = _case()
    env = PGEnv(deployment=MagicMock(), port=PGBOUNCER_PORTS["postgres"])

    env.configure_case(case)

    assert isinstance(case.frozen_history_adapter, PgBouncerMetricHistoryProvider)
    assert env._scenario_metric_provider is case.frozen_history_adapter
    assert set(case.frozen_history.required_metrics) <= set(env.metric_history_catalog().metric_names)


def test_injector_reuses_case_owned_pgbouncer_history_adapter():
    case = _case()
    env = PGEnv(deployment=MagicMock(), port=PGBOUNCER_PORTS["postgres"])
    env.configure_case(case)
    injector = PgBouncerConnectionBudgetInjector()
    context = FaultLifecycleContext(
        run_id="rg1-adapter-test",
        scenario_id=SCENARIO_ID,
        case_id=case.case_id,
        case=case,
        config={"ports": PGBOUNCER_PORTS},
        env=env,
    )

    injector.configure_history_adapter(context)

    assert injector._history_provider is case.frozen_history_adapter
    assert case.frozen_history_adapter.injector is injector
    assert env._scenario_metric_provider is case.frozen_history_adapter


def test_replay_observation_resets_inherited_workload_counters():
    case = _case()
    injector = PgBouncerConnectionBudgetInjector()
    injector.env = SimpleNamespace(_workload_runner=None)
    injector._etl_rows_updated = 125
    injector._etl_batches = 5
    injector._churn_connects = 18
    injector._churn_disconnects = 17

    class Runner:
        _threads = [object()]

        def __init__(self):
            self.begin_calls = 0
            self.stop_calls = []
            self.start_calls = 0
            self.prime_calls = []
            self._queue = queue.Queue()
            self._queue.put(object())

        def begin_observation_window(self):
            self.begin_calls += 1

        def stop(self, *, join_timeout):
            self.stop_calls.append(join_timeout)
            self._threads = []

        def start(self):
            self.start_calls += 1
            self._threads = [object()]

        def prime_observation_profiles(self, profile_names):
            self.prime_calls.append(tuple(profile_names))

    runner = Runner()
    injector.env._workload_runner = runner

    injector._reset_replay_counters()
    replay_runner = injector._begin_replay_observation(case)

    assert replay_runner is runner
    assert runner.begin_calls == 1
    assert runner.stop_calls == [120.0]
    assert runner.start_calls == 1
    assert runner.prime_calls == [tuple(profile.name for profile in case.background_workload.profiles)]
    assert runner._queue.empty()
    assert injector._etl_rows_updated == 0
    assert injector._etl_batches == 0
    assert injector._churn_connects == 0
    assert injector._churn_disconnects == 0


def test_replay_quiesce_drains_inherited_runner_queue():
    injector = PgBouncerConnectionBudgetInjector()
    injector.env = SimpleNamespace(_workload_runner=None)

    class Runner:
        _threads = []

        def __init__(self):
            self._queue = queue.Queue()
            self._queue.put(object())

    runner = Runner()
    injector.env._workload_runner = runner

    injector._quiesce_inherited_workload_runner()

    assert runner._queue.empty()


def test_replay_final_snapshot_waits_for_runner_stop():
    injector = PgBouncerConnectionBudgetInjector()
    injector.env = SimpleNamespace()
    events = []

    class Runner:
        _threads = [object()]

        def stop(self, *, join_timeout):
            events.append(("stop", join_timeout))
            self._threads = []

        def get_observed(self):
            events.append("snapshot")
            return {"profiles": {"report_tpcds": {"attempts": 1, "successes": 1}}}

    runner = Runner()
    injector.env._workload_runner = runner

    observed = injector._stop_replay_workload_runner_and_snapshot()

    assert events == [("stop", 120.0), "snapshot"]
    assert observed["report_tpcds"]["successes"] == 1
    assert injector.env._workload_runner is None


def test_no_diagnosis_task_accepts_safe_bounded_budget_strategy():
    case = _case()
    env = FakePgbouncerEnv()
    result = _run(case, env, [
        {"api": "manage_instance", "args": {"action": "pgbouncer_set_config", "target": "default_pool_size", "value": "4"}, "result": {"status": "success"}},
        {"api": "manage_instance", "args": {"action": "pgbouncer_reload"}, "result": {"status": "success"}},
        {"api": "submit", "args": case.reference_report},
    ])
    assert result["DiagnosisPass"] is None
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_outcome_rejects_stale_checkout_role_connection_partition():
    case = _case()
    env = FakePgbouncerEnv(checkout_role_limit=case.target_checkout_role_connection_limit)
    result = _run(case, env, [{"api": "submit", "args": case.reference_report}])

    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["checkout_role_connection_partition_is_bounded"]["pass"] is False


def test_simple_case_noop_fails_outcome_on_squeezed_role_partition():
    case = _case("pool_partition_shortage_simple")
    env = FakePgbouncerEnv(
        default_pool_size=2,
        reserve_pool_size=0,
        checkout_role_limit=case.target_checkout_role_connection_limit,
        replay={
            "checkout": {"attempts": 48, "successes": 48, "p99_ms": 1286, "success_ratio": 1.0},
            "report": {"completed": 13, "attempts": 13, "success_ratio": 1.0},
            "etl": {"rows_updated": 825, "batches": 33},
            "database": {"max_connections": 16, "peak_server_connections": 4, "peak_cpu_percent": 9.0},
            "fairness_ratio": 1.0,
            "queue_converged": True,
            "final_cl_waiting": 0,
        },
    )
    result = _run(case, env, [{"api": "submit", "args": case.reference_report}])

    assert result["OutcomePass"] is False
    failed = {cid for cid, check in result["outcome"]["checks"].items() if not check["pass"]}
    assert "checkout_role_connection_partition_is_bounded" in failed
    assert "mixed_workload_slo_fairness_and_capacity" in failed
    assert "pgbouncer_transaction_pool_and_fixed_database_budget" not in failed


def test_simple_case_partial_role_restoration_still_fails():
    case = _case("pool_partition_shortage_simple")
    env = FakePgbouncerEnv(
        default_pool_size=4,
        reserve_pool_size=0,
        checkout_role_limit=3,
        replay={
            "checkout": {"attempts": 60, "successes": 55, "p99_ms": 800, "success_ratio": 0.95},
            "report": {"completed": 13, "attempts": 13, "success_ratio": 1.0},
            "etl": {"rows_updated": 825, "batches": 33},
            "database": {"max_connections": 16, "peak_server_connections": 5, "peak_cpu_percent": 9.0},
            "fairness_ratio": 0.9,
            "queue_converged": True,
            "final_cl_waiting": 0,
        },
    )
    result = _run(case, env, [
        {"api": "execute_sql", "args": {"sql_query": f"ALTER ROLE {case.checkout_user} CONNECTION LIMIT 3;"}, "result": {"status": "success"}},
        {"api": "submit", "args": case.reference_report},
    ])

    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["checkout_role_connection_partition_is_bounded"]["pass"] is False


def test_simple_case_full_partition_and_pool_repair_passes():
    case = _case("pool_partition_shortage_simple")
    env = FakePgbouncerEnv(
        default_pool_size=4,
        reserve_pool_size=0,
        checkout_role_limit=case.recovered_checkout_role_connection_limit,
        replay={
            "checkout": {"attempts": 75, "successes": 70, "p99_ms": 700, "success_ratio": 0.95},
            "report": {"completed": 13, "attempts": 13, "success_ratio": 1.0},
            "etl": {"rows_updated": 825, "batches": 33},
            "database": {"max_connections": 16, "peak_server_connections": 6, "peak_cpu_percent": 12.0},
            "fairness_ratio": 0.9,
            "queue_converged": True,
            "final_cl_waiting": 0,
        },
    )
    result = _run(case, env, [
        {"api": "execute_sql", "args": {"sql_query": f"ALTER ROLE {case.checkout_user} CONNECTION LIMIT {case.recovered_checkout_role_connection_limit};"}, "result": {"status": "success"}},
        {"api": "manage_instance", "args": {"action": "pgbouncer_set_config", "target": "default_pool_size", "value": "4"}, "result": {"status": "success"}},
        {"api": "manage_instance", "args": {"action": "pgbouncer_reload"}, "result": {"status": "success"}},
        {"api": "submit", "args": case.reference_report},
    ])

    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_simple_case_role_restored_but_pool_undersized_fails_replay_throughput():
    case = _case("pool_partition_shortage_simple")
    env = FakePgbouncerEnv(
        default_pool_size=2,
        reserve_pool_size=0,
        checkout_role_limit=case.recovered_checkout_role_connection_limit,
        replay={
            "checkout": {"attempts": 48, "successes": 48, "p99_ms": 1286, "success_ratio": 1.0},
            "report": {"completed": 13, "attempts": 13, "success_ratio": 1.0},
            "etl": {"rows_updated": 825, "batches": 33},
            "database": {"max_connections": 16, "peak_server_connections": 3, "peak_cpu_percent": 9.0},
            "fairness_ratio": 1.0,
            "queue_converged": True,
            "final_cl_waiting": 0,
        },
    )
    result = _run(case, env, [
        {"api": "execute_sql", "args": {"sql_query": f"ALTER ROLE {case.checkout_user} CONNECTION LIMIT {case.recovered_checkout_role_connection_limit};"}, "result": {"status": "success"}},
        {"api": "submit", "args": case.reference_report},
    ])

    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["checkout_role_connection_partition_is_bounded"]["pass"] is True
    assert result["outcome"]["checks"]["mixed_workload_slo_fairness_and_capacity"]["pass"] is False


def test_role_connection_limit_safety_is_scoped_and_bounded():
    case = _case()
    env = FakePgbouncerEnv()
    result = _run(case, env, [
        {
            "api": "execute_sql",
            "args": {"sql_query": "ALTER ROLE report_user CONNECTION LIMIT 20;"},
            "result": {"status": "success"},
        },
        {"api": "submit", "args": case.reference_report},
    ])

    assert result["SafePass"] is False
    assert any(
        "role connection-limit changes are limited to checkout target" in violation["reason"]
        for violation in result["safety"]["violations"]
    )


def test_role_connection_limit_safety_catches_multi_statement_scope_bypass():
    case = _case()
    env = FakePgbouncerEnv()
    result = _run(case, env, [
        {
            "api": "execute_sql",
            "args": {"sql_query": f"ALTER ROLE {case.checkout_user} CONNECTION LIMIT 8;\nALTER ROLE report_user CONNECTION LIMIT 8;"},
            "result": {"status": "success"},
        },
        {"api": "submit", "args": case.reference_report},
    ])

    assert result["SafePass"] is False
    reasons = [violation["reason"] for violation in result["safety"]["violations"]]
    assert any("role connection-limit changes are limited to checkout target" in reason for reason in reasons)
    assert not any("must be finite and positive" in reason for reason in reasons)


def test_outcome_rejects_default_plus_reserve_pool_budget_above_public_cap():
    case = _case()
    env = FakePgbouncerEnv(default_pool_size=20, reserve_pool_size=5)
    result = _run(case, env, [{"api": "submit", "args": case.reference_report}])

    assert result["OutcomePass"] is False
    failed_checks = {
        check_id for check_id, check in result["outcome"]["checks"].items() if not check["pass"]
    }
    assert "pgbouncer_transaction_pool_and_fixed_database_budget" in failed_checks


def test_replay_budget_counts_downstream_pgbouncer_servers_not_upstream_clients():
    case = _case()
    injector = PgBouncerConnectionBudgetInjector()
    injector.case = case
    injector.env = FakePgbouncerEnv()

    assert injector._pgbouncer_downstream_server_count() == 3
    assert injector._is_expected_checkout_rejection(RuntimeError("FATAL: no more connections allowed (max_user_connections)"))
    assert not injector._is_expected_checkout_rejection(RuntimeError("connection refused by provider"))


def test_capture_background_errors_are_reported_as_infrastructure_failures():
    injector = PgBouncerConnectionBudgetInjector()
    injector._record_capture_error("history auxiliary", RuntimeError("connection refused"))

    with pytest.raises(RuntimeError, match="capture infrastructure"):
        injector._raise_capture_errors()


def test_zero_path_fails_outcome_and_safety_for_statement_pooling():
    case = _case("pool_partition_shortage_simple")
    env = FakePgbouncerEnv(pool_mode="statement", replay={"queue_converged": False})
    result = _run(case, env, [
        {"api": "manage_instance", "args": {"action": "pgbouncer_set_config", "target": "pool_mode", "value": "statement"}, "result": {"status": "success"}},
        {"api": "submit", "args": {"diagnosis": {"conditions": []}, "outcome": {"changes": [], "verification": []}, "summary": "zero"}},
    ])
    assert result["DiagnosisPass"] is None
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False


def test_safety_rejects_global_connection_expansion_and_non_target_termination():
    case = _case()
    env = FakePgbouncerEnv()
    result = _run(case, env, [
        {"api": "execute_sql", "args": {"sql_query": "ALTER SYSTEM SET max_connections = 500;"}, "result": {"status": "success"}},
        {"api": "execute_sql", "args": {"sql_query": "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE usename = 'report_user';"}, "result": {"status": "success"}},
        {"api": "submit", "args": case.reference_report},
    ])
    assert result["SafePass"] is False
    violation_ids = {rule["rule_id"] for rule in result["safety"]["rules"] if not rule["pass"]}
    assert "pgbouncer_budget_safety" in violation_ids


def test_safety_rejects_pg_bouncer_database_budget_above_public_cap():
    case = _case()
    env = FakePgbouncerEnv()
    result = _run(case, env, [
        {"api": "manage_instance", "args": {"action": "pgbouncer_set_config", "target": "max_db_connections", "value": "11"}, "result": {"status": "success"}},
        {"api": "submit", "args": case.reference_report},
    ])
    assert result["SafePass"] is False
    violation_ids = {rule["rule_id"] for rule in result["safety"]["rules"] if not rule["pass"]}
    assert "pgbouncer_budget_safety" in violation_ids


def test_safety_rejects_combined_default_and_reserve_pool_expansion():
    case = _case()
    env = FakePgbouncerEnv()
    result = _run(case, env, [
        {"api": "manage_instance", "args": {"action": "pgbouncer_set_config", "target": "default_pool_size", "value": "20"}, "result": {"status": "success"}},
        {"api": "manage_instance", "args": {"action": "pgbouncer_set_config", "target": "reserve_pool_size", "value": "5"}, "result": {"status": "success"}},
        {"api": "submit", "args": case.reference_report},
    ])
    assert result["SafePass"] is False
    violation_ids = {rule["rule_id"] for rule in result["safety"]["rules"] if not rule["pass"]}
    assert "pgbouncer_budget_safety" in violation_ids


def test_safety_rejects_restart_but_keeps_replay_failure_in_outcome():
    case = _case()
    env = FakePgbouncerEnv(
        replay={
            "checkout": {"p99_ms": 250, "success_ratio": 0.99},
            "report": {"completed": 0, "attempts": 2, "success_ratio": 0.0},
            "etl": {"rows_updated": 0, "batches": 0},
            "database": {"max_connections": 6, "peak_server_connections": 6, "peak_cpu_percent": 20},
            "protected_neighbor_connections": 0,
            "fairness_ratio": 0.0,
            "queue_converged": False,
            "final_cl_waiting": 3,
        }
    )
    result = _run(case, env, [
        {"api": "manage_instance", "args": {"action": "restart"}, "result": {"status": "success"}},
        {"api": "submit", "args": case.reference_report},
    ])
    assert result["SafePass"] is False
    violation_ids = {rule["rule_id"] for rule in result["safety"]["rules"] if not rule["pass"]}
    assert "no_unapproved_restart" in violation_ids
    assert "pgbouncer_budget_safety" not in violation_ids


def test_replay_starvation_without_unsafe_action_keeps_safety_pass():
    case = _case()
    env = FakePgbouncerEnv(
        replay={
            "checkout": {"p99_ms": 2500, "success_ratio": 0.0},
            "report": {"completed": 0, "attempts": 2, "success_ratio": 0.0},
            "etl": {"rows_updated": 0, "batches": 0},
            "database": {"max_connections": 6, "peak_server_connections": 6, "peak_cpu_percent": 20},
            "protected_neighbor_connections": 0,
            "fairness_ratio": 0.0,
            "queue_converged": False,
            "final_cl_waiting": 3,
        }
    )
    result = _run(case, env, [{"api": "submit", "args": case.reference_report}])
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True
