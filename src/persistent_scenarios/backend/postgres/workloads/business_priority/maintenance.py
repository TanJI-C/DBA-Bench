"""Instance 1 (business priority) legitimate scheduled maintenance.

The ledger-rebuild worker is the honest counterpart of the poisoned
maintenance masquerade (tx_leak_2): one long-lived session runs short
read-only aggregate transactions over `shop.orders_archive`, journals every
committed batch into `ops.maintenance_audit`, and honours its registry row's
bounded per-transaction claim. Its dense audit trajectory plus bounded
transaction age are what separate a legitimate maintenance job from the
poisoned session that only writes `started` and never commits a batch.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass

from ..oltp_core.ports import Clock, ConnectionSource, EvidenceLedgerFile

MAINTENANCE_APPLICATION_NAME = "maintenance_ledger_rebuild"
MAINTENANCE_LEDGER_TASK_ID = "orders-archive-ledger-rebuild"
MAINTENANCE_POLL_SECONDS = 45.0

MAINTENANCE_AGGREGATE_SQL = (
    "SELECT count(*), coalesce(sum(amount_cents), 0) FROM shop.orders_archive "
    "WHERE status IN ('paid', 'cancelled') AND created_at < %(cutoff)s;"
)
MAINTENANCE_AUDIT_SQL = (
    "INSERT INTO ops.maintenance_audit (task_id, event, at_epoch, detail) VALUES ("
    "%(task_id)s, %(event)s, extract(epoch FROM clock_timestamp()), %(detail)s);"
)


@dataclass(frozen=True, slots=True)
class MaintenanceRunReport:
    batches: int


class MaintenanceLedgerWorker:
    """Runs one read-only archive statistics batch per cycle and journals it."""

    def __init__(
        self,
        *,
        source: ConnectionSource,
        clock: Clock,
        evidence: EvidenceLedgerFile,
        task_id: str,
        cutoff_created_at: float,
        poll_seconds: float = MAINTENANCE_POLL_SECONDS,
    ) -> None:
        self._source = source
        self._clock = clock
        self._evidence = evidence
        self._task_id = task_id
        self._cutoff = cutoff_created_at
        self._poll_seconds = poll_seconds
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._first_batch = threading.Event()
        self._batches = 0
        self._error: BaseException | None = None

    def start_in_background(self) -> None:
        if self._thread is not None:
            raise RuntimeError("MaintenanceLedgerWorker cannot start twice")
        self._thread = threading.Thread(
            target=self._run, name="pg5-oltp-maintenance-worker", daemon=True
        )
        self._thread.start()

    def stop(self) -> MaintenanceRunReport:
        if self._thread is None:
            raise RuntimeError("MaintenanceLedgerWorker stopped before it was started")
        self._stop.set()
        self._thread.join(timeout=30)
        if self._thread.is_alive():
            raise RuntimeError("MaintenanceLedgerWorker thread did not stop within its join timeout")
        if self._error is not None:
            raise RuntimeError(
                f"MaintenanceLedgerWorker failed: error={self._error!r}"
            ) from self._error
        return MaintenanceRunReport(batches=self._batches)

    def wait_for_first_batch(self, budget_seconds: float) -> bool:
        return self._first_batch.wait(timeout=budget_seconds)

    def _run(self) -> None:
        connection = self._source.connection(MAINTENANCE_APPLICATION_NAME)
        try:
            while not self._stop.is_set():
                with connection.cursor() as cursor:  # type: ignore[attr-defined]
                    cursor.execute(MAINTENANCE_AGGREGATE_SQL, {"cutoff": self._cutoff})
                    cursor.fetchall()
                connection.commit()  # type: ignore[attr-defined]
                self._journal(connection, "batch_committed", f"batches={self._batches + 1}")
                self._batches += 1
                self._first_batch.set()
                self._evidence.append({
                    "kind": "maintenance_batch",
                    "task_id": self._task_id,
                    "batches": self._batches,
                    "at": self._clock.monotonic(),
                })
                if not self._clock.wait_until(
                    self._clock.monotonic() + self._poll_seconds, self._stop
                ):
                    break
        except BaseException as exc:  # noqa: BLE001 - surfaced through stop()
            self._error = exc
        finally:
            connection.close()

    def _journal(self, connection: object, event: str, detail: str) -> None:
        with connection.cursor() as cursor:  # type: ignore[attr-defined]
            cursor.execute(MAINTENANCE_AUDIT_SQL, {
                "task_id": self._task_id, "event": event, "detail": detail,
            })
        connection.commit()  # type: ignore[attr-defined]
