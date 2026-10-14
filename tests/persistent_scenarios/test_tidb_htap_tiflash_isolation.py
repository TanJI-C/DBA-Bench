"""Focused tests for tidb_htap_tiflash_isolation (tidb5-portfolio, instance 3).

Covers: the HTAP spec shape (transaction+analysis objectives), engine preference
release with its audit trail, per-claim SESSION application of the published config
(new claims follow the release; existing sessions are untouched), tenant onboarding
that repeats the same analysis class, verifiers over fake trusted connections, and
the prevention/capability surface.
"""

from __future__ import annotations

from pathlib import Path
import pytest

from src.persistent_scenarios.backend.tidb.capabilities.tiflash import (
    HtapCapabilityRegistry,
    CAPABILITIES,
    EngineRouteReleaseCapability,
    TiflashDegradationCapability,
)
from src.persistent_scenarios.backend.tidb.capabilities.tiflash import verifiers as htap_verifiers
from src.persistent_scenarios.backend.tidb.capabilities.tiflash.runtime import HtapIsolationRuntime
from src.persistent_scenarios.model.enums import LoadClass
from src.database.system import DatabaseSystem
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.persistent_scenarios.runtime.ledger import (
    JobAttempt,
    JobAttemptOutcome,
    LedgerTerminal,
    TrustedLedger,
)

YAML_PATH = Path("src/persistent_scenarios/tidb/tidb_htap_tiflash_isolation.yaml")


class FakeCursor:
    def __init__(self, rows_by_sql=None):
        self._queues: dict[str, list[list[tuple]]] = {k: list(v) for k, v in (rows_by_sql or {}).items()}
        self._last: str = ""
        self.executed: list[tuple[str, tuple]] = []

    def execute(self, sql, args=()):
        self.executed.append((sql, args))
        self._last = sql

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
    def __init__(self, rows_by_sql=None):
        self._cursor = FakeCursor(rows_by_sql)
        self.committed = 0
        self.rolled_back = 0

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed += 1

    def rollback(self):
        self.rolled_back += 1

    def close(self):
        pass


def spec():
    return load_persistent_scenario(YAML_PATH)


# ---------------------------------------------------------------------------
# spec shape: one HTAP composition over independent objectives


def test_htap_spec_loads_with_objective_references() -> None:
    s = spec()
    assert s.system is DatabaseSystem.TIDB
    htap = [service for service in s.services if service.load_class is LoadClass.HTAP]
    assert len(htap) == 1
    by_id = {service.objective_id: service for service in s.services}
    composition = htap[0]
    trade = by_id[composition.transaction_objective_id]
    analysis = by_id[composition.analysis_objective_id]
    assert trade.load_class is LoadClass.OLTP
    assert analysis.load_class is LoadClass.OLAP
    assert analysis.olap_mode == "deliverable_checklist"
    # the dashboard budget stays an independent service so a low-frequency checklist
    # is never diluted by the high-frequency class
    dashboard = [s2 for s2 in s.services if getattr(s2, "olap_mode", None) == "task_class_budget"]
    assert len(dashboard) == 1


def test_required_state_uses_verifier_kind_until_scope_vocabulary_lands() -> None:
    """TIDB-REQ-001 is unresolved: TiDB scopes are expressed through verifiers."""
    s = spec()
    assert s.required_state
    for item in s.required_state:
        assert item.kind == "verifier"


def test_events_cover_contract_timeline() -> None:
    events = spec().events
    starts = [e.start_seconds for e in events]
    assert starts == sorted(starts)
    assert {e.capability_id for e in events} <= set(CAPABILITIES)
    route_release = [e for e in events if e.capability_id == "tidb5_htap_engine_route_release"][0]
    assert route_release.payload["engine_preference"] == "tikv_only"


# ---------------------------------------------------------------------------
# engine preference release: audited, applied per claim


def test_engine_release_updates_config_and_writes_audit() -> None:
    conn = FakeConnection({
        "SELECT config_value FROM htap.analytics_config WHERE config_key = %s;": [
            [("auto",)],
            [("auto",)],
        ],
    })
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash.runtime import AnalyticsTables

    runtime = HtapIsolationRuntime.__new__(HtapIsolationRuntime)
    runtime.connection_factory = lambda name: conn
    runtime.tables = AnalyticsTables()
    release = runtime.release_engine_preference(1.0, "tikv_only")
    assert release == {"config_key": "engine_preference", "old_value": "auto", "new_value": "tikv_only"}
    sqls = [sql for sql, _args in conn._cursor.executed]
    assert any("UPDATE htap.analytics_config SET config_value = %s" in sql for sql in sqls)
    assert any("INSERT INTO htap.trade_audit" in sql for sql in sqls)


def test_claim_applies_published_preference_as_session_setting() -> None:
    """New claims read the released config; the mechanism is per-connection SESSION."""
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash.runtime import AnalyticsTables

    conn = FakeConnection({
        "SELECT config_value FROM htap.analytics_config WHERE config_key = %s;": [
            [("tikv_only",)],
        ],
    })
    tables = AnalyticsTables()
    tables.apply_engine_preference(conn)
    session_sets = [sql for sql, _args in conn._cursor.executed if sql.startswith("SET SESSION")]
    assert any("tidb_isolation_read_engines = 'tikv'" in sql for sql in session_sets)
    assert conn.rolled_back >= 1  # the config read never leaves a transaction open


def test_engine_route_release_capability_rejects_unknown_preference() -> None:
    capability = EngineRouteReleaseCapability(runtime_provider=lambda: None)
    context = SimpleNamespace(
        event=SimpleNamespace(event_id="bad", entity="analytics_pool", payload={"engine_preference": "yolo"}),
        clock=FakeClockish(),
    )
    with pytest.raises(ValueError, match="engine preference payload must be one of"):
        capability.activate(context)


class FakeClockish:
    def monotonic(self) -> float:
        return 0.0


# ---------------------------------------------------------------------------
# tenant onboarding repeats the same analysis class


def test_tenant_onboarding_capability_declares_queue_ownership() -> None:
    registry = HtapCapabilityRegistry(runtime_provider=lambda: None)
    event = SimpleNamespace(event_id="tenant_onboarding_repeat", entity="tenant_new", payload={})
    declaration = registry.capability("tidb5_htap_tenant_onboarding").declaration(event)
    assert any(resource.resource_key == "queue:analysis:tenant_new" for resource in declaration.resources)


def test_tiflash_degradation_requires_positive_cpu_limit() -> None:
    capability = TiflashDegradationCapability(runtime_provider=lambda: None)
    context = SimpleNamespace(
        event=SimpleNamespace(event_id="tiflash_node_degradation", entity="tiflash-0", payload={"cpu_limit": 0}),
        clock=FakeClockish(),
    )
    with pytest.raises(ValueError, match="throttled cpu limit must be positive"):
        capability.activate(context)


def test_registry_rejects_unknown_capability() -> None:
    registry = HtapCapabilityRegistry(runtime_provider=lambda: None)
    with pytest.raises(KeyError):
        registry.capability("tidb5_htap_nonexistent")


# ---------------------------------------------------------------------------
# required analysis submission: deliverable_id == job_id


class CapturingAnalysisStore:
    def __init__(self):
        self.enqueued: list = []

    def enqueue(self, job, connection) -> None:
        self.enqueued.append(job)


