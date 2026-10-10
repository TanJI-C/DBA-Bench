"""Assembly regressions: verifier verdicts must survive the assembly.

Two failure modes at the assembly boundary are pinned here:

1. ``TiDBStateFactProvider`` must derive the fact status from the instance
   verifiers' own verdict conventions (the SLO evaluator's
   ``incorrect_job_ids`` result-truth lists, cdc's top-level ``passed``,
   ``satisfied`` control-plane booleans), never from a single ``failures``
   key, or failed verifiers are recorded as PASSED while their deliverables
   digest-mismatch.
2. ``_bootstrap_warehouse`` must seed the batch registry rows before the
   schema's provision statements apply the report hold, or the hold preset
   matches zero rows and the deployed gate is inert.

No docker: verifier bindings are faked at the assembly call convention and
the registry seed is recorded at the cursor boundary.
"""

from __future__ import annotations

from types import SimpleNamespace

from src.persistent_scenarios.backend.tidb.assembly import (
    InstanceBinding,
    LazyRuntimeProvider,
    TiDBStateFactProvider,
    VerifierBinding,
    _seed_warehouse_registry,
    verifier_verdict_failed,
)
from src.persistent_scenarios.backend.tidb.capabilities.warehouse.schema import (
    BATCH_A_ID,
    BATCH_REGISTRY,
)
from src.persistent_scenarios.evaluation.required_state import evaluate_required_state
from src.persistent_scenarios.model.spec import RequiredStateKind, VerifierStateSpec


def test_verifier_verdict_failed_honors_every_instance_convention():
    assert verifier_verdict_failed({"failures": ["x"]})
    assert verifier_verdict_failed({"passed": False})
    assert verifier_verdict_failed({"satisfied": False})
    assert verifier_verdict_failed({"incorrect_job_ids": ["job1"]})
    assert verifier_verdict_failed({"incorrect_business_ids": ["o1"]})
    assert not verifier_verdict_failed({"failures": [], "passed": True, "satisfied": True})
    # An absent verdict key never fails by itself (indeterminate observations).
    assert not verifier_verdict_failed({"satisfied": None, "detail": "observation only"})


def _environment():
    connection = SimpleNamespace(close=lambda: None)
    return SimpleNamespace(control_connection=lambda: connection)


def _provider_with_verifier(verifier_id: str, result: dict) -> TiDBStateFactProvider:
    def call(_env, _conn, _views, _params):
        return result

    binding = InstanceBinding(
        scenario_id="test",
        bootstrap=lambda *args: None,
        make_workload=lambda *args: None,
        registry=lambda *args: None,
        integrity={verifier_id: VerifierBinding(ledger_ids=(), call=call)},
        required_state={verifier_id: VerifierBinding(ledger_ids=(), call=call)},
    )
    runtime_provider = LazyRuntimeProvider()
    runtime_provider.attach(SimpleNamespace(ledgers=lambda: {}))
    return TiDBStateFactProvider(binding, runtime_provider)


def _integrity_spec(verifier_id: str):
    check = SimpleNamespace(check_id=f"{verifier_id}_check", verifier_id=verifier_id, params={})
    return SimpleNamespace(integrity_checks=[check])


def _required_state_spec(verifier_id: str):
    return [VerifierStateSpec(check_id="r2_state", verifier_id=verifier_id, params={})]


def test_result_truth_verifier_with_incorrect_job_ids_is_recorded_failed():
    result = {"deliverables": {}, "incorrect_business_ids": [],
              "incorrect_job_ids": ["region_daily_revenue_batch1"]}
    provider = _provider_with_verifier("wh_report_result_truth", result)
    facts = provider.capture_integrity_facts(_environment(), _integrity_spec("wh_report_result_truth"))
    assert facts[0].status.name == "FAILED"


def test_cdc_style_passed_bool_and_satisfied_verdicts_are_recorded_failed():
    provider = _provider_with_verifier("cdc_marker_pairing", {"passed": False, "missing_count": 3})
    facts = provider.capture_integrity_facts(_environment(), _integrity_spec("cdc_marker_pairing"))
    assert facts[0].status.name == "FAILED"

    provider = _provider_with_verifier("htap_trade_conservation", {"satisfied": False})
    facts = provider.capture_integrity_facts(_environment(), _integrity_spec("htap_trade_conservation"))
    assert facts[0].status.name == "FAILED"


def test_required_state_verifier_passed_reflects_the_verifier_verdict():
    spec = _required_state_spec("htap_tenant_replica_attached")
    provider = _provider_with_verifier("htap_tenant_replica_attached", {"satisfied": False, "replica_count": 0})
    evidence = provider.capture_required_state_evidence(_environment(), SimpleNamespace(required_state=spec))
    assert evidence[0].facts["passed"] is False

    passed, results = evaluate_required_state(spec, evidence)
    assert passed is False
    assert results[0]["pass"] is False


def test_warehouse_registry_seed_applies_the_report_hold_to_the_seeded_rows():
    statements: list[str] = []

    class _Cursor:
        def execute(self, statement, *args):
            statements.append(statement)

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    _seed_warehouse_registry(_Cursor())

    assert len(statements) == 2
    insert, hold = statements
    assert insert.startswith("INSERT INTO wh.batch_registry")
    assert hold == f"UPDATE {BATCH_REGISTRY} SET reports_held = TRUE WHERE batch_id = {BATCH_A_ID};"
    # The gate lands after the rows exist: the provisioning preset cannot.
    assert statements.index(hold) > statements.index(insert)


def test_htap_truth_verifier_binding_spans_analysis_and_tenant_ledgers() -> None:
    """The tenant heavy analysis is a separate delivery duty: its job record
    lives in the tenant service ledger, so the truth check must span both
    ledgers or the tenant deliverable can never be verified present."""
    from src.persistent_scenarios.backend.tidb.assembly import _htap_verifier_bindings

    bindings = _htap_verifier_bindings()
    assert bindings["htap_analysis_result_truth"].ledger_ids == (
        "htap_analysis_service",
        "htap_tenant_service",
    )


def test_composite_ledger_view_merges_jobs_across_services() -> None:
    from src.persistent_scenarios.backend.tidb.assembly import _CompositeLedgerView

    class _StubView:
        def __init__(self, jobs, transactions=()):
            self._jobs, self._transactions = jobs, transactions

        def jobs(self):
            return tuple(self._jobs)

        def logical_transactions(self):
            return tuple(self._transactions)

    merged = _CompositeLedgerView((_StubView(["a"]), _StubView(["b"], ["t1"])))
    assert merged.jobs() == ("a", "b")
    assert merged.logical_transactions() == ("t1",)
