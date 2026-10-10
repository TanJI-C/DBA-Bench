"""TiDB workload executor tests: ledger semantics over fake pymysql connections."""

from dataclasses import dataclass, field
import time as time_module

import pymysql.err
import pytest

from src.persistent_scenarios.backend.tidb.workloads import (
    TiDBJobControl,
    TiDBJobQueueRunner,
    TiDBJobQueueStore,
    TiDBLogicalTransactionPlan,
    TiDBOltpTransactionPool,
    TiDBQueuedJob,
)
from src.persistent_scenarios.runtime.clock import FakeClock
from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    JobAttemptOutcome,
    LedgerTerminal,
    LedgerView,
    TrustedLedger,
)


class FakeCursor:
    def __init__(self, connection):
        self._connection = connection
        self.description = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, args=None):
        self._connection.executed.append(sql)

    def fetchall(self):
        return []


class FakeConnection:
    def __init__(self, *, commit_error: Exception | None = None):
        self.executed: list[str] = []
        self.commit_error = commit_error
        self.committed = False
        self.closed = False

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        if self.commit_error is not None:
            raise self.commit_error
        self.committed = True

    def rollback(self):
        pass

    def close(self):
        self.closed = True


def _plan_executor(plan, connection) -> str:
    connection.cursor().execute(f"INSERT INTO orders (id, sku) VALUES (1, '{plan.business_id}')")
    return f"digest:{plan.business_id}"


def _planned_plan(business_id: str, clock: FakeClock) -> TiDBLogicalTransactionPlan:
    return TiDBLogicalTransactionPlan(
        business_id=business_id,
        tx_kind="order_submit",
        planned_at_monotonic=clock.monotonic(),
        deadline_at_monotonic=clock.monotonic() + 60,
        execute=_plan_executor,
    )


def _wait_until(predicate, timeout: float = 5.0, message: str = "condition"):
    deadline = time_module.monotonic() + timeout
    while time_module.monotonic() < deadline:
        if predicate():
            return
        time_module.sleep(0.01)
    raise AssertionError(f"Timed out waiting for {message}")


def test_pool_completes_one_logical_transaction(tmp_path):
    clock = FakeClock(start=100.0)
    connection = FakeConnection()
    ledger = TrustedLedger("oltp-test", tmp_path / "oltp-ledger.jsonl")
    pool = TiDBOltpTransactionPool(
        service_id="orders",
        ledger=ledger,
        clock=clock,
        concurrency=1,
        connection_factory=lambda: connection,
        request_timeout_ms=1000,
    )
    pool.start()
    pool.submit(_planned_plan("order-1", clock))
    _wait_until(lambda: ledger.event_count("transaction_terminal") == 1, message="first terminal")
    pool.stop()

    ledger.seal()
    records = LedgerView(ledger).logical_transactions()
    assert len(records) == 1
    record = records[0]
    assert record.business_id == "order-1"
    assert record.terminal is LedgerTerminal.COMPLETED
    assert record.result_digest == "digest:order-1"
    assert record.good
    # session bounds are applied on the fresh attempt connection
    assert connection.executed[0] == "SET SESSION MAX_EXECUTION_TIME = 1000"
    assert "orders" in connection.executed[1]
    assert connection.closed


def test_pool_unknown_commit_stays_open_then_retry_completes(tmp_path):
    """commit() result unknown (2013) records the attempt; retry merges identity."""
    clock = FakeClock(start=100.0)
    ledger = TrustedLedger("oltp-unknown", tmp_path / "oltp-unknown-ledger.jsonl")
    failing = FakeConnection(commit_error=pymysql.err.OperationalError(2013, "Lost connection during query"))
    succeeding = FakeConnection()
    connections = [failing, succeeding]
    pool = TiDBOltpTransactionPool(
        service_id="orders",
        ledger=ledger,
        clock=clock,
        concurrency=1,
        connection_factory=lambda: connections.pop(0),
        request_timeout_ms=1000,
    )
    plan = _planned_plan("order-2", clock)
    pool.start()
    pool.submit(plan)
    _wait_until(lambda: ledger.event_count("transaction_attempt") == 1, message="first attempt")
    pool.submit_retry(plan)
    _wait_until(lambda: ledger.event_count("transaction_terminal") == 1, message="retry terminal")
    pool.stop()

    with pytest.raises(ValueError, match="planned twice"):
        pool.submit(plan)
    with pytest.raises(ValueError, match="unknown logical transaction"):
        pool.submit_retry(_planned_plan("order-unknown", clock))

    ledger.seal()
    records = LedgerView(ledger).logical_transactions()
    assert len(records) == 1
    record = records[0]
    assert record.business_id == "order-2"
    assert record.terminal is LedgerTerminal.COMPLETED
    assert record.result_digest == "digest:order-2"
    assert [attempt.outcome for attempt in record.attempts] == [
        AttemptOutcome.CONNECTION_REFUSED,
        AttemptOutcome.COMMITTED,
    ]
    assert record.attempts[0].detail["errno"] == 2013
    # retries never widen the ledger denominator: one planned event, two attempts
    assert ledger.event_count("planned_transaction") == 1
    assert ledger.event_count("transaction_attempt") == 2


