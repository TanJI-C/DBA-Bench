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
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgHealthCheckCapacityTrendScenario
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


HARD_TIMEOUT_SEC = 900


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Skip the health-check analysis and submit immediately.",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    env = PGEnv(
        workload=None,
        port=port,
        allow_sampler_jitter=True,
        allow_sampler_reconnect=True,
    )
    env.deployment.container_name = container_name
    env.deployment.image_name = image_name or case.base_image_name
    return env


def build_full_score_mock_responses(case) -> list:
    sample_table = case.sample_table
    review_table = case.review_table
    target_table = case.target_table
    review_key = case.review_key

    queue_sql = f"""
        SET statement_timeout = '10s';
        SELECT check_key, status, opened_at
        FROM {review_table}
        WHERE status = 'open'
        ORDER BY opened_at;
    """
    history_sql = f"""
        SET statement_timeout = '10s';
        SELECT observed_at::date, used_mb, total_mb, persistent_mb,
               database_mb, index_mb, archive_mb, pg_wal_mb, temp_mb,
               reporting_batch_mb, backup_residue_mb, maintenance_reclaimed_mb,
               note
        FROM {sample_table}
        WHERE check_key = '{review_key}' AND record_type = 'storage_sample'
        ORDER BY observed_at;
    """
    regression_sql = f"""
        SET statement_timeout = '10s';
        WITH base AS (
            SELECT
                observed_at,
                used_mb,
                persistent_mb,
                total_mb,
                EXTRACT(EPOCH FROM (observed_at - min(observed_at) OVER())) / 86400.0 AS day_no
            FROM {sample_table}
            WHERE check_key = '{review_key}' AND record_type = 'storage_sample'
        ),
        stats AS (
            SELECT
                regr_slope(persistent_mb, day_no) AS daily_growth_mb,
                regr_r2(persistent_mb, day_no) AS confidence_r2,
                max(total_mb) AS total_mb,
                (array_agg(persistent_mb ORDER BY observed_at DESC))[1] AS latest_persistent_mb,
                max(used_mb - persistent_mb) AS max_transient_mb
            FROM base
        )
        SELECT
            round(daily_growth_mb::numeric, 2) AS daily_growth_mb,
            round(((total_mb - latest_persistent_mb) / NULLIF(daily_growth_mb, 0))::numeric, 2) AS predicted_full_days,
            round(confidence_r2::numeric, 4) AS confidence_r2,
            round(max_transient_mb::numeric, 2) AS max_transient_mb
        FROM stats;
    """
    finding_sql = f"""
        SET statement_timeout = '10s';
        SELECT record_type, subject, current_mb, thirty_day_growth_mb,
               trend_mb_per_day, reclaimable_mb, persistent_capacity_risk, note
        FROM {sample_table}
        WHERE check_key = '{review_key}' AND record_type <> 'storage_sample'
        ORDER BY persistent_capacity_risk DESC, trend_mb_per_day DESC, current_mb DESC;
    """
    report_sql = f"""
        SET statement_timeout = '10s';
        UPDATE {review_table}
        SET status = 'action_required',
            closed_at = NOW(),
            measured_change_mb_per_day = round(forecast.daily_growth_mb::numeric, 2),
            risk_window_days = round(forecast.predicted_full_days::numeric, 2),
            confidence_score = round(forecast.confidence_r2::numeric, 4),
            risk_source = '{target_table}',
            dismissed_signals = 'Transient reporting/temp spikes, WAL bursts, backup residue, monitoring probes, historical slow SQL, and maintenance cleanup were separated from persistent capacity risk.',
            action_plan = 'Persistent capacity grows ' || round(forecast.daily_growth_mb::numeric, 2)::text ||
                ' MB/day and reaches capacity in ' || round(forecast.predicted_full_days::numeric, 1)::text ||
                ' days; expand storage before that window, partition and archive {target_table} cold events, keep backup residue cleanup on retention policy, and verify usage after cleanup.'
        FROM (
            WITH base AS (
                SELECT
                    observed_at,
                    persistent_mb,
                    total_mb,
                    EXTRACT(EPOCH FROM (observed_at - min(observed_at) OVER())) / 86400.0 AS day_no
                FROM {sample_table}
                WHERE check_key = '{review_key}' AND record_type = 'storage_sample'
            ),
            stats AS (
                SELECT
                    regr_slope(persistent_mb, day_no) AS daily_growth_mb,
                    regr_r2(persistent_mb, day_no) AS confidence_r2,
                    max(total_mb) AS total_mb,
                    (array_agg(persistent_mb ORDER BY observed_at DESC))[1] AS latest_persistent_mb
                FROM base
            )
            SELECT
                daily_growth_mb,
                (total_mb - latest_persistent_mb) / NULLIF(daily_growth_mb, 0) AS predicted_full_days,
                confidence_r2
            FROM stats
        ) AS forecast
        WHERE {review_table}.check_key = '{review_key}';
    """
    verify_sql = f"""
        SET statement_timeout = '5s';
        SELECT check_key, status, measured_change_mb_per_day, risk_window_days,
               confidence_score, risk_source, dismissed_signals, action_plan
        FROM {review_table}
        WHERE check_key = '{review_key}';
    """

    return [
        {
            "thinking": "Start with live disk telemetry and list the open health-check queue item.",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "disk_usage", "target": None}},
                {"api": "execute_sql", "args": {"sql_query": queue_sql}},
            ],
        },
        {
            "thinking": "Inspect the historical records for the open review item.",
            "action": {"api": "execute_sql", "args": {"sql_query": history_sql}},
        },
        {
            "thinking": "Use the persistent component for trend math so transient spikes do not drive the forecast.",
            "action": {"api": "execute_sql", "args": {"sql_query": regression_sql}},
        },
        {
            "thinking": "Review mixed health-check records and classify persistent capacity risk versus routine activity.",
            "action": {"api": "execute_sql", "args": {"sql_query": finding_sql}},
        },
        {
            "thinking": "Close the review queue row with the forecast and production action plan.",
            "action": {"api": "execute_sql", "args": {"sql_query": report_sql}},
        },
        {
            "thinking": "Verify the closed review row, then submit.",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": verify_sql}},
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def _json_result(raw):
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return {"status": "error", "raw": raw}






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
    print("AiOpsBench PostgreSQL - Capacity Trend Full-Score Mock Path")
    print("=" * 70)

    scenario = PgHealthCheckCapacityTrendScenario()
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
    print("AiOpsBench PostgreSQL - Capacity Trend Zero-Score Mock Path")
    print("=" * 70)

    scenario = PgHealthCheckCapacityTrendScenario()
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
    print("AiOpsBench PostgreSQL - Capacity Trend LLMAgent Path")
    print("=" * 70)

    max_turns = min(max_turns, 30)
    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] Missing or invalid local LLM config: {exc}")
        return 0.0

    scenario = PgHealthCheckCapacityTrendScenario()
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
    parser = argparse.ArgumentParser(description="Run the PG capacity trend health-check scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15742)
    parser.add_argument("--container-name", default="aiopsbench-pg-health-capacity")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgHealthCheckCapacityTrendScenario()
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
