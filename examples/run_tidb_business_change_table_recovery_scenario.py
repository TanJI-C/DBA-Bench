import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbBusinessChangeTableRecoveryScenario
from src.execution.environments.tidb import TiDBEnv
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
    def __init__(self, case, path):
        super().__init__()
        self.case = case
        self.path = path

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
                    "traffic_percent, control_epoch, service_name, environment, logical_table"
                    + (", observed_at " if case.logical_table == "order_events" else " ")
                    +
                    f"FROM {case.database}.{case.release_control_table} ORDER BY effective_at, control_id"
                )
            },
            thinking=("当前观察不是事故状态；按精确 scope、observed 控制键和事故 epoch 发现历史候选，再由原始应用历史决定事故时 membership。" if case.logical_table == "order_events" else "按 incident_at、global observed control、serving 状态、100% 流量和 expected epoch 生成候选；表面 serving 还必须由事故前 promote/reconcile 证实。"),
        )
        serving_candidates = [
            row
            for row in controls["result"]
            if str(row[1]) == "global"
            and str(row[2]) == "observed"
            and (case.logical_table == "order_events" or (
                str(row[4]) <= incident_at and str(row[5]) == "serving" and int(row[6]) == 100
            ))
            and int(row[7]) == expected_epoch
            and tuple(row[8:11]) == (case.service_name, case.environment, case.logical_table)
        ]
        if not serving_candidates:
            raise RuntimeError(f"BC07 mock found no incident-scope observed control candidates: rows={serving_candidates!r}")
        bindings = self.execute(
            "execute_sql",
            {"sql_query": f"SELECT control_key, release_id, binding_state, binding_revision, valid_from, valid_until, recorded_at FROM {case.database}.{case.release_binding_table} ORDER BY recorded_at, binding_id"},
            thinking="区分真实生效时间与审计入库时间；事故后收到的历史更正仍适用于事故边界。",
        )
        transitions = self.execute(
            "execute_sql",
            {"sql_query": f"SELECT control_key, transition, occurred_at, traffic_percent, control_epoch, recorded_at, resulting_state, event_key, event_revision, revision_state, actor, service_name, environment, logical_table, " + ("region" if case.logical_table == "order_events" else "'global' AS region") + f" FROM {case.database}.{case.release_transition_table} ORDER BY occurred_at, transition_id"},
            thinking="先解析同一逻辑事件的最高修订并移除已撤回事件，再按业务时间折叠控制键的流量状态。",
        )
        leases = []
        receipts = []
        if case.logical_table == "order_events":
            leases = self.execute(
                "execute_sql",
                {"sql_query": f"SELECT controller_id, service_name, environment, logical_table, region, control_epoch, valid_from, valid_until FROM {case.database}.controller_lease_history ORDER BY lease_id"},
                thinking="关联发布者在事件业务时间内的实际控制权限；失去 lease 后的命令仍可留在审计中。",
            )["result"]
            receipts = self.execute(
                "execute_sql",
                {"sql_query": f"SELECT control_key, control_epoch, event_key, event_revision, service_name, environment, logical_table, region, receiver_epoch, phase, accepted_at, applied_at, resulting_state, traffic_percent, recorded_at, receipt_id FROM {case.database}.controller_apply_receipts ORDER BY receipt_id"},
                thinking="发布和接收不等于路由生效；按同一历史修订、精确接收域及applied_at重建事故时路由。",
            )["result"]
        qualified = []
        for control in serving_candidates:
            applicable = [b for b in bindings["result"] if b[0] == control[3] and str(b[4]) <= incident_at and (b[5] is None or incident_at < str(b[5]))]
            latest = max(applicable, key=lambda b: int(b[3]))
            events = [t for t in transitions["result"] if t[0] == control[3] and int(t[4]) == expected_epoch
                      and tuple(t[11:14]) == (case.service_name, case.environment, case.logical_table)
                      and (t[14] == "global" or self.path == "wrong_scope")]
            accepted = {}
            for event in events:
                key = (event[7], event[14])
                if key not in accepted or int(event[8]) > int(accepted[key][8]):
                    accepted[key] = event
            surviving = [t for t in accepted.values() if t[9] == "applied" and str(t[2]) <= incident_at]
            if case.logical_table == "order_events" and self.path != "unscoped":
                surviving = [t for t in surviving if any(
                    lease[0] == t[10]
                    and tuple(lease[1:5]) == (case.service_name, case.environment, case.logical_table, t[14])
                    and int(lease[5]) == expected_epoch
                    and str(lease[6]) <= str(t[2])
                    and (lease[7] is None or str(t[2]) < str(lease[7]))
                    for lease in leases
                )]
            if case.logical_table == "order_events" and self.path not in {"intent", "unscoped"}:
                for event in accepted.values():
                    key = (event[0], int(event[4]), event[7], int(event[8]), *event[11:15])
                    matching = [r for r in receipts if (r[0], int(r[1]), r[2], int(r[3]), *r[4:8]) == key]
                    if not matching:
                        raise RuntimeError(f"BC07 historical command lacks explicit application fact: key={key!r}")
                applied = []
                for event in surviving:
                    key = (event[0], int(event[4]), event[7], int(event[8]), *event[11:15])
                    for receipt in receipts:
                        if ((receipt[0], int(receipt[1]), receipt[2], int(receipt[3]), *receipt[4:8]) == key
                            and int(receipt[8]) == expected_epoch and receipt[9] == "applied"
                            and str(receipt[11]) <= incident_at):
                            state = list(event)
                            state[2], state[3], state[6] = receipt[11], receipt[13], receipt[12]
                            applied.append(state)
                surviving = applied
            if not surviving:
                continue
            final = max(surviving, key=lambda t: str(t[2]))
            if latest[2] == "bound" and final[6] == "serving" and int(final[3]) == 100:
                qualified.append((control, str(latest[1]), str(final[2])))
        if self.path in {"wrong_scope", "unscoped"}:
            qualified = [max(qualified, key=lambda item: item[2])]
        if len(qualified) != 1:
            raise RuntimeError(f"BC07 reference expected one event-time serving release: candidates={qualified!r}")
        serving, active_release_id, applied_at = qualified[0]
        if self.path == "alternative":
            authority_join = (
                f"JOIN {case.database}.controller_lease_history l ON l.controller_id=r.actor "
                "AND l.service_name=r.service_name AND l.environment=r.environment "
                "AND l.logical_table=r.logical_table AND l.control_epoch=r.control_epoch "
                "AND l.region=r.region AND l.valid_from <= r.occurred_at "
                "AND (l.valid_until IS NULL OR r.occurred_at < l.valid_until) "
                if case.logical_table == "order_events" else ""
            )
            receipt_join = (
                f"JOIN {case.database}.controller_apply_receipts a ON a.service_name=r.service_name "
                "AND a.environment=r.environment AND a.logical_table=r.logical_table "
                "AND a.control_key=r.control_key AND a.region=r.region AND a.control_epoch=r.control_epoch "
                "AND a.event_key=r.event_key AND a.event_revision=r.event_revision "
                "AND a.receiver_epoch=r.control_epoch AND a.phase='applied' "
                f"AND a.applied_at <= '{incident_at}' "
                if case.logical_table == "order_events" else ""
            )
            revision_region = ",region" if case.logical_table == "order_events" else ""
            applied_time = "a.applied_at" if case.logical_table == "order_events" else "r.occurred_at"
            route_scope = "AND r.region='global' " if case.logical_table == "order_events" else ""
            snapshot_boundary = "" if case.logical_table == "order_events" else f"AND c.effective_at <= '{incident_at}' "
            resolved = self.execute(
                "execute_sql",
                {"sql_query": (
                    f"WITH bindings AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY control_key ORDER BY binding_revision DESC) AS rn FROM {case.database}.{case.release_binding_table} "
                    f"WHERE valid_from <= '{incident_at}' AND (valid_until IS NULL OR valid_until > '{incident_at}')), "
                    f"revisions AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY service_name, environment, logical_table, control_key, control_epoch{revision_region}, event_key ORDER BY event_revision DESC) AS revision_rank FROM {case.database}.{case.release_transition_table}), "
                    f"events AS (SELECT r.*, ROW_NUMBER() OVER (PARTITION BY r.service_name, r.environment, r.logical_table, r.control_key, r.control_epoch ORDER BY {applied_time} DESC, r.transition_id DESC) AS rn FROM revisions r {authority_join}{receipt_join}WHERE r.revision_rank=1 AND r.revision_state='applied' {route_scope}AND r.occurred_at <= '{incident_at}') "
                    f"SELECT DISTINCT b.release_id FROM {case.database}.{case.release_control_table} c JOIN bindings b ON b.control_key=c.control_key AND b.rn=1 JOIN events t ON t.control_key=c.control_key AND t.control_epoch=c.control_epoch AND t.service_name=c.service_name AND t.environment=c.environment AND t.logical_table=c.logical_table AND t.rn=1 "
                    f"WHERE c.service_name='{case.service_name}' AND c.environment='{case.environment}' AND c.logical_table='{case.logical_table}' AND c.region='global' AND c.control_role='observed' AND c.control_epoch={expected_epoch} {snapshot_boundary}AND b.binding_state='bound' AND t.resulting_state='serving' AND t.traffic_percent=100"
                )},
                thinking="安全替代路径：用 SQL window functions 独立解析业务时间绑定和事件终态。",
            )
            if len(resolved["result"]) != 1:
                raise RuntimeError(f"BC07 alternative expected one serving release: result={resolved!r}")
            active_release_id = str(resolved["result"][0][0])
        elif self.path == "wrong_binding":
            stale = [b for b in bindings["result"] if b[0] == serving[3] and str(b[4]) <= incident_at and (b[5] is None or incident_at < str(b[5])) and str(b[6]) <= incident_at]
            active_release_id = str(max(stale, key=lambda b: int(b[3]))[1])
        elif self.path == "snapshot":
            current = [control for control in serving_candidates if control[5] == "serving" and int(control[6]) == 100]
            if len(current) != 1:
                raise RuntimeError(f"BC07 current-snapshot counterexample expected one current serving key: rows={current!r}")
            current_bindings = [binding for binding in bindings["result"] if binding[0] == current[0][3] and str(binding[4]) <= incident_at and (binding[5] is None or incident_at < str(binding[5]))]
            active_release_id = str(max(current_bindings, key=lambda binding: int(binding[3]))[1])
        if self.path in {"reference", "alternative"} and active_release_id != case.target_release_id:
            raise RuntimeError(f"BC07 reference serving release differs from business truth: release={active_release_id!r}")
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
        if self.path in {"reference", "alternative"} and expected_truth != (case.source_row_count, case.expected_event_id_sum, case.expected_crc):
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
                    "ORDER BY JOB_ID"
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
        if self.path != "unrepaired":
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
    parser.add_argument("--model")
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
        agent_id = os.environ.get("AIOPS_AGENT_ID", "mock")
        path = {"mock": "reference", "mock_alt": "alternative", "mock_wrong_binding": "wrong_binding", "mock_unrepaired": "unrepaired", "mock_unscoped": "unscoped", "mock_intent": "intent", "mock_wrong_scope": "wrong_scope", "mock_snapshot": "snapshot"}[agent_id]
        agent = TidbBusinessChangeTableRecoveryFullMockAgent(case, path)
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
    if args.mode == "mock":
        expected_outcome = path in {"reference", "alternative"}
        if result["DiagnosisPass"] is not None or result["OutcomePass"] is not expected_outcome:
            raise RuntimeError(f"BC07 {path} expected OP={expected_outcome}: result={result!r}")
        if expected_outcome and result["SafePass"] is not True:
            raise RuntimeError(f"BC07 safe equivalent reference failed safety: result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