def analysis_runtime(tmp_path):
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash.schema import ORDERS_TABLE
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse.runtime import TiDBJobRunner

    clock = FakeClockish()
    ledger = TrustedLedger("htap_analysis_service", tmp_path / "identity.jsonl")
    runner = TiDBJobRunner(
        service_id="htap_analysis_service", ledger=ledger, clock=clock,
        store=CapturingAnalysisStore(), connection_factory=lambda name: FakeConnection(),
        application_name="test", max_workers=1,
    )
    runtime = HtapIsolationRuntime.__new__(HtapIsolationRuntime)
    runtime.clock = clock
    runtime.connection_factory = lambda name: FakeConnection({
        f"SELECT COUNT(*) FROM {ORDERS_TABLE};": [[(12345,)]],
    })
    runtime._analysis_runner = runner
    return runtime, ledger, runner


def test_submit_required_analysis_uses_the_deliverable_identity(tmp_path) -> None:
    """The report id IS the deliverable identity: no suffixed name; retries merge
    into the same job through ledger attempts, and a second submission of the same
    deliverable is rejected."""
    deliverable = [
        d for d in [s for s in spec().services if getattr(s, "olap_mode", None) == "deliverable_checklist"][0].deliverables
        if d.deliverable_id == "region_analysis_peak"
    ][0]
    runtime, ledger, _runner = analysis_runtime(tmp_path)
    returned = runtime.submit_required_analysis("region_analysis_peak", 1000.0)

    assert returned == deliverable.deliverable_id == "region_analysis_peak"
    ledger.append_job_attempt(
        job_id=returned, attempt=JobAttempt(1, 0.0, 1.0, 2.0, JobAttemptOutcome.SUCCEEDED, {})
    )
    ledger.append_job_terminal(
        job_id=returned,
        terminal=LedgerTerminal.COMPLETED,
        delivered_at_monotonic=20.0,
        result_digest="digest-ok",
    )
    record = ledger_view_of(ledger).jobs()[0]
    assert record.job_id == deliverable.deliverable_id
    with pytest.raises(ValueError, match="submitted twice"):
        runtime.submit_required_analysis("region_analysis_peak", 1000.0)


def test_uuid_suffixed_analysis_job_fails_the_deliverable_checklist(tmp_path) -> None:
    """Regression counterexample: a `{report_id}_{uuid4[:8]}`-style job name
    leaves the checklist deliverable missing even though the job delivered on
    time; the deliverable-named job passes the same evaluation."""
    from src.persistent_scenarios.evaluation.slo import evaluate_service_objectives
    from tests.persistent_scenarios._evaluation_factories import (
        LedgerBuilder,
        WINDOW,
        deliverable,
        olap_objective,
    )

    objective = olap_objective(
        service_id="htap_analysis_service",
        deliverables=[deliverable("region_analysis_peak")],
    )

    def evaluated(job_id: str):
        ledger = (
            LedgerBuilder("htap_identity", tmp_path)
            .plan_job(job_id, service_id="htap_analysis_service", submitted_at=10.0, deadline_at=40.0)
            .attempt_job(job_id)
            .deliver_job(job_id, delivered_at=20.0, digest="digest-ok")
        )
        return evaluate_service_objectives(
            [objective], window=WINDOW, ledgers={"htap_analysis_service": ledger.trusted()}, integrity_facts=()
        )

    all_pass, results = evaluated("region_analysis_peak")
    assert all_pass is True
    assert results[0]["deliverables"][0]["pass"] is True

    all_pass, results = evaluated("region_analysis_peak_1a2b3c4d")
    assert all_pass is False
    row = results[0]["deliverables"][0]
    assert row["deliverable_id"] == "region_analysis_peak"
    assert row["terminal_outcome"] == "missing"
    assert row["pass"] is False


# ---------------------------------------------------------------------------
# verifiers


def test_analytics_config_continuity_fails_when_analysis_left_disabled(tmp_path) -> None:
    """Permanently shutting analysis cannot protect trading (wrong path)."""
    conn = FakeConnection({
        "SELECT config_key, config_value FROM htap.analytics_config;": [
            [("engine_preference", "auto"), ("analysis_enabled", "false"), ("dashboard_enabled", "true")],
        ],
    })
    ledger = TrustedLedger("htap_test", tmp_path / "htap-continuity.jsonl")
    facts = htap_verifiers.htap_analytics_config_continuity(
        conn, ledger_view_of(ledger), {"config_table": "htap.analytics_config"}
    )
    assert facts["analysis_enabled"] is False
    assert facts["satisfied"] is False


def test_tiflash_replica_absence_is_reported_not_guessed(tmp_path) -> None:
    conn = FakeConnection({
        "SELECT AVAILABLE, PROGRESS, REPLICA_COUNT FROM information_schema.tiflash_replica "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;": [[]],
    })
    ledger = TrustedLedger("htap_test2", tmp_path / "htap-replica.jsonl")
    facts = htap_verifiers.htap_tiflash_replica_present(
        conn, ledger_view_of(ledger), {"schema": "htap", "table": "orders"}
    )
    assert facts["present"] is False
    assert facts["satisfied"] is False


def test_tiflash_replica_progress_is_observation_only(tmp_path) -> None:
    """A lagging replica (progress<1) does NOT fail the check: lag never gates correctness."""
    conn = FakeConnection({
        "SELECT AVAILABLE, PROGRESS, REPLICA_COUNT FROM information_schema.tiflash_replica "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;": [[(0, 0.5, 1)]],
    })
    ledger = TrustedLedger("htap_test3", tmp_path / "htap-replica2.jsonl")
    facts = htap_verifiers.htap_tiflash_replica_present(
        conn, ledger_view_of(ledger), {"schema": "htap", "table": "orders"}
    )
    assert facts["present"] is True
    assert facts["progress"] == 0.5
    assert facts["satisfied"] is True


def ledger_view_of(ledger: TrustedLedger):
    from src.persistent_scenarios.runtime.ledger import LedgerView

    return LedgerView(ledger)


from types import SimpleNamespace  # noqa: E402


# ---------------------------------------------------------------------------
# region_analysis_early: the capability timeline owns the commit point

import re  # noqa: E402

from src.persistent_scenarios.backend.tidb.capabilities.tiflash.runtime import (  # noqa: E402
    AnalyticsTables,
    AnalysisQueueStore,
    TenantQueueStore,
)
from src.persistent_scenarios.backend.tidb.capabilities.warehouse.runtime import (  # noqa: E402
    JobControl,
    QueuedJob,
)

BASELINE_ORDERS = 800_000
DELIVERABLE_IDS = ("region_analysis_early", "region_analysis_peak", "region_analysis_final")
TENANT_DELIVERABLE_ID = "tenant_region_heavy_analysis"

_region_day_truth: dict[int, list[tuple]] = {}
_tenant_region_day_truth: dict[int, list[tuple]] = {}


def region_day_truth_rows(marker: int) -> list[tuple]:
    """Deterministic snapshot truth over contiguous order ids 1..marker (the harness
    data shape): a pure function of the declared snapshot marker."""
    rows = _region_day_truth.get(marker)
    if rows is None:
        rows = _aggregate_truth(range(1, marker + 1))
        _region_day_truth[marker] = rows
    return rows


def tenant_region_day_truth_rows(marker: int) -> list[tuple]:
    """Tenant slice truth: the onboarding loads order ids divisible by 20, so the
    tenant table's snapshot truth is a pure function of its max order id."""
    rows = _tenant_region_day_truth.get(marker)
    if rows is None:
        rows = _aggregate_truth(index for index in range(1, marker + 1) if index % 20 == 0)
        _tenant_region_day_truth[marker] = rows
    return rows


