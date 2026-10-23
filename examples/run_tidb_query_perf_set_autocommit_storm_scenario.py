import argparse
from dataclasses import replace
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import StructuredReport
from src.scenarios.tidb import TidbQueryPerfSetAutocommitStormScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.evaluation.config import add_diagnosis_arguments
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


PASS_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "root_cause",
                "factor": "TiDB SQL/session 前端是主要 CPU 来源，慢业务 SQL、TiKV 和 PD 不是主要瓶颈",
                "entity": "TiDB SQL front end",
                "evidence": ["CPU, request latency, slow query and node observations separate the SQL front end from TiKV and PD"],
            },
            {
                "type": "statement_source",
                "factor": "只有一个 cohort 的 SET autocommit/business ratio 异常，健康 cohort 的相同 fingerprint 只是少量合法 session state traffic",
                "entity": "one deployment cohort compared with three online siblings",
                "evidence": ["cluster statement counts are normalized by business request counts and session identity"],
            },
            {
                "type": "entity_mapping",
                "factor": "通过 CLUSTER_PROCESSLIST 的 resource group/session alias 将异常 statement 映射到具体 deployment cohort",
                "entity": "CLUSTER_PROCESSLIST and runtime_assignments",
                "evidence": ["the resource group and session alias join one cohort to its assignment"],
            },
            {
                "type": "root_cause",
                "factor": "connector, checkout and session lease revisions are correlated with the incident but are not sufficient causes; the live behavior must be explained together with deployment lane, session binding and session lease mode",
                "entity": "runtime assignment and revision state for the affected cohort",
                "evidence": ["the same revision combinations are healthy in the other deployment-state cohorts"],
            },
            {
                "type": "counterfactual",
                "factor": "四个在线 revision 与运行时状态组合构成健康 sibling；只有 canary 与 renew_on_checkout 同时存在时异常，binding 和 checkout 是竞争相关状态",
                "entity": "four online cohort combinations",
                "evidence": ["the lane-only and binding-only siblings keep the same workload without the abnormal ratio"],
            },
            {
                "type": "root_cause",
                "factor": "deployment_lane=canary and session_lease_mode=renew_on_checkout are both required for the persistent session-state reset storm; changing binding or a connector/checkout revision alone does not remove it",
                "entity": "cohort-04 deployment state",
                "evidence": ["changing either state alone leaves the storm while the coordinated stable/steady rollout removes it"],
            },
            {
                "type": "control_plane_reconcile",
                "factor": "runtime_assignments is current state; its connector, checkout, deployment lane, session binding and session lease fields drift from the desired runtime_rollouts generation and reconcile reapplies the desired state",
                "entity": "target runtime rollout and current assignment",
                "evidence": ["runtime_rollouts exposes desired revisions, desired deployment state, generation, applied generation and rollout state"],
            },
            {
                "type": "durable_repair_scope",
                "factor": "a durable repair changes target desired session lease mode or deployment lane in one target rollout; changing only current state, binding, connector or checkout is incomplete",
                "entity": "target rollout boundary and shared revision catalog",
                "evidence": ["the recovery window shows whether both current state fields converge to the desired generation"],
            },
        ]
    },
    "outcome": {
        "changes": ["changed only the affected cohort desired session lease mode to fixed"],
        "verification": ["verified target workload success, zero last setup statements, business truth and protected assignments"],
    },
    "summary": "The only abnormal session-state traffic came from the canary and renew-on-checkout lease interaction in one cohort; a target rollout preserved capacity and business data.",
}
StructuredReport.from_mapping(PASS_REPORT)


NO_INCIDENT_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "observation",
                "factor": "the selected live client combination does not produce the incident signature in this calibration run",
                "entity": "order-maintenance cohort",
                "evidence": ["the target cohort remains within the recovery observation thresholds"],
            }
        ]
    },
    "outcome": {
        "changes": [],
        "verification": ["observed the fixed-resource calibration window"],
    },
    "summary": "Calibration run only; no remediation action was required.",
}
StructuredReport.from_mapping(NO_INCIDENT_REPORT)


