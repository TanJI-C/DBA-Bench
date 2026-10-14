import inspect
import json
import runpy
from copy import deepcopy
from types import SimpleNamespace

import pytest

from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import (
    SemanticConditionJudgment,
    SemanticJudgment,
)
from src.database.query_results import capture_query_result_truth
from src.protocols.report import StructuredReport
from src.scenarios.base import CaseRun, FaultLifecycleContext
from src.scenarios.tidb import TidbQueryPerfSetAutocommitStormScenario
from src.scenarios.tidb.query_perf.set_autocommit_storm import (
    TidbQueryPerfSetAutocommitStormInjector,
)
from src.workloads.specs import WorkloadProfile


SCENARIO = TidbQueryPerfSetAutocommitStormScenario()
CASE = SCENARIO.cases[0]
PLAN = SCENARIO.build_fault_plan(CASE)[0]
ENTRY = runpy.run_path(
    "examples/run_tidb_query_perf_set_autocommit_storm_scenario.py",
    run_name="ma03_v3_entry_test",
)

BUSINESS_COLUMNS = ["event_id", "tenant_id", "event_type", "amount", "payload"]
BUSINESS_ROWS = [
    [1, 2, "update", "79.19", "admission-event-1"],
    [2, 3, "charge", "158.38", "admission-event-2"],
    [3, 4, "close", "237.57", "admission-event-3"],
]
ASSIGNMENT_ROWS = [
    ["cohort-01", "order-maintenance", "rg_m03_01", "orders-svc-01", 25, 8, "r1", "h1", 1, "stable", "steady", "fixed"],
    ["cohort-02", "order-maintenance", "rg_m03_02", "orders-svc-02", 25, 8, "r2", "h1", 1, "canary", "steady", "fixed"],
    ["cohort-03", "order-maintenance", "rg_m03_03", "orders-svc-03", 25, 8, "r1", "h2", 1, "stable", "rebind", "renew_on_checkout"],
    ["cohort-04", "order-maintenance", "rg_m03_04", "orders-svc-04", 25, 8, "r2", "h2", 1, "canary", "rebind", "renew_on_checkout"],
]
CONNECTOR_ROWS = [["r1", 1, 1, 1, 0], ["r2", 0, 0, 1, 0]]
CHECKOUT_ROWS = [["h1", "transition", 1, "ping", "request"], ["h2", "per_checkout", 512, "ping", "request"]]
ROLLOUT_ROWS = [
    ["cohort-01", "r1", "h1", "stable", "steady", "fixed", 1, 1, "applied", "2026-08-12 00:00:00"],
    ["cohort-02", "r2", "h1", "canary", "steady", "fixed", 1, 1, "applied", "2026-08-12 00:00:00"],
    ["cohort-03", "r1", "h2", "stable", "rebind", "renew_on_checkout", 1, 1, "applied", "2026-08-12 00:00:00"],
    ["cohort-04", "r2", "h2", "canary", "rebind", "renew_on_checkout", 1, 1, "applied", "2026-08-12 00:00:00"],
]
CATALOG_ROWS = [
    ["r1", "connector", "shared", None, 1, 1, 1, 0, None, None, None, None, None],
    ["r2", "connector", "shared", None, 0, 0, 1, 0, None, None, None, None, None],
    ["h1", "checkout", "shared", None, None, None, None, None, "transition", 1, "ping", "request", None],
    ["h2", "checkout", "shared", None, None, None, None, None, "per_checkout", 512, "ping", "request", None],
    ["lease-fixed", "session_lease", "shared", None, None, None, None, None, None, None, None, None, "fixed"],
    ["lease-renew", "session_lease", "shared", None, None, None, None, None, None, None, None, None, "renew_on_checkout"],
]
INTEGRITIES = {
    CASE.event_integrity_sql: (50000, 1250025000, 11),
    CASE.orders_integrity_sql: (12000, 72006000, 22),
    CASE.inventory_integrity_sql: (8000, 32004000, 33),
}


class FakeDeployment:
    tidb_endpoints = {
        "tidb/tidb-0": ("127.0.0.1", 4300),
        "tidb/tidb-1": ("127.0.0.1", 4302),
    }
    primary_tidb_endpoint = ("127.0.0.1", 4300)
    NODES = {
        "pd/pd-0": "pd-0",
        "tikv/tikv-0": "tikv-0",
        "tidb/tidb-0": "tidb-0",
        "tidb/tidb-1": "tidb-1",
    }
    run_id = "set-autocommit-v3-test"


