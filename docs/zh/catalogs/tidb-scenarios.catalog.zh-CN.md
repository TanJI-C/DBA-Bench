---
doc_id: catalog.tidb-scenarios
doc_type: catalog
status: canonical
audience: [authoring, reviewer, maintainer, runtime_agent]
exposure: agent_safe
scope: [tidb]
summary: Catalogs the 62 formal TiDB v8.1 Scenarios, 124 registered Cases, five task categories, evidence boundary, implementation gates, and historical non-canonical candidates.
source_of_truth: code
related: [standard.evaluation.dp-op-sp, standard.scenario.difficulty, guide.scenario.implement-scenario-case]
language: zh-CN
---

# TiDB DBA Benchmark 正式场景规范（TiDB v8.1）

## 关键结论

本文件是 TiDB v8.1.0 固定基准下的正式场景目录。当前代码注册表包含 63 个注册项，其中 `basic=1` 是演示场景，不计入正式 benchmark 任务；其余 62 个正式 Scenario、124 个正式 ScenarioCase 分为 `query_perf=11`、`system_failure=14`、`health_check=11`、`business_change=13` 和 `resource_governance=13` 五类。Frozen History 是独立的正式 Scenario，必须进入 Scenario 和 Case 总数。正式条目的身份、入口和 Case 数以 `src.scenarios` 注册表为准；本目录只负责定位和说明，不替代具体合同。通用难度定义见 [场景难度设计原则](../../standards/scenario/difficulty.standard.md)，通用评估边界见 [DP、OP、SP 设计原则](../../standards/evaluation/dp-op-sp.standard.md)。场景严格归入以下五类：

1. `query_perf`
2. `system_failure`
3. `health_check`
4. `business_change`
5. `resource_governance`

任务材料来自固定的 TiDB 社区「监控与诊断」「管理与运维」栏目和 PingCAP 官方文档仓库快照，共纳入 136 篇可复现任务材料：60 篇故障闭环、51 篇社区日常运维闭环、25 篇官方 task/runbook。纯特性介绍、指标字典、FAQ 聚合页、未闭环问答和产品体验文章不计入。

正式分布为 `query_perf=11/22 Cases`、`system_failure=14/28 Cases`、`health_check=11/22 Cases`、`business_change=13/26 Cases`、`resource_governance=13/26 Cases`，合计 62 个 Scenario、124 个 ScenarioCase。

所有正式场景均已在项目固定 TiDB/TiKV/PD 及所需组件 `v8.1.0` lane 上验证相同因果机制、允许的 OP、业务真值或 SLO、组件最终状态和安全边界。各表中的 `D`/`C` 列对已完成正式校准的 Case 为 reference run 实测值，其余为设计目标值；实现与校准证据以各自 Scenario/Case 合同为准。

### 当前注册表 Case 快照

下面的 Case 集合直接来自 `src.scenarios.TIDB_SCENARIO_REGISTRY`。Frozen History 是独立正式
Scenario；`basic` demo 不计入正式任务。Case 语义、告警、初始状态、目标状态和 evaluator 仍须
继续阅读对应代码以及场景证据。快照直接标明代码侧校准状态；`uncalibrated` 不得从旧文档或
相邻 Case 推断为 `hard`。

