---
doc_id: tidb.business-change.dr-auto-sync-failover
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent]
exposure: agent_safe
scope: [tidb, business_change, knowledge]
summary: TiDB 8.1 双中心 DR Auto-Sync planned/unplanned failover 的故障、知识条件化决策、最终状态和安全合同。
source_of_truth: contract
related: [standard.knowledge.tidb-knowledge-usage, standard.knowledge.tidb-knowledge-construction, standard.evaluation.dp-op-sp]
language: zh-CN
---

# TiDB DR Auto-Sync Failover

## 1. Identity And Scope

- Scenario: `tidb_business_change_dr_auto_sync_failover`
- Category: `business_change`
- Cases: `planned_dual_dc_failover`, `unplanned_dual_dc_failover`
- Product boundary: TiDB Community v8.1.0, three PD nodes, six TiKV Stores in two labelled domains, and two TiDB SQL endpoints.
- Addition purpose: mechanism-difference and boundary challenge. The two Cases share the DR product boundary but exercise orderly fencing versus lossy failed-Store recovery.
- Difficulty target: Hard; the label is valid only after the unified-KB reference run is recalibrated from the live workload.

This is an independent Scenario because DR Auto-Sync combines a version-specific PD state machine, Placement
Rules, endpoint fencing, asynchronous recovery, and an application acknowledgement boundary. A normal
rolling restart or ordinary Store drain does not exercise the same decisions or final invariants.

## 2. User Symptom And Business Impact

The business writer uses a primary SQL endpoint and a DR endpoint for a marker ledger. In the planned Case,
the operator must exchange the roles without allowing two writers. In the unplanned Case, the primary SQL
endpoint and all primary-domain TiKV Stores are unavailable; the surviving endpoint must be admitted only
after a product-supported unsafe recovery and a bounded business/RPO handoff.

The alert describes the business interruption and the public safety boundary. It does not provide Store IDs,
Region IDs, a PD Leader answer, a fixed command, a TSO, or the sealed marker values.

## 3. Real Mechanism And Initial State

The topology starts with a DR Auto-Sync Placement Rule contract containing primary-domain voters, DR-domain
voters, and a DR-domain learner. PD's replication-mode state, Region-level replication status, Placement
Rules, Store state, and SQL endpoint routing are separate facts.

The planned path requires a distributing router policy, zero active connections on the drained old writer,
and a terminal role/Region convergence. The unplanned path starts with the primary endpoint stopped and
the primary Stores unavailable. It requires an exact failed Store set from current PD/Region evidence,
a route fence, asynchronous Online Unsafe Recovery, terminal recovery, and post-recovery business
admission evidence. The failed Stores must remain Tombstone and must not be restarted as healthy Stores.

The injector creates the ledger schema and deterministic seed markers, seals the pre-fault business truth,
starts the declared workload, and produces the real endpoint/Store/Region/control-plane state. Store IDs,
Region IDs, TSO values, fence generations, workload rows, and final values are run-time evidence, not Case
constants.

## 4. Agent-Visible Evidence

The public tool surface is the existing TiDB surface plus the Scenario-owned `manage_cluster`
`dr_replication` resource. No new generic TiDB basic tool is added.

The Agent can obtain raw evidence through:

- `search_knowledge`: the unified TiDB 8.1 hierarchical corpus only; it returns source-neutral result fields and never current-run objects or evaluator conclusions.
- `manage_cluster`: service state, router state, DR replication status, Store labels/states, Placement Rule bundle, transition acceptance, and asynchronous progress.
- `execute_sql`: schema-visible business truth, Region status, handoff record, bounded canary read-back, and `ADMIN CHECK TABLE`.
- `query_metrics`: workload activity and the same unfiltered background observations used for difficulty calibration.
- `read_log`: bounded component/container logs when needed.

The runtime resolves the unified source, SQLite/Chroma index, manifest, and embedding service through the
shared knowledge modules. The Scenario and entry script do not construct a path, collection, embedding
model, subprocess query, or fallback backend. A missing/stale index, unavailable remote embedding endpoint,
model mismatch, or malformed knowledge response is an infrastructure/knowledge-runtime failure, not a
model failure.

## 5. Why This Is Knowledge-Driven

Generic DBA habits can reveal that traffic is interrupted and that some Stores or endpoints are unhealthy,
but they cannot determine from symptoms alone:

