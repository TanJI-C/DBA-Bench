---
doc_id: scenario.postgresql.pg_business_change_collation_conversion
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, business_change, pg_business_change_collation_conversion]
summary: Current code-backed contract snapshot for pg_business_change_collation_conversion; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_business_change_collation_conversion`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `business_change`
- Scenario implementation: `src.scenarios.postgres.business_change.collation_conversion.PgBusinessChangeCollationConversionScenario`
- Formal entrypoint: `examples/run_pg_business_change_collation_conversion_scenario.py`
- Current description: Simulates an online collation conversion on a TPC-DS fact table that invalidates LIKE-friendly B-tree access paths.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `store_returns_collation_conversion` | Simulates an online collation conversion on a TPC-DS fact table that invalidates LIKE-friendly B-tree access paths. | `hard` |
| 1 | `store_returns_ticket_locale_simple` | Simplified regional collation conversion with one adjacent ticket-search decoy. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `store_returns_collation_conversion`

- Case number: `0`
- Title: Simulates an online collation conversion on a TPC-DS fact table that invalidates LIKE-friendly B-tree access paths.
- Alert/symptom: 业务变更窗口提醒：退货报表发布要求主票号文本字段支持区域性排序，同时该字段仍承载线上 LIKE 前缀检索，变更存在计划回归风险。请先从当前业务负载中区分主票号、审计票号和历史预览字段，再评估表重写成本、锁等待窗口、空间膨胀和依赖索引影响；随后在低峰期完成必要的在线变更，恢复前缀检索计划并用元数据查询与 EXPLAIN 验证。避免无关临时演练；确认变更闭环后必须调用 submit 结束流程。
- Initial-state fields: `column`, `current_collation`, `risk`, `status`, `table`
- Expected-target fields: `column`, `like_index`, `plan`, `status`, `table`, `target_collation`
- Background profiles: returns_ticket_prefix_probe, returns_ticket_audit_prefix_probe, returns_ticket_legacy_sort_preview, returns_numeric_ticket_rollup, missing_returns_locale_cache_noise, returns_archive_prefix_probe
- Evaluator: `src.scenarios.evaluation.postgres.business_change.collation_conversion.PgBusinessChangeCollationConversionForStoreReturnsCollationConversionEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): `execute_sql.pg_views/pg_depend` (6, 7)
### `store_returns_ticket_locale_simple`

- Case number: `1`
- Title: Simplified regional collation conversion with one adjacent ticket-search decoy.
- Alert/symptom: 变更窗口告警：退货检索服务需要支持区域化文本排序，发布预检显示前缀查询计划可能回退。请确认真正承载线上检索的字段，评估转换与索引影响，安全完成变更并验证查询计划；审计预览流量仍在低频运行。
- Initial-state fields: `status`, `symptom`
- Expected-target fields: `collation`, `plan`, `status`
- Background profiles: returns_ticket_prefix_probe, returns_ticket_audit_prefix_probe
- Evaluator: `src.scenarios.evaluation.postgres.business_change.collation_conversion.PgBusinessChangeCollationConversionForStoreReturnsTicketLocaleSimpleEvaluatorCase`
- Calibration evidence (tool m/n): not declared in code

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

- Scenario and Case source: `src.scenarios.postgres.business_change.collation_conversion.PgBusinessChangeCollationConversionScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/business_change/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_business_change_collation_conversion_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
