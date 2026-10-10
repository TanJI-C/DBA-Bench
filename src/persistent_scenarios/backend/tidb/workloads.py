"""pymysql shared workload executors for TiDB persistent scenarios.

Ledger semantics align with the core ``TrustedLedger``: one business identity
is planned exactly once, retries re-enqueue the same identity and inherit the
original deadline, queueing and execution count into end-to-end latency, and
every record reaches exactly one terminal state. Public control surfaces (job
queue tables, business marker tables) are instance-owned SQL; the trusted
ledger lives outside the database and is the only scoring truth.

TiDB specifics versus the PostgreSQL executors:

- connections use pymysql; per-attempt bounds are session variables
  (``MAX_EXECUTION_TIME`` covers SELECT statements; DML deadlines come from the
  business deadline plus idempotent plan SQL, never from invented timeouts);
- commit-result-unknown: an error raised by ``commit()`` records the attempt
  outcome and leaves the identity open for retry; plan SQL must verify the
  business idempotency key instead of assuming rollback;
- error classification lives in ``tidberrors.py``.
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import queue
import threading
import time
from typing import Mapping

import pymysql.err

from src.persistent_scenarios.model.spec import JSONValue
from src.persistent_scenarios.runtime.clock import Clock
from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    JobAttempt,
    JobAttemptOutcome,
    LedgerTerminal,
    TransactionAttempt,
    TrustedLedger,
)

from .tidberrors import classify_job_outcome, classify_transaction_outcome


@dataclass(frozen=True, slots=True)
class TiDBLogicalTransactionPlan:
    """One logical business transaction planned by the instance driver."""

    business_id: str
    tx_kind: str
    planned_at_monotonic: float
    deadline_at_monotonic: float
    execute: Callable[["TiDBLogicalTransactionPlan", object], str]

    def __post_init__(self) -> None:
        if not isinstance(self.business_id, str) or not self.business_id.strip():
            raise ValueError(f"business_id must be non-empty: value={self.business_id!r}")
        if not callable(self.execute):
            raise TypeError(f"plan execute must be callable: business_id={self.business_id!r}")


class TiDBOltpTransactionPool:
    def __init__(
        self,
        *,
        service_id: str,
        ledger: TrustedLedger,
        clock: Clock,
        concurrency: int,
        connection_factory: Callable[[], object],
        request_timeout_ms: int,
        queue_capacity: int = 64,
        drain_grace_seconds: float = 30.0,
    ):
        if concurrency < 1:
            raise ValueError(f"OLTP pool concurrency must be at least 1: service_id={service_id!r}, concurrency={concurrency}")
        if request_timeout_ms <= 0:
            raise ValueError(f"OLTP request_timeout_ms must be positive: service_id={service_id!r}, value={request_timeout_ms}")
        if queue_capacity < 1:
            raise ValueError(f"OLTP queue_capacity must be at least 1: service_id={service_id!r}, value={queue_capacity}")
        self.service_id = service_id
        self.ledger = ledger
        self.clock = clock
        self._connection_factory = connection_factory
        self._request_timeout_ms = request_timeout_ms
        self._drain_grace_seconds = drain_grace_seconds
        self._work_queue: queue.Queue[TiDBLogicalTransactionPlan] = queue.Queue(maxsize=queue_capacity)
        self._accepting = threading.Event()
        self._accepting.set()
        self._stop_workers = threading.Event()
        self._planned: set[str] = set()
        self._open: dict[str, TiDBLogicalTransactionPlan] = {}
        self._failed: dict[str, TiDBLogicalTransactionPlan] = {}
        self._attempt_counts: dict[str, int] = {}
        self._active_count = 0
        self._lock = threading.Lock()
        self._idle_condition = threading.Condition()
        self._executor = ThreadPoolExecutor(
            max_workers=concurrency, thread_name_prefix=f"persistent_scenario-tidb-oltp-{service_id}"
        )
        self._started = False
        self._stopped = False

    # -- planning and retry submission ---------------------------------------

    def submit(self, plan: TiDBLogicalTransactionPlan) -> None:
        """Plan one logical transaction. Each business_id is planned once."""
        with self._lock:
            if plan.business_id in self._planned:
                raise ValueError(
                    f"logical transaction {plan.business_id!r} planned twice in service {self.service_id!r}"
                )
            self._planned.add(plan.business_id)
            self._open[plan.business_id] = plan
        self.ledger.append_planned_transaction(
            business_id=plan.business_id,
            service_id=self.service_id,
            tx_kind=plan.tx_kind,
            planned_at_monotonic=plan.planned_at_monotonic,
            deadline_at_monotonic=plan.deadline_at_monotonic,
        )
        self._enqueue(plan)

    def submit_retry(self, plan: TiDBLogicalTransactionPlan) -> None:
        """Client-side retry of an already planned business identity.

        The retry inherits the original deadline; retries never widen the
        ledger denominator. Plan SQL must be idempotent (business key check),
        because the prior commit result may be unknown.
        """
        with self._lock:
            if plan.business_id not in self._planned:
                raise ValueError(
                    f"retry of unknown logical transaction: business_id={plan.business_id!r}, service_id={self.service_id!r}"
                )
        self._enqueue(plan)

    def failed_plans(self) -> list[TiDBLogicalTransactionPlan]:
        """Plans awaiting a retry decision after a failed attempt.

        A plan enters this view when its latest attempt records a
        non-committed outcome and leaves it when the identity is re-enqueued
        or reaches a terminal. The driver owns the retry policy; it must
        eventually re-drive every identity here through ``submit_retry``,
        otherwise ``stop()`` fails on the still-open plan.
        """
        with self._lock:
            return [self._failed[business_id] for business_id in sorted(self._failed)]

    def _enqueue(self, plan: TiDBLogicalTransactionPlan) -> None:
        with self._lock:
            self._failed.pop(plan.business_id, None)
        deadline = plan.deadline_at_monotonic
        while True:
            now = self.clock.monotonic()
            if now >= deadline:
                self._record_terminal(plan, LedgerTerminal.INCOMPLETE_TIMEOUT)
                return
            if not self._accepting.is_set():
                self._record_terminal(plan, LedgerTerminal.INCOMPLETE_OUTSTANDING)
                return
            try:
                self._work_queue.put_nowait(plan)
                return
            except queue.Full:
                time.sleep(min(0.01, max(0.001, deadline - now)))

    def _record_terminal(
        self,
        plan: TiDBLogicalTransactionPlan,
        terminal: LedgerTerminal,
        *,
        completed_at_monotonic: float | None = None,
        result_digest: str | None = None,
    ) -> None:
        with self._lock:
            still_open = self._open.pop(plan.business_id, None)
        if still_open is None:
            raise RuntimeError(
                f"logical transaction {plan.business_id!r} reached a second terminal decision in service {self.service_id!r}"
            )
        self.ledger.append_transaction_terminal(
            business_id=plan.business_id,
            terminal=terminal,
            completed_at_monotonic=completed_at_monotonic,
            result_digest=result_digest,
        )

    # -- worker execution ------------------------------------------------------

    def start(self) -> None:
        if self._started:
            raise RuntimeError(f"OLTP pool already started: service_id={self.service_id!r}")
        self._started = True
        for index in range(self._executor._max_workers):
            self._executor.submit(self._worker_loop, index)

    def _worker_loop(self, index: int) -> None:
        while not self._stop_workers.is_set():
            try:
                plan = self._work_queue.get(timeout=0.05)
            except queue.Empty:
                continue
            with self._idle_condition:
                self._active_count += 1
            try:
                self._run_item(plan)
            finally:
                self._work_queue.task_done()
                with self._idle_condition:
                    self._active_count -= 1
                    if self._active_count == 0:
                        self._idle_condition.notify_all()

    def _run_item(self, plan: TiDBLogicalTransactionPlan) -> None:
        if self.clock.monotonic() >= plan.deadline_at_monotonic:
            self._record_terminal(plan, LedgerTerminal.INCOMPLETE_TIMEOUT)
            return
        with self._lock:
            attempt_index = self._attempt_counts.get(plan.business_id, 0)
        outcome, ended, digest, detail = self._execute_attempt(plan)
        self.ledger.append_transaction_attempt(
            business_id=plan.business_id,
            attempt=TransactionAttempt(
                attempt_index=attempt_index,
                started_at_monotonic=ended[0],
                ended_at_monotonic=ended[1],
                outcome=outcome,
                detail=detail,
            ),
        )
        if outcome is AttemptOutcome.COMMITTED:
            self._record_terminal(
                plan,
                LedgerTerminal.COMPLETED,
                completed_at_monotonic=ended[1],
                result_digest=digest,
            )
        else:
            with self._lock:
                self._failed[plan.business_id] = plan

    def _execute_attempt(self, plan: TiDBLogicalTransactionPlan) -> tuple[AttemptOutcome, tuple[float, float], str | None, dict]:
        started = self.clock.monotonic()
        try:
            connection = self._connection_factory()
        except pymysql.err.MySQLError as exc:
            ended = self.clock.monotonic()
            return (
                AttemptOutcome.CONNECTION_REFUSED,
                (started, ended),
                None,
                {"error": type(exc).__name__, "errno": exc.args[0] if exc.args else None},
            )
        try:
            self._bound_session(connection)
            digest = plan.execute(plan, connection)
            ended = self.clock.monotonic()
            connection.commit()
        except pymysql.err.MySQLError as exc:
            ended = self.clock.monotonic()
            return (
                classify_transaction_outcome(exc),
                (started, ended),
                None,
                {"error": type(exc).__name__, "errno": exc.args[0] if exc.args else None},
            )
        finally:
            connection.close()
        return AttemptOutcome.COMMITTED, (started, ended), digest, {}

    def _bound_session(self, connection: object) -> None:
        with connection.cursor() as cursor:
            cursor.execute(f"SET SESSION MAX_EXECUTION_TIME = {int(self._request_timeout_ms)}")

    # -- lifecycle --------------------------------------------------------------

    def stop_new_requests(self) -> None:
        """Input stop boundary: already accepted work continues to its deadline."""
        self._accepting.clear()

    def drain(self) -> None:
        if not self._started:
            raise RuntimeError(f"OLTP pool drain before start: service_id={self.service_id!r}")
        deadline = time.monotonic() + self._drain_grace_seconds
        with self._idle_condition:
            while not self._work_queue.empty() or self._active_count > 0:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise RuntimeError(
                        "OLTP pool drain exceeded its grace period: "
                        f"service_id={self.service_id!r}, queued={self._work_queue.qsize()}, "
                        f"active={self._active_count}, grace_seconds={self._drain_grace_seconds!r}"
                    )
                self._idle_condition.wait(timeout=min(remaining, 0.05))

    def stop(self) -> None:
        if self._stopped:
            raise RuntimeError(f"OLTP pool already stopped: service_id={self.service_id!r}")
        self._stopped = True
        self.stop_new_requests()
        self.drain()
        self._stop_workers.set()
        self._executor.shutdown(wait=True)
        with self._lock:
            outstanding = sorted(self._open)
        if outstanding:
            raise RuntimeError(
                f"OLTP pool stopped with open logical transactions: service_id={self.service_id!r}, "
                f"open_business_ids={outstanding!r}"
            )


@dataclass(frozen=True, slots=True)
class TiDBQueuedJob:
    """One delivery obligation (report, import batch, backfill, backup)."""

    job_id: str
    job_kind: str
    submitted_at_monotonic: float
    deadline_at_monotonic: float
    run: Callable[["TiDBQueuedJob", object], str]
    batch_version: str | None = None
    input_snapshot: Mapping[str, JSONValue] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.job_id, str) or not self.job_id.strip():
            raise ValueError(f"job_id must be non-empty: value={self.job_id!r}")
        if not callable(self.run):
            raise TypeError(f"job run must be callable: job_id={self.job_id!r}")


@dataclass(frozen=True, slots=True)
class TiDBJobControl:
    """Authorized queue control read from the public control table."""

    max_concurrency: int
    paused: bool = False


class TiDBJobQueueStore:
    """SQL adapter over the instance's public queue table (instance-owned).

    Implementations belong to the instance package; they run on trusted
    connections. ``read_control`` implementations may raise a MySQLError with
    errno 1146 when the public control table is absent - the queue then runs
    with its nominal concurrency, because the trusted ledger, not the control
    table, carries the delivery obligations.
    """

    def enqueue(self, job: TiDBQueuedJob, connection: object) -> None:
        raise NotImplementedError

    def claim(self, worker_id: str, connection: object) -> TiDBQueuedJob | None:
        raise NotImplementedError

    def record_result(self, job_id: str, result_digest: str, connection: object) -> None:
        raise NotImplementedError

    def read_control(self, connection: object) -> TiDBJobControl:
        raise NotImplementedError


class TiDBJobQueueRunner:
    def __init__(
        self,
        *,
        service_id: str,
        ledger: TrustedLedger,
        clock: Clock,
        store: TiDBJobQueueStore,
        connection_factory: Callable[[], object],
        max_workers: int,
        poll_interval_seconds: float = 0.2,
        drain_grace_seconds: float = 60.0,
    ):
        if max_workers < 1:
            raise ValueError(f"job runner max_workers must be at least 1: service_id={service_id!r}, value={max_workers}")
        self.service_id = service_id
        self.ledger = ledger
        self.clock = clock
        self.store = store
        self._connection_factory = connection_factory
        self._max_workers = max_workers
        self._poll_interval_seconds = poll_interval_seconds
        self._drain_grace_seconds = drain_grace_seconds
        self._planned: set[str] = set()
        self._attempt_counts: dict[str, int] = {}
        self._control_connection: object | None = None
        self._lock = threading.Lock()
        self._accepting = threading.Event()
        self._accepting.set()
        self._stop_workers = threading.Event()
        self._active_count = 0
        self._idle_condition = threading.Condition()
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix=f"persistent_scenario-tidb-jobs-{service_id}"
        )
        self._started = False
        self._stopped = False

    def submit(self, job: TiDBQueuedJob) -> None:
        """Submit a delivery obligation: ledger first, then the public queue."""
        with self._lock:
            if job.job_id in self._planned:
                raise ValueError(f"job {job.job_id!r} submitted twice in service {self.service_id!r}")
            self._planned.add(job.job_id)
        self.ledger.append_job_planned(
            job_id=job.job_id,
            service_id=self.service_id,
            job_kind=job.job_kind,
            batch_version=job.batch_version,
            input_snapshot=job.input_snapshot,
            submitted_at_monotonic=job.submitted_at_monotonic,
            deadline_at_monotonic=job.deadline_at_monotonic,
        )
        connection = self._connection_factory()
        try:
            self.store.enqueue(job, connection)
            connection.commit()
        finally:
            connection.close()

    def start(self) -> None:
        if self._started:
            raise RuntimeError(f"job runner already started: service_id={self.service_id!r}")
        self._started = True
        self._control_connection = self._connection_factory()
        for index in range(self._max_workers):
            self._executor.submit(self._worker_loop, index)

    def _read_control(self) -> TiDBJobControl:
        try:
            return self.store.read_control(self._control_connection)
        except pymysql.err.MySQLError as exc:
            if exc.args and exc.args[0] == 1146:
                return TiDBJobControl(max_concurrency=self._max_workers, paused=False)
            raise

    def _worker_loop(self, worker_index: int) -> None:
        worker_id = f"{self.service_id}-worker-{worker_index}"
        while not self._stop_workers.is_set():
            control = self._read_control()
            if control.paused or worker_index >= control.max_concurrency:
                time.sleep(self._poll_interval_seconds)
                continue
            connection = self._connection_factory()
            try:
                job = self.store.claim(worker_id, connection)
                connection.commit()
            except pymysql.err.MySQLError:
                connection.close()
                time.sleep(self._poll_interval_seconds)
                continue
            if job is None:
                connection.close()
                time.sleep(self._poll_interval_seconds)
                continue
            with self._idle_condition:
                self._active_count += 1
            try:
                self._run_job(job, connection)
            finally:
                connection.close()
                with self._idle_condition:
                    self._active_count -= 1
                    if self._active_count == 0:
                        self._idle_condition.notify_all()

    def _run_job(self, job: TiDBQueuedJob, connection: object) -> None:
        with self._lock:
            attempt_index = self._attempt_counts.get(job.job_id, 0)
            self._attempt_counts[job.job_id] = attempt_index + 1
        queued_at = job.submitted_at_monotonic
        started = self.clock.monotonic()
        try:
            digest = job.run(job, connection)
            ended = self.clock.monotonic()
            outcome = JobAttemptOutcome.SUCCEEDED
            detail: dict = {}
        except pymysql.err.MySQLError as exc:
            ended = self.clock.monotonic()
            outcome = classify_job_outcome(exc)
            digest = None
            detail = {"error": type(exc).__name__, "errno": exc.args[0] if exc.args else None}
            connection.rollback()
        self.ledger.append_job_attempt(
            job_id=job.job_id,
            attempt=JobAttempt(
                attempt_index=attempt_index,
                queued_at_monotonic=queued_at,
                started_at_monotonic=started,
                ended_at_monotonic=ended,
                outcome=outcome,
                detail=detail,
            ),
        )
        if outcome is JobAttemptOutcome.SUCCEEDED:
            self.store.record_result(job.job_id, digest, connection)
            connection.commit()
            self.ledger.append_job_terminal(
                job_id=job.job_id,
                terminal=LedgerTerminal.COMPLETED,
                delivered_at_monotonic=ended,
                result_digest=digest,
            )

    # -- lifecycle ----------------------------------------------------------

    def stop_new_requests(self) -> None:
        self._accepting.clear()

    def drain(self) -> None:
        if not self._started:
            raise RuntimeError(f"job runner drain before start: service_id={self.service_id!r}")
        deadline = time.monotonic() + self._drain_grace_seconds
        with self._idle_condition:
            while self._active_count > 0:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise RuntimeError(
                        "job runner drain exceeded its grace period: "
                        f"service_id={self.service_id!r}, active={self._active_count}, "
                        f"grace_seconds={self._drain_grace_seconds!r}"
                    )
                self._idle_condition.wait(timeout=min(remaining, 0.05))

    def stop(self) -> None:
        if self._stopped:
            raise RuntimeError(f"job runner already stopped: service_id={self.service_id!r}")
        self._stopped = True
        self.stop_new_requests()
        self.drain()
        self._stop_workers.set()
        self._executor.shutdown(wait=True)
        if self._control_connection is not None:
            self._control_connection.close()
