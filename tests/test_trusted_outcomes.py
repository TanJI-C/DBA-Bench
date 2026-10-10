import json
from types import SimpleNamespace

import pytest

from src.database.query_results import capture_query_result_truth
from src.scenarios import ALL_SCENARIOS
from src.scenarios.base import CaseRun


TARGETS = (
    ("pg_query_perf_heavy_offset_pagination", "branch_order_deep_offset"),
    ("pg_system_failure_deadlock", "checkout_order_deadlock"),
    ("pg_system_failure_page_corruption", "order_line_audit_page_corruption"),
)


def _case(scenario_id, case_id):
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == scenario_id)
    return scenario, scenario.get_case(case_id)


def _report(case):
    return {
        "diagnosis": {
            "conditions": [
            {
                "type": "finding",
                    "factor": sorted(condition.aliases)[0],
                    "entity": case.case_id,
                    "evidence": [sorted(condition.aliases)[0]],
                }
                for condition in case.evaluator.diagnosis_conditions
            ]
        },
        "outcome": {"changes": ["pitr", "consistent lock order", "keyset"], "verification": ["verified"]},
        "summary": "diagnostic report",
    }


class FinalStateEnv:
    def __init__(self, case, *, repaired=False):
        self.case = case
        self.repaired = repaired
        # deadlock recurrence probe：金额状态 + 重放 seam（仅 deadlock case 使用）。
        self._amounts = {
            int(order_id): 100.0 + 100.0 * index
            for index, order_id in enumerate(getattr(case, "order_ids", ()) or ())
        } or {101: 100.0, 102: 200.0}
        self.deadlock_probe_pair_result = self._apply_deadlock_probe_replay
        # 健康孪生计划线（仅 checkout case）：健康金额状态 + 健康重放 seam。
        self._healthy_amounts = {
            int(order_id): 300.0 + 100.0 * index
            for index, order_id in enumerate(getattr(case, "healthy_order_ids", ()) or ())
        }
        self.healthy_probe_pair_result = self._apply_healthy_probe_replay

    def _apply_deadlock_probe_replay(self, case):
        self._amounts = {
            order_id: amount + 2.0
            for order_id, amount in self._amounts.items()
        }
        return {"ok": True, "errors": []}

    def _apply_healthy_probe_replay(self, case):
        self._healthy_amounts = {
            order_id: amount + 2.0
            for order_id, amount in self._healthy_amounts.items()
        }
        return {"ok": True, "errors": []}

    def execute_sql(self, sql):
        normalized = sql.casefold()
        if self.case.case_id == "branch_order_deep_offset":
            if "from pg_settings" in normalized:
                result = [["work_mem", "4096", "default", "", False]]
            elif "from pg_file_settings" in normalized:
                result = []
            elif "c.relkind <> 'i'" in normalized:
                result = [["public", self.case.table, "r"]]
            elif "from pg_constraint" in normalized:
                result = []
            elif "i.indisvalid" in normalized:
                result = [[
                    "public", self.case.table, self.case.index_name,
                    f"CREATE INDEX {self.case.index_name} ON {self.case.table} ({self.case.order_column})",
                    True,
                ]]
            elif "from pg_db_role_setting" in normalized:
                result = []
            elif "from pg_roles" in normalized:
                result = [["postgres", None]]
            elif "role_table_grants" in normalized:
                result = []
            elif "pg_indexes" in normalized:
                result = [[1]]
            else:
                result = [[1]]
        elif self.case.case_id == "checkout_order_deadlock":
            if "plan_sync_job_registry" in normalized:
                # 调度控制面默认持有一行 scheduled 作业（probe tick 经服务端
                # DO 块重部署并执行，不经结果绑定读取模板全文）。
                result = [["plan_sync_publish", "scheduled", 7]]
            elif "returns_plan_source" in normalized or "returns_job_steps" in normalized:
                # 健康计划源/已发布 steps 与装机映射一致（全升序）。
                order_a, order_b = (int(value) for value in self.case.healthy_order_ids)
                job_a, job_b = (int(value) for value in self.case.healthy_job_ids)
                result = [
                    [job_a, 10, order_a], [job_a, 20, order_b],
                    [job_b, 10, order_a], [job_b, 20, order_b],
                ]
            elif "o_total_amount" in normalized and "5001" in normalized:
                result = [
                    [order_id, amount]
                    for order_id, amount in sorted(self._healthy_amounts.items())
                ]
            elif "o_total_amount" in normalized:
                result = [
                    [order_id, amount]
                    for order_id, amount in sorted(self._amounts.items())
                ]
            elif "checkout_job_steps" in normalized:
                result = [[101, 1001], [101, 1002], [102, 1002], [102, 1001]]
            else:
                result = [[
                    "deadlock detected; process_checkout_job; job 101; job 102; "
                    "batch_job_executor_1; batch_job_executor_2"
                ]]
        elif self.case.case_id == "order_line_audit_page_corruption":
            # Result-type outcome: an unrepaired read path still errors, a
            # repaired one serves the baseline comparison rows.
            if not self.repaired and ("order_line_audit" in normalized or "order_detail_live" in normalized):
                return json.dumps({"status": "error", "error": "invalid page checksum"})
            result = [[1]]
        else:
            raise AssertionError(self.case.case_id)
        return json.dumps({"status": "success", "result": result})


