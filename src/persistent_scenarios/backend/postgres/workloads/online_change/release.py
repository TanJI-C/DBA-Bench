"""Instance 5 (online change) release worker.

The release worker emulates a real deployment pipeline: each pass starts at
the release plan's first unfinished task, follows `task:` dependencies, honours
the task's change-calendar `window_start` (scenario seconds over the workload
origin), runs DDL with the task row's `lock_timeout_ms` and a bounded deploy
budget, skips already-applied tasks, and appends every attempt to
`ops.release_log`. A lock or statement timeout ends the pass; the deploy tool
(not the injector) starts the retry pass, which is how the contract's
`release_ddl_retry` occurrence materializes.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass

from ..oltp_core.control import read_release_task
from ..oltp_core.ports import Clock, ConnectionSource, EvidenceLedgerFile

RELEASE_APPLICATION_NAME = "release_worker"
DEPENDENCY_POLL_SECONDS = 2.0

RELEASE_TASK_DONE_SQL = "SELECT status FROM ops.release_tasks WHERE task_id = %(task_id)s;"
RELEASE_DEPENDENT_SQL = (
    "SELECT task_id FROM ops.release_tasks WHERE depends_on = %(depends_on)s;"
)
RELEASE_LOG_SQL = (
    "INSERT INTO ops.release_log (task_id, attempt, statement_kind, outcome, pgcode, detail, logged_at) "
    "VALUES (%(task_id)s, %(attempt)s, %(statement_kind)s, %(outcome)s, %(pgcode)s, %(detail)s, %(logged_at)s);"
)
RELEASE_STATUS_SQL = (
    "UPDATE ops.release_tasks SET status = %(status)s WHERE task_id = %(task_id)s;"
)

_TIMEOUT_PGCODES = frozenset({"55P03", "57014"})
# 23502 (not_null_violation) is the completeness gate's honest terminal
# outcome: applying SET NOT NULL before the backfill settles fails the ALTER
# itself — the order-dependent delivery rejection.
_CHECK_VIOLATION_PGCODES = frozenset({"23502"})


@dataclass(frozen=True, slots=True)
class DdlStepReport:
    task_id: str
    attempt: int
    outcome: str  # "applied" | "already_done" | "lock_timeout" | "statement_timeout" | "check_violation"
    detail: str


@dataclass(frozen=True, slots=True)
class ReleasePlanReport:
    """One deploy-tool pass over the release plan starting at the given task."""

    steps: tuple[DdlStepReport, ...]

    @property
    def final_outcome(self) -> str:
        return self.steps[-1].outcome if self.steps else "no_work"


class ReleaseWorker:
    def __init__(
        self,
        *,
        source: ConnectionSource,
        clock: Clock,
        evidence: EvidenceLedgerFile,
        scenario_origin_monotonic: float,
    ) -> None:
        self._source = source
        self._clock = clock
        self._evidence = evidence
        # Task `window_start` values are scenario seconds; windows translate as
        # origin + window_start (the deploy tool submits the plan against the
        # change calendar, so windows are business-plan facts, not clock magic).
        self._scenario_origin = scenario_origin_monotonic

    def run_release_plan(
        self, *, start_task_id: str, deploy_timeout_seconds: float, stop: threading.Event
    ) -> ReleasePlanReport:
        deadline = self._clock.monotonic() + deploy_timeout_seconds
        steps: list[DdlStepReport] = []
        connection = self._source.connection(RELEASE_APPLICATION_NAME)
        self._evidence.append({
            "kind": "job_planned",
            "job_id": start_task_id,
            "job_kind": "release_plan",
            "deploy_timeout_seconds": deploy_timeout_seconds,
            "at": self._clock.monotonic(),
        })
        try:
            current: str | None = start_task_id
            while current is not None:
                task = read_release_task(connection, current)
                if task.kind != "ddl":
                    raise ValueError(
                        f"Release plan tasks must be ddl tasks: task_id={current!r}, kind={task.kind!r}"
                    )
                if task.status == "done":
                    steps.append(DdlStepReport(current, 0, "already_done", "task already applied"))
                else:
                    steps.append(self._run_task(connection, current, deadline, stop))
                current = self._dependent_task(connection, current)
        except RuntimeError as exc:
            # Deploy-budget exhaustion while waiting on a dependency is a
            # terminal pass outcome (the deploy tool times out and records),
            # not a harness crash: the job ledger must keep the terminal row.
            if "deploy budget expired" not in str(exc) and "Deploy budget expired" not in str(exc):
                raise
            steps.append(DdlStepReport("<dependency_wait>", 0, "statement_timeout", str(exc)))
        finally:
            connection.close()
        report = ReleasePlanReport(steps=tuple(steps))
        self._evidence.append({
            "kind": "job_terminal",
            "job_id": start_task_id,
            "job_kind": "release_plan",
            "status": report.final_outcome,
            "steps": [step.outcome for step in report.steps],
            "at": self._clock.monotonic(),
        })
        return report

    def _dependent_task(self, connection: object, task_id: str) -> str | None:
        with connection.cursor() as cursor:  # type: ignore[attr-defined]
            cursor.execute(RELEASE_DEPENDENT_SQL, {"depends_on": f"task:{task_id}"})
            row = cursor.fetchone()
        connection.commit()  # type: ignore[attr-defined]
        return None if row is None else str(row[0])

    def _run_task(self, connection: object, task_id: str, deadline: float, stop: threading.Event) -> DdlStepReport:
        task = read_release_task(connection, task_id)
        if task.ddl_statement is None or not task.ddl_statement.strip():
            raise ValueError(f"DDL task has no statement: task_id={task_id!r}")
        if task.window_start > 0:
            self._wait_until_window(connection, task.window_start, deadline, stop)
        if task.depends_on is not None:
            self._wait_for_dependency(connection, task.depends_on, deadline, stop)
        with connection.cursor() as cursor:  # type: ignore[attr-defined]
            cursor.execute("SELECT count(*) FROM ops.release_log WHERE task_id = %(task_id)s;", {"task_id": task_id})
            attempt = int(cursor.fetchone()[0]) + 1
        connection.commit()  # type: ignore[attr-defined]
        remaining_ms = int((deadline - self._clock.monotonic()) * 1000)
        if remaining_ms <= 0:
            self._log_attempt(connection, task_id, attempt, "statement_timeout", "57014", "deploy_budget_expired_before_execution")
            return DdlStepReport(task_id, attempt, "statement_timeout", "deploy_budget_expired_before_execution")
        try:
            with connection.cursor() as cursor:  # type: ignore[attr-defined]
                cursor.execute(f"SET LOCAL lock_timeout = {int(task.lock_timeout_ms)};")
                cursor.execute(f"SET LOCAL statement_timeout = {remaining_ms};")
                cursor.execute(task.ddl_statement)
        except Exception as exc:
            outcome, pgcode = self._classify_ddl_error(exc)
            connection.rollback()  # type: ignore[attr-defined]
            self._log_attempt(connection, task_id, attempt, outcome, pgcode, repr(exc))
            return DdlStepReport(task_id, attempt, outcome, repr(exc))
        self._log_attempt(connection, task_id, attempt, "applied", None, task.ddl_statement)
        with connection.cursor() as cursor:  # type: ignore[attr-defined]
            cursor.execute(RELEASE_STATUS_SQL, {"status": "done", "task_id": task_id})
        connection.commit()  # type: ignore[attr-defined]
        return DdlStepReport(task_id, attempt, "applied", task.ddl_statement)

    def _wait_until_window(self, connection: object, window_start: float, deadline: float, stop: threading.Event) -> None:
        # Close the implicit read transaction BEFORE idling: the deploy tool
        # must not hold a transaction open across a long wait, or any
        # idle-in-transaction protection (role GUC or agent-set) aborts its
        # session mid-window and kills the pass.
        connection.commit()  # type: ignore[attr-defined]
        window_monotonic = self._scenario_origin + window_start
        while self._clock.monotonic() < window_monotonic:
            if self._clock.monotonic() >= deadline:
                raise RuntimeError(
                    "Release deploy budget expired before the release window opened: "
                    f"window_start={window_start}, deadline={deadline}"
                )
            if not self._clock.wait_until(min(window_monotonic, self._clock.monotonic() + DEPENDENCY_POLL_SECONDS), stop):
                raise RuntimeError("ReleaseWorker stopped while waiting for its release window")
        connection.commit()  # type: ignore[attr-defined]

    def _wait_for_dependency(self, connection: object, depends_on: str, deadline: float, stop: threading.Event) -> None:
        if not depends_on.startswith("task:"):
            raise ValueError(
                f"DDL task dependency must reference a task: depends_on={depends_on!r}"
            )
        dependency_task_id = depends_on.removeprefix("task:")
        while True:
            with connection.cursor() as cursor:  # type: ignore[attr-defined]
                cursor.execute(RELEASE_TASK_DONE_SQL, {"task_id": dependency_task_id})
                row = cursor.fetchone()
            if row is None:
                raise ValueError(
                    f"DDL dependency references an unknown task: depends_on={depends_on!r}"
                )
            if str(row[0]) == "done":
                connection.commit()  # type: ignore[attr-defined]
                return
            if self._clock.monotonic() >= deadline:
                raise RuntimeError(
                    "Release deploy budget expired while waiting for its dependency: "
                    f"task_id={dependency_task_id!r}, deadline={deadline}"
                )
            if not self._clock.wait_until(self._clock.monotonic() + DEPENDENCY_POLL_SECONDS, stop):
                raise RuntimeError("ReleaseWorker stopped while waiting for its dependency")
            connection.commit()  # type: ignore[attr-defined]

    @staticmethod
    def _classify_ddl_error(exc: Exception) -> tuple[str, str | None]:
        pgcode = getattr(exc, "pgcode", None)
        if pgcode in _TIMEOUT_PGCODES:
            return ("lock_timeout" if pgcode == "55P03" else "statement_timeout"), pgcode
        if pgcode in _CHECK_VIOLATION_PGCODES:
            return "check_violation", pgcode
        raise RuntimeError(
            f"Release DDL failed with an unexpected database error: pgcode={pgcode!r}, error={exc!r}"
        ) from exc

    def _log_attempt(
        self,
        connection: object,
        task_id: str,
        attempt: int,
        outcome: str,
        pgcode: str | None,
        detail: str,
    ) -> None:
        with connection.cursor() as cursor:  # type: ignore[attr-defined]
            cursor.execute(RELEASE_LOG_SQL, {
                "task_id": task_id,
                "attempt": attempt,
                "statement_kind": "ddl",
                "outcome": outcome,
                "pgcode": pgcode,
                "detail": detail[:500],
                "logged_at": self._clock.monotonic(),
            })
        connection.commit()  # type: ignore[attr-defined]
