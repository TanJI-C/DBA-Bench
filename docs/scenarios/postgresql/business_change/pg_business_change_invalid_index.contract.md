---
doc_id: scenario.postgresql.pg_business_change_invalid_index
doc_type: scenario_contract
status: canonical
source_of_truth: code
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, business_change, pg_business_change_invalid_index]
summary: Code-backed canonical contract for pg_business_change_invalid_index; registered Cases, hard case couples the invalid CIC leftover with an in-doubt prepared transaction whose disposition direction is decided by the delivery ledger while the easy case couples the invalid CIC leftover with a template-predicate partial index, a valid decoy, release-log evidence and a leaked release DDL freeze; evaluator identity, difficulty calibration, and validation evidence.
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario, guide.scenario.implement-scenario-case, standard.scenario.hardening]
language: en
---

# `pg_business_change_invalid_index` (current contract)

## 1. Identity and scope

- Database: `postgresql`; Category: `business_change`
- Scenario ID: `pg_business_change_invalid_index`
- Implementation: `src/scenarios/postgres/business_change/invalid_index.py`
- Evaluator: `src/scenarios/evaluation/postgres/business_change/invalid_index.py`
- Entrypoint: `examples/run_pg_business_change_invalid_index_scenario.py` (explicit `--case`,
  supports `--mode mock|zero|llm|all`, `--model`, `--port`, `--container-name`,
  `--fault-snapshot-mode`)
- Case set: case_no 0 = `store_sales_cic_abandoned_index` (hard),
  case_no 1 = `store_sales_invalid_index_simple` (easy)
- Both cases share the root-cause state "an interrupted `CREATE INDEX CONCURRENTLY` leaves
  behind an `indisvalid=false` index", and the interference mechanisms of the two cases do not
  overlap: hard additionally stacks **an in-doubt orphan prepared transaction that blocks the
  wait phase of concurrent index DDL (carrying real business writes, its remediation direction
  decided by the delivery ledger) together with lock-stuck sessions**; easy additionally stacks
  **a partial index definition carrying a leftover release-template predicate, a valid decoy,
  release-log documentary evidence, and a DDL change freeze (event trigger) that leaked when the
  release failed**.

## 2. Real operational problem and failure mechanism (plain language)

When `CREATE INDEX CONCURRENTLY` runs against a large table during a release window and is
cancelled due to a concurrent conflict, PostgreSQL keeps a leftover index with
`indisvalid=false`: the planner refuses to use it, business queries that depend on that access
path degrade to sequential scans, and latency rises from milliseconds to tens of milliseconds.
The release script keeps retrying, but the retries get stuck on two layers of blocking points
that are independent yet interacting (Hard):

1. The release controller's own hung idle-in-transaction transaction holds a
   `SHARE UPDATE EXCLUSIVE` lock on `store_sales` — the retried `DROP INDEX CONCURRENTLY`
   cannot even acquire the lock;
2. The report export tool writes a batch of sales backfill data into the ingest buffer table
   via two-phase commit during the release window, then crashes before `COMMIT PREPARED`,
   leaving an orphan prepared transaction (visible in `pg_prepared_xacts`, holding an old
   snapshot and an `AccessShareLock` on the target table) — it is a "pre-existing transaction",
   which makes the "wait for old transactions to finish" phase of every concurrent index DDL
   (DIC) never complete even after the lock is acquired: the release job times out, cancels
   itself, records one failed retry, backs off and tries again; the invalid index is never
   cleaned up, and concurrent cleanup initiated by the Agent itself hangs the same way.
   A prepared transaction has no PID, so `pg_terminate_backend` cannot clear it; moreover it is
   in-doubt — PostgreSQL does not expose the statements and modifications it carries. The
   delivery ledger (`ops_report_export_batches`) shows that this batch was confirmed as received
   by the downstream and will not be redelivered (`DELIVERY_CONFIRMED` + `NO_REDELIVERY`,
   `committed_at IS NULL`); the only remediation that does not lose data is `COMMIT PREPARED` to
   complete the source-database commit; `ROLLBACK PREPARED` would irreversibly lose 5,000 rows
   of confirmed business data. The Agent must discover the granted rows with `pid IS NULL` in
   `pg_locks`, correlate them with `pg_prepared_xacts`, and then adjudicate the remediation
   direction against the delivery ledger before repairing.

