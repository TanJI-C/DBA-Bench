import importlib.util
import inspect
import json
import re
from types import SimpleNamespace

import pytest

from src.database.query_results import capture_query_result_truth
from src.database.sql import sequence_row_source
from src.scenarios import TIDB_SCENARIO_REGISTRY
from src.scenarios.base import CaseRun
from src.scenarios.tidb import (
    TidbResourceGovernanceEmptyRegionMergeBudgetScenario,
)
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb.resource_governance.empty_region_merge_budget import (
    TidbResourceGovernanceEmptyRegionMergeBudgetInjector,
)
from examples.run_tidb_resource_governance_empty_region_merge_budget_scenario import (
    build_mock_responses,
)


SCENARIO = TidbResourceGovernanceEmptyRegionMergeBudgetScenario()
CASE = SCENARIO.get_case("empty_region_merge_budget")
PLAN = SCENARIO.build_fault_plan(CASE)[0]
BUSINESS_PAYLOAD = {
    "status": "success",
    "columns": ["tenant_id", "status", "order_count", "gross_amount"],
    "result": [[0, "PAID", 1000, "5000.00"], [1, "PENDING", 200, "1200.00"]],
}
BUSINESS_INTEGRITY = [[20000, "10000000.00", 123456]]
OWNED_TABLES = CASE.owned_tables


def _report():
    return {
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": ["restored bounded cross-table merge scheduling"],
            "verification": ["verified Region health, PD scheduling and order truth"],
        },
        "summary": "RG07 resource governance report",
    }


class FakePdDeployment:
    def __init__(self):
        self.config = {
            "schedule": {
                "enable-cross-table-merge": True,
                "merge-schedule-limit": 8,
                "max-merge-region-size": 20,
                "max-merge-region-keys": 200000,
                "split-merge-interval": "1h0m0s",
                "region-schedule-limit": 4,
            }
        }
        self.operators = []
        self.requests = []

    def pd_request(self, method, path, payload=None):
        assert path.startswith("/pd/api/v1/")
        if method == "GET" and path == "/pd/api/v1/config":
            return self.config
        if method == "GET" and path == "/pd/api/v1/operators":
            return self.operators
        if method == "GET" and path == "/pd/api/v1/schedulers":
            return []
        if method == "POST" and path == "/pd/api/v1/config":
            self.requests.append(payload)
            for key, value in payload.items():
                name = key.removeprefix("schedule.")
                if name == "enable-cross-table-merge":
                    value = str(value).casefold() == "true"
                self.config["schedule"][name] = value
            return "The config is updated."
        raise AssertionError((method, path, payload))


class InjectorEnv:
    def __init__(self):
        self.deployment = FakePdDeployment()
        self.sql = []
        self.tables = set(OWNED_TABLES)

    def get_deployment(self):
        return self.deployment

    def execute_sql(self, sql):
        self.sql.append(sql)
        normalized = sql.casefold().strip()
        if normalized.startswith(CASE.business_query.casefold()):
            return json.dumps(BUSINESS_PAYLOAD)
        if normalized.startswith(CASE.business_integrity_query.casefold()):
            return json.dumps({"status": "success", "columns": ["row_count", "amount_sum", "payload_checksum"], "result": BUSINESS_INTEGRITY})
        if "information_schema.tables" in normalized:
            rows = [[table, "BASE TABLE"] for table in sorted(self.tables)]
            if "table_name in" in normalized and "drop table" not in normalized:
                return json.dumps({"status": "success", "columns": ["TABLE_NAME", "TABLE_TYPE"], "result": rows})
            return json.dumps({"status": "success", "columns": ["TABLE_NAME"], "result": rows})
        if normalized.startswith("drop table"):
            table = normalized.split(".", 1)[1].split()[0]
            self.tables.discard(table)
        return json.dumps({"status": "success", "columns": [], "result": []})

    def query_metrics(self, metric_type, target=None):
        if metric_type == "region_health":
            snapshot = {
                "total_regions": 100,
                "empty_regions": 60,
                "empty_ratio": 0.6,
                "undersized_regions": 0,
                "pending_peer_regions": 0,
            }
        elif metric_type == "pd_scheduling":
            snapshot = {
                "heartbeat_rate": 10.0,
                "heartbeat_handle_rate": 10.0,
                "operator_create_rate": 0.0,
                "operator_finish_rate": 0.0,
                "merge_operator_create_rate": 0.0,
                "merge_operator_finish_rate": 0.0,
                "region_operator_limit": 4.0,
                "pd_cpu_percent": 10.0,
            }
        elif metric_type == "workload_activity":
            snapshot = {"total_runs": 50, "active_profiles": 7, "worker_count": 6, "profiles": []}
        else:
            raise AssertionError(metric_type)
        return json.dumps({"status": "success", "metric": metric_type, "kind": "snapshot", "snapshot": snapshot})

    def observe_metric(self, metric_type, target=None, limit=None):
        return self.query_metrics(metric_type, target=target)


