from collections.abc import Mapping

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    run_sql_batches,
    validate_sql_identifier,
)

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.health_check.empty_region_leader_skew import (
    TidbHealthCheckEmptyRegionLeaderSkewForRegionalJobSkewReviewEvaluatorCase,
    TidbHealthCheckEmptyRegionLeaderSkewForRecentSplitWindowEvaluatorCase,
)
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckEmptyRegionLeaderSkewCase(TiDBScenarioCase):
    db: str
    review_key: str
    business_table: str
    review_table: str
    region_inventory_table: str
    store_distribution_table: str
    pd_config_table: str
    metric_samples_table: str
    empty_lane_prefix: str
    empty_lane_count: int
    pre_split_regions: int
    business_rows: int
    business_checksum: int
    persistent_age_minutes: int
    persistent_empty_region_count: int
    persistent_zero_key_region_count: int
    recent_empty_region_count: int
    expected_empty_region_count: int
    expected_zero_key_region_count: int
    expected_total_region_count: int
    expected_empty_ratio: float
    expected_persistent_empty_ratio: float
    expected_leader_skew_ratio: float
    expected_persistent_leader_skew_ratio: float
    expected_merge_rate_per_min: float
    observation_window_minutes: int
    expected_empty_trend_first: float
    expected_empty_trend_last: float
    expected_leader_trend_first: float
    expected_leader_trend_last: float
    leader_counts: tuple[int, int, int]
    persistent_leader_counts: tuple[int, int, int]
    focused_fixture: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckEmptyRegionLeaderSkewForRegionalJobSkewReviewScenarioCase(
    TidbHealthCheckEmptyRegionLeaderSkewCase
):
    pass


HC03_DB = "benchops"
HC03_BUSINESS_TABLE = "hc03_business_events"
HC03_REVIEW_TABLE = "hc03_region_capacity_review"
HC03_REGION_INVENTORY_TABLE = "hc03_region_inventory"
HC03_STORE_DISTRIBUTION_TABLE = "hc03_store_distribution"
HC03_PD_CONFIG_TABLE = "hc03_pd_config"
HC03_METRIC_SAMPLES_TABLE = "hc03_pd_region_samples"
HC03_REVIEW_KEY = "hc03-weekly-region-risk-20260801"
HC03_BUSINESS_ROWS = 2400
HC03_BUSINESS_CHECKSUM = HC03_BUSINESS_ROWS * (HC03_BUSINESS_ROWS + 1) // 2


