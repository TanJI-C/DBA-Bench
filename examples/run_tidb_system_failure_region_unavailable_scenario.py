import argparse
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import StructuredReport
from src.scenarios.tidb import TidbSystemFailureRegionUnavailableScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.evaluation.config import add_diagnosis_arguments
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


SCENARIO = TidbSystemFailureRegionUnavailableScenario()
CASE = SCENARIO.get_case("region_unavailable_pd_network_block")


PASS_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "root_cause",
                "factor": "misleading_region_alert",
                "entity": CASE.table,
                "evidence": [
                    "PD and TiKV node health stayed normal while the Region-unavailable symptom was isolated to one TiDB target"
                ],
            },
            {
                "type": "affected_target",
                "factor": "affected_tidb_target",
                "entity": CASE.affected_tidb_target,
                "evidence": [
        "the comparison TiDB targets served SQL while the affected target failed its control-plane probes"
                ],
            },
            {
                "type": "root_cause",
                "factor": "pd_client_connectivity",
                "entity": CASE.affected_tidb_target,
                "evidence": [
                    "direct SQL to the affected target failed while the comparison target and all PD members remained reachable"
                ],
            },
            {
                "type": "root_cause",
                "factor": "tidb_egress_shadow_exclusion",
                "entity": CASE.affected_tidb_target,
                "evidence": [
                    "tidb-2 OUTPUT has an ACCEPT before each same-destination pd-client-policy REJECT, so the TiDB-side rejects are shadowed"
                ],
            },
            {
                "type": "root_cause",
                "factor": "pd_response_egress_firewall",
                "entity": "pd/pd-0,pd/pd-1,pd/pd-2 -> tidb/tidb-2",
                "evidence": [
                    "each PD OUTPUT rejects response traffic with source port 2379 to tidb-2's current address, matching the failed PD client path"
                ],
            },
            {
                "type": "root_cause",
                "factor": "pd_ingress_shadow_exclusion",
                "entity": CASE.affected_tidb_target,
                "evidence": [
                    "each PD INPUT has a same-source 2379 ACCEPT before the same-source pd-client-policy REJECT, so the inbound reject is shadowed",
                    "the target OUTPUT destination rejects and TiDB PD client logs identify the effective direction",
                ],
            },
            {
                "type": "root_cause",
                "factor": "tidb_stale_egress_boundary",
                "entity": CASE.affected_tidb_target,
                "evidence": [
                    "after all three PD response blocks were allowed, tidb-2 still had a pd-client-stale-policy OUTPUT reject before its client shadow ACCEPT; restarting only tidb-2 cleared that second boundary"
                ],
            },
            {
                "type": "root_cause",
                "factor": "tidb_post_restart_rehydrated_boundary",
                "entity": CASE.affected_tidb_target,
                "evidence": [
                    "after the affected-only restart, a real PD endpoint had a rehydrated generic OUTPUT reject; a second affected-TiDB network allow cleared it"
                ],
            },
            {
                "type": "necessary_exclusion",
                "factor": "pd_region_control_plane_healthy",
                "entity": "pd/pd-0,pd/pd-1,pd/pd-2,tikv",
                "evidence": [
                    "PD membership, TiKV stores, Region status, and the unchanged 100000-row business truth were verified"
                ],
            },
        ]
    },
    "outcome": {
        "changes": [
            "removed only the three PD response OUTPUT blocks to tidb-2 for server port 2379",
            "restarted only the affected TiDB target so its PD client connections were rebuilt and its stale local egress boundary was cleared",
            "removed the post-restart generic affected-TiDB PD egress boundary after verifying the rehydrated policy",
        ],
        "verification": [
            "all TiDB targets executed SQL",
            "the healthy TiDB neighbor retained its single non-causal PD endpoint rule",
            "all PD/TiKV/TiDB containers were running",
            "Region status and the 100000-row business truth matched the baseline on every target",
        ],
    },
    "summary": (
        "The Region-unavailable alert was a misleading symptom of a staged PD response-side block and affected-TiDB policy replay; "
        "the repair restored all three PD response paths, restarted only the affected TiDB, and cleared the rehydrated local boundary without touching shadow policy, healthy stores, or data."
    ),
}
StructuredReport.from_mapping(PASS_REPORT)


