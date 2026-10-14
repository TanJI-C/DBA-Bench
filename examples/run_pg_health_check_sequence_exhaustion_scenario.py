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
from src.scenarios.postgres import PgHealthCheckSequenceExhaustionScenario
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


HARD_TIMEOUT_SEC = 900


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Do not inspect sequence metadata; submit immediately.",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    env = PGEnv(port=port)
    env.deployment.container_name = container_name
    env.deployment.image_name = image_name or case.base_image_name
    return env


def sequence_inventory_query() -> str:
    return """
        SET statement_timeout = '5s';
        SELECT
            ns.nspname AS schema_name,
            seq.relname AS sequence_name,
            tbl.relname AS table_name,
            col.attname AS column_name,
            typ.typname AS data_type,
            ps.last_value,
            dep.deptype,
            pseq.seqtypid::regtype AS sequence_type
        FROM pg_class seq
        JOIN pg_namespace ns ON ns.oid = seq.relnamespace
        JOIN pg_sequence pseq ON pseq.seqrelid = seq.oid
        JOIN pg_sequences ps
          ON ps.schemaname = ns.nspname
         AND ps.sequencename = seq.relname
        LEFT JOIN pg_depend dep
          ON dep.objid = seq.oid
         AND dep.deptype IN ('a', 'i')
        LEFT JOIN pg_class tbl ON tbl.oid = dep.refobjid
        LEFT JOIN pg_attribute col
          ON col.attrelid = tbl.oid
         AND col.attnum = dep.refobjsubid
        LEFT JOIN pg_type typ ON typ.oid = col.atttypid
        WHERE seq.relkind = 'S'
          AND ns.nspname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY ns.nspname, seq.relname;
    """


def capacity_query() -> str:
    return """
        SET statement_timeout = '5s';
        WITH owned_sequences AS (
            SELECT
                ns.nspname AS schema_name,
                seq.relname AS sequence_name,
            tbl.relname AS table_name,
            col.attname AS column_name,
            typ.typname AS data_type,
            ps.last_value,
            dep.deptype
        FROM pg_class seq
        JOIN pg_namespace ns ON ns.oid = seq.relnamespace
        JOIN pg_sequence pseq ON pseq.seqrelid = seq.oid
        JOIN pg_sequences ps
          ON ps.schemaname = ns.nspname
         AND ps.sequencename = seq.relname
        LEFT JOIN pg_depend dep
          ON dep.objid = seq.oid
         AND dep.deptype IN ('a', 'i')
        LEFT JOIN pg_class tbl ON tbl.oid = dep.refobjid
        LEFT JOIN pg_attribute col
          ON col.attrelid = tbl.oid
         AND col.attnum = dep.refobjsubid
        LEFT JOIN pg_type typ ON typ.oid = col.atttypid
        WHERE seq.relkind = 'S'
          AND ns.nspname NOT IN ('pg_catalog', 'information_schema')
    )
        SELECT
            sequence_name,
            table_name,
            column_name,
            data_type,
            last_value,
            CASE
                WHEN data_type IN ('integer', 'int4') THEN 2147483647::numeric
                WHEN data_type IN ('bigint', 'int8') THEN 9223372036854775807::numeric
                WHEN data_type IN ('smallint', 'int2') THEN 32767::numeric
                ELSE NULL
            END AS max_value,
            CASE
                WHEN data_type IN ('integer', 'int4') THEN 2147483647 - last_value
                WHEN data_type IN ('smallint', 'int2') THEN 32767 - last_value
                ELSE NULL
            END AS remaining_values,
            CASE
                WHEN data_type IN ('integer', 'int4') THEN ROUND(last_value::numeric * 100 / 2147483647, 4)
                WHEN data_type IN ('smallint', 'int2') THEN ROUND(last_value::numeric * 100 / 32767, 4)
                ELSE 0
            END AS usage_percent
        FROM owned_sequences
        ORDER BY usage_percent DESC NULLS LAST, sequence_name;
    """


def build_full_score_mock_responses(case) -> list:
    target_sequence = case.sequence_name
    target_table = case.table_name
    target_column = case.column_name
    target_value = case.target_value
    return [
        {
            "thinking": (
                "Start from PostgreSQL logs because the canary reported failed writes, "
                "and filter the noisy log window around the failing write-path sequence."
            ),
            "action": {
                "api": "read_log",
                "args": {"log_type": "pg_log", "match_key": target_sequence},
            },
        },
        {
            "thinking": (
                "Inventory all user-owned sequences with pg_class, pg_depend, "
                "pg_attribute, pg_type, pg_sequence, and pg_sequences.last_value. "
                "Also keep unowned sequences in the result so legacy counters are visible as noise."
            ),
            "action": {"api": "execute_sql", "args": {"sql_query": sequence_inventory_query()}},
        },
        {
            "thinking": (
                f"Calculate sequence capacity. {target_sequence} on {target_table}.{target_column} "
                f"is around {target_value}; integer max is 2147483647, so remaining capacity "
                "is zero and usage_percent is 100%. ledger_batches is BIGINT and safe, "
                "legacy_order_ticket_seq is unowned legacy noise, and report/slow SQL probe tables "
                "are workload noise rather than this write-path capacity risk."
            ),
            "action": {"api": "execute_sql", "args": {"sql_query": capacity_query()}},
        },
        {
            "thinking": (
                f"{target_sequence} is exhausted on {target_table}.{target_column}; submit the "
                "target-bound BIGINT DDL, lock/rewrite risk, migration window, and verification plan "
                "without changing production during this advisory health check."
            ),
            "action": {
                "api": "submit",
                "args": {"report": case.reference_report},
            },
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
    print("AiOpsBench PostgreSQL - Sequence Exhaustion Full-Score Mock Path")
    print("=" * 70)

    scenario = PgHealthCheckSequenceExhaustionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=6)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Sequence Exhaustion Zero-Score Mock Path")
    print("=" * 70)

    scenario = PgHealthCheckSequenceExhaustionScenario()
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
    print("AiOpsBench PostgreSQL - Sequence Exhaustion LLMAgent Path")
    print("=" * 70)

    max_turns = min(max_turns, 30)
    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] Missing or invalid local LLM config: {exc}")
        return 0.0

    scenario = PgHealthCheckSequenceExhaustionScenario()
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
    parser = argparse.ArgumentParser(description="Run the PG sequence exhaustion health-check scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15755)
    parser.add_argument("--container-name", default="aiopsbench-pg-health-37")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgHealthCheckSequenceExhaustionScenario()
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
