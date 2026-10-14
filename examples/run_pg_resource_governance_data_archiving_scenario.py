import argparse
import json
import os
import sys
import time
from contextlib import nullcontext

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.base import evaluation_passed
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgResourceGovernanceDataArchivingScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig



FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "先查看 order_history 的表级磁盘占用，再用 SQL 识别一年以前冷数据的数量、物理占用和校验基线。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "disk_usage", "target": "order_history"}},
            {"api": "query_metrics", "args": {"metric_type": "workload_activity"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT count(*) AS cold_rows, "
                        "coalesce(sum(id), 0) AS cold_id_sum, "
                        "pg_size_pretty(pg_total_relation_size('order_history')) AS total_size, "
                        "(SELECT count(*) FROM order_history WHERE status = 'LIVE_SENTINEL') AS live_sentinel_rows "
                        "FROM order_history WHERE order_ts < NOW() - INTERVAL '1 year';"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT locktype, relation::regclass, mode, granted "
                        "FROM pg_locks WHERE relation = 'order_history'::regclass;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "采用新表重构和短事务切换，避免 VACUUM FULL 独占锁；先归档冷数据。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "DROP TABLE IF EXISTS order_history_archive; "
                    "CREATE TABLE order_history_archive (LIKE order_history INCLUDING ALL); "
                    "ALTER TABLE order_history_archive "
                    "ADD COLUMN archived_at TIMESTAMP NOT NULL DEFAULT clock_timestamp(), "
                    "ADD COLUMN archive_batch_id TEXT NOT NULL DEFAULT 'batch_202607_data_reclaim'; "
                    "INSERT INTO order_history_archive (id, order_ts, customer_id, amount, status, payload) "
                    "SELECT id, order_ts, customer_id, amount, status, payload "
                    "FROM order_history WHERE order_ts < NOW() - INTERVAL '1 year'; "
                    "DROP TABLE IF EXISTS order_history_archive_manifest; "
                    "CREATE TABLE order_history_archive_manifest AS "
                    "SELECT 'batch_202607_data_reclaim'::text AS archive_batch_id, "
                    "count(*)::bigint AS archived_rows, coalesce(sum(id), 0)::bigint AS archived_id_sum "
                    "FROM order_history_archive;"
                )
            },
        },
    },
    {
        "thinking": "只把热数据导入新表，并在切换前准备索引，降低在线业务阻塞时间。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "DROP TABLE IF EXISTS order_history_new; "
                    "CREATE TABLE order_history_new (LIKE order_history INCLUDING ALL); "
                    "INSERT INTO order_history_new "
                    "SELECT * FROM order_history WHERE order_ts >= NOW() - INTERVAL '1 year'; "
                    "CREATE INDEX idx_order_history_new_order_ts ON order_history_new(order_ts); "
                    "ANALYZE order_history_new; ANALYZE order_history_archive;"
                )
            },
        },
    },
    {
        "thinking": "使用短事务完成重命名切换，再删除旧堆表释放物理空间。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "BEGIN; "
                    "ALTER TABLE order_history RENAME TO order_history_old; "
                    "ALTER TABLE order_history_new RENAME TO order_history; "
                    "COMMIT; "
                    "DROP TABLE order_history_old; "
                    "ALTER INDEX idx_order_history_new_order_ts RENAME TO idx_order_history_order_ts;"
                )
            },
        },
    },
    {
        "thinking": "验证冷数据已经归档，当前热表尺寸下降，并再次观察表级磁盘占用。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "disk_usage", "target": "order_history"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT "
                        "(SELECT count(*) FROM order_history WHERE order_ts < NOW() - INTERVAL '1 year') AS remaining_cold, "
                        "(SELECT count(*) FROM order_history_archive WHERE order_ts < NOW() - INTERVAL '1 year') AS archived_cold, "
                        "(SELECT count(*) FROM order_history WHERE status = 'LIVE_SENTINEL') AS live_sentinel_rows, "
                        "(SELECT archived_id_sum FROM order_history_archive_manifest) AS archived_id_sum, "
                        "pg_size_pretty(pg_total_relation_size('order_history')) AS current_size;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "空间已回收，在线表只保留热数据，提交结果。",
        "action": {"api": "submit", "args": {"report": PgResourceGovernanceDataArchivingScenario().get_case('order_history_cold_archive').reference_report}},
    },
]

ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "错误地执行无关 DDL。",
        "action": {"api": "execute_sql", "args": {"sql_query": "DROP TABLE IF EXISTS unrelated_zero_probe;"}},
    },
    {
        "thinking": "我不知道该怎么做，直接提交。",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def _rewrite_strings(value, replacements):
    if isinstance(value, str):
        for old, new in replacements:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [_rewrite_strings(item, replacements) for item in value]
    if isinstance(value, tuple):
        return tuple(_rewrite_strings(item, replacements) for item in value)
    if isinstance(value, dict):
        return {
            _rewrite_strings(key, replacements): _rewrite_strings(item, replacements)
            for key, item in value.items()
        }
    return value


def build_full_score_mock_responses(case):
    responses = _rewrite_strings(FULL_SCORE_MOCK_RESPONSES, (("order_history", case.table),))
    responses[-1]["action"]["args"]["report"] = case.reference_report
    return responses


def build_zero_score_mock_responses(case):
    responses = _rewrite_strings(ZERO_SCORE_MOCK_RESPONSES, ())
    responses[-1]["action"]["args"]["report"] = EMPTY_REPORT
    return responses




def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    # Custom deployment is only used to isolate this scenario from other local PG runs.
    deployment = PGDockerDeployment(container_name=container_name, port=port)
    deployment.image_name = image_name or case.base_image_name
    return PGEnv(workload=None, deployment=deployment, port=port)















def run_with_orchestrator(
    env, scenario, case, agent, run_config, max_turns: int,
):
    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
        max_turns=max_turns,
        run_config=run_config,
    )
    result = orchestrator.run()
    return result, orchestrator.action_history


