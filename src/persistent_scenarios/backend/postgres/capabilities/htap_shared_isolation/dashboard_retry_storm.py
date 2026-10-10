"""Capability: the dashboard tier's newest client release (v2.4.1-rc3) shipped
a retry/backoff parameter regression; timeouts on the shared instance are
amplified into a dense-but-bounded retry storm. The DB-side symptom face (far
too many short aggregation reads) looks like an attack or a database bug; the
root cause lives in the client release, published into htap_release_audit, and
in the release-tagged session identity. The cohort honors the public
dashboard_max_concurrency budget: admitting fewer sessions clamps the storm —
the DB-side repair — while the client rollback itself stays outside the
database authorization boundary.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Mapping

import psycopg2

from src.persistent_scenarios.backend.contracts import EventActivationContext, EventAlertPayload

from .base import (
    CoreProtocolCapability,
    HtapCapabilityHandle,
    PreventedActivation,
    exclusive,
    injection_failed,
)

RELEASE_TAG = "v2.4.1-rc3"
PREVIOUS_CONFIG = '{"retry_max": 1, "retry_backoff_ms": 2000}'
STORM_CONFIG = '{"retry_max": 3, "retry_backoff_ms": 10}'
APP = f"dashboard-edge/{RELEASE_TAG}"
RETRIES_PER_FAILURE = 3
QUERY_TIMEOUT_MS = 300
GOVERNANCE_REFRESH_SECONDS = 5.0


class DashboardRetryStormCapability(CoreProtocolCapability):
    capability_id = "htap_dashboard_retry_storm"
    max_activation_seconds = 180

    def __init__(self, *, default_cohort_size: int = 3, default_storm_seconds: int = 480, default_retry_qps: float = 6.0):
        self._default_cohort_size = default_cohort_size
        self._default_storm_seconds = default_storm_seconds
        self._default_retry_qps = default_retry_qps

    def _resources(self, entity: str):
        return (exclusive(f"cohort:retry:{entity}", "workload_cohort"),)

    def _start(self, context: EventActivationContext) -> HtapCapabilityHandle:
        payload = context.event.payload
        handle = HtapCapabilityHandle(
            event_id=context.event.event_id,
            capability_id=self.capability_id,
            entity=context.event.entity,
            payload=payload,
        )
        cohort_size = int(payload.get("cohort_size", self._default_cohort_size))
        storm_seconds = float(payload.get("storm_seconds", self._default_storm_seconds))
        retry_qps = float(payload.get("retry_qps", self._default_retry_qps))
        handle.facts["cohort_size"] = cohort_size
        handle.facts["release_tag"] = RELEASE_TAG
        handle.runtime_state["counter_lock"] = threading.Lock()
        handle.runtime_state["attempts"] = 0
        handle.runtime_state["governance"] = {"lock": threading.Lock(), "limit": None, "read_at": 0.0}
        self._publish_release_audit(context)

        def session_facts() -> dict[str, Any]:
            connection = self._open_connection(context, "pg5r-htap3-retry-facts")
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE application_name = %s;", (APP,))
                    sessions = int(cursor.fetchone()[0])
                connection.rollback()
            finally:
                connection.close()
            return {"retry_session_count": sessions}

        handle.runtime_state["session_facts_fn"] = session_facts
        interval = 1.0 / retry_qps
        started = context.clock.monotonic()
        for index in range(cohort_size):
            thread = threading.Thread(
                target=self._retry_worker,
                args=(context, handle, started, index, interval, storm_seconds),
                name=f"pg5r-htap3-retry-{context.event.event_id}-{index}",
                daemon=True,
            )
            handle.sessions.append(thread)
            thread.start()
        return handle

    def _publish_release_audit(self, context: EventActivationContext) -> None:
        """The client release precedes the storm: its config change lands in the
        public release audit trail as the cross-system attribution artifact."""
        connection = self._open_connection(context, "pg5r-htap3-retry-release")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO htap_release_audit (component, release_tag, old_config, new_config) "
                    "VALUES (%s, %s, %s, %s) ON CONFLICT (component, release_tag) DO NOTHING;",
                    ("dashboard_edge", RELEASE_TAG, PREVIOUS_CONFIG, STORM_CONFIG),
                )
            connection.commit()
        finally:
            connection.close()

    def _read_dashboard_limit(self, context: EventActivationContext) -> int:
        connection = self._open_connection(context, "pg5r-htap3-retry-control")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT control_value FROM htap_work_control WHERE control_key = 'dashboard_max_concurrency';"
                )
                row = cursor.fetchone()
            connection.rollback()
        finally:
            connection.close()
        if row is None:
            raise ValueError(
                "dashboard_max_concurrency control key is missing from htap_work_control: "
                f"event_id={context.event.event_id!r}"
            )
        return int(str(row[0]))

    def _dashboard_limit(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> int:
        """The dashboard edge tier honors the public ops budget with a short TTL
        cache, so a governance update reaches the running cohort."""
        state = handle.runtime_state["governance"]
        now = time.monotonic()
        with state["lock"]:
            if state["limit"] is None or now - state["read_at"] >= GOVERNANCE_REFRESH_SECONDS:
                state["limit"] = self._read_dashboard_limit(context)
                state["read_at"] = now
                handle.facts["dashboard_max_concurrency_effective"] = state["limit"]
            return int(state["limit"])

    def _retry_worker(self, context, handle, started, index, interval, storm_seconds) -> None:
        next_at = time.monotonic() + index * interval
        try:
            connection = self._open_connection(context, APP)
        except psycopg2.Error as exc:
            handle.facts["phase"] = "connection_refused"
            handle.facts["error"] = repr(exc)
            return
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET ROLE htap_dashboard;")
            connection.commit()
            while not handle.stop.is_set() and time.monotonic() - started < storm_seconds:
                if index >= self._dashboard_limit(context, handle):
                    # Governance clamp: the edge tier admits only the configured
                    # number of concurrent clients; clamped clients stay
                    # connected but emit nothing.
                    handle.stop.wait(1.0)
                    continue
                delay = next_at - time.monotonic()
                if delay > 0:
                    time.sleep(delay)
                next_at += interval
                failures_left = RETRIES_PER_FAILURE
                while failures_left >= 0:
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(f"SET statement_timeout = {QUERY_TIMEOUT_MS};")
                            cursor.execute(
                                "SELECT count(*), COALESCE(sum(amount), 0.0) FROM htap_orders "
                                "WHERE status = 'paid' AND created_at > clock_timestamp() - interval '60 seconds';"
                            )
                            cursor.fetchone()
                        connection.rollback()
                        break
                    except psycopg2.Error:
                        connection.rollback()
                        failures_left -= 1
                        if failures_left < 0:
                            break
                        time.sleep(0.01)
                    finally:
                        with handle.runtime_state["counter_lock"]:
                            handle.runtime_state["attempts"] += 1
        finally:
            connection.close()

    def _await_impact(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> Mapping[str, Any]:
        started = context.clock.monotonic()
        limit = self._dashboard_limit(context, handle)
        while context.clock.monotonic() < started + 60.0:
            with handle.runtime_state["counter_lock"]:
                attempts = handle.runtime_state["attempts"]
            if attempts >= max(1, min(handle.facts["cohort_size"], limit)):
                break
            if limit == 0 and context.clock.monotonic() - started >= 10.0:
                break
            time.sleep(0.2)
        with handle.runtime_state["counter_lock"]:
            handle.facts["retry_attempts"] = handle.runtime_state["attempts"]
        facts = handle.runtime_state["session_facts_fn"]()
        handle.facts.update(facts)
        if handle.facts["retry_attempts"] <= 0 and limit == 0:
            raise PreventedActivation(
                mechanism="dashboard_admission_clamp",
                protection_state={
                    "dashboard_max_concurrency": limit,
                    "release_tag": RELEASE_TAG,
                    "phase": handle.facts.get("phase"),
                },
            )
        if handle.facts["retry_attempts"] <= 0 or facts["retry_session_count"] <= 0:
            raise injection_failed(
                handle,
                f"retry storm produced no observable attempts: attempts={handle.facts['retry_attempts']}, "
                f"sessions={facts['retry_session_count']}, limit={limit}, phase={handle.facts.get('phase')!r}",
            )
        handle.facts["outcome_kind"] = "applied"
        return dict(handle.facts)

    def _alert(self, handle: HtapCapabilityHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title=(
                "One dashboard tier is emitting far more short aggregation queries than its normal envelope; "
                "dashboard freshness and order latency are both degrading."
            ),
            symptoms=(
                "dashboard query volume far above baseline",
                "elevated order latency",
                "dashboard timeouts rising",
            ),
            severity="warning",
            category="read_amplification",
        )

    def assert_clean(self, handle: HtapCapabilityHandle) -> Mapping[str, object]:
        facts = handle.runtime_state["session_facts_fn"]()
        if facts["retry_session_count"] != 0:
            raise RuntimeError(f"Dashboard retry cohort survived cleanup: event_id={handle.event_id!r}, facts={facts!r}")
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}
