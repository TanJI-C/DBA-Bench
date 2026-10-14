from collections.abc import Mapping
from dataclasses import dataclass, replace
import threading
import time

from src.database.query_results import capture_query_result_truth
from src.database.sql import (
    execute_json_payload,
    execute_result_rows,
    require_one_result_row,
    require_success_payload,
)
from src.database.tidb import execute_integrity_tuple
from src.scenarios.evaluation.tidb.query_perf.set_autocommit_storm import (
    TidbQueryPerfSetAutocommitStormEvaluatorCase,
    TidbQueryPerfSetAutocommitStormFocusedEvaluatorCase,
)
from src.protocols.report import structured_reference_report
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.tidb.common import validate_sql_identifier
from src.workloads.specs import SessionSetupBehavior, WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


_DB = "benchops"
_EVENTS_TABLE = "admission_events"
_ORDERS_TABLE = "order_facts"
_INVENTORY_TABLE = "inventory_snapshot"
_ASSIGNMENTS_TABLE = "runtime_assignments"
_CONNECTOR_TABLE = "connector_revisions"
_CHECKOUT_TABLE = "checkout_revisions"
_ROLLOUTS_TABLE = "runtime_rollouts"
_REVISION_CATALOG_TABLE = "runtime_revision_catalog"

_TARGET_COHORT = "cohort-04"
_RESOURCE_GROUPS = {
    "cohort-01": "rg_m03_01",
    "cohort-02": "rg_m03_02",
    "cohort-03": "rg_m03_03",
    "cohort-04": "rg_m03_04",
}
_SESSION_ALIASES = {
    "cohort-01": "orders-svc-01",
    "cohort-02": "orders-svc-02",
    "cohort-03": "orders-svc-03",
    "cohort-04": "orders-svc-04",
}
_ROUTERS = {cohort: f"router_{cohort.replace('-', '_')}" for cohort in _RESOURCE_GROUPS}

_SESSION_SETUP_STATEMENT = "SET autocommit=1"
_TRANSITION_CHECKOUT_INTERVAL = 16
_PER_CHECKOUT_RESET_COUNT = 512
_HISTORICAL_ROLLOUT_COHORT = "cohort-02"
_HISTORICAL_ROLLOUT_SECONDS = 6.0
_CURRENT_INCIDENT_WINDOW_SECONDS = 2.0
_RECONCILE_INTERVAL_SECONDS = 1.0
_SET_AUTOCOMMIT_MONITORING_SETTLE_DEADLINE_SECONDS = 90
_SET_AUTOCOMMIT_MONITORING_SETTLE_INTERVAL_SECONDS = 2.0
_DEPLOYMENT_LANES = ("stable", "canary")
_SESSION_BINDING_MODES = ("steady", "rebind")
_SESSION_LEASE_MODES = ("fixed", "renew_on_checkout")

_BUSINESS_QUERY = (
    f"SELECT event_id, tenant_id, event_type, amount, payload FROM {_DB}.{_EVENTS_TABLE} "
    "WHERE event_id BETWEEN 1 AND 200 ORDER BY event_id"
)
_EVENT_INTEGRITY_SQL = (
    "SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_type, amount, payload))), 0) "
    f"FROM {_DB}.{_EVENTS_TABLE}"
)
_ORDERS_INTEGRITY_SQL = (
    "SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, amount, status))), 0) "
    f"FROM {_DB}.{_ORDERS_TABLE}"
)
_INVENTORY_INTEGRITY_SQL = (
    "SELECT COUNT(*), COALESCE(SUM(item_id), 0), "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', item_id, warehouse_id, available))), 0) "
    f"FROM {_DB}.{_INVENTORY_TABLE}"
)

_COHORTS = (
    ("cohort-01", "r1", "h1", 0),
    ("cohort-02", "r2", "h1", 1),
    ("cohort-03", "r1", "h2", 0),
    ("cohort-04", "r2", "h2", 1),
)
_COHORT_STATES = {
    "cohort-01": ("stable", "steady"),
    "cohort-02": ("canary", "steady"),
    "cohort-03": ("stable", "rebind"),
    "cohort-04": ("canary", "rebind"),
}
_COHORT_LEASE_MODES = {
    "cohort-01": "fixed",
    "cohort-02": "fixed",
    "cohort-03": "renew_on_checkout",
    "cohort-04": "renew_on_checkout",
}


def _connection_setup_statements(cohort_id: str) -> tuple[str, ...]:
    resource_group = _RESOURCE_GROUPS[cohort_id]
    session_alias = _SESSION_ALIASES[cohort_id]
    return (
        f"SET RESOURCE GROUP {resource_group}",
        f"SET SESSION tidb_session_alias = '{session_alias}'",
    )


def _session_setup_statement_count(
    configuration: tuple[object, ...],
    checkout_number: int,
) -> int:
    if len(configuration) != 7:
        raise ValueError(
            "set-autocommit session setup configuration must contain connector, checkout, lane, binding and lease values: "
            f"configuration={configuration!r}"
        )
    (
        _use_local_session_state,
        _elide_set_autocommits,
        reset_mode,
        reset_count,
        deployment_lane,
        binding_mode,
        lease_mode,
    ) = configuration
    if str(deployment_lane).casefold() not in _DEPLOYMENT_LANES:
        raise ValueError(
            "set-autocommit deployment lane is unsupported: "
            f"deployment_lane={deployment_lane!r}, configuration={configuration!r}"
        )
    if str(binding_mode).casefold() not in _SESSION_BINDING_MODES:
        raise ValueError(
            "set-autocommit session binding mode is unsupported: "
            f"session_binding_mode={binding_mode!r}, configuration={configuration!r}"
        )
    if str(lease_mode).casefold() not in _SESSION_LEASE_MODES:
        raise ValueError(
            "set-autocommit session lease mode is unsupported: "
            f"session_lease_mode={lease_mode!r}, configuration={configuration!r}"
        )
    if (
        str(deployment_lane).casefold() == "canary"
        and str(lease_mode).casefold() == "renew_on_checkout"
    ):
        return _PER_CHECKOUT_RESET_COUNT
    if str(reset_mode).casefold() == "transition":
        return int((checkout_number - 1) % _TRANSITION_CHECKOUT_INTERVAL == 0)
    if str(reset_mode).casefold() == "per_checkout":
        return 0
    raise ValueError(
        "set-autocommit checkout revision has unsupported reset mode: "
        f"reset_mode={reset_mode!r}, configuration={configuration!r}"
    )


def _session_setup_behavior(cohort_id: str) -> SessionSetupBehavior:
    return SessionSetupBehavior(
        config_query=(
            "SELECT c.use_local_session_state, c.elide_set_autocommits, "
            "h.reset_mode, h.reset_count, a.deployment_lane, a.session_binding_mode, "
            "a.session_lease_mode "
            f"FROM {_DB}.{_ASSIGNMENTS_TABLE} AS a "
            f"JOIN {_DB}.{_CONNECTOR_TABLE} AS c ON c.revision_id = a.connector_revision "
            f"JOIN {_DB}.{_CHECKOUT_TABLE} AS h ON h.revision_id = a.checkout_revision "
            f"WHERE a.cohort_id = '{cohort_id}'"
        ),
        statement=_SESSION_SETUP_STATEMENT,
        statement_count=_session_setup_statement_count,
    )


