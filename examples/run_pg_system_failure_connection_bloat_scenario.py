import argparse
import json
import os
import signal
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scenarios.runtime.config import required_run_timeout_seconds
from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.postgres import PgSystemFailureConnectionBloatScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.evaluation.config import add_diagnosis_arguments
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


HARD_TIMEOUT_SEC = 720


def build_report(case, success):
    factors = (
        "connection pool exhaustion",
        "dead tuple table bloat",
        "idle transaction holds old snapshot",
        "old snapshot causes bloat and connection exhaustion",
        "orphaned prepared transaction also pins the vacuum horizon",
        "terminate blocker then vacuum",
    ) if success else ()
    return {
        "diagnosis": {"conditions": [
            {"type": "finding", "factor": factor, "entity": case.table, "evidence": [f"observed {factor}"]}
            for factor in factors
        ]},
        "outcome": {
            "changes": ([f"terminated {case.blocker_app_name}, rolled back {case.orphan_prepared_gid}, and vacuumed {case.table}"] if success else []),
            "verification": (["old transaction, prepared xact, dead tuples, and worker connections cleared"] if success else []),
        },
        "summary": "An old snapshot and an orphan prepared transaction caused bloat, slow queries, and connection exhaustion." if success else "No diagnosis was attempted.",
    }


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(
    case,
    port: int,
    container_name: str,
    image_name: str = None,
    tool_profile: str = None,
) -> PGEnv:
    # Low max_connections is required to reproduce normal-client rejection while
    # preserving reserved superuser slots for the agent's administrative channel.
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        postgres_runtime_options=(
            f"-c max_connections={case.max_connections} "
            f"-c superuser_reserved_connections={case.superuser_reserved_connections} "
            "-c max_prepared_transactions=10 "
            "-c shared_preload_libraries=pg_stat_statements"
        ),
        image_name=image_name or case.base_image_name,
    )
    env_kwargs = {"workload": None, "deployment": deployment, "port": port}
    if tool_profile:
        env_kwargs["tool_profile"] = tool_profile
    return PGEnv(**env_kwargs)


def _json_result(raw):
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return {"status": "error", "raw": raw}










