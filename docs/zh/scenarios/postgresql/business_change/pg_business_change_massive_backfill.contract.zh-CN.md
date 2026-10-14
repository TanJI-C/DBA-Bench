---
doc_id: scenario.postgresql.pg_business_change_massive_backfill
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, business_change, pg_business_change_massive_backfill]
summary: Current code-backed contract snapshot for pg_business_change_massive_backfill; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_business_change_massive_backfill`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `business_change`
- Scenario implementation: `src.scenarios.postgres.business_change.massive_backfill.PgBusinessChangeMassiveBackfillScenario`
- Formal entrypoint: `examples/run_pg_business_change_massive_backfill_scenario.py`
- Current description: Simulates a massive historical data backfill that must be chunked and throttled.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `customer_birth_decade_backfill` | Simulates a massive historical data backfill that must be chunked and throttled. | `easy` |
| 1 | `customer_loyalty_decade_backfill_simple` | Simplified staged loyalty-decade backfill under a low-rate writer. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `customer_birth_decade_backfill`

- Case number: `0`
- Title: Simulates a massive historical data backfill that must be chunked and throttled.
- Alert/symptom: 变更发布告警：业务要求重新计算 customer_backfill 历史一年数据中的订正字段 c_birth_decade_corrected。当前 customer_backfill 仍有高并发读写，监控显示写入吞吐和 I/O 对批量变更非常敏感。请先评估变更风险，并在执行过程中持续确认业务负载保持稳定。
- Initial-state fields: `backfill`, `risk`, `status`
- Expected-target fields: `backfill`, `status`, `strategy`
- Background profiles: customer_backfill_stage_pending_probe, customer_backfill_preview_pending_decoy, customer_backfill_audit_delta_rollup, customer_backfill_hot_writer_preview, missing_backfill_control_cache_noise
- Evaluator: `src.scenarios.evaluation.postgres.business_change.massive_backfill.PgBusinessChangeMassiveBackfillForCustomerBirthDecadeBackfillEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `customer_loyalty_decade_backfill_simple`

- Case number: `1`
- Title: Simplified staged loyalty-decade backfill under a low-rate writer.
- Alert/symptom: 发布告警：客户忠诚度历史分段需要按本次已审核发布清单完成订正。本次发布以 2025-01-06 00:00:00+00 冻结的清单快照为准，冻结后追加的清单行随下一发布窗口执行、本次不得修改。冻结后发布台仍会对个别在册行登记范围裁定（作废或回退），最新裁定以发布操作事件记录为准，请按最新裁定确定本次订正范围。线上客户资料仍有低频写入，未来批次预览与历史批次残留同时可见；资料表上的批次标签存在漂移，请以发布清单确定订正范围。请采用可控批次完成变更，并验证冻结切片外的记录保持原状。
- Initial-state fields: `backfill`, `status`, `symptom`
- Expected-target fields: `backfill`, `status`, `strategy`
- Mechanism (case-owned initial state): the release staging table holds the approved batch `loyalty_decade_2025q1` (12000 rows, loaded in two passes: initial 2025-01-02 with 11572 rows and delta 2025-01-08 with 428 rows for `pk%40=0`) plus a leftover experimental draft batch `loyalty_decade_2024q4` (about 798 rows with source_name `crm_decade_estimator_experimental_v2`, loaded 2024-12-18; its pk set overlaps the approved batch on 522 rows (474 with conflicting staged values) and is otherwise contained in the future-tagged rows). `customer_loyalty_audit_shadow` samples the approved initial pass (`pk%17=0`, 680 rows, checked 2025-01-05, no coverage of the delta pass) and the draft batch (`pk%13=0`, checked 2024-12-19). The staging primary key is `(c_customer_sk, release_batch_id)` for this Case. A frozen-slice cutoff (`release_freeze_cutoff` = 2025-01-06 00:00:00+00, stated in the alert) excludes the delta pass from this change window; 81 frozen listed rows carry a drifted `future_birth_decade_2025q1` profile tag while remaining in the approved list; and 155 frozen listed rows already hold wrong values from an interrupted pass that used the unapproved estimator, so completion means every frozen listed row matches the staged value (not merely NULL-filling). The approved frozen slice alone defines the release scope; the profile tag is unreliable; the audit table is a post-hoc sample, not an approval set. After the freeze the release desk additionally recorded scope rulings in the agent-visible operation event table `customer_loyalty_operation_event` (public CHECK enum `row_annulled`/`row_restored`/`window_noted`): 66 frozen listed rows (`pk%173=17`, excluding value-drift and restored rows) were annulled on 2025-01-07 and roll to the next release window (they must stay uncorrected in this window), 11 frozen listed rows (`pk%997=42`) were annulled on 2025-01-07 and restored on 2025-01-09 (they stay in scope and must be corrected), 5 delta rows were annulled after already rolling out of the window, 61 draft-batch rows record the 2024-12-20 withdrawal of the experimental batch, and 2 window-level notes document the freeze and the delta staging. The effective scope is the frozen slice minus rows whose latest ruling is an annulment (annulled with no later restore for the approved batch); the alert states that the latest ruling governs.
- Background profiles: customer_backfill_stage_pending_probe, customer_backfill_preview_pending_decoy
- Evaluator: `src.scenarios.evaluation.postgres.business_change.massive_backfill.PgBusinessChangeMassiveBackfillForCustomerLoyaltyDecadeSimpleEvaluatorCase`
- Calibration is measured per Case against the live reference workload; the tool-hit ledger and rho values are maintained by the Case registry and the [difficulty standard](../../../../standards/scenario/difficulty.standard.md), not restated in this contract. OP verifies release_list_present, backfill_complete over the frozen slice excluding final-void rows, post_freeze_rows_untouched, void_rows_untouched, and out_of_scope_rows_unchanged.

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
- **OP** is the evaluator's final-state and business-truth contract. The expected-target fields above identify the state boundary; accepted repairs and equivalent outcomes are defined by the evaluator. Both Cases verify `release_list_present` (the approved release batch must keep a non-empty staging slice), `backfill_complete` (every approved-batch row carries the staged value), and `out_of_scope_rows_unchanged` (no out-of-list row receives a corrected value). For `customer_loyalty_decade_backfill_simple` the completeness slice is the frozen list snapshot (`loaded_at` at or before the stated cutoff) and additionally excludes rows whose latest operation-event ruling is an annulment for the approved batch; `post_freeze_rows_untouched` keeps post-cutoff listed rows uncorrected and `void_rows_untouched` keeps final-void frozen rows uncorrected (they roll to the next release window).
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.business_change.massive_backfill.PgBusinessChangeMassiveBackfillScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/business_change/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_business_change_massive_backfill_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