def _cohort_profiles(cohort_id: str) -> tuple[WorkloadProfile, ...]:
    router = _ROUTERS[cohort_id]
    setup = _connection_setup_statements(cohort_id)
    common = {
        "qps": 4.5,
        "tier": "ORDER_MAINTENANCE",
        "application_name": "orders-maintenance",
        "connection_pool": router,
        "connection_setup_statements": setup,
        "session_setup": _session_setup_behavior(cohort_id),
        "transactional": False,
    }
    return (
        WorkloadProfile(
            name=f"order_path_{cohort_id}_lookup",
            sql=(
                f"SELECT amount, event_type FROM {_DB}.{_EVENTS_TABLE} "
                "WHERE event_id = 1"
            ),
            **common,
        ),
        WorkloadProfile(
            name=f"order_path_{cohort_id}_rollup",
            sql=(
                f"SELECT tenant_id, COUNT(*), SUM(amount) FROM {_DB}.{_EVENTS_TABLE} "
                "WHERE tenant_id IN (7, 11, 19) AND event_id BETWEEN 1 AND 2000 "
                "GROUP BY tenant_id"
            ),
            qps=3.5,
            **{key: value for key, value in common.items() if key != "qps"},
        ),
    )


_COHORT_PROFILE_GROUPS = {
    cohort_id: _cohort_profiles(cohort_id)
    for cohort_id, _connector, _checkout, _index in _COHORTS
}
_TARGET_PROFILE_NAMES = tuple(profile.name for profile in _COHORT_PROFILE_GROUPS[_TARGET_COHORT])
_ALL_COHORT_PROFILE_NAMES = tuple(
    profile.name
    for cohort_id in _COHORT_PROFILE_GROUPS
    for profile in _COHORT_PROFILE_GROUPS[cohort_id]
)

_NOISE_PROFILES = (
    WorkloadProfile(
        name="order_dashboard_summary",
        sql=(
            f"SELECT tenant_id, status, COUNT(*), SUM(amount) FROM {_DB}.{_ORDERS_TABLE} "
            "GROUP BY tenant_id, status ORDER BY tenant_id, status"
        ),
        qps=1.1,
        tier="REPORTING",
        application_name="orders-dashboard",
        target="tidb/tidb-0",
        transactional=False,
    ),
    WorkloadProfile(
        name="inventory_health_scan",
        sql=(
            f"SELECT warehouse_id, COUNT(*), SUM(available) FROM {_DB}.{_INVENTORY_TABLE} "
            "GROUP BY warehouse_id ORDER BY warehouse_id"
        ),
        qps=0.9,
        tier="INVENTORY",
        application_name="inventory-monitor",
        target="tidb/tidb-1",
        transactional=False,
    ),
    WorkloadProfile(
        name="order_preview_probe",
        sql=f"SELECT COUNT(*) FROM {_DB}.{_ORDERS_TABLE} WHERE amount > 50",
        qps=0.8,
        tier="REPORTING",
        application_name="order-preview",
        target="tidb/tidb-0",
        transactional=False,
    ),
    WorkloadProfile(
        name="reconciliation_error_probe",
        sql=f"SELECT COUNT(*) FROM {_DB}.reconciliation_cache_missing",
        qps=0.25,
        tier="MONITORING",
        application_name="reconciliation-monitor",
        target="tidb/tidb-1",
        transactional=False,
    ),
)

_SET_AUTOCOMMIT_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=tuple(
        profile
        for cohort_id in _COHORT_PROFILE_GROUPS
        for profile in _COHORT_PROFILE_GROUPS[cohort_id]
    ) + _NOISE_PROFILES,
    worker_count=8,
    seed=20260811,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=18,
)

_SET_AUTOCOMMIT_FOCUSED_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=tuple(
        profile
        for cohort_id in _COHORT_PROFILE_GROUPS
        for profile in _COHORT_PROFILE_GROUPS[cohort_id]
    ),
    worker_count=6,
    seed=20260813,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=16,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfSetAutocommitStormForAutocommitStormCpuSaturationScenarioCase(TiDBScenarioCase):
    db: str
    events_table: str
    orders_table: str
    inventory_table: str
    assignments_table: str
    connector_table: str
    checkout_table: str
    rollouts_table: str
    revision_catalog_table: str
    target_cohort: str
    initial_target_connector_revision: str
    initial_target_checkout_revision: str
    initial_target_deployment_lane: str
    initial_target_session_binding_mode: str
    initial_target_session_lease_mode: str
    cohort_ids: tuple[str, ...]
    target_profile_names: tuple[str, ...]
    business_query: str
    event_integrity_sql: str
    orders_integrity_sql: str
    inventory_integrity_sql: str


_SET_AUTOCOMMIT_CASE = TidbQueryPerfSetAutocommitStormForAutocommitStormCpuSaturationScenarioCase(
    case_id="autocommit_storm_cpu_saturation",
    reference_report=structured_reference_report(
        case_id="autocommit_storm_cpu_saturation",
        factors=(
            "TiDB SQL/session 前端的高频 session-state traffic 是 CPU 主要来源，慢业务 SQL、TiKV 和 PD 不是主要矛盾",
            "同一 SET digest 只有一个 deployment cohort 的 SET/business ratio 异常，三个在线 sibling 是健康反事实",
            "只有 deployment lane=canary 与 session lease mode=renew_on_checkout 同时存在时，session-state reset 循环才会放大；connector/checkout revision 和 session binding mode 只是相关配置",
        ),
        changes=(
            "changed only the affected cohort desired session lease mode to fixed",
            "preserved cohort capacity, traffic, business data and the three healthy siblings",
        ),
        verification=(
            "verified the target cohort no longer emits the session-state storm",
            "verified business truth, workload success, node health and protected assignments",
        ),
        summary="The reference path used four online revision, deployment-state and session-lease combinations to identify and break the only causal interaction.",
    ),
    case_no=0,
    evaluator=TidbQueryPerfSetAutocommitStormEvaluatorCase,
    title="Order-maintenance database performance incident",
    alert=(
        "[CRITICAL] 订单数据清理接口的 p95/p99 延迟持续恶化，数据库集群出现 CPU 告警，"
        "但请求吞吐没有同幅增长。请定位并修复主要原因，恢复接口和数据库状态。"
        "允许对经证据确认的应用运行时配置做有界修改；不得修改业务数据、健康 cohort、"
        "集群拓扑或 TiDB 全局参数，也不得通过重启、停流或缩小既有业务容量掩盖问题。"
    ),
    initial_state={
        "status": "degraded",
        "symptoms": ("order-maintenance p95/p99 degradation", "database CPU alert", "flat request throughput"),
        "protected_scope": ("business data", "healthy cohorts", "cluster topology", "existing capacity"),
    },
    expected_target={
        "status": "recovered",
        "target_cohort": _TARGET_COHORT,
        "business_truth": "unchanged",
        "healthy_siblings": 3,
        "cluster": "healthy",
    },
    background_workload=_SET_AUTOCOMMIT_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=120,
        image_group_key=None,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=10,
        environmental_complexity=0.506568,
        reference_run_ids=(
            "reference-284__tidb_query_perf_set_autocommit_storm__autocommit_storm_cpu_saturation__mock__r001",
            "reference-284__tidb_query_perf_set_autocommit_storm__autocommit_storm_cpu_saturation__mock__r002",
        ),
    ),
    db=_DB,
    events_table=_EVENTS_TABLE,
    orders_table=_ORDERS_TABLE,
    inventory_table=_INVENTORY_TABLE,
    assignments_table=_ASSIGNMENTS_TABLE,
    connector_table=_CONNECTOR_TABLE,
    checkout_table=_CHECKOUT_TABLE,
    rollouts_table=_ROLLOUTS_TABLE,
    revision_catalog_table=_REVISION_CATALOG_TABLE,
    target_cohort=_TARGET_COHORT,
    initial_target_connector_revision="r2",
    initial_target_checkout_revision="h2",
    initial_target_deployment_lane="canary",
    initial_target_session_binding_mode="rebind",
    initial_target_session_lease_mode="renew_on_checkout",
    cohort_ids=tuple(cohort_id for cohort_id, _connector, _checkout, _index in _COHORTS),
    target_profile_names=_TARGET_PROFILE_NAMES,
    business_query=_BUSINESS_QUERY,
    event_integrity_sql=_EVENT_INTEGRITY_SQL,
    orders_integrity_sql=_ORDERS_INTEGRITY_SQL,
    inventory_integrity_sql=_INVENTORY_INTEGRITY_SQL,
)

