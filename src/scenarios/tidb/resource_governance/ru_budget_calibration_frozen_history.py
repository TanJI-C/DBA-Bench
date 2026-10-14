from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace

from src.database.sql import execute_json_payload
from src.scenarios.evaluation.tidb.resource_governance.ru_budget_calibration_frozen_history import (
    TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryEvaluatorCase,
    TidbResourceGovernanceRuBudgetHistoryInvestigationEvaluatorCase,
)
from src.execution.history.records import HistoricalRecordSource
from src.execution.history.metrics import format_utc_timestamp
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)
from src.scenarios.tidb.common import validate_sql_identifier
from src.scenarios.tidb.resource_governance.ru_budget_calibration import (
    TidbResourceGovernanceRuBudgetCalibrationCase,
    TidbResourceGovernanceRuBudgetCalibrationInjector,
    _build_rg01_workload,
)
from src.workloads.specs import BackgroundWorkloadStartPhase

from ...base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


MF_RG01_RESOURCE_GROUPS = (
    "mf_rg01_checkout",
    "mf_rg01_revenue",
    "mf_rg01_archive",
    "mf_rg01_dashboard",
)
MF_RG01_CHECKOUT_PROFILES = (
    "mf_rg01_checkout_order_lookup",
    "mf_rg01_checkout_customer_lookup",
    "mf_rg01_checkout_status_probe",
    "mf_rg01_checkout_order_update",
)
MF_RG01_REVENUE_PROFILES = (
    "mf_rg01_revenue_revenue_rollup",
    "mf_rg01_revenue_region_join",
)

MF_RG01_SERVICE_OBJECTIVES = (
    (1, "2026-07-01 00:00:00", None, "checkout", "mf_rg01_checkout", "checkout_p95_ms", "<=", 500.0, "active"),
    (2, "2026-07-01 00:00:00", None, "revenue", "mf_rg01_revenue", "revenue_qps", ">=", 0.18, "active"),
    (3, "2026-07-01 00:00:00", None, "cluster", "cluster", "shared_ru_per_sec", "<=", 1100.0, "active"),
    (4, "2026-07-01 00:00:00", None, "checkout", "mf_rg01_checkout", "minimum_ru_per_sec", ">=", 500.0, "active"),
    (5, "2026-07-01 00:00:00", None, "revenue", "mf_rg01_revenue", "minimum_ru_per_sec", ">=", 220.0, "active"),
    (6, "2026-07-01 00:00:00", None, "archive", "mf_rg01_archive", "minimum_ru_per_sec", ">=", 40.0, "active"),
    (7, "2026-07-01 00:00:00", None, "dashboard", "mf_rg01_dashboard", "minimum_ru_per_sec", ">=", 20.0, "active"),
    (11, "2026-07-01 00:00:00", None, "platform", "default", "reserved_ru_per_sec", ">=", 100.0, "active"),
    (8, "2026-01-01 00:00:00", "2026-06-30 23:59:59", "checkout", "mf_rg01_checkout", "checkout_p95_ms", "<=", 800.0, "retired"),
    (9, "2026-01-01 00:00:00", "2026-06-30 23:59:59", "revenue", "mf_rg01_revenue", "revenue_qps", ">=", 0.10, "retired"),
    (10, "2026-01-01 00:00:00", "2026-06-30 23:59:59", "cluster", "cluster", "shared_ru_per_sec", "<=", 900.0, "retired"),
)

MF_RG01_BASELINE_RESOURCE_GROUPS = (
    ("mf_rg01_checkout", 600, "BOUNDED"),
    ("mf_rg01_revenue", 240, "BOUNDED"),
    ("mf_rg01_archive", 80, "BOUNDED"),
    ("mf_rg01_dashboard", 80, "BOUNDED"),
)
MF_RG01_FAULT_RESOURCE_GROUPS = (
    ("mf_rg01_checkout", 8, "BOUNDED"),
    ("mf_rg01_revenue", 40, "UNLIMITED"),
    ("mf_rg01_archive", 180, "UNLIMITED"),
    ("mf_rg01_dashboard", 260, "UNLIMITED"),
)


