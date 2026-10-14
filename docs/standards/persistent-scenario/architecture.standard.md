---
doc_id: standard.persistent-scenario.architecture
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, persistent-scenario, postgres, tidb]
summary: Defines the Persistent Scenario static contract, persistent runtime, event capabilities, ownership, cleanup, and domain boundary.
source_of_truth: contract
related: [standard.persistent-scenario.evaluation, standard.persistent-scenario.difficulty, standard.evaluation.dp-op-sp, guide.persistent-scenario.implement-persistent-scenario]
language: en
---

# Persistent Scenario Architecture Principles

This document is the production-realism-first architecture standard for Persistent Scenarios; the
implementation, review, and later refactoring of Persistent Scenarios all follow it. A long task
uses one persistent mailbox session and one public mailbox document; the Agent-facing Persistent
Scenario control plane has a single `mailbox` tool that selects read, write, or wait through
`operation`. No composite `ScenarioPass` is produced; the Event remediation deadline is
observation only, while the business delivery deadline belongs to the service contract.

Companion documents:

- [Persistent Scenario Evaluation Design Principles](evaluation.standard.md)
- [Persistent Scenario Difficulty Design Principles](difficulty.standard.md)
- [Persistent Scenario Implementation Guide](../../guides/persistent-scenario/implement-persistent-scenario.guide.md)
- [DP / OP / SP Design Principles](../evaluation/dp-op-sp.standard.md)

## 1. Core Definition

A Persistent Scenario is not a serial wrapper around multiple bounded Scenarios, nor does it
require one LLM call to block for the whole horizon. It evaluates:

> whether an Agent, in a persistent database environment facing continuous, asynchronous,
> partially observable, and mutually influencing operations events, can sustain business
> outcomes, recover stably, and control its own operational risk.

This definition carries four non-removable constraints:

1. **Persistent environment**: the database is deployed exactly once for the whole Persistent
   Scenario, and state produced by earlier faults and remediations must be retained.
2. **Independent event arrival**: events are scheduled by a monotonic timeline; later events do
   not wait for earlier events to finish being handled.
3. **Persistent session**: the whole Persistent Scenario creates exactly one Agent session and one
   continuous LLM conversation. The Agent works through the public mailbox document when there
   are tasks and idles when the mailbox is empty; when new tasks are appended, the system wakes
   the same session.
4. **Whole-timeline acceptance**: the final result is decided by the entire Persistent Scenario's
   business service objectives, data integrity, required system state, and global safety history,
   not by the fixed remediation action of any single event.

## 2. Boundary Between Persistent Scenario and bounded Scenario

| Dimension | bounded Scenario | Persistent Scenario |
| --- | --- | --- |
| Capability under test | Diagnosis and remediation of a single problem | Continuous operations, concurrent event handling, business priorities, and state retention |
| Environment lifecycle | One CaseRun gets one setup / teardown | One deployment for the whole Persistent Scenario; all events share the environment |
| Event model | One primary fault plan | Multiple Events arriving independently over time |
| Agent context | Usually one bounded interaction window | One persistent mailbox session keeping the same conversation across idle/wakeup |
| Pass conditions | Per-Case DP / OP / SP | Persistent-Scenario-level DiagnosisPass / OutcomePass / SafePass |
| Outcome acceptance | Case evaluator | PersistentScenarioEvaluator with the Persistent Scenario trusted contract |
| Time semantics | Fixed action windows or turn boundaries can be meaningful | Event response time is observation; business delivery time is accepted per the service contract |

A bounded Scenario can provide mature fault-injection capability, but it must not become the
runtime's primary model for the Persistent Scenario. What may be reused is the fault capability
expressed by `ScenarioCase`, `FaultPlan`, and injectors; what must not be reused is the bounded
Scenario evaluator, the one-shot `submit`, fixed action windows, and per-Case OP/SP.

The target dependency direction is:

```text
PersistentScenarioSpec / EventSpec
    -> PersistentScenarioEventCapability
    -> PersistentScenarioTrustedOutcomeContract
    -> PersistentScenarioSafetyPolicy
    -> PersistentScenarioEvaluator
```

In the end, the Persistent Scenario provider must face the Persistent Scenario contract directly.
The existing case library is only a mechanism reference; no Event is required to come from a
registered Case, and native capabilities register under their own ID/version/occurrence. The same
capability may recur; event_id uniqueness suffices. The legacy mandatory scenario_id/case_id
references and pair deduplication are technical debt slated for removal.

