---
doc_id: scenario.tidb.tidb_system_failure_sf01
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, system_failure, tidb_system_failure_sf01]
summary: Current code-backed contract snapshot for tidb_system_failure_sf01; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `tidb_system_failure_sf01`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `system_failure`
- Scenario implementation: `src.scenarios.tidb.system_failure.pd_metadata_recovery.TidbSystemFailureSf01Scenario`
- Formal entrypoint: `examples/run_tidb_system_failure_sf01_scenario.py`
- Current description: Investigates a TiDB write-latency and Region-placement incident and restores service and business integrity.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `pd_mixed_disk_eviction` | TiDB write latency and Region placement are unstable during a control-plane incident. | `hard` |
| 1 | `pd_mixed_disk_eviction_simple` | TiDB write latency and Region placement are unstable during a control-plane incident. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `pd_mixed_disk_eviction`

- Case number: `0`
- Title: TiDB write latency and Region placement are unstable during a control-plane incident.
- Alert/symptom: [CRITICAL] A portion of TiDB write traffic has become slower and Region leadership is uneven, while TiDB/TiKV endpoints and most business reads remain available. The incident window also contains component restarts, placement changes, storage telemetry, and unrelated business reconciliation noise. Determine whether the dominant issue is data/replica health, placement state, node/storage behavior, or transient workloa
- Initial-state fields: `evict_leader_scheduler`, `pd_leader`, `status`, `tikv_leader_distribution`
- Expected-target fields: `business_reconciliation`, `disk_fault`, `pd_scheduler`, `status`
- Background profiles: sf01_business_recent_paid_orders, sf01_business_settlement_dashboard, sf01_business_region_rollup_dashboard, sf01_business_exception_queue, sf01_business_reconciliation_drift, sf01_business_point_lookup, sf01_business_hot_row_touch, sf01_business_region_probe
- Evaluator: `src.scenarios.evaluation.tidb.system_failure.pd_metadata_recovery.TidbSystemFailureSf01ForPdMixedDiskEvictionEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): manage_cluster(service/list)=3/6; manage_cluster(store/list)=3/0; manage_cluster(scheduler/list)=1/4; manage_cluster(region/list)=79/0; query_metrics(disk_io)=5/65; read_log(pd)=18/39

### `pd_mixed_disk_eviction_simple`

- Case number: `1`
- Title: TiDB write latency and Region placement are unstable during a control-plane incident.
- Alert/symptom: [CRITICAL] A portion of TiDB write traffic has become slower and Region leadership is uneven, while TiDB/TiKV endpoints and most business reads remain available. The incident window also contains component restarts, placement changes, storage telemetry, and unrelated business reconciliation noise. Determine whether the dominant issue is data/replica health, placement state, node/storage behavior, or transient workloa
- Initial-state fields: `evict_leader_scheduler`, `pd_leader`, `status`, `tikv_leader_distribution`
- Expected-target fields: `business_reconciliation`, `disk_fault`, `pd_scheduler`, `status`
- Background profiles: sf01_business_recent_paid_orders, sf01_business_settlement_dashboard, sf01_business_region_rollup_dashboard, sf01_business_exception_queue, sf01_business_region_probe
- Evaluator: `src.scenarios.evaluation.tidb.system_failure.pd_metadata_recovery.TidbSystemFailureSf01FocusedEvaluatorCase`
- Calibration evidence (tool m/n): manage_cluster.service_list=3/6; manage_cluster.store_list=3/0; manage_cluster.scheduler_list=1/4; manage_cluster.region_list=79/0; query_metrics.disk_io=3/77; read_log.pd_members=112/334

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
- **OP** is the evaluator's final-state and business-truth contract. The expected-target fields above identify the state boundary; accepted repairs and equivalent outcomes are defined by the evaluator. The re-written business audit event is accepted by its business identity (`event_amount` + `record_crc` with state `paid` and the seeded region code); the row's `event_id` and `settlement_day` need not equal the pre-failure values.
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.tidb.system_failure.pd_metadata_recovery.TidbSystemFailureSf01Scenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/system_failure/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_system_failure_sf01_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
