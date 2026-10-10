---
doc_id: scenario.tidb.tidb_system_failure_br_permission
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, system_failure, tidb_system_failure_br_permission]
summary: Current code-backed contract snapshot for tidb_system_failure_br_permission; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `tidb_system_failure_br_permission`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `system_failure`
- Scenario implementation: `src.scenarios.tidb.system_failure.br_permission.TidbSystemFailureBrPermissionScenario`
- Formal entrypoint: `examples/run_tidb_system_failure_br_permission_scenario.py`
- Current description: Diagnoses a failed table-backup path and produces a verified backup.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `br_s3_credentials_denied` | Nightly table backup SLO is breached while foreground data remains available. | `hard` |
| 1 | `br_s3_binding_focus` | Nightly table backup SLO is breached while foreground data remains available. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from old prose labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `br_s3_credentials_denied`

- Case number: `0`
- Title: Nightly table backup SLO is breached while foreground data remains available.
- Alert/symptom: [CRITICAL] The nightly table-backup SLO has been breached repeatedly. The source ledger remains readable and foreground requests are serving, but the latest backup attempt is not usable. Separate source-data integrity, database/backup execution, job history, and remote-storage evidence; identify the failed stage, restore a verified backup, and keep source data and unrelated backup-control records unchanged.
- Initial-state fields: `backup`, `source_table`, `status`
- Expected-target fields: `backup`, `objects`, `source_table`, `status`
- Background profiles: ledger_event_lookup, ledger_dashboard_rollup, ledger_reconciliation_rollup, backup_history_audit, ledger_payload_risk_probe, backup_credential_inventory_audit, ledger_recent_event_window, ledger_amount_bucket_rollup, ledger_payload_prefix_scan, ledger_backup_join_reconciliation, backup_history_failure_rollup, backup_history_object_prefix_sweep
- Evaluator: `src.scenarios.evaluation.tidb.system_failure.br_permission.TidbSystemFailureBrPermissionEvaluatorCase`
- Difficulty: hard; D=24; C_s family ledger SQL/catalog 750/811=0.924784, workload/operation event 2/13=0.153846, C=0.539315; reference=reference-237__tidb_system_failure_br_permission__br_s3_credentials_denied__mock__r001
- Calibration evidence (tool m/n): manage_cluster(job=get)=2/0; manage_cluster(job=refresh_binding)=3/0; execute_sql(backup_job_history)=1/60; execute_sql(backup_runtime_bindings)=5/239; execute_sql(backup_credentials)=5/243; execute_sql(backup_credential_scope_grants)=2/6; execute_sql(backup_authority_grant_leases)=9/9; execute_sql(cluster_statements_summary)=0/50; execute_sql(backup_worker_leases)=7/9; execute_sql(backup_worker_registry)=7/10; execute_sql(backup_worker_materials)=3/5; execute_sql(backup_request_material_cache)=6/10; execute_sql(backup_job_dispatches)=3/44; execute_sql(backup_dispatch_routes)=6/48; execute_sql(backup_storage_request_attempts)=11/2; execute_sql(backup_storage_audit)=1/17; execute_sql(source_truth)=1/0

### `br_s3_binding_focus`