def _aggregate_truth(order_ids) -> list[tuple]:
    aggregates: dict[tuple[int, int], list[float]] = {}
    for index in order_ids:
        cell = aggregates.get((1 + (index * 7 % 12), index % 5))
        if cell is None:
            aggregates[(1 + (index * 7 % 12), index % 5)] = cell = [0.0, 0]
        cell[0] += 10 + (index * 31 % 5000) / 100.0
        cell[1] += 1
    return [
        (region, day, round(amount, 2), count)
        for (region, day), (amount, count) in sorted(aggregates.items())
    ]


def test_baseline_event_is_the_first_commit_point_of_the_timeline() -> None:
    """The early deliverable has a real in-capability timeline commit point: the t=0
    baseline event wires the registered baseline capability, and each required analysis
    owns exactly one capability commit (early=baseline, peak=t=28, final=t=58,
    tenant heavy=recovery-overlap peak occurrence at t=67)."""
    s = spec()
    baseline = s.events[0]
    assert baseline.event_id == "baseline_region_analysis"
    assert baseline.capability_id == "tidb5_htap_baseline_analysis"
    assert baseline.start_seconds == 0
    assert baseline.trigger.value == "silent"

    registry = HtapCapabilityRegistry(runtime_provider=lambda: None)
    declaration = registry.capability(baseline.capability_id).declaration(baseline)
    assert declaration.capability_id == baseline.capability_id
    assert any(resource.resource_key == "queue:analysis:baseline" for resource in declaration.resources)
    assert declaration.max_activation_seconds <= baseline.activation_timeout_seconds

    analysis_commit_starts = sorted(
        event.start_seconds for event in s.events
        if event.capability_id in {
            "tidb5_htap_baseline_analysis", "tidb5_htap_peak_and_analysis", "tidb5_htap_tenant_onboarding",
        }
    )
    assert analysis_commit_starts == [0, 1680, 3480, 4020]


def monkeypatch_docker(monkeypatch) -> None:
    import src.persistent_scenarios.backend.tidb.capabilities.tiflash.runtime as htap_runtime

    monkeypatch.setattr(
        htap_runtime, "subprocess", SimpleNamespace(run=lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout=b""))
    )
    monkeypatch.setattr(HtapIsolationRuntime, "_read_nanocpus", staticmethod(lambda container: 2_000_000_000))


def test_complete_timeline_repairs_routing_and_tenant_placement_and_passes(tmp_path, monkeypatch) -> None:
    """Complete path: all seven YAML events activate through the real
    registry; the agent fixes the wrong route release, re-attaches the tenant
    placement the onboarding deferred inside the maintenance window, and the tenant's
    heavy analysis rides the recovery-overlap peak on the column-store replica. All
    four deliverables deliver on time with digests matching the recomputed snapshot
    truth, and the real checklist evaluation passes for both analysis objectives."""
    monkeypatch_docker(monkeypatch)
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash import ANALYSIS_DEADLINE_OFFSET
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash import verifiers as htap_verifiers
    from src.persistent_scenarios.runtime.ledger import LedgerView, LedgerTerminal

    tables = MemoryAnalyticsTables()
    runtime, clock, analysis_ledger, tenant_ledger = timeline_runtime(tmp_path, tables)
    events = spec().events
    assert [e.start_seconds for e in events] == [0, 900, 1680, 2400, 3480, 4020, 4200]

    registry = HtapCapabilityRegistry(runtime_provider=lambda: runtime)
    previous_start = 0
    for index, event in enumerate(events):
        if index:
            clock.advance(event.start_seconds - previous_start)
        previous_start = event.start_seconds
        context = SimpleNamespace(
            clock=clock,
            event=SimpleNamespace(event_id=event.event_id, entity=event.entity, payload=dict(event.payload)),
        )
        registry.capability(event.capability_id).activate(context)

        if event.event_id == "tenant_onboarding_repeat":
            # Residue: the onboarding ran inside the node's maintenance window, so
            # the placement attachment was deferred (audited) - the repair surface.
            assert tables.tenant_created and tables.tenant_loaded
            assert tables.tenant_replica_count == 0
            assert any(row[1] == "tenant_replica_attachment" and "deferred" in row[3] for row in tables.audit)
            assert tables.config["tenant_engine_preference"] == "tiflash_preferred"
            # agent repair 1: re-attach the tenant placement (real DDL path)
            StatefulHtapConnection(tables).cursor().execute(ATTACH_TENANT_REPLICA_SQL)
        if event.event_id == "analytics_route_error_release":
            pass  # the wrong release lands; the agent fixes it below
        if event.event_id == "trade_peak_and_heavy_analysis":
            drain_analysis_deliveries(runtime)
            drain_tenant_deliveries(runtime)
            # agent repair 2 (after the peak drained under the wrong route): publish a
            # routing-healthy preference (auto accepted, tiflash_preferred equally)
            runtime.release_engine_preference(clock.monotonic(), "auto")
            continue

        drain_analysis_deliveries(runtime)
        drain_tenant_deliveries(runtime)

    clock.advance(1200)  # to the horizon
    runtime.stop()
    analysis_ledger.finalize_outstanding(clock.monotonic())
    tenant_ledger.finalize_outstanding(clock.monotonic())

    jobs = {record.job_id: record for record in LedgerView(analysis_ledger).jobs()}
    tenant_jobs = {record.job_id: record for record in LedgerView(tenant_ledger).jobs()}
    assert set(jobs) == set(DELIVERABLE_IDS)
    assert set(tenant_jobs) == {TENANT_DELIVERABLE_ID}
    early = jobs["region_analysis_early"]
    assert early.terminal is LedgerTerminal.COMPLETED
    assert early.submitted_at_monotonic == 0.0
    assert early.deadline_at_monotonic == early.submitted_at_monotonic + ANALYSIS_DEADLINE_OFFSET == 900.0
    assert early.delivered_on_time is True

    # the early commit consumed the baseline snapshot BEFORE the wrong route release;
    # the tenant heavy analysis ran under the tenant's column-store template
    assert tables.results["region_analysis_early"]["snapshot_marker"] == tables.orders_count == BASELINE_ORDERS
    assert tables.results["region_analysis_early"]["engine_used"] == "tikv,tiflash,tidb"
    assert tables.results["region_analysis_peak"]["engine_used"] == "tikv"  # claimed before the routing fix
    assert tables.results["tenant_region_heavy_analysis"]["engine_used"] == "tiflash"
    assert tables.tenant_replica_count == 1

    truth = truth_facts_for(tables, LedgerView(analysis_ledger), LedgerView(tenant_ledger))
    assert truth["incorrect_job_ids"] == []
    for deliverable_id in (*DELIVERABLE_IDS, TENANT_DELIVERABLE_ID):
        fact = truth["deliverables"][deliverable_id]
        assert fact["present"] is True, deliverable_id
        assert fact["digest_match"] is True, deliverable_id
        assert fact["on_time"] is True, deliverable_id

    all_pass, results = evaluated_checklist(tmp_path, analysis_ledger, truth, tenant_ledger=tenant_ledger)
    assert all_pass is True
    rows = {row["deliverable_id"]: row for row in results[0]["deliverables"] + results[1]["deliverables"]}
    assert rows["region_analysis_early"]["pass"] is True
    assert rows["tenant_region_heavy_analysis"]["pass"] is True

    # required-state: routing continuity and the tenant placement both hold at seal
    config_facts = htap_verifiers.htap_analytics_config_continuity(
        StatefulHtapConnection(tables), LedgerView(analysis_ledger),
        {"config_table": "htap.analytics_config", "require_routing_healthy": True},
    )
    assert config_facts["satisfied"] is True and config_facts["routing_healthy"] is True
    replica_facts = htap_verifiers.htap_tenant_replica_attached(
        StatefulHtapConnection(tables), LedgerView(tenant_ledger), {"schema": "htap", "table": "tenant_orders"},
    )
    assert replica_facts["satisfied"] is True


