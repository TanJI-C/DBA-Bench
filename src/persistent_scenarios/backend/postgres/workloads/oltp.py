"""Open-loop OLTP logical-transaction execution with retry merging.

The pool owns scheduling and accounting only: one business identity is
planned exactly once, retries re-enqueue the same identity and inherit the
original deadline, queueing and execution time both count into the end-to-end
latency, and every record reaches exactly one terminal state. Business SQL
belongs to the instance package through the plan's ``execute`` callable.

A failed attempt leaves the identity open without scheduling it again; the
pool reports such identities through ``failed_plans()`` so the instance
driver can apply its own retry policy mid-run via ``submit_retry``. Every
identity must be re-driven to a terminal before ``stop()``.
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import queue
import threading
import time

import psycopg2

from src.persistent_scenarios.runtime.clock import Clock
from src.persistent_scenarios.runtime.ledger import AttemptOutcome, LedgerTerminal, TransactionAttempt, TrustedLedger

from .pgerrors import WorkloadConnectionFailure, classify_transaction_outcome


@dataclass(frozen=True, slots=True)
class LogicalTransactionPlan:
    business_id: str
    tx_kind: str
    planned_at_monotonic: float
    deadline_at_monotonic: float
    execute: Callable[[LogicalTransactionPlan, object], str]

    def __post_init__(self) -> None:
        if not isinstance(self.business_id, str) or not self.business_id.strip():
            raise ValueError(f"business_id must be non-empty: value={self.business_id!r}")
        if not callable(self.execute):
            raise TypeError(f"plan execute must be callable: business_id={self.business_id!r}")


class OltpTransactionPool:
    def __init__(
        self,
        *,
        service_id: str,
        ledger: TrustedLedger,
        clock: Clock,
        concurrency: int,
        connection_factory: Callable[[str], object],
        request_timeout_ms: int,
        application_name: str,
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
        self._application_name = application_name
        self._drain_grace_seconds = drain_grace_seconds
        self._work_queue: queue.Queue[LogicalTransactionPlan] = queue.Queue(maxsize=queue_capacity)
        self._accepting = threading.Event()
        self._accepting.set()
        self._stop_workers = threading.Event()
        self._planned: set[str] = set()
        self._open: dict[str, LogicalTransactionPlan] = {}
        self._failed: dict[str, LogicalTransactionPlan] = {}
        self._attempt_counts: dict[str, int] = {}
        self._active_count = 0
        self._lock = threading.Lock()
        self._idle_condition = threading.Condition()
        self._executor = ThreadPoolExecutor(
            max_workers=concurrency, thread_name_prefix=f"persistent_scenario-oltp-{service_id}"
        )
        self._started = False
        self._stopped = False

    # -- planning and retry submission ---------------------------------------

    def submit(self, plan: LogicalTransactionPlan) -> None:
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

    def submit_retry(self, plan: LogicalTransactionPlan) -> None:
        """Client-side retry of an already planned business identity.

        The retry inherits the original deadline; retries never widen the
        ledger denominator. A retry past the deadline or after
        ``stop_new_requests`` records the matching incomplete terminal.
        """
        with self._lock:
            if plan.business_id not in self._planned:
                raise ValueError(
                    f"retry of unknown logical transaction: business_id={plan.business_id!r}, service_id={self.service_id!r}"
                )
        self._enqueue(plan)

    def failed_plans(self) -> list[LogicalTransactionPlan]:
        """Plans awaiting a retry decision after a failed attempt.

        A plan enters this view when its latest attempt records a
        non-committed outcome and leaves it when the identity is re-enqueued
        or reaches a terminal. The driver owns the retry policy; it must
        eventually re-drive every identity here through ``submit_retry``,
        otherwise ``stop()`` fails on the still-open plan.
        """
        with self._lock:
            return [self._failed[business_id] for business_id in sorted(self._failed)]

    def _enqueue(self, plan: LogicalTransactionPlan) -> None:
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
        plan: LogicalTransactionPlan,
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

    def _run_item(self, plan: LogicalTransactionPlan) -> None:
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

    def _execute_attempt(self, plan: LogicalTransactionPlan) -> tuple[AttemptOutcome, tuple[float, float], str | None, dict]:
        started = self.clock.monotonic()
        try:
            connection = self._connection_factory(self._application_name)
        except psycopg2.Error as exc:
            ended = self.clock.monotonic()
            return (
                AttemptOutcome.CONNECTION_REFUSED,
                (started, ended),
                None,
                {"error": type(exc).__name__, "pgcode": getattr(exc, "pgcode", None)},
            )
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SET LOCAL statement_timeout = '{self._request_timeout_ms}ms';")
                cursor.execute(f"SET LOCAL lock_timeout = '{self._request_timeout_ms}ms';")
            digest = plan.execute(plan, connection)
            ended = self.clock.monotonic()
            connection.commit()
        except psycopg2.Error as exc:
            ended = self.clock.monotonic()
            return (
                classify_transaction_outcome(exc),
                (started, ended),
                None,
                {"error": type(exc).__name__, "pgcode": getattr(exc, "pgcode", None)},
            )
        finally:
            connection.close()
        return AttemptOutcome.COMMITTED, (started, ended), digest, {}

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
        # Idempotent: the engine's shutdown/cleanup layers may both stop the
        # workload (e.g. after a mid-stop failure), and a second stop is a
        # no-op, not an error.
        if self._stopped:
            return
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
