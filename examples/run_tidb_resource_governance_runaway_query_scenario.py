import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb.resource_governance import (
    TidbResourceGovernanceRunawayQueryScenario,
)
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


RG02_PASS_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": [
            "activated a finite ACTION=KILL runaway policy for the customer-insights report resource group",
            "left the protected monthly-close resource group unchanged",
        ],
        "verification": [
            "target report SQL appears in mysql.tidb_runaway_queries with action=kill",
            "all 1,200 monthly-close rows have processed_at",
            "no monthly-close runaway kill record exists",
        ],
    },
    "summary": "The runaway report is governed by its own resource-group policy while the protected monthly-close batch completes.",
}


class RG02FullMockAgent(BaseAgent):
    def __init__(self, case):
        super().__init__()
        self.case = case

    def solve(self):
        if self.case.case_no == 1:
            return self._solve_compressed_export_governance()
        self.execute(
            "execute_sql",
            {"sql_query": "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY FROM information_schema.cluster_statements_summary ORDER BY SUM_LATENCY DESC LIMIT 50"},
            thinking="把 workload fingerprint 关联到未过滤 TopSQL，区分持续长 customer aggregation、portal cooldown 噪声和 finance batch。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT NAME, RU_PER_SEC, PRIORITY, BURSTABLE, QUERY_LIMIT "
                    "FROM INFORMATION_SCHEMA.RESOURCE_GROUPS ORDER BY NAME"
                )
            },
            thinking="对照资源组边界，找到报表和 protected batch 的独立治理面。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT ID, USER, DB, COMMAND, TIME, STATE, INFO "
                    "FROM INFORMATION_SCHEMA.PROCESSLIST "
                    "WHERE INFO IS NOT NULL ORDER BY TIME DESC"
                )
            },
            thinking="观察活动会话，确认长时间执行的 SQL fingerprint。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT resource_group_name, time, match_type, action, original_sql, plan_digest, tidb_server "
                    "FROM mysql.tidb_runaway_queries ORDER BY time DESC LIMIT 50"
                )
            },
            thinking="先区分已有 portal cooldown 历史和目标 customer SQL 尚未被自动 KILL 的状态。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"ALTER RESOURCE GROUP {self.case.report_group} "
                    "QUERY_LIMIT=(EXEC_ELAPSED='1s', ACTION=KILL, WATCH=SIMILAR DURATION='10m')"
                )
            },
            thinking="用历史执行时长设置有限阈值和 KILL 动作，并把相同 SQL 模式加入短观察窗口。",
        )
        time.sleep(12)
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT resource_group_name, time, match_type, action, original_sql, plan_digest, tidb_server "
                    "FROM mysql.tidb_runaway_queries "
                    "ORDER BY time DESC LIMIT 20"
                )
            },
            thinking="确认 TiDB 记录了目标报表的自动 runaway 处置，而不是手工杀会话。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT COUNT(*), COUNT(processed_at) "
                    f"FROM {self.case.db}.{self.case.batch_table} WHERE batch_id='{self.case.batch_id}'"
                )
            },
            thinking="确认合法月结批处理完整结束。",
        )
        return {"report": self.case.reference_report}

    def _solve_compressed_export_governance(self):
        case = self.case
        self.execute(
            "execute_sql",
            {"sql_query": "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY FROM information_schema.cluster_statements_summary ORDER BY SUM_LATENCY DESC LIMIT 50"},
            thinking="从 TopSQL 直接确认持续长时运行的 customer 报表 fingerprint。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT NAME, RU_PER_SEC, PRIORITY, BURSTABLE, QUERY_LIMIT "
                    "FROM INFORMATION_SCHEMA.RESOURCE_GROUPS ORDER BY NAME"
                )
            },
            thinking="确认报表组尚无 runaway 治理而 protected export 批处理组独立。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT resource_group_name, time, match_type, action, original_sql, plan_digest, tidb_server "
                    "FROM mysql.tidb_runaway_queries ORDER BY time DESC LIMIT 50"
                )
            },
            thinking="用历史记录排除 portal cooldown 噪声，确认目标报表 SQL 尚未被自动 KILL。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"ALTER RESOURCE GROUP {case.report_group} "
                    "QUERY_LIMIT=(EXEC_ELAPSED='1s', ACTION=KILL, WATCH=SIMILAR DURATION='10m')"
                )
            },
            thinking="只对失控报表组上线有限 KILL 阈值和短观察窗口，保护 export 批处理。",
        )
        time.sleep(12)
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT resource_group_name, time, match_type, action, original_sql, plan_digest, tidb_server "
                    "FROM mysql.tidb_runaway_queries "
                    "ORDER BY time DESC LIMIT 20"
                )
            },
            thinking="确认 TiDB 自动记录并处置了目标报表，而不是手工杀会话。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT COUNT(*), COUNT(processed_at) "
                    f"FROM {case.db}.{case.batch_table} WHERE batch_id='{case.batch_id}'"
                )
            },
            thinking="确认受保护的 export 批处理完整结束。",
        )
        return {"report": case.reference_report}


def main() -> None:
    scenario = TidbResourceGovernanceRunawayQueryScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB RG02 runaway-query governance scenario."
    )
    parser.add_argument(
        "--case",
        required=True,
        choices=[case.case_id for case in scenario.cases],
    )
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--container-name", default="tidb-resource-governance-rg02")
    parser.add_argument(
        "--fault-snapshot-mode",
        choices=("auto", "off", "save", "use"),
        default="off",
    )
    args = parser.parse_args()
    if args.mode == "llm" and not args.model:
        raise ValueError("--model is required when --mode=llm")

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name,
        port_base=args.port,
        return_window_seconds=300,
    )
    agent = (
        RG02FullMockAgent(case)
        if args.mode == "mock"
        else build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    )
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
        ),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (None, True, True):
            raise RuntimeError(
                "RG02 mock must produce DP=None, OP=True, SP=True: "
                f"observed={observed!r}, result={result!r}"
            )
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
