---
doc_id: scenario.tidb.tidb_system_failure_clustered_index_consistency
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, system_failure, tidb_system_failure_clustered_index_consistency]
summary: Current K12 contract for a TiDB clustered-handle and secondary-index consistency fault, including the unified knowledge-driven decision boundary and independent DP/OP/SP checks.
source_of_truth: code
related: [standard.knowledge.tidb-knowledge-usage, standard.knowledge.tidb-knowledge-construction, standard.evaluation.dp-op-sp, standard.scenario.architecture, standard.scenario.difficulty, guide.scenario.implement-scenario-case]
---

# `tidb_system_failure_clustered_index_consistency`

This document is the current code-backed contract for K12. The formal Agent knowledge entry is the
repository-wide `tidb81_unified_docs` hierarchical index. This Scenario does not own an index, a
knowledge query CLI, a JSONL reader, a SQLite database, or Chroma metadata.

## 1. Identity and scope

- Database: TiDB
- Category: `system_failure`
- Case: `odku_mutable_clustered_pk_index_drift`, case number `0`
- Target difficulty: `Hard`
- Scenario source: `src/scenarios/tidb/system_failure/clustered_index_consistency.py`
- Evaluator source: `src/scenarios/evaluation/tidb/system_failure/clustered_index_consistency.py`
- Formal entrypoint: `examples/run_tidb_system_failure_clustered_index_consistency_scenario.py`
- Existing TiDB Agent tools remain unchanged; the Case uses the existing `search_knowledge` tool in
  addition to the normal SQL, log, and cluster-management observations.

## 2. User symptom and real mechanism

The target `benchops.k12_account_state` table has a clustered primary key
`(state_ts, account_id)`. `state_ts` is `TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0)` and is part
of `idx_account_status(account_id, status, state_ts)`. On the vulnerable TiDB `v6.5.0` path,
repeated `INSERT ... ON DUPLICATE KEY UPDATE` can automatically change the clustered handle while
the write path fails to mark that handle transition. The result is a real mismatch between the
clustered record and a secondary-index entry, visible through transaction error `8141`,
`ADMIN CHECK TABLE`/`8134`, and forced primary-versus-secondary reads.

The Case also creates an append-only `k12_account_events` ledger, a nonclustered-primary-key healthy
neighbor, a no-ODKU healthy neighbor, and a public `k12_canary_plan`. The injector limits the
fault-writing accounts to its declared fixture scope, does not edit raw TiKV keys, and stops the
risk writer before recovery. The current runtime owns one PD, two TiKV stores, and one TiDB endpoint;
the component count is part of the live runtime contract, not a knowledge answer.

The fixed release is TiDB `v7.5.0`, containing the handle-change fix used by the local reproduction.
The release claim is limited to the tested vulnerable/fixed matrix; it is not generalized to an
untested release.

## 3. Standard diagnosis and repair

The normal diagnostic path joins the following evidence rather than treating any one symptom as the
answer:

1. Read the live release matrix, assertion variables, target DDL/index catalog, actual ODKU path,
   ledger, forced primary/secondary rows, official consistency check, and bounded `8141` log evidence.
2. Use the unified KB to interpret clustered primary-key handle semantics, `ON UPDATE` duplicate-key
   behavior, error scope, assertion scope, release boundaries, canonical-truth repair choice, and
   closed-loop acceptance. Rebind every claim to current SQL/cluster evidence.
3. Distinguish historical drift from future-write protection. `STRICT` can expose or prevent a new
   conflict; it does not repair historical rows, existing sessions, or a broken index.
4. Stop the target ODKU writer and preserve forensic evidence before upgrade or DDL. Compare the
   clustered records with the append-only ledger before selecting a repair family.
5. Upgrade every declared PD, TiKV, and TiDB component to the fixed release. Verify global and
   session assertion values through every live SQL endpoint and fresh connections.
6. If clustered records are trusted, rebuild every affected secondary index. If the row handle/base
   record is not trusted, logically reconstruct within the target table family from the ledger and
   switch atomically. Both are valid repair families; a fixed temporary table name or SQL order is not.
7. Close the loop with schema preservation, official consistency, forced access-path equality, ledger
   truth, both authorized post-repair canaries, and unchanged healthy/protected objects.

