---
doc_id: scenario.tidb.tidb_health_check_empty_region_leader_skew
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, health_check, tidb_health_check_empty_region_leader_skew]
summary: Current code-backed contract snapshot for tidb_health_check_empty_region_leader_skew; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `tidb_health_check_empty_region_leader_skew`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `health_check`
- Scenario implementation: `src.scenarios.tidb.health_check.empty_region_leader_skew.TidbHealthCheckEmptyRegionLeaderSkewScenario`
- Formal entrypoint: `examples/run_tidb_health_check_empty_region_leader_skew_scenario.py`
- Current description: Routine TiDB health check that distinguishes business-query noise from region inventory and leader/store scheduling-capacity risk.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `regional_job_empty_region_skew_review` | Routine TiDB capacity review with mixed business traffic and an unresolved regional scheduling risk. | `hard` |
| 1 | `recent_split_window_region_review` | A bounded TiDB Region review separating persistent empty Regions from a recent split window. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `regional_job_empty_region_skew_review`

- Case number: `0`
- Title: Routine TiDB capacity review with mixed business traffic and an unresolved regional scheduling risk.
- Alert/symptom: [Routine TiDB Fleet Review] The weekly capacity health-check queue has one open item for the regional jobs cluster. User-facing latency and PD CPU are still below paging thresholds, but the review window overlaps checkout, merchant rollup, audit, DDL, and backup activity. Separate ordinary business-query noise from topology risk, then close the stored review row with evidence, impact, and a bounded remediation plan.
- Initial-state fields: `business_window`, `pd_cpu`, `review_key`, `status`
- Expected-target fields: `bounded_plan`, `business_checksum`, `risk`, `status`, `structured_review`
- Background profiles: checkout_probe, merchant_rollup, audit_reconciliation, ops_queue_probe, dashboard_refresh, region_sampler, scheduler_snapshot, window_reconciliation, tenant_heatmap, raft_observer, backup_heartbeat, ddl_watch
- Evaluator: `src.scenarios.evaluation.tidb.health_check.empty_region_leader_skew.TidbHealthCheckEmptyRegionLeaderSkewForRegionalJobSkewReviewEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): query_metrics(region_count)=60/33; query_metrics(topsql)=0/50; query_metrics(workload_activity)=0/16; hc03_pd_region_samples=5/36; hc03_pd_config=3/21; hc03_region_inventory=1/0; hc03_store_distribution=3/0

### `recent_split_window_region_review`

- Case number: `1`
- Title: A bounded TiDB Region review separating persistent empty Regions from a recent split window.
- Alert/symptom: 例行 Region 健康复核：最近 split 窗口出现一批短时 empty Region，同时仍有少量长期 zero-key Region。请用库存年龄、短窗口趋势、PD 调度快照和 store leader 分布区分两类现象，写入有边界的 review 结论。本次只允许记录复核，不重启组件、不修改业务表和调度配置。
- Initial-state fields: `review_key`, `status`, `window`
- Expected-target fields: `business_checksum`, `persistent_region_risk`, `recent_split_window_excluded`, `status`
- Background profiles: checkout_probe, merchant_rollup, audit_reconciliation, ops_queue_probe, dashboard_refresh, region_sampler, scheduler_snapshot, window_reconciliation, tenant_heatmap, raft_observer, backup_heartbeat, ddl_watch
- Evaluator: `src.scenarios.evaluation.tidb.health_check.empty_region_leader_skew.TidbHealthCheckEmptyRegionLeaderSkewForRecentSplitWindowEvaluatorCase`
- Calibration evidence (tool m/n): hc03_region_inventory=1/1; hc03_pd_region_samples=3/3; hc03_pd_config=1/1; hc03_store_distribution=1/0

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
- **OP** is the evaluator's final-state and business-truth contract. The expected-target fields above identify the state boundary; accepted repairs and equivalent outcomes are defined by the evaluator.
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.tidb.health_check.empty_region_leader_skew.TidbHealthCheckEmptyRegionLeaderSkewScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/health_check/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_health_check_empty_region_leader_skew_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
