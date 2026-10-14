---
doc_id: scenario.postgresql.pg_query_perf_stale_statistics
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, query_perf, pg_query_perf_stale_statistics]
summary: pg_query_perf_stale_statistics 的当前基于代码的契约快照；包含其注册的 Case、状态边界、评测器标识与校准状态。热窗口 simple Case 携带一个复合根因故障：关键列的统计信息目标被降级为 2，因此单纯的 ANALYZE/autovacuum 恢复已无法修复计划。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_query_perf_stale_statistics`

> 这是当前基于注册中心的场景（Scenario）契约。请先阅读数据库目录进行导航，然后在修改实现之前，于关联源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`query_perf`
- 场景实现：`src.scenarios.postgres.query_perf.stale_statistics.PgQueryPerfStaleStatisticsScenario`
- 正式入口：`examples/run_pg_query_perf_stale_statistics_scenario.py`
- 当前描述：模拟目标表上的过期统计信息，造成基数估计误差。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `branch_order_distribution_shift` | 模拟目标表上的过期统计信息，造成基数估计误差。 | `hard` |
| 1 | `branch_order_hot_window_simple` | 简化的热窗口报表，分支订单统计信息过期。 | `hard` |

上方的 Case 集合是当前的代码快照。缺失校准是显式状态，不得从非注册标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现持有；本文档不杜撰代码中不存在的值。

### `branch_order_distribution_shift`

- Case 编号：`0`
- 标题：模拟目标表上的过期统计信息，造成基数估计误差。
- Alert/symptom: Alert: the January hot-channel revenue reforecast report breached its latency SLO this morning — the same report that finished within its usual runtime yesterday now runs far past the reporting threshold. Finance needs the regression resolved urgently without changing the report SQL or its session execution environment.
- 初始状态字段：`statistics`, `status`
- 期望目标字段：`statistics`, `status`
- 背景工作负载配置：未声明
- 评测器：`src.scenarios.evaluation.postgres.query_perf.stale_statistics.PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase`
- 难度标签与各 Case 的校准值维护在代码注册中心与场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复述这些实测值。
- 本 Case 禁用 `calendar_drift`；注入器不施加日历维护漂移。
- 告警与事故构成：题面被改写为业务症状加修复边界约束；不再包含诊断建议、连接顺序观察或延迟数字。注入器在 `assisted_order_line` 与 `digital_order_line` 中各安装 120,000 行同窗口干扰行（每 Case 的 `decoy_rows`；simple Case 保留 8,000），因此不加过滤的统计信息巡检会显示三张同量级的过期事实表，修复目标必须从受影响的 SQL 映射得出。在 `install` 与 `activate` 结束时，注入器会重建 `pg_stat_statements` 事故基线（与连接膨胀注入器相同的模式），因此合成安装语句（批量 `INSERT`、显式 `ANALYZE`、计划快照）不会通过原始 `pg_stat_statements` 被 Agent 看到；过期机制仍然可以通过 `pg_stat_user_tables`、`pg_class`、`pg_stats`、表分布查询与执行计划观测。DP/OP/SP 与修复空间不变。
- 报表身份与可见性：复杂 Case 的题面不再附带受影响的报表 SQL——题面只点名报表（“January hot-channel revenue reforecast report”）并只陈述修复边界；报表 SQL 移入每 Case 的 `business_report_sql` 字段，不再是题面的一部分。在 `pg_stat_statements` 基线重建之后，注入器在事故开始时执行三条业务身份报表轨迹（`target_report`：带标签的完整报表 SQL；`assisted_report`：作用于 `assisted_order_line` 的 `/* finance_dashboard: assisted_channel_rebate_summary_v5 */`；`digital_report`：作用于 `digital_order_line` 的 `/* finance_dashboard: digital_channel_monthly_close_v3 */`），这些语句在隐藏块之外执行，因此仍然可以通过原始 `pg_stat_statements` 与 `slow_queries` 指标看到，是事故窗口内仅有的工作负载轨迹（在本场景中 `query_metrics(topsql)` 返回 Unknown metric_type 错误）。原先仅用于规划的种子 `EXPLAIN /* reporting_store_sales_join */` 已被移除；它被真实的目标报表轨迹完全取代。Agent 必须先把报表名映射到受影响的 SQL 与表（报表标签匹配唯一），再进入计划/统计信息证据链；修复干扰表会让 `branch_order_line` 保持过期并导致 OP 失败。DP/OP/SP 与修复空间不变。
- 维护窗口干扰项：在分布偏移行落库之后，注入器执行一次维护窗口限定的统计信息刷新 `ANALYZE branch_order_line (bol_account_sk, bol_net_paid)`——一次在隐藏块内（产生状态效果），一次在 `pg_stat_statements` 基线重建之后再次执行，作为 Agent 可见的维护记录。在 PostgreSQL 16 上，这会更新 `last_analyze`、`reltuples` 与 `n_live_tup`（行数差距闭合），但既不重置 `n_mod_since_analyze`，也不触及故障关键的 `bol_product_sk`/`bol_quantity`/`bol_sold_date_sk` 统计信息，因此表级计数器读起来“最近维护过”，而计划误差（实测 fault_max_plan_error_ratio 1251）与过期的关键列直方图依旧存在。可见语句历史中还会多出一条 3,000 行的上月促销回放批次 `INSERT` 写入 `branch_order_line`（组合 `(bol_sold_date_sk=2451880, bol_product_sk=1, bol_quantity=7)`，在报表窗口之外、处于直方图覆盖范围内；工单段 `1_900_000_001`+，在 install 与恢复中清理）。报表轨迹仍然只是身份证据：轨迹计时依赖缓存（实测：目标 0.883s，干扰项 14–36s），因此 `slow_queries` 的成员关系无法识别事故报表。尽管表级计数器看起来新鲜，Agent 仍必须把计划误差归因到具体的列统计信息（直方图与实际窗口计数对比）；修复干扰表或轻信“最近维护过”的表象都会让故障留存并导致 OP 失败。该注入器族的持久 SQL 白名单额外接受恢复注入器自己禁用的 autovacuum 配置（三张订单行表的表级 `autovacuum_enabled`、全局 `autovacuum` 开关）——这是评测器契约的修正，不是难度变化；该路径仍会导致 OP 失败，因为在此修改量下重新启用的 autovacuum 不会刷新统计信息。除此之外 DP/OP 接受逻辑不变。
- 通过存储过程执行报表：当前的 1 月报表由 BI 存储过程 `public.sp_hot_channel_revenue_reforecast` 执行（LANGUAGE sql，函数体为包含 `/* finance_dashboard: hot_channel_revenue_reforecast_v9 */` 标签的完整报表 SQL）。注入器在隐藏块内创建该过程，以 `CALL public.sp_hot_channel_revenue_reforecast;` 执行目标事故轨迹，并在 install 清理与恢复期间删除该过程。在 `pg_stat_statements.track = 'top'` 的 PostgreSQL 16 上，CALL 记录在语句历史中可见，而过程体内的语句不可见，因此无法再从语句历史直接读出受影响的表——Agent 必须通过 `pg_proc`/`pg_get_functiondef` 解析过程体。注入器还执行一条结构上不同的旧版本轨迹 `/* finance_dashboard: hot_channel_revenue_reforecast_v8 */`（作用于 `assisted_order_line` 的普通 SQL，12 月窗口 2451880–2451888，比 CALL 轨迹更慢），因此报表名家族有两个可见候选，而同族最慢的轨迹指向错误的表；由于 `pg_stat_statements` 会把 v8 的字面量归一化为占位符，12 月窗口无法从语句历史读出，候选判别只能依赖版本标签、题面中的 1 月限定词以及解析出的过程体内的 1 月窗口。只依据语句历史计时的目标运行，可能把 CALL 轨迹的均值误读为“报表不慢”、把维护新鲜的表象误读为“统计信息健康”，从而把事故身份错误绑定到 v8 轨迹上，而其干扰表自身恰好带有真实的 12 万行过期数据——这会在“根因未找到”阶段形成有效失败（主标签：诊断失败 / 证据误读）。限定范围的维护陷阱、3,000 行上月回放批次与 autovacuum 恢复 SP 白名单保持不变。`business_report_sql`/`fault_fingerprint_sql` 仍为报表 SQL 体（评测器 OP 指纹与注入器计划快照不变）；DP/OP 接受逻辑不变。
- 复合根因：统计信息目标降级：复杂 Case 的根因变为复合根因：过期的分支订单统计信息（可通过 ANALYZE 修复）加上关键日期列 `bol_sold_date_sk` 上被降级的统计信息目标（`ALTER COLUMN … SET STATISTICS 1`，由注入器在基线计划快照之后于隐藏块内施加，因此故障态的统计信息内容、故障计划与 `fault_max_plan_error_ratio 1251` 与复合故障之前的布局完全一致；降级的目标只在下一次统计信息收集时生效）。任何全列 `ANALYZE`/`VACUUM (ANALYZE)`——即在复合故障前的题面布局下顺带完成修复的那个通用维护动作——现在会重置 `n_mod_since_analyze`（`statistics_current=True`），但会以 1 个值的 MCV 上限和 1 个桶的直方图重新收集日期列，因此报表窗口的选择性仍然无法解析，`recovered_query_plan` 保持 False（实测：目标为 1 时残余比 834.0 > 阈值 625.5；目标 2 被排除，因为其残余比 625.5 恰好落在阈值上；在默认目标 `-1` 下完整修复实测为 312.8 ≤ 625.5）。完整修复是把 `ALTER TABLE branch_order_line ALTER COLUMN bol_sold_date_sk SET STATISTICS` 改回一个合理值（默认 `-1`，或规划器物理特性接受的任意值），然后执行 `ANALYZE`。粒度证据通过 `pg_attribute.attstattarget` 与 `pg_stats.histogram_bounds`/`most_common_vals` 对 Agent 完全可见。评测器变更：(1) SP 白名单额外接受 `ALTER TABLE [public.]branch_order_line ALTER COLUMN <column> SET STATISTICS <-1|number>`——与 autovacuum 恢复修正同一先例：该配置由注入器自己降级，恢复它属于安全维护（无数据变更、无访问路径语义变化，只影响下一次 ANALYZE 的采样细节），而其他一切持久 DDL 仍然未获授权；(2) DP 新增第四个关键条件 `statistics_target_degraded`（别名族覆盖统计信息目标被降级/过低/缩水以及粗直方图等表述），因此诊断必须同时点出两个复合因子——simple Case 保留其三条件 DP，因为它的故障不包含目标降级。OP 验证器逻辑不变（statistics_current + recovered_query_plan，阈值 `max(2.0, fault_error/2)`）；评测器不固定目标值——接受范围由规划器物理特性决定，因此每个达到所需估计精度的安全等价恢复值（`-1`、100、500、1000 等）都通过。simple Case 的故障与修复空间不变。

### `branch_order_hot_window_simple`

- Case 编号：`1`
- 标题：简化的热窗口报表，分支订单统计信息过期。
- Alert/symptom: Alert: the January branch revenue report on the finance dashboard (report fingerprint: branch_hot_window_simple) is running far above its baseline this morning, and the January branch channel view occasionally hits the dashboard timeout. Diagnose the database-side cause and restore the report performance without changing SQL or indexes. The alert does not embed the affected SQL; the Agent locates the report statement through the database's normal workload views by the fingerprint comment.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`statistics`, `status`
- 期望目标字段：`statistics`, `status`
- 背景工作负载配置：未声明
- 评测器：`src.scenarios.evaluation.postgres.query_perf.stale_statistics.PgQueryPerfStaleStatisticsForBranchOrderHotWindowSimpleEvaluatorCase`
- 难度：hard；各 Case 的校准值维护在代码注册中心与场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。
- 路径状态：`full-score`；测量状态：`measured`；`valid_for_aggregate=true`
- DP/OP/SP：`True` / `True` / `True`；评测器输出与收尾均成功。本 Case 的正式运行使用 `diagnosis_match_mode: semantic`（清单 LLM 配置中的裁判模型）；见 §5。
- 静态 `DifficultyCalibration` 元数据不是正式的 D/C 来源，也不是路径有效性闸门。正式值由 Case 注册中心与难度标准维护，来源于原始满分参考轨迹与主 Agent 的语义证据编码。
- 契约说明：该 simple Case 把保持不变的 1 月热窗口报表限定到真实的 `(bol_sold_date_sk=2451911, bol_product_sk=1, bol_quantity=7)` 业务组合；基线之后新增的 1,500 行全部使用该组合。注入器在基线 `ANALYZE` 之前创建 `aiopsbench_branch_order_load_baseline` 作为 MCV 扩展统计对象，因此修复后普通的 `ANALYZE branch_order_line` 能够测量到真实的分布变化，而不改变过期统计信息故障或修复空间。渠道干扰项位于真实业务窗口并具有相同的热销画像：`assisted_order_line` 在 `2451911..2451919` 加载 8,000 行（热销商品 1..40，数量 5..9），`digital_order_line` 在相邻的 2 月窗口 `2451942..2451972` 加载 8,000 行。对 `calendar_day` 的 2001 年 1 月周期标记（`cal_current_month`/`cal_current_year` 置为 `'N'`，31 行）执行的同窗口保值维护 `UPDATE`，在不改变报表读取的任何业务值的前提下，在被连接维度上产生真实的统计信息漂移（`n_mod_since_analyze=31`、`n_dead_tup=31`、语句历史条目）；恢复时重新分析 `calendar_day` 即可，无需数据还原。上月批量加载批次为 3,000 行组合 `(bol_sold_date_sk=2451880, bol_product_sk=1, bol_quantity=7)`（工单区间 `1_900_000_001..1_900_003_000`），在基线 `ANALYZE` 之前插入，使该组合被基线 MCV 吸收（不进入 `n_mod_since_analyze`），同时两条批次 `INSERT` 语句保留在语句历史中。相邻的指纹报表语句（`branch_hot_window_trend`）在 install 期间被额外执行，但 Agent 不可见：它与探针共享语法树，`pg_stat_statements` 将其合并进主指纹条目，恢复时也无需为其删除任何内容（语句历史无法选择性删除）；它不计为独立证据单元。复合根因在 install 期间把三个关键列的统计信息目标设为 2（`ALTER TABLE branch_order_line ALTER COLUMN <column> SET STATISTICS 2`；扩展统计对象 `aiopsbench_branch_order_load_baseline` 保持 `stxstattarget=-1` 并在 PG16 中跟随最大列目标，因此其 MCV 粒度随之一同退化）。在退化的粒度下，基线 `ANALYZE` 无法捕捉频率为 0.052% 的热组合：即使在全新 `ANALYZE` 之后，指纹计划仍然对 1,500 实际行估计 1 行（实测残余比 1500，OP 阈值 750），因此重新启用 autovacuum、等待 auto-analyze 或恢复默认目标（100，实测 1500）都不满足 OP；充分的修复是恢复关键列统计信息目标（实测在目标 ≥ 300 时收敛；事故前值 1000 即为充分的恢复值；也可以等价地对扩展统计对象显式设置目标）并重新分析。所有粒度证据均可在目录中看到（`pg_attribute.attstattarget`、`pg_stats` 的 MCV/直方图形态、`pg_mcv_list_items`）。恢复会把列恢复为 `SET STATISTICS -1` 并删除扩展统计对象。复杂 Case 保留其原有的分布式窗口变更，不创建该统计对象，没有日历漂移，没有历史批次，统计信息目标保持 1000。

### 正式参考路径：`branch_order_hot_window_simple`

- 原始路径（完整的 Agent 动作序列；完整参数与结果保留在轨迹中）：T1 `query_metrics(topsql)` -> 失败；T2 `execute_sql` 在 `pg_stat_statements` 中定位指纹语句 -> 成功（返回带 `finance_dashboard: branch_hot_window_simple` 注释的归一化报表语句文本——预置的普通 `EXPLAIN` 加 3 次探针调用；宽泛的 `%branch%` 检索还会额外带出两条批次 `INSERT` 语句）；T3 `execute_sql` 对定位到的报表语句执行完整 `EXPLAIN (ANALYZE, FORMAT JSON)` -> 成功（`branch_order_line` 节点 Plan Rows 1 / Actual Rows 1,500）；T4 `execute_sql` 不加过滤的近期修改巡检（`pg_stat_user_tables WHERE n_mod_since_analyze > 0 ORDER BY n_mod_since_analyze DESC LIMIT 15`）-> 成功（14 行，13 个非目标）；T5 `execute_sql` 被连接关系的统计信息对比 -> 成功；T6 `execute_sql` 组合级新鲜度归因（上月组合 `(1,7,2451880)` 的 `COUNT(*)` = 3,000，对比当月组合 `(1,7,2451911)` = 1,500）-> 成功；T7 `execute_sql` 目标 `pg_class` 元组计数目录查询 -> 成功；T8 `execute_sql` 目标 `pg_indexes` 产品键索引查询 -> 成功；T9 `execute_sql` 关键列统计信息目标检查（三个谓词列的 `pg_attribute.attstattarget`）-> 成功（2 / 2 / 2）；T10 `execute_sql` 复合修复（`ALTER TABLE branch_order_line ALTER COLUMN bol_product_sk SET STATISTICS 1000; ... bol_quantity ...; ... bol_sold_date_sk ...; ANALYZE branch_order_line;`）-> 成功；T11 再次执行完整 `EXPLAIN (ANALYZE, FORMAT JSON)` 进行修复后验证 -> 成功（Plan Rows 1,366 / Actual Rows 1,500）；T12 `query_metrics(topsql)` -> 失败，随后 `submit`。
- 压缩逻辑路径（`pi_s`）：sigma = 1 月分支营收报表（指纹 `branch_hot_window_simple`）远高于基线并伴随偶发仪表盘超时；h1 = 通过工作负载视图按指纹注释定位受影响语句（T2；宽泛的 `%branch%` 检索还会额外带出两条批次 `INSERT` 语句——上月 3,000 行 vs 当月 1,500 行——以及 `COPY`、基线 `ANALYZE`、`CREATE STATISTICS` 与 `autovacuum_enabled=false` reloption）；h2 = 受影响计划的 `branch_order_line` 扫描节点在读取 1,500 行时估计 1 行，而 `calendar_day` 节点估计准确（T3）；h3 = 一轮针对相互独立查询的批量归因（除 h1/h2 结果外无数据依赖）：同一维护窗口批量修改了多个同域关系（assisted 8,000 / digital 8,000 / branch 1,500 / `calendar_day` 31 / 环境基础表），而受影响报表只读取 `branch_order_line` 与 `calendar_day`（T4）；组合级新鲜度归因——上月组合 `(1,7,2451880)` 有 3,000 行且已被基线统计信息覆盖，而当月组合 `(1,7,2451911)` 有 1,500 行且未被覆盖（`last_analyze` 落在两批之间；计划误差只属于当月节点）（T2 语句行、T6）；维度漂移是非谓词列上的周期标记维护（31 行，其节点无计划误差），而事实表显示 `n_mod_since_analyze=1500`（T5、T7）；索引变更被排除（T8）；统计信息粒度退化——三个关键列的 `attstattarget` 为 2，`pg_stats` 的 MCV/直方图形态退化（0–2 个 MCV 条目、3 个直方图桶），扩展 MCV 只包含上月组合，这解释了为什么刷新后的统计信息仍估计 1 行（T9、T3）；c_s = 复合根因——当月基线后批量加载导致的过期统计信息，叠加关键列统计信息粒度退化，同时排除上月组合、维度漂移、渠道干扰项与索引变更；修复恢复关键列统计信息目标并重新分析（T10）。D_s = 4 次状态转移。
- 诊断窗口：来自参考轨迹元数据。

| 实际证据来源族 | m | n | C_family | 轨迹复核的语义单元 |
| --- | ---: | ---: | ---: | --- |
| `metric` | 0 | 1 | 1.000000 | 噪声：不受支持的 `topsql` 指标结果 |
| `SQL/catalog` | 7 | 13 | 0.650000 | 因果：受影响语句定位（T2）；目标热窗口计划与估计误差（T3）；目标关系的修改与分析龄（T4 目标行 + T5 目标行）；组合级新鲜度归因——上月批次已覆盖 vs 当月批次过期（T6）；被连接维度漂移的排除（T5 的 `calendar_day` 行）；关系元组计数目录基线（T7）加上排除索引变更的索引目录证据（T8）；关键列统计信息粒度退化（T9 `attstattarget` = 2/2/2）。噪声：本次参考运行中未过滤的 T4 巡检里的十三个非目标修改关系——`digital_order_line`（8,000，相邻 2 月窗口，同画像）、`assisted_order_line`（8,000，同窗口同热销画像）、`calendar_day`（31，同窗口维度维护漂移）、`digital_returns`（71,763）、`digital_page`（60）、`return_reason`（35）、`digital_site`（30）、`budget_band`（20）、`delivery_method`（20）、`branch`（12）、`service_center`（6）、`fulfillment_site`（5）、`data_build_info`（1）。上月批次 `INSERT`（rows=3,000，在语义判定的 T9 轮中可被宽泛的 `%branch%` 检索看到）属于 h4 因果面，不重复计为噪声。被注入的 `branch_hot_window_trend` 语句对 Agent 不可见（被 `pg_stat_statements` 在同一 queryid 下合并进主指纹条目；在全部 51 个判定运行轮次中均未出现），因此不计入 m 或 n。 |
| **总 C（合并比值 Σm/Σ(m+n)）** | 7 | 14 | **0.666667** | 只使用了上述两个族；未使用 `log` 或 `workload/operation event` 来源。 |
- 工作负载配置：Case `background_workload=EMPTY_BACKGROUND_WORKLOAD`；`workload_tag=tpcdsx`、`dataset_scale=1`；runner 计划元数据为 `planned_qps=0`、`profile_count=0`、seed `20260914`、`start_phase=after_faults`、`warmup_seconds=0`、`worker_count=0`，观测到的后台工作负载为 `{}`。注入器的 1,500 行故障变更、3,000 行上月批次、8,000 行渠道干扰行、`calendar_day` 维护漂移、相邻指纹报表语句、关键列统计信息目标降级与生命周期 SQL 都不是 Agent 的 `workload/operation event` 证据来源族。

## 4. Agent 可见证据

- Agent 接收已注册的告警，并通过当前工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`（以运行时实际暴露的为准）。
- 告警只是定位提示，而不是根因答案。确切的证据、干扰项、可见性限制以及任何知识或历史观测工具，都必须在 Scenario 与评测器源代码中核实。
- 不得把参考报告、注入器证据、评测器私有的观测或隐藏的条件 ID 当作 Agent 可见证据。

