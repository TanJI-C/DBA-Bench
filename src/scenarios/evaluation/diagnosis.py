from dataclasses import dataclass
import re
from typing import Mapping, Protocol

from src.execution.history.metrics import parse_utc_timestamp
from src.execution.history.records import (
    FrozenHistoricalRecordStore,
    HistoricalIntervalRecord,
    HistoricalPointRecord,
    HistoricalRecordSource,
)
from src.scenarios.evaluation.semantic import (
    SemanticDiagnosisJudge,
    SemanticJudgment,
    validate_semantic_judgment,
)
from src.protocols.report import DiagnosisCondition, StructuredReport


@dataclass(frozen=True, slots=True)
class ExpectedCondition:
    condition_id: str
    aliases: frozenset[str]
    critical: bool = False
    contradictions: frozenset[str] = frozenset()


def verify_historical_investigation(
    report: StructuredReport,
    history_audit: Mapping[str, object],
    *,
    record_store: FrozenHistoricalRecordStore,
    required_exclusions: frozenset[str],
    causal_metric_tokens: frozenset[str],
    minimum_timeline_items: int = 4,
) -> dict[str, object]:
    """Validate frozen-history timing, evidence records, and required decoy exclusions."""
    failures: list[str] = []
    diagnosis = report.diagnosis
    plan = report.outcome.plan or {}
    target_windows = [
        window
        for window in history_audit.get("window_roles", ())
        if isinstance(window, Mapping) and window.get("role") == "target"
    ]
    if len(target_windows) != 1:
        failures.append(f"sealed target window count must be one, actual={len(target_windows)}")
        return {"pass": False, "failures": failures, "target_window": None}
    target_window = target_windows[0]
    try:
        target_start = int(target_window["start_ms"])
        target_end = int(target_window["end_ms"])
        incident_window = plan.get("incident_window")
        if not isinstance(incident_window, Mapping):
            raise ValueError("outcome.plan.incident_window is missing")
        report_start = parse_utc_timestamp(
            str(incident_window["start_timestamp"]),
            "outcome.plan.incident_window.start_timestamp",
        )
        report_end = parse_utc_timestamp(
            str(incident_window["end_timestamp"]),
            "outcome.plan.incident_window.end_timestamp",
        )
    except (KeyError, TypeError, ValueError) as exc:
        return {
            "pass": False,
            "failures": [f"incident window is not valid UTC evidence: {exc}"],
            "target_window": dict(target_window),
        }
    if report_start >= report_end:
        failures.append(f"reported incident window is reversed: start={report_start}, end={report_end}")
    if target_start >= target_end:
        failures.append(f"sealed target window is reversed: start={target_start}, end={target_end}")
    overlap = max(0, min(report_end, target_end) - max(report_start, target_start))
    target_duration = max(target_end - target_start, 1)
    report_duration = max(report_end - report_start, 0)
    overlap_ratio = overlap / target_duration
    if overlap_ratio < 0.70:
        failures.append(f"incident window overlap is too small: overlap_ratio={overlap_ratio:.4f}")
    if report_duration > target_duration * 2.5:
        failures.append(
            f"incident window is too broad: report_duration_ms={report_duration}, "
            f"target_duration_ms={target_duration}"
        )

    timeline = plan.get("timeline", ())
    if not isinstance(timeline, (list, tuple)):
        failures.append("outcome.plan.timeline must be a list")
        timeline = ()
    if len(timeline) < minimum_timeline_items:
        failures.append(
            f"timeline needs at least {minimum_timeline_items} logical states: actual={len(timeline)}"
        )
    sequences = [item.get("sequence") for item in timeline]
    if any(not isinstance(sequence, int) or isinstance(sequence, bool) for sequence in sequences):
        failures.append(f"timeline sequence must contain integers: sequences={sequences!r}")
    elif sequences != sorted(sequences) or len(set(sequences)) != len(sequences):
        failures.append(f"timeline sequence must be strictly increasing: sequences={sequences!r}")
    previous_end = None
    observed_metric_tokens: set[str] = set()
    for index, item in enumerate(timeline):
        try:
            start = parse_utc_timestamp(
                str(item["start_timestamp"]),
                f"timeline[{index}].start_timestamp",
            )
            end = parse_utc_timestamp(
                str(item["end_timestamp"]),
                f"timeline[{index}].end_timestamp",
            )
        except (KeyError, TypeError, ValueError) as exc:
            failures.append(f"timeline[{index}] has invalid UTC bounds: {exc}")
            continue
        if start >= end:
            failures.append(f"timeline[{index}] has reversed bounds: start={start}, end={end}")
        if previous_end is not None and start < previous_end:
            failures.append(f"timeline timestamps move backwards at index={index}")
        previous_end = end
        evidence = item.get("metric_evidence", ())
        if not isinstance(evidence, (list, tuple)):
            failures.append(f"timeline[{index}].metric_evidence must be a list")
            continue
        for evidence_item in evidence:
            if isinstance(evidence_item, Mapping):
                observed_metric_tokens.update(
                    str(value).casefold()
                    for key, value in evidence_item.items()
                    if key in {"metric", "field", "direction"}
                )
    missing_metric_tokens = sorted(
        token
        for token in causal_metric_tokens
        if not any(token.casefold() in observed for observed in observed_metric_tokens)
    )
    if missing_metric_tokens:
        failures.append(
            "timeline does not cover every required causal metric relation: "
            f"observed={sorted(observed_metric_tokens)!r}, missing={missing_metric_tokens!r}"
        )

    record_sources, record_failures = _verify_frozen_record_evidence(
        plan.get("corroborating_records", ()),
        record_store,
        target_start_ms=target_start,
        target_end_ms=target_end,
        incident_start_ms=report_start,
        incident_end_ms=report_end,
    )
    failures.extend(record_failures)
    required_by_id = {
        _canonical_window_id(window["decoy_id"]): window
        for window in history_audit.get("window_roles", ())
        if isinstance(window, Mapping)
        and window.get("role") == "decoy"
        and window.get("decoy_id") is not None
        and _canonical_window_id(window["decoy_id"]) in {
            _canonical_window_id(candidate) for candidate in required_exclusions
        }
    }
    missing_required_windows = {
        _canonical_window_id(candidate) for candidate in required_exclusions
    } - set(required_by_id)
    if missing_required_windows:
        failures.append(
            "required benign windows are absent from sealed history: "
            f"missing={sorted(missing_required_windows)!r}"
        )
    excluded: set[str] = set()
    excluded_windows = plan.get("excluded_windows", ())
    if not isinstance(excluded_windows, (list, tuple)):
        failures.append("outcome.plan.excluded_windows must be a list")
        excluded_windows = ()
    for index, item in enumerate(excluded_windows):
        if not isinstance(item, Mapping):
            continue
        reason = item.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            failures.append(f"excluded_windows[{index}] requires a non-empty reason")
        candidate = item.get("candidate")
        candidate_id = _canonical_window_id(candidate) if candidate is not None else None
        start_value = item.get("start_timestamp")
        end_value = item.get("end_timestamp")
        if start_value is None or end_value is None:
            if candidate_id in required_by_id:
                excluded.add(candidate_id)
                continue
            failures.append(
                f"excluded_windows[{index}] must expose start_timestamp and end_timestamp: item={item!r}"
            )
            continue
        try:
            start_ms = parse_utc_timestamp(
                str(start_value),
                f"excluded_windows[{index}].start_timestamp",
            )
            end_ms = parse_utc_timestamp(
                str(end_value),
                f"excluded_windows[{index}].end_timestamp",
            )
        except (TypeError, ValueError) as exc:
            failures.append(f"excluded_windows[{index}] has invalid UTC bounds: {exc}")
            continue
        if start_ms >= end_ms:
            failures.append(f"excluded_windows[{index}] has reversed bounds: start={start_ms}, end={end_ms}")
            continue
        matched = [
            normalized_id
            for normalized_id, window in required_by_id.items()
            if int(window["start_ms"]) == start_ms and int(window["end_ms"]) == end_ms
        ]
        if not matched:
            failures.append(
                f"excluded_windows[{index}] does not match a required benign window by public UTC bounds: "
                f"start_ms={start_ms}, end_ms={end_ms}"
            )
            continue
        excluded.update(matched)
    missing_exclusions = sorted(set(required_by_id) - excluded)
    if missing_exclusions:
        failures.append(f"required benign windows were not excluded: missing={missing_exclusions!r}")
    current_state_interpretation = plan.get("current_state_interpretation")
    if not isinstance(current_state_interpretation, str) or not current_state_interpretation.strip():
        failures.append("outcome.plan.current_state_interpretation is missing")
    return {
        "pass": not failures,
        "failures": failures,
        "target_window": dict(target_window),
        "overlap_ratio": round(overlap_ratio, 6),
        "reported_timeline_items": len(timeline),
        "observed_metric_tokens": sorted(observed_metric_tokens),
        "record_sources": sorted(record_sources),
        "excluded_candidates": sorted(excluded),
    }


