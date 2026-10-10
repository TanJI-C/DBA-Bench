from collections.abc import Mapping
from dataclasses import dataclass, replace
import re
import time
from urllib.error import HTTPError

from src.database.sql import require_result_rows
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    require_sql_success,
    validate_sql_identifier,
)

from src.scenarios.workloads import WorkloadProfile
from src.scenarios.evaluation.tidb.business_change.timezone_ddl_backpressure import (
    TidbBusinessChangeTimezoneDdlBackpressureEvaluatorCase,
    TidbBusinessChangeTimezoneDdlReducedBackpressureEvaluatorCase,
)

from ...base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    TiDBReplicationRuntime,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import MYSQL_8_4, TICDC_V8_1_0, TIDB_V8_1_0, tidb_runtime


SCENARIO_ID = "tidb_business_change_timezone_ddl_backpressure"
SOURCE_DB = "benchops"
SOURCE_TABLE = "cf01_events"
ARCHIVE_TABLE = "cf01_archive_events"
CHANGEFEED_ID = "dr-cutover"
DDL_TABLE = "cf01_order_cutover"
BUSINESS_TRIGGER = "cf01_event_audit"
ARCHIVE_TRIGGER = "cf01_archive_audit"
DDL_COLUMN = "end_time"
DDL_DEFAULT_UTC = "1970-01-01 00:00:01"
DDL_DEFAULT_LOCAL = "1970-01-01 08:00:01"
SEEDED_ROWS = 64
POST_FAULT_ROWS = 32
POST_FAULT_START_ID = SEEDED_ROWS + 1
POST_FAULT_END_ID = SEEDED_ROWS + POST_FAULT_ROWS
LIVE_WRITER_ID = 100_000_000_000_000_001


TIMEZONE_DDL_KNOWLEDGE_HOPS = (
    {
        "hop_id": "H1",
        "knowledge_question": "How can checkpoint stop while resolved and a normal changefeed state continue?",
        "expected_concept": "A sink retry can hold checkpoint while resolved describes a source frontier; control-plane normal is not catch-up proof.",
        "version_scope": "TiDB/TiCDC 8.1 self-managed",
        "required_environment_binding": ("changefeed progress", "bounded TiCDC retry log", "source TSO"),
        "decision_changed": "Treat the incident as a sink-side retry and keep investigating instead of declaring the feed healthy.",
        "counterfactual": "A normal REST state is sufficient evidence that no replication work is blocked.",
        "allowed_source_scope": ("official", "version_bound_curated"),
        "visible_evidence": ("manage_cluster", "read_log", "execute_sql"),
        "query": "TiCDC checkpoint resolved sink retry normal source progress",
        "retrieval_markers": ("checkpoint", "resolved", "sink-retry"),
        "kb_type": "diagnosis",
        "component": "ticdc",
    },
    {
        "hop_id": "H2",
        "knowledge_question": "Why can the same timestamp DDL succeed upstream and fail downstream with Error 1067?",
        "expected_concept": "TIMESTAMP defaults use session time semantics, so a lower-bound literal can be valid in UTC and invalid in a +08:00 downstream session.",
        "version_scope": "TiDB 8.1 with MySQL 8.4 downstream",
        "required_environment_binding": ("DDL text", "upstream session timezone", "downstream session/global timezone"),
        "decision_changed": "Repair the downstream schema equivalently rather than changing a global timezone or blaming the cluster.",
        "counterfactual": "Identical DDL text has identical validity at both endpoints regardless of session timezone.",
        "allowed_source_scope": ("official", "version_bound_curated"),
        "visible_evidence": ("execute_sql", "read_log"),
        "query": "TiDB TIMESTAMP default session time zone Error 1067 downstream DDL",
        "retrieval_markers": ("TIMESTAMP", "session time semantics", "downstream"),
        "kb_type": "diagnosis",
        "component": "tidb",
    },
    {
        "hop_id": "H3",
        "knowledge_question": "What recovery boundary is safe after one isolated failed DDL event?",
        "expected_concept": "Repair the downstream schema, then recreate the same feed from the first TSO after the unique failed DDL CommitTs; do not use a later current TSO.",
        "version_scope": "TiCDC 8.1",
        "required_environment_binding": ("unique CommitTs from raw retry log", "same changefeed identity", "downstream schema gap"),
        "decision_changed": "Choose CommitTs + 1 for the target feed and reject an arbitrary later start point.",
        "counterfactual": "The latest observed source TSO is always a safe resume point after schema repair.",
        "allowed_source_scope": ("official", "version_bound_curated"),
        "visible_evidence": ("read_log", "manage_cluster", "execute_sql"),
        "query": "TiCDC failed DDL CommitTs recreate start after failed event recovery boundary",
        "retrieval_markers": ("failed DDL event commit timestamp", "first timestamp after"),
        "kb_type": "recovery",
        "component": "ticdc",
    },
    {
        "hop_id": "H4",
        "knowledge_question": "Why must post-DDL writes constrain the resume point?",
        "expected_concept": "Source DML committed after the failed DDL is already part of the cutover window; starting later can create a data hole even when the schema is fixed.",
        "version_scope": "TiDB/TiCDC 8.1 replication",
        "required_environment_binding": ("post-DDL row boundary", "live-writer row", "source and downstream row truth"),
        "decision_changed": "Preserve and verify all post-event rows instead of accepting a schema-only recovery.",
        "counterfactual": "Once the downstream table exists, skipped post-DDL DML is harmless.",
        "allowed_source_scope": ("official", "version_bound_curated"),
        "visible_evidence": ("execute_sql", "manage_cluster"),
        "query": "TiCDC post-DDL rows data hole later start TSO row integrity",
        "retrieval_markers": ("complete source and downstream business rows", "post-event writes"),
        "kb_type": "operation",
        "component": "shared",
    },
    {
        "hop_id": "H5",
        "knowledge_question": "Why can replication remain slow after the DDL retry is bypassed?",
        "expected_concept": "A table-bound slow write hook independently reduces downstream sink capacity; it must be identified by table, event, body, and observed latency.",
        "version_scope": "TiCDC 8.1 with MySQL-compatible sink",
        "required_environment_binding": ("all downstream triggers", "trigger table/event/body", "business versus archive latency"),
        "decision_changed": "Remove only the slow hook on the replicated business table and preserve the healthy archive path.",
        "counterfactual": "A healthy TiDB/TiKV/PD topology rules out a downstream sink bottleneck.",
        "allowed_source_scope": ("official", "version_bound_curated"),
        "visible_evidence": ("execute_sql", "query_metrics"),
        "query": "TiCDC table-bound sink latency trigger sleep healthy neighboring table",
        "retrieval_markers": ("table-bound slow write hooks", "healthy neighboring paths"),
        "kb_type": "performance",
        "component": "ticdc",
    },
    {
        "hop_id": "H6",
        "knowledge_question": "Which nearby path must remain protected while repairing sink backpressure?",
        "expected_concept": "The archive table and its audit trigger are a healthy neighboring path; their truth and trigger must remain unchanged.",
        "version_scope": "TiDB/TiCDC 8.1 self-managed",
        "required_environment_binding": ("archive table rows", "archive trigger body", "core topology health"),
        "decision_changed": "Keep the repair scoped to the business table and target changefeed rather than resetting the archive path.",
        "counterfactual": "All downstream triggers are interchangeable cleanup targets during a sink incident.",
        "allowed_source_scope": ("official", "version_bound_curated"),
        "visible_evidence": ("execute_sql", "query_metrics", "manage_cluster"),
        "query": "TiCDC healthy neighboring archive trigger preserve sink backpressure scope",
        "retrieval_markers": ("table-bound slow write hooks", "healthy neighboring paths"),
        "kb_type": "performance",
        "component": "ticdc",
    },
    {
        "hop_id": "H7",
        "knowledge_question": "What proves this recovery is complete rather than merely accepted by the control plane?",
        "expected_concept": "Closed-loop acceptance combines changefeed progress, equivalent DDL, full source/downstream rows including post-event writes, sink capacity, healthy neighbor truth, and core service health.",
        "version_scope": "TiDB/TiCDC 8.1 with MySQL 8.4 downstream",
        "required_environment_binding": ("checkpoint/resolved/source TSO", "DDL metadata", "business and archive rows", "trigger state", "PD/TiKV/TiDB health"),
        "decision_changed": "Continue verification until every public invariant holds; do not submit after one successful command.",
        "counterfactual": "A successful changefeed recreate or a temporary lag decrease alone proves recovery.",
        "allowed_source_scope": ("official", "version_bound_curated"),
        "visible_evidence": ("manage_cluster", "execute_sql", "query_metrics", "read_log"),
        "query": "TiCDC closed-loop recovery full business rows post-DDL archive neighbor core service health",
        "retrieval_markers": ("Closed-loop recovery requires", "core service health"),
        "kb_type": "operation",
        "component": "shared",
    },
)


