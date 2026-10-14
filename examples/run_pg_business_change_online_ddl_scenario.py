import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.base import evaluation_passed
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import (
    PgBusinessChangeOnlineDdlCase,
    PgBusinessChangeOnlineDdlScenario,
)
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
























def build_full_score_mock_agent(case: PgBusinessChangeOnlineDdlCase):
    table = case.table
    target_column = case.target_column
    safe_retry_ddl = f"""
SET lock_timeout = '500ms';
DO $$
DECLARE
    retries integer := 0;
BEGIN
    LOOP
        BEGIN
            ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {target_column} text;
            EXIT;
        EXCEPTION WHEN lock_not_available THEN
            retries := retries + 1;
            IF retries >= 40 THEN
                RAISE;
            END IF;
            PERFORM pg_sleep(0.5);
        END;
    END LOOP;
END $$;
"""
    mock_responses = [
        {
            "thinking": "先确认当前业务负载，必须同时看 qps 和活跃连接，避免在写入高峰直接 DDL。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "qps", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "active_connections", "target": None}},
            ],
        },
        {
            "thinking": "负载仍在运行，先查看 workload 噪声和发布预检活动，避免把审计/队列噪声误判成目标变更。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "workload_activity", "target": None, "limit": 10}},
            ],
        },
        {
            "thinking": "确认目标列当前缺失，再继续确认 order_line 是大表并检查会放大 AccessExclusiveLock 风险的锁活动。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' AND column_name = '{target_column}';"}},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT c.relname, c.reltuples::bigint AS estimated_rows, pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size FROM pg_class c WHERE c.oid = '{table}'::regclass;"}},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT l.locktype, l.mode, l.granted, a.state, a.wait_event_type, a.wait_event, a.query FROM pg_locks l JOIN pg_stat_activity a ON a.pid = l.pid WHERE l.relation = '{table}'::regclass OR a.query ILIKE '%{table}%';"}},
            ],
        },
        {
            "thinking": "直接 ALTER TABLE 会申请 AccessExclusiveLock。采用短 lock_timeout + retry 的在线 DDL，拿不到锁就快速失败并重试，避免业务雪崩。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": safe_retry_ddl}},
            ],
        },
        {
            "thinking": "DDL 已执行，查询系统目录确认新增列生效。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' AND column_name = '{target_column}';"}},
            ],
        },
        {
            "thinking": "已验证结构变更生效，提交。",
            "actions": [{"api": "submit", "args": {"report": case.reference_report}}],
        },
    ]
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(mock_responses)
    return agent








def run_mode(args, scenario, case, mode, container_name, run_config):
    override_image = None
    env = PGEnv(workload=None, port=args.port, allow_sampler_jitter=True)
    env.deployment.container_name = container_name
    if override_image:
        env.deployment.image_name = override_image
    if mode == "mock":
        agent = build_full_score_mock_agent(case)
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses([{"thinking": "Submit without diagnosis.", "action": {"api": "submit", "args": {"report": EMPTY_REPORT}}}])
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    default_max_turns = {"mock": 8, "zero": 3, "llm": 8}
    max_turns = args.max_turns if args.max_turns is not None else default_max_turns[mode]
    orchestrator = Orchestrator(env, scenario, case, agent, max_turns=max_turns, run_config=run_config)
    return orchestrator.run()


def main():
    scenario = PgBusinessChangeOnlineDdlScenario()
    parser = argparse.ArgumentParser(description="Run PgBusinessChangeOnlineDdlScenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-run-pg-business-change-online-ddl-scenario")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )
    case = scenario.get_case(args.case)
    modes = ("mock", "zero", "llm") if args.mode == "all" else (args.mode,)
    for mode in modes:
        result = run_mode(
            args,
            scenario,
            case,
            mode,
            f"{args.container_name}-{case.case_id}-{mode}",
            run_config,
        )
        print(f"[{mode}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")
        if mode == "mock":
            assert evaluation_passed(result), json.dumps(result, ensure_ascii=False)
        elif mode == "zero":
            assert not evaluation_passed(result), json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    main()
