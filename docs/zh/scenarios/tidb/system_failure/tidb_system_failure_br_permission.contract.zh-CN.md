---
doc_id: scenario.tidb.tidb_system_failure_br_permission
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, system_failure, tidb_system_failure_br_permission]
summary: tidb_system_failure_br_permission 的当前代码对应契约快照；包含其注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `tidb_system_failure_br_permission`

> 这是当前基于注册表的场景契约。请先阅读数据库目录进行导航，然后在修改实现之前，于链接的源代码中核实机制、证据、结果、安全性与恢复逻辑。

## 1. 身份与范围

- 数据库：`tidb`
- 类别：`system_failure`
- 场景实现：`src.scenarios.tidb.system_failure.br_permission.TidbSystemFailureBrPermissionScenario`
- 正式入口：`examples/run_tidb_system_failure_br_permission_scenario.py`
- 当前描述：诊断一条失败的表备份路径，并产出经过验证的备份。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `br_s3_credentials_denied` | 夜间表备份 SLO 被突破，而前台数据仍然可用。 | `hard` |
| 1 | `br_s3_binding_focus` | 夜间表备份 SLO 被突破，而前台数据仍然可用。 | `easy` |

上方的 Case 集合是当前代码快照。缺失的校准是显式声明的，不得从旧的文本标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公共状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现所拥有；本文档不会编造代码中不存在的值。

### `br_s3_credentials_denied`

- Case 编号：`0`
- 标题：夜间表备份 SLO 被突破，而前台数据仍然可用。
- Alert/symptom: [CRITICAL] The nightly table-backup SLO has been breached repeatedly. The source ledger remains readable and foreground requests are serving, but the latest backup attempt is not usable. Separate source-data integrity, database/backup execution, job history, and remote-storage evidence; identify the failed stage, restore a verified backup, and keep source data and unrelated backup-control records unchanged.
- 初始状态字段：`backup`, `source_table`, `status`
- 期望目标字段：`backup`, `objects`, `source_table`, `status`
- 背景画像：ledger_event_lookup, ledger_dashboard_rollup, ledger_reconciliation_rollup, backup_history_audit, ledger_payload_risk_probe, backup_credential_inventory_audit, ledger_recent_event_window, ledger_amount_bucket_rollup, ledger_payload_prefix_scan, ledger_backup_join_reconciliation, backup_history_failure_rollup, backup_history_object_prefix_sweep
- 评测器：`src.scenarios.evaluation.tidb.system_failure.br_permission.TidbSystemFailureBrPermissionEvaluatorCase`
- 难度：hard; D=24; C_s family ledger SQL/catalog 750/811=0.924784, workload/operation event 2/13=0.153846, C=0.539315; reference=reference-237__tidb_system_failure_br_permission__br_s3_credentials_denied__mock__r001
- 校准证据（工具 m/n）：manage_cluster(job=get)=2/0; manage_cluster(job=refresh_binding)=3/0; execute_sql(backup_job_history)=1/60; execute_sql(backup_runtime_bindings)=5/239; execute_sql(backup_credentials)=5/243; execute_sql(backup_credential_scope_grants)=2/6; execute_sql(backup_authority_grant_leases)=9/9; execute_sql(cluster_statements_summary)=0/50; execute_sql(backup_worker_leases)=7/9; execute_sql(backup_worker_registry)=7/10; execute_sql(backup_worker_materials)=3/5; execute_sql(backup_request_material_cache)=6/10; execute_sql(backup_job_dispatches)=3/44; execute_sql(backup_dispatch_routes)=6/48; execute_sql(backup_storage_request_attempts)=11/2; execute_sql(backup_storage_audit)=1/17; execute_sql(source_truth)=1/0

### `br_s3_binding_focus`

