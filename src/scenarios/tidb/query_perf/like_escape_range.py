from collections.abc import Mapping
from dataclasses import dataclass, replace
import re

from src.database.query_results import (
    capture_query_result_truth,
    measure_latency_profile,
    query_result_truth_mismatch,
)
from src.database.sql import execute_result_rows, parse_json_object, require_success_payload
from src.database.tidb import catalog_processed_keys
from src.scenarios.evaluation.tidb.query_perf.like_escape_range import (
    TidbQueryPerfLikeEscapeRangeForLiteralUnderscoreEvaluatorCase,
    TidbQueryPerfLikeEscapeRangeForLiteralUnderscoreReducedDecoyEvaluatorCase,
)
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    validate_sql_identifier,
)

from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


_TARGET_QUERY = (
    "SELECT path, object_id, object_size, payload FROM test.qp07_search "
    "WHERE request_id = 7001 ORDER BY path, object_id LIMIT 40"
)
_WILDCARD_QUERY = (
    "SELECT path, object_id, object_size, payload FROM test.qp07_search "
    "WHERE request_id = 7002 ORDER BY path, object_id LIMIT 40"
)
_ADJACENT_QUERY = (
    "SELECT path, object_id, object_size, payload FROM test.qp07_search "
    "WHERE request_id = 7003 ORDER BY path, object_id LIMIT 20"
)
_LITERAL_PROBE_REQUEST_IDS = (7001, 7003, 7004, 7005, 7006, 7007, 7009, 7010, 7011, 7012, 7013, 7016, 7017, 7018, 7019)
_LITERAL_PROBE_QUERIES = tuple(
    (
        _TARGET_QUERY
        if request_id == 7001
        else "SELECT path, object_id, object_size, payload FROM test.qp07_search "
        f"WHERE request_id = {request_id} ORDER BY path, object_id LIMIT 20"
    )
    for request_id in _LITERAL_PROBE_REQUEST_IDS
)
_LITERAL_TRUTH_QUERY = (
    "SELECT path, object_id, object_size, payload FROM test.qp07_object_catalog "
    "WHERE bucket_id = 'bucket01' "
    "AND path LIKE 'tenant-east/2026\\_08/exports\\_2026/%' "
    "AND object_kind = 'file' AND visibility = 'customer' AND deleted = 0 "
    "AND object_size BETWEEN 4096 AND 8192 "
    "AND region_code = 'us-east-1' AND storage_tier = 'hot' "
    "AND lifecycle_state = 'active' AND retention_epoch >= 202608 "
    "AND legal_hold = 0 "
    "ORDER BY path, object_id LIMIT 40"
)
_LITERAL_INVENTORY_TRUTH_QUERY = (
    "SELECT r.request_id, COUNT(o.object_id), COALESCE(SUM(o.object_id), 0), "
    "COALESCE(BIT_XOR(CASE WHEN o.object_id IS NULL THEN NULL ELSE "
    "CRC32(CONCAT_WS('#', o.path, o.object_id, o.object_size, o.payload)) END), 0) "
    "FROM test.qp07_search_requests AS r "
    "LEFT JOIN test.qp07_path_bindings AS b "
    "ON b.request_id = r.request_id AND b.bucket_id = r.bucket_id "
    "LEFT JOIN test.qp07_object_catalog AS o "
    "ON o.bucket_id = b.bucket_id "
    "AND o.path >= b.lower_key AND o.path < b.upper_key "
    "AND o.path LIKE CONCAT(b.compiled_prefix, "
    "REPLACE(REPLACE(REPLACE(r.path_fragment, CHAR(92), CONCAT(CHAR(92), CHAR(92))), "
    "'%', CONCAT(CHAR(92), '%')), '_', CONCAT(CHAR(92), '_')), r.path_suffix) "
    "AND o.object_kind = r.object_kind "
    "AND o.visibility = r.visibility "
    "AND o.object_size BETWEEN r.min_object_size AND r.max_object_size "
    "AND o.region_code = 'us-east-1' AND o.storage_tier = 'hot' "
    "AND o.lifecycle_state = 'active' AND o.retention_epoch >= 202608 "
    "AND o.legal_hold = 0 "
    "AND (r.include_deleted = 1 OR o.deleted = 0) "
    "WHERE r.active = 1 AND r.search_mode = 'literal_prefix' "
    "GROUP BY r.request_id ORDER BY r.request_id"
)
_WILDCARD_TRUTH_QUERY = (
    "SELECT COUNT(*), COALESCE(SUM(object_id), 0), "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', path, object_id, object_size, payload))), 0) "
    "FROM test.qp07_object_catalog "
    "WHERE bucket_id = 'bucket01' AND path LIKE 'tenant-east/2026_%/exports_%/%' "
    "AND object_kind = 'file' AND visibility = 'customer' AND deleted = 0 "
    "AND object_size BETWEEN 4096 AND 8192 "
    "AND region_code = 'us-east-1' AND storage_tier = 'hot' "
    "AND lifecycle_state = 'active' AND retention_epoch >= 202608 "
    "AND legal_hold = 0"
)
_CATALOG_CRC_QUERY = (
    "SELECT COUNT(*), COALESCE(SUM(object_id), 0), "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', object_id, bucket_id, path, object_size, payload, object_kind, visibility, deleted, region_code, storage_tier, lifecycle_state, retention_epoch, legal_hold))), 0) "
    "FROM test.qp07_object_catalog"
)
_REQUEST_CRC_QUERY = (
    "SELECT COUNT(*), COALESCE(SUM(request_id), 0), "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', request_id, bucket_id, path_prefix, path_fragment, path_suffix, search_mode, object_kind, visibility, min_object_size, max_object_size, include_deleted, request_name))), 0) "
    "FROM test.qp07_search_requests"
)
_BINDING_CRC_QUERY = (
    "SELECT COUNT(*), COALESCE(SUM(request_id), 0), "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', request_id, bucket_id, compiled_prefix, lower_key, upper_key, bind_status))), 0) "
    "FROM test.qp07_path_bindings"
)
_REQUEST_INVENTORY_QUERY = (
    "SELECT request_id, bucket_id, path_prefix, path_fragment, path_suffix, search_mode, object_kind, visibility, min_object_size, max_object_size, include_deleted, request_name "
    "FROM test.qp07_search_requests ORDER BY request_id"
)
_BUCKET_INVENTORY_QUERY = (
    "SELECT bucket_id, object_kind, visibility, deleted, COUNT(*) "
    "FROM test.qp07_object_catalog "
    "GROUP BY bucket_id, object_kind, visibility, deleted "
    "ORDER BY bucket_id, object_kind, visibility, deleted"
)


def _background_workload() -> BackgroundWorkloadSpec:
    return BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="qp07_target_object_search",
                sql=_TARGET_QUERY,
                qps=0.34,
                tier="TARGET_SEARCH",
                application_name="object-search-api",
            ),
            WorkloadProfile(
                name="qp07_wildcard_directory_search",
                sql=_WILDCARD_QUERY,
                qps=0.16,
                tier="PATTERN_SEARCH",
                application_name="directory-browser-api",
            ),
            WorkloadProfile(
                name="qp07_adjacent_namespace_search",
                sql=_ADJACENT_QUERY,
                qps=0.18,
                tier="NEIGHBOR_SEARCH",
                application_name="object-search-neighbor-api",
            ),
            WorkloadProfile(
                name="qp07_catalog_bucket_inventory",
                sql=_BUCKET_INVENTORY_QUERY,
                qps=0.14,
                tier="INVENTORY",
                application_name="bucket-inventory-worker",
            ),
            WorkloadProfile(
                name="qp07_request_metadata_audit",
                sql=_REQUEST_INVENTORY_QUERY,
                qps=0.11,
                tier="REQUEST_METADATA",
                application_name="search-request-audit",
            ),
            WorkloadProfile(
                name="qp07_route_context_audit",
                sql="SELECT request_id, route_shape, route_contract, tail_policy, request_lane FROM test.qp07_request_route ORDER BY request_id",
                qps=0.09,
                tier="ROUTE_CONTEXT",
                application_name="search-route-audit",
            ),
            WorkloadProfile(
                name="qp07_export_namespace_probe",
                sql=(
                    "SELECT COUNT(*) FROM test.qp07_object_catalog "
                    "WHERE bucket_id = 'bucket01' "
                    "AND path LIKE 'tenant-east/2026_%/exports_%/%' "
                    "AND object_kind = 'file' AND visibility = 'customer' AND deleted = 0"
                ),
                qps=0.15,
                tier="PREFIX_NEIGHBOR",
                application_name="catalog-health-probe",
            ),
        ),
        worker_count=3,
        seed=20260806,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=12,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfLikeEscapeRangeForLiteralUnderscoreScenarioCase(TiDBScenarioCase):
    db: str
    catalog_table: str
    request_table: str
    binding_table: str
    contract_table: str
    builder_view: str
    route_view: str
    suffix_view: str
    view: str
    bucket_id: str
    target_request_id: int
    wildcard_request_id: int
    target_path_prefix: str
    target_path_fragment: str
    target_path_suffix: str
    wildcard_path_prefix: str
    wildcard_path_fragment: str
    wildcard_path_suffix: str
    target_object_kind: str
    target_visibility: str
    target_min_object_size: int
    target_max_object_size: int
    target_include_deleted: int
    target_range_start: str
    target_range_end: str
    fault_fingerprint_sql: str
    wildcard_fingerprint_sql: str
    adjacent_fingerprint_sql: str
    literal_probe_sqls: tuple[str, ...]
    literal_truth_sql: str
    literal_inventory_truth_sql: str
    wildcard_truth_sql: str
    catalog_crc_sql: str
    request_crc_sql: str
    binding_crc_sql: str
    request_inventory_sql: str
    bucket_inventory_sql: str
    row_count: int
    request_count: int
    binding_count: int
    target_result_limit: int
    wildcard_result_limit: int
    noise_row_count: int
    active_neighbor_row_count: int
    other_bucket_row_count: int
    outside_range_row_count: int
    index_name: str
    processed_key_ratio: float
    p95_ratio: float