def build_mock_responses(
    case,
    repair_mode: str = "coordinated_state",
    ablation_mode: str | None = None,
) -> list[dict]:
    if repair_mode in {"coordinated_state", "coordinated_state_checkout"}:
        repair_sql = (
            f"UPDATE {case.db}.{case.rollouts_table} SET desired_deployment_lane='stable', "
            "desired_session_binding_mode='steady'"
            + (", desired_checkout_revision='h1'" if repair_mode == "coordinated_state_checkout" else "")
            + ", "
            f"generation=generation+1, rollout_state='pending' WHERE cohort_id='{case.target_cohort}'"
        )
        repair_description = (
            "changed only the affected cohort desired deployment lane to stable and session binding mode to steady"
            + (" with the existing checkout revision h1" if repair_mode == "coordinated_state_checkout" else "")
        )
    elif repair_mode == "connector":
        repair_sql = (
            f"UPDATE {case.db}.{case.rollouts_table} SET desired_connector_revision='r1', "
            f"generation=generation+1, rollout_state='pending' WHERE cohort_id='{case.target_cohort}'"
        )
        repair_description = "changed only the affected cohort desired rollout to connector revision r1"
    elif repair_mode == "checkout":
        repair_sql = (
            f"UPDATE {case.db}.{case.rollouts_table} SET desired_checkout_revision='h1', "
            f"generation=generation+1, rollout_state='pending' WHERE cohort_id='{case.target_cohort}'"
        )
        repair_description = "changed only the affected cohort desired rollout to checkout revision h1"
    elif repair_mode == "deployment_lane":
        repair_sql = (
            f"UPDATE {case.db}.{case.rollouts_table} SET desired_deployment_lane='stable', "
            f"generation=generation+1, rollout_state='pending' WHERE cohort_id='{case.target_cohort}'"
        )
        repair_description = "changed only the affected cohort desired deployment lane to stable"
    elif repair_mode == "session_binding":
        repair_sql = (
            f"UPDATE {case.db}.{case.rollouts_table} SET desired_session_binding_mode='steady', "
            f"generation=generation+1, rollout_state='pending' WHERE cohort_id='{case.target_cohort}'"
        )
        repair_description = "changed only the affected cohort desired session binding mode to steady"
    elif repair_mode == "lease":
        repair_sql = (
            f"UPDATE {case.db}.{case.rollouts_table} SET desired_session_lease_mode='fixed', "
            f"generation=generation+1, rollout_state='pending' WHERE cohort_id='{case.target_cohort}'"
        )
        repair_description = "changed only the affected cohort desired session lease mode to fixed"
    elif repair_mode == "shallow_assignment":
        repair_sql = (
            f"UPDATE {case.db}.{case.assignments_table} SET connector_revision='r1' "
            f"WHERE cohort_id='{case.target_cohort}'"
        )
        repair_description = "changed only the current target assignment to connector revision r1"
    elif repair_mode == "none":
        repair_sql = None
        repair_description = "left the live calibration combination unchanged"
    else:
        raise ValueError(
            "unsupported set-autocommit mock repair mode: "
            f"repair_mode={repair_mode!r}, expected one of ('coordinated_state', 'coordinated_state_checkout', 'connector', 'checkout', 'deployment_lane', 'session_binding', 'lease', 'shallow_assignment', 'none')"
        )

    report = (
        PASS_REPORT
        if repair_mode in {"coordinated_state", "coordinated_state_checkout", "deployment_lane", "lease"}
        or ablation_mode == "storm"
        else NO_INCIDENT_REPORT
    )
    statement_summary_sql = (
        "SELECT INSTANCE, RESOURCE_GROUP, STMT_TYPE, DIGEST, DIGEST_TEXT, EXEC_COUNT, "
        "AVG_LATENCY, SUM_LATENCY, AVG_PARSE_LATENCY, AVG_COMPILE_LATENCY, "
        "AVG_PROCESS_TIME, AVG_PROCESSED_KEYS, FIRST_SEEN, LAST_SEEN "
        "FROM information_schema.cluster_statements_summary "
        "ORDER BY EXEC_COUNT DESC LIMIT 200"
    )
    processlist_sql = (
        "SELECT INSTANCE, ID, USER, RESOURCE_GROUP, SESSION_ALIAS, DB, STATE, INFO "
        "FROM information_schema.cluster_processlist "
        "WHERE SESSION_ALIAS <> '' ORDER BY INSTANCE, ID LIMIT 200"
    )
    assignments_sql = (
        f"SELECT cohort_id, service_name, resource_group, session_alias_prefix, traffic_weight, pool_size, "
        f"connector_revision, checkout_revision, enabled, deployment_lane, session_binding_mode, session_lease_mode "
        f"FROM {case.db}.{case.assignments_table} ORDER BY cohort_id"
    )
    connector_sql = (
        f"SELECT revision_id, use_local_session_state, elide_set_autocommits, "
        f"cache_server_configuration, always_send_set_isolation "
        f"FROM {case.db}.{case.connector_table} ORDER BY revision_id"
    )
    checkout_sql = (
        f"SELECT revision_id, reset_mode, reset_count, validation_mode, transaction_boundary_mode "
        f"FROM {case.db}.{case.checkout_table} ORDER BY revision_id"
    )
    revision_catalog_sql = (
        f"SELECT revision_id, revision_kind, scope, owner_cohort_id, session_lease_mode "
        f"FROM {case.db}.{case.revision_catalog_table} ORDER BY revision_id"
    )
    rollouts_sql = (
        f"SELECT cohort_id, desired_connector_revision, desired_checkout_revision, desired_deployment_lane, "
        f"desired_session_binding_mode, desired_session_lease_mode, generation, applied_generation, "
        f"rollout_state, last_reconcile_at FROM {case.db}.{case.rollouts_table} ORDER BY cohort_id"
    )
    actions = []
    if repair_sql is not None:
        actions.append({"api": "execute_sql", "args": {"sql_query": repair_sql}})
    actions.extend([
        {"api": "query_metrics", "args": {"metric_type": "query_latency", "target": None}},
        {"api": "query_metrics", "args": {"metric_type": "active_connections", "target": None}},
        {"api": "submit", "args": {"report": {
            **report,
            "outcome": {
                **report["outcome"],
                "changes": [repair_description],
            },
        }}},
    ])
    return [
    {
        "thinking": "Establish the shared time window and separate service symptoms from component health.",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "cpu", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "qps", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "query_latency", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "active_connections", "target": None}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT TIME, INSTANCE, DIGEST, QUERY, QUERY_TIME FROM information_schema.cluster_slow_query ORDER BY TIME DESC LIMIT 50"}},
            {"api": "manage_cluster", "args": {"resource": "service", "operation": "list"}},
        ],
    },
    {
        "thinking": "Compare raw statement fingerprints and session identities before reading the separate application control tables.",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": statement_summary_sql}},
            {"api": "execute_sql", "args": {"sql_query": processlist_sql}},
            {"api": "execute_sql", "args": {"sql_query": assignments_sql}},
            {"api": "execute_sql", "args": {"sql_query": connector_sql}},
            {"api": "execute_sql", "args": {"sql_query": checkout_sql}},
            {"api": "execute_sql", "args": {"sql_query": revision_catalog_sql}},
            {"api": "execute_sql", "args": {"sql_query": rollouts_sql}},
        ],
    },
    {
        "thinking": "The four assignments form the 2 by 2 client behavior comparison. Observe the fixed-resource result and submit the calibration record.",
        "actions": actions,
    },
    ]


