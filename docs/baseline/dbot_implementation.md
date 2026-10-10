# D-Bot Baseline 实现文档

## 实现原则

本实现以 `DB-GPT/` 开源代码为优先依据，而不是以论文描述优先。若论文和开源代码有差异，以开源代码中的实际运行路径为准。

上游 DB-GPT 的 D-Bot 主路径是：

```text
run_diagnose.py / batch_main.py
  -> MultiAgents.from_task(config.yaml)
  -> DBAEnvironment.step()
  -> ReporterAgent initialize_report 生成 anomaly description / title
  -> RoleAssignerAgent 选择专家
  -> VerticalDecisionMaker 并发运行选中的 SolverAgent
  -> 每个 SolverAgent 内部用 UCT_vote_function 做 Thought/Action/Action Input 轨迹搜索
  -> 每个专家输出 root cause / solutions / knowledge
  -> roundtable review
  -> ReporterAgent refine root cause / labels / solutions / citations
```

因此 DBA-Bench 的 D-Bot baseline 现在实现为 `dbot_code` 模式：在 `BaseAgent` 的逐 turn 接口内适配 DB-GPT 的多专家诊断流水线。专家内部不是固定脚本，而是在 `DbotAgent` 内保留 `Thought / Action / Action Input / Observation` 轨迹搜索：LLM 选择 PGEnv 当前 profile 暴露的工具，Orchestrator 执行对应 DBA-Bench action，observation 回写后继续下一步。

## DB-GPT 创新点边界

当前实现把 DB-GPT 的方法贡献和工具链拆开：

| 类别 | 是否属于 D-Bot 方法核心 | 当前实现 |
|---|---:|---|
| RoleAssigner 根据 anomaly description 招募专家 | 是 | `DbotAgent._select_experts()` + `DBOT_ROLE_ASSIGNER_PROMPT` |
| 多专家独立诊断 | 是 | `DbotAgent` 顺序运行每个 selected expert 的独立搜索状态 |
| UCT trajectory search | 是 | `DbotAgent` + `mcts.py` 保留 `Thought -> Action -> Action Input -> Observation` tree、softmax UCT branch selection、candidate vote、value backpropagation |
| Reflection | 是 | 每条 terminal candidate 后执行 expert reflection prompt |
| Candidate vote | 是 | 每轮 simulation 后按 DB-GPT vote prompt 更新 terminal 和 ancestor value |
| Roundtable review | 是 | `DBOT_ROUND_TABLE_PROMPT` 顺序审核全部专家结果 |
| ChiefDBA / Reporter 汇总报告、标签、citation marking | 是 | reporter 初始化 anomaly description/title，最终 refine root cause/solutions/labels/citations |
| `whether_is_abnormal_metric` / `match_diagnose_knowledge` / `optimize_index_selection` / `finish` / `mark_citations` / `submit` | 不是算法创新点本身，是上游工具链和交互协议 | `PGEnv(tool_profile="db_gpt")` 暴露 DB-GPT semantic tools 和 benchmark `submit`；`DbotAgent` 在专家阶段额外注册内部虚拟 `finish`，报告阶段用内部虚拟 `mark_citations` 提交标注后的两段文本，最终才向 Orchestrator 返回 `submit` |

因此实验时通过 PGEnv 的工具 profile 比较两类暴露方式：

- `PGEnv(tool_profile="db_gpt")`：专家 LLM 看到 DB-GPT semantic tools；这些工具是 PGEnv 的 `@Tool` 方法，schema/help/native tool calling 都走现有环境工具机制。
- `PGEnv(tool_profile="no_knowledge" / "general_knowledge" / "hierarchical_knowledge")`：专家 LLM 直接看到该 PGEnv profile 下的全部原生工具；D-Bot 算法流程仍然是 role assignment、多专家、UCT、roundtable 和 reporter。

## 与旧实现的冲突和处理

旧 DBA-Bench D-Bot 实现偏向论文复现，存在以下与 DB-GPT 开源代码冲突的机制：

