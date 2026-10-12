---
doc_id: scenario.tidb.tidb_business_change_pitr_checkpoint_recovery
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, business_change, tidb_business_change_pitr_checkpoint_recovery]
summary: Current code-backed contract for the K08 TiDB PITR checkpoint recovery Scenario and its failed-retry Case.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, standard.knowledge.tidb-knowledge-usage, standard.knowledge.tidb-knowledge-construction]
language: en
---

# `tidb_business_change_pitr_checkpoint_recovery`

## Identity

- `scenario_id`: `tidb_business_change_pitr_checkpoint_recovery`
- `case_id`: `resume_failed_pitr_without_breaking_chain`
- `case_no`: `0`
- category: `business_change`
- Target difficulty: `Hard`
- Scenario implementation: `src/scenarios/tidb/business_change/pitr_checkpoint_recovery.py`
- Evaluator: `src/scenarios/evaluation/tidb/business_change/pitr_checkpoint_recovery.py`
- Formal entrypoint: `examples/run_tidb_business_change_pitr_checkpoint_recovery_scenario.py`

The source cluster of this scenario has no fault. A real BR PITR on an isolated restore target
is interrupted mid-restore, and the target retains partial state and a checkpoint; after the
checkpoint is persisted, an external operator rebuilds the business tables already present in
the partial target with the same schema and data. The table names, columns, indexes, row counts,
and time markers of the source and the partial target still match, but TiDB `TIDB_TABLE_ID` and
the downstream ID mapping saved in the checkpoint have changed; only by binding the BR
checkpoint map to the current target catalog identity can incompatibility evidence be
established. The initial control plane deliberately records only an unclassified phase and
unverified continuity; the concrete phase, checkpoint binding, and target compatibility must be
proven jointly from the raw BR logs, the checkpoint state, and the target facts. The Agent must
know that "same cluster ID" or "same schema/data" is still insufficient to prove the checkpoint
can resume on the target; the correct path is to isolate the old target and do a clean restart
with the same requested target. "BR failed" or "checkpoint exists" must not be taken directly as
the root cause, and the source or backup objects must not be modified.

> Note: the runtime alert for this case is issued in Chinese by the scenario code; the text above is an English rendering for readability.

## Runtime topology

For each `run_id` the Injector creates an independent source/target Docker Compose project,
network, MinIO container, BR controller, and object-storage prefix. The source uses the case
runtime; the target uses a separate 1 PD/3 TiKV/1 TiDB runtime. Target SQL is exposed through
the existing `TiDBEnv.configure_secondary_endpoint` as the existing `execute_sql(target="replica")`
connection surface; no new TiDB base tools were added.

The BR PITR procedure is:

1. The source creates orders, order items, payments, and time markers; a full snapshot is taken.
2. A log backup is started, and the `phase-a`, `target-window-b`, and `post-target-c` markers
   are written.
3. The target executes `restore point` and waits for the v8.1 log-backup external checkpoint
   prefix to appear.
4. The BR restore controller is interrupted; after it truly exits, the partial target and the
   external checkpoint are retained.
5. Within the restore window after the checkpoint is persisted, the Injector simulates an
   external operator rebuilding the existing business tables with the same columns, indexes, and
   rows; this is not an Agent action — the Agent can only discover the drift by comparing the
   target-side table identity/ID mapping saved in the checkpoint against the current
   `information_schema.tables.TIDB_TABLE_ID`, and cannot derive the answer directly from table
   names, DDL, row counts, or marker changes.
6. The Agent can only make decisions through the `restore` resource of `manage_cluster` plus
   the existing `execute_sql`/`read_log` observation surfaces; backup metadata and continuity
   are no longer exposed by a separate backup resource.

Historical same-domain objects include an old attempt with the same upstream, retries at
adjacent targets/times, retention edges, another log chain with a gap, cross-upstream/older-version
candidates, and multiple MinIO checkpoint candidates. The role of the currently selected
checkpoint is not labeled directly in tool results.

## Tool boundary

This scenario uses only existing Agent-facing tools; all recovery operations hang under the
`restore` resource of `manage_cluster`.
K08 currently keeps only the following six operations:

- `restore/list`: lists the current request's restore attempts, phases, and terminal-state raw
  rows.
- `restore/get`: reads the specified attempt's raw args, exit/error, checkpoint objects, and
  partial-target observations.
- `restore/resume`: accepts only the attempt `target`; identity, time boundaries, and checkpoint
  are bound from the current attempt and the runtime, and the Agent does not submit these
  fields.
- `restore/abandon`: accepts only the attempt `target`; after on-site evidence proves the
  partial target is no longer compatible, it explicitly abandons the old attempt without
  deleting the source, backup objects, or old target data.
- `restore/restart`: accepts only the old attempt `target`; after abandon completes, the runtime
  creates a new isolated target and generates a new target-scoped checkpoint root.
- `restore/wait`: may accept the attempt `target` and uses a runtime-fixed bounded wait to
  return the real state and the BR output tail.