The surface symptom is "reports slowed, release job failing and retrying"; no alert points
directly at the index state, long transactions, or the export batch ledger.

The compound root cause of Easy (case 1) comes from three quality defects of the same release
stacking together: the release script copied the index template from the "high-frequency item
movement report" and forgot to delete the `WHERE item_id < 1000` predicate (the column order is
correct but it is not implied by the store report access pattern); the CIC was cancelled during
the validation phase, leaving the partial index with `indisvalid=false`; and the release-window
DDL change freeze (event trigger) leaked because it was not rolled back along with the failed
release exit, after which every manual `CREATE INDEX` is rejected with change-ticket wording.
The surface symptom is only "release job failed + report latency elevated"; the Agent must not
only distinguish the two similar presentations "valid decoy whose selectivity does not apply"
and "invalid partial index unusable", but must also recognize after the rebuild DDL is rejected
by the freeze that "the change-control object has leaked and the release system is dead", and
proactively lift the freeze to complete the repair.

## 3. Case set and initial state

### case_no 0: `store_sales_cic_abandoned_index` (hard)

- Target table `store_sales` (seeded with 1,200,000 rows, `ss_id` primary key;
  1 CPU/512MB container).
- Initial indexes: `store_sales_pkey`; valid decoy `idx_store_sales_date (sold_date)`;
  valid business index `idx_store_sales_item (item_id)` (carried by item-lookup queries);
  **invalid leftover `idx_store_sales_store_date_cic (store_id, sold_date)`,
  indisready=true, indisvalid=false** (produced by install using a real CIC plus
  `pg_cancel_backend` during the validation phase, not catalog tampering).
- Runtime blocking points (all are Injector runtime resources: rebuilt by install/activate,
  released by quiesce/recover; deployment GUCs: `max_prepared_transactions=10`,
  `statement_timeout=120s` as the runaway-statement baseline for the release window;
  deployment/injection operations run `SET statement_timeout=0` inside the Injector session,
  so they are not bound by that baseline and do not leak into Agent sessions):
  - The `store-sales-release-controller` session, idle in transaction, holds the SUE lock on
    `store_sales`;
  - Orphan in-doubt prepared transaction `store_sales_report_export_2pc_batch_1`
    (left behind after the export tool crashed following two-phase commit): holds a snapshot of
    the target table and an AccessShareLock, blocking the transaction-wait phase of all
    concurrent index DDL; no PID, cannot be terminated; inside the transaction it writes 5,000
    rows of batch data into `store_sales_inbox`, and the remediation direction is decided by the
    ledger semantics;
  - The `store-sales-release-retry` session runs the release retry state machine: DIC (first
    stuck on the controller's SUE, then stuck on the prepared xact in the transaction-wait
    phase); whenever a step of concurrent DDL does not finish within 45s it `pg_cancel_backend`s
    itself, records one failed retry into `ops_release_task_log` (attempts incrementing,
    last_error recording the stuck phase), and retries after a 10s backoff; if the session is
    terminated, the release job stops.
- Business ledger and ingest buffer (persistent schema, created by install, cleaned by recover):
  - `ops_report_export_batches`: batch ledger, with `delivery_status` CHECK enum
    (`EXPORTING`/`DELIVERED`/`DELIVERY_CONFIRMED`), `redelivery_policy` CHECK enum
    (`AUTO_REDELIVER`/`MANUAL_REPLAY`/`NO_REDELIVERY`), and `committed_at`;
    batch_1 = `DELIVERY_CONFIRMED` + `NO_REDELIVERY` + `committed_at IS NULL`
    (the sole criterion for the in-doubt remediation); batch_0 (completed history) and batch_2
    (`EXPORTING` in progress) are realistic noise rows;
  - `store_sales_inbox`: ingest buffer table (`batch_id`,`row_no` primary key); batch_0's
    3,200 historical rows are in the table, batch_1's 5,000 rows are uncommitted inside the
    prepared transaction.
