"""Focused tests for tidb_olap_warehouse_delivery (tidb5-portfolio, instance 2).

Covers: frozen-loader spec shape, deliverable cutoff binding (a stale result can
never pass as a newer report), cancellation that never deletes the delivery duty,
ingest validation before publication, the capability surface, and verifiers against
fake trusted connections.
"""

from __future__ import annotations

from pathlib import Path
import json

import pytest

from src.persistent_scenarios.backend.contracts import OwnershipMode
from src.persistent_scenarios.backend.tidb.capabilities.warehouse import (
    WarehouseCapabilityRegistry,
    CAPABILITIES,
    BatchArrivalCapability,
)
from src.persistent_scenarios.backend.tidb.capabilities.warehouse import reports as wh_reports
from src.persistent_scenarios.backend.tidb.capabilities.warehouse import verifiers as wh_verifiers
from src.persistent_scenarios.backend.tidb.capabilities.warehouse.reports import (
    REPORT_CONTRACTS_BY_ID,
    deliverable_batch_number,
    report_sql,
    streaming_result_digest,
)
from src.persistent_scenarios.backend.tidb.capabilities.warehouse.runtime import (
    DRAIN_GRACE_SECONDS,
    SERVICE_REPORT,
    JobControl,
    JobStore,
    QueuedJob,
    TiDBJobRunner,
    WarehouseDeliveryRuntime,
)
from src.persistent_scenarios.backend.tidb.capabilities.warehouse.store import (
    MAX_ATTEMPTS,
    QueueTables,
    make_ingest_run,
)
from src.database.system import DatabaseSystem
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.persistent_scenarios.runtime.clock import FakeClock
from src.persistent_scenarios.runtime.ledger import (
    JobAttempt,
    JobAttemptOutcome,
    LedgerTerminal,
    TrustedLedger,
)

YAML_PATH = Path("src/persistent_scenarios/tidb/tidb_olap_warehouse_delivery.yaml")


# ---------------------------------------------------------------------------
# fakes


class FakeCursor:
    """Rows are queued per SQL: each `rows_by_sql` entry is a list of results,
    one result (a list of tuples) consumed per execution."""

    def __init__(self, rows_by_sql: dict[str, list[list[tuple]]] | None = None):
        self._queues: dict[str, list[list[tuple]]] = {k: list(v) for k, v in (rows_by_sql or {}).items()}
        self._last: str = ""
        self.executed: list[tuple[str, tuple]] = []

    def execute(self, sql, args=()):
        self.executed.append((sql, args))
        self._last = sql

    def executemany(self, sql, rows):
        self.executed.append((sql, tuple(rows)))

    def _next(self) -> list[tuple]:
        queue = self._queues.get(self._last, [])
        return queue.pop(0) if queue else []

    def fetchall(self):
        return self._next()

    def fetchone(self):
        rows = self._next()
        return rows[0] if rows else None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeConnection:
    def __init__(self, rows_by_sql: dict[str, list[tuple]] | None = None):
        self._cursor = FakeCursor(rows_by_sql)
        self.committed = 0
        self.rolled_back = 0
        self.closed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed += 1

    def rollback(self):
        self.rolled_back += 1

    def close(self):
        self.closed = True


class RecordingStore(JobStore):
    """Store fake: the public queue row exists iff `rows` holds it."""

    def __init__(self, *, paused: bool = False, max_concurrency: int = 2):
        self.rows: dict[str, dict] = {}
        self.job_state_view: dict[str, tuple[str, bool, int]] = {}
        self._paused = paused
        self._max_concurrency = max_concurrency
        self.requeued: list[str] = []
        self.failed: list[str] = []

    def enqueue(self, job, connection) -> None:
        self.rows[job.job_id] = {"status": "queued", "attempts": 0}

    def claim(self, worker_id, connection):
        return None

    def record_result(self, job_id, result_digest, connection) -> None:
        self.rows[job_id]["status"] = "delivered"

    def read_control(self, connection) -> JobControl:
        return JobControl(max_concurrency=self._max_concurrency, paused=self._paused)

    def job_state(self, job_id, connection):
        return self.job_state_view[job_id]

    def requeue_row(self, connection, job_id: str) -> None:
        self.requeued.append(job_id)

    def fail_row(self, connection, job_id: str) -> None:
        self.failed.append(job_id)


class RunnerClock(FakeClock):
    pass


def make_runner(store: RecordingStore, ledger: TrustedLedger, clock: FakeClock) -> TiDBJobRunner:
    return TiDBJobRunner(
        service_id="wh_report_service",
        ledger=ledger,
        clock=clock,
        store=store,
        connection_factory=lambda name: FakeConnection(),
        application_name="test",
        max_workers=2,
    )


def run_one_job(runner: TiDBJobRunner, store: RecordingStore, job: QueuedJob, connection) -> None:
    runner._execute(job, connection)


# ---------------------------------------------------------------------------
# spec shape


def test_spec_loads_through_frozen_loader() -> None:
    spec = load_persistent_scenario(YAML_PATH)
    assert spec.system is DatabaseSystem.TIDB
    assert spec.protocol_version == "persistent-scenario-v2"
    assert spec.warmup_seconds < spec.input_stop_seconds <= spec.agent_stop_seconds <= spec.horizon_seconds
    checklist = [s for s in spec.services if s.olap_mode == "deliverable_checklist"][0]
    assert len(checklist.deliverables) == 10
    assert all(d.input_batch_binding == f"through_batch_{i}" for i in (1, 2) for d in checklist.deliverables
               if d.deliverable_id.endswith(f"batch{i}"))
    # freshness is NOT declared: one same-database fact table, binding carries the obligation
    assert all(d.requires_freshness is False for d in checklist.deliverables)
    events = spec.events
    assert [e.start_seconds for e in events] == sorted(e.start_seconds for e in events)
    assert {e.capability_id for e in events} <= set(CAPABILITIES)


# ---------------------------------------------------------------------------
# cutoff binding: stale results cannot pass as newer reports


def test_deliverable_binding_through_batch() -> None:
    assert deliverable_batch_number("region_daily_revenue_batch1") == 1
    assert deliverable_batch_number("region_group_share_batch2") == 2
    assert "batch_id <= 2" in report_sql("region_daily_revenue", 2)
    assert "batch_id <= 1" in report_sql("region_daily_revenue", 1)