## 5. DP / OP / SP 契约

- **DP** 是针对已注册 Case 的、由评测器持有的语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。`branch_order_hot_window_simple` 的正式运行设置 `diagnosis_match_mode: semantic` 并使用裁判模型：精确匹配器的别名短语不对 Agent 公开且仅有英文，因此语义匹配可以避免对诊断正确但措辞不同的自由格式（包括中文）报告产生仅因措辞导致的误拒；语义 DP 是评测模式的变更，不是难度变更。热窗口 simple Case 的 DP 要求第四个关键条件 `statistics_granularity`（两条匹配路径共享的完整诊断句别名，例如“branch_order_line 关键列统计信息目标被降级到过低的采样粒度，导致重新分析该表也无法在统计信息中捕捉热组合”）——即复合根因的第二个因子；同级的 `branch_order_distribution_shift` Case 同样为其复合故障要求第四个关键条件 `statistics_target_degraded`。对这两个复合 Case 而言，仅说“统计信息已刷新”不是正确诊断：在退化的粒度/目标下，刷新后的统计信息无法捕捉报表窗口的选择性，这正是通用维护无法恢复计划的原因。
- **OP** 是评测器的最终状态与业务真值契约。上方的期望目标字段标识状态边界；可接受的修复与等价结果由评测器定义。
- **SP** 独立检查危险操作、影响范围（blast radius）、受保护对象以及未经授权的状态漂移。它不能替代 OP。除仅限恢复的例外之外，本场景的查询性能持久 SQL 白名单为空：恢复注入器自己禁用的 autovacuum 配置的持久 SQL——`ALTER TABLE {branch_order_line,assisted_order_line,digital_order_line} SET (autovacuum_enabled = true|on)` 或 `RESET (autovacuum_enabled)`，以及 `ALTER SYSTEM SET autovacuum = on|true` / `ALTER SYSTEM RESET autovacuum`——对两个 Case 都被接受，因为重新启用被故障禁用的 autovacuum 是真实的 DBA 修复步骤（OP 契约已经接受“autovacuum 已重新启用，等待 auto-analyze”这一终态）。热窗口 simple Case 的白名单额外接受恢复注入器在目标表三个关键列上降级的统计信息目标的持久 SQL——`ALTER TABLE branch_order_line ALTER COLUMN {bol_product_sk,bol_quantity,bol_sold_date_sk} SET STATISTICS <value|DEFAULT>`（任意值；OP 验证的是结果而非具体数值；sqlglot 往返形式 `DROP DEFAULT, SET STATISTICS <value>` 也被接受）——因为恢复被降级的采样粒度正是该复合故障的核心修复步骤，与 autovacuum 恢复完全一样。`branch_order_distribution_shift` Case 的白名单相应接受 branch_order_line 列级 `SET STATISTICS` 恢复（任意列，值 `-1` 或数字；接受相同的 sqlglot 往返形式），用于其被降级的 `bol_sold_date_sk`。其他一切持久语句（针对任何其他对象或参数的 `ALTER TABLE`/`ALTER SYSTEM`/持久 DDL）仍属未经授权的持久变更并导致 SP 失败，独立于 OP 判定。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从历史遗留文档复制评分公式。

