"""PG-HC-MF02: real backup-chain and RPO certification lifecycle."""

from __future__ import annotations

import json
import subprocess
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping

from src.protocols.report import EMPTY_REPORT
from src.execution.backup_rpo import (
    RPO_ARCHIVE_COMMAND,
    RPO_ARCHIVE_EMERGENCY_COMMAND,
    RPO_ARCHIVE_ROUTE_EMERGENCY,
    RPO_ARCHIVE_ROUTE_STANDARD,
)
from src.execution.history.records import HistoricalRecordSource
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)
from src.scenarios.evaluation.postgres.health_check.backup_rpo_certification import (
    PgHealthCheckBackupRpoCertificationEvaluatorCase,
    PgHealthCheckBackupRpoCertificationSimpleEvaluatorCase,
)
from src.execution.specs import HostPortLayout, CaseResourceSpec, PostgresCaseRuntime, PostgresRuntimeSpec
from src.scenarios.base import DifficultyCalibration, FaultPlan, PostgresScenario, PostgresScenarioCase
from src.workloads.specs import EMPTY_BACKGROUND_WORKLOAD
from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase, WorkloadProfile
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext


RPO_RESOURCES = CaseResourceSpec(
    worker_physical_cores=2,
    worker_memory_mb=2048,
    container_cpu_limit=2.0,
    container_memory_mb=1024,
)

RPO_RUNTIME = PostgresRuntimeSpec(
    parameters=(
        ("shared_preload_libraries", "pg_stat_statements"),
        ("wal_level", "replica"),
        ("archive_mode", "on"),
        ("archive_command", "/usr/local/bin/aiopsbench-rpo-archive %p %f"),
        ("archive_timeout", "10s"),
        ("timezone", "UTC"),
        ("log_timezone", "UTC"),
        ("track_io_timing", "on"),
        ("log_checkpoints", "on"),
        ("logging_collector", "on"),
        ("log_destination", "stderr"),
        ("log_directory", "/var/log/postgresql"),
        ("log_filename", "postgresql-%Y-%m-%d_%H%M%S.log"),
        ("log_rotation_age", "1d"),
        ("log_rotation_size", "100MB"),
        ("log_line_prefix", "%m [%p] app=%a user=%u db=%d "),
        ("log_min_duration_statement", "0"),
        ("log_lock_waits", "on"),
    )
)


def _parse_postgres_timestamp(value: str) -> datetime:
    """Normalize PostgreSQL's UTC offset form before Python parsing."""
    normalized = value.replace(" ", "T")
    date_part, separator, fractional_part = normalized.partition(".")
    if separator:
        offset_start = next(
            (index for index, character in enumerate(fractional_part) if character in "+-"),
            len(fractional_part),
        )
        fraction = fractional_part[:offset_start]
        offset = fractional_part[offset_start:]
        normalized = f"{date_part}.{fraction.ljust(6, '0')}{offset}"
    if normalized.endswith("+00"):
        normalized = f"{normalized}:00"
    return datetime.fromisoformat(normalized)


# Fixed trusted stall window for deterministic (non-Docker) test runs; real
# runs record the frozen-history audit target window into runtime state when
# the assembled history is bound (metric_history_bound hook).
_DETERMINISTIC_STALL_START_MS = 1_784_000_640_000
_DETERMINISTIC_STALL_END_MS = _DETERMINISTIC_STALL_START_MS + 180_000

# Residual incident configuration. The standard delivery tier (healthy
# archive route, no transport pacing) is recorded into the frozen history's
# normal windows by the environment's route-config operation event; the
# current instance state never publishes it. The incident close-out instead
# leaves the archive route bound to the emergency transport wrapper (one
# per-segment pacing value), which is invisible at the idle agent-phase load
# but physically fails a capacity replay judged at the standard tier.
# The emergency route uses an independent name that shares no substring
# with the standard command (substring surgery cannot recover the standard
# binding), and its wrapper is self-contained (its file content never
# references the standard wrapper), so the frozen history's pre-incident
# strip records are the only surface carrying the standard tier.
_STANDARD_ARCHIVE_COMMAND = "/usr/local/bin/aiopsbench-rpo-archive %p %f"
_EMERGENCY_ARCHIVE_COMMAND = "/usr/local/sbin/aiopsbench-wal-cold-relay %p %f"
_EMERGENCY_ROUTE_SCRIPT = "/usr/local/sbin/aiopsbench-wal-cold-relay"


def _emergency_route_script_body(pacing: int) -> str:
    """Self-contained cold-relay transport script.

    The emergency tier paces every segment hand-off itself and installs the
    segment atomically. It deliberately contains no reference to the standard
    wrapper (path, file name, or command): an agent that can read the script
    must not be able to derive the standard route from it — the frozen
    history's pre-incident strip records are the only standard-tier surface.
    """
    return (
        "#!/usr/bin/env bash\n"
        "# Cold relay transport tier: paces every segment hand-off before it\n"
        "# lands in the archive repository.\n"
        "set -euo pipefail\n"
        'source_path="${1:?cold relay requires the WAL source path}"\n'
        'wal_name="${2:?cold relay requires the WAL file name}"\n'
        "repository=/aiopsbench/archive\n"
        f"sleep {pacing}\n"
        'mkdir -p "$repository"\n'
        'if [[ ! -e "${repository}/${wal_name}" ]]; then\n'
        '  cp -- "${source_path}" "${repository}/${wal_name}.cold"\n'
        '  mv "${repository}/${wal_name}.cold" "${repository}/${wal_name}"\n'
        "fi\n"
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckBackupRpoCertificationCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    rpo_seconds: int
    marker_interval_seconds: int
    workload_duration_seconds: int
    archive_delay_seconds: int
    workload_profile: str
    snapshot_unsafe: bool = True
    # Residual incident configuration (attribution-outcome coupling). Zero
    # values mean no residual route downgrade, and the
    # recover_archive canary keeps its infrastructure deadline. The simple case
    # declares the pacing/acceptance pair; the hard case declares the
    # capacity-replay triple below.
    residual_emergency_route_pacing_seconds: int = 0
    archive_capacity_acceptance_seconds: int = 0
    # Hard-case residual-route coupling: the incident response downgrades the
    # archive route to the emergency transmission tier, and the post-incident
    # cleanup lifts only the congestion delay. The route residual is invisible
    # under the idle post-aftermath load, but the certification capacity replay
    # accepts the publication tier only, so an unattributed repair physically
    # cannot close the chain.
    residual_archive_route_hardening: bool = False
    capacity_replay_segments: int = 0
    capacity_replay_envelope_seconds: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckBackupRpoCertificationForThroughputGapScenarioCase(
    PgHealthCheckBackupRpoCertificationCase
):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckBackupRpoCertificationForThroughputGapSimpleScenarioCase(
    PgHealthCheckBackupRpoCertificationCase
):
    pass


def _reference_report() -> dict[str, Any]:
    report = json.loads(json.dumps(EMPTY_REPORT))
    report.update({
        "outcome": {
            "changes": ["restored archive delivery capacity and ran isolated PITR"],
            "verification": ["manifest, inventory continuity, hidden marker and checksum passed"],
        },
        "summary": "History, bounded operation events and trusted PITR establish the RPO decision.",
    })
    return report


_RPO_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(WorkloadProfile(
        name="rpo_history_probe",
        sql="SELECT 1;",
        qps=0.2,
        tier="LIGHT",
        application_name="rpo-history-probe",
        transactional=False,
    ),),
    worker_count=1,
    seed=0x9C02,
    start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
    warmup_seconds=4,
)