def test_streaming_digest_is_order_sensitive() -> None:
    class Cursor:
        def __init__(self, rows):
            self.rows = rows

        def fetchall(self):
            return self.rows

    ordered_a = streaming_result_digest(Cursor([(1, "a"), (2, "b")]), ordered=True)[0]
    ordered_b = streaming_result_digest(Cursor([(2, "b"), (1, "a")]), ordered=True)[0]
    unordered = streaming_result_digest(Cursor([(2, "b"), (1, "a")]), ordered=False)[0]
    assert ordered_a != ordered_b
    assert ordered_a == unordered


def test_stale_delivered_digest_fails_truth_verifier(tmp_path) -> None:
    """A batch1 result delivered as the batch2 report must be flagged incorrect."""
    clock = FakeClock()
    ledger = TrustedLedger("wh_report_service", tmp_path / "stale.jsonl")
    ledger.append_job_planned(
        job_id="region_daily_revenue_batch2", service_id="wh_report_service", job_kind="report",
        batch_version=None, input_snapshot=None, submitted_at_monotonic=1.0, deadline_at_monotonic=10.0,
    )
    ledger.append_job_attempt(
        job_id="region_daily_revenue_batch2",
        attempt={"attempt_index": 1, "queued_at_monotonic": 1.0, "started_at_monotonic": 1.0,
                 "ended_at_monotonic": 2.0, "outcome": JobAttemptOutcome.SUCCEEDED.value, "detail": {}}
        if isinstance({"attempt_index": 1}, dict) else None,
    ) if False else ledger.append(
        "job_attempt",
        {"job_id": "region_daily_revenue_batch2", "attempt_index": 1, "queued_at_monotonic": 1.0,
         "started_at_monotonic": 1.0, "ended_at_monotonic": 2.0, "outcome": "succeeded", "detail": {}},
    )
    # delivered with a batch1-cutoff digest: the stale result
    cutoff1_sql = report_sql("region_daily_revenue", 1)
    conn = FakeConnection({
        cutoff1_sql: [[(1, "2026-09-18", "100", 10)]],
        report_sql("region_daily_revenue", 2): [
            [(1, "2026-09-18", "100", 10), (2, "2026-09-18", "300", 30)],
        ],
    })
    with conn.cursor() as cursor:
        cursor.execute(cutoff1_sql)
        stale_digest, _ = streaming_result_digest(cursor, ordered=True)
    ledger.append_job_terminal(
        job_id="region_daily_revenue_batch2", terminal=LedgerTerminal.COMPLETED,
        delivered_at_monotonic=2.0, result_digest=stale_digest,
    )
    from src.persistent_scenarios.runtime.ledger import LedgerView
    view = LedgerView(ledger)
    facts = wh_verifiers.wh_report_result_truth(
        conn, view,
        {"deliverables": [{"deliverable_id": "region_daily_revenue_batch2", "report_id": "region_daily_revenue"}]},
    )
    assert facts["deliverables"]["region_daily_revenue_batch2"]["present"] is True
    assert facts["deliverables"]["region_daily_revenue_batch2"]["digest_match"] is False
    assert facts["incorrect_job_ids"] == ["region_daily_revenue_batch2"]


# ---------------------------------------------------------------------------
# cancellation never deletes the delivery duty


def test_cancelled_attempt_requeues_until_attempts_exhausted(tmp_path) -> None:
    clock = FakeClock()
    ledger = TrustedLedger("wh_cxl", tmp_path / "cxl.jsonl")
    store = RecordingStore()
    runner = make_runner(store, ledger, clock)
    connection = FakeConnection()

    def attempt(job_id: str) -> None:
        store.rows.setdefault(job_id, {"status": "queued", "attempts": 0})
        store.rows[job_id]["attempts"] += 1
        store.job_state_view[job_id] = ("SELECT 1", True, store.rows[job_id]["attempts"])

        def failing_run(_job, _conn):
            import pymysql

            raise pymysql.err.OperationalError(1317, "Query execution was interrupted")

        job = QueuedJob(
            job_id=job_id, job_kind="report",
            submitted_at_monotonic=clock.monotonic(),
            deadline_at_monotonic=clock.monotonic() + 100, run=failing_run,
        )
        run_one_job(runner, store, job, connection)

    ledger.append_job_planned(
        job_id="region_daily_revenue_batch1", service_id="wh_report_service", job_kind="report",
        batch_version=None, input_snapshot=None, submitted_at_monotonic=1.0, deadline_at_monotonic=200.0,
    )

    # A requested cancellation requeues while attempts remain: no terminal, duty stays.
    for _ in range(MAX_ATTEMPTS - 1):
        attempt("region_daily_revenue_batch1")
        assert store.requeued[-1] == "region_daily_revenue_batch1"
    assert ledger.event_count("job_terminal") == 0

    # The final cancelled attempt ends as an explicit failure, never silently.
    attempt("region_daily_revenue_batch1")
    view = ledger_view_of(ledger)
    assert view.jobs()[0].terminal is LedgerTerminal.INCOMPLETE_ERROR


def test_finalizing_outstanding_jobs_keeps_the_loss(tmp_path) -> None:
    """Deleting the queue row cannot erase the obligation: the ledger ends it as loss."""
    clock = FakeClock()
    ledger = TrustedLedger("wh_loss", tmp_path / "loss.jsonl")
    ledger.append_job_planned(
        job_id="item_margin_top50_batch1", service_id="wh_report_service", job_kind="report",
        batch_version=None, input_snapshot=None, submitted_at_monotonic=1.0, deadline_at_monotonic=5.0,
    )
    ledger.finalize_outstanding(clock.monotonic())
    view = ledger_view_of(ledger)
    record = view.jobs()[0]
    assert record.terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING
    assert record.delivered_on_time is False


def ledger_view_of(ledger: TrustedLedger):
    from src.persistent_scenarios.runtime.ledger import LedgerView

    return LedgerView(ledger)


# ---------------------------------------------------------------------------
# ingest validation and atomicity boundary


def test_ingest_body_rejects_a_short_staged_batch() -> None:
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse.schema import stage_spec

    spec = stage_spec(1)
    conn = FakeConnection({
        f"SELECT COUNT(*) FROM {spec.stage_table};": [[(spec.row_count - 1,)]],
    })
    tables = type("T", (), {})()
    run = make_ingest_run(tables, "ingest_batch_1", 1, attempt_timeout_seconds=60)
    job = QueuedJob(job_id="ingest_batch_1", job_kind="ingest", submitted_at_monotonic=0.0,
                    deadline_at_monotonic=1.0, run=run)
    with pytest.raises(RuntimeError, match="staged batch validation failed"):
        run(job, conn)


# ---------------------------------------------------------------------------
# submission identity: the deliverable batch binding travels with the job


