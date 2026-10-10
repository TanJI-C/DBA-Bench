"""Required-state acceptance on the effective final state.

Required state is what a service can continue from, not a restored reference
snapshot. A GUC counts only when a fresh connection in the declared scope
observes the value (and no restart is pending when the setting requires one);
values inherited by old connections or ALTER SYSTEM text alone never count.
Missing evidence or collector failures raise ``LedgerIncompleteError``: the
sampling facility broke, which invalidates the run instead of failing the model.
"""

from __future__ import annotations

from typing import Mapping

from ..model.enums import SETTING_SCOPES_WITH_NAME, RequiredStateKind, SettingEffect
from ..runtime.lifecycle import EvidenceStatus

from .contracts import LedgerIncompleteError


def _required(facts: Mapping[str, object], check_id: str, field: str) -> object:
    try:
        return facts[field]
    except KeyError as exc:
        raise LedgerIncompleteError(
            f"Required-state evidence is missing the field {field!r}: check_id={check_id!r}"
        ) from exc


def _check_guc_effective(check, evidence: Mapping) -> bool:
    value = _required(evidence, check.check_id, "value")
    fresh_connection = _required(evidence, check.check_id, "fresh_connection")
    scope = _required(evidence, check.check_id, "scope")
    if fresh_connection is not True:
        return False
    if scope != check.scope:
        return False
    if check.scope in SETTING_SCOPES_WITH_NAME:
        scope_name = _required(evidence, check.check_id, "scope_name")
        if scope_name != check.scope_name:
            return False
    # persist_required 是声明性字段；persisted 事实门待 backend 证据契约（integration state_facts）定型后启用。
    if check.effective_on is SettingEffect.AFTER_RESTART and _required(evidence, check.check_id, "pending_restart") is not False:
        return False
    return value in check.allowed_values


def _check_continuity(check, evidence: Mapping) -> bool:
    completed = _required(evidence, check.check_id, "completed")
    denominator = _required(evidence, check.check_id, "denominator")
    if isinstance(denominator, bool) or not isinstance(denominator, int) or denominator < 1:
        raise LedgerIncompleteError(
            f"Continuity evidence has an unusable denominator: check_id={check.check_id!r}, denominator={denominator!r}"
        )
    return completed / denominator >= check.min_success_fraction


def _check_deliverable_present(check, evidence: Mapping) -> bool:
    present = _required(evidence, check.check_id, "present")
    correct = _required(evidence, check.check_id, "correct")
    return present is True and correct is True


def _check_verifier(check, evidence: Mapping) -> bool:
    return _required(evidence, check.check_id, "passed") is True


def evaluate_required_state(checks, evidence) -> tuple[bool, list[dict[str, object]]]:
    """Accept declared required-state checks against captured final samples."""
    evidence_by_check: dict[str, object] = {}
    for item in evidence:
        if item.check_id in evidence_by_check:
            raise ValueError(
                f"Two required-state evidence records share one check_id: check_id={item.check_id!r}"
            )
        evidence_by_check[item.check_id] = item
    unknown = sorted(set(evidence_by_check) - {check.check_id for check in checks})
    if unknown:
        raise ValueError(
            f"Required-state evidence references undeclared checks: check_ids={unknown!r}"
        )
    results: list[dict[str, object]] = []
    for check in checks:
        item = evidence_by_check.get(check.check_id)
        if item is None:
            raise LedgerIncompleteError(
                f"Declared required-state check was never sampled: check_id={check.check_id!r}, kind={check.kind.value!r}"
            )
        if item.status is EvidenceStatus.COLLECTOR_FAILURE:
            raise LedgerIncompleteError(
                f"The collector failed to sample a required-state check: check_id={check.check_id!r}, "
                f"reason={item.facts.get('reason')!r}"
            )
        if check.kind is RequiredStateKind.GUC_EFFECTIVE:
            passed = _check_guc_effective(check, item.facts)
        elif check.kind is RequiredStateKind.CONTINUITY:
            passed = _check_continuity(check, item.facts)
        elif check.kind is RequiredStateKind.DELIVERABLE_PRESENT:
            passed = _check_deliverable_present(check, item.facts)
        elif check.kind is RequiredStateKind.VERIFIER:
            passed = _check_verifier(check, item.facts)
        else:
            raise ValueError(
                f"Unknown required-state check kind: check_id={check.check_id!r}, kind={check.kind!r}"
            )
        results.append(
            {
                "check_id": check.check_id,
                "kind": check.kind.value,
                "pass": passed,
                "evidence": dict(item.facts),
                "captured_at_monotonic": item.captured_at_monotonic,
            }
        )
    # A scenario that declares no required-state checks imposes no final-state gate.
    return all(result["pass"] is True for result in results), results