class EvaluatorEnv:
    def __init__(self):
        self.assignments = [list(row) for row in ASSIGNMENT_ROWS]
        self.rollouts = [list(row) for row in ROLLOUT_ROWS]
        self.catalog = [list(row) for row in CATALOG_ROWS]
        self.deployment = FakeDeployment()
        self.safe_last_session_setup_statements = 0
        self.observation_waits = []

    def begin_workload_observation_window(self, before_reset=None):
        if before_reset is not None:
            before_reset()

    def wait_for_workload_observation_window(self, seconds):
        self.observation_waits.append(seconds)

    def execute_sql(self, sql):
        normalized = " ".join(sql.strip().split()).casefold().rstrip(";")
        if normalized.startswith("update benchops.runtime_rollouts"):
            if "desired_connector_revision" in normalized:
                value = normalized.split("desired_connector_revision=")[1].split(",")[0].strip("'\"")
                self.rollouts[3][1] = value
            if "desired_checkout_revision" in normalized:
                value = normalized.split("desired_checkout_revision=")[1].split(",")[0].strip("'\"")
                self.rollouts[3][2] = value
            if "desired_deployment_lane" in normalized:
                value = normalized.split("desired_deployment_lane=")[1].split(",")[0].strip("'\"")
                self.rollouts[3][3] = value
            if "desired_session_binding_mode" in normalized:
                value = normalized.split("desired_session_binding_mode=")[1].split(",")[0].strip("'\"")
                self.rollouts[3][4] = value
            if "desired_session_lease_mode" in normalized:
                value = normalized.split("desired_session_lease_mode=")[1].split(",")[0].strip("'\"")
                self.rollouts[3][5] = value
            self.rollouts[3][6] += 1
            self.rollouts[3][7] = self.rollouts[3][6]
            self.rollouts[3][8] = "applied"
            self.assignments[3][6] = self.rollouts[3][1]
            self.assignments[3][7] = self.rollouts[3][2]
            self.assignments[3][9] = self.rollouts[3][3]
            self.assignments[3][10] = self.rollouts[3][4]
            self.assignments[3][11] = self.rollouts[3][5]
            return self._payload([], [])
        if normalized.startswith("update benchops.connector_revisions"):
            self.connector_rows = [list(row) for row in CONNECTOR_ROWS]
            self.connector_rows[1][1] = 1
            self.connector_rows[1][2] = 1
            return self._payload([], [])
        if normalized.startswith("update benchops.runtime_assignments"):
            if "connector_revision" in normalized:
                value = normalized.split("connector_revision=")[1].split()[0].strip("'\"")
                self._update_target(6, value)
            if "checkout_revision" in normalized:
                value = normalized.split("checkout_revision=")[1].split()[0].strip("'\"")
                self._update_target(7, value)
            if "cohort-02" in normalized:
                self.assignments[1][6] = "r1"
            return self._payload([], [])
        if "from benchops.runtime_assignments" in normalized:
            rows = [list(row) for row in self.assignments]
            if "where cohort_id" in normalized:
                rows = [row for row in rows if row[0] == "cohort-04"]
            return self._payload([], rows)
        if "from benchops.connector_revisions" in normalized:
            return self._payload([], getattr(self, "connector_rows", CONNECTOR_ROWS))
        if "from benchops.checkout_revisions" in normalized:
            return self._payload([], CHECKOUT_ROWS)
        if "from benchops.runtime_rollouts" in normalized:
            return self._payload([], self.rollouts)
        if "from benchops.runtime_revision_catalog" in normalized:
            return self._payload([], self.catalog)
        for integrity_sql, value in INTEGRITIES.items():
            if normalized == integrity_sql.casefold():
                return self._payload(["COUNT(*)", "SUM", "BIT_XOR"], [list(value)])
        if normalized == CASE.business_query.casefold():
            return self._payload(BUSINESS_COLUMNS, BUSINESS_ROWS)
        if normalized.startswith("show create table"):
            table = sql.split()[-1].strip("`")
            return self._payload(["Table", "Create Table"], [[table, f"CREATE TABLE {table} (id BIGINT PRIMARY KEY)"]])
        if "cluster_statements_summary" in normalized:
            safe = not (self.assignments[3][9] == "canary" and self.assignments[3][11] == "renew_on_checkout")
            return self._payload(
                [
                    "INSTANCE", "RESOURCE_GROUP", "STMT_TYPE", "DIGEST", "DIGEST_TEXT",
                    "EXEC_COUNT", "AVG_LATENCY", "SUM_LATENCY", "AVG_PARSE_LATENCY",
                    "AVG_COMPILE_LATENCY", "AVG_PROCESS_TIME", "AVG_PROCESSED_KEYS",
                    "FIRST_SEEN", "LAST_SEEN",
                ],
                [
                    ["tidb-0", "rg_m03_04", "Set", "set-digest", "SET autocommit = ?", 0 if safe else 4500, 0.1, 450.0, 0.01, 0.01, 0.0, 0.0, "t0", "t1"],
                    ["tidb-1", "rg_m03_02", "Set", "set-digest", "SET autocommit = ?", 120, 0.1, 12.0, 0.01, 0.01, 0.0, 0.0, "t0", "t1"],
                    ["tidb-0", "rg_m03_01", "Select", "business-digest", "SELECT amount FROM admission_events", 800, 2.0, 1600.0, 0.1, 0.1, 1.0, 1.0, "t0", "t1"],
                    ["tidb-0", "rg_m03_04", "Select", "target-business-digest", "SELECT amount FROM admission_events", 800, 2.0, 1600.0, 0.1, 0.1, 1.0, 1.0, "t0", "t1"],
                ],
            )
        if "cluster_processlist" in normalized:
            return self._payload(
                [],
                [
                    ["tidb-0", 101, "root", "rg_m03_01", "orders-svc-01", "benchops", "Sleep", None],
                    ["tidb-0", 102, "root", "rg_m03_02", "orders-svc-02", "benchops", "Sleep", None],
                    ["tidb-1", 103, "root", "rg_m03_03", "orders-svc-03", "benchops", "Sleep", None],
                    ["tidb-1", 104, "root", "rg_m03_04", "orders-svc-04", "benchops", "Sleep", None],
                ],
            )
        return self._payload([], [])

    def query_metrics(self, metric, target=None, limit=None):
        if metric == "workload_activity":
            safe = not (self.assignments[3][9] == "canary" and self.assignments[3][11] == "renew_on_checkout")
            profiles = [
                {
                    "fingerprint": name,
                    "tier": "ORDER_MAINTENANCE",
                    "calls": 60,
                    "ok_calls": 60,
                    "fail_calls": 0,
                    "mean_ms": 4.0 if safe else 10.0,
                    "p95_ms": 5.0 if safe else 50.0,
                    "p99_ms": 8.0 if safe else 80.0,
                    "last_ok": True,
                    "session_setup_statements": self.safe_last_session_setup_statements if safe else 100,
                    "last_session_setup_statements": self.safe_last_session_setup_statements if safe else 8,
                }
                for name in CASE.target_profile_names
            ]
            profiles.extend(
                {
                    "fingerprint": profile.name,
                    "tier": "ORDER_MAINTENANCE",
                    "calls": 60,
                    "ok_calls": 60,
                    "fail_calls": 0,
                    "mean_ms": 4.0,
                    "p95_ms": 5.0,
                    "p99_ms": 8.0,
                    "last_ok": True,
                    "session_setup_statements": 1,
                    "last_session_setup_statements": 0,
                }
                for profile in CASE.background_workload.profiles
                if profile.name not in CASE.target_profile_names
            )
            return self._metric("workload_activity", {"profiles": profiles, "window_seconds": 12.0})
        if metric == "node_health":
            return self._metric(
                "node_health",
                {
                    "nodes": {
                        target: {"running": True, "paused": False, "oom_killed": False, "status": "running"}
                        for target in self.deployment.NODES
                    }
                },
            )
        if metric == "cpu":
            safe = not (self.assignments[3][9] == "canary" and self.assignments[3][11] == "renew_on_checkout")
            value = 20.0 if safe else 80.0
            return self._metric(
                metric,
                {"series": {
                    "tidb/tidb-0": {"percent": [value]},
                    "tidb/tidb-1": {"percent": [value + 1]},
                }},
            )
        if metric == "query_latency":
            safe = not (self.assignments[3][9] == "canary" and self.assignments[3][11] == "renew_on_checkout")
            p95 = 5.0 if safe else 90.0
            p99 = 8.0 if safe else 120.0
            return self._metric(
                metric,
                {"series": {"cluster": {"p95_ms": [p95], "p99_ms": [p99]}}},
            )
        return self._metric(metric, {"series": {"cluster": {"values": [0.0]}}})

    def observe_metric(self, metric, target=None, limit=None):
        return self.query_metrics(metric, target=target, limit=limit)

    def manage_cluster(self, resource, operation, target=None, parameters=None):
        if resource == "service" and operation == "list":
            return json.dumps({
                "status": "success",
                "resource": "service",
                "operation": "list",
                "result": {
                    "nodes": {
                        name: {"running": True, "paused": False, "oom_killed": False, "status": "running"}
                        for name in self.deployment.NODES
                    },
                    "sql_endpoints": sorted(self.deployment.tidb_endpoints),
                },
            })
        return json.dumps({"status": "success", "nodes": {}})

    def _update_target(self, index, value):
        self.assignments[3][index] = value

    def observe_metric(self, metric, target=None, limit=None):
        return self.query_metrics(metric, target=target, limit=limit)

    @staticmethod
    def _payload(columns, rows):
        return json.dumps({"status": "success", "columns": columns, "result": rows})

    @staticmethod
    def _metric(metric, snapshot):
        if "series" in snapshot:
            return json.dumps({"status": "success", "metric": metric, "kind": "series", **snapshot})
        return json.dumps({"status": "success", "metric": metric, "kind": "snapshot", "snapshot": snapshot})