def checklist_deliverable(spec, deliverable_id: str):
    checklist = [s for s in spec.services if s.olap_mode == "deliverable_checklist"][0]
    return [d for d in checklist.deliverables if d.deliverable_id == deliverable_id][0]


def test_submit_required_report_carries_the_through_batch_binding(tmp_path) -> None:
    """The checklist compares the ledger batch_version to the
    deliverable's input_batch_binding literally, so the through_batch_N binding
    must be recorded on the job at submission."""
    deliverable = checklist_deliverable(load_persistent_scenario(YAML_PATH), "region_daily_revenue_batch2")

    clock = FakeClock()
    ledger = TrustedLedger("wh_report_service", tmp_path / "binding.jsonl")
    runner = make_runner(RecordingStore(), ledger, clock)
    runtime = WarehouseDeliveryRuntime.__new__(WarehouseDeliveryRuntime)
    runtime.clock = clock
    runtime.tables = QueueTables()
    runtime._runners = {SERVICE_REPORT: runner}
    returned = runtime.submit_required_report("region_daily_revenue", 2, clock.monotonic() + 600)

    assert returned == deliverable.deliverable_id == "region_daily_revenue_batch2"
    ledger.append_job_attempt(
        job_id=returned,
        attempt=JobAttempt(1, 0.0, 1.0, 2.0, JobAttemptOutcome.SUCCEEDED, {}),
    )
    ledger.append_job_terminal(
        job_id=returned, terminal=LedgerTerminal.COMPLETED, delivered_at_monotonic=20.0, result_digest="digest-ok"
    )
    record = ledger_view_of(ledger).jobs()[0]
    assert record.job_id == deliverable.deliverable_id
    assert record.batch_version == deliverable.input_batch_binding == "through_batch_2"


def test_checklist_pass_requires_the_bound_batch_version(tmp_path) -> None:
    """Regression pair over the real checklist evaluation: the bound job passes;
    an unbound payload (batch_version=None) fails on the binding even though the
    report itself was delivered on time."""
    from src.persistent_scenarios.evaluation.slo import evaluate_service_objectives
    from tests.persistent_scenarios._evaluation_factories import (
        LedgerBuilder,
        WINDOW,
        deliverable,
        olap_objective,
    )

    def evaluated(batch_version: str | None):
        ledger = (
            LedgerBuilder("wh_binding", tmp_path)
            .plan_job("region_daily_revenue_batch2", service_id="wh_report_service",
                      submitted_at=10.0, deadline_at=40.0, batch_version=batch_version)
            .attempt_job("region_daily_revenue_batch2")
            .deliver_job("region_daily_revenue_batch2", delivered_at=20.0, digest="digest-ok")
        )
        objective = olap_objective(
            service_id="wh_report_service",
            deliverables=[deliverable("region_daily_revenue_batch2", input_batch_binding="through_batch_2")],
        )
        return evaluate_service_objectives(
            [objective], window=WINDOW, ledgers={"wh_report_service": ledger.trusted()}, integrity_facts=()
        )

    all_pass, results = evaluated("through_batch_2")
    assert all_pass is True
    assert results[0]["deliverables"][0]["pass"] is True

    all_pass, results = evaluated(None)
    assert all_pass is False
    row = results[0]["deliverables"][0]
    assert row["terminal_outcome"] == "completed" and row["delivered_at_monotonic"] == 20.0
    assert row["input_batch_version"] is None
    assert row["pass"] is False


# ---------------------------------------------------------------------------
# capability surface


def test_batch_arrival_capability_declares_exclusive_ownership() -> None:
    clock = FakeClock()
    registry = WarehouseCapabilityRegistry(runtime_provider=lambda: None)
    event = SimpleNamespace(event_id="batch_a_arrival", entity="batch_a",
                            payload={"batch": 1, "analyze_after_ingest": False})
    declaration = registry.capability("tidb5_olap_batch_arrival").declaration(event)
    assert declaration.max_activation_seconds > 0
    assert all(resource.mode is OwnershipMode.EXCLUSIVE for resource in declaration.resources)
    assert any(resource.resource_key == "queue:ingest:batch_a" for resource in declaration.resources)


def test_batch_arrival_rejects_unknown_batch_payload() -> None:
    runtime = None  # activation never reaches the runtime: payload validation happens first
    capability = BatchArrivalCapability(runtime_provider=lambda: runtime)
    context = SimpleNamespace(
        event=SimpleNamespace(event_id="bad", entity="batch_x", payload={"batch": 9}),
        clock=FakeClock(),
    )
    with pytest.raises(ValueError, match="must select batch 1 or 2"):
        capability.activate(context)


def test_registry_rejects_unknown_capability() -> None:
    registry = WarehouseCapabilityRegistry(runtime_provider=lambda: None)
    with pytest.raises(KeyError):
        registry.capability("tidb5_olap_nonexistent")


# ---------------------------------------------------------------------------
# control-plane release audited


def test_queue_config_release_is_audited() -> None:
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse.store import QueueTables

    clock = FakeClock()
    config_select = (
        "SELECT max_workers, report_memory_quota_mb, analytics_enabled, ingest_enabled "
        "FROM wh.warehouse_config WHERE id = 1;"
    )
    audit_select = "SELECT skew_note, analyze_after_ingest FROM wh.batch_registry WHERE batch_id = 1;"
    conn = FakeConnection({
        config_select: [
            [(2, 512, 1, 1)],   # pre-read
            [(6, 512, 1, 1)],   # post-update read
            [(6, 512, 1, 1)],   # read_control
        ],
    })
    runtime = WarehouseDeliveryRuntime.__new__(WarehouseDeliveryRuntime)
    runtime.connection_factory = lambda name: conn
    runtime.tables = QueueTables()
    runtime.clock = clock
    release = runtime.apply_queue_config_release(clock.monotonic(), max_workers=6)
    assert release["max_workers"] == 6
    sqls = [sql for sql, _args in conn._cursor.executed]
    assert any("UPDATE wh.warehouse_config SET max_workers = %s" in sql for sql in sqls)
    assert any("INSERT INTO wh.config_audit" in sql for sql in sqls)


def _unused(*args):
    return None


from types import SimpleNamespace  # noqa: E402  (used above in capability tests)


# ---------------------------------------------------------------------------
# Stateful warehouse model for the hold / correction-wave / decoy mechanics

import re  # noqa: E402

