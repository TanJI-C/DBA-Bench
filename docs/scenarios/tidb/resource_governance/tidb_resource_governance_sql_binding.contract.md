---
doc_id: scenario.tidb.tidb_resource_governance_sql_binding
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, resource_governance, tidb_resource_governance_sql_binding]
summary: Current code-backed contract snapshot for tidb_resource_governance_sql_binding; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `tidb_resource_governance_sql_binding`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `resource_governance`
- Scenario implementation: `src.scenarios.tidb.resource_governance.sql_binding.TidbResourceGovernanceSqlBindingScenario`
- Formal entrypoint: `examples/run_tidb_resource_governance_sql_binding_scenario.py`
- Current description: Approve one currently served customer read path with a session-local TiDB SQL binding in a noisy workload.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `deterministic_or_binding_approval` | Approve one currently served customer read path with a session-local plan policy. | `hard` |
| 1 | `channel_window_binding_approval` | Approve the batch-channel search window with a session-local plan policy. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `deterministic_or_binding_approval`

- Case number: `0`
- Title: Approve one currently served customer read path with a session-local plan policy.
- Alert/symptom: [RESOURCE GOVERNANCE] 一个 customer-facing read path 需要批准稳定的 session-local 执行计划。当前 workload 同时包含相邻业务读取、历史 plan policy、schema/统计探针和可失败的辅助探针；请从未过滤的 workload/TopSQL 与当前 plan policy 证据中识别准确的业务请求，在当前 session 选择已有的匹配访问路径，保护全局 policy、全局 TiDB 变量、schema 和业务数据。当前业务真值摘要必须保持为 782 行、event id sum=39092962、CRC=1892534002；提交时保留启用的 session binding，并验证最终计划由该 binding 控制、业务结果与表真值未变；harness 会在 teardown 清理 session binding。
- Initial-state fields: `approved_access_path`, `global_binding`, `session_binding`, `status`
- Expected-target fields: `cleanup`, `last_plan_from_binding`, `plan_contains`, `result_count`, `session_binding`, `status`
- Background profiles: wrk_03, wrk_04, wrk_05, wrk_06, wrk_07, wrk_08, wrk_09, wrk_10, wrk_11, wrk_12, wrk_29, wrk_30
- Evaluator: `src.scenarios.evaluation.tidb.resource_governance.sql_binding.TidbResourceGovernanceSqlBindingEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): execute_sql(statement summary)=1/41; global_bindings=1/18; show_index=2/6; business_result_summary=1/0; candidate_result_probe=1/18; explain=1/4

### `channel_window_binding_approval`

- Case number: `1`
- Title: Approve the batch-channel search window with a session-local plan policy.
- Alert/symptom: [RESOURCE GOVERNANCE] A customer-facing channel search window needs a session-local plan approval. The workload contains neighboring tenant/time and channel searches, historical plan policies, schema probes, and auxiliary checks. Identify the exact batch-channel request from live evidence, choose an existing matching access path in the current session, and preserve global policy, global TiDB variables, schema, and bu
- Initial-state fields: `approved_access_path`, `global_binding`, `session_binding`, `status`
- Expected-target fields: `cleanup`, `last_plan_from_binding`, `plan_contains`, `result_count`, `session_binding`, `status`
- Background profiles: wrk_03, wrk_04, wrk_05, wrk_06, wrk_07, wrk_08, wrk_09, wrk_10, wrk_11, wrk_12, wrk_29, wrk_30
- Evaluator: `src.scenarios.evaluation.tidb.resource_governance.sql_binding.TidbResourceGovernanceSqlBindingChannelWindowEvaluatorCase`
- Calibration evidence (tool m/n): execute_sql(statement summary)=1/31; global_bindings=1/15; show_index=2/6; business_result_summary=1/0; candidate_result_probe=0/14; explain=1/4

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

- Scenario and Case source: `src.scenarios.tidb.resource_governance.sql_binding.TidbResourceGovernanceSqlBindingScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/resource_governance/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_resource_governance_sql_binding_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