_CASE = TidbQueryPerfLikeEscapeRangeForLiteralUnderscoreScenarioCase(
    case_id="literal_underscore_like_range",
    case_no=0,
    evaluator=TidbQueryPerfLikeEscapeRangeForLiteralUnderscoreEvaluatorCase,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": (
                        "the affected request is literal_prefix, so the shared compiler must keep the "
                        "namespace prefix and the selected static route suffix literal before appending "
                        "the wildcard tail, while like_pattern requests must keep their wildcard prefix "
                        "and fragment semantics"
                    ),
                    "entity": "literal_underscore_like_range",
                    "evidence": ["request inventory and route definitions distinguish literal and wildcard requests"],
                },
                {
                    "type": "finding",
                    "factor": (
                        "the refactored suffix route contains manually written SQL string literals with an underscore "
                        "and appends one of them after the already compiled prefix without applying literal "
                        "LIKE handling, so the regression is in query generation rather than in the catalog "
                        "or TiDB data"
                    ),
                    "entity": "literal_underscore_like_range",
                    "evidence": ["SHOW CREATE VIEW exposes the uncompiled static route literal"],
                },
                {
                    "type": "finding",
                    "factor": (
                        "the unprocessed underscore in the selected static literal makes TiDB derive a broad "
                        "range over neighboring object families, while the extra object predicates filter "
                        "most candidates after the scan and inflate processed keys and p95"
                    ),
                    "entity": "literal_underscore_like_range",
                    "evidence": ["EXPLAIN ANALYZE shows a broad range with elevated processed keys and p95"],
                },
            ]
        },
        "outcome": {
            "changes": [
                "compile every literal route into a route-specific escaped LIKE predicate and [lower, upper) range while preserving the wildcard branch"
            ],
            "verification": [
                "literal and wildcard business truth, all literal route probes, protected CRCs, processed-key limits, and p95 recovered"
            ],
        },
        "summary": "The shared literal route compiler was repaired without changing catalog, request, or binding data.",
    },
    title="Object path search returns the right directory family but develops a high latency tail under mixed request traffic.",
    alert=(
        "[CRITICAL] [Object Search/API] the object-prefix endpoint has a sustained high p95 and a sharp rise in "
        "TiKV processed keys, while request latency and bucket inventory traffic are otherwise stable. The affected "
        "request belongs to bucket01 and the tenant-east 2026_08 exports_2026 namespace. Several adjacent namespaces "
        "and legitimate pattern-search requests are active at the same time. Diagnose the request path and restore "
        "the endpoint without changing catalog data, search request metadata, or serving route configuration."
    ),
    initial_state={
        "status": "degraded",
        "endpoint": "object-prefix-search",
        "target_request": "bucket01/tenant-east/2026_08/exports_2026/",
        "result_semantics": "expected_rows_present_but_scan_tail_degraded",
    },
    expected_target={
        "status": "recovered",
        "target_request_semantics": "literal_prefix_with_suffix",
        "pattern_request_semantics": "wildcard_preserved",
        "catalog_crc": "unchanged",
        "request_crc": "unchanged",
        "binding_crc": "unchanged",
        "range": "compiled_literal_range",
        "processed_keys": "substantially_lower",
        "p95": "substantially_lower",
    },
    background_workload=_background_workload(),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.939722,
        reference_run_ids=(
            "reference-215__tidb_query_perf_like_escape_range__literal_underscore_like_range__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=120,
        image_group_key="qp07-literal-prefix-suffix-template",
        tidb_memory_mb=4096,
    ),
    db="test",
    catalog_table="qp07_object_catalog",
    request_table="qp07_search_requests",
    binding_table="qp07_path_bindings",
    contract_table="qp07_route_contracts",
    builder_view="qp07_query_builder",
    route_view="qp07_request_route",
    suffix_view="qp07_suffix_template",
    view="qp07_search",
    bucket_id="bucket01",
    target_request_id=7001,
    wildcard_request_id=7002,
    target_path_prefix="tenant-east/2026_08/",
    target_path_fragment="exports_2026/",
    target_path_suffix="%",
    wildcard_path_prefix="tenant-east/2026_%/",
    wildcard_path_fragment="exports_%/",
    wildcard_path_suffix="%",
    target_object_kind="file",
    target_visibility="customer",
    target_min_object_size=4096,
    target_max_object_size=8192,
    target_include_deleted=0,
    target_range_start="tenant-east/2026_08/exports_2026/",
    target_range_end="tenant-east/2026_08/exports_20260",
    fault_fingerprint_sql=_TARGET_QUERY,
    wildcard_fingerprint_sql=_WILDCARD_QUERY,
    adjacent_fingerprint_sql=_ADJACENT_QUERY,
    literal_probe_sqls=_LITERAL_PROBE_QUERIES,
    literal_truth_sql=_LITERAL_TRUTH_QUERY,
    literal_inventory_truth_sql=_LITERAL_INVENTORY_TRUTH_QUERY,
    wildcard_truth_sql=_WILDCARD_TRUTH_QUERY,
    catalog_crc_sql=_CATALOG_CRC_QUERY,
    request_crc_sql=_REQUEST_CRC_QUERY,
    binding_crc_sql=_BINDING_CRC_QUERY,
    request_inventory_sql=_REQUEST_INVENTORY_QUERY,
    bucket_inventory_sql=_BUCKET_INVENTORY_QUERY,
    row_count=61040,
    request_count=19,
    binding_count=15,
    target_result_limit=40,
    wildcard_result_limit=40,
    noise_row_count=50000,
    active_neighbor_row_count=1000,
    other_bucket_row_count=6000,
    outside_range_row_count=4000,
    index_name="idx_bucket_path",
    processed_key_ratio=0.03,
    p95_ratio=0.70,
)

_REDUCED_DECOY_PROFILE_NAMES = {
    "qp07_target_object_search",
    "qp07_wildcard_directory_search",
    "qp07_adjacent_namespace_search",
    "qp07_catalog_bucket_inventory",
}

_CASE_REDUCED_DECOY = replace(
    _CASE,
    case_id="literal_underscore_like_range_simple_decoy",
    case_no=1,
    evaluator=TidbQueryPerfLikeEscapeRangeForLiteralUnderscoreReducedDecoyEvaluatorCase,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": (
                        "the affected request is literal_prefix, so the shared compiler must keep the "
                        "namespace prefix and the selected static route suffix literal before appending "
                        "the wildcard tail, while like_pattern requests must keep their wildcard prefix "
                        "and fragment semantics"
                    ),
                    "entity": "literal_underscore_like_range_simple_decoy",
                    "evidence": ["request inventory and route definitions distinguish literal and wildcard requests"],
                },
                {
                    "type": "finding",
                    "factor": (
                        "the refactored suffix route contains manually written SQL string literals with an underscore "
                        "and appends one of them after the already compiled prefix without applying literal "
                        "LIKE handling, so the regression is in query generation rather than in the catalog "
                        "or TiDB data"
                    ),
                    "entity": "literal_underscore_like_range_simple_decoy",
                    "evidence": [
                        (
                            "the unprocessed underscore in the selected static literal makes TiDB derive a broad "
                            "range over neighboring object families, while the extra object predicates filter "
                            "most candidates after the scan and inflate processed keys and p95"
                        ),
                        "SHOW CREATE VIEW exposes the uncompiled static route literal and EXPLAIN ANALYZE shows "
                        "the broad range with elevated processed keys and p95",
                    ],
                },
            ]
        },
        "outcome": {
            "changes": [
                "compile every literal route into a route-specific escaped LIKE predicate and [lower, upper) range while preserving the wildcard branch"
            ],
            "verification": [
                "literal and wildcard business truth, all literal route probes, protected CRCs, processed-key limits, and p95 recovered"
            ],
        },
        "summary": "The shared literal route compiler was repaired without changing catalog, request, or binding data.",
    },
    title="Object path search returns the right directory family but develops a high latency tail under mixed request traffic.",
    row_count=30_540,
    noise_row_count=25_000,
    active_neighbor_row_count=500,
    other_bucket_row_count=3_000,
    outside_range_row_count=2_000,
    background_workload=replace(
        _background_workload(),
        profiles=tuple(
            profile for profile in _background_workload().profiles if profile.name in _REDUCED_DECOY_PROFILE_NAMES
        ),
        worker_count=2,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.552056,
        reference_run_ids=(
            "tidb-reference-2__tidb_query_perf_like_escape_range__"
            "literal_underscore_like_range_simple_decoy__mock__r001",
        ),
    ),
)


