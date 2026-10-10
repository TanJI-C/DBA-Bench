"""Append-only mailbox document for a persistent PersistentScenario Agent."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
import threading


_TASK_TYPES = frozenset({"incident", "periodic_inspection"})
_TASK_STATES = frozenset({"pending", "completed"})


@dataclass(frozen=True, slots=True)
class MailboxTask:
    sequence: int
    task_id: str
    task_type: str
    created_at_monotonic: float
    title: str
    description: str
    severity: str | None
    category: str | None
    symptoms: tuple[str, ...]
    status: str
    updated_at_monotonic: float
    completed_at_monotonic: float | None
    completion: Mapping[str, object] | None

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise ValueError(f"Mailbox task sequence must be positive: sequence={self.sequence}")
        if not self.task_id.strip():
            raise ValueError(f"Mailbox task_id must be non-empty: task_id={self.task_id!r}")
        if self.task_type not in _TASK_TYPES:
            raise ValueError(
                f"Unsupported mailbox task_type: task_id={self.task_id!r}, task_type={self.task_type!r}"
            )
        if not self.title.strip() or not self.description.strip():
            raise ValueError(f"Mailbox task text must be non-empty: task_id={self.task_id!r}")
        if self.status not in _TASK_STATES:
            raise ValueError(f"Unsupported mailbox task status: task_id={self.task_id!r}, status={self.status!r}")
        if self.status == "completed" and self.completed_at_monotonic is None:
            raise ValueError(f"Completed mailbox task requires completed_at_monotonic: task_id={self.task_id!r}")
        if self.status != "completed" and self.completed_at_monotonic is not None:
            raise ValueError(f"Open mailbox task cannot have completed_at_monotonic: task_id={self.task_id!r}")

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"

    def as_agent_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "sequence": self.sequence,
            "task_id": self.task_id,
            "status": self.status,
            "created_at_monotonic": self.created_at_monotonic,
            "updated_at_monotonic": self.updated_at_monotonic,
            "title": self.title,
            "description": self.description,
            "symptoms": list(self.symptoms),
        }
        if self.severity is not None:
            payload["severity"] = self.severity
        if self.category is not None:
            payload["category"] = self.category
        if self.completed_at_monotonic is not None:
            payload["completed_at_monotonic"] = self.completed_at_monotonic
        if self.completion is not None:
            payload["report"] = dict(self.completion)
        return payload


class PersistentScenarioMailbox:
    """Thread-safe append-only mailbox document with a live task projection."""

    def __init__(
        self,
        stop_signal: threading.Event,
        *,
        on_change: Callable[[Mapping[str, object]], None] | None = None,
    ) -> None:
        self._stop = stop_signal
        self._condition = threading.Condition(threading.RLock())
        self._publish_lock = threading.Lock()
        self._on_change = on_change
        self._items: list[MailboxTask] = []
        self._items_by_id: dict[str, MailboxTask] = {}
        self._history: list[dict[str, object]] = []
        self._revision = 0
        self._sequence = 0

    @property
    def revision(self) -> int:
        with self._condition:
            return self._revision

    def publish(
        self,
        *,
        task_type: str,
        created_at_monotonic: float,
        title: str,
        description: str,
        severity: str | None = None,
        category: str | None = None,
        symptoms: tuple[str, ...] = (),
        on_published: Callable[[MailboxTask], None] | None = None,
    ) -> MailboxTask:
        if task_type not in _TASK_TYPES:
            raise ValueError(f"Unsupported mailbox task_type: task_type={task_type!r}")
        # Registration prepares the control plane before the task becomes visible
        # to the Agent. The document lock is released during that callback so
        # task publication cannot deadlock with an Agent mutation.
        with self._publish_lock:
            with self._condition:
                self._sequence += 1
                task = MailboxTask(
                    sequence=self._sequence,
                    task_id=f"task-{self._sequence:04d}",
                    task_type=task_type,
                    created_at_monotonic=created_at_monotonic,
                    title=title,
                    description=description,
                    severity=severity,
                    category=category,
                    symptoms=tuple(symptoms),
                    status="pending",
                    updated_at_monotonic=created_at_monotonic,
                    completed_at_monotonic=None,
                    completion=None,
                )
            if on_published is not None:
                on_published(task)
            with self._condition:
                self._items.append(task)
                self._items_by_id[task.task_id] = task
                self._record_change("published", task, created_at_monotonic)
                self._condition.notify_all()
                return task

    def complete(
        self,
        task_id: str,
        completed_at_monotonic: float,
        completion: Mapping[str, object],
    ) -> MailboxTask:
        if not isinstance(completion, Mapping):
            raise TypeError(f"Mailbox task completion must be a mapping: task_id={task_id!r}, completion={completion!r}")
        with self._condition:
            task = self._require(task_id)
            if task.status == "completed":
                raise ValueError(f"Mailbox task is already completed: task_id={task_id!r}")
            updated = replace(
                task,
                status="completed",
                updated_at_monotonic=completed_at_monotonic,
                completed_at_monotonic=completed_at_monotonic,
                completion=dict(completion),
            )
            return self._replace("completed", task, updated, completed_at_monotonic)

    def complete_many(
        self,
        task_ids: list[str],
        completed_at_monotonic: float,
        completion: Mapping[str, object],
    ) -> tuple[MailboxTask, ...]:
        if not task_ids:
            raise ValueError("Mailbox complete_many requires at least one task_id")
        if not all(isinstance(task_id, str) and task_id.strip() for task_id in task_ids):
            raise TypeError(f"Mailbox complete_many requires non-empty string task IDs: task_ids={task_ids!r}")
        if len(task_ids) != len(set(task_ids)):
            raise ValueError(f"Mailbox complete_many task IDs must be unique: task_ids={task_ids!r}")
        if not isinstance(completion, Mapping):
            raise TypeError(f"Mailbox task completion must be a mapping: completion={completion!r}")
        with self._condition:
            tasks = tuple(self._require(task_id) for task_id in task_ids)
            if any(task.status == "completed" for task in tasks):
                completed = [task.task_id for task in tasks if task.status == "completed"]
                raise ValueError(f"Mailbox task is already completed: task_ids={completed!r}")
            completed_tasks = []
            for task in tasks:
                updated = replace(
                    task,
                    status="completed",
                    updated_at_monotonic=completed_at_monotonic,
                    completed_at_monotonic=completed_at_monotonic,
                    completion=dict(completion),
                )
                completed_tasks.append(
                    self._replace("completed", task, updated, completed_at_monotonic)
                )
            return tuple(completed_tasks)

    def task(self, task_id: str) -> MailboxTask:
        with self._condition:
            return self._require(task_id)

    def status(self) -> dict[str, object]:
        with self._condition:
            pending = [task.as_agent_payload() for task in self._items if task.is_pending]
            completed = [task.as_agent_payload() for task in self._items if not task.is_pending]
            return {
                "document_type": "persistent_scenario_mailbox",
                "revision": self._revision,
                "pending": pending,
                "completed": completed,
                "counts": {"pending": len(pending), "completed": len(completed), "total": len(self._items)},
            }

    def history(self) -> tuple[dict[str, object], ...]:
        with self._condition:
            return tuple(dict(item) for item in self._history)

    def wait_for_pending(self, after_revision: int) -> int:
        if after_revision < 0:
            raise ValueError(f"Mailbox after_revision must be non-negative: after_revision={after_revision}")
        with self._condition:
            while not self._stop.is_set():
                if self._revision > after_revision and any(task.is_pending for task in self._items):
                    return self._revision
                self._condition.wait(0.25)
            return self._revision

    def wake(self) -> None:
        with self._condition:
            self._condition.notify_all()

    def _require(self, task_id: str) -> MailboxTask:
        try:
            return self._items_by_id[task_id]
        except KeyError as exc:
            raise ValueError(f"Unknown mailbox task_id: task_id={task_id!r}") from exc

    def _replace(
        self,
        operation: str,
        previous: MailboxTask,
        updated: MailboxTask,
        at_monotonic: float,
        *,
        details: Mapping[str, object] | None = None,
    ) -> MailboxTask:
        index = previous.sequence - 1
        self._items[index] = updated
        self._items_by_id[updated.task_id] = updated
        self._record_change(operation, updated, at_monotonic, previous=previous, details=details)
        self._condition.notify_all()
        return updated

    def _record_change(
        self,
        operation: str,
        task: MailboxTask,
        at_monotonic: float,
        *,
        previous: MailboxTask | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        self._revision += 1
        change: dict[str, object] = {
            "revision": self._revision,
            "operation": operation,
            "at_monotonic": at_monotonic,
            "task": task.as_agent_payload(),
        }
        if previous is not None:
            change["previous_status"] = previous.status
        if details is not None:
            change["details"] = dict(details)
        self._history.append(change)
        if self._on_change is not None:
            self._on_change(change)
