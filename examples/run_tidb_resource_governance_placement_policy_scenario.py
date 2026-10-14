import argparse
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbResourceGovernancePlacementPolicyScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig

TARGET_TABLE = "rg04_relation_02"
TARGET_POLICY = "rg04_layout_b"
SERVICE_REGISTRY_TABLE = "rg04_service_registry"
WORKLOAD_CATALOG_TABLE = "rg04_workload_catalog"
RELATION_DIRECTORY_TABLE = "rg04_relation_directory"
ROUTE_LEASE_TABLE = "rg04_route_leases"
ROUTE_ALLOCATION_TABLE = "rg04_route_allocations"
TRAFFIC_ASSIGNMENT_TABLE = "rg04_traffic_assignments"
ROUTE_SEGMENT_TABLE = "rg04_route_segments"
REQUEST_BINDING_TABLE = "rg04_request_route_bindings"
REQUEST_CONTEXT_TABLE = "rg04_request_contexts"
COMPLIANCE_REQUEST_TABLE = "rg04_compliance_requests"


def _placement_observation_actions():
    return [
        {"api": "execute_sql", "args": {"sql_query": "SHOW PLACEMENT"}},
        {"api": "manage_cluster", "args": {"resource": "operator", "operation": "list"}},
    ]


MOCK_RESPONSES = [
    {
        "thinking": "先从 catalog、当前 routing epoch、route lease、route allocation、traffic assignment 和租户 segment 识别 regulated checkout relation，再把 request context 的当前 epoch 与 request binding、allocation 的 generation 精确对齐，排除同一 routing epoch 中尚未提交到当前请求的 generation。",
        "actions": [
            {
                "api": "search_knowledge",
                "args": {
                    "query": (
                        "TiDB 8.1 FOLLOWERS PRIMARY_REGION REGIONS SCHEDULE "
                        "LEADER_CONSTRAINTS FOLLOWER_CONSTRAINTS placement policy semantics"
                    ),
                    "source_scope": "self_managed",
                    "kb_type": "reference",
                    "component": "sql",
                    "top_k": 5,
                },
            },
            {"api": "execute_sql", "args": {"sql_query": "SHOW TABLES FROM test"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT TABLE_NAME, TIDB_PLACEMENT_POLICY_NAME "
                        "FROM INFORMATION_SCHEMA.TABLES "
                        "WHERE TABLE_SCHEMA='test' ORDER BY TABLE_NAME"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": f"SHOW CREATE TABLE test.{TARGET_TABLE}"
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": f"SHOW PLACEMENT FOR TABLE test.{TARGET_TABLE}"
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT request_shape, service_role_code, routing_epoch, context_epoch, context_state, active "
                        f"FROM {REQUEST_CONTEXT_TABLE} ORDER BY request_shape, service_role_code, routing_epoch"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT request_shape, service_role_code, route_id, segment_id, routing_epoch, binding_epoch, binding_rank, active "
                        f"FROM {REQUEST_BINDING_TABLE} ORDER BY request_shape, service_role_code, routing_epoch, binding_rank"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT table_names, query_sample_text "
                        "FROM information_schema.statements_summary "
                        "WHERE query_sample_text LIKE '%tenant_id BETWEEN 10 AND 60%' "
                        "ORDER BY table_names"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT route_id, service_role_code, segment_id, routing_epoch, tenant_start, tenant_end, segment_state, active "
                        f"FROM {ROUTE_SEGMENT_TABLE} ORDER BY route_id, routing_epoch, segment_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT service_role_code, business_purpose, service_class, active "
                        f"FROM {SERVICE_REGISTRY_TABLE} ORDER BY service_role_code"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT service_key, service_role_code, route_id, routing_epoch, active "
                        f"FROM {WORKLOAD_CATALOG_TABLE} ORDER BY service_key, routing_epoch"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT route_id, routing_epoch, relation_name, relation_class, active "
                        f"FROM {RELATION_DIRECTORY_TABLE} ORDER BY route_id, routing_epoch"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT route_id, routing_epoch, lease_state, traffic_class, active "
                        f"FROM {ROUTE_LEASE_TABLE} ORDER BY route_id, routing_epoch"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT route_id, routing_epoch, allocation_epoch, effective_routing_epoch, allocation_state, traffic_class, active "
                        f"FROM {ROUTE_ALLOCATION_TABLE} ORDER BY route_id, routing_epoch, allocation_epoch"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT service_key, service_role_code, route_id, routing_epoch, traffic_scope, claim_state, traffic_share, active "
                        f"FROM {TRAFFIC_ASSIGNMENT_TABLE} ORDER BY service_key, routing_epoch"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT POLICY_NAME, PRIMARY_REGION, REGIONS, CONSTRAINTS, "
                        "LEADER_CONSTRAINTS, FOLLOWER_CONSTRAINTS, LEARNER_CONSTRAINTS, "
                        "SCHEDULE, FOLLOWERS, LEARNERS "
                        "FROM INFORMATION_SCHEMA.PLACEMENT_POLICIES ORDER BY POLICY_NAME"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT request_id, service_role_code, request_shape, routing_epoch, "
                        "jurisdiction, survival_objective, leader_locality_code, required_voters, "
                        "policy_scope, request_state, active "
                        f"FROM {COMPLIANCE_REQUEST_TABLE} ORDER BY request_id"
                    )
                },
            },
            *_placement_observation_actions(),
            {"api": "manage_cluster", "args": {"resource": "service", "operation": "list"}},
            {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
        ],
    },
    {
        "thinking": "两个 role-17 route 的 lease、allocation、traffic assignment 和 tenant range 都是当前合法状态，且 effective routing epoch 相同；必须将 checkout request context_epoch 与 binding_epoch、allocation_epoch 以及当前 routing_epoch 精确对齐，再检查当前 policy、candidate constraints 和 TiKV zone labels，最后检查目标 Region peer 和容量。",
        "actions": [
            {
                "api": "search_knowledge",
                "args": {
                    "query": (
                        "Separate policy definitions from object attachments; table partition "
                        "inheritance; PENDING INPROGRESS SCHEDULED asynchronous convergence"
                    ),
                    "source_scope": "self_managed",
                    "top_k": 5,
                },
            },
            {
                "api": "search_knowledge",
                "args": {
                    "query": (
                        "Validate every target Region: healthy voter peers, domain coverage, "
                        "leader locality, no learner; accepted policy capacity and fault domains"
                    ),
                    "source_scope": "self_managed",
                    "component": "tikv",
                    "top_k": 5,
                },
            },
            {"api": "execute_sql", "args": {"sql_query": "SHOW PLACEMENT LABELS"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT TABLE_NAME, TIDB_PLACEMENT_POLICY_NAME "
                        "FROM INFORMATION_SCHEMA.TABLES "
                        "WHERE TABLE_SCHEMA='test' ORDER BY TABLE_NAME"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT request_shape, service_role_code, routing_epoch, context_epoch, context_state, active "
                        f"FROM {REQUEST_CONTEXT_TABLE} ORDER BY request_shape, service_role_code, routing_epoch"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT request_shape, service_role_code, route_id, segment_id, routing_epoch, binding_epoch, binding_rank, active "
                        f"FROM {REQUEST_BINDING_TABLE} ORDER BY request_shape, service_role_code, routing_epoch, binding_rank"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT table_names, query_sample_text "
                        "FROM information_schema.statements_summary "
                        "WHERE query_sample_text LIKE '%tenant_id BETWEEN 10 AND 60%' "
                        "ORDER BY table_names"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT route_id, service_role_code, segment_id, routing_epoch, tenant_start, tenant_end, segment_state, active "
                        f"FROM {ROUTE_SEGMENT_TABLE} ORDER BY route_id, routing_epoch, segment_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT POLICY_NAME, PRIMARY_REGION, REGIONS, CONSTRAINTS, "
                        "LEADER_CONSTRAINTS, FOLLOWER_CONSTRAINTS, LEARNER_CONSTRAINTS, "
                        "SCHEDULE, FOLLOWERS, LEARNERS "
                        "FROM INFORMATION_SCHEMA.PLACEMENT_POLICIES ORDER BY POLICY_NAME"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT request_id, service_role_code, request_shape, routing_epoch, "
                        "jurisdiction, survival_objective, leader_locality_code, required_voters, "
                        "policy_scope, request_state, active "
                        f"FROM {COMPLIANCE_REQUEST_TABLE} ORDER BY request_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT service_role_code, business_purpose, service_class, active "
                        f"FROM {SERVICE_REGISTRY_TABLE} ORDER BY service_role_code"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT service_key, service_role_code, route_id, routing_epoch, active "
                        f"FROM {WORKLOAD_CATALOG_TABLE} ORDER BY service_key, routing_epoch"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT route_id, routing_epoch, relation_name, relation_class, active "
                        f"FROM {RELATION_DIRECTORY_TABLE} ORDER BY route_id, routing_epoch"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT route_id, routing_epoch, lease_state, traffic_class, active "
                        f"FROM {ROUTE_LEASE_TABLE} ORDER BY route_id, routing_epoch"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT route_id, routing_epoch, allocation_epoch, effective_routing_epoch, allocation_state, traffic_class, active "
                        f"FROM {ROUTE_ALLOCATION_TABLE} ORDER BY route_id, routing_epoch, allocation_epoch"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT service_key, service_role_code, route_id, routing_epoch, traffic_scope, claim_state, traffic_share, active "
                        f"FROM {TRAFFIC_ASSIGNMENT_TABLE} ORDER BY service_key, routing_epoch"
                    )
                },
            },
            {"api": "execute_sql", "args": {"sql_query": "SHOW PLACEMENT"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT r.REGION_ID, p.STORE_ID, p.IS_LEADER, p.IS_LEARNER, "
                        "s.LABEL AS LABEL, "
                        "s.STORE_STATE_NAME, p.STATUS "
                        "FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS r "
                        "JOIN INFORMATION_SCHEMA.TIKV_REGION_PEERS p ON p.REGION_ID=r.REGION_ID "
                        "JOIN INFORMATION_SCHEMA.TIKV_STORE_STATUS s ON s.STORE_ID=p.STORE_ID "
                        f"WHERE r.DB_NAME='test' AND r.TABLE_NAME='{TARGET_TABLE}' "
                        "AND r.IS_INDEX=0 ORDER BY r.REGION_ID, p.STORE_ID"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT STORE_ID, STORE_STATE_NAME, LABEL, CAPACITY, AVAILABLE "
                        "FROM INFORMATION_SCHEMA.TIKV_STORE_STATUS ORDER BY STORE_ID"
                    )
                },
            },
        ],
    },
    {
        "thinking": "将合规表切换到三副本、az-c leader 的现有 policy。",
        "actions": [
            {
                "api": "search_knowledge",
                "args": {
                    "query": (
                        "TiDB 8.1 table-scoped placement repair preserve shared policy "
                        "definitions control-plane rows Store topology and business data"
                    ),
                    "source_scope": "self_managed",
                    "kb_type": "operation",
                    "component": "pd",
                    "top_k": 5,
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"ALTER TABLE test.{TARGET_TABLE} "
                        f"PLACEMENT POLICY={TARGET_POLICY}"
                    )
                },
            },
        ],
    },
    {
        "thinking": "等待第一轮 Region operator，再观察 Placement 是否已经收敛。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(12)"}},
            *_placement_observation_actions(),
        ],
    },
    {
        "thinking": "Placement 仍可能在迁移中，继续等待并重新确认调度状态。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(12)"}},
            *_placement_observation_actions(),
        ],
    },
    {
        "thinking": "再次等待 PD operator 完成，避免只创建 policy 就提前提交。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(12)"}},
            *_placement_observation_actions(),
        ],
    },
    {
        "thinking": "继续等待最后的 learner 完成，随后检查 Placement 收敛、业务结果和保护表。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(12)"}},
            *_placement_observation_actions(),
        ],
    },
    {
        "thinking": "最后的 Region operator 仍可能在处理，继续观察而不是提前提交。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(15)"}},
            *_placement_observation_actions(),
        ],
    },
    {
        "thinking": "确认 Placement 已进入最终状态，再读取业务查询结果。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(15)"}},
            *_placement_observation_actions(),
        ],
    },
    {
        "thinking": "完成最终收敛等待，检查业务结果和保护表未被修改。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(15)"}},
            *_placement_observation_actions(),
        ],
    },
    {
        "thinking": "迁移仍有一个 learner 未完成，延长等待并再次观察 PD 状态。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(30)"}},
            *_placement_observation_actions(),
        ],
    },
    {
        "thinking": "继续等待最后一个 Region operator，不能用业务查询成功替代副本验证。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(30)"}},
            *_placement_observation_actions(),
        ],
    },
    {
        "thinking": "再做一轮完整收敛观察，确认没有 pending learner 后再提交。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(30)"}},
            *_placement_observation_actions(),
        ],
    },
    {
        "thinking": "最终检查 Placement 收敛、业务结果和保护表未被修改。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(15)"}},
            *_placement_observation_actions(),
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT status, COUNT(*) AS orders, SUM(amount) AS gross_amount "
                        f"FROM {TARGET_TABLE} WHERE tenant_id BETWEEN 10 AND 60 "
                        "GROUP BY status ORDER BY status"
                    )
                },
            },
        ],
    },
    {
        "thinking": "最终状态已核对，提交结构化结果。",
        "action": {
            "api": "submit",
            "args": {"report": TidbResourceGovernancePlacementPolicyScenario().get_case('compliance_table_zone_migration').reference_report},
        },
    },
]


