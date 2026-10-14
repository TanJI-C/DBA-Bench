---
doc_id: guide.persistent-scenario.implement-persistent-scenario
doc_type: guide
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, persistent-scenario, postgres, tidb]
summary: Guides production-first implementation of the persistent scenarios from the portfolio contracts, covering scope, business contracts, event design, three-path validation, runtime lifecycle, evaluation surface, and acceptance order.
source_of_truth: contract
related: [standard.persistent-scenario.architecture, standard.persistent-scenario.evaluation, standard.persistent-scenario.difficulty, standard.evaluation.dp-op-sp]
language: en
---

# Persistent Scenario Production-Grade Instance Implementation Guide

## 1. Scope and order

This guide is the target process: implementation progress must not be reported as passing runs or calibration. Read in order: the [architecture](../../standards/persistent-scenario/architecture.standard.md), [evaluation](../../standards/persistent-scenario/evaluation.standard.md), and [difficulty](../../standards/persistent-scenario/difficulty.standard.md) standards, and the [five-instance design](../../persistent-scenarios/postgresql/production-portfolio.contract.md).

First define the production services and workload, then define risk evolution and the three paths, and write the injector last. Do not start by picking 5–10 cases from the case library to piece together a timeline. Old cases can lend mechanisms; native capabilities do not need ScenarioCase identity.

### Implementation boundary

This guide is the implementation entry point; the three standards above define general rules, and the five-instance target contract defines the PG portfolio, timeline, three paths, and the file-level change list. Budgets and timelines not yet measured stay provisional; verify resource feasibility first, then freeze the numbers, and never tune against model scores.

The five instances do not adopt bounded Scenario constraints such as mandatory reuse of the case library, fixed event quotas, scenario/case pair deduplication, per-injected-event diagnosis responses, and a new session per alert. Business delivery deadlines remain in effect; event remediation deadlines are observational only. The five instances do not require item-by-item enumeration of all uncontrolled cascades; instead, they require real inputs, a trustworthy business ledger, data invariants, and a safety history that covers actual consequences.

The design philosophy is: production services and the workload determine faults; brief bursts of pressure, repetition, and interaction are allowed; ongoing operations are evaluated by business delivery, data correctness, and safety across the whole run; the full/zero/incorrect-handling three paths prove solvability, the need for intervention, and decision effectiveness. A single symptom disappearing, being prevented, or being offset by another event does not automatically constitute failure.

## 2. Business contract first

Specify the users, transactions/reports/jobs, data ground truth, topology, normal external arrivals, resource budgets, business deadlines, acceptable losses, required system states, and safety authorizations. OLAP uses a job manifest, and HTAP has objectives on both sides; contrast flows are kept separate from required business. Build an external ledger that is recomputable and cannot be rewritten by the Agent.

Make explicit the Agent's actual tools and control plane. When scheduling concurrency, retries, or routing must be changed, provide authorized interfaces that genuinely take effect, rather than requiring modifications to inaccessible application code. The healthy baseline must cover normal peaks and legitimate maintenance, not just idle probes.

## 3. Design events and interactions

The event table records external intent, arrival time, mechanism, observable signals, resource ownership, duration of effect, and potential interactions. Repeated mechanisms, different entities, and partial overlap are allowed; independent causality and per-event responses are not required.

Later arrivals do not wait for the Agent; real business dependencies are expressed through business job state — for example, a backfill waits when the schema is not ready — and cannot be driven by the benchmark starting only after the previous Event has been scored. The injector does not repeatedly undo remediation to keep the fault alive.

Record applied, attempted/prevented, and technical failures: prevention requires a trustworthy protection state and evidence of actual attempts; unknown anomalies are exposed directly. Drop the unique scenario/case pair and the fixed long-tx-before-lock rules in favor of real resource conflicts and bounded activation validation.

## 4. Three-path design and experiments

1. Full handling: legitimate public tools can satisfy end-to-end OP/SP; verify at least one alternative remediation or advance prevention.
2. Zero handling: all external changes keep executing, and the business ends with at least one violation; not every injected fault is required to survive.
3. Incorrect handling: treating only the symptoms, sacrificing another business function, and dangerous shortcuts each have observable failures; failure on the incorrect path does not automatically prove Hard.

Validate the resources and semantics of subsequent events under unresolved, resolved, and prevented prefixes. When a fault cascade intentionally eliminates another symptom, judge by service delivery. Regressions, repetition counts, and time to detection are explanatory data, not additional hard event gates.

## 5. Runtime and lifecycle

One environment/topology runs continuously, with one persistent mailbox session; regular work items and inspections are handled within the same conversation; the control tools are mailbox read/write/wait. Task completion is bookkeeping and does not imply recovery. Public alerts come from monitored symptoms and must not leak internal event IDs, exact remediation targets, or standard SQL.

Workload, scheduling, Agent, and telemetry are independent; original sessions and compaction phases are recorded append-only. Stopping business input, stopping the Agent, drain, and final sampling are specified in the contract. Final evaluation happens before reverse cleanup; cleanup only reclaims the resources actually used in this run and does not undo legitimate remediation.

## 6. Evaluation and minimal implementation surface

Compute OP from service objectives, data correctness, and required system states; SP reads actions, states, and authorizations; DP may be N/A — answering for every fault is not required. Do not build a generic untyped rule engine first; directly implement the transaction/job/watermark/delivery contracts the five instances need, reusing existing capabilities such as database/sql and query_results.

Terminal states such as workload timeouts are separated from collection failures. Deployment/provider/collector failures make the run invalid; a database broken by the Agent under test is not automatically invalid — the external ledger keeps recording business and safety consequences.

## 7. Rework and acceptance order

Freeze inputs/spec/data/resources/schema; implement the new model, ledger, capabilities, and evaluator; migrate the five instances and their consumers; delete old instance entry points and old aggregation paths; focused tests; real healthy runs, three paths, prefixes, and cleanup; a real-model pilot; finally validated. All Python commands run inside the conda aiops environment, and experiments follow the [benchmark experiment guide](../benchmark/run-experiment.guide.md).

Tests must cover repeated capabilities, prevented events, cascade disappearance, one remediation fixing multiple events, low QPS, retry denominators, cross-horizon effects, HTAP dual-side constraints, GUC effective scope, ledger tampering, and real timeouts and collector failures.

Formal delivery includes the five-instance contract, the implemented spec, three-path scripts/traces, failure classification, evidence of equivalent solutions, budget sources, and resource and cleanup records. Keep development_provisional when only documentation or unit tests have passed; do not report industrial realism as proven by measurement.
