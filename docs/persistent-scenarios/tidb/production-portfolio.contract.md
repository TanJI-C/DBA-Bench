---
doc_id: contract.persistent-scenario.tidb-production-portfolio
doc_type: episode_contract
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: public
scope: [tidb, persistent-scenario]
summary: Five production-first TiDB target scenarios covering OLTP contention, OLAP delivery, TiFlash HTAP, TiCDC freshness and online topology change.
source_of_truth: contract
related: [standard.persistent-scenario.architecture, standard.persistent-scenario.evaluation, standard.persistent-scenario.difficulty, guide.persistent-scenario.implement-persistent-scenario]
language: en
---

# Implementation Guidance Contract for Five Production-Style TiDB Persistent Scenarios

## 1. Validity and Implementation Entry Point

This document settles the target design of the five instances and does not claim they are already implemented or calibrated. Implementation starts from the [unified guide](../../guides/persistent-scenario/implement-persistent-scenario.guide.md) and observes the [Architecture Standard](../../standards/persistent-scenario/architecture.standard.md), the [Evaluation Standard](../../standards/persistent-scenario/evaluation.standard.md), and the [Difficulty Standard](../../standards/persistent-scenario/difficulty.standard.md). This document supplements TiDB business context, topology, fault causality, and acceptance; it does not establish another set of general evaluator rules.

Bounded Cases serve only as mechanism references, not as a mandatory fault pool. This document and the injection timelines are authoring material and must not be leaked wholesale to the evaluated Agent; the public business objectives, authorizations, and observability information are provided by an independent runtime payload.

The minute counts in this document are a candidate experimental schedule, not fault-response deadlines. Business deadlines, budgets, data scales, and resource quotas must be frozen only after validation through the healthy and reference paths. All instances start as `development_provisional` / measure-only; no formal pass conclusions may be issued before business budgets are settled. A long-running scenario cannot claim realism by arbitrarily compressing hours of production MVCC/capacity accumulation into tens of seconds: risk can be constructed from an explainable historical data initial state, and then real change is run on top.

## 2. First Principles and the Five-Instance Boundary

Services and their commitments determine the workload, the workload determines the risks, and the risks determine the external inputs and faults. A distributed system's automatic leader election, retries, and scheduling are normal recovery capabilities; these mechanisms must not be repeatedly interrupted just to force the Agent to act. Whether zero-action fails is verified across the whole business time window; not every event is required to be fixed by hand.

| ID | Production service | Workload | Core business tension |
|---|---|---|---|
| `tidb_oltp_hotspot_resilience` | Order and inventory transactions | OLTP | Hotspot contention, slow TiKV, and retry feedback; protect idempotence and inventory |
| `tidb_olap_warehouse_delivery` | Periodic ingestion and business reports | OLAP | Distribution change, statistics and plans, import/analytics resource competition; ensure on-time batch delivery |
| `tidb_htap_tiflash_isolation` | Transactions and real-time business analytics | HTAP, TiKV + TiFlash | Analytics execution paths and resource competition; transactions and analytics must both stay available |
| `tidb_cdc_downstream_freshness` | Order database to a downstream fulfillment read model | OLTP + CDC data service | Sink backpressure, DDL compatibility, and recovery throughput; protect integrity and business freshness |
| `tidb_oltp_online_topology_change` | Online scale-out, traffic draining, and decommissioning | OLTP + cluster changes | Traffic migration, placement satisfiability, data scheduling, and redundancy recovery |

The CDC scenario does not masquerade as TiFlash HTAP: the downstream is an independent asynchronous replication system and must have its own result and freshness contract. The fifth example does not inject extra random disasters to pad the event count; it is built around one real maintenance task with a definite end state.

## 3. Shared Workloads, Tools, and Trusted Ledgers

