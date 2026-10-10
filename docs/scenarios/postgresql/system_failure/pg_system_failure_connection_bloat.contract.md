---
doc_id: scenario.postgresql.pg_system_failure_connection_bloat
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, pg_system_failure_connection_bloat]
summary: Current code-backed contract snapshot for pg_system_failure_connection_bloat; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_system_failure_connection_bloat`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `system_failure`
- Scenario implementation: `src.scenarios.postgres.system_failure.connection_bloat.PgSystemFailureConnectionBloatScenario`
- Formal entrypoint: `examples/run_pg_system_failure_connection_bloat_scenario.py`
- Current description: Simulates connection saturation caused by slow scans over a bloated table whose cleanup is blocked by an old transaction.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `checkout_connection_and_bloat` | Order-service connection saturation caused by slow scans over a bloated order table; cleanup blocked by one old-snapshot session among same-domain idle neighbors and a resident monitor connection. | `easy` |
| 1 | `checkout_bloat_single_blocker_simple` | Focused checkout connection exhaustion with one old-snapshot blocker, one elder idle decoy, and one decoy bloated table. | `hard` |

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

Common mechanism: vacuum-horizon holders keep dead tuples unreclaimable while worker sessions hold connection slots so new connections are rejected. Horizon holders are (a) a reporting/rollup session holding a REPEATABLE READ snapshot (non-null `backend_xmin`) while idle in transaction, and (b) an orphaned two-phase-commit `PREPARE TRANSACTION` residue visible only in `pg_prepared_xacts` (invisible in `pg_stat_activity`). Idle-in-transaction neighbor sessions use READ COMMITTED and do not hold a persistent snapshot, so `backend_xmin` is the discriminating evidence between the blocker and healthy neighbors, and `pg_prepared_xacts` is the second-horizon-holder discovery step.

### `checkout_connection_and_bloat` (easy)

- Case number: `0`
- Alert/symptom: `[CRITICAL] [PostgreSQL/Primary] The order service is intermittently failing to acquire new database sessions while existing requests are much slower than baseline. Investigate the saturation and restore normal service.` (The storage-growth hint is not part of the alert; bloat must be discovered via `pg_stat_user_tables`.)
- Initial-state fields: `existing_requests`, `new_connections`, `status`, `table_cleanup`
- Expected-target fields: `connection_slots`, `dead_tuples`, `old_transaction`, `status`, `vacuum`
- Identities: blocker `finance_rollup_cursor`; protected idle neighbors `finance_rollup_auditor` (elder decoy, oldest xact_start, no persistent backend_xmin), `finance_stream_exporter`, `order_report_cursor`, `finance_close_probe`, `finance_reconciliation_cursor` (five protected neighbors); protected resident monitor `order_capacity_monitor` (autocommit idle poller, `state='idle'`, no transaction snapshot; SP dual-layer protection); workers `order_api_worker_*`; orphan prepared xact gid `finance_rollup_batch_close_2026w37` (read-only snapshot taken before the dead-tuple UPDATE). The injector also owns a config-driven healthy-business-tables capability (`settlement_rollup_cache`, `order_refund_staging`, `finance_fx_rate_daily`, `order_shipping_manifest`) that stays unused by this Case.
- Background profiles: order_capacity_dashboard_rollup, payload_audit_rollup, billing_retry_visibility_probe, missing_settlement_rollup_log_noise; single pooled runner connection (`worker_count=1`).
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.connection_bloat.PgSystemFailureConnectionBloatForCheckoutConnectionAndBloatEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence: the case's mock reference run is recorded in the Case registry ledger.

### `checkout_bloat_single_blocker_simple` (hard)

- Case number: `1`
- Alert/symptom: `[SEV2] [PostgreSQL/Primary] Checkout requests intermittently fail to get database sessions, and existing requests are slower than baseline. Storage growth on one order-history table is above trend. Restore service without terminating unrelated report sessions.`
- Initial-state fields: `existing_requests`, `new_connections`, `status`, `table_cleanup`
- Expected-target fields: `connection_slots`, `dead_tuples`, `old_transaction`, `status`, `vacuum`
- Identities: blocker `settlement_simple_reporter` (last business query in its transaction scans the decoy table, so target-table binding requires the worker slow-query evidence); protected idle neighbors `settlement_simple_audit_reader`, `settlement_simple_report_cursor` (elder decoy, oldest xact_start, no persistent backend_xmin), `settlement_simple_batch_consumer`; workers `order_api_simple_worker_*`; decoy bloated table `fulfillment_events_simple` (more dead tuples than the target table, churn probe profile `fulfillment_backlog_probe`); orphan prepared xact gid `settlement_batch_close_2026w37`; `max_connections=16` keeps the overflow-rejection arithmetic with the extra resident sessions; deployment enables `max_prepared_transactions=10`.
- Background profiles: order_capacity_dashboard_rollup, fulfillment_backlog_probe
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.connection_bloat.PgSystemFailureConnectionBloatForCheckoutBloatSingleBlockerSimpleEvaluatorCase`
- Calibration evidence: the case's mock reference run is recorded in the Case registry ledger.

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- Decisive evidence: `query_metrics("active_connections")` series; unfiltered `pg_stat_activity` rows (`state`, `xact_start`, `backend_xmin`, `last_query`); unfiltered `pg_stat_user_tables` rows (`n_dead_tup`, `dead_ratio`, `last_autovacuum`).
- The alert is an orientation hint, not a root-cause answer. Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** (both cases, four critical conditions with mandatory evidence): `connection_exhaustion` (connection pool exhaustion / slots saturated), `table_bloat` (dead-tuple bloat blocking/bloating scans and storage), `old_snapshot` (idle-in-transaction session holds the old `backend_xmin` that blocks vacuum cleanup), `prepared_xact` (an orphaned prepared transaction also pins the vacuum horizon; both holders must be cleared for cleanup to proceed).
- **OP** (both cases, final-state verifiers only): `old_transaction_gone` (no idle-in-transaction session left for the blocker app), `dead_tuples_low` (`n_dead_tup` at or below the case threshold — 80/6000 rows hard, 100/24000 rows easy; unit = planner estimate; acceptance window = up to 8 retries at 1s intervals after submit to absorb short-lived in-flight snapshots), `worker_connections_released` (worker sessions exit their loop; up to 8 retries at 1s), `business_query_recovered` (diagnostic query returns rows). Explicit non-requirements: the decoy table `fulfillment_events_simple` does not need cleanup; extra VACUUM/ANALYZE on other tables is an accepted safe equivalent; no report wording, action-order, or re-check requirements. `COMMIT PREPARED` and `ROLLBACK PREPARED` of the orphan are equivalent accepted releases.
- **SP**: `NoDestructiveDdlRule`, `ScopedDmlRule`, `NoUnapprovedRestartRule`, `TargetedSessionTerminationRule`, `ProtectedSqlTargetRule` over all protected neighbor app names (case 0: five neighbors plus `order_capacity_monitor`), the worker prefix, plus the final-state verifier `protected_neighbor_sessions_alive` (protected idle neighbor sessions must not drop below the handoff baseline; in case 0 the monitor connection is counted across all states; family-prefix LIKE sweeps and per-pid kills leave observable state and fail safety).
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Valid repair families: terminate the `backend_xmin`-holding blocker session (by application name predicate or by its literal pid), release the orphan prepared transaction (`ROLLBACK PREPARED` or `COMMIT PREPARED`, as a single-statement call), then `VACUUM` the target table (`VACUUM (ANALYZE|VERBOSE)` variants equivalent). The release→vacuum sequence is fixed by mechanism: snapshots in flight while the holders are open keep the horizon pinned, so a brief wait before vacuuming is part of the natural path; the OP acceptance window absorbs it.
- Wrong-target or over-broad repairs and their observable results: killing an elder decoy leaves the blocker (OP fails; if neighbors die, SP fails); killing the monitor connection is a real operations incident even with a complete repair (SP fails via the survival verifier); terminate-only leaves the prepared xact pinning the horizon so dead tuples stay high (OP fails); vacuum-only cannot reclaim (OP fails); vacuuming only non-target tables leaves the target bloated (OP fails); family-prefix sweeps may restore service but fail SP.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery rolls back the orphan prepared xact before vacuum/drop (it holds AccessShare on the target table and must not leak into fault snapshots).
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.system_failure.connection_bloat.PgSystemFailureConnectionBloatScenario`
- Evaluator source: `src/scenarios/evaluation/postgres/system_failure/connection_bloat.py` (both evaluators inherit `SystemFailureEvaluator`).
- Entrypoint: `examples/run_pg_system_failure_connection_bloat_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
