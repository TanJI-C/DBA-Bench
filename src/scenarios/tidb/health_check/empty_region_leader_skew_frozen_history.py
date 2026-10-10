from __future__ import annotations

import json
import re
import threading
import time
import zlib
from dataclasses import dataclass, replace
from typing import Mapping

from src.scenarios.evaluation.tidb.health_check.empty_region_leader_skew_frozen_history import (
    TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryEvaluatorCase,
    TidbHealthCheckEmptyRegionLeaderSkewReducedInventoryEvaluatorCase,
)
from src.execution.history.records import HistoricalRecordSource
from src.execution.tidb_metrics import (
    PD_EMPTY_REGION_COUNT_QUERY,
    PD_MERGE_RATE_QUERY,
    PD_SPLIT_RATE_QUERY,
)
from src.database.sql import sequence_row_source
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    connect_tidb,
    json_object,
    require_sql_success,
    sequence_row_source,
    validate_sql_identifier,
)
from src.scenarios.tidb.runtime import TIDB_V8_1_0, tidb_runtime
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)
from src.scenarios.workloads import BackgroundWorkloadStartPhase, WorkloadProfile
from src.scenarios.base import (
    BackgroundWorkloadSpec,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenarioCase,
    TiDBScenario,
)


HC02_DB = "benchops_mf_hc03"
HC02_REVIEW_KEY = "mf-hc03-weekly-region-risk-20260816"
HC02_BUSINESS_TABLE = "mf_hc03_business_events"
HC02_REVIEW_TABLE = "mf_hc03_capacity_review"
HC02_RISK_PREFIX = "mf_hc03_empty_lane"
HC02_BENIGN_PREFIX = "mf_hc03_benign_split"
HC02_RISK_TABLE_COUNT = 18
HC02_BENIGN_TABLE_COUNT = 10
HC02_BUSINESS_ROWS = 2400
HC02_BUSINESS_CHECKSUM = HC02_BUSINESS_ROWS * (HC02_BUSINESS_ROWS + 1) // 2


def _business_crc(rows: int) -> int:
    value = 0
    for event_id in range(1, rows + 1):
        value ^= zlib.crc32(
            f"{event_id}#{event_id % 32}#PAID#{event_id / 100:.2f}".encode("utf-8")
        )
    return value


HC02_BUSINESS_CRC = _business_crc(HC02_BUSINESS_ROWS)


_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="checkout_probe",
            sql=f"SELECT event_id, status, amount FROM {HC02_DB}.{HC02_BUSINESS_TABLE} WHERE event_id IN (17, 271, 983, 1777)",
            qps=0.9,
            tier="OLTP_READ",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="merchant_rollup",
            sql=f"SELECT tenant_id, COUNT(*), SUM(amount) FROM {HC02_DB}.{HC02_BUSINESS_TABLE} GROUP BY tenant_id ORDER BY SUM(amount) DESC LIMIT 20",
            qps=0.35,
            tier="REPORTING",
            application_name="merchant-rollup",
        ),
        WorkloadProfile(
            name="audit_reconciliation",
            sql=f"SELECT status, COUNT(*), SUM(event_id) FROM {HC02_DB}.{HC02_BUSINESS_TABLE} GROUP BY status",
            qps=0.45,
            tier="AUDIT",
            application_name="risk-audit",
        ),
        WorkloadProfile(
            name="review_probe",
            sql=f"SELECT review_key, status FROM {HC02_DB}.{HC02_REVIEW_TABLE} WHERE review_key = '{HC02_REVIEW_KEY}'",
            qps=0.4,
            tier="OPS_PROBE",
            application_name="ops-health-probe",
        ),
        WorkloadProfile(
            name="tenant_heatmap",
            sql=f"SELECT tenant_id, COUNT(*), SUM(amount) FROM {HC02_DB}.{HC02_BUSINESS_TABLE} GROUP BY tenant_id ORDER BY tenant_id",
            qps=0.28,
            tier="REPORTING",
            application_name="tenant-heatmap",
        ),
        WorkloadProfile(
            name="business_crc_probe",
            sql=f"SELECT COUNT(*), COALESCE(SUM(event_id), 0), BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, status, amount))) FROM {HC02_DB}.{HC02_BUSINESS_TABLE}",
            qps=0.22,
            tier="CONTROL_PLANE",
            application_name="business-reconciliation",
        ),
        WorkloadProfile(
            name="region_catalog_probe",
            sql="SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'benchops_mf_hc03' ORDER BY TABLE_NAME LIMIT 40",
            qps=0.2,
            tier="CONTROL_PLANE",
            application_name="region-catalog",
        ),
        WorkloadProfile(
            name="slow_report_decoy",
            sql=f"SELECT tenant_id, status, SUM(amount) FROM {HC02_DB}.{HC02_BUSINESS_TABLE} GROUP BY tenant_id, status ORDER BY SUM(amount) DESC LIMIT 50",
            qps=0.24,
            tier="REPORTING",
            application_name="weekly-report",
        ),
    ),
    worker_count=8,
    seed=0xC303,
    start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
    warmup_seconds=15,
)