- Case number: `1`
- Title: Nightly table backup SLO is breached while foreground data remains available.
- Alert/symptom: [CRITICAL] The nightly table-backup SLO has been breached repeatedly. The source ledger remains readable and foreground requests are serving, but the latest backup attempt is not usable. Separate source-data integrity, database/backup execution, job history, and remote-storage evidence; identify the failed stage, restore a verified backup, and keep source data and unrelated backup-control records unchanged.
- Initial-state fields: `backup`, `source_table`, `status`
- Expected-target fields: `backup`, `objects`, `source_table`, `status`
- Background profiles: ledger_event_lookup, backup_history_audit, backup_credential_inventory_audit, backup_target_candidate_audit, backup_runtime_binding_watch, backup_effective_binding_lookup, backup_binding_propagation_audit, backup_current_job_binding_join
- Evaluator: `src.scenarios.evaluation.tidb.system_failure.br_permission.TidbSystemFailureBrPermissionFocusedEvaluatorCase`
- Difficulty: easy; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). Reference run: `reference-233__tidb_system_failure_br_permission__br_s3_binding_focus__mock__r001`.
- Calibration evidence (tool m/n): execute_sql(backup_job_history)=2/59; execute_sql(backup_runtime_bindings)=8/89; execute_sql(backup_credentials)=8/91; execute_sql(backup_credential_scope_grants)=12/11; execute_sql(backup_authority_grant_leases)=26/5; execute_sql(backup_worker_leases)=8/17; execute_sql(backup_worker_registry)=8/17; execute_sql(backup_worker_materials)=7/4; execute_sql(backup_job_dispatches)=6/43; execute_sql(backup_dispatch_routes)=10/54; execute_sql(backup_request_material_cache)=8/14; execute_sql(backup_storage_request_attempts)=12/2; execute_sql(backup_storage_audit)=3/15; execute_sql(backup_storage_quarantine_tickets)=1/0; execute_sql(source_truth)=1/1; manage_cluster(job observe)=3/13.
- Entity decoys and fixture profile (focused case only): production-family look-alike credentials 230/231/232 with active production-scope materials and newer canary bindings 224/225/226; closed-window or expired production-URI grants (10/11/13/14/15/21) plus rehearsal-only grants (12/16/19/20) for the decoys and the true credential; authority-lease shadow rows 35/36/40/42/43 whose observed grants fail observed-material, window, or epoch validation; r3 moved the causal authority lease from id 17 to id 46 (this Case only; the base causal row 17 is absent here); r4 pruned the r3 descriptor shadows 37/38/39/41/44 (under sentinel semantics they would share the causal lease's full identity) and trims the background credential/binding inventory (220+20 -> 80+8 each) because this Case's difficulty comes from the derivation chain, not data volume.
- Desired-derivation semantics (focused case only): every focused authority-lease row stores the sentinel `desired_grant_id=0` ("the target grant is not materialized on lease rows"); the `refresh_binding` validator derives the expected desired grant in real time as the unique grant satisfying `credential = control-plane desired credential AND grant_scope = target scope AND grant_uri = production URI AND state = active AND window covers request_started_at`, and accepts only that value. No single row or single-table read carries the repair pair: the diagnostic path is h1 failed-request context (history/audit/attempts) -> h2 observed authority chain (route/registry/worker lease/cache/material -> credential 1902 -> rehearsal grants, fingerprint-pinned) -> h3 desired derivation (candidate credentials x grants window: "active + production URI + request-time window" matches grant 1 of credential 1901 plus grants 21/22/23 of the wave-2 canary credentials 232/230/231 (20261005-r7), so the causal credential is pinned only by the control-plane binding candidate and the healthy worker br-worker-1 serving credential 1901's production material; focused grant_source values are opaque work-order tokens, so the grant 1 vs previous-wave grant 18 choice requires the actual window comparison) -> h4 reconcile-target lease (unique row passing token x generation x epoch x fence x context x change_ref x observed-grant x window identity). Wrong-target refreshes are rejected with no state change; the only passing combination is (lease 46, observed 8, derived desired 1).
- Uniform refresh rejection (focused case only): the focused authority broker answers every `refresh_binding` identity-check failure — target worker, scope, attempt identity, route, registry, worker lease, authority epoch, request cache, material, observed/desired grant, authority lease, fence/context, change_ref — with one uniform rejection text that names no dimension and echoes no internal token, tuple, or fence pair; missing-parameter usage errors keep their protocol text. The accepted combination and the no-state property are unchanged. This removes the dimension-by-dimension error-feedback channel so the passing combination can only be assembled from the h1-h4 diagnostic derivation; the sibling Case `br_s3_credentials_denied` keeps its diagnostic rejection texts.
- Live controller epoch and storage-prefix quarantine (focused case only): the rotation controller completed an epoch promotion that the lease-table epoch columns do not reflect (paper trail lags the live state), so the refresh validator verifies `authority_epoch` against the controller's live promoted epoch; the live epoch is observable only on the read-only `manage_cluster(job, observe)` event stream (epoch promotion event, per-worker serving heartbeats, and unrelated noise events); 20261006-r10 makes that stream a rolling window — the default observe response returns only the most recent steady heartbeats, so the epoch promotion and quarantine entries must be read back with the explicit `start_timestamp`/`end_timestamp` window parameters, and the quarantine 403 text no longer carries the quarantine ref. 20261006-r11 supersedes the event-stream identity: the controller stream announces the quarantine without any release ticket, and the guard issues the release ticket into its own `backup_storage_quarantine_tickets` table (created empty by the fixture) only on the first denied write under the active quarantine — every denied write is also announced on the controller stream as a `storage_write_denied` event (no ticket number), so the release identity (ticket_ref, prefix, triggering_change_ref) exists only after the agent has attempted the denied backup and cannot be pre-emptively collected. Repeated denied writes have also tripped the bucket denial-rate guard: the backup prefix is quarantined, a correct-credentials backup rerun is denied with a quarantine-policy 403 naming the quarantine ref, and recovery requires the bounded `manage_cluster(job, release_prefix_quarantine)` operation presenting the target prefix, the quarantine ref from the event stream, and the triggering rotation change_ref; wrong identities are rejected with no state change. The focused OP contract gains the `prefix_quarantine_released` check; the sibling Case keeps the r61 four-check contract and its diagnostic rejection texts.
- Time-phased serving history and rotation-watch worker chains (focused case only): the healthy sibling's own worker-lease history gains a pre-rotation row (generation 104, serving the stale credential-1902 material, window closed 23:58:45) alongside its current converged production row, and two rotation-watch canary workers (br-worker-4/5) hold converged same-scope chains with their own dispatches, routes, registry assignments, and authority leases. The desired-credential pin therefore requires revision/window discrimination across several currently-serving rows instead of a single healthy-peer lookup, the reconcile-target worker can no longer be found by scanning for stale rows, and the wave-2 stage is rolled back mid-flight (bindings 224/225/226 to `rolled_back`, plus the true candidate's own rolled-back false start binding 227) while its pre-authorization grants 21/22/23 stay window-open. Grant 24 (the causal credential's open-window production grant on the sibling settlement table) forces grant_scope and grant_uri to be checked together. The refresh validator, accepted combination (lease 46, observed 8, derived desired 1), and DP/OP/SP contracts are unchanged.
- Wave-2 open-window production grants (focused case only): the entire in-flight wave-2 canary set — credentials 230, 231, and 232 behind the newer canary bindings 224/225/226 — now carries active production-URI grants whose windows cover the failed request (grants 22/23 join the r5 grant 21), so "active + production URI + request-time window" matches grants 1/21/22/23 across four candidate credentials. The validator's desired-grant derivation is unchanged (per-credential uniqueness inside the control-plane desired credential), so grants 21/22/23 remain non-refreshable decoys; the causal credential is still pinned only by the control-plane binding chain (effective binding 1900 on retired credential 1902, pending canary 1901) together with the healthy worker br-worker-1 serving credential 1901's production material, and the newer canary binding dates make recency heuristics point away from the causal credential.

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
- **OP** is the evaluator's final-state and business-truth contract. The expected-target fields above identify the state boundary; accepted repairs and equivalent outcomes are defined by the evaluator.
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.tidb.system_failure.br_permission.TidbSystemFailureBrPermissionScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/system_failure/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_system_failure_br_permission_scenario.py`
- Focused tests and reference runs are selected through `docs/index.md` and the related records; they are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