## 3. Separation of Static Contract and Runtime State

### 3.1 Static contract

`PersistentScenarioSpec` describes reviewable, serializable facts fixed before the run:

- the Persistent Scenario identity, database system, time range, and calibration status;
- the single environment specification and resource budget;
- OLTP logical transactions, OLAP jobs, HTAP services on both sides, data ground truth, and
  business delivery budgets;
- business SLOs and operations risk objectives;
- arrival times of external changes, repeated occurrences, trigger types, impact scope, and
  bounded activation;
- inspection cadence.

The static contract must pass validation before deployment. Unknown fields, duplicate IDs,
out-of-range times, missing objectives, insufficient resources, or unregistered capabilities must
fail immediately; the run must not continue with defaults.

### 3.2 Runtime state

`PersistentScenarioRun` and `EventRun` record only what actually happened during execution:

- the lifecycle of the environment and workload;
- injection start, success, failure, release, and cleanup;
- mailbox task publication and completion, Agent state, and actions;
- the business transaction/job/watermark ledger, checkpoints, trusted outcomes, and safety
  snapshots;
- provider failures and run validity;
- the final evaluation.

Static intent and runtime facts must not be conflated. For example, `start_seconds=300` is only
the planned time; the actual `injected_at_monotonic` is the runtime evidence. Likewise, a
configuration declaration that a flow would be affected cannot substitute for measured no-agent
impact results.

## 4. Layering and Ownership

### 4.1 System-neutral core

The core layer under `src/persistent_scenarios/model/`, `src/persistent_scenarios/runtime/`,
`src/persistent_scenarios/evaluation/`, and `src/persistent_scenarios/backend/` is responsible
for:

- strictly loading and validating the Persistent Scenario static contract;
- monotonic timeline scheduling;
- Event, session, and checkpoint state machines;
- the append-only trace;
- provider protocols and failure classification;
- Persistent-Scenario-level evaluation composition.

The core layer must not import Scenario evaluators, and must not contain PostgreSQL/TiDB object
names, SQL text, or fault special cases.

`src/protocols/report.py` defines structured reports shared by both task domains;
`src/database/system.py` defines database identities; `src/execution/specs.py` defines
environment resources, topology, and release specifications. Shared infrastructure must not
import task domains or benchmark. Environment and deployment implementations live under
`src/execution/environments/` and `src/execution/deployments/`; callers import defining modules directly.

### 4.2 System-specific provider

The database provider implements the generic contract as real system behavior:

- creating and destroying environments;
- registering, injecting, verifying, releasing, and cleaning up Event capabilities;
- running the workload and collecting telemetry;
- generating production-plausible alert symptoms;
- verifying the real impact and final state of Events;
- reading the trusted final state and the global safety state.

Provider output must be structured facts. The core layer composes facts per protocol; it must not
parse provider natural language to guess state.

### 4.3 Event capability

Every Event must own an explicit capability before entering a Persistent Scenario, declaring at
least:

- a unique capability identifier and the supported database systems;
- injection prerequisites and bounded activation;
- resource ownership, including processes, sessions, rows, tables, files, containers, or workload;
- observable evidence of injection success;
- the visibility contract of the alert or inspection;
- execution/prevention evidence of the external intent and observation of its business impact;
- the idempotent boundary of release and cleanup;
- conflict relations with other capabilities.

Event orchestration must not rely on "the configuration order should be fine". Resource ownership
must allow conflicts to be discovered at the static admission stage — for example, a lock event
holds customer rows while a later capability's activation also needs to access the same rows.
Such combinations must either be redesigned or explicitly prove that activation will not be
blocked indefinitely by an existing fault.

## 5. Persistent Environment and Lifecycle

A valid Persistent Scenario executes in this order:

```text
static admission
-> deploy once
-> start workload and telemetry
-> warmup health gate
-> capture baseline and safety baseline
-> run monotonic event timeline
-> keep one mailbox session through idle/wakeup
-> stop new mailbox tasks at horizon
-> stop the persistent Agent session
-> capture final checkpoints
-> final evaluation
-> reverse-order event cleanup
-> environment teardown
```

Key rules:

- warmup is environment health admission and context capture, not a way to turn a single
  incidental value into a hidden scoring gate;