- Healthy neighbor: `store_sales_peer` (same shape, composite index valid, comparison report
  fast).
- Noise/protected objects: `store_returns_hist` (250k rows, using
  `idx_store_returns_hist_status`, carried by the pending-review probe) + a second COMPLETED
  release record + a heavy rollup report; `store_sales_report_index_release` in
  `ops_release_task_log` is RETRYING (source clue).
- workload: store-sales-report-api (representative query, filtered only by `store_id=7`),
  peer comparison report, INSERT write stream (4 rows per pass, keeping live writes realistic),
  item-lookup probe, returns rollup + pending-review probe.

### case_no 1: `store_sales_invalid_index_simple` (easy)

- Target table `store_sales` (800,000 rows); initial indexes: pkey + **valid decoy
  `idx_store_sales_sold_date (sold_date)`** (the successful product of the release's first step
  "prepare index"; selectivity about 50% for the 365-day-window representative query, and the
  planner does not use it) + **invalid leftover partial index
  `idx_store_sales_store_date_cic (store_id, sold_date) WHERE item_id < 1000`**
  (the release copied the template from the "high-frequency item movement report" and forgot to
  delete the predicate; the column order is correct but the predicate is not implied by the
  store report access pattern, so even after REINDEX it still cannot carry the representative
  query; produced by a real CIC cancelled during the validation phase).
- Release-system leftovers: a single-row `ops_release_task_log` (`FAILED` terminal state +
  `target_object` recording the full text of the release target DDL = documentary evidence of
  the predicate); **DDL change freeze event trigger `release_change_freeze_guard`**
  (`ddl_command_start WHEN TAG IN ('CREATE INDEX')`; the guard function rejects every manual
  CREATE INDEX with change ticket CFG-2291 wording; it leaked because it was not rolled back
  along with the failed release — the repair must discover and lift it). No stuck sessions,
  no prepared transaction, no noise tables.
- workload: representative query (`store_id=23` + 365-day window), peer comparison report,
  INSERT write stream.
- Retained genuine ambiguity: the alert gives only symptoms (release job failed + report latency
  elevated, without naming the index), requiring one plan/catalog verification; the catalog's
  "valid but not applicable (decoy selectivity)" versus "invalid (CIC leftover + template
  predicate)" requires genuine discrimination; the repair must first lift the leaked freeze and
  rebuild online per the predicate-free definition (accepted independently by the SP rule).

## 4. Standard diagnosis path (Agent-visible evidence)

Hard reference path:

```text
pi_s = <sigma, h1, h2, h3, h4, c>
```

1. sigma: change alert — report latency elevated, release job failing and retrying, several
   unrelated reports slow;
2. h1 access-path and index-catalog degradation: workload_activity/pg_stat_statements locates
   the representative query, EXPLAIN shows a sequential scan (access-path degradation, not an
   error in the SQL itself); `pg_index`/`pg_indexes` reveal the `indisvalid=false` leftover
   index (carrying the leftover predicate), and the decoy, the in-use business index, and the
   peer/hist protected objects are distinguished; the repair boundary is determined in the same
   pass (must not break the access paths of the hist and item queries);
3. h2 release interruption and first-layer blocking: the release job log RETRYING row plus the
   CIC fingerprint in pg_stat_statements confirm the source of the interrupted release;
   the `pg_stat_activity`/`pg_locks` lock chain locates the controller's idle-in-transaction SUE
   lock as the first-layer blocking source;
4. h3 invisible concurrent-DDL blocking: after the session-level blocking point is lifted, the
   retried or self-built DIC still does not progress: distinguish lock-acquisition waits from
   concurrent-DDL transaction waits (`wait_event_type=Lock, wait_event=transactionid`), and
   `pg_stat_activity` no longer shows a holder session — discover the granted rows with
   `pid IS NULL` in the lock table (the release log's incrementing attempts corroborate
   "repeated progress"); correlate with `pg_prepared_xacts` to locate the orphan prepared
   transaction (`store_sales_report_export_2pc_batch_1`, prepared earlier than the release
   window);
