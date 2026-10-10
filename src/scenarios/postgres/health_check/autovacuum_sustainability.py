"""PG-HC-MF01: real churn versus sustainable autovacuum capacity.

The Scenario and Case objects are immutable.  All database connections, worker
threads and sampling state belong to the injector instance for one CaseRun.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import json
import os
import subprocess
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Mapping

from src.scenarios.base import (
    BackgroundWorkloadSpec,
    CaseResourceSpec,
    DifficultyCalibration,
    FaultPlan,
    PostgresCaseRuntime,
    PostgresRuntimeSpec,
    PostgresScenario,
    PostgresScenarioCase,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.execution.history.metrics import MetricDefinition, MetricFrame, format_utc_timestamp, validate_metric_frame
from src.execution.history.records import CapturedRecords, HistoricalCoverage, HistoricalPointRecord, HistoricalRecordSource
from src.execution.postgres_metrics import (
    LivePostgresScenarioMetricProvider,
    POSTGRES_METRIC_CATALOG,
    PostgresScenarioMetricCatalog,
)
from src.scenarios.frozen_history import DecoyDirection, DecoyKind, HistoryDecoySpec, FrozenHistorySpec
from src.scenarios.postgres.common import (
    _json_object,
    _require_sql_success,
    _run_cleanup_steps,
    _validate_sql_identifier,
)
from src.scenarios.workloads import BackgroundWorkloadStartPhase, WorkloadProfile
from src.workloads.tpcds import get_tpcds_query

from src.scenarios.evaluation.postgres.health_check import (
    PgHealthCheckAutovacuumSustainabilityForCapacityDeficitEvaluatorCase,
    PgHealthCheckAutovacuumSustainabilityForCapacityDeficitSimpleEvaluatorCase,
)


PG_HC_MF01_RESOURCES = CaseResourceSpec(
    worker_physical_cores=4,
    worker_memory_mb=8192,
    container_cpu_limit=2.0,
    container_memory_mb=8192,
)

_PG_HC_MF01_COMMON_PARAMETERS = (
    ("autovacuum_naptime", "1s"),
    ("log_autovacuum_min_duration", "0"),
    ("track_io_timing", "on"),
    ("shared_preload_libraries", "pg_stat_statements"),
    ("logging_collector", "on"),
    ("log_destination", "stderr"),
    ("log_directory", "/var/log/postgresql"),
    ("log_filename", "postgresql-%Y-%m-%d_%H%M%S.log"),
    ("log_rotation_age", "1d"),
    ("log_rotation_size", "100MB"),
)

PG_HC_MF01_HARD_RUNTIME = PostgresRuntimeSpec(
    parameters=(
        ("autovacuum_max_workers", "3"),
        *_PG_HC_MF01_COMMON_PARAMETERS,
    )
)

PG_HC_MF01_SIMPLE_RUNTIME = PostgresRuntimeSpec(
    parameters=(
        ("autovacuum_max_workers", "8"),
        *_PG_HC_MF01_COMMON_PARAMETERS,
    )
)


def _profile_for_table(table: str, name: str, qps: float) -> WorkloadProfile:
    return WorkloadProfile(
        name=name,
        application_name="pg-hc-mf01-business-oltp",
        qps=qps,
        tier="OLTP",
        commit=True,
        sql=(
            "WITH changed AS ("
            f"UPDATE {table} SET payload = md5(clock_timestamp()::text || id::text), "
            "updated_at = clock_timestamp() "
            "WHERE id = ((extract(epoch FROM clock_timestamp())::bigint % 10000) + 1) "
            "RETURNING id) SELECT count(*) FROM changed"
        ),
    )


def _tpcds_profiles() -> tuple[WorkloadProfile, ...]:
    return (
        WorkloadProfile(
            name="tpcds_light_q3",
            sql=get_tpcds_query("q3"),
            qps=0.005,
            tier="TPCDS_LIGHT",
            commit=True,
            application_name="pg-hc-mf01-tpcds-light",
        ),
        WorkloadProfile(
            name="tpcds_medium_q2",
            sql=get_tpcds_query("q2"),
            qps=0.005,
            tier="TPCDS_MEDIUM",
            commit=True,
            application_name="pg-hc-mf01-tpcds-medium",
        ),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckAutovacuumSustainabilityCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    tables: tuple[str, ...]
    target_table: str
    decoy_tables: tuple[str, ...]
    history_table: str
    latency_table: str
    target_rows: int
    decoy_rows: int
    churn_workers: int
    churn_interval_seconds: float
    churn_baseline_seconds: float
    churn_weights: tuple[int, ...]
    churn_batch_sizes: tuple[int, ...]
    churn_baseline_batch_sizes: tuple[int, ...]
    churn_working_set_rows: tuple[int, ...]
    churn_baseline_working_set_rows: tuple[int, ...]
    churn_phase_seconds: float
    churn_phase_weights: tuple[tuple[int, ...], ...]
    churn_phase_batch_sizes: tuple[tuple[int, ...], ...]
    churn_phase_working_set_rows: tuple[tuple[int, ...], ...]
    planned_vacuum_tables: tuple[str, ...]
    target_reloptions: tuple[str, ...]
    normal_reloptions: tuple[str, ...]
    normal_reloptions_by_table: tuple[tuple[str, tuple[str, ...]], ...]
    slo_p99_ms: float
    min_success_rate: float
    background_profile_count: int
    pgbench_clients: int
    replay_tail_samples: int
    replay_history_seconds: int
    # The trusted acceptance replay models the announced next write window.
    # The multiplier raises only the target relation's churn batch during the
    # replay, so an unchanged maintenance policy must fail the published
    # bounded/removal acceptance and a real per-relation capacity increase is
    # required for OutcomePass.
    replay_churn_multiplier: float
    max_backlog_growth: int
    minimum_removal_ratio: float


class PgHealthCheckAutovacuumSustainabilityForCapacityDeficitScenarioCase(
    PgHealthCheckAutovacuumSustainabilityCase
):
    pass


class PgHealthCheckAutovacuumSustainabilityForCapacityDeficitSimpleScenarioCase(
    PgHealthCheckAutovacuumSustainabilityCase
):
    pass


_HARD_TABLES = (
    "hc_mf01_orders",
    "hc_mf01_order_items",
    "hc_mf01_customer_profile",
    "hc_mf01_inventory",
    "hc_mf01_shipments",
    "hc_mf01_web_sessions",
    "hc_mf01_audit_events",
    "hc_mf01_payment_events",
)
_SIMPLE_TABLES = (
    "hc_mf01_simple_orders",
    "hc_mf01_simple_events",
    "hc_mf01_simple_decoy",
)
_NORMAL_RELOPTIONS = (
    "autovacuum_enabled=true",
    "autovacuum_vacuum_scale_factor=0.2",
    "autovacuum_vacuum_threshold=50",
)
_HARD_SHARED_RELOPTIONS = (
    "autovacuum_enabled=true",
    "autovacuum_vacuum_scale_factor=0.005",
    "autovacuum_vacuum_threshold=20",
    "autovacuum_vacuum_cost_limit=60",
    "autovacuum_vacuum_cost_delay=2",
)
# The Easy target deliberately shares the ordinary static profile with its
# peers.  The target identity must come from the staged churn history.
_SIMPLE_TARGET_RELOPTIONS = _NORMAL_RELOPTIONS
# Hard must not expose the target through an obviously under-provisioned
# static setting. The target shares this ordinary profile with healthy
# near-neighbor relations; the deficit is observable only over time.
_HARD_TARGET_RELOPTIONS = _HARD_SHARED_RELOPTIONS
_HARD_CHURN_WEIGHTS = (3, 3, 3, 3, 3, 3, 3, 3)
_HARD_PHASE_SECONDS = 16.0
_HARD_PHASE_WEIGHTS = tuple(
    (3,) * len(_HARD_TABLES) for _ in range(1, len(_HARD_TABLES))
)
_HARD_PHASE_BATCH_SIZES = tuple(
    # Keep the public fault window short, but make an ungoverned target
    # genuinely unsustainable during the trusted replay.  Healthy peers stay
    # at the original 5-row cadence; a targeted capacity control still makes
    # the reference/mock path recover.
    tuple(80 if index == 0 else 5 for index in range(len(_HARD_TABLES)))
    for _ in range(1, len(_HARD_TABLES))
)
_HARD_PHASE_WORKING_SET_ROWS = tuple(
    tuple(30000 if index == 0 else 200 for index in range(len(_HARD_TABLES)))
    for _ in range(1, len(_HARD_TABLES))
)
# Keep the decoy active but below the target's sustained churn. Its real,
# local-workset maintenance activity creates a plausible short-window signal;
# only the multi-window generation/removal/backlog relationship identifies the
# target. The lower burst batch prevents a healthy near-neighbor from becoming
# a second sustained deficit under the shared maintenance budget.
_SIMPLE_CHURN_WEIGHTS = (4, 1, 2)
_HARD_NORMAL_RELOPTIONS_BY_TABLE = (
    *((table, _HARD_SHARED_RELOPTIONS) for table in _HARD_TABLES[1:]),
)
_SIMPLE_NORMAL_RELOPTIONS_BY_TABLE = (
    (_SIMPLE_TABLES[2], _NORMAL_RELOPTIONS),
)

HC1_METRICS = (
    "relation_churn",
    "vacuum_cleanup",
    "dead_tuple_backlog",
    "maintenance_io",
    "oltp_service",
    "xmin_horizon",
)

_HC1_RELATION_METRICS = frozenset({
    "relation_churn",
    "vacuum_cleanup",
    "dead_tuple_backlog",
})


def _hc1_metric_catalog(tables: tuple[str, ...]) -> PostgresScenarioMetricCatalog:
    relation_targets = tuple(tables)
    fixed_targets = {
        "maintenance_io": ("postgres",),
        "oltp_service": ("checkout",),
        "xmin_horizon": ("postgres",),
    }
    return PostgresScenarioMetricCatalog(
        definitions={metric: POSTGRES_METRIC_CATALOG.definition(metric) for metric in HC1_METRICS},
        targets={
            **fixed_targets,
            **{metric: relation_targets for metric in _HC1_RELATION_METRICS},
        },
        version=f"pg-hc1-capacity-deficit-v2-{','.join(relation_targets)}",
    )


_HC1_METRIC_CATALOG = _hc1_metric_catalog(_SIMPLE_TABLES)


def _simple_history_spec() -> FrozenHistorySpec:
    return FrozenHistorySpec(
        schema_version=2,
        duration_seconds=6 * 60 * 60,
        normal_capture_seconds=120,
        fault_capture_seconds=180,
        base_step_seconds=2,
        overview_step_seconds=300,
        block_min_seconds=60,
        block_max_seconds=120,
        transition_seconds=20,
        # Keep the target fault recent enough that the public two-hour
        # investigation window also contains the captured benign competitors.
        # The history remains six hours; only the placement contract narrows.
        target_age_seconds_range=(900, 1800),
        required_metrics=HC1_METRICS,
        record_sources=(HistoricalRecordSource.OPERATION_EVENT,),
        decoys=(
            HistoryDecoySpec(
                decoy_id="healthy-churn-burst",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="relation_churn",
                field="updated_tps",
                target=_SIMPLE_TABLES[2],
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=20,
                minimum_deviation_mad=1.0,
            ),
            HistoryDecoySpec(
                decoy_id="healthy-target-burst",
                # The target relation also has a real, recoverable burst in
                # the normal capture. The same relation later becomes the
                # sustained deficit, so target identity alone is not causal
                # proof.
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="relation_churn",
                field="updated_tps",
                target=_SIMPLE_TABLES[0],
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=40,
                minimum_deviation_mad=1.0,
            ),
            HistoryDecoySpec(
                decoy_id="planned-vacuum",
                # The planned VACUUM and its surrounding churn are captured
                # from the real normal window. Do not synthesize a metric
                # curve for a benign explanation.
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="relation_churn",
                field="updated_tps",
                target=_SIMPLE_TABLES[2],
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                minimum_deviation_mad=1.0,
            ),
        ),
        max_points_per_series=2000,
        max_scalar_samples_per_response=8000,
        max_history_query_seconds=1200,
        max_history_records_per_response=120,
        decoys_adjacent_to_target=True,
    )


def _hard_history_spec() -> FrozenHistorySpec:
    return FrozenHistorySpec(
        schema_version=2,
        duration_seconds=12 * 60 * 60,
        normal_capture_seconds=120,
        fault_capture_seconds=180,
        base_step_seconds=2,
        overview_step_seconds=300,
        block_min_seconds=60,
        block_max_seconds=120,
        transition_seconds=20,
        target_age_seconds_range=(1800, 10800),
        required_metrics=HC1_METRICS,
        record_sources=(
            HistoricalRecordSource.OPERATION_EVENT,
            HistoricalRecordSource.COMPONENT_LOG,
        ),
        # Both competitors are selected from the real normal capture. The
        # target burst is intentionally recoverable; target identity alone is
        # not evidence of a sustained cleanup deficit.
        decoys=(
            HistoryDecoySpec(
                decoy_id="healthy-target-burst",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="relation_churn",
                field="updated_tps",
                target=_HARD_TABLES[0],
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                minimum_deviation_mad=1.0,
            ),
            HistoryDecoySpec(
                decoy_id="healthy-neighbor-burst",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="relation_churn",
                field="updated_tps",
                target=_HARD_TABLES[1],
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                minimum_deviation_mad=1.0,
            ),
            HistoryDecoySpec(
                decoy_id="metric-only-cleanup-wave",
                # A cleanup-shaped metric deviation without an operation
                # record.  It is intentionally plausible, but cannot prove
                # that vacuum removed the generated backlog.
                kind=DecoyKind.METRIC_ONLY,
                metric="vacuum_cleanup",
                field="removed_tps",
                target=_HARD_TABLES[1],
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                amplitude_mad=2.0,
            ),
            HistoryDecoySpec(
                decoy_id="metric-only-backlog-wave",
                # A second same-family shape makes a single dead-tuple peak
                # insufficient; the Agent must check repeated churn/removal
                # and bounded historical records.
                kind=DecoyKind.METRIC_ONLY,
                metric="dead_tuple_backlog",
                field="estimated_dead_tuples",
                target=_HARD_TABLES[2],
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                amplitude_mad=2.0,
            ),
        ),
        max_points_per_series=4000,
        # Keep each historical tool response small enough for an LLM context.
        # The agent already has a compact overview; detailed evidence is
        # bounded to one interval and should not consume the whole prompt.
        max_scalar_samples_per_response=8000,
        max_history_query_seconds=900,
        max_history_records_per_response=120,
        max_history_response_chars=12000,
        decoys_adjacent_to_target=True,
    )


class PgAutovacuumMetricProvider(LivePostgresScenarioMetricProvider):
    """Public raw HC1 metrics and operation events backed by live observations."""

    def __init__(self, tables: tuple[str, ...], *, sample_interval_sec: int = 2) -> None:
        self.tables = tuple(tables)
        self._catalog = _hc1_metric_catalog(self.tables)
        super().__init__(catalog=self._catalog, sample_interval_sec=sample_interval_sec, max_points=2000)
        self._events: list[HistoricalPointRecord] = []
        self._latencies: deque[tuple[int, float, bool]] = deque(maxlen=4096)

    def reset(self) -> None:
        with self.lock:
            for metric in self._samples.values():
                metric.clear()
            self._events.clear()
            self._latencies.clear()

    def sample_metrics(self, *, connection, timestamp_ms: int, elapsed_seconds: float, base_values) -> Mapping[str, Mapping[str, float]]:
        """The injector owns HC1 sampling; no environment-level extras are needed."""
        return {}

    def record_latency(self, timestamp_ms: int, latency_ms: float, success: bool) -> None:
        with self.lock:
            self._latencies.append((int(timestamp_ms), float(latency_ms), bool(success)))

    def service_snapshot(self, timestamp_ms: int, window_seconds: int = 30) -> dict[str, float]:
        with self.lock:
            cutoff = int(timestamp_ms) - window_seconds * 1000
            recent = [item for item in self._latencies if item[0] >= cutoff]
        latencies = sorted(item[1] for item in recent)
        successes = sum(1 for _, _, success in recent if success)
        p99 = latencies[min(len(latencies) - 1, int(len(latencies) * 0.99))] if latencies else 0.0
        return {
            "transactions_per_sec": successes / max(window_seconds, 1),
            "p99_ms": p99,
            "success_ratio": successes / len(recent) if recent else 1.0,
        }

    def record_event(self, timestamp_ms: int, payload: Mapping[str, object]) -> None:
        with self.lock:
            self._events.append(HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                timestamp_ms=int(timestamp_ms),
                payload=dict(payload),
            ))

    def sample_metrics(
        self,
        *,
        connection,
        timestamp_ms: int,
        elapsed_seconds: float,
        base_values: Mapping[str, Mapping[str, float]],
    ) -> Mapping[str, Mapping[str, float]]:
        """The injector owns this provider's aligned sampling loop."""
        return {}

    def metric_history_warmup_seconds(self) -> float:
        return float(self.sample_interval_sec * 2)

    def capture_history(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
    ):
        deadline = time.monotonic() + max(10.0, float(self.sample_interval_sec * 3))
        while time.monotonic() < deadline:
            try:
                if self.available_range[1] >= end_epoch_ms:
                    break
            except RuntimeError:
                pass
            time.sleep(0.1)
        return self.capture(metrics, start_epoch_ms, end_epoch_ms, step_seconds)

    def capture_history_records(self, sources, start_ms: int, end_ms: int) -> CapturedRecords:
        if HistoricalRecordSource.OPERATION_EVENT not in sources:
            return CapturedRecords()
        with self.lock:
            events = tuple(event for event in self._events if start_ms <= event.timestamp_ms <= end_ms)
        return CapturedRecords(
            point_records=events,
            coverage=(HistoricalCoverage(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                start_ms=start_ms,
                end_ms=end_ms,
            ),),
        )

    def agent_contract(self) -> Mapping[str, object]:
        return {
            "metrics": {
                metric: {
                    "fields": list(POSTGRES_METRIC_CATALOG.definition(metric).value_fields),
                    "targets": list(self.catalog.target_variants(metric, None))[1:],
                }
                for metric in HC1_METRICS
            },
            "interpretation": "Compare raw churn, cleanup, backlog, I/O, OLTP and xmin observations across windows; no derived diagnosis field is exposed.",
        }