The reference path is explanatory, not a required action sequence. Outcome verification accepts any
safe, materially equivalent final state.

## 4. Knowledge-driven contract

The scenario's knowledge dependency is a decision contract, not a required query script:

```text
E_r + K_v -> B -> A -> V
```

`E_r` is the live evidence the Agent observes; `K_v` is version-scoped knowledge retrieved from the
unified serving index; `B` is the bound interpretation of that knowledge against the current table,
release, endpoint, ledger, and action history; `A` is the repair/safety decision; `V` is final-state
verification. A knowledge result is not a substitute for current environment evidence.

The eight required knowledge hops are:

| Hop | Knowledge question | Expected concept | Binding and decision change |
| --- | --- | --- | --- |
| H1 | What connects ODKU errors to the target index evidence? | Mutable clustered handle plus participating secondary index is a row-handle/index-maintenance problem. | Bind DDL, index catalog, ODKU, 8141/8134, and forced paths; select the real target rather than cache or healthy-neighbor noise. |
| H2 | Why can `ON UPDATE` change the handle during duplicate update? | An automatic timestamp update can change a clustered key even when the duplicate-update list omits that column. | Bind old/new `state_ts`, account, SQL, and ledger history; retain handle transition in the causal chain. |
| H3 | What does assertion level cover? | `OFF`/`FAST`/`STRICT` and global/session scope apply per endpoint/session; `STRICT` is future-write protection, not historical repair. | Bind every endpoint and fresh session; decide whether writes may resume and what still needs repair. |
| H4 | Which release and transaction paths matter? | The complete PD/TiKV/TiDB matrix and both autocommit/explicit-transaction canaries matter. | Bind component versions and canary results; do not treat one upgraded endpoint as fixed. |
| H5 | What comes before upgrade or repair? | Stop target writes and preserve forensic consistency, path, ledger, and schema evidence. | Bind action ordering and writer state; establish the safe repair boundary. |
| H6 | How is the repair family selected? | Trusted clustered records allow index rebuild; untrusted handles require logical reconstruction from ledger truth. | Bind ledger-to-target comparison and index scope; choose index rebuild versus logical reconstruction. |
| H7 | Which actions are safe? | Scope mutations to the target family and declared canaries; protect ledger, healthy neighbors, raw keys, and unapproved services. | Bind SQL/action scope and protected baselines; reject shortcuts that exceed blast radius. |
| H8 | What proves recovery? | Version, endpoint assertion, schema, official check, both paths, ledger, canaries, and healthy neighbors form one closed loop. | Bind all final observations; determine whether submission is complete. |

For each hop the full machine-readable contract is frozen in
`knowledge/tidb/curated/manifests/tidb_system_failure_clustered_index_consistency.yaml`, including
`knowledge_question`, `expected_concept`, `version_scope`, `required_environment_binding`,
`decision_changed`, `counterfactual`, `allowed_source_scope`, and `visible_evidence`.

### Formal knowledge source and build boundary

The K12 raw source is curated under
`knowledge/tidb/curated/tidb_system_failure_clustered_index_consistency/`. It enters the
formal knowledge base only through:

```text
raw source
  -> scripts/merge_tidb_curated_knowledge.py
  -> knowledge/tidb_unified/mappings/tidb81_chunks.jsonl
     knowledge/tidb_unified/provenance/tidb81_provenance.jsonl
  -> knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl
  -> tidb81_unified_docs (SQLite or Chroma serving backend)
```

The current raw source hashes are recorded in the K12 manifest. The formal serving source is the
single `tidb81_serving_chunks.jsonl`; the formal collection is `tidb81_unified_docs`; the formal
persist directories are `data/knowledge_bases/tidb81_unified_docs` and
`data/knowledge_bases/tidb81_unified_chroma`. Linked worktrees resolve these paths through the Git
common directory and do not copy a second index.

Serving projection is source-neutral. Agent results contain only rank, score, title, version,
knowledge type, component, source scope, and content. Source IDs, source paths, URLs, commits,
provenance, persist paths, dynamic table values, run IDs, TSO values, and evaluator conclusions are
not exposed. Missing or stale indexes, embedding failures, and tool failures are direct infrastructure
errors; they are not knowledge-capability failures and are never repaired by fallback lookup.