_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="checkout_probe",
            sql=(
                f"SELECT tenant_id, status, amount FROM {HC03_DB}.{HC03_BUSINESS_TABLE} "
                "WHERE event_id IN (17, 271, 983, 1777)"
            ),
            qps=0.9,
            tier="OLTP_READ",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="merchant_rollup",
            sql=(
                f"SELECT tenant_id, COUNT(*), SUM(amount) FROM {HC03_DB}.{HC03_BUSINESS_TABLE} "
                "WHERE event_day >= DATE('2026-07-20') "
                "GROUP BY tenant_id ORDER BY SUM(amount) DESC LIMIT 20"
            ),
            qps=0.35,
            tier="REPORTING",
            application_name="merchant-rollup",
        ),
        WorkloadProfile(
            name="audit_reconciliation",
            sql=(
                f"SELECT status, COUNT(*), SUM(event_id) FROM {HC03_DB}.{HC03_BUSINESS_TABLE} "
                "WHERE tenant_id BETWEEN 70 AND 210 GROUP BY status"
            ),
            qps=0.45,
            tier="AUDIT",
            application_name="risk-audit",
        ),
        WorkloadProfile(
            name="ops_queue_probe",
            sql=(
                f"SELECT review_key, status FROM {HC03_DB}.{HC03_REVIEW_TABLE} "
                f"WHERE review_key = '{HC03_REVIEW_KEY}'"
            ),
            qps=0.4,
            tier="OPS_PROBE",
            application_name="ops-health-probe",
        ),
        WorkloadProfile(
            name="dashboard_refresh",
            sql=(
                f"SELECT metric_name, target, MAX(value) FROM {HC03_DB}.{HC03_METRIC_SAMPLES_TABLE} "
                "WHERE metric_name IN ('tidb_qps', 'cpu_percent', 'backup_bytes_per_second', 'ddl_owner_cpu') "
                "GROUP BY metric_name, target"
            ),
            qps=0.32,
            tier="MONITORING",
            application_name="grafana-refresh",
        ),
        WorkloadProfile(
            name="region_sampler",
            sql=(
                f"SELECT table_name, leader_store_id, COUNT(*), SUM(read_bytes), SUM(written_bytes) "
                f"FROM {HC03_DB}.{HC03_REGION_INVENTORY_TABLE} "
                "GROUP BY table_name, leader_store_id ORDER BY SUM(read_bytes) DESC LIMIT 20"
            ),
            qps=0.25,
            tier="REGION_SCAN",
            application_name="pd-region-sampler",
        ),
        WorkloadProfile(
            name="scheduler_snapshot",
            sql=(
                f"SELECT config_key, config_value, observed_at FROM {HC03_DB}.{HC03_PD_CONFIG_TABLE} "
                "ORDER BY observed_at DESC, config_key LIMIT 24"
            ),
            qps=0.22,
            tier="CONTROL_PLANE",
            application_name="scheduler-console",
        ),
        WorkloadProfile(
            name="window_reconciliation",
            sql=(
                f"SELECT metric_name, target, MIN(value), MAX(value) FROM {HC03_DB}.{HC03_METRIC_SAMPLES_TABLE} "
                "WHERE sample_ts >= TIMESTAMP'2026-08-03 09:30:00' "
                "GROUP BY metric_name, target"
            ),
            qps=0.2,
            tier="CONTROL_PLANE",
            application_name="capacity-reconciliation",
        ),
        WorkloadProfile(
            name="tenant_heatmap",
            sql=(
                f"SELECT tenant_id, COUNT(*), SUM(amount) FROM {HC03_DB}.{HC03_BUSINESS_TABLE} "
                "GROUP BY tenant_id ORDER BY SUM(amount) DESC LIMIT 20"
            ),
            qps=0.28,
            tier="REPORTING",
            application_name="tenant-heatmap",
        ),
        WorkloadProfile(
            name="raft_observer",
            sql=(
                f"SELECT metric_name, target, MAX(value) FROM {HC03_DB}.{HC03_METRIC_SAMPLES_TABLE} "
                "WHERE metric_name IN ('pending_peer_count', 'leader_skew_ratio', 'region_split_rate') "
                "GROUP BY metric_name, target"
            ),
            qps=0.24,
            tier="CONTROL_PLANE",
            application_name="raft-observer",
        ),
        WorkloadProfile(
            name="backup_heartbeat",
            sql=(
                f"SELECT target, MAX(value) FROM {HC03_DB}.{HC03_METRIC_SAMPLES_TABLE} "
                "WHERE metric_name = 'backup_bytes_per_second' GROUP BY target"
            ),
            qps=0.18,
            tier="BACKUP",
            application_name="backup-heartbeat",
        ),
        WorkloadProfile(
            name="ddl_watch",
            sql=(
                f"SELECT target, MAX(value) FROM {HC03_DB}.{HC03_METRIC_SAMPLES_TABLE} "
                "WHERE metric_name = 'ddl_owner_cpu' GROUP BY target"
            ),
            qps=0.18,
            tier="DDL",
            application_name="ddl-watch",
        ),
        WorkloadProfile(
            name="placement_reconcile",
            sql=(
                f"SELECT leader_store_id, COUNT(*), SUM(approximate_keys) "
                f"FROM {HC03_DB}.{HC03_REGION_INVENTORY_TABLE} "
                "GROUP BY leader_store_id ORDER BY leader_store_id"
            ),
            qps=0.2,
            tier="CONTROL_PLANE",
            application_name="placement-reconcile",
        ),
        WorkloadProfile(
            name="replica_lag_probe",
            sql=(
                f"SELECT target, MAX(value) FROM {HC03_DB}.{HC03_METRIC_SAMPLES_TABLE} "
                "WHERE metric_name = 'pending_peer_count' GROUP BY target"
            ),
            qps=0.2,
            tier="MONITORING",
            application_name="replica-lag-probe",
        ),
        WorkloadProfile(
            name="cache_refresh_probe",
            sql=f"SELECT COUNT(*) FROM {HC03_DB}.hc03_dashboard_cache_missing",
            qps=0.28,
            tier="LOG_NOISE",
            application_name="dashboard-cache-refresh",
        ),
        WorkloadProfile(
            name="rollup_refresh_probe",
            sql=f"SELECT COUNT(*) FROM {HC03_DB}.hc03_rollup_snapshot_missing",
            qps=0.24,
            tier="LOG_NOISE",
            application_name="rollup-refresh",
        ),
    ),
    worker_count=8,
    seed=0x0C03,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=45,
)