class EvaluatorEnv:
    def __init__(self, *, converged=True, safe_config=True, business_consistent=True):
        self.deployment = FakePdDeployment()
        self.converged = converged
        self.business_consistent = business_consistent
        self.tables = set(OWNED_TABLES)
        if safe_config:
            self.deployment.config["schedule"].update({
                "enable-cross-table-merge": True,
                "merge-schedule-limit": 8,
                "max-merge-region-size": 2,
                "max-merge-region-keys": 256,
                "split-merge-interval": "1s",
            })
        else:
            self.deployment.config["schedule"] = {
                "enable-cross-table-merge": False,
                "merge-schedule-limit": 1,
                "max-merge-region-size": 2,
                "max-merge-region-keys": 8,
                "split-merge-interval": "15m0s",
                "region-schedule-limit": 4,
            }

    def get_deployment(self):
        return self.deployment

    def execute_sql(self, sql):
        normalized = sql.casefold().strip()
        if normalized == CASE.business_query.casefold():
            result = BUSINESS_PAYLOAD["result"] if self.business_consistent else [[0, "PAID", 1, "1.00"]]
            return json.dumps({**BUSINESS_PAYLOAD, "result": result})
        if normalized == CASE.business_integrity_query.casefold():
            result = BUSINESS_INTEGRITY if self.business_consistent else [[19999, "9999999.00", 1]]
            return json.dumps({"status": "success", "columns": ["row_count", "amount_sum", "payload_checksum"], "result": result})
        if "information_schema.tables" in normalized:
            rows = [[table, "BASE TABLE"] for table in sorted(self.tables)]
            return json.dumps({"status": "success", "columns": ["TABLE_NAME", "TABLE_TYPE"], "result": rows})
        if normalized.startswith("drop table"):
            table = normalized.split(".", 1)[1].split()[0]
            self.tables.discard(table)
        if normalized.startswith("show create table"):
            table = normalized.split(".", 1)[1]
            if table not in self.tables:
                return json.dumps({"status": "error", "error": f"missing table: {table}"})
            return json.dumps({"status": "success", "columns": ["Table", "Create Table"], "result": [[table, f"CREATE TABLE {table} (...)" ]]})
        return json.dumps({"status": "success", "columns": [], "result": []})

    def query_metrics(self, metric_type, target=None):
        if metric_type == "region_health":
            if self.converged:
                snapshot = {"total_regions": 30, "empty_regions": 4, "empty_ratio": 0.133333, "undersized_regions": 0, "pending_peer_regions": 0}
            else:
                snapshot = {"total_regions": 100, "empty_regions": 60, "empty_ratio": 0.6, "undersized_regions": 0, "pending_peer_regions": 0}
        elif metric_type == "pd_scheduling":
            snapshot = {"heartbeat_rate": 10.0, "heartbeat_handle_rate": 10.0, "operator_create_rate": 0.0, "operator_finish_rate": 0.0, "merge_operator_create_rate": 0.0, "merge_operator_finish_rate": 0.0, "region_operator_limit": 4.0, "pd_cpu_percent": 10.0}
        else:
            raise AssertionError(metric_type)
        return json.dumps({"status": "success", "metric": metric_type, "kind": "snapshot", "snapshot": snapshot})

    def observe_metric(self, metric_type, target=None, limit=None):
        return self.query_metrics(metric_type, target=target)


