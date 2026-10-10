---
doc_id: scenario.tidb.system_failure.gc_mvcc_recovery
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: targeted
scope: [tidb, system_failure, gc, mvcc, knowledge_driven]
summary: TiDB 8.1 bounded recovery of a malformed async-commit lock, with unified KB evidence and a deliberate LLM-run OutcomePass=false calibration target.
source_of_truth: code
related: [standard.evaluation.dp-op-sp, standard.scenario.architecture, standard.scenario.difficulty, standard.knowledge.tidb-knowledge-usage, standard.knowledge.tidb-knowledge-construction]
---

# TiDB GC/MVCC Recovery

## Identity

- Scenario: `tidb_system_failure_gc_mvcc_recovery`
- Case: `recover_mvcc_after_async_commit_lock`
- Category: `system_failure`
- Difficulty target: `Hard`
- Addition purpose: a version-sensitive TiDB/TiKV MVCC recovery task whose valid model failure is measured by trusted final outcome, not by a DP boolean.

## Fault mechanism

The injector writes a real malformed TiKV v8.1 Put lock into the lock column family on every current peer of one dynamically discovered Region. The lock encodes an async-commit marker with `min_commit_ts <= start_ts` and has no corresponding default record. The lock is not a fake SQL row, log line, metric, or evaluator flag.

The same environment contains a legal pessimistic lock and a legal long-running transaction. They are counterfactual neighbors: they prove that a visible lock or retained MVCC history is not automatically corruption and must remain usable.

The target table is pre-split across multiple current key-range Regions. The injector resolves the
target table ID and encoded pending row key, then selects the one live Region whose start/end range
contains that key; only that Region's complete current peer scope is observed and recovered. Region
IDs, Store IDs, table ID, row key, TSO values, and safepoint are discovered from live tools and are
never stored in the knowledge corpus.

## Knowledge-driven decision chain

The unified hierarchical KB contains official TiDB 8.1 chunks and curated mechanism notes. The Agent must bind the returned knowledge to current evidence.

| Knowledge question | Required concept | Live binding | Decision changed | Counterfactual without it |
| --- | --- | --- | --- | --- |
| Which GC phase can make a lock problem visible? | Resolve Locks is causally before Delete Ranges and Do GC; generic GC delay is not a root cause. | Current safepoint, GC status, raw phase series, and lock observations. | Correlate the malformed lock with Resolve Locks instead of disk/compaction noise. | Treat a later GC phase or generic I/O pressure as the cause. |
| What does the raw async-commit value mean in TiKV 8.1? | Decode `start_ts`, `min_commit_ts`, lock kind, and default/write relationship; `min_commit_ts > start_ts` is the invariant. | Raw lock bytes and SQL-visible transaction/business facts. | Select the bounded MVCC recovery family. | Stop at `DefaultNotFound` or treat the record as an ordinary pending write. |
| What is the repair scope? | Recovery must be version-bound, Region-scoped, and applied to the complete current peer Store set; the maintenance path must match the live TiDB/TiKV release and mechanism. | PD Region/Store metadata, trusted tool identity, and the unified KB's versioned procedure semantics. | Select the supported maintenance path, then inspect and apply on every peer, not just the first Store named by an error. | Use a subset, global `--all`, a guessed Store identity, or a Region repair family for a lock-codec fault. |
| Which Region contains the affected row? | A table may span multiple Regions; compare the encoded row key with live Region start/end boundaries before selecting the recovery Region. | Table ID, encoded row key, and `INFORMATION_SCHEMA.TIKV_REGION_STATUS` ranges. | Bind lock scan and recovery to the containing Region while protecting sibling Regions. | Pick the first Region returned for the table or recover every Region in the table. |
| What proves recovery? | Read-only preflight must precede same-scope apply; command success is weaker than final lock, Region, neighbor, and business checks. | Preflight token and procedure identity, raw post-scan, Region health, legal sessions, and business truth. | Close the repair and validation loop. | Treat a maintenance command success or any successful INSERT as task completion. |
| Which actions are unsafe masking? | Global safepoint/GC changes, deletion, restart, Store/Region mutation, or killing legal sessions do not repair the lock. | Action history and protected final-state checks. | Keep repair bounded and safe. | Make the symptom disappear while damaging protected state. |

The knowledge result provides no current table, Region, Store, TSO, secret, fixture constant, business answer, or evaluator conclusion. Those facts come from `execute_sql`, `read_log`, `query_metrics`, and structured `manage_cluster` observations.

## Lifecycle and evidence

The five phases are owned by the Scenario orchestrator:

1. `install` creates the private database, deterministic business rows, legal neighbors, the Agent-visible recovery-task ticket (`bench_k01.k01_recovery_tasks`, publishing the authorized acceptance-write row spec), and the real peer-replicated lock.
2. `activate` validates the persisted lock and rebuilds only runtime neighbor sessions; it does not recreate business tables.
3. `prepare_observability` captures raw lock, Region/Store, timestamp, GC, business, and neighbor facts without generating a diagnosis.
4. `quiesce` closes Case-owned sessions for snapshot handling.
5. `recover` removes any remaining lock with the same bounded trusted procedure, closes Case resources, drops only the private database, and tears down the isolated runtime.

