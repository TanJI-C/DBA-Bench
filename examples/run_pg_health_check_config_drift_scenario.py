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
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.scenarios.postgres import PgHealthCheckConfigDriftScenario
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


HARD_TIMEOUT_SEC = 900


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Do not inspect capacity or configuration; submit immediately.",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def build_full_score_mock_responses(case) -> list:
    recommendation = (
        "Live cgroup memory for pg-primary-17 is 64GB (65536MB). pg_settings "
        "shows shared_buffers=1GB, effective_cache_size=6GB, and "
        "maintenance_work_mem=256MB coming from postgresql.auto.conf with "
        "pending_restart=false after the recent class move; these are the real "
        "baseline variances. The report SQL, exporter sampling, connection-pool "
        "migration, autovacuum_naptime, max_connections, and intentionally small "
        "work_mem are operational noise, not root cause. shared_buffers is not "
        "sized as a linear fraction of physical memory; increase it only as a "
        "modest restart-window step after checking workload cache pressure. "
        "Production-safe plan: ALTER SYSTEM SET shared_buffers = '6GB'; "
        "ALTER SYSTEM SET effective_cache_size = '48GB'; "
        "ALTER SYSTEM SET maintenance_work_mem = '1GB'; "
        "leave work_mem at 8MB until per-role concurrency is reviewed; "
        "SELECT pg_reload_conf() for reloadable settings, then schedule the "
        "shared_buffers restart in the approved low-traffic maintenance window. "
        "Validate with pg_settings source/unit/pending_restart, query_metrics(memory), "
        "cache_hit_ratio/QPS, and keep a rollback script with ALTER SYSTEM RESET."
    )
    return [
        {
            "thinking": "First check the runtime memory limit exposed by the instance metrics.",
            "action": {
                "api": "query_metrics",
                "args": {"metric_type": "memory", "target": None},
            },
        },
        {
            "thinking": "Compare current PostgreSQL settings, including source and pending_restart, against the live profile.",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": settings_query()},
            },
        },
        {
            "thinking": "Read the maintenance and workload context so reporting, monitoring, pool, and autovacuum noise are not mistaken for the actionable variance.",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {"sql_query": ops_context_query(case.ops_schema)},
                },
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "active_connections", "target": None},
                },
            ],
        },
        {
            "thinking": "Only shared_buffers, effective_cache_size, and maintenance_work_mem lag the current cgroup-sized instance; restart is scheduled, not run during the health check.",
            "action": {
                "api": "submit",
                "args": {"report": case.reference_report},
            },
        },
    ]


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str = None, memory_mb: int = None, image_name: str = None) -> PGEnv:
    env = PGEnv(
        port=port,
        allow_sampler_jitter=True,
        allow_sampler_reconnect=True,
    )
    if container_name:
        env.deployment.container_name = container_name
    env.deployment.image_name = image_name or case.base_image_name
    # This scenario simulates a post-upgrade host profile. Only this entry script
    # overrides resource shape; project defaults remain unchanged.
    env.deployment.resources.update({
        "memory_mb": memory_mb,
        "shm_size": "2g",
    })
    env.deployment.postgres_runtime_options = "-c shared_preload_libraries=pg_stat_statements"
    return env


def settings_query() -> str:
    return """
        SET statement_timeout = '5s';
        SELECT name, setting, unit, source, sourcefile, pending_restart, context,
               round(CASE
                 WHEN unit = '8kB' THEN setting::numeric * 8 / 1024
                 WHEN unit = 'kB' THEN setting::numeric / 1024
                 WHEN unit = 'MB' THEN setting::numeric
                 ELSE NULL
               END, 2) AS current_mb
        FROM pg_settings
        WHERE name IN ('shared_buffers', 'effective_cache_size',
                       'maintenance_work_mem', 'work_mem',
                       'max_connections', 'autovacuum_naptime')
        ORDER BY name;
    """


def ops_context_query(schema: str) -> str:
    return f"""
        SET statement_timeout = '5s';
        SELECT 'instance_inventory' AS section, source, memory_mb::text, note
        FROM {schema}.instance_inventory
        UNION ALL
        SELECT 'maintenance_events', actor, change_summary, note
        FROM {schema}.maintenance_events
        UNION ALL
        SELECT 'workload_observations', application_name, signal, verdict
        FROM {schema}.workload_observations
        ORDER BY section;
    """


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
    print("AiOpsBench PostgreSQL - Configuration Drift Full-Score Mock Path")
    print("=" * 70)

    scenario = PgHealthCheckConfigDriftScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, case.memory_limit_mb, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=8)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Configuration Drift Zero-Score Mock Path")
    print("=" * 70)

    scenario = PgHealthCheckConfigDriftScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, case.memory_limit_mb, image_name=None)
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
    print("AiOpsBench PostgreSQL - Configuration Drift LLMAgent Path")
    print("=" * 70)

    max_turns = min(max_turns, 30)
    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] Missing or invalid local LLM config: {exc}")
        return 0.0

    scenario = PgHealthCheckConfigDriftScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, case.memory_limit_mb, image_name=None)
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
            print("[LLMAGENT_BLOCKED] Agent reached max_turns without submit.")
    print_evaluation_basis("llm", result)
    print(f"[Result] LLMAgent passed={passed}")
    return passed


def main():
    parser = argparse.ArgumentParser(description="Run the PG configuration drift health-check scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15735)
    parser.add_argument("--container-name", default="aiopsbench-pg-health-35")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgHealthCheckConfigDriftScenario()
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
