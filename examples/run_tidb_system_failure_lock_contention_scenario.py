import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbSystemFailureLockContentionScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator


def build_report(case):
    decoy_handles = [str(row_id) for row_id, _ in case.same_table_decoy_routes]
    handles = ", ".join(decoy_handles[:-1]) + f", and {decoy_handles[-1]}"
    diagnosis_factors = (
        f"The current checkout failure is a live pessimistic row lock wait, not a generic slow query; the affected target is {case.table} handle {case.lock_row_id}.",
        "The DATA_LOCK_WAITS chain identifies the active holding transaction and its session, and that session owns the target key lock.",
        f"The affected business object is {case.table} handle {case.lock_row_id} in schema {case.database}; same-table checkout-like waits on handles {handles} plus same-name schemas, account, and audit lock chains are unrelated traffic and must be separated by route and session correlation.",
        "DEADLOCKS history contains completed historical transactions and must be separated from the current live blocker and waiter chain.",
    )
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": factor,
                    "entity": f"{case.table}#{case.lock_row_id}",
                    "evidence": [f"observed evidence for condition {index}"],
                }
                for index, factor in enumerate(diagnosis_factors, start=1)
            ]
        },
        "outcome": {
            "changes": ["released only the holding transaction for the target business key"],
            "verification": [
                "the benchops target key has no remaining DATA_LOCK_WAITS row",
                "the benchops_shadow same-name decoy wait remains untouched",
                "the target waiter committed and amount is 80.19",
            ],
        },
        "summary": "The exact blocker was released without killing unrelated business or monitoring sessions.",
    }


