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
from src.scenarios.postgres import PgSystemFailureWalAccumulationScenario
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload


TARGET_SLOT = "analytics_backfill_20240620"
PROTECTED_SLOT = "cdc_billing_export_20260705"
DECOY_SLOTS = [
    PROTECTED_SLOT,
    "standby_warm_archive_a",
    "cdc_orders_stream_20260705",
    "nightly_basebackup_20260706",
    "analytics_backfill_20240618",
    "analytics_backfill_20240619_recent_ack",
    "analytics_backfill_20240621_probe",
    "cdc_billing_recent_ack_20260706",
    "billing_export_slot_replay_probe",
]
SLOT_NAMES_SQL = ", ".join(f"'{slot}'" for slot in [TARGET_SLOT] + DECOY_SLOTS)
DECOY_SLOTS_SQL = ", ".join(f"'{slot}'" for slot in DECOY_SLOTS)


FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": (
            "Storage growth and write latency are the user-visible symptoms. "
            "First check disk usage, I/O, and the WAL directory footprint."
        ),
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "disk_usage"}},
            {"api": "query_metrics", "args": {"metric_type": "disk_io"}},
            {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT count(*) AS wal_files, "
                        "pg_size_pretty(coalesce(sum(size), 0)) AS wal_size "
                        "FROM pg_ls_waldir();"
                    )
                },
            },
        ],
    },
    {
        "thinking": (
            "The instance has normal application, reporting, and monitoring noise. "
            "Check top SQL and slow SQL so bulk write/report activity is not mistaken "
            "for the WAL retention blocker."
        ),
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
            {"api": "query_metrics", "args": {"metric_type": "slow_queries", "threshold_ms": 1000}},
        ],
    },
    {
        "thinking": (
            "Before changing anything, rule out common adjacent causes such as "
            "archive/checkpoint trouble."
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT archived_count, failed_count, last_failed_wal "
                        "FROM pg_stat_archiver;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT name, setting FROM pg_settings "
                        "WHERE name IN ('archive_mode', 'archive_command', "
                        "'checkpoint_timeout', 'max_wal_size') ORDER BY name;"
                    )
                },
            },
        ],
    },
    {
        "thinking": (
            "Archiving/checkpoint settings are not the direct retention blocker. "
            "Quantify replication slot retained WAL and distinguish the old "
            "backfill slot from the billing CDC path named in the alert."
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT slot_name, slot_type, active, restart_lsn, wal_status, "
                        "pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) "
                        "AS retained_wal "
                        "FROM pg_replication_slots "
                        f"WHERE slot_name IN ({SLOT_NAMES_SQL}) "
                        "ORDER BY pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) DESC NULLS LAST;"
                    )
                },
            }
        ],
    },
    {
        "thinking": (
            "Only the old analytics backfill slot has a restart_lsn and retained "
            "WAL. Drop that abandoned backfill slot and preserve the billing CDC slot."
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {"sql_query": "SELECT pg_drop_replication_slot('analytics_backfill_20240620');"},
            }
        ],
    },
    {
        "thinking": "Verify the backfill slot is gone, the billing CDC slot remains, and WAL retention is clear.",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "CHECKPOINT;"}},
            {
                "api": "execute_sql",
                "args": {
                        "sql_query": (
                        "SELECT "
                        "count(*) FILTER (WHERE slot_name = 'analytics_backfill_20240620') AS target_slots, "
                        f"count(*) FILTER (WHERE slot_name IN ({DECOY_SLOTS_SQL})) AS protected_slots, "
                        f"count(*) FILTER (WHERE restart_lsn IS NOT NULL AND slot_name NOT IN ({DECOY_SLOTS_SQL})) AS retaining_slots "
                        "FROM pg_replication_slots "
                        f"WHERE slot_name IN ({SLOT_NAMES_SQL});"
                    )
                },
            },
            {"api": "query_metrics", "args": {"metric_type": "disk_usage"}},
            {"api": "submit", "args": {"report": PgSystemFailureWalAccumulationScenario().get_case('analytics_slot_wal_retention').reference_report}},
        ],
    },
]


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Do not diagnose or repair; submit immediately.",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]