def _rename_workload_text(value: str) -> str:
    replacements = (
        ("rg01_oltp_order_history_probe", "mf_rg01_checkout_order_history_probe"),
        ("rg01_oltp_order_lookup", "mf_rg01_checkout_order_lookup"),
        ("rg01_oltp_customer_lookup", "mf_rg01_checkout_customer_lookup"),
        ("rg01_oltp_status_probe", "mf_rg01_checkout_status_probe"),
        ("rg01_oltp_order_update", "mf_rg01_checkout_order_update"),
        ("rg01_olap_revenue_rollup", "mf_rg01_revenue_revenue_rollup"),
        ("rg01_olap_region_join", "mf_rg01_revenue_region_join"),
        ("rg01_olap_customer_mix", "mf_rg01_revenue_customer_mix"),
        ("rg01_batch", "mf_rg01_archive"),
        ("rg01_adhoc", "mf_rg01_dashboard"),
        ("rg01_oltp", "mf_rg01_checkout"),
        ("rg01_olap", "mf_rg01_revenue"),
    )
    for source, target in replacements:
        value = value.replace(source, target)
    return value


def _build_frozen_history_workload(db: str) -> object:
    base = _build_rg01_workload(db, "orders", "customers", "event_log")
    profiles = tuple(
        replace(
            profile,
            name=_rename_workload_text(profile.name),
            sql=_rename_workload_text(profile.sql),
        )
        for profile in base.profiles
    )
    return replace(
        base,
        profiles=profiles,
        seed=20260816,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        warmup_seconds=60,
    )