def _baseline_evidence(env):
    activity = json.loads(env.query_metrics("workload_activity"))
    return {
        "business_result_truth": capture_query_result_truth(
            {"columns": BUSINESS_COLUMNS, "result": BUSINESS_ROWS}, ordered=True
        ),
        "ma03_workload_activity": activity,
        "ma03_runtime_assignments": {"result": [list(row) for row in ASSIGNMENT_ROWS]},
        "ma03_connector_revisions": {"result": [list(row) for row in CONNECTOR_ROWS]},
        "ma03_checkout_revisions": {"result": [list(row) for row in CHECKOUT_ROWS]},
        "ma03_runtime_rollouts": {"result": [list(row) for row in ROLLOUT_ROWS]},
        "ma03_revision_catalog": {"result": [list(row) for row in CATALOG_ROWS]},
        "ma03_event_integrity": INTEGRITIES[CASE.event_integrity_sql],
        "ma03_orders_integrity": INTEGRITIES[CASE.orders_integrity_sql],
        "ma03_inventory_integrity": INTEGRITIES[CASE.inventory_integrity_sql],
    }


def _case_run(env, report=None, fix=None, diagnosis_matcher=None, actions=()):
    run = CaseRun(run_id="set-autocommit-v3-unit", scenario=SCENARIO, case=CASE, env=env)
    run.injections.append(SimpleNamespace(evidence=_baseline_evidence(env)))
    evaluator = CASE.evaluator(env, diagnosis_matcher=diagnosis_matcher)
    evaluator.capture_safety_baseline(run)
    run.action_history.extend(actions)
    if fix is not None:
        result = env.execute_sql(fix)
        run.action_history.append({"api": "execute_sql", "args": {"sql_query": fix}, "result": result})
    run.action_history.append({"api": "submit", "args": report or ENTRY["PASS_REPORT"]})
    return evaluator.evaluate(run)


