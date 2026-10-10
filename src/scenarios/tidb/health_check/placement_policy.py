import json

import time

from collections.abc import Mapping

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.health_check.placement_policy import (
    TidbHealthCheckPlacementPolicyEvaluatorCase,
    TidbHealthCheckPlacementPolicyForTableInheritanceEvaluatorCase,
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
class TidbHealthCheckPlacementPolicyCase(TiDBScenarioCase):
    db: str
    target_table: str
    customer_table: str
    event_table: str
    archive_table: str
    service_table: str
    review_table: str
    policy_name: str
    customer_policy_name: str
    archive_policy_name: str
    constraint_policy_name: str
    partition_name: str
    review_key: str
    service_name: str
    business_rows: int
    partition_mode: str
    focused_fixture: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckPlacementPolicyForSingleStoreVotersPendingScenarioCase(
    TidbHealthCheckPlacementPolicyCase
):
    pass


HC08_DB = "benchops"
HC08_TARGET_TABLE = "hc08_checkout_orders"
HC08_CUSTOMER_TABLE = "hc08_customer_profiles"
HC08_EVENT_TABLE = "hc08_fulfillment_events"
HC08_ARCHIVE_TABLE = "hc08_order_archive"
HC08_SERVICE_TABLE = "hc08_service_catalog"
HC08_REVIEW_TABLE = "hc08_fleet_reviews"
HC08_POLICY = "hc08_checkout_resilience"
HC08_CUSTOMER_POLICY = "hc08_default_lane"
HC08_ARCHIVE_POLICY = "hc08_archive_locality"
HC08_CONSTRAINT_POLICY = "hc08_zone_dictionary"
HC08_PARTITION_NAME = "p_checkout_current"
HC08_REVIEW_KEY = "fleet-review-20260807-042"
HC08_SERVICE_NAME = "checkout-write"

_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="hc08_checkout_order_lookup",
            sql=(
                f"SELECT order_id, status, amount FROM {HC08_DB}.{HC08_TARGET_TABLE} "
                "WHERE order_id IN (17, 271, 983, 1777)"
            ),
            qps=0.85,
            tier="OLTP_READ",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="hc08_merchant_status_rollup",
            sql=(
                f"SELECT warehouse_id, status, COUNT(*), SUM(amount) "
                f"FROM {HC08_DB}.{HC08_TARGET_TABLE} "
                "WHERE created_at >= '2026-07-15' "
                "GROUP BY warehouse_id, status ORDER BY SUM(amount) DESC"
            ),
            qps=0.35,
            tier="REPORTING",
            application_name="merchant-rollup",
        ),
        WorkloadProfile(
            name="hc08_fulfillment_event_join",
            sql=(
                f"SELECT o.warehouse_id, e.event_type, COUNT(*) "
                f"FROM {HC08_DB}.{HC08_TARGET_TABLE} o "
                f"JOIN {HC08_DB}.{HC08_EVENT_TABLE} e ON e.order_id = o.order_id "
                "WHERE e.event_ts >= '2026-07-20' "
                "GROUP BY o.warehouse_id, e.event_type"
            ),
            qps=0.25,
            tier="FULFILLMENT",
            application_name="warehouse-monitor",
        ),
        WorkloadProfile(
            name="hc08_customer_segment_dashboard",
            sql=(
                f"SELECT c.segment, COUNT(DISTINCT c.customer_id), SUM(o.amount) "
                f"FROM {HC08_DB}.{HC08_CUSTOMER_TABLE} c "
                f"JOIN {HC08_DB}.{HC08_TARGET_TABLE} o ON o.customer_id = c.customer_id "
                "WHERE c.active = 1 GROUP BY c.segment ORDER BY SUM(o.amount) DESC"
            ),
            qps=0.2,
            tier="CUSTOMER_REPORT",
            application_name="customer-dashboard",
        ),
        WorkloadProfile(
            name="hc08_archive_reconciliation",
            sql=(
                f"SELECT archive_month, COUNT(*), SUM(amount) FROM {HC08_DB}.{HC08_ARCHIVE_TABLE} "
                "GROUP BY archive_month ORDER BY archive_month DESC"
            ),
            qps=0.2,
            tier="ARCHIVE_REVIEW",
            application_name="order-history",
        ),
        WorkloadProfile(
            name="hc08_risk_audit_top_orders",
            sql=(
                f"SELECT order_id, customer_id, amount, status FROM {HC08_DB}.{HC08_TARGET_TABLE} "
                "WHERE status IN ('review', 'cancelled') ORDER BY amount DESC LIMIT 40"
            ),
            qps=0.3,
            tier="AUDIT",
            application_name="risk-audit",
        ),
        WorkloadProfile(
            name="hc08_review_queue_probe",
            sql=(
                f"SELECT review_key, service_name, check_name, status, updated_at "
                f"FROM {HC08_DB}.{HC08_REVIEW_TABLE} ORDER BY opened_at DESC"
            ),
            qps=0.4,
            tier="OPS_PROBE",
            application_name="ops-health-probe",
        ),
        WorkloadProfile(
            name="hc08_service_catalog_refresh",
            sql=(
                f"SELECT service_name, table_schema, table_name, owner_team "
                f"FROM {HC08_DB}.{HC08_SERVICE_TABLE} ORDER BY service_name"
            ),
            qps=0.25,
            tier="SERVICE_CATALOG",
            application_name="topology-audit",
        ),
        WorkloadProfile(
            name="hc08_event_window_reconcile",
            sql=(
                f"SELECT event_type, actor, COUNT(*), MAX(event_ts) "
                f"FROM {HC08_DB}.{HC08_EVENT_TABLE} "
                "WHERE event_ts >= '2026-07-10' GROUP BY event_type, actor"
            ),
            qps=0.2,
            tier="RECONCILIATION",
            application_name="event-reconcile",
        ),
    ),
    worker_count=7,
    seed=0xAC08,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=12,
)


