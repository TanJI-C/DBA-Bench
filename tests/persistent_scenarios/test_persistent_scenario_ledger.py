"""Trusted ledger, retry merging and shared workload executor accounting tests."""

from __future__ import annotations

import threading
import time

import psycopg2
import pytest

from src.persistent_scenarios.backend.postgres.workloads import (
    FreshnessRecorder,
    JobControl,
    JobQueueRunner,
    JobQueueStore,
    LogicalTransactionPlan,
    OltpTransactionPool,
    QueuedJob,
    classify_transaction_outcome,
)
from src.persistent_scenarios.runtime.clock import FakeClock
from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    FreshnessSample,
    JobAttempt,
    JobAttemptOutcome,
    JobRecord,
    LedgerTerminal,
    LedgerView,
    LogicalTransactionRecord,
    TrustedLedger,
)


def make_ledger(tmp_path, ledger_id="orders") -> TrustedLedger:
    return TrustedLedger(ledger_id, tmp_path / f"{ledger_id}.jsonl")


class TestTrustedLedger:
    def test_hash_chain_seal_and_verify(self, tmp_path):
        ledger = make_ledger(tmp_path)
        ledger.append_planned_transaction(
            business_id="tx-1", service_id="orders", tx_kind="order",
            planned_at_monotonic=10.0, deadline_at_monotonic=20.0,
        )
        ledger.append_transaction_terminal(
            business_id="tx-1", terminal=LedgerTerminal.COMPLETED,
            completed_at_monotonic=15.0, result_digest="abc",
        )
        digest = ledger.seal()
        assert digest
        ledger.verify()

    def test_verify_detects_tampering(self, tmp_path):
        ledger = make_ledger(tmp_path)
        ledger.append_planned_transaction(
            business_id="tx-1", service_id="orders", tx_kind="order",
            planned_at_monotonic=10.0, deadline_at_monotonic=20.0,
        )
        ledger.seal()
        lines = ledger.path.read_text(encoding="utf-8").splitlines()
        tampered = lines[0].replace("tx-1", "tx-X")
        ledger.path.write_text("\n".join([tampered, lines[1], ""]) + "\n", encoding="utf-8")
        with pytest.raises(ValueError, match="hash chain mismatch"):
            ledger.verify()

    def test_sealed_ledger_rejects_append(self, tmp_path):
        ledger = make_ledger(tmp_path)
        ledger.seal()
        with pytest.raises(RuntimeError, match="sealed"):
            ledger.append("planned_transaction", {"business_id": "tx-1"})

    def test_verify_detects_truncation(self, tmp_path):
        ledger = make_ledger(tmp_path)
        ledger.append_planned_transaction(
            business_id="tx-1", service_id="orders", tx_kind="order",
            planned_at_monotonic=10.0, deadline_at_monotonic=20.0,
        )
        ledger.append_transaction_terminal(
            business_id="tx-1", terminal=LedgerTerminal.COMPLETED,
            completed_at_monotonic=15.0, result_digest="abc",
        )
        ledger.seal()
        lines = ledger.path.read_text(encoding="utf-8").splitlines()
        ledger.path.write_text("\n".join([lines[0], lines[2]]) + "\n", encoding="utf-8")
        with pytest.raises(ValueError, match="sequence is broken"):
            ledger.verify()

    def test_duplicate_planning_rejected(self, tmp_path):
        ledger = make_ledger(tmp_path)
        ledger.append_planned_transaction(
            business_id="tx-1", service_id="orders", tx_kind="order",
            planned_at_monotonic=10.0, deadline_at_monotonic=20.0,
        )
        with pytest.raises(ValueError, match="already planned"):
            ledger.append_planned_transaction(
                business_id="tx-1", service_id="orders", tx_kind="order",
                planned_at_monotonic=11.0, deadline_at_monotonic=20.0,
            )

    def test_finalize_outstanding_closes_open_records(self, tmp_path):
        ledger = make_ledger(tmp_path)
        ledger.append_planned_transaction(
            business_id="tx-open", service_id="orders", tx_kind="order",
            planned_at_monotonic=10.0, deadline_at_monotonic=20.0,
        )
        ledger.append_job_planned(
            job_id="job-open", service_id="orders", job_kind="report",
            batch_version="b1", input_snapshot=None,
            submitted_at_monotonic=10.0, deadline_at_monotonic=40.0,
        )
        ledger.finalize_outstanding(now_monotonic=50.0)
        ledger.seal()
        view = LedgerView(ledger)
        transactions = view.logical_transactions()
        jobs = view.jobs()
        assert transactions[0].terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING
        assert jobs[0].terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING


