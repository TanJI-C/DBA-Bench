"""Runtime topology for the PostgreSQL backup/RPO certification scenario.

The scenario owns the lifecycle controller, while this module owns the
primary deployment and the isolated restore resources.  All resource names
are derived from the run and case identity so two cases cannot share state.
"""

from __future__ import annotations

import re
import json
import shlex
import subprocess
import threading
import time
from collections import deque
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping

from src.agent_language import agent_text
from src.execution.history.metrics import MetricDefinition, MetricService
from src.execution.history.records import (
    CapturedRecords,
    HistoricalCoverage,
    HistoricalPointRecord,
    HistoricalRecordSource,
)
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.execution.postgres_metrics import (
    LivePostgresSamplerMetricProvider,
    PostgresMetricCatalog,
    PostgresMetricSourceDefinition,
)
from src.execution.postgres_history import (
    PgStatementCounters,
    PgStatementKey,
    PgStatementSnapshot,
)


_WAL_SEGMENT_RE = re.compile(r"^(?P<timeline>[0-9A-Fa-f]{8})(?P<log>[0-9A-Fa-f]{8})(?P<segment>[0-9A-Fa-f]{8})$")

# The archive route tier lives in postgresql.auto.conf (not on the command
# line) so the certification chain can re-point it at runtime through the
# normal ALTER SYSTEM channel. The standard route is the deployment default;
# the emergency route is the incident response tier whose transmission
# throttle keeps up with an idle segment cadence but cannot sustain the
# certification capacity replay.
RPO_ARCHIVE_ROUTE_STANDARD = "standard"
RPO_ARCHIVE_ROUTE_EMERGENCY = "emergency"
RPO_ARCHIVE_COMMAND = "/usr/local/bin/aiopsbench-rpo-archive %p %f"
RPO_ARCHIVE_EMERGENCY_COMMAND = "/usr/local/bin/aiopsbench-rpo-archive --route=emergency %p %f"


