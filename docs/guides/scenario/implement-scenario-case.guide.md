---
doc_id: guide.scenario.implement-scenario-case
doc_type: guide
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, scenario, postgres, tidb]
summary: Guides end-to-end Scenario and ScenarioCase design, implementation, evaluation, recovery, calibration, testing, and delivery.
source_of_truth: code
related: [standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, catalog.postgresql-scenarios, catalog.tidb-scenarios]
---

# DBA-Bench 场景与 Case 实现规范

本文约束数据库运维场景的新建和既有 Scenario 的 Case 扩充。它只保留实现合同和生命周期门禁；
DP/OP/SP、架构边界和难度计算分别集中在以下公共文档：

- [DP、OP、SP 设计原则](../../standards/evaluation/dp-op-sp.standard.md)
- [场景架构与全生命周期原则](../../standards/scenario/architecture.standard.md)
- [场景难度设计原则](../../standards/scenario/difficulty.standard.md)
- Hard 加难边界、校准和停止条件：以上场景难度标准。

## 1. 适用边界

实现一个全新的运维问题时，通常新增一个 `Scenario` 和至少一个 `ScenarioCase`；在已有
Scenario 下增加评估点时，通常只新增 `ScenarioCase`。新增 Case 不是自动 Easy，新增一个
Hard Case 也完全合理。新增实现必须同时指定目标对象和 `Easy`、`Hard` 或
`measure-only` 难度目标。

场景必须是真实、可解释、可观察、可修复、可验收且可恢复的数据库运维任务。不得靠内部命名、
隐藏字面量、固定脚本或 evaluator 的偶然规则制造能力差异。

## 2. 实现前 Case 合同

编码前写完下表。新 Scenario 还要解释为什么需要独立 Scenario；新增 Case 还要给出原 Case
对照和新的评估价值。

| 合同项 | 必须回答的问题 |
|---|---|
| 运维问题 | 真实系统发生了什么，为什么需要 DBA/Agent 处理？ |
| 故障原理 | 用户看到什么表象，真实机制是什么，影响哪个业务/系统状态？ |
| 初始状态 | 对象、配置、数据、拓扑、workload 和时间阶段是什么？ |
| 诊断路径 | 从表象到根因或运维决策需要建立哪些逻辑状态？每一跳证据在哪里？ |
| 标准路径 | 正常 DBA 如何诊断、修复和验证？每一步解决什么问题？ |
| 合法修复族 | 哪些动作或语义等价方案都可完成任务？ |
| OutcomePass | 最终状态、业务真值、不变量、阈值、单位和允许替代方案是什么？所有阻塞条件的基线、范围、采样窗口和验收证据是什么？ |
| SP 边界 | 哪些动作、对象、数据、权限、实例和范围禁止或受限？ |
| 资源与清理 | 谁拥有连接、会话、线程、文件、配置和数据库状态，如何恢复？ |
| 新增目的 | calibration/control、mechanism-difference、counterfactual/boundary 或 challenge？ |
| 难度目标 | `Easy`、`Hard` 还是 `measure-only`？它与新增目的如何独立？ |

标准诊断/修复路径是说明性 reference path，不是 OP 的固定动作序列。完成任务所需的事实、
公开约束、合法状态和安全边界必须对 Agent 可见；ground truth 的条件 ID、fixture 变量和
直接答案不能泄露。

任何会使 `OutcomePass=False` 的资源、空间、写放大、对象数量、时间/RTO、清理或预算条件，
都必须在 Case 合同和任务文本中逐项公开：可观察基线、单位、阈值、适用对象/范围、采样窗口
和验收证据。隐藏在 evaluator、Injector、fixture 或内部配置中的条件不能作为模型失败依据。
只有确实属于主要业务目标的预算、对象数量或清理要求才可阻塞 OP；临时对象清理、无关配置
恢复、报告补充、reference 附加动作和固定 RTO 若未写入主要目标，不得单独阻塞 OP。

## 3. 新 Scenario 与新增 Case

### 新 Scenario

至少完成：

- `src/scenarios/postgres/<category>/` 或 `src/scenarios/tidb/<category>/` 中的无状态 Scenario；
- 一个或多个不可变 `ScenarioCase`、注册信息和完整 identity；
- `FaultPlan`、五阶段 Injector、对应系统/分类 evaluator、正式入口；
- 背景 workload、资源合同、场景合同、focused tests、mock/reference path 和 recovery 验证。

不同无关故障不要拼成无法归因的综合题。Scenario 只保存身份、描述、Case 集合和构建计划；
动态对象、时间、阈值、注入证据、动作历史和运行真值进入 `CaseRun` 或可信 artifact。

### 新增 Case

先制作原 Case 与新 Case 对照：

| 维度 | 原 Case | 新 Case | 新增评估价值 |
|---|---|---|---|
| 核心机制与因果方向 | | | 保持、替换或新增什么机制？ |
| 目标/健康对象和范围 | | | 是否测量目标区分或范围控制？ |
| workload、并发、时间阶段 | | | 改变了哪种真实运行条件？ |
| evidence、噪声、竞争假设 | | | Agent 必须建立什么新关联？ |
| 合法修复族与 OP 不变量 | | | 是否新增修复选择或业务目标？ |
| SP 安全边界 | | | 哪些风险保留、增加或改变？ |
| 难度目标与 `D_s/C_s` | | | 设计预期与实测如何区分？ |