TIMEZONE_DDL_KNOWLEDGE_CONTRACT = {
    "rationale": "Generic replication troubleshooting does not determine TiCDC progress semantics, timestamp session scope, failed-event recovery boundaries, or sink-specific safety scope.",
    "capability_targets": (
        "question_formulation",
        "semantic_extraction",
        "environment_binding",
        "operationalization",
        "verification",
    ),
    "source_contract": {
        "knowledge_base_mode": "hierarchical",
        "target_version": "TiDB/TiCDC 8.1 with MySQL 8.4 downstream",
        "allowed_source_scope": ("official", "version_bound_curated"),
        "runtime_interface": "search_knowledge",
        "agent_projection": "source-neutral serving records only",
        "private_index": False,
    },
    "hops": TIMEZONE_DDL_KNOWLEDGE_HOPS,
    "expected_failure_paths": {
        "A": "The Agent anchors on NORMAL, generic lag, or cluster health and fails before binding the timestamp DDL and failed CommitTs.",
        "B": "The Agent names the DDL or sink issue but chooses a later TSO, repairs only the schema, removes the wrong trigger, or submits without the closed-loop checks.",
    },
    "ablation": {
        "matched_conditions": ("no-KB", "unified official/version-bound KB"),
        "changed_variable": "knowledge availability only",
        "fixed_variables": ("case", "seed", "runtime", "prompt", "tool surface", "evaluator"),
        "valid_run_requirement": "environment ready, complete trace, and valid structured submission",
    },
}


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeTimezoneDdlBackpressureForDrCutoverTimezoneDdlAndSinkBackpressureScenarioCase(
    TiDBScenarioCase
):
    source_db: str
    source_table: str
    archive_table: str
    ddl_table: str
    ddl_column: str
    allowed_timestamp_defaults: tuple[str, ...]
    changefeed_id: str
    business_trigger: str
    archive_trigger: str
    seeded_rows: int
    post_fault_rows: int
    post_fault_start_id: int
    post_fault_end_id: int
    live_writer_id: int


