import threading
from collections.abc import Mapping
from dataclasses import dataclass, replace

from src.database.sql import sql_literal
from src.scenarios.evaluation.tidb.health_check.syncpoint_consistency import (
    TidbHealthCheckSyncpointConsistencyEvaluatorCase,
    TidbHealthCheckSyncpointConsistencyForSingleReleaseRepairEvaluatorCase,
)
from src.scenarios.base import (
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.tidb.common import (
    connect_tidb,
    json_object,
    join_thread,
    require_sql_success,
    run_sql_batches,
    validate_sql_identifier,
)
from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase, WorkloadProfile

from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime

@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckSyncpointConsistencyCase(TiDBScenarioCase):
    primary_schema: str
    secondary_schema: str
    ops_schema: str
    syncpoint_id: str
    audit_key: str
    audit_request: str
    audit_request_queue_table: str
    release_consumer: str
    audit_window_label: str
    order_table: str
    item_table: str
    gc_setting: str
    original_gc_life_time: str
    temporary_gc_life_time: str
    secondary_port_offset: int
    primary_tso: int
    secondary_tso: int
    external_tso: int
    syncpoint_order_count: int
    syncpoint_order_diff_rows: int
    syncpoint_item_count: int
    syncpoint_item_checksum_match: int
    syncpoint_item_diff_rows: int
    order_item_orphan_rows: int
    release_allowed: int
    live_primary_extra_orders: int
    noise_event_count: int
    repair_lease_id: str
    repair_lease_id_2: str
    repair_lease_table: str
    repair_request_table: str
    repair_worker_table: str
    repair_item_id: str
    repair_item_id_2: str
    repair_count: int
    repair_decoy_lease_count: int
    repair_same_row_decoy_count: int
    repair_delay_seconds: float


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckSyncpointConsistencyForSyncpointConsistencyUnderWritesScenarioCase(
    TidbHealthCheckSyncpointConsistencyCase
):
    pass


def _hc02_profiles() -> tuple[WorkloadProfile, ...]:
    return (
        WorkloadProfile(
            name="hc02_live_primary_order_writes",
            sql=(
                "INSERT INTO retail_primary.orders "
                "(order_id, customer_id, region_code, order_status, amount_cents, commit_tso, updated_at, payload_crc) "
                "VALUES (CONCAT('live-', REPLACE(UUID(), '-', '')), "
                "FLOOR(1000 + RAND() * 9000), 'EAST', 'paid', FLOOR(1000 + RAND() * 90000), "
                "900000000000 + FLOOR(UNIX_TIMESTAMP(NOW(6)) * 1000), NOW(6), CRC32(UUID()))"
            ),
            qps=0.35,
            tier="WRITE",
            commit=True,
        ),
        WorkloadProfile(
            name="hc02_live_primary_item_writes",
            sql=(
                "INSERT INTO retail_primary.order_items "
                "(item_id, order_id, sku_id, quantity, item_amount_cents, commit_tso, updated_at, payload_crc) "
                "VALUES (CONCAT('live-item-', REPLACE(UUID(), '-', '')), CONCAT('live-', FLOOR(RAND()*1000000)), "
                "FLOOR(10000 + RAND() * 90000), 1 + FLOOR(RAND() * 3), FLOOR(500 + RAND() * 20000), "
                "900000000000 + FLOOR(UNIX_TIMESTAMP(NOW(6)) * 1000), NOW(6), CRC32(UUID()))"
            ),
            qps=0.25,
            tier="WRITE",
            commit=True,
        ),
        WorkloadProfile(
            name="hc02_direct_count_decoy",
            sql=(
                "SELECT 'orders' AS table_name, "
                "(SELECT COUNT(*) FROM retail_primary.orders) AS primary_rows, "
                "(SELECT COUNT(*) FROM retail_secondary.orders) AS secondary_rows, "
                "(SELECT COUNT(*) FROM retail_primary.orders) - (SELECT COUNT(*) FROM retail_secondary.orders) AS direct_delta"
            ),
            qps=0.45,
            tier="NOISE",
        ),
        WorkloadProfile(
            name="hc02_customer_dashboard",
            sql=(
                "SELECT customer_id % 17 AS bucket, COUNT(*) AS orders, SUM(amount_cents) AS amount_cents "
                "FROM retail_primary.orders WHERE updated_at >= TIMESTAMPADD(HOUR, -24, NOW()) "
                "GROUP BY customer_id % 17 ORDER BY amount_cents DESC LIMIT 12"
            ),
            qps=0.35,
            tier="BUSINESS",
        ),
        WorkloadProfile(
            name="hc02_fulfillment_lag_report",
            sql=(
                "SELECT region_code, order_status, COUNT(*) "
                "FROM retail_secondary.orders WHERE updated_at >= TIMESTAMPADD(DAY, -2, NOW()) "
                "GROUP BY region_code, order_status ORDER BY COUNT(*) DESC"
            ),
            qps=0.3,
            tier="BUSINESS",
        ),
        WorkloadProfile(
            name="hc02_item_revenue_rollup",
            sql=(
                "SELECT sku_id % 29 AS sku_bucket, COUNT(*) AS lines, SUM(item_amount_cents) AS revenue "
                "FROM retail_primary.order_items GROUP BY sku_id % 29 ORDER BY revenue DESC LIMIT 20"
            ),
            qps=0.28,
            tier="BUSINESS",
        ),
        WorkloadProfile(
            name="hc02_repl_noise_events",
            sql=(
                "SELECT severity, source, COUNT(*) FROM ops_repl.repl_events "
                "WHERE event_time >= TIMESTAMPADD(HOUR, -6, NOW()) GROUP BY severity, source ORDER BY COUNT(*) DESC"
            ),
            qps=0.25,
            tier="NOISE",
        ),
        WorkloadProfile(
            name="hc02_syncpoint_catalog_scan",
            sql=(
                "SELECT syncpoint_id, state, primary_tso, secondary_tso, external_tso, captured_at "
                "FROM ops_repl.syncpoint_map ORDER BY captured_at DESC LIMIT 12"
            ),
            qps=0.18,
            tier="NOISE",
        ),
        WorkloadProfile(
            name="hc02_runbook_lookup",
            sql=(
                "SELECT step_no, step_name FROM ops_repl.audit_runbook_steps "
                "WHERE audit_key = 'hc02_live_retail_orders' ORDER BY step_no"
            ),
            qps=0.12,
            tier="NOISE",
        ),
        WorkloadProfile(
            name="hc02_audit_window_scan",
            sql=(
                "SELECT request_id, consumer, window_label, release_state, audit_key "
                "FROM ops_repl.audit_window_catalog ORDER BY requested_at DESC LIMIT 20"
            ),
            qps=0.1,
            tier="NOISE",
        ),
        WorkloadProfile(
            name="hc02_binding_history_scan",
            sql=(
                "SELECT binding_id, audit_key, syncpoint_id, consumer, window_label, binding_state "
                "FROM ops_repl.audit_syncpoint_bindings ORDER BY bound_at DESC LIMIT 20"
            ),
            qps=0.1,
            tier="NOISE",
        ),
        WorkloadProfile(
            name="hc02_release_request_queue_scan",
            sql=(
                "SELECT request_id, consumer, target_window, request_state, priority "
                "FROM ops_repl.audit_request_queue ORDER BY requested_at DESC LIMIT 20"
            ),
            qps=0.08,
            tier="NOISE",
        ),
    )


_HC02_CASE = TidbHealthCheckSyncpointConsistencyForSyncpointConsistencyUnderWritesScenarioCase(
    case_id="syncpoint_consistency_under_writes",
    case_no=0,
    reference_report={
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": [
                "recorded the mapped-TSO audit artifact and restored temporary GC retention"
            ],
            "verification": [
                "final mapped snapshot, repair jobs, release binding, and GC state were verified"
            ],
        },
        "summary": "The mapped syncpoint audit was completed and the temporary control was restored.",
    },
    evaluator=TidbHealthCheckSyncpointConsistencyEvaluatorCase,
    title="持续写入下的主备快照一致性审计",
    alert=(
        "晨间例行巡检：新零售账务/履约链路昨晚经历持续写入高峰。请按库内值班资料完成一次"
        "可复核的主备一致性审计，判断今天下游盘点是否可以放行。请遵循受控变更边界，不能"
        "直接修改业务表；结束时需要把临时审计配置恢复到巡检前状态。"
    ),
    initial_state={
        "surface": "current primary/secondary row counts differ while writes continue",
        "audit_context": "syncpoint metadata, release windows and runbook are stored in ops_repl",
        "mapped_snapshot": "mapped snapshot state must be established from the two business tables",
        "repair_context": "control-plane authorization records include current and historical candidates",
    },
    expected_target={
        "audit_result": "one_complete_mapped_tso_consistency_artifact_after_reconciling_the_interrupted_attempt",
        "syncpoint_selection": "resolve_audit_key_binding_before_latest_eligible_candidate",
        "repair_workflow": "follow_the_current_release_control_plane_authorization_and_reaudit_if_repair_is_required",
        "release_decision": "release_allowed_only_after_the_mapped_snapshot_is_consistent",
        "gc_config": "restored",
        "direct_count_delta": "orders and order_items deltas documented separately as expected live-write differences",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_hc02_profiles(),
        worker_count=8,
        seed=0xAC02,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=8.0,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=26,
        environmental_complexity=0.961382,
        reference_run_ids=(
            "reference-195__tidb_health_check_syncpoint_consistency__syncpoint_consistency_under_writes__mock__r001",
        ),
    ),
    runtime=tidb_runtime(release=TIDB_V8_1_0, pd_count=3, tikv_count=3, tidb_count=2),
    primary_schema="retail_primary",
    secondary_schema="retail_secondary",
    ops_schema="ops_repl",
    syncpoint_id="sp_hc02_20260801_1020",
    audit_key="hc02_live_retail_orders",
    audit_request="hc02_morning_release",
    audit_request_queue_table="audit_request_queue",
    release_consumer="downstream_inventory",
    audit_window_label="retail_orders_20260801_1000",
    order_table="orders",
    item_table="order_items",
    gc_setting="tidb_gc_life_time",
    original_gc_life_time="10m",
    temporary_gc_life_time="2h",
    secondary_port_offset=2,
    primary_tso=720000000420,
    secondary_tso=719999998880,
    external_tso=720000000960,
    syncpoint_order_count=180,
    syncpoint_order_diff_rows=0,
    syncpoint_item_count=420,
    syncpoint_item_checksum_match=1,
    syncpoint_item_diff_rows=0,
    order_item_orphan_rows=0,
    release_allowed=1,
    live_primary_extra_orders=28,
    noise_event_count=720,
    repair_lease_id="auth_7c1f92e4a6b8",
    repair_lease_id_2="auth_b4e8d17c6a20",
    repair_lease_table="repair_leases",
    repair_request_table="repair_requests",
    repair_worker_table="repair_worker_status",
    repair_item_id="itm-00001-1",
    repair_item_id_2="itm-00002-1",
    repair_count=2,
    repair_decoy_lease_count=180,
    repair_same_row_decoy_count=8,
    repair_delay_seconds=0.8,
)


