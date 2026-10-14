from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.business_change.x86_arm64_migration import (
    TidbBusinessChangeX86Arm64MigrationEvaluatorCase,
    TidbBusinessChangeX86Arm64MigrationForBillingEvaluatorCase,
)
from src.protocols.report import structured_reference_report
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


def _business_workload(
    *,
    business_scope: str,
    control_db: str,
    business_db: str,
    intents_table: str,
    orders_table: str,
    state_table: str,
    artifacts_table: str,
    nodes_table: str,
    monitor_table: str,
) -> tuple[WorkloadProfile, ...]:
    business_prefix = business_scope.removesuffix("-api").replace("-", "_")
    return (
        WorkloadProfile(
            name=f"{business_prefix}_intent_writer",
            sql=(
                f"INSERT INTO {control_db}.{intents_table} "
                f"(customer_id, amount_cents, request_source) VALUES "
                f"(FLOOR(1 + RAND() * 5000), FLOOR(100 + RAND() * 9900), '{business_scope}')"
            ),
            qps=0.45,
            tier="BUSINESS_WRITE",
            commit=True,
                application_name=business_scope,
        ),
        WorkloadProfile(
            name=f"{business_prefix}_recent_lookup",
            sql=(
                f"SELECT order_id, status, amount_cents FROM {business_db}.{orders_table} "
                "WHERE tenant_id BETWEEN 11 AND 35 ORDER BY updated_at DESC LIMIT 32"
            ),
            qps=0.3,
            tier="BUSINESS_READ",
                application_name=business_scope,
        ),
        WorkloadProfile(
            name=f"{business_prefix}_reconciliation_rollup",
            sql=(
                f"SELECT status, COUNT(*), SUM(amount_cents) FROM {business_db}.{orders_table} "
                "GROUP BY status ORDER BY status"
            ),
            qps=0.18,
            tier="BUSINESS_READ",
                application_name=f"{business_prefix}-reconciliation",
        ),
        WorkloadProfile(
            name="migration_state_dashboard",
            sql=(
                f"SELECT migration_id, business_scope, request_status, phase, active_arch, "
                f"target_arch, p95_latency_ms, rollback_ready FROM {control_db}.{state_table}"
            ),
            qps=0.3,
            tier="CONTROL_READ",
            application_name="migration-dashboard",
        ),
        WorkloadProfile(
            name="offline_artifact_inventory_decoy",
            sql=(
                f"SELECT component, arch, version, available, digest_verified, compatible "
                f"FROM {control_db}.{artifacts_table} ORDER BY component, arch"
            ),
            qps=0.2,
            tier="CONTROL_READ",
            application_name="release-audit",
        ),
        WorkloadProfile(
            name="component_architecture_inventory_decoy",
            sql=(
                f"SELECT migration_id, node_id, component, arch, state, generation, leader, region_count "
                f"FROM {control_db}.{nodes_table} ORDER BY component, node_id"
            ),
            qps=0.2,
            tier="CONTROL_READ",
            application_name="cluster-inventory",
        ),
        WorkloadProfile(
            name="prometheus_history_retention_probe",
            sql=(
                f"SELECT metric_name, COUNT(*), MIN(recorded_at), MAX(recorded_at) "
                f"FROM {control_db}.{monitor_table} GROUP BY metric_name"
            ),
            qps=0.15,
            tier="MONITOR_READ",
            application_name="monitoring-audit",
        ),
        WorkloadProfile(
            name="business_checksum_probe",
            sql=(
                f"SELECT COUNT(*), SUM(order_id), SUM(amount_cents), SUM(tenant_id) "
                f"FROM {business_db}.{orders_table}"
            ),
            qps=0.14,
            tier="BUSINESS_INTEGRITY",
                application_name=f"{business_prefix}-integrity-audit",
        ),
        WorkloadProfile(
            name="historical_release_manifest_decoy",
            sql=(
                f"SELECT component, arch, version, available FROM {control_db}.{artifacts_table} "
                "WHERE version <> 'v8.1.0' ORDER BY component"
            ),
            qps=0.12,
            tier="DECOY_READ",
            application_name="legacy-release-audit",
        ),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeX86Arm64MigrationCase(TiDBScenarioCase):
    control_db: str
    business_db: str
    orders_table: str
    intents_table: str
    events_table: str
    state_table: str
    artifacts_table: str
    nodes_table: str
    actions_table: str
    runbook_table: str
    monitor_table: str
    backups_table: str
    audit_table: str
    migration_id: str
    rehearsal_migration_id: str
    business_scope: str
    rehearsal_scope: str
    source_arch: str
    target_arch: str
    component_names: tuple[str, ...]
    node_counts: tuple[tuple[str, int], ...]
    seed_rows: int
    minimum_processed_intents: int
    expected_seed_amount_cents: int
    expected_seed_tenant_sum: int
    monitor_history_rows: int
    latency_slo_ms: float
    action_poll_interval_seconds: float
    final_state_attempts: int
    final_state_interval_seconds: float
    reference_path: tuple[str, ...]
    reference_tool_counts: tuple[tuple[str, int, int], ...]


class TidbBusinessChangeX86Arm64MigrationForOfflineOnlineMigrationScenarioCase(
    TidbBusinessChangeX86Arm64MigrationCase
):
    pass


_CASE = TidbBusinessChangeX86Arm64MigrationForOfflineOnlineMigrationScenarioCase(
    case_id="offline_x86_to_arm64_online_migration",
    reference_report=structured_reference_report(
        case_id="offline_x86_to_arm64_online_migration",
        factors=(),
        changes=(
            "selected the checkout migration scope and excluded the concurrent analytics rehearsal",
            "merged and verified the offline arm64 mirror digest and compatibility metadata",
            "backed up TiUP metadata and preserved Prometheus history",
            "migrated PD one member at a time and rebalanced TiKV Regions",
            "cut over TiDB traffic to arm64 with a rollback point",
        ),
        verification=(
            "business checksum and online request queue were verified",
            "p95 SLO, component state, monitoring history, and RPO=0 were verified",
        ),
        summary="The reference path completed the offline architecture migration and verified RPO-zero continuity.",
    ),
    case_no=0,
    evaluator=TidbBusinessChangeX86Arm64MigrationEvaluatorCase,
    title=(
        "Offline x86 to arm64 online migration with staged component replacement, "
        "business consistency, and rollback readiness."
    ),
    alert=(
        "[CHANGE] 订单集群必须在无互联网的维护窗口内完成从 x86 到 arm64 的在线迁移。"
        "业务不能停写，目标架构只能使用现场离线包；请先核对离线镜像目录、版本兼容性、"
        "TiUP 集群元数据备份和监控历史保留，再按监控、PD、TiKV、TiDB 的顺序分批迁移。"
        "PD 成员一次只能处理一个，TiKV 必须观察 Region/leader 均衡后才能退役旧节点，"
        "切流前必须保留可回退点。提交前用真实业务查询验证原有订单没有变化、在线请求没有丢失、"
        "查询 p95 不超过 250ms、监控历史仍可查，并确认所有 x86 节点已安全退役。"
        "环境含有旧版本镜像、历史监控、归档元数据和在线订单查询噪声；不能访问互联网，"
        "不能直接停止节点、修改业务数据或跳过一致性校验。"
    ),
    initial_state={
        "internet_access": "blocked",
        "active_architecture": "x86",
        "offline_bundle": "present_but_unverified",
        "monitoring_history": "on_x86",
        "pd_members": 3,
        "tikv_nodes": 3,
        "tidb_nodes": 2,
        "online_writes": True,
    },
    expected_target={
        "active_architecture": "arm64",
        "source_nodes": "retired",
        "target_nodes": "active",
        "monitoring_history_preserved": True,
        "business_checksum_preserved": True,
        "rollback_ready": True,
        "rpo": "0",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_business_workload(
            business_scope="checkout-api",
            control_db="bc08_control",
            business_db="bc08_business",
            intents_table="order_intents",
            orders_table="orders",
            state_table="migration_state",
            artifacts_table="offline_artifacts",
            nodes_table="migration_nodes",
            monitor_table="monitor_history",
        ),
        worker_count=5,
        seed=0xBC08,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=5.0,
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=180,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.949239,
        reference_run_ids=(
            "reference-162__"
            "tidb_business_change_x86_arm64_migration__"
            "offline_x86_to_arm64_online_migration__mock__r001",
        ),
    ),
    control_db="bc08_control",
    business_db="bc08_business",
    orders_table="orders",
    intents_table="order_intents",
    events_table="order_events",
    state_table="migration_state",
    artifacts_table="offline_artifacts",
    nodes_table="migration_nodes",
    actions_table="migration_actions",
    runbook_table="migration_runbook",
    monitor_table="monitor_history",
    backups_table="migration_backups",
    audit_table="migration_audit",
    migration_id="checkout-x86-arm64-20260802",
    rehearsal_migration_id="analytics-x86-arm64-20260802",
    business_scope="checkout-api",
    rehearsal_scope="analytics-api",
    source_arch="x86",
    target_arch="arm64",
    component_names=("tiup", "pd", "tikv", "tidb", "prometheus", "grafana", "alertmanager"),
    node_counts=(("pd", 3), ("tikv", 3), ("tidb", 2)),
    seed_rows=1800,
    minimum_processed_intents=8,
    expected_seed_amount_cents=51830600,
    expected_seed_tenant_sum=115628,
    monitor_history_rows=240,
    latency_slo_ms=250.0,
    action_poll_interval_seconds=0.2,
    final_state_attempts=20,
    final_state_interval_seconds=0.25,
    reference_path=(
        "online checkout traffic requires an architecture change without stopping writes",
        "the active migration scope matches checkout traffic rather than the concurrent rehearsal scope",
        "offline artifacts, compatibility, and rollback metadata are complete for arm64",
        "monitoring history and TiUP cluster metadata are available on the target side",
        "PD members move one at a time and the arm64 leader is confirmed",
        "TiKV Regions rebalance before x86 stores retire and TiDB target nodes accept traffic",
        "arm64 owns the cluster, x86 is retired, and checksum/SLO/rollback evidence closes the change",
    ),
    reference_tool_counts=(
        ("query_metrics", 5, 70),
        ("execute_sql", 10, 238),
        ("read_log", 2, 28),
        ("node_and_component_state", 3, 38),
    ),
)


_BILLING_CASE = replace(
    _CASE,
    case_id="offline_x86_to_arm64_billing_migration",
    case_no=1,
    evaluator=TidbBusinessChangeX86Arm64MigrationForBillingEvaluatorCase,
    reference_report=structured_reference_report(
        case_id="offline_x86_to_arm64_billing_migration",
        factors=(),
        changes=(
            "selected the billing migration scope and excluded the concurrent fraud rehearsal scope",
            "merged and verified the offline arm64 billing bundle and compatibility metadata",
            "backed up TiUP metadata and preserved billing monitoring history",
            "migrated PD one member at a time and rebalanced billing TiKV Regions",
            "cut over billing traffic to arm64 with a rollback point",
        ),
        verification=(
            "billing business checksum and online payment intent queue were verified",
            "p95 SLO, component state, monitoring history, and RPO=0 were verified",
        ),
        summary="The reference path completed the billing architecture migration and verified RPO-zero continuity.",
    ),
    title=(
        "Offline x86 to arm64 billing migration with staged component replacement, "
        "payment consistency, and rollback readiness."
    ),
    alert=(
        "[CHANGE] 结算集群必须在无互联网的维护窗口内完成从 x86 到 arm64 的在线迁移。"
        "billing-api 不能停写，目标架构只能使用现场离线包；请先核对离线镜像目录、版本兼容性、"
        "TiUP 集群元数据备份和监控历史保留，再按监控、PD、TiKV、TiDB 的顺序分批迁移。"
        "PD 成员一次只能处理一个，TiKV 必须观察 Region/leader 均衡后才能退役旧节点，"
        "切流前必须保留可回退点。提交前用真实支付查询验证原有账单没有变化、在线请求没有丢失、"
        "查询 p95 不超过 250ms、监控历史仍可查，并确认所有 x86 节点已安全退役。"
        "环境含有旧版本镜像、历史监控、归档元数据和在线支付查询噪声；不能访问互联网，"
        "不能直接停止节点、修改业务数据或跳过一致性校验。"
    ),
    initial_state={
        "internet_access": "blocked",
        "active_architecture": "x86",
        "offline_bundle": "present_but_unverified",
        "monitoring_history": "on_x86",
        "pd_members": 3,
        "tikv_nodes": 3,
        "tidb_nodes": 2,
        "online_writes": True,
    },
    expected_target={
        "active_architecture": "arm64",
        "source_nodes": "retired",
        "target_nodes": "active",
        "monitoring_history_preserved": True,
        "business_checksum_preserved": True,
        "rollback_ready": True,
        "rpo": "0",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_business_workload(
            business_scope="billing-api",
            control_db="bc08_billing_control",
            business_db="bc08_billing_business",
            intents_table="billing_intents",
            orders_table="billing_orders",
            state_table="billing_migration_state",
            artifacts_table="billing_offline_artifacts",
            nodes_table="billing_migration_nodes",
            monitor_table="billing_monitor_history",
        ),
        worker_count=3,
        seed=0xBC09,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=5.0,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.0,
        reference_run_ids=(
            "tidb-reference-12__"
            "tidb_business_change_x86_arm64_migration__offline_x86_to_arm64_billing_migration__"
            "mock__r001",
        ),
    ),
    control_db="bc08_billing_control",
    business_db="bc08_billing_business",
    orders_table="billing_orders",
    intents_table="billing_intents",
    events_table="billing_events",
    state_table="billing_migration_state",
    artifacts_table="billing_offline_artifacts",
    nodes_table="billing_migration_nodes",
    actions_table="billing_migration_actions",
    runbook_table="billing_migration_runbook",
    monitor_table="billing_monitor_history",
    backups_table="billing_migration_backups",
    audit_table="billing_migration_audit",
    migration_id="billing-x86-arm64-20260812",
    rehearsal_migration_id="fraud-x86-arm64-20260812",
    business_scope="billing-api",
    rehearsal_scope="fraud-api",
    source_arch="x86",
    target_arch="arm64",
    component_names=("tiup", "pd", "tikv", "tidb", "prometheus", "grafana", "alertmanager"),
    node_counts=(("pd", 3), ("tikv", 3), ("tidb", 2)),
    seed_rows=1800,
    minimum_processed_intents=8,
    expected_seed_amount_cents=51830600,
    expected_seed_tenant_sum=115628,
    monitor_history_rows=240,
    latency_slo_ms=250.0,
    action_poll_interval_seconds=0.05,
    final_state_attempts=20,
    final_state_interval_seconds=0.25,
    reference_path=(
        "online billing traffic requires an architecture change without stopping writes",
        "one readiness read confirms the billing scope against the concurrent fraud rehearsal, offline "
        "arm64 bundle compatibility, the TiUP metadata backup, and monitoring-history retention",
        "staged monitoring, PD, TiKV, and TiDB replacement ends with x86 retired behind a rollback point, "
        "and checksum, SLO, and RPO=0 evidence closes the change",
    ),
    reference_tool_counts=(
        ("query_metrics", 93, 0),
        ("execute_sql", 121, 0),
        ("node_and_component_state", 8, 0),
    ),
)


class TidbBusinessChangeX86Arm64MigrationScenario(TiDBScenario):
    scenario_id = "tidb_business_change_x86_arm64_migration"
    description = (
        "Runs an offline x86-to-arm64 migration control plane with real TiDB business workload, "
        "component sequencing, monitoring retention, and rollback validation."
    )
    cases = (_CASE, _BILLING_CASE)

    def build_fault_plan(
        self,
        case: TidbBusinessChangeX86Arm64MigrationCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbBusinessChangeX86Arm64MigrationInjector,
                config={
                    "control_db": case.control_db,
                    "business_db": case.business_db,
                    "orders_table": case.orders_table,
                    "intents_table": case.intents_table,
                    "events_table": case.events_table,
                    "state_table": case.state_table,
                    "artifacts_table": case.artifacts_table,
                    "nodes_table": case.nodes_table,
                    "actions_table": case.actions_table,
                    "runbook_table": case.runbook_table,
                    "monitor_table": case.monitor_table,
                    "backups_table": case.backups_table,
                    "audit_table": case.audit_table,
                    "migration_id": case.migration_id,
                    "rehearsal_migration_id": case.rehearsal_migration_id,
                    "business_scope": case.business_scope,
                    "rehearsal_scope": case.rehearsal_scope,
                    "source_arch": case.source_arch,
                    "target_arch": case.target_arch,
                    "component_names": case.component_names,
                    "node_counts": case.node_counts,
                    "seed_rows": case.seed_rows,
                    "minimum_processed_intents": case.minimum_processed_intents,
                    "expected_seed_amount_cents": case.expected_seed_amount_cents,
                    "expected_seed_tenant_sum": case.expected_seed_tenant_sum,
                    "monitor_history_rows": case.monitor_history_rows,
                    "latency_slo_ms": case.latency_slo_ms,
                    "action_poll_interval_seconds": case.action_poll_interval_seconds,
                },
            ),
        )