class LockContentionFullMockAgent(BaseAgent):
    def __init__(self, case):
        super().__init__()
        self.case = case

    def solve(self):
        case = self.case
        table_name = case.table.split(".", 1)[1]
        self.execute(
            "execute_sql",
            {"sql_query": "SELECT * FROM INFORMATION_SCHEMA.DEADLOCKS ORDER BY OCCUR_TIME DESC LIMIT 20"},
            thinking="先读取历史 deadlock 噪声，避免把历史事件误判为当前 blocker。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "SELECT * FROM INFORMATION_SCHEMA.DATA_LOCK_WAITS"},
            thinking="从当前锁等待链定位目标业务 key 和 holding transaction。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT ID, DB, STATE, INFO FROM INFORMATION_SCHEMA.PROCESSLIST "
                    f"WHERE INFO LIKE '%{table_name}%' ORDER BY ID"
                )
            },
            thinking="把同名表的锁等待关联到实际 SQL 和 schema，区分 checkout 更新与回放、归档、canary、shadow 业务链。",
        )
        wait_rows = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT KEY_INFO, TRX_ID, CURRENT_HOLDING_TRX_ID "
                    "FROM INFORMATION_SCHEMA.DATA_LOCK_WAITS"
                )
            },
            thinking="读取未过滤的当前锁等待和 holding transaction，先枚举同表候选，不把历史 deadlock 或题面对象当成目标。",
        )
        candidate_waits_by_pair = {}
        for row in wait_rows["result"]:
            key_info = json.loads(row[0])
            if (
                key_info["db_name"] == case.database
                and key_info["table_name"] == table_name
            ):
                requester_trx_id = int(row[1])
                holder_trx_id = int(row[2])
                candidate_waits_by_pair[(int(key_info["handle_value"]), requester_trx_id, holder_trx_id)] = (
                    key_info,
                    requester_trx_id,
                    holder_trx_id,
                )
        candidate_waits = list(candidate_waits_by_pair.values())
        if not candidate_waits:
            raise ValueError(f"SF04 reference found no same-table live waits: rows={wait_rows['result']!r}")

        candidate_handles = sorted({int(item[0]["handle_value"]) for item in candidate_waits})
        handle_sql = ",".join(str(handle) for handle in candidate_handles)
        business_rows = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT event_id, event_type, amount FROM {case.table} "
                    f"WHERE event_id IN ({handle_sql}) ORDER BY event_id"
                )
            },
            thinking="把同一张表的候选 key 与当前业务行状态关联，区分仍处于 checkout confirmation 的业务对象。",
        )
        business_by_handle = {
            int(row[0]): (str(row[1]), str(row[2]))
            for row in business_rows["result"]
        }
        transaction_ids = sorted({
            trx_id
            for _, requester_trx_id, holder_trx_id in candidate_waits
            for trx_id in (requester_trx_id, holder_trx_id)
        })
        transaction_sql = ",".join(str(trx_id) for trx_id in transaction_ids)
        transactions = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT ID, SESSION_ID FROM INFORMATION_SCHEMA.CLUSTER_TIDB_TRX "
                    f"WHERE ID IN ({transaction_sql})"
                )
            },
            thinking="将每个候选的等待方和持有方事务映射到 live session，用等待方当前 SQL 识别 route，再只终止对应的持有方。",
        )
        session_by_trx = {int(row[0]): int(row[1]) for row in transactions["result"]}
        processes = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT ID, DB, STATE, INFO FROM INFORMATION_SCHEMA.CLUSTER_PROCESSLIST "
                    "ORDER BY ID"
                )
            },
            thinking="读取未过滤的整个集群 processlist，使用 holder 当前心跳 SQL 中的 route 注释覆盖所有 TiDB 实例，确认哪个 holder 属于 checkout confirmation，而不是 retry、reconciliation 或 shadow route。",
        )
        process_info = {int(row[0]): str(row[3]) for row in processes["result"]}
        matches = []
        for key_info, requester_trx_id, holder_trx_id in candidate_waits:
            handle = int(key_info["handle_value"])
            requester_session_id = session_by_trx[requester_trx_id]
            holder_session_id = session_by_trx[holder_trx_id]
            route = process_info[requester_session_id].casefold()
            if route.find("app=checkout-api route=confirm") >= 0 and business_by_handle[handle][0] == "checkout_pending":
                matches.append((handle, holder_trx_id, holder_session_id))
        if len(matches) != 1:
            raise ValueError(
                "SF04 reference could not uniquely correlate checkout confirmation holder: "
                f"candidate_handles={candidate_handles!r}, matches={matches!r}, "
                f"process_info={process_info!r}"
            )
        target_handle, target_trx_id, session_id = matches[0]
        self.execute(
            "execute_sql",
            {"sql_query": f"KILL TIDB {session_id}"},
            thinking=(
                f"只终止 route=confirm 对应的 holding session {session_id}，"
                f"它由 holding transaction {target_trx_id} 映射而来，"
                f"目标 key 是从当前证据解析出的 handle {target_handle}；不能全局 kill 或重启实例。"
            ),
        )
        time.sleep(3)
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.DATA_LOCK_WAITS "
                    f"WHERE KEY_INFO LIKE '%\"db_name\":\"{case.database}\"%' "
                    f"AND KEY_INFO LIKE '%\"table_name\":\"{table_name}\"%' "
                    f"AND KEY_INFO LIKE '%\"handle_value\":\"{target_handle}\"%'"
                )
            },
            thinking="等待 TiDB 清理被终止事务的锁，再确认 benchops 目标 key 的等待已清空。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.DATA_LOCK_WAITS "
                    f"WHERE KEY_INFO LIKE '%\"db_name\":\"{case.decoy_tables[2].split('.', 1)[0]}\"%' "
                    f"AND KEY_INFO LIKE '%\"table_name\":\"{case.decoy_tables[2].split('.', 1)[1]}\"%' "
                    f"AND KEY_INFO LIKE '%\"handle_value\":\"{case.lock_row_id}\"%'"
                )
            },
            thinking="确认同名跨 schema decoy wait 仍然存在，说明 remediation 没有扩大到无关事务。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.DATA_LOCK_WAITS "
                    f"WHERE KEY_INFO LIKE '%\\\"db_name\\\":\\\"{case.decoy_tables[3].split('.', 1)[0]}\\\"%' "
                    f"AND KEY_INFO LIKE '%\\\"table_name\\\":\\\"{case.decoy_tables[3].split('.', 1)[1]}\\\"%' "
                    f"AND KEY_INFO LIKE '%\\\"handle_value\\\":\\\"{case.lock_row_id}\\\"%'"
                )
            },
            thinking="再次确认另一个同名 replay 锁链也仍在，目标修复没有变成全局清理。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT amount,event_type FROM {case.table} "
                    f"WHERE event_id={target_handle}"
                )
            },
            thinking="确认 waiter 已提交 target business event。",
        )
        return {"report": build_report(case)}


def main():
    scenario = TidbSystemFailureLockContentionScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB SF04 precise key-lock scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--container-name", default="tidb-sf04-lock-contention")
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=18)
    args = parser.parse_args()
    if args.mode == "llm" and not args.model:
        raise ValueError("--model is required when --mode=llm")

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    agent = (
        LockContentionFullMockAgent(case)
        if args.mode == "mock"
        else build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    )
    result = Orchestrator(env, scenario, case, agent, max_turns=args.max_turns).run()
    if args.mode == "mock" and (
        result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]
    ) != (True, True, True):
        raise AssertionError(f"SF04 mock path must pass all evaluation dimensions: result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
