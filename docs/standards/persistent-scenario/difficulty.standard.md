---
doc_id: standard.persistent-scenario.difficulty
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, persistent-scenario, postgres, tidb]
summary: Defines difficulty through production decisions, recurrence and whole-system reference, no-action and wrong-action paths.
source_of_truth: contract
related: [standard.persistent-scenario.architecture, standard.persistent-scenario.evaluation, standard.scenario.difficulty, guide.persistent-scenario.implement-persistent-scenario]
---

# Persistent Scenario 难度与三路径校准

## 1. 范围

本规范用于生产型 OLTP、OLAP、HTAP 持续运维；配套 [评估规范](evaluation.standard.md)。它替换按题目组合、事件数量和逐事件可解性推导长任务难度的做法。

## 2. 被测能力

难度来自真实业务取舍、因果解耦、发现路径、跨时间状态保持与防复发。不来自严重程度、事件数、固定修复时限或扩大损失。alert/inspection、高噪声、长时间是实例属性，不足以分别成为不同生产服务。

## 3. 三条路径是必要证据

完整处理路径证明公开工具下可满足端到端业务与安全合同，接受等价修复；零处理证明需要治理，不能依赖所有故障永久存在；错误处理证明表面恢复、片面优化和危险捷径可被拒绝。

三路径验证的是整个系统，不能用每个 case 单独可解代替组合可解。一个动作解除两故障、第三个故障消除第二个症状、提前保护阻止复发，都必须有合法评价。零动作仍通过全部业务合同则需重审实例，不强行新增事件关闭要求。

## 4. 难度证据

保留可解释向量：业务服务冲突、共享资源、因果遮蔽、事故发现机会、有效修复选择、重复机制、上下文和持久状态。记录真实到达、业务损失、预防、恢复和副作用，不使用全事件关闭率作为难度分数。

同机制重复可以测防复发和持续学习；要控制业务量、缓存、数据、故障强度差异，比较配对损失与处理证据，单次第二轮更快不能证明学习。禁止清空会话或撤销已生效保护来保证难度。

## 5. 校准顺序

静态与资源准入 → 重复健康正常/峰值负载 → 零处理 → 完整处理及等价解 → 错误处理 → unresolved/resolved/prevented 组合前缀 → cleanup/账本完整性 → 真实模型重复 pilot。

阈值依据业务承诺及资源可行性冻结，不能按模型失败情况回调。无可靠证据保持 measure-only/development_provisional；Hard 需要重复、可归因的决策能力差距。不能通过缩小预算、隐去正常运维证据或压短响应 deadline 创造 Hard。

## 6. 正式证据

保存输入种子、数据/拓扑/资源/代码/spec 版本、三路径 trace、可观测性与账本有效性、模型重复结果、invalid 清单、cleanup、阈值来源。业务交付 deadline 可以影响业务结果，作者的故障修复 deadline 仅作响应观测。分别报告 DP/OP/SP，不计算总 pass 或把 invalid 当模型失败。
