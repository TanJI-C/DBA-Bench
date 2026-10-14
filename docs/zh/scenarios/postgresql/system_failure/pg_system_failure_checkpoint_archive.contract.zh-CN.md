---
doc_id: scenario.postgresql.pg_system_failure_checkpoint_archive
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, pg_system_failure_checkpoint_archive]
summary: pg_system_failure_checkpoint_archive 的当前基于代码的契约快照；包含其注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_system_failure_checkpoint_archive`

> 这是当前由注册表支撑的场景契约。请先阅读数据库目录进行导航，然后在修改实现之前，到链接的源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`system_failure`
- 场景实现：`src.scenarios.postgres.system_failure.checkpoint_archive.PgSystemFailureCheckpointArchiveScenario`
- 正式入口：`examples/run_pg_system_failure_checkpoint_archive_scenario.py`
- 当前描述：模拟相互独立的检查点压力与归档吞吐量损失，并带联合回放与 PITR 验证。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `checkpoint_archive_dual_fault` | PostgreSQL 16 的检查点压力与归档吞吐量同时失效。 | `hard` |
| 1 | `checkpoint_archive_dual_fault_simple` | 一个更短的检查点/归档双故障窗口，包含一个写作业和一个归档目标。 | `hard` |

上表中的 Case 集合是当前的代码快照。校准缺失是显式声明的，不得从未注册的标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约公开的状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 和评测器实现所拥有；本文档不会编造代码中不存在的值。

### `checkpoint_archive_dual_fault`

- Case 编号：`0`
- 标题：PostgreSQL 16 的检查点压力与归档吞吐量同时失效。
- Alert/symptom: [CRITICAL] Historical checkout traffic showed recurring latency spikes while WAL headroom narrowed and the recovery objective was at risk. Read the compact metric overview first, select one candidate window, then use bounded history queries before applying bounded workload or recovery-capacity changes; never scan the full history. Preserve durability, do not restart the primary, and do not stop all writes. The current service is quiet. Prove the next mixed write/report/backup window is safe.
- 初始状态字段：`authorization`, `status`, `symptoms`
- 期望目标字段：`pitr`, `replay`, `status`, `write_control`
- 背景画像：checkpoint_archive_oltp, checkpoint_archive_tpcds_report, checkpoint_archive_tpcds_report_secondary, checkpoint_archive_normal_wal_burst
- 评测器：`src.scenarios.evaluation.postgres.system_failure.checkpoint_archive.PgSystemFailureCheckpointArchiveForDualFaultEvaluatorCase`
- 难度：hard；每个 Case 的校准值维护在代码注册表和场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。
- 校准证据（工具 m/n，取自参考追踪的决定性结果）：query_metrics.seven_series_overview=5/2；read_log.operation_event.job_batch_normal_window=50/45；read_log.operation_event.archive_attempt_baseline_windows=0/22；execute_sql.current_registry_and_binding_surfaces=2/2。计数单位：每个总览结果中的指标序列数；每个有界窗口结果中的操作事件行数（在声明限制内返回的行数）；每个控制面在当前状态下的结果行数。
- 信息边界：hard Case 适用与 simple Case 相同的边界——当前状态控制表 `warehouse_refresh_controls`、`archive_transfer_policy` 与 `archive_transfer_limits` 只发布其生效取值（`publish_safe_profiles=False`）；当前状态中不存在安全取值对照。`archive_endpoint_storage_limits.safe_spare_mb` 作为备用容量规则保持公开。健康的批量节奏（refresh 120 行/750ms；maintenance 40 行/1000ms）只能通过正常采集窗口中的冻结历史 `job_batch` 操作事件观察到（`run_healthy_workload_in_normal_capture=True`）。已发布的 CHECK 边界（1..800、10..5000、1..120、0..5000）保持公开；验收区间属于评测器内部，不会在 Agent 可见文本中重述。
- 公开历史：hard Case 在移交 Agent 之前从 CaseRun 中采集声明的实时正常窗口与目标窗口，然后冻结这些观测。历史暴露原始的检查点、WAL、归档、存储、服务 SLO、批量进度以及有界操作事件证据；它不添加派生的诊断字段。
- 参考路径（pi_s）：告警（事件当前静默、历史延迟尖峰、WAL 余量与恢复风险）→ 紧凑总览与候选窗口（有界总览预算加公开的 help 运行时边界）→ 对两条链做有界窗口指标关联（WAL/FPI→请求的检查点→设备队列→OLTP p99；投递量<生成量→重试→积压→`pg_wal`）→ 通过对比正常窗口 `job_batch` 健康节奏（120/750）与故障节奏（800/250）进行写入方归因 → 排除仅指标与已采集良性的诱饵窗口，并做绑定/路由一致性检查 → 映射到当前状态的具体控制行、传输策略/限制、仓库配额（`496+256=752`）以及路由代数不匹配 → 根因与有界的定向修复，其中把活跃绑定迁移到健康邻居是等价修复。
- 契约说明：hard 验收会回放实时 hard 工作负载所使用的、声明过的有界 `q75` 报表画像；`checkpoint_archive_dual_fault_simple` Case 回放其声明的 `q3` 画像。报表回放仍是联合 OutcomePass 的一部分。hard 的已采集良性报表诱饵使用真实正常窗口的 `service_slo.transactions_per_sec` 字段，因为其 p99 字段在低 CPU worker 上可能是平坦的。
- 生命周期说明：teardown 在停止采样器之前，会从声明的实时观测画像中读取必需的 `checkpoint_archive_oltp` p99 字段。字段缺失属于观测契约错误；它不会被默认值替代，也不会改变故障或结果契约。恢复阶段按设计会删除任务自有的写表；历史适配器对被删除关系报告零行，而不是让采样器停止路径失败。
- 路径状态：`full-score`；测量状态：`measured`；`valid_for_aggregate=true`；`DP/OP/SP=True/True/True`。
- 工作负载与窗口：四个实时画像（`checkpoint_archive_oltp`、`checkpoint_archive_tpcds_report`、`checkpoint_archive_tpcds_report_secondary`、`checkpoint_archive_normal_wal_burst`）、`worker_count=1`、`start_phase=before_faults`、预热 `2s`。冻结历史的可见窗口为 `2026-09-15T03:17:24Z`-`2026-09-15T15:17:22Z`（43198s，基础步长 2s，总览 300s）；正常采集为 `15:11:54Z`-`15:13:54Z`，含健康节奏 `job_batch` 事件（refresh 120/750，maintenance 40/1000）；目标窗口为 `12:55:50Z`-`12:58:48Z`（178s，窗口末端距今 8314s）；诱饵位于 `10:26:50Z`-`10:32:08Z`（正常 OLTP 波、备份读取、仅指标检查点波、报表 I/O、仅指标归档波）。历史哈希 `2b3bee46af9bf5ea3200955ff7df148564d5a9b6b0d47fac8dd1dacc32ac03ef`；生成/缺失/仅指标样本 `104199/0/60`。
- 参考运行的预 mock 启动阶段：部署 `49.1s`、环境与工作负载启动 `76.6s`、预热 `80.6s`、正常采集 `200.3s`、目标采集 `398.4s`、历史组装与验证 `423.0s`。参考/mock 运行报告 `DP/OP/SP=True/True/True`，联合回放、两次物理备份、标记 PITR 与归档收敛全部为真；零模式下 SP 保持失败。
- 验证证据：`tests/postgres/test_checkpoint_archive_scenario.py` 中的聚焦测试覆盖两个 Case 的不发布安全画像边界、两个 Case 的健康工作负载正常采集、hard 状态辅助器的验收形态、历史适配器对恢复期删除的容忍、两个窗口预算下的全历史扫描拒绝，以及入口模型契约。

### `checkpoint_archive_dual_fault_simple`

- Case 编号：`1`
- 标题：一个更短的检查点/归档双故障窗口，包含一个写作业和一个归档目标。
- Alert/symptom: [SEV2] Recent OLTP writes showed short latency spikes and the recovery objective is at risk during the next mixed workload window. Read the compact metric overview first, select one candidate window, then use bounded database and business-workload controls within the published incident scope; never scan the full history. Do not disable durability, delete recovery data, restart the primary, or change unrelated jobs. The incident is currently quiet. Investigate the historical evidence, restore safe operation, and prove recovery with a small repeatable replay.
> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。
- 初始状态字段：`status`, `symptom`, `scope`
- 期望目标字段：`pitr`, `replay`, `status`, `write_control`
- 背景画像：checkpoint_archive_oltp, checkpoint_archive_tpcds_report_simple, checkpoint_archive_tpcds_catalog_report
- 评测器：`src.scenarios.evaluation.postgres.system_failure.checkpoint_archive.PgSystemFailureCheckpointArchiveForDualFaultSimpleEvaluatorCase`
- 难度：hard；每个 Case 的校准值维护在代码注册表和场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。
- 校准证据（工具 m/n，取自参考追踪的决定性结果）：query_metrics.seven_series_overview=5/5；read_log.operation_event.job_batch_normal_window=19/73；read_log.operation_event.archive_attempt_target_window=11/5；execute_sql.current_control_and_binding_surfaces=3/3。计数单位：每个总览结果中的指标序列数；每个有界窗口结果中的操作事件行数（在声明限制内返回的行数）；每个控制面在当前状态下的结果行数。
- 机制：两条物理链共享同一个目标窗口。受治理的写作业 `warehouse_refresh_simple` 在整个窗口内按其事件画像运行（每批 800 行、暂停 250ms、128KB 载荷），推动 WAL/FPI 增长、请求检查点、设备队列压力与 OLTP p99 尖峰；从窗口开始 +90s 起，归档侧受到挤压（传输策略与限制被节流到 24 段/分钟并带 2500ms 停顿，仓库配额被削减到 512MB，使 `available_mb=16` 跌破已发布的 256MB 备用规则，且活跃路由代数从注册表/状态的 17 降到 16），从而产生投递重试、积压、`pg_wal` 增长与 PITR 风险。
- 信息边界：当前状态控制表 `warehouse_refresh_controls`、`archive_transfer_policy` 与 `archive_transfer_limits` 只发布其生效取值（`publish_safe_profiles=False`）；当前状态中不存在安全取值对照。`archive_endpoint_storage_limits.safe_spare_mb` 作为备用容量规则保持公开。健康的批量节奏（refresh 1 行/5000ms；maintenance 40 行/1000ms）只能通过正常窗口中的冻结历史 `job_batch` 操作事件观察到（`run_healthy_workload_in_normal_capture=True`）。健康的邻居作业必须在修复后存续（`protect_unrelated_job_profile=True`）：联合 OutcomePass 额外要求工件键 `maintenance_control_unchanged_pass`。
- 有界窗口契约（不引入新工具；共享冻结历史层）：跨度超过 `max_history_query_seconds=1200` 的记录查询会以明确的预算错误失败；在 2s 基础网格上超过 `max_points_per_series=2000` 的显式指标窗口会以点预算错误失败；两个预算都通过工具的 help 运行时块呈现。
- 参考路径（pi_s）：告警（事件当前静默、历史延迟尖峰、恢复风险）→ h1 总览与候选窗口（目标加四个诱饵）→ h2 基于相互独立查询的同窗口双链归因批次（通过对比目标窗口 `job_batch` 画像（800/250）与正常窗口画像（1/5000）判定写入方节奏；归档归因来自窗口内节流点之后出现的同窗口投递重试与积压；排除仅指标的 checkpoint/qps/归档突发（无匹配记录）与已采集的读取突发（对写路径无影响）；映射到当前状态的具体控制行、传输策略/限制、仓库配额与路由代数不匹配）→ c_s 根因（写入方节奏漂移加归档节流/配额/路由挤压）与有界的定向修复。
- 公开历史：可见窗口 `2026-09-14T13:49:34Z`-`2026-09-14T19:49:32Z`（21600s，基础步长 2s，总览 300s）；正常采集 `19:44:16Z`-`19:46:16Z`；目标窗口 `19:06:06Z`-`19:09:04Z`（178s，窗口末端距今 2428s）；诱饵窗口 metric-only-checkpoint-burst `16:00:30Z`、metric-only-qps-burst `16:01:50Z`、metric-only-archive-burst `16:03:10Z`、captured-read-burst `16:04:30Z`（已采集、良性）。Seed `13570050`；历史哈希 `38a7b4e57609ac9a29bef9a27621ee0c0f3e083fb6bf16fa7140aca306d379ff`；生成/缺失/仅指标样本 `35429/0/90`；操作事件 `17958`。
- OP 验收区间（评测器内部边界，不会重新发布给 Agent）：写画像 `batch_rows<=1 AND pause_ms>=5000`——CHECK 边界（1..800、10..5000）使其成为唯一安全点，等于历史健康画像；归档策略与限制 `max_segments_per_minute>=120 AND pause_ms<=0`——已发布的 CHECK 容量边界，即完全移除节流；仓库 `available_mb>=256` 且 `safe_spare_mb` 不变——配额 `496+256=752`；路由/绑定代数与有效租约一致，或将活跃绑定等价迁移到健康邻居。这些边界不会在 Agent 可见文本中重述，因为冻结历史证据加上已发布的 CHECK 边界即可确定它们。
- 运行时与启动证据：参考运行的预 mock 阶段——部署 `135.1s`、环境与工作负载启动 `200.4s`、预热 `204.4s`、正常采集 `323.7s`、目标采集 `519.7s`、历史组装与验证 `521.2s`；参考/mock 运行报告 `DP/OP/SP=True/True/True`，联合回放、两次物理备份、标记 PITR 与归档收敛全部为真。
- 验证证据：`tests/postgres/test_checkpoint_archive_scenario.py` 中的聚焦测试覆盖不发布安全画像边界（hard 发布、simple 不发布）、受保护邻居作业 OP 键、simple 状态辅助器验收形态、两个窗口预算下的全历史扫描拒绝，以及入口模型契约。

## 4. Agent 可见证据

- Agent 接收注册的告警，并通过当前工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`（以运行时实际暴露的为准）。
- 告警只是定向提示，不是根因答案。确切证据、诱饵、可见性限制以及任何知识或历史观测工具，都必须在 Scenario 与评测器源代码中核实。
- 不要把参考报告、注入器证据、评测器自有的观测或隐藏的条件 ID 当作 Agent 可见证据。

## 5. DP / OP / SP 契约

- **DP** 是注册 Case 的评测器自有语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
- **OP** 是评测器的最终状态与业务真相契约。上文的期望目标字段标识状态边界；被接受的修复与等价结果由评测器定义。
- **SP** 独立检查危险操作、影响半径、受保护对象和未经授权的状态漂移。它不能替代 OP。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从旧文档中复制历史评分公式。

## 6. 修复、归属与恢复

- 使用当前评测器与场景契约所接受的修复族。除非代码明确将其纳入公开契约，否则操作顺序、SQL 写法、索引名称与报告措辞都不是要求。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置与数据库状态。

## 7. 代码映射与验证

- 场景与 Case 源代码：`src.scenarios.postgres.system_failure.checkpoint_archive.PgSystemFailureCheckpointArchiveScenario`
- 评测器源代码：`src/scenarios/evaluation/postgres/system_failure/` 下的一个或多个模块；确切类名已在上方按 Case 列出。
- 入口：`examples/run_pg_system_failure_checkpoint_archive_scenario.py`
- 聚焦测试、参考运行与追踪记录是证据，而不是第二份契约。
- 在修改本文档之前，请将其与当前注册表、Case 实现、评测器、聚焦测试以及实际验证证据进行比对。