class TestLedgerView:
    def test_retries_merge_into_single_record(self, tmp_path):
        ledger = make_ledger(tmp_path)
        ledger.append_planned_transaction(
            business_id="tx-1", service_id="orders", tx_kind="order",
            planned_at_monotonic=10.0, deadline_at_monotonic=40.0,
        )
        for index, outcome in enumerate((AttemptOutcome.TIMED_OUT, AttemptOutcome.COMMITTED)):
            ledger.append_transaction_attempt(
                business_id="tx-1",
                attempt=JobAttemptToTransaction(index, outcome),
            )
        ledger.append_transaction_terminal(
            business_id="tx-1", terminal=LedgerTerminal.COMPLETED,
            completed_at_monotonic=35.0, result_digest="d1",
        )
        ledger.seal()
        records = LedgerView(ledger).logical_transactions()
        assert len(records) == 1
        record = records[0]
        assert [attempt.outcome for attempt in record.attempts] == [AttemptOutcome.TIMED_OUT, AttemptOutcome.COMMITTED]
        assert record.terminal is LedgerTerminal.COMPLETED
        assert record.good is True

    def test_completed_after_deadline_is_not_good(self, tmp_path):
        ledger = make_ledger(tmp_path)
        ledger.append_planned_transaction(
            business_id="tx-1", service_id="orders", tx_kind="order",
            planned_at_monotonic=10.0, deadline_at_monotonic=20.0,
        )
        ledger.append_transaction_terminal(
            business_id="tx-1", terminal=LedgerTerminal.COMPLETED,
            completed_at_monotonic=25.0, result_digest="d1",
        )
        ledger.seal()
        record = LedgerView(ledger).logical_transactions()[0]
        assert record.terminal is LedgerTerminal.COMPLETED
        assert record.good is False

    def test_job_delivered_on_time(self, tmp_path):
        ledger = make_ledger(tmp_path)
        ledger.append_job_planned(
            job_id="job-1", service_id="reports", job_kind="report",
            batch_version="b1", input_snapshot={"cutoff": 5},
            submitted_at_monotonic=10.0, deadline_at_monotonic=30.0,
        )
        ledger.append_job_terminal(
            job_id="job-1", terminal=LedgerTerminal.COMPLETED,
            delivered_at_monotonic=28.0, result_digest="rd",
        )
        ledger.seal()
        record = LedgerView(ledger).jobs()[0]
        assert isinstance(record, JobRecord)
        assert record.delivered_on_time is True
        assert record.batch_version == "b1"

    def test_missing_terminal_rejected_at_view_time(self, tmp_path):
        ledger = make_ledger(tmp_path)
        ledger.append_planned_transaction(
            business_id="tx-1", service_id="orders", tx_kind="order",
            planned_at_monotonic=10.0, deadline_at_monotonic=20.0,
        )
        ledger.seal()
        with pytest.raises(ValueError, match="never reached a terminal state"):
            LedgerView(ledger).logical_transactions()


def JobAttemptToTransaction(index, outcome):
    from src.persistent_scenarios.runtime.ledger import TransactionAttempt

    return TransactionAttempt(index, 10.0 + index, 12.0 + index, outcome, {})


# ---------------------------------------------------------------------------
# Shared OLTP executor accounting
# ---------------------------------------------------------------------------


class FakeConnection:
    def __init__(self, behavior):
        self.behavior = behavior
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        me = self

        class Cursor:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def execute(self, sql, params=None):
                me.behavior("cursor", sql)

        return Cursor()

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def blocking_pool_plan(business_id, clock, deadline, gate, release):
    def execute(plan, connection):
        gate.set()
        release.wait(timeout=5)
        return f"digest-{plan.business_id}"

    return LogicalTransactionPlan(
        business_id=business_id,
        tx_kind="order",
        planned_at_monotonic=clock.monotonic(),
        deadline_at_monotonic=deadline,
        execute=execute,
    )