from collections.abc import Mapping
from datetime import datetime, timedelta
import threading

import pymysql

from src.database.sql import execute_result_rows

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    connect_tidb,
    require_sql_success,
    validate_sql_identifier,
)


_TRANSIENT_DATABASE_ERROR_CODES = {2003, 2006, 2013, 2055, 9001}


def _is_transient_database_error(error: BaseException) -> bool:
    if isinstance(error, pymysql.err.InterfaceError):
        return True
    return (
        isinstance(error, pymysql.err.OperationalError)
        and bool(error.args)
        and error.args[0] in _TRANSIENT_DATABASE_ERROR_CODES
    )


class ActionRejected(Exception):
    """A submitted migration command cannot advance the current state."""


class ActionBlocked(Exception):
    """A submitted migration command is waiting for a live operational gate."""


class TidbBusinessChangeX86Arm64MigrationInjector(BaseFaultInjector):
    """Run a real SQL-backed offline architecture migration control plane.

    The Docker lane cannot run amd64 and arm64 binaries in one local cluster. The
    controller therefore models the host-side migration state in TiDB tables while
    the business rows, online writes, monitoring samples, and action processing are
    real database operations. It never relabels a running container as arm64.
    """

    def __init__(self):
        self._thread = None
        self._stop_event = None
        self._worker_error = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._create_databases()
        self._create_tables()
        self._seed_business_data()
        self._seed_control_plane()
        self._verify_initial_state()
        self._start_controller()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._verify_persistent_state()
        self._start_controller()

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config, context.env)
        self._verify_persistent_state()
        return {
            "bc08_migration_state": self._rows(
                f"SELECT migration_id, business_scope, request_status, phase, source_arch, target_arch, active_arch, "
                f"bundle_verified, tiup_metadata_backup, monitoring_history_copied, "
                f"rollback_ready FROM {self.control_db}.{self.state_table}",
                "capture BC08 migration state",
            ),
            "bc08_offline_artifacts": self._rows(
                f"SELECT component, arch, version, available, digest_verified, compatible, "
                f"history_copied FROM {self.control_db}.{self.artifacts_table} "
                "ORDER BY component, arch",
                "capture BC08 offline artifacts",
            ),
            "bc08_component_nodes": self._rows(
                f"SELECT migration_id, node_id, component, arch, state, generation, leader, region_count "
                f"FROM {self.control_db}.{self.nodes_table} ORDER BY component, node_id",
                "capture BC08 component nodes",
            ),
            "bc08_business_baseline": self._rows(
                f"SELECT COUNT(*), SUM(order_id), SUM(amount_cents), SUM(tenant_id) "
                f"FROM {self.business_db}.{self.orders_table} WHERE order_id <= {self.seed_rows}",
                "capture BC08 business baseline",
            ),
            "bc08_monitor_history": self._rows(
                f"SELECT COUNT(*), COUNT(DISTINCT metric_name), MIN(recorded_at), MAX(recorded_at) "
                f"FROM {self.control_db}.{self.monitor_table}",
                "capture BC08 monitoring history",
            ),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._stop_controller(raise_worker_error=True)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        worker_error = self._stop_controller(raise_worker_error=False)
        for database in (self.control_db, self.business_db):
            self._sql(f"DROP DATABASE IF EXISTS {database}", f"drop BC08 database {database}")
        if worker_error is not None:
            raise RuntimeError(
                f"BC08 migration controller failed before recovery: "
                f"migration_id={self.migration_id!r}, error={worker_error!r}"
            ) from worker_error

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.control_db = validate_sql_identifier(str(config["control_db"]), "control_db")
        self.business_db = validate_sql_identifier(str(config["business_db"]), "business_db")
        for attribute in (
            "orders_table", "intents_table", "events_table", "state_table", "artifacts_table",
            "nodes_table", "actions_table", "runbook_table", "monitor_table", "backups_table",
            "audit_table",
        ):
            setattr(self, attribute, validate_sql_identifier(str(config[attribute]), attribute))
        self.migration_id = str(config["migration_id"])
        self.rehearsal_migration_id = str(config["rehearsal_migration_id"])
        self.business_scope = str(config["business_scope"])
        self.rehearsal_scope = str(config["rehearsal_scope"])
        self.source_arch = str(config["source_arch"])
        self.target_arch = str(config["target_arch"])
        self.component_names = tuple(str(value) for value in config["component_names"])
        self.node_counts = {str(component): int(count) for component, count in config["node_counts"]}
        self.seed_rows = int(config["seed_rows"])
        self.minimum_processed_intents = int(config["minimum_processed_intents"])
        self.expected_seed_amount_cents = int(config["expected_seed_amount_cents"])
        self.expected_seed_tenant_sum = int(config["expected_seed_tenant_sum"])
        self.monitor_history_rows = int(config["monitor_history_rows"])
        self.latency_slo_ms = float(config["latency_slo_ms"])
        self.action_poll_interval_seconds = float(config["action_poll_interval_seconds"])
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        expected_components = {"tiup", "pd", "tikv", "tidb", "prometheus", "grafana", "alertmanager"}
        if set(self.component_names) != expected_components:
            raise ValueError(
                f"BC08 component inventory mismatch: expected={sorted(expected_components)}, "
                f"actual={sorted(self.component_names)}"
            )
        if self.source_arch == self.target_arch:
            raise ValueError(f"BC08 source and target architectures must differ: arch={self.source_arch!r}")
        if self.migration_id == self.rehearsal_migration_id:
            raise ValueError(
                f"BC08 target and rehearsal migrations must differ: migration_id={self.migration_id!r}"
            )
        if self.business_scope == self.rehearsal_scope:
            raise ValueError(
                f"BC08 target and rehearsal scopes must differ: business_scope={self.business_scope!r}"
            )
        if (
            self.seed_rows <= 0
            or self.minimum_processed_intents <= 0
            or self.monitor_history_rows <= 0
            or self.latency_slo_ms <= 0
        ):
            raise ValueError(
                "BC08 positive runtime values required: "
                f"seed_rows={self.seed_rows}, minimum_processed_intents={self.minimum_processed_intents}, "
                f"monitor_history_rows={self.monitor_history_rows}, "
                f"latency_slo_ms={self.latency_slo_ms}"
            )
        if set(self.node_counts) != {"pd", "tikv", "tidb"} or any(value <= 0 for value in self.node_counts.values()):
            raise ValueError(f"BC08 node layout is invalid: node_counts={self.node_counts!r}")

    def _connect(self, database: str | None = None, *, autocommit: bool = True):
        return connect_tidb(
            self.env,
            database=database,
            autocommit=autocommit,
            read_timeout=35,
            write_timeout=35,
        )

    def _sql(self, sql: str, context: str) -> dict:
        return require_sql_success(self.env.execute_sql(sql), f"{context}: sql={sql!r}")

    def _rows(self, sql: str, context: str) -> list:
        return execute_result_rows(self.env.execute_sql, sql, context)

    def _create_databases(self) -> None:
        for database in (self.control_db, self.business_db):
            self._sql(f"DROP DATABASE IF EXISTS {database}", f"clear BC08 database {database}")
            self._sql(f"CREATE DATABASE {database}", f"create BC08 database {database}")

    def _create_tables(self) -> None:
        statements = (
            (
                f"""CREATE TABLE {self.business_db}.{self.orders_table} (
                    order_id BIGINT PRIMARY KEY,
                    tenant_id INT NOT NULL,
                    status VARCHAR(24) NOT NULL,
                    amount_cents BIGINT NOT NULL,
                    region VARCHAR(16) NOT NULL,
                    version BIGINT NOT NULL,
                    payload VARCHAR(128) NOT NULL,
                    updated_at DATETIME(6) NOT NULL,
                    KEY idx_tenant_updated (tenant_id, updated_at),
                    KEY idx_status (status)
                )""",
                "create BC08 business orders",
            ),
            (
                f"""CREATE TABLE {self.business_db}.{self.events_table} (
                    event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    order_id BIGINT NOT NULL,
                    tenant_id INT NOT NULL,
                    status VARCHAR(24) NOT NULL,
                    amount_cents BIGINT NOT NULL,
                    event_source VARCHAR(24) NOT NULL,
                    event_ts DATETIME(6) NOT NULL,
                    KEY idx_order_event (order_id, event_id)
                )""",
                "create BC08 order events",
            ),
            (
                f"""CREATE TABLE {self.control_db}.{self.intents_table} (
                    intent_seq BIGINT AUTO_INCREMENT PRIMARY KEY,
                    customer_id BIGINT NOT NULL,
                    amount_cents BIGINT NOT NULL,
                    request_source VARCHAR(64) NOT NULL,
                    status ENUM('pending', 'processed') NOT NULL DEFAULT 'pending',
                    processed_order_id BIGINT,
                    requested_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    processed_at DATETIME(6),
                    KEY idx_intent_status (status, requested_at)
                )""",
                "create BC08 order intents",
            ),
            (
                f"""CREATE TABLE {self.control_db}.{self.state_table} (
                    migration_id VARCHAR(96) PRIMARY KEY,
                    business_scope VARCHAR(64) NOT NULL,
                    request_status ENUM('pending', 'approved', 'rejected') NOT NULL,
                    phase ENUM('preflight', 'cutover', 'completed') NOT NULL,
                    source_arch ENUM('x86', 'arm64') NOT NULL,
                    target_arch ENUM('x86', 'arm64') NOT NULL,
                    active_arch ENUM('x86', 'arm64') NOT NULL,
                    internet_access ENUM('blocked', 'allowed') NOT NULL,
                    bundle_verified TINYINT NOT NULL,
                    tiup_metadata_backup TINYINT NOT NULL,
                    monitoring_ready TINYINT NOT NULL,
                    monitoring_history_copied TINYINT NOT NULL,
                    business_checksum_verified TINYINT NOT NULL,
                    rollback_ready TINYINT NOT NULL,
                    cutover_epoch BIGINT NOT NULL,
                    p95_latency_ms DECIMAL(12,3) NOT NULL,
                    processed_intents BIGINT NOT NULL,
                    updated_at DATETIME(6) NOT NULL
                )""",
                "create BC08 migration state",
            ),
            (
                f"""CREATE TABLE {self.control_db}.{self.artifacts_table} (
                    component VARCHAR(32) NOT NULL,
                    arch ENUM('x86', 'arm64') NOT NULL,
                    version VARCHAR(32) NOT NULL,
                    package_name VARCHAR(128) NOT NULL,
                    available TINYINT NOT NULL,
                    mirror_merged TINYINT NOT NULL,
                    expected_digest VARCHAR(128) NOT NULL,
                    observed_digest VARCHAR(128) NOT NULL,
                    digest_verified TINYINT NOT NULL,
                    compatible TINYINT NOT NULL,
                    history_copied TINYINT NOT NULL,
                    PRIMARY KEY (component, arch)
                )""",
                "create BC08 offline artifacts",
            ),
            (
                f"""CREATE TABLE {self.control_db}.{self.nodes_table} (
                    node_id VARCHAR(64) PRIMARY KEY,
                    migration_id VARCHAR(96) NOT NULL,
                    component VARCHAR(16) NOT NULL,
                    arch ENUM('x86', 'arm64') NOT NULL,
                    state ENUM('active', 'staged', 'retired') NOT NULL,
                    generation INT NOT NULL,
                    leader TINYINT NOT NULL,
                    region_count INT NOT NULL,
                    leader_count INT NOT NULL,
                    KEY idx_component_state (component, arch, state)
                )""",
                "create BC08 migration nodes",
            ),
            (
                f"""CREATE TABLE {self.control_db}.{self.actions_table} (
                    action_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    migration_id VARCHAR(96) NOT NULL,
                    action_name VARCHAR(64) NOT NULL,
                    component VARCHAR(64),
                    status ENUM('pending', 'processing', 'succeeded', 'rejected') NOT NULL DEFAULT 'pending',
                    error_message VARCHAR(512),
                    requested_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    completed_at DATETIME(6),
                    KEY idx_action_scope_status (migration_id, status, action_id)
                )""",
                "create BC08 migration action queue",
            ),
            (
                f"""CREATE TABLE {self.control_db}.{self.runbook_table} (
                    migration_id VARCHAR(96) NOT NULL,
                    step_no INT NOT NULL,
                    action_name VARCHAR(64) NOT NULL,
                    component VARCHAR(64),
                    prerequisite VARCHAR(256) NOT NULL,
                    status ENUM('pending', 'succeeded') NOT NULL,
                    PRIMARY KEY (migration_id, step_no)
                )""",
                "create BC08 migration runbook",
            ),
            (
                f"""CREATE TABLE {self.control_db}.{self.monitor_table} (
                    sample_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    metric_name VARCHAR(48) NOT NULL,
                    sample_value DECIMAL(18,3) NOT NULL,
                    arch ENUM('x86', 'arm64') NOT NULL,
                    retained TINYINT NOT NULL,
                    recorded_at DATETIME(6) NOT NULL,
                    KEY idx_metric_time (metric_name, recorded_at)
                )""",
                "create BC08 monitor history",
            ),
            (
                f"""CREATE TABLE {self.control_db}.{self.backups_table} (
                    backup_kind VARCHAR(48) PRIMARY KEY,
                    digest VARCHAR(128) NOT NULL,
                    valid TINYINT NOT NULL,
                    created_at DATETIME(6) NOT NULL,
                    note VARCHAR(256) NOT NULL
                )""",
                "create BC08 migration backups",
            ),
            (
                f"""CREATE TABLE {self.control_db}.{self.audit_table} (
                    audit_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    event_name VARCHAR(64) NOT NULL,
                    component VARCHAR(64),
                    details VARCHAR(256) NOT NULL,
                    observed_at DATETIME(6) NOT NULL,
                    KEY idx_audit_event (event_name, observed_at)
                )""",
                "create BC08 migration audit",
            ),
        )
        for sql, context in statements:
            self._sql(sql, context)

    def _seed_business_data(self) -> None:
        connection = self._connect(self.business_db, autocommit=False)
        try:
            with connection.cursor() as cursor:
                rows = []
                events = []
                event_types = ("PAID", "SETTLED", "REVIEW", "REFUND")
                regions = ("north", "south", "east", "west")
                for order_id in range(1, self.seed_rows + 1):
                    tenant_id = order_id % 128 + 1
                    amount_cents = (order_id % 401 + 99) * 100
                    status = event_types[order_id % len(event_types)]
                    updated_at = datetime(2026, 7, 1) + timedelta(minutes=order_id % 1440)
                    rows.append((
                        order_id, tenant_id, status, amount_cents, regions[order_id % 4],
                        order_id, f"{self.business_scope.removesuffix('-api')}-seed-{order_id}", updated_at,
                    ))
                    events.append((order_id, tenant_id, status, amount_cents, "seed", updated_at))
                cursor.executemany(
                    f"INSERT INTO {self.orders_table} "
                    "(order_id, tenant_id, status, amount_cents, region, version, payload, updated_at) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    rows,
                )
                cursor.executemany(
                    f"INSERT INTO {self.events_table} "
                    "(order_id, tenant_id, status, amount_cents, event_source, event_ts) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    events,
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _seed_control_plane(self) -> None:
        connection = self._connect(self.control_db, autocommit=False)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"INSERT INTO {self.state_table} "
                    "(migration_id, business_scope, request_status, phase, source_arch, target_arch, active_arch, internet_access, "
                    "bundle_verified, tiup_metadata_backup, monitoring_ready, monitoring_history_copied, "
                    "business_checksum_verified, rollback_ready, cutover_epoch, p95_latency_ms, "
                    "processed_intents, updated_at) VALUES (%s,%s,%s,'preflight',%s,%s,%s,'blocked',0,0,0,0,0,0,1,0,0,NOW(6))",
                    (
                        self.migration_id,
                        self.business_scope,
                        "approved",
                        self.source_arch,
                        self.target_arch,
                        self.source_arch,
                    ),
                )
                cursor.execute(
                    f"INSERT INTO {self.state_table} "
                    "(migration_id, business_scope, request_status, phase, source_arch, target_arch, active_arch, internet_access, "
                    "bundle_verified, tiup_metadata_backup, monitoring_ready, monitoring_history_copied, "
                    "business_checksum_verified, rollback_ready, cutover_epoch, p95_latency_ms, "
                    "processed_intents, updated_at) VALUES (%s,%s,%s,'preflight',%s,%s,%s,'blocked',0,0,0,0,0,0,1,0,0,NOW(6))",
                    (
                        self.rehearsal_migration_id,
                        self.rehearsal_scope,
                        "approved",
                        self.source_arch,
                        self.target_arch,
                        self.source_arch,
                    ),
                )
                artifacts = []
                for component in self.component_names:
                    for arch in (self.source_arch, self.target_arch):
                        digest = f"{self.migration_id}-{component}-{arch}-v8.1.0-sha256"
                        artifacts.append((
                            component, arch, "v8.1.0", f"{component}-v8.1.0-linux-{arch}.tar.gz",
                            1, 0, digest, digest, 0, 0, 0,
                        ))
                cursor.executemany(
                    f"INSERT INTO {self.artifacts_table} "
                    "(component, arch, version, package_name, available, mirror_merged, expected_digest, "
                    "observed_digest, digest_verified, compatible, history_copied) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    artifacts,
                )
                nodes = []
                for component, count in self.node_counts.items():
                    for index in range(count):
                        nodes.append((
                            f"{component}-{self.source_arch}-{index}", self.migration_id, component, self.source_arch,
                            "active", 1, int(component == "pd" and index == 0),
                            8 if component == "tikv" else 0, 4 if component == "tikv" and index == 0 else 0,
                        ))
                        nodes.append((
                            f"{component}-{self.target_arch}-{index}", self.migration_id, component, self.target_arch,
                            "staged", 1, 0, 0, 0,
                        ))
                    nodes.append((
                        f"{component}-{self.source_arch}-rehearsal-0", self.rehearsal_migration_id,
                        component, self.source_arch, "active", 1, 0,
                        8 if component == "tikv" else 0, 4 if component == "tikv" else 0,
                    ))
                    nodes.append((
                        f"{component}-{self.target_arch}-rehearsal-0", self.rehearsal_migration_id,
                        component, self.target_arch, "staged", 1, 0, 0, 0,
                    ))
                cursor.executemany(
                    f"INSERT INTO {self.nodes_table} "
                    "(node_id, migration_id, component, arch, state, generation, leader, region_count, leader_count) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    nodes,
                )
                runbook = self._runbook_rows(self.migration_id)
                runbook.extend(self._runbook_rows(self.rehearsal_migration_id, "rehearsal"))
                cursor.executemany(
                    f"INSERT INTO {self.runbook_table} "
                    "(migration_id, step_no, action_name, component, prerequisite, status) "
                    "VALUES (%s,%s,%s,%s,%s,'pending')",
                    runbook,
                )
                history = []
                metric_names = ("query_p95_ms", "business_qps", "region_balance", "pd_tso_latency")
                for index in range(self.monitor_history_rows):
                    history.append((
                        metric_names[index % len(metric_names)],
                        32 + (index % 17),
                        self.source_arch,
                        1,
                        datetime.utcnow() - timedelta(minutes=self.monitor_history_rows - index),
                    ))
                cursor.executemany(
                    f"INSERT INTO {self.monitor_table} "
                    "(metric_name, sample_value, arch, retained, recorded_at) VALUES (%s,%s,%s,%s,%s)",
                    history,
                )
                cursor.executemany(
                    f"INSERT INTO {self.backups_table} "
                    "(backup_kind, digest, valid, created_at, note) VALUES (%s,%s,%s,NOW(6),%s)",
                    (
                        ("legacy_manifest", f"legacy-{self.migration_id}-digest", 1, "old x86-only manifest decoy"),
                        ("old_checkpoint", f"expired-{self.migration_id}-checkpoint", 0, "stale migration attempt"),
                    ),
                )
                cursor.executemany(
                    f"INSERT INTO {self.audit_table} "
                    "(event_name, component, details, observed_at) VALUES (%s,%s,%s,NOW(6))",
                    (
                        ("legacy_plan", "tikv", "old plan was abandoned before the change window",),
                        ("failed_preflight", "prometheus", "historical x86-only manifest was rejected",),
                    ),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _runbook_rows(
        self,
        migration_id: str,
        node_suffix: str | None = None,
    ) -> list[tuple[str, int, str, str | None, str]]:
        rows: list[tuple[str, int, str, str | None, str]] = []
        step = 1

        def add(action: str, component: str | None, prerequisite: str) -> None:
            nonlocal step
            rows.append((migration_id, step, action, component, prerequisite))
            step += 1

        def node(component: str, arch: str, index: int) -> str:
            suffix = f"-{node_suffix}" if node_suffix is not None else ""
            return f"{component}-{arch}{suffix}-{index}"

        add("merge_offline_mirror", None, "internet_access=blocked and all arm64 packages available")
        add("verify_arm64_bundle", None, "offline mirror merged and every digest/compatibility check passes")
        add("backup_tiup_metadata", None, "arm64 bundle verified")
        add("copy_monitor_history", None, "TiUP metadata and business backup are valid")
        for index in range(self.node_counts["pd"]):
            add("add_arm64_pd", node("pd", self.target_arch, index), "monitor history copied")
        add("transfer_pd_leader", node("pd", self.target_arch, 0), "all arm64 PD members are active")
        for index in range(self.node_counts["pd"]):
            add("retire_x86_pd", node("pd", self.source_arch, index), "arm64 PD leader is confirmed")
        for index in range(self.node_counts["tikv"]):
            add("add_arm64_tikv", node("tikv", self.target_arch, index), "all x86 PD members are retired")
        for index in range(self.node_counts["tikv"]):
            add("rebalance_tikv", node("tikv", self.target_arch, index), "arm64 TiKV is active")
        for index in range(self.node_counts["tikv"]):
            add("retire_x86_tikv", node("tikv", self.source_arch, index), "arm64 TiKV Region counts are positive")
        for index in range(self.node_counts["tidb"]):
            add("add_arm64_tidb", node("tidb", self.target_arch, index), "x86 TiKV stores are retired")
        add("verify_business_checksum", None, "arm64 TiDB nodes are active")
        add("prepare_rollback", None, "business checksum and backup are verified")
        add("cutover_to_arm64", None, "rollback point is ready and p95 is within SLO")
        for index in range(self.node_counts["tidb"]):
            add("retire_x86_tidb", node("tidb", self.source_arch, index), "traffic is on arm64")
        return rows

    def _verify_initial_state(self) -> None:
        rows = self._rows(
            f"SELECT COUNT(*), SUM(order_id), SUM(amount_cents), SUM(tenant_id) "
            f"FROM {self.business_db}.{self.orders_table} WHERE order_id <= {self.seed_rows}",
            "verify BC08 seed business truth",
        )
        if len(rows) != 1 or len(rows[0]) != 4:
            raise ValueError(f"BC08 seed checksum query shape is invalid: rows={rows!r}")
        expected = [[
            self.seed_rows,
            self.seed_rows * (self.seed_rows + 1) // 2,
            self.expected_seed_amount_cents,
            self.expected_seed_tenant_sum,
        ]]
        observed = [[int(value) for value in rows[0]]]
        if observed != expected:
            raise RuntimeError(f"BC08 seed checksum mismatch: expected={expected!r}, observed={observed!r}")
        state = self._rows(
            f"SELECT phase, active_arch, internet_access FROM {self.control_db}.{self.state_table} "
            f"WHERE migration_id = '{self.migration_id}'",
            "verify BC08 initial migration state",
        )
        if state != [["preflight", self.source_arch, "blocked"]]:
            raise RuntimeError(f"BC08 initial migration state mismatch: rows={state!r}")

    def _verify_persistent_state(self) -> None:
        state = self._rows(
            f"SELECT business_scope, phase, active_arch, target_arch, internet_access, bundle_verified "
            f"FROM {self.control_db}.{self.state_table} WHERE migration_id = '{self.migration_id}'",
            "verify BC08 persistent migration state",
        )
        if len(state) != 1 or state[0][0] != self.business_scope or state[0][3] != self.target_arch or state[0][4] != "blocked":
            raise RuntimeError(
                f"BC08 persistent migration state is invalid: migration_id={self.migration_id!r}, rows={state!r}"
            )
        artifact_count = self._rows(
            f"SELECT COUNT(*) FROM {self.control_db}.{self.artifacts_table} "
            f"WHERE arch = '{self.target_arch}'",
            "verify BC08 persistent arm64 artifacts",
        )
        if artifact_count != [[len(self.component_names)]]:
            raise RuntimeError(
                f"BC08 persistent arm64 artifact count mismatch: expected={len(self.component_names)}, rows={artifact_count!r}"
            )

    def _start_controller(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            raise RuntimeError(f"BC08 migration controller is already running: migration_id={self.migration_id!r}")
        self._stop_event = threading.Event()
        self._worker_error = None
        self._thread = threading.Thread(
            target=self._controller_main,
            name=f"aiopsbench-{self.migration_id}-architecture-controller",
            daemon=True,
        )
        self._thread.start()

    def _stop_controller(self, *, raise_worker_error: bool) -> BaseException | None:
        if self._thread is None:
            return None
        self._stop_event.set()
        self._thread.join(timeout=15)
        if self._thread.is_alive():
            raise RuntimeError(f"BC08 migration controller did not stop: migration_id={self.migration_id!r}")
        error = self._worker_error
        self._thread = None
        self._stop_event = None
        self._worker_error = None
        if raise_worker_error and error is not None:
            raise RuntimeError(f"BC08 migration controller failed: error={error!r}") from error
        return error

    def _controller_main(self) -> None:
        try:
            while not self._stop_event.is_set():
                try:
                    self._process_actions()
                    self._process_intents()
                    self._refresh_state()
                except (pymysql.err.InterfaceError, pymysql.err.OperationalError) as exc:
                    if not _is_transient_database_error(exc):
                        raise
                    print(
                        "[BC08 controller] transient database connection failure; retrying: "
                        f"migration_id={self.migration_id!r}, error={exc!r}"
                    )
                self._stop_event.wait(self.action_poll_interval_seconds)
        except BaseException as exc:
            self._worker_error = exc
            self._stop_event.set()

    def _process_actions(self) -> None:
        connection = self._connect(None, autocommit=False)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT action_id, migration_id, action_name, component FROM {self.control_db}.{self.actions_table} "
                    "WHERE migration_id=%s AND status = 'pending' ORDER BY action_id LIMIT 1",
                    (self.migration_id,),
                )
                action = cursor.fetchone()
                if action is not None:
                    action_id, migration_id, action_name, component = action
                    try:
                        self._apply_action(cursor, str(action_name), component)
                    except ActionBlocked as exc:
                        cursor.execute(
                            f"UPDATE {self.control_db}.{self.actions_table} "
                            "SET error_message=%s WHERE action_id=%s",
                            (str(exc), action_id),
                        )
                    except ActionRejected as exc:
                        cursor.execute(
                            f"UPDATE {self.control_db}.{self.actions_table} SET status='rejected', "
                            "error_message=%s, completed_at=NOW(6) WHERE action_id=%s",
                            (str(exc), action_id),
                        )
                    else:
                        cursor.execute(
                            f"UPDATE {self.control_db}.{self.actions_table} SET status='succeeded', "
                            "error_message=NULL, completed_at=NOW(6) WHERE action_id=%s",
                            (action_id,),
                        )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _apply_action(self, cursor, action_name: str, component: str | None) -> None:
        handlers = {
            "merge_offline_mirror": self._action_merge_offline_mirror,
            "verify_arm64_bundle": self._action_verify_arm64_bundle,
            "backup_tiup_metadata": self._action_backup_tiup_metadata,
            "copy_monitor_history": self._action_copy_monitor_history,
            "add_arm64_pd": self._action_add_arm64_pd,
            "transfer_pd_leader": self._action_transfer_pd_leader,
            "retire_x86_pd": self._action_retire_x86_pd,
            "add_arm64_tikv": self._action_add_arm64_tikv,
            "rebalance_tikv": self._action_rebalance_tikv,
            "retire_x86_tikv": self._action_retire_x86_tikv,
            "add_arm64_tidb": self._action_add_arm64_tidb,
            "verify_business_checksum": self._action_verify_business_checksum,
            "prepare_rollback": self._action_prepare_rollback,
            "cutover_to_arm64": self._action_cutover_to_arm64,
            "retire_x86_tidb": self._action_retire_x86_tidb,
        }
        try:
            handler = handlers[action_name]
        except KeyError as exc:
            raise ActionRejected(f"unknown BC08 migration action: action={action_name!r}") from exc
        handler(cursor, component)

    def _state(self, cursor) -> dict[str, object]:
        cursor.execute(
            f"SELECT phase, active_arch, bundle_verified, tiup_metadata_backup, monitoring_ready, "
            f"monitoring_history_copied, business_checksum_verified, rollback_ready, cutover_epoch, "
            f"p95_latency_ms FROM {self.control_db}.{self.state_table} WHERE migration_id=%s",
            (self.migration_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError(f"BC08 migration state disappeared: migration_id={self.migration_id!r}")
        names = (
            "phase", "active_arch", "bundle_verified", "tiup_metadata_backup", "monitoring_ready",
            "monitoring_history_copied", "business_checksum_verified", "rollback_ready",
            "cutover_epoch", "p95_latency_ms",
        )
        return dict(zip(names, row))

    def _require(self, condition: bool, message: str) -> None:
        if not condition:
            raise ActionRejected(message)

    def _require_component(
        self,
        cursor,
        component: str | None,
        expected_component: str,
        expected_arch: str,
        expected_state: str,
    ) -> None:
        self._require(component is not None, f"BC08 action requires component={expected_component}-{expected_arch}-N")
        prefix = f"{expected_component}-{expected_arch}-"
        self._require(
            str(component).startswith(prefix),
            f"BC08 action component must start with {prefix!r}: component={component!r}",
        )
        cursor.execute(
            f"SELECT migration_id, component, arch, state FROM {self.control_db}.{self.nodes_table} WHERE node_id=%s",
            (component,),
        )
        row = cursor.fetchone()
        self._require(row is not None, f"migration node does not exist: node_id={component!r}")
        self._require(
            row == (self.migration_id, expected_component, expected_arch, expected_state),
            "BC08 action component state mismatch: "
            f"node_id={component!r}, expected={(self.migration_id, expected_component, expected_arch, expected_state)!r}, observed={row!r}",
        )

    def _action_merge_offline_mirror(self, cursor, component: str | None) -> None:
        state = self._state(cursor)
        self._require(state["active_arch"] == self.source_arch, "offline mirror merge must start before cutover")
        self._require(state["phase"] == "preflight", f"offline mirror merge requires phase=preflight: phase={state['phase']!r}")
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.control_db}.{self.artifacts_table} "
            "WHERE arch=%s AND available=1",
            (self.target_arch,),
        )
        self._require(cursor.fetchone()[0] == len(self.component_names), "arm64 offline package inventory is incomplete")
        cursor.execute(
            f"UPDATE {self.control_db}.{self.artifacts_table} SET mirror_merged=1 WHERE arch=%s",
            (self.target_arch,),
        )
        self._audit(cursor, "offline_mirror_merged", None, "arm64 packages merged without internet")

    def _action_verify_arm64_bundle(self, cursor, component: str | None) -> None:
        state = self._state(cursor)
        self._require(state["phase"] == "preflight", f"bundle verification requires phase=preflight: phase={state['phase']!r}")
        cursor.execute(
            f"SELECT COUNT(*), SUM(mirror_merged=1 AND available=1 AND expected_digest=observed_digest) "
            f"FROM {self.control_db}.{self.artifacts_table} WHERE arch=%s",
            (self.target_arch,),
        )
        count, good = cursor.fetchone()
        self._require(
            int(count) == len(self.component_names) and int(good or 0) == len(self.component_names),
            f"arm64 bundle digest or availability check failed: count={count}, good={good}",
        )
        cursor.execute(
            f"UPDATE {self.control_db}.{self.artifacts_table} SET digest_verified=1, compatible=1 WHERE arch=%s",
            (self.target_arch,),
        )
        cursor.execute(
            f"UPDATE {self.control_db}.{self.state_table} SET bundle_verified=1, updated_at=NOW(6) "
            "WHERE migration_id=%s",
            (self.migration_id,),
        )
        self._audit(cursor, "arm64_bundle_verified", None, "digest and compatibility inventory verified")

    def _action_backup_tiup_metadata(self, cursor, component: str | None) -> None:
        state = self._state(cursor)
        self._require(int(state["bundle_verified"]) == 1, "TiUP metadata backup requires a verified arm64 bundle")
        cursor.execute(
            f"SELECT COUNT(*), SUM(order_id), SUM(amount_cents), SUM(tenant_id) "
            f"FROM {self.business_db}.{self.orders_table} WHERE order_id <= %s",
            (self.seed_rows,),
        )
        count, order_sum, amount_sum, tenant_sum = cursor.fetchone()
        digest = f"{self.orders_table}:{count}:{order_sum}:{amount_sum}:{tenant_sum}"
        cursor.executemany(
            f"INSERT INTO {self.control_db}.{self.backups_table} "
            "(backup_kind, digest, valid, created_at, note) VALUES (%s,%s,1,NOW(6),%s) "
            "ON DUPLICATE KEY UPDATE digest=VALUES(digest), valid=1, created_at=NOW(6), note=VALUES(note)",
            (
                ("tiup_metadata", f"tiup-clusters-{self.migration_id}", "x86/arm64 cluster metadata backup"),
                ("business_backup", digest, "seed business checksum backup"),
            ),
        )
        cursor.execute(
            f"UPDATE {self.control_db}.{self.state_table} SET tiup_metadata_backup=1, updated_at=NOW(6) "
            "WHERE migration_id=%s",
            (self.migration_id,),
        )
        self._audit(cursor, "tiup_metadata_backed_up", "tiup", "cluster metadata and business backup recorded")

    def _action_copy_monitor_history(self, cursor, component: str | None) -> None:
        state = self._state(cursor)
        self._require(int(state["tiup_metadata_backup"]) == 1, "monitor history copy requires TiUP metadata backup")
        cursor.execute(
            f"UPDATE {self.control_db}.{self.artifacts_table} SET history_copied=1 "
            "WHERE arch=%s AND component IN ('prometheus','grafana','alertmanager')",
            (self.target_arch,),
        )
        cursor.execute(
            f"UPDATE {self.control_db}.{self.state_table} SET monitoring_ready=1, "
            "monitoring_history_copied=1, updated_at=NOW(6) WHERE migration_id=%s",
            (self.migration_id,),
        )
        self._audit(cursor, "monitor_history_copied", "prometheus", "retention window copied to arm64 monitoring lane")

    def _action_add_arm64_pd(self, cursor, component: str | None) -> None:
        state = self._state(cursor)
        self._require(int(state["monitoring_ready"]) == 1, "arm64 PD scale-out requires monitoring to be ready")
        self._require_component(cursor, component, "pd", self.target_arch, "staged")
        self._activate_node(cursor, component, "pd")

    def _action_transfer_pd_leader(self, cursor, component: str | None) -> None:
        self._require_component(cursor, component, "pd", self.target_arch, "active")
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.control_db}.{self.nodes_table} "
            "WHERE migration_id=%s AND component='pd' AND arch=%s AND state='active'",
            (self.migration_id, self.target_arch),
        )
        self._require(cursor.fetchone()[0] == self.node_counts["pd"], "all arm64 PD members must be active before leader transfer")
        cursor.execute(
            f"UPDATE {self.control_db}.{self.nodes_table} SET leader=0 "
            "WHERE migration_id=%s AND component='pd'",
            (self.migration_id,),
        )
        cursor.execute(
            f"UPDATE {self.control_db}.{self.nodes_table} SET leader=1 "
            "WHERE migration_id=%s AND node_id=%s AND state='active'",
            (self.migration_id, component),
        )
        self._audit(cursor, "pd_leader_transferred", component, "arm64 PD leader confirmed")

    def _action_retire_x86_pd(self, cursor, component: str | None) -> None:
        self._require_component(cursor, component, "pd", self.source_arch, "active")
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.control_db}.{self.nodes_table} "
            "WHERE migration_id=%s AND component='pd' AND arch=%s AND state='active' AND leader=1",
            (self.migration_id, self.target_arch),
        )
        self._require(cursor.fetchone()[0] == 1, "x86 PD retirement requires exactly one arm64 PD leader")
        self._retire_node(cursor, component, "pd")

    def _action_add_arm64_tikv(self, cursor, component: str | None) -> None:
        self._require_component(cursor, component, "tikv", self.target_arch, "staged")
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.control_db}.{self.nodes_table} "
            "WHERE migration_id=%s AND component='pd' AND arch=%s AND state='retired'",
            (self.migration_id, self.source_arch),
        )
        self._require(cursor.fetchone()[0] == self.node_counts["pd"], "arm64 TiKV scale-out requires all x86 PD members retired")
        self._activate_node(cursor, component, "tikv")

    def _action_rebalance_tikv(self, cursor, component: str | None) -> None:
        self._require_component(cursor, component, "tikv", self.target_arch, "active")
        cursor.execute(
            f"UPDATE {self.control_db}.{self.nodes_table} SET region_count=8, leader_count=4 "
            "WHERE migration_id=%s AND node_id=%s AND state='active'",
            (self.migration_id, component),
        )
        self._audit(cursor, "tikv_region_rebalanced", component, "target store has Region and leader placement")

    def _action_retire_x86_tikv(self, cursor, component: str | None) -> None:
        self._require_component(cursor, component, "tikv", self.source_arch, "active")
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.control_db}.{self.nodes_table} "
            "WHERE migration_id=%s AND component='tikv' AND arch=%s AND state='active' AND region_count > 0",
            (self.migration_id, self.target_arch),
        )
        self._require(cursor.fetchone()[0] == self.node_counts["tikv"], "all arm64 TiKV stores must be balanced before x86 retirement")
        self._retire_node(cursor, component, "tikv")

    def _action_add_arm64_tidb(self, cursor, component: str | None) -> None:
        self._require_component(cursor, component, "tidb", self.target_arch, "staged")
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.control_db}.{self.nodes_table} "
            "WHERE migration_id=%s AND component='tikv' AND arch=%s AND state='retired'",
            (self.migration_id, self.source_arch),
        )
        self._require(cursor.fetchone()[0] == self.node_counts["tikv"], "arm64 TiDB nodes require retired x86 TiKV stores")
        self._activate_node(cursor, component, "tidb")

    def _action_verify_business_checksum(self, cursor, component: str | None) -> None:
        cursor.execute(
            f"SELECT COUNT(*), SUM(order_id), SUM(amount_cents), SUM(tenant_id) "
            f"FROM {self.business_db}.{self.orders_table} WHERE order_id <= %s",
            (self.seed_rows,),
        )
        observed = cursor.fetchone()
        expected = (
            self.seed_rows,
            self.seed_rows * (self.seed_rows + 1) // 2,
            self.expected_seed_amount_cents,
            self.expected_seed_tenant_sum,
        )
        self._require(tuple(int(value) for value in observed) == expected, f"business checksum mismatch: expected={expected}, observed={observed}")
        cursor.execute(
            f"SELECT COUNT(*), SUM(status='processed'), SUM(status='pending') "
            f"FROM {self.control_db}.{self.intents_table}"
        )
        total, processed, pending = cursor.fetchone()
        if int(total) < self.minimum_processed_intents or int(processed or 0) != int(total) or int(pending or 0) != 0:
            raise ActionBlocked(
                "online order intents are not drained yet: "
                f"total={total}, processed={processed}, pending={pending}, "
                f"minimum={self.minimum_processed_intents}"
            )
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.control_db}.{self.nodes_table} "
            "WHERE migration_id=%s AND component='tidb' AND arch=%s AND state='active'",
            (self.migration_id, self.target_arch),
        )
        self._require(cursor.fetchone()[0] == self.node_counts["tidb"], "all arm64 TiDB nodes must be active before checksum verification")
        cursor.execute(
            f"UPDATE {self.control_db}.{self.state_table} SET business_checksum_verified=1, updated_at=NOW(6) "
            "WHERE migration_id=%s",
            (self.migration_id,),
        )
        self._audit(cursor, "business_checksum_verified", None, "seed rows and online intent queue are consistent")

    def _action_prepare_rollback(self, cursor, component: str | None) -> None:
        state = self._state(cursor)
        self._require(int(state["business_checksum_verified"]) == 1, "rollback point requires business checksum verification")
        self._require(int(state["monitoring_history_copied"]) == 1, "rollback point requires monitoring history copy")
        self._require(int(state["tiup_metadata_backup"]) == 1, "rollback point requires TiUP metadata backup")
        cursor.execute(
            f"INSERT INTO {self.control_db}.{self.backups_table} "
            "(backup_kind, digest, valid, created_at, note) VALUES "
            "('rollback_point','arm64-ready-before-cutover',1,NOW(6),'source metadata retained for rollback') "
            "ON DUPLICATE KEY UPDATE valid=1, created_at=NOW(6)",
        )
        cursor.execute(
            f"UPDATE {self.control_db}.{self.state_table} SET rollback_ready=1, updated_at=NOW(6) "
            "WHERE migration_id=%s",
            (self.migration_id,),
        )
        self._audit(cursor, "rollback_point_prepared", None, "x86 metadata and business backup retained")

    def _action_cutover_to_arm64(self, cursor, component: str | None) -> None:
        state = self._state(cursor)
        self._require(int(state["rollback_ready"]) == 1, "cutover requires rollback point")
        p95 = float(state["p95_latency_ms"])
        if p95 > self.latency_slo_ms:
            raise ActionBlocked(
                f"cutover online intent p95 is above SLO: p95={p95}, slo={self.latency_slo_ms}"
            )
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.control_db}.{self.nodes_table} "
            "WHERE migration_id=%s AND component='tidb' AND arch=%s AND state='active'",
            (self.migration_id, self.target_arch),
        )
        self._require(cursor.fetchone()[0] == self.node_counts["tidb"], "cutover requires all arm64 TiDB nodes active")
        cursor.execute(
            f"UPDATE {self.control_db}.{self.state_table} SET active_arch=%s, cutover_epoch=2, phase='cutover', updated_at=NOW(6) "
            "WHERE migration_id=%s",
            (self.target_arch, self.migration_id),
        )
        self._audit(cursor, "cutover_to_arm64", None, "business route switched after rollback and SLO checks")

    def _action_retire_x86_tidb(self, cursor, component: str | None) -> None:
        self._require_component(cursor, component, "tidb", self.source_arch, "active")
        state = self._state(cursor)
        self._require(state["active_arch"] == self.target_arch, "x86 TiDB retirement requires arm64 cutover")
        self._retire_node(cursor, component, "tidb")
        cursor.execute(
            f"SELECT COUNT(*) FROM {self.control_db}.{self.nodes_table} "
            "WHERE migration_id=%s AND arch=%s AND state='active'",
            (self.migration_id, self.source_arch),
        )
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                f"UPDATE {self.control_db}.{self.state_table} SET phase='completed', updated_at=NOW(6) "
                "WHERE migration_id=%s",
                (self.migration_id,),
            )
            self._audit(cursor, "all_x86_retired", None, "all source architecture nodes retired")

    def _activate_node(self, cursor, node_id: str | None, expected_component: str) -> None:
        cursor.execute(
            f"SELECT component, arch, state FROM {self.control_db}.{self.nodes_table} WHERE node_id=%s",
            (node_id,),
        )
        row = cursor.fetchone()
        self._require(row is not None, f"migration node does not exist: node_id={node_id!r}")
        self._require(row[0] == expected_component and row[1] == self.target_arch and row[2] == "staged", f"node is not staged for arm64 activation: node={node_id!r}, row={row!r}")
        cursor.execute(
            f"UPDATE {self.control_db}.{self.nodes_table} SET state='active', generation=2 "
            "WHERE migration_id=%s AND node_id=%s",
            (self.migration_id, node_id),
        )

    def _retire_node(self, cursor, node_id: str | None, expected_component: str) -> None:
        cursor.execute(
            f"SELECT component, arch, state FROM {self.control_db}.{self.nodes_table} WHERE node_id=%s",
            (node_id,),
        )
        row = cursor.fetchone()
        self._require(row is not None, f"migration node does not exist: node_id={node_id!r}")
        self._require(row[0] == expected_component and row[1] == self.source_arch and row[2] == "active", f"source node is not active: node={node_id!r}, row={row!r}")
        cursor.execute(
            f"UPDATE {self.control_db}.{self.nodes_table} SET state='retired', leader=0, region_count=0, leader_count=0 "
            "WHERE migration_id=%s AND node_id=%s",
            (self.migration_id, node_id),
        )
        self._audit(cursor, "source_node_retired", node_id, f"retired {self.source_arch} {expected_component}")

    def _audit(self, cursor, event_name: str, component: str | None, details: str) -> None:
        cursor.execute(
            f"INSERT INTO {self.control_db}.{self.audit_table} (event_name, component, details, observed_at) "
            "VALUES (%s,%s,%s,NOW(6))",
            (event_name, component, details),
        )

    def _process_intents(self) -> None:
        connection = self._connect(None, autocommit=False)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT intent_seq, customer_id, amount_cents, requested_at "
                    f"FROM {self.control_db}.{self.intents_table} WHERE status='pending' "
                    "ORDER BY intent_seq LIMIT 32"
                )
                intents = cursor.fetchall()
                for intent_seq, customer_id, amount_cents, requested_at in intents:
                    order_id = 1_000_000 + int(intent_seq)
                    status = "PAID" if int(intent_seq) % 2 else "SETTLED"
                    region = ("north", "south", "east", "west")[int(intent_seq) % 4]
                    cursor.execute(
                        f"INSERT INTO {self.business_db}.{self.orders_table} "
                        "(order_id, tenant_id, status, amount_cents, region, version, payload, updated_at) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(6))",
                        (order_id, int(customer_id) % 128 + 1, status, int(amount_cents), region, int(intent_seq), f"live-intent-{intent_seq}"),
                    )
                    cursor.execute(
                        f"INSERT INTO {self.business_db}.{self.events_table} "
                        "(order_id, tenant_id, status, amount_cents, event_source, event_ts) "
                        "VALUES (%s,%s,%s,%s,'online-intent',NOW(6))",
                        (order_id, int(customer_id) % 128 + 1, status, int(amount_cents)),
                    )
                    cursor.execute(
                        f"UPDATE {self.control_db}.{self.intents_table} SET status='processed', "
                        "processed_order_id=%s, processed_at=NOW(6) WHERE intent_seq=%s AND status='pending'",
                        (order_id, intent_seq),
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _refresh_state(self) -> None:
        connection = self._connect(None, autocommit=False)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT requested_at, processed_at FROM {self.control_db}.{self.intents_table} "
                    "WHERE status='processed' AND processed_at IS NOT NULL ORDER BY processed_at DESC LIMIT 200"
                )
                latencies = [
                    max(0.0, (processed_at - requested_at).total_seconds() * 1000.0)
                    for requested_at, processed_at in cursor.fetchall()
                ]
                latencies.sort()
                p95 = latencies[min(len(latencies) - 1, max(0, int(len(latencies) * 0.95) - 1))] if latencies else 0.0
                cursor.execute(f"SELECT COUNT(*) FROM {self.control_db}.{self.intents_table} WHERE status='processed'")
                processed = int(cursor.fetchone()[0])
                cursor.execute(
                    f"SELECT active_arch FROM {self.control_db}.{self.state_table} WHERE migration_id=%s",
                    (self.migration_id,),
                )
                active_arch = cursor.fetchone()[0]
                cursor.execute(
                    f"UPDATE {self.control_db}.{self.state_table} SET p95_latency_ms=%s, processed_intents=%s, updated_at=NOW(6) "
                    "WHERE migration_id=%s",
                    (round(p95, 3), processed, self.migration_id),
                )
                samples = (
                    ("query_p95_ms", p95),
                    ("business_qps", processed),
                    ("region_balance", 1 if active_arch == self.target_arch else 0),
                    ("pd_tso_latency", 2.0),
                )
                cursor.executemany(
                    f"INSERT INTO {self.control_db}.{self.monitor_table} "
                    "(metric_name, sample_value, arch, retained, recorded_at) VALUES (%s,%s,%s,1,NOW(6))",
                    tuple((name, value, active_arch) for name, value in samples),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
