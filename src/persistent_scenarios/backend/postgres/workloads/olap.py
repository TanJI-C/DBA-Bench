"""Job queue runner for OLAP deliveries, publications, backfills and backups.

The public database queue table is the real scheduling source: workers claim
rows from it and authorized agents may legitimately influence the queue.
The trusted ledger preserves every obligation, so deleting queued rows or
cancelling attempts can never erase a delivery duty - unfinished work ends as
an explicit outstanding loss.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import threading
import time

import psycopg2

from src.persistent_scenarios.model.spec import JSONValue
from src.persistent_scenarios.runtime.clock import Clock
from src.persistent_scenarios.runtime.ledger import JobAttempt, JobAttemptOutcome, LedgerTerminal, TrustedLedger

from .pgerrors import classify_job_outcome, job_failure_terminal


@dataclass(frozen=True, slots=True)
class QueuedJob:
    job_id: str
    job_kind: str
    submitted_at_monotonic: float
    deadline_at_monotonic: float
    run: Callable[[QueuedJob, object], str]
    batch_version: str | None = None
    input_snapshot: Mapping[str, JSONValue] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.job_id, str) or not self.job_id.strip():
            raise ValueError(f"job_id must be non-empty: value={self.job_id!r}")
        if not callable(self.run):
            raise TypeError(f"job run must be callable: job_id={self.job_id!r}")


@dataclass(frozen=True, slots=True)
class JobControl:
    """Authorized queue control read from the public control table."""

    max_concurrency: int
    paused: bool = False


class JobQueueStore:
    """SQL adapter over the instance's public queue table (instance-owned)."""

    def enqueue(self, job: QueuedJob, connection: object) -> None: ...

    def claim(self, worker_id: str, connection: object) -> QueuedJob | None: ...

    def record_result(self, job_id: str, result_digest: str, connection: object) -> None: ...

    def read_control(self, connection: object) -> JobControl: ...

    def failure_disposition(self, connection: object, job: QueuedJob) -> str:
        """Whether a failed attempt will be retried ('retry') or is final ('final').

        A final failure is a trusted business result: the runner closes the
        obligation with an INCOMPLETE_* terminal in the ledger. A retryable
        failure (the body requeued the row) stays open until a later attempt
        or the scoring end decides it. The default treats a body failure as
        final; stores whose rows can return to 'queued' override this by
        reading the row state.
        """
        return "final"


class JobQueueRunner:
    def __init__(
        self,
        *,
        service_id: str,
        ledger: TrustedLedger,
        clock: Clock,
        store: JobQueueStore,
        connection_factory: Callable[[str], object],
        application_name: str,
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
        self._application_name = application_name
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
            max_workers=max_workers, thread_name_prefix=f"persistent_scenario-jobs-{service_id}"
        )
        self._started = False
        self._stopped = False

    def submit(self, job: QueuedJob) -> None:
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
        connection = self._connection_factory(f"{self._application_name}-submit")
        try:
            self.store.enqueue(job, connection)
            connection.commit()
        finally:
            connection.close()

    def start(self) -> None:
        if self._started:
            raise RuntimeError(f"job runner already started: service_id={self.service_id!r}")
        self._started = True
        self._control_connection = self._connection_factory(f"{self._application_name}-control")
        for index in range(self._max_workers):
            self._executor.submit(self._worker_loop, index)

    def _read_control(self) -> JobControl:
        try:
            return self.store.read_control(self._control_connection)
        except psycopg2.Error:
            return JobControl(max_concurrency=self._max_workers, paused=False)

    def _worker_loop(self, worker_index: int) -> None:
        worker_id = f"{self.service_id}-worker-{worker_index}"
        while not self._stop_workers.is_set():
            control = self._read_control()
            if control.paused or worker_index >= control.max_concurrency:
                time.sleep(self._poll_interval_seconds)
                continue
            connection = self._connection_factory(self._application_name)
            try:
                job = self.store.claim(worker_id, connection)
                connection.commit()
            except psycopg2.Error:
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

    def _run_job(self, job: QueuedJob, connection: object) -> None:
        with self._lock:
            attempt_index = self._attempt_counts.get(job.job_id, 0)
            self._attempt_counts[job.job_id] = attempt_index + 1
        queued_at = job.submitted_at_monotonic
        started = self.clock.monotonic()
        try:
            digest = job.run(job, connection)
            ended = self.clock.monotonic()
            # The result exists only once it is consumable: persisting it is part
            # of the attempt, so a persistence failure is a failed attempt.
            self.store.record_result(job.job_id, digest, connection)
            connection.commit()
        except Exception as exc:
            # A failure is a recorded business result, not a crash: the attempt
            # lands in the ledger, a final failure closes the obligation with an
            # INCOMPLETE_* terminal, and the worker thread survives to serve the
            # remaining queue.
            self._record_failed_attempt(job, connection, attempt_index, queued_at, started, exc)
            return
        self.ledger.append_job_attempt(
            job_id=job.job_id,
            attempt=JobAttempt(
                attempt_index=attempt_index,
                queued_at_monotonic=queued_at,
                started_at_monotonic=started,
                ended_at_monotonic=ended,
                outcome=JobAttemptOutcome.SUCCEEDED,
                detail={},
            ),
        )
        self.ledger.append_job_terminal(
            job_id=job.job_id,
            terminal=LedgerTerminal.COMPLETED,
            delivered_at_monotonic=ended,
            result_digest=digest,
        )

    def _record_failed_attempt(self, job: QueuedJob, connection: object, attempt_index: int,
                               queued_at: float, started: float, exc: Exception) -> None:
        ended = self.clock.monotonic()
        if isinstance(exc, psycopg2.Error):
            outcome = classify_job_outcome(exc)
            detail: dict = {"error": type(exc).__name__, "pgcode": getattr(exc, "pgcode", None)}
            terminal = job_failure_terminal(exc)
        else:
            outcome = JobAttemptOutcome.FAILED
            detail = {"error": type(exc).__name__}
            terminal = LedgerTerminal.INCOMPLETE_ERROR
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
        try:
            disposition = self.store.failure_disposition(connection, job)
        except psycopg2.Error:
            # The connection died with the attempt: no requeued row can be
            # confirmed, so the obligation is closed as a loss.
            disposition = "final"
        if disposition == "retry":
            return
        self.ledger.append_job_terminal(
            job_id=job.job_id,
            terminal=terminal,
            delivered_at_monotonic=None,
            result_digest=None,
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
                    # Seal contract: jobs still running at seal are business
                    # losses, not an environment failure. Stop claiming, kill
                    # this service's worker backends and let each worker close
                    # its obligation through the connection-death path
                    # (failure_disposition falls back to "final" on a dead
                    # connection, so no attempt can requeue past seal).
                    self._stop_workers.set()
                    self._terminate_active_backends()
                    if not self._idle_condition.wait_for(
                        lambda: self._active_count == 0, timeout=30.0
                    ):
                        raise RuntimeError(
                            "job runner drain still active after seal-time termination: "
                            f"service_id={self.service_id!r}, active={self._active_count}, "
                            f"grace_seconds={self._drain_grace_seconds!r}"
                        )
                    break
                self._idle_condition.wait(timeout=min(remaining, 0.05))

    def _terminate_active_backends(self) -> None:
        if self._control_connection is None:
            raise RuntimeError(
                f"job runner drain cannot terminate active backends without a control connection: "
                f"service_id={self.service_id!r}"
            )
        with self._control_connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE application_name = %s AND pid <> pg_backend_pid();",
                (self._application_name,),
            )
        self._control_connection.commit()

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
