import inspect
import json
from types import SimpleNamespace

import pytest

from src.database.query_results import capture_query_result_truth
from src.scenarios.base import CaseRun
from src.scenarios.tidb import TidbResourceGovernanceRg06Scenario
from src.execution.tidb_runtime import TIDB_V8_1_0
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb.resource_governance.rg06_ticdc_checkpoint_lag import (
    TidbResourceGovernanceRg06Injector,
)


SCENARIO = TidbResourceGovernanceRg06Scenario()
CASE = SCENARIO.get_case("ticdc_checkpoint_sink_budget")
PLAN = SCENARIO.build_fault_plan(CASE)[0]

REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": ["bounded sink and sorter budget"],
        "verification": ["verified final replication and SLO invariants"],
    },
    "summary": "The resource budget was adjusted within the case envelope.",
}

BUSINESS_PAYLOAD = {
    "status": "success",
    "columns": ["event_id", "tenant_id", "event_type", "amount", "payload"],
    "result": [[1, 7, "captured", "10.00", "order-1"]],
    "row_count": 1,
}


def _metric_rows(*, converged=True):
    if converged:
        values = {
            "checkpoint_lag_rows": 0,
            "checkpoint_event_id": 1800,
            "resolved_event_id": 1800,
            "sink_write_rows_per_second": 60,
            "gc_headroom_seconds": 1160,
            "downstream_write_p95_ms": 28,
            "foreground_p95_ms": 32,
            "error_count": 0,
            "overload_events": 0,
        }
    else:
        values = {
            "checkpoint_lag_rows": 380,
            "checkpoint_event_id": 1420,
            "resolved_event_id": 1800,
            "sink_write_rows_per_second": 1,
            "gc_headroom_seconds": 420,
            "downstream_write_p95_ms": 31,
            "foreground_p95_ms": 34,
            "error_count": 0,
            "overload_events": 0,
        }
    rows = []
    for name, value in values.items():
        rows.append([name, str(value), None, "test", "unit", "2026-08-02 00:00:10"])
    rows.append(["changefeed_state", None, "NORMAL", "changefeed", "state", "2026-08-02 00:00:10"])
    return rows


class EvaluatorEnv:
    def __init__(self, *, converged=True, unsafe_budget=False, changed_source=False):
        self.converged = converged
        self.unsafe_budget = unsafe_budget
        self.changed_source = changed_source
        self.sql = []
        self.config = {
            "changefeed_id": "archive-orders",
            "state": "NORMAL",
            "capture_workers": 4,
            "sorter_memory_mb": 256 if not unsafe_budget else 1024,
            "sink_workers": 8 if not unsafe_budget else 32,
            "sink_batch_rows": 100 if not unsafe_budget else 512,
            "sink_write_budget": 0.75 if not unsafe_budget else 2.0,
            "gc_ttl_seconds": 1200,
            "overload_events": 0 if not unsafe_budget else 1,
            "error_count": 0 if not unsafe_budget else 1,
            "last_checkpoint_id": 1800 if converged else 1420,
            "last_resolved_id": 1800,
        }

    def execute_sql(self, sql):
        self.sql.append(sql)
        normalized = sql.casefold()
        if "rg06_cdc_config" in normalized and normalized.startswith("select"):
            row = [
                self.config["changefeed_id"],
                self.config["state"],
                self.config["capture_workers"],
                self.config["sorter_memory_mb"],
                self.config["sink_workers"],
                self.config["sink_batch_rows"],
                str(self.config["sink_write_budget"]),
                self.config["gc_ttl_seconds"],
                self.config["overload_events"],
                self.config["error_count"],
                self.config["last_checkpoint_id"],
                self.config["last_resolved_id"],
            ]
            return self._success([row])
        if "rg06_cdc_metrics" in normalized:
            rows = _metric_rows(converged=self.converged)
            if self.unsafe_budget:
                for row in rows:
                    if row[0] == "error_count":
                        row[1] = "1"
                    if row[0] == "overload_events":
                        row[1] = "1"
                    if row[0] == "downstream_write_p95_ms":
                        row[1] = "90"
                    if row[0] == "foreground_p95_ms":
                        row[1] = "120"
            return self._success(rows)
        if "left join benchops.rg06_cdc_sink" in normalized:
            return self._success([[0 if self.converged else 380]])
        if "rg06_cdc_source" in normalized and "bit_xor" in normalized:
            return self._success([[1800, 1620900, 123456789 if not self.changed_source else 9]])
        if "rg06_cdc_sink" in normalized and "bit_xor" in normalized:
            return self._success([[1800, 1620900, 123456789]])
        if "rg06_reconcile_source" in normalized and "bit_xor" in normalized:
            return self._success([[900, 404550, 246813579]])
        if "rg06_reconcile_sink" in normalized and "bit_xor" in normalized:
            return self._success([[840, 378420, 246813579]])
        if "rg06_archive_audit" in normalized and "bit_xor" in normalized:
            return self._success([[96, 4656, 987654321]])
        if "rg06_cdc_source" in normalized and "select event_id" in normalized:
            return self._success(BUSINESS_PAYLOAD["result"], BUSINESS_PAYLOAD["columns"])
        if "rg06_cdc_sink" in normalized and "select event_id" in normalized:
            return self._success(BUSINESS_PAYLOAD["result"], BUSINESS_PAYLOAD["columns"])
        return self._success([])

    @staticmethod
    def _success(rows, columns=None):
        return json.dumps({
            "status": "success",
            "columns": columns or ["value"],
            "result": rows,
            "row_count": len(rows),
        })


