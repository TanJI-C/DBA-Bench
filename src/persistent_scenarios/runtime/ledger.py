"""Business ledgers: typed records plus an append-only, tamper-evident store.

Ledgers are the trusted business truth of a run. They live outside the
database (agent-unwritable), append hash-chained events, and materialize
records where retries merge into one business identity and nothing can
silently disappear - queueing, cancellation and cross-horizon work included.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import threading
from pathlib import Path
from typing import Mapping

from ..model.spec import JSONValue
from .encoding import jsonable


class AttemptOutcome(str, Enum):
    COMMITTED = "committed"
    ABORTED = "aborted"
    TIMED_OUT = "timed_out"
    CONNECTION_REFUSED = "connection_refused"
    CANCELLED = "cancelled"


class JobAttemptOutcome(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LedgerTerminal(str, Enum):
    COMPLETED = "completed"
    INCOMPLETE_TIMEOUT = "incomplete_timeout"
    INCOMPLETE_ERROR = "incomplete_error"
    INCOMPLETE_CANCELLED = "incomplete_cancelled"
    INCOMPLETE_OUTSTANDING = "incomplete_outstanding"


OUTSTANDING_TERMINAL = LedgerTerminal.INCOMPLETE_OUTSTANDING

_SEAL_KIND = "seal"


@dataclass(frozen=True, slots=True)
class TransactionAttempt:
    attempt_index: int
    started_at_monotonic: float
    ended_at_monotonic: float
    outcome: AttemptOutcome
    detail: Mapping[str, JSONValue]


@dataclass(frozen=True, slots=True)
class LogicalTransactionRecord:
    business_id: str
    service_id: str
    tx_kind: str
    planned_at_monotonic: float
    deadline_at_monotonic: float
    attempts: tuple[TransactionAttempt, ...]
    terminal: LedgerTerminal
    completed_at_monotonic: float | None
    result_digest: str | None

    @property
    def good(self) -> bool:
        """Correctly completed within the business deadline."""
        return (
            self.terminal is LedgerTerminal.COMPLETED
            and self.completed_at_monotonic is not None
            and self.completed_at_monotonic <= self.deadline_at_monotonic
        )


@dataclass(frozen=True, slots=True)
class JobAttempt:
    attempt_index: int
    queued_at_monotonic: float
    started_at_monotonic: float | None
    ended_at_monotonic: float | None
    outcome: JobAttemptOutcome
    detail: Mapping[str, JSONValue]


@dataclass(frozen=True, slots=True)
class JobRecord:
    job_id: str
    service_id: str
    job_kind: str
    batch_version: str | None
    input_snapshot: Mapping[str, JSONValue] | None
    submitted_at_monotonic: float
    deadline_at_monotonic: float
    attempts: tuple[JobAttempt, ...]
    terminal: LedgerTerminal
    delivered_at_monotonic: float | None
    result_digest: str | None

    @property
    def delivered_on_time(self) -> bool:
        return (
            self.terminal is LedgerTerminal.COMPLETED
            and self.delivered_at_monotonic is not None
            and self.delivered_at_monotonic <= self.deadline_at_monotonic
        )


@dataclass(frozen=True, slots=True)
class FreshnessSample:
    sample_id: str
    sampled_at_monotonic: float
    primary_watermark: str
    replica_watermark: str
    lag_seconds: float | None
    detail: Mapping[str, JSONValue]


def _require_text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string: value={value!r}")


def _require_positive(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{name} must be positive: value={value!r}")


class TrustedLedger:
    """Append-only hash-chained ledger file.

    Each line is ``{"seq", "prev_digest", "digest", "kind", "record"}`` with
    ``digest = sha256(prev_digest + canonical_json(record))``. The ledger is
    written only by trusted runtime processes; ``verify()`` recomputes the
    chain so any tampering is detected at seal time.
    """

    def __init__(self, ledger_id: str, path: Path):
        _require_text("ledger_id", ledger_id)
        self.ledger_id = ledger_id
        self.path = Path(path)
        self._lock = threading.Lock()
        self._seq = 0
        self._digest = hashlib.sha256(f"trusted-ledger:{ledger_id}".encode("utf-8")).hexdigest()
        self._sealed = False
        self._event_counts: dict[str, int] = {}
        self._planned_records: set[tuple[str, str]] = set()
        self._open_records: dict[tuple[str, str], str] = {}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(mode=0o600, exist_ok=False)

    def append(self, kind: str, record: Mapping[str, JSONValue]) -> None:
        if not isinstance(kind, str) or not kind.strip():
            raise ValueError(f"ledger event kind must be a non-empty string: value={kind!r}")
        encoded = json.dumps(jsonable(dict(record)), ensure_ascii=False, sort_keys=True)
        with self._lock:
            if self._sealed:
                raise RuntimeError(
                    f"ledger {self.ledger_id!r} is sealed and cannot accept events: kind={kind!r}"
                )
            self._seq += 1
            digest = hashlib.sha256(f"{self._digest}:{encoded}".encode("utf-8")).hexdigest()
            line = json.dumps(
                {"seq": self._seq, "prev_digest": self._digest, "digest": digest, "kind": kind, "record": jsonable(dict(record))},
                ensure_ascii=False,
                sort_keys=True,
            )
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
                handle.flush()
            self._digest = digest
            self._event_counts[kind] = self._event_counts.get(kind, 0) + 1
            if kind == _SEAL_KIND:
                self._sealed = True

    def event_count(self, kind: str) -> int:
        with self._lock:
            return self._event_counts.get(kind, 0)

    def finalize_outstanding(self, now_monotonic: float) -> None:
        """Close every still-open record as outstanding at the scoring end.

        Nothing may disappear from the ledger because the horizon ended:
        queued and in-flight work becomes an explicit loss, never a shrunk
        denominator.
        """
        with self._lock:
            pending = sorted(self._open_records.items())
        for (kind, record_id), _service_id in pending:
            if kind == "transaction":
                self.append_transaction_terminal(
                    business_id=record_id,
                    terminal=OUTSTANDING_TERMINAL,
                    completed_at_monotonic=None,
                    result_digest=None,
                )
            else:
                self.append_job_terminal(
                    job_id=record_id,
                    terminal=OUTSTANDING_TERMINAL,
                    delivered_at_monotonic=None,
                    result_digest=None,
                )

    def seal(self) -> str:
        with self._lock:
            if self._sealed:
                raise RuntimeError(f"ledger {self.ledger_id!r} is already sealed")
        self.append(_SEAL_KIND, {"ledger_id": self.ledger_id, "final_digest": self._digest})
        return self._digest

    def verify(self) -> None:
        """Recompute the full hash chain; raise on any tamper or truncation."""
        previous = hashlib.sha256(f"trusted-ledger:{self.ledger_id}".encode("utf-8")).hexdigest()
        expected_seq = 0
        sealed = False
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"ledger {self.ledger_id!r} contains a corrupt line: path={self.path!r}, line={line_number}, error={exc!r}"
                    ) from exc
                expected_seq += 1
                if entry.get("seq") != expected_seq:
                    raise ValueError(
                        f"ledger {self.ledger_id!r} sequence is broken: path={self.path!r}, "
                        f"line={line_number}, expected_seq={expected_seq}, found={entry.get('seq')!r}"
                    )
                encoded = json.dumps(entry["record"], ensure_ascii=False, sort_keys=True)
                digest = hashlib.sha256(f"{previous}:{encoded}".encode("utf-8")).hexdigest()
                if entry.get("prev_digest") != previous or entry.get("digest") != digest:
                    raise ValueError(
                        f"ledger {self.ledger_id!r} hash chain mismatch (tamper audit failed): "
                        f"path={self.path!r}, line={line_number}, expected_digest={digest!r}, found={entry.get('digest')!r}"
                    )
                previous = digest
                if entry.get("kind") == _SEAL_KIND:
                    sealed = True
        if not sealed:
            raise RuntimeError(f"ledger {self.ledger_id!r} is not sealed: path={self.path!r}")
        with self._lock:
            if self._seq != expected_seq:
                raise ValueError(
                    f"ledger {self.ledger_id!r} lost appended events: path={self.path!r}, "
                    f"in_memory_seq={self._seq}, file_seq={expected_seq}"
                )

    # -- typed append helpers -------------------------------------------------

    def append_planned_transaction(
        self,
        *,
        business_id: str,
        service_id: str,
        tx_kind: str,
        planned_at_monotonic: float,
        deadline_at_monotonic: float,
    ) -> None:
        _require_text("business_id", business_id)
        _require_positive("deadline_at_monotonic", deadline_at_monotonic)
        with self._lock:
            if ("transaction", business_id) in self._planned_records:
                raise ValueError(
                    f"transaction {business_id!r} is already planned in ledger {self.ledger_id!r}"
                )
            self._planned_records.add(("transaction", business_id))
            self._open_records[("transaction", business_id)] = service_id
        self.append(
            "planned_transaction",
            {
                "business_id": business_id,
                "service_id": service_id,
                "tx_kind": tx_kind,
                "planned_at_monotonic": planned_at_monotonic,
                "deadline_at_monotonic": deadline_at_monotonic,
            },
        )

    def append_transaction_attempt(self, *, business_id: str, attempt: TransactionAttempt) -> None:
        self.append(
            "transaction_attempt",
            {
                "business_id": business_id,
                "attempt_index": attempt.attempt_index,
                "started_at_monotonic": attempt.started_at_monotonic,
                "ended_at_monotonic": attempt.ended_at_monotonic,
                "outcome": attempt.outcome.value,
                "detail": jsonable(dict(attempt.detail)),
            },
        )

    def append_transaction_terminal(
        self,
        *,
        business_id: str,
        terminal: LedgerTerminal,
        completed_at_monotonic: float | None,
        result_digest: str | None,
    ) -> None:
        if terminal is LedgerTerminal.COMPLETED and completed_at_monotonic is None:
            raise ValueError(f"completed transaction requires completed_at_monotonic: business_id={business_id!r}")
        if terminal is not LedgerTerminal.COMPLETED and result_digest is not None:
            raise ValueError(f"incomplete transaction cannot carry a result digest: business_id={business_id!r}")
        with self._lock:
            if ("transaction", business_id) not in self._open_records:
                raise ValueError(
                    f"transaction {business_id!r} terminal decided twice in ledger {self.ledger_id!r}"
                )
            self._open_records.pop(("transaction", business_id), None)
        self.append(
            "transaction_terminal",
            {
                "business_id": business_id,
                "terminal": terminal.value,
                "completed_at_monotonic": completed_at_monotonic,
                "result_digest": result_digest,
            },
        )

    def append_job_planned(
        self,
        *,
        job_id: str,
        service_id: str,
        job_kind: str,
        batch_version: str | None,
        input_snapshot: Mapping[str, JSONValue] | None,
        submitted_at_monotonic: float,
        deadline_at_monotonic: float,
    ) -> None:
        _require_text("job_id", job_id)
        _require_positive("deadline_at_monotonic", deadline_at_monotonic)
        with self._lock:
            if ("job", job_id) in self._planned_records:
                raise ValueError(f"job {job_id!r} is already planned in ledger {self.ledger_id!r}")
            self._planned_records.add(("job", job_id))
            self._open_records[("job", job_id)] = service_id
        self.append(
            "planned_job",
            {
                "job_id": job_id,
                "service_id": service_id,
                "job_kind": job_kind,
                "batch_version": batch_version,
                "input_snapshot": jsonable(dict(input_snapshot)) if input_snapshot is not None else None,
                "submitted_at_monotonic": submitted_at_monotonic,
                "deadline_at_monotonic": deadline_at_monotonic,
            },
        )

    def append_job_attempt(self, *, job_id: str, attempt: JobAttempt) -> None:
        self.append(
            "job_attempt",
            {
                "job_id": job_id,
                "attempt_index": attempt.attempt_index,
                "queued_at_monotonic": attempt.queued_at_monotonic,
                "started_at_monotonic": attempt.started_at_monotonic,
                "ended_at_monotonic": attempt.ended_at_monotonic,
                "outcome": attempt.outcome.value,
                "detail": jsonable(dict(attempt.detail)),
            },
        )

    def append_job_terminal(
        self,
        *,
        job_id: str,
        terminal: LedgerTerminal,
        delivered_at_monotonic: float | None,
        result_digest: str | None,
    ) -> None:
        if terminal is LedgerTerminal.COMPLETED and (delivered_at_monotonic is None or result_digest is None):
            raise ValueError(
                f"delivered job requires delivered_at_monotonic and result_digest: job_id={job_id!r}"
            )
        if terminal is not LedgerTerminal.COMPLETED and result_digest is not None:
            raise ValueError(f"undelivered job cannot carry a result digest: job_id={job_id!r}")
        with self._lock:
            if ("job", job_id) not in self._open_records:
                raise ValueError(f"job {job_id!r} terminal decided twice in ledger {self.ledger_id!r}")
            self._open_records.pop(("job", job_id), None)
        self.append(
            "job_terminal",
            {
                "job_id": job_id,
                "terminal": terminal.value,
                "delivered_at_monotonic": delivered_at_monotonic,
                "result_digest": result_digest,
            },
        )

    def append_freshness_sample(self, sample: FreshnessSample) -> None:
        self.append(
            "freshness_sample",
            {
                "sample_id": sample.sample_id,
                "sampled_at_monotonic": sample.sampled_at_monotonic,
                "primary_watermark": sample.primary_watermark,
                "replica_watermark": sample.replica_watermark,
                "lag_seconds": sample.lag_seconds,
                "detail": jsonable(dict(sample.detail)),
            },
        )


class LedgerView:
    """Materialized read-only view over one trusted ledger."""

    def __init__(self, ledger: TrustedLedger):
        self._transactions: dict[str, dict] = {}
        self._jobs: dict[str, dict] = {}
        self._freshness: list[FreshnessSample] = []
        self._transaction_order: list[str] = []
        self._job_order: list[str] = []
        with ledger.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                entry = json.loads(line)
                kind = entry["kind"]
                record = entry["record"]
                try:
                    self._consume(kind, record)
                except (KeyError, TypeError, ValueError) as exc:
                    raise ValueError(
                        f"ledger {ledger.ledger_id!r} contains an invalid {kind!r} event: "
                        f"path={ledger.path!r}, line={line_number}, error={exc!r}"
                    ) from exc

    def _consume(self, kind: str, record: dict) -> None:
        if kind == "planned_transaction":
            business_id = record["business_id"]
            if business_id in self._transactions:
                raise ValueError(f"transaction {business_id!r} planned twice")
            self._transactions[business_id] = {
                "business_id": business_id,
                "service_id": record["service_id"],
                "tx_kind": record["tx_kind"],
                "planned_at_monotonic": record["planned_at_monotonic"],
                "deadline_at_monotonic": record["deadline_at_monotonic"],
                "attempts": [],
                "terminal": None,
                "completed_at_monotonic": None,
                "result_digest": None,
            }
            self._transaction_order.append(business_id)
        elif kind == "transaction_attempt":
            state = self._transactions[record["business_id"]]
            state["attempts"].append(TransactionAttempt(
                attempt_index=record["attempt_index"],
                started_at_monotonic=record["started_at_monotonic"],
                ended_at_monotonic=record["ended_at_monotonic"],
                outcome=AttemptOutcome(record["outcome"]),
                detail=dict(record["detail"]),
            ))
        elif kind == "transaction_terminal":
            state = self._transactions[record["business_id"]]
            if state["terminal"] is not None:
                raise ValueError(f"transaction {record['business_id']!r} terminal decided twice")
            state["terminal"] = LedgerTerminal(record["terminal"])
            state["completed_at_monotonic"] = record["completed_at_monotonic"]
            state["result_digest"] = record["result_digest"]
        elif kind == "planned_job":
            job_id = record["job_id"]
            if job_id in self._jobs:
                raise ValueError(f"job {job_id!r} planned twice")
            self._jobs[job_id] = {
                "job_id": job_id,
                "service_id": record["service_id"],
                "job_kind": record["job_kind"],
                "batch_version": record["batch_version"],
                "input_snapshot": record["input_snapshot"],
                "submitted_at_monotonic": record["submitted_at_monotonic"],
                "deadline_at_monotonic": record["deadline_at_monotonic"],
                "attempts": [],
                "terminal": None,
                "delivered_at_monotonic": None,
                "result_digest": None,
            }
            self._job_order.append(job_id)
        elif kind == "job_attempt":
            state = self._jobs[record["job_id"]]
            state["attempts"].append(JobAttempt(
                attempt_index=record["attempt_index"],
                queued_at_monotonic=record["queued_at_monotonic"],
                started_at_monotonic=record["started_at_monotonic"],
                ended_at_monotonic=record["ended_at_monotonic"],
                outcome=JobAttemptOutcome(record["outcome"]),
                detail=dict(record["detail"]),
            ))
        elif kind == "job_terminal":
            state = self._jobs[record["job_id"]]
            if state["terminal"] is not None:
                raise ValueError(f"job {record['job_id']!r} terminal decided twice")
            state["terminal"] = LedgerTerminal(record["terminal"])
            state["delivered_at_monotonic"] = record["delivered_at_monotonic"]
            state["result_digest"] = record["result_digest"]
        elif kind == "freshness_sample":
            self._freshness.append(FreshnessSample(
                sample_id=record["sample_id"],
                sampled_at_monotonic=record["sampled_at_monotonic"],
                primary_watermark=record["primary_watermark"],
                replica_watermark=record["replica_watermark"],
                lag_seconds=record["lag_seconds"],
                detail=dict(record["detail"]),
            ))
        elif kind == _SEAL_KIND:
            pass
        else:
            raise ValueError(f"unknown ledger event kind: kind={kind!r}")

    @staticmethod
    def _finalize(records: list[dict], id_field: str) -> list:
        finalized = []
        for state in records:
            if state["terminal"] is None:
                raise ValueError(f"{id_field} {state[id_field]!r} never reached a terminal state")
            finalized.append(state)
        return finalized

    def logical_transactions(self) -> tuple[LogicalTransactionRecord, ...]:
        records = []
        for state in self._finalize([self._transactions[key] for key in self._transaction_order], "business_id"):
            records.append(LogicalTransactionRecord(
                business_id=state["business_id"],
                service_id=state["service_id"],
                tx_kind=state["tx_kind"],
                planned_at_monotonic=state["planned_at_monotonic"],
                deadline_at_monotonic=state["deadline_at_monotonic"],
                attempts=tuple(state["attempts"]),
                terminal=state["terminal"],
                completed_at_monotonic=state["completed_at_monotonic"],
                result_digest=state["result_digest"],
            ))
        return tuple(records)

    def jobs(self) -> tuple[JobRecord, ...]:
        records = []
        for state in self._finalize([self._jobs[key] for key in self._job_order], "job_id"):
            records.append(JobRecord(
                job_id=state["job_id"],
                service_id=state["service_id"],
                job_kind=state["job_kind"],
                batch_version=state["batch_version"],
                input_snapshot=state["input_snapshot"],
                submitted_at_monotonic=state["submitted_at_monotonic"],
                deadline_at_monotonic=state["deadline_at_monotonic"],
                attempts=tuple(state["attempts"]),
                terminal=state["terminal"],
                delivered_at_monotonic=state["delivered_at_monotonic"],
                result_digest=state["result_digest"],
            ))
        return tuple(records)

    def freshness_samples(self) -> tuple[FreshnessSample, ...]:
        return tuple(self._freshness)
