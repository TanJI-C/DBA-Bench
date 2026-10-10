"""Workload driver for ``tidb_oltp_online_topology_change``.

Extends the hotspot trade driver with the maintenance delivery ledger: the
work-order control table (published by the change-plan capability) is the
public maintenance contract; this driver plans one ledger job per published
deliverable (``deliverable_id == job_id``) and records
delivery strictly from trusted environment facts (PD store records, SQL
placement state, connection counts). Agent repairs change the world; this
ledger only observes it.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Mapping

from src.persistent_scenarios.runtime.clock import Clock
from src.persistent_scenarios.runtime.ledger import (
    JobAttempt,
    JobAttemptOutcome,
    LedgerTerminal,
    TrustedLedger,
)

from ..hotspot.driver import HotspotWorkloadDriver, TrafficPlan
from .delivery import DELIVERY_PREDICATES
from .schema import READ_MAINTENANCE_ORDERS_SQL


@dataclass(frozen=True, slots=True)
class MaintenanceOrderRow:
    order_id: str
    deliverable_id: str
    kind: str
    target: str
    deadline_seconds: int
    published_at_ms: int


class TopologyWorkloadDriver(HotspotWorkloadDriver):
    """Trade workload plus trusted maintenance delivery observation."""

    def __init__(
        self,
        *,
        maintenance_ledger: TrustedLedger,
        maintenance_service_id: str,
        environment_port: Any,
        maintenance_poll_seconds: float = 2.0,
        **trade_kwargs: Any,
    ) -> None:
        super().__init__(**trade_kwargs)
        self.maintenance_ledger = maintenance_ledger
        self.maintenance_service_id = maintenance_service_id
        self.port = environment_port
        self._maintenance_poll_seconds = maintenance_poll_seconds
        self._planned_deliverables: set[tuple[str, str]] = set()
        self._decided_deliverables: set[tuple[str, str]] = set()
        self._planned_lock = threading.Lock()
        self._busy_backends: set[str] = set()
        self._maintenance_stop = threading.Event()
        self._maintenance_thread: threading.Thread | None = None
        self._delivered: tuple[Mapping[str, Any], ...] = ()
        self._maintenance_errors: tuple[str, ...] = ()
        self._delivery_lock = threading.Lock()

    # -- lifecycle -------------------------------------------------------------

    def start(self) -> None:
        super().start()
        self._maintenance_thread = threading.Thread(
            target=self._maintenance_loop, name="tidb5-topology-maintenance", daemon=True
        )
        self._maintenance_thread.start()

    def stop(self) -> Mapping[str, Any]:
        self._maintenance_stop.set()
        if self._maintenance_thread is not None:
            self._maintenance_thread.join(timeout=30)
            if self._maintenance_thread.is_alive():
                raise RuntimeError(
                    f"maintenance poller did not stop: run_id={self.run_id!r}"
                )
        self._finalize_outstanding_maintenance()
        summary = dict(super().stop())
        with self._delivery_lock:
            summary["maintenance_deliveries"] = self._delivered
        return summary

    def ledgers(self) -> Mapping[str, TrustedLedger]:
        return {"trade": self.ledger, "maintenance": self.maintenance_ledger}

    def baseline_facts(self) -> Mapping[str, object]:
        return {
            **super().baseline_facts(),
            "maintenance_delivered": len(self._delivered),
        }

    def planned_deliverable_ids(self) -> set[str]:
        """Deliverable ids planned but not yet decided (adoption evidence)."""
        with self._planned_lock:
            return {deliverable_id for _order_id, deliverable_id in self._planned_deliverables}

    def decided_deliverable_ids(self) -> set[str]:
        """Deliverable ids that reached a terminal decision.

        The driver decides a terminal and then removes the job from the
        planned set in the same step (decide-then-remove), so a decided id is
        the real terminal evidence of an adopted deliverable."""
        with self._planned_lock:
            return {deliverable_id for _order_id, deliverable_id in self._decided_deliverables}

    # -- PersistentWorkloadRuntime protocol extensions -------------------------

    def stop_new_requests(self) -> None:
        super().stop_new_requests()
        # The runtime stops arrivals before sealing the trusted ledgers
        # (engine._stop_before_evaluation); the maintenance poller appends to
        # the maintenance ledger, so it must stop in the same phase. Keeping
        # it alive past the seal is what produces "terminal decided twice":
        # ledger.finalize_outstanding closes every open job while this thread
        # is still deciding terminals for the same deliverables.
        self._maintenance_stop.set()

    def drain(self) -> None:
        super().drain()
        if self._maintenance_thread is not None:
            self._maintenance_thread.join(timeout=30)
            if self._maintenance_thread.is_alive():
                raise RuntimeError(
                    f"maintenance poller did not stop during drain: run_id={self.run_id!r}"
                )

    # -- maintenance delivery ----------------------------------------------------

    def _maintenance_loop(self) -> None:
        while not self._maintenance_stop.is_set():
            try:
                self._maintenance_tick()
            except Exception as exc:  # noqa: BLE001 - recorded, retried, surfaced at stop
                self._maintenance_errors = self._maintenance_errors + (repr(exc),)
                if len(self._maintenance_errors) > 100:
                    raise RuntimeError(
                        f"maintenance poller failed repeatedly: run_id={self.run_id!r}, "
                        f"last_errors={self._maintenance_errors[-3:]!r}"
                    ) from exc
                self._maintenance_stop.wait(1.0)
                continue
            self._maintenance_stop.wait(self._maintenance_poll_seconds)

    def _maintenance_tick(self) -> None:
        rows = self._read_maintenance_rows()
        for target, count in self.port.backend_connection_counts().items():
            if int(count) > 0:
                self._busy_backends.add(str(target))
        for row in rows:
            key = (row.order_id, row.deliverable_id)
            with self._planned_lock:
                if key in self._decided_deliverables:
                    # A decided deliverable is terminal; the work-order row
                    # stays in the table as the public contract record but is
                    # never re-delivered.
                    continue
            self._plan_job(row)
            if row.kind == "tidb_drain" and row.target not in self._busy_backends:
                # Delivery guard: every published deliverable is planned at
                # publication (that is the work-order adoption evidence), but a
                # drain is only evaluable once the target actually carried
                # connections. Zero connections before the pool bias ever
                # concentrated anything is not "drained": deciding the
                # terminal in that degenerate window would fake the
                # obligation. The job stays planned-pending until the bias
                # lifts this guard, then the predicate reads the real
                # post-bias facts.
                continue
            predicate = DELIVERY_PREDICATES.get(row.kind)
            if predicate is None:
                raise ValueError(
                    f"maintenance work order references an unknown delivery kind: "
                    f"order_id={row.order_id!r}, deliverable_id={row.deliverable_id!r}, kind={row.kind!r}"
                )
            facts = predicate(self.port, self.source.connect_control(), row.target)
            if not facts["satisfied"]:
                if self.clock.monotonic() >= self._deadline_for(row):
                    self._deliver(row, LedgerTerminal.INCOMPLETE_TIMEOUT, facts)
                continue
            self._deliver(row, LedgerTerminal.COMPLETED, facts)

    def _read_maintenance_rows(self) -> tuple[MaintenanceOrderRow, ...]:
        connection = self.source.connect_control()
        try:
            with connection.cursor() as cursor:
                cursor.execute(READ_MAINTENANCE_ORDERS_SQL)
                rows = cursor.fetchall()
            connection.commit()
        finally:
            connection.close()
        return tuple(
            MaintenanceOrderRow(
                order_id=str(row[0]),
                deliverable_id=str(row[1]),
                kind=str(row[2]),
                target=str(row[3]),
                deadline_seconds=int(row[4]),
                published_at_ms=int(row[5]),
            )
            for row in rows
        )

    def _plan_job(self, row: MaintenanceOrderRow) -> None:
        key = (row.order_id, row.deliverable_id)
        with self._planned_lock:
            if key in self._planned_deliverables or key in self._decided_deliverables:
                return
            self._planned_deliverables.add(key)
        submitted_at = row.published_at_ms / 1000.0
        self.maintenance_ledger.append_job_planned(
            job_id=row.deliverable_id,
            service_id=self.maintenance_service_id,
            job_kind=row.kind,
            batch_version=row.order_id,
            input_snapshot={"target": row.target, "order_id": row.order_id},
            submitted_at_monotonic=submitted_at,
            deadline_at_monotonic=submitted_at + row.deadline_seconds,
        )

    def _deadline_for(self, row: MaintenanceOrderRow) -> float:
        return row.published_at_ms / 1000.0 + row.deadline_seconds

    def _deliver(self, row: MaintenanceOrderRow, terminal: LedgerTerminal, facts: Mapping[str, Any]) -> None:
        key = (row.order_id, row.deliverable_id)
        with self._planned_lock:
            if key not in self._planned_deliverables:
                raise RuntimeError(
                    f"delivery observed for an un-planned job: deliverable_id={row.deliverable_id!r}"
                )
            now = self.clock.monotonic()
            delivered_at = now if terminal is LedgerTerminal.COMPLETED else None
            digest = f"{row.deliverable_id}:{row.kind}:{row.target}" if terminal is LedgerTerminal.COMPLETED else None
            if terminal is LedgerTerminal.COMPLETED:
                self.maintenance_ledger.append_job_attempt(
                    job_id=row.deliverable_id,
                    attempt=JobAttempt(
                        attempt_index=0,
                        queued_at_monotonic=row.published_at_ms / 1000.0,
                        started_at_monotonic=None,
                        ended_at_monotonic=now,
                        outcome=JobAttemptOutcome.SUCCEEDED,
                        detail={str(k): v for k, v in facts.items()},
                    ),
                )
            self.maintenance_ledger.append_job_terminal(
                job_id=row.deliverable_id,
                terminal=terminal,
                delivered_at_monotonic=delivered_at,
                result_digest=digest,
            )
            self._planned_deliverables.discard(key)
            self._decided_deliverables.add(key)
        if terminal is LedgerTerminal.COMPLETED:
            with self._delivery_lock:
                self._delivered = self._delivered + ({
                    "deliverable_id": row.deliverable_id,
                    "kind": row.kind,
                    "target": row.target,
                    "delivered_at_monotonic": now,
                },)

    def _finalize_outstanding_maintenance(self) -> None:
        with self._planned_lock:
            keys = sorted(self._planned_deliverables)
        for order_id, deliverable_id in keys:
            self._finalize_one_outstanding(deliverable_id)
        with self._planned_lock:
            for key in keys:
                self._planned_deliverables.discard(key)
                # Whether this driver wrote the terminal or the runtime's
                # ledger seal decided it first, the deliverable is terminal-
                # decided now; a surviving tick must never re-plan it.
                self._decided_deliverables.add(key)

    def _finalize_one_outstanding(self, deliverable_id: str) -> None:
        """Close one undecided job as an explicit outstanding loss.

        Idempotent: the runtime's ledger seal (``engine._seal_ledgers`` ->
        ``TrustedLedger.finalize_outstanding``) runs while this driver is
        still alive and closes the same open jobs, so a key still in the
        planned set at stop time may already carry its INCOMPLETE_OUTSTANDING
        terminal. The append arguments here are always valid by construction,
        so the only ValueError the append can raise is the ledger's
        already-terminal-decided guard - that is the skip case, not a failure.
        """
        try:
            self.maintenance_ledger.append_job_terminal(
                job_id=deliverable_id,
                terminal=LedgerTerminal.INCOMPLETE_OUTSTANDING,
                delivered_at_monotonic=None,
                result_digest=None,
            )
        except ValueError as exc:
            if "terminal decided twice" not in str(exc):
                raise
