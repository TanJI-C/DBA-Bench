from dataclasses import dataclass, replace

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    run_cleanup_steps,
    validate_sql_identifier,
)

from dataclasses import dataclass

from src.scenarios.evaluation.tidb.query_perf.index_order_correlation import (
    TidbQueryPerfIndexOrderCorrelationEvaluatorCase,
    TidbQueryPerfIndexOrderCorrelationReducedEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfIndexOrderCorrelationCase(TiDBScenarioCase):
    db: str
    table: str
    policy_table: str
    target_bucket: str
    tenant_id: str
    lower_bound: str
    upper_bound: str
    result_limit: int
    total_row_count: int
    target_current_row_count: int
    target_history_row_count: int
    decoy_row_count: int
    other_row_count: int
    policy_noise_row_count: int
    policy_cross_tenant_noise_row_count: int
    policy_history_row_count: int
    catalog_decoy_index: str
    admin_catalog_decoy_index: str
    policy_decoy_index: str
    policy_scan_floor: int
    recovered_policy_scan_ceiling: int
    original_index: str
    repaired_index: str
    admin_repaired_index: str
    policy_repaired_index: str
    fault_query_sql: str
    admin_fault_query_sql: str
    result_truth_sql: str
    admin_result_truth_sql: str
    table_crc_sql: str
    latency_warmup_count: int
    latency_sample_count: int
    latency_outlier_tolerance: int
    fault_scan_floor: int
    recovered_scan_ceiling: int
    admin_fault_scan_floor: int
    admin_recovered_scan_ceiling: int
    latency_stability_floor_ms: float
    source_id: str
    source_url: str
    source_sha256: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfIndexOrderCorrelationForObjectListingScenarioCase(
    TidbQueryPerfIndexOrderCorrelationCase
):
    pass


_DB = "test"
_TABLE = "qp01_object_catalog"
_POLICY_TABLE = "qp01_bucket_policy"
_TARGET_BUCKET = "bucket_b"
_TENANT_ID = "tenant-b"
_LOWER_BOUND = "dir-00000000"
_UPPER_BOUND = "zzzzzzzz"
_RESULT_LIMIT = 100
_TOTAL_ROWS = 110_000
_TARGET_CURRENT_ROWS = 1_601
_TARGET_HISTORY_ROWS = 8_401
_DECOY_ROWS = 45_000
_OTHER_ROWS = _TOTAL_ROWS - _DECOY_ROWS - _TARGET_CURRENT_ROWS - _TARGET_HISTORY_ROWS
_POLICY_NOISE_ROWS = 50_000
_POLICY_CROSS_TENANT_NOISE_ROWS = 12_000
_POLICY_HISTORY_ROWS = 500
_ORIGINAL_INDEX = "idx_nm_bkt_ver"
_REPAIRED_INDEX = "idx_bkt_cur_del_name_ver"
_ADMIN_CATALOG_DECOY_INDEX = "idx_updated_tenant"
_ADMIN_REPAIRED_INDEX = "idx_tenant_cur_del_updated"
_POLICY_REPAIRED_INDEX = "idx_policy_bucket_tenant_current"
_CATALOG_DECOY_INDEX = "idx_bkt_ver_name"
_POLICY_DECOY_INDEX = "idx_policy_tenant_state"
_FAULT_QUERY = (
    "SELECT o.item_id, o.name, o.bucket_id, o.version_id, o.payload, "
    "o.size_bytes, o.etag, o.updated_at, "
    "CASE WHEN o.storage_class = 'archive' THEN 'cold' ELSE 'hot' END AS storage_tier, "
    "COALESCE((SELECT p.policy_state FROM "
    f"{_DB}.{_POLICY_TABLE} AS p WHERE p.bucket_id = o.bucket_id "
    f"AND p.tenant_id = '{_TENANT_ID}' AND p.is_current = 1 "
    "ORDER BY p.policy_version DESC LIMIT 1), 'missing') AS policy_state, "
    "COALESCE((SELECT p.list_enabled FROM "
    f"{_DB}.{_POLICY_TABLE} AS p WHERE p.bucket_id = o.bucket_id "
    f"AND p.tenant_id = '{_TENANT_ID}' AND p.is_current = 1 "
    "ORDER BY p.policy_version DESC LIMIT 1), 0) AS list_enabled "
    f"FROM {_DB}.{_TABLE} AS o "
    f"WHERE o.bucket_id = '{_TARGET_BUCKET}' "
    f"AND o.name > '{_LOWER_BOUND}' AND o.name < '{_UPPER_BOUND}' "
    "AND o.is_current = 1 AND o.is_deleted = 0 "
    "AND (o.visibility = 'public' "
    f"OR (o.visibility = 'tenant' AND o.tenant_id = '{_TENANT_ID}')) "
    "AND (o.storage_class IN ('standard', 'infrequent') "
    "OR (o.storage_class = 'archive' AND o.restore_state = 'ready')) "
    f"ORDER BY o.name ASC LIMIT {_RESULT_LIMIT}"
)
_ADMIN_FAULT_QUERY = (
    "SELECT o.item_id, o.name, o.bucket_id, o.version_id, o.payload, "
    "o.size_bytes, o.etag, o.updated_at "
    f"FROM {_DB}.{_TABLE} AS o "
    f"WHERE o.tenant_id = '{_TENANT_ID}' "
    "AND o.is_current = 1 AND o.is_deleted = 0 "
    "AND (o.visibility = 'public' "
    f"OR (o.visibility = 'tenant' AND o.tenant_id = '{_TENANT_ID}')) "
    "AND (o.storage_class IN ('standard', 'infrequent') "
    "OR (o.storage_class = 'archive' AND o.restore_state = 'ready')) "
    f"ORDER BY o.updated_at DESC, o.item_id DESC LIMIT {_RESULT_LIMIT}"
)
_TABLE_CRC = (
    "SELECT 'catalog' AS source, COUNT(*), COALESCE(SUM(item_id), 0), "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', item_id, bucket_id, name, version_id, "
    "payload, is_current, is_deleted, visibility, storage_class))), 0) "
    f"FROM {_DB}.{_TABLE} "
    "UNION ALL "
    "SELECT 'policy', COUNT(*), 0, "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', bucket_id, tenant_id, policy_state, list_enabled, "
    "policy_version, is_current))), 0) "
    f"FROM {_DB}.{_POLICY_TABLE} ORDER BY source"
)

_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="qp01_bucket_a_listing_noise",
            sql=_FAULT_QUERY.replace("'bucket_b'", "'bucket_a'").replace("'tenant-b'", "'tenant-a'"),
            qps=0.25,
        ),
        WorkloadProfile(
            name="qp01_bucket_c_listing_noise",
            sql=_FAULT_QUERY.replace("'bucket_b'", "'bucket_c'").replace("'tenant-b'", "'tenant-c'"),
            qps=0.25,
        ),
        WorkloadProfile(
            name="qp01_catalog_crc_noise",
            sql=_TABLE_CRC,
            qps=0.05,
        ),
        WorkloadProfile(
            name="qp01_bucket_b_archive_listing_decoy",
            sql=_FAULT_QUERY.replace(
                "o.storage_class IN ('standard', 'infrequent') "
                "OR (o.storage_class = 'archive' AND o.restore_state = 'ready')",
                "o.storage_class = 'archive' AND o.restore_state = 'ready'",
            ),
            qps=0.18,
        ),
        WorkloadProfile(
            name="qp01_policy_tenant_b_scan_decoy",
            sql=(
                f"SELECT bucket_id, policy_state FROM {_DB}.{_POLICY_TABLE} "
                f"WHERE tenant_id = '{_TENANT_ID}' ORDER BY bucket_id LIMIT 100"
            ),
            qps=0.18,
        ),
        WorkloadProfile(
            name="qp01_same_bucket_count_decoy",
            sql=(
                f"SELECT COUNT(*) FROM {_DB}.{_TABLE} "
                f"WHERE bucket_id = '{_TARGET_BUCKET}' "
                f"AND name > '{_LOWER_BOUND}' AND name < '{_UPPER_BOUND}' "
                "AND is_deleted = 0"
            ),
            qps=0.12,
        ),
        WorkloadProfile(
            name="qp01_tenant_a_policy_scan_decoy",
            sql=(
                f"SELECT bucket_id, policy_state FROM {_DB}.{_POLICY_TABLE} "
                "WHERE tenant_id = 'tenant-a' ORDER BY bucket_id LIMIT 100"
            ),
            qps=0.12,
        ),
        WorkloadProfile(
            name="qp01_bucket_b_version_listing_decoy",
            sql=(
                f"SELECT item_id, name, version_id FROM {_DB}.{_TABLE} "
                f"WHERE bucket_id = '{_TARGET_BUCKET}' AND version_id = 'v-00000002' "
                f"AND name > '{_LOWER_BOUND}' AND name < '{_UPPER_BOUND}' "
                "ORDER BY name LIMIT 100"
            ),
            qps=0.10,
        ),
        WorkloadProfile(
            name="qp01_tenant_b_admin_listing_causal",
            sql=_ADMIN_FAULT_QUERY,
            qps=0.22,
        ),
    ),
    worker_count=3,
    seed=20260731,
    start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
    warmup_seconds=4,
)


