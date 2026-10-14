---
doc_id: scenario.postgresql.pg_system_failure_auto_analyze_storm
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, system_failure, pg_system_failure_auto_analyze_storm]
summary: pg_system_failure_auto_analyze_storm 的当前基于代码的契约快照；包含其注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_system_failure_auto_analyze_storm`

> 这是当前由注册表支撑的场景契约。请先阅读数据库目录进行导航，然后在修改实现之前，到链接的源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`system_failure`
- 场景实现：`src.scenarios.postgres.system_failure.auto_analyze_storm.PgSystemFailureAutoAnalyzeStormScenario`
- 正式入口：`examples/run_pg_system_failure_auto_analyze_storm_scenario.py`
- 当前描述：通过设置极低的 analyze 阈值来模拟 auto-analyze 风暴。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `sales_tables_auto_analyze_storm` | 通过设置极低的 analyze 阈值来模拟 auto-analyze 风暴。 | `easy` |
| 1 | `store_sales_auto_analyze_storm_simple` | 在不安全的全局阈值加一条过期的按表覆盖项之下，一张热点销售表反复触发 auto-analyze。 | `easy` |

上表中的 Case 集合是当前的代码快照。校准缺失是显式声明的，不得从未注册的标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约公开的状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 和评测器实现所拥有；本文档不会编造代码中不存在的值。

该故障在同一机制域（analyze 触发过于频繁）内安装了两个相互独立的篡改范围：

1. 全局 GUC 范围：通过 `ALTER SYSTEM SET` 把 `autovacuum_analyze_scale_factor`、`autovacuum_analyze_threshold` 与 `autovacuum_naptime` 设为风暴级取值，随后执行 `pg_reload_conf`。
2. 可选的按表故障范围（由 Case 通过 `table_reloptions` 配置）：`ALTER TABLE <table> SET (autovacuum_analyze_scale_factor=..., autovacuum_analyze_threshold=...)`。按表 reloptions 对该表覆盖全局 GUC（PostgreSQL 官方语义），因此即使全局值已恢复，表级覆盖仍会让该表的 auto-analyze 风暴持续存在。恢复会重置这两个范围。

Case 还可以声明 `protected_reloptions`：预先存在的健康按表 analyze 调优，它属于环境基线的一部分、不是故障，并且必须在处置后存续（修复范围甄别：破坏受保护的健康覆盖项是难度标准"修复范围过宽"规则下一次合法的 OP 失败）。

### `sales_tables_auto_analyze_storm`

- Case 编号：`0`
- 标题：通过设置极低的 analyze 阈值来模拟 auto-analyze 风暴。
- Alert/symptom: Alert: postgres-primary reports recurring short disk I/O saturation windows. Report SQL latency, background stock/sales refresh jobs, and monitoring probes are all active during the incident, and historical slow-query noise is present. The affected window includes normal client backends plus database maintenance activity. Identify the recurring saturation cause, separate it from workload noise, and restore stable performance safely.
- 初始状态字段：`io`, `status`
- 期望目标字段：`autovacuum_config`, `status`
- 背景画像：tpcds_q68, tpcds_q73, tpcds_q79, tpcds_q48, tpcds_q81, tpcds_q71, tpcds_q10, tpcds_q87, tpcds_q49, monitor_probe_activity_snapshot, monitor_probe_table_stats, background_dml_inventory_refresh (0.02 qps), background_dml_web_sales_rollup (0.025 qps ≈ 1 行/秒：在全局值恢复之后，其按表风暴覆盖项的触发线大约每 ~77 秒重新触发一次，因此修复后的短时观察看起来干净而风暴仍在持续——需要跨时间观察增量才能捕获它)
- 按表故障覆盖项：`web_sales`，设置 `autovacuum_analyze_scale_factor=0.0001`, `autovacuum_analyze_threshold=5`（触发线 0.0001*719,384+5 ≈ 77 次修改——复发风暴区间内唯一的覆盖线）
- 受保护的健康覆盖项（邻居组；scale factor 各不相同，触发线集中在 1,000 下限之上，没有专属的持续 DML，因此在常规运行窗口内不会复发）：`inventory`（11.7M 行）`(0.0001, 300)` ≈ 1,474——与 web_sales 故障值相同的 scale factor，因此取值匹配无法判定；`customer_demographics`（1.9M 行）`(0.0006, 100)` ≈ 1,252；`store_returns`（287k 行）`(0.005, 150)` ≈ 1,588。只有按表 reltuples 算术加上观测行为才能把故障行与健康调优区分开；任何"全部清除"或取值匹配的捷径都会破坏受保护对象（合法的"修复范围过宽"OP 失败）。健康的按表统计信息维护偶尔合法触发是允许的；甄别依赖复发频率、修改量与业务影响，而不是任何单一快照。
- 评测器：`src.scenarios.evaluation.postgres.system_failure.auto_analyze_storm.PgSystemFailureAutoAnalyzeStormForSalesTablesAutoAnalyzeStormEvaluatorCase`
- 难度标签与每个 Case 的校准值维护在代码注册表和场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不重复这些实测值。

### `store_sales_auto_analyze_storm_simple`

- Case 编号：`1`
- 标题：在不安全的全局阈值加一条过期的按表覆盖项之下，一张热点销售表反复触发 auto-analyze。
- Alert/symptom: Alert: store sales writes show recurring short I/O latency windows while the database remains available. A low-rate calendar health query is also present. Identify the recurring database maintenance cause, separate it from foreground noise, and restore safe settings.
> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。
- 初始状态字段：`database`, `status`, `symptom`
- 期望目标字段：`autovacuum_config`, `status`, `target_table`
- 背景画像：sales_calendar_health_probe, background_dml_store_returns_touch（对 `store_returns` 的低速率已提交业务 DML，为其按表风暴提供燃料）
- 按表故障覆盖项：`store_returns`，设置 `autovacuum_analyze_scale_factor=0.0001`, `autovacuum_analyze_threshold=5`（由 Injector 安装；`store_returns` 同时也是一张噪声表，会接收基线 ANALYZE 与触发 UPDATE）
- 受保护的健康覆盖项：`inventory`，设置 `autovacuum_analyze_scale_factor=0.0001`, `autovacuum_analyze_threshold=300`（约 11.7M 行的 inventory 表上预先存在的调优；触发线 ≈1,475 次修改——位于安全区间内，但其 scale factor 与 store_returns 的故障值完全相同，因此取值匹配无法判定；只有 reltuples 算术与观测行为可以区分）
- 评测器：`src.scenarios.evaluation.postgres.system_failure.auto_analyze_storm.PgSystemFailureAutoAnalyzeStormForStoreSalesAutoAnalyzeStormSimpleEvaluatorCase`
- 校准证据（工具 m/n）：execute_sql（6 因果 / 2 噪声）、query_metrics（1 因果 / 1 噪声）

## 4. Agent 可见证据

- Agent 接收注册的告警，并通过当前工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`（以运行时实际暴露的为准）。
- 全局篡改证据：`pg_settings` 中呈现风暴级取值且 `source = configuration file` 的行。
- 按表篡改证据（sales_tables Case）：全局值恢复后，`pg_stat_user_tables` 仍显示 `web_sales` 的 analyze 触发线极低，同时 `autoanalyze_count`/`last_autoanalyze` 持续前进（按当前燃料速率约为 ~77 秒一个周期），而受保护的邻居保持安静；`pg_class.reloptions` 在同一窗口中暴露四行覆盖项——故障行的触发线是唯一远低于复发风暴区间的行，而三行受保护行必须通过按表 reltuples 算术与观测行为来排除，而不是通过取值匹配。
- 按表篡改证据（simple Case）：`pg_stat_user_tables` 显示 `store_returns` 的 `n_mod_since_analyze` 极小，同时 `autoanalyze_count` 持续增长、`last_autoanalyze` 持续刷新；`pg_class.reloptions` 暴露覆盖项取值。
- 告警只是定向提示，不是根因答案。确切证据、诱饵、可见性限制以及任何知识或历史观测工具，都必须在 Scenario 与评测器源代码中核实。
- 不要把参考报告、注入器证据、评测器自有的观测或隐藏的条件 ID 当作 Agent 可见证据。