def build_simple_full_score_mock_responses(case) -> list:
    stale_names_sql = ", ".join(f"'{name}'" for name in case.stale_slot_names)
    fresh_names_sql = ", ".join(f"'{name}'" for name in case.fresh_slot_names)
    slot_names = case.stale_slot_names + case.fresh_slot_names
    names_sql = ", ".join(f"'{name}'" for name in slot_names)
    stale_drops = " ".join(
        f"SELECT pg_drop_replication_slot('{name}');" for name in case.stale_slot_names
    )
    return [
        {
            "thinking": "先确认增长来自 WAL，并核对低频订单健康探针只是正常背景流量。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "disk_usage"}},
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT count(*) AS wal_files, "
                            "pg_size_pretty(coalesce(sum(size), 0)) AS wal_size "
                            "FROM pg_ls_waldir();"
                        )
                    },
                },
                {"api": "query_metrics", "args": {"metric_type": "workload_activity"}},
            ],
        },
        {
            "thinking": "结合业务登记表的用途与确认时间，比较各槽 active、restart_lsn 和 retained bytes，区分废弃槽与仍被确认的消费槽。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT slot_name, active, restart_lsn, wal_status, "
                            "pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS retained_bytes "
                            "FROM pg_replication_slots "
                            f"WHERE slot_name IN ({names_sql}) "
                            "ORDER BY retained_bytes DESC NULLS LAST;"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT r.slot_name, r.purpose, r.last_ack_at, "
                            "s.active, s.restart_lsn IS NOT NULL AS retaining "
                            "FROM wal_slot_business_registry r "
                            "LEFT JOIN pg_replication_slots s ON s.slot_name = r.slot_name "
                            "ORDER BY r.last_ack_at;"
                        )
                    },
                },
            ],
        },
        {
            "thinking": "只有长期未确认的废弃 analytics/retry 槽在保留 WAL；CDC、standby、recent-ack 与排水中的槽确认新鲜，必须保留。仅删除废弃集合。",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": stale_drops},
            },
        },
        {
            "thinking": "执行 checkpoint，确认废弃槽全部消失且受保护槽保留，然后提交。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "CHECKPOINT;"}},
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT "
                            f"count(*) FILTER (WHERE slot_name IN ({stale_names_sql}) AND restart_lsn IS NOT NULL) AS stale_retaining, "
                            f"count(*) FILTER (WHERE slot_name IN ({fresh_names_sql})) AS fresh_preserved "
                            "FROM pg_replication_slots "
                            f"WHERE slot_name IN ({names_sql});"
                        )
                    },
                },
                {
                    "api": "submit",
                    "args": {"report": case.reference_report},
                },
            ],
        },
    ]


HARD_TIMEOUT_SEC = 420


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    workload = TPCDSWorkload(scale=case.dataset_scale)
    env = PGEnv(workload=workload, port=port)
    env.deployment.container_name = container_name
    env.deployment.image_name = image_name or case.base_image_name
    return env










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
    print("AiOpsBench PostgreSQL - WAL Accumulation Full-Score Mock Path")
    print("=" * 70)

    scenario = PgSystemFailureWalAccumulationScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(
        build_simple_full_score_mock_responses(case)
        if case.case_id == "abandoned_report_slot_wal_retention_simple"
        else FULL_SCORE_MOCK_RESPONSES
    )
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=8)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 70)
    print("AiOpsBench PostgreSQL - WAL Accumulation Zero-Score Mock Path")
    print("=" * 70)

    scenario = PgSystemFailureWalAccumulationScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses([
        {
            "thinking": "Do not diagnose or repair; submit immediately.",
            "action": {
                "api": "submit",
                "args": {"report": EMPTY_REPORT},
            },
        }
    ])
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("zero", result)
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str, port: int, container_name: str, model: str = None,
            config_path: str = "config/llm_config.json",
            max_turns: int = 20, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 70)
    print("AiOpsBench PostgreSQL - WAL Accumulation LLMAgent Path")
    print("=" * 70)

    max_turns = min(max_turns, 30)
    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] {exc}")
        return 0.0

    scenario = PgSystemFailureWalAccumulationScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
            print(
                "[LLMAGENT_BLOCKED] Agent reached max_turns without submit; "
                "increase --max-turns up to 30 and record the trace as a blocker only if submit is still missing."
            )
    print_evaluation_basis("llm", result)
    print(f"[Result] LLMAgent passed={passed}")
    return passed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["mock", "zero", "llm"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-pg-system-failure-wal-accumulation")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgSystemFailureWalAccumulationScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )

    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(required_run_timeout_seconds())

    if args.mode == "mock":
        passed = run_mock_full(args.case, args.port, args.container_name, run_config=run_config)
    elif args.mode == "zero":
        passed = run_mock_zero(args.case, args.port, f"{args.container_name}-zero", run_config=run_config)
    else:
        passed = run_llm(args.case, args.port, args.container_name, model=args.model,
                        config_path=args.config, max_turns=args.max_turns, run_config=run_config)
    print(f"[Result] mode={args.mode}, passed={passed}")


if __name__ == "__main__":
    main()