| 类别 | Scenario ID | 当前 Case（`case_no:case_id [label]`） |
|---|---|---|
| `business_change` | `tidb_business_change_cdc_dc_migration` | `0:cdc_dc_migration_reverse_cutover [hard]`; |
| `business_change` | `tidb_business_change_dr_auto_sync_failover` | `0:planned_dual_dc_failover [hard]`; |
| `business_change` | `tidb_business_change_pitr_checkpoint_recovery` |  |
| `query_perf` | `tidb_query_perf_index_merge_selection_failure` | `0:dual_single_column_index_or_predicate [easy]`; |
| `query_perf` | `tidb_query_perf_index_order_correlation` | `0:object_listing_composite_index_correlation [hard]`; |
| `query_perf` | `tidb_query_perf_optimistic_write_conflict` | `0:settlement_retry_completion [hard]`; |
| `query_perf` | `tidb_query_perf_statistics_drift` | `0:distribution_shift_stale_statistics [hard]`; |
| `query_perf` | `tidb_query_perf_optimistic_write_conflict_frozen_history` |  |
| `query_perf` | `tidb_query_perf_statistics_drift_frozen_history` |  |
| `query_perf` | `tidb_query_perf_noncovering_index_tail_latency` | `0:noncovering_index_tail_latency [hard]`; |
| `query_perf` | `tidb_query_perf_case_when_in_cartesian_semi_join` | `0:case_when_in_cartesian_semi_join [hard]`; |
| `query_perf` | `tidb_query_perf_like_escape_range` | `0:literal_underscore_like_range [hard]`; |
| `system_failure` | `tidb_system_failure_lock_contention` | `0:admission_events_row_lock_deadlock [hard]`; |
| `system_failure` | `tidb_system_failure_pending_offline` |  |
| `system_failure` | `tidb_system_failure_mdl_blocking` | `0:long_transaction_mdl_blocks_online_ddl [easy]`; |
| `system_failure` | `tidb_system_failure_deadlock` | `0:wallet_pair_reverse_order_deadlock [hard]`; |
| `system_failure` | `tidb_system_failure_sf01` | `0:pd_mixed_disk_eviction [hard]`; |
| `system_failure` | `tidb_system_failure_sf02` | `0:slow_store_lock_ttl_commit_failure [hard]`; |
| `system_failure` | `tidb_system_failure_pd_metadata_recovery` |  |
| `system_failure` | `tidb_system_failure_br_permission` | `0:br_s3_credentials_denied [hard]`; |
| `system_failure` | `tidb_system_failure_clustered_index_consistency` |  |
| `system_failure` | `tidb_system_failure_gc_mvcc_recovery` |  |
| `resource_governance` | `tidb_resource_governance_ru_budget_calibration` | `0:mixed_oltp_olap_ru_budget_calibration [hard]`; |
| `resource_governance` | `tidb_resource_governance_runaway_query` | `0:runaway_query_protected_batch [hard]`; |
| `resource_governance` | `tidb_resource_governance_br_slo_adaptive_throttling` | `0:br_backup_frontend_slo [hard]`; |
| `resource_governance` | `tidb_resource_governance_ru_budget_calibration_frozen_history` |  |
| `resource_governance` | `tidb_resource_governance_br_slo_adaptive_throttling_frozen_history` |  |
| `resource_governance` | `tidb_resource_governance_placement_policy` | `0:compliance_table_zone_migration [hard]`; |
| `resource_governance` | `tidb_resource_governance_lightning_budget` | `0:lightning_import_budget [hard]`; |
| `resource_governance` | `tidb_resource_governance_lightning_budget_frozen_history` |  |
| `resource_governance` | `tidb_resource_governance_rg06` | `0:ticdc_checkpoint_sink_budget [hard]`; |
| `resource_governance` | `tidb_resource_governance_empty_region_merge_budget` | `0:empty_region_merge_budget [hard]`; |
| `resource_governance` | `tidb_resource_governance_connection_balancing` | `0:multi_tidb_connection_balance_and_drain [hard]`; |
| `resource_governance` | `tidb_resource_governance_pd_api_security` | `0:pd_api_access_hardening [hard]`; |
| `resource_governance` | `tidb_resource_governance_sql_binding` | `0:deterministic_or_binding_approval [hard]`; |
| `business_change` | `tidb_business_change_batched_dml_ddl` | `0:retention_archive_online_index [hard]`; |
| `health_check` | `tidb_health_check_gc_safepoint_pin` | `0:abandoned_changefeed_gc_safepoint_pin [hard]`; |
| `health_check` | `tidb_health_check_syncpoint_consistency` | `0:syncpoint_consistency_under_writes [hard]`; |
| `health_check` | `tidb_health_check_empty_region_leader_skew` | `0:regional_job_empty_region_skew_review [hard]`; |
| `health_check` | `tidb_health_check_empty_region_leader_skew_frozen_history` |  |
| `health_check` | `tidb_health_check_backup_recoverability` | `0:backup_chain_repair_and_restore [hard]`; |
| `health_check` | `tidb_health_check_placement_policy` | `0:single_store_voters_pending [hard]`; |
| `health_check` | `tidb_health_check_long_transaction_mvcc` | `0:daily_reconciliation_snapshot_transaction [hard]`; |
| `health_check` | `tidb_health_check_ticdc_replication_trend` | `0:ticdc_replication_capacity_review [hard]`; |
| `health_check` | `tidb_health_check_ticdc_replication_trend_frozen_history` |  |
| `health_check` | `tidb_health_check_lightning_preflight` | `0:lightning_preflight_admission_review [hard]`; |
| `health_check` | `tidb_health_check_auto_analyze_drift` | `0:auto_analyze_configuration_drift [hard]`; |
| `business_change` | `tidb_business_change_timezone_ddl_backpressure` |  |
| `system_failure` | `tidb_system_failure_ticdc_gc_safepoint` |  |
| `business_change` | `tidb_business_change_timezone_ddl_backpressure_frozen_history` |  |
| `system_failure` | `tidb_system_failure_region_unavailable` | `0:region_unavailable_pd_network_block [hard]`; |
| `system_failure` | `tidb_system_failure_table_cache_lease` | `0:table_cache_lease_write_conflict [hard]`; |
| `system_failure` | `tidb_system_failure_table_cache_lease_frozen_history` |  |
| `query_perf` | `tidb_query_perf_set_autocommit_storm` | `0:autocommit_storm_cpu_saturation [hard]`; |
| `query_perf` | `tidb_query_perf_set_autocommit_storm_frozen_history` |  |
| `business_change` | `tidb_business_change_rolling_upgrade` | `0:rolling_upgrade_6_5_to_7_5 [hard]`; |
| `business_change` | `tidb_business_change_large_table_batch_dml` | `0:large_table_batch_update_and_index [easy]`; |
| `business_change` | `tidb_business_change_lightning_checkpoint` | `0:lightning_checkpoint_scale_out [hard]`; |
| `business_change` | `tidb_business_change_dm_replace` | `0:failed_ddl_safe_replace [hard]`; |
| `business_change` | `tidb_business_change_table_recovery` | `0:dropped_table_gc_recovery [hard]`; |
| `business_change` | `tidb_business_change_x86_arm64_migration` | `0:offline_x86_to_arm64_online_migration [hard]`; |
| `business_change` | `tidb_business_change_online_ddl_pause_resume` | `0:paused_unique_index_backfill [hard]`; |
### 来源导航约定

场景表“主要来源”列中的 `Cxx`、`Oxx`、`Rxx` 是来源编号：`C` 是社区故障闭环，`O` 是社区日常运维闭环，`R` 是官方 task/runbook。实现新场景时不得只根据本文件的场景摘要编码；必须打开所有主要来源，核对原站和版本，再把实际采用的症状、诊断证据、机制、修复边界及验收条件记录进正式 `docs/scenarios/<database>/<category>/<scenario-id>.contract.md`。场景摘要与原文冲突时以交叉验证后的版本化事实为准。

## 1. 范围与分类边界

| 类别 | 本 benchmark 中的定义 | 典型 DP/OP/SP |
|---|---|---|
| `query_perf` | 已知业务 SQL 或 SQL 指纹发生性能退化，需要解释 TiDB 特有的执行、统计或存储引擎原因 | `True/True/True` |
| `system_failure` | 服务、事务、复制或存储已不可用，需要找出单一主要故障并恢复 | `True/True/True` |
| `health_check` | 主动巡检、容量检查、一致性检查或变更前检查，目标是发现风险并形成可信结论 | `None/True/True`；若明确要求诊断已存在异常才使用 DP |
| `business_change` | 升级、扩缩容、迁移、备份恢复、容灾切换、DDL/DML 等计划变更 | `None/True/True` |
| `resource_governance` | 在业务 SLO、安全或合规约束下分配 RU、并发、存储、拓扑和后台任务预算 | `None/True/True` |

备份、恢复、扩缩容等名词本身不决定分类。计划内恢复属于 `business_change`，多数副本丢失后的恢复属于 `system_failure`，恢复任务在前台 SLO 下的调速属于 `resource_governance`。安全加固和数据放置合规也归入 `resource_governance`，不新增第八类。

## 2. 来源纳入规则

### 2.1 故障文档