def _canonical_window_id(value: object) -> str:
    return str(value).casefold().replace("-", "_")


def _verify_frozen_record_evidence(
    records: tuple[Mapping[str, object], ...],
    record_store: FrozenHistoricalRecordStore,
    *,
    target_start_ms: int,
    target_end_ms: int,
    incident_start_ms: int,
    incident_end_ms: int,
) -> tuple[set[str], list[str]]:
    failures: list[str] = []
    sources: set[str] = set()
    for index, item in enumerate(records):
        source_value = item.get("source")
        target = item.get("target")
        raw_payload = item.get("record")
        if not isinstance(source_value, str) or not source_value.strip():
            failures.append(f"corroborating_records[{index}] is missing source")
            continue
        source_name = source_value.casefold()
        try:
            source = HistoricalRecordSource(source_name)
        except ValueError:
            failures.append(
                f"corroborating_records[{index}] has unknown source: source={source_value!r}"
            )
            continue
        sources.add(source.value)
        if not isinstance(target, str) or not target.strip():
            failures.append(f"corroborating_records[{index}] is missing target: source={source.value!r}")
            continue
        if not isinstance(raw_payload, Mapping):
            failures.append(
                f"corroborating_records[{index}] must copy a non-empty record payload: "
                f"source={source.value!r}, target={target!r}"
            )
            continue
        payload = {
            key: value
            for key, value in raw_payload.items()
            if key not in {"source", "target", "timestamp", "start_timestamp", "end_timestamp"}
        }
        if not payload:
            failures.append(
                f"corroborating_records[{index}] has no raw payload field: "
                f"source={source.value!r}, target={target!r}"
            )
            continue
        try:
            point_timestamp = item.get("timestamp")
            interval_start = item.get("start_timestamp")
            interval_end = item.get("end_timestamp")
            if point_timestamp is not None and (interval_start is not None or interval_end is not None):
                raise ValueError("point and interval bounds cannot be mixed")
            if point_timestamp is not None:
                point_timestamp_ms = parse_utc_timestamp(
                    str(point_timestamp),
                    f"corroborating_records[{index}].timestamp",
                )
                matches = record_store.find_matching_evidence(
                    source=source,
                    target=target,
                    point_timestamp_ms=point_timestamp_ms,
                    payload=payload,
                )
            elif interval_start is not None and interval_end is not None:
                interval_start_ms = parse_utc_timestamp(
                    str(interval_start),
                    f"corroborating_records[{index}].start_timestamp",
                )
                interval_end_ms = parse_utc_timestamp(
                    str(interval_end),
                    f"corroborating_records[{index}].end_timestamp",
                )
                matches = record_store.find_matching_evidence(
                    source=source,
                    target=target,
                    interval_start_ms=interval_start_ms,
                    interval_end_ms=interval_end_ms,
                    payload=payload,
                )
            else:
                raise ValueError("record must contain timestamp or start_timestamp/end_timestamp")
        except (TypeError, ValueError) as exc:
            failures.append(
                f"corroborating_records[{index}] has invalid time or payload identity: "
                f"source={source.value!r}, target={target!r}, error={exc}"
            )
            continue
        if not matches:
            failures.append(
                f"corroborating_records[{index}] does not match frozen history: "
                f"source={source.value!r}, target={target!r}"
            )
            continue
        if not any(
            _record_overlaps(record, target_start_ms, target_end_ms)
            and _record_overlaps(record, incident_start_ms, incident_end_ms)
            for record in matches
        ):
            failures.append(
                f"corroborating_records[{index}] is outside the sealed incident window: "
                f"source={source.value!r}, target={target!r}"
            )
    if not sources & {source.value for source in HistoricalRecordSource}:
        failures.append(
            f"target window has no corroborating historical record source: sources={sorted(sources)!r}"
        )
    return sources, failures


