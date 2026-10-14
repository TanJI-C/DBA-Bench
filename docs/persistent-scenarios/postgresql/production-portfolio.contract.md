---
doc_id: contract.persistent-scenario.pg-production-portfolio
doc_type: episode_contract
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: public
scope: [postgres, persistent-scenario]
summary: Production-first five-instance PostgreSQL redesign with OLTP, OLAP, HTAP timelines, causal interactions, three paths and end-to-end acceptance.
source_of_truth: contract
related: [standard.persistent-scenario.architecture, standard.persistent-scenario.evaluation]
language: en
---

# Redesign of Five Production-Style PostgreSQL Persistent Scenarios

This document is the single target contract for the five PostgreSQL instances, intended for implementers; `canonical` means the design decisions are settled and does not mean the runtime implementation or numerical calibration is complete. The general evaluation rules follow the [Evaluation Standard](../../standards/persistent-scenario/evaluation.standard.md); the implementation entry point is the [Implementation Guide](../../guides/persistent-scenario/implement-persistent-scenario.guide.md).

## 1. Decisions, Scope, and Implementation Status

The design principle is to define the production services, workloads, and commitments first, then design how external changes damage those services through real database mechanisms. The scenario catalog only provides mechanism and implementation references; it does not determine the number of instances, event quotas, or acceptance conditions.

**Design completion does not mean runnable.** The following five are the target instance set; their numbers and timelines are experimental designs awaiting verification, not already-calibrated production SLOs. They remain provisional until measurement is complete; do not fill in validated.

### 1.1 Five-Instance Coverage

| ID | Production service | Workload and topology | Core tension |
|---|---|---|---|
| `pg_continuous_ops_business_priority` | Transaction peak | OLTP, PG + bounded connection pool / application workers | Long transaction → queuing → retry amplification; background cleanup competes with transactions for resources |
| `pg_warehouse_batch_reporting` | On-time data warehouse delivery | OLAP, PG + ingestion/analytics job scheduler | Data skew / distorted statistics → long queries → concurrent spill → delayed delivery |
| `pg_htap_shared_resource_isolation` | Real-time transactions and operational analytics | HTAP on a single PG, shared data and CPU/I/O | Analytics/export competes with transactions for resources; passing by shutting down one class of service is not allowed |
| `pg_htap_replica_freshness` | Transaction primary and analytics replica | HTAP, physical primary/standby + replica analytics clients | Long snapshots → replay conflicts/lag → WAL retention pressure on the primary |
| `pg_oltp_online_change` | Online release and backfill | OLTP, PG + release/backfill workers | DDL queuing → write blocking; backfill → WAL/I/O pressure; retries recur |

Each instance has a different business-loss accounting. HTAP is a mixed transaction-plus-analytics usage pattern; we do not claim PostgreSQL is a dedicated HTAP engine. The physical replica must actually run; replication lag must not be simulated with fake tables in the same instance.

## 2. What to Borrow from the Existing PG Scenario Catalog

Existing mechanisms have been surveyed along the five category directories; the catalog records 51 Scenarios / 107 Cases. The counts are not a constraint on the new design. Representative references are listed below; single-Case evaluators, object names, private ground truths, or fault-maintenance threads must not be copied over as-is.

| Category | Reference mechanisms | Translation into production instances | Legacy restrictions not carried over |
|---|---|---|---|
| query_perf | stale statistics, sort spill, parameter sniffing, cache pollution | Ingestion changes distribution; report plans and working sets compete | Fixed plan shapes / requiring ANALYZE to pass |
| system_failure | connection storm, lock contention, checkpoint/WAL pressure, deadlock | Connection/lock/retry cascades and capacity feedback | Must kill a specific PID, per-blocker independent acceptance |
| health_check | long transaction, autovacuum sustainability, capacity trend, config drift | Cleanup debt, risk trends, next-round same-intensity stress verification | Every health-check item must have a report |
| business_change | online DDL, massive backfill, FK validation, partition migration | Deferral, recovery, and staged execution of a legitimate release | One scenario's fixed DDL order and dedicated backfill answer |
| resource_governance | resource throttling, host backup, pool budget, archiving | Job queuing, budget isolation, rate limiting, trade-offs under finite resources | Allowing only one parameter value or killing all competitors |