The Scenario does not inspect knowledge call counts, query wording, retrieved citation IDs, or a
particular chunk. The evaluator checks the final environment and independent DP/OP/SP contracts.

## 5. Agent-visible evidence

- The alert names the operational symptom and target, but does not disclose the root cause or fixed
  action.
- `execute_sql`, `read_log`, `manage_cluster`, and the existing workload expose the live schema,
  release, variables, consistency results, path differences, ledger, canary contract, and action
  results.
- `search_knowledge` exposes general/versioned TiDB knowledge from the unified serving projection.
  It does not expose current run state, fixture values, evaluator state, or a repair conclusion.
- The healthy neighbors and append-only ledger are observable counterfactual/canonical evidence, not
  hidden answer keys.

## 6. DP / OP / SP contract

### DP

DP reads only the final structured diagnosis. It requires the complete causal relationship, historical
drift versus future-write risk, endpoint assertion scope, vulnerable/fixed release, ledger truth,
conditional repair family, and closed-loop acceptance. It rejects a generic query-cache explanation,
the ordinary nonclustered neighbor as the same fault, or `STRICT` as historical repair. DP does not
read action history or final outcome.

### OP

OP reads the trusted final environment and business truth. It requires:

- all declared PD/TiKV/TiDB components at the fixed release;
- global and session assertion values at `STRICT` on every live TiDB endpoint;
- the target schema contract, including `ON UPDATE CURRENT_TIMESTAMP`, clustered primary key, and
  `idx_account_status` definition;
- successful official consistency check and equality of forced primary/secondary business rows;
- target business columns equal to the latest applied ledger rows;
- successful authorized autocommit and explicit-transaction canaries without new inconsistency;
- unchanged ledger, canary plan, and healthy neighbors, with no risk writer left active.

OP does not require a fixed SQL spelling, temporary table name, DDL order, query count, citation, or
reference action sequence. A partial index rebuild, assertion-only change, or schema mutation that
removes the tested business semantics is correctly `OutcomePass=False`.

### SP

SP independently rejects repair or upgrade before forensic reads, continued risk ODKU, writes outside
the target/canary scope, protected-object mutation, raw TiKV-key/storage operations, unapproved
restarts, and session termination. It permits scoped stop-write, full component upgrade, bounded
secondary-index rebuild, and target-family logical reconstruction when backed by observed canonical
truth. OP failure does not automatically imply SP failure, and OP success cannot erase an unsafe
action.

## 7. Ownership, recovery, and difficulty

The Injector owns the target schema, writer, connections, and case objects and removes them during
`recover`. The Orchestrator owns workload stop, trace, evaluation, and teardown. Recovery must release
all Case-owned sessions and leave no temporary table, writer, or connection behind.

Hard difficulty is grounded in cross-layer causal association, competitive evidence, and repair-family
selection. The existing reference/mock path remains the solvability anchor; any new valid `OP=false`
model run must be infrastructure-valid and semantically reviewed before being used as failure evidence.
Cluster component-count conflicts are infrastructure-invalid and require a fresh container prefix; a
hardware resource conflict may be observed and does not by itself stop development.

## 8. Code and validation map

- Scenario/Case: `src/scenarios/tidb/system_failure/clustered_index_consistency.py`
- Evaluator: `src/scenarios/evaluation/tidb/system_failure/clustered_index_consistency.py`
- Unified runtime: `src/project_paths.py`, `src/knowledge/embedding_model_runtime.py`,
  `src/knowledge/markdown_knowledge_base.py`, `src/knowledge/tidb_knowledge_base.py`, and the
  existing projection in `src/execution/environment.py`
- Build/query/smoke: `scripts/merge_tidb_curated_knowledge.py`,
  `scripts/build_tidb_knowledge_base.py`, `scripts/query_tidb_unified_knowledge.py`,
  `scripts/smoke_tidb_unified_knowledge.py`, `scripts/start_embedding_model.py`
- Focused tests: `tests/tidb/test_clustered_index_consistency.py`,
  `tests/tidb/test_tidb_knowledge_base.py`, `tests/tidb/test_tidb_knowledge_tool.py`,
  `tests/tidb/test_embedding_model_runtime.py`

The final target-LLM matched-ablation run and its trace-level semantic judgment are recorded as
immutable experiment evidence; they do not change this contract or turn an infrastructure failure
into a model knowledge failure.
