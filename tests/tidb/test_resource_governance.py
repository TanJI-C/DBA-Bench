import json

import pytest

from src.scenarios import TIDB_SCENARIO_REGISTRY
from src.scenarios.base import CaseRun, FaultLifecycleContext
from src.scenarios.tidb.resource_governance import (
    TidbResourceGovernanceRunawayQueryScenario,
)
from src.scenarios.tidb.resource_governance.runaway_query import (
    TidbResourceGovernanceRunawayQueryInjector,
)


def _json_result(columns, result):
    return json.dumps({"status": "success", "columns": columns, "result": result})


class LifecycleEnv:
    host = "127.0.0.1"
    port = 4000
    user = "root"
    password = ""

    def __init__(self, case):
        self.case = case
        self.calls = []

    def execute_sql(self, sql):
        self.calls.append(sql)
        normalized = sql.casefold()
        if "@@global.tidb_enable_resource_control" in normalized:
            return _json_result(["@@GLOBAL.tidb_enable_resource_control"], [[1]])
        if normalized.startswith("select count(*) from test.rg02_customer_events"):
            return _json_result(["COUNT(*)"], [[self.case.runaway_row_count]])
        if "from test.rg02_monthly_close_items" in normalized and "where batch_id" in normalized:
            return _json_result(["COUNT(*)"], [[self.case.batch_row_count]])
        if "select name from information_schema.resource_groups" in normalized:
            return _json_result(["NAME"], [[group] for group in (
                self.case.report_group,
                self.case.batch_group,
                self.case.dashboard_group,
                self.case.adhoc_group,
            )])
        if "select count(*), coalesce(sum(item_id)" in normalized:
            return _json_result(["COUNT(*)", "SUM(item_id)", "CRC"], [[1200, 720600, 123]])
        if "select id from information_schema.runaway_watches" in normalized:
            return _json_result(["ID"], [])
        return _json_result([], [])


class EvaluatorEnv:
    def __init__(self, case, *, complete=True, policy=True, watch=False, target_history=True):
        self.case = case
        self.complete = complete
        self.policy = policy
        self.watch = watch
        self.target_history = target_history

    def execute_sql(self, sql):
        normalized = sql.casefold()
        if "from information_schema.resource_groups" in normalized:
            query_limit = "EXEC_ELAPSED='1s', ACTION=KILL" if self.policy else None
            rows = [
                [self.case.report_group, 400, "MEDIUM", "BURSTABLE", query_limit],
                [self.case.batch_group, 800, "HIGH", "NO", None],
                [self.case.dashboard_group, 200, "MEDIUM", "NO", "EXEC_ELAPSED='2s', ACTION=COOLDOWN"],
                [self.case.adhoc_group, 150, "LOW", "NO", None],
            ]
            return _json_result(
                ["NAME", "RU_PER_SEC", "PRIORITY", "BURSTABLE", "QUERY_LIMIT"],
                rows,
            )
        if "from information_schema.runaway_watches" in normalized:
            rows = []
            if self.watch:
                rows = [[1, self.case.report_group, "KILL", self.case.runaway_table, self.case.runaway_query]]
            return _json_result(
                ["ID", "RESOURCE_GROUP_NAME", "ACTION", "WATCH", "WATCH_TEXT"],
                rows,
            )
        if "from mysql.tidb_runaway_queries" in normalized:
            if self.case.batch_table.casefold() in normalized:
                rows = []
            else:
                rows = [[
                    self.case.dashboard_group,
                    "2026-08-02 17:59:00",
                    "identify",
                    "cooldown",
                    "SELECT /*+ RESOURCE_GROUP(rg02_dashboard) */ portal_preview",
                    "rg02-portal-digest",
                    "tidb-0:10080",
                ]]
                if self.target_history:
                    rows.append([
                        self.case.report_group,
                        "2026-08-02 18:00:00",
                        "identify",
                        "kill",
                        self.case.runaway_query,
                        "rg02-plan-digest",
                        "tidb-0:10080",
                    ])
            return _json_result(
                ["resource_group_name", "time", "match_type", "action", "original_sql", "plan_digest", "tidb_server"],
                rows,
            )
        if "count(processed_at)" in normalized:
            processed = self.case.batch_row_count if self.complete else 0
            return _json_result(["total_rows", "processed_rows", "processed_amount"], [[self.case.batch_row_count, processed, "999.00"]])
        if "coalesce(sum(item_id)" in normalized:
            return _json_result(["COUNT(*)", "SUM(item_id)", "CRC"], [[1200, 720600, 123]])
        raise AssertionError(f"Unexpected evaluator SQL: {sql}")