_CASE = TidbQueryPerfIndexOrderCorrelationForObjectListingScenarioCase(
    case_id="object_listing_composite_index_correlation",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "bucket_name_distribution_correlation",
                    "entity": _TABLE,
                    "evidence": ["EXPLAIN ANALYZE and bucket distribution evidence"],
                },
                {
                    "type": "root_cause",
                    "factor": "equality_column_not_leading_index",
                    "entity": _TABLE,
                    "evidence": ["SHOW CREATE TABLE and the customer-list plan"],
                },
                {
                    "type": "root_cause",
                    "factor": "index_scan_amplification",
                    "entity": _TABLE,
                    "evidence": ["Customer-list EXPLAIN ANALYZE actual rows"],
                },
                {
                    "type": "root_cause",
                    "factor": "policy_lookup_amplification",
                    "entity": _POLICY_TABLE,
                    "evidence": ["Policy lookup EXPLAIN ANALYZE actual rows"],
                },
                {
                    "type": "root_cause",
                    "factor": "admin_tenant_order_not_leading_index",
                    "entity": _TABLE,
                    "evidence": ["Tenant-admin SHOW CREATE TABLE and plan"],
                },
                {
                    "type": "root_cause",
                    "factor": "admin_scan_amplification",
                    "entity": _TABLE,
                    "evidence": ["Tenant-admin EXPLAIN ANALYZE actual rows"],
                },
                {
                    "type": "root_cause",
                    "factor": "versioned_policy_state_not_leading_lookup",
                    "entity": _POLICY_TABLE,
                    "evidence": ["Policy version distribution and current-state plan"],
                },
            ]
        },
        "outcome": {
            "changes": [
                "Added separate customer-list, tenant-admin-list, and current-policy access paths."
            ],
            "verification": [
                "All three plans, latency samples, both truths, and the protected-table CRC were checked."
            ],
        },
        "summary": "Each query family now has its selective equality and state prefix before its ordering column.",
    },
    case_no=0,
    evaluator=TidbQueryPerfIndexOrderCorrelationEvaluatorCase,
    title="Object-listing latency degradation across customer and tenant-admin query families.",
    alert=(
        "[CRITICAL] object listing API 的 P95 延迟从基线约 5 ms 升到 150 ms 以上。"
        "相同查询模板只因 bucket 参数不同就出现数量级差异：bucket_b 只需返回 100 行，"
        "但请求明显慢于其他 bucket；TiDB 集群和其他业务查询仍然健康。"
        "同一接口的 customer-list 与 tenant-admin-list 两个真实查询族也都变慢；TopSQL 中还存在"
        "版本化 policy lookup、相似列表、版本读取和校验指纹。请从指标、指纹、执行计划、索引定义、"
        "元数据分布和业务真值中定位三条相互耦合的退化路径，恢复所有选择性访问并记录端到端延迟样本，"
        "保持返回结果和双表业务 CRC，不得修改业务数据。"
    ),
    initial_state={
        "status": "degraded",
        "query": "object_listing",
        "plan": "IndexLookUp",
        "scan": "large_name_range",
        "policy_lookup": "unresolved_metadata_lookup",
        "admin_scan": "large_updated_at_range",
    },
    expected_target={
        "status": "recovered",
        "plan": "selective_bucket_name_access",
        "policy_plan": "selective_bucket_tenant_access",
        "admin_plan": "selective_tenant_updated_access",
        "result_rows": _RESULT_LIMIT,
        "business_crc": "unchanged",
        "latency": "recorded_separately",
    },
    background_workload=_BACKGROUND_WORKLOAD,
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.875665,
        reference_run_ids=("reference-269__tidb_query_perf_index_order_correlation",),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=300,
        image_group_key="qp01-index-order-correlation",
    ),
    db=_DB,
    table=_TABLE,
    policy_table=_POLICY_TABLE,
    target_bucket=_TARGET_BUCKET,
    tenant_id=_TENANT_ID,
    lower_bound=_LOWER_BOUND,
    upper_bound=_UPPER_BOUND,
    result_limit=_RESULT_LIMIT,
    total_row_count=_TOTAL_ROWS,
    target_current_row_count=_TARGET_CURRENT_ROWS,
    target_history_row_count=_TARGET_HISTORY_ROWS,
    decoy_row_count=_DECOY_ROWS,
    other_row_count=_OTHER_ROWS,
    policy_noise_row_count=_POLICY_NOISE_ROWS,
    policy_cross_tenant_noise_row_count=_POLICY_CROSS_TENANT_NOISE_ROWS,
    policy_history_row_count=_POLICY_HISTORY_ROWS,
    catalog_decoy_index=_CATALOG_DECOY_INDEX,
    admin_catalog_decoy_index=_ADMIN_CATALOG_DECOY_INDEX,
    policy_decoy_index=_POLICY_DECOY_INDEX,
    policy_scan_floor=10_000,
    recovered_policy_scan_ceiling=100,
    original_index=_ORIGINAL_INDEX,
    repaired_index=_REPAIRED_INDEX,
    admin_repaired_index=_ADMIN_REPAIRED_INDEX,
    policy_repaired_index=_POLICY_REPAIRED_INDEX,
    fault_query_sql=_FAULT_QUERY,
    admin_fault_query_sql=_ADMIN_FAULT_QUERY,
    result_truth_sql=_FAULT_QUERY,
    admin_result_truth_sql=_ADMIN_FAULT_QUERY,
    table_crc_sql=_TABLE_CRC,
    latency_warmup_count=8,
    latency_sample_count=40,
    latency_outlier_tolerance=2,
    fault_scan_floor=10_000,
    recovered_scan_ceiling=2_000,
    admin_fault_scan_floor=10_000,
    admin_recovered_scan_ceiling=2_000,
    latency_stability_floor_ms=45.0,
    source_id="O47",
    source_url="https://tidb.net/blog/ca23dfca",
    source_sha256="235f5426919eece592b27ac10699b9ecc2640e5971d3d9591c439aa0b1bd4c72",
)