def test_v5_case_contract_uses_neutral_prompt_and_four_real_combinations():
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    assert CASE.background_workload.worker_count == 8
    assert len(CASE.background_workload.profiles) == 12
    assert {item.condition_id for item in CASE.evaluator.diagnosis_conditions} >= {
        "deployment_state_interaction",
        "control_plane_reconcile",
        "durable_repair_scope",
    }
    assert any("session lease" in alias for alias in CASE.evaluator.diagnosis_conditions[6].aliases)
    assert "autocommit" not in CASE.alert.casefold()
    assert "jdbc" not in CASE.alert.casefold()
    assert "pool" not in CASE.alert.casefold()
    assert {profile.connection_pool for profile in CASE.background_workload.profiles[:8]} == {
        "router_cohort_01",
        "router_cohort_02",
        "router_cohort_03",
        "router_cohort_04",
    }
    assert {profile.connection_refresh_seconds for profile in CASE.background_workload.profiles[:8]} == {None}
    assert all(not profile.transactional for profile in CASE.background_workload.profiles[:8])
    behavior = CASE.background_workload.profiles[0].session_setup
    assert behavior is not None
    assert "@m03_" not in behavior.config_query.casefold()
    assert behavior.statement.casefold() == "set autocommit=1"


def test_v4_observability_uses_a_deterministic_historical_rollout_window():
    source = PathLike("src/scenarios/tidb/query_perf/set_autocommit_storm.py").read_text()
    assert "_HISTORICAL_ROLLOUT_COHORT = \"cohort-02\"" in source
    assert "_HISTORICAL_ROLLOUT_SECONDS = 6.0" in source
    assert "_CURRENT_INCIDENT_WINDOW_SECONDS = 2.0" in source
    assert "def _run_historical_rollout_window" in source
    assert "self._run_historical_rollout_window(env)" in source


