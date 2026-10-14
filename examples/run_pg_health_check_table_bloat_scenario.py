import argparse
import json
import os
import signal
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scenarios.runtime.config import required_run_timeout_seconds
from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgHealthCheckTableBloatScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload


HARD_TIMEOUT_SEC = 900


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "不做巡检和修复，直接提交。",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    workload = TPCDSWorkload(scale=case.dataset_scale)
    # The entry script needs an isolated container name for repeated mock/zero/llm runs.
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        init_sql_path=workload.get_init_sql_path(),
        workload_data_dir=workload.data_dir,
        image_name=image_name or case.base_image_name,
        resources={
            "cpus": 0.5,
            "memory_mb": 256,
            "shm_size": "128m",
            "disk_quota_mb": getattr(workload, "disk_quota_mb", 8192),
        },
    )
    return PGEnv(
        workload=workload,
        deployment=deployment,
        port=port,
        allow_sampler_jitter=True,
        allow_sampler_reconnect=True,
    )


def build_full_score_mock_responses(case) -> list:
    table = case.target_table
    index_name = case.index_name
    diagnostic_sql = f"""
        SET statement_timeout = '10s';
        SELECT
            s.relname,
            s.n_live_tup,
            s.n_dead_tup,
            round(s.n_dead_tup::numeric / NULLIF(s.n_live_tup + s.n_dead_tup, 0) * 100, 2) AS dead_pct,
            pg_size_pretty(pg_total_relation_size(s.relid)) AS total_size,
            c.reloptions,
            pg_size_pretty(pg_relation_size(i.indexrelid)) AS index_size,
            ci.relname AS index_name
        FROM pg_stat_user_tables s
        JOIN pg_class c ON c.oid = s.relid
        JOIN pg_index i ON i.indrelid = s.relid
        JOIN pg_class ci ON ci.oid = i.indexrelid
        WHERE s.relname IN ({", ".join(repr(t) for t in case.tables)})
        ORDER BY dead_pct DESC NULLS LAST, s.n_dead_tup DESC;
    """
    impact_sql = f"""
        SET statement_timeout = '10s';
        SELECT a.pid, a.application_name, a.state, now() - a.xact_start AS xact_age,
               l.mode, l.granted, left(a.query, 120) AS query
        FROM pg_locks l
        JOIN pg_stat_activity a ON a.pid = l.pid
        WHERE l.relation = '{table}'::regclass
          AND a.pid <> pg_backend_pid()
        ORDER BY l.granted, a.xact_start NULLS LAST;
    """
    repack_sql = "SELECT extname FROM pg_extension WHERE extname = 'pg_repack';"
    lock_timeout_sql = "SET statement_timeout = 0; SET lock_timeout = '30s';"
    vacuum_sql = f"VACUUM FULL {table};"
    reindex_sql = f"REINDEX INDEX {index_name};"
    verify_sql = f"""
        SET statement_timeout = '30s';
        ANALYZE {table};
        SELECT
            s.relname,
            s.n_live_tup,
            s.n_dead_tup,
            round(s.n_dead_tup::numeric / NULLIF(s.n_live_tup + s.n_dead_tup, 0) * 100, 2) AS dead_pct,
            pg_relation_size('{index_name}'::regclass) AS index_bytes
        FROM pg_stat_user_tables s
        WHERE s.relname = '{table}';
    """
    return [
        {
            "thinking": "先看全库 dead tuple 排名和 topsql，避免把普通报表或低比例 dead tuple 当成目标。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "dead_tuples", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "topsql", "target": None, "limit": 10}},
            ],
        },
        {
            "thinking": f"多表都有 dead tuples，但 {table} 的 dead_pct 明显高于比较表，且带有 per-table autovacuum 高阈值；更大的比较表只是低比例噪声。",
            "action": {"api": "execute_sql", "args": {"sql_query": diagnostic_sql}},
        },
        {
            "thinking": "VACUUM FULL 会拿 ACCESS EXCLUSIVE；先查目标表锁、长事务和 pg_repack 是否可用，只能在低峰维护窗口或明确停服风险下做。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": impact_sql}},
                {"api": "execute_sql", "args": {"sql_query": repack_sql}},
            ],
        },
        {
            "thinking": f"pg_repack 不可用，本 benchmark 进入维护窗口后对唯一超阈值目标 {table} 执行 VACUUM FULL 和目标索引 REINDEX，不处理普通噪声表。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": lock_timeout_sql}},
                {"api": "execute_sql", "args": {"sql_query": vacuum_sql}},
                {"api": "execute_sql", "args": {"sql_query": reindex_sql}},
            ],
        },
        {
            "thinking": "复查死元组比例和目标索引大小，确认清理生效。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": verify_sql}},
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def print_evaluation_basis(label: str, result: dict):
    print(f"[Evaluation:{label}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")

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
    print("AiOpsBench PostgreSQL - Table and Index Bloat Full-Score Mock Path")
    print("=" * 60)

    scenario = PgHealthCheckTableBloatScenario()
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
    print("AiOpsBench PostgreSQL - Table and Index Bloat Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgHealthCheckTableBloatScenario()
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
            max_turns: int = 20, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Table and Index Bloat LLMAgent Path")
    print("=" * 60)

    max_turns = min(max_turns, 30)
    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] Missing or invalid local LLM config: {exc}")
        return 0.0

    scenario = PgHealthCheckTableBloatScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
            print("[LLMAGENT_BLOCKED] Agent reached max_turns without submit.")
    print_evaluation_basis("llm", result)
    print(f"[Result] LLMAgent passed={passed}")
    return passed


def main():
    parser = argparse.ArgumentParser(description="Run the PG table and index bloat health-check scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15731)
    parser.add_argument("--container-name", default="aiopsbench-pg-health-31")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgHealthCheckTableBloatScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )
    case = scenario_definition.get_case(args.case)

    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(required_run_timeout_seconds())
    try:
        if args.mode in ("mock", "all"):
            run_mock_full(args.case, args.port, f"{args.container_name}-{case.case_id}-mock", run_config)
        if args.mode in ("zero", "all"):
            run_mock_zero(args.case, args.port, f"{args.container_name}-{case.case_id}-zero", run_config)
        if args.mode in ("llm", "all"):
            run_llm(args.case, args.port, f"{args.container_name}-{case.case_id}-llm", args.model, args.config_path, args.max_turns, run_config=run_config)
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
