"""PostgreSQL PersistentScenario trusted telemetry provider."""

from __future__ import annotations

import time

import psycopg2

from src.persistent_scenarios.runtime.telemetry import TelemetryRuntime


class PostgresTelemetryProvider:
    _RECONNECT_WINDOW_SECONDS = 90.0
    _RECONNECT_INTERVAL_SECONDS = 0.5

    def create_runtime(self, environment, spec, run_id: str, clock, *, persistent_scenario_started: float):
        def sample_once():
            connection = environment.open_workload_connection("persistent_scenario-trusted-telemetry")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT count(*) FILTER (WHERE state = 'active'), "
                        "count(*) FILTER (WHERE state = 'idle in transaction' AND backend_xmin IS NOT NULL) "
                        "FROM pg_stat_activity WHERE pid <> pg_backend_pid();"
                    )
                    row = cursor.fetchone()
                connection.rollback()
            finally:
                connection.close()
            return {
                "active_connection_count": int(row[0]),
                "stale_backend_xmin_holder_count": int(row[1]),
            }

        def sample():
            deadline = time.monotonic() + self._RECONNECT_WINDOW_SECONDS
            while True:
                try:
                    return sample_once()
                except psycopg2.OperationalError as exc:
                    if time.monotonic() >= deadline:
                        raise RuntimeError(
                            "PostgreSQL trusted telemetry could not reconnect after a transient database restart"
                        ) from exc
                    time.sleep(self._RECONNECT_INTERVAL_SECONDS)

        return TelemetryRuntime(sample, interval_seconds=2.0, clock=clock)