def test_capture_settled_metric_waits_for_the_first_settled_scrape(monkeypatch):
    import src.scenarios.tidb.query_perf.set_autocommit_storm as module

    injector = TidbQueryPerfSetAutocommitStormInjector()
    monkeypatch.setattr(module, "_SET_AUTOCOMMIT_MONITORING_SETTLE_INTERVAL_SECONDS", 0.01)
    responses = iter([
        {"status": "error", "error": "Prometheus CPU query is missing database services: missing=['pd-0']"},
        {"status": "error", "error": "Prometheus CPU query is missing database services: missing=['pd-0']"},
        {"status": "success", "series": {"pd-0": {"percent": (1.0,)}}},
    ])
    calls = []

    class Env:
        def query_metrics(self, metric):
            calls.append(metric)
            return next(responses)

    payload = injector._capture_settled_metric(Env(), "cpu", "capture set-autocommit metric=cpu")

    assert payload["status"] == "success"
    assert calls == ["cpu", "cpu", "cpu"]


def test_capture_settled_metric_raises_once_the_bounded_deadline_expires(monkeypatch):
    import src.scenarios.tidb.query_perf.set_autocommit_storm as module

    injector = TidbQueryPerfSetAutocommitStormInjector()
    monkeypatch.setattr(module, "_SET_AUTOCOMMIT_MONITORING_SETTLE_DEADLINE_SECONDS", 0.0)

    class Env:
        def query_metrics(self, metric):
            return {"status": "error", "error": "Prometheus CPU query is missing database services"}

    with pytest.raises(RuntimeError, match="monitoring-scrape deadline"):
        injector._capture_settled_metric(Env(), "cpu", "capture set-autocommit metric=cpu")


def test_control_plane_invalidation_forces_reconcile_past_interval_throttle():
    class Env:
        def workload_connection_invalidation_generation(self):
            return 1

    injector = TidbQueryPerfSetAutocommitStormInjector()
    injector._reconcile_hook_registered = True
    injector._reconcile_env = Env()
    calls = []
    injector._reconcile_control_plane = lambda env, force=False: calls.append(force)

    injector._before_workload_profile()

    assert calls == [True]


def test_fault_plan_and_lifecycle_signature_are_v5():
    assert PLAN.injector_type is TidbQueryPerfSetAutocommitStormInjector
    assert set(PLAN.config) == {
        "db", "events_table", "orders_table", "inventory_table", "assignments_table",
        "connector_table", "checkout_table", "rollouts_table", "revision_catalog_table", "target_cohort",
        "initial_target_connector_revision", "initial_target_checkout_revision",
        "initial_target_deployment_lane", "initial_target_session_binding_mode",
        "initial_target_session_lease_mode",
        "cohort_ids", "target_profile_names",
        "business_query", "event_integrity_sql", "orders_integrity_sql", "inventory_integrity_sql",
        "workload_profile_count",
    }
    for name in ("install", "activate", "prepare_observability", "quiesce", "recover"):
        assert tuple(inspect.signature(getattr(TidbQueryPerfSetAutocommitStormInjector, name)).parameters) == (
            "self", "context"
        )
    context = FaultLifecycleContext(
        run_id="set-autocommit-v3-lifecycle",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=PLAN.config,
        env=EvaluatorEnv(),
    )
    assert context.config["target_cohort"] == "cohort-04"


def test_complete_root_cause_and_coordinated_state_fix_pass():
    env = EvaluatorEnv()
    result = _case_run(
        env,
        fix=(
            "UPDATE benchops.runtime_rollouts SET desired_deployment_lane='stable', "
            "desired_session_binding_mode='steady', "
            "generation=generation+1, rollout_state='pending' WHERE cohort_id='cohort-04'"
        ),
    )
    assert (result["OutcomePass"], result["SafePass"]) == (True, True)
    assert env.observation_waits == [12.0, 18.0]


