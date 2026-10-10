---
doc_id: scenario.tidb.tidb_business_change_table_recovery
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, business_change, tidb_business_change_table_recovery]
summary: Current code-backed contract snapshot for tidb_business_change_table_recovery; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `tidb_business_change_table_recovery`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `business_change`
- Scenario implementation: `src.scenarios.tidb.business_change.table_recovery.TidbBusinessChangeTableRecoveryScenario`
- Formal entrypoint: `examples/run_tidb_business_change_table_recovery_scenario.py`
- Current description: Recover an accidentally dropped TiDB business table from the exact DDL job within the GC lifetime.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `dropped_table_gc_recovery` | Recover the original order-event table from an exact DROP DDL job before GC removes its data. | `hard` |
| 1 | `dropped_payment_events_gc_recovery` | Recover the incident-boundary payment-events table from the exact DROP DDL job before GC cleanup. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `dropped_table_gc_recovery`

- Case number: `0`
- Title: Recover the original order-event table from an exact DROP DDL job before GC removes its data.
- Alert/symptom: [CRITICAL] [Order Platform] 查询 benchops.order_events 的订单检索、对账和发布审计接口同时出现 'table doesn't exist'；数据库节点仍然 Up，其他归档查询正常。最近一次 release cleanup 可能误删了 order_events，但同一逻辑表曾被发布流程重复创建和清理。请在 GC 可恢复窗口内恢复原始业务表，事故边界为 2026-08-03 11:30:00；请从 incident context 和 release transition history 重建该时刻 order-api/prod 实际 serving 的 release，而不是直接采用当前 desired release。保留当前在线查询负载，不要从应用导出重建数据；恢复前必须核对 DDL 历史、GC safe point 和恢复对象，恢复后必须证明业务真值、主键/索引一致性和 Ti
- Initial-state fields: `cluster`, `database`, `gc_window`, `status`, `table`
- Expected-target fields: `admin_check`, `crc`, `drop_job_id`, `gc_life_time`, `last_known_good_release`, `status`, `table_rows`
- Background profiles: order_api_recent_lookup, order_reconciliation_rollup, release_archive_preview, release_audit_window, ddl_history_refresh, gc_window_probe, missing_order_cache_refresh, release_control_plane_lookup, release_registry_snapshot, business_release_ledger_reconcile, release_ddl_lineage_refresh, release_audit_config_window
- Evaluator: `src.scenarios.evaluation.tidb.business_change.table_recovery.TidbBusinessChangeTableRecoveryEvaluatorCase`
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).
- Calibration evidence (tool m/n): not declared in code

### `dropped_payment_events_gc_recovery`

- Case number: `1`
- Title: Recover the incident-boundary payment-events table from the exact DROP DDL job before GC cleanup.
- Alert/symptom: [CRITICAL] [Payment Platform] 查询 benchops_bc07_payments.payment_events 的支付检索、对账和发布审计接口同时出现 'table doesn't exist'；数据库节点仍然 Up，其他归档查询正常。最近一次 payment release cleanup 可能误删了 payment_events，但同一逻辑表曾被发布流程重复创建和清理。请在 GC 可恢复窗口内恢复原始业务表，事故边界为 2026-08-10 16:30:00；请从 incident context 和 release transition history 重建该时刻 payments-api/prod 实际 serving 的 release，而不是直接采用当前 desired release。保留当前在线查询负载，不要从应用导出重建数据；恢复前必须核对 DDL 历史、GC safe point
- Initial-state fields: `cluster`, `database`, `gc_window`, `status`, `table`
- Expected-target fields: `admin_check`, `crc`, `drop_job_id`, `gc_life_time`, `last_known_good_release`, `status`, `table_rows`
- Background profiles: payment_api_recent_lookup, payment_reconciliation_rollup, release_archive_preview, release_audit_window, ddl_history_refresh, gc_window_probe, missing_payment_cache_refresh, release_control_plane_lookup, release_registry_snapshot, business_release_ledger_reconcile, release_ddl_lineage_refresh, release_audit_config_window
- Evaluator: `src.scenarios.evaluation.tidb.business_change.table_recovery.TidbBusinessChangeTableRecoveryForPaymentEventsEvaluatorCase`
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md).
- Calibration evidence (tool m/n): execute_sql=27/56; query_metrics=17/425; read_log=1/25; search_knowledge=5/0

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

- Scenario and Case source: `src.scenarios.tidb.business_change.table_recovery.TidbBusinessChangeTableRecoveryScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/business_change/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_business_change_table_recovery_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
