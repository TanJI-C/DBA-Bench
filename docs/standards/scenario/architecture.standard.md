---
doc_id: standard.scenario.architecture
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, scenario, postgres, tidb]
summary: Defines the current Scenario and ScenarioCase model, five-phase fault lifecycle, evaluator boundary, and delivery gates.
source_of_truth: code
related: [standard.evaluation.dp-op-sp, standard.scenario.difficulty, guide.scenario.implement-scenario-case]
language: en
---

# Scenario Architecture and Full-lifecycle Principles

This document describes the unified structure of the current DBA-Bench scenarios from requirements
to delivery. Implementation follows the current source code: the scenario model, runtime, and
system implementations live in `src/scenarios/`, the Scenario evaluator in
`src/scenarios/evaluation/`, and environments and deployment in `src/execution/`. Do not keep
using the old `src/control/scenarios` or `src/control/evaluators` paths as templates for new
implementations.

## 1. Scenario and ScenarioCase

`Scenario` is a stateless scenario container that expresses the database system, scenario identity,
description, and a stable, ordered set of Cases, and returns a `FaultPlan` per Case. It does not
hold connections, PIDs, timestamps, runtime objects, or the results of the previous run.

`ScenarioCase` is an immutable evaluation contract holding the Case-specific identity, alert,
initial state, target state, background workload, runtime/resource contract, reference report,
evaluator identity, and difficulty calibration. Dynamic objects, thresholds, times, injection
evidence, action history, the workload runner, and the final ground truth belong to `CaseRun` or
trusted run artifacts.

The boundary for adding each of the two must be explicit:

| Requirement | What to modify | What not to do |
|---|---|---|
| Adding a scenario | Add a new `Scenario` with at least one `ScenarioCase`, and complete registration, FaultPlan/Injector, the evaluator, the official entry point, documentation, and tests | Stuffing different operations problems into an existing Scenario, or merely copying an old Case and changing constants |
| Adding a Case | Add a new immutable `ScenarioCase` under the existing Scenario; extend the shared evaluator, Injector configuration, workload, entry-point selection, and tests when necessary | Re-creating a same-named Scenario for an existing one, or only changing table names, alerts, and object names |

A new Case must still have its own `case_id`, a continuous `case_no`, evaluator identity, fault
configuration, the target contract, and recovery. If a shared implementation is modified, all
existing Cases affected by it must be regression-tested.

## 2. Current Module Responsibilities

- `src/scenarios/base.py`: shared models such as `ScenarioCase`, `CaseRun`, `FaultPlan`, runtime
  contracts, and `BaseScenario`;
- `src/scenarios/postgres/<category>/`, `src/scenarios/tidb/<category>/`: system- and
  category-specific Scenarios, Cases, and real fault configurations;
- `src/scenarios/faults.py`: the five-phase `BaseFaultInjector` protocol;
- `src/scenarios/evaluation/base.py`, `protocol.py`, `diagnosis.py`, `outcome.py`, `safety.py`: the
  unified evaluator, structured submissions, DP/OP/SP, and shared verifiers/rules; system- and
  category-specific evaluators go in `src/scenarios/evaluation/postgres/<category>/` or
  `src/scenarios/evaluation/tidb/<category>/`;
- `src/scenarios/runtime/orchestrator.py`, `workload_runner.py`, `env_gateway.py`: post-deployment
  lifecycle, workload, the Agent loop, evaluation, recovery, and trace;
- `src/execution/`: PostgreSQL/TiDB environments, deployment, snapshots, and tool execution;
- `src/workloads/`: real background workloads reusable across scenarios.

Entry-point scripts only select the environment, workload, Agent, Scenario, and Case, and hand the
complete lifecycle to `Orchestrator.run()`. Entry points must not spin up a parallel deploy,
inject, evaluate, recover, or teardown path of their own.

## 3. From Requirements to Delivery

### 3.1 Requirements and the Case contract

Before coding, spell out: the real operations problem, the fault mechanism, the initial state,
target and excluded objects, Agent-visible evidence, the standard diagnosis/remediation path, the
family of legitimate remediations, the OutcomePass final invariants, the SP safety boundary, the
resource contract, cleanup ownership, the addition purpose, and the difficulty objective. A new
scenario must also explain why it is a separate Scenario; a new Case must explain its evaluation
value relative to the original Case.

The standard path is an explanatory reference path, not a fixed answer. The facts, constraints,
legitimate states, and safety boundaries needed to complete the task must be public to the Agent,
while the internal condition IDs, fixture variables, and direct answers of the ground truth stay
hidden.

### 3.2 Implementing real faults

`FaultPlan` stores only the Injector type and the complete configuration; it does not hold
Injector instances or mutable runtime state. The Injector must produce symptoms in real
database/system state and must not merely flip Python flags, fake metrics, tamper with tool
responses, or stuff answers into injection evidence.

All five phase signatures are exactly `self, context`:

1. `install`: create the complete persistent fault and base state in the fresh environment;
2. `activate`: validate the persistent state and restore runtime symptoms after the fault image
   starts;
3. `prepare_observability`: make the real evidence visible to the official tools and return the
   injection evidence the evaluator needs;
4. `quiesce`: stop runtime resources before the fault image is saved, keeping only persistable
   state;
5. `recover`: remove the fault and release the connections, sessions, threads, processes, files,
   configuration, and database state owned by the Case.

Repeated runs must recover reliably, and state ownership must be explicit. Do not add `inject()`,
`get_name()`, reflection, legacy-interface adapters, default configurations, or silent degradation
after exceptions.

### 3.3 Evaluator and protocol