_CASE = TidbHealthCheckEmptyRegionLeaderSkewForRegionalJobSkewReviewScenarioCase(
    case_id="regional_job_empty_region_skew_review",
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "recorded a time-bounded capacity review with an equivalent staged consolidation plan"
            ],
            "verification": [
                "source counts, effective scheduler state, trend window and raw event-id sum were rechecked"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=TidbHealthCheckEmptyRegionLeaderSkewForRegionalJobSkewReviewEvaluatorCase,
    title=(
        "Routine TiDB capacity review with mixed business traffic and an unresolved regional "
        "scheduling risk."
    ),
    alert=(
        "[Routine TiDB Fleet Review] The weekly capacity health-check queue has one open item "
        "for the regional jobs cluster. User-facing latency and PD CPU are still below paging "
        "thresholds, but the review window overlaps checkout, merchant rollup, audit, DDL, and "
        "backup activity. Separate ordinary business-query noise from topology risk, then close "
        "the stored review row with evidence, impact, and a bounded remediation plan. Do not "
        "restart healthy components or change business rows during this patrol."
    ),
    initial_state={
        "status": "routine_review_open",
        "pd_cpu": "below_alert_threshold",
        "business_window": "mixed checkout/reporting/audit load",
        "review_key": HC03_REVIEW_KEY,
    },
    expected_target={
        "status": "closed_or_action_required_review",
        "risk": "persistent_region_capacity_risk_after_transient_windows_are_excluded",
        "bounded_plan": "stage_an_equivalent_cross_table_merge_plan_during_a_maintenance_window",
        "business_checksum": "raw SUM(event_id) preserved",
        "structured_review": "source_counts_trend_and_latest_scheduler_snapshot_reconciled",
    },
    background_workload=_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(release=TIDB_V8_1_0, pd_count=3, tikv_count=3, tidb_count=2),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.724364,
        reference_run_ids=("reference-267__tidb_health_check_empty_region_leader_skew__regional_job_empty_region_skew_review__mock__r001",),
    ),
    db=HC03_DB,
    review_key=HC03_REVIEW_KEY,
    business_table=HC03_BUSINESS_TABLE,
    review_table=HC03_REVIEW_TABLE,
    region_inventory_table=HC03_REGION_INVENTORY_TABLE,
    store_distribution_table=HC03_STORE_DISTRIBUTION_TABLE,
    pd_config_table=HC03_PD_CONFIG_TABLE,
    metric_samples_table=HC03_METRIC_SAMPLES_TABLE,
    empty_lane_prefix="hc03_empty_lane",
    empty_lane_count=18,
    pre_split_regions=4,
    business_rows=HC03_BUSINESS_ROWS,
    business_checksum=HC03_BUSINESS_CHECKSUM,
    persistent_age_minutes=60,
    persistent_empty_region_count=108,
    persistent_zero_key_region_count=108,
    recent_empty_region_count=48,
    expected_empty_region_count=156,
    expected_zero_key_region_count=156,
    expected_total_region_count=220,
    expected_empty_ratio=156 / 220,
    expected_persistent_empty_ratio=108 / 220,
    expected_leader_skew_ratio=172 / 34,
    expected_persistent_leader_skew_ratio=96 / 6,
    expected_merge_rate_per_min=0.075,
    observation_window_minutes=36,
    expected_empty_trend_first=108.0,
    expected_empty_trend_last=143.0,
    expected_leader_trend_first=11.5,
    expected_leader_trend_last=15.0,
    leader_counts=(172, 38, 34),
    persistent_leader_counts=(96, 6, 6),
)


_NEW_CASE = replace(
    _CASE,
    case_id="recent_split_window_region_review",
    case_no=1,
    evaluator=TidbHealthCheckEmptyRegionLeaderSkewForRecentSplitWindowEvaluatorCase,
    title="A bounded TiDB Region review separating persistent empty Regions from a recent split window.",
    reference_report={
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": ["recorded a bounded review that separated persistent empty Regions from the recent split window"],
            "verification": ["rechecked source counts, the short trend window, scheduler state, leader distribution, and business sum"],
        },
        "summary": "The recent split-window Region review was recorded without changing cluster or business state.",
    },
    alert=(
        "例行 Region 健康复核：最近 split 窗口出现一批短时 empty Region，同时仍有少量长期 zero-key Region。"
        "请用库存年龄、短窗口趋势、PD 调度快照和 store leader 分布区分两类现象，写入有边界的 review 结论。"
        "本次只允许记录复核，不重启组件、不修改业务表和调度配置。"
    ),
    initial_state={
        "status": "routine_review_open",
        "review_key": "hc03-recent-split-window-20260801",
        "window": "short_recent_split_window",
    },
    expected_target={
        "status": "closed_or_action_required_review",
        "persistent_region_risk": True,
        "recent_split_window_excluded": True,
        "business_checksum": "preserved",
    },
    review_key="hc03-recent-split-window-20260801",
    empty_lane_count=10,
    pre_split_regions=3,
    persistent_age_minutes=45,
    persistent_empty_region_count=60,
    persistent_zero_key_region_count=60,
    recent_empty_region_count=24,
    expected_empty_region_count=84,
    expected_zero_key_region_count=84,
    expected_total_region_count=100,
    expected_empty_ratio=84 / 100,
    expected_persistent_empty_ratio=60 / 100,
    expected_leader_skew_ratio=3.0,
    expected_persistent_leader_skew_ratio=9.0,
    expected_merge_rate_per_min=0.075,
    observation_window_minutes=24,
    expected_empty_trend_first=60.0,
    expected_empty_trend_last=83.0,
    expected_leader_trend_first=7.5,
    expected_leader_trend_last=9.8,
    leader_counts=(30, 18, 10),
    persistent_leader_counts=(45, 12, 5),
    focused_fixture=True,
    background_workload=replace(_CASE.background_workload, worker_count=5, warmup_seconds=30),
    runtime=replace(_CASE.runtime, bootstrap_cache_enabled=False),
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.454545,
        reference_run_ids=(
            "tidb-reference-11__"
            "tidb_health_check_empty_region_leader_skew__"
            "recent_split_window_region_review__mock__r001",
        ),
    ),
)


