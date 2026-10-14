---
doc_id: standard.persistent-scenario.architecture
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, persistent-scenario, postgres, tidb]
summary: Defines the Persistent Scenario static contract, persistent runtime, event capabilities, ownership, cleanup, and domain boundary.
source_of_truth: contract
related: [standard.persistent-scenario.evaluation, standard.persistent-scenario.difficulty, standard.evaluation.dp-op-sp, guide.persistent-scenario.implement-persistent-scenario]
language: zh-CN
---

# Persistent Scenario 场景架构原则

本文是生产真实性优先的 Persistent Scenario 架构规范；Persistent Scenario 的实现、评审和后续重构均以本文为准。长任务使用一个持久 mailbox session 和一份公开信箱文档；Agent-facing 的 Persistent Scenario 控制面只有一个 `mailbox` 工具，通过 `operation` 选择读取、写入或等待。不产生组合的 `ScenarioPass`；Event 修复 deadline 只作观测，业务交付 deadline 属于服务合同。

配套文档：

- [Persistent Scenario 评估设计原则](../../../standards/persistent-scenario/evaluation.standard.md)
- [Persistent Scenario 难度设计原则](../../../standards/persistent-scenario/difficulty.standard.md)
- [Persistent Scenario 实现指南](../../../guides/persistent-scenario/implement-persistent-scenario.guide.md)
- [DP / OP / SP 设计原则](../../../standards/evaluation/dp-op-sp.standard.md)

## 1. 核心定义

Persistent Scenario 不是多个 bounded Scenario 的串行包装，也不是要求一次 LLM 调用阻塞整个 horizon。它评估的是：

> 在一个持久化数据库环境中，Agent 面对连续、异步、部分可观测且可能相互影响的运维事件时，能否维持业务结果、稳定恢复，并控制自身操作风险。

这个定义包含四个不可删减的约束：

1. **环境持久化**：整个 Persistent Scenario 只部署一次数据库，前序故障和修复产生的状态必须保留。
2. **事件独立到达**：事件由 monotonic timeline 调度，后续事件不等待前序事件处理完成。
3. **会话持久化**：整个 Persistent Scenario 只创建一个 Agent session 和一条持续的 LLM conversation。Agent 通过公开 mailbox 文档在有任务时工作，在空信箱时 idle；新任务追加后由系统唤醒同一会话。
4. **全时间轴验收**：最终结果由整个 Persistent Scenario 的业务服务目标、数据完整性、必要系统状态和全局安全历史决定，不由某个事件的固定修复动作决定。

## 2. Persistent Scenario 与 bounded Scenario 的边界

| 维度 | bounded Scenario | Persistent Scenario |
| --- | --- | --- |
| 被测能力 | 单个问题的诊断与修复 | 持续运维、并发事件处理、业务优先级与状态保持 |
| 环境生命周期 | 一个 CaseRun 一次 setup / teardown | 一个 Persistent Scenario 一次部署，所有事件共享环境 |
| 事件模型 | 一个主要故障计划 | 多个按时间独立到达的 Event |
| Agent 上下文 | 通常是一个有界交互窗口 | 一个持久 mailbox session，跨 idle/wakeup 保留同一 conversation |
| 通过条件 | 单 Case 的 DP / OP / SP | Persistent Scenario 级 DiagnosisPass / OutcomePass / SafePass |
| 结果验收 | Case evaluator | PersistentScenarioEvaluator 与 Persistent Scenario 可信合同 |
| 时间语义 | 固定动作窗口或 turn 边界可以有意义 | Event 响应时间用于观测，业务交付时间按服务合同验收 |

bounded Scenario 可以提供成熟的故障注入能力，但不能成为 Persistent Scenario 的运行时主模型。允许复用的是 `ScenarioCase`、`FaultPlan` 和 injector 所表达的故障能力；禁止复用的是 bounded Scenario evaluator、一次性 `submit`、固定动作窗口以及单 Case OP/SP。

目标依赖方向是：

```text
PersistentScenarioSpec / EventSpec
    -> PersistentScenarioEventCapability
    -> PersistentScenarioTrustedOutcomeContract
    -> PersistentScenarioSafetyPolicy
    -> PersistentScenarioEvaluator
```