def build_mock_responses(case):
    responses = copy.deepcopy(MOCK_RESPONSES)
    for response in responses:
        for action in response.get("actions", ()):
            if action.get("api") == "execute_sql":
                sql = action["args"]["sql_query"]
                action["args"]["sql_query"] = sql.replace(
                    TARGET_TABLE, case.table
                ).replace(TARGET_POLICY, case.target_policy)
            if action.get("api") == "submit":
                action["args"]["report"] = case.reference_report
        action = response.get("action")
        if action is not None:
            if action.get("api") == "execute_sql":
                sql = action["args"]["sql_query"]
                action["args"]["sql_query"] = sql.replace(
                    TARGET_TABLE, case.table
                ).replace(TARGET_POLICY, case.target_policy)
            if action.get("api") == "submit":
                action["args"]["report"] = case.reference_report
    return responses


def main() -> None:
    scenario = TidbResourceGovernancePlacementPolicyScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB RG04 placement-policy scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--port", type=int, default=4300)
    parser.add_argument("--container-name", default="tidb-rg04-placement-policy")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="off")
    parser.add_argument("--storage-key")
    parser.add_argument("--storage-root")
    parser.add_argument("--cold-start-timeout", type=int, default=900)
    parser.add_argument("--warm-start-timeout", type=int, default=300)
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=40)
    args = parser.parse_args()
    if args.mode == "llm" and not args.model:
        parser.error("--model is required when --mode=llm")

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        storage_key=args.storage_key,
        storage_root=args.storage_root,
        tidb_readiness_timeout_sec=args.cold_start_timeout,
        warm_tidb_readiness_timeout_sec=args.warm_start_timeout,
        return_window_seconds=300,
    )
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA agent.",
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
        expected = (None, True, True)
        actual = (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"])
        if actual != expected:
            raise RuntimeError(f"RG04 mock path did not fully pass: expected={expected}, actual={actual}, result={result!r}")


if __name__ == "__main__":
    main()
