---
doc_id: scenario.persistent-scenario.pg-continuous-ops-smoke
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [postgres, persistent-scenario, pg-continuous-ops]
summary: Defines the PostgreSQL Persistent Scenario smoke contract with one durable mailbox session, asynchronous events, and persistent business-state evaluation.
source_of_truth: code
related: [standard.persistent-scenario.architecture, standard.persistent-scenario.evaluation, guide.persistent-scenario.implement-persistent-scenario]
---

# `pg_continuous_ops_smoke`

这是 PostgreSQL 长任务 Persistent Scenario 的开发配置。一个 TPC-DS scale 1 环境从 warmup 到 horizon 只部署一次，两个事件按固定时间线到达，后一个 Event 不等待前一个 Event 的处理。整个运行只创建一个持久 `session-0001` 和一条 LLM conversation。

可见的工作项在影响确认后写入 mailbox；不可见的系统变化不会直接向 Agent 解释原因，scheduler 只按 cadence 向同一个 mailbox 追加普通例行检查 task。Agent 感知到的是数据库状态变化和普通运维工作，不知道任务来自哪一种内部机制。Agent-facing Persistent Scenario 控制面只有一个 `mailbox` 工具：`read` 同时读取 pending/completed，`write` 一次完成一个或多个任务并保存结构化报告，`wait` 在信箱为空时挂起同一 conversation，直到新任务到来。alert task 的报告会作为对应 Diagnosis matcher 的输入，periodic task 的报告只做审计记录；Mailbox 不负责验证修复，也不直接决定 Outcome/Safety。

当前 smoke YAML 中的两个事件仍显式使用 `trigger: alert`，因此不改变既有 no-agent / calibration gate 语义。普通例行检查 task、可信状态检查、deadline、verification、mailbox lifecycle、`active/idle/woken` 状态、raw/phase conversation Trace 和单一 session wakeup 语义由 Persistent Scenario engine 的 focused tests 覆盖。

四条业务 flow 分别覆盖受影响的 `customer_profile_write`、不受影响的写/读控制流，以及只用于正确性校验的 `customer_integrity_probe`。业务 SLO 从 warmup 结束开始按固定 bucket 计算；Event 1 只进入 operational-risk objective，避免把 cleanup horizon 风险虚构成前端延迟事件。

`calibration.status=development_provisional` 只允许开发 Gate 和 focused tests。正式实验必须使用带证据 ID 的 `validated` calibration artifact，runner 不会警告后继续。

旧格式 trace 只作为历史反例保存，不能由 `persistent-scenario-v1` loader、trace reader 或 aggregate 读取。
