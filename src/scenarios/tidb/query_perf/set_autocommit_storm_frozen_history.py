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
from src.scenarios.evaluation.tidb.query_perf.set_autocommit_storm_frozen_history import (
    TidbQueryPerfSetAutocommitStormFrozenHistoryEvaluatorCase,
    TidbQueryPerfSetAutocommitFocusedCohortEvaluatorCase,
)
from src.execution.history.records import HistoricalRecordSource
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)
from src.scenarios.tidb.common import validate_sql_identifier
from src.scenarios.workloads import SessionSetupBehavior, WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V8_1_0, tidb_runtime


_DB = "benchops_mf_ma03"
_EVENTS_TABLE = "mf_ma03_events"
_ORDERS_TABLE = "mf_ma03_order_facts"
_INVENTORY_TABLE = "mf_ma03_inventory_snapshot"
_ASSIGNMENTS_TABLE = "mf_ma03_runtime_assignments"
_CONNECTOR_TABLE = "mf_ma03_connector_revisions"
_CHECKOUT_TABLE = "mf_ma03_checkout_revisions"
_ROLLOUTS_TABLE = "mf_ma03_runtime_rollouts"
_REVISION_CATALOG_TABLE = "mf_ma03_runtime_revision_catalog"

_TARGET_COHORT = "cohort-d"
_RESOURCE_GROUPS = {
    "cohort-a": "rg_mf_set_autocommit_a",
    "cohort-b": "rg_mf_set_autocommit_b",
    "cohort-c": "rg_mf_set_autocommit_c",
    "cohort-d": "rg_mf_set_autocommit_d",
}
_SESSION_ALIASES = {
    "cohort-a": "mf_set_autocommit_orders_a",
    "cohort-b": "mf_set_autocommit_orders_b",
    "cohort-c": "mf_set_autocommit_orders_c",
    "cohort-d": "mf_set_autocommit_orders_d",
}
_ROUTERS = {cohort: f"router_{cohort.replace('-', '_')}" for cohort in _RESOURCE_GROUPS}

_SESSION_SETUP_STATEMENT = "SET autocommit=1"
_TRANSITION_CHECKOUT_INTERVAL = 16
_PER_CHECKOUT_RESET_COUNT = 512
_HISTORICAL_ROLLOUT_COHORT = "cohort-b"
_HISTORICAL_ROLLOUT_SECONDS = 6.0
_HISTORICAL_ROLLOUT_DELAY_SECONDS = 15.0
_CURRENT_INCIDENT_WINDOW_SECONDS = 2.0
_RECONCILE_INTERVAL_SECONDS = 1.0
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
    ("cohort-a", "r1", "h1", 0),
    ("cohort-b", "r2", "h1", 1),
    ("cohort-c", "r1", "h2", 0),
    ("cohort-d", "r2", "h2", 1),
)
_COHORT_STATES = {
    "cohort-a": ("stable", "steady"),
    "cohort-b": ("canary", "steady"),
    "cohort-c": ("stable", "rebind"),
    "cohort-d": ("canary", "rebind"),
}
_COHORT_LEASE_MODES = {
    "cohort-a": "fixed",
    "cohort-b": "fixed",
    "cohort-c": "renew_on_checkout",
    "cohort-d": "renew_on_checkout",
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
            "MF-set-autocommit session setup configuration must contain connector, checkout, lane, binding and lease values: "
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
            "MF-set-autocommit deployment lane is unsupported: "
            f"deployment_lane={deployment_lane!r}, configuration={configuration!r}"
        )
    if str(binding_mode).casefold() not in _SESSION_BINDING_MODES:
        raise ValueError(
            "MF-set-autocommit session binding mode is unsupported: "
            f"session_binding_mode={binding_mode!r}, configuration={configuration!r}"
        )
    if str(lease_mode).casefold() not in _SESSION_LEASE_MODES:
        raise ValueError(
            "MF-set-autocommit session lease mode is unsupported: "
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
        "MF-set-autocommit checkout revision has unsupported reset mode: "
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

_MF_SET_AUTOCOMMIT_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=tuple(
        profile
        for cohort_id in _COHORT_PROFILE_GROUPS
        for profile in _COHORT_PROFILE_GROUPS[cohort_id]
    ) + _NOISE_PROFILES,
    worker_count=8,
    seed=20260816,
    start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
    warmup_seconds=18,
)