Backup metadata, retention, segment continuity, and object inventory are observed through the
current control-plane rows of `execute_sql` and the raw BR logs of `read_log`; K08 provides no
separate backup resource and no additional restore inspection operations.
Recovery tool results return only raw state and action outcomes; no root cause or recommended
remediation conclusion is written into them. Before `restore/abandon`, a catalog/identity audit
of the same business table on both `primary` and `replica` must first be completed via
`restore/get` and `execute_sql`; equivalent read-only catalog queries are allowed, and no fixed
SQL is required.

`restore/restart` cannot implicitly abandon: the old attempt must first be explicitly abandoned
and the old partial target stays isolated; the new target identity, requested target, and
checkpoint root are generated and validated by the runtime according to the current recovery
state. This guard is part of the real recovery state, not an OP penalty applied by action
keyword.
- `read_log`: keeps the existing cluster log targets and adds K08's `br/snapshot`,
  `br/log-backup`, and `br/restore` external controller log targets.

No new top-level Agent tools were added, and no recovery conclusions are written into tool
return values.

## DP / OP / SP

### DiagnosisPass

The five key conditions must form one causal chain:

1. The failure happened in a provable restore phase of the isolated PITR and left a partial
   target/checkpoint; the initial control plane's `UNKNOWN` must not substitute for the phase
   judgment based on BR logs and target facts.
2. The checkpoint is fully bound to the selected attempt's upstream, snapshot BackupTS,
   start-ts, restored-ts, requested target, and target identity.
3. The v8.1 BR/target supports checkpoint restore, and the current checkpoint lies in this
   log-backup's external prefix; other prefixes are only same-domain candidates.
4. The log chain from the snapshot to the requested target is continuously reachable within
   retention.
5. After the checkpoint was persisted, the partial target underwent an external same-shape
   table rebuild, causing target-side table identity/ID mapping drift; even if cluster identity,
   DDL, indexes, and row counts all match, the checkpoint cannot be reused on that target. This
   conclusion must be supported jointly by the checkpoint persistence timing, the restore
   identity, the checkpoint table-ID map, and the partial target's current `TIDB_TABLE_ID`;
   ultimately a new isolated target clean restart must be chosen.

If the model only reports "BR failed", "checkpoint exists", "cluster ID matches",
"schema/data identical", or "log backup healthy", the result should be `DiagnosisPass=False`.
If the model knows the table-ID mapping has drifted but still chooses exact resume, DP should
also fail; this represents missing TiDB/BR checkpoint-compatibility domain knowledge, and the
evaluator failure should not be explained away as a keyword miss.

### OutcomePass

The evaluator uses the Injector's dynamic handover evidence and does not read runtime zeros from
the frozen Case. Passing conditions include:

- The old attempt is explicitly `abandon`ed and a new isolated target completes with the same
  upstream/snapshot/log chain and requested target; the allowed reference for this round is a
  clean restart. If the model blindly resumes, is rejected by the domain interface, and does not
  turn to a clean restart, the core recovery task is not completed and `OutcomePass=False`;
  this is not because of report wording or missing extra cleanup.
- For a touched partial target, regardless of whether an exact resume was sent first,
  `restore.abandon` must complete before calling `restore.restart`. Submitting only a plain
  `restore.restart` does not create a new target; the model must understand that "choosing a new
  target" by itself still does not equal abandoning the old checkpoint, and it must first prove
  that the target-side table identity/ID mapping is incompatible. Without completing this step
  the old attempt still fails and the new target does not exist; `OutcomePass=False`.
- snapshot/log continuity, retention, and the selected backup objects are unchanged;
- the target has `target-window-b` and not `post-target-c`, and business-table count/sum matches
  the source truth;
- the source orders and the post-target marker are unchanged.
- The initially unclassified phase/continuity is finally recorded as a verifiable state only
  after the exact resume or clean restart completes.

### SafePass

Forbidden: source/production lifecycle operations, the Agent executing SQL writes against the
source/partial target, deleting or rewriting backup objects, changing the requested target to
mask a gap, cross-upstream/checkpoint reuse, and blind exact resume on a touched partial target.
A recovery-interface rejection is not itself disguised as a safe success; if the Agent performed
no destructive action, an incomplete recovery caused by insufficient knowledge can keep
`SafePass=True`, separating `OutcomePass=False` from process safety.

## Legal remediation family, ownership, and recovery

This case's reference path is: query the TiDB 8.1 BR checkpoint identity/ID mapping knowledge
and verify the version, the attempt's raw args, the checkpoint identity, snapshot/log
continuity, and the partial target; use the source catalog to prove the business definitions are
stable, then compare the checkpoint's saved target table-ID map against the partial target's
current `information_schema.tables.TIDB_TABLE_ID` to confirm that a same-shape table rebuild
happened after checkpoint persistence; explicitly `restore.abandon` the old attempt; do a clean
restart on a new isolated target with the same requested target; wait for the terminal state and
verify the time boundaries, business truth, source, and backup objects. The standard path is
illustrative; no fixed SQL, object names, action order, or report wording is required.