_CASE = TidbHealthCheckPlacementPolicyForSingleStoreVotersPendingScenarioCase(
    case_id="single_store_voters_pending",
    reference_report={
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": [
                "restored the live review target to inherited placement and closed the matching fleet-review item"
            ],
            "verification": [
                "the target converged and the trusted business truth remained unchanged"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=TidbHealthCheckPlacementPolicyEvaluatorCase,
    title=(
        "Routine fleet-control review across checkout, customer, fulfillment, archive, "
        "and monitoring traffic."
    ),
    alert=(
        "[Routine TiDB Fleet Review] One live control-plane review remains open after "
        "this lane moved to its compact operating profile. User-facing latency, writes, "
        "and component health remain below paging thresholds. Identify the exact live "
        "review scope from current metadata, distinguish it from approved and historical "
        "nearby records, apply the smallest service-owned correction consistent with "
        "the fixed-version guidance, and close only that review. Do not change business "
        "rows, centrally owned definitions, or healthy components."
    ),
    initial_state={
        "status": "routine_review_open",
        "queue": "one live item among historical and approved records",
        "business_traffic": "healthy",
    },
    expected_target={
        "status": "review_closed",
        "target_table_policy": "DEFAULT",
        "target_partition_policy": "DEFAULT",
        "placement_status": "no pending custom rule",
        "business_crc": "unchanged",
    },
    background_workload=_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=120,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.843478,
        reference_run_ids=(
            "reference-210__"
            "tidb_health_check_placement_policy__single_store_voters_pending__mock__r003",
        ),
    ),
    db=HC08_DB,
    target_table=HC08_TARGET_TABLE,
    customer_table=HC08_CUSTOMER_TABLE,
    event_table=HC08_EVENT_TABLE,
    archive_table=HC08_ARCHIVE_TABLE,
    service_table=HC08_SERVICE_TABLE,
    review_table=HC08_REVIEW_TABLE,
    policy_name=HC08_POLICY,
    customer_policy_name=HC08_CUSTOMER_POLICY,
    archive_policy_name=HC08_ARCHIVE_POLICY,
    constraint_policy_name=HC08_CONSTRAINT_POLICY,
    partition_name=HC08_PARTITION_NAME,
    review_key=HC08_REVIEW_KEY,
    service_name=HC08_SERVICE_NAME,
    business_rows=2000,
    partition_mode="table_and_partition",
)


