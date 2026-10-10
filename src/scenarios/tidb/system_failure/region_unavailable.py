from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.system_failure.region_unavailable import (
    TidbSystemFailureRegionUnavailableEvaluatorCase,
    TidbSystemFailureRegionUnavailableFocusedEvaluatorCase,
)
from src.scenarios.evaluation.protocol import structured_reference_report
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


def _business_truth(row_count: int) -> tuple[int, int, int]:
    return (
        row_count,
        row_count * (row_count + 1) // 2,
        sum((order_id * 37) % 9000 + 100 for order_id in range(1, row_count + 1)),
    )


def _business_profiles() -> tuple[WorkloadProfile, ...]:
    return (
        WorkloadProfile(
            name="ma01_order_status_region_rollup",
            sql=(
                "SELECT order_status, region_id, COUNT(*) AS order_count, "
                "SUM(amount_cents) AS amount_cents "
                "FROM ma01_orders GROUP BY order_status, region_id "
                "ORDER BY order_count DESC LIMIT 24"
            ),
            qps=0.42,
            tier="MEDIUM",
            application_name="checkout-api",
            target="tidb/tidb-2",
        ),
        WorkloadProfile(
            name="ma01_customer_spend_leaderboard",
            sql=(
                "SELECT customer_id, COUNT(*) AS order_count, SUM(amount_cents) AS amount_cents "
                "FROM ma01_orders WHERE customer_id BETWEEN 1 AND 500 "
                "GROUP BY customer_id ORDER BY amount_cents DESC LIMIT 20"
            ),
            qps=0.32,
            tier="MEDIUM",
            application_name="customer-summary-api",
            target="tidb/tidb-0",
        ),
        WorkloadProfile(
            name="ma01_settlement_reconciliation",
            sql=(
                "SELECT COUNT(*) AS order_count, SUM(order_id) AS order_id_sum, "
                "BIT_XOR(order_id) AS order_id_xor "
                "FROM ma01_orders WHERE created_at >= '2026-02-01'"
            ),
            qps=0.24,
            tier="LIGHT",
            application_name="settlement-worker",
            target="tidb/tidb-1",
        ),
        WorkloadProfile(
            name="ma01_recent_order_search",
            sql=(
                "SELECT order_id, customer_id, order_status, amount_cents "
                "FROM ma01_orders WHERE order_id BETWEEN 1000 AND 11000 "
                "AND order_status IN ('PAID', 'SHIPPED') "
                "ORDER BY order_id DESC LIMIT 64"
            ),
            qps=0.55,
            tier="LIGHT",
            application_name="order-search-api",
            target="tidb/tidb-0",
        ),
        WorkloadProfile(
            name="ma01_region_amount_summary",
            sql=(
                "SELECT region_id, AVG(amount_cents) AS average_amount, "
                "MAX(created_at) AS newest_order "
                "FROM ma01_orders GROUP BY region_id ORDER BY region_id"
            ),
            qps=0.28,
            tier="LIGHT",
            application_name="regional-dashboard",
            target="tidb/tidb-2",
        ),
        WorkloadProfile(
            name="ma01_active_region_status_mix",
            sql=(
                "SELECT order_status, COUNT(*) AS order_count "
                "FROM ma01_orders WHERE region_id IN (1, 3, 5, 7, 9, 11) "
                "GROUP BY order_status ORDER BY order_status"
            ),
            qps=0.36,
            tier="LIGHT",
            application_name="fulfillment-dashboard",
            target="tidb/tidb-1",
        ),
        WorkloadProfile(
            name="ma01_amount_exception_scan",
            sql=(
                "SELECT COUNT(*) AS exception_count, SUM(amount_cents) AS exception_amount "
                "FROM ma01_orders WHERE amount_cents BETWEEN 1000 AND 5000 "
                "AND created_at >= '2026-01-15'"
            ),
            qps=0.31,
            tier="LIGHT",
            application_name="risk-monitor",
            target="tidb/tidb-2",
        ),
        WorkloadProfile(
            name="ma01_customer_order_probe",
            sql=(
                "SELECT order_id, order_status, amount_cents, created_at "
                "FROM ma01_orders WHERE customer_id = 4097 "
                "ORDER BY created_at DESC, order_id DESC LIMIT 32"
            ),
            qps=0.62,
            tier="LIGHT",
            application_name="customer-profile-api",
            target="tidb/tidb-0",
        ),
        WorkloadProfile(
            name="ma01_region_customer_cardinality",
            sql=(
                "SELECT region_id, COUNT(DISTINCT customer_id) AS customer_count "
                "FROM ma01_orders GROUP BY region_id ORDER BY customer_count DESC"
            ),
            qps=0.26,
            tier="MEDIUM",
            application_name="capacity-report",
            target="tidb/tidb-1",
        ),
        WorkloadProfile(
            name="ma01_completed_amount_window",
            sql=(
                "SELECT order_status, SUM(amount_cents) AS amount_cents "
                "FROM ma01_orders WHERE order_id > 50000 "
                "GROUP BY order_status ORDER BY amount_cents DESC"
            ),
            qps=0.34,
            tier="LIGHT",
            application_name="finance-report",
            target="tidb/tidb-0",
        ),
        WorkloadProfile(
            name="ma01_point_lookup_decoy",
            sql=(
                "SELECT order_id, customer_id, order_status, amount_cents "
                "FROM ma01_orders WHERE order_id = 77777"
            ),
            qps=0.85,
            tier="LIGHT",
            application_name="order-detail-api",
            target="tidb/tidb-2",
        ),
        WorkloadProfile(
            name="ma01_status_time_bucket",
            sql=(
                "SELECT order_status, DATE_FORMAT(created_at, '%Y-%m-%d') AS order_day, "
                "COUNT(*) AS order_count "
                "FROM ma01_orders WHERE created_at BETWEEN '2026-01-10' AND '2026-02-20' "
                "GROUP BY order_status, order_day ORDER BY order_day DESC LIMIT 40"
            ),
            qps=0.29,
            tier="MEDIUM",
            application_name="operations-report",
            target="tidb/tidb-1",
        ),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureRegionUnavailableForPdNetworkBlockScenarioCase(TiDBScenarioCase):
    db: str
    table: str
    row_count: int
    expected_business_truth: tuple[int, int, int]
    affected_tidb_target: str
    control_tidb_target: str
    protected_tidb_target: str
    affected_stale_pd_address: str
    control_pd_reject_rule_count: int
    control_stale_pd_address: str
    protected_stale_pd_address: str
    pd_ingress_rule_count: int
    pd_ingress_rule_marker: str
    pd_ingress_decoy_rules: tuple[tuple[str, str], ...]
    pd_shadow_ingress_targets: tuple[str, ...]
    pd_targets: tuple[str, ...]
    post_restart_rehydrated_pd_target: str
    pd_response_rule_count: int
    pd_response_rule_marker: str
    pd_response_shadow_targets: tuple[str, ...]
    pd_response_shadow_rule_marker: str
    tidb_shadow_egress_rule_marker: str
    tidb_stale_egress_rule_marker: str
    business_query: str


_CASE = TidbSystemFailureRegionUnavailableForPdNetworkBlockScenarioCase(
    case_id="region_unavailable_pd_network_block",
    reference_report=structured_reference_report(
        case_id="region_unavailable_pd_network_block",
        factors=(
            "Region unavailable is a misleading symptom from one TiDB losing PD client connectivity",
            "the effective failure is the three-member PD response OUTPUT boundary followed by stale affected-TiDB local egress and a replayed generic boundary",
            "PD, TiKV, Region replicas, and business data remain healthy",
        ),
        changes=("restored all three PD response paths, restarted only the affected TiDB to clear its stale local boundary, and removed the replayed generic boundary",),
        verification=(
            "all TiDB targets served the order workload",
            "PD/TiKV health, Region counts, and business truth remained unchanged",
        ),
        summary="The reference path fixed the PD response OUTPUT boundary, cleared the affected TiDB stale and replayed generic boundaries, and verified the alert was misleading.",
    ),
    case_no=0,
    evaluator=TidbSystemFailureRegionUnavailableEvaluatorCase,
    title="A misleading Region-unavailable alert during an intermittent order-service incident.",
    alert=(
        "告警：订单查询偶发 ERROR 9005 Region is unavailable，部分请求超时，但仍有 TiDB endpoint "
        "可以正常服务。请确定实际受影响的服务边界，在不重启健康 PD/TiKV、不改动业务数据、"
        "Region 副本或其他健康实例既有服务和安全边界的前提下恢复订单服务。"
    ),
    initial_state={
        "status": "degraded",
        "alert": "Region is unavailable",
        "business_impact": "intermittent order queries time out while comparison endpoints still serve",
    },
    expected_target={
        "status": "recovered",
        "pd": "healthy",
        "tikv": "healthy",
        "all_tidb_targets": "serving",
        "business_truth": "unchanged",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_business_profiles(),
        worker_count=8,
        seed=20260803,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=20,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=9,
        environmental_complexity=0.868603,
        reference_run_ids=(
            "reference-171__tidb_region_unavailable__"
            "region_unavailable_pd_network_block__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=3,
        sql_timeout_seconds=300,
        image_group_key=None,
        bootstrap_cache_enabled=False,
    ),
    db="benchops",
    table="ma01_orders",
    row_count=100_000,
    expected_business_truth=_business_truth(100_000),
    affected_tidb_target="tidb/tidb-2",
    control_tidb_target="tidb/tidb-0",
    protected_tidb_target="tidb/tidb-1",
    affected_stale_pd_address="192.0.2.239",
    control_pd_reject_rule_count=1,
    control_stale_pd_address="192.0.2.237",
    protected_stale_pd_address="192.0.2.238",
    pd_ingress_rule_count=1,
    pd_ingress_rule_marker="pd-client-policy",
    pd_ingress_decoy_rules=(
        ("pd/pd-0", "tidb/tidb-0"),
        ("pd/pd-1", "tidb/tidb-1"),
    ),
    pd_shadow_ingress_targets=("pd/pd-0", "pd/pd-1", "pd/pd-2"),
    pd_targets=("pd/pd-0", "pd/pd-1", "pd/pd-2"),
    post_restart_rehydrated_pd_target="pd/pd-1",
    pd_response_rule_count=1,
    pd_response_rule_marker="pd-response-policy",
    pd_response_shadow_targets=("tidb/tidb-0", "tidb/tidb-1"),
    pd_response_shadow_rule_marker="pd-response-shadow-policy",
    tidb_shadow_egress_rule_marker="pd-client-policy",
    tidb_stale_egress_rule_marker="pd-client-stale-policy",
    business_query=(
        "SELECT COUNT(*) AS order_count, SUM(order_id) AS order_id_sum, "
        "SUM(amount_cents) AS amount_cents FROM ma01_orders"
    ),
)

_FOCUSED_CASE = replace(
    _CASE,
    case_id="region_unavailable_pd_response_focus",
    case_no=1,
    evaluator=TidbSystemFailureRegionUnavailableFocusedEvaluatorCase,
    reference_report=structured_reference_report(
        case_id="region_unavailable_pd_response_focus",
        factors=(
            "the Region is unavailable alert is misleading because TiKV, Region replicas, the PD members, and the healthy TiDB neighbors remain healthy, while only one TiDB target is affected and the healthy comparison TiDB targets continue serving SQL",
            "the affected TiDB cannot complete PD client heartbeat, TSO, and operator state on TCP port 2379 because each PD member rejects response traffic from source port 2379 to the affected TiDB address; after the PD response paths are restored, the affected TiDB still holds a pd-client-stale-policy OUTPUT reject that requires an affected-only restart, and the post-restart policy replay that reintroduces a generic OUTPUT reject to a real PD endpoint must also be cleared before the order service is recovered",
        ),
        changes=(
            "restored the three PD response paths, restarted only the affected TiDB, and removed its replayed local boundary",
        ),
        verification=(
            "all TiDB targets served the order workload",
            "PD/TiKV health, Region counts, and business truth remained unchanged",
        ),
        summary="The focused reference path keeps the staged PD response and affected-TiDB recovery chain while reducing same-domain firewall decoys.",
    ),
    title="A focused Region-unavailable alert during an intermittent order-service incident.",
    alert=(
        "告警：订单查询偶发 ERROR 9005 Region is unavailable，tidb/tidb-1 的部分请求超时，"
        "但其他 TiDB endpoint 仍可服务。请定位实际服务边界，在不重启健康 PD/TiKV、"
        "不改动业务数据和健康实例既有安全边界的前提下恢复订单服务。"
    ),
    initial_state={
        "status": "degraded",
        "alert": "Region is unavailable",
        "business_impact": "tidb/tidb-1 order queries time out while comparison endpoints serve",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_business_profiles()[:8],
        worker_count=6,
        seed=20260813,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=16,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.794429,
        reference_run_ids=(
            "reference-81__tidb_system_failure_region_unavailable__"
            "region_unavailable_pd_response_focus__mock__r001",
        ),
    ),
    affected_tidb_target="tidb/tidb-1",
    control_tidb_target="tidb/tidb-0",
    protected_tidb_target="tidb/tidb-2",
    affected_stale_pd_address="192.0.2.239",
    control_stale_pd_address="192.0.2.237",
    protected_stale_pd_address="192.0.2.238",
    pd_ingress_decoy_rules=(("pd/pd-0", "tidb/tidb-0"),),
    pd_shadow_ingress_targets=("pd/pd-0", "pd/pd-1", "pd/pd-2"),
    pd_response_shadow_targets=("tidb/tidb-0",),
    post_restart_rehydrated_pd_target="pd/pd-0",
)


class TidbSystemFailureRegionUnavailableScenario(TiDBScenario):
    scenario_id = "tidb_system_failure_region_unavailable"
    description = (
        "An intermittent order-service incident with a misleading Region-unavailable alert."
    )
    cases = (_CASE, _FOCUSED_CASE)

    def build_fault_plan(
        self,
        case: TidbSystemFailureRegionUnavailableForPdNetworkBlockScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailureRegionUnavailableInjector,
                config={
                    "db": case.db,
                    "table": case.table,
                    "row_count": case.row_count,
                    "expected_business_truth": case.expected_business_truth,
                    "affected_tidb_target": case.affected_tidb_target,
                    "control_tidb_target": case.control_tidb_target,
                    "protected_tidb_target": case.protected_tidb_target,
                    "affected_stale_pd_address": case.affected_stale_pd_address,
                    "control_pd_reject_rule_count": case.control_pd_reject_rule_count,
                    "control_stale_pd_address": case.control_stale_pd_address,
                    "protected_stale_pd_address": case.protected_stale_pd_address,
                    "pd_ingress_rule_count": case.pd_ingress_rule_count,
                    "pd_ingress_rule_marker": case.pd_ingress_rule_marker,
                    "pd_ingress_decoy_rules": case.pd_ingress_decoy_rules,
                    "pd_shadow_ingress_targets": case.pd_shadow_ingress_targets,
                    "pd_targets": case.pd_targets,
                    "post_restart_rehydrated_pd_target": case.post_restart_rehydrated_pd_target,
                    "pd_response_rule_count": case.pd_response_rule_count,
                    "pd_response_rule_marker": case.pd_response_rule_marker,
                    "pd_response_shadow_targets": case.pd_response_shadow_targets,
                    "pd_response_shadow_rule_marker": case.pd_response_shadow_rule_marker,
                    "tidb_stale_egress_rule_marker": case.tidb_stale_egress_rule_marker,
                    "tidb_shadow_egress_rule_marker": case.tidb_shadow_egress_rule_marker,
                    "business_query": case.business_query,
                },
            ),
        )


__all__ = (
    "TidbSystemFailureRegionUnavailableForPdNetworkBlockScenarioCase",
    "TidbSystemFailureRegionUnavailableScenario",
)

import time

from collections.abc import Mapping
from datetime import date, timedelta

import pymysql

from src.database.sql import parse_json_object

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)


