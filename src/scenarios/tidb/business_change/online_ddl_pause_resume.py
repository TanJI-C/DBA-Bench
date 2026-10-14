from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.business_change.online_ddl_pause_resume import (
    TidbBusinessChangeOnlineDdlPauseResumeForPausedIndexBackfillEvaluatorCase,
    TidbBusinessChangeOnlineDdlPauseResumeForBillingEvaluatorCase,
)
from src.protocols.report import structured_reference_report
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True)
class BusinessDecoySpec:
    database: str
    table: str
    row_count: int
    payload_index_name: str
    window_index_name: str
    audit_column_name: str
    paused_index_name: str
    payload_padding_bytes: int
    precreate_indexes: bool
    payload_index_prefix_length: int


_DECOY_TABLES = (
    BusinessDecoySpec(
        database="benchops_bc09",
        table="ddl_events_archive",
        row_count=100000,
        payload_index_name="idx_archive_payload",
        window_index_name="idx_event_type_window",
        audit_column_name="archive_batch",
        paused_index_name="idx_alt_payload",
        payload_padding_bytes=96,
        precreate_indexes=False,
        payload_index_prefix_length=0,
    ),
    BusinessDecoySpec(
        database="benchops_bc09",
        table="ddl_events_shadow",
        row_count=18000,
        payload_index_name="idx_shadow_payload",
        window_index_name="idx_event_type_window",
        audit_column_name="shadow_batch",
        paused_index_name="idx_alt_payload",
        payload_padding_bytes=96,
        precreate_indexes=False,
        payload_index_prefix_length=0,
    ),
    BusinessDecoySpec(
        database="benchops_bc09",
        table="ddl_events_replay",
        row_count=14000,
        payload_index_name="idx_replay_payload",
        window_index_name="idx_replay_window",
        audit_column_name="replay_batch",
        paused_index_name="idx_alt_payload",
        payload_padding_bytes=96,
        precreate_indexes=False,
        payload_index_prefix_length=0,
    ),
    BusinessDecoySpec(
        database="benchops_bc09",
        table="ddl_events_canary",
        row_count=30000,
        payload_index_name="idx_canary_payload",
        window_index_name="idx_canary_window",
        audit_column_name="canary_batch",
        paused_index_name="idx_alt_payload",
        payload_padding_bytes=96,
        precreate_indexes=True,
        payload_index_prefix_length=0,
    ),
    BusinessDecoySpec(
        database="benchops_bc09",
        table="ddl_events_mirror",
        row_count=25000,
        payload_index_name="idx_mirror_payload",
        window_index_name="idx_mirror_window",
        audit_column_name="mirror_batch",
        paused_index_name="idx_alt_payload",
        payload_padding_bytes=96,
        precreate_indexes=True,
        payload_index_prefix_length=0,
    ),
    BusinessDecoySpec(
        database="benchops_bc09_reporting",
        table="ddl_events",
        row_count=60000,
        payload_index_name="idx_reporting_payload",
        window_index_name="idx_reporting_window",
        audit_column_name="reporting_batch",
        paused_index_name="idx_alt_payload",
        payload_padding_bytes=96,
        precreate_indexes=False,
        payload_index_prefix_length=0,
    ),
)


_BILLING_DECOY_TABLES = tuple(
    replace(
        decoy,
        database=(
            "benchops_bc09_billing"
            if decoy.database == "benchops_bc09"
            else "benchops_bc09_billing_reporting"
        ),
        table=decoy.table.replace("ddl_events", "billing_events"),
        payload_index_name=decoy.payload_index_name.replace("idx_", "idx_billing_"),
        window_index_name=decoy.window_index_name.replace("idx_", "idx_billing_"),
        audit_column_name=decoy.audit_column_name.replace("_batch", "_billing_batch"),
        paused_index_name="idx_billing_alt_payload",
    )
    for decoy in _DECOY_TABLES
)


def _business_workload(
    database: str,
    table: str,
    decoy_tables: tuple[BusinessDecoySpec, ...],
    service_name: str,
    route_key: str,
    stream_prefix: str,
    route_table: str,
    route_binding_table: str,
    change_request_table: str,
    route_lease_table: str,
    route_owner_table: str,
    route_commit_table: str,
    route_traffic_table: str,
    route_runtime_table: str,
    business_contract_table: str,
) -> tuple[WorkloadProfile, ...]:
    relations = ((database, table), *((decoy.database, decoy.table) for decoy in decoy_tables))
    schemas = tuple(dict.fromkeys(schema for schema, _ in relations))
    schema_list = ", ".join(f"'{schema}'" for schema in schemas)
    profiles = []
    for index, (relation_database, relation_table) in enumerate(relations, start=1):
        relation = f"{relation_database}.{relation_table}"
        slot = f"svc_read_{index:02d}"
        payload_prefix = f"{stream_prefix}-{index:02d}"
        next_relation_database, next_relation_table = relations[index % len(relations)]
        profiles.extend(
            (
                WorkloadProfile(
                    name=f"{slot}_point",
                    sql=f"SELECT event_id, payload, amount FROM {relation} WHERE event_id = 9001",
                    qps=0.18,
                    tier="LIGHT",
                    application_name=service_name,
                ),
                WorkloadProfile(
                    name=f"{slot}_queue",
                    sql=(
                        f"SELECT event_id, amount FROM {relation} "
                        "WHERE tenant_id = 17 AND event_type = 'refund' "
                        "ORDER BY event_id DESC LIMIT 64"
                    ),
                    qps=0.12,
                    tier="LIGHT",
                    application_name=service_name,
                ),
                WorkloadProfile(
                    name=f"{slot}_rollup",
                    sql=(
                        f"SELECT event_type, COUNT(*), SUM(amount) FROM {relation} "
                        "GROUP BY event_type ORDER BY event_type"
                    ),
                    qps=0.1,
                    tier="MEDIUM",
                    application_name=service_name,
                ),
                WorkloadProfile(
                    name=f"{slot}_window",
                    sql=(
                        f"SELECT COUNT(*), SUM(amount) FROM {relation} "
                        "WHERE event_ts >= '2024-01-02' AND event_ts < '2024-01-08'"
                    ),
                    qps=0.1,
                    tier="MEDIUM",
                    application_name=service_name,
                ),
                WorkloadProfile(
                    name=f"{slot}_lookup",
                    sql=(
                        f"SELECT event_id, tenant_id FROM {relation} "
                        f"WHERE payload LIKE '{payload_prefix}-090001-%'"
                    ),
                    qps=0.16,
                    tier="MEDIUM",
                    application_name=service_name,
                ),
                WorkloadProfile(
                    name=f"{slot}_reconciliation",
                    sql=(
                        f"SELECT primary_batch, COUNT(*), SUM(amount), MIN(event_id), MAX(event_id), "
                        f"COUNT(DISTINCT payload), BIT_XOR(CRC32(CONCAT_WS('#', event_id, payload))) FROM {relation} "
                        "WHERE event_id BETWEEN 8990 AND 9010 AND tenant_id IN (1, 33, 37, 65, 69) "
                        "AND event_type = 'refund' "
                        "GROUP BY primary_batch"
                    ),
                    qps=0.11,
                    tier="MEDIUM",
                    application_name=service_name,
                ),
                WorkloadProfile(
                    name=f"{slot}_join",
                    sql=(
                        f"SELECT e.event_type, COUNT(*) FROM {relation} e "
                        f"JOIN {next_relation_database}.{next_relation_table} n ON n.event_id = e.event_id "
                        "GROUP BY e.event_type ORDER BY e.event_type"
                    ),
                    qps=0.08,
                    tier="MEDIUM",
                    application_name=service_name,
                ),
                WorkloadProfile(
                    name=f"{slot}_probe",
                    sql=(
                        f"SELECT event_id, amount FROM {relation} "
                        "WHERE event_type IN ('refund', 'chargeback') ORDER BY event_id LIMIT 32"
                    ),
                    qps=0.1,
                    tier="LIGHT",
                    application_name=service_name,
                ),
            )
        )
    profiles.extend(
        (
            WorkloadProfile(
                name="route_registry_resolution",
                sql=(
                    "SELECT route_id, service_name, route_role, route_state, route_key, binding_id, "
                    "route_version, current_route "
                    f"FROM {database}.{route_table} WHERE service_name = '{service_name}' "
                    "ORDER BY route_version DESC, route_id"
                ),
                qps=0.34,
                tier="LIGHT",
                application_name=f"{service_name.removesuffix('-api')}-router",
            ),
            WorkloadProfile(
                name="route_binding_resolution",
                sql=(
                    "SELECT binding_id, route_id, route_key, binding_generation, binding_state, "
                    "relation_schema, relation_table, lease_state, current_binding, effective_from, effective_until "
                    f"FROM {database}.{route_binding_table} ORDER BY route_key, binding_generation DESC, binding_id"
                ),
                qps=0.28,
                tier="LIGHT",
                application_name=f"{service_name.removesuffix('-api')}-router",
            ),
            WorkloadProfile(
                name="schema_change_request_audit",
                sql=(
                    "SELECT change_id, route_id, binding_id, request_state, change_kind, index_name, "
                    "column_name, expected_unique, approved_route_version, current_request "
                    f"FROM {database}.{change_request_table} ORDER BY approved_route_version DESC, change_id"
                ),
                qps=0.24,
                tier="LIGHT",
                application_name="change-control",
            ),
            WorkloadProfile(
                name="route_lease_fence_audit",
                sql=(
                    "SELECT binding_id, fence_epoch, fence_state, current_lease, owner_instance, "
                    "owner_incarnation, observed_at, valid_until "
                    f"FROM {database}.{route_lease_table} ORDER BY binding_id, fence_epoch DESC"
                ),
                qps=0.24,
                tier="LIGHT",
                application_name=f"{service_name.removesuffix('-api')}-router",
            ),
            WorkloadProfile(
                name="route_owner_heartbeat_audit",
                sql=(
                    "SELECT owner_instance, service_name, owner_state, last_heartbeat, lease_expires_at, "
                    "incarnation, current_owner "
                    f"FROM {database}.{route_owner_table} ORDER BY owner_instance"
                ),
                qps=0.22,
                tier="LIGHT",
                application_name=f"{service_name.removesuffix('-api')}-router",
            ),
            WorkloadProfile(
                name="route_cutover_commit_audit",
                sql=(
                    "SELECT commit_id, route_id, binding_id, route_version, commit_state, current_commit, "
                    "effective_from, effective_until "
                    f"FROM {database}.{route_commit_table} ORDER BY route_key, route_version, commit_id"
                ),
                qps=0.2,
                tier="LIGHT",
                application_name="change-control",
            ),
            WorkloadProfile(
                name="route_traffic_assignment_audit",
                sql=(
                    "SELECT assignment_id, route_id, binding_id, service_name, traffic_class, assignment_state, "
                    "read_weight, write_weight, current_assignment, effective_from, effective_until "
                    f"FROM {database}.{route_traffic_table} ORDER BY service_name, traffic_class, assignment_id"
                ),
                qps=0.2,
                tier="LIGHT",
                application_name=f"{service_name.removesuffix('-api')}-router",
            ),
            WorkloadProfile(
                name="route_runtime_observation_audit",
                sql=(
                    "SELECT observation_id, route_id, binding_id, service_name, route_key, observed_state, request_origin, "
                    "read_requests, write_requests, last_request_at, observed_at, observation_until, "
                    "current_observation, relation_schema, relation_table "
                    f"FROM {database}.{route_runtime_table} ORDER BY route_id, observation_id"
                ),
                qps=0.2,
                tier="LIGHT",
                application_name=f"{service_name.removesuffix('-api')}-router",
            ),
            WorkloadProfile(
                name="business_query_contract_audit",
                sql=(
                    "SELECT contract_id, service_name, route_key, query_name, contract_state, "
                    "expected_row_count, expected_amount_sum, expected_min_event_id, expected_max_event_id, "
                    "expected_payload_count, expected_payload_digest, current_contract, effective_from, effective_until "
                    f"FROM {database}.{business_contract_table} ORDER BY service_name, route_key, contract_id"
                ),
                qps=0.18,
                tier="LIGHT",
                application_name=service_name,
            ),
            WorkloadProfile(
                name="schema_history_audit",
                sql=(
                    "SELECT JOB_ID, DB_NAME, TABLE_NAME, JOB_TYPE, STATE FROM information_schema.ddl_jobs "
                    "ORDER BY JOB_ID DESC LIMIT 40"
                ),
                qps=0.32,
                tier="LIGHT",
                application_name="schema-audit",
            ),
            WorkloadProfile(
                name="index_catalog_audit",
                sql=(
                    "SELECT TABLE_SCHEMA, TABLE_NAME, KEY_NAME, NON_UNIQUE, IS_VISIBLE, "
                    "SEQ_IN_INDEX, COLUMN_NAME FROM information_schema.tidb_indexes "
                    f"WHERE TABLE_SCHEMA IN ({schema_list}) ORDER BY TABLE_SCHEMA, TABLE_NAME, KEY_NAME, SEQ_IN_INDEX"
                ),
                qps=0.2,
                tier="LIGHT",
                application_name="catalog-audit",
            ),
            WorkloadProfile(
                name="table_cardinality_audit",
                sql=(
                    "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS, AVG_ROW_LENGTH "
                    "FROM information_schema.tables "
                    f"WHERE TABLE_SCHEMA IN ({schema_list}) ORDER BY TABLE_ROWS DESC, TABLE_SCHEMA, TABLE_NAME"
                ),
                qps=0.16,
                tier="LIGHT",
                application_name="capacity-audit",
            ),
            WorkloadProfile(
                name="column_change_audit",
                sql=(
                    "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_DEFAULT "
                    "FROM information_schema.columns "
                    f"WHERE TABLE_SCHEMA IN ({schema_list}) ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION"
                ),
                qps=0.12,
                tier="LIGHT",
                application_name="schema-audit",
            ),
            WorkloadProfile(
                name="cluster_version_decoy",
                sql=(
                    "SELECT TYPE, COUNT(*) FROM information_schema.cluster_info "
                    "GROUP BY TYPE ORDER BY TYPE"
                ),
                qps=0.2,
                tier="LIGHT",
                application_name="release-audit",
            ),
        )
    )
    return tuple(profiles)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeOnlineDdlPauseResumeCase(TiDBScenarioCase):
    database: str
    table: str
    index_name: str
    service_name: str
    route_key: str
    route_id: str
    binding_id: str
    change_id: str
    commit_id: str
    contract_id: str
    owner_instance: str
    owner_incarnation: int
    route_version: int
    stream_prefix: str
    row_count: int
    payload_padding_bytes: int
    route_table: str
    route_binding_table: str
    change_request_table: str
    route_lease_table: str
    route_owner_table: str
    route_commit_table: str
    route_traffic_table: str
    route_runtime_table: str
    business_contract_table: str
    decoy_tables: tuple[BusinessDecoySpec, ...]
    reference_evidence_counts: tuple[tuple[str, int, int], ...]