MOCK_RESPONSES = [
    {
        "thinking": "先比较各组件状态和两条 TiDB target 的可观测性，确认告警是否真的来自 TiKV。",
        "actions": [
            {"api": "manage_cluster", "args": {"resource": "service", "operation": "list"}},
            {"api": "query_metrics", "args": {"metric_type": "network_io", "target": CASE.affected_tidb_target}},
        ],
    },
    {
        "thinking": "新 target 的控制面日志和定向 SQL 失败，而旧 target 仍服务，继续查 PD client 方向。",
        "actions": [
            {
                "api": "manage_cluster",
                "args": {"resource": "network", "operation": "get", "target": CASE.control_tidb_target},
            },
            {
                "api": "manage_cluster",
                "args": {"resource": "network", "operation": "get", "target": CASE.protected_tidb_target},
            },
            {
                "api": "manage_cluster",
                "args": {"resource": "network", "operation": "get", "target": CASE.affected_tidb_target},
            },
            *[
                {
                    "api": "manage_cluster",
                    "args": {"resource": "network", "operation": "get", "target": target},
                }
                for target in CASE.pd_targets
            ],
            {
                "api": "read_log",
                "args": {"target": CASE.affected_tidb_target, "lines": 600},
            },
            {
                "api": "read_log",
                "args": {"target": CASE.control_tidb_target, "lines": 200},
            },
            {
                "api": "read_log",
                "args": {"target": CASE.protected_tidb_target, "lines": 200},
            },
            {
                "api": "read_log",
                "args": {"target": CASE.pd_targets[0], "lines": 200},
            },
            {
                "api": "read_log",
                "args": {"target": "tikv/tikv-0", "lines": 200},
            },
            {
                "api": "read_log",
                "args": {"target": "tikv/tikv-1", "lines": 200},
            },
            {
                "api": "read_log",
                "args": {"target": "tikv/tikv-2", "lines": 200},
            },
            {"api": "execute_sql", "args": {"sql_query": "SHOW TABLE benchops.ma01_orders REGIONS"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": "SELECT order_id FROM benchops.ma01_orders WHERE order_id = 1",
                    "target": CASE.affected_tidb_target,
                },
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": CASE.business_query, "target": CASE.control_tidb_target},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": CASE.business_query, "target": CASE.protected_tidb_target},
            },
        ],
    },
    {
        "thinking": "需要修复的是三个 PD 到 affected TiDB 的 response-side OUTPUT egress；放行后仍要识别 tidb-2 的 stale local egress boundary。TiDB 同目标 OUTPUT reject 和 PD 同源 INPUT reject 都被前置 allow 覆盖。",
        "actions": [
            *[
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "network",
                        "operation": "update",
                        "target": target,
                        "parameters": {"access": "allow"},
                    },
                }
                for target in CASE.pd_targets
            ],
            {
                "api": "manage_cluster",
                "args": {"resource": "network", "operation": "get", "target": CASE.affected_tidb_target},
            },
            {
                "api": "manage_cluster",
                "args": {
                    "resource": "service",
                    "operation": "restart",
                    "target": CASE.affected_tidb_target,
                },
            },
            {
                "api": "manage_cluster",
                "args": {"resource": "network", "operation": "get", "target": CASE.affected_tidb_target},
            },
            {
                "api": "manage_cluster",
                "args": {
                    "resource": "network",
                    "operation": "update",
                    "target": CASE.affected_tidb_target,
                    "parameters": {"access": "allow"},
                },
            },
        ],
    },
    {
        "thinking": "修复后逐个 target 验证 SQL、Region 状态和业务真值。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": "SELECT order_id FROM benchops.ma01_orders WHERE order_id = 1",
                    "target": CASE.affected_tidb_target,
                },
            },
            {"api": "execute_sql", "args": {"sql_query": CASE.business_query, "target": CASE.affected_tidb_target}},
            {"api": "execute_sql", "args": {"sql_query": CASE.business_query, "target": CASE.control_tidb_target}},
            {"api": "execute_sql", "args": {"sql_query": CASE.business_query, "target": CASE.protected_tidb_target}},
            {"api": "manage_cluster", "args": {"resource": "service", "operation": "list"}},
        ],
    },
    {"thinking": "提交完整的根因、排除项、修复和验收报告。", "action": {"api": "submit", "args": {"report": PASS_REPORT}}},
]


def main() -> None:
    scenario = TidbSystemFailureRegionUnavailableScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB region-unavailable misleading-alert scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=18)
    parser.add_argument("--port", type=int, default=4300)
    parser.add_argument("--container-name", default="tidb-region-unavailable")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    parser.add_argument("--skip-affected-restart", action="store_true")
    add_diagnosis_arguments(parser)
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        dbname=case.db,
        return_window_seconds=300,
    )
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA agent.",
            use_native_tools=False,
        )
        responses = copy.deepcopy(MOCK_RESPONSES)
        if case.case_id != CASE.case_id:
            for response in responses:
                for action in response.get("actions", ()):
                    args_mapping = action.get("args", {})
                    target = args_mapping.get("target")
                    if target in {
                        CASE.affected_tidb_target,
                        CASE.control_tidb_target,
                        CASE.protected_tidb_target,
                    }:
                        replacement = {
                            CASE.affected_tidb_target: case.affected_tidb_target,
                            CASE.control_tidb_target: case.control_tidb_target,
                            CASE.protected_tidb_target: case.protected_tidb_target,
                        }[target]
                        args_mapping["target"] = replacement
                    sql = args_mapping.get("sql_query")
                    if isinstance(sql, str):
                        args_mapping["sql_query"] = (
                            sql.replace(CASE.table, case.table)
                            .replace(CASE.business_query, case.business_query)
                        )
                submit = response.get("action")
                if submit and submit.get("api") == "submit":
                    submit["args"]["report"] = {
                        **PASS_REPORT,
                        "summary": "The focused region-unavailable reference path restored the affected TiDB PD response path and cleared its staged local boundaries without changing healthy data or stores.",
                    }
        if args.skip_affected_restart:
            responses[2]["actions"] = [
                action
                for action in responses[2]["actions"]
                if not (
                    action["api"] == "manage_cluster"
                    and action["args"].get("resource") == "service"
                    and action["args"].get("operation") == "restart"
                )
            ]
        agent.set_mock_responses(responses)
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
            diagnosis_match_mode=args.diagnosis_match_mode,
            diagnosis_semantic_model=args.diagnosis_semantic_model,
            diagnosis_semantic_config_path=args.diagnosis_semantic_config_path,
        ),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (True, True, True):
            raise RuntimeError(f"region-unavailable mock must pass DP/OP/SP, observed={observed!r}, result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
