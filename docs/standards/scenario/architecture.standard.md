---
doc_id: standard.scenario.architecture
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, scenario, postgres, tidb]
summary: Defines the current Scenario and ScenarioCase model, five-phase fault lifecycle, evaluator boundary, and delivery gates.
source_of_truth: code
related: [standard.evaluation.dp-op-sp, standard.scenario.difficulty, guide.scenario.implement-scenario-case]
---

# 场景架构与全生命周期原则

本文描述当前 DBA-Bench 场景从需求到交付的统一结构。实现以当前源码为准：场景模型、运行时
和系统实现位于 `src/scenarios/`，Scenario evaluator 位于 `src/scenarios/evaluation/`，环境和
部署位于 `src/execution/`。不要继续使用旧的 `src/control/scenarios` 或 `src/control/evaluators`
路径作为新实现模板。

## 1. Scenario 与 ScenarioCase

`Scenario` 是一个无状态的场景容器，表达数据库系统、场景身份、描述、稳定有序的 Case 集合，
并根据 Case 返回 `FaultPlan`。它不保存连接、PID、时间戳、运行期对象或上一次运行的结果。

`ScenarioCase` 是一个不可变的评估合同，保存 Case-specific 的 identity、告警、初始状态、
目标状态、背景负载、runtime/resource contract、reference report、evaluator identity 和
难度校准。动态对象、阈值、时间、注入证据、动作历史、workload runner 和最终真值属于
`CaseRun` 或可信运行产物。

两者的新增边界必须明确：

| 需求 | 通常应修改什么 | 不应做什么 |
|---|---|---|
| 新增场景 | 新增一个 `Scenario` 及至少一个 `ScenarioCase`，并完成注册、FaultPlan/Injector、evaluator、正式入口、文档和测试 | 把不同运维问题塞进一个既有 Scenario，或只复制一个旧 Case 改常量 |
| 新增 Case | 既有 Scenario 下新增一个不可变 `ScenarioCase`；必要时扩展共享 evaluator、Injector 配置、workload、入口选择和测试 | 为已有 Scenario 重复创建同名 Scenario，或只改表名、告警和对象名 |

新增 Case 仍然必须有独立 `case_id`、连续 `case_no`、evaluator identity、fault 配置、目标
合同和 recovery。若修改共享实现，必须回归该实现影响到的所有既有 Case。

## 2. 当前模块职责

- `src/scenarios/base.py`：`ScenarioCase`、`CaseRun`、`FaultPlan`、runtime contract 和
  `BaseScenario` 等公共模型；
- `src/scenarios/postgres/<category>/`、`src/scenarios/tidb/<category>/`：系统和分类下的
  Scenario、Case 与真实故障配置；
- `src/scenarios/faults.py`：五阶段 `BaseFaultInjector` 协议；
- `src/scenarios/evaluation/base.py`、`protocol.py`、`diagnosis.py`、`outcome.py`、`safety.py`：统一
  evaluator、结构化提交、DP/OP/SP 和共享 verifier/rule；系统与分类专属 evaluator 放在
  `src/scenarios/evaluation/postgres/<category>/` 或 `src/scenarios/evaluation/tidb/<category>/`；
- `src/scenarios/runtime/orchestrator.py`、`workload_runner.py`、`env_gateway.py`：部署后生命周期、
  workload、Agent loop、评估、恢复和 trace；
- `src/execution/`：PostgreSQL/TiDB 环境、deployment、snapshot 和工具执行；
- `src/workloads/`：跨场景可复用的真实背景负载。

入口脚本只负责选择环境、workload、Agent、Scenario 和 Case，把完整生命周期交给
`Orchestrator.run()`。入口不得另起一套 deploy、inject、evaluate、recover 或 teardown 旁路。

## 3. 从需求到交付

### 3.1 需求与 Case 合同

编码前必须写清：真实运维问题、故障原理、初始状态、目标对象和排除对象、Agent-visible
证据、标准诊断/修复路径、合法修复族、OutcomePass 最终不变量、SP 安全边界、资源合同、
清理所有权、新增目的和难度目标。新场景还要说明为什么它是一个独立 Scenario；新增 Case
要说明相对原 Case 的评估价值。

标准路径是解释性 reference path，不是固定答案。必须把完成任务所需的事实、约束、合法
状态和安全边界公开给 Agent，同时隐藏 ground truth 的内部条件 ID、fixture 变量和直接答案。

### 3.2 实现真实故障

`FaultPlan` 只保存 Injector 类型和完整配置，不保存 Injector 实例或可变运行状态。Injector
必须在真实数据库/系统状态中产生症状，不得只改 Python 标志、伪造指标、篡改工具响应或把答案
塞入注入 evidence。

五阶段签名都只能是 `self, context`：

1. `install`：在新环境创建完整持久故障和基础状态；
2. `activate`：校验持久状态，并在 fault image 启动后恢复运行时症状；
3. `prepare_observability`：让正式工具可见真实证据，并返回 evaluator 所需的 injection evidence；
4. `quiesce`：保存 fault image 前停止运行时资源，只保留可持久化状态；
5. `recover`：移除故障，释放 Case 拥有的连接、会话、线程、进程、文件、配置和数据库状态。

重复运行必须能可靠恢复，状态所有权必须明确。不要添加 `inject()`、`get_name()`、反射、
旧接口适配、默认配置或异常后静默降级。

### 3.3 evaluator 与协议

