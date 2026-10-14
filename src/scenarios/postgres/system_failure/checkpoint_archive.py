"""Real PostgreSQL 16 checkpoint and archive dual-fault scenario."""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import quantiles
from typing import Mapping

from src.execution.history.records import HistoricalRecordSource
from src.scenarios.evaluation.postgres.system_failure.checkpoint_archive import (
    PgSystemFailureCheckpointArchiveForDualFaultEvaluatorCase,
    PgSystemFailureCheckpointArchiveForDualFaultSimpleEvaluatorCase,
)
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.history.records import HistoricalRecordSource
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.postgres.common import _json_object, _require_sql_success, _validate_sql_identifier
from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase, WorkloadProfile
from src.scenarios.frozen_history import DecoyDirection, DecoyKind, HistoryDecoySpec, FrozenHistorySpec
from src.workloads.tpcds import get_tpcds_query

from src.execution.specs import HostPortLayout, CaseResourceSpec, PostgresCaseRuntime, PostgresRuntimeSpec
from src.scenarios.base import DifficultyCalibration, FaultPlan, PostgresScenario, PostgresScenarioCase
from .checkpoint_archive_history import OLTP_PROFILE_NAME, CheckpointArchiveHistoryAdapter


SCENARIO_ID = "pg_system_failure_checkpoint_archive"
BASE_IMAGE_NAME = "aiopsbench-pg-tpcds:latest"
FAULT_IMAGE_PREFIX = "aiopsbench-pg-fault-pg-system-failure-checkpoint-archive"
PRIMARY_PORT = 15841
ARCHIVE_PORT = 15842
RESTORE_CANARY_PORT = 15843
ARCHIVE_TARGET_CONTAINER_PATH = "/var/lib/postgresql/archive_target"
BACKFILL_CONFIG_TABLE = "warehouse_refresh_controls"
ARCHIVE_POLICY_TABLE = "archive_transfer_policy"
ARCHIVE_GUARD_TABLE = "archive_transfer_limits"
ARCHIVE_TARGET_REGISTRY_TABLE = "archive_endpoint_registry"
ARCHIVE_BINDING_STATE_TABLE = "archive_endpoint_binding_state"
ARCHIVE_ROUTE_STATE_TABLE = "archive_endpoint_route_state"
ARCHIVE_REPOSITORY_TABLE = "archive_endpoint_storage_limits"
NORMAL_WAL_TABLE = "checkpoint_archive_normal_wal_events"
OLTP_TABLE = "checkpoint_archive_oltp_events"
ARCHIVE_SHADOW_DIRECTORY = "archive_endpoint_shadow"
ARCHIVE_AVAILABLE_FUNCTION = "archive_endpoint_available_mb"
ARCHIVE_SAFE_SPARE_FUNCTION = "archive_endpoint_safe_spare_mb"


def _sql_literal(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _sql_rows(env: object, sql: str) -> list:
    payload = env.execute_sql(sql)
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, Mapping) or payload.get("status") != "success":
        raise RuntimeError(f"checkpoint/archive SQL probe failed: {payload!r}")
    rows = payload.get("result")
    if not isinstance(rows, list):
        raise RuntimeError(f"checkpoint/archive SQL probe returned no rows: {payload!r}")
    return rows


def _execute_sql_for_injector(env: object, sql: str) -> str:
    """Use the trusted current-state surface for injector-owned SQL when available."""
    execute_sql_trusted = getattr(env, "execute_sql_trusted", None)
    if callable(execute_sql_trusted):
        return execute_sql_trusted(sql)
    return env.execute_sql(sql)


def _archive_target_container_subpath(archive_target_name: str) -> str:
    return f"{ARCHIVE_TARGET_CONTAINER_PATH}/{archive_target_name}"


def _healthy_archive_command(archive_target_name: str = "archive_target") -> str:
    target_path = _archive_target_container_subpath(archive_target_name)
    # Publish a segment only after cp has completed. PITR must never consume a
    # partially copied WAL file from the task-owned archive repository.
    return (
        f"test ! -f {target_path}/%f "
        f"&& cp %p {target_path}/.%f.tmp "
        f"&& mv -f {target_path}/.%f.tmp {target_path}/%f"
    )


def _archive_policy_script_path(archive_target_name: str) -> str:
    return f"{ARCHIVE_TARGET_CONTAINER_PATH}/.archive_transfer_{archive_target_name}_policy.sh"


def _policy_archive_command(archive_target_name: str) -> str:
    return f"bash {_archive_policy_script_path(archive_target_name)} %p %f"


def _fault_archive_command(delay_seconds: float, archive_target_name: str = "archive_target") -> str:
    target_path = _archive_target_container_subpath(archive_target_name)
    return (
        f"sleep {float(delay_seconds):.2f}; "
        f"test ! -f {target_path}/%f "
        f"&& cp %p {target_path}/.%f.tmp "
        f"&& mv -f {target_path}/.%f.tmp {target_path}/%f"
    )


def _archive_shadow_root(root: str | Path) -> Path:
    """Return the task-owned healthy archive-repository neighbor."""
    return Path(root) / ARCHIVE_SHADOW_DIRECTORY


def _archive_binding_lease_sql(*, expired: bool) -> str:
    """Return a deterministic public binding lease state for the case."""
    interval = "- interval '1 hour'" if expired else "+ interval '1 hour'"
    return f"clock_timestamp() {interval}"


def _archive_binding_generations(*, binding_fault: bool = False, route_fault: bool = False) -> tuple[int, int, int]:
    """Return public registry/state/route generations for one binding lifecycle."""
    if binding_fault and route_fault:
        raise ValueError("binding and route faults cannot be combined")
    if binding_fault:
        return 17, 16, 17
    if route_fault:
        return 17, 17, 16
    return 17, 17, 17


def _archive_route_worker_epochs(*, route_fault: bool = False) -> tuple[int, int]:
    """Return active and neighbor route-worker activation epochs."""
    return (16 if route_fault else 17), 17


def _fault_image_name(case_id: str) -> str:
    """Return the PostgreSQL fault snapshot name for this case."""
    return f"{FAULT_IMAGE_PREFIX}-{case_id.replace('_', '-')}:tpcds"


def _pitr_marker(run_id: str, random_value: int) -> str:
    """Keep the marker unique while respecting PostgreSQL's 63-byte limit."""
    run_digest = hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:24]
    return f"aiopsbench_{run_digest}_{int(random_value) % 1_000_000:06d}"


def _network_subnet_candidates(network_name: str):
    """Yield deterministic private /24s so exhausted Docker pools remain usable."""
    digest = hashlib.sha256(network_name.encode("utf-8")).digest()
    start = int.from_bytes(digest[:2], "big") % 240
    for offset in range(240):
        third_octet = 16 + ((start + offset) % 240)
        yield f"10.254.{third_octet}.0/24"


def _docker_named_resource_exists(resource_kind: str, resource_name: str) -> bool:
    """Check one task-owned Docker resource without an unbounded inspect call."""
    if resource_kind not in {"network", "volume"}:
        raise ValueError(f"unsupported Docker resource kind: {resource_kind!r}")
    result = subprocess.run(
        [
            "docker", resource_kind, "ls", "--filter", f"name={resource_name}",
            "--format", "{{.Name}}",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Docker {resource_kind} resource lookup failed: name={resource_name!r}, "
            f"error={result.stderr.strip()!r}"
        )
    return any(line.strip() == resource_name for line in result.stdout.splitlines())


class _ArchiveHandler(BaseHTTPRequestHandler):
    """A real archive-target endpoint used for health and inventory checks."""

    server_version = "AiOpsBenchArchiveTarget/1.0"

    def do_GET(self):  # noqa: N802 - stdlib HTTP handler API
        if self.path == "/healthz":
            body = b"ok\n"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def log_message(self, *_args):
        return


class _ArchiveService:
    def __init__(self, root: Path, port: int):
        self.root = root
        self.port = int(port)
        self.server = None
        self.thread = None

    def start(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        if self.server is not None:
            return
        try:
            self.server = ThreadingHTTPServer(("127.0.0.1", self.port), _ArchiveHandler)
        except OSError as exc:
            raise RuntimeError(f"archive service port {self.port} is unavailable") from exc
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
        if self.thread is not None:
            self.thread.join(timeout=3)
        self.server = None
        self.thread = None


class CheckpointArchiveDeployment(PGDockerDeployment):
    """PG deployment with task-owned WAL/archive resources and an isolated canary port."""

    def __init__(
        self,
        *,
        archive_target_root: str,
        archive_target_name: str,
        wal_volume_name: str,
        network_name: str,
        archive_port: int,
        restore_port: int,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.archive_target_root = os.path.abspath(archive_target_root)
        if not re.fullmatch(r"[a-z0-9][a-z0-9_]{0,62}", archive_target_name):
            raise ValueError(f"archive_target_name is not a valid directory name: {archive_target_name!r}")
        self.archive_target_name = archive_target_name
        if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{0,127}", wal_volume_name):
            raise ValueError(f"wal_volume_name is not a valid Docker resource name: {wal_volume_name!r}")
        if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{0,127}", network_name):
            raise ValueError(f"network_name is not a valid Docker resource name: {network_name!r}")
        self.wal_volume_name = wal_volume_name
        self.network_name = network_name
        self.archive_port = int(archive_port)
        self.restore_port = int(restore_port)
        self._owned_volume = False
        self._owned_network = False

    def _ensure_task_resources(self) -> None:
        os.makedirs(self.archive_target_root, exist_ok=True)
        # The archive command runs as the container's postgres user while the
        # bind mount is created by the host user. This task-owned directory
        # must be writable by that database user for a real, delayed archive
        # target rather than an accidental permanent permission failure.
        os.chmod(self.archive_target_root, 0o777)
        active_root = Path(self.archive_target_root) / self.archive_target_name
        active_root.mkdir(parents=True, exist_ok=True)
        os.chmod(active_root, 0o777)
        shadow_root = _archive_shadow_root(self.archive_target_root)
        shadow_root.mkdir(parents=True, exist_ok=True)
        os.chmod(shadow_root, 0o777)
        volume = subprocess.run(
            ["docker", "volume", "inspect", self.wal_volume_name],
            capture_output=True,
            text=True,
        )
        if volume.returncode != 0:
            subprocess.run(["docker", "volume", "create", self.wal_volume_name], check=True, capture_output=True)
            self._owned_volume = True
        if not _docker_named_resource_exists("network", self.network_name):
            errors = []
            for subnet in _network_subnet_candidates(self.network_name):
                created = subprocess.run(
                    [
                        "docker", "network", "create",
                        "--label", "aiopsbench.owner=pg-hc-mf01",
                        "--subnet", subnet,
                        self.network_name,
                    ],
                    capture_output=True,
                    text=True,
                )
                if created.returncode == 0:
                    self._owned_network = True
                    break
                errors.append(created.stderr.strip() or f"returncode={created.returncode}")
            else:
                raise RuntimeError(
                    f"Could not create isolated PostgreSQL network {self.network_name!r}: "
                    f"tried_subnets=240, last_error={errors[-1] if errors else 'unknown'}"
                )

    def _build_docker_run_command(self, for_init: bool = False) -> list:
        command = super()._build_docker_run_command(for_init=for_init)
        image = "postgres:16" if for_init else self.image_name
        try:
            image_index = command.index(image)
        except ValueError as exc:
            raise RuntimeError(f"Could not locate image in PG docker command: {command!r}") from exc
        wal_target = "/aiopsbench_wal_seed" if for_init else "/var/lib/postgresql/data_fat/pg_wal"
        command[image_index:image_index] = [
            "-v", f"{self.wal_volume_name}:{wal_target}",
            "-v", f"{self.archive_target_root}:{ARCHIVE_TARGET_CONTAINER_PATH}",
            "-p", f"{self.restore_port}:5433",
        ]
        return command

    def initialize_dataset_container(self):
        super().initialize_dataset_container()
        stop = subprocess.run(
            [
                "docker", "exec", self.container_name,
                "bash", "-ec",
                "su - postgres -c '/usr/lib/postgresql/16/bin/pg_ctl stop -D /var/lib/postgresql/data_fat -m fast -w'",
            ],
            capture_output=True,
            text=True,
        )
        status = subprocess.run(
            [
                "docker", "exec", self.container_name,
                "bash", "-ec",
                "su - postgres -c '/usr/lib/postgresql/16/bin/pg_ctl status -D /var/lib/postgresql/data_fat'",
            ],
            capture_output=True,
            text=True,
        )
        if stop.returncode != 0 and status.returncode == 0:
            raise RuntimeError(
                f"Failed to stop initialized PostgreSQL before seeding WAL volume {self.wal_volume_name!r}: "
                f"stop_stdout={stop.stdout.strip()!r}, stop_stderr={stop.stderr.strip()!r}, "
                f"status={status.stdout.strip()!r} {status.stderr.strip()!r}"
            )
        source_root = tempfile.mkdtemp(prefix="aiopsbench-pg-sf-ca01-wal-source-")
        try:
            export = subprocess.run(
                [
                    "docker", "cp",
                    f"{self.container_name}:/var/lib/postgresql/data_fat/pg_wal/.",
                    source_root,
                ],
                capture_output=True,
                text=True,
            )
            if export.returncode != 0:
                raise RuntimeError(
                    f"Failed to export consistent WAL from initialized container {self.container_name!r}: "
                    f"{export.stderr.strip()}"
                )
            seed = subprocess.run(
                [
                    "docker", "run", "--rm", "--entrypoint", "bash",
                    "-v", f"{self.wal_volume_name}:/aiopsbench_wal_seed",
                    "-v", f"{source_root}:/aiopsbench_wal_source:ro",
                    "postgres:16", "-ec",
                    "cp -a /aiopsbench_wal_source/. /aiopsbench_wal_seed/ "
                    "&& mkdir -p /aiopsbench_wal_seed/archive_status "
                    "&& chown -R 999:999 /aiopsbench_wal_seed",
                ],
                capture_output=True,
                text=True,
            )
            if seed.returncode != 0:
                raise RuntimeError(
                    f"Failed to seed task-owned WAL volume {self.wal_volume_name!r}: "
                    f"{seed.stderr.strip()}"
                )
        finally:
            shutil.rmtree(source_root, ignore_errors=True)

    def deploy(self):
        self._ensure_task_resources()
        super().deploy()

    def teardown(self):
        super().teardown()
        if self._owned_volume:
            subprocess.run(["docker", "volume", "rm", self.wal_volume_name], capture_output=True, text=True)
        if self._owned_network:
            subprocess.run(["docker", "network", "rm", self.network_name], capture_output=True, text=True)
        shutil.rmtree(self.archive_target_root, ignore_errors=True)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureCheckpointArchiveCase(PostgresScenarioCase):
    base_image_name: str
    fault_image_name: str
    workload_tag: str
    dataset_scale: int
    write_job_name: str
    write_table: str
    archive_target_name: str
    archive_target_root: str
    wal_volume_name: str
    network_name: str
    checkpoint_timeout_fault: str
    max_wal_size_fault: str
    checkpoint_completion_target_fault: str
    checkpoint_timeout_target: str
    max_wal_size_target: str
    checkpoint_completion_target_target: str
    archive_delay_fault_seconds: float
    archive_fault_start_delay_seconds: float = 0.0
    replay_seconds: int
    wal_space_budget_bytes: int
    max_checkpoint_req_delta: int
    max_checkpoint_write_ms: float
    min_tps: float
    max_p99_ms: float
    base_backup_noise: bool
    backfill_batch_rows_fault: int
    backfill_pause_ms_fault: int
    backfill_batch_rows_target: int
    backfill_pause_ms_target: int
    maintenance_job_name: str
    maintenance_table: str
    maintenance_batch_rows: int
    maintenance_pause_ms: int
    backfill_payload_repeat: int
    maintenance_payload_repeat: int
    archive_policy_name: str
    archive_segments_per_minute_fault: int
    archive_pause_ms_fault: int
    archive_segments_per_minute_target: int
    archive_pause_ms_target: int
    archive_guard_name: str
    archive_guard_enabled_fault: bool
    archive_guard_segments_per_minute_fault: int
    archive_guard_pause_ms_fault: int
    archive_guard_enabled_target: bool
    archive_repository_name: str
    archive_neighbor_target_name: str
    archive_neighbor_repository_name: str
    archive_repository_reserved_mb: int
    archive_repository_quota_mb_fault: int
    archive_repository_quota_mb_target: int
    archive_repository_safe_spare_mb: int
    archive_binding_fault_repository_name: str
    archive_binding_fault_target_path: str
    archive_binding_fault: bool = False
    archive_route_fault: bool = False
    # Publish the safe repair profile in the current-state control tables. The
    # Simple Case keeps the healthy profile out of current state so it
    # is only observable in the frozen history.
    publish_safe_profiles: bool = True
    # Run the governed write jobs at their healthy profile through the normal
    # capture so the frozen history records the pre-incident batch cadence.
    run_healthy_workload_in_normal_capture: bool = False
    # Require the healthy neighbor job's control row to survive the repair.
    protect_unrelated_job_profile: bool = False
    archive_port: int = ARCHIVE_PORT
    restore_port: int = RESTORE_CANARY_PORT
    primary_port: int = PRIMARY_PORT


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureCheckpointArchiveForCheckpointArchiveDualFaultScenarioCase(
    PgSystemFailureCheckpointArchiveCase
):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureCheckpointArchiveForCheckpointArchiveDualFaultSimpleScenarioCase(
    PgSystemFailureCheckpointArchiveCase
):
    pass


def _reference_report(case: PgSystemFailureCheckpointArchiveCase) -> dict:
    report = {
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "WAL/FPI growth -> requested checkpoint -> checkpoint write/sync and device queue -> OLTP p99",
                    "entity": case.write_job_name,
                    "evidence": ["write job WAL/FPI growth preceded requested checkpoints, checkpoint write/sync and device queue pressure, then OLTP p99 worsened"],
                },
                {
                    "type": "finding",
                    "factor": "archive throughput fell below WAL generation -> delivery retries -> ready count and oldest-unarchived age -> pg_wal space -> PITR risk",
                    "entity": case.archive_target_name,
                    "evidence": ["archive delivery fell below generation, retries increased, ready files and oldest age grew, pg_wal space narrowed, and PITR risk increased"],
                },
                {
                    "type": "finding",
                    "factor": "active archive registry, lease state, route state and route worker activation share one valid binding generation",
                    "entity": case.archive_target_name,
                    "evidence": ["registry, binding state, route state and route worker activation are coherent and the lease is valid"],
                },
                {
                    "type": "finding",
                    "factor": "dual fault",
                    "entity": "checkpoint and archive",
                    "evidence": ["both causal directions remained after separating the timelines"],
                },
                {
                    "type": "finding",
                    "factor": "write job and archive target",
                    "entity": case.write_job_name,
                    "evidence": ["the named write job was the affected writer"],
                },
                {
                    "type": "finding",
                    "factor": "target archive target",
                    "entity": case.archive_target_name,
                    "evidence": ["the named archive target was the affected delivery endpoint"],
                },
                {
                    "type": "finding",
                    "factor": "timed checkpoint, base backup, and TPC-DS report I/O were excluded as root causes",
                    "entity": "history candidates",
                    "evidence": ["timed checkpoint and backup/report events did not explain the sustained two-chain impact"],
                },
                {
                    "type": "finding",
                    "factor": "normal WAL burst was excluded because archive delivery caught up and it did not produce sustained OLTP impact",
                    "entity": "history candidates",
                    "evidence": ["the normal WAL burst was followed by archive catch-up without sustained OLTP impact"],
                },
                {
                    "type": "finding",
                    "factor": "archive target binding points to the active repository with sufficient capacity headroom",
                    "entity": case.archive_target_name,
                    "evidence": ["the active binding and published repository spare-capacity rule were both checked"],
                },
                {
                    "type": "finding",
                    "factor": "excluded timed checkpoint or backup/read benign window",
                    "entity": "history candidates",
                    "evidence": ["the timed checkpoint and backup/read windows were compared and excluded as benign"],
                },
            ]
        },
        "outcome": {
            "changes": ["governed the write/checkpoint chain and restored archive throughput"],
            "verification": ["joint replay, WAL headroom and marker PITR passed"],
        },
        "summary": "Checkpoint pressure and archive backlog were separate physical causes and both were recovered.",
    }
    return report