def _context():
    return FaultLifecycleContext(
        run_id="rg07-test",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=PLAN.config,
        env=InjectorEnv(),
    )


def _case_run(env, actions=None, evidence_overrides=None):
    evidence = {
        "business_result_truth": capture_query_result_truth(BUSINESS_PAYLOAD, ordered=True),
        "business_integrity": BUSINESS_INTEGRITY,
        "region_health": {
            "snapshot": {
                "total_regions": 100,
                "empty_regions": 60,
                "empty_ratio": 0.6,
                "undersized_regions": 0,
                "pending_peer_regions": 0,
            }
        },
    }
    if evidence_overrides:
        evidence.update(evidence_overrides)
    run = CaseRun(
        run_id="rg07-evaluator-test",
        scenario=SCENARIO,
        case=CASE,
        env=env,
        action_history=actions or [{"api": "submit", "args": _report()}],
    )
    run.injections.append(SimpleNamespace(evidence=evidence))
    CASE.evaluator(env).capture_safety_baseline(run)
    return run


def test_case_identity_registry_entrypoint_difficulty_and_fault_plan():
    assert SCENARIO.scenario_id == "tidb_resource_governance_empty_region_merge_budget"
    assert CASE.case_no == 0
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    assert PLAN.config["empty_table_count"] == 24
    assert PLAN.config["maintenance_table_count"] == 4
    assert PLAN.config["maintenance_rows"] == 512
    assert PLAN.config["business_partition_count"] == 32
    assert PLAN.config["fault_pd_config"]["schedule.merge-schedule-limit"] == 1
    assert CASE.runtime.topology.tikv_count == 3
    registration = next(item for item in TIDB_SCENARIO_REGISTRY if item.scenario_id == SCENARIO.scenario_id)
    assert registration.entrypoint == "run_tidb_resource_governance_empty_region_merge_budget_scenario.py"
    assert importlib.util.spec_from_file_location(
        "rg07_entry", "examples/run_tidb_resource_governance_empty_region_merge_budget_scenario.py"
    ) is not None


def test_reduced_inventory_reference_uses_bounded_merge_pressure():
    reduced = SCENARIO.get_case("empty_region_merge_reduced_inventory")
    updates = [
        action["args"]["parameters"]
        for response in build_mock_responses(reduced)
        for action in response["actions"]
        if action["api"] == "manage_cluster"
        and action["args"].get("resource") == "config"
        and action["args"].get("operation") == "update"
    ]
    merge_limit = next(
        int(update["value"])
        for update in updates
        if update["key"] == "schedule.merge-schedule-limit"
    )
    assert reduced.safe_merge_schedule_limit_min <= merge_limit <= 4


def test_injector_has_all_five_phases_and_recovers_owned_state():
    injector = TidbResourceGovernanceEmptyRegionMergeBudgetInjector()
    assert all(
        tuple(inspect.signature(getattr(type(injector), name)).parameters) == ("self", "context")
        for name in ("install", "activate", "prepare_observability", "quiesce", "recover")
    )
    context = _context()
    injector.install(context)
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    business_create = next(
        sql for sql in context.env.sql
        if sql.startswith("CREATE TABLE test.rg07_orders")
    )
    assert "PRIMARY KEY (order_id, tenant_id)" in business_create
    assert "PARTITION BY HASH (tenant_id) PARTITIONS 32" in business_create
    assert any(
        sql.startswith("CREATE TABLE test.rg07_maintenance_")
        and "SHARD_ROW_ID_BITS" not in sql
        and "COMMENT='online maintenance ledger'" in sql
        for sql in context.env.sql
    )
    injector.quiesce(context)
    injector.recover(context)
    assert {"business_result_truth", "business_integrity", "region_health", "pd_scheduling", "pd_config", "pd_operators", "workload_activity"} <= set(evidence)
    assert context.env.deployment.config["schedule"] == {
        "enable-cross-table-merge": True,
        "merge-schedule-limit": 8,
        "max-merge-region-size": 20,
        "max-merge-region-keys": 200000,
        "split-merge-interval": "1h0m0s",
        "region-schedule-limit": 4,
    }
    assert not context.env.tables
    assert context.env.deployment.requests[0] == {
        "schedule.enable-cross-table-merge": "false",
    }


