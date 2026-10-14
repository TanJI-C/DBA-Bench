import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.tidb import TidbSystemFailureDeadlockScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


class DeadlockFullMockAgent(BaseAgent):
    def __init__(self, case):
        super().__init__()
        self.case = case

    def solve(self):
        self.execute(
            "query_metrics",
            {"metric_type": "active_connections"},
            thinking="先确认 TiDB endpoint 仍可用，区分业务现场噪声与组件不可用。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT DEADLOCK_ID, OCCUR_TIME, RETRYABLE, TRY_LOCK_TRX_ID, "
                    "CURRENT_SQL_DIGEST_TEXT, KEY_INFO, TRX_HOLDING_LOCK "
                    "FROM information_schema.deadlocks "
                        "ORDER BY occur_time DESC, deadlock_id DESC"
                )
            },
            thinking="读取未过滤的 TiDB deadlock history，按时间、锁 key 和事务关系区分多个同域 1213 事件。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT batch_id, worker_id, first_account_id, second_account_id, error_code, "
                    "final_state, observed_at "
                    "FROM sf05_transfer_attempts "
                        "ORDER BY observed_at DESC, attempt_id DESC"
                )
            },
            thinking="把 deadlock row 的账户 pair 与业务 attempt、错误历史和 observed_at 关联，识别当前候选而不是只看 1213。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT batch_id, from_account_id, to_account_id, amount, status, "
                    "lock_order, retry_strategy, updated_at "
                    "FROM sf05_transfer_jobs ORDER BY updated_at DESC, batch_id"
                )
            },
            thinking="检查所有 retry job 的状态和更新时间，保留 nearby batch 的 manual_review、settled 与其他队列状态。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT receipt_id, batch_id, from_account_id, to_account_id, amount, receipt_state, observed_at "
                    "FROM sf05_settlement_receipts ORDER BY observed_at DESC, receipt_id"
                )
            },
            thinking="把用户可见的结算回执状态与同一账户对的多个 batch 关联，找出真正仍未完成的业务事件。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT reconciliation_id, batch_id, from_account_id, to_account_id, amount, "
                    "control_state, source, observed_at "
                    "FROM sf05_settlement_reconciliation ORDER BY observed_at DESC, reconciliation_id"
                )
            },
            thinking="把结算控制记录与相似的当前 job、receipt、attempt 关联，确认 open reconciliation 项而不是 duplicate_hold 事件。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT dispatch_id, incident_key, batch_id, from_account_id, to_account_id, amount, "
                    "dispatch_state, route, observed_at "
                    "FROM sf05_settlement_dispatch ORDER BY observed_at DESC, dispatch_id"
                )
            },
            thinking="读取 settlement dispatch 原始状态，确认 customer incident 与 suppressed replay 的授权范围。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT ledger_entry_id, batch_id, account_id, leg_type, amount, entry_state, "
                    "ledger_reference, observed_at "
                    "FROM sf05_settlement_ledger ORDER BY observed_at DESC, ledger_entry_id"
                )
            },
            thinking="读取业务 ledger，确认 101 debit 已落账，只补 202 pending credit，避免重复扣款。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT account_id, customer_id, lock_group, balance, updated_at "
                    "FROM sf05_accounts ORDER BY account_id"
                )
            },
            thinking="把 deadlock 的 KEY_INFO handle 与业务账户、lock_group 和当前余额对应起来。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": "SELECT count(*) FROM information_schema.data_lock_waits",
            },
            thinking="确认死锁 victim 已回滚，当前没有需要终止的持久 blocker。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "START TRANSACTION; "
                    "SELECT account_id, balance FROM sf05_accounts "
                    "WHERE account_id IN (101, 202) ORDER BY account_id FOR UPDATE; "
                    "UPDATE sf05_accounts SET balance = CASE account_id "
                    "WHEN 202 THEN balance + 70 ELSE balance END "
                    "WHERE account_id = 202 AND EXISTS ("
                    "SELECT 1 FROM sf05_settlement_ledger "
                    "WHERE batch_id = 'settlement-20260808-042' AND account_id = 202 "
                    "AND leg_type = 'credit' AND entry_state = 'pending' AND amount = 70"
                    "); "
                    "UPDATE sf05_settlement_ledger SET entry_state = 'applied', observed_at = CURRENT_TIMESTAMP "
                    "WHERE batch_id = 'settlement-20260808-042' AND account_id = 202 "
                    "AND leg_type = 'credit' AND entry_state = 'pending' AND amount = 70; "
                    "UPDATE sf05_transfer_jobs "
                    "SET status = 'settled', retry_strategy = 'ordered_retry', updated_at = CURRENT_TIMESTAMP "
                    "WHERE batch_id = 'settlement-20260808-042' AND status = 'needs_retry'; "
                    "UPDATE sf05_settlement_receipts "
                    "SET receipt_state = 'delivered', observed_at = CURRENT_TIMESTAMP "
                    "WHERE batch_id = 'settlement-20260808-042' AND receipt_state = 'pending'; "
                    "UPDATE sf05_settlement_reconciliation "
                    "SET control_state = 'closed', source = 'ops-recovery', observed_at = CURRENT_TIMESTAMP "
                    "WHERE batch_id = 'settlement-20260808-042' AND control_state = 'open'; "
                    "UPDATE sf05_settlement_dispatch "
                    "SET dispatch_state = 'closed', observed_at = CURRENT_TIMESTAMP "
                    "WHERE batch_id = 'settlement-20260808-042' AND dispatch_state = 'active_customer_incident'; "
                    "COMMIT;"
                )
            },
            thinking="按稳定主键顺序锁定账户后重试失败批次，确保两笔更新一起提交。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT account_id, balance FROM sf05_accounts "
                    "WHERE account_id IN (101, 202) ORDER BY account_id"
                )
            },
            thinking="复核目标两行已落账。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT batch_id, status, retry_strategy FROM sf05_transfer_jobs "
                    "ORDER BY batch_id"
                )
            },
            thinking="确认目标 job 完成，同时所有 decoy job 的状态和 retry strategy 保持原样。",
        )
        return {"report": self.case.reference_report}


class DeadlockZeroMockAgent(BaseAgent):
    def solve(self):
        return {"report": EMPTY_REPORT}


def main():
    scenario = TidbSystemFailureDeadlockScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB SF05 deadlock scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--port", type=int, default=4600)
    parser.add_argument("--container-name", default="tidb-system-failure-sf05")
    parser.add_argument("--mode", choices=("mock", "zero", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--llm-config", "--config-path", dest="config_path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=16)
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    if args.mode == "mock":
        agent = DeadlockFullMockAgent(case)
    elif args.mode == "zero":
        agent = DeadlockZeroMockAgent()
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode="off",
        diagnosis_match_mode="semantic" if args.mode == "llm" else "exact",
        diagnosis_semantic_model=args.model,
        diagnosis_semantic_config_path=args.config_path,
    )
    Orchestrator(env, scenario, case, agent, max_turns=args.max_turns, run_config=run_config).run()


if __name__ == "__main__":
    main()
