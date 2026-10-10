"""Capability: primary write/cleanup surge.

A bounded cohort increases order churn and generates real cleanup WAL
(DELETE + VACUUM on frs_order_events). When a standby snapshot holds an old
xmin, this WAL replays into genuine recovery conflicts on the standby.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable, Mapping

import psycopg2

from src.persistent_scenarios.backend.contracts import EventActivationContext, EventAlertPayload

from ..htap_shared_isolation.base import (
    CoreProtocolCapability,
    HtapCapabilityHandle,
    exclusive,
    injection_failed,
)

APP = "pg5r-htap4-capability-surge"
VACUUM_INTERVAL_SECONDS = 8.0


class PrimaryUpdateSurgeCapability(CoreProtocolCapability):
    capability_id = "frs_primary_update_surge"
    max_activation_seconds = 180

    def __init__(self, *, default_writer_count: int = 4, default_surge_seconds: int = 900, default_churn_qps: float = 30.0):
        self._default_writer_count = default_writer_count
        self._default_surge_seconds = default_surge_seconds
        self._default_churn_qps = default_churn_qps

    def _resources(self, entity: str):
        return (exclusive(f"cohort:surge:{entity}", "workload_cohort"),)

    def _start(self, context: EventActivationContext) -> HtapCapabilityHandle:
        payload = context.event.payload
        handle = HtapCapabilityHandle(
            event_id=context.event.event_id,
            capability_id=self.capability_id,
            entity=context.event.entity,
            payload=payload,
        )
        writer_count = int(payload.get("writer_count", self._default_writer_count))
        surge_seconds = float(payload.get("surge_seconds", self._default_surge_seconds))
        churn_qps = float(payload.get("churn_qps", self._default_churn_qps))
        handle.facts["writer_count"] = writer_count
        handle.runtime_state["counter_lock"] = threading.Lock()
        handle.runtime_state["churn_updates"] = 0
        handle.runtime_state["deadlock_retries"] = 0
        handle.runtime_state["vacuum_runs"] = 0

        def session_facts() -> dict[str, Any]:
            rows = context.environment.primary_sql(
                f"SELECT count(*) FROM pg_stat_activity WHERE application_name LIKE '{APP}%';"
            )
            wal = context.environment.primary_sql("SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0');")
            return {"surge_session_count": int(rows[0][0]), "primary_wal_generated_bytes": int(wal[0][0])}

        handle.runtime_state["session_facts_fn"] = session_facts
        started = time.monotonic()
        for index in range(writer_count):
            thread = threading.Thread(
                target=self._surge_writer,
                args=(context, handle, started, index, surge_seconds, churn_qps, writer_count),
                name=f"pg5r-htap4-surge-{context.event.event_id}-{index}",
                daemon=True,
            )
            handle.sessions.append(thread)
            thread.start()
        vacuum_thread = threading.Thread(
            target=self._vacuum_loop, args=(context, handle, started, surge_seconds),
            name=f"pg5r-htap4-vacuum-{context.event.event_id}", daemon=True,
        )
        handle.sessions.append(vacuum_thread)
        vacuum_thread.start()
        return handle

    def _surge_writer(self, context, handle, started, index, surge_seconds, churn_qps, writer_count) -> None:
        interval = 1.0 / (churn_qps / writer_count)
        next_at = time.monotonic() + index * interval
        connection = context.environment.open_workload_connection(APP, "primary")
        try:
            while not handle.stop.is_set() and time.monotonic() - started < surge_seconds:
                delay = next_at - time.monotonic()
                if delay > 0:
                    time.sleep(delay)
                next_at += interval
                try:
                    with connection.cursor() as cursor:
                        # Writers ship disjoint order_id partitions: a shared
                        # "oldest paid" window queues every writer on the same
                        # row locks and throughput collapses to a few ticks.
                        # Contention with the OLTP order path stays - that is
                        # the injected hotspot.
                        cursor.execute(
                            "UPDATE frs_orders SET status = 'shipped', updated_at = clock_timestamp() "
                            "WHERE order_id %% %s = %s AND order_id IN ("
                            "SELECT order_id FROM frs_orders WHERE status = 'paid' "
                            "ORDER BY updated_at LIMIT 8);",
                            (writer_count, index),
                        )
                        cursor.execute(
                            "INSERT INTO frs_order_events (order_id, kind) "
                            "SELECT (order_id %% 50000) + 1, 'surge' FROM frs_orders "
                            "WHERE order_id %% %s = %s "
                            "ORDER BY updated_at DESC LIMIT 16;",
                            (writer_count, index),
                        )
                    connection.commit()
                except psycopg2.errors.DeadlockDetected:
                    # A deadlock victim is an expected contention outcome of the
                    # injected update surge; a real client retries the tx.
                    connection.rollback()
                    with handle.runtime_state["counter_lock"]:
                        handle.runtime_state["deadlock_retries"] += 1
                except psycopg2.Error:
                    connection.rollback()
                    raise
                with handle.runtime_state["counter_lock"]:
                    handle.runtime_state["churn_updates"] += 1
        finally:
            connection.close()

    def _vacuum_loop(self, context, handle, started, surge_seconds) -> None:
        next_at = time.monotonic()
        while not handle.stop.is_set() and time.monotonic() - started < surge_seconds:
            delay = next_at - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            next_at += VACUUM_INTERVAL_SECONDS
            connection = context.environment.open_workload_connection(f"{APP}-vacuum", "primary")
            try:
                connection.autocommit = True
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM frs_order_events WHERE event_id % 3 = 0 AND kind = 'surge';")
                    cursor.execute("VACUUM frs_order_events;")
            finally:
                connection.close()
            with handle.runtime_state["counter_lock"]:
                handle.runtime_state["vacuum_runs"] += 1

    def _await_impact(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> Mapping[str, Any]:
        started = context.clock.monotonic()
        while context.clock.monotonic() < started + 60.0:
            with handle.runtime_state["counter_lock"]:
                if handle.runtime_state["churn_updates"] >= handle.facts["writer_count"] and handle.runtime_state["vacuum_runs"] >= 1:
                    break
            time.sleep(0.2)
        with handle.runtime_state["counter_lock"]:
            handle.facts["churn_updates"] = handle.runtime_state["churn_updates"]
            handle.facts["deadlock_retries"] = handle.runtime_state["deadlock_retries"]
            handle.facts["vacuum_runs"] = handle.runtime_state["vacuum_runs"]
        facts = handle.runtime_state["session_facts_fn"]()
        handle.facts.update(facts)
        if handle.facts["churn_updates"] <= 0 or handle.facts["vacuum_runs"] < 1:
            raise injection_failed(
                handle,
                f"surge produced no observable work within 60s: churn_updates={handle.facts['churn_updates']}, "
                f"vacuum_runs={handle.facts['vacuum_runs']}",
            )
        handle.facts["outcome_kind"] = "applied"
        return dict(handle.facts)

    def _alert(self, handle: HtapCapabilityHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title=(
                "Primary write volume is peaking and cleanup of expired order events is generating heavy "
                "WAL; replica replay progress and report freshness are at risk."
            ),
            symptoms=("primary write peak", "heavy cleanup WAL generation"),
            severity="warning",
            category="write_surge",
        )

    def assert_clean(self, handle: HtapCapabilityHandle) -> Mapping[str, object]:
        facts = handle.runtime_state["session_facts_fn"]()
        if facts["surge_session_count"] != 0:
            raise RuntimeError(f"Surge cohort survived cleanup: event_id={handle.event_id!r}, facts={facts!r}")
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}