MF_RG01_HISTORY = FrozenHistorySpec(
    schema_version=1,
    duration_seconds=43_200,
    normal_capture_seconds=120,
    normal_capture_count=5,
    fault_capture_seconds=480,
    base_step_seconds=2,
    overview_step_seconds=120,
    block_min_seconds=120,
    block_max_seconds=120,
    transition_seconds=20,
    target_age_seconds_range=(3_600, 7_200),
    required_metrics=(
        "resource_group_usage",
        "resource_group_throttle",
        "qps",
        "query_latency",
    ),
    metric_targets={
        "resource_group_usage": (
            "mf_rg01_checkout",
            "mf_rg01_revenue",
            "mf_rg01_archive",
            "mf_rg01_dashboard",
            "default",
        ),
        "resource_group_throttle": (
            "mf_rg01_checkout",
            "mf_rg01_revenue",
            "mf_rg01_archive",
            "mf_rg01_dashboard",
            "default",
        ),
        "qps": (None,),
        "query_latency": (None,),
    },
    record_sources=(
        HistoricalRecordSource.COMPONENT_LOG,
        HistoricalRecordSource.TOPSQL,
        HistoricalRecordSource.SLOW_QUERIES,
    ),
    decoys=(
        HistoryDecoySpec(
            decoy_id="archive_bounded_peak",
            kind=DecoyKind.METRIC_ONLY,
            metric="resource_group_usage",
            field="total_ru_per_second",
            target="mf_rg01_archive",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=120,
            amplitude_mad=1.0,
        ),
        HistoryDecoySpec(
            decoy_id="single_report_slow",
            kind=DecoyKind.METRIC_ONLY,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=120,
            amplitude_mad=1.0,
        ),
        HistoryDecoySpec(
            decoy_id="dashboard_token_burst",
            kind=DecoyKind.METRIC_ONLY,
            metric="resource_group_usage",
            field="total_ru_per_second",
            target="mf_rg01_dashboard",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=120,
            amplitude_mad=1.5,
        ),
        HistoryDecoySpec(
            decoy_id="platform_peak",
            kind=DecoyKind.METRIC_ONLY,
            metric="resource_group_usage",
            field="total_ru_per_second",
            target="default",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=120,
            amplitude_mad=1.2,
        ),
        HistoryDecoySpec(
            decoy_id="checkout_demand_peak",
            kind=DecoyKind.METRIC_ONLY,
            metric="resource_group_usage",
            field="total_ru_per_second",
            target="mf_rg01_checkout",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=120,
            amplitude_mad=1.0,
        ),
    ),
    max_points_per_series=1_000,
    max_scalar_samples_per_response=20_000,
    max_history_records_per_response=250,
    install_before_normal_capture=True,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryForHistoryCalibrationScenarioCase(
    TidbResourceGovernanceRuBudgetCalibrationCase
):
    baseline_resource_groups: tuple[tuple[str, int, str], ...]
    platform_reserve_ru_per_sec: int


class TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryInjector(
    TidbResourceGovernanceRuBudgetCalibrationInjector
):
    """Create a healthy baseline, then activate the historical allocation error."""

    retain_workload_after_metric_history = True

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Keep the fault state active through the Agent phase."""

    def install(self, context: FaultLifecycleContext) -> None:
        super().install(context)

    def _configure(self, config: Mapping[str, object]) -> None:
        super()._configure(config)
        self.fault_resource_groups = tuple(
            (
                validate_sql_identifier(str(group), "fault_resource_group"),
                int(ru),
                str(burstable),
            )
            for group, ru, burstable in config["fault_resource_groups"]
        )

    @staticmethod
    def _execute(env, sql: str, context: str) -> dict:
        return execute_json_payload(env.execute_internal_sql, sql, f"{context}: sql={sql!r}")

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        for group, ru, burstable in self.fault_resource_groups:
            burst_clause = {
                "BOUNDED": "BURSTABLE=FALSE",
                "UNLIMITED": "BURSTABLE=TRUE",
            }[burstable]
            self._execute(
                context.env,
                f"ALTER RESOURCE GROUP {group} RU_PER_SEC = {ru} {burst_clause}",
                f"activate frozen-history RG01 allocation group={group}",
            )
        self._verify_persistent_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        evidence = super().prepare_observability(context)
        return {
            "mf_rg01_initial_resource_groups": evidence["rg01_initial_resource_groups"],
            "mf_rg01_business_truth": evidence["rg01_business_truth"],
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        super().quiesce(context)

    def recover(self, context: FaultLifecycleContext) -> None:
        super().recover(context)


_MF_RG01_CASE = TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryForHistoryCalibrationScenarioCase(
    case_id="ru_budget_history_calibration",
    case_no=0,
    evaluator=TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryEvaluatorCase,
    title="Calibrate a bounded checkout RU budget from historical demand pressure.",
    alert=(
        "[SEV-2] Checkout and revenue users report uneven response time during recurring operational cycles. "
        "Archive and dashboard traffic share the TiDB cluster, and the current resource-governance allocation "
        "is under review. Investigate the recent operating history and current service objectives, then calibrate "
        "the existing managed resource groups without changing business data, disabling resource control, or "
        "restarting cluster services. In the submitted report, describe the historical demand, wait, latency, "
        "allocation, active-objective, and benign-window findings in the standard diagnosis.conditions evidence."
    ),
    initial_state={
        "resource_control": "ON",
        "resource_groups": {
            "mf_rg01_checkout": {"ru_per_sec": 8, "burstable": "BOUNDED"},
            "mf_rg01_revenue": {"ru_per_sec": 40, "burstable": "UNLIMITED"},
            "mf_rg01_archive": {"ru_per_sec": 180, "burstable": "UNLIMITED"},
            "mf_rg01_dashboard": {"ru_per_sec": 260, "burstable": "UNLIMITED"},
        },
        "history": "recent operating cycles are available for inspection",
    },
    expected_target={
        "resource_control": "ON",
        "minimum_ru_per_sec": {
            "mf_rg01_checkout": 500,
            "mf_rg01_revenue": 220,
            "mf_rg01_archive": 40,
            "mf_rg01_dashboard": 20,
        },
        "maximum_managed_ru_per_sec": 1100,
        "platform_reserve_ru_per_sec": 100,
        "checkout_p95_ms": 500.0,
        "revenue_qps": 0.18,
        "burstable": "NO/BOUNDED",
    },
    background_workload=_build_frozen_history_workload("benchops_mf_rg01"),
    frozen_history=MF_RG01_HISTORY,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "historical_window",
                    "factor": "the root cause is visible only in the historical mixed peak window",
                    "entity": "historical checkout resource pressure",
                    "evidence": ["resource group usage and throttling history"],
                },
                {
                    "type": "competition",
                    "factor": "checkout RU demand exceeds its bounded budget before checkout resource wait",
                    "entity": "checkout demand precedes checkout resource wait",
                    "evidence": ["checkout resource-group RU and wait time ordering"],
                },
                {
                    "type": "propagation",
                    "factor": "checkout resource wait and shared query latency rise after checkout demand",
                    "entity": "checkout quota wait propagates into shared TiDB latency",
                    "evidence": ["checkout RU, wait, cluster latency, and qps sequence"],
                },
                {
                    "type": "allocation",
                    "factor": "checkout is below its active minimum and its bounded budget is below historical demand",
                    "entity": "checkout allocation mismatch with an undersized bounded budget",
                    "evidence": ["current resource group inventory"],
                },
                {
                    "type": "objectives",
                    "factor": "active service objectives and platform reserve must be used instead of retired objectives",
                    "entity": "current objectives bind the four managed groups and preserve the default platform reserve",
                    "evidence": ["effective_from, effective_to, and status rows"],
                },
                {
                    "type": "exclusions",
                    "factor": "bounded archive peak and single report slow query are benign windows, not the root cause",
                    "entity": "archive bounded peak and single-report slow are excluded explanations",
                    "evidence": ["benign windows retain normal checkout wait and business SLO"],
                },
            ]
        },
        "outcome": {
            "changes": [
                "calibrated the four managed resource groups with finite bounded allocations",
                "preserved the default platform reserve and resource control",
            ],
            "verification": [
                "fresh mixed-workload observation met checkout and revenue objectives",
                "business truth was unchanged",
            ],
        },
        "summary": "Historical checkout RU and wait evidence identified an undersized bounded allocation; the managed budgets were calibrated without changing business data.",
    },
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.762289,
        reference_run_ids=(
            "tidb_frozen_history_rg01_mock_reference_r9_20260816__tidb_resource_governance_ru_budget_calibration_frozen_history__"
            "ru_budget_history_calibration__reference_mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=3,
        tidb_count=1,
        tikv_memory_mb=4096,
        sql_timeout_seconds=120,
        image_group_key=None,
        bootstrap_cache_enabled=False,
    ),
    db="benchops_mf_rg01",
    orders_table="orders",
    customers_table="customers",
    event_table="event_log",
    objective_table="service_objectives",
    service_objectives=MF_RG01_SERVICE_OBJECTIVES,
    resource_groups=MF_RG01_RESOURCE_GROUPS,
    oltp_group="mf_rg01_checkout",
    olap_group="mf_rg01_revenue",
    minimum_ru_per_sec=(
        ("mf_rg01_checkout", 500),
        ("mf_rg01_revenue", 220),
        ("mf_rg01_archive", 40),
        ("mf_rg01_dashboard", 20),
    ),
    # The managed-group total cap is the published active service objective
    # (cluster shared_ru_per_sec <= 1100); the evaluator enforces exactly this
    # agent-visible bound.
    maximum_total_ru_per_sec=1100,
    maximum_oltp_p95_ms=500.0,
    minimum_olap_qps=0.18,
    observation_window_seconds=20.0,
    oltp_profiles=MF_RG01_CHECKOUT_PROFILES,
    olap_profiles=MF_RG01_REVENUE_PROFILES,
    orders_row_count=60000,
    customers_row_count=12000,
    event_row_count=24000,
    business_truth_sql=(
        "SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
        "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, customer_id, "
        "order_status, order_ts, amount, payload))), 0) "
        "FROM benchops_mf_rg01.orders"
    ),
    initial_resource_groups=MF_RG01_FAULT_RESOURCE_GROUPS,
    baseline_resource_groups=MF_RG01_BASELINE_RESOURCE_GROUPS,
    platform_reserve_ru_per_sec=100,
)

_INVESTIGATION_PROFILE_NAMES = (
    "mf_rg01_checkout_order_lookup",
    "mf_rg01_checkout_customer_lookup",
    "mf_rg01_checkout_status_probe",
    "mf_rg01_checkout_order_update",
    "mf_rg01_revenue_revenue_rollup",
    "mf_rg01_revenue_region_join",
    # Two archive profiles keep the archive RU channel dense enough that the
    # metric-only archive decoy always finds a nonzero MAD inside a short capture.
    "mf_rg01_archive_archive_scan",
    "mf_rg01_archive_customer_rollup",
    "mf_rg01_dashboard_dashboard_probe",
)
_INVESTIGATION_WORKLOAD = replace(
    _MF_RG01_CASE.background_workload,
    profiles=tuple(
        profile
        for profile in _MF_RG01_CASE.background_workload.profiles
        if profile.name in _INVESTIGATION_PROFILE_NAMES
    ),
    worker_count=4,
    seed=20260903,
    warmup_seconds=10,
)
_MF_RG01_INVESTIGATION_CASE = replace(
    _MF_RG01_CASE,
    case_id="ru_budget_history_investigation",
    case_no=1,
    evaluator=TidbResourceGovernanceRuBudgetHistoryInvestigationEvaluatorCase,
    title="Investigate a checkout RU deficit under a smaller mixed-service estate.",
    alert=(
        "[SEV-2] Checkout latency breached its objective during one recent mixed-service peak while revenue stayed healthy. "
        "Use the frozen history to distinguish bounded checkout throttling from the archive burst, then calibrate only the managed groups "
        "without changing business data, resource-control mode, or cluster lifecycle."
    ),
    background_workload=_INVESTIGATION_WORKLOAD,
    frozen_history=replace(
        _MF_RG01_CASE.frozen_history,
        duration_seconds=7_200,
        normal_capture_seconds=12,
        normal_capture_count=2,
        fault_capture_seconds=40,
        base_step_seconds=2,
        overview_step_seconds=60,
        block_min_seconds=8,
        block_max_seconds=12,
        transition_seconds=4,
        target_age_seconds_range=(900, 2_400),
        decoys=tuple(
            replace(decoy, duration_seconds=12)
            for decoy in _MF_RG01_CASE.frozen_history.decoys[:2]
        ),
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.5,
        reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
        protocol_version='difficulty-v2',
    ),
    orders_row_count=18_000,
    customers_row_count=4_000,
    event_row_count=6_000,
    observation_window_seconds=15.0,
)


def build_frozen_history_reference_report(
    audit: Mapping[str, object],
    timeline=None,
) -> dict[str, object]:
    target = audit["target_window"]
    decoys = {
        str(item["decoy_id"]): item
        for item in audit["decoy_windows"]
    }
    target_start = int(target["start_ms"])
    target_end = int(target["end_ms"])
    capture_validation = audit.get("frozen_history_validation")
    if not isinstance(capture_validation, Mapping):
        raise RuntimeError(
            "Frozen-history RG01 reference requires real capture validation in the frozen audit: "
            f"audit_keys={sorted(audit)!r}"
        )
    if timeline is not None:
        validation = TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryEvaluatorCase.validate_metric_history_timeline(
            timeline,
            dict(capture_validation),
        )
    else:
        validation = capture_validation
    validation_chain = validation.get("causal_chain")
    if not isinstance(validation_chain, list) or len(validation_chain) != 3:
        raise RuntimeError(
            "Frozen-history RG01 reference requires three real target metric hops: "
            f"causal_chain={validation_chain!r}"
        )
    timestamps = [format_utc_timestamp(int(item["timestamp_ms"])) for item in validation_chain]
    if int(validation_chain[-1]["timestamp_ms"]) >= target_end:
        raise RuntimeError(
            "Frozen-history RG01 reference cannot append the allocation hop after the measured latency hop: "
            f"latency_timestamp_ms={validation_chain[-1]['timestamp_ms']}, target_end_ms={target_end}"
        )
    timestamps.append(format_utc_timestamp(target_end))
    decoy_validation = validation.get("decoy_validation")
    if not isinstance(decoy_validation, Mapping):
        raise RuntimeError(
            "Frozen-history RG01 reference requires real decoy validation in the frozen audit: "
            f"validation_keys={sorted(validation)!r}"
        )
    target_window = {
        "start_timestamp": format_utc_timestamp(target_start),
        "end_timestamp": format_utc_timestamp(target_end),
        "timezone": "UTC",
    }
    demand = validation_chain[0]["values"]
    wait = validation_chain[1]["values"]
    latency = validation_chain[2]["values"]
    conditions = [
        {
            "type": "historical_window",
            "factor": "the root cause is visible only in the historical mixed peak window",
            "entity": "historical checkout resource pressure",
            "evidence": [
                f"the validated target window is {target_window['start_timestamp']} to {target_window['end_timestamp']} UTC",
                f"the target sequence starts with checkout demand {demand['checkout_ru_per_second']:.3f} RU/s at {timestamps[0]}",
                "the current snapshot is a post-fault state and is not substituted for the historical window",
            ],
        },
        {
            "type": "competition",
            "factor": "checkout RU demand exceeds its bounded budget before checkout resource wait",
            "entity": "checkout demand precedes checkout resource wait",
            "evidence": [
                f"at {timestamps[0]}, checkout demand was {demand['checkout_ru_per_second']:.3f} RU/s against budget {demand['configured_budget_ru_per_second']:.3f} RU/s",
                f"at {timestamps[1]}, checkout wait rose to {wait['checkout_wait_p95_ms']:.3f} ms after the demand hop",
            ],
        },
        {
            "type": "propagation",
            "factor": "checkout resource wait and shared query latency rise after checkout demand",
            "entity": "checkout quota wait propagates into shared TiDB latency",
            "evidence": [
                f"the validated order is demand at {timestamps[0]}, wait at {timestamps[1]}, then p95 latency {latency['query_latency_p95_ms']:.3f} ms at {timestamps[2]}",
                f"qps at the latency hop was {latency['qps']:.3f}, so the chain is not explained by a matching demand flash",
            ],
        },
        {
            "type": "allocation",
            "factor": "checkout is below its active minimum and its bounded budget is below historical demand",
            "entity": "checkout allocation mismatch with an undersized bounded budget",
            "evidence": [
                "current resource-group inventory and the validated target budget identify the undersized bounded checkout allocation",
            ],
        },
        {
            "type": "objectives",
            "factor": "active service objectives and platform reserve must be used instead of retired objectives",
            "entity": "current objectives bind the four managed groups and preserve the default platform reserve",
            "evidence": [
                "the standard handling path checks effective_from, effective_to, and status before changing the four Case-owned groups",
            ],
        },
        {
            "type": "exclusions",
            "factor": "bounded archive peak and single report slow query are benign windows, not the root cause",
            "entity": "archive bounded peak and single-report slow are excluded explanations",
            "evidence": [
                f"archive decoy max wait was {decoy_validation['archive_bounded_peak']['max_checkout_wait_p95_ms']:.3f} ms and its full chain flag was {decoy_validation['archive_bounded_peak']['complete_causal_chain']!r}",
                f"single-report decoy max checkout RU was {decoy_validation['single_report_slow']['max_checkout_ru_per_second']:.3f} RU/s and its full chain flag was {decoy_validation['single_report_slow']['complete_causal_chain']!r}",
            ],
        },
    ]
    return {
        "diagnosis": {"conditions": conditions},
        "outcome": dict(_MF_RG01_CASE.reference_report["outcome"]),
        "summary": _MF_RG01_CASE.reference_report["summary"],
    }


class TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryScenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_ru_budget_calibration_frozen_history"
    description = "Calibrates TiDB RU budgets from historical checkout pressure and group metric evidence."
    cases = (_MF_RG01_CASE, _MF_RG01_INVESTIGATION_CASE)

    def build_fault_plan(
        self,
        case: TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryForHistoryCalibrationScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryInjector,
                config={
                    "db": case.db,
                    "orders_table": case.orders_table,
                    "customers_table": case.customers_table,
                    "event_table": case.event_table,
                    "objective_table": case.objective_table,
                    "service_objectives": case.service_objectives,
                    "resource_groups": case.resource_groups,
                    "initial_resource_groups": case.baseline_resource_groups,
                    "fault_resource_groups": case.initial_resource_groups,
                    "orders_row_count": case.orders_row_count,
                    "customers_row_count": case.customers_row_count,
                    "event_row_count": case.event_row_count,
                    "business_truth_sql": case.business_truth_sql,
                },
            ),
        )


__all__ = (
    "MF_RG01_BASELINE_RESOURCE_GROUPS",
    "MF_RG01_FAULT_RESOURCE_GROUPS",
    "MF_RG01_HISTORY",
    "MF_RG01_RESOURCE_GROUPS",
    "TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryForHistoryCalibrationScenarioCase",
    "TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryInjector",
    "TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryScenario",
)