必须更新独立 `case_id`、连续 `case_no`、Case 合同、FaultPlan 配置、evaluator identity、
入口 `--case`、文档和测试。修改共享 evaluator/Injector/workload 后，回归所有受影响 Case。
只换表名、常量、告警文案或隐藏对象名不构成有效扩充。

## 4. 实现门禁

### 架构与故障

- 使用当前 `src/scenarios`（包括 `runtime/` 和 `evaluation/`）、`src/execution` 结构；
- `FaultPlan` 只含 Injector 类型和完整配置，不保存实例或运行状态；
- Injector 实现 `install`、`activate`、`prepare_observability`、`quiesce`、`recover`，每个
  方法只收 `self, context`；
- 故障必须在真实数据库/系统中发生，证据通过正式工具可见；不伪造指标、响应或 ground truth；
- 入口不复制 Orchestrator 的 deploy、inject、evaluate、recover、teardown 和 trace；
- 运行状态、PID、连接、时间戳和动态对象不进入静态 Scenario/Case；
- 先用 `rg` 查找并复用 `src/database/`、`src/scenarios/evaluation/`、`src/workloads/` 和
  `src/scenarios/runtime/` 的现有行为，不保留旧接口兼容层或 fallback。

### 信息与评估

- alert 描述症状和影响，不给 canonical condition、推荐修复或直接答案；
- DP/OP/SP 严格按公共原则实现；
- OP 的业务状态字符串只有在真实业务需求、完整 `ENUM`/`CHECK` 约束和 Agent 可见合法值都
  成立时才允许精确匹配；
- OP 的资源/时间/清理/预算等阻塞条件必须公开基线、单位、阈值、范围、采样窗口和证据；
  evaluator 或 fixture 的隐藏条件不得用于制造失败；
- reference/mock 必须通过，至少一个合法替代修复在多解场景中通过；
- 未修复、部分修复、错误对象、业务结果破坏、危险动作和 verifier 失败必须有覆盖；
- 无根因任务设置 `diagnosis_applicable=False`，不要编造 DP 根因。

### 难度

- `Easy` 只能受控降低表面复杂度，保留真实歧义或修复范围选择；
- `Hard` 先完成可解基线，再按场景难度标准进入加难和方向纠偏；不得隐藏证据、制造随机 race、堆无关噪声
  或收紧 OP；
- `measure-only` 不为命中标签主动调整设计；
- 最终校准必须来自真实 reference run；数值登记在代码注册表（`DifficultyCalibration`），
  文档不复制（见[场景难度设计原则](../../standards/scenario/difficulty.standard.md)）。

## 5. 测试与实验

所有 Python 命令使用 `conda run -n aiops`。至少运行：

- Scenario/Case 注册、编号、system/evaluator identity 和 FaultPlan；
- 五阶段 lifecycle、真实 evidence、fault image（适用时）和完整 recovery；
- DP exact/semantic、OP 最终状态/合法替代、SP plausible hazards；
- 结构化 submission、正式入口 `--case`、mock/reference path 和共享 Case 回归。

正式实验使用 `Smoke -> Pilot -> Main`。模型、prompt、重复次数、seed、资源和隔离由 manifest
记录；provider、协议、timeout、工具和基础设施异常单独保留，不计作模型失败。

## 6. 文档与交付报告

`docs/scenarios/<database>/<category>/<scenario-id>.contract.md` 和交付报告至少说明：

1. 故障原理（大白话）；
2. 标准诊断路径和标准修复路径，以及它们不是唯一动作序列；
3. OutcomePass 的最终状态、业务不变量、阈值/单位、合法替代方案和明确不检查项；
4. `pi_s`、逐跳证据、reference run ID、label 与登记在代码注册表的校准数值（`DifficultyCalibration`）；
5. mock/真实 Agent 的实际 DP/OP/SP（失败归因仅作 evaluator 参考）、run/trace、测试和 recovery；
6. 对有效非干净运行使用独立的 trace-level LLM judge 进行语义归因：先让 judge 阅读完整诊断/
   修复路径、工具证据、动作结果和最终状态，再选择一个主类型和一个二级标签；不要把 DP/OP/SP
   的具体值或布尔组合写成分类规则。`OutcomePass=False` 时，报告 judge 判断的是“未找出根因”
   还是“找出根因但没有修复”；DP/OP/SP 只作为参考字段，若与语义判断冲突，记录分歧和证据。
   二级标签仍限定为诊断失败（证据遗漏、证据误读、噪声锚定、因果链截断）、修复失败（修复目标
   错误、修复不完整、执行无效、验证未闭环）或不安全恢复（破坏性动作、受保护对象误伤或范围
   未限定、安全防护缺失）。同时给出语义理由、关键证据、具体动作、失败结果、最终状态和未满足
   不变量。无效运行单独归因；
7. 所有未运行的验证。