_CASE_REDUCED = replace(
    _CASE,
    case_id="object_listing_composite_index_correlation_simple",
    case_no=1,
    evaluator=TidbQueryPerfIndexOrderCorrelationReducedEvaluatorCase,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": (
                        "The object-listing query filters one bucket with equality but orders and ranges "
                        "on name while also filtering current, visible, non-deleted versions and projecting "
                        "bucket policy metadata, and the target bucket's qualifying names occur late in the "
                        "global name order because bucket and name are correlated in the data distribution."
                    ),
                    "entity": _TABLE,
                    "evidence": [
                        (
                            "The affected object-listing table uses a composite index beginning with name, "
                            "so the bucket_id equality is applied only after scanning a broad ordered name "
                            "range instead of narrowing the index access first."
                        ),
                        (
                            "The affected object-listing plan estimates a small result but its IndexRangeScan "
                            "processes tens of thousands of physical version keys before the current/version "
                            "and policy predicates produce the first 100 rows, which explains the elevated "
                            "query latency and p95."
                        ),
                        (
                            "The tenant-admin object listing filters tenant_id and current, non-deleted rows "
                            "but orders by updated_at, while the existing catalog index begins with updated_at "
                            "and cannot narrow the tenant and state predicates before the ordered scan."
                        ),
                        (
                            "The tenant-admin listing returns a small limited result but its updated_at-first "
                            "catalog path scans the whole tenant/state population before producing the newest rows."
                        ),
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": (
                        "The projected policy metadata lookup uses a tenant-first index on a large policy "
                        "table, so the correlated bucket_id predicate is residual and each listing can "
                        "scan thousands of policy-noise rows; a bucket_id,tenant_id access path is also "
                        "required for the query to recover."
                    ),
                    "entity": _POLICY_TABLE,
                    "evidence": [
                        (
                            "The correlated policy lookup has many historical rows for the same bucket and tenant; "
                            "bucket_id and tenant_id alone only locate the version chain, while is_current and "
                            "policy_version must narrow the current policy lookup without changing which policy is returned."
                        ),
                    ],
                },
            ]
        },
        "outcome": {
            "changes": [
                "Added separate customer-list, tenant-admin-list, and current-policy access paths."
            ],
            "verification": [
                "All three plans, latency samples, both truths, and the protected-table CRC were checked."
            ],
        },
        "summary": "Each query family now has its selective equality and state prefix before its ordering column.",
    },
    title="Object-listing latency degradation across customer and tenant-admin query families.",
    alert=(
        "[CRITICAL] object listing API 的 P95 延迟从基线约 5 ms 升到 150 ms 以上。"
        "相同查询模板只因 bucket 参数不同就出现数量级差异：bucket_b 只需返回 100 行，"
        "但请求明显慢于其他 bucket；TiDB 集群和其他业务查询仍然健康。"
        "同一接口的 customer-list 与 tenant-admin-list 两个真实查询族也都变慢；TopSQL 中还存在"
        "版本化 policy lookup、相似列表、版本读取和校验指纹。请从指标、指纹、执行计划、索引定义、"
        "元数据分布和业务真值中定位相互耦合的退化路径，恢复所有选择性访问并记录端到端延迟样本，"
        "保持返回结果和双表业务 CRC，不得修改业务数据。"
    ),
    policy_noise_row_count=25_000,
    policy_cross_tenant_noise_row_count=6_000,
    policy_history_row_count=250,
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.492454,
        reference_run_ids=(
            "tidb-reference-4__tidb_query_perf_index_order_correlation__"
            "object_listing_composite_index_correlation_simple__mock__r001",
        ),
    ),
)