_METRIC_HISTORY = FrozenHistorySpec(
    schema_version=2,
    duration_seconds=43200,
    normal_capture_seconds=300,
    fault_capture_seconds=600,
    base_step_seconds=2,
    overview_step_seconds=300,
    block_min_seconds=30,
    block_max_seconds=120,
    transition_seconds=30,
    target_age_seconds_range=(1800, 7200),
    required_metrics=(
        "pd_region_inventory",
        "pd_region_activity",
        "pd_leader_distribution",
    ),
    record_sources=(
        HistoricalRecordSource.COMPONENT_LOG,
        HistoricalRecordSource.TOPSQL,
        HistoricalRecordSource.SLOW_QUERIES,
    ),
    decoys=(
        HistoryDecoySpec(
            decoy_id="benign-presplit-merge",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="pd_region_inventory",
            field="total_regions",
            target=None,
            direction=DecoyDirection.DIP,
            count=1,
            duration_seconds=10,
            minimum_deviation_mad=0.1,
        ),
        HistoryDecoySpec(
            decoy_id="benign-hot-leader",
            kind=DecoyKind.METRIC_ONLY,
            metric="pd_region_inventory",
            field="total_regions",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=30,
            amplitude_mad=2.0,
        ),
        HistoryDecoySpec(
            decoy_id="benign-backup-io",
            kind=DecoyKind.METRIC_ONLY,
            metric="pd_region_inventory",
            field="total_regions",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=30,
            amplitude_mad=2.0,
        ),
        HistoryDecoySpec(
            decoy_id="benign-pd-handoff",
            kind=DecoyKind.METRIC_ONLY,
            metric="pd_region_inventory",
            field="total_regions",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=30,
            amplitude_mad=2.0,
        ),
        HistoryDecoySpec(
            decoy_id="reporting-peak",
            kind=DecoyKind.METRIC_ONLY,
            metric="pd_region_inventory",
            field="total_regions",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=60,
            amplitude_mad=2.0,
        ),
    ),
    max_points_per_series=5000,
    max_scalar_samples_per_response=60000,
    max_history_records_per_response=200,
    metric_targets={
        "pd_region_inventory": (None,),
        "pd_region_activity": (None,),
        "pd_leader_distribution": (None,),
    },
)


