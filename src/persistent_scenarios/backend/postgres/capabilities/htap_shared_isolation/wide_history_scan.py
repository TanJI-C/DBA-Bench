"""Capability: analysis tenant submits wide-range history scans.

A legitimate business-input change; it becomes harmful only in combination
with the stuck snapshot, churn and retry events. Always applied (rows land in
the public queue); no injector-owned session exists.
"""

from __future__ import annotations

from typing import Any, Mapping

from src.persistent_scenarios.backend.contracts import EventActivationContext, EventAlertPayload

from .base import (
    CoreProtocolCapability,
    HtapCapabilityHandle,
    injection_failed,
    shared,
)


class WideHistoryScanCapability(CoreProtocolCapability):
    capability_id = "htap_wide_history_scan"
    max_activation_seconds = 120

    def _resources(self, entity: str):
        return (shared(f"rows:analysis_jobs:{entity}", "business_input_rows"),)

    def _start(self, context: EventActivationContext) -> HtapCapabilityHandle:
        payload = context.event.payload
        tenant = str(payload["tenant"])
        scan_count = int(payload.get("scan_count", 2))
        handle = HtapCapabilityHandle(
            event_id=context.event.event_id,
            capability_id=self.capability_id,
            entity=context.event.entity,
            payload=payload,
        )
        connection = self._open_connection(context, "pg5r-htap3-capability-scan")
        job_ids: list[str] = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET ROLE htap_analyst;")
                for index in range(scan_count):
                    ref = f"{context.event.event_id}:{index}"
                    cursor.execute(
                        "INSERT INTO htap_analysis_jobs (ref, tenant, kind, range_start, range_end, deadline_at) "
                        "SELECT %s, %s, 'scan', "
                        "(SELECT COALESCE(max(line_id), 1) - %s FROM htap_order_lines), "
                        "(SELECT COALESCE(max(line_id), 0) FROM htap_order_lines), "
                        "clock_timestamp() + interval '30 minutes' RETURNING job_id;",
                        (ref, tenant, int(payload.get("scan_span_lines", 600_000))),
                    )
                    job_ids.append(str(cursor.fetchone()[0]))
            connection.commit()
        finally:
            connection.close()
        handle.facts = {"tenant": tenant, "job_ids": job_ids}
        return handle

    def _await_impact(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> Mapping[str, Any]:
        facts = self._job_facts(context, handle)
        if facts["job_count"] != len(handle.facts["job_ids"]):
            raise injection_failed(
                handle,
                f"scan submissions missing from the public queue: submitted={handle.facts['job_ids']!r}, facts={facts!r}",
            )
        handle.facts.update(facts)
        return dict(handle.facts)

    def _alert(self, handle: HtapCapabilityHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title=(
                "An analytics tenant expanded its reporting to wide historical order-line scans. "
                "Watch I/O, cache behaviour and order/dashboard latency while the scans run."
            ),
            symptoms=("wide historical scans from a new analysis tenant", "elevated read I/O"),
            severity="info",
            category="analysis_load",
        )

    def assert_clean(self, handle: HtapCapabilityHandle) -> Mapping[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}

    def _job_facts(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> dict[str, Any]:
        refs = [f"{handle.event_id}:{index}" for index in range(len(handle.facts["job_ids"]))]
        connection = self._open_connection(context, "pg5r-htap3-capability-scan-facts")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT ref, state FROM htap_analysis_jobs WHERE ref = ANY(%s) ORDER BY job_id;",
                    (refs,),
                )
                rows = cursor.fetchall()
            connection.rollback()
        finally:
            connection.close()
        states = {str(row[0]): str(row[1]) for row in rows}
        return {
            "job_count": len(rows),
            "job_states": states,
            "terminal_job_count": sum(1 for state in states.values() if state in {"done", "cancelled", "deadline_missed"}),
        }