from src.persistent_scenarios.backend.tidb.capabilities.warehouse.schema import (  # noqa: E402
    BATCH_A_ID,
    BATCH_B_ID,
    CORRECTION_COST_FACTOR,
    CORRECTION_PRICE_FACTOR,
    CORRECTION_ROW_MODULUS,
)
from src.persistent_scenarios.runtime.clock import FakeClock as _FakeClock  # noqa: E402

WAREHOUSE_SERVICE_LEDGERS = ("wh_report_service", "wh_heartbeat_service", "wh_ingest_service")
MODEL_ROWS_PER_BATCH = 8


def _model_rows(batch_id: int, count: int = MODEL_ROWS_PER_BATCH) -> list[dict]:
    """Tiny deterministic fact model: the same row shape as the real generator, small
    enough to recompute report truth cheaply in tests."""
    rows = []
    for index in range(count):
        order_id = batch_id * 10_000_000 + index + 1
        price = round(5 + (order_id % 50) / 4.0, 2)
        quantity = 1 + (order_id % 5)
        rows.append({
            "order_id": order_id,
            "batch_id": batch_id,
            "region_id": (order_id % 12) + 1,
            "warehouse_id": (order_id % 40) + 1,
            "item_id": (order_id % 400) + 1,
            "channel": ("app", "web", "pos")[order_id % 3],
            "quantity": quantity,
            "unit_price": price,
            "unit_cost": round(price * 0.72, 2),
            "amount": round(price * quantity, 2),
            "order_ts": f"2026-09-1{order_id % 8} 12:00:00",
        })
    return rows


def _correct_row(row: dict) -> None:
    row["unit_price"] = round(row["unit_price"] * CORRECTION_PRICE_FACTOR, 2)
    row["unit_cost"] = round(row["unit_cost"] * CORRECTION_COST_FACTOR, 2)
    row["amount"] = round(row["quantity"] * row["unit_price"], 2)


class WarehouseModel:
    """In-memory wh.* state: config, registry, queue, fact/stage rows, deliveries."""

    def __init__(self):
        self.config = {"max_workers": 2, "report_memory_quota_mb": 512,
                       "analytics_enabled": True, "ingest_enabled": True}
        self.batches = {
            BATCH_A_ID: {"skew_note": "region_skew_east", "analyze_after_ingest": False,
                          "reports_held": True, "republished_at": None, "ingest_started_at": None,
                          "ingest_finished_at": None, "analyzed_at": None, "row_count": None},
            BATCH_B_ID: {"skew_note": "region_skew_south", "analyze_after_ingest": True,
                          "reports_held": False, "republished_at": None, "ingest_started_at": None,
                          "ingest_finished_at": None, "analyzed_at": None, "row_count": None},
        }
        self.stage_rows = {BATCH_A_ID: _model_rows(BATCH_A_ID), BATCH_B_ID: _model_rows(BATCH_B_ID)}
        self.fact_rows = _model_rows(0, count=12)
        self.queue: dict[str, dict] = {}
        self.report_result: dict[str, dict] = {}
        self.audit: list[tuple] = []

    def dim_group(self, region_id: int) -> str:
        return "east" if region_id <= 4 else ("south" if region_id <= 8 else "north")

    def fact_rows_through(self, cutoff: int) -> list[dict]:
        return [row for row in self.fact_rows if row["batch_id"] <= cutoff]

    def release_hold(self, batch_id: int) -> None:
        # the agent's authorized registry UPDATE (queue_control class)
        self.batches[batch_id]["reports_held"] = False