_HARD_HISTORY = FrozenHistorySpec(
    schema_version=1,
    duration_seconds=43_200,
    normal_capture_seconds=120,
    fault_capture_seconds=180,
    base_step_seconds=2,
    # The coarse public overview keeps the whole 12-hour grid inside the
    # shared point budget (43200s / 480s = 90 points). The anchored target
    # window shows up as a single suspicious point that must compete with the
    # candidate valleys; ordered causality stays at mid and base granularity.
    overview_step_seconds=480,
    block_min_seconds=60,
    block_max_seconds=120,
    transition_seconds=20,
    target_age_seconds_range=(1_800, 10_800),
    required_metrics=(
        "wal_generation",
        "archive_delivery",
        "archive_backlog",
        "business_commits",
        "oltp_service",
        "backup_progress",
    ),
    record_sources=(HistoricalRecordSource.OPERATION_EVENT,),
    decoys=(
        # Three candidate valleys replay the real target capture's own channel
        # shapes at the same depth, duration, and metric signature, so overview
        # and mid-granularity statistics cannot separate them from the buried
        # incident window. Only operation-event evidence and the ordered
        # wal-burst -> delivery-stall -> backlog-climb causality distinguish
        # the true window:
        #   - missing_precursor flattens the WAL channels (the delivery
        #     collapse and backlog climb have no generating burst);
        #   - scrambled_order deepens the backlog before it falls again while
        #     delivery stays collapsed (a stall cannot drain itself);
        #   - shadow_copy is metrically identical to the incident window and
        #     only lacks the business marker continuity in its records.
        HistoryDecoySpec(
            decoy_id="valley-missing-precursor",
            kind=DecoyKind.CANDIDATE_VALLEY,
            metric="wal_generation",
            field="bytes_per_sec",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=180,
            valley_profile="missing_precursor",
            baseline_metrics=("wal_generation",),
        ),
        HistoryDecoySpec(
            decoy_id="valley-scrambled-order",
            kind=DecoyKind.CANDIDATE_VALLEY,
            metric="archive_backlog",
            field="oldest_age_sec",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=180,
            valley_profile="scrambled_order",
        ),
        HistoryDecoySpec(
            decoy_id="valley-shadow-stall",
            kind=DecoyKind.CANDIDATE_VALLEY,
            metric="archive_delivery",
            field="bytes_per_sec",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=180,
            valley_profile="shadow_copy",
            record_event_types=("archive_attempt",),
        ),
    ),
    max_points_per_series=3_000,
    max_scalar_samples_per_response=12_000,
    max_history_query_seconds=900,
    max_history_records_per_response=100,
    decoys_adjacent_to_target=True,
    # The stall exists only inside the buried target window. After the capture,
    # the orchestrator physically resolves the archive congestion and captures
    # the real backlog-drain convergence, so the frozen tail returns to the
    # normal regime and the tail carries no stall evidence. The emergency
    # route residual survives that cleanup: the live tail keeps up with the
    # idle segment cadence, so no current-state metric exposes it.
    aftermath="RETURN_TO_NORMAL",
    aftermath_capture_seconds=180,
)


_SIMPLE_HISTORY = FrozenHistorySpec(
    schema_version=1,
    duration_seconds=21_600,
    normal_capture_seconds=120,
    fault_capture_seconds=180,
    base_step_seconds=2,
    overview_step_seconds=300,
    block_min_seconds=60,
    block_max_seconds=120,
    transition_seconds=20,
    target_age_seconds_range=(900, 5_400),
    required_metrics=_HARD_HISTORY.required_metrics,
    record_sources=(HistoricalRecordSource.OPERATION_EVENT,),
    # The real archiver catch-up is captured live right after the stall
    # window; the assembled history therefore ends the stall signature with a
    # physical convergence (delivery catch-up, backlog drain) and returns to
    # the normal regime for the remaining tail. The signature exists only
    # inside the target window, so a tail query no longer reproduces it.
    aftermath_capture_seconds=240,
    # The standard archive route binding is published only in the pre-incident
    # strip: the assembled normal blocks within 480s before the target window.
    # A query window disjoint from the strip observes zero route-config
    # records, so restoring the standard tier (and passing the standard-tier
    # capacity replay) physically requires locating the incident neighborhood
    # first. The former replay-into-every-normal-block guarantee was an
    # information leak, not a solvability guarantee.
    pre_incident_strip_seconds=480,
    strip_pinned_record_actions=(("repository_sync", "route_config"),),
    decoys=(
        HistoryDecoySpec(
            decoy_id="simple-wal-burst-window",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="wal_generation",
            field="bytes_per_sec",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=40,
            # The real normal capture is intentionally sparse at this
            # workload scale.  The shared captured-benign selector uses its
            # observed-peak fallback when MAD is zero, whose normalized
            # deviation is bounded by 1.0.
            minimum_deviation_mad=0.01,
        ),
        HistoryDecoySpec(
            decoy_id="simple-backup-window",
            kind=DecoyKind.METRIC_ONLY,
            metric="backup_progress",
            field="progress_percent",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=40,
            amplitude_mad=2.0,
            record_event_type="backup_run",
        ),
        HistoryDecoySpec(
            decoy_id="simple-archive-retry-window",
            # A bounded archive-retry distractor on the delivery channel: the
            # failure counter spikes without any delivery drop or backlog
            # growth, so naive "first anomaly" window selection produces a
            # window the certification verifier rejects.
            kind=DecoyKind.METRIC_ONLY,
            metric="archive_delivery",
            field="failure_delta",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=60,
            amplitude_mad=2.0,
            record_event_type="archive_attempt",
        ),
        HistoryDecoySpec(
            decoy_id="simple-delivery-quiet-window",
            # A real captured delivery-quiet segment: durable archive
            # delivery falls to its silent baseline for a minute and recovers
            # by itself, with zero backlog growth and zero oldest-age climb.
            # The target stall instead couples the delivery collapse with a
            # sustained backlog rise, so anchoring the certification on this
            # window is the wrong-window failure the case punishes.
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="archive_delivery",
            field="bytes_per_sec",
            target=None,
            direction=DecoyDirection.DIP,
            count=1,
            duration_seconds=60,
            minimum_deviation_mad=0.01,
        ),
    ),
    max_points_per_series=2_000,
    max_scalar_samples_per_response=8_000,
    max_history_query_seconds=1_200,
    max_history_records_per_response=120,
)


_HARD_CASE = PgHealthCheckBackupRpoCertificationForThroughputGapScenarioCase(
    case_id="throughput_gap",
    case_no=0,
    evaluator=PgHealthCheckBackupRpoCertificationEvaluatorCase,
    title="Hard historical RPO certification with an isolated business restore.",
    alert=(
        "[Scheduled PostgreSQL DR Certification] Certify recovery capability against the approved "
        "60-second RPO using the bounded evidence window selected from the metric overview. The "
        "current system appears recovered; use "
        "bounded historical observations and physical backup evidence to determine whether "
        "the contract held, then perform an isolated point-in-time restore at the selected "
        "business point. Refuse certification and report the last recoverable boundary when "
        "the chain cannot support the contract. HARD TOOL BOUNDARIES: each historical metric/log "
        "Start with query_metrics for each required metric without timestamps to obtain the compact overview; "
        "then select one evidence interval and query at most one 900-second window per metric. Do not scan "
        "the full 12-hour range or retry an identical failed window. operation_event also requires the same "
        "bounded timestamps. Every explicit historical window must be <=900 seconds; use only wal_generation, archive_delivery, archive_backlog, "
        "business_commits, oltp_service, backup_progress; use logical targets archive_repository, "
        "backup_repository, and evaluator_selected, never container filesystem paths."
    ),
    initial_state={
        "status": "rpo_certification_pending",
        "topology": "primary_archive_repository_isolated_restore",
        "rpo_seconds": 60,
        "backup_toolchain": "physical_backup_and_archive_repository",
    },
    expected_target={
        "status": "rpo_certified",
        "manifest": "sha256",
        "pitr": "isolated",
        "marker_checksum": "verified",
    },
    background_workload=_RPO_BACKGROUND_WORKLOAD,
    reference_report=_reference_report(),
    frozen_history=_HARD_HISTORY,
    runtime=PostgresCaseRuntime(host_ports=HostPortLayout(offsets=(0, 1)), resources=RPO_RESOURCES, parameters=RPO_RUNTIME),
    base_image_name="aiopsbench-pg-initialized:latest",
    workload_tag="pgbench",
    rpo_seconds=60,
    marker_interval_seconds=15,
    workload_duration_seconds=240,
    # Keep the archive command slower than archive_timeout so the real
    # archive-status queue can grow under the certification workload.
    archive_delay_seconds=20,
    workload_profile="pgbench_with_certification_windows",
    residual_archive_route_hardening=True,
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.924293,
        reference_run_ids=(
            "reference-59__"
            "pg_health_check_backup_rpo_certification__throughput_gap__llm__r001",
        ),
    ),

    # The capacity replay bursts 8 segments (128 MiB); the emergency route's
    # ~4 MB/s transmission tier needs ~32 s and misses the 15 s publication
    # envelope, while the standard route delivers within seconds. The idle
    # segment cadence (16 MiB / 10 s) stays below the emergency throttle, so
    # the residual raises no metric anomaly at the current low load.
    capacity_replay_segments=8,
    capacity_replay_envelope_seconds=15,
)