def test_incomplete_repair_recurs_on_tenant_tables(tmp_path, monkeypatch) -> None:
    """Wrong path: the agent fixes the routing for the existing tables
    but skips the deferred tenant placement. The tenant's heavy analysis then recurs
    into routing errors on the new tenant tables - three real retry attempts, each
    failing with the column-store routing error - and the tenant duty ends as an
    explicit loss the checklist rejects."""
    monkeypatch_docker(monkeypatch)
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash import runtime as htap_runtime
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash import verifiers as htap_verifiers
    from src.persistent_scenarios.runtime.ledger import LedgerView, LedgerTerminal

    fake_now = [1000.0]
    monkeypatch.setattr(htap_runtime, "_now", lambda: fake_now[0])

    tables = MemoryAnalyticsTables()
    runtime, clock, analysis_ledger, tenant_ledger = timeline_runtime(tmp_path, tables)
    events = spec().events
    tenant_store = runtime._tenant_runner.store

    registry = HtapCapabilityRegistry(runtime_provider=lambda: runtime)
    previous_start = 0
    for index, event in enumerate(events):
        if index:
            clock.advance(event.start_seconds - previous_start)
        previous_start = event.start_seconds
        context = SimpleNamespace(
            clock=clock,
            event=SimpleNamespace(event_id=event.event_id, entity=event.entity, payload=dict(event.payload)),
        )
        registry.capability(event.capability_id).activate(context)
        if event.event_id == "trade_peak_and_heavy_analysis":
            runtime.release_engine_preference(clock.monotonic(), "auto")  # routing fixed...
        drain_analysis_deliveries(runtime)
        drained = drain_tenant_deliveries(runtime)
        while drained:
            # retry backoff: advance the fake retry clock past the requeue backoff
            fake_now[0] += 180.0
            drained = drain_tenant_deliveries(runtime)

    clock.advance(1200)
    runtime.stop()
    analysis_ledger.finalize_outstanding(clock.monotonic())
    tenant_ledger.finalize_outstanding(clock.monotonic())

    # the placement was never re-attached: the residue stayed broken all run
    assert tables.tenant_replica_count == 0
    tenant_jobs = {record.job_id: record for record in LedgerView(tenant_ledger).jobs()}
    heavy = tenant_jobs[TENANT_DELIVERABLE_ID]
    assert heavy.terminal is LedgerTerminal.INCOMPLETE_ERROR
    # recurrence observable: three real attempts, each a 1815 routing failure
    attempts = [attempt for attempt in heavy.attempts]
    assert len(attempts) == 3
    assert all(a.outcome is JobAttemptOutcome.FAILED for a in attempts)
    assert all(a.detail.get("error_code") == TENANT_ROUTING_ERROR_CODE for a in attempts)
    assert tables.results.get(TENANT_DELIVERABLE_ID) is None

    truth = truth_facts_for(tables, LedgerView(analysis_ledger), LedgerView(tenant_ledger))
    assert truth["deliverables"][TENANT_DELIVERABLE_ID]["present"] is False
    assert TENANT_DELIVERABLE_ID in truth["incorrect_job_ids"]

    all_pass, results = evaluated_checklist(tmp_path, analysis_ledger, truth, tenant_ledger=tenant_ledger)
    assert all_pass is False
    tenant_rows = results[1]["deliverables"]
    assert tenant_rows[0]["deliverable_id"] == TENANT_DELIVERABLE_ID
    assert tenant_rows[0]["terminal_outcome"] == "incomplete_error"
    assert tenant_rows[0]["pass"] is False

    # required state also rejects the run: the tenant replica stays unattached
    replica_facts = htap_verifiers.htap_tenant_replica_attached(
        StatefulHtapConnection(tables), LedgerView(tenant_ledger), {"schema": "htap", "table": "tenant_orders"},
    )
    assert replica_facts["satisfied"] is False


def test_recovery_restarts_the_node_and_closes_the_maintenance_window(tmp_path, monkeypatch) -> None:
    """Recovery semantics: the node rejoins (CPU restore + restart), the maintenance
    window closes, and the placement deferral the onboarding recorded is NOT flushed
    by the recovery - the residue is the operator's to repair."""
    monkeypatch_docker(monkeypatch)
    import src.persistent_scenarios.backend.tidb.capabilities.tiflash.runtime as htap_runtime
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash import (
        TenantOnboardingCapability, TiflashDegradationCapability, TiflashRecoveryCapability,
    )

    restart_calls: list[list[str]] = []

    def recording_run(args, **kwargs):
        restart_calls.append(list(args))
        return SimpleNamespace(returncode=0, stdout=b"")

    tables = MemoryAnalyticsTables()
    runtime, clock, analysis_ledger, tenant_ledger = timeline_runtime(tmp_path, tables)
    monkeypatch.setattr(htap_runtime, "subprocess", SimpleNamespace(run=recording_run))
    monkeypatch.setattr(HtapIsolationRuntime, "_read_nanocpus", staticmethod(lambda container: 2_000_000_000))

    degrade_context = SimpleNamespace(
        clock=clock,
        event=SimpleNamespace(event_id="tiflash_node_degradation", entity="tiflash-0", payload={"cpu_limit": 0.5}),
    )
    TiflashDegradationCapability(runtime_provider=lambda: runtime).activate(degrade_context)
    assert runtime.node_under_maintenance is True

    onboarding = SimpleNamespace(
        clock=clock,
        event=SimpleNamespace(event_id="tenant_onboarding_repeat", entity="tenant_new", payload={}),
    )
    TenantOnboardingCapability(runtime_provider=lambda: runtime).activate(onboarding)
    assert tables.tenant_replica_count == 0  # deferred inside the window, audited

    recover_context = SimpleNamespace(
        clock=clock,
        event=SimpleNamespace(event_id="tiflash_node_recovery", entity="tiflash-0", payload={}),
    )
    TiflashRecoveryCapability(runtime_provider=lambda: runtime).activate(recover_context)
    assert runtime.node_under_maintenance is False
    restart_calls = [call for call in restart_calls if call[:2] == ["docker", "restart"]]
    assert restart_calls and restart_calls[0][2] == "tiflash-fake"
    assert tables.tenant_replica_count == 0  # the recovery does NOT flush the deferral

    runtime.stop()


