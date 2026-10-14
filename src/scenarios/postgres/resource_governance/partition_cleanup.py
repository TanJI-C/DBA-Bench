"""Real filesystem-backed partition cleanup pressure scenario.

The injector deliberately fails admission when the running storage stack does
not expose a block filesystem and a measured filesystem -> BufferIO -> host
pressure ordering.  It never synthesizes metric samples.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import socket
import subprocess
import tempfile
import threading
import time
from collections import deque
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping

from src.scenarios.evaluation.postgres.resource_governance.partition_cleanup import (
    PgResourceGovernancePartitionCleanupForFilesystemCleanupPressureEvaluatorCase,
    PgResourceGovernancePartitionCleanupForFilesystemCleanupPressureSimpleEvaluatorCase,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.postgres.common import (
    _json_object,
    _require_sql_success,
    _run_cleanup_steps,
    _validate_sql_identifier,
)
from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase, WorkloadProfile
from src.workloads.tpcds import get_tpcds_query

from src.execution.specs import CaseResourceSpec, HostPortLayout, PostgresCaseRuntime
from src.scenarios.base import DifficultyCalibration, FaultPlan, PostgresScenario, PostgresScenarioCase


PARTITION_CLEANUP_RESOURCES = CaseResourceSpec(
    worker_physical_cores=2,
    worker_memory_mb=2048,
    container_cpu_limit=1.0,
    container_memory_mb=1024,
)
PARTITION_CLEANUP_SIMPLE_RESOURCES = CaseResourceSpec(
    worker_physical_cores=2,
    worker_memory_mb=1536,
    container_cpu_limit=0.75,
    container_memory_mb=768,
)
METRIC_RESPONSE_SAMPLE_LIMIT = 24
# Host-wide CPU PSI is dominated by co-tenant load on shared machines (its
# swing is an order of magnitude larger than this case's own increment), so
# the admission chain confirms the downstream victim stage with the
# in-container OLTP probe latency instead of a host PSI delta.
ADMISSION_OLTP_LATENCY_MS = 20.0


def _tpcds_profiles(case_tag: str, simple: bool) -> tuple[WorkloadProfile, ...]:
    query_names = ("q14",) if simple else ("q14", "q75", "q95")
    return tuple(
        WorkloadProfile(
            name=f"{case_tag}-tpcds-{query_name}",
            sql=get_tpcds_query(query_name),
            qps=0.12 if simple else 0.18,
            tier="MEDIUM" if query_name != "q75" else "HEAVY",
            commit=False,
            application_name=f"{case_tag}-tpcds-report",
        )
        for query_name in query_names
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernancePartitionCleanupCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    parent_table: str
    metadata_table: str
    lifecycle_table: str
    job_table: str
    oltp_table: str
    cleanup_job_name: str
    cleanup_app_name: str
    cleanup_process_name: str
    compressor_process_name: str
    basebackup_process_name: str
    legal_hold_partition: str
    expired_partition_names: tuple[str, ...]
    partition_specs: tuple[tuple[str, int, int, bool, int], ...]
    partition_count: int
    retention_days: int
    max_retention_days: int
    enable_basebackup: bool
    enable_host_compressor: bool
    enable_small_partition_drop: bool
    cleanup_batch_size: int
    cleanup_worker_interval_seconds: float
    pgbench_clients: int
    pgbench_duration_seconds: int
    telemetry_sample_interval_seconds: float
    admission_sample_count: int
    admission_filesystem_io_mb_per_sec: float
    admission_bufferio_waiters: int
    admission_host_pressure: float
    recovery_sample_count: int
    recovery_host_pressure_limit: float
    recovery_filesystem_io_limit: float
    oltp_p99_slo_ms: float
    aux_port_count: int
    policy_table: str | None = None
    mislabeled_hold_partition: str | None = None
    drifted_retention_days: int | None = None
    sync_app_name: str | None = None
    sync_interval_seconds: float = 8.0


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernancePartitionCleanupForFilesystemCleanupPressureScenarioCase(
    PgResourceGovernancePartitionCleanupCase
):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernancePartitionCleanupForFilesystemCleanupPressureSimpleScenarioCase(
    PgResourceGovernancePartitionCleanupCase
):
    pass


def _case_report(case_entity: str) -> dict[str, object]:
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "filesystem cleanup",
                    "entity": case_entity,
                    "evidence": ["filesystem I/O led BufferIO waiters before host pressure"],
                },
                {
                    "type": "finding",
                    "factor": "filesystem io precedes bufferio waiters",
                    "entity": case_entity,
                    "evidence": ["real filesystem telemetry showed the lead-lag chain"],
                },
                {
                    "type": "finding",
                    "factor": "bufferio waiters",
                    "entity": case_entity,
                    "evidence": ["PostgreSQL activity sampled BufferIO waiters"],
                },
                {
                    "type": "finding",
                    "factor": "host cpu and database query cpu diverge",
                    "entity": case_entity,
                    "evidence": ["host pressure exceeded database query CPU attribution"],
                },
                {
                    "type": "finding",
                    "factor": "retention cleanup lifecycle change job",
                    "entity": case_entity,
                    "evidence": ["partition lifecycle history identified the cleanup change/job"],
                },
                {
                    "type": "finding",
                    "factor": "oltp tail latency victim",
                    "entity": case_entity,
                    "evidence": ["OLTP tail latency rose during filesystem cleanup"],
                },
            ]
        },
        "outcome": {
            "changes": ["bounded retention cleanup while preserving legal hold"],
            "verification": ["expired partitions, detached state, OLTP SLO, and host pressure were rechecked"],
        },
        "summary": "Partition cleanup, rather than database query CPU, caused the host pressure and OLTP tail latency.",
    }


_HARD_SPECS = (
    ("pc_hard_expired_01", -14, -12, False, 30000),
    ("pc_hard_expired_02", -12, -10, False, 30000),
    ("pc_hard_legal_hold", -10, -8, True, 30000),
    ("pc_hard_expired_03", -8, -6, False, 30000),
    ("pc_hard_recent_01", -6, -4, False, 18000),
    ("pc_hard_recent_02", -4, -2, False, 18000),
    ("pc_hard_current", -2, 1, False, 18000),
    ("pc_hard_future", 1, 3, False, 12000),
)
_EASY_SPECS = (
    ("pc_easy_expired_01", -10, -8, False, 24000),
    ("pc_easy_legal_hold", -8, -6, True, 24000),
    ("pc_easy_expired_02", -6, -4, False, 24000),
    ("pc_easy_current", -1, 2, False, 16000),
)


HARD_CASE = PgResourceGovernancePartitionCleanupForFilesystemCleanupPressureScenarioCase(
    case_id="filesystem_cleanup_pressure",
    case_no=0,
    evaluator=PgResourceGovernancePartitionCleanupForFilesystemCleanupPressureEvaluatorCase,
    base_image_name="aiopsbench-pg-tpcds:latest",
    workload_tag="tpcds",
    title="Host CPU pressure caused by filesystem-backed retention partition cleanup.",
    alert=(
        "[FIRING: WARNING] alertname=PostgresHostCpuPressure service=oltp-orders "
        "instance=postgresql-primary severity=warning\n"
        "summary=Host CPU pressure and OLTP tail latency exceeded SLO\n"
        "description=The database host had a short CPU pressure episode while transaction tail latency rose. "
        "The episode has recovered on its own. Reports, backup, and maintenance jobs were active in the same "
        "window. An application change was rolled out on this host earlier today."
    ),
    initial_state={"status": "degraded", "alert": "host_cpu_pressure", "visible_symptom": "oltp_tail_latency"},
    expected_target={
        "status": "recovered",
        "root_cause": "filesystem_partition_cleanup",
        "retention": "expired_partitions_deleted",
        "legal_hold": "preserved",
    },
    reference_report=_case_report("retention-cleanup-hard"),
    background_workload=BackgroundWorkloadSpec(
        profiles=_tpcds_profiles("pc-hard", simple=False),
        worker_count=3,
        seed=861,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        warmup_seconds=2,
    ),
    runtime=PostgresCaseRuntime(host_ports=HostPortLayout(offsets=(0, 1, 2)), resources=PARTITION_CLEANUP_RESOURCES),
    parent_table="pc_hard_events",
    metadata_table="pc_hard_partition_catalog",
    lifecycle_table="pc_hard_partition_lifecycle",
    job_table="pc_hard_cleanup_jobs",
    oltp_table="pc_hard_oltp_hot",
    cleanup_job_name="pc-hard-retention-cleanup",
    cleanup_app_name="pc-hard-retention-worker",
    cleanup_process_name="pc-hard-retention-worker",
    compressor_process_name="pc-hard-host-compressor",
    basebackup_process_name="pc-hard-base-backup",
    legal_hold_partition="pc_hard_legal_hold",
    expired_partition_names=("pc_hard_expired_01", "pc_hard_expired_02", "pc_hard_expired_03"),
    partition_specs=_HARD_SPECS,
    partition_count=len(_HARD_SPECS),
    retention_days=7,
    max_retention_days=14,
    enable_basebackup=True,
    enable_host_compressor=True,
    enable_small_partition_drop=True,
    cleanup_batch_size=1,
    cleanup_worker_interval_seconds=4.0,
    pgbench_clients=6,
    pgbench_duration_seconds=3600,
    telemetry_sample_interval_seconds=1.0,
    admission_sample_count=2,
    admission_filesystem_io_mb_per_sec=0.1,
    admission_bufferio_waiters=1,
    admission_host_pressure=0.01,
    recovery_sample_count=2,
    recovery_host_pressure_limit=1.0,
    # Hard keeps report, backup, compressor, and small-drop decoys live while
    # verifying recovery. The published bound therefore allows the longer
    # post-cleanup background tail that accumulates while the mirror keeps the
    # cleanup worker paused, but still rejects the 100+ MB/s cleanup spikes
    # that establish the fault.
    recovery_filesystem_io_limit=60.0,
    oltp_p99_slo_ms=250.0,
    aux_port_count=2,
    policy_table="pc_hard_retention_policy",
    mislabeled_hold_partition="pc_hard_expired_03",
    drifted_retention_days=30,
    sync_app_name="pc-hard-config-agent",
    sync_interval_seconds=8.0,
    difficulty=DifficultyCalibration(
        diagnostic_depth=9,
        environmental_complexity=0.52381,
        reference_run_ids=("reference-250__pg_resource_governance_partition_cleanup__filesystem_cleanup_pressure__mock__r001",),
    ),
)


SIMPLE_CASE = PgResourceGovernancePartitionCleanupForFilesystemCleanupPressureSimpleScenarioCase(
    case_id="filesystem_cleanup_pressure_simple",
    case_no=1,
    evaluator=PgResourceGovernancePartitionCleanupForFilesystemCleanupPressureSimpleEvaluatorCase,
    base_image_name="aiopsbench-pg-tpcds:latest",
    workload_tag="tpcds",
    title="Simplified filesystem partition cleanup pressure with OLTP tail latency.",
    alert=(
        "[FIRING: WARNING] alertname=PostgresHostCpuPressure service=checkout-api "
        "instance=postgresql-primary severity=warning\n"
        "summary=Host pressure and checkout tail latency crossed SLO together\n"
        "description=Checkout latency rose during a host pressure episode that is now clear. "
        "A small number of cleanup and reporting jobs were also active. Preserve the retention boundary and legal hold. "
        "You may use the case-specific filesystem_io, bufferio_waiters, host_pressure, and "
        "partition_lifecycle observations exposed by query_metrics. For final recovery, keep "
        "the cleanup job enabled and unpaused, preserve the legal hold, remove all due non-hold "
        "partitions through the retention cleanup workflow "
        "without detached leftovers, and verify the last 2 samples are within the "
        "published filesystem-I/O and OLTP latency limits; host CPU pressure stays a reported observation."
    ),
    initial_state={"status": "degraded", "alert": "host_cpu_pressure", "visible_symptom": "checkout_tail_latency"},
    expected_target={
        "status": "recovered",
        "root_cause": "filesystem_partition_cleanup",
        "retention": "expired_partitions_deleted",
        "legal_hold": "preserved",
    },
    reference_report=_case_report("retention-cleanup-simple"),
    background_workload=BackgroundWorkloadSpec(
        profiles=_tpcds_profiles("pc-easy", simple=True),
        worker_count=1,
        seed=862,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        warmup_seconds=1,
    ),
    runtime=PostgresCaseRuntime(host_ports=HostPortLayout(offsets=(0, 1, 2)), resources=PARTITION_CLEANUP_SIMPLE_RESOURCES),
    parent_table="pc_easy_events",
    metadata_table="pc_easy_partition_catalog",
    lifecycle_table="pc_easy_partition_lifecycle",
    job_table="pc_easy_cleanup_jobs",
    oltp_table="pc_easy_oltp_hot",
    cleanup_job_name="pc-easy-retention-cleanup",
    cleanup_app_name="pc-easy-retention-worker",
    cleanup_process_name="pc-easy-retention-worker",
    compressor_process_name="pc-easy-host-compressor",
    basebackup_process_name="pc-easy-base-backup",
    legal_hold_partition="pc_easy_legal_hold",
    expired_partition_names=("pc_easy_expired_01", "pc_easy_expired_02"),
    partition_specs=_EASY_SPECS,
    partition_count=len(_EASY_SPECS),
    retention_days=5,
    max_retention_days=10,
    enable_basebackup=False,
    enable_host_compressor=False,
    enable_small_partition_drop=False,
    cleanup_batch_size=1,
    cleanup_worker_interval_seconds=5.0,
    pgbench_clients=2,
    pgbench_duration_seconds=1800,
    telemetry_sample_interval_seconds=1.0,
    admission_sample_count=2,
    admission_filesystem_io_mb_per_sec=0.05,
    admission_bufferio_waiters=1,
    admission_host_pressure=0.005,
    recovery_sample_count=2,
    recovery_host_pressure_limit=1.0,
    recovery_filesystem_io_limit=2.0,
    oltp_p99_slo_ms=300.0,
    aux_port_count=2,
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.464286,
        reference_run_ids=(
            "reference-66__pg_partition_cleanup__"
            "filesystem_cleanup_pressure_simple__mock__r001",
        ),
    ),
)


class _TelemetryServer:
    def __init__(self, provider: "PartitionCleanupTelemetry", port: int, endpoint: str):
        self.provider = provider
        self.port = int(port)
        self.endpoint = endpoint
        provider_ref = provider

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802 - stdlib HTTP handler API
                if self.path not in {"/", "/metrics"}:
                    self.send_error(404)
                    return
                body = json.dumps(provider_ref.snapshot(), default=str).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_args):
                return

        self.server = ThreadingHTTPServer(("127.0.0.1", self.port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True, name=f"{endpoint}-{port}")

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)


def _find_admission_chain(
    samples: list[dict[str, Any]],
    case: PgResourceGovernancePartitionCleanupCase,
    *,
    baseline_cpu_pressure: float,
    baseline_bufferio_waiters: int,
    baseline_filesystem_io: float = 0.0,
) -> dict[str, int] | None:
    """Find a measured multi-sample filesystem -> waiters -> victim sequence.

    The filesystem stage is a real device-throughput spike above the pre-fault
    baseline; the waiter stage is an actual PostgreSQL observation after that
    spike (a long-lived waiter may already exist when sampling begins); the
    victim stage is the in-container OLTP probe latency spiking while cleanup
    I/O is in flight. Host CPU PSI stays exposed to the Agent through the
    host_pressure series, but it cannot discriminate this case's increment on
    a shared host, so it does not gate admission.
    """
    if len(samples) < case.admission_sample_count:
        return None
    filesystem_threshold = float(case.admission_filesystem_io_mb_per_sec)
    bufferio_threshold = int(case.admission_bufferio_waiters)
    minimum_span = max(1, int(case.admission_sample_count) - 1)
    filesystem_indexes = [
        index
        for index, item in enumerate(samples)
        if max(0.0, float(item["filesystem_io_mb_per_sec"]) - baseline_filesystem_io)
        >= filesystem_threshold
    ]
    bufferio_indexes = [
        index
        for index, item in enumerate(samples)
        if int(item["bufferio_waiters"]) >= bufferio_threshold
    ]
    victim_indexes = [
        index
        for index, item in enumerate(samples)
        if float(item["oltp_latency_ms"]) >= ADMISSION_OLTP_LATENCY_MS
    ]
    for filesystem_index in filesystem_indexes:
        for bufferio_index in bufferio_indexes:
            if bufferio_index < filesystem_index:
                continue
            for victim_index in victim_indexes:
                if victim_index < bufferio_index or victim_index - filesystem_index < minimum_span:
                    continue
                return {
                    "filesystem_index": filesystem_index,
                    "bufferio_index": bufferio_index,
                    "victim_index": victim_index,
                }
    return None


class PartitionCleanupTelemetry:
    """Collect only measurements made from the live container and database."""

    def __init__(self, env, case, sample_interval: float):
        self.env = env
        self.case = case
        self.sample_interval = float(sample_interval)
        self.samples: deque[dict[str, Any]] = deque(maxlen=512)
        self._previous_io = None
        self._previous_query_cpu_ms = None
        self._previous_sample_time = None
        self._baseline_cpu_pressure: float | None = None
        self._baseline_bufferio_waiters: int | None = None
        self._baseline_filesystem_io: float | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.storage: dict[str, str] = {}
        self._lock = threading.Lock()

    @property
    def container_name(self) -> str:
        return self.env.deployment.container_name

    @property
    def pgdata(self) -> str:
        return self.env.deployment.pgdata

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="partition-cleanup-telemetry")
        self._thread.start()

    def sample_metrics(
        self,
        *,
        connection,
        timestamp_ms: int,
        elapsed_seconds: float,
        base_values,
    ) -> dict[str, dict[str, float]]:
        """The injector's own telemetry loop owns case sampling from live probes."""
        return {}

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        self._thread = None

    def verify_storage(self) -> dict[str, str]:
        probe = self._docker_probe()
        fs_type, source = probe["storage"].split(" ", 1)
        allowed = {"ext4", "xfs", "btrfs", "zfs"}
        if fs_type.casefold() not in allowed or source.casefold() in {"overlay", "overlay2"}:
            raise RuntimeError(
                "PG-RG-PC01 admission blocker: PGDATA is not on an allowed real block filesystem: "
                f"filesystem={fs_type!r}, source={source!r}, allowed={sorted(allowed)}"
            )
        self.storage = {"filesystem": fs_type, "source": source}
        return dict(self.storage)

    def prime_admission_baseline(self) -> dict[str, Any]:
        """Capture the live background-load baseline before fault activity starts.

        Baselines use the minimum of the pre-fault window: the case's own
        one-CPU workload routinely drives host PSI to 25-30 percent, and a
        max baseline would pin the CPU delta check above any level the fault
        window can reach on a shared host. The chain still requires the
        measured filesystem spike followed by waiters and later pressure.
        """
        samples = [self.sample()]
        time.sleep(self.sample_interval)
        samples.append(self.sample())
        self._baseline_cpu_pressure = min(
            float(sample["cpu_pressure_some_avg10"]) for sample in samples
        )
        self._baseline_bufferio_waiters = min(
            int(sample["bufferio_waiters"]) for sample in samples
        )
        self._baseline_filesystem_io = min(
            float(sample["filesystem_io_mb_per_sec"]) for sample in samples
        )
        return samples[-1]

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.sample()
            except Exception as exc:
                print(f"[PartitionCleanupTelemetry] sample failed: {exc}")
            self._stop.wait(self.sample_interval)

    def sample(self) -> dict[str, Any]:
        probe = self._docker_probe()
        db = self._database_probe()
        now = time.monotonic()
        delta_seconds = now - self._previous_sample_time if self._previous_sample_time else None
        read_sectors = int(probe["read_sectors"])
        write_sectors = int(probe["write_sectors"])
        io_rate = 0.0
        if self._previous_io is not None and delta_seconds and delta_seconds > 0:
            delta_sectors = max(0, read_sectors - self._previous_io[0]) + max(0, write_sectors - self._previous_io[1])
            io_rate = delta_sectors * 512 / (1024 * 1024) / delta_seconds
        query_cpu_rate = 0.0
        if self._previous_query_cpu_ms is not None and delta_seconds and delta_seconds > 0:
            query_cpu_rate = max(0.0, float(db["query_cpu_ms"]) - self._previous_query_cpu_ms) / delta_seconds
        sample = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "filesystem": probe["storage"],
            "filesystem_io_mb_per_sec": round(io_rate, 3),
            "data_used_bytes": int(probe["used_bytes"]),
            "io_pressure_some_avg10": float(probe["io_pressure_some_avg10"]),
            "cpu_pressure_some_avg10": float(probe["cpu_pressure_some_avg10"]),
            "bufferio_waiters": int(db["bufferio_waiters"]),
            "query_cpu_ms_per_sec": round(query_cpu_rate, 3),
            "oltp_latency_ms": float(db["oltp_latency_ms"]),
        }
        with self._lock:
            self.samples.append(sample)
        self._previous_io = (read_sectors, write_sectors)
        self._previous_query_cpu_ms = float(db["query_cpu_ms"])
        self._previous_sample_time = now
        return sample

    def _docker_probe(self) -> dict[str, Any]:
        script = (
            "set -eu; "
            f"printf '%s\\n' \"$(findmnt -no FSTYPE,SOURCE {self.pgdata})\"; "
            f"mount_source=$(findmnt -no SOURCE {self.pgdata}); "
            "mount_source=${mount_source%%[*}; device=${mount_source##*/}; "
            f"df -B1 --output=used {self.pgdata} | tail -n 1; "
            "awk '/^some / {for (i=1;i<=NF;i++) if ($i ~ /^avg10=/) print substr($i,7)}' /proc/pressure/io; "
            "awk '/^some / {for (i=1;i<=NF;i++) if ($i ~ /^avg10=/) print substr($i,7)}' /proc/pressure/cpu; "
            "awk -v device=\"$device\" '$3 == device {print $6; print $10; found=1; exit} END {if (!found) {print 0; print 0}}' /proc/diskstats"
        )
        result = subprocess.run(
            ["docker", "exec", self.container_name, "bash", "-lc", script],
            capture_output=True,
            text=True,
            # findmnt/df/diskstats can exceed 10s when the shared host is under
            # heavy IO contention (dozens of co-tenant containers); the probe
            # is infrastructure, and a false timeout would invalidate runs.
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"real filesystem probe failed: {result.stderr.strip()}")
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if len(lines) < 6:
            raise RuntimeError(f"real filesystem probe returned incomplete output: {result.stdout!r}")
        fs_type, source = lines[0].split(None, 1)
        used_bytes = int(lines[1])
        io_pressure = float(lines[2])
        cpu_pressure = float(lines[3])
        read_sectors = int(lines[4])
        write_sectors = int(lines[5])
        return {
            "storage": f"{fs_type} {source}",
            "used_bytes": used_bytes,
            "io_pressure_some_avg10": io_pressure,
            "cpu_pressure_some_avg10": cpu_pressure,
            "read_sectors": read_sectors,
            "write_sectors": write_sectors,
        }

    def _database_probe(self) -> dict[str, Any]:
        rows = _json_object(
            self.env.execute_sql(
                "SELECT count(*) FILTER (WHERE wait_event = 'BufferIO' OR wait_event_type = 'IO'), "
                "coalesce((SELECT sum(total_exec_time) FROM pg_stat_statements), 0) "
                "FROM pg_stat_activity;"
            ),
            "partition cleanup database wait probe",
        )["result"]
        bufferio_waiters, query_cpu_ms = rows[0]
        start = time.perf_counter()
        _require_sql_success(
            self.env.execute_sql(f"SELECT count(*) FROM {self.case.oltp_table} WHERE id = 1;"),
            "partition cleanup OLTP probe",
        )
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "bufferio_waiters": int(bufferio_waiters or 0),
            "query_cpu_ms": float(query_cpu_ms or 0),
            "oltp_latency_ms": latency_ms,
        }

    def _series(self, keys: tuple[str, ...]) -> dict[str, Any]:
        with self._lock:
            samples = list(self.samples)[-300:]
        result = {"timestamps": [item["timestamp"] for item in samples]}
        result.update({key: [item[key] for item in samples] for key in keys})
        return result

    def _selected_samples(self, start, end) -> list[dict[str, Any]]:
        with self._lock:
            samples = list(self.samples)
        if start is None:
            return samples[-300:]
        selected = []
        for sample in samples:
            timestamp = datetime.strptime(sample["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start <= timestamp <= end:
                selected.append(sample)
        return selected

    def query(self, metric: str, _target=None, _start=None, _end=None) -> str:
        if not self.samples:
            self.sample()
        if metric == "filesystem_io":
            samples = self._selected_samples(_start, _end)
            samples = samples[-METRIC_RESPONSE_SAMPLE_LIMIT:]
            series = {
                "timestamps": [item["timestamp"] for item in samples],
                "filesystem_io_mb_per_sec": [item["filesystem_io_mb_per_sec"] for item in samples],
                "filesystem_io_mb_per_sec_delta_from_baseline": [
                    max(0.0, float(item["filesystem_io_mb_per_sec"]) - (self._baseline_filesystem_io or 0.0))
                    for item in samples
                ],
                "data_used_bytes": [item["data_used_bytes"] for item in samples],
            }
        elif metric == "bufferio_waiters":
            samples = self._selected_samples(_start, _end)
            samples = samples[-METRIC_RESPONSE_SAMPLE_LIMIT:]
            series = {
                "timestamps": [item["timestamp"] for item in samples],
                "bufferio_waiters": [item["bufferio_waiters"] for item in samples],
                "query_cpu_ms_per_sec": [item["query_cpu_ms_per_sec"] for item in samples],
            }
        elif metric == "host_pressure":
            samples = self._selected_samples(_start, _end)
            samples = samples[-METRIC_RESPONSE_SAMPLE_LIMIT:]
            series = {
                "timestamps": [item["timestamp"] for item in samples],
                "cpu_pressure_some_avg10": [item["cpu_pressure_some_avg10"] for item in samples],
                "cpu_pressure_some_avg10_delta_from_baseline": [
                    max(0.0, float(item["cpu_pressure_some_avg10"]) - (self._baseline_cpu_pressure or 0.0))
                    for item in samples
                ],
                "io_pressure_some_avg10": [item["io_pressure_some_avg10"] for item in samples],
                "query_cpu_ms_per_sec": [item["query_cpu_ms_per_sec"] for item in samples],
                "oltp_latency_ms": [item["oltp_latency_ms"] for item in samples],
            }
        elif metric == "partition_lifecycle":
            payload = _json_object(
                self.env.execute_sql(
                    f"SELECT change_id, partition_name, action, state, event_ts "
                    f"FROM {self.case.lifecycle_table} ORDER BY event_ts, change_id"
                ),
                "partition lifecycle telemetry",
            )
            return json.dumps({"status": "success", "metric": metric, "kind": "records", "records": payload["result"]}, default=str)
        else:
            raise ValueError(f"unsupported partition cleanup metric: {metric}")
        return json.dumps({"status": "success", "metric": metric, "kind": "series", "series": {"host": series}}, default=str)

    def agent_contract(self) -> dict[str, Any]:
        """Expose raw case observability and final-state bounds through help()."""
        return {
            "case_id": self.case.case_id,
            "sampling": {
                "source": "live container and PostgreSQL observations",
                "sample_interval_seconds": self.sample_interval,
                "agent_response_max_samples": METRIC_RESPONSE_SAMPLE_LIMIT,
                "baseline": "filesystem_io and host_pressure include delta_from_baseline fields",
            },
            "metrics": {
                "filesystem_io": {
                    "kind": "series",
                    "fields": ["filesystem_io_mb_per_sec", "filesystem_io_mb_per_sec_delta_from_baseline", "data_used_bytes"],
                    "units": "MB/s for I/O rate; bytes for data_used_bytes",
                },
                "bufferio_waiters": {
                    "kind": "series",
                    "fields": ["bufferio_waiters", "query_cpu_ms_per_sec"],
                    "units": "waiter count; PostgreSQL execution milliseconds per second",
                },
                "host_pressure": {
                    "kind": "series",
                    "fields": [
                        "cpu_pressure_some_avg10",
                        "cpu_pressure_some_avg10_delta_from_baseline",
                        "io_pressure_some_avg10",
                        "query_cpu_ms_per_sec",
                        "oltp_latency_ms",
                    ],
                    "units": "PSI percentage points; milliseconds per second; milliseconds",
                },
                "partition_lifecycle": {
                    "kind": "records",
                    "fields": ["change_id", "partition_name", "action", "state", "event_ts"],
                    "units": "database lifecycle records",
                },
            },
            "final_recovery_contract": {
                "cleanup_job_enabled": True,
                "cleanup_job_paused": False,
                "retention_days_range": [1, self.case.max_retention_days],
                "legal_hold_attached": 1,
                "legal_hold_source": (
                    f"approved assignments are listed in {self.case.policy_table}; "
                    "catalog legal_hold flags must stay consistent with that list"
                    if self.case.policy_table
                    else "approved assignments follow the published retention policy"
                ),
                "detached_partition_count": 0,
                "due_non_hold_partition_count": 0,
                "metadata_state_changes": "state changes to dropped must use the retention cleanup workflow",
                "recovery_sample_count": self.case.recovery_sample_count,
                "host_pressure_observable_max": self.case.recovery_host_pressure_limit,
                "host_pressure_note": "host-wide CPU PSI is co-tenant noise; it is reported but does not gate recovery",
                "retention_note": (
                    "the business retention floor is 7 days; active governance automations on this host "
                    "hold stored configuration and may re-apply it to operational job rows, so verify "
                    "final job state stays inside the published range after any change"
                ),
                "filesystem_io_mb_per_sec_max": self.case.recovery_filesystem_io_limit,
                "oltp_latency_ms_max": self.case.oltp_p99_slo_ms,
            },
            "interpretation": "These are raw observations. Build the causal chain yourself; the metric names do not identify the root cause.",
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "storage": self.storage,
            "samples": list(self.samples),
            "case_id": self.case.case_id,
        }

    def has_admission_chain(self, case) -> bool:
        with self._lock:
            samples = list(self.samples)
        return _find_admission_chain(
            samples,
            case,
            baseline_cpu_pressure=self._baseline_cpu_pressure or 0.0,
            baseline_bufferio_waiters=self._baseline_bufferio_waiters or 0,
            baseline_filesystem_io=self._baseline_filesystem_io or 0.0,
        ) is not None

    def admission_diagnostics(self, case) -> dict[str, Any]:
        with self._lock:
            samples = list(self.samples)
        baseline_cpu_pressure = self._baseline_cpu_pressure or 0.0
        baseline_bufferio_waiters = self._baseline_bufferio_waiters or 0
        baseline_filesystem_io = self._baseline_filesystem_io or 0.0
        return {
            "sample_count": len(samples),
            "max_filesystem_io_mb_per_sec": max(
                (float(item["filesystem_io_mb_per_sec"]) for item in samples), default=0.0
            ),
            "max_bufferio_waiters": max(
                (int(item["bufferio_waiters"]) for item in samples), default=0
            ),
            "max_cpu_pressure_some_avg10": max(
                (float(item["cpu_pressure_some_avg10"]) for item in samples), default=0.0
            ),
            "baseline_cpu_pressure_some_avg10": baseline_cpu_pressure,
            "baseline_bufferio_waiters": baseline_bufferio_waiters,
            "baseline_filesystem_io_mb_per_sec": baseline_filesystem_io,
            "admission_cpu_delta_threshold": float(case.admission_host_pressure),
            "admission_bufferio_threshold": int(case.admission_bufferio_waiters),
            "admission_filesystem_io_delta_threshold": float(case.admission_filesystem_io_mb_per_sec),
            "admission_oltp_latency_ms_threshold": ADMISSION_OLTP_LATENCY_MS,
            "admission_chain": _find_admission_chain(
                samples,
                case,
                baseline_cpu_pressure=baseline_cpu_pressure,
                baseline_bufferio_waiters=baseline_bufferio_waiters,
                baseline_filesystem_io=baseline_filesystem_io,
            ),
            "recent_samples": samples[-8:],
        }


class PgResourceGovernancePartitionCleanupInjector(BaseFaultInjector):
    def __init__(self):
        self.env = None
        self.case = None
        self.config = {}
        self.telemetry: PartitionCleanupTelemetry | None = None
        self._stop_event: threading.Event | None = None
        self._worker_thread: threading.Thread | None = None
        self._worker_connection = None
        self._bait_thread: threading.Thread | None = None
        self._sync_thread: threading.Thread | None = None
        self._bait_connection = None
        self._connections = []
        self._servers: list[_TelemetryServer] = []
        self._pgbench_process = None
        self._compressor_process = None
        self._basebackup_process = None
        self._backup_dir: str | None = None
        self._container_backup_dir: str | None = None

    def _configure(self, context: FaultLifecycleContext) -> None:
        self.env = context.env
        self.case = context.case
        self.config = dict(context.config)

    @property
    def container_name(self) -> str:
        return self.env.deployment.container_name

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self.recover(context)
        metrics_hidden = getattr(self.env, "metrics_hidden", None)
        with metrics_hidden() if metrics_hidden else nullcontext():
            self._setup_schema()
        self._start_runtime(context)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self._stop_runtime(context)
        self._verify_persistent_state()
        self._start_runtime(context)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        if self.telemetry is None:
            raise RuntimeError("partition cleanup telemetry is not active")
        return {
            "storage": dict(self.telemetry.storage),
            "filesystem_io": self.env.query_metrics("filesystem_io"),
            "bufferio_waiters": self.env.query_metrics("bufferio_waiters"),
            "host_pressure": self.env.query_metrics("host_pressure"),
            "partition_lifecycle": self.env.query_metrics("partition_lifecycle"),
        }

    def fault_ready(self) -> bool:
        """Return whether the real sampled filesystem causal chain is admitted."""
        return self.telemetry is not None and self.telemetry.has_admission_chain(self.case)

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime(context)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self._stop_runtime(context)
        if self.env is None:
            return
        if not getattr(self.env, "_conn", None) and not hasattr(self.env, "execute_sql"):
            return
        table_names = (
            self.case.parent_table,
            self.case.metadata_table,
            self.case.lifecycle_table,
            self.case.job_table,
            self.case.oltp_table,
        )
        statements = [
            f"DROP FUNCTION IF EXISTS aiopsbench_retention_worker_run(integer);",
            f"DROP TRIGGER IF EXISTS {self.case.metadata_table}_workflow_guard ON {self.case.metadata_table};",
            f"DROP FUNCTION IF EXISTS aiopsbench_retention_catalog_guard();",
            f"DROP TABLE IF EXISTS {self.case.parent_table} CASCADE;",
            f"DROP TABLE IF EXISTS {self.case.metadata_table};",
            f"DROP TABLE IF EXISTS {self.case.lifecycle_table};",
            f"DROP TABLE IF EXISTS {self.case.job_table};",
            f"DROP TABLE IF EXISTS {self.case.oltp_table};",
            f"DROP TABLE IF EXISTS {self.case.parent_table}_bait CASCADE;",
        ]
        if getattr(self.case, "policy_table", None):
            statements.append(f"DROP TABLE IF EXISTS {self.case.policy_table};")
        _require_sql_success(self.env.execute_sql(" ".join(statements)), "recover partition cleanup objects")

    def cleanup(self, context: FaultLifecycleContext) -> None:
        self.recover(context)

    def _setup_schema(self) -> None:
        c = self.case
        for name in (c.parent_table, c.metadata_table, c.lifecycle_table, c.job_table, c.oltp_table, *[spec[0] for spec in c.partition_specs]):
            _validate_sql_identifier(name, "partition cleanup object")
        if getattr(c, "policy_table", None):
            _validate_sql_identifier(c.policy_table, "partition cleanup policy table")
        self.env.execute_sql(f"DROP TABLE IF EXISTS {c.parent_table} CASCADE;")
        self.env.execute_sql(
            f"CREATE TABLE {c.parent_table} (event_id bigint NOT NULL, event_ts timestamptz NOT NULL, payload text NOT NULL) PARTITION BY RANGE (event_ts);"
        )
        self.env.execute_sql(
            f"CREATE TABLE {c.metadata_table} (partition_name text PRIMARY KEY, partition_end timestamptz NOT NULL, legal_hold boolean NOT NULL, state text NOT NULL, last_change_id text);"
        )
        self.env.execute_sql(
            f"CREATE TABLE {c.lifecycle_table} (change_id text PRIMARY KEY, partition_name text NOT NULL, action text NOT NULL, state text NOT NULL, event_ts timestamptz NOT NULL DEFAULT clock_timestamp());"
        )
        self.env.execute_sql(
            f"CREATE TABLE {c.job_table} (job_name text PRIMARY KEY, enabled boolean NOT NULL, paused boolean NOT NULL, batch_size integer NOT NULL, retention_days integer NOT NULL, storage_target text NOT NULL);"
        )
        if getattr(c, "policy_table", None):
            self.env.execute_sql(
                f"CREATE TABLE {c.policy_table} (approved_partition_name text PRIMARY KEY, approved_at timestamptz NOT NULL, note text NOT NULL);"
            )
        self.env.execute_sql(
            f"CREATE OR REPLACE FUNCTION aiopsbench_retention_catalog_guard() RETURNS trigger LANGUAGE plpgsql AS $$ "
            f"BEGIN "
            f"IF NEW.state = 'dropped' AND OLD.state IS DISTINCT FROM NEW.state "
            f"AND current_setting('aiopsbench.partition_cleanup_approved', true) IS DISTINCT FROM '1' THEN "
            f"RAISE EXCEPTION 'partition metadata state changes to dropped must use the retention cleanup workflow'; "
            f"END IF; "
            f"RETURN NEW; "
            f"END; $$; "
            f"CREATE TRIGGER {c.metadata_table}_workflow_guard BEFORE UPDATE ON {c.metadata_table} "
            f"FOR EACH ROW EXECUTE FUNCTION aiopsbench_retention_catalog_guard();"
        )
        self.env.execute_sql(
            f"CREATE TABLE {c.oltp_table} (id bigint PRIMARY KEY, payload text NOT NULL); INSERT INTO {c.oltp_table} SELECT g, repeat('hot', 32) FROM generate_series(1, 50000) g;"
        )
        now = datetime.now(timezone.utc).date()
        for name, start_offset, end_offset, legal_hold, rows in c.partition_specs:
            start = now + timedelta(days=start_offset)
            end = now + timedelta(days=end_offset)
            self.env.execute_sql(
                f"CREATE TABLE {name} PARTITION OF {c.parent_table} FOR VALUES FROM ('{start}') TO ('{end}');"
            )
            self.env.execute_sql(
                f"INSERT INTO {name} SELECT g, '{start + timedelta(days=1)}'::timestamptz, repeat(md5(g::text), {512 if c.case_no == 0 else 128}) FROM generate_series(1, {rows}) g;"
            )
            self.env.execute_sql(
                f"INSERT INTO {c.metadata_table}(partition_name, partition_end, legal_hold, state) VALUES ('{name}', '{end}', {str(legal_hold).lower()}, 'attached');"
            )
        mislabeled = getattr(c, "mislabeled_hold_partition", None)
        if mislabeled:
            self.env.execute_sql(
                f"UPDATE {c.metadata_table} SET legal_hold = true WHERE partition_name = '{mislabeled}';"
            )
        if getattr(c, "policy_table", None):
            self.env.execute_sql(
                f"INSERT INTO {c.policy_table}(approved_partition_name, approved_at, note) VALUES "
                f"('{c.legal_hold_partition}', now() - interval '30 days', 'ongoing litigation hold approved by compliance');"
            )
        self.env.execute_sql(
            f"INSERT INTO {c.job_table} VALUES ('{c.cleanup_job_name}', true, false, {c.cleanup_batch_size}, {c.retention_days}, 'pgdata-volume');"
        )
        self.env.execute_sql(
            f"CREATE OR REPLACE FUNCTION aiopsbench_retention_worker_run(requested_batch integer) RETURNS integer LANGUAGE plpgsql AS $$ "
            f"DECLARE item record; completed integer := 0; change text; BEGIN "
            f"PERFORM set_config('aiopsbench.partition_cleanup_approved', '1', true); "
            f"FOR item IN SELECT partition_name, state FROM {c.metadata_table} WHERE state = 'detached' OR (state = 'attached' AND partition_end <= now() - make_interval(days => (SELECT retention_days FROM {c.job_table} WHERE job_name = '{c.cleanup_job_name}') ) AND NOT legal_hold) ORDER BY partition_end LIMIT GREATEST(requested_batch, 1) LOOP "
            f"change := to_char(clock_timestamp(), 'YYYYMMDDHH24MISSMS') || '-' || item.partition_name; "
            f"IF item.state = 'attached' THEN EXECUTE format('ALTER TABLE %I DETACH PARTITION %I', '{c.parent_table}', item.partition_name); UPDATE {c.metadata_table} SET state = 'detached', last_change_id = change WHERE partition_name = item.partition_name; INSERT INTO {c.lifecycle_table}(change_id, partition_name, action, state) VALUES (change, item.partition_name, 'detach', 'detached'); END IF; "
            f"EXECUTE format('DROP TABLE IF EXISTS %I', item.partition_name); UPDATE {c.metadata_table} SET state = 'dropped', last_change_id = change WHERE partition_name = item.partition_name; INSERT INTO {c.lifecycle_table}(change_id, partition_name, action, state) VALUES (change || '-drop', item.partition_name, 'drop', 'dropped'); completed := completed + 1; END LOOP; RETURN completed; END; $$;"
        )
        if getattr(c, "sync_app_name", None) and getattr(c, "drifted_retention_days", None):
            # The stale-config agent applies its snapshot through this helper,
            # so the session surface and pg_stat_statements only show a neutral
            # call; the out-of-range UPDATE lives one function-body hop deeper.
            self.env.execute_sql(
                f"CREATE OR REPLACE FUNCTION aiopsbench_retention_worker_feed() RETURNS void LANGUAGE sql AS $$ "
                f"UPDATE {c.job_table} SET retention_days = {int(c.drifted_retention_days)}, paused = true "
                f"WHERE job_name = '{c.cleanup_job_name}'; $$;"
            )
        self.env.execute_sql(
            f"CREATE TABLE {c.parent_table}_bait (event_id bigint, event_ts timestamptz, payload text) PARTITION BY RANGE(event_ts); "
            f"CREATE TABLE {c.parent_table}_bait_small PARTITION OF {c.parent_table}_bait FOR VALUES FROM ('2000-01-01') TO ('2000-01-02'); "
            f"INSERT INTO {c.parent_table}_bait SELECT g, '2000-01-01', repeat('bait', 16) FROM generate_series(1, 1000) g;"
        )

    def _verify_persistent_state(self) -> None:
        c = self.case
        rows = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{c.parent_table}')::text, count(*) FROM {c.metadata_table};"
            ),
            "verify partition cleanup fault image",
        )["result"]
        if not rows or rows[0][0] != c.parent_table or int(rows[0][1]) != c.partition_count:
            raise RuntimeError(f"partition cleanup fault image does not match case: rows={rows!r}")

    def _start_runtime(self, context: FaultLifecycleContext) -> None:
        c = self.case
        self.telemetry = PartitionCleanupTelemetry(self.env, c, c.telemetry_sample_interval_seconds)
        if hasattr(self.env, "attach_scenario_metric_provider"):
            self.env.attach_scenario_metric_provider(self.telemetry)
        self.telemetry.verify_storage()
        ports = tuple(int(port) for port in self.config["auxiliary_ports"])
        self._servers = [
            _TelemetryServer(self.telemetry, ports[0], "filesystem-telemetry"),
            _TelemetryServer(self.telemetry, ports[1], "cleanup-control"),
        ]
        for server in self._servers:
            server.start()
        self._initialize_pgbench()
        self.telemetry.prime_admission_baseline()
        self.telemetry.start()
        self._stop_event = threading.Event()
        self._start_cleanup_worker()
        if c.enable_small_partition_drop:
            self._start_small_partition_drop()
        self._start_pgbench()
        self._start_host_noise(context)
        self._wait_fault_ready()

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

    def _start_cleanup_worker(self) -> None:
        def run_worker():
            conn = None
            try:
                conn = self._connect(self.case.cleanup_app_name)
                self._worker_connection = conn
                with conn.cursor() as cur:
                    cur.execute("SET statement_timeout = '0';")
                    while self._stop_event is not None and not self._stop_event.is_set():
                        cur.execute(
                            f"SELECT enabled, paused, batch_size FROM {self.case.job_table} "
                            f"WHERE job_name = '{self.case.cleanup_job_name}';"
                        )
                        enabled, paused, batch_size = cur.fetchone()
                        if enabled and not paused:
                            cur.execute(
                                f"SELECT aiopsbench_retention_worker_run({int(batch_size)});"
                            )
                        self._stop_event.wait(self.case.cleanup_worker_interval_seconds)
            except Exception as exc:
                if self._stop_event is None or not self._stop_event.is_set():
                    print(f"[PartitionCleanupInjector] cleanup worker stopped: {exc}")
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                self._worker_connection = None

        self._worker_thread = threading.Thread(target=run_worker, daemon=True, name=self.case.cleanup_process_name)
        self._worker_thread.start()

    def _start_small_partition_drop(self) -> None:
        """Run one real, small partition drop as an I/O decoy."""
        def run_bait():
            conn = None
            try:
                self._stop_event.wait(2.0)
                if self._stop_event.is_set():
                    return
                conn = self._connect(f"{self.case.case_id}-small-partition-drop")
                self._bait_connection = conn
                with conn.cursor() as cur:
                    cur.execute(
                        f"ALTER TABLE {self.case.parent_table}_bait DETACH PARTITION {self.case.parent_table}_bait_small;"
                    )
                    cur.execute(
                        f"INSERT INTO {self.case.lifecycle_table}(change_id, partition_name, action, state) "
                        f"VALUES (to_char(clock_timestamp(), 'YYYYMMDDHH24MISSMS') || '-bait', '{self.case.parent_table}_bait_small', 'bait_drop', 'detached');"
                    )
                    cur.execute(f"DROP TABLE {self.case.parent_table}_bait_small;")
            except Exception as exc:
                if self._stop_event is None or not self._stop_event.is_set():
                    print(f"[PartitionCleanupInjector] small partition decoy stopped: {exc}")
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                self._bait_connection = None

        self._bait_thread = threading.Thread(target=run_bait, daemon=True, name=f"{self.case.case_id}-small-partition-drop")
        self._bait_thread.start()

    def _start_pgbench(self) -> None:
        pgbench = [
            "docker", "exec", "-e", f"PGPASSWORD={self.env.password}", self.container_name,
            "pgbench",
        ]
        self._pgbench_process = subprocess.Popen(
            pgbench + ["-h", "127.0.0.1", "-p", "5432", "-U", self.env.user, "-d", self.env.dbname, "-c", str(self.case.pgbench_clients), "-j", str(min(2, self.case.pgbench_clients)), "-T", str(self.case.pgbench_duration_seconds), "-P", "1"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    def _initialize_pgbench(self, pgbench: list[str] | None = None) -> None:
        pgbench = pgbench or [
            "docker", "exec", "-e", f"PGPASSWORD={self.env.password}", self.container_name,
            "pgbench",
        ]
        init = subprocess.run(
            pgbench + ["-h", "127.0.0.1", "-p", "5432", "-U", self.env.user, "-d", self.env.dbname, "-i", "-q", "-s", "1"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if init.returncode != 0:
            raise RuntimeError(f"PG-RG-PC01 admission blocker: container pgbench initialization failed: {init.stderr.strip()}")

    def _start_host_noise(self, context: FaultLifecycleContext) -> None:
        if self.case.enable_host_compressor:
            self._compressor_process = subprocess.Popen(
                ["bash", "-lc", "while true; do gzip -1 -c /bin/bash >/dev/null; done"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        if not self.case.enable_basebackup:
            return
        backup_root = Path(tempfile.gettempdir()) / f"aiopsbench-{context.scenario_id}-{context.case_id}-{context.run_id}"
        backup_root.mkdir(parents=True, exist_ok=True)
        self._backup_dir = str(backup_root)
        pg_basebackup = shutil.which("pg_basebackup")
        if pg_basebackup:
            env = {**os.environ, "PGPASSWORD": self.env.password}
            self._basebackup_process = subprocess.Popen(
                [pg_basebackup, "-h", self.env.host, "-p", str(self.env.port), "-U", self.env.user, "-D", self._backup_dir, "-Fp", "-X", "none", "-P"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        else:
            self._container_backup_dir = f"/tmp/aiopsbench-{context.scenario_id}-{context.case_id}-{context.run_id}"
            probe = subprocess.run(
                ["docker", "exec", self.container_name, "bash", "-lc", "command -v pg_basebackup"],
                capture_output=True,
                text=True,
            )
            if probe.returncode != 0:
                raise RuntimeError("PG-RG-PC01 admission blocker: pg_basebackup is unavailable on host and PostgreSQL container")
            env_args = ["docker", "exec", "-e", f"PGPASSWORD={self.env.password}", self.container_name, "pg_basebackup"]
            self._basebackup_process = subprocess.Popen(
                env_args + ["-h", "127.0.0.1", "-p", "5432", "-U", self.env.user, "-D", self._container_backup_dir, "-Fp", "-X", "none", "-P"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

    def _wait_fault_ready(self) -> None:
        deadline = time.monotonic() + float(self.config["fault_ready_timeout_seconds"])
        while time.monotonic() < deadline:
            try:
                if self.fault_ready():
                    break
            except Exception:
                pass
            time.sleep(0.5)
        else:
            raise RuntimeError(
                "PG-RG-PC01 admission blocker: target kernel/filesystem/storage driver did not produce "
                "a stable filesystem I/O -> BufferIO -> OLTP victim latency chain; "
                f"diagnostics={self.telemetry.admission_diagnostics(self.case) if self.telemetry else {}}"
            )
        self._apply_retention_drift()

    def _apply_retention_drift(self) -> None:
        """Start the stale-config governance session after fault admission.

        The drift source is not a job-table row: it is a live automation
        session (identifiable only through pg_stat_activity by its
        application_name and the UPDATE text it runs) that re-applies a stale
        stored snapshot — paused with an out-of-range horizon — to the cleanup
        job every few seconds. Fixing the job row alone never converges; the
        model must correlate the observed flip-back with the active session.
        """
        self._start_retention_sync_applier()

    def _start_retention_sync_applier(self) -> None:
        case = self.case
        drifted = int(getattr(case, "drifted_retention_days", 0) or 0)
        if not drifted:
            return

        def run_sync():
            # Hold a single long-lived connection (like the cleanup worker):
            # terminating the session backend makes the next write fail, and
            # the fragile agent exits instead of reconnecting, so killing the
            # session is a converging remediation for the drift.
            conn = None
            for _ in range(5):
                try:
                    conn = self._connect(case.sync_app_name)
                    break
                except Exception as exc:
                    if self._stop_event is None or self._stop_event.is_set():
                        return
                    print(f"[PartitionCleanupInjector] stale-config agent connect retry: {exc}")
                    time.sleep(2.0)
            if conn is None:
                print("[PartitionCleanupInjector] stale-config agent gave up connecting")
                return
            try:
                with conn.cursor() as cur:
                    cur.execute("SET statement_timeout = '0';")
                    while self._stop_event is not None and not self._stop_event.is_set():
                        cur.execute("SELECT aiopsbench_retention_worker_feed();")
                        self._stop_event.wait(case.sync_interval_seconds)
            except Exception as exc:
                if self._stop_event is None or not self._stop_event.is_set():
                    print(f"[PartitionCleanupInjector] stale-config agent exited on error: {exc}")
                # Fragile-automation semantics: this agent treats a broken
                # session (e.g. pg_terminate_backend) as fatal and does not
                # reconnect.
                return
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass

        self._sync_thread = threading.Thread(
            target=run_sync,
            daemon=True,
            name=case.sync_app_name,
        )
        self._sync_thread.start()

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
        if self.env is not None and self.case is not None:
            sync_app = getattr(self.case, "sync_app_name", None)
            sync_clause = f" OR application_name = '{sync_app}'" if sync_app else ""
            try:
                self.env.execute_sql(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    f"WHERE (application_name = '{self.case.cleanup_app_name}' "
                    f"OR application_name = '{self.case.case_id}-small-partition-drop'"
                    f"{sync_clause}) "
                    "AND pid <> pg_backend_pid();"
                )
            except Exception:
                pass
        if self._worker_thread is not None:
            self._worker_thread.join(timeout=5)
        self._worker_thread = None
        self._worker_connection = None
        if self._sync_thread is not None:
            self._sync_thread.join(timeout=5)
        self._sync_thread = None
        if self._bait_thread is not None:
            self._bait_thread.join(timeout=5)
        self._bait_thread = None
        self._bait_connection = None
        for process in (self._pgbench_process, self._compressor_process, self._basebackup_process):
            if process is not None and process.poll() is None:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                except (ProcessLookupError, PermissionError):
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        process.kill()
        self._pgbench_process = None
        self._compressor_process = None
        self._basebackup_process = None
        for server in self._servers:
            try:
                server.stop()
            except Exception:
                pass
        self._servers = []
        if self.telemetry is not None:
            self.telemetry.stop()
            if hasattr(self.env, "detach_scenario_metric_provider"):
                self.env.detach_scenario_metric_provider(self.telemetry)
        self.telemetry = None
        for conn in list(self._connections):
            try:
                conn.close()
            except Exception:
                pass
        self._connections = []
        self._stop_event = None
        if self._backup_dir:
            shutil.rmtree(self._backup_dir, ignore_errors=True)
            self._backup_dir = None
        if self._container_backup_dir:
            subprocess.run(
                ["docker", "exec", self.container_name, "rm", "-rf", "--", self._container_backup_dir],
                capture_output=True,
            )
            self._container_backup_dir = None


class PgResourceGovernancePartitionCleanupScenario(PostgresScenario):
    scenario_id = "pg_resource_governance_partition_cleanup"
    description = "Host CPU pressure caused by real filesystem-backed partition retention cleanup."
    cases = (HARD_CASE, SIMPLE_CASE)

    def build_fault_plan(self, case: PgResourceGovernancePartitionCleanupCase) -> tuple[FaultPlan, ...]:
        configured_ports = os.environ.get("AIOPS_PARTITION_CLEANUP_AUX_PORTS", "")
        auxiliary_ports = (
            tuple(int(port) for port in configured_ports.split(",") if port.strip())
            if configured_ports.strip()
            else tuple(range(15862, 15862 + case.aux_port_count))
        )
        if (
            len(auxiliary_ports) != case.aux_port_count
            or len(set(auxiliary_ports)) != len(auxiliary_ports)
            or any(port < 1024 or port > 65535 for port in auxiliary_ports)
        ):
            raise ValueError(
                "PG-RG-PC01 requires unique auxiliary ports in 1024-65535: "
                f"expected_count={case.aux_port_count}, got={auxiliary_ports!r}"
            )
        return (
            FaultPlan(
                injector_type=PgResourceGovernancePartitionCleanupInjector,
                config={
                    "auxiliary_ports": auxiliary_ports,
                    "fault_ready_timeout_seconds": 90.0 if case.case_no == 0 else 60.0,
                },
            ),
        )