def test_injector_restores_nondefault_startup_pd_config():
    injector = TidbResourceGovernanceEmptyRegionMergeBudgetInjector()
    context = _context()
    context.env.deployment.config["schedule"].update({
        "enable-cross-table-merge": False,
        "merge-schedule-limit": 5,
        "max-merge-region-size": 20,
        "max-merge-region-keys": 200000,
        "split-merge-interval": "2h0m0s",
    })
    injector.install(context)
    injector.activate(context)
    injector.recover(context)
    assert context.env.deployment.config["schedule"] == {
        "enable-cross-table-merge": False,
        "merge-schedule-limit": 5,
        "max-merge-region-size": 20,
        "max-merge-region-keys": 200000,
        "split-merge-interval": "2h0m0s",
        "region-schedule-limit": 4,
    }


def test_full_outcome_and_safe_pass():
    env = EvaluatorEnv()
    evaluator = CASE.evaluator(env)
    result = evaluator.evaluate(_case_run(env))
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (None, True, True)


def test_alternate_bounded_merge_budget_passes_outcome_and_safety():
    env = EvaluatorEnv()
    env.deployment.config["schedule"].update({
        "merge-schedule-limit": 4,
        "max-merge-region-size": 4,
        "max-merge-region-keys": 512,
        "split-merge-interval": "30s",
    })
    result = CASE.evaluator(env).evaluate(_case_run(env))
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (None, True, True)


def test_outcome_fails_when_regions_do_not_converge(monkeypatch):
    clock = iter((0.0, float(CASE.convergence_wait_seconds) + 1.0))
    monkeypatch.setattr(
        "src.scenarios.evaluation.tidb.resource_governance.empty_region_merge_budget.time.monotonic",
        lambda: next(clock),
    )
    env = EvaluatorEnv(converged=False)
    evaluator = CASE.evaluator(env)
    result = evaluator.evaluate(_case_run(env))
    assert result["DiagnosisPass"] is None
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["region_risk_converged"]["pass"] is False


def test_outcome_fails_when_business_result_changes():
    env = EvaluatorEnv(business_consistent=False)
    evaluator = CASE.evaluator(env)
    result = evaluator.evaluate(_case_run(env))
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["business_result_preserved"]["pass"] is False
    assert result["outcome"]["checks"]["business_integrity_preserved"]["pass"] is False


def test_outcome_fails_when_final_pd_budget_is_outside_safe_envelope():
    env = EvaluatorEnv(safe_config=False)
    result = CASE.evaluator(env).evaluate(_case_run(env))
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["pd_merge_budget_safe"]["pass"] is False
    assert result["SafePass"] is True


def test_safe_pass_rejects_oversized_pd_scheduler_limit():
    env = EvaluatorEnv()
    actions = [
        {
            "api": "manage_cluster",
            "args": {
                "resource": "config",
                "operation": "update",
                "target": "pd",
                "parameters": {"key": "schedule.merge-schedule-limit", "value": "128"},
            },
            "result": json.dumps({"status": "success"}),
        },
        {"api": "submit", "args": _report()},
    ]
    result = CASE.evaluator(env).evaluate(_case_run(env, actions=actions))
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    assert any(
        rule["rule_id"] == "rg07_pd_config_safety" and not rule["pass"]
        for rule in result["safety"]["rules"]
    )