class StatefulWhCursor:
    """Serves the report-truth SQL, ingest/validation SQL and verifier reads over the
    model; every unrecognized statement fails loudly."""

    _REPORT_HANDLERS = (
        ("SELECT region_id, DATE(order_ts)", "_truth_region_day"),
        ("SELECT item_id, SUM(amount - quantity * unit_cost)", "_truth_item_margin"),
        ("SELECT warehouse_id, DATE(order_ts)", "_truth_warehouse_day"),
        ("SELECT channel, batch_id", "_truth_channel_batch"),
        ("SELECT r.group_name", "_truth_region_group"),
    )

    def __init__(self, model: WarehouseModel):
        self._model = model
        self._pending: list[tuple] = []
        self.rowcount = 0

    def _truth_rows(self, sql: str) -> list[tuple]:
        match = re.search(r"batch_id <= (\d+)", sql)
        if match is None:
            raise AssertionError(f"report truth SQL without a batch cutoff: sql={sql!r}")
        cutoff = int(match.group(1))
        rows = self._model.fact_rows_through(cutoff)
        if sql.startswith("SELECT region_id, DATE(order_ts)"):
            return self._group(rows, lambda r: (r["region_id"], r["order_ts"].split(" ")[0]),
                               amount=lambda r: r["amount"], count=True)
        if sql.startswith("SELECT item_id, SUM(amount - quantity * unit_cost)"):
            groups: dict[int, float] = {}
            for row in rows:
                margin = round(row["amount"] - row["quantity"] * row["unit_cost"], 2)
                groups[row["item_id"]] = round(groups.get(row["item_id"], 0.0) + margin, 2)
            ranked = sorted(groups.items(), key=lambda kv: (-kv[1], kv[0]))[:50]
            return [(item_id, margin) for item_id, margin in ranked]
        if sql.startswith("SELECT warehouse_id, DATE(order_ts)"):
            return self._group(rows, lambda r: (r["warehouse_id"], r["order_ts"].split(" ")[0]),
                               amount=lambda r: r["quantity"], count=False)
        if sql.startswith("SELECT channel, batch_id"):
            return self._group(rows, lambda r: (r["channel"], r["batch_id"]),
                               amount=lambda r: r["amount"], count=True)
        if sql.startswith("SELECT r.group_name"):
            groups: dict[str, float] = {}
            for row in rows:
                group = self._model.dim_group(row["region_id"])
                groups[group] = round(groups.get(group, 0.0) + row["amount"], 2)
            return [(group, amount) for group, amount in sorted(groups.items())]
        raise AssertionError(f"unexpected truth SQL: sql={sql!r}")

    @staticmethod
    def _group(rows, key, *, amount, count):
        groups: dict[tuple, list[float]] = {}
        for row in rows:
            cell = groups.setdefault(key(row), [0.0, 0])
            cell[0] += amount(row)
            cell[1] += 1
        return [
            (*k, round(v[0], 2), v[1]) if count else (*k, round(v[0], 2))
            for k, v in sorted(groups.items())
        ]

    def execute(self, sql, args=()):
        self.rowcount = 0
        model = self._model
        if sql.startswith("SELECT region_id, DATE(order_ts)") or \
            sql.startswith("SELECT item_id, SUM(amount - quantity * unit_cost)") or \
            sql.startswith("SELECT warehouse_id, DATE(order_ts)") or \
            sql.startswith("SELECT channel, batch_id") or \
            sql.startswith("SELECT r.group_name"):
            self._pending = self._truth_rows(sql)
        elif sql.startswith("INSERT INTO wh.orders") and "SELECT order_id" in sql:
            batch_id = int(args[0])
            stage_table = {BATCH_A_ID: "wh.stage_batch_a", BATCH_B_ID: "wh.stage_batch_b"}[batch_id]
            # the fake routes the stage read through the modeled stage rows
            source = model.stage_rows[batch_id if stage_table != "wh.stage_backfill" else 3]
            published = [dict(row, batch_id=batch_id) for row in source]
            model.fact_rows = [row for row in model.fact_rows if row["batch_id"] != batch_id]
            model.fact_rows.extend(published)
            self.rowcount = len(published)
        elif sql.startswith("ANALYZE TABLE wh.orders"):
            model.batches[int(args[0])]["analyzed_at"] = float(args[1]) if len(args) > 1 else 0.0
        elif sql.startswith("ANALYZE TABLE wh.stage_batch"):
            model.audit.append(("maintenance_analyze_sql", sql))
        elif sql.startswith("SELECT COUNT(*) FROM wh.stage_batch"):
            batch_id = {BATCH_A_ID: BATCH_A_ID, BATCH_B_ID: BATCH_B_ID}[
                1 if "stage_batch_a" in sql else 2
            ]
            self._pending = [(len(model.stage_rows[batch_id]),)]
        elif sql.startswith("SELECT COUNT(*) FROM wh.orders WHERE batch_id"):
            batch_id = int(args[0])
            self._pending = [(sum(1 for row in model.fact_rows if row["batch_id"] == batch_id),)]
        elif sql.startswith("SELECT report_id, batch_cutoff FROM wh.warehouse_jobs"):
            row = model.queue[str(args[0])]
            self._pending = [(row["report_id"], row["batch_cutoff"])]
        elif sql.startswith("SELECT republished_at FROM wh.batch_registry"):
            self._pending = [(model.batches[int(args[0])]["republished_at"],)]
        elif sql.startswith("SELECT COUNT(*) FROM information_schema.tables"):
            present = 1 if "stage_batch" in str(args[0]) else 0
            self._pending = [(present,)]
        elif sql.startswith("SELECT analytics_enabled, ingest_enabled FROM wh.warehouse_config"):
            self._pending = [(model.config["analytics_enabled"], model.config["ingest_enabled"])]
        elif sql.startswith("SELECT sm.modify_count"):
            raise AssertionError("statistics verifier is not exercised by the timeline tests")
        elif sql.startswith("SELECT skew_note"):
            batch = model.batches[int(args[0])]
            self._pending = [(batch["skew_note"], batch["analyze_after_ingest"], batch["reports_held"],
                              batch["republished_at"], batch["ingest_started_at"],
                              batch["ingest_finished_at"], batch["analyzed_at"], batch["row_count"])]
        elif sql.startswith("SET SESSION"):
            pass
        else:
            raise AssertionError(f"unexpected SQL in the warehouse timeline test: sql={sql!r}")

    def fetchall(self):
        pending, self._pending = self._pending, []
        return pending

    def fetchone(self):
        pending, self._pending = self._pending, []
        return pending[0] if pending else None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class StatefulWhConnection:
    def __init__(self, model: WarehouseModel):
        self._model = model

    def cursor(self):
        return StatefulWhCursor(self._model)

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