故障材料必须同时包含：具体表象、诊断证据、明确原因、可执行修复和结果验证。只有报错、原理说明或仍以“可能是”结束的帖子不计入。

### 2.2 非故障运维文档

无根因任务使用独立标准，不能因为没有“故障原因”而被排除：

1. 有具体运维目标，而不是介绍某个功能能做什么。
2. 给出环境、版本、业务窗口、RPO/RTO 或 SLO 等约束。
3. 给出可执行步骤或决策流程。
4. 明确安全边界、不可逆动作、回退条件或影响范围。
5. 有状态、性能、数据一致性或业务验收方法。

官方文档只有满足这五项时才作为主任务来源，例如升级、扩缩容、BR/PITR、Lightning precheck、DM 迁移和 TiCDC 一致性校验 runbook。参数参考和特性概览只用于机制核验。

## 3. 难度设计入口

`D_s`、`C_s`、`pi_s`、`K_s`、未过滤 `m/n`、采样窗口、workload、reference run ID 和
`Easy`/`Hard` 阈值统一见 [场景难度设计原则](../../standards/scenario/difficulty.standard.md)。TiDB
场景还使用以下四个对照象限指导选题：

### 3.1 四个对照象限

| 象限 | 用途 |
|---|---|
| 浅路径、低噪声 | 接口和 evaluator 校准 |
| 深路径、低噪声 | 隔离 TiDB 垂域知识检索能力 |
| 浅路径、高噪声 | 隔离时序筛选与窗口选择能力 |
| 深路径、高噪声 | 主挑战集 |

## 4. 指标历史路径与知识检索契约

### 4.1 指标历史路径

一个场景只有同时满足以下条件才标记为指标历史路径（M）：

- 参考路径中的多数关键状态主要由 `query_metrics` 的时序形态、标签关联或组件间先后关系支持；对 `D>2` 的深路径，至少三跳必须由时序证据支持，对浅路径则要求全部关键状态由时序证据支持。
- 日志和系统表只能确认实体或排除候选，不能一条记录直接泄漏根因。
- 关键指标以未过滤时间序列返回，包含真实前台、后台和组件噪声。
- Agent 必须选择时间窗、比较 target、关联多个 metric family；单点当前值不足以完成诊断。

指标历史路径不等于禁止 SQL 或日志。它要求主要因果证据来自时序数据，而不是人为隐藏所有其他观测。

### 4.2 知识检索路径

垂域知识场景必须提供 `search_knowledge(query, filters)`，知识库由固定版本的官方文档、已关闭 issue 和入选社区案例构建。Agent 不知道文档 ID，只能检索。benchmark 记录检索和引用，但不把“调用过知识库”设为 DP 条件；最终报告正确识别根因即可通过 DP。

为了避免题面泄漏，告警不得出现参数名、issue 标题或修复命令。场景需先用至少一个未接入知识库的强模型做污染基线：若仅凭题面即可稳定答对，必须增加真正的中间证据状态或淘汰，不能靠 evaluator 变严来制造难度。

## 5. 工作负载与观测噪声

每个高 `C` 场景从以下真实 profile 中组合至少三类，并固定随机种子和阶段：

| Profile | 真实行为 | 主要噪声 |
|---|---|---|
| `oltp_core` | sysbench 或场景专用 OLTP 读写事务 | QPS、事务延迟、锁、Raft 写入 |
| `olap_burst` | 场景专用 TiFlash 扫描与聚合 | CPU、内存、网络、coprocessor/MPP |
| `ddl_maintenance` | 加索引、ANALYZE、分区变更 | 扫描、backfill、统计任务、I/O |
| `backup_migration` | BR、Lightning、TiCDC/DM | snapshot、ingest、网络、GC safepoint |
| `topology_churn` | 合法的 leader/region 调度 | scheduler、snapshot、Region heartbeat |
| `host_noise` | 同机非数据库 CPU/I/O/内存压力 | cAdvisor/host 指标，不伪造数据库信号 |

噪声必须由真实进程产生，不能在 fault injector 中改写 live Prometheus 返回值。fault injector 只拥有故障状态，
workload runner 只拥有背景负载，恢复阶段分别清理，避免把“噪声”写进故障实现后无法归因。

对于明确标记为 `frozen-history` 的 TiDB Case，允许在 Agent 启动前由本次 run 的真实 normal/fault capture 构造一份
`procedural historical observation`：背景块来自真实 normal capture，target bundle 来自真实故障 capture，显式
decoy 的类型、窗口和允许变换写入 Case contract。该历史不是 Prometheus archive，也不宣称代表连续数小时真实运行；
timeline 构造完成后必须冻结并计算 hash，Agent 运行期间不追加或按查询改变结果。日志、TopSQL 和 slow query 记录与
target bundle 使用同一相对时间平移，查询受时间窗口和返回预算限制。

这项例外只改变 Agent 的历史观察数据面，不改变真实性边界：当前故障、修复后的状态、业务真值、配置、拓扑、锁和
安全检查仍读取真实 TiDB/Prometheus/SQL；evaluator 和 trusted observation 不读取 generated history。不得生成假的
INFORMATION_SCHEMA、拦截并重写任意 SQL、把 history 注入 Prometheus，或在失败后 fallback 到旧 archive；frozen-history
Case 的物理 TopSQL/slow-query 历史表必须由 public `execute_sql` 旁路保护；需要历史 SQL 时通过 `execute_sql(target="history")` 查询，组件日志通过已有 `read_log` 查询，物理历史表不对外暴露。trace 保存 seed、history hash、窗口角色和来源摘要用于审计，但 Agent response 不得泄漏这些内部字段。

## 6. 五类挑战场景

表中 `M` 表示指标历史路径，`K` 表示知识检索路径，`M+K` 表示两者都不可缺少。

### 6.1 `query_perf`