Persistent Scenario provider 最终必须直接面向 Persistent Scenario 合同。题库只作机制参考，不要求任何 Event 来自已注册 Case；原生 capability 以自身 ID/version/occurrence 注册。同一 capability 可以重复发生，event_id 唯一即可。旧 scenario_id/case_id 强制引用和 pair 去重均为待删除技术债。

## 3. 静态合同与运行态分离

### 3.1 静态合同

`PersistentScenarioSpec` 描述可审查、可序列化、运行前固定的事实：

- Persistent Scenario 身份、数据库系统、时间范围和 calibration 状态；
- 唯一的环境规格和资源预算；
- OLTP 逻辑事务、OLAP job、HTAP 双侧服务、数据真值及业务交付预算；
- 业务 SLO 与运维风险目标；
- 外部变化的到达时间、重复 occurrence、触发类型、影响范围和有界 activation；
- inspection cadence。

静态合同必须在部署前通过校验。未知字段、重复 ID、越界时间、缺失 objective、资源不足或未注册能力都应直接失败，不能使用默认值继续运行。

### 3.2 运行态

`PersistentScenarioRun` 和 `EventRun` 只记录执行过程中实际发生的事实：

- 环境与 workload 的生命周期；
- 注入开始、成功、失败、释放和 cleanup；
- mailbox task 发布与完成、Agent 状态和 actions；
- 业务事务/job/水位账本、checkpoint、可信 outcome 和 safety snapshot；
- provider failure 与 run validity；
- 最终 evaluation。

静态意图和运行事实不能混写。例如 `start_seconds=300` 只是计划时间，真正的 `injected_at_monotonic` 才是运行证据；配置声明会影响某条 flow，也不能替代 no-agent impact 的实测结果。

## 4. 分层与所有权

### 4.1 System-neutral core

`src/persistent_scenarios/model/`、`src/persistent_scenarios/runtime/`、`src/persistent_scenarios/evaluation/` 和
`src/persistent_scenarios/backend/` 的核心层负责：

- 严格加载和验证 Persistent Scenario 静态合同；
- monotonic timeline 调度；
- Event、session 和 checkpoint 状态机；
- append-only trace；
- provider 协议与失败分类；
- Persistent Scenario 级评估组合。

核心层不能导入 Scenario evaluator，也不能包含 PostgreSQL/TiDB 对象名、SQL 文本或故障特例。

### 4.2 System-specific provider

数据库 provider 负责将通用合同实现为真实系统行为：

- 创建和销毁环境；
- 注册、注入、验证、释放和 cleanup Event capability；
- 运行 workload 与采集 telemetry；
- 生成生产合理的 alert 症状；
- 验证 Event 的真实影响和最终状态；
- 读取可信最终状态和全局安全状态。

Provider 输出必须是结构化事实。核心层根据协议组合事实，不能解析 provider 的自然语言来猜测状态。

### 4.3 Event capability

每个 Event 在进入 Persistent Scenario 前必须拥有显式 capability，至少声明：

- 唯一能力标识及支持的数据库系统；
- 注入前置条件和 bounded activation；
- 资源所有权，包括进程、会话、行、表、文件、容器或 workload；
- 注入成功的可观测证据；
- alert 或 inspection 的可见性合同；
- 外部意图的执行/预防证据及其业务影响观测；
- release 与 cleanup 的幂等边界；
- 与其他 capability 的冲突关系。

Event 编排不能依赖“配置顺序应该没问题”。资源所有权必须能够在静态 admission 阶段发现冲突，例如一个锁事件持有 customer 行，而后续 capability 的 activation 也必须访问同一行。此类组合要么调整设计，要么明确证明 activation 不会被已有故障无限阻塞。

## 5. 持久环境与生命周期

一个有效 Persistent Scenario 按以下顺序执行：

```text
static admission
-> deploy once
-> start workload and telemetry
-> warmup health gate
-> capture baseline and safety baseline
-> run monotonic event timeline
-> keep one mailbox session through idle/wakeup
-> stop new mailbox tasks at horizon
-> stop the persistent Agent session
-> capture final checkpoints
-> final evaluation
-> reverse-order event cleanup
-> environment teardown
```

关键规则：