_SIMPLE_CASE = PgHealthCheckBackupRpoCertificationForThroughputGapSimpleScenarioCase(
    case_id="throughput_gap_simple",
    case_no=1,
    evaluator=PgHealthCheckBackupRpoCertificationSimpleEvaluatorCase,
    title="Simple historical RPO certification with an isolated business restore.",
    alert=(
        "[Scheduled PostgreSQL DR Certification] Validate the selected recovery target "
        "using bounded historical observations, the physical backup, archive inventory, "
        "and an isolated restore. Certify only after the marker boundary and checksum are "
        "verified. First read metric overviews without timestamps, then drill into a single bounded evidence "
        "window; never request the full 6-hour history. HARD TOOL BOUNDARIES: each historical metric/log window must be <=900 seconds; "
        "use only wal_generation, archive_delivery, archive_backlog, business_commits, oltp_service, "
        "backup_progress; use logical targets archive_repository, backup_repository, and "
        "evaluator_selected, never container filesystem paths."
    ),
    initial_state={
        "status": "rpo_certification_pending",
        "topology": "primary_archive_repository_isolated_restore",
        "rpo_seconds": 60,
        "backup_toolchain": "physical_backup_and_archive_repository",
    },
    expected_target={
        "status": "rpo_certified",
        "manifest": "sha256",
        "pitr": "isolated",
        "marker_checksum": "verified",
    },
    background_workload=_RPO_BACKGROUND_WORKLOAD,
    reference_report=_reference_report(),
    frozen_history=_SIMPLE_HISTORY,
    runtime=PostgresCaseRuntime(host_ports=HostPortLayout(offsets=(0, 1)), resources=RPO_RESOURCES, parameters=RPO_RUNTIME),
    base_image_name="aiopsbench-pg-initialized:latest",
    workload_tag="pgbench",
    rpo_seconds=60,
    marker_interval_seconds=15,
    workload_duration_seconds=120,
    archive_delay_seconds=2,
    workload_profile="pgbench_with_certification_windows_simple",
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.797589,
        reference_run_ids=(
            "reference-60__"
            "pg_health_check_backup_rpo_certification__throughput_gap_simple__llm__r001",
        ),
    ),
    # Attribution-outcome coupling: the incident close-out leaves the archive
    # route bound to the emergency transport wrapper (90s per-segment pacing),
    # which is metric-invisible at the idle agent-phase load. The certification
    # capacity replay accepts at the standard delivery tier (60s acceptance
    # window, an evaluator-side interval that is never published), so the
    # replay physically fails until the standard route is restored from the
    # frozen history's route-config records.
    residual_emergency_route_pacing_seconds=90,
    archive_capacity_acceptance_seconds=60,
)