_HARD_CASE = PgHealthCheckAutovacuumSustainabilityForCapacityDeficitScenarioCase(
    case_id="capacity_deficit",
    case_no=0,
    evaluator=PgHealthCheckAutovacuumSustainabilityForCapacityDeficitEvaluatorCase,
    base_image_name="aiopsbench-pg-pg-hc-mf01-capacity-deficit-base:pg16",
    workload_tag="tpcds",
    tables=_HARD_TABLES,
    target_table=_HARD_TABLES[0],
    decoy_tables=_HARD_TABLES[1:],
    history_table="hc_mf01_observation_history",
    latency_table="hc_mf01_oltp_latency",
    target_rows=30000,
    # Equal initial cardinality prevents a single pg_class/pg_stat snapshot
    # from identifying the target. Only the live churn/removal relationship
    # should distinguish it from the protected near-neighbors.
    decoy_rows=30000,
    churn_workers=3,
    churn_interval_seconds=0.35,
    # Keep the first observation windows symmetric. The target-only high-churn
    # phase begins after the agent has a real baseline to compare against.
    churn_baseline_seconds=20.0,
    churn_weights=_HARD_CHURN_WEIGHTS,
    churn_batch_sizes=(20, 20, 20, 20, 20, 20, 20, 20),
    churn_baseline_batch_sizes=(5, 5, 5, 5, 5, 5, 5, 5),
    churn_working_set_rows=(30000, 2000, 2000, 2000, 2000, 2000, 2000, 2000),
    churn_baseline_working_set_rows=(2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000),
    churn_phase_seconds=_HARD_PHASE_SECONDS,
    churn_phase_weights=_HARD_PHASE_WEIGHTS,
    churn_phase_batch_sizes=_HARD_PHASE_BATCH_SIZES,
    churn_phase_working_set_rows=_HARD_PHASE_WORKING_SET_ROWS,
    # Hard relies on PostgreSQL's real autovacuum cycles. A helper that
    # manually vacuums every non-target relation would make the target identity
    # an orchestration artifact instead of a workload/capacity diagnosis.
    planned_vacuum_tables=(),
    target_reloptions=_HARD_TARGET_RELOPTIONS,
    normal_reloptions=_HARD_SHARED_RELOPTIONS,
    normal_reloptions_by_table=_HARD_NORMAL_RELOPTIONS_BY_TABLE,
    slo_p99_ms=6000.0,
    min_success_rate=0.98,
    background_profile_count=10,
    pgbench_clients=2,
    replay_tail_samples=8,
    replay_history_seconds=120,
    # Calibrated against the live 20260914 replay trials: at 3x the unchanged
    # shared policy cannot hold the published <=300-tuple / 75%-removal
    # acceptance, while the mock and moderate per-relation tunings pass.
    replay_churn_multiplier=3.0,
    max_backlog_growth=300,
    minimum_removal_ratio=0.75,
    title="Hard autovacuum sustainability review with multi-table churn, OLTP and TPC-DS noise.",
    alert=(
        "[Scheduled PostgreSQL Health Check] The next trading window is expected to increase write volume. "
        "Start with the compact metric overview, select one candidate relation/window, then use bounded "
        "history queries to review relation maintenance sustainability and prove that the next "
        "replay window keeps cleanup bounded without disabling maintenance or degrading OLTP. "
        "Change only relations whose repeated completed maintenance cycles prove a sustained deficit; relations "
        "that recover within the published replay window are healthy business objects and must remain unchanged. "
        "Acceptance uses the latest 8 samples: target backlog growth must be <=300 tuples, effective removal must "
        "reach at least 75% of generation, OLTP p99 must be <=6000 ms, and success "
        "rate must be >=0.98. From adjacent raw samples, generation is the sum of positive deltas in "
        "n_tup_ins, n_tup_upd and n_tup_del. When last_autovacuum or last_vacuum advances, effective "
        "removal is max(previous n_dead_tup + generation - current n_dead_tup, 0); otherwise it is zero. "
        "HARD HISTORY BOUNDARIES: first call query_metrics without timestamps for the compact overview; "
        "then choose exactly one evidence interval no longer than 900 seconds and use that same interval "
        "for the required metrics/logs. Never request a multi-hour explicit window, never retry an identical "
        "failed window, and after a history-window error either select a narrower interval or submit the "
        "evidence already collected."
    ),
    initial_state={
        "status": "maintenance_sustainability_review",
        "database": "postgresql-16",
        "workload": "pgbench_oltp_plus_tpcds_light_medium",
        "relation_mix": "eight_tables_with_overlapping_settings_and_sustained_target_workset",
    },
    expected_target={
        "status": "sustainable_after_targeted_governance",
        "target": "hc_mf01_orders",
        "backlog": "bounded_under_replay",
        "oltp_p99_ms": "<= 6000",
        "autovacuum": "enabled",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=(
            *(
                _profile_for_table(table, f"business_write_{index:02d}", 0.1)
                for index, table in enumerate(_HARD_TABLES, start=1)
            ),
            *_tpcds_profiles(),
        ),
        worker_count=3,
        seed=0xAF01,
        # Frozen-history setup needs a real normal capture before activation.
        # The SQL profiles, worker count, seed and rates remain unchanged.
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        warmup_seconds=5,
    ),
    reference_report={
        "diagnosis": {
            "conditions": [
                {"type": "finding", "factor": "cleanup capacity is insufficient", "entity": "hc_mf01_orders", "evidence": ["observed cleanup capacity below churn generation"]},
                {"type": "finding", "factor": "churn generation exceeds effective vacuum removal rate", "entity": "hc_mf01_orders", "evidence": ["DML counter deltas exceed removed tuples over multiple windows"]},
                {"type": "finding", "factor": "dead tuple backlog grows across observation cycles", "entity": "hc_mf01_orders", "evidence": ["same-strength replay shows a rising backlog"]},
                {"type": "exclusion", "factor": "the sustained deficit is target-specific while healthy neighboring relations recover after completed maintenance cycles", "entity": "hc_mf01_orders", "evidence": ["neighbor backlogs catch up or remain bounded after real vacuum cycles"]},
            ]
        },
        "outcome": {"changes": ["applied targeted cleanup-capacity governance"], "verification": ["replayed the next write window and verified bounded backlog and OLTP SLO"]},
        "summary": "The diagnosis must use repeated generation, removal and backlog observations to separate a sustained capacity deficit from high-I/O noise; the target has ordinary settings and the same initial size as healthy near-neighbors.",
    },
    runtime=PostgresCaseRuntime(resources=PG_HC_MF01_RESOURCES, parameters=PG_HC_MF01_HARD_RUNTIME),
    frozen_history=_hard_history_spec(),
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.813333,
        reference_run_ids=(
            "reference-58__"
            "pg_health_check_autovacuum_sustainability__capacity_deficit__mock__r001",
        ),
    ),
)