class TidbHealthCheckEmptyRegionLeaderSkewInjector(BaseFaultInjector):
    """Create real empty-region pressure plus a bounded review evidence surface."""

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        env = context.env
        require_sql_success(env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"), "clear HC03 schema")
        require_sql_success(env.execute_sql(f"CREATE DATABASE {self.db}"), "create HC03 schema")
        self._create_business_table(env)
        self._create_empty_region_lanes(env)
        self._create_observability_tables(env)
        self._verify_state(env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._verify_state(context.env)
        return {
            "review_key": self.review_key,
            "business_checksum": self.business_checksum,
            "region_inventory": require_sql_success(
                context.env.execute_sql(
                    f"SELECT COUNT(*), SUM(is_empty = 1), SUM(approximate_keys = 0), "
                    f"SUM(is_empty = 1 AND TIMESTAMPDIFF(MINUTE, first_seen_at, last_seen_at) >= {self.persistent_age_minutes}) "
                    f"FROM {self.db}.{self.region_inventory_table}"
                ),
                "capture HC03 region inventory summary",
            ),
            "store_distribution": require_sql_success(
                context.env.execute_sql(
                    f"SELECT store_id, leader_count, persistent_leader_count, recent_leader_count, region_count "
                    f"FROM {self.db}.{self.store_distribution_table} ORDER BY store_id"
                ),
                "capture HC03 store distribution",
            ),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        return None

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"),
            "drop HC03 schema",
        )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.review_key = str(config["review_key"])
        self.business_table = validate_sql_identifier(str(config["business_table"]), "business_table")
        self.review_table = validate_sql_identifier(str(config["review_table"]), "review_table")
        self.region_inventory_table = validate_sql_identifier(
            str(config["region_inventory_table"]), "region_inventory_table"
        )
        self.store_distribution_table = validate_sql_identifier(
            str(config["store_distribution_table"]), "store_distribution_table"
        )
        self.pd_config_table = validate_sql_identifier(str(config["pd_config_table"]), "pd_config_table")
        self.metric_samples_table = validate_sql_identifier(
            str(config["metric_samples_table"]), "metric_samples_table"
        )
        self.empty_lane_prefix = validate_sql_identifier(str(config["empty_lane_prefix"]), "empty_lane_prefix")
        self.empty_lane_count = int(config["empty_lane_count"])
        self.pre_split_regions = int(config["pre_split_regions"])
        self.business_rows = int(config["business_rows"])
        self.business_checksum = int(config["business_checksum"])
        self.persistent_age_minutes = int(config["persistent_age_minutes"])
        self.recent_empty_region_count = int(config["recent_empty_region_count"])
        self.persistent_empty_region_count = int(config["persistent_empty_region_count"])
        self.persistent_zero_key_region_count = int(config["persistent_zero_key_region_count"])
        self.observation_window_minutes = int(config["observation_window_minutes"])
        self.expected_empty_trend_first = float(config["expected_empty_trend_first"])
        self.expected_leader_trend_first = float(config["expected_leader_trend_first"])
        self.leader_counts = tuple(int(value) for value in config["leader_counts"])
        self.persistent_leader_counts = tuple(
            int(value) for value in config["persistent_leader_counts"]
        )
        self.focused_fixture = bool(config["focused_fixture"])
        self.business_region_rows = 16 if self.focused_fixture else 64

    def _create_business_table(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.business_table} ("
                "event_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, event_day DATE NOT NULL, "
                "amount DECIMAL(12,2) NOT NULL, status VARCHAR(20) NOT NULL, payload VARCHAR(64) NOT NULL, "
                "KEY idx_tenant_day (tenant_id, event_day), KEY idx_status_day (status, event_day)"
                ")"
            ),
            "create HC03 business table",
        )
        batch_size = 400
        for start in range(1, self.business_rows + 1, batch_size):
            end = min(start + batch_size, self.business_rows + 1)
            values = []
            for event_id in range(start, end):
                tenant_id = event_id % 307
                day = 1 + event_id % 28
                amount = 10 + event_id % 997
                status = ("paid", "pending", "refunded", "review")[event_id % 4]
                values.append(
                    f"({event_id}, {tenant_id}, DATE('2026-07-{day:02d}'), "
                    f"{amount}.00, '{status}', 'hc03-business-noise')"
                )
            require_sql_success(
                env.execute_sql(
                    f"INSERT INTO {self.db}.{self.business_table} "
                    "(event_id, tenant_id, event_day, amount, status, payload) VALUES "
                    + ",".join(values)
                ),
                f"load HC03 business rows {start}-{end - 1}",
            )

    def _create_empty_region_lanes(self, env) -> None:
        for index in range(self.empty_lane_count):
            table = f"{self.empty_lane_prefix}_{index:02d}"
            require_sql_success(
                env.execute_sql(
                    f"CREATE TABLE {self.db}.{table} ("
                    "id BIGINT PRIMARY KEY NONCLUSTERED, shard_hint BIGINT NOT NULL, payload VARCHAR(32), "
                    "KEY idx_shard_hint (shard_hint)"
                    f") SHARD_ROW_ID_BITS = 4 PRE_SPLIT_REGIONS = {self.pre_split_regions}"
                ),
                f"create HC03 empty region lane {table}",
            )

    def _create_observability_tables(self, env) -> None:
        self._create_review_table(env)
        self._create_region_inventory(env)
        self._create_store_distribution(env)
        self._create_pd_config(env)
        self._create_metric_samples(env)

    def _create_review_table(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.review_table} ("
                "review_key VARCHAR(96) PRIMARY KEY, status VARCHAR(48) NOT NULL, "
                "risk_confirmed TINYINT NOT NULL DEFAULT 0, "
                "persistent_pattern_confirmed TINYINT NOT NULL DEFAULT 0, "
                "decoy_causes_excluded TINYINT NOT NULL DEFAULT 0, "
                "leader_skew_attributed TINYINT NOT NULL DEFAULT 0, "
                "scheduler_constraint_confirmed TINYINT NOT NULL DEFAULT 0, "
                "plan_bounded TINYINT NOT NULL DEFAULT 0, "
                "plan_cross_table TINYINT NOT NULL DEFAULT 0, "
                "maintenance_window_required TINYINT NOT NULL DEFAULT 0, "
                "restart_required TINYINT NOT NULL DEFAULT 0, "
                "business_data_mutation_allowed TINYINT NOT NULL DEFAULT 0, "
                "verification_complete TINYINT NOT NULL DEFAULT 0, "
                "risk_entity VARCHAR(256), empty_region_count INT, zero_key_region_count INT, "
                "persistent_empty_region_count INT, persistent_zero_key_region_count INT, "
                "recent_empty_region_count INT, "
                "total_region_count INT, empty_ratio DECIMAL(8,4), leader_skew_ratio DECIMAL(8,4), "
                "persistent_empty_ratio DECIMAL(8,4), persistent_leader_skew_ratio DECIMAL(8,4), "
                "merge_rate_per_min DECIMAL(8,4), observation_window_minutes INT, "
                "recommended_action TEXT, safety_boundary TEXT, verification TEXT, "
                "business_checksum BIGINT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                ")"
            ),
            "create HC03 review table",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.review_table} "
                "(review_key, status, risk_entity, recommended_action, safety_boundary, verification) "
                f"VALUES ('{self.review_key}', 'open', NULL, NULL, NULL, NULL)"
            ),
            "insert HC03 open review row",
        )

    def _create_region_inventory(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.region_inventory_table} ("
                "region_id BIGINT PRIMARY KEY, table_name VARCHAR(96) NOT NULL, "
                "leader_store_id INT NOT NULL, approximate_size INT NOT NULL, approximate_keys INT NOT NULL, "
                "written_bytes BIGINT NOT NULL, read_bytes BIGINT NOT NULL, is_empty TINYINT NOT NULL, "
                "first_seen_at TIMESTAMP NOT NULL, last_seen_at TIMESTAMP NOT NULL, "
                "sample_note VARCHAR(128) NOT NULL"
                ")"
            ),
            "create HC03 region inventory table",
        )
        rows = []
        region_id = 800000
        for lane in range(self.empty_lane_count):
            table = f"{self.empty_lane_prefix}_{lane:02d}"
            for split in range(6):
                leader_store = 1 if split < 5 else 2 + lane % 2
                rows.append(
                    f"({region_id}, '{table}', {leader_store}, 1, 0, {split * 17}, {split * 11}, 1, "
                    "TIMESTAMP'2026-07-30 00:00:00', TIMESTAMP'2026-08-03 10:05:00', "
                    "'sample-family-a')"
                )
                region_id += 1
        for index in range(self.recent_empty_region_count):
            leader_store = 2 if index % 3 else 3
            table = f"hc03_online_lane_{index % 6:02d}"
            rows.append(
                f"({region_id}, '{table}', {leader_store}, 1, 0, {index * 7}, {index * 5}, 1, "
                "TIMESTAMP'2026-08-03 10:01:00', TIMESTAMP'2026-08-03 10:05:00', "
                "'sample-family-b')"
            )
            region_id += 1
        for index in range(self.business_region_rows):
            leader_store = 1 + index % 3
            table = [
                "hc03_checkout_orders",
                "hc03_merchant_rollup",
                "hc03_audit_events",
                self.business_table,
            ][index % 4]
            rows.append(
                f"({region_id}, '{table}', {leader_store}, {8 + index % 23}, {500 + index * 13}, "
                f"{9000 + index * 37}, {12000 + index * 29}, 0, "
                "TIMESTAMP'2026-08-02 20:00:00', TIMESTAMP'2026-08-03 10:05:00', "
                "'sample-family-c')"
            )
            region_id += 1
        run_sql_batches(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.region_inventory_table} "
            "(region_id, table_name, leader_store_id, approximate_size, approximate_keys, "
            "written_bytes, read_bytes, is_empty, first_seen_at, last_seen_at, sample_note) VALUES ",
            rows,
            200,
            "load HC03 region inventory",
        )

    def _create_store_distribution(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.store_distribution_table} ("
                "store_id INT PRIMARY KEY, leader_count INT NOT NULL, region_count INT NOT NULL, "
                "persistent_leader_count INT NOT NULL, recent_leader_count INT NOT NULL, "
                "hot_read_regions INT NOT NULL, hot_write_regions INT NOT NULL, note VARCHAR(128) NOT NULL"
                ")"
            ),
            "create HC03 store distribution table",
        )
        store_rows = [
            (1, self.leader_counts[0], 260, self.persistent_leader_counts[0], 5, 7, 5, 'distribution-slice-a'),
        ]
        if self.focused_fixture:
            store_rows.append(
                (3, self.leader_counts[2], 75, self.persistent_leader_counts[2], 21, 8, 6, 'distribution-slice-c'),
            )
        else:
            store_rows.extend((
                (2, self.leader_counts[1], 80, self.persistent_leader_counts[1], 22, 9, 7, 'distribution-slice-b'),
                (3, self.leader_counts[2], 75, self.persistent_leader_counts[2], 21, 8, 6, 'distribution-slice-c'),
            ))
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.store_distribution_table} VALUES "
                + ",".join(str(tuple(row)) for row in store_rows)
            ),
            "load HC03 store distribution rows",
        )

    def _create_pd_config(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.pd_config_table} ("
                "config_key VARCHAR(96) NOT NULL, config_value VARCHAR(96) NOT NULL, "
                "observed_at TIMESTAMP NOT NULL, source VARCHAR(64) NOT NULL, "
                "PRIMARY KEY (config_key, observed_at)"
                ")"
            ),
            "create HC03 PD config table",
        )
        config_rows = []
        for timestamp, cross_table_merge, merge_limit, split_interval in (
            ("2026-08-03 08:00:00", "true", "8", "10m0s"),
            ("2026-08-03 09:00:00", "true", "4", "30m0s"),
            ("2026-08-03 10:00:00", "false", "2", "1h0m0s"),
        ):
            config_rows.extend((
                f"('enable-cross-table-merge', '{cross_table_merge}', TIMESTAMP'{timestamp}', 'pd-runtime'),",
                f"('merge-schedule-limit', '{merge_limit}', TIMESTAMP'{timestamp}', 'pd-runtime'),",
                f"('split-merge-interval', '{split_interval}', TIMESTAMP'{timestamp}', 'pd-runtime'),",
            ))
            if not self.focused_fixture:
                config_rows.extend((
                    f"('max-merge-region-size', '20', TIMESTAMP'{timestamp}', 'pd-runtime'),",
                    f"('max-merge-region-keys', '200000', TIMESTAMP'{timestamp}', 'pd-runtime'),",
                    f"('leader-schedule-limit', '4', TIMESTAMP'{timestamp}', 'pd-runtime'),",
                    f"('hot-region-schedule-limit', '8', TIMESTAMP'{timestamp}', 'pd-runtime'),",
                    f"('patrol-region-interval', '100ms', TIMESTAMP'{timestamp}', 'pd-runtime'),",
                ))
        config_rows[-1] = config_rows[-1].rstrip(",")
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.pd_config_table} VALUES "
                + "".join(config_rows)
            ),
            "load HC03 PD config rows",
        )

    def _create_metric_samples(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.metric_samples_table} ("
                "sample_ts TIMESTAMP NOT NULL, metric_name VARCHAR(96) NOT NULL, "
                "target VARCHAR(96) NOT NULL, value DECIMAL(18,4) NOT NULL, note VARCHAR(160) NOT NULL, "
                "KEY idx_metric_time (metric_name, sample_ts), KEY idx_target_time (target, sample_ts)"
                ")"
            ),
            "create HC03 metric samples table",
        )
        rows = []
        for minute in range(self.observation_window_minutes):
            hour = 9 + (30 + minute) // 60
            minute_of_hour = (30 + minute) % 60
            ts = f"2026-08-03 {hour:02d}:{minute_of_hour:02d}:00"
            empty_regions = int(self.expected_empty_trend_first) + minute
            total_regions = 188 + minute * 2
            rows.extend((
                f"(TIMESTAMP'{ts}', 'empty_region_count', 'pd/region-health', {empty_regions}, 'controller-observation')",
                f"(TIMESTAMP'{ts}', 'zero_key_region_count', 'pd/region-health', {empty_regions}, 'controller-observation')",
                f"(TIMESTAMP'{ts}', 'total_region_count', 'pd/region-health', {total_regions}, 'controller-observation')",
                f"(TIMESTAMP'{ts}', 'region_merge_rate_per_min', 'pd/region-health', {0.06 + (minute % 4) * 0.01:.4f}, 'controller-observation')",
                f"(TIMESTAMP'{ts}', 'leader_skew_ratio', 'pd/region-health', {self.expected_leader_trend_first + minute * 0.1:.4f}, 'controller-observation')",
                f"(TIMESTAMP'{ts}', 'pending_peer_count', 'pd/region-health', {2 + minute % 3}, 'controller-observation')",
                f"(TIMESTAMP'{ts}', 'cross_table_merge_enabled', 'pd/region-health', 0, 'controller-observation')",
                f"(TIMESTAMP'{ts}', 'merge_schedule_limit', 'pd/region-health', 2, 'controller-observation')",
            ))
            split_window = 250 if 8 <= minute <= 10 else 120 + minute % 5
            hot_store_skew = 8.5 if 20 <= minute <= 24 else 2.4 + (minute % 3) * 0.1
            rows.extend((
                f"(TIMESTAMP'{ts}', 'empty_region_count', 'pd/split-window', {split_window}, 'controller-observation')",
                f"(TIMESTAMP'{ts}', 'zero_key_region_count', 'pd/split-window', {split_window - 4}, 'controller-observation')",
                f"(TIMESTAMP'{ts}', 'total_region_count', 'pd/split-window', {split_window + 60}, 'controller-observation')",
                f"(TIMESTAMP'{ts}', 'region_merge_rate_per_min', 'pd/split-window', {0.42 if 8 <= minute <= 10 else 0.18:.4f}, 'controller-observation')",
                f"(TIMESTAMP'{ts}', 'leader_skew_ratio', 'pd/split-window', {3.2 if 8 <= minute <= 10 else 2.1:.4f}, 'controller-observation')",
                f"(TIMESTAMP'{ts}', 'region_split_rate', 'pd/split-window', {18 if 8 <= minute <= 10 else 3}, 'controller-observation')",
            ))
            if not self.focused_fixture:
                rows.extend((
                    f"(TIMESTAMP'{ts}', 'pending_peer_count', 'tikv/store-2', {14 if 20 <= minute <= 24 else 2}, 'controller-observation')",
                    f"(TIMESTAMP'{ts}', 'leader_skew_ratio', 'tikv/store-2', {hot_store_skew:.4f}, 'controller-observation')",
                ))
                for target in (
                    "tidb/tidb-0",
                    "tidb/tidb-1",
                    "tikv/tikv-0",
                    "tikv/tikv-1",
                    "tikv/tikv-2",
                ):
                    rows.extend((
                        f"(TIMESTAMP'{ts}', 'tidb_qps', '{target}', {350 + minute * 7 + len(target)}, 'service-observation')",
                        f"(TIMESTAMP'{ts}', 'cpu_percent', '{target}', {34 + minute % 9 + len(target) % 5}, 'service-observation')",
                        f"(TIMESTAMP'{ts}', 'backup_bytes_per_second', '{target}', {2048 + minute * 19}, 'service-observation')",
                        f"(TIMESTAMP'{ts}', 'ddl_owner_cpu', '{target}', {12 + minute % 5}, 'service-observation')",
                        f"(TIMESTAMP'{ts}', 'region_split_rate', '{target}', {2 + minute % 4}, 'service-observation')",
                    ))
        run_sql_batches(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.metric_samples_table} "
            "(sample_ts, metric_name, target, value, note) VALUES ",
            rows,
            200,
            "load HC03 metric samples",
        )

    def _verify_state(self, env) -> None:
        business = json_object(
            env.execute_sql(
                f"SELECT COUNT(*), SUM(event_id) FROM {self.db}.{self.business_table}"
            ),
            "verify HC03 business table",
        )["result"]
        if business not in (
            [[self.business_rows, str(self.business_checksum)]],
            [[self.business_rows, self.business_checksum]],
        ):
            raise RuntimeError(
                "HC03 business checksum mismatch: "
                f"expected=({self.business_rows}, {self.business_checksum}), observed={business!r}"
            )
        inventory = json_object(
            env.execute_sql(
                f"SELECT COUNT(*), SUM(is_empty = 1), SUM(approximate_keys = 0), "
                f"SUM(is_empty = 1 AND TIMESTAMPDIFF(MINUTE, first_seen_at, last_seen_at) >= {self.persistent_age_minutes}) "
                f"FROM {self.db}.{self.region_inventory_table}"
            ),
            "verify HC03 region inventory",
        )["result"][0]
        expected_inventory = [
            self.empty_lane_count * 6 + self.recent_empty_region_count + self.business_region_rows,
            self.empty_lane_count * 6 + self.recent_empty_region_count,
            self.empty_lane_count * 6 + self.recent_empty_region_count,
            self.empty_lane_count * 6,
        ]
        observed_inventory = [int(value) for value in inventory]
        if observed_inventory != expected_inventory:
            raise RuntimeError(
                "HC03 region inventory source truth mismatch: "
                f"expected={expected_inventory!r}, observed={observed_inventory!r}"
            )
        review = json_object(
            env.execute_sql(
                f"SELECT status FROM {self.db}.{self.review_table} "
                f"WHERE review_key = '{self.review_key}'"
            ),
            "verify HC03 review row",
        )["result"]
        if review != [["open"]]:
            raise RuntimeError(f"HC03 review row must start open: observed={review!r}")