每个 Case 的 evaluator `scenario_id/case_id` 必须与 ScenarioCase 完全一致；使用统一结构化
`submit`，只提交 `diagnosis`、`outcome`、`summary`。DP/OP/SP 的设计和常见陷阱见
[DP、OP、SP 设计原则](../evaluation/dp-op-sp.standard.md)，实现时不要在分类模块重复造 matcher、
SQL 结果解析、业务真值比较或 safety rule。

先用 `rg` 搜索已有实现，再决定是否提炼公共抽象。优先复用定义行为的模块，例如
`src/database/sql.py`、`src/database/query_results.py`、`src/scenarios/evaluation/outcome.py`、
`src/scenarios/evaluation/safety.py`、`src/scenarios/evaluation/diagnosis.py` 和 `src/workloads/`。只有至少两个
真实消费者且语义一致时才抽象；不要为了兼容旧调用方保留双路径。

### 3.4 入口、测试、实验和文档

正式入口为 `examples/run_<scenario_id>_scenario.py`，要求显式 `--case`，支持结构化 mock
和显式配置的真实 `LLMAgent`。测试至少覆盖 identity/编号、FaultPlan、五阶段 lifecycle、
真实 observability、DP 两种路径、OP 最终状态和合法替代方案、SP 风险、结构化提交、入口和
完整 recovery，并回归受影响的共享 Case。

校准和实验遵循 `Smoke -> Pilot -> Main`：先验证 mock/reference 和环境，再运行 manifest
指定的真实 Agent，最后扩大矩阵。provider、协议、timeout、工具或基础设施失败不能包装成
模型能力失败。

场景合同必须能让读者复现：故障原理（大白话）、标准诊断/修复路径、Agent 可见证据、OP 验收
标准、SP 边界、难度证据、命令、trace、测试和 recovery。所有阻塞 OP 的资源、空间、写放大、
对象数量、时间/RTO、清理或预算条件都要公开基线、单位、阈值、范围、采样窗口和验收证据；
隐藏条件和非核心清理不得单独判定 OP 失败。有效非干净运行交给独立 trace-level LLM judge，
由它阅读完整路径后语义选择一个主类型和二级标签；DP/OP/SP 只作为参考，不能用具体值或组合
机械分类。若有效 LLMAgent 得到 `OutcomePass=False`，先记录 judge 判断是未找出根因还是找出根因
但没有修复，再记录标签、动作、证据、失败结果、最终状态和未满足的不变量，并保留与 evaluator
结果的分歧。

### 3.5 TiDB frozen-history 的程序化历史观察

Frozen-history Case 的场景目标、历史调查语义、干扰窗口和 Agent 证据协议由各 Case 合同与
[TiDB 场景目录](../../catalogs/tidb-scenarios.catalog.md) 的指标历史路径与冻结历史章节定义。本节只补充当前架构对
程序化历史观察的实现边界，不重复定义场景设计目标。

TiDB 的 frozen-history Case 可以声明 `procedural historical observation`，用于评测 Agent 从较长时序中定位
候选窗口、再用同一窗口的日志或 TopSQL/slow-query 证据交叉验证的能力。这是对观察数据面的明确扩展，不是对
真实故障原则的豁免：

- 当前 TiDB 的故障、修复结果、业务真值、配置、锁、拓扑和安全状态仍必须由真实环境产生；trusted
  observation、evaluator、OP 和 SP 永远读取当前真实环境，不能读取 generated history 判断修复成功；
- 每次 run 必须从本次真实 TiDB 环境采集正常阶段和目标故障阶段的指标及声明的记录源；允许的背景拼接、时间平移、
  显式 decoy 和同一 bundle 的变换必须由 Case contract 声明并可复现；不得声称它是连续真实运行了数小时；
- 历史 timeline 必须在 Agent 启动前一次性构造、校验、计算 hash 并冻结。运行期间不得追加 live 样本、替换 provider、
  按查询内容临时修改结果或自动 fallback 到旧 archive；构造失败必须终止 setup；
- Agent 只能通过声明的 historical observation 工具读取 frozen metrics 和 bounded records。不得把 generated history
  注入 Prometheus、伪造 INFORMATION_SCHEMA、拦截并改写任意 SQL，或把物理历史表作为旁路；当前业务/schema/config
  SQL 仍可执行，但受控历史表查询必须明确拒绝；
- trace 保存 seed、history hash、可见范围、窗口角色和来源摘要以支持审计与复现，但 Agent 的工具响应不得泄漏
  target/decoy role、真实/生成来源、capture 时间、block ID、seed 或根因标签。

该能力只适用于能由短时真实 capture 表达的局部历史窗口；数小时容量漂移、内存泄漏和长期单调趋势不得用程序化
拼接伪造。新增 frozen-history Case 必须在场景合同中说明历史观察的边界、负证据、可见窗口、预算和当前状态的真实
验收方式。

## 4. 常见架构错误

- 把动态连接、PID、时间戳或跨运行对象放进 `Scenario`/静态 Case；
- 新增 Case 复制成新 Scenario，或仅替换常量而没有新的评估价值；
- Injector 不产生真实状态，只伪造指标或工具字段；
- 入口复制 Orchestrator 生命周期，导致恢复、trace 或 snapshot 分叉；
- shared evaluator/workload 修改后没有回归既有 Case；
- 用旧 `src/control` 路径、旧协议或兼容适配层指导新代码；
- 为了让模型失败删除必要证据、收紧合法修复或引入不可复现的随机竞争。
- 把程序化历史当成当前状态、在 injector 中伪造历史工具响应，或让历史构造失败后读取 live/旧 archive 继续运行。