- Event 2's arrival does not wait for Event 1 to be diagnosed, resolved, timed out, or cleaned up;
- Agent remediations and unresolved faults both persist across Events;
- completing a mailbox task only updates the public work record; it is neither a trusted recovery
  nor a release of Event resources;
- cleanup belongs to infrastructure reclamation only and must not erase state needed by the final
  evaluation early;
- final evaluation must happen before reverse cleanup;
- teardown must have a clear outcome whether it succeeds or not; failure marks the run invalid
  directly, and a dirty environment must not be dressed up as model failure.

### 5.1 Three Kinds of Time That Must Be Separated

| Time | Meaning | Blocks subsequent Events |
| --- | --- | --- |
| Event arrival | The scheduler starts injection and produces visibility | No |
| Incident resolution | The trusted outcome is satisfied and stability verification is complete | No |
| Injector cleanup | Injection resources are reclaimed after Persistent Scenario evaluation | No, only affects teardown |

Merging the three degrades the Persistent Scenario into a bounded Scenario queue and creates
event-ordering deadlocks.

## 6. Timeline, Concurrency, and Checkpoints

### 6.1 Monotonic timeline

All relative time computation, deadlines, latency, and event ordering use the monotonic clock.
Wall-clock is for display and cross-system correlation only and must not drive scheduling.

Event arrivals, Agent actions, workload observations, checkpoints, and provider results must carry
sortable monotonic timestamps. With identical timestamps, an append sequence guarantees a
deterministic order.

### 6.2 Append-only runtime history

The following data must be append-only:

- the timeline;
- Agent request/action/tool result history;
- mailbox document publication, completion, and other engine-side state changes;
- the Agent's database actions and tool results;
- workload observations;
- event checkpoints and safety checkpoints.

State machines may maintain current views, but must not overwrite or delete original evidence.
The evaluator computes results only from trusted run facts and must not rely on summaries modified
after execution.

### 6.3 Checkpoint

A checkpoint is a structured sample of the trusted environment state at a moment, not an Agent
self-report. Sample at least at these boundaries:

- healthy baseline;
- after an Event's injection is confirmed;
- after a mailbox task completes, or when the engine needs to record trusted state;
- verification window expiry;
- the end of the Persistent Scenario horizon;
- after high-risk actions.

Failures of checkpoint capture infrastructure must make the run invalid. When the database cannot
respond due to a fault or Agent actions, record verifiable unavailability facts and evaluate them
against the business contract; do not automatically classify them as infrastructure failure.
Fields that cannot be determined must not be faked as passing.

## 7. Agent Session and Mailbox Model

The entire Persistent Scenario creates exactly one `session-0001`. It binds one persistent Agent
instance and one continuous conversation; visible operations work items, periodic inspection
tasks, and later-appended work all enter the same mailbox, and no new Agent, context, or
conversation is created.

```text
Persistent Scenario start ----------> session-0001 starts and reads mailbox
visible work item ------> generic task appended -------------┐
periodic check ---------> routine task appended --------------┼-> same Agent wakeup
mailbox empty ----------> same session idle ------------------┘
new task appended ------> same conversation resumes
Persistent Scenario horizon --------> stop task publication and signal session stop
```

The mailbox is a public structured control plane containing at least:

- `pending`: tasks not yet completed;
- `completed`: completed tasks and their completion times;
- `revision`: a monotonically increasing version after each publication or completion;
- append-only history: task state changes and times.

The Agent-facing Persistent Scenario control plane is fixed to a single `mailbox` tool:

- `mailbox(operation="read")`: reads the current mailbox, showing both incomplete and completed
  tasks;
- `mailbox(operation="write", task_ids=[...], report={...})`: moves one or more specified tasks to
  `completed` and saves one structured report for that batch of work;
- `mailbox(operation="wait")`: suspends the current Agent when no incomplete tasks exist, until
  new tasks are appended or the Persistent Scenario ends.

A task payload contains only the title, description, symptoms, severity, and category that would
reasonably be visible in production monitoring. It contains no task provenance, `task_type`,
`event_id`, `scenario_id`, `case_id`, injector-private state, or evaluator ground truth. The Agent
does not need to, and cannot, distinguish tasks by their source through the control plane.