_HC02_NEW_CASE = replace(
    _HC02_CASE,
    case_id="syncpoint_consistency_single_release_repair",
    case_no=1,
    evaluator=TidbHealthCheckSyncpointConsistencyForSingleReleaseRepairEvaluatorCase,
    title="A scoped TiDB syncpoint audit for one release window under continued writes.",
    reference_report={
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": ["reconciled the mapped-TSO drifts for the current release and restored temporary GC retention"],
            "verification": ["re-audited the mapped rows, current authorization, asynchronous jobs, and release binding"],
        },
        "summary": "The single-release syncpoint repair completed with a bounded authorization scope.",
    },
    alert=(
        "例行发布前一致性复核：当前 release window 在持续写入期间出现主备直接计数差异。"
        "请先解析当前 consumer、window、syncpoint 和授权 lease，再按 mapped TSO 做行级比较。"
        "只处理当前 release 仍授权的少量 drift，等待异步 worker 完成后重新审计，并恢复临时 GC 保留设置。"
    ),
    initial_state={
        "surface": "one current release has a small mapped snapshot drift while writes continue",
        "audit_context": "the active binding and repair leases are visible in ops_repl",
        "direct_count_decoy": "primary and secondary totals include expected live-write differences",
    },
    expected_target={
        "audit_result": "mapped rows consistent after the current release repair",
        "repair_workflow": "current-scope lease and bounded asynchronous repair",
        "gc_config": "restored",
        "release_decision": "release allowed after re-audit",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_hc02_profiles(),
        worker_count=6,
        seed=0xAC12,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=6.0,
    ),
    runtime=replace(_HC02_CASE.runtime, bootstrap_cache_enabled=False),
    difficulty=DifficultyCalibration(
        diagnostic_depth=9,
        environmental_complexity=0.82,
        reference_run_ids=(
            "reference-212__"
            "tidb_health_check_syncpoint_consistency__"
            "syncpoint_consistency_single_release_repair__mock__r001",
        ),
    ),
    syncpoint_order_count=96,
    syncpoint_item_count=180,
    live_primary_extra_orders=12,
    noise_event_count=240,
    repair_decoy_lease_count=64,
    repair_same_row_decoy_count=3,
    repair_delay_seconds=0.5,
)


class TidbHealthCheckSyncpointConsistencyScenario(TiDBScenario):
    scenario_id = "tidb_health_check_syncpoint_consistency"
    description = "Health-check audit for TiDB upstream/downstream consistency under continuous writes."
    cases = (_HC02_CASE, _HC02_NEW_CASE)

    def build_fault_plan(self, case: TidbHealthCheckSyncpointConsistencyCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbHealthCheckSyncpointConsistencyInjector,
                config={
                    "primary_schema": case.primary_schema,
                    "secondary_schema": case.secondary_schema,
                    "ops_schema": case.ops_schema,
                    "syncpoint_id": case.syncpoint_id,
                    "audit_key": case.audit_key,
                    "audit_request": case.audit_request,
                    "audit_request_queue_table": case.audit_request_queue_table,
                    "release_consumer": case.release_consumer,
                    "audit_window_label": case.audit_window_label,
                    "order_table": case.order_table,
                    "item_table": case.item_table,
                    "gc_setting": case.gc_setting,
                    "original_gc_life_time": case.original_gc_life_time,
                    "temporary_gc_life_time": case.temporary_gc_life_time,
                    "secondary_port_offset": case.secondary_port_offset,
                    "primary_tso": case.primary_tso,
                    "secondary_tso": case.secondary_tso,
                    "external_tso": case.external_tso,
                    "syncpoint_order_count": case.syncpoint_order_count,
                    "syncpoint_order_diff_rows": case.syncpoint_order_diff_rows,
                    "syncpoint_item_count": case.syncpoint_item_count,
                    "syncpoint_item_checksum_match": case.syncpoint_item_checksum_match,
                    "syncpoint_item_diff_rows": case.syncpoint_item_diff_rows,
                    "order_item_orphan_rows": case.order_item_orphan_rows,
                    "release_allowed": case.release_allowed,
                    "live_primary_extra_orders": case.live_primary_extra_orders,
                    "noise_event_count": case.noise_event_count,
                    "repair_lease_id": case.repair_lease_id,
                    "repair_lease_id_2": case.repair_lease_id_2,
                    "repair_lease_table": case.repair_lease_table,
                    "repair_request_table": case.repair_request_table,
                    "repair_worker_table": case.repair_worker_table,
                    "repair_item_id": case.repair_item_id,
                    "repair_item_id_2": case.repair_item_id_2,
                    "repair_count": case.repair_count,
                    "repair_decoy_lease_count": case.repair_decoy_lease_count,
                    "repair_same_row_decoy_count": case.repair_same_row_decoy_count,
                    "repair_delay_seconds": case.repair_delay_seconds,
                },
            ),
        )