| ID | 正式场景 | 路径模式 | `D` | `C` | 主要来源 |
|---|---|---:|---:|---:|---|
| QP01 | 多查询族联合索引列序、状态前缀与版本相关性导致局部修复误判 | M+K | 6 | 0.91 | O47 |
| QP02 | 高冲突写模型使简单 DML 在乐观事务下退化 | M+K | 5 | 0.80 | O50 |
| QP03 | 窄时间窗口与同域 fingerprint 噪声下的复杂 `OR` 查询未启用 Index Merge 导致全表扫描 | K | 5 | 0.78 | O48 |
| QP04 | 数据分布突变后统计估算失真与计划漂移 | M+K | 3 | 0.65 | C08、R01 |
| QP05 | 非覆盖索引引发多余回表与长尾 | M+K | 3 | 0.60 | O47、O48 |
| QP06 | `CASE WHEN ... IN` 的 Cartesian semi join 性能退化 | K | 4 | 0.55 | C16 |
| QP07 | 字面下划线未转义导致 LIKE range 过宽 | M+K | 3 | 0.55 | O49 |

**QP01**：Agent 要关联 customer-list、tenant-admin-list 和版本化 policy lookup 三条真实访问路径，分别证明计划摘要、估算/实际行数、索引 leading prefix、状态过滤与列相关性。OP 的核心判定同时验证两类 catalog 查询、policy 版本 lookup、两类结果 truth 和双表 CRC；端到端延迟以 warmup 后多样本稳定性观测独立记录，不把单个外部抖动直接并入 OutcomePass。

**QP02**：Agent 要从 SQL 指纹、冲突 key、事务模式和提交重试定位热点写模型。OP 必须消除不必要竞争并恢复吞吐；无限提高重试次数或丢弃冲突更新不通过。

**QP03**：带 08:00-24:00 窄事件窗口和两个重复 branch-local 时间谓词的内层 `OR` 查询，再叠加外层 `DISTINCT`、API `ORDER BY event_id` 和 `LIMIT 512` 分页，在 Index Merge 关闭时为 `TableFullScan`，启用后必须形成使用 `idx_tenant_time` 与 `idx_type` 的双索引 `IndexMerge` 并完成 TopN 排序。数据中 `refund` 分支与目标 tenant 相关但不为空，背景 workload 另行产生同表同窗口的分页/去重/排序近邻 fingerprint、`amount`/payload 残余过滤、tenant/event-type 相似 fingerprint、重叠分支、集合谓词、边界/跨日窗口、主键范围、索引/表状态/变量观测和四个缺失对象的错误噪声，共 36 个真实 profile。Agent 必须先从相似 SQL 中选出正式嵌套目标，再排除只改变分页边界、排序列、去重、分支覆盖或残余过滤的近邻，以及统计和缺失 cache 等干扰，将计划、session/global scope、两个索引分支和 session-only 因果干预串起来。OP 验收计划、450 行结果、整表真值和索引目录均不变，不能用删数据、缩小业务谓词、改写成另一个查询、创建新索引或修改 global/session 外持久优化器状态制造加速。

**QP04**：确定性数据倾斜后，旧统计把 50,000 行误估为 10 行。Agent 必须用统计更新时间、估算/实际行数和计划选择证明因果；OP 执行 `ANALYZE` 后估算回到 50,000，实际业务结果不得变化。

**QP05**：查询从非覆盖索引 `IndexLookUp` 改为覆盖索引 `IndexReader`。OP 要同时验证 p95 `158.03→21.72 ms`、返回结果和 10 万行业务真值；只用 hint 固定错误索引不通过。

**QP06**：普通 `NOT IN` 已被 v8.1 的 Null-Aware anti semi join 修复，因此正式合同只保留标量 `CASE WHEN key IN (subquery)` 的 Cartesian left outer semi join。相关 `EXISTS` 改写后计划变为等值半连接，10,001×3,001 行 probe 从 `3.84 s` 降到 `17.6 ms`，命中数均为 1,500，NULL 行未被过滤；标题不再声称 OOM。

**QP07**：业务真值要求匹配字面 `_`，故障 SQL 却把 `_` 当单字符通配符。未转义 range 为 `[dir,dis)`、扫描 105 key/返回 5 行；转义后为精确前缀 range、扫描 2 key/返回 2 行并匹配字面 truth。OP 不能以保持故障 SQL 的错误结果集为目标。

### 6.2 `system_failure`

| ID | 场景 | 路径模式 | `D` | `C` | 主要来源 |
|---|---|---:|---:|---:|---|
| SF01 | PD 混部磁盘故障导致 Leader 切换与错误驱逐 | M+K | 5 | 0.85 | C09 |
| SF02 | 慢 Store 使锁 TTL 续期丢失并触发提交失败 | M+K | 6 | 0.949772 | C06、C26 |
| SF03 | 异常 async-commit lock 阻塞 resolve-lock 与 GC | K | 7 | 0.45 | C04 |
| SF04 | 同一 Region 多数副本永久丢失后的受控恢复 | K | 6 | 0.40 | C01、C27、C47 |
| SF05 | TiKV SST 文件损坏后的限定 peer 恢复 | K | 5 | 0.45 | C37 |
| SF06 | BR 对象存储凭据错误导致备份失败 | K | 3 | 0.40 | O39、R13 |
| SF07 | TiKV Pending Offline 因异常 peer/调度卡住 | M+K | 5 | 0.75 | C40、C42、C43 |
**SF01**：当前实现不是 PD 元数据全损恢复，而是混部节点的存储 `fsync` 尾延迟先拖慢 PD heartbeat/lease，随后发生 term/leader 变化，新 leader 错误地挂载 `evict-leader-scheduler`，把健康 TiKV 的 leader 数量驱逐到异常水平。Region 数量、三副本数据和 TiKV 进程仍完整，Agent 必须区分 leader placement 故障与 Region/data loss，修复或隔离真实存储故障、移除错误 scheduler，并完成受影响业务 reconciliation。focused Case 还要求在授权范围内补写一条审计事件、从 base aggregate 重建 derived controls；不得修改历史业务行、无关元数据或生成新集群。

**SF02**：Agent 要从三副本 Store 状态、业务 Region peer/leader、目标与同域事务历史、Store-scoped I/O tail、TiKV write/Raft/apply 日志和 3 秒 lock TTL 窗口，定位慢 Store 导致的 ordinary `TxnLockNotFound` 提交失败。OP 要求恢复确切 Store 的原始 I/O 配置、目标 settlement job 定向重试并提交，目标订单/job/ledger、三副本、业务 checksum 和五张 decoy 均通过；不能把普通 9007/锁等待或任意 8022 当成目标故障。`sf02_settlement_jobs.state` 的合法值是 `retry_required`、`settled`、`committed`，`sf02_settlement_ledger.state` 的合法值只有 `applied`，两列均由 `ENUM` 与同值域 `CHECK` 共同约束。