def test_pool_failed_plans_view_tracks_retry_decisions(tmp_path):
    """A failed attempt surfaces the plan through failed_plans() until re-driven."""
    clock = FakeClock(start=100.0)
    ledger = TrustedLedger("oltp-failed", tmp_path / "oltp-failed-ledger.jsonl")
    failing = FakeConnection(commit_error=pymysql.err.OperationalError(2013, "Lost connection during query"))
    succeeding = FakeConnection()
    connections = [failing, succeeding]
    pool = TiDBOltpTransactionPool(
        service_id="orders",
        ledger=ledger,
        clock=clock,
        concurrency=1,
        connection_factory=lambda: connections.pop(0),
        request_timeout_ms=1000,
    )
    plan = _planned_plan("order-3", clock)
    pool.start()
    pool.submit(plan)
    _wait_until(lambda: pool.failed_plans(), message="failed attempt to surface in failed_plans")
    assert [p.business_id for p in pool.failed_plans()] == ["order-3"]
    pool.submit_retry(plan)
    assert pool.failed_plans() == []
    _wait_until(lambda: ledger.event_count("transaction_terminal") == 1, message="retry terminal")
    pool.stop()
    assert pool.failed_plans() == []


def test_pool_submit_after_input_stop_lands_outstanding(tmp_path):
    clock = FakeClock(start=100.0)
    ledger = TrustedLedger("oltp-stop", tmp_path / "oltp-stop-ledger.jsonl")
    pool = TiDBOltpTransactionPool(
        service_id="orders",
        ledger=ledger,
        clock=clock,
        concurrency=1,
        connection_factory=lambda: FakeConnection(),
        request_timeout_ms=1000,
    )
    pool.start()
    pool.stop_new_requests()
    pool.submit(_planned_plan("order-3", clock))
    pool.stop()

    ledger.finalize_outstanding(0.0)
    ledger.seal()
    records = LedgerView(ledger).logical_transactions()
    assert records[0].terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING


def test_pool_expired_deadline_records_timeout(tmp_path):
    """A plan submitted after its business deadline closes as INCOMPLETE_TIMEOUT."""
    clock = FakeClock(start=100.0)
    ledger = TrustedLedger("oltp-expired", tmp_path / "oltp-expired-ledger.jsonl")
    pool = TiDBOltpTransactionPool(
        service_id="orders",
        ledger=ledger,
        clock=clock,
        concurrency=1,
        connection_factory=lambda: FakeConnection(),
        request_timeout_ms=1000,
    )
    from src.persistent_scenarios.backend.tidb.workloads import TiDBLogicalTransactionPlan as Plan

    expired = Plan(
        business_id="order-4",
        tx_kind="order_submit",
        planned_at_monotonic=clock.monotonic() - 10,
        deadline_at_monotonic=clock.monotonic() - 5,
        execute=_plan_executor,
    )
    pool.submit(expired)
    ledger.seal()
    records = LedgerView(ledger).logical_transactions()
    assert records[0].terminal is LedgerTerminal.INCOMPLETE_TIMEOUT
    assert not records[0].good


@dataclass
class FakeStore(TiDBJobQueueStore):
    queue: list = field(default_factory=list)
    results: list = field(default_factory=list)
    control: TiDBJobControl | None = None
    control_error: Exception | None = None

    def enqueue(self, job, connection):
        self.queue.append(job)

    def claim(self, worker_id, connection):
        if self.queue:
            return self.queue.pop(0)
        return None

    def record_result(self, job_id, result_digest, connection):
        self.results.append((job_id, result_digest))

    def read_control(self, connection):
        if self.control_error is not None:
            raise self.control_error
        return self.control or TiDBJobControl(max_concurrency=1)


