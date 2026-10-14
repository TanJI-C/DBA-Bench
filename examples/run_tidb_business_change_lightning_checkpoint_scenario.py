import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbBusinessChangeLightningCheckpointScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator


CASE_ID = "lightning_checkpoint_scale_out"
SCENARIO = TidbBusinessChangeLightningCheckpointScenario()
CASE = SCENARIO.get_case(CASE_ID)


def _partition_resume_mock_responses(case):
    control = f"{case.database}.{case.control_table}"
    request = f"{case.database}.{case.request_table}"
    plan = f"{case.database}.{case.capacity_plan_table}"
    reservation = f"{case.database}.{case.capacity_reservation_table}"
    manifest = f"{case.database}.{case.checkpoint_manifest_table}"
    lease = f"{case.database}.{case.lease_journal_table}"
    gate = f"{case.database}.{case.resume_gate_table}"
    target = f"{case.database}.{case.table}"
    return [
        {
            "thinking": "用一次关联读取把控制面状态、容量计划、reservation、manifest 和 lease 的 token 对齐证据收敛为唯一的兼容候选。",
            "actions": [
                {"api": "manage_cluster", "args": {"resource": "service", "operation": "list"}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT phase, source_rows, source_sha256, checkpoint_schema FROM {control} WHERE id = 1"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT r.request_id, r.plan_epoch, r.checkpoint_generation, r.checkpoint_schema, r.request_state, "
                    f"p.node_name, p.zone, p.device_class, p.available_gib, p.checkpoint_compatible, p.lifecycle_state, p.lease_state, "
                    f"v.reservation_token, v.reservation_state, "
                    f"m.source_sha256, m.fence_token, m.reuse_state, "
                    f"l.lease_revision, l.lease_state, l.reservation_token, l.fence_token, l.renewed_at "
                    f"FROM {request} r "
                    f"JOIN {plan} p ON p.plan_epoch = r.plan_epoch "
                    f"LEFT JOIN {reservation} v ON v.request_id = r.request_id AND v.node_name = p.node_name "
                    "AND v.plan_epoch = r.plan_epoch AND v.checkpoint_generation = r.checkpoint_generation "
                    f"LEFT JOIN {manifest} m ON m.node_name = p.node_name AND m.checkpoint_schema = r.checkpoint_schema "
                    "AND m.checkpoint_generation = r.checkpoint_generation "
                    f"LEFT JOIN {lease} l ON l.request_id = r.request_id AND l.node_name = p.node_name "
                    "AND l.plan_epoch = r.plan_epoch AND l.checkpoint_generation = r.checkpoint_generation "
                    "WHERE r.id = 1 ORDER BY p.node_name"
                )}},
            ],
        },
        {
            "thinking": "启动唯一与 checkpoint generation、source digest 和 fence 对齐的候选，并提交 reservation、request 与 resume gate 三项行级准入。",
            "actions": [
                {"api": "manage_cluster", "args": {"resource": "service", "operation": "start", "target": f"tikv/{case.approved_tikv_service}"}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {reservation} SET reservation_state = 'committed', updated_at = NOW() "
                    f"WHERE request_id = '{case.request_id}' AND node_name = '{case.approved_tikv_service}' "
                    f"AND plan_epoch = {case.approved_plan_epoch} AND checkpoint_generation = {case.approved_checkpoint_generation} "
                    f"AND reservation_token = '{case.approved_reservation_token}' AND reservation_state = 'available'"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {request} SET request_state = 'APPROVED' WHERE id = 1 AND request_id = '{case.request_id}' "
                    f"AND plan_epoch = {case.approved_plan_epoch} AND checkpoint_generation = {case.approved_checkpoint_generation} "
                    "AND request_state = 'PENDING'"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {gate} SET gate_state = 'approved', approved_service = '{case.approved_tikv_service}', "
                    f"approved_epoch = {case.approved_plan_epoch}, checkpoint_source_sha256 = '{case.expected_source_sha256}', "
                    f"approved_fence_token = '{case.approved_fence_token}' WHERE id = 1 AND gate_state = 'pending' "
                    f"AND request_id = '{case.request_id}' AND checkpoint_schema = '{case.checkpoint_schema}'"
                )}},
            ],
        },
        {
            "thinking": "验证 checkpoint 完成、lease 对齐、billing 行数、聚合、ADMIN CHECKSUM 和 stats 后提交报告。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT phase, source_rows, checkpoint_schema FROM {control} WHERE id = 1"}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT l.node_name, l.plan_epoch, l.checkpoint_generation, l.reservation_token, l.fence_token, l.lease_state "
                    f"FROM {lease} l JOIN {reservation} r ON r.request_id = l.request_id AND r.node_name = l.node_name "
                    "AND r.plan_epoch = l.plan_epoch AND r.checkpoint_generation = l.checkpoint_generation "
                    f"JOIN {manifest} m ON m.node_name = l.node_name AND m.checkpoint_schema = '{case.checkpoint_schema}' "
                    f"AND m.checkpoint_generation = l.checkpoint_generation WHERE l.request_id = '{case.request_id}' "
                    f"AND l.node_name = '{case.approved_tikv_service}' AND l.plan_epoch = {case.approved_plan_epoch} "
                    f"AND l.checkpoint_generation = {case.approved_checkpoint_generation} AND l.lease_state = 'current' "
                    "AND l.reservation_token = r.reservation_token AND l.fence_token = m.fence_token AND l.renewed_at > m.observed_at"
                )}},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT COUNT(*), SUM(id), SUM(account_id), SUM(amount_cents) FROM {target}"}},
                {"api": "execute_sql", "args": {"sql_query": f"ADMIN CHECKSUM TABLE {target}"}},
                {"api": "execute_sql", "args": {"sql_query": (
                    "SELECT `count` FROM mysql.stats_meta WHERE table_id = (SELECT TIDB_TABLE_ID "
                    f"FROM information_schema.tables WHERE TABLE_SCHEMA = '{case.database}' AND TABLE_NAME = '{case.table}') "
                    "ORDER BY version DESC LIMIT 1"
                )}},
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def build_mock_responses(case):
    if case.case_no == 1:
        return _partition_resume_mock_responses(case)
    control = f"{case.database}.{case.control_table}"
    request = f"{case.database}.{case.request_table}"
    plan = f"{case.database}.{case.capacity_plan_table}"
    reservation = f"{case.database}.{case.capacity_reservation_table}"
    manifest = f"{case.database}.{case.checkpoint_manifest_table}"
    lease = f"{case.database}.{case.lease_journal_table}"
    gate = f"{case.database}.{case.resume_gate_table}"
    target = f"{case.database}.{case.table}"
    return [
        {
            "thinking": "Inspect the cluster topology and current migration control state before changing capacity.",
            "actions": [
                {"api": "search_knowledge", "args": {
                    "query": "TiDB Lightning 8.1 checkpoints mysql driver resume same source schema target",
                    "source_scope": "self_managed",
                    "kb_type": "configuration",
                    "component": "lightning",
                    "top_k": 3,
                }},
                {"api": "manage_cluster", "args": {"resource": "service", "operation": "list"}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT phase, source_rows, source_sha256, checkpoint_schema FROM {control} WHERE id = 1"
                )}},
            ],
        },
        {
            "thinking": "Correlate the checkpoint, capacity plan, reservation, manifest, and lease before selecting the approved candidate.",
            "actions": [
                {"api": "search_knowledge", "args": {
                    "query": "TiDB Lightning 8.1 physical import PITR TiCDC parallel import empty Regions precheck",
                    "source_scope": "self_managed",
                    "kb_type": "operation",
                    "component": "lightning",
                    "top_k": 5,
                }},
                {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": "tikv/tikv-0"}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT r.request_id, r.required_zone, r.required_device_class, r.min_free_gib, "
                    f"r.plan_epoch, r.checkpoint_generation, p.node_name, p.zone, p.device_class, p.available_gib, "
                    f"p.checkpoint_compatible, p.lifecycle_state, p.lease_state FROM {request} r "
                    f"JOIN {plan} p ON p.plan_epoch = r.plan_epoch WHERE r.id = 1 ORDER BY p.node_name"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT request_id, node_name, plan_epoch, checkpoint_generation, reservation_token, reservation_state "
                    f"FROM {reservation} ORDER BY request_id, node_name"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT node_name, checkpoint_schema, checkpoint_generation, source_sha256, fence_token, "
                    f"verified_rows, reuse_state, lease_state FROM {manifest} ORDER BY node_name, checkpoint_generation"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT request_id, node_name, plan_epoch, checkpoint_generation, lease_revision, lease_state, "
                    f"reservation_token, fence_token, renewed_at FROM {lease} "
                    "ORDER BY request_id, node_name, checkpoint_generation, lease_revision"
                )}},
            ],
        },
        {
            "thinking": "Start the approved candidate, commit the matching reservation and request, then approve the existing resume gate without touching data or checkpoint state.",
            "actions": [
                {"api": "manage_cluster", "args": {"resource": "service", "operation": "start", "target": f"tikv/{case.approved_tikv_service}"}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {reservation} SET reservation_state = 'committed', updated_at = NOW() "
                    f"WHERE request_id = '{case.request_id}' AND node_name = '{case.approved_tikv_service}' "
                    f"AND plan_epoch = {case.approved_plan_epoch} AND checkpoint_generation = {case.approved_checkpoint_generation} "
                    f"AND reservation_token = '{case.approved_reservation_token}' AND reservation_state = 'available'"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {request} SET request_state = 'APPROVED' WHERE id = 1 AND request_id = '{case.request_id}' "
                    f"AND plan_epoch = {case.approved_plan_epoch} AND checkpoint_generation = {case.approved_checkpoint_generation} "
                    "AND request_state = 'PENDING'"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {gate} SET gate_state = 'approved', approved_service = '{case.approved_tikv_service}', "
                    f"approved_epoch = {case.approved_plan_epoch}, checkpoint_source_sha256 = '{case.expected_source_sha256}', "
                    f"approved_fence_token = '{case.approved_fence_token}' WHERE id = 1 AND gate_state = 'pending' "
                    f"AND request_id = '{case.request_id}' AND checkpoint_schema = '{case.checkpoint_schema}'"
                )}},
            ],
        },
        {
            "thinking": "Verify the checkpoint completion, lease alignment, billing aggregates, checksum, and statistics.",
            "actions": [
                {"api": "search_knowledge", "args": {
                    "query": "TiDB Lightning checkpoint recovery after insufficient TiKV space resume import",
                    "source_scope": "self_managed",
                    "kb_type": "recovery",
                    "component": "lightning",
                    "top_k": 3,
                }},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT phase, source_rows, checkpoint_schema FROM {control} WHERE id = 1"}},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT request_state, plan_epoch, checkpoint_generation FROM {request} WHERE id = 1"}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT node_name, plan_epoch, checkpoint_generation, reservation_token, reservation_state "
                    f"FROM {reservation} WHERE request_id = '{case.request_id}' AND reservation_state = 'committed'"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT gate_state, approved_service, approved_epoch, checkpoint_schema, checkpoint_source_sha256, "
                    f"approved_fence_token FROM {gate} WHERE id = 1"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT node_name, checkpoint_generation, source_sha256, fence_token, reuse_state, lease_state "
                    f"FROM {manifest} WHERE node_name = '{case.approved_tikv_service}' "
                    f"AND checkpoint_schema = '{case.checkpoint_schema}' AND checkpoint_generation = {case.approved_checkpoint_generation}"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT l.node_name, l.plan_epoch, l.checkpoint_generation, l.reservation_token, l.fence_token, l.lease_state "
                    f"FROM {lease} l JOIN {reservation} r ON r.request_id = l.request_id AND r.node_name = l.node_name "
                    "AND r.plan_epoch = l.plan_epoch AND r.checkpoint_generation = l.checkpoint_generation "
                    f"JOIN {manifest} m ON m.node_name = l.node_name AND m.checkpoint_schema = '{case.checkpoint_schema}' "
                    f"AND m.checkpoint_generation = l.checkpoint_generation WHERE l.request_id = '{case.request_id}' "
                    f"AND l.node_name = '{case.approved_tikv_service}' AND l.plan_epoch = {case.approved_plan_epoch} "
                    f"AND l.checkpoint_generation = {case.approved_checkpoint_generation} AND l.lease_state = 'current' "
                    "AND l.reservation_token = r.reservation_token AND l.fence_token = m.fence_token AND l.renewed_at > m.observed_at"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT file_name, byte_size, file_sha256, row_start, row_end, file_format, file_charset, "
                    f"has_header, bundle_sha256 FROM {case.database}.{case.source_manifest_table} ORDER BY file_name"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT target_table, schema_sha256, index_signature, create_statement, source_format, "
                    f"source_charset, lightning_backend, config_sha256 FROM {case.database}.{case.schema_manifest_table} WHERE id = 1"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT task_identity, target_table, source_sha256, source_bundle_sha256, schema_sha256, "
                    f"checkpoint_driver, checkpoint_host, checkpoint_schema, checkpoint_generation, "
                    f"checkpoint_table_count, checkpoint_table_names, checkpoint_metadata_sha256, config_sha256, "
                    f"partial_target_rows, checkpoint_state FROM {case.database}.{case.checkpoint_identity_table} WHERE id = 1"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT checkpoint_table_name, table_rows, column_signature, checkpoint_state "
                    f"FROM {case.database}.{case.checkpoint_table_manifest_table} ORDER BY checkpoint_table_name"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT physical_backend, pitr_state, ticdc_state, parallel_import_enabled, empty_region_count, "
                    f"empty_region_limit, target_empty_at_start, observed_target FROM {case.database}.{case.protection_state_table} WHERE id = 1"
                )}},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT COUNT(*), SUM(id), SUM(account_id), SUM(amount_cents) FROM {target}"}},
                {"api": "execute_sql", "args": {"sql_query": f"ADMIN CHECKSUM TABLE {target}"}},
                {"api": "execute_sql", "args": {"sql_query": (
                    "SELECT `count` FROM mysql.stats_meta WHERE table_id = (SELECT TIDB_TABLE_ID "
                    f"FROM information_schema.tables WHERE TABLE_SCHEMA = '{case.database}' AND TABLE_NAME = '{case.table}') "
                    "ORDER BY version DESC LIMIT 1"
                )}},
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


FULL_PASS_MOCK_RESPONSES = build_mock_responses(CASE)


def main():
    scenario = SCENARIO
    parser = argparse.ArgumentParser(
        description="Run the TiDB BC05 Lightning checkpoint scale-out scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--port", type=int, default=5200)
    parser.add_argument("--container-name", default="aiopsbench-tidb-bc05")
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB migration DBA.",
            use_native_tools=False,
        )
        agent.set_mock_responses(build_mock_responses(case))
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)

    result = Orchestrator(env, scenario, case, agent, max_turns=args.max_turns).run()
    if args.mode == "mock":
        assert result["DiagnosisPass"] is None
        assert result["OutcomePass"] is True
        assert result["SafePass"] is True
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
