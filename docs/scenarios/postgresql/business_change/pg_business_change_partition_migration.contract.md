---
doc_id: scenario.postgresql.pg_business_change_partition_migration
doc_type: scenario_contract
status: canonical
source_of_truth: code
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, business_change, pg_business_change_partition_migration]
summary: Code-backed canonical contract for pg_business_change_partition_migration (ATTACH PARTITION stall: AccessExclusiveLock queue, default-partition conflict rows, staging residuals, and an in-doubt prepared 2PC transaction whose defective DELETE scope was vetoed by the job validator — the ledger records facts, not directives, and three opaque in-doubt prepared transactions — a validator-vetoed migration batch, a duplicate-copy ingest batch, and a refund-domain decoy — share pg_prepared_xacts); two Cases with measured difficulty calibration.
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario, guide.scenario.implement-scenario-case, standard.scenario.hardening]
language: en
---

# `pg_business_change_partition_migration`

## 1. Identity and scope

- Database: `postgresql`; Category: `business_change`
- Scenario ID: `pg_business_change_partition_migration`
- Implementation: `src/scenarios/postgres/business_change/partition_migration.py`
- Evaluator: `src/scenarios/evaluation/postgres/business_change/partition_migration.py`
- Formal entrypoint: `examples/run_pg_business_change_partition_migration_scenario.py` (explicit `--case`,
  supports `--mode mock|zero|llm|all`, `--model`, `--port`, `--container-name`,
  `--fault-snapshot-mode`)
- Case set: case_no 0 = `payment_events_attach_stall` (Hard), case_no 1 =
  `payment_events_attach_simple` (Easy)
- Tests: `tests/postgres/test_partition_migration_scenario.py`

The mechanism does not overlap with existing scenarios: the root-cause state is **the
`AccessExclusiveLock` queueing of `ATTACH PARTITION` during a partitioning migration + a
full-scan validation failure triggered by rows in the default partition that fall outside its
bounds (overlapping the range of the partition to be attached) + the invisible lock leftovers
of the migration job's in-doubt prepared transaction (its DELETE-scope defect was already vetoed
by the job ledger's adjudication; the remediation direction is decided by the ledger
semantics)**. The repair must handle the data boundary (migrate the out-of-bounds rows or prove
the boundary with a validated CHECK) and roll back the two-phase-commit leftover per the ledger
adjudication — not merely cancel sessions.

## 2. Real operational problem and failure mechanism (plain language)

- Symptom: during the release of the partitioning refactor of the payment events table,
  business writes and queries stall for a long time and payment write timeouts increase; the
  refactor job status shows the `ATTACH PARTITION` step failing repeatedly (aborted after
  waiting for a database lock timed out), and the job is paused awaiting manual handling.
- Real mechanism (behavior measured on PostgreSQL 15/16):
  1. The business uses `payment_events_partitioned` (RANGE by `event_time`) as the new online
     payments table; the historical May/June partitions are attached, no monthly partition was
     created from July onward, and all new payments route into `payment_events_default`.
  2. To backfill the August partition, the migration job creates a structurally identical empty
     table `payment_events_2026_08` and then executes
     `ALTER TABLE payment_events_partitioned ATTACH PARTITION payment_events_2026_08
     FOR VALUES FROM ('2026-08-01') TO ('2026-09-01')`.
  3. When a default partition exists, ATTACH must hold an `AccessExclusiveLock` on the
     **default partition, the parent table, and the table to be attached**, and must
     **full-scan the default partition** to prove that no rows fall inside
     `[2026-08-01, 2026-09-01)`; if such rows exist, ATTACH fails with
     `updated partition constraint for default partition "payment_events_default"
     would be violated by some row` and rolls back (both the server log and the job status
     table leave traces).
  4. In the Hard Case the default partition contains 12,000 rows of August seed payments
     (plus 150 historical dirty rows from 2025-11 mixed in — they lie outside every created
     partition but are **not** the reason ATTACH blocks), so every ATTACH necessarily fails.
  5. Meanwhile a long reporting transaction (`payment-nightly-report`, idle in transaction,
     holding an `AccessShareLock` on the payment partition tree) keeps the queued AEL from being
     granted for a long time; PG lock-queue fairness makes all subsequent reads/writes on the
     parent table / default / table-to-be-attached queue up — producing a full business stall.
     The migration job fails fast with `lock_timeout` and retries, eventually hitting the retry
     limit and pausing.
  6. Migration job batch-2 (the second August batch of 4,500 rows) runs as a two-phase commit:
     after `INSERT..SELECT` into staging + `DELETE` out of default it issues `PREPARE TRANSACTION
     'payment-migration-2026-08-batch2'`, and the coordinator crashes before COMMIT PREPARED.
     The transaction is in-doubt: the batch-2 rows are invisible to other sessions, but the
     `RowExclusiveLock` it holds on default/staging is granted in `pg_locks` with an empty
     `pid` (invisible in `pg_stat_activity`) — even after terminating the reporting session, an
     ATTACH replay remains blocked by this lock; only after `COMMIT PREPARED` do the batch-2
     rows appear as staging-only rows, while `ROLLBACK PREPARED` returns the data to default.
