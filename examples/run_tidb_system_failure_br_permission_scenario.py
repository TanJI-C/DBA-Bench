import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.scenarios.tidb import TidbSystemFailureBrPermissionScenario
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb.system_failure.runtime.br_permission import BrPermissionEnv
from src.scenarios.evaluation.config import add_diagnosis_arguments
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


SF06_ENABLED_TOOLS = (
    "query_metrics",
    "execute_sql",
    "manage_cluster",
    "read_log",
    "search_knowledge",
    "help",
    "submit",
    "exit",
)


def build_mock_responses(case):
    source_table = f"{case.database}.{case.table}"
    history_table = f"{case.database}.{case.history_table}"
    bindings_table = f"{case.database}.{case.bindings_table}"
    credentials_table = f"{case.database}.{case.credentials_table}"
    return [
        {
            "thinking": "先核对最近的备份作业和对象存储错误，把业务查询噪声与目标 BR 作业分开。",
            "actions": [
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "job",
                        "operation": "get",
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT job_id, database_name, table_name, status, error_text, "
                            "ranges_total, ranges_succeed, ranges_failed, checksum_percent "
                            f"FROM {history_table} ORDER BY started_at DESC, job_id"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT binding_id, target_scope, credential_id, role, binding_state, "
                            "effective_from, effective_to, change_ticket "
                            f"FROM {bindings_table} ORDER BY binding_id LIMIT 200 OFFSET 0"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT binding_id, target_scope, credential_id, role, binding_state, "
                            "effective_from, effective_to, change_ticket "
                            f"FROM {bindings_table} ORDER BY binding_id LIMIT 200 OFFSET 200"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT credential_id, profile_name, scope, storage_uri, access_key, access_key_fingerprint, secret_key, "
                            "status, owner, last_rotated "
                            f"FROM {credentials_table} ORDER BY credential_id LIMIT 200 OFFSET 0"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT grant_id, credential_id, grant_scope, grant_uri, grant_state, valid_from, valid_to, grant_source "
                            "FROM benchops.backup_credential_scope_grants ORDER BY grant_id"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT credential_id, profile_name, scope, storage_uri, access_key, access_key_fingerprint, secret_key, "
                            "status, owner, last_rotated "
                            f"FROM {credentials_table} ORDER BY credential_id LIMIT 200 OFFSET 200"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY "
                            "FROM information_schema.cluster_statements_summary "
                            "ORDER BY SUM_LATENCY DESC LIMIT 50"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT lease_token, assignment_generation, authority_epoch, worker_id, target_scope, storage_uri, desired_binding_id, desired_revision, "
                            "observed_binding_id, observed_revision, observed_material_handle, lease_state, "
                            "valid_from, valid_to, last_heartbeat, change_ref, request_assignment_fence, request_context_token, execution_phase, execution_reason "
                            "FROM benchops.backup_worker_leases ORDER BY lease_id LIMIT 200"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT lease_id, lease_token, assignment_generation, authority_epoch, target_scope, observed_grant_id, desired_grant_id, observed_revision, "
                            "desired_revision, lease_state, valid_from, valid_to, change_ref "
                            ", request_assignment_fence, request_context_token, execution_phase, execution_reason "
                            "FROM benchops.backup_authority_grant_leases ORDER BY lease_id"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT assignment_id, executor_handle, lease_token, assignment_generation, worker_handle, target_scope, valid_from, valid_to, assignment_state "
                            "FROM benchops.backup_worker_registry ORDER BY assignment_id LIMIT 200"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT material_handle, credential_id, target_scope, storage_uri, material_digest, "
                            "material_status, valid_from, valid_to, rotation_source "
                            "FROM benchops.backup_worker_materials ORDER BY valid_from, material_handle"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT dispatch_id, job_id, target_scope, storage_uri, "
                            "dispatch_generation, dispatched_at, released_at, dispatch_state, assignment_phase, assignment_reason "
                            ", request_assignment_fence, request_context_token "
                            "FROM benchops.backup_job_dispatches ORDER BY dispatched_at, dispatch_id"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT route_token, dispatch_id, target_scope, executor_handle, lease_token, route_generation, "
                            "valid_from, valid_to, route_state, assignment_phase, route_reason "
                            ", request_assignment_fence, request_context_token "
                            "FROM benchops.backup_dispatch_routes ORDER BY valid_from, route_token"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT cache_token, route_token, target_scope, worker_handle, material_handle, cache_phase, "
                            "valid_from, valid_to, cache_state, change_ref "
                            ", request_assignment_fence, request_context_token "
                                "FROM benchops.backup_request_material_cache ORDER BY valid_from, cache_token"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT attempt_id, dispatch_id, target_scope, request_context_token, request_assignment_fence, "
                            "request_started_at, event_time, request_stage, execution_phase, execution_reason, "
                            "attempt_sequence, operation_name, attempt_state, access_key_fingerprint, http_status "
                            "FROM benchops.backup_storage_request_attempts ORDER BY dispatch_id, attempt_sequence, attempt_id"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT job_id, target_scope, storage_uri, dispatch_id, "
                            "http_status, access_key_fingerprint, policy_decision, request_stage, request_started_at, event_time "
                            ", request_assignment_fence, request_context_token "
                            "FROM benchops.backup_storage_audit ORDER BY event_time DESC, job_id LIMIT 200"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT COUNT(*), SUM(event_id), "
                            "BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_type, amount, payload))) "
                            f"FROM {source_table}"
                        )
                    },
                },
            ],
        },
        {
            "thinking": "失败 dispatch 的十一个 put_backup_chunk 都使用同一 generation 和 request window；先枚举所有 failed-write candidate，再用 registry、route、worker lease、authority lease、request cache、material/grant 和 lifecycle 的联合 identity 确认 production 403 根因；lease 表的 epoch 列是轮换前的 paper trail，refresh 必须使用控制器事件流上已提升的 live epoch；被拒写触发的存储守卫隔离不随事件流公布释放工单，必须先触发一次拒绝写入，再从守务工单表读取释放身份做有界释放。",
            "actions": [
                *(
                    [
                        {
                            "api": "manage_cluster",
                            "args": {
                                "resource": "job",
                                "operation": "observe",
                            },
                        },
                        {
                            "api": "manage_cluster",
                            "args": {
                                "resource": "job",
                                "operation": "observe",
                                "parameters": {
                                    "start_timestamp": "2026-08-01 23:58:00",
                                    "end_timestamp": "2026-08-01 23:59:55",
                                },
                            },
                        },
                    ]
                    if case.epoch_from_observation
                    else []
                ),
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "job",
                        "operation": "refresh_binding",
                        "target": case.target_worker,
                        "parameters": {
                            "target_scope": f"{case.database}.{case.table}",
                            "request_route_token": "rt-5e7c9b3a1d04",
                            "request_cache_token": "c-7b4d9e1a2f60",
                            "attempt_id": "att-4a7f1c9e",
                            "observed_authority_grant_id": 8,
                            "desired_authority_grant_id": 1,
                            "authority_lease_id": case.target_authority_lease_id,
                            "authority_epoch": case.live_authority_epoch or case.target_authority_epoch,
                            "request_assignment_fence": "af-target-sf06-2330",
                            "request_context_token": "ctx-target-sf06-request",
                            "request_stage": "backup_upload",
                            "assignment_phase": "dispatch_window",
                            "assignment_reason": "storage-write",
                            "cache_phase": "dispatch_window",
                        },
                    },
                },
                *(
                    [
                        {
                            "api": "manage_cluster",
                            "args": {
                                "resource": "job",
                                "operation": "start",
                                "parameters": {
                                    "database": case.database,
                                    "table": case.table,
                                },
                            },
                        },
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    "SELECT ticket_ref, prefix, bucket, guard, "
                                    "triggering_change_ref, issued_at, ticket_state "
                                    f"FROM {case.database}.{case.quarantine_tickets_table} "
                                    "ORDER BY issued_at"
                                )
                            },
                        },
                        {
                            "api": "manage_cluster",
                            "args": {
                                "resource": "job",
                                "operation": "release_prefix_quarantine",
                                "parameters": {
                                    "target_prefix": "br-permission",
                                    "quarantine_ref": case.prefix_quarantine_ref,
                                    "triggering_change_ref": "br-watch-20260801-2330-a1",
                                },
                            },
                        },
                    ]
                    if case.storage_prefix_quarantine
                    else []
                ),
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "job",
                        "operation": "get",
                    },
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "job",
                        "operation": "start",
                        "parameters": {
                            "database": case.database,
                            "table": case.table,
                        },
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT COUNT(*), SUM(event_id), "
                            "BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_type, amount, payload))) "
                            f"FROM {source_table}"
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


def main():
    scenario = TidbSystemFailureBrPermissionScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB SF06 BR permission scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--port", type=int, default=4620)
    parser.add_argument("--container-name", default="aiopsbench-tidb-sf06-br-permission")
    add_diagnosis_arguments(parser)
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = BrPermissionEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        enabled_tools=SF06_ENABLED_TOOLS,
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
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
            max_output_tokens=args.max_output_tokens,
        )
    run_config = OrchestratorRunConfig(
        diagnosis_match_mode=args.diagnosis_match_mode,
        diagnosis_semantic_model=args.diagnosis_semantic_model,
        diagnosis_semantic_config_path=args.diagnosis_semantic_config_path,
    )
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=run_config,
    ).run()
    if args.mode == "mock" and (
        result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]
    ) != (True, True, True):
        raise RuntimeError(f"SF06 full mock path did not pass DP/OP/SP: result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