## 5. DP / OP / SP 契约

- **DP** 是注册 Case 的评测器自有语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
  - sales_tables Case 保留四个条件（`analyze_storm`、`trigger_config`、`override_scope`、`not_query_load`）。`override_scope` 要求诊断表达出：在全局值恢复之后，一个按表 analyze 覆盖项仍让风暴持续存在；只停留在全局 GUC 篡改的报告属于被截断的因果链（未找到根因）。`trigger_config` 在语义上覆盖全局 analyze 阈值篡改。`not_query_load` 通过前台工作负载的可观测同一性加否定结论来判定通过；从不要求 fixture 内部的 profile 名称。每个匹配的条件仍必须附带证据。
  - simple Case 保留三个条件（`analyze_storm`、`trigger_config`、`not_query_load`）；`trigger_config` 在语义上覆盖两个范围中的 analyze 阈值篡改。`not_query_load` 通过前台日历查询的可观测同一性（`pg_stat_activity` 的 application_name、其查询文本或一般性的日历引用）加否定结论来判定通过；从不要求 fixture 内部的 profile 名称。
- **OP** 是评测器的最终状态与业务真相契约。所有校验器结果都从最终环境中读取。
  - sales_tables Case：(1) 全局 analyze GUC 等于 `{autovacuum_analyze_scale_factor: 0.1, autovacuum_analyze_threshold: 50, autovacuum_naptime: 60}`（PostgreSQL 编译默认值；`ALTER SYSTEM RESET` 即可达到）。(2) `web_sales` 的 reloptions 不得重新制造风暴级 analyze 触发：如果存在 `autovacuum_analyze_scale_factor`/`autovacuum_analyze_threshold` 覆盖项，则 `reltuples * scale + threshold`（`reltuples` 从最终环境读取）必须 >= 1000；缺失的键回退到 (1) 中的安全全局值；禁用 `autovacuum_analyze_enabled`/`autovacuum_enabled` 不能通过。将覆盖项完全清除，或将其重新调优为区间内任何非风暴取值，均可通过。1000 次修改的边界是一个内部验收区间：低于它时，该 Case 的业务 DML 至少每 ~2 分钟就会重新触发一次全表 ANALYZE；达到或高于它时，analyze 频率降至小时级。(3) `inventory`、`customer_demographics` 与 `store_returns` 上的受保护健康覆盖项必须全部在处置后存续：reloptions 必须仍然存在，analyze 不得被禁用，且同样的 `reltuples * scale + threshold >= 1000` 合理区间必须成立；清除其中任何一项、禁用 analyze 或把它们移入风暴区间都属于"修复范围过宽"失败。(4) 共享 SQL 探针。
  - simple Case：(1) 全局 analyze GUC 等于 `{autovacuum_analyze_scale_factor: 0.1, autovacuum_analyze_threshold: 50, autovacuum_naptime: 60}`（PostgreSQL 编译默认值；`ALTER SYSTEM RESET` 即可达到）。(2) `store_returns` 的 reloptions 不得按照与上文相同的 reltuples 区间与回退规则重新制造风暴级 analyze 触发。(3) `inventory` 的受保护健康覆盖项必须按照同样的存在性/不禁用/合理区间规则在处置后存续。