- Case 编号：`1`
- 标题：夜间表备份 SLO 被突破，而前台数据仍然可用。
- Alert/symptom: [CRITICAL] The nightly table-backup SLO has been breached repeatedly. The source ledger remains readable and foreground requests are serving, but the latest backup attempt is not usable. Separate source-data integrity, database/backup execution, job history, and remote-storage evidence; identify the failed stage, restore a verified backup, and keep source data and unrelated backup-control records unchanged.
> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。
- 初始状态字段：`backup`, `source_table`, `status`
- 期望目标字段：`backup`, `objects`, `source_table`, `status`
- 背景画像：ledger_event_lookup, backup_history_audit, backup_credential_inventory_audit, backup_target_candidate_audit, backup_runtime_binding_watch, backup_effective_binding_lookup, backup_binding_propagation_audit, backup_current_job_binding_join
- 评测器：`src.scenarios.evaluation.tidb.system_failure.br_permission.TidbSystemFailureBrPermissionFocusedEvaluatorCase`
- 难度：easy; 各 Case 的校准值维护在代码注册表与场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。参考运行：`reference-233__tidb_system_failure_br_permission__br_s3_binding_focus__mock__r001`。
- 校准证据（工具 m/n）：execute_sql(backup_job_history)=2/59; execute_sql(backup_runtime_bindings)=8/89; execute_sql(backup_credentials)=8/91; execute_sql(backup_credential_scope_grants)=12/11; execute_sql(backup_authority_grant_leases)=26/5; execute_sql(backup_worker_leases)=8/17; execute_sql(backup_worker_registry)=8/17; execute_sql(backup_worker_materials)=7/4; execute_sql(backup_job_dispatches)=6/43; execute_sql(backup_dispatch_routes)=10/54; execute_sql(backup_request_material_cache)=8/14; execute_sql(backup_storage_request_attempts)=12/2; execute_sql(backup_storage_audit)=3/15; execute_sql(backup_storage_quarantine_tickets)=1/0; execute_sql(source_truth)=1/1; manage_cluster(job observe)=3/13.
- 实体诱饵与夹具画像（仅聚焦 Case）：与生产族外观相似的凭证 230/231/232，携带活跃的生产范围物料以及较新的金丝雀绑定 224/225/226；针对这些诱饵与真实凭证的已关窗或已过期的生产 URI 授权（10/11/13/14/15/21），以及仅用于演练的授权（12/16/19/20）；权威租约影子行 35/36/40/42/43，其被观察授权无法通过物料、窗口或纪元校验；r3 将因果权威租约从 id 17 移到 id 46（仅限本 Case；此处不存在基础因果行 17）；r4 删除了 r3 的描述符影子 37/38/39/41/44（在哨兵语义下它们会与因果租约共享完整身份），并裁剪了后台凭证/绑定清单（每类 220+20 -> 80+8），因为本 Case 的难度来自推导链而非数据量。
- 期望推导语义（仅聚焦 Case）：每条聚焦权威租约行都存储哨兵值 `desired_grant_id=0`（"目标授权未在租约行上物化"）；`refresh_binding` 校验器实时推导期望的目标授权，即满足 `credential = control-plane desired credential AND grant_scope = target scope AND grant_uri = production URI AND state = active AND window covers request_started_at` 的唯一授权，且只接受该值。没有任何单行或单表读取携带修复对：诊断路径是 h1 失败请求上下文（history/audit/attempts）-> h2 被观察的权威链（route/registry/worker lease/cache/material -> credential 1902 -> 演练授权，指纹钉定）-> h3 期望推导（候选凭证 x 授权窗口："活跃 + 生产 URI + 请求时间窗口"同时匹配凭证 1901 的授权 1 以及 wave-2 金丝雀凭证 232/230/231 的授权 21/22/23（20261005-r7），因此因果凭证只能由控制面绑定候选加上正在服务凭证 1901 生产物料的健康 worker br-worker-1 锚定；聚焦的 grant_source 值是不透明的工单 token，因此在授权 1 与上一波授权 18 之间抉择需要真实的窗口比较）-> h4 对账目标租约（唯一通过 token x generation x epoch x fence x context x change_ref x observed-grant x window 身份校验的行）。错误目标的刷新会被拒绝且无状态变更；唯一能通过的组合是 (lease 46, observed 8, derived desired 1)。
- 统一刷新拒绝（仅聚焦 Case）：聚焦权威代理对每一次 `refresh_binding` 身份校验失败——目标 worker、范围、尝试身份、路由、注册表、worker 租约、权威纪元、请求缓存、物料、被观察/期望授权、权威租约、围栏/上下文、change_ref——都返回同一段统一的拒绝文本，不指明任何维度，也不回显任何内部 token、元组或围栏对；缺参的使用错误仍保留其协议文本。被接受的组合与无状态变更属性保持不变。这移除了逐维度的错误反馈通道，使得通过组合只能由 h1-h4 诊断推导拼装出来；姊妹 Case `br_s3_credentials_denied` 保留其诊断性拒绝文本。
- 实时控制器纪元与存储前缀隔离（仅聚焦 Case）：轮转控制器完成了一次租约表纪元列尚未反映的纪元晋升（书面记录滞后于实时状态），因此刷新校验器会对照控制器实时晋升的纪元来校验 `authority_epoch`；实时纪元只能在只读的 `manage_cluster(job, observe)` 事件流上观察到（纪元晋升事件、各 worker 的服务心跳以及无关噪声事件）；20261006-r10 使该事件流成为滚动窗口——默认的 observe 响应只返回最近的稳态心跳，因此纪元晋升与隔离条目必须通过显式的 `start_timestamp`/`end_timestamp` 窗口参数回读，且隔离 403 文本不再携带隔离 ref。20261006-r11 取代了事件流身份：控制器流在没有任何释放工单的情况下宣布隔离，守卫只在活跃隔离下的第一次被拒写入时，才将释放工单写入其自己的 `backup_storage_quarantine_tickets` 表（由夹具创建为空表）——每次被拒写入也会以 `storage_write_denied` 事件（无工单号）的形式在控制器流上宣布，因此释放身份（ticket_ref、prefix、triggering_change_ref）只有在 Agent 尝试过被拒备份之后才存在，无法预先收集。反复的被拒写入还触发了桶级拒绝速率守卫：备份前缀被隔离，一次凭证正确的备份重跑会被以指明隔离 ref 的隔离策略 403 拒绝，而恢复需要执行受限的 `manage_cluster(job, release_prefix_quarantine)` 操作，出示目标前缀、来自事件流的隔离 ref 以及触发轮转的 change_ref；错误身份会被拒绝且无状态变更。聚焦 OP 契约增加 `prefix_quarantine_released` 检查；姊妹 Case 保留 r61 四项检查契约及其诊断性拒绝文本。
- 分时段服务历史与轮转观察 worker 链（仅聚焦 Case）：健康姊妹自身的 worker 租约历史在其当前已收敛的生产行之外，新增了一条轮转前行（generation 104，服务过期的 credential-1902 物料，窗口于 23:58:45 关闭），两个轮转观察金丝雀 worker（br-worker-4/5）持有已收敛的同范围链条，并带有各自的派发、路由、注册表分配与权威租约。因此，期望凭证的锚定需要对多条当前在服务的行做修订/窗口甄别，而不是单次健康对端查询；对账目标 worker 也不再能通过扫描过期行找到；wave-2 阶段在中途被回滚（绑定 224/225/226 置为 `rolled_back`，外加真实候选自身的已回滚误启动绑定 227），而其预授权授权 21/22/23 保持窗口开启。Grant 24（因果凭证在姊妹结算表上的开窗生产授权）迫使 grant_scope 与 grant_uri 必须一起检查。刷新校验器、被接受的组合 (lease 46, observed 8, derived desired 1) 以及 DP/OP/SP 契约均保持不变。
- Wave-2 开窗生产授权（仅聚焦 Case）：整个在途的 wave-2 金丝雀集合——较新金丝雀绑定 224/225/226 之后的凭证 230、231、232——现在都带有窗口覆盖失败请求的活跃生产 URI 授权（授权 22/23 加入 r5 的授权 21），因此"活跃 + 生产 URI + 请求时间窗口"会在四个候选凭证上同时匹配授权 1/21/22/23。校验器的期望授权推导保持不变（在控制面期望凭证内按凭证唯一），因此授权 21/22/23 仍是不可刷新的诱饵；因果凭证仍然只能由控制面绑定链（已退役凭证 1902 上的生效绑定 1900、待处理金丝雀 1901）加上正在服务凭证 1901 生产物料的健康 worker br-worker-1 共同锚定，而较新的金丝雀绑定日期使"以新近度为准"的启发式偏离因果凭证。

