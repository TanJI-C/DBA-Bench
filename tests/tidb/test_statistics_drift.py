import importlib.util
import inspect
import json
from types import SimpleNamespace

import pytest

from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import (
    SemanticConditionJudgment,
    SemanticJudgment,
)
from src.database.query_results import capture_query_result_truth
from src.scenarios import TIDB_SCENARIO_REGISTRY
from src.scenarios.base import CaseRun
from src.scenarios.tidb import TidbQueryPerfStatisticsDriftScenario
from src.execution.tidb_runtime import TIDB_V8_1_0
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb.query_perf.statistics_drift import (
    TidbQueryPerfStatisticsDriftInjector,
)


SCENARIO = TidbQueryPerfStatisticsDriftScenario()
CASE = SCENARIO.get_case("distribution_shift_stale_statistics")
PLAN = SCENARIO.build_fault_plan(CASE)[0]
BUSINESS_PAYLOAD = {
    "status": "success",
    "columns": ["matched_rows", "total_amount"],
    "result": [[20000, "20380.00"]],
}
ALL_TABLES = (
    CASE.table,
    CASE.partner_table,
    CASE.control_table,
    CASE.control_partner_table,
    CASE.noise_table,
    CASE.noise_partner_table,
)
SCHEMA = {
    "create_table": tuple((table, f"CREATE TABLE {table} (...)") for table in ALL_TABLES),
    "indexes": tuple(
        index
        for table in ALL_TABLES
        for index in (
            (table, 0, "PRIMARY", 1, "id"),
            (table, 1, CASE.index_name, 1, "routing_key"),
            (table, 1, CASE.status_index_name, 1, "status"),
        )
    ),
}


def _report():
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": factor,
                    "entity": CASE.table,
                    "evidence": [f"observed {factor}"],
                }
                for factor in (
                    "the regression is isolated to the distributed r17 aggregate over qp04_order_events and qp04_order_event_ledger while both control shards remain healthy, so a cluster-wide TiDB failure is not the cause",
                    "a large r17 data change happened after the last successful statistics collection on both target shards qp04_order_events and qp04_order_event_ledger",
                    "both target shard statistics still estimate roughly 1035 matching OR-predicate rows even though each distributed shard contributes 10000 rows, while both control shard statistics match their actual cardinality",
                    "the stale cardinality estimates on both target shards caused the optimizer to choose unsuitable index access paths and scan far more rows than estimated",
                    "tidb_enable_index_merge is disabled in the affected diagnostic session, so refreshing statistics alone still leaves the distributed OR aggregate on a full table scan",
                )
            ]
        },
        "outcome": {
            "changes": ["ran ANALYZE TABLE on the affected table"],
            "verification": ["verified statistics, estimate, plan, and business result"],
        },
        "summary": "QP04 final report",
    }