def test_zero_path_without_analysis_capacity_keeps_the_early_deliverable_honestly_violated(tmp_path) -> None:
    """Zero-path honesty: the baseline event still commits region_analysis_early, but
    with the analysis service disabled (the wrong-action class) nothing
    can claim it; after the horizon the job is an explicit outstanding loss and the
    real checklist evaluation fails on it - no fabricated pass."""
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash import BaselineAnalysisCapability
    from src.persistent_scenarios.runtime.ledger import LedgerView, LedgerTerminal

    tables = MemoryAnalyticsTables()
    tables.config["analysis_enabled"] = "false"
    runtime, clock, analysis_ledger, tenant_ledger = timeline_runtime(tmp_path, tables)
    baseline_event = spec().events[0]
    context = SimpleNamespace(
        clock=clock,
        event=SimpleNamespace(event_id=baseline_event.event_id, entity=baseline_event.entity, payload={}),
    )
    BaselineAnalysisCapability(runtime_provider=lambda: runtime).activate(context)
    assert drain_analysis_deliveries(runtime) == 0

    clock.advance(5400)
    runtime.stop()
    analysis_ledger.finalize_outstanding(clock.monotonic())
    tenant_ledger.finalize_outstanding(clock.monotonic())

    jobs = {record.job_id: record for record in LedgerView(analysis_ledger).jobs()}
    assert jobs["region_analysis_early"].terminal is LedgerTerminal.INCOMPLETE_OUTSTANDING

    truth = truth_facts_for(tables, LedgerView(analysis_ledger))
    assert truth["deliverables"]["region_analysis_early"]["present"] is False
    # only the baseline event ran in this reduced zero-path scenario, so every
    # uncommitted deliverable is honestly absent; the early one must be among them
    assert "region_analysis_early" in truth["incorrect_job_ids"]

    all_pass, results = evaluated_checklist(tmp_path, analysis_ledger, truth)
    assert all_pass is False
    rows = {row["deliverable_id"]: row for row in results[0]["deliverables"]}
    assert rows["region_analysis_early"]["pass"] is False
    assert rows["region_analysis_early"]["terminal_outcome"] == "incomplete_outstanding"


def test_wrong_route_release_cannot_stand_as_the_final_template(tmp_path) -> None:
    """Routing continuity (zero path): a published `tikv_only`
    preference - the known-bad scheduler release - fails the required-state routing
    check at seal time, while both routing-healthy values pass."""
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash import verifiers as htap_verifiers

    def facts(preference: str):
        tables = MemoryAnalyticsTables()
        tables.config["engine_preference"] = preference
        return htap_verifiers.htap_analytics_config_continuity(
            StatefulHtapConnection(tables), None,
            {"config_table": "htap.analytics_config", "require_routing_healthy": True},
        )

    assert facts("tikv_only")["satisfied"] is False
    assert facts("tikv_only")["routing_healthy"] is False
    assert facts("auto")["satisfied"] is True
    assert facts("tiflash_preferred")["satisfied"] is True


def test_tenant_template_pins_the_column_store_engine() -> None:
    """The tenant's own template - not the shared pool preference - reaches every
    tenant claim, so a placement gap cannot be masked by the shared preference."""
    conn = FakeConnection({
        "SELECT config_value FROM htap.analytics_config WHERE config_key = %s;": [
            [("tiflash_preferred",)],
        ],
    })
    tables = AnalyticsTables()
    tables.apply_tenant_template(conn)
    session_sets = [sql for sql, _args in conn._cursor.executed if sql.startswith("SET SESSION")]
    assert any("tidb_isolation_read_engines = 'tiflash'" in sql for sql in session_sets)
    with pytest.raises(RuntimeError, match="tenant_engine_preference"):
        tables.apply_tenant_template(FakeConnection())  # template missing = contract break


def test_tenant_analysis_failure_requeues_with_backoff_then_completes(tmp_path) -> None:
    """The tenant BI scheduler's retry policy: a failed load requeues with the real
    backoff while attempts remain, so a repair landing between attempts is honored;
    the duty never silently disappears."""
    import src.persistent_scenarios.backend.tidb.capabilities.tiflash.runtime as htap_runtime
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash.runtime import (
        SERVICE_TENANT, TENANT_RETRY_BACKOFF_SECONDS, TenantQueueStore,
    )
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse.runtime import TiDBJobRunner
    from src.persistent_scenarios.runtime.clock import FakeClock
    from src.persistent_scenarios.runtime.ledger import LedgerView, LedgerTerminal

    fake_now = [500.0]
    monkeyish = pytest.MonkeyPatch()
    monkeyish.setattr(htap_runtime, "_now", lambda: fake_now[0])
    try:
        tables = MemoryAnalyticsTables()
        tables.tenant_created = True
        tables.tenant_loaded = True
        tables.tenant_max_order_id = BASELINE_ORDERS
        tables.config["tenant_engine_preference"] = "tiflash_preferred"
        clock = FakeClock()
        ledger = TrustedLedger("htap_tenant_service", tmp_path / "tenant-retry.jsonl")
        store = MemoryTenantQueueStore(tables, attempt_timeout_seconds=600.0)
        runner = TiDBJobRunner(
            service_id=SERVICE_TENANT, ledger=ledger, clock=clock, store=store,
            connection_factory=lambda name: StatefulHtapConnection(tables),
            application_name="test-tenant-retry", max_workers=1,
        )
        runtime = HtapIsolationRuntime.__new__(HtapIsolationRuntime)
        runtime.clock = clock
        runtime.connection_factory = lambda name: StatefulHtapConnection(tables)
        runtime._tenant_runner = runner
        runtime.submit_tenant_analysis(TENANT_DELIVERABLE_ID, clock.monotonic() + 900)

        # attempt 1 fails on the missing placement (routing error 1815)
        assert drain_tenant_deliveries(runtime) == 1
        assert TENANT_DELIVERABLE_ID not in tables.results
        assert store._not_before[TENANT_DELIVERABLE_ID] == fake_now[0] + TENANT_RETRY_BACKOFF_SECONDS

        # before the backoff elapses the store holds the duty back
        assert drain_tenant_deliveries(runtime) == 0

        # the operator re-attaches the placement while the duty waits
        StatefulHtapConnection(tables).cursor().execute(ATTACH_TENANT_REPLICA_SQL)
        fake_now[0] += TENANT_RETRY_BACKOFF_SECONDS + 1.0

        # attempt 2 delivers on the column-store template
        assert drain_tenant_deliveries(runtime) == 1
        assert tables.results[TENANT_DELIVERABLE_ID]["engine_used"] == "tiflash"

        ledger.finalize_outstanding(clock.monotonic())
        record = LedgerView(ledger).jobs()[0]
        assert record.terminal is LedgerTerminal.COMPLETED
        assert record.delivered_on_time is True
    finally:
        monkeyish.undo()


def test_early_delivery_past_its_deadline_fails_the_on_time_check(tmp_path) -> None:
    """Timed-out honesty: a delivery that lands after the 900s submission-anchored
    budget stays digest-correct but loses on_time, and the real checklist evaluation
    fails the early deliverable."""
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash import BaselineAnalysisCapability
    from src.persistent_scenarios.runtime.ledger import LedgerView, LedgerTerminal

    tables = MemoryAnalyticsTables()
    runtime, clock, analysis_ledger, tenant_ledger = timeline_runtime(tmp_path, tables)
    baseline_event = spec().events[0]
    context = SimpleNamespace(
        clock=clock,
        event=SimpleNamespace(event_id=baseline_event.event_id, entity=baseline_event.entity, payload={}),
    )
    BaselineAnalysisCapability(runtime_provider=lambda: runtime).activate(context)

    clock.advance(901)
    assert drain_analysis_deliveries(runtime) == 1
    runtime.stop()
    analysis_ledger.finalize_outstanding(clock.monotonic())
    tenant_ledger.finalize_outstanding(clock.monotonic())

    jobs = {record.job_id: record for record in LedgerView(analysis_ledger).jobs()}
    early = jobs["region_analysis_early"]
    assert early.terminal is LedgerTerminal.COMPLETED
    assert early.delivered_on_time is False

    truth = truth_facts_for(tables, LedgerView(analysis_ledger))
    early_fact = truth["deliverables"]["region_analysis_early"]
    assert early_fact["present"] is True and early_fact["digest_match"] is True
    assert early_fact["on_time"] is False

    all_pass, results = evaluated_checklist(tmp_path, analysis_ledger, truth)
    assert all_pass is False
    rows = {row["deliverable_id"]: row for row in results[0]["deliverables"]}
    assert rows["region_analysis_early"]["pass"] is False
    assert rows["region_analysis_early"]["terminal_outcome"] == "completed"