- warmup 是环境健康准入和上下文采集，不是把单次偶然值变成隐藏评分门槛；
- Event 2 到达不等待 Event 1 被诊断、解决、超时或 cleanup；
- Agent 修复和未解决故障都跨 Event 保留；
- mailbox task 完成只更新公开工作记录，不等于可信恢复，也不等于释放 Event 资源；
- cleanup 只属于基础设施回收，不能提前擦除最终评估所需状态；
- final evaluation 必须发生在 reverse cleanup 之前；
- teardown 无论成功与否都必须有清晰结果，失败直接标记 run invalid，不能把脏环境包装成模型失败。

### 5.1 三种必须分离的时间

| 时间 | 含义 | 是否阻塞后续 Event |
| --- | --- | --- |
| Event arrival | 调度器开始注入并产生可见性 | 否 |
| Incident resolution | 可信 outcome 已满足并完成稳定性验证 | 否 |
| Injector cleanup | Persistent Scenario 评估后回收注入资源 | 否，仅影响 teardown |

将三者合并会把 Persistent Scenario 退化成 bounded Scenario 队列，并制造事件顺序死锁。

## 6. 时间轴、并发与检查点

### 6.1 Monotonic timeline

所有相对时间计算、deadline、latency 和 event ordering 使用 monotonic clock。Wall-clock 只用于展示和跨系统关联，不能驱动调度。

事件到达、Agent action、workload observation、checkpoint 和 provider result 必须携带可排序的 monotonic timestamp。相同 timestamp 下使用 append sequence 保证确定顺序。

### 6.2 Append-only runtime history

以下数据必须 append-only：

- timeline；
- Agent request/action/tool result history；
- mailbox 文档的发布、完成和其他引擎侧状态变更；
- Agent 的数据库 action 与工具结果；
- workload observations；
- event checkpoints 和 safety checkpoints。

状态机可以维护当前视图，但不能覆盖或删除原始证据。Evaluator 只从可信运行事实计算结果，不能依赖执行后被修改的摘要。

### 6.3 Checkpoint

Checkpoint 是对某一时刻可信环境状态的结构化采样，不是 Agent 自报。至少在下列边界采样：

- healthy baseline；
- Event 注入确认后；
- mailbox task 完成后或引擎需要记录可信状态时；
- verification window 到期；
- Persistent Scenario horizon 结束；
- 高风险动作之后。

Checkpoint 采集设施故障应使 run invalid。数据库因故障或 Agent 操作无法响应时，记录可验证的不可用事实并按业务合同评价；不能自动归类为设施故障。无法确定的字段不伪造为通过。

## 7. Agent session 与 mailbox 模型

整个 Persistent Scenario 只创建一个 `session-0001`。它绑定一个持久 Agent 实例和一条持续 conversation；可见运维工作项、周期巡检任务和后续追加的工作都进入同一份 mailbox，不创建新的 Agent、context 或 conversation。

```text
Persistent Scenario start ----------> session-0001 starts and reads mailbox
visible work item ------> generic task appended -------------┐
periodic check ---------> routine task appended --------------┼-> same Agent wakeup
mailbox empty ----------> same session idle ------------------┘
new task appended ------> same conversation resumes
Persistent Scenario horizon --------> stop task publication and signal session stop
```

Mailbox 是公开的结构化控制面，至少包含：

- `pending`：尚未完成的任务；
- `completed`：已完成任务及完成时间；
- `revision`：每次发布或完成后的单调版本；
- append-only history：任务状态变化和时间。

Agent-facing Persistent Scenario 控制面固定为一个 `mailbox` 工具：

- `mailbox(operation="read")`：读取当前 mailbox，同时查看未完成和已完成任务；
- `mailbox(operation="write", task_ids=[...], report={...})`：把一个或多个指定任务移到 `completed`，并为这批工作保存一份结构化报告；
- `mailbox(operation="wait")`：在没有未完成任务时挂起当前 Agent，直到新任务追加或 Persistent Scenario 结束。

任务 payload 只包含生产监控中合理可见的标题、描述、症状、严重性和类别。它不包含任务来源、`task_type`、`event_id`、`scenario_id`、`case_id`、注入器私有状态或 evaluator 真值。Agent 不需要也不能通过控制面区分不同来源的任务。

`mailbox(operation="write")` 不验证数据库状态，也不触发恢复检查。`report` 采用与 bounded Scenario `submit` 相同的结构化形状：`diagnosis.conditions`、`outcome.changes`、`outcome.verification` 和 `summary` 为必填字段，`outcome.plan` 可选。仅当合同明确要求业务事故解释时，相关报告作为该事故 diagnosis matcher 的输入，不按 Event 一一映射；它不是 trusted database evidence，也不是 Outcome/Safety 结果。周期巡检任务只保存报告，不创建 diagnosis claim。一次写入可以完成多个任务，控制面不按任务来源设置不同的完成路径。