def _workload_profiles(simple: bool) -> tuple[WorkloadProfile, ...]:
    # q3 is a bounded light report that completes on the Simple resource
    # profile. q1's correlated return calculation can turn normal capture into
    # an all-failed regime instead of providing useful read noise.
    query = get_tpcds_query("q3" if simple else "q75")
    profiles = [
        WorkloadProfile(
            name=OLTP_PROFILE_NAME,
            sql=(
                f"INSERT INTO {OLTP_TABLE} (payload) "
                "SELECT repeat('o', 128) FROM generate_series(1, "
                "1 + (extract(epoch FROM clock_timestamp())::bigint % 8));"
            ),
            qps=0.25,
            tier="LIGHT",
            commit=True,
            application_name=OLTP_PROFILE_NAME,
        ),
        WorkloadProfile(
            name="checkpoint_archive_tpcds_report_simple" if simple else "checkpoint_archive_tpcds_report",
            sql=query,
            qps=0.08 if simple else 0.05,
            tier="MEDIUM" if simple else "HEAVY",
            application_name="checkpoint_archive_tpcds_report",
        ),
    ]
    if simple:
        # A bounded read-only report shares the writer identity and emits a
        # handled health-probe warning. It cannot generate the writer's WAL/FPI
        # or the active archive backlog.
        profiles.append(
            WorkloadProfile(
                name="checkpoint_archive_tpcds_catalog_report",
                sql=(
                    "DO $$ "
                    "BEGIN "
                    "RAISE EXCEPTION 'archive delivery health probe timeout'; "
                    "EXCEPTION WHEN OTHERS THEN "
                    "RAISE WARNING 'archive delivery health probe timeout was handled for refresh catalog'; "
                    "END $$; "
                    "SELECT i_category, count(*) AS item_count, "
                    "round(avg(i_current_price)::numeric, 2) AS avg_price "
                    "FROM public.item GROUP BY i_category "
                    "ORDER BY i_category LIMIT 20;"
                ),
                qps=0.40,
                tier="LIGHT",
                application_name="warehouse_refresh_simple",
                transactional=False,
            )
        )
    else:
        profiles.extend((
            WorkloadProfile(
                name="checkpoint_archive_tpcds_report_secondary",
                sql=get_tpcds_query("q14"),
                qps=0.02,
                tier="MEDIUM",
                application_name="checkpoint_archive_tpcds_report_secondary",
            ),
            WorkloadProfile(
                name="checkpoint_archive_normal_wal_burst",
                sql=(
                    f"INSERT INTO {NORMAL_WAL_TABLE} (payload) "
                    "SELECT repeat('w', 160) FROM generate_series(1, 4);"
                ),
                qps=0.25,
                tier="LIGHT",
                commit=True,
                application_name="checkpoint_archive_normal_wal_burst",
            ),
        ))
    return tuple(profiles)


def _report_replay_query_name(case: PgSystemFailureCheckpointArchiveCase) -> str:
    """Replay the report profile declared by each Case's live workload."""
    return "q3" if case.case_id.endswith("_simple") else "q75"


def _hard_history_spec() -> FrozenHistorySpec:
    return FrozenHistorySpec(
        schema_version=1,
        duration_seconds=43_200,
        normal_capture_seconds=120,
        fault_capture_seconds=180,
        base_step_seconds=2,
        overview_step_seconds=300,
        block_min_seconds=60,
        block_max_seconds=120,
        transition_seconds=20,
        target_age_seconds_range=(1_800, 10_800),
        required_metrics=(
            "wal_generation", "checkpoint_activity", "archive_delivery", "archive_backlog",
            "storage_pressure", "service_slo", "batch_progress",
        ),
        record_sources=(
            HistoricalRecordSource.OPERATION_EVENT,
            HistoricalRecordSource.TOPSQL,
            HistoricalRecordSource.COMPONENT_LOG,
        ),
        decoys=(
            HistoryDecoySpec(
                decoy_id="report-io",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="service_slo",
                # The live report profile is a real normal-window workload
                # source. Its p99 can be flat on a lightly provisioned worker,
                # while throughput remains a measured changing signal.
                field="transactions_per_sec",
                target=None,
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=40,
                minimum_deviation_mad=0.01,
            ),
            HistoryDecoySpec(
                decoy_id="backup-read",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="storage_pressure",
                field="device_weighted_io_ms_per_sec",
                target=None,
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=40,
                minimum_deviation_mad=0.01,
            ),
            HistoryDecoySpec(
                decoy_id="normal-oltp-wave",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="wal_generation",
                field="bytes_per_sec",
                target=None,
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=40,
                minimum_deviation_mad=0.01,
            ),
            HistoryDecoySpec(
                decoy_id="metric-only-checkpoint-wave",
                # Checkpoint-shaped pressure with no matching operation
                # event.  It competes on the same causal family and requires
                # the Agent to validate the checkpoint/archive sequence.
                kind=DecoyKind.METRIC_ONLY,
                metric="checkpoint_activity",
                field="requested_per_min",
                target=None,
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                amplitude_mad=2.0,
            ),
            HistoryDecoySpec(
                decoy_id="metric-only-archive-wave",
                # Archive backlog alone is not evidence of the dual fault;
                # the bounded record query must establish the paired cause.
                kind=DecoyKind.METRIC_ONLY,
                metric="archive_backlog",
                field="ready_files",
                target=None,
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                amplitude_mad=2.0,
            ),
        ),
        max_points_per_series=3_000,
        max_scalar_samples_per_response=12_000,
        max_history_query_seconds=900,
        max_history_records_per_response=100,
    )


def _simple_metric_history_spec() -> FrozenHistorySpec:
    return FrozenHistorySpec(
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
        # Keep the short case smaller in duration and entity count, but retain
        # the complete public evidence surface for both physical chains. The
        # generic qps/disk_io/active_connections series remain useful context;
        # WAL/checkpoint/archive/service metrics are the causal signals.
        required_metrics=(
            "qps", "disk_io", "active_connections",
            "wal_generation", "checkpoint_activity", "archive_delivery",
            "archive_backlog", "storage_pressure", "service_slo", "batch_progress",
        ),
        record_sources=(HistoricalRecordSource.OPERATION_EVENT,),
        decoys=(
            HistoryDecoySpec(
                decoy_id="captured-read-burst",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="disk_io",
                field="read_mb_per_second",
                target=None,
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                minimum_deviation_mad=0.01,
            ),
            HistoryDecoySpec(
                decoy_id="metric-only-qps-burst",
                kind=DecoyKind.METRIC_ONLY,
                metric="qps",
                field="queries_per_second",
                target=None,
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                amplitude_mad=2.0,
            ),
            HistoryDecoySpec(
                decoy_id="metric-only-checkpoint-burst",
                kind=DecoyKind.METRIC_ONLY,
                metric="checkpoint_activity",
                field="requested_per_min",
                target=None,
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                amplitude_mad=2.0,
            ),
            HistoryDecoySpec(
                decoy_id="metric-only-archive-burst",
                kind=DecoyKind.METRIC_ONLY,
                metric="archive_backlog",
                field="ready_files",
                target=None,
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                amplitude_mad=2.0,
            ),
        ),
        max_points_per_series=2_000,
        max_scalar_samples_per_response=8_000,
        max_history_query_seconds=1_200,
        max_history_records_per_response=120,
    )


_HARD_CASE = PgSystemFailureCheckpointArchiveForCheckpointArchiveDualFaultScenarioCase(
    case_id="checkpoint_archive_dual_fault",
    case_no=0,
    evaluator=PgSystemFailureCheckpointArchiveForDualFaultEvaluatorCase,
    reference_report={"diagnosis": {"conditions": []}, "outcome": {"changes": [], "verification": []}, "summary": "Reference report is replaced below."},
    title="Historical transaction latency spikes with WAL headroom and recovery-risk signals.",
    alert="[CRITICAL] Historical checkout traffic showed recurring latency spikes while WAL headroom narrowed and the recovery objective was at risk. Read the compact metric overview first, select one candidate window, then use bounded history queries before applying bounded workload or recovery-capacity changes; never scan the full history. Preserve durability, do not restart the primary, and do not stop all writes. The current service is quiet. Prove the next mixed write/report/backup window is safe.",
    initial_state={"status": "quiet", "symptoms": "historical transaction latency spikes, narrowing WAL headroom, and recovery risk", "authorization": "bounded changes within the published workload and recovery scope are allowed; durability and primary availability must remain intact"},
    expected_target={"status": "recovered", "replay": "write/report/backup replay passes", "pitr": "random marker restore succeeds", "write_control": "target write job remains within its published safe profile"},
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.789062,
        reference_run_ids=(
            "logs/traces/run_pg_system_failure_checkpoint_archive_checkpoint_archive_dual_fault_"
            "MockLLMAgent.json",
        ),
    ),
    background_workload=BackgroundWorkloadSpec(
        profiles=_workload_profiles(False),
        worker_count=1,
        seed=0xCF01,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        warmup_seconds=2,
    ),
    runtime=PostgresCaseRuntime(
        host_ports=HostPortLayout(offsets=(0, 1, 2)),
        resources=CaseResourceSpec(worker_physical_cores=2, worker_memory_mb=2048, container_cpu_limit=2.0, container_memory_mb=2048),
        parameters=PostgresRuntimeSpec(parameters=(
            ("archive_mode", "on"),
            ("wal_level", "replica"),
            ("max_wal_senders", "4"),
            ("track_io_timing", "on"),
            ("log_checkpoints", "on"),
            ("shared_preload_libraries", "pg_stat_statements"),
            ("logging_collector", "on"),
            ("log_destination", "stderr"),
            ("log_directory", "/var/log/postgresql"),
            ("log_filename", "postgresql-%Y-%m-%d_%H%M%S.log"),
        )),
    ),
    base_image_name=BASE_IMAGE_NAME,
    fault_image_name=_fault_image_name("checkpoint_archive_dual_fault"),
    workload_tag="tpcds",
    dataset_scale=1,
    write_job_name="warehouse_refresh_hard",
    write_table="warehouse_refresh_events_hard",
    archive_target_name="archive_endpoint_hard",
    archive_target_root="/tmp/aiopsbench-pg-system-failure-checkpoint-archive-checkpoint-archive-dual-fault",
    wal_volume_name="aiopsbench-pg-system-failure-checkpoint-archive-checkpoint-archive-dual-fault-wal",
    network_name="aiopsbench-pg-system-failure-checkpoint-archive-checkpoint-archive-dual-fault-net",
    checkpoint_timeout_fault="30s",
    max_wal_size_fault="32MB",
    checkpoint_completion_target_fault="0.1",
    checkpoint_timeout_target="5min",
    max_wal_size_target="256MB",
    checkpoint_completion_target_target="0.9",
    archive_delay_fault_seconds=3.0,
    replay_seconds=8,
    wal_space_budget_bytes=192 * 1024 * 1024,
    max_checkpoint_req_delta=16,
    max_checkpoint_write_ms=5000.0,
    min_tps=1.0,
    max_p99_ms=2500.0,
    base_backup_noise=True,
    backfill_batch_rows_fault=800,
    backfill_pause_ms_fault=250,
    backfill_batch_rows_target=120,
    backfill_pause_ms_target=750,
    maintenance_job_name="warehouse_maintenance_hard",
    maintenance_table="warehouse_maintenance_events_hard",
    maintenance_batch_rows=40,
    maintenance_pause_ms=1000,
    backfill_payload_repeat=2048,
    maintenance_payload_repeat=256,
    archive_policy_name="archive_transfer_policy_hard",
    archive_segments_per_minute_fault=24,
    archive_pause_ms_fault=2500,
    archive_segments_per_minute_target=120,
    archive_pause_ms_target=0,
    archive_guard_name="archive_transfer_limit_hard",
    archive_guard_enabled_fault=True,
    archive_guard_segments_per_minute_fault=24,
    archive_guard_pause_ms_fault=2500,
    archive_guard_enabled_target=False,
    archive_repository_name="archive_storage_pool_hard",
    archive_neighbor_target_name="archive_endpoint_neighbor_hard",
    archive_neighbor_repository_name="archive_storage_pool_neighbor_hard",
    archive_repository_reserved_mb=496,
    archive_repository_quota_mb_fault=512,
    archive_repository_quota_mb_target=752,
    archive_repository_safe_spare_mb=256,
    frozen_history=_hard_history_spec(),
    frozen_history_adapter=CheckpointArchiveHistoryAdapter(),
    archive_binding_fault_repository_name="archive_endpoint_unbound",
    archive_binding_fault_target_path=f"{ARCHIVE_TARGET_CONTAINER_PATH}/archive_endpoint_unbound",
    archive_route_fault=False,
    # The Hard Case applies the same information boundary as the Simple Case:
    # the safe repair profile is absent from current state, and the healthy
    # batch cadence is only observable as frozen-history job_batch events in
    # the normal capture window.
    publish_safe_profiles=False,
    run_healthy_workload_in_normal_capture=True,
)