_SET_AUTOCOMMIT_FOCUSED_CASE = replace(
    _SET_AUTOCOMMIT_CASE,
    case_id="autocommit_storm_rollout_focus",
    case_no=1,
    evaluator=TidbQueryPerfSetAutocommitStormFocusedEvaluatorCase,
    title="Focused order-maintenance database performance incident",
    alert=(
        "[CRITICAL] 订单数据清理接口的 p95/p99 延迟持续恶化，数据库出现 CPU 告警，"
        "但请求吞吐没有同幅增长。请定位并修复主要原因，恢复接口和数据库状态。"
        "允许对经证据确认的应用运行时配置做有界修改；不得修改业务数据、健康 cohort、"
        "集群拓扑或 TiDB 全局参数，也不得通过重启或缩小既有业务容量掩盖问题。"
    ),
    initial_state={
        "status": "degraded",
        "symptoms": ("order-maintenance p95/p99 degradation", "database CPU alert", "flat request throughput"),
        "protected_scope": ("business data", "healthy cohorts", "cluster topology", "existing capacity"),
        "background_noise_profiles": 0,
    },
    background_workload=_SET_AUTOCOMMIT_FOCUSED_BACKGROUND_WORKLOAD,
    difficulty=DifficultyCalibration(
        diagnostic_depth=8,
        environmental_complexity=0.48366,
        reference_run_ids=(
            "tidb-reference-15__tidb_query_perf_set_autocommit_storm__"
            "autocommit_storm_rollout_focus__mock__r001",
        ),
    ),
)


class TidbQueryPerfSetAutocommitStormScenario(TiDBScenario):
    scenario_id = "tidb_query_perf_set_autocommit_storm"
    description = "Investigate a degraded order-maintenance service and restore its database-backed request path."
    cases = (_SET_AUTOCOMMIT_CASE, _SET_AUTOCOMMIT_FOCUSED_CASE)

    def build_fault_plan(
        self,
        case: TidbQueryPerfSetAutocommitStormForAutocommitStormCpuSaturationScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbQueryPerfSetAutocommitStormInjector,
                config={
                    "db": case.db,
                    "events_table": case.events_table,
                    "orders_table": case.orders_table,
                    "inventory_table": case.inventory_table,
                    "assignments_table": case.assignments_table,
                    "connector_table": case.connector_table,
                    "checkout_table": case.checkout_table,
                    "rollouts_table": case.rollouts_table,
                    "revision_catalog_table": case.revision_catalog_table,
                    "target_cohort": case.target_cohort,
                    "initial_target_connector_revision": case.initial_target_connector_revision,
                    "initial_target_checkout_revision": case.initial_target_checkout_revision,
                    "initial_target_deployment_lane": case.initial_target_deployment_lane,
                    "initial_target_session_binding_mode": case.initial_target_session_binding_mode,
                    "initial_target_session_lease_mode": case.initial_target_session_lease_mode,
                    "cohort_ids": case.cohort_ids,
                    "target_profile_names": case.target_profile_names,
                    "business_query": case.business_query,
                    "event_integrity_sql": case.event_integrity_sql,
                    "orders_integrity_sql": case.orders_integrity_sql,
                    "inventory_integrity_sql": case.inventory_integrity_sql,
                    "workload_profile_count": len(case.background_workload.profiles),
                },
            ),
        )


