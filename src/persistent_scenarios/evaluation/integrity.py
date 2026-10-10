"""Data-integrity acceptance over trusted verification facts.

Wrong business results are a hard constraint that successful requests cannot
offset. A probe that could not verify data is not evidence of data damage:
verification infrastructure failures invalidate the run instead of failing the
model, and business failures stay valid business results.
"""

from __future__ import annotations

from ..runtime.lifecycle import IntegrityStatus

from .contracts import LedgerIncompleteError


def evaluate_integrity(facts, objective_results) -> tuple[bool, list[dict[str, object]]]:
    """Combine integrity facts with business-result correctness into DataIntegrityPass."""
    results: list[dict[str, object]] = []
    for fact in facts:
        if fact.status is IntegrityStatus.VERIFICATION_INFRASTRUCTURE_FAILURE:
            raise LedgerIncompleteError(
                f"An integrity check could not be executed by the verification facility: "
                f"check_id={fact.check_id!r}, kind={fact.kind!r}, details={dict(fact.details)!r}"
            )
        results.append(
            {
                "check_id": fact.check_id,
                "kind": fact.kind,
                "status": fact.status.value,
                "details": dict(fact.details),
            }
        )
    failed = any(fact.status is IntegrityStatus.FAILED for fact in facts)
    incorrect_results = sum(
        result.get("incorrect_result_count", 0) for result in objective_results
    )
    return not failed and incorrect_results == 0, results