_HARD_CASE = replace(_HARD_CASE, reference_report=_reference_report(_HARD_CASE))


_SIMPLE_CASE = PgSystemFailureCheckpointArchiveForCheckpointArchiveDualFaultSimpleScenarioCase(
    case_id="checkpoint_archive_dual_fault_simple",
    case_no=1,
    evaluator=PgSystemFailureCheckpointArchiveForDualFaultSimpleEvaluatorCase,
    reference_report={"diagnosis": {"conditions": []}, "outcome": {"changes": [], "verification": []}, "summary": "Reference report is replaced below."},
    title="PostgreSQL 16 historical write latency and recovery risk during a mixed workload.",
    alert="[SEV2] Recent OLTP writes showed short latency spikes and the recovery objective is at risk during the next mixed workload window. Read the compact metric overview first, select one candidate window, then use bounded database and business-workload controls within the published incident scope; never scan the full history. Do not disable durability, delete recovery data, restart the primary, or change unrelated jobs. The incident is currently quiet. Investigate the historical evidence, restore safe operation, and prove recovery with a small repeatable replay.",
    initial_state={"status": "degraded", "symptom": "OLTP latency spikes and recovery risk during a mixed workload window", "scope": "bounded database and business-workload controls are available; unrelated jobs and recovery data are protected"},
    expected_target={"status": "recovered", "replay": "joint replay passes", "pitr": "marker restore succeeds", "write_control": "target write job remains within its published safe profile"},
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.693548,
        reference_run_ids=(
            "logs/traces/run_pg_system_failure_checkpoint_archive_checkpoint_archive_dual_fault_simple_"
            "MockLLMAgent.json",
        ),
    ),
    background_workload=BackgroundWorkloadSpec(
        profiles=_workload_profiles(True),
        worker_count=2,
        seed=0xCF02,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        warmup_seconds=2,
    ),
    frozen_history=_simple_metric_history_spec(),
    frozen_history_adapter=CheckpointArchiveHistoryAdapter(),
    runtime=PostgresCaseRuntime(
        host_ports=HostPortLayout(offsets=(0, 1, 2)),
        resources=CaseResourceSpec(worker_physical_cores=1, worker_memory_mb=1024, container_cpu_limit=0.75, container_memory_mb=768),
        parameters=PostgresRuntimeSpec(parameters=(
            ("archive_mode", "on"),
            ("wal_level", "replica"),
            ("max_wal_senders", "2"),
            ("track_io_timing", "on"),
            ("log_checkpoints", "on"),
            ("shared_preload_libraries", "pg_stat_statements"),
            ("logging_collector", "on"),
            ("log_destination", "stderr"),
            ("log_directory", "/var/log/postgresql"),
            ("log_filename", "postgresql-%Y-%m-%d_%H%M%S.log"),
        )),
    ),
    base_image_name=BASE_IMAGE_NAME,
    fault_image_name=_fault_image_name("checkpoint_archive_dual_fault_simple"),
    workload_tag="tpcds",
    dataset_scale=1,
    write_job_name="warehouse_refresh_simple",
    write_table="warehouse_refresh_events_simple",
    archive_target_name="archive_endpoint_simple",
    archive_target_root="/tmp/aiopsbench-pg-system-failure-checkpoint-archive-checkpoint-archive-dual-fault-simple",
    wal_volume_name="aiopsbench-pg-system-failure-checkpoint-archive-checkpoint-archive-dual-fault-simple-wal",
    network_name="aiopsbench-pg-system-failure-checkpoint-archive-checkpoint-archive-dual-fault-simple-net",
    checkpoint_timeout_fault="35s",
    max_wal_size_fault="32MB",
    checkpoint_completion_target_fault="0.2",
    checkpoint_timeout_target="5min",
    max_wal_size_target="256MB",
    checkpoint_completion_target_target="0.9",
    archive_delay_fault_seconds=2.5,
    # Fire the archive-side squeeze inside the target capture: the writer
    # overpressure leads the window, the archive deficit trails it, so the
    # frozen history carries the ordered two-chain evidence.
    archive_fault_start_delay_seconds=90.0,
    replay_seconds=18,
    wal_space_budget_bytes=192 * 1024 * 1024,
    max_checkpoint_req_delta=10,
    max_checkpoint_write_ms=3500.0,
    min_tps=0.5,
    max_p99_ms=2500.0,
    base_backup_noise=True,
    # Keep the target writer above the repaired checkpoint/WAL budget when it
    # remains ungoverned. This is the published workload baseline, not an
    # evaluator-only failure threshold.
    backfill_batch_rows_fault=800,
    backfill_pause_ms_fault=250,
    backfill_batch_rows_target=1,
    backfill_pause_ms_target=5000,
    maintenance_job_name="warehouse_maintenance_simple",
    maintenance_table="warehouse_maintenance_events_simple",
    maintenance_batch_rows=40,
    maintenance_pause_ms=1000,
    backfill_payload_repeat=4096,
    maintenance_payload_repeat=256,
    archive_policy_name="archive_transfer_policy_simple",
    archive_segments_per_minute_fault=24,
    archive_pause_ms_fault=2500,
    archive_segments_per_minute_target=120,
    archive_pause_ms_target=0,
    archive_guard_name="archive_transfer_limit_simple",
    archive_guard_enabled_fault=True,
    archive_guard_segments_per_minute_fault=24,
    archive_guard_pause_ms_fault=2500,
    # Enabling the bounded guard at its safe transfer budget is a valid
    # governance repair; the boolean itself must not become a repair trap.
    archive_guard_enabled_target=True,
    archive_repository_name="archive_storage_pool_simple",
    archive_neighbor_target_name="archive_endpoint_neighbor_simple",
    archive_neighbor_repository_name="archive_storage_pool_neighbor_simple",
    archive_repository_reserved_mb=496,
    archive_repository_quota_mb_fault=512,
    archive_repository_quota_mb_target=752,
    archive_repository_safe_spare_mb=256,
    archive_binding_fault_repository_name="archive_endpoint_unbound",
    archive_binding_fault_target_path=f"{ARCHIVE_TARGET_CONTAINER_PATH}/archive_endpoint_unbound",
    archive_binding_fault=False,
    archive_route_fault=True,
    # The Simple Case hides the safe repair profile from current state: the
    # healthy batch cadence is only observable in the frozen history, and the
    # unrelated healthy job's profile must survive the repair.
    publish_safe_profiles=False,
    run_healthy_workload_in_normal_capture=True,
    protect_unrelated_job_profile=True,
)


_SIMPLE_CASE = replace(_SIMPLE_CASE, reference_report=_reference_report(_SIMPLE_CASE))