class TidbHealthCheckSyncpointConsistencyInjector(BaseFaultInjector):
    """Create a live-write primary/secondary consistency-audit fixture."""

    def __init__(self) -> None:
        self._repair_stop = threading.Event()
        self._repair_thread = None
        self._repair_error = None

    def install(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._drop_existing(context.env)
        self._create_schemas(context.env)
        self._create_business_tables(context.env)
        self._load_syncpoint_rows(context.env)
        self._load_live_primary_rows(context.env)
        self._create_ops_tables(context.env)
        self._load_noise_tables(context.env)
        context.env.configure_secondary_endpoint(
            "127.0.0.1", context.env.port + self.secondary_port_offset, ""
        )
        self._verify_persistent_state(context.env)

    def activate(self, context: FaultLifecycleContext):
        self._configure(context.config)
        context.env.configure_secondary_endpoint(
            "127.0.0.1", context.env.port + self.secondary_port_offset, ""
        )
        self._verify_persistent_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext):
        self._configure(context.config)
        direct_primary = self._scalar(
            context.env,
            f"SELECT COUNT(*) FROM {self.primary_schema}.{self.order_table}",
            "primary current order count",
        )
        direct_secondary = self._scalar(
            context.env,
            f"SELECT COUNT(*) FROM {self.secondary_schema}.{self.order_table}",
            "secondary current order count",
        )
        self._start_repair_worker(context.env, context.run_id)
        return {
            "syncpoint_id": self.syncpoint_id,
            "direct_primary_orders": direct_primary,
            "direct_secondary_orders": direct_secondary,
            "direct_count_delta": direct_primary - direct_secondary,
        }

    def quiesce(self, context: FaultLifecycleContext):
        self._stop_repair_worker()

    def recover(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._stop_repair_worker()
        repair_error = self._repair_error
        self._repair_error = None
        self._drop_existing(context.env)
        context.env.clear_secondary_endpoint()
        if repair_error is not None:
            raise RuntimeError(f"HC02 repair worker failed: {repair_error}") from repair_error

    def _configure(self, config: Mapping[str, object]) -> None:
        self.primary_schema = validate_sql_identifier(str(config["primary_schema"]), "primary_schema")
        self.secondary_schema = validate_sql_identifier(str(config["secondary_schema"]), "secondary_schema")
        self.ops_schema = validate_sql_identifier(str(config["ops_schema"]), "ops_schema")
        self.syncpoint_id = str(config["syncpoint_id"])
        self.audit_key = str(config["audit_key"])
        self.audit_request = str(config["audit_request"])
        self.audit_request_queue_table = validate_sql_identifier(
            str(config["audit_request_queue_table"]), "audit_request_queue_table"
        )
        self.release_consumer = str(config["release_consumer"])
        self.audit_window_label = str(config["audit_window_label"])
        self.order_table = validate_sql_identifier(str(config["order_table"]), "order_table")
        self.item_table = validate_sql_identifier(str(config["item_table"]), "item_table")
        self.gc_setting = str(config["gc_setting"])
        self.original_gc_life_time = str(config["original_gc_life_time"])
        self.temporary_gc_life_time = str(config["temporary_gc_life_time"])
        self.secondary_port_offset = int(config["secondary_port_offset"])
        self.primary_tso = int(config["primary_tso"])
        self.secondary_tso = int(config["secondary_tso"])
        self.external_tso = int(config["external_tso"])
        self.syncpoint_order_count = int(config["syncpoint_order_count"])
        self.syncpoint_order_diff_rows = int(config["syncpoint_order_diff_rows"])
        self.syncpoint_item_count = int(config["syncpoint_item_count"])
        self.syncpoint_item_checksum_match = int(config["syncpoint_item_checksum_match"])
        self.syncpoint_item_diff_rows = int(config["syncpoint_item_diff_rows"])
        self.order_item_orphan_rows = int(config["order_item_orphan_rows"])
        self.release_allowed = int(config["release_allowed"])
        self.live_primary_extra_orders = int(config["live_primary_extra_orders"])
        self.noise_event_count = int(config["noise_event_count"])
        self.repair_lease_id = str(config["repair_lease_id"])
        self.repair_lease_id_2 = str(config["repair_lease_id_2"])
        self.repair_lease_table = validate_sql_identifier(
            str(config["repair_lease_table"]), "repair_lease_table"
        )
        self.repair_request_table = validate_sql_identifier(
            str(config["repair_request_table"]), "repair_request_table"
        )
        self.repair_worker_table = validate_sql_identifier(
            str(config["repair_worker_table"]), "repair_worker_table"
        )
        self.repair_item_id = str(config["repair_item_id"])
        self.repair_item_id_2 = str(config["repair_item_id_2"])
        self.repair_count = int(config["repair_count"])
        self.repair_decoy_lease_count = int(config["repair_decoy_lease_count"])
        self.repair_same_row_decoy_count = int(config["repair_same_row_decoy_count"])
        self.repair_delay_seconds = float(config["repair_delay_seconds"])

    def _start_repair_worker(self, env, run_id: str) -> None:
        if self._repair_thread is not None:
            raise RuntimeError(
                f"HC02 repair worker is already running: run_id={run_id!r}, "
                f"thread={self._repair_thread.name!r}"
            )
        self._repair_error = None
        self._repair_stop.clear()
        require_sql_success(
            env.execute_sql(
                f"UPDATE {self.ops_schema}.{self.repair_worker_table} "
                "SET service_state = 'running', last_poll_at = NOW(), last_error = NULL "
                "WHERE worker_name = 'hc02_repair_worker'"
            ),
            "start HC02 repair worker status",
        )
        self._repair_thread = threading.Thread(
            target=self._repair_worker_loop,
            args=(env, run_id),
            name=f"hc02-repair-worker-{run_id}",
            daemon=True,
        )
        self._repair_thread.start()

    def _stop_repair_worker(self) -> None:
        if self._repair_thread is None:
            return
        self._repair_stop.set()
        join_thread(self._repair_thread, 15.0, "HC02 repair worker")
        self._repair_thread = None

    def _repair_worker_loop(self, env, run_id: str) -> None:
        connection = None
        try:
            connection = connect_tidb(
                env,
                database=self.ops_schema,
                autocommit=True,
                application_name=f"hc02-repair-worker-{run_id}",
                read_timeout=30,
                write_timeout=30,
            )
            while not self._repair_stop.wait(0.25):
                self._repair_worker_tick(connection)
        except Exception as exc:
            self._repair_error = exc
            self._repair_stop.set()
            if connection is not None:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"UPDATE {self.repair_worker_table} SET service_state = 'failed', "
                        "last_error = %s WHERE worker_name = 'hc02_repair_worker'",
                        (str(exc),),
                    )
        finally:
            if connection is not None:
                connection.close()

    def _repair_worker_tick(self, connection) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {self.repair_worker_table} "
                "SET last_poll_at = NOW() WHERE worker_name = 'hc02_repair_worker'"
            )
            cursor.execute(
                f"SELECT request_id, lease_id, audit_key, syncpoint_id, consumer, window_label, "
                f"table_name, row_key, source_schema_name, target_schema_name, source_tso, target_tso, "
                f"source_checksum, target_checksum_before, requested_by, request_state "
                f"FROM {self.repair_request_table} "
                "WHERE request_state = 'submitted' "
                f"AND audit_key = %s AND syncpoint_id = %s AND consumer = %s AND window_label = %s "
                "ORDER BY submitted_at, request_id LIMIT 1",
                (self.audit_key, self.syncpoint_id, self.release_consumer, self.audit_window_label),
            )
            request = cursor.fetchone()
            if request is None:
                return
            request_id = str(request[0])
            cursor.execute(
                f"UPDATE {self.repair_request_table} "
                "SET request_state = 'running', started_at = NOW() "
                "WHERE request_id = %s AND request_state = 'submitted'",
                (request_id,),
            )
            if cursor.rowcount != 1:
                return

            lease = self._read_repair_lease(cursor, str(request[1]))
            validation_error = self._validate_repair_request(request, lease, cursor)
            if validation_error is not None:
                self._fail_repair_request(cursor, request_id, validation_error[0], validation_error[1])
                return
            row_key = str(request[7])

            if self._repair_stop.wait(self.repair_delay_seconds):
                return

            cursor.execute(
                f"SELECT "
                "CRC32(CONCAT_WS('#', p.item_id, p.order_id, p.sku_id, p.quantity, p.item_amount_cents, p.updated_at, p.payload_crc)), "
                "CRC32(CONCAT_WS('#', s.item_id, s.order_id, s.sku_id, s.quantity, s.item_amount_cents, s.updated_at, s.payload_crc)) "
                f"FROM {self.primary_schema}.{self.item_table} AS p "
                f"JOIN {self.secondary_schema}.{self.item_table} AS s ON s.item_id = p.item_id "
                "WHERE p.item_id = %s AND p.commit_tso <= %s AND s.commit_tso <= %s",
                (row_key, self.primary_tso, self.secondary_tso),
            )
            checksums = cursor.fetchall()
            if len(checksums) != 1:
                self._fail_repair_request(
                    cursor,
                    request_id,
                    "ROW_NOT_UNIQUE",
                    f"mapped repair row must have exactly one source/target pair: rows={checksums!r}",
                )
                return
            source_checksum, target_checksum = (int(value) for value in checksums[0])
            if source_checksum != int(request[12]) or target_checksum != int(request[13]):
                self._fail_repair_request(
                    cursor,
                    request_id,
                    "FINGERPRINT_CHANGED",
                    "source or target row checksum changed after request submission",
                )
                return
            if source_checksum == target_checksum:
                self._fail_repair_request(
                    cursor,
                    request_id,
                    "NO_MAPPED_DRIFT",
                    f"repair request does not target a mapped row drift: request_id={request_id!r}, row_key={row_key!r}",
                )
                return

            connection.begin()
            try:
                cursor.execute(
                    f"UPDATE {self.secondary_schema}.{self.item_table} AS target "
                    f"JOIN {self.primary_schema}.{self.item_table} AS source "
                    "ON source.item_id = target.item_id "
                    "SET target.order_id = source.order_id, target.sku_id = source.sku_id, "
                    "target.quantity = source.quantity, target.item_amount_cents = source.item_amount_cents, "
                    "target.updated_at = source.updated_at, target.payload_crc = source.payload_crc "
                    "WHERE target.item_id = %s AND source.commit_tso <= %s AND target.commit_tso <= %s",
                    (row_key, self.primary_tso, self.secondary_tso),
                )
                applied_rows = cursor.rowcount
                if applied_rows != 1:
                    raise RuntimeError(
                        "HC02 repair worker expected one changed target row: "
                        f"request_id={request_id!r}, applied_rows={applied_rows}"
                    )
                cursor.execute(
                    f"SELECT "
                    "CRC32(CONCAT_WS('#', p.item_id, p.order_id, p.sku_id, p.quantity, p.item_amount_cents, p.updated_at, p.payload_crc)), "
                    "CRC32(CONCAT_WS('#', s.item_id, s.order_id, s.sku_id, s.quantity, s.item_amount_cents, s.updated_at, s.payload_crc)) "
                    f"FROM {self.primary_schema}.{self.item_table} AS p "
                    f"JOIN {self.secondary_schema}.{self.item_table} AS s ON s.item_id = p.item_id "
                    "WHERE p.item_id = %s AND p.commit_tso <= %s AND s.commit_tso <= %s",
                    (row_key, self.primary_tso, self.secondary_tso),
                )
                after_checksums = cursor.fetchall()
                if len(after_checksums) != 1 or int(after_checksums[0][0]) != int(after_checksums[0][1]):
                    raise RuntimeError(
                        "HC02 repair worker postcondition failed: "
                        f"request_id={request_id!r}, checksums={after_checksums!r}"
                    )
                cursor.execute(
                    f"UPDATE {self.repair_request_table} "
                    "SET request_state = 'succeeded', finished_at = NOW(), applied_rows = 1, "
                    "error_code = NULL, error_message = NULL "
                    "WHERE request_id = %s",
                    (request_id,),
                )
                cursor.execute(
                    f"UPDATE {self.repair_lease_table} "
                    "SET lease_state = 'consumed', consumed_at = NOW() "
                    "WHERE lease_id = %s AND lease_state = 'claimed'",
                    (str(request[1]),),
                )
                cursor.execute(
                    f"UPDATE {self.repair_worker_table} "
                    "SET processed_requests = processed_requests + 1, last_request_id = %s "
                    "WHERE worker_name = 'hc02_repair_worker'",
                    (request_id,),
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    def _read_repair_lease(self, cursor, lease_id: str):
        cursor.execute(
            f"SELECT lease_id, audit_key, syncpoint_id, consumer, window_label, table_name, row_key, "
            f"source_schema_name, target_schema_name, source_tso, target_tso, expected_source_checksum, "
            f"expected_target_checksum, lease_state, expires_at "
            f"FROM {self.repair_lease_table} WHERE lease_id = %s",
            (lease_id,),
        )
        rows = cursor.fetchall()
        return rows[0] if len(rows) == 1 else None

    def _validate_repair_request(self, request, lease, cursor):
        if lease is None:
            return "LEASE_NOT_FOUND", f"repair lease does not exist: request_id={request[0]!r}, lease_id={request[1]!r}"
        expected_request = (
            self.audit_key,
            self.syncpoint_id,
            self.release_consumer,
            self.audit_window_label,
            self.item_table,
            str(request[7]),
            self.primary_schema,
            self.secondary_schema,
            self.primary_tso,
            self.secondary_tso,
        )
        observed_request = tuple(request[index] for index in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11))
        observed_lease = tuple(lease[index] for index in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
        if observed_request != expected_request or observed_lease != expected_request:
            return "REQUEST_SCOPE_MISMATCH", (
                "repair request or lease scope does not match the active release binding: "
                f"request_id={request[0]!r}, observed_request={observed_request!r}, observed_lease={observed_lease!r}, "
                f"expected={expected_request!r}"
            )
        if (
            int(request[12]) != int(lease[11])
            or int(request[13]) != int(lease[12])
        ):
            return "LEASE_FINGERPRINT_MISMATCH", (
                "repair request fingerprints do not match the claimed lease: "
                f"request_id={request[0]!r}, request_checksums={(request[12], request[13])!r}, "
                f"lease_checksums={(lease[11], lease[12])!r}"
            )
        if str(lease[13]).casefold() != "claimed":
            return "LEASE_NOT_CLAIMED", f"repair lease is not claimed: lease_id={lease[0]!r}, state={lease[13]!r}"
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.ops_schema}.audit_syncpoint_bindings AS b "
            f"JOIN {self.ops_schema}.audit_window_catalog AS w "
            "ON w.request_id = %s AND w.audit_key = b.audit_key AND w.consumer = b.consumer "
            "AND w.window_label = b.window_label AND w.release_state = 'open' "
            f"JOIN {self.ops_schema}.{self.audit_request_queue_table} AS q "
            "ON q.request_id = w.request_id AND q.audit_key = w.audit_key "
            "AND q.consumer = w.consumer AND q.target_window = w.window_label "
            "AND q.request_state = 'awaiting_audit' AND q.priority = 'release' "
            "WHERE b.audit_key = %s AND b.syncpoint_id = %s AND b.consumer = %s "
            "AND b.window_label = %s AND b.binding_state = 'active' AND b.released_at IS NULL",
            (
                self.audit_request,
                self.audit_key,
                self.syncpoint_id,
                self.release_consumer,
                self.audit_window_label,
            ),
        )
        binding_rows = cursor.fetchone()[0]
        if int(binding_rows) != 1:
            return "BINDING_CHANGED", f"active release binding is no longer unique: rows={binding_rows}"
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.repair_lease_table} "
            "WHERE lease_id = %s AND lease_state = 'claimed' AND expires_at > NOW()",
            (str(lease[0]),),
        )
        if int(cursor.fetchone()[0]) != 1:
            return "LEASE_EXPIRED", f"repair lease is expired or not claimed: lease_id={lease[0]!r}"
        return None

    def _fail_repair_request(self, cursor, request_id: str, error_code: str, error_message: str) -> None:
        cursor.execute(
            f"UPDATE {self.repair_request_table} "
            "SET request_state = 'failed', finished_at = NOW(), applied_rows = 0, "
            "error_code = %s, error_message = %s WHERE request_id = %s",
            (error_code, error_message, request_id),
        )

    def _drop_existing(self, env) -> None:
        for schema in (self.primary_schema, self.secondary_schema, self.ops_schema):
            require_sql_success(env.execute_sql(f"DROP DATABASE IF EXISTS {schema}"), f"drop schema {schema}")

    def _create_schemas(self, env) -> None:
        for schema in (self.primary_schema, self.secondary_schema, self.ops_schema):
            require_sql_success(env.execute_sql(f"CREATE DATABASE {schema}"), f"create schema {schema}")

    def _create_business_tables(self, env) -> None:
        order_columns = (
            "order_id VARCHAR(64) PRIMARY KEY, "
            "customer_id BIGINT NOT NULL, "
            "region_code VARCHAR(12) NOT NULL, "
            "order_status VARCHAR(24) NOT NULL, "
            "amount_cents BIGINT NOT NULL, "
            "commit_tso BIGINT NOT NULL, "
            "updated_at DATETIME NOT NULL, "
            "payload_crc BIGINT NOT NULL"
        )
        item_columns = (
            "item_id VARCHAR(64) PRIMARY KEY, "
            "order_id VARCHAR(64) NOT NULL, "
            "sku_id BIGINT NOT NULL, "
            "quantity INT NOT NULL, "
            "item_amount_cents BIGINT NOT NULL, "
            "commit_tso BIGINT NOT NULL, "
            "updated_at DATETIME NOT NULL, "
            "payload_crc BIGINT NOT NULL"
        )
        for schema in (self.primary_schema, self.secondary_schema):
            require_sql_success(
                env.execute_sql(f"CREATE TABLE {schema}.{self.order_table} ({order_columns})"),
                f"create {schema}.{self.order_table}",
            )
            require_sql_success(
                env.execute_sql(f"CREATE INDEX idx_{self.order_table}_commit_tso ON {schema}.{self.order_table}(commit_tso)"),
                f"index {schema}.{self.order_table}.commit_tso",
            )
            require_sql_success(
                env.execute_sql(f"CREATE TABLE {schema}.{self.item_table} ({item_columns})"),
                f"create {schema}.{self.item_table}",
            )
            require_sql_success(
                env.execute_sql(f"CREATE INDEX idx_{self.item_table}_commit_tso ON {schema}.{self.item_table}(commit_tso)"),
                f"index {schema}.{self.item_table}.commit_tso",
            )
            require_sql_success(
                env.execute_sql(
                    f"CREATE TABLE {schema}.inventory_reservations ("
                    "reservation_id VARCHAR(64) PRIMARY KEY, sku_id BIGINT, warehouse_id BIGINT, "
                    "quantity INT, commit_tso BIGINT, updated_at DATETIME, payload_crc BIGINT)"
                ),
                f"create {schema}.inventory_reservations",
            )

    def _load_syncpoint_rows(self, env) -> None:
        primary_orders = []
        secondary_orders = []
        primary_items = []
        secondary_items = []
        for i in range(1, self.syncpoint_order_count + 1):
            order_id = f"ord-{i:05d}"
            customer_id = 1000 + (i % 57)
            region = ("EAST", "WEST", "NORTH", "SOUTH")[i % 4]
            status = ("paid", "packed", "shipped")[i % 3]
            amount = 1500 + i * 37
            primary_commit = self.primary_tso - (self.syncpoint_order_count - i + 1) * 9
            secondary_commit = self.secondary_tso - (self.syncpoint_order_count - i + 1) * 11
            updated_at = f"2026-08-01 09:{i % 60:02d}:{(i * 7) % 60:02d}"
            payload_crc = (i * 2654435761) % 4294967295
            business = (order_id, customer_id, region, status, amount, updated_at, payload_crc)
            primary_orders.append((*business[:5], primary_commit, business[5], business[6]))
            secondary_orders.append((*business[:5], secondary_commit, business[5], business[6]))
            if len(primary_items) >= self.syncpoint_item_count:
                continue
            item_count = 2 + (i % 2)
            for j in range(1, item_count + 1):
                if len(primary_items) >= self.syncpoint_item_count:
                    break
                item_index = len(primary_items) + 1
                item_id = f"itm-{i:05d}-{j}"
                sku_id = 20000 + ((i * 13 + j) % 997)
                quantity = 1 + ((i + j) % 4)
                item_amount = amount // item_count + j
                item_crc = (item_index * 11400714819323198485) % 4294967295
                primary_items.append((item_id, order_id, sku_id, quantity, item_amount, primary_commit, updated_at, item_crc))
                secondary_items.append((item_id, order_id, sku_id, quantity, item_amount, secondary_commit, updated_at, item_crc))
        self._insert_rows(
            env,
            f"{self.primary_schema}.{self.order_table}",
            ("order_id", "customer_id", "region_code", "order_status", "amount_cents", "commit_tso", "updated_at", "payload_crc"),
            primary_orders,
        )
        self._insert_rows(
            env,
            f"{self.secondary_schema}.{self.order_table}",
            ("order_id", "customer_id", "region_code", "order_status", "amount_cents", "commit_tso", "updated_at", "payload_crc"),
            secondary_orders,
        )
        self._insert_rows(
            env,
            f"{self.primary_schema}.{self.item_table}",
            ("item_id", "order_id", "sku_id", "quantity", "item_amount_cents", "commit_tso", "updated_at", "payload_crc"),
            primary_items[: self.syncpoint_item_count],
        )
        self._insert_rows(
            env,
            f"{self.secondary_schema}.{self.item_table}",
            ("item_id", "order_id", "sku_id", "quantity", "item_amount_cents", "commit_tso", "updated_at", "payload_crc"),
            secondary_items[: self.syncpoint_item_count],
        )
        require_sql_success(
            env.execute_sql(
                f"UPDATE {self.secondary_schema}.{self.item_table} "
                f"SET quantity = quantity + 1 WHERE item_id = {sql_literal(self.repair_item_id)}"
            ),
            "inject first mapped-TSO order-item drift",
        )
        require_sql_success(
            env.execute_sql(
                f"UPDATE {self.secondary_schema}.{self.item_table} "
                f"SET item_amount_cents = item_amount_cents + 7 WHERE item_id = {sql_literal(self.repair_item_id_2)}"
            ),
            "inject second mapped-TSO order-item drift",
        )

    def _load_live_primary_rows(self, env) -> None:
        orders = []
        items = []
        for i in range(1, self.live_primary_extra_orders + 1):
            order_id = f"live-seeded-{i:04d}"
            commit_tso = self.primary_tso + i * 19
            updated_at = f"2026-08-01 10:{i % 60:02d}:{(i * 5) % 60:02d}"
            orders.append((order_id, 9000 + i, "EAST", "paid", 9000 + i * 17, commit_tso, updated_at, i * 1999))
            items.append((f"live-seeded-item-{i:04d}", order_id, 88000 + i, 1, 9000 + i * 17, commit_tso, updated_at, i * 2999))
        self._insert_rows(
            env,
            f"{self.primary_schema}.{self.order_table}",
            ("order_id", "customer_id", "region_code", "order_status", "amount_cents", "commit_tso", "updated_at", "payload_crc"),
            orders,
        )
        self._insert_rows(
            env,
            f"{self.primary_schema}.{self.item_table}",
            ("item_id", "order_id", "sku_id", "quantity", "item_amount_cents", "commit_tso", "updated_at", "payload_crc"),
            items,
        )

    def _create_ops_tables(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.ops_schema}.syncpoint_map ("
                "syncpoint_id VARCHAR(64) PRIMARY KEY, primary_schema_name VARCHAR(64), secondary_schema_name VARCHAR(64), "
                "primary_tso BIGINT, secondary_tso BIGINT, external_tso BIGINT, state VARCHAR(32), "
                "captured_at DATETIME, confidence VARCHAR(32), note VARCHAR(512))"
            ),
            "create syncpoint_map",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.ops_schema}.syncpoint_map VALUES "
                f"('{self.syncpoint_id}', '{self.primary_schema}', '{self.secondary_schema}', "
                f"{self.primary_tso}, {self.secondary_tso}, {self.external_tso}, 'stable', "
                "'2026-08-01 10:20:00', 'operator_verified', "
                "'Checkpoint capture from the upstream/downstream observer.')"
            ),
            "insert syncpoint_map",
        )
        decoy_syncpoints = (
            (
                f"{self.syncpoint_id}_probe",
                self.primary_schema,
                self.secondary_schema,
                self.primary_tso + 100,
                self.secondary_tso + 100,
                self.primary_tso + 50,
                "stable",
                "2026-08-01 10:21:00",
                "probe_only",
                "Checkpoint capture from the observer.",
            ),
            (
                f"{self.syncpoint_id}_stale",
                self.primary_schema,
                self.secondary_schema,
                self.primary_tso - 4000,
                self.secondary_tso - 4000,
                self.primary_tso - 4001,
                "stable",
                "2026-08-01 10:19:00",
                "operator_verified",
                "Checkpoint capture from the observer.",
            ),
            (
                f"{self.syncpoint_id}_pending",
                self.primary_schema,
                self.secondary_schema,
                self.primary_tso + 200,
                self.secondary_tso + 200,
                self.primary_tso + 300,
                "pending",
                "2026-08-01 10:22:00",
                "operator_verified",
                "Checkpoint capture from the observer.",
            ),
            (
                f"{self.syncpoint_id}_expired",
                self.primary_schema,
                self.secondary_schema,
                self.primary_tso - 8000,
                self.secondary_tso - 8000,
                self.primary_tso - 7000,
                "expired",
                "2026-08-01 09:58:00",
                "operator_verified",
                "Checkpoint capture from the observer.",
            ),
            (
                f"{self.syncpoint_id}_inventory",
                self.primary_schema,
                self.secondary_schema,
                self.primary_tso + 9000,
                self.secondary_tso + 9000,
                self.primary_tso + 10000,
                "stable",
                "2026-08-01 10:31:00",
                "operator_verified",
                "Checkpoint capture from the observer.",
            ),
        )
        self._insert_rows(
            env,
            f"{self.ops_schema}.syncpoint_map",
            (
                "syncpoint_id", "primary_schema_name", "secondary_schema_name", "primary_tso",
                "secondary_tso", "external_tso", "state", "captured_at", "confidence", "note",
            ),
            decoy_syncpoints,
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.ops_schema}.{self.audit_request_queue_table} ("
                "request_id VARCHAR(64) PRIMARY KEY, audit_key VARCHAR(64), consumer VARCHAR(64), "
                "target_window VARCHAR(128), request_state VARCHAR(32), priority VARCHAR(32), "
                "requested_at DATETIME, requested_by VARCHAR(64), note VARCHAR(256))"
            ),
            "create audit_request_queue",
        )
        self._insert_rows(
            env,
            f"{self.ops_schema}.{self.audit_request_queue_table}",
            (
                "request_id", "audit_key", "consumer", "target_window", "request_state", "priority",
                "requested_at", "requested_by", "note",
            ),
            (
                (
                    self.audit_request,
                    self.audit_key,
                    self.release_consumer,
                    self.audit_window_label,
                    "awaiting_audit",
                    "release",
                    "2026-08-01 10:24:00",
                    "inventory-control",
                    "queue record",
                ),
                (
                    f"{self.audit_request}_replay",
                    f"{self.audit_key}_replay",
                    self.release_consumer,
                    "retail_orders_20260801_1000_replay",
                    "awaiting_audit",
                    "replay",
                    "2026-08-01 10:25:00",
                    "inventory-control",
                    "queue record",
                ),
                (
                    f"{self.audit_request}_backfill",
                    f"{self.audit_key}_backfill",
                    self.release_consumer,
                    "retail_orders_20260801_0950",
                    "awaiting_audit",
                    "backfill",
                    "2026-08-01 10:26:00",
                    "inventory-control",
                    "queue record",
                ),
                (
                    f"{self.audit_request}_projection",
                    f"{self.audit_key}_inventory",
                    "inventory_projection",
                    "inventory_projection_20260801_1030",
                    "awaiting_audit",
                    "refresh",
                    "2026-08-01 10:31:00",
                    "projection-worker",
                    "queue record",
                ),
                (
                    f"{self.audit_request}_closed",
                    f"{self.audit_key}_previous",
                    self.release_consumer,
                    "retail_orders_20260801_0900",
                    "cancelled",
                    "release",
                    "2026-08-01 09:10:00",
                    "inventory-control",
                    "queue record",
                ),
                (
                    f"{self.audit_request}_shadow",
                    f"{self.audit_key}_shadow",
                    self.release_consumer,
                    self.audit_window_label,
                    "shadow",
                    "release",
                    "2026-08-01 10:24:30",
                    "inventory-control",
                    "queue record",
                ),
                (
                    f"{self.audit_request}_nightly",
                    f"{self.audit_key}_nightly",
                    self.release_consumer,
                    "retail_orders_20260731_2300",
                    "completed",
                    "release",
                    "2026-07-31 23:05:00",
                    "inventory-control",
                    "queue record",
                ),
                (
                    f"{self.audit_request}_adhoc",
                    f"{self.audit_key}_adhoc",
                    self.release_consumer,
                    "retail_orders_20260801_1015",
                    "rejected",
                    "adhoc",
                    "2026-08-01 10:15:00",
                    "inventory-control",
                    "queue record",
                ),
            ),
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.ops_schema}.audit_window_catalog ("
                "request_id VARCHAR(64) PRIMARY KEY, consumer VARCHAR(64), window_label VARCHAR(128), "
                "release_state VARCHAR(32), audit_key VARCHAR(64), requested_at DATETIME, note VARCHAR(512))"
            ),
            "create audit_window_catalog",
        )
        self._insert_rows(
            env,
            f"{self.ops_schema}.audit_window_catalog",
            ("request_id", "consumer", "window_label", "release_state", "audit_key", "requested_at", "note"),
            (
                (
                    self.audit_request,
                    self.release_consumer,
                    self.audit_window_label,
                    "open",
                    self.audit_key,
                    "2026-08-01 10:24:00",
                    "Queue-controlled audit window.",
                ),
                (
                    f"{self.audit_request}_projection",
                    "inventory_projection",
                    "inventory_projection_20260801_1030",
                    "open",
                    f"{self.audit_key}_inventory",
                    "2026-08-01 10:31:00",
                    "Queue-controlled audit window.",
                ),
                (
                    f"{self.audit_request}_closed",
                    self.release_consumer,
                    "retail_orders_20260801_0900",
                    "closed",
                    f"{self.audit_key}_previous",
                    "2026-08-01 09:10:00",
                    "Queue-controlled audit window.",
                ),
                (
                    f"{self.audit_request}_shadow",
                    self.release_consumer,
                    self.audit_window_label,
                    "shadow",
                    f"{self.audit_key}_shadow",
                    "2026-08-01 10:24:30",
                    "Queue-controlled audit window.",
                ),
                (
                    f"{self.audit_request}_replay",
                    self.release_consumer,
                    "retail_orders_20260801_1000_replay",
                    "open",
                    f"{self.audit_key}_replay",
                    "2026-08-01 10:25:00",
                    "Queue-controlled audit window.",
                ),
                (
                    f"{self.audit_request}_backfill",
                    self.release_consumer,
                    "retail_orders_20260801_0950",
                    "open",
                    f"{self.audit_key}_backfill",
                    "2026-08-01 10:26:00",
                    "Queue-controlled audit window.",
                ),
            ),
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.ops_schema}.audit_syncpoint_bindings ("
                "binding_id BIGINT PRIMARY KEY, audit_key VARCHAR(64), syncpoint_id VARCHAR(64), "
                "consumer VARCHAR(64), window_label VARCHAR(128), binding_state VARCHAR(32), "
                "bound_at DATETIME, released_at DATETIME NULL, note VARCHAR(512))"
            ),
            "create audit_syncpoint_bindings",
        )
        self._insert_rows(
            env,
            f"{self.ops_schema}.audit_syncpoint_bindings",
            (
                "binding_id", "audit_key", "syncpoint_id", "consumer", "window_label",
                "binding_state", "bound_at", "released_at", "note",
            ),
            (
                (
                    1001,
                    self.audit_key,
                    self.syncpoint_id,
                    self.release_consumer,
                    self.audit_window_label,
                    "active",
                    "2026-08-01 10:20:00",
                    None,
                    "Binding history record.",
                ),
                (
                    1002,
                    self.audit_key,
                    f"{self.syncpoint_id}_inventory",
                    "inventory_projection",
                    "inventory_projection_20260801_1030",
                    "active",
                    "2026-08-01 10:31:00",
                    None,
                    "Binding history record.",
                ),
                (
                    1003,
                    self.audit_key,
                    f"{self.syncpoint_id}_probe",
                    self.release_consumer,
                    self.audit_window_label,
                    "superseded",
                    "2026-08-01 10:21:00",
                    "2026-08-01 10:22:00",
                    "Binding history record.",
                ),
                (
                    1004,
                    self.audit_key,
                    f"{self.syncpoint_id}_stale",
                    self.release_consumer,
                    "retail_orders_20260801_0900",
                    "expired",
                    "2026-08-01 09:00:00",
                    "2026-08-01 10:00:00",
                    "Binding history record.",
                ),
                (
                    1005,
                    f"{self.audit_key}_replay",
                    f"{self.syncpoint_id}_probe",
                    self.release_consumer,
                    "retail_orders_20260801_1000_replay",
                    "active",
                    "2026-08-01 10:25:00",
                    None,
                    "Binding history record.",
                ),
                (
                    1006,
                    f"{self.audit_key}_backfill",
                    f"{self.syncpoint_id}_inventory",
                    self.release_consumer,
                    "retail_orders_20260801_0950",
                    "active",
                    "2026-08-01 10:26:00",
                    None,
                    "Binding history record.",
                ),
            ),
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.ops_schema}.{self.repair_lease_table} ("
                "lease_id VARCHAR(64) PRIMARY KEY, audit_key VARCHAR(64), syncpoint_id VARCHAR(64), "
                "consumer VARCHAR(64), window_label VARCHAR(128), table_name VARCHAR(64), "
                "row_key VARCHAR(128), source_schema_name VARCHAR(64), target_schema_name VARCHAR(64), "
                "source_tso BIGINT, target_tso BIGINT, expected_source_checksum BIGINT, "
                "expected_target_checksum BIGINT, lease_state VARCHAR(16), expires_at DATETIME, "
                "claimed_by VARCHAR(64) NULL, claimed_at DATETIME NULL, consumed_at DATETIME NULL, "
                "note VARCHAR(512))"
            ),
            "create repair leases",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.ops_schema}.{self.repair_lease_table} ("
                "lease_id, audit_key, syncpoint_id, consumer, window_label, table_name, row_key, "
                "source_schema_name, target_schema_name, source_tso, target_tso, "
                "expected_source_checksum, expected_target_checksum, lease_state, expires_at, note) "
                f"SELECT {sql_literal(self.repair_lease_id)}, {sql_literal(self.audit_key)}, "
                f"{sql_literal(self.syncpoint_id)}, {sql_literal(self.release_consumer)}, "
                f"{sql_literal(self.audit_window_label)}, {sql_literal(self.item_table)}, "
                f"{sql_literal(self.repair_item_id)}, {sql_literal(self.primary_schema)}, "
                f"{sql_literal(self.secondary_schema)}, {self.primary_tso}, {self.secondary_tso}, "
                "CRC32(CONCAT_WS('#', p.item_id, p.order_id, p.sku_id, p.quantity, "
                "p.item_amount_cents, p.updated_at, p.payload_crc)), "
                "CRC32(CONCAT_WS('#', s.item_id, s.order_id, s.sku_id, s.quantity, "
                "s.item_amount_cents, s.updated_at, s.payload_crc)), "
                "'issued', DATE_ADD(NOW(), INTERVAL 30 MINUTE), "
                "'issued authorization record' "
                f"FROM {self.primary_schema}.{self.item_table} AS p "
                f"JOIN {self.secondary_schema}.{self.item_table} AS s ON s.item_id = p.item_id "
                f"WHERE p.item_id = {sql_literal(self.repair_item_id)} "
                f"AND p.commit_tso <= {self.primary_tso} AND s.commit_tso <= {self.secondary_tso}"
            ),
            "insert current repair lease",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.ops_schema}.{self.repair_lease_table} ("
                "lease_id, audit_key, syncpoint_id, consumer, window_label, table_name, row_key, "
                "source_schema_name, target_schema_name, source_tso, target_tso, "
                "expected_source_checksum, expected_target_checksum, lease_state, expires_at, note) "
                f"SELECT {sql_literal(self.repair_lease_id_2)}, {sql_literal(self.audit_key)}, "
                f"{sql_literal(self.syncpoint_id)}, {sql_literal(self.release_consumer)}, "
                f"{sql_literal(self.audit_window_label)}, {sql_literal(self.item_table)}, "
                f"{sql_literal(self.repair_item_id_2)}, {sql_literal(self.primary_schema)}, "
                f"{sql_literal(self.secondary_schema)}, {self.primary_tso}, {self.secondary_tso}, "
                "CRC32(CONCAT_WS('#', p.item_id, p.order_id, p.sku_id, p.quantity, "
                "p.item_amount_cents, p.updated_at, p.payload_crc)), "
                "CRC32(CONCAT_WS('#', s.item_id, s.order_id, s.sku_id, s.quantity, "
                "s.item_amount_cents, s.updated_at, s.payload_crc)), "
                "'issued', DATE_ADD(NOW(), INTERVAL 30 MINUTE), "
                "'issued authorization record' "
                f"FROM {self.primary_schema}.{self.item_table} AS p "
                f"JOIN {self.secondary_schema}.{self.item_table} AS s ON s.item_id = p.item_id "
                f"WHERE p.item_id = {sql_literal(self.repair_item_id_2)} "
                f"AND p.commit_tso <= {self.primary_tso} AND s.commit_tso <= {self.secondary_tso}"
            ),
            "insert second current repair lease",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.ops_schema}.{self.repair_lease_table} ("
                "lease_id, audit_key, syncpoint_id, consumer, window_label, table_name, row_key, "
                "source_schema_name, target_schema_name, source_tso, target_tso, "
                "expected_source_checksum, expected_target_checksum, lease_state, expires_at, note) "
                f"SELECT CONCAT('auth_', LEFT(MD5(CONCAT(p.item_id, ':healthy')), 12)), {sql_literal(self.audit_key)}, "
                f"{sql_literal(self.syncpoint_id)}, {sql_literal(self.release_consumer)}, "
                f"{sql_literal(self.audit_window_label)}, {sql_literal(self.item_table)}, p.item_id, "
                f"{sql_literal(self.primary_schema)}, {sql_literal(self.secondary_schema)}, "
                f"{self.primary_tso}, {self.secondary_tso}, "
                "CRC32(CONCAT_WS('#', p.item_id, p.order_id, p.sku_id, p.quantity, "
                "p.item_amount_cents, p.updated_at, p.payload_crc)), "
                "CRC32(CONCAT_WS('#', s.item_id, s.order_id, s.sku_id, s.quantity, "
                "s.item_amount_cents, s.updated_at, s.payload_crc)), "
                "'issued', DATE_ADD(NOW(), INTERVAL 30 MINUTE), 'issued authorization record' "
                f"FROM {self.primary_schema}.{self.item_table} AS p "
                f"JOIN {self.secondary_schema}.{self.item_table} AS s ON s.item_id = p.item_id "
                f"WHERE p.item_id NOT IN ({sql_literal(self.repair_item_id)}, {sql_literal(self.repair_item_id_2)}) "
                f"AND p.commit_tso <= {self.primary_tso} AND s.commit_tso <= {self.secondary_tso} "
                f"ORDER BY p.item_id LIMIT {self.repair_decoy_lease_count}"
            ),
            "insert current-scope repair authorization noise",
        )
        current_item_ids_sql = ", ".join(
            sql_literal(item_id) for item_id in (self.repair_item_id, self.repair_item_id_2)
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.ops_schema}.{self.repair_lease_table} ("
                "lease_id, audit_key, syncpoint_id, consumer, window_label, table_name, row_key, "
                "source_schema_name, target_schema_name, source_tso, target_tso, "
                "expected_source_checksum, expected_target_checksum, lease_state, expires_at, note) "
                f"SELECT CONCAT('auth_', LEFT(MD5(CONCAT(p.item_id, ':equal')), 12)), {sql_literal(self.audit_key)}, "
                f"{sql_literal(self.syncpoint_id)}, {sql_literal(self.release_consumer)}, "
                f"{sql_literal(self.audit_window_label)}, {sql_literal(self.item_table)}, p.item_id, "
                f"{sql_literal(self.primary_schema)}, {sql_literal(self.secondary_schema)}, "
                f"{self.primary_tso}, {self.secondary_tso}, "
                "CRC32(CONCAT_WS('#', p.item_id, p.order_id, p.sku_id, p.quantity, "
                "p.item_amount_cents, p.updated_at, p.payload_crc)), "
                "CRC32(CONCAT_WS('#', p.item_id, p.order_id, p.sku_id, p.quantity, "
                "p.item_amount_cents, p.updated_at, p.payload_crc)), "
                "'issued', DATE_ADD(NOW(), INTERVAL 30 MINUTE), 'issued authorization record' "
                f"FROM {self.primary_schema}.{self.item_table} AS p "
                f"JOIN {self.secondary_schema}.{self.item_table} AS s ON s.item_id = p.item_id "
                f"WHERE p.item_id IN ({current_item_ids_sql}) "
                f"AND p.commit_tso <= {self.primary_tso} AND s.commit_tso <= {self.secondary_tso}"
            ),
            "insert stale same-row authorization noise",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.ops_schema}.{self.repair_lease_table} ("
                "lease_id, audit_key, syncpoint_id, consumer, window_label, table_name, row_key, "
                "source_schema_name, target_schema_name, source_tso, target_tso, "
                "expected_source_checksum, expected_target_checksum, lease_state, expires_at, note) "
                f"SELECT CONCAT('auth_', LEFT(MD5(CONCAT(p.item_id, ':history:', n.n)), 12)), {sql_literal(self.audit_key)}, "
                f"{sql_literal(self.syncpoint_id)}, {sql_literal(self.release_consumer)}, "
                f"{sql_literal(self.audit_window_label)}, {sql_literal(self.item_table)}, p.item_id, "
                f"{sql_literal(self.primary_schema)}, {sql_literal(self.secondary_schema)}, "
                f"{self.primary_tso}, {self.secondary_tso}, "
                "CRC32(CONCAT_WS('#', p.item_id, p.order_id, p.sku_id, p.quantity, "
                "p.item_amount_cents, p.updated_at, p.payload_crc)), "
                "CRC32(CONCAT_WS('#', s.item_id, s.order_id, s.sku_id, s.quantity + n.n, "
                "s.item_amount_cents, s.updated_at, s.payload_crc)), "
                "'issued', DATE_ADD(NOW(), INTERVAL 30 MINUTE), 'issued authorization record' "
                f"FROM {self.primary_schema}.{self.item_table} AS p "
                f"JOIN {self.secondary_schema}.{self.item_table} AS s ON s.item_id = p.item_id "
                "JOIN (SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 "
                "UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8) AS n "
                f"WHERE p.item_id IN ({current_item_ids_sql}) AND n.n <= {self.repair_same_row_decoy_count} "
                f"AND p.commit_tso <= {self.primary_tso} AND s.commit_tso <= {self.secondary_tso}"
            ),
            "insert same-row historical authorization noise",
        )
        self._insert_rows(
            env,
            f"{self.ops_schema}.{self.repair_lease_table}",
            (
                "lease_id", "audit_key", "syncpoint_id", "consumer", "window_label", "table_name",
                "row_key", "source_schema_name", "target_schema_name", "source_tso", "target_tso",
                "expected_source_checksum", "expected_target_checksum", "lease_state", "expires_at", "note",
            ),
            (
                (
                    "auth_3a8f51d0c742",
                    f"{self.audit_key}_inventory",
                    f"{self.syncpoint_id}_inventory",
                    "inventory_projection",
                    "inventory_projection_20260801_1030",
                    self.item_table,
                    self.repair_item_id,
                    self.primary_schema,
                    self.secondary_schema,
                    self.primary_tso + 9000,
                    self.secondary_tso + 9000,
                    0,
                    0,
                    "issued",
                    "2099-01-01 00:00:00",
                    "Lease belongs to a different consumer and release window.",
                ),
                (
                    "auth_91e6c4b7d208",
                    self.audit_key,
                    f"{self.syncpoint_id}_stale",
                    self.release_consumer,
                    "retail_orders_20260801_0900",
                    self.item_table,
                    self.repair_item_id,
                    self.primary_schema,
                    self.secondary_schema,
                    self.primary_tso - 4000,
                    self.secondary_tso - 4000,
                    0,
                    0,
                    "expired",
                    "2020-01-01 00:00:00",
                    "Historical lease is outside the current release window.",
                ),
            ),
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.ops_schema}.{self.repair_request_table} ("
                "request_id VARCHAR(64) PRIMARY KEY, lease_id VARCHAR(64), audit_key VARCHAR(64), "
                "syncpoint_id VARCHAR(64), consumer VARCHAR(64), window_label VARCHAR(128), "
                "table_name VARCHAR(64), row_key VARCHAR(128), source_schema_name VARCHAR(64), "
                "target_schema_name VARCHAR(64), source_tso BIGINT, target_tso BIGINT, "
                "source_checksum BIGINT, target_checksum_before BIGINT, requested_by VARCHAR(64), "
                "request_state VARCHAR(16), submitted_at DATETIME, started_at DATETIME NULL, "
                "finished_at DATETIME NULL, applied_rows INT, error_code VARCHAR(64) NULL, "
                "error_message VARCHAR(512) NULL)"
            ),
            "create repair requests",
        )
        self._insert_rows(
            env,
            f"{self.ops_schema}.{self.repair_request_table}",
            (
                "request_id", "lease_id", "audit_key", "syncpoint_id", "consumer", "window_label",
                "table_name", "row_key", "source_schema_name", "target_schema_name", "source_tso", "target_tso",
                "source_checksum", "target_checksum_before", "requested_by", "request_state", "submitted_at",
                "started_at", "finished_at", "applied_rows", "error_code", "error_message",
            ),
            (
                (
                    "req_52a7d9c1e804",
                    "auth_3a8f51d0c742",
                    f"{self.audit_key}_inventory",
                    f"{self.syncpoint_id}_inventory",
                    "inventory_projection",
                    "inventory_projection_20260801_1030",
                    self.item_table,
                    self.repair_item_id,
                    self.primary_schema,
                    self.secondary_schema,
                    self.primary_tso + 9000,
                    self.secondary_tso + 9000,
                    0,
                    0,
                    "projection-worker",
                    "succeeded",
                    "2026-08-01 10:31:00",
                    "2026-08-01 10:31:01",
                    "2026-08-01 10:31:02",
                    1,
                    None,
                    "different consumer; not the release repair",
                ),
            ),
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.ops_schema}.{self.repair_worker_table} ("
                "worker_name VARCHAR(64) PRIMARY KEY, service_state VARCHAR(16), poll_interval_ms INT, "
                "last_poll_at DATETIME NULL, processed_requests INT, last_request_id VARCHAR(64) NULL, "
                "last_error VARCHAR(512) NULL)"
            ),
            "create repair worker status",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.ops_schema}.{self.repair_worker_table} VALUES ("
                "'hc02_repair_worker', 'starting', 250, NULL, 0, NULL, NULL)"
            ),
            "insert repair worker status",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.ops_schema}.gc_retention_controls ("
                "setting_name VARCHAR(64) PRIMARY KEY, original_value VARCHAR(32), current_value VARCHAR(32), "
                "temporary_owner VARCHAR(64), reason VARCHAR(256), restored_at DATETIME NULL)"
            ),
            "create gc_retention_controls",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.ops_schema}.gc_retention_controls VALUES "
                f"('{self.gc_setting}', '{self.original_gc_life_time}', '{self.temporary_gc_life_time}', "
                f"'{self.audit_key}', 'preserve syncpoint snapshots during consistency audit', NULL)"
            ),
            "insert gc_retention_controls",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.ops_schema}.audit_runbook_steps ("
                "audit_key VARCHAR(64), step_no INT, step_name VARCHAR(128), details VARCHAR(768), "
                "PRIMARY KEY (audit_key, step_no))"
            ),
            "create audit_runbook_steps",
        )
        runbook_rows = (
            (self.audit_key, 1, "scope_handoff", "Record the request context and the owner of the operational handoff."),
            (self.audit_key, 2, "capture_upstream_state", "Capture the upstream state relevant to the audit window."),
            (self.audit_key, 3, "capture_downstream_state", "Capture the downstream state relevant to the audit window."),
            (self.audit_key, 4, "compare_related_objects", "Compare the related objects and preserve the evidence needed for review."),
            (self.audit_key, 5, "review_operational_records", "Review the operational records that govern any scoped change."),
            (self.audit_key, 6, "apply_scoped_change_if_needed", "Apply a scoped operational change only when the collected evidence supports it."),
            (self.audit_key, 7, "observe_change_progress", "Observe the service handling the scoped change until its state is known."),
            (self.audit_key, 8, "recheck_observed_state", "Recheck the affected state after the operational action."),
            (self.audit_key, 9, "record_audit_result", "Record the observations and the resulting audit artifact."),
            (self.audit_key, 10, "restore_temporary_control", "Restore temporary controls to the values recorded at the start of the audit."),
            (self.audit_key, 11, "release_or_hold", "Record whether the downstream consumer may proceed."),
            (self.audit_key, 12, "archive_evidence", "Archive the evidence required for later review."),
            (self.audit_key, 13, "handoff_to_owner", "Hand the completed audit to the operational owner."),
            (self.audit_key, 14, "close_runbook", "Close the runbook entry after the audit is complete."),
        )
        self._insert_rows(
            env,
            f"{self.ops_schema}.audit_runbook_steps",
            ("audit_key", "step_no", "step_name", "details"),
            runbook_rows,
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.ops_schema}.consistency_audit_results ("
                "audit_key VARCHAR(64) PRIMARY KEY, syncpoint_id VARCHAR(64), schema_contract_match TINYINT NOT NULL, conclusion VARCHAR(64), "
                "orders_primary_count INT, orders_secondary_count INT, orders_checksum_match TINYINT, "
                "orders_diff_rows INT, items_primary_count INT, items_secondary_count INT, "
                "items_checksum_match TINYINT, items_diff_rows INT, order_item_orphan_rows INT, "
                "orders_direct_count_delta INT, items_direct_count_delta INT, "
                "direct_count_expected TINYINT, gc_restored TINYINT, "
                "created_at DATETIME, notes VARCHAR(1024), release_allowed TINYINT, "
                "repair_job_count INT NULL, repair_applied_rows INT NULL)"
            ),
            "create consistency_audit_results",
        )
        self._insert_rows(
            env,
            f"{self.ops_schema}.consistency_audit_results",
            (
                "audit_key", "syncpoint_id", "schema_contract_match", "conclusion", "orders_primary_count",
                "orders_secondary_count", "orders_checksum_match", "orders_diff_rows",
                "items_primary_count", "items_secondary_count", "items_checksum_match",
                "items_diff_rows", "order_item_orphan_rows", "orders_direct_count_delta",
                "items_direct_count_delta", "direct_count_expected", "gc_restored",
                "created_at", "notes", "release_allowed", "repair_job_count", "repair_applied_rows",
            ),
            (
                (
                    self.audit_key, self.syncpoint_id, 0, "interrupted",
                    self.syncpoint_order_count, self.syncpoint_order_count, 1,
                    self.syncpoint_order_diff_rows, self.syncpoint_item_count,
                    self.syncpoint_item_count, 1, self.syncpoint_item_diff_rows,
                    self.order_item_orphan_rows, 25, 22, 1, 0,
                    "2026-08-01 10:24:00",
                    "previous audit attempt stopped before GC restore; reconcile this row before final submission",
                    0,
                    0,
                    0,
                ),
            ),
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE VIEW {self.ops_schema}.v_direct_count_decoy AS "
                f"SELECT 'orders' AS table_name, "
                f"(SELECT COUNT(*) FROM {self.primary_schema}.{self.order_table}) AS primary_rows, "
                f"(SELECT COUNT(*) FROM {self.secondary_schema}.{self.order_table}) AS secondary_rows, "
                f"(SELECT COUNT(*) FROM {self.primary_schema}.{self.order_table}) - "
                f"(SELECT COUNT(*) FROM {self.secondary_schema}.{self.order_table}) AS direct_delta "
                "UNION ALL "
                f"SELECT 'order_items', "
                f"(SELECT COUNT(*) FROM {self.primary_schema}.{self.item_table}), "
                f"(SELECT COUNT(*) FROM {self.secondary_schema}.{self.item_table}), "
                f"(SELECT COUNT(*) FROM {self.primary_schema}.{self.item_table}) - "
                f"(SELECT COUNT(*) FROM {self.secondary_schema}.{self.item_table})"
            ),
            "create direct count decoy view",
        )

    def _load_noise_tables(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.ops_schema}.repl_events ("
                "event_id BIGINT PRIMARY KEY, event_time DATETIME, severity VARCHAR(16), source VARCHAR(32), "
                "related_table VARCHAR(64), message VARCHAR(512))"
            ),
            "create repl_events",
        )
        rows = []
        severities = ("INFO", "WARN", "INFO", "INFO", "DEBUG")
        sources = ("cdc", "br", "dm", "tikv", "tidb", "scheduler")
        for i in range(1, self.noise_event_count + 1):
            rows.append((
                i,
                f"2026-08-01 {8 + (i % 4):02d}:{i % 60:02d}:{(i * 13) % 60:02d}",
                severities[i % len(severities)],
                sources[i % len(sources)],
                ("orders", "order_items", "inventory_reservations", "payments")[i % 4],
                f"background replication check event {i}; no action required",
            ))
        self._insert_rows(
            env,
            f"{self.ops_schema}.repl_events",
            ("event_id", "event_time", "severity", "source", "related_table", "message"),
            rows,
        )
        for schema in (self.primary_schema, self.secondary_schema):
            reservations = []
            for i in range(1, 121):
                reservations.append((f"res-{schema}-{i:04d}", 50000 + i, 1 + (i % 5), 1 + (i % 7), self.primary_tso - i * 3, "2026-08-01 09:30:00", i * 101))
            self._insert_rows(
                env,
                f"{schema}.inventory_reservations",
                ("reservation_id", "sku_id", "warehouse_id", "quantity", "commit_tso", "updated_at", "payload_crc"),
                reservations,
            )

    def _verify_persistent_state(self, env) -> None:
        primary_syncpoint = self._scalar(
            env,
            f"SELECT COUNT(*) FROM {self.primary_schema}.{self.order_table} WHERE commit_tso <= {self.primary_tso}",
            "verify primary syncpoint orders",
        )
        secondary_syncpoint = self._scalar(
            env,
            f"SELECT COUNT(*) FROM {self.secondary_schema}.{self.order_table} WHERE commit_tso <= {self.secondary_tso}",
            "verify secondary syncpoint orders",
        )
        items = self._scalar(
            env,
            f"SELECT COUNT(*) FROM {self.primary_schema}.{self.item_table} WHERE commit_tso <= {self.primary_tso}",
            "verify primary syncpoint items",
        )
        if (
            primary_syncpoint != self.syncpoint_order_count
            or secondary_syncpoint != self.syncpoint_order_count
            or items != self.syncpoint_item_count
        ):
            raise RuntimeError(
                "HC02 syncpoint fixture counts are wrong: "
                f"primary_orders={primary_syncpoint}, secondary_orders={secondary_syncpoint}, "
                f"primary_items={items}, expected_orders={self.syncpoint_order_count}, "
                f"expected_items={self.syncpoint_item_count}"
            )
        incomplete_audit_rows = self._scalar(
            env,
            f"SELECT COUNT(*) FROM {self.ops_schema}.consistency_audit_results "
            f"WHERE audit_key = {sql_literal(self.audit_key)} AND conclusion = 'interrupted'",
            "verify interrupted audit row",
        )
        if incomplete_audit_rows != 1:
            raise RuntimeError(
                "HC02 fixture must start with exactly one interrupted audit row: "
                f"audit_key={self.audit_key!r}, rows={incomplete_audit_rows}"
            )
        release_window_rows = self._scalar(
            env,
            f"SELECT COUNT(*) FROM {self.ops_schema}.audit_window_catalog "
            f"WHERE request_id = {sql_literal(self.audit_request)} "
            f"AND consumer = {sql_literal(self.release_consumer)} "
            f"AND window_label = {sql_literal(self.audit_window_label)} "
            "AND release_state = 'open' "
            f"AND audit_key = {sql_literal(self.audit_key)}",
            "verify current audit window",
        )
        if release_window_rows != 1:
            raise RuntimeError(
                "HC02 fixture must have exactly one open current audit window: "
                f"request_id={self.audit_request!r}, consumer={self.release_consumer!r}, "
                f"window_label={self.audit_window_label!r}, rows={release_window_rows}"
            )
        queue_rows = self._scalar(
            env,
            f"SELECT COUNT(*) FROM {self.ops_schema}.{self.audit_request_queue_table} "
            f"WHERE request_id = {sql_literal(self.audit_request)} "
            f"AND audit_key = {sql_literal(self.audit_key)} "
            f"AND consumer = {sql_literal(self.release_consumer)} "
            f"AND target_window = {sql_literal(self.audit_window_label)} "
            "AND request_state = 'awaiting_audit' AND priority = 'release'",
            "verify current audit request queue record",
        )
        if queue_rows != 1:
            raise RuntimeError(
                "HC02 fixture must have exactly one current awaiting audit request: "
                f"request_id={self.audit_request!r}, audit_key={self.audit_key!r}, rows={queue_rows}"
            )
        binding_rows = self._scalar(
            env,
            f"SELECT COUNT(*) FROM {self.ops_schema}.audit_syncpoint_bindings AS b "
            f"JOIN {self.ops_schema}.audit_window_catalog AS w "
            f"ON w.request_id = {sql_literal(self.audit_request)} "
            "AND w.audit_key = b.audit_key AND w.consumer = b.consumer "
            "AND w.window_label = b.window_label AND w.release_state = 'open' "
            f"JOIN {self.ops_schema}.{self.audit_request_queue_table} AS q "
            "ON q.request_id = w.request_id AND q.audit_key = w.audit_key "
            "AND q.consumer = w.consumer AND q.target_window = w.window_label "
            "AND q.request_state = 'awaiting_audit' AND q.priority = 'release' "
            f"WHERE b.audit_key = {sql_literal(self.audit_key)} "
            f"AND b.syncpoint_id = {sql_literal(self.syncpoint_id)} "
            f"AND b.consumer = {sql_literal(self.release_consumer)} "
            f"AND b.window_label = {sql_literal(self.audit_window_label)} "
            "AND b.binding_state = 'active' AND b.released_at IS NULL",
            "verify active audit syncpoint binding",
        )
        if binding_rows != 1:
            raise RuntimeError(
                "HC02 fixture must have exactly one active binding for the current audit window: "
                f"audit_key={self.audit_key!r}, syncpoint_id={self.syncpoint_id!r}, "
                f"consumer={self.release_consumer!r}, window_label={self.audit_window_label!r}, "
                f"rows={binding_rows}"
            )
        repair_lease_rows = self._scalar(
            env,
            f"SELECT COUNT(*) FROM {self.ops_schema}.{self.repair_lease_table} "
            f"WHERE lease_id IN ({sql_literal(self.repair_lease_id)}, {sql_literal(self.repair_lease_id_2)}) "
            f"AND audit_key = {sql_literal(self.audit_key)} "
            f"AND syncpoint_id = {sql_literal(self.syncpoint_id)} AND consumer = {sql_literal(self.release_consumer)} "
            f"AND window_label = {sql_literal(self.audit_window_label)} AND lease_state = 'issued'",
            "verify current repair lease",
        )
        if repair_lease_rows != self.repair_count:
            raise RuntimeError(
                "HC02 fixture must have all issued repair leases for the current release: "
                f"lease_ids={(self.repair_lease_id, self.repair_lease_id_2)!r}, "
                f"expected={self.repair_count}, rows={repair_lease_rows}"
            )
        authorization_rows = self._scalar(
            env,
            f"SELECT COUNT(*) FROM {self.ops_schema}.{self.repair_lease_table} "
            f"WHERE audit_key = {sql_literal(self.audit_key)} "
            f"AND syncpoint_id = {sql_literal(self.syncpoint_id)} "
            f"AND consumer = {sql_literal(self.release_consumer)} "
            f"AND window_label = {sql_literal(self.audit_window_label)} "
            "AND lease_state = 'issued'",
            "verify current-scope repair authorization noise",
        )
        expected_authorization_rows = (
            self.repair_count * (2 + self.repair_same_row_decoy_count) + self.repair_decoy_lease_count
        )
        if authorization_rows != expected_authorization_rows:
            raise RuntimeError(
                "HC02 fixture must have the expected current-scope authorization population: "
                f"expected={expected_authorization_rows}, rows={authorization_rows}"
            )
        worker_rows = self._scalar(
            env,
            f"SELECT COUNT(*) FROM {self.ops_schema}.{self.repair_worker_table} "
            "WHERE worker_name = 'hc02_repair_worker' AND service_state = 'starting'",
            "verify repair worker status",
        )
        if worker_rows != 1:
            raise RuntimeError(
                "HC02 fixture must have one starting repair worker status row: "
                f"rows={worker_rows}"
            )
        direct_delta = self._scalar(
            env,
            f"SELECT (SELECT COUNT(*) FROM {self.primary_schema}.{self.order_table})"
            f" - (SELECT COUNT(*) FROM {self.secondary_schema}.{self.order_table})",
            "verify direct count delta",
        )
        if direct_delta < self.live_primary_extra_orders:
            raise RuntimeError(
                f"HC02 direct-count decoy is too weak: direct_delta={direct_delta}, "
                f"expected_at_least={self.live_primary_extra_orders}"
            )

    def _insert_rows(self, env, table: str, columns: tuple[str, ...], rows: list[tuple] | tuple[tuple, ...]) -> None:
        if not rows:
            return
        col_sql = ", ".join(columns)
        values = (self._sql_tuple(row) for row in rows)
        run_sql_batches(
            env.execute_sql,
            f"INSERT INTO {table} ({col_sql}) VALUES ",
            values,
            80,
            f"insert {table}",
        )

    def _sql_tuple(self, row: tuple) -> str:
        return "(" + ", ".join(self._sql_value(value) for value in row) + ")"

    def _sql_value(self, value) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, int):
            return str(value)
        return sql_literal(value)

    def _scalar(self, env, sql: str, context: str) -> int:
        payload = json_object(env.execute_sql(sql), context)
        rows = payload.get("result")
        if not isinstance(rows, list) or len(rows) != 1 or len(rows[0]) != 1:
            raise RuntimeError(f"{context} expected one scalar row: sql={sql!r}, rows={rows!r}")
        return int(rows[0][0])
