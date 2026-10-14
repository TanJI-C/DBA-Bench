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
from src.scenarios.postgres import PgHealthCheckLongRunningTxCase, PgHealthCheckLongRunningTxScenario
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload


HARD_TIMEOUT_SEC = 900


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Do not inspect the database state; submit immediately.",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def build_full_score_mock_responses(case: PgHealthCheckLongRunningTxCase) -> list:
    table = case.table
    app_name = case.blocker_app_name
    decoy_app_name = case.decoy_app_name
    reference_report = json.loads(json.dumps(case.reference_report))
    if case.case_id.startswith("stress_idle_transaction_cleanup_"):
        reference_report["diagnosis"]["conditions"].extend([
            {
                "type": "finding",
                "factor": "short idle transaction must be preserved",
                "entity": case.case_id,
                "evidence": [
                    "scripted diagnostic actions observed short idle transaction must be preserved"
                ],
            },
            {
                "type": "finding",
                "factor": "configure a five minute idle transaction timeout",
                "entity": case.case_id,
                "evidence": [
                    "scripted diagnostic actions observed configure a five minute idle transaction timeout"
                ],
            },
        ])
    return [
        {
            "thinking": "Build a connection census before touching anything; the ticket only says cleanup horizon drift.",
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": f"""
                        SET statement_timeout = '10s';
                        SELECT pid, application_name, state, wait_event_type, wait_event,
                               now() - xact_start AS xact_age,
                               now() - query_start AS query_age,
                               backend_xmin,
                               left(query, 220) AS query
                        FROM pg_stat_activity
                        WHERE datname = current_database()
                          AND backend_type = 'client backend'
                          AND pid <> pg_backend_pid()
                        ORDER BY xact_start NULLS LAST, query_start NULLS LAST, application_name;
                    """,
                },
            },
        },
        {
            "thinking": "Quantify cleanup impact from table stats instead of assuming every idle transaction is harmful.",
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": f"""
                        SET statement_timeout = '10s';
                        SELECT relname, n_live_tup, n_dead_tup, last_vacuum, last_autovacuum,
                               vacuum_count, autovacuum_count
                        FROM pg_stat_user_tables
                        WHERE relname = '{table}';
                    """,
                },
            },
        },
        {
            "thinking": "Check whether the old snapshot is also holding locks; avoid killing report, monitor, or short decoy sessions.",
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": f"""
                        SET statement_timeout = '10s';
                        SELECT a.pid, a.application_name, a.state, a.backend_xmin,
                               pg_blocking_pids(a.pid) AS blocking_pids,
                               l.locktype, l.mode, l.granted
                        FROM pg_stat_activity a
                        LEFT JOIN pg_locks l ON l.pid = a.pid
                        WHERE a.application_name IN ('{app_name}', '{decoy_app_name}')
                           OR a.application_name LIKE 'reporting-%'
                           OR a.application_name LIKE 'pg-exporter-%'
                           OR a.application_name LIKE 'grafana-%';
                    """,
                },
            },
        },
        {
            "thinking": "Terminate only the old checkout pool transaction with backend_xmin; leave the short payment decoy and reporting probes alone.",
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": f"""
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE application_name = '{app_name}'
                          AND state = 'idle in transaction'
                          AND backend_xmin IS NOT NULL
                          AND pid <> pg_backend_pid();
                    """,
                },
            },
        },
        {
            "thinking": "Configure a guardrail so future idle transactions are closed automatically.",
            "action": {
                "api": "manage_instance",
                "args": {
                    "action": "set_config",
                    "target": "idle_in_transaction_session_timeout",
                    "value": "5min",
                },
            },
        },
        {
            "thinking": "Reload PostgreSQL configuration so the timeout guardrail is active.",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": "SELECT pg_reload_conf();"},
            },
        },
        {
            "thinking": "With the old snapshot gone, run maintenance and verify dead tuples can be reclaimed.",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": f"VACUUM {table};"},
            },
        },
        {
            "thinking": "Verify the blocker is gone, the short decoy was not killed, timeout is active, and cleanup can reclaim dead tuples.",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": f"""
                            SET statement_timeout = '10s';
                            SELECT
                                count(*) FILTER (
                                    WHERE application_name = '{app_name}'
                                      AND state = 'idle in transaction'
                                      AND backend_xmin IS NOT NULL
                                ) AS target_blockers,
                                count(*) FILTER (
                                    WHERE application_name = '{decoy_app_name}'
                                      AND state = 'idle in transaction'
                                ) AS short_idle_decoys
                            FROM pg_stat_activity
                            WHERE pid <> pg_backend_pid();
                        """,
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "SHOW idle_in_transaction_session_timeout;"},
                },
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "dead_tuple_backlog", "target": table},
                },
                {"api": "submit", "args": {"report": reference_report}},
            ],
        },
    ]


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    workload = TPCDSWorkload(scale=case.dataset_scale)
    env = PGEnv(
        workload=workload,
        port=port,
        allow_sampler_jitter=True,
        allow_sampler_reconnect=True,
    )
    env.deployment.container_name = container_name
    env.deployment.image_name = image_name or case.base_image_name
    return env


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
    print("AiOpsBench PostgreSQL - Long Transaction Full-Score Mock Path")
    print("=" * 70)

    scenario = PgHealthCheckLongRunningTxScenario()
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
    print("AiOpsBench PostgreSQL - Long Transaction Zero-Score Mock Path")
    print("=" * 70)

    scenario = PgHealthCheckLongRunningTxScenario()
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
    print("AiOpsBench PostgreSQL - Long Transaction LLMAgent Path")
    print("=" * 70)

    max_turns = min(max_turns, 30)
    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] Missing or invalid local LLM config: {exc}")
        return 0.0

    scenario = PgHealthCheckLongRunningTxScenario()
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
    parser = argparse.ArgumentParser(description="Run the PG long-running transaction health-check scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15734)
    parser.add_argument("--container-name", default="aiopsbench-pg-health-34")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgHealthCheckLongRunningTxScenario()
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