_TIMEZONE_DDL_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="cf01_cutover_business_summary",
            sql=(
                "SELECT state, COUNT(*) AS orders, COALESCE(SUM(amount), 0) AS gross_amount "
                f"FROM {SOURCE_DB}.{SOURCE_TABLE} GROUP BY state ORDER BY state"
            ),
            qps=0.55,
            tier="OLTP_CORE",
            application_name="cutover-order-api",
        ),
        WorkloadProfile(
            name="cf01_cutover_recent_events",
            sql=(
                f"SELECT COUNT(*), MIN(id), MAX(id) FROM {SOURCE_DB}.{SOURCE_TABLE} "
                "WHERE updated_at >= NOW() - INTERVAL 1 HOUR"
            ),
            qps=0.70,
            tier="OLTP_CORE",
            application_name="cutover-order-api",
        ),
        WorkloadProfile(
            name="cf01_cutover_checksum_probe",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(id), 0), "
                f"COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', id, amount, state, note))), 0) "
                f"FROM {SOURCE_DB}.{SOURCE_TABLE}"
            ),
            qps=0.35,
            tier="REPLICATION_OBSERVABILITY",
            application_name="replication-audit",
        ),
        WorkloadProfile(
            name="cf01_cutover_schema_probe",
            sql=f"SHOW CREATE TABLE {SOURCE_DB}.{SOURCE_TABLE}",
            qps=0.45,
            tier="DDL_MAINTENANCE_OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="cf01_cutover_ddl_history_probe",
            sql="ADMIN SHOW DDL JOBS 10",
            qps=0.25,
            tier="DDL_MAINTENANCE_OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="cf01_archive_report_rollup",
            sql=(
                f"SELECT tenant_id, COUNT(*), COALESCE(SUM(amount), 0) "
                f"FROM {SOURCE_DB}.{ARCHIVE_TABLE} GROUP BY tenant_id ORDER BY tenant_id"
            ),
            qps=0.65,
            tier="OLAP_BURST",
            application_name="archive-reporting",
        ),
        WorkloadProfile(
            name="cf01_archive_report_window_scan",
            sql=(
                f"SELECT COUNT(*) FROM {SOURCE_DB}.{ARCHIVE_TABLE} "
                "WHERE updated_at >= NOW() - INTERVAL 7 DAY"
            ),
            qps=0.75,
            tier="OLAP_BURST",
            application_name="archive-reporting",
        ),
        WorkloadProfile(
            name="cf01_tso_probe",
            sql="SELECT TIDB_CURRENT_TSO(), NOW(), @@session.time_zone",
            qps=0.90,
            tier="REPLICATION_OBSERVABILITY",
            application_name="cutover-controller",
        ),
        WorkloadProfile(
            name="cf01_archive_table_status",
            sql=f"SHOW TABLE STATUS FROM {SOURCE_DB} LIKE '{ARCHIVE_TABLE}'",
            qps=0.40,
            tier="DDL_MAINTENANCE_OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="cf01_point_lookup_noise",
            sql=(
                f"SELECT id, amount, state FROM {SOURCE_DB}.{SOURCE_TABLE} "
                "WHERE id = 17"
            ),
            qps=1.10,
            tier="OLTP_CORE",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="cf01_archive_cache_probe",
            sql=f"SELECT COUNT(*) FROM {SOURCE_DB}.cf01_archive_cache_missing",
            qps=0.22,
            tier="LOG_NOISE",
            application_name="archive-cache-refresh",
        ),
        WorkloadProfile(
            name="cf01_live_order_writer",
            sql=(
                f"REPLACE INTO {SOURCE_DB}.{SOURCE_TABLE} "
                "(id, amount, state, updated_at, note) VALUES "
                f"({LIVE_WRITER_ID}, 1.00, 'paid', "
                "'2026-08-03 00:00:00', 'live-writer-stable')"
            ),
            qps=0.20,
            tier="OLTP_CORE",
            commit=True,
            application_name="cutover-order-writer",
        ),
        WorkloadProfile(
            name="cf01_archive_audit_writer",
            sql=(
                f"REPLACE INTO {SOURCE_DB}.{ARCHIVE_TABLE} "
                "(id, tenant_id, amount, updated_at, note) VALUES "
                "(80, 3, 240.00, '2026-08-03 00:00:00', 'archive-80')"
            ),
            qps=0.15,
            tier="OLTP_CORE",
            commit=True,
            application_name="archive-audit-writer",
        ),
    ),
    worker_count=6,
    seed=20260803,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=18,
)