class TestOltpTransactionPool:
    def _pool(self, ledger, clock, *, concurrency=1, behavior=None):
        behavior = behavior or (lambda kind, sql: None)

        def connection_factory(application_name):
            return FakeConnection(behavior)

        return OltpTransactionPool(
            service_id="orders",
            ledger=ledger,
            clock=clock,
            concurrency=concurrency,
            connection_factory=connection_factory,
            request_timeout_ms=200,
            application_name="oltp-test",
            queue_capacity=8,
            drain_grace_seconds=5.0,
        )

    def test_success_within_deadline_is_good(self, tmp_path):
        ledger = make_ledger(tmp_path)
        clock = FakeClock(100.0)
        pool = self._pool(ledger, clock)
        pool.start()
        plan = LogicalTransactionPlan(
            "tx-1", "order", clock.monotonic(), clock.monotonic() + 10,
            lambda plan, connection: f"digest-{plan.business_id}",
        )
        pool.submit(plan)
        pool.stop()
        ledger.seal()
        record = LedgerView(ledger).logical_transactions()[0]
        assert isinstance(record, LogicalTransactionRecord)
        assert record.good is True
        assert record.result_digest == "digest-tx-1"
        assert len(record.attempts) == 1

    def test_queue_timeout_when_deadline_passes_while_blocked(self, tmp_path):
        ledger = make_ledger(tmp_path)
        clock = FakeClock(100.0)
        gate = threading.Event()
        release = threading.Event()

        def behavior(kind, sql):
            if "SELECT" in sql:
                gate.set()
                release.wait(timeout=5)

        pool = self._pool(ledger, clock, behavior=behavior)
        pool.start()
        first = blocking_pool_plan("tx-block", clock, clock.monotonic() + 50, gate, release)
        second = LogicalTransactionPlan(
            "tx-queued", "order", clock.monotonic(), clock.monotonic() + 1,
            lambda plan, connection: "unused",
        )
        pool.submit(first)
        gate.wait(timeout=5)
        pool.submit(second)
        clock.advance(2)
        release.set()
        pool.stop()
        ledger.seal()
        records = {record.business_id: record for record in LedgerView(ledger).logical_transactions()}
        assert records["tx-block"].good is True
        assert records["tx-queued"].terminal is LedgerTerminal.INCOMPLETE_TIMEOUT

    def test_retry_merges_into_same_business_id(self, tmp_path):
        ledger = make_ledger(tmp_path)
        clock = FakeClock(100.0)
        attempts = {"count": 0}

        def execute_first_fails(plan, connection):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise pg_error(psycopg2.errors.LockNotAvailable, "55P03")
            return "digest-final"

        pool = self._pool(ledger, clock)
        pool.start()
        deadline = clock.monotonic() + 10
        plan = LogicalTransactionPlan(
            "tx-1", "order", clock.monotonic(), deadline,
            execute_first_fails,
        )
        pool.submit(plan)
        waited = 0
        while attempts["count"] < 1 and waited < 200:
            time.sleep(0.01)
            waited += 1
        pool.submit_retry(plan)
        pool.stop()
        ledger.seal()
        record = LedgerView(ledger).logical_transactions()[0]
        assert len(record.attempts) == 2
        assert record.attempts[0].outcome is AttemptOutcome.TIMED_OUT
        assert record.good is True

    def test_failed_attempt_is_visible_and_retry_clears_the_view(self, tmp_path):
        ledger = make_ledger(tmp_path)
        clock = FakeClock(100.0)
        attempts = {"count": 0}

        def execute_first_fails(plan, connection):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise pg_error(psycopg2.errors.LockNotAvailable, "55P03")
            return "digest-retry"

        pool = self._pool(ledger, clock)
        pool.start()
        assert pool.failed_plans() == []
        plan = LogicalTransactionPlan(
            "tx-1", "order", clock.monotonic(), clock.monotonic() + 10,
            execute_first_fails,
        )
        pool.submit(plan)
        poll_deadline = time.monotonic() + 5
        while not pool.failed_plans() and time.monotonic() < poll_deadline:
            time.sleep(0.01)
        assert [failed.business_id for failed in pool.failed_plans()] == ["tx-1"]
        pool.submit_retry(plan)
        assert pool.failed_plans() == []
        pool.stop()
        ledger.seal()
        record = LedgerView(ledger).logical_transactions()[0]
        assert record.good is True
        assert record.result_digest == "digest-retry"
        assert len(record.attempts) == 2

    def test_retry_after_deadline_records_timeout_terminal(self, tmp_path):
        ledger = make_ledger(tmp_path)
        clock = FakeClock(100.0)

        def always_canceled(plan, connection):
            raise pg_error(psycopg2.errors.QueryCanceled, "57014")

        pool = self._pool(ledger, clock)
        pool.start()
        plan = LogicalTransactionPlan(
            "tx-1", "order", clock.monotonic(), clock.monotonic() + 10,
            always_canceled,
        )
        pool.submit(plan)
        poll_deadline = time.monotonic() + 5
        while not pool.failed_plans() and time.monotonic() < poll_deadline:
            time.sleep(0.01)
        assert [failed.business_id for failed in pool.failed_plans()] == ["tx-1"]
        clock.advance(20.0)
        pool.submit_retry(plan)
        assert pool.failed_plans() == []
        pool.stop()
        ledger.seal()
        record = LedgerView(ledger).logical_transactions()[0]
        assert record.terminal is LedgerTerminal.INCOMPLETE_TIMEOUT
        assert record.good is False
        assert len(record.attempts) == 1

    def test_stop_boundary_retry_records_outstanding(self, tmp_path):
        ledger = make_ledger(tmp_path)
        clock = FakeClock(100.0)

        def always_canceled(plan, connection):
            raise pg_error(psycopg2.errors.QueryCanceled, "57014")

        pool = self._pool(ledger, clock)
        pool.start()
        plan = LogicalTransactionPlan(
            "tx-1", "order", clock.monotonic(), clock.monotonic() + 10,
            always_canceled,
        )
        pool.submit(plan)
        poll_deadline = time.monotonic() + 5
        while not pool.failed_plans() and time.monotonic() < poll_deadline:
            time.sleep(0.01)
        pool.stop_new_requests()
        for failed in pool.failed_plans():
            pool.submit_retry(failed)
        pool.stop()
        ledger.seal()
        record = LedgerView(ledger).logical_transactions()[0]
        assert record.terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING
        assert record.good is False

    def test_error_after_success_is_rejected(self, tmp_path):
        ledger = make_ledger(tmp_path)
        clock = FakeClock(100.0)
        pool = self._pool(ledger, clock)
        pool.start()
        plan = LogicalTransactionPlan(
            "tx-1", "order", clock.monotonic(), clock.monotonic() + 10,
            lambda plan, connection: "digest",
        )
        pool.submit(plan)
        pool.stop()
        with pytest.raises(ValueError, match="terminal decided twice"):
            ledger.append_transaction_terminal(
                business_id="tx-1", terminal=LedgerTerminal.INCOMPLETE_ERROR,
                completed_at_monotonic=None, result_digest=None,
            )