def _run(scenario, case, env, actions):
    fault_plan = json.dumps({
        "status": "success",
        "result": [[{"Plan": {"Node Type": "WindowAgg"}, "Execution Time": 1000.0}]],
    })
    evidence = {"fault_plan": fault_plan}
    if case.case_id == "branch_order_deep_offset":
        evidence.update({
            "fault_query_seconds": 1.0,
            "fault_query_truth": capture_query_result_truth({
                "columns": [f"column_{index}" for index in range(12)],
                "result": [[row] * 12 for row in range(10)],
            }, ordered=True),
        })
    run = CaseRun(
        run_id=f"trusted-{case.case_id}",
        scenario=scenario,
        case=case,
        env=env,
        injections=[SimpleNamespace(evidence=evidence)],
        action_history=[*actions, {"api": "submit", "args": _report(case)}],
    )
    evaluator = case.evaluator(env)
    evaluator.capture_safety_baseline(run)
    return evaluator.evaluate(run)


@pytest.mark.parametrize("scenario_id,case_id", TARGETS)
def test_report_only_cannot_pass_outcome(scenario_id, case_id):
    scenario, case = _case(scenario_id, case_id)
    result = _run(scenario, case, FinalStateEnv(case), [])
    assert result["OutcomePass"] is False


@pytest.mark.parametrize("scenario_id,case_id", TARGETS)
def test_outcome_uses_final_state_and_successful_diagnosis_action(scenario_id, case_id):
    scenario, case = _case(scenario_id, case_id)
    if case_id == "branch_order_deep_offset":
        actions = [{
                "api": "execute_sql",
                "args": {"sql_query": f"EXPLAIN SELECT * FROM {case.table}"},
                "result": {
                    "status": "success",
                    "result": [[{"Plan": {"Node Type": "Limit"}, "Execution Time": 100.0}]],
                },
        }]
    elif case_id == "checkout_order_deadlock":
        actions = [{
            "api": "read_log",
            "args": {"log_type": "pg_log", "lines": 100},
                "result": {
                    "status": "success",
                    "result": (
                        "deadlock detected: process 11 waits for a lock blocked by process 12; "
                        "process 12 waits for a lock blocked by process 11; "
                        f"process_checkout_job {case.job_ids[0]} {case.job_ids[1]}"
                    ),
                },
        }]
    else:
        actions = [{
            "api": "read_log",
            "args": {"log_type": "pg_log", "lines": 100},
                "result": {"status": "success", "result": f"invalid page checksum relation {case.table}"},
        }]
    result = _run(scenario, case, FinalStateEnv(case, repaired=True), actions)
    assert result["OutcomePass"] is (case_id != "branch_order_deep_offset")
    assert result["outcome"]["trusted_artifacts_used"]
    assert result["outcome"]["report_fields_used"] == []