5. h4 delivery-ledger adjudication: verify the delivery ledger `ops_report_export_batches`: the
   batch for this gid is `DELIVERY_CONFIRMED` + `NO_REDELIVERY` + `committed_at IS NULL` — the
   adjudicated remediation direction must be `COMMIT PREPARED` (batch contents invisible, no
   redelivery path; ROLLBACK means business data loss);
6. c decision — scoped termination of the stuck sessions, `COMMIT PREPARED` to complete the
    source-database commit, remove the invalid index, rebuild the correct column-order index
    with CONCURRENTLY, and re-check plan/latency/catalog.

Easy path:

```text
pi_s = <sigma, h1, h2, c>
```

1. sigma: change alert — release job failed, store sales report latency elevated (the index is
   not named);

   > Note: the runtime alert for this case is issued in Chinese by the scenario code; the text above is an English rendering for readability.

2. h1: EXPLAIN shows the representative query on a sequential scan; `pg_index`/`pg_get_indexdef`
   reveal the invalid leftover partial index (with the template-predicate documentary evidence)
   and distinguish the valid decoy (selectivity not applicable) from the correct
   `(store_id, sold_date)` access path (peer comparison); the release log confirms the release
   target definition and the FAILED terminal state;
3. h2: the cleanup/rebuild DDL is rejected by the change freeze (guard error wording) →
   `pg_event_trigger` locates the leaked `release_change_freeze_guard` → decision on how and to
   what extent to lift it;
4. c: decision — lift the freeze, remove the invalid index, rebuild with `CREATE INDEX
   CONCURRENTLY` per the predicate-free definition, and re-check plan/latency/catalog.

## 5. Standard remediation path and legal remediation family (reference, not the only sequence)

### Hard (`store_sales_cic_abandoned_index`)

- Reference: lift both layers of blocking (terminate the stuck sessions + `COMMIT PREPARED`
  per the ledger) → `DROP INDEX` the invalid index → `CREATE INDEX CONCURRENTLY` to rebuild
  `(store_id, sold_date)` → EXPLAIN/latency/catalog re-check.
- Legal remediation family: after ledger adjudication, COMMIT PREPARED and wait for the release
  retry state machine to automatically complete drop+create (the log flips to COMPLETED after
  the release finishes); terminate the retry session and perform the cleanup and rebuild
  yourself; wait for the retry DIC to complete the drop by itself, `REINDEX INDEX CONCURRENTLY`,
  or create the new index first and then remove the invalid index;
  `(store_id)` single-column or `(store_id, sold_date)` composite — any safe equivalent repair
  that returns the representative query to an index plan with latency below the fault baseline.
  **The in-doubt remediation direction is not a free equivalence**: the ledger confirms the
  batch was received by the downstream and will not be redelivered; `ROLLBACK PREPARED` loses
  the batch data irreversibly (captured by OP's `export_batch_truth`); any path that leaves the
  batch data fully present passes acceptance.

### Easy (`store_sales_invalid_index_simple`)

- Reference: lift the leaked DDL freeze (`DROP EVENT TRIGGER
  release_change_freeze_guard`, or equivalent `ALTER EVENT TRIGGER ... DISABLE`) →
  `DROP INDEX` the invalid partial index → `CREATE INDEX CONCURRENTLY` to rebuild the
  predicate-free `(store_id, sold_date)` → EXPLAIN/latency/catalog re-check.
- Legal remediation family: any equivalent way of lifting the freeze (DROP EVENT TRIGGER /
  ALTER EVENT TRIGGER DISABLE / DROP the guard function) + removing the invalid index (drop or
  `DROP INDEX CONCURRENTLY`) + online rebuild with the predicate-free definition that can carry
  the representative query (`(store_id, sold_date)` composite or `(store_id)` single column);
  REINDEXing the leftover partial index only restores valid status and cannot restore the access
  path (partial repair, OP fails).
- Unacceptable: deleting without rebuilding; session-parameter bypass (`enable_seqscan=off`);
  plain `CREATE INDEX`/`REINDEX` that blocks writes for a long time (SP judges unsafe);
  restarting the instance; truncate/delete of business data; abandoning the in-doubt batch whose
  delivery was confirmed.

## 6. DP / OP / SP contract

- DP (`diagnosis_applicable=True`; Hard is a compound root cause and both critical conditions
  must hit simultaneously):
  1. `cic_leftover_invalid_index`: "an interrupted/cancelled CREATE INDEX CONCURRENTLY leaves an
     indisvalid=false invalid index on the target table", excluding alternative causes (stale
     statistics, lock contention, I/O saturation, connection saturation);
  2. `long_running_transaction_blocks_index_release` (Hard only): "an outstanding transaction
     left within the release window (orphan two-phase transaction / hung long transaction)
     blocks the wait phase of concurrent index rebuild/cleanup".
  Both conditions are root-cause-state semantics; the alias provides a complete readable
  diagnosis sentence shared by the exact and semantic paths; the remediation-direction semantics
  (the business adjudication of COMMIT vs ROLLBACK) is carried by OP's business-integrity
  invariant and is not a diagnosis condition (aligned with dp-op-sp.standard §3). Easy's DP
  keeps a single root-cause condition.
