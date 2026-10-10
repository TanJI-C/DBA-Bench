"""Required-state acceptance on effective final state."""

from __future__ import annotations

import pytest

from src.persistent_scenarios.evaluation.contracts import LedgerIncompleteError
from src.persistent_scenarios.evaluation.required_state import evaluate_required_state
from src.persistent_scenarios.model.enums import SettingEffect, SettingScope
from src.persistent_scenarios.runtime.lifecycle import EvidenceStatus

from tests.persistent_scenarios._evaluation_factories import (
    continuity_check,
    deliverable_present_check,
    guc_check,
    required_state_evidence,
    verifier_check,
)


def _contract(check):
    return (check,)


def test_guc_passes_only_on_fresh_connection_in_declared_scope_without_pending_restart():
    check = guc_check(
        "guc-fsync",
        "fsync",
        ("on",),
        SettingScope.SERVER,
        None,
        effective_on=SettingEffect.AFTER_RESTART,
        persist_required=True,
    )

    passed, results = evaluate_required_state(
        _contract(check),
        [
            required_state_evidence(
                "guc-fsync",
                {
                    "value": "on",
                    "pending_restart": False,
                    "fresh_connection": True,
                    "scope": SettingScope.SERVER,
                },
            )
        ],
    )

    assert passed is True
    assert results[0]["pass"] is True
    assert results[0]["kind"] == "guc_effective"


def test_pending_restart_means_the_configuration_is_not_repaired():
    check = guc_check(
        "guc-workmem",
        "work_mem",
        ("64MB", "128MB"),
        SettingScope.ROLE,
        "etl_worker",
        effective_on=SettingEffect.AFTER_RESTART,
        persist_required=True,
    )

    passed, _ = evaluate_required_state(
        _contract(check),
        [
            required_state_evidence(
                "guc-workmem",
                {
                    "value": "128MB",
                    "pending_restart": True,
                    "fresh_connection": True,
                    "scope": SettingScope.ROLE,
                    "scope_name": "etl_worker",
                },
            )
        ],
    )

    assert passed is False


def test_value_inherited_by_old_connections_never_counts_as_effective():
    check = guc_check(
        "guc-synccommit",
        "synchronous_commit",
        ("on",),
        SettingScope.ROLE,
        "etl_worker",
        effective_on=SettingEffect.NEW_CONNECTIONS,
        persist_required=False,
    )

    passed, _ = evaluate_required_state(
        _contract(check),
        [
            required_state_evidence(
                "guc-synccommit",
                {
                    "value": "on",
                    "fresh_connection": False,
                    "scope": SettingScope.ROLE,
                    "scope_name": "etl_worker",
                },
            )
        ],
    )

    assert passed is False


def test_role_database_scope_conflicts_are_resolved_by_the_declared_scope():
    role_scope = guc_check(
        "guc-role",
        "default_transaction_isolation",
        ("repeatable read",),
        SettingScope.ROLE,
        "etl_worker",
        effective_on=SettingEffect.NEW_CONNECTIONS,
        persist_required=False,
    )
    database_scope = guc_check(
        "guc-database",
        "default_transaction_isolation",
        ("repeatable read",),
        SettingScope.DATABASE,
        "warehouse",
        effective_on=SettingEffect.NEW_CONNECTIONS,
        persist_required=False,
    )

    passed_role, _ = evaluate_required_state(
        _contract(role_scope),
        [
            required_state_evidence(
                "guc-role",
                {
                    "value": "repeatable read",
                    "fresh_connection": True,
                    "scope": SettingScope.ROLE,
                    "scope_name": "etl_worker",
                },
            )
        ],
    )
    passed_database, _ = evaluate_required_state(
        _contract(database_scope),
        [
            required_state_evidence(
                "guc-database",
                {
                    "value": "read committed",
                    "fresh_connection": True,
                    "scope": SettingScope.DATABASE,
                    "scope_name": "warehouse",
                },
            )
        ],
    )

    # The role override satisfies the role contract while the database default
    # still resolves to the old value: each declared scope judges its own probe.
    assert passed_role is True
    assert passed_database is False


def test_continuity_check_requires_the_final_window_fraction():
    check = continuity_check("orders-continuity", "orders", window_seconds=20.0, min_success_fraction=0.9)

    healthy, _ = evaluate_required_state(
        _contract(check), [required_state_evidence("orders-continuity", {"completed": 19, "denominator": 20})]
    )
    damaged, _ = evaluate_required_state(
        _contract(check), [required_state_evidence("orders-continuity", {"completed": 17, "denominator": 20})]
    )

    assert healthy is True
    assert damaged is False


def test_deliverable_presence_requires_present_and_correct():
    check = deliverable_present_check("archive-delivered", "archive_2026")

    delivered, _ = evaluate_required_state(
        _contract(check), [required_state_evidence("archive-delivered", {"present": True, "correct": True})]
    )
    wrong, _ = evaluate_required_state(
        _contract(check), [required_state_evidence("archive-delivered", {"present": True, "correct": False})]
    )

    assert delivered is True
    assert wrong is False


def test_verifier_check_reads_the_instance_verdict():
    check = verifier_check("backfill-complete", "backfill_completeness")

    complete, _ = evaluate_required_state(
        _contract(check), [required_state_evidence("backfill-complete", {"passed": True, "ratio": 1.0})]
    )
    incomplete, _ = evaluate_required_state(
        _contract(check), [required_state_evidence("backfill-complete", {"passed": False, "ratio": 0.7})]
    )

    assert complete is True
    assert incomplete is False


def test_missing_or_failed_sampling_is_a_collector_failure_not_a_business_failure():
    check = guc_check("guc-fsync", "fsync", ("on",), SettingScope.SERVER, None, SettingEffect.NEW_CONNECTIONS, False)

    with pytest.raises(LedgerIncompleteError, match="never sampled"):
        evaluate_required_state(_contract(check), [])

    with pytest.raises(LedgerIncompleteError, match="collector failed to sample"):
        evaluate_required_state(
            _contract(check),
            [
                required_state_evidence(
                    "guc-fsync",
                    {"reason": "probe connection could not be established"},
                    status=EvidenceStatus.COLLECTOR_FAILURE,
                )
            ],
        )


def test_evidence_for_undeclared_checks_is_a_contract_violation():
    check = guc_check("guc-fsync", "fsync", ("on",), SettingScope.SERVER, None, SettingEffect.NEW_CONNECTIONS, False)

    with pytest.raises(ValueError, match="undeclared checks"):
        evaluate_required_state(
            _contract(check),
            [
                required_state_evidence(
                    "guc-some-other",
                    {"value": "on", "pending_restart": False, "fresh_connection": True, "scope": SettingScope.SERVER},
                )
            ],
        )