class MemoryWarehouseTables(QueueTables):
    """The package's own store/claim/run bodies and the correction-wave/republish
    methods run unchanged; only the raw SQL becomes model state."""

    def __init__(self, model: WarehouseModel):
        super().__init__()
        self.model = model

    # -- config ---------------------------------------------------------------

    def config_row(self, connection) -> tuple[int, int, bool, bool]:
        cfg = self.model.config
        return (cfg["max_workers"], cfg["report_memory_quota_mb"],
                cfg["analytics_enabled"], cfg["ingest_enabled"])

    def update_config(self, connection, at: float, **changes: object) -> dict:
        old = dict(self.model.config)
        self.model.config.update(changes)
        self.model.audit.append((at, "wh.warehouse_config", old, dict(self.model.config)))
        return (self.model.config["max_workers"], self.model.config["report_memory_quota_mb"],
                self.model.config["analytics_enabled"], self.model.config["ingest_enabled"])

    # -- queue ----------------------------------------------------------------

    def enqueue_row(self, connection, job_id, job_type, report_id, batch_cutoff, sql_text,
                    submit_at, deadline, priority) -> None:
        self.model.queue[job_id] = {
            "job_id": job_id, "job_type": job_type, "report_id": report_id,
            "batch_cutoff": batch_cutoff, "sql_text": sql_text, "submit_at": submit_at,
            "deadline": deadline, "status": "queued", "attempts": 0, "priority": priority,
        }

    def claim_row(self, connection, job_type, worker_id, report_id_prefix=None,
                  respect_report_hold=False):
        candidates = [row for row in self.model.queue.values()
                      if row["job_type"] == job_type and row["status"] == "queued"]
        if report_id_prefix is not None:
            if report_id_prefix.startswith("!"):
                excluded = report_id_prefix[1:]
                candidates = [row for row in candidates
                              if not str(row["report_id"] or "").startswith(excluded)]
            else:
                candidates = [row for row in candidates
                              if str(row["report_id"] or "").startswith(report_id_prefix)]
        if respect_report_hold:
            candidates = [row for row in candidates
                          if not self.model.batches[row["batch_cutoff"]]["reports_held"]]
        candidates.sort(key=lambda row: (row["priority"], row["job_id"]))
        if not candidates:
            return None
        row = candidates[0]
        row["status"] = "running"
        row["attempts"] += 1
        return (row["job_id"], row["report_id"], row["batch_cutoff"], row["sql_text"],
                row["submit_at"], row["deadline"], row["attempts"])

    def job_state(self, connection, job_id) -> tuple[str, bool, int]:
        row = self.model.queue[job_id]
        return (row["sql_text"], False, row["attempts"])

    def requeue_row(self, connection, job_id) -> None:
        self.model.queue[job_id]["status"] = "queued"

    def fail_row(self, connection, job_id) -> None:
        self.model.queue[job_id]["status"] = "failed"

    def mark_delivered(self, connection, job_id) -> None:
        self.model.queue[job_id]["status"] = "delivered"

    def deliver_report_row(self, connection, job_id, report_id, batch_cutoff,
                           delivered_at, result_digest, row_count) -> None:
        self.model.queue[job_id]["status"] = "delivered"
        self.model.report_result[job_id] = {
            "report_id": report_id, "batch_cutoff": batch_cutoff,
            "delivered_at": delivered_at, "row_count": row_count, "result_digest": result_digest,
        }

    # -- registry / audit -----------------------------------------------------

    def registry_row(self, connection, batch_id):
        batch = self.model.batches[batch_id]
        return (batch["skew_note"], batch["analyze_after_ingest"], batch["reports_held"],
                batch["republished_at"], batch["ingest_started_at"], batch["ingest_finished_at"],
                batch["analyzed_at"], batch["row_count"])

    def record_batch_registry(self, connection, batch_id, started_at, finished_at,
                              analyzed_at, row_count) -> None:
        batch = self.model.batches[batch_id]
        batch["ingest_started_at"] = started_at
        batch["ingest_finished_at"] = finished_at
        batch["analyzed_at"] = analyzed_at if batch["analyzed_at"] is None else batch["analyzed_at"]
        batch["row_count"] = row_count

    def set_analyze_after_ingest(self, connection, batch_id, analyze_after_ingest, at) -> dict:
        old = self.model.batches[batch_id]["analyze_after_ingest"]
        self.model.batches[batch_id]["analyze_after_ingest"] = analyze_after_ingest
        self.model.audit.append((at, "wh.batch_registry", {"batch_id": batch_id, "analyze_after_ingest": old},
                                 {"batch_id": batch_id, "analyze_after_ingest": analyze_after_ingest}))
        return {"batch_id": batch_id, "analyze_after_ingest": analyze_after_ingest}

    def audit_registry_change(self, connection, at, table_name, old_row, new_row) -> None:
        self.model.audit.append((at, table_name, old_row, new_row))

    def record_maintenance_analyze(self, connection, at, table_name, phase) -> None:
        self.model.audit.append((at, "maintenance_analyze", {"table": table_name, "phase": phase}, {}))

    # -- correction wave ------------------------------------------------------

    def rewrite_stage_with_correction(self, connection, stage_table, at, batch_id) -> dict:
        batch_id_map = {"wh.stage_batch_a": BATCH_A_ID, "wh.stage_batch_b": BATCH_B_ID}
        model_batch = batch_id_map[stage_table]
        rows = self.model.stage_rows[model_batch]
        corrected = 0
        for row in rows:
            if row["order_id"] % CORRECTION_ROW_MODULUS == 0:
                _correct_row(row)
                corrected += 1
        self.model.audit.append((at, stage_table,
                                 {"batch_id": model_batch, "stage_rows": len(rows)},
                                 {"batch_id": model_batch, "corrected_rows": corrected}))
        return {"stage_table": stage_table, "stage_rows": len(rows), "corrected_rows": corrected}

    def republish_batch(self, connection, batch_id, at) -> dict:
        rows = [dict(row, batch_id=batch_id) for row in self.model.stage_rows[batch_id]]
        self.model.fact_rows = [row for row in self.model.fact_rows if row["batch_id"] != batch_id]
        self.model.fact_rows.extend(rows)
        batch = self.model.batches[batch_id]
        batch["republished_at"] = at
        batch["ingest_started_at"] = at
        batch["ingest_finished_at"] = at
        batch["row_count"] = len(rows)
        self.model.audit.append((at, "wh.batch_registry",
                                 {"batch_id": batch_id, "republished_at": None},
                                 {"batch_id": batch_id, "republished_rows": len(rows)}))
        return {"batch_id": batch_id, "republished_rows": len(rows), "republished_at": at}


def wh_timeline_runtime(tmp_path, model: WarehouseModel):
    clock = _FakeClock()
    ledgers = {
        service_id: TrustedLedger(f"wh_timeline:{service_id}", tmp_path / f"{service_id}.jsonl")
        for service_id in WAREHOUSE_SERVICE_LEDGERS
    }
    runtime = WarehouseDeliveryRuntime(
        connection_factory=lambda name: StatefulWhConnection(model),
        clock=clock, run_id="wh-timeline-test", ledgers=ledgers,
        input_end_monotonic=clock.monotonic() + 5100,
    )
    tables = MemoryWarehouseTables(model)
    runtime.tables = tables
    runtime._report_store.tables = tables
    runtime._heartbeat_store.tables = tables
    runtime._ingest_store.tables = tables
    return runtime, clock, tables, ledgers


def drain_service(runtime, service_id: str) -> int:
    runner = runtime._runners[service_id]
    store = runner.store
    connection = runtime.connection_factory("test-drain")
    executed = 0
    while True:
        claimed = store.claim("test-drain-w0", connection)
        if claimed is None:
            return executed
        runner._execute(claimed, connection)
        executed += 1


def activate_wh_events(runtime, clock, tables, events, *, on_event=None) -> None:
    registry = WarehouseCapabilityRegistry(runtime_provider=lambda: runtime)
    previous_start = 0
    for index, event in enumerate(events):
        if index:
            clock.advance(event.start_seconds - previous_start)
        previous_start = event.start_seconds
        context = SimpleNamespace(
            clock=clock,
            event=SimpleNamespace(event_id=event.event_id, entity=event.entity, payload=dict(event.payload)),
        )
        result = registry.capability(event.capability_id).activate(context)
        if on_event is not None:
            on_event(event)
        # the wave/maintenance threads are real background activity; the deterministic
        # drain waits for them exactly like the engine's activation boundaries do
        for thread_name in ("wave", "maintenance"):
            thread = getattr(result.handle, thread_name, None)
            if thread is not None:
                thread.join(timeout=60)
                assert not thread.is_alive()
        drain_service(runtime, "wh_ingest_service")
        drain_service(runtime, "wh_report_service")
        drain_service(runtime, "wh_heartbeat_service")


def wh_report_ledger(ledgers) -> TrustedLedger:
    return ledgers["wh_report_service"]


def test_spec_shape_puts_the_backfill_inside_batch_a_report_window() -> None:
    s = load_persistent_scenario(YAML_PATH)
    events = {e.event_id: e for e in s.events}
    backfill = events["backfill_arrival"]
    reports = events["batch_a_reports"]
    assert reports.start_seconds < backfill.start_seconds
    assert backfill.payload["batch"] == BATCH_A_ID
    assert backfill.start_seconds < reports.start_seconds + 840  # inside the report window
    assert events["batch_b_arrival"].start_seconds < events["scheduler_concurrency_release"].start_seconds
    assert list(s.safety_policy.protected_objects) == []