**SF03**：在线 DDL 被一个可定位的长事务持有 MDL 阻塞。OP 只结束精确 blocker，并验证同一 DDL job 完成、目标列 public、无关会话未被终止。

**SF04**：`DATA_LOCK_WAITS.KEY_INFO` 必须定位到目标表和 handle。OP 只回滚 holding transaction，使 waiter 提交并验证目标行最终金额；全局 kill 或重启实例不通过。

**SF05**：两事务以相反顺序锁定两个 key，真实返回 `ERROR 1213` 并写入 deadlock history。OP 按稳定主键顺序重试并提交两行，禁止通过跳过一笔业务更新消除死锁。

**SF06**：错误对象存储凭据必须稳定返回 `403 Forbidden`。Agent 必须从 BR 失败结果、备份历史、凭据 inventory、runtime binding 和源表真值中区分目标表备份故障、轮换传播滞后、历史任务噪声和业务数据异常。实现使用 220 个同 prefix 的重叠轮换 credential profile、244 条 runtime binding、60 条混合历史 job 和 28 个真实 ledger/backup/control-plane 业务 SQL profile；目标 scope 的唯一 `effective` binding 初始指向已退休 credential，活动生产 pair 只作为 canary 候选可见。正确的生产 pair 需要结合 scope、rotation/history/binding-state 证据，并先恢复精确的 production binding，再以真实 BR 结果验证。OP 必须同时满足 binding 指向活动生产 credential、BR 达到 `3/3 ranges`、`ranges-failed=0`、Checksum `100%`，生成包含 `backupmeta` 的对象，且源表 CRC 不变；修改源表或 credential inventory、批量修改 binding、把错误凭据替换为无关 bucket 或只验证命令退出码均不通过。

**SF07**：当前实现仍是 TiKV storage-topology scale-in 未收敛，不是后来设计稿中的 Online Unsafe Recovery。注入器在 3 PD/5 TiKV 上让目标 Store 进入 Offline/迁移状态，同时关闭或压低 `region-schedule-limit`、`replica-schedule-limit`、`max-pending-peer-count` 和 `enable-replace-offline-replica`，并保留真实 checkout/支付/审计/库存/区域观测噪声。Agent 必须定位目标业务 Region、容量 blocker 和 PD schedule 配置，完成目标 Store 的安全 Tombstone/Region 清空，保留至少 3 个 Up Store，恢复调度预算，并验证业务 count/sum/checksum 不变；禁止 force-delete、提前停目标组件、扩大影响范围或把旧 K13/Online Unsafe Recovery 规划当成当前 Case。

### 6.3 `health_check`

| ID | 正式场景 | 路径模式 | `D` | `C` | 主要来源 |
|---|---|---:|---:|---:|---|
| HC01 | 深度巡检发现废弃 changefeed 正在长期 pin GC | M+K | 4 | 0.80 | O01、C41、R01 |
| HC02 | 持续写入下的主备快照一致性审计 | M+K | 26 | 0.93 | O03、O25、R05 |
| HC03 | Empty Region 与 leader 偏斜容量健康检查 | M | 5 | 0.684211 | O44、O45、R01 |
| HC04 | 六段备份链修复、审批历史消歧与隔离恢复证明 | M+K | 10 | 0.95 | O15、O17、O18、R13、R14 |
| HC05 | TiCDC 复制链路日检与延迟容量趋势 | M | 5 | 0.990971 | C29、R05、R06 |
| HC06 | Lightning 上线前容量与兼容性预检 | M+K | 3 | 0.65 | R18、R19 |
| HC07 | 自动统计配置漂移与维护范围巡检 | K | 5 | 0.739159 | O01、R01 |
| HC08 | Placement policy 不可满足的合规巡检 | K | 3 | 0.55 | O28、R25 |
| HC09 | 长事务与 MVCC 版本风险巡检 | M+K | 3 | 0.55 | C14、C15 |

**HC01**：任务不是修复现有告警，而是在例行巡检中找出未来磁盘风险。报告必须把 GC safepoint 趋势、service safepoint owner、changefeed 进度和磁盘增长联系起来。OP 验证巡检报告覆盖风险、影响和建议；若任务授权清理，再验证 safepoint 推进。

**HC02**：主备持续写入，直接行数比较必然产生假差异；映射 TSO 内还存在两条 `order_items` 行级漂移。Agent 要先解析当前 release 的 queue/window/binding，再用 Syncpoint 对两张关联表完成 count、checksum、双向 diff 和 orphan/schema 校验，按 opaque fingerprint authorization 交给受控 repair worker 修复两个不同 row，重新审计并恢复临时 GC 配置。OP 是最终数据库状态满足完整一致性不变量，而不是“没有报错”或报告写了某个结论。

**HC03**：PD CPU 暂未告警，但三节点 Region 时序、长期 empty/zero-key 年龄、merge 速率和 persistent leader/store 离散度共同显示调度容量风险；短时 split、hot-store 和业务查询是高相似噪声。任务要求把结构化巡检结论和有边界的跨表整理计划写入 review row，不修改业务数据或重启健康组件。

**HC04**：已有备份任务显示成功，但批准的隔离恢复无法到达目标 checkpoint。当前 selected primary chain 同时包含 A3/A4/A5/A7/A8 五个可读但 checksum-invalid 的 active object，以及 A6 一个 bytes 可读但 `present=0`、`NOT_REPLICATED` 的 continuity gap。Agent 要关联 request、metadata、archive object、segment continuity、approval owner、checkpoint、checksum 和业务关键数据，修复六段并重新执行隔离恢复。DP 只判断是否识别这两个真实根因；OP 只验证六段最终可用、最新 restore attempt 成功、四张关键表及 sandbox 真值一致、production truth 不变。RPO/RTO 字段、恢复耗时、报告关键词、固定 action sequence 和隐藏 source ID 都不是 OutcomePass 条件；source role/mode/state/owner 是 Agent 可查询的业务约束。未发现根因时 run 应因真实状态未修复而失败；发现根因但选错副本、只修一段、没有重跑 restore 或恢复校验失败时，真实 OutcomePass 仍为 False。手工伪造审计/restore 表或在生产集群原地覆盖恢复仍属于 SP 失败。

