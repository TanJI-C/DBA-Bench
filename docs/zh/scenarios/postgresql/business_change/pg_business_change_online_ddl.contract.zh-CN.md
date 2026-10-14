---
doc_id: scenario.postgresql.pg_business_change_online_ddl
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, business_change, pg_business_change_online_ddl]
summary: Current code-backed contract snapshot for pg_business_change_online_ddl; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_business_change_online_ddl`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `business_change`
- Scenario implementation: `src.scenarios.postgres.business_change.online_ddl.PgBusinessChangeOnlineDdlScenario`
- Formal entrypoint: `examples/run_pg_business_change_online_ddl_scenario.py`
- Current description: Online schema change on a large hot PostgreSQL order_line table.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `order_line_delivery_note_ddl` | Online schema change on a large hot PostgreSQL order_line table. | `easy` |
| 1 | `order_line_gift_note_ddl_simple` | Simplified online nullable-column release on a moderately large hot order table. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `order_line_delivery_note_ddl`

- Case number: `0`
- Title: Online schema change on a large hot PostgreSQL order_line table.
- Alert/symptom: 发布窗口告警：订单写入链路正在上线配送备注能力，应用映射字段为 ol_delivery_note。当前 order-entry 读写延迟 SLO 接近阈值，连接数、事务吞吐和发布预检任务同时升高。请确认应变更的在线业务对象，在不中断下单流量的前提下完成结构变更，并复查变更已生效。
- Initial-state fields: `status`, `table`, `target_column`, `workload`
- Expected-target fields: `required_strategy`, `status`, `table`, `target_column`
- Background profiles: order_entry_latency_probe, delivery_note_audit_rollup, release_queue_backfill_probe, order_line_sample_count_decoy, release_precheck_lock_probe, missing_delivery_note_cache_log_noise
- Evaluator: `src.scenarios.evaluation.postgres.business_change.online_ddl.PgBusinessChangeOnlineDdlForOrderLineDeliveryNoteDdlEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `order_line_gift_note_ddl_simple`

- Case number: `1`
- Title: Simplified online nullable-column release on a moderately large hot order table.
- Alert/symptom: 发布窗口告警：订单链路正在上线礼赠备注能力，当前写入仍在持续，发布预检观察到短暂锁竞争。请确认实际在线对象和缺失结构，使用快速失败并可重试的方式完成变更，随后核验业务结构。
- Initial-state fields: `status`, `target_column`, `workload`
- Expected-target fields: `required_strategy`, `status`
- Background profiles: order_entry_latency_probe, delivery_note_audit_rollup
- Evaluator: `src.scenarios.evaluation.postgres.business_change.online_ddl.PgBusinessChangeOnlineDdlForOrderLineGiftNoteSimpleEvaluatorCase`
- Calibration evidence (tool m/n): not declared in code

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
- **OP** is the evaluator's final-state and business-truth contract. The expected-target fields above identify the state boundary; accepted repairs and equivalent outcomes are defined by the evaluator. For the delivered column, OP accepts the finite character-type domain published by `information_schema.columns` (`text`, `character varying`, `character`) instead of one fixed type literal.
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.business_change.online_ddl.PgBusinessChangeOnlineDdlScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/business_change/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_business_change_online_ddl_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
