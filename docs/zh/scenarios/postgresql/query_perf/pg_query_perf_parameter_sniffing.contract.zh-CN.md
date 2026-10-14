---
doc_id: scenario.postgresql.pg_query_perf_parameter_sniffing
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, query_perf, pg_query_perf_parameter_sniffing]
summary: pg_query_perf_parameter_sniffing 的当前基于代码的契约快照；包含其注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_query_perf_parameter_sniffing`

> 这是当前基于注册中心的场景（Scenario）契约。请先阅读数据库目录进行导航，然后在修改实现之前，于关联源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`query_perf`
- 场景实现：`src.scenarios.postgres.query_perf.parameter_sniffing.PgQueryPerfParameterSniffingScenario`
- 正式入口：`examples/run_pg_query_perf_parameter_sniffing_scenario.py`
- 当前描述：参数化客户营收报表在大容量绑定值下发生退化。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `branch_order_year_skew` | 参数化客户营收报表在大容量绑定值下发生退化。 | `hard` |
| 1 | `branch_order_year_skew_simple` | 紧凑客户营收查询在某个大容量绑定值下退化。 | `easy` |

上方的 Case 集合是当前的代码快照。缺失校准是显式状态，不得从非注册标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现持有；本文档不杜撰代码中不存在的值。

### `branch_order_year_skew`

- Case 编号：`0`
- 标题：参数化客户营收报表在大容量绑定值下发生退化。
- Alert/symptom: Alert: customer 360 revenue segmentation dashboard latency is unstable. The report is usually fast for smaller historical cohorts, but the January-February 2001 customer segment now exceeds the dashboard SLO and dominates recent topsql mean/max latency. Diagnose the production query path from database evidence and restore the slow dashboard without changing report semantics.
- 初始状态字段：`report`, `status`
- 期望目标字段：`report`, `status`
- 背景工作负载配置：未声明
- 评测器：`src.scenarios.evaluation.postgres.query_perf.parameter_sniffing.PgQueryPerfParameterSniffingForBranchOrderYearSkewEvaluatorCase`
- 难度标签与各 Case 的校准值维护在代码注册中心与场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复述这些实测值。

### `branch_order_year_skew_simple`

- Case 编号：`1`
- 标题：紧凑客户营收查询在某个大容量绑定值下退化。
- Alert/symptom: Alert: the customer revenue lookup is slow only for the January-February 2001 cohort. The same prepared report is fast for an empty historical cohort. Diagnose the database-side cause and restore the report without changing its result.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`report`, `status`
- 期望目标字段：`report`, `status`
- 背景工作负载配置：未声明
- 评测器：`src.scenarios.evaluation.postgres.query_perf.parameter_sniffing.PgQueryPerfParameterSniffingForBranchOrderYearSkewSimpleEvaluatorCase`
- 难度：`hard`；各 Case 的校准值维护在代码注册中心与场景目录中。题面只点名业务症状，不内嵌根因细节。
- 路径状态：`full-score`；测量状态：`measured`；`valid_for_aggregate=true`
- DP/OP/SP：`True` / `True` / `True`；评测器输出与收尾均成功。
- 静态 `DifficultyCalibration` 元数据不是正式的 D/C 来源，也不是路径有效性闸门。正式值由 Case 注册中心与难度标准维护，来源于原始满分参考轨迹与主 Agent 的语义证据编码。
- 契约说明：紧凑报表保留 2001 年 1-2 月客群与空历史客群对比的语义，同时在参数化 SQL 中约束相应的日期键范围。其 simple Case 支撑状态使用 Case 自有的 `idx_aiopsbench_worker_hot_date` 部分索引来覆盖热日期范围；full Case 保留原有的完整分支订单支撑索引。其因果诊断使用评测器的 `parameter sniffing plan mismatch` 别名；参考入口不改写 Case 报告。

### 正式参考证据：`branch_order_year_skew_simple`

- 原始路径（完整的 Agent 动作序列；完整参数与结果保留在轨迹中）：T1 `query_metrics(topsql)` -> 失败；T2 重复的 `query_metrics(topsql)` -> 失败；T3 `execute_sql` 查询 `pg_stat_statements` 定位对绑定值敏感的报表 -> 成功；T4 `execute_sql` 查询 `pg_prepared_statements` -> 成功；T5 `execute_sql` 对热绑定值执行 `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` -> 成功；T6 `execute_sql` 执行 `SET plan_cache_mode = 'force_custom_plan'` 与 `DEALLOCATE ALL` 修复 -> 成功；T7 `execute_sql` 执行 prepare 与修复后 EXPLAIN 验证、`query_metrics(topsql)` -> 失败、`execute_sql` 预处理语句验证 -> 成功，随后 `submit`。
- 压缩逻辑路径：(1) 定位对绑定值敏感的客户营收查询；(2) 识别 generic/custom 计划失配及其对热绑定值的性能影响；(3) 选择 `force_custom_plan` 作为限定范围的计划缓存修复决策。重复查询、轮询、翻页、修复执行、修复后验证与提交不计入诊断深度。
- 诊断窗口：从参考运行的轨迹元数据读取的约 7 秒区间。

- 证据单元台账：由 Case 注册中心与难度标准维护；单元是未过滤轨迹结果中的语义单元（不是 SQL 行、日志行、指标样本或工具调用），没有预过滤噪声，也没有填充的零值。

- 工作负载配置：Case `background_workload=EMPTY_BACKGROUND_WORKLOAD`；`workload_tag=tpcdsx`、`dataset_scale=1`；runner 计划元数据为 `planned_qps=0`、`profile_count=0`、`seed=0`、`start_phase=after_faults`、`warmup_seconds=0`、`worker_count=0`，观测到的后台工作负载为 `{}`。注入器播种的预处理语句与绑定值执行属于生命周期 SQL，不是 Agent 的 `workload/operation event` 证据来源族。
- 必要的 Case 兼容性接线：simple Case 使用 `support_index_variant=hot_window_partial` 与 `idx_aiopsbench_worker_hot_date`，其诊断报告使用评测器的 `parameter sniffing plan mismatch` 别名。故障组合、工作负载、拓扑、参数含义、强度、修复空间、安全性、评测器以及 DP、OP、SP 逻辑均未改变。

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
- 查询性能类 Case 为正式 runner 隔离暴露一个物理核的资源预留；参数嗅探 simple Case 保留其既有的 `1 CPU / 512 MB` PostgreSQL 容器限制。资源绑定记录实际的 Docker cpuset 与 NUMA 证据，不改变故障或工作负载契约。

## 7. 代码地图与验证

- Scenario 与 Case 源代码：`src.scenarios.postgres.query_perf.parameter_sniffing.PgQueryPerfParameterSniffingScenario`
- 评测器源代码：`src/scenarios/evaluation/postgres/query_perf/` 下的一个或多个模块；确切的类已在上方按 Case 列出。
- 入口：`examples/run_pg_query_perf_parameter_sniffing_scenario.py`
- 聚焦测试、参考运行与调用轨迹只是证据，并非第二份契约。
- 当前验证目标：以 `fault_snapshot=off` 通过正式 Mock/参考路径重跑 `branch_order_year_skew_simple`；由此产生的运行 ID、原始轨迹、评测器输出、运行时绑定与清理产物是路径与测量状态的权威依据。
- 在修改本文档之前，请将其与当前注册中心、Case 实现、评测器、聚焦测试以及实时验证证据进行比对。