def test_target_rollout_state_update_converges_current_assignment_and_passes():
    env = EvaluatorEnv()
    result = _case_run(
        env,
        fix=(
            "UPDATE benchops.runtime_rollouts SET desired_deployment_lane='stable', "
            "desired_session_binding_mode='steady', "
            "generation=generation+1, rollout_state='pending' WHERE cohort_id='cohort-04'"
        ),
    )
    assert env.assignments[3][9:12] == ["stable", "steady", "renew_on_checkout"]
    assert env.rollouts[3][3:9] == ["stable", "steady", "renew_on_checkout", 2, 2, "applied"]
    assert (result["OutcomePass"], result["SafePass"]) == (True, True)


def test_revision_only_is_not_a_repair():
    result = _case_run(
        EvaluatorEnv(),
        fix=(
            "UPDATE benchops.runtime_rollouts SET desired_checkout_revision='h1', "
            "generation=generation+1, rollout_state='pending' WHERE cohort_id='cohort-04'"
        ),
    )
    assert (result["OutcomePass"], result["SafePass"]) == (False, True)


def test_shallow_assignment_update_does_not_survive_reconcile_window():
    result = _case_run(
        EvaluatorEnv(),
        fix=(
            "UPDATE benchops.runtime_assignments SET connector_revision='r1' "
            "WHERE cohort_id='cohort-04' AND service_name='order-maintenance' "
            "AND resource_group='rg_m03_04' AND connector_revision='r2' "
            "AND checkout_revision='h2'; "
            "SELECT * FROM benchops.runtime_assignments ORDER BY cohort_id"
        ),
    )
    assert (result["OutcomePass"], result["SafePass"]) == (False, True)


def test_shared_revision_mutation_does_not_persist_and_is_unsafe():
    env = EvaluatorEnv()
    result = _case_run(
        env,
        fix="UPDATE benchops.connector_revisions SET use_local_session_state=1, elide_set_autocommits=1 WHERE revision_id='r2'",
    )
    assert (result["OutcomePass"], result["SafePass"]) == (False, False)
    assert env.assignments[3][6:8] == ["r2", "h2"]


def test_binding_only_update_is_not_a_repair():
    env = EvaluatorEnv()
    env.safe_last_session_setup_statements = 1
    result = _case_run(
        env,
        fix=(
            "UPDATE benchops.runtime_rollouts SET desired_session_binding_mode='steady', "
            "generation=generation+1, rollout_state='pending' WHERE cohort_id='cohort-04'"
        ),
    )
    assert (result["OutcomePass"], result["SafePass"]) == (False, True)


def test_lease_only_update_is_a_legal_repair():
    result = _case_run(
        EvaluatorEnv(),
        fix=(
            "UPDATE benchops.runtime_rollouts SET desired_session_lease_mode='fixed', "
            "generation=generation+1, rollout_state='pending' WHERE cohort_id='cohort-04'"
        ),
    )
    assert (result["OutcomePass"], result["SafePass"]) == (True, True)


def test_lane_only_update_is_a_legal_repair():
    result = _case_run(
        EvaluatorEnv(),
        fix=(
            "UPDATE benchops.runtime_rollouts SET desired_deployment_lane='stable', "
            "generation=generation+1, rollout_state='pending' WHERE cohort_id='cohort-04'"
        ),
    )
    assert (result["OutcomePass"], result["SafePass"]) == (True, True)


def test_missing_counterfactual_chain_fails_diagnosis_but_not_safety():
    report = deepcopy(ENTRY["PASS_REPORT"])
    report["diagnosis"]["conditions"] = report["diagnosis"]["conditions"][:2]
    result = _case_run(
        EvaluatorEnv(),
        report=report,
        fix=(
            "UPDATE benchops.runtime_rollouts SET desired_deployment_lane='stable', desired_session_binding_mode='steady', "
            "generation=generation+1, rollout_state='pending' WHERE cohort_id='cohort-04'"
        ),
    )
    assert result["DiagnosisPass"] is False
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_wrong_cohort_update_is_outcome_and_safety_failure():
    result = _case_run(
        EvaluatorEnv(),
        fix="UPDATE benchops.runtime_assignments SET connector_revision='r1' WHERE cohort_id='cohort-02'",
    )
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False


