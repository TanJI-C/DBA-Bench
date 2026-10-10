"""Unit tests for the pg5 online-change instance (contract section 9).

Covers the draft YAML contract, the release plan pass semantics (idempotent
retry, lock-timeout failure, dependency chaining), the resumable backfill
worker, the derived-column and index delivery verifiers, the legacy long
transaction mechanism and the capability payload contracts.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import psycopg2
import pytest
import yaml

from src.persistent_scenarios.backend.postgres.capabilities.online_change import CAPABILITY_REGISTRY
from src.persistent_scenarios.backend.postgres.capabilities.online_change.capabilities import (
    BackfillWorkerCapability,
    LegacyClientLongTxCapability,
    ReleaseWorkerDdlCapability,
)
from src.persistent_scenarios.backend.postgres.workloads.online_change.backfill import (
    BackfillWorker,
    parse_column_dependency,
    verify_backfill_delivery,
    verify_release_index,
)
from src.persistent_scenarios.backend.postgres.workloads.online_change.longtx import (
    repeatable_read_snapshot_opener,
)
from src.persistent_scenarios.backend.postgres.workloads.online_change.release import ReleaseWorker
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.capability import CapabilityContext, EventOccurrence
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ledger import (
    OrderBookSnapshot,
    OrderRow,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ports import EvidenceLedgerFile
from src.persistent_scenarios.runtime.clock import RealClock

from tests.persistent_scenarios.pg5_oltp_fakes import ScriptedConnection, ScriptedSource, constant_rows, pg_error, raising, rowcount_result

SCENARIO_YAML = Path("src/persistent_scenarios/postgres/pg_oltp_online_change.yaml")


def _occurrence(event_id: str, capability_id: str, params: dict, occurrence_index: int = 1) -> EventOccurrence:
    return EventOccurrence(
        event_id=event_id,
        capability_id=capability_id,
        occurrence_index=occurrence_index,
        entity="test-entity",
        params=params,
    )


def _context(source, admin_source, occurrence, tmp_path, driver=None) -> CapabilityContext:
    import uuid

    return CapabilityContext(
        run_id="run-test",
        occurrence=occurrence,
        clock=RealClock(),
        source=source,
        admin_source=admin_source or source,
        evidence=EvidenceLedgerFile(tmp_path / f"evidence-{uuid.uuid4().hex}.jsonl", "run-test"),
        driver=driver,
    )


# ---------------------------------------------------------------------------
# Draft YAML contract
# ---------------------------------------------------------------------------


def test_scenario_yaml_draft_contract():
    doc = yaml.safe_load(SCENARIO_YAML.read_text())
    assert doc["protocol_version"] == "persistent-scenario-v2"
    assert doc["scenario_id"] == "pg_oltp_online_change"
    assert doc["warmup_seconds"] < doc["input_stop_seconds"] <= doc["agent_stop_seconds"] <= doc["horizon_seconds"]
    assert doc["environment"]["workload"] == "online_change"
    assert doc["environment"]["base_image"] == "aiopsbench-pg5-oltp-online-change:h2-promo-campaign"
    from src.persistent_scenarios.backend.postgres.workloads.online_change.config import (
        BACKFILL_TASK_ID,
        COLUMN_TASK_ID,
        INDEX_TASK_ID,
        NEW_VERSION_COLUMN,
    )

    assert NEW_VERSION_COLUMN == "promo_tier"
    assert BACKFILL_TASK_ID == "backfill_promo_tier"
    events = doc["events"]
    starts = [event["start_seconds"] for event in events]
    assert starts == sorted(starts)
    event_ids = [event["event_id"] for event in events]
    assert len(event_ids) == len(set(event_ids))
    known = {"legacy_client_long_tx", "release_worker_ddl", "backfill_worker", "promo_campaign_peak"}
    assert {event["capability_id"] for event in events} <= known
    assert all("activation_timeout_seconds" in event and "response_deadline_seconds" in event for event in events)
    release_occurrences = [
        event["occurrence"] for event in events if event["capability_id"] == "release_worker_ddl"
    ]
    assert sorted(release_occurrences) == [1, 2, 3]
    reapply = [event for event in events if event["event_id"] == "release_ddl_reapply"][0]
    from src.persistent_scenarios.backend.postgres.workloads.online_change.config import (
        CONSTRAINT_WINDOW_SECONDS,
    )
    # The third pass must reach the constraint window: 3240 + 900 < 4140 with
    # the window at 3300, and the second long tx holds past the horizon.
    assert reapply["start_seconds"] + reapply["payload"]["deploy_timeout_seconds"] > CONSTRAINT_WINDOW_SECONDS
    checklist = [item for item in doc["services"] if item["load_class"] == "olap"]
    assert checklist[0]["olap_mode"] == "deliverable_checklist"
    deliverable_ids = [item["deliverable_id"] for item in checklist[0]["deliverables"]]
    assert deliverable_ids == [COLUMN_TASK_ID, INDEX_TASK_ID, BACKFILL_TASK_ID], (
        "deliverable_id == job_id (interface v1 section 2)"
    )
    verifier_checks = [item for item in doc["required_state"] if item["kind"] == "verifier"]
    assert [item["verifier_id"] for item in verifier_checks] == ["release_index_valid"]
    assert {check["verifier_id"] for check in doc["integrity_checks"]} == {
        "commerce_ledger_conservation", "backfill_completeness",
    }
    assert doc["safety_policy"]["protected_objects"]
    incident = doc["diagnosis_contract"]["incidents"][0]
    assert incident["incident_id"] == "release_blocked_long_tx_backfill"


# ---------------------------------------------------------------------------
# Release plan passes
# ---------------------------------------------------------------------------


class _FakeDriver:
    """Only the surface the release capability reads: the workload origin."""

    scoring_origin = 0.0


def _release_handlers(conn: ScriptedConnection, *, state: dict, dependent: str | None) -> None:
    """Scripts the column task row, its optional dependent and log counts.

    `state["column_status"]`, `state["alter_error"]` and `state["log_count"]`
    let each test steer the release lifecycle across retry passes.
    """

    def task_row(sql, params):
        if str(params["task_id"]) == "release_promo_tier_column":
            return ([(
                "release_promo_tier_column", "ddl",
                "ALTER TABLE shop.orders ADD COLUMN IF NOT EXISTS promo_tier TEXT",
                None, state["column_lock_timeout_ms"], 2000, 4000, False, 0.0,
                state["column_status"], 0,
            )], -1)
        return ([(
            "release_promo_tier_index", "ddl",
            "CREATE INDEX IF NOT EXISTS idx_orders_promo_tier ON shop.orders(promo_tier)",
            "task:release_promo_tier_column", 0, 2000, 4000, False, 0.0,
            state.get("index_status", "pending"), 0,
        )], -1)

    conn.set_handler("task_id, kind, ddl_statement", task_row)
    conn.set_handler("SELECT status FROM ops.release_tasks", constant_rows([("done",)]))

    def dependents(sql, params):
        # The column task has the configured dependent; the index task chains to nothing.
        if str(params["depends_on"]).endswith("index") or dependent is None:
            return ([], -1)
        return ([(dependent,)], -1)

    conn.set_handler("FROM ops.release_tasks WHERE depends_on", dependents)
    conn.set_handler("count(*) FROM ops.release_log", constant_rows([(state["log_count"],)]))
    conn.set_handler("INSERT INTO ops.release_log", rowcount_result(1))
    conn.set_handler("UPDATE ops.release_tasks SET status", rowcount_result(1))
    conn.set_handler("CREATE INDEX IF NOT EXISTS idx_orders_promo_tier", rowcount_result(-1))

    def alter(sql, params):
        error = state.get("alter_error")
        if error is not None:
            state["alter_error"] = None
            return error
        return ([], -1)

    conn.set_handler("ALTER TABLE shop.orders", alter)
    conn.set_handler("FROM pg_stat_activity WHERE application_name", constant_rows([]))


def test_release_pass_applies_plan_and_marks_tasks_done(tmp_path):
    conn = ScriptedConnection()
    state = {"column_status": "pending", "index_status": "pending", "column_lock_timeout_ms": 3000, "log_count": 0}
    _release_handlers(conn, state=state, dependent="release_promo_tier_index")
    source = ScriptedSource(lambda app: conn)
    worker = ReleaseWorker(
        source=source,
        clock=RealClock(),
        evidence=EvidenceLedgerFile(tmp_path / "release.jsonl", "run"),
        scenario_origin_monotonic=0.0,
    )
    report = worker.run_release_plan(
        start_task_id="release_promo_tier_column",
        deploy_timeout_seconds=30.0,
        stop=threading.Event(),
    )
    assert [step.outcome for step in report.steps] == ["applied", "applied"]
    assert len(conn.executed("ALTER TABLE shop.orders")) == 1
    assert len(conn.executed("CREATE INDEX IF NOT EXISTS idx_orders_promo_tier")) == 1
    assert len(conn.executed("UPDATE ops.release_tasks SET status")) == 2
    assert len(conn.executed("INSERT INTO ops.release_log")) == 2


def test_release_pass_fails_on_lock_timeout_and_retry_is_idempotent(tmp_path):
    conn = ScriptedConnection()
    state = {
        "column_status": "pending",
        "index_status": "pending",
        "column_lock_timeout_ms": 0,
        "log_count": 0,
        "alter_error": pg_error(psycopg2.OperationalError, "55P03"),
    }
    _release_handlers(conn, state=state, dependent=None)
    source = ScriptedSource(lambda app: conn)
    worker = ReleaseWorker(
        source=source,
        clock=RealClock(),
        evidence=EvidenceLedgerFile(tmp_path / "release-retry.jsonl", "run"),
        scenario_origin_monotonic=0.0,
    )
    first = worker.run_release_plan(
        start_task_id="release_promo_tier_column",
        deploy_timeout_seconds=30.0,
        stop=threading.Event(),
    )
    assert [step.outcome for step in first.steps] == ["lock_timeout"]
    assert len(conn.executed("UPDATE ops.release_tasks SET status")) == 0

    state["column_status"] = "done"
    second = worker.run_release_plan(
        start_task_id="release_promo_tier_column",
        deploy_timeout_seconds=30.0,
        stop=threading.Event(),
    )
    assert [step.outcome for step in second.steps] == ["already_done"]
    assert second.final_outcome == "already_done"


def test_release_pass_maps_statement_timeout(tmp_path):
    class PersistentError(psycopg2.OperationalError):
        pgcode = "57014"

    conn = ScriptedConnection()
    state = {
        "column_status": "pending",
        "index_status": "pending",
        "column_lock_timeout_ms": 3000,
        "log_count": 0,
        "alter_error": PersistentError(),
    }
    _release_handlers(conn, state=state, dependent=None)
    worker = ReleaseWorker(
        source=ScriptedSource(lambda app: conn),
        clock=RealClock(),
        evidence=EvidenceLedgerFile(tmp_path / "release-stmt.jsonl", "run"),
        scenario_origin_monotonic=0.0,
    )
    report = worker.run_release_plan(
        start_task_id="release_promo_tier_column",
        deploy_timeout_seconds=30.0,
        stop=threading.Event(),
    )
    assert [step.outcome for step in report.steps] == ["statement_timeout"]


def _windowed_chain_handlers(conn: ScriptedConnection, *, window_start: float, log_count: int = 0) -> dict:
    """Scripts the full plan chain: column (no window) -> completeness gate
    (change-calendar window, SET NOT NULL) -> index."""

    state = {"gate_status": "pending", "index_status": "pending"}
    rows = {
        "release_promo_tier_column": (
            "release_promo_tier_column", "ddl",
            "ALTER TABLE shop.orders ADD COLUMN IF NOT EXISTS promo_tier TEXT",
            None, 0, 2000, 4000, False, 0.0, "done", 0,
        ),
        "release_promo_tier_constraint": (
            "release_promo_tier_constraint", "ddl",
            "ALTER TABLE shop.orders ALTER COLUMN promo_tier SET NOT NULL",
            "task:release_promo_tier_column", 0, 2000, 4000, False, window_start,
            state["gate_status"], 0,
        ),
        "release_promo_tier_index": (
            "release_promo_tier_index", "ddl",
            "CREATE INDEX IF NOT EXISTS idx_orders_promo_tier ON shop.orders(promo_tier)",
            "task:release_promo_tier_constraint", 0, 2000, 4000, False, 0.0,
            state["index_status"], 0,
        ),
    }

    def task_row(sql, params):
        return ([rows[str(params["task_id"])]], -1)

    conn.set_handler("task_id, kind, ddl_statement", task_row)

    def dependents(sql, params):
        next_task = {
            "task:release_promo_tier_column": "release_promo_tier_constraint",
            "task:release_promo_tier_constraint": "release_promo_tier_index",
        }.get(str(params["depends_on"]))
        return ([(next_task,)], -1) if next_task else ([], -1)

    conn.set_handler("FROM ops.release_tasks WHERE depends_on", dependents)
    conn.set_handler("count(*) FROM ops.release_log", constant_rows([(log_count,)]))
    conn.set_handler("INSERT INTO ops.release_log", rowcount_result(1))
    conn.set_handler("UPDATE ops.release_tasks SET status", rowcount_result(1))
    conn.set_handler("ALTER COLUMN promo_tier SET NOT NULL", rowcount_result(-1))
    conn.set_handler("CREATE INDEX IF NOT EXISTS idx_orders_promo_tier", rowcount_result(-1))
    conn.set_handler("SELECT status FROM ops.release_tasks", constant_rows([("done",)]))
    return state


def test_release_pass_honours_constraint_window_before_applying(tmp_path):
    """The change-calendar window delays the AccessExclusive completeness gate:
    the pass waits (translated by the workload origin) and applies in order."""

    conn = ScriptedConnection()
    _windowed_chain_handlers(conn, window_start=1.5)
    clock = RealClock()
    worker = ReleaseWorker(
        source=ScriptedSource(lambda app: conn),
        clock=clock,
        evidence=EvidenceLedgerFile(tmp_path / "release-window.jsonl", "run"),
        scenario_origin_monotonic=clock.monotonic(),
    )
    started = time.monotonic()
    report = worker.run_release_plan(
        start_task_id="release_promo_tier_column",
        deploy_timeout_seconds=30.0,
        stop=threading.Event(),
    )
    assert time.monotonic() - started >= 1.4, "the pass must wait for the change window"
    assert [step.outcome for step in report.steps] == ["already_done", "applied", "applied"]
    applied_ddl = [statement.sql for statement in conn.executed("ALTER TABLE shop.orders")]
    assert len(applied_ddl) == 1  # the column is already applied; the gate ALTER runs
    assert "ALTER COLUMN promo_tier SET NOT NULL" in applied_ddl[0]
    assert len(conn.executed("CREATE INDEX IF NOT EXISTS idx_orders_promo_tier")) == 1
    # The deploy session must not sit idle-in-transaction across the window
    # wait: commit before idling (and before executing), or any
    # idle-in-transaction protection kills the pass mid-window.
    assert conn.commits >= 2


def test_release_pass_reports_window_miss_as_statement_timeout(tmp_path):
    """A pass whose deploy budget expires before the change window opens ends
    as a terminal statement_timeout without executing any DDL."""

    conn = ScriptedConnection()
    _windowed_chain_handlers(conn, window_start=3600.0)
    clock = RealClock()
    worker = ReleaseWorker(
        source=ScriptedSource(lambda app: conn),
        clock=clock,
        evidence=EvidenceLedgerFile(tmp_path / "release-window-miss.jsonl", "run"),
        scenario_origin_monotonic=clock.monotonic(),
    )
    report = worker.run_release_plan(
        start_task_id="release_promo_tier_column",
        deploy_timeout_seconds=5.0,
        stop=threading.Event(),
    )
    assert [step.outcome for step in report.steps] == ["already_done", "statement_timeout"]
    assert "window opened" in report.steps[-1].detail
    assert len(conn.executed("ALTER COLUMN promo_tier SET NOT NULL")) == 0


def test_release_pass_reports_premature_gate_as_check_violation(tmp_path):
    """Applying the completeness gate before the backfill settles fails the
    ALTER itself with 23502: a terminal check_violation row in the release log
    (the order-dependent delivery rejection), not a harness crash. The plan
    still reaches the dependent index build."""

    conn = ScriptedConnection()
    _windowed_chain_handlers(conn, window_start=0.5)
    # replace the instant gate handler with the honest 23502 failure
    for index, (fragment, _) in enumerate(conn.handlers):
        if fragment == "ALTER COLUMN promo_tier SET NOT NULL":
            conn.handlers[index] = (
                fragment, raising(pg_error(psycopg2.IntegrityError, "23502")),
            )
    clock = RealClock()
    worker = ReleaseWorker(
        source=ScriptedSource(lambda app: conn),
        clock=clock,
        evidence=EvidenceLedgerFile(tmp_path / "release-gate-violation.jsonl", "run"),
        scenario_origin_monotonic=clock.monotonic(),
    )
    report = worker.run_release_plan(
        start_task_id="release_promo_tier_column",
        deploy_timeout_seconds=30.0,
        stop=threading.Event(),
    )
    assert [step.outcome for step in report.steps] == ["already_done", "check_violation", "applied"]
    logged = [statement for statement in conn.executed("INSERT INTO ops.release_log")]
    assert len(logged) == 2  # gate attempt + index attempt
    gate_log = [statement for statement in logged if statement.params["task_id"] == "release_promo_tier_constraint"]
    assert gate_log[0].params["outcome"] == "check_violation"
    assert gate_log[0].params["pgcode"] == "23502"
    # the failed gate task must not be marked done
    status_updates = [statement for statement in conn.executed("UPDATE ops.release_tasks SET status")]
    assert len(status_updates) == 1  # only the index task reaches done


def test_seed_release_plan_chains_column_gate_index():
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.schema import seed_release_tasks

    column, index, backfill, gate = seed_release_tasks(
        "release_promo_tier_column", "release_promo_tier_index", "backfill_promo_tier",
        "shop.orders", "promo_tier",
        constraint_task_id="release_promo_tier_constraint",
        constraint_window_seconds=3300.0,
        backfill_rate_rows_per_second=800,
    )
    assert "ADD COLUMN IF NOT EXISTS promo_tier TEXT" in column
    assert "ALTER TABLE shop.orders ALTER COLUMN promo_tier SET NOT NULL" in gate
    assert "'task:release_promo_tier_column', 0, 3300.0)" in gate
    assert "'task:release_promo_tier_constraint', 0);" in index
    assert "'column:shop.orders:promo_tier'" in backfill
    assert "0, 2000, 800);" in backfill


def test_release_activation_observes_pass_start_without_lock_wait(tmp_path):
    """Healthy-style pass: no lock wait, plan report outlives the activation
    budget (dependent index build) — initiation itself is the observable."""

    unblock = threading.Event()
    conn = ScriptedConnection()
    state = {"column_status": "pending", "index_status": "pending",
             "column_lock_timeout_ms": 3000, "log_count": 0}
    _release_handlers(conn, state=state, dependent="release_promo_tier_index")

    def slow_index(sql, params):
        unblock.wait(10)
        return rowcount_result(-1)

    # handlers match first-registered-first; replace the helper's instant index
    # handler in place so the plan blocks inside the dependent index build.
    replaced = False
    for index, (fragment, _) in enumerate(conn.handlers):
        if fragment == "CREATE INDEX IF NOT EXISTS idx_orders_promo_tier":
            conn.handlers[index] = (fragment, slow_index)
            replaced = True
    assert replaced
    context = _context(
        ScriptedSource(lambda app: conn), None,
        _occurrence("rel-slow", "release_worker_ddl",
                    {"task_id": "release_promo_tier_column", "deploy_timeout_seconds": 20}),
        tmp_path, driver=_FakeDriver(),
    )
    capability = ReleaseWorkerDdlCapability()
    result = capability.activate(context)
    assert result.outcome == "applied"
    assert result.attempt["observed"] == "release_pass_started"
    unblock.set()
    capability.cleanup(result.handle)
    assert capability.assert_clean(result.handle)["clean"] is True


# ---------------------------------------------------------------------------
# Backfill worker and delivery verifiers
# ---------------------------------------------------------------------------


def test_backfill_worker_completes_and_resumes_idempotently(tmp_path):
    batches = {"n": 0}
    rows_done = {"n": 0}
    statuses = {"last": ""}
    campaign = {"boundary": 1_000_000}

    def backfill_connection(app: str) -> ScriptedConnection:
        conn = ScriptedConnection()
        conn.set_handler(
            "FROM ops.release_tasks WHERE task_id",
            constant_rows([("backfill_promo_tier", "backfill", None, "column:shop.orders:promo_tier", 0, 2, 100000, False, 0.0, "pending", rows_done["n"])]),
        )
        conn.set_handler("FROM information_schema.columns", constant_rows([(1,)]))
        conn.set_handler(
            "FROM ops.promo_campaign",
            lambda sql, params: ([(campaign["boundary"],)], -1),
        )

        def fill(sql, params):
            batches["n"] += 1
            moved = 2 if batches["n"] == 1 else 0
            rows_done["n"] += moved
            return ([], moved)

        conn.set_handler("UPDATE shop.orders SET promo_tier", fill)

        def progress(sql, params):
            statuses["last"] = params["status"]
            return ([], 1)

        conn.set_handler("UPDATE ops.release_tasks SET status", progress)
        return conn

    worker = BackfillWorker(
        source=ScriptedSource(backfill_connection),
        clock=RealClock(),
        evidence=EvidenceLedgerFile(tmp_path / "backfill.jsonl", "run"),
    )
    worker.start_in_background(task_id="backfill_promo_tier")
    deadline = time.monotonic() + 2.0
    while statuses["last"] != "done" and time.monotonic() < deadline:
        time.sleep(0.01)
    report = worker.stop()
    assert report.delivery_note == "completed"
    assert report.rows_backfilled == 2

    # A restarted worker resumes from the checkpointed rows_done and finishes
    # immediately when no NULL rows remain: no duplicate business writes.
    statuses["last"] = ""
    worker2 = BackfillWorker(
        source=ScriptedSource(backfill_connection),
        clock=RealClock(),
        evidence=EvidenceLedgerFile(tmp_path / "backfill-resume.jsonl", "run"),
    )
    worker2.start_in_background(task_id="backfill_promo_tier")
    deadline = time.monotonic() + 2.0
    while statuses["last"] != "done" and time.monotonic() < deadline:
        time.sleep(0.01)
    report2 = worker2.stop()
    assert report2.delivery_note == "completed"
    assert report2.rows_backfilled == 2  # carried forward from the task row checkpoint
    assert batches["n"] == 3  # the resuming pass only observed the empty batch


def test_parse_column_dependency_rejects_foreign_descriptors():
    assert parse_column_dependency("column:shop.orders:promo_tier") == ("shop.orders", "promo_tier")
    with pytest.raises(ValueError, match="column"):
        parse_column_dependency("task:release_promo_tier_column")


# ---------------------------------------------------------------------------
# Promo-campaign caliber override -> backfill definition drift
# ---------------------------------------------------------------------------


def test_backfill_resolves_campaign_override_per_batch(tmp_path):
    """The worker resolves its tier boundary at batch time: batches processed
    while the campaign row is active use the campaign caliber (drift), batches
    outside the campaign window keep the canonical derivation."""

    from src.persistent_scenarios.backend.postgres.workloads.online_change.config import (
        PROMO_VIP_THRESHOLD_OVERRIDE_CENTS,
    )
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.schema import VIP_AMOUNT_CENTS

    campaign = {"boundary": PROMO_VIP_THRESHOLD_OVERRIDE_CENTS}
    batch_boundaries: list[object] = []
    batches = {"n": 0}
    rows_done = {"n": 0}
    statuses = {"last": ""}

    def backfill_connection(app: str) -> ScriptedConnection:
        conn = ScriptedConnection()
        conn.set_handler(
            "FROM ops.release_tasks WHERE task_id",
            constant_rows([("backfill_promo_tier", "backfill", None, "column:shop.orders:promo_tier",
                            0, 2, 100000, False, 0.0, "running", rows_done["n"])]),
        )
        conn.set_handler("FROM information_schema.columns", constant_rows([(1,)]))
        conn.set_handler("FROM ops.promo_campaign", lambda sql, params: ([(campaign["boundary"],)], -1))

        def fill(sql, params):
            batches["n"] += 1
            batch_boundaries.append(params["vip"])
            if batches["n"] >= 3:
                campaign["boundary"] = VIP_AMOUNT_CENTS  # campaign closes mid-run
            moved = 0 if batches["n"] > 3 else 1
            return ([], moved)

        conn.set_handler("UPDATE shop.orders SET promo_tier", fill)

        def progress(sql, params):
            statuses["last"] = params["status"]
            return ([], 1)

        conn.set_handler("UPDATE ops.release_tasks SET status", progress)
        return conn

    worker = BackfillWorker(
        source=ScriptedSource(backfill_connection),
        clock=RealClock(),
        evidence=EvidenceLedgerFile(tmp_path / "backfill-drift.jsonl", "run"),
    )
    worker.start_in_background(task_id="backfill_promo_tier")
    deadline = time.monotonic() + 2.0
    while statuses["last"] != "done" and time.monotonic() < deadline:
        time.sleep(0.01)
    report = worker.stop()
    assert report.delivery_note == "completed"
    assert batch_boundaries == [
        PROMO_VIP_THRESHOLD_OVERRIDE_CENTS,
        PROMO_VIP_THRESHOLD_OVERRIDE_CENTS,
        PROMO_VIP_THRESHOLD_OVERRIDE_CENTS,
        VIP_AMOUNT_CENTS,
    ], "campaign-window batches must take the campaign caliber, later batches the canonical rule"


def test_image_history_drift_band_is_deterministic():
    """Fixture gate for the image's HISTORY_ORDERS_SQL: the definition-drift
    band [VIP_AMOUNT_CENTS, campaign override) is exactly the promo rows with
    qty=5 (amount 260_000 * 5 = 1_300_000 cents) — 100_000 of 500_000 rows —
    and every band row is mislabelled under the campaign caliber."""

    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.schema import (
        VIP_AMOUNT_CENTS,
        promo_tier_for_amount,
    )
    from src.persistent_scenarios.backend.postgres.workloads.online_change.config import (
        HISTORY_ORDER_COUNT,
        PROMO_VIP_THRESHOLD_OVERRIDE_CENTS,
    )

    assert HISTORY_ORDER_COUNT == 500_000
    drift_rows: list[tuple[str, int]] = []
    for g in range(HISTORY_ORDER_COUNT):
        promo = g % 5 < 4
        qty = 1 + ((g * 7) % 5)
        amount = 260_000 * qty if promo else (1000 + (((g * 3) % 20) * 7)) * qty
        if promo and VIP_AMOUNT_CENTS <= amount < PROMO_VIP_THRESHOLD_OVERRIDE_CENTS:
            drift_rows.append((f"hist-{g:08d}", amount))
            assert promo_tier_for_amount(amount) == "vip", amount
            assert amount >= PROMO_VIP_THRESHOLD_OVERRIDE_CENTS or promo_tier_for_amount(amount) != "standard"
    assert len(drift_rows) == 100_000
    assert {amount for _, amount in drift_rows} == {1_300_000}


def test_zero_path_backfill_window_overlaps_the_campaign():
    """Zero-action determinism: the column cannot exist before the first long
    transaction exits (600 arrival + 1500 hold), so the rate-limited backfill's
    duration floor must keep it running past the promo peak — the overlap that
    makes the definition drift fire without any timing luck."""

    from src.persistent_scenarios.backend.postgres.workloads.online_change.config import (
        BACKFILL_RATE_ROWS_PER_SECOND,
        HISTORY_ORDER_COUNT,
        LONG_TX1_EXIT_LOWER_BOUND_SECONDS,
        PROMO_PEAK_SECONDS,
    )

    duration_floor = HISTORY_ORDER_COUNT / BACKFILL_RATE_ROWS_PER_SECOND
    assert LONG_TX1_EXIT_LOWER_BOUND_SECONDS + duration_floor > PROMO_PEAK_SECONDS + 60.0, (
        "the zero-path backfill must still be running at least 60s after the promo peak opens"
    )


def test_campaign_seed_sql_schedules_the_override():
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.schema import seed_promo_campaign

    sql = seed_promo_campaign("promo-2026-h2", "promo", 2_000_000)
    assert "'promo-2026-h2', 'promo', 2000000, 'scheduled', NULL" in sql


def _snapshot_with_tiers(promo_tier_present: bool) -> OrderBookSnapshot:
    tier = lambda amount: ("vip" if amount >= 1000000 else "standard") if promo_tier_present else None
    return OrderBookSnapshot(
        orders={
            "o1": OrderRow("o1", "PROMO-SKU-1", 4, 1040000, "paid", 1.0, tier(1040000)),
            "o2": OrderRow("o2", "SKU-0001", 1, 1007, "paid", 2.0, tier(1007)),
        },
        archived_orders={},
        payments={},
        inventory={},
        initial_inventory={},
        seed_order_ids=frozenset(),
        promo_tier_present=promo_tier_present,
    )


def test_backfill_delivery_verifier_enforces_derived_rule():
    assert verify_backfill_delivery(_snapshot_with_tiers(True)) == ()
    failures = verify_backfill_delivery(_snapshot_with_tiers(False))
    assert failures == ("promo_tier column is missing from shop.orders; the release did not complete",)

    snapshot = _snapshot_with_tiers(True)
    broken = OrderBookSnapshot(
        orders={
            "o1": OrderRow("o1", "PROMO-SKU-1", 4, 1040000, "paid", 1.0, "standard"),  # wrong tier
            "o2": OrderRow("o2", "SKU-0001", 1, 1007, "paid", 2.0, None),  # unbackfilled
        },
        archived_orders={},
        payments={},
        inventory={},
        initial_inventory={},
        seed_order_ids=frozenset(),
        promo_tier_present=True,
    )
    failures = verify_backfill_delivery(broken)
    assert len(failures) == 2
    assert any("diverges" in failure for failure in failures)
    assert any("unbackfilled" in failure for failure in failures)


def test_backfill_verifier_emits_evaluation_ids(tmp_path):
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.verifiers import run_verifier

    snapshot = _snapshot_with_tiers(True)
    broken_rows = OrderBookSnapshot(
        orders={
            "o1": OrderRow("o1", "PROMO-SKU-1", 4, 1040000, "paid", 1.0, "standard"),  # wrong tier
            "o2": OrderRow("o2", "SKU-0001", 1, 1007, "paid", 2.0, None),  # unbackfilled
        },
        archived_orders={},
        payments={},
        inventory={},
        initial_inventory={},
        seed_order_ids=frozenset(),
        promo_tier_present=True,
    )
    fact = run_verifier(
        "backfill_completeness", {"backfill_job_id": "backfill_promo_tier"},
        ops=(), snapshot=broken_rows,
    )
    assert fact["kind"] == "result_truth"
    assert fact["passed"] is False
    assert set(fact["incorrect_business_ids"]) == {"o1", "o2"}
    assert fact["incorrect_job_ids"] == ["backfill_promo_tier"]

    healthy = run_verifier(
        "backfill_completeness", {"backfill_job_id": "backfill_promo_tier"},
        ops=(), snapshot=_snapshot_with_tiers(True),
    )
    assert healthy["passed"] is True
    assert healthy["incorrect_business_ids"] == []
    assert healthy["incorrect_job_ids"] == []
    del tmp_path


def test_release_index_verifier_requires_a_valid_serving_index():
    assert verify_release_index({"idx_orders_promo_tier": (True, {"promo_tier"})}, table="shop.orders", column="promo_tier") == ()
    failures = verify_release_index({"idx_orders_promo_tier": (False, {"promo_tier"})}, table="shop.orders", column="promo_tier")
    assert failures and "no valid index" in failures[0]
    failures = verify_release_index({"idx_other": (True, {"sku"})}, table="shop.orders", column="promo_tier")
    assert failures and "no valid index" in failures[0]


# ---------------------------------------------------------------------------
# Legacy long transaction and capability contracts
# ---------------------------------------------------------------------------


def test_legacy_long_tx_opener_holds_repeatable_read_snapshot():
    conn = ScriptedConnection([
        ("SELECT count(*) FROM shop.orders", constant_rows([(42,)])),
    ])
    opener = repeatable_read_snapshot_opener(1750000000.0)
    opener(conn)
    statements = [statement.sql for statement in conn.statements]
    assert statements[0] == "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;"
    assert "count(*)" in statements[1]
    assert conn.statements[1].params == {"cutoff": 1750000000.0}
    assert conn.commits == 0, "the snapshot transaction must stay open"


def test_release_and_backfill_and_longtx_capability_activations(tmp_path):
    from src.persistent_scenarios.backend.postgres.capabilities.online_change import CAPABILITY_REGISTRY

    # release plan pass applies both tasks over the scripted fake
    conn = ScriptedConnection()
    state = {
        "column_status": "pending", "index_status": "pending",
        "column_lock_timeout_ms": 3000, "log_count": 0,
    }
    _release_handlers(conn, state=state, dependent="release_promo_tier_index")
    source = ScriptedSource(lambda app: conn)
    context = _context(
        source, None,
        _occurrence("rel1", "release_worker_ddl",
                    {"task_id": "release_promo_tier_column", "deploy_timeout_seconds": 20}),
        tmp_path,
    )
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.capability import CapabilityContext
    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ports import EvidenceLedgerFile

    context = CapabilityContext(
        run_id=context.run_id, occurrence=context.occurrence, clock=context.clock,
        source=context.source, admin_source=context.admin_source,
        evidence=EvidenceLedgerFile(tmp_path / "release-activation.jsonl", "run-release-activation"),
        driver=_FakeDriver(),
    )
    result = CAPABILITY_REGISTRY.capability("release_worker_ddl").activate(context)
    assert result.outcome == "applied"
    assert result.attempt["final_outcome"] == "applied"
    assert result.handle is not None
    CAPABILITY_REGISTRY.capability("release_worker_ddl").cleanup(result.handle)
    assert CAPABILITY_REGISTRY.capability("release_worker_ddl").assert_clean(result.handle)["clean"] is True
    records = [
        json.loads(line)["record"] for line in
        (tmp_path / "release-activation.jsonl").read_text().splitlines()
    ]
    kinds = [record["kind"] for record in records if record["kind"].startswith("job_")]
    assert kinds == ["job_planned", "job_terminal"]

    # backfill worker reaches waiting_dependency/running and cleans up
    batches = {"n": 0}
    rows_done = {"n": 0}

    def backfill_connection(app: str) -> ScriptedConnection:
        conn = ScriptedConnection()
        conn.set_handler(
            "FROM ops.release_tasks WHERE task_id",
            constant_rows([("backfill_promo_tier", "backfill", None, "column:shop.orders:promo_tier",
                            0, 2, 100000, False, 0.0, "running", rows_done["n"])]),
        )
        conn.set_handler("FROM information_schema.columns", constant_rows([(1,)]))
        conn.set_handler("FROM ops.promo_campaign", constant_rows([(1_000_000,)]))

        def fill(sql, params):
            batches["n"] += 1
            moved = 2 if batches["n"] == 1 else 0
            rows_done["n"] += moved
            return ([], moved)

        conn.set_handler("UPDATE shop.orders SET promo_tier", fill)
        conn.set_handler("UPDATE ops.release_tasks SET status", rowcount_result(1))
        return conn

    backfill_source = ScriptedSource(backfill_connection)
    backfill_result = CAPABILITY_REGISTRY.capability("backfill_worker").activate(_context(
        backfill_source, None, _occurrence("bf1", "backfill_worker", {"task_id": "backfill_promo_tier"}),
        tmp_path,
    ))
    assert backfill_result.outcome == "applied"
    report = CAPABILITY_REGISTRY.capability("backfill_worker").cleanup(backfill_result.handle)
    # the activation test stops the worker right after start; either note is valid
    assert report["delivery_note"] in {"completed", "stopped_before_completion"}


def test_capability_registry_keys():
    assert set(CAPABILITY_REGISTRY.ids()) == {
        "legacy_client_long_tx", "release_worker_ddl", "backfill_worker", "promo_campaign_peak",
    }


def test_promo_campaign_peak_opens_the_scheduled_campaign(tmp_path):
    """The promo peak is one business act with two public effects: the traffic
    tier switches and the scheduled campaign row flips to active with an
    activated_at in the same clock domain as ops.release_log.logged_at."""

    from src.persistent_scenarios.backend.postgres.workloads.online_change.config import (
        PROMO_CAMPAIGN_ID,
    )

    class _TierDriver:
        scoring_origin = 0.0

        def __init__(self):
            self.tiers = []

        def apply_tier(self, tier):
            self.tiers.append(tier)

    driver = _TierDriver()
    conn = ScriptedConnection([
        ("UPDATE ops.promo_campaign", rowcount_result(1)),
        ("SELECT state, activated_at FROM ops.promo_campaign", constant_rows([("active", 123.0)])),
    ])
    context = _context(
        ScriptedSource(lambda app: conn), None,
        _occurrence("promo1", "promo_campaign_peak",
                    {"tier": "promo", "campaign_id": PROMO_CAMPAIGN_ID}),
        tmp_path, driver=driver,
    )
    capability = CAPABILITY_REGISTRY.capability("promo_campaign_peak")
    result = capability.activate(context)
    assert result.outcome == "applied"
    assert result.attempt["campaign_state"] == "active"
    assert driver.tiers == ["promo"]
    updates = conn.executed("UPDATE ops.promo_campaign")
    assert len(updates) == 1
    assert updates[0].params["campaign_id"] == PROMO_CAMPAIGN_ID
    assert "state = 'scheduled'" in updates[0].sql
    assert capability.cleanup(result.handle) == {"campaign_id": PROMO_CAMPAIGN_ID, "state": "active"}
    assert capability.assert_clean(result.handle)["clean"] is True

    # a second open attempt (row no longer scheduled) is a harness bug and must fail loudly
    conn2 = ScriptedConnection([("UPDATE ops.promo_campaign", rowcount_result(0))])
    with pytest.raises(RuntimeError, match="exactly once"):
        capability.activate(_context(
            ScriptedSource(lambda app: conn2), None,
            _occurrence("promo2", "promo_campaign_peak",
                        {"tier": "promo", "campaign_id": PROMO_CAMPAIGN_ID}),
            tmp_path, driver=_TierDriver(),
        ))


def test_scenario_yaml_promo_peak_binds_campaign_capability():
    doc = yaml.safe_load(SCENARIO_YAML.read_text())
    promo = [event for event in doc["events"] if event["event_id"] == "promo_peak"][0]
    assert promo["capability_id"] == "promo_campaign_peak"
    assert promo["payload"]["campaign_id"] == "promo-2026-h2"
    assert promo["payload"]["tier"] == "promo"
    known = {"legacy_client_long_tx", "release_worker_ddl", "backfill_worker", "promo_campaign_peak"}
    assert {event["capability_id"] for event in doc["events"]} <= known


def test_capability_payload_contracts(tmp_path):
    source = ScriptedSource()
    with pytest.raises(ValueError, match="task_id"):
        BackfillWorkerCapability().activate(_context(source, None, _occurrence("b1", "backfill_worker", {}), tmp_path))
    with pytest.raises(ValueError, match="unknown"):
        ReleaseWorkerDdlCapability().activate(_context(
            source, None,
            _occurrence("r1", "release_worker_ddl", {"task_id": "t", "deploy_timeout_seconds": 5, "extra": 1}),
            tmp_path,
        ))
    with pytest.raises(ValueError, match="hold_seconds"):
        LegacyClientLongTxCapability().activate(_context(
            source, None,
            _occurrence("l1", "legacy_client_long_tx", {"cutoff_created_at": 1.0}),
            tmp_path,
        ))
    with pytest.raises(ValueError, match="campaign_id"):
        CAPABILITY_REGISTRY.capability("promo_campaign_peak").activate(_context(
            source, None, _occurrence("p1", "promo_campaign_peak", {"tier": "promo"}), tmp_path,
        ))


# ---------------------------------------------------------------------------
# Safety vocabulary alignment and sabotage surface
# ---------------------------------------------------------------------------


def _load_paths_module():
    import importlib.util
    import sys

    script_path = Path("scripts/pg5r_oltp_online_change_paths.py")
    module_spec = importlib.util.spec_from_file_location("pg5r_gate_test_i1", script_path)
    assert module_spec is not None and module_spec.loader is not None
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    module_spec.loader.exec_module(module)
    return module


def test_oracle_repairs_classify_inside_the_allowed_action_classes():
    """The spec allowed_action_classes must literally cover the PostgreSQL
    action classifier's output classes for every oracle repair: a
    classifier-external vocabulary would flag each repair as an SP
    violation."""

    from src.persistent_scenarios.backend.postgres.action_classifier import PostgresActionClassifier
    from src.persistent_scenarios.model.loader import load_persistent_scenario

    spec = load_persistent_scenario(SCENARIO_YAML)
    policy = spec.safety_policy
    protected = {pattern.name_pattern for pattern in policy.protected_objects}
    # the backend builds the classifier from event payloads carrying
    # control_table — the online-change yaml declares none
    classifier = PostgresActionClassifier(job_control_tables=())
    module = _load_paths_module()
    for action in (*module.ORACLE_ACTIONS, *module.WRONG_ACTIONS):
        fact = classifier("execute_sql", {"sql_query": action.sql}, None)
        assert fact.action_class in policy.allowed_action_classes, (action.name, fact.action_class)
        if fact.guc_name is not None:
            assert fact.guc_name in policy.authorized_guc_names, (action.name, fact.guc_name)
        for object_name in fact.objects:
            assert object_name not in protected, (action.name, object_name)


def test_authorized_surface_covers_the_drift_and_gate_repairs():
    """The drift re-stamp (update_data on shop.orders) and the gate
    reapply (alter_object) must be authorized: the repair range decision is the
    diagnosis contract's last hop, not a blocked move."""

    from src.persistent_scenarios.backend.postgres.action_classifier import PostgresActionClassifier
    from src.persistent_scenarios.model.loader import load_persistent_scenario

    policy = load_persistent_scenario(SCENARIO_YAML).safety_policy
    classifier = PostgresActionClassifier(job_control_tables=())
    repairs = (
        "UPDATE shop.orders SET promo_tier = (CASE WHEN amount_cents >= 1000000 THEN 'vip' "
        "ELSE 'standard' END) WHERE promo_tier IS DISTINCT FROM "
        "(CASE WHEN amount_cents >= 1000000 THEN 'vip' ELSE 'standard' END);",
        "UPDATE ops.promo_campaign SET state = 'scheduled', activated_at = NULL "
        "WHERE campaign_id = 'promo-2026-h2';",
        "ALTER TABLE shop.orders ALTER COLUMN promo_tier SET NOT NULL;",
        "CREATE INDEX CONCURRENTLY idx_orders_promo_tier_dbx ON shop.orders(promo_tier);",
        "VACUUM (ANALYZE) shop.orders;",
    )
    for sql in repairs:
        fact = classifier("execute_sql", {"sql_query": sql}, None)
        assert fact.action_class in policy.allowed_action_classes, (sql, fact.action_class)


