"""pg5 PostgreSQL assembly tests: loader -> adapters -> core admission, ledger
bridge, gate scripts and pending-workload refusal."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.persistent_scenarios.api import build_postgres_backend
from src.persistent_scenarios.backend.postgres.gate_scripts import gate_script
from src.workloads.tpcds import _QUERY_FILE as TPCDS_QUERY_FILE
from src.persistent_scenarios.backend.postgres.instance_adapter import (
    InstanceWorkloadRuntime,
    translate_business_ledger,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ledger import (
    AttemptOutcome,
    BusinessLedger,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ports import EvidenceLedgerFile
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.persistent_scenarios.runtime.admission import admit_persistent_scenario
from src.persistent_scenarios.runtime.ledger import LedgerView, TrustedLedger
from src.persistent_scenarios.runtime.ports import PersistentScenarioProviderError

SCENARIO_ROOT = Path("src/persistent_scenarios/postgres")


def _spec(name: str):
    return load_persistent_scenario(SCENARIO_ROOT / f"{name}.yaml")


def _backend(name: str, tmp_path: Path):
    spec = _spec(name)
    backend = build_postgres_backend(spec, evidence_root=tmp_path)
    backend.validate_spec(spec)
    return spec, backend


@pytest.mark.parametrize(
    "name, event_count, capability_count",
    [
        ("pg_continuous_ops_smoke", 2, 1),
        ("pg_continuous_ops_business_priority", 8, 5),
        ("pg_oltp_online_change", 7, 4),
        ("pg_warehouse_batch_reporting", 9, 7),
    ],
)
def test_v2_scenarios_load_and_admit_through_the_assembly(tmp_path, name, event_count, capability_count):
    spec, backend = _backend(name, tmp_path)

    assert len(spec.events) == event_count
    assert backend.capabilities.capability_ids() == tuple(
        sorted({event.capability_id for event in spec.events})
    )
    admit_persistent_scenario(spec, backend, backend.events)


def test_warehouse_binding_deploys_the_measured_runtime_options(tmp_path):
    spec, backend = _backend("pg_warehouse_batch_reporting", tmp_path)

    options = backend.environment._runtime_options
    assert "shared_buffers=512MB" in options
    # the core capability protocol speaks directly: no adapter wrapping
    for event in spec.events:
        capability = backend.capabilities.capability(event.capability_id)
        assert type(capability).__module__.startswith(
            "src.persistent_scenarios.backend.postgres.capabilities.warehouse_reporting"
        )


def test_warehouse_binding_owns_its_ledgers_and_verifiers(tmp_path):
    spec, backend = _backend("pg_warehouse_batch_reporting", tmp_path)
    binding = backend._bindings[spec.environment.workload]

    assert sorted(binding.ledgers_factory(tmp_path, "run-1")) == [
        "wh_backup_service",
        "wh_heartbeat_service",
        "wh_ingest_service",
        "wh_report_service",
    ]
    for check in spec.integrity_checks:
        assert check.verifier_id in binding.verifiers
        assert check.verifier_id in binding.verifier_ledgers


def test_repeated_smoke_capability_on_distinct_entities_passes_admission(tmp_path):
    spec, backend = _backend("pg_continuous_ops_smoke", tmp_path)

    # Both smoke events share the smoke_tx_leak capability on distinct
    # entities with overlapping activation windows: per-entity isolation.
    assert spec.events[0].capability_id == spec.events[1].capability_id == "smoke_tx_leak"
    assert spec.events[0].entity != spec.events[1].entity
    admit_persistent_scenario(spec, backend, backend.events)


def test_unknown_instance_workload_is_refused_with_an_explicit_error(tmp_path):
    spec = _spec("pg_continuous_ops_smoke")
    object.__setattr__(spec.environment, "workload", "unknown_workload")

    with pytest.raises(ValueError, match="No PostgreSQL instance binding is registered"):
        build_postgres_backend(spec, evidence_root=tmp_path)


@pytest.mark.parametrize(
    "name, event_count, capability_ids",
    [
        ("pg_htap_shared_resource_isolation", 5, (
            "htap_wide_history_scan",
            "htap_stuck_export_snapshot",
            "htap_hotspot_churn",
            "htap_dashboard_retry_storm",
        )),
        ("pg_htap_replica_freshness", 6, (
            "frs_standby_long_snapshot",
            "frs_primary_update_surge",
            "frs_link_bandwidth_degraded",
        )),
    ],
)
def test_htap_scenarios_load_and_admit_through_the_assembly(tmp_path, name, event_count, capability_ids):
    spec, backend = _backend(name, tmp_path)

    assert len(spec.events) == event_count
    assert set(backend.capabilities.capability_ids()) == set(capability_ids)
    admit_persistent_scenario(spec, backend, backend.events)


def test_htap_bindings_register_the_third_verifier_dialect(tmp_path):
    spec, backend = _backend("pg_htap_replica_freshness", tmp_path)
    binding = backend._bindings[spec.environment.workload]

    assert binding.style == "htap"
    for check in spec.integrity_checks:
        assert check.verifier_id in binding.verifiers
    # role-scoped GUC verification logs in fresh as the role
    assert binding.role_credentials == {"frs_oltp": "frs_oltp", "frs_report": "frs_report"}


def test_htap_environment_assembly_builds_topology_primitives(tmp_path):
    spec, backend = _backend("pg_htap_replica_freshness", tmp_path)

    environment = backend.environment.create(spec, "run-1", 25240)
    assert type(environment._primitive).__name__ == "HtapReplicaTopology"
    assert environment._primitive.config.primary_port == 25240
    assert environment._primitive.config.standby_port == 25241

    single = _backend("pg_htap_shared_resource_isolation", tmp_path)
    environment3 = single[1].environment.create(single[0], "run-2", 25210)
    assert type(environment3._primitive).__name__ == "SingleNodePostgres"


def test_htap_role_logins_target_the_primitive_workload_database(tmp_path, monkeypatch):
    """Role logins must dial the database the topology bootstraps, not a hardcoded name."""
    from src.persistent_scenarios.backend.postgres import environment as environment_module

    spec, backend = _backend("pg_htap_replica_freshness", tmp_path)
    htap = backend.environment.create(spec, "run-role-db", 25240)
    assert htap._primitive.workload_dbname == "postgres"

    single_spec, single_backend = _backend("pg_htap_shared_resource_isolation", tmp_path)
    single = single_backend.environment.create(single_spec, "run-role-db-2", 25210)
    assert single._primitive.workload_dbname == "testdb"

    dialed = {}

    class _FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, query, params=None):
            raise AssertionError("role login check must not run queries in this test")

    class _FakeConnection:
        def __init__(self, **kwargs):
            dialed.update(kwargs)
            self.autocommit = None

        def cursor(self):
            return _FakeCursor()

        def close(self):
            pass

    monkeypatch.setattr(environment_module.psycopg2, "connect", _FakeConnection)

    dialed.clear()
    connection = htap.open_role_connection("frs_oltp", "role-login-probe")
    assert connection is not None
    assert dialed["dbname"] == htap._primitive.workload_dbname
    assert dialed["application_name"] == "role-login-probe"


def test_htap_runtime_adapter_exposes_only_the_core_ledger(tmp_path):
    from src.persistent_scenarios.backend.postgres.instance_adapter import HtapWorkloadRuntimeAdapter

    class _FakeRuntime:
        def __init__(self):
            self.ledger = TrustedLedger("htap3_trusted", tmp_path / "trusted.jsonl")
            self.externals = {"export_pages": object(), "commit_watermarks": object()}

        def ledgers(self):
            return {"trusted": self.ledger, **self.externals}

        def wait_for_warmup(self):
            return 100.0

    adapter = HtapWorkloadRuntimeAdapter(_FakeRuntime(), horizon_seconds=900.0, input_stop_seconds=880.0)
    ledgers = adapter.ledgers()
    assert sorted(ledgers) == ["trusted"]
    assert adapter.wait_for_warmup() == 100.0
    assert adapter.scoring_end_monotonic == 1000.0
    assert adapter.input_stop_monotonic == 980.0


def test_htap_state_facts_dispatch_the_third_verifier_dialect(tmp_path):
    """Integrity verifier receives (open_connection, params), not oltp kwargs."""

    spec, backend = _backend("pg_htap_shared_resource_isolation", tmp_path)

    seen = {}

    class _ClosedConnection:
        def close(self):
            pass

    backend.state_facts._workload_runtime = None
    # direct dispatch check without assembling a real driver
    binding = backend._bindings[spec.environment.workload]
    verifier = binding.verifiers["htap3_inventory_non_negative"]

    def _fake_open_connection(application_name, target="primary"):
        seen["application_name"] = application_name
        seen["target"] = target

        class _Cursor:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def execute(self, sql, params=None):
                pass

            def fetchone(self):
                return (0,)

            def fetchall(self):
                return [(0,)]

        class _Connection:
            def cursor(self):
                return _Cursor()

            def rollback(self):
                pass

            def close(self):
                pass

        return _Connection()

    result = verifier(_fake_open_connection, {})
    assert result["passed"] is True
    assert seen["application_name"] == "pg5r-htap3-verifier"
    assert seen["target"] == "primary"


def test_scenario_identity_outside_the_binding_is_refused(tmp_path):
    spec = _spec("pg_oltp_online_change")
    object.__setattr__(spec, "scenario_id", "pg_continuous_ops_smoke")

    with pytest.raises(ValueError, match="not owned by the resolved instance binding"):
        build_postgres_backend(spec, evidence_root=tmp_path)


def test_gate_script_covers_every_registered_pg5_scenario():
    if not Path(TPCDS_QUERY_FILE).exists():
        pytest.skip(
            "TPC-DS query text is not present; fetch it per docs/getting-started.md"
        )
    smoke = gate_script("pg_continuous_ops_smoke")
    assert smoke.reference_actions and smoke.wrong_actions
    assert all(action["api"] == "execute_sql" for action in smoke.reference_actions)

    for scenario_id in (
        "pg_continuous_ops_business_priority",
        "pg_oltp_online_change",
        "pg_htap_replica_freshness",
    ):
        script = gate_script(scenario_id)
        assert script.reference_actions, scenario_id
        assert script.wrong_actions, scenario_id

    with pytest.raises(ValueError, match="No gate action script"):
        gate_script("pg_unknown_scenario")


class _StubDriver:
    def __init__(self, ledger: BusinessLedger):
        self.ledger = ledger
        self.stopped = False
        self._warmup_return = 100.0

    def start(self) -> None:
        return None

    def wait_for_warmup(self) -> float:
        return self._warmup_return

    def stop_new_requests(self) -> None:
        return None

    def stop_and_drain(self):
        self.stopped = True
        return {"tier_schedule": {}}

    def baseline_facts(self) -> dict:
        return {"tier": "normal"}


def _record_ops(ledger: BusinessLedger) -> None:
    ledger.plan("o1", "place_order", 10.0, 25.0, {"sku": "PROMO-SKU-1", "qty": 1})
    ledger.attempt("o1", 10.0, 10.5, AttemptOutcome.TIMEOUT, "pgcode='55P03'")
    ledger.attempt("o1", 11.0, 11.4, AttemptOutcome.COMMITTED, "committed")
    ledger.terminal("o1", AttemptOutcome.COMMITTED, 11.4, "committed")
    ledger.plan("o2", "pay_order", 12.0, 27.0, {"order_id": "o1"})
    ledger.attempt("o2", 12.0, 27.5, AttemptOutcome.TIMEOUT, "deadline exceeded")
    ledger.terminal("o2", AttemptOutcome.PENDING_AT_CLOSE, 27.5, "pending at close")


def _translate(tmp_path: Path) -> LedgerView:
    instance_ledger = BusinessLedger(EvidenceLedgerFile(tmp_path / "instance.jsonl", "run-1"))
    _record_ops(instance_ledger)
    trusted = TrustedLedger("commerce", tmp_path / "commerce.jsonl")
    translate_business_ledger(instance_ledger, trusted, service_id="trade")
    return LedgerView(trusted)


def test_ledger_bridge(tmp_path):
    view = _translate(tmp_path)
    records = view.logical_transactions()

    by_id = {record.business_id: record for record in records}
    assert set(by_id) == {"o1", "o2"}
    completed = by_id["o1"]
    assert len(completed.attempts) == 2
    assert completed.attempts[0].outcome.value == "timed_out"
    assert completed.terminal.value == "completed"
    assert completed.good is True

    outstanding = by_id["o2"]
    assert outstanding.terminal.value == "incomplete_outstanding"
    assert outstanding.good is False


def test_workload_runtime_drain_translates_and_blocks_missing_job_evidence(tmp_path):
    instance_ledger = BusinessLedger(EvidenceLedgerFile(tmp_path / "instance.jsonl", "run-1"))
    _record_ops(instance_ledger)
    evidence = EvidenceLedgerFile(tmp_path / "evidence.jsonl", "run-1")
    trusted = TrustedLedger("commerce", tmp_path / "commerce.jsonl")
    driver = _StubDriver(instance_ledger)
    runtime = InstanceWorkloadRuntime(
        driver,
        trusted,
        evidence,
        transaction_service_id="trade",
        horizon_seconds=900.0,
        input_stop_seconds=890.0,
        job_ids=(),
    )
    scoring_started = runtime.wait_for_warmup()
    assert scoring_started == 100.0
    runtime.drain()

    assert driver.stopped is True
    assert [record.business_id for record in LedgerView(trusted).logical_transactions()] == ["o1", "o2"]

    # A deliverable whose job never started is a business result (the
    # evaluation checklist reports it missing), not a facility failure.
    strict = InstanceWorkloadRuntime(
        _StubDriver(instance_ledger),
        TrustedLedger("commerce-strict", tmp_path / "commerce-strict.jsonl"),
        evidence,
        transaction_service_id="trade",
        horizon_seconds=900.0,
        input_stop_seconds=890.0,
        job_ids=("orders-history-archive",),
    )
    strict.wait_for_warmup()
    strict.drain()
    assert LedgerView(strict.trusted_ledger).jobs() == ()

    # A job still in flight at the scoring end seals as an explicit
    # outstanding loss via the core finalize_outstanding path.
    evidence = EvidenceLedgerFile(tmp_path / "inflight.jsonl", "run-2")
    evidence.append({"kind": "job_planned", "job_id": "orders-history-archive", "job_kind": "archive", "at": 100.0})
    inflight = InstanceWorkloadRuntime(
        _StubDriver(instance_ledger),
        TrustedLedger("commerce-inflight", tmp_path / "commerce-inflight.jsonl"),
        evidence,
        transaction_service_id="trade",
        horizon_seconds=900.0,
        input_stop_seconds=890.0,
        job_ids=("orders-history-archive",),
        job_deadline_seconds={"orders-history-archive": 3480.0},
    )
    inflight.wait_for_warmup()
    inflight.drain()
    inflight.trusted_ledger.finalize_outstanding(10_000.0)
    inflight.trusted_ledger.seal()
    view = LedgerView(inflight.trusted_ledger)
    jobs = view.jobs()
    assert jobs[0].terminal.value == "incomplete_outstanding"
    assert jobs[0].delivered_on_time is False


def test_continuity_window_anchors_at_the_input_stop(tmp_path):
    """Business input is planned only up to the input stop, so the continuity
    observation window anchors at min(scoring_end, input_stop).

    An anchored-at-scoring_end window sits entirely past the input freeze,
    where no transaction can exist by design, so its denominator is
    structurally zero. Transactions here are planned inside
    the final [input_stop - window, input_stop] stretch: they count under the
    anchored window and would be structurally invisible to a scoring_end
    anchor.
    """
    from dataclasses import replace

    from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ports import (
        EvidenceLedgerFile,
    )
    from src.persistent_scenarios.model.enums import RequiredStateKind
    from src.persistent_scenarios.runtime.lifecycle import EvidenceStatus
    from src.persistent_scenarios.runtime.ledger import (
        AttemptOutcome,
        LedgerTerminal,
        TransactionAttempt,
    )

    spec, backend = _backend("pg_htap_shared_resource_isolation", tmp_path)
    continuity = next(c for c in spec.required_state if c.kind is RequiredStateKind.CONTINUITY)
    spec = replace(spec, required_state=(continuity,))

    instance_ledger = EvidenceLedgerFile(tmp_path / "instance.jsonl", "run-1")
    trusted = TrustedLedger("trusted", tmp_path / "trusted.jsonl")
    runtime = InstanceWorkloadRuntime(
        _StubDriver(instance_ledger),
        trusted,
        instance_ledger,
        transaction_service_id=continuity.service_id,
        horizon_seconds=spec.horizon_seconds,
        input_stop_seconds=spec.input_stop_seconds,
    )
    scoring_started = runtime.wait_for_warmup()
    window_end = min(runtime.scoring_end_monotonic, runtime.input_stop_monotonic)
    assert window_end == pytest.approx(scoring_started + spec.input_stop_seconds)

    for index in range(3):
        business_id = f"o{index}"
        planned = window_end - continuity.window_seconds / 2 + index
        trusted.append_planned_transaction(
            business_id=business_id,
            service_id=continuity.service_id,
            tx_kind="order",
            planned_at_monotonic=planned,
            deadline_at_monotonic=planned + 60.0,
        )
        trusted.append_transaction_attempt(
            business_id=business_id,
            attempt=TransactionAttempt(0, planned, planned + 5.0, AttemptOutcome.COMMITTED, {}),
        )
        trusted.append_transaction_terminal(
            business_id=business_id,
            terminal=LedgerTerminal.COMPLETED,
            completed_at_monotonic=planned + 5.0,
            result_digest="digest",
        )

    backend.state_facts._workload_runtime = runtime
    evidence = backend.state_facts.capture_required_state_evidence(None, spec)
    assert len(evidence) == 1
    item = evidence[0]
    assert item.check_id == continuity.check_id
    assert item.status is EvidenceStatus.CAPTURED
    assert item.facts["denominator"] == 3
    assert item.facts["completed"] == 3
