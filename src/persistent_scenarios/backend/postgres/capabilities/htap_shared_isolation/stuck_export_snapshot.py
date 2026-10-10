"""Capability: an export consumer cohort opens its export window. One client
stops consuming right after its first page and holds a long REPEATABLE READ
snapshot, pinning the cluster-wide xmin so vacuum cleanup falls behind; its
sibling keeps consuming properly (one short snapshot per page) and is the
legitimate look-alike in pg_stat_activity. The alert reports symptoms only:
attributing the pinned-xmin holder and separating its bloat growth from the
churn dead-tuple volume is the diagnosis work.
"""

from __future__ import annotations

import hashlib
import threading
import time
from typing import Any, Callable, Mapping

import psycopg2

from src.persistent_scenarios.backend.contracts import EventActivationContext, EventAlertPayload
from src.persistent_scenarios.backend.postgres.workloads.htap_common.pg_values import interval_seconds

from .base import (
    CoreProtocolCapability,
    HtapCapabilityHandle,
    PreventedActivation,
    exclusive,
    injection_failed,
)

APP = "dw-export-consumer"
KEEPALIVE_INTERVAL_SECONDS = 20.0
CONSUMER_PAGE_SIZE = 50_000
CONSUMER_PAGE_PAUSE_SECONDS = 60.0