class InjectorEnv:
    def __init__(self):
        self.sql = []

    def execute_sql(self, sql):
        self.sql.append(sql)
        normalized = sql.casefold()
        if "rg06_cdc_config" in normalized and normalized.startswith("select"):
            return EvaluatorEnv._success([[
                "archive-orders", "NORMAL", 4, 64, 1, 8, "0.050", 1200, 0, 0, 420, 1800
            ]])
        if "rg06_cdc_source" in normalized and "select event_id" in normalized:
            return EvaluatorEnv().execute_sql(sql)
        if "rg06_cdc_source" in normalized and "bit_xor" in normalized:
            return EvaluatorEnv().execute_sql(sql)
        if "rg06_cdc_sink" in normalized and "bit_xor" in normalized:
            return EvaluatorEnv._success([[420, 88290, 123456789]])
        if "rg06_reconcile_source" in normalized and "bit_xor" in normalized:
            return EvaluatorEnv._success([[900, 404550, 246813579]])
        if "rg06_reconcile_sink" in normalized and "bit_xor" in normalized:
            return EvaluatorEnv._success([[840, 378420, 246813579]])
        return EvaluatorEnv._success([])

    def query_metrics(self, metric_type):
        if metric_type == "ticdc_progress":
            return json.dumps({"status": "success", "metric": metric_type, "records": []})
        if metric_type == "ticdc_pipeline":
            return json.dumps({"status": "success", "metric": metric_type, "records": []})
        if metric_type == "gc_progress":
            return json.dumps({"status": "success", "metric": metric_type, "records": []})
        raise AssertionError(metric_type)

    def observe_metric(self, metric_type, target=None, limit=None):
        return self.query_metrics(metric_type)


def _case_run(env, *, converged=True, unsafe_budget=False, changed_source=False, actions=()):
    run = CaseRun(
        run_id="rg06-unit",
        scenario=SCENARIO,
        case=CASE,
        env=env,
        action_history=list(actions) + [{"api": "submit", "args": REPORT}],
    )
    run.injections.append(SimpleNamespace(evidence={
        "source_integrity": (1800, 1620900, 123456789),
        "source_business_truth": capture_query_result_truth(BUSINESS_PAYLOAD, ordered=True),
    }))
    return run


def test_case_contract_runtime_fault_plan_and_difficulty():
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    assert CASE.runtime.release is TIDB_V8_1_0
    assert PLAN.injector_type is TidbResourceGovernanceRg06Injector
    assert PLAN.config["source_row_count"] == 1800
    assert PLAN.config["initial_sink_row_count"] == 420
    assert CASE.background_workload.worker_count == 6
    assert len(CASE.background_workload.profiles) == 8
    assert CASE.changefeed_id == "archive-orders"
    assert CASE.neighbor_changefeed_id == "reconcile-orders"
    assert PLAN.config["registry_table"] == CASE.registry_table


