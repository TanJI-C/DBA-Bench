import argparse
import json
import os
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.base import evaluation_passed
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.scenarios.postgres import (
    PgBusinessChangeCollationConversionCase,
    PgBusinessChangeCollationConversionScenario,
)
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload




def build_mock_responses(case: PgBusinessChangeCollationConversionCase):
    table = case.table
    column = case.column
    like_index = case.like_index_name
    like_prefix = case.like_prefix
    return [
        {
            "thinking": "先确认磁盘 I/O 基线和待变更列当前 collation，避免盲目执行 DDL。",
            "actions": [
                {"api": "query_metrics", "args": {
                    "metric_type": "disk_io", "target": None}},
                {"api": "query_metrics", "args": {
                    "metric_type": "workload_activity", "target": None,
                    "limit": 10}},
                {"api": "execute_sql", "args": {"sql_query":
                    "SELECT a.attname, c.collname "
                    "FROM pg_attribute a "
                    "JOIN pg_class t ON t.oid = a.attrelid "
                    "JOIN pg_collation c ON c.oid = a.attcollation "
                    f"WHERE t.relname = '{table}' "
                    f"AND a.attname = '{column}';"}}
            ]
        },
        {
            "thinking": "评估表重写成本、空间膨胀风险和依赖该列的索引范围。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query":
                    f"SELECT pg_size_pretty(pg_total_relation_size('{table}')) AS total_size, "
                    f"pg_size_pretty(pg_relation_size('{table}')) AS heap_size, "
                    f"pg_size_pretty(pg_indexes_size('{table}')) AS index_size;"}},
                {"api": "execute_sql", "args": {"sql_query":
                    "SELECT indexname, indexdef FROM pg_indexes "
                    f"WHERE tablename = '{table}' "
                    f"AND indexdef LIKE '%{column}%';"}}
            ]
        },
        {
            "thinking": "查看 LIKE 前缀查询在当前索引下的执行计划，确认变更后需要重建模式匹配索引。",
            "action": {"api": "execute_sql", "args": {"sql_query":
                f"EXPLAIN SELECT count(*) FROM {table} "
                f"WHERE {column} LIKE '{like_prefix}';"}}
        },
        *([] if not case.preview_view_name else [
            {
                "thinking": "发布预览视图依赖目标列，直接 ALTER 会被目录依赖阻塞；先检查依赖视图并按变更流程下线视图。",
                "action": {"api": "execute_sql", "args": {"sql_query":
                    "SELECT viewname FROM pg_views "
                    f"WHERE schemaname = 'public' AND definition LIKE '%{column}%';"}},
            },
            {
                "thinking": "低峰期先 DROP 预览视图，为列级 collation 转换扫清依赖。",
                "action": {"api": "execute_sql", "args": {"sql_query":
                    f"DROP VIEW {case.preview_view_name};"}}
            },
        ]),
        {
            "thinking": "在低峰窗口执行 collation 转换，动态选择可用的区域性 collation。",
            "action": {"api": "execute_sql", "args": {"sql_query":
                "SET lock_timeout = '2s'; "
                "DO $$ "
                "DECLARE target_collation text; "
                "BEGIN "
                "  IF EXISTS (SELECT 1 FROM pg_collation WHERE collname = 'en_US.utf8') THEN "
                "    target_collation := 'en_US.utf8'; "
                "  ELSIF EXISTS (SELECT 1 FROM pg_collation WHERE collname = 'en_US.utf-8') THEN "
                "    target_collation := 'en_US.utf-8'; "
                "  ELSIF EXISTS (SELECT 1 FROM pg_collation WHERE collname = 'en_US') THEN "
                "    target_collation := 'en_US'; "
                "  ELSIF EXISTS (SELECT 1 FROM pg_collation WHERE collname = 'en-US-x-icu') THEN "
                "    target_collation := 'en-US-x-icu'; "
                "  ELSE "
                "    SELECT collname INTO target_collation "
                "    FROM pg_collation "
                "    WHERE collname NOT IN ('C', 'POSIX', 'default') "
                "    AND collname !~* '^c([._-]|$)' "
                "    AND collprovider IN ('i', 'c') "
                "    ORDER BY collname "
                "    LIMIT 1; "
                "  END IF; "
                "  IF target_collation IS NULL THEN "
                "    RAISE EXCEPTION 'No usable non-C collation found'; "
                "  END IF; "
                f"  EXECUTE format('ALTER TABLE {table} ALTER COLUMN {column} "
                f"TYPE text COLLATE %I USING {column}::text', target_collation); "
                "END $$;"}}
        },
        *([] if not case.preview_view_name else [
            {
                "thinking": "转换完成后按区域性排序语义重建发布预览视图，保持上线功能可用。",
                "action": {"api": "execute_sql", "args": {"sql_query":
                    f"CREATE VIEW {case.preview_view_name} AS "
                    f"SELECT sr_item_sk, sr_ticket_number, {column} "
                    f"FROM {table} "
                    f"ORDER BY {column};"}}
            },
        ]),
        {
            "thinking": "重建索引，并补充 text_pattern_ops 索引恢复 LIKE 前缀查询的可用执行计划。",
            "action": {"api": "execute_sql", "args": {"sql_query":
                f"CREATE INDEX CONCURRENTLY IF NOT EXISTS {like_index} "
                f"ON {table} ({column} text_pattern_ops);"}}
        },
        {
            "thinking": "验证 collation 已变更，并强制查看 LIKE 查询是否可使用修复索引。",
            "action": {"api": "execute_sql", "args": {"sql_query":
                "ANALYZE store_returns; "
                "SELECT a.attname, c.collname "
                "FROM pg_attribute a "
                "JOIN pg_class t ON t.oid = a.attrelid "
                "JOIN pg_collation c ON c.oid = a.attcollation "
                f"WHERE t.relname = '{table}' "
                f"AND a.attname = '{column}'; "
                "SET enable_seqscan = off; "
                f"EXPLAIN SELECT count(*) FROM {table} "
                f"WHERE {column} LIKE '{like_prefix}';"}}
        },
        {
            "thinking": "变更完成，表重写和索引恢复均已验证。",
            "action": {"api": "submit", "args": {"report": case.reference_report}}
        }
    ]
















def run_mode(args, scenario, case, mode, container_name, run_config):
    override_image = None
    env = PGEnv(workload=TPCDSWorkload(scale=case.dataset_scale), port=args.port, allow_sampler_jitter=True)
    env.deployment.container_name = container_name
    if override_image:
        env.deployment.image_name = override_image
    if mode == "mock":
        agent = MockLLMAgent(url='mock', api_key='mock', system_prompt='You are a DBA agent.', use_native_tools=False)
        agent.set_mock_responses(build_mock_responses(case))
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses([{"thinking": "Submit without diagnosis.", "action": {"api": "submit", "args": {"report": EMPTY_REPORT}}}])
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    orchestrator = Orchestrator(env, scenario, case, agent, max_turns=args.max_turns, run_config=run_config)
    return orchestrator.run()


def main():
    scenario = PgBusinessChangeCollationConversionScenario()
    parser = argparse.ArgumentParser(description="Run PgBusinessChangeCollationConversionScenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-run-pg-business-change-collation-conversion-scenario")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=12)
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
