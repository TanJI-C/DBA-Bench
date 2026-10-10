import argparse
import json
import os
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.base import evaluation_passed
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.scenarios.postgres import PgResourceGovernanceAuditLoggingScenario
from src.execution.deployment import PGDockerDeployment
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "First check write I/O and transaction rate to confirm the symptom is write amplification under active traffic.",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "qps", "target": None}},
        ],
    },
    {
        "thinking": "Inspect logging and audit-related runtime settings to see whether recent compliance logging is too broad.",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT name, setting, source "
                    "FROM pg_settings "
                    "WHERE name IN ('log_statement', 'log_min_duration_statement') "
                    "UNION ALL "
                    "SELECT 'pgaudit.log', current_setting('pgaudit.log', true), 'runtime' "
                    "UNION ALL "
                    "SELECT 'pgaudit.role', current_setting('pgaudit.role', true), 'runtime';"
                )
            },
        },
    },
    {
        "thinking": "Tie the write amplification to PostgreSQL log growth, then check WAL/data-page stats so the root cause is not mistaken for checkpoint or table writes.",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT (pg_stat_file('/var/log/postgresql/postgresql.log')).size AS pg_log_bytes; "
                        "SELECT wal_bytes, wal_records FROM pg_stat_wal; "
                        "SELECT buffers_checkpoint, buffers_clean, buffers_backend FROM pg_stat_bgwriter;"
                    )
                },
            },
            {"api": "read_log", "args": {"log_type": "pg_log", "lines": 40}},
        ],
    },
    {
        "thinking": "Keep compliance coverage but stop full statement auditing: scope audit classes and bind object audit to the compliance role.",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "ALTER SYSTEM SET pgaudit.log = 'write, ddl, role';"}},
            {"api": "execute_sql", "args": {"sql_query": "ALTER SYSTEM SET pgaudit.role = 'compliance_audit_role';"}},
            {"api": "execute_sql", "args": {"sql_query": "ALTER SYSTEM SET log_statement = 'none';"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT pg_reload_conf();"}},
        ],
    },
    {
        "thinking": "Verify scoped configuration is active and the checkout table is still serving traffic.",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT current_setting('pgaudit.log', true), "
                        "current_setting('pgaudit.role', true), "
                        "current_setting('log_statement', true);"
                    )
                },
            },
            {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "qps", "target": None}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT amount FROM audit_orders WHERE id = 42;"}},
        ],
    },
    {
        "thinking": "Audit logging is now scoped and business traffic is still healthy; submit the result.",
        "action": {"api": "submit", "args": {"report": PgResourceGovernanceAuditLoggingScenario().get_case('audit_orders_role_logging').reference_report}},
    },
]


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "I will run an unrelated DDL instead of diagnosing safely.",
        "action": {"api": "execute_sql", "args": {"sql_query": "DROP TABLE IF EXISTS unrelated_zero_probe;"}},
    },
    {
        "thinking": "I will submit without diagnosis or repair.",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def _rewrite_strings(value, replacements):
    if isinstance(value, str):
        for old, new in replacements:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [_rewrite_strings(item, replacements) for item in value]
    if isinstance(value, tuple):
        return tuple(_rewrite_strings(item, replacements) for item in value)
    if isinstance(value, dict):
        return {
            _rewrite_strings(key, replacements): _rewrite_strings(item, replacements)
            for key, item in value.items()
        }
    return value


def build_full_score_mock_responses(case):
    replacements = (
        ("audit_orders_role_logging", case.case_id),
        ("compliance_audit_role", case.audit_role),
        ("audit_orders", case.table),
    )
    return _rewrite_strings(FULL_SCORE_MOCK_RESPONSES, replacements)


def build_zero_score_mock_responses(case):
    return _rewrite_strings(
        ZERO_SCORE_MOCK_RESPONSES,
        (("audit_orders_role_logging", case.case_id),),
    )


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        image_name=image_name or case.base_image_name,
        postgres_runtime_options=case.runtime.parameters.as_command_line(),
    )
    return PGEnv(workload=None, deployment=deployment, port=port)






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
    print("AiOpsBench PostgreSQL - Audit Logging Full-Score Mock Path")
    print("=" * 60)

    scenario = PgResourceGovernanceAuditLoggingScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=10)
    passed = evaluation_passed(result)
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Audit Logging Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgResourceGovernanceAuditLoggingScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_zero_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = evaluation_passed(result)
    print_evaluation_basis("zero", result)
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str, port: int, container_name: str, model: str = None,
            config_path: str = "config/llm_config.json",
            max_turns: int = 20, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Audit Logging LLMAgent Path")
    print("=" * 60)

    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] Missing or invalid local LLM config: {exc}")
        return 0.0

    scenario = PgResourceGovernanceAuditLoggingScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = evaluation_passed(result)
    if not any(action.get("api") == "submit" for action in action_history):
            print(
                "[LLMAGENT_BLOCKED] Agent reached max_turns without submit; "
                "increase --max-turns up to 30 and record this run as a blocker only if submit is still missing."
            )
    print_evaluation_basis("llm", result)
    print(f"[Result] LLMAgent passed={passed}")
    return passed


def main():
    parser = argparse.ArgumentParser(description="Run the PG audit logging performance tuning scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15710)
    parser.add_argument("--container-name", default="aiopsbench-pg-resource-audit")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgResourceGovernanceAuditLoggingScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )

    if args.mode in ("mock", "all"):
        run_mock_full(args.case, args.port, args.container_name, run_config)
    if args.mode in ("zero", "all"):
        run_mock_zero(args.case, args.port, args.container_name, run_config)
    if args.mode in ("llm", "all"):
        run_llm(args.case, args.port, args.container_name, args.model, args.config_path, args.max_turns, run_config=run_config)


if __name__ == "__main__":
    main()