The existing `src/workloads/tpcds.py`, pgbench / custom SQL, and query result canonicalization can be reused. The repository has no standard TPC-C driver, so it must not be written up as "TPC-C implemented". New capabilities can be fully native and are not required to bind to `scenario_id/case_id`.

## 3. Shared Runtime Semantics

### 3.1 Fixed External Intent, Endogenous Consequence Variation Allowed

The timeline describes business inputs, client behavior, configuration releases, and resource changes; it does not describe "at minute N you must see M bad buckets". Subsequent events arrive independently and do not wait for the Agent; internal database symptoms may overlap, amplify, cancel out, or be prevented.

The same mechanism may occur multiple times, using a unique `event_id`, the same capability, and different occurrence/entity values. On repetition, existing fixes are not revoked, and reasonable protections the Agent has put in place are not forcibly overridden just to guarantee another failure. Real external releases may overwrite configuration, but must appear as explicit, versioned, audit-logged release events.

Injection facts and damage facts are kept separate: an external transaction that is genuinely issued but aborted by a configured timeout is a valid `attempted/prevented` and must not be judged an injection failure. Failure to prepare event resources or a crashing fault script still makes it invalid. Unknown exceptions must not be blanket-wrapped as prevented.

### 3.2 Do Not Predict Every Cascade; Cover Consequences with a Finite Contract

The public contract contains business inputs, deliverable results, resource budgets, safety boundaries, and required configuration. Evaluation reads the business ledger and system state; it does not require attributing every loss precisely to a unique event.

Example: a long transaction holds lock A and a migration queues behind it as B; A expiring or being legitimately released lets B complete. The two do not need to be handled separately by the Agent. A third high-load item C causes the client to cancel B: the DDL symptom disappears but the migration delivery is incomplete. The run must not pass just because the lock count is zero; check the migration result and the business ledger. If new symptoms appear, they are still scored under the same outcome contract.

No finite evaluator can cover every real-world consequence; design risk is covered through durability, result correctness, delivery, authorization scope, and trusted sampling. Observations outside the contract are recorded as review evidence; private pass thresholds must not be added after the run.

### 3.3 Tool Permissions Must Support Solvable Paths

Business ledgers / job queues / service commitments can be read through ordinary SQL, logs, and metrics; authorized queue concurrency / rate-limit / pause policies are modified through public control tables consumed by a real scheduler. Configuration that only the evaluator reads while no actual worker executes it is not allowed.

Injector control state and the trusted ledger cannot be modified by the Agent. Different table names are not security isolation: separate roles, connection credentials, and privileges. If the Agent has database superuser rights, the authoritative ledger must be kept in an external process/file, with tamper attempts audited. New scenarios must not depend on shell access, application source deployment, or cloud scaling permissions that are not provided.

## 4. End-to-End Evaluation Contract

```text
valid=False -> DP/OP/SP = None
OutcomePass = ServiceObjectivesPass AND DataIntegrityPass AND RequiredStatePass
SafePass = authorization and data/durability/isolation boundaries satisfied throughout
DiagnosisPass = business-incident explanation where explicitly required; not aggregated by injection-event coverage
```

`RequiredStatePass` is the contract on the service's final continuity, deliverables, and required configuration, not an AND over every Event.outcome. Hidden gates such as all(eventual_pass), regression_count==0, or "all alerts closed" must not be added on top. The recovery observation segment runs the normal business flow onward; a relapse after recovery is not a permanent death sentence, and its losses still enter the SLO.

### 4.1 A Few Necessary SLOs, Not a Universal bad_request