_PD_LEADER_PIN_ATTEMPTS = 3
_PD_LEADER_PIN_RETRY_SECONDS = 8


class TidbSystemFailureRegionUnavailableInjector(BaseFaultInjector):
    """Create a target-local PD connectivity incident with a partial-neighbor control-plane decoy."""

    def __init__(self):
        self.db = None
        self.table = None
        self.row_count = None
        self.expected_business_truth = None
        self.affected_tidb_target = None
        self.control_tidb_target = None
        self.protected_tidb_target = None
        self.affected_stale_pd_address = None
        self.control_pd_reject_rule_count = None
        self.control_stale_pd_address = None
        self.protected_stale_pd_address = None
        self.pd_ingress_rule_count = None
        self.pd_ingress_rule_marker = None
        self.pd_ingress_decoy_rules = None
        self.pd_shadow_ingress_targets = None
        self.pd_targets = None
        self.post_restart_rehydrated_pd_target = None
        self.pd_response_shadow_targets = None
        self.pd_response_shadow_rule_marker = None
        self.tidb_stale_egress_rule_marker = None
        self.business_query = None
        self.deployment = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._create_fixture(context.env)
        self._inject_recovered_control_plane_noise(context.env)
        self._pin_pd_leader_off_decoy_targets()
        self.deployment.arm_pd_network_rehydration(
            self.affected_tidb_target,
            (self.post_restart_rehydrated_pd_target,),
        )
        self.deployment.restart_component(self.affected_tidb_target)
        self.deployment.block_pd_network_egress_shadow(
            self.affected_tidb_target,
            self.pd_targets,
        )
        self.deployment.block_pd_network_stale_egress(
            self.affected_tidb_target,
            self.pd_targets,
        )
        self.deployment.block_pd_network_response(
            self.pd_targets,
            self.affected_tidb_target,
        )
        self.deployment.block_pd_network_response_shadow(
            self.pd_targets,
            self.pd_response_shadow_targets,
        )
        self.deployment.block_pd_network_address(
            self.affected_tidb_target,
            self.affected_stale_pd_address,
        )
        self._inject_pd_shadow_ingress()
        self._inject_pd_ingress_decoys()
        self._inject_protected_neighbor_noise()
        self._verify_fixture(context.env)
        self._verify_blocked(context.env)
        self._verify_protected(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._verify_fixture(context.env)
        self._inject_recovered_control_plane_noise(context.env)
        self._pin_pd_leader_off_decoy_targets()
        self.deployment.arm_pd_network_rehydration(
            self.affected_tidb_target,
            (self.post_restart_rehydrated_pd_target,),
        )
        self.deployment.restart_component(self.affected_tidb_target)
        self.deployment.block_pd_network_egress_shadow(
            self.affected_tidb_target,
            self.pd_targets,
        )
        self.deployment.block_pd_network_stale_egress(
            self.affected_tidb_target,
            self.pd_targets,
        )
        self.deployment.block_pd_network_response(
            self.pd_targets,
            self.affected_tidb_target,
        )
        self.deployment.block_pd_network_response_shadow(
            self.pd_targets,
            self.pd_response_shadow_targets,
        )
        self.deployment.block_pd_network_address(
            self.affected_tidb_target,
            self.affected_stale_pd_address,
        )
        self._inject_pd_shadow_ingress()
        self._inject_pd_ingress_decoys()
        self._inject_protected_neighbor_noise()
        self._verify_blocked(context.env)
        self._verify_protected(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config, context.env)
        affected_rules = self.deployment.inspect_pd_network(self.affected_tidb_target)
        affected_source_address = self._source_address(affected_rules, self.affected_tidb_target)
        shadow_egress = self._shadow_egress_evidence(affected_rules)
        if len(shadow_egress) != len(self.pd_targets):
            raise RuntimeError(
                "region-unavailable TiDB shadow egress policy is invalid: "
                f"target={self.affected_tidb_target!r}, expected={len(self.pd_targets)}, "
                f"actual={len(shadow_egress)}, rules={affected_rules!r}"
            )
        response_shadow_addresses = {
            target: self._source_address(
                self.deployment.inspect_pd_network(target),
                target,
            )
            for target in self.pd_response_shadow_targets
        }
        response_evidence = []
        response_shadow_evidence = []
        for pd_target in self.pd_targets:
            pd_rules = self.deployment.inspect_pd_network(pd_target)
            response_rule_count = self._pd_response_rule_count(
                pd_rules,
                marker=self.pd_response_rule_marker,
                destination_address=affected_source_address,
            )
            if response_rule_count != self.pd_response_rule_count:
                raise RuntimeError(
                    "region-unavailable PD response egress rule count is invalid: "
                    f"target={pd_target!r}, expected={self.pd_response_rule_count}, "
                    f"actual={response_rule_count}, destination={affected_source_address!r}, "
                    f"rules={pd_rules!r}"
                )
            response_evidence.append({
                "pd_target": pd_target,
                "destination_address": affected_source_address,
                "marker": self.pd_response_rule_marker,
                "rule_count": response_rule_count,
            })
        for pd_target in self.pd_targets:
            pd_rules = self.deployment.inspect_pd_network(pd_target)
            response_shadow_evidence.append({
                "pd_target": pd_target,
                "rules": self._pd_response_shadow_evidence(
                    pd_rules,
                    response_shadow_addresses,
                ),
            })
        stale_egress = self._tidb_stale_egress_evidence(affected_rules)
        if len(stale_egress) != len(self.pd_targets) or any(
            not item["effective_before_accept"] for item in stale_egress
        ):
            raise RuntimeError(
                "region-unavailable TiDB stale egress policy is invalid: "
                f"target={self.affected_tidb_target!r}, expected={len(self.pd_targets)}, "
                f"actual={len(stale_egress)}, marker={self.tidb_stale_egress_rule_marker!r}, "
                f"rules={affected_rules!r}"
            )
        control_rules = self.deployment.inspect_pd_network(self.control_tidb_target)
        control_rule_count = control_rules.count("--dport 2379")
        protected_rules = self.deployment.inspect_pd_network(self.protected_tidb_target)
        protected_rule_count = protected_rules.count("--dport 2379")
        if (
            self.affected_stale_pd_address not in affected_rules
        ):
            raise RuntimeError(
                "region-unavailable affected TiDB must retain its shadow PD egress pairs and stale mapping rule: "
                f"target={self.affected_tidb_target!r}, expected_shadow_rules={len(self.pd_targets)}, "
                f"stale_address={self.affected_stale_pd_address!r}, "
                f"observed_shadow_rules={len(shadow_egress)}, rules={affected_rules!r}"
            )
        source_addresses = {
            self.control_tidb_target: self._source_address(
                self.deployment.inspect_pd_network(self.control_tidb_target),
                self.control_tidb_target,
            ),
            self.protected_tidb_target: self._source_address(
                self.deployment.inspect_pd_network(self.protected_tidb_target),
                self.protected_tidb_target,
            ),
        }
        shadow_evidence = []
        for pd_target in self.pd_shadow_ingress_targets:
            pd_rules = self.deployment.inspect_pd_network(pd_target)
            if not self._shadow_ingress_rule_present(
                pd_rules,
                self.pd_ingress_rule_marker,
                affected_source_address,
            ):
                raise RuntimeError(
                    "region-unavailable PD shadow ingress policy is invalid: "
                    f"target={pd_target!r}, source={affected_source_address!r}, "
                    f"marker={self.pd_ingress_rule_marker!r}, "
                    f"rules={pd_rules!r}"
                )
            shadow_evidence.append({
                "pd_target": pd_target,
                "source_address": affected_source_address,
                "marker": self.pd_ingress_rule_marker,
                "effective": False,
                "reason": "source/port ACCEPT precedes the same-source REJECT",
            })
        decoy_evidence = []
        for pd_target, source_target in self.pd_ingress_decoy_rules:
            pd_rules = self.deployment.inspect_pd_network(pd_target)
            marker = self._ingress_marker(source_target)
            source_address = source_addresses[source_target]
            decoy_rule_count = self._ingress_rule_count(
                pd_rules,
                marker,
                source_address,
            )
            if decoy_rule_count != 1:
                raise RuntimeError(
                    "region-unavailable PD ingress decoy rule count is invalid: "
                    f"target={pd_target!r}, source={source_target!r}, expected=1, "
                    f"actual={decoy_rule_count}, marker={marker!r}, rules={pd_rules!r}"
                )
            decoy_evidence.append({
                "pd_target": pd_target,
                "source_target": source_target,
                "marker": marker,
                "source_address": source_address,
            })
        if (
            control_rule_count != self.control_pd_reject_rule_count
            or self.control_stale_pd_address not in control_rules
        ):
            raise RuntimeError(
                "region-unavailable control-neighbor firewall rule count is invalid: "
                f"target={self.control_tidb_target!r}, expected={self.control_pd_reject_rule_count}, "
                f"actual={control_rule_count}, stale_address={self.control_stale_pd_address!r}, "
                f"rules={control_rules!r}"
            )
        expected_protected_rule_count = 1
        if (
            protected_rule_count != expected_protected_rule_count
            or self.protected_stale_pd_address not in protected_rules
        ):
            raise RuntimeError(
                "region-unavailable protected-neighbor firewall rule count is invalid: "
                f"target={self.protected_tidb_target!r}, expected={expected_protected_rule_count}, "
                f"actual={protected_rule_count}, stale_address={self.protected_stale_pd_address!r}, "
                f"rules={protected_rules!r}"
            )
        return {
            "ma01_affected_tidb_target": self.affected_tidb_target,
            "ma01_control_tidb_target": self.control_tidb_target,
            "ma01_protected_tidb_target": self.protected_tidb_target,
            "ma01_affected_stale_pd_address": self.affected_stale_pd_address,
            "ma01_affected_stale_rule_count": int(
                self.affected_stale_pd_address in affected_rules
            ),
            "ma01_pd_ingress_source_address": affected_source_address,
            "ma01_pd_shadow_ingress_source_address": affected_source_address,
            "ma01_pd_shadow_ingress_rule_marker": self.pd_ingress_rule_marker,
            "ma01_pd_targets": self.pd_targets,
            "ma01_post_restart_rehydrated_pd_target": self.post_restart_rehydrated_pd_target,
            "ma01_blocked_pd_rule_count": len(self.pd_targets),
            "ma01_affected_pd_egress_rule_count": 0,
            "ma01_pd_response_rule_count": self.pd_response_rule_count,
            "ma01_pd_response_rule_marker": self.pd_response_rule_marker,
            "ma01_pd_response_rules": response_evidence,
            "ma01_pd_response_shadow_targets": self.pd_response_shadow_targets,
            "ma01_pd_response_shadow_rule_marker": self.pd_response_shadow_rule_marker,
            "ma01_pd_response_shadow_rules": response_shadow_evidence,
            "ma01_tidb_shadow_egress_rule_marker": self.tidb_shadow_egress_rule_marker,
            "ma01_tidb_shadow_egress_rules": shadow_egress,
            "ma01_tidb_stale_egress_rule_marker": self.tidb_stale_egress_rule_marker,
            "ma01_tidb_stale_egress_rules": stale_egress,
            "ma01_pd_shadow_ingress_rule_count": self.pd_ingress_rule_count,
            "ma01_pd_shadow_ingress_targets": self.pd_shadow_ingress_targets,
            "ma01_pd_shadow_ingress_rules": shadow_evidence,
            "ma01_control_neighbor_rule_count": control_rule_count,
            "ma01_control_stale_pd_address": self.control_stale_pd_address,
            "ma01_protected_neighbor_rule_count": protected_rule_count,
            "ma01_protected_stale_pd_address": self.protected_stale_pd_address,
            "ma01_pd_ingress_rule_count": self.pd_ingress_rule_count,
            "ma01_pd_ingress_rule_marker": self.pd_ingress_rule_marker,
            "ma01_pd_ingress_targets": self.pd_targets,
            "ma01_pd_ingress_decoy_rules": decoy_evidence,
            "ma01_business_truth": self.expected_business_truth,
            "ma01_business_query": self.business_query,
        }

    def _inject_recovered_control_plane_noise(self, env) -> None:
        self.deployment.block_pd_network(self.control_tidb_target)
        region_sql = f"SHOW TABLE {self.db}.{self.table} REGIONS"
        payload = parse_json_object(
            env.execute_sql(region_sql, target=self.control_tidb_target),
            "verify region-unavailable recovered control-plane noise",
        )
        if payload.get("status") == "success":
            raise RuntimeError(
                "region-unavailable recovered control-plane noise did not produce a PD-dependent failure: "
                f"target={self.control_tidb_target!r}, sql={region_sql!r}, payload={payload!r}"
        )
        self.deployment.allow_pd_network(self.control_tidb_target)
        self.deployment.block_pd_network_address(
            self.control_tidb_target,
            self.control_stale_pd_address,
        )
        self._verify_control(env)

    def _inject_pd_ingress_decoys(self) -> None:
        for pd_target, source_target in self.pd_ingress_decoy_rules:
            self.deployment.block_pd_network_ingress_decoy(source_target, pd_target)

    def _inject_pd_shadow_ingress(self) -> None:
        for pd_target in self.pd_shadow_ingress_targets:
            self.deployment.block_pd_network_ingress_shadow(
                self.affected_tidb_target,
                pd_target,
            )

    def _inject_protected_neighbor_noise(self) -> None:
        self.deployment.block_pd_network_address(
            self.protected_tidb_target,
            self.protected_stale_pd_address,
        )

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self.deployment.disarm_pd_network_rehydration(self.affected_tidb_target)
        for pd_target in self.pd_shadow_ingress_targets:
            self.deployment.allow_pd_network_ingress_shadow(
                self.affected_tidb_target,
                pd_target,
            )
        self.deployment.allow_pd_network_egress_shadow(
            self.affected_tidb_target,
            self.pd_targets,
        )
        self.deployment.allow_pd_network_stale_egress(
            self.affected_tidb_target,
            self.pd_targets,
        )
        for pd_target, source_target in self.pd_ingress_decoy_rules:
            self.deployment.allow_pd_network_ingress_decoy(source_target, pd_target)
        for pd_target in self.pd_targets:
            self.deployment.allow_pd_network_response_shadow(
                pd_target,
                self.pd_response_shadow_targets,
            )
        for pd_target in self.pd_targets:
            self.deployment.allow_pd_network(pd_target)
        self.deployment.allow_pd_network(self.affected_tidb_target)
        self.deployment.allow_pd_network_address(
            self.affected_tidb_target,
            self.affected_stale_pd_address,
        )
        self.deployment.allow_pd_network(self.control_tidb_target)
        self.deployment.allow_pd_network_address(
            self.control_tidb_target,
            self.control_stale_pd_address,
        )
        self.deployment.allow_pd_network(self.protected_tidb_target)
        self.deployment.allow_pd_network_address(
            self.protected_tidb_target,
            self.protected_stale_pd_address,
        )

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self.deployment.disarm_pd_network_rehydration(self.affected_tidb_target)
        for pd_target in self.pd_shadow_ingress_targets:
            self.deployment.allow_pd_network_ingress_shadow(
                self.affected_tidb_target,
                pd_target,
            )
        self.deployment.allow_pd_network_egress_shadow(
            self.affected_tidb_target,
            self.pd_targets,
        )
        self.deployment.allow_pd_network_stale_egress(
            self.affected_tidb_target,
            self.pd_targets,
        )
        for pd_target, source_target in self.pd_ingress_decoy_rules:
            self.deployment.allow_pd_network_ingress_decoy(source_target, pd_target)
        for pd_target in self.pd_targets:
            self.deployment.allow_pd_network_response_shadow(
                pd_target,
                self.pd_response_shadow_targets,
            )
        for pd_target in self.pd_targets:
            self.deployment.allow_pd_network(pd_target)
        self.deployment.allow_pd_network(self.affected_tidb_target)
        self.deployment.allow_pd_network_address(
            self.affected_tidb_target,
            self.affected_stale_pd_address,
        )
        self.deployment.allow_pd_network(self.control_tidb_target)
        self.deployment.allow_pd_network_address(
            self.control_tidb_target,
            self.control_stale_pd_address,
        )
        self.deployment.allow_pd_network(self.protected_tidb_target)
        self.deployment.allow_pd_network_address(
            self.protected_tidb_target,
            self.protected_stale_pd_address,
        )
        self.deployment.restart_component(self.affected_tidb_target)
        self.deployment.wait_for_target(self.affected_tidb_target, 120)

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "db")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.row_count = int(config["row_count"])
        self.expected_business_truth = tuple(config["expected_business_truth"])
        self.affected_tidb_target = str(config["affected_tidb_target"])
        self.control_tidb_target = str(config["control_tidb_target"])
        self.protected_tidb_target = str(config["protected_tidb_target"])
        self.affected_stale_pd_address = str(config["affected_stale_pd_address"])
        self.control_pd_reject_rule_count = int(config["control_pd_reject_rule_count"])
        self.control_stale_pd_address = str(config["control_stale_pd_address"])
        self.protected_stale_pd_address = str(config["protected_stale_pd_address"])
        self.pd_ingress_rule_count = int(config["pd_ingress_rule_count"])
        self.pd_ingress_rule_marker = str(config["pd_ingress_rule_marker"])
        self.pd_ingress_decoy_rules = tuple(
            (str(pd_target), str(source_target))
            for pd_target, source_target in config["pd_ingress_decoy_rules"]
        )
        self.pd_shadow_ingress_targets = tuple(
            str(target) for target in config["pd_shadow_ingress_targets"]
        )
        self.pd_targets = tuple(str(target) for target in config["pd_targets"])
        self.post_restart_rehydrated_pd_target = str(config["post_restart_rehydrated_pd_target"])
        self.business_query = str(config["business_query"])
        self.pd_response_rule_count = int(config["pd_response_rule_count"])
        self.pd_response_rule_marker = str(config["pd_response_rule_marker"])
        self.pd_response_shadow_targets = tuple(
            str(target) for target in config["pd_response_shadow_targets"]
        )
        self.pd_response_shadow_rule_marker = str(config["pd_response_shadow_rule_marker"])
        self.tidb_stale_egress_rule_marker = str(config["tidb_stale_egress_rule_marker"])
        self.tidb_shadow_egress_rule_marker = str(config["tidb_shadow_egress_rule_marker"])
        self.deployment = env.get_deployment()

    def _ingress_marker(self, source_target: str) -> str:
        return self.pd_ingress_rule_marker

    def _source_address(self, rules: str, target: str) -> str:
        addresses = {
            parts[3].removesuffix("/32")
            for line in rules.splitlines()
            if (parts := line.split())
            and len(parts) > 3
            and parts[0] == "-A"
            and parts[1] == "OUTPUT"
            and parts[2] == "-s"
        }
        if len(addresses) != 1:
            raise RuntimeError(
                "region-unavailable TiDB source address mapping is ambiguous: "
                f"target={target!r}, addresses={sorted(addresses)!r}, rules={rules!r}"
            )
        return next(iter(addresses))

    def _ingress_rule_count(
        self,
        rules: str,
        marker: str,
        source_address: str,
    ) -> int:
        return sum(
            "-A INPUT" in line
            and "--dport 2379" in line
            and marker in line
            and f"-s {source_address}/32" in line
            for line in rules.splitlines()
        )

    def _pd_response_rule_count(
        self,
        rules: str,
        *,
        marker: str,
        destination_address: str,
    ) -> int:
        return sum(
            "-A OUTPUT" in line
            and "--sport 2379" in line
            and marker in line
            and f"-d {destination_address}/32" in line
            for line in rules.splitlines()
        )

    def _pd_response_shadow_evidence(
        self,
        rules: str,
        destination_addresses: Mapping[str, str],
    ) -> list[dict[str, object]]:
        lines = rules.splitlines()
        evidence = []
        for destination_target, destination_address in destination_addresses.items():
            accept_indexes = [
                index
                for index, line in enumerate(lines)
                if "-A OUTPUT" in line
                and "--sport 2379" in line
                and f"-d {destination_address}/32" in line
                and "-j ACCEPT" in line
            ]
            reject_indexes = [
                index
                for index, line in enumerate(lines)
                if "-A OUTPUT" in line
                and "--sport 2379" in line
                and self.pd_response_shadow_rule_marker in line
                and f"-d {destination_address}/32" in line
                and "-j REJECT" in line
            ]
            if (
                len(accept_indexes) != 1
                or len(reject_indexes) != 1
                or min(accept_indexes) >= min(reject_indexes)
            ):
                raise RuntimeError(
                    "region-unavailable PD response shadow policy is invalid: "
                    f"destination_target={destination_target!r}, "
                    f"destination_address={destination_address!r}, "
                    f"accept_indexes={accept_indexes!r}, reject_indexes={reject_indexes!r}, "
                    f"marker={self.pd_response_shadow_rule_marker!r}, rules={rules!r}"
                )
            evidence.append({
                "destination_target": destination_target,
                "destination_address": destination_address,
                "marker": self.pd_response_shadow_rule_marker,
                "accept_before_reject": True,
                "accept_count": 1,
                "reject_count": 1,
            })
        return evidence

    def _shadow_egress_evidence(self, rules: str) -> list[dict[str, object]]:
        lines = rules.splitlines()
        accepts: dict[str, list[int]] = {}
        rejects: dict[str, list[int]] = {}
        for index, line in enumerate(lines):
            parts = line.split()
            if (
                len(parts) >= 4
                and parts[0] == "-A"
                and parts[1] == "OUTPUT"
                and "--dport 2379" in line
                and "-d" in parts
            ):
                destination = parts[parts.index("-d") + 1]
                if "-j ACCEPT" in line:
                    accepts.setdefault(destination, []).append(index)
                elif self.tidb_shadow_egress_rule_marker in line and "-j REJECT" in line:
                    rejects.setdefault(destination, []).append(index)
        return [
            {
                "destination_address": destination.removesuffix("/32"),
                "accept_before_reject": min(accept_indexes) < min(reject_indexes),
                "accept_count": len(accept_indexes),
                "reject_count": len(reject_indexes),
            }
            for destination, accept_indexes in sorted(accepts.items())
            if (reject_indexes := rejects.get(destination))
        ]

    def _tidb_stale_egress_evidence(self, rules: str) -> list[dict[str, object]]:
        lines = rules.splitlines()
        accepts: dict[str, list[int]] = {}
        stale_rejects: dict[str, list[int]] = {}
        for index, line in enumerate(lines):
            parts = line.split()
            if (
                len(parts) >= 4
                and parts[0] == "-A"
                and parts[1] == "OUTPUT"
                and "--dport 2379" in line
                and "-d" in parts
            ):
                destination = parts[parts.index("-d") + 1]
                if "-j ACCEPT" in line:
                    accepts.setdefault(destination, []).append(index)
                elif self.tidb_stale_egress_rule_marker in line and "-j REJECT" in line:
                    stale_rejects.setdefault(destination, []).append(index)
        evidence = []
        for destination, reject_indexes in sorted(stale_rejects.items()):
            accept_indexes = accepts.get(destination, [])
            if len(reject_indexes) != 1 or not accept_indexes:
                raise RuntimeError(
                    "region-unavailable TiDB stale egress policy is missing its client shadow boundary: "
                    f"destination={destination!r}, reject_indexes={reject_indexes!r}, "
                    f"accept_indexes={accept_indexes!r}, marker={self.tidb_stale_egress_rule_marker!r}, "
                    f"rules={rules!r}"
                )
            evidence.append({
                "destination_address": destination.removesuffix("/32"),
                "marker": self.tidb_stale_egress_rule_marker,
                "effective_before_accept": min(reject_indexes) < min(accept_indexes),
                "accept_count": len(accept_indexes),
                "reject_count": len(reject_indexes),
            })
        return evidence

    def _shadow_ingress_rule_present(
        self,
        rules: str,
        marker: str,
        source_address: str,
    ) -> bool:
        lines = rules.splitlines()
        accept_indexes = [
            index
            for index, line in enumerate(lines)
            if "-A INPUT" in line
            and "--dport 2379" in line
            and "-j ACCEPT" in line
            and f"-s {source_address}/32" in line
        ]
        reject_indexes = [
            index
            for index, line in enumerate(lines)
            if "-A INPUT" in line
            and "--dport 2379" in line
            and marker in line
            and "-j REJECT" in line
            and f"-s {source_address}/32" in line
        ]
        return bool(accept_indexes and reject_indexes and min(accept_indexes) < min(reject_indexes))

    def _connection(self, env):
        return pymysql.connect(
            host=env.host,
            port=env.port,
            user=env.user,
            password=env.password,
            database=self.db,
            charset="utf8mb4",
            autocommit=False,
            connect_timeout=10,
            read_timeout=35,
            write_timeout=35,
        )

    def _create_fixture(self, env) -> None:
        conn = self._connection(env)
        try:
            with conn.cursor() as cur:
                require_sql_success(
                    env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.table}"),
                    "clear region-unavailable business fixture",
                )
                require_sql_success(
                    env.execute_sql(
                        f"CREATE TABLE {self.db}.{self.table} ("
                        "order_id BIGINT PRIMARY KEY, "
                        "customer_id INT NOT NULL, "
                        "region_id INT NOT NULL, "
                        "order_status VARCHAR(16) NOT NULL, "
                        "amount_cents INT NOT NULL, "
                        "created_at DATETIME NOT NULL, "
                        "KEY idx_ma01_customer_status (customer_id, order_status), "
                        "KEY idx_ma01_region_created (region_id, created_at)"
                        ")"
                    ),
                    "create region-unavailable business fixture",
                )
                insert_sql = (
                    f"INSERT INTO {self.db}.{self.table} "
                    "(order_id, customer_id, region_id, order_status, amount_cents, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s)"
                )
                statuses = ("PAID", "PENDING", "SHIPPED", "CANCELLED")
                for start in range(1, self.row_count + 1, 2000):
                    rows = [
                        (
                            order_id,
                            (order_id * 17) % 5000 + 1,
                            (order_id * 7) % 12 + 1,
                            statuses[order_id % len(statuses)],
                            (order_id * 37) % 9000 + 100,
                            date(2026, 1, 1) + timedelta(days=order_id % 90),
                        )
                        for order_id in range(start, min(start + 2000, self.row_count + 1))
                    ]
                    cur.executemany(insert_sql, rows)
                    conn.commit()
        finally:
            conn.close()

    def _verify_fixture(self, env) -> None:
        payload = json_object(
            env.execute_sql(self.business_query, target=self.control_tidb_target),
            "verify region-unavailable business fixture",
        )
        rows = payload.get("result")
        if not isinstance(rows, list) or len(rows) != 1:
            raise RuntimeError(
                "region-unavailable business fixture truth returned an invalid row shape: "
                f"expected_one_row=True, actual={rows!r}, target={self.control_tidb_target!r}, "
                f"payload={payload!r}"
            )
        values = rows[0]
        if not isinstance(values, (list, tuple)) or len(values) != len(self.expected_business_truth):
            raise RuntimeError(
                "region-unavailable business fixture truth returned an invalid aggregate shape: "
                f"expected_columns={len(self.expected_business_truth)}, actual={values!r}, "
                f"target={self.control_tidb_target!r}, payload={payload!r}"
            )
        actual_truth = tuple(int(value) for value in values)
        if actual_truth != self.expected_business_truth:
            raise RuntimeError(
                "region-unavailable business fixture truth mismatch: "
                f"expected={self.expected_business_truth!r}, actual={actual_truth!r}, "
                f"raw={values!r}, "
                f"target={self.control_tidb_target!r}"
            )

    def _pin_pd_leader_off_decoy_targets(self) -> None:
        """Pin the PD raft leader to a PD without an ingress decoy.

        TiDB's PD client follows the PD raft leader, and each ingress decoy
        REJECTs client traffic on exactly its paired PD. The protected and
        control neighbors must keep serving while those decoys are active, so
        the leader has to sit on a PD whose ingress has no decoy rule.

        Contract: the pin is a preventive optimization, not a correctness
        requirement. PD transiently rejects transfers while an election is
        still settling (wget returncode=8), so each transfer is retried a
        bounded number of times, and when the pin still fails this method
        logs and returns with the leader left in place instead of raising.
        `_verify_protected` remains the hard gate: it fails the install if
        the leader placement actually breaks the protected neighbor.
        """
        decoyed = {pd_target for pd_target, _source in self.pd_ingress_decoy_rules}
        candidates = [pd_target for pd_target in self.pd_targets if pd_target not in decoyed]
        if not candidates:
            raise RuntimeError(
                "region-unavailable requires a PD without an ingress decoy to host the PD leader: "
                f"pd_targets={self.pd_targets!r}, decoys={self.pd_ingress_decoy_rules!r}"
            )
        destination = candidates[0].split("/", 1)[1]
        if self.deployment.current_pd_leader() == destination:
            return
        for attempt in range(1, _PD_LEADER_PIN_ATTEMPTS + 1):
            try:
                self.deployment.transfer_pd_leader(destination)
            except RuntimeError as error:
                print(
                    f"[region-unavailable] pd leader transfer rejected "
                    f"(attempt {attempt}/{_PD_LEADER_PIN_ATTEMPTS}): {error}"
                )
                if attempt < _PD_LEADER_PIN_ATTEMPTS:
                    time.sleep(_PD_LEADER_PIN_RETRY_SECONDS)
            else:
                break
        else:
            print(
                "[region-unavailable] pd leader pin abandoned: all "
                f"{_PD_LEADER_PIN_ATTEMPTS} transfer attempts were rejected, the leader "
                "stays in place, and the protected-neighbor probe remains the correctness gate"
            )
            return
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if self.deployment.current_pd_leader() == destination:
                return
            time.sleep(1)
        print(
            "[region-unavailable] pd leader pin abandoned: the leader did not reach "
            f"{destination!r} within 60s, the leader stays in place, and the "
            "protected-neighbor probe remains the correctness gate"
        )

    def _verify_blocked(self, env) -> None:
        probe_sql = (
            f"SELECT order_id FROM {self.db}.{self.table} "
            "WHERE order_id = 1"
        )
        payload = parse_json_object(
            env.execute_sql(probe_sql, target=self.affected_tidb_target),
            "verify region-unavailable affected TiDB connectivity",
        )
        if payload.get("status") == "success":
            raise RuntimeError(
                "region-unavailable business-table probe unexpectedly remains reachable after PD network block: "
                f"target={self.affected_tidb_target!r}, probe_sql={probe_sql!r}, payload={payload!r}"
            )
        if payload.get("status") != "error":
            raise RuntimeError(
                "region-unavailable target connectivity probe returned an invalid status: "
                f"target={self.affected_tidb_target!r}, probe_sql={probe_sql!r}, payload={payload!r}"
            )

    def _verify_protected(self, env) -> None:
        self._verify_serving(env, self.protected_tidb_target, "protected-neighbor")

    def _verify_control(self, env) -> None:
        self._verify_serving(env, self.control_tidb_target, "control-neighbor")

    def _verify_serving(self, env, target: str, label: str) -> None:
        probe_sql = (
            f"SELECT order_id FROM {self.db}.{self.table} "
            "WHERE order_id = 1"
        )
        payload = parse_json_object(
            env.execute_sql(probe_sql, target=target),
            f"verify region-unavailable {label} TiDB connectivity",
        )
        if payload.get("status") != "success":
            raise RuntimeError(
                f"region-unavailable {label} probe failed despite retaining a reachable PD endpoint: "
                f"target={target!r}, probe_sql={probe_sql!r}, payload={payload!r}"
            )


__all__ = ("TidbSystemFailureRegionUnavailableInjector",)
