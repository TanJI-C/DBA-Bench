"""Frozen-history RG05: diagnose a Lightning budget from frozen temporal evidence."""

from __future__ import annotations

from dataclasses import dataclass, replace
import threading
from typing import Mapping

from src.execution.deployment import lightning_job_id
from src.execution.history.records import HistoricalRecordSource
from src.scenarios.tidb.common import BaseFaultInjector, FaultLifecycleContext, json_object, require_sql_success
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)
from src.scenarios.workloads import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase

from src.scenarios.evaluation.tidb.resource_governance.lightning_budget_frozen_history import (
    TidbResourceGovernanceLightningBudgetFrozenHistoryEvaluatorCase,
    TidbResourceGovernanceLightningBudgetHistoryInvestigationEvaluatorCase,
)

from ...base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from ..runtime import TIDB_V8_1_0, tidb_runtime
from .lightning_budget import (
    LightningBudgetController,
    build_lightning_budget_noise_profiles,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceLightningBudgetFrozenHistoryForBudgetCalibrationScenarioCase(TiDBScenarioCase):
    db: str
    import_table: str
    business_table: str
    inventory_table: str
    row_count: int
    source_file_count: int
    engine_batch_size_bytes: int | None
    business_row_count: int
    inventory_row_count: int
    phase1_checkpoint_deadline_seconds: int
    checkpoint_poll_interval_seconds: int
    phase1_region_concurrency: int
    phase1_disk_quota_mb: int
    phase1_store_write_bwlimit_mib: int
    rebalance_after_rows: int
    phase2_region_concurrency_max: int
    phase2_disk_quota_mb_max: int
    phase2_store_write_bwlimit_mib_max: int
    phase2_store_write_bwlimit_mib_min: int
    frontend_min_successes: int
    settlement_window_seconds: int
    frontend_max_failures: int
    staging_table: str | None
    staging_row_count: int
    backfill_decoy: bool


def _history_spec() -> FrozenHistorySpec:
    return FrozenHistorySpec(
        schema_version=2,
        duration_seconds=43200,
        normal_capture_seconds=60,
        fault_capture_seconds=840,
        base_step_seconds=2,
        overview_step_seconds=60,
        block_min_seconds=10,
        block_max_seconds=30,
        transition_seconds=10,
        target_age_seconds_range=(30000, 36000),
        required_metrics=(
            "lightning_progress",
            "lightning_throughput",
            "lightning_workers",
            "workload_profile",
            "query_latency",
            "cpu",
            "disk_io",
            "disk_usage",
        ),
        record_sources=(
            HistoricalRecordSource.COMPONENT_LOG,
        ),
        decoys=(
            HistoryDecoySpec(
                decoy_id="frontend-p95-history-spike",
                kind=DecoyKind.METRIC_ONLY,
                metric="workload_profile",
                field="p95_ms",
                target="checkout_recent_order_search",
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                amplitude_mad=3.0,
            ),
            HistoryDecoySpec(
                decoy_id="tikv-write-surge",
                kind=DecoyKind.METRIC_ONLY,
                metric="disk_io",
                field="write_mb_per_second",
                target="tikv/tikv-0",
                direction=DecoyDirection.SPIKE,
                count=2,
                duration_seconds=60,
                amplitude_mad=3.0,
            ),
            HistoryDecoySpec(
                decoy_id="tidb-cpu-saturation",
                kind=DecoyKind.METRIC_ONLY,
                metric="cpu",
                field="percent",
                target="tidb/tidb-0",
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                amplitude_mad=3.0,
            ),
            HistoryDecoySpec(
                decoy_id="frontend-latency-climb",
                kind=DecoyKind.METRIC_ONLY,
                metric="query_latency",
                field="p95_ms",
                target="tidb/tidb-0",
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                amplitude_mad=2.5,
            ),
        ),
        max_points_per_series=900,
        max_scalar_samples_per_response=12000,
        max_history_records_per_response=30,
        metric_targets={
            "cpu": (
                "tidb/tidb-0",
                "tidb/tidb-1",
                "tikv/tikv-0",
                "tikv/tikv-1",
                "tikv/tikv-2",
            ),
            "disk_io": ("tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"),
            "disk_usage": ("tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"),
            "query_latency": ("tidb/tidb-0", "tidb/tidb-1"),
            "lightning_progress": (None,),
            "lightning_throughput": (None,),
            "lightning_workers": (None,),
            "workload_profile": (None,),
        },
        metric_rate_windows={
            "lightning_throughput": 30,
            "query_latency": 30,
            "cpu": 30,
            "disk_io": 30,
        },
        install_before_normal_capture=True,
        activate_during_target_capture=True,
        post_target_mode="RESUME_NORMAL",
        decoy_lightning_job_count=7,
    )


_CASE = TidbResourceGovernanceLightningBudgetFrozenHistoryForBudgetCalibrationScenarioCase(
    case_id="lightning_budget_history_calibration",
    case_no=0,
    evaluator=TidbResourceGovernanceLightningBudgetFrozenHistoryEvaluatorCase,
    title=(
        "Use a bounded second-phase budget to resume one TiDB Lightning job from its checkpoint "
        "without sacrificing the live frontend SLO."
    ),
    alert=(
        "P1 resource-governance alert: last night the customer-facing Lightning import on the migration "
        "host stopped mid-flight and checkout search latency spiked at the same time; this morning the "
        "target tables are still short on data. The host controller currently shows more than one paused "
        "Lightning import job. Use the frozen historical observations to work out which paused job is the "
        "customer import that failed overnight, then resume that job only, with a legal non-zero phase2 "
        "budget within the controller's published bounds. The checkpoint handoff leaves the remaining "
        "source rows to the phase2 continuation, and every frontend SLO profile must stay online with "
        "zero failures while the continuation runs. Keep the protected business tables unchanged, leave "
        "every other paused job untouched, avoid cluster lifecycle changes, and finish with exact "
        "row-count, frontend SLO, and protected-state verification."
    ),
    initial_state={
        "schema": "benchops_mf_rg05",
        "status": "multiple_import_jobs_paused",
        "import": "the customer import stopped overnight; two paused Lightning jobs are registered",
        "precheck": "passed",
        "frontend": "normal after Lightning stopped",
        "protected_tables": "mf_rg05_business_orders and mf_rg05_inventory",
        "agent_phase": "identify the incident job from history, then phase2 only",
    },
    expected_target={
        "status": "completed",
        "import_rows": 2000000,
        "incident_job": "the paused job whose overnight history matches the frontend stall",
        "same_job_checkpoint": True,
        "precheck": True,
        "phase2_budget": "bounded and non-zero across all three dimensions",
        "phase1_checkpoint": (
            "at least half the restore chunks completed with the target table still unfinished"
        ),
        "frontend_slo": "three profiles online during the continuation, >=3 successes and 0 failures",
        "protected_tables": "unchanged aggregate and checksum",
    },
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "correct target history window and temporal causal chain",
                    "entity": "throughput and progress rise before TiKV write I/O and CPU and frontend p95 worsens later",
                    "evidence": [
                        "target Lightning history window",
                    ],
                },
                {
                    "type": "constraint",
                    "factor": "shared Lightning and TiKV pressure requires coupled region concurrency sort quota and write bandwidth bounds",
                    "entity": "all three budget dimensions jointly constrain the frontend SLO",
                    "evidence": [
                        "coupled Lightning and TiKV pressure",
                    ],
                },
                {
                    "type": "exclusion",
                    "factor": "precheck passed and the strict source format is not the root cause",
                    "entity": "precheck source and target contract are valid",
                    "evidence": [
                        "precheck passed",
                    ],
                },
                {
                    "type": "exclusion",
                    "factor": "the paused backfill job is excluded and the overnight customer import is identified from history",
                    "entity": "incident-window component records name the customer import source while the backfill job has no activity there",
                    "evidence": [
                        "incident-window component records and the job registry",
                    ],
                },
                {
                    "type": "state",
                    "factor": "the resumed checkpoint belongs to the incident job identified from history",
                    "entity": "the incident job's registry entry and its checkpoint handoff match the history evidence",
                    "evidence": [
                        "incident-window records and the job registry identify the customer import",
                    ],
                },
                {
                    "type": "state",
                    "factor": "reconfigure_required is a checkpoint handoff pause rather than import failure",
                    "entity": "current Lightning controller checkpoint handoff",
                    "evidence": [
                        "current controller stopped the same job after checkpoint handoff and preserves source and sorted directories",
                    ],
                },
            ]
        },
        "outcome": {
            "changes": [
                "Identified the overnight incident job from the frozen history and resumed its checkpoint with bounded phase2 region concurrency, disk quota, and store write bandwidth",
                "Left the paused backfill job untouched",
            ],
            "verification": [
                "Completed exactly 2000000 rows and verified all three frontend profiles plus protected table state",
            ],
        },
        "summary": "The overnight incident job's checkpoint completed under a coupled bounded phase2 budget while the paused backfill job stayed untouched and frontend and protected business invariants remained healthy.",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=build_lightning_budget_noise_profiles(
            db="benchops_mf_rg05",
            business_table="mf_rg05_business_orders",
            inventory_table="mf_rg05_inventory",
        ),
        worker_count=6,
        seed=50705,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        warmup_seconds=8,
    ),
    frozen_history=_history_spec(),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.911477,
        reference_run_ids=(
            "reference-241__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=120,
        image_group_key=None,
        bootstrap_cache_enabled=False,
    ),
    db="benchops_mf_rg05",
    import_table="mf_rg05_lightning_orders",
    business_table="mf_rg05_business_orders",
    inventory_table="mf_rg05_inventory",
    row_count=2000000,
    source_file_count=4,
    engine_batch_size_bytes=None,
    business_row_count=120000,
    inventory_row_count=20000,
    phase1_checkpoint_deadline_seconds=900,
    checkpoint_poll_interval_seconds=2,
    phase1_region_concurrency=6,
    phase1_disk_quota_mb=4096,
    phase1_store_write_bwlimit_mib=128,
    rebalance_after_rows=1000000,
    phase2_region_concurrency_max=2,
    phase2_disk_quota_mb_max=2048,
    phase2_store_write_bwlimit_mib_max=48,
    phase2_store_write_bwlimit_mib_min=16,
    frontend_min_successes=3,
    # Calibration keeps the settlement time-box non-binding: its phase2
    # continuation finishes far inside one hour, so only the investigation
    # case is governed by the box.
    settlement_window_seconds=3600,
    frontend_max_failures=0,
    staging_table=None,
    staging_row_count=0,
    backfill_decoy=True,
)