_CASE = TidbBusinessChangeTimezoneDdlBackpressureForDrCutoverTimezoneDdlAndSinkBackpressureScenarioCase(
    case_id="dr_cutover_timezone_ddl_and_sink_backpressure",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "timezone_sensitive_ddl",
                    "factor": "timezone_sensitive_ddl",
                    "entity": "timezone_sensitive_ddl",
                    "evidence": [
                        "TiCDC log exposed one downstream DDL rejection and its failed commit TSO."
                    ]
                },
                {
                    "type": "checkpoint_resolved_split",
                    "factor": "checkpoint_resolved_split",
                    "entity": "checkpoint_resolved_split",
                    "evidence": [
                        "The control-plane state stayed normal while checkpoint stopped at the failed DDL and resolved progress advanced."
                    ]
                },
                {
                    "type": "failed_commit_epoch",
                    "factor": "failed_commit_epoch",
                    "entity": "failed_commit_epoch",
                    "evidence": [
                        "The unique failed DDL CommitTs defined the first safe recovery TSO."
                    ]
                },
                {
                    "type": "downstream_sink_backpressure",
                    "factor": "downstream_sink_backpressure",
                    "entity": "downstream_sink_backpressure",
                    "evidence": [
                        "SHOW TRIGGERS distinguished the slow write trigger on the replicated business table from the healthy archive trigger."
                    ]
                },
                {
                    "type": "post_ddl_data_risk",
                    "factor": "post_ddl_data_risk",
                    "entity": "post_ddl_data_risk",
                    "evidence": [
                        "The recovery preserved business rows committed after the failed DDL and the fixed live-writer row."
                    ]
                },
                {
                    "type": "scope_exclusion",
                    "factor": "scope_exclusion",
                    "entity": "scope_exclusion",
                    "evidence": [
                        "The healthy topology and archive neighbor were excluded from the root cause."
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "created the equivalent downstream timestamp DDL",
                "recreated the same changefeed immediately after the observed failed DDL commit TSO",
                "removed the slow write behavior from the replicated business table"
            ],
            "verification": [
                "the changefeed returned NORMAL with resolved progress caught up from the required recovery epoch",
                "the downstream DDL and complete business rows matched the source"
            ]
        },
        "summary": "The recovery separated the downstream DDL compatibility issue from real business-table sink backpressure and preserved all cutover-window rows."
    },
    case_no=0,
    evaluator=TidbBusinessChangeTimezoneDdlBackpressureEvaluatorCase,
    title="容灾切换期间 TiCDC 复制进度与下游写入能力复合故障",
    alert=(
        "[CRITICAL] 容灾切换窗口内，下游业务数据新鲜度持续落后于仍在写入的上游。"
        "请在给定业务范围内定位并恢复这条复制路径，保留切换窗口内已经提交的业务数据。"
        "允许执行完成任务所需的受限业务写入、schema 修复和目标 changefeed 恢复；不要改变全局时区、"
        "删除或重建业务数据，也不要影响无关服务。"
    ),
    initial_state={
        "status": "degraded",
        "changefeed": "control_plane_may_be_normal",
        "checkpoint": "not advancing",
        "resolved": "lagging",
        "downstream": "freshness_behind_source",
        "business_data": "cutover_window_at_risk",
    },
    expected_target={
        "status": "recovered",
        "changefeed": "normal",
        "checkpoint": "caught_up",
        "resolved": "caught_up",
        "downstream": "business_write_capacity_restored",
        "business_data": "all_rows_preserved",
    },
    background_workload=_TIMEZONE_DDL_BACKGROUND_WORKLOAD,
    knowledge_contract=TIMEZONE_DDL_KNOWLEDGE_CONTRACT,
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.837563,
        reference_run_ids=(
            "reference-92__"
            "tidb_business_change_timezone_ddl_backpressure__"
            "dr_cutover_timezone_ddl_and_sink_backpressure__mock-reference__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=180,
        bootstrap_cache_enabled=False,
        replication=TiDBReplicationRuntime(
            ticdc_image=TICDC_V8_1_0,
            downstream_image=MYSQL_8_4,
            ticdc_cpu_limit=1.0,
            ticdc_memory_mb=1024,
            downstream_cpu_limit=0.5,
            downstream_memory_mb=1024,
        ),
    ),
    source_db=SOURCE_DB,
    source_table=SOURCE_TABLE,
    archive_table=ARCHIVE_TABLE,
    ddl_table=DDL_TABLE,
    ddl_column=DDL_COLUMN,
    allowed_timestamp_defaults=(DDL_DEFAULT_UTC, DDL_DEFAULT_LOCAL),
    changefeed_id=CHANGEFEED_ID,
    business_trigger=BUSINESS_TRIGGER,
    archive_trigger=ARCHIVE_TRIGGER,
    seeded_rows=SEEDED_ROWS,
    post_fault_rows=POST_FAULT_ROWS,
    post_fault_start_id=POST_FAULT_START_ID,
    post_fault_end_id=POST_FAULT_END_ID,
    live_writer_id=LIVE_WRITER_ID,
)

_REDUCED_BACKPRESSURE_CASE = replace(
    _CASE,
    case_id="dr_cutover_timezone_ddl_reduced_backpressure",
    case_no=1,
    evaluator=TidbBusinessChangeTimezoneDdlReducedBackpressureEvaluatorCase,
    title="容灾切换期间较小写入批次下的 TiCDC 时区 DDL 与 sink 背压",
    post_fault_rows=12,
    post_fault_end_id=_CASE.post_fault_start_id + 11,
    background_workload=replace(_CASE.background_workload, worker_count=4),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.5,
        reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
        protocol_version='difficulty-v2',
    ),
)


