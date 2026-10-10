"""Append-only episodic memory and lexical retrieval for V-ExpeL."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import re
import threading


MEMORY_SCHEMA = "v_expel_memory_v1"
_CARD_KINDS = frozenset({"procedure", "anti_pattern"})
_CARD_STATUSES = frozenset({"active", "retired"})
_OPERATIONS = frozenset({"ADD", "EDIT", "UPVOTE", "DOWNVOTE"})
_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"V-ExpeL {field} must be a non-empty string: value={value!r}")
    return value.strip()


def _positive_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"V-ExpeL {field} must be a positive integer: value={value!r}")
    return value


def _tokens(value: str) -> frozenset[str]:
    return frozenset(_TOKEN_RE.findall(value.casefold()))


def _cue_key(cue: str) -> str:
    return " ".join(sorted(_tokens(cue)))


@dataclass(frozen=True, slots=True)
class ExperienceRecord:
    """Sanitized public trajectory used to justify one memory consolidation."""

    record_id: str
    cue: str
    kind: str
    attempted_actions: tuple[str, ...]
    reported_changes: tuple[str, ...]
    reported_verification: tuple[str, ...]
    trusted_outcome: str
    trusted_safety: str

    def __post_init__(self) -> None:
        _text(self.record_id, field="record_id")
        _text(self.cue, field="cue")
        if self.kind not in _CARD_KINDS:
            raise ValueError(f"V-ExpeL experience kind is unsupported: kind={self.kind!r}")
        for name, values in (
            ("attempted_actions", self.attempted_actions),
            ("reported_changes", self.reported_changes),
            ("reported_verification", self.reported_verification),
        ):
            if not isinstance(values, tuple) or any(not isinstance(item, str) or not item.strip() for item in values):
                raise TypeError(f"V-ExpeL experience {name} must be a tuple of non-empty strings: value={values!r}")
        if self.trusted_outcome not in {"pass", "fail"}:
            raise ValueError(f"V-ExpeL trusted_outcome is unsupported: value={self.trusted_outcome!r}")
        if self.trusted_safety not in {"pass", "fail"}:
            raise ValueError(f"V-ExpeL trusted_safety is unsupported: value={self.trusted_safety!r}")

    def as_dict(self) -> dict[str, object]:
        return {
            "record_id": self.record_id,
            "cue": self.cue,
            "kind": self.kind,
            "attempted_actions": list(self.attempted_actions),
            "reported_changes": list(self.reported_changes),
            "reported_verification": list(self.reported_verification),
            "trusted_outcome": self.trusted_outcome,
            "trusted_safety": self.trusted_safety,
        }


@dataclass(frozen=True, slots=True)
class MemoryCard:
    """A reusable insight promoted from a trusted checkpoint."""

    card_id: str
    kind: str
    cue: str
    lesson: str
    actions: tuple[str, ...]
    verification: tuple[str, ...]
    support_count: int = 1
    counterexample_count: int = 0
    version: int = 1
    status: str = "active"
    provenance: tuple[str, ...] = ("trusted_checkpoint",)

    def __post_init__(self) -> None:
        _text(self.card_id, field="card_id")
        if self.kind not in _CARD_KINDS:
            raise ValueError(f"V-ExpeL memory card kind is unsupported: kind={self.kind!r}")
        _text(self.cue, field="card cue")
        _text(self.lesson, field="card lesson")
        for name, values in (("actions", self.actions), ("verification", self.verification)):
            if not isinstance(values, tuple) or any(not isinstance(item, str) or not item.strip() for item in values):
                raise TypeError(f"V-ExpeL card {name} must be a tuple of non-empty strings: value={values!r}")
        if isinstance(self.support_count, bool) or not isinstance(self.support_count, int) or self.support_count < 0:
            raise ValueError(f"V-ExpeL card support_count must be non-negative: value={self.support_count!r}")
        if isinstance(self.counterexample_count, bool) or not isinstance(self.counterexample_count, int) or self.counterexample_count < 0:
            raise ValueError(
                "V-ExpeL card counterexample_count must be non-negative: "
                f"value={self.counterexample_count!r}"
            )
        _positive_int(self.version, field="card version")
        if self.status not in _CARD_STATUSES:
            raise ValueError(f"V-ExpeL card status is unsupported: status={self.status!r}")
        if not isinstance(self.provenance, tuple) or any(not isinstance(item, str) or not item.strip() for item in self.provenance):
            raise TypeError(f"V-ExpeL card provenance must be a tuple of non-empty strings: value={self.provenance!r}")

    @property
    def cue_key(self) -> str:
        return _cue_key(self.cue)

    def as_dict(self) -> dict[str, object]:
        return {
            "card_id": self.card_id,
            "kind": self.kind,
            "cue": self.cue,
            "lesson": self.lesson,
            "actions": list(self.actions),
            "verification": list(self.verification),
            "support_count": self.support_count,
            "counterexample_count": self.counterexample_count,
            "version": self.version,
            "status": self.status,
            "provenance": list(self.provenance),
        }

    def prompt_text(self) -> str:
        lines = [f"[{self.kind}]", f"cue: {self.cue}", f"lesson: {self.lesson}"]
        if self.actions:
            lines.append("observed sequence: " + " -> ".join(self.actions))
        if self.verification:
            lines.append("verification evidence: " + " | ".join(self.verification))
        return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class MemoryOperation:
    operation: str
    card_id: str
    card_kind: str
    version: int

    def __post_init__(self) -> None:
        if self.operation not in _OPERATIONS:
            raise ValueError(f"V-ExpeL memory operation is unsupported: operation={self.operation!r}")
        _text(self.card_id, field="operation card_id")
        if self.card_kind not in _CARD_KINDS:
            raise ValueError(f"V-ExpeL operation card kind is unsupported: kind={self.card_kind!r}")
        _positive_int(self.version, field="operation version")

    def as_dict(self) -> dict[str, object]:
        return {
            "operation": self.operation,
            "card_id": self.card_id,
            "card_kind": self.card_kind,
            "version": self.version,
        }


def card_id_for(kind: str, cue: str) -> str:
    if kind not in _CARD_KINDS:
        raise ValueError(f"V-ExpeL card ID requires a supported kind: kind={kind!r}")
    key = f"{kind}\0{_cue_key(_text(cue, field='card ID cue'))}"
    return f"card-{hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]}"


class VExpeLMemory:
    """Run-scoped memory with deterministic retrieval and explicit consolidation."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._cards: dict[str, MemoryCard] = {}
        self._records: list[ExperienceRecord] = []
        self._retrievals: list[dict[str, object]] = []

    def retrieve(self, mailbox_status: Mapping[str, object], *, top_k: int) -> tuple[MemoryCard, ...]:
        if not isinstance(mailbox_status, Mapping):
            raise TypeError(f"V-ExpeL mailbox status must be a mapping: value={mailbox_status!r}")
        pending = mailbox_status.get("pending")
        completed = mailbox_status.get("completed")
        if not isinstance(pending, list) or not isinstance(completed, list):
            raise TypeError(
                "V-ExpeL mailbox status must contain pending and completed lists: "
                f"pending={pending!r}, completed={completed!r}"
            )
        tasks = pending if pending else completed
        if any(not isinstance(task, Mapping) for task in tasks):
            raise TypeError(f"V-ExpeL mailbox task projection must be a mapping: tasks={tasks!r}")
        query_parts: list[str] = []
        for task in tasks:
            query_parts.extend(
                str(task[key])
                for key in ("title", "description", "severity", "category")
                if task.get(key) is not None
            )
            symptoms = task.get("symptoms", [])
            if not isinstance(symptoms, list):
                raise TypeError(f"V-ExpeL task symptoms must be a list: task={task!r}")
            query_parts.extend(str(symptom) for symptom in symptoms)
        return self.retrieve_query(" ".join(query_parts).strip(), top_k=top_k, source="mailbox_read")

    def retrieve_query(self, query: str, *, top_k: int, source: str) -> tuple[MemoryCard, ...]:
        """Rank active cards against an explicit query with deterministic lexical overlap."""
        if not isinstance(query, str):
            raise TypeError(f"V-ExpeL retrieval query must be a string: value={query!r}")
        if not isinstance(source, str) or not source.strip():
            raise ValueError(f"V-ExpeL retrieval source must be a non-empty string: source={source!r}")
        _positive_int(top_k, field="retrieval top_k")
        query_tokens = _tokens(query)
        with self._lock:
            scored = []
            for card in self._cards.values():
                if card.status != "active":
                    continue
                card_tokens = _tokens(card.cue)
                union = query_tokens | card_tokens
                score = len(query_tokens & card_tokens) / len(union) if union else 0.0
                if score > 0:
                    scored.append((score, card.support_count, -card.counterexample_count, card.card_id, card))
            scored.sort(key=lambda item: item[:4], reverse=True)
            matches = tuple(item[4] for item in scored[:top_k])
            self._retrievals.append(
                {
                    "source": source,
                    "query": query,
                    "card_ids": [card.card_id for card in matches],
                    "scores": [round(item[0], 6) for item in scored[:top_k]],
                }
            )
            return matches

    def consolidate(self, record: ExperienceRecord, candidate: MemoryCard) -> tuple[MemoryOperation, ...]:
        if candidate.kind != record.kind or candidate.cue != record.cue:
            raise ValueError(
                "V-ExpeL candidate does not describe its experience record: "
                f"record_id={record.record_id!r}, candidate={candidate.as_dict()!r}"
            )
        with self._lock:
            if any(existing.record_id == record.record_id for existing in self._records):
                raise ValueError(f"V-ExpeL experience record already consolidated: record_id={record.record_id!r}")
            self._records.append(record)
            operations: list[MemoryOperation] = []
            same_kind = self._cards.get(candidate.card_id)
            if same_kind is None:
                self._cards[candidate.card_id] = candidate
                operations.append(MemoryOperation("ADD", candidate.card_id, candidate.kind, candidate.version))
            else:
                updated = MemoryCard(
                    card_id=same_kind.card_id,
                    kind=same_kind.kind,
                    cue=same_kind.cue,
                    lesson=candidate.lesson,
                    actions=candidate.actions,
                    verification=candidate.verification,
                    support_count=same_kind.support_count + 1,
                    counterexample_count=same_kind.counterexample_count,
                    version=same_kind.version + 1,
                    status="active",
                    provenance=same_kind.provenance,
                )
                self._cards[updated.card_id] = updated
                operation = (
                    "UPVOTE"
                    if (
                        same_kind.lesson == candidate.lesson
                        and same_kind.actions == candidate.actions
                        and same_kind.verification == candidate.verification
                    )
                    else "EDIT"
                )
                operations.append(MemoryOperation(operation, updated.card_id, updated.kind, updated.version))
            for card_id, card in tuple(self._cards.items()):
                if card_id == candidate.card_id or card.cue_key != candidate.cue_key or card.kind == candidate.kind:
                    continue
                counterexample_count = card.counterexample_count + 1
                status = "retired" if counterexample_count > card.support_count else card.status
                updated = MemoryCard(
                    card_id=card.card_id,
                    kind=card.kind,
                    cue=card.cue,
                    lesson=card.lesson,
                    actions=card.actions,
                    verification=card.verification,
                    support_count=card.support_count,
                    counterexample_count=counterexample_count,
                    version=card.version + 1,
                    status=status,
                    provenance=card.provenance,
                )
                self._cards[card_id] = updated
                operations.append(MemoryOperation("DOWNVOTE", card_id, updated.kind, updated.version))
            return tuple(operations)

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return {
                "$schema": MEMORY_SCHEMA,
                "cards": [self._cards[card_id].as_dict() for card_id in sorted(self._cards)],
                "records": [record.as_dict() for record in self._records],
                "retrievals": deepcopy(self._retrievals),
            }

    def summary(self) -> dict[str, object]:
        with self._lock:
            return {
                "$schema": MEMORY_SCHEMA,
                "card_count": len(self._cards),
                "active_card_count": sum(card.status == "active" for card in self._cards.values()),
                "experience_count": len(self._records),
                "retrieval_count": len(self._retrievals),
            }

    def render(self, cards: tuple[MemoryCard, ...]) -> str:
        if not isinstance(cards, tuple) or any(not isinstance(card, MemoryCard) for card in cards):
            raise TypeError(f"V-ExpeL render requires a tuple of MemoryCard: cards={cards!r}")
        if not cards:
            return (
                "Verified prior experience memory: no matching card was found. "
                "Use current database evidence and record a verified result after the work."
            )
        return (
            "Verified prior experience memory follows. Treat each card as a hypothesis, "
            "validate it against current database evidence, and never reuse dynamic identifiers blindly.\n\n"
            + "\n\n".join(card.prompt_text() for card in cards)
        )

    def cards(self) -> tuple[MemoryCard, ...]:
        with self._lock:
            return tuple(self._cards[card_id] for card_id in sorted(self._cards))