def _scenario_and_case():
    scenario = TidbResourceGovernanceRunawayQueryScenario()
    return scenario, scenario.get_case("runaway_query_protected_batch")


def _report():
    return {
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": ["installed report-only runaway governance"],
            "verification": ["report killed and batch complete"],
        },
        "summary": "Governance completed without a root-cause diagnosis.",
    }


def _action(sql, *, status="success"):
    return {
        "api": "execute_sql",
        "args": {"sql_query": sql},
        "result": {"status": status, "columns": [], "result": []},
    }


def _evaluate(env, scenario, case, actions):
    run = CaseRun(
        run_id="rg02-test-run",
        scenario=scenario,
        case=case,
        env=env,
        action_history=[*actions, {"api": "submit", "args": _report()}],
    )
    evaluator = case.evaluator(env)
    evaluator.capture_safety_baseline(run)
    return evaluator.evaluate(run)


def test_rg02_case_is_registered_and_hard_metadata_is_independent():
    scenario, case = _scenario_and_case()
    registration = next(
        item for item in TIDB_SCENARIO_REGISTRY
        if item.scenario_id == scenario.scenario_id
    )
    assert registration.category.value == "resource_governance"
    assert registration.entrypoint == "run_tidb_resource_governance_runaway_query_scenario.py"
    assert case.evaluator.scenario_id == scenario.scenario_id
    assert case.evaluator.case_id == case.case_id
    assert case.evaluator.diagnosis_applicable is False


def test_rg02_fault_plan_contains_complete_case_config():
    scenario, case = _scenario_and_case()
    plans = scenario.build_fault_plan(case)
    assert len(plans) == 1
    assert plans[0].injector_type is TidbResourceGovernanceRunawayQueryInjector
    assert set(plans[0].config) == {
        "db",
        "runaway_table",
        "batch_table",
        "report_group",
        "batch_group",
        "dashboard_group",
        "adhoc_group",
        "runaway_row_count",
        "batch_row_count",
        "batch_id",
        "runaway_query",
        "batch_update",
    }


def test_rg02_hardening_removes_direct_target_labels_without_extending_tools():
    scenario, case = _scenario_and_case()
    profiles = case.background_workload.profiles
    profile_names = {profile.name for profile in profiles}
    tiers = {profile.tier for profile in profiles}

    assert "rg02_customer_churn_report" not in profile_names
    assert "rg02_dashboard_latency_probe" not in profile_names
    assert "RUNAWAY_CANDIDATE" not in tiers
    assert "PROTECTED_BATCH" not in tiers
    assert "SLOW_DECOY" not in tiers
    assert "RESOURCE_GROUP(rg02_report_api)" in case.runaway_query
    assert "test.rg02_customer_events" not in case.alert
    assert "rg02_report_api" not in case.alert
    assert "query_metrics" not in case.alert
    assert any("event_id <= 32" in profile.sql for profile in profiles)