**HC05**：TiCDC changefeed 当前状态为 Normal，但 checkpoint lag、sink throughput、error rate 和 GC headroom 在历史窗口与当前业务负载下可能恶化。当前实现同时限制 TiCDC 与下游 MySQL sink 的资源预算；下游事件表额外维护只存在于 sink 的 17 条写放大索引（连同 5 条基础索引共 22 条），用于形成真实的 sink-side 成本，不改变业务真值。Agent 要区分短时波动与持续问题，识别复合瓶颈并在已授权的在线维护窗口内执行必要的可逆处置。正式负载是 256 行批次、目标 `20.0 QPS`，sink 参数为 4 workers、`max-txn-row=1`；HC05 工具 profile 保留复制、工作负载、节点健康、SQL、日志和受控实例操作，但去掉无关的 PD/Region 管理接口；历史容量结果交错返回 commerce 与 warehouse 两条 delivery stream，要求 Agent 先按 `changefeed_id` 对齐证据。OP 只验证持续 source 写入下的复制 SLO、checkpoint 收敛、上下游 watermark 数据一致性和 GC 安全终态，不要求固定 review 表、固定报告措辞或某一个资源调整数值。正式 reference run 实测 `D=5`、`C=0.990971`（`m/n=37/4061`，Hard）；授权不包括停止业务流量、删除或改写业务数据、跳过交付事件、停止 changefeed、重启 TiDB/TiKV/PD 或改变集群拓扑。

**HC06**：Lightning 尚未启动时，Agent 要检查源文件不可变性、本地排序空间、TiKV 容量、权限、目标表状态、PITR/TiCDC 冲突与 checkpoint 持久化；目标非空时必须拒绝。

**HC07**：隔夜统计维护交接同时遗留全局 `tidb_enable_auto_analyze=OFF` 和订单表的表级统计锁；订单、支付两张表都追加数据，锁定时 `STATS_HEALTHY` 仍可能为 100，必须关联真实行数、`SHOW STATS_META`、`SHOW STATS_LOCKED` 与维护上下文。恢复全局 ON、只解锁并刷新已完成批量任务的订单表，保留仍 active 的支付 plan canary 锁和统计版本，最终校验双表业务 checksum 不变。实测 `D=5`、`m/n=31/231`、`C=0.739159`。

**HC08**：单 Store lane 绑定 `VOTERS=3` 后 placement 稳定为 `PENDING`。解绑不适用的表级 policy 后必须回到 `DEFAULT`、pending 消失、2,000 行 CRC 不变。

**HC09**：打开 snapshot transaction，在 `CLUSTER_TIDB_TRX` 中定位明确 session；并发完成 20 行新版本后结束该事务，目标 session 数变为 0，新写入和 CRC 均保留。

### 6.4 `business_change`

| ID | Case | 路径 | `D_s` | `C_s` | `m/n` | Mock DP/OP/SP | 主要来源 |
|---|---|---:|---:|---:|---:|---|---|
| BC01 | `rolling_upgrade_6_5_to_7_5` | K | 5 | 0.959142 | 40/939 | `N/A / True / True` | [BC01](../../scenarios/tidb/business_change/tidb_business_change_rolling_upgrade.contract.md) |
| BC02 | `cdc_dc_migration_reverse_cutover` | M+K | 7 | 0.869198 | 31/206 | `N/A / True / True` | [BC02](../../scenarios/tidb/business_change/tidb_business_change_cdc_dc_migration.contract.md) |
| BC03 | `batched_dml_ddl` | K | 6 | 0.759259 | 78/246 | `N/A / True / True` | [BC03](../../scenarios/tidb/business_change/tidb_business_change_batched_dml_ddl.contract.md) |
| BC04 | `large_table_batch_update_and_index` | M+K | 4 | 0.957831 | 7/159 | `N/A / True / True` | [BC04](../../scenarios/tidb/business_change/tidb_business_change_large_table_batch_dml.contract.md) |
| BC05 | `lightning_checkpoint_scale_out` | M | 6 | 0.989731 | 13/1253 | `N/A / True / True` | [BC05](../../scenarios/tidb/business_change/tidb_business_change_lightning_checkpoint.contract.md) |
| BC06 | `failed_ddl_safe_replace` | M+K | 9 | 0.677419 | 30/63 | `N/A / True / True` | [BC06](../../scenarios/tidb/business_change/tidb_business_change_dm_replace.contract.md) |
| BC07 | `dropped_table_gc_recovery` | K | 7 | 0.910072 | 50/506 | `N/A / True / True` | [BC07](../../scenarios/tidb/business_change/tidb_business_change_table_recovery.contract.md) |
| BC08 | `offline_x86_to_arm64_online_migration` | M+K | 6 | 0.949239 | 20/374 | `N/A / True / True` | [BC08](../../scenarios/tidb/business_change/tidb_business_change_x86_arm64_migration.contract.md) |
| BC09 | `paused_unique_index_backfill` | K | 6 | 0.966443 | 15/372 | `N/A / True / True` | [BC09](../../scenarios/tidb/business_change/tidb_business_change_online_ddl_pause_resume.contract.md) |
| BC10 | `dr_cutover_timezone_ddl_and_sink_backpressure` | M+K | 7 | 0.837563 | — | — | [BC10](../../scenarios/tidb/business_change/tidb_business_change_timezone_ddl_backpressure.contract.md) |
| BC11 | `timezone_ddl_backpressure_history_investigation` | M+K | 8 | 0.936733 | — | — | [BC11](../../scenarios/tidb/business_change/tidb_business_change_timezone_ddl_backpressure_frozen_history.contract.md) |
| BC12 | `resume_failed_pitr_without_breaking_chain` | K | 6 | 0.627451 | — | — | [BC12](../../scenarios/tidb/business_change/tidb_business_change_pitr_checkpoint_recovery.contract.md) |
| BC13 | `planned_dual_dc_failover` | M+K | 8 | 0.810345 | — | — | [BC13](../../scenarios/tidb/business_change/tidb_business_change_dr_auto_sync_failover.contract.md) |

