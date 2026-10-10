import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbBusinessChangeTableRecoveryScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


SCENARIO = TidbBusinessChangeTableRecoveryScenario()


def _report(case) -> dict:
    return {
        "report": {
            "diagnosis": {"conditions": []},
            "outcome": {
                "changes": [
                    f"Recovered the last-known-good {case.logical_table} release from the exact historical DROP job before GC cleanup.",
                    "Restored the pre-run tidb_gc_life_time after the recovery window was no longer needed.",
                ],
                "verification": [
                    f"The {case.source_row_count}-row primary-key fixture, event-id sum, and CRC {case.expected_crc} match the handoff truth.",
                    "The original DROP job is synced and ADMIN CHECK TABLE returned a successful empty result.",
                ],
            },
            "summary": f"The incident-boundary {case.service_name} release was reconstructed from control epochs and transition history, then recovered without data recreation.",
        }
    }


class TidbBusinessChangeTableRecoveryFullMockAgent(BaseAgent):
    def __init__(self, case):
        super().__init__()
        self.case = case

    def solve(self):
        case = self.case
        self.execute(
            "query_metrics",
            {"metric_type": "active_connections"},
            thinking="先看业务查询失败是否集中在目标表，同时保留归档和监控 profile 作为噪声对照。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT TABLE_NAME FROM information_schema.tables "
                    f"WHERE TABLE_SCHEMA='{case.database}' ORDER BY TABLE_NAME"
                )
            },
            thinking=f"确认目标对象缺失，而不是 TiDB 节点或整个 {case.database} schema 不可用。",
        )
        incident = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT incident_id, incident_at, last_known_good_at, expected_control_epoch "
                    f"FROM {case.database}.{case.incident_context_table} WHERE service_name='{case.service_name}' "
                    f"AND environment='{case.environment}' AND logical_table='{case.logical_table}'"
                )
            },
            thinking="先确定事故边界和控制 epoch，不能把事故之后的 desired/hotfix 状态误当成事故时 serving 版本。",
        )
        if len(incident["result"]) != 1:
            raise RuntimeError(f"BC07 mock expected one incident boundary: rows={incident['result']!r}")
        incident_at = str(incident["result"][0][1])
        expected_epoch = int(incident["result"][0][3])
        controls = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT control_id, region, control_role, control_key, effective_at, status, "
                    f"traffic_percent, control_epoch FROM {case.database}.{case.release_control_table} "
                    f"WHERE service_name='{case.service_name}' AND environment='{case.environment}' "
                    f"AND logical_table='{case.logical_table}' ORDER BY effective_at, control_id"
                )
            },
            thinking="按 incident_at、global observed control、serving 状态、100% 流量和 expected epoch 生成候选；表面 serving 还必须由事故前 promote/reconcile 证实。",
        )
        serving = [
            row
            for row in controls["result"]
            if str(row[1]) == "global"
            and str(row[2]) == "observed"
            and str(row[4]) <= incident_at
            and str(row[5]) == "serving"
            and int(row[6]) == 100
            and int(row[7]) == expected_epoch
        ]
        if not serving:
            raise RuntimeError(f"BC07 mock found no incident-boundary serving candidates: rows={serving!r}")
        bindings = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT control_key, release_id, binding_state, bound_at "
                    f"FROM {case.database}.{case.release_binding_table} ORDER BY bound_at, binding_id"
                )
            },
            thinking="把 opaque deployment control key 解析为 canonical release ID，排除 stale binding 和同一 epoch 的 shadow key。",
        )
        bound_candidates = []
        for control_row in serving:
            historical_bindings = [
                binding_row
                for binding_row in bindings["result"]
                if str(binding_row[0]) == str(control_row[3])
                and str(binding_row[3]) <= str(control_row[4])
                and str(binding_row[2]) != "revoked"
            ]
            if not historical_bindings:
                continue
            latest_bound_at = max(str(binding_row[3]) for binding_row in historical_bindings)
            selected_bindings = [
                binding_row
                for binding_row in historical_bindings
                if str(binding_row[3]) == latest_bound_at
            ]
            if len(selected_bindings) != 1:
                raise RuntimeError(
                    "BC07 mock expected one as-of binding for a control snapshot: "
                    f"control={control_row!r}, bindings={selected_bindings!r}"
                )
            bound_candidates.append((control_row, str(selected_bindings[0][1])))
        if not bound_candidates:
            raise RuntimeError(f"BC07 mock found no as-of binding for serving candidates: rows={serving!r}")
        transitions = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT release_id, transition, occurred_at, traffic_percent, control_epoch "
                    f"FROM {case.database}.{case.release_transition_table} WHERE service_name='{case.service_name}' "
                    f"AND environment='{case.environment}' AND logical_table='{case.logical_table}' "
                    "ORDER BY occurred_at, transition_id"
                )
            },
            thinking="用 rollout transition history 验证候选 release 在事故边界前完成 100% promote/reconcile，排除未来 hotfix、shadow 和 rehearsal。",
        )
        qualified_candidates = [
            (control_row, release_id)
            for control_row, release_id in bound_candidates
            if sum(
                1
                for transition in transitions["result"]
                if str(transition[0]) == release_id
                and str(transition[2]) <= incident_at
                and int(transition[4]) == expected_epoch
                and str(transition[1]) in {"promoted", "reconciled"}
            ) == 2
        ]
        if len(qualified_candidates) != 1:
            raise RuntimeError(
                "BC07 mock expected one serving candidate with two pre-incident transitions: "
                f"candidates={qualified_candidates!r}"
            )
        serving, active_release_id = qualified_candidates[0]
        if active_release_id != case.target_release_id:
            raise RuntimeError(
                f"BC07 mock observed unexpected last-known-good release: {active_release_id!r}"
            )
        registry = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT release_id, table_id, lifecycle_state, generation, expected_rows, "
                    "expected_event_id_sum, expected_crc, effective_at, change_ticket "
                    f"FROM {case.database}.{case.release_registry_table} "
                    "ORDER BY effective_at"
                )
            },
            thinking="将事故边界 release 映射到物理 TABLE_ID，并与多个完整但未在事故时 serving 的同名版本区分开。",
        )
        active_registry = [row for row in registry["result"] if str(row[0]) == active_release_id]
        if len(active_registry) != 1:
            raise RuntimeError(f"BC07 mock expected one active registry row: rows={active_registry!r}")
        target_table_id = int(active_registry[0][1])
        expected_truth = tuple(int(value) for value in active_registry[0][4:7])
        if expected_truth != (case.source_row_count, case.expected_event_id_sum, case.expected_crc):
            raise RuntimeError(f"BC07 mock active release truth mismatch: truth={expected_truth!r}")
        ledger = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT release_id, order_count, event_id_sum, crc "
                    f"FROM {case.database}.{case.release_ledger_table} ORDER BY release_id"
                )
            },
            thinking="用业务账本复核 registry 的业务真值，避免把物理上完整但不属于事故边界的版本恢复成线上版本。",
        )
        active_ledger = [row for row in ledger["result"] if str(row[0]) == active_release_id]
        if len(active_ledger) != 1 or tuple(int(value) for value in active_ledger[0][1:]) != expected_truth:
            raise RuntimeError(f"BC07 mock active ledger mismatch: rows={active_ledger!r}")
        history = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT JOB_ID, TABLE_NAME, JOB_TYPE, STATE, TABLE_ID "
                    f"FROM information_schema.ddl_jobs WHERE DB_NAME='{case.database}' "
                    f"AND TABLE_NAME='{case.table}' ORDER BY JOB_ID"
                )
            },
            thinking="在分页噪声和多代同名 DROP 中，用 incident-boundary release 的 TABLE_ID 精确关联目标 DROP，而不是选最早或最新 job。",
        )
        drop_jobs = [
            int(row[0])
            for row in history["result"]
            if str(row[2]).casefold() == "drop table" and int(row[4]) == target_table_id
        ]
        if len(drop_jobs) != 1:
            raise RuntimeError(f"BC07 mock expected one active-release DROP job, observed={drop_jobs!r}")
        target_drop_job_id = drop_jobs[0]
        self.execute(
            "execute_sql",
            {"sql_query": "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY FROM information_schema.cluster_statements_summary ORDER BY SUM_LATENCY DESC LIMIT 50"},
            thinking="把业务错误和 schema registry/归档查询等真实 profile 分开。",
        )
        self.execute(
            "read_log",
            {"target": "tidb/tidb-0", "lines": 240},
            thinking="确认错误来自目标表不存在，而不是节点重启或存储故障。",
        )
        knowledge_result = self.execute(
            "search_knowledge",
            {
                "query": "TiDB RECOVER TABLE BY JOB exact DDL job DROP TABLE GC lifetime",
                "source_scope": "self_managed",
                "top_k": 5,
            },
            thinking="核对 RECOVER TABLE BY JOB 对同名多次删除和 GC safe point 的语义。",
        )
        if knowledge_result["status"] != "success":
            raise RuntimeError(
                "BC07 mock knowledge lookup failed before recovery: "
                f"result={knowledge_result!r}"
            )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT VARIABLE_NAME, VARIABLE_VALUE FROM mysql.tidb "
                    "WHERE VARIABLE_NAME IN ('tikv_gc_safe_point','tikv_gc_last_run_time')"
                )
            },
            thinking="确认临时 GC 窗口仍在，先恢复事故边界 release 的 DDL job，再做业务真值验收。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"RECOVER TABLE BY JOB {target_drop_job_id}"},
            thinking="恢复生产 active release 对应的精确 DROP，不恢复其他完整但已回滚的同名版本。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT COUNT(*), COALESCE(SUM(event_id),0), "
                    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#',event_id,tenant_id,event_type,amount_cents,payload))),0) "
                    f"FROM {case.database}.{case.table}"
                )
            },
            thinking="验证业务行数、主键编号范围和 CRC，而不是只看表重新出现。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT COUNT(*), COUNT(DISTINCT event_id), MIN(event_id), MAX(event_id) "
                    f"FROM {case.database}.{case.table}"
                )
            },
            thinking="确认恢复的是原始主键空间，不是 17 行同名 decoy。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"ADMIN CHECK TABLE {case.database}.{case.table}"},
            thinking="执行 TiDB 的最终表和索引一致性检查。",
        )
        baseline_result = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT previous_value FROM {case.database}.{case.audit_table} "
                    "WHERE action='gc-lifetime-override' AND config_key='tidb_gc_life_time' "
                    f"AND requested_value='{case.recovery_gc_lifetime}' AND created_at < '" + incident_at + "' "
                    "ORDER BY audit_id"
                )
            },
            thinking="从发布审计记录读取注入前的 GC baseline，再精确恢复它。",
        )
        baseline = str(baseline_result["result"][0][0])
        self.execute(
            "execute_sql",
            {"sql_query": f"SET GLOBAL tidb_gc_life_time='{baseline}'"},
            thinking="恢复 injector 交接前的 GC 保留窗口，避免把临时应急配置留在集群。",
        )
        return _report(case)


def main() -> None:
    scenario = SCENARIO
    parser = argparse.ArgumentParser(
        description="Run the TiDB BC07 exact DROP-job table recovery scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=32)
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--container-name", default="tidb-business-change-table-recovery")
    parser.add_argument("--tidb-readiness-timeout-seconds", type=int, default=1800)
    parser.add_argument(
        "--fault-snapshot-mode",
        choices=("auto", "off", "save", "use"),
        default="off",
    )
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    run_id = args.container_name.removeprefix("aiopsbench-")
    env = TiDBEnv(
        run_id=run_id,
        port_base=args.port,
        tidb_readiness_timeout_sec=args.tidb_readiness_timeout_seconds,
    )
    if args.mode == "mock":
        agent = TidbBusinessChangeTableRecoveryFullMockAgent(case)
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode),
    ).run()
    if args.mode == "mock" and (
        result["DiagnosisPass"] is not None
        or result["OutcomePass"] is not True
        or result["SafePass"] is not True
    ):
        raise RuntimeError(f"BC07 mock full-pass contract failed: result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