class TidbHealthCheckEmptyRegionLeaderSkewScenario(TiDBScenario):
    scenario_id = "tidb_health_check_empty_region_leader_skew"
    description = (
        "Routine TiDB health check that distinguishes business-query noise from region inventory "
        "and leader/store scheduling-capacity risk."
    )
    cases = (_CASE, _NEW_CASE)

    def build_fault_plan(
        self,
        case: TidbHealthCheckEmptyRegionLeaderSkewCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbHealthCheckEmptyRegionLeaderSkewInjector,
                config={
                    "db": case.db,
                    "review_key": case.review_key,
                    "business_table": case.business_table,
                    "review_table": case.review_table,
                    "region_inventory_table": case.region_inventory_table,
                    "store_distribution_table": case.store_distribution_table,
                    "pd_config_table": case.pd_config_table,
                    "metric_samples_table": case.metric_samples_table,
                    "empty_lane_prefix": case.empty_lane_prefix,
                    "empty_lane_count": case.empty_lane_count,
                    "pre_split_regions": case.pre_split_regions,
                    "business_rows": case.business_rows,
                    "business_checksum": case.business_checksum,
                    "persistent_age_minutes": case.persistent_age_minutes,
                    "recent_empty_region_count": case.recent_empty_region_count,
                    "persistent_empty_region_count": case.persistent_empty_region_count,
                    "persistent_zero_key_region_count": case.persistent_zero_key_region_count,
                    "observation_window_minutes": case.observation_window_minutes,
                    "expected_empty_trend_first": case.expected_empty_trend_first,
                    "expected_leader_trend_first": case.expected_leader_trend_first,
                    "leader_counts": case.leader_counts,
                    "persistent_leader_counts": case.persistent_leader_counts,
                    "focused_fixture": case.focused_fixture,
                },
            ),
        )
