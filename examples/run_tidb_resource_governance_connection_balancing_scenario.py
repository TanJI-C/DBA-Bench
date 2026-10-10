import argparse
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.tidb import TidbResourceGovernanceConnectionBalancingScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


PASS_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": [
            "changed the checkout, reporting and settlement business pools to least_connections",
            "marked tidb/tidb-0 draining while preserving the identity probe affinity",
        ],
        "verification": [
            "verified all managed business pools balanced connections and zero routed business connections on tidb/tidb-0",
            "verified the identity probe remained on tidb/tidb-2, all endpoints served, workload continuity and unchanged business rows",
        ],
    },
    "summary": "The affected business pools were rebalanced and the old TiDB SQL instance was drained without changing the protected identity probe.",
}
StructuredReport.from_mapping(PASS_REPORT)


SCENARIO = TidbResourceGovernanceConnectionBalancingScenario()
CASE = SCENARIO.get_case("multi_tidb_connection_balance_and_drain")

FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Compare the TiDB instances over the same observation window before changing a routing policy.",
        "actions": [
            {
                "api": "query_metrics",
                "args": {"metric_type": "active_connections", "target": None},
            },
            {
                "api": "query_metrics",
                "args": {"metric_type": "cpu", "target": None},
            },
            {
                "api": "query_metrics",
                "args": {"metric_type": "qps", "target": None},
            },
            {
                "api": "query_metrics",
                "args": {"metric_type": "query_latency", "target": None},
            },
            {
                "api": "manage_cluster",
                "args": {"resource": "service", "operation": "list"},
            },
        ],
    },
    {
        "thinking": "Inspect all router roles, select a policy for the affected business pools, preserve the identity probe affinity, then drain the affected backend.",
        "actions": [
            {
                "api": "manage_cluster",
                "args": {
                    "resource": "router",
                    "operation": "get",
                    "target": "connection-router",
                },
            },
            {
                "api": "manage_cluster",
                "args": {
                    "resource": "router",
                    "operation": "update",
                    "target": "checkout-router",
                    "parameters": {"policy": "least_connections"},
                },
            },
            {
                "api": "manage_cluster",
                "args": {
                    "resource": "router",
                    "operation": "update",
                    "target": "reporting-router",
                    "parameters": {"policy": "least_connections"},
                },
            },
            {
                "api": "manage_cluster",
                "args": {
                    "resource": "router",
                    "operation": "update",
                    "target": "settlement-router",
                    "parameters": {"policy": "least_connections"},
                },
            },
            {
                "api": "manage_cluster",
                "args": {
                    "resource": "router",
                    "operation": "drain",
                    "target": CASE.initial_target,
                },
            },
        ],
    },
    {
        "thinking": "Verify all managed business pools, that old sessions have drained naturally, the backend remains reachable, and the business truth is unchanged.",
        "actions": [
            {
                "api": "manage_cluster",
                "args": {
                    "resource": "router",
                    "operation": "get",
                    "target": "connection-router",
                },
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": CASE.business_query},
            },
            {"api": "submit", "args": {"report": PASS_REPORT}},
        ],
    },
]


def alternate_target_mock_responses(case):
    return [
        {
            "thinking": "从连接分布、服务清单和 router 角色一次性确认承载受影响业务池的后端与保护范围。",
            "actions": [
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "active_connections", "target": None},
                },
                {
                    "api": "manage_cluster",
                    "args": {"resource": "service", "operation": "list"},
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "router",
                        "operation": "get",
                        "target": "connection-router",
                    },
                },
            ],
        },
        {
            "thinking": "把三个业务池切换到 distributing 策略并排水受影响后端，保持 identity probe 亲和与 settlement 连续性。",
            "actions": [
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "router",
                        "operation": "update",
                        "target": "checkout-router",
                        "parameters": {"policy": "least_connections"},
                    },
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "router",
                        "operation": "update",
                        "target": "reporting-router",
                        "parameters": {"policy": "least_connections"},
                    },
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "router",
                        "operation": "update",
                        "target": "settlement-router",
                        "parameters": {"policy": "least_connections"},
                    },
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "router",
                        "operation": "drain",
                        "target": case.initial_target,
                    },
                },
            ],
        },
        {
            "thinking": "复查受管池平衡、后端连续性与业务真值后提交。",
            "actions": [
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "router",
                        "operation": "get",
                        "target": "connection-router",
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.business_query},
                },
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def build_mock_responses(case):
    if case.case_no == 1:
        return alternate_target_mock_responses(case)
    responses = copy.deepcopy(FULL_SCORE_MOCK_RESPONSES)
    for response in responses:
        for action in response.get("actions", ()):
            if action.get("api") == "manage_cluster" and action["args"].get("operation") == "drain":
                action["args"]["target"] = case.initial_target
            if action.get("api") == "execute_sql":
                action["args"]["sql_query"] = case.business_query
            if action.get("api") == "submit":
                action["args"]["report"] = case.reference_report
    return responses


def main() -> None:
    scenario = TidbResourceGovernanceConnectionBalancingScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB RG08 connection balancing and session drain scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--port", type=int, default=4400)
    parser.add_argument("--container-name", default="tidb-rg08-connection-balancing")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(run_id=args.container_name, port_base=args.port, return_window_seconds=300)
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a production TiDB DBA.",
            use_native_tools=False,
        )
        agent.set_mock_responses(build_mock_responses(case))
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (None, True, True):
            raise RuntimeError(
                f"RG08 mock must pass DiagnosisPass=None/OutcomePass=True/SafePass=True, "
                f"observed={observed!r}, result={result!r}"
            )
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