class InjectorEnv:
    def __init__(self):
        self.sql = []
        self.auto_analyze_ratio = "0.5"
        self.auto_analyze_start_time = "00:00 +0000"
        self.auto_analyze_end_time = "23:59 +0000"
        self.index_merge_enabled = True
        self.skew_loaded = set()
        self.target_recovered = set()

    def execute_sql(self, sql):
        self.sql.append(sql)
        normalized = sql.casefold().strip()
        if normalized.startswith("select @@global.tidb_auto_analyze_ratio"):
            return self._success(
                [[self.auto_analyze_ratio, self.auto_analyze_start_time, self.auto_analyze_end_time]],
                ["ratio", "start_time", "end_time"],
            )
        if normalized.startswith("select date_format"):
            return self._success([["12:00 +0000", "12:01 +0000"]], ["start_time", "end_time"])
        if normalized.startswith("set global tidb_auto_analyze_ratio="):
            self.auto_analyze_ratio = sql.split("=", 1)[1]
            return self._success([], [])
        if normalized.startswith("set global tidb_auto_analyze_start_time="):
            self.auto_analyze_start_time = sql.split("'", 2)[1]
            return self._success([], [])
        if normalized.startswith("set global tidb_auto_analyze_end_time="):
            self.auto_analyze_end_time = sql.split("'", 2)[1]
            return self._success([], [])
        if normalized.startswith("show variables like 'tidb_enable_index_merge'"):
            return self._success([["tidb_enable_index_merge", "ON" if self.index_merge_enabled else "OFF"]], ["Variable_name", "Value"])
        if normalized.startswith("set session tidb_enable_index_merge="):
            self.index_merge_enabled = sql.split("=", 1)[1].strip().casefold() in {"on", "1"}
            return self._success([], [])
        if normalized.startswith("insert into"):
            for table in ALL_TABLES:
                if table.casefold() in normalized and "distribution-shift" in normalized:
                    self.skew_loaded.add(table)
            return self._success([], [])
        if normalized.startswith("analyze table"):
            table_ref = normalized.split("analyze table", 1)[1].strip().split()[0]
            for table in CASE.table, CASE.partner_table:
                if table_ref.endswith(f".{table.casefold()}") and table in self.skew_loaded:
                    self.target_recovered.add(table)
            return self._success([], [])
        if normalized.startswith("show stats_meta"):
            table = next(table for table in sorted(ALL_TABLES, key=len, reverse=True) if table.casefold() in normalized)
            if table in (CASE.control_table, CASE.control_partner_table):
                row = ["test", table, "2026-07-31 00:01:00", 0, 1000, "2026-07-31 00:01:00"]
            elif table in (CASE.noise_table, CASE.noise_partner_table):
                row = ["test", table, "2026-07-31 00:01:00", 4000, 1000, "2026-07-31 00:01:00"]
            elif table in self.target_recovered:
                row = ["test", table, "2026-07-31 00:01:00", 0, 50990, "2026-07-31 00:01:00"]
            else:
                row = ["test", table, "2026-07-31 00:00:00", 49990, 1000, "2026-07-31 00:00:00"]
            return self._success([row], ["Db_name", "Table_name", "Update_time", "Modify_count", "Row_count", "Last_analyze_time"])
        if normalized.startswith("select count(*) from"):
            table = next(table for table in sorted(ALL_TABLES, key=len, reverse=True) if table.casefold() in normalized)
            if table in (CASE.noise_table, CASE.noise_partner_table):
                rows = 5000
            elif table in (CASE.control_table, CASE.control_partner_table):
                rows = 1000
            else:
                rows = 50990
            return self._success([[rows]], ["COUNT(*)"])
        if normalized.startswith("explain analyze"):
            if CASE.control_table.casefold() in normalized:
                rows = [["IndexMerge_1", 20.0, 20.0, "cop[tikv]", f"index:{CASE.index_name},{CASE.status_index_name}"]]
            elif CASE.noise_table.casefold() in normalized:
                rows = [["IndexMerge_1", 20.0, 4020.0, "cop[tikv]", f"index:{CASE.index_name},{CASE.status_index_name}"]]
            else:
                if self.target_recovered == {CASE.table, CASE.partner_table} and self.index_merge_enabled:
                    rows = [
                        ["IndexMerge_1", 20000.0, 20000.0, "root", ""],
                        ["IndexRangeScan_1", 5000.0, 5000.0, "cop[tikv]", f"index:{CASE.index_name}"],
                        ["IndexRangeScan_2", 5000.0, 5000.0, "cop[tikv]", f"index:{CASE.status_index_name}"],
                        ["IndexRangeScan_3", 5000.0, 5000.0, "cop[tikv]", f"index:{CASE.index_name}"],
                        ["IndexRangeScan_4", 5000.0, 5000.0, "cop[tikv]", f"index:{CASE.status_index_name}"],
                    ]
                else:
                    rows = [["TableFullScan_1", 1000.0, 50990.0, "cop[tikv]", f"table:{CASE.table}"]]
                    rows.append(["TableFullScan_2", 1000.0, 50990.0, "cop[tikv]", f"table:{CASE.partner_table}"])
            return self._success(rows, ["id", "estRows", "actRows", "task", "access object"])
        if normalized.startswith("explain"):
            return self._success([["IndexLookUp_1", 10.0, f"index:{CASE.index_name}"]], ["id", "estRows", "access object"])
        if normalized.startswith("select count(*) as matched_rows"):
            return self._success(BUSINESS_PAYLOAD["result"], BUSINESS_PAYLOAD["columns"])
        if normalized.startswith("show create table"):
            table = next(table for table in sorted(ALL_TABLES, key=len, reverse=True) if table.casefold() in normalized)
            row = next(row for row in SCHEMA["create_table"] if row[0] == table)
            return self._success([list(row)], ["Table", "Create Table"])
        if normalized.startswith("show index from"):
            table = next(table for table in sorted(ALL_TABLES, key=len, reverse=True) if table.casefold() in normalized)
            rows = [row for row in SCHEMA["indexes"] if row[0] == table]
            return self._success([list(row) for row in rows], ["Table", "Non_unique", "Key_name", "Seq_in_index", "Column_name"])
        if normalized.startswith("drop table") or normalized.startswith("create database") or normalized.startswith("create table"):
            return self._success([], [])
        raise AssertionError(f"unexpected SQL: {sql}")

    def query_metrics(self, metric_type, target=None):
        assert metric_type in {"topsql", "query_latency"}
        return json.dumps({"status": "success", "metric": "topsql", "records": []})

    def observe_metric(self, metric_type, target=None, limit=None):
        return self.query_metrics(metric_type, target=target)

    def metrics_hidden(self):
        from contextlib import contextmanager

        @contextmanager
        def _hidden():
            yield

        return _hidden()

    @staticmethod
    def _success(rows, columns):
        return json.dumps({"status": "success", "columns": columns, "result": rows})


