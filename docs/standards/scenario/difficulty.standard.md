---
doc_id: standard.scenario.difficulty
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, scenario, postgres, tidb]
summary: Defines the evidence-based Scenario difficulty dimensions, binary labels, calibration rules, and hardening boundary.
source_of_truth: code
related: [standard.scenario.architecture, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# 场景难度设计原则

Difficulty 描述 Agent 面对的诊断环境，不是 evaluator 的惩罚项。它是 Case 的元数据，不能
改变 DP、OP、SP、turn budget、工具合法性或安全且实质等价的解空间。实现完成后用真实
reference run 校准；`Easy`/`Hard` 是测量结果，不是文件名或设计意图直接决定的标签。

## 1. 两个独立维度

### 诊断路径深度 `D_s`

用 DBA 可复核的逻辑状态路径表示：

```text
pi_s = <sigma_s, h_1, ..., h_(D_s-1), c_s>
D_s = len(pi_s) - 1
```

`sigma_s` 是初始表象，`h_i` 是 Agent 必须建立的中间逻辑状态，`c_s` 是根因、复合因果状态，
或无根因任务所需的安全/运维决策。每一跳都要有正式工具可见的支持证据。重复查询、分页、
轮询、修复和验证不增加深度；路径不要求唯一或最短，其他合法路径仍按 DP/OP/SP 正常计分。

### 环境复杂度 `C_s`

取 reference path 所需关键工具集合 `K_s`，在同一 live workload 下统计未过滤结果：

- `m_(s,u)`：工具 `u` 返回的因果证据单元；
- `n_(s,u)`：同一结果里的其他可观测单元；日志按行、表格按结果行、时序按数据点计数；
- `rho_s = sum(m_(s,u)) / sum(m_(s,u) + n_(s,u))`；
- `C_s = 1 - rho_s`。

分母必须来自真实 observed units 且大于零。记录每个关键工具的 `m/n`、采样窗口、workload
配置和 reference run ID。只有未过滤结果确实没有竞争观测时才允许 `C_s=0`；不能先过滤、
截断或靠作者估计得到零噪声。噪声应来自真实业务、维护、历史事件或系统状态，并且可解释、
可复现、出现在 Agent 实际依赖的关键结果中。

## 2. 二元标签

当前阈值为 `D_0=2`、`C_0=0.5`：

- `Hard` 当且仅当 `D_s > 2` 且 `C_s >= 0.5`；
- 其他组合均为 `Easy`；
- 不使用 `Medium`，代码序列化为小写 `hard`/`easy`。

两个维度是独立的：路径深但几乎没有竞争证据，或证据很嘈杂但路径很浅，都不能凭单一维度
宣称 Hard。改动影响 reference path、工具返回、workload 或计数单位时，旧校准失效，必须重算。

## 3. 新 Case 的难度目标

`addition_purpose` 和 `difficulty_target` 分开记录。新增 Case 可以是 Easy、Hard 或只测量，
不能因为“只是新增”就默认 Easy，也不能因为“覆盖新机制”就自动是 Hard。

- **Easy**：可以减少表面实体、背景噪声、并发或阶段数量，但必须保留至少一个真实歧义或
  修复范围决策；不能退化成一次工具调用直接给出根因和固定动作。
- **Hard**：选择真实的因果链、同域竞争证据、跨层/时间关联、健康近邻区分、目标范围或
  修复选择等维度增加能力要求，仍须保留完整可观察、可修复的 reference path。
- **只测量**：不为了命中特定标签调整设计，完成真实实现后观察 `D_s/C_s`。

Hard 不得靠隐藏必要证据、随机 race、无关噪声、缩短时间预算、损坏工具、删除合法修复或
收紧 OP 产生。Easy 也不得删除关键 workload、verifier 或安全边界来制造“简单”。任何表面
简化都要说明隔离了哪项能力、保留了哪项真实判断。

## 4. 难度与评估的关系

难度变化应落在真实证据结构或修复决策上，而不是评估器门槛上：

- DP 仍只判断最终诊断语义；
- OP 仍按最终状态、业务真值和公开约束验收，并接受合法等价修复；
- SP 仍独立判断危险动作和 blast radius；
- 难度不参与 pass 计算，也不能用来为某个模型定制失败。

如果被测模型失败，先由独立 trace-level LLM judge 阅读诊断/修复路径和证据，语义判断是未找出
根因还是找出根因但没有修复，并选择一个主类型和二级标签：诊断失败（证据遗漏、证据误读、噪声
锚定、因果链截断）、修复失败（修复目标错误、修复不完整、执行无效、验证未闭环）或不安全恢复
（破坏性动作、受保护对象误伤或范围未限定、安全防护缺失）。DP/OP/SP 只作参考，不得用其具体
值或组合机械分类。provider、基础设施、工具、随机时序和格式失败不是难度证据。只有有效
`OutcomePass=False` 才进入 Hard 加难要求的方向纠偏循环；具体执行步骤由调用方流程负责，本
标准只定义加难的证据、边界和停止条件。

## 5. 校准记录与信息源边界

校准数值只有一个登记处：代码注册表中的 `DifficultyCalibration`（`diagnostic_depth`、
逐工具 m/n 证据单元、复杂度、`reference_run_ids`）。文档侧按以下分工引用，不复制数值：

- 场景合同记录 `pi_s` 和每一跳的 Agent-visible evidence、合法 reference/mock 修复、
  替代修复、失败状态和 recovery 结果；校准数值不复述，指向本标准与代码注册表；
- 场景目录只保留二元标签；
- `data/scenarios/*_case_attributes.yaml` 只保留派生属性（标签、deep/direct、high/low），
  由一致性测试与注册表对齐。

常见错误是用 Agent turn 数代替逻辑深度、只统计过滤后的“相关行”、把随机波动当噪声、用
删证据制造 Hard，或因为模型通过就不断堆叠无关条件。难度应服务于可解释、可复现的能力测量。
