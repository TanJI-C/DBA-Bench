---
doc_id: guide.persistent-scenario.implement-persistent-scenario
doc_type: guide
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, persistent-scenario, postgres, tidb]
summary: Guides production-first implementation of the persistent scenarios from the portfolio contracts, covering scope, business contracts, event design, three-path validation, runtime lifecycle, evaluation surface, and acceptance order.
source_of_truth: contract
related: [standard.persistent-scenario.architecture, standard.persistent-scenario.evaluation, standard.persistent-scenario.difficulty, standard.evaluation.dp-op-sp]
---

# Persistent Scenario 生产型实例实施指南

## 1. 范围与顺序

本指南是目标流程：实现进度不得报告为运行或校准通过。依次阅读 [架构](../../standards/persistent-scenario/architecture.standard.md)、[评估](../../standards/persistent-scenario/evaluation.standard.md)、[难度](../../standards/persistent-scenario/difficulty.standard.md)、[五实例设计](../../persistent-scenarios/postgresql/production-portfolio.contract.md)。

先定义生产服务与负载，再定义风险演化、三路径，最后写 injector。不得先从题库选 5～10 个 case 拼时间线。旧 case 可借鉴机制；原生 capability 不需要 ScenarioCase 身份。

### 实施边界

本指南是实现入口；上述三个标准定义通则，五实例目标合同定义 PG 组合、时间线、三路径和文件级改造清单。尚未实测的预算和时间线保持 provisional；先验证资源可行性，再冻结数值，不按模型得分调参。

五实例不采用 bounded Scenario 的题库强制复用、固定事件配额、scenario/case pair 去重、逐注入事件诊断回应和每次告警新建会话等约束。业务交付 deadline 仍有效，事件修复 deadline 仅观察。五实例不要求不可控的全部级联逐项枚举，而要求真实输入、可信业务账本、数据不变量和安全历史覆盖实际后果。

设计哲学是：生产服务和负载决定故障；允许短暂压力、重复与联动；以整个运行的业务交付、数据正确性和安全性评价持续运维；完整/零/错误处理三路径证明可解、需要干预和决策有效。单个症状消失、被预防或被其他事件抵消不自动构成失败。

## 2. 业务合同先行

写明用户、交易/报表/作业、数据真值、拓扑、正常外部到达、资源预算、业务期限、可接受损失、必要系统状态、安全授权。OLAP 使用 job 清单，HTAP 两侧各有目标；对照流与必需业务分开。建立可复算、Agent 不可改写的外部账本。

明确 Agent 实际工具和控制面。需要改变调度并发、重试或路由时，提供真实生效的授权接口，不要求修改不可访问的应用代码。健康 baseline 必须覆盖正常峰值和合法维护，不只运行空闲探针。

## 3. 设计事件与联动

事件表写外部意图、到达时刻、机制、可观察信号、资源所有权、作用持续时间和潜在交互。允许重复机制、不同实体及部分重叠；不要求独立因果和逐事件响应。

后续到达不等 Agent；真实业务依赖由业务 job state 表达，例如 schema 未准备时回填等待，不能由 benchmark 等前一 Event 被评分后再启动。注入器不反复撤销修复保证故障存在。

记录 applied、attempted/prevented 与技术失败：预防需要可信保护状态和实际尝试证据；未知异常直接暴露。取消唯一 scenario/case pair 与 long-tx-before-lock 固定规则，改为真实资源冲突和 bounded activation 校验。

## 4. 三路径设计与实验

1. 完整处理：合法公开工具能满足端到端 OP/SP；至少验证可替代修复或提前预防。
2. 零处理：全部外部变化持续执行，业务最终至少一项违约；不要求所有注入故障都存活。
3. 错误处理：只治症状、牺牲另一业务、危险捷径分别有可观察失败；错误路径失败不自动证明 Hard。

在 unresolved、resolved、prevented prefix 下验证后续事件资源与语义。故障级联有意消除另一症状时按服务交付判断。回归、重复次数与发现时间是解释数据，非额外事件硬门槛。

## 5. Runtime 和生命周期

一个环境/拓扑持续运行，一个持久 mailbox session，普通工作项与巡检在同一 conversation 内处理；控制工具为 mailbox read/write/wait。任务完成是记账，不代表恢复。公开告警来自监测症状，不能泄漏内部 event ID、精确修复目标或标准 SQL。

workload、调度、Agent、遥测独立；append-only 记录原始会话与 compaction phases。业务输入停止、Agent 停止、drain、最终采样在合同中明确。最终评价在 reverse cleanup 前；清理仅回收本次实际资源，不撤销合法修复。

## 6. 评估与最小实现面

按服务目标、数据正确性和必要系统状态计算 OP；SP 读取动作、状态和授权；DP 可 N/A，不要求对每个故障作答。不要先建立通用无类型规则引擎，直接实现五实例需要的事务/job/水位/交付合同，复用 database/sql、query_results 等既有能力。

工作负载超时等终态与采集失败分离。部署/provider/collector 失效导致 invalid；被测 Agent 导致数据库坏掉不自动 invalid，靠外部账本继续记录业务和安全后果。

## 7. 改造与验收顺序

冻结输入/spec/data/resource/schema；实施新 model、ledger、capability 和 evaluator；迁移五实例与消费者；删除旧实例入口和旧聚合路径；focused tests；真实 healthy、三路径、prefix、cleanup；真实模型 pilot；最后 validated。所有 Python 命令在 conda aiops 环境内执行，实验按 [benchmark 实验指南](../benchmark/run-experiment.guide.md) 执行。

测试必须覆盖重复 capability、prevented、级联消失、一次修多个事件、低 QPS、重试分母、跨 horizon、HTAP 双侧约束、GUC 有效作用域、ledger 篡改、真实 timeout 与 collector failure。

正式 delivery 包括五实例合同、已实现 spec、三路径脚本/trace、失败分类、等价解证据、预算来源、资源与清理记录。只有文档或单元测试通过时保持 development_provisional；不能报告工业真实性已由实测证明。