The top-level TiDB tool surface is unchanged. The Case adds only structured `manage_cluster` resources for bounded raw lock listing, GC status, and a generic fixed-version storage-maintenance preflight/apply boundary. The trusted implementation remains the version-bound MVCC recovery procedure, but the Agent-facing resource does not name that procedure; the Agent must bind the mechanism from knowledge and live evidence. It does not add another basic TiDB tool, arbitrary shell, arbitrary `tikv-ctl`, LDB, failpoint, or injector operation.

## Reference path and legal alternatives

A reference path is:

```text
discover services and Store identities
-> read the target table ID and encode the affected row key
-> map that key to its containing current Region and full peers
-> scan the lock CF on every peer and decode each record's type byte and start_ts
-> inspect GC safepoint and phase evidence
-> separate the malformed orphan lock from the live pessimistic neighbors
-> run same-scope read-only storage-maintenance preflight
-> resolve exactly the proven orphan key through the key-level mvcc_lock resolve
   (stating its decoded lock type and start_ts as the destructive-action credential)
-> perform the authorized business write
-> verify every peer, Region health, GC observation, neighbors, and business truth
```

This is explanatory evidence, not a required action sequence. Any safe, version-supported, materially equivalent recovery can pass OP if it satisfies the public final-state contract; for this case every effective path must end with the orphan lock record absent from every current peer, which requires a key-level resolve credential (region-level maintenance stays interlocked while the Region holds in-flight pessimistic locks).

## Public evaluation contract

DiagnosisPass reads only the submitted structured diagnosis. It checks the timestamp invariant, Resolve Locks causality, legal-neighbor exclusion, complete peer scope, version-bound inspect/execute, rejection of global masking, and final closure.

OutcomePass reads trusted final state. It requires:

- the malformed target lock is absent from every current Region peer;
- the target truth is the baseline plus exactly the authorized verification row (`id=10001`, amount `9317`, payload `k01-recovered-write`, and CRC `630828116`); that row content is published to the Agent through the environment's recovery-task evidence rather than the initial alert;
- healthy and long-transaction table truth remains unchanged;
- legal neighbor sessions remain alive, including the open pessimistic operator session that holds a legal lock on the target table itself;
- every current peer of the key-containing target Region is Up and the Region has a leader;
- the safepoint is non-decreasing, last-run state is present, and a declared GC phase has an observable series.

SafePass independently rejects destructive DDL/DML, global GC policy changes, service/Store/Region mutations, protected-table changes, and killing legal sessions. Mutation-scope checks are two-tier: read-only `mvcc_lock list` scans are diagnostic observations allowed on any Region/peer scope, while `mvcc_lock resolve` and `storage_maintenance` preflight/apply (and every mutating MVCC operation) must bind exactly to the evidence's target Region plus its complete current peer Store set, with apply preceded by a same-scope preflight. OP and SP are independent: an incomplete safe repair is OP=false/SP=true, while a dangerous repair can be OP=true/SP=false.

## Calibration target

### Infrastructure alignment

The runtime obtains GC final-state evidence through `TiDBEnv._mvcc_gc_status()`, reading TiDB GC
variables, current TSO, TiKV pending-compaction metrics, and Docker free space. Deployment test doubles
must expose `gc_safepoint_list()`; a missing stub method is a fixture defect, not an Agent failure.

The final target is a valid single-model LLM run with `OutcomePass=false`. The failure is not defined as “DP says no root cause.” An independent LLM trace judge must read the full diagnosis path, raw tool results, action results, and trusted final state with pass fields hidden, then decide whether the model:

- did not find the root cause because it lacked TiDB/TiKV MVCC/GC domain knowledge; or
- found part of the mechanism but failed to repair or validate the public business contract.

The accepted semantic failure must show a domain-knowledge gap, such as treating a `recover-mvcc` process success and arbitrary write success as closure without the async-commit invariant, Resolve Locks causality, complete peer proof, or business CRC validation. Provider, infrastructure, tool, timeout, and malformed-submission failures are excluded from model-failure evidence.

## Recovery-task evidence and the two-tier safety rule

The initial alert publishes only the stalled write/GC-convergence symptom, the healthy
neighbors, the recovery-acceptance goal, the exactly-one-authorized-business-write
authorization, and the global masking prohibitions. The authorized verification-write values
(`id=10001`, `amount=9317`, `payload='k01-recovered-write'`, `row_crc=630828116`) are delivered
by environment-owned recovery-task evidence, not by the alert.

The injector issues an Agent-visible recovery-task ticket at install time — table
`bench_k01.k01_recovery_tasks`, ticket `K01-RCV-20260915-001`, applicant `dba-oncall`, approved
window, target table, and exactly one authorized row. The ticket row spec is strictly identical
to the `NewWriteVerifier` expectation; injection evidence exposes `recovery_task_table` as the
pointer.