_INVESTIGATION_WORKLOAD = replace(
    _CASE.background_workload,
    profiles=_CASE.background_workload.profiles[:4],
    worker_count=4,
    seed=20260905,
)
# The settlement time-box (r4): the resumed phase2 import must finish within
# this many seconds of container runtime, so slow low-corner budgets fail the
# batch window while the frontend SLO under real load fails the saturation
# top-bound budget. Calibrated between the top-bound and low-corner import
# durations on the reference machine.
_SETTLEMENT_WINDOW_SECONDS = 240

_INVESTIGATION_REFERENCE_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "root_cause",
                "factor": "correct target history window and temporal causal chain",
                "entity": "throughput and progress rise before TiKV write I/O and CPU and frontend p95 worsens later",
                "evidence": [
                    "target Lightning history window",
                ],
            },
            {
                "type": "constraint",
                "factor": "shared Lightning and TiKV pressure requires coupled region concurrency sort quota and write bandwidth bounds",
                "entity": "all three budget dimensions jointly constrain the frontend SLO",
                "evidence": [
                    "coupled Lightning and TiKV pressure",
                ],
            },
            {
                "type": "exclusion",
                "factor": "precheck passed and the strict source format is not the root cause",
                "entity": "precheck source and target contract are valid",
                "evidence": [
                    "precheck passed",
                ],
            },
            {
                "type": "state",
                "factor": "the current reconfigure_required state is the same Lightning job source and checkpoint handoff",
                "entity": "same job source path and checkpoint",
                "evidence": [
                    "reconfigure_required is a checkpoint handoff pause rather than import failure",
                ],
            },
            {
                "type": "state",
                "factor": "reconfigure_required is a checkpoint handoff pause rather than import failure",
                "entity": "current Lightning controller checkpoint handoff",
                "evidence": [
                    "current controller stopped the same job after checkpoint handoff and preserves source and sorted directories",
                ],
            },
            {
                "type": "exclusion",
                "factor": "the benign staging Lightning import completed safely inside the history and is not the incident",
                "entity": "same-shape small Lightning window with normal frontend SLO",
                "evidence": [
                    "benign staging Lightning window",
                ],
            },
        ]
    },
    "outcome": {
        "changes": [
            "Resumed the same checkpoint with bounded phase2 region concurrency, disk quota, and store write bandwidth",
        ],
        "verification": [
            "Completed exactly 2000000 rows inside the settlement time-box and verified all three frontend profiles plus protected table state",
        ],
    },
    "summary": "The same Lightning checkpoint completed inside the settlement time-box under a coupled bounded phase2 budget while frontend and protected business invariants remained healthy.",
}
_INVESTIGATION_CASE = replace(
    _CASE,
    case_id="lightning_budget_history_investigation",
    case_no=1,
    evaluator=TidbResourceGovernanceLightningBudgetHistoryInvestigationEvaluatorCase,
    title="Investigate a Lightning checkpoint handoff and choose a bounded continuation budget.",
    reference_report=_INVESTIGATION_REFERENCE_REPORT,
    alert=(
        f"P2 data-platform incident: the 2,000,000-row import into "
        "benchops_mf_rg05.mf_rg05_lightning_orders stopped partway and the target table is still "
        "empty; downstream order flows are waiting on this data today. The upstream snapshot is "
        "about 1.5 GiB and the nightly settlement batch can only absorb about "
        f"{round(_SETTLEMENT_WINDOW_SECONDS / 60)} minutes of final import runtime before it must "
        "see the complete table. While the last import run was active, order-search and checkout "
        "frontend p95 repeatedly exceeded the 650ms SLO, and the frontend is calm now that the "
        "import is stopped. Finish the import completely within the settlement time-box with every "
        "frontend SLO profile within its p95 target, keeping mf_rg05_business_orders and "
        "mf_rg05_inventory untouched."
    ),
    background_workload=_INVESTIGATION_WORKLOAD,
    frozen_history=replace(
        _CASE.frozen_history,
        duration_seconds=21_600,
        normal_capture_seconds=60,
        # The 2,000,000-row source (4 files x 500,000 rows, ~1.5 GiB) encodes
        # at region_concurrency 6 in ~130-250 s under co-tenant load, and the
        # r5 precheck + staging import measured 165-376 s across the shared
        # machine's load spectrum, so the 720 s window covers staging +
        # encode-time handoff with margin plus a real post-handoff tail. The
        # phase1 deadline below must equal the window so status() cannot fail
        # a handoff the window still covers (and it starts at the main
        # import, so staging never eats the deadline).
        fault_capture_seconds=720,
        overview_step_seconds=60,
        # The age floor must exceed the window by the after_target decoy's
        # footprint (60 s + transition): the post-target placement headroom is
        # age_low - window, and the aftermath transient lives there.
        target_age_seconds_range=(800, 1_980),
        post_target_mode="HOLD_TARGET",
        # Pre-target decoys sit flush against the incident window (r3): the
        # replayed benign TiKV write burst must compete for the same reading
        # position as the real coupling, so spike- or pressure-anchored
        # attribution without three-channel co-occurrence fails.
        decoys_adjacent_to_target=True,
        # Two p95 decoys bracket the incident: the pre-incident baseline spike
        # (inherited from the calibration spec's normal segment) and a
        # post-incident transient on the same frontend profile (after_target).
        # Only the import-coupled p95 behavior inside the target window
        # co-moves with import throughput and TiKV write pressure, so
        # spike-anchored attribution without time alignment fails.
        decoys=(
            _CASE.frozen_history.decoys[0],
            HistoryDecoySpec(
                decoy_id="frontend-p95-aftermath-transient",
                kind=DecoyKind.METRIC_ONLY,
                metric="workload_profile",
                field="p95_ms",
                target="checkout_recent_order_search",
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                amplitude_mad=3.0,
                after_target=True,
            ),
            # A real elevated TiKV write segment replayed from the normal
            # capture (no synthetic amplitude, no manufactured operation
            # events): pressure rose here without import activity and without
            # a frontend p95 response, so co-occurrence — not pressure alone —
            # is the causal discriminant.
            HistoryDecoySpec(
                decoy_id="tikv-benign-write-burst",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="disk_io",
                field="write_mb_per_second",
                target="tikv/tikv-1",
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=40,
                minimum_deviation_mad=0.5,
            ),
        ),
        decoy_lightning_job_count=0,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.541667,
        reference_run_ids=(
            "reference-241__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001",
        ),
        protocol_version="difficulty-v2",
    ),
    # r5: the benign staging import adds a real same-shape Lightning window
    # (100k rows, safe completion) the agent must exclude, per the frozen-history
    # build guide's interference plan.
    staging_table="mf_rg05_staging_orders",
    staging_row_count=100_000,
    row_count=2_000_000,
    source_file_count=4,
    # One data engine: this Lightning build numbers "restore file completed"
    # marks per engine, so only a single-engine source can ever present the
    # source_file_count distinct marks the partial handoff requires. The
    # engine ingests as one unit after encoding every file, so the handoff is
    # taken at encode completion with importedCount still zero (measured in
    # smoke runs).
    engine_batch_size_bytes=None,
    business_row_count=120_000,
    inventory_row_count=20_000,
    # The single engine flushes importedCount only at ingest completion, so
    # the row threshold must accept the zero-progress encode-time handoff
    # instead of demanding ingest rows that cannot exist yet; the poll still
    # runs every 1 s so the monitor cannot miss the handoff window.
    rebalance_after_rows=0,
    # The handoff fires at encode completion, so phase1 sets the encode pace:
    # region_concurrency 6 (the initial-policy max) brings the 2,000,000-row
    # encode back to ~89-128 s under load — long enough for the frozen history
    # to capture real finished progress and inside the 720 s window.
    phase1_region_concurrency=6,
    phase1_disk_quota_mb=4_096,
    phase1_store_write_bwlimit_mib=96,
    phase1_checkpoint_deadline_seconds=720,
    checkpoint_poll_interval_seconds=1,
    settlement_window_seconds=_SETTLEMENT_WINDOW_SECONDS,
    frontend_max_failures=0,
    # r4 repair-side pinch: the raised rc ceiling lets the fast corner actually
    # saturate TiKV writes against the frontend SLO while the low bw floor
    # stretches the conservative corner against the settlement time-box.
    phase2_region_concurrency_max=4,
    phase2_store_write_bwlimit_mib_min=8,
    backfill_decoy=False,
)


