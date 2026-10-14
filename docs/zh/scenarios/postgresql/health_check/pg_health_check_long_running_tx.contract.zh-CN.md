---
doc_id: scenario.postgresql.pg_health_check_long_running_tx
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, health_check, pg_health_check_long_running_tx]
summary: pg_health_check_long_running_tx 的当前代码背书契约快照；包含其注册的 Case、状态边界、评估器身份与校准状态。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_health_check_long_running_tx`

> 本文件是当前由注册表支撑的场景契约。请先阅读数据库目录进行导航，并在修改实现之前，于链接的源代码中核实机制、证据、结果、安全性与恢复。

## 1. 身份与范围

- 数据库：`postgresql`
- 类别：`health_check`
- 场景实现：`src.scenarios.postgres.health_check.long_running_tx.PgHealthCheckLongRunningTxScenario`
- 正式入口：`examples/run_pg_health_check_long_running_tx_scenario.py`
- 当前描述：模拟一个长时间处于 idle-in-transaction 状态的会话阻塞 vacuum/垃圾回收。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 当前标签 |
| ---: | --- | --- | --- |
| 0 | `checkout_pool_idle_transaction` | 模拟一次常规生产健康检查：在正常连接噪声中，一个过期的空闲事务钳制住清理水位。 | `hard` |
| 1 | `single_idle_transaction_cleanup_simple` | 在一个短暂空闲事务和一个监控工作进程的伴随下，一个过期的连接池事务阻塞清理。 | `easy` |
| 2 | `stress_idle_transaction_cleanup_01` | 清理水位压力阻塞项 01。 | `easy` |
| 3 | `stress_idle_transaction_cleanup_02` | 清理水位压力阻塞项 02。 | `easy` |
| 4 | `stress_idle_transaction_cleanup_03` | 清理水位压力阻塞项 03。 | `easy` |

上表是当前的代码快照。缺失的校准是显式的，不得从未注册的标签中推断。

## 3. 机制、初始状态与目标

以下字段是当前 Case 契约暴露的公共状态边界。实际的故障机制、持久化资源与目标值由 ScenarioCase、FaultPlan、Injector 和评估器实现所有；本文档不编造代码中不存在的值。

### `checkout_pool_idle_transaction`

- Case 编号：`0`
- 标题：模拟一次常规生产健康检查：在正常连接噪声中，一个过期的空闲事务钳制住清理水位。
- Alert/symptom: [Scheduled PostgreSQL Health Check] Transaction age, cleanup horizon, and maintenance indicators crossed the housekeeping threshold during the latest routine review. Inspect connection state, transaction age, xmin horizon, and table cleanup signals; take only necessary low-risk action and report prevention measures.
- 初始状态字段：`connection_mix`、`maintenance_indicators`、`status`
- 期望目标字段：`cleanup_horizon`、`idle_timeout`、`status`、`table`
- 背景画像：未声明
- 评估器：`src.scenarios.evaluation.postgres.health_check.long_running_tx.PgHealthCheckLongRunningTxForCheckoutPoolIdleTransactionEvaluatorCase`
- 难度标签与逐 Case 校准值由代码注册表和场景目录维护；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约刻意不重复这些实测值。

### `single_idle_transaction_cleanup_simple`

- Case 编号：`1`
- 标题：在一个短暂空闲事务和一个监控工作进程的伴随下，一个过期的连接池事务阻塞清理。
- Alert/symptom: [Scheduled PostgreSQL Health Check] Cleanup progress is behind its normal window while the instance remains available. Identify the session holding the cleanup horizon, avoid terminating unrelated sessions, restore cleanup, and add a preventive timeout.
- 初始状态字段：`connection_mix`、`status`
- 期望目标字段：`cleanup_horizon`、`status`、`table`
- 背景画像：未声明
- 评估器：`src.scenarios.evaluation.postgres.health_check.long_running_tx.PgHealthCheckLongRunningTxForSingleIdleTransactionCleanupSimpleEvaluatorCase`
- 校准证据（工具 m/n）：代码中未声明

### `stress_idle_transaction_cleanup_01`

- Case 编号：`2`
- 标题：清理水位压力阻塞项 01。
- Alert/symptom: [Scheduled PostgreSQL Health Check] Additional cleanup horizon blocker 01 is active during the long-task stress probe.
- 初始状态字段：`connection_mix`、`status`
- 期望目标字段：`cleanup_horizon`、`status`、`table`
- 背景画像：未声明
- 评估器：`src.scenarios.evaluation.postgres.health_check.long_running_tx.PgHealthCheckLongRunningTxForStressIdleTransactionCleanup01EvaluatorCase`

### `stress_idle_transaction_cleanup_02`

- Case 编号：`3`
- 标题：清理水位压力阻塞项 02。
- Alert/symptom: [Scheduled PostgreSQL Health Check] Additional cleanup horizon blocker 02 is active during the long-task stress probe.
- 初始状态字段：`connection_mix`、`status`
- 期望目标字段：`cleanup_horizon`、`status`、`table`
- 背景画像：未声明
- 评估器：`src.scenarios.evaluation.postgres.health_check.long_running_tx.PgHealthCheckLongRunningTxForStressIdleTransactionCleanup02EvaluatorCase`

### `stress_idle_transaction_cleanup_03`

- Case 编号：`4`
- 标题：清理水位压力阻塞项 03。
- Alert/symptom: [Scheduled PostgreSQL Health Check] Additional cleanup horizon blocker 03 is active during the long-task stress probe.

> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。

- 初始状态字段：`connection_mix`、`status`
- 期望目标字段：`cleanup_horizon`、`status`、`table`
- 背景画像：未声明
- 评估器：`src.scenarios.evaluation.postgres.health_check.long_running_tx.PgHealthCheckLongRunningTxForStressIdleTransactionCleanup03EvaluatorCase`

故障启动遵守 bounded Scenario 生命周期。`fault_snapshot=off` 时，`install()` 必须在观测和 Agent 开始前建立持久化现场及运行中的阻塞会话。`save` 在安装后先通过 `quiesce()` 停止会话再保存镜像，之后通过 `activate()` 重建运行时；`use` 从已有现场重建运行时。Persistent Scenario 使用独立 Event 能力，不调用此注入器。

## 4. Agent 可见的证据

- Agent 接收注册的告警，并在运行时暴露的范围内通过当前工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`。
- 告警只是定位提示，而不是根因答案。确切的证据、干扰项、可见性限制以及任何知识或历史观测工具，都必须在场景与评估器源代码中核实。
- 不要把参考报告、注入器证据、评估器自有的观测或隐藏的条件 ID 当作 Agent 可见的证据。