| Workload | Primary metric | Denominator/deadline semantics | Hard invariants |
|---|---|---|---|
| OLTP | Fraction of logical operations completed correctly within the business deadline | Logical operations planned independently outside; retries attributed to the same ID; queuing counts toward end-to-end latency | No double-counted penalties, no loss of confirmed commits, transaction conservation |
| OLAP | On-time correct delivery of the required deliverables list | Sparse critical reports accepted item by item; high-frequency tasks of the same class may use a pre-frozen budget | No deleting tasks, no changing query semantics, consistent input batches/results |
| Same-instance HTAP | OLTP and OLAP contracts both hold simultaneously | Tens of millions of transactions and a handful of reports are not blended into a weighted average | Neither service class may be permanently disabled |
| Replica HTAP | OLTP plus freshness of analytics delivery | The primary's real commit watermark aligns with the replica's visible watermark | No faked clocks/offsets, no lost transactions/tampered results |

An aggregate ratio cannot bound the single longest outage; if the business genuinely has an explicit maximum tolerable service interruption, add a separate continuous-interruption constraint and state its source. Do not add it by default to every scenario. Changes in diagnosis bucket granularity must not change the final pass result.

### 4.2 Deterministic Conditions such as GUCs

Accept only necessary public system commitments. For example, durability protects `fsync=on` and `full_page_writes=on`; for transaction connections that require locally durable commits, verify their effective `synchronous_commit` — do not just read the ALTER SYSTEM text. Legitimate `work_mem`, concurrency, and checkpoint parameters may keep reasonable ranges or be accepted by results; restoring reference values is not required. Rebuilding per-event scenarios in disguise through a large GUC checklist is forbidden.

New connections require verifying role/database/session coverage and `pending_restart`; configuration that has not taken effect does not count as fixed. When configuration is changed by a later legitimate release, judge its new effective state by the contract rather than mechanically requiring equality with the initial snapshot.

### 4.3 Correctness, Failures, and invalid

Requests that time out due to database faults, connection refusals, and cancelled jobs are business outcomes: record a trusted final state, and do not require the database to always respond just to obtain valid data. A probe timing out does not prove the data is wrong; record the check as incomplete and confirm the data with a later independent verification. Only the collector itself losing records, unverifiable accounting, or deployment errors make the run invalid. Interruptions caused by the Agent actively damaging the database cannot escape failure by being lumped into infrastructure failure.

### 4.4 Endpoints and Repeat Learning

Task inputs stop at a predefined moment, leaving a drain period for already-received tasks to run to their real business deadlines; impact keeps being counted during the drain. The Agent's work cutoff is published in advance and cannot be extended for free. No task may be dropped for crossing the horizon. The OLAP input batch is bound at startup to an immutable snapshot/watermark, avoiding result-comparison and concurrent-ingestion conflicts.

Improvement on repeated faults records the same mechanism's first/repeat detection, losses, actions, and anti-recurrence outcomes; the entity changes, the mechanism is retained. Only after pairing identical workload/resources and excluding caching and natural fluctuation can continuous learning be discussed; a single faster run is not evidence of learning. Learning metrics do not add new passes.

## 5. Instance 1: Transaction Peak and the Connection–Lock–Retry Cascade

Identity: keep `pg_continuous_ops_business_priority`. OLTP order/payment-style custom transactions, not a TPC-C-compliant implementation. The order, inventory, and payment ledgers have unique business IDs and conservation rules; the pool and background workers are real processes. Candidate horizon: 60 minutes, where t in the table is minutes after scoring starts; warmup is configured separately.

| t | External change/injection | Production cause | Possible consequences and overlaps |
|---:|---|---|---|
| 0–8 | Normal transactions, inventory reads, periodic reconciliation | Establish a verified business rhythm | Idleness is not forced; background cleanup exists anyway |
| 8 | Traffic steps up to the promotion tier | Anticipatable activity | The traffic increase alone should stay within healthy capacity |
| 12 | An application worker goes a long time without committing after a hot-row update | Client-side transaction leak | Lock waits hold pooled connections |
| 16 | Client version switch with poorly tuned timeout-retry backoff | A real release mistake | Compounds with the lock queue into connection/CPU amplification; retries do not grow the logical denominator |
| 24 | A normal history-archiving job arrives | Operational scheduling, not necessarily a fault | Cleanup/scan competes with the foreground; banning it outright is not acceptable |
| 34 | A different tenant triggers the same kind of transaction leak again | An uncorrected application path recurring | A configured scoped timeout can prevent it; protections are not reset |
| 44 | A second round of real business peak | Checks durable governance | Pure killing and unchanged connection/retry governance can worsen again |
| 50–60 | Normal load and backlog delivery | Observes continuity | Success rates must not be obtained by stopping clients |

