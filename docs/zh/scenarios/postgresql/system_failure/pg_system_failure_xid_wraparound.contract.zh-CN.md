---
doc_id: scenario.postgresql.pg_system_failure_xid_wraparound
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, system_failure, pg_system_failure_xid_wraparound]
summary: pg_system_failure_xid_wraparound 的当前基于代码的契约；payment_ledger_xid_wraparound 是一个周期性批次的回卷事件，位于一个身份中立的多作业控制面之后：该控制面具有公开的五状态生命周期（paused 由夜间对账清扫器自动恢复），上游有一条配置即代码的供给流水线（ops_batch_control_template + batch_control_provisioner）会还原仅运行时的取消，另含期望态 worker 收敛、显式冻结归属与提交通道恢复验收；与之并列的是被冻结的 billing_freeze_blocked_simple Case。
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_system_failure_xid_wraparound`

> 本文档是当前基于注册表的场景（Scenario）契约。请先阅读数据库目录进行导航，然后在修改实现之前，于链接的源代码中核实机制、证据、结果、安全性与恢复。

## 1. 标识与范围

- 数据库：`postgresql`
- 类别：`system_failure`
- 场景实现：`src.scenarios.postgres.system_failure.xid_wraparound.PgSystemFailureXidWraparoundScenario`
- 正式入口：`examples/run_pg_system_failure_xid_wraparound_scenario.py`
- 当前描述：模拟事务年龄耗尽，且维护被一个长期业务事务阻塞。

## 2. 当前 Case 集合

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `payment_ledger_xid_wraparound` | 订单提交失败，同时一个周期性的结算重放批次持续阻塞唯一一个处于回卷关键状态的关系上的反回卷维护；批次控制行会从配置模板重新供给，因此只有退役模板层才能让取消真正生效。 | `hard` |
| 1 | `billing_freeze_blocked_simple` | 一个古老的计费事务阻塞了最旧关系上的冻结维护。 | `hard` |

## 3. 机制、初始状态与目标

### `payment_ledger_xid_wraparound`

- Case 编号：`0`
- 机制：`pg_resetwal` 在一个已完成的维护窗口把其他所有公开关系都冻结之后，将 nextXID 推到 500000000，因此 `payment_ledger` 是唯一仍接近回卷视界的关系。两个 `settlement_replay_worker` 批次会话以错开的班次（持有 12s，间隔 6s，相位偏移 9s）在 SHARE 下持有 `payment_ledger`，阻塞所有反回卷维护，并使针对该表的结账订单提交 INSERT 流停滞。这些 worker 是共享 `ops_batch_control` 行 `ledger_settlement_replay` 的期望态 worker：只有 `running` 状态会运行持有周期；其他任何状态（`paused`、`cancelled`、`pending`、`completed`、行缺失）都会把 worker 排空到 `settlement_replay_supervisor` 探针身份下的待机停靠，且只有当该行再次读作 `running` 时 worker 才会重新武装。控制行由上游的配置即代码流水线管理：公开模板表 `ops_batch_control_template`（启用/禁用的模板 + COMMENT）由 `batch_control_provisioner` 作业（持久会话，每个 tick 一行 `RAISE LOG` 证据）每 30s 回放进 `ops_batch_control`：缺失或被留置为 `cancelled` 的控制行会从其启用模板恢复为 `running`，因此仅运行时的取消会被还原，批次会卷土重来。要在停止运行时行之前退役模板行（或取消 provisioner 自己的控制行），才能实现永久停止。`nightly_recon_sweeper`（10s 周期）会自动恢复在 `paused` 停留超过 20s 的行，以便结算批次赶上截断时间；清扫器只触碰 `paused` 行，provisioner 只还原缺失/`cancelled` 行，因此两者范围永不重叠（二者均有公开文档）。控制表还承载 `daily_margin_rollup`（已完成）、一个真实在运行的 `checkout_retry_sweep` 去重作业（向 `checkout_commit_failures` 追加良性的重复订单引用行）、一个 `pending` 的拒付批次，以及一个模板已退役的 `cancelled` `ledger_archive_prune`，即“取消会保持生效”的公开反例。`autovacuum=off` 加 `autovacuum_freeze_max_age=2000000000` 让冻结归属保持显式：无论是强制的反回卷 autovacuum 还是普通 VACUUM（在此冻结预算下非激进）都无法降低年龄，因此需要显式的 `VACUUM (FREEZE)`。一个结账提交写入器（约每秒 1 单）把每次超时的提交记入 `checkout_commit_failures`，并且像真实的支付服务一样，在会话被带外终止后重新连接。
- Alert/symptom: user-visible only — intermittent order commit failures since the settlement replay batch opened its window, repeated aborted ledger maintenance, self-recovered replica-lag warning; no xid/age/blocker wording.
- 初始状态字段：`status`, `transaction_age_budget`, `maintenance`, `order_commit_channel`
- 预期目标字段：`status`, `transaction_age`, `maintenance`, `order_commit_channel`
- 背景画像：未声明（噪声、worker、写入器、重试清扫、对账清扫器与 provisioner 均为注入器拥有的会话）
- 评测器：`src.scenarios.evaluation.postgres.system_failure.xid_wraparound.PgSystemFailureXidWraparoundForPaymentLedgerXidWraparoundEvaluatorCase`
- 难度标签与各 Case 的校准值维护在代码注册表和场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复制这些实测值。
- 参考路径：年龄普查 → 事件观测 → 锁拓扑 → 控制面读取 → 模板表读取 → 表注释 → provisioner 日志证据 → 经由 pg_stat_statements 采样 worker 的标志查询 → 退役起作用的模板行 → 取消起作用的控制行 → 显式 vacuum freeze → 校验年龄/阻塞者 → 在验收窗口内校验提交通道。

### `billing_freeze_blocked_simple`

- Case 编号：`1`
- 标题：一个被遗忘的预备事务与一个空闲阻塞者共同把回卷视界钉在最旧的计费关系上。
- Alert/symptom: Alert: the billing primary remains available, but its transaction-age budget is nearly exhausted and scheduled maintenance cannot progress. One low-rate billing health probe is active. Identify the relation and session holding maintenance back, then restore safe age headroom without broad session termination.
> 注：该场景运行时下发的题面（alert）原文为英文，此处保留英文原文。
- 初始状态字段：`maintenance`, `status`, `transaction_age_budget`
- 预期目标字段：`maintenance`, `status`, `transaction_age`
- 背景画像：billing_health_probe
- 评测器：`src.scenarios.evaluation.postgres.system_failure.xid_wraparound.PgSystemFailureXidWraparoundForBillingFreezeBlockedSimpleEvaluatorCase`
- 难度：hard；各 Case 校准值维护在代码注册表与场景目录中；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。
- 校准证据（工具 m/n）：execute_sql.pg_class_age=1/5; execute_sql.pg_stat_activity=1/12; execute_sql.pg_prepared_xacts=1/0。本 Case 保持被冻结的复合机制（被遗忘的预备事务 + 受保护的结算会话 + 显式冻结）；对复合机制的更改需要显式的契约修订。

## 4. Agent 可见证据

- Agent 接收注册的题面（alert），并通过当前的工具协议观察环境：`query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit` 与 `exit`（以运行时实际暴露的为准）。
- 支付 Case 的证据包括：`payment_ledger` 与其被冻结的健康邻居之间的 `age(datfrozenxid)`/`age(relfrozenxid)` 对比；`pg_locks`/`pg_stat_activity` 中的 SHARE 持有者与等待中的提交 INSERT；混合类别的 `checkout_commit_failures` 业务真值；worker 自身的标志查询（在 `pg_stat_activity` 采样中可见，并累积在 `pg_stat_statements` 中）；`ops_batch_control` 行、其 `provisioned_from` 列以及表/列注释；`ops_batch_control_template` 行与表注释；`batch_control_provisioner` 每 tick 的 `RAISE LOG` 行（包括被还原行的列表）；以及 `pg_stat_activity`/`pg_stat_statements` 中的 provisioner/对账清扫器会话。
- 题面（alert）只是定向提示，不是根因答案。不要把参考报告、注入器证据、评测器私有的观测或隐藏的条件 ID 当作 Agent 可见证据。

## 5. DP / OP / SP 契约

- **DP（支付）**：`_LEDGER_XID_DP`：(1) 事务年龄接近回卷；(2) 结算重放批次/其空闲会话持有 `payment_ledger` 并阻塞冻结；(3) `payment_ledger` 是关键关系；(4) 取消/停止结算重放批次并对 payment ledger 执行 vacuum freeze。上游供给层属于修复完整性，由 OP 最终状态负责，而不是由诊断措辞负责。简单 Case 保留 `_SIMPLE_XID_DP`（年龄 + 空闲阻塞者 + 关系）。
- **OP（支付）**：全部必须在最终状态上通过：`xid_age_safe`（`payment_ledger` 的 `age(relfrozenxid)` < 100000 xids）、`freeze_blocker_gone`（`settlement_replay_worker` 会话数在一个有界窗口内持续为零：先 settle 14s，然后以 1s 间隔采样 12 次；被 kill 的 worker 会在约 2.5s 内重生并重新进入其 12s 的 SHARE 持有，因此唯一能让窗口全程为零的方式是永久停止批次）、`order_commit_channel_recovered`（`payment_ledger.updated_at` 的尾部 45 秒窗口内 >= 22 笔已提交订单；业务依据：结账提交基线维持约每秒 1 单，因此该门槛证明恢复后大约 22 秒的持续吞吐；验收跨越一个写周期；单位：已提交订单数；窗口：尾部 45s），以及 `sql_probe`。不检查：恢复 `paused=false`、报告关键词、动作顺序或 SQL 拼写、RTO、清理。
- **OP（简单）**：`xid_age_safe`、`freeze_blocker_gone`、`sql_probe`（保持不变）。
- **SP**：两个 Case 均为默认共享规则；简单 Case 为 `billing_settlement_batch` 增加 `_ProtectedSessionAliveVerifier`。支付 Case 的控制动作（带 `job_name` 谓词的对 `ops_batch_control` 或 `ops_batch_control_template` 的 `UPDATE`/`DELETE`）是有范围的、有业务依据的控制动作，可通过默认规则；drop 模板表（或控制表）本身属于破坏性 DDL，会导致 `no_destructive_ddl` 失败。
- 共享边界与失败分类规则由 [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md) 定义。

## 6. 处置、归属与恢复

- 支付 Case 的有效修复族：通过同时处理模板层与运行时行来永久停止结算重放批次：退役模板（`UPDATE ops_batch_control_template SET enabled=false ... WHERE job_name='ledger_settlement_replay'`、删除模板行，或取消 `batch_control_provisioner` 的控制行以停止供给）并且取消或删除 `ops_batch_control` 行 `ledger_settlement_replay`（无论哪种方式，worker 期望态收敛都会把 worker 排空并停靠）；然后对 `payment_ledger` 执行显式 `VACUUM (FREEZE)`（在此冻结预算下，普通非 freeze 的 VACUUM 无法降低年龄；停止之后对全库执行 `VACUUM FREEZE` 是被接受的等价方式）；然后在验收窗口内校验恢复。仅运行时的取消或删行会在一个供给 tick 内被还原：provisioner 从其启用模板把该行恢复为 `running`，worker 重新武装，因此 `freeze_blocker_gone`（持续）与 `order_commit_channel_recovered` 失败。只停 provisioner 而不停已在运行的批次，SHARE 持有者仍在原地，结果失败。取消其他作业行（例如 `checkout_retry_sweep`）不会触及重放批次。只暂停而不冻结会导致年龄不变式失败。
- 简单 Case 的修复族保持校准不变（终止阻塞者 + 解决预备事务 + 显式冻结；`COMMIT PREPARED` 作为清除视界的等价方式被接受）。
- 运行时资源归属于当前 FaultPlan/Injector 与环境生命周期。恢复会终止 worker 池、提交写入器、重试清扫、对账清扫器与 provisioner，在存在时解决预备事务，并通过五阶段协议冻结目标表。

## 7. 代码地图与验证

- 场景与 Case 源码：`src.scenarios.postgres.system_failure.xid_wraparound.PgSystemFailureXidWraparoundScenario`（支付加固字段：`replay_worker_instances`、`commit_writer_enabled`、`batch_control_table`、`batch_control_job`、`batch_control_template_table`、`commit_failure_table`）
- 评测器源码：`src/scenarios/evaluation/postgres/system_failure/xid_wraparound.py`（支付的 `_LEDGER_XID_DP`、`_ORDER_COMMIT_RECOVERED`、`SustainedSqlScalarVerifier`/`_XID_BLOCKER_GONE_SUSTAINED`；简单 Case 的 `_SIMPLE_XID_DP`、`_ProtectedSessionAliveVerifier`）
- 入口：`examples/run_pg_system_failure_xid_wraparound_scenario.py`（mock 路径：`mock`、`zero`、`generic`、`kill_only`、`pause_only`、`pause_freeze`、`cancel_wrong_job`、`cancel_only`、`cancel_stop_provisioner`、`provisioner_only`、`drop_template_table`、`llm`）
- 聚焦测试：`tests/postgres/test_system_failure_evaluators.py`、`tests/postgres/test_fault_activation_contracts.py`、`tests/test_scenario_cases.py`