| 旧机制 | DB-GPT 开源代码事实 | 当前处理 |
|---|---|---|
| `dbot_tree` 作为外部持久树，每个 Orchestrator turn 扩展一个环境 action | 上游树搜索在每个 `SolverAgent` 内部运行，搜索的是 `Thought -> Action -> Action Input -> Observation` 轨迹 | 删除外部持久 benefit tree，改为专家内 DB-GPT turn-based trajectory search |
| `BenefitScorer` 的 instant/long-term/UCT 三分量评分 | 上游 `tree_node` 只有投票产生的 `values`，选择由 `softmax(child.compute_weight(), epsilon_new_node)` 决定 | 删除 `BenefitScorer` / `Reflector` |
| `dbot_collab` 自造 CPU/QUERY/STORAGE/CONFIG 四专家面板 | 上游从知识库专家名动态选择，如 `CpuExpert`、`QueryExpert`、`IndexExpert` 等 | 改成 DB-GPT 专家名体系 |
| `ReadOnlyEnvProxy` 让 D-Bot 侧绕过 Orchestrator 模拟环境 | 上游工具在 DB-GPT runtime 内执行；DBA-Bench 要保持统一工具边界 | 删除执行代理；DB-GPT semantic tools 注册为 PGEnv `@Tool` 方法，由 Orchestrator 调度 |
| native function calling 优先 | 上游 prompt 使用 `Thought / Action / Action Input` 文本协议 | 同时支持文本 ReAct 和 SDK native tools；工具 schema 均来自 PGEnv，不在 D-Bot 内维护第二套工具说明 |
| LLM 自由决定 `query_metrics/execute_sql/manage_instance` | 上游专家默认看到 DB-GPT semantic tools | 由 `PGEnv.tool_profile` 决定暴露 DB-GPT semantic tools 还是 PGEnv 原生工具 |
| 知识库是任意文本关键词 RAG | 上游知识按专家知识库组织，记录含 `cause_name/desc/metrics/steps/source` | `DbotKnowledge` 改为专家知识条目加载和检索 |

## 当前组件

```text
src/agents/baselines/dbot/
  agent.py       DbotAgent 与 ExpertSolver，DB-GPT code-first pipeline adapter；包含角色选择、专家轨迹搜索、roundtable 和报告状态
  tools.py       schema-derived ReAct helper、内部虚拟工具 schema（finish / mark_citations）与 TiDB 工具面判定
  prompts.py     DB-GPT role assigner、expert、roundtable、report prompts
  types.py       DbotToolStep / ExpertDiagnosis / DbotReport
  knowledge.py   expert knowledge loader and retriever
  mcts.py        DB-GPT trajectory tree helper，不再是外部 remediation MCTS
  experts.py     DB-GPT expert metadata
```

## 运行模式

仅支持：

```python
DbotAgent(mode="dbot_code", use_native_tools=False)
DbotAgent(mode="dbot_code", use_native_tools=True)
```

旧模式 `dbot_prompt`、`dbot_rag`、`dbot_tree`、`dbot_collab` 会直接报错。这样可以避免旧论文优先语义被误用。

工具暴露方式由 PGEnv 控制，不由 DbotAgent 维护：

```python
PGEnv(tool_profile="db_gpt")       # DB-GPT semantic tools
PGEnv(tool_profile="no_knowledge") # PGEnv 原生工具，无知识库
PGEnv(tool_profile="general_knowledge")
PGEnv(tool_profile="hierarchical_knowledge")
```

`use_native_tools=True` 时，Orchestrator 把 `env.get_tool_schemas()` 下发给 DbotAgent，DbotAgent 再通过 `LLMAgent.set_tools()` 把 schema 放进 SDK 的 `tools` 参数；工具用法不写进 system prompt。`use_native_tools=False` 时，D-Bot 仍使用 `Thought / Action / Action Input` 文本协议，但可用工具列表从同一份 schema 派生。专家诊断阶段会过滤全局控制工具 `submit/exit`，并追加内部虚拟工具 `finish`；最终报告阶段才返回 DBA-Bench 全局 `submit`。

## 工具暴露与映射

### `PGEnv(tool_profile="db_gpt")`