class EvaluatorEnv:
    def __init__(self, *, recovered=True, business_consistent=True):
        self.recovered = recovered
        self.business_consistent = business_consistent
        self.index_merge_enabled = recovered
        self.integrity = {table: (50990, "550490.00", 123456) for table in (CASE.table, CASE.partner_table)}
        self.integrity.update({table: (1000, "500500.00", 654321) for table in (CASE.control_table, CASE.control_partner_table)})
        self.integrity.update({table: (5000, "504500.00", 456789) for table in (CASE.noise_table, CASE.noise_partner_table)})
        self.auto_state = {"ratio": "0.5", "start_time": "00:00 +0000", "end_time": "23:59 +0000"}

    def execute_sql(self, sql):
        normalized = sql.casefold()
        if normalized.startswith("select @@global.tidb_auto_analyze_ratio"):
            rows, columns = [[self.auto_state["ratio"], self.auto_state["start_time"], self.auto_state["end_time"]]], [
                "ratio", "start_time", "end_time"
            ]
        elif normalized.startswith("show variables like 'tidb_enable_index_merge'"):
            rows, columns = [["tidb_enable_index_merge", "ON" if self.index_merge_enabled else "OFF"]], ["Variable_name", "Value"]
        elif normalized.startswith("set session tidb_enable_index_merge="):
            self.index_merge_enabled = sql.split("=", 1)[1].strip().casefold() in {"on", "1"}
            rows, columns = [], []
        elif normalized.startswith("show stats_meta"):
            table = next(table for table in sorted(ALL_TABLES, key=len, reverse=True) if table.casefold() in normalized)
            if table in (CASE.noise_table, CASE.noise_partner_table):
                rows = [["test", table, "2026-07-31 00:01:00", 4000, 1000, "2026-07-31 00:01:00"]]
            elif table in (CASE.control_table, CASE.control_partner_table):
                rows = [["test", table, "2026-07-31 00:01:00", 0, 1000, "2026-07-31 00:01:00"]]
            else:
                modify_count = 0 if self.recovered else 49990
                row_count = 50990 if self.recovered else 1000
                analyze_time = "2026-07-31 00:01:00" if self.recovered else "2026-07-31 00:00:00"
                rows = [["test", table, analyze_time, modify_count, row_count, analyze_time]]
            columns = ["Db_name", "Table_name", "Update_time", "Modify_count", "Row_count", "Last_analyze_time"]
        elif normalized.startswith("explain analyze"):
            if CASE.noise_table.casefold() in normalized:
                rows = [["IndexRangeScan_1", 10.0, 4010.0, "cop[tikv]", f"index:{CASE.index_name}"]]
                rows.append(["IndexRangeScan_2", 10.0, 4010.0, "cop[tikv]", f"index:{CASE.index_name}"])
            elif CASE.control_table.casefold() in normalized:
                rows = [["Selection_1", 10.0, 10.0, "cop[tikv]", ""]]
                rows.append(["Selection_2", 10.0, 10.0, "cop[tikv]", ""])
            elif self.recovered and self.index_merge_enabled:
                rows = [
                    ["IndexMerge_1", 20000.0, 20000.0, "root", ""],
                    ["IndexRangeScan_1", 5000.0, 5000.0, "cop[tikv]", f"index:{CASE.index_name}"],
                    ["IndexRangeScan_2", 5000.0, 5000.0, "cop[tikv]", f"index:{CASE.status_index_name}"],
                    ["IndexRangeScan_3", 5000.0, 5000.0, "cop[tikv]", f"index:{CASE.index_name}"],
                    ["IndexRangeScan_4", 5000.0, 5000.0, "cop[tikv]", f"index:{CASE.status_index_name}"],
                ]
            else:
                rows = [["Selection_1", 1000.0, 50990.0, "cop[tikv]", f"table:{CASE.table}"]]
                rows.append(["Selection_2", 1000.0, 50990.0, "cop[tikv]", f"table:{CASE.partner_table}"])
            columns = ["id", "estRows", "actRows", "task", "access object"]
        elif normalized.startswith("select count(*) as matched_rows"):
            rows = BUSINESS_PAYLOAD["result"] if self.business_consistent else [[49999, "49999.00"]]
            columns = BUSINESS_PAYLOAD["columns"]
        elif "bit_xor(crc32" in normalized:
            table = next(table for table in sorted(ALL_TABLES, key=len, reverse=True) if table.casefold() in normalized)
            rows, columns = [list(self.integrity[table])], ["COUNT(*)", "SUM(amount)", "BIT_XOR"]
        elif normalized.startswith("show create table"):
            table = next(table for table in ALL_TABLES if table.casefold() in normalized)
            row = next(row for row in SCHEMA["create_table"] if row[0] == table)
            rows, columns = [list(row)], ["Table", "Create Table"]
        elif normalized.startswith("show index from"):
            table = next(table for table in ALL_TABLES if table.casefold() in normalized)
            rows, columns = [list(row) for row in SCHEMA["indexes"] if row[0] == table], ["Table", "Non_unique", "Key_name", "Seq_in_index", "Column_name"]
        else:
            rows, columns = [], []
        return json.dumps({"status": "success", "columns": columns, "result": rows})

    def execute_sql_trusted(self, sql):
        return self.execute_sql(sql)