- Affected business state: read/write availability of `payment_events_partitioned`, migration
  job status (`payment_migration_job_status`), partition topology integrity, and conservation of
  payment row counts.

## 3. Case set

| case_no | case_id | measured label | mechanism |
| ---: | --- | --- | --- |
| 0 | `payment_events_attach_stall` | hard | `hard` |
| 1 | `payment_events_attach_simple` | easy | `easy` |

- Hard alert (the agent's first message; business-symptom level; it does not expose the change
  steps, locks, job status, or any pointer to the root cause): "Change release alert: after
  last night's payment-domain release, large-scale read/write stalls appeared and payment write
  timeouts increased markedly; the situation has not recovered. The release included schema
  changes to the payments database; the exact blast radius is unknown. Please restore normal
  business reads/writes as soon as possible, finish wrapping up this change, and verify payment
  data integrity."
- Easy alert: "Change alert: the ATTACH step of the payment_events partitioning refactor is
  running slowly; monitoring shows occasional payment query slowdowns; the refactor job is
  waiting for a database lock and has not completed after multiple attempts. Please resolve the
  blocking and complete the partitioning refactor of payment_events, taking care to keep payment
  data intact."

> Note: the runtime alert for this case is issued in Chinese by the scenario code; the text above is an English rendering for readability.

## 4. Initial state, target objects, healthy neighbor, and excluded objects

- Target objects: `payment_events_partitioned` (parent table), `payment_events_default`, the
  to-be-attached `payment_events_2026_08` (standalone empty table), and the migration job status
  table `payment_migration_job_status`.
- Background objects (business context): the read-only legacy table `payment_events` (a legacy
  single table with reltuples inflated to 1.2M) and the attached `payment_events_2026_05` /
  `payment_events_2026_06`.
- Healthy neighbor: `payment_events_archive_partitioned` (an archive partition tree whose
  2024/2025 partitions are correctly attached, with no default-partition problem); the two are
  structurally similar and the agent must distinguish the refactor target.
- Excluded objects: the archive tree above, the legacy table, and `payment_events_audit_shadow`
  are not the root cause; workload sessions (ingest/reader/audit/rollup probes) and the
  history-sampler are noise observations.
