import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbSystemFailureMdlBlockingScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator


class MdlBlockingFullMockAgent(BaseAgent):
    """Deterministic DBA path that still discovers the session ID from TiDB."""

    def __init__(self, case):
        super().__init__()
        self.case = case

    def solve(self):
        self.execute(
            "execute_sql",
            {"sql_query": "ADMIN SHOW DDL JOBS"},
            thinking="先确认是否是存储层 DDL worker 或普通 DDL job 队列问题。",
        )
        mdl_sql = (
            "SELECT m.job_id, t.session_id, t.start_time, t.current_sql_digest_text, t.related_table_ids "
            "FROM mysql.tidb_mdl_info AS m "
            "JOIN information_schema.cluster_tidb_trx AS t "
            "ON CONCAT(',', m.table_ids, ',') REGEXP "
            "CONCAT(',(', REPLACE(t.related_table_ids, ',', '|'), '),') "
            "AND t.related_table_ids = m.table_ids "
            "JOIN information_schema.ddl_jobs AS d "
            "ON d.job_id = m.job_id AND t.start_time <= d.start_time "
            f"WHERE m.table_ids = (SELECT TIDB_TABLE_ID FROM information_schema.tables "
            f"WHERE TABLE_SCHEMA = '{self.case.database}' AND TABLE_NAME = '{self.case.table}') "
            "ORDER BY t.start_time"
        )
        for stage in range(self.case.release_stage_count):
            mdl = None
            for _ in range(12):
                mdl = self.execute(
                    "execute_sql",
                    {"sql_query": mdl_sql},
                    thinking=(
                        "绕开 v8.1 无效的 tidb_mdl_view，直接把 MDL job 和事务表按 table id 关联。"
                        if stage == 0
                        else "第一阶段已释放，重新检查 release chain 是否出现新的同表 MDL blocker。"
                    ),
                )
                if mdl["result"]:
                    break
                self.execute(
                    "execute_sql",
                    {"sql_query": "SELECT SLEEP(1)"},
                    thinking="等待串行 release DDL 的下一阶段进入可观测状态。",
                )
            holder_session_ids = sorted({int(row[1]) for row in mdl["result"]})
            if len(holder_session_ids) < 1:
                raise RuntimeError(
                    f"MDL blocking mock expected release-chain MDL blockers: stage={stage}, rows={mdl['result']!r}"
                )
            for holder_session_id in holder_session_ids:
                self.execute(
                    "execute_sql",
                    {"sql_query": f"KILL TIDB {holder_session_id}"},
                    thinking="只结束关联结果中精确持有目标表 MDL 的 blocker。",
                )
            if stage in (1, 2):
                self.execute(
                    "execute_sql",
                    {"sql_query": "SELECT SLEEP(2)"},
                    thinking="等待第二个 DDL job 完成并让 evaluator 观察到完整 release chain。",
                )
        return {"report": self.case.reference_report}


def main():
    scenario = TidbSystemFailureMdlBlockingScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB MDL blocking MDL-blocking scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--port", type=int, default=6420)
    parser.add_argument("--container-name", default="aiopsbench-tidb-mdl-blocking")
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    if args.mode == "mock":
        agent = MdlBlockingFullMockAgent(case)
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    result = Orchestrator(env, scenario, case, agent, max_turns=args.max_turns).run()
    print(f"Final result: {result}")
    if args.mode == "mock" and (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) != (
        True,
        True,
        True,
    ):
        raise RuntimeError(f"MDL blocking mock must pass all dimensions: result={result!r}")


if __name__ == "__main__":
    main()