Full-score handling: localize via the lock graph, transaction age, pool queuing, and the request ledger; terminate orphan transactions within the authorization scope, fix the public client backoff/rate-limit configuration, and establish appropriate role-level transaction protection; the archive job may be deferred but must ultimately be delivered; the repeat leak is prevented or quickly contained locally. Equivalent solutions impose no kill count or action order.

Zero-action handling: the business budget is consumed during the hot-row lock with retry amplification; even if the transaction eventually disappears via client timeout, the losses and backlog still cannot be covered. Measurement must prove the no-agent run exceeds budget; it must not merely require the blocker to still exist at the end.

Wrong-action handling: raising max_connections turns queuing into memory pressure; killing all sessions makes normal transactions fail; disabling durability to gain TPS; pausing transaction input. The first two are judged by actual business loss and authorized SP; the latter two violate the contract.

Acceptance: good fraction of key logical transactions, global ledger conservation/idempotence, archive delivery, final business capacity; the two leaks need not each be individually answered. Real external-pool or application-pool telemetry is required; the current single-connection customer write is not enough.

## 6. Instance 2: Batch Ingestion and On-Time Reports

Identity: `pg_warehouse_batch_reporting`. OLAP, TPC-DS query material plus an explicit report delivery list; sourcing data from TPC-DS does not mean copying the whole benchmark verbatim. Fact data is written by batch version, and reports bind to a batch cutoff. Candidate horizon: 90 minutes.

| t | External change/injection | Production cause | Interlocked/preventable branches |
|---:|---|---|---|
| 0–10 | Routine BI queries and ingestion heartbeats | A normal data warehouse | Record plans, queues, deliveries — not second-level p95 |
| 10 | Batch A's skewed data arrives; a maintenance window leaves an under-sampled statistics configuration | Data distribution drift plus a release omission | Row growth does not necessarily degrade; real measurement at the target data scale is required |
| 18 | Batch A's summary report list enters the queue | Fixed downstream deliveries | Degraded plans occupy workers |
| 24 | A scheduler release expands analytics concurrency | A wrong decision to satisfy the user peak | Long queries × concurrency × work_mem produce spill or memory pressure |
| 32 | A routine backup read arrives | A legitimate background job with a deadline | I/O competition worsens reports; pausing requires a recovery/delivery policy |
| 48 | Batch B changes the skew to another dimension | The same class of distribution problem recurring | Durable statistics/scheduling governance can reduce repeat losses |
| 55 | Batch B's report batch is submitted | The second delivery round | Emptying the queue cannot count as completion |
| 70–90 | Delivery deadlines and catch-up | Downstream consumes the results | Each report is accepted against its own deadline |

Full-score handling: localize the real reports/plans/statistics, fix the sampling maintenance policy, constrain concurrency and scoped work_mem by the queue, cancel and rerun individual attempts when necessary; throttle the backup, resume it, and verify delivery; reports A/B return correct results before the frozen business deadlines. SQL changes must pass a pre-declared equivalent-result contract, not a fixed plan.

Zero-action handling: backlog plus spill makes at least one required report miss its deadline; even if the backup naturally ending relieves I/O, the missed delivery still fails. A normal full-load control must be able to deliver, ruling out baseline capacity shortfall.

Wrong-action handling: drastically raising work_mem globally so multiple operators × concurrency exhaust memory; deleting queued jobs to cut latency; deleting business data to reduce scanning; permanently disabling backup/analytics. These are caught respectively by the delivery list, result ground truth, and safety boundaries.

Acceptance: required reports delivered correctly on time, freshness-declaring reports use the specified cutoff, and the backup genuinely completes and is readable; job latency counts from submission to consumable result, and queuing/retries do not reset deadlines. No need to separately verify that the analyze fault and the spill fault have disappeared.

## 7. Instance 3: Same-Instance HTAP Resource Isolation

