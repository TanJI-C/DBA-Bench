"""Capability: transaction write hotspot amplification.

A bounded cohort of churn writers hammers hot inventory rows and order status
transitions. This is a production traffic change: cleanup debt only becomes
harmful when an old snapshot (xmin) blocks vacuum.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable, Mapping

import psycopg2

from src.persistent_scenarios.backend.contracts import EventActivationContext, EventAlertPayload

from .base import (
    CoreProtocolCapability,
    HtapCapabilityHandle,
    exclusive,
    injection_failed,
)

APP = "pg5r-htap3-capability-churn"


class HotspotChurnCapability(CoreProtocolCapability):
    capability_id = "htap_hotspot_churn"
    max_activation_seconds = 180

    def __init__(self, *, default_writer_count: int = 4, default_churn_seconds: int = 1200, default_churn_qps: float = 24.0):
        self._default_writer_count = default_writer_count
        self._default_churn_seconds = default_churn_seconds
        self._default_churn_qps = default_churn_qps

    def _resources(self, entity: str):
        return (exclusive(f"cohort:churn:{entity}", "workload_cohort"),)

    def _start(self, context: EventActivationContext) -> HtapCapabilityHandle:
        payload = context.event.payload
        handle = HtapCapabilityHandle(
            event_id=context.event.event_id,
            capability_id=self.capability_id,
            entity=context.event.entity,
            payload=payload,
        )
        writer_count = int(payload.get("writer_count", self._default_writer_count))
        churn_seconds = float(payload.get("churn_seconds", self._default_churn_seconds))
        churn_qps = float(payload.get("churn_qps", self._default_churn_qps))
        handle.runtime_state["counter_lock"] = threading.Lock()
        handle.runtime_state["churn_updates"] = 0
        handle.runtime_state["deadlock_retries"] = 0
        handle.facts["writer_count"] = writer_count

        def session_facts() -> dict[str, Any]:
            connection = self._open_connection(context, "pg5r-htap3-capability-churn-facts")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT count(*) FROM pg_stat_activity WHERE application_name = %s;", (APP,)
                    )
                    sessions = int(cursor.fetchone()[0])
                connection.rollback()
            finally:
                connection.close()
            return {"churn_session_count": sessions}

        handle.runtime_state["session_facts_fn"] = session_facts
        started = context.clock.monotonic()
        for index in range(writer_count):
            thread = threading.Thread(
                target=self._churn_writer,
                args=(context, handle, started, index, churn_seconds, churn_qps, writer_count),
                name=f"pg5r-htap3-churn-{context.event.event_id}-{index}",
                daemon=True,
            )
            handle.sessions.append(thread)
            thread.start()
        return handle

    def _churn_writer(self, context, handle, started, index, churn_seconds, churn_qps, writer_count) -> None:
        interval = 1.0 / (churn_qps / writer_count)
        next_at = time.monotonic() + index * interval
        try:
            connection = self._open_connection(context, APP)
        except psycopg2.Error as exc:
            handle.facts["phase"] = "connection_refused"
            handle.facts["error"] = repr(exc)
            return
        try:
            while not handle.stop.is_set() and time.monotonic() - started < churn_seconds:
                delay = next_at - time.monotonic()
                if delay > 0:
                    time.sleep(delay)
                next_at += interval
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("SET ROLE htap_oltp;")
                        cursor.execute(
                            "UPDATE htap_inventory SET on_hand = on_hand + 1 "
                            "WHERE sku IN (SELECT sku FROM htap_inventory ORDER BY (sku * 13) %% 7 LIMIT %s);",
                            (6,),
                        )
                        cursor.execute(
                            "UPDATE htap_orders SET status = 'shipped', updated_at = clock_timestamp() "
                            "WHERE order_id IN ("
                            "SELECT order_id FROM htap_orders WHERE status = 'paid' "
                            "ORDER BY updated_at LIMIT 8);"
                        )
                    connection.commit()
                except psycopg2.errors.DeadlockDetected:
                    # A deadlock victim is an expected contention outcome of the
                    # injected hotspot; a real client retries the transaction.
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

    def _await_impact(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> Mapping[str, Any]:
        started = context.clock.monotonic()
        while context.clock.monotonic() < started + 60.0:
            with handle.runtime_state["counter_lock"]:
                if handle.runtime_state["churn_updates"] >= handle.facts["writer_count"]:
                    break
            time.sleep(0.2)
        with handle.runtime_state["counter_lock"]:
            handle.facts["churn_updates"] = handle.runtime_state["churn_updates"]
            handle.facts["deadlock_retries"] = handle.runtime_state["deadlock_retries"]
        facts = handle.runtime_state["session_facts_fn"]()
        handle.facts.update(facts)
        if handle.facts["churn_updates"] <= 0 or facts["churn_session_count"] <= 0:
            raise injection_failed(
                handle,
                f"hotspot churn produced no observable updates: churn_updates={handle.facts['churn_updates']}, "
                f"churn_session_count={facts['churn_session_count']}, phase={handle.facts.get('phase')!r}",
            )
        handle.facts["outcome_kind"] = "applied"
        return dict(handle.facts)

    def _alert(self, handle: HtapCapabilityHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title=(
                "Order submission volume shifted onto a narrow set of hot SKUs; row-update contention and "
                "dead-tuple generation on the order path are rising."
            ),
            symptoms=("hot-row update contention", "dead tuple generation increasing"),
            severity="warning",
            category="write_hotspot",
        )

    def assert_clean(self, handle: HtapCapabilityHandle) -> Mapping[str, object]:
        facts = handle.runtime_state["session_facts_fn"]()
        if facts["churn_session_count"] != 0:
            raise RuntimeError(f"Hotspot churn cohort survived cleanup: event_id={handle.event_id!r}, facts={facts!r}")
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}