_SIMPLE_CASE = PgHealthCheckAutovacuumSustainabilityForCapacityDeficitSimpleScenarioCase(
    case_id="capacity_deficit_simple",
    case_no=1,
    evaluator=PgHealthCheckAutovacuumSustainabilityForCapacityDeficitSimpleEvaluatorCase,
    base_image_name="aiopsbench-pg-pg-hc-mf01-capacity-deficit-simple-base:pg16",
    workload_tag="tpcds",
    tables=_SIMPLE_TABLES,
    target_table=_SIMPLE_TABLES[0],
    decoy_tables=(_SIMPLE_TABLES[2],),
    history_table="hc_mf01_simple_observation_history",
    latency_table="hc_mf01_simple_oltp_latency",
    target_rows=12000,
    # Equal initial cardinality removes the simple case's former table-size
    # shortcut while keeping the workload and table count Easy-sized.
    decoy_rows=12000,
    churn_workers=1,
    churn_interval_seconds=0.8,
    # Keep the first agent-visible catalog snapshot in the common phase. The
    # target-only split must be learned from later history windows, not from a
    # single dead-tuple ranking.
    churn_baseline_seconds=60.0,
    churn_weights=_SIMPLE_CHURN_WEIGHTS,
    churn_batch_sizes=(5, 5, 5),
    # Keep protected simple neighbors healthy during the short normal
    # capture; only the target carries sustained churn in this case.
    churn_baseline_batch_sizes=(5, 1, 1),
    churn_working_set_rows=(12000, 12000, 12000),
    churn_baseline_working_set_rows=(12000, 12000, 12000),
    churn_phase_seconds=0.0,
    churn_phase_weights=(),
    churn_phase_batch_sizes=(),
    churn_phase_working_set_rows=(),
    planned_vacuum_tables=(_SIMPLE_TABLES[2],),
    target_reloptions=_SIMPLE_TARGET_RELOPTIONS,
    normal_reloptions=_NORMAL_RELOPTIONS,
    normal_reloptions_by_table=_SIMPLE_NORMAL_RELOPTIONS_BY_TABLE,
    slo_p99_ms=6000.0,
    min_success_rate=0.98,
    background_profile_count=3,
    # The Easy case already has one deterministic background OLTP profile;
    # a second pgbench workload only adds host contention to its SLO.
    pgbench_clients=0,
    replay_tail_samples=4,
    replay_history_seconds=120,
    # The Easy case keeps the published replay window at the observed write
    # strength; only the Hard case hardens the acceptance replay.
    replay_churn_multiplier=1.0,
    # The replay window never crosses the protected relations' vacuum
    # thresholds, so their natural accumulation (~105 tuples per 120s) must
    # stay inside this allowance or even perfect play fails bounded checks.
    max_backlog_growth=300,
    minimum_removal_ratio=0.75,
    title="Easy autovacuum sustainability review with one target, one decoy and one deterministic OLTP profile.",
    alert=(
        "[Scheduled PostgreSQL Health Check] One relation is accumulating cleanup work during a predictable "
        "write profile. Read the compact metric overview first, then compare the target with the decoy in one "
        "bounded history window, apply only a bounded target-level control, and verify the next write window."
    ),
    initial_state={"status": "maintenance_sustainability_review", "workload": "deterministic_oltp", "relation_mix": "three_relations_with_staged_churn_split"},
    expected_target={"status": "sustainable_after_targeted_governance", "target": "hc_mf01_simple_orders", "backlog": "bounded_under_replay", "oltp_p99_ms": "<= 6000", "autovacuum": "enabled"},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(
            _profile_for_table(table, f"pgbench_oltp_simple_{index}", 0.12)
            for index, table in enumerate(_SIMPLE_TABLES, start=1)
        ),
        worker_count=1,
        seed=0xAF01,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        warmup_seconds=3,
    ),
    reference_report={
        "diagnosis": {
            "conditions": [
                {"type": "finding", "factor": "cleanup capacity is insufficient", "entity": "hc_mf01_simple_orders", "evidence": ["target cleanup cannot keep up with its deterministic churn"]},
                {"type": "finding", "factor": "churn generation exceeds effective vacuum removal rate", "entity": "hc_mf01_simple_orders", "evidence": ["window deltas show generation above removal"]},
                {"type": "finding", "factor": "dead tuple backlog grows across observation cycles", "entity": "hc_mf01_simple_orders", "evidence": ["backlog rises over consecutive cycles"]},
            ]
        },
        "outcome": {"changes": ["applied targeted cleanup-capacity governance"], "verification": ["replayed the deterministic write profile and verified bounded backlog"]},
        "summary": "The Easy case keeps a small search space, but static settings and initial size are identical; only the short baseline-to-dynamic churn history identifies the target.",
    },
    runtime=PostgresCaseRuntime(resources=PG_HC_MF01_RESOURCES, parameters=PG_HC_MF01_SIMPLE_RUNTIME),
    frozen_history=_simple_history_spec(),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.678571,
        reference_run_ids=("pending_pg_hc_mf01_capacity_deficit_simple_reference",),
    ),
)


