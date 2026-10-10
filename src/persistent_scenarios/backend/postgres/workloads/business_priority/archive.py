"""Instance 1 (business priority) history archive job.

The archive worker is legitimate operations work: it moves terminal-status
orders older than the configured cutoff into `shop.orders_archive` in rate-
limited batches, honours the public `ops.archive_state` control row (enable,
rate, batch size), and records its progress. Pausing it is an authorized
operational choice; never delivering it is a contract violation.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass

from ..oltp_core.ports import Clock, ConnectionSource, EvidenceLedgerFile

ARCHIVE_APPLICATION_NAME = "archive_worker"
ARCHIVE_JOB_ID = "orders-history-archive"
ARCHIVE_POLL_SECONDS = 2.0

ARCHIVE_STATE_SQL = (
    "SELECT enabled, cutoff_created_at, rate_rows_per_second, batch_rows, rows_moved "
    "FROM ops.archive_state WHERE job_id = %(job_id)s;"
)
ARCHIVE_MOVE_BATCH_SQL = (
    "WITH victims AS ("
    "  SELECT order_id FROM shop.orders"
    "  WHERE created_at < %(cutoff)s AND status IN ('paid', 'cancelled')"
    "  LIMIT %(batch)s"
    "), moved AS ("
    "  INSERT INTO shop.orders_archive (order_id, sku, qty, amount_cents, status, created_at, paid_at)"
    "  SELECT o.order_id, o.sku, o.qty, o.amount_cents, o.status, o.created_at, o.paid_at"
    "  FROM shop.orders o JOIN victims USING (order_id)"
    "  RETURNING order_id"
    ")"
    "DELETE FROM shop.orders WHERE order_id IN (SELECT order_id FROM moved);"
)
ARCHIVE_PROGRESS_SQL = (
    "UPDATE ops.archive_state SET rows_moved = %(rows_moved)s WHERE job_id = %(job_id)s;"
)
ARCHIVE_COMPLETE_SQL = (
    "UPDATE ops.archive_state SET enabled = FALSE WHERE job_id = %(job_id)s;"
)


@dataclass(frozen=True, slots=True)
class ArchiveRunReport:
    rows_moved: int
    completed_at: float | None
    batches: int
    delivery_note: str  # "completed" or "stopped_before_completion"


@dataclass(frozen=True, slots=True)
class _ArchiveStateRow:
    enabled: bool
    cutoff_created_at: float
    rate_rows_per_second: int
    batch_rows: int
    rows_moved: int


def read_archive_state(connection: object, job_id: str) -> _ArchiveStateRow:
    with connection.cursor() as cursor:  # type: ignore[attr-defined]
        cursor.execute(ARCHIVE_STATE_SQL, {"job_id": job_id})
        row = cursor.fetchone()
    if row is None:
        raise ValueError(f"ops.archive_state has no row for the archive job: job_id={job_id!r}")
    return _ArchiveStateRow(bool(row[0]), float(row[1]), int(row[2]), int(row[3]), int(row[4]))


def move_one_batch(connection: object, cutoff: float, batch_rows: int) -> int:
    with connection.cursor() as cursor:  # type: ignore[attr-defined]
        cursor.execute(ARCHIVE_MOVE_BATCH_SQL, {"cutoff": cutoff, "batch": batch_rows})
        moved = cursor.rowcount
    connection.commit()  # type: ignore[attr-defined]
    return moved


def verify_archive_delivery(snapshot, *, cutoff_created_at: float, deadline_note: str) -> tuple[str, ...]:
    """Terminal delivery check: every eligible history order lives in the archive."""

    failures: list[str] = []
    for order_id, row in snapshot.orders.items():
        if not order_id.startswith("hist-"):
            continue
        if row.created_at < cutoff_created_at and row.status in {"paid", "cancelled"}:
            failures.append(
                f"history order still lives in shop.orders after the archive cutoff: "
                f"order_id={order_id!r}, created_at={row.created_at}"
            )
    for order_id, row in snapshot.archived_orders.items():
        if row.created_at >= cutoff_created_at:
            failures.append(
                f"archive holds a row at or after the cutoff: order_id={order_id!r}, created_at={row.created_at}"
            )
    if failures:
        failures.append(f"archive delivery deadline context: {deadline_note}")
    return tuple(failures)


def verify_archive_tradeoff(
    controls,
    *,
    scoring_start_epoch: float,
    peak_window_start_seconds: float,
    peak_window_end_seconds: float,
    peak_grace_seconds: float,
    peak_rate_cap_rows_per_second: int,
    rate_ceiling_rows_per_second: int,
    deferral_budget_seconds: float,
    total_rows: int,
    horizon_seconds: float,
    deadline_note: str = "",
) -> tuple[tuple[str, ...], dict[str, object]]:
    """Evaluates the published archive delivery tradeoff from the control audit.

    ``controls`` are ``(changed_at_epoch, enabled, rate_rows_per_second,
    rows_moved)`` tuples in insertion order, straight from
    ``ops.archive_state_audit``. Every control change opens a segment that
    lasts until the next change (or the horizon end); a completed job closes
    its own active span by disabling itself with ``rows_moved == total_rows``.
    Rules enforced over segments whose start still has pending work
    (``rows_moved < total_rows``):

    - inside the promo peak window (after the published ``peak_grace_seconds``
      reaction allowance) an enabled segment's rate must stay at or under
      ``peak_rate_cap_rows_per_second`` (transaction I/O protection);
    - outside that window the rate ceiling is ``rate_ceiling_rows_per_second``;
    - cumulative disabled (deferred) time within the job lifetime must stay
      within ``deferral_budget_seconds``.

    Returns ``(failures, summary)``; delivery truth itself is the separate
    ``verify_archive_delivery`` check, so an agent that never touches the
    archive is judged by both surfaces.
    """

    peak_start = scoring_start_epoch + peak_window_start_seconds
    peak_end = scoring_start_epoch + peak_window_end_seconds
    cap_start = peak_start + peak_grace_seconds
    horizon_end = scoring_start_epoch + horizon_seconds

    ordered = sorted(controls, key=lambda row: row[0])
    segments: list[tuple[float, float, bool, int, int]] = []
    for index, (at, enabled, rate, moved) in enumerate(ordered):
        end = ordered[index + 1][0] if index + 1 < len(ordered) else horizon_end
        if end > at:
            segments.append((at, end, bool(enabled), int(rate), int(moved)))
    first_enabled_at = next((start for start, _end, enabled, _rate, _moved in segments if enabled), None)

    failures: list[str] = []
    peak_max_rate = 0
    deferral_seconds = 0.0
    for start, end, enabled, rate, moved in segments:
        pending = moved < total_rows
        if enabled:
            cap_overlap = max(0.0, min(end, peak_end) - max(start, cap_start))
            if pending and cap_overlap > 0:
                peak_max_rate = max(peak_max_rate, rate)
                if rate > peak_rate_cap_rows_per_second:
                    failures.append(
                        f"peak-window archive rate cap exceeded: rate={rate} rows/s > "
                        f"cap={peak_rate_cap_rows_per_second} rows/s in scoring-axis window "
                        f"[{peak_window_start_seconds:.0f}s, {peak_window_end_seconds:.0f}s]"
                    )
            if pending and rate > rate_ceiling_rows_per_second:
                failures.append(
                    f"archive rate ceiling exceeded: rate={rate} rows/s > "
                    f"ceiling={rate_ceiling_rows_per_second} rows/s (the ceiling applies "
                    f"wherever the peak-window cap does not)"
                )
        elif first_enabled_at is not None and end > first_enabled_at and pending:
            deferral_seconds += min(end, horizon_end) - max(start, first_enabled_at)

    if deferral_seconds > deferral_budget_seconds:
        failures.append(
            f"archive deferral budget exceeded: paused {deferral_seconds:.0f}s > budget "
            f"{deferral_budget_seconds:.0f}s (deadline context: {deadline_note})"
        )
    summary = {
        "segments": len(segments),
        "peak_max_rate_rows_per_second": peak_max_rate,
        "deferral_seconds": round(deferral_seconds, 1),
    }
    return tuple(failures), summary


class ArchiveWorker:
    """Consumes `ops.archive_state` until the cutoff is drained or it is stopped."""

    def __init__(
        self,
        *,
        source: ConnectionSource,
        clock: Clock,
        evidence: EvidenceLedgerFile,
        job_id: str = ARCHIVE_JOB_ID,
    ) -> None:
        self._source = source
        self._clock = clock
        self._evidence = evidence
        self._job_id = job_id
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._report: ArchiveRunReport | None = None
        self._error: BaseException | None = None

    def start_in_background(self) -> None:
        if self._thread is not None:
            raise RuntimeError("ArchiveWorker cannot start twice")
        self._thread = threading.Thread(
            target=self._run, name="pg5-oltp-archive-worker", daemon=True
        )
        self._thread.start()

    def stop(self) -> ArchiveRunReport:
        if self._thread is None:
            raise RuntimeError("ArchiveWorker stopped before it was started")
        self._stop.set()
        self._thread.join(timeout=60)
        if self._thread.is_alive():
            raise RuntimeError("ArchiveWorker thread did not stop within its join timeout")
        if self._error is not None:
            raise RuntimeError(f"ArchiveWorker failed: error={self._error!r}") from self._error
        assert self._report is not None
        return self._report

    def _run(self) -> None:
        connection = self._source.connection(ARCHIVE_APPLICATION_NAME)
        batches = 0
        moved_total = 0
        completed_at: float | None = None
        self._evidence.append({
            "kind": "job_planned",
            "job_id": self._job_id,
            "job_kind": "archive",
            "at": self._clock.monotonic(),
        })
        try:
            while not self._stop.is_set():
                state = read_archive_state(connection, self._job_id)
                if not state.enabled:
                    if self._clock.wait_until(self._clock.monotonic() + ARCHIVE_POLL_SECONDS, self._stop):
                        continue
                    break
                moved = move_one_batch(connection, state.cutoff_created_at, state.batch_rows)
                if moved == 0:
                    completed_at = self._clock.monotonic()
                    # A completed job takes itself out of the schedule; the
                    # control audit then closes the job's active span and the
                    # delivery-tradeoff verifier reads the final rows_moved.
                    with connection.cursor() as cursor:  # type: ignore[attr-defined]
                        cursor.execute(ARCHIVE_COMPLETE_SQL, {"job_id": self._job_id})
                    connection.commit()  # type: ignore[attr-defined]
                    break
                batches += 1
                moved_total += moved
                with connection.cursor() as cursor:  # type: ignore[attr-defined]
                    cursor.execute(ARCHIVE_PROGRESS_SQL, {"rows_moved": moved_total, "job_id": self._job_id})
                connection.commit()  # type: ignore[attr-defined]
                self._evidence.append({
                    "kind": "archive_batch",
                    "job_id": self._job_id,
                    "rows_moved": moved,
                    "rows_total": moved_total,
                    "at": self._clock.monotonic(),
                })
                pause = moved / state.rate_rows_per_second
                if not self._clock.wait_until(self._clock.monotonic() + pause, self._stop):
                    break
        except BaseException as exc:  # noqa: BLE001 - surfaced through stop()
            self._error = exc
        finally:
            connection.close()
            delivery_note = "completed" if completed_at is not None else "stopped_before_completion"
            self._evidence.append({
                "kind": "job_terminal",
                "job_id": self._job_id,
                "job_kind": "archive",
                "status": delivery_note,
                "rows_moved": moved_total,
                "completed_at": completed_at,
                "error": repr(self._error) if self._error is not None else None,
                "at": self._clock.monotonic(),
            })
            self._report = ArchiveRunReport(
                rows_moved=moved_total,
                completed_at=completed_at,
                batches=batches,
                delivery_note=delivery_note,
            )