def build_full_score_mock_responses(scenario: PgSystemFailureConnectionBloatScenario) -> list:
    activity_sql = f"""
        SET statement_timeout = '10s';
        SELECT pid, application_name, state, wait_event_type, wait_event,
               now() - xact_start AS xact_age,
               now() - query_start AS query_age,
               backend_xmin,
               left(query, 180) AS query
        FROM pg_stat_activity
        WHERE backend_type = 'client backend'
          AND pid <> pg_backend_pid()
        ORDER BY xact_start NULLS LAST, application_name;
    """
    bloat_sql = """
        SET statement_timeout = '10s';
        SELECT s.relname, s.n_live_tup, s.n_dead_tup,
               round(s.n_dead_tup::numeric / NULLIF(s.n_live_tup + s.n_dead_tup, 0), 4) AS dead_ratio,
               pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
               s.last_vacuum, s.last_autovacuum
        FROM pg_stat_user_tables s
        JOIN pg_class c ON c.oid = s.relid
        ORDER BY s.n_dead_tup DESC;
    """
    terminate_sql = f"""
        SET statement_timeout = '10s';
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE application_name = '{scenario.blocker_app_name}'
          AND state = 'idle in transaction'
          AND pid <> pg_backend_pid();
    """
    verify_sql = f"""
        SET statement_timeout = '10s';
        SELECT
            (SELECT count(*) FROM pg_stat_activity
             WHERE application_name = '{scenario.blocker_app_name}'
               AND state = 'idle in transaction') AS old_sessions,
            (SELECT count(*) FROM pg_stat_activity
             WHERE application_name LIKE '{scenario.worker_app_prefix}%') AS worker_sessions,
            (SELECT COALESCE(n_dead_tup, 0)
             FROM pg_stat_user_tables
             WHERE relname = '{scenario.table}') AS dead_tuples,
            (SELECT coalesce(string_agg(application_name || ':' || backend_xmin::text, ', '), 'none')
             FROM pg_stat_activity WHERE backend_xmin IS NOT NULL) AS xmin_holders,
            (SELECT coalesce(string_agg(gid, ', '), 'none') FROM pg_prepared_xacts) AS prepared_gids;
    """
    prepared_xact_probe_sql = """
        SET statement_timeout = '10s';
        SELECT gid, owner, database, prepared
        FROM pg_prepared_xacts
        ORDER BY prepared;
    """
    rollback_prepared_sql = (
        f"ROLLBACK PREPARED '{scenario.orphan_prepared_gid}';"
        if scenario.orphan_prepared_gid
        else None
    )
    repair_actions = [
        {
            "thinking": (
                "The source is the old idle transaction holding backend_xmin. "
                "Terminate only that backend, then check for any other vacuum-horizon holder."
            ),
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": terminate_sql}},
                {"api": "execute_sql", "args": {"sql_query": prepared_xact_probe_sql}},
            ],
        },
    ]
    if rollback_prepared_sql:
        repair_actions.append(
            {
                "thinking": (
                    "An orphaned prepared transaction also pins the horizon; release it, "
                    "give the remaining short in-flight snapshots a moment to age out, "
                    "then vacuum the affected table. Keep each statement a separate "
                    "single-statement call so VACUUM never lands in an implicit transaction."
                ),
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": rollback_prepared_sql}},
                    {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(3);"}},
                    {"api": "execute_sql", "args": {"sql_query": f"VACUUM {scenario.table};"}},
                ],
            }
        )
    else:
        repair_actions.append(
            {
                "thinking": (
                    "No other horizon holder remains. Run VACUUM on the affected table."
                ),
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"VACUUM {scenario.table};"}},
                ],
            }
        )
    return [
        {
            "thinking": (
                "New sessions are failing and existing requests are slow. "
                "First inspect connection pressure and table cleanup metrics."
            ),
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "active_connections", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "dead_tuples", "target": None, "tables": scenario.table}},
            ],
        },
        {
            "thinking": (
                "Connection pressure is real. Inspect pg_stat_activity to see what is occupying "
                "sessions and whether an old transaction is holding a snapshot."
            ),
            "action": {"api": "execute_sql", "args": {"sql_query": activity_sql}},
        },
        {
            "thinking": (
                "The connection pile-up aligns with repeated heap scans over a table with "
                "many dead tuples. Confirm bloat metadata and the scan plan."
            ),
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": bloat_sql}},
                {"api": "execute_sql", "args": {"sql_query": f"SET statement_timeout = '20s'; EXPLAIN ANALYZE {scenario.diagnostic_query}"}},
            ],
        },
        *repair_actions,
        {
            "thinking": "Verify that the old session is gone, dead tuples are cleaned, and worker sessions released.",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "active_connections", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "dead_tuples", "target": None, "tables": scenario.table}},
                {"api": "execute_sql", "args": {"sql_query": verify_sql}},
                {"api": "submit", "args": {"report": build_report(scenario, True)}},
            ],
        },
    ]


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
    print("AiOpsBench PostgreSQL - Connection Exhaustion + Bloat Full-Score Mock Path")
    print("=" * 70)
    scenario = PgSystemFailureConnectionBloatScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(
        case,
        port,
        container_name,
        image_name=None,
    )
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=8)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Connection Exhaustion + Bloat Zero-Score Mock Path")
    print("=" * 70)
    scenario = PgSystemFailureConnectionBloatScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(
        case,
        port,
        container_name,
        image_name=None,
    )
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses([
        {
            "thinking": "Run an unrelated destructive DDL instead of diagnosing safely.",
            "action": {"api": "execute_sql", "args": {"sql_query": "DROP TABLE IF EXISTS unrelated_zero_probe;"}},
        },
        {
            "thinking": "Do not inspect or change the database; submit immediately.",
            "action": {"api": "submit", "args": {"report": build_report(case, False)}},
        },
    ])
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
            dbot_tool_profile: str = "general_knowledge",
            max_output_tokens: int = None) -> float:
    print("=" * 70)
    print(f"AiOpsBench PostgreSQL - Connection Exhaustion + Bloat {agent_name.upper()}Agent Path")
    print("=" * 70)
    max_turns = min(max_turns, 30)
    try:
        agent = build_agent(
            agent_name=agent_name,
            model=model,
            config_path=config_path,
            dbaiops_graph=dbaiops_graph,
            max_output_tokens=max_output_tokens,
        )
    except (ValueError, RuntimeError) as exc:
        raise RuntimeError(
            f"Failed to initialize agent={agent_name!r}, model={model!r}, "
            f"config_path={config_path!r}: {exc}"
        ) from exc

    tool_profile = dbot_tool_profile if agent_name == "dbot" else None

    scenario = PgSystemFailureConnectionBloatScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(
        case,
        port,
        container_name,
        image_name=None,
        tool_profile=tool_profile,
    )
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
        print(f"[{agent_name.upper()}AGENT_BLOCKED] Agent reached max_turns without submit; this run is a blocker, not a pass.")
    print_evaluation_basis(agent_name, result)
    print(f"[Result] {agent_name.upper()}Agent passed={passed}")
    return passed


def build_agent(
    agent_name: str,
    model: str = None,
    config_path: str = "config/llm_config.json",
    dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
    max_output_tokens: int = None,
):
    return build_experiment_agent(
        model=model,
        config_path=config_path,
        use_native_tools=True,
        max_output_tokens=max_output_tokens,
    )


def main():
    parser = argparse.ArgumentParser(description="Run the PG connection exhaustion + long transaction + bloat scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15720)
    parser.add_argument("--container-name", default="aiopsbench-pg-system-failure-connection-bloat")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot. Default: general_knowledge.")
    scenario_definition = PgSystemFailureConnectionBloatScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    add_diagnosis_arguments(parser)
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
        runtime_warmup_seconds=3,
        diagnosis_match_mode=args.diagnosis_match_mode,
        diagnosis_semantic_model=args.diagnosis_semantic_model,
        diagnosis_semantic_config_path=args.diagnosis_semantic_config_path,
    )
    container_prefix = f"{args.container_name}-{args.case}"

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
                agent_name=args.agent,
                dbaiops_graph=args.dbaiops_graph,
                dbot_tool_profile=args.dbot_tool_profile,
                max_output_tokens=args.max_output_tokens,
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
                agent_name=args.agent,
                dbaiops_graph=args.dbaiops_graph,
                dbot_tool_profile=args.dbot_tool_profile,
            )
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
