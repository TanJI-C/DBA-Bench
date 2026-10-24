---
doc_id: scenario.postgresql.pg_business_change_io_saturation
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, pg_business_change_io_saturation]
summary: pg_business_change_io_saturation 的当前代码背书契约；包含其注册的 Case、状态边界、评估器身份与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_business_change_io_saturation`

> 本文件是当前由注册表支撑的场景契约。请先阅读数据库目录进行导航，并在修改实现之前，于链接的源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`business_change`
- 场景实现：`src.scenarios.postgres.business_change.io_saturation.PgBusinessChangeIoSaturationScenario`
- 正式入口：`examples/run_pg_business_change_io_saturation_scenario.py`
- 当前描述：后台维护打满数据库 I/O 导致的慢查询告警。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `reporting_maintenance_io_saturation` | 后台维护打满数据库 I/O 导致的慢查询告警。 | `hard` |
| 1 | `vacuum_report_io_victim_simple` | 维护性刷新打满 I/O 导致的报表慢查询告警。 | `hard` |
| 2 | `archive_backlog_io_pressure` | 由 WAL 归档槽停滞（而非报表 SQL 退化）引起的 I/O 打满告警。 | `easy` |

上表是当前的代码快照。缺失的校准是显式的，不得从未注册的标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公共状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 和评估器实现所有；本文档不编造代码中不存在的值。

### `reporting_maintenance_io_saturation`

- Case 编号：`0`
- 标题：后台维护打满数据库 I/O 导致的慢查询告警。
- Alert/symptom: [FIRING: WARNING] alertname=PostgresReportQueryLatencyHigh service=tpcds-reporting instance=postgresql-primary severity=warning summary=Multiple TPC-DS report query fingerprints exceeded the slow-query threshold description=In the last 5m, customer revenue, regional sales, and inventory trend reports all exceeded 5s latency; p95 report latency is 18.4s. Please diagnose the shared cause of the concurrent query slowdown and restore latency.
- 初始状态字段：`alert`、`status`、`table`、`visible_symptom`
- 期望目标字段：`maintenance_sessions`、`root_cause`、`status`、`table`
- 背景画像：regional_sales_dashboard_refresh、report_temp_spill_rollup、invoice_cpu_rollup、order_status_touch_worker、missing_report_cache_log_noise
- 评估器：`src.scenarios.evaluation.postgres.business_change.io_saturation.PgBusinessChangeIoSaturationForReportingMaintenanceIoSaturationEvaluatorCase`
- 难度标签与逐 Case 校准值由代码注册表和场景目录维护；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约刻意不重复这些实测值。
### `vacuum_report_io_victim_simple`

- Case 编号：`1`
- 标题：维护性刷新打满 I/O 导致的报表慢查询告警。
- Alert/symptom: [FIRING: WARNING] alertname=PostgresReportQueryLatencyHigh service=ops-reporting instance=postgresql-primary severity=warning summary=Two operational reports crossed the slow-query threshold together description=Recent slow-query samples point at customer aging and shipment status reports, while host storage latency is elevated. A change window earlier today adjusted scheduled maintenance jobs. Restore report latency and keep other production workloads running unaffected.
- 初始状态字段：`alert`、`status`、`table`、`visible_symptom`
- 期望目标字段：`maintenance_sessions`、`root_cause`、`status`、`table`
- 背景画像：regional_sales_dashboard_refresh、report_temp_spill_rollup
- 评估器：`src.scenarios.evaluation.postgres.business_change.io_saturation.PgBusinessChangeIoSaturationForVacuumReportIoVictimSimpleEvaluatorCase`
- 校准按 Case 对照实时参考工作负载测量；工具命中台账与 rho 值由 Case 注册表和[难度标准](../../../../standards/scenario/difficulty.standard.md)维护，本契约不再复述。
### `archive_backlog_io_pressure`

- Case 编号：`2`
- 标题：由 WAL 归档槽停滞（而非报表 SQL 退化）引起的 I/O 打满告警。
- Alert/symptom: [FIRING: WARNING] alertname=PostgresDiskIOLatencyHigh service=checkout-writes instance=postgresql-primary severity=warning summary=Database write latency and report latency rose while disk I/O stayed elevated description=Recent dashboards show several report samples and checkout writes slower than normal, but the WAL/archive panel also shows unusual backlog growth. Determine whether the visible slow SQL is the root cause or a victim of WAL retention/archive pressure, then clear the backlog safely without changing report SQL.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`alert`、`fault_mechanism`、`status`、`table`、`visible_symptom`
- 期望目标字段：`maintenance_sessions`、`root_cause`、`status`、`table`
- 背景画像：未声明
- 评估器：`src.scenarios.evaluation.postgres.business_change.io_saturation.PgBusinessChangeIoSaturationForArchiveBacklogIoPressureEvaluatorCase`

## 4. Agent 可见的证据

- Agent 接收注册的告警，并在运行时暴露的范围内通过当前工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`。
- 告警只是定位提示，而不是根因答案。确切的证据、干扰项、可见性限制以及任何知识或历史观测工具，都必须在场景与评估器源代码中核实。
- 不要把参考报告、注入器证据、评估器自有的观测或隐藏的条件 ID 当作 Agent 可见的证据。

