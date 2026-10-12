---
doc_id: scenario.postgresql.pg_query_perf_suboptimal_join
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, query_perf, pg_query_perf_suboptimal_join]
summary: Current code-backed contract snapshot for pg_query_perf_suboptimal_join; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_query_perf_suboptimal_join`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `query_perf`
- Scenario implementation: `src.scenarios.postgres.query_perf.suboptimal_join.PgQueryPerfSuboptimalJoinScenario`
- Formal entrypoint: `examples/run_pg_query_perf_suboptimal_join_scenario.py`
- Current description: Simulates suboptimal join method regression from role-level planner setting drift.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `sales_report_role_planner_drift` | Simulates suboptimal join method regression from role-level planner setting drift. | `hard` |
| 1 | `daily_account_summary_planner_drift` | Simulates a smaller daily account summary slowed by role-level join planner drift. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `sales_report_role_planner_drift`

- Case number: `0`
- Title: Simulates suboptimal join method regression from role-level planner setting drift.
- Alert/symptom: Alert: the branch account margin report has slowed from ~2s to over 30s since this morning. CPU and read I/O rise during the report, while row counts, application SQL, and visible indexes have not changed. Identify the database-side cause and provide a verifiable fix. Affected query: /* crm_reporting: branch_account_margin_v3_with_decile */ WITH order_lines AS MATERIALIZED ( SELECT ol.bol_account_sk, ol.bol_branch_sk, ol.bol_sold_date_sk, ol.bol_product_sk, ol.bol_net_paid, ol.bol_net_profit FROM branch_order_line ol WHERE ol.bol_sold_date_sk BETWEEN 2451911 AND 2451925 ), account_segments AS MATERIALIZED ( SELECT acct.sa_account_sk, acct.sa_current_addr_sk, acct.sa_preferred_flag, acct.sa_birth_country FROM shopper_account acct WHERE acct.sa_account_sk BETWEEN 1 AND 15000 ), qualified_orders AS MATERIALIZED ( SELECT seg.sa_account_sk, seg.sa_preferred_flag, seg.sa_birth_country, ord.bol_branch_sk, ord.bol_sold_date_sk, ord.bol_product_sk, prod.pr_category, prod.pr_brand, ord.bol_net_paid, ord.bol_net_profit FROM account_segments seg JOIN account_address addr ON addr.aa_address_sk = seg.sa_current_addr_sk JOIN branch br ON br.br_state = addr.aa_state JOIN order_lines ord ON ord.bol_account_sk = seg.sa_account_sk AND ord.bol_branch_sk = br.br_branch_sk JOIN product prod ON prod.pr_product_sk = ord.bol_product_sk JOIN calendar_day cal ON cal.cal_day_sk = ord.bol_sold_date_sk AND cal.cal_year = 2001 ), account_profit AS MATERIALIZED ( SELECT qo.sa_account_sk, qo.sa_preferred_flag, qo.sa_birth_country, qo.pr_category, qo.pr_brand, SUM(qo.bol_net_paid) AS total_revenue, SUM(qo.bol_net_profit) AS total_profit, COUNT(*) AS line_count, NTILE(100) OVER (ORDER BY SUM(qo.bol_net_profit) DESC) AS profit_decile, ROW_NUMBER() OVER ( PARTITION BY qo.pr_category ORDER BY SUM(qo.bol_net_profit) DESC, qo.sa_account_sk ) AS category_rank FROM qualified_orders qo GROUP BY qo.sa_account_sk, qo.sa_preferred_flag, qo.sa_birth_country, qo.pr_category, qo.pr_brand ) SELECT ap.sa_account_sk, ap.sa_preferred_flag, ap.sa_birth_country, ap.pr_category, ap.pr_brand, ap.total_revenue, ap.total_profit, ap.line_count, ap.profit_decile, ap.category_rank, ( SELECT MAX(dol.dol_net_paid) FROM digital_order_line dol WHERE dol.dol_bill_account_sk = ap.sa_account_sk ) AS max_digital_order, ( SELECT COUNT(DISTINCT aol.aol_order_number) FROM assisted_order_line aol WHERE aol.aol_bill_account_sk = ap.sa_account_sk ) AS assisted_order_count FROM account_profit ap WHERE ap.profit_decile <= 10 AND ap.category_rank <= 50 ORDER BY ap.total_profit DESC, ap.sa_account_sk LIMIT 50 Hint: compare the current execution plan with the expected shape for this multi-stage report.
- Initial-state fields: `app_role`, `join_method`, `role_enable_hashjoin`, `role_enable_mergejoin`, `status`
- Expected-target fields: `app_role`, `join_method`, `role_planner_settings`, `status`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.query_perf.suboptimal_join.PgQueryPerfSuboptimalJoinForSalesReportRolePlannerDriftEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `daily_account_summary_planner_drift`

- Case number: `1`
- Title: Simulates a smaller daily account summary slowed by role-level join planner drift.
- Alert/symptom: Alert: the branch account margin report has slowed from ~2s to over 30s since this morning. CPU and read I/O rise during the report, while row counts, application SQL, and visible indexes have not changed. Identify the database-side cause and provide a verifiable fix. Affected query: /* crm_reporting: branch_account_margin_v3_with_decile */ WITH order_lines AS MATERIALIZED ( SELECT ol.bol_account_sk, ol.bol_branch_sk, ol.bol_sold_date_sk, ol.bol_product_sk, ol.bol_net_paid, ol.bol_net_profit FROM branch_order_line ol WHERE ol.bol_sold_date_sk BETWEEN 2451911 AND 2451925 ), account_segments AS MATERIALIZED ( SELECT acct.sa_account_sk, acct.sa_current_addr_sk, acct.sa_preferred_flag, acct.sa_birth_country FROM shopper_account acct WHERE acct.sa_account_sk BETWEEN 1 AND 15000 ), qualified_orders AS MATERIALIZED ( SELECT seg.sa_account_sk, seg.sa_preferred_flag, seg.sa_birth_country, ord.bol_branch_sk, ord.bol_sold_date_sk, ord.bol_product_sk, prod.pr_category, prod.pr_brand, ord.bol_net_paid, ord.bol_net_profit FROM account_segments seg JOIN account_address addr ON addr.aa_address_sk = seg.sa_current_addr_sk JOIN branch br ON br.br_state = addr.aa_state JOIN order_lines ord ON ord.bol_account_sk = seg.sa_account_sk AND ord.bol_branch_sk = br.br_branch_sk JOIN product prod ON prod.pr_product_sk = ord.bol_product_sk JOIN calendar_day cal ON cal.cal_day_sk = ord.bol_sold_date_sk AND cal.cal_year = 2001 ), account_profit AS MATERIALIZED ( SELECT qo.sa_account_sk, qo.sa_preferred_flag, qo.sa_birth_country, qo.pr_category, qo.pr_brand, SUM(qo.bol_net_paid) AS total_revenue, SUM(qo.bol_net_profit) AS total_profit, COUNT(*) AS line_count, NTILE(100) OVER (ORDER BY SUM(qo.bol_net_profit) DESC) AS profit_decile, ROW_NUMBER() OVER ( PARTITION BY qo.pr_category ORDER BY SUM(qo.bol_net_profit) DESC, qo.sa_account_sk ) AS category_rank FROM qualified_orders qo GROUP BY qo.sa_account_sk, qo.sa_preferred_flag, qo.sa_birth_country, qo.pr_category, qo.pr_brand ) SELECT ap.sa_account_sk, ap.sa_preferred_flag, ap.sa_birth_country, ap.pr_category, ap.pr_brand, ap.total_revenue, ap.total_profit, ap.line_count, ap.profit_decile, ap.category_rank, ( SELECT MAX(dol.dol_net_paid) FROM digital_order_line dol WHERE dol.dol_bill_account_sk = ap.sa_account_sk ) AS max_digital_order, ( SELECT COUNT(DISTINCT aol.aol_order_number) FROM assisted_order_line aol WHERE aol.aol_bill_account_sk = ap.sa_account_sk ) AS assisted_order_count FROM account_profit ap WHERE ap.profit_decile <= 10 AND ap.category_rank <= 50 ORDER BY ap.total_profit DESC, ap.sa_account_sk LIMIT 50 Hint: compare the current execution plan with the expected shape for this multi-stage report.
- Initial-state fields: `app_role`, `join_method`, `role_enable_hashjoin`, `role_enable_mergejoin`, `status`
- Expected-target fields: `app_role`, `join_method`, `role_planner_settings`, `status`
- Background profiles: none declared
- Evaluator: `src.scenarios.evaluation.postgres.query_perf.suboptimal_join.PgQueryPerfSuboptimalJoinForDailyAccountSummaryEvaluatorCase`
- Difficulty: easy; D=2, C=0.6, reference=pg_query_perf_suboptimal_simple_flash__pg_query_perf_suboptimal_join__daily_account_summary_planner_drift__mock__r001
- Calibration evidence (tool m/n): not declared in code

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

- Scenario and Case source: `src.scenarios.postgres.query_perf.suboptimal_join.PgQueryPerfSuboptimalJoinScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/query_perf/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_query_perf_suboptimal_join_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
