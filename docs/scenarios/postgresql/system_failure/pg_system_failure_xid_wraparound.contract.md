---
doc_id: scenario.postgresql.pg_system_failure_xid_wraparound
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, system_failure, pg_system_failure_xid_wraparound]
summary: Current code-backed contract for pg_system_failure_xid_wraparound; payment_ledger_xid_wraparound is a recurring-batch wraparound incident behind an identity-neutral multi-job control surface with a public five-state lifecycle (paused auto-resumed by the nightly recon sweeper), an upstream configuration-as-code provisioning pipeline (ops_batch_control_template + batch_control_provisioner) that restores runtime-only cancellations, desired-state worker convergence, explicit-freeze ownership, and commit-channel recovery acceptance, alongside the frozen billing_freeze_blocked_simple case.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_system_failure_xid_wraparound`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `system_failure`
- Scenario implementation: `src.scenarios.postgres.system_failure.xid_wraparound.PgSystemFailureXidWraparoundScenario`
- Formal entrypoint: `examples/run_pg_system_failure_xid_wraparound_scenario.py`
- Current description: Simulates transaction age exhaustion with maintenance blocked by a long business transaction.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `payment_ledger_xid_wraparound` | Order commits fail while a recurring settlement replay batch keeps blocking anti-wraparound maintenance on the only wraparound-critical relation; the batch control row is re-provisioned from a configuration template, so only retiring the template layer makes a cancellation stick. | `hard` |
| 1 | `billing_freeze_blocked_simple` | One old billing transaction blocks freeze maintenance on the oldest relation. | `hard` |

## 3. Mechanism, initial state, and target

### `payment_ledger_xid_wraparound`

- Case number: `0`
- Mechanism: `pg_resetwal` pushes nextXID to 500000000 after a completed maintenance window froze every other public relation, so `payment_ledger` is the only relation left near the wraparound horizon. Two `settlement_replay_worker` batch sessions hold `payment_ledger` under SHARE in staggered shifts (hold 12s, gap 6s, phase offset 9s), blocking all anti-wraparound maintenance and stalling the checkout order-commit INSERT stream against the table. The workers are desired-state workers for the shared `ops_batch_control` row `ledger_settlement_replay`: `running` is the only state that runs a hold cycle; every other state (`paused`, `cancelled`, `pending`, `completed`, missing row) drains the worker into a standby park under the `settlement_replay_supervisor` probe identity, and the worker re-arms only when the row reads `running` again. The control row is managed by an upstream configuration-as-code pipeline: the public template table `ops_batch_control_template` (enabled/disabled templates + COMMENT) is replayed into `ops_batch_control` every 30s tick by the `batch_control_provisioner` job (persistent session, one `RAISE LOG` evidence line per tick) — a control row that is missing or left `cancelled` is restored to `running` from its enabled template, so a runtime-only cancellation reverts and the batch comes back. Retiring the template row (or cancelling the provisioner's own control row) before stopping the runtime row is required for a permanent stop. The `nightly_recon_sweeper` (10s cycle) auto-resumes rows parked in `paused` longer than 20s so settlement batches make their cutoff; the sweeper only touches `paused` rows and the provisioner only restores missing/`cancelled` rows, so their scopes never overlap (both documented publicly). The control table also carries `daily_margin_rollup` (already completed), a genuinely running `checkout_retry_sweep` dedup job that appends benign duplicate-order-ref rows into `checkout_commit_failures`, a `pending` chargeback batch, and a `cancelled` `ledger_archive_prune` whose template is retired — the public counter-example of a cancellation that stays. `autovacuum=off` plus `autovacuum_freeze_max_age=2000000000` keep freeze ownership explicit: neither forced anti-wraparound autovacuum nor a plain VACUUM (non-aggressive at this freeze budget) can clear the age, so an explicit `VACUUM (FREEZE)` is required. A checkout commit writer (~1 order/second) records each timed-out commit into `checkout_commit_failures` and, like a real payment service, reconnects after out-of-band session termination.
- Alert/symptom: user-visible only — intermittent order commit failures since the settlement replay batch opened its window, repeated aborted ledger maintenance, self-recovered replica-lag warning; no xid/age/blocker wording.
- Initial-state fields: `status`, `transaction_age_budget`, `maintenance`, `order_commit_channel`
- Expected-target fields: `status`, `transaction_age`, `maintenance`, `order_commit_channel`
- Background profiles: none declared (noise, workers, writer, retry sweep, recon sweeper, and provisioner are injector-owned sessions)
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.xid_wraparound.PgSystemFailureXidWraparoundForPaymentLedgerXidWraparoundEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Reference path: age census → incident observation → lock topology → control-surface read → template-table read → table comment → provisioner log evidence → worker flag-query sample via pg_stat_statements → retire the governing template row → cancel the governing control row → explicit vacuum freeze → verify age/blockers → verify commit channel across the acceptance window.

### `billing_freeze_blocked_simple`

- Case number: `1`
- Title: A forgotten prepared transaction and an idle blocker jointly pin the wraparound horizon on the oldest billing relation.
- Alert/symptom: Alert: the billing primary remains available, but its transaction-age budget is nearly exhausted and scheduled maintenance cannot progress. One low-rate billing health probe is active. Identify the relation and session holding maintenance back, then restore safe age headroom without broad session termination.
- Initial-state fields: `maintenance`, `status`, `transaction_age_budget`
- Expected-target fields: `maintenance`, `status`, `transaction_age`
- Background profiles: billing_health_probe
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.xid_wraparound.PgSystemFailureXidWraparoundForBillingFreezeBlockedSimpleEvaluatorCase`
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).
- Calibration evidence (tool m/n): execute_sql.pg_class_age=1/5; execute_sql.pg_stat_activity=1/12; execute_sql.pg_prepared_xacts=1/0. This case keeps the frozen composite mechanism (forgotten prepared transaction + protected settlement session + explicit freeze); changes to the composite mechanism require an explicit contract revision.

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- Payment case evidence surfaces: `age(datfrozenxid)`/`age(relfrozenxid)` contrast between `payment_ledger` and its frozen healthy neighbors; `pg_locks`/`pg_stat_activity` SHARE holders and the waiting commit INSERT; the mixed-class `checkout_commit_failures` business truth; the workers' own flag query (visible in `pg_stat_activity` samples and accumulated in `pg_stat_statements`); the `ops_batch_control` rows, their `provisioned_from` column, and the table/column comments; the `ops_batch_control_template` rows and table comment; the `batch_control_provisioner` per-tick `RAISE LOG` lines (including the restored-row list); and the provisioner/recon-sweeper sessions in `pg_stat_activity`/`pg_stat_statements`.
- The alert is an orientation hint, not a root-cause answer. Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP (payment)** — `_LEDGER_XID_DP`: (1) transaction age near wraparound; (2) the settlement replay batch / its idle sessions hold `payment_ledger` and block freeze; (3) `payment_ledger` is the critical relation; (4) cancel/stop the settlement replay batch and vacuum freeze the payment ledger. The upstream provisioning layer belongs to repair completeness and is owned by the OP final state, not by diagnosis wording. The simple case keeps `_SIMPLE_XID_DP` (age + idle blocker + relation).
- **OP (payment)** — all must pass on final state: `xid_age_safe` (`age(relfrozenxid)` of `payment_ledger` < 100000 xids), `freeze_blocker_gone` (zero `settlement_replay_worker` sessions sustained across a bounded window: settle 14s, then 12 samples at 1s intervals — a killed worker respawns inside ~2.5s and re-enters its 12s SHARE hold, so a permanently stopped batch is the only way to keep the window all-zero), `order_commit_channel_recovered` (≥ 22 committed orders inside the trailing 45-second window of `payment_ledger.updated_at`; business basis: the checkout commit baseline sustains ~1 order/second, so the bar certifies roughly 22 seconds of sustained post-recovery throughput — the acceptance spans a write cycle; units: committed orders; window: trailing 45s), and `sql_probe`. Not checked: restoring `paused=false`, report keywords, action order or SQL spelling, RTO, cleanup.
- **OP (simple)** — `xid_age_safe`, `freeze_blocker_gone`, `sql_probe` (unchanged).
- **SP** — default shared rules for both cases; the simple case adds `_ProtectedSessionAliveVerifier` for `billing_settlement_batch`. The payment case control actions (`UPDATE`/`DELETE` on `ops_batch_control` or `ops_batch_control_template` with a `job_name` predicate) are scoped, business-grounded control actions and pass the default rules; dropping the template table (or the control table) itself is destructive DDL and fails `no_destructive_ddl`.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../standards/evaluation/dp-op-sp.standard.md).