RPO_METRIC_DEFINITIONS = {
    "wal_generation": MetricDefinition(
        name="wal_generation",
        value_fields=("bytes_per_sec", "fpi_per_sec", "segments_switched"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "archive_delivery": MetricDefinition(
        name="archive_delivery",
        value_fields=("bytes_per_sec", "segments_per_min", "success_delta", "failure_delta"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "archive_backlog": MetricDefinition(
        name="archive_backlog",
        value_fields=("ready_files", "oldest_age_sec", "pg_wal_bytes"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "business_commits": MetricDefinition(
        name="business_commits",
        value_fields=("commits_per_sec", "marker_commits_per_min"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "backup_progress": MetricDefinition(
        name="backup_progress",
        value_fields=("bytes_per_sec", "progress_percent", "backup_read_mb_per_sec"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
}

RPO_METRIC_SOURCES = {
    "wal_generation": PostgresMetricSourceDefinition(source="pg_stat_wal_delta_v1", target_shape="postgres"),
    "archive_delivery": PostgresMetricSourceDefinition(source="archive_repository_durable_v1", target_shape="repository"),
    "archive_backlog": PostgresMetricSourceDefinition(source="pg_wal_archive_status_v1", target_shape="postgres"),
    "business_commits": PostgresMetricSourceDefinition(source="pg_business_commit_delta_v1", target_shape="primary"),
    "backup_progress": PostgresMetricSourceDefinition(source="pg_backup_progress_v1", target_shape="backup_repository"),
}

RPO_METRIC_CATALOG = PostgresMetricCatalog(
    extra_definitions=RPO_METRIC_DEFINITIONS,
    extra_sources=RPO_METRIC_SOURCES,
    catalog_version="postgres-rpo-metric-catalog-v1",
)

# Keep the complete 12-hour Hard history on the public fixed-grid sampler. The
# response budget is enforced by the frozen timeline's overview step; this ring
# must not evict the oldest evidence first.
RPO_HISTORY_MAX_POINTS = 21_601


def _slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return value or "run"


@dataclass(frozen=True, slots=True)
class RpoTopology:
    run_id: str
    case_id: str
    primary_port: int
    restore_port: int
    primary_container: str
    restore_container: str
    archive_volume: str
    backup_volume: str
    restore_volume: str
    network_name: str
    fault_image_name: str
    archive_mount: str = "/aiopsbench/archive"
    backup_mount: str = "/aiopsbench/basebackups"

    def __post_init__(self) -> None:
        if self.primary_port <= 0 or self.restore_port <= 0:
            raise ValueError("RPO topology ports must be positive")
        if self.primary_port == self.restore_port:
            raise ValueError("primary and restore ports must be distinct")
        names = (
            self.primary_container,
            self.restore_container,
            self.archive_volume,
            self.backup_volume,
            self.restore_volume,
            self.network_name,
        )
        if len(set(names)) != len(names):
            raise ValueError(f"RPO topology resource names must be unique: {names!r}")

    @classmethod
    def for_run(
        cls,
        *,
        run_id: str,
        case_id: str,
        primary_port: int = 15811,
        restore_port: int = 15812,
    ) -> "RpoTopology":
        identity = _slug(f"{run_id}-{case_id}")
        return cls(
            run_id=run_id,
            case_id=case_id,
            primary_port=primary_port,
            restore_port=restore_port,
            primary_container=f"aiopsbench-rpo-primary-{identity}",
            restore_container=f"aiopsbench-rpo-restore-{identity}",
            archive_volume=f"aiopsbench-rpo-archive-{identity}",
            backup_volume=f"aiopsbench-rpo-backup-{identity}",
            restore_volume=f"aiopsbench-rpo-restore-data-{identity}",
            network_name=f"aiopsbench-rpo-net-{identity}",
            fault_image_name=f"aiopsbench-pg-rpo-fault-{identity}:latest",
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "case_id": self.case_id,
            "primary_port": self.primary_port,
            "restore_port": self.restore_port,
            "primary_container": self.primary_container,
            "restore_container": self.restore_container,
            "archive_volume": self.archive_volume,
            "backup_volume": self.backup_volume,
            "restore_volume": self.restore_volume,
            "network_name": self.network_name,
            "fault_image_name": self.fault_image_name,
            "archive_mount": self.archive_mount,
            "backup_mount": self.backup_mount,
        }


def _run(command: list[str], *, timeout: int = 30, check: bool = False) -> subprocess.CompletedProcess:
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if check and result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}: "
            f"{(result.stderr or result.stdout).strip()}"
        )
    return result


def archive_chain_continuity(file_names: list[str] | tuple[str, ...] | set[str]) -> dict[str, Any]:
    """Check adjacent 16 MiB WAL segments without treating backup history as a segment."""
    parsed = []
    for raw_name in file_names:
        name = str(raw_name)
        match = _WAL_SEGMENT_RE.fullmatch(name)
        if match:
            parsed.append((
                int(match.group("timeline"), 16),
                int(match.group("log"), 16),
                int(match.group("segment"), 16),
                name,
            ))
    parsed.sort()
    missing: list[str] = []
    for previous, current in zip(parsed, parsed[1:]):
        if previous[:1] != current[:1]:
            continue
        expected_segment = previous[2] + 1
        expected_log = previous[1]
        if expected_segment >= 0x100:
            expected_segment = 0
            expected_log += 1
        if current[1:3] != (expected_log, expected_segment):
            missing.append(
                f"{previous[0]:08X}{expected_log:08X}{expected_segment:08X}"
            )
    return {
        "wal_files": [item[3] for item in parsed],
        "missing_segments": missing,
        "timeline_contiguous": bool(parsed) and not missing,
    }


class RpoPGDeployment(PGDockerDeployment):
    """Primary PG deployment with dedicated backup/archive mounts and network."""

    def __init__(self, *, topology: RpoTopology, **kwargs: Any) -> None:
        super().__init__(
            container_name=topology.primary_container,
            port=topology.primary_port,
            **kwargs,
        )
        self.topology = topology

    def _build_docker_run_command(self, for_init: bool = False) -> list[str]:
        command = super()._build_docker_run_command(for_init=for_init)
        image_index = next(
            (
                index
                for index, value in enumerate(command)
                if value in {self.image_name, "postgres:16"}
            ),
            len(command),
        )
        mounts = [
            "--network", self.topology.network_name,
            "-v", f"{self.topology.archive_volume}:{self.topology.archive_mount}",
            "-v", f"{self.topology.backup_volume}:{self.topology.backup_mount}",
            "-v", f"{self._archive_script_path()}:/usr/local/bin/aiopsbench-rpo-archive:ro",
        ]
        command[image_index:image_index] = mounts
        if not for_init and command[-2:] == ["bash", "/pg-entrypoint.sh"]:
            command[-2:] = [
                "bash",
                "-lc",
                "chown postgres:postgres /aiopsbench/archive /aiopsbench/basebackups "
                "&& exec bash /pg-entrypoint.sh",
            ]
        return command

    @staticmethod
    def _archive_script_path() -> str:
        return str(Path(__file__).resolve().parents[2] / "scripts" / "backup_rpo_archive_command.sh")


class RpoPGEnv(PGEnv):
    """PGEnv variant exposing controlled archive and isolated PITR operations."""

    is_rpo_environment = True
    public_sql_protected_relations = (
        "aiopsbench_rpo.business_markers",
        "aiopsbench_rpo.recovery_fences",
    )
    # RPO runtime options carry the history-observability contract at
    # PostgreSQL startup, with one deliberate exception: archive_command is
    # kept off the postgres command line (a command-line GUC outranks
    # postgresql.auto.conf) and is applied via ALTER SYSTEM right after
    # deployment readiness, so the incident archive-route lifecycle (close-out
    # rebinding, agent restore, recovery cleanup) is physically effective.
    history_guc_mutation_allowed = False
    RPO_PUBLIC_TOOLS = (
        "query_metrics",
        "execute_sql",
        "manage_instance",
        "read_log",
        "help",
        "submit",
        "exit",
    )
    _RPO_FORBIDDEN_MANAGE_ACTIONS = frozenset({
        "set_config",
        "reset_config",
        "pgbouncer_set_config",
        "pgbouncer_reload",
    })

    def _frozen_history_public_tools(self) -> tuple[str, ...]:
        return self.RPO_PUBLIC_TOOLS

    def _refresh_rpo_tool_specs(self) -> None:
        visible_metrics = {*RPO_METRIC_DEFINITIONS, "oltp_service"}
        action_description = agent_text(
            zh=(
                "RPO action。合法组合: archive_status/archive_repository; "
                "rpo_topology/archive_repository; recover_archive/archive_repository; "
                "validate_backup/backup_repository; pitr_restore/evaluator_selected。"
            ),
            en=(
                "RPO action. Valid combinations: archive_status/archive_repository; "
                "rpo_topology/archive_repository; recover_archive/archive_repository; "
                "validate_backup/backup_repository; pitr_restore/evaluator_selected."
            ),
        )
        target_description = agent_text(
            zh=(
                "必须使用 action 对应的逻辑 target，禁止猜测容器路径: "
                "archive_repository、backup_repository 或 evaluator_selected。"
            ),
            en=(
                "Use the logical target that matches the action; do not guess container paths: "
                "archive_repository, backup_repository or evaluator_selected."
            ),
        )
        self._enabled_tool_specs = [
            replace(
                spec,
                description=agent_text(
                    zh="管理 RPO 归档与隔离恢复；仅支持当前 Case 声明的逻辑 action/target。",
                    en="Manage RPO archiving and isolated recovery; only the logical action/target declared by the current Case are supported.",
                ),
                parameters=tuple(
                    replace(parameter, description=action_description)
                    if parameter.name == "action"
                    else replace(parameter, description=target_description)
                    if parameter.name == "target"
                    else parameter
                    for parameter in spec.parameters
                ),
            )
            if spec.alias == "manage_instance"
            else replace(
                spec,
                parameters=tuple(
                    replace(
                        parameter,
                        description=(
                            agent_text(
                                zh="当前 RPO Case metric，可选值: ",
                                en="Metric of the current RPO Case, allowed values: ",
                            )
                            + ", ".join(sorted(visible_metrics))
                        ),
                    )
                    if parameter.name == "metric_type"
                    else parameter
                    for parameter in spec.parameters
                ),
                definition={
                    **spec.definition,
                    "parameter_definitions": [
                        {
                            **parameter,
                            **(
                                {"allowed_values": sorted(visible_metrics)}
                                if parameter.get("parameter_name") == "metric_type"
                                else {}
                            ),
                        }
                        for parameter in spec.definition["parameter_definitions"]
                    ],
                    "metric_definitions": [
                        item for item in spec.definition["metric_definitions"]
                        if item["metric_name"] in visible_metrics
                    ],
                },
            )
            if spec.alias == "query_metrics" and spec.definition is not None
            else spec
            for spec in self._enabled_tool_specs
        ]
        self._alias_to_tool_spec = {spec.alias: spec for spec in self._enabled_tool_specs}

    def configure_case(self, case) -> None:
        super().configure_case(case)
        self._refresh_rpo_tool_specs()

    def __init__(
        self,
        *,
        topology: RpoTopology,
        image_name: str = "aiopsbench-pg-initialized:latest",
        postgres_password: str = "password",
        postgres_db: str = "testdb",
        **kwargs: Any,
    ) -> None:
        self.rpo_topology = topology
        self.rpo_runtime_state: dict[str, Any] = {}
        self.rpo_standard_archive_command: str | None = None
        self._rpo_operation_events: list[HistoricalPointRecord] = []
        self._rpo_operation_events_lock = threading.RLock()
        self._rpo_sampler_state: dict[str, float | str] = {}
        self._rpo_service_observations: deque[tuple[int, float, bool]] = deque(maxlen=120)
        self._metric_history_backup_probe: subprocess.Popen | None = None
        self._metric_history_oltp_probe: subprocess.Popen | None = None
        self._metric_history_wal_burst_probe: subprocess.Popen | None = None
        self._metric_history_backup_probe_started_ms: int | None = None
        env_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key in {
                "sample_interval_sec",
                "history_maxlen",
                "ret_window_len",
                "tool_profile",
                "enabled_tools",
                "allow_sampler_jitter",
                "allow_sampler_reconnect",
            }
        }
        # RPO certification has no resource-metric contract. Avoid starting the
        # generic sampler so host scheduling cannot invalidate backup evidence.
        # Deploy readiness can take a long time on a busy Docker host. Do not
        # start an unneeded sampler before the frozen-history lifecycle configures
        # its fixed-grid observation window.
        self.disable_generic_sampler = True
        env_kwargs["enabled_tools"] = self.RPO_PUBLIC_TOOLS
        deployment = RpoPGDeployment(
            topology=topology,
            postgres_user="postgres",
            postgres_password=postgres_password,
            postgres_db=postgres_db,
            image_name=image_name,
            resources={
                "cpus": 2.0,
                "memory_mb": 1024,
                "shm_size": "256m",
                "disk_quota_mb": 8192,
            },
        )
        super().__init__(
            deployment=deployment,
            host="localhost",
            port=topology.primary_port,
            user="postgres",
            password=postgres_password,
            dbname=postgres_db,
            **env_kwargs,
        )
        self._metric_catalog = RPO_METRIC_CATALOG
        self._metric_service = MetricService(
            catalog=self._metric_catalog,
            live=LivePostgresSamplerMetricProvider(
                sample_interval_sec=self.sample_interval_sec,
                max_points=RPO_HISTORY_MAX_POINTS,
                catalog=self._metric_catalog,
            ),
        )
        # Refresh the enabled ToolSpec after binding the RPO catalog so native
        # function calling and help() expose the same public metrics.
        self._configure_tools(self.RPO_PUBLIC_TOOLS)
        self._refresh_metric_query_tool_spec()
        # Agent native schemas are bound before Orchestrator.setup() calls
        # configure_case(), so the RPO-only surface must already be exact here.
        self._refresh_rpo_tool_specs()

    def manage_instance(self, action: str, target: str = None, value: str = None) -> str:
        """Keep generic configuration mutation outside the RPO recovery contract."""
        if str(action or "").casefold() in self._RPO_FORBIDDEN_MANAGE_ACTIONS:
            return json.dumps({
                "status": "error",
                "error": "RPO certification does not permit instance or pool configuration mutation",
            }, ensure_ascii=False)
        return super().manage_instance(action, target, value)

    def configure_history_observability(self, spec) -> None:
        """Start the shared sampler only after deployment readiness is complete."""
        self.disable_generic_sampler = False
        self._rpo_sampler_state.clear()
        self._rpo_service_observations.clear()
        super().configure_history_observability(spec)

    def query_metrics(self, metric_type: str, target=None, threshold_ms=None, tables=None,
                      limit=None, start_timestamp=None, end_timestamp=None,
                      step_seconds=None) -> str:
        """Serve the coarse frozen overview grid for RPO metrics.

        The shared overview budget keeps only the newest 20 grid points, which
        for the 12-hour RPO history reduces the public overview to the quiet
        regime tail and erases every earlier evidence window from the first
        observation. Frozen-history certification requires the coarse whole
        timeline (43200s / 480s = 90 points, inside the shared point budget);
        explicit bounded windows bypass the overview budget and carry their own
        window/step contract. A self-limited no-window request re-creates the
        same evidence erasure, so any no-window overview call is served on the
        full coarse grid regardless of an explicit limit.
        """
        if (
            start_timestamp is None
            and end_timestamp is None
            and getattr(self, "_history_timeline", None) is not None
            and str(metric_type).casefold() in self._metric_catalog.metric_names
        ):
            timeline = self._history_timeline
            limit = (
                (timeline.visible_end_ms - timeline.visible_start_ms)
                // (timeline.overview_step_seconds * 1000)
                + 2
            )
        return super().query_metrics(
            metric_type,
            target=target,
            threshold_ms=threshold_ms,
            tables=tables,
            limit=limit,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            step_seconds=step_seconds,
        )

    def _resource_sampler_loop(self) -> None:
        """Collect only the RPO catalog on the shared fixed UTC grid.

        RPO history does not expose the generic resource metrics, statement
        snapshots, or cache counters. Avoiding those unrelated queries keeps
        the public two-second history contract from depending on host-wide
        workload contention.
        """
        interval_ms = self.sample_interval_sec * 1000
        next_timestamp_ms = (int(time.time() * 1000) // interval_ms + 1) * interval_ms
        while not self._sampler_stop.is_set():
            wait_seconds = next_timestamp_ms / 1000 - time.time()
            if wait_seconds > 0 and self._sampler_stop.wait(wait_seconds):
                return
            if self._sampler_stop.is_set():
                return
            timestamp_ms = next_timestamp_ms
            sampler_conn = self._sampler_ensure_conn()
            if sampler_conn is None:
                return
            values = self._sample_additional_metrics(sampler_conn, timestamp_ms)
            with self._metric_service.live.lock:
                self._metric_service.live.append_sample(timestamp_ms, values)
            with self._sampler_condition:
                self._sampler_last_timestamp_ms = timestamp_ms
                self._sampler_condition.notify_all()
            next_timestamp_ms += interval_ms
            lag_seconds = time.time() - next_timestamp_ms / 1000
            if lag_seconds > max(1.0, self.sample_interval_sec * 0.25):
                if self.allow_sampler_jitter:
                    next_timestamp_ms = (
                        int(time.time() * 1000) // interval_ms + 1
                    ) * interval_ms
                    continue
                raise RuntimeError(
                    "PostgreSQL RPO sampler missed a fixed grid tick: "
                    f"completed_timestamp_ms={timestamp_ms}, next_timestamp_ms={next_timestamp_ms}, "
                    f"lag_seconds={lag_seconds:.3f}"
                )

    def start_metric_history_normal_capture(self) -> None:
        """Run real archive, backup, and OLTP work while the normal window is captured."""
        # archive_command is applied through postgresql.auto.conf (ALTER
        # SYSTEM at deploy time); the normal capture only flips the wrapper's
        # delay control file back to the standard no-pacing tier.
        _run([
            "docker", "exec", "-u", "postgres", self.deployment.container_name,
            "bash", "-lc", "printf '0\\n' > /aiopsbench/archive/.aiopsbench-delay-seconds",
        ], check=True)
        self._record_archive_route_config_event()
        _run([
            "docker", "exec", "-u", "postgres", self.deployment.container_name,
            "bash", "-lc", "printf '1\\n' > /aiopsbench/archive/.aiopsbench-fail-next",
        ], check=True)
        table_probe = _run([
            "docker", "exec", "-e", "PGPASSWORD=password", self.deployment.container_name,
            "psql", "-U", "postgres", "-d", "testdb", "-At", "-c",
            "SELECT to_regclass('public.pgbench_accounts');",
        ], timeout=30)
        if table_probe.returncode != 0 or table_probe.stdout.strip() != "pgbench_accounts":
            _run(
                [
                    "docker", "exec", "-e", "PGPASSWORD=password", self.deployment.container_name,
                    "pgbench", "-h", "127.0.0.1", "-U", "postgres", "-d", "testdb",
                    "-i", "-s", "1", "-q",
                ],
                check=True,
                timeout=600,
            )

        if self._metric_history_oltp_probe is None or self._metric_history_oltp_probe.poll() is not None:
            self._metric_history_oltp_probe = subprocess.Popen(
                [
                    "docker", "exec", "-e", "PGPASSWORD=password", self.deployment.container_name,
                    "pgbench", "-h", "127.0.0.1", "-U", "postgres", "-d", "testdb",
                    "-c", "1", "-j", "1", "-T", "1200", "-P", "5",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.record_operation_event(
                event_type="workload_run",
                entity_type="primary",
                entity="oltp_workload",
                action="start",
                status="running",
                correlation_id=f"metric-history-oltp-{self.rpo_topology.case_id}",
            )
        if self._metric_history_wal_burst_probe is None or self._metric_history_wal_burst_probe.poll() is not None:
            self._metric_history_wal_burst_probe = subprocess.Popen(
                [
                    "docker", "exec", "-e", "PGPASSWORD=password", self.deployment.container_name,
                    "pgbench", "-h", "127.0.0.1", "-U", "postgres", "-d", "testdb",
                    "-c", "4", "-j", "4", "-T", "40", "-P", "5",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.record_operation_event(
                event_type="workload_run",
                entity_type="primary",
                entity="wal_burst_workload",
                action="start",
                status="running",
                correlation_id=f"metric-history-wal-burst-{self.rpo_topology.case_id}",
                details={"clients": 4, "duration_seconds": 40},
            )
        process = self._metric_history_backup_probe
        if process is not None and process.poll() is None:
            return
        # Make the benign normal-window backup a usable trusted artifact when
        # it finishes. The injector reuses it after the window; incomplete
        # probes are discarded by its existing real-backup fallback.
        # -c fast is required: without it pg_basebackup waits up to
        # checkpoint_timeout for a checkpoint, outlives the capture window,
        # and a killed client leaves an orphaned in-container backup racing
        # the injector's own pg_basebackup for the same destination.
        destination = "/aiopsbench/basebackups/base"
        command = [
            "docker", "exec", "-e", "PGPASSWORD=password", self.deployment.container_name,
            "bash", "-lc",
            (
                f"rm -rf {destination} && mkdir -p {destination} && "
                f"exec pg_basebackup -h 127.0.0.1 -U postgres -D {destination} "
                "-Fp -Xs -P -c fast --manifest-checksums=SHA256 --max-rate=16M"
            ),
        ]
        self._metric_history_backup_probe = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        self._metric_history_backup_probe_started_ms = int(time.time() * 1000)
        self.record_operation_event(
            event_type="backup_run",
            entity_type="repository",
            entity="base_backup_repository",
            action="start",
            status="running",
            correlation_id=f"metric-history-backup-{self.rpo_topology.case_id}",
            details={
                "destination": destination,
                "max_rate": "16M",
            },
            timestamp_ms=self._metric_history_backup_probe_started_ms,
        )

    def _record_archive_route_config_event(self) -> None:
        """Record the standard archive route binding into public history.

        The frozen history's normal windows are the only surface that carries
        the standard delivery tier (route command, zero transport pacing);
        the current instance state never publishes route values. The binding
        is a state fact valid for the whole capture window, so it is recorded
        as route_config announcements every 20 seconds across the 120-second
        normal capture (first normalized +6s into the window because this
        hook runs a fraction of a second before the aligned capture start).
        Where the assembled history publishes these records is owned by the
        Case's history contract: a spec declaring
        pre_incident_strip_seconds replays them only into the normal blocks
        immediately before the target window (the evidence is then physically
        coupled to the incident neighborhood), while every other spec replays
        them with all normal blocks.

        Shared RPO environment surface (both throughput_gap cases): the hard
        case gains the same factual route records.
        """
        probe = json.loads(self.execute_sql_trusted(
            "SELECT current_setting('archive_command')"
        ))
        if probe.get("status") == "error" or not probe.get("result"):
            raise RuntimeError(
                "archive route config probe failed: "
                f"case={self.rpo_topology.case_id}: {probe}"
            )
        archive_command = str(probe["result"][0][0])
        now_ms = int(time.time() * 1000)
        for offset_seconds in (6, 26, 46, 66, 86, 106):
            self.record_operation_event(
                event_type="repository_sync",
                entity_type="repository",
                entity="archive_repository",
                action="route_config",
                status="success",
                correlation_id=f"archive-route-config-{self.rpo_topology.case_id}",
                details={
                    "archive_command": archive_command,
                    "transport_pacing_seconds": 0,
                },
                timestamp_ms=now_ms + offset_seconds * 1000,
            )

    def finish_metric_history_normal_capture(self) -> None:
        """Stop the normal-window backup probe before the fault window starts."""
        wal_burst_process = self._metric_history_wal_burst_probe
        self._metric_history_wal_burst_probe = None
        wal_burst_error = None
        wal_burst_status = "success"
        if wal_burst_process is not None:
            if wal_burst_process.poll() is None:
                try:
                    wal_burst_process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    # Docker may keep the exec stream open after the bounded
                    # workload window has elapsed under load.
                    wal_burst_status = "stopped"
                    wal_burst_process.terminate()
                    try:
                        wal_burst_process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        wal_burst_process.kill()
                        wal_burst_process.wait(timeout=10)
            elif wal_burst_process.returncode != 0:
                detail = (wal_burst_process.stderr.read() if wal_burst_process.stderr else "").strip()
                wal_burst_error = RuntimeError(
                    f"normal WAL burst workload failed: returncode={wal_burst_process.returncode}, detail={detail}"
                )
                wal_burst_status = "failed"
            self.record_operation_event(
                event_type="workload_run",
                entity_type="primary",
                entity="wal_burst_workload",
                action="finish",
                status=wal_burst_status,
                correlation_id=f"metric-history-wal-burst-{self.rpo_topology.case_id}",
                details={"clients": 4, "duration_seconds": 40},
            )
        oltp_process = self._metric_history_oltp_probe
        self._metric_history_oltp_probe = None
        oltp_status = "success"
        oltp_error: RuntimeError | None = None
        if oltp_process is not None:
            if oltp_process.poll() is None:
                oltp_process.terminate()
                try:
                    oltp_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    oltp_process.kill()
                    oltp_process.wait(timeout=10)
                oltp_status = "stopped"
            elif oltp_process.returncode != 0:
                detail = (oltp_process.stderr.read() if oltp_process.stderr else "").strip()
                oltp_status = "failed"
                oltp_error = RuntimeError(
                    f"normal OLTP workload failed: returncode={oltp_process.returncode}, detail={detail}"
                )
            self.record_operation_event(
                event_type="workload_run",
                entity_type="primary",
                entity="oltp_workload",
                action="finish",
                status=oltp_status,
                correlation_id=f"metric-history-oltp-{self.rpo_topology.case_id}",
            )
        process = self._metric_history_backup_probe
        self._metric_history_backup_probe = None
        if process is not None:
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
            self.record_operation_event(
                event_type="backup_run",
                entity_type="repository",
                entity="base_backup_repository",
                action="finish",
                status="success" if process.returncode == 0 else "stopped",
                correlation_id=f"metric-history-backup-{self.rpo_topology.case_id}",
                details={
                    "durability_result": "verified" if process.returncode == 0 else "not_required",
                },
            )
        _run([
            "docker", "exec", self.deployment.container_name,
            "bash", "-lc", "rm -f /aiopsbench/archive/.aiopsbench-fail-next",
        ], timeout=30)
        if oltp_error is not None:
            raise oltp_error
        if wal_burst_error is not None:
            raise wal_burst_error

    def _sample_additional_metrics(self, sampler_conn, timestamp_ms: int) -> dict[str, dict[str, float]]:
        """Sample RPO counters from PostgreSQL and the mounted repository."""
        state = self._rpo_sampler_state

        def delta(name: str, current: float) -> float:
            previous = state.get(name)
            state[name] = current
            if not isinstance(previous, (int, float)) or current < previous:
                return 0.0
            return current - previous

        interval_seconds = max(self.sample_interval_sec, 1)
        probe_started = time.perf_counter()
        probe_success = False
        try:
            with sampler_conn.cursor() as probe_cursor:
                probe_cursor.execute(
                    "SELECT abalance FROM public.pgbench_accounts WHERE aid = 1"
                )
                probe_cursor.fetchone()
            probe_success = True
        except Exception:
            sampler_conn.rollback()
        self._rpo_service_observations.append(
            (timestamp_ms, (time.perf_counter() - probe_started) * 1000.0, probe_success)
        )
        cutoff_ms = timestamp_ms - 30_000
        while self._rpo_service_observations and self._rpo_service_observations[0][0] < cutoff_ms:
            self._rpo_service_observations.popleft()
        recent_service = tuple(self._rpo_service_observations)
        sorted_latencies = sorted(item[1] for item in recent_service)
        p99_index = max(0, (len(sorted_latencies) * 99 + 99) // 100 - 1)
        service_p99_ms = sorted_latencies[p99_index] if sorted_latencies else 0.0
        service_success_ratio = (
            sum(1.0 for _, _, success in recent_service if success) / len(recent_service)
            if recent_service else 0.0
        )
        service_window_seconds = (
            max(
                interval_seconds,
                (recent_service[-1][0] - recent_service[0][0]) / 1000.0 + interval_seconds,
            )
            if recent_service
            else interval_seconds
        )
        service_transactions_per_sec = (
            sum(1.0 for _, _, success in recent_service if success) / service_window_seconds
            if recent_service
            else 0.0
        )
        with sampler_conn.cursor() as cursor:
            cursor.execute("SELECT wal_bytes, wal_fpi FROM pg_stat_wal")
            wal_bytes, wal_fpi = (float(value or 0) for value in cursor.fetchone())
            cursor.execute("SELECT archived_count, failed_count FROM pg_stat_archiver")
            archived_count, failed_count = (float(value or 0) for value in cursor.fetchone())
            cursor.execute(
                "SELECT COALESCE(SUM(xact_commit), 0), COALESCE(SUM(xact_rollback), 0) "
                "FROM pg_stat_database WHERE datname = current_database()"
            )
            commits, rollbacks = (float(value or 0) for value in cursor.fetchone())
            cursor.execute("SELECT COALESCE(SUM(calls), 0) FROM pg_stat_statements")
            statement_calls = float(cursor.fetchone()[0] or 0)
            state["statement_calls"] = statement_calls
            cursor.execute(
                "SELECT "
                "CASE WHEN pg_stat_file(current_setting('data_directory') || '/pg_wal/archive_status', true) IS NULL "
                "THEN 0 ELSE (SELECT COUNT(*) FILTER (WHERE name LIKE '%%.ready') "
                "FROM pg_ls_dir(current_setting('data_directory') || '/pg_wal/archive_status') AS files(name)) END, "
                "CASE WHEN pg_stat_file(current_setting('data_directory') || '/pg_wal/archive_status', true) IS NULL "
                "THEN 0 ELSE (SELECT COALESCE(MAX(EXTRACT(EPOCH FROM clock_timestamp() - "
                "(pg_stat_file(current_setting('data_directory') || '/pg_wal/archive_status/' || name, true)).modification)), 0) "
                "FROM pg_ls_dir(current_setting('data_directory') || '/pg_wal/archive_status') AS files(name)) END"
            )
            ready_files, oldest_age = (float(value or 0) for value in cursor.fetchone())
            cursor.execute(
                "SELECT COALESCE(SUM(size), 0) "
                "FROM pg_ls_waldir() "
                "WHERE name <> 'archive_status'"
            )
            pg_wal_bytes = float(cursor.fetchone()[0] or 0)
            cursor.execute(
                "SELECT COALESCE(SUM((pg_stat_file('/aiopsbench/archive/' || name, true)).size), 0) "
                "FROM pg_ls_dir('/aiopsbench/archive') AS files(name) "
                "WHERE name NOT LIKE '.%%'"
            )
            repository_bytes = float(cursor.fetchone()[0] or 0)
            cursor.execute(
                "SELECT COALESCE(SUM(backup_total), 0), COALESCE(SUM(backup_streamed), 0) "
                "FROM pg_stat_progress_basebackup"
            )
            backup_total, backup_streamed = (float(value or 0) for value in cursor.fetchone())
            try:
                cursor.execute("SELECT COUNT(*) FROM aiopsbench_rpo.business_markers")
                marker_count = float(cursor.fetchone()[0] or 0)
            except Exception:
                marker_count = 0.0
            cursor.execute("SELECT pg_walfile_name(pg_current_wal_lsn())")
            wal_file = str(cursor.fetchone()[0] or "")

        previous_wal_file = state.get("wal_file")
        state["wal_file"] = wal_file
        switched = 1.0 if previous_wal_file and wal_file != previous_wal_file else 0.0
        streamed_delta = delta("backup_streamed", backup_streamed)
        rollback_delta = delta("rollbacks", rollbacks)
        commit_delta = delta("commits", commits)
        transaction_delta = commit_delta + rollback_delta
        total = backup_total
        return {
            "wal_generation": {
                "bytes_per_sec": round(delta("wal_bytes", wal_bytes) / interval_seconds, 3),
                "fpi_per_sec": round(delta("wal_fpi", wal_fpi) / interval_seconds, 3),
                "segments_switched": switched,
            },
            "archive_delivery": {
                "bytes_per_sec": round(delta("repository_bytes", repository_bytes) / interval_seconds, 3),
                "segments_per_min": round(delta("archived_count", archived_count) * 60 / interval_seconds, 3),
                "success_delta": delta("archived_count_visible", archived_count),
                "failure_delta": delta("failed_count", failed_count),
            },
            "archive_backlog": {
                "ready_files": ready_files,
                "oldest_age_sec": oldest_age,
                "pg_wal_bytes": pg_wal_bytes,
            },
            "business_commits": {
                "commits_per_sec": round(commit_delta / interval_seconds, 3),
                "marker_commits_per_min": round(delta("marker_count", marker_count) * 60 / interval_seconds, 3),
            },
            "oltp_service": {
                "transactions_per_sec": round(service_transactions_per_sec, 3),
                "p99_ms": round(service_p99_ms, 3),
                "success_ratio": round(service_success_ratio, 4),
            },
            "backup_progress": {
                "bytes_per_sec": round(streamed_delta / interval_seconds, 3),
                "progress_percent": round(min(100.0, backup_streamed * 100.0 / total) if total > 0 else 0.0, 3),
                "backup_read_mb_per_sec": round(streamed_delta / interval_seconds / (1024 * 1024), 3),
            },
        }

    def _capture_sampler_statement_snapshot(self, sampler_conn, timestamp_ms: int) -> PgStatementSnapshot:
        """Use the already-read aggregate calls counter for qps-only sampling."""
        statement_calls = self._rpo_sampler_state.get("statement_calls")
        if not isinstance(statement_calls, (int, float)):
            with sampler_conn.cursor() as cursor:
                cursor.execute("SELECT COALESCE(SUM(calls), 0) FROM pg_stat_statements")
                statement_calls = float(cursor.fetchone()[0] or 0)
        return PgStatementSnapshot(
            timestamp_ms=timestamp_ms,
            counters={
                PgStatementKey(userid=0, dbid=0, queryid=-1): PgStatementCounters(
                    query="__rpo_aggregate_calls__",
                    calls=int(statement_calls),
                    total_exec_time_ms=0.0,
                    rows=0,
                    shared_blks_hit=0,
                    shared_blks_read=0,
                    shared_blks_written=0,
                    temp_blks_read=0,
                    temp_blks_written=0,
                )
            },
        )

    def record_operation_event(
        self,
        *,
        event_type: str,
        entity_type: str,
        entity: str,
        action: str,
        status: str,
        correlation_id: str,
        details: Mapping[str, object] | None = None,
        timestamp_ms: int | None = None,
    ) -> None:
        payload = {
            "event_type": str(event_type),
            "entity_type": str(entity_type),
            "entity": str(entity),
            "action": str(action),
            "status": str(status),
            "correlation_id": str(correlation_id),
            "details": dict(details or {}),
        }
        record = HistoricalPointRecord(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            timestamp_ms=int(timestamp_ms if timestamp_ms is not None else time.time() * 1000),
            payload=payload,
        )
        with self._rpo_operation_events_lock:
            self._rpo_operation_events.append(record)

    def _archive_operation_events(self) -> tuple[HistoricalPointRecord, ...]:
        command = [
            "docker", "exec", self.deployment.container_name,
            "bash", "-lc", "test -r /aiopsbench/archive/.aiopsbench-operation-events.jsonl && cat /aiopsbench/archive/.aiopsbench-operation-events.jsonl",
        ]
        result = _run(command, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(
                "PostgreSQL operation-event history could not be read from the archive repository: "
                f"returncode={result.returncode}, detail={(result.stderr or result.stdout).strip()}"
            )
        records = []
        required_fields = {
            "timestamp_ms",
            "event_type",
            "entity_type",
            "entity",
            "action",
            "status",
            "correlation_id",
        }
        for line_number, line in enumerate(result.stdout.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                if not isinstance(raw, Mapping) or not required_fields.issubset(raw):
                    raise ValueError("missing required operation-event field")
                records.append(HistoricalPointRecord(
                    source=HistoricalRecordSource.OPERATION_EVENT,
                    target="postgres",
                    timestamp_ms=int(raw["timestamp_ms"]),
                    payload={
                        key: raw[key]
                        for key in (
                            "event_type", "entity_type", "entity", "action", "status", "correlation_id", "details"
                        )
                        if key in raw
                    },
                ))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise RuntimeError(
                    "PostgreSQL operation-event history contains an invalid record: "
                    f"line={line_number}, detail={exc}"
                ) from exc
        return tuple(records)

    def capture_history_records(self, sources, start_epoch_ms: int, end_epoch_ms: int) -> CapturedRecords:
        requested = tuple(sources)
        non_events = tuple(source for source in requested if source is not HistoricalRecordSource.OPERATION_EVENT)
        base = super().capture_history_records(non_events, start_epoch_ms, end_epoch_ms) if non_events else CapturedRecords()
        if HistoricalRecordSource.OPERATION_EVENT not in requested:
            return base
        with self._rpo_operation_events_lock:
            memory_records = tuple(self._rpo_operation_events)
        records = [*memory_records, *self._archive_operation_events()]
        selected = tuple(
            record for record in records
            if start_epoch_ms <= record.timestamp_ms <= end_epoch_ms
        )
        return CapturedRecords(
            point_records=(*base.point_records, *selected),
            interval_records=base.interval_records,
            coverage=(
                *base.coverage,
                HistoricalCoverage(
                    source=HistoricalRecordSource.OPERATION_EVENT,
                    target="postgres",
                    start_ms=start_epoch_ms,
                    end_ms=end_epoch_ms,
                ),
            ),
        )

    def provision_resources(self) -> None:
        for volume in (
            self.rpo_topology.archive_volume,
            self.rpo_topology.backup_volume,
            self.rpo_topology.restore_volume,
        ):
            _run(["docker", "volume", "create", volume], check=True)
        network = _run(["docker", "network", "inspect", self.rpo_topology.network_name])
        if network.returncode != 0:
            _run(["docker", "network", "create", self.rpo_topology.network_name], check=True)

    def _ensure_baseline(self) -> None:
        """RPO evidence is produced by the real archive/PITR timeline, not old baselines."""
        return None

    def configure_runtime(self, runtime) -> None:
        super().configure_runtime(runtime)
        self.deployment.host_port_offsets = (0, self.rpo_topology.restore_port - self.rpo_topology.primary_port)
        spec = getattr(runtime, "parameters", None)
        if spec is not None:
            self.rpo_standard_archive_command = spec.parameter("archive_command")
            # A command-line GUC outranks postgresql.auto.conf, so the archive
            # route must not be applied through POSTGRES_RUNTIME_OPTIONS; the
            # standard tier is activated via ALTER SYSTEM in deploy().
            self.deployment.postgres_runtime_options = " ".join(
                f"-c {shlex.quote(f'{name}={value}')}"
                for name, value in spec.parameters
                if name != "archive_command"
            )

    def _install_standard_archive_route(self) -> None:
        """Bind the standard archive route in postgresql.auto.conf.

        archive_command is deliberately absent from the case command-line
        parameters: a command-line value would shadow ALTER SYSTEM for the
        whole process lifetime, so the route tier must live in auto.conf to
        stay re-pointable at certification time.
        """
        standard_command = self.rpo_standard_archive_command or RPO_ARCHIVE_COMMAND
        activate = json.loads(self.execute_sql_trusted(
            f"ALTER SYSTEM SET archive_command = '{standard_command}'"
        ))
        if activate.get("status") == "error":
            raise RuntimeError(f"standard archive route installation failed: {activate}")
        reload_result = json.loads(self.execute_sql_trusted("SELECT pg_reload_conf()"))
        if reload_result.get("status") == "error":
            raise RuntimeError(f"standard archive route reload failed: {reload_result}")
        deadline = time.monotonic() + 15
        while True:
            probe = json.loads(self.execute_sql_trusted(
                "SELECT current_setting('archive_command')"
            ))
            if probe.get("status") == "error":
                raise RuntimeError(f"archive command probe failed: {probe}")
            if probe["result"][0][0] == standard_command:
                break
            if time.monotonic() > deadline:
                raise RuntimeError(
                    "standard archive command did not become active after deployment reload: "
                    f"expected={standard_command!r}, "
                    f"observed={probe['result'][0][0]!r}"
                )
            time.sleep(0.5)
        self.rpo_runtime_state["archive_route_tier"] = RPO_ARCHIVE_ROUTE_STANDARD

    def deploy(self) -> None:
        self.provision_resources()
        super().deploy()
        self._install_standard_archive_route()

    def set_rpo_controller(self, controller: object) -> None:
        self._rpo_controller = controller

    def rpo_frozen_stall_window_ms(self) -> tuple[int, int]:
        """Trusted frozen-history stall window for certification anchoring.

        Returns the assembled target window in frozen-timeline coordinates from
        the bound timeline audit. Injector/evaluator truth only; never exposed
        through public agent tools.
        """
        timeline = self._history_timeline
        if timeline is None:
            raise RuntimeError(
                "RPO certification requested the frozen stall window before metric history "
                f"was bound: run_id={self.rpo_topology.run_id!r}"
            )
        window = timeline.audit.get("target_window") if isinstance(timeline.audit, Mapping) else None
        if not isinstance(window, Mapping) or "start_ms" not in window or "end_ms" not in window:
            raise RuntimeError(
                "RPO frozen history audit has no target window: "
                f"audit_type={type(timeline.audit).__name__}, "
                f"keys={sorted(timeline.audit) if isinstance(timeline.audit, Mapping) else None}"
            )
        return int(window["start_ms"]), int(window["end_ms"])

    def cleanup_rpo_resources(self) -> None:
        topology = self.rpo_topology
        _run(["docker", "rm", "-f", topology.restore_container])
        for volume in (topology.restore_volume, topology.backup_volume, topology.archive_volume):
            _run(["docker", "volume", "rm", "-f", volume])
        _run(["docker", "network", "rm", topology.network_name])

    def teardown(self) -> None:
        failure: Exception | None = None
        try:
            super().teardown()
        except Exception as exc:
            failure = exc
        try:
            self.cleanup_rpo_resources()
        except Exception as exc:
            if failure is None:
                failure = exc
        if failure is not None:
            raise failure


def repository_listing(env: RpoPGEnv) -> dict[str, Any]:
    """Return the archive file listing with continuity, without checksums.

    A full-library sha256 sweep takes minutes on a busy shared host, so
    polling callers use this listing first and checksum only the files whose
    durability the poll actually judges.
    """
    command = [
        "docker", "exec", env.deployment.container_name, "bash", "-lc",
        "find /aiopsbench/archive -maxdepth 1 -type f ! -name '.aiopsbench-delay-seconds' -printf '%f\\t%s\\t%T@\\n' | sort",
    ]
    result = _run(command, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"archive listing failed: {(result.stderr or result.stdout).strip()}")
    entries: dict[str, dict[str, Any]] = {}
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) == 3:
            name, size, mtime = fields
            entries[name] = {"wal_file": name, "size_bytes": int(size), "mtime": float(mtime)}
    files = sorted(entries.values(), key=lambda item: item.get("wal_file", ""))
    continuity = archive_chain_continuity([item.get("wal_file", "") for item in files])
    return {"files": files, **continuity}


def archive_segment_checksums(env: RpoPGEnv, names: list[str] | tuple[str, ...] | set[str]) -> dict[str, str]:
    """Checksum explicit archive segment names; the archive-command owned volume."""
    validated = []
    for name in names:
        if not re.fullmatch(r"[0-9A-Za-z.\-]+", str(name)):
            raise ValueError(f"archive segment name is outside the WAL naming scheme: name={name!r}")
        validated.append(str(name))
    if not validated:
        return {}
    command = [
        "docker", "exec", env.deployment.container_name, "bash", "-lc",
        f"cd /aiopsbench/archive && sha256sum {' '.join(sorted(validated))}",
    ]
    result = _run(command, timeout=180)
    if result.returncode != 0:
        raise RuntimeError(f"archive checksum failed: {(result.stderr or result.stdout).strip()}")
    checksums: dict[str, str] = {}
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) == 2 and len(fields[0]) == 64:
            checksums[fields[1].rsplit("/", 1)[-1]] = fields[0]
    return checksums


def repository_inventory(env: RpoPGEnv) -> dict[str, Any]:
    """Return a file-backed archive inventory with checksums and sizes."""
    command = [
        "docker", "exec", env.deployment.container_name, "bash", "-lc",
        (
            # The emergency route stages segment copies as *.partial and moves
            # them into place atomically, so staging files are not durable
            # inventory members and vanish between the find and the checksum.
            "find /aiopsbench/archive -maxdepth 1 -type f ! -name '.aiopsbench-delay-seconds' ! -name '*.partial' -printf '%f\\t%s\\t%T@\\n' | sort; "
            # Batch the checksum arguments so a large real WAL inventory does
            # not pay one process startup per archived segment.
            "find /aiopsbench/archive -maxdepth 1 -type f ! -name '.aiopsbench-delay-seconds' ! -name '*.partial' -print0 | "
            "xargs -0 -r sha256sum"
        ),
    ]
    # The certification replay leaves the archive holding the replayed burst
    # on top of the canary segments; a busy host can push the batched
    # sha256 inventory past 60 s, so keep the same 180 s
    # headroom the certification surfaces already use.
    result = _run(command, timeout=180)
    if result.returncode != 0:
        raise RuntimeError(f"archive inventory failed: {(result.stderr or result.stdout).strip()}")
    entries: dict[str, dict[str, Any]] = {}
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) == 3:
            name, size, mtime = fields
            entries[name] = {"wal_file": name, "size_bytes": int(size), "mtime": float(mtime)}
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[0].isalnum() and len(fields[0]) == 64:
            entries.setdefault(fields[1].rsplit("/", 1)[-1], {})["sha256"] = fields[0]
    files = sorted(entries.values(), key=lambda item: item.get("wal_file", ""))
    continuity = archive_chain_continuity([item.get("wal_file", "") for item in files])
    return {"files": files, **continuity}


__all__ = [
    "RpoTopology",
    "RpoPGDeployment",
    "RpoPGEnv",
    "archive_chain_continuity",
    "archive_segment_checksums",
    "repository_inventory",
    "repository_listing",
]