class PgSystemFailureCheckpointArchiveInjector(BaseFaultInjector):
    """Owns all runtime state for one real dual-fault run."""

    def __init__(self):
        self.env = None
        self.config = {}
        self.case = None
        self._stop_event = None
        self._backfill_stop_event = None
        self._maintenance_stop_event = None
        self._noise_stop_event = None
        self._threads = []
        self._backfill_thread = None
        self._maintenance_thread = None
        self._noise_threads = []
        self._processes = []
        self._noise_processes = []
        self._connections = []
        self._archive_fault_thread = None
        self._archive_fault_stop_event = None
        self._archive_fault_transition_error = None
        self._archive_service = None
        self._target_root = None
        self._external_services = True
        self._replay_artifact = None
        self._restore_error = None
        self._recovered = False

    def _apply_config(self, context: FaultLifecycleContext) -> None:
        self.env = context.env
        self.case = context.case
        self.config = dict(context.config)
        self._external_services = bool(self.config.get("run_external_services", True))
        self._target_root = Path(getattr(self.env.deployment, "archive_target_root", self.case.archive_target_root))
        self._validate_config()

    def _validate_config(self) -> None:
        _validate_sql_identifier(self.case.write_table, "write_table")
        _validate_sql_identifier(self.case.write_job_name, "write_job_name")
        _validate_sql_identifier(self.case.maintenance_table, "maintenance_table")
        _validate_sql_identifier(self.case.maintenance_job_name, "maintenance_job_name")
        _validate_sql_identifier(self.case.archive_target_name, "archive_target_name")
        _validate_sql_identifier(
            self.case.archive_binding_fault_repository_name,
            "archive_binding_fault_repository_name",
        )
        _validate_sql_identifier(BACKFILL_CONFIG_TABLE, "backfill_config_table")
        if self.case.archive_delay_fault_seconds <= 0 or self.case.replay_seconds <= 0:
            raise ValueError("archive delay and replay duration must be positive")
        if self.case.archive_fault_start_delay_seconds < 0:
            raise ValueError("archive fault start delay must not be negative")

    def _record_operation_event(self, **kwargs) -> None:
        provider = getattr(self.env, "_scenario_metric_provider", None)
        recorder = getattr(provider, "record_operation_event", None)
        if callable(recorder):
            recorder(**kwargs)

    def _set_settings(self, *, fault: bool) -> None:
        values = (
            ("checkpoint_timeout", self.case.checkpoint_timeout_fault if fault else self.case.checkpoint_timeout_target),
            ("max_wal_size", self.case.max_wal_size_fault if fault else self.case.max_wal_size_target),
            ("checkpoint_completion_target", self.case.checkpoint_completion_target_fault if fault else self.case.checkpoint_completion_target_target),
            (
                "archive_command",
                _policy_archive_command(self.case.archive_target_name),
            ),
        )
        with self.env.metrics_hidden():
            for name, value in values:
                _require_sql_success(
                    _execute_sql_for_injector(
                        self.env,
                        f"ALTER SYSTEM SET {name} = {_sql_literal(value)};",
                    ),
                    f"set checkpoint/archive setting {name}",
                )
            _require_sql_success(
                _execute_sql_for_injector(self.env, "SELECT pg_reload_conf();"),
                "reload checkpoint/archive settings",
            )

    def _binding_values(self, *, fault: bool) -> tuple[str, str]:
        if fault and self.case.archive_binding_fault:
            return (
                self.case.archive_binding_fault_repository_name,
                self.case.archive_binding_fault_target_path,
            )
        return (
            self.case.archive_repository_name,
            _archive_target_container_subpath(self.case.archive_target_name),
        )

    def _ensure_tables(self, *, binding_fault: bool = False) -> None:
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE IF NOT EXISTS {self.case.write_table} ("
                "id bigserial PRIMARY KEY, payload text NOT NULL, created_at timestamptz NOT NULL DEFAULT clock_timestamp());"
            ),
            f"create {self.case.write_table}",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE IF NOT EXISTS {self.case.write_table}_markers ("
                "marker_id text PRIMARY KEY, created_at timestamptz NOT NULL DEFAULT clock_timestamp());"
            ),
            f"create {self.case.write_table}_markers",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE IF NOT EXISTS {self.case.maintenance_table} ("
                "id bigserial PRIMARY KEY, payload text NOT NULL, created_at timestamptz NOT NULL DEFAULT clock_timestamp());"
            ),
            f"create {self.case.maintenance_table}",
        )
        for table_name, label in (
            (OLTP_TABLE, "create OLTP workload table"),
            (NORMAL_WAL_TABLE, "create normal WAL workload table"),
        ):
            _require_sql_success(
                self.env.execute_sql(
                    f"CREATE TABLE IF NOT EXISTS {table_name} ("
                    "event_id bigserial PRIMARY KEY, payload text NOT NULL, "
                    "created_at timestamptz NOT NULL DEFAULT clock_timestamp());"
                ),
                label,
            )
        publish_safe = bool(self.case.publish_safe_profiles)
        backfill_safe_columns = (
            ", safe_batch_rows integer NOT NULL CHECK (safe_batch_rows BETWEEN 1 AND 800), "
            "safe_pause_ms integer NOT NULL CHECK (safe_pause_ms BETWEEN 10 AND 5000)"
            if publish_safe
            else ""
        )
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE IF NOT EXISTS {BACKFILL_CONFIG_TABLE} ("
                "job_name text PRIMARY KEY CHECK (job_name <> ''), "
                "batch_rows integer NOT NULL CHECK (batch_rows BETWEEN 1 AND 800), "
                "pause_ms integer NOT NULL CHECK (pause_ms BETWEEN 10 AND 5000)"
                f"{backfill_safe_columns});"
            ),
            f"create {BACKFILL_CONFIG_TABLE}",
        )
        if publish_safe:
            _require_sql_success(
                self.env.execute_sql(
                    f"ALTER TABLE {BACKFILL_CONFIG_TABLE} ADD COLUMN IF NOT EXISTS safe_batch_rows integer; "
                    f"ALTER TABLE {BACKFILL_CONFIG_TABLE} ADD COLUMN IF NOT EXISTS safe_pause_ms integer; "
                    f"INSERT INTO {BACKFILL_CONFIG_TABLE} (job_name, batch_rows, pause_ms, safe_batch_rows, safe_pause_ms) VALUES "
                    f"({_sql_literal(self.case.write_job_name)}, {self.case.backfill_batch_rows_fault}, {self.case.backfill_pause_ms_fault}, {self.case.backfill_batch_rows_target}, {self.case.backfill_pause_ms_target}), "
                    f"({_sql_literal(self.case.maintenance_job_name)}, {self.case.maintenance_batch_rows}, {self.case.maintenance_pause_ms}, {self.case.maintenance_batch_rows}, {self.case.maintenance_pause_ms}) "
                    "ON CONFLICT (job_name) DO UPDATE SET batch_rows = EXCLUDED.batch_rows, pause_ms = EXCLUDED.pause_ms, "
                    "safe_batch_rows = EXCLUDED.safe_batch_rows, safe_pause_ms = EXCLUDED.safe_pause_ms;"
                ),
                f"initialize {BACKFILL_CONFIG_TABLE}",
            )
        else:
            _require_sql_success(
                self.env.execute_sql(
                    f"INSERT INTO {BACKFILL_CONFIG_TABLE} (job_name, batch_rows, pause_ms) VALUES "
                    f"({_sql_literal(self.case.write_job_name)}, {self.case.backfill_batch_rows_fault}, {self.case.backfill_pause_ms_fault}), "
                    f"({_sql_literal(self.case.maintenance_job_name)}, {self.case.maintenance_batch_rows}, {self.case.maintenance_pause_ms}) "
                    "ON CONFLICT (job_name) DO UPDATE SET batch_rows = EXCLUDED.batch_rows, pause_ms = EXCLUDED.pause_ms;"
                ),
                f"initialize {BACKFILL_CONFIG_TABLE}",
            )
        policy_safe_columns = (
            ", safe_max_segments_per_minute integer NOT NULL CHECK (safe_max_segments_per_minute BETWEEN 1 AND 120), "
            "safe_pause_ms integer NOT NULL CHECK (safe_pause_ms BETWEEN 0 AND 5000)"
            if publish_safe
            else ""
        )
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE IF NOT EXISTS {ARCHIVE_POLICY_TABLE} ("
                "policy_name text PRIMARY KEY CHECK (policy_name <> ''), "
                "max_segments_per_minute integer NOT NULL CHECK (max_segments_per_minute BETWEEN 1 AND 120), "
                "pause_ms integer NOT NULL CHECK (pause_ms BETWEEN 0 AND 5000)"
                f"{policy_safe_columns});"
            ),
            f"create {ARCHIVE_POLICY_TABLE}",
        )
        if publish_safe:
            _require_sql_success(
                self.env.execute_sql(
                    f"INSERT INTO {ARCHIVE_POLICY_TABLE} "
                    "(policy_name, max_segments_per_minute, pause_ms, safe_max_segments_per_minute, safe_pause_ms) VALUES "
                    f"({_sql_literal(self.case.archive_policy_name)}, {self.case.archive_segments_per_minute_fault}, "
                    f"{self.case.archive_pause_ms_fault}, {self.case.archive_segments_per_minute_target}, "
                    f"{self.case.archive_pause_ms_target}) "
                    "ON CONFLICT (policy_name) DO UPDATE SET max_segments_per_minute = EXCLUDED.max_segments_per_minute, "
                    "pause_ms = EXCLUDED.pause_ms, safe_max_segments_per_minute = EXCLUDED.safe_max_segments_per_minute, "
                    "safe_pause_ms = EXCLUDED.safe_pause_ms;"
                ),
                f"initialize {ARCHIVE_POLICY_TABLE}",
            )
        else:
            _require_sql_success(
                self.env.execute_sql(
                    f"INSERT INTO {ARCHIVE_POLICY_TABLE} "
                    "(policy_name, max_segments_per_minute, pause_ms) VALUES "
                    f"({_sql_literal(self.case.archive_policy_name)}, {self.case.archive_segments_per_minute_fault}, "
                    f"{self.case.archive_pause_ms_fault}) "
                    "ON CONFLICT (policy_name) DO UPDATE SET max_segments_per_minute = EXCLUDED.max_segments_per_minute, "
                    "pause_ms = EXCLUDED.pause_ms;"
                ),
                f"initialize {ARCHIVE_POLICY_TABLE}",
            )
        guard_safe_columns = (
            ", safe_enabled boolean NOT NULL, "
            "safe_max_segments_per_minute integer NOT NULL CHECK (safe_max_segments_per_minute BETWEEN 1 AND 120), "
            "safe_pause_ms integer NOT NULL CHECK (safe_pause_ms BETWEEN 0 AND 5000)"
            if publish_safe
            else ""
        )
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE IF NOT EXISTS {ARCHIVE_GUARD_TABLE} ("
                "guard_name text PRIMARY KEY CHECK (guard_name <> ''), "
                "enabled boolean NOT NULL, "
                "max_segments_per_minute integer NOT NULL CHECK (max_segments_per_minute BETWEEN 1 AND 120), "
                "pause_ms integer NOT NULL CHECK (pause_ms BETWEEN 0 AND 5000)"
                f"{guard_safe_columns});"
            ),
            f"create {ARCHIVE_GUARD_TABLE}",
        )
        if publish_safe:
            _require_sql_success(
                self.env.execute_sql(
                    f"INSERT INTO {ARCHIVE_GUARD_TABLE} "
                    "(guard_name, enabled, max_segments_per_minute, pause_ms, safe_enabled, "
                    "safe_max_segments_per_minute, safe_pause_ms) VALUES "
                    f"({_sql_literal(self.case.archive_guard_name)}, "
                    f"{'true' if self.case.archive_guard_enabled_fault else 'false'}, "
                    f"{self.case.archive_guard_segments_per_minute_fault}, {self.case.archive_guard_pause_ms_fault}, "
                    f"{'true' if self.case.archive_guard_enabled_target else 'false'}, "
                    f"{self.case.archive_segments_per_minute_target}, {self.case.archive_pause_ms_target}) "
                    "ON CONFLICT (guard_name) DO UPDATE SET enabled = EXCLUDED.enabled, "
                    "max_segments_per_minute = EXCLUDED.max_segments_per_minute, pause_ms = EXCLUDED.pause_ms, "
                    "safe_enabled = EXCLUDED.safe_enabled, safe_max_segments_per_minute = EXCLUDED.safe_max_segments_per_minute, "
                    "safe_pause_ms = EXCLUDED.safe_pause_ms;"
                ),
                f"initialize {ARCHIVE_GUARD_TABLE}",
            )
        else:
            _require_sql_success(
                self.env.execute_sql(
                    f"INSERT INTO {ARCHIVE_GUARD_TABLE} "
                    "(guard_name, enabled, max_segments_per_minute, pause_ms) VALUES "
                    f"({_sql_literal(self.case.archive_guard_name)}, "
                    f"{'true' if self.case.archive_guard_enabled_fault else 'false'}, "
                    f"{self.case.archive_guard_segments_per_minute_fault}, {self.case.archive_guard_pause_ms_fault}) "
                    "ON CONFLICT (guard_name) DO UPDATE SET enabled = EXCLUDED.enabled, "
                    "max_segments_per_minute = EXCLUDED.max_segments_per_minute, pause_ms = EXCLUDED.pause_ms;"
                ),
                f"initialize {ARCHIVE_GUARD_TABLE}",
            )
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE IF NOT EXISTS {ARCHIVE_TARGET_REGISTRY_TABLE} ("
                "target_name text PRIMARY KEY CHECK (target_name <> ''), "
                "repository_name text NOT NULL CHECK (repository_name <> ''), "
                "target_path text NOT NULL CHECK (target_path <> ''), "
                "enabled boolean NOT NULL, "
                "role text NOT NULL CHECK (role IN ('active', 'neighbor')), "
                "binding_generation bigint NOT NULL CHECK (binding_generation > 0));"
            ),
            f"create {ARCHIVE_TARGET_REGISTRY_TABLE}",
        )
        if self.case.archive_binding_fault:
            active_repository_name = self.case.archive_neighbor_repository_name
            # The active row is public and inspectable, but points at a
            # directory that is not published by the deployment. A repair may
            # restore the target path or migrate to the healthy neighbor.
            active_target_path = _archive_target_container_subpath("archive_endpoint_unbound")
            neighbor_repository_name = self.case.archive_repository_name
            neighbor_target_path = _archive_target_container_subpath(self.case.archive_target_name)
        else:
            active_repository_name = self.case.archive_repository_name
            active_target_path = _archive_target_container_subpath(self.case.archive_target_name)
            neighbor_repository_name = self.case.archive_neighbor_repository_name
            neighbor_target_path = _archive_target_container_subpath(ARCHIVE_SHADOW_DIRECTORY)
        _require_sql_success(
            self.env.execute_sql(
                f"ALTER TABLE {ARCHIVE_TARGET_REGISTRY_TABLE} "
                "DROP COLUMN IF EXISTS lease_expires_at; "
                f"ALTER TABLE {ARCHIVE_TARGET_REGISTRY_TABLE} "
                "ADD COLUMN IF NOT EXISTS binding_generation bigint NOT NULL DEFAULT 1;"
            ),
            f"remove legacy inline lease from {ARCHIVE_TARGET_REGISTRY_TABLE}",
        )
        active_repository_name, active_target_path = self._binding_values(fault=binding_fault)
        registry_generation, state_generation, route_generation = _archive_binding_generations(
            binding_fault=binding_fault and self.case.archive_binding_fault,
            route_fault=binding_fault and self.case.archive_route_fault,
        )
        route_worker_epoch, neighbor_route_worker_epoch = _archive_route_worker_epochs(
            route_fault=binding_fault and self.case.archive_route_fault,
        )
        _require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {ARCHIVE_TARGET_REGISTRY_TABLE} "
                "(target_name, repository_name, target_path, enabled, role, binding_generation) VALUES "
                f"({_sql_literal(self.case.archive_target_name)}, {_sql_literal(active_repository_name)}, "
                f"{_sql_literal(active_target_path)}, true, 'active', {registry_generation}), "
                f"({_sql_literal(self.case.archive_neighbor_target_name)}, {_sql_literal(self.case.archive_neighbor_repository_name)}, "
                f"{_sql_literal(f'{ARCHIVE_TARGET_CONTAINER_PATH}/{ARCHIVE_SHADOW_DIRECTORY}')}, true, 'neighbor', 17) "
                "ON CONFLICT (target_name) DO UPDATE SET repository_name = EXCLUDED.repository_name, "
                "target_path = EXCLUDED.target_path, enabled = EXCLUDED.enabled, role = EXCLUDED.role, "
                "binding_generation = EXCLUDED.binding_generation;"
            ),
            f"initialize {ARCHIVE_TARGET_REGISTRY_TABLE}",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE IF NOT EXISTS {ARCHIVE_BINDING_STATE_TABLE} ("
                "target_name text PRIMARY KEY CHECK (target_name <> ''), "
                "lease_expires_at timestamptz NOT NULL, "
                "binding_generation bigint NOT NULL CHECK (binding_generation > 0));"
            ),
            f"create {ARCHIVE_BINDING_STATE_TABLE}",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"ALTER TABLE {ARCHIVE_BINDING_STATE_TABLE} "
                "ADD COLUMN IF NOT EXISTS binding_generation bigint NOT NULL DEFAULT 1; "
                f"INSERT INTO {ARCHIVE_BINDING_STATE_TABLE} (target_name, lease_expires_at, binding_generation) VALUES "
                f"({_sql_literal(self.case.archive_target_name)}, "
                f"{_archive_binding_lease_sql(expired=binding_fault and self.case.archive_binding_fault)}, {state_generation}), "
                f"({_sql_literal(self.case.archive_neighbor_target_name)}, {_archive_binding_lease_sql(expired=False)}, 17) "
                "ON CONFLICT (target_name) DO UPDATE SET lease_expires_at = EXCLUDED.lease_expires_at, "
                "binding_generation = EXCLUDED.binding_generation;"
            ),
            f"initialize {ARCHIVE_BINDING_STATE_TABLE}",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE IF NOT EXISTS {ARCHIVE_ROUTE_STATE_TABLE} ("
                "target_name text PRIMARY KEY CHECK (target_name <> ''), "
                "route_name text NOT NULL CHECK (route_name <> ''), "
                "target_path text NOT NULL CHECK (target_path <> ''), "
                "enabled boolean NOT NULL, "
                "binding_generation bigint NOT NULL CHECK (binding_generation > 0), "
                "worker_activation_epoch bigint NOT NULL CHECK (worker_activation_epoch > 0));"
            ),
            f"create {ARCHIVE_ROUTE_STATE_TABLE}",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"ALTER TABLE {ARCHIVE_ROUTE_STATE_TABLE} "
                "ADD COLUMN IF NOT EXISTS worker_activation_epoch bigint NOT NULL DEFAULT 1;"
            ),
            f"add {ARCHIVE_ROUTE_STATE_TABLE} worker activation state",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {ARCHIVE_ROUTE_STATE_TABLE} "
                "(target_name, route_name, target_path, enabled, binding_generation, worker_activation_epoch) VALUES "
                f"({_sql_literal(self.case.archive_target_name)}, "
                f"{_sql_literal(self.case.archive_target_name + '_route')}, "
                f"{_sql_literal(active_target_path)}, true, {route_generation}, {route_worker_epoch}), "
                f"({_sql_literal(self.case.archive_neighbor_target_name)}, "
                f"{_sql_literal(self.case.archive_neighbor_target_name + '_route')}, "
                f"{_sql_literal(f'{ARCHIVE_TARGET_CONTAINER_PATH}/{ARCHIVE_SHADOW_DIRECTORY}')}, true, 17, {neighbor_route_worker_epoch}) "
                "ON CONFLICT (target_name) DO UPDATE SET route_name = EXCLUDED.route_name, "
                "target_path = EXCLUDED.target_path, enabled = EXCLUDED.enabled, "
                "binding_generation = EXCLUDED.binding_generation, "
                "worker_activation_epoch = EXCLUDED.worker_activation_epoch;"
            ),
            f"initialize {ARCHIVE_ROUTE_STATE_TABLE}",
        )
        _require_sql_success(
            # This table is task-owned. Recreate it so a snapshot made before
            # the quota schema change cannot leave legacy columns in place.
            self.env.execute_sql(f"DROP TABLE IF EXISTS {ARCHIVE_REPOSITORY_TABLE};"),
            f"reset {ARCHIVE_REPOSITORY_TABLE} schema",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE IF NOT EXISTS {ARCHIVE_REPOSITORY_TABLE} ("
                "repository_name text PRIMARY KEY CHECK (repository_name <> ''), "
                "quota_mb integer NOT NULL CHECK (quota_mb BETWEEN 1 AND 1048576), "
                "reserved_mb integer NOT NULL CHECK (reserved_mb BETWEEN 0 AND 1048576), "
                "safe_spare_mb integer NOT NULL CHECK (safe_spare_mb BETWEEN 1 AND 1048576), "
                "CHECK (quota_mb >= reserved_mb));"
            ),
            f"create {ARCHIVE_REPOSITORY_TABLE}",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {ARCHIVE_REPOSITORY_TABLE} "
                "(repository_name, quota_mb, reserved_mb, safe_spare_mb) VALUES "
                f"({_sql_literal(self.case.archive_repository_name)}, {self.case.archive_repository_quota_mb_fault}, "
                f"{self.case.archive_repository_reserved_mb}, {self.case.archive_repository_safe_spare_mb}), "
                f"({_sql_literal(self.case.archive_neighbor_repository_name)}, {self.case.archive_repository_quota_mb_target}, "
                f"{self.case.archive_repository_reserved_mb}, {self.case.archive_repository_safe_spare_mb}) "
                "ON CONFLICT (repository_name) DO UPDATE SET quota_mb = EXCLUDED.quota_mb, "
                "reserved_mb = EXCLUDED.reserved_mb, safe_spare_mb = EXCLUDED.safe_spare_mb;"
            ),
            f"initialize {ARCHIVE_REPOSITORY_TABLE}",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE OR REPLACE FUNCTION {ARCHIVE_AVAILABLE_FUNCTION}(p_repository_name text) "
                "RETURNS integer LANGUAGE sql STABLE AS $$ "
                f"SELECT quota_mb - reserved_mb FROM {ARCHIVE_REPOSITORY_TABLE} "
                "WHERE repository_name = p_repository_name $$;"
            ),
            f"publish {ARCHIVE_AVAILABLE_FUNCTION}",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE OR REPLACE FUNCTION {ARCHIVE_SAFE_SPARE_FUNCTION}(p_repository_name text) "
                "RETURNS integer LANGUAGE sql STABLE AS $$ "
                f"SELECT safe_spare_mb FROM {ARCHIVE_REPOSITORY_TABLE} "
                "WHERE repository_name = p_repository_name $$;"
            ),
            f"publish {ARCHIVE_SAFE_SPARE_FUNCTION}",
        )

        # Fill the published safe profile for a table created by an older
        # snapshot. OP checks this business control state, not a fixed query.
        if publish_safe:
            _require_sql_success(
                self.env.execute_sql(
                    f"UPDATE {BACKFILL_CONFIG_TABLE} SET safe_batch_rows = CASE WHEN job_name = {_sql_literal(self.case.write_job_name)} THEN {self.case.backfill_batch_rows_target} ELSE {self.case.maintenance_batch_rows} END, "
                    f"safe_pause_ms = CASE WHEN job_name = {_sql_literal(self.case.write_job_name)} THEN {self.case.backfill_pause_ms_target} ELSE {self.case.maintenance_pause_ms} END "
                    "WHERE safe_batch_rows IS NULL OR safe_pause_ms IS NULL;"
                ),
                f"publish {BACKFILL_CONFIG_TABLE} safe profile",
            )

    def _set_backfill_profile(self, *, fault: bool) -> None:
        batch_rows = self.case.backfill_batch_rows_fault if fault else self.case.backfill_batch_rows_target
        pause_ms = self.case.backfill_pause_ms_fault if fault else self.case.backfill_pause_ms_target
        _require_sql_success(
            self.env.execute_sql(
                f"UPDATE {BACKFILL_CONFIG_TABLE} SET batch_rows = {batch_rows}, pause_ms = {pause_ms} "
                f"WHERE job_name = {_sql_literal(self.case.write_job_name)};"
            ),
            f"set {BACKFILL_CONFIG_TABLE} profile",
        )

    def _set_archive_policy(self, *, fault: bool) -> None:
        segments_per_minute = (
            self.case.archive_segments_per_minute_fault
            if fault else self.case.archive_segments_per_minute_target
        )
        pause_ms = self.case.archive_pause_ms_fault if fault else self.case.archive_pause_ms_target
        _require_sql_success(
            self.env.execute_sql(
                f"UPDATE {ARCHIVE_POLICY_TABLE} SET max_segments_per_minute = {segments_per_minute}, "
                f"pause_ms = {pause_ms} WHERE policy_name = {_sql_literal(self.case.archive_policy_name)};"
            ),
            f"set {ARCHIVE_POLICY_TABLE} policy",
        )

    def _set_archive_guard(self, *, fault: bool) -> None:
        enabled = self.case.archive_guard_enabled_fault if fault else self.case.archive_guard_enabled_target
        max_segments = (
            self.case.archive_guard_segments_per_minute_fault
            if fault else self.case.archive_segments_per_minute_target
        )
        pause_ms = self.case.archive_guard_pause_ms_fault if fault else self.case.archive_pause_ms_target
        _require_sql_success(
            self.env.execute_sql(
                f"UPDATE {ARCHIVE_GUARD_TABLE} SET enabled = {'true' if enabled else 'false'}, "
                f"max_segments_per_minute = {max_segments}, pause_ms = {pause_ms} "
                f"WHERE guard_name = {_sql_literal(self.case.archive_guard_name)};"
            ),
            f"set {ARCHIVE_GUARD_TABLE} guard",
        )

    def _set_archive_repository(self, *, fault: bool) -> None:
        quota_mb = self.case.archive_repository_quota_mb_fault if fault else self.case.archive_repository_quota_mb_target
        _require_sql_success(
            self.env.execute_sql(
                f"UPDATE {ARCHIVE_REPOSITORY_TABLE} SET quota_mb = {quota_mb}, "
                f"reserved_mb = {self.case.archive_repository_reserved_mb} "
                f"WHERE repository_name = {_sql_literal(self.case.archive_repository_name)};"
            ),
            f"set {ARCHIVE_REPOSITORY_TABLE} active repository",
        )

    def _set_archive_binding(self, *, fault: bool) -> None:
        repository_name, target_path = self._binding_values(fault=fault)
        binding_fault = fault and self.case.archive_binding_fault
        route_fault = fault and self.case.archive_route_fault
        expired = binding_fault
        registry_generation, state_generation, route_generation = _archive_binding_generations(
            binding_fault=binding_fault,
            route_fault=route_fault,
        )
        _require_sql_success(
            self.env.execute_sql(
                f"UPDATE {ARCHIVE_TARGET_REGISTRY_TABLE} SET role = 'neighbor' "
                f"WHERE target_name = {_sql_literal(self.case.archive_neighbor_target_name)};"
            ),
            f"demote {ARCHIVE_TARGET_REGISTRY_TABLE} neighbor before active binding",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"UPDATE {ARCHIVE_TARGET_REGISTRY_TABLE} SET repository_name = {_sql_literal(repository_name)}, "
                f"target_path = {_sql_literal(target_path)}, enabled = true, role = 'active' "
                f", binding_generation = {registry_generation} "
                f"WHERE target_name = {_sql_literal(self.case.archive_target_name)};"
            ),
            f"set {ARCHIVE_TARGET_REGISTRY_TABLE} active binding",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"UPDATE {ARCHIVE_BINDING_STATE_TABLE} SET lease_expires_at = "
                f"{_archive_binding_lease_sql(expired=expired)}, binding_generation = {state_generation} "
                f"WHERE target_name = {_sql_literal(self.case.archive_target_name)};"
            ),
                f"set {ARCHIVE_BINDING_STATE_TABLE} active lease",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"UPDATE {ARCHIVE_ROUTE_STATE_TABLE} SET route_name = {_sql_literal(self.case.archive_target_name + '_route')}, "
                f"target_path = {_sql_literal(target_path)}, enabled = true, binding_generation = {route_generation}, "
                f"worker_activation_epoch = {route_generation} "
                f"WHERE target_name = {_sql_literal(self.case.archive_target_name)};"
            ),
            f"set {ARCHIVE_ROUTE_STATE_TABLE} active route",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"UPDATE {ARCHIVE_BINDING_STATE_TABLE} SET lease_expires_at = {_archive_binding_lease_sql(expired=False)}, "
                "binding_generation = 17 "
                f"WHERE target_name = {_sql_literal(self.case.archive_neighbor_target_name)}; "
                f"UPDATE {ARCHIVE_ROUTE_STATE_TABLE} SET route_name = {_sql_literal(self.case.archive_neighbor_target_name + '_route')}, "
                f"target_path = {_sql_literal(f'{ARCHIVE_TARGET_CONTAINER_PATH}/{ARCHIVE_SHADOW_DIRECTORY}')}, enabled = true, "
                "binding_generation = 17, worker_activation_epoch = 17 "
                f"WHERE target_name = {_sql_literal(self.case.archive_neighbor_target_name)};"
            ),
            f"restore {ARCHIVE_BINDING_STATE_TABLE} neighbor state",
        )

    def _apply_delayed_archive_fault(self, connection) -> None:
        """Apply the archive-side fault on its own connection at the fixed phase boundary."""
        segments_per_minute = self.case.archive_segments_per_minute_fault
        pause_ms = self.case.archive_pause_ms_fault
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {ARCHIVE_POLICY_TABLE} SET max_segments_per_minute = %s, pause_ms = %s "
                f"WHERE policy_name = %s",
                (segments_per_minute, pause_ms, self.case.archive_policy_name),
            )
            cursor.execute(
                f"UPDATE {ARCHIVE_GUARD_TABLE} SET enabled = true, max_segments_per_minute = %s, pause_ms = %s "
                f"WHERE guard_name = %s",
                (
                    self.case.archive_guard_segments_per_minute_fault,
                    self.case.archive_guard_pause_ms_fault,
                    self.case.archive_guard_name,
                ),
            )
            cursor.execute(
                f"UPDATE {ARCHIVE_REPOSITORY_TABLE} SET quota_mb = %s, reserved_mb = %s "
                f"WHERE repository_name = %s",
                (
                    self.case.archive_repository_quota_mb_fault,
                    self.case.archive_repository_reserved_mb,
                    self.case.archive_repository_name,
                ),
            )
            if self.case.archive_binding_fault:
                binding_repository, binding_path = self._binding_values(fault=True)
                cursor.execute(
                    f"UPDATE {ARCHIVE_TARGET_REGISTRY_TABLE} SET repository_name = %s, target_path = %s, "
                    "enabled = true, role = 'active', binding_generation = 17 "
                    "WHERE target_name = %s",
                    (binding_repository, binding_path, self.case.archive_target_name),
                )
                cursor.execute(
                    f"UPDATE {ARCHIVE_BINDING_STATE_TABLE} SET lease_expires_at = clock_timestamp() - interval '1 hour' "
                    ", binding_generation = 16 "
                    "WHERE target_name = %s",
                    (self.case.archive_target_name,),
                )
            if self.case.archive_route_fault:
                cursor.execute(
                    f"UPDATE {ARCHIVE_ROUTE_STATE_TABLE} SET route_name = %s, target_path = %s, "
                    "enabled = true, binding_generation = 16, worker_activation_epoch = 16 WHERE target_name = %s",
                    (
                        self.case.archive_target_name + "_route",
                        _archive_target_container_subpath(self.case.archive_target_name),
                        self.case.archive_target_name,
                    ),
                )

    def _archive_fault_transition_loop(self) -> None:
        stop_event = self._archive_fault_stop_event
        if stop_event is None or stop_event.wait(self.case.archive_fault_start_delay_seconds):
            return
        try:
            connection = self._connect("archive_fault_transition")
            self._apply_delayed_archive_fault(connection)
        except Exception as exc:
            self._archive_fault_transition_error = str(exc)
            if self._stop_event is not None and not self._stop_event.is_set():
                print(f"[FaultInjector:{type(self).__name__}] archive transition stopped: {exc}")

    def _raise_archive_fault_transition_error(self) -> None:
        error = self._archive_fault_transition_error
        if error:
            raise RuntimeError(
                "archive fault transition failed; the dual-fault capture is invalid: "
                f"error={error}"
            )

    def _archive_policy_state(self) -> dict:
        if not self.case.publish_safe_profiles:
            rows = _sql_rows(
                self.env,
                f"SELECT max_segments_per_minute, pause_ms "
                f"FROM {ARCHIVE_POLICY_TABLE} WHERE policy_name = {_sql_literal(self.case.archive_policy_name)};",
            )
            if len(rows) != 1 or len(rows[0]) != 2:
                raise RuntimeError(f"unexpected archive policy state: {rows!r}")
            max_segments, pause_ms = (int(value) for value in rows[0])
            return {
                "policy_name": self.case.archive_policy_name,
                "max_segments_per_minute": max_segments,
                "pause_ms": pause_ms,
                "safe_profile_pass": (
                    max_segments >= int(self.case.archive_segments_per_minute_target)
                    and pause_ms <= int(self.case.archive_pause_ms_target)
                ),
            }
        rows = _sql_rows(
            self.env,
            f"SELECT max_segments_per_minute, pause_ms, safe_max_segments_per_minute, safe_pause_ms "
            f"FROM {ARCHIVE_POLICY_TABLE} WHERE policy_name = {_sql_literal(self.case.archive_policy_name)};",
        )
        if len(rows) != 1 or len(rows[0]) != 4:
            raise RuntimeError(f"unexpected archive policy state: {rows!r}")
        max_segments, pause_ms, safe_max_segments, safe_pause_ms = (int(value) for value in rows[0])
        return {
            "policy_name": self.case.archive_policy_name,
            "max_segments_per_minute": max_segments,
            "pause_ms": pause_ms,
            "safe_max_segments_per_minute": safe_max_segments,
            "safe_pause_ms": safe_pause_ms,
            "published_profile_unchanged": (
                safe_max_segments == int(self.case.archive_segments_per_minute_target)
                and safe_pause_ms == int(self.case.archive_pause_ms_target)
            ),
            "safe_profile_pass": (
                safe_max_segments == int(self.case.archive_segments_per_minute_target)
                and safe_pause_ms == int(self.case.archive_pause_ms_target)
                and max_segments >= safe_max_segments
                and pause_ms <= safe_pause_ms
            ),
        }

    def _archive_guard_state(self) -> dict:
        if not self.case.publish_safe_profiles:
            rows = _sql_rows(
                self.env,
                f"SELECT enabled, max_segments_per_minute, pause_ms "
                f"FROM {ARCHIVE_GUARD_TABLE} "
                f"WHERE guard_name = {_sql_literal(self.case.archive_guard_name)};",
            )
            if len(rows) != 1 or len(rows[0]) != 3:
                raise RuntimeError(f"unexpected archive guard state: {rows!r}")
            enabled, max_segments, pause_ms = rows[0]
            return {
                "guard_name": self.case.archive_guard_name,
                "enabled": bool(enabled),
                "max_segments_per_minute": int(max_segments),
                "pause_ms": int(pause_ms),
                "safe_profile_pass": (
                    int(max_segments) >= int(self.case.archive_segments_per_minute_target)
                    and int(pause_ms) <= int(self.case.archive_pause_ms_target)
                ),
            }
        rows = _sql_rows(
            self.env,
            f"SELECT enabled, max_segments_per_minute, pause_ms, safe_enabled, "
            f"safe_max_segments_per_minute, safe_pause_ms "
            f"FROM {ARCHIVE_GUARD_TABLE} "
            f"WHERE guard_name = {_sql_literal(self.case.archive_guard_name)};",
        )
        if len(rows) != 1 or len(rows[0]) != 6:
            raise RuntimeError(f"unexpected archive guard state: {rows!r}")
        enabled, max_segments, pause_ms, safe_enabled, safe_max_segments, safe_pause_ms = rows[0]
        expected_enabled = bool(self.case.archive_guard_enabled_target)
        expected_max_segments = int(self.case.archive_segments_per_minute_target)
        expected_pause_ms = int(self.case.archive_pause_ms_target)
        published_profile_unchanged = (
            bool(safe_enabled) == expected_enabled
            and int(safe_max_segments) == expected_max_segments
            and int(safe_pause_ms) == expected_pause_ms
        )
        return {
            "guard_name": self.case.archive_guard_name,
            "enabled": bool(enabled),
            "max_segments_per_minute": int(max_segments),
            "pause_ms": int(pause_ms),
            "safe_enabled": bool(safe_enabled),
            "safe_max_segments_per_minute": int(safe_max_segments),
            "safe_pause_ms": int(safe_pause_ms),
            "published_profile_unchanged": published_profile_unchanged,
            "safe_profile_pass": (
                published_profile_unchanged
                and int(max_segments) >= expected_max_segments
                and int(pause_ms) <= expected_pause_ms
            ),
        }

    def _archive_repository_state(self) -> dict:
        active_binding = self._active_archive_binding()
        rows = _sql_rows(
            self.env,
            f"SELECT r.repository_name, r.quota_mb, r.reserved_mb, r.safe_spare_mb, "
            f"EXISTS (SELECT 1 FROM {ARCHIVE_TARGET_REGISTRY_TABLE} t "
            f"WHERE t.repository_name = r.repository_name "
            f"AND t.enabled AND t.role = 'active') "
            f"FROM {ARCHIVE_REPOSITORY_TABLE} r "
            f"WHERE r.repository_name IN ({_sql_literal(self.case.archive_repository_name)}, {_sql_literal(self.case.archive_neighbor_repository_name)}) "
            "ORDER BY r.repository_name;",
        )
        active_rows = [row for row in rows if len(row) == 5 and bool(row[4])]
        if len(active_rows) != 1:
            raise RuntimeError(f"exactly one active archive repository is required: {rows!r}")
        active = active_rows[0]
        repository_name, quota_mb, reserved_mb, safe_spare_mb, active_target = active
        available_mb = int(quota_mb) - int(reserved_mb)
        valid_bindings = {
            (
                self.case.archive_target_name,
                self.case.archive_repository_name,
                _archive_target_container_subpath(self.case.archive_target_name),
            ),
            (
                self.case.archive_neighbor_target_name,
                self.case.archive_neighbor_repository_name,
                _archive_target_container_subpath(ARCHIVE_SHADOW_DIRECTORY),
            ),
        }
        active_target_match = (
            active_binding["target_name"],
            active_binding["repository_name"],
            active_binding["target_path"],
        ) in valid_bindings
        return {
            "repository_name": str(repository_name),
            "quota_mb": int(quota_mb),
            "reserved_mb": int(reserved_mb),
            "available_mb": available_mb,
            "safe_spare_mb": int(safe_spare_mb),
            "active_target_match": active_target_match,
            "binding_repository_name": str(repository_name),
            "safe_profile_pass": (
                active_target_match
                and available_mb >= int(self.case.archive_repository_safe_spare_mb)
                and int(safe_spare_mb) == int(self.case.archive_repository_safe_spare_mb)
            ),
            "rows": [list(row) for row in rows],
        }

    def _write_archive_policy_script(self) -> None:
        if self._target_root is None:
            raise RuntimeError("archive target is not initialized")
        script = self._target_root / f".archive_transfer_{self.case.archive_target_name}_policy.sh"
        policy_name = self.case.archive_policy_name.replace("'", "''")
        script.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "source_path=${1:?missing source WAL path}\n"
            "wal_name=${2:?missing WAL name}\n"
            f"policy_row=$(psql -X -At -v ON_ERROR_STOP=1 -U postgres -d testdb -c "
            f"\"SELECT p.max_segments_per_minute, p.pause_ms, g.enabled, g.max_segments_per_minute, g.pause_ms, "
            f"{ARCHIVE_AVAILABLE_FUNCTION}(r.repository_name), "
            f"{ARCHIVE_SAFE_SPARE_FUNCTION}(r.repository_name), route.target_path, "
            "t.binding_generation, l.binding_generation, route.binding_generation, route.worker_activation_epoch, "
            "(l.lease_expires_at > clock_timestamp()) "
            f"FROM public.{ARCHIVE_POLICY_TABLE} p "
            f"CROSS JOIN public.{ARCHIVE_GUARD_TABLE} g "
            f"JOIN public.{ARCHIVE_TARGET_REGISTRY_TABLE} t ON t.enabled AND t.role = 'active' "
            f"JOIN public.{ARCHIVE_BINDING_STATE_TABLE} l ON l.target_name = t.target_name "
            f"JOIN public.{ARCHIVE_ROUTE_STATE_TABLE} route ON route.target_name = t.target_name AND route.enabled "
            f"JOIN public.{ARCHIVE_REPOSITORY_TABLE} r ON r.repository_name = t.repository_name "
            f"WHERE p.policy_name = '{policy_name}' AND g.guard_name = '{self.case.archive_guard_name}'\")\n"
            "IFS='|' read -r policy_max_segments policy_pause_ms guard_enabled guard_max_segments guard_pause_ms repository_available_mb repository_required_spare_mb target_dir registry_generation state_generation route_generation worker_activation_epoch lease_valid <<< \"$policy_row\"\n"
            "max_segments_per_minute=$policy_max_segments\n"
            "pause_ms=$policy_pause_ms\n"
            "if [ \"$guard_enabled\" = \"t\" ]; then\n"
            "  if [ \"$guard_max_segments\" -lt \"$max_segments_per_minute\" ]; then max_segments_per_minute=$guard_max_segments; fi\n"
            "  if [ \"$guard_pause_ms\" -gt \"$pause_ms\" ]; then pause_ms=$guard_pause_ms; fi\n"
            "fi\n"
            "if [ \"$repository_available_mb\" -lt \"$repository_required_spare_mb\" ]; then echo 'transfer deferred by endpoint policy; retry later' >&2; exit 1; fi\n"
            "if [ \"$registry_generation\" != \"$state_generation\" ] || [ \"$registry_generation\" != \"$route_generation\" ] || [ \"$registry_generation\" != \"$worker_activation_epoch\" ]; then echo 'transfer deferred by stale endpoint binding generation; stale endpoint route worker activation; retry later' >&2; exit 1; fi\n"
            "if [ \"$lease_valid\" != \"t\" ]; then echo 'transfer deferred by expired endpoint lease; retry later' >&2; exit 1; fi\n"
            ": \"${max_segments_per_minute:?missing archive policy}\"\n"
            ": \"${pause_ms:?missing archive policy}\"\n"
            "rate_pause_ms=$(( (60000 + max_segments_per_minute - 1) / max_segments_per_minute ))\n"
            "if [ \"$pause_ms\" -lt \"$rate_pause_ms\" ]; then pause_ms=$rate_pause_ms; fi\n"
            "if [ \"$pause_ms\" -gt 0 ]; then sleep \"$(awk \"BEGIN { printf \\\"%.3f\\\", $pause_ms / 1000 }\")\"; fi\n"
            "if [ -f \"$target_dir/$wal_name\" ]; then exit 0; fi\n"
            "cp \"$source_path\" \"$target_dir/.$wal_name.tmp\"\n"
            "mv -f \"$target_dir/.$wal_name.tmp\" \"$target_dir/$wal_name\"\n",
            encoding="ascii",
        )
        os.chmod(script, 0o755)
        # Both public bindings are valid repair targets. Keep the command
        # name discoverable from either target while the script itself reads
        # the active binding and route at execution time.
        neighbor_script = self._target_root / (
            f".archive_transfer_{self.case.archive_neighbor_target_name}_policy.sh"
        )
        shutil.copyfile(script, neighbor_script)
        os.chmod(neighbor_script, 0o755)

    def _write_control_state(self) -> dict:
        if not self.case.publish_safe_profiles:
            rows = _sql_rows(
                self.env,
                f"SELECT batch_rows, pause_ms "
                f"FROM {BACKFILL_CONFIG_TABLE} WHERE job_name = {_sql_literal(self.case.write_job_name)};",
            )
            if len(rows) != 1 or len(rows[0]) != 2:
                raise RuntimeError(f"unexpected write control state: {rows!r}")
            batch_rows, pause_ms = (int(value) for value in rows[0])
            return {
                "job_name": self.case.write_job_name,
                "batch_rows": batch_rows,
                "pause_ms": pause_ms,
                "safe_profile_pass": (
                    batch_rows <= self.case.backfill_batch_rows_target
                    and pause_ms >= self.case.backfill_pause_ms_target
                ),
            }
        rows = _sql_rows(
            self.env,
            f"SELECT batch_rows, pause_ms, safe_batch_rows, safe_pause_ms "
            f"FROM {BACKFILL_CONFIG_TABLE} WHERE job_name = {_sql_literal(self.case.write_job_name)};",
        )
        if len(rows) != 1 or len(rows[0]) != 4:
            raise RuntimeError(f"unexpected write control state: {rows!r}")
        batch_rows, pause_ms, safe_batch_rows, safe_pause_ms = (int(value) for value in rows[0])
        return {
            "job_name": self.case.write_job_name,
            "batch_rows": batch_rows,
            "pause_ms": pause_ms,
            "safe_batch_rows": safe_batch_rows,
            "safe_pause_ms": safe_pause_ms,
            "published_profile_unchanged": (
                safe_batch_rows == int(self.case.backfill_batch_rows_target)
                and safe_pause_ms == int(self.case.backfill_pause_ms_target)
            ),
            "safe_profile_pass": (
                safe_batch_rows == int(self.case.backfill_batch_rows_target)
                and safe_pause_ms == int(self.case.backfill_pause_ms_target)
                and
                batch_rows <= self.case.backfill_batch_rows_target
                and pause_ms >= self.case.backfill_pause_ms_target
            ),
        }

    def _maintenance_control_state(self) -> dict:
        """Read the healthy neighbor job's published control row."""
        rows = _sql_rows(
            self.env,
            f"SELECT batch_rows, pause_ms "
            f"FROM {BACKFILL_CONFIG_TABLE} WHERE job_name = {_sql_literal(self.case.maintenance_job_name)};",
        )
        if len(rows) != 1 or len(rows[0]) != 2:
            raise RuntimeError(f"unexpected maintenance control state: {rows!r}")
        batch_rows, pause_ms = (int(value) for value in rows[0])
        return {
            "job_name": self.case.maintenance_job_name,
            "batch_rows": batch_rows,
            "pause_ms": pause_ms,
            "unchanged_pass": (
                batch_rows == int(self.case.maintenance_batch_rows)
                and pause_ms == int(self.case.maintenance_pause_ms)
            ),
        }

    def _init_pgbench(self) -> None:
        deployment = getattr(self.env, "deployment", None)
        if deployment is None or not self._external_services:
            return
        command = [
            "docker", "exec", deployment.container_name,
            "pgbench", "-i", "-s", "1", "-U", self.env.user, "-d", self.env.dbname,
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=180, env={**os.environ, "PGPASSWORD": self.env.password})
        if result.returncode != 0 and "already exists" not in (result.stderr + result.stdout).casefold():
            raise RuntimeError(f"pgbench initialization failed: {result.stderr.strip()}")

    def _start_services(self) -> None:
        if not self._external_services:
            return
        deployment = getattr(self.env, "deployment", None)
        if deployment is None:
            return
        archive_port = int(getattr(deployment, "archive_port", self.case.archive_port))
        self._archive_service = _ArchiveService(self._target_root, archive_port)
        self._archive_service.start()
        # The restore/canary PostgreSQL is published by CheckpointArchiveDeployment
        # on restore_port:5433. Do not bind a second host listener here.

    def _connect(self, application_name: str):
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name=application_name,
        )
        conn.autocommit = True
        self._connections.append(conn)
        return conn

    def _write_loop(
        self,
        *,
        stop_event: threading.Event | None,
        job_name: str,
        table_name: str,
        payload_repeat: int,
    ) -> None:
        conn = None
        try:
            conn = self._connect(job_name)
            with conn.cursor() as cur:
                while stop_event is not None and not stop_event.is_set():
                    cur.execute(
                        f"SELECT batch_rows, pause_ms FROM {BACKFILL_CONFIG_TABLE} "
                        f"WHERE job_name = {_sql_literal(job_name)};"
                    )
                    batch_rows, pause_ms = cur.fetchone()
                    cur.execute(
                        f"INSERT INTO {table_name} (payload) "
                        f"SELECT repeat(md5(random()::text), {int(payload_repeat)}) "
                        f"FROM generate_series(1, {int(batch_rows)});"
                    )
                    self._record_operation_event(
                        timestamp_ms=int(time.time() * 1000),
                        event_type="job_batch",
                        entity_type="write_job",
                        entity=job_name,
                        action="write",
                        status="completed",
                        correlation_id=f"{job_name}-{int(time.time() * 1000)}",
                        details={
                            "table": table_name,
                            "rows": int(batch_rows),
                            "payload_repeat": int(payload_repeat),
                            "pause_ms": int(pause_ms),
                        },
                    )
                    time.sleep(max(0.01, int(pause_ms) / 1000))
        except Exception as exc:
            if self._stop_event is not None and not self._stop_event.is_set():
                print(f"[FaultInjector:{type(self).__name__}] backfill stopped: {exc}")

    def _backfill_loop(self) -> None:
        self._write_loop(
            stop_event=self._backfill_stop_event,
            job_name=self.case.write_job_name,
            table_name=self.case.write_table,
            payload_repeat=self.case.backfill_payload_repeat,
        )

    def _maintenance_loop(self) -> None:
        self._write_loop(
            stop_event=self._maintenance_stop_event,
            job_name=self.case.maintenance_job_name,
            table_name=self.case.maintenance_table,
            payload_repeat=self.case.maintenance_payload_repeat,
        )

    def _pgbench_loop(self) -> None:
        deployment = getattr(self.env, "deployment", None)
        if deployment is None or not self._external_services:
            return
        command = [
            "docker", "exec", deployment.container_name,
            "pgbench", "-n", "-c", "2", "-j", "2", "-T", "120", "-P", "1",
            "-U", self.env.user, "-d", self.env.dbname,
        ]
        try:
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env={**os.environ, "PGPASSWORD": self.env.password})
            self._processes.append(process)
            self._noise_processes.append(process)
            process.wait()
        except Exception as exc:
            if self._stop_event is not None and not self._stop_event.is_set():
                print(f"[FaultInjector:{type(self).__name__}] pgbench stopped: {exc}")

    def _base_backup_loop(self) -> None:
        deployment = getattr(self.env, "deployment", None)
        if deployment is None or not self._external_services:
            return
        backup_path = f"/tmp/aiopsbench-{self.case.case_id}-basebackup"
        command = [
            "docker", "exec", "-u", "postgres", "-e", f"PGPASSWORD={self.env.password}", deployment.container_name,
            "bash", "-lc",
            (
                f"rm -rf {backup_path} && "
                f"if command -v ionice >/dev/null 2>&1; then "
                f"ionice -c 3 nice -n 19 pg_basebackup -D {backup_path} -Fp -X none -c fast "
                f"--no-sync --max-rate=2MB -U {self.env.user} -h localhost; "
                f"else nice -n 19 pg_basebackup -D {backup_path} -Fp -X none -c fast "
                f"--no-sync --max-rate=2MB -U {self.env.user} -h localhost; fi"
            ),
        ]
        process = None
        try:
            self._record_operation_event(
                timestamp_ms=int(time.time() * 1000),
                event_type="backup_run",
                entity_type="backup_job",
                entity=self.case.maintenance_job_name,
                action="start",
                status="running",
                correlation_id=f"backup-{self.case.case_id}",
                details={"path": backup_path, "max_rate": "2MB"},
            )
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._processes.append(process)
            self._noise_processes.append(process)
            deadline = time.monotonic() + max(60, self.case.replay_seconds * 10)
            while process.poll() is None:
                if self._stop_event is not None and self._stop_event.wait(0.25):
                    process.terminate()
                    break
                if time.monotonic() >= deadline:
                    process.terminate()
                    break
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            self._record_operation_event(
                timestamp_ms=int(time.time() * 1000),
                event_type="backup_run",
                entity_type="backup_job",
                entity=self.case.maintenance_job_name,
                action="finish",
                status="completed" if process.returncode == 0 else "failed",
                correlation_id=f"backup-{self.case.case_id}",
                details={"path": backup_path, "return_code": process.returncode},
            )
        except Exception as exc:
            print(f"[FaultInjector:{type(self).__name__}] base backup noise stopped: {exc}")

    def _run_base_backup(self, backup_path: str) -> tuple[bool, str | None]:
        """Take a task-owned physical backup and return its own error."""
        deployment = getattr(self.env, "deployment", None)
        if deployment is None or not self._external_services:
            return True, None
        command = [
            "docker", "exec", "-u", "postgres", "-e", f"PGPASSWORD={self.env.password}", deployment.container_name,
            "bash", "-lc",
            (
                f"rm -rf {backup_path} && "
                # This backup is immediately used as a restore data directory.
                # Let pg_basebackup fsync it instead of racing pg_ctl against
                # an asynchronously flushed --no-sync directory.
                f"pg_basebackup -D {backup_path} -Fp -X none -c fast "
                f"-U {self.env.user} -h localhost"
            ),
        ]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=max(600, self.case.replay_seconds * 60),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, str(exc)
        if result.returncode != 0:
            return False, (result.stderr or result.stdout).strip()
        return True, None

    def _start_healthy_history_workload(self) -> None:
        """Run the governed write jobs at their healthy profile for the normal capture."""
        self._stop_event = threading.Event()
        self._backfill_stop_event = threading.Event()
        self._maintenance_stop_event = threading.Event()
        self._noise_stop_event = threading.Event()
        self._backfill_thread = threading.Thread(target=self._backfill_loop, daemon=True)
        self._maintenance_thread = threading.Thread(target=self._maintenance_loop, daemon=True)
        self._threads = [self._backfill_thread, self._maintenance_thread]
        for thread in self._threads:
            thread.start()

    def _start_workloads(self) -> None:
        self._stop_event = threading.Event()
        self._backfill_stop_event = threading.Event()
        self._maintenance_stop_event = threading.Event()
        self._noise_stop_event = threading.Event()
        self._backfill_thread = threading.Thread(target=self._backfill_loop, daemon=True)
        self._maintenance_thread = threading.Thread(target=self._maintenance_loop, daemon=True)
        self._noise_threads = [threading.Thread(target=self._pgbench_loop, daemon=True)]
        if self.case.base_backup_noise:
            self._noise_threads.append(threading.Thread(target=self._base_backup_loop, daemon=True))
        self._threads = [self._backfill_thread, self._maintenance_thread, *self._noise_threads]
        if self.case.archive_fault_start_delay_seconds > 0:
            self._archive_fault_stop_event = threading.Event()
            self._archive_fault_thread = threading.Thread(target=self._archive_fault_transition_loop, daemon=True)
            self._threads.append(self._archive_fault_thread)
        for thread in self._threads:
            thread.start()

    def _stop_replay_noise(self) -> None:
        """Stop injector-owned noise while keeping the target writer alive for replay."""
        if self._noise_stop_event is not None:
            self._noise_stop_event.set()
        if self._archive_fault_stop_event is not None:
            self._archive_fault_stop_event.set()
        deployment = getattr(self.env, "deployment", None)
        if deployment is not None and self._external_services:
            # docker exec's client process can exit while its child remains in
            # the container. Reap only the exact workload process names owned
            # by this injector before joining local threads.
            for process_name in ("pgbench", "pg_basebackup"):
                subprocess.run(
                    ["docker", "exec", deployment.container_name, "pkill", "-TERM", "-x", process_name],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
        for process in self._noise_processes:
            if process.poll() is None:
                process.terminate()
        for process in self._noise_processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        for thread in self._noise_threads:
            thread.join(timeout=5)
        if deployment is not None and self._external_services:
            # The noise backup shares the container overlay with the replay
            # backup. Remove the injector-owned copy before replay allocates
            # its two task-owned physical backups.
            backup_path = f"/tmp/aiopsbench-{self.case.case_id}-basebackup"
            subprocess.run(
                ["docker", "exec", deployment.container_name, "rm", "-rf", backup_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
        self._noise_threads.clear()
        self._noise_processes.clear()

    def _stop_workloads(self) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
        if self._backfill_stop_event is not None:
            self._backfill_stop_event.set()
        if self._maintenance_stop_event is not None:
            self._maintenance_stop_event.set()
        if self._noise_stop_event is not None:
            self._noise_stop_event.set()
        self._stop_replay_noise()
        deployment = getattr(self.env, "deployment", None)
        for process in self._processes:
            if process.poll() is None:
                process.terminate()
        for process in self._processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        for thread in self._threads:
            thread.join(timeout=5)
        archive_fault_thread = self._archive_fault_thread
        archive_fault_thread_alive = bool(
            archive_fault_thread is not None and archive_fault_thread.is_alive()
        )
        archive_fault_transition_error = self._archive_fault_transition_error
        if deployment is not None and self._external_services:
            backup_path = f"/tmp/aiopsbench-{self.case.case_id}-basebackup"
            subprocess.run(
                ["docker", "exec", deployment.container_name, "rm", "-rf", backup_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
        for conn in self._connections:
            try:
                conn.close()
            except Exception:
                pass
        self._connections.clear()
        self._processes.clear()
        self._threads.clear()
        self._noise_processes.clear()
        self._noise_threads.clear()
        self._backfill_thread = None
        self._maintenance_thread = None
        self._stop_event = None
        self._backfill_stop_event = None
        self._maintenance_stop_event = None
        self._noise_stop_event = None
        self._archive_fault_stop_event = None
        self._archive_fault_thread = None
        if archive_fault_thread_alive:
            raise RuntimeError(
                "archive fault transition thread did not stop; the dual-fault capture is invalid"
            )
        if archive_fault_transition_error:
            raise RuntimeError(
                "archive fault transition failed during workload shutdown; the dual-fault capture is invalid: "
                f"error={archive_fault_transition_error}"
            )

    def install(self, context: FaultLifecycleContext) -> None:
        self._apply_config(context)
        self._recovered = False
        self._archive_fault_transition_error = None
        self._stop_workloads()
        if self._archive_service is not None:
            self._archive_service.stop()
        self._target_root.mkdir(parents=True, exist_ok=True)
        if self._external_services:
            os.chmod(self._target_root, 0o777)
        initial_binding_fault = (
            (self.case.archive_binding_fault or self.case.archive_route_fault)
            and self.case.archive_fault_start_delay_seconds <= 0
        )
        self._ensure_tables(binding_fault=initial_binding_fault)
        if self._external_services:
            self._write_archive_policy_script()
        self._init_pgbench()
        self._set_backfill_profile(fault=True)
        if self.case.archive_fault_start_delay_seconds > 0:
            self._set_archive_policy(fault=False)
            self._set_archive_guard(fault=False)
            self._set_archive_repository(fault=False)
            self._set_archive_binding(fault=False)
        else:
            self._set_archive_policy(fault=True)
            self._set_archive_guard(fault=True)
            self._set_archive_repository(fault=True)
            self._set_archive_binding(fault=True)
        self._set_settings(fault=True)
        self._start_services()
        self._start_workloads()
        self._replay_artifact = None

    def prepare_metric_history(self, context: FaultLifecycleContext) -> None:
        """Prepare the healthy baseline before the normal history window starts."""
        self._apply_config(context)
        if self._target_root is None:
            raise RuntimeError("archive target root is unavailable during metric history preparation")
        self._target_root.mkdir(parents=True, exist_ok=True)
        if self._external_services:
            os.chmod(self._target_root, 0o777)
        self._ensure_tables()
        if self._external_services:
            self._write_archive_policy_script()
        self._set_backfill_profile(fault=False)
        self._set_archive_policy(fault=False)
        self._set_archive_guard(fault=False)
        self._set_archive_repository(fault=False)
        self._set_settings(fault=False)
        if self.case.run_healthy_workload_in_normal_capture:
            # Record the governed pre-incident batch cadence into the frozen
            # history: the normal capture is the only place the healthy
            # profile is observable once current state stops publishing it.
            self._start_healthy_history_workload()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._apply_config(context)
        self._recovered = False
        self._verify_persistent_fault()
        if self._external_services:
            self._write_archive_policy_script()
        self._start_services()
        self._start_workloads()

    def _verify_persistent_fault(self) -> None:
        rows = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{self.case.write_table}')::text, "
                "current_setting('archive_mode'), current_setting('archive_command'), "
                "current_setting('checkpoint_timeout'), current_setting('max_wal_size'), "
                "current_setting('checkpoint_completion_target')"
            ),
            "verify checkpoint/archive fault image",
        )["result"]
        if (
            len(rows) != 1
            or rows[0][0] != self.case.write_table
            or str(rows[0][2]) != _policy_archive_command(self.case.archive_target_name)
        ):
            raise RuntimeError(f"checkpoint/archive fault image does not match the case: rows={rows!r}")

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        active_binding = self._active_archive_binding()
        archive_entries = []
        if self._target_root is not None and self._target_root.exists():
            archive_entries = sorted(
                {
                    f"{path.name}/" if path.is_dir() else path.name
                    for path in self._target_root.iterdir()
                }
            )
        return {
            "database_settings": self.env.execute_sql(
                "SELECT current_setting('archive_mode'), current_setting('archive_command'), "
                "current_setting('checkpoint_timeout'), current_setting('max_wal_size'), "
                "current_setting('checkpoint_completion_target'), current_setting('full_page_writes'), "
                "current_setting('fsync'), current_setting('synchronous_commit');"
            ),
            "database_checkpoint_stats": self.env.execute_sql(
                "SELECT checkpoints_timed, checkpoints_req, checkpoint_write_time, checkpoint_sync_time "
                "FROM pg_stat_bgwriter;"
            ),
            "database_wal_stats": self.env.execute_sql(
                "SELECT wal_bytes, wal_fpi, wal_records FROM pg_stat_wal;"
            ),
            "archive_worker_stats": self.env.execute_sql(
                "SELECT archived_count, failed_count, last_archived_wal, last_archived_time, "
                "last_failed_wal, last_failed_time FROM pg_stat_archiver;"
            ),
            "transfer_policy": self.env.execute_sql(
                f"SELECT policy_name, max_segments_per_minute, pause_ms"
                + (
                    ", safe_max_segments_per_minute, safe_pause_ms"
                    if self.case.publish_safe_profiles
                    else ""
                )
                + f" FROM {ARCHIVE_POLICY_TABLE};"
            ),
            "transfer_limits": self.env.execute_sql(
                f"SELECT guard_name, enabled, max_segments_per_minute, pause_ms"
                + (
                    ", safe_enabled, safe_max_segments_per_minute, safe_pause_ms"
                    if self.case.publish_safe_profiles
                    else ""
                )
                + f" FROM {ARCHIVE_GUARD_TABLE};"
            ),
            "endpoint_registry": self.env.execute_sql(
                f"SELECT target_name, repository_name, target_path, enabled, role, binding_generation "
                f"FROM {ARCHIVE_TARGET_REGISTRY_TABLE} ORDER BY target_name;"
            ),
            "endpoint_binding_state": self.env.execute_sql(
                f"SELECT target_name, lease_expires_at, binding_generation FROM {ARCHIVE_BINDING_STATE_TABLE} ORDER BY target_name;"
            ),
            "endpoint_route_state": self.env.execute_sql(
                f"SELECT target_name, route_name, target_path, enabled, binding_generation, worker_activation_epoch "
                f"FROM {ARCHIVE_ROUTE_STATE_TABLE} ORDER BY target_name;"
            ),
            "endpoint_storage_limits": self.env.execute_sql(
                f"SELECT repository_name, quota_mb, reserved_mb, safe_spare_mb "
                f"FROM {ARCHIVE_REPOSITORY_TABLE} ORDER BY repository_name;"
            ),
            "wal_directory_inventory": self.env.execute_sql(
                "SELECT count(*), COALESCE(sum(size), 0) FROM pg_ls_waldir();"
            ),
            "archive_endpoint_inventory": {
                "service_port": getattr(getattr(self.env, "deployment", None), "archive_port", self.case.archive_port),
                "active_target": active_binding["target_name"],
                "repository_name": active_binding["repository_name"],
                "container_path": active_binding["target_path"],
                "standby_container_path": f"{ARCHIVE_TARGET_CONTAINER_PATH}/{ARCHIVE_SHADOW_DIRECTORY}",
                "entries": archive_entries,
                "files": self._archive_inventory(),
            },
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._raise_archive_fault_transition_error()
        self._stop_workloads()
        if self._archive_service is not None:
            self._archive_service.stop()

    def recover(self, context: FaultLifecycleContext) -> None:
        if self._recovered:
            return
        self._apply_config(context)
        self._stop_workloads()
        if self._archive_service is not None:
            self._archive_service.stop()
        if not self.env.reconnect():
            raise RuntimeError(f"could not reconnect during recovery: {context.run_id}")
        self._set_backfill_profile(fault=False)
        self._set_archive_policy(fault=False)
        self._set_archive_guard(fault=False)
        self._set_archive_repository(fault=False)
        self._set_settings(fault=False)
        with self.env.metrics_hidden():
            for table_name, label in (
                (f"{self.case.write_table}_markers", "drop PITR marker table"),
                (self.case.write_table, "drop backfill table"),
                (self.case.maintenance_table, "drop maintenance table"),
                (NORMAL_WAL_TABLE, "drop normal WAL table"),
                (OLTP_TABLE, "drop OLTP workload table"),
                (BACKFILL_CONFIG_TABLE, "drop backfill controls"),
                (ARCHIVE_POLICY_TABLE, "drop archive policy"),
                (ARCHIVE_GUARD_TABLE, "drop archive guard"),
                (ARCHIVE_TARGET_REGISTRY_TABLE, "drop archive target registry"),
                (ARCHIVE_BINDING_STATE_TABLE, "drop archive binding state"),
                (ARCHIVE_ROUTE_STATE_TABLE, "drop archive route state"),
                (ARCHIVE_REPOSITORY_TABLE, "drop archive repository limits"),
            ):
                _require_sql_success(
                    _execute_sql_for_injector(self.env, f"DROP TABLE IF EXISTS {table_name};"),
                    label,
                )
            for function_name, label in (
                (ARCHIVE_AVAILABLE_FUNCTION, "drop archive availability function"),
                (ARCHIVE_SAFE_SPARE_FUNCTION, "drop archive safe-spare function"),
            ):
                _require_sql_success(
                    _execute_sql_for_injector(self.env, f"DROP FUNCTION IF EXISTS {function_name}(text);"),
                    label,
                )
            # The policy script is task-scoped and is removed below. Leave a
            # durable direct-copy archive command behind for callers that keep
            # the database alive after recover() returns.
            _require_sql_success(
                self.env.execute_sql(
                    f"ALTER SYSTEM SET archive_command = {_sql_literal(_healthy_archive_command(self.case.archive_target_name))};"
                ),
                "restore standalone healthy archive command",
            )
            _require_sql_success(
                _execute_sql_for_injector(self.env, "SELECT pg_reload_conf();"),
                "reload standalone archive command",
            )
        shutil.rmtree(self._target_root, ignore_errors=True)
        self._replay_artifact = None
        self._recovered = True

    def cleanup(self, context: FaultLifecycleContext) -> None:
        """Idempotent explicit cleanup hook for callers outside Orchestrator."""
        if not self._recovered:
            self.recover(context)

    def _archive_inventory(self) -> dict:
        active_root = self._active_archive_root()
        if not active_root.exists():
            return {"file_count": 0, "bytes": 0}
        files = [path for path in active_root.rglob("*") if path.is_file()]
        return {"file_count": len(files), "bytes": sum(path.stat().st_size for path in files)}

    def _active_archive_binding(self) -> dict[str, str]:
        """Return the single published active target/repository binding."""
        if self.env is None or not self._external_services:
            return {
                "target_name": self.case.archive_target_name,
                "repository_name": self.case.archive_repository_name,
                "target_path": _archive_target_container_subpath(self.case.archive_target_name),
            }
        rows = _sql_rows(
            self.env,
            f"SELECT target_name, repository_name, target_path FROM {ARCHIVE_TARGET_REGISTRY_TABLE} "
            "WHERE enabled AND role = 'active' ORDER BY target_name;",
        )
        if len(rows) != 1 or len(rows[0]) != 3:
            raise RuntimeError(f"exactly one active archive target binding is required: {rows!r}")
        target_name, repository_name, target_path = (str(value) for value in rows[0])
        prefix = f"{ARCHIVE_TARGET_CONTAINER_PATH}/"
        if not target_path.startswith(prefix):
            raise RuntimeError(
                "active archive target path is outside the task repository: "
                f"path={target_path!r}, required_prefix={prefix!r}"
            )
        relative = target_path.removeprefix(prefix)
        if not relative or relative.startswith("/") or ".." in Path(relative).parts:
            raise RuntimeError(f"active archive target path is outside the task repository: path={target_path!r}")
        return {
            "target_name": target_name,
            "repository_name": repository_name,
            "target_path": target_path,
        }

    def _active_archive_container_path(self) -> str:
        rows = _sql_rows(
            self.env,
            f"SELECT route.target_path FROM {ARCHIVE_ROUTE_STATE_TABLE} route "
            f"JOIN {ARCHIVE_TARGET_REGISTRY_TABLE} t ON t.target_name = route.target_name "
            "WHERE route.enabled AND t.enabled AND t.role = 'active';",
        )
        if len(rows) != 1 or len(rows[0]) != 1:
            raise RuntimeError(f"active archive binding is unavailable: {rows!r}")
        target_path = str(rows[0][0])
        prefix = f"{ARCHIVE_TARGET_CONTAINER_PATH}/"
        if not target_path.startswith(prefix) or target_path == prefix:
            raise RuntimeError(f"active archive binding path is outside the task target: {target_path!r}")
        relative_path = Path(target_path[len(prefix):])
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise RuntimeError(f"active archive binding path is outside the task target: {target_path!r}")
        return target_path

    def _archive_binding_lease_valid(self) -> bool:
        rows = _sql_rows(
            self.env,
            f"SELECT l.lease_expires_at > clock_timestamp() "
            "AND t.binding_generation = l.binding_generation "
            "AND t.binding_generation = route.binding_generation "
            "AND t.binding_generation = route.worker_activation_epoch "
            f"FROM {ARCHIVE_BINDING_STATE_TABLE} l "
            f"JOIN {ARCHIVE_TARGET_REGISTRY_TABLE} t ON t.target_name = l.target_name "
            f"JOIN {ARCHIVE_ROUTE_STATE_TABLE} route ON route.target_name = t.target_name "
            "WHERE t.enabled AND t.role = 'active' AND route.enabled;",
        )
        return len(rows) == 1 and len(rows[0]) == 1 and bool(rows[0][0])

    def _active_archive_root(self) -> Path:
        if self._target_root is None or self.case is None:
            raise RuntimeError("archive target is not initialized")
        target_path = self._active_archive_container_path()
        relative_path = target_path[len(f"{ARCHIVE_TARGET_CONTAINER_PATH}/"):]
        return self._target_root / relative_path

    def _snapshot(self) -> dict:
        rows = _sql_rows(
            self.env,
            "SELECT b.checkpoints_req, b.checkpoints_timed, b.checkpoint_write_time, w.wal_bytes, w.wal_fpi, "
            "a.archived_count, a.failed_count, "
            "(SELECT COALESCE(sum(size), 0) FROM pg_ls_waldir()) "
            "FROM pg_stat_bgwriter b CROSS JOIN pg_stat_wal w CROSS JOIN pg_stat_archiver a;",
        )
        if len(rows) != 1:
            raise RuntimeError(f"unexpected checkpoint/archive snapshot: {rows!r}")
        return {
            "checkpoints_req": int(rows[0][0] or 0),
            "checkpoints_timed": int(rows[0][1] or 0),
            "checkpoint_write_time": float(rows[0][2] or 0.0),
            "wal_bytes": int(rows[0][3] or 0),
            "wal_fpi": int(rows[0][4] or 0),
            "archived_count": int(rows[0][5] or 0),
            "failed_count": int(rows[0][6] or 0),
            "wal_dir_bytes": int(rows[0][7] or 0),
            "archive_inventory": self._archive_inventory(),
        }

    def _run_oltp_replay(self) -> tuple[float, float, int]:
        if not self._external_services:
            return 1.0, 1.0, 1
        deadline = time.monotonic() + self.case.replay_seconds
        latencies = []
        successes = 0
        while time.monotonic() < deadline:
            started = time.monotonic()
            try:
                with self.env._conn.cursor() as cur:
                    cur.execute("UPDATE pgbench_accounts SET abalance = abalance + 1 WHERE aid = 1")
                    self.env._conn.commit()
                successes += 1
            except Exception:
                try:
                    self.env._conn.rollback()
                except Exception:
                    pass
            latencies.append((time.monotonic() - started) * 1000)
            time.sleep(0.02)
        if not latencies:
            return 0.0, float("inf"), 0
        p99 = quantiles(latencies, n=100, method="inclusive")[98] if len(latencies) >= 2 else latencies[0]
        return successes / max(self.case.replay_seconds, 1), p99, successes

    def _run_report_replay(self) -> tuple[bool, float, str | None]:
        """Run one bounded report query as part of the joint replay contract."""
        if not self._external_services:
            return True, 0.0, None
        connection = None
        started = time.monotonic()
        try:
            connection = self._connect("checkpoint_archive_report_replay")
            with connection.cursor() as cursor:
                # q1 can exceed the old floor on the formal TPC-DS image; keep
                # the acceptance query bounded while allowing one measured
                # replay on the declared resource contract to finish.
                cursor.execute("SET statement_timeout = %s", (max(300_000, self.case.replay_seconds * 20_000),))
                cursor.execute(get_tpcds_query(_report_replay_query_name(self.case)))
                cursor.fetchall()
            return True, (time.monotonic() - started) * 1000, None
        except Exception as exc:
            return False, (time.monotonic() - started) * 1000, str(exc)
        finally:
            if connection is not None:
                try:
                    connection.close()
                finally:
                    if connection in self._connections:
                        self._connections.remove(connection)

    def _run_restore_canary(self, marker: str, marker_lsn: str, backup_path: str) -> bool:
        deployment = getattr(self.env, "deployment", None)
        if deployment is None or not self._external_services:
            return True
        self._restore_error = None
        sql_marker = marker.replace("'", "''")
        active_archive_path = self._active_archive_container_path()
        command = [
            "docker", "exec", "-u", "postgres", "-e", f"PGPASSWORD={self.env.password}", deployment.container_name,
            "bash", "-lc",
            "set -e; "
            "PG_BIN=$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1); "
            f"restore_path={backup_path}; rm -f \"$restore_path/postmaster.pid\"; "
            "test -f \"$restore_path/PG_VERSION\"; "
            # pg_basebackup does not copy configuration files that are
            # external to PGDATA. Supply a minimal local-only config for the
            # isolated canary while preserving the backup's data and WAL.
            "mkdir -p \"$restore_path/pg_tblspc\" \"$restore_path/pg_twophase\" \"$restore_path/pg_subtrans\" \"$restore_path/pg_xact\"; "
            "if [ ! -f \"$restore_path/postgresql.conf\" ]; then printf \"listen_addresses = '127.0.0.1'\\nport = 5433\\n\" > \"$restore_path/postgresql.conf\"; fi; "
            "if [ ! -f \"$restore_path/pg_hba.conf\" ]; then printf \"local all all trust\\nhost all all 127.0.0.1/32 trust\\n\" > \"$restore_path/pg_hba.conf\"; fi; "
            f"printf \"restore_command = 'test -f {active_archive_path}/%%f && cp "
            f"{active_archive_path}/%%f %%p'\\n"
            f"recovery_target_lsn = '{marker_lsn}'\\nrecovery_target_inclusive = 'on'\\n"
            f"recovery_target_action = 'promote'\\n\" "
            f">> \"$restore_path/postgresql.auto.conf\"; touch \"$restore_path/recovery.signal\"; "
            f"cleanup() {{ \"$PG_BIN/pg_ctl\" -D \"$restore_path\" -m fast -t 60 -w stop >/dev/null 2>&1 || true; "
            f"rm -rf \"$restore_path\"; }}; trap cleanup EXIT; "
            f"\"$PG_BIN/pg_ctl\" -D \"$restore_path\" -o '-p 5433' -t 300 -w start; "
            # pg_ctl -w only waits for a read-only recovery server to accept
            # connections. Wait for recovery_target_action=promote before
            # checking the marker, otherwise a long WAL replay is sampled at
            # the backup's consistency point.
            "recovery_deadline=$((SECONDS + 300)); "
            "while [ \"$(\"$PG_BIN/psql\" -X -At -p 5433 -U "
            f"{self.env.user} -d {self.env.dbname} -c \"SELECT pg_is_in_recovery()\" | tr -d '[:space:]')\" = 't' ]; do "
            "if [ \"$SECONDS\" -ge \"$recovery_deadline\" ]; then echo 'PITR recovery did not promote at target LSN' >&2; exit 1; fi; "
            "sleep 1; done; "
            f"marker_count=$(\"$PG_BIN/psql\" -X -v ON_ERROR_STOP=1 -At -p 5433 -U {self.env.user} -d {self.env.dbname} "
            f"-c \"SELECT count(*) FROM {self.case.write_table}_markers WHERE marker_id = '{sql_marker}'\" | tr -d '[:space:]'); "
            "test \"$marker_count\" = 1 || { echo \"pitr marker count=$marker_count\" >&2; exit 1; }; "
            "true",
        ]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=max(600, self.case.replay_seconds * 80),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self._restore_error = str(exc)
            return False
        if result.returncode != 0:
            self._restore_error = (
                f"returncode={result.returncode}; "
                f"stdout={(result.stdout or '').strip()[-2000:]}; "
                f"stderr={(result.stderr or '').strip()[-8000:]}"
            )
        return result.returncode == 0

    def _archive_ready_count(self) -> int:
        rows = _sql_rows(
            self.env,
            "SELECT count(*) FROM pg_ls_dir('pg_wal/archive_status') "
            "WHERE pg_ls_dir LIKE '%.ready';",
        )
        if len(rows) != 1 or len(rows[0]) != 1:
            raise RuntimeError(f"unexpected archive-ready count: {rows!r}")
        return int(rows[0][0] or 0)

    def _wait_for_marker_archive(self, marker_wal_name: str) -> bool:
        """Wait for the exact WAL segment containing the restore point."""
        if not re.fullmatch(r"[0-9A-F]{24}", marker_wal_name):
            raise ValueError(f"invalid restore-point WAL segment name: {marker_wal_name!r}")
        if self._target_root is None:
            raise RuntimeError("archive target is not initialized")
        # A stale public lease is a recoverable archive-binding failure. Keep
        # it in the trusted replay artifact instead of converting it into an
        # evaluator/tool exception after a long blind wait.
        if not self._archive_binding_lease_valid():
            return False
        marker_wal_path = self._active_archive_root() / marker_wal_name
        deadline = time.monotonic() + max(30, self.case.archive_delay_fault_seconds * 12)
        while time.monotonic() < deadline:
            if marker_wal_path.is_file() and marker_wal_path.stat().st_size > 0:
                return True
            time.sleep(0.5)
        return False

    def collect_outcome_artifact(self, context) -> Mapping[str, object]:
        if self._replay_artifact is not None:
            return self._replay_artifact
        # Evaluators may be invoked against a persisted CaseRun without the
        # injector lifecycle being replayed in this process. Bind the run
        # environment lazily for artifact collection in that case.
        if self.env is None:
            self.env = context.case_run.env
        fake_artifact = getattr(self.env, "checkpoint_archive_replay_artifact", None)
        if fake_artifact is not None:
            self._replay_artifact = dict(fake_artifact)
            return self._replay_artifact
        # The agent has submitted its repair. Stop only the injector-owned
        # fault generators before measuring the next replay so base backup and
        # PITR test recovery are not contending with the fault itself.
        self._stop_replay_noise()
        backup_root = f"/tmp/aiopsbench-{self.case.case_id}"
        pitr_backup_path = f"{backup_root}-pitr-basebackup"
        replay_backup_path = f"{backup_root}-replay-backup"
        write_control = self._write_control_state()
        maintenance_control = self._maintenance_control_state()
        archive_policy = self._archive_policy_state()
        archive_guard = self._archive_guard_state()
        archive_repository = self._archive_repository_state()
        pitr_backup_pass, pitr_backup_error = self._run_base_backup(pitr_backup_path)
        # The fault window can leave a requested checkpoint in flight while
        # the agent is repairing settings. Drain that old checkpoint before
        # taking the replay baseline; otherwise its historical write time is
        # charged to the repaired replay.
        _require_sql_success(self.env.execute_sql("CHECKPOINT;"), "drain pre-replay checkpoint")
        before = self._snapshot()
        marker = _pitr_marker(context.run_id, random.randrange(1_000_000))
        _require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.case.write_table}_markers (marker_id) VALUES ({_sql_literal(marker)});"
            ),
            "commit random PITR marker row",
        )
        # Put the marker transaction in a completed archive segment before
        # creating the recovery point. The recovery target is then strictly
        # after the marker, even when both would otherwise share a segment.
        _require_sql_success(self.env.execute_sql("SELECT pg_switch_wal();"), "switch WAL after PITR marker")
        restore_point_rows = _sql_rows(
            self.env,
            f"SELECT pg_create_restore_point({_sql_literal(marker)});",
        )
        if len(restore_point_rows) != 1 or len(restore_point_rows[0]) != 1:
            raise RuntimeError(f"unexpected restore point result: {restore_point_rows!r}")
        marker_lsn = str(restore_point_rows[0][0])
        marker_wal_rows = _sql_rows(
            self.env,
            f"SELECT pg_walfile_name({_sql_literal(marker_lsn)}::pg_lsn);",
        )
        if len(marker_wal_rows) != 1 or len(marker_wal_rows[0]) != 1:
            raise RuntimeError(f"unexpected restore point WAL result: {marker_wal_rows!r}")
        marker_wal_name = str(marker_wal_rows[0][0])
        _require_sql_success(self.env.execute_sql("SELECT pg_switch_wal();"), "switch WAL for PITR marker")
        marker_archived = self._wait_for_marker_archive(marker_wal_name)
        report_result: dict[str, object] = {}

        def run_report() -> None:
            passed, elapsed_ms, error = self._run_report_replay()
            report_result.update(
                passed=passed,
                elapsed_ms=elapsed_ms,
                error=error,
            )

        report_thread = threading.Thread(target=run_report, name="checkpoint-archive-report-replay")
        report_thread.start()
        tps, p99_ms, successful_transactions = self._run_oltp_replay()
        report_thread.join()
        report_replay_pass = bool(report_result.get("passed", False))
        report_replay_elapsed_ms = float(report_result.get("elapsed_ms", 0.0) or 0.0)
        report_replay_error = report_result.get("error")
        # pg_basebackup -c fast intentionally requests a checkpoint. Capture
        # the workload checkpoint counters before that backup-only checkpoint
        # so checkpoint_slo_pass measures the repaired mixed write window.
        workload_after = self._snapshot()
        replay_backup_pass, replay_backup_error = self._run_base_backup(replay_backup_path)
        _require_sql_success(self.env.execute_sql("SELECT pg_switch_wal();"), "switch WAL for PITR marker")
        after = self._snapshot()
        binding_lease_pass = self._archive_binding_lease_valid()
        ready_count = self._archive_ready_count()
        archive_failed_delta = after["failed_count"] - before["failed_count"]
        if binding_lease_pass:
            convergence_deadline = time.monotonic() + max(30, self.case.replay_seconds * 5)
            while ready_count > 0 and time.monotonic() < convergence_deadline:
                time.sleep(0.5)
                after = self._snapshot()
                ready_count = self._archive_ready_count()
                archive_failed_delta = after["failed_count"] - before["failed_count"]
        checkpoint_req_delta = workload_after["checkpoints_req"] - before["checkpoints_req"]
        checkpoint_timed_delta = workload_after["checkpoints_timed"] - before["checkpoints_timed"]
        checkpoint_write_delta = workload_after["checkpoint_write_time"] - before["checkpoint_write_time"]
        wal_generated_bytes = max(0, after["wal_bytes"] - before["wal_bytes"])
        wal_dir_growth_bytes = max(0, after["wal_dir_bytes"] - before["wal_dir_bytes"])
        wal_growth_bytes = max(wal_generated_bytes, wal_dir_growth_bytes)
        wal_headroom = wal_growth_bytes <= self.case.wal_space_budget_bytes
        archive_converged = (
            binding_lease_pass
            and ready_count == 0
            and archive_failed_delta == 0
            and after["archived_count"] >= before["archived_count"]
        )
        pitr_marker_pass = (
            pitr_backup_pass
            and replay_backup_pass
            and marker_archived
            and self._run_restore_canary(marker, marker_lsn, pitr_backup_path)
        )
        self._replay_artifact = {
            "replay_completed": True,
            "pitr_base_backup_pass": pitr_backup_pass,
            "backup_replay_pass": replay_backup_pass,
            "report_replay_pass": report_replay_pass,
            "oltp_slo_pass": tps >= self.case.min_tps and p99_ms <= self.case.max_p99_ms,
            "write_control_safe_profile_pass": write_control["safe_profile_pass"],
            "maintenance_control_unchanged_pass": maintenance_control["unchanged_pass"],
            "archive_policy_safe_profile_pass": archive_policy["safe_profile_pass"],
            "archive_guard_safe_profile_pass": archive_guard["safe_profile_pass"],
            "archive_repository_safe_profile_pass": archive_repository["safe_profile_pass"],
            "checkpoint_slo_pass": checkpoint_req_delta <= self.case.max_checkpoint_req_delta and checkpoint_write_delta <= self.case.max_checkpoint_write_ms,
            "archive_backlog_converged": archive_converged,
            "archive_binding_lease_pass": binding_lease_pass,
            "archive_binding_coherence_pass": binding_lease_pass,
            "wal_headroom_pass": wal_headroom,
            "pitr_marker_pass": pitr_marker_pass,
            "tps": round(tps, 3),
            "p99_ms": round(p99_ms, 3),
            "successful_transactions": successful_transactions,
            "report_query_name": _report_replay_query_name(self.case),
            "report_replay_elapsed_ms": round(report_replay_elapsed_ms, 3),
            "write_control": write_control,
            "maintenance_control": maintenance_control,
            "archive_policy": archive_policy,
            "archive_guard": archive_guard,
            "archive_repository": archive_repository,
            "checkpoint_req_delta": checkpoint_req_delta,
            "checkpoint_timed_delta": checkpoint_timed_delta,
            "checkpoint_write_time_delta_ms": round(checkpoint_write_delta, 3),
            "archive_failed_delta": archive_failed_delta,
            "archive_ready_count": ready_count,
            "wal_baseline_bytes": before["wal_dir_bytes"],
            "wal_stat_baseline_bytes": before["wal_bytes"],
            "wal_generated_bytes": wal_generated_bytes,
            "wal_dir_growth_bytes": wal_dir_growth_bytes,
            "wal_growth_bytes": wal_growth_bytes,
            "wal_dir_bytes": after["wal_dir_bytes"],
            "archive_target": self._archive_inventory(),
            "marker": marker,
            "marker_lsn": marker_lsn,
            "marker_wal_name": marker_wal_name,
        }
        if self._restore_error:
            self._replay_artifact["restore_error"] = self._restore_error
        if pitr_backup_error:
            self._replay_artifact["pitr_backup_error"] = pitr_backup_error
        if replay_backup_error:
            self._replay_artifact["replay_backup_error"] = replay_backup_error
        if report_replay_error:
            self._replay_artifact["report_replay_error"] = str(report_replay_error)
        cleanup = [
            "docker", "exec", deployment.container_name, "rm", "-rf",
            pitr_backup_path, replay_backup_path,
        ] if (deployment := getattr(self.env, "deployment", None)) is not None and self._external_services else None
        if cleanup is not None:
            subprocess.run(cleanup, capture_output=True, text=True, timeout=30)
        if pitr_backup_error or replay_backup_error:
            self._replay_artifact["backup_error"] = "; ".join(
                error for error in (pitr_backup_error, replay_backup_error) if error
            )
        return self._replay_artifact


class PgSystemFailureCheckpointArchiveScenario(PostgresScenario):
    scenario_id = SCENARIO_ID
    description = "Simulates independent checkpoint pressure and archive throughput loss with joint replay and PITR validation."
    cases = (_HARD_CASE, _SIMPLE_CASE)

    def build_fault_plan(self, case: PgSystemFailureCheckpointArchiveCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureCheckpointArchiveInjector,
                config={
                    "archive_port": case.archive_port,
                    "restore_port": case.restore_port,
                    "run_external_services": True,
                },
            ),
        )


__all__ = (
    "ARCHIVE_PORT",
    "BASE_IMAGE_NAME",
    "FAULT_IMAGE_PREFIX",
    "PgSystemFailureCheckpointArchiveCase",
    "PgSystemFailureCheckpointArchiveForCheckpointArchiveDualFaultScenarioCase",
    "PgSystemFailureCheckpointArchiveForCheckpointArchiveDualFaultSimpleScenarioCase",
    "PgSystemFailureCheckpointArchiveInjector",
    "PgSystemFailureCheckpointArchiveScenario",
    "CheckpointArchiveDeployment",
    "PRIMARY_PORT",
    "RESTORE_CANARY_PORT",
)