## 5. DP / OP / SP 契约

- **DP** 是注册 Case 的评估器自有语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
- **OP** 是评估器的终态与业务事实契约。上文的期望目标字段界定了状态边界；被接受的修复与等价结果由评估器定义。
- **SP** 独立检查危险操作、影响范围、受保护对象以及未经授权的状态漂移。它不是 OP 的替代品。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从遗留文档复制历史评分公式。

### 维护与报表的复合故障 Case

`vacuum_report_io_victim_simple` 中，后台维护 I/O 压力与 `report_reader` 的 work_mem
回归都是有意设计的故障。OP 要求维护及受害者会话退出、报表数据可查询、健康调度作业保持新鲜心跳，
同时保留以下配置不变量：

- `report_reader` 认证连接到当前数据库后的新会话必须满足 `work_mem >= 8MB`，并执行两条原始报表
  SQL。配置优先级由 PostgreSQL 决定；仅在 Agent 会话执行 `SET` 不算修复。其他数据库的低配置
  不影响当前业务验收。复位故障的本库覆盖，或在本库设置足够的值，都是有效修复。
- 当前数据库保存的 work_mem 不低于 `32MB`，初始值为 `64MB`。
- 健康角色 `bi_viewer` 保存的角色级 work_mem 不低于 `16MB`，初始值为 `32MB`。该角色在当前库
  若有覆盖，也必须达到下限；允许同时存在多条健康配置。其他库的覆盖不参与此检查。`bi_viewer`
  是 `NOLOGIN`，因此检查其保存的配置，不把它描述为业务登录回放。

配置值由 PostgreSQL 在隔离、仅回滚的评估会话中规范化。无单位 work_mem 数值使用 PostgreSQL
的 kB 单位，例如 `32768` 表示 `32MB`。维护停止后，受害者运行门控也读取新报表登录的配置，
避免修复前的旧会话保留低值而使 Case 无法结束。这些检查保留现有 OP 不变量，不新增 SP 限制，
也不在告警中直接提示根因。

## 6. 修复、归属与恢复

- 使用当前评估器和场景契约接受的修复族。操作顺序、SQL 写法、索引名称和报告措辞都不是硬性要求，除非代码明确将其纳入公共契约。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前的五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置和数据库状态。

## 7. 代码地图与验证

- 场景与 Case 源码：`src.scenarios.postgres.business_change.io_saturation.PgBusinessChangeIoSaturationScenario`
- 评估器源码：`src/scenarios/evaluation/postgres/business_change/` 下的一个或多个模块；确切的类已在上方逐 Case 列出。
- 入口：`examples/run_pg_business_change_io_saturation_scenario.py`
- 聚焦测试、参考运行和轨迹是证据，而不是第二份契约。
- 作用域、单位、登录与受害者退出回归：`tests/postgres/test_io_saturation_work_mem_scope.py`；
  真实 PostgreSQL 验证需设置 `DBA_BENCH_LIVE_IO_SCOPE=1`。
- 复合 Case 保留注册表校准（`hard`，D=6，C=0.565）：故障、诊断路径与 Agent 可见证据未变。
  当前公开仓库不含可同步的 Results Catalog；修复等价性的定向验证不构成一次新难度校准。
- 在修改本文档之前，请将其与当前注册表、Case 实现、评估器、聚焦测试和实际验证证据进行比对。