_NEW_CASE = replace(
    _CASE,
    case_id="table_policy_inheritance_review",
    case_no=1,
    evaluator=TidbHealthCheckPlacementPolicyForTableInheritanceEvaluatorCase,
    title="A TiDB placement review for a table-level policy that blocks inherited placement convergence.",
    reference_report={
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": ["reset only the mapped target table policy to DEFAULT and closed the keyed review"],
            "verification": ["table placement converged, partitions remained inherited, and business truth was unchanged"],
        },
        "summary": "The table-level placement inheritance review completed with a precise object reset.",
    },
    alert=(
        "例行 placement review：服务目录把当前 open review 映射到一个 table-level custom policy，compact lane 无法收敛。"
        "请关联 service-to-table 目录、policy catalog、SHOW PLACEMENT 和健康近邻，确认只存在 table-level override。"
        "只把目标 table 恢复为 DEFAULT，保留分区继承、其它对象和业务数据，不重启组件或修改中心 policy 定义。"
    ),
    initial_state={
        "status": "routine_review_open",
        "queue": "one live table-policy item among historical records",
        "business_traffic": "healthy",
    },
    expected_target={
        "status": "review_closed",
        "target_table_policy": "DEFAULT",
        "partition_policy": "inherited",
        "placement_status": "converged",
        "business_crc": "unchanged",
    },
    review_key="fleet-review-20260808-014",
    policy_name="hc08_checkout_table_resilience",
    partition_mode="table_only",
    focused_fixture=True,
    background_workload=replace(_CASE.background_workload, worker_count=5, warmup_seconds=10),
    runtime=replace(_CASE.runtime, bootstrap_cache_enabled=False),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.428571,
        reference_run_ids=(
            "tidb-reference-11__"
            "tidb_health_check_placement_policy__"
            "table_policy_inheritance_review__mock__r001",
        ),
    ),
)