def run_mock_full(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Data Archiving Full-Score Mock Path")
    print("=" * 60)

    scenario = PgResourceGovernanceDataArchivingScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=10)
    passed = evaluation_passed(result)
    print(f"[Assert] Mock full-passed path passed={passed}")
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Data Archiving Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgResourceGovernanceDataArchivingScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_zero_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = evaluation_passed(result)
    print(f"[Assert] Mock zero-passed path passed={passed}")
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str, port: int, container_name: str, model: str = None,
            config_path: str = "config/llm_config.json",
            max_turns: int = 30, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Data Archiving LLMAgent Path")
    print("=" * 60)

    scenario = PgResourceGovernanceDataArchivingScenario()
    case = scenario.get_case(case_id)
    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] Missing or invalid local LLM config: {exc}")
        return 0.0

    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = evaluation_passed(result)
    if not any(action.get("api") == "submit" for action in action_history):
        print(
            "[LLMAGENT_BLOCKED] Agent reached max_turns without submit; "
            "increase --max-turns up to 30 and record this run as a blocker only if submit is still missing."
        )
    print(f"[Result] LLMAgent passed={passed}")
    return passed


def main():
    parser = argparse.ArgumentParser(description="Run the PG data archiving and space reclaim scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-pg-resource-archive")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgResourceGovernanceDataArchivingScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )

    if args.mode in ("mock", "all"):
        run_mock_full(args.case, args.port, args.container_name, run_config)
    if args.mode in ("zero", "all"):
        run_mock_zero(args.case, args.port, args.container_name, run_config)
    if args.mode in ("llm", "all"):
        run_llm(args.case, args.port, args.container_name, args.model, args.config_path, args.max_turns, run_config)


if __name__ == "__main__":
    main()