_FROZEN_HISTORY_HISTORY = FrozenHistorySpec(
    schema_version=1,
    duration_seconds=12 * 60 * 60,
    normal_capture_seconds=240,
    fault_capture_seconds=150,
    base_step_seconds=30,
    overview_step_seconds=60,
    block_min_seconds=60,
    block_max_seconds=90,
    transition_seconds=60,
    target_age_seconds_range=(1800, 3600),
    required_metrics=("cpu", "qps", "query_latency", "active_connections"),
    # cAdvisor scrapes every 5s with a 4s timeout; under host load a 10s rate
    # window loses whole samples.  A 30s window tolerates isolated scrape
    # misses while the completeness validator still rejects real gaps.
    metric_rate_windows={"cpu": 30},
    record_sources=(
        HistoricalRecordSource.COMPONENT_LOG,
        HistoricalRecordSource.TOPSQL,
        HistoricalRecordSource.SLOW_QUERIES,
    ),
    decoys=(
        HistoryDecoySpec(
            decoy_id="business-peak",
            kind=DecoyKind.METRIC_ONLY,
            metric="qps",
            field="queries_per_second",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=180,
            amplitude_mad=2.0,
        ),
        HistoryDecoySpec(
            decoy_id="historical-rollout-b",
            kind=DecoyKind.METRIC_ONLY,
            metric="qps",
            field="queries_per_second",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=120,
            amplitude_mad=1.5,
        ),
        HistoryDecoySpec(
            decoy_id="reporting-cpu",
            kind=DecoyKind.METRIC_ONLY,
            metric="cpu",
            field="percent",
            target="tidb/tidb-0",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=120,
            amplitude_mad=1.5,
        ),
        HistoryDecoySpec(
            decoy_id="rebind-stable",
            kind=DecoyKind.METRIC_ONLY,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=120,
            amplitude_mad=1.5,
        ),
    ),
    max_points_per_series=7200,
    max_scalar_samples_per_response=12000,
    max_history_records_per_response=240,
)


_REFERENCE_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "timeline",
                "factor": "the historical window shows SET autocommit execution rate rising before TiDB endpoint CPU and target business tail latency while business QPS stays approximately flat",
                "entity": "the target historical window",
                "evidence": ["the aligned history metrics and records preserve the SET -> CPU -> latency order"],
            },
            {
                "type": "source",
                "factor": "TiDB SQL session front end is the main CPU source while slow business SQL, TiKV and PD are not the main bottleneck",
                "entity": "TiDB SQL front end",
                "evidence": ["TopSQL, slow query and node observations separate the SQL front end from TiKV and PD"],
            },
            {
                "type": "ratio",
                "factor": "SET autocommit is an abnormal session-state amplification item only for one cohort after normalizing by business requests; the same fingerprint in healthy cohorts is low",
                "entity": "cohort-d compared with three online siblings",
                "evidence": ["the per-cohort SET/business ratios isolate one abnormal resource group"],
            },
            {
                "type": "mapping",
                "factor": "CLUSTER_PROCESSLIST resource group and session alias map the abnormal statements to one deployment cohort and its application assignment",
                "entity": "CLUSTER_PROCESSLIST and runtime assignments",
                "evidence": ["resource group and session alias join the abnormal endpoint traffic to cohort-d"],
            },
            {
                "type": "exclusion",
                "factor": "the ended cohort-b rollout, fixed-lease connection surge, stable rebind and reporting CPU windows do not match the current target generation and causal time order",
                "entity": "historical decoy windows",
                "evidence": ["their state, record timestamps or statement fingerprints differ from the current target episode"],
            },
            {
                "type": "interaction",
                "factor": "connector, checkout and session lease revisions are correlated with the incident but are not sufficient causes; the live behavior must be explained together with deployment lane, session binding and session lease mode",
                "entity": "target runtime assignment and revision state",
                "evidence": ["the same connector and checkout families appear in healthy online combinations"],
            },
            {
                "type": "counterfactual",
                "factor": "the four online revision and runtime-state combinations provide healthy siblings; only canary with renew_on_checkout is abnormal while binding and checkout remain correlated competing states",
                "entity": "four online cohort combinations",
                "evidence": ["cohort-b is lane-only, cohort-c is lease-only and cohort-a is the stable/fixed control"],
            },
            {
                "type": "root_cause",
                "factor": "deployment_lane=canary and session_lease_mode=renew_on_checkout are both required for the persistent session-state reset storm; changing binding or a connector/checkout revision alone does not remove it",
                "entity": "cohort-d deployment state",
                "evidence": ["the target combination is the only online combination with the repeated no-op SET behavior"],
            },
            {
                "type": "control_plane",
                "factor": "runtime_assignments is current state and can drift from the desired runtime_rollouts generation; reconcile reapplies the desired connector, checkout, deployment lane, session binding and session lease state",
                "entity": "target runtime rollout and current assignment",
                "evidence": ["generation, applied_generation and rollout_state expose desired/current convergence"],
            },
        ]
    },
    "outcome": {
        "changes": ["changed only cohort-d desired session lease mode to fixed"],
        "verification": ["verified target rollout convergence, fresh workload recovery, business truth, capacity and protected siblings"],
    },
    "summary": "The frozen history and four-cohort counterfactual identify the canary plus renew-on-checkout interaction as the only causal session-state storm; a target desired rollout removes it without changing data or capacity.",
}


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfSetAutocommitStormFrozenHistoryForHistoryInvestigationScenarioCase(TiDBScenarioCase):
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