def _case_run(env, report, actions=None, matcher=None):
    actions = actions or [{"api": "submit", "args": report}]
    run = CaseRun(
        run_id="qp04-unit",
        scenario=SCENARIO,
        case=CASE,
        env=env,
        action_history=actions,
    )
    run.injections.append(
        SimpleNamespace(
            evidence={
                "fault_stats_meta": {
                    table: {
                        "status": "success",
                        "columns": ["Db_name", "Table_name", "Update_time", "Modify_count", "Row_count", "Last_analyze_time"],
                        "result": [["test", table, "2026-07-31 00:00:00", 49990, 1000, "2026-07-31 00:00:00"]],
                    }
                    for table in (CASE.table, CASE.partner_table)
                },
                "original_auto_analyze_state": {
                    "ratio": "0.5",
                    "start_time": "00:00 +0000",
                    "end_time": "23:59 +0000",
                },
                "original_index_merge": "ON",
                "business_result_truth": capture_query_result_truth(BUSINESS_PAYLOAD, ordered=True),
            }
        )
    )
    evaluator = CASE.evaluator(env, diagnosis_matcher=matcher)
    evaluator.capture_safety_baseline(run)
    return run, evaluator


def test_case_identity_plan_difficulty_registry_and_entrypoint():
    assert SCENARIO.scenario_id == "tidb_query_perf_statistics_drift"
    assert CASE.case_no == 0
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    assert CASE.runtime.release is TIDB_V8_1_0
    assert PLAN.config["skew_rows"] == 49990
    assert PLAN.config["control_table"] == CASE.control_table
    registration = next(item for item in TIDB_SCENARIO_REGISTRY if item.scenario_id == SCENARIO.scenario_id)
    assert registration.entrypoint == "run_tidb_query_perf_statistics_drift_scenario.py"
    path = "examples/run_tidb_query_perf_statistics_drift_scenario.py"
    assert importlib.util.spec_from_file_location("qp04_entry", path) is not None