class TidbQueryPerfLikeEscapeRangeScenario(TiDBScenario):
    scenario_id = "tidb_query_perf_like_escape_range"
    description = "Diagnoses and repairs a high-tail object-prefix query while preserving literal and wildcard request semantics."
    cases = (_CASE, _CASE_REDUCED_DECOY)

    def build_fault_plan(
        self,
        case: TidbQueryPerfLikeEscapeRangeForLiteralUnderscoreScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbQueryPerfLikeEscapeRangeInjector,
                config={
                    "db": case.db,
                    "catalog_table": case.catalog_table,
                    "request_table": case.request_table,
                    "binding_table": case.binding_table,
                    "contract_table": case.contract_table,
                    "builder_view": case.builder_view,
                    "route_view": case.route_view,
                    "suffix_view": case.suffix_view,
                    "view": case.view,
                    "bucket_id": case.bucket_id,
                    "target_request_id": case.target_request_id,
                    "wildcard_request_id": case.wildcard_request_id,
                    "target_path_prefix": case.target_path_prefix,
                    "target_path_fragment": case.target_path_fragment,
                    "target_path_suffix": case.target_path_suffix,
                    "wildcard_path_prefix": case.wildcard_path_prefix,
                    "wildcard_path_fragment": case.wildcard_path_fragment,
                    "wildcard_path_suffix": case.wildcard_path_suffix,
                    "target_object_kind": case.target_object_kind,
                    "target_visibility": case.target_visibility,
                    "target_min_object_size": case.target_min_object_size,
                    "target_max_object_size": case.target_max_object_size,
                    "target_include_deleted": case.target_include_deleted,
                    "target_range_start": case.target_range_start,
                    "target_range_end": case.target_range_end,
                    "fault_fingerprint_sql": case.fault_fingerprint_sql,
                    "wildcard_fingerprint_sql": case.wildcard_fingerprint_sql,
                    "adjacent_fingerprint_sql": case.adjacent_fingerprint_sql,
                    "literal_truth_sql": case.literal_truth_sql,
                    "literal_inventory_truth_sql": case.literal_inventory_truth_sql,
                    "wildcard_truth_sql": case.wildcard_truth_sql,
                    "catalog_crc_sql": case.catalog_crc_sql,
                    "request_crc_sql": case.request_crc_sql,
                    "binding_crc_sql": case.binding_crc_sql,
                    "request_inventory_sql": case.request_inventory_sql,
                    "bucket_inventory_sql": case.bucket_inventory_sql,
                    "row_count": case.row_count,
                    "request_count": case.request_count,
                    "binding_count": case.binding_count,
                    "target_result_limit": case.target_result_limit,
                    "wildcard_result_limit": case.wildcard_result_limit,
                    "noise_row_count": case.noise_row_count,
                    "active_neighbor_row_count": case.active_neighbor_row_count,
                    "other_bucket_row_count": case.other_bucket_row_count,
                    "outside_range_row_count": case.outside_range_row_count,
                    "index_name": case.index_name,
                },
            ),
        )
_LITERAL_ROUTE_TEMPLATES = (
    ("exports_2026/", "%", "exports_2026/%"),
    ("exports_2026/", "object-00%", "exports_2026/object-00%"),
    ("exports_2026/", "object-000%", "exports_2026/object-000%"),
    ("ingest_2026/", "%", "ingest_2026/%"),
    ("reports_2026/", "%", "reports_2026/%"),
    ("snapshots_2026/", "%", "snapshots_2026/%"),
    ("manifests_2026/", "%", "manifests_2026/%"),
    ("archive_2026/", "%", "archive_2026/%"),
    ("staging_2026/", "%", "staging_2026/%"),
    ("analytics_2026/", "%", "analytics_2026/%"),
    ("exports_2026_archive/", "%", "exports_2026_archive/%"),
    ("exports_2026/", "object-%", "exports_2026/object-%"),
    ("exports_2026/", "object-0%", "exports_2026/object-0%"),
    ("ingest_2026/", "object-%", "ingest_2026/object-%"),
    ("reports_2026/", "object-%", "reports_2026/object-%"),
    ("snapshots_2026/", "object-%", "snapshots_2026/object-%"),
    ("manifests_2026/", "object-%", "manifests_2026/object-%"),
    ("archive_2026/", "object-%", "archive_2026/object-%"),
    ("staging_2026/", "object-%", "staging_2026/object-%"),
    ("analytics_2026/", "object-%", "analytics_2026/object-%"),
    ("exports_2026_archive/", "object-%", "exports_2026_archive/object-%"),
    ("exports_2026/", "manifest-%", "exports_2026/manifest-%"),
    ("exports_2026/", "checksum-%", "exports_2026/checksum-%"),
    ("ingest_2026/", "batch-%", "ingest_2026/batch-%"),
    ("reports_2026/", "report-%", "reports_2026/report-%"),
    ("billing%_2026/", "%", "billing%_2026/%"),
    ("billing%_2026/", "object-%", "billing%_2026/object-%"),
    ("retention_2026/", "%", "retention_2026/%"),
    ("retention_2026/", "object-%", "retention_2026/object-%"),
    ("legal_%_archive/", "%", "legal_%_archive/%"),
    ("legal_%_archive/", "object-%", "legal_%_archive/object-%"),
    ("exports%_2026/", "%", "exports%_2026/%"),
)