# ---------------------------------------------------------------------------
# Shared job queue accounting
# ---------------------------------------------------------------------------


class FakeJobStore(JobQueueStore):
    """In-memory queue table whose rows agents may delete like a real table."""

    def __init__(self):
        self.rows: dict[str, QueuedJob] = {}
        self.results: dict[str, str] = {}
        self.control = JobControl(max_concurrency=2, paused=False)
        self.lock = threading.Lock()

    def enqueue(self, job, connection):
        with self.lock:
            self.rows[job.job_id] = job

    def claim(self, worker_id, connection):
        with self.lock:
            for job_id, job in self.rows.items():
                return job
        return None

    def record_result(self, job_id, result_digest, connection):
        with self.lock:
            self.results[job_id] = result_digest
            self.rows.pop(job_id, None)

    def read_control(self, connection):
        return self.control

    def delete(self, job_id):
        with self.lock:
            self.rows.pop(job_id, None)

    def failure_disposition(self, connection, job):
        # A row still present is queued for re-claim (requeued semantics);
        # a deleted row can never be retried again.
        with self.lock:
            return "retry" if job.job_id in self.rows else "final"


def job_runner(ledger, clock, store, *, max_workers=1):
    return JobQueueRunner(
        service_id="reports",
        ledger=ledger,
        clock=clock,
        store=store,
        connection_factory=lambda application_name: FakeConnection(lambda kind, sql: None),
        application_name="job-test",
        max_workers=max_workers,
        poll_interval_seconds=0.01,
        drain_grace_seconds=5.0,
    )