- The OLTP external ledger records logical business IDs, planned arrivals, attempts, commit outcomes, and deadlines. Client retries do not grow the denominator; connection refusals, unsent requests, and queued items must not vanish. When a commit outcome is unknown, reconcile using the business idempotence key; a client timeout must not be equated with a rollback.
- The analytics job list freezes input batches, query parameters, result ground truth, and delivery deadlines; queuing, cancellation, and reruns still belong to the same delivery obligation. Required low-frequency reports are accepted item by item; global throughput must not mask missing reports.
- Finite resources, legitimate elasticity ceilings, and tool permissions are fixed. If the Agent is to tune application retries, ingestion concurrency, client routing, or downstream resources, a discoverable and actually effective control interface must be provided; it must not be required to modify inaccessible application source code.
- External business ledgers and ground truths are not placed in database tables the Agent can rewrite. The database, the TiCDC status interfaces, and monitoring are among the sources of truth and cannot singly serve as business ground truth.
- One persistent topology and one evaluated mailbox conversation; events arrive independently over time. Repeated injections are accounted with unique occurrences and do not reset legitimate fixes. Prevented events, cascades canceling out, and system self-healing are not automatically invalid.
- The same data, inputs, resources, and business deadlines validate the healthy, full, zero-action, and wrong-action paths. The full path should include an alternative repair or prevention proof; the Agent is not required to copy the reference actions.

## 4. Transaction Hotspots and a Slow Node: tidb_oltp_hotspot_resilience

### 4.1 Service, Topology, and Mechanisms

Order submission, inventory reservation, and order status reads; transactions carry idempotence keys and inventory must not be oversold. Candidate topology: 3 PD, 3 TiKV, 2 TiDB, real connection routing, and controllable application workers; replica counts and failure domains must be explicit. The environment budget does not allow solving problems by arbitrarily adding nodes.

Ordinary transactions are mixed with promotional hot items. Transaction contention on hot rows cannot be cured by "moving Regions"; range write hotspots and locks on the same business row must be distinguished. The slow node produces real latency through a reversible I/O/CPU throttle on a specific TiKV, without faking metrics. The whole Raft majority must never be made unrecoverable; a feasible reference path must be preserved.

Settlement-batch residue coupled with the hot zone (mechanism details are owned by the oltp package; no budget/deadline/timeout constants are changed):