class PgHealthCheckAutovacuumSustainabilityInjector(BaseFaultInjector):
    """Create real churn, sampling and bounded maintenance noise for one CaseRun."""

    def __init__(self) -> None:
        self.env = None
        self.run_id = ""
        self.case_id = ""
        self.tables: tuple[str, ...] = ()
        self.target_table = ""
        self.decoy_tables: tuple[str, ...] = ()
        self.history_table = ""
        self.latency_table = ""
        self.target_rows = 0
        self.decoy_rows = 0
        self.churn_workers = 0
        self.churn_interval_seconds = 0.5
        self.churn_baseline_seconds = 0.0
        self.churn_weights: tuple[int, ...] = ()
        self.churn_batch_sizes: tuple[int, ...] = ()
        self.churn_baseline_batch_sizes: tuple[int, ...] = ()
        self.churn_working_set_rows: tuple[int, ...] = ()
        self.churn_baseline_working_set_rows: tuple[int, ...] = ()
        self.churn_phase_seconds = 0.0
        self.churn_phase_weights: tuple[tuple[int, ...], ...] = ()
        self.churn_phase_batch_sizes: tuple[tuple[int, ...], ...] = ()
        self.churn_phase_working_set_rows: tuple[tuple[int, ...], ...] = ()
        self.replay_churn_multiplier = 1.0
        self.planned_vacuum_tables: tuple[str, ...] = ()
        self._churn_schedule: tuple[str, ...] = ()
        self._churn_phase_schedules: tuple[tuple[str, ...], ...] = ()
        self._baseline_churn_schedule: tuple[str, ...] = ()
        self._baseline_until = 0.0
        self.target_reloptions: tuple[str, ...] = ()
        self.normal_reloptions: tuple[str, ...] = ()
        self.normal_reloptions_by_table: dict[str, tuple[str, ...]] = {}
        self.pgbench_clients = 2
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []
        self._pgbench_process = None
        self._vacuum_started: dict[str, dt.datetime] = {}
        self._metric_provider: PgAutovacuumMetricProvider | None = None
        self._public_history = False
        self._prepared_for_history = False
        self._fault_active = False
        self._runtime_started = 0.0
        self._previous_table_samples: dict[str, tuple] = {}
        self._previous_io_sample: tuple[float, float, float, float] | None = None
        self._replay_capture = False
        self._replay_samples: list[dict[str, object]] = []
        self._replay_artifact: dict[str, object] | None = None

    @staticmethod
    def _literal(value: object) -> str:
        return "'" + str(value).replace("'", "''") + "'"

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.run_id = str(config["run_id"])
        self.case_id = str(config["case_id"])
        self.tables = tuple(_validate_sql_identifier(value, "table") for value in config["tables"])
        self.target_table = _validate_sql_identifier(str(config["target_table"]), "target_table")
        self.decoy_tables = tuple(_validate_sql_identifier(value, "decoy_table") for value in config["decoy_tables"])
        self.history_table = _validate_sql_identifier(str(config["history_table"]), "history_table")
        self.latency_table = _validate_sql_identifier(str(config["latency_table"]), "latency_table")
        self.target_rows = int(config["target_rows"])
        self.decoy_rows = int(config["decoy_rows"])
        self.churn_workers = int(config["churn_workers"])
        self.churn_interval_seconds = float(config["churn_interval_seconds"])
        self.churn_baseline_seconds = max(float(config.get("churn_baseline_seconds", 0.0)), 0.0)
        self.churn_weights = tuple(max(int(value), 0) for value in config["churn_weights"])
        self.churn_batch_sizes = tuple(
            max(int(value), 1) for value in config.get("churn_batch_sizes", ())
        )
        if len(self.churn_batch_sizes) != len(self.tables):
            raise ValueError("PG-HC-MF01 churn_batch_sizes must match tables")
        self.churn_baseline_batch_sizes = tuple(
            max(int(value), 1) for value in config.get("churn_baseline_batch_sizes", ())
        )
        if len(self.churn_baseline_batch_sizes) != len(self.tables):
            raise ValueError("PG-HC-MF01 churn_baseline_batch_sizes must match tables")
        self.churn_working_set_rows = tuple(
            max(int(value), 1) for value in config.get("churn_working_set_rows", ())
        )
        self.churn_baseline_working_set_rows = tuple(
            max(int(value), 1) for value in config.get("churn_baseline_working_set_rows", ())
        )
        if len(self.churn_working_set_rows) != len(self.tables):
            raise ValueError("PG-HC-MF01 churn_working_set_rows must match tables")
        if len(self.churn_baseline_working_set_rows) != len(self.tables):
            raise ValueError("PG-HC-MF01 churn_baseline_working_set_rows must match tables")
        self.churn_phase_seconds = max(float(config.get("churn_phase_seconds", 0.0)), 0.0)
        self.churn_phase_weights = tuple(
            tuple(max(int(value), 0) for value in phase)
            for phase in config.get("churn_phase_weights", ())
        )
        self.churn_phase_batch_sizes = tuple(
            tuple(max(int(value), 1) for value in phase)
            for phase in config.get("churn_phase_batch_sizes", ())
        )
        self.churn_phase_working_set_rows = tuple(
            tuple(max(int(value), 1) for value in phase)
            for phase in config.get("churn_phase_working_set_rows", ())
        )
        phased = (
            bool(self.churn_phase_weights),
            bool(self.churn_phase_batch_sizes),
            bool(self.churn_phase_working_set_rows),
        )
        if len(set(phased)) != 1:
            raise ValueError(
                "PG-HC-MF01 phased churn weights, batch sizes and working sets must be configured together"
            )
        if self.churn_phase_weights and self.churn_phase_seconds <= 0:
            raise ValueError("PG-HC-MF01 churn_phase_seconds must be positive for phased churn")
        if not (
            len(self.churn_phase_weights)
            == len(self.churn_phase_batch_sizes)
            == len(self.churn_phase_working_set_rows)
        ):
            raise ValueError("PG-HC-MF01 phased churn plans must have the same phase count")
        if any(
            len(phase) != len(self.tables)
            for phase in (
                *self.churn_phase_weights,
                *self.churn_phase_batch_sizes,
                *self.churn_phase_working_set_rows,
            )
        ):
            raise ValueError("PG-HC-MF01 phased churn plans must match tables")
        all_working_sets = (
            self.churn_working_set_rows,
            self.churn_baseline_working_set_rows,
            *self.churn_phase_working_set_rows,
        )
        if any(value > self.target_rows for plan in all_working_sets for value in plan):
            raise ValueError("PG-HC-MF01 churn working sets cannot exceed seeded relation rows")
        self.planned_vacuum_tables = tuple(
            _validate_sql_identifier(value, "planned_vacuum_table")
            for value in config.get("planned_vacuum_tables", ())
        )
        if len(self.churn_weights) != len(self.tables):
            raise ValueError("PG-HC-MF01 churn_weights must match tables")
        self._churn_schedule = tuple(
            table
            for table, weight in zip(self.tables, self.churn_weights)
            for _ in range(weight)
        )
        if not self._churn_schedule:
            raise ValueError("PG-HC-MF01 churn_weights must schedule at least one table")
        self._churn_phase_schedules = tuple(
            tuple(table for table, weight in zip(self.tables, phase) for _ in range(weight))
            for phase in self.churn_phase_weights
        )
        if any(not schedule for schedule in self._churn_phase_schedules):
            raise ValueError("PG-HC-MF01 each churn phase must schedule at least one table")
        # Hard starts with the same table mix for every relation. This makes a
        # single early pg_stat snapshot non-diagnostic; the configured weighted
        # schedule becomes active only after the baseline window.
        self._baseline_churn_schedule = tuple(self.tables)
        self.target_reloptions = tuple(str(value) for value in config["target_reloptions"])
        self.normal_reloptions = tuple(str(value) for value in config["normal_reloptions"])
        self.normal_reloptions_by_table = {
            _validate_sql_identifier(str(table), "reloptions table"): tuple(str(value) for value in options)
            for table, options in config.get("normal_reloptions_by_table", ())
        }
        self.pgbench_clients = max(int(config.get("pgbench_clients", 0)), 0)
        self.replay_churn_multiplier = float(config["replay_churn_multiplier"])
        self._public_history = self._metric_provider is not None or str(config.get("history_mode", "")).casefold() == "public"

    @property
    def public_history_mode(self) -> bool:
        return self._public_history

    def _hidden(self):
        hidden = getattr(self.env, "metrics_hidden", None)
        return hidden() if callable(hidden) else contextlib.nullcontext()

    def _sql(self, statement: str, context: str) -> object:
        return _require_sql_success(self.env.execute_sql(statement), context)

    def _options_for_table(self, table: str) -> tuple[str, ...]:
        return (
            self.target_reloptions
            if table == self.target_table
            else self.normal_reloptions_by_table.get(table, self.normal_reloptions)
        )

    def _drop_objects(self) -> None:
        self._stop_runtime()
        objects = (*self.tables, "pgbench_accounts", "pgbench_branches", "pgbench_history", "pgbench_tellers")
        if not self._public_history:
            objects += (self.history_table, f"{self.history_table}_run_state", self.latency_table)
        for table in objects:
            self._sql(f"DROP TABLE IF EXISTS {table} CASCADE;", f"drop PG-HC-MF01 object {table}")

    def _create_objects(self) -> None:
        for table in self.tables:
            self._sql(
                f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id bigint PRIMARY KEY,
                    account_id bigint NOT NULL,
                    status text NOT NULL,
                    payload text NOT NULL,
                    updated_at timestamptz NOT NULL
                );
                CREATE INDEX IF NOT EXISTS {table}_updated_at_idx ON {table}(updated_at);
                TRUNCATE {table};
                """,
                f"create business table and symmetric maintenance index {table}",
            )
        if not self._public_history:
            self._sql(
                f"""
            CREATE TABLE IF NOT EXISTS {self.history_table} (
                observed_at timestamptz NOT NULL,
                run_id text NOT NULL,
                case_id text NOT NULL,
                provenance text NOT NULL,
                table_name text NOT NULL,
                n_tup_ins bigint NOT NULL,
                n_tup_upd bigint NOT NULL,
                n_tup_del bigint NOT NULL,
                n_dead_tup bigint NOT NULL,
                last_autovacuum timestamptz,
                last_vacuum timestamptz,
                vacuum_start timestamptz,
                vacuum_end timestamptz,
                vacuum_duration_ms numeric,
                progress_phase text,
                heap_blks_scanned bigint,
                heap_blks_total bigint,
                remain_tuples bigint,
                oldest_xmin bigint,
                io_read_ms numeric,
                io_write_ms numeric,
                oltp_p95_ms numeric,
                oltp_p99_ms numeric,
                oltp_success_rate numeric
            );
            TRUNCATE {self.history_table};
            CREATE INDEX IF NOT EXISTS {self.history_table}_time_idx ON {self.history_table}(observed_at, table_name);
            """,
                "create observation history",
            )
            self._sql(
                f"""
            CREATE TABLE IF NOT EXISTS {self.latency_table} (
                observed_at timestamptz NOT NULL,
                operation text NOT NULL,
                latency_ms numeric NOT NULL,
                success boolean NOT NULL,
                provenance text NOT NULL
            );
            TRUNCATE {self.latency_table};
            """,
                "create OLTP latency samples",
            )
        for table in self.tables:
            rows = self.target_rows if table == self.target_table else self.decoy_rows
            self._sql(
                f"""
                INSERT INTO {table}(id, account_id, status, payload, updated_at)
                SELECT gs, gs % 1000, 'open', repeat(md5(gs::text), 4), clock_timestamp()
                FROM generate_series(1, {rows}) AS gs;
                ANALYZE {table};
                """,
                f"seed real rows for {table}",
            )
            options = self._options_for_table(table)
            self._sql(f"ALTER TABLE {table} SET ({', '.join(options)});", f"set reloptions for {table}")
        if not self._public_history:
            self._sql(
                f"""
            CREATE TABLE {self.history_table}_run_state (
                run_id text PRIMARY KEY,
                created_at timestamptz NOT NULL,
                fault_ready_at timestamptz
            );
            INSERT INTO {self.history_table}_run_state
                (run_id, created_at, fault_ready_at)
            VALUES ({self._literal(self.run_id)}, clock_timestamp(), clock_timestamp());
            """,
                "record fault-ready state",
            )

    def _verify_persistent_state(self) -> None:
        state_sql = (
            f"SELECT "
            f"(SELECT count(*) FROM pg_stat_user_tables WHERE relname IN ({','.join(self._literal(t) for t in self.tables)})), "
            + (f"(SELECT count(*) FROM {self.history_table}_run_state), " if not self._public_history else "1, ")
            + f"(SELECT count(*) FROM {self.target_table}), "
            f"(SELECT reloptions FROM pg_class WHERE oid={self._literal(self.target_table)}::regclass);"
        )
        payload = _json_object(self.env.execute_sql(state_sql), "verify PG-HC-MF01 persistent state")
        row = payload.get("result", [[]])[0]
        if len(row) < 4 or int(row[0]) != len(self.tables) or int(row[1]) != 1 or int(row[2]) <= 0:
            raise RuntimeError(f"PG-HC-MF01 fault state is incomplete: result={row!r}")

    def _adopt_run_state(self) -> None:
        """Bind a reusable fault snapshot's state row to the current CaseRun."""
        if not self._public_history:
            self._sql(
                f"TRUNCATE {self.history_table}, {self.latency_table}; "
                f"ALTER TABLE {self.history_table}_run_state DROP COLUMN IF EXISTS case_id, "
                "DROP COLUMN IF EXISTS target_table, DROP COLUMN IF EXISTS initial_dead_tup, "
                "DROP COLUMN IF EXISTS initial_reloptions; "
                f"UPDATE {self.history_table}_run_state SET run_id={self._literal(self.run_id)}, "
                "fault_ready_at=clock_timestamp();",
                "adopt PG-HC-MF01 run state",
            )
        # A fault-image cache may predate a case-contract calibration change.
        # Reapply the immutable case reloptions so activation is idempotent and
        # the evaluator observes the current target/protected-table contract.
        for table in self.tables:
            self._sql(
                f"ALTER TABLE {table} SET ({', '.join(self._options_for_table(table))});",
                f"reapply PG-HC-MF01 reloptions for {table}",
            )

    def _supports_runtime_connections(self) -> bool:
        return all(
            isinstance(getattr(self.env, name, None), expected)
            for name, expected in (
                ("host", str),
                ("port", int),
                ("user", str),
                ("password", str),
                ("dbname", str),
            )
        )

    def _connect(self, application_name: str):
        import psycopg2

        connection = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name=application_name,
        )
        connection.autocommit = True
        return connection

    def _prepare_pgbench(self) -> None:
        if self.pgbench_clients <= 0:
            return
        deployment = getattr(self.env, "deployment", None)
        container = getattr(deployment, "container_name", None)
        if not container:
            return
        result = subprocess.run(
            ["docker", "exec", container, "pgbench", "-U", self.env.user, "-d", self.env.dbname, "-i", "-s", "1"],
            check=False,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "pgbench initialization failed: "
                f"stdout={result.stdout[-2000:]!r} stderr={result.stderr[-4000:]!r}"
            )

    def _start_pgbench(self) -> None:
        if self.pgbench_clients <= 0 or os.environ.get("AIOPSBENCH_DISABLE_PGBENCH") == "1":
            return
        deployment = getattr(self.env, "deployment", None)
        container = getattr(deployment, "container_name", None)
        if not container:
            return
        self._pgbench_process = subprocess.Popen(
            [
                "docker", "exec", container, "pgbench", "-U", self.env.user,
                "-d", self.env.dbname, "-c", str(self.pgbench_clients),
                "-j", str(min(self.pgbench_clients, 2)), "-T", "3600", "-P", "5",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

    def _in_baseline(self) -> bool:
        return self._baseline_until > time.monotonic()

    def _wait_for_dynamic_phase(self) -> bool:
        while not self._stop.is_set():
            remaining = self._baseline_until - time.monotonic()
            if remaining <= 0:
                return True
            self._stop.wait(min(remaining, 0.25))
        return False

    def _delayed_pgbench_loop(self) -> None:
        if self._wait_for_dynamic_phase():
            self._start_pgbench()

    def _replay_scaled_plan(
        self,
        schedule: tuple[str, ...],
        batch_sizes: tuple[int, ...],
        working_set_rows: tuple[int, ...],
    ) -> tuple[tuple[str, ...], tuple[int, ...], tuple[int, ...]]:
        """Scale the target relation's churn batch for the trusted acceptance replay.

        The replay models the announced next write window. Only the fault-active,
        post-baseline plan is scaled, so the normal capture, the live fault
        capture and the frozen history keep their documented strength.
        """
        if not (self._replay_capture and self._fault_active):
            return schedule, batch_sizes, working_set_rows
        target_index = self.tables.index(self.target_table)
        scaled = list(batch_sizes)
        scaled[target_index] = round(batch_sizes[target_index] * self.replay_churn_multiplier)
        return schedule, tuple(scaled), working_set_rows

    def _current_churn_plan(self) -> tuple[tuple[str, ...], tuple[int, ...], tuple[int, ...]]:
        if not self._fault_active:
            # A short healthy-neighbor burst is captured during the normal
            # window. It raises one visible raw signal without creating a
            # sustained backlog deficit. The target also gets a longer,
            # recoverable burst so target identity alone is not causal proof.
            elapsed = max(time.monotonic() - self._runtime_started, 0.0)
            if self._public_history and 80.0 <= elapsed % 120.0 < 120.0:
                return (
                    (self.target_table,) * 8 + (self.tables[1], self.decoy_tables[0]),
                    (80, 5, 5),
                    self.churn_baseline_working_set_rows,
                )
            # Repeat the bounded burst so a normal capture that starts after
            # the runtime warmup still contains real deviation, regardless of
            # the wall-clock alignment chosen by the history sampler.
            if self._public_history and 20.0 <= elapsed % 120.0 < 80.0:
                burst_batch_sizes = list(self.churn_baseline_batch_sizes)
                # Keep the neighbor burst visible without making the
                # protected decoy relation itself exceed its bounded-health
                # contract during the short frozen-history capture.
                burst_batch_sizes[self.tables.index(self.decoy_tables[0])] = (
                    10 if self.case_id.endswith("_simple") else 100
                )
                return (
                    (self.decoy_tables[0],) * 8 + (self.tables[1],),
                    # Make the captured benign window statistically visible
                    # over its full 60-second source block. The decoy still
                    # receives the planned VACUUM loop and must recover.
                    tuple(burst_batch_sizes),
                    self.churn_baseline_working_set_rows,
                )
            return (
                self._baseline_churn_schedule,
                self.churn_baseline_batch_sizes,
                self.churn_baseline_working_set_rows,
            )
        if self._in_baseline():
            return (
                self._baseline_churn_schedule,
                self.churn_baseline_batch_sizes,
                self.churn_baseline_working_set_rows,
            )
        if not self._churn_phase_schedules:
            return self._replay_scaled_plan(
                self._churn_schedule, self.churn_batch_sizes, self.churn_working_set_rows
            )
        elapsed = max(time.monotonic() - self._baseline_until, 0.0)
        phase_index = int(elapsed // self.churn_phase_seconds) % len(self._churn_phase_schedules)
        return self._replay_scaled_plan(
            self._churn_phase_schedules[phase_index],
            self.churn_phase_batch_sizes[phase_index],
            self.churn_phase_working_set_rows[phase_index],
        )

    def _churn_loop(self, worker_id: int) -> None:
        connection = None
        try:
            connection = self._connect(f"pg-hc-mf01-churn-{self.case_id}-{worker_id}")
            cycle = 0
            table_cycles = {table: 0 for table in self.tables}
            while not self._stop.is_set():
                schedule, batch_sizes, working_set_rows = self._current_churn_plan()
                table = schedule[(cycle + worker_id) % len(schedule)]
                table_index = self.tables.index(table)
                batch_size = batch_sizes[table_index]
                working_set = working_set_rows[table_index]
                start = time.monotonic()
                success = False
                try:
                    with connection.cursor() as cursor:
                        offset = (
                            (table_cycles[table] * batch_size)
                            + (worker_id * batch_size * 7)
                        ) % max(working_set - batch_size, 1)
                        # Keep tuple generation symmetric while making the
                        # full-table path visit scattered heap pages. This is
                        # a deterministic business-update pattern, not a
                        # target-only workload multiplier.
                        row_order = (
                            f"md5(id::text || '{self.case_id}:distributed')"
                            if working_set >= 30000
                            else "id"
                        )
                        cursor.execute(
                            f"UPDATE {table} SET payload=md5(clock_timestamp()::text || id::text), updated_at=clock_timestamp() "
                            f"WHERE id IN (SELECT id FROM {table} ORDER BY {row_order} "
                            f"OFFSET {offset} LIMIT {batch_size})"
                        )
                    success = True
                    table_cycles[table] += 1
                except Exception:
                    try:
                        connection.rollback()
                    except Exception:
                        pass
                elapsed_ms = round((time.monotonic() - start) * 1000.0, 3)
                if not self._public_history:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"INSERT INTO {self.latency_table}(observed_at, operation, latency_ms, success, provenance) VALUES (clock_timestamp(), %s, %s, %s, %s)",
                            ("pgbench_like_oltp", elapsed_ms, success, f"injector:{self.run_id}:churn:{worker_id}"),
                        )
                if self._metric_provider is not None:
                    timestamp_ms = (int(time.time() * 1000) // 2000) * 2000
                    self._metric_provider.record_latency(timestamp_ms, elapsed_ms, success)
                    self._metric_provider.record_event(timestamp_ms, {
                        "event_type": "churn_job",
                        "entity_type": "table",
                        "entity": table,
                        "action": "update",
                        "status": "success" if success else "failed",
                        "correlation_id": f"{self.run_id}:churn:{worker_id}",
                        "application_name": f"pg-hc-mf01-churn-{self.case_id}-{worker_id}",
                        "rows": int(batch_size) if success else 0,
                        "duration_ms": elapsed_ms,
                    })
                cycle += 1
                self._stop.wait(self.churn_interval_seconds)
        finally:
            if connection is not None:
                connection.close()

    def _maintenance_loop(self) -> None:
        connection = None
        try:
            connection = self._connect(f"pg-hc-mf01-planned-vacuum-{self.case_id}")
            if not self._wait_for_dynamic_phase():
                return
            index = 0
            while not self._stop.wait(9.0):
                # Capture recovery for both real normal bursts. Once the
                # fault is active, keep maintenance on the configured decoy
                # only so the target retains its capacity deficit.
                normal_capture_tables = (
                    (self.target_table, *self.planned_vacuum_tables)
                    if self._public_history and not self._fault_active
                    else self.planned_vacuum_tables
                )
                candidates = normal_capture_tables or self.tables
                table = candidates[index % len(candidates)]
                index += 1
                vacuum_succeeded = False
                try:
                    with connection.cursor() as cursor:
                        # Keep a bounded burst of real short transactions in
                        # the maintenance signal without holding an xmin. The
                        # planned-VACUUM decoy also creates a small, real dead
                        # tuple set so the 2-second observer can see removal.
                        cursor.execute("BEGIN")
                        if self.planned_vacuum_tables:
                            cursor.execute(
                                f"UPDATE {table} SET payload=md5(clock_timestamp()::text || id::text), "
                                f"updated_at=clock_timestamp() WHERE id IN "
                                # Keep the captured healthy-neighbor maintenance
                                # sustainable over the public 120-second replay
                                # window; the target workload remains unchanged.
                                f"(SELECT id FROM {table} ORDER BY id LIMIT 50)"
                            )
                        else:
                            cursor.execute(f"SELECT count(*) FROM {table} WHERE id > 0")
                        cursor.execute("COMMIT")
                        if self.planned_vacuum_tables:
                            cursor.execute(f"VACUUM (VERBOSE, ANALYZE) {table}")
                            vacuum_succeeded = True
                except Exception:
                    try:
                        connection.rollback()
                    except Exception:
                        pass
                if self._metric_provider is not None and self.planned_vacuum_tables:
                    timestamp_ms = (int(time.time() * 1000) // 2000) * 2000
                    self._metric_provider.record_event(timestamp_ms, {
                        "event_type": "vacuum",
                        "entity_type": "table",
                        "entity": table,
                        "action": "run",
                        "status": "success" if vacuum_succeeded else "failed",
                        "correlation_id": f"{self.run_id}:planned-vacuum:{index}",
                        "application_name": f"pg-hc-mf01-planned-vacuum-{self.case_id}",
                    })
                if index % 3 == 0:
                    self._run_backup_noise()
        finally:
            if connection is not None:
                connection.close()

    def _run_backup_noise(self) -> None:
        """Take a real bounded logical backup of this case's relations."""
        deployment = getattr(self.env, "deployment", None)
        container = getattr(deployment, "container_name", None)
        if not container:
            return
        backup_path = f"/tmp/pg-hc-mf01-{self.case_id}-maintenance.dump"
        command = [
            "docker", "exec", container, "pg_dump", "-U", self.env.user,
            "-d", self.env.dbname, "--format=custom", "--file", backup_path,
        ]
        for table in self.tables:
            command.extend(("--table", f"public.{table}"))
        try:
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=5)
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return
        subprocess.run(
            ["docker", "exec", container, "rm", "-f", backup_path],
            check=False,
            capture_output=True,
            text=True,
        )

    def _sampling_loop(self) -> None:
        connection = None
        try:
            connection = self._connect(f"pg-hc-mf01-observer-{self.case_id}")
            interval_ms = 2000
            next_timestamp_ms = (int(time.time() * 1000) // interval_ms + 1) * interval_ms
            while not self._stop.is_set():
                remaining = next_timestamp_ms / 1000.0 - time.time()
                if remaining > 0 and self._stop.wait(remaining):
                    return
                if self._stop.is_set():
                    return
                self._sample_once(connection, next_timestamp_ms)
                next_timestamp_ms += interval_ms
        finally:
            if connection is not None:
                connection.close()

    def _sample_once(self, connection, timestamp_ms: int | None = None) -> None:
        now = dt.datetime.now(dt.timezone.utc)
        timestamp_ms = timestamp_ms or (int(now.timestamp() * 1000) // 2000) * 2000
        quoted = ",".join(self._literal(table) for table in self.tables)
        relation_values: dict[str, dict[str, float]] = {}
        cleanup_values: dict[str, dict[str, float]] = {}
        backlog_values: dict[str, dict[str, float]] = {}
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT relname, n_live_tup, n_tup_ins, n_tup_upd, n_tup_hot_upd, n_tup_del, n_dead_tup, last_autovacuum, last_vacuum "
                f"FROM pg_stat_user_tables WHERE relname IN ({quoted}) ORDER BY relname"
            )
            table_rows = cursor.fetchall()
            cursor.execute(
                "SELECT relid::regclass::text, phase, heap_blks_scanned, heap_blks_total, num_dead_tuples "
                "FROM pg_stat_progress_vacuum"
            )
            progress = {str(row[0]).split(".")[-1].strip('"'): row for row in cursor.fetchall()}
            cursor.execute(
                "SELECT coalesce(max(extract(epoch FROM clock_timestamp() - xact_start)), 0) "
                "FROM pg_stat_activity WHERE backend_xmin IS NOT NULL AND xact_start IS NOT NULL"
            )
            oldest_xmin_age_sec = float(cursor.fetchone()[0] or 0.0)
            try:
                cursor.execute(
                    "SELECT coalesce(sum(read_bytes),0), coalesce(sum(write_bytes),0), "
                    "coalesce(sum(read_time),0), coalesce(sum(write_time),0) FROM pg_stat_io"
                )
                io_read_bytes, io_write_bytes, io_read_ms, io_write_ms = cursor.fetchone()
            except Exception:
                connection.rollback()
                io_read_bytes = io_write_bytes = io_read_ms = io_write_ms = 0
            if self._metric_provider is not None:
                service = self._metric_provider.service_snapshot(timestamp_ms)
                p95 = p99 = service["p99_ms"]
                success_rate = service["success_ratio"]
            else:
                cursor.execute(
                    f"SELECT percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms), "
                    f"percentile_cont(0.99) WITHIN GROUP (ORDER BY latency_ms), "
                    f"coalesce(avg(success::int), 1) FROM {self.latency_table} "
                    "WHERE observed_at >= clock_timestamp() - interval '30 seconds'"
                )
                p95, p99, success_rate = cursor.fetchone()
            previous_io = self._previous_io_sample
            io_interval = 2.0
            if previous_io is not None:
                io_interval = max((timestamp_ms - self._previous_table_samples.get("__io__", (timestamp_ms,))[0]) / 1000.0, 0.001)
            io_values = {
                "read_mb_per_sec": max(float(io_read_bytes or 0) - float(previous_io[0] if previous_io else io_read_bytes or 0), 0.0) / io_interval / (1024 * 1024),
                "write_mb_per_sec": max(float(io_write_bytes or 0) - float(previous_io[1] if previous_io else io_write_bytes or 0), 0.0) / io_interval / (1024 * 1024),
                "io_time_ms_per_sec": max(
                    float(io_read_ms or 0) + float(io_write_ms or 0)
                    - float(previous_io[2] + previous_io[3] if previous_io else float(io_read_ms or 0) + float(io_write_ms or 0)),
                    0.0,
                ) / io_interval,
            }
            self._previous_io_sample = (
                float(io_read_bytes or 0), float(io_write_bytes or 0),
                float(io_read_ms or 0), float(io_write_ms or 0),
            )
            self._previous_table_samples["__io__"] = (timestamp_ms,)
            for row in table_rows:
                table, live, inserted, updated, hot_updated, deleted, dead, last_autovacuum, last_vacuum = row
                table = str(table)
                live = int(live or 0)
                inserted = int(inserted or 0)
                updated = int(updated or 0)
                hot_updated = int(hot_updated or 0)
                deleted = int(deleted or 0)
                dead = int(dead or 0)
                progress_row = progress.get(table)
                active = progress_row is not None
                scanned = progress_row[2] if progress_row else None
                total = progress_row[3] if progress_row else None
                previous = self._previous_table_samples.get(table)
                interval_seconds = max((timestamp_ms - previous[0]) / 1000.0, 0.001) if previous else 2.0
                inserted_delta = max(inserted - (previous[2] if previous else inserted), 0)
                updated_delta = max(updated - (previous[3] if previous else updated), 0)
                hot_updated_delta = max(hot_updated - (previous[4] if previous else hot_updated), 0)
                deleted_delta = max(deleted - (previous[5] if previous else deleted), 0)
                generation = inserted_delta + updated_delta + deleted_delta
                advanced = (
                    previous is not None
                    and ((last_autovacuum is not None and last_autovacuum != previous[7])
                         or (last_vacuum is not None and last_vacuum != previous[8]))
                )
                removal = max((previous[6] if previous else dead) + generation - dead, 0) if advanced else 0
                if active:
                    self._vacuum_started.setdefault(table, now)
                elif table in self._vacuum_started:
                    self._vacuum_started.pop(table)
                scanned_delta = (
                    max(float(scanned) - float(previous[9]), 0.0)
                    if scanned is not None and previous and previous[9] is not None else 0.0
                )
                self._previous_table_samples[table] = (
                    timestamp_ms, live, inserted, updated, hot_updated, deleted, dead,
                    last_autovacuum, last_vacuum, int(scanned) if scanned is not None else None,
                )
                relation_values[table] = {
                    "updated_tps": updated_delta / interval_seconds,
                    "deleted_tps": deleted_delta / interval_seconds,
                    "inserted_tps": inserted_delta / interval_seconds,
                    "hot_update_ratio": min(hot_updated_delta / max(updated_delta, 1), 1.0),
                }
                cleanup_values[table] = {
                    "removed_tps": removal / interval_seconds,
                    "active_workers": 1.0 if active else 0.0,
                    "heap_blocks_scanned_per_sec": scanned_delta / interval_seconds,
                }
                backlog_values[table] = {
                    "estimated_dead_tuples": float(dead),
                    "estimated_live_tuples": float(live),
                }
                if self._metric_provider is not None and advanced:
                    self._metric_provider.record_event(timestamp_ms, {
                        "event_type": "vacuum",
                        "entity_type": "table",
                        "entity": table,
                        "action": "finish",
                        "status": "success",
                        "correlation_id": f"{self.run_id}:vacuum:{table}:{timestamp_ms}",
                        "duration_ms": 0.0,
                        "tuples_removed": float(removal),
                        "tuples_remaining": float(dead),
                    })
                if not self._public_history:
                    cursor.execute(
                        f"""
                    INSERT INTO {self.history_table}(
                        observed_at, run_id, case_id, provenance, table_name,
                        n_tup_ins, n_tup_upd, n_tup_del, n_dead_tup,
                        last_autovacuum, last_vacuum, vacuum_start, vacuum_end, vacuum_duration_ms,
                        progress_phase, heap_blks_scanned, heap_blks_total,
                        remain_tuples, oldest_xmin, io_read_ms,
                        io_write_ms, oltp_p95_ms, oltp_p99_ms, oltp_success_rate
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                              %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                        now, self.run_id, self.case_id, f"injector:{self.run_id}:sampler", table,
                        int(inserted or 0), int(updated or 0), int(deleted or 0), dead,
                        last_autovacuum, last_vacuum, None, None, None,
                        progress_row[1] if progress_row else None, scanned, total, progress_row[4] if progress_row else dead,
                        None, io_read_ms, io_write_ms,
                        p95, p99, success_rate,
                        ),
                    )
            if self._metric_provider is not None:
                self._metric_provider.append_sample(timestamp_ms, {
                    "relation_churn": relation_values,
                    "vacuum_cleanup": cleanup_values,
                    "dead_tuple_backlog": backlog_values,
                    "maintenance_io": {"postgres": io_values},
                    "oltp_service": {"checkout": {
                        "transactions_per_sec": service["transactions_per_sec"],
                        "p99_ms": service["p99_ms"],
                        "success_ratio": service["success_ratio"],
                    }},
                    "xmin_horizon": {"postgres": {
                        "oldest_xmin_age_sec": oldest_xmin_age_sec,
                        "blocked_vacuum_workers": float(sum(1 for row in progress.values() if row[1] not in ("vacuuming heap", "vacuuming indexes"))),
                    }},
                })
                if self._replay_capture:
                    self._replay_samples.append({
                        "timestamp_ms": timestamp_ms,
                        "relation_churn": relation_values,
                        "vacuum_cleanup": cleanup_values,
                        "dead_tuple_backlog": backlog_values,
                        "oltp_service": {"checkout": dict(service)},
                    })

    def _start_runtime(self, *, fault_active: bool | None = None) -> None:
        self._stop_runtime()
        self._stop.clear()
        self._vacuum_started.clear()
        self._baseline_until = time.monotonic() + self.churn_baseline_seconds
        self._runtime_started = time.monotonic()
        if fault_active is not None:
            self._fault_active = fault_active
        elif not self._public_history:
            self._fault_active = True
        if not self._supports_runtime_connections():
            return
        self._prepare_pgbench()
        for worker_id in range(self.churn_workers):
            thread = threading.Thread(target=self._churn_loop, args=(worker_id,), daemon=True, name=f"pg-hc-mf01-churn-{worker_id}")
            thread.start()
            self._threads.append(thread)
        for target, name in ((self._sampling_loop, "pg-hc-mf01-sampler"), (self._maintenance_loop, "pg-hc-mf01-maintenance")):
            thread = threading.Thread(target=target, daemon=True, name=name)
            thread.start()
            self._threads.append(thread)
        pgbench_thread = threading.Thread(
            target=self._delayed_pgbench_loop,
            daemon=True,
            name="pg-hc-mf01-pgbench-starter",
        )
        pgbench_thread.start()
        self._threads.append(pgbench_thread)

    def _stop_runtime(self) -> None:
        self._stop.set()
        for thread in self._threads:
            thread.join(timeout=8)
        self._threads.clear()
        process = self._pgbench_process
        self._pgbench_process = None
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        self._baseline_until = 0.0

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure({**context.config, "run_id": context.run_id, "case_id": context.case_id}, context.env)
        if self._public_history and self._prepared_for_history:
            self._verify_persistent_state()
            self._fault_active = True
            self._baseline_until = time.monotonic() + self.churn_baseline_seconds
            return
        with self._hidden():
            self._drop_objects()
            self._create_objects()
        self._verify_persistent_state()
        self._start_runtime()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure({**context.config, "run_id": context.run_id, "case_id": context.case_id}, context.env)
        self._verify_persistent_state()
        self._adopt_run_state()
        # Public metric-history runs prepare a benign capture first.  The
        # activation phase must explicitly switch to the target fault; the
        # generic _start_runtime() path preserves the existing public-history
        # flag and otherwise leaves the injector in benign mode.
        self._start_runtime(fault_active=True)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._verify_persistent_state()
        evidence = {
            "fault_ready": True,
            "observability": ("dml_counter_delta", "dead_tuples", "vacuum_progress", "oldest_xmin", "device_io", "oltp_p99"),
        }
        if not self._public_history:
            evidence.update({
                "history_table": self.history_table,
                "provenance": f"injector:{context.run_id}:sampler",
            })
        return evidence

    def prepare_metric_history(self, context: FaultLifecycleContext) -> None:
        self._configure({**context.config, "run_id": context.run_id, "case_id": context.case_id}, context.env)
        self._metric_provider = PgAutovacuumMetricProvider(self.tables)
        self._public_history = True
        attach = getattr(self.env, "attach_scenario_metric_provider", None)
        if not callable(attach):
            raise RuntimeError("PG-HC-MF01 public history requires scenario metric provider support")
        attach(self._metric_provider)
        with self._hidden():
            self._drop_objects()
            self._create_objects()
        self._verify_persistent_state()
        self._fault_active = False
        self._prepared_for_history = True
        self._start_runtime(fault_active=False)

    def run_acceptance_replay(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        """Run a trusted target/peer replay and retain only raw in-memory evidence."""
        if not self._public_history or self._metric_provider is None:
            raise RuntimeError("PG-HC-MF01 trusted replay requires public history mode")
        if self._replay_artifact is not None:
            return self._replay_artifact
        self._stop_runtime()
        self._previous_table_samples.clear()
        self._previous_io_sample = None
        self._replay_samples.clear()
        self._replay_capture = True
        self._start_runtime(fault_active=True)
        self._baseline_until = time.monotonic() + 4.0
        try:
            # The replay window is part of the public Case contract. Do not
            # shorten it here, or a valid target-level policy can be judged on
            # a different write horizon than the one documented to the Agent.
            time.sleep(max(12.0, float(context.case.replay_history_seconds)))
        finally:
            self._stop_runtime()
            self._replay_capture = False

        by_table: dict[str, list[dict[str, object]]] = {table: [] for table in self.tables}
        for sample in self._replay_samples:
            for table in self.tables:
                by_table[table].append({
                    "timestamp_ms": sample["timestamp_ms"],
                    "churn": sample["relation_churn"][table],
                    "cleanup": sample["vacuum_cleanup"][table],
                    "backlog": sample["dead_tuple_backlog"][table],
                })
        relations: dict[str, dict[str, object]] = {}
        for table, samples in by_table.items():
            if not samples:
                relations[table] = {"samples": 0, "bounded": False, "generation_delta": 0.0, "removal_delta": 0.0}
                continue
            generation = sum(
                sum(float(item["churn"].get(field, 0.0)) for field in ("updated_tps", "deleted_tps", "inserted_tps")) * 2.0
                for item in samples[1:]
            )
            removal = sum(float(item["cleanup"].get("removed_tps", 0.0)) * 2.0 for item in samples[1:])
            first_dead = float(samples[0]["backlog"].get("estimated_dead_tuples", 0.0))
            last_dead = float(samples[-1]["backlog"].get("estimated_dead_tuples", 0.0))
            relations[table] = {
                "samples": len(samples),
                "first_dead": first_dead,
                "last_dead": last_dead,
                "generation_delta": generation,
                "removal_delta": removal,
                "removed_tuples": removal,
                "bounded": last_dead <= first_dead + float(context.case.max_backlog_growth),
            }
        service_samples = [sample["oltp_service"]["checkout"] for sample in self._replay_samples]
        service = service_samples[-1] if service_samples else {"p99_ms": float("inf"), "success_ratio": 0.0}
        self._replay_artifact = {
            "relations": relations,
            "service": {
                "p99_ms": float(service.get("p99_ms", float("inf"))),
                "success_ratio": float(service.get("success_ratio", 0.0)),
                "transactions_per_sec": float(service.get("transactions_per_sec", 0.0)),
            },
            "sample_count": len(self._replay_samples),
        }
        return self._replay_artifact

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime()

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure({**context.config, "run_id": context.run_id, "case_id": context.case_id}, context.env)
        self._stop_runtime()
        failures = []
        try:
            if hasattr(self.env, "reconnect"):
                self.env.reconnect()
            # Cleanup is injector-owned current-state SQL. It must bypass the
            # Agent-facing historical-read guard while remaining invisible to
            # the public tool surface.
            trusted_execute = getattr(self.env, "execute_sql_trusted", self.env.execute_sql)
            for table in self.tables:
                _require_sql_success(
                    trusted_execute(
                        f"ALTER TABLE IF EXISTS {table} RESET (autovacuum_enabled, autovacuum_vacuum_scale_factor, autovacuum_vacuum_threshold, autovacuum_vacuum_cost_limit, autovacuum_vacuum_cost_delay);"
                    ),
                    f"reset reloptions for {table}",
                )
            self._drop_objects()
        except Exception as exc:
            failures.append(("recover PG-HC-MF01 objects", exc))
        if failures:
            _run_cleanup_steps("PG-HC-MF01 cleanup", ((name, lambda exc=exc: (_ for _ in ()).throw(exc)) for name, exc in failures))


class PgHealthCheckAutovacuumSustainabilityScenario(PostgresScenario):
    scenario_id = "pg_health_check_autovacuum_sustainability"
    description = "Audits whether PostgreSQL autovacuum cleanup capacity remains sustainable under real churn."
    cases = (_HARD_CASE, _SIMPLE_CASE)

    def build_fault_plan(self, case: PgHealthCheckAutovacuumSustainabilityCase) -> tuple[FaultPlan, ...]:
        if case not in self.cases:
            raise ValueError(f"Unknown PG-HC-MF01 case: {case.case_id}")
        return (
            FaultPlan(
                injector_type=PgHealthCheckAutovacuumSustainabilityInjector,
                config={
                    "case_id": case.case_id,
                    "tables": case.tables,
                    "target_table": case.target_table,
                    "decoy_tables": case.decoy_tables,
                    "history_table": case.history_table,
                    "latency_table": case.latency_table,
                    "target_rows": case.target_rows,
                    "decoy_rows": case.decoy_rows,
                    "churn_workers": case.churn_workers,
                    "churn_interval_seconds": case.churn_interval_seconds,
                    "churn_baseline_seconds": case.churn_baseline_seconds,
                    "churn_weights": case.churn_weights,
                    "churn_batch_sizes": case.churn_batch_sizes,
                    "churn_baseline_batch_sizes": case.churn_baseline_batch_sizes,
                    "churn_working_set_rows": case.churn_working_set_rows,
                    "churn_baseline_working_set_rows": case.churn_baseline_working_set_rows,
                    "churn_phase_seconds": case.churn_phase_seconds,
                    "churn_phase_weights": case.churn_phase_weights,
                    "churn_phase_batch_sizes": case.churn_phase_batch_sizes,
                    "churn_phase_working_set_rows": case.churn_phase_working_set_rows,
                    "planned_vacuum_tables": case.planned_vacuum_tables,
                    "target_reloptions": case.target_reloptions,
                    "normal_reloptions": case.normal_reloptions,
                    "normal_reloptions_by_table": case.normal_reloptions_by_table,
                    "pgbench_clients": case.pgbench_clients,
                    "replay_churn_multiplier": case.replay_churn_multiplier,
                },
            ),
        )


__all__ = (
    "PgHealthCheckAutovacuumSustainabilityCase",
    "PgHealthCheckAutovacuumSustainabilityForCapacityDeficitScenarioCase",
    "PgHealthCheckAutovacuumSustainabilityForCapacityDeficitSimpleScenarioCase",
    "PgHealthCheckAutovacuumSustainabilityInjector",
    "PgHealthCheckAutovacuumSustainabilityScenario",
)