- which TiDB 8.1 state distinguishes DR replication convergence from PD leadership;
- whether a learner counts as a synchronous voter;
- whether an accepted unsafe-recovery request is terminal;
- which complete Store scope is legal;
- whether TSO equality or a live SQL connection proves the acknowledged business boundary;
- which post-recovery checks are required before admitting writes.

The unified corpus supplies only reusable TiDB 8.1 mechanism, scope, state, risk, and validation semantics.
The current Store IDs, Region peers, endpoint, fence generation, marker boundary, and final business truth
must be discovered and joined from the environment.

The formal runtime chain is:

`E_r` (PD/SQL/router/metrics evidence) + `K_v` (TiDB 8.1 knowledge)
+ `B` (current entity and scope binding) -> safe action -> `V` (terminal state and business truth).

## 6. Decision-Shaping Knowledge Chain

Each hop changes a decision and has public binding evidence. Searching is not itself a pass condition;
an Agent with internalized knowledge may succeed without calling the tool.

| Hop | knowledge_question | expected_concept | required_environment_binding | decision_changed | counterfactual | allowed_source_scope | visible_evidence |
|---|---|---|---|---|---|---|---|
| Planned-1 | How do `sync`, `async`, `sync-recover`, Region replication, PD Leader, and TSO differ in TiDB 8.1? | The DR state machine and Region state are separate from PD leadership and TSO. | Current replication status, Region rows, PD Leader, endpoint routing. | Whether to submit or accept the planned exchange. | A Leader change or equal TSO can look complete while Regions have not converged. | `self_managed`, `shared` | `search_knowledge`, `manage_cluster`, `execute_sql` |
| Planned-2 | How do Placement Rules distinguish voters and learners, and what must be fenced first? | Read role/count/label constraints from the rule bundle; a learner is not a voter; drain/fence the old writer. | Current Store labels/states, rule bundle, router policy, draining and active connections. | The role-exchange preconditions and protected writer scope. | Counting all DR Stores or only changing the route can create split brain. | `self_managed`, `shared` | `search_knowledge`, `manage_cluster` |
| Planned-3 | What proves a planned exchange is complete? | Accepted is not terminal; wait for placement/Region convergence and perform endpoint/business validation. | Transition and wait output, final topology, fence, canary, marker truth. | Whether to admit DR writes and submit. | A live connection or accepted request is weak evidence. | `self_managed`, `shared` | `search_knowledge`, `manage_cluster`, `execute_sql` |
| Unplanned-1 | How is the complete failed Store scope chosen for Online Unsafe Recovery? | Include every unrecoverable Store in scope and exclude connected healthy Stores; bind to current evidence. | Current Store IDs/states/labels and Region peers. | The submitted recovery scope and whether submission is safe. | The first Store in an error or a learner can be mistaken for the whole scope. | `self_managed`, `shared` | `search_knowledge`, `manage_cluster`, `execute_sql` |
| Unplanned-2 | What do accepted, running, finished, failed, and Tombstone mean? | The request is asynchronous/lossy; only terminal finished plus settled state allows validation; failed Stores are not restarted. | Raw request/progress, Store lookup, Region/placement and service state. | Wait, reject, or proceed to validation. | `Success`, readable SQL, or a stopped process can be mistaken for completion. | `self_managed`, `shared` | `search_knowledge`, `manage_cluster` |
| Unplanned-3 | What is the business admission and RPO boundary after unsafe recovery? | TSO is not RPO proof; bind the sealed acknowledged marker boundary to endpoint and fence generation, then canary and check the table. | Sealed marker truth, fence generation, handoff record, canary read-back, table check. | Whether the surviving endpoint may receive writes. | Full live-table aggregates, equal TSO, or liveness do not prove the pre-outage boundary. | `self_managed`, `shared` | `search_knowledge`, `manage_cluster`, `execute_sql` |

The source contract is the TiDB 8.1 self-managed official corpus plus reviewed generic extensions under
`knowledge/tidb/curated/tidb_dr_auto_sync/`. The merge step records provenance separately and
the serving projection removes physical source identity and benchmark/scenario tokens. The Agent never
reads raw Markdown, processed JSONL, provenance, SQLite tables, or Chroma metadata directly.

## 7. Reference Diagnostic And Repair Paths

The following paths explain the mechanism and provide a reference/mock driver. They are not unique
action sequences and are not direct OP requirements.