class TidbBusinessChangeTimezoneDdlBackpressureInjector(BaseFaultInjector):

    retain_workload_after_metric_history = True

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Keep the fault state active through the Agent phase."""
    """Create a real TiCDC DDL stop plus a downstream sink throttle."""

    def __init__(self):
        self.source_db = None
        self.source_table = None
        self.archive_table = None
        self.ddl_table = None
        self.ddl_column = None
        self.changefeed_id = None
        self.business_trigger = None
        self.archive_trigger = None
        self.seeded_rows = None
        self.post_fault_rows = None
        self.post_fault_start_id = None
        self.post_fault_end_id = None
        self.live_writer_id = None
        self.ddl_commit_ts = None
        self.pre_ddl_checkpoint_tso = None
        self.seed_truth = None
        self.archive_truth = None
        self._workload_runner = None

    def _configure(self, config: Mapping[str, object]) -> None:
        self.source_db = validate_sql_identifier(str(config["source_db"]), "source_db")
        self.source_table = validate_sql_identifier(str(config["source_table"]), "source_table")
        self.archive_table = validate_sql_identifier(str(config["archive_table"]), "archive_table")
        self.ddl_table = validate_sql_identifier(str(config["ddl_table"]), "ddl_table")
        self.ddl_column = validate_sql_identifier(str(config["ddl_column"]), "ddl_column")
        self.changefeed_id = str(config["changefeed_id"])
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", self.changefeed_id):
            raise ValueError(f"Invalid TiCDC changefeed_id: {self.changefeed_id!r}")
        self.business_trigger = validate_sql_identifier(str(config["business_trigger"]), "business_trigger")
        self.archive_trigger = validate_sql_identifier(str(config["archive_trigger"]), "archive_trigger")
        self.seeded_rows = int(config["seeded_rows"])
        self.post_fault_rows = int(config["post_fault_rows"])
        self.post_fault_start_id = int(config["post_fault_start_id"])
        self.post_fault_end_id = int(config["post_fault_end_id"])
        self.live_writer_id = int(config["live_writer_id"])

    @staticmethod
    def _rows(env, sql: str, context: str, target: str | None = None) -> tuple[tuple[object, ...], ...]:
        raw = env.execute_sql(sql, target=target) if target is not None else env.execute_sql(sql)
        return tuple(tuple(row) for row in require_result_rows(raw, context))

    def _current_tso(self, env, context: str) -> int:
        tso = int(env.current_tso())
        if tso <= 0:
            raise ValueError(f"{context} must be positive: changefeed_id={self.changefeed_id!r}, tso={tso}")
        return tso

    def attach_workload_runner(self, runner) -> None:
        if self._workload_runner is not None:
            raise RuntimeError("timezone-ddl received more than one workload runner")
        self._workload_runner = runner

    @staticmethod
    def _values(start: int, end: int, prefix: str) -> str:
        return ",".join(
            f"({row_id}, {row_id * 10}.00, 'paid', '2026-08-03 00:00:00', '{prefix}-{row_id}')"
            for row_id in range(start, end + 1)
        )

    @staticmethod
    def _run_ticdc_cli(env, arguments: list[str]) -> str:
        return env.get_deployment().exec("ticdc/ticdc-0", ["/cdc", "cli", "changefeed", *arguments])

    @staticmethod
    def _wait_for_status(env, changefeed_id: str, predicate, label: str, timeout: float = 120) -> dict:
        deadline = time.monotonic() + timeout
        last_status = None
        while time.monotonic() < deadline:
            try:
                last_status = env.replication_status(changefeed_id)
            except HTTPError as exc:
                if exc.code == 404:
                    time.sleep(1)
                    continue
                if exc.code == 400:
                    body = exc.read().decode("utf-8", errors="replace")
                    if "CDC:ErrChangeFeedNotExists" in body:
                        time.sleep(1)
                        continue
                    raise RuntimeError(
                        f"TiCDC status request failed: changefeed_id={changefeed_id!r}, "
                        f"http_status={exc.code}, response_body={body!r}"
                    ) from exc
                body = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"TiCDC status request failed: changefeed_id={changefeed_id!r}, "
                    f"http_status={exc.code}, response_body={body!r}"
                ) from exc
            if predicate(last_status):
                return last_status
            time.sleep(1)
        raise RuntimeError(
            f"TiCDC status did not reach {label}: changefeed_id={changefeed_id!r}, last_status={last_status!r}"
        )

    def _setup_upstream(self, env) -> None:
        require_sql_success(
            env.execute_sql(f"CREATE DATABASE {self.source_db}"),
            f"timezone-ddl create upstream database {self.source_db}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.source_db}.{self.source_table} ("
                "id BIGINT PRIMARY KEY, amount DECIMAL(12,2) NOT NULL, "
                "state VARCHAR(16) NOT NULL, updated_at DATETIME NOT NULL, note VARCHAR(255) NOT NULL)"
            ),
            "timezone-ddl create upstream business table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.source_db}.{self.archive_table} ("
                "id BIGINT PRIMARY KEY, tenant_id BIGINT NOT NULL, amount DECIMAL(12,2) NOT NULL, "
                "updated_at DATETIME NOT NULL, note VARCHAR(255) NOT NULL)"
            ),
            "timezone-ddl create upstream archive table",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.source_db}.{self.source_table} "
                f"(id, amount, state, updated_at, note) VALUES {self._values(1, self.seeded_rows, 'seed')}"
            ),
            "timezone-ddl seed upstream business rows",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.source_db}.{self.archive_table} "
                f"(id, tenant_id, amount, updated_at, note) VALUES "
                + ",".join(
                    f"({row_id}, {row_id % 7}, {row_id * 3}.00, '2026-08-03 00:00:00', 'archive-{row_id}')"
                    for row_id in range(1, 81)
                )
            ),
            "timezone-ddl seed upstream archive rows",
        )

    def _setup_downstream(self, env) -> None:
        require_sql_success(
            env.execute_sql(f"CREATE DATABASE {self.source_db}", target="downstream"),
            f"timezone-ddl create downstream database {self.source_db}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.source_db}.{self.source_table} ("
                "id BIGINT PRIMARY KEY, amount DECIMAL(12,2) NOT NULL, "
                "state VARCHAR(16) NOT NULL, updated_at DATETIME NOT NULL, note VARCHAR(255) NOT NULL)",
                target="downstream",
            ),
            "timezone-ddl create downstream business table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.source_db}.{self.archive_table} ("
                "id BIGINT PRIMARY KEY, tenant_id BIGINT NOT NULL, amount DECIMAL(12,2) NOT NULL, "
                "updated_at DATETIME NOT NULL, note VARCHAR(255) NOT NULL)",
                target="downstream",
            ),
            "timezone-ddl create downstream archive table",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.source_db}.{self.source_table} "
                f"(id, amount, state, updated_at, note) VALUES {self._values(1, self.seeded_rows, 'seed')}",
                target="downstream",
            ),
            "timezone-ddl seed downstream business rows",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.source_db}.{self.archive_table} "
                f"(id, tenant_id, amount, updated_at, note) VALUES "
                + ",".join(
                    f"({row_id}, {row_id % 7}, {row_id * 3}.00, '2026-08-03 00:00:00', 'archive-{row_id}')"
                    for row_id in range(1, 81)
                ),
                target="downstream",
            ),
            "timezone-ddl seed downstream archive rows",
        )

    def _create_sink_triggers(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TRIGGER {self.source_db}.{self.business_trigger} "
                f"BEFORE INSERT ON {self.source_db}.{self.source_table} "
                "FOR EACH ROW BEGIN DO SLEEP(0.12); END",
                target="downstream",
            ),
            "timezone-ddl create real downstream business slow-write trigger",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TRIGGER {self.source_db}.{self.archive_trigger} "
                f"AFTER INSERT ON {self.source_db}.{self.archive_table} "
                "FOR EACH ROW SET @cf01_archive_audit_seen = 1",
                target="downstream",
            ),
            "timezone-ddl create healthy downstream archive audit trigger",
        )

    def _create_changefeed(self, env) -> dict:
        self._run_ticdc_cli(
            env,
            [
                "create",
                "--server=http://127.0.0.1:8300",
                "--sink-uri=mysql://root@mysql-0:3306/",
                f"--changefeed-id={self.changefeed_id}",
                "--no-confirm",
            ]
        )
        seed_tso = self._current_tso(env, "timezone-ddl capture seed replication TSO")
        return self._wait_for_status(
            env,
            self.changefeed_id,
            lambda status: (
                str(status.get("state", "")).casefold() == "normal"
                and not status.get("error")
                and int(status.get("checkpoint_tso", 0)) >= seed_tso
                and int(status.get("resolved_ts", 0)) >= int(status.get("checkpoint_tso", 0))
            ),
            f"seed replication catch-up at source TSO {seed_tso}",
        )

    def _inject_pre_ddl_probe(self, env, baseline_status: Mapping[str, object]) -> None:
        baseline_checkpoint = int(baseline_status.get("checkpoint_tso", 0))
        if baseline_checkpoint <= 0:
            raise RuntimeError(
                "timezone-ddl cannot establish the pre-DDL progress boundary: "
                f"changefeed_id={self.changefeed_id!r}, baseline_status={baseline_status!r}"
            )
        require_sql_success(
            env.execute_sql(
                f"REPLACE INTO {self.source_db}.{self.source_table} "
                "(id, amount, state, updated_at, note) VALUES "
                f"({self.seeded_rows}, {self.seeded_rows * 10}.00, 'paid', "
                "'2026-08-03 00:00:00', "
                f"'seed-{self.seeded_rows}')"
            ),
            "timezone-ddl create pre-DDL sink progress probe",
        )
        self._wait_for_status(
            env,
            self.changefeed_id,
            lambda status: (
                str(status.get("state", "")).casefold() == "normal"
                and not status.get("error")
                and int(status.get("checkpoint_tso", 0)) > baseline_checkpoint
                and int(status.get("resolved_ts", 0)) >= int(status.get("checkpoint_tso", 0))
            ),
            "checkpoint progress after the pre-DDL sink probe",
        )
        self.pre_ddl_checkpoint_tso = baseline_checkpoint

    def _inject_timezone_ddl(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"SET SESSION time_zone = '+00:00'; "
                f"CREATE TABLE {self.source_db}.{self.ddl_table} ("
                f"id BIGINT PRIMARY KEY, {self.ddl_column} TIMESTAMP NOT NULL "
                f"DEFAULT '{DDL_DEFAULT_UTC}')"
            ),
            "timezone-ddl execute UTC-sensitive upstream DDL",
        )

    def _read_ddl_commit_ts(self, env, log: str | None = None) -> int:
        if log is None:
            log = env.get_deployment().read_logs("ticdc/ticdc-0", lines=10000)
        if "Error 1067" not in log or "Invalid default" not in log:
            raise RuntimeError(
                f"timezone-ddl TiCDC log does not contain the expected timezone DDL failure: "
                f"changefeed_id={self.changefeed_id!r}, log_tail={log[-4000:]!r}"
            )
        matches = sorted(set(re.findall(
            r'(?:\\?"CommitTs\\?"\s*:\s*|commitTs=)(\d+)',
            log,
            flags=re.IGNORECASE,
        )))
        if len(matches) != 1:
            raise RuntimeError(
                f"timezone-ddl expected one failed DDL CommitTs in TiCDC log: matches={matches!r}, "
                f"changefeed_id={self.changefeed_id!r}"
            )
        return int(matches[0])

    def _wait_for_ddl_failure(self, env, timeout: float = 120) -> int:
        deadline = time.monotonic() + timeout
        last_status = None
        while time.monotonic() < deadline:
            log = env.get_deployment().read_logs("ticdc/ticdc-0", lines=10000)
            if "Error 1067" in log and "Invalid default" in log:
                commit_ts = self._read_ddl_commit_ts(env, log)
                last_status = env.replication_status(self.changefeed_id)
                checkpoint = int(last_status.get("checkpoint_tso", 0))
                resolved = int(last_status.get("resolved_ts", 0))
                if checkpoint == commit_ts and resolved >= checkpoint:
                    return commit_ts
            time.sleep(1)
        raise RuntimeError(
            f"timezone-ddl TiCDC did not expose the failed DDL checkpoint: "
            f"changefeed_id={self.changefeed_id!r}, last_status={last_status!r}"
        )

    def _inject_post_fault_rows(self, env) -> None:
        start = self.seeded_rows + 1
        end = self.seeded_rows + self.post_fault_rows
        if start != self.post_fault_start_id or end != self.post_fault_end_id:
            raise RuntimeError(
                "timezone-ddl post-DDL row boundary does not match the case contract: "
                f"start={start}, end={end}, expected=({self.post_fault_start_id}, {self.post_fault_end_id})"
            )
        values = (
            f"{self._values(start, end, 'after-ddl')},"
            f"({self.live_writer_id}, 1.00, 'paid', '2026-08-03 00:00:00', 'live-writer-stable')"
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.source_db}.{self.source_table} "
                f"(id, amount, state, updated_at, note) VALUES {values}"
            ),
            "timezone-ddl create post-DDL upstream business changes",
        )

    def _trigger_rows(self, env) -> tuple[tuple[object, ...], ...]:
        return self._rows(
            env,
            f"SHOW TRIGGERS FROM {self.source_db}",
            "timezone-ddl inspect downstream trigger catalog",
            target="downstream",
        )

    def _validate_trigger_contract(self, env) -> None:
        rows = self._trigger_rows(env)
        slow_business = tuple(
            row
            for row in rows
            if len(row) >= 4
            and str(row[2]).casefold() == self.source_table.casefold()
            and re.search(r"\bSLEEP\s*\(", str(row[3]), re.IGNORECASE)
        )
        healthy_archive = tuple(
            row
            for row in rows
            if len(row) >= 4
            and str(row[2]).casefold() == self.archive_table.casefold()
            and not re.search(r"\bSLEEP\s*\(", str(row[3]), re.IGNORECASE)
        )
        if len(slow_business) != 1 or len(healthy_archive) != 1:
            raise RuntimeError(
                "timezone-ddl trigger contract is not established: "
                f"changefeed_id={self.changefeed_id!r}, source_table={self.source_table!r}, "
                f"archive_table={self.archive_table!r}, slow_business={slow_business!r}, "
                f"healthy_archive={healthy_archive!r}, trigger_rows={rows!r}"
            )

    def _validate_core_health(self, env) -> None:
        deployment = env.get_deployment()
        states = deployment.node_states()
        expected_targets = set(deployment.list_database_nodes())
        missing = sorted(expected_targets - set(states))
        if missing:
            raise RuntimeError(
                "timezone-ddl core health check is missing database nodes: "
                f"missing={missing!r}, observed={sorted(states)!r}"
            )
        unhealthy = {
            target: state
            for target, state in states.items()
            if target in expected_targets
            and (
                state.get("running") is not True
                or state.get("paused") is True
                or state.get("oom_killed") is True
                or state.get("status") != "running"
            )
        }
        if unhealthy:
            raise RuntimeError(f"timezone-ddl core TiDB health check failed: unhealthy={unhealthy!r}")

    def _validate_fault_state(self, env) -> None:
        if self.ddl_commit_ts is None:
            raise RuntimeError("timezone-ddl cannot validate the fault before the failed DDL CommitTs is known")
        log = env.get_deployment().read_logs("ticdc/ticdc-0", lines=10000)
        observed_commit_ts = self._read_ddl_commit_ts(env, log)
        if observed_commit_ts != self.ddl_commit_ts:
            raise RuntimeError(
                "timezone-ddl failed DDL CommitTs changed during lifecycle validation: "
                f"expected={self.ddl_commit_ts}, observed={observed_commit_ts}, "
                f"changefeed_id={self.changefeed_id!r}"
            )
        status = env.replication_status(self.changefeed_id)
        checkpoint = int(status.get("checkpoint_tso", 0))
        resolved = int(status.get("resolved_ts", 0))
        if (
            str(status.get("state", "")).casefold() != "normal"
            or status.get("error")
            or checkpoint != self.ddl_commit_ts
            or resolved < checkpoint
        ):
            raise RuntimeError(
                "timezone-ddl fault progress contract is not established: "
                f"changefeed_id={self.changefeed_id!r}, failed_commit_ts={self.ddl_commit_ts}, "
                f"status={status!r}"
            )
        self._validate_trigger_contract(env)
        seed_rows = self._rows(
            env,
            f"SELECT id, amount, state, updated_at, note FROM {self.source_db}.{self.source_table} "
            f"WHERE id <= {self.seeded_rows} ORDER BY id",
            "timezone-ddl validate source seed truth",
        )
        if self.seed_truth is None:
            self.seed_truth = seed_rows
        if seed_rows != self.seed_truth:
            raise RuntimeError(
                "timezone-ddl source seed truth changed during fault setup: "
                f"expected={self.seed_truth!r}, observed={seed_rows!r}"
            )
        archive_rows = self._rows(
            env,
            f"SELECT id, tenant_id, amount, updated_at, note FROM {self.source_db}.{self.archive_table} "
            "ORDER BY id",
            "timezone-ddl validate source archive truth",
        )
        if self.archive_truth is None:
            self.archive_truth = archive_rows
        if archive_rows != self.archive_truth:
            raise RuntimeError(
                "timezone-ddl source archive truth changed during fault setup: "
                f"expected={self.archive_truth!r}, observed={archive_rows!r}"
            )
        post_rows = self._rows(
            env,
            f"SELECT id, amount, state, updated_at, note FROM {self.source_db}.{self.source_table} "
            f"WHERE id BETWEEN {self.post_fault_start_id} AND {self.post_fault_end_id} "
            f"OR id = {self.live_writer_id} ORDER BY id",
            "timezone-ddl validate post-DDL business boundary",
        )
        observed_ids = {int(row[0]) for row in post_rows}
        expected_ids = set(range(self.post_fault_start_id, self.post_fault_end_id + 1))
        expected_ids.add(self.live_writer_id)
        if observed_ids != expected_ids:
            raise RuntimeError(
                "timezone-ddl post-DDL business boundary is incomplete: "
                f"expected_ids={sorted(expected_ids)!r}, observed_ids={sorted(observed_ids)!r}"
            )
        ddl_rows = self._rows(
            env,
            f"SHOW TABLES FROM {self.source_db} LIKE '{self.ddl_table}'",
            "timezone-ddl inspect downstream DDL gap",
            target="downstream",
        )
        if ddl_rows:
            raise RuntimeError(
                "timezone-ddl downstream DDL unexpectedly exists before repair: "
                f"ddl_table={self.ddl_table!r}, rows={ddl_rows!r}"
            )
        self._validate_core_health(env)

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        env = context.env
        self._setup_upstream(env)
        self._setup_downstream(env)
        self.seed_truth = self._rows(
            env,
            f"SELECT id, amount, state, updated_at, note FROM {self.source_db}.{self.source_table} "
            f"WHERE id <= {self.seeded_rows} ORDER BY id",
            "timezone-ddl capture source seed truth",
        )
        self.archive_truth = self._rows(
            env,
            f"SELECT id, tenant_id, amount, updated_at, note FROM {self.source_db}.{self.archive_table} "
            "ORDER BY id",
            "timezone-ddl capture source archive truth",
        )
        changefeed_status = self._create_changefeed(env)
        self._create_sink_triggers(env)
        self._inject_pre_ddl_probe(env, changefeed_status)
        self._inject_timezone_ddl(env)
        self.ddl_commit_ts = self._wait_for_ddl_failure(env)
        self._inject_post_fault_rows(env)
        self._validate_fault_state(env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        if self.ddl_commit_ts is None:
            self.ddl_commit_ts = self._wait_for_ddl_failure(context.env)
        self.seed_truth = self._rows(
            context.env,
            f"SELECT id, amount, state, updated_at, note FROM {self.source_db}.{self.source_table} "
            f"WHERE id <= {self.seeded_rows} ORDER BY id",
            "timezone-ddl restore source seed truth",
        )
        self.archive_truth = self._rows(
            context.env,
            f"SELECT id, tenant_id, amount, updated_at, note FROM {self.source_db}.{self.archive_table} "
            "ORDER BY id",
            "timezone-ddl restore source archive truth",
        )
        self._validate_fault_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._validate_fault_state(context.env)
        return {
            "fault_ddl_commit_ts": self.ddl_commit_ts,
            "fault_source_seed_truth": self.seed_truth,
            "fault_archive_truth": self.archive_truth,
            "fault_post_fault_row_ids": (
                self.post_fault_start_id,
                self.post_fault_end_id,
                self.live_writer_id,
            ),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        if self._workload_runner is not None:
            self._workload_runner.stop()
            self._workload_runner = None

    def recover(self, context: FaultLifecycleContext) -> None:
        env = context.env
        if self._workload_runner is not None:
            self._workload_runner.stop()
            self._workload_runner = None
        require_sql_success(
            env.execute_sql(
                f"DROP TRIGGER IF EXISTS {self.source_db}.{self.business_trigger}",
                target="downstream",
            ),
            "timezone-ddl remove downstream business slow-write trigger",
        )
        require_sql_success(
            env.execute_sql(
                f"DROP TRIGGER IF EXISTS {self.source_db}.{self.archive_trigger}",
                target="downstream",
            ),
            "timezone-ddl remove downstream archive audit trigger",
        )
        try:
            env.replication_status(self.changefeed_id)
        except HTTPError as exc:
            if exc.code == 404:
                pass
            elif exc.code == 400:
                body = exc.read().decode("utf-8", errors="replace")
                if "CDC:ErrChangeFeedNotExists" not in body:
                    raise RuntimeError(
                        "timezone-ddl changefeed cleanup status request failed: "
                        f"changefeed_id={self.changefeed_id!r}, http_status={exc.code}, response_body={body!r}"
                    ) from exc
            else:
                raise
        else:
            self._run_ticdc_cli(
                env,
                [
                    "remove",
                    "--server=http://127.0.0.1:8300",
                    f"--changefeed-id={self.changefeed_id}",
                ]
            )
        require_sql_success(
            env.execute_sql(f"DROP DATABASE IF EXISTS {self.source_db}"),
            "timezone-ddl remove upstream case schema",
        )
        require_sql_success(
            env.execute_sql(
                f"DROP DATABASE IF EXISTS {self.source_db}",
                target="downstream",
            ),
            "timezone-ddl remove downstream case schema",
        )


class TidbBusinessChangeTimezoneDdlBackpressureScenario(TiDBScenario):
    scenario_id = SCENARIO_ID
    description = "TiCDC replication progress mismatch compounded by downstream business-write slowdown."
    cases = (_CASE, _REDUCED_BACKPRESSURE_CASE)

    def build_fault_plan(
        self,
        case: TidbBusinessChangeTimezoneDdlBackpressureForDrCutoverTimezoneDdlAndSinkBackpressureScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbBusinessChangeTimezoneDdlBackpressureInjector,
                config={
                    "source_db": case.source_db,
                    "source_table": case.source_table,
                    "archive_table": case.archive_table,
                    "ddl_table": case.ddl_table,
                    "ddl_column": case.ddl_column,
                    "changefeed_id": case.changefeed_id,
                    "business_trigger": case.business_trigger,
                    "archive_trigger": case.archive_trigger,
                    "seeded_rows": case.seeded_rows,
                    "post_fault_rows": case.post_fault_rows,
                    "post_fault_start_id": case.post_fault_start_id,
                    "post_fault_end_id": case.post_fault_end_id,
                    "live_writer_id": case.live_writer_id,
                },
            ),
        )