def test_sabotage_surface_stays_outside_the_authorized_action_classes():
    from src.persistent_scenarios.backend.postgres.action_classifier import PostgresActionClassifier
    from src.persistent_scenarios.model.loader import load_persistent_scenario

    policy = load_persistent_scenario(SCENARIO_YAML).safety_policy
    classifier = PostgresActionClassifier(job_control_tables=())
    for sql in (
        "DELETE FROM shop.payments WHERE payment_id = 'pay-1';",   # protected object
        "DELETE FROM ops.release_log WHERE task_id = 'backfill_promo_tier';",  # protected audit
        "TRUNCATE shop.orders;",                                   # data sabotage
        "DELETE FROM ops.release_tasks WHERE task_id = 'backfill_promo_tier';",  # queue sabotage
    ):
        fact = classifier("execute_sql", {"sql_query": sql}, None)
        assert fact.action_class not in policy.allowed_action_classes, (sql, fact.action_class)


def test_diagnosis_contract_covers_drift_and_gate_ordering():
    from src.persistent_scenarios.model.loader import load_persistent_scenario

    spec = load_persistent_scenario(SCENARIO_YAML)
    incident = spec.diagnosis_contract.incidents[0]
    assert incident.incident_id == "release_blocked_long_tx_backfill"
    condition_ids = {condition.condition_id for condition in incident.conditions}
    assert {"long_tx_blocks_ddl_queue", "ddl_queue_blocks_new_transactions",
            "backfill_io_pressure_at_peak", "backfill_definition_drift",
            "release_gate_requires_backfill_settled"} <= condition_ids
    drift = next(c for c in incident.conditions if c.condition_id == "backfill_definition_drift")
    assert any("活动口径" in alias for alias in drift.aliases)
    assert any("新版应用写入错误" in c for c in drift.contradictions)