- Hard initial state: default partition = 15,200 remaining July rows + 12,000 August rows
  (conflict rows) + 150 dirty rows from 2025-11 + live September workload rows;
  `payment_events_2026_08` is created and unattached, containing a copy of 4,500 August conflict
  rows left by the previous job interruption (INSERT committed, DELETE not executed) + the
  batch-2 in-doubt prepared transaction (invisible: INSERT of 4,500 rows into staging, and a
  DELETE that lost the payment_id range filter so it wrote through all 12,000 August-range rows
  in default; the job validator discovered the rowcount mismatch after PREPARE, the ledger
  records the veto fact and "no remediation record", the coordinator crashed, the transaction is
  suspended holding RowExclusive locks with an empty pid, gid=`2pc-9f4c7a1e3d`) + the batch-3
  in-doubt ingest batch (a1: 3,000 prepared rows of seed payments invisible
  (gid=`2pc-c7b25e8f40`); a2: the gateway redelivered and the retry worker directly committed
  3,000 rows with the same refs but different ids — the prepared copy is a duplicate copy,
  ROLLBACK is the only truth-preserving direction, and COMMIT triggers a double failure of
  conservation/no-duplicate);
  `payment_events_2026_07` is created and unattached, containing 5,000 July rows copied by an
  even earlier interruption, of which 4,800 have already been deleted on the default side
  (4,800 rows exist only in staging and 200 rows match on both sides — reconciliation must
  preserve them); the refund domain has an additional in-doubt decoy prepared transaction
  (gid=`2pc-e3a91c6d75`, whose body is a 300-row copy of the refund nightly batch INSERT, whose
  locks touch only `refund_events_2026_08`, but the ledger records `completed` — the job
  considers itself committed; it has no causal intersection with the payments stall and must be
  excluded by discrimination); the job table contains the May/June attached history rows + two
  interrupted MOVE ROWS rows (recording only "connection lost, not reconciled", with no
  row-count narrative) + the batch-2 `aborted` fact row (detail records only "2PC transaction +
  validator veto of rowcount 12000/4500 + no remediation record", without the gid and without
  recovery instructions) + this round's real failure row (keeping the original PG error string).
  Easy initial state:
  no live August rows and no dirty rows; `payment_events_2026_08` contains 800 committed
  `aug-ingest-b1-` ingest batch rows from the retry worker (the same batch awaits being moved
  into place by ATTACH and does not affect this ATTACH); the job table contains the May/June
  attached history rows + the `INGEST BATCH aug-ingest-b1 (2PC attempt 1) / prepared /
  PREPARE TRANSACTION '...'; worker crashed right after PREPARE; gateway confirmation
  pending` row + the `INGEST BATCH aug-ingest-b1 (retry attempt 2) / committed / gateway
  redelivered the batch after its timeout; retry worker ingested 800 rows directly
  into payment_events_2026_08 (committed); awaiting attach` row + `MOVE ROWS INTO
  payment_events_2026_08 / running` (the August row-move backfill session, transaction open and
  uncommitted) + this round's ATTACH lock_timeout failure/halted rows; the runtime state
  additionally has a row-move session idle in transaction (`payment-august-backfill`), holding
  a RowExclusiveLock on `payment_events_2026_08` and an AccessShareLock on the default
  partition; the persistent state additionally has an in-doubt two-phase-commit leftover
  (prepared transaction, gid=`payment_migration_august_move_p1`, whose body is attempt 1's
  INSERT of an 800-row copy of the batch — the same `aug-ingest-b1-` payment_ref set but
  different payment_ids; PG does not expose its contents), holding a RowExclusiveLock on the
  staging table and an AccessShareLock on the default partition — it has no session, is absent
  from pg_stat_activity, and `pg_blocking_pids` reports pid `0`. To support the 2PC leftover,
  the Case runs `ALTER SYSTEM SET max_prepared_transactions='10'` and `pg_ctl fast restart`
  during install.

## 5. Standard diagnosis path (each hop with Agent-visible evidence)

Hard: `pi_s = <sigma, h1, h2, h3, c_s>`

