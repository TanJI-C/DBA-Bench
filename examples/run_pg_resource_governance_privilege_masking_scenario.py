import argparse
import json
import os
import signal
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scenarios.evaluation.base import evaluation_passed
from src.scenarios.runtime.config import required_run_timeout_seconds
from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.scenarios.postgres import PgResourceGovernancePrivilegeMaskingScenario
from src.execution.deployment import PGDockerDeployment
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Read the database-maintained policy, then compare role membership and effective privileges across the affected and approved near-neighbor accounts.",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT principal_role, business_purpose, base_customer_read_allowed, "
                        "sensitive_field_policy, approval_state "
                        "FROM public.customer_access_policy ORDER BY principal_role;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT rolname, rolsuper, rolcreatedb, rolcreaterole, rolcanlogin "
                        "FROM pg_roles "
                        "WHERE rolname IN ('test_dev_user', 'app_user', 'qa_readonly_group', "
                        "'analytics_user', 'analytics_readonly_group') "
                        "ORDER BY rolname;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT member.rolname AS member, parent.rolname AS inherited_role "
                        "FROM pg_auth_members m "
                        "JOIN pg_roles member ON member.oid = m.member "
                        "JOIN pg_roles parent ON parent.oid = m.roleid "
                        "WHERE member.rolname IN ('test_dev_user', 'analytics_user') "
                        "ORDER BY member, inherited_role;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT "
                        "has_table_privilege('test_dev_user', 'public.customer', 'SELECT') AS dev_effective_base_select, "
                        "has_table_privilege('qa_readonly_group', 'public.customer', 'SELECT') AS group_base_select, "
                        "has_table_privilege('app_user', 'public.customer', 'SELECT') AS app_base_select, "
                        "has_table_privilege('analytics_user', 'public.customer', 'SELECT') AS analytics_base_select, "
                        "has_table_privilege('analytics_readonly_group', 'public.customer', 'SELECT') AS analytics_group_base_select;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "Compare the existing partial preview with policy, then prove the review-required role still reads both sensitive fields in clear text.",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT table_schema, table_name, column_name "
                        "FROM information_schema.columns "
                        "WHERE table_schema = 'dev_access' "
                        "ORDER BY table_name, ordinal_position;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT table_schema, table_name, column_name, data_type "
                        "FROM information_schema.columns "
                        "WHERE table_schema = 'public' "
                        "AND table_name = 'customer' "
                        "AND column_name IN ('id_number', 'phone_number') "
                        "ORDER BY column_name;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SET ROLE test_dev_user; "
                        "SELECT customer_id, id_number, phone_number "
                        "FROM public.customer "
                        "ORDER BY customer_id LIMIT 2; "
                        "RESET ROLE;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "Create a complete least-privilege masked view, then remove the inherited clear-text role from the non-production account and grant only the masked view.",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "CREATE SCHEMA IF NOT EXISTS dev_access;"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "CREATE OR REPLACE VIEW dev_access.customer AS "
                        "SELECT customer_id, full_name, "
                        "concat('*******', right(phone_number, 4))::text AS phone_number, "
                        "concat('**************', right(id_number, 4))::text AS id_number, "
                        "email, account_status "
                        "FROM public.customer;"
                    )
                },
            },
            {"api": "execute_sql", "args": {"sql_query": "REVOKE SELECT ON public.customer FROM qa_readonly_group;"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
                        "REVOKE SELECT ON TABLES FROM qa_readonly_group;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "GRANT USAGE ON SCHEMA dev_access TO test_dev_user; "
                        "GRANT SELECT ON dev_access.customer TO test_dev_user; "
                        "ALTER ROLE test_dev_user SET search_path = dev_access, public;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "Verify target-role convergence, complete masking, and preservation of both approved production and fraud-review reads.",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT "
                        "has_table_privilege('test_dev_user', 'public.customer', 'SELECT') AS dev_base_select, "
                        "pg_has_role('test_dev_user', 'qa_readonly_group', 'member') AS still_inherited, "
                        "has_schema_privilege('test_dev_user', 'dev_access', 'USAGE') AS dev_schema_usage, "
                        "has_table_privilege('test_dev_user', 'dev_access.customer', 'SELECT') AS dev_view_select, "
                        "has_table_privilege('app_user', 'public.customer', 'SELECT') AS app_base_select, "
                        "has_table_privilege('analytics_user', 'public.customer', 'SELECT') AS analytics_base_select;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT v.customer_id, v.id_number, v.phone_number, "
                        "v.id_number <> c.id_number AS id_masked, "
                        "v.phone_number <> c.phone_number AS phone_masked "
                        "FROM dev_access.customer v "
                        "JOIN public.customer c USING (customer_id) "
                        "ORDER BY v.customer_id LIMIT 3;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SET ROLE test_dev_user; SET search_path = dev_access, public; "
                        "SELECT customer_id, id_number, phone_number FROM customer ORDER BY customer_id LIMIT 2; "
                        "RESET ROLE;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SET ROLE app_user; "
                        "SELECT customer_id, id_number, phone_number FROM public.customer WHERE customer_id = 1; "
                        "RESET ROLE;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "Privileges are converged and masked access is verified; submit the result.",
        "action": {"api": "submit", "args": {"report": PgResourceGovernancePrivilegeMaskingScenario().get_case('customer_developer_masking').reference_report}},
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


def _case_replacements(case):
    return (
        ("customer_developer_masking", case.case_id),
        ("test_dev_user", case.dev_role),
        ("app_user", case.app_role),
        ("qa_readonly_group", case.inherited_role),
        ("analytics_readonly_group", case.decoy_inherited_role),
        ("analytics_user", case.decoy_role),
        ("customer_access_policy", case.policy_table),
        ("dev_access.customer", f"{case.view_schema}.{case.table}"),
        ("public.customer", f"public.{case.table}"),
        ("table_name = 'customer'", f"table_name = '{case.table}'"),
        ("FROM customer ORDER", f"FROM {case.table} ORDER"),
        ("dev_access", case.view_schema),
    )


def build_full_score_mock_responses(case):
    return _rewrite_strings(FULL_SCORE_MOCK_RESPONSES, _case_replacements(case))


def build_zero_score_mock_responses(case):
    return _rewrite_strings(ZERO_SCORE_MOCK_RESPONSES, _case_replacements(case))


HARD_TIMEOUT_SEC = 420


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    # Custom deployment is only used to provide a neutral isolated container name for parallel runs.
    deployment = PGDockerDeployment(container_name=container_name, port=port, image_name=image_name or case.base_image_name)
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
    print("AiOpsBench PostgreSQL - Privilege Masking Full-Score Mock Path")
    print("=" * 60)

    scenario = PgResourceGovernancePrivilegeMaskingScenario()
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
    print("AiOpsBench PostgreSQL - Privilege Masking Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgResourceGovernancePrivilegeMaskingScenario()
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
    print("AiOpsBench PostgreSQL - Privilege Masking LLMAgent Path")
    print("=" * 60)

    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] Missing or invalid local LLM config: {exc}")
        return 0.0

    scenario = PgResourceGovernancePrivilegeMaskingScenario()
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
    parser = argparse.ArgumentParser(description="Run the PG privilege masking scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15720)
    parser.add_argument("--container-name", default="aiopsbench-pg-security-access")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgResourceGovernancePrivilegeMaskingScenario()
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
    try:
        if args.mode in ("mock", "all"):
            run_mock_full(args.case, args.port, args.container_name, run_config)
        if args.mode in ("zero", "all"):
            run_mock_zero(args.case, args.port, args.container_name, run_config)
        if args.mode in ("llm", "all"):
            run_llm(args.case, args.port, args.container_name, args.model, args.config_path, args.max_turns, run_config=run_config)
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