class StuckExportSnapshotCapability(CoreProtocolCapability):
    capability_id = "htap_stuck_export_snapshot"
    max_activation_seconds = 180

    def _resources(self, entity: str):
        return (exclusive(f"session:stuck-export:{entity}", "database_session"),)

    def _start(self, context: EventActivationContext) -> HtapCapabilityHandle:
        handle = HtapCapabilityHandle(
            event_id=context.event.event_id,
            capability_id=self.capability_id,
            entity=context.event.entity,
            payload=context.event.payload,
        )
        handle.runtime_state["session_facts_fn"] = self._session_facts_factory(context)
        threads = (
            threading.Thread(
                target=self._hold_snapshot, args=(context, handle), name=f"pg5r-htap3-stuck-{context.event.event_id}", daemon=True
            ),
            threading.Thread(
                target=self._consume_pages, args=(context, handle), name=f"pg5r-htap3-consumer-{context.event.event_id}", daemon=True
            ),
        )
        for thread in threads:
            handle.sessions.append(thread)
            thread.start()
        return handle

    def _session_facts_factory(self, context: EventActivationContext) -> Callable[[], dict[str, Any]]:
        def read() -> dict[str, Any]:
            connection = self._open_connection(context, "pg5r-htap3-stuck-facts")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT count(*) FILTER (WHERE state = 'idle in transaction' AND backend_xmin IS NOT NULL), "
                        "count(*) FILTER (WHERE state <> 'idle in transaction') "
                        "FROM pg_stat_activity WHERE application_name = %s;",
                        (APP,),
                    )
                    row = cursor.fetchone()
                    cursor.execute(
                        "SELECT COALESCE((SELECT option FROM unnest(COALESCE(rolconfig, '{}')) AS option "
                        "WHERE option LIKE 'idle_in_transaction_session_timeout=%'), '0') "
                        "FROM pg_roles WHERE rolname = 'htap_analyst';"
                    )
                    role_timeout_row = cursor.fetchone()
                    role_timeout_value = (
                        str(role_timeout_row[0]).split("=", 1)[1]
                        if role_timeout_row and "=" in str(role_timeout_row[0])
                        else "0"
                    )
                    role_timeout_ms = int(interval_seconds(role_timeout_value) * 1000)
                    cursor.execute("SHOW idle_in_transaction_session_timeout;")
                    global_timeout_ms = int(interval_seconds(str(cursor.fetchone()[0])) * 1000)
                connection.rollback()
            finally:
                connection.close()
            return {
                "stuck_session_count": int(row[0]),
                "consuming_session_count": int(row[1]),
                "analyst_idle_in_tx_timeout_ms": role_timeout_ms,
                "global_idle_in_tx_timeout_ms": global_timeout_ms,
            }

        return read

    def _hold_snapshot(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> None:
        try:
            connection = self._open_connection(context, APP)
        except psycopg2.Error as exc:
            handle.facts["phase"] = "connection_refused"
            handle.facts["error"] = repr(exc)
            return
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET ROLE htap_analyst;")
            connection.commit()
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
                cursor.execute(
                    "SELECT count(*), COALESCE(max(line_id), 0) FROM ("
                    "SELECT line_id FROM htap_order_lines ORDER BY line_id LIMIT 50000) page;"
                )
                page_rows, max_line = cursor.fetchone()
                cursor.execute("SELECT pg_current_snapshot();")
                snapshot_text = str(cursor.fetchone()[0])
            # The REPEATABLE READ transaction stays open idle: keeping it idle is
            # exactly what pins the cluster-wide xmin.
            handle.facts["phase"] = "holding"
            handle.facts["snapshot"] = snapshot_text
            handle.facts["page_rows"] = int(page_rows)
            handle.facts["page_max_line_id"] = int(max_line)
            max_hold_seconds = float(handle.payload.get("max_hold_seconds", 1320))
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

    def _consume_pages(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> None:
        """The sibling consumer that keeps working: one short REPEATABLE READ
        transaction per checkpointed page, snapshot released between pages. Its
        pg_stat_activity row never carries an old backend_xmin; killing it with
        the holder breaks a live consumer instead of repairing the pin."""
        try:
            connection = self._open_connection(context, APP)
        except psycopg2.Error as exc:
            handle.facts["consumer_phase"] = "connection_refused"
            handle.facts["consumer_error"] = repr(exc)
            return
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET ROLE htap_analyst;")
                cursor.execute("SELECT COALESCE(max(watermark_seq), 0) FROM htap_commit_watermark;")
                watermark_seq = int(cursor.fetchone()[0])
                binding = f"dw-export-lines-w{watermark_seq}"
                cursor.execute(
                    "SELECT COALESCE(max(last_line_id), 0) FROM htap_export_checkpoints WHERE export_id = %s;",
                    (binding,),
                )
                last_line_id = int(cursor.fetchone()[0])
            connection.commit()
            handle.facts["consumer_binding"] = binding
            handle.facts["consumer_phase"] = "consuming"
            consume_rows = int(handle.payload.get("consume_rows", 200_000))
            page_pause = float(handle.payload.get("consume_page_pause_seconds", CONSUMER_PAGE_PAUSE_SECONDS))
            consumed = 0
            while not handle.stop.is_set() and consumed < consume_rows:
                if handle.stop.wait(page_pause):
                    break
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT line_id, order_id, sku, qty, price FROM htap_order_lines "
                        "WHERE line_id > %s ORDER BY line_id LIMIT %s;",
                        (last_line_id, CONSUMER_PAGE_SIZE),
                    )
                    rows = cursor.fetchall()
                    if not rows:
                        handle.facts["consumer_phase"] = "completed"
                        return
                    page_digest = hashlib.sha256(
                        "\n".join("|".join(str(value) for value in row) for row in rows).encode("utf-8")
                    ).hexdigest()
                    cursor.execute(
                        "INSERT INTO htap_export_checkpoints (export_id, watermark_seq, last_line_id, page_digest, page_rows) "
                        "VALUES (%s, %s, %s, %s, %s);",
                        (binding, watermark_seq, int(rows[-1][0]), page_digest, len(rows)),
                    )
                connection.commit()
                consumed += len(rows)
                last_line_id = int(rows[-1][0])
                handle.facts["consumer_last_line_id"] = last_line_id
            if handle.facts.get("consumer_phase") == "consuming":
                handle.facts["consumer_phase"] = "completed"
        except psycopg2.Error as exc:
            handle.facts["consumer_phase"] = "terminated_by_server"
            handle.facts["consumer_error"] = repr(exc)
        finally:
            try:
                connection.rollback()
                connection.close()
            except psycopg2.Error:
                pass

    def _await_impact(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> Mapping[str, Any]:
        deadline = context.clock.monotonic() + 60.0
        while context.clock.monotonic() < deadline:
            if handle.facts.get("phase") in {"holding", "terminated_by_server", "connection_refused"}:
                break
            time.sleep(0.2)
        facts = handle.runtime_state["session_facts_fn"]()
        handle.facts.update(facts)
        if facts["stuck_session_count"] >= 1:
            handle.facts["outcome_kind"] = "applied"
            return dict(handle.facts)
        if (
            handle.facts.get("phase") == "terminated_by_server"
            and max(facts["analyst_idle_in_tx_timeout_ms"], facts["global_idle_in_tx_timeout_ms"]) > 0
        ):
            raise PreventedActivation(
                mechanism="idle_in_transaction_session_timeout",
                protection_state={
                    "analyst_idle_in_tx_timeout_ms": facts["analyst_idle_in_tx_timeout_ms"],
                    "global_idle_in_tx_timeout_ms": facts["global_idle_in_tx_timeout_ms"],
                    "phase": handle.facts.get("phase"),
                },
            )
        raise injection_failed(
            handle,
            f"snapshot session is absent without a protection explanation, phase={handle.facts.get('phase')!r}, "
            f"idle_in_tx_timeouts=({facts['analyst_idle_in_tx_timeout_ms']}, {facts['global_idle_in_tx_timeout_ms']})",
        )

    def _alert(self, handle: HtapCapabilityHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title=(
                "Dead tuples on the order tables keep climbing and vacuum cleanup is not advancing; "
                "export page progress has stalled and order latency is drifting up."
            ),
            symptoms=(
                "dead tuples growing on the order tables",
                "vacuum cleanup not advancing",
                "export page progress stalled",
            ),
            severity="warning",
            category="bloat_cleanup",
        )

    def assert_clean(self, handle: HtapCapabilityHandle) -> Mapping[str, object]:
        facts = handle.runtime_state["session_facts_fn"]()
        if facts["stuck_session_count"] != 0 or facts["consuming_session_count"] != 0:
            raise RuntimeError(
                f"Stuck export consumer sessions survived cleanup: event_id={handle.event_id!r}, facts={facts!r}"
            )
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}