def _reference_report() -> dict[str, object]:
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "persistent empty and zero-key Region accumulation caused by Region growth outrunning constrained merge scheduling",
                    "entity": "pd/cluster and tikv/tikv-0..2",
                    "evidence": ["reference path derives the target window from the frozen metric history"],
                }
            ],
        },
        "outcome": {
            "changes": ["recorded a bounded multi-table consolidation plan in the review row"],
            "verification": ["current PD source truth and business checksum were reconciled"],
        },
        "summary": "Reference report placeholder; the formal mock fills the runtime UTC window and timeline from observed history.",
    }


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryForHistoryReviewScenarioCase(
    TiDBScenarioCase
):
    db: str
    review_key: str
    business_table: str
    review_table: str
    risk_table_prefix: str
    risk_table_count: int
    benign_table_prefix: str
    benign_table_count: int
    business_rows: int
    business_checksum: int
    business_crc: int
    minimum_empty_regions: int
    minimum_zero_key_regions: int
    minimum_leader_skew_ratio: float
    maximum_merge_rate_per_min: float


_CASE = TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryForHistoryReviewScenarioCase(
    case_id="empty_region_leader_history_review",
    case_no=0,
    evaluator=TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryEvaluatorCase,
    title="Historical Region-capacity review with empty Region accumulation and downstream leader skew.",
    alert=(
        "[Weekly capacity review] The commerce TiDB cluster is reachable and frontend p99 latency and PD CPU are currently within the ordinary range. "
        "During the review period checkout, reporting, backup, DDL, and topology scheduling all ran. "
        "Find the historical UTC window that still represents an actionable capacity risk, distinguish it from completed maintenance episodes, "
        "and record a bounded plan with a maintenance boundary. When citing historical SQL or log evidence in corroborating_records, retain its source, target, "
        "timestamp or start/end timestamps, and at least one raw record field. Do not modify business rows, change cluster scheduling, restart components, "
        "or execute the consolidation itself."
    ),
    initial_state={
        "status": "available_with_historical_capacity_review_open",
        "business": "checkout_and_reporting_available",
        "current_frontend_slo": "ordinary",
        "review": "open",
    },
    expected_target={
        "status": "action_required_review_recorded",
        "business_checksum_unchanged": True,
        "pd_config_unchanged": True,
        "bounded_plan": True,
        "live_consolidation": False,
    },
    background_workload=_BACKGROUND_WORKLOAD,
    reference_report=_reference_report(),
    frozen_history=_METRIC_HISTORY,
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.870833,
        reference_run_ids=("reference-268__tidb_health_check_empty_region_leader_skew_frozen_history__empty_region_leader_history_review__mock__r001",),
    ),
    runtime=tidb_runtime(release=TIDB_V8_1_0, pd_count=3, tikv_count=3, tidb_count=2),
    db=HC02_DB,
    review_key=HC02_REVIEW_KEY,
    business_table=HC02_BUSINESS_TABLE,
    review_table=HC02_REVIEW_TABLE,
    risk_table_prefix=HC02_RISK_PREFIX,
    risk_table_count=HC02_RISK_TABLE_COUNT,
    benign_table_prefix=HC02_BENIGN_PREFIX,
    benign_table_count=HC02_BENIGN_TABLE_COUNT,
    business_rows=HC02_BUSINESS_ROWS,
    business_checksum=HC02_BUSINESS_CHECKSUM,
    business_crc=HC02_BUSINESS_CRC,
    minimum_empty_regions=36,
    minimum_zero_key_regions=36,
    minimum_leader_skew_ratio=1.4,
    maximum_merge_rate_per_min=4.0,
)

_REDUCED_INVENTORY_CASE = replace(
    _CASE,
    case_id="empty_region_leader_reduced_inventory_review",
    case_no=1,
    evaluator=TidbHealthCheckEmptyRegionLeaderSkewReducedInventoryEvaluatorCase,
    title="Historical Region-capacity review over a reduced empty-Region inventory.",
    risk_table_count=12,
    benign_table_count=6,
    business_rows=1200,
    business_checksum=1200 * 1201 // 2,
    business_crc=_business_crc(1200),
    minimum_empty_regions=24,
    minimum_zero_key_regions=24,
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.473684,
        reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
        protocol_version='difficulty-v2',
    ),
)


class TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryInjector(BaseFaultInjector):

    retain_workload_after_metric_history = True

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Keep the fault state active through the Agent phase."""
    """Create real Region state and constrain PD scheduling without history fixtures."""

    def __init__(self) -> None:
        self.recovery_pd_config: dict[str, object] = {}
        self.recovery_store_weights: dict[int, tuple[object, object]] = {}
        self._normal_fixture_stop: threading.Event | None = None
        self._normal_fixture_thread: threading.Thread | None = None
        self._normal_fixture_failure: BaseException | None = None

    def prepare_metric_history_normal_capture(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._create_database_and_tables(context.env)
        self._normal_fixture_stop = threading.Event()
        self._normal_fixture_failure = None

    @staticmethod
    def _wait_for_pd_activity_sources(env) -> None:
        deadline = time.monotonic() + 120
        last_counts = None
        while time.monotonic() < deadline:
            split_series = env._prometheus_instant_payload(PD_SPLIT_RATE_QUERY)
            merge_series = env._prometheus_instant_payload(PD_MERGE_RATE_QUERY)
            if len(split_series) > 1 or len(merge_series) > 1:
                raise RuntimeError(
                    "HC02 PD activity source returned multiple aggregated series: "
                    f"split_series={len(split_series)}, merge_series={len(merge_series)}"
                )
            last_counts = {
                "split_series": len(split_series),
                "merge_series": len(merge_series),
            }
            if len(split_series) == 1 and len(merge_series) == 1:
                return
            time.sleep(2)
        raise RuntimeError(
            "HC02 PD activity source did not become rate-queryable after the real probe: "
            f"last={last_counts!r}"
        )

    def start_metric_history_normal_capture(self, context: FaultLifecycleContext) -> None:
        if self._normal_fixture_stop is None:
            raise RuntimeError("HC02 normal history fixture was not prepared before start")
        if self._normal_fixture_thread is not None:
            raise RuntimeError("HC02 normal history fixture started twice")
        self._normal_fixture_thread = threading.Thread(
            target=self._run_normal_history_fixture,
            args=(context.env,),
            name=f"aiops-hc02-normal-fixture-{context.run_id}",
            daemon=True,
        )
        self._normal_fixture_thread.start()
        self._wait_for_pd_activity_sources(context.env)

    def finish_metric_history_normal_capture(self, context: FaultLifecycleContext) -> None:
        stop = self._normal_fixture_stop
        if stop is None:
            return
        stop.set()
        thread = self._normal_fixture_thread
        if thread is not None:
            thread.join(timeout=120)
            if thread.is_alive():
                raise RuntimeError("HC02 normal history fixture did not stop")
        failure = self._normal_fixture_failure
        self._normal_fixture_stop = None
        self._normal_fixture_thread = None
        self._normal_fixture_failure = None
        self._drop_tables(context.env, self.benign_tables)
        if failure is not None:
            raise RuntimeError(f"HC02 normal history fixture failed: failure={failure!r}") from failure

    def _run_normal_history_fixture(self, env) -> None:
        stop = self._normal_fixture_stop
        if stop is None:
            raise RuntimeError("HC02 normal history fixture has no stop event")
        try:
            connection = connect_tidb(
                env,
                database=self.db,
                autocommit=True,
                application_name="hc02-normal-history-fixture",
                read_timeout=60,
                write_timeout=60,
            )
            try:
                if stop.wait(5):
                    return
                active_tables: list[str] = []
                for table in self.benign_tables:
                    self._create_normal_benign_table(connection, table)
                    active_tables.append(table)
                    if self._run_normal_benign_io(connection, tuple(active_tables), stop, 22):
                        return
            finally:
                connection.close()
        except BaseException as exc:
            self._normal_fixture_failure = exc
            stop.set()

    def _create_normal_benign_table(self, connection, table: str) -> None:
        self._execute_normal_fixture_sql(
            connection,
            f"CREATE TABLE {self.db}.{table} (id BIGINT NOT NULL, payload VARCHAR(32) NOT NULL, "
            f"KEY idx_hc02_benign_id (id)) SHARD_ROW_ID_BITS = 4 PRE_SPLIT_REGIONS = 8",
            f"create HC02 normal benign table {table}",
        )
        self._execute_normal_fixture_sql(
            connection,
            f"INSERT INTO {self.db}.{table} VALUES (1, 'benign')",
            f"seed HC02 normal benign table {table}",
        )
        self._execute_normal_fixture_sql(
            connection,
            f"TRUNCATE TABLE {self.db}.{table}",
            f"clear HC02 normal benign table {table}",
        )

    @staticmethod
    def _execute_normal_fixture_sql(connection, sql: str, context: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute(sql)

    def _run_normal_benign_io(
        self,
        connection,
        tables: tuple[str, ...],
        stop: threading.Event,
        duration_seconds: int,
    ) -> bool:
        deadline = time.monotonic() + duration_seconds
        while time.monotonic() < deadline:
            for table in tables:
                self._execute_normal_fixture_sql(
                    connection,
                    f"INSERT INTO {self.db}.{table} (id, payload) "
                    "SELECT n % 100000, 'normal-io' "
                    f"FROM ({sequence_row_source(1000)}) source",
                    f"write HC02 normal benign IO batch {table}",
                )
            if stop.wait(5):
                return True
        return False

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._create_database_and_tables(context.env)
        self._capture_pd_config(context.env)
        self._create_benign_tables(context.env)
        self._drop_tables(context.env, self.benign_tables)
        self._create_risk_tables(context.env)
        self._set_fault_pd_config(context.env)
        self._verify_business(context.env)
        self._verify_fault_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_fault_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._wait_for_region_state(context.env)
        self._verify_fault_state(context.env)
        self._apply_leader_placement_constraint(context.env)
        business = self._payload(context.env, self.business_sql, "capture HC02 business truth")
        deployment = context.env.get_deployment()
        regions = deployment.pd_request("GET", "/pd/api/v1/regions")
        stores = deployment.pd_request("GET", "/pd/api/v1/stores")
        config = deployment.pd_request("GET", "/pd/api/v1/config")
        return {
            "business_truth": business,
            "region_inventory": regions,
            "store_distribution": stores,
            "pd_config": config,
            "review_key": self.review_key,
            "risk_table_count": self.risk_table_count,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_fault_state(context.env)
        self._verify_business(context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        deployment = context.env.get_deployment()
        for store_id, (leader_weight, region_weight) in self.recovery_store_weights.items():
            deployment._pd_ctl(
                "store",
                "weight",
                str(store_id),
                str(leader_weight),
                str(region_weight),
            )
        self.recovery_store_weights.clear()
        for key, value in self.recovery_pd_config.items():
            result = deployment.pd_request(
                "POST",
                "/pd/api/v1/config",
                {key: value},
            )
            if result is not None and not isinstance(result, (dict, str)):
                raise TypeError(f"HC02 PD config recovery returned invalid payload: key={key!r}, result={result!r}")
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"),
            "drop HC02 database",
        )
        self._assert_database_absent(context.env)

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.review_key = str(config["review_key"])
        self.business_table = validate_sql_identifier(str(config["business_table"]), "business table")
        self.review_table = validate_sql_identifier(str(config["review_table"]), "review table")
        self.risk_table_prefix = validate_sql_identifier(str(config["risk_table_prefix"]), "risk table prefix")
        self.risk_table_count = int(config["risk_table_count"])
        self.benign_table_prefix = validate_sql_identifier(str(config["benign_table_prefix"]), "benign table prefix")
        self.benign_table_count = int(config["benign_table_count"])
        self.business_rows = int(config["business_rows"])
        self.business_checksum = int(config["business_checksum"])
        self.business_crc = int(config["business_crc"])
        self.minimum_empty_regions = int(config["minimum_empty_regions"])
        self.minimum_zero_key_regions = int(config["minimum_zero_key_regions"])
        self.minimum_leader_skew_ratio = float(config["minimum_leader_skew_ratio"])
        self.fault_pd_config = dict(config["fault_pd_config"])
        self.business_sql = str(config["business_sql"])
        self.risk_tables = tuple(f"{self.risk_table_prefix}_{index:02d}" for index in range(self.risk_table_count))
        self.benign_tables = tuple(f"{self.benign_table_prefix}_{index:02d}" for index in range(self.benign_table_count))
        self.owned_tables = (self.business_table, self.review_table, *self.risk_tables, *self.benign_tables)

    @staticmethod
    def _payload(env, sql: str, context: str) -> dict:
        return json_object(env.execute_sql(sql), context)

    def _capture_pd_config(self, env) -> None:
        payload = env.get_deployment().pd_request("GET", "/pd/api/v1/config")
        if not isinstance(payload, Mapping) or not isinstance(payload.get("schedule"), Mapping):
            raise TypeError(f"HC02 PD config has no schedule mapping: payload={payload!r}")
        schedule = payload["schedule"]
        self.recovery_pd_config = {
            key: schedule[key.removeprefix("schedule.")]
            for key in self.fault_pd_config
        }

    def _set_fault_pd_config(self, env) -> None:
        for key, value in self.fault_pd_config.items():
            api_value = str(value).casefold() if isinstance(value, bool) else value
            env.get_deployment().pd_request("POST", "/pd/api/v1/config", {key: api_value})

    def _verify_fault_state(self, env) -> None:
        payload = env.get_deployment().pd_request("GET", "/pd/api/v1/config")
        schedule = payload["schedule"]
        expected = {
            key: self._normalize_pd_value(key, value)
            for key, value in self.fault_pd_config.items()
        }
        observed = {
            key: self._normalize_pd_value(key, schedule[key.removeprefix("schedule.")])
            for key in self.fault_pd_config
        }
        if observed != expected:
            raise RuntimeError(f"HC02 constrained PD config is not active: expected={expected!r}, observed={observed!r}")

    @staticmethod
    def _normalize_pd_value(key: str, value: object) -> object:
        if key.endswith("enable-cross-table-merge"):
            return str(value).casefold() in {"true", "1", "on"}
        if key.endswith("merge-schedule-limit"):
            return int(value)
        if key.endswith("split-merge-interval"):
            match = re.fullmatch(r"(?:(?P<h>[0-9]+(?:\.[0-9]+)?)h)?(?:(?P<m>[0-9]+(?:\.[0-9]+)?)m)?(?:(?P<s>[0-9]+(?:\.[0-9]+)?)s)?", str(value).casefold())
            if match is None:
                raise ValueError(f"invalid HC02 PD interval: key={key!r}, value={value!r}")
            return round(float(match.group("h") or 0) * 3600 + float(match.group("m") or 0) * 60 + float(match.group("s") or 0), 6)
        raise KeyError(key)

    def _create_database_and_tables(self, env) -> None:
        require_sql_success(env.execute_sql(f"CREATE DATABASE IF NOT EXISTS {self.db}"), "create HC02 database")
        self._drop_tables(env, self.owned_tables)
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.business_table} ("
                "event_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, status VARCHAR(16) NOT NULL, "
                "amount DECIMAL(12,2) NOT NULL, "
                "CONSTRAINT hc02_status_values CHECK (status IN ('PAID', 'PENDING', 'CANCELLED'))"
                ")"
            ),
            "create HC02 protected business table",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.business_table} (event_id, tenant_id, status, amount) "
                f"SELECT n, MOD(n, 32), 'PAID', CAST(n / 100 AS DECIMAL(12,2)) "
                f"FROM ({sequence_row_source(self.business_rows)}) source"
            ),
            "load HC02 protected business rows",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.review_table} ("
                "review_key VARCHAR(96) PRIMARY KEY, status VARCHAR(32) NOT NULL, "
                "risk_confirmed TINYINT NOT NULL DEFAULT 0, persistent_pattern_confirmed TINYINT NOT NULL DEFAULT 0, "
                "decoy_causes_excluded TINYINT NOT NULL DEFAULT 0, leader_skew_attributed TINYINT NOT NULL DEFAULT 0, "
                "scheduler_constraint_confirmed TINYINT NOT NULL DEFAULT 0, plan_bounded TINYINT NOT NULL DEFAULT 0, "
                "maintenance_window_required TINYINT NOT NULL DEFAULT 0, restart_required TINYINT NOT NULL DEFAULT 0, "
                "business_data_mutation_allowed TINYINT NOT NULL DEFAULT 0, verification_complete TINYINT NOT NULL DEFAULT 0, "
                "target_window_start DATETIME, target_window_end DATETIME, empty_region_count INT, zero_key_region_count INT, "
                "leader_skew_ratio DECIMAL(12,4), merge_rate_per_min DECIMAL(12,4), business_checksum BIGINT, "
                "bounded_plan TEXT, maintenance_boundary TEXT, "
                "CONSTRAINT hc02_review_status_values CHECK (status IN ('open', 'action_required', 'closed'))"
                ")"
            ),
            "create HC02 review table",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.review_table} (review_key, status) VALUES ('{self.review_key}', 'open')"
            ),
            "insert HC02 open review row",
        )

    def _create_benign_tables(self, env) -> None:
        for table in self.benign_tables:
            require_sql_success(
                env.execute_sql(
                    f"CREATE TABLE {self.db}.{table} (id BIGINT NOT NULL, payload VARCHAR(32) NOT NULL, KEY idx_hc02_benign_id (id)) "
                    "SHARD_ROW_ID_BITS = 2 PRE_SPLIT_REGIONS = 2"
                ),
                f"create HC02 benign pre-split table {table}",
            )
            require_sql_success(env.execute_sql(f"INSERT INTO {self.db}.{table} VALUES (1, 'benign')"), f"seed HC02 benign table {table}")
            require_sql_success(env.execute_sql(f"TRUNCATE TABLE {self.db}.{table}"), f"clear HC02 benign table {table}")

    def _create_risk_tables(self, env) -> None:
        for table in self.risk_tables:
            require_sql_success(
                env.execute_sql(
                    f"CREATE TABLE {self.db}.{table} (id BIGINT NOT NULL, payload VARCHAR(32) NOT NULL, KEY idx_hc02_risk_id (id)) "
                    "SHARD_ROW_ID_BITS = 4 PRE_SPLIT_REGIONS = 4"
                ),
                f"create HC02 risk table {table}",
            )
            require_sql_success(env.execute_sql(f"INSERT INTO {self.db}.{table} VALUES (1, 'risk')"), f"seed HC02 risk table {table}")
            require_sql_success(env.execute_sql(f"TRUNCATE TABLE {self.db}.{table}"), f"clear HC02 risk table {table}")

    def _drop_tables(self, env, tables: tuple[str, ...]) -> None:
        for table in tables:
            require_sql_success(env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"), f"drop HC02 table {table}")

    def _verify_business(self, env) -> None:
        rows = self._payload(env, self.business_sql, "verify HC02 business checksum")["result"]
        if len(rows) != 1 or tuple(int(value) for value in rows[0]) != (self.business_rows, self.business_checksum, self.business_crc):
            raise RuntimeError(f"HC02 business checksum changed: expected={(self.business_rows, self.business_checksum, self.business_crc)!r}, observed={rows!r}")

    def _wait_for_region_state(self, env) -> None:
        deadline = time.monotonic() + 300
        last = None
        while time.monotonic() < deadline:
            payload = env.get_deployment().pd_request("GET", "/pd/api/v1/regions")
            regions = payload["regions"]
            zero_key = sum(int(region["approximate_keys"]) == 0 for region in regions)
            empty = int(env._prometheus_instant_scalar(PD_EMPTY_REGION_COUNT_QUERY))
            last = {
                "total": len(regions),
                "empty_prometheus": empty,
                "zero_key_pd_regions": zero_key,
            }
            if empty >= self.minimum_empty_regions and zero_key >= self.minimum_zero_key_regions:
                return
            time.sleep(1)
        raise RuntimeError(f"HC02 target Region state did not materialize: minimum={self.minimum_empty_regions}, last={last!r}")

    def _apply_leader_placement_constraint(self, env) -> None:
        deployment = env.get_deployment()
        stores_payload = deployment.pd_request("GET", "/pd/api/v1/stores")
        stores = stores_payload["stores"]
        tikv_stores = [
            item
            for item in stores
            if str(item["store"]["address"]).split(":", 1)[0].startswith("tikv-")
        ]
        if len(tikv_stores) != 3:
            raise RuntimeError(f"HC02 leader placement constraint requires three TiKV stores: stores={stores!r}")
        target = next(
            item
            for item in tikv_stores
            if str(item["store"]["address"]).split(":", 1)[0] == "tikv-0"
        )
        for item in tikv_stores:
            store_id = int(item["store"]["id"])
            status = item["status"]
            self.recovery_store_weights[store_id] = (
                status["leader_weight"],
                status["region_weight"],
            )
            leader_weight = 10 if item is target else 1
            deployment._pd_ctl(
                "store",
                "weight",
                str(store_id),
                str(leader_weight),
                str(status["region_weight"]),
            )

        deadline = time.monotonic() + 300
        last_counts = None
        while time.monotonic() < deadline:
            current = deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
            counts = [int(item["status"]["leader_count"]) for item in current]
            last_counts = counts
            if min(counts) > 0 and max(counts) / min(counts) >= self.minimum_leader_skew_ratio:
                return
            time.sleep(2)
        raise RuntimeError(
            "HC02 leader placement constraint did not materialize: "
            f"minimum_ratio={self.minimum_leader_skew_ratio}, last_counts={last_counts!r}"
        )

    def _assert_database_absent(self, env) -> None:
        rows = self._payload(
            env,
            f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{self.db}'",
            "verify HC02 database recovery",
        )["result"]
        if rows:
            raise RuntimeError(f"HC02 recovery left owned database: expected_absent={self.db!r}, observed={rows!r}")


class TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryScenario(TiDBScenario):
    scenario_id = "tidb_health_check_empty_region_leader_skew_frozen_history"
    description = "Frozen-history TiDB health check for persistent empty Region accumulation and downstream leader skew."
    cases = (_CASE, _REDUCED_INVENTORY_CASE)

    def build_fault_plan(
        self,
        case: TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryForHistoryReviewScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryInjector,
                config={
                    "db": case.db,
                    "review_key": case.review_key,
                    "business_table": case.business_table,
                    "review_table": case.review_table,
                    "risk_table_prefix": case.risk_table_prefix,
                    "risk_table_count": case.risk_table_count,
                    "benign_table_prefix": case.benign_table_prefix,
                    "benign_table_count": case.benign_table_count,
                    "business_rows": case.business_rows,
                    "business_checksum": case.business_checksum,
                    "business_crc": case.business_crc,
                    "minimum_empty_regions": case.minimum_empty_regions,
                    "minimum_zero_key_regions": case.minimum_zero_key_regions,
                    "minimum_leader_skew_ratio": case.minimum_leader_skew_ratio,
                    "fault_pd_config": {
                        "schedule.enable-cross-table-merge": False,
                        "schedule.merge-schedule-limit": 2,
                        "schedule.split-merge-interval": "1h0m0s",
                    },
                    "business_sql": f"SELECT COUNT(*), COALESCE(SUM(event_id), 0), BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, status, amount))) FROM {case.db}.{case.business_table}",
                },
            ),
        )


__all__ = (
    "TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryForHistoryReviewScenarioCase",
    "TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryInjector",
    "TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryScenario",
)