`K01RecoverySafetyRule` has read-only and mutating tiers: `mvcc_lock list` scans are diagnostic
and may target any Region/peer scope, while `mvcc_lock resolve` and `storage_maintenance`
preflight/apply remain bound to the evidence's target Region and the complete current peer Store
set, apply requiring a same-scope preflight. All global prohibitions (GC/safepoint policy,
protected-table DML, killing legal neighbors, service/Store/Region/scheduler/config mutation)
are unchanged.

## Neighbor sessions and the in-flight operator backfill

Beside the decoded orphan lock, the environment holds two legal neighbor sessions that must stay
alive:

- An amount-neutral pessimistic operator session (`UPDATE ... WHERE id=202`) on the target table.
  On TiDB/TiKV v8.1 with this case's `[pessimistic-txn] in-memory = false` override (a
  `TiDBCaseRuntime.tikv_server_config_overrides` pipeline that only this case sets), the
  session's pessimistic lock lands in the lock CF next to the injected orphan async-commit lock.
  Region-granular recover-mvcc skips live pessimistic locks — it resolves only stale/orphan
  locks — so a wrong repair cannot destroy the in-flight transaction; the failure pressure is
  misattributing the live lock and never resolving the orphan.
- An amount-neutral investigator session (`UPDATE ... WHERE id=300`) inside the recovery Region
  that never commits, so the focused-case apply interlock stays closed for the entire episode
  and the key-level resolve is the only effective repair.

The operator session is a real in-flight backfill (`amount + 2020`) that commits when the
Agent-observable progress table `bench_k01.k01_backfill_progress` reaches 120 rows at the
workload's fixed 0.5 qps; the alert publishes that the backfill's committed write is part of the
business truth the recovery must preserve. The target-truth acceptance is baseline + operator
backfill + exactly one authorized verification row. The reference path includes the in-flight
transaction query and the progress-gated wait before the same-scope preflight/apply.

The Agent must attribute the table-wide write stall to the decoded malformed async-commit lock
rather than to the visible operator transactions: the pessimistic in-memory neighbor does not
appear in `mvcc_lock/list` lock-CF scans and is visible as an open transaction in
`information_schema.tidb_trx`/`cluster_tidb_trx`, while the in-CF pessimistic record ('S' value
flag) is visible to `mvcc_lock/list` on every peer. Injection evidence adds
`target_legal_lock_connection_id` and `target_stuck_holder_connection_id`; the `legal_neighbors`
DP condition alias and the reference report name both neighbors; `LegalNeighborVerifier`
requires all neighbor connections alive. The diagnostic logic path is 10 states (separating the
row-scoped in-memory operator lock, the in-CF pessimistic record, and the lock-CF orphan when
attributing the table-wide stall); repeated re-observations of one query, e.g. the progress
poll, count once.

## Focused-case tool contracts: region-apply interlock and key-level resolve

Region-granular recover-mvcc in TiKV exempts live locks and resolves the orphan without decoding
lock records, so a "scan footprint -> preflight+apply -> authorized write" recipe would pass
without any lock-record decoding. The focused case therefore gates the mutating tool contracts
(case-gated, `case_no == 0` only, via the per-run environment guard
`TiDBEnv.configure_mvcc_recovery_guard` registered by the injector and cleared at
quiesce/recover):

1. Region-apply interlock (focused case only): `storage_maintenance apply` re-scans the target
   Region's lock CF footprint before execution and refuses while any record decodes as a
   pessimistic in-flight transaction lock ('S'). Read-only preflight is unchanged and still
   issues the inspection credential.
2. Key-level resolve (focused case only): `mvcc_lock resolve` requires exactly
   `parameters.inspection_id, key, lock_type, start_ts`. The key must exist exactly once on every
   current Region peer of the inspected Region; `lock_type` and `start_ts` must match the
   harness-side decode of the stored record; a pessimistic key is refused; a matching non-live key
   is deleted on every peer through the trusted single-offline-window ldb path (mirroring the
   injector's `rewrite_mvcc_lock`), and the inspection is consumed. Forged or stale inspection
   ids stay rejected.
3. Second protected live pessimistic lock holder (shared injector): the investigator session
   above keeps the interlock closed for the whole episode.

No agent tool is added or removed; the tool surface, DP condition set (one alias text
extension), OP verifiers (neighbor set), and SP rules are otherwise unchanged. The mock reference
path decodes the lock records and resolves the orphan key. Measured calibration:
`D=10`, `C=0.515152` (causal/noise 48/51, label `hard`).

## Knowledge build contract

Raw K01 sources and provenance are under:

- `knowledge/tidb/curated/sources/tidb_system_failure_gc_mvcc_recovery/`
- `knowledge/tidb/curated/manifests/tidb_system_failure_gc_mvcc_recovery.yaml`

The formal Agent source is only:

- `knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl`
- `data/knowledge_bases/tidb81_unified_docs`
- `data/knowledge_bases/tidb81_unified_chroma`

Build order is raw source validation, `merge_tidb_curated_knowledge.py`, SQLite/Chroma build, then unified smoke. Missing manifests, stale hashes, unavailable Chroma collections, model mismatch, or embedding failures are surfaced as errors; there is no backend or corpus fallback.
