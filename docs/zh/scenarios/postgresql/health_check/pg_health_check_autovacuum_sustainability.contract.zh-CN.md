---
doc_id: scenario.postgresql.pg_health_check_autovacuum_sustainability
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, health_check, pg_health_check_autovacuum_sustainability]
summary: pg_health_check_autovacuum_sustainability 的当前代码背书契约快照；包含其注册的 Case、状态边界、评估器身份与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_health_check_autovacuum_sustainability`

> 本文件是当前由注册表支撑的场景契约。请先阅读数据库目录进行导航，并在修改实现之前，于链接的源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`health_check`
- 场景实现：`src.scenarios.postgres.health_check.autovacuum_sustainability.PgHealthCheckAutovacuumSustainabilityScenario`
- 正式入口：`examples/run_pg_health_check_autovacuum_sustainability_scenario.py`
- 当前描述：审计 PostgreSQL autovacuum 清理能力在真实数据变更下是否仍然可持续。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `capacity_deficit` | 带多表数据变更、OLTP 与 TPC-DS 噪声的困难版 autovacuum 可持续性审查。 | `hard` |
| 1 | `capacity_deficit_simple` | 带一个目标、一个干扰项和一个确定性 OLTP 画像的简单版 autovacuum 可持续性审查。 | `hard` |

上表是当前的代码快照。缺失的校准是显式的，不得从未注册的标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公共状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 和评估器实现所有；本文档不编造代码中不存在的值。

### `capacity_deficit`

- Case 编号：`0`
- 标题：带多表数据变更、OLTP 与 TPC-DS 噪声的困难版 autovacuum 可持续性审查。
- Alert/symptom: [Scheduled PostgreSQL Health Check] The next trading window is expected to increase write volume. Start with the compact metric overview, select one candidate relation/window, then use bounded history queries to review relation maintenance sustainability and prove that the next replay window keeps cleanup bounded without disabling maintenance or degrading OLTP. Change only relations whose repeated completed maintenance cycles prove a sustained deficit; relations that recover within the published replay window are healthy business objects and must remain unchanged. Acceptance uses the latest 8 samples: target backlog growth must be <=300 tuples, effective removal must reach at least 75% of generation, OLTP p99 must be <=6000 ms, and success rate must be >=0.98. From adjacent raw samples, generation is the sum of positive deltas in `n_tup_ins`, `n_tup_upd` and `n_tup_del`. When `last_autovacuum` or `last_vacuum` advances, effective removal is `max(previous n_dead_tup + generation - current n_dead_tup, 0)`; otherwise it is zero. HARD HISTORY BOUNDARIES: first call query_metrics without timestamps for the compact overview; then choose exactly one evidence interval no longer than 900 seconds and use that same interval for the required metrics/logs. Never request a multi-hour explicit window, never retry an identical failed window, and after a history-window error either select a narrower interval or submit the evidence already collected.
- 初始状态字段：`database`、`relation_mix`、`status`、`workload`
- 期望目标字段：`autovacuum`、`backlog`、`oltp_p99_ms`、`status`、`target`
- 背景画像：business_write_01、business_write_02、business_write_03、business_write_04、business_write_05、business_write_06、business_write_07、business_write_08、tpcds_light_q3、tpcds_medium_q2
- 评估器：`src.scenarios.evaluation.postgres.health_check.autovacuum_sustainability.PgHealthCheckAutovacuumSustainabilityForCapacityDeficitEvaluatorCase`
- 公共历史：冻结历史在故障激活前从实时 CaseRun 捕获，并在 Agent 交接前冻结。它以 2 秒粒度、20 秒总览暴露原始的 `relation_churn`、`vacuum_cleanup`、`dead_tuple_backlog`、`maintenance_io`、`oltp_service` 和 `xmin_horizon`；有界历史记录为 `operation_event` 和 `component_log`。
- 历史几何：12 小时可见时间线、900 秒正常捕获、600 秒目标捕获、目标距今 1,800-10,800 秒，以及从真实正常捕获中选出的两个“捕获时为良性”的 relation-churn 竞争者。公共历史不包含任何诊断或派生的缺口字段；终态结果验证使用可信实时重放而非冻结历史。
- 难度：hard；逐 Case 校准值由代码注册表和场景目录维护；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。
- 测量状态：`path_status=full-score`、`measurement_status=measured`。
- 可信验收重放：对目标关系基线之后的数据变更批次应用 `replay_churn_multiplier=3.0`，以模拟公告的下一个写入窗口；实时数据变更、正常/目标捕获、干扰项、历史几何与查询预算均不变。OutcomePass `target_controlled` 要求在诊断出的目标上做有界的单关系容量提升（`autovacuum_enabled=true` 加上偏离已配置基线的目标 reloptions），因此无操作、错误目标和全局性修复都无法通过。
- 诊断窗口：参考证据查询在可见尾部使用有界的 900 秒区间，在该区间内目标的持续缺口状态保持可见；冻结目标窗口真值为 UTC `2026-09-14 17:36:10` 至 `2026-09-14 17:39:08`。
- 原始路径：`T1 overview relation_churn/dead_tuple_backlog/maintenance_io`；`T2 target-window relation_churn/vacuum_cleanup/dead_tuple_backlog, operation_event history, component_log history, and reloptions for all eight relations`；`T3 target-scoped ALTER TABLE repair followed by VACUUM`；`T4 sleep, repeat VACUUM, workload_activity, final catalog read, and submit`。
- 压缩路径：(1) 建立八关系的长窗口候选集及正常/目标窗口；(2) 跨窗口联合比较数据变更生成、vacuum 清理与死元组积压；(3) 利用操作事件、组件日志和 reloptions 上下文确认目标专属的持续缺口，并排除健康邻居与静态捷径；(4) 在保留 autovacuum 的前提下选择仅针对目标的有界清理容量修复。
- 深度核算：重复查询、轮询、分页、修复执行、修复后验证和提交不计入诊断深度。
- 证据单元台账：由 Case 注册表和难度标准维护；单元是未过滤轨迹结果中的语义单元，没有预过滤噪声，也没有填充的零值。
  `metric` 的因果单元是目标数据变更生成、目标清理缺口、目标积压增长和目标专属邻居对比；其噪声单元是正常关系状态、健康邻居对比集、被捕获的健康目标突发、被捕获的健康邻居突发，以及维护 I/O 上下文。`log` 结果只包含观测者查询日志上下文，没有可用的自动清理因果记录，因此贡献一个语义噪声单元而不贡献因果单元。`SQL/catalog` 的因果单元是目标的普通/共享 reloptions 上下文；七个受保护邻居的对比上下文是噪声。`operation_event` 窗口没有返回已完成的 vacuum 事件，这是可观测的否定证据并算作一个因果单元，而不是捏造的零值或机械统计的空结果。
- 总体复杂度：`C = (12 + 34 + 15) / (15 + 41 + 19) = 61/75 = 0.813333`。
- 工作负载：十个实时画像（`business_write_01` 至 `business_write_08`、`tpcds_light_q3`、`tpcds_medium_q2`）、计划 QPS `0.81`、`worker_count=3`、工作负载种子 `44801`（`0xAF01`）、历史种子 `20260914`、`start_phase=before_faults`、预热 `5s`；十个画像全部在 CaseRun 正常/目标捕获期间运行，保留的注入器数据变更加 pgbench 驱动可信重放。
- 历史/运行时证据：实时冻结历史 SHA-256 `051344f41cf3070e8d7fb3f4557683f6ac58281929605b1fe9672aa2ced0c5a8`；可见范围为 UTC `2026-09-14 08:06:32` 至 `2026-09-14 20:06:30`；正常捕获 `20:01:28`-`20:03:28`；目标捕获 `20:03:30`-`20:06:30`；目标窗口真值 `17:36:10`-`17:39:08`，其前相邻有四个干扰项（`healthy-target-burst`、`metric-only-backlog-wave`、`metric-only-cleanup-wave`、`healthy-neighbor-burst`）；`missing_sample_count=0`、`generated_sample_count=353965`（目标后平台期保留加 60 个仅指标干扰样本）、`point_count=583200`、`metric_only_sample_count=60`。未使用冻结暂存 SQL 或捏造的指标。
- `DifficultyCalibration` 仅是元数据：其 `diagnostic_depth` 与本次轨迹审计一致，而其遗留的因果/噪声证据单元字段不用于计算按族加权的复杂度；缺少校准/工具证据/来源台账元数据不构成路径有效性失败。

### `capacity_deficit_simple`

- Case 编号：`1`
- 标题：带一个目标、一个干扰项和一个确定性 OLTP 画像的简单版 autovacuum 可持续性审查。
- Alert/symptom: [Scheduled PostgreSQL Health Check] One relation is accumulating cleanup work during a predictable write profile. Compare the target with the decoy, apply only a bounded target-level control, and verify the next write window.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`relation_mix`、`status`、`workload`
- 期望目标字段：`autovacuum`、`backlog`、`oltp_p99_ms`、`status`、`target`
- 背景画像：pgbench_oltp_target_simple
- 评估器：`src.scenarios.evaluation.postgres.health_check.autovacuum_sustainability.PgHealthCheckAutovacuumSustainabilityForCapacityDeficitSimpleEvaluatorCase`
- 难度：hard；D=3、C=0.678571、reference=pending_pg_hc_mf01_capacity_deficit_simple_reference
- 校准证据（工具 m/n）：代码中未声明

## 4. Agent 可见的证据

- Agent 接收注册的告警，并在运行时暴露的范围内通过当前工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`。
- 告警只是定位提示，而不是根因答案。确切的证据、干扰项、可见性限制以及任何知识或历史观测工具，都必须在场景与评估器源代码中核实。
- 不要把参考报告、注入器证据、评估器自有的观测或隐藏的条件 ID 当作 Agent 可见的证据。

