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
from src.scenarios.postgres import PgHealthCheckUnusedIndexesScenario
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload


HARD_TIMEOUT_SEC = 900


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Do not inspect index health; submit immediately.",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    workload = TPCDSWorkload(scale=case.dataset_scale)
    env = PGEnv(workload=workload, port=port, allow_sampler_jitter=True, allow_sampler_reconnect=True)
    # Scenario runs need isolated container names for mock/zero/llm repetitions.
    env.deployment.container_name = container_name
    env.deployment.image_name = image_name or case.base_image_name
    return env


def build_full_score_mock_responses(case) -> list:
    table = case.table
    drop_names = tuple(case.required_drop_indexes)
    protected_names = tuple(case.must_keep_indexes)
    drop_names_sql = ", ".join(repr(name) for name in drop_names)
    protected_names_sql = ", ".join(repr(name) for name in protected_names)
    stats_tables = [case.table] + ([case.attribution_table] if case.attribution_table else [])
    stats_tables_sql = ", ".join(repr(name) for name in stats_tables)
    return [
        {
            "thinking": (
                "The ticket covers the customer domain, so first quantify the "
                "write pattern per table: update volume, HOT ratio, and dead "
                "tuples decide which table's index maintenance drives overhead."
            ),
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SET statement_timeout = '10s'; "
                            "SELECT relname, n_tup_ins, n_tup_upd, n_tup_hot_upd, "
                            "n_tup_del, n_dead_tup, last_autovacuum, last_autoanalyze "
                            "FROM pg_stat_user_tables "
                            f"WHERE relname IN ({stats_tables_sql});"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SET statement_timeout = '10s'; "
                            "SELECT query, calls, mean_exec_time "
                            "FROM pg_stat_statements "
                            "WHERE query NOT ILIKE '%pg_stat_statements%' "
                            "ORDER BY total_exec_time DESC LIMIT 10;"
                        )
                    },
                },
            ],
        },
        {
            "thinking": (
                "Now inspect per-index usage counters; idx_scan=0 is only a "
                "candidate signal, not a drop decision."
            ),
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SET statement_timeout = '10s'; "
                        "SELECT relname, indexrelname, idx_scan, idx_tup_read, idx_tup_fetch "
                        "FROM pg_stat_user_indexes "
                        f"WHERE relname = '{table}' "
                        "ORDER BY idx_scan, indexrelname;"
                    )
                },
            },
        },
        {
            "thinking": (
                "Pull definitions, key order, predicates, expressions, comments, "
                "and constraints to separate true cleanup targets from protected "
                "release, rollback, partial, expression, FK, unique, and low-frequency paths."
            ),
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SET statement_timeout = '10s'; "
                            "SELECT indexname, indexdef "
                            "FROM pg_indexes "
                            f"WHERE tablename = '{table}' "
                            "ORDER BY indexname;"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SET statement_timeout = '10s'; "
                            "SELECT c.relname AS index_name, i.indisunique, i.indisprimary, "
                            "i.indkey::text AS key_attnums, "
                            "pg_get_expr(i.indpred, i.indrelid) AS predicate, "
                            "pg_get_expr(i.indexprs, i.indrelid) AS expression, "
                            "obj_description(i.indexrelid, 'pg_class') AS note, "
                            "con.conname AS constraint_name, pg_get_indexdef(i.indexrelid) AS indexdef "
                            "FROM pg_index i "
                            "JOIN pg_class c ON c.oid = i.indexrelid "
                            "LEFT JOIN pg_constraint con ON con.conindid = i.indexrelid "
                            f"WHERE i.indrelid = '{table}'::regclass "
                            "ORDER BY c.relname;"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SET statement_timeout = '10s'; "
                            "SELECT conname, contype, convalidated "
                            "FROM pg_constraint "
                            f"WHERE conrelid = '{table}'::regclass "
                            "ORDER BY conname;"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SET statement_timeout = '10s'; "
                            "SELECT change_id, applied_at, table_name, index_name, action, "
                            "observation_policy, note "
                            "FROM ops_maintenance.index_changes "
                            f"WHERE table_name IN ({stats_tables_sql}) "
                            "ORDER BY applied_at;"
                        )
                    },
                },
            ],
        },
        {
            "thinking": (
                f"Only {', '.join(drop_names)} are safe cleanup targets. "
                "Use CONCURRENTLY to avoid blocking production writes."
            ),
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {"sql_query": f"DROP INDEX CONCURRENTLY IF EXISTS {idx};"},
                }
                for idx in case.required_drop_indexes
            ],
        },
        {
            "thinking": "Verify the cleanup result, then submit.",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                        "SET statement_timeout = '5s'; "
                        "SELECT c.relname, "
                        f"CASE WHEN c.relname IN ({protected_names_sql}) "
                        "THEN 'protected_index_retained' ELSE 'unexpected_remaining_target' END AS status "
                        "FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid "
                        f"WHERE i.indrelid = '{table}'::regclass "
                        f"AND c.relname IN ({drop_names_sql}, {protected_names_sql}) "
                            "ORDER BY c.relname;"
                        )
                    },
                },
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
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Unused Indexes Full-Score Mock Path")
    print("=" * 70)

    scenario = PgHealthCheckUnusedIndexesScenario()
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
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Unused Indexes Zero-Score Mock Path")
    print("=" * 70)

    scenario = PgHealthCheckUnusedIndexesScenario()
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
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Unused Indexes LLMAgent Path")
    print("=" * 70)

    max_turns = min(max_turns, 30)
    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] Missing or invalid local LLM config: {exc}")
        return 0.0

    scenario = PgHealthCheckUnusedIndexesScenario()
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
    parser = argparse.ArgumentParser(description="Run the PG unused/redundant indexes health-check scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15733)
    parser.add_argument("--container-name", default="aiopsbench-pg-health-33")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    parser.add_argument("--diagnosis-match-mode", choices=("exact", "semantic"), default="exact")
    parser.add_argument("--diagnosis-semantic-model")
    parser.add_argument("--diagnosis-semantic-config")
    scenario_definition = PgHealthCheckUnusedIndexesScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
        diagnosis_match_mode=args.diagnosis_match_mode,
        diagnosis_semantic_model=args.diagnosis_semantic_model or OrchestratorRunConfig().diagnosis_semantic_model,
        diagnosis_semantic_config_path=args.diagnosis_semantic_config or args.config_path,
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