class TidbQueryPerfSetAutocommitStormInjector(BaseFaultInjector):
    """Install four online client combinations with one causal interaction."""

    def __init__(self) -> None:
        self._router_initialized = False
        self._router_invalidation_registered = False
        self._reconcile_hook_registered = False
        self._reconcile_env = None
        self._reconcile_lock = threading.RLock()
        self._last_reconcile_monotonic = 0.0
        self._reconcile_count = 0
        self._last_connection_invalidation_generation = 0
        self._resource_control_before = None
        self._statement_summary_before = None
        self._resource_groups_created = False

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        with context.env.metrics_hidden():
            self._create_schema(context.env)
            self._load_events(context.env)
            self._create_noise_tables(context.env)
            self._create_resource_groups(context.env)
            self._initialize_routers(context.env)
            self._register_reconcile_hook(context.env)
            self._reconcile_control_plane(context.env, force=True)
            self._verify_fault_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._create_resource_groups(context.env)
        self._initialize_routers(context.env)
        self._register_reconcile_hook(context.env)
        self._reconcile_control_plane(context.env, force=True)
        self._verify_fault_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._verify_fault_state(context.env)
        env = context.env
        activity = require_success_payload(
            env.observe_metric("workload_activity", limit=self.workload_profile_count),
            "capture set-autocommit workload activity",
        )
        profiles = self._profile_rows(activity)
        missing = [name for name in self.all_cohort_profile_names if name not in profiles]
        if missing:
            raise RuntimeError(
                "set-autocommit workload did not observe every cohort profile: "
                f"missing={missing!r}, observed={sorted(profiles)!r}"
            )
        inactive = {
            name: profiles[name]
            for name in self.all_cohort_profile_names
            if profiles[name]["calls"] <= 0
        }
        if inactive:
            raise RuntimeError(
                "set-autocommit cohort profiles did not execute during warmup: "
                f"profiles={inactive!r}"
            )

        statement_summary_sql = (
            "SELECT INSTANCE, RESOURCE_GROUP, STMT_TYPE, DIGEST, DIGEST_TEXT, EXEC_COUNT, "
            "AVG_LATENCY, SUM_LATENCY, AVG_PARSE_LATENCY, AVG_COMPILE_LATENCY, "
            "AVG_PROCESS_TIME, AVG_PROCESSED_KEYS, FIRST_SEEN, LAST_SEEN "
            "FROM information_schema.cluster_statements_summary "
            "ORDER BY EXEC_COUNT DESC LIMIT 200"
        )
        self._clear_statement_summary(env)
        self._run_historical_rollout_window(env)
        statement_summary = self._wait_for_statement_summary(env, statement_summary_sql)
        set_rows = [
            row
            for row in statement_summary["result"]
            if len(row) >= 5 and "autocommit" in str(row[4]).casefold()
        ]
        if not set_rows:
            raise RuntimeError(
                "set-autocommit warmup produced no autocommit statement summary rows: "
                f"summary={statement_summary!r}"
            )

        processlist_sql = (
            "SELECT INSTANCE, ID, USER, RESOURCE_GROUP, SESSION_ALIAS, DB, STATE, INFO "
            "FROM information_schema.cluster_processlist "
            "WHERE SESSION_ALIAS <> '' ORDER BY INSTANCE, ID LIMIT 200"
        )
        processlist = execute_json_payload(env.execute_sql, processlist_sql, "capture set-autocommit processlist")
        observed_aliases = {str(row[4]) for row in processlist["result"] if len(row) >= 5}
        missing_aliases = sorted(
            set(self.session_aliases.values()) - observed_aliases
        )
        if missing_aliases:
            raise RuntimeError(
                "set-autocommit processlist did not expose all cohort aliases: "
                f"missing={missing_aliases!r}, observed={sorted(observed_aliases)!r}"
            )

        assignments_sql = (
            f"SELECT cohort_id, service_name, resource_group, session_alias_prefix, traffic_weight, "
            f"pool_size, connector_revision, checkout_revision, enabled, deployment_lane, "
            f"session_binding_mode, session_lease_mode "
            f"FROM {self.db}.{self.assignments_table} ORDER BY cohort_id"
        )
        connector_sql = (
            f"SELECT revision_id, use_local_session_state, elide_set_autocommits, "
            f"cache_server_configuration, always_send_set_isolation "
            f"FROM {self.db}.{self.connector_table} ORDER BY revision_id"
        )
        checkout_sql = (
            f"SELECT revision_id, reset_mode, reset_count, validation_mode, transaction_boundary_mode "
            f"FROM {self.db}.{self.checkout_table} ORDER BY revision_id"
        )
        assignments = execute_json_payload(env.execute_sql, assignments_sql, "capture set-autocommit assignments")
        connectors = execute_json_payload(env.execute_sql, connector_sql, "capture set-autocommit connector revisions")
        checkouts = execute_json_payload(env.execute_sql, checkout_sql, "capture set-autocommit checkout revisions")
        business_payload = execute_json_payload(env.execute_sql, self.business_query, "capture set-autocommit business truth")
        ma03_cpu = self._capture_settled_metric(env, "cpu", "capture set-autocommit metric=cpu")
        return {
            "ma03_cpu": ma03_cpu,
            "ma03_qps": require_success_payload(env.query_metrics("qps"), "capture set-autocommit metric=qps"),
            "ma03_query_latency": require_success_payload(
                env.query_metrics("query_latency"), "capture set-autocommit metric=query_latency"
            ),
            "ma03_active_connections": require_success_payload(
                env.query_metrics("active_connections"), "capture set-autocommit metric=active_connections"
            ),
            "ma03_slow_queries": require_success_payload(
                env.observe_metric("slow_queries"), "capture set-autocommit metric=slow_queries"
            ),
            "ma03_topsql": require_success_payload(env.observe_metric("topsql"), "capture set-autocommit metric=topsql"),
            "ma03_node_health": require_success_payload(
                env.manage_cluster("service", "list"), "capture set-autocommit service health"
            ),
            "ma03_workload_activity": activity,
            "ma03_statement_summary": statement_summary,
            "ma03_statement_summary_sql": statement_summary_sql,
            "ma03_processlist": processlist,
            "ma03_processlist_sql": processlist_sql,
            "ma03_runtime_assignments": assignments,
            "ma03_runtime_assignments_sql": assignments_sql,
            "ma03_connector_revisions": connectors,
            "ma03_checkout_revisions": checkouts,
            "ma03_runtime_rollouts": self._query_rollouts(env),
            "ma03_revision_catalog": self._query_revision_catalog(env),
            "business_result_truth": capture_query_result_truth(business_payload, ordered=True),
            "ma03_event_integrity": self._integrity(env, self.event_integrity_sql, "set-autocommit event integrity"),
            "ma03_orders_integrity": self._integrity(env, self.orders_integrity_sql, "set-autocommit order integrity"),
            "ma03_inventory_integrity": self._integrity(
                env, self.inventory_integrity_sql, "set-autocommit inventory integrity"
            ),
        }

    def _capture_settled_metric(self, env: object, metric: str, context: str) -> Mapping[str, object]:
        """Live container metrics depend on cAdvisor's settled per-container scrapes.

        Deployment readiness only proves the cAdvisor endpoint answered once; the
        per-container samples for this deployment can lag behind it or stall under
        host load, which empties the whole rate window at capture time. Wait for
        the capture to settle instead of failing on an empty scrape window.
        """
        deadline = time.monotonic() + _SET_AUTOCOMMIT_MONITORING_SETTLE_DEADLINE_SECONDS
        while True:
            try:
                return require_success_payload(env.query_metrics(metric), context)
            except RuntimeError as exc:
                if time.monotonic() >= deadline:
                    raise RuntimeError(
                        f"{context} did not settle before the bounded monitoring-scrape deadline: last_error={exc}"
                    ) from exc
                time.sleep(_SET_AUTOCOMMIT_MONITORING_SETTLE_INTERVAL_SECONDS)

    def _run_historical_rollout_window(self, env) -> None:
        self._set_desired_rollout(
            env,
            _HISTORICAL_ROLLOUT_COHORT,
            checkout="h2",
            session_binding_mode="rebind",
            session_lease_mode="renew_on_checkout",
        )
        self._reconcile_control_plane(env, force=True)
        time.sleep(_HISTORICAL_ROLLOUT_SECONDS)
        self._set_desired_rollout(
            env,
            _HISTORICAL_ROLLOUT_COHORT,
            checkout="h1",
            session_binding_mode="steady",
            session_lease_mode="fixed",
        )
        self._reconcile_control_plane(env, force=True)
        time.sleep(_CURRENT_INCIDENT_WINDOW_SECONDS)

    def attach_workload_runner(self, runner) -> None:
        if getattr(self, "_workload_runner", None) is not None:
            raise RuntimeError("set-autocommit reconcile workload runner is already attached")
        self._workload_runner = runner
        runner.set_before_profile_hook(self._before_workload_profile)

    def _before_workload_profile(self) -> None:
        if self._reconcile_hook_registered:
            generation = self._reconcile_env.workload_connection_invalidation_generation()
            self._reconcile_control_plane(
                self._reconcile_env,
                force=generation != self._last_connection_invalidation_generation,
            )

    def _register_reconcile_hook(self, env) -> None:
        if self._reconcile_hook_registered and self._reconcile_env is not env:
            raise RuntimeError("set-autocommit reconcile hook is attached to a different environment")
        self._reconcile_env = env
        self._reconcile_hook_registered = True

    def _clear_reconcile_hook(self, env) -> None:
        if self._reconcile_hook_registered and self._reconcile_env is not env:
            raise RuntimeError("set-autocommit reconcile hook environment mismatch")
        self._reconcile_hook_registered = False
        self._reconcile_env = None
        self._workload_runner = None

    def _control_query(self, env, sql: str, context: str) -> dict:
        executor = getattr(env, "execute_internal_sql", None)
        if executor is None:
            raise RuntimeError(
                "set-autocommit control-plane reconcile requires TiDBEnv.execute_internal_sql: "
                f"context={context!r}, environment={type(env).__name__!r}"
            )
        return execute_json_payload(executor, sql, context)

    def _query_rollouts(self, env) -> dict:
        return self._control_query(
            env,
            f"SELECT cohort_id, desired_connector_revision, desired_checkout_revision, "
            f"desired_deployment_lane, desired_session_binding_mode, desired_session_lease_mode, generation, "
            f"applied_generation, rollout_state, last_reconcile_at FROM {self.db}.{self.rollouts_table} "
            "ORDER BY cohort_id",
            "query set-autocommit runtime rollouts",
        )

    def _query_revision_catalog(self, env) -> dict:
        return self._control_query(
            env,
            f"SELECT revision_id, revision_kind, scope, owner_cohort_id, use_local_session_state, "
            f"elide_set_autocommits, cache_server_configuration, always_send_set_isolation, "
            f"reset_mode, reset_count, validation_mode, transaction_boundary_mode, session_lease_mode "
            f"FROM {self.db}.{self.revision_catalog_table} ORDER BY revision_id",
            "query set-autocommit revision catalog",
        )

    def _set_desired_rollout(
        self,
        env,
        cohort_id: str,
        *,
        connector: str | None = None,
        checkout: str | None = None,
        deployment_lane: str | None = None,
        session_binding_mode: str | None = None,
        session_lease_mode: str | None = None,
    ) -> None:
        assignments = []
        if connector is not None:
            assignments.append(f"desired_connector_revision='{connector}'")
        if checkout is not None:
            assignments.append(f"desired_checkout_revision='{checkout}'")
        if deployment_lane is not None:
            assignments.append(f"desired_deployment_lane='{deployment_lane}'")
        if session_binding_mode is not None:
            assignments.append(f"desired_session_binding_mode='{session_binding_mode}'")
        if session_lease_mode is not None:
            assignments.append(f"desired_session_lease_mode='{session_lease_mode}'")
        if not assignments:
            raise ValueError(f"set-autocommit desired rollout update requires a revision: cohort_id={cohort_id!r}")
        assignments.extend(("generation=generation+1", "rollout_state='pending'"))
        execute_json_payload(
            env.execute_sql,
            f"UPDATE {self.db}.{self.rollouts_table} SET {', '.join(assignments)} "
            f"WHERE cohort_id='{cohort_id}'",
            f"update set-autocommit desired rollout for {cohort_id}",
        )

    def _reconcile_control_plane(self, env, *, force: bool = False) -> None:
        now = time.monotonic()
        if not force and now - self._last_reconcile_monotonic < _RECONCILE_INTERVAL_SECONDS:
            return
        with self._reconcile_lock:
            now = time.monotonic()
            if not force and now - self._last_reconcile_monotonic < _RECONCILE_INTERVAL_SECONDS:
                return
            rollouts = self._query_rollouts(env)["result"]
            assignments = self._control_query(
                env,
            f"SELECT cohort_id, connector_revision, checkout_revision, deployment_lane, session_binding_mode, session_lease_mode "
                f"FROM {self.db}.{self.assignments_table} "
                "ORDER BY cohort_id",
                "query set-autocommit current assignments for reconcile",
            )["result"]
            catalog = self._query_revision_catalog(env)["result"]
            rollout_by_id = {str(row[0]): row for row in rollouts}
            assignment_by_id = {str(row[0]): row for row in assignments}
            if set(rollout_by_id) != set(self.cohort_ids):
                raise RuntimeError(
                    "set-autocommit rollout cohort contract mismatch: "
                    f"expected={sorted(self.cohort_ids)!r}, observed={sorted(rollout_by_id)!r}"
                )
            if set(assignment_by_id) != set(self.cohort_ids):
                raise RuntimeError(
                    "set-autocommit assignment cohort contract mismatch during reconcile: "
                    f"expected={sorted(self.cohort_ids)!r}, observed={sorted(assignment_by_id)!r}"
                )
            connectors = {
                str(row[0]): row
                for row in execute_json_payload(
                    env.execute_internal_sql,
                    f"SELECT revision_id, use_local_session_state, elide_set_autocommits, "
                    f"cache_server_configuration, always_send_set_isolation FROM {self.db}.{self.connector_table} "
                    "ORDER BY revision_id",
                    "query set-autocommit connector revisions for reconcile",
                )["result"]
            }
            checkouts = {
                str(row[0]): row
                for row in execute_json_payload(
                    env.execute_internal_sql,
                    f"SELECT revision_id, reset_mode, reset_count, validation_mode, transaction_boundary_mode "
                    f"FROM {self.db}.{self.checkout_table} ORDER BY revision_id",
                    "query set-autocommit checkout revisions for reconcile",
                )["result"]
            }
            revision_drift = []
            for row in catalog:
                revision_id = str(row[0])
                if str(row[1]).casefold() == "connector":
                    current = connectors.get(revision_id)
                    expected = [revision_id, int(row[4]), int(row[5]), int(row[6]), int(row[7])]
                    if current is None:
                        raise RuntimeError(
                            "set-autocommit revision catalog references a missing connector revision: "
                            f"revision_id={revision_id!r}"
                        )
                    if list(current) != expected:
                        revision_drift.append(
                            f"UPDATE {self.db}.{self.connector_table} SET "
                            f"use_local_session_state={expected[1]}, elide_set_autocommits={expected[2]}, "
                            f"cache_server_configuration={expected[3]}, always_send_set_isolation={expected[4]} "
                            f"WHERE revision_id='{revision_id}'"
                        )
                elif str(row[1]).casefold() == "checkout":
                    current = checkouts.get(revision_id)
                    expected = [revision_id, row[8], int(row[9]), row[10], row[11]]
                    if current is None:
                        raise RuntimeError(
                            "set-autocommit revision catalog references a missing checkout revision: "
                            f"revision_id={revision_id!r}"
                        )
                    if list(current) != expected:
                        revision_drift.append(
                            f"UPDATE {self.db}.{self.checkout_table} SET reset_mode='{expected[1]}', "
                            f"reset_count={expected[2]}, validation_mode='{expected[3]}', "
                            f"transaction_boundary_mode='{expected[4]}' WHERE revision_id='{revision_id}'"
                        )
                elif str(row[1]).casefold() == "session_lease":
                    lease_mode = str(row[12])
                    if lease_mode not in _SESSION_LEASE_MODES:
                        raise RuntimeError(
                            "set-autocommit revision catalog has unsupported session lease mode: "
                            f"revision_id={revision_id!r}, session_lease_mode={lease_mode!r}"
                        )
                else:
                    raise RuntimeError(
                        "set-autocommit revision catalog has an unsupported revision kind: "
                        f"revision_id={revision_id!r}, revision_kind={row[1]!r}"
                    )
            for statement in revision_drift:
                self._control_query(env, statement, "restore set-autocommit shared revision from catalog")
            assignment_drift = []
            rollout_updates = []
            for cohort_id in self.cohort_ids:
                rollout = rollout_by_id[cohort_id]
                current = assignment_by_id[cohort_id]
                desired_connector = str(rollout[1])
                desired_checkout = str(rollout[2])
                desired_lane = str(rollout[3])
                desired_binding = str(rollout[4])
                desired_lease = str(rollout[5])
                if (
                    desired_lane not in _DEPLOYMENT_LANES
                    or desired_binding not in _SESSION_BINDING_MODES
                    or desired_lease not in _SESSION_LEASE_MODES
                ):
                    raise RuntimeError(
                        "set-autocommit rollout has unsupported deployment state: "
                        f"cohort_id={cohort_id!r}, lane={desired_lane!r}, binding={desired_binding!r}, "
                        f"lease={desired_lease!r}"
                    )
                if desired_connector not in connectors or desired_checkout not in checkouts:
                    raise RuntimeError(
                        "set-autocommit rollout references an unknown revision: "
                        f"cohort_id={cohort_id!r}, desired_connector={desired_connector!r}, "
                        f"desired_checkout={desired_checkout!r}"
                    )
                lease_catalog_modes = {
                    str(row[12])
                    for row in catalog
                    if str(row[1]).casefold() == "session_lease"
                }
                if desired_lease not in lease_catalog_modes:
                    raise RuntimeError(
                        "set-autocommit rollout references an unregistered session lease mode: "
                        f"cohort_id={cohort_id!r}, session_lease_mode={desired_lease!r}, "
                        f"catalog_modes={sorted(lease_catalog_modes)!r}"
                    )
                if (
                    str(current[1]) != desired_connector
                    or str(current[2]) != desired_checkout
                    or str(current[3]) != desired_lane
                    or str(current[4]) != desired_binding
                    or str(current[5]) != desired_lease
                ):
                    assignment_drift.append(
                        f"UPDATE {self.db}.{self.assignments_table} SET connector_revision='{desired_connector}', "
                        f"checkout_revision='{desired_checkout}', deployment_lane='{desired_lane}', "
                        f"session_binding_mode='{desired_binding}', session_lease_mode='{desired_lease}' "
                        f"WHERE cohort_id='{cohort_id}'"
                    )
                if (
                    str(current[1]) != desired_connector
                    or str(current[2]) != desired_checkout
                    or str(current[3]) != desired_lane
                    or str(current[4]) != desired_binding
                    or str(current[5]) != desired_lease
                    or int(rollout[7]) != int(rollout[6])
                    or str(rollout[8]).casefold() != "applied"
                ):
                    rollout_updates.append(
                        f"UPDATE {self.db}.{self.rollouts_table} SET applied_generation=generation, "
                        f"rollout_state='applied', last_reconcile_at=NOW() WHERE cohort_id='{cohort_id}'"
                    )
            for statement in assignment_drift:
                self._control_query(env, statement, "apply set-autocommit desired rollout assignment")
            for statement in rollout_updates:
                self._control_query(env, statement, "mark set-autocommit rollout applied")
            self._last_reconcile_monotonic = time.monotonic()
            self._last_connection_invalidation_generation = (
                env.workload_connection_invalidation_generation()
            )
            self._reconcile_count += 1

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._clear_reconcile_hook(context.env)
        self._reset_routers(context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._clear_reconcile_hook(context.env)
        self._reset_routers(context.env)
        for table in (
            self.assignments_table,
            self.connector_table,
            self.checkout_table,
            self.rollouts_table,
            self.revision_catalog_table,
            self.events_table,
            self.orders_table,
            self.inventory_table,
        ):
            execute_json_payload(
                context.env.execute_sql,
                f"DROP TABLE IF EXISTS {self.db}.{table}",
                f"drop set-autocommit table {self.db}.{table}",
            )
        if self._resource_groups_created:
            for resource_group in self.resource_groups:
                execute_json_payload(
                    context.env.execute_sql,
                    f"DROP RESOURCE GROUP {resource_group}",
                    f"drop set-autocommit resource group {resource_group}",
                )
            self._resource_groups_created = False
        if self._resource_control_before is not None:
            execute_json_payload(
                context.env.execute_sql,
                f"SET GLOBAL tidb_enable_resource_control = {self._resource_control_before}",
                "restore set-autocommit resource control",
            )
        if self._statement_summary_before is not None:
            execute_json_payload(
                context.env.execute_sql,
                f"SET GLOBAL tidb_enable_stmt_summary = {self._statement_summary_before}",
                "restore set-autocommit statement summary",
            )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.events_table = validate_sql_identifier(str(config["events_table"]), "events_table")
        self.orders_table = validate_sql_identifier(str(config["orders_table"]), "orders_table")
        self.inventory_table = validate_sql_identifier(str(config["inventory_table"]), "inventory_table")
        self.assignments_table = validate_sql_identifier(str(config["assignments_table"]), "assignments_table")
        self.connector_table = validate_sql_identifier(str(config["connector_table"]), "connector_table")
        self.checkout_table = validate_sql_identifier(str(config["checkout_table"]), "checkout_table")
        self.rollouts_table = validate_sql_identifier(str(config["rollouts_table"]), "rollouts_table")
        self.revision_catalog_table = validate_sql_identifier(
            str(config["revision_catalog_table"]), "revision_catalog_table"
        )
        self.target_cohort = str(config["target_cohort"])
        self.initial_target_connector_revision = str(config["initial_target_connector_revision"])
        self.initial_target_checkout_revision = str(config["initial_target_checkout_revision"])
        self.initial_target_deployment_lane = str(config["initial_target_deployment_lane"])
        self.initial_target_session_binding_mode = str(config["initial_target_session_binding_mode"])
        self.initial_target_session_lease_mode = str(config["initial_target_session_lease_mode"])
        self.cohort_ids = tuple(str(item) for item in config["cohort_ids"])
        self.target_profile_names = tuple(str(item) for item in config["target_profile_names"])
        self.all_cohort_profile_names = _ALL_COHORT_PROFILE_NAMES
        self.resource_groups = tuple(_RESOURCE_GROUPS[cohort] for cohort in self.cohort_ids)
        self.session_aliases = {cohort: _SESSION_ALIASES[cohort] for cohort in self.cohort_ids}
        self.router_config = {
            _ROUTERS[cohort]: {"initial_target": f"tidb/tidb-{index % 2}"}
            for index, cohort in enumerate(self.cohort_ids)
        }
        self.business_query = str(config["business_query"])
        self.event_integrity_sql = str(config["event_integrity_sql"])
        self.orders_integrity_sql = str(config["orders_integrity_sql"])
        self.inventory_integrity_sql = str(config["inventory_integrity_sql"])
        self.workload_profile_count = int(config["workload_profile_count"])

    def _create_schema(self, env) -> None:
        execute_json_payload(env.execute_sql, f"CREATE DATABASE IF NOT EXISTS {self.db}", "create set-autocommit database")
        for table in (
            self.assignments_table,
            self.connector_table,
            self.checkout_table,
            self.rollouts_table,
            self.revision_catalog_table,
            self.events_table,
            self.orders_table,
            self.inventory_table,
        ):
            execute_json_payload(
                env.execute_sql,
                f"DROP TABLE IF EXISTS {self.db}.{table}",
                f"clear set-autocommit table {self.db}.{table}",
            )
        execute_json_payload(
            env.execute_sql,
            f"CREATE TABLE {self.db}.{self.connector_table} ("
            "revision_id VARCHAR(32) PRIMARY KEY, "
            "use_local_session_state TINYINT NOT NULL, "
            "elide_set_autocommits TINYINT NOT NULL, "
            "cache_server_configuration TINYINT NOT NULL, "
            "always_send_set_isolation TINYINT NOT NULL"
            ")",
            "create set-autocommit connector revisions",
        )
        execute_json_payload(
            env.execute_sql,
            f"CREATE TABLE {self.db}.{self.checkout_table} ("
            "revision_id VARCHAR(32) PRIMARY KEY, "
            "reset_mode VARCHAR(32) NOT NULL, "
            "reset_count INT NOT NULL, "
            "validation_mode VARCHAR(32) NOT NULL, "
            "transaction_boundary_mode VARCHAR(32) NOT NULL"
            ")",
            "create set-autocommit checkout revisions",
        )
        execute_json_payload(
            env.execute_sql,
            f"CREATE TABLE {self.db}.{self.revision_catalog_table} ("
            "revision_id VARCHAR(32) PRIMARY KEY, "
            "revision_kind ENUM('connector', 'checkout', 'session_lease') NOT NULL, "
            "scope ENUM('shared', 'target') NOT NULL, "
            "owner_cohort_id VARCHAR(32) NULL, "
            "use_local_session_state TINYINT NULL, "
            "elide_set_autocommits TINYINT NULL, "
            "cache_server_configuration TINYINT NULL, "
            "always_send_set_isolation TINYINT NULL, "
            "reset_mode VARCHAR(32) NULL, "
            "reset_count INT NULL, "
            "validation_mode VARCHAR(32) NULL, "
            "transaction_boundary_mode VARCHAR(32) NULL, "
            "session_lease_mode ENUM('fixed', 'renew_on_checkout') NULL"
            ")",
            "create set-autocommit revision catalog",
        )
        execute_json_payload(
            env.execute_sql,
            f"CREATE TABLE {self.db}.{self.assignments_table} ("
            "cohort_id VARCHAR(32) PRIMARY KEY, "
            "service_name VARCHAR(64) NOT NULL, "
            "resource_group VARCHAR(64) NOT NULL, "
            "session_alias_prefix VARCHAR(64) NOT NULL, "
            "traffic_weight INT NOT NULL, "
            "pool_size INT NOT NULL, "
            "connector_revision VARCHAR(32) NOT NULL, "
            "checkout_revision VARCHAR(32) NOT NULL, "
            "enabled TINYINT NOT NULL, "
            "deployment_lane ENUM('stable', 'canary') NOT NULL, "
            "session_binding_mode ENUM('steady', 'rebind') NOT NULL, "
            "session_lease_mode ENUM('fixed', 'renew_on_checkout') NOT NULL"
            ")",
            "create set-autocommit runtime assignments",
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.connector_table} "
            "(revision_id, use_local_session_state, elide_set_autocommits, cache_server_configuration, always_send_set_isolation) VALUES "
            "('r1', 1, 1, 1, 0), ('r2', 0, 0, 1, 0)",
            "seed set-autocommit connector revisions",
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.checkout_table} "
            "(revision_id, reset_mode, reset_count, validation_mode, transaction_boundary_mode) VALUES "
            "('h1', 'transition', 1, 'ping', 'request'), "
            f"('h2', 'per_checkout', {_PER_CHECKOUT_RESET_COUNT}, 'ping', 'request')",
            "seed set-autocommit checkout revisions",
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.revision_catalog_table} "
            "(revision_id, revision_kind, scope, owner_cohort_id, use_local_session_state, "
            "elide_set_autocommits, cache_server_configuration, always_send_set_isolation, "
            "reset_mode, reset_count, validation_mode, transaction_boundary_mode, session_lease_mode) VALUES "
            "('r1', 'connector', 'shared', NULL, 1, 1, 1, 0, NULL, NULL, NULL, NULL, NULL), "
            "('r2', 'connector', 'shared', NULL, 0, 0, 1, 0, NULL, NULL, NULL, NULL, NULL), "
            "('h1', 'checkout', 'shared', NULL, NULL, NULL, NULL, NULL, 'transition', 1, 'ping', 'request', NULL), "
            f"('h2', 'checkout', 'shared', NULL, NULL, NULL, NULL, NULL, 'per_checkout', {_PER_CHECKOUT_RESET_COUNT}, 'ping', 'request', NULL), "
            "('lease-fixed', 'session_lease', 'shared', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'fixed'), "
            "('lease-renew', 'session_lease', 'shared', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'renew_on_checkout')",
            "seed set-autocommit revision catalog",
        )
        assignment_values = ", ".join(
            f"('{cohort}', 'order-maintenance', '{_RESOURCE_GROUPS[cohort]}', '{_SESSION_ALIASES[cohort]}', 25, 8, "
            f"'{self.initial_target_connector_revision if cohort == self.target_cohort else connector}', "
            f"'{self.initial_target_checkout_revision if cohort == self.target_cohort else checkout}', 1, "
            f"'{self.initial_target_deployment_lane if cohort == self.target_cohort else _COHORT_STATES[cohort][0]}', "
            f"'{self.initial_target_session_binding_mode if cohort == self.target_cohort else _COHORT_STATES[cohort][1]}', "
            f"'{self.initial_target_session_lease_mode if cohort == self.target_cohort else _COHORT_LEASE_MODES[cohort]}')"
            for cohort, connector, checkout, _index in _COHORTS
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.assignments_table} "
            "(cohort_id, service_name, resource_group, session_alias_prefix, traffic_weight, pool_size, connector_revision, checkout_revision, enabled, deployment_lane, session_binding_mode, session_lease_mode) VALUES "
            f"{assignment_values}",
            "seed set-autocommit runtime assignments",
        )
        rollout_values = ", ".join(
            f"('{cohort}', "
            f"'{self.initial_target_connector_revision if cohort == self.target_cohort else connector}', "
            f"'{self.initial_target_checkout_revision if cohort == self.target_cohort else checkout}', "
            f"'{self.initial_target_deployment_lane if cohort == self.target_cohort else _COHORT_STATES[cohort][0]}', "
            f"'{self.initial_target_session_binding_mode if cohort == self.target_cohort else _COHORT_STATES[cohort][1]}', "
            f"'{self.initial_target_session_lease_mode if cohort == self.target_cohort else _COHORT_LEASE_MODES[cohort]}', "
            "1, 1, 'applied', NOW())"
            for cohort, connector, checkout, _index in _COHORTS
        )
        execute_json_payload(
            env.execute_sql,
            f"CREATE TABLE {self.db}.{self.rollouts_table} ("
            "cohort_id VARCHAR(32) PRIMARY KEY, "
            "desired_connector_revision VARCHAR(32) NOT NULL, "
            "desired_checkout_revision VARCHAR(32) NOT NULL, "
            "desired_deployment_lane ENUM('stable', 'canary') NOT NULL, "
            "desired_session_binding_mode ENUM('steady', 'rebind') NOT NULL, "
            "desired_session_lease_mode ENUM('fixed', 'renew_on_checkout') NOT NULL, "
            "generation BIGINT NOT NULL, "
            "applied_generation BIGINT NOT NULL, "
            "rollout_state ENUM('pending', 'applying', 'applied') NOT NULL, "
            "last_reconcile_at DATETIME NULL"
            ")",
            "create set-autocommit runtime rollouts",
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.rollouts_table} "
            "(cohort_id, desired_connector_revision, desired_checkout_revision, desired_deployment_lane, "
            "desired_session_binding_mode, desired_session_lease_mode, generation, "
            "applied_generation, rollout_state, last_reconcile_at) VALUES "
            f"{rollout_values}",
            "seed set-autocommit runtime rollouts",
        )
        execute_json_payload(
            env.execute_sql,
            f"CREATE TABLE {self.db}.{self.events_table} ("
            "event_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, event_type VARCHAR(16) NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, payload VARCHAR(96) NOT NULL, created_at DATETIME NOT NULL, "
            "KEY idx_tenant_created (tenant_id, created_at), KEY idx_type_created (event_type, created_at)"
            ")",
            "create set-autocommit events table",
        )

    def _load_events(self, env) -> None:
        batch_size = 1000
        row_count = 50000
        for start in range(1, row_count + 1, batch_size):
            end = min(row_count, start + batch_size - 1)
            values = []
            for event_id in range(start, end + 1):
                event_type = ("create", "update", "charge", "close")[event_id % 4]
                amount = ((event_id * 7919) % 100000) / 100
                values.append(
                    f"({event_id}, {event_id % 64 + 1}, '{event_type}', {amount:.2f}, "
                    f"'admission-event-{event_id}', TIMESTAMPADD(SECOND, {event_id}, TIMESTAMP'2026-01-01 00:00:00'))"
                )
            execute_json_payload(
                env.execute_sql,
                f"INSERT INTO {self.db}.{self.events_table} "
                "(event_id, tenant_id, event_type, amount, payload, created_at) VALUES "
                + ", ".join(values),
                f"load set-autocommit events starting at {start}",
            )

    def _create_noise_tables(self, env) -> None:
        execute_json_payload(
            env.execute_sql,
            f"CREATE TABLE {self.db}.{self.orders_table} ("
            "order_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, amount DECIMAL(12,2) NOT NULL, "
            "status VARCHAR(16) NOT NULL, created_at DATETIME NOT NULL, KEY idx_order_tenant (tenant_id, created_at)"
            ")",
            "create set-autocommit order table",
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.orders_table} "
            "(order_id, tenant_id, amount, status, created_at) "
            f"SELECT event_id, tenant_id, amount, event_type, created_at FROM {self.db}.{self.events_table} WHERE event_id <= 12000",
            "load set-autocommit order table",
        )
        execute_json_payload(
            env.execute_sql,
            f"CREATE TABLE {self.db}.{self.inventory_table} ("
            "item_id BIGINT PRIMARY KEY, warehouse_id INT NOT NULL, available INT NOT NULL, "
            "updated_at DATETIME NOT NULL, KEY idx_warehouse (warehouse_id)"
            ")",
            "create set-autocommit inventory table",
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.inventory_table} "
            "(item_id, warehouse_id, available, updated_at) "
            f"SELECT event_id, MOD(tenant_id, 8) + 1, MOD(event_id, 100), created_at FROM {self.db}.{self.events_table} WHERE event_id <= 8000",
            "load set-autocommit inventory table",
        )

    def _create_resource_groups(self, env) -> None:
        if self._statement_summary_before is None:
            settings = execute_result_rows(
                env.execute_sql,
                "SHOW GLOBAL VARIABLES LIKE 'tidb_enable_stmt_summary'",
                "capture set-autocommit statement summary",
            )
            row = require_one_result_row(settings, "capture set-autocommit statement summary")
            self._statement_summary_before = str(row[1]).upper()
        execute_json_payload(
            env.execute_sql,
            "SET GLOBAL tidb_enable_stmt_summary = ON",
            "enable set-autocommit statement summary",
        )
        if self._resource_control_before is None:
            settings = execute_result_rows(
                env.execute_sql,
                "SHOW GLOBAL VARIABLES LIKE 'tidb_enable_resource_control'",
                "capture set-autocommit resource control",
            )
            row = require_one_result_row(settings, "capture set-autocommit resource control")
            self._resource_control_before = str(row[1]).upper()
        execute_json_payload(
            env.execute_sql,
            "SET GLOBAL tidb_enable_resource_control = ON",
            "enable set-autocommit resource control",
        )
        for resource_group in self.resource_groups:
            execute_json_payload(
                env.execute_sql,
                f"CREATE RESOURCE GROUP {resource_group} RU_PER_SEC = 1000 BURSTABLE=TRUE",
                f"create set-autocommit resource group {resource_group}",
            )
        self._resource_groups_created = True

    def _initialize_routers(self, env) -> None:
        if self._router_initialized:
            return
        env.initialize_connection_routers(self.router_config)
        for router_name in self.router_config:
            env.set_connection_router_policy(router_name, "round_robin")
        env.register_connection_router_invalidation(
            "set-autocommit-runtime-revisions",
            tables=(
                f"{self.db}.{self.assignments_table}",
                f"{self.db}.{self.connector_table}",
                f"{self.db}.{self.checkout_table}",
                f"{self.db}.{self.rollouts_table}",
                f"{self.db}.{self.revision_catalog_table}",
            ),
            routers=tuple(self.router_config),
        )
        self._router_invalidation_registered = True
        self._router_initialized = True

    def _reset_routers(self, env) -> None:
        if self._router_invalidation_registered:
            env.unregister_connection_router_invalidation("set-autocommit-runtime-revisions")
            self._router_invalidation_registered = False
        if self._router_initialized:
            env.reset_connection_routers()
            self._router_initialized = False

    @staticmethod
    def _clear_statement_summary(env) -> None:
        execute_json_payload(
            env.execute_sql,
            "SET GLOBAL tidb_enable_stmt_summary = OFF",
            "clear set-autocommit statement summary",
        )
        execute_json_payload(
            env.execute_sql,
            "SET GLOBAL tidb_enable_stmt_summary = ON",
            "restart set-autocommit statement summary",
        )

    def _wait_for_statement_summary(self, env, sql: str) -> dict:
        deadline = time.monotonic() + 30
        while True:
            summary = execute_json_payload(
                env.execute_sql,
                sql,
                "capture set-autocommit statement summary",
            )
            rows = summary["result"]
            business_groups = {
                str(row[1])
                for row in rows
                if len(row) >= 5
                and str(row[1]) in self.resource_groups
                and str(row[2]).casefold() == "select"
                and "admission_events" in str(row[4]).casefold()
            }
            autocommit_groups = {
                str(row[1])
                for row in rows
                if len(row) >= 5
                and str(row[4]).casefold() == "set `autocommit` = ?"
            }
            if (
                set(self.resource_groups) <= business_groups
                and (
                    {_RESOURCE_GROUPS["cohort-02"]}
                    | (
                        {_RESOURCE_GROUPS[self.target_cohort]}
                        if (
                            self.initial_target_deployment_lane == "canary"
                            and self.initial_target_session_lease_mode == "renew_on_checkout"
                        )
                        else set()
                    )
                )
                <= autocommit_groups
            ):
                return summary
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "set-autocommit statement summary did not expose the complete cohort contrast: "
                    f"business_groups={sorted(business_groups)!r}, "
                    f"autocommit_groups={sorted(autocommit_groups)!r}, row_count={len(rows)}"
                )
            time.sleep(0.5)

    def _verify_fault_state(self, env) -> None:
        counts = tuple(
            self._scalar(env, f"SELECT COUNT(*) FROM {self.db}.{table}", f"verify set-autocommit {table} rows")
            for table in (self.events_table, self.orders_table, self.inventory_table)
        )
        if counts != (50000, 12000, 8000):
            raise RuntimeError(
                "set-autocommit business row contract mismatch: "
                f"expected=(50000, 12000, 8000), observed={counts!r}"
            )
        assignments = execute_json_payload(
            env.execute_sql,
            f"SELECT cohort_id, connector_revision, checkout_revision, pool_size, enabled, "
            f"deployment_lane, session_binding_mode, session_lease_mode "
            f"FROM {self.db}.{self.assignments_table} ORDER BY cohort_id",
            "verify set-autocommit assignment state",
        )
        if len(assignments["result"]) != 4:
            raise RuntimeError(f"set-autocommit expected four assignments: assignments={assignments!r}")
        target = [row for row in assignments["result"] if row[0] == self.target_cohort]
        expected = [[
            self.target_cohort,
            self.initial_target_connector_revision,
            self.initial_target_checkout_revision,
            8,
            1,
            self.initial_target_deployment_lane,
            self.initial_target_session_binding_mode,
            self.initial_target_session_lease_mode,
        ]]
        if target != expected:
            raise RuntimeError(
                "set-autocommit target assignment does not match the configured live combination: "
                f"expected={expected!r}, observed={target!r}"
            )
        rollout = self._query_rollouts(env)
        target_rollout = [row for row in rollout["result"] if row[0] == self.target_cohort]
        expected_rollout = [[
            self.target_cohort,
            self.initial_target_connector_revision,
            self.initial_target_checkout_revision,
            self.initial_target_deployment_lane,
            self.initial_target_session_binding_mode,
            self.initial_target_session_lease_mode,
            1,
            1,
            "applied",
            target_rollout[0][8] if target_rollout else None,
        ]]
        if not target_rollout or target_rollout[0][:8] != expected_rollout[0][:8]:
            raise RuntimeError(
                "set-autocommit target desired rollout does not match the configured live combination: "
                f"expected_prefix={expected_rollout[0][:8]!r}, observed={target_rollout!r}"
            )

    @staticmethod
    def _scalar(env, sql: str, context: str) -> int:
        row = require_one_result_row(execute_result_rows(env.execute_sql, sql, context), context)
        if len(row) != 1:
            raise ValueError(f"{context} expected one scalar column: sql={sql!r}, row={row!r}")
        return int(row[0])

    @staticmethod
    def _integrity(env, sql: str, context: str) -> tuple[int, int, int]:
        return execute_integrity_tuple(env.execute_sql, sql, context)

    @staticmethod
    def _profile_rows(activity: dict) -> dict[str, dict]:
        snapshot = activity.get("snapshot")
        profiles = snapshot.get("profiles") if isinstance(snapshot, dict) else None
        if not isinstance(profiles, list):
            raise TypeError(f"set-autocommit workload activity snapshot profiles must be a list: activity={activity!r}")
        return {str(profile["fingerprint"]): profile for profile in profiles}