import json
import re
import time
from collections.abc import Mapping

from src.database.query_results import (
    capture_query_result_truth,
    measure_latency_profile,
)
from src.database.sql import (
    parse_json_object,
    require_result_rows,
    require_success_payload,
)
from src.database.tidb import qp01_plan_metrics


class TidbQueryPerfIndexOrderCorrelationInjector(BaseFaultInjector):
    """Create O47's v8.1 correlated composite-index access-path regression."""

    def _analyze_with_lock_retry(self, env, table: str, description: str) -> None:
        # A cluster that just recovered from a rough deployment can still hold
        # DDL/region locks; one bounded retry absorbs a transient lock-wait
        # timeout instead of failing the whole setup.
        deadline = time.monotonic() + 60
        while True:
            payload = parse_json_object(
                env.execute_sql_with_timeout(f"ANALYZE TABLE {self.db}.{table}", self.sql_timeout_seconds),
                description,
            )
            if payload.get("status") == "success":
                return
            if "1205" not in str(payload.get("error", "")) or time.monotonic() >= deadline:
                raise RuntimeError(f"{description} failed: response={payload!r}")
            time.sleep(2)

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        with context.env.metrics_hidden():
            self._create_table(context.env)
            self._load_rows(context.env)
            self._verify_fault_state(context.env)
            self._hidden_evidence = self._capture_fault_evidence(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_fault_state(context.env)
        self._hidden_evidence = self._capture_fault_evidence(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._verify_fault_state(context.env)
        require_success_payload(
            context.env.execute_sql(self.fault_query_sql),
            "execute QP01 visible fault query",
        )
        require_success_payload(
            context.env.execute_sql(self.admin_fault_query_sql),
            "execute QP01 visible admin fault query",
        )
        return self._hidden_evidence

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_fault_state(context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        run_cleanup_steps(
            f"recover TiDB QP01 {context.scenario_id}/{context.case_id}",
            (
                (
                    f"drop QP01 policy table {self.db}.{self.policy_table}",
                    lambda: require_success_payload(
                        context.env.execute_sql(
                            f"DROP TABLE IF EXISTS {self.db}.{self.policy_table}"
                        ),
                        f"drop QP01 policy table {self.db}.{self.policy_table}",
                    ),
                ),
                (
                    f"drop QP01 table {self.db}.{self.table}",
                    lambda: require_success_payload(
                        context.env.execute_sql(
                            f"DROP TABLE IF EXISTS {self.db}.{self.table}"
                        ),
                        f"drop QP01 table {self.db}.{self.table}",
                    ),
                ),
                (
                    f"drop QP01 numbers table {self.db}.{self.numbers_table}",
                    lambda: require_success_payload(
                        context.env.execute_sql(
                            f"DROP TABLE IF EXISTS {self.db}.{self.numbers_table}"
                        ),
                        f"drop QP01 numbers table {self.db}.{self.numbers_table}",
                    ),
                ),
            ),
        )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.policy_table = validate_sql_identifier(
            str(config["policy_table"]), "policy table"
        )
        self.numbers_table = validate_sql_identifier(
            f"{self.table}_numbers",
            "numbers table",
        )
        self.target_bucket = str(config["target_bucket"])
        self.tenant_id = str(config["tenant_id"])
        self.lower_bound = str(config["lower_bound"])
        self.upper_bound = str(config["upper_bound"])
        self.result_limit = int(config["result_limit"])
        self.total_row_count = int(config["total_row_count"])
        self.target_current_row_count = int(config["target_current_row_count"])
        self.target_history_row_count = int(config["target_history_row_count"])
        self.decoy_row_count = int(config["decoy_row_count"])
        self.other_row_count = int(config["other_row_count"])
        self.policy_noise_row_count = int(config["policy_noise_row_count"])
        self.policy_cross_tenant_noise_row_count = int(
            config["policy_cross_tenant_noise_row_count"]
        )
        self.policy_history_row_count = int(config["policy_history_row_count"])
        self.catalog_decoy_index = validate_sql_identifier(
            str(config["catalog_decoy_index"]), "catalog decoy index"
        )
        self.admin_catalog_decoy_index = validate_sql_identifier(
            str(config["admin_catalog_decoy_index"]), "admin catalog decoy index"
        )
        self.policy_decoy_index = validate_sql_identifier(
            str(config["policy_decoy_index"]), "policy decoy index"
        )
        self.policy_scan_floor = int(config["policy_scan_floor"])
        self.original_index = validate_sql_identifier(
            str(config["original_index"]), "original index"
        )
        self.repaired_index = validate_sql_identifier(
            str(config["repaired_index"]), "repaired index"
        )
        self.admin_repaired_index = validate_sql_identifier(
            str(config["admin_repaired_index"]), "admin repaired index"
        )
        self.policy_repaired_index = validate_sql_identifier(
            str(config["policy_repaired_index"]), "policy repaired index"
        )
        self.fault_query_sql = str(config["fault_query_sql"])
        self.admin_fault_query_sql = str(config["admin_fault_query_sql"])
        self.result_truth_sql = str(config["result_truth_sql"])
        self.admin_result_truth_sql = str(config["admin_result_truth_sql"])
        self.table_crc_sql = str(config["table_crc_sql"])
        self.latency_warmup_count = int(config["latency_warmup_count"])
        self.latency_sample_count = int(config["latency_sample_count"])
        self.fault_scan_floor = int(config["fault_scan_floor"])
        self.admin_fault_scan_floor = int(config["admin_fault_scan_floor"])
        self.sql_timeout_seconds = int(config["sql_timeout_seconds"])

    def _create_table(self, env) -> None:
        require_success_payload(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.table}"),
            f"clear QP01 table {self.db}.{self.table}",
        )
        require_success_payload(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.policy_table}"),
            f"clear QP01 policy table {self.db}.{self.policy_table}",
        )
        require_success_payload(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.numbers_table}"),
            f"clear QP01 numbers table {self.db}.{self.numbers_table}",
        )
        require_success_payload(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.table} ("
                "item_id BIGINT PRIMARY KEY, "
                "name VARCHAR(128) NOT NULL, "
                "bucket_id VARCHAR(32) NOT NULL, "
                "version_id VARCHAR(32) NOT NULL, "
                "tenant_id VARCHAR(32) NOT NULL, "
                "is_current TINYINT NOT NULL, "
                "is_deleted TINYINT NOT NULL, "
                "visibility VARCHAR(16) NOT NULL, "
                "storage_class VARCHAR(16) NOT NULL, "
                "restore_state VARCHAR(16) NOT NULL, "
                "size_bytes BIGINT NOT NULL, "
                "etag VARCHAR(64) NOT NULL, "
                "updated_at BIGINT NOT NULL, "
                "payload VARCHAR(128) NOT NULL, "
                f"UNIQUE KEY {self.original_index} (name, bucket_id, version_id)"
                ")"
            ),
            f"create QP01 table {self.db}.{self.table}",
        )
        require_success_payload(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.policy_table} ("
                "bucket_id VARCHAR(32) NOT NULL, "
                "tenant_id VARCHAR(32) NOT NULL, "
                "policy_state VARCHAR(16) NOT NULL, "
                "list_enabled TINYINT NOT NULL, "
                "policy_version INT NOT NULL, "
                "is_current TINYINT NOT NULL, "
                "KEY idx_policy_tenant (tenant_id)"
                ")"
            ),
            f"create QP01 policy table {self.db}.{self.policy_table}",
        )
        require_success_payload(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.numbers_table} (n INT PRIMARY KEY)"
            ),
            f"create QP01 numbers table {self.db}.{self.numbers_table}",
        )

    def _load_rows(self, env) -> None:
        target_current_end = self.decoy_row_count + self.target_current_row_count
        target_end = target_current_end + self.target_history_row_count
        require_success_payload(
            env.execute_sql(f"INSERT INTO {self.db}.{self.numbers_table} VALUES (1)"),
            "seed QP01 numbers table",
        )
        generated = 1
        while generated < self.total_row_count:
            extension = min(generated, self.total_row_count - generated)
            require_success_payload(
                env.execute_sql(
                    f"INSERT INTO {self.db}.{self.numbers_table} (n) "
                    f"SELECT n + {generated} FROM {self.db}.{self.numbers_table} "
                    f"WHERE n <= {extension}"
                ),
                f"extend QP01 numbers table to {generated + extension} rows",
            )
            generated += extension
        require_success_payload(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.table} "
                "(item_id, name, bucket_id, version_id, tenant_id, is_current, "
                "is_deleted, visibility, storage_class, restore_state, size_bytes, "
                "etag, updated_at, payload) "
                "SELECT n, "
                f"CASE WHEN n <= {self.decoy_row_count} THEN CONCAT('dir-', LPAD(n, 8, '0')) "
                f"WHEN n <= {target_current_end} THEN CONCAT('risk-', LPAD(n - {self.decoy_row_count}, 8, '0')) "
                f"WHEN n <= {target_end} THEN CONCAT('risk-', LPAD(n - {target_current_end}, 8, '0')) "
                f"ELSE CONCAT('zz-', LPAD(n - {target_end}, 8, '0')) END, "
                f"CASE WHEN n <= {self.decoy_row_count} THEN 'bucket_a' "
                f"WHEN n <= {target_end} THEN 'bucket_b' ELSE 'bucket_c' END, "
                f"CASE WHEN n BETWEEN {self.decoy_row_count + 1} AND {target_current_end} THEN 'v-00000002' "
                f"WHEN n BETWEEN {target_current_end + 1} AND {target_end} THEN 'v-00000001' "
                "ELSE 'v-00000001' END, "
                f"CASE WHEN n <= {self.decoy_row_count} THEN 'tenant-a' "
                f"WHEN n <= {target_end} THEN 'tenant-b' ELSE 'tenant-c' END, "
                f"CASE WHEN n BETWEEN {target_current_end + 1} AND {target_end} THEN 0 ELSE 1 END, "
                "0, "
                f"CASE WHEN n BETWEEN {self.decoy_row_count + 1} AND {target_end} THEN 'tenant' ELSE 'public' END, "
                "CASE WHEN n % 17 = 0 THEN 'archive' ELSE 'standard' END, "
                "CASE WHEN n % 17 = 0 THEN 'ready' ELSE 'none' END, "
                "n * 10, CONCAT('etag-', LPAD(n, 8, '0')), 20260731000000 + n, "
                "CONCAT('payload-', LPAD(n, 8, '0')) "
                f"FROM {self.db}.{self.numbers_table}"
            ),
            f"load QP01 rows into {self.db}.{self.table}",
        )
        require_success_payload(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.policy_table} "
                "(bucket_id, tenant_id, policy_state, list_enabled, policy_version, is_current) "
                f"SELECT CONCAT('noise-', LPAD(n, 8, '0')), 'tenant-b', 'disabled', 0, 1, 1 "
                f"FROM {self.db}.{self.numbers_table} WHERE n <= {self.policy_noise_row_count}"
            ),
            f"load QP01 policy noise rows into {self.db}.{self.policy_table}",
        )
        require_success_payload(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.policy_table} "
                "(bucket_id, tenant_id, policy_state, list_enabled, policy_version, is_current) "
                "SELECT CONCAT('tenant-decoy-', LPAD(n, 8, '0')), "
                "CASE WHEN MOD(n, 2) = 0 THEN 'tenant-a' ELSE 'tenant-c' END, "
                "'disabled', 0, 1, 1 "
                f"FROM {self.db}.{self.numbers_table} "
                f"WHERE n <= {self.policy_cross_tenant_noise_row_count}"
            ),
            f"load QP01 cross-tenant policy noise rows into {self.db}.{self.policy_table}",
        )
        require_success_payload(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.policy_table} "
                "(bucket_id, tenant_id, policy_state, list_enabled, policy_version, is_current) VALUES "
                "('bucket_a', 'tenant-a', 'active', 1, 1, 1), "
                "('bucket_c', 'tenant-c', 'active', 1, 1, 1), "
                "('bucket_b', 'tenant-noise', 'disabled', 0, 1, 1)"
            ),
            f"load QP01 policy rows into {self.db}.{self.policy_table}",
        )
        require_success_payload(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.policy_table} "
                "(bucket_id, tenant_id, policy_state, list_enabled, policy_version, is_current) "
                "SELECT 'bucket_b', 'tenant-b', "
                f"CASE WHEN n = {self.policy_history_row_count} THEN 'active' ELSE 'disabled' END, "
                f"CASE WHEN n = {self.policy_history_row_count} THEN 1 ELSE 0 END, n, "
                f"CASE WHEN n = {self.policy_history_row_count} THEN 1 ELSE 0 END "
                f"FROM {self.db}.{self.numbers_table} "
                f"WHERE n <= {self.policy_history_row_count}"
            ),
            f"load QP01 policy history into {self.db}.{self.policy_table}",
        )
        require_success_payload(
            env.execute_sql(
                f"ALTER TABLE {self.db}.{self.table} ADD INDEX {self.catalog_decoy_index} "
                "(bucket_id, version_id, name)"
            ),
            f"create QP01 catalog decoy index {self.catalog_decoy_index}",
        )
        require_success_payload(
            env.execute_sql(
                f"ALTER TABLE {self.db}.{self.table} ADD INDEX {self.admin_catalog_decoy_index} "
                "(updated_at, tenant_id, item_id)"
            ),
            f"create QP01 admin catalog decoy index {self.admin_catalog_decoy_index}",
        )
        require_success_payload(
            env.execute_sql(
                f"ALTER TABLE {self.db}.{self.policy_table} ADD INDEX {self.policy_decoy_index} "
                "(tenant_id, policy_state, bucket_id)"
            ),
            f"create QP01 policy decoy index {self.policy_decoy_index}",
        )
        self._analyze_with_lock_retry(env, self.table, f"analyze QP01 table {self.db}.{self.table}")
        self._analyze_with_lock_retry(
            env, self.policy_table, f"analyze QP01 policy table {self.db}.{self.policy_table}"
        )
        require_success_payload(
            env.execute_sql(f"DROP TABLE {self.db}.{self.numbers_table}"),
            f"drop QP01 numbers table {self.db}.{self.numbers_table}",
        )

    def _capture_fault_evidence(self, env) -> dict[str, object]:
        latency_profile = measure_latency_profile(
            env.execute_sql,
            self.fault_query_sql,
            warmup_samples=self.latency_warmup_count,
            measured_samples=self.latency_sample_count,
            context="measure QP01 fault query latency",
        )
        plan_rows = require_result_rows(
            env.execute_sql(f"EXPLAIN ANALYZE {self.fault_query_sql}"),
            "capture QP01 fault plan",
        )
        plan_metrics = qp01_plan_metrics(plan_rows)
        if plan_metrics["index_scan_rows"] < self.fault_scan_floor:
            raise RuntimeError(
                "QP01 fault plan does not exhibit scan amplification: "
                f"index={self.original_index!r}, scan_rows={plan_metrics['index_scan_rows']}, "
                f"required_at_least={self.fault_scan_floor}, plan={plan_rows!r}"
            )
        admin_plan_rows = require_result_rows(
            env.execute_sql(f"EXPLAIN ANALYZE {self.admin_fault_query_sql}"),
            "capture QP01 admin fault plan",
        )
        admin_plan_metrics = qp01_plan_metrics(admin_plan_rows)
        if admin_plan_metrics["index_scan_rows"] < self.admin_fault_scan_floor:
            raise RuntimeError(
                "QP01 admin fault plan does not exhibit tenant scan amplification: "
                f"index={self.admin_catalog_decoy_index!r}, "
                f"scan_rows={admin_plan_metrics['index_scan_rows']}, "
                f"required_at_least={self.admin_fault_scan_floor}, plan={admin_plan_rows!r}"
            )
        truth_payload = require_success_payload(
            env.execute_sql(self.result_truth_sql),
            "capture QP01 result truth",
        )
        admin_truth_payload = require_success_payload(
            env.execute_sql(self.admin_result_truth_sql),
            "capture QP01 admin result truth",
        )
        return {
            "fault_query_truth": capture_query_result_truth(
                truth_payload,
                ordered=True,
            ),
            "fault_admin_query_truth": capture_query_result_truth(
                admin_truth_payload,
                ordered=True,
            ),
            "fault_table_crc": require_result_rows(
                env.execute_sql(self.table_crc_sql),
                "capture QP01 table CRC",
            ),
            "fault_latency_summary": latency_profile,
        }

    def _row_counts(self, env) -> dict[str, int]:
        rows = require_result_rows(
            env.execute_sql(
                f"SELECT bucket_id, COUNT(*) FROM {self.db}.{self.table} "
                "GROUP BY bucket_id ORDER BY bucket_id"
            ),
            "verify QP01 bucket row counts",
        )
        counts = {str(row[0]): int(row[1]) for row in rows}
        expected = {
            "bucket_a": self.decoy_row_count,
            self.target_bucket: self.target_current_row_count + self.target_history_row_count,
            "bucket_c": self.other_row_count,
        }
        if counts != expected:
            raise RuntimeError(
                "QP01 bucket distribution mismatch: "
                f"expected={expected!r}, observed={counts!r}"
            )
        return counts

    def _verify_policy(self, env) -> None:
        rows = require_result_rows(
            env.execute_sql(
                f"SELECT bucket_id, tenant_id, COUNT(*), SUM(is_current), MAX(policy_version) "
                f"FROM {self.db}.{self.policy_table} "
                "WHERE bucket_id IN ('bucket_a', 'bucket_b', 'bucket_c') "
                "GROUP BY bucket_id, tenant_id ORDER BY bucket_id, tenant_id"
            ),
            "verify QP01 bucket policies",
        )
        expected = [
            ["bucket_a", "tenant-a", 1, 1, 1],
            ["bucket_b", "tenant-b", self.policy_history_row_count, 1, self.policy_history_row_count],
            ["bucket_b", "tenant-noise", 1, 1, 1],
            ["bucket_c", "tenant-c", 1, 1, 1],
        ]
        normalized_rows = [
            [str(row[0]), str(row[1]), int(row[2]), int(row[3]), int(row[4])]
            for row in rows
        ]
        if normalized_rows != expected:
            raise RuntimeError(
                "QP01 bucket policy mismatch: "
                f"expected={expected!r}, observed={normalized_rows!r}"
            )

    def _version(self, env) -> str:
        rows = require_result_rows(env.execute_sql("SELECT VERSION()"), "read QP01 TiDB version")
        version = str(rows[0][0])
        if "v8.1.0" not in version:
            raise RuntimeError(
                f"QP01 requires the fixed TiDB v8.1.0 lane: observed_version={version!r}"
            )
        return version

    def _verify_fault_state(self, env) -> None:
        self._version(env)
        self._row_counts(env)
        self._verify_policy(env)
        rows = require_result_rows(
            env.execute_sql(f"SHOW CREATE TABLE {self.db}.{self.table}"),
            "verify QP01 fault table definition",
        )
        definition = json.dumps(rows, ensure_ascii=False, default=str).casefold()
        expected_index = (
            f"unique key `{self.original_index.casefold()}` "
            "(`name`,`bucket_id`,`version_id`)"
        )
        if re.sub(r"\s+", "", expected_index) not in re.sub(r"\s+", "", definition):
            raise RuntimeError(
                "QP01 fault table must expose the name-first composite index: "
                f"index={self.original_index!r}, definition={rows!r}"
            )
        policy_rows = require_result_rows(
            env.execute_sql(f"SHOW CREATE TABLE {self.db}.{self.policy_table}"),
            "verify QP01 policy table definition",
        )
        policy_definition = json.dumps(
            policy_rows,
            ensure_ascii=False,
            default=str,
        ).casefold()
        expected_policy_index = "key `idx_policy_tenant` (`tenant_id`)"
        if re.sub(r"\s+", "", expected_policy_index) not in re.sub(
            r"\s+", "", policy_definition
        ):
            raise RuntimeError(
                "QP01 policy table must expose the tenant-first policy index: "
                f"index='idx_policy_tenant', definition={policy_rows!r}"
            )
        expected_catalog_decoy = (
            f"key `{self.catalog_decoy_index.casefold()}` "
            "(`bucket_id`,`version_id`,`name`)"
        )
        if re.sub(r"\s+", "", expected_catalog_decoy) not in re.sub(
            r"\s+", "", definition
        ):
            raise RuntimeError(
                "QP01 fault table must expose the catalog decoy index: "
                f"index={self.catalog_decoy_index!r}, definition={rows!r}"
            )
        expected_admin_catalog_decoy = (
            f"key `{self.admin_catalog_decoy_index.casefold()}` "
            "(`updated_at`,`tenant_id`,`item_id`)"
        )
        if re.sub(r"\s+", "", expected_admin_catalog_decoy) not in re.sub(
            r"\s+", "", definition
        ):
            raise RuntimeError(
                "QP01 fault table must expose the admin catalog decoy index: "
                f"index={self.admin_catalog_decoy_index!r}, definition={rows!r}"
            )
        expected_policy_decoy = (
            f"key `{self.policy_decoy_index.casefold()}` "
            "(`tenant_id`,`policy_state`,`bucket_id`)"
        )
        if re.sub(r"\s+", "", expected_policy_decoy) not in re.sub(
            r"\s+", "", policy_definition
        ):
            raise RuntimeError(
                "QP01 policy table must expose the policy decoy index: "
                f"index={self.policy_decoy_index!r}, definition={policy_rows!r}"
            )
        plan_rows = require_result_rows(
            env.execute_sql(f"EXPLAIN ANALYZE {self.fault_query_sql}"),
            "verify QP01 fault plan",
        )
        plan_metrics = qp01_plan_metrics(plan_rows)
        if (
            self.original_index.casefold() not in plan_metrics["plan_text"]
            and self.catalog_decoy_index.casefold() not in plan_metrics["plan_text"]
            and "tablefullscan" not in plan_metrics["catalog_scan_operator"]
        ):
            raise RuntimeError(
                "QP01 fault plan does not expose a configured catalog fault index or a full scan: "
                f"indexes={(self.original_index, self.catalog_decoy_index)!r}, plan={plan_rows!r}"
            )
        if plan_metrics["index_scan_rows"] < self.fault_scan_floor:
            raise RuntimeError(
                "QP01 fault plan lost its correlated scan amplification: "
                f"scan_rows={plan_metrics['index_scan_rows']}, "
                f"required_at_least={self.fault_scan_floor}, plan={plan_rows!r}"
            )
        if plan_metrics["policy_scan_rows"] is None or plan_metrics["policy_scan_rows"] < self.policy_scan_floor:
            raise RuntimeError(
                "QP01 fault plan lost its policy lookup amplification: "
                f"policy_scan_rows={plan_metrics['policy_scan_rows']}, "
                f"required_at_least={self.policy_scan_floor}, plan={plan_rows!r}"
            )
        admin_plan_rows = require_result_rows(
            env.execute_sql(f"EXPLAIN ANALYZE {self.admin_fault_query_sql}"),
            "verify QP01 admin fault plan",
        )
        admin_plan_metrics = qp01_plan_metrics(admin_plan_rows)
        if self.admin_catalog_decoy_index.casefold() not in admin_plan_metrics["plan_text"]:
            raise RuntimeError(
                "QP01 admin fault plan must expose the updated_at-first decoy index: "
                f"index={self.admin_catalog_decoy_index!r}, plan={admin_plan_rows!r}"
            )
        if admin_plan_metrics["index_scan_rows"] < self.admin_fault_scan_floor:
            raise RuntimeError(
                "QP01 admin fault plan lost its tenant scan amplification: "
                f"scan_rows={admin_plan_metrics['index_scan_rows']}, "
                f"required_at_least={self.admin_fault_scan_floor}, plan={admin_plan_rows!r}"
            )