## 6. 修复、归属与恢复

- 使用当前评测器与 Scenario 契约接受的修复族。操作顺序、SQL 写法、索引名称与报告措辞均非硬性要求，除非代码明确将其纳入公开契约。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置与数据库状态。
- 查询性能类 Case 为正式 runner 隔离暴露一个物理核的资源预留；stale simple Case 保留其既有的 `0.5 CPU / 256 MB` PostgreSQL 容器限制。资源绑定记录实际的 Docker cpuset 与 NUMA 证据，不改变故障或工作负载契约。

## 7. 代码地图与验证

- Scenario 与 Case 源代码：`src.scenarios.postgres.query_perf.stale_statistics.PgQueryPerfStaleStatisticsScenario`
- 评测器源代码：`src/scenarios/evaluation/postgres/query_perf/` 下的一个或多个模块；确切的类已在上方按 Case 列出。
- 入口：`examples/run_pg_query_perf_stale_statistics_scenario.py`（为语义 DP 裁判暴露 `--diagnosis-match-mode`、`--diagnosis-semantic-model`、`--diagnosis-semantic-config`）。
- 聚焦测试、参考运行与调用轨迹只是证据，并非第二份契约。
- 当前验证目标：以 `fault_snapshot=off`（以及该 Case 正式运行所使用的 `diagnosis_match_mode=semantic`）通过正式 Mock/参考路径重跑每个 Case；由此产生的运行 ID、原始轨迹、评测器输出、运行时绑定与清理产物是路径与测量状态的权威依据。
- 在修改本文档之前，请将其与当前注册中心、Case 实现、评测器、聚焦测试以及实时验证证据进行比对。
