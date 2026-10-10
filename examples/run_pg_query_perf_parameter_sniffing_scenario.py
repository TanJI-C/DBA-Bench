import argparse
import copy
import json
import os
import re
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.scenarios.postgres import PgQueryPerfParameterSniffingScenario
from src.execution.deployment import PGDockerDeployment
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSXWorkload



PG_STAT_SQL = (
    "SELECT queryid, query, calls, mean_exec_time, max_exec_time, rows "
    "FROM pg_stat_statements "
    "WHERE query ILIKE '%customer_360%' "
    "   OR query ILIKE '%branch_order_line%' "
    "ORDER BY mean_exec_time DESC LIMIT 10;"
)
PREPARED_SQL = (
    "SELECT name, statement, generic_plans, custom_plans "
    "FROM pg_prepared_statements;"
)


def reference_report_for_case(case):
    return copy.deepcopy(case.reference_report)


def build_full_score_mock_responses(case):
    target_execute_sql = f"EXECUTE {case.stmt_name}({case.hot_year});"
    prepare_sql = (
        f"PREPARE {case.stmt_name}(int) AS {case.fault_fingerprint_sql.rstrip(';')};"
    )
    verify_stmt_sql = (
        "SELECT count(*) FROM pg_prepared_statements "
        f"WHERE name = '{case.stmt_name}';"
    )
    return [
    {
        "thinking": "先看 topsql，定位最近 mean/max latency 异常的 customer 360 报表 fingerprint。",
        "action": {"api": "query_metrics", "args": {"metric_type": "topsql"}},
    },
    {
        "thinking": "再看一次 topsql，确认同一业务报表是否有多次调用和明显 max/mean 分裂。",
        "action": {
            "api": "query_metrics",
            "args": {"metric_type": "topsql", "target": None},
        },
    },
    {
        "thinking": "查询 pg_stat_statements，拿到 queryid、calls、mean/max 和完整业务 SQL。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": PG_STAT_SQL},
        },
    },
    {
        "thinking": "检查当前会话里的运行态 SQL 对象，区分目标报表和其它业务报表噪声。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": PREPARED_SQL},
        },
    },
    {
        "thinking": "对高流量年份绑定执行完整报表的 EXPLAIN ANALYZE，确认慢路径来自原始业务形态。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {target_execute_sql}"},
        },
    },
    {
        "thinking": "应用会让同一报表按当前业务取值重新选择执行路径的修复，并清理旧执行对象。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {"sql_query": "SET plan_cache_mode = 'force_custom_plan';"},
            },
            {"api": "execute_sql", "args": {"sql_query": "DEALLOCATE ALL;"}},
        ],
    },
    {
        "thinking": "用原始高流量年份 EXECUTE 形态复验，再查看可观测指标并提交。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": prepare_sql}},
            {"api": "execute_sql", "args": {"sql_query": f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {target_execute_sql}"}},
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
            {"api": "execute_sql", "args": {"sql_query": verify_stmt_sql}},
            {"api": "submit", "args": {"report": reference_report_for_case(case)}},
        ],
    },
    ]

def build_zero_score_mock_responses(case_id):
    return [{
        "thinking": "不做诊断和修复，直接提交。",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }]


def build_env(case, port: int, container_name: str, image_name: str = None, tool_profile: str = None) -> PGEnv:
    workload = TPCDSXWorkload(scale=case.dataset_scale)
    deployment = PGDockerDeployment(
        container_name=container_name,
        postgres_user="postgres",
        postgres_password="password",
        postgres_db="testdb",
        port=port,
        init_sql_path=workload.get_init_sql_path(),
        workload_data_dir=workload.data_dir,
        dataset_manifest_path=workload.manifest_path,
        image_name=image_name or case.base_image_name,
        resources={
            "cpus": case.deployment_cpus,
            "memory_mb": case.deployment_memory_mb,
            "shm_size": case.deployment_shm_size,
            "disk_quota_mb": workload.disk_quota_mb,
        },
    )
    env_kwargs = {"workload": workload, "deployment": deployment, "port": port}
    if tool_profile:
        env_kwargs["tool_profile"] = tool_profile
    env_kwargs.update({
        "allow_sampler_jitter": True,
        "allow_sampler_reconnect": True,
    })
    return PGEnv(**env_kwargs)













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


def print_evaluation_basis(label: str, result: dict):
    print(f"[Evaluation:{label}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")

def run_mock_full(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Customer 360 Bind-Skew Full-Score Mock Path")
    print("=" * 60)

    scenario = PgQueryPerfParameterSniffingScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=8)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Customer 360 Bind-Skew Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgQueryPerfParameterSniffingScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_zero_score_mock_responses(case_id))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("zero", result)
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str,
    port: int,
    container_name: str,
    model: str = None,
    config_path: str = "config/llm_config.json",
    max_turns: int = 20,
    run_config: OrchestratorRunConfig = None,
    agent_name: str = "llm",
    dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
    dbot_tool_profile: str = "general_knowledge",
    ) -> float:
    print("=" * 60)
    print(f"AiOpsBench PostgreSQL - Customer 360 Bind-Skew {agent_name.upper()}Agent Path")
    print("=" * 60)

    max_turns = min(max_turns, 30)
    try:
        agent = build_agent(
            agent_name=agent_name,
            model=model,
            config_path=config_path,
            dbaiops_graph=dbaiops_graph,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"[{agent_name.upper()}AGENT_BLOCKED] {exc}")
        return 0.0

    tool_profile = dbot_tool_profile if agent_name == "dbot" else None

    scenario = PgQueryPerfParameterSniffingScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case,
        port,
        container_name,
        image_name=None,
        tool_profile=tool_profile,
    )
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
                print(
                    f"[{agent_name.upper()}AGENT_BLOCKED] Agent reached max_turns without submit; "
                    "this is recorded as an execution blocker, not a scenario setup failure."
                )
    print_evaluation_basis(agent_name, result)
    return passed


def build_agent(
    agent_name: str,
    model: str = None,
    config_path: str = "config/llm_config.json",
    dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
):
    return build_experiment_agent(
        model=model,
        config_path=config_path,
        use_native_tools=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Run the PG customer 360 bind-skew query performance scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15448)
    parser.add_argument("--container-name", default="aiopsbench-pg-queryperf-04")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--llm-config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot. Default: general_knowledge.")
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgQueryPerfParameterSniffingScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )

    if args.max_turns > 30:
        raise ValueError("--max-turns must be <= 30")
    if args.mode in ("mock", "all"):
        run_mock_full(args.case, args.port, args.container_name, run_config)
    if args.mode in ("zero", "all"):
        run_mock_zero(args.case, args.port, args.container_name, run_config)
    if args.mode in ("llm", "all"):
        run_llm(args.case,
            args.port,
            args.container_name,
            args.model,
            args.llm_config,
            args.max_turns,
            run_config,
            agent_name=args.agent,
            dbaiops_graph=args.dbaiops_graph,
            dbot_tool_profile=args.dbot_tool_profile,
        )


if __name__ == "__main__":
    main()