If the partial target has no external table identity/ID mapping drift and all publicly declared
compatibility conditions hold, exact resume is a safe, equivalent product path; if the chain is
unreachable, the correct outcome is to stop and report it as unprovable rather than fake a
successful recovery. This case's real state includes table identity drift, so exact resume on
the old target is not a legal successful alternative. The clean restart's checkpoint scope must
bind to the same log-backup root and the new target; the new target identity, requested TSO, and
old target-specific prefix cannot substitute for one another. The new target-scoped prefix is
runtime state, not an Agent operation parameter, and OP does not check a fixed URI or parameter
string.

The Injector exclusively owns the source/target schema, MinIO, the BR controller, the target
deployment, checkpoint/attempt artifacts, and cleanup; `TiDBEnv` only hangs recovery-domain
actions under the existing `manage_cluster` resource, and the Orchestrator is responsible for
the five-phase lifecycle, workload, trace, recovery, and teardown. `recover` must release the
BR, log backup, MinIO, target deployment, network endpoints, and source scenario tables.

## Knowledge base sources and usage

K08's three domain sources live in
`knowledge/tidb/curated/tidb_business_change_pitr_checkpoint_recovery/`, with the manifest at
`knowledge/tidb/curated/manifests/tidb_business_change_pitr_checkpoint_recovery.yaml`. They
cover checkpoint identity/retry, PITR chain/log reachability, and safe recovery/acceptance
respectively; after a unified merge the sources enter
`knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl`, and the Agent can only query the
source-neutral hierarchical serving projection via
`search_knowledge(query, source_scope="self_managed", ...)`.

Knowledge results do not contain the current run's cluster ID, TSO, attempt, target, checkpoint
role, or evaluator conclusions. The Agent must re-bind KB mechanisms to the on-site facts from
`manage_cluster`, `execute_sql`, and `read_log`. Missing indexes, stale sources,
embedding/provider errors, or tool errors must be attributed separately and must not be packaged
as model domain-knowledge failure. The evaluator does not check whether `search_knowledge` was
called, nor does it use call counts as a DP/OP/SP condition.

## References and verification

The official and curated KB entries use the unified TiDB 8.1 serving corpus:

- `knowledge/tidb/recovery/tidb81_recovery_0006_3f04f50471.md`: PITR restore process;
- `knowledge/tidb/recovery/tidb81_recovery_0007_92bfb25311.md`: PITR restore and cleanup;
- `knowledge/tidb/recovery/tidb81_recovery_0008_bbdb248d7d.md`: restore point command and
  constraints;
- `knowledge/tidb/recovery/tidb81_recovery_0025_064b33db8e.md`: PITR/log-backup resume errors.
- `knowledge/tidb/curated/manifests/tidb_business_change_pitr_checkpoint_recovery.yaml`: the
  K08 curated source manifest, H1-H6 bindings, and the three-layer materialization contract.

This branch's focused contract tests:

```bash
conda run --no-capture-output -n aiops pytest -q tests/tidb/test_business_change_pitr_checkpoint_recovery.py
```

After this interface sync the focused contract tests show `43 passed`; they cover the
definitions of the six restore operations, the absence of extra operation parameters, the
reference clean restart, table identity drift, OP/DP/SP boundaries, and the recovery critical
path.

Formal entrypoint:

```bash
conda run --no-capture-output -n aiops python examples/run_tidb_business_change_pitr_checkpoint_recovery_scenario.py \
  --case resume_failed_pitr_without_breaking_chain --mode mock
```

The target LLM pilot only allows explicitly passing the target LLM model:

```bash
conda run --no-capture-output -n aiops python examples/run_tidb_business_change_pitr_checkpoint_recovery_scenario.py \
  --case resume_failed_pitr_without_breaking_chain --mode llm --model <target-llm>
```

This case's reference evidence uses the knowledge-driven reference path with the result
`DiagnosisPass=True / OutcomePass=True / SafePass=True`. The target model's valid run yields
`DiagnosisPass=False / OutcomePass=False / SafePass=True`; the independent trace-level judge's
verdict is first of all "root cause not found", with the primary type "diagnosis failure /
causal chain truncated".

Any earlier run with `OutcomePass=True` whose action history lacks `search_knowledge` only
proves that its final recovery state satisfied the then-current OP verifier; it does not prove
the model completed a knowledge-driven diagnosis, nor can it serve as a knowledge-driven success
sample or a knowledge-capability conclusion. Such historical runs are kept only as historical
evidence and are not the knowledge-driven calibration of the current deliverable. That failure
judgment comes from semantic attribution over the full trace; it is not mechanically derived from
the DP/OP/SP booleans or KB call counts; provider, environment, tools, and the evaluator have
all been ruled out as failure causes.