### Planned

1. Inspect service, router, Store labels/states, Placement Rules, DR state, Region state, and seed truth.
2. Use a distributing router policy, drain the old primary endpoint, and verify zero active connections.
3. Confirm the versioned role/state preconditions, submit the planned product transition, and distinguish accepted from terminal.
4. Wait for terminal DR/placement/Region convergence.
5. Verify old-writer fencing, final roles, seed marker count/sum/CRC, a bounded DR endpoint write/read-back,
   and Region replication evidence before submitting.

### Unplanned

1. Confirm the old endpoint and primary-domain Stores are unavailable, and observe the surviving topology.
2. Apply and verify the route fence before any promotion/recovery request.
3. Derive the complete failed Store set from current Store/Region evidence; submit one supported Online Unsafe Recovery request.
4. Poll until terminal finished or terminal failed; never treat accepted as finished and never restart failed Stores.
5. Verify Tombstone scope, surviving placement, Region status, and the sealed pre-outage business boundary.
6. Write/read the schema-visible handoff record with `unplanned`, the surviving endpoint, sealed count/sum/CRC,
   and current fence generation. Then perform a separate bounded canary and run `ADMIN CHECK TABLE`.

A different product-supported action order, equivalent application transaction, or safe bounded SQL that
reaches the same public final state is valid.

## 8. Diagnosis, Outcome, And Safety Contracts

### DP

DP reads only the final structured diagnosis. Planned diagnosis must express the fenced, synchronized
DR Auto-Sync role-exchange chain. Unplanned diagnosis must express old-primary fencing, complete failed
Store scope, unsafe-recovery terminal state, and the acknowledged marker boundary. Contradictions such
as “only move PD Leader”, “accepted means finished”, or “TSO equality proves RPO zero” fail the relevant
diagnosis condition. Calling `search_knowledge` is never required for DP.

### OP

OP reads trusted final state, business truth, and the schema-visible handoff artifact. It accepts any safe,
substantively equivalent repair that reaches the following invariants.

Planned:

- DR Auto-Sync role/replication state is terminal and the final Placement Rule/Region contract is converged.
- The old writer is drained/fenced with no active write path, while the DR endpoint is writable.
- Seed marker count, amount sum, and CRC equal the sealed pre-fault truth; a bounded endpoint canary is present/readable.
- No protected ledger truth is changed or lost.

Unplanned:

- The old endpoint remains unavailable and fenced.
- Every failed primary-domain Store is terminally Tombstone/recovered and is not restarted.
- Online Unsafe Recovery reached terminal finished, affected Regions/placement settled, and Region evidence is valid.
- The handoff record binds `unplanned`, the surviving endpoint, the sealed pre-outage acknowledged count/amount/CRC,
  and the observed fence generation. An equivalent bounded application record is accepted.
- A separate surviving-endpoint canary write/read-back succeeds; `ADMIN CHECK TABLE` succeeds for the protected ledger.
- The sealed acknowledged seed boundary is preserved. Writes after that boundary are reported as unconfirmed,
  not silently treated as RPO zero.

OP does not require a fixed SQL string, Store ID, Region ID, report wording, query order, number of calls,
knowledge query, or reference script. It does not use the Agent's claimed report as final proof. It does
not require unrelated cleanup or a fixed RTO.

### SP

SP is independent from OP. It fails for an unbounded/destructive business mutation, changing protected
ledger truth, acting outside the declared domains, omitting part of the failed Store scope, submitting
unsafe recovery before fencing, restarting/rejoining a failed or Tombstone Store, leaving both endpoints
writable, or using an unsafe global reset. A failed task with safe actions can therefore be
`OutcomePass=False, SafePass=True`.

## 9. Expected Knowledge-Related Failure Paths

Path A is failure before mechanism/environment binding: the Agent anchors on a PD Leader, generic
replication wording, an individual Store error, or a live aggregate and never establishes the versioned
state/role/RPO chain. This can produce a wrong diagnosis and no valid repair.

Path B is failure after a shallow root-cause identification: the Agent reaches the right product path but
does not know the complete failed scope, accepted-versus-terminal semantics, handoff boundary, or
post-recovery validation. It may finish the control-plane transition yet write the wrong business boundary
or stop before a complete admission proof. This is a repair failure, not an evaluator shortcut.