ANALYSIS_SQL_PREFIX = "SELECT region_id, DATE(created_at) AS day"
CLAIM_SCAN_SQL = (
    "SELECT job_id FROM htap.analytics_jobs WHERE job_kind = %s AND status = 'queued' "
    "ORDER BY priority, job_id LIMIT 1 FOR UPDATE SKIP LOCKED;"
)
RESULT_ROW_SQL = "SELECT snapshot_marker, engine_used FROM htap.analytics_result WHERE job_id = %s;"
ORDERS_COUNT_SQL = "SELECT COUNT(*) FROM htap.orders;"
SESSION_ENGINES_SQL = "SELECT @@SESSION.tidb_isolation_read_engines;"
SESSION_ENGINES_BY_PREFERENCE = {"auto": "tikv,tiflash,tidb", "tikv_only": "tikv", "tiflash_preferred": "tiflash"}
TENANT_MAX_SQL = "SELECT COALESCE(MAX(order_id), 0) FROM htap.tenant_orders;"
TIFLASH_REPLICA_SQL = (
    "SELECT AVAILABLE, PROGRESS, REPLICA_COUNT FROM information_schema.tiflash_replica "
    "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;"
)
CREATE_TENANT_SQL = "CREATE TABLE IF NOT EXISTS htap.tenant_orders LIKE htap.orders;"
TENANT_SLICE_SQL_PREFIX = "INSERT INTO htap.tenant_orders"
ATTACH_TENANT_REPLICA_SQL = "ALTER TABLE htap.tenant_orders SET TIFLASH REPLICA 1;"
# CREATE TABLE LIKE inherits the source table's replica on this v8.1.0 build
# (measured), so the frozen pipeline strips it.
STRIP_TENANT_REPLICA_SQL = "ALTER TABLE htap.tenant_orders SET TIFLASH REPLICA 0;"
TENANT_AUDIT_PREFIX = "INSERT INTO htap.trade_audit"
TENANT_ROUTING_ERROR_CODE = 1815


class StatefulHtapCursor:
    """Serves the exact raw-SQL surface the capability-timeline tests reach outside the
    memory tables; every unrecognized statement fails loudly."""

    def __init__(self, connection: "StatefulHtapConnection"):
        self._connection = connection
        self._pending: list[tuple] = []
        self.rowcount = 0

    def execute(self, sql, args=()):
        connection = self._connection
        tables = connection.tables
        self.rowcount = 0
        if sql.startswith(ANALYSIS_SQL_PREFIX):
            match = re.search(r"order_id <= (\d+)", sql)
            if match is None:
                raise AssertionError(f"analysis truth SQL without a snapshot marker: sql={sql!r}")
            marker = int(match.group(1))
            if "FROM htap.tenant_orders" in sql:
                # The tenant template pins the column-store replica: a missing
                # placement attachment surfaces as the real routing error (1815).
                if connection.session_engines == "tiflash" and tables.tenant_replica_count == 0:
                    import pymysql

                    raise pymysql.err.InternalError(
                        TENANT_ROUTING_ERROR_CODE,
                        "[planner:1815] no TiFlash replica available for htap.tenant_orders",
                    )
                self._pending = tenant_region_day_truth_rows(marker)
            else:
                self._pending = region_day_truth_rows(marker)
        elif sql == ORDERS_COUNT_SQL:
            self._pending = [(connection.tables.orders_count,)]
        elif sql == TENANT_MAX_SQL:
            self._pending = [(connection.tables.tenant_max_order_id,)]
        elif sql == SESSION_ENGINES_SQL:
            if connection.session_engines is None:
                raise AssertionError("a claimed analysis read the session engines before its claim set them")
            self._pending = [(connection.session_engines,)]
        elif sql == RESULT_ROW_SQL:
            result = connection.tables.results.get(str(args[0]))
            self._pending = [(result["snapshot_marker"], result["engine_used"])] if result else []
        elif sql == TIFLASH_REPLICA_SQL:
            table = str(args[1])
            if table == "orders":
                self._pending = [(1, 1.0, 1)]
            elif table == "tenant_orders":
                count = connection.tables.tenant_replica_count
                self._pending = [(1, 1.0, count)] if count else []
            else:
                raise AssertionError(f"unexpected replica query for table={table!r}")
        elif sql == CREATE_TENANT_SQL:
            connection.tables.tenant_created = True
            connection.tables.tenant_replica_count = 1  # LIKE inherits the orders replica
        elif sql == STRIP_TENANT_REPLICA_SQL:
            if not connection.tables.tenant_created:
                raise AssertionError("replica strip before the tenant table exists")
            connection.tables.tenant_replica_count = 0
        elif sql.startswith(TENANT_SLICE_SQL_PREFIX):
            if not connection.tables.tenant_created:
                raise AssertionError("tenant slice loaded before the tenant table exists")
            connection.tables.tenant_loaded = True
            connection.tables.tenant_max_order_id = connection.tables.orders_count
            self.rowcount = connection.tables.orders_count // 20
        elif sql == ATTACH_TENANT_REPLICA_SQL:
            if not connection.tables.tenant_created:
                raise AssertionError("replica attachment before the tenant table exists")
            connection.tables.tenant_replica_count = 1
        elif sql.startswith(TENANT_AUDIT_PREFIX):
            connection.tables.audit.append(("tenant_audit", str(args[1]), str(args[2]), str(args[3])))
        elif sql == "SELECT config_key, config_value FROM htap.analytics_config;":
            self._pending = [(key, value) for key, value in sorted(connection.tables.config.items())]
        elif sql == CLAIM_SCAN_SQL:
            # the memory queue store owns the queued rows; extra raw-SQL worker scans
            # (tenant workers) must starve, not fail
            self._pending = []
        elif sql.startswith("SET SESSION max_execution_time") or sql in {"BEGIN PESSIMISTIC;", "ROLLBACK;", "COMMIT;"}:
            self._pending = []
        elif sql.startswith("SET SESSION tidb_isolation_read_engines"):
            match = re.search(r"tidb_isolation_read_engines\s*=\s*'([^']+)'", sql)
            if match is None:
                raise AssertionError(f"unparsed engine isolation SET: sql={sql!r}")
            connection.session_engines = match.group(1)
        elif sql.startswith("SET SESSION tidb_mem_quota_query"):
            self._pending = []
        else:
            raise AssertionError(f"unexpected SQL in the capability-timeline test: sql={sql!r}")

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


class StatefulHtapConnection:
    def __init__(self, tables: "MemoryAnalyticsTables"):
        self.tables = tables
        self.session_engines: str | None = None

    def set_session_engine_preference(self, preference: str) -> None:
        self.session_engines = SESSION_ENGINES_BY_PREFERENCE[preference]

    def cursor(self):
        return StatefulHtapCursor(self)

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