`mailbox(operation="write")` does not validate database state and does not trigger recovery
checks. `report` uses the same structured shape as the bounded Scenario `submit`:
`diagnosis.conditions`, `outcome.changes`, `outcome.verification`, and `summary` are required
fields, and `outcome.plan` is optional. Only when the contract explicitly requires a
business-incident explanation does the relevant report feed that incident's diagnosis matcher,
not mapped one-to-one per Event; it is not trusted database evidence and not an Outcome/Safety
result. Periodic inspection tasks only save reports and do not create diagnosis claims. One write
can complete multiple tasks, and the control plane does not set different completion paths by task
source.

On every activation the Agent first calls `mailbox(operation="read")`. With pending tasks it uses
ordinary database tools to handle the tasks it chooses, and after finishing one or more calls
`mailbox(operation="write", task_ids=[...], report={...})`; with no pending tasks it calls
`mailbox(operation="wait")`, and the system suspends that same conversation. When new tasks are
appended, the system wakes the same session and the same conversation, which continues reading the
live mailbox. Existing context compaction still runs per the Agent layer's existing implementation;
context management is not bypassed by creating new sessions.

`agent_sessions[].status` is the session lifecycle and uses `running`, `completed`, or `failed`;
`agent_sessions[].state` is the current working state and uses `active`, `idle`, or `woken`.
`mailbox(wait)` must record `idle` before it starts blocking, record `woken` after being woken by a
new task or the end signal, and record `active` when the next round of processing starts.

There is no second Agent session during the run. The control plane validates only the unique
session, operation parameters, task IDs, task states, and report structure; unknown task IDs,
duplicate completion, waiting with incomplete tasks, or a missing report raise protocol errors
immediately. The mailbox is an information notification and work-accounting mechanism, not the
final judging metric.

## 8. Alert and Inspection Observability

### 8.1 Alert Event

Alerts present only symptoms that monitoring systems would reasonably produce in production, such
as business error rates, wait counts, resource anomalies, or affected services. After an Event's
impact is confirmed, the engine organizes this content into an ordinary mailbox work item. The
Agent sees only the work item itself and does not know which internal source produced it. Alerts
must not directly contain:

- root cause names;
- the exact blocker PID, application name, or objects to kill;
- standard remediation SQL;
- the unique correct action order;
- evaluator-private fields.

Whether an alert is sufficient to trigger investigation should be calibrated with real LLM pilots;
"not leaking the answer" does not mean deliberately hiding every useful clue.

### 8.2 Inspection Event

An Inspection Event does not publish hints targeted at a specific Event. The scheduler only
appends ordinary routine-check tasks per cadence; the Agent observes the current system itself
with everyday database tools, and whether to act is its own decision. Completing a task only means
the Agent considers that piece of work done; it does not mean the engine endorses any finding or
remediation.

Whether recovery ultimately happened is still judged by the trusted outcome, business SLOs, and
safety rules reading real database state. Natural-language descriptions, task completion records,
or keywords cannot substitute for these checks.

Inspection cadence is a design parameter for discovery opportunities, not a difficulty switch for
shrinking the Agent's time budget.

## 9. Final Evaluation and cleanup

After the Persistent Scenario horizon ends, the scheduler stops creating new mailbox tasks, wakes
and stops the single persistent session, and waits for already-started bounded operations to reach
a protocol boundary. It then captures the final workload, event outcome, and safety checkpoints,
runs PersistentScenarioEvaluator, and finally cleans up in reverse order of the Events' actual
activation.

Reverse-order cleanup exists because of resource dependencies, not to treat cleanup as remediation.
Each capability must reclaim only the resources it owns; it must not undo legitimate Agent
remediations, nor reset the whole database to mask contamination.

Only three mutually independent pass results are reported:

```text
DiagnosisPass = the explicitly required business-incident explanation is correct; N/A by default
OutcomePass   = ServiceObjectivesPass and DataIntegrityPass and RequiredStatePass
SafePass      = PersistentScenarioSafePass
```

No composite `ScenarioPass` is produced. For the concrete semantics see
[Persistent Scenario Evaluation Design Principles](evaluation.standard.md).

## 10. Trace and run validity

The complete trace must preserve at least:

- the source spec, the actually run spec, the run ID, the code version, and resource leases;
- deploy, warmup, baseline, timeline, final evaluation, cleanup, teardown;
- each Event's activation handle, trusted evidence, checkpoints, and cleanup;
- the single mailbox session's inputs, `active`/`idle`/`woken` states, actions, tool results, and
  termination reason;
- one raw conversation that is never compacted, plus the Agent-perspective phase conversation
  appended after each compaction;
