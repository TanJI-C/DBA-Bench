import argparse
import json
import os
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgQueryPerfMissingIndexScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSXWorkload



# 讲解这类入口脚本时可以按这一条主线走：
# 1. 定义目标慢 SQL 和 mock/zero/llm 三条运行路径；
# 2. build_env 部署数据库；
# 3. prepare_and_inject 在 hidden 区域搭建真实故障并做可观测性验收；
# 4. seed 一条 Agent 可见的真实业务 SQL；
# 5. Orchestrator 接管 agent loop，最后 evaluator 根据 action_history 和真实环境打分。
# Mock 满分路径必须覆盖场景文档的关键检查点：
# pg_stat_statements 找 fault fingerprint → EXPLAIN 验证 → 索引元数据 →
# 表达式索引修复 → 修复后指纹与计划复验 → submit。
def reference_report_for_case(case):
    if case.case_id in {"product_category_substring", "product_category_prefix_simple"}:
        return {
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "sequential scan on product",
                        "entity": "product",
                        "evidence": [
                            "scripted diagnostic actions observed sequential scan on product"
                        ],
                    },
                    {
                        "type": "finding",
                        "factor": "missing substring expression index",
                        "entity": "product",
                        "evidence": [
                            "scripted diagnostic actions observed missing substring expression index"
                        ],
                    },
                ]
            },
            "outcome": {
                "changes": ["created the matching substring expression index"],
                "verification": ["verified the recovered indexed plan"],
            },
            "summary": "The scripted mock completed its case-specific diagnosis and verification.",
        }
    return case.reference_report


def build_full_score_mock_responses(case):
    target_explain_sql = (
        "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
        f"{case.fault_fingerprint_sql.rstrip(';')};"
    )
    fingerprint_rank_sql = (
        "SELECT query, calls, mean_exec_time FROM pg_stat_statements "
        "ORDER BY mean_exec_time DESC LIMIT 5;"
    )
    return [
    {
        "thinking": "先从 pg_stat_statements 找出 mean_exec_time 最高的业务 fingerprint（injector 在后台循环跑 fault fingerprint），再 EXPLAIN 定位。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": fingerprint_rank_sql},
        },
    },
    {
        "thinking": "对退化最严重的报表查询做 EXPLAIN ANALYZE，确认 filtered_product 里的 substring(pr_category) 触发表扫描并放大后续 join/aggregate 成本。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": target_explain_sql},
        },
    },
    {
        "thinking": f"检查 {case.table} 表索引定义，确认同列普通索引与 pattern 索引为何都不服务该谓词、是否缺表达式索引。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT indexname, indexdef FROM pg_indexes "
                    f"WHERE tablename = '{case.table}' "
                    f"AND (indexdef ILIKE '%{case.column}%' "
                    "OR indexdef ILIKE '%substring%');"
                )
            },
        },
    },
    {
        "thinking": "目标谓词使用 substring(pr_category, 1, 3)；创建 evaluator 合同允许的表达式索引。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    f"CREATE INDEX IF NOT EXISTS {case.remediation_index_name} "
                    f"ON {case.table} ((substring({case.column}, 1, 3)));"
                )
            },
        },
    },
    {
        "thinking": "复查 pg_stat_statements 中同一条查询的耗时，并对完整复杂查询做 EXPLAIN ANALYZE，确认修复后执行时间下降。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": fingerprint_rank_sql}},
            {"api": "execute_sql", "args": {"sql_query": target_explain_sql}},
        ],
    },
    {
        "thinking": "重复验证同一条完整查询，排除首次读取索引与数据页的冷缓存开销。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": target_explain_sql},
        },
    },
    {
        "thinking": "目标查询已恢复使用索引路径，提交结果。",
        "action": {
            "api": "submit",
            "args": {"report": reference_report_for_case(case)},
        },
    },
    ]


def build_zero_score_mock_responses(case):
    return [{
        "thinking": "没有诊断和修复，直接提交。",
        "action": {
            "api": "submit",
            "args": {"report": EMPTY_REPORT},
        },
    }]


def build_env(
    case,
    port: int,
    container_name: str = None,
    image_name: str = None,
    tool_profile: str = None,
    cold_start_timeout: int = 600,
) -> PGEnv:
    # 数据集指纹与 fat 镜像标签不一致时，deployment 会重建数据集容器并回写镜像标签；
    # 共享主机 I/O 繁忙时全量 COPY 可能超出默认 600s，需要通过 --cold-start-timeout 放宽。
    workload = TPCDSXWorkload(scale=case.dataset_scale)
    deployment = PGDockerDeployment(
        container_name=container_name or "aiopsbench-pg",
        postgres_user="postgres",
        postgres_password="password",
        port=port,
        init_sql_path=workload.get_init_sql_path(),
        workload_data_dir=workload.data_dir,
        dataset_manifest_path=workload.manifest_path,
        image_name=image_name or case.base_image_name,
        resources={
            "cpus": 1.0,
            "memory_mb": 512,
            "shm_size": "256m",
            "disk_quota_mb": getattr(workload, "disk_quota_mb", 8192),
        },
        initialization_timeout_seconds=cold_start_timeout,
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

def run_mock_full(case_id: str,
    port: int,
    container_name: str = None,
    run_config: OrchestratorRunConfig = None,
    cold_start_timeout: int = 600,
    ) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Missing Index Full-Score Mock Path")
    print("=" * 60)

    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None, cold_start_timeout=cold_start_timeout)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=12)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    print(f"[Assert] Mock full-passed path passed={passed}")
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str,
    port: int,
    container_name: str = None,
    run_config: OrchestratorRunConfig = None,
    cold_start_timeout: int = 600,
    ) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Missing Index Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None, cold_start_timeout=cold_start_timeout)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_zero_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("zero", result)
    print(f"[Assert] Mock zero-passed path passed={passed}")
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str,
    port: int,
    container_name: str = None,
    model: str = None,
    config_path: str = None,
    max_turns: int = 30,
    run_config: OrchestratorRunConfig = None,
    agent_name: str = "llm",
    dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
    dbot_tool_profile: str = "general_knowledge",
    cold_start_timeout: int = 600,
    ) -> float:
    print("=" * 60)
    print(f"AiOpsBench PostgreSQL - Missing Index {agent_name.upper()}Agent Path")
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

    # D-Bot 依赖 PGEnv 的 tool_profile；其他 agent 走默认 profile 即可。
    tool_profile = dbot_tool_profile if agent_name == "dbot" else None

    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(
        case,
        port,
        container_name,
        image_name=None,
        tool_profile=tool_profile,
        cold_start_timeout=cold_start_timeout,
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
    parser = argparse.ArgumentParser(description="Run the PG missing index query performance scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-pg-queryperf-01")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--llm-config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot. Default: general_knowledge "
                             "(better RCA on PG scenarios). Pass db_gpt for the DB-GPT semantic tool set.")
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--cold-start-timeout", type=int, default=600,
                        help="Dataset container initialization budget in seconds.")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgQueryPerfMissingIndexScenario()
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
        run_mock_full(args.case, args.port, args.container_name, run_config, args.cold_start_timeout)
    if args.mode in ("zero", "all"):
        run_mock_zero(args.case, args.port, args.container_name, run_config, args.cold_start_timeout)
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
            cold_start_timeout=args.cold_start_timeout,
        )


if __name__ == "__main__":
    main()