class TidbQueryPerfLikeEscapeRangeInjector(BaseFaultInjector):
    """Create the QP07 request compiler regression behind an application search view."""

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._drop_owned_objects(context.env)
        self._create_catalog(context.env)
        self._create_request_table(context.env)
        self._create_binding_table(context.env)
        self._create_contract_table(context.env)
        self._load_catalog(context.env)
        self._load_requests(context.env)
        self._load_bindings(context.env)
        self._load_contracts(context.env)
        self._execute(context.env, f"ANALYZE TABLE {self.db}.{self.catalog_table}", "analyze QP07 catalog")
        self._execute(context.env, f"ANALYZE TABLE {self.db}.{self.request_table}", "analyze QP07 requests")
        self._execute(context.env, f"ANALYZE TABLE {self.db}.{self.binding_table}", "analyze QP07 bindings")
        self._create_views(context.env)
        self._verify_fault_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._create_views(context.env)
        self._verify_fault_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._verify_fault_state(context.env)
        fault_plan = execute_result_rows(
            context.env.execute_sql,
            f"EXPLAIN ANALYZE {self.fault_fingerprint_sql}",
            "capture QP07 faulty EXPLAIN ANALYZE",
        )
        fault_latency_profile = measure_latency_profile(
            context.env.execute_sql,
            self.fault_fingerprint_sql,
            warmup_samples=0,
            measured_samples=5,
            context="measure QP07 faulty target latency",
        )
        literal_truth_payload = self._payload(
            context.env,
            self.literal_truth_sql,
            "capture QP07 literal business truth",
        )
        wildcard_truth_payload = self._payload(
            context.env,
            self.wildcard_truth_sql,
            "capture QP07 wildcard business truth",
        )
        return {
            "fault_plan": fault_plan,
            "fault_processed_keys": catalog_processed_keys(
                fault_plan,
                table_name=self.catalog_table,
                index_name=self.index_name,
                table_alias="o",
            ),
            "fault_p95_ms": fault_latency_profile["p95_ms"],
            "fault_p95_samples_ms": fault_latency_profile["samples_ms"],
            "literal_business_truth": capture_query_result_truth(literal_truth_payload, ordered=True),
            "literal_inventory_truth": tuple(
                tuple(row)
                for row in execute_result_rows(
                    context.env.execute_sql,
                    self.literal_inventory_truth_sql,
                    "capture QP07 literal request truth",
                )
            ),
            "wildcard_business_truth": tuple(tuple(row) for row in wildcard_truth_payload["result"]),
            "fault_result": self._payload(
                context.env,
                self.fault_fingerprint_sql,
                "capture QP07 faulty target result",
            ),
            "catalog_crc": self._crc(context.env, self.catalog_crc_sql, "capture QP07 catalog CRC"),
            "request_crc": self._crc(context.env, self.request_crc_sql, "capture QP07 request CRC"),
            "binding_crc": self._crc(context.env, self.binding_crc_sql, "capture QP07 binding CRC"),
            "target_request": self._target_request(context.env),
            "request_inventory": tuple(
                tuple(row)
                for row in execute_result_rows(
                    context.env.execute_sql,
                    self.request_inventory_sql,
                    "capture QP07 request inventory",
                )
            ),
            "bucket_inventory": tuple(
                tuple(row)
                for row in execute_result_rows(
                    context.env.execute_sql,
                    self.bucket_inventory_sql,
                    "capture QP07 bucket inventory",
                )
            ),
            "builder_definition": self._view_definition(context.env, self.builder_view),
            "route_definition": self._view_definition(context.env, self.route_view),
            "suffix_definition": self._view_definition(context.env, self.suffix_view),
            "search_definition": self._view_definition(context.env, self.view),
            "topsql": self._metric(context.env, "topsql"),
            "slow_queries": self._metric(context.env, "slow_queries"),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_fault_state(context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._drop_owned_objects(context.env)
        remaining = self._payload(
            context.env,
            "SELECT COUNT(*) FROM information_schema.tables "
            f"WHERE table_schema = '{self.db}' "
            f"AND table_name IN ('{self.catalog_table}', '{self.request_table}', '{self.binding_table}', '{self.contract_table}', "
            f"'{self.builder_view}', '{self.route_view}', '{self.suffix_view}', '{self.view}')",
            "verify QP07 recovery",
        )
        if int(remaining["result"][0][0]) != 0:
            raise RuntimeError(
                "QP07 recovery left owned objects behind: "
                f"database={self.db!r}, tables={(self.catalog_table, self.request_table, self.binding_table, self.contract_table)!r}, "
                f"views={(self.builder_view, self.route_view, self.suffix_view, self.view)!r}, remaining={remaining['result']!r}"
            )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.catalog_table = validate_sql_identifier(str(config["catalog_table"]), "catalog table")
        self.request_table = validate_sql_identifier(str(config["request_table"]), "request table")
        self.binding_table = validate_sql_identifier(str(config["binding_table"]), "binding table")
        self.contract_table = validate_sql_identifier(str(config["contract_table"]), "route contract table")
        self.builder_view = validate_sql_identifier(str(config["builder_view"]), "query builder view")
        self.route_view = validate_sql_identifier(str(config["route_view"]), "request route view")
        self.suffix_view = validate_sql_identifier(str(config["suffix_view"]), "suffix template view")
        self.view = validate_sql_identifier(str(config["view"]), "search view")
        self.bucket_id = str(config["bucket_id"])
        self.target_request_id = int(config["target_request_id"])
        self.wildcard_request_id = int(config["wildcard_request_id"])
        self.target_path_prefix = str(config["target_path_prefix"])
        self.target_path_fragment = str(config["target_path_fragment"])
        self.target_path_suffix = str(config["target_path_suffix"])
        self.wildcard_path_prefix = str(config["wildcard_path_prefix"])
        self.wildcard_path_fragment = str(config["wildcard_path_fragment"])
        self.wildcard_path_suffix = str(config["wildcard_path_suffix"])
        self.target_object_kind = str(config["target_object_kind"])
        self.target_visibility = str(config["target_visibility"])
        self.target_min_object_size = int(config["target_min_object_size"])
        self.target_max_object_size = int(config["target_max_object_size"])
        self.target_include_deleted = int(config["target_include_deleted"])
        self.target_range_start = str(config["target_range_start"])
        self.target_range_end = str(config["target_range_end"])
        self.fault_fingerprint_sql = str(config["fault_fingerprint_sql"])
        self.wildcard_fingerprint_sql = str(config["wildcard_fingerprint_sql"])
        self.adjacent_fingerprint_sql = str(config["adjacent_fingerprint_sql"])
        self.literal_truth_sql = str(config["literal_truth_sql"])
        self.literal_inventory_truth_sql = str(config["literal_inventory_truth_sql"])
        self.wildcard_truth_sql = str(config["wildcard_truth_sql"])
        self.catalog_crc_sql = str(config["catalog_crc_sql"])
        self.request_crc_sql = str(config["request_crc_sql"])
        self.binding_crc_sql = str(config["binding_crc_sql"])
        self.request_inventory_sql = str(config["request_inventory_sql"])
        self.bucket_inventory_sql = str(config["bucket_inventory_sql"])
        self.row_count = int(config["row_count"])
        self.request_count = int(config["request_count"])
        self.binding_count = int(config["binding_count"])
        self.target_result_limit = int(config["target_result_limit"])
        self.wildcard_result_limit = int(config["wildcard_result_limit"])
        self.noise_row_count = int(config["noise_row_count"])
        self.active_neighbor_row_count = int(config["active_neighbor_row_count"])
        self.other_bucket_row_count = int(config["other_bucket_row_count"])
        self.outside_range_row_count = int(config["outside_range_row_count"])
        self.index_name = validate_sql_identifier(str(config["index_name"]), "path index")

    def _drop_owned_objects(self, env) -> None:
        for view in (self.view, self.suffix_view, self.route_view, self.builder_view):
            self._execute(env, f"DROP VIEW IF EXISTS {self.db}.{view}", f"drop QP07 view {view}")
        for table in (self.request_table, self.binding_table, self.contract_table, self.catalog_table):
            self._execute(env, f"DROP TABLE IF EXISTS {self.db}.{table}", f"drop QP07 table {table}")

    def _create_catalog(self, env) -> None:
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.catalog_table} ("
            "object_id BIGINT PRIMARY KEY, "
            "bucket_id VARCHAR(64) NOT NULL, "
            "path VARCHAR(255) NOT NULL, "
            "object_size BIGINT NOT NULL, "
            "payload VARCHAR(128) NOT NULL, "
            "object_kind VARCHAR(32) NOT NULL, "
            "visibility VARCHAR(32) NOT NULL, "
            "deleted TINYINT NOT NULL, "
            "region_code VARCHAR(32) NOT NULL, "
            "storage_tier VARCHAR(32) NOT NULL, "
            "lifecycle_state VARCHAR(32) NOT NULL, "
            "retention_epoch BIGINT NOT NULL, "
            "legal_hold TINYINT NOT NULL, "
            f"KEY {self.index_name} (bucket_id, path, object_id))",
            "create QP07 catalog",
        )

    def _create_request_table(self, env) -> None:
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.request_table} ("
            "request_id BIGINT PRIMARY KEY, "
            "bucket_id VARCHAR(64) NOT NULL, "
            "path_prefix VARCHAR(255) NOT NULL, "
            "path_fragment VARCHAR(255) NOT NULL, "
            "path_suffix VARCHAR(255) NOT NULL, "
            "search_mode VARCHAR(32) NOT NULL, "
            "object_kind VARCHAR(32) NOT NULL, "
            "visibility VARCHAR(32) NOT NULL, "
            "min_object_size BIGINT NOT NULL, "
            "max_object_size BIGINT NOT NULL, "
            "include_deleted TINYINT NOT NULL, "
            "request_name VARCHAR(96) NOT NULL, "
            "active TINYINT NOT NULL, "
            "KEY idx_search_mode (search_mode, request_id))",
            "create QP07 request table",
        )

    def _create_binding_table(self, env) -> None:
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.binding_table} ("
            "request_id BIGINT PRIMARY KEY, "
            "bucket_id VARCHAR(64) NOT NULL, "
            "compiled_prefix VARCHAR(255) NOT NULL, "
            "lower_key VARCHAR(255) NOT NULL, "
            "upper_key VARCHAR(255) NOT NULL, "
            "bind_status VARCHAR(32) NOT NULL, "
            f"KEY idx_binding_bucket (bucket_id, lower_key, upper_key, request_id))",
            "create QP07 binding table",
        )

    def _create_contract_table(self, env) -> None:
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.contract_table} ("
            "contract_id BIGINT PRIMARY KEY, "
            "search_mode VARCHAR(32) NOT NULL, "
            "route_token VARCHAR(255) NOT NULL, "
            "route_upper_bound VARCHAR(255) NOT NULL, "
            "tail_token VARCHAR(255) NOT NULL, "
            "route_shape VARCHAR(64) NOT NULL, "
            "access_lane VARCHAR(64) NOT NULL, "
            "route_status VARCHAR(32) NOT NULL, "
            "route_priority BIGINT NOT NULL, "
            "min_object_size BIGINT NOT NULL, "
            "max_object_size BIGINT NOT NULL, "
            "region_scope VARCHAR(32) NOT NULL, "
            "storage_tier VARCHAR(32) NOT NULL, "
            "lifecycle_state VARCHAR(32) NOT NULL, "
            "min_retention_epoch BIGINT NOT NULL, "
            "legal_hold_required TINYINT NOT NULL, "
            "active TINYINT NOT NULL, "
            f"KEY idx_route_contract (search_mode, route_token, tail_token, active))",
            "create QP07 route contract table",
        )

    def _load_catalog(self, env) -> None:
        rows = [
            (
                index,
                self.bucket_id,
                f"tenant-east/2026_08/exports_2026/object-{index:04d}",
                4096 + index,
                f"target-export-{index:04d}",
                "file",
                "customer",
                0,
            )
            for index in range(1, 13)
        ]
        rows.extend(
            (
                400000 + (index - 1) * 2 + ordinal,
                self.bucket_id,
                f"tenant-east/2026_08/{fragment}object-{ordinal:04d}",
                4096 + (index - 1) * 2 + ordinal,
                f"target-{fragment.rstrip('/').replace('/', '-')}-{ordinal:04d}",
                "file",
                "customer",
                0,
            )
            for index, fragment in enumerate(
                (
                    "ingest_2026/",
                    "reports_2026/",
                    "snapshots_2026/",
                    "manifests_2026/",
                    "archive_2026/",
                    "staging_2026/",
                    "analytics_2026/",
                    "exports_2026_archive/",
                ),
                start=1,
            )
            for ordinal in range(1, 3)
        )
        months = tuple(f"{index:02d}" for index in range(1, 13))
        variants = (
            "exports-2026",
            "exportsA2026",
            "exports.2026",
            "exports/2026",
            "exportsX2026",
            "exports-v2026",
            "exports_2025",
            "exports_2027",
            "ingest_2026",
            "reports_2026",
            "snapshots_2026",
            "manifests_2026",
            "staging_2026",
            "analytics_2026",
        )
        rows.extend(
            (
                500000 + index,
                self.bucket_id,
                f"tenant-east/2026_{('08' if index % 5 else '07')}/{self._active_neighbor_variant(index)}/object-{index:06d}",
                4096 + (index % 2048),
                f"live-neighbor-{index:06d}",
                "file",
                "customer",
                0,
            )
            for index in range(self.active_neighbor_row_count)
        )
        rows.extend(
            (
                600000 + index,
                self.bucket_id,
                f"tenant-east/2026_08/billing%_2026/object-{index:04d}",
                4096 + index,
                f"target-billing-percent-{index:04d}",
                "file",
                "customer",
                0,
            )
            for index in range(1, 13)
        )
        rows.extend(
            (
                100000 + index,
                self.bucket_id,
                self._noise_path(index, months, variants),
                8192 + index,
                f"tenant-east-object-{index:06d}",
                "archive",
                "internal",
                1,
            )
            for index in range(self.noise_row_count)
        )
        rows.extend(
            (
                200000 + index,
                f"bucket{2 + index % 12:02d}",
                f"tenant-east/2026_{months[index % len(months)]}/{variants[index % len(variants)]}/object-{index:06d}",
                12288 + index,
                f"cross-bucket-object-{index:06d}",
                "archive",
                "internal",
                1,
            )
            for index in range(self.other_bucket_row_count)
        )
        rows.extend(
            (
                300000 + index,
                self.bucket_id,
                f"tenant-west/2026_{months[index % len(months)]}/{variants[index % len(variants)]}/object-{index:06d}",
                16384 + index,
                f"outside-tenant-object-{index:06d}",
                "archive",
                "internal",
                1,
            )
            for index in range(self.outside_range_row_count)
        )
        if len(rows) != self.row_count:
            raise RuntimeError(
                "QP07 catalog fixture row declaration mismatch: "
                f"declared={self.row_count}, generated={len(rows)}"
            )
        rows = tuple(row + self._catalog_dimensions(row) for row in rows)
        self._insert_batches(
            env,
            self.catalog_table,
            (
                "object_id",
                "bucket_id",
                "path",
                "object_size",
                "payload",
                "object_kind",
                "visibility",
                "deleted",
                "region_code",
                "storage_tier",
                "lifecycle_state",
                "retention_epoch",
                "legal_hold",
            ),
            rows,
            "load QP07 catalog",
        )

    def _catalog_dimensions(self, row: tuple) -> tuple:
        _, bucket_id, path, _, _, object_kind, visibility, deleted = row
        if object_kind == "file" and visibility == "customer" and deleted == 0:
            return ("us-east-1", "hot", "active", 202608, 0)
        region = "us-west-2" if path.startswith("tenant-west/") else "eu-west-1" if bucket_id != self.bucket_id else "us-east-1"
        return (region, "cold", "archived", 202401, 0)

    @staticmethod
    def _noise_path(index: int, months: tuple[str, ...], variants: tuple[str, ...]) -> str:
        month = "08" if index % 5 else months[(index // 5) % len(months)]
        archive_families = (
            "exports_2026_archive_snapshot",
            "exports_2026_manifest_backfill",
            "exports_2026_reprocess",
            "exports_2026_legal_hold",
        )
        family = (
            archive_families[index % len(archive_families)]
            if index % 2 == 0
            else variants[index % len(variants)]
        )
        return f"tenant-east/2026_{month}/{family}/object-{index:06d}"

    @staticmethod
    def _active_neighbor_variant(index: int) -> str:
        families = (
            "exports-2026",
            "exportsA2026",
            "exports.2026",
            "exports/2026",
            "exportsX2026",
            "ingest-2026",
            "ingestA2026",
            "ingest.2026",
            "ingest/2026",
            "reports-2026",
            "reportsA2026",
            "reports.2026",
            "reports/2026",
            "snapshots-2026",
            "manifestsA2026",
            "archive.2026",
            "staging/2026",
            "analyticsX2026",
        )
        return families[index % len(families)]

    def _load_requests(self, env) -> None:
        rows = self._request_rows()
        if len(rows) != self.request_count:
            raise RuntimeError(
                "QP07 request fixture row declaration mismatch: "
                f"declared={self.request_count}, generated={len(rows)}"
            )
        self._insert_batches(
            env,
            self.request_table,
            (
                "request_id",
                "bucket_id",
                "path_prefix",
                "path_fragment",
                "path_suffix",
                "search_mode",
                "object_kind",
                "visibility",
                "min_object_size",
                "max_object_size",
                "include_deleted",
                "request_name",
                "active",
            ),
            rows,
            "load QP07 requests",
        )

    def _load_bindings(self, env) -> None:
        rows = tuple(
            (
                request_id,
                bucket_id,
                self._escape_like(path_prefix),
                path_prefix,
                self._prefix_upper_bound(path_prefix),
                "compiled_prefix_v2",
            )
            for request_id, bucket_id, path_prefix, path_fragment, path_suffix, search_mode, *_ in self._request_rows()
            if search_mode == "literal_prefix"
        )
        if len(rows) != self.binding_count:
            raise RuntimeError(
                "QP07 binding fixture row declaration mismatch: "
                f"declared={self.binding_count}, generated={len(rows)}"
            )
        self._insert_batches(
            env,
            self.binding_table,
            ("request_id", "bucket_id", "compiled_prefix", "lower_key", "upper_key", "bind_status"),
            rows,
            "load QP07 bindings",
        )

    def _load_contracts(self, env) -> None:
        rows = []
        seen = set()
        for fragment, suffix, _ in _LITERAL_ROUTE_TEMPLATES:
            key = ("literal_prefix", fragment, suffix)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                (
                    len(rows) + 1,
                    "literal_prefix",
                    fragment,
                    self._prefix_upper_bound(fragment),
                    suffix,
                    "literal_directory" if suffix == "%" else "literal_object_prefix",
                    "customer_live",
                    "serving",
                    len(rows) + 1,
                    0,
                    1000000000,
                    "us-east-1",
                    "hot",
                    "active",
                    202608,
                    0,
                    1,
                )
            )
        for request_id, _, _, fragment, suffix, search_mode, *_ in self._request_rows():
            if search_mode != "like_pattern":
                continue
            key = (search_mode, fragment, suffix)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                (
                    len(rows) + 1,
                    search_mode,
                    fragment,
                    self._prefix_upper_bound(fragment),
                    suffix,
                    "wildcard_pattern",
                    "customer_live",
                    "serving",
                    len(rows) + 1,
                    0,
                    1000000000,
                    "us-east-1",
                    "hot",
                    "active",
                    202608,
                    0,
                    1,
                )
            )
        self._insert_batches(
            env,
            self.contract_table,
            (
                "contract_id",
                "search_mode",
                "route_token",
                "route_upper_bound",
                "tail_token",
                "route_shape",
                "access_lane",
                "route_status",
                "route_priority",
                "min_object_size",
                "max_object_size",
                "region_scope",
                "storage_tier",
                "lifecycle_state",
                "min_retention_epoch",
                "legal_hold_required",
                "active",
            ),
            rows,
            "load QP07 route contracts",
        )

    def _request_rows(self) -> tuple[tuple, ...]:
        return (
            (7001, self.bucket_id, "tenant-east/2026_08/", "exports_2026/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "target-export-prefix", 1),
            (7002, self.bucket_id, "tenant-east/2026_%/", "exports_%/", "%", "like_pattern", "file", "customer", 4096, 8192, 0, "all-month-exports", 1),
            (7003, self.bucket_id, "tenant-east/2026_07/", "exports_2026/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "adjacent-month-july", 1),
            (7004, self.bucket_id, "tenant-east/2026_09/", "exports_2026/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "adjacent-month-september", 1),
            (7005, self.bucket_id, "tenant-east/2026_08/", "ingest_2026/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "same-month-ingest", 1),
            (7006, self.bucket_id, "tenant-east/2026_08/", "reports_2026/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "same-month-reports", 1),
            (7007, self.bucket_id, "tenant-east/2026_08/", "exports_2026/", "object-00%", "literal_prefix", "file", "customer", 4096, 8192, 0, "target-object-subprefix", 1),
            (7008, self.bucket_id, "tenant-east/2026_%/", "ingest_%/", "%", "like_pattern", "file", "customer", 4096, 8192, 0, "all-month-ingest", 1),
            (7009, self.bucket_id, "tenant-east/2026_08/", "snapshots_2026/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "same-month-snapshots", 1),
            (7010, self.bucket_id, "tenant-east/2026_08/", "manifests_2026/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "same-month-manifests", 1),
            (7011, self.bucket_id, "tenant-east/2026_08/", "archive_2026/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "same-month-archive", 1),
            (7012, "bucket02", "tenant-east/2026_08/", "exports_2026/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "other-bucket-exports", 1),
            (7013, self.bucket_id, "tenant-east/2026_08/", "exports_2026/", "object-000%", "literal_prefix", "file", "customer", 4096, 8192, 0, "target-first-object", 1),
            (7014, self.bucket_id, "tenant-east/2026_08/", "exports_%/", "%", "like_pattern", "file", "customer", 4096, 8192, 0, "export-family-pattern", 1),
            (7015, self.bucket_id, "tenant-east/2026_%/", "reports_%/", "%", "like_pattern", "file", "customer", 4096, 8192, 0, "all-month-reports", 1),
            (7016, self.bucket_id, "tenant-east/2026_08/", "staging_2026/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "same-month-staging", 1),
            (7017, self.bucket_id, "tenant-east/2026_08/", "analytics_2026/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "same-month-analytics", 1),
            (7018, self.bucket_id, "tenant-east/2026_08/", "exports_2026_archive/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "same-month-export-archive", 1),
            (7019, self.bucket_id, "tenant-east/2026_08/", "billing%_2026/", "%", "literal_prefix", "file", "customer", 4096, 8192, 0, "billing-percent-literal", 1),
        )

    def _create_views(self, env) -> None:
        self._create_builder_view(env)
        self._create_route_view(env)
        self._create_fault_suffix_view(env)
        self._create_search_view(env)

    def _create_builder_view(self, env) -> None:
        self._execute(
            env,
            f"CREATE OR REPLACE VIEW {self.db}.{self.builder_view} AS "
            f"SELECT r.request_id, r.bucket_id, r.path_prefix, r.path_fragment, r.path_suffix, r.search_mode, "
            f"r.object_kind, r.visibility, r.min_object_size, r.max_object_size, r.include_deleted, "
            f"r.request_name, r.active, "
            f"CASE WHEN r.search_mode = 'literal_prefix' THEN b.compiled_prefix ELSE r.path_prefix END AS compiled_prefix, "
            f"b.lower_key, b.upper_key "
            f"FROM {self.db}.{self.request_table} AS r "
            f"LEFT JOIN {self.db}.{self.binding_table} AS b "
            "ON b.request_id = r.request_id AND b.bucket_id = r.bucket_id "
            "WHERE r.active = 1",
            "create QP07 unified query builder",
        )

    def _create_route_view(self, env) -> None:
        self._execute(
            env,
            f"CREATE OR REPLACE VIEW {self.db}.{self.route_view} AS "
            f"SELECT q.request_id, q.bucket_id, q.path_prefix, q.path_fragment, q.path_suffix, q.search_mode, "
            f"q.object_kind, q.visibility, q.min_object_size, q.max_object_size, q.include_deleted, "
            f"q.request_name, q.active, q.compiled_prefix, q.lower_key, q.upper_key, "
            "CASE WHEN q.search_mode = 'literal_prefix' AND q.path_suffix = '%' "
            "THEN 'literal_directory' "
            "WHEN q.search_mode = 'literal_prefix' THEN 'literal_object_prefix' "
            "ELSE 'wildcard_pattern' END AS route_shape, "
            "CASE WHEN q.visibility = 'customer' AND q.include_deleted = 0 "
            "THEN 'customer_live' "
            "WHEN q.visibility = 'customer' AND q.include_deleted = 1 THEN 'customer_with_deleted' "
            "ELSE CONCAT(q.visibility, '_scope') END AS access_lane, "
            "CASE WHEN q.path_prefix LIKE 'tenant-east/2026_%/' THEN 'tenant_calendar' "
            "ELSE 'other_namespace' END AS namespace_class, "
            "CASE WHEN q.search_mode = 'literal_prefix' THEN 'literal_route' "
            "ELSE 'pattern_route' END AS route_contract, "
            "CASE WHEN q.search_mode = 'literal_prefix' AND q.path_suffix = '%' "
            "THEN 'directory_tail' "
            "WHEN q.search_mode = 'literal_prefix' THEN 'object_prefix_tail' "
            "ELSE 'pattern_tail' END AS tail_policy, "
            "CASE WHEN q.request_name LIKE 'target-%' THEN 'target_lane' "
            "WHEN q.request_name LIKE 'adjacent-%' THEN 'neighbor_lane' "
            "WHEN q.request_name LIKE 'same-%' THEN 'same_namespace_lane' "
            "WHEN q.request_name LIKE 'billing-%' THEN 'billing_lane' "
            "WHEN q.request_name LIKE 'other-%' THEN 'cross_bucket_lane' "
            "ELSE 'pattern_lane' END AS request_lane "
            f"FROM {self.db}.{self.builder_view} AS q "
            "WHERE q.active = 1",
            "create QP07 request route context",
        )

    def _create_fault_suffix_view(self, env) -> None:
        self._execute(
            env,
            f"CREATE OR REPLACE VIEW {self.db}.{self.suffix_view} AS "
            f"SELECT q.request_id, q.bucket_id, q.path_prefix, q.path_fragment, q.path_suffix, q.search_mode, "
            f"q.object_kind, q.visibility, q.min_object_size, q.max_object_size, q.include_deleted, "
            f"q.request_name, q.active, q.compiled_prefix, q.lower_key, q.upper_key, "
            "q.route_shape, q.access_lane, q.namespace_class, q.route_contract, q.tail_policy, q.request_lane, "
            "c.contract_id, c.route_status AS contract_status, c.route_priority AS contract_priority, "
            "c.route_upper_bound AS contract_route_upper, "
            "c.min_object_size AS contract_min_size, c.max_object_size AS contract_max_size, "
            "c.region_scope AS contract_region, c.storage_tier AS contract_storage_tier, "
            "c.lifecycle_state AS contract_lifecycle, c.min_retention_epoch AS contract_min_retention, "
            "c.legal_hold_required AS contract_legal_hold, "
            "CASE "
            "WHEN q.search_mode = 'literal_prefix' AND LOCATE('%', q.path_fragment) > 0 "
            "AND LOCATE('_', q.path_fragment) > 0 THEN 'mixed_metachar_route' "
            "WHEN q.search_mode = 'literal_prefix' AND LOCATE('_', q.path_fragment) > 0 THEN 'underscore_route' "
            "WHEN q.search_mode = 'literal_prefix' AND LOCATE('%', q.path_fragment) > 0 THEN 'percent_route' "
            "ELSE 'pattern_route' END AS fragment_class, "
            "CASE WHEN q.path_suffix = '%' THEN 'open_tail' "
            "WHEN RIGHT(q.path_suffix, 1) = '%' THEN 'filtered_tail' "
            "ELSE 'closed_tail' END AS suffix_class "
            f"FROM {self.db}.{self.route_view} AS q "
            f"JOIN {self.db}.{self.contract_table} AS c "
            "ON c.search_mode = q.search_mode "
            "AND c.route_token = q.path_fragment "
            "AND c.tail_token = q.path_suffix "
            "AND c.route_shape = q.route_shape "
            "AND c.access_lane = q.access_lane "
            "AND c.active = 1 "
            "AND c.min_object_size <= q.min_object_size "
            "AND c.max_object_size >= q.max_object_size "
            "WHERE q.active = 1 AND q.min_object_size <= q.max_object_size",
            "create QP07 suffix template input",
        )

    def _create_search_view(self, env) -> None:
        literal_branches = "\nUNION ALL\n".join(
            self._literal_route_branch(fragment, suffix, literal_tail)
            for fragment, suffix, literal_tail in _LITERAL_ROUTE_TEMPLATES
        )
        wildcard_branch = self._wildcard_route_branch()
        self._execute(
            env,
            f"CREATE OR REPLACE VIEW {self.db}.{self.view} AS "
            "SELECT DISTINCT matched.request_id, matched.bucket_id, matched.path_prefix, "
            "matched.path_fragment, matched.path_suffix, matched.search_mode, matched.path, "
            "matched.object_id, matched.object_size, matched.payload "
            "FROM (\n"
            f"{literal_branches}\nUNION ALL\n{wildcard_branch}\n"
            ") AS matched "
            "WHERE matched.path IS NOT NULL "
            "AND matched.object_id > 0 "
            "AND matched.payload <> '' "
            "AND matched.search_mode IN ('literal_prefix', 'like_pattern')",
            "create QP07 static-template search view",
        )

    def _literal_route_branch(self, fragment: str, suffix: str, literal_tail: str) -> str:
        route_shape = "literal_directory" if suffix == "%" else "literal_object_prefix"
        return (
            "SELECT q.request_id, q.bucket_id, q.path_prefix, q.path_fragment, q.path_suffix, q.search_mode, "
            "o.path, o.object_id, o.object_size, o.payload "
            f"FROM {self.db}.{self.suffix_view} AS q "
            f"JOIN {self.db}.{self.catalog_table} AS o "
            "ON o.bucket_id = q.bucket_id "
            "AND o.region_code = q.contract_region "
            "AND o.storage_tier = q.contract_storage_tier "
            "AND o.lifecycle_state = q.contract_lifecycle "
            "AND o.retention_epoch >= q.contract_min_retention "
            "AND o.legal_hold = q.contract_legal_hold "
            f"AND q.route_shape = {self._literal(route_shape)} "
            "AND q.access_lane = 'customer_live' "
            "AND q.namespace_class = 'tenant_calendar' "
            "AND o.object_kind = q.object_kind "
            "AND o.visibility = q.visibility "
            "AND o.object_size BETWEEN q.min_object_size AND q.max_object_size "
            "AND o.object_size BETWEEN GREATEST(q.min_object_size, q.contract_min_size) "
            "AND LEAST(q.max_object_size, q.contract_max_size) "
            "AND o.object_size - q.min_object_size >= 0 "
            "AND q.max_object_size - o.object_size >= 0 "
            "AND o.object_id > 0 "
            "AND o.object_id <= q.max_object_size * 1000000 "
            "AND o.path IS NOT NULL "
            "AND CHAR_LENGTH(o.path) >= CHAR_LENGTH(q.path_prefix) "
            "AND CHAR_LENGTH(o.path) <= 255 "
            "AND LEFT(o.path, CHAR_LENGTH(q.path_prefix)) = q.path_prefix "
            "AND LOCATE('/', o.path, CHAR_LENGTH(q.path_prefix) + 1) > CHAR_LENGTH(q.path_prefix) "
            "AND LOCATE('/object-', o.path, CHAR_LENGTH(q.path_prefix)) > CHAR_LENGTH(q.path_prefix) "
            "AND SUBSTRING_INDEX(SUBSTRING_INDEX(o.path, '/', 3), '/', -1) = SUBSTRING_INDEX(q.path_fragment, '/', 1) "
            "AND o.path REGEXP '^tenant-east/2026_[0-9]{2}/.+/object-[0-9]+$' "
            "AND RIGHT(o.path, 1) <> '/' "
            "AND CHAR_LENGTH(o.payload) BETWEEN 1 AND 128 "
            "AND LEFT(o.payload, 6) IN ('target', 'live-n') "
            "AND LOCATE('-', o.payload) > 0 "
            "AND o.payload NOT REGEXP '(deleted|tombstone|placeholder)' "
            "AND COALESCE(o.payload, '') <> '' "
            "AND (q.include_deleted = 1 OR (q.include_deleted = 0 AND o.deleted = 0)) "
            "AND COALESCE(o.deleted, 0) IN (0, 1) "
            "AND CASE "
            "WHEN q.visibility = 'customer' AND q.include_deleted = 0 THEN o.deleted = 0 "
            "WHEN q.visibility = 'customer' AND q.include_deleted = 1 THEN o.deleted IN (0, 1) "
            "WHEN q.visibility = 'internal' THEN o.visibility = q.visibility "
            "ELSE o.visibility = q.visibility END "
            "AND q.contract_route_upper <> '' "
            "AND q.contract_priority BETWEEN 1 AND 64 "
            "AND q.contract_region IN ('us-east-1', 'eu-west-1', 'us-west-2') "
            "AND q.contract_storage_tier IN ('hot', 'warm', 'cold') "
            "AND q.contract_lifecycle IN ('active', 'archived') "
            "AND q.contract_min_retention BETWEEN 202000 AND 203000 "
            "AND q.contract_legal_hold IN (0, 1) "
            "AND q.lower_key < q.upper_key "
            "AND q.contract_route_upper > q.path_fragment "
            "AND q.contract_route_upper <> q.path_fragment "
            "AND CHAR_LENGTH(q.path_fragment) BETWEEN 1 AND 255 "
            "AND CHAR_LENGTH(q.path_suffix) BETWEEN 1 AND 255 "
            "AND RIGHT(q.path_fragment, 1) = '/' "
            "AND (q.path_suffix = '%' OR RIGHT(q.path_suffix, 1) = '%') "
            "AND LEFT(q.path_prefix, 7) = 'tenant-' "
            "AND CHAR_LENGTH(o.path) - CHAR_LENGTH(REPLACE(o.path, '/', '')) BETWEEN 3 AND 5 "
            "AND LOCATE('-', q.request_name) > 0 "
            "AND SUBSTRING(o.path, CHAR_LENGTH(q.path_prefix) + 1, CHAR_LENGTH(q.path_fragment)) = q.path_fragment "
            "AND SUBSTRING_INDEX(o.path, '/', 3) = CONCAT(SUBSTRING_INDEX(q.path_prefix, '/', 2), '/', SUBSTRING_INDEX(q.path_fragment, '/', 1)) "
            "AND CHAR_LENGTH(o.payload) + CHAR_LENGTH(q.request_name) <= 224 "
            "AND COALESCE(NULLIF(TRIM(o.payload), ''), 'missing') <> 'missing' "
            "AND SUBSTRING_INDEX(o.payload, '-', 1) IN ('target', 'live') "
            "AND (q.contract_status = 'serving' OR q.contract_status = 'shadow') "
            "AND o.path LIKE CONCAT(q.compiled_prefix, "
            f"{self._literal(literal_tail)}"
            ") "
            "WHERE q.active = 1 "
            "AND q.search_mode = 'literal_prefix' "
            f"AND q.path_fragment = {self._literal(fragment)} "
            f"AND q.path_suffix = {self._literal(suffix)} "
            "AND q.route_contract = 'literal_route' "
            "AND q.tail_policy IN ('directory_tail', 'object_prefix_tail') "
            "AND q.suffix_class IN ('open_tail', 'filtered_tail') "
            "AND q.fragment_class IN ('underscore_route', 'mixed_metachar_route', 'percent_route') "
            "AND q.request_lane IN ('target_lane', 'neighbor_lane', 'same_namespace_lane', 'billing_lane', 'cross_bucket_lane') "
            "AND q.contract_status = 'serving' "
            "AND q.contract_priority = q.contract_id "
            "AND q.contract_min_size <= q.min_object_size "
            "AND q.contract_max_size >= q.max_object_size "
            "AND q.min_object_size <= q.max_object_size "
            "AND CHAR_LENGTH(q.request_name) BETWEEN 1 AND 96 "
            "AND q.path_prefix <> '' AND q.path_fragment <> '' AND q.path_suffix <> '' "
            "AND EXISTS ("
            f"SELECT 1 FROM {self.db}.{self.request_table} AS eligibility "
            "WHERE eligibility.request_id = q.request_id "
            "AND eligibility.active = q.active "
            "AND eligibility.bucket_id = q.bucket_id "
            "AND eligibility.search_mode = q.search_mode "
            "AND eligibility.request_name = q.request_name "
            "AND eligibility.include_deleted = q.include_deleted "
            "AND eligibility.min_object_size <= q.min_object_size "
            "AND eligibility.max_object_size >= q.max_object_size"
            ") "
            "AND EXISTS ("
            f"SELECT 1 FROM {self.db}.{self.request_table} AS policy "
            "WHERE policy.request_id = q.request_id "
            "AND policy.active = 1 "
            "AND policy.bucket_id = o.bucket_id "
            "AND policy.object_kind = o.object_kind "
            "AND policy.visibility = o.visibility "
            "AND policy.search_mode = q.search_mode "
            "AND policy.path_fragment = q.path_fragment "
            "AND policy.path_suffix = q.path_suffix "
            "AND policy.request_name = q.request_name "
            "AND policy.min_object_size <= o.object_size "
            "AND policy.max_object_size >= o.object_size"
            ") "
            "AND NOT EXISTS ("
            f"SELECT 1 FROM {self.db}.{self.request_table} AS revoked "
            "WHERE revoked.request_id = q.request_id "
            "AND revoked.active = 0 "
            "AND revoked.request_name = q.request_name"
            ")"
        )

    def _wildcard_route_branch(self) -> str:
        return (
            "SELECT q.request_id, q.bucket_id, q.path_prefix, q.path_fragment, q.path_suffix, q.search_mode, "
            "o.path, o.object_id, o.object_size, o.payload "
            f"FROM {self.db}.{self.suffix_view} AS q "
            f"JOIN {self.db}.{self.catalog_table} AS o "
            "ON o.bucket_id = q.bucket_id "
            "AND o.region_code = q.contract_region "
            "AND o.storage_tier = q.contract_storage_tier "
            "AND o.lifecycle_state = q.contract_lifecycle "
            "AND o.retention_epoch >= q.contract_min_retention "
            "AND o.legal_hold = q.contract_legal_hold "
            "AND o.path LIKE CONCAT(q.path_prefix, q.path_fragment, q.path_suffix) "
            "AND q.route_shape = 'wildcard_pattern' "
            "AND q.access_lane = 'customer_live' "
            "AND q.namespace_class = 'tenant_calendar' "
            "AND q.route_contract = 'pattern_route' "
            "AND q.tail_policy = 'pattern_tail' "
            "AND q.fragment_class = 'pattern_route' "
            "AND q.request_lane = 'pattern_lane' "
            "AND q.contract_status = 'serving' "
            "AND q.contract_priority = q.contract_id "
            "AND q.contract_region IN ('us-east-1', 'eu-west-1', 'us-west-2') "
            "AND q.contract_storage_tier IN ('hot', 'warm', 'cold') "
            "AND q.contract_lifecycle IN ('active', 'archived') "
            "AND q.contract_min_retention BETWEEN 202000 AND 203000 "
            "AND q.contract_legal_hold IN (0, 1) "
            "AND q.contract_route_upper <> '' "
            "AND o.object_kind = q.object_kind "
            "AND o.visibility = q.visibility "
            "AND o.object_size BETWEEN q.min_object_size AND q.max_object_size "
            "AND o.object_size BETWEEN GREATEST(q.min_object_size, q.contract_min_size) "
            "AND LEAST(q.max_object_size, q.contract_max_size) "
            "AND CHAR_LENGTH(q.request_name) BETWEEN 1 AND 96 "
            "AND q.path_prefix <> '' AND q.path_fragment <> '' AND q.path_suffix <> '' "
            "AND o.object_size - q.min_object_size >= 0 "
            "AND q.max_object_size - o.object_size >= 0 "
            "AND o.object_id > 0 "
            "AND o.object_id <= q.max_object_size * 1000000 "
            "AND o.path IS NOT NULL "
            "AND CHAR_LENGTH(o.path) >= CHAR_LENGTH(q.path_prefix) "
            "AND CHAR_LENGTH(o.path) <= 255 "
            "AND LOCATE('/', o.path, CHAR_LENGTH(q.path_prefix) + 1) > CHAR_LENGTH(q.path_prefix) "
            "AND LOCATE('/object-', o.path) > 0 "
            "AND o.path REGEXP '^tenant-east/2026_[0-9]{2}/.+/object-[0-9]+$' "
            "AND RIGHT(o.path, 1) <> '/' "
            "AND CHAR_LENGTH(o.payload) BETWEEN 1 AND 128 "
            "AND LEFT(o.payload, 6) IN ('target', 'live-n') "
            "AND LOCATE('-', o.payload) > 0 "
            "AND o.payload NOT REGEXP '(deleted|tombstone|placeholder)' "
            "AND COALESCE(o.payload, '') <> '' "
            "AND (q.include_deleted = 1 OR (q.include_deleted = 0 AND o.deleted = 0)) "
            "AND COALESCE(o.deleted, 0) IN (0, 1) "
            "AND CASE "
            "WHEN q.visibility = 'customer' AND q.include_deleted = 0 THEN o.deleted = 0 "
            "WHEN q.visibility = 'customer' AND q.include_deleted = 1 THEN o.deleted IN (0, 1) "
            "WHEN q.visibility = 'internal' THEN o.visibility = q.visibility "
            "ELSE o.visibility = q.visibility END "
            "AND CHAR_LENGTH(q.path_fragment) BETWEEN 1 AND 255 "
            "AND CHAR_LENGTH(q.path_suffix) BETWEEN 1 AND 255 "
            "AND LEFT(q.path_prefix, 7) = 'tenant-' "
            "AND LOCATE('-', q.request_name) > 0 "
            "AND CHAR_LENGTH(o.payload) + CHAR_LENGTH(q.request_name) <= 224 "
            "WHERE q.active = 1 "
            "AND q.search_mode = 'like_pattern' "
            "AND q.min_object_size <= q.max_object_size "
            "AND EXISTS ("
            f"SELECT 1 FROM {self.db}.{self.request_table} AS eligibility "
            "WHERE eligibility.request_id = q.request_id "
            "AND eligibility.active = q.active "
            "AND eligibility.bucket_id = q.bucket_id "
            "AND eligibility.search_mode = q.search_mode "
            "AND eligibility.request_name = q.request_name "
            "AND eligibility.include_deleted = q.include_deleted "
            "AND eligibility.min_object_size <= q.min_object_size "
            "AND eligibility.max_object_size >= q.max_object_size"
            ") "
            "AND EXISTS ("
            f"SELECT 1 FROM {self.db}.{self.request_table} AS policy "
            "WHERE policy.request_id = q.request_id "
            "AND policy.active = 1 "
            "AND policy.bucket_id = o.bucket_id "
            "AND policy.object_kind = o.object_kind "
            "AND policy.visibility = o.visibility "
            "AND policy.search_mode = q.search_mode "
            "AND policy.path_fragment = q.path_fragment "
            "AND policy.path_suffix = q.path_suffix "
            "AND policy.request_name = q.request_name "
            "AND policy.min_object_size <= o.object_size "
            "AND policy.max_object_size >= o.object_size"
            ") "
            "AND NOT EXISTS ("
            f"SELECT 1 FROM {self.db}.{self.request_table} AS revoked "
            "WHERE revoked.request_id = q.request_id "
            "AND revoked.active = 0 "
            "AND revoked.request_name = q.request_name"
            ")"
        )

    def _verify_fault_state(self, env) -> None:
        catalog_crc = self._crc(env, self.catalog_crc_sql, "verify QP07 catalog CRC")
        if int(catalog_crc[0]) != self.row_count:
            raise RuntimeError(
                "QP07 catalog row count mismatch: "
                f"expected={self.row_count}, observed={catalog_crc!r}"
            )
        request_crc = self._crc(env, self.request_crc_sql, "verify QP07 request CRC")
        if int(request_crc[0]) != self.request_count:
            raise RuntimeError(
                "QP07 request row count mismatch: "
                f"expected={self.request_count}, observed={request_crc!r}"
            )
        binding_crc = self._crc(env, self.binding_crc_sql, "verify QP07 binding CRC")
        if int(binding_crc[0]) != self.binding_count:
            raise RuntimeError(
                "QP07 binding row count mismatch: "
                f"expected={self.binding_count}, observed={binding_crc!r}"
            )
        builder_sql = self._view_definition(env, self.builder_view).casefold()
        route_sql = self._view_definition(env, self.route_view).casefold()
        suffix_sql = self._view_definition(env, self.suffix_view).casefold()
        search_sql = self._view_definition(env, self.view).casefold()
        search_sql_normalized = re.sub(r"[`\s]", "", search_sql).replace("_utf8mb4", "")
        required_fragments = {
            "builder binding dependency": self.binding_table.casefold(),
            "builder mode branch": "search_mode",
            "builder compiled output": "compiled_prefix",
            "suffix route dependency": self.route_view.casefold(),
            "route builder dependency": self.builder_view.casefold(),
            "route contract": "route_contract",
            "route tail policy": "tail_policy",
            "route request lane": "request_lane",
            "suffix route shape": "route_shape",
            "suffix access lane": "access_lane",
            "suffix namespace class": "namespace_class",
            "search suffix dependency": self.suffix_view.casefold(),
            "fault compiled prefix join": "concat(",
            "fault compiled prefix operand": "compiled_prefix",
            "fault namespace range lower": "lower_key",
            "fault namespace range upper": "upper_key",
            "fault target static literal": "'exports_2026/%'",
            "fault static route literals": "'ingest_2026/%'",
            "wildcard compiled join": "concat(q.path_prefix,q.path_fragment,q.path_suffix)",
            "search object predicates": "object_kind",
            "search path-shape predicate": "substring_index",
            "search payload predicate": "char_length(o.payload)",
            "search path qualification": "o.pathregexp",
            "search payload qualification": "left(o.payload,6)",
            "search visibility case": "case",
            "search region policy": "region_code",
            "search lifecycle policy": "lifecycle_state",
            "search retention policy": "retention_epoch",
            "search policy predicate": "exists(",
            "search policy revocation predicate": "notexists(",
            "search deduplication": "selectdistinctmatched.request_id",
        }
        combined = {
            "builder binding dependency": builder_sql,
            "builder mode branch": builder_sql,
            "builder compiled output": builder_sql,
            "suffix route dependency": suffix_sql,
            "route builder dependency": route_sql,
            "route contract": route_sql,
            "route tail policy": route_sql,
            "route request lane": route_sql,
            "suffix route shape": suffix_sql,
            "suffix access lane": suffix_sql,
            "suffix namespace class": suffix_sql,
            "search suffix dependency": search_sql,
            "fault compiled prefix join": search_sql_normalized,
            "fault compiled prefix operand": search_sql_normalized,
            "fault namespace range lower": search_sql_normalized,
            "fault namespace range upper": search_sql_normalized,
            "fault target static literal": search_sql_normalized,
            "fault static route literals": search_sql,
            "wildcard compiled join": search_sql_normalized,
            "search object predicates": search_sql,
            "search path-shape predicate": search_sql_normalized,
            "search payload predicate": search_sql_normalized,
            "search path qualification": search_sql_normalized,
            "search payload qualification": search_sql_normalized,
            "search visibility case": search_sql_normalized,
            "search region policy": search_sql_normalized,
            "search lifecycle policy": search_sql_normalized,
            "search retention policy": search_sql_normalized,
            "search policy predicate": search_sql_normalized,
            "search policy revocation predicate": search_sql_normalized,
            "search deduplication": search_sql_normalized,
        }
        missing = {
            name: fragment
            for name, fragment in required_fragments.items()
            if fragment not in combined[name]
        }
        if missing:
            raise RuntimeError(
                "QP07 fault view chain does not contain the expected static-literal regression: "
                f"missing={missing!r}, builder={builder_sql!r}, route={route_sql!r}, suffix={suffix_sql!r}, search={search_sql!r}"
            )
        target = self._payload(env, self.fault_fingerprint_sql, "verify QP07 faulty target result")
        truth = self._payload(env, self.literal_truth_sql, "verify QP07 literal business truth")
        mismatch = query_result_truth_mismatch(
            capture_query_result_truth(truth, ordered=True),
            target["columns"],
            target["result"],
        )
        if mismatch is not None:
            raise RuntimeError(
                "QP07 faulty target result changed business truth: "
                f"mismatch={mismatch!r}, target={target!r}, truth={truth!r}"
            )
        target_request = self._target_request(env)
        expected_request = (
            self.bucket_id,
            self.target_path_prefix,
            self.target_path_fragment,
            self.target_path_suffix,
            "literal_prefix",
            self.target_object_kind,
            self.target_visibility,
            self.target_min_object_size,
            self.target_max_object_size,
            self.target_include_deleted,
        )
        if target_request != expected_request:
            raise RuntimeError(
                "QP07 target request metadata mismatch: "
                f"expected={expected_request!r}, observed={target_request!r}"
            )
        wildcard = self._payload(
            env,
            "SELECT COUNT(*), COALESCE(SUM(object_id), 0), "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', path, object_id, object_size, payload))), 0) "
            f"FROM {self.db}.{self.view} WHERE request_id = {self.wildcard_request_id}",
            "verify QP07 wildcard result",
        )
        wildcard_truth = self._payload(env, self.wildcard_truth_sql, "verify QP07 wildcard truth")
        if wildcard["result"] != wildcard_truth["result"]:
            raise RuntimeError(
                "QP07 wildcard request changed unexpectedly: "
                f"expected={wildcard_truth['result']!r}, observed={wildcard['result']!r}"
            )

    def _target_request(self, env) -> tuple:
        rows = execute_result_rows(
            env.execute_sql,
            "SELECT bucket_id, path_prefix, path_fragment, path_suffix, search_mode, object_kind, visibility, "
            "min_object_size, max_object_size, include_deleted "
            f"FROM {self.db}.{self.request_table} WHERE request_id = {self.target_request_id}",
            "read QP07 target request metadata",
        )
        if len(rows) != 1:
            raise RuntimeError(
                "QP07 target request metadata must contain exactly one row: "
                f"request_id={self.target_request_id}, rows={rows!r}"
            )
        return tuple(rows[0])

    @staticmethod
    def _escape_like(value: str) -> str:
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    @staticmethod
    def _prefix_upper_bound(prefix: str) -> str:
        for index in range(len(prefix) - 1, -1, -1):
            codepoint = ord(prefix[index])
            if codepoint < 0xFF:
                return prefix[:index] + chr(codepoint + 1)
        raise ValueError(f"QP07 literal range has no representable upper bound: prefix={prefix!r}")

    def _insert_batches(self, env, table: str, columns: tuple[str, ...], rows: list[tuple], context: str) -> None:
        batch_size = 8000
        column_sql = ", ".join(columns)
        for start in range(0, len(rows), batch_size):
            batch = rows[start : start + batch_size]
            values = ", ".join(
                "(" + ", ".join(self._literal(value) for value in row) + ")"
                for row in batch
            )
            self._execute(
                env,
                f"INSERT INTO {self.db}.{table} ({column_sql}) VALUES {values}",
                f"{context} rows {start}-{start + len(batch) - 1}",
            )

    def _metric(self, env, metric_type: str) -> dict:
        return require_success_payload(
            parse_json_object(
                env.observe_metric(metric_type),
                f"capture QP07 metric {metric_type}",
            ),
            f"capture QP07 metric {metric_type}",
        )

    def _crc(self, env, sql: str, context: str) -> tuple:
        rows = execute_result_rows(env.execute_sql, sql, context)
        if len(rows) != 1:
            raise RuntimeError(f"{context} expected one row: sql={sql!r}, rows={rows!r}")
        return tuple(rows[0])

    def _view_definition(self, env, view: str) -> str:
        # SHOW CREATE VIEW definitions for this scenario exceed the agent-facing
        # 2048-char result clamp; fixture verification needs the full definition.
        rows = execute_result_rows(
            env.execute_sql_trusted,
            f"SHOW CREATE VIEW {self.db}.{view}",
            f"read QP07 view definition {view}",
        )
        if len(rows) != 1 or len(rows[0]) < 2:
            raise RuntimeError(
                "QP07 SHOW CREATE VIEW returned an invalid result: "
                f"view={view!r}, rows={rows!r}"
            )
        return str(rows[0][1])

    def _payload(self, env, sql: str, context: str) -> dict:
        return require_success_payload(parse_json_object(env.execute_sql(sql), context), context)

    def _execute(self, env, sql: str, context: str) -> dict:
        return self._payload(env, sql, f"{context}: sql={sql!r}")

    @staticmethod
    def _literal(value: object) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, int):
            return str(value)
        return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"
