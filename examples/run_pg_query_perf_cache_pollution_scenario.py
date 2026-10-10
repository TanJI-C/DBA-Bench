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
from src.scenarios.postgres import PgQueryPerfCachePollutionScenario
from src.execution.deployment import PGDockerDeployment
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


HARD_TIMEOUT_SEC = 720


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def _condition(factor: str, entity: str, evidence: str) -> dict:
    return {
        "type": "finding",
        "factor": factor,
        "entity": entity,
        "evidence": [evidence],
    }


def build_success_report(case) -> dict:
    if case.fault_variant == "long_tx_cache_churn":
        conditions = [
            _condition("low cache hit ratio", case.hot_table, "cache_hit_ratio showed degradation"),
            _condition("long analytics cursor", case.scan_app_name, "pg_stat_activity showed an old backend_xmin"),
            _condition("vacuum blocked by old snapshot", case.hot_table, "dead tuples remained while the cursor held its snapshot"),
            _condition("cursor blocks vacuum causing cache churn", case.hot_table, "session age, dead tuples, and cache pressure formed one causal chain"),
            _condition("terminate analytics cursor then vacuum", case.scan_app_name, "only the culprit cursor was terminated before cleanup"),
        ]
    else:
        cause = "billing export scan cache churn" if case.case_id.startswith("billing") else "archive scan cache pollution"
        conditions = [
            _condition("low cache hit ratio", case.hot_table, "cache_hit_ratio showed degradation"),
            _condition(cause, case.scan_app_name, "pg_stat_activity identified the reporting scan"),
            _condition("memory sizing is not root cause", "shared_buffers", "pg_settings showed the intended memory configuration"),
            _condition("hot page displacement", case.hot_table, "pg_buffercache showed archive pages displacing hot OLTP pages"),
            _condition("workload isolation", case.scan_app_name, "the recurrence control isolates and limits this reporting workload"),
        ]
    return {
        "diagnosis": {"conditions": conditions},
        "outcome": {
            "changes": [
                f"terminated only {case.scan_app_name}",
                f"persisted recurrence control in {case.control_table}",
            ],
            "verification": [
                f"{case.scan_app_name} is absent",
                f"{case.hot_table} probe succeeds",
            ],
        },
        "summary": "Targeted remediation removed cache pressure without resizing memory or restarting PostgreSQL.",
    }


def build_failure_report() -> dict:
    return {
        "diagnosis": {"conditions": []},
        "outcome": {"changes": [], "verification": []},
        "summary": "No diagnosis or remediation was attempted.",
    }


def build_env(
    case,
    port: int,
    container_name: str,
    image_name: str = None,
) -> PGEnv:
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        image_name=image_name or case.base_image_name,
        postgres_runtime_options=(
            f"-c shared_buffers={case.shared_buffers} "
            "-c work_mem=32MB "
            "-c shared_preload_libraries=pg_stat_statements"
        ),
    )
    return PGEnv(workload=None, deployment=deployment, port=port)