| DB-GPT 工具 | PGEnv 执行 | 说明 |
|---|---|---|
| `whether_is_abnormal_metric` | PGEnv 内调用 `query_metrics(...)` | 复现上游专家先查核心指标的约束 |
| `match_diagnose_knowledge` | PGEnv 内聚合多个 `query_metrics(...)` 和可选 `query_knowledge_base(...)` | 按上游专家名规则选择 `cpu/io/memory` metric prefix，聚合系统指标、`topsql`、`slow_queries` 和知识库 |
| `optimize_index_selection` | PGEnv 内执行多条 `execute_sql(...)` | 收集 workload、schema、column statistics、已有索引和 `hypopg` 可用性证据 |
| `finish` | DbotAgent 内部虚拟动作 | expert diagnosis 阶段结束当前 simulation，并保存 `diagnose` / `solution` / `knowledge` payload；不进入环境 action history |
| `submit` | DBA-Bench 全局控制动作 | 只在 report 阶段作为真实 benchmark submit 返回给 Orchestrator |

### PGEnv 原生 profiles

| Profile | 暴露给 SolverAgent 的工具 |
|---|---|
| `no_knowledge` | `query_metrics`、`execute_sql`、`manage_instance`、`read_log`、`help`、`submit`、`exit` |
| `general_knowledge` | `no_knowledge` + `query_knowledge_base` |
| `hierarchical_knowledge` | `no_knowledge` + typed `query_knowledge_base` |

这让实验可以区分“DB-GPT 的多专家 UCT 诊断流程”与“DB-GPT semantic tools”各自的贡献，而且无需在 D-Bot 内维护第二套 DBA-Bench 工具清单。

## Expert Trajectory Search

DB-GPT 上游 `SolverAgent.step()` 会运行 `UCT_vote_function.start(simulation_count=2, epsilon_new_node=0.3, choice_count=1, vote_candidates=2, vote_count=1, single_chain_max_step=24)`。DBA-Bench 不能在 agent 内直接执行环境工具，所以当前实现采用逐 turn 适配：

1. `DbotAgent` 为当前 expert 维护 DB-GPT trajectory tree 和候选轨迹；
2. expert LLM 输出 `Thought / Action / Action Input`，或在 native mode 下调用 SDK tool；
3. `Action` 必须属于 expert tool schema：当前 PGEnv profile 工具去掉 `submit/exit` 后再加内部 `finish`；
4. 非 `finish` action 原样作为环境 action，由 Orchestrator 执行；
5. observation 回写到 trajectory 的 `Action Input` 节点；
6. expert diagnosis 阶段调用 `finish` 或达到单链步数上限后形成 terminal candidate，调用 reflection prompt；
7. 每轮 simulation 结束后执行 DB-GPT 式 candidate vote，把 value 回传到 terminal 和 ancestor 节点；
8. 下一轮 simulation 从 root 按 DB-GPT 的 `softmax(child.compute_weight(), epsilon_new_node)` 随机采样，选择复用已有分支或扩展新分支；vote 候选也按 DB-GPT 先随机 shuffle 再取 `vote_candidates` 个；
9. 最终按 terminal node 累计 value 选择 trajectory。

### Prompt 预算

上游只规定了搜索机制，没有规定每一步 prompt 里要重发多少历史。适配层按下面的规则控制 prompt 体积，完整证据仍保留在 `DbotToolStep.observation`、`ExpertDiagnosis` 和 trace 导出里：

- trajectory tree 的 `Action Input` 节点只写紧凑的 `db_gpt_observation`（环境工具和 `whether_is_abnormal_metric` 的结果文本上限 1200 字符），不写环境原始返回；
- expansion prompt 的 former candidates 和 vote prompt 使用候选摘要：工具调用序列 + `finish` 的 `diagnose/solution/knowledge`；expansion prompt 的 reflection 只出现在独立的 reflections 段，不再随候选重复；
- 环境工具 step 只产生一条 citation（由 `_prepare_expert_diagnosis` 生成），不再额外写入 `knowledge_items`。

## Expert 输出

DB-GPT 上游 `SolverAgent.step()` 在 UCT 工具轨迹结束后，会再次调用 LLM：

- `expert_root_cause`：只分析根因，不写解决方案；
- `expert_solution`：只写解决方案，不重复根因。

