---
doc_id: scenario.postgresql.pg_health_check_backup_rpo_certification
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, health_check, pg_health_check_backup_rpo_certification]
summary: Current code-backed contract snapshot for pg_health_check_backup_rpo_certification; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_health_check_backup_rpo_certification`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `health_check`
- Scenario implementation: `src.scenarios.postgres.health_check.backup_rpo_certification.PgHealthCheckBackupRpoCertificationScenario`
- Formal entrypoint: `examples/run_pg_health_check_backup_rpo_certification_scenario.py`
- Current description: Certifies a real PostgreSQL base backup and archive chain through an isolated PITR at a hidden business marker.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `throughput_gap` | Hard RPO certification with a real archive throughput gap and hidden target marker. | `hard` |
| 1 | `throughput_gap_simple` | Easy RPO certification with one bounded archive delay window and fewer markers; the diagnosis must locate the archive-stall window while the certification runbook stays end to end. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `throughput_gap`

- Case number: `0`
- Title: Hard RPO certification with a real archive throughput gap and hidden target marker.
- Alert/symptom: [Scheduled PostgreSQL DR Certification] Certify the last 12 hours of recovery capability against the approved 60-second RPO. Use bounded historical metrics and operation events, verify the physical backup and archive continuity, and perform an isolated point-in-time restore at the evaluator-selected business marker. Refuse certification and report the last recoverable boundary when the chain cannot support the target.
- Initial-state fields: `backup_toolchain`, `rpo_seconds`, `status`, `topology`
- Expected-target fields: `manifest`, `marker_checksum`, `pitr`, `status`
- Background profiles: `rpo_history_probe`; the Hard Case freezes public WAL generation, archive delivery, archive backlog, business commits, OLTP service, and backup progress history with three candidate-valley windows that replay the buried target capture's own channel shapes at the same depth, duration, and metric signature: `missing_precursor` flattens the WAL channels to the pre-incident regime (no generating burst behind the delivery collapse and backlog climb), `scrambled_order` replays the same values with the ordered causality broken (the backlog falls again while delivery stays collapsed), and `shadow_copy` is metrically identical to the incident window and carries only plausible-but-incomplete `archive_attempt` records (segment, checksum, and correlation identity stripped, no business-marker continuity). Overview and mid-granularity statistics cannot separate the valleys from the buried incident window; only operation-event evidence and the ordered wal-burst -> delivery-stall -> backlog-climb causality can. The stall signature exists only inside the buried target window: after the target capture the environment physically resolves the archive congestion and the run captures a real 180 s aftermath recovery (backlog drain), so the frozen tail returns to the normal regime instead of holding a plateau. The aftermath cleanup lifts only the congestion: the incident response downgrades `archive_command` to the emergency transmission tier (a rate-limited archive relay that keeps up with the idle segment cadence but cannot sustain the certification replay), and that residual raises no current-state metric anomaly at the post-aftermath load. `oltp_service` is a real bounded probe on `pgbench_accounts`, not a readiness `SELECT 1`.
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).
- Evaluator: `src.scenarios.evaluation.postgres.health_check.backup_rpo_certification.PgHealthCheckBackupRpoCertificationEvaluatorCase`
- Overview: the RPO environment serves the complete coarse frozen overview grid (about 90 points at the 480 s overview step for the 12-hour history) for no-window `query_metrics` calls regardless of an explicit limit; the newest-20-points shared overview budget does not apply to this catalog. The assembler anchors the target window so exactly one overview grid point falls inside its late half, and each candidate valley is placed so exactly one grid point falls inside its own span, so every valley competes as a coarse candidate next to the buried target. Bounded windows (max 900 s each) keep the full base grid, so the intended funnel is overview candidate (480 s) -> per-candidate base-grid confirmation and operation-event evidence (2 s) -> record-plus-causality exclusion of same-shape valleys.
- DP: applicable and deterministic (exact matcher, no LLM judge). The diagnosis must state three conditions: the located archive-delivery stall window, the throughput-gap root cause (archive delivery falling behind or stalling while WAL generation continues), and the RPO breach impact (recoverable point pushed beyond the approved 60-second RPO, including the public `rpo_not_met` restore result). The located UTC window is read from the diagnosis conditions' free-text evidence (the agents' own wording, no dedicated report field): a window is either two full UTC timestamps or a full timestamp with a same-day end time (`2026-09-15 14:39:00-14:54:00`, `to`/`until` spellings, ISO `T`/`Z`/`+00:00` accepted); it is accepted when it overlaps the frozen history's target window by at least 60 s (the approved RPO) and stays within the public 900 s bounded-query budget; missing, unparseable, non-overlapping, or oversized windows leave the window condition unsatisfied (`DiagnosisPass=False`). A tail/persistent-plateau window that does not reach back to the frozen stall event window fails the same condition. All window roles stay evaluator-internal.
- OP: purely end-to-end. The trusted manifest/inventory/isolated-PITR invariants above must all hold on the real environment's final state, and `recover_archive` must additionally pass the certification capacity replay: the recovery replays a declared WAL burst (8 segments) through the live archive route and requires every segment durable inside the 15 s publication envelope, so the residual emergency route physically fails the recovery until it is re-pointed at the publication tier that the frozen pre-incident operation-event records (`details.route`) expose. The evaluator does not parse the submit report for windows or certification text.
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `throughput_gap_simple`

- Case number: `1`
- Title: Simple historical RPO certification with an isolated business restore.
- Alert/symptom: [Scheduled PostgreSQL DR Certification] Validate the selected recovery target using bounded historical observations, the physical backup, archive inventory, and an isolated restore. Certify only after the marker boundary and checksum are verified. First read metric overviews without timestamps, then drill into a single bounded evidence window; never request the full 6-hour history. HARD TOOL BOUNDARIES: each historical metric/log window must be <=900 seconds; use only wal_generation, archive_delivery, archive_backlog, business_commits, oltp_service, backup_progress; use logical targets archive_repository, backup_repository, and evaluator_selected, never container filesystem paths.
- Initial-state fields: `backup_toolchain`, `rpo_seconds`, `status`, `topology`
- Expected-target fields: `manifest`, `marker_checksum`, `pitr`, `status`
- Background profiles: `rpo_history_probe`; the Simple Case uses the shorter public frozen-history history contract (6 hours) with four decoys: `simple-wal-burst-window` (captured benign WAL burst), `simple-backup-window` (metric-only backup-progress spike), `simple-archive-retry-window` (metric-only archive delivery failure-delta spike without backlog propagation), and `simple-delivery-quiet-window` (captured benign archive-delivery quiet segment that recovers by itself without backlog growth). The Simple history also captures a real 240-second aftermath immediately after the stall window: the assembled timeline ends the stall signature with the physically captured archiver catch-up (delivery catch-up, backlog drain) and returns to the normal regime for the remaining tail, so the fault signature exists only inside the target window; a tail query no longer reproduces it. The overview stays coarse (300-second step). The frozen history also carries the standard archive route binding as `repository_sync/route_config` operation events announced every 20 seconds of the normal capture, but the Simple history publishes these records only in its pre-incident strip: the assembled normal blocks within 480 seconds before the target window (a query window disjoint from the strip observes zero route-config records, so restoring the standard tier physically requires locating the incident neighborhood first; the former replay-into-every-normal-block guarantee was an information leak, not a solvability guarantee); the live instance state never publishes route values, so the frozen history's pre-incident strip is the only surface carrying the healthy tier. At incident close-out (after the aftermath capture, before the agent phase) the archive route is left bound to an emergency transport wrapper whose command shares no substring with the standard command and whose self-contained script never references the standard wrapper; its per-segment pacing is metric-invisible at the idle agent-phase load, and the `recover_archive` capacity replay is accepted at the standard delivery tier with an evaluator-side acceptance window that is never published.
- DP (Simple only): `diagnosis_applicable=True` with three critical conditions matched by the exact matcher — `archive_stall_window_located`, `archive_delivery_throughput_root_cause`, and `rpo_promise_violated_in_stall_window`. The located-window condition is verified deterministically against the trusted frozen stall window held in runtime state: the diagnosis evidence must cite a `<UTC start>/<UTC end>` window (multi-format parsing) that overlaps the stall window by at least 60 seconds (evaluator-side acceptance interval, not published) and spans at most the declared `max_history_query_seconds` budget. Equivalent window families all pass; the window may be cited in any submitted condition's evidence; parse failures or non-covering windows fail the located-window condition. The trusted stall window is never disclosed through public tools.
- Evaluator: `src.scenarios.evaluation.postgres.health_check.backup_rpo_certification.PgHealthCheckBackupRpoCertificationSimpleEvaluatorCase` using the shared `RpoCertificationOutcomeVerifier` (11 trusted physical artifact checks); `pitr_restore` keeps its original action semantics and derives the restore target from the internal hidden marker.

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

- Scenario and Case source: `src.scenarios.postgres.health_check.backup_rpo_certification.PgHealthCheckBackupRpoCertificationScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/health_check/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_health_check_backup_rpo_certification_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