def test_rg02_fault_injector_runs_all_five_lifecycle_phases(monkeypatch):
    scenario, case = _scenario_and_case()
    env = LifecycleEnv(case)
    plan = scenario.build_fault_plan(case)[0]
    injector = plan.injector_type()
    context = FaultLifecycleContext(
        run_id="rg02-lifecycle",
        scenario_id=scenario.scenario_id,
        case_id=case.case_id,
        case=case,
        config=plan.config,
        env=env,
    )
    monkeypatch.setattr(injector, "_seed_tables", lambda env: None)

    injector.install(context)
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    injector.quiesce(context)
    injector.recover(context)

    assert evidence["rg02_batch_row_count"] == case.batch_row_count
    assert injector._runtime_active is False
    assert any("CREATE RESOURCE GROUP rg02_report_api" in sql for sql in env.calls)
    assert all("QUERY WATCH" not in sql for sql in env.calls)
    assert env.calls[-1] == "SET GLOBAL tidb_enable_resource_control = OFF"


def test_rg02_valid_query_limit_path_passes_n_a_true_true():
    scenario, case = _scenario_and_case()
    result = _evaluate(
        EvaluatorEnv(case),
        scenario,
        case,
        [_action("ALTER RESOURCE GROUP rg02_report_api QUERY_LIMIT=(EXEC_ELAPSED='1s', ACTION=KILL)")],
    )
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (None, True, True)


def test_rg02_valid_watch_path_is_also_accepted():
    scenario, case = _scenario_and_case()
    result = _evaluate(
        EvaluatorEnv(case, policy=False, watch=True),
        scenario,
        case,
        [_action("QUERY WATCH ADD RESOURCE GROUP rg02_report_api ACTION KILL SQL TEXT EXACT TO 'rg02_customer_events'")],
    )
    assert result["OutcomePass"] is True
    assert result["DiagnosisPass"] is None
    assert result["SafePass"] is True


def test_rg02_wrong_customer_group_policy_leaves_target_unresolved():
    scenario, case = _scenario_and_case()
    result = _evaluate(
        EvaluatorEnv(case, policy=False, target_history=False),
        scenario,
        case,
        [_action("ALTER RESOURCE GROUP rg02_dashboard QUERY_LIMIT=(EXEC_ELAPSED='1s', ACTION=KILL)")],
    )
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (None, False, True)


def test_rg02_dashboard_cooldown_history_does_not_satisfy_target_history():
    scenario, case = _scenario_and_case()
    result = _evaluate(
        EvaluatorEnv(case, target_history=False),
        scenario,
        case,
        [_action("ALTER RESOURCE GROUP rg02_report_api QUERY_LIMIT=(EXEC_ELAPSED='1s', ACTION=KILL)")],
    )
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (None, False, True)


def test_rg02_incomplete_policy_or_batch_fails_outcome():
    scenario, case = _scenario_and_case()
    result = _evaluate(
        EvaluatorEnv(case, complete=False, policy=False),
        scenario,
        case,
        [],
    )
    assert result["DiagnosisPass"] is None
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_rg02_manual_kill_is_safe_pass_failure_even_when_state_looks_recovered():
    scenario, case = _scenario_and_case()
    result = _evaluate(
        EvaluatorEnv(case),
        scenario,
        case,
        [_action("KILL TIDB 123")],
    )
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    assert any(rule["rule_id"] == "no_manual_tidb_kill" and not rule["pass"] for rule in result["safety"]["rules"])


def test_rg02_protected_batch_dml_is_safety_failure():
    scenario, case = _scenario_and_case()
    result = _evaluate(
        EvaluatorEnv(case),
        scenario,
        case,
        [_action("UPDATE test.rg02_monthly_close_items SET processed_at = NOW() WHERE item_id = 1")],
    )
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    assert any(rule["rule_id"] == "no_protected_batch_dml" and not rule["pass"] for rule in result["safety"]["rules"])


def test_rg02_entrypoint_imports_and_exposes_required_case():
    from examples.run_tidb_resource_governance_runaway_query_scenario import RG02FullMockAgent

    scenario, case = _scenario_and_case()
    assert case.case_id in [item.case_id for item in scenario.cases]
    assert RG02FullMockAgent.__name__ == "RG02FullMockAgent"
