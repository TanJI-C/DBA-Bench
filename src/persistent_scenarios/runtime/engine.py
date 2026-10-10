"""System-neutral Persistent Scenario engine with one persistent mailbox session.

Arrival and result are separated: the monotonic scheduler only advances
arrivals, and every activation produces structured arrival facts
(applied / attempted+prevented). Capability exceptions are infrastructure
failures and invalidate the run; they are never masked as prevention.
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
import hashlib
import os
import threading
import time
import traceback
from collections.abc import Mapping

from src.agents.persistent_scenario_agent import PersistentScenarioAgentContext
from src.persistent_scenarios.backend.contracts import EventActivationContext
from src.persistent_scenarios.runtime.lifecycle import (
    ArrivalFacts,
    EventArrivalStatus,
    EventAttemptEvidence,
    AppliedEvidence,
    FailureClassification,
    InputVersions,
    PreventionEvidence,
    RunValidityFact,
    ScoringWindow,
)
from src.persistent_scenarios.runtime.ports import (
    PersistentScenarioAgentProtocolError,
    PersistentScenarioAgentProviderError,
    PersistentScenarioEnvironmentInvalidError,
    PersistentScenarioEvaluationProvider,
    PersistentScenarioProviderError,
)
from src.persistent_scenarios.model.calibration import require_validated_calibration
from src.persistent_scenarios.model.spec import EventSpec, EventTrigger, PersistentScenarioSpec, compress_persistent_scenario_timeline
from src.persistent_scenarios.runtime.state import EventRun, PersistentScenarioRun

from .admission import admit_persistent_scenario
from .activation import ActivationLedger
from .checkpoints import CheckpointCoordinator
from .cleanup import cleanup_activated_events
from .clock import Clock
from .finalization import seal_pre_cleanup_evaluation
from .mailbox import MailboxTask, PersistentScenarioMailbox
from .scheduler import TimelineScheduler
from .sequence_gate import build_gate_result
from .sessions import PersistentScenarioAgentControl, PersistentScenarioAgentGateway

_RUN_MODES = frozenset({"formal", "development", "development_compressed", "calibration_failure_probe"})
_PREFIX_GATE_NAMES = frozenset({"resolved-prefix", "unresolved-prefix", "prevented-prefix"})

_EVALUATION_PASS_FIELDS = (
    "BaselinePass",
    "DiagnosisPass",
    "OutcomePass",
    "SafePass",
)


def _caused_by(error: BaseException, error_type: type[BaseException]) -> bool:
    current: BaseException | None = error
    visited: set[int] = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        if isinstance(current, error_type):
            return True
        current = current.__cause__
    return False


def _classify_provider_error(error: BaseException, default: FailureClassification) -> FailureClassification:
    if _caused_by(error, PersistentScenarioEnvironmentInvalidError):
        return FailureClassification.INVALID_ENVIRONMENT
    if _caused_by(error, PersistentScenarioProviderError):
        return FailureClassification.INFRASTRUCTURE_FAILURE
    return default


_FAILURE_PRIORITY = {
    FailureClassification.AGENT_FAILURE: 10,
    FailureClassification.AGENT_PROVIDER_FAILURE: 20,
    FailureClassification.INFRASTRUCTURE_FAILURE: 30,
    FailureClassification.TOOL_OR_TRACE_FAILURE: 40,
    FailureClassification.INVALID_ENVIRONMENT: 50,
}


def _prefer_failure(current: FailureClassification | None, candidate: FailureClassification) -> FailureClassification:
    if current is None or _FAILURE_PRIORITY[candidate] > _FAILURE_PRIORITY[current]:
        return candidate
    return current


class PersistentScenarioEngine:
    def __init__(
        self,
        spec: PersistentScenarioSpec,
        backend,
        agent_factory,
        *,
        evaluation_provider: PersistentScenarioEvaluationProvider,
        run_id: str,
        port: int,
        clock: Clock,
        output_dir: str | None = None,
        run_mode: str = "development",
        time_scale: float = 1.0,
        event_activation: bool = True,
        evaluation_mode: str = "persistent_scenario",
        gate_name: str | None = None,
        trusted_checkpoint_observer=None,
    ):
        if run_mode not in _RUN_MODES:
            raise ValueError(f"Unsupported Persistent Scenario run_mode: run_mode={run_mode!r}, allowed={sorted(_RUN_MODES)!r}")
        if isinstance(time_scale, bool) or not isinstance(time_scale, (int, float)) or time_scale <= 0:
            raise ValueError(f"Persistent Scenario time_scale must be positive: time_scale={time_scale!r}")
        if run_mode == "development_compressed" and time_scale <= 1:
            raise ValueError(
                "development_compressed Persistent Scenario runs require time_scale > 1: "
                f"scenario_id={spec.scenario_id!r}, time_scale={time_scale!r}"
            )
        if run_mode != "development_compressed" and float(time_scale) != 1.0:
            raise ValueError(
                "Only development_compressed Persistent Scenario runs may use time_scale != 1: "
                f"scenario_id={spec.scenario_id!r}, run_mode={run_mode!r}, time_scale={time_scale!r}"
            )
        if spec.system.value != backend.system.value:
            raise ValueError(
                "Persistent Scenario/backend system mismatch: "
                f"scenario_id={spec.scenario_id!r}, scenario_system={spec.system.value!r}, backend_system={backend.system.value!r}"
            )
        if evaluation_mode not in {"persistent_scenario", "baseline"}:
            raise ValueError(f"Unsupported Persistent Scenario evaluation_mode: evaluation_mode={evaluation_mode!r}")
        if not event_activation and evaluation_mode != "baseline":
            raise ValueError("Persistent Scenario event_activation=False requires evaluation_mode='baseline'")

        self.source_spec = spec
        self.spec = compress_persistent_scenario_timeline(spec, float(time_scale)) if run_mode == "development_compressed" else spec
        self.backend = backend
        if not callable(agent_factory):
            raise TypeError(f"Persistent Scenario engine requires an agent_factory callable: value={agent_factory!r}")
        self.agent_factory = agent_factory
        self.evaluation_provider = evaluation_provider
        self.run_id = run_id
        self.port = port
        self.clock = clock
        self.output_dir = output_dir
        self.run_mode = run_mode
        self.time_scale = float(time_scale)
        self.event_activation = event_activation
        self.evaluation_mode = evaluation_mode
        self.gate_name = gate_name
        self.trusted_checkpoint_observer = trusted_checkpoint_observer
        self.formal_eligible = run_mode == "formal"
        self.calibration_evidence_hash: str | None = None
        if run_mode == "formal":
            self.calibration_evidence_hash = require_validated_calibration(self.source_spec)
        self.stop_signal = threading.Event()
        self._activation_executor = ThreadPoolExecutor(thread_name_prefix="persistent_scenario-event-activation")
        self._session_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="persistent_scenario-agent-session")
        self._scheduler_impl = TimelineScheduler(clock=self.clock, activation_executor=self._activation_executor)
        self._activation_lock = threading.Lock()
        self._activation_ledger = ActivationLedger()
        # While an event activation is in flight its fault is only partially
        # applied: an agent repair landing before the arrival facts snapshot
        # would be judged against state that does not exist yet. Agent-surface
        # SQL waits on this gate; trusted injector/evaluator SQL bypasses it.
        self._activation_gate = threading.Event()
        self._activation_gate_count = 0
        self._activation_gate_lock = threading.Lock()
        # Alert mailbox order must match spec event order even though event
        # activation itself runs concurrently: reference/mock agents pair their
        # prebuilt action plans with alert tasks by arrival order.
        self._alert_order_condition = threading.Condition()
        self._next_alert_publish_index = 0
        self._errors: list[tuple[str, Exception]] = []
        self._session_futures: list[tuple[str, Future]] = []
        self._session_lock = threading.Lock()
        self._agent = None
        self._scheduler_thread: threading.Thread | None = None
        self._agent_error: Exception | None = None
        self._agent_error_classification: FailureClassification | None = None
        self._persistent_scenario_error: Exception | None = None
        self._persistent_scenario_error_classification: FailureClassification | None = None
        self._scheduler_error: Exception | None = None
        self._scheduler_error_classification: FailureClassification | None = None
        self._runtime_error: Exception | None = None
        self._runtime_error_classification: FailureClassification | None = None
        self.persistent_scenario_run: PersistentScenarioRun | None = None
        self.mailbox: PersistentScenarioMailbox | None = None
        self.control: PersistentScenarioAgentControl | None = None
        self.coordinator: CheckpointCoordinator | None = None
        self.workload = None
        self.telemetry = None
        self._environment_created = False
        self._environment_deployed = False
        self._workload_created = False
        self._workload_stopped = False
        self._workload_started = False
        self._telemetry_created = False
        self._telemetry_started = False
        self._telemetry_stopped = False
        self._safety_baseline = None
        self._baseline_safety: Mapping[str, object] | None = None
        self._ledgers_sealed = False

    def _require_run(self) -> PersistentScenarioRun:
        if self.persistent_scenario_run is None:
            raise RuntimeError("Persistent Scenario engine requires an initialized PersistentScenarioRun")
        return self.persistent_scenario_run

    def _on_mailbox_change(self, change: Mapping[str, object]) -> None:
        run = self._require_run()
        run.mailbox_history.append(dict(change))
        run.mailbox_state = dict(self.mailbox.status())
        run.append_timeline(
            owner="scheduler",
            kind="mailbox_document_changed",
            payload={
                "revision": change["revision"],
                "operation": change["operation"],
                "task_id": change["task"]["task_id"],
                "status": change["task"]["status"],
            },
        )

    def _start_agent(self) -> str:
        if self.control is None:
            raise RuntimeError("Persistent Scenario mailbox Agent started before control initialization")
        if self.mailbox is None:
            raise RuntimeError("Persistent Scenario mailbox Agent started before mailbox initialization")
        with self._session_lock:
            if self._session_futures:
                raise RuntimeError(f"Persistent Scenario mailbox Agent already started: run_id={self.run_id!r}")
        session_id = "session-0001"
        gateway = PersistentScenarioAgentGateway(self._require_run().env, self.control, session_id)
        context = PersistentScenarioAgentContext(
            scenario_id=self.spec.scenario_id,
            session_id=session_id,
            gateway=gateway,
            stop_signal=self.stop_signal,
        )
        record = {
            "session_id": session_id,
            "kind": "mailbox",
            "started_at_monotonic": self.clock.monotonic(),
            "ended_at_monotonic": None,
            "status": "running",
            "state": "active",
            "error": None,
            "result": None,
        }
        self.control.register_session(session_id)
        with self._session_lock:
            self._require_run().agent_sessions.append(record)
        self._require_run().append_agent_conversation(
            [],
            [{"phase_index": 0, "messages": [], "compaction": None, "session_id": session_id}],
        )
        self._require_run().append_timeline(
            owner="engine",
            kind="agent_session_started",
            payload={"session_id": session_id, "kind": "mailbox", "state": "active"},
        )
        future = self._session_executor.submit(self._run_session, context, record)
        with self._session_lock:
            self._session_futures.append((session_id, future))
        return session_id

    def _run_session(self, context: PersistentScenarioAgentContext, record: dict[str, object]) -> None:
        try:
            agent = self.agent_factory(context)
            if agent is None:
                raise RuntimeError(f"Persistent Scenario agent_factory returned None: session_id={context.session_id!r}")
            self._agent = agent
            agent.start(context)
            result = agent.run_until_stop()
            record["result"] = dict(result)
            record["status"] = "completed"
        except Exception as exc:
            record["status"] = "failed"
            record["error"] = repr(exc)
            self._agent_error = exc
            if _caused_by(exc, PersistentScenarioEnvironmentInvalidError):
                self._agent_error_classification = FailureClassification.INVALID_ENVIRONMENT
            elif _caused_by(exc, PersistentScenarioProviderError):
                self._agent_error_classification = _classify_provider_error(exc, FailureClassification.INFRASTRUCTURE_FAILURE)
            elif _caused_by(exc, PersistentScenarioAgentProviderError):
                self._agent_error_classification = FailureClassification.AGENT_PROVIDER_FAILURE
            elif _caused_by(exc, PersistentScenarioAgentProtocolError):
                self._agent_error_classification = FailureClassification.AGENT_FAILURE
            else:
                self._agent_error_classification = FailureClassification.AGENT_FAILURE
            self._require_run().early_stop_reason = "agent_session_terminal_failure"
            self._errors.append((f"agent:{context.session_id}", exc))
            self.stop_signal.set()
        finally:
            record["ended_at_monotonic"] = self.clock.monotonic()
            self._require_run().append_timeline(
                owner="engine",
                kind="agent_session_finished",
                payload={"session_id": context.session_id, "status": record["status"], "error": record["error"]},
            )

    def _publish_periodic_task(self) -> MailboxTask:
        if self.mailbox is None:
            raise RuntimeError("Persistent Scenario periodic task published before mailbox initialization")

        def prepare(task: MailboxTask) -> None:
            self._require_run().append_timeline(
                owner="scheduler",
                kind="periodic_task_published",
                payload={"task_id": task.task_id, "published_at_monotonic": task.created_at_monotonic},
            )

        return self.mailbox.publish(
            task_type="periodic_inspection",
            created_at_monotonic=self.clock.monotonic(),
            title="Routine database health inspection",
            description="Inspect the live database and record any actionable anomaly found by ordinary operations tools.",
            on_published=prepare,
        )

    def _on_runtime_error(self, source: str, error: Exception) -> None:
        classification = _classify_provider_error(error, FailureClassification.INFRASTRUCTURE_FAILURE)
        self._runtime_error = error
        self._runtime_error_classification = _prefer_failure(self._runtime_error_classification, classification)
        self.stop_signal.set()

    def export_agent_llm_usage(self) -> list[dict[str, object]]:
        """Per-LLM-call token usage from the run's agent, for cost accounting."""
        agent = self._agent
        if agent is not None and hasattr(agent, "llm_usage_events"):
            return agent.llm_usage_events()
        return []

    # ------------------------------------------------------------------
    # Event arrival
    # ------------------------------------------------------------------

    def _activate_event(self, event: EventSpec) -> EventRun:
        with self._activation_gate_lock:
            self._activation_gate_count += 1
            self._activation_gate.clear()
        try:
            return self._activate_event_inner(event)
        finally:
            with self._activation_gate_lock:
                self._activation_gate_count -= 1
                if self._activation_gate_count == 0:
                    self._activation_gate.set()

    def _prefix_event_statuses(self, exclude: EventRun) -> dict[str, str]:
        run = self._require_run()
        statuses = {}
        for existing in run.events:
            if existing is exclude:
                continue
            if self._prefix_impact_resolved(existing):
                statuses[existing.event_id] = "resolved"
                continue
            statuses[existing.event_id] = (
                existing.arrival.status.value if existing.arrival is not None else "planned"
            )
        return statuses

    def _prefix_impact_resolved(self, event_run: EventRun) -> bool:
        """A prefix event counts as resolved once its injected impact no longer
        exists in the environment (the agent repaired it). Arrival facts alone
        cannot express this: an applied arrival stays applied forever.

        The live-impact probe applies only to the prefix event (the first
        timeline event) of a prefix gate run: cohorts of other events are
        production traffic that legitimately persists until cleanup, and a
        mid-run ``assert_clean`` on them would misclassify the run."""
        if self.gate_name not in _PREFIX_GATE_NAMES:
            return False
        prefix_event = self.spec.events[0] if self.spec.events else None
        if prefix_event is None or event_run.event_id != prefix_event.event_id:
            return False
        if (
            event_run.arrival is None
            or event_run.arrival.status is not EventArrivalStatus.APPLIED
            or event_run.provider_handle is None
        ):
            return False
        facts = self.backend.events.assert_clean(event_run.provider_handle)
        return facts.get("clean") is True

    def _activate_event_inner(self, event: EventSpec) -> EventRun:
        run = self._require_run()
        event_run = EventRun(
            event_id=event.event_id,
            capability_id=event.capability_id,
            occurrence=event.occurrence,
            entity=event.entity,
            planned_start_monotonic=float(run.started_monotonic) + event.start_seconds,
        )
        with self._activation_lock:
            run.events.append(event_run)
        run.append_timeline(
            owner="scheduler",
            kind="event_activation_started",
            event_id=event.event_id,
            payload={
                "capability_id": event.capability_id,
                "occurrence": event.occurrence,
                "entity": event.entity,
                "prefix_event_statuses": self._prefix_event_statuses(event_run),
            },
        )
        arrival_started = self.clock.monotonic()
        context = EventActivationContext(
            run_id=self.run_id,
            spec=self.spec,
            event=event,
            environment=run.env,
            clock=self.clock,
        )
        try:
            capability = self.backend.events.capability(event.capability_id)
            result = capability.activate(context)
            elapsed = self.clock.monotonic() - arrival_started
            if elapsed > event.activation_timeout_seconds:
                raise PersistentScenarioProviderError(
                    "Persistent Scenario event activation exceeded its timeout: "
                    f"scenario_id={self.spec.scenario_id!r}, event_id={event.event_id!r}, "
                    f"elapsed_seconds={elapsed!r}, activation_timeout_seconds={event.activation_timeout_seconds!r}"
                )
            if result.applied is not None:
                arrival = ArrivalFacts(
                    status=EventArrivalStatus.APPLIED,
                    attempt=result.attempt,
                    applied=result.applied,
                    prevented=None,
                    arrived_at_monotonic=self.clock.monotonic(),
                )
            else:
                arrival = ArrivalFacts(
                    status=EventArrivalStatus.PREVENTED,
                    attempt=result.attempt,
                    applied=None,
                    prevented=result.prevented,
                    arrived_at_monotonic=self.clock.monotonic(),
                )
            event_run.arrival = arrival
            event_run.provider_handle = result.handle
            with self._activation_lock:
                self._activation_ledger.record(event_run, result.handle)
            self.coordinator.on_arrival(event, event_run)
            self._await_alert_publish_turn(event)
            if event.trigger is EventTrigger.ALERT:
                alert = self.backend.events.agent_alert(result.handle)

                def prepare_alert(task: MailboxTask) -> None:
                    event_run.alert_task_id = task.task_id
                    run.alert_truth_map[task.task_id] = event.event_id
                    run.append_timeline(
                        owner="scheduler",
                        kind="alert_published",
                        event_id=event.event_id,
                        payload={"alert_id": task.task_id, "published_at_monotonic": task.created_at_monotonic},
                    )

                self.mailbox.publish(
                    task_type="incident",
                    created_at_monotonic=self.clock.monotonic(),
                    title=alert.title,
                    description=alert.title,
                    symptoms=tuple(alert.symptoms),
                    severity=alert.severity,
                    category=alert.category,
                    on_published=prepare_alert,
                )
            else:
                run.append_timeline(
                    owner="scheduler",
                    kind="silent_event_arrived",
                    event_id=event.event_id,
                    payload={"arrival_status": arrival.status.value},
                )
            run.append_timeline(
                owner="scheduler",
                kind="event_arrival_recorded",
                event_id=event.event_id,
                payload={
                    "arrival_status": arrival.status.value,
                    "prefix_event_statuses": self._prefix_event_statuses(event_run),
                    "response_deadline_seconds": event.response_deadline_seconds,
                },
            )
            return event_run
        except Exception as exc:
            import traceback
            traceback.print_exc()
            run.append_timeline(owner="scheduler", kind="event_arrival_failed", event_id=event.event_id, payload={"error": repr(exc)})
            event_run.arrival = ArrivalFacts(
                status=EventArrivalStatus.FAILED,
                attempt=EventAttemptEvidence(
                    attempted_at_monotonic=arrival_started,
                    detail={"error": repr(exc)},
                ),
                applied=None,
                prevented=None,
                arrived_at_monotonic=self.clock.monotonic(),
            )
            raise
        finally:
            self._finish_alert_publish_turn(event)

    def _event_alert_index(self, event: EventSpec) -> int:
        for index, candidate in enumerate(self.spec.events):
            if candidate.event_id == event.event_id:
                return index
        raise RuntimeError(
            "Persistent Scenario event is not part of the timeline: "
            f"scenario_id={self.spec.scenario_id!r}, event_id={event.event_id!r}"
        )

    def _await_alert_publish_turn(self, event: EventSpec) -> None:
        index = self._event_alert_index(event)
        with self._alert_order_condition:
            while self._next_alert_publish_index < index and not self.stop_signal.is_set():
                self._alert_order_condition.wait(timeout=0.5)

    def _finish_alert_publish_turn(self, event: EventSpec) -> None:
        index = self._event_alert_index(event)
        with self._alert_order_condition:
            if self._next_alert_publish_index <= index:
                self._next_alert_publish_index = index + 1
                self._alert_order_condition.notify_all()

    def _run_scheduler(self) -> None:
        try:
            self._scheduler_impl.run(
                float(self._require_run().started_monotonic),
                self.spec.events,
                self._activate_event,
                self._publish_periodic_task,
                self.spec.inspection_interval_seconds,
                self.spec.inspection_interval_seconds,
                self.stop_signal,
            )
        except Exception as exc:
            classification = _classify_provider_error(exc, FailureClassification.INFRASTRUCTURE_FAILURE)
            self._scheduler_error = exc
            self._scheduler_error_classification = _prefer_failure(self._scheduler_error_classification, classification)
            self._errors.append(("event_scheduler", exc))
            self.stop_signal.set()

    # ------------------------------------------------------------------
    # Horizon, stop, evaluation, cleanup
    # ------------------------------------------------------------------

    def _wait_horizon(self) -> None:
        run = self._require_run()
        if not self.clock.wait_until(float(run.started_monotonic) + self.spec.horizon_seconds, self.stop_signal) and not self._errors:
            raise RuntimeError("Persistent Scenario stopped before horizon without a classified error")

    def _join_thread(self, thread: threading.Thread | None, name: str) -> None:
        if thread is None:
            return
        thread.join(timeout=10)
        if thread.is_alive():
            raise RuntimeError(f"Persistent Scenario {name} thread did not stop: thread={thread.name!r}")

    def _join_sessions(self) -> None:
        with self._session_lock:
            sessions = tuple(self._session_futures)
        for session_id, future in sessions:
            try:
                future.result()
            except Exception as exc:
                if self._agent_error is None:
                    self._agent_error = exc
                raise RuntimeError(f"Persistent Scenario Agent session did not finish: session_id={session_id!r}, error={exc!r}") from exc

    def _seal_ledgers(self) -> None:
        if self._ledgers_sealed:
            return
        run = self._require_run()
        for ledger_id, ledger in run.ledgers.items():
            ledger.finalize_outstanding(self.clock.monotonic())
            ledger.seal()
            ledger.verify()
        self._ledgers_sealed = True

    def _stop_telemetry(self) -> None:
        if not self._telemetry_created or self._telemetry_stopped:
            return
        self._telemetry_stopped = True
        run = self._require_run()
        try:
            if self._telemetry_started:
                run.trusted_telemetry[:] = list(self.telemetry.stop())
            run.cleanup.append({"owner": "telemetry", "status": "stopped"})
        except Exception as exc:
            item = {"owner": "telemetry", "status": "failed", "error": repr(exc)}
            run.cleanup.append(item)
            raise RuntimeError(f"Persistent Scenario telemetry shutdown failed: error={exc!r}") from exc

    def _stop_before_evaluation(self) -> None:
        if not self._workload_created and not self._telemetry_created and self._scheduler_thread is None and not self._session_futures:
            return
        self.stop_signal.set()
        if self.mailbox is not None:
            self.mailbox.wake()
        shutdown_error: Exception | None = None
        if self.workload is not None and self._workload_created:
            # The workload stop finalizes its own open identities (failed plans
            # reach exactly one terminal via the driver's retry finalization).
            # It must run BEFORE the ledger seal: sealing closes every still-open
            # record, so a post-seal workload terminal would collide with the
            # already-closed ledger record and raise "terminal decided twice".
            try:
                self.workload.stop()
                self._workload_stopped = True
                self._require_run().cleanup.append({"owner": "workload", "status": "stopped"})
            except Exception as exc:
                shutdown_error = exc
                self._errors.append(("persistent_scenario_shutdown", exc))
        run = self._require_run()
        try:
            self._seal_ledgers()
        except Exception as exc:
            shutdown_error = shutdown_error or exc
            self._errors.append(("ledger_seal", exc))
        self._join_thread(self._scheduler_thread, "scheduler")
        self._join_sessions()
        try:
            self._stop_telemetry()
        except Exception as exc:
            self._errors.append(("persistent_scenario_shutdown", exc))
            raise
        if shutdown_error is not None:
            raise RuntimeError(
                f"Persistent Scenario workload shutdown failed before final evaluation: error={shutdown_error!r}"
            ) from shutdown_error

    def _final_evaluate(self) -> dict[str, object]:
        run = self._require_run()
        self.coordinator.on_horizon_final()
        # Final trusted sampling: backend executes the instance verifiers and
        # returns typed facts; evaluation consumes them from the run.
        scoring_start_epoch = (
            time.time() - (self.clock.monotonic() - run.business_window.scoring_start_monotonic)
            if run.business_window is not None
            else None
        )
        run.integrity_facts.extend(self.backend.state_facts.capture_integrity_facts(
            run.env, self.spec, scoring_start_epoch=scoring_start_epoch
        ))
        run.required_state_evidence.extend(self.backend.state_facts.capture_required_state_evidence(
            run.env, self.spec, scoring_start_epoch=scoring_start_epoch
        ))
        if self.evaluation_mode == "baseline":
            result = dict(self.evaluation_provider.evaluate_baseline(run, dict(self._baseline_safety or {})))
        else:
            result = dict(self.evaluation_provider.evaluate(run))
        return seal_pre_cleanup_evaluation(run, result)

    def _failure_certificate(self, classification: FailureClassification, reason: str) -> dict[str, object]:
        run = self._require_run()
        return {
            "classification": classification.value,
            "reason_code": classification.value,
            "reason": reason,
            "occurred_at_monotonic": self.clock.monotonic(),
            "last_successful_timeline_sequence": len(run.canonical_timeline),
            "last_agent_action": run.action_history[-1] if run.action_history else None,
            "trusted_environment_state": {"created": self._environment_created, "deployed": self._environment_deployed},
            "workload_state": {
                "started": self._workload_started,
                "ledger_planned_counts": {
                    ledger_id: {
                        "transactions": ledger.event_count("planned_transaction"),
                        "jobs": ledger.event_count("planned_job"),
                    }
                    for ledger_id, ledger in run.ledgers.items()
                },
            },
            "unmet_invariants": [reason],
            "trace_artifacts": {"output_dir": self.output_dir},
            "formal_eligible": self.formal_eligible,
            "early_stop_reason": run.early_stop_reason,
        }

    def _invalid(self, classification: FailureClassification, reason: str) -> dict[str, object]:
        run = self._require_run()
        run.failure_classification = classification
        run.failure_certificate = self._failure_certificate(classification, reason)
        result = dict(self.evaluation_provider.invalid_run(run, classification, reason))
        result["failure_certificate"] = run.failure_certificate
        run.evaluation = result
        return result

    @staticmethod
    def _invalidate_result(
        result: Mapping[str, object],
        classification: FailureClassification,
        reason: str,
    ) -> dict[str, object]:
        invalid = dict(result)
        invalid.update(
            {
                "valid": False,
                "failure_classification": classification.value,
                "FailureClassification": classification.value,
                "model_failure": False,
                "failure": reason,
            }
        )
        for field in _EVALUATION_PASS_FIELDS:
            invalid[field] = None
        return invalid

    def _cleanup(self) -> list[dict[str, object]]:
        run = self._require_run()
        cleanup_errors = cleanup_activated_events(
            run,
            self._activation_ledger.order,
            self._activation_ledger.handles,
            self.backend.events,
        )
        if self.workload is not None and self._workload_created and not self._workload_stopped:
            try:
                self.workload.stop()
                run.cleanup.append({"owner": "workload", "status": "stopped"})
            except Exception as exc:
                item = {"owner": "workload", "status": "failed", "error": repr(exc)}
                cleanup_errors.append(item)
                run.cleanup.append(item)
        if self._environment_created:
            try:
                self.backend.environment.teardown(run.env)
                run.cleanup.append({"owner": "environment", "status": "torn_down"})
            except Exception as exc:
                item = {"owner": "environment", "status": "failed", "error": repr(exc)}
                cleanup_errors.append(item)
                run.cleanup.append(item)
        return cleanup_errors

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def _build_input_versions(self, spec: PersistentScenarioSpec) -> InputVersions:
        from .encoding import jsonable
        from .lifecycle import EVALUATION_SCHEMA, TRACE_SCHEMA
        from src.trace_serialization import strict_json_dumps

        spec_json = strict_json_dumps(jsonable(spec), sort_keys=True)
        return InputVersions(
            spec_digest=hashlib.sha256(spec_json.encode("utf-8")).hexdigest(),
            protocol_version=spec.protocol_version,
            trace_schema=TRACE_SCHEMA,
            evaluation_schema=EVALUATION_SCHEMA,
            resource_lease_id=self.run_id,
            calibration_evidence_id=spec.calibration.evidence_id,
            code_version=os.environ.get("AIOPS_CODE_VERSION", "unversioned"),
        )

    def run_persistent_scenario(self) -> dict[str, object]:
        if self.persistent_scenario_run is not None:
            raise RuntimeError(f"Persistent Scenario engine cannot run twice: run_id={self.run_id!r}")
        self.persistent_scenario_run = PersistentScenarioRun(
            self.run_id,
            self.spec,
            None,
            source_spec=self.source_spec,
            timeline_clock=self.clock.monotonic,
            started_monotonic=self.clock.monotonic(),
            started_wall=time.time(),
            run_mode=self.run_mode,
            time_scale=self.time_scale,
            formal_eligible=self.formal_eligible,
            calibration_evidence_hash=self.calibration_evidence_hash,
            evaluation_mode=self.evaluation_mode,
        )
        self.persistent_scenario_run.input_versions = self._build_input_versions(self.spec)
        result: dict[str, object] | None = None
        runtime_ready = False
        try:
            admit_persistent_scenario(self.spec, self.backend, self.backend.events)
            environment = self.backend.environment.create(self.spec, self.run_id, self.port, time_scale=self.time_scale)
            self._environment_created = True
            self.persistent_scenario_run.env = environment
            self.backend.environment.deploy(environment)
            self._environment_deployed = True
            # Deployment is setup work. The scenario timeline starts only after
            # the persistent database is ready, so deployment latency cannot
            # expire warmup or business deadlines. All boundaries are measured
            # from the scoring start (t=0).
            scoring_started = self.clock.monotonic()
            self.persistent_scenario_run.started_monotonic = scoring_started
            self.persistent_scenario_run.started_wall = time.time()
            self.workload = self.backend.workload.create_runtime(
                environment, self.spec, self.run_id, self.clock, persistent_scenario_started=scoring_started
            )
            self._workload_created = True
            self.telemetry = self.backend.telemetry.create_runtime(
                environment, self.spec, self.run_id, self.clock, persistent_scenario_started=scoring_started
            )
            self._telemetry_created = True
            self.workload.start()
            self._workload_started = True
            self.telemetry.start()
            self._telemetry_started = True
            scoring_started = self.workload.wait_for_warmup()
            self.persistent_scenario_run.started_monotonic = scoring_started
            self.persistent_scenario_run.business_window = ScoringWindow(
                scoring_start_monotonic=scoring_started,
                scoring_end_monotonic=scoring_started + self.spec.horizon_seconds,
                input_stop_monotonic=scoring_started + self.spec.input_stop_seconds,
            )
            baseline = self.backend.safety.capture_baseline(environment, self.spec)
            self._safety_baseline = baseline
            self.mailbox = PersistentScenarioMailbox(self.stop_signal, on_change=self._on_mailbox_change)
            self.persistent_scenario_run.mailbox_state = self.mailbox.status()
            self.control = PersistentScenarioAgentControl(
                self.persistent_scenario_run,
                environment,
                self.mailbox,
                clock=self.clock,
                activation_gate=self._activation_gate,
                action_classifier=self.backend.action_classifier,
            )
            self.coordinator = CheckpointCoordinator(
                self.persistent_scenario_run,
                clock=self.clock,
                safety_provider=self.backend.safety,
                safety_baseline=baseline,
                ledger_positions=lambda: {
                    f"{ledger_id}:{kind}": ledger.event_count(kind)
                    for ledger_id, ledger in self.persistent_scenario_run.ledgers.items()
                    for kind in ("planned_transaction", "transaction_attempt", "transaction_terminal", "planned_job", "job_attempt", "job_terminal", "freshness_sample")
                },
                telemetry_index_count=lambda: len(self.persistent_scenario_run.trusted_telemetry),
                on_error=self._on_runtime_error,
                on_checkpoint=self.trusted_checkpoint_observer,
            )
            run = self._require_run()
            run.ledgers = dict(self.workload.ledgers())
            warmup_safety = self.coordinator.capture_baseline_safety()
            self._baseline_safety = warmup_safety
            self.coordinator.on_warmup_baseline()
            run.append_timeline(
                owner="workload",
                kind="scoring_phase_started",
                # Baseline capture between the warmup barrier and this append
                # already recorded later timeline instants; the business
                # scoring start stays in the payload while the ordering key
                # is the append time, keeping the canonical timeline
                # monotonic.
                payload={
                    "scoring_started_monotonic": scoring_started,
                    "input_stop_seconds": self.spec.input_stop_seconds,
                    "agent_stop_seconds": self.spec.agent_stop_seconds,
                    "horizon_seconds": self.spec.horizon_seconds,
                },
            )
            if self.event_activation:
                self._start_agent()
                self._scheduler_thread = threading.Thread(target=self._run_scheduler, name="persistent_scenario-scheduler", daemon=True)
                self._scheduler_thread.start()
            runtime_ready = True
            self._wait_horizon()
        except Exception as exc:
            self._errors.append(("persistent_scenario", exc))
            self._persistent_scenario_error = exc
            self._persistent_scenario_error_classification = _classify_provider_error(
                exc,
                FailureClassification.INFRASTRUCTURE_FAILURE,
            )
        finally:
            if runtime_ready or self._scheduler_thread is not None or self._session_futures or self._workload_created or self._telemetry_created or self._environment_created:
                try:
                    self._stop_before_evaluation()
                except Exception as exc:
                    traceback.print_exc()
                    self._errors.append(("persistent_scenario_shutdown", exc))
            if runtime_ready and self.coordinator is not None and not any(
                source in {"persistent_scenario_shutdown", "persistent_scenario_evaluation", "persistent_scenario", "ledger_seal"}
                for source, _ in self._errors
            ):
                try:
                    self._materialize_run_validity()
                    result = self._final_evaluate()
                except Exception as exc:
                    traceback.print_exc()
                    classification = _classify_provider_error(exc, FailureClassification.INFRASTRUCTURE_FAILURE)
                    self._runtime_error = exc
                    self._runtime_error_classification = _prefer_failure(self._runtime_error_classification, classification)
                    self._errors.append(("persistent_scenario_evaluation", exc))
            if result is None:
                classification, failure_error = self._failure_classification()
                reason = repr(self._errors[-1][1]) if self._errors else "Persistent Scenario did not reach a final evaluation"
                result = self._invalid(classification, reason)
                if classification is FailureClassification.AGENT_FAILURE:
                    result["valid"] = True
                    result["model_failure"] = True
                    result["failure_classification"] = classification.value
                    result["FailureClassification"] = classification.value
            self._activation_executor.shutdown(wait=True)
            self._session_executor.shutdown(wait=True)
            cleanup_errors = self._cleanup()
            run = self.persistent_scenario_run
            run.ended_monotonic = self.clock.monotonic()
            run.ended_wall = time.time()
            run.runtime_evidence = {
                "environment_created": self._environment_created,
                "environment_deployed": self._environment_deployed,
                "workload_created": self._workload_created,
                "workload_started": self._workload_started,
                "telemetry_created": self._telemetry_created,
                "telemetry_started": self._telemetry_started,
                "telemetry_sample_count": len(run.trusted_telemetry),
                "ledger_event_count": sum(
                    sum(ledger.event_count(kind) for kind in ("planned_transaction", "transaction_attempt", "transaction_terminal", "planned_job", "job_attempt", "job_terminal", "freshness_sample"))
                    for ledger in run.ledgers.values()
                ),
                "ledgers_sealed": self._ledgers_sealed,
            }
            if cleanup_errors:
                cleanup_reason = "Persistent Scenario cleanup failed"
                result = self._invalidate_result(
                    result,
                    FailureClassification.INFRASTRUCTURE_FAILURE,
                    cleanup_reason,
                )
                result["cleanup_errors"] = cleanup_errors
                result["pre_cleanup_evaluation"] = run.pre_cleanup_evaluation
                run.failure_classification = FailureClassification.INFRASTRUCTURE_FAILURE
                run.failure_certificate = self._failure_certificate(
                    FailureClassification.INFRASTRUCTURE_FAILURE,
                    cleanup_reason,
                )
                result["failure_certificate"] = run.failure_certificate
                run.evaluation = result
            else:
                classification, failure_error = self._failure_classification()
                has_failure = any(
                    candidate is not None
                    for candidate in (
                        self._runtime_error_classification,
                        self._scheduler_error_classification,
                        self._persistent_scenario_error_classification,
                        self._agent_error_classification,
                    )
                )
                if has_failure:
                    if classification is FailureClassification.AGENT_FAILURE:
                        result = dict(result)
                        result["failure_classification"] = classification.value
                        result["FailureClassification"] = classification.value
                        result["model_failure"] = True
                        result["valid"] = True
                    else:
                        result = self._invalidate_result(
                            result,
                            classification,
                            repr(failure_error) if failure_error is not None else "Persistent Scenario provider failed",
                        )
                    result["pre_cleanup_evaluation"] = run.pre_cleanup_evaluation
                    run.failure_classification = classification
                    run.failure_certificate = self._failure_certificate(
                        classification,
                        repr(failure_error) if failure_error is not None else "Persistent Scenario provider failed",
                    )
                    result["failure_certificate"] = run.failure_certificate
                    run.evaluation = result
            if run.pre_cleanup_evaluation is not None:
                result.setdefault("pre_cleanup_evaluation", run.pre_cleanup_evaluation)
            result["cleanup"] = list(run.cleanup)
            run.evaluation = result
            certificate = run.failure_certificate or {}
            # The evaluator may invalidate a runtime-clean run (its validity
            # block carries its own classification/reason, e.g. a ledger
            # integrity verdict); the serialized validity must carry that
            # classification instead of crashing on a bare invalid fact.
            evaluation_validity = result.get("validity") if isinstance(result.get("validity"), dict) else {}
            validity_classification = (
                run.failure_classification.value
                if run.failure_classification is not None
                else evaluation_validity.get("classification")
            )
            run.validity = RunValidityFact(
                valid=result["valid"],
                classification=validity_classification,
                reason=certificate.get("reason") or evaluation_validity.get("reason"),
                ledger_complete=self._ledgers_sealed,
            )
            if self.gate_name is not None:
                gate_result = build_gate_result(
                    self.gate_name,
                    run,
                    event_activation=self.event_activation,
                    runtime_evidence=run.runtime_evidence,
                    cleanup_errors=tuple(cleanup_errors),
                )
                result = dict(result)
                result["gate_result"] = gate_result
                run.gate_result = gate_result
                run.evaluation = result
        return result

    def _classified_failure(self) -> tuple[FailureClassification, Exception | None] | None:
        candidates = (
            (self._runtime_error_classification, self._runtime_error),
            (self._scheduler_error_classification, self._scheduler_error),
            (self._persistent_scenario_error_classification, self._persistent_scenario_error),
            (self._agent_error_classification, self._agent_error),
        )
        selected: tuple[FailureClassification, Exception | None] | None = None
        for classification, error in candidates:
            if classification is None:
                continue
            if selected is None or _FAILURE_PRIORITY[classification] > _FAILURE_PRIORITY[selected[0]]:
                selected = (classification, error)
        return selected

    def _failure_classification(self) -> tuple[FailureClassification, Exception | None]:
        return self._classified_failure() or (FailureClassification.INFRASTRUCTURE_FAILURE, None)

    def _materialize_run_validity(self) -> None:
        """Materialize run validity before final evaluation consumes it.

        The evaluator refuses runs whose validity facts are unmaterialized.
        Validity at evaluation entry is the classified runtime failure state
        plus the sealed-ledger completeness; an agent failure keeps the run
        valid because the run is a valid observation whose model failed.
        """
        run = self._require_run()
        selected = self._classified_failure()
        if selected is None:
            run.validity = RunValidityFact(
                valid=True, classification=None, reason=None, ledger_complete=self._ledgers_sealed,
            )
            return
        classification, error = selected
        run.validity = RunValidityFact(
            valid=classification is FailureClassification.AGENT_FAILURE,
            classification=classification.value,
            reason=repr(error) if error is not None else None,
            ledger_complete=self._ledgers_sealed,
        )

    def run(self) -> dict[str, object]:
        return self.run_persistent_scenario()