def _record_overlaps(
    record: HistoricalPointRecord | HistoricalIntervalRecord,
    start_ms: int,
    end_ms: int,
) -> bool:
    if isinstance(record, HistoricalPointRecord):
        return start_ms <= record.timestamp_ms <= end_ms
    return record.end_ms >= start_ms and record.start_ms <= end_ms


class DiagnosisMatchingStrategy(Protocol):
    mode: str

    def match(
        self,
        expected: tuple[ExpectedCondition, ...],
        report: StructuredReport,
        applicable: bool = True,
    ) -> dict:
        raise NotImplementedError


class NotApplicableDiagnosisMatcher:
    """Return the N/A contract without constructing a diagnosis judge."""

    def __init__(self, mode: str):
        self.mode = mode

    def match(
        self,
        expected: tuple[ExpectedCondition, ...],
        report: StructuredReport,
        applicable: bool = True,
    ) -> dict:
        return _not_applicable_result(self.mode, report)


class ExactDiagnosisMatcher:
    mode = "exact"

    def match(
        self,
        expected: tuple[ExpectedCondition, ...],
        report: StructuredReport,
        applicable: bool = True,
    ) -> dict:
        if not applicable:
            return _not_applicable_result(self.mode, report)
        submitted = report.diagnosis.conditions
        submitted_terms = {term for condition in submitted for term in self._terms(condition)}
        submitted_match_terms = [
            self._terms(condition, include_evidence=True) for condition in submitted
        ]
        matched = []
        matched_indexes = {}
        missing_evidence = []
        for condition in expected:
            candidate_indexes = [
                index
                for index, terms in enumerate(submitted_match_terms)
                if self._matches_any(condition.aliases, terms)
            ]
            if not candidate_indexes:
                continue
            matched.append(condition.condition_id)
            matched_indexes[condition.condition_id] = candidate_indexes
            if not any(submitted[index].evidence for index in candidate_indexes):
                missing_evidence.append(condition.condition_id)
        missing = [condition.condition_id for condition in expected if condition.condition_id not in matched]
        critical_missing = [
            condition.condition_id
            for condition in expected
            if condition.critical and condition.condition_id in missing
        ]
        contradictory = [
            condition.condition_id
            for condition in expected
            if self._matches_contradiction(condition.contradictions, submitted_terms)
        ]
        matched_aliases = set().union(*(
            condition.aliases for condition in expected if condition.condition_id in matched
        )) if matched else set()
        extra = sorted(submitted_terms - matched_aliases)
        passed = (
            not critical_missing
            and not contradictory
            and not missing_evidence
            and len(matched) == len(expected)
        )
        return {
            "DiagnosisPass": passed,
            "diagnosis_applicable": applicable,
            "matching_mode": self.mode,
            "report_valid": True,
            "submitted_conditions": [_condition_dict(item) for item in submitted],
            "matched_conditions": matched,
            "matched_condition_indexes": matched_indexes,
            "missing_conditions": missing,
            "extra_conditions": extra,
            "critical_missing": critical_missing,
            "missing_evidence": missing_evidence,
            "contradictory_conditions": contradictory,
            "evidence_references": [evidence for item in submitted for evidence in item.evidence],
        }

    @staticmethod
    def _terms(
        condition: DiagnosisCondition,
        *,
        include_evidence: bool = False,
    ) -> set[str]:
        values = [condition.type, condition.factor, condition.entity]
        if include_evidence:
            values.extend(condition.evidence)
        return {
            ExactDiagnosisMatcher._normalize(value)
            for value in values
        }

    @staticmethod
    def _normalize(value: str) -> str:
        value = value.casefold().replace("_", " ")
        return " ".join(re.sub(r"[^\w\u3400-\u9fff]+", " ", value).split())

    @classmethod
    def _matches_any(cls, aliases: frozenset[str], terms: set[str]) -> bool:
        return any(cls._matches(alias, term) for alias in aliases for term in terms)

    @classmethod
    def _matches_contradiction(cls, aliases: frozenset[str], terms: set[str]) -> bool:
        for alias in aliases:
            normalized_alias = cls._normalize(alias)
            for term in terms:
                normalized_term = cls._normalize(term)
                if cls._matches(normalized_alias, normalized_term) and not cls._is_negated(
                    normalized_alias,
                    normalized_term,
                ):
                    return True
        return False

    @staticmethod
    def _is_negated(alias: str, term: str) -> bool:
        return re.search(
            rf"\b(?:no|not|without|never|none|neither)\b[^.;]*\b{re.escape(alias)}\b",
            term,
        ) is not None

    @classmethod
    def _matches(cls, alias: str, term: str) -> bool:
        normalized_alias = cls._normalize(alias)
        normalized_term = cls._normalize(term)
        if not normalized_alias or not normalized_term:
            return False
        if normalized_alias == normalized_term:
            return True

        # Phrase containment accepts explanatory LLM prose while preventing a
        # one-word label such as "risk" from matching an unrelated long claim.
        alias_tokens = normalized_alias.split()
        contains_cjk = re.search(r"[\u3400-\u9fff]", normalized_alias) is not None
        if len(alias_tokens) < 2 and not (contains_cjk and len(normalized_alias) >= 4):
            return False
        return f" {normalized_alias} " in f" {normalized_term} "