class TidbBusinessChangeOnlineDdlPauseResumeForPausedIndexBackfillScenarioCase(
    TidbBusinessChangeOnlineDdlPauseResumeCase
):
    pass


_CASE = TidbBusinessChangeOnlineDdlPauseResumeForPausedIndexBackfillScenarioCase(
    case_id="paused_unique_index_backfill",
    reference_report=structured_reference_report(
        case_id="paused_unique_index_backfill",
        factors=(),
        changes=("resumed only the already-started unique-index backfill for the serving route binding",),
        verification=(
            "the target unique index is public and visible",
            "ADMIN CHECK TABLE passed, no duplicate add-index job exists, and business truth stayed unchanged",
        ),
        summary="The reference path resumed the correct paused online DDL job and verified route-bound safety.",
    ),
    case_no=0,
    evaluator=TidbBusinessChangeOnlineDdlPauseResumeForPausedIndexBackfillEvaluatorCase,
    title="Resume one paused unique-index backfill under concurrent business reads.",
    alert=(
        "[CHANGE] 订单平台需要在在线读流量下完成订单事件流当前 primary route 的唯一查找键 schema change。"
        "当前集群有七项已经开始但暂停的相近后台索引构建，覆盖主业务、历史归档、影子、回放、canary、mirror 和 reporting 候选；数据库中还保留相近历史 DDL、索引、审计查询和业务路由登记。"
        "请不要凭表名、行数或最近一条记录猜测目标；route_registry 只保存逻辑 route_key 和 binding_id，不直接保存物理表。"
        "本次现场观测时刻固定为 2026-08-02 23:59:59 UTC。route_registry 中保留了 staged rollout 的多个 active primary/current 标记；不要按最新版本或 current_route 单字段选表，必须核对版本化 route binding 的 serving lease、生效时间窗口和当前观测时刻。"
        "集群还保留 route、lease/owner、cutover、traffic、runtime、business contract、schema-change request、索引目录和 DDL history 等控制面与数据面记录；请综合现场证据确认当前 serving relation 和已有 schema change。"
        "不要修改业务数据，也不要重复提交 schema change；按业务目标完成已有变更。"
        "提交前必须验证 job 已完成、目标索引为唯一且可见、ADMIN CHECK TABLE 通过、"
        "没有重复的 add-index job，业务真值没有变化。"
    ),
    initial_state={
        "status": "change_paused",
        "ddl_job_state": "paused",
        "candidate_table_count": 7,
        "route_resolution_hops": 10,
        "index_name": "idx_alt_payload",
        "index_state": "not_public",
        "paused_add_index_jobs": 7,
        "concurrent_business_reads": True,
    },
    expected_target={
        "ddl_job_state": "synced",
        "public_unique_index": "idx_alt_payload",
        "admin_check": "passed",
        "add_index_job_count": 1,
        "business_truth_unchanged": True,
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_business_workload(
            "benchops_bc09",
            "ddl_events",
            _DECOY_TABLES,
            "orders-api",
            "orders.events",
            "bc09-stream",
            "route_registry",
            "route_bindings",
            "schema_change_requests",
            "route_lease_fences",
            "route_owner_heartbeats",
            "route_cutover_commits",
            "route_traffic_assignments",
            "route_runtime_observations",
            "business_query_contracts",
        ),
        worker_count=1,
        seed=0xBC09,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=10,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.966443,
        reference_run_ids=(
            "reference-164__"
            "tidb_business_change_online_ddl_pause_resume__paused_unique_index_backfill__mock__r001",
        ),
    ),
    runtime=tidb_runtime(release=TIDB_V8_1_0, pd_count=3, tikv_count=3, tidb_count=2),
    database="benchops_bc09",
    table="ddl_events",
    index_name="idx_alt_payload",
    service_name="orders-api",
    route_key="orders.events",
    route_id="order-events-primary-01",
    binding_id="binding-orders-events-v43",
    change_id="chg-orders-events-v43-payload-unique",
    commit_id="commit-orders-events-v43",
    contract_id="contract-orders-events-customer-v7",
    owner_instance="orders-router-2",
    owner_incarnation=20260802017,
    route_version=43,
    stream_prefix="bc09-stream",
    row_count=100000,
    payload_padding_bytes=96,
    route_table="route_registry",
    route_binding_table="route_bindings",
    change_request_table="schema_change_requests",
    route_lease_table="route_lease_fences",
    route_owner_table="route_owner_heartbeats",
    route_commit_table="route_cutover_commits",
    route_traffic_table="route_traffic_assignments",
    route_runtime_table="route_runtime_observations",
    business_contract_table="business_query_contracts",
    decoy_tables=_DECOY_TABLES,
    reference_evidence_counts=(
        ("execute_sql:statement_summary", 0, 50),
        ("query_metrics:active_connections", 0, 62),
        ("execute_sql:route_registry", 1, 10),
        ("execute_sql:route_binding", 1, 11),
        ("execute_sql:route_lease_fence", 1, 11),
        ("execute_sql:route_owner_heartbeat", 1, 10),
        ("execute_sql:route_cutover_commit", 1, 11),
        ("execute_sql:route_traffic_assignment", 1, 11),
        ("execute_sql:route_runtime_observation", 1, 11),
        ("execute_sql:business_query_contract", 1, 13),
        ("execute_sql:schema_change_request", 1, 11),
        ("execute_sql:ddl_history", 1, 16),
        ("execute_sql:ddl_job_query", 1, 0),
        ("execute_sql:index_catalog", 0, 35),
        ("execute_sql:table_cardinality", 1, 15),
        ("execute_sql:column_catalog", 1, 149),
        ("execute_sql:business_query_probe", 1, 6),
        ("execute_sql:business_truth", 1, 0),
    ),
)


_BILLING_CASE = replace(
    _CASE,
    case_id="paused_unique_index_backfill_billing",
    case_no=1,
    evaluator=TidbBusinessChangeOnlineDdlPauseResumeForBillingEvaluatorCase,
    reference_report=structured_reference_report(
        case_id="paused_unique_index_backfill_billing",
        factors=(),
        changes=("resumed only the already-started unique-index backfill for the serving billing route binding",),
        verification=(
            "the billing target unique index is public and visible",
            "ADMIN CHECK TABLE passed, no duplicate add-index job exists, and billing truth stayed unchanged",
        ),
        summary="The reference path resumed the billing route's prepared online DDL job and verified route-bound safety.",
    ),
    title="Resume one paused billing unique-index backfill under concurrent payment reads.",
    alert=(
        "[CHANGE] 结算平台需要在在线读流量下完成 billing.events 当前 primary route 的唯一查找键 schema change。"
        "当前集群有七项已经开始但暂停的相近后台索引构建，覆盖支付主业务、历史归档、影子、回放、canary、mirror 和 reporting 候选；数据库中还保留相近历史 DDL、索引、审计查询和业务路由登记。"
        "请不要凭表名、行数或最近一条记录猜测目标；route_registry 只保存逻辑 route_key 和 binding_id，不直接保存物理表。"
        "本次现场观测时刻固定为 2026-08-02 23:59:59 UTC。route_registry 中保留了 staged rollout 的多个 active primary/current 标记；不要按最新版本或 current_route 单字段选表，必须核对版本化 route binding 的 serving lease、生效时间窗口和当前观测时刻。"
        "集群还保留 route、lease/owner、cutover、traffic、runtime、business contract、schema-change request、索引目录和 DDL history 等控制面与数据面记录；请综合现场证据确认当前 serving relation 和已有 schema change。"
        "不要修改业务数据，也不要重复提交 schema change；按业务目标完成已有变更。"
        "提交前必须验证 job 已完成、目标索引为唯一且可见、ADMIN CHECK TABLE 通过、"
        "没有重复的 add-index job，业务真值没有变化。"
    ),
    initial_state={
        "status": "change_paused",
        "ddl_job_state": "paused",
        "candidate_table_count": 7,
        "route_resolution_hops": 10,
        "index_name": "idx_billing_alt_payload",
        "index_state": "not_public",
        "paused_add_index_jobs": 7,
        "concurrent_business_reads": True,
    },
    expected_target={
        "ddl_job_state": "synced",
        "public_unique_index": "idx_billing_alt_payload",
        "admin_check": "passed",
        "add_index_job_count": 1,
        "business_truth_unchanged": True,
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_business_workload(
            "benchops_bc09_billing",
            "billing_events",
            _BILLING_DECOY_TABLES,
            "billing-api",
            "billing.events",
            "billing-stream",
            "billing_route_registry",
            "billing_route_bindings",
            "billing_schema_change_requests",
            "billing_route_lease_fences",
            "billing_route_owner_heartbeats",
            "billing_route_cutover_commits",
            "billing_route_traffic_assignments",
            "billing_route_runtime_observations",
            "billing_business_query_contracts",
        ),
        worker_count=1,
        seed=0xBC10,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=10,
    ),
    difficulty=replace(
        _CASE.difficulty,
        reference_run_ids=(
            "reference-242__"
            "tidb_business_change_online_ddl_pause_resume__paused_unique_index_backfill_billing__"
            "mock__r001",
        ),
    ),
    database="benchops_bc09_billing",
    table="billing_events",
    index_name="idx_billing_alt_payload",
    service_name="billing-api",
    route_key="billing.events",
    route_id="billing-events-primary-01",
    binding_id="binding-billing-events-v53",
    change_id="chg-billing-events-v53-payload-unique",
    commit_id="commit-billing-events-v53",
    contract_id="contract-billing-events-settlement-v53",
    owner_instance="billing-router-2",
    owner_incarnation=20260812017,
    route_version=53,
    stream_prefix="billing-stream",
    row_count=150000,
    payload_padding_bytes=128,
    route_table="billing_route_registry",
    route_binding_table="billing_route_bindings",
    change_request_table="billing_schema_change_requests",
    route_lease_table="billing_route_lease_fences",
    route_owner_table="billing_route_owner_heartbeats",
    route_commit_table="billing_route_cutover_commits",
    route_traffic_table="billing_route_traffic_assignments",
    route_runtime_table="billing_route_runtime_observations",
    business_contract_table="billing_business_query_contracts",
    decoy_tables=_BILLING_DECOY_TABLES,
)