def make_job(job_id, clock, run):
    return QueuedJob(
        job_id=job_id,
        job_kind="report",
        submitted_at_monotonic=clock.monotonic(),
        deadline_at_monotonic=clock.monotonic() + 30,
        run=run,
        batch_version="b1",
        input_snapshot={"cutoff": 1},
    )


class TestJobQueueRunner:
    def test_seal_time_termination_closes_in_flight_jobs_as_losses(self, tmp_path):
        # A job still running at seal is a business loss, not an environment
        # failure: the drain terminates the service's worker backends and the
        # worker closes the obligation through the connection-death path.
        ledger = make_ledger(tmp_path, "reports")
        clock = FakeClock(100.0)

        class SealingStore(FakeJobStore):
            dead_connection = False

            def failure_disposition(self, connection, job):
                if self.dead_connection:
                    raise psycopg2.InterfaceError("connection already closed")
                return super().failure_disposition(connection, job)

        store = SealingStore()
        release = threading.Event()
        claimed = threading.Event()
        original_claim = store.claim

        def claiming_store_claim(worker_id, connection):
            job = original_claim(worker_id, connection)
            if job is not None:
                claimed.set()
            return job

        store.claim = claiming_store_claim

        def behavior(kind, sql):
            if "pg_terminate_backend" in sql:
                store.dead_connection = True
                release.set()

        runner = JobQueueRunner(
            service_id="reports",
            ledger=ledger,
            clock=clock,
            store=store,
            connection_factory=lambda application_name: FakeConnection(behavior),
            application_name="job-test",
            max_workers=1,
            poll_interval_seconds=0.01,
            drain_grace_seconds=0.3,
        )

        def blocked_run(job, connection):
            release.wait(timeout=5)
            raise psycopg2.OperationalError("terminating connection due to administrator command")

        runner.start()
        runner.submit(make_job("job-seal", clock, blocked_run))
        assert claimed.wait(timeout=5), "worker never claimed the job"
        runner.stop()
        ledger.seal()
        record = LedgerView(ledger).jobs()[0]
        assert record.terminal in (LedgerTerminal.INCOMPLETE_ERROR, LedgerTerminal.INCOMPLETE_TIMEOUT)
        assert record.delivered_on_time is False

    def test_successful_delivery_recorded_on_time(self, tmp_path):
        ledger = make_ledger(tmp_path, "reports")
        clock = FakeClock(100.0)
        store = FakeJobStore()
        runner = job_runner(ledger, clock, store)
        runner.start()
        runner.submit(make_job("job-1", clock, lambda job, connection: "result-digest"))
        deadline = time.monotonic() + 5
        while "job-1" not in store.results and time.monotonic() < deadline:
            time.sleep(0.01)
        runner.stop()
        ledger.seal()
        record = LedgerView(ledger).jobs()[0]
        assert record.terminal is LedgerTerminal.COMPLETED
        assert record.delivered_on_time is True
        assert record.batch_version == "b1"

    def test_deleted_queue_row_keeps_obligation_outstanding(self, tmp_path):
        ledger = make_ledger(tmp_path, "reports")
        clock = FakeClock(100.0)
        store = FakeJobStore()
        runner = job_runner(ledger, clock, store)
        runner.start()
        runner.submit(make_job("job-2", clock, lambda job, connection: "never"))
        store.delete("job-2")
        runner.stop_new_requests()
        runner.drain()
        runner.stop()
        ledger.finalize_outstanding(clock.monotonic())
        ledger.seal()
        record = LedgerView(ledger).jobs()[0]
        assert record.terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING
        assert record.attempts == ()

    def test_failed_attempt_then_success_merges_attempts(self, tmp_path):
        ledger = make_ledger(tmp_path, "reports")
        clock = FakeClock(100.0)
        store = FakeJobStore()
        runner = job_runner(ledger, clock, store)
        runner.start()
        calls = {"count": 0}

        def run(job, connection):
            calls["count"] += 1
            if calls["count"] == 1:
                raise pg_error(psycopg2.errors.QueryCanceled, "57014")
            return "digest-retry"

        job = make_job("job-3", clock, run)
        runner.submit(job)
        deadline = time.monotonic() + 5
        while "job-3" not in store.results and time.monotonic() < deadline:
            time.sleep(0.01)
        runner.stop()
        ledger.seal()
        record = LedgerView(ledger).jobs()[0]
        assert len(record.attempts) == 2
        assert record.attempts[0].outcome is JobAttemptOutcome.FAILED
        assert record.attempts[1].outcome is JobAttemptOutcome.SUCCEEDED
        assert record.delivered_on_time is True

    def test_paused_control_blocks_claims(self, tmp_path):
        ledger = make_ledger(tmp_path, "reports")
        clock = FakeClock(100.0)
        store = FakeJobStore()
        store.control = JobControl(max_concurrency=2, paused=True)
        runner = job_runner(ledger, clock, store)
        runner.start()
        runner.submit(make_job("job-4", clock, lambda job, connection: "result"))
        time.sleep(0.2)
        assert store.results == {}
        store.control = JobControl(max_concurrency=2, paused=False)
        deadline = time.monotonic() + 5
        while "job-4" not in store.results and time.monotonic() < deadline:
            time.sleep(0.01)
        runner.stop()
        ledger.seal()
        assert LedgerView(ledger).jobs()[0].delivered_on_time

    def test_runtime_error_is_trusted_terminal_and_worker_survives(self, tmp_path):
        ledger = make_ledger(tmp_path, "reports")
        clock = FakeClock(100.0)
        store = FakeJobStore()
        runner = job_runner(ledger, clock, store)
        runner.start()

        def broken(job, connection):
            store.delete(job.job_id)
            raise RuntimeError("boom")

        runner.submit(make_job("job-broken", clock, broken))
        runner.submit(make_job("job-after", clock, lambda job, connection: "ok-digest"))
        deadline = time.monotonic() + 5
        while "job-after" not in store.results and time.monotonic() < deadline:
            time.sleep(0.01)
        runner.stop()
        ledger.seal()
        records = {record.job_id: record for record in LedgerView(ledger).jobs()}
        assert records["job-broken"].terminal is LedgerTerminal.INCOMPLETE_ERROR
        assert records["job-broken"].attempts[0].outcome is JobAttemptOutcome.FAILED
        assert records["job-broken"].attempts[0].detail == {"error": "RuntimeError"}
        # The worker thread must survive the failure and serve the next job.
        assert records["job-after"].terminal is LedgerTerminal.COMPLETED

    def test_db_timeout_failure_closes_as_incomplete_timeout(self, tmp_path):
        ledger = make_ledger(tmp_path, "reports")
        clock = FakeClock(100.0)
        store = FakeJobStore()
        runner = job_runner(ledger, clock, store)
        runner.start()

        def timed_out(job, connection):
            store.delete(job.job_id)
            raise pg_error(psycopg2.errors.QueryCanceled, "57014")

        runner.submit(make_job("job-timeout", clock, timed_out))
        deadline = time.monotonic() + 5
        while not ledger.event_count("job_terminal") and time.monotonic() < deadline:
            time.sleep(0.01)
        runner.stop()
        ledger.seal()
        record = LedgerView(ledger).jobs()[0]
        assert record.terminal is LedgerTerminal.INCOMPLETE_TIMEOUT
        assert record.attempts[0].outcome is JobAttemptOutcome.FAILED
        assert record.attempts[0].detail == {"error": "CodedPgError", "pgcode": "57014"}

    def test_retryable_failure_stays_open_until_success(self, tmp_path):
        ledger = make_ledger(tmp_path, "reports")
        clock = FakeClock(100.0)
        store = FakeJobStore()
        runner = job_runner(ledger, clock, store)
        runner.start()
        calls = {"count": 0}

        def run(job, connection):
            calls["count"] += 1
            if calls["count"] == 1:
                raise pg_error(psycopg2.errors.QueryCanceled, "57014")
            return "digest-retry"

        runner.submit(make_job("job-retry", clock, run))
        deadline = time.monotonic() + 5
        while "job-retry" not in store.results and time.monotonic() < deadline:
            time.sleep(0.01)
        runner.stop()
        ledger.seal()
        record = LedgerView(ledger).jobs()[0]
        assert record.terminal is LedgerTerminal.COMPLETED
        assert len(record.attempts) == 2