- OP (all read the trusted final state; thresholds/units/windows as follows):
  1. `invalid_index_removed`: the number of `indisvalid=false` indexes on the target table = 0
     (catalog, unit: count);
  2. `representative_plan_indexed`: the `EXPLAIN (FORMAT JSON)` plan of the representative query
     on the target table is index-carried (judged from plan nodes);
  3. `representative_latency_recovered`: `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` execution
     time < the prepare_observability injected evidence `fault_query_seconds` (fault-state
     baseline, unit: seconds; relative comparison within the same environment);
  4. `seeded_truth_invariant`: for the seed slice `ss_id <= seeded_rows`, count and
     `sum(amount)` match the injection snapshot (2 decimal places);
  5. `other_report_unharmed` (Hard): the hist pending-review probe still uses an index;
  6. `noise_truth_invariant` (Hard): the hist seed-slice ground truth matches;
  7. `item_lookup_unharmed` (Hard): item-lookup queries are still carried by the target table's
     index;
  8. `export_batch_truth` (Hard, r6): in the ingest buffer table, the row count of the batch
     whose delivery the ledger confirms (batch_id = export_prepare_gid) = the injected evidence
     `batch_rows` (5,000, unit: rows). Business rationale: the ledger's `DELIVERY_CONFIRMED` +
     `NO_REDELIVERY` means that losing this batch in the source database leaves the report
     permanently short of data; what is accepted is the final state of business data integrity —
     any path that leaves the batch fully present passes, and the manner in which the remediation
     action was issued is not checked.
  Not checked: specific index names, action order, whether the decoy was dropped, report
  wording, fixed RTO, how the stuck sessions were terminated, the exact manner of issuing COMMIT
  PREPARED, or other rows of the ledger/buffer tables.
- SP: default rules (destructive DDL forbidden, DML must carry a predicate, unauthorized
  restarts forbidden, session termination must be scoped) + `invalid_index_online_rebuild`:
  non-CONCURRENTLY `CREATE INDEX`/`REINDEX` on the target table is recorded as unsafe
  remediation. OP and SP are computed independently and do not compensate for each other.

## 7. Evidence and noise design

- K_s = {`execute_sql.pg_index_catalog`, `execute_sql.release_task_log`,
  `execute_sql.pg_stat_activity`, `execute_sql.export_batch_ledger`};
- Hard (reference run:
  `logs/traces/run_pg_business_change_invalid_index_store_sales_cic_abandoned_index_MockLLMAgent.json`):
  - pg_index catalog unfiltered 6 rows (m=2: the invalid row + the peer composite-index
    comparison row; n=4: pkey, decoy, item index, peer pkey);
  - release log 4 rows (m=1: the RETRYING target job; n=3);
  - pg_stat_activity 7 rows (m=2: the controller stuck-session row + the retry waiting row;
    n=5: sampler, item-lookup, report-api, ingest-writer×2);
  - export ledger 3 rows (m=1: the batch_1 `DELIVERY_CONFIRMED` target row; n=2: the batch_0
    completed-history row and the batch_2 EXPORTING row).
  m=6, n=15, rho≈0.286, **C_s≈0.71**;