class TidbBusinessChangeOnlineDdlPauseResumeScenario(TiDBScenario):
    scenario_id = "tidb_business_change_online_ddl_pause_resume"
    description = "Resume a paused TiDB online unique-index backfill without duplicating the DDL job."
    cases = (_CASE, _BILLING_CASE)

    def build_fault_plan(
        self,
        case: TidbBusinessChangeOnlineDdlPauseResumeCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbBusinessChangeOnlineDdlPauseResumeInjector,
                config={
                    "database": case.database,
                    "table": case.table,
                    "index_name": case.index_name,
                    "service_name": case.service_name,
                    "route_key": case.route_key,
                    "route_id": case.route_id,
                    "binding_id": case.binding_id,
                    "change_id": case.change_id,
                    "commit_id": case.commit_id,
                    "contract_id": case.contract_id,
                    "owner_instance": case.owner_instance,
                    "owner_incarnation": case.owner_incarnation,
                    "route_version": case.route_version,
                    "stream_prefix": case.stream_prefix,
                    "row_count": case.row_count,
                    "payload_padding_bytes": case.payload_padding_bytes,
                    "route_table": case.route_table,
                    "route_binding_table": case.route_binding_table,
                    "change_request_table": case.change_request_table,
                    "route_lease_table": case.route_lease_table,
                    "route_owner_table": case.route_owner_table,
                    "route_commit_table": case.route_commit_table,
                    "route_traffic_table": case.route_traffic_table,
                    "route_runtime_table": case.route_runtime_table,
                    "business_contract_table": case.business_contract_table,
                    "decoy_tables": tuple(
                        {
                            "database": decoy.database,
                            "table": decoy.table,
                            "row_count": decoy.row_count,
                            "payload_index_name": decoy.payload_index_name,
                            "window_index_name": decoy.window_index_name,
                            "audit_column_name": decoy.audit_column_name,
                            "paused_index_name": decoy.paused_index_name,
                            "payload_padding_bytes": decoy.payload_padding_bytes,
                            "precreate_indexes": decoy.precreate_indexes,
                            "payload_index_prefix_length": decoy.payload_index_prefix_length,
                        }
                        for decoy in case.decoy_tables
                    ),
                },
            ),
        )

import threading
import time
from collections.abc import Mapping

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext

from src.scenarios.tidb.common import json_object, require_sql_success, validate_sql_identifier


