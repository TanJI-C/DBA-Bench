"""Diagnosis acceptance for explicitly declared business-incident explanations.

DP is only computed for incidents the contract explicitly requires explained; with
an empty contract it is N/A (``None``), never a default failure. The input is the
structured report of every completed mailbox write in ``run.mailbox_history``
(``diagnosis.conditions`` plus ``summary`` joined as one text). Only report text
is read: a diagnosis is never inferred from repair actions, and one explanation
may cover multiple root causes and their interaction.
"""

from __future__ import annotations

from typing import Mapping


def _condition_text(condition: Mapping[str, object]) -> str:
    """Render one structured mailbox condition into matchable diagnosis text.

    Mailbox writes validate ``diagnosis.conditions[]`` as
    ``DiagnosisCondition`` mappings (type/factor/entity/evidence, scenarios
    protocol ``StructuredReport``); matching is text based, so each condition
    is rendered with its fields instead of being joined as a raw object.
    """
    return (
        f"{condition['type']}: {condition['factor']} on {condition['entity']} "
        f"(evidence: {'; '.join(condition['evidence'])})"
    )


def collect_report_diagnosis_texts(mailbox_history) -> tuple[str, ...]:
    """Join every completed mailbox write report into one diagnosis text."""
    texts: list[str] = []
    for change in mailbox_history:
        if change["operation"] != "completed":
            continue
        task = change["task"]
        if task.get("status") != "completed":
            raise ValueError(
                f"A completed mailbox change carries a non-completed task: task_id={task['task_id']!r}, "
                f"status={task.get('status')!r}"
            )
        report = task["report"]
        conditions = report["diagnosis"]["conditions"]
        rendered = [_condition_text(condition) for condition in conditions]
        texts.append("; ".join([*rendered, report["summary"]]))
    return tuple(texts)


def _text_hits(alias: str, texts: list[str]) -> bool:
    return any(alias in text for text in texts)


def evaluate_diagnosis_contract(contract, texts) -> tuple[bool | None, list[dict[str, object]]]:
    """Match declared incident conditions against Agent report texts (exact path)."""
    incidents = contract.incidents
    if not incidents:
        return None, []
    folded = [text.casefold() for text in texts]
    results: list[dict[str, object]] = []
    for incident in incidents:
        if not incident.conditions:
            raise ValueError(
                f"Declared diagnosis incident must declare at least one condition: incident_id={incident.incident_id!r}"
            )
        matched: list[str] = []
        contradictions: list[str] = []
        missing: list[str] = []
        for condition in incident.conditions:
            if not condition.aliases:
                raise ValueError(
                    f"Diagnosis condition must declare readable aliases: incident_id={incident.incident_id!r}, "
                    f"condition_id={condition.condition_id!r}"
                )
            contradiction_hits = sorted(
                {alias for alias in condition.contradictions if _text_hits(alias.casefold(), folded)}
            )
            contradictions.extend(contradiction_hits)
            if any(_text_hits(alias.casefold(), folded) for alias in condition.aliases):
                if not contradiction_hits:
                    matched.append(condition.condition_id)
            else:
                missing.append(condition.condition_id)
        results.append(
            {
                "incident_id": incident.incident_id,
                "statement": incident.statement,
                "pass": not missing and not contradictions,
                "matched": matched,
                "missing": missing,
                "contradictions": sorted(set(contradictions)),
                "report_text_count": len(texts),
            }
        )
    return all(result["pass"] is True for result in results), results