Agent 每次 activation 首先调用 `mailbox(operation="read")`。有 pending task 时使用普通数据库工具处理自己选择的任务，完成一个或多个后调用 `mailbox(operation="write", task_ids=[...], report={...})`；没有 pending task 时调用 `mailbox(operation="wait")`，由系统挂起这条相同 conversation。新任务追加后，系统唤醒相同 session 和相同 conversation，并继续读取实时 mailbox。既有上下文 compaction 仍按 Agent 层已有实现执行，不通过新建 session 绕过上下文管理。

`agent_sessions[].status` 表示 session 生命周期，使用 `running`、`completed` 或 `failed`；`agent_sessions[].state` 表示当前工作态，使用 `active`、`idle` 或 `woken`。`mailbox(wait)` 开始阻塞前必须记录 `idle`，被新任务或结束信号唤醒后记录 `woken`，下一次处理开始时记录 `active`。

运行中不存在第二个 Agent session。控制面只校验唯一 session、操作参数、任务 ID、任务状态和报告结构；未知任务 ID、重复完成、带未完成任务等待或缺少报告直接报协议错误。Mailbox 是信息通知和工作记账机制，不是最终评判指标。

## 8. Alert 与 inspection 可观测性

### 8.1 Alert Event

Alert 只呈现监控系统在生产环境中合理产生的症状，例如业务错误率、等待数、资源异常或受影响服务。Event 影响确认后，引擎把这些内容整理成一个普通 mailbox work item。Agent 只看到工作项本身，不知道它是由什么内部来源产生的。Alert 不得直接包含：

- 根因名称；
- 精确 blocker PID、application name 或待终止对象；
- 标准修复 SQL；
- 唯一正确的操作顺序；
- evaluator 私有字段。

Alert 是否足以触发排查，应通过真实 LLM pilot 校准；“不泄漏答案”不等于故意隐藏所有有效线索。

### 8.2 Inspection Event

Inspection Event 不发布针对某个 Event 的提示。调度器只按 cadence 追加普通例行检查 task；Agent 使用日常数据库工具自行观察当前系统，是否采取动作由 Agent 自己决定。完成 task 只表示 Agent 认为这一项工作已经处理完，不代表引擎认可某个发现或修复。

最终是否恢复仍由可信 outcome、业务 SLO 和安全规则读取真实数据库状态判断。自然语言描述、任务完成记录或关键词不能替代这些检查。

Inspection cadence 是发现机会的设计参数，不是用来缩短 Agent 时间预算的难度开关。

## 9. 最终评估与 cleanup

Persistent Scenario horizon 结束后，调度器停止创建新 mailbox task，唤醒并停止唯一持久 session，等待已开始的 bounded 操作到达协议边界。随后采集最终 workload、event outcome 和 safety checkpoint，执行 PersistentScenarioEvaluator，最后按 Event 实际 activation 的逆序 cleanup。

逆序 cleanup 的原因是资源依赖，而不是把 cleanup 当成修复。每个 capability 必须只回收自己拥有的资源，不能撤销 Agent 合法修复，也不能重置整个数据库来掩盖污染。

最终只报告三个相互独立的通过结果：

```text
DiagnosisPass = 明确要求的业务事故解释正确；默认可为 N/A
OutcomePass   = ServiceObjectivesPass and DataIntegrityPass and RequiredStatePass
SafePass      = PersistentScenarioSafePass
```

不产生组合的 `ScenarioPass`。具体语义见 [Persistent Scenario 评估设计原则](../../../standards/persistent-scenario/evaluation.standard.md)。

## 10. Trace 与 run validity

完整 trace 至少需要保存：

- source spec、实际运行 spec、run ID、代码版本和资源租约；
- deploy、warmup、baseline、timeline、final evaluation、cleanup、teardown；
- 每个 Event 的 activation handle、可信证据、checkpoint 和 cleanup；
- 唯一 mailbox session 的输入、`active`/`idle`/`woken` 状态、action、工具结果和终止原因；
- 一份永远不压缩的原始 conversation，以及每次 compaction 后新增的 Agent 视角 phase conversation；
- mailbox 当前视图及 append-only 状态变更 history；
- 每个 workload observation 和 telemetry completeness；
- DP / OP / SP 的证据引用和 failure classification。