## 5. DP / OP / SP 契约

- **DP** 是注册 Case 的评估器自有语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
- **OP** 是评估器的终态与业务事实契约。上文的期望目标字段界定了状态边界；被接受的修复与等价结果由评估器定义。
- **SP** 独立检查危险操作、影响范围、受保护对象以及未经授权的状态漂移。它不是 OP 的替代品。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从遗留文档复制历史评分公式。

## 6. 修复、归属与恢复

- 使用当前评估器和场景契约接受的修复族。操作顺序、SQL 写法、索引名称和报告措辞都不是硬性要求，除非代码明确将其纳入公共契约。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前的五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置和数据库状态。

## 7. 代码地图与验证

- 场景与 Case 源码：`src.scenarios.postgres.health_check.autovacuum_sustainability.PgHealthCheckAutovacuumSustainabilityScenario`
- 评估器源码：`src/scenarios/evaluation/postgres/health_check/` 下的一个或多个模块；确切的类已在上方逐 Case 列出。
- 入口：`examples/run_pg_health_check_autovacuum_sustainability_scenario.py`
- 聚焦测试、参考运行和轨迹是证据，而不是第二份契约。
- 在修改本文档之前，请将其与当前注册表、Case 实现、评估器、聚焦测试和实际验证证据进行比对。