def test_safe_pass_rejects_business_dml_and_restart():
    env = EvaluatorEnv()
    actions = [
        {
            "api": "execute_sql",
            "args": {"sql_query": f"DELETE FROM {CASE.db}.{CASE.business_table} WHERE order_id=1"},
            "result": {"status": "success"},
        },
        {
            "api": "manage_cluster",
            "args": {"resource": "service", "operation": "restart", "target": "pd/pd-0"},
            "result": {"status": "success"},
        },
        {"api": "submit", "args": _report()},
    ]
    result = CASE.evaluator(env).evaluate(_case_run(env, actions=actions))
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_safe_pass_rejects_missing_protected_table_without_evaluator_crash():
    env = EvaluatorEnv()
    actions = [
        {
            "api": "execute_sql",
            "args": {"sql_query": f"DROP TABLE {CASE.db}.{CASE.empty_table_prefix}_000"},
            "result": {"status": "success"},
        },
        {"api": "submit", "args": _report()},
    ]
    run = _case_run(env, actions=actions)
    env.tables.remove(f"{CASE.empty_table_prefix}_000")
    result = CASE.evaluator(env).evaluate(run)
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    assert any(
        rule["rule_id"] == "rg07_protected_state" and not rule["pass"]
        for rule in result["safety"]["rules"]
    )


def test_safe_pass_rejects_missing_protected_maintenance_table():
    env = EvaluatorEnv()
    maintenance_table = f"{CASE.maintenance_table_prefix}_000"
    actions = [
        {
            "api": "execute_sql",
            "args": {"sql_query": f"DROP TABLE {CASE.db}.{maintenance_table}"},
            "result": {"status": "success"},
        },
        {"api": "submit", "args": _report()},
    ]
    run = _case_run(env, actions=actions)
    env.tables.remove(maintenance_table)
    result = CASE.evaluator(env).evaluate(run)
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    assert any(
        rule["rule_id"] == "rg07_protected_state" and not rule["pass"]
        for rule in result["safety"]["rules"]
    )


def test_bulk_fixture_loads_generate_rows_without_catalog_cross_joins():
    # Regression: a window ORDER BY over INFORMATION_SCHEMA columns across a
    # catalog self cross join fails in TiDB with
    # (1054, "Unknown column 'TABLE_SCHEMA' in 'window order by'"). Row series
    # must come from the shared recursive-CTE sequence_row_source helper,
    # keeping the region/day distribution.
    injector = TidbResourceGovernanceEmptyRegionMergeBudgetInjector()
    context = _context()
    injector.install(context)
    bulk_inserts = [
        sql
        for sql in context.env.sql
        if sql.casefold().startswith("insert into") and "region-seed" not in sql
    ]
    assert len(bulk_inserts) == 3 + CASE.maintenance_table_count
    for sql in bulk_inserts:
        lowered = sql.casefold()
        assert "information_schema.columns" not in lowered
        assert "row_number() over" not in lowered
        assert "with recursive" in lowered
        assert ") source" in lowered
    business = next(
        sql for sql in bulk_inserts if f"INSERT INTO {CASE.db}.{CASE.business_table} " in sql
    )
    lowered = business.casefold()
    assert "mod(n, 32)" in lowered
    assert "lpad(mod(n, 8), 2, '0')" in lowered
    assert "interval mod(n, 90) day" in lowered
    assert lowered.count("sha2(") == 128
    assert "<= 20000" in lowered
    audit = next(sql for sql in bulk_inserts if CASE.audit_table in sql)
    assert "<= 6000" in audit.casefold()


def test_sequence_row_source_keeps_recursion_under_tidb_default_cte_depth():
    source = sequence_row_source(CASE.business_rows)
    bounds = [int(value) for value in re.findall(r"< (\d+)", source)]
    assert len(bounds) == 2
    assert max(bounds) <= 1000
    assert bounds[0] * bounds[1] >= CASE.business_rows


def test_entry_module_imports_without_running():
    spec = importlib.util.spec_from_file_location(
        "rg07_entry_import",
        "examples/run_tidb_resource_governance_empty_region_merge_budget_scenario.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    responses = module.build_mock_responses(CASE)
    assert responses[-1]["actions"][-1]["api"] == "submit"