Provider 实现、工具传输设施、部署、trace recorder 或 telemetry 采集设施失效时，run 必须标记为 invalid，并保留明确分类与上下文。数据库业务超时、合法取消、连接拒绝以及 Agent 导致的数据库不可用，应由外部可信账本记录为业务结果，不能因此抹掉 OP/SP 后果。Invalid run 的三个 pass 均为 `None`；禁止将基础设施错误记成 `DiagnosisPass=False`、`OutcomePass=False` 或 `SafePass=False`。

## 11. 当前实现债务

以下内容是现状，不是应继续复制的模式：

| 位置 | 当前问题 | 目标 |
| --- | --- | --- |
| `src/persistent_scenarios/evaluation/evaluator.py` / `src/persistent_scenarios/evaluation/diagnosis.py` | 公共层不能定义具体故障的根因语义 | 由合同明确要求的业务事故解释 matcher 判定，默认 N/A，不合取所有 Event |
| `src/persistent_scenarios/backend/postgres/registry.py` | 依赖 `SCENARIOS_BY_ID`、`ScenarioCase`、`FaultPlan` 并按 ID 分派 | 独立的 PersistentScenarioEventCapability 注册表 |
| `src/persistent_scenarios/backend/postgres/capabilities/` | 部分 outcome 依赖 action 文本、固定 SQL、对象名和 `repair_action_observed` | 仅验收最终状态、业务真值和公开不变量 |
| `PostgresEventProvider.agent_alert` | 部分 alert 泄漏精确 blocker 和修复顺序 | 只暴露生产合理症状 |
| `src/persistent_scenarios/evaluation/slo.py` | 部分 control 阈值直接绑定单次 warmup | 使用公开、稳定、经 calibration 的阈值；warmup 只做健康准入与上下文 |

处理这些债务时直接迁移到目标合同，删除旧路径和硬编码；不要增加兼容层或双重 evaluator。

## 12. 架构评审清单

合入 Persistent Scenario 前必须回答：

- 是否只部署一次环境，并在最终评估前保留所有故障和修复状态？
- 后续 Event 是否无需等待前序 Event resolution、deadline 或 cleanup？
- 每个 capability 是否有 bounded activation、资源所有权、可信 outcome 和 cleanup？
- Event 组合是否通过资源冲突 admission，而不是依赖幸运顺序？
- alert 是否只暴露症状，inspection 是否必须通过真实工具发现？
- 是否始终只有一个 mailbox session，且新任务唤醒时复用同一 conversation？
- timeline、action、checkpoint 和 telemetry 是否 append-only 且可追溯？
- Persistent Scenario evaluator 是否独立于 bounded Scenario evaluator？
- final evaluation 是否在 reverse cleanup 之前？
- 是否区分评测设施失败（invalid）与数据库业务失败、Agent 破坏（有效业务/安全后果）？

任何一项无法给出代码和 trace 证据，都说明该 Persistent Scenario 尚未达到架构准入标准。

## 13. 生产因果、重复与端到端目标

先定义生产 workload/业务交付，再设计外部变化；没有必须复用题库或事件配额。同一故障可多次发生，保留 Agent 修复和单会话状态。后续输入按时到达，但症状是否出现取决于真实数据库状态：保护措施成功预防、其他事件抵消症状都是有效结果，需要证据而非吞掉注入异常。

事件可以共享资源并级联，admission 验证真实权限/资源和有界执行，不用“长事务必须先于锁”掩盖架构限制。注入器不能不断恢复坏配置或重建被合法修复的 blocker 以保证故障存活。

RequiredStatePass 面向最终业务接续、交付物与必要 GUC，禁止 all(Event.outcome) 和 regression_count==0。历史损失进 SLO，恢复后的正常负载继续验证接续能力。DP 不按注入事件要求逐项应答；多根因可由一个事故解释覆盖。

新五实例设计、淘汰名单和实现差距见 [生产型五实例方案](../../../persistent-scenarios/postgresql/production-portfolio.contract.md)。真实副本型 HTAP 需要一个持续拓扑而非伪造 lag；一次部署可以包含多个明确角色的数据库节点。