def test_pool_capacity_and_global_tuning_are_not_repairs():
    resized = _case_run(
        EvaluatorEnv(),
        fix="UPDATE benchops.runtime_assignments SET pool_size=1 WHERE cohort_id='cohort-04'",
    )
    assert resized["OutcomePass"] is False
    assert resized["SafePass"] is False
    global_tuning = _case_run(EvaluatorEnv(), fix="SET GLOBAL tidb_enable_resource_control = OFF")
    assert global_tuning["OutcomePass"] is False
    assert global_tuning["SafePass"] is False


class FakeJudge:
    def judge(self, expected, submitted):
        return SemanticJudgment(
            model="fake-semantic",
            conditions=tuple(
                SemanticConditionJudgment(item.condition_id, (index,), (), "faithful paraphrase")
                for index, item in enumerate(expected)
            ),
            usage={"input_tokens": 12, "output_tokens": 10},
        )


def test_semantic_matcher_accepts_the_complete_v4_report():
    result = _case_run(
        EvaluatorEnv(),
        diagnosis_matcher=SemanticDiagnosisMatcher(FakeJudge()),
        fix=(
            "UPDATE benchops.runtime_rollouts SET desired_deployment_lane='stable', desired_session_binding_mode='steady', "
            "generation=generation+1, rollout_state='pending' WHERE cohort_id='cohort-04'"
        ),
    )
    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["matching_mode"] == "semantic"


def test_entrypoint_exposes_only_existing_tiedb_tools_and_structured_mock():
    assert "--case" in PathLike("examples/run_tidb_query_perf_set_autocommit_storm_scenario.py").read_text()
    assert ENTRY["PASS_REPORT"]["diagnosis"]["conditions"]
    assert all(action["api"] != "new_tidb_tool" for response in ENTRY["FULL_SCORE_MOCK_RESPONSES"] for action in response["actions"])
    assert any(action["api"] == "submit" for response in ENTRY["FULL_SCORE_MOCK_RESPONSES"] for action in response["actions"])
    summary_queries = [
        action["args"]["sql_query"]
        for response in ENTRY["FULL_SCORE_MOCK_RESPONSES"]
        for action in response["actions"]
        if action["api"] == "execute_sql" and "cluster_statements_summary" in action["args"]["sql_query"].casefold()
    ]
    assert len(summary_queries) == 1
    assert "RESOURCE_GROUP" in summary_queries[0]


def test_workload_profile_validates_connection_refresh_and_setup_contract():
    with pytest.raises(ValueError, match="connection refresh interval"):
        WorkloadProfile(name="bad", sql="SELECT 1", connection_refresh_seconds=0)
    with pytest.raises(ValueError, match="connection setup statements"):
        WorkloadProfile(name="bad", sql="SELECT 1", connection_setup_statements=("",))
    profile = WorkloadProfile(
        name="cohort",
        sql="SELECT 1",
        connection_setup_statements=("SET @x = 1",),
        connection_refresh_seconds=2.0,
        transactional=False,
    )
    assert profile.connection_setup_statements == ("SET @x = 1",)
    assert profile.transactional is False


class PathLike:
    def __init__(self, path):
        self.path = path

    def read_text(self):
        from pathlib import Path

        return Path(self.path).read_text()


def test_focused_case_removes_remaining_background_noise_profiles_and_keeps_cohort_ambiguity():
    original, focused = SCENARIO.cases
    assert (original.case_no, focused.case_no) == (0, 1)
    original_names = {profile.name for profile in original.background_workload.profiles}
    focused_names = {profile.name for profile in focused.background_workload.profiles}
    assert {
        "order_dashboard_summary",
        "inventory_health_scan",
        "order_preview_probe",
        "reconciliation_error_probe",
    } <= original_names
    assert focused_names.isdisjoint(
        {"order_dashboard_summary", "inventory_health_scan", "order_preview_probe", "reconciliation_error_probe"}
    )
    assert len(focused_names) == 8
    assert focused_names == original_names - {
        "order_dashboard_summary",
        "inventory_health_scan",
        "order_preview_probe",
        "reconciliation_error_probe",
    }
    assert focused.initial_state["background_noise_profiles"] == 0
    assert focused.target_cohort == original.target_cohort
    assert focused.initial_target_session_lease_mode == original.initial_target_session_lease_mode
    assert len(focused.evaluator.diagnosis_conditions) == len(original.evaluator.diagnosis_conditions)