_MF_SET_AUTOCOMMIT_CASE = TidbQueryPerfSetAutocommitStormFrozenHistoryForHistoryInvestigationScenarioCase(
    case_id="autocommit_storm_history_investigation",
    reference_report=_REFERENCE_REPORT,
    case_no=0,
    evaluator=TidbQueryPerfSetAutocommitStormFrozenHistoryEvaluatorCase,
    title="Historical investigation of a misleading TiDB CPU and latency alert",
    alert=(
        "[CRITICAL] 订单服务的 p95/p99 延迟持续恶化，数据库集群出现 CPU 告警，"
        "但请求吞吐没有同幅增长。请使用当前状态和冻结历史窗口定位并修复主要原因，"
        "恢复接口和数据库状态。允许对经证据确认的应用运行时配置做有界修改；不得修改业务数据、"
        "健康 cohort、集群拓扑或 TiDB 全局参数，也不得通过重启、停流或缩小既有业务容量掩盖问题。"
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
        "fresh_window": {
            "set_business_ratio_max": 0.25,
            "profile_success_min": 0.95,
            "profile_qps_fraction_min": 0.65,
            "profile_p95_ms_max": 50,
            "profile_p99_ms_max": 150,
            "tidb_cpu_percent_max": 40,
            "cluster_p95_ms_max": 35,
            "cluster_p99_ms_max": 150,
        },
    },
    background_workload=_MF_SET_AUTOCOMMIT_BACKGROUND_WORKLOAD,
    frozen_history=_FROZEN_HISTORY_HISTORY,
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
        environmental_complexity=0.815104,
        reference_run_ids=(
            "tidb_mf-set-autocommit_frozen_history_reference_lease_pending",
            "tidb_mf-set-autocommit_frozen_history_reference_lane_pending",
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

_FOCUSED_COHORT_CASE = replace(
    _MF_SET_AUTOCOMMIT_CASE,
    case_id="set_autocommit_focused_cohort_history_investigation",
    case_no=1,
    evaluator=TidbQueryPerfSetAutocommitFocusedCohortEvaluatorCase,
    title="Focused historical investigation of a cohort-scoped TiDB session-state storm.",
    background_workload=replace(_MF_SET_AUTOCOMMIT_CASE.background_workload, worker_count=6),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.755102,
        reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
        protocol_version='difficulty-v2',
    ),
)


class TidbQueryPerfSetAutocommitStormFrozenHistoryScenario(TiDBScenario):
    scenario_id = "tidb_query_perf_set_autocommit_storm_frozen_history"
    description = "Investigate a misleading TiDB CPU alert through a frozen 12-hour cohort history."
    cases = (_MF_SET_AUTOCOMMIT_CASE, _FOCUSED_COHORT_CASE)

    def build_fault_plan(
        self,
        case: TidbQueryPerfSetAutocommitStormFrozenHistoryForHistoryInvestigationScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbQueryPerfSetAutocommitStormFrozenHistoryInjector,
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


class TidbQueryPerfSetAutocommitStormFrozenHistoryInjector(BaseFaultInjector):

    retain_workload_after_metric_history = True

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Keep the fault state active through the Agent phase."""
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
        self._statement_summary_settings_before = None
        self._resource_groups_created = False
        self._historical_rollout_pending = False
        self._historical_rollout_not_before = None
        self._frozen_history_environment_prepared = False

    def prepare_frozen_history_environment(self, context: FaultLifecycleContext) -> None:
        """Create a healthy fixture before the frozen-history normal capture."""
        if self._frozen_history_environment_prepared:
            raise RuntimeError("MF-set-autocommit frozen-history environment was already prepared")
        self._configure(context.config)
        env = context.env
        with env.metrics_hidden():
            self._create_schema(
                env,
                target_state=("r2", "h2", "stable", "steady", "fixed"),
            )
            self._load_events(env)
            self._create_noise_tables(env)
            self._create_resource_groups(env)
            self._initialize_routers(env)
            self._register_reconcile_hook(env)
            self._reconcile_control_plane(env, force=True)
            self._verify_bootstrap_state(env)
        self._frozen_history_environment_prepared = True

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        if not self._frozen_history_environment_prepared:
            raise RuntimeError(
                "MF-set-autocommit install requires the healthy frozen-history environment preparation"
            )
        self._set_desired_rollout(
            context.env,
            self.target_cohort,
            connector=self.initial_target_connector_revision,
            checkout=self.initial_target_checkout_revision,
            deployment_lane=self.initial_target_deployment_lane,
            session_binding_mode=self.initial_target_session_binding_mode,
            session_lease_mode=self.initial_target_session_lease_mode,
        )
        self._reconcile_control_plane(context.env, force=True)
        self._verify_fault_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        if not self._frozen_history_environment_prepared:
            raise RuntimeError(
                "MF-set-autocommit activate requires the healthy frozen-history environment preparation"
            )
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
            "capture MF-set-autocommit v3 workload activity",
        )
        profiles = self._profile_rows(activity)
        missing = [name for name in self.all_cohort_profile_names if name not in profiles]
        if missing:
            raise RuntimeError(
                "MF-set-autocommit v3 workload did not observe every cohort profile: "
                f"missing={missing!r}, observed={sorted(profiles)!r}"
            )
        inactive = {
            name: profiles[name]
            for name in self.all_cohort_profile_names
            if profiles[name]["calls"] <= 0
        }
        if inactive:
            raise RuntimeError(
                "MF-set-autocommit v3 cohort profiles did not execute during warmup: "
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
        statement_summary = self._wait_for_statement_summary(env, statement_summary_sql)
        set_rows = [
            row
            for row in statement_summary["result"]
            if len(row) >= 5 and "autocommit" in str(row[4]).casefold()
        ]
        if not set_rows:
            raise RuntimeError(
                "MF-set-autocommit v3 warmup produced no autocommit statement summary rows: "
                f"summary={statement_summary!r}"
            )

        processlist_sql = (
            "SELECT INSTANCE, ID, USER, RESOURCE_GROUP, SESSION_ALIAS, DB, STATE, INFO "
            "FROM information_schema.cluster_processlist "
            "WHERE SESSION_ALIAS <> '' ORDER BY INSTANCE, ID LIMIT 200"
        )
        processlist = execute_json_payload(env.execute_sql, processlist_sql, "capture MF-set-autocommit v3 processlist")
        observed_aliases = {str(row[4]) for row in processlist["result"] if len(row) >= 5}
        missing_aliases = sorted(
            set(self.session_aliases.values()) - observed_aliases
        )
        if missing_aliases:
            raise RuntimeError(
                "MF-set-autocommit v3 processlist did not expose all cohort aliases: "
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
        assignments = execute_json_payload(env.execute_sql, assignments_sql, "capture MF-set-autocommit v3 assignments")
        connectors = execute_json_payload(env.execute_sql, connector_sql, "capture MF-set-autocommit v3 connector revisions")
        checkouts = execute_json_payload(env.execute_sql, checkout_sql, "capture MF-set-autocommit v3 checkout revisions")
        business_payload = execute_json_payload(env.execute_sql, self.business_query, "capture MF-set-autocommit v3 business truth")
        evidence = {
            "mf-set-autocommit_cpu": require_success_payload(env.query_metrics("cpu"), "capture MF-set-autocommit v3 metric=cpu"),
            "mf-set-autocommit_qps": require_success_payload(env.query_metrics("qps"), "capture MF-set-autocommit v3 metric=qps"),
            "mf-set-autocommit_query_latency": require_success_payload(
                env.query_metrics("query_latency"), "capture MF-set-autocommit v3 metric=query_latency"
            ),
            "mf-set-autocommit_active_connections": require_success_payload(
                env.query_metrics("active_connections"), "capture MF-set-autocommit v3 metric=active_connections"
            ),
            "mf-set-autocommit_slow_queries": require_success_payload(
                env.observe_metric("slow_queries"), "capture MF-set-autocommit v3 metric=slow_queries"
            ),
            "mf-set-autocommit_topsql": require_success_payload(env.observe_metric("topsql"), "capture MF-set-autocommit v3 metric=topsql"),
            "mf-set-autocommit_node_health": require_success_payload(
                env.manage_cluster("service", "list"), "capture MF-set-autocommit v3 service health"
            ),
            "mf-set-autocommit_workload_activity": activity,
            "mf-set-autocommit_statement_summary": statement_summary,
            "mf-set-autocommit_statement_summary_sql": statement_summary_sql,
            "mf-set-autocommit_processlist": processlist,
            "mf-set-autocommit_processlist_sql": processlist_sql,
            "mf-set-autocommit_runtime_assignments": assignments,
            "mf-set-autocommit_runtime_assignments_sql": assignments_sql,
            "mf-set-autocommit_connector_revisions": connectors,
            "mf-set-autocommit_checkout_revisions": checkouts,
            "mf-set-autocommit_runtime_rollouts": self._query_rollouts(env),
            "mf-set-autocommit_revision_catalog": self._query_revision_catalog(env),
            "business_result_truth": capture_query_result_truth(business_payload, ordered=True),
            "mf-set-autocommit_event_integrity": self._integrity(env, self.event_integrity_sql, "MF-set-autocommit v3 event integrity"),
            "mf-set-autocommit_orders_integrity": self._integrity(env, self.orders_integrity_sql, "MF-set-autocommit v3 order integrity"),
            "mf-set-autocommit_inventory_integrity": self._integrity(
                env, self.inventory_integrity_sql, "MF-set-autocommit v3 inventory integrity"
            ),
        }
        self._historical_rollout_pending = True
        self._historical_rollout_not_before = time.monotonic() + _HISTORICAL_ROLLOUT_DELAY_SECONDS
        return evidence

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
            raise RuntimeError("MF-set-autocommit reconcile workload runner is already attached")
        self._workload_runner = runner
        runner.set_before_profile_hook(self._before_workload_profile)

    def _before_workload_profile(self) -> None:
        if (
            self._historical_rollout_pending
            and self._historical_rollout_not_before is not None
            and time.monotonic() >= self._historical_rollout_not_before
        ):
            with self._reconcile_lock:
                if (
                    self._historical_rollout_pending
                    and self._historical_rollout_not_before is not None
                    and time.monotonic() >= self._historical_rollout_not_before
                ):
                    self._historical_rollout_pending = False
                    self._run_historical_rollout_window(self._reconcile_env)
        if self._reconcile_hook_registered:
            generation = self._reconcile_env.workload_connection_invalidation_generation()
            self._reconcile_control_plane(
                self._reconcile_env,
                force=generation != self._last_connection_invalidation_generation,
            )

    def _register_reconcile_hook(self, env) -> None:
        if self._reconcile_hook_registered and self._reconcile_env is not env:
            raise RuntimeError("MF-set-autocommit reconcile hook is attached to a different environment")
        self._reconcile_env = env
        self._reconcile_hook_registered = True

    def _clear_reconcile_hook(self, env) -> None:
        if self._reconcile_hook_registered and self._reconcile_env is not env:
            raise RuntimeError("MF-set-autocommit reconcile hook environment mismatch")
        self._reconcile_hook_registered = False
        self._reconcile_env = None
        self._workload_runner = None
        self._historical_rollout_pending = False
        self._historical_rollout_not_before = None

    def _control_query(self, env, sql: str, context: str) -> dict:
        executor = getattr(env, "execute_internal_sql", None)
        if executor is None:
            raise RuntimeError(
                "MF-set-autocommit control-plane reconcile requires TiDBEnv.execute_internal_sql: "
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
            "query MF-set-autocommit runtime rollouts",
        )

    def _query_revision_catalog(self, env) -> dict:
        return self._control_query(
            env,
            f"SELECT revision_id, revision_kind, scope, owner_cohort_id, use_local_session_state, "
            f"elide_set_autocommits, cache_server_configuration, always_send_set_isolation, "
            f"reset_mode, reset_count, validation_mode, transaction_boundary_mode, session_lease_mode "
            f"FROM {self.db}.{self.revision_catalog_table} ORDER BY revision_id",
            "query MF-set-autocommit revision catalog",
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
            raise ValueError(f"MF-set-autocommit desired rollout update requires a revision: cohort_id={cohort_id!r}")
        assignments.extend(("generation=generation+1", "rollout_state='pending'"))
        execute_json_payload(
            env.execute_sql,
            f"UPDATE {self.db}.{self.rollouts_table} SET {', '.join(assignments)} "
            f"WHERE cohort_id='{cohort_id}'",
            f"update MF-set-autocommit desired rollout for {cohort_id}",
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
                "query MF-set-autocommit current assignments for reconcile",
            )["result"]
            catalog = self._query_revision_catalog(env)["result"]
            rollout_by_id = {str(row[0]): row for row in rollouts}
            assignment_by_id = {str(row[0]): row for row in assignments}
            if set(rollout_by_id) != set(self.cohort_ids):
                raise RuntimeError(
                    "MF-set-autocommit rollout cohort contract mismatch: "
                    f"expected={sorted(self.cohort_ids)!r}, observed={sorted(rollout_by_id)!r}"
                )
            if set(assignment_by_id) != set(self.cohort_ids):
                raise RuntimeError(
                    "MF-set-autocommit assignment cohort contract mismatch during reconcile: "
                    f"expected={sorted(self.cohort_ids)!r}, observed={sorted(assignment_by_id)!r}"
                )
            connectors = {
                str(row[0]): row
                for row in execute_json_payload(
                    env.execute_internal_sql,
                    f"SELECT revision_id, use_local_session_state, elide_set_autocommits, "
                    f"cache_server_configuration, always_send_set_isolation FROM {self.db}.{self.connector_table} "
                    "ORDER BY revision_id",
                    "query MF-set-autocommit connector revisions for reconcile",
                )["result"]
            }
            checkouts = {
                str(row[0]): row
                for row in execute_json_payload(
                    env.execute_internal_sql,
                    f"SELECT revision_id, reset_mode, reset_count, validation_mode, transaction_boundary_mode "
                    f"FROM {self.db}.{self.checkout_table} ORDER BY revision_id",
                    "query MF-set-autocommit checkout revisions for reconcile",
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
                            "MF-set-autocommit revision catalog references a missing connector revision: "
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
                            "MF-set-autocommit revision catalog references a missing checkout revision: "
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
                            "MF-set-autocommit revision catalog has unsupported session lease mode: "
                            f"revision_id={revision_id!r}, session_lease_mode={lease_mode!r}"
                        )
                else:
                    raise RuntimeError(
                        "MF-set-autocommit revision catalog has an unsupported revision kind: "
                        f"revision_id={revision_id!r}, revision_kind={row[1]!r}"
                    )
            for statement in revision_drift:
                self._control_query(env, statement, "restore MF-set-autocommit shared revision from catalog")
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
                        "MF-set-autocommit rollout has unsupported deployment state: "
                        f"cohort_id={cohort_id!r}, lane={desired_lane!r}, binding={desired_binding!r}, "
                        f"lease={desired_lease!r}"
                    )
                if desired_connector not in connectors or desired_checkout not in checkouts:
                    raise RuntimeError(
                        "MF-set-autocommit rollout references an unknown revision: "
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
                        "MF-set-autocommit rollout references an unregistered session lease mode: "
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
                self._control_query(env, statement, "apply MF-set-autocommit desired rollout assignment")
            for statement in rollout_updates:
                self._control_query(env, statement, "mark MF-set-autocommit rollout applied")
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
        executor = getattr(context.env, "execute_internal_sql", None)
        if executor is None:
            raise RuntimeError(
                "MF-set-autocommit recovery requires TiDBEnv.execute_internal_sql: "
                f"environment={type(context.env).__name__!r}"
            )
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
                executor,
                f"DROP TABLE IF EXISTS {self.db}.{table}",
                f"drop MF-set-autocommit v3 table {self.db}.{table}",
            )
        if self._resource_groups_created:
            for resource_group in self.resource_groups:
                execute_json_payload(
                    executor,
                    f"DROP RESOURCE GROUP {resource_group}",
                    f"drop MF-set-autocommit v3 resource group {resource_group}",
                )
            self._resource_groups_created = False
        if self._resource_control_before is not None:
            execute_json_payload(
                executor,
                f"SET GLOBAL tidb_enable_resource_control = {self._resource_control_before}",
                "restore MF-set-autocommit v3 resource control",
            )
        if self._statement_summary_settings_before is not None:
            for variable, value in self._statement_summary_settings_before.items():
                execute_json_payload(
                    executor,
                    f"SET GLOBAL {variable} = {value}",
                    f"restore MF-set-autocommit v3 {variable}",
                )
            self._statement_summary_settings_before = None
        self._frozen_history_environment_prepared = False

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

    def _create_schema(
        self,
        env,
        *,
        target_state: tuple[str, str, str, str, str],
    ) -> None:
        target_connector, target_checkout, target_lane, target_binding, target_lease = target_state
        execute_json_payload(env.execute_sql, f"CREATE DATABASE IF NOT EXISTS {self.db}", "create MF-set-autocommit v3 database")
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
                f"clear MF-set-autocommit v3 table {self.db}.{table}",
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
            "create MF-set-autocommit v3 connector revisions",
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
            "create MF-set-autocommit v3 checkout revisions",
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
            "create MF-set-autocommit v3 revision catalog",
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
            "create MF-set-autocommit v3 runtime assignments",
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.connector_table} "
            "(revision_id, use_local_session_state, elide_set_autocommits, cache_server_configuration, always_send_set_isolation) VALUES "
            "('r1', 1, 1, 1, 0), ('r2', 0, 0, 1, 0)",
            "seed MF-set-autocommit v3 connector revisions",
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.checkout_table} "
            "(revision_id, reset_mode, reset_count, validation_mode, transaction_boundary_mode) VALUES "
            "('h1', 'transition', 1, 'ping', 'request'), "
            f"('h2', 'per_checkout', {_PER_CHECKOUT_RESET_COUNT}, 'ping', 'request')",
            "seed MF-set-autocommit v3 checkout revisions",
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
            "seed MF-set-autocommit v3 revision catalog",
        )
        assignment_values = ", ".join(
            f"('{cohort}', 'order-maintenance', '{_RESOURCE_GROUPS[cohort]}', '{_SESSION_ALIASES[cohort]}', 25, 8, "
            f"'{target_connector if cohort == self.target_cohort else connector}', "
            f"'{target_checkout if cohort == self.target_cohort else checkout}', 1, "
            f"'{target_lane if cohort == self.target_cohort else _COHORT_STATES[cohort][0]}', "
            f"'{target_binding if cohort == self.target_cohort else _COHORT_STATES[cohort][1]}', "
            f"'{target_lease if cohort == self.target_cohort else _COHORT_LEASE_MODES[cohort]}')"
            for cohort, connector, checkout, _index in _COHORTS
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.assignments_table} "
            "(cohort_id, service_name, resource_group, session_alias_prefix, traffic_weight, pool_size, connector_revision, checkout_revision, enabled, deployment_lane, session_binding_mode, session_lease_mode) VALUES "
            f"{assignment_values}",
            "seed MF-set-autocommit v3 runtime assignments",
        )
        rollout_values = ", ".join(
            f"('{cohort}', "
            f"'{target_connector if cohort == self.target_cohort else connector}', "
            f"'{target_checkout if cohort == self.target_cohort else checkout}', "
            f"'{target_lane if cohort == self.target_cohort else _COHORT_STATES[cohort][0]}', "
            f"'{target_binding if cohort == self.target_cohort else _COHORT_STATES[cohort][1]}', "
            f"'{target_lease if cohort == self.target_cohort else _COHORT_LEASE_MODES[cohort]}', "
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
            "create MF-set-autocommit v3 runtime rollouts",
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.rollouts_table} "
            "(cohort_id, desired_connector_revision, desired_checkout_revision, desired_deployment_lane, "
            "desired_session_binding_mode, desired_session_lease_mode, generation, "
            "applied_generation, rollout_state, last_reconcile_at) VALUES "
            f"{rollout_values}",
            "seed MF-set-autocommit v3 runtime rollouts",
        )
        execute_json_payload(
            env.execute_sql,
            f"CREATE TABLE {self.db}.{self.events_table} ("
            "event_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, event_type VARCHAR(16) NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, payload VARCHAR(96) NOT NULL, created_at DATETIME NOT NULL, "
            "KEY idx_tenant_created (tenant_id, created_at), KEY idx_type_created (event_type, created_at)"
            ")",
            "create MF-set-autocommit v3 events table",
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
                f"load MF-set-autocommit v3 events starting at {start}",
            )

    def _create_noise_tables(self, env) -> None:
        execute_json_payload(
            env.execute_sql,
            f"CREATE TABLE {self.db}.{self.orders_table} ("
            "order_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, amount DECIMAL(12,2) NOT NULL, "
            "status VARCHAR(16) NOT NULL, created_at DATETIME NOT NULL, KEY idx_order_tenant (tenant_id, created_at)"
            ")",
            "create MF-set-autocommit v3 order table",
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.orders_table} "
            "(order_id, tenant_id, amount, status, created_at) "
            f"SELECT event_id, tenant_id, amount, event_type, created_at FROM {self.db}.{self.events_table} WHERE event_id <= 12000",
            "load MF-set-autocommit v3 order table",
        )
        execute_json_payload(
            env.execute_sql,
            f"CREATE TABLE {self.db}.{self.inventory_table} ("
            "item_id BIGINT PRIMARY KEY, warehouse_id INT NOT NULL, available INT NOT NULL, "
            "updated_at DATETIME NOT NULL, KEY idx_warehouse (warehouse_id)"
            ")",
            "create MF-set-autocommit v3 inventory table",
        )
        execute_json_payload(
            env.execute_sql,
            f"INSERT INTO {self.db}.{self.inventory_table} "
            "(item_id, warehouse_id, available, updated_at) "
            f"SELECT event_id, MOD(tenant_id, 8) + 1, MOD(event_id, 100), created_at FROM {self.db}.{self.events_table} WHERE event_id <= 8000",
            "load MF-set-autocommit v3 inventory table",
        )

    def _create_resource_groups(self, env) -> None:
        if self._statement_summary_settings_before is None:
            self._statement_summary_settings_before = {}
            for variable in (
                "tidb_enable_stmt_summary",
                "tidb_stmt_summary_refresh_interval",
                "tidb_stmt_summary_history_size",
                "tidb_stmt_summary_max_stmt_count",
            ):
                settings = execute_result_rows(
                    env.execute_sql,
                    f"SHOW GLOBAL VARIABLES LIKE '{variable}'",
                    f"capture MF-set-autocommit v3 {variable}",
                )
                row = require_one_result_row(settings, f"capture MF-set-autocommit v3 {variable}")
                self._statement_summary_settings_before[variable] = str(row[1])
        execute_json_payload(
            env.execute_sql,
            "SET GLOBAL tidb_enable_stmt_summary = ON",
            "enable MF-set-autocommit v3 statement summary",
        )
        if self._resource_control_before is None:
            settings = execute_result_rows(
                env.execute_sql,
                "SHOW GLOBAL VARIABLES LIKE 'tidb_enable_resource_control'",
                "capture MF-set-autocommit v3 resource control",
            )
            row = require_one_result_row(settings, "capture MF-set-autocommit v3 resource control")
            self._resource_control_before = str(row[1]).upper()
        execute_json_payload(
            env.execute_sql,
            "SET GLOBAL tidb_enable_resource_control = ON",
            "enable MF-set-autocommit v3 resource control",
        )
        for resource_group in self.resource_groups:
            execute_json_payload(
                env.execute_sql,
                f"CREATE RESOURCE GROUP {resource_group} RU_PER_SEC = 1000 BURSTABLE=TRUE",
                f"create MF-set-autocommit v3 resource group {resource_group}",
            )
        self._resource_groups_created = True

    def _initialize_routers(self, env) -> None:
        if self._router_initialized:
            return
        env.initialize_connection_routers(self.router_config)
        for router_name in self.router_config:
            env.set_connection_router_policy(router_name, "round_robin")
        env.register_connection_router_invalidation(
            "mf-set-autocommit_runtime_revisions",
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
            env.unregister_connection_router_invalidation("mf-set-autocommit_runtime_revisions")
            self._router_invalidation_registered = False
        if self._router_initialized:
            env.reset_connection_routers()
            self._router_initialized = False

    @staticmethod
    def _clear_statement_summary(env) -> None:
        execute_json_payload(
            env.execute_sql,
            "SET GLOBAL tidb_enable_stmt_summary = OFF",
            "clear MF-set-autocommit v3 statement summary",
        )
        execute_json_payload(
            env.execute_sql,
            "SET GLOBAL tidb_enable_stmt_summary = ON",
            "restart MF-set-autocommit v3 statement summary",
        )

    def _wait_for_statement_summary(self, env, sql: str) -> dict:
        deadline = time.monotonic() + 30
        while True:
            summary = execute_json_payload(
                env.execute_sql,
                sql,
                "capture MF-set-autocommit v3 statement summary",
            )
            rows = summary["result"]
            business_groups = {
                str(row[1])
                for row in rows
                if len(row) >= 5
                and str(row[1]) in self.resource_groups
                and str(row[2]).casefold() == "select"
                and self.events_table.casefold() in str(row[4]).casefold()
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
                    {_RESOURCE_GROUPS["cohort-b"]}
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
                    "MF-set-autocommit v3 statement summary did not expose the complete cohort contrast: "
                    f"business_groups={sorted(business_groups)!r}, "
                    f"autocommit_groups={sorted(autocommit_groups)!r}, row_count={len(rows)}"
                )
            time.sleep(0.5)

    def _verify_bootstrap_state(self, env) -> None:
        assignments = execute_json_payload(
            env.execute_sql,
            f"SELECT cohort_id, connector_revision, checkout_revision, pool_size, enabled, "
            f"deployment_lane, session_binding_mode, session_lease_mode "
            f"FROM {self.db}.{self.assignments_table} ORDER BY cohort_id",
            "verify MF-set-autocommit v3 healthy frozen-history bootstrap",
        )
        target = [row for row in assignments["result"] if row[0] == self.target_cohort]
        expected = [[self.target_cohort, "r2", "h2", 8, 1, "stable", "steady", "fixed"]]
        if target != expected:
            raise RuntimeError(
                "MF-set-autocommit v3 healthy frozen-history bootstrap has the wrong target state: "
                f"expected={expected!r}, observed={target!r}"
            )

    def _verify_fault_state(self, env) -> None:
        counts = tuple(
            self._scalar(env, f"SELECT COUNT(*) FROM {self.db}.{table}", f"verify MF-set-autocommit v3 {table} rows")
            for table in (self.events_table, self.orders_table, self.inventory_table)
        )
        if counts != (50000, 12000, 8000):
            raise RuntimeError(
                "MF-set-autocommit v3 business row contract mismatch: "
                f"expected=(50000, 12000, 8000), observed={counts!r}"
            )
        assignments = execute_json_payload(
            env.execute_sql,
            f"SELECT cohort_id, connector_revision, checkout_revision, pool_size, enabled, "
            f"deployment_lane, session_binding_mode, session_lease_mode "
            f"FROM {self.db}.{self.assignments_table} ORDER BY cohort_id",
            "verify MF-set-autocommit v3 assignment state",
        )
        if len(assignments["result"]) != 4:
            raise RuntimeError(f"MF-set-autocommit v3 expected four assignments: assignments={assignments!r}")
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
                "MF-set-autocommit v3 target assignment does not match the configured live combination: "
                f"expected={expected!r}, observed={target!r}"
            )
        rollout = self._query_rollouts(env)
        target_rollout = [row for row in rollout["result"] if row[0] == self.target_cohort]
        expected_rollout_prefix = (
            self.target_cohort,
            self.initial_target_connector_revision,
            self.initial_target_checkout_revision,
            self.initial_target_deployment_lane,
            self.initial_target_session_binding_mode,
            self.initial_target_session_lease_mode,
        )
        if (
            not target_rollout
            or tuple(target_rollout[0][:6]) != expected_rollout_prefix
            or int(target_rollout[0][6]) != int(target_rollout[0][7])
            or str(target_rollout[0][8]).casefold() != "applied"
        ):
            raise RuntimeError(
                "MF-set-autocommit v4 target desired rollout does not match the configured live combination: "
                f"expected_prefix={expected_rollout_prefix!r}, observed={target_rollout!r}"
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
            raise TypeError(f"MF-set-autocommit v3 workload activity snapshot profiles must be a list: activity={activity!r}")
        return {str(profile["fingerprint"]): profile for profile in profiles}
