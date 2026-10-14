---
doc_id: scenario.postgresql.pg_query_perf_suboptimal_join
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, query_perf, pg_query_perf_suboptimal_join]
summary: pg_query_perf_suboptimal_join 的当前基于代码的契约快照；包含其注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_query_perf_suboptimal_join`

> 这是当前基于注册中心的场景（Scenario）契约。请先阅读数据库目录进行导航，然后在修改实现之前，于关联源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`query_perf`
- 场景实现：`src.scenarios.postgres.query_perf.suboptimal_join.PgQueryPerfSuboptimalJoinScenario`
- 正式入口：`examples/run_pg_query_perf_suboptimal_join_scenario.py`
- 当前描述：模拟角色级规划器设置漂移导致的次优连接方法退化。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `sales_report_role_planner_drift` | 模拟角色级规划器设置漂移导致的次优连接方法退化。 | `hard` |
| 1 | `daily_account_summary_planner_drift` | 模拟更小的每日账户汇总因角色级连接规划器漂移而变慢。 | `hard` |

上方的 Case 集合是当前的代码快照。缺失校准是显式状态，不得从非注册标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现持有；本文档不杜撰代码中不存在的值。

### `sales_report_role_planner_drift`

- Case 编号：`0`
- 标题：模拟角色级规划器设置漂移导致的次优连接方法退化。
- Alert/symptom: Alert: the branch account margin report has slowed from ~2s to over 30s since this morning. CPU and read I/O rise during the report, while row counts, application SQL, and visible indexes have not changed. Identify the database-side cause and provide a verifiable fix. Affected query: /* crm_reporting: branch_account_margin_v3_with_decile */ WITH order_lines AS MATERIALIZED ( SELECT ol.bol_account_sk, ol.bol_branch_sk, ol.bol_sold_date_sk, ol.bol_product_sk, ol.bol_net_paid, ol.bol_net_profit FROM branch_order_line ol WHERE ol.bol_sold_date_sk BETWEEN 2451911 AND 2451925 ), account_segments AS MATERIALIZED ( SELECT acct.sa_account_sk, acct.sa_current_addr_sk, acct.sa_preferred_flag, acct.sa_birth_country FROM shopper_account acct WHERE acct.sa_account_sk BETWEEN 1 AND 15000 ), qualified_orders AS MATERIALIZED ( SELECT seg.sa_account_sk, seg.sa_preferred_flag, seg.sa_birth_country, ord.bol_branch_sk, ord.bol_sold_date_sk, ord.bol_product_sk, prod.pr_category, prod.pr_brand, ord.bol_net_paid, ord.bol_net_profit FROM account_segments seg JOIN account_address addr ON addr.aa_address_sk = seg.sa_current_addr_sk JOIN branch br ON br.br_state = addr.aa_state JOIN order_lines ord ON ord.bol_account_sk = seg.sa_account_sk AND ord.bol_branch_sk = br.br_branch_sk JOIN product prod ON prod.pr_product_sk = ord.bol_product_sk JOIN calendar_day cal ON cal.cal_day_sk = ord.bol_sold_date_sk AND cal.cal_year = 2001 ), account_profit AS MATERIALIZED ( SELECT qo.sa_account_sk, qo.sa_preferred_flag, qo.sa_birth_country, qo.pr_category, qo.pr_brand, SUM(qo.bol_net_paid) AS total_revenue, SUM(qo.bol_net_profit) AS total_profit, COUNT(*) AS line_count, NTILE(100) OVER (ORDER BY SUM(qo.bol_net_profit) DESC) AS profit_decile, ROW_NUMBER() OVER ( PARTITION BY qo.pr_category ORDER BY SUM(qo.bol_net_profit) DESC, qo.sa_account_sk ) AS category_rank FROM qualified_orders qo GROUP BY qo.sa_account_sk, qo.sa_preferred_flag, qo.sa_birth_country, qo.pr_category, qo.pr_brand ) SELECT ap.sa_account_sk, ap.sa_preferred_flag, ap.sa_birth_country, ap.pr_category, ap.pr_brand, ap.total_revenue, ap.total_profit, ap.line_count, ap.profit_decile, ap.category_rank, ( SELECT MAX(dol.dol_net_paid) FROM digital_order_line dol WHERE dol.dol_bill_account_sk = ap.sa_account_sk ) AS max_digital_order, ( SELECT COUNT(DISTINCT aol.aol_order_number) FROM assisted_order_line aol WHERE aol.aol_bill_account_sk = ap.sa_account_sk ) AS assisted_order_count FROM account_profit ap WHERE ap.profit_decile <= 10 AND ap.category_rank <= 50 ORDER BY ap.total_profit DESC, ap.sa_account_sk LIMIT 50 Hint: compare the current execution plan with the expected shape for this multi-stage report.
- 初始状态字段：`app_role`, `join_method`, `role_enable_hashjoin`, `role_enable_mergejoin`, `status`
- 期望目标字段：`app_role`, `join_method`, `role_planner_settings`, `status`
- 背景工作负载配置：未声明
- 评测器：`src.scenarios.evaluation.postgres.query_perf.suboptimal_join.PgQueryPerfSuboptimalJoinForSalesReportRolePlannerDriftEvaluatorCase`
- 难度标签与各 Case 的校准值维护在代码注册中心与场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复述这些实测值。

### `daily_account_summary_planner_drift`

- Case 编号：`1`
- 标题：模拟更小的每日账户汇总因角色级连接规划器漂移而变慢。
- Alert/symptom: Alert: the branch account margin report has slowed from ~2s to over 30s since this morning. CPU and read I/O rise during the report, while row counts, application SQL, and visible indexes have not changed. Identify the database-side cause and provide a verifiable fix. Affected query: /* crm_reporting: branch_account_margin_v3_with_decile */ WITH order_lines AS MATERIALIZED ( SELECT ol.bol_account_sk, ol.bol_branch_sk, ol.bol_sold_date_sk, ol.bol_product_sk, ol.bol_net_paid, ol.bol_net_profit FROM branch_order_line ol WHERE ol.bol_sold_date_sk BETWEEN 2451911 AND 2451925 ), account_segments AS MATERIALIZED ( SELECT acct.sa_account_sk, acct.sa_current_addr_sk, acct.sa_preferred_flag, acct.sa_birth_country FROM shopper_account acct WHERE acct.sa_account_sk BETWEEN 1 AND 15000 ), qualified_orders AS MATERIALIZED ( SELECT seg.sa_account_sk, seg.sa_preferred_flag, seg.sa_birth_country, ord.bol_branch_sk, ord.bol_sold_date_sk, ord.bol_product_sk, prod.pr_category, prod.pr_brand, ord.bol_net_paid, ord.bol_net_profit FROM account_segments seg JOIN account_address addr ON addr.aa_address_sk = seg.sa_current_addr_sk JOIN branch br ON br.br_state = addr.aa_state JOIN order_lines ord ON ord.bol_account_sk = seg.sa_account_sk AND ord.bol_branch_sk = br.br_branch_sk JOIN product prod ON prod.pr_product_sk = ord.bol_product_sk JOIN calendar_day cal ON cal.cal_day_sk = ord.bol_sold_date_sk AND cal.cal_year = 2001 ), account_profit AS MATERIALIZED ( SELECT qo.sa_account_sk, qo.sa_preferred_flag, qo.sa_birth_country, qo.pr_category, qo.pr_brand, SUM(qo.bol_net_paid) AS total_revenue, SUM(qo.bol_net_profit) AS total_profit, COUNT(*) AS line_count, NTILE(100) OVER (ORDER BY SUM(qo.bol_net_profit) DESC) AS profit_decile, ROW_NUMBER() OVER ( PARTITION BY qo.pr_category ORDER BY SUM(qo.bol_net_profit) DESC, qo.sa_account_sk ) AS category_rank FROM qualified_orders qo GROUP BY qo.sa_account_sk, qo.sa_preferred_flag, qo.sa_birth_country, qo.pr_category, qo.pr_brand ) SELECT ap.sa_account_sk, ap.sa_preferred_flag, ap.sa_birth_country, ap.pr_category, ap.pr_brand, ap.total_revenue, ap.total_profit, ap.line_count, ap.profit_decile, ap.category_rank, ( SELECT MAX(dol.dol_net_paid) FROM digital_order_line dol WHERE dol.dol_bill_account_sk = ap.sa_account_sk ) AS max_digital_order, ( SELECT COUNT(DISTINCT aol.aol_order_number) FROM assisted_order_line aol WHERE aol.aol_bill_account_sk = ap.sa_account_sk ) AS assisted_order_count FROM account_profit ap WHERE ap.profit_decile <= 10 AND ap.category_rank <= 50 ORDER BY ap.total_profit DESC, ap.sa_account_sk LIMIT 50 Hint: compare the current execution plan with the expected shape for this multi-stage report.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`app_role`, `join_method`, `role_enable_hashjoin`, `role_enable_mergejoin`, `status`
- 期望目标字段：`app_role`, `join_method`, `role_planner_settings`, `status`
- 背景工作负载配置：未声明
- 评测器：`src.scenarios.evaluation.postgres.query_perf.suboptimal_join.PgQueryPerfSuboptimalJoinForDailyAccountSummaryEvaluatorCase`
- 难度：easy；D=2，C=0.6，参考运行=pg_query_perf_suboptimal_simple_flash__pg_query_perf_suboptimal_join__daily_account_summary_planner_drift__mock__r001
- 校准证据（工具 m/n）：代码中未声明

## 4. Agent 可见证据

- Agent 接收已注册的告警，并通过当前工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`（以运行时实际暴露的为准）。
- 告警只是定位提示，而不是根因答案。确切的证据、干扰项、可见性限制以及任何知识或历史观测工具，都必须在 Scenario 与评测器源代码中核实。
- 不得把参考报告、注入器证据、评测器私有的观测或隐藏的条件 ID 当作 Agent 可见证据。