class DiagnosisMatcher:
    """Public exact matcher used by evaluator-specific offline normalization tests."""

    def __init__(self, expected: tuple[ExpectedCondition, ...]):
        self.expected = expected

    def match(self, report: StructuredReport, applicable: bool = True) -> dict:
        return ExactDiagnosisMatcher().match(
            self.expected,
            report,
            applicable=applicable,
        )


class SemanticDiagnosisMatcher:
    mode = "semantic"

    def __init__(self, judge: SemanticDiagnosisJudge):
        self.judge = judge

    def match(
        self,
        expected: tuple[ExpectedCondition, ...],
        report: StructuredReport,
        applicable: bool = True,
    ) -> dict:
        if not applicable:
            return _not_applicable_result(self.mode, report)
        judgment = self.judge.judge(expected, report.diagnosis.conditions)
        return self._result(expected, report, judgment)

    def _result(
        self,
        expected: tuple[ExpectedCondition, ...],
        report: StructuredReport,
        judgment: SemanticJudgment,
    ) -> dict:
        submitted = report.diagnosis.conditions
        judgments = {item.condition_id: item for item in judgment.conditions}
        validate_semantic_judgment(expected, len(submitted), judgment)
        matched = [item.condition_id for item in expected if judgments[item.condition_id].entailed_by]
        missing = [item.condition_id for item in expected if item.condition_id not in matched]
        missing_evidence = [
            item.condition_id
            for item in expected
            if judgments[item.condition_id].entailed_by
            and not any(
                submitted[index].evidence
                for index in judgments[item.condition_id].entailed_by
            )
        ]
        critical_missing = [
            item.condition_id for item in expected if item.critical and item.condition_id in missing
        ]
        contradictory = [
            item.condition_id for item in expected if judgments[item.condition_id].contradicted_by
        ]
        referenced_indexes = {
            index
            for item in judgment.conditions
            for index in (*item.entailed_by, *item.contradicted_by)
        }
        extra_indexes = [index for index in range(len(submitted)) if index not in referenced_indexes]
        passed = (
            not critical_missing
            and not contradictory
            and not missing_evidence
            and len(matched) == len(expected)
        )
        return {
            "DiagnosisPass": passed,
            "diagnosis_applicable": True,
            "matching_mode": self.mode,
            "judge_model": judgment.model,
            "judge_usage": dict(judgment.usage),
            "report_valid": True,
            "submitted_conditions": [_condition_dict(item) for item in submitted],
            "matched_conditions": matched,
            "missing_conditions": missing,
            "extra_conditions": [_condition_dict(submitted[index]) for index in extra_indexes],
            "extra_condition_indexes": extra_indexes,
            "critical_missing": critical_missing,
            "missing_evidence": missing_evidence,
            "contradictory_conditions": contradictory,
            "semantic_judgments": [item.as_dict() for item in judgment.conditions],
            "evidence_references": [evidence for item in submitted for evidence in item.evidence],
        }


def _not_applicable_result(mode: str, report: StructuredReport) -> dict:
    return {
        "DiagnosisPass": None,
        "diagnosis_applicable": False,
        "matching_mode": mode,
        "report_valid": True,
        "submitted_conditions": [_condition_dict(item) for item in report.diagnosis.conditions],
        "matched_conditions": [],
        "missing_conditions": [],
        "extra_conditions": [],
        "critical_missing": [],
        "contradictory_conditions": [],
        "evidence_references": [
            evidence for item in report.diagnosis.conditions for evidence in item.evidence
        ],
    }


def _condition_dict(condition: DiagnosisCondition) -> Mapping[str, object]:
    return {
        "type": condition.type,
        "factor": condition.factor,
        "entity": condition.entity,
        "evidence": list(condition.evidence),
    }
