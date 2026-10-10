"""Deterministic Agents for PersistentScenario gates and protocol tests."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy

from src.scenarios.evaluation.protocol import EMPTY_REPORT

from .persistent_scenario_agent import PersistentScenarioAgent

_MAX_ACTION_RETRY_ATTEMPTS = 10

# A routine inspection that found nothing actionable is still a real report:
# it documents that the inspection ran, not that the agent did nothing.
ROUTINE_CLEAR_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": [],
        "verification": ["routine inspection completed; no actionable anomaly found"],
    },
    "summary": "Routine inspection completed; no actionable anomaly found.",
}


class MockPersistentScenarioAgent(PersistentScenarioAgent):
    """Execute reference database actions and use the mailbox as bookkeeping."""

    def __init__(
        self,
        reference_actions: Sequence[Sequence[Mapping[str, object]]] = (),
        *,
        repair: bool = True,
        periodic_actions: Sequence[Sequence[Mapping[str, object]]] = (),
        reference_reports: Sequence[Mapping[str, object]] = (),
        periodic_reports: Sequence[Mapping[str, object]] = (),
        periodic_plan_thresholds: Sequence[int] = (),
    ):
        super().__init__()
        self.reference_actions = tuple(tuple(actions) for actions in reference_actions)
        self.periodic_actions = tuple(tuple(actions) for actions in periodic_actions)
        # Each periodic plan becomes eligible only from its event's timeline
        # position onward, expressed as the minimum periodic-task ordinal; this
        # keeps repairs from running before their Event has been injected.
        self.periodic_plan_thresholds = tuple(periodic_plan_thresholds)
        self.reference_reports = tuple(dict(report) for report in reference_reports)
        self.periodic_reports = tuple(dict(report) for report in periodic_reports)
        self.repair = repair
        self._handled: set[str] = set()
        self._plan_cache: dict[str, tuple[Mapping[str, object], ...]] = {}
        self._event_action_index = 0
        self._periodic_ordinal = 0
        self._consumed_periodic_plans: set[int] = set()
        self._event_report_index = 0
        self._periodic_report_index = 0
        self._last_periodic_plan_index: int | None = None

    def run_until_stop(self) -> Mapping[str, object]:
        context = self._require_context()
        attempts: dict[str, int] = {}
        while not context.stop_signal.is_set():
            status = context.gateway.mailbox("read")
            tasks = [task for task in status["pending"] if task["task_id"] not in self._handled]
            if not tasks:
                context.gateway.mailbox("wait")
                continue
            reports = []
            completed_ids = []
            deferred = False
            for task in tasks:
                report, failed = self._handle_task(task)
                if failed and attempts.get(task["task_id"], 0) < _MAX_ACTION_RETRY_ATTEMPTS:
                    attempts[task["task_id"]] = attempts.get(task["task_id"], 0) + 1
                    deferred = True
                    continue
                reports.append(report)
                completed_ids.append(task["task_id"])
                self._handled.add(task["task_id"])
            if deferred and not completed_ids:
                # The mailbox protocol forbids waiting while tasks are pending;
                # retry immediately instead of waiting.
                continue
            if not completed_ids:
                context.gateway.mailbox("wait")
                continue
            context.gateway.mailbox(
                "write",
                task_ids=completed_ids,
                report=reports[-1],
            )
        return {
            "status": "horizon_reached",
            "handled_tasks": sorted(self._handled),
        }

    def _handle_task(self, task: Mapping[str, object]) -> tuple[Mapping[str, object], bool]:
        context = self._require_context()
        if task["symptoms"]:
            actions = self._next_symptom_actions(task)
            failed = False
            if self.repair:
                for action in actions:
                    if self._execute_reference_action(action):
                        failed = True
            return self._next_symptom_report(), failed
        return self._handle_routine_task(task)

    def _next_symptom_actions(self, task: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
        cached = self._plan_cache.get(task["task_id"])
        if cached is not None:
            return cached
        if self._event_action_index >= len(self.reference_actions):
            raise ValueError(
                "MockPersistentScenarioAgent received more symptom-bearing work items than reference action plans: "
                f"task_id={task['task_id']!r}, action_plan_count={len(self.reference_actions)}"
            )
        actions = self.reference_actions[self._event_action_index]
        self._event_action_index += 1
        self._plan_cache[task["task_id"]] = actions
        return actions

    def _next_symptom_report(self) -> Mapping[str, object]:
        report_index = self._event_report_index
        self._event_report_index += 1
        if report_index >= len(self.reference_reports):
            return deepcopy(EMPTY_REPORT)
        return self.reference_reports[report_index]

    def _handle_routine_task(self, task: Mapping[str, object]) -> tuple[Mapping[str, object], bool]:
        """One routine task offers every eligible inspection plan, in order.

        A plan is consumed only when all of its reference actions succeed. A
        failing action usually means the fault is not observable yet (its
        injector may still be activating) — the plan stays unconsumed and is
        re-offered on a later routine task. Later plans are still offered in
        the same round so one stuck plan cannot starve the plans behind it.
        Routine tasks always complete: the mailbox protocol has no pending
        work backing up behind a not-yet-applicable plan.
        """
        self._periodic_ordinal += 1
        report: Mapping[str, object] | None = None
        for plan_index in range(len(self.periodic_actions)):
            if plan_index in self._consumed_periodic_plans:
                continue
            threshold = (
                self.periodic_plan_thresholds[plan_index]
                if plan_index < len(self.periodic_plan_thresholds)
                else 1
            )
            if threshold > self._periodic_ordinal:
                continue
            if not self.repair:
                self._consumed_periodic_plans.add(plan_index)
                report = report or self._report_for_periodic_plan(plan_index)
                continue
            failed = False
            for action in self.periodic_actions[plan_index]:
                if self._execute_reference_action(action):
                    failed = True
                    break
            if failed:
                continue
            self._consumed_periodic_plans.add(plan_index)
            report = report or self._report_for_periodic_plan(plan_index)
        if report is None:
            return deepcopy(ROUTINE_CLEAR_REPORT), False
        return report, False

    def _report_for_periodic_plan(self, plan_index: int) -> Mapping[str, object]:
        if plan_index >= len(self.periodic_reports):
            return deepcopy(ROUTINE_CLEAR_REPORT)
        return self.periodic_reports[plan_index]

    def _execute_reference_action(self, action: Mapping[str, object]) -> bool:
        """Execute one reference action; return True when the environment rejected it."""
        if set(action) != {"api", "args"}:
            raise ValueError(f"MockPersistentScenarioAgent reference action has unexpected fields: action={action!r}")
        context = self._require_context()
        result = context.gateway.execute(action["api"], action["args"], thinking="deterministic reference action", source="mock-reference")
        if isinstance(result, Mapping) and result.get("status") == "error":
            return True
        if isinstance(result, str) and '"status": "error"' in result:
            return True
        return False


class ZeroPersistentScenarioAgent(PersistentScenarioAgent):
    def run_until_stop(self) -> Mapping[str, object]:
        context = self._require_context()
        while not context.stop_signal.is_set():
            context.stop_signal.wait(0.25)
        return {"status": "horizon_reached", "handled_tasks": []}


class WrongActionPersistentScenarioAgent(PersistentScenarioAgent):
    """Deterministic negative control with an unsafe remediation action."""

    def __init__(self) -> None:
        super().__init__()
        self._handled: set[str] = set()
        self._acted = False

    def run_until_stop(self) -> Mapping[str, object]:
        context = self._require_context()
        while not context.stop_signal.is_set():
            status = context.gateway.mailbox("read")
            tasks = [task for task in status["pending"] if task["task_id"] not in self._handled]
            if not tasks:
                context.gateway.mailbox("wait")
                continue
            if not self._acted:
                context.gateway.execute(
                    "execute_sql",
                    {
                        "sql_query": (
                            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                            "WHERE application_name LIKE 'checkout_api_wait_%' "
                            "AND pid <> pg_backend_pid();"
                        )
                    },
                    thinking="broad negative-control action",
                    source="wrong-action-gate",
                )
                self._acted = True
            context.gateway.mailbox(
                "write",
                task_ids=[task["task_id"] for task in tasks],
                report=EMPTY_REPORT,
            )
            self._handled.update(task["task_id"] for task in tasks)
        return {"status": "horizon_reached", "handled_tasks": sorted(self._handled)}