def test_report_claim_honors_the_batch_hold() -> None:
    """Held batch: report claims stay queued (the wave gates the batch's report class);
    heartbeat and ingest claims are untouched; releasing the hold drains the class."""
    model = WarehouseModel()
    tables = MemoryWarehouseTables(model)
    connection = StatefulWhConnection(model)
    tables.enqueue_row(connection, "region_daily_revenue_batch1", "report", "region_daily_revenue",
                       1, "SELECT 1", 0.0, 100.0, 50)
    tables.enqueue_row(connection, "bi_heartbeat_region_recent_0001", "report",
                       "bi_heartbeat_region_recent_0001", 2, "SELECT 2", 0.0, 100.0, 100)
    tables.enqueue_row(connection, "ingest_batch_1", "ingest", "ingest_batch_1", 1,
                       "staged_batch_publish", 0.0, 100.0, 10)

    assert tables.claim_row(connection, "report", "w0", report_id_prefix="!bi_heartbeat_",
                            respect_report_hold=True) is None
    heartbeat = tables.claim_row(connection, "report", "w0", report_id_prefix="bi_heartbeat_")
    assert heartbeat is not None  # the heartbeat class is not held
    ingest = tables.claim_row(connection, "ingest", "w0")
    assert ingest is not None  # the ingest path is not held

    model.release_hold(BATCH_A_ID)
    report = tables.claim_row(connection, "report", "w0", report_id_prefix="!bi_heartbeat_",
                              respect_report_hold=True)
    assert report is not None and report[0] == "region_daily_revenue_batch1"


def test_correction_wave_rewrites_stage_tables_and_republishes_batch_a() -> None:
    model = WarehouseModel()
    tables = MemoryWarehouseTables(model)
    connection = StatefulWhConnection(model)
    before = [row["amount"] for row in model.stage_rows[BATCH_A_ID]]

    tables.rewrite_stage_with_correction(connection, "wh.stage_batch_a", 1.0, BATCH_A_ID)
    tables.rewrite_stage_with_correction(connection, "wh.stage_batch_b", 1.0, BATCH_A_ID)
    result = tables.republish_batch(connection, BATCH_A_ID, 2.0)

    corrected = [row for row in model.stage_rows[BATCH_A_ID] if row["order_id"] % CORRECTION_ROW_MODULUS == 0]
    assert corrected and all(row["amount"] != old for row, old in zip(corrected, before[::CORRECTION_ROW_MODULUS]))
    assert result["republished_rows"] == len(model.stage_rows[BATCH_A_ID])
    assert model.batches[BATCH_A_ID]["republished_at"] == 2.0
    assert [row for row in model.fact_rows if row['batch_id'] == BATCH_A_ID] == model.stage_rows[BATCH_A_ID]
    assert any(entry[1] == "wh.batch_registry" for entry in model.audit)


def test_correction_wave_thread_updates_fact_truth(tmp_path) -> None:
    """The wave runs as real background driver activity: after it completes, the fact
    table truth for batch A differs from the pre-wave truth and the registry marker
    proves completion."""
    model = WarehouseModel()
    runtime, clock, tables, ledgers = wh_timeline_runtime(tmp_path, model)
    pre_wave_truth = [row["amount"] for row in model.fact_rows if row["batch_id"] == BATCH_A_ID]

    wave = runtime.start_correction_wave(BATCH_A_ID, clock.monotonic())
    wave.join(timeout=30)

    assert model.batches[BATCH_A_ID]["republished_at"] is not None
    post_wave_truth = [row["amount"] for row in model.fact_rows if row["batch_id"] == BATCH_A_ID]
    assert post_wave_truth != pre_wave_truth
    assert any(entry[1] == "wh.stage_batch_a" for entry in model.audit)
    with pytest.raises(ValueError, match="re-publishes batch A only"):
        runtime.start_correction_wave(BATCH_B_ID, clock.monotonic())


def test_release_capability_starts_the_maintenance_analyze_decoy(tmp_path) -> None:
    """Decoy: the release window carries the scheduler's real stage-statistics
    maintenance (FULL ANALYZE on the non-target stage tables), audited per phase."""
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse import QueueConcurrencyReleaseCapability

    model = WarehouseModel()
    runtime, clock, tables, ledgers = wh_timeline_runtime(tmp_path, model)
    capability = QueueConcurrencyReleaseCapability(runtime_provider=lambda: runtime)
    context = SimpleNamespace(
        clock=clock,
        event=SimpleNamespace(event_id="scheduler_concurrency_release", entity="report_pool",
                              payload={"max_workers": 6}),
    )
    result = capability.activate(context)
    handle = result.handle
    handle.maintenance.join(timeout=30)

    assert result.applied.facts["maintenance_analyze_started"] is True
    phases = [entry for entry in model.audit if entry[1] == "maintenance_analyze"]
    assert {entry[2]["table"] for entry in phases} == {"wh.stage_batch_a", "wh.stage_batch_b"}
    assert {entry[2]["phase"] for entry in phases} == {"started", "finished"}
    assert model.config["max_workers"] == 6


def test_wh_report_result_truth_flags_delivery_over_superseded_inputs(tmp_path) -> None:
    """The extended truth verifier attributes a digest mismatch to a delivery that
    happened before the batch's republish marker (honest incompleteness)."""
    model = WarehouseModel()
    tables = MemoryWarehouseTables(model)
    connection = StatefulWhConnection(model)
    clock = _FakeClock()

    ledger = TrustedLedger("wh_truth", tmp_path / "truth.jsonl")
    ledger.append_job_planned(
        job_id="region_daily_revenue_batch1", service_id="wh_report_service", job_kind="report",
        batch_version="through_batch_1", input_snapshot=None, submitted_at_monotonic=1.0,
        deadline_at_monotonic=600.0,
    )
    ledger.append("job_attempt",
                  {"job_id": "region_daily_revenue_batch1", "attempt_index": 1,
                   "queued_at_monotonic": 1.0, "started_at_monotonic": 1.0,
                   "ended_at_monotonic": 2.0, "outcome": "succeeded", "detail": {}})
    # delivered over pre-correction inputs, before the wave's republish marker
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse.reports import (
        report_sql,
        streaming_result_digest,
    )

    with connection.cursor() as cursor:
        cursor.execute(report_sql("region_daily_revenue", 1))
        stale_digest, _rows = streaming_result_digest(cursor, ordered=True)
    ledger.append_job_terminal(
        job_id="region_daily_revenue_batch1", terminal=LedgerTerminal.COMPLETED,
        delivered_at_monotonic=5.0, result_digest=stale_digest,
    )
    # the wave then re-publishes batch A: truth changes under the delivery
    tables.rewrite_stage_with_correction(connection, "wh.stage_batch_a", 10.0, BATCH_A_ID)
    tables.republish_batch(connection, BATCH_A_ID, 10.0)

    facts = wh_verifiers.wh_report_result_truth(
        connection, ledger_view_of(ledger),
        {"deliverables": [{"deliverable_id": "region_daily_revenue_batch1",
                           "report_id": "region_daily_revenue"}]},
    )
    fact = facts["deliverables"]["region_daily_revenue_batch1"]
    assert fact["digest_match"] is False
    assert fact["batch_republished_at"] == 10.0
    assert fact["delivered_after_republish"] is False
    assert facts["incorrect_job_ids"] == ["region_daily_revenue_batch1"]


