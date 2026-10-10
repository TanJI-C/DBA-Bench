"""Instance 5 (online change) resumable idempotent backfill worker.

The worker consumes its task row from `ops.release_tasks`: it waits for the
declared schema dependency (the column must exist), then fills the derived
`promo_tier` column in rate-limited batches over rows where it is still NULL.
Every batch is idempotent (the derived value is a pure function of business
columns), progress is checkpointed to the task row, and a restarted worker
resumes from wherever the NULLs are. Pausing and re-rate are authorized
through the task row; the worker honours changes between batches.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass

from ..oltp_core.control import column_exists, read_release_task
from ..oltp_core.ports import Clock, ConnectionSource, EvidenceLedgerFile
from ..oltp_core.schema import VIP_AMOUNT_CENTS

BACKFILL_APPLICATION_NAME = "backfill_worker"
BACKFILL_POLL_SECONDS = 2.0

BACKFILL_BATCH_SQL = (
    "UPDATE shop.orders SET promo_tier = "
    "(CASE WHEN amount_cents >= %(vip)s THEN 'vip' ELSE 'standard' END) "
    "WHERE order_id IN ("
    "  SELECT order_id FROM shop.orders WHERE promo_tier IS NULL ORDER BY order_id LIMIT %(batch)s"
    ");"
)
BACKFILL_PROGRESS_SQL = (
    "UPDATE ops.release_tasks SET status = %(status)s, rows_done = %(rows_done)s "
    "WHERE task_id = %(task_id)s;"
)

# The worker resolves its tier boundary at batch time from the live campaign
# config (the production bug behind the definition drift: a historical backfill
# must use the canonical derivation, not the time-varying effective policy).
# The resolved value is used, never logged — the drift stays silent until the
# delivery verifier recomputes the canonical rule.
BACKFILL_TIER_BOUNDARY_SQL = (
    "SELECT COALESCE(("
    "SELECT vip_threshold_cents_override FROM ops.promo_campaign "
    "WHERE state = 'active' ORDER BY activated_at DESC LIMIT 1"
    "), %(canonical)s);"
)


@dataclass(frozen=True, slots=True)
class BackfillRunReport:
    rows_backfilled: int
    batches: int
    completed_at: float | None
    delivery_note: str  # "completed" | "stopped_before_completion"


def parse_column_dependency(depends_on: str) -> tuple[str, str]:
    if not depends_on.startswith("column:"):
        raise ValueError(
            f"Backfill dependency must reference a schema column: depends_on={depends_on!r}"
        )
    _, table, column = depends_on.split(":", 2)
    return table, column


class BackfillWorker:
    def __init__(
        self,
        *,
        source: ConnectionSource,
        clock: Clock,
        evidence: EvidenceLedgerFile,
    ) -> None:
        self._source = source
        self._clock = clock
        self._evidence = evidence
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._report: BackfillRunReport | None = None
        self._error: BaseException | None = None

    def start_in_background(self, *, task_id: str) -> None:
        if self._thread is not None:
            raise RuntimeError("BackfillWorker cannot start twice")
        self._task_id = task_id
        self._thread = threading.Thread(
            target=self._run, name="pg5-oltp-backfill-worker", daemon=True
        )
        self._thread.start()

    def stop(self) -> BackfillRunReport:
        if self._thread is None:
            raise RuntimeError("BackfillWorker stopped before it was started")
        self._stop.set()
        self._thread.join(timeout=120)
        if self._thread.is_alive():
            raise RuntimeError("BackfillWorker thread did not stop within its join timeout")
        if self._error is not None:
            raise RuntimeError(f"BackfillWorker failed: error={self._error!r}") from self._error
        assert self._report is not None
        return self._report

    def _run(self) -> None:
        connection = self._source.connection(BACKFILL_APPLICATION_NAME)
        rows_total = 0
        batches = 0
        completed_at: float | None = None
        self._evidence.append({
            "kind": "job_planned",
            "job_id": self._task_id,
            "job_kind": "backfill",
            "at": self._clock.monotonic(),
        })
        try:
            task = read_release_task(connection, self._task_id)
            if task.kind != "backfill":
                raise ValueError(
                    f"BackfillWorker requires a backfill task: task_id={self._task_id!r}, kind={task.kind!r}"
                )
            rows_total = task.rows_done
            table, column = parse_column_dependency(task.depends_on or "")
            with connection.cursor() as cursor:  # type: ignore[attr-defined]
                cursor.execute(BACKFILL_PROGRESS_SQL, {"status": "waiting_dependency", "rows_done": rows_total, "task_id": self._task_id})
            connection.commit()  # type: ignore[attr-defined]
            while not self._stop.is_set() and not column_exists(connection, table, column):
                self._evidence.append({
                    "kind": "backfill_waiting_schema",
                    "task_id": self._task_id,
                    "table": table,
                    "column": column,
                    "at": self._clock.monotonic(),
                })
                if not self._clock.wait_until(self._clock.monotonic() + BACKFILL_POLL_SECONDS, self._stop):
                    break
            if column_exists(connection, table, column):
                while not self._stop.is_set():
                    task = read_release_task(connection, self._task_id)
                    if task.paused:
                        if self._clock.wait_until(self._clock.monotonic() + BACKFILL_POLL_SECONDS, self._stop):
                            continue
                        break
                    moved = self._run_one_batch(connection, task.batch_rows)
                    if moved == 0:
                        self._mark_done(connection, rows_total)
                        completed_at = self._clock.monotonic()
                        break
                    batches += 1
                    rows_total += moved
                    with connection.cursor() as cursor:  # type: ignore[attr-defined]
                        cursor.execute(BACKFILL_PROGRESS_SQL, {"status": "running", "rows_done": rows_total, "task_id": self._task_id})
                    connection.commit()  # type: ignore[attr-defined]
                    self._evidence.append({
                        "kind": "backfill_batch",
                        "task_id": self._task_id,
                        "rows_backfilled": moved,
                        "rows_total": rows_total,
                        "at": self._clock.monotonic(),
                    })
                    pause = moved / task.rate_rows_per_second
                    if not self._clock.wait_until(self._clock.monotonic() + pause, self._stop):
                        break
        except BaseException as exc:  # noqa: BLE001 - surfaced through stop()
            self._error = exc
        finally:
            connection.close()
            delivery_note = "completed" if completed_at is not None else "stopped_before_completion"
            self._evidence.append({
                "kind": "job_terminal",
                "job_id": self._task_id,
                "job_kind": "backfill",
                "status": delivery_note,
                "rows_backfilled": rows_total,
                "completed_at": completed_at,
                "error": repr(self._error) if self._error is not None else None,
                "at": self._clock.monotonic(),
            })
            self._report = BackfillRunReport(
                rows_backfilled=rows_total,
                batches=batches,
                completed_at=completed_at,
                delivery_note=delivery_note,
            )

    def _run_one_batch(self, connection: object, batch_rows: int) -> int:
        with connection.cursor() as cursor:  # type: ignore[attr-defined]
            cursor.execute(BACKFILL_TIER_BOUNDARY_SQL, {"canonical": VIP_AMOUNT_CENTS})
            boundary = int(cursor.fetchone()[0])
        connection.commit()  # type: ignore[attr-defined]
        with connection.cursor() as cursor:  # type: ignore[attr-defined]
            cursor.execute(BACKFILL_BATCH_SQL, {"vip": boundary, "batch": batch_rows})
            moved = cursor.rowcount
        connection.commit()  # type: ignore[attr-defined]
        return moved

    def _mark_done(self, connection: object, rows_total: int) -> None:
        with connection.cursor() as cursor:  # type: ignore[attr-defined]
            cursor.execute(BACKFILL_PROGRESS_SQL, {"status": "done", "rows_done": rows_total, "task_id": self._task_id})
        connection.commit()  # type: ignore[attr-defined]


def verify_backfill_delivery(snapshot, *, vip_amount_cents: int = VIP_AMOUNT_CENTS) -> tuple[str, ...]:
    """Every order row must carry the derived promo tier matching the rule."""

    from ..oltp_core.schema import promo_tier_for_amount

    if not snapshot.promo_tier_present:
        return ("promo_tier column is missing from shop.orders; the release did not complete",)
    failures: list[str] = []
    for order_id, row in snapshot.orders.items():
        expected = promo_tier_for_amount(row.amount_cents)
        if row.promo_tier is None:
            failures.append(f"order row left unbackfilled: order_id={order_id!r}")
        elif row.promo_tier != expected:
            failures.append(
                f"order row promo_tier diverges from the derived rule: order_id={order_id!r}, "
                f"promo_tier={row.promo_tier!r}, expected={expected!r}, amount_cents={row.amount_cents}"
            )
    return tuple(failures)


def verify_release_index(indexes, *, table: str, column: str) -> tuple[str, ...]:
    """`indexes` maps index_name -> (is_valid, key_columns); a valid index must cover the column."""

    failures: list[str] = []
    serving = [
        name
        for name, (is_valid, columns) in indexes.items()
        if is_valid and column in columns
    ]
    if not serving:
        rendered = {
            name: (is_valid, sorted(columns))
            for name, (is_valid, columns) in indexes.items()
        }
        failures.append(
            f"no valid index serves the released query pattern: table={table!r}, "
            f"column={column!r}, indexes={rendered!r}"
        )
    return tuple(failures)