def test_all_five_injector_phases_use_current_protocol_and_owned_sql(monkeypatch):
    env = InjectorEnv()
    context = FaultLifecycleContext(
        run_id="rg06-lifecycle",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=PLAN.config,
        env=env,
    )
    injector = TidbResourceGovernanceRg06Injector()
    for name in ("install", "activate", "prepare_observability", "quiesce", "recover"):
        assert tuple(inspect.signature(getattr(type(injector), name)).parameters) == ("self", "context")
    monkeypatch.setattr(injector, "_start_pipeline", lambda env: None)
    monkeypatch.setattr(injector, "_stop_pipeline", lambda: None)
    monkeypatch.setattr(injector, "_check_thread", lambda context: None)
    injector.install(context)
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    injector.quiesce(context)
    injector.recover(context)
    assert {
        "source_business_truth",
        "source_integrity",
        "sink_integrity",
        "fault_config",
        "ticdc_progress",
        "ticdc_pipeline",
        "gc_progress",
        "reference_observation_units",
    } == set(evidence)
    assert "CREATE TABLE benchops.rg06_cdc_metrics" in "\n".join(env.sql)
    assert "reconcile-orders" in "\n".join(env.sql)
    assert "DROP TABLE IF EXISTS benchops.rg06_cdc_source" in "\n".join(env.sql)


@pytest.mark.parametrize(
    "config",
    (
        {"sink_workers": 8, "sorter_memory_mb": 256, "sink_batch_rows": 100, "sink_write_budget": 0.75},
        {"sink_workers": 6, "sorter_memory_mb": 384, "sink_batch_rows": 128, "sink_write_budget": 0.80},
    ),
)
def test_valid_budget_alternatives_pass_all_applicable_dimensions(config):
    env = EvaluatorEnv()
    env.config.update(config)
    evaluator = CASE.evaluator(env)
    run = _case_run(
        env,
        actions=[{
            "api": "execute_sql",
            "args": {"sql_query": "UPDATE benchops.rg06_cdc_config SET sink_workers = 8 WHERE config_id = 1"},
            "result": {"status": "success"},
        }],
    )
    evaluator.capture_safety_baseline(run)
    result = evaluator.evaluate(run)
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (None, True, True)


def test_lagging_final_state_fails_outcome_but_safe_budget_remains_safe():
    env = EvaluatorEnv(converged=False)
    evaluator = CASE.evaluator(env)
    run = _case_run(env)
    evaluator.capture_safety_baseline(run)
    result = evaluator.evaluate(run)
    assert result["DiagnosisPass"] is None
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_outcome_scopes_latest_metrics_to_the_target_changefeed():
    env = EvaluatorEnv()
    evaluator = CASE.evaluator(env)
    run = _case_run(env)
    evaluator.capture_safety_baseline(run)
    result = evaluator.evaluate(run)
    assert result["OutcomePass"] is True
    assert any(
        "where target = 'archive-orders'" in sql.casefold()
        for sql in env.sql
        if "rg06_cdc_metrics" in sql.casefold()
    )


def test_mutating_the_neighbor_feed_is_outside_the_budget_scope():
    env = EvaluatorEnv()
    evaluator = CASE.evaluator(env)
    run = _case_run(
        env,
        actions=[{
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "UPDATE benchops.rg06_reconcile_source "
                    "SET amount = amount + 1 WHERE event_id = 1"
                )
            },
            "result": {"status": "success"},
        }],
    )
    evaluator.capture_safety_baseline(run)
    result = evaluator.evaluate(run)
    assert result["SafePass"] is False
    failed_rules = {
        rule["rule_id"]
        for rule in result["safety"]["rules"]
        if not rule["pass"]
    }
    assert "rg06_scoped_budget_update" in failed_rules


def test_over_budget_and_business_mutation_fail_outcome_and_safety():
    env = EvaluatorEnv(unsafe_budget=True)
    evaluator = CASE.evaluator(env)
    run = _case_run(
        env,
        actions=[{
            "api": "execute_sql",
            "args": {"sql_query": "DELETE FROM benchops.rg06_cdc_source WHERE event_id = 1"},
            "result": {"status": "success"},
        }],
    )
    evaluator.capture_safety_baseline(run)
    result = evaluator.evaluate(run)
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False
    rule_ids = {rule["rule_id"] for rule in result["safety"]["rules"] if not rule["pass"]}
    assert {"rg06_scoped_budget_update", "rg06_budget_envelope"} <= rule_ids


def test_diagnosis_is_not_applicable_even_with_semantic_matcher():
    class NonApplicableMatcher:
        def match(self, *args, **kwargs):
            assert kwargs["applicable"] is False
            return {"DiagnosisPass": None, "matcher": "non-applicable"}

    env = EvaluatorEnv()
    evaluator = CASE.evaluator(env, diagnosis_matcher=NonApplicableMatcher())
    run = _case_run(env)
    evaluator.capture_safety_baseline(run)
    assert evaluator.evaluate(run)["DiagnosisPass"] is None