class TidbResourceGovernanceLightningBudgetFrozenHistoryInjector(BaseFaultInjector):

    retain_workload_after_metric_history = True

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Keep the fault state active through the Agent phase."""
        import json as _json
        from urllib.parse import quote
        from urllib.request import urlopen

        probe_port = context.env.deployment.prometheus_port
        try:
            with urlopen(f"http://127.0.0.1:{probe_port}/api/v1/targets", timeout=5) as response:
                payload = _json.load(response)
            summary = [
                {
                    "scrapeUrl": target.get("scrapeUrl"),
                    "health": target.get("health"),
                    "lastError": (target.get("lastError") or "")[:200],
                }
                for target in payload.get("data", {}).get("activeTargets", [])
                if "lightning" in str(target.get("scrapeUrl"))
            ]
            print(f">>> [RG05-mf probe] lightning targets: {_json.dumps(summary)}")
            query = quote('sum(lightning_chunks{job="lightning", state="estimated"})')
            with urlopen(
                f"http://127.0.0.1:{probe_port}/api/v1/query?query={query}", timeout=5
            ) as response:
                payload = _json.load(response)
            print(f">>> [RG05-mf probe] estimated_chunks now: {_json.dumps(payload.get('data', {}).get('result'))}")
            state = self.controller._container_state()
            print(f">>> [RG05-mf probe] lightning container state: {_json.dumps(state)}")
        except Exception as exc:
            print(f">>> [RG05-mf probe] failed: {exc!r}")
    """Prepare the persistent import before history capture and activate phase1 in target time."""

    def __init__(self) -> None:
        self.controller: LightningBudgetController | None = None
        self._monitor_stop = threading.Event()
        self._monitor_thread: threading.Thread | None = None
        self._monitor_error: Exception | None = None
        self._poll_interval_seconds = 2

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self.controller.prepare()
        if context.config["backfill_decoy"]:
            self.controller.seed_history_jobs()
        context.env.attach_import_controller(self.controller)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self.controller.precheck()
        # The benign staging load runs to safe completion inside the captured
        # target window before the main import: a real same-shape Lightning
        # window the agent must tell apart from the incident (r5).
        if self.controller.staging_table is not None:
            self.controller.run_staging_import()
        self.controller.apply_budget(
            region_concurrency=context.config["phase1_region_concurrency"],
            disk_quota_mb=context.config["phase1_disk_quota_mb"],
            store_write_bwlimit_mib=context.config["phase1_store_write_bwlimit_mib"],
            job_id=lightning_job_id(context.env.run_id),
        )
        state = self.controller._container_state()
        print(f">>> [RG05-mf probe] after apply_budget container state: {state!r}")
        self._poll_interval_seconds = int(context.config["checkpoint_poll_interval_seconds"])
        self._monitor_thread = threading.Thread(
            target=self._monitor_checkpoint,
            name=f"frozen-history-lightning-monitor-{context.run_id}",
            daemon=True,
        )
        self._monitor_thread.start()

    def _monitored_start(self) -> None:
        observations = 0
        while not self._monitor_stop.is_set():
            state = self.controller._container_state()
            observations += 1
            if state is None:
                print(f">>> [RG05-mf probe] monitor: container object gone after {observations} polls")
                return
            if observations <= 3 or not state["Running"]:
                print(
                    ">>> [RG05-mf probe] monitor:"
                    f" running={state['Running']!r}, status={state.get('Status')!r},"
                    f" exit_code={state.get('ExitCode')!r}, error={str(state.get('Error'))[:120]!r}"
                )
            if not state["Running"]:
                print(">>> [RG05-mf probe] monitor: container no longer running, stopping monitor")
                return
            self._monitor_stop.wait(self._poll_interval_seconds)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context)
        business = json_object(
            context.env.execute_sql(
                f"SELECT COUNT(*), COALESCE(SUM(amount),0), MIN(order_id), MAX(order_id) "
                f"FROM {self.controller.db}.{self.controller.business_table}"
            ),
            "capture frozen-history Lightning business baseline",
        )
        inventory = json_object(
            context.env.execute_sql(
                f"SELECT COUNT(*), COALESCE(SUM(available_units),0), COALESCE(SUM(reserved_units),0), "
                f"MIN(sku_id), MAX(sku_id) FROM {self.controller.db}.{self.controller.inventory_table}"
            ),
            "capture frozen-history Lightning inventory baseline",
        )
        business_checksum = json_object(
            context.env.execute_sql(
                f"ADMIN CHECKSUM TABLE {self.controller.db}.{self.controller.business_table}"
            ),
            "capture frozen-history Lightning business checksum",
        )
        inventory_checksum = json_object(
            context.env.execute_sql(
                f"ADMIN CHECKSUM TABLE {self.controller.db}.{self.controller.inventory_table}"
            ),
            "capture frozen-history Lightning inventory checksum",
        )
        return {
            "frozen_history_lightning_identity": {
                "job_id": lightning_job_id(self.controller.run_id),
                "target": f"{self.controller.db}.{self.controller.import_table}",
                "source_directory": str(self.controller.source_dir),
                "checkpoint_directory": str(self.controller.checkpoint_dir),
                "source_file_count": self.controller.source_file_count,
                "source_row_count": self.controller.row_count,
            },
            "frozen_history_lightning_business_baseline": {
                "business_aggregate": business["result"],
                "business_checksum": business_checksum["result"],
                "inventory_aggregate": inventory["result"],
                "inventory_checksum": inventory_checksum["result"],
            },
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self._stop_monitor()

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self._stop_monitor()
        self.controller.cleanup()
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.controller.db}"),
            f"drop frozen-history Lightning database {self.controller.db}",
        )

    def _configure(self, context: FaultLifecycleContext) -> None:
        if self.controller is None:
            self.controller = LightningBudgetController(context.env, context.config)

    def _monitor_checkpoint(self) -> None:
        observations = 0
        try:
            while not self._monitor_stop.is_set():
                state = self.controller._container_state()
                observations += 1
                if state is None:
                    print(
                        f">>> [RG05-mf probe] monitor: container object gone after {observations} polls"
                    )
                    return
                if observations <= 3 or not state["Running"]:
                    print(
                        ">>> [RG05-mf probe] monitor:"
                        f" running={state['Running']!r}, status={state.get('Status')!r},"
                        f" exit_code={state.get('ExitCode')!r}, error={str(state.get('Error'))[:160]!r}"
                    )
                if not state["Running"]:
                    return
                if self.controller.monitor_checkpoint() == "reconfigure_required":
                    return
                if self._monitor_stop.wait(self._poll_interval_seconds):
                    return
        except Exception as exc:
            self._monitor_error = exc

    def _stop_monitor(self) -> None:
        self._monitor_stop.set()
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=10)
            if self._monitor_thread.is_alive():
                raise RuntimeError("Frozen-history Lightning checkpoint monitor did not stop")
            self._monitor_thread = None
        if self._monitor_error is not None:
            raise RuntimeError("Frozen-history Lightning checkpoint monitor failed") from self._monitor_error


class TidbResourceGovernanceLightningBudgetFrozenHistoryScenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_lightning_budget_frozen_history"
    description = (
        "Diagnose a historical Lightning/TiKV/frontend resource chain and resume the same "
        "checkpoint under a bounded second-phase budget."
    )
    cases = (_CASE, _INVESTIGATION_CASE)

    def build_fault_plan(
        self,
        case: TidbResourceGovernanceLightningBudgetFrozenHistoryForBudgetCalibrationScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbResourceGovernanceLightningBudgetFrozenHistoryInjector,
                config={
                    "db": case.db,
                    "import_table": case.import_table,
                    "business_table": case.business_table,
                    "inventory_table": case.inventory_table,
                    "row_count": case.row_count,
                    "source_file_count": case.source_file_count,
                    "engine_batch_size_bytes": case.engine_batch_size_bytes,
                    "business_row_count": case.business_row_count,
                    "inventory_row_count": case.inventory_row_count,
                    "analyze_required": False,
                    "reset_workload_on_rebalance": True,
                    "phase1_checkpoint_deadline_seconds": case.phase1_checkpoint_deadline_seconds,
                    "checkpoint_poll_interval_seconds": case.checkpoint_poll_interval_seconds,
                    "phase1_region_concurrency": case.phase1_region_concurrency,
                    "phase1_disk_quota_mb": case.phase1_disk_quota_mb,
                    "phase1_store_write_bwlimit_mib": case.phase1_store_write_bwlimit_mib,
                    "rebalance_after_rows": case.rebalance_after_rows,
                    "phase2_region_concurrency_max": case.phase2_region_concurrency_max,
                    "phase2_disk_quota_mb_max": case.phase2_disk_quota_mb_max,
                    "phase2_store_write_bwlimit_mib_max": case.phase2_store_write_bwlimit_mib_max,
                    "phase2_store_write_bwlimit_mib_min": case.phase2_store_write_bwlimit_mib_min,
                    "staging_table": case.staging_table,
                    "staging_row_count": case.staging_row_count,
                    "backfill_decoy": case.backfill_decoy,
                },
            ),
        )


__all__ = (
    "TidbResourceGovernanceLightningBudgetFrozenHistoryForBudgetCalibrationScenarioCase",
    "TidbResourceGovernanceLightningBudgetFrozenHistoryInjector",
    "TidbResourceGovernanceLightningBudgetFrozenHistoryScenario",
)