def pg_error(error_cls, pgcode: str) -> psycopg2.Error:
    """Manually built psycopg2 errors carry a read-only pgcode; shadow it in a subclass."""
    coded = type("CodedPgError", (error_cls,), {"pgcode": property(lambda self: pgcode)})
    return coded()


class TestFreshnessRecorder:
    """Regression: the sampling loop must complete a real sample into the ledger.

    The loop runs in a daemon thread and parks its failure in ``self._error``
    (surfaced only at ``stop()``), so a broken loop is silent during the run -
    it must be driven end to end through the real thread, not via record_once.
    """

    def test_loop_drives_sample_into_ledger(self, tmp_path):
        ledger = make_ledger(tmp_path, "freshness")
        clock = FakeClock(100.0)
        calls = {"count": 0}

        def sample(sequence: int) -> FreshnessSample:
            calls["count"] += 1
            return FreshnessSample(
                sample_id=f"s-{sequence}",
                sampled_at_monotonic=clock.monotonic(),
                primary_watermark="0/AAAAAA1",
                replica_watermark="0/AAAAAA0",
                lag_seconds=0.5,
                detail={},
            )

        recorder = FreshnessRecorder(
            service_id="reports", ledger=ledger, clock=clock,
            sample=sample, interval_seconds=1.0,
        )
        recorder.start()
        deadline = time.monotonic() + 5
        while calls["count"] < 1 and time.monotonic() < deadline:
            time.sleep(0.005)
        assert calls["count"] == 1, "sampling loop never completed its first sample"
        clock.advance(1.0)
        second_deadline = time.monotonic() + 5
        while calls["count"] < 2 and time.monotonic() < second_deadline:
            clock.advance(1.0)
            time.sleep(0.005)
        recorder.stop()
        ledger.seal()
        samples = LedgerView(ledger).freshness_samples()
        # The loop thread may land extra in-flight samples before stop, but the
        # first two intervals must be sequential and fully accounted.
        assert len(samples) >= 2
        assert [sample.sample_id for sample in samples[:2]] == ["s-1", "s-2"]
        assert samples[0].lag_seconds == 0.5

    def test_broken_sample_surfaces_at_stop(self, tmp_path):
        ledger = make_ledger(tmp_path, "freshness")
        clock = FakeClock(100.0)

        def broken(sequence: int) -> FreshnessSample:
            raise RuntimeError("replica unreachable")

        recorder = FreshnessRecorder(
            service_id="reports", ledger=ledger, clock=clock,
            sample=broken, interval_seconds=1.0,
        )
        recorder.start()
        deadline = time.monotonic() + 5
        while not recorder._stop.is_set() and time.monotonic() < deadline:
            time.sleep(0.005)
        with pytest.raises(RuntimeError, match="replica unreachable"):
            recorder.stop()


class TestPgErrorClassification:
    def test_statement_timeout_maps_to_timed_out(self):
        assert classify_transaction_outcome(pg_error(psycopg2.errors.QueryCanceled, "57014")) is AttemptOutcome.TIMED_OUT

    def test_lock_timeout_maps_to_timed_out(self):
        assert classify_transaction_outcome(pg_error(psycopg2.errors.LockNotAvailable, "55P03")) is AttemptOutcome.TIMED_OUT

    def test_deadlock_maps_to_aborted(self):
        assert classify_transaction_outcome(pg_error(psycopg2.errors.DeadlockDetected, "40P01")) is AttemptOutcome.ABORTED

    def test_connection_refusal_maps_to_connection_refused(self):
        assert classify_transaction_outcome(pg_error(psycopg2.OperationalError, "53300")) is AttemptOutcome.CONNECTION_REFUSED

    def test_unknown_code_maps_to_aborted(self):
        assert classify_transaction_outcome(pg_error(psycopg2.errors.SyntaxError, "42601")) is AttemptOutcome.ABORTED