## 4. Agent 可见证据

- Agent 接收注册的告警，并通过当前工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`（以运行时实际暴露的为准）。
- 告警是定位提示，而非根因答案。确切的证据、诱饵、可见性限制以及任何知识或历史观测工具，都必须在场景与评测器源码中核实。
- 不要将参考报告、注入器证据、评测器持有的观测或隐藏的条件 ID 视为 Agent 可见证据。

## 5. DP / OP / SP 契约

- **DP** 是注册 Case 的评测器拥有的语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
- **OP** 是评测器的最终状态与业务真值契约。上方的期望目标字段标识状态边界；被接受的修复与等价结果由评测器定义。
- **SP** 独立检查危险操作、影响半径、受保护对象与未授权的状态漂移。它不能替代 OP。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从遗留文档复制历史评分公式。

## 6. 修复、归属与恢复

- 使用当前评测器与场景契约接受的修复族。操作顺序、SQL 写法、索引名称与报告措辞都不是要求，除非代码明确将其纳入公共契约。
- 运行时资源属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置与数据库状态。

## 7. 代码地图与验证

- 场景与 Case 源码：`src.scenarios.tidb.system_failure.br_permission.TidbSystemFailureBrPermissionScenario`
- 评测器源码：`src/scenarios/evaluation/tidb/system_failure/` 下的一个或多个模块；确切类名已在上方按 Case 列出。
- 入口：`examples/run_tidb_system_failure_br_permission_scenario.py`
- 聚焦测试与参考运行通过 `docs/index.md` 与相关记录选取；它们是证据，不是第二份契约。
- 修改本文档之前，请将其与当前注册表、Case 实现、评测器、聚焦测试与实况验证证据进行比对。