DBA-Bench 适配层保持这个行为。两个 prompt 只带 vote 选中的 candidate trajectory（含紧凑 observation），不再附带全部步骤的 diagnosis process；如果专家 LLM 返回空 root cause 或空 solution，直接报错，不生成本地默认建议。

## Roundtable 与 Reporter

DB-GPT 上游会先让 `ReporterAgent.initialize_report()` 根据原始 alert 生成 anomaly description 和 title；role assignment 使用生成后的 anomaly description。随后会把所有专家诊断摘要广播给每个专家，再逐个执行 cross review；每个已生成的 review 会追加到后续专家和 reporter 的消息里。DBA-Bench 适配层保持这个信息流：

- role assignment、expert diagnosis 和 final report 使用 reporter 生成的 anomaly description；
- final report title 使用 reporter 生成的 title；
- 每个 roundtable prompt 都包含全部专家诊断上下文（selected trajectory 截取末尾 1500 字符）；
- 后续专家的 roundtable prompt 会包含已经生成的 review advice；
- final report 的 refine root cause / refine solution prompt 会包含 roundtable reviews、citations 和 topMetrics；工具级 diagnosis process 只保留在报告对象和 trace 中，不进入 reporter prompt；
- 若有 citations，Reporter 通过内部虚拟工具 `mark_citations`（与专家阶段的 `finish` 同一种机制）一次性提交标注后的 `root_cause` 和 `solutions` 两个参数：native mode 走 SDK tool calling，文本 mode 走 ReAct `Action / Action Input`；未调用该工具、调用多于一次或字段缺失/为空直接报错。

## 验证

在仓库根目录运行：

```bash
PYTHONPATH=$PWD conda run -n aiops pytest tests/test_dbot_agent.py tests/test_dbot_mcts.py
PYTHONPATH=$PWD conda run -n aiops pytest tests/test_andromeda_agent.py tests/test_dbaiops_agent.py
PYTHONPATH=$PWD conda run -n aiops python tests/test_mock_llm.py
```

当前验证覆盖：

- role assignment 必须解析出 DB-GPT 专家名，空选择直接抛错；超过 `max_hired_experts` 时按回复中的出现顺序裁剪，保留 role assigner 的优先级；
- reporter 初始化会先生成 anomaly description / title，并进入 role assignment 和 final report；
- expert diagnosis 由 DB-GPT-style `Thought / Action / Action Input` 输出选择工具，不再固定顺序；
- tool observation 写入 `ExpertDiagnosis`；
- `match_diagnose_knowledge` 按 DB-GPT 的 `cpu/io/memory` metric prefix 规则聚合系统指标、workload、slow queries、专家知识和 topMetrics；
- `PGEnv(tool_profile="db_gpt")` 暴露 DB-GPT semantic tools，`PGEnv(tool_profile="no_knowledge")` 暴露 PGEnv 原生工具；
- `optimize_index_selection` 由 PGEnv 收集 workload、schema、column statistics、已有索引、`hypopg` 可用性证据，不再查询 `pg_stat_user_indexes` 或正则生成伪索引建议；
- D-Bot schema 校验来自 PGEnv tool schemas，不再维护 `tool_mode` 或私有 DBA-Bench 工具列表；
- expert trajectory search 覆盖 terminal candidate、DB-GPT stochastic branch selection、random vote candidates、vote value 回传和 value-based final selection；
- expert root cause / solution 由 LLM 从工具轨迹生成，空输出直接抛错；
- roundtable review 使用全部专家诊断上下文，并把已生成 review 传给后续专家和 ChiefDBA report；
- 旧 `dbot_tree` 被显式拒绝，native tools 通过现有 `LLMAgent.set_tools()` / SDK `tools` 参数支持；
- native mode 下模型未返回 tool call、退回文本 ReAct 解析时，user/assistant 消息同样成对写入 conversation，供 `token_accounting` 重放；
- trajectory tree 只存紧凑 observation，former candidates / vote 使用候选摘要，reporter prompt 不含 diagnosis process，citation marking 通过 `mark_citations` 工具的两个参数提交（文本 mode 和 native mode 各有用例）；
- DB-GPT trajectory tree helper 保留 `Thought/Action/Action Input/Observation` 结构。