def _json_payload(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return result
    try:
        return json.loads(result)
    except (TypeError, json.JSONDecodeError):
        return {"status": "error", "error": str(result)}


class PgHealthCheckBackupRpoCertificationInjector(BaseFaultInjector):
    """Create a real base backup, archive stream, marker stream and gap window."""

    def __init__(self) -> None:
        self.env = None
        self.case = None
        self._real_mode = False
        self._stop_event = threading.Event()
        self._marker_thread: threading.Thread | None = None
        self._pgbench_process: subprocess.Popen | None = None
        self._markers: list[dict[str, str]] = []
        self._installed = False
        self._incident_archive_fault_active = False
        self._marker_count = 0

    def _configure(self, context: FaultLifecycleContext) -> None:
        self.env = context.env
        self.case = context.case
        self._real_mode = bool(getattr(self.env, "is_rpo_environment", False))
        if hasattr(self.env, "set_rpo_controller"):
            self.env.set_rpo_controller(self)
        self.state = getattr(self.env, "rpo_runtime_state", {})
        topology = getattr(self.env, "rpo_topology", None)
        self.state.update(
            {
                "scenario_id": context.scenario_id,
                "case_id": context.case_id,
                "toolchain": "pg_basebackup+archive_command",
                "topology": topology.as_dict() if topology is not None else {},
                "rpo_seconds": int(self.case.rpo_seconds),
            }
        )
        defaults = {
            "target_recoverable": True,
            "primary_intact": True,
            "backup_manifest_valid": False,
            "archive_inventory_complete": False,
            "timeline_contiguous": False,
            "archive_capacity_verified": False,
            "pitr_reached_target": False,
            "marker_boundary_valid": False,
            "marker_checksum_valid": False,
            "rpo_met": False,
            "pitr_attempts": [],
            "archive_recovered": False,
            "archive_replay_verified": False,
        }
        for key, value in defaults.items():
            self.state.setdefault(key, value)

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        if self._installed:
            return
        if self.case.residual_archive_route_hardening:
            # The incident response downgrades the archive route to the
            # emergency transmission tier; the aftermath cleanup lifts only
            # the congestion delay, so this residual survives into the
            # certification phase where the idle load hides it metrically.
            self._set_archive_route(RPO_ARCHIVE_ROUTE_EMERGENCY)
            self._incident_archive_fault_active = True
        if not self._real_mode:
            self._install_deterministic_test_state()
            self._installed = True
            return
        try:
            self._markers.clear()
            self._create_marker_table()
            self._create_base_backup()
            self._set_archive_delay(self.case.archive_delay_seconds)
            self._install_emergency_route_script()
            self._start_pgbench()
            self._start_marker_workload()
            self._wait_for_marker(minimum_count=2)
            self._installed = True
        except Exception as exc:
            raise RuntimeError(
                "PG-HC-MF02 setup blocker: real backup/archive workload setup failed; "
                f"case={context.case_id}: {exc}"
            ) from exc

    def prepare_metric_history(self, context: FaultLifecycleContext) -> None:
        """Finish one-time pgbench schema setup before the fixed-grid sampler."""
        self._configure(context)
        if not self._real_mode:
            return
        result = subprocess.run(
            [
                "docker", "exec", "-e", "PGPASSWORD=password", self.env.deployment.container_name,
                "pgbench", "-h", "127.0.0.1", "-U", "postgres", "-d", "testdb",
                "-i", "-s", "1", "-q",
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "PG-HC-MF02 metric-history schema setup failed: "
                f"{(result.stderr or result.stdout).strip()}"
            )

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        if not self._installed and not self.state.get("fault_ready"):
            self.install(context)
        self._assert_fault_ready()

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._assert_fault_ready(require_target=False)
        if self._real_mode:
            from src.execution.backup_rpo import repository_inventory

            inventory = repository_inventory(self.env)
            self.state["archive_inventory"] = inventory
            self.state["archive_inventory_complete"] = bool(inventory.get("files"))
            self.state["timeline_contiguous"] = self._check_inventory_continuity(inventory)
            if hasattr(self.env, "record_operation_event"):
                self.env.record_operation_event(
                    event_type="repository_sync",
                    entity_type="repository",
                    entity="archive_repository",
                    action="inventory",
                    status="success",
                    correlation_id=f"repository-sync-{self.case.case_id}",
                    details={
                        "file_count": len(inventory.get("files", ())),
                        "timeline_contiguous": bool(inventory.get("timeline_contiguous")),
                    },
                )
        self.state["fault_ready"] = True
        return {
            "fault_ready": True,
            "backup_toolchain": "pg_basebackup+archive_command",
            "topology_isolated": self._topology_isolated(),
            "archive_repository_provenance": "real_file_inventory",
        }

    def finalize_metric_history_target_capture(
        self,
        context: FaultLifecycleContext,
        target_start_ms: int,
        target_end_ms: int,
    ) -> None:
        """Freeze the hidden marker only after its event is in target history."""
        latest_allowed_ms = int(target_end_ms) - 2_000
        candidates = []
        for marker in self._markers:
            try:
                marker_ms = int(_parse_postgres_timestamp(marker["committed_at"]).timestamp() * 1000)
            except (KeyError, TypeError, ValueError):
                continue
            if int(target_start_ms) <= marker_ms <= latest_allowed_ms:
                candidates.append(marker)
        if not candidates:
            raise RuntimeError(
                "PG-HC-MF02 target marker was not captured in the frozen target range: "
                f"target_start_ms={target_start_ms}, target_end_ms={target_end_ms}, markers={len(self._markers)}"
            )
        self._select_hidden_target(candidates[-1])
        self._assert_fault_ready()

    def begin_metric_history_aftermath(self, context: FaultLifecycleContext) -> None:
        """Physically resolve the archive congestion before the aftermath capture.

        The frozen history must replay a real return to normal, so the delay
        control is cleared exactly as a completed remediation would and the
        certification workload keeps running while the backlog drains. The
        emergency route tier is deliberately left in place: the post-incident
        cleanup lifted the congestion, not the route downgrade, and that
        residual is what the certification capacity replay must expose.
        """
        self._configure(context)
        self._incident_archive_fault_active = False
        if not self._real_mode:
            self.state["archive_delay_seconds"] = 0
            return
        write_delay = subprocess.run(
            [
                "docker", "exec", self.env.deployment.container_name, "bash", "-lc",
                "printf '0\\n' > /aiopsbench/archive/.aiopsbench-delay-seconds && "
                "rm -f /aiopsbench/archive/.aiopsbench-fail-next",
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if write_delay.returncode != 0:
            raise RuntimeError(
                f"archive delay aftermath resolution failed: {write_delay.stderr.strip()}"
            )
        self.state["archive_delay_seconds"] = 0

    def end_metric_history_aftermath(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime_workload()

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime_workload()

    def recover(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime_workload()
        if self._real_mode and self.env is not None:
            try:
                subprocess.run(
                    [
                        "docker", "exec", self.env.deployment.container_name, "bash", "-lc",
                        "rm -f /aiopsbench/archive/.aiopsbench-delay-seconds "
                        "/aiopsbench/archive/.aiopsbench-fail-next "
                        f"{_EMERGENCY_ROUTE_SCRIPT}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                # Reverse the residual route binding so the dedicated container
                # is released with the standard route it was deployed with.
                subprocess.run(
                    [
                        "docker", "exec", "-e", "PGPASSWORD=password",
                        self.env.deployment.container_name, "psql",
                        "-U", "postgres", "-d", "testdb", "-At",
                        "-c",
                        f"ALTER SYSTEM SET archive_command = '{self.env.rpo_standard_archive_command}'",
                        "-c", "SELECT pg_reload_conf()",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                # Teardown remains best-effort; the run is already being
                # finalized and the dedicated container is removed afterward.
                pass
        self._installed = False

    def handle_manage_instance(self, action: str, target: str | None = None, value: str | None = None) -> str:
        if action in {"archive_status", "rpo_topology"}:
            if self._real_mode:
                from src.execution.backup_rpo import repository_inventory

                self.state["archive_inventory"] = repository_inventory(self.env)
            return json.dumps({"status": "success", "action": action, "result": self._current_public_status()}, default=str)
        if action == "recover_archive":
            return self._recover_archive(target)
        if action == "pitr_restore":
            return self._restore_to_selected_target(target)
        if action == "validate_backup":
            return self._validate_backup(target)
        return json.dumps({"status": "error", "error": f"Unknown RPO action: {action}"})

    def start_metric_history_normal_capture(self, context: FaultLifecycleContext) -> None:
        """Run the RPO normal-capture workload and record the healthy tier.

        The orchestrator dispatches this hook to injectors; the environment
        owns the actual capture workload (archive delay reset, standard route
        announcements, OLTP/WAL-burst/backup probes). Without this delegation
        the normal capture stays empty of RPO operation events and the frozen
        history never carries the standard archive route binding.
        """
        self._configure(context)
        if self._real_mode:
            self.env.start_metric_history_normal_capture()

    def finish_metric_history_normal_capture(self, context: FaultLifecycleContext) -> None:
        """Stop the RPO normal-capture workload after the normal window."""
        self._configure(context)
        if self._real_mode:
            self.env.finish_metric_history_normal_capture()

    def metric_history_bound(self, context: FaultLifecycleContext) -> None:
        """Record the trusted frozen stall window into runtime state.

        Called by the orchestrator right after the assembled history is bound
        to the environment, before the agent phase. The frozen-timeline target
        window is evaluator/injector truth for diagnosis scoring; it is never
        exposed through public agent tools (`_public_state` excludes it).
        """
        self._configure(context)
        if self._real_mode:
            start_ms, end_ms = self.env.rpo_frozen_stall_window_ms()
            self.state["stall_window"] = {"start_ms": start_ms, "end_ms": end_ms}
        self._bind_residual_emergency_route()

    def _bind_residual_emergency_route(self) -> None:
        """Leave the archive route at the emergency transport tier.

        The incident close-out downgrades the archive route binding after the
        aftermath capture, so the metric face stays converged while the
        transport capacity is no longer the standard tier. The standard route
        binding exists only inside the frozen history's route-config records;
        current state (config, tools, public status) never publishes it. The
        residual binding is visible through physical config inspection
        (pg_settings) and physically fails the standard-tier capacity replay.
        """
        pacing = int(getattr(self.case, "residual_emergency_route_pacing_seconds", 0) or 0)
        if pacing <= 0:
            return
        if self._real_mode:
            rebind = _json_payload(self.env.execute_sql_trusted(
                f"ALTER SYSTEM SET archive_command = '{_EMERGENCY_ARCHIVE_COMMAND}'"
            ))
            if rebind.get("status") == "error":
                raise RuntimeError(f"archive emergency route rebinding failed: {rebind}")
            reload_result = _json_payload(self.env.execute_sql_trusted("SELECT pg_reload_conf()"))
            if reload_result.get("status") == "error":
                raise RuntimeError(f"archive emergency route reload failed: {reload_result}")
            deadline = time.monotonic() + 15
            while True:
                probe = _json_payload(self.env.execute_sql_trusted(
                    "SELECT current_setting('archive_command')"
                ))
                if probe.get("status") == "error":
                    raise RuntimeError(f"archive emergency route probe failed: {probe}")
                if probe["result"][0][0] == _EMERGENCY_ARCHIVE_COMMAND:
                    break
                if time.monotonic() > deadline:
                    raise RuntimeError(
                        "archive emergency route did not become active after reload: "
                        f"expected={_EMERGENCY_ARCHIVE_COMMAND!r}, observed={probe['result'][0][0]!r}"
                    )
                time.sleep(0.5)
        self.state["residual_emergency_route"] = {
            "archive_command": _EMERGENCY_ARCHIVE_COMMAND,
            "transport_pacing_seconds": pacing,
        }
        self.state["residual_emergency_route_active"] = True

    def _install_emergency_route_script(self) -> None:
        """Ship the emergency transport wrapper into the primary container."""
        pacing = int(getattr(self.case, "residual_emergency_route_pacing_seconds", 0) or 0)
        if pacing <= 0:
            return
        if not self._real_mode:
            return
        script = _emergency_route_script_body(pacing)
        write = subprocess.run(
            [
                "docker", "exec", self.env.deployment.container_name, "bash", "-lc",
                f"cat > {_EMERGENCY_ROUTE_SCRIPT} <<'AIOPSBENCH_EOF'\n{script}AIOPSBENCH_EOF\n"
                f"chmod 755 {_EMERGENCY_ROUTE_SCRIPT}",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if write.returncode != 0:
            raise RuntimeError(
                f"emergency archive route script install failed: {(write.stderr or write.stdout).strip()}"
            )

    def _validate_backup(self, target: str | None) -> str:
        """Validate the standard pg_basebackup manifest without mutating the primary."""
        accepted_targets = {
            "",
            "backup_repository",
            "base_backup",
            "primary_backup",
            "/aiopsbench/basebackups/base",
            "/var/lib/postgresql/backup/base",
            "/tmp/backup",
            "/var/tmp/backup",
        }
        requested = str(target or "").strip()
        if requested not in accepted_targets:
            return json.dumps({
                "status": "error",
                "action": "validate_backup",
                "error": "backup target is outside the declared RPO backup repository",
            })
        if not self._real_mode:
            return json.dumps({
                "status": "success",
                "action": "validate_backup",
                "backup_path": "/aiopsbench/basebackups/base",
                "manifest_path": "/aiopsbench/basebackups/base/backup_manifest",
                "validation_status": "passed",
                "base_backup_ok": True,
                "archive_chain_ok": bool(self.state.get("archive_inventory_complete")),
                "recoverable": bool(self.state.get("archive_inventory_complete")),
            })

        container = self.env.deployment.container_name
        backup_path = "/aiopsbench/basebackups/base"
        verify = subprocess.run(
            ["docker", "exec", container, "pg_verifybackup", backup_path],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if verify.returncode != 0:
            return json.dumps({
                "status": "success",
                "action": "validate_backup",
                "backup_path": backup_path,
                "manifest_path": f"{backup_path}/backup_manifest",
                "validation_status": "failed",
                "base_backup_ok": False,
                "archive_chain_ok": False,
                "recoverable": False,
                "error": (verify.stderr or verify.stdout).strip(),
            })
        from src.execution.backup_rpo import repository_inventory

        inventory = repository_inventory(self.env)
        archive_chain_ok = bool(inventory.get("files")) and self._check_inventory_continuity(inventory)
        self.state["archive_inventory"] = inventory
        self.state["archive_inventory_complete"] = archive_chain_ok
        self.state["timeline_contiguous"] = archive_chain_ok
        return json.dumps({
            "status": "success",
            "action": "validate_backup",
            "backup_path": backup_path,
            "manifest_path": f"{backup_path}/backup_manifest",
            "validation_status": "passed" if archive_chain_ok else "failed",
            "base_backup_ok": True,
            "archive_chain_ok": archive_chain_ok,
            "recoverable": archive_chain_ok,
            "archive_inventory": inventory,
        }, default=str)

    def read_log(self, log_type: str) -> str | None:
        if log_type not in {"rpo_archive_inventory", "rpo_backup_manifest", "rpo_restore_result"}:
            return None
        if log_type == "rpo_archive_inventory" and self._real_mode:
            from src.execution.backup_rpo import repository_inventory

            self.state["archive_inventory"] = repository_inventory(self.env)
        if log_type == "rpo_archive_inventory":
            inventory = self.state.get("archive_inventory", {})
            return json.dumps({
                "status": "success",
                "log_type": log_type,
                "result": {
                    "file_count": len(inventory.get("files", ())),
                    "missing_segments": list(inventory.get("missing_segments", ())),
                    "timeline_contiguous": inventory.get("timeline_contiguous"),
                },
            }, default=str)
        if log_type == "rpo_backup_manifest":
            return json.dumps({
                "status": "success",
                "log_type": log_type,
                "result": {
                    "manifest_path": self.state.get("backup_manifest_path", "/aiopsbench/basebackups/base/backup_manifest"),
                    "manifest_valid": self.state.get("backup_manifest_valid") is True,
                },
            }, default=str)
        attempts = self.state.get("pitr_attempts", ())
        last_attempt = dict(attempts[-1]) if attempts else {"status": "not_attempted"}
        if last_attempt.get("status") == "success":
            last_attempt = {
                key: value
                for key, value in last_attempt.items()
                if key not in {"target_time", "marker_id", "marker_checksum", "rpo_met"}
            }
        return json.dumps({
            "status": "success",
            "log_type": log_type,
            "result": last_attempt,
        }, default=str)

    def _install_deterministic_test_state(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.state.update(
            {
                "fault_ready": True,
                "target_marker_id": f"marker-{self.case.case_id}-target",
                "target_time": now,
                "target_checksum": "a" * 32,
                "last_recoverable_time": now,
                "backup_manifest_valid": True,
                "archive_inventory_complete": True,
                "timeline_contiguous": True,
                "archive_capacity_verified": False,
                "archive_gap_recoverable": True,
                "archive_inventory": {"files": [{"wal_file": "000000010000000000000001", "sha256": "a" * 64}]},
                "stall_window": {
                    "start_ms": _DETERMINISTIC_STALL_START_MS,
                    "end_ms": _DETERMINISTIC_STALL_END_MS,
                },
            }
        )

    def _create_marker_table(self) -> None:
        result = self.env.execute_sql_trusted(
            """
            CREATE SCHEMA IF NOT EXISTS aiopsbench_rpo;
            CREATE TABLE IF NOT EXISTS aiopsbench_rpo.business_markers(
                marker_id text PRIMARY KEY,
                committed_at timestamptz NOT NULL,
                checksum text NOT NULL,
                payload text NOT NULL
            );
            CREATE TABLE IF NOT EXISTS aiopsbench_rpo.recovery_fences(
                fence_id text PRIMARY KEY,
                committed_at timestamptz NOT NULL
            );
            """
        )
        if _json_payload(result).get("status") == "error":
            raise RuntimeError(f"marker table creation failed: {result}")

    def _create_base_backup(self) -> None:
        container = self.env.deployment.container_name
        backup_path = "/aiopsbench/basebackups/base"
        manifest_probe = subprocess.run(
            ["docker", "exec", container, "test", "-s", f"{backup_path}/backup_manifest"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if manifest_probe.returncode != 0:
            command = [
                "docker", "exec", "-e", "PGPASSWORD=password", container,
                "bash", "-lc",
                (
                    f"rm -rf {backup_path} && mkdir -p {backup_path} && "
                    f"pg_basebackup -h 127.0.0.1 -U postgres -D {backup_path} "
                    "-Fp -Xs -P --manifest-checksums=SHA256 --max-rate=16M"
                ),
            ]
            result = subprocess.run(command, capture_output=True, text=True, timeout=900)
            if result.returncode != 0:
                raise RuntimeError(f"pg_basebackup failed: {(result.stderr or result.stdout).strip()}")
        verify = subprocess.run(
            ["docker", "exec", container, "pg_verifybackup", backup_path],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if verify.returncode != 0:
            raise RuntimeError(f"pg_verifybackup failed: {(verify.stderr or verify.stdout).strip()}")
        self.state["backup_manifest_valid"] = True
        self.state["backup_manifest_path"] = f"{backup_path}/backup_manifest"
        if hasattr(self.env, "record_operation_event"):
            self.env.record_operation_event(
                event_type="backup_run",
                entity_type="repository",
                entity="base_backup_repository",
                action="verify",
                status="success",
                correlation_id=f"backup-run-{self.case.case_id}",
                details={"manifest": "sha256", "validation": "pg_verifybackup"},
            )

    def _set_archive_delay(self, delay_seconds: int) -> None:
        if self._real_mode:
            container = self.env.deployment.container_name
            write_delay = subprocess.run(
                [
                    "docker", "exec", container, "bash", "-lc",
                    f"printf '%s\\n' {int(delay_seconds)} > /aiopsbench/archive/.aiopsbench-delay-seconds",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if write_delay.returncode != 0:
                raise RuntimeError(f"archive delay control file failed: {write_delay.stderr.strip()}")
        self.state["archive_delay_seconds"] = int(delay_seconds)

    def _start_pgbench(self) -> None:
        container = self.env.deployment.container_name
        self._pgbench_process = subprocess.Popen(
            [
                "docker", "exec", "-e", "PGPASSWORD=password", container,
                "pgbench", "-h", "127.0.0.1", "-U", "postgres", "-d", "testdb",
                "-c", "2", "-j", "2", "-T", str(self.case.workload_duration_seconds), "-P", "5",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

    def _start_marker_workload(self) -> None:
        self._stop_event.clear()
        self._marker_thread = threading.Thread(target=self._marker_loop, name="rpo-marker", daemon=True)
        self._marker_thread.start()

    def _switch_wal_with_event(self, correlation_id: str) -> str:
        """Force one real WAL switch and return the switched-out segment name.

        A restore point is emitted first: a switch requested while the insert
        position still sits on a fresh segment boundary is a no-op, so the
        burst would under-deliver exactly when the archive route is fast.
        """
        restore_point = subprocess.run(
            [
                "docker", "exec", "-e", "PGPASSWORD=password", self.env.deployment.container_name,
                "psql", "-U", "postgres", "-d", "testdb", "-At", "-c",
                f"SELECT pg_create_restore_point('{correlation_id}');",
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if restore_point.returncode != 0:
            if hasattr(self.env, "record_operation_event"):
                self.env.record_operation_event(
                    event_type="wal_switch",
                    entity_type="primary",
                    entity="primary_wal",
                    action="switch",
                    status="error",
                    correlation_id=correlation_id,
                    details={"reason": "restore_point_failed"},
                )
            return ""
        try:
            result = subprocess.run(
                [
                    "docker", "exec", "-e", "PGPASSWORD=password", self.env.deployment.container_name,
                    "psql", "-U", "postgres", "-d", "testdb", "-At", "-c",
                    "SELECT pg_walfile_name(pg_switch_wal());",
                ],
                capture_output=True,
                text=True,
                timeout=20,
            )
        except subprocess.TimeoutExpired:
            if hasattr(self.env, "record_operation_event"):
                self.env.record_operation_event(
                    event_type="wal_switch",
                    entity_type="primary",
                    entity="primary_wal",
                    action="switch",
                    status="timeout",
                    correlation_id=correlation_id,
                    details={"reason": "bounded_probe_timeout"},
                )
            return ""
        if result.returncode != 0 or not result.stdout.strip():
            return ""
        return result.stdout.strip().splitlines()[-1]

    def _marker_loop(self) -> None:
        while not self._stop_event.is_set():
            marker_id = f"marker-{time.time_ns()}"
            self._marker_count += 1
            if self._incident_archive_fault_active and self._marker_count % 3 == 0:
                self._engage_incident_archive_failure()
            sql = (
                "WITH inserted AS ("
                f"INSERT INTO aiopsbench_rpo.business_markers(marker_id, committed_at, checksum, payload) "
                f"VALUES ('{marker_id}', clock_timestamp(), md5('{marker_id}'), repeat('rpo', 64)) "
                "RETURNING marker_id, committed_at::text, checksum) "
                "SELECT marker_id, committed_at, checksum FROM inserted;"
            )
            result = subprocess.run(
                [
                    "docker", "exec", "-e", "PGPASSWORD=password", self.env.deployment.container_name,
                    "psql", "-U", "postgres", "-d", "testdb", "-At", "-F", "\t", "-c", sql,
                ],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if result.returncode == 0:
                fields = result.stdout.strip().split("\t")
                if len(fields) == 3:
                    marker = {"marker_id": fields[0], "committed_at": fields[1], "checksum": fields[2]}
                    wal_file_result = subprocess.run(
                        [
                            "docker", "exec", "-e", "PGPASSWORD=password", self.env.deployment.container_name,
                            "psql", "-U", "postgres", "-d", "testdb", "-At", "-c",
                            "SELECT pg_walfile_name(pg_current_wal_lsn());",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    if wal_file_result.returncode == 0 and wal_file_result.stdout.strip():
                        marker["wal_file"] = wal_file_result.stdout.strip().splitlines()[-1]
                    self._markers.append(marker)
                    if hasattr(self.env, "record_operation_event"):
                        self.env.record_operation_event(
                            event_type="marker_commit",
                            entity_type="business",
                            entity="business_marker_ledger",
                            action="commit",
                            status="success",
                            correlation_id=marker_id,
                            details={
                                "marker_id": marker_id,
                                "committed_at": marker["committed_at"],
                                "checksum": marker["checksum"],
                            },
                            timestamp_ms=int(_parse_postgres_timestamp(marker["committed_at"]).timestamp() * 1000),
                        )
                    self._switch_wal_with_event(f"wal-switch-{marker_id}")
            self._stop_event.wait(max(int(self.case.marker_interval_seconds), 1))

    def _engage_incident_archive_failure(self) -> None:
        """Force one real archiver failure inside the incident window.

        The failed attempt and its retry are real archive attempts, so the
        frozen target window carries the genuine operation-event retry/error
        sequence that the record-free candidate valleys cannot replay.
        """
        result = subprocess.run(
            [
                "docker", "exec", self.env.deployment.container_name, "bash", "-lc",
                "printf '1\\n' > /aiopsbench/archive/.aiopsbench-fail-next",
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "incident archive failure engagement failed: "
                f"{(result.stderr or result.stdout).strip()}"
            )

    def _wait_for_marker(self, minimum_count: int = 1) -> None:
        minimum_count = max(int(minimum_count), 1)
        interval = max(int(getattr(self.case, "marker_interval_seconds", 30)), 1)
        deadline = time.monotonic() + max(35, interval * (minimum_count + 1) + 5)
        while len(self._markers) < minimum_count and time.monotonic() < deadline:
            time.sleep(0.5)
        if len(self._markers) < minimum_count:
            raise RuntimeError(
                "marker workload did not commit enough real markers: "
                f"required={minimum_count}, observed={len(self._markers)}"
            )

    def _select_hidden_target(self, target: Mapping[str, str]) -> None:
        """Record trusted target state for a marker already in frozen history."""
        marker_time = _parse_postgres_timestamp(target["committed_at"])
        pitr_target_time = (marker_time + timedelta(seconds=2)).isoformat()
        self.state.update(
            {
                "target_marker_id": target["marker_id"],
                "marker_committed_at": target["committed_at"],
                "target_wal_file": target.get("wal_file"),
                "target_time": pitr_target_time,
                "target_checksum": target["checksum"],
                "last_recoverable_time": pitr_target_time,
                "archive_gap_recoverable": True,
            }
        )
        target_dt = _parse_postgres_timestamp(pitr_target_time)
        wait_seconds = (target_dt - datetime.now(timezone.utc)).total_seconds() + 0.5
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        fence_id = f"fence-{time.time_ns()}"
        fence_result = self.env.execute_sql_trusted(
            "INSERT INTO aiopsbench_rpo.recovery_fences(fence_id, committed_at) "
            f"VALUES ('{fence_id}', clock_timestamp());"
        )
        if _json_payload(fence_result).get("status") == "error":
            raise RuntimeError(f"post-target WAL fence setup failed: {fence_result}")
        post_target_wal = subprocess.run(
            [
                "docker", "exec", "-e", "PGPASSWORD=password", self.env.deployment.container_name,
                "psql", "-U", "postgres", "-d", "testdb", "-At", "-c",
                "SELECT pg_walfile_name(pg_current_wal_lsn());",
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if post_target_wal.returncode == 0 and post_target_wal.stdout.strip():
            self.state["post_target_wal_file"] = post_target_wal.stdout.strip().splitlines()[-1]
        self._switch_wal_with_event(f"wal-switch-fence-{fence_id}")

    def _recover_archive(self, target: str | None) -> str:
        if target and str(target).casefold() not in {"archive_repository", "archive", "primary"}:
            return json.dumps({"status": "error", "error": "archive recovery target is outside the declared repository"})
        replay_failure = json.dumps({
            "status": "error",
            "error": (
                "archive capacity replay missed the publication envelope: "
                f"segments={self.case.capacity_replay_segments}, "
                f"envelope_seconds={self.case.capacity_replay_envelope_seconds}, "
                "the current archive route tier cannot sustain the certification burst"
            ),
        })
        acceptance_seconds = int(getattr(self.case, "archive_capacity_acceptance_seconds", 0) or 0)
        capacity_verified = False
        if not self._real_mode:
            if acceptance_seconds > 0 and self.state.get("residual_emergency_route_active") is True:
                # Deterministic stand-in for the physical capacity replay: the
                # emergency transport tier cannot deliver a fresh segment at
                # the standard tier within the acceptance window.
                self.state["archive_recovered"] = False
                self.state["archive_capacity_verified"] = False
                self.state["archive_replay_verified"] = False
                return json.dumps({
                    "status": "error",
                    "action": "recover_archive",
                    "reason": "archive_capacity_acceptance_failed",
                    "error": (
                        "archive capacity replay did not reach the standard delivery "
                        "tier within the certification acceptance window"
                    ),
                }, default=str)
            if (
                int(self.case.capacity_replay_segments) > 0
                and self.state.get("archive_route_tier") == RPO_ARCHIVE_ROUTE_EMERGENCY
            ):
                # Deterministic mirror of the physical replay gate: the residual
                # emergency route tier cannot sustain the certification burst, so
                # the recovery fails until the route is re-pointed at the healthy
                # publication tier derived from the frozen history.
                return replay_failure
            capacity_verified = True
        else:
            write_delay = subprocess.run(
                [
                    "docker", "exec", self.env.deployment.container_name, "bash", "-lc",
                    "printf '0\\n' > /aiopsbench/archive/.aiopsbench-delay-seconds && "
                    "rm -f /aiopsbench/archive/.aiopsbench-fail-next",
                ],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if write_delay.returncode != 0:
                return json.dumps({"status": "error", "error": f"archive delay recovery failed: {write_delay.stderr.strip()}"})
            from src.execution.backup_rpo import repository_inventory, repository_listing

            try:
                before_inventory = repository_inventory(self.env)
            except RuntimeError as exc:
                return json.dumps({"status": "error", "error": f"archive inventory before replay failed: {exc}"})
            before_names = {
                str(item.get("wal_file"))
                for item in before_inventory.get("files", ())
                if item.get("wal_file")
            }
            if acceptance_seconds > 0:
                # Simple-case acceptance path: the stall window already
                # converged physically, so the repository is complete before
                # this action runs. Recovery still has to prove the delivery
                # pipeline end to end. An idle primary generates no WAL by
                # itself, so commit a real canary row first; the subsequent
                # switch then archives a brand-new segment and the canary
                # proves live delivery instead of passively re-reading files
                # that converged on their own.
                canary_id = f"archive-recover-{time.time_ns()}"
                canary_result = self.env.execute_sql_trusted(
                    "INSERT INTO aiopsbench_rpo.recovery_fences(fence_id, committed_at) "
                    f"VALUES ('{canary_id}', clock_timestamp());"
                )
                if _json_payload(canary_result).get("status") == "error":
                    raise RuntimeError(
                        f"archive recovery canary write failed: case={self.case.case_id}: {canary_result}"
                    )
                # Pin the canary segment by name so the acceptance judges only
                # this attempt's own delivery (earlier attempts may leave
                # throttled segments that arrive later and must not satisfy
                # this replay).
                canary_name_probe = _json_payload(self.env.execute_sql_trusted(
                    "SELECT pg_walfile_name(pg_current_wal_lsn())"
                ))
                if canary_name_probe.get("status") == "error" or not canary_name_probe.get("result"):
                    raise RuntimeError(
                        f"archive capacity canary segment probe failed: case={self.case.case_id}: {canary_name_probe}"
                    )
                canary_wal_file = str(canary_name_probe["result"][0][0])
                canary_started_ms = int(time.time() * 1000)
                self._switch_wal_with_event(f"archive-capacity-{self.case.case_id}")
                # The canary polls the cheap file listing and checksums only
                # the files whose durability it judges (the drained backlog
                # plus the target segments); a full-library sha256 sweep inside
                # a 0.5s polling loop cannot win against host load and turns
                # correct recoveries into infrastructure failures.
                deadline = time.monotonic() + acceptance_seconds
                poll_state: dict[str, Any] = {}
                while time.monotonic() < deadline:
                    try:
                        listing = repository_listing(self.env)
                        files = listing.get("files", ())
                        listed_names = {
                            str(item.get("wal_file"))
                            for item in files
                            if item.get("wal_file")
                        }
                        target_wal_file = self.state.get("target_wal_file")
                        required_wal_files = {item for item in (target_wal_file, self.state.get("post_target_wal_file")) if item}
                        names_to_judge = (listed_names - before_names) | set(required_wal_files)
                        continuity_ok = self._check_inventory_continuity(listing)
                        poll_state = {
                            "listed_files": len(files),
                            "required_wal_files": sorted(required_wal_files),
                            "required_missing": sorted(required_wal_files - listed_names),
                            "timeline_contiguous": continuity_ok,
                            "new_files_since_inventory": sorted(listed_names - before_names),
                        }
                        if files and required_wal_files <= listed_names and names_to_judge and continuity_ok:
                            # Judge only segments the listing already shows as
                            # durable: the canary segment may still be in flight
                            # (emergency-tier pacing), and checksumming an absent
                            # name would mask the poll diagnostics with a
                            # spurious sha256sum error.
                            checksum_names = (
                                names_to_judge | {canary_wal_file}
                                if canary_wal_file and canary_wal_file in listed_names
                                else names_to_judge
                            )
                            from src.execution.backup_rpo import archive_segment_checksums

                            checksums = archive_segment_checksums(self.env, checksum_names)
                            merged_files = [
                                (
                                    {**item, "sha256": checksums[item["wal_file"]]}
                                    if item.get("wal_file") in checksums
                                    else item
                                )
                                for item in files
                            ]
                            inventory = {
                                **listing,
                                "files": merged_files,
                            }
                            canary_entry = next(
                                (
                                    item
                                    for item in merged_files
                                    if item.get("wal_file") == canary_wal_file
                                ),
                                None,
                            )
                            accepted = self._canary_capacity_accepted(
                                canary_entry, canary_started_ms, acceptance_seconds
                            )
                            poll_state["canary_wal_file"] = canary_wal_file
                            poll_state["canary_capacity_accepted"] = accepted
                            if accepted:
                                self.state["archive_inventory"] = inventory
                                self.state["archive_inventory_complete"] = True
                                self.state["timeline_contiguous"] = continuity_ok
                                self.state["archive_capacity_verified"] = True
                                capacity_verified = True
                                break
                    except RuntimeError as exc:
                        poll_state = {"poll_error": str(exc)}
                    time.sleep(0.5)
                if not capacity_verified:
                    # The standard-tier capacity replay failure is a designed
                    # model-facing result: the agent observes it, attributes
                    # the throttled route, and restores the standard tier.
                    # Never raise it — a raised error would crash the whole
                    # scenario process instead of scoring the certification.
                    self.state["archive_recovered"] = False
                    self.state["archive_capacity_verified"] = False
                    self.state["archive_replay_verified"] = False
                    return json.dumps({
                        "status": "error",
                        "action": "recover_archive",
                        "reason": "archive_capacity_acceptance_failed",
                        "error": (
                            "archive capacity replay did not reach the standard delivery tier "
                            f"within the {acceptance_seconds}s certification acceptance window"
                        ),
                        "canary": canary_id,
                        "poll_state": poll_state,
                    }, default=str)
            else:
                self._switch_wal_with_event(f"archive-capacity-{self.case.case_id}")
                # Hard-case legacy canary: each poll snapshots the repository
                # directory at its own start, so on a busy host one full-sha256
                # poll can outlast the delivery and return stale contents; the
                # canary therefore takes a bounded number of polls (each
                # internally timeout-bounded) instead of a wall-clock budget
                # that a single slow poll would exhaust.
                for _ in range(3):
                    try:
                        inventory = repository_inventory(self.env)
                        files = inventory.get("files", ())
                        target_wal_file = self.state.get("target_wal_file")
                        required_wal_files = {item for item in (target_wal_file, self.state.get("post_target_wal_file")) if item}
                        target_archived = not required_wal_files or all(
                            any(
                                file_item.get("wal_file") == required and file_item.get("sha256")
                                for file_item in files
                            )
                            for required in required_wal_files
                        )
                        new_durable_files = [
                            item for item in files
                            if item.get("wal_file") not in before_names and item.get("sha256")
                        ]
                        continuity_ok = self._check_inventory_continuity(inventory)
                        if files and target_archived and continuity_ok and new_durable_files:
                            self.state["archive_inventory"] = inventory
                            self.state["archive_inventory_complete"] = True
                            self.state["timeline_contiguous"] = continuity_ok
                            capacity_verified = True
                            break
                    except RuntimeError:
                        pass
                    time.sleep(0.5)
                if not capacity_verified:
                    return json.dumps({"status": "error", "error": "archive recovery timed out before inventory became durable"})
                if int(self.case.capacity_replay_segments) > 0:
                    replay_passed = self._capacity_replay_passed(
                        segments=int(self.case.capacity_replay_segments),
                        envelope_seconds=int(self.case.capacity_replay_envelope_seconds),
                        burst_fn=self._capacity_replay_burst,
                        durable_fn=self._repository_segments_durable,
                    )
                    if not replay_passed:
                        return replay_failure
        self.state["archive_recovered"] = True
        self.state["archive_delay_seconds"] = 0
        self.state["archive_capacity_verified"] = capacity_verified
        self.state["archive_replay_verified"] = capacity_verified
        if hasattr(self.env, "record_operation_event"):
            self.env.record_operation_event(
                event_type="repository_sync",
                entity_type="repository",
                entity="archive_repository",
                action="replay",
                status="success",
                correlation_id=f"archive-replay-{self.case.case_id}",
                details={"durability": "verified", "segments": "replayed_and_new_canary"},
            )
        return json.dumps({"status": "success", "action": "recover_archive", "repository": "declared_archive_volume"})

    @staticmethod
    def _canary_capacity_accepted(
        canary_entry: Mapping[str, Any] | None,
        canary_started_ms: int | None,
        acceptance_seconds: int,
    ) -> bool:
        """Judge the canary delivery against the standard transport tier.

        The canary segment must be durably delivered with its repository
        write time within the acceptance window measured from the canary
        commit. A throttled route delivers the same segment far beyond the
        window even when the repository listing already looks complete.
        """
        if not isinstance(canary_entry, Mapping) or not canary_entry.get("sha256"):
            return False
        mtime = canary_entry.get("mtime")
        if not isinstance(mtime, (int, float)) or canary_started_ms is None:
            return False
        delivery_seconds = mtime * 1000.0 - canary_started_ms
        return 0.0 <= delivery_seconds <= acceptance_seconds * 1000.0

    def _restore_to_selected_target(self, target: str | None) -> str:
        # Mock agents do not receive the hidden marker.  Fall back to the
        # latest real marker if finalization had no eligible target, keeping
        # the PITR protocol executable instead of raising KeyError.
        if not self.state.get("target_time") and self._markers:
            self._select_hidden_target(self._markers[-1])
        if str(target or "").casefold() not in {"evaluator_selected", "selected_target"}:
            return json.dumps({"status": "error", "error": "PITR target must be evaluator_selected"})
        if self.state.get("target_recoverable") is False:
            result = {
                "status": "success",
                "certification_status": "rejected",
                "target_alias": "evaluator_selected",
                "last_recoverable_time": self.state.get("last_recoverable_time"),
                "reason": "archive continuity gap is not recoverable",
            }
            self.state.setdefault("pitr_attempts", []).append(result)
            return json.dumps({
                "status": result["status"],
                "certification_status": result["certification_status"],
                "target_alias": result["target_alias"],
                "last_recoverable_time": result["last_recoverable_time"],
                "reason": result["reason"],
            }, default=str)
        if not self.state.get("archive_recovered"):
            result = {
                "status": "error",
                "reason": "rpo_not_met",
                "target_alias": "evaluator_selected",
                "target_time": self.state.get("target_time"),
            }
            self.state.setdefault("pitr_attempts", []).append(result)
            return json.dumps({
                "status": result["status"],
                "reason": result["reason"],
                "target_alias": result["target_alias"],
            }, default=str)
        if self._real_mode:
            result = self._run_real_pitr()
        else:
            result = {
                "status": "success",
                "target_alias": "evaluator_selected",
                "target_time": self.state.get("target_time"),
                "timeline": 1,
                "marker_id": self.state.get("target_marker_id"),
                "marker_checksum": self.state.get("target_checksum", ""),
                "rpo_met": True,
                "restore_volume": self.state.get("topology", {}).get("restore_volume", "isolated"),
            }
        self.state.setdefault("pitr_attempts", []).append(result)
        if result.get("status") == "success":
            self.state.update(
                {
                    "pitr_reached_target": True,
                    "marker_boundary_valid": result.get("marker_id") == self.state.get("target_marker_id"),
                    "marker_checksum_valid": bool(result.get("marker_checksum")),
                    "rpo_met": bool(result.get("rpo_met")),
                    "restore_volume": result.get("restore_volume"),
                }
            )
        return json.dumps({
            key: value
            for key, value in result.items()
            if key not in {"target_time", "marker_id", "marker_checksum", "rpo_met"}
        }, default=str)

    def _run_real_pitr(self) -> dict[str, Any]:
        topology = self.env.rpo_topology
        target = str(self.state["target_time"]).replace("'", "''")
        target_marker_id = str(self.state["target_marker_id"]).replace("'", "''")
        container = topology.restore_container
        subprocess.run(["docker", "rm", "-f", container], capture_output=True, text=True)
        run = subprocess.run(
            [
                "docker", "run", "-d", "--name", container, "--network", topology.network_name,
                "-p", f"{topology.restore_port}:5432",
                "-v", f"{topology.backup_volume}:/aiopsbench/basebackups:ro",
                "-v", f"{topology.archive_volume}:/aiopsbench/archive:ro",
                "-v", f"{topology.restore_volume}:/var/lib/postgresql/data",
                "postgres:16", "sleep", "infinity",
            ],
            capture_output=True,
            text=True,
            # The floor must absorb docker-create and volume-attach latency
            # spikes on a busy shared host; a transiently slow start must not
            # crash the scenario process and invalidate an otherwise valid
            # certification run.
            timeout=180,
        )
        if run.returncode != 0:
            return {"status": "error", "reason": "restore_container_start_failed", "detail": run.stderr.strip()}
        restore_script = (
            "rm -rf /var/lib/postgresql/data/*; "
            "cp -a /aiopsbench/basebackups/base/. /var/lib/postgresql/data/; "
            "chown -R postgres:postgres /var/lib/postgresql/data; chmod 700 /var/lib/postgresql/data; "
            "mkdir -p /tmp/rpo-socket; chown postgres:postgres /tmp/rpo-socket; "
            "cat >> /var/lib/postgresql/data/postgresql.auto.conf <<'EOF'\n"
            "restore_command = 'cp /aiopsbench/archive/%f %p'\n"
            f"recovery_target_time = '{target}'\n"
            "recovery_target_action = 'promote'\nEOF\n"
            "touch /var/lib/postgresql/data/recovery.signal; "
            "su postgres -c '/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/data -l /tmp/rpo-restore.log -o \"-p 5432 -k /tmp/rpo-socket\" -t 600 -w start >/tmp/rpo-pgctl.log 2>&1'; "
            "for attempt in $(seq 1 120); do "
            "  recovery_state=$(PGPASSWORD=password psql -h /tmp/rpo-socket -U postgres -d testdb -At -c \"SELECT pg_is_in_recovery();\" 2>/dev/null || true); "
            "  test \"$recovery_state\" = f && break; "
            "  sleep 1; "
            "done; "
            "PGPASSWORD=password psql -h /tmp/rpo-socket -U postgres -d testdb -At -F '\t' -c "
            "\"SELECT marker_id, checksum FROM aiopsbench_rpo.business_markers "
            f"WHERE marker_id = '{target_marker_id}';\""
        )
        execute = subprocess.run(
            ["docker", "exec", container, "bash", "-lc", restore_script],
            capture_output=True,
            text=True,
            timeout=900,
        )
        if execute.returncode != 0:
            detail_parts = [execute.stderr.strip(), execute.stdout.strip()]
            log = subprocess.run(
                ["docker", "exec", container, "bash", "-lc", "cat /tmp/rpo-restore.log 2>/dev/null || true"],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if log.stdout.strip():
                detail_parts.append(log.stdout.strip())
            subprocess.run(["docker", "rm", "-f", container], capture_output=True, text=True)
            return {
                "status": "error",
                "reason": "pitr_restore_failed",
                "detail": "\\n".join(part for part in detail_parts if part),
            }
        subprocess.run(["docker", "rm", "-f", container], capture_output=True, text=True)
        fields = execute.stdout.strip().split("\t")
        marker_id = fields[0] if fields else ""
        checksum = fields[1] if len(fields) > 1 else ""
        return {
            "status": "success",
            "target_alias": "evaluator_selected",
            "target_time": self.state.get("target_time"),
            "timeline": 1,
            "marker_id": marker_id,
            "marker_checksum": checksum,
            "rpo_met": marker_id == self.state.get("target_marker_id") and checksum == self.state.get("target_checksum"),
            "restore_volume": topology.restore_volume,
        }

    def _set_archive_route(self, route: str) -> None:
        command = (
            RPO_ARCHIVE_EMERGENCY_COMMAND
            if route == RPO_ARCHIVE_ROUTE_EMERGENCY
            else RPO_ARCHIVE_COMMAND
        )
        # ALTER SYSTEM rejects transaction blocks: single-statement autocommit
        # queries, one per call (shared execute surface convention).
        result = self.env.execute_sql_trusted(
            f"ALTER SYSTEM SET archive_command = '{command}';"
        )
        if _json_payload(result).get("status") == "error":
            raise RuntimeError(
                f"archive route tier change failed: route={route}, result={result}"
            )
        reload_result = self.env.execute_sql_trusted("SELECT pg_reload_conf();")
        if _json_payload(reload_result).get("status") == "error":
            raise RuntimeError(
                f"archive route tier reload failed: route={route}, result={reload_result}"
            )
        self.state["archive_route_tier"] = route

    def _capacity_replay_burst(self) -> tuple[str, ...]:
        """Switch the replay burst segments and return the switched-out names.

        Duplicate names are retried: a switch over a fresh segment boundary
        cannot produce a new archiveable segment, and the replay verdict
        counts distinct durable segments.
        """
        switched: list[str] = []
        for attempt in range(3 * int(self.case.capacity_replay_segments)):
            if len(switched) >= int(self.case.capacity_replay_segments):
                break
            wal_name = self._switch_wal_with_event(
                f"capacity-replay-{attempt}-{self.case.case_id}"
            )
            if wal_name and wal_name not in switched:
                switched.append(wal_name)
        return tuple(switched)

    def _repository_segments_durable(self, wal_names: tuple[str, ...]) -> bool:
        """Check the named segments are durably present in the archive repository.

        The replay gate reads the repository itself, not pg_stat_archiver: the
        archiver's stat counter can lag tens of seconds behind the physical
        archive, which would false-fail the standard
        tier inside the publication envelope.
        """
        if not wal_names or any(not name for name in wal_names):
            return False
        name_list = " ".join(wal_names)
        result = subprocess.run(
            [
                "docker", "exec", self.env.deployment.container_name, "bash", "-lc",
                (
                    "cd /aiopsbench/archive && status=0; for f in " + name_list + "; do "
                    'if [ -f "$f" ]; then sha256sum "$f"; else echo "MISSING $f"; status=1; fi; done; '
                    "exit $status"
                ),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return False
        digests = {
            line.split()[0] for line in result.stdout.splitlines() if line.strip()
        }
        return len(digests) == len(wal_names)

    @staticmethod
    def _capacity_replay_passed(
        *,
        segments: int,
        envelope_seconds: int,
        burst_fn: Callable[[], tuple[str, ...]],
        durable_fn: Callable[[tuple[str, ...]], bool],
    ) -> bool:
        """Replay a bounded certification burst and require publication-tier delivery.

        The burst switches ``segments`` WAL segments; the replay passes only
        when the archiver makes every one of them durable in the archive
        repository inside the envelope. The standard route meets the
        publication tier; a transmission-throttled route keeps up with the
        idle cadence but physically cannot.
        """
        switched = burst_fn()
        if len(switched) != segments:
            return False
        deadline = time.monotonic() + envelope_seconds
        while time.monotonic() < deadline:
            if durable_fn(switched):
                return True
            time.sleep(0.25)
        return False

    def _stop_runtime_workload(self) -> None:
        self._stop_event.set()
        if self._marker_thread is not None:
            self._marker_thread.join(timeout=10)
            self._marker_thread = None
        if self._pgbench_process is not None and self._pgbench_process.poll() is None:
            self._pgbench_process.terminate()
            try:
                self._pgbench_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._pgbench_process.kill()
        self._pgbench_process = None

    def _assert_fault_ready(self, *, require_target: bool = True) -> None:
        if not self.state.get("backup_manifest_valid") and self._real_mode:
            raise RuntimeError("backup/archive setup blocker: backup manifest is not verified")
        if require_target and not self.state.get("target_marker_id"):
            raise RuntimeError("backup/archive setup blocker: hidden target marker was not selected")

    def _check_inventory_continuity(self, inventory: Mapping[str, Any]) -> bool:
        if "timeline_contiguous" in inventory:
            return inventory.get("timeline_contiguous") is True and not inventory.get("missing_segments")
        files = [item.get("wal_file", "") for item in inventory.get("files", ())]
        return bool(files) and all(len(name) >= 24 for name in files)

    def _topology_isolated(self) -> bool:
        topology = self.state.get("topology", {})
        return bool(
            topology
            and topology.get("primary_container") != topology.get("restore_container")
            and topology.get("backup_volume") != topology.get("restore_volume")
            and topology.get("archive_volume") != topology.get("restore_volume")
            and topology.get("primary_port") != topology.get("restore_port")
        )

    def _public_state(self) -> dict[str, Any]:
        return {
            key: value
            for key, value in self.state.items()
            if key not in {
                "controller",
                "pitr_attempts",
                "target_marker_id",
                "marker_committed_at",
                "target_time",
                "target_checksum",
                "target_wal_file",
                "post_target_wal_file",
                "rpo_met",
                "stall_window",
            }
        }

    def _current_public_status(self) -> dict[str, Any]:
        return {
            "backup_manifest_valid": self.state.get("backup_manifest_valid") is True,
            "archive_inventory_complete": self.state.get("archive_inventory_complete") is True,
            "timeline_contiguous": self.state.get("timeline_contiguous") is True,
            "archive_recovered": self.state.get("archive_recovered") is True,
            "primary_intact": self.state.get("primary_intact") is True,
            "topology_isolated": self._topology_isolated(),
            "archive_route_tier": self.state.get("archive_route_tier", RPO_ARCHIVE_ROUTE_STANDARD),
        }


class PgHealthCheckBackupRpoCertificationScenario(PostgresScenario):
    scenario_id = "pg_health_check_backup_rpo_certification"
    description = "Certifies a real PostgreSQL base backup and archive chain through an isolated PITR at a hidden business marker."
    cases = (_HARD_CASE, _SIMPLE_CASE)

    def build_fault_plan(self, case: PgHealthCheckBackupRpoCertificationCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgHealthCheckBackupRpoCertificationInjector,
                config={
                    "case_id": case.case_id,
                    "rpo_seconds": case.rpo_seconds,
                    "marker_interval_seconds": case.marker_interval_seconds,
                    "archive_delay_seconds": case.archive_delay_seconds,
                    "workload_duration_seconds": case.workload_duration_seconds,
                    "toolchain": "pg_basebackup+archive_command",
                },
            ),
        )


__all__ = [
    "PgHealthCheckBackupRpoCertificationCase",
    "PgHealthCheckBackupRpoCertificationForThroughputGapScenarioCase",
    "PgHealthCheckBackupRpoCertificationForThroughputGapSimpleScenarioCase",
    "PgHealthCheckBackupRpoCertificationInjector",
    "PgHealthCheckBackupRpoCertificationScenario",
]