## 5. DP / OP / SP 契约

- **DP** 是针对已注册 Case 的、由评测器持有的语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
- **OP** 是评测器的最终状态与业务真值契约。上方的期望目标字段标识状态边界；可接受的修复与等价结果由评测器定义。
- **SP** 独立检查危险操作、影响范围（blast radius）、受保护对象以及未经授权的状态漂移。它不能替代 OP。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从历史遗留文档复制评分公式。

## 6. 修复、归属与恢复

- 使用当前评测器与 Scenario 契约接受的修复族。操作顺序、SQL 写法、索引名称与报告措辞均非硬性要求，除非代码明确将其纳入公开契约。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置与数据库状态。

## 7. 代码地图与验证

- Scenario 与 Case 源代码：`src.scenarios.postgres.query_perf.suboptimal_join.PgQueryPerfSuboptimalJoinScenario`
- 评测器源代码：`src/scenarios/evaluation/postgres/query_perf/` 下的一个或多个模块；确切的类已在上方按 Case 列出。
- 入口：`examples/run_pg_query_perf_suboptimal_join_scenario.py`
- 聚焦测试、参考运行与调用轨迹只是证据，并非第二份契约。
- 在修改本文档之前，请将其与当前注册中心、Case 实现、评测器、聚焦测试以及实时验证证据进行比对。