class MemoryAnalyticsTables(AnalyticsTables):
    """Config, audit and delivery state in memory. The package's own store/claim/run
    bodies and verifiers run unchanged; only the raw queue SQL becomes state."""

    def __init__(self, orders_count: int = BASELINE_ORDERS):
        super().__init__()
        self.config = {"engine_preference": "auto", "analysis_enabled": "true", "dashboard_enabled": "true"}
        self.orders_count = orders_count
        self.audit: list[tuple] = []
        self.queue_state: dict[str, tuple[str, bool, int]] = {}
        self.results: dict[str, dict] = {}
        # tenant placement model
        self.tenant_created = False
        self.tenant_loaded = False
        self.tenant_replica_count = 0
        self.tenant_max_order_id = 0

    def config_value(self, connection, key: str) -> str:
        if key not in self.config:
            raise RuntimeError(f"analytics config lost its {key!r} row")
        return self.config[key]

    def release_config(self, connection, at: float, key: str, value: str) -> dict:
        old = self.config_value(connection, key)
        self.config[key] = value
        self.audit.append((at, key, old, value))
        connection.commit()
        return {"config_key": key, "old_value": old, "new_value": value}

    def publish_config_key(self, connection, at: float, key: str, value: str) -> dict:
        old = self.config.get(key)
        self.config[key] = value
        self.audit.append((at, key, old, value))
        connection.commit()
        return {"config_key": key, "old_value": old, "new_value": value}

    def apply_engine_preference(self, connection) -> None:
        connection.set_session_engine_preference(self.config_value(connection, "engine_preference"))

    def job_state(self, connection, job_id: str) -> tuple[str, bool, int]:
        return self.queue_state[job_id]

    def record_result(self, connection, job_id: str, report_id: str, marker: int, delivered_at: float,
                      row_count: int, engines: str, digest: str) -> None:
        self.results[job_id] = {
            "report_id": report_id, "snapshot_marker": marker, "delivered_at": delivered_at,
            "row_count": row_count, "engine_used": engines, "result_digest": digest,
        }
        connection.commit()


class MemoryAnalysisQueueStore(AnalysisQueueStore):
    """Queue rows in memory; claim still applies the published engine preference per
    claim and still builds the package's own snapshot-bound run body."""

    def __init__(self, tables: MemoryAnalyticsTables, *, attempt_timeout_seconds: float):
        super().__init__(tables, attempt_timeout_seconds=attempt_timeout_seconds)
        self._queued: dict[str, QueuedJob] = {}

    def enqueue(self, job: QueuedJob, connection) -> None:
        self.tables.queue_state[job.job_id] = (str(job.input_snapshot["sql"]), False, 0)
        self._queued[job.job_id] = job

    def claim(self, worker_id: str, connection) -> QueuedJob | None:
        if not self.tables.analysis_enabled(connection):
            return None
        for job_id, job in self._queued.items():
            del self._queued[job_id]
            self.tables.apply_engine_preference(connection)
            return QueuedJob(
                job_id=job.job_id,
                job_kind=job.job_kind,
                submitted_at_monotonic=job.submitted_at_monotonic,
                deadline_at_monotonic=job.deadline_at_monotonic,
                run=self._make_run(job.job_id, str(job.input_snapshot["report_id"]), int(job.input_snapshot["snapshot_marker"])),
                input_snapshot=dict(job.input_snapshot),
            )
        return None

    def read_control(self, connection) -> JobControl:
        return JobControl(
            max_concurrency=self.tables.max_analysis_workers,
            paused=not self.tables.analysis_enabled(connection),
        )


class MemoryTenantQueueStore(TenantQueueStore):
    """Tenant queue rows in memory: the claim applies the real tenant template, and
    the retry policy requeues with the real backoff (the module `_now` is patched to
    a controllable fake in the tests that exercise retries)."""

    def __init__(self, tables: MemoryAnalyticsTables, *, attempt_timeout_seconds: float):
        super().__init__(tables, attempt_timeout_seconds=attempt_timeout_seconds)
        self._queued: dict[str, QueuedJob] = {}
        self._archive: dict[str, QueuedJob] = {}
        self._not_before: dict[str, float] = {}

    def enqueue(self, job: QueuedJob, connection) -> None:
        self.tables.queue_state[job.job_id] = (str(job.input_snapshot["sql"]), False, 0)
        self._queued[job.job_id] = job
        self._archive[job.job_id] = job

    def claim(self, worker_id: str, connection) -> QueuedJob | None:
        from src.persistent_scenarios.backend.tidb.capabilities.tiflash import runtime as htap_runtime

        if not self.tables.analysis_enabled(connection):
            return None
        for job_id, job in self._queued.items():
            not_before = self._not_before.get(job_id)
            if not_before is not None and htap_runtime._now() < not_before:
                continue
            del self._queued[job_id]
            self._not_before.pop(job_id, None)
            self.tables.apply_tenant_template(connection)
            return QueuedJob(
                job_id=job.job_id,
                job_kind=job.job_kind,
                submitted_at_monotonic=job.submitted_at_monotonic,
                deadline_at_monotonic=job.deadline_at_monotonic,
                run=self._make_run(job.job_id, str(job.input_snapshot["report_id"]), int(job.input_snapshot["snapshot_marker"])),
                input_snapshot=dict(job.input_snapshot),
            )
        return None

    def read_control(self, connection) -> JobControl:
        return JobControl(
            max_concurrency=self.tables.max_analysis_workers,
            paused=not self.tables.analysis_enabled(connection),
        )

    def retry_on_failure(self, job: QueuedJob, attempts: int) -> bool:
        return attempts < self.max_attempts

    def requeue_row(self, connection, job_id: str) -> None:
        from src.persistent_scenarios.backend.tidb.capabilities.tiflash import runtime as htap_runtime

        # the duty returns to the queue with the real retry backoff
        self._queued[job_id] = self._archive[job_id]
        self._not_before[job_id] = htap_runtime._now() + self.retry_backoff_seconds

    def fail_row(self, connection, job_id: str) -> None:
        # terminal loss: the duty leaves the queue (the ledger carries the explicit loss)
        self._queued.pop(job_id, None)
        self._not_before.pop(job_id, None)


def timeline_runtime(tmp_path, tables: MemoryAnalyticsTables):
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash.runtime import (
        SERVICE_ANALYSIS, SERVICE_DASHBOARD, SERVICE_TENANT, SERVICE_TRADE, TenantQueueStore,
    )
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse.runtime import TiDBJobRunner
    from src.persistent_scenarios.runtime.clock import FakeClock

    clock = FakeClock()
    ledgers = {
        service_id: TrustedLedger(f"htap_timeline:{service_id}", tmp_path / f"{service_id}.jsonl")
        for service_id in (SERVICE_TRADE, SERVICE_ANALYSIS, SERVICE_DASHBOARD, SERVICE_TENANT)
    }
    runtime = HtapIsolationRuntime(
        connection_factory=lambda name: StatefulHtapConnection(tables),
        clock=clock, run_id="htap-timeline-test", ledgers=ledgers,
        input_end_monotonic=clock.monotonic() + 5400,
        tiflash_container="tiflash-fake",
    )
    runtime.tables = tables
    runtime._analysis_runner = TiDBJobRunner(
        service_id=SERVICE_ANALYSIS, ledger=ledgers[SERVICE_ANALYSIS], clock=clock,
        store=MemoryAnalysisQueueStore(tables, attempt_timeout_seconds=600.0),
        connection_factory=lambda name: StatefulHtapConnection(tables),
        application_name="test-analysis", max_workers=1,
    )
    runtime._tenant_runner = TiDBJobRunner(
        service_id=SERVICE_TENANT, ledger=ledgers[SERVICE_TENANT], clock=clock,
        store=MemoryTenantQueueStore(tables, attempt_timeout_seconds=600.0),
        connection_factory=lambda name: StatefulHtapConnection(tables),
        application_name="test-tenant", max_workers=1,
    )
    # the tests drain deliveries deterministically; the background worker pool would
    # race the manual claim/execute loop
    runtime._tenant_runner.start = lambda: None
    return runtime, clock, ledgers[SERVICE_ANALYSIS], ledgers[SERVICE_TENANT]