MOCK_SCENARIO = TidbQueryPerfSetAutocommitStormScenario()
MOCK_CASE = MOCK_SCENARIO.get_case("autocommit_storm_cpu_saturation")
FULL_SCORE_MOCK_RESPONSES = build_mock_responses(MOCK_CASE)


def main() -> None:
    scenario = TidbQueryPerfSetAutocommitStormScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB order-maintenance performance scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=18)
    parser.add_argument("--port", type=int, default=4700)
    parser.add_argument("--container-name", default="tidb-set-autocommit-v3")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="off")
    add_diagnosis_arguments(parser)
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    settings = json.loads(os.environ.get("AIOPS_AGENT_SETTINGS", "{}"))
    ablation_mode = settings.get("ablation_mode")
    ablation_assignments = {
        "control": ("r1", "h1", "stable", "steady", "fixed"),
        "a_only": ("r2", "h1", "canary", "steady", "fixed"),
        "b_only": ("r1", "h2", "stable", "rebind", "fixed"),
        "storm": ("r2", "h2", "canary", "rebind", "renew_on_checkout"),
    }
    if ablation_mode is not None:
        if ablation_mode not in ablation_assignments:
            raise ValueError(
                "unsupported set-autocommit ablation mode: "
                f"ablation_mode={ablation_mode!r}, expected={sorted(ablation_assignments)!r}"
            )
        connector_revision, checkout_revision, deployment_lane, session_binding_mode, session_lease_mode = ablation_assignments[ablation_mode]
        case = replace(
            case,
            initial_target_connector_revision=connector_revision,
            initial_target_checkout_revision=checkout_revision,
            initial_target_deployment_lane=deployment_lane,
            initial_target_session_binding_mode=session_binding_mode,
            initial_target_session_lease_mode=session_lease_mode,
        )
    env = TiDBEnv(run_id=args.container_name, port_base=args.port, return_window_seconds=300)
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA agent.",
            use_native_tools=False,
        )
        agent.set_mock_responses(
            build_mock_responses(
                case,
                settings.get("repair_mode", "coordinated_state"),
                ablation_mode=ablation_mode,
            )
        )
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
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
            diagnosis_match_mode=args.diagnosis_match_mode,
            diagnosis_semantic_model=args.diagnosis_semantic_model,
            diagnosis_semantic_config_path=args.diagnosis_semantic_config_path,
        ),
    ).run()
    if (
        args.mode == "mock"
        and settings.get("expect_full_pass", settings.get("repair_mode", "coordinated_state") == "coordinated_state")
        and (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) != (True, True, True)
    ):
        raise RuntimeError(
            "set-autocommit mock must pass DP/OP/SP: "
            f"observed={(result['DiagnosisPass'], result['OutcomePass'], result['SafePass'])!r}, result={result!r}"
        )
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