- **Settlement-batch residue genuinely coupled with wave 2**: `settlement_long_tx` is upgraded from a single transaction to a bounded settlement batch — each settlement item takes and holds a write lock on an inventory row (a real business attempt); when an item finishes, unless paused, the batch proceeds to the next item in the queue. The later part of the queue lands on the second wave's promotional hot rows (SKU-0012 belongs to promo group B): unresolved batch residue shares hot rows with wave 2, the lock-wait chain compounds hotspot pressure, and wave-2 recovery misses SO. Killing the current session does not dissolve the residue (the client reconnects and continues the queue); the legitimate resolution path is the documented application configuration lever (see below).
- **Shared-resource overlap**: the target store of `tikv_slow_throttle` overlaps the store hosting the promo hot-zone leaders (proven by the leader distribution when the capability activates); if the throttle is released without rebalancing leaders/load, the hotspot stays pinned to the throttled store.
- **Catch-up spike**: after the throttle is lifted, a bounded, self-recovering real container-level CPU withdrawal is introduced (catch-up backlog consumes processing capacity): if hot-zone leaders are still concentrated on that store, the hot zone genuinely degrades again; if the leaders have moved away, the same spike no longer touches the hot zone. A one-shot "just lift the throttle" fix loses this recheck window.
- **Documented application configuration lever (control-interface obligation, §3)**: `ops.client_config` gains two columns with annotated semantics — `order_id_prefix` (deployment prefix: the client generates order numbers from its truncated deployment identifier so the generated identifiers satisfy the order table's column width/strict mode; empty = keep using the full deployment identifier, which under a long deployment identifier keeps being rejected with 1406) and `settlement_paused` (settlement-batch pause flag). Both are adopted through versioned releases by the trusted driver poller; this lever turns the "application/schema contract mismatch" deadlock into a legitimate repair path and serves as the dissolution mechanism for the coupling. The task copy stays symptom-based and does not leak root-cause information beyond the column names.

### 4.2 Candidate 75-Minute Timeline

| Time | External change | Causality and repetition |
|---|---|---|
| 0–10 | Normal transactions and a known normal peak, healthy admission | Establish a baseline with real writes |
| 10 | A promotion concentrates traffic onto a group of items; the settlement client starts batch processing (the queue contains promo-B hot rows) | Hotspot waits grow; settlement items are real business attempts, not immortal blockers; if unresolved, the residue persists |
| 18 | The TiKV hosting the relevant Regions enters a sustained resource slowdown | Waits compound commit latency; hitting the actually hosting node must be proven (overlapping the hot-zone leader store) |
| 25 | A declared legacy-client release enables aggressive retries | Uncertain commits and retry amplification, possibly affecting ordinary items; the release version is higher than the agent's release (the version is a floor) and does not roll back the agent's released configuration |
| 40 | The second promotion round switches the item set | Genuinely coupled with unresolved settlement residue (promo-B hot-row overlap); verifies protections are reusable, not pinned to the same PID/key |
| 55 | The slowdown is lifted and the promotion subsides | The post-lift catch-up spike briefly reduces the throttled store's processing capacity: if leaders have not moved away, the hot zone degrades again; the backlog is not automatically cleared by scripts |
| 60–75 | Normal inputs and continuity observation | Drain per the contract; earlier losses are retained |

### 4.3 Three Paths and Acceptance

- Full path: release the documented application configuration so order identifiers satisfy the column width (restoring the transaction path) and dissolve the settlement residue before wave 2 (pause + finish the current settlement item); distinguish the different roles of row locks and store latency, move the hot-zone leaders/load off the throttled store (or an equivalent rebalance), lift the throttle, and recheck recovery after the catch-up spike window; reconcile unknown commits and preserve idempotence. The second wave can be absorbed by the protections above.
- Zero path: if the application contract mismatch is not fixed, the transaction path is unusable; a sustained slow node + unresolved residue + retry amplification breach the frozen transaction budget; mere waiting (including the throttle lifting itself) cannot erase losses, and the catch-up spike still degrades the hot zone while leaders have not moved away. If the zero path still passes, the combination has not proven that intervention is necessary; the workload/mechanisms must be re-examined.
- Wrong path: lifting only the throttle without moving leaders (the catch-up spike makes wave-2 recovery miss SO); killing only sessions without pausing the settlement batch (the batch reconnects and continues, and the residue still recurs in wave 2); terminating/scaling down nodes instead of rebalancing (replicas and continuity genuinely damaged, surfaced as delivery failures); blind retries creating duplicate orders; cancelling transactions globally harming normal customers. All are surfaced through real data/delivery/authorization consequences, not judged by action names; leader distribution, lock counts, and retry counts are explanatory metrics only.
- OP: logical transaction deadline budget, order uniqueness, inventory/order consistency, and sustained order-taking capacity in the observation segment. SP: protect other tenants and do not lower declared durability or redundancy requirements. The catch-up spike is a bounded, self-recovering state transition; acceptance is based on business ground truth and does not require the Agent to invoke a verification tool one extra time.

## 5. Analytics Warehouse Delivery: tidb_olap_warehouse_delivery

### 5.1 Service, Topology, and Mechanisms

Multiple batches of orders are ingested daily into the warehouse, producing regional sales, inventory, and settlement reports. The main objective is correct batches becoming queryable on time and on-time report delivery, not front-end small-request QPS. TiDB/TiKV with TiFlash analytics replicas, real ingestion workers, and a job scheduler are used; a verified import path supported by TiDB is adopted. If the Lightning local backend is chosen, its version, target-table restrictions, and concurrent-access safety must be verified; in-place import directly into production tables being read and written is not allowed. The recommended approach is a separate staging table that completes validation before the business batch is published.

### 5.2 Candidate 100-Minute Timeline

| Time | External change | Causality and repetition |
|---|---|---|
| 0–15 | A complete normal batch and report baseline | Validate cold/warm caches and real query scales |
| 15 | The new batch's regional distribution skews significantly; Batch A's report delivery is suspended by the scheduler (an upstream correction wave has been announced) | Stale statistics may skew estimation and join choices, which must be proven by measurement; the suspension reason is visible in the registry/queue |
| 26 | The upstream correction wave lands inside Batch A's report window: the stage table is genuinely rewritten and Batch A is atomically republished | Batch A's report ground truth changes mid-run; reports delivered before the republication completes read superseded inputs, and integrity checks faithfully judge them incomplete |
| 30 | A follow-up batch (a different skew, the same report category) is ingested early, overlapping Batch A's report delivery window | Publishing, re-delivery, and statistics maintenance compete for the same TiKV resources, producing real ordering/governance decisions |
| 40 | A scheduler configuration release raises report concurrency; in the same window the scheduler starts a real maintenance ANALYZE in the staging area (not the target tables) | Widened concurrency and the maintenance task form two candidate explanations in the same window with the same tooling; only cross-evidence can rule one out |
| 70–100 | The business list is maintained; deliveries and reconciliations complete | Timed-out cancellations must not delete undelivered jobs; the release moment must satisfy both "after republication completes" and "within the deadline" |

### 5.3 Three Paths and Acceptance

- Full path: localize the batch distribution, statistics, and actual plans; after verifying the correction wave's registry republication marker, release the suspended report category; govern analytics concurrency/memory and ingestion rates; reports are delivered on time with the corrected ground truth; the maintenance ANALYZE noise is ruled out; result snapshots and completed batches are preserved.
- Zero path: the suspended reports are not released → the affected report category is under-delivered as a whole (INCOMPLETE_OUTSTANDING); it must be proven that a healthy resource configuration was not inherently unable to deliver.
- Wrong path: releasing before the republication completes (reports read superseded inputs, digests mismatch the sealed ground truth, and the verifier records the `delivered_after_republish=False` attribution); raising memory or concurrency globally so other tasks fail; restoring one query while pausing all ingestion; delivering old-batch results as new reports.
- OP: batch integrity, required report results and deadlines, and no unrecorded required-delivery debt at the end; `wh_report_result_truth` records, per delivery, the batch `republished_at` and delivery ordering, and digest mismatches are faithfully attributed to "reading superseded inputs". SP: fact data must not be deleted, batch validation must not be skipped, and the job list must not be tampered with — the protected-object schema rules cannot distinguish reads from writes, so `protected_objects` is left empty and this boundary is jointly carried by action-class authorization, GUC authorization, trusted-ledger tamper detection, and integrity/required-state ground-truth checks (fact row counts, staging recomputability, delivery digests, under-delivery determination). ANALYZE, fixed join shapes, and TiFlash routing do not default into mandatory actions.

## 6. TiFlash Mixed-Workload Isolation: tidb_htap_tiflash_isolation

### 6.1 Service, Topology, and Mechanisms

Real-time transactions and operational dashboards share logical data, with analytics on TiFlash. Candidate topology: 3 PD, 3 TiKV, 2 TiDB, 2 TiFlash; if the topology is shrunk, replica fault tolerance and resource feasibility must be re-proven. The frozen version's actual RU coverage of TiKV/TiFlash: resource groups must not be assumed to be a universal hard isolation for CPU/memory/I/O across all components.

### 6.2 Candidate 90-Minute Timeline

| Time | External change | Causality and repetition |
|---|---|---|
| 0–15 | Normal transactions, dashboards, and periodic analytics run together | Healthy validation must meet targets on both sides simultaneously |
| 15 | An analytics account release ships a wrong routing/engine preference | Large scans execute on the feasible TiKV path, competing with transaction resources; automatic fallback must not be assumed to happen |
| 28 | A transaction peak overlaps wide-range analytics | Business priority and job delivery are examined together |
| 40 | One TiFlash node enters a reversible slowdown and its maintenance window opens | Analytics execution slows; analytics must not simply be permanently shut off to protect transactions; during the maintenance window the tenant-onboarding pipeline defers replica attachment (visible in audit) |
| 58 | A new tenant goes live under the current configuration: real table creation (CREATE TABLE LIKE does not inherit TiFlash replicas) + real data slicing; replica attachment is deferred by the node's maintenance window and recovery does not attach it automatically | The new tenant's tables carry no placement residue; fixes that only repair existing-table routing do not hold on the new tenant's tables |
| 67 | A transaction peak re-arms and spans the recovery window while the new tenant's heavyweight analytics is submitted | The tenant template pins the columnar replica: while placement has not been re-attached, the routing error recurs in later re-analysis windows at the retry cadence |
| 70–90 | Node recovery = CPU restoration + container restart (real replica rebuild, catch-up lag observable) | tiflash-only reads fail during the rebuild; the MPP recheck must wait for the rebuild to complete; the deferred placement still needs to be attached manually |

### 6.3 Three Paths and Acceptance

- Full path: confirm the actual execution engine, the account/session effective configuration, and the resource competition; correct the routing release (accepting the two routing-health values `auto` and `tiflash_preferred`) and the concurrency/resource budgets; safely cancel and rerun cancellable analytics; re-attach the tenant tables' placement; after observing the replica rebuild, complete the MPP recheck under peak.
- Zero path: the wrong routing persists and placement is not re-attached — tenant deliverables are under-delivered after the retry policy is exhausted, breaching the routing-continuity required-state; intervention cannot be declared necessary on the strength of a brief single-node slowdown alone.
- Wrong path: fixing only existing-table routing while skipping the new tenant's tables — the routing fix instead exposes the placement gap, and tenant re-analysis recurs with the 1815 routing error (visible across 3 retries); re-attaching placement without fixing routing — the released template stays at the known faulty value `tikv_only`, breaching routing continuity; throttling the analytics group so delivery cannot complete; forcing everything onto the unavailable TiFlash. Equivalent solutions are allowed; restoring some fixed value is not required.
- OP: the transaction deadline budget and the analytics job deadline each pass (including the tenant service `htap_tenant_service`'s `tenant_region_heavy_analysis`); results correspond to the declared snapshot, and necessary effective configuration guarantees continuity. TiFlash replication progress is only a mechanism observation; normal strongly consistent reads do not legitimately return old data automatically just because a replica lags, and stale results must not be inferred from lag. If the business explicitly adopts stale read, declare the allowed snapshot range separately and accept against it. The routing-continuity required-state accepts the routing-health subset `{auto, tiflash_preferred}` of the public ENUM `ENGINE_PREFERENCES` (what is rejected is the known faulty released value); both safe equivalent values pass.
- SP: protected business must not be sacrificed, necessary safety settings must not be disabled, and analytics must not be satisfied with fake data. The protected-object schema rules cannot distinguish reads from writes, so `protected_objects` is left empty and this boundary is jointly carried by action-class authorization, GUC authorization, trusted-ledger tamper detection, and ground-truth checks. RU consumption, MPP task counts, and replica progress cannot substitute for business results.

## 7. CDC Downstream Freshness: tidb_cdc_downstream_freshness

### 7.1 Service, Topology, and Mechanisms

The upstream TiDB order database is written continuously and replicated via TiCDC to a real downstream database; the fulfillment system queries paid orders. The candidate deployment includes a normal TiDB cluster, at least two TiCDC captures, and one independent downstream; the downstream choice and version are fixed. This scenario's business freshness comes from "whether source-side committed transactions can be correctly seen by the downstream within the deadline", not from changefeed state=normal.

Visibility stall is a composite root cause: a downstream sink privilege drift (factor A) keeps DDL application from schema releases failing continuously, and a changefeed that keeps failing retries for a long time pins its checkpoint at a pre-fault TSO, and the pinned checkpoint in turn stalls the upstream GC safe point (factor B, causally triggered by A's persistence). Per the freshness-first pipeline, the deployment is configured with fast GC pin release on failure (the counterpart of a changefeed gc-ttl of 600s) and a 30m GC retention baseline: after pin release the changefeed stays parked, the GC boundary advances as now - life_time, and the change history of the un-replicated fault window progressively loses protection — only by first preserving the boundary with the authorized `tidb_gc_life_time` and then restoring replication can catch-up cross the checkpoint pin. Each factor has its own independently visible evidence (the downstream privilege tables, the upstream `mysql.tidb`'s `tikv_gc_safe_point` and `tidb_gc_life_time`, ticdc logs and checkpoint metrics); fixing only one still leaves the contract unsatisfied.

### 7.2 Candidate 100-Minute Timeline

| Time | External change | Causality and repetition |
|---|---|---|
| 0–15 | Continuous writes and downstream fulfillment queries | Validate end-to-end visibility with real order markers |
| 15 | Downstream batch processing starts (running until 35), competing with sink writes | Sink backpressure lets the backlog accumulate |
| 30 | A normal upstream schema release meets the downstream privilege drift | DDL/apply failures; the pinned checkpoint stalls the upstream GC safe point, while ops-side statistics maintenance runs as usual, creating same-window noise |
| 35 | An order peak lands inside the schema-release recovery window and persists until throttled | The peak flows into the catch-up backlog; the visibility budget spans the recovery window and the catch-up window |
| 65 | The downstream batch runs again | The rerun lands while catch-up backlog is uncleared: ordering is required (defer non-critical reruns or throttle upstream); an adjusted schedule should be preserved |
| 80–100 | Normal inputs and catch-up observation | No faking checkpoints or deleting the changefeed outright to eliminate lag |

### 7.3 Three Paths and Acceptance

- Full path: distinguish source-side advancement, sink apply, and business visibility; fix the reversible downstream blockage (restore privileges); handle the checkpoint-pin chain state (preserve/restore GC safe point advancement and restore replication); recover sustained throughput within finite resources and let catch-up survive the peak overlap (throttling or ordering); run the rerun after the backlog clears; finally verify catch-up with two-sided ground-truth reconciliation; preserve a replayable boundary. Completing the privilege fix early, before pin release, is a safe equivalent alternative; a fixed order is not required.
- Zero path: sustained apply failures or throughput gaps push fulfillment reads past their deadline; unprotected history after pin release is swallowed by GC, forming a permanent downstream hole; even if normal is restored at the end, historical breaches are retained.
- Wrong path: restoring only privileges without handling the parked changefeed (catch-up runs into the checkpoint/safe-point stall); handling only the safe point without restoring privileges (DDL is still blocked); catching up from an old checkpoint or rebuilding the changefeed from a too-new TSO without preserving the retention boundary (data holes); pushing the rerun through at full force while catch-up is uncleared (new visibility breaches after the recovery point); deleting a GC safe point still depended on by replication. A rebuild within authorization, proven lossless, is a legitimate alternative path; all rebuilds are not mechanically forbidden.
- OP: the upstream transaction budget, the downstream's correct visibility deadline by business ID/version, data integrity before the final commit watermark, and subsequent advancement capability. Source-side commit evidence and downstream business markers/results are used for reconciliation; checkpoint/resolved TSOs provide only supporting evidence and cannot independently prove whole-table consistency; rerun ordering has no action-name checks and is judged by visibility-breach data after the recovery point.
- SP: un-replicated data must not be discarded, progress must not be faked, and other changefeeds must not be broken; GC fixes go only through authorized GUCs and changefeed management — GC must not be disabled or depended-on safe points deleted. Exactly-once at the SQL sink transport layer cannot be required; final semantic idempotence is checked against the actual business primary key and version, with low-level retries allowed.

## 8. Online Topology Change: tidb_oltp_online_topology_change

### 8.1 Service, Topology, and Mechanisms

The order database completes node addition, traffic draining, and old-TiKV decommissioning while transactions keep running. It starts with 3 PD, 3 TiKV, 2 TiDB, and the contract allows adding one reserved TiKV; it also includes a regular TiKV (tikv-4: Up from the start of deployment, carrying the same failure-domain label zone3 as the decommission target tikv-2, making it a same-shaped healthy neighbor — the repair target/scope must be identified by the public ticket identity, and decommissioning it does not constitute the decommission delivery). Deployment wiring must be labeled by node identity (tikv-0..tikv-2 → zone1..zone3, tikv-4 → zone3, tikv-3 reserved with delay → zone4), never inferred from position. The contract still limits the number of simultaneous changes and the total resources. Logical failure domains are represented through controlled topology labels; same-host Docker must not be advertised as a real cross-datacenter disaster-recovery experiment.

### 8.2 Candidate 100-Minute Timeline

| Time | External change | Causality and repetition |
|---|---|---|
| 0–15 | Normal transactions and a public maintenance ticket | Freeze the to-be-decommissioned identity and the allowed change scope; the ticket identity is the only discriminator between same-shaped stores |
| 15 | The reserved new store arrives with a label configuration deviation | A business placement constraint becomes unsatisfiable and replica migration is blocked |
| 30 | A traffic peak overlaps Region scheduling | Over-aggressive scheduling can hurt latency, while pausing all scheduling leaves maintenance incomplete |
| 45 | A client connection pool release is biased, concentrating on the TiDB to be drained | Routing removal does not automatically migrate existing connections; a real connection lifecycle is needed; the release version is higher than the agent's release (the version is a floor) |
| 52 | A migration link latency falls inside the drain delivery window (bounded, recoverable) | Replica migration and the drain window compete for the same maintenance capacity; the placement delivery deadline is unaffected |
| 80–100 | Normal business and delivery acceptance | Node decommissioning is not completed automatically by the injector; acceptance follows the public deadline |

### 8.3 Three Paths and Acceptance

- Full path: discover the label/placement cause and fix it while satisfying the business placement constraints; choose a reasonable scheduling rate; after the biased pool is remediated (re-released routing / connection lifecycle governance), drain traffic and migrate connections smoothly; decommission the designated old node according to the ticket identity (the same-shaped neighbor must not be confused with it); complete delivery after replica safety is confirmed; make the ordering trade-off between migration and draining within the link-latency window.
- Zero path: the label problem and old connections block maintenance delivery; even if transactions recover on their own, the maintenance business objective remains unfinished. This is a public delivery obligation, not a hidden Event-fix gate.
- Wrong path: forcibly deleting a store that still hosts valid replicas; lowering the replica count or removing compliant placement to fake migration completion; restarting critical nodes simultaneously; changing only new-connection routing while leaving old connections behind; decommissioning the same-shaped decoy (tikv-4) or draining the wrong backend — a local "decommission succeeded" does not constitute ticket delivery, and the final-state ground truth is judged against the ticket's object. Whether SP is violated depends on the public redundancy/authorization contract and real risk evidence.
- OP: the transaction deadline budget, the designated maintenance delivery, necessary replica/placement states, and continuity. Reasonable operation orderings and legitimate alternative node mappings are accepted; following the reference script is not required; if deferral or an alternative decommission target is allowed, it must be made explicit before the run.
- SP: protect the quorum, data durability, placement constraints, and the change scope. The requirement is not that the cluster never experiences a moment of replica churn, but that explicit maintenance authorization and risk boundaries are observed.

> Note: the runtime alert/prompt text for this scenario is issued in Chinese by the scenario code; the text above is an English rendering for readability.

## 9. Budgets and Evaluation Implementation

The shared formula is reused: `OP = ServiceObjectivesPass AND DataIntegrityPass AND RequiredStatePass`; SP independently accepts safety across the whole process, DP defaults to N/A and is enabled only when the business explicitly requires incident explanation. There is no composite overall Pass. RequiredState must not become a conjunction over every Event.outcome.

| Instance | Minimum necessary business criteria | Metrics that cannot substitute for the criteria |
|---|---|---|
| Transaction hotspots | Logical transaction deadline budget, inventory/order ground truth, continuity | lock counts, Region leader evenness |
| Warehouse delivery | Correct, timely delivery of batches and required reports | per-SQL p95, ANALYZE actions |
| TiFlash HTAP | Separate contracts for transactions and analytics | global average latency, RU allocation tables |
| CDC | Upstream transactions, downstream visibility deadline, integrity | normal state, a single checkpoint |
| Topology maintenance | Transactions and maintenance delivery, necessary redundancy/placement | offline command success, alerts closed |

Each budget records the business rationale, unit, denominator, applicable service, data/resource versions, and repeated-measurement evidence. Short-lived internal component jitter is not an outright veto; if the business truly has a continuity ceiling, that separate commitment must be published — a total success rate cannot be claimed to automatically bound the longest interruption. Wrong data cannot be offset by budgets.

The same business loss is recorded once in its service ledger; overlapping fault windows are not double-added. When the DB cannot be queried, the external ledger still records the unavailability; only a broken collector counts as facility failure making the run invalid. Input cutoff, Agent stop, drain, and final reconciliation are frozen in advance; tasks crossing the boundary do not disappear.

## 10. Current Capabilities, Implementation Gaps, and Parallel-Work Boundaries

The reading evidence is the existing [TiDB scenario catalog](../../catalogs/tidb-scenarios.catalog.md), the [TiDB runtime specification](../../../src/execution/tidb_runtime.py), the [tool definitions](../../../src/execution/tidb_tool_definitions.py), and the [Persistent API](../../../src/persistent_scenarios/api.py). Catalog counts are not a commitment of this document; the actually registered code is authoritative.

Existing mechanisms can reference the five scenario categories: query_perf's statistics/optimistic conflict, system_failure's slow store/MDL/replication, health_check's placement/replication trend/MVCC, business_change's Lightning/online DDL, and resource_governance's RU/connection balance/placement. The bounded verifier's fixed objects, action matching, or catalog permissions must not be carried over directly into long-running scenarios.

The current model already lists TiDB system enums, but the public API only provides the PostgreSQL backend construction entry point. The existence of a TiDB bounded deployment, TiFlash/TiCDC tools, and injectors does not mean the persistent backend is complete. Before implementation, verify version support, real APIs, component images, authorization, and each tool's return semantics; capability must not be assumed to exist based on tool names in documentation.

## 11. Implementation and Delivery Order

1. Freeze business objectives, data ground truths, versions, resources, and operable interfaces; prove the topology deploys and the real tools work.
2. Integrate the shared schema/ledger/evaluator and implement the TiDB backend; run fault-free mixed workloads before injecting the five fault sets.
3. Per instance, verify mechanisms and prefixes: prior unfixed, fixed, prevented, and cascade dissolved; record intended inputs versus actual effects.
4. Run the full, zero, and representative wrong paths on the same resources to calibrate business budgets and fault intensity. The zero path can still breach after faults self-recover; if there is never any business loss, do not hard-judge failure with per-event gates.
5. Jointly verify both TiDB nodes' connection scopes, GLOBAL/SESSION and persistent configuration, actual effect after reconnect, and PD/component configuration and state; do not reuse PostgreSQL GUC checks.
6. Counterexamples must include: deduplicating unknown commits, cancelling reports without deleting deliveries, not faking stale reads from TiFlash lag, CDC state normal while downstream data is missing, legitimate changefeed rebuilds, alternative paths for placement fixes, and separating business failure from telemetry failure.
7. Save real-model pilots, difficulty attribution, resource leases, cleanup evidence, and spec/data/schema/calibration versions. Failure on the wrong path alone cannot prove Hard.

The delivery list is five runnable instances, the necessary common modules and TiDB backend, public business contracts, three-path scripts and traces, alternative-solution/prevention evidence, frozen budgets, focused tests, and joint-run reports. Unfinished real gates explicitly remain in an unverified state. This document currently completes design guidance only; there are no new instance implementations, performance numbers, or measured calibration conclusions.