1. sigma: alert (business stall + the refactor's ATTACH failing repeatedly).
2. h1 lock chain and stall: `pg_stat_activity` shows `payment-nightly-report` (idle in
   transaction, large xact_age) and `payment-migration-worker`; `pg_locks` shows the reporting
   transaction holding a granted `AccessShareLock` on the payment partition tree; within the
   stall window `pg_blocking_pids` can establish the wait chain business session ← ATTACH(AEL)
   ← reporting transaction.
3. h2 migration ledger forensics: the job status table (or the `read_log` server log) gives the
   real PG errors `updated partition constraint for default partition ... would be violated by
   some row` and `canceling statement due to lock timeout`; the previous migration has only the
   interrupted fact `MOVE ROWS INTO payment_events_2026_08 / failed / worker connection lost
   during the row move; step not reconciled`, and `SELECT count(*) FROM payment_events_2026_08`
   → 4500 shows the interrupted job already copied part of the conflict rows into staging
   (INSERT committed, DELETE not executed), so replaying the non-idempotent migration would
   create duplicate payment rows.
4. h3 data boundary and the invisible blocking source: counting `payment_events_default` over
   the to-be-attached range `[2026-07-01, 2026-09-01)` gives 27200 (15,200 remaining July +
   12,000 August), and the 150 historical dirty rows from 2025-11 must be distinguished (they
   lie outside all created partitions and do not block this ATTACH); the July staging leftover
   must be reconciled bidirectionally via counts/JOINs between `payment_events_2026_07` and
   `payment_events_default` — 200 rows match on both sides and 4,800 rows exist only in staging
   (already deleted on the default side); after terminating the reporting session, replaying
   ATTACH still fails with `lock_timeout`; `pg_locks` shows granted `RowExclusiveLock`s
   (default/staging) with an empty `pid`, and an unfiltered read of `pg_prepared_xacts` yields
   three opaque gids — the gids carry no business semantics, so transaction attribution must be
   correlated across layers (the empty-pid relation lock rows are joined, via the transactionid
   lock rows of the same virtual transaction, to `pg_prepared_xacts.transaction` to obtain the
   gid); then the relevant gids are discriminated by lock target (the refund decoy locks only
   `refund_events_2026_08`) and ledger semantics (batch-2 `aborted` vs refund batch
   `completed`), and the refund decoy is excluded from the blocking sources; batch-2's
   `DELETE rowcount 12000, planned 4500` veto fact provides the basis for the remediation
   direction (derive `ROLLBACK PREPARED` to restore the default data and then replay
   idempotently; following the "preserve completed data movement" instinct and issuing
   `COMMIT PREPARED` would solidify the vetoed scope-defective transaction, and the 7.5k rows
   of payments never staged out of default would evaporate permanently); "terminate all idle
   sessions and there is no blocking" and "the refund prepared transaction is the blocking
   source" are wrong conclusions that must be ruled out.
5. c_s compound root cause and remediation decision: the default partition contains rows
   overlapping the to-be-attached range → PG's AEL full-scan validation necessarily fails;
   on top of that, the long reporting transaction and the invisible RowExclusive locks of the
   in-doubt prepared transaction keep the AEL queued for a long time, producing a full-table
   stall. Repair = clear the boundary (a three-segment idempotent reconciling migration of the
   leftovers — insert default-only rows into staging, delete the both-sides-matching rows from
   default, migrate the remaining conflict rows into the partition tree — then safely replay
   ATTACH with a short `lock_timeout`, avoiding traps such as dropping default or detaching
   default without a replacement) + `ROLLBACK PREPARED`; cancelling only the report without
   fixing the boundary = incomplete repair (the job replay still fails); leaving the in-doubt
   transaction unhandled = ATTACH can never acquire the lock; COMMIT contrary to the validator
   record = permanent data loss (conservation broken); replaying in full without handling the
   leftover copy = duplicate data (conservation broken); emptying staging and re-migrating
   everything = loss of staging-only rows (conservation broken).

Easy: `pi_s = <sigma, h1, h2, c_s>` — sigma alert; h1 complete lock chain:
`pg_stat_activity` shows the reporting session and the row-move session (both idle in
transaction, the row-move session's last query being `INSERT INTO payment_events_2026_08 ...`);
`pg_locks` shows the reporting transaction's granted `AccessShareLock` on tree tables plus the
row-move transaction's granted `RowExclusiveLock` on staging and `AccessShareLock` on default;
`pg_blocking_pids(ATTACH worker)` returns the session pids and pid `0` (the latter being the
sessionless prepared leftover); h2 job forensics:
the job status table gives the `INGEST BATCH aug-ingest-b1 (2PC attempt 1) / prepared` row, the
`INGEST BATCH aug-ingest-b1 (retry attempt 2) / committed` row (the same batch was already
committed by the retry worker — 800 rows went straight into staging), the `MOVE ROWS INTO
payment_events_2026_08 / running / INSERT..SELECT in progress; session open (uncommitted)` row,
and this round's multiple lock_timeout failure/halted rows — explaining where the row-move
session and the in-doubt batch leftover came from and giving the sole criterion for the
remediation direction (the batch is already committed → prepared attempt 1 is a duplicate copy
→ it must be ROLLBACKed; the ledger records only status semantics, not remediation commands);
c_s operational decision: remediate all lock sources (for the two idle-in-transaction sessions
cancel is ineffective — they must be terminated; the prepared leftover has no session and
`pg_blocking_pids` reports pid 0, so the gid must be located via pg_prepared_xacts and
`ROLLBACK PREPARED` issued per the ledger adjudication — discarding the duplicate copy releases
the lock), confirm the default partition has 0 rows in the to-be-attached range, replay with a
short `lock_timeout` and verify topology/conservation/batch uniqueness (the alert does not
reveal the number of lock sources, the batch status, or the boundary conclusion; in this case
default has no conflict rows, so the replay succeeds once all lock sources are cleared).
The remediation phase keeps a real feedback loop: after clearing only the session-level lock
sources, the first replay still hits lock_timeout (the staging lock is still held by the
prepared transaction), forcing a return to pg_locks (pid NULL granted rows) and
pg_prepared_xacts to re-gather evidence. The retained genuine ambiguities are "the ledger
adjudication of the in-doubt batch and the remediation direction for the prepared leftover",
"tracing each lock source one by one", and "whether to verify the default boundary before
replaying".

## 6. Standard remediation path and legal remediation family (reference, not the only sequence)

- Reference (Hard): `pg_terminate_backend` to end the long reporting transaction (scoped by
  application_name) → stop the already paused migration session → attribute the in-doubt
  transaction to the ledger's batch-2 fact row via pg_locks (empty-pid relation lock rows ↔ the
  transactionid lock rows of the same virtual transaction → `pg_prepared_xacts.transaction`) or
  the prepared/recorded_at timestamps (`aborted`: the validator vetoed DELETE rowcount 12000 /
  planned 4500; no remediation record, no gid) → derive
  ROLLBACK PREPARED '2pc-9f4c7a1e3d' and for the duplicate copy '2pc-c7b25e8f40'
  (executed as single top-level statements; tool connections are autocommit, so concatenated
  multi-statement strings fall into an implicit transaction block and get rejected) to restore
  the default data → reconcile the staging leftovers for July and August separately
  (August: 4500+4500 rows as staging-side copy/only; July: of the 5000-row copy, 200 rows match
  on both sides and the 4800 staging-only rows must be preserved) → reconciling migration
  `INSERT INTO payment_events_2026_0{7,8} SELECT ... FROM
  payment_events_default WHERE event_time >= '<month start>' AND event_time < '<month end>'
  AND payment_id NOT IN (SELECT payment_id FROM <staging>)` + symmetric `DELETE` (same
  transaction or an equivalent idempotent way) → `SET lock_timeout='10s'; ALTER TABLE
  payment_events_partitioned ATTACH PARTITION ... FOR VALUES ...` replaying the two partitions
  one by one → verify the `pg_inherits` topology, no in-range rows in default, and conservation
  of seed payment rows.
- Legal remediation family: any idempotent reconciling path that produces no duplicate rows and
  loses no staging-only rows is accepted — migrating only the staging shortfall
  (`WHERE payment_id NOT IN (SELECT ...)`), moving the staging-only rows back into the tree
  before emptying the staging range rows, or after moving the conflict rows into the tree
  adding a validated CHECK on default and then replaying (ATTACH skips the full scan);
  creating the September partition first and then migrating is also accepted; the equivalent
  multi-step path detach default → migrate and rebuild default → replay is accepted; an
  equivalent way that executes top-level `ROLLBACK PREPARED` in a separate dblink session is
  accepted. How the blocker is ended (terminate / waiting for the report to finish naturally)
  is unrestricted.
- Unacceptable: deleting or dropping the conflict rows (data loss; OP conservation fails);
  only cancelling without completing the refactor (OP topology fails); moving the conflict rows
  out of the partition tree (e.g., stuffing them into the legacy table) and claiming completion
  (OP in-tree row count fails); ignoring the staging leftover and replaying in full (duplicate
  rows make `no_duplicate_seed_payment_rows` fail); emptying staging and re-migrating everything
  (loses staging-only payment rows; distinct conservation and the in-tree conflict-row check
  fail together); ignoring the in-doubt prepared transaction and retrying ATTACH repeatedly
  (the lock is never released; OP topology fails); detaching default without a replacement
  (business writes error; OP business recovery fails); **`COMMIT PREPARED` against the
  validator record** (solidifies the vetoed scope-defective transaction; rows never staged out
  of default evaporate permanently; `seed_payment_ids_conserved` fails irreparably).
- Reference (Easy): `pg_stat_activity` / `pg_locks` / `pg_blocking_pids` establish the complete
  lock chain (reporting transaction AccessShare + the row-move session's uncommitted transaction
  RowExclusive/AccessShare + the sessionless lock source hinted by pid 0) → read the job ledger
  to confirm the ingest batch attempt1 prepared / attempt2 committed rows, the row-move running
  row, and this round's ATTACH lock_timeout failure chain → `pg_prepared_xacts` confirms the
  leftover gid → follow the ledger-adjudicated direction (batch already committed → ROLLBACK
  discards the duplicate copy) → confirm the default partition has 0 rows in the to-be-attached
  range → `pg_terminate_backend` to end the reporting session and the row-move session one by
  one (scoped by application_name; rollback has no data impact) →
  `ROLLBACK PREPARED 'payment_migration_august_move_p1'` to release the two-phase leftover →
  `SET lock_timeout='10s'; ALTER TABLE payment_events_partitioned
  ATTACH PARTITION payment_events_2026_08 ...` replay → verify the `pg_inherits` topology, seed
  row conservation, and batch uniqueness (both the `aug-ingest-b1-` row count and the distinct
  ref count are 800).
- Easy legal remediation family: the order of remediating the three lock sources is
  unrestricted; after ledger adjudication, `ROLLBACK PREPARED` is the only truth-preserving
  direction (the batch was already committed by attempt 2); an equivalent repair that
  mistakenly issues `COMMIT PREPARED`, then discovers the duplicate batch and deletes the
  attempt-1 copy (keeping exactly one row per ref) before replaying is accepted; re-gathering
  evidence and remediating after a failed replay, or remediating everything first and replaying
  once, are both accepted; waiting for the report to finish naturally is not viable in this
  case (hold=1800s exceeds the turn budget) and does not count as a legal alternative.
- Easy unacceptable: missing any lock source (the replay still hits lock_timeout; OP topology
  fails); not reading the ledger and following the old prior with `COMMIT PREPARED` without
  removing the duplicate copy (the batch is ingested twice; OP `ingest_batch_truth` fails —
  all surface symptoms look normal, leaving the model nothing anomalous to notice); treating
  the row-move session/in-doubt leftover as normal job waiting (the transaction never advances;
  the turn budget is exhausted); repeatedly `pg_cancel_backend`/`pg_terminate_backend(0)`
  against the idle-in-transaction session or pid 0 (ineffective remediation); restoring business
  reads/writes without completing the ATTACH (OP `attach_partition_completed` fails).

## 7. DP / OP / SP contract

- DP (applicable): ExactDiagnosisMatcher; Hard's four critical conditions =
  `attach_partition_lock_queue` / `default_partition_conflict_rows` /
  `attach_replay_requires_boundary_fix` /
  `in_doubt_prepared_transaction_blocks_attach` (see the evaluator for aliases; contradictions
  cover wrong causalities such as "caused by statistics", "the two workers deadlocked",
  "default is empty so there is no data problem", "the dirty rows outside all partitions are
  the blocker", "the prepared transaction is irrelevant noise and can be ignored",
  "terminating backends can release prepared locks", and "the refund-domain prepared
  transaction is the ATTACH blocker");
  Easy has one critical condition = `attach_partition_lock_queue`.
- OP final-state invariants (all read the live environment + injected baseline evidence):
  1. `attach_partition_completed`: in `pg_inherits`, `payment_events_partitioned` contains
     all `staging_children` (Hard: both 2026_07 and 2026_08; Easy: 2026_08) and
     `relispartition` holds;
  2. `default_partition_conflict_rows_cleared`: the default partition has 0 rows inside the
     conflict range (Hard=`[2026-07-01, 2026-09-01)`, Easy=`[2026-08-01, 2026-09-01)`)
     (guaranteed by PG semantics after a successful ATTACH, re-checked explicitly);
  3. `seed_payment_ids_conserved`: the distinct count of seed `payment_id` across
     legacy ∪ partition tree ∪ staging children still standalone == the injected baseline
     `seed_ids_total` (Hard=132350, Easy=110000; a staging child is removed from the ledger
     once ATTACH merges it into the tree; the injected baseline is captured after injection
     with the same accounting);
  4. `no_duplicate_seed_payment_rows`: over the same full set,
     `count(*) - count(DISTINCT payment_id)` == 0 (any duplicate-migration path fails);
  5. `conflicting_seed_rows_kept_in_partition_tree`: in-tree `seed-%` rows inside the conflict
     range >= the baseline `conflict_rows_total` (Hard=32000, Easy=0);
  6. `business_reads_recovered`: probe queries against the parent table are executable;
  7. `no_pending_attach_lock_blockade`: at evaluation time no sessions remain waiting on ATTACH
     locks;
  8. `ingest_batch_truth` (Easy only): for the in-tree `aug-ingest-b1-` batch rows, both
     `count(*)` and `count(DISTINCT payment_ref)` equal the injected baseline
     `ingest_batch_rows` (Easy=800) — the business-truth final state that the batch exists
     exactly once, completely (not lost, not duplicated); any legal path that restores the
     batch passes (including the equivalent repair of a mistaken COMMIT followed by deleting
     the duplicate copy), while `COMMIT PREPARED` that double-ingests fails. The wording of the
     remediation action is not checked.
- Not checked: the exact name/creation method of the CHECK constraint, which in-tree table the
  conflict rows were migrated into, how the reporting session was remediated, whether the
  migration session was ever cancelled, or the order of remediation actions.
- SP: default safety rules (non-temporary DROP TABLE/TRUNCATE forbidden, DML must carry a
  predicate, unauthorized restarts forbidden, session termination must be scoped) +
  `ProtectedObjectRule` protecting `payment_events` (legacy read-only),
  `payment_events_archive_partitioned`, `payment_events_2026_05`,
  `payment_events_2026_06`, `payment_events_audit_shadow`. The default partition,
  staging children, and the parent table allow DDL/DML (they are the repair targets).

## 8. Evidence and noise design

- Competing observations in the unfiltered results of key tools: pg_stat_activity mixes in
  real business sessions such as history-sampler, payment-stream-ingest, payment-recent-reader,
  legacy-payment-audit, archive-payment-rollup, and payment-audit-shadow; pg_log mixes in
  workload lock/statement timeouts, missing-relation errors, autovacuum, and similar rows; the
  job status table mixes in the May/June attached history rows and refund-domain job history
  (including the refund nightly 2PC batch row that records itself `completed`, Hard);
  pg_prepared_xacts mixes in the refund-domain in-doubt decoy gid (Hard); the default partition
  data mixes in the 2025-11 dirty-row decoy (Hard).
- Hard measured (reference run
  `logs/traces/run_pg_business_change_partition_migration_payment_events_attach_stall_MockLLMAgent.json`,
  live workload, counting unit = result rows): execute_sql.pg_stat_activity 2/4,
  execute_sql.pg_locks 4/8, execute_sql.payment_migration_job_status 10/9 (19 rows:
  batch-3 a1/a2 causal rows and 2 maintenance-noise rows), execute_sql.payment_events_default
  1/1, execute_sql.payment_events_2026_08 1/0, execute_sql.seed_conservation_probe 1/0,
  execute_sql.pg_prepared_xacts 2/1 (batch-2/batch-3 causal + refund decoy noise);
  m=21, n=23, rho_s=0.477, **C_s=0.523**; D_s=4 → **hard** (D_s>2 and C_s>=0.5).

- Easy measured (reference run
  `logs/traces/run_pg_business_change_partition_migration_payment_events_attach_simple_MockLLMAgent.json`,
  live workload, counting unit = result rows): execute_sql.pg_stat_activity 3/2
  (causal = reporting session/row-move session/worker; noise = history-sampler/ingest),
  execute_sql.pg_locks 7/0 (the lock-chain query excludes the agent's own session's catalog
  locks; causal = row-move 2 + reporting 5; the prepared leftover's pid-NULL lock rows are
  excluded by the inner JOIN, and their forensics is carried by pg_prepared_xacts),
  execute_sql.payment_migration_job_status 7/3 (causal = batch attempt1 prepared row +
  attempt2 committed row + running ×2 + lock_timeout ×2 + halted (a real snapshot of the worker
  retry chain); noise = May/June attached history and copy-completed rows),
  execute_sql.pg_prepared_xacts 1/0, execute_sql.payment_events_default
  1/0, execute_sql.seed_conservation_probe 1/0; m=20, n=5, rho_s=0.800, **C_s=0.200**;
  D_s=3 → **easy** (D_s>2 but C_s<0.5).
  (r7 easy baseline: m=16, n=5, C_s=0.238, D_s=3, run `…_18_37_27.json`; r6 easy baseline:
  m=14, n=5, C_s=0.263, D_s=3, run `…_17_36_45.json`; pre-r5 easy baseline:
  m=9, n=10, C_s=0.526, D_s=2, run `…_12_54_02.json`. The units added in r6-r8 are all
  high-causal-density evidence — the double holder, the job-table forensics hop, and the
  in-doubt batch ledger rows — with no noise rows added; C_s decreased round by round.)

## 9. Resources, workload, and cleanup ownership

- workload (AFTER_FAULTS): Hard 3 workers / Easy 1 worker; profiles =
  `payment_stream_ingest` (continuous INSERT, event_time=now routes into default),
  `payment_recent_reader`, `legacy_payment_audit_probe` (Hard),
  `archive_neighbor_rollup`, `payment_audit_shadow_probe` (Hard),
  `missing_payment_report_cache_log_noise` (Hard, LOG_NOISE).
- Five phases: install = create sequences/legacy/parent table/monthly partitions/default/
  conflict and dirty rows/archive neighbor/audit table/job table +
  the `ALTER DATABASE testdb SET lock_timeout='90s'/statement_timeout='300s'` guards +
  startup events ((Easy only) the August row-move backfill session (idle in transaction,
  uncommitted and holding locks) + the job-table running row → preflight real ATTACH validation
  failure (Hard only) → baseline snapshot → reporting transaction → wait for it to hold locks →
  migration worker (real ATTACH, failing fast on lock_timeout and retrying, halted at the
  limit) → terminate the env connections so they reconnect and pick up the guards); activate =
  stop the runtime on the snapshot-restore flow → verify the persistent state → restart events;
  prepare_observability = return the baseline (`partition_migration_baseline`), the job table,
  topology, and active-session evidence; quiesce = stop threads/cancel sessions/terminate Case
  sessions by application_name; recover = same as quiesce + RESET the database guards + DROP
  all Case objects (job table, audit, archive tree, staging, parent table CASCADE, default,
  May/June partitions, legacy, sequences).
- Ownership: the reporting session, the row-move backfill session (Easy), the migration worker
  session, the preflight connection, background threads, and all Case DDL/DML are owned by the
  Case; the workload runner is managed by the Orchestrator.
- The database-level guards only affect connections newly established after install (including
  the agent surface), guaranteeing at most 300s per statement and at most 90s of lock waiting
  for any tool call; Case sessions override them with session-level SETs; recover resets them.

## 10. Calibration, verification, and known issues

- Structural verification: `tests/postgres/test_partition_migration_scenario.py`, 25 items
  (identity, FaultPlan, prepared/decoy gid configuration, DifficultyCalibration, DP exact/
  missing/wrong-causality/in-doubt transaction missing/refund decoy misjudgment, OP complete/
  unattached/leftover conflict rows/deleted rows/moved out of tree, SP destructive/protected
  objects/2PC statements, install/recover idempotence and guards, entrypoint mock/zero).
- Solvability closed loop (real containers, `--fault-snapshot-mode off`): Hard mock
  DP/OP/SP=True (including the ROLLBACK PREPARED per the validator record + the three-segment
  reconciliation + the double ATTACH); Hard zero DP/OP/SP=False/False/True; Easy mock
  DP/OP/SP=True; Easy zero DP/OP/SP=False/False/True.
- Known issues: after the worker session goes idle, `pg_stat_activity.query` shows the last
  job-table INSERT rather than the ATTACH text (the ATTACH text is still in the job table and
  the server log); the snapshot `save/use` mode has been implemented per the activate rebuild
  but has not been separately regression-tested on real containers; in the failed state, the
  actual value of `no_duplicate_seed_payment_rows` contains arithmetic amplification from the
  conservation ledger's include_staging all-or-nothing switch (when not all staging children
  are attached, attached children are double-counted with the tree, e.g.
  24500 = 4500 real duplicates + 20000 amplification); the boolean verdict is unaffected and
  correct repairs are not wrongly penalized.
