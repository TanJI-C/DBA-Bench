---
doc_id: scenario.postgresql.pg_resource_governance_audit_logging
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, resource_governance, pg_resource_governance_audit_logging]
summary: pg_resource_governance_audit_logging 的当前基于代码的契约快照；包含其注册的 Case、状态边界、评测器标识与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_resource_governance_audit_logging`

> 这是当前基于注册中心的场景（Scenario）契约。请先阅读数据库目录进行导航，然后在修改实现之前，于关联源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`resource_governance`
- 场景实现：`src.scenarios.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingScenario`
- 正式入口：`examples/run_pg_resource_governance_audit_logging_scenario.py`
- 当前描述：模拟高 QPS OLTP 工作负载下过量审计日志放大磁盘写入。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `audit_orders_role_logging` | 模拟高 QPS OLTP 工作负载下过量审计日志放大磁盘写入。 | `easy` |
| 1 | `orders_write_audit_scope_simple` | 聚焦的 pgAudit Case：一张结账表与一个合规审计角色。 | `easy` |

上方的 Case 集合是当前的代码快照。缺失校准是显式状态，不得从非注册标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公开状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 与评测器实现持有；本文档不杜撰代码中不存在的值。

### `audit_orders_role_logging`

- Case 编号：`0`
- 标题：模拟高 QPS OLTP 工作负载下过量审计日志放大磁盘写入。
- Alert/symptom: P1 production alert: a compliance logging rollout caused excessive checkout log writes not explained by WAL or table growth. Restore normal checkout operation while retaining real audit records for INSERT/UPDATE/DELETE, DDL and role changes. Routine checkout SELECTs must not produce statement or audit logs, and checkout reads/writes must succeed. No particular native statement-logging setting is required.
- 初始状态字段： `audit_scope`, `disk_write_amplification`, `status`
- 期望目标字段： `audit_scope`, `business_read_write`, `checkout_read_logging`, `status`
- 背景工作负载配置：checkout_status_rollup、payment_reconciliation_preview、checkout_live_touch_probe、receipt_latency_probe、missing_compliance_cache_log_noise
- 评测器：`src.scenarios.evaluation.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase`
- 难度标签与各 Case 的校准值维护在代码注册中心与场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复述这些实测值。

### `orders_write_audit_scope_simple`

- Case 编号：`1`
- 标题：聚焦的 pgAudit Case：一张结账表与一个合规审计角色。
- Alert/symptom: P2 compliance rollout alert: checkout log writes increased after audit logging was enabled, without corresponding WAL or table growth. Retain real audit records for INSERT/UPDATE/DELETE, DDL and role changes while eliminating routine checkout SELECT logs. Checkout reads/writes must succeed; no particular native statement-logging setting is required.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段： `audit_scope`, `disk_write_amplification`, `status`
- 期望目标字段： `audit_scope`, `business_read_write`, `checkout_read_logging`, `status`
- 背景工作负载配置：checkout_status_rollup
- 评测器：`src.scenarios.evaluation.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingForOrdersWriteAuditScopeSimpleEvaluatorCase`
- 校准：当前真实 pgAudit reference 证据见下文；正式测量值由代码注册表维护。

### 真实 pgAudit 机制与验收

专用 PostgreSQL 16 镜像安装 `postgresql-16-pgaudit`。两个 Case 启动时预加载 `pg_stat_statements,pgaudit`，先执行 `CREATE EXTENSION pgaudit`，再启用审计配置；保留业务 workload。初始同时启用原生 `log_statement=all`、pgAudit session 的 `pgaudit.log=all`，以及合规角色的 SELECT/INSERT/UPDATE/DELETE 对象审计权限，产生真实的读日志写放大。

最终通过实际结果验收：在新连接执行普通 checkout SELECT、已有行 UPDATE、探针行 INSERT/DELETE、CREATE TEMP TABLE 和 CREATE ROLE，全部写入和探针对象回滚。要求产生 INSERT、UPDATE、DELETE、CREATE TABLE（含实际对象信息）、CREATE ROLE 的真实 pgAudit 记录，checkout 读取返回一行非空数据、UPDATE 成功命中该行，且普通 checkout SELECT 日志数为零。原生语句/时长日志、pgAudit session/object READ 都计入多余读日志；保留业务表非空检查。

评估器读取探针期间追加的服务端日志，用已有 PostgreSQL 日志解析器按新连接 PID 隔离，使用标准 CSV 解析 pgAudit 记录。同一后端的最终 LOG 标记确认前序日志已经到达，才判断读日志缺失；最多轮询 20 次、间隔 100 ms。收集不到标记明确抛出日志采集错误，这不是业务延迟阈值。SQL 执行失败明确报错，异常路径也回滚并关闭连接。

参考修复仍可设置 `pgaudit.log='write,ddl,role'`、撤销对象审计角色的 SELECT 权限、使用原生 `log_statement=none`。这只是一个合理解法；`none`、`mod`、`ddl`、其他/空对象审计角色、等价掩码及无害的额外审计类别，只要实际结果满足要求都接受。ROLE 是类别，`pgaudit.role` 是对象审计角色，其 SELECT 权限可能在 session READ 关闭后继续记录读查询。真实审计缺失、checkout READ 日志仍存在、业务读写失败均不通过；占位 GUC 或只有原生语句日志无法代替结构化审计记录。

本 Case 不设置数值吞吐、延迟、磁盘 I/O 或日志容量 SLO。验收证明审计覆盖、普通读日志消除和业务可读写，不宣称已经测量吞吐恢复。公开 alert 明示这些行为要求。扩展、角色和权限随快照持久化，activate 核验后重建运行线程；recover 停线程、reset/reload 配置并重连，再删除扩展、业务表和自有角色。

### Reference 路径与难度测量证据

reference 逻辑路径为两跳：活跃 checkout 下日志写入过量 → 日志重复记录 checkout 语句而 WAL/表增长不对应 → 原生日志及 pgAudit session/object READ 策略叠加，超出必要 WRITE/DDL/ROLE 覆盖。参数、扩展元数据、角色权限及真实日志共同暴露最终复合原因；修复和验证调用不增加 D。

行为验收探针在诊断采样后运行，不增加诊断深度；初始故障、workload 和诊断证据集合保持一致。旧版原生审计校准已被替换。当前注册表使用新 reference 测量，catalog 同步对应标签。下方脚本在同一实际 workload 下保留未过滤的全部 `pg_settings`、表权限结果，以及声明的三秒窗口内追加的全部服务端日志，同时记录 reference Agent 首次获取的 disk-I/O/QPS 序列。参数中五行因果证据为 `shared_preload_libraries`、`pgaudit.log`、`pgaudit.role`、`log_statement`、`log_min_duration_statement`；权限中四行是本 Case 审计角色的授权；日志中业务表的真实 audit/statement 行为因果证据；磁盘写/QPS 是因果样本，磁盘读为竞争样本。其他行均保留并计数。完整 m/n、采样窗口、workload、真实审计证明及 run ID 保存到 `logs/calibration/pg-audit-reference-<case_id>.json`；不改写冻结结果或数据。

```bash
conda run -n aiops python scripts/validate_pg_audit_logging.py audit_orders_role_logging
conda run -n aiops python scripts/validate_pg_audit_logging.py orders_write_audit_scope_simple
```

脚本还验证：原生日志关闭后仍有 WRITE/DDL/ROLE 真实审计；带标记的只读 SELECT 没有日志；重新授予表级或列级对象 SELECT 会被 OP 拒绝；原生 none/mod/ddl、纯 session 审计及减法掩码等价配置可通过。

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

- Scenario 与 Case 源代码：`src.scenarios.postgres.resource_governance.audit_logging.PgResourceGovernanceAuditLoggingScenario`
- 评测器源代码：`src/scenarios/evaluation/postgres/resource_governance/` 下的一个或多个模块；确切的类已在上方按 Case 列出。
- 入口：`examples/run_pg_resource_governance_audit_logging_scenario.py`
- 聚焦测试、参考运行与调用轨迹只是证据，并非第二份契约。
- 在修改本文档之前，请将其与当前注册中心、Case 实现、评测器、聚焦测试以及实时验证证据进行比对。