class TidbBusinessChangeOnlineDdlPauseResumeInjector(BaseFaultInjector):
    """Create a real paused TiDB ADD UNIQUE INDEX backfill job."""

    _INSERT_BATCH_SIZE = 1000
    _PAUSE_CONFIRM_TIMEOUT_SECONDS = 180
    _RUNTIME_SAMPLE_COUNT = 40
    _REORG_VARIABLES = (
        "tidb_enable_dist_task",
        "tidb_ddl_reorg_worker_cnt",
        "tidb_ddl_reorg_batch_size",
    )
    _TERMINAL_STATES = frozenset({"synced", "cancelled", "canceled", "rollback done", "error"})

    def __init__(self):
        self._ddl_threads: dict[str, threading.Thread] = {}
        self._ddl_connections: dict[str, object] = {}
        self._ddl_done: dict[str, threading.Event] = {}
        self._ddl_errors: dict[str, Exception | None] = {}
        self._job_ids: dict[str, int] = {}
        self._job_id = None
        self._baseline_checksum = None
        self._original_reorg_settings: dict[str, str] = {}
        self.decoy_tables: tuple[dict[str, object], ...] = ()
        self.service_name = None
        self.route_key = None
        self.route_id = None
        self.binding_id = None
        self.change_id = None
        self.commit_id = None
        self.contract_id = None
        self.owner_instance = None
        self.owner_incarnation = None
        self.route_version = None
        self.stream_prefix = None
        self.route_table = None
        self.route_binding_table = None
        self.change_request_table = None
        self.route_lease_table = None
        self.route_owner_table = None
        self.route_commit_table = None
        self.route_traffic_table = None
        self.route_runtime_table = None
        self.business_contract_table = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._prepare_table(context.env)
        self._original_reorg_settings = self._capture_reorg_settings(context.env)
        self._set_slow_reorg_settings(context.env)
        target_started = False
        for decoy_index, decoy in enumerate(self.decoy_tables):
            if decoy_index == 3:
                self._start_ddl(context.env, "target", self.database, self.table, self.index_name)
                self._pause_started_job(context.env, "target", self.database, self.table, require_ingest=True)
                target_started = True
            database = str(decoy["database"])
            table = str(decoy["table"])
            job_key = self._decoy_job_key(database, table)
            self._start_ddl(context.env, job_key, database, table, str(decoy["paused_index_name"]))
            self._pause_started_job(context.env, job_key, database, table, require_ingest=False)
        if not target_started:
            self._start_ddl(context.env, "target", self.database, self.table, self.index_name)
            self._pause_started_job(context.env, "target", self.database, self.table, require_ingest=True)
        self._verify_all_paused_jobs(context.env)
        self._set_paused_reorg_batch_size(context.env)
        self._verify_all_paused_jobs(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        if self._job_id is None:
            self._job_id = self._find_job(context.env, self.database, self.table)[0]
            self._job_ids["target"] = self._job_id
        for decoy in self.decoy_tables:
            database = str(decoy["database"])
            table = str(decoy["table"])
            job_key = self._decoy_job_key(database, table)
            self._job_ids[job_key] = self._find_job(context.env, database, table)[0]
        self._verify_route_metadata(context.env)
        self._verify_all_paused_jobs(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._verify_all_paused_jobs(context.env)
        if self._baseline_checksum is None:
            self._baseline_checksum = self._business_truth(context.env)
        decoys = []
        for decoy in self.decoy_tables:
            job_key = self._decoy_job_key(str(decoy["database"]), str(decoy["table"]))
            decoys.append({**decoy, "job_id": self._job_ids[job_key], "state": "paused"})
        return {
            "bc09_ddl_job": {
                "job_id": self._job_ids["target"],
                "state": "paused",
                "job_type": "add index",
                "database": self.database,
                "table": self.table,
                "index_name": self.index_name,
            },
            "bc09_business_truth": {
                "checksum": list(self._baseline_checksum),
                "row_count": self.row_count,
            },
            "bc09_route_registry": {
                "database": self.database,
                "table": self.route_table,
                "service_name": self.service_name,
                "route_role": "primary",
                "route_state": "active",
                "current_route": True,
                "route_key": self.route_key,
                "binding_id": self.binding_id,
                "route_version": self.route_version,
            },
            "bc09_route_binding": {
                "database": self.database,
                "table": self.route_binding_table,
                "binding_id": self.binding_id,
                "route_id": self.route_id,
                "binding_generation": self.route_version,
                "binding_state": "serving",
                "relation": f"{self.database}.{self.table}",
                "lease_state": "valid",
                "current_binding": True,
            },
            "bc09_change_request": {
                "database": self.database,
                "table": self.change_request_table,
                "change_id": self.change_id,
                "route_id": self.route_id,
                "binding_id": self.binding_id,
                "request_state": "paused",
                "change_kind": "add_unique_index",
                "index_name": self.index_name,
                "column_name": "payload",
                "approved_route_version": self.route_version,
                "current_request": True,
            },
            "bc09_route_lease": {
                "database": self.database,
                "table": self.route_lease_table,
                "binding_id": self.binding_id,
                "fence_epoch": self.route_version * 1000 + 17,
                "fence_state": "held",
                "current_lease": True,
                "owner_instance": self.owner_instance,
                "owner_incarnation": self.owner_incarnation,
                "observed_at": "2026-08-02 23:59:58",
                "valid_until": "2026-08-03 00:00:30",
            },
            "bc09_route_owner": {
                "database": self.database,
                "table": self.route_owner_table,
                "owner_instance": self.owner_instance,
                "service_name": self.service_name,
                "owner_state": "healthy",
                "last_heartbeat": "2026-08-02 23:59:58",
                "lease_expires_at": "2026-08-03 00:00:20",
                "incarnation": self.owner_incarnation,
                "current_owner": True,
            },
            "bc09_route_commit": {
                "database": self.database,
                "table": self.route_commit_table,
                "commit_id": self.commit_id,
                "route_id": self.route_id,
                "binding_id": self.binding_id,
                "route_version": self.route_version,
                "commit_state": "committed",
                "current_commit": True,
                "effective_from": "2024-02-01 00:00:00",
                "effective_until": "2099-12-31 23:59:59",
            },
            "bc09_route_traffic": {
                "database": self.database,
                "table": self.route_traffic_table,
                "assignment_id": f"traffic-{self.route_key.replace('.', '-')}-v{self.route_version}",
                "route_id": self.route_id,
                "binding_id": self.binding_id,
                "service_name": self.service_name,
                "traffic_class": "all_orders",
                "assignment_state": "serving",
                "read_weight": 100,
                "write_weight": 100,
                "current_assignment": True,
            },
            "bc09_route_runtime": {
                "database": self.database,
                "table": self.route_runtime_table,
                "observation_group": f"{self.route_id}/{self.binding_id}",
                "route_id": self.route_id,
                "binding_id": self.binding_id,
                "observed_state": "active",
                "request_origin": "production",
                "read_requests": 18420,
                "write_requests": 931,
                "last_request_at": "2026-08-02 23:59:58",
                "observed_at": "2026-08-02 23:59:00",
                "observation_until": "2026-08-03 00:00:00",
                "current_observation": True,
                "relation": f"{self.database}.{self.table}",
            },
            "bc09_route_resolution": {
                "route_key": self.route_key,
                "route_id": self.route_id,
                "binding_id": self.binding_id,
                "relation": f"{self.database}.{self.table}",
                "approved_index": self.index_name,
                "approved_column": "payload",
            },
            "bc09_decoy_tables": tuple(decoys),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_ddl_threads()

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._stop_ddl_threads()
        job_rows = self._job_rows_for_ids(context.env, tuple(self._job_ids.values()))
        active_job_ids = tuple(
            int(row[0])
            for row in job_rows
            if len(row) >= 3 and str(row[2]).casefold() not in self._TERMINAL_STATES
        )
        if active_job_ids:
            require_sql_success(
                context.env.execute_sql(
                    f"ADMIN CANCEL DDL JOBS {','.join(str(job_id) for job_id in active_job_ids)}"
                ),
                f"cancel BC09 DDL jobs {active_job_ids!r}",
            )
            self._wait_for_terminal(context.env, active_job_ids)
        owned_relations = (
            (self.database, self.table),
            *((str(item["database"]), str(item["table"])) for item in self.decoy_tables),
        )
        for database, table in owned_relations:
            require_sql_success(
                context.env.execute_sql(f"DROP TABLE IF EXISTS {database}.{table}"),
                f"drop BC09 table {database}.{table}",
            )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_table}"),
            f"drop BC09 route registry {self.database}.{self.route_table}",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_binding_table}"),
            f"drop BC09 route bindings {self.database}.{self.route_binding_table}",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.change_request_table}"),
            f"drop BC09 change requests {self.database}.{self.change_request_table}",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_lease_table}"),
            f"drop BC09 route lease fences {self.database}.{self.route_lease_table}",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_owner_table}"),
            f"drop BC09 route owner heartbeats {self.database}.{self.route_owner_table}",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_commit_table}"),
            f"drop BC09 route cutover commits {self.database}.{self.route_commit_table}",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_traffic_table}"),
            f"drop BC09 route traffic assignments {self.database}.{self.route_traffic_table}",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_runtime_table}"),
            f"drop BC09 route runtime observations {self.database}.{self.route_runtime_table}",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.business_contract_table}"),
            f"drop BC09 business query contracts {self.database}.{self.business_contract_table}",
        )
        self._restore_reorg_settings(context.env)
        self._job_ids.clear()
        self._job_id = None
        self._baseline_checksum = None
        self.route_table = None
        self.route_binding_table = None
        self.change_request_table = None
        self.route_lease_table = None
        self.route_owner_table = None
        self.route_commit_table = None
        self.route_traffic_table = None
        self.route_runtime_table = None
        self.business_contract_table = None

    def _configure(self, config: Mapping[str, object], env: object) -> None:
        self.database = validate_sql_identifier(str(config["database"]), "database")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.index_name = validate_sql_identifier(str(config["index_name"]), "index_name")
        self.service_name = str(config["service_name"])
        self.route_key = str(config["route_key"])
        self.route_id = str(config["route_id"])
        self.binding_id = str(config["binding_id"])
        self.change_id = str(config["change_id"])
        self.commit_id = str(config["commit_id"])
        self.contract_id = str(config["contract_id"])
        self.owner_instance = str(config["owner_instance"])
        self.owner_incarnation = int(config["owner_incarnation"])
        self.route_version = int(config["route_version"])
        self.stream_prefix = str(config["stream_prefix"])
        self.row_count = int(config["row_count"])
        self.payload_padding_bytes = int(config["payload_padding_bytes"])
        self.route_table = validate_sql_identifier(str(config["route_table"]), "route_table")
        self.route_binding_table = validate_sql_identifier(
            str(config["route_binding_table"]), "route_binding_table"
        )
        self.change_request_table = validate_sql_identifier(
            str(config["change_request_table"]), "change_request_table"
        )
        self.route_lease_table = validate_sql_identifier(
            str(config["route_lease_table"]), "route_lease_table"
        )
        self.route_owner_table = validate_sql_identifier(
            str(config["route_owner_table"]), "route_owner_table"
        )
        self.route_commit_table = validate_sql_identifier(
            str(config["route_commit_table"]), "route_commit_table"
        )
        self.route_traffic_table = validate_sql_identifier(
            str(config["route_traffic_table"]), "route_traffic_table"
        )
        self.route_runtime_table = validate_sql_identifier(
            str(config["route_runtime_table"]), "route_runtime_table"
        )
        self.business_contract_table = validate_sql_identifier(
            str(config["business_contract_table"]), "business_contract_table"
        )
        self.decoy_tables = tuple(
            {
                "database": validate_sql_identifier(str(item["database"]), "decoy_database"),
                "table": validate_sql_identifier(str(item["table"]), "decoy_table"),
                "row_count": int(item["row_count"]),
                "payload_index_name": validate_sql_identifier(
                    str(item["payload_index_name"]), "decoy_payload_index_name"
                ),
                "window_index_name": validate_sql_identifier(
                    str(item["window_index_name"]), "decoy_window_index_name"
                ),
                "audit_column_name": validate_sql_identifier(
                    str(item["audit_column_name"]), "decoy_audit_column_name"
                ),
                "paused_index_name": validate_sql_identifier(
                    str(item["paused_index_name"]), "decoy_paused_index_name"
                ),
                "payload_padding_bytes": int(item["payload_padding_bytes"]),
                "precreate_indexes": bool(item["precreate_indexes"]),
                "payload_index_prefix_length": int(item["payload_index_prefix_length"]),
            }
            for item in config["decoy_tables"]
        )
        relations = (
            (self.database, self.table),
            *((str(item["database"]), str(item["table"])) for item in self.decoy_tables),
        )
        if len(relations) != len(set(relations)):
            raise ValueError(f"BC09 owned table relations must be unique: relations={relations!r}")
        metadata_relations = (
            (self.database, self.route_table),
            (self.database, self.route_binding_table),
            (self.database, self.change_request_table),
            (self.database, self.route_lease_table),
            (self.database, self.route_owner_table),
            (self.database, self.route_commit_table),
            (self.database, self.route_traffic_table),
            (self.database, self.route_runtime_table),
            (self.database, self.business_contract_table),
        )
        if len(metadata_relations) != len(set(metadata_relations)):
            raise ValueError(f"BC09 metadata relations must be unique: relations={metadata_relations!r}")
        if set(metadata_relations) & set(relations):
            raise ValueError(
                f"BC09 metadata relation conflicts with an owned event table: "
                f"metadata_relations={metadata_relations!r}, relations={relations!r}"
            )

    def _prepare_table(self, env: object) -> None:
        databases = tuple(
            dict.fromkeys((self.database, *(str(item["database"]) for item in self.decoy_tables)))
        )
        for database in databases:
            require_sql_success(
                env.execute_sql(f"CREATE DATABASE IF NOT EXISTS {database}"),
                f"create BC09 database {database}",
            )
        owned_relations = (
            (self.database, self.table),
            *((str(item["database"]), str(item["table"])) for item in self.decoy_tables),
        )
        for database, table in owned_relations:
            require_sql_success(
                env.execute_sql(f"DROP TABLE IF EXISTS {database}.{table}"),
                f"clear BC09 table {database}.{table}",
            )
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_table}"),
            f"clear BC09 route registry {self.database}.{self.route_table}",
        )
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_binding_table}"),
            f"clear BC09 route bindings {self.database}.{self.route_binding_table}",
        )
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.change_request_table}"),
            f"clear BC09 change requests {self.database}.{self.change_request_table}",
        )
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_lease_table}"),
            f"clear BC09 route lease fences {self.database}.{self.route_lease_table}",
        )
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_owner_table}"),
            f"clear BC09 route owner heartbeats {self.database}.{self.route_owner_table}",
        )
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_commit_table}"),
            f"clear BC09 route cutover commits {self.database}.{self.route_commit_table}",
        )
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_traffic_table}"),
            f"clear BC09 route traffic assignments {self.database}.{self.route_traffic_table}",
        )
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.route_runtime_table}"),
            f"clear BC09 route runtime observations {self.database}.{self.route_runtime_table}",
        )
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.business_contract_table}"),
            f"clear BC09 business query contracts {self.database}.{self.business_contract_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.table} ("
                "event_id BIGINT PRIMARY KEY, "
                "tenant_id INT NOT NULL, "
                "event_type VARCHAR(16) NOT NULL, "
                "amount INT NOT NULL, "
                f"payload VARCHAR({64 + self.payload_padding_bytes}) NOT NULL, "
                "event_ts DATETIME NOT NULL, "
                "primary_batch VARCHAR(32) NOT NULL DEFAULT 'live'"
                ")"
            ),
            f"create BC09 table {self.database}.{self.table}",
        )
        self._insert_event_rows(
            env,
            self.database,
            self.table,
            self.row_count,
            self.stream_prefix + "-01",
            self.payload_padding_bytes,
        )
        self._baseline_checksum = self._business_truth(env)
        if self._baseline_checksum[0] != self.row_count:
            raise RuntimeError(
                f"BC09 fixture row count mismatch: table={self.database}.{self.table}, "
                f"expected={self.row_count}, observed={self._baseline_checksum[0]}"
            )
        self._prepare_decoy_tables(env)
        self._prepare_route_registry(env)

    def _insert_event_rows(
        self,
        env: object,
        database: str,
        table: str,
        row_count: int,
        payload_prefix: str,
        payload_padding_bytes: int = 0,
        execute_sql=None,
    ) -> None:
        execute = env.execute_sql if execute_sql is None else execute_sql
        for start in range(1, row_count + 1, self._INSERT_BATCH_SIZE):
            stop = min(start + self._INSERT_BATCH_SIZE - 1, row_count)
            values = ",".join(
                f"({seq}, {1 + (seq * 17) % 100}, "
                f"'{('refund', 'capture', 'review', 'chargeback')[seq % 4]}', "
                f"{100 + (seq * 13) % 10000}, "
                f"{self._payload_expression(payload_prefix, seq, payload_padding_bytes)}, "
                f"TIMESTAMPADD(SECOND, {seq}, '2024-01-01 00:00:00'))"
                for seq in range(start, stop + 1)
            )
            require_sql_success(
                execute(
                    f"INSERT INTO {database}.{table} "
                    "(event_id, tenant_id, event_type, amount, payload, event_ts) "
                    f"VALUES {values}"
                ),
                f"load BC09 rows {start}-{stop} into {database}.{table}",
            )

    @staticmethod
    def _payload_expression(prefix: str, sequence: int, padding_bytes: int) -> str:
        if padding_bytes:
            return f"CONCAT('{prefix}-{sequence:06d}-', RPAD('x', {padding_bytes}, 'x'))"
        return f"'{prefix}-{sequence:06d}'"

    def _prepare_decoy_tables(self, env: object) -> None:
        for decoy_index, decoy in enumerate(self.decoy_tables, start=2):
            database = str(decoy["database"])
            table = str(decoy["table"])
            payload_index = str(decoy["payload_index_name"])
            window_index = str(decoy["window_index_name"])
            audit_column = str(decoy["audit_column_name"])
            payload_key = (
                f"payload({int(decoy['payload_index_prefix_length'])})"
                if int(decoy["payload_index_prefix_length"])
                else "payload"
            )
            inline_indexes = (
                f", KEY {payload_index} ({payload_key}), "
                f"KEY {window_index} (event_type, event_ts)"
                if bool(decoy["precreate_indexes"])
                else ""
            )
            primary_batch_default = "live" if table == "ddl_events_archive" else "archive"
            require_sql_success(
                env.execute_sql(
                    f"CREATE TABLE {database}.{table} ("
                    "event_id BIGINT PRIMARY KEY, "
                    "tenant_id INT NOT NULL, "
                    "event_type VARCHAR(16) NOT NULL, "
                    "amount INT NOT NULL, "
                f"payload VARCHAR({64 + int(decoy['payload_padding_bytes'])}) NOT NULL, "
                f"event_ts DATETIME NOT NULL, "
                f"primary_batch VARCHAR(32) NOT NULL DEFAULT '{primary_batch_default}'"
                f"{inline_indexes}"
                ")"
                ),
                f"create BC09 decoy table {database}.{table}",
            )
            row_count = int(decoy["row_count"])
            if bool(decoy["precreate_indexes"]):
                with env.open_long_running_connection(f"bc09-fixture-load-{database}-{table}") as connection:
                    self._insert_event_rows(
                        env,
                        database,
                        table,
                        row_count,
                        f"bc09-stream-{decoy_index:02d}",
                        int(decoy["payload_padding_bytes"]),
                        execute_sql=lambda sql: self._execute_connection_sql(connection, sql),
                    )
            else:
                self._insert_event_rows(
                    env,
                    database,
                    table,
                    row_count,
                    f"bc09-stream-{decoy_index:02d}",
                    int(decoy["payload_padding_bytes"]),
                )
            if not bool(decoy["precreate_indexes"]):
                require_sql_success(
                    env.execute_sql(
                        f"ALTER TABLE {database}.{table} ADD INDEX {payload_index} (payload)"
                    ),
                    f"add BC09 decoy payload index {database}.{table}.{payload_index}",
                )
                require_sql_success(
                    env.execute_sql(
                        f"ALTER TABLE {database}.{table} "
                        f"ADD INDEX {window_index} (event_type, event_ts)"
                    ),
                    f"add BC09 decoy window index {database}.{table}.{window_index}",
                )
            require_sql_success(
                env.execute_sql(
                    f"ALTER TABLE {database}.{table} "
                    f"ADD COLUMN {audit_column} VARCHAR(32) NOT NULL DEFAULT 'legacy'"
                ),
                f"add BC09 decoy audit column {database}.{table}.{audit_column}",
            )
            self._wait_for_decoy_index(env, database, table, payload_index, ("payload",))
            self._wait_for_decoy_index(env, database, table, window_index, ("event_type", "event_ts"))

    def _prepare_route_registry(self, env: object) -> None:
        decoy_relations = tuple(
            (str(decoy["database"]), str(decoy["table"])) for decoy in self.decoy_tables
        )
        archive_database, archive_table = decoy_relations[0]
        shadow_database, shadow_table = decoy_relations[1]
        replay_database, replay_table = decoy_relations[2]
        canary_database, canary_table = decoy_relations[3]
        mirror_database, mirror_table = decoy_relations[4]
        reporting_database, reporting_table = decoy_relations[5]
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.route_table} ("
                "route_id VARCHAR(64) PRIMARY KEY, "
                "service_name VARCHAR(32) NOT NULL, "
                "route_role VARCHAR(16) NOT NULL, "
                "route_state VARCHAR(16) NOT NULL, "
                "route_key VARCHAR(64) NOT NULL, "
                "binding_id VARCHAR(64) NOT NULL, "
                "route_version INT NOT NULL, "
                "current_route TINYINT NOT NULL, "
                "last_verified DATETIME NOT NULL"
                ")"
            ),
            f"create BC09 route registry {self.database}.{self.route_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.route_binding_table} ("
                "binding_id VARCHAR(64) PRIMARY KEY, "
                "route_id VARCHAR(64) NOT NULL, "
                "route_key VARCHAR(64) NOT NULL, "
                "binding_generation INT NOT NULL, "
                "binding_state VARCHAR(16) NOT NULL, "
                "relation_schema VARCHAR(64) NOT NULL, "
                "relation_table VARCHAR(64) NOT NULL, "
                "lease_state VARCHAR(16) NOT NULL, "
                "current_binding TINYINT NOT NULL, "
                "effective_from DATETIME NOT NULL, "
                "effective_until DATETIME NOT NULL"
                ")"
            ),
            f"create BC09 route bindings {self.database}.{self.route_binding_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.change_request_table} ("
                "change_id VARCHAR(96) PRIMARY KEY, "
                "route_id VARCHAR(64) NOT NULL, "
                "binding_id VARCHAR(64) NOT NULL, "
                "request_state VARCHAR(16) NOT NULL, "
                "change_kind VARCHAR(32) NOT NULL, "
                "index_name VARCHAR(64) NOT NULL, "
                "column_name VARCHAR(64) NOT NULL, "
                "expected_unique TINYINT NOT NULL, "
                "approved_route_version INT NOT NULL, "
                "current_request TINYINT NOT NULL, "
                "submitted_at DATETIME NOT NULL"
                ")"
            ),
            f"create BC09 change requests {self.database}.{self.change_request_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.route_lease_table} ("
                "binding_id VARCHAR(64) NOT NULL, "
                "fence_epoch BIGINT NOT NULL, "
                "fence_state VARCHAR(16) NOT NULL, "
                "current_lease TINYINT NOT NULL, "
                "owner_instance VARCHAR(64) NOT NULL, "
                "owner_incarnation BIGINT NOT NULL, "
                "observed_at DATETIME NOT NULL, "
                "valid_until DATETIME NOT NULL, "
                "PRIMARY KEY (binding_id, fence_epoch)"
                ")"
            ),
            f"create BC09 route lease fences {self.database}.{self.route_lease_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.route_owner_table} ("
                "owner_instance VARCHAR(64) PRIMARY KEY, "
                "service_name VARCHAR(32) NOT NULL, "
                "owner_state VARCHAR(16) NOT NULL, "
                "last_heartbeat DATETIME NOT NULL, "
                "lease_expires_at DATETIME NOT NULL, "
                "incarnation BIGINT NOT NULL, "
                "current_owner TINYINT NOT NULL"
                ")"
            ),
            f"create BC09 route owner heartbeats {self.database}.{self.route_owner_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.route_commit_table} ("
                "commit_id VARCHAR(96) PRIMARY KEY, "
                "route_id VARCHAR(64) NOT NULL, "
                "route_key VARCHAR(64) NOT NULL, "
                "binding_id VARCHAR(64) NOT NULL, "
                "route_version INT NOT NULL, "
                "commit_state VARCHAR(16) NOT NULL, "
                "current_commit TINYINT NOT NULL, "
                "effective_from DATETIME NOT NULL, "
                "effective_until DATETIME NOT NULL"
                ")"
            ),
            f"create BC09 route cutover commits {self.database}.{self.route_commit_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.route_traffic_table} ("
                "assignment_id VARCHAR(96) PRIMARY KEY, "
                "route_id VARCHAR(64) NOT NULL, "
                "binding_id VARCHAR(64) NOT NULL, "
                "service_name VARCHAR(32) NOT NULL, "
                "traffic_class VARCHAR(32) NOT NULL, "
                "assignment_state VARCHAR(16) NOT NULL, "
                "read_weight INT NOT NULL, "
                "write_weight INT NOT NULL, "
                "current_assignment TINYINT NOT NULL, "
                "effective_from DATETIME NOT NULL, "
                "effective_until DATETIME NOT NULL"
                ")"
            ),
            f"create BC09 route traffic assignments {self.database}.{self.route_traffic_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.route_runtime_table} ("
                "observation_id VARCHAR(96) PRIMARY KEY, "
                "route_id VARCHAR(64) NOT NULL, "
                "binding_id VARCHAR(64) NOT NULL, "
                "service_name VARCHAR(32) NOT NULL, "
                "route_key VARCHAR(64) NOT NULL, "
                "observed_state VARCHAR(16) NOT NULL, "
                "request_origin VARCHAR(16) NOT NULL, "
                "read_requests BIGINT NOT NULL, "
                "write_requests BIGINT NOT NULL, "
                "last_request_at DATETIME NOT NULL, "
                "observed_at DATETIME NOT NULL, "
                "observation_until DATETIME NOT NULL, "
                "current_observation TINYINT NOT NULL, "
                "relation_schema VARCHAR(64) NOT NULL, "
                "relation_table VARCHAR(64) NOT NULL"
                ")"
            ),
            f"create BC09 route runtime observations {self.database}.{self.route_runtime_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.business_contract_table} ("
                "contract_id VARCHAR(96) PRIMARY KEY, "
                "service_name VARCHAR(32) NOT NULL, "
                "route_key VARCHAR(64) NOT NULL, "
                "query_name VARCHAR(96) NOT NULL, "
                "contract_state VARCHAR(16) NOT NULL, "
                "expected_row_count INT NOT NULL, "
                "expected_amount_sum BIGINT NOT NULL, "
                "expected_min_event_id BIGINT NOT NULL, "
                "expected_max_event_id BIGINT NOT NULL, "
                "expected_payload_count INT NOT NULL, "
                "expected_payload_digest BIGINT NOT NULL, "
                "current_contract TINYINT NOT NULL, "
                "effective_from DATETIME NOT NULL, "
                "effective_until DATETIME NOT NULL"
                ")"
            ),
            f"create BC09 business query contracts {self.database}.{self.business_contract_table}",
        )
        route_rows = (
            (self.route_id, self.service_name, "primary", "active", self.route_key, self.binding_id, self.route_version, 1),
            ("order-events-primary-02", "orders-api", "primary", "draining", "orders.events", "binding-orders-events-v42", 42, 0),
            ("order-events-shadow-03", "orders-api", "shadow", "active", "orders.events", "binding-orders-events-shadow-v43", 43, 0),
            ("order-events-primary-04", "replay-worker", "primary", "active", "orders.events", "binding-orders-events-replay-v19", 19, 1),
            ("order-events-canary-05", "orders-api", "canary", "active", "orders.events", "binding-orders-events-canary-v43", 43, 1),
            ("order-events-mirror-06", "orders-api", "mirror", "active", "orders.events", "binding-orders-events-mirror-v43", 43, 1),
            ("order-events-reporting-07", "orders-api", "reporting", "active", "orders.events", "binding-orders-events-reporting-v43", 43, 1),
            ("order-events-prewarm-08", "orders-api", "primary", "active", "orders.events", "binding-orders-events-prewarm-v44", 44, 1),
            ("order-events-prewarm-09", "orders-api", "primary", "active", "orders.events", "binding-orders-events-prewarm-v45", 45, 1),
            ("order-events-prewarm-10", "orders-api", "primary", "active", "orders.events", "binding-orders-events-prewarm-v46", 46, 1),
            ("order-events-prewarm-11", "orders-api", "primary", "active", "orders.events", "binding-orders-events-prewarm-v47", 47, 1),
            ("order-events-prewarm-12", "orders-api", "primary", "active", "orders.events", "binding-orders-events-prewarm-v48", 48, 1),
        )
        route_values = ",".join(
            "(" + ", ".join(
                (
                    f"'{route_id}'",
                    f"'{service}'",
                    f"'{role}'",
                    f"'{state}'",
                    f"'{route_key}'",
                    f"'{binding_id}'",
                    str(version),
                    str(current),
                    "'2024-02-01 00:00:00'",
                )
            ) + ")"
            for route_id, service, role, state, route_key, binding_id, version, current in route_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.route_table} "
                "(route_id, service_name, route_role, route_state, route_key, binding_id, "
                f"route_version, current_route, last_verified) VALUES {route_values}"
            ),
            f"load BC09 route registry {self.database}.{self.route_table}",
        )
        binding_rows = (
            (self.binding_id, self.route_id, "serving", self.database, self.table, "valid", 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59", self.route_version),
            ("binding-orders-events-v42", "order-events-primary-02", "draining", archive_database, archive_table, "expired", 0, "2024-01-01 00:00:00", "2024-01-31 23:59:59", 42),
            ("binding-orders-events-shadow-v43", "order-events-shadow-03", "shadow", shadow_database, shadow_table, "valid", 0, "2024-02-01 00:00:00", "2099-12-31 23:59:59", 43),
            ("binding-orders-events-replay-v19", "order-events-primary-04", "replay", replay_database, replay_table, "valid", 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59", 19),
            ("binding-orders-events-canary-v43", "order-events-canary-05", "canary", canary_database, canary_table, "valid", 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59", 43),
            ("binding-orders-events-mirror-v43", "order-events-mirror-06", "mirror", mirror_database, mirror_table, "valid", 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59", 43),
            ("binding-orders-events-reporting-v43", "order-events-reporting-07", "reporting", reporting_database, reporting_table, "valid", 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59", 43),
            ("binding-orders-events-prewarm-v44", "order-events-prewarm-08", "serving", self.database, "ddl_events_shadow", "valid", 1, "2026-08-03 00:00:00", "2099-12-31 23:59:59", 44),
            ("binding-orders-events-prewarm-v45", "order-events-prewarm-09", "serving", self.database, "ddl_events_canary", "valid", 1, "2026-08-04 00:00:00", "2099-12-31 23:59:59", 45),
            ("binding-orders-events-prewarm-v46", "order-events-prewarm-10", "serving", self.database, "ddl_events_mirror", "valid", 1, "2026-08-05 00:00:00", "2099-12-31 23:59:59", 46),
            ("binding-orders-events-prewarm-v47", "order-events-prewarm-11", "serving", self.database, "ddl_events_replay", "valid", 1, "2026-08-02 00:00:00", "2099-12-31 23:59:59", 47),
            ("binding-orders-events-prewarm-v48", "order-events-prewarm-12", "serving", self.database, "ddl_events_archive", "valid", 1, "2026-08-02 00:00:00", "2099-12-31 23:59:59", 48),
        )
        binding_values = ",".join(
            "(" + ", ".join(
                (
                    f"'{binding_id}'",
                    f"'{route_id}'",
                    f"'{self.route_key}'",
                    str(generation),
                    f"'{binding_state}'",
                    f"'{relation_schema}'",
                    f"'{relation_table}'",
                    f"'{lease_state}'",
                    str(current),
                    f"'{effective_from}'",
                    f"'{effective_until}'",
                )
            ) + ")"
            for binding_id, route_id, binding_state, relation_schema, relation_table, lease_state, current, effective_from, effective_until, generation in binding_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.route_binding_table} "
                "(binding_id, route_id, route_key, binding_generation, binding_state, relation_schema, "
                f"relation_table, lease_state, current_binding, effective_from, effective_until) VALUES {binding_values}"
            ),
            f"load BC09 route bindings {self.database}.{self.route_binding_table}",
        )
        request_rows = (
            (self.change_id, self.route_id, self.binding_id, "paused", "add_unique_index", self.index_name, "payload", 1, self.route_version, 1),
            ("chg-orders-events-v42-payload-unique", "order-events-primary-02", "binding-orders-events-v42", "superseded", "add_unique_index", self.index_name, "payload", 1, 42, 0),
            ("chg-orders-events-shadow-v43-payload-unique", "order-events-shadow-03", "binding-orders-events-shadow-v43", "paused", "add_unique_index", self.index_name, "payload", 1, 43, 0),
            ("chg-orders-events-replay-v19-payload-unique", "order-events-primary-04", "binding-orders-events-replay-v19", "paused", "add_unique_index", self.index_name, "payload", 1, 19, 1),
            ("chg-orders-events-canary-v43-payload-unique", "order-events-canary-05", "binding-orders-events-canary-v43", "paused", "add_unique_index", self.index_name, "payload", 1, 43, 1),
            ("chg-orders-events-mirror-v43-payload-unique", "order-events-mirror-06", "binding-orders-events-mirror-v43", "paused", "add_unique_index", self.index_name, "payload", 1, 43, 1),
            ("chg-orders-events-reporting-v43-payload-unique", "order-events-reporting-07", "binding-orders-events-reporting-v43", "paused", "add_unique_index", self.index_name, "payload", 1, 43, 1),
            ("chg-orders-events-prewarm-v44-payload-next", "order-events-prewarm-08", "binding-orders-events-prewarm-v44", "approved", "add_unique_index", self.index_name, "payload", 1, 44, 1),
            ("chg-orders-events-prewarm-v45-payload-rollout", "order-events-prewarm-09", "binding-orders-events-prewarm-v45", "approved", "add_unique_index", self.index_name, "payload", 1, 45, 1),
            ("chg-orders-events-prewarm-v46-payload-next", "order-events-prewarm-10", "binding-orders-events-prewarm-v46", "approved", "add_unique_index", self.index_name, "payload", 1, 46, 1),
            ("chg-orders-events-prewarm-v47-payload-next", "order-events-prewarm-11", "binding-orders-events-prewarm-v47", "approved", "add_unique_index", self.index_name, "payload", 1, 47, 1),
            ("chg-orders-events-prewarm-v48-payload-next", "order-events-prewarm-12", "binding-orders-events-prewarm-v48", "paused", "add_unique_index", self.index_name, "payload", 1, 48, 1),
        )
        request_values = ",".join(
            "(" + ", ".join(
                (
                    f"'{change_id}'",
                    f"'{route_id}'",
                    f"'{binding_id}'",
                    f"'{request_state}'",
                    f"'{change_kind}'",
                    f"'{index_name}'",
                    f"'{column_name}'",
                    str(expected_unique),
                    str(approved_version),
                    str(current),
                    "'2024-02-01 00:00:00'",
                )
            ) + ")"
            for change_id, route_id, binding_id, request_state, change_kind, index_name, column_name, expected_unique, approved_version, current in request_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.change_request_table} "
                "(change_id, route_id, binding_id, request_state, change_kind, index_name, column_name, "
                f"expected_unique, approved_route_version, current_request, submitted_at) VALUES {request_values}"
            ),
            f"load BC09 change requests {self.database}.{self.change_request_table}",
        )
        lease_rows = (
            (self.binding_id, self.route_version * 1000 + 17, "held", 1, self.owner_instance, self.owner_incarnation, "2026-08-02 23:59:58", "2026-08-03 00:00:30"),
            ("binding-orders-events-v42", 42001, "released", 0, "orders-router-1", 20240131001, "2024-01-31 23:59:58", "2024-01-31 23:59:59"),
            ("binding-orders-events-shadow-v43", 43011, "held", 0, "orders-router-shadow", 20260802053, "2026-08-02 23:59:57", "2026-08-03 00:00:20"),
            ("binding-orders-events-replay-v19", 19009, "held", 1, "replay-router-1", 20260802054, "2026-08-02 23:59:57", "2026-08-03 00:00:20"),
            ("binding-orders-events-canary-v43", 43012, "held", 1, "orders-router-canary", 20260802051, "2026-08-02 23:59:57", "2026-08-03 00:00:20"),
            ("binding-orders-events-mirror-v43", 43013, "held", 1, "orders-router-mirror", 20260802052, "2026-08-02 23:59:57", "2026-08-03 00:00:20"),
            ("binding-orders-events-reporting-v43", 43014, "held", 1, "reporting-router-1", 20260802055, "2026-08-02 23:59:57", "2026-08-03 00:00:20"),
            ("binding-orders-events-prewarm-v44", 44001, "held", 1, "orders-router-prewarm-44", 20260802044, "2026-08-02 23:59:57", "2026-08-03 00:00:30"),
            ("binding-orders-events-prewarm-v45", 45001, "held", 1, "orders-router-prewarm-45", 20260802045, "2026-08-02 23:59:57", "2026-08-04 00:00:30"),
            ("binding-orders-events-prewarm-v46", 46001, "held", 1, "orders-router-prewarm-46", 20260802046, "2026-08-02 23:59:57", "2026-08-05 00:00:30"),
            ("binding-orders-events-prewarm-v47", 47003, "held", 1, "orders-router-prewarm-47", 20260802047, "2026-08-02 23:58:30", "2026-08-02 23:59:58"),
            ("binding-orders-events-prewarm-v48", 48004, "held", 1, "orders-router-prewarm-48", 20260802048, "2026-08-02 23:59:58", "2026-08-03 00:00:30"),
        )
        lease_values = ",".join(
            "(" + ", ".join(
                (
                    f"'{binding_id}'",
                    str(fence_epoch),
                    f"'{fence_state}'",
                    str(current_lease),
                    f"'{owner_instance}'",
                    str(owner_incarnation),
                    f"'{observed_at}'",
                    f"'{valid_until}'",
                )
            ) + ")"
            for binding_id, fence_epoch, fence_state, current_lease, owner_instance, owner_incarnation, observed_at, valid_until in lease_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.route_lease_table} "
                "(binding_id, fence_epoch, fence_state, current_lease, owner_instance, owner_incarnation, observed_at, valid_until) "
                f"VALUES {lease_values}"
            ),
            f"load BC09 route lease fences {self.database}.{self.route_lease_table}",
        )
        owner_rows = (
            (self.owner_instance, self.service_name, "healthy", "2026-08-02 23:59:58", "2026-08-03 00:00:20", self.owner_incarnation, 1),
            ("orders-router-prewarm-44", "orders-api", "healthy", "2026-08-02 23:59:57", "2026-08-03 00:00:30", 20260802044, 1),
            ("orders-router-prewarm-45", "orders-api", "healthy", "2026-08-02 23:59:57", "2026-08-04 00:00:30", 20260802045, 1),
            ("orders-router-prewarm-46", "orders-api", "healthy", "2026-08-02 23:59:57", "2026-08-05 00:00:30", 20260802046, 1),
            ("orders-router-prewarm-47", "orders-api", "healthy", "2026-08-02 23:58:30", "2026-08-02 23:59:58", 20260802047, 1),
            ("orders-router-prewarm-48", "orders-api", "healthy", "2026-08-02 23:59:58", "2026-08-03 00:00:30", 20260802048, 1),
            ("orders-router-canary", "orders-api", "healthy", "2026-08-02 23:59:57", "2026-08-03 00:00:20", 20260802051, 1),
            ("orders-router-mirror", "orders-api", "healthy", "2026-08-02 23:59:57", "2026-08-03 00:00:20", 20260802052, 1),
            ("orders-router-shadow", "orders-api", "healthy", "2026-08-02 23:59:57", "2026-08-03 00:00:20", 20260802053, 0),
            ("replay-router-1", "replay-worker", "healthy", "2026-08-02 23:59:57", "2026-08-03 00:00:20", 20260802054, 1),
            ("reporting-router-1", "orders-api", "healthy", "2026-08-02 23:59:57", "2026-08-03 00:00:20", 20260802055, 1),
        )
        owner_values = ",".join(
            "(" + ", ".join(
                (
                    f"'{owner_instance}'",
                    f"'{service_name}'",
                    f"'{owner_state}'",
                    f"'{last_heartbeat}'",
                    f"'{lease_expires_at}'",
                    str(incarnation),
                    str(current_owner),
                )
            ) + ")"
            for owner_instance, service_name, owner_state, last_heartbeat, lease_expires_at, incarnation, current_owner in owner_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.route_owner_table} "
                "(owner_instance, service_name, owner_state, last_heartbeat, lease_expires_at, incarnation, current_owner) "
                f"VALUES {owner_values}"
            ),
            f"load BC09 route owner heartbeats {self.database}.{self.route_owner_table}",
        )
        commit_rows = (
            (self.commit_id, self.route_id, self.route_key, self.binding_id, self.route_version, "committed", 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59"),
            ("commit-orders-events-v42", "order-events-primary-02", "orders.events", "binding-orders-events-v42", 42, "retired", 0, "2024-01-01 00:00:00", "2024-01-31 23:59:59"),
            ("commit-orders-events-shadow-v43", "order-events-shadow-03", "orders.events", "binding-orders-events-shadow-v43", 43, "committed", 0, "2024-02-01 00:00:00", "2099-12-31 23:59:59"),
            ("commit-orders-events-replay-v19", "order-events-primary-04", "orders.events", "binding-orders-events-replay-v19", 19, "committed", 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59"),
            ("commit-orders-events-canary-v43", "order-events-canary-05", "orders.events", "binding-orders-events-canary-v43", 43, "committed", 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59"),
            ("commit-orders-events-mirror-v43", "order-events-mirror-06", "orders.events", "binding-orders-events-mirror-v43", 43, "committed", 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59"),
            ("commit-orders-events-reporting-v43", "order-events-reporting-07", "orders.events", "binding-orders-events-reporting-v43", 43, "committed", 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59"),
            ("commit-orders-events-prewarm-v44", "order-events-prewarm-08", "orders.events", "binding-orders-events-prewarm-v44", 44, "scheduled", 1, "2026-08-03 00:00:00", "2099-12-31 23:59:59"),
            ("commit-orders-events-prewarm-v45", "order-events-prewarm-09", "orders.events", "binding-orders-events-prewarm-v45", 45, "scheduled", 1, "2026-08-04 00:00:00", "2099-12-31 23:59:59"),
            ("commit-orders-events-prewarm-v46", "order-events-prewarm-10", "orders.events", "binding-orders-events-prewarm-v46", 46, "scheduled", 1, "2026-08-05 00:00:00", "2099-12-31 23:59:59"),
            ("commit-orders-events-prewarm-v47", "order-events-prewarm-11", "orders.events", "binding-orders-events-prewarm-v47", 47, "committed", 1, "2026-08-02 00:00:00", "2026-08-02 23:59:58"),
            ("commit-orders-events-prewarm-v48", "order-events-prewarm-12", "orders.events", "binding-orders-events-prewarm-v48", 48, "committed", 1, "2026-08-02 00:00:00", "2099-12-31 23:59:59"),
        )
        commit_values = ",".join(
            "(" + ", ".join(
                (
                    f"'{commit_id}'",
                    f"'{route_id}'",
                    f"'{route_key}'",
                    f"'{binding_id}'",
                    str(route_version),
                    f"'{commit_state}'",
                    str(current_commit),
                    f"'{effective_from}'",
                    f"'{effective_until}'",
                )
            ) + ")"
            for commit_id, route_id, route_key, binding_id, route_version, commit_state, current_commit, effective_from, effective_until in commit_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.route_commit_table} "
                "(commit_id, route_id, route_key, binding_id, route_version, commit_state, current_commit, effective_from, effective_until) "
                f"VALUES {commit_values}"
            ),
            f"load BC09 route cutover commits {self.database}.{self.route_commit_table}",
        )
        traffic_rows = (
            (f"traffic-{self.route_key.replace('.', '-')}-v{self.route_version}", self.route_id, self.binding_id, self.service_name, "all_orders", "serving", 100, 100, 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59"),
            ("traffic-orders-events-v42", "order-events-primary-02", "binding-orders-events-v42", "orders-api", "all_orders", "draining", 0, 0, 0, "2024-01-01 00:00:00", "2024-01-31 23:59:59"),
            ("traffic-orders-events-shadow-v43", "order-events-shadow-03", "binding-orders-events-shadow-v43", "orders-api", "shadow", "shadow", 0, 0, 0, "2024-02-01 00:00:00", "2099-12-31 23:59:59"),
            ("traffic-orders-events-replay-v19", "order-events-primary-04", "binding-orders-events-replay-v19", "replay-worker", "replay", "shadow", 0, 0, 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59"),
            ("traffic-orders-events-canary-v43", "order-events-canary-05", "binding-orders-events-canary-v43", "orders-api", "canary", "shadow", 0, 0, 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59"),
            ("traffic-orders-events-mirror-v43", "order-events-mirror-06", "binding-orders-events-mirror-v43", "orders-api", "mirror", "shadow", 0, 0, 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59"),
            ("traffic-orders-events-reporting-v43", "order-events-reporting-07", "binding-orders-events-reporting-v43", "orders-api", "reporting", "shadow", 0, 0, 1, "2024-02-01 00:00:00", "2099-12-31 23:59:59"),
            ("traffic-orders-events-prewarm-v44", "order-events-prewarm-08", "binding-orders-events-prewarm-v44", "orders-api", "all_orders", "prewarm", 0, 0, 1, "2026-08-03 00:00:00", "2099-12-31 23:59:59"),
            ("traffic-orders-events-prewarm-v45", "order-events-prewarm-09", "binding-orders-events-prewarm-v45", "orders-api", "all_orders", "prewarm", 0, 0, 1, "2026-08-04 00:00:00", "2099-12-31 23:59:59"),
            ("traffic-orders-events-prewarm-v46", "order-events-prewarm-10", "binding-orders-events-prewarm-v46", "orders-api", "all_orders", "prewarm", 0, 0, 1, "2026-08-05 00:00:00", "2099-12-31 23:59:59"),
            ("traffic-orders-events-prewarm-v47", "order-events-prewarm-11", "binding-orders-events-prewarm-v47", "orders-api", "all_orders", "draining", 0, 0, 1, "2026-08-02 00:00:00", "2026-08-02 23:59:58"),
            ("traffic-orders-events-prewarm-v48", "order-events-prewarm-12", "binding-orders-events-prewarm-v48", "orders-api", "all_orders", "serving", 100, 100, 1, "2026-08-02 00:00:00", "2099-12-31 23:59:59"),
        )
        traffic_values = ",".join(
            "(" + ", ".join(
                (
                    f"'{assignment_id}'",
                    f"'{route_id}'",
                    f"'{binding_id}'",
                    f"'{service_name}'",
                    f"'{traffic_class}'",
                    f"'{assignment_state}'",
                    str(read_weight),
                    str(write_weight),
                    str(current_assignment),
                    f"'{effective_from}'",
                    f"'{effective_until}'",
                )
            ) + ")"
            for assignment_id, route_id, binding_id, service_name, traffic_class, assignment_state, read_weight, write_weight, current_assignment, effective_from, effective_until in traffic_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.route_traffic_table} "
                "(assignment_id, route_id, binding_id, service_name, traffic_class, assignment_state, read_weight, write_weight, current_assignment, effective_from, effective_until) "
                f"VALUES {traffic_values}"
            ),
            f"load BC09 route traffic assignments {self.database}.{self.route_traffic_table}",
        )
        runtime_rows = (
            (f"runtime-{self.route_key.replace('.', '-')}-v{self.route_version}", self.route_id, self.binding_id, self.service_name, self.route_key, "active", "production", 18420, 931, "2026-08-02 23:59:58", "2026-08-02 23:59:00", "2026-08-03 00:00:00", 1, self.database, self.table),
            ("runtime-orders-events-v42", "order-events-primary-02", "binding-orders-events-v42", "orders-api", "orders.events", "retired", "production", 0, 0, "2024-01-31 23:59:58", "2024-01-31 23:59:00", "2024-01-31 23:59:59", 0, self.database, "ddl_events_archive"),
            ("runtime-orders-events-shadow-v43", "order-events-shadow-03", "binding-orders-events-shadow-v43", "orders-api", "orders.events", "shadow", "shadow", 302, 0, "2026-08-02 23:59:20", "2026-08-02 23:59:00", "2026-08-03 00:00:00", 1, self.database, "ddl_events_shadow"),
            ("runtime-orders-events-replay-v19", "order-events-primary-04", "binding-orders-events-replay-v19", "replay-worker", "orders.events", "replay", "replay", 1800, 0, "2026-08-02 23:59:57", "2026-08-02 23:59:00", "2026-08-03 00:00:00", 1, self.database, "ddl_events_replay"),
            ("runtime-orders-events-canary-v43", "order-events-canary-05", "binding-orders-events-canary-v43", "orders-api", "orders.events", "canary", "canary", 740, 12, "2026-08-02 23:59:56", "2026-08-02 23:59:00", "2026-08-03 00:00:00", 1, self.database, "ddl_events_canary"),
            ("runtime-orders-events-mirror-v43", "order-events-mirror-06", "binding-orders-events-mirror-v43", "orders-api", "orders.events", "mirror", "mirror", 690, 8, "2026-08-02 23:59:55", "2026-08-02 23:59:00", "2026-08-03 00:00:00", 1, self.database, "ddl_events_mirror"),
            ("runtime-orders-events-reporting-v43", "order-events-reporting-07", "binding-orders-events-reporting-v43", "orders-api", "orders.events", "reporting", "reporting", 215, 0, "2026-08-02 23:59:54", "2026-08-02 23:59:00", "2026-08-03 00:00:00", 1, "benchops_bc09_reporting", "ddl_events"),
            ("runtime-orders-events-prewarm-v44", "order-events-prewarm-08", "binding-orders-events-prewarm-v44", "orders-api", "orders.events", "warming", "prewarm", 0, 0, "2024-01-01 00:00:00", "2026-08-02 23:59:00", "2026-08-03 00:00:00", 1, self.database, "ddl_events_shadow"),
            ("runtime-orders-events-prewarm-v45", "order-events-prewarm-09", "binding-orders-events-prewarm-v45", "orders-api", "orders.events", "warming", "prewarm", 0, 0, "2024-01-01 00:00:00", "2026-08-02 23:59:00", "2026-08-04 00:00:00", 1, self.database, "ddl_events_canary"),
            ("runtime-orders-events-prewarm-v46", "order-events-prewarm-10", "binding-orders-events-prewarm-v46", "orders-api", "orders.events", "warming", "prewarm", 0, 0, "2024-01-01 00:00:00", "2026-08-02 23:59:00", "2026-08-05 00:00:00", 1, self.database, "ddl_events_mirror"),
            ("runtime-orders-events-prewarm-v47", "order-events-prewarm-11", "binding-orders-events-prewarm-v47", "orders-api", "orders.events", "draining", "prewarm", 31, 0, "2026-08-02 23:59:57", "2026-08-02 23:59:00", "2026-08-02 23:59:58", 1, self.database, "ddl_events_replay"),
            ("runtime-orders-events-prewarm-v48", "order-events-prewarm-12", "binding-orders-events-prewarm-v48", "orders-api", "orders.events", "active", "production", 19700, 1060, "2026-08-02 23:59:58", "2026-08-02 23:59:00", "2026-08-03 00:00:00", 1, self.database, "ddl_events_archive"),
        )
        runtime_samples = []
        for row in runtime_rows:
            read_per_sample, read_remainder = divmod(int(row[7]), self._RUNTIME_SAMPLE_COUNT)
            write_per_sample, write_remainder = divmod(int(row[8]), self._RUNTIME_SAMPLE_COUNT)
            for sample_no in range(self._RUNTIME_SAMPLE_COUNT):
                runtime_samples.append(
                    (
                        f"{row[0]}-sample-{sample_no:02d}",
                        *row[1:7],
                        read_per_sample + (sample_no < read_remainder),
                        write_per_sample + (sample_no < write_remainder),
                        *row[9:],
                    )
                )
        runtime_rows = runtime_samples
        runtime_values = ",".join(
            "(" + ", ".join(
                (
                    f"'{observation_id}'",
                    f"'{route_id}'",
                    f"'{binding_id}'",
                    f"'{service_name}'",
                    f"'{route_key}'",
                    f"'{observed_state}'",
                    f"'{request_origin}'",
                    str(read_requests),
                    str(write_requests),
                    f"'{last_request_at}'",
                    f"'{observed_at}'",
                    f"'{observation_until}'",
                    str(current_observation),
                    f"'{relation_schema}'",
                    f"'{relation_table}'",
                )
            ) + ")"
            for observation_id, route_id, binding_id, service_name, route_key, observed_state, request_origin, read_requests, write_requests, last_request_at, observed_at, observation_until, current_observation, relation_schema, relation_table in runtime_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.route_runtime_table} "
                "(observation_id, route_id, binding_id, service_name, route_key, observed_state, request_origin, read_requests, write_requests, "
                "last_request_at, observed_at, observation_until, current_observation, relation_schema, relation_table) "
                f"VALUES {runtime_values}"
            ),
            f"load BC09 route runtime observations {self.database}.{self.route_runtime_table}",
        )
        customer_truth = self._customer_query_truth(env, self.database, self.table)
        archive_truth = self._customer_query_truth(env, archive_database, archive_table)
        contract_rows = (
            (
                "contract-orders-events-customer-v6",
                "orders-api",
                "orders.events",
                "customer_reconciliation_v6",
                "active",
                *archive_truth,
                0,
                "2024-02-01 00:00:00",
                "2026-08-02 12:00:00",
            ),
            (
                self.contract_id,
                self.service_name,
                self.route_key,
                "customer_reconciliation_v7",
                "active",
                *customer_truth,
                1,
                "2026-08-02 12:00:00",
                "2026-08-03 00:00:00",
            ),
            (
                "contract-orders-events-customer-v8",
                "orders-api",
                "orders.events",
                "customer_reconciliation_v8",
                "active",
                *archive_truth,
                1,
                "2026-08-03 00:00:00",
                "2099-12-31 23:59:59",
            ),
            *(
                (
                    f"contract-noise-{number:02d}",
                    "orders-api" if number % 2 else "batch-router",
                    "orders.events" if number % 3 else "orders.archive",
                    f"customer_reconciliation_v{number}",
                    "retired" if number % 2 else "shadow",
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    "2024-02-01 00:00:00",
                    "2099-12-31 23:59:59",
                )
                for number in range(1, 12)
            ),
        )
        contract_values = ",".join(
            "(" + ", ".join(
                (
                    f"'{contract_id}'",
                    f"'{service_name}'",
                    f"'{route_key}'",
                    f"'{query_name}'",
                    f"'{contract_state}'",
                    str(expected_row_count),
                    str(expected_amount_sum),
                    str(expected_min_event_id),
                    str(expected_max_event_id),
                    str(expected_payload_count),
                    str(expected_payload_digest),
                    str(current_contract),
                    f"'{effective_from}'",
                    f"'{effective_until}'",
                )
            ) + ")"
            for contract_id, service_name, route_key, query_name, contract_state, expected_row_count, expected_amount_sum, expected_min_event_id, expected_max_event_id, expected_payload_count, expected_payload_digest, current_contract, effective_from, effective_until in contract_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.business_contract_table} "
                "(contract_id, service_name, route_key, query_name, contract_state, expected_row_count, "
                "expected_amount_sum, expected_min_event_id, expected_max_event_id, expected_payload_count, "
                "expected_payload_digest, current_contract, effective_from, effective_until) "
                f"VALUES {contract_values}"
            ),
            f"load BC09 business query contracts {self.database}.{self.business_contract_table}",
        )

    def _wait_for_decoy_index(
        self,
        env: object,
        database: str,
        table: str,
        index_name: str,
        columns: tuple[str, ...],
    ) -> None:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            rows = json_object(
                env.execute_sql(
                    "SELECT KEY_NAME, SEQ_IN_INDEX, COLUMN_NAME "
                    "FROM information_schema.tidb_indexes "
                    f"WHERE TABLE_SCHEMA = '{database}' AND TABLE_NAME = '{table}' "
                    f"AND KEY_NAME = '{index_name}' ORDER BY SEQ_IN_INDEX"
                ),
                f"verify BC09 decoy index {database}.{table}.{index_name}",
            )["result"]
            observed = tuple(str(row[2]) for row in rows if len(row) >= 3)
            if observed == columns:
                return
            time.sleep(0.2)
        raise RuntimeError(
            f"BC09 decoy index did not become visible: database={database!r}, "
            f"table={table!r}, index={index_name!r}, expected_columns={columns!r}, observed={observed!r}"
        )

    def _verify_route_metadata(self, env: object) -> None:
        route_rows = json_object(
            env.execute_sql(
                f"SELECT route_id, binding_id, route_key, route_version, current_route "
                f"FROM {self.database}.{self.route_table} WHERE route_id = '{self.route_id}'"
            ),
            "verify BC09 active route metadata",
        )["result"]
        expected_route = [[self.route_id, self.binding_id, self.route_key, self.route_version, 1]]
        if route_rows != expected_route:
            raise RuntimeError(f"BC09 active route metadata changed: expected={expected_route!r}, observed={route_rows!r}")
        binding_rows = json_object(
            env.execute_sql(
                f"SELECT binding_id, route_id, binding_generation, binding_state, relation_schema, "
                f"relation_table, lease_state, current_binding "
                f"FROM {self.database}.{self.route_binding_table} "
                f"WHERE binding_id = '{self.binding_id}'"
            ),
            "verify BC09 serving route binding",
        )["result"]
        expected_binding = [[
            self.binding_id,
            self.route_id,
            self.route_version,
            "serving",
            self.database,
            self.table,
            "valid",
            1,
        ]]
        if binding_rows != expected_binding:
            raise RuntimeError(f"BC09 serving route binding changed: expected={expected_binding!r}, observed={binding_rows!r}")
        request_rows = json_object(
            env.execute_sql(
                f"SELECT change_id, binding_id, request_state, change_kind, index_name, column_name, "
                f"expected_unique, approved_route_version, current_request "
                f"FROM {self.database}.{self.change_request_table} "
                f"WHERE change_id = '{self.change_id}'"
            ),
            "verify BC09 approved change request",
        )["result"]
        expected_request = [[
            self.change_id,
            self.binding_id,
            "paused",
            "add_unique_index",
            self.index_name,
            "payload",
            1,
            self.route_version,
            1,
        ]]
        if request_rows != expected_request:
            raise RuntimeError(f"BC09 approved change request changed: expected={expected_request!r}, observed={request_rows!r}")
        lease_rows = json_object(
            env.execute_sql(
                f"SELECT binding_id, fence_epoch, fence_state, current_lease, owner_instance, "
                f"owner_incarnation, observed_at, valid_until FROM {self.database}.{self.route_lease_table} "
                f"WHERE binding_id = '{self.binding_id}'"
            ),
            "verify BC09 active route lease fence",
        )["result"]
        expected_lease = [[
            self.binding_id,
            self.route_version * 1000 + 17,
            "held",
            1,
            self.owner_instance,
            self.owner_incarnation,
            "2026-08-02 23:59:58",
            "2026-08-03 00:00:30",
        ]]
        if lease_rows != expected_lease:
            raise RuntimeError(
                f"BC09 active route lease fence changed: expected={expected_lease!r}, observed={lease_rows!r}"
            )
        owner_rows = json_object(
            env.execute_sql(
                f"SELECT owner_instance, service_name, owner_state, last_heartbeat, lease_expires_at, "
                f"incarnation, current_owner FROM {self.database}.{self.route_owner_table} "
                f"WHERE owner_instance = '{self.owner_instance}'"
            ),
            "verify BC09 route owner heartbeat",
        )["result"]
        expected_owner = [[
            self.owner_instance,
            self.service_name,
            "healthy",
            "2026-08-02 23:59:58",
            "2026-08-03 00:00:20",
            self.owner_incarnation,
            1,
        ]]
        if owner_rows != expected_owner:
            raise RuntimeError(
                f"BC09 route owner heartbeat changed: expected={expected_owner!r}, observed={owner_rows!r}"
            )
        commit_rows = json_object(
            env.execute_sql(
                f"SELECT commit_id, route_id, route_key, binding_id, route_version, commit_state, "
                f"current_commit, effective_from, effective_until FROM {self.database}.{self.route_commit_table} "
                f"WHERE commit_id = '{self.commit_id}'"
            ),
            "verify BC09 committed route cutover",
        )["result"]
        expected_commit = [[
            self.commit_id,
            self.route_id,
            self.route_key,
            self.binding_id,
            self.route_version,
            "committed",
            1,
            "2024-02-01 00:00:00",
            "2099-12-31 23:59:59",
        ]]
        if commit_rows != expected_commit:
            raise RuntimeError(
                f"BC09 route cutover commit changed: expected={expected_commit!r}, observed={commit_rows!r}"
            )
        traffic_rows = json_object(
            env.execute_sql(
                f"SELECT assignment_id, route_id, binding_id, service_name, traffic_class, assignment_state, "
                f"read_weight, write_weight, current_assignment, effective_from, effective_until "
                f"FROM {self.database}.{self.route_traffic_table} "
                f"WHERE assignment_id = 'traffic-{self.route_key.replace('.', '-')}-v{self.route_version}'"
            ),
            "verify BC09 serving traffic assignment",
        )["result"]
        expected_traffic = [[
            f"traffic-{self.route_key.replace('.', '-')}-v{self.route_version}",
            self.route_id,
            self.binding_id,
            self.service_name,
            "all_orders",
            "serving",
            100,
            100,
            1,
            "2024-02-01 00:00:00",
            "2099-12-31 23:59:59",
        ]]
        if traffic_rows != expected_traffic:
            raise RuntimeError(
                f"BC09 route traffic assignment changed: expected={expected_traffic!r}, observed={traffic_rows!r}"
            )
        runtime_rows = json_object(
            env.execute_sql(
                f"SELECT route_id, binding_id, service_name, route_key, MAX(observed_state), MAX(request_origin), "
                f"SUM(read_requests), SUM(write_requests), MAX(last_request_at), MIN(observed_at), "
                f"MAX(observation_until), MAX(current_observation), relation_schema, relation_table "
                f"FROM {self.database}.{self.route_runtime_table} "
                f"WHERE route_id = '{self.route_id}' AND binding_id = '{self.binding_id}' "
                "GROUP BY route_id, binding_id, service_name, route_key, relation_schema, relation_table"
            ),
            "verify BC09 route runtime observation",
        )["result"]
        expected_runtime = [[
            self.route_id,
            self.binding_id,
            self.service_name,
            self.route_key,
            "active",
            "production",
            18420,
            931,
            "2026-08-02 23:59:58",
            "2026-08-02 23:59:00",
            "2026-08-03 00:00:00",
            1,
            self.database,
            self.table,
        ]]
        if runtime_rows != expected_runtime:
            raise RuntimeError(
                f"BC09 route runtime observation changed: expected={expected_runtime!r}, observed={runtime_rows!r}"
            )

    @staticmethod
    def _execute_connection_sql(connection: object, sql: str) -> dict[str, str]:
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
        except Exception as exc:
            raise RuntimeError(
                f"BC09 long-running TiDB SQL failed: query={sql!r}, error={exc}"
            ) from exc
        return {"status": "success"}

    def _customer_query_truth(self, env: object, database: str, table: str) -> tuple[int, int, int, int, int, int]:
        payload = json_object(
            env.execute_sql(
                f"SELECT COUNT(*), COALESCE(SUM(amount), 0), COALESCE(MIN(event_id), 0), "
                f"COALESCE(MAX(event_id), 0), COUNT(DISTINCT payload), "
                f"COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', event_id, payload))), 0) "
                f"FROM {database}.{table} "
                "WHERE event_id BETWEEN 8990 AND 9010 AND tenant_id IN (1, 33, 37, 65, 69) "
                "AND event_type = 'refund'"
            ),
            f"read BC09 customer query truth for {database}.{table}",
        )
        rows = payload["result"]
        if len(rows) != 1 or len(rows[0]) != 6:
            raise RuntimeError(f"BC09 customer query truth result has unexpected shape: table={database}.{table}, rows={rows!r}")
        return tuple(int(value) for value in rows[0])

    def _business_truth(self, env: object) -> tuple[int, int, int]:
        payload = json_object(
            env.execute_sql(
                f"SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
                f"COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_type, amount, payload))), 0) "
                f"FROM {self.database}.{self.table}"
            ),
            f"read BC09 business truth for {self.database}.{self.table}",
        )
        rows = payload["result"]
        if len(rows) != 1 or len(rows[0]) != 3:
            raise RuntimeError(f"BC09 business truth result has unexpected shape: rows={rows!r}")
        return tuple(int(value) for value in rows[0])

    def _capture_reorg_settings(self, env: object) -> dict[str, str]:
        settings: dict[str, str] = {}
        for variable in self._REORG_VARIABLES:
            payload = json_object(
                env.execute_sql(f"SHOW GLOBAL VARIABLES LIKE '{variable}'"),
                f"read BC09 global variable {variable}",
            )
            rows = payload["result"]
            if len(rows) != 1 or len(rows[0]) < 2:
                raise RuntimeError(f"BC09 global variable query returned unexpected rows: variable={variable!r}, rows={rows!r}")
            settings[variable] = str(rows[0][1])
        return settings

    def _set_slow_reorg_settings(self, env: object) -> None:
        require_sql_success(
            env.execute_sql("SET GLOBAL tidb_enable_dist_task = OFF"),
            "disable BC09 distributed DDL tasks",
        )
        require_sql_success(
            env.execute_sql("SET GLOBAL tidb_ddl_reorg_worker_cnt = 1"),
            "set BC09 DDL reorg worker count",
        )
        require_sql_success(
            env.execute_sql("SET GLOBAL tidb_ddl_reorg_batch_size = 1"),
            "set BC09 DDL reorg batch size",
        )

    def _set_paused_reorg_batch_size(self, env: object) -> None:
        require_sql_success(
            env.execute_sql("SET GLOBAL tidb_ddl_reorg_batch_size = 128"),
            "increase BC09 paused DDL reorg batch size",
        )

    def _restore_reorg_settings(self, env: object) -> None:
        for variable, value in self._original_reorg_settings.items():
            require_sql_success(
                env.execute_sql(f"SET GLOBAL {variable} = {value}"),
                f"restore BC09 global variable {variable}",
            )

    def _connection(self, env: object, job_key: str):
        return env.open_workload_connection(f"bc09-ddl-backfill-{job_key.replace(':', '-')}")

    def _start_ddl(
        self,
        env: object,
        job_key: str,
        database: str,
        table: str,
        index_name: str,
    ) -> None:
        done = threading.Event()
        self._ddl_done[job_key] = done
        self._ddl_errors[job_key] = None

        def run_ddl() -> None:
            connection = None
            try:
                connection = self._connection(env, job_key)
                self._ddl_connections[job_key] = connection
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"ALTER TABLE {database}.{table} "
                        f"ADD UNIQUE INDEX {index_name} (payload)"
                    )
            except Exception as exc:
                self._ddl_errors[job_key] = exc
            finally:
                if connection is not None and self._ddl_connections.get(job_key) is connection:
                    connection.close()
                    self._ddl_connections.pop(job_key, None)
                done.set()

        thread = threading.Thread(
            target=run_ddl,
            name=f"bc09-ddl-{job_key.replace(':', '-')}",
            daemon=True,
        )
        self._ddl_threads[job_key] = thread
        thread.start()

    def _decoy_job_key(self, database: str, table: str) -> str:
        return f"decoy:{database}:{table}"

    def _latest_job_rows(self, env: object, database: str, table: str) -> list:
        all_jobs = json_object(
            env.execute_sql("ADMIN SHOW DDL JOBS"),
            "find BC09 add-index job",
        )["result"]
        rows = [
            [row[0], row[3], row[11]]
            for row in all_jobs
            if len(row) >= 12
            and str(row[1]) == database
            and str(row[2]) == table
            and str(row[3]).casefold().startswith("add index")
            and str(row[11]).casefold() not in self._TERMINAL_STATES
        ]
        if len(rows) > 1:
            raise RuntimeError(
                f"BC09 add-index job query returned more than one latest row: "
                f"database={database!r}, table={table!r}, rows={rows!r}"
            )
        return rows

    def _find_job(self, env: object, database: str, table: str) -> tuple[int, str]:
        rows = self._latest_job_rows(env, database, table)
        if len(rows) != 1 or len(rows[0]) < 3:
            raise RuntimeError(
                f"BC09 add-index job was not observable: database={database!r}, "
                f"table={table!r}, rows={rows!r}"
            )
        return int(rows[0][0]), str(rows[0][2]).casefold()

    def _job_rows(self, env: object, job_id: int):
        return self._job_rows_for_ids(env, (job_id,))

    def _job_rows_for_ids(self, env: object, job_ids: tuple[int, ...]) -> list:
        if not job_ids:
            return []
        payload = json_object(
            env.execute_sql(
                "SELECT JOB_ID, JOB_TYPE, STATE FROM information_schema.ddl_jobs "
                f"WHERE JOB_ID IN ({','.join(str(job_id) for job_id in job_ids)})"
            ),
            f"read BC09 DDL jobs {job_ids!r}",
        )
        return payload["result"]

    def _pause_started_job(
        self,
        env: object,
        job_key: str,
        database: str,
        table: str,
        *,
        require_ingest: bool,
    ) -> None:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            error = self._ddl_errors[job_key]
            if error is not None:
                raise RuntimeError(f"BC09 {job_key} ADD UNIQUE INDEX failed before pause: error={error!r}")
            if self._ddl_done[job_key].is_set():
                raise RuntimeError(f"BC09 {job_key} ADD UNIQUE INDEX completed before it could be paused")
            rows = self._latest_job_rows(env, database, table)
            if not rows:
                time.sleep(0.05)
                continue
            if len(rows[0]) < 3:
                raise RuntimeError(
                    f"BC09 add-index job row has an unexpected shape: "
                    f"database={database!r}, table={table!r}, rows={rows!r}"
                )
            job_id, state = int(rows[0][0]), str(rows[0][2]).casefold()
            self._job_ids[job_key] = job_id
            if job_key == "target":
                self._job_id = job_id
            if state == "paused":
                return
            if state in {"queueing", "none"}:
                time.sleep(0.05)
                continue
            if state != "running":
                raise RuntimeError(
                    f"BC09 {job_key} DDL job reached an unexpected state before pause: "
                    f"job_id={job_id}, state={state!r}"
                )
            job_type = str(rows[0][1]).casefold()
            if require_ingest and not job_type.endswith("/* ingest */"):
                raise RuntimeError(
                    f"BC09 {job_key} DDL job entered running with an unsupported backfill type: "
                    f"job_id={job_id}, job_type={rows[0][1]!r}"
                )
            require_sql_success(
                env.execute_sql(f"ADMIN PAUSE DDL JOBS {job_id}"),
                f"pause BC09 DDL job {job_id}",
            )
            pause_deadline = time.monotonic() + self._PAUSE_CONFIRM_TIMEOUT_SECONDS
            last_rows = rows
            while time.monotonic() < pause_deadline:
                rows = self._job_rows(env, job_id)
                last_rows = rows
                if len(rows) == 1 and str(rows[0][2]).casefold() == "paused":
                    return
                error = self._ddl_errors[job_key]
                if error is not None:
                    raise RuntimeError(f"BC09 {job_key} ADD UNIQUE INDEX failed while pausing: error={error!r}")
                if self._ddl_done[job_key].is_set():
                    raise RuntimeError(f"BC09 {job_key} DDL job {job_id} completed while pausing")
                time.sleep(0.05)
            raise RuntimeError(
                f"BC09 {job_key} DDL job did not enter paused state: job_id={job_id}, "
                f"last_rows={last_rows!r}, timeout_seconds={self._PAUSE_CONFIRM_TIMEOUT_SECONDS}"
            )
        raise RuntimeError(
            f"Timed out waiting for the BC09 {job_key} add-index job to become observable: "
            f"database={self.database!r}, table={table!r}"
        )

    def _verify_paused_job(self, env: object, job_key: str) -> None:
        job_id = self._job_ids.get(job_key)
        if job_id is None:
            raise RuntimeError(f"BC09 paused job ID is not initialized: job_key={job_key!r}")
        rows = self._job_rows(env, job_id)
        if len(rows) != 1 or str(rows[0][2]).casefold() != "paused":
            raise RuntimeError(f"BC09 DDL job is not paused: job_key={job_key!r}, job_id={job_id}, rows={rows!r}")

    def _verify_all_paused_jobs(self, env: object) -> None:
        self._verify_paused_job(env, "target")
        for decoy in self.decoy_tables:
            self._verify_paused_job(
                env,
                self._decoy_job_key(str(decoy["database"]), str(decoy["table"])),
            )

    def _wait_for_terminal(self, env: object, job_ids: tuple[int, ...]) -> None:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            rows = self._job_rows_for_ids(env, job_ids)
            states = {
                int(row[0]): str(row[2]).casefold()
                for row in rows
                if len(row) >= 3
            }
            if len(states) == len(job_ids) and all(
                states[job_id] in self._TERMINAL_STATES for job_id in job_ids
            ):
                return
            time.sleep(0.2)
        raise RuntimeError(f"BC09 DDL jobs did not reach terminal states: job_ids={job_ids!r}")

    def _stop_ddl_threads(self) -> None:
        for job_key, thread in tuple(self._ddl_threads.items()):
            connection = self._ddl_connections.pop(job_key, None)
            if thread.is_alive() and connection is not None:
                connection.close()
            thread.join(timeout=10)
            if thread.is_alive():
                raise RuntimeError(f"BC09 DDL worker thread did not stop within 10 seconds: job_key={job_key!r}")
        self._ddl_threads.clear()
        self._ddl_connections.clear()
        self._ddl_done.clear()
        self._ddl_errors.clear()
