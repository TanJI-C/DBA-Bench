import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.scenarios.postgres import PgQueryPerfSortSpillScenario
from src.execution.deployment import PGDockerDeployment
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSXWorkload



# 讲解主线：本入口脚本用 TPC-DS 重型 fingerprint（q80，9 表 + UNION + 大排序），
# injector 把 work_mem 降到 4MB，让 q80 的 Sort/Hash 落盘写临时文件。
# evaluator 要看到 Agent 查 topsql、查 EXPLAIN、检查 work_mem、调大并 reload，
# 再用环境验证 temp I/O 消失。目标 SQL 从运行时选中的 Case 读取。
WORK_MEM_SQL = (
    "SELECT name, setting, unit, source "
    "FROM pg_settings WHERE name = 'work_mem';"
)
TEMP_IO_SQL = (
    "SELECT datname, temp_files, temp_bytes "
    "FROM pg_stat_database WHERE datname = current_database();"
)


def build_full_score_mock_responses(case):
    target_explain_sql = (
        "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
        f"{case.fault_fingerprint_sql.rstrip(';')};"
    )
    reference_report = (
        {
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "sort spills to disk",
                        "entity": "branch_order_sort_spill_simple",
                        "evidence": [
                            "scripted diagnostic actions observed sort spills to disk"
                        ],
                    },
                    {
                        "type": "finding",
                        "factor": "work_mem too low for report",
                        "entity": "branch_order_sort_spill_simple",
                        "evidence": [
                            "scripted diagnostic actions observed work_mem too low for report"
                        ],
                    },
                ]
            },
            "outcome": {
                "changes": ["set the targeted report work_mem"],
                "verification": ["verified an in-memory sort"],
            },
            "summary": "The scripted mock completed its case-specific diagnosis and verification.",
        }
        if case.case_id == "branch_order_sort_spill_simple"
        else case.reference_report
    )
    return [
    {
        "thinking": "先看 topsql 找出 pg_stat_statements 里 mean_exec_time 最高的 fingerprint（injector 在后台循环跑 fault fingerprint），再做 EXPLAIN 定位。",
        "action": {"api": "query_metrics", "args": {"metric_type": "topsql"}},
    },
    {
        "thinking": "先查看报表查询执行计划，确认是否存在排序或聚合阶段的磁盘临时 I/O。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": target_explain_sql},
        },
    },
    {
        "thinking": "执行计划显示 external merge 和 temp written blocks，继续检查当前 work_mem 配置。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": WORK_MEM_SQL},
        },
    },
    {
        "thinking": "检查 pg_stat_database 的 temp_files/temp_bytes，确认瓶颈是排序/聚合临时文件 I/O，而不是缺索引。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": TEMP_IO_SQL},
        },
    },
    {
        "thinking": "work_mem 偏低，使用 ALTER SYSTEM 提高该配置，reload 后重置当前会话设置以便验证持久配置。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER SYSTEM SET work_mem = '256MB';"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SELECT pg_reload_conf();"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "RESET work_mem; SHOW work_mem;"},
            },
        ],
    },
    {
        "thinking": "重新执行计划验证排序不再落盘，并确认临时块写入消失。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": target_explain_sql},
        },
    },
    {
        "thinking": "配置已生效，目标查询不再外部排序，再次查看 topsql 确认 mean_exec_time 下降，提交诊断结果。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
            {"api": "submit", "args": {"report": reference_report}},
        ],
    },
    ]


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "不做诊断和修复，直接提交。",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def build_env(case, port: int, container_name: str, image_name: str = None, tool_profile: str = None) -> PGEnv:
    workload = TPCDSXWorkload(scale=case.dataset_scale)
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        init_sql_path=workload.get_init_sql_path(),
        workload_data_dir=workload.data_dir,
        dataset_manifest_path=workload.manifest_path,
        image_name=image_name or case.base_image_name,
        resources={
            "shm_size": "128m",
            "cpus": 1.0,
            "memory_mb": case.deployment_memory_mb,
            "disk_quota_mb": workload.disk_quota_mb,
        },
        # shared_buffers 固定较小，帮助稳定复现大表分析查询的物理读压力；
        # 本场景真正要修的是 work_mem，不是 shared_buffers。
        postgres_runtime_options=(
            "-c shared_buffers=64MB "
            "-c autovacuum=off "
            "-c shared_preload_libraries=pg_stat_statements"
        ),
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
    print("AiOpsBench PostgreSQL - Sort Spill Full-Score Mock Path")
    print("=" * 60)

    scenario = PgQueryPerfSortSpillScenario()
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
    print("AiOpsBench PostgreSQL - Sort Spill Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgQueryPerfSortSpillScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(ZERO_SCORE_MOCK_RESPONSES)
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("zero", result)
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str, port: int, container_name: str, model: str = None,
            config_path: str = "config/llm_config.json",
            max_turns: int = 20,
            run_config: OrchestratorRunConfig = None,
            agent_name: str = "llm",
            dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
            dbot_tool_profile: str = "general_knowledge") -> float:
    print("=" * 60)
    print(f"AiOpsBench PostgreSQL - Sort Spill {agent_name.upper()}Agent Path")
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

    scenario = PgQueryPerfSortSpillScenario()
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
    print(f"[Result] {agent_name.upper()}Agent passed={passed}")
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
    parser = argparse.ArgumentParser(description="Run the PG sort spill query performance scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15457)
    parser.add_argument("--container-name", default="aiopsbench-pg-queryperf-07")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--llm-config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot. Default: general_knowledge.")
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgQueryPerfSortSpillScenario()
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
        run_mock_full(args.case, args.port, args.container_name, run_config=run_config)
    if args.mode in ("zero", "all"):
        run_mock_zero(args.case, args.port, args.container_name, run_config=run_config)
    if args.mode in ("llm", "all"):
        run_llm(args.case,
            args.port,
            args.container_name,
            args.model,
            args.llm_config,
            args.max_turns,
            run_config=run_config,
            agent_name=args.agent,
            dbaiops_graph=args.dbaiops_graph,
            dbot_tool_profile=args.dbot_tool_profile,
        )


if __name__ == "__main__":
    main()
