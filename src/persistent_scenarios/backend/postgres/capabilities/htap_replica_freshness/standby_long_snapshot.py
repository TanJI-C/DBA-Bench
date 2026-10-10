"""Capability: a standby report client opens a long REPEATABLE READ snapshot
and idles. Under the preconfigured standby policy this blocks replay and turns
later primary cleanup WAL into real recovery conflicts.
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
    PreventedActivation,
    exclusive,
    injection_failed,
)

APP = "pg5r-htap4-capability-long-snapshot"
KEEPALIVE_INTERVAL_SECONDS = 15.0
SNAPSHOT_SPAN_ROWS = 50000


class StandbyLongSnapshotCapability(CoreProtocolCapability):
    capability_id = "frs_standby_long_snapshot"
    max_activation_seconds = 180

    def _resources(self, entity: str):
        return (exclusive(f"session:standby-snapshot:{entity}", "database_session"),)

    def _open_standby(self, context: EventActivationContext, application: str):
        return context.environment.open_workload_connection(application, "standby")

    def _start(self, context: EventActivationContext) -> HtapCapabilityHandle:
        handle = HtapCapabilityHandle(
            event_id=context.event.event_id,
            capability_id=self.capability_id,
            entity=context.event.entity,
            payload=context.event.payload,
        )
        handle.runtime_state["session_facts_fn"] = self._session_facts_factory(context)
        thread = threading.Thread(
            target=self._hold_snapshot, args=(context, handle), name=f"pg5r-htap4-longsnap-{context.event.event_id}", daemon=True
        )
        handle.sessions.append(thread)
        thread.start()
        return handle

    def _session_facts_factory(self, context: EventActivationContext) -> Callable[[], dict[str, Any]]:
        def read() -> dict[str, Any]:
            connection = self._open_standby(context, "pg5r-htap4-capability-snapshot-facts")
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SET statement_timeout = '10s';")
                    cursor.execute(
                        "SELECT count(*), COALESCE(max(age(backend_xmin)), 0) "
                        f"FROM pg_stat_activity WHERE application_name = '{APP}' AND backend_xmin IS NOT NULL;"
                    )
                    row = cursor.fetchone()
                    cursor.execute("SHOW max_standby_streaming_delay;")
                    delay = str(cursor.fetchone()[0])
                    cursor.execute("SHOW hot_standby_feedback;")
                    feedback = str(cursor.fetchone()[0])
                connection.rollback()
            finally:
                connection.close()
            return {
                "standby_snapshot_session_count": int(row[0]),
                "standby_snapshot_xmin_transactions": int(row[1]),
                "max_standby_streaming_delay": delay,
                "hot_standby_feedback": feedback,
            }

        return read

    def _hold_snapshot(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> None:
        try:
            connection = self._open_standby(context, APP)
        except psycopg2.Error as exc:
            handle.facts["phase"] = "connection_refused"
            handle.facts["error"] = repr(exc)
            return
        try:
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_is_in_recovery(), inet_server_port(), current_user, "
                               "(SELECT count(*) FROM pg_roles WHERE rolname = 'frs_report');")
                identity = cursor.fetchone()
                handle.facts["connection_identity"] = {
                    "in_recovery": str(identity[0]),
                    "port": str(identity[1]),
                    "user": str(identity[2]),
                    "frs_report_role_count": int(identity[3]),
                }
            connection.autocommit = False
        except psycopg2.Error as exc:
            handle.facts["identity_error"] = repr(exc)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
                cursor.execute("SET ROLE frs_report;")
                cursor.execute("SELECT pg_is_in_recovery(), inet_server_port(), current_user;")
                identity = cursor.fetchone()
                handle.facts["connection_identity"] = {
                    "in_recovery": str(identity[0]),
                    "port": str(identity[1]),
                    "effective_role": str(identity[2]),
                }
                cursor.execute(
                    "SELECT count(*), COALESCE(max(order_id), 0) FROM ("
                    "SELECT order_id FROM frs_order_events ORDER BY event_id LIMIT %s) page;",
                    (SNAPSHOT_SPAN_ROWS,),
                )
                page_rows, max_order = cursor.fetchone()
                cursor.execute("SELECT pg_current_snapshot(), pg_last_wal_replay_lsn();")
                snapshot_text, replay_lsn = cursor.fetchone()
            # The REPEATABLE READ transaction stays open: keeping it idle is
            # exactly what blocks replay on the standby.
            handle.facts["phase"] = "holding"
            handle.facts["snapshot"] = str(snapshot_text)
            handle.facts["page_rows"] = int(page_rows)
            handle.facts["page_max_order_id"] = int(max_order)
            handle.facts["snapshot_replay_lsn"] = str(replay_lsn)
            max_hold_seconds = float(handle.payload.get("max_hold_seconds", 1800))
            started = context.clock.monotonic()
            while not handle.stop.is_set():
                if context.clock.monotonic() - started >= max_hold_seconds:
                    handle.facts["phase"] = "released_naturally"
                    break
                if handle.stop.wait(KEEPALIVE_INTERVAL_SECONDS):
                    break
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1;")
                except psycopg2.Error as exc:
                    handle.facts["phase"] = "terminated_by_server"
                    handle.facts["error"] = repr(exc)
                    return
            if handle.facts["phase"] == "holding":
                handle.facts["phase"] = "released_by_cleanup"
        finally:
            try:
                connection.rollback()
                connection.close()
            except psycopg2.Error:
                pass

    def _await_impact(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> Mapping[str, Any]:
        started = context.clock.monotonic()
        while context.clock.monotonic() - started < 60.0:
            if handle.facts.get("phase") in {"holding", "terminated_by_server", "connection_refused", "failed"}:
                break
            time.sleep(0.2)
        handle.facts["await_elapsed_seconds"] = round(context.clock.monotonic() - started, 1)
        handle.facts["holder_thread_alive"] = handle.sessions[0].is_alive() if handle.sessions else False
        facts = handle.runtime_state["session_facts_fn"]()
        handle.facts.update(facts)
        if facts["standby_snapshot_session_count"] >= 1:
            handle.facts["outcome_kind"] = "applied"
            return dict(handle.facts)
        if handle.facts.get("phase") == "terminated_by_server":
            raise PreventedActivation(
                mechanism="standby_snapshot_terminated_by_server",
                protection_state={
                    "max_standby_streaming_delay": facts["max_standby_streaming_delay"],
                    "hot_standby_feedback": facts["hot_standby_feedback"],
                    "phase": handle.facts.get("phase"),
                    "error": handle.facts.get("error"),
                },
            )
        raise injection_failed(
            handle,
            f"standby snapshot session is absent without an explanation, phase={handle.facts.get('phase')!r}, "
            f"holder_error={handle.facts.get('error')!r}, holder_alive={handle.facts.get('holder_thread_alive')!r}, "
            f"identity={handle.facts.get('connection_identity')!r}, identity_error={handle.facts.get('identity_error')!r}, "
            f"await_elapsed={handle.facts.get('await_elapsed_seconds')!r}, facts={facts!r}",
        )

    def _alert(self, handle: HtapCapabilityHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title=(
                "A report reader on the analytics replica is holding a long-open snapshot; replay may stall "
                "and report queries can be cancelled while it lasts."
            ),
            symptoms=("long-open report snapshot on the replica", "replay progress stalling"),
            severity="warning",
            category="replica_snapshot",
        )

    def assert_clean(self, handle: HtapCapabilityHandle) -> Mapping[str, object]:
        facts = handle.runtime_state["session_facts_fn"]()
        if facts["standby_snapshot_session_count"] != 0:
            raise RuntimeError(
                f"Standby long-snapshot session survived cleanup: event_id={handle.event_id!r}, facts={facts!r}"
            )
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}
