import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.base import evaluation_passed
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgResourceGovernanceHostBackupScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


def _sql_string_list(values):
    return "(" + ", ".join(f"'{value}'" for value in values) + ")"


def build_full_score_mock_responses(case):
    return [
        {
            "thinking": "先查看磁盘 I/O 与慢查询，确认这是多条报表共同受影响而不是单条 SQL 计划退化。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "slow_queries", "target": None, "threshold_ms": 1000}},
            ],
        },
        {
            "thinking": "检查活跃会话和备份治理目录，把报表受害者与备份读流区分开。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT pid, application_name, state, wait_event_type, left(query, 160) "
                            "FROM pg_stat_activity "
                            f"WHERE application_name = '{case.backup_app_name}' "
                            f"OR application_name IN {_sql_string_list(case.report_app_names)} "
                            "ORDER BY application_name, query_start NULLS LAST;"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            f"SELECT job_name, status, source, scheduled_window FROM {case.control_table} "
                            "ORDER BY job_name;"
                        )
                    },
                },
            ],
        },
        {
            "thinking": "暂停目标备份读流，不改报表 SQL，也不重启数据库。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT pg_terminate_backend(pid) "
                            "FROM pg_stat_activity "
                            f"WHERE application_name = '{case.backup_app_name}' "
                            "AND pid <> pg_backend_pid();"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            f"UPDATE {case.control_table} "
                            "SET status = 'paused', governed_at = clock_timestamp() "
                            f"WHERE job_name = '{case.backup_job_name}';"
                        )
                    },
                },
            ],
        },
        {
            "thinking": "验证备份读会话已消失，目录状态已治理，报表探针可正常返回。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT count(*) FROM pg_stat_activity "
                            f"WHERE application_name = '{case.backup_app_name}';"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            f"SELECT status FROM {case.control_table} "
                            f"WHERE job_name = '{case.backup_job_name}';"
                        )
                    },
                },
                {"api": "execute_sql", "args": {"sql_query": case.report_probe_query}},
            ],
        },
        {
            "thinking": "确认根因是备份读流抢占，已安全暂停并恢复报表，提交结果。",
            "action": {"api": "submit", "args": {"report": case.reference_report}},
        },
    ]


def build_zero_score_mock_responses(case):
    return [
        {
            "thinking": "错误地尝试执行无关 DDL。",
            "action": {"api": "execute_sql", "args": {"sql_query": "DROP TABLE IF EXISTS unrelated_zero_probe;"}},
        },
        {
            "thinking": "不排查，直接提交。",
            "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
        }
    ]


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    deployment = PGDockerDeployment(container_name=container_name, port=port, image_name=image_name or case.base_image_name)
    return PGEnv(workload=None, deployment=deployment, port=port)


def run_with_orchestrator(env, scenario, case, agent, run_config, max_turns: int):
    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
        max_turns=max_turns,
        run_config=run_config,
    )
    return orchestrator.run(), orchestrator.action_history


def run_mode(case_id: str, mode: str, port: int, container_name: str, model: str, config_path: str, max_turns: int, run_config):
    scenario = PgResourceGovernanceHostBackupScenario()
    case = scenario.get_case(case_id)
    env = build_env(case, port, container_name)
    if mode == "mock":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(build_full_score_mock_responses(case))
        turns = 10
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(build_zero_score_mock_responses(case))
        turns = 3
    else:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
        turns = max_turns
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, turns)
    passed = evaluation_passed(result)
    print(f"[{mode}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']} passed={passed}")
    if mode == "mock":
        assert passed is True, json.dumps(result, ensure_ascii=False)
    if mode == "zero":
        assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def main():
    scenario = PgResourceGovernanceHostBackupScenario()
    parser = argparse.ArgumentParser(description="Run the PG host backup read-saturation scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15730)
    parser.add_argument("--container-name", default="aiopsbench-pg-resource-host-backup")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )
    modes = ("mock", "zero", "llm") if args.mode == "all" else (args.mode,)
    for index, mode in enumerate(modes):
        run_mode(
            args.case,
            mode,
            args.port + index,
            f"{args.container_name}-{args.case}-{mode}",
            args.model,
            args.config_path,
            args.max_turns,
            run_config,
        )


if __name__ == "__main__":
    main()