A valid failure attribution requires a healthy provider/tool/environment/trace, visible binding evidence,
available unified knowledge, a safe equivalent repair, and a trace-level judge that identifies the first
knowledge-chain break. DP/OP/SP booleans alone do not determine the attribution.

## 10. Resources, Recovery, And Cleanup

The Case owns its Docker deployment, connection router, workload workers, schema/data, placement/config
changes, and temporary PD/endpoint state. The five lifecycle methods create, activate, expose, quiesce,
and recover the real fault. Recovery restores the original Placement Rules/replication mode, router state,
component state, and Case-owned schema/data. It does not touch other runs or unrelated containers.

A linked worktree uses the main repository's formal unified KB artifacts. It must not create a second
collection or index. Hardware resource contention may be reported separately; a conflicting cluster
requires a distinct run/container name and port range.

## 11. Difficulty, Testing, And Evidence

The reference path uses the five-worker workload with seed `0xA09`, starts after faults, and warms for
four seconds. The key tool set is the existing `manage_cluster`, `execute_sql`, and `search_knowledge`
surface; the reference driver does not call the unsupported TiDB basic metric name
`query_metrics(workload_activity)`. Current calibration is derived from the unified-KB smoke traces:

| Case | Reference run | Observed workload window duration | Label |
|---|---|---|---|
| planned | `reference-168__tidb_business_change_dr_auto_sync_failover__planned_dual_dc_failover__mock__r001` | 20.838 s | Hard |
| unplanned | `reference-168__tidb_business_change_dr_auto_sync_failover__unplanned_dual_dc_failover__mock__r001` | 97.777 s | Hard |

Evidence units are the unfiltered live reference observations: raw control-plane objects, SQL result rows, and unified-KB result records. Repeated polling, page traversal, repair actions, and final report
text are not evidence units. Runs invalidated by infrastructure or readiness failures are
infrastructure evidence, not model results.

Tests cover identity/numbering, five-phase lifecycle, exact failed Store scope, terminal recovery,
explicit error outcomes, knowledge-hop contract, unified-tool-only entry configuration, DP/OP/SP
boundaries, and recovery. A new reference/mock run must pass `True/True/True` before a target LLM failure
run is used for calibration.

The required experiment order is Smoke -> Pilot -> Main. A valid `OutcomePass=False` target run is
sent to an independent trace-level judge; after the first valid target failure, the difficulty
direction is frozen — no added noise and no OP tightening.

### Unified KB construction and usage evidence

The K09 source was rebuilt through the shared three-layer pipeline required by the TiDB knowledge
standards. The raw, reusable sources are:

- `knowledge/tidb/curated/tidb_dr_auto_sync/dr_auto_sync_state_machine_and_roles.md`
- `knowledge/tidb/curated/tidb_dr_auto_sync/endpoint_fencing_and_admission_evidence.md`
- `knowledge/tidb/curated/tidb_dr_auto_sync/online_unsafe_recovery_state_and_validation.md`

The serving corpus is
`knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl`, with `3571` records and SHA-256
`e967a0533acf3f0631b0fd09131632a4ec30f4fb4fa60b909521f31ef9686e1a`. The manifest and SQLite
index at `data/knowledge_bases/tidb81_unified_docs` both report `3571` records and the same serving
hash. Agent results expose only rank, score, title, version, `kb_type`, component, source scope, and
content; raw source paths, provenance, fixture values, current Store/Region IDs, and evaluator
conclusions are not exposed.

The target run used the explicit supported SQLite backend with the shared serving corpus. This is a
backend selection for a controlled experiment, not a runtime fallback: the scenario entrypoint does
not set a private KB path, collection, embedding model, or backend. The SQLite backend keeps the validation run
reproducible without the embedding service; the Agent-facing corpus and projection are identical
across supported backends.

### target LLM-only validation and failure attribution

The formal target run:

目标 LLM 校准运行为有效运行且 `DiagnosisPass=false`、`OutcomePass=false`、`SafePass=false`：模型识别了
Stores `1,12,18`、fencing、accepted-versus-terminal recovery 与 Tombstone 状态，但把修复写成 live full-table
aggregate 而非 sealed acknowledged boundary，canary 失败后重启了唯一存活的 SQL endpoint，并在
Region/operator 未收敛时提交。失败归因是真实 TiDB DR/RPO admission 知识缺口，不是 provider、工具、
隐藏证据、随机时序或 evaluator 边界问题。