def drain_analysis_deliveries(runtime) -> int:
    """Claim and execute every queued analysis through the real runner execute path."""
    store = runtime._analysis_runner.store
    connection = runtime.connection_factory("test-drain")
    executed = 0
    while True:
        claimed = store.claim("test-drain-w0", connection)
        if claimed is None:
            return executed
        runtime._analysis_runner._execute(claimed, connection)
        executed += 1


def drain_tenant_deliveries(runtime, fake_now=None) -> int:
    """Claim and execute every due tenant analysis; returns the executed count."""
    store = runtime._tenant_runner.store
    connection = runtime.connection_factory("test-tenant-drain")
    executed = 0
    while True:
        claimed = store.claim("test-tenant-w0", connection)
        if claimed is None:
            return executed
        runtime._tenant_runner._execute(claimed, connection)
        executed += 1


def activate_timeline_events(runtime, clock, events) -> None:
    """Activate every YAML event through the real registry, in timeline order, exactly
    as the engine scheduler does; deliveries drain after each activation."""
    registry = HtapCapabilityRegistry(runtime_provider=lambda: runtime)
    previous_start = 0
    for index, event in enumerate(events):
        if index:
            clock.advance(event.start_seconds - previous_start)
        previous_start = event.start_seconds
        context = SimpleNamespace(
            clock=clock,
            event=SimpleNamespace(event_id=event.event_id, entity=event.entity, payload=dict(event.payload)),
        )
        registry.capability(event.capability_id).activate(context)
        drain_analysis_deliveries(runtime)
        drain_tenant_deliveries(runtime)


def service_objective_of(s, objective_id):
    return [service for service in s.services if service.objective_id == objective_id][0]


def analysis_objective_of(s):
    return service_objective_of(s, "analysis_deliverables")


def tenant_objective_of(s):
    return service_objective_of(s, "tenant_analysis_deliverables")


def evaluated_checklist(tmp_path, ledger, truth, tenant_ledger=None):
    from src.persistent_scenarios.evaluation.slo import evaluate_service_objectives
    from src.persistent_scenarios.runtime.lifecycle import IntegrityFact, IntegrityStatus, ScoringWindow

    fact = IntegrityFact(
        check_id="analysis_results_match_truth",
        kind="result_truth",
        status=IntegrityStatus.FAILED if truth["incorrect_job_ids"] else IntegrityStatus.PASSED,
        details=truth,
    )
    objectives = [analysis_objective_of(spec()), tenant_objective_of(spec())]
    ledgers = {"htap_analysis_service": ledger}
    if tenant_ledger is not None:
        ledgers["htap_tenant_service"] = tenant_ledger
    return evaluate_service_objectives(
        objectives,
        window=ScoringWindow(scoring_start_monotonic=0.0, scoring_end_monotonic=5400.0, input_stop_monotonic=5100.0),
        ledgers=ledgers,
        integrity_facts=(fact,),
    )


def truth_facts_for(tables, analysis_ledger_view, tenant_ledger_view=None):
    """Recompute delivery truth per service ledger (the tenant duty lives on its own
    ledger) and merge the per-deliverable facts."""
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash import verifiers as htap_verifiers

    connection = StatefulHtapConnection(tables)
    analysis = htap_verifiers.htap_analysis_result_truth(
        connection,
        analysis_ledger_view,
        {"deliverables": [{"deliverable_id": d, "report_id": "region_analysis"} for d in DELIVERABLE_IDS]},
    )
    merged_deliverables = dict(analysis["deliverables"])
    incorrect = list(analysis["incorrect_job_ids"])
    if tenant_ledger_view is not None:
        tenant = htap_verifiers.htap_analysis_result_truth(
            connection,
            tenant_ledger_view,
            {"deliverables": [{"deliverable_id": TENANT_DELIVERABLE_ID, "report_id": TENANT_DELIVERABLE_ID}]},
        )
        merged_deliverables.update(tenant["deliverables"])
        incorrect.extend(tenant["incorrect_job_ids"])
    return {
        "deliverables": merged_deliverables,
        "incorrect_business_ids": [],
        "incorrect_job_ids": incorrect,
    }


def test_tenant_run_body_reads_control_unpinned_and_repins_for_analysis() -> None:
    """Recurrence surface: the tenant's routing failures must
    fire on the tenant table (the analysis SQL), never on the row-store
    control read. The run body therefore resets the session engines for the
    job_state read and re-applies the published tenant template before the
    analysis; the recorded engine evidence stays the signed column-store pin."""
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash.runtime import (
        AnalyticsTables,
        TenantQueueStore,
    )
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash.schema import (
        QUEUE_TABLE,
        tenant_analysis_sql,
    )

    bound_sql = tenant_analysis_sql(800000)
    conn = FakeConnection({
        f"SELECT sql_text, cancel_requested, attempts FROM {QUEUE_TABLE} WHERE job_id = %s;": [
            [("SELECT 1", False, 0)],
        ],
        "SELECT config_value FROM htap.analytics_config WHERE config_key = %s;": [
            [("tiflash_preferred",)],
        ],
        bound_sql: [
            [("r1",), ("r2",)],
        ],
        "SELECT @@SESSION.tidb_isolation_read_engines;": [
            [("tiflash",)],
        ],
    })
    from types import SimpleNamespace
    store = TenantQueueStore(AnalyticsTables(), attempt_timeout_seconds=5.0)
    run = store._make_run("tenant_region_heavy_analysis", "tenant_region_heavy_analysis", 800000)
    digest = run(job=SimpleNamespace(job_id="tenant_region_heavy_analysis"), connection=conn)
    assert digest

    executed = [sql for sql, _args in conn._cursor.executed]
    control_index = next(i for i, sql in enumerate(executed) if "FROM htap.analytics_jobs" in sql)
    reset_index = next(i for i, sql in enumerate(executed) if "tidb_isolation_read_engines = 'tikv,tiflash,tidb'" in sql)
    repin_index = next(i for i, sql in enumerate(executed) if "tidb_isolation_read_engines = 'tiflash'" in sql)
    analysis_index = executed.index(bound_sql)
    assert reset_index < control_index, "the control read must run on default engines"
    assert control_index < repin_index < analysis_index, "the signed pin must be back before the analysis"
    # engine_used evidence is captured under the pin, after the analysis
    assert executed.index("SELECT @@SESSION.tidb_isolation_read_engines;") > analysis_index
    # the completion writes ride the row store: a pinned session cannot
    # execute non-readonly statements (planner 1815)
    write_index = next(i for i, sql in enumerate(executed) if "UPDATE htap.analytics_jobs SET status = 'delivered'" in sql)
    write_reset_index = min(
        i for i, sql in enumerate(executed)
        if "tidb_isolation_read_engines = 'tikv,tiflash,tidb'" in sql and i > analysis_index
    )
    assert write_reset_index < write_index
