"""K09 TiDB DR Auto-Sync planned and unplanned failover cases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.database.sql import require_success_payload
from src.scenarios.evaluation.protocol import structured_reference_report
from src.scenarios.evaluation.tidb.business_change.dr_auto_sync_failover import (
    TidbBusinessChangeDrAutoSyncPlannedFailoverEvaluatorCase,
    TidbBusinessChangeDrAutoSyncUnplannedFailoverEvaluatorCase,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.workloads import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    WorkloadProfile,
)

from ...base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from ..runtime import TIDB_V8_1_0, tidb_runtime


def _k09_workload() -> BackgroundWorkloadSpec:
    return BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="ledger_commit_writer",
                sql=(
                    "INSERT INTO k09_dr.ledger_markers "
                    "(marker_id, amount_cents, payload, commit_tso, origin) VALUES "
                    "(UUID(), FLOOR(100 + RAND() * 9000), 'router-commit', TIDB_CURRENT_TSO(), 'business-writer')"
                ),
                qps=1.1,
                tier="BUSINESS_WRITE",
                commit=True,
                application_name="ledger-writer",
                connection_pool="k09-business-router",
            ),
            WorkloadProfile(
                name="ledger_truth_probe",
                sql=(
                    "SELECT COUNT(*), COALESCE(SUM(amount_cents), 0), "
                    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', marker_id, amount_cents, payload, commit_tso, origin))), 0) "
                    "FROM k09_dr.ledger_markers"
                ),
                qps=0.8,
                tier="BUSINESS_READ",
                application_name="ledger-reconciliation",
                connection_pool="k09-business-router",
            ),
            WorkloadProfile(
                name="region_replication_probe",
                sql=(
                    "SELECT DB_NAME, TABLE_NAME, REPLICATIONSTATUS_STATE, COUNT(*) "
                    "FROM information_schema.TIKV_REGION_STATUS "
                    "WHERE DB_NAME = 'k09_dr' AND TABLE_NAME = 'ledger_markers' "
                    "GROUP BY DB_NAME, TABLE_NAME, REPLICATIONSTATUS_STATE"
                ),
                qps=0.55,
                tier="CONTROL_READ",
                application_name="dr-observer",
                connection_pool="k09-business-router",
            ),
            WorkloadProfile(
                name="cluster_store_inventory_decoy",
                sql=(
                    "SELECT TYPE, INSTANCE, STATUS_ADDRESS "
                    "FROM information_schema.cluster_info "
                    "WHERE TYPE IN ('tikv', 'pd') ORDER BY TYPE, INSTANCE"
                ),
                qps=0.45,
                tier="DECOY_READ",
                application_name="cluster-inventory",
                connection_pool="k09-business-router",
            ),
            WorkloadProfile(
                name="schema_inventory_decoy",
                sql=(
                    "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE "
                    "FROM information_schema.tables "
                    "WHERE TABLE_SCHEMA IN ('k09_dr', 'mysql') "
                    "ORDER BY TABLE_SCHEMA, TABLE_NAME LIMIT 24"
                ),
                qps=0.4,
                tier="DECOY_READ",
                application_name="schema-inventory",
                connection_pool="k09-business-router",
            ),
        ),
        worker_count=5,
        seed=0xA09,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=4.0,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class K09KnowledgeDecisionHop:
    knowledge_question: str
    expected_concept: str
    version_scope: str
    required_environment_binding: str
    decision_changed: str
    counterfactual: str
    allowed_source_scope: tuple[str, ...]
    visible_evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeDrAutoSyncFailoverCase(TiDBScenarioCase):
    database: str
    table: str
    canary_table: str
    handoff_table: str
    zone_label: str
    primary_zone: str
    dr_zone: str
    primary_endpoint: str
    dr_endpoint: str
    primary_tikv_targets: tuple[str, ...]
    primary_store_count: int
    dr_voter_count: int
    dr_learner_count: int
    total_dr_store_count: int
    wait_store_timeout: str
    wait_recover_timeout: str
    failover_mode: str
    knowledge_hops: tuple[K09KnowledgeDecisionHop, ...]
    reference_path: tuple[str, ...]
    reference_tool_counts: tuple[tuple[str, int, int], ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeDrAutoSyncForPlannedFailoverScenarioCase(
    TidbBusinessChangeDrAutoSyncFailoverCase
):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeDrAutoSyncForUnplannedFailoverScenarioCase(
    TidbBusinessChangeDrAutoSyncFailoverCase
):
    pass


_COMMON_RUNTIME = tidb_runtime(
    release=TIDB_V8_1_0,
    pd_count=3,
    tikv_count=6,
    tidb_count=2,
    sql_timeout_seconds=120,
    tikv_store_zones=("primary", "primary", "primary", "dr", "dr", "dr"),
    pd_location_labels=("zone",),
    tikv_memory_mb=2048,
    tidb_memory_mb=2048,
    readiness_timeout_seconds=900,
    pd_cpu_limit=4.0,
)


_PLANNED_KNOWLEDGE_HOPS = (
    K09KnowledgeDecisionHop(
        knowledge_question="In TiDB 8.1, how do DR Auto-Sync state, Region replication state, and PD leadership differ?",
        expected_concept="sync, async, and sync-recover describe the PD-controlled replication state machine; Region replication evidence and PD Leader/TSO observations are separate.",
        version_scope="TiDB 8.1 self-managed PD/TiKV DR Auto-Sync deployment",
        required_environment_binding="Current replication-mode status, Region status rows for the business table, PD Leader, and current endpoint routing.",
        decision_changed="Whether a planned role exchange is actually synchronized and ready to submit or accept.",
        counterfactual="A PD Leader change or equal TSO strings can look like a completed failover without proving Region convergence.",
        allowed_source_scope=("self_managed", "shared"),
        visible_evidence=("search_knowledge", "manage_cluster:dr_replication:get", "execute_sql:TIKV_REGION_STATUS"),
    ),
    K09KnowledgeDecisionHop(
        knowledge_question="How do TiDB 8.1 Placement Rules distinguish voters and learners during a dual-domain role exchange, and what must be fenced first?",
        expected_concept="Placement role/count/label constraints must be read from the rule bundle; a learner is not a synchronous voter and the old writer must be drained/fenced before exchange.",
        version_scope="TiDB 8.1 self-managed Placement Rules and business router",
        required_environment_binding="Current Store labels and states, current rule bundle, router policy, draining endpoint, and active connections.",
        decision_changed="Which role-exchange preconditions are satisfied and which endpoint is protected from split-brain writes.",
        counterfactual="Counting every DR Store as a voter or only changing the route can make an unsafe exchange appear complete.",
        allowed_source_scope=("self_managed", "shared"),
        visible_evidence=("search_knowledge", "manage_cluster:dr_replication:topology", "manage_cluster:router", "manage_cluster:dr_replication:fence_get"),
    ),
    K09KnowledgeDecisionHop(
        knowledge_question="What proves that a planned DR Auto-Sync exchange is complete rather than merely accepted?",
        expected_concept="The request must reach terminal placement/Region convergence, then the endpoint and business canary/marker truth must be verified separately.",
        version_scope="TiDB 8.1 self-managed DR Auto-Sync control plane",
        required_environment_binding="Transition response, terminal wait response, final Store/placement/Region state, router fence, and bounded endpoint write/read-back.",
        decision_changed="Whether to admit new DR writes and submit the final report.",
        counterfactual="An accepted request, a live SQL connection, or a liveness probe is weaker than terminal convergence plus business validation.",
        allowed_source_scope=("self_managed", "shared"),
        visible_evidence=("search_knowledge", "manage_cluster:dr_replication:wait", "execute_sql:business_truth", "execute_sql:canary"),
    ),
)


_UNPLANNED_KNOWLEDGE_HOPS = (
    K09KnowledgeDecisionHop(
        knowledge_question="What does TiDB 8.1 Online Unsafe Recovery accept, and how must the complete failed Store scope be derived?",
        expected_concept="The request is asynchronous and lossy, requires every unrecoverable Store but no connected healthy Store, and must be bound to current PD/Region evidence.",
        version_scope="TiDB 8.1 self-managed PD Online Unsafe Recovery",
        required_environment_binding="Current Store IDs/states/labels, affected Region peers, stopped endpoint, and the complete failed primary scope.",
        decision_changed="The failed_store_ids submitted to the recovery request and whether the request is safe to submit.",
        counterfactual="The first Store named by an error, a learner, or an arbitrary healthy Store can look like the recovery set without peer-level binding.",
        allowed_source_scope=("self_managed", "shared"),
        visible_evidence=("search_knowledge", "manage_cluster:dr_replication:topology", "manage_cluster:service:list", "execute_sql:Region peers"),
    ),
    K09KnowledgeDecisionHop(
        knowledge_question="How do accepted, running, finished, failed, and Tombstone states differ for Online Unsafe Recovery?",
        expected_concept="A successful request only registers a background task; terminal finished state, settled Regions, and Tombstone failed Stores are required, while terminal failed is failure and failed Stores must not be restarted.",
        version_scope="TiDB 8.1 self-managed PD/TiKV Online Unsafe Recovery",
        required_environment_binding="Raw transition response, progress polling output, Store state lookup, placement/Region convergence, and service state.",
        decision_changed="Whether to continue waiting, reject the recovery, or proceed to bounded post-recovery validation.",
        counterfactual="Treating Success/accepted, readable SQL, or a stopped process as terminal can reopen a partially recovered cluster.",
        allowed_source_scope=("self_managed", "shared"),
        visible_evidence=("search_knowledge", "manage_cluster:dr_replication:transition", "manage_cluster:dr_replication:wait", "manage_cluster:service:list"),
    ),
    K09KnowledgeDecisionHop(
        knowledge_question="What is the TiDB 8.1 business admission and RPO boundary after an unsafe failover?",
        expected_concept="TSO equality is not an RPO proof; bind the sealed acknowledged marker boundary to the surviving endpoint and fence generation, then perform a separate bounded canary and ADMIN CHECK TABLE.",
        version_scope="TiDB 8.1 self-managed DR Auto-Sync with application failover admission",
        required_environment_binding="Sealed pre-outage business truth, current router fence generation, surviving endpoint, schema-visible handoff record, canary read-back, and table check.",
        decision_changed="Whether the surviving endpoint may receive new business writes and what evidence belongs in the handoff receipt.",
        counterfactual="A live endpoint, unchanged full-table aggregate, equal TSO text, or an accepted recovery request can be mistaken for an acknowledged-boundary proof.",
        allowed_source_scope=("self_managed", "shared"),
        visible_evidence=("search_knowledge", "manage_cluster:dr_replication:fence_get", "execute_sql:sealed_business_truth", "execute_sql:handoff", "execute_sql:ADMIN CHECK TABLE"),
    ),
)


_PLANNED_CASE = TidbBusinessChangeDrAutoSyncForPlannedFailoverScenarioCase(
    case_id="planned_dual_dc_failover",
    case_no=0,
    evaluator=TidbBusinessChangeDrAutoSyncPlannedFailoverEvaluatorCase,
    title="Perform a planned K09 dual-AZ DR Auto-Sync role exchange without losing ledger markers.",
    alert=(
        "K09 计划内灾备切换：当前业务写入口位于 primary，DR Auto-Sync 双中心集群正在承载 ledger 写入。"
        "请在业务停写/排空和产品同步条件满足后，把业务写入口有序切到 DR；旧 primary 只能保留为只读/standby，"
        "新入口必须可写，且必须用公开的 marker、checksum、Region replication status 和 endpoint fence 证据闭环。"
        "不要只切 PD Leader、不要把 TSO 字符串相等当作完成，也不要修改 ledger truth。"
    ),
    initial_state={
        "replication_mode": "dr-auto-sync",
        "primary_zone": "primary",
        "dr_zone": "dr",
        "business_route": "primary",
        "region_replication": "sync",
    },
    expected_target={
        "replication_mode": "dr-auto-sync",
        "primary_zone": "dr",
        "old_primary_route": "drained",
        "new_endpoint": "writable",
        "business_truth": "seed markers preserved",
    },
    background_workload=_k09_workload(),
    reference_report=structured_reference_report(
        case_id="planned_dual_dc_failover",
        factors=("DR Auto-Sync planned failover requires router fencing, sync confirmation, and placement role exchange",),
        changes=(
            "distributed the business router and drained the primary endpoint",
            "confirmed DR Auto-Sync sync state and swapped the placement primary/DR labels",
            "waited for terminal placement/Region convergence before accepting DR writes",
        ),
        verification=(
            "old primary endpoint is drained while the DR endpoint remains live",
            "seed marker count, sum, and CRC are unchanged and new endpoint writes are observed",
            "TIKV_REGION_STATUS reports documented replication states",
        ),
        summary="The reference path performs a fenced, synchronized planned DR Auto-Sync role exchange.",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=8,
        environmental_complexity=0.810345,
        reference_run_ids=(
            "reference-168__tidb_business_change_dr_auto_sync_failover__planned_dual_dc_failover__mock__r001",
        ),
    ),
    runtime=_COMMON_RUNTIME,
    database="k09_dr",
    table="ledger_markers",
    canary_table="endpoint_fence_canaries",
    handoff_table="dr_failover_handoffs",
    zone_label="zone",
    primary_zone="primary",
    dr_zone="dr",
    primary_endpoint="tidb/tidb-0",
    dr_endpoint="tidb/tidb-1",
    primary_tikv_targets=("tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"),
    primary_store_count=3,
    dr_voter_count=2,
    dr_learner_count=1,
    total_dr_store_count=3,
    wait_store_timeout="5s",
    wait_recover_timeout="0s",
    failover_mode="planned",
    knowledge_hops=_PLANNED_KNOWLEDGE_HOPS,
    reference_path=(
        "the business interruption is bound to the live two-domain topology rather than to a PD Leader or TSO observation",
        "three primary-zone voters, two DR voters, and one DR learner are distinguished from the current Store labels and Placement Rules",
        "DR Auto-Sync state, Region replication status, PD leadership, and TSO are treated as separate facts",
        "the router is switched to a distributing policy and the old endpoint is drained to zero active connections",
        "the old writer fence and voter/learner role constraints are verified before the role exchange",
        "the official placement role exchange is accepted but not treated as terminal",
        "terminal DR state and Placement/Region convergence are confirmed before business admission",
        "the old route remains fenced while seed marker truth and a bounded DR endpoint canary are verified",
        "the planned exchange is submitted only after the synchronized role, endpoint, and business invariants close",
    ),
    reference_tool_counts=(
        ("manage_cluster(router,dr_replication)", 8, 20),
        ("execute_sql(business_truth_region_status)", 7, 44),
        ("search_knowledge(dr-auto-sync_and_placement)", 7, 30),
    ),
)


_UNPLANNED_CASE = TidbBusinessChangeDrAutoSyncForUnplannedFailoverScenarioCase(
    case_id="unplanned_dual_dc_failover",
    case_no=1,
    evaluator=TidbBusinessChangeDrAutoSyncUnplannedFailoverEvaluatorCase,
    title="Recover a primary-AZ loss through the K09 DR Auto-Sync unsafe-recovery boundary.",
    alert=(
        "K09 计划外灾难：primary 数据中心的 SQL endpoint 和 3 个 primary-AZ TiKV 已不可用，DR 端仍保留控制面和副本。"
        "请先证明旧 primary 已被业务写入口 fence，再从当前 Store/Region/复制状态确定完整 failed Store 集合，"
        "提交官方 Online Unsafe Recovery 并等待 terminal；只在最后远端确认边界、把已确认 marker 的 count/sum/CRC 与幸存 endpoint 的 fence generation 写入业务 handoff receipt，"
        "并完成业务 marker/CRC/ADMIN CHECK TABLE 和 bounded canary 可复核后恢复 DR 写入。"
        "不要把 accepted 当成完成，不要把 learner 当成 voter，不要重启 Tombstone failed Store，也不要声称 TSO 对齐等于 RPO=0。"
    ),
    initial_state={
        "replication_mode": "dr-auto-sync",
        "primary_zone": "primary",
        "dr_zone": "dr",
        "primary_sql_endpoint": "stopped",
        "primary_store_count": 3,
        "business_route": "interrupted_until_fenced",
    },
    expected_target={
        "replication_mode": "dr-auto-sync",
        "primary_zone": "dr",
        "failed_stores": "Tombstone and not restarted",
        "old_primary": "fenced and unavailable",
        "business_truth": "acknowledged seed markers preserved within public RPO boundary",
    },
    background_workload=_k09_workload(),
    reference_report=structured_reference_report(
        case_id="unplanned_dual_dc_failover",
        factors=("DR Auto-Sync unplanned failover requires fencing the old primary, identifying every failed Store, and waiting for unsafe recovery terminal state",),
        changes=(
            "fenced the stopped primary SQL endpoint and identified all three failed primary Stores",
            "submitted unsafe remove-failed-stores and waited for the documented terminal output",
            "kept failed Stores Tombstone, applied the DR voter placement, and resumed through the DR endpoint",
        ),
        verification=(
            "the old endpoint remains stopped and fenced while the DR endpoint is live",
            "all acknowledged seed markers retain their count, sum, and CRC",
            "the DR handoff receipt binds the acknowledged boundary to the surviving endpoint and fence generation",
            "ADMIN CHECK TABLE and Region replication status complete the recovery evidence",
        ),
        summary="The reference path preserves the documented unsafe-recovery boundary and avoids split-brain writes.",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=9,
        environmental_complexity=0.798658,
        reference_run_ids=(
            "reference-168__tidb_business_change_dr_auto_sync_failover__unplanned_dual_dc_failover__mock__r001",
        ),
    ),
    runtime=_COMMON_RUNTIME,
    database="k09_dr",
    table="ledger_markers",
    canary_table="endpoint_fence_canaries",
    handoff_table="dr_failover_handoffs",
    zone_label="zone",
    primary_zone="primary",
    dr_zone="dr",
    primary_endpoint="tidb/tidb-0",
    dr_endpoint="tidb/tidb-1",
    primary_tikv_targets=("tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"),
    primary_store_count=3,
    dr_voter_count=2,
    dr_learner_count=1,
    total_dr_store_count=3,
    wait_store_timeout="5s",
    wait_recover_timeout="0s",
    failover_mode="unplanned",
    knowledge_hops=_UNPLANNED_KNOWLEDGE_HOPS,
    reference_path=(
        "the business interruption is decomposed into the stopped primary endpoint, failed Stores, surviving DR endpoint, and current business boundary",
        "the route fence is applied and verified before any promotion or recovery request",
        "the complete failed primary voter scope is derived from Store labels, states, and Region peers while the DR learner stays outside it",
        "unsafe remove-failed-stores returns accepted and exposes an asynchronous, lossy recovery task",
        "terminal recovery is distinguished from accepted request and every failed Store is verified Tombstone without restart",
        "surviving placement, Region state, and post-recovery scheduling are allowed to settle before validation",
        "the sealed acknowledged marker boundary is separated from live full-table aggregates, TSO text, and endpoint liveness",
        "the boundary is bound to the surviving endpoint and current fence generation in a schema-visible handoff receipt",
        "a bounded canary and ADMIN CHECK TABLE close the business admission proof before new DR writes are declared",
        "the unplanned recovery is accepted only when product, RPO, business, and safety invariants are all readable",
    ),
    reference_tool_counts=(
        ("manage_cluster(router,dr_replication,service)", 12, 28),
        ("execute_sql(business_truth_region_status_admin_check_handoff)", 10, 55),
        ("search_knowledge(unsafe_recovery_and_RPO)", 8, 36),
    ),
)


class _K09Injector(BaseFaultInjector):
    mode: str

    def __init__(self):
        self.control = None
        self.case = None

    def install(self, context: FaultLifecycleContext) -> None:
        self.case = context.case
        env = context.env
        self.control = env.configure_dr_auto_sync(self.case)
        self.control.install()
        self._create_business_truth(env, self.case)
        self.control.seal_business_truth()
        self._after_business_truth(env, self.case)

    def activate(self, context: FaultLifecycleContext) -> None:
        if self.control is None:
            self.case = context.case
            self.control = context.env.configure_dr_auto_sync(self.case)
        self.control.activate()
        self._after_activation(context.env, self.case)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        if self.control is None:
            raise RuntimeError("K09 injector has no DR Auto-Sync control during observability preparation")
        return self.control.prepare_observability()

    def quiesce(self, context: FaultLifecycleContext) -> None:
        return None

    def recover(self, context: FaultLifecycleContext) -> None:
        if self.control is None:
            raise RuntimeError("K09 injector has no DR Auto-Sync control during recovery")
        self.control.recover()

    def _create_business_truth(self, env, case) -> None:
        require_success_payload(
            env.execute_internal_sql(f"CREATE DATABASE {case.database}"),
            "K09 create business database",
        )
        require_success_payload(
            env.execute_internal_sql(
                f"CREATE TABLE {case.database}.{case.table} ("
                "marker_id VARCHAR(64) PRIMARY KEY, "
                "amount_cents BIGINT NOT NULL, "
                "payload VARCHAR(128) NOT NULL, "
                "commit_tso BIGINT NOT NULL, "
                "origin VARCHAR(64) NOT NULL"
                ")"
            ),
            "K09 create ledger marker table",
        )
        require_success_payload(
            env.execute_internal_sql(
                f"CREATE TABLE {case.database}.{case.canary_table} ("
                "canary_id BIGINT PRIMARY KEY AUTO_INCREMENT, "
                "endpoint_name VARCHAR(128) NOT NULL, "
                "token VARCHAR(64) NOT NULL, "
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                ")"
            ),
            "K09 create endpoint fence canary table",
        )
        require_success_payload(
            env.execute_internal_sql(
                f"CREATE TABLE {case.database}.{case.handoff_table} ("
                "handoff_id BIGINT PRIMARY KEY AUTO_INCREMENT, "
                "failover_mode ENUM('planned', 'unplanned') NOT NULL, "
                "endpoint_name VARCHAR(128) NOT NULL, "
                "acknowledged_marker_count BIGINT NOT NULL, "
                "acknowledged_amount_sum BIGINT NOT NULL, "
                "acknowledged_crc BIGINT NOT NULL, "
                "fence_generation BIGINT NOT NULL, "
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                ")"
            ),
            "K09 create DR failover handoff receipt table",
        )
        values = ",".join(
            "(" + ",".join((
                f"'seed-{index:04d}'",
                str(1000 + index * 17),
                f"'seed-payload-{index:04d}'",
                "TIDB_CURRENT_TSO()",
                "'initial-seed'",
            )) + ")"
            for index in range(1, 97)
        )
        require_success_payload(
            env.execute_internal_sql(
                f"INSERT INTO {case.database}.{case.table} "
                "(marker_id, amount_cents, payload, commit_tso, origin) VALUES "
                f"{values}"
            ),
            "K09 seed ledger markers",
        )

    def _after_business_truth(self, env, case) -> None:
        return None

    def _after_activation(self, env, case) -> None:
        return None


class TidbBusinessChangeDrAutoSyncPlannedInjector(_K09Injector):
    mode = "planned"
    install = _K09Injector.install
    activate = _K09Injector.activate
    prepare_observability = _K09Injector.prepare_observability
    quiesce = _K09Injector.quiesce
    recover = _K09Injector.recover


class TidbBusinessChangeDrAutoSyncUnplannedInjector(_K09Injector):
    mode = "unplanned"
    install = _K09Injector.install
    activate = _K09Injector.activate
    prepare_observability = _K09Injector.prepare_observability
    quiesce = _K09Injector.quiesce
    recover = _K09Injector.recover

    def _after_business_truth(self, env, case) -> None:
        env.deployment.stop_component(case.primary_endpoint)
        for target in case.primary_tikv_targets:
            env.deployment.stop_component(target)

    def _after_activation(self, env, case) -> None:
        services = env.deployment.node_states()
        if services[case.primary_endpoint]["running"]:
            raise RuntimeError(
                "K09 unplanned activation found the primary SQL endpoint running: "
                f"target={case.primary_endpoint!r}, state={services[case.primary_endpoint]!r}"
            )


class TidbBusinessChangeDrAutoSyncFailoverScenario(TiDBScenario):
    scenario_id = "tidb_business_change_dr_auto_sync_failover"
    description = (
        "Evaluates planned and unplanned TiDB v8.1 DR Auto-Sync dual-AZ role transitions "
        "with real PD placement, Store recovery, endpoint fencing, and business marker truth."
    )
    cases = (_PLANNED_CASE, _UNPLANNED_CASE)

    def build_fault_plan(self, case: TidbBusinessChangeDrAutoSyncFailoverCase) -> tuple[FaultPlan, ...]:
        injector_type = {
            "planned": TidbBusinessChangeDrAutoSyncPlannedInjector,
            "unplanned": TidbBusinessChangeDrAutoSyncUnplannedInjector,
        }[case.failover_mode]
        return (
            FaultPlan(
                injector_type=injector_type,
                config={
                    "mode": case.failover_mode,
                    "primary_endpoint": case.primary_endpoint,
                    "dr_endpoint": case.dr_endpoint,
                    "primary_tikv_targets": list(case.primary_tikv_targets),
                },
            ),
        )


__all__ = (
    "TidbBusinessChangeDrAutoSyncFailoverCase",
    "TidbBusinessChangeDrAutoSyncForPlannedFailoverScenarioCase",
    "TidbBusinessChangeDrAutoSyncForUnplannedFailoverScenarioCase",
    "TidbBusinessChangeDrAutoSyncFailoverScenario",
    "TidbBusinessChangeDrAutoSyncPlannedInjector",
    "TidbBusinessChangeDrAutoSyncUnplannedInjector",
)