Each Case's evaluator `scenario_id/case_id` must exactly match the ScenarioCase; use the unified
structured `submit` and submit only `diagnosis`, `outcome`, and `summary`. For DP/OP/SP design and
common pitfalls see the [DP, OP, and SP Design Principles](../evaluation/dp-op-sp.standard.md);
when implementing, do not re-create matchers, SQL result parsing, business ground-truth
comparison, or safety rules inside category modules.

Search existing implementations with `rg` first, then decide whether to extract a shared
abstraction. Prefer reusing the modules that own the behavior, such as `src/database/sql.py`,
`src/database/query_results.py`, `src/scenarios/evaluation/outcome.py`,
`src/scenarios/evaluation/safety.py`, `src/scenarios/evaluation/diagnosis.py`, and
`src/workloads/`. Abstract only when there are at least two real consumers with consistent
semantics; do not keep dual paths for compatibility with old callers.

### 3.4 Entry points, tests, experiments, and documentation

The official entry point is `examples/run_<scenario_id>_scenario.py`; it requires an explicit
`--case`, and supports structured mocks and a real `LLMAgent` with explicit configuration. Tests
must cover at least identity/numbering, the FaultPlan, the five-phase lifecycle, real
observability, both DP paths, OP final state and legitimate alternatives, SP risks, structured
submission, the entry point, and complete recovery, and must regression-test the affected shared
Cases.

Calibration and experiments follow `Smoke -> Pilot -> Main`: first verify mocks/references and the
environment, then run the real Agent specified by the manifest, and finally expand the matrix.
Provider, protocol, timeout, tool, or infrastructure failures must not be packaged as model
capability failures.

The scenario contract must let a reader reproduce: the fault mechanism (in plain language), the
standard diagnosis/remediation path, Agent-visible evidence, OP acceptance criteria, the SP
boundary, difficulty evidence, commands, trace, tests, and recovery. Every resource, space,
write-amplification, object-count, time/RTO, cleanup, or budget condition that can block OP must
publish its baseline, unit, threshold, scope, sampling window, and acceptance evidence; hidden
conditions and non-core cleanup must not by themselves decide an OP failure. Valid non-clean runs
go to an independent trace-level LLM judge, which reads the full path and semantically chooses one
primary type and one secondary label; DP/OP/SP are reference only and must not be used for
mechanical classification by specific values or combinations. If a valid LLMAgent gets
`OutcomePass=False`, first record whether the judge determined that the root cause was not found or
was found but not fixed, then record the labels, actions, evidence, failed results, final state,
and unmet invariants, and preserve the disagreement with the evaluator results.

### 3.5 Procedural historical observation for TiDB frozen-history

The scenario objectives, historical-investigation semantics, interference windows, and Agent
evidence protocols of frozen-history Cases are defined by each Case contract and by the
metric-history paths and frozen-history sections of the
[TiDB Scenario Catalog](../../catalogs/tidb-scenarios.catalog.md). This section only adds the
current architecture's implementation boundary for procedural historical observation; it does not
redefine scenario design goals.

A TiDB frozen-history Case may declare `procedural historical observation` to evaluate the Agent's
ability to locate candidate windows in a longer time series and then cross-validate with log or
TopSQL/slow-query evidence from the same window. This is an explicit extension of the observation
data plane, not an exemption from the real-fault principles:

- Current TiDB faults, remediation results, business ground truth, configuration, locks, topology,
  and safety state must still be produced by the real environment; trusted observation, the
  evaluator, OP, and SP always read the current real environment and must not read generated
  history to judge remediation success;
- each run must collect metrics for the normal phase and the target fault phase, plus the declared
  record sources, from this run's real TiDB environment; permitted background splicing, time
  shifting, explicit decoys, and transformations within the same bundle must be declared by the
  Case contract and be reproducible; the history must not be claimed to be a continuous real run of
  hours;
- the historical timeline must be constructed, validated, hashed, and frozen once before the Agent
  starts. During the run, no live samples may be appended, no provider replaced, no results
  temporarily modified based on query content, and no automatic fallback to an old archive;
  construction failure must terminate setup;
- the Agent can read frozen metrics and bounded records only through the declared historical
  observation tools. It must not inject generated history into Prometheus, fake
  INFORMATION_SCHEMA, intercept and rewrite arbitrary SQL, or use physical history tables as a
  bypass; current business/schema/config SQL remains executable, but controlled history-table
  queries must be explicitly rejected;
- the trace preserves the seed, history hash, visible scope, window roles, and source digests to
  support audit and reproduction, but the Agent's tool responses must not leak the target/decoy
  role, real/generated provenance, capture times, block IDs, the seed, or root-cause labels.

This capability applies only to local historical windows expressible by a short real capture;
multi-hour capacity drift, memory leaks, and long-term monotonic trends must not be faked by
procedural splicing. New frozen-history Cases must state in the scenario contract the boundary of
historical observation, negative evidence, visible windows, budgets, and how the current state is
really accepted.

## 4. Common Architecture Mistakes

- Putting dynamic connections, PIDs, timestamps, or cross-run objects into `Scenario`/static Cases;
- copying a new Case into a new Scenario, or only replacing constants with no new evaluation value;
- an Injector that produces no real state and only fakes metrics or tool fields;
- entry points duplicating the Orchestrator lifecycle, forking recovery, trace, or snapshots;
- shared evaluator/workload changes without regression-testing existing Cases;
- letting the old `src/control` paths, old protocols, or compatibility adapters guide new code;
- deleting necessary evidence, tightening legitimate remediations, or introducing unreproducible
  random races to make the model fail.
- treating procedural history as current state, faking historical tool responses in the injector,
  or continuing the run by reading live/old archives after history construction fails.