## 5. DP / OP / SP 契约

- **DP** 是注册 Case 的评估器自有语义诊断契约。它独立于修复是否完成，并使用共享的 DP 协议。
- **OP** 是评估器的终态与业务事实契约。上文的期望目标字段界定了状态边界；被接受的修复与等价结果由评估器定义。预防性的 `idle_in_transaction_session_timeout` 在预定区间 [30s, 15min] 内接受（DP/OP/SP 标准的 config-interval 例外）：远低于故障的 2 小时空闲水位，因此再次出现的停滞无法重新钳制清理水位，同时又高于该 Case 的合法业务事务跨度；而不是要求某个固定的设置字面量。
- **SP** 独立检查危险操作、影响范围、受保护对象以及未经授权的状态漂移。它不是 OP 的替代品。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义；不要从遗留文档复制历史评分公式。

## 6. 修复、归属与恢复

- 使用当前评估器和场景契约接受的修复族。操作顺序、SQL 写法、索引名称和报告措辞都不是硬性要求，除非代码明确将其纳入公共契约。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复必须通过当前的五阶段协议释放 Case 持有的连接、会话、线程、进程、文件、配置和数据库状态。

## 7. 代码地图与验证

- 场景与 Case 源码：`src.scenarios.postgres.health_check.long_running_tx.PgHealthCheckLongRunningTxScenario`
- 评估器源码：`src/scenarios/evaluation/postgres/health_check/` 下的一个或多个模块；确切的类已在上方逐 Case 列出。
- 入口：`examples/run_pg_health_check_long_running_tx_scenario.py`
- 聚焦测试、参考运行和轨迹是证据，而不是第二份契约。
- 在修改本文档之前，请将其与当前注册表、Case 实现、评估器、聚焦测试和实际验证证据进行比对。