- the mailbox's current view and its append-only state-change history;
- every workload observation and telemetry completeness;
- the DP / OP / SP evidence references and failure classification.

When the provider implementation, tool transport infrastructure, deployment, trace recorder, or
telemetry collection infrastructure fails, the run must be marked invalid with a clear
classification and context retained. Database business timeouts, legitimate cancellations,
connection refusals, and Agent-caused database unavailability must be recorded by the external
trusted ledger as business outcomes; their OP/SP consequences must not be erased because of them.
For an invalid run all three passes are `None`; recording an infrastructure error as
`DiagnosisPass=False`, `OutcomePass=False`, or `SafePass=False` is forbidden.

## 11. Current Implementation Debt

The following is the current state, not a pattern to keep copying:

| Location | Current problem | Target |
| --- | --- | --- |
| `src/persistent_scenarios/evaluation/evaluator.py` / `src/persistent_scenarios/evaluation/diagnosis.py` | The shared layer must not define root-cause semantics for specific faults | Judged by the business-incident explanation matcher explicitly required by the contract, N/A by default, not a conjunction over all Events |
| `src/persistent_scenarios/backend/postgres/registry.py` | Depends on `SCENARIOS_BY_ID`, `ScenarioCase`, `FaultPlan` and dispatches by ID | An independent PersistentScenarioEventCapability registry |
| `src/persistent_scenarios/backend/postgres/capabilities/` | Some outcomes depend on action text, fixed SQL, object names, and `repair_action_observed` | Accept only final state, business ground truth, and public invariants |
| `PostgresEventProvider.agent_alert` | Some alerts leak exact blockers and the remediation order | Expose only production-plausible symptoms |
| `src/persistent_scenarios/evaluation/slo.py` | Some control thresholds bind directly to a single warmup | Use public, stable, calibrated thresholds; warmup only does health admission and context |

When addressing this debt, migrate directly to the target contract and delete the old paths and
hardcoding; do not add compatibility layers or dual evaluators.

## 12. Architecture Review Checklist

Before merging a Persistent Scenario, answer:

- Is the environment deployed exactly once, with all fault and remediation state retained until
  the final evaluation?
- Do later Events need not wait for an earlier Event's resolution, deadline, or cleanup?
- Does every capability have bounded activation, resource ownership, a trusted outcome, and
  cleanup?
- Do Event combinations pass resource-conflict admission instead of relying on lucky ordering?
- Do alerts expose only symptoms, and must inspection findings be discovered through real tools?
- Is there always exactly one mailbox session, with new-task wakeups reusing the same
  conversation?
- Are timeline, actions, checkpoints, and telemetry append-only and traceable?
- Is the Persistent Scenario evaluator independent of the bounded Scenario evaluator?
- Does final evaluation happen before reverse cleanup?
- Are evaluation-infrastructure failures (invalid) distinguished from database business failures
  and Agent-caused damage (valid business/safety consequences)?

If any item cannot be evidenced from code and trace, the Persistent Scenario has not met the
architecture admission bar.

## 13. Production Causality, Recurrence, and End-to-end Objectives

Define the production workload/business delivery first, then design external changes; there is no
requirement to reuse the existing case library or event quotas. The same fault may occur multiple
times, retaining Agent remediations and single-session state. Subsequent inputs arrive on
schedule, but whether symptoms appear depends on the real database state: successful prevention by
protective measures and symptom cancellation by other events are both valid outcomes, and require
evidence rather than swallowing injection exceptions.

Events may share resources and cascade; admission verifies real permissions/resources and bounded
execution, and does not use "the long transaction must precede the lock" to mask architectural
limitations. The injector must not continuously restore bad configurations or rebuild blockers
that were legitimately remediated in order to keep a fault alive.

RequiredStatePass targets final business continuity, deliverables, and required GUCs;
all(Event.outcome) and regression_count==0 are forbidden. Historical losses enter the SLO, and
normal load after recovery continues to verify continuity. DP does not require itemized answers
per injected event; multiple root causes can be covered by one incident explanation.

See the [Production-oriented Five-instance Portfolio](../../persistent-scenarios/postgresql/production-portfolio.contract.md)
for the new five-instance design, the deprecation list, and implementation gaps. A real-replica
HTAP needs a continuously maintained topology rather than fabricated lag; one deployment may
contain multiple database nodes with explicit roles.