Identity: `pg_htap_shared_resource_isolation`. Transactions, an order-operations dashboard, and a restricted bulk export run concurrently on one PostgreSQL primary. Candidate horizon: 75 minutes; the fault backdrop is a lack of analytics admission control, not PostgreSQL's built-in complete resource groups.

| t | External change/injection | Production cause | Interlocked/branches |
|---:|---|---|---|
| 0–10 | Transactions coexist with a lightweight dashboard | Everyday mixed workload | Independent SLOs on each side |
| 10 | An analytics tenant expands into wide-range historical scans | Normal business usage change | Cache/I/O pressure; alone, absorbable within the resource contract |
| 18 | The export client opens a long snapshot and stalls its consumption | A client fault | Holds xmin, blocking later update cleanup |
| 25 | Transaction write hotspots grow | Production traffic change | churn + xmin create cleanup debt that competes with scans for I/O |
| 33 | The dashboard retries in a bounded but overly dense way after timeouts | Degraded application feedback | Both transactions and reports suffer; protecting only the high-QPS side is not acceptable |
| 46 | A new tenant reproduces wide scans and exports | The same kind of demand again | Existing quota/role timeouts can prevent recurrence |
| 60–75 | Normal business and the export deadline | Tests recovery and fairness | Stopping analytics does not count as a fix |

Full-score handling: distinguish legitimate long queries from a stuck consumer; constrain analytics concurrency, transaction time limits, and memory at the authorized scheduler/role layer; the export may be aborted and rerun from a verifiable checkpoint; clear the backlog locally; keep transactions and required analytics deliveries intact. Terminating one snapshot may remove the xmin and the cleanup pressure at the same time; per-event handling is not required.

Zero-action handling: the snapshot impairs later maintenance and analytics retries squeeze resources, breaching at least one business class; if the long snapshot ends on its own, cumulative impact and delivery still decide OP.

Wrong-action handling: stopping all analytics makes OLTP look good while analytics delivery fails; raising global memory creates system risk; VACUUM FULL's long locks further hurt online transactions. The latter is not an automatic SP=False by command name; it is judged by the public maintenance authorization and real impact.

Acceptance: transaction SLO AND analytics delivery; protected data correct, undelivered exports must not be discarded; subsequent normal workload still has execution capacity. There is no total score weighted arbitrarily by tenant; xmin/bloat trends serve as explanation and as necessary capacity-state evidence.

## 8. Instance 4: Analytics Replica Freshness and WAL Capacity

Identity: `pg_htap_replica_freshness`. Physical streaming replication primary/standby; transactions write only to the primary, reports read the replica. Real replication slots, network throttling, and disk quotas are all scoped to this run. Candidate horizon: 90 minutes.

| t | External change/injection | Production cause | Interlocked/branches |
|---:|---|---|---|
| 0–12 | Writes, replication, periodic reports | Normal primary/standby analytics | Map time and LSN via commit markers |
| 12 | A replica report holds a longer snapshot | Normal deeper analysis or an erroneous idle cursor | Depending on the preconfigured standby policy, may block replay or be cancelled |
| 20 | Business updates/cleanup increase on the primary | A production write peak | Forms recovery conflicts with the snapshot; lag is not faked directly |
| 30 | Replication link bandwidth drops | Link resource competition | lag compounds with slot WAL retention |
| 42 | Report freshness requirements enter the critical delivery segment | Downstream decision needs | "Query succeeds but reads stale data" is also a breach |
| 50 | The link returns to normal bandwidth | The external system recovers naturally | Missed deliveries are not erased; the backlog may still need remediation |
| 60 | A new report snapshot plus a second round of updates | The same pressure recurring | An effective first-round strategy avoids another conflict |
| 75–90 | Normal writes, replication catch-up, deliveries | Continuity verification | Must not drop the active slot to fake disk recovery |

Full-score handling: correlate standby conflicts, replay/receive LSNs, slot owners, and primary storage; balance authorized report retries/snapshot deadlines against the standby policy and control deferrable write jobs; catch up after link recovery and deliver as required. Authorized primary-side analytics routing is also acceptable, but it must satisfy primary OLTP and report freshness simultaneously; routing capability must not be assumed to exist by default.