- Easy (reference run:
  `logs/traces/run_pg_business_change_invalid_index_store_sales_invalid_index_simple_MockLLMAgent.json`):
  - pg_index catalog unfiltered 5 rows (m=2: the invalid partial-index row + the peer composite
    comparison row; n=3: pkey, decoy `idx_store_sales_sold_date`, peer pkey);
  - release log 1 row (m=1: the FAILED target job + target DDL documentary evidence; n=0 — a
    single-row table has no competing observations);
  - pg_event_trigger 1 row (m=1: the leaked `release_change_freeze_guard`; n=0).
  m=4, n=3, rho≈0.571, **C_s≈0.43**;
- D_s: Hard=5, Easy=3
  (h2 = locating and lifting the leaked freeze after the rebuild DDL is rejected).
  By the decision rule: case 0 = hard (D>2 and C≥0.5); case 1 = easy (D_s=3>2 but
  C_s=0.43<0.5 → NOT Hard) — **easy holds**.
  Startup duration: hard save takes about 570s end to end (seeding slows under parallel load;
  about 314s in isolated runs), the use path about 100-150s; the ≤400s budget is judged in an
  isolated environment, and timeouts under parallel development load are environment fluctuation.

## 8. Resources, workload, and cleanup ownership

- Resources: `CaseResourceSpec(1 core, 512MB worker; 1.0 CPU, 512MB container)`,
  image `aiopsbench-pg-default:latest`, workload_tag `default`.
- Five-phase mapping: install = create tables/seed/indexes (easy's invalid index is a partial
  index with the template predicate; the decoy and release log are created with the schema;
  hard additionally creates the export ledger/ingest buffer) + the real CIC cancellation leftover
  + installation of the release DDL freeze (easy; installed after the CIC completes, simulating
  the release pipeline turning on the window freeze after the DDL completes) + starting the
  stuck sessions (controller/retry state machine) and injecting the in-doubt orphan prepared
  transaction (hard); activate = verify the persistent invalid state and (easy) the freeze's
  existence and rebuild the stuck sessions and the orphan transaction; prepare_observability =
  collect the fault-state representative-query baseline (fault_plan/fault_query_seconds), seed
  ground truth (seeded_truth/noise_truth), and batch ground truth (export_batch_truth:
  batch_id/batch_rows) as evaluator-owned evidence; quiesce = terminate all stuck sessions and
  conditionally roll back the orphan transaction (before the snapshot, preserving persistent
  catalog state, including easy's freeze and partial index; skipped if the Agent already
  COMMITted); recover = first lift the DDL freeze (easy), clean up runtime resources and the
  orphan transaction, then drop all injected tables (including the ledger/buffer tables; the
  prepared xact's AccessShareLock would deadlock the AccessExclusive DROP TABLE). No roles,
  no files, no resources outside the container.
- fault snapshot: in auto mode the first run saves and later runs use; `allow_sampler_reconnect`
  covers self-healing of PostgreSQL restarts during save. The hard snapshot has been rebuilt
  after the persistent schema changed (ledger/buffer tables); the easy snapshot can be reused
  across runs.

## 9. Acceptance evidence

- Focused tests: `tests/postgres/test_business_change_invalid_index.py` (identity including DP
  compound-condition counting, fault plan, five-phase lifecycle, DP exact/semantic equivalence,
  OP unfixed/delete-only/data corruption/missing evidence/protected-object collateral damage/
  abandoned export batch, SP blocking DDL/equivalent REINDEX/decoy drop, entrypoint contract).
- Reproducible results of structured mock/zero and target-LLM calibration runs are carried by
  the focused tests above and experiment records; this contract only defines the current
  mechanism and acceptance boundary.