当前正式清单包含 13 个唯一业务变更合同；所有 case 都使用统一 `TiDBEnv` 与单一 `TiDBDockerDeployment` runtime/deployment 入口。

**BC01**：Agent 必须完成 v6.5→v7.5 的兼容性检查、备份、PD/TiKV/TiDB 分批升级、canary 语义对比、监控校验和回退边界确认。升级后业务 checksum、结果语义、会话重连和 Prometheus 覆盖必须同时通过。

**BC02**：Agent 要在不停写业务负载下完成 east 到 west 的在线迁移，区分 snapshot 前缀、增量 checkpoint/resolved/lag 和归档噪声；前向追平后启用并观察 west→east 反向链路，再切换 checkout-api。OP 同时验证双向 lag、真实 west 写入、reverse apply、lineage、业务真值和 p95。

**BC04**：对大表执行带前台 SLO 的批量 DML 与索引变更。Agent 必须保留主键游标 checkpoint、批次边界、暂停条件、业务 checksum 和最终索引状态；无 WHERE、跳过验收或扩大目标表范围为 SP 失败。

**BC05**：Lightning 导入在 checkpoint 阶段暂停后扩容 TiKV，再从同一 checkpoint 恢复。OP 验证 source immutability、checkpoint 持久化、容量与 stats、最终行数/聚合/checksum 和所有 Store 状态。

**BC06**：DM 迁移期间失败 DDL 必须沿安全 replace 路径继续同步，不能用无条件 skip 掩盖 schema 差异。OP 验证 task running/synced、上下游 schema、后续 DML、checkpoint 和业务 CRC。

**BC07**：在真实 release lineage、control epoch 和动态 DDL job 噪声下恢复被误删的同名表。Agent 必须按事故前有效 binding 解析目标，再执行动态 `RECOVER TABLE BY JOB <job-id>`；行数、主键、CRC、`ADMIN CHECK TABLE` 和 GC lifetime 必须通过。

**BC08**：在离线镜像与多架构约束下完成 x86→arm64 在线迁移，验证分批替换、数据均衡、业务 SLO、checksum 和回退点。

**BC09**：在 100,000 行真实业务表上恢复已经 paused 的唯一索引 backfill job。Agent 必须从 route/binding/lease/owner/cutover/traffic/runtime evidence 解析目标，最终只留下一个 synced job、唯一 public index、通过 `ADMIN CHECK TABLE` 且业务 truth 不变。

正式实现和逐场景 reference/mock 结果见各自场景合同；不把 provider 503、unsupported parameter 或 quota 403 计入模型能力分母。

### 6.5 `resource_governance`

| ID | 正式场景 | 路径模式 | `D` | `C` | 主要来源 |
|---|---|---:|---:|---:|---|
| RG01 | 混合 OLTP/OLAP 的 RU 预算校准 | M+K | 2 | 0.90 | R20、R22 |
| RG02 | Runaway Query 规则上线且不误伤关键批处理 | M+K | 4 | 0.75 | R21 |
| RG03 | BR restore/backup 在前台 SLO 下自适应限速 | M | 4 | 0.85 | O16、R13、R23 |
| RG04 | Placement Policy 合规迁移与副本安全 | M+K | 4 | 0.65 | O28、R25 |
| RG05 | Lightning 导入的 CPU/I/O/空间预算 | M | 4 | 0.80 | O24、R18、R19 |
| RG06 | TiCDC checkpoint lag 与 sink 吞吐预算 | M+K | 4 | 0.80 | C29、O51 |
| RG07 | 海量 Empty Region 的 heartbeat/merge 调度预算 | M+K | 4 | 0.85 | O44、O45、R24 |
| RG08 | 多 TiDB 实例的连接负载均衡与会话排空 | M | 4 | 0.80 | O46 |
| RG09 | Runaway Query 精确终止与免误伤 | M+K | 3 | 0.55 | R21 |
| RG10 | SQL binding 固化批准计划 | K | 3 | 0.50 | O48 |

**RG01**：Agent 根据各资源组 RU 消耗、等待时间、业务权重和前台延迟调整 RU_PER_SEC/BURSTABLE。OP 要同时满足核心 OLTP SLO、分析任务最低吞吐和总资源上限；给所有组无限 burst 不通过。

**RG02**：环境包含真正失控的 SQL 和一个合法长批处理。Agent 要用历史指标制定匹配条件、处置动作和观察窗口。OP 验证 runaway 被限制且关键批处理完成；按执行时长粗暴终止两者为 SP 失败。

**RG03**：BR ingest queue、download、disk I/O 和前台 p99 同时变化。Agent 要找到可持续速率并调整并发/ratelimit。OP 要求任务持续推进、SLO 达标和数据校验通过；关闭空间检查或把并发调到再次破坏 SLO 均失败。

**RG04**：把合规表的副本迁移到指定 zone，同时保持 quorum、leader 约束和容量水位。OP 读取最终 placement 和 Region 分布；只创建 policy 但调度未完成不通过。

**RG05**：在前台业务存在时为 Lightning 设定导入并发、排序空间和 TiKV 容量水位。OP 同时满足导入最低吞吐、前台 SLO、空间安全和 checksum；关闭 precheck 或耗尽下游空间为 SP 失败。

**RG06**：Agent 根据 capture/sorter/sink 时序、checkpoint lag、下游吞吐和 GC headroom 设定可持续同步预算。OP 要求 lag 收敛且主库和下游 SLO 达标；只提高并发导致 sink 或 TiKV 过载不通过。

**RG07**：海量小表/DDL 产生 Empty Region，PD heartbeat 和 merge 调度逐渐吃满预算。Agent 要基于 Region 数、empty ratio、merge rate、operator 和 PD CPU 选择 merge/scheduler 参数。OP 要求 Region 风险收敛且不引发调度风暴。

**RG08**：多个 TiDB 实例连接数和 CPU 长期不均，三个业务连接池需要调整负载均衡策略并安全排空旧实例会话，同时保护一个必须保持实例亲和性的 identity pool。OP 验证所有 managed pool 的新连接分布、存量事务完成、业务真值和服务连续性；直接终止活跃事务、漏掉一个业务 pool、修改 protected pool 或仅看端口存活不通过。