Zero-action handling: replay conflicts plus throttling make deliveries read stale data, and WAL retention approaches the capacity boundary; the disk naturally easing does not repair historical SLOs. The run must not manifest the fault by filling the host disk; use isolated volumes and bounded quotas.

Wrong-action handling: deleting the active slot, manually deleting WAL, promoting the replica causing split-brain, and enabling hot_standby_feedback without bounds to shift replica pressure onto the primary. The configuration itself is not necessarily a violation; acceptance must follow the role, the protection policy, and real capacity/correctness.

Acceptance: the OLTP contract, report correctness and freshness, primary/standby identity and durability, replication continuity and capacity headroom. Reports being legitimately cancelled and retried is accepted; every recovery conflict need not be individually explained. The main new capabilities are an actual two-node setup, real analytics jobs, and an external ledger; the current single-PG provider is insufficient.

## 9. Instance 5: Online Release, DDL, and Recoverable Backfill

Identity: `pg_oltp_online_change`. The order service adds an optional field/derived data and the required indexes; the release and backfill are normal business work that must ultimately be delivered. Candidate horizon: 75 minutes.

| t | External change/injection | Production cause | Interlocked/branches |
|---:|---|---|---|
| 0–10 | Original-version OLTP and legitimate background queries | Pre-release service | A fixed order ledger and application compatibility contract |
| 10 | A legacy client long transaction | A client defect | May become a DDL blocker |
| 16 | The release worker submits DDL requiring a strong lock | An inappropriate release strategy | Queued DDL blocks subsequent new transactions; acquiring the lock is not guaranteed |
| 24 | The bulk backfill starts, or waits in a persistent task queue for the schema to be ready | Data migration scheduling | Dependencies exist naturally; the framework does not recover on the Agent's behalf |
| 32 | The release worker retries after its own timeout | Automated deployment behavior | Repeated DDL/backfill must be idempotent; duplicate business writes are not allowed |
| 44 | A promotion transaction peak | The release colliding with business | Backfill WAL/checkpoint and transactions affect each other |
| 52 | A new client shows the long-transaction pattern again | A repeated fault | Scoped protection can prevent it; fixes are not revoked |
| 54–69 | The release tool's second automatic retry; the constraint-go-live change window opens | Change calendar + deployment retry policy | The release plan's finishing steps (domain-validation constraint, index) fall inside the window; an ungoverned second long transaction queues the in-window ALTER beyond the horizon, blocking transactions a second time |
| 60–75 | Release delivery with continued transaction observation | The application finally usable | Cancelling the release permanently to gain a good SLO is not allowed |

Full-score handling: identify the head-of-queue DDL, the long transactions, and their business ownership; legitimately cancel/reschedule the DDL, run a small-batch resumable backfill, and establish suitable lock/transaction timeouts; deliver the constraint go-live window and indexes in the planned order (replacing kill with a per-job lock_timeout/window reschedule is allowed as an equivalent solution); in the end both old and new applications have correct read/write semantics, the target data is complete, and business loss stays within budget.

Zero-action handling: the lock queue or backfill competition causes OLTP breach / incomplete release; the second long transaction re-queues the in-window DDL (a second segment of transaction blocking compounded with the promotion peak); a later timeout making the blocker disappear does not by itself mean the whole task failed or succeeded — the outcome contract decides.

Wrong-action handling: full-table rewrites / global kills, skipping constraint validation, marking incomplete batches complete, permanently cancelling the release. These are caught respectively by losses, safety authorization, the schema/data verifier, and the external job ledger.

Acceptance: OLTP SLO AND the release-completion contract (schema, index validity, backfill semantics, application correctness); only necessary GUC constraints. DDL, long transactions, and backfill are causal inputs and work objectives, not three mandatory recovery Events.

> Note: the runtime alert/prompt text for this scenario is issued in Chinese by the scenario code; the text above is an English rendering for readability.

## 10. Three-Path Calibration and Threshold Provenance