def test_complete_path_defers_reports_past_the_correction_wave_and_passes(tmp_path) -> None:
    """Complete path: batch A's reports are held while the upstream
    correction wave rewrites the stage tables and re-publishes batch A; the agent
    verifies the republish marker, releases the hold, and every required report
    delivers on time over the corrected truth - batch B riding the same window."""
    model = WarehouseModel()
    runtime, clock, tables, ledgers = wh_timeline_runtime(tmp_path, model)
    events = load_persistent_scenario(YAML_PATH).events

    def on_event(event):
        if event.event_id == "batch_a_reports":
            # the hold keeps the report class queued while the wave is in flight
            assert drain_service(runtime, "wh_report_service") == 0
        if event.event_id == "batch_b_arrival":
            # agent repair: the wave has republished batch A (marker visible), so the
            # operator releases the held report class before the deadlines
            assert model.batches[BATCH_A_ID]["republished_at"] is not None
            model.release_hold(BATCH_A_ID)

    activate_wh_events(runtime, clock, tables, events, on_event=on_event)
    clock.advance(1200)
    runtime.stop()
    for ledger in ledgers.values():
        ledger.finalize_outstanding(clock.monotonic())

    from src.persistent_scenarios.runtime.ledger import LedgerView

    report_view = LedgerView(ledgers["wh_report_service"])
    jobs = {record.job_id: record for record in report_view.jobs()}
    assert len(jobs) == 10
    assert all(record.terminal is LedgerTerminal.COMPLETED and record.delivered_on_time
               for record in jobs.values())

    connection = StatefulWhConnection(model)
    truth = wh_verifiers.wh_report_result_truth(
        connection, report_view,
        {"deliverables": [{"deliverable_id": f"{report_id}_batch{batch}", "report_id": report_id}
                          for report_id in wh_reports.REQUIRED_REPORT_IDS for batch in (1, 2)]},
    )
    assert truth["incorrect_job_ids"] == []
    assert all(fact["digest_match"] and fact["delivered_after_republish"] is not False
               for fact in truth["deliverables"].values() if fact["present"])

    # the corrected batch A truth really changed: the delivered digests are the
    # corrected ones, not the pre-wave ones
    assert any(entry[1] == "wh.batch_registry" for entry in model.audit)


def test_wrong_path_releasing_the_hold_early_delivers_incomplete_reports(tmp_path) -> None:
    """Wrong path: the operator releases the hold before the correction wave finishes;
    the reports deliver over superseded inputs and the truth verifier rejects them."""
    model = WarehouseModel()
    runtime, clock, tables, ledgers = wh_timeline_runtime(tmp_path, model)
    events = load_persistent_scenario(YAML_PATH).events

    def on_event(event):
        if event.event_id == "batch_a_reports":
            model.release_hold(BATCH_A_ID)  # too early: the wave has not re-published yet

    activate_wh_events(runtime, clock, tables, events, on_event=on_event)
    clock.advance(1200)
    runtime.stop()
    for ledger in ledgers.values():
        ledger.finalize_outstanding(clock.monotonic())

    from src.persistent_scenarios.runtime.ledger import LedgerView

    report_view = LedgerView(ledgers["wh_report_service"])
    connection = StatefulWhConnection(model)
    truth = wh_verifiers.wh_report_result_truth(
        connection, report_view,
        {"deliverables": [{"deliverable_id": f"{report_id}_batch1", "report_id": report_id}
                          for report_id in wh_reports.REQUIRED_REPORT_IDS]},
    )
    stale = [job_id for job_id, fact in truth["deliverables"].items() if not fact["digest_match"]]
    assert stale, "the early deliveries must be judged incomplete against the corrected truth"
    assert all(fact["delivered_after_republish"] is False
               for fact in truth["deliverables"].values() if fact["present"])


def test_zero_path_without_the_hold_release_keeps_the_reports_outstanding(tmp_path) -> None:
    """Zero path: no operator release - the held report class never delivers and ends
    as an explicit outstanding loss the checklist evaluation rejects."""
    from src.persistent_scenarios.evaluation.slo import evaluate_service_objectives
    from src.persistent_scenarios.runtime.ledger import LedgerView, LedgerTerminal
    from src.persistent_scenarios.runtime.lifecycle import ScoringWindow

    model = WarehouseModel()
    runtime, clock, tables, ledgers = wh_timeline_runtime(tmp_path, model)
    activate_wh_events(runtime, clock, tables, load_persistent_scenario(YAML_PATH).events)
    clock.advance(1200)
    runtime.stop()
    for ledger in ledgers.values():
        ledger.finalize_outstanding(clock.monotonic())

    report_view = LedgerView(ledgers["wh_report_service"])
    jobs = {record.job_id: record for record in report_view.jobs()}
    batch1_jobs = [record for job_id, record in jobs.items() if job_id.endswith("batch1")]
    assert batch1_jobs and all(record.terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING
                               for record in batch1_jobs)

    checklist = [service for service in load_persistent_scenario(YAML_PATH).services
                 if service.objective_id == "warehouse_required_reports"][0]
    all_pass, results = evaluate_service_objectives(
        [checklist],
        window=ScoringWindow(scoring_start_monotonic=0.0, scoring_end_monotonic=6000.0,
                             input_stop_monotonic=5100.0),
        ledgers={"wh_report_service": ledgers["wh_report_service"]},
        integrity_facts=(),
    )
    assert all_pass is False
    rows = {row["deliverable_id"]: row for row in results[0]["deliverables"]}
    assert rows["region_daily_revenue_batch1"]["terminal_outcome"] == "incomplete_outstanding"
    assert rows["region_daily_revenue_batch1"]["pass"] is False