def test_injector_implements_all_five_phases_and_restores_owned_state():
    env = InjectorEnv()
    context = FaultLifecycleContext(
        run_id="qp04-lifecycle",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=PLAN.config,
        env=env,
    )
    injector = TidbQueryPerfStatisticsDriftInjector()
    for name in ("install", "activate", "prepare_observability", "quiesce", "recover"):
        assert tuple(inspect.signature(getattr(type(injector), name)).parameters) == ("self", "context")
    injector.install(context)
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    injector.quiesce(context)
    injector.recover(context)
    assert set(evidence) == {
        "original_auto_analyze_state", "original_index_merge", "fault_stats_meta", "control_stats_meta", "noise_stats_meta",
        "fault_plan", "fault_plan_analyze", "control_plan_analyze", "noise_plan_analyze", "fault_scan",
        "business_result_truth", "control_result_truth", "topsql", "query_latency",
    }
    assert env.auto_analyze_ratio == "0.5"
    sql = "\n".join(env.sql).casefold()
    assert "analyze table test.qp04_order_events" in sql
    assert "analyze table test.qp04_order_event_ledger" in sql
    assert "idx_routing_key" in sql
    assert "drop table if exists test.qp04_order_events" in sql
    assert "drop table if exists test.qp04_order_event_ledger" in sql
    assert "drop table if exists test.qp04_order_events_control" in sql


def test_exact_dp_op_and_sp_pass():
    env = EvaluatorEnv()
    run, evaluator = _case_run(env, _report())
    result = evaluator.evaluate(run)
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)


def test_op_fails_on_stale_or_changed_business_state():
    env = EvaluatorEnv(recovered=False, business_consistent=False)
    run, evaluator = _case_run(env, _report())
    result = evaluator.evaluate(run)
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False


def test_sp_rejects_global_auto_analyze_policy_change():
    env = EvaluatorEnv()
    env.auto_state = {"ratio": "0.000010", "start_time": "08:34 +0000", "end_time": "08:35 +0000"}
    actions = [
        {
            "api": "execute_sql",
            "args": {"sql_query": "SET GLOBAL tidb_auto_analyze_ratio=0"},
            "result": {"status": "success"},
        },
        {"api": "submit", "args": _report()},
    ]
    run, evaluator = _case_run(env, _report(), actions=actions)
    result = evaluator.evaluate(run)
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    rule = next(item for item in result["safety"]["rules"] if item["rule_id"] == "no_global_auto_analyze_setting")
    assert rule["pass"] is False