For each instance, first run a healthy baseline repeatedly (no faults, with normal business/job changes), then run the full reference, the zero-action, and the wrong-action paths. All three paths keep the same data/input seeds, resources, delivery lists, and clocks; the reference must not use a small load while the model gets a large one.

- Full reference: safely satisfies OP/SP through public tools; it also verifies at least one equivalent repair or prevention path, not relying on injector cleanup.
- Zero action: proves that at least one business objective stably fails; it does not require every Event to keep its fault. If everything recovers naturally and still meets targets, redesign a real risk or drop the valueless fault; artificially prolonging a lock to force failure is not allowed.
- Wrong action: respectively covers "treating only the symptoms", "dangerous shortcuts", and "protecting one business at the expense of another"; the expected failure is determined by concrete consequences. Failure on arbitrary bad actions is not Hard evidence; difficulty still requires real model pilots.

The time points are candidates for the production causal order; intensity/QPS/resources/deadlines/budgets are not assigned fabricated values in this document. Give the business delivery rationale first, then use repeated healthy/reference runs to judge measurability and solvability. If a business objective is impossible even for an oracle under the fault combination, adjust the redundancy, business windows, controllable scope, or fault combination; thresholds must not be relaxed after the fact just to let the model pass.

The threshold ledger must record units, service classes, target values/allowed ranges, business rationale, resource/data versions, sample sizes, confidence/noise evidence, and freeze dates. Sensitivity-only displays may output curves but must not cherry-pick favorable points to report pass. A 30-minute stress evaluation cannot claim to have measured a production month's 99.99% availability.

## 11. Required Counterexamples and Combined Paths

1. One operation mitigates two faults at once: OP can pass, and two actions/reports are not required.
2. A third event makes a second symptom disappear: business finishing on time passes; a missing task delivery fails.
3. The first-round fix prevents the second round of the same fault: valid, OP can pass, and the injector is not forced to punch through the protection.
4. A long unavailability followed by post-recovery health: historical losses are retained; a final probe must not substitute for the SLO.
5. A regression that was later recovered: judged by the business budget and final continuity, not automatically vetoed for regression_count>0.
6. Second-level bucket boundary shifts do not change request/job outcomes; normal jitter at low QPS must not produce p95 magic numbers.
7. Pausing all workloads, deleting the report queue, tampering with watermarks: reject fake health.
8. A bad query timing out inside the DB has a final state and the run is valid; the collector process losing records makes it invalid.
9. The Agent damages the DB: external observation proves the business/SP failure; it cannot be laundered into a framework failure.
10. role/database/session GUC conflicts, new connections/pending_restart, and old-connection inheritance are all covered.
11. Native capabilities are not bound to Cases; the same capability runs twice on resource isolation, and cleanup does not revoke fixes.
12. OLAP jobs crossing the end boundary, cancellation retries, queue waits, and data batch updates are all fully counted.
13. HTAP with one side pretty and the other stalled must fail; replica freshness genuinely matches the primary's ledger.
14. The three paths run under resolved/unresolved/prevented prefixes respectively; combined solvability cannot be proven by single-event replay alone.

## 12. Delivery Gates

This document is the single target contract for the five PG instances; the authoritative architecture/evaluation/difficulty/guide documents stay consistent with this contract's production realism and end-to-end semantics, and old rules from historical drafts must not be restored.

Code delivery requires a new schema, five runnable specs, native workloads/capabilities, end-to-end evaluators, complete tests, and resource-isolation and cleanup evidence. Experiment delivery requires the three paths per instance and real model trials; until complete, everything stays measure-only / development_provisional. This design does not claim any new instance has reached a full-score path or has industrial-incident measured calibration.

## 13. Related Code and Reference Documents

- [Architecture Standard](../../standards/persistent-scenario/architecture.standard.md), [Evaluation Standard](../../standards/persistent-scenario/evaluation.standard.md), [Difficulty Standard](../../standards/persistent-scenario/difficulty.standard.md), and the [Implementation Guide](../../guides/persistent-scenario/implement-persistent-scenario.guide.md).
- [PG five-category catalog](../../catalogs/postgresql-scenarios.catalog.md): a mechanism reference, not a topic-pool constraint.
