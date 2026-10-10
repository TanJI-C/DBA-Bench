"""Smoke instance capability: a held transaction on the promo hot row.

The smoke scenario is a framework test:
one mechanism, exercised twice on distinct entities, proving arrival facts,
repair-by-termination, cleanup and the reverse-cleanup boundary without any
instance business verdicts. The same capability ID repeats with a distinct
entity, which also covers the per-entity resource isolation admission path.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Mapping

from ...workloads.oltp_core.capability import (
    CapabilityContext,
    CapabilityDeclaration,
    CapabilityRegistry,
    EventActivationResult,
    EventOccurrence,
    ResourceOwnership,
)
from ...workloads.oltp_core.held_session import HeldSession
from ...workloads.oltp_core.ports import ConnectionSource

ACTIVATION_BUDGET_SECONDS = 60.0
SMOKE_APPLICATION_NAME = "smoke_tx_leak"

SMOKE_HELD_ROW_SQL = (
    "UPDATE shop.inventory SET qty_available = qty_available - 1 "
    "WHERE sku = %(sku)s RETURNING sku;"
)


@dataclass(slots=True)
class _SmokeLeakHandle:
    event_id: str
    sku: str
    clock: object
    source: ConnectionSource
    stop: threading.Event = field(default_factory=threading.Event)
    thread: threading.Thread | None = None
    observation_slot: list = field(default_factory=list)

    def observation(self):
        return self.observation_slot[0] if self.observation_slot else None


class SmokeTxLeakCapability:
    """One application worker holds an uncommitted update on the promo row."""

    capability_id = "smoke_tx_leak"
    _PARAMS = frozenset({"sku", "hold_seconds"})

    def declaration(self, occurrence: EventOccurrence) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            ownership=(ResourceOwnership(
                resource_key=f"session:smoke-tx-leak:{occurrence.entity}",
                resource_kind="database_session",
            ),),
            max_activation_seconds=ACTIVATION_BUDGET_SECONDS,
        )

    def activate(self, context: CapabilityContext) -> EventActivationResult:
        context.occurrence.reject_unknown_params(self._PARAMS)
        sku = context.occurrence.require_str("sku")
        hold_seconds = context.occurrence.require_number("hold_seconds")
        handle = _SmokeLeakHandle(
            event_id=context.occurrence.event_id,
            sku=sku,
            clock=context.clock,
            source=context.source,
        )

        def opener(connection) -> None:
            with connection.cursor() as cursor:
                cursor.execute(SMOKE_HELD_ROW_SQL, {"sku": sku})
                cursor.fetchall()

        def run() -> None:
            session = HeldSession(
                source=handle.source,
                clock=handle.clock,
                application_name=f"{SMOKE_APPLICATION_NAME}-{handle.event_id}",
                opener=opener,
            )
            observation = session.run(hold_seconds=hold_seconds, stop=handle.stop)
            handle.observation_slot.append(observation)

        handle.thread = threading.Thread(target=run, name=f"pg5-smoke-tx-leak-{handle.event_id}", daemon=True)
        handle.thread.start()

        def evidence_now():
            observation = handle.observation()
            if observation is not None and observation.prevented:
                return {
                    "mechanism": "role_transaction_timeout",
                    "protection_state": dict(observation.protection_gucs),
                    "held_seconds": observation.held_seconds,
                }
            # Live server evidence: while the session holds, hold_seconds far
            # exceeds the activation budget, so the observation is still
            # pending and the held transaction is proven through
            # pg_stat_activity instead.
            connection = handle.source.connection(f"smoke-impact-{handle.event_id}")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT pid FROM pg_stat_activity "
                        "WHERE application_name = %(app)s AND state = 'idle in transaction';",
                        {"app": f"{SMOKE_APPLICATION_NAME}-{handle.event_id}"},
                    )
                    rows = cursor.fetchall()
                connection.rollback()
            finally:
                connection.close()
            if not rows:
                return None
            return {"held_sessions": [int(row[0]) for row in rows]}

        deadline = handle.clock.monotonic() + ACTIVATION_BUDGET_SECONDS
        while handle.clock.monotonic() < deadline:
            evidence = evidence_now()
            if evidence is not None:
                outcome = "prevented" if "mechanism" in evidence else "applied"
                return EventActivationResult(
                    handle=handle,
                    attempt={"event_id": handle.event_id, "sku": sku, **evidence},
                    outcome=outcome,
                )
            handle.clock.wait_until(handle.clock.monotonic() + 0.5, handle.stop)
        raise RuntimeError(
            f"Smoke transaction leak produced no observable impact: event_id={handle.event_id!r}"
        )

    def alert(self, context: CapabilityContext, handle: object) -> Mapping[str, object]:
        return {
            "title": "库存更新请求出现排队",
            "symptoms": [
                "库存热点行上存在长时间未提交的应用事务",
                "更新请求等待时间明显上升",
            ],
            "severity": "critical",
            "category": "trade_degradation",
        }

    def cleanup(self, handle: object) -> None:
        handle = self._handle(handle)
        handle.stop.set()
        if handle.thread is not None:
            handle.thread.join(timeout=30)
            if handle.thread.is_alive():
                raise RuntimeError(
                    f"Smoke leak session did not stop within its join timeout: event_id={handle.event_id!r}"
                )
        connection = handle.source.connection(f"smoke-clean-{handle.event_id}")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE application_name = %(app)s AND pid <> pg_backend_pid();",
                    {"app": f"{SMOKE_APPLICATION_NAME}-{handle.event_id}"},
                )
                cursor.fetchall()
            connection.commit()
        finally:
            connection.close()

    def assert_clean(self, handle: object) -> Mapping[str, object]:
        handle = self._handle(handle)
        connection = handle.source.connection(f"smoke-assert-clean-{handle.event_id}")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT count(*) FROM pg_stat_activity "
                    "WHERE application_name = %(app)s AND pid <> pg_backend_pid();",
                    {"app": f"{SMOKE_APPLICATION_NAME}-{handle.event_id}"},
                )
                remaining = int(cursor.fetchone()[0])
            connection.rollback()
        finally:
            connection.close()
        return {
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "clean": remaining == 0,
            "remaining_sessions": remaining,
        }

    def _handle(self, handle: object) -> _SmokeLeakHandle:
        if not isinstance(handle, _SmokeLeakHandle):
            raise ValueError(f"Unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


CAPABILITY_REGISTRY = CapabilityRegistry((SmokeTxLeakCapability(),))