def _job(job_id: str, clock: FakeClock, run) -> TiDBQueuedJob:
    return TiDBQueuedJob(
        job_id=job_id,
        job_kind="report",
        submitted_at_monotonic=clock.monotonic(),
        deadline_at_monotonic=clock.monotonic() + 60,
        run=run,
        batch_version="b-1",
    )


def test_job_runner_delivers_and_records(tmp_path):
    clock = FakeClock(start=0.0)
    ledger = TrustedLedger("jobs-test", tmp_path / "jobs-ledger.jsonl")
    store = FakeStore()
    runner = TiDBJobQueueRunner(
        service_id="warehouse",
        ledger=ledger,
        clock=clock,
        store=store,
        connection_factory=lambda: FakeConnection(),
        max_workers=1,
        poll_interval_seconds=0.01,
    )
    runner.start()
    runner.submit(_job("report-daily", clock, lambda job, conn: f"digest:{job.job_id}"))
    _wait_until(lambda: store.results, message="job delivery")
    runner.stop()

    ledger.finalize_outstanding(0.0)
    ledger.seal()
    jobs = LedgerView(ledger).jobs()
    assert len(jobs) == 1
    assert jobs[0].job_id == "report-daily"
    assert jobs[0].terminal is LedgerTerminal.COMPLETED
    assert jobs[0].delivered_on_time
    assert jobs[0].result_digest == "digest:report-daily"
    assert store.results == [("report-daily", "digest:report-daily")]
    assert store.queue == []
    assert ledger.event_count("planned_job") == 1
    # deliverable_id == job_id identity
    assert jobs[0].job_id == "report-daily"


def test_job_runner_failure_keeps_obligation_open(tmp_path):
    clock = FakeClock(start=0.0)
    ledger = TrustedLedger("jobs-fail", tmp_path / "jobs-fail-ledger.jsonl")
    store = FakeStore()
    runner = TiDBJobQueueRunner(
        service_id="warehouse",
        ledger=ledger,
        clock=clock,
        store=store,
        connection_factory=lambda: FakeConnection(),
        max_workers=1,
        poll_interval_seconds=0.01,
    )

    def run_job(job, connection):
        raise pymysql.err.OperationalError(3024, "Query execution was interrupted")

    runner.start()
    runner.submit(_job("report-stuck", clock, run_job))
    _wait_until(lambda: ledger.event_count("job_attempt") == 1, message="job attempt")
    runner.stop()

    ledger.finalize_outstanding(0.0)
    ledger.seal()
    jobs = LedgerView(ledger).jobs()
    assert jobs[0].terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING
    assert jobs[0].attempts[0].outcome is JobAttemptOutcome.FAILED
    assert jobs[0].attempts[0].detail["errno"] == 3024
    assert store.results == []


def test_job_runner_double_submit_rejected(tmp_path):
    clock = FakeClock(start=0.0)
    ledger = TrustedLedger("jobs-dup", tmp_path / "jobs-dup-ledger.jsonl")
    store = FakeStore()
    runner = TiDBJobQueueRunner(
        service_id="warehouse",
        ledger=ledger,
        clock=clock,
        store=store,
        connection_factory=lambda: FakeConnection(),
        max_workers=1,
    )
    runner.start()
    runner.submit(_job("report-x", clock, lambda job, conn: "d"))
    with pytest.raises(ValueError, match="submitted twice"):
        runner.submit(_job("report-x", clock, lambda job, conn: "d"))
    runner.stop()


def test_job_runner_control_table_semantics(tmp_path):
    clock = FakeClock(start=0.0)
    ledger = TrustedLedger("jobs-control", tmp_path / "jobs-control-ledger.jsonl")
    store = FakeStore(control_error=pymysql.err.OperationalError(1146, "Table 'test.job_control' doesn't exist"))
    runner = TiDBJobQueueRunner(
        service_id="warehouse",
        ledger=ledger,
        clock=clock,
        store=store,
        connection_factory=lambda: FakeConnection(),
        max_workers=2,
    )
    # absent public control table: nominal concurrency, obligations stay in the ledger
    assert runner._read_control() == TiDBJobControl(max_concurrency=2, paused=False)

    store = FakeStore(control_error=pymysql.err.OperationalError(1054, "Unknown column"))
    runner = TiDBJobQueueRunner(
        service_id="warehouse",
        ledger=ledger,
        clock=clock,
        store=store,
        connection_factory=lambda: FakeConnection(),
        max_workers=2,
    )
    with pytest.raises(pymysql.err.MySQLError):
        runner._read_control()
