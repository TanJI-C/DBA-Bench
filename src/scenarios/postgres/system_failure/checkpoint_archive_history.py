"""Public frozen-history observations for the PostgreSQL checkpoint/archive Case."""

from __future__ import annotations

import threading
import time
from collections.abc import Mapping

from src.execution.history.metrics import MetricDefinition
from src.execution.history.records import (
    CapturedRecords,
    HistoricalCoverage,
    HistoricalPointRecord,
    HistoricalRecordSource,
)
from src.execution.postgres_metrics import read_device_io_stats


_SEGMENT_BYTES = 16 * 1024 * 1024
_ARCHIVE_STATUS_RELATIVE_PATH = "/pg_wal/archive_status"
OLTP_PROFILE_NAME = "checkpoint_archive_oltp"


class CheckpointArchiveHistoryAdapter:
    """Expose scenario-owned metrics without creating an answer-direct tool."""

    _DEFINITIONS = {
        "wal_generation": MetricDefinition(
            name="wal_generation",
            value_fields=("bytes_per_sec", "fpi_per_sec", "records_per_sec"),
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        ),
        "checkpoint_activity": MetricDefinition(
            name="checkpoint_activity",
            value_fields=("requested_per_min", "timed_per_min", "write_ms_per_sec", "sync_ms_per_sec"),
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        ),
        "archive_delivery": MetricDefinition(
            name="archive_delivery",
            value_fields=("bytes_per_sec", "success_delta", "failure_delta", "retry_count"),
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
        "storage_pressure": MetricDefinition(
            name="storage_pressure",
            value_fields=(
                "read_mb_per_sec",
                "write_mb_per_sec",
                "checkpoint_io_time_ms_per_sec",
                "device_io_in_progress",
                "device_weighted_io_ms_per_sec",
            ),
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        ),
        "service_slo": MetricDefinition(
            name="service_slo",
            value_fields=("transactions_per_sec", "p99_ms", "success_ratio"),
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        ),
        "batch_progress": MetricDefinition(
            name="batch_progress",
            value_fields=("rows_per_sec", "completed_units", "deadline_remaining_sec"),
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        ),
    }

    def __init__(self) -> None:
        self.env = None
        self.case = None
        self._lock = threading.RLock()
        self._previous: dict[str, float] | None = None
        self._previous_timestamp_ms: int | None = None
        self._previous_rows = 0.0
        self._write_table_seen = False
        self._previous_device_weighted_io_ms: float | None = None
        self._previous_settings: tuple[str, str, str, str] | None = None
        self._events: list[HistoricalPointRecord] = []
        self._sample_count = 0
        self._started_at = time.monotonic()

    def configure(self, env, case) -> None:
        with self._lock:
            self.env = env
            self.case = case
            self._previous = None
            self._previous_timestamp_ms = None
            self._previous_rows = 0.0
            self._write_table_seen = False
            self._previous_device_weighted_io_ms = None
            self._previous_settings = None
            self._events.clear()
            self._sample_count = 0
            self._started_at = time.monotonic()

    def metric_definitions(self) -> Mapping[str, MetricDefinition]:
        return dict(self._DEFINITIONS)

    def target_variants(self, metric: str) -> tuple[str | None, ...]:
        """Every checkpoint/archive series is a single postgres-level target."""
        normalized = str(metric).casefold()
        if normalized not in self._DEFINITIONS:
            raise ValueError(
                f"Unknown checkpoint/archive scenario metric: metric={normalized!r}, "
                f"expected={sorted(self._DEFINITIONS)!r}"
            )
        return (None,)

    @property
    def metric_names(self) -> frozenset[str]:
        return frozenset(self._DEFINITIONS)

    def capture_history(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
    ):
        """Capture the adapter metrics from the shared fixed-grid sampler."""
        if self.env is None:
            raise RuntimeError("checkpoint/archive history adapter is not configured")
        condition = getattr(self.env, "_sampler_condition", None)
        if condition is not None:
            with condition:
                while (
                    getattr(self.env, "_sampler_last_timestamp_ms", None) is None
                    or self.env._sampler_last_timestamp_ms < end_epoch_ms
                ):
                    raise_failure = getattr(self.env, "_raise_sampler_failure", None)
                    if callable(raise_failure):
                        raise_failure()
                    sampler_thread = getattr(self.env, "_sampler_thread", None)
                    sampler_stop = getattr(self.env, "_sampler_stop", None)
                    if sampler_thread is None or (sampler_stop is not None and sampler_stop.is_set()):
                        raise RuntimeError("checkpoint/archive history sampler stopped before the requested end")
                    condition.wait()
        service = getattr(self.env, "_metric_service", None)
        live = getattr(service, "live", None)
        capture = getattr(live, "capture", None)
        if not callable(capture):
            raise RuntimeError("checkpoint/archive history sampler is unavailable")
        # The fixed-grid sampler can publish its first sample one tick after
        # the requested window start.  Clamp only that stale leading edge so
        # a short normal capture does not fail before the agent starts.
        samples = getattr(live, "_samples", None)
        if isinstance(samples, dict):
            starts = [entries[0][0] for entries in samples.values() if entries]
            if starts:
                start_epoch_ms = max(start_epoch_ms, max(starts))
        return capture(metrics, start_epoch_ms, end_epoch_ms, step_seconds)

    def observation_profile_names(self) -> tuple[str, ...]:
        return (OLTP_PROFILE_NAME,)

    def agent_contract(self) -> dict[str, object]:
        """Return schema guidance only; causal interpretation stays with the Agent."""
        case = self.case
        return {
            "series_target": "postgres",
            "metric_fields": {
                name: list(definition.value_fields)
                for name, definition in sorted(self._DEFINITIONS.items())
            },
            "sampling": {"step_seconds": 2, "query_target": None},
            "recovery_acceptance": {
                "joint_replay_window_seconds": int(case.replay_seconds),
                "max_wal_growth_bytes": int(case.wal_space_budget_bytes),
                "max_requested_checkpoint_delta": int(case.max_checkpoint_req_delta),
                "max_checkpoint_write_ms": float(case.max_checkpoint_write_ms),
                "min_transactions_per_second": float(case.min_tps),
                "max_oltp_p99_ms": float(case.max_p99_ms),
                "archive_safe_spare_mb": int(case.archive_repository_safe_spare_mb),
                "unit_scope": "joint write/report/backup replay and marker PITR verification",
            },
        }

    def _event(
        self,
        *,
        timestamp_ms: int,
        event_type: str,
        entity_type: str,
        entity: str,
        action: str,
        status: str,
        correlation_id: str,
        details: Mapping[str, object] | None = None,
    ) -> None:
        self._events.append(HistoricalPointRecord(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target="postgres",
            timestamp_ms=int(timestamp_ms),
            payload={
                "event_type": event_type,
                "entity_type": entity_type,
                "entity": entity,
                "action": action,
                "status": status,
                "correlation_id": correlation_id,
                "details": dict(details or {}),
            },
        ))

    def record_operation_event(self, **kwargs) -> None:
        """Record a scenario event through the shared operation-event source."""
        with self._lock:
            self._event(**kwargs)

    def capture_operation_events(self, start_epoch_ms: int, end_epoch_ms: int) -> CapturedRecords:
        with self._lock:
            events = tuple(
                event
                for event in self._events
                if start_epoch_ms <= event.timestamp_ms <= end_epoch_ms
            )
        return CapturedRecords(point_records=events)

    def capture_history_records(
        self,
        sources: tuple[HistoricalRecordSource, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
    ) -> CapturedRecords:
        """Expose operation events through the shared history-record contract."""
        if HistoricalRecordSource.OPERATION_EVENT not in tuple(sources):
            return CapturedRecords()
        captured = self.capture_operation_events(start_epoch_ms, end_epoch_ms)
        return CapturedRecords(
            point_records=captured.point_records,
            interval_records=captured.interval_records,
            coverage=(HistoricalCoverage(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                start_ms=start_epoch_ms,
                end_ms=end_epoch_ms,
            ),),
        )

    @staticmethod
    def _delta(current: float, previous: float | None) -> float:
        if previous is None or current < previous:
            return 0.0
        return current - previous

    def _query_rows(self, connection, table_name: str) -> float:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COALESCE(n_tup_ins, 0) FROM pg_stat_user_tables WHERE relname = %s",
                    (table_name,),
                )
                row = cursor.fetchone()
            if row is None:
                if not self._write_table_seen:
                    return 0.0
                with connection.cursor() as cursor:
                    cursor.execute("SELECT to_regclass(%s)", (f"public.{table_name}",))
                    relation = cursor.fetchone()
                if relation is not None and relation[0] is None:
                    # Recovery drops the task-owned write table by design. The
                    # frozen history ends at that point and the sampler must
                    # report zero rows instead of failing the stop path.
                    return 0.0
                raise RuntimeError(
                    f"write-table row counter returned no row after table was observed: table={table_name!r}"
                )
            if len(row) != 1:
                raise RuntimeError(
                    f"write-table row counter returned an invalid row: table={table_name!r}, row={row!r}"
                )
            self._write_table_seen = True
            return float(row[0] or 0.0)
        except Exception as exc:
            try:
                connection.rollback()
            except Exception:
                pass
            if isinstance(exc, RuntimeError):
                raise
            raise RuntimeError(
                f"write-table row counter sampling failed: table={table_name!r}"
            ) from exc

    def _archive_status(self, connection, timestamp_ms: int) -> tuple[float, float]:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_ls_dir FROM pg_ls_dir(current_setting('data_directory') || %s) "
                    "WHERE pg_ls_dir LIKE '%%.ready'",
                    (_ARCHIVE_STATUS_RELATIVE_PATH,),
                )
                names = [str(row[0]) for row in cursor.fetchall()]
            oldest_age = 0.0
            if names:
                ages = []
                with connection.cursor() as cursor:
                    for name in names:
                        cursor.execute(
                            "SELECT EXTRACT(EPOCH FROM (clock_timestamp() - "
                            "(pg_stat_file(current_setting('data_directory') || %s || %s, true)).modification))",
                            (_ARCHIVE_STATUS_RELATIVE_PATH + "/", name),
                        )
                        value = cursor.fetchone()[0]
                        if value is not None:
                            ages.append(max(0.0, float(value)))
                oldest_age = max(ages, default=0.0)
            return float(len(names)), oldest_age
        except Exception as exc:
            try:
                connection.rollback()
            except Exception:
                pass
            raise RuntimeError("archive-status sampling failed") from exc

    def _service_values(self) -> tuple[float, float, float]:
        runner = getattr(self.env, "_workload_runner", None)
        if runner is None:
            raise RuntimeError("shared workload runner is unavailable for service history sampling")
        try:
            activity = runner.get_observation_activity(limit=100)
            if not isinstance(activity, Mapping):
                raise RuntimeError(
                    f"shared workload runner returned a non-mapping activity payload: {activity!r}"
                )
            window_seconds = float(activity.get("window_seconds", 0.0))
            if window_seconds <= 0:
                raise RuntimeError("OLTP observation window has no elapsed time")
            values = activity.get("value", ())
            oltp = next(
                (
                    item for item in values
                    if isinstance(item, Mapping) and item.get("fingerprint") == OLTP_PROFILE_NAME
                ),
                None,
            )
            if oltp is None:
                raise RuntimeError(
                    f"OLTP workload profile is missing from activity history: profile={OLTP_PROFILE_NAME!r}"
                )
            total_calls = float(oltp.get("calls", 0))
            successful_calls = float(oltp.get("ok_calls", 0))
            # During container startup the shared workload may have one
            # failed probe and no completed transaction yet.  Keep the
            # sampler alive and expose an explicit zero-throughput sample;
            # later windows will contain the real OLTP measurements.
            if total_calls <= 0:
                return (0.0, 0.0, 0.0)
            p99 = float(oltp.get("p99_ms", 0.0) or 0.0)
            return (
                max(0.0, successful_calls / window_seconds),
                max(0.0, p99),
                min(1.0, max(0.0, successful_calls / total_calls if total_calls else 1.0)),
            )
        except Exception as exc:
            if isinstance(exc, RuntimeError):
                raise
            raise RuntimeError("shared workload service history sampling failed") from exc

    def sample_metrics(self, *, connection, timestamp_ms: int, elapsed_seconds: float, base_values) -> Mapping[str, Mapping[str, float]]:
        """Sample public counters from PostgreSQL and the shared workload runner."""
        interval = max(float(elapsed_seconds), 0.001)
        with self._lock:
            self._sample_count += 1
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT w.wal_bytes, w.wal_fpi, w.wal_records, "
                    "b.checkpoints_req, b.checkpoints_timed, b.checkpoint_write_time, b.checkpoint_sync_time, "
                    "a.archived_count, a.failed_count, "
                    "(SELECT COALESCE(sum(size), 0) FROM pg_ls_waldir()) "
                    "FROM pg_stat_wal w CROSS JOIN pg_stat_bgwriter b CROSS JOIN pg_stat_archiver a"
                )
                row = cursor.fetchone()
                cursor.execute(
                    "SELECT current_setting('checkpoint_timeout'), current_setting('max_wal_size'), "
                    "current_setting('checkpoint_completion_target'), current_setting('archive_command')"
                )
                settings_row = cursor.fetchone()
            if row is None or len(row) != 10:
                raise RuntimeError(f"checkpoint/archive counters returned an invalid row: {row!r}")
            if settings_row is None or len(settings_row) != 4:
                raise RuntimeError(f"checkpoint/archive settings returned an invalid row: {settings_row!r}")
            current = {
                "wal_bytes": float(row[0] or 0),
                "wal_fpi": float(row[1] or 0),
                "wal_records": float(row[2] or 0),
                "checkpoints_req": float(row[3] or 0),
                "checkpoints_timed": float(row[4] or 0),
                "checkpoint_write_ms": float(row[5] or 0),
                "checkpoint_sync_ms": float(row[6] or 0),
                "archived_count": float(row[7] or 0),
                "failed_count": float(row[8] or 0),
                "pg_wal_bytes": float(row[9] or 0),
            }
            settings = tuple(str(value) for value in (settings_row or ()))
            if len(settings) == 4 and settings != self._previous_settings:
                self._event(
                    timestamp_ms=timestamp_ms,
                    event_type="config_revision",
                    entity_type="database_config",
                    entity="postgres",
                    action="observed",
                    status="active",
                    correlation_id=f"config-{timestamp_ms}",
                    details={
                        "checkpoint_timeout": settings[0],
                        "max_wal_size": settings[1],
                        "checkpoint_completion_target": settings[2],
                        "archive_command": settings[3],
                    },
                )
                self._previous_settings = settings
            previous = self._previous
            wal_delta = {name: self._delta(current[name], previous.get(name) if previous else None) for name in (
                "wal_bytes", "wal_fpi", "wal_records",
            )}
            checkpoint_delta = {name: self._delta(current[name], previous.get(name) if previous else None) for name in (
                "checkpoints_req", "checkpoints_timed", "checkpoint_write_ms", "checkpoint_sync_ms",
            )}
            archived_delta = self._delta(current["archived_count"], previous.get("archived_count") if previous else None)
            failed_delta = self._delta(current["failed_count"], previous.get("failed_count") if previous else None)
            ready_files, oldest_age = self._archive_status(connection, timestamp_ms)
            rows = self._query_rows(connection, getattr(self.case, "write_table", ""))
            rows_delta = self._delta(rows, self._previous_rows)
            self._previous_rows = rows
            self._previous = current
            self._previous_timestamp_ms = timestamp_ms

            device_io_in_progress, device_weighted_io_ms = read_device_io_stats()
            previous_device_weighted_io_ms = self._previous_device_weighted_io_ms
            self._previous_device_weighted_io_ms = float(device_weighted_io_ms)

            if archived_delta:
                self._event(
                    timestamp_ms=timestamp_ms,
                    event_type="archive_attempt",
                    entity_type="archive_target",
                    entity=getattr(self.case, "archive_target_name", "archive"),
                    action="deliver",
                    status="completed",
                    correlation_id=f"archive-{timestamp_ms}",
                    details={"segment_count": archived_delta, "bytes": archived_delta * _SEGMENT_BYTES},
                )
            if failed_delta:
                self._event(
                    timestamp_ms=timestamp_ms,
                    event_type="archive_attempt",
                    entity_type="archive_target",
                    entity=getattr(self.case, "archive_target_name", "archive"),
                    action="retry",
                    status="failed",
                    correlation_id=f"archive-retry-{timestamp_ms}",
                    details={"attempt_count": failed_delta},
                )

            disk_io = base_values.get("disk_io")
            if disk_io is None:
                if self._sample_count > 1:
                    raise RuntimeError("shared disk_io history sample is missing after the initial baseline")
                read_rate = write_rate = 0.0
            else:
                if not isinstance(disk_io, Mapping) or not {"read_mb_per_second", "write_mb_per_second"}.issubset(disk_io):
                    raise RuntimeError(f"shared disk_io history sample is malformed: {disk_io!r}")
                read_rate = float(disk_io["read_mb_per_second"])
                write_rate = float(disk_io["write_mb_per_second"])
            if getattr(self.env, "_workload_runner", None) is None:
                # configure_history_observability resets deployment-time
                # samples before the real capture. The shared runner is
                # attached immediately after that reset.
                tps, p99, success_ratio = 0.0, 0.0, 1.0
            else:
                tps, p99, success_ratio = self._service_values()
            return {
                "wal_generation": {
                    "bytes_per_sec": wal_delta["wal_bytes"] / interval,
                    "fpi_per_sec": wal_delta["wal_fpi"] / interval,
                    "records_per_sec": wal_delta["wal_records"] / interval,
                },
                "checkpoint_activity": {
                    "requested_per_min": checkpoint_delta["checkpoints_req"] * 60.0 / interval,
                    "timed_per_min": checkpoint_delta["checkpoints_timed"] * 60.0 / interval,
                    "write_ms_per_sec": checkpoint_delta["checkpoint_write_ms"] / interval,
                    "sync_ms_per_sec": checkpoint_delta["checkpoint_sync_ms"] / interval,
                },
                "archive_delivery": {
                    "bytes_per_sec": archived_delta * _SEGMENT_BYTES / interval,
                    "success_delta": archived_delta / interval,
                    "failure_delta": failed_delta / interval,
                    "retry_count": failed_delta,
                },
                "archive_backlog": {
                    "ready_files": ready_files,
                    "oldest_age_sec": oldest_age,
                    "pg_wal_bytes": current["pg_wal_bytes"],
                },
                "storage_pressure": {
                    "read_mb_per_sec": max(0.0, read_rate),
                    "write_mb_per_sec": max(0.0, write_rate),
                    "checkpoint_io_time_ms_per_sec": (
                        checkpoint_delta["checkpoint_write_ms"] + checkpoint_delta["checkpoint_sync_ms"]
                    ) / interval,
                    "device_io_in_progress": float(device_io_in_progress),
                    "device_weighted_io_ms_per_sec": self._delta(
                        float(device_weighted_io_ms), previous_device_weighted_io_ms
                    ) / interval,
                },
                "service_slo": {
                    "transactions_per_sec": max(0.0, tps),
                    "p99_ms": max(0.0, p99),
                    "success_ratio": min(1.0, max(0.0, success_ratio)),
                },
                "batch_progress": {
                    "rows_per_sec": rows_delta / interval,
                    "completed_units": rows,
                    "deadline_remaining_sec": max(0.0, 600.0 - self._sample_count * interval),
                },
            }


__all__ = ["CheckpointArchiveHistoryAdapter"]
