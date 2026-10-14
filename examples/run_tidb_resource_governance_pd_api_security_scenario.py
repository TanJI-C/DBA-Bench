import argparse
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import StructuredReport
from src.scenarios.tidb.resource_governance.pd_api_security import (
    RG09_CLUSTER_CONFIG_SQL,
    RG09_CLUSTER_INFO_SQL,
    RG09_CONSUMER_ROUTE_SQL,
    RG09_CONSUMER_ROUTE_SUMMARY_SQL,
    rg09_route_controls,
    rg09_reference_route_controls,
    TidbResourceGovernancePdApiSecurityScenario,
)
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


PASS_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": [
            "Recommended primary control: firewall/iptables network allowlist on the PD client API, permitting only internal TiDB/TiKV, pd-ctl, BR, Lightning, Prometheus, and Grafana sources.",
            "The rollout uses a maintenance change window, validates one PD member and quorum before continuing, and keeps a rollback rule ready.",
        ],
        "verification": [
            "Test an unauthenticated request to the PD API and require 403/denied/blocked, then use authenticated pd-ctl control with the authorized internal path.",
            "Verify cluster_info, PD leader/quorum, TiDB SQL business queries, BR backup/restore, TiDB Lightning, Dashboard, Prometheus, and Grafana after the allowlist change.",
            "Preserve Dashboard traffic visualization and historical search records; export or back up history before any alternate-port migration.",
            "Rollback the firewall rule if SQL, PD control, BR, Lightning, Dashboard, Prometheus, Grafana, leader, or quorum checks fail.",
        ],
        "plan": {
            "primary_control": "network_allowlist",
            "consumer_controls": {
                "pd_api": {"control": "allow internal management clients", "validation": "negative and positive access tests"},
                "pd_control": {"control": "retain authorized control path", "validation": "authenticated control command succeeds"},
                "dashboard": {"control": "keep the current service route", "validation": "live dashboard request succeeds"},
                "br": {"control": "retain the backup route", "validation": "backup and restore smoke checks succeed"},
                "lightning": {"control": "retain the import route", "validation": "precheck and import connectivity succeed"},
                "prometheus": {"control": "retain metrics scrape route", "validation": "targets remain healthy"},
                "grafana": {"control": "retain query route", "validation": "dashboard panels query successfully"},
                "sql_business": {"control": "leave SQL path unchanged", "validation": "business truth is unchanged"},
            },
            "route_controls": rg09_reference_route_controls(),
            "access_validation": {
                "unauthenticated_test": "unauthorized request is denied",
                "authenticated_test": "authorized control request succeeds",
                "health_gates": ["cluster health", "leader", "quorum", "SQL"],
            },
            "history": {
                "disposition": "preserve",
                "mitigation": "export history before any endpoint migration",
            },
            "rollout": {
                "maintenance_window": True,
                "availability_impact": "announce the change window",
                "topology_guardrail": "validate one member and quorum before continuing",
                "rollback_condition": "rollback when any dependency or health gate fails",
            },
        },
    },
    "summary": "The plan preserves authorized operations while closing the exposed management path.",
}
StructuredReport.from_mapping(PASS_REPORT)


MOCK_RESPONSES = [
    {
        "thinking": "先从混合业务、拓扑和管理面配置确认暴露面，再查官方知识中的访问边界和运维可达性约束。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
            {"api": "manage_cluster", "args": {"resource": "service", "operation": "list"}},
            {"api": "execute_sql", "args": {"sql_query": RG09_CLUSTER_CONFIG_SQL}},
            {"api": "execute_sql", "args": {"sql_query": RG09_CLUSTER_INFO_SQL}},
            {"api": "execute_sql", "args": {"sql_query": RG09_CONSUMER_ROUTE_SQL}},
            {"api": "execute_sql", "args": {"sql_query": RG09_CONSUMER_ROUTE_SUMMARY_SQL}},
            {"api": "read_log", "args": {"target": "pd/pd-0", "lines": 200}},
            {
                "api": "search_knowledge",
                "args": {
                    "query": "distributed database management endpoint access boundary operations reachability",
                    "source_scope": "self_managed",
                    "top_k": 5,
                    "kb_type": "configuration",
                    "component": "pd",
                },
            },
        ],
    },
    {
        "thinking": "这是方案设计任务，不直接重启健康组件；用业务查询和依赖验证清单约束安全边界后提交。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT COUNT(*), COALESCE(SUM(account_id), 0) "
                        "FROM benchops_rg09.rg09_accounts"
                    )
                },
            },
            {
                "api": "search_knowledge",
                "args": {
                    "query": "TiDB dashboard endpoint migration multiple members operational consequences",
                    "source_scope": "self_managed",
                    "top_k": 5,
                    "kb_type": "operation",
                    "component": "dashboard",
                },
            },
            {"api": "submit", "args": {"report": PASS_REPORT}},
        ],
    },
]


def build_mock_report(case):
    report = copy.deepcopy(case.reference_report)
    report["outcome"]["plan"]["route_controls"] = rg09_route_controls(case.consumer_route_data)
    return report


def build_mock_responses(case):
    responses = copy.deepcopy(MOCK_RESPONSES)
    for response in responses:
        for action in response.get("actions", ()):
            if action.get("api") == "submit":
                action["args"]["report"] = build_mock_report(case)
    return responses


def main() -> None:
    scenario = TidbResourceGovernancePdApiSecurityScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB RG09 PD API security planning scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=16)
    parser.add_argument("--port", type=int, default=4860)
    parser.add_argument("--container-name", default="tidb-rg09-pd-api-security")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    parser.add_argument(
        "--tool-profile",
        choices=("hierarchical_knowledge", "general_knowledge", "no_knowledge"),
        default="hierarchical_knowledge",
    )
    parser.add_argument("--knowledge-backend", choices=("sqlite", "chroma"), default="sqlite")
    args = parser.parse_args()

    if args.mode == "llm" and not args.model:
        raise ValueError("--model is required when --mode=llm")
    os.environ["AIOPS_TIDB_KB_BACKEND"] = args.knowledge_backend

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        return_window_seconds=300,
    )
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB security and operations DBA.",
            use_native_tools=False,
        )
        agent.set_mock_responses(build_mock_responses(case))
    else:
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
            raise RuntimeError(f"RG09 mock must pass N/A/True/True, observed={observed!r}, result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