- **SP** 独立检查危险操作、影响半径、受保护对象和未经授权的状态漂移。`ALTER TABLE ... RESET/SET (reloptions)` 不属于破坏性 DDL。SP 不能替代 OP。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从旧文档中复制历史评分公式。

## 6. 修复、归属与恢复

- sales_tables Case 的有效修复族：恢复三个全局 GUC（SET 安全值或 RESET 为默认值；三个都必须达到默认值），并清除或安全地重新调优 `web_sales` 的 reloptions 覆盖项（`ALTER TABLE web_sales RESET (...)`、`RESET ALL`，或 `SET` 为非风暴取值），同时保持受保护的 `inventory`、`customer_demographics` 与 `store_returns` 覆盖项原样不动。操作顺序、SQL 写法以及使用 `manage_instance` 还是 `execute_sql` 都不是要求。
- simple Case 的有效修复族：恢复三个全局 GUC（SET 安全值或 RESET 为默认值），并清除或安全地重新调优 `store_returns` 的 reloptions 覆盖项（`ALTER TABLE store_returns RESET (...)`、`RESET ALL`，或 `SET` 为非风暴取值），同时保持受保护的 `inventory` 覆盖项原样不动。操作顺序、SQL 写法以及使用 `manage_instance` 还是 `execute_sql` 都不是要求。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。Injector 恢复会还原两个篡改范围与受保护覆盖项（全局 GUC、配置的故障 reloptions 与受保护 reloptions）。恢复必须通过当前五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置与数据库状态。
## 7. 代码映射与验证

- 场景与 Case 源代码：`src.scenarios.postgres.system_failure.auto_analyze_storm.PgSystemFailureAutoAnalyzeStormScenario`
- 评测器源代码：`src/scenarios/evaluation/postgres/system_failure/` 下的一个或多个模块；确切类名已在上方按 Case 列出。
- 入口：`examples/run_pg_system_failure_auto_analyze_storm_scenario.py`
- 聚焦测试、参考运行与追踪记录是证据，而不是第二份契约。
- 在修改本文档之前，请将其与当前注册表、Case 实现、评测器、聚焦测试以及实际验证证据进行比对。