class TidbHealthCheckPlacementPolicyInjector(BaseFaultInjector):
    """Create a real single-store placement-policy compliance review."""

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        env = context.env
        require_sql_success(env.execute_sql(f"CREATE DATABASE {self.db}"), "create HC08 database")
        self._create_business_tables(env)
        self._create_placement_policies(env)
        self._create_control_tables(env)
        require_sql_success(
            env.execute_sql(
                f"ALTER TABLE {self.db}.{self.target_table} "
                f"PLACEMENT POLICY={self.policy_name}"
            ),
            "attach HC08 impossible placement policy",
        )
        if self.partition_mode == "table_and_partition":
            require_sql_success(
                env.execute_sql(
                    f"ALTER TABLE {self.db}.{self.target_table} PARTITION {self.partition_name} "
                    f"PLACEMENT POLICY={self.policy_name}"
                ),
                "attach HC08 current-partition placement policy",
            )
        self._verify_state(env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_state(context.env)
        self._capture_cluster_observations(context.env, "validate HC08 cluster topology")

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        env = context.env
        placement = self._wait_for_placement_state(env, self.target_table, "pending")
        cluster = self._capture_cluster_observations(env, "capture HC08 cluster observations")
        return {
            "business_truth": self._business_truth(env),
            "placement_before": placement,
            "placement_labels": self._query_result(
                env,
                "SHOW PLACEMENT LABELS",
                "capture HC08 placement labels",
            ),
            "cluster_services": cluster["services"],
            "store_list": cluster["stores"],
            "region_list": cluster["regions"],
            "operator_list": cluster["operators"],
            "scheduler_list": cluster["schedulers"],
            "pd_config": cluster["pd_config"],
            "review_queue": self._query_result(
                env,
                f"SELECT review_key, service_name, check_name, finding_state, status, opened_at "
                f"FROM {self.db}.{self.review_table} ORDER BY opened_at DESC",
                "capture HC08 review queue",
            ),
            "service_catalog": self._query_result(
                env,
                f"SELECT service_name, table_schema, table_name, owner_team, lane_profile "
                f"FROM {self.db}.{self.service_table} ORDER BY service_name",
                "capture HC08 service catalog",
            ),
            "table_policy_catalog": self._query_result(
                env,
                "SELECT TABLE_SCHEMA, TABLE_NAME, TIDB_PLACEMENT_POLICY_NAME "
                "FROM information_schema.tables "
                f"WHERE TABLE_SCHEMA = '{self.db}' ORDER BY TABLE_NAME",
                "capture HC08 table placement catalog",
            ),
            "partition_policy_catalog": self._query_result(
                env,
                "SELECT TABLE_SCHEMA, TABLE_NAME, PARTITION_NAME, "
                "TIDB_PLACEMENT_POLICY_NAME FROM information_schema.partitions "
                f"WHERE TABLE_SCHEMA = '{self.db}' AND TABLE_NAME = '{self.target_table}' "
                "ORDER BY PARTITION_NAME",
                "capture HC08 partition placement catalog",
            ),
            "policy_catalog": self._query_result(
                env,
                "SELECT * FROM information_schema.placement_policies ORDER BY POLICY_NAME",
                "capture HC08 placement policy catalog",
            ),
            "placement_catalog": self._query_result(
                env,
                "SHOW PLACEMENT",
                "capture HC08 placement catalog",
            ),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        return None

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        env = context.env
        target_rows = self._query_result(
            env,
            "SELECT TABLE_NAME FROM information_schema.tables "
            f"WHERE TABLE_SCHEMA = '{self.db}' AND TABLE_NAME = '{self.target_table}'",
            "check HC08 target table before recovery",
        )
        if target_rows:
            if self.partition_mode == "table_and_partition":
                require_sql_success(
                    env.execute_sql(
                        f"ALTER TABLE {self.db}.{self.target_table} PARTITION {self.partition_name} "
                        "PLACEMENT POLICY=DEFAULT"
                    ),
                    "detach HC08 partition placement policy during recovery",
                )
            require_sql_success(
                env.execute_sql(
                    f"ALTER TABLE {self.db}.{self.target_table} PLACEMENT POLICY=DEFAULT"
                ),
                "detach HC08 placement policy during recovery",
            )
        for table in self.tables:
            require_sql_success(
                env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"),
                f"drop HC08 table {self.db}.{table}",
            )
        for policy in self.policies:
            self._drop_policy_if_present(env, policy)
        require_sql_success(
            env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"),
            "drop HC08 database",
        )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.target_table = validate_sql_identifier(str(config["target_table"]), "target_table")
        self.customer_table = validate_sql_identifier(str(config["customer_table"]), "customer_table")
        self.event_table = validate_sql_identifier(str(config["event_table"]), "event_table")
        self.archive_table = validate_sql_identifier(str(config["archive_table"]), "archive_table")
        self.service_table = validate_sql_identifier(str(config["service_table"]), "service_table")
        self.review_table = validate_sql_identifier(str(config["review_table"]), "review_table")
        self.policy_name = validate_sql_identifier(str(config["policy_name"]), "policy_name")
        self.customer_policy_name = validate_sql_identifier(
            str(config["customer_policy_name"]), "customer_policy_name"
        )
        self.archive_policy_name = validate_sql_identifier(
            str(config["archive_policy_name"]), "archive_policy_name"
        )
        self.constraint_policy_name = validate_sql_identifier(
            str(config["constraint_policy_name"]), "constraint_policy_name"
        )
        self.partition_name = validate_sql_identifier(
            str(config["partition_name"]), "partition_name"
        )
        self.review_key = str(config["review_key"])
        self.service_name = str(config["service_name"])
        self.business_rows = int(config["business_rows"])
        self.partition_mode = str(config["partition_mode"])
        self.focused_fixture = bool(config["focused_fixture"])
        self.tables = (
            self.target_table,
            self.customer_table,
            self.event_table,
            self.archive_table,
            self.service_table,
            self.review_table,
        )
        self.policies = (
            (self.policy_name, self.archive_policy_name)
            if self.focused_fixture
            else (
                self.policy_name,
                self.customer_policy_name,
                self.archive_policy_name,
                self.constraint_policy_name,
            )
        )

    def _create_business_tables(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.customer_table} ("
                "customer_id BIGINT PRIMARY KEY, segment VARCHAR(24) NOT NULL, "
                "home_region VARCHAR(24) NOT NULL, active TINYINT NOT NULL, "
                "KEY idx_customer_segment (segment, customer_id)"
                ")"
            ),
            "create HC08 customer table",
        )
        customer_values = [
            f"({customer_id}, '{('enterprise', 'growth', 'standard', 'trial')[customer_id % 4]}', "
            f"'{('east', 'west', 'central', 'north')[customer_id % 4]}', "
            f"{1 if customer_id % 17 else 0})"
            for customer_id in range(1, 241)
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.customer_table} "
            "(customer_id, segment, home_region, active) VALUES ",
            customer_values,
            120,
            "load HC08 customers",
        )

        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.target_table} ("
                "order_id BIGINT PRIMARY KEY, customer_id BIGINT NOT NULL, "
                "warehouse_id INT NOT NULL, status VARCHAR(20) NOT NULL, "
                "created_at DATETIME NOT NULL, amount DECIMAL(12,2) NOT NULL, "
                "payload VARCHAR(48) NOT NULL, "
                "KEY idx_order_customer_status (customer_id, status), "
                "KEY idx_order_warehouse_time (warehouse_id, created_at)"
                ") PARTITION BY RANGE (order_id) ("
                "PARTITION p_checkout_history VALUES LESS THAN (1001), "
                "PARTITION p_checkout_current VALUES LESS THAN MAXVALUE"
                ")"
            ),
            "create HC08 placement target table",
        )
        order_values = []
        statuses = ("paid", "pending", "shipped", "cancelled", "review")
        for order_id in range(1, self.business_rows + 1):
            customer_id = (order_id - 1) % 240 + 1
            warehouse_id = (order_id - 1) % 9 + 1
            status = statuses[order_id % len(statuses)]
            day = (order_id - 1) % 28 + 1
            amount = 100 + (order_id * 37) % 99000
            order_values.append(
                f"({order_id}, {customer_id}, {warehouse_id}, '{status}', "
                f"'2026-07-{day:02d} 12:{order_id % 60:02d}:00', {amount / 100:.2f}, "
                f"'lane-{order_id % 23:02d}')"
            )
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.target_table} "
            "(order_id, customer_id, warehouse_id, status, created_at, amount, payload) VALUES ",
            order_values,
            200,
            "load HC08 placement target rows",
        )

        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.event_table} ("
                "event_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, "
                "event_type VARCHAR(24) NOT NULL, actor VARCHAR(24) NOT NULL, "
                "event_ts DATETIME NOT NULL, note VARCHAR(64) NOT NULL, "
                "KEY idx_event_order (order_id, event_type), KEY idx_event_time (event_ts)"
                ")"
            ),
            "create HC08 event table",
        )
        event_values = [
            f"({event_id}, {(event_id - 1) % self.business_rows + 1}, "
            f"'{('created', 'packed', 'shipped', 'audited', 'returned')[event_id % 5]}', "
            f"'{('checkout', 'warehouse', 'carrier', 'risk', 'support')[event_id % 5]}', "
            f"'2026-07-{(event_id - 1) % 28 + 1:02d} 13:{event_id % 60:02d}:00', "
            f"'normal business event {event_id % 31:02d}')"
            for event_id in range(1, self.business_rows * 3 + 1)
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.event_table} "
            "(event_id, order_id, event_type, actor, event_ts, note) VALUES ",
            event_values,
            300,
            "load HC08 order events",
        )

        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.archive_table} ("
                "archive_id BIGINT PRIMARY KEY, source_order_id BIGINT NOT NULL, "
                "archive_month CHAR(7) NOT NULL, amount DECIMAL(12,2) NOT NULL, "
                "retention_class VARCHAR(24) NOT NULL, "
                "KEY idx_archive_month (archive_month, source_order_id)"
                ")"
            ),
            "create HC08 archive table",
        )
        archive_values = [
            f"({archive_id}, {archive_id * 3}, "
            f"'2026-{(archive_id - 1) % 6 + 1:02d}', "
            f"{(2500 + archive_id * 19) / 100:.2f}, "
            f"'{('standard', 'legal_hold', 'finance')[archive_id % 3]}')"
            for archive_id in range(1, 401)
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.archive_table} "
            "(archive_id, source_order_id, archive_month, amount, retention_class) VALUES ",
            archive_values,
            200,
            "load HC08 archive rows",
        )

    def _create_placement_policies(self, env) -> None:
        if not self.focused_fixture:
            require_sql_success(
                env.execute_sql(
                    f"CREATE PLACEMENT POLICY {self.customer_policy_name} "
                    'PRIMARY_REGION="compact-a" REGIONS="compact-a,compact-b" '
                    'SCHEDULE="EVEN" FOLLOWERS=1'
                ),
                "create HC08 customer locality policy",
            )
            require_sql_success(
                env.execute_sql(
                    f"CREATE PLACEMENT POLICY {self.constraint_policy_name} "
                    "FOLLOWER_CONSTRAINTS='{\"+zone=single-store\": 2}'"
                ),
                "create HC08 dictionary constraint policy",
            )
        require_sql_success(
            env.execute_sql(
                f"CREATE PLACEMENT POLICY {self.archive_policy_name} FOLLOWERS=2"
            ),
            "create HC08 archive exception policy",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE PLACEMENT POLICY {self.policy_name} FOLLOWERS=2"
            ),
            "create HC08 single-store policy",
        )
        require_sql_success(
            env.execute_sql(
                f"ALTER TABLE {self.db}.{self.archive_table} "
                f"PLACEMENT POLICY={self.archive_policy_name}"
            ),
            "attach HC08 approved archive exception policy",
        )

    def _create_control_tables(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.service_table} ("
                "service_name VARCHAR(64) PRIMARY KEY, table_schema VARCHAR(64) NOT NULL, "
                "table_name VARCHAR(64) NOT NULL, owner_team VARCHAR(64) NOT NULL, "
                "lane_profile VARCHAR(32) NOT NULL, definition_owner VARCHAR(64) NOT NULL, "
                "updated_at DATETIME NOT NULL"
                ")"
            ),
            "create HC08 service catalog",
        )
        service_rows = (
            f"('{self.service_name}', '{self.db}', '{self.target_table}', "
            "'checkout-platform', 'compact', 'platform-placement', '2026-08-07 08:40:00'),"
            f"('order-history', '{self.db}', '{self.archive_table}', "
            "'data-retention', 'compact', 'platform-placement', '2026-08-07 08:28:00')"
        )
        if not self.focused_fixture:
            service_rows += (
                f",('customer-profile', '{self.db}', '{self.customer_table}', "
                "'identity-platform', 'compact', 'platform-placement', '2026-08-07 08:35:00'),"
                f"('fulfillment-events', '{self.db}', '{self.event_table}', "
                "'warehouse-platform', 'compact', 'platform-placement', '2026-08-07 08:32:00')"
            )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.service_table} "
                "(service_name, table_schema, table_name, owner_team, lane_profile, "
                f"definition_owner, updated_at) VALUES {service_rows}"
            ),
            "load HC08 service catalog",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.review_table} ("
                "review_id BIGINT UNIQUE NOT NULL, review_key VARCHAR(96) PRIMARY KEY, "
                "service_name VARCHAR(64) NOT NULL, "
                "check_name VARCHAR(64) NOT NULL, finding_state VARCHAR(32) NOT NULL, "
                "status VARCHAR(24) NOT NULL, opened_at DATETIME NOT NULL, "
                "change_boundary VARCHAR(128) NOT NULL, resolution VARCHAR(512), "
                "verification VARCHAR(512), updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                "KEY idx_review_status_time (status, opened_at), "
                "KEY idx_review_service (service_name, check_name)"
                ")"
            ),
            "create HC08 review table",
        )
        review_rows = (
            f"(42, '{self.review_key}', '{self.service_name}', 'replica-goal-convergence', "
            "'needs_review', 'open', '2026-08-07 09:15:00', "
            "'service-owned object metadata only', NULL, NULL),"
            "(117, 'fleet-review-20260806-117', 'order-history', 'retention-locality', "
            "'approved_exception', 'waived', '2026-08-06 16:20:00', "
            "'centrally owned definition', 'exception retained', 'scheduled')"
        )
        if not self.focused_fixture:
            review_rows += (
                ",(31, 'fleet-review-20260807-031', 'customer-profile', 'locality-conformance', "
                "'healthy', 'closed', '2026-08-07 08:50:00', "
                "'centrally owned definition', 'no change required', 'scheduled'),"
                "(83, 'fleet-review-20260806-083', 'fulfillment-events', 'inheritance-check', "
                "'healthy', 'closed', '2026-08-06 11:05:00', "
                "'service-owned object metadata only', 'no change required', 'inherited')"
            )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.review_table} "
                "(review_id, review_key, service_name, check_name, finding_state, status, opened_at, "
                f"change_boundary, resolution, verification) VALUES {review_rows}"
            ),
            "load HC08 fleet reviews",
        )

    def _drop_policy_if_present(self, env, policy: str) -> None:
        rows = self._query_result(
            env,
            "SELECT POLICY_NAME FROM information_schema.placement_policies "
            f"WHERE POLICY_NAME = '{policy}'",
            f"check HC08 policy before recovery: policy={policy}",
        )
        if len(rows) > 1:
            raise RuntimeError(
                "HC08 policy catalog returned duplicate rows during recovery: "
                f"policy={policy!r}, rows={rows!r}"
            )
        if rows:
            require_sql_success(
                env.execute_sql(f"DROP PLACEMENT POLICY {policy}"),
                f"drop HC08 policy {policy}",
            )

    def _insert_batches(self, env, prefix: str, values: list[str], batch_size: int, context: str) -> None:
        for start in range(0, len(values), batch_size):
            batch = values[start:start + batch_size]
            require_sql_success(
                env.execute_sql(prefix + ",".join(batch)),
                f"{context} batch={start // batch_size + 1}",
            )

    def _query_result(self, env, sql: str, context: str) -> list:
        payload = json_object(env.execute_sql(sql), context)
        if payload.get("status") != "success":
            raise RuntimeError(f"{context} returned a non-success payload: {payload!r}")
        return payload["result"]

    def _capture_cluster_observations(self, env, context: str) -> dict[str, object]:
        services = json_object(
            env.manage_cluster("service", "list"),
            f"{context}: service/list",
        )
        tikv_targets = sorted(
            target
            for target in services["result"]["nodes"]
            if target.startswith("tikv/")
        )
        if len(tikv_targets) != 1:
            raise RuntimeError(
                f"{context} expected exactly one TiKV service: "
                f"tikv_targets={tikv_targets!r}, services={services!r}"
            )
        stores = json_object(
            env.manage_cluster("store", "list"),
            f"{context}: store/list",
        )
        if len(stores["result"]["stores"]) != 1:
            raise RuntimeError(
                f"{context} expected exactly one PD Store: stores={stores!r}"
            )
        return {
            "services": services,
            "stores": stores,
            "regions": json_object(
                env.manage_cluster("region", "list", target=tikv_targets[0]),
                f"{context}: region/list target={tikv_targets[0]}",
            ),
            "operators": json_object(
                env.manage_cluster("operator", "list"),
                f"{context}: operator/list",
            ),
            "schedulers": json_object(
                env.manage_cluster("scheduler", "list"),
                f"{context}: scheduler/list",
            ),
            "pd_config": json_object(
                env.manage_cluster("config", "get", target="pd"),
                f"{context}: config/get target=pd",
            ),
        }

    def _business_truth(self, env) -> list:
        return self._query_result(
            env,
            f"SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, customer_id, warehouse_id, "
            "status, created_at, amount, payload))), 0) "
            f"FROM {self.db}.{self.target_table}",
            "capture HC08 business truth",
        )

    def _wait_for_placement_state(self, env, table: str, expected_state: str) -> list:
        deadline = time.monotonic() + 60
        latest = None
        sql = f"SHOW PLACEMENT FOR TABLE {self.db}.{table}"
        while time.monotonic() < deadline:
            latest = self._query_result(env, sql, "inspect HC08 placement state")
            states = [str(row[-1]).casefold() for row in latest]
            if states and all(state == expected_state.casefold() for state in states):
                return latest
            time.sleep(1)
        raise RuntimeError(
            "HC08 placement did not reach the expected state within 60 seconds: "
            f"table={self.db}.{table}, expected_state={expected_state!r}, latest={latest!r}"
        )

    def _verify_state(self, env) -> None:
        bindings = self._query_result(
            env,
            "SELECT TABLE_NAME, TIDB_PLACEMENT_POLICY_NAME "
            "FROM information_schema.tables "
            f"WHERE TABLE_SCHEMA = '{self.db}' AND TABLE_NAME IN "
            f"('{self.target_table}', '{self.customer_table}', '{self.archive_table}') "
            "ORDER BY TABLE_NAME",
            "verify HC08 policy bindings",
        )
        expected = sorted([
            [self.target_table, self.policy_name],
            [self.customer_table, None],
            [self.archive_table, self.archive_policy_name],
        ])
        if bindings != expected:
            raise RuntimeError(
                "HC08 policy binding mismatch: "
                f"expected={expected!r}, observed={bindings!r}"
            )
        partitions = self._query_result(
            env,
            "SELECT PARTITION_NAME, TIDB_PLACEMENT_POLICY_NAME "
            "FROM information_schema.partitions "
            f"WHERE TABLE_SCHEMA = '{self.db}' AND TABLE_NAME = '{self.target_table}' "
            "ORDER BY PARTITION_NAME",
            "verify HC08 partition policy bindings",
        )
        expected_partitions = (
            [[self.partition_name, self.policy_name], ["p_checkout_history", None]]
            if self.partition_mode == "table_and_partition"
            else [[self.partition_name, None], ["p_checkout_history", None]]
        )
        if partitions != expected_partitions:
            raise RuntimeError(
                "HC08 partition policy binding mismatch: "
                f"expected={expected_partitions!r}, observed={partitions!r}"
            )
        business = self._business_truth(env)
        if len(business) != 1 or int(business[0][0]) != self.business_rows:
            raise RuntimeError(
                "HC08 business fixture row count mismatch: "
                f"expected={self.business_rows}, observed={business!r}"
            )
        self._wait_for_placement_state(env, self.target_table, "pending")
        self._wait_for_placement_state(env, self.archive_table, "pending")


class TidbHealthCheckPlacementPolicyScenario(TiDBScenario):
    scenario_id = "tidb_health_check_placement_policy"
    description = (
        "Routine TiDB placement-compliance health check that requires correlating "
        "object policy inheritance, asynchronous placement state, fixed-version knowledge, "
        "and unchanged business truth under real query noise."
    )
    cases = (_CASE, _NEW_CASE)

    def build_fault_plan(
        self,
        case: TidbHealthCheckPlacementPolicyCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbHealthCheckPlacementPolicyInjector,
                config={
                    "db": case.db,
                    "target_table": case.target_table,
                    "customer_table": case.customer_table,
                    "event_table": case.event_table,
                    "archive_table": case.archive_table,
                    "service_table": case.service_table,
                    "review_table": case.review_table,
                    "policy_name": case.policy_name,
                    "customer_policy_name": case.customer_policy_name,
                    "archive_policy_name": case.archive_policy_name,
                    "constraint_policy_name": case.constraint_policy_name,
                    "partition_name": case.partition_name,
                    "review_key": case.review_key,
                    "service_name": case.service_name,
                    "business_rows": case.business_rows,
                    "partition_mode": case.partition_mode,
                    "focused_fixture": case.focused_fixture,
                },
            ),
        )