## 6. Repair, ownership, and recovery

- Payment case valid repair families: permanently stop the settlement replay batch by handling BOTH the template layer and the runtime row — retire the template (`UPDATE ops_batch_control_template SET enabled=false ... WHERE job_name='ledger_settlement_replay'`, delete the template row, or cancel the `batch_control_provisioner` control row to stop provisioning) AND cancel or remove the `ops_batch_control` row `ledger_settlement_replay` (worker desired-state convergence drains and parks the workers either way) — then an explicit `VACUUM (FREEZE)` of `payment_ledger` (plain non-freeze VACUUM does not clear the age at this freeze budget; a database-wide `VACUUM FREEZE` after the stop is an accepted equivalent), then verify recovery across the acceptance window. Runtime-only cancellation or row removal reverts within one provisioning tick: the provisioner restores the row to `running` from its enabled template and the workers re-arm, so `freeze_blocker_gone` (sustained) and `order_commit_channel_recovered` fail. Stopping the provisioner without stopping the already-running batch leaves the SHARE holders in place and fails the outcome. Cancelling other job rows (e.g. `checkout_retry_sweep`) leaves the replay batch untouched. Pausing without freezing fails the age invariant.
- Simple case repair families remain as calibrated (terminate blocker + resolve the prepared transaction + explicit freeze; `COMMIT PREPARED` accepted as the horizon-clearing equivalent).
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery terminates the worker pool, commit writer, retry sweep, recon sweeper, and provisioner, resolves the prepared transaction when present, and freezes the target table through the five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.system_failure.xid_wraparound.PgSystemFailureXidWraparoundScenario` (payment hardening fields: `replay_worker_instances`, `commit_writer_enabled`, `batch_control_table`, `batch_control_job`, `batch_control_template_table`, `commit_failure_table`)
- Evaluator source: `src/scenarios/evaluation/postgres/system_failure/xid_wraparound.py` (`_LEDGER_XID_DP`, `_ORDER_COMMIT_RECOVERED`, `SustainedSqlScalarVerifier`/`_XID_BLOCKER_GONE_SUSTAINED` for payment; `_SIMPLE_XID_DP`, `_ProtectedSessionAliveVerifier` for the simple case)
- Entrypoint: `examples/run_pg_system_failure_xid_wraparound_scenario.py` (mock paths: `mock`, `zero`, `generic`, `kill_only`, `pause_only`, `pause_freeze`, `cancel_wrong_job`, `cancel_only`, `cancel_stop_provisioner`, `provisioner_only`, `drop_template_table`, `llm`)
- Focused tests: `tests/postgres/test_system_failure_evaluators.py`, `tests/postgres/test_fault_activation_contracts.py`, `tests/test_scenario_cases.py`