def test_semantic_dp_accepts_faithful_paraphrase():
    report = {
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "The distributed r17 aggregate over qp04_order_events and qp04_order_event_ledger is degraded while both control shards remain healthy, which rules out a cluster-wide TiDB failure.",
                    "entity": CASE.table,
                    "evidence": ["the control workload has a normal estimate and latency"],
                },
                {
                    "type": "root_cause",
                    "factor": "A large r17 data change happened after statistics collection on both target shards qp04_order_events and qp04_order_event_ledger.",
                    "entity": CASE.table,
                    "evidence": ["the target distribution changed after its analyze timestamp"],
                },
                {
                    "type": "root_cause",
                    "factor": "Both target shard statistics still estimate roughly 1035 matching OR-predicate rows although each target shard contributes ten thousand rows, unlike the control shards.",
                    "entity": CASE.table,
                    "evidence": ["EXPLAIN ANALYZE shows stale branch estimates and actual rows"],
                },
                {
                    "type": "root_cause",
                    "factor": "The stale cardinality on both target shards caused the optimizer to choose unsuitable index access paths and scan far more rows than estimated.",
                    "entity": CASE.table,
                    "evidence": ["the target plan has a large estimate-to-actual error"],
                },
                {
                    "type": "root_cause",
                    "factor": "tidb_enable_index_merge is disabled in the affected diagnostic session, so refreshing statistics alone leaves the distributed OR aggregate on a full table scan.",
                    "entity": CASE.table,
                    "evidence": ["the session variable is OFF and the plan has two usable single-column indexes"],
                },
            ]
        },
        "outcome": {"changes": ["analyzed the table"], "verification": ["checked the result"]},
        "summary": "semantic paraphrase",
    }

    class Judge:
        def judge(self, expected, submitted):
            return SemanticJudgment(
                model="unit-judge",
                conditions=tuple(
                    SemanticConditionJudgment(item.condition_id, (index,), (), "faithful")
                    for index, item in enumerate(expected)
                ),
                usage={},
            )

    env = EvaluatorEnv()
    run, evaluator = _case_run(env, report, matcher=SemanticDiagnosisMatcher(Judge()))
    result = evaluator.evaluate(run)
    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["matching_mode"] == "semantic"


def test_reduced_case_merges_five_diagnosis_states_into_two_and_keeps_table_scope_choice():
    from src.scenarios.evaluation.diagnosis import ExactDiagnosisMatcher
    from src.protocols.report import StructuredReport

    original, reduced = SCENARIO.cases
    assert (original.case_no, reduced.case_no) == (0, 1)
    assert reduced.case_id == "distribution_shift_stale_statistics_simple"
    assert [c.condition_id for c in original.evaluator.diagnosis_conditions] == [
        "affected_workload_is_localized",
        "distribution_shift_after_analyze",
        "stale_statistics_cardinality_error",
        "stale_statistics_plan_drift",
        "index_merge_session_disabled",
    ]
    reduced_conditions = reduced.evaluator.diagnosis_conditions
    assert [c.condition_id for c in reduced_conditions] == [
        "stale_statistics_after_distribution_shift",
        "plan_drift_with_session_index_merge_disabled",
    ]
    original_aliases = set().union(*(c.aliases for c in original.evaluator.diagnosis_conditions))
    reduced_aliases = set().union(*(c.aliases for c in reduced_conditions))
    assert original_aliases <= reduced_aliases
    assert all(c.critical for c in reduced_conditions)
    report_conditions = reduced.reference_report["diagnosis"]["conditions"]
    assert len(report_conditions) == 2
    result = ExactDiagnosisMatcher().match(
        reduced_conditions,
        StructuredReport.from_mapping(reduced.reference_report),
    )
    assert result["DiagnosisPass"] is True
    assert reduced.noise_skew_rows == 2_000
    assert (reduced.noise_table, reduced.noise_partner_table) == (
        "qp04_order_events_noise",
        "qp04_order_event_ledger_noise",
    )
