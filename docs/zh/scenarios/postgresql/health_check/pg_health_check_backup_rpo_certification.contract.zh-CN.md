---
doc_id: scenario.postgresql.pg_health_check_backup_rpo_certification
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, health_check, pg_health_check_backup_rpo_certification]
summary: pg_health_check_backup_rpo_certification 的当前代码背书契约快照；包含其注册的 Case、状态边界、评估器身份与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_health_check_backup_rpo_certification`

> 本文件是当前由注册表支撑的场景契约。请先阅读数据库目录进行导航，并在修改实现之前，于链接的源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`health_check`
- 场景实现：`src.scenarios.postgres.health_check.backup_rpo_certification.PgHealthCheckBackupRpoCertificationScenario`
- 正式入口：`examples/run_pg_health_check_backup_rpo_certification_scenario.py`
- 当前描述：通过在隐藏业务标记处的隔离 PITR，认证真实的 PostgreSQL 基础备份与归档链。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `throughput_gap` | 带真实归档吞吐缺口和隐藏目标标记的困难版 RPO 认证。 | `hard` |
| 1 | `throughput_gap_simple` | 带一个有界归档延迟窗口和更少标记的简单版 RPO 认证；诊断必须定位归档停滞窗口，而认证操作手册保持端到端。 | `hard` |

上表是当前的代码快照。缺失的校准是显式的，不得从未注册的标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公共状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 和评估器实现所有；本文档不编造代码中不存在的值。

### `throughput_gap`

- Case 编号：`0`
- 标题：带真实归档吞吐缺口和隐藏目标标记的困难版 RPO 认证。
- Alert/symptom: [Scheduled PostgreSQL DR Certification] Certify the last 12 hours of recovery capability against the approved 60-second RPO. Use bounded historical metrics and operation events, verify the physical backup and archive continuity, and perform an isolated point-in-time restore at the evaluator-selected business marker. Refuse certification and report the last recoverable boundary when the chain cannot support the target.
- 初始状态字段：`backup_toolchain`、`rpo_seconds`、`status`、`topology`
- 期望目标字段：`manifest`、`marker_checksum`、`pitr`、`status`
- 背景画像：`rpo_history_probe`；Hard Case 冻结公共的 WAL 生成、归档投递、归档积压、业务提交、OLTP 服务和备份进度历史，并附三个候选低谷窗口，它们以相同的深度、时长和指标特征重放被掩埋目标捕获自身的通道形态：`missing_precursor` 把 WAL 通道压平到事发前状态（投递崩塌与积压爬升背后没有生成突发）、`scrambled_order` 以打乱顺序因果关系的方式重放相同取值（投递持续崩塌的同时积压再次回落）、`shadow_copy` 在指标上与事故窗口完全一致，只携带貌似合理但不完整的 `archive_attempt` 记录（剥离了段、校验和与关联标识，没有业务标记连续性）。总览与中等粒度统计无法把这些低谷与被掩埋的事故窗口区分开；只有操作事件证据以及“wal 突发 -> 投递停滞 -> 积压爬升”的有序因果链可以。停滞特征只存在于被掩埋的目标窗口之内：目标捕获之后，环境在物理上解除归档拥塞，运行还捕获了真实的 180 秒事后恢复（积压排空），因此冻结尾部回到正常状态而不是维持平台期。事后清理只解除拥塞：事故响应把 `archive_command` 降级为应急传输层（一个限速的归档中继，能跟上空闲段的节奏但撑不住认证重放），而这一残留没有在事后负载下引发任何当前状态指标异常。`oltp_service` 是对 `pgbench_accounts` 的真实有界探测，而不是就绪性 `SELECT 1`。
- 难度：hard；逐 Case 校准值由代码注册表和场景目录维护；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。
- 评估器：`src.scenarios.evaluation.postgres.health_check.backup_rpo_certification.PgHealthCheckBackupRpoCertificationEvaluatorCase`
- 总览：RPO 环境对不带窗口的 `query_metrics` 调用提供完整的粗粒度冻结总览网格（12 小时历史按 480 秒总览步长约为 90 个点），而不受显式 limit 的影响；共享的“最新 20 个点”总览预算不适用于该目录。装配器锚定目标窗口，使恰好一个总览网格点落入其后半段；每个候选低谷也被放置成恰好一个网格点落入其自身跨度，因此每个低谷都作为粗粒度候选与被掩埋的目标同台竞争。有界窗口（每个最多 900 秒）保留完整的基础网格，因此预期的漏斗是：总览候选（480 秒）-> 逐候选的基础网格确认与操作事件证据（2 秒）-> 以记录加因果链的方式排除同形低谷。
- DP：适用且确定（精确匹配器，无 LLM 裁判）。诊断必须陈述三个条件：定位到的归档投递停滞窗口、吞吐缺口根因（WAL 持续生成期间归档投递落后或停滞），以及 RPO 违约影响（可恢复点被推到超出批准的 60 秒 RPO，包括公共的 `rpo_not_met` 恢复结果）。定位到的 UTC 窗口从诊断条件的自由文本证据中读取（即 agent 自己的措辞，没有专用报告字段）：窗口可以是两个完整的 UTC 时间戳，或一个完整时间戳加一个同日结束时间（接受 `2026-09-15 14:39:00-14:54:00`、`to`/`until` 写法、ISO `T`/`Z`/`+00:00`）；当它与冻结历史的目标窗口重叠至少 60 秒（即批准的 RPO）且保持在公共 900 秒有界查询预算内时被接受；缺失、无法解析、不重叠或超大的窗口都会使窗口条件不满足（`DiagnosisPass=False`）。未回溯到冻结停滞事件窗口的尾部/持续平台期窗口同样无法满足该条件。所有窗口角色都保持在评估器内部。
- OP：纯端到端。上述可信的清单/库存/隔离 PITR 不变量必须在真实环境的终态上全部成立，且 `recover_archive` 还必须通过认证容量重放：恢复过程通过实时归档路由重放一次声明的 WAL 突发（8 个段），要求每个段都在 15 秒发布包络内持久化，因此在把残留应急路由重新指向发布层（由冻结的事发前操作事件记录 `details.route` 暴露）之前，恢复在物理上会失败。评估器不会解析提交报告中的窗口或认证文本。
- 难度标签与逐 Case 校准值由代码注册表和场景目录维护；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约刻意不重复这些实测值。

### `throughput_gap_simple`

- Case 编号：`1`
- 标题：带隔离业务恢复的简单版历史 RPO 认证。
- Alert/symptom: [Scheduled PostgreSQL DR Certification] Validate the selected recovery target using bounded historical observations, the physical backup, archive inventory, and an isolated restore. Certify only after the marker boundary and checksum are verified. First read metric overviews without timestamps, then drill into a single bounded evidence window; never request the full 6-hour history. HARD TOOL BOUNDARIES: each historical metric/log window must be <=900 seconds; use only wal_generation, archive_delivery, archive_backlog, business_commits, oltp_service, backup_progress; use logical targets archive_repository, backup_repository, and evaluator_selected, never container filesystem paths.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`backup_toolchain`、`rpo_seconds`、`status`、`topology`
- 期望目标字段：`manifest`、`marker_checksum`、`pitr`、`status`
- 背景画像：`rpo_history_probe`；Simple Case 使用更短的公共冻结历史契约（6 小时），带有四个干扰项：`simple-wal-burst-window`（捕获的良性 WAL 突发窗口）、`simple-backup-window`（仅指标的备份进度尖峰）、`simple-archive-retry-window`（仅指标的归档投递失败增量尖峰，无积压传播）和 `simple-delivery-quiet-window`（捕获的良性归档投递安静段，可自行恢复且无积压增长）。Simple 历史还在停滞窗口之后立即捕获了真实的 240 秒事后段：装配后的时间线以物理捕获的 archiver 追平（投递追平、积压排空）结束停滞特征，并在剩余尾部回到正常状态，因此故障特征只存在于目标窗口之内；尾部查询不再能复现它。总览保持粗粒度（300 秒步长）。冻结历史还携带标准归档路由绑定，作为正常捕获中每 20 秒公布一次的 `repository_sync/route_config` 操作事件，但 Simple 历史只在事发前条带中发布这些记录：目标窗口之前 480 秒内的装配正常块（与该条带不相交的查询窗口观测到零条 route-config 记录，因此物理恢复标准层必须先定位事故邻域；原先“重放到每个正常块”的保证是信息泄露，而不是可解性保证）；实时实例状态从不公布路由值，因此冻结历史的事发前条带是唯一携带健康层的表面。在事故收尾时（事后捕获之后、agent 阶段之前），归档路由保持绑定在一个应急传输包装器上，其命令与标准命令没有任何公共子串，其自包含脚本也从不引用标准包装器；在空闲的 agent 阶段负载下，其逐段限速对指标不可见，且 `recover_archive` 容量重放按标准投递层接受，评估器侧的接受窗口从不公布。
- DP（仅 Simple）：`diagnosis_applicable=True`，三个关键条件由精确匹配器匹配——`archive_stall_window_located`、`archive_delivery_throughput_root_cause` 和 `rpo_promise_violated_in_stall_window`。定位窗口条件针对运行时状态中保存的可信冻结停滞窗口进行确定性验证：诊断证据必须引用一个 `<UTC start>/<UTC end>` 窗口（多格式解析），它与停滞窗口重叠至少 60 秒（评估器侧接受区间，不公布），且跨度不超过声明的 `max_history_query_seconds` 预算。等价的窗口族全部通过；窗口可以在任一提交条件的证据中引用；解析失败或未覆盖的窗口会使定位窗口条件失败。可信停滞窗口从不通过公共工具披露。
- 评估器：`src.scenarios.evaluation.postgres.health_check.backup_rpo_certification.PgHealthCheckBackupRpoCertificationSimpleEvaluatorCase`，使用共享的 `RpoCertificationOutcomeVerifier`（11 项可信物理工件检查）；`pitr_restore` 保留其原有动作语义，并从内部隐藏标记推导恢复目标。

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

- 场景与 Case 源码：`src.scenarios.postgres.health_check.backup_rpo_certification.PgHealthCheckBackupRpoCertificationScenario`
- 评估器源码：`src/scenarios/evaluation/postgres/health_check/` 下的一个或多个模块；确切的类已在上方逐 Case 列出。
- 入口：`examples/run_pg_health_check_backup_rpo_certification_scenario.py`
- 聚焦测试、参考运行和轨迹是证据，而不是第二份契约。
- 在修改本文档之前，请将其与当前注册表、Case 实现、评估器、聚焦测试和实际验证证据进行比对。