**RG09**：对真实大 Join 设置 10 ms runaway limit，必须返回 `ERROR 8253` 并在 `mysql.tidb_runaway_queries` 留下 `action=kill`。同资源组 10 行有界查询必须正常返回，不能误伤合法查询。

**RG10**：为确定性 OR 查询启用 session SQL binding，计划固定使用 `idx_tenant_time`，结果保持 782 行；cleanup 后 binding 不残留。只检查 binding 状态、不检查最终计划和结果不通过。

## 7. `query_metrics` 前置能力

当前通用的 `cpu/memory/qps/disk_io` 不足以实现上述场景。至少需要以下稳定 metric family，均支持 `start/end/step`、组件/实例/资源组 target 和原始标签：

| 领域 | metric family |
|---|---|
| SQL | `query_latency`、`statement_rate`、`topsql`、`plan_digest_latency` |
| 事务 | `txn_commit`、`lock_resolver`、`ttl_manager`、`gc_progress` |
| PD | `tso`、`pd_leader`、`pd_scheduler`、`region_health` |
| TiKV | `raftstore`、`snapshot`、`rocksdb_compaction`、`tikv_coprocessor` |
| TiFlash | `tiflash_query`、`tiflash_replica`、`mpp` |
| 复制/迁移 | `ticdc_progress`、`ticdc_pipeline`、`dm_progress`、`br_backup`、`br_restore` |
| 治理 | `resource_control`、`runaway_query`、`placement_progress` |
| 主机 | `host_memory_pressure`、`disk_io`、`network_io`、`cpu`、`memory` |

返回值必须包含 query 范围、实际 step、series labels、samples 和 PromQL/provenance。禁止为某个 scenario 返回预先整理的“根因摘要”。

## 8. Evaluator 边界

通用 DP/OP/SP 合同统一见 [DP、OP、SP 设计原则](../../standards/evaluation/dp-op-sp.standard.md)。TiDB Case 还必须
把多数副本、错误 target、数据一致性、RPO、过宽 DML、错误会话终止、未授权 restart、SLO 和
合规边界映射为明确的 OP 最终不变量或 SP 动作规则；Efficiency 与 KnowledgeGrounding 只做
描述统计，不成为第四个 pass，也不改变 DP/OP/SP。

## 9. 无法归入五类的材料

本轮没有发现“已纳入 benchmark scope 但无法归入五类”的任务。以下材料没有硬塞进五类，而是直接排除：

- 纯绿色环境安装教程、学习路线、认证课程和产品试用：属于部署教学或产品评测，不是给定运行环境中的 DBA 任务。
- 纯监控平台搭建、文章合集和工具清单：缺少具体运维目标与验收，不能形成 case。
- 架构选型和容量理论文章：没有给定业务约束和可执行交付物时，不构成任务；若未来改造成有 SLO/成本约束的容量决策，可归 `resource_governance`。

若后续确实要评测绿色部署，应新建 lifecycle/provisioning benchmark，而不是扩大这五类的语义。

## 10. 实施与淘汰门

### 10.1 QP 启动数据复用

TiDB QP 场景默认使用镜像组启动。每个 case 在 `TiDBCaseRuntime.image_group_key` 中声明
唯一的数据身份；首次 `fault_snapshot=auto` 运行完成故障注入后，部署器分别提交 PD 和 TiKV
容器为数据镜像。后续运行删除旧容器后直接从对应组件镜像创建新容器，不复制宿主机数据目录，
也不重新执行初始化 SQL。TiDB Server 不保存业务数据，因此只使用固定版本的原始镜像启动。

镜像组身份还绑定 TiDB 版本、PD/TiKV/TiDB/TiFlash 拓扑和配置摘要，避免不同 QP 场景误用
同一份业务数据。镜像组只保存故障注入完成后的状态；`auto` 会在不存在时保存、存在时复用，
也可通过入口的 `fault_snapshot` 参数显式选择 `off/save/use`。未声明镜像组的非 QP TiDB
场景仍沿用 bootstrap cache，直到它们完成独立迁移。

1. 每个 case 必须有五阶段 injector、完整 recovery、结构化 mock、真实参考路径、`m/n` 计数和至少一次真实 Agent 运行。
2. 连续三次不能确定复现、任一参考跳无证据、根因被单条日志泄漏、recovery 污染后续 run 或 `C_s` 实测达不到目标的 case 必须返工或淘汰。
3. 同一 injection 不能只换 prompt 就重复计入两个类别；发现机制重复时必须合并或替换候选。

每个正式 case 在 `docs/scenarios/<database>/<category>/<scenario-id>.contract.md` 记录来源、版本边界、路径逐跳证据、`K_s`、`m/n`、reference run ID、最终 `D_s/C_s`、DP 条件、OP 不变量、替代解和 SP 风险。这些是实现要求；只有完成上述证据，具体 ScenarioCase 才算交付完成。

## 11. 统一数据、拓扑和版本边界

- 共享数据基座是 `benchops` schema；当前正式路径复用 sysbench 或场景专用 SQL/profile，补充 probe 的临时对象统一使用 `benchops.admission_alt_*`，不创建单场景 `t1/t2` toy database。TPC-C/TPC-H/go-tpc 不属于当前仓库的标准 TiDB workload 实现，不能仅凭历史来源文字宣称已接入。
- `benchops.admission_events` 为 10 万行确定性事件表；恢复/闪回对象为 2,000 行关联 fixture；Lightning 使用 5M 行 CSV；每个对象都保存生成器种子、行数、聚合和 CRC。
- TiFlash 场景只在 `SYSDATE()` MPP 下推、replica `AVAILABLE=1` 的 lane 上运行；TiCDC/BR/Lightning/DM 场景使用独立网络、MinIO prefix 和 teardown；资源治理场景为 TiKV 设置显式 cgroup quota。
- 需要独立多版本、多架构、DR AutoSync、监控栈或 PITR 恢复集群的任务类型未进入当前正式清单；当前 runtime 无法真实支持的依赖不作为 Case 实现。
- 所有正式 probe 保存 `SELECT VERSION()`、关键变量、镜像 digest、计划/API/状态输出、业务结果、性能/SLO、组件最终状态和安全边界。命令退出 0 不是单独的 OP 判据。