class TidbQueryPerfIndexOrderCorrelationScenario(TiDBScenario):
    scenario_id = "tidb_query_perf_index_order_correlation"
    description = (
        "TiDB v8.1 object-listing query performance degradation under correlated data and "
        "mixed access-path candidates, based on source O47."
    )
    cases = (_CASE, _CASE_REDUCED)

    def build_fault_plan(
        self,
        case: TidbQueryPerfIndexOrderCorrelationCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbQueryPerfIndexOrderCorrelationInjector,
                config={
                    "db": case.db,
                    "table": case.table,
                    "target_bucket": case.target_bucket,
                    "lower_bound": case.lower_bound,
                    "result_limit": case.result_limit,
                    "total_row_count": case.total_row_count,
                    "target_current_row_count": case.target_current_row_count,
                    "target_history_row_count": case.target_history_row_count,
                    "decoy_row_count": case.decoy_row_count,
                    "other_row_count": case.other_row_count,
                    "policy_noise_row_count": case.policy_noise_row_count,
                    "policy_cross_tenant_noise_row_count": (
                        case.policy_cross_tenant_noise_row_count
                    ),
                    "policy_history_row_count": case.policy_history_row_count,
                    "catalog_decoy_index": case.catalog_decoy_index,
                    "admin_catalog_decoy_index": case.admin_catalog_decoy_index,
                    "policy_decoy_index": case.policy_decoy_index,
                    "policy_scan_floor": case.policy_scan_floor,
                    "recovered_policy_scan_ceiling": case.recovered_policy_scan_ceiling,
                    "policy_table": case.policy_table,
                    "tenant_id": case.tenant_id,
                    "upper_bound": case.upper_bound,
                    "original_index": case.original_index,
                    "repaired_index": case.repaired_index,
                    "admin_repaired_index": case.admin_repaired_index,
                    "policy_repaired_index": case.policy_repaired_index,
                    "fault_query_sql": case.fault_query_sql,
                    "admin_fault_query_sql": case.admin_fault_query_sql,
                    "result_truth_sql": case.result_truth_sql,
                    "admin_result_truth_sql": case.admin_result_truth_sql,
                    "table_crc_sql": case.table_crc_sql,
                    "latency_warmup_count": case.latency_warmup_count,
                    "latency_sample_count": case.latency_sample_count,
                    "latency_outlier_tolerance": case.latency_outlier_tolerance,
                    "fault_scan_floor": case.fault_scan_floor,
                    "admin_fault_scan_floor": case.admin_fault_scan_floor,
                    "sql_timeout_seconds": case.runtime.sql_timeout_seconds,
                },
            ),
        )