def build_full_score_mock_agent(case):
    if getattr(case, "fault_variant", "") == "long_tx_cache_churn":
        activity_sql = f"""
            SET statement_timeout = '10s';
            SELECT pid, application_name, state, backend_xmin, xact_start,
                   now() - xact_start AS xact_age,
                   left(query, 220) AS query
            FROM pg_stat_activity
            WHERE datname = current_database()
              AND (application_name IN ('{case.scan_app_name}', '{case.oltp_app_name}')
                   OR state = 'idle in transaction')
            ORDER BY xact_start NULLS LAST, application_name;
        """
        settings_sql = """
            SELECT name, setting, unit, source
            FROM pg_settings
            WHERE name IN ('shared_buffers', 'effective_cache_size', 'work_mem')
            ORDER BY name;
        """
        dead_tuple_sql = f"""
            SELECT relname, n_dead_tup, last_autovacuum, last_vacuum
            FROM pg_stat_user_tables
            WHERE relname = '{case.hot_table}';
        """
        terminate_sql = f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE application_name = '{case.scan_app_name}'
              AND pid <> pg_backend_pid();
        """
        settle_sql = "SELECT pg_sleep(1); COMMIT;"
        vacuum_sql = f"VACUUM {case.hot_table};"
        mitigation_sql = f"""
            INSERT INTO {case.control_table} (control_name, recommendation)
            VALUES (
                '{case.scan_app_name}',
                'Limit analytics cursor lifetime with transaction timeout, isolate long snapshots on a replica, and monitor dead tuples/vacuum lag before cache hit ratio degrades.'
            )
            ON CONFLICT (control_name)
            DO UPDATE SET recommendation = EXCLUDED.recommendation, applied_at = now();
        """
        verify_sql = f"""
            SELECT pg_sleep(1);
            SELECT application_name, state, count(*)
            FROM pg_stat_activity
            WHERE application_name IN ('{case.scan_app_name}', '{case.oltp_app_name}')
            GROUP BY application_name, state
            ORDER BY application_name, state;

            SELECT relname, n_dead_tup
            FROM pg_stat_user_tables
            WHERE relname = '{case.hot_table}';

            SELECT control_name, recommendation
            FROM {case.control_table}
            WHERE control_name = '{case.scan_app_name}';
        """
        mock_responses = [
            {
                "thinking": "The alert is a low cache hit ratio, so first confirm the cache symptom.",
                "action": {"api": "query_metrics", "args": {"metric_type": "cache_hit_ratio", "target": None}},
            },
            {
                "thinking": "Do not assume shared_buffers is too small; first check memory settings.",
                "action": {"api": "execute_sql", "args": {"sql_query": settings_sql}},
            },
            {
                "thinking": "Now inspect active sessions for a long transaction or cursor with backend_xmin.",
                "action": {"api": "execute_sql", "args": {"sql_query": activity_sql}},
            },
            {
                "thinking": "The suspicious session is an old analytics cursor with backend_xmin. Check dead tuples and vacuum visibility on the hot table.",
                "action": {"api": "execute_sql", "args": {"sql_query": dead_tuple_sql}},
            },
            {
                "thinking": "Confirm the same dead tuple pressure through the SQL-backed table statistics.",
                "action": {"api": "execute_sql", "args": {"sql_query": dead_tuple_sql}},
            },
            {
                "thinking": "Root cause is a long analytics cursor holding an old snapshot and blocking cleanup, not a one-off scan or memory size issue. Terminate the cursor session first.",
                "action": {"api": "execute_sql", "args": {"sql_query": terminate_sql}},
            },
            {
                "thinking": "Allow the terminated cursor session to settle before starting maintenance.",
                "action": {"api": "execute_sql", "args": {"sql_query": settle_sql}},
            },
            {
                "thinking": "With the old snapshot gone, vacuum the hot table so the dead tuple pressure is actually cleared.",
                "action": {"api": "execute_sql", "args": {"sql_query": vacuum_sql}},
            },
            {
                "thinking": "Record recurrence control so future analytics cursors are time-bounded and isolated from OLTP cleanup.",
                "action": {"api": "execute_sql", "args": {"sql_query": mitigation_sql}},
            },
            {
                "thinking": "Validate that the long transaction is gone, dead tuples are cleaned, mitigation is recorded, and cache metrics are recovering.",
                "action": {"api": "execute_sql", "args": {"sql_query": verify_sql}},
            },
            {
                "thinking": "Check the cache metric after mitigation for post-fix validation.",
                "action": {"api": "query_metrics", "args": {"metric_type": "cache_hit_ratio", "target": None}},
            },
            {
                "thinking": "The long cursor was removed and cleanup recovered, so submit.",
                "action": {"api": "submit", "args": {"report": build_success_report(case)}},
            },
        ]
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a PostgreSQL DBA agent.", use_native_tools=False)
        agent.set_mock_responses(mock_responses)
        return agent

    activity_sql = f"""
        SET statement_timeout = '10s';
        SELECT pid, application_name, state, wait_event_type, wait_event,
               now() - query_start AS duration,
               left(query, 220) AS query
        FROM pg_stat_activity
        WHERE datname = current_database()
          AND (application_name IN ('{case.scan_app_name}', '{case.oltp_app_name}')
               OR state = 'active')
        ORDER BY query_start NULLS LAST, application_name;
    """
    settings_sql = """
        SELECT name, setting, unit, source
        FROM pg_settings
        WHERE name IN ('shared_buffers', 'effective_cache_size', 'work_mem')
        ORDER BY name;
    """
    buffers_sql = f"""
        CREATE EXTENSION IF NOT EXISTS pg_buffercache;
        SELECT c.relname, count(*) AS buffers, round(count(*) * 8 / 1024.0, 2) AS mb
        FROM pg_buffercache b
        JOIN pg_class c ON b.relfilenode = pg_relation_filenode(c.oid)
        WHERE c.relname IN ('{case.hot_table}', '{case.archive_table}')
        GROUP BY c.relname
        ORDER BY buffers DESC;
    """
    buffers_verify_sql = f"""
        SELECT c.relname, count(*) AS buffers, round(count(*) * 8 / 1024.0, 2) AS mb
        FROM pg_buffercache b
        JOIN pg_class c ON b.relfilenode = pg_relation_filenode(c.oid)
        WHERE c.relname IN ('{case.hot_table}', '{case.archive_table}')
        GROUP BY c.relname
        ORDER BY buffers DESC;
    """
    fix_sql = f"""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE application_name = '{case.scan_app_name}'
          AND pid <> pg_backend_pid();

        INSERT INTO {case.control_table} (control_name, recommendation)
        VALUES (
            '{case.scan_app_name}',
            'Isolate analytics reporting scans on a read replica or scheduled OLAP window; limit large reporting scans with statement timeout and admission control.'
        )
        ON CONFLICT (control_name)
        DO UPDATE SET recommendation = EXCLUDED.recommendation, applied_at = now();
    """
    verify_sql = f"""
        SELECT pg_sleep(1);
        SELECT application_name, state, count(*)
        FROM pg_stat_activity
        WHERE application_name IN ('{case.scan_app_name}', '{case.oltp_app_name}')
        GROUP BY application_name, state
        ORDER BY application_name, state;

        SELECT control_name, recommendation
        FROM {case.control_table}
        WHERE control_name = '{case.scan_app_name}';
    """
    mock_responses = [
        {
            "thinking": "The alert is a shared-buffer hit ratio drop, so first inspect the cache metric itself.",
            "action": {"api": "query_metrics", "args": {"metric_type": "cache_hit_ratio", "target": None}},
        },
        {
            "thinking": "There may be several business queries in the slow-query list, so inspect it only as a candidate source list before deciding on root cause.",
            "action": {"api": "query_metrics", "args": {"metric_type": "slow_queries", "threshold_ms": 1000}},
        },
        {
            "thinking": "A low hit ratio can be a ambiguous memory symptom; check whether shared_buffers is simply undersized or recently misconfigured.",
            "action": {"api": "execute_sql", "args": {"sql_query": settings_sql}},
        },
        {
            "thinking": "The memory setting is deliberate for this instance, so correlate the time window with active SQL sessions.",
            "action": {"api": "execute_sql", "args": {"sql_query": activity_sql}},
        },
        {
            "thinking": "The reporting reader is repeatedly scanning the archive table. Inspect buffer residency to confirm it is taking shared buffers away from OLTP pages.",
            "action": {"api": "execute_sql", "args": {"sql_query": buffers_sql}},
        },
        {
            "thinking": "The root cause is mixed workload cache displacement, not insufficient memory. Stop the reporting scan and record the isolation/limit mitigation.",
            "action": {"api": "execute_sql", "args": {"sql_query": fix_sql}},
        },
        {
            "thinking": "Validate that the reporting scan is gone, the mitigation is recorded, and cache metrics are recovering.",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": verify_sql}},
                {"api": "query_metrics", "args": {"metric_type": "cache_hit_ratio", "target": None}},
                {"api": "execute_sql", "args": {"sql_query": buffers_verify_sql}},
            ],
        },
        {
            "thinking": "The scan source has been stopped and workload isolation/limits are in place, so submit.",
            "action": {"api": "submit", "args": {"report": build_success_report(case)}},
        },
    ]
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a PostgreSQL DBA agent.", use_native_tools=False)
    agent.set_mock_responses(mock_responses)
    return agent


def build_zero_score_mock_agent():
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a PostgreSQL DBA agent.", use_native_tools=False)
    agent.set_mock_responses([
        {
            "thinking": "Submit without inspecting the database.",
            "action": {"api": "submit", "args": {"report": build_failure_report()}},
        }
    ])
    return agent


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
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Cache Pressure / Cache Pollution Mock Path")
    print("=" * 70)
    scenario = PgQueryPerfCachePollutionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(
        case,
        port,
        container_name,
        image_name=None,
    )
    result, _ = run_with_orchestrator(
        env,
        scenario,
        case,
        build_full_score_mock_agent(case),
        run_config,
        max_turns=12,
    )
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Cache Pressure / Cache Pollution Zero Path")
    print("=" * 70)
    scenario = PgQueryPerfCachePollutionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(
        case,
        port,
        container_name,
        image_name=None,
    )
    result, _ = run_with_orchestrator(
        env,
        scenario,
        case,
        build_zero_score_mock_agent(),
        run_config,
        max_turns=3,
    )
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("zero", result)
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str, port: int, container_name: str, model: str = None,
            config_path: str = "config/llm_config.json",
            max_turns: int = 20,
            run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Cache Pressure / Cache Pollution LLMAgent Path")
    print("=" * 70)
    agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)

    scenario = PgQueryPerfCachePollutionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(
        case,
        port,
        container_name,
        image_name=None,
    )
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("llm", result)
    return passed


def main():
    parser = argparse.ArgumentParser(description="Run the PG cache pollution scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15730)
    parser.add_argument("--container-name", default="aiopsbench-pg-cache-pollution")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgQueryPerfCachePollutionScenario()
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
    container_prefix = f"{args.container_name}-{case.case_id}"

    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(required_run_timeout_seconds())
    try:
        if args.mode == "mock":
            run_mock_full(args.case, args.port, f"{container_prefix}-mock", run_config=run_config)
        elif args.mode == "zero":
            run_mock_zero(args.case, args.port, f"{container_prefix}-zero", run_config=run_config)
        elif args.mode == "llm":
            run_llm(args.case,
                args.port,
                f"{container_prefix}-llm",
                args.model,
                args.config_path,
                args.max_turns,
                run_config=run_config,
            )
        else:
            run_mock_full(args.case, args.port, f"{container_prefix}-mock", run_config=run_config)
            run_mock_zero(args.case, args.port + 1, f"{container_prefix}-zero", run_config=run_config)
            run_llm(args.case,
                args.port + 2,
                f"{container_prefix}-llm",
                args.model,
                args.config_path,
                args.max_turns,
                run_config=run_config,
            )
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
