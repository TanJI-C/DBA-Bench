---
language: zh-CN
---

# Panda Baseline 实现文档

## 论文概述

**论文**: "Panda: Performance Debugging for Databases using LLM Agents" (AWS AI Labs)

**核心思想**: 通过 Context Grounding 为预训练 LLM 提供上下文，使其生成针对特定数据库问题的可操作诊断建议，而非泛泛的通用建议。

**论文的 5 个组件**:
1. Question Verification Agent (QVA) — 过滤无关查询
2. Grounding Mechanism — 文档检索 + T2T + 上下文聚合
3. Verification Mechanism — NLI 验证 + 来源归因
4. Feedback Mechanism — 向量存储反馈缓存
5. Affordance Mechanism — 影响估计 + 高风险标记

---

## 1. Grounding Mechanism（上下文构建）

### 1.1 论文算法

**Document Retriever**:
- 使用 embedding 模型对用户查询和文档库（troubleshooting docs + 历史工单）进行向量化
- 通过 cosine 相似度检索 top-K 相关文档
- 将长文档拆分为 chunks，仅保留 top-3 相关 chunks

**Feature Extractor (Telemetry-to-Text)**:
- 从提供的指标名称列表中，通过 embedding 相似度识别 top-K(K=3) 相关指标
- 查询数据湖获取原始时间序列（默认最近 24 小时）
- 使用 change point detection 算法将时间序列分为"问题区间"和"基线区间"
- 提取可解释特征: trend, seasonality, mean, p95, correlation score
- 识别异常指标（至少一个统计量异常的指标）
- 识别异常 SQL 查询（至少一个查询统计量异常的 SQL）
- 收集异常 SQL 的原始语句 + Database/Information Schema

**Context Aggregator**:
- 将所有提取的特征存储为 JSON 结构化文本
- 与检索到的文档和工单合并
- 限制 prompt 大小: 仅保留 top-3 相关文档 chunks + top-3 异常 SQL

### 1.2 我们的实现

**文件**: `src/control/baselines/panda_grounding.py`

**PandaDocumentRetriever**:
- 使用 `sentence-transformers` (all-MiniLM-L6-v2) 进行 embedding
- 文档加载: 支持 .txt/.md/.json 文件，按段落分块
- 检索: cosine 相似度 top-K
- 降级: 无 sentence-transformers 时使用关键词匹配（词重叠计数）

**PandaTelemetryToText**:
- `extract_features(metric_name, values)`: 对单个指标提取特征
  - Trend: 前半段均值 vs 后半段均值，relative_change > 0.15 判定为 increasing/decreasing
  - Mean / P95: numpy 统计计算
  - Change Points: 滚动均值比较，阈值 1.5*std
  - Seasonality: 自相关检测（lag = len/4）
- `compute_correlations(features)`: 跨指标 Pearson 相关性（|r| > 0.7 视为相关）
- `identify_problematic_metrics(features)`: 识别趋势异常或高相关的指标

**PandaContextAggregator**:
- 将 alert + telemetry_text + documents + schema_info + feedback 聚合为 JSON prompt

### 1.3 与论文的差异

| 方面 | 论文 | 我们的实现 | 原因 |
|------|------|-----------|------|
| 指标选择 | embedding 相似度从文档中识别 top-3 相关指标 | 预定义标准指标列表（cpu, memory, slow_queries 等），全部收集 | DBA-Bench 环境指标有限且已知，无需动态选择 |
| 时间序列来源 | 查询数据湖获取 24h 原始数据 | 通过 `query_metrics` API 获取环境返回的数据 | 适配 Orchestrator 的 tool dispatch 机制 |
| Change Point 算法 | 引用 [21] 的专用算法 | 滚动均值比较 + 1.5σ 阈值 | 轻量实现，无外部依赖 |
| 异常 SQL 识别 | 基于查询统计量异常检测 | 依赖 `slow_queries` 指标 + LLM 分析 | 环境 API 不直接暴露 per-query 统计 |
| 文档来源 | 2.5K troubleshooting docs + 历史工单 | 可配置的本地文档路径（knowledge_paths） | Benchmark 环境无 AWS 文档库 |

---

## 2. Verification Mechanism（验证机制）

### 2.1 论文算法

**Answer Verification (NLI)**:
- 将验证问题建模为 Natural Language Inference (NLI) 任务
- Hypothesis = 生成的诊断答案
- Premise = 检索到的文档和工单（NOT 工具执行结果）
- LLM 作为 verifier 产生标签: accept / reject / neutral
- 如果 reject 或 neutral: 重新运行生成过程获取新答案并验证
- K=3 次失败后输出失败消息 + 相关文档列表
- 工单从展示给用户的文档中移除（含敏感数据）

**Source Attribution**:
- 验证通过后，提供检索到的文档段落作为参考来源
- 将输出和参考段落分割为单独句子
- 如果输出句子与参考段落逐字匹配，提供内联引用 [s_N]

### 2.2 我们的实现

**文件**: `src/control/baselines/panda_verification.py`

**PandaVerifier**:
- `verify(hypothesis, retrieved_docs, telemetry_summary)`:
  - Premise = 检索到的文档（`retrieved_docs`）+ 遥测摘要文本
  - Hypothesis = agent 生成的 root_cause 诊断
  - 构造 NLI prompt 让 LLM 判断 entail / contradict / neutral
  - 解析 LLM 响应提取 verdict + reasoning
- 重试逻辑在 `PandaAgent.get_next_input()` 中实现为 while 循环:
  - 验证失败 → 向 LLM 追加 retry prompt → 重新生成诊断 → 再次验证
  - 最多重试 K=3 次

**PandaSourceAttribution**:
- `attribute(output_text, source_docs)`:
  - 将输出文本按句号分割为句子
  - 将每个源文档按句号分割为句子
  - 计算输出句子与源文档句子的相似度（embedding 或词重叠）
  - 相似度超过阈值时添加内联引用 `[s_N]`
  - 降级: 无 sentence-transformers 时使用词重叠比例

### 2.3 与论文的差异

| 方面 | 论文 | 我们的实现 | 原因 |
|------|------|-----------|------|
| Premise 构成 | 检索文档 + 历史工单 | 检索文档 + 遥测摘要文本 | 无工单数据源，用 telemetry summary 补充 |
| 失败后行为 | 输出失败消息 + 相关文档列表 | 用尽重试后仍提交最后一次生成的诊断 | Benchmark 需要 agent 始终提交结果以便评分 |
| 归因粒度 | "taken verbatim"（逐字匹配） | 词重叠比例 > 0.3 或 embedding 相似度 > 0.7 | 逐字匹配过于严格，LLM 会改写表述 |
| 工单过滤 | 展示给用户时移除工单（含敏感数据） | 不区分文档和工单 | Benchmark 环境无敏感工单数据 |

---

## 3. Feedback Mechanism（反馈机制）

### 3.1 论文算法

- 用户对每个生成的响应提供二元反馈: "Helpful" 或 "Not Helpful"
- 反馈 + 用户查询 + 响应存储在向量存储中，以用户查询的 embedding 为索引
- 生成新响应时，通过 embedding 相似度检索 top-K 相似的历史响应
- 检索规则: 至少 1 个、至多 3 个正面反馈 + 至少 1 个、至多 3 个负面反馈
- 作为 few-shot in-context learning 示例加入 prompt

### 3.2 我们的实现

**文件**: `src/control/baselines/panda_feedback.py`

**PandaFeedbackStore**:
- 存储 `FeedbackEntry` 对象（query, actions_taken, observations, outcome）
- `store(entry)`: 存储条目 + 计算 embedding（如可用）
- `store_interaction(query, actions, observations, outcome)`: 便捷方法
- `retrieve_similar(query, top_k)`:
  - Embedding 路径: cosine 相似度检索，区分 positive/negative
  - Keyword 路径: 词重叠计数（含停用词过滤）
- `get_recent(n)`: 获取最近 N 条交互记录

### 3.3 与论文的差异

| 方面 | 论文 | 我们的实现 | 原因 |
|------|------|-----------|------|
| 反馈来源 | 用户显式提供 "Helpful/Not Helpful" | 自动记录每次交互，outcome 字段标记结果 | Benchmark 无人工反馈环节，改为自动记录 |
| 存储介质 | 持久化向量存储 | 内存中 List + numpy array | 单次运行场景，无需持久化 |
| 检索策略 | 至少1至多3正面 + 至少1至多3负面 | 同论文: positive[:top_k] + negative[:top_k] | 忠实复现 |
| Embedding 模型 | text-embedding-ada-002 (OpenAI) | all-MiniLM-L6-v2 (sentence-transformers) | 本地运行，无 API 成本 |

---

## 4. Affordance Mechanism（可供性机制）

### 4.1 论文算法

**Impact Estimation**:
- 目标: 估计执行某个修复操作后数据库性能的变化量
- 两种方式:
  - Generic（不精确）: 从检索文档和工单中推断类似数据库的通常影响
  - Specific: 使用外部行为模型预测性能变化（如 OtterTune, MB2）
- 论文当前主要依赖 Generic 方式
- 对重要操作（实例类型变更、引擎版本变更等）使用简单统计行为模型

**High-Risk Action Flagging**:
- 维护一个先验的高风险操作列表（DROP, DELETE, 改变隔离级别等）
- 如果推荐中包含高风险操作，在输出中高亮标记

### 4.2 我们的实现

**文件**: `src/control/baselines/panda_affordance.py`

**PandaAffordance**:
- `assess_action(action, context)`:
  - 规则层: 基于 SQL 模式和 API 类型快速分类风险等级
    - `query_metrics`, `read_log` → no-risk, 始终通过
    - `execute_sql` + SELECT/EXPLAIN → low-risk, 通过
    - `execute_sql` + DDL (CREATE INDEX, VACUUM, ANALYZE) → medium-risk
    - `execute_sql` + DROP/DELETE/TRUNCATE/ALTER → high-risk
    - `manage_instance` + restart/stop/reboot → high-risk
  - LLM 层: 对 medium/high-risk 操作调用 LLM 估计具体影响
    - 输入: 操作描述 + 当前上下文（遥测 + 文档）
    - 输出: 预期影响描述 + 风险评估
  - 启发式层: LLM 不可用时的回退估计
    - CREATE INDEX → "May cause brief lock, improves query performance"
    - VACUUM → "Reclaims dead tuple space, brief I/O spike"
    - restart → "Service interruption 10-30s, clears all connections"
- `filter_actions(actions, evidence_count, context)`:
  - 过滤掉 high-risk 且证据不足的操作
  - `require_evidence_for_high_risk`: 高风险操作需要至少 2 条证据支持

### 4.3 与论文的差异

| 方面 | 论文 | 我们的实现 | 原因 |
|------|------|-----------|------|
| 影响估计精度 | 外部行为模型（OtterTune, MB2）预测具体指标变化 | LLM 估计 + 启发式规则 | 无外部行为模型可用 |
| 量化程度 | 预测具体性能指标变化量（如 active sessions 减少 X%） | 定性描述（"brief I/O spike", "improves query performance"） | 缺乏历史数据训练行为模型 |
| 高风险列表 | 先验维护 | 正则匹配 SQL 模式 + API 类型规则 | 等效实现，更易扩展 |
| 操作过滤 | 仅高亮标记，不阻止 | 可配置阻止（require_evidence_for_high_risk） | Benchmark 需要防止 agent 执行破坏性操作 |

---

## 5. Question Verification Agent (QVA)

### 5.1 论文算法

- 对用户查询进行 embedding，与文档库做相似度搜索
- 如果最高相似度 < λ=0.85，判定为 "out-of-context"
- 对 out-of-context 查询，进一步匹配 AWS 服务描述文档，推荐相关服务
- 完全无关查询（如 "今天天气如何"）要求用户修改查询

### 5.2 我们的实现

**未实现**。

### 5.3 差异说明

QVA 在 DBA-Bench 中不适用。Benchmark 的 Orchestrator 直接向 agent 发送预定义的告警信息，不存在用户输入无关查询的场景。所有查询都是有效的数据库性能问题。

---

## 6. 整体架构适配

### 6.1 论文架构 vs DBA-Bench 架构

**论文**: Panda 是一个单轮 Q&A 系统
- 用户提问 → Grounding → LLM 生成 → Verification → 返回答案
- 所有信息在一次调用中收集和处理

**DBA-Bench**: 多轮 Agent 循环
- Orchestrator 驱动: `get_next_input()` → `dispatch(action)` → `add_tool_result()` → 循环
- Agent 需要主动收集信息（不能一次获取所有遥测数据）

### 6.2 适配方案

```
Turn 1 (Proactive Grounding):
  └── 返回预定义的指标收集 + schema 查询动作（无需 LLM）

Turn 2+ (After receiving metric results):
  ├── T2T: 将收到的数值指标转换为文本特征
  ├── Correlation: 计算跨指标相关性
  ├── Anomaly: 识别异常指标
  ├── RAG: 基于 alert + 异常摘要检索文档
  ├── Aggregate: 构建 JSON 结构化上下文
  ├── LLM: 注入上下文后生成诊断 + 动作
  ├── Affordance: 评估动作风险，过滤高风险操作
  └── 返回动作列表

Submit Turn:
  ├── Verification: NLI 验证诊断是否被文档支持
  │   ├── entail → Source Attribution → 提交
  │   └── reject/neutral → 重新生成（最多 K=3 次）
  └── 提交 root_cause + solution（含内联引用）
```

### 6.3 渐进模式设计

| 模式 | 组件 | 用途 |
|------|------|------|
| `panda_basic` | LLM + T2T | 消融实验: 仅 grounding 无 RAG |
| `panda_rag` | + Document Retriever | 消融实验: 加入文档检索 |
| `panda_verified` | + Verification + Attribution | 消融实验: 加入验证机制 |
| `panda_full` | + Affordance + Feedback | 完整 Panda 流水线 |

---

## 7. 文件结构

```
src/control/baselines/
├── panda_agent.py          # 主 Agent 类，协调所有组件
├── panda_grounding.py      # Document Retriever + T2T + Context Aggregator
├── panda_verification.py   # NLI Verifier + Source Attribution
├── panda_affordance.py     # Impact Estimation + Risk Flagging
├── panda_feedback.py       # Vector Store Feedback Cache
├── panda_prompts.py        # 所有 prompt 模板
├── panda_types.py          # 数据类定义

examples/
├── run_panda_baseline.py   # 示例运行脚本
```

---

## 8. 总结: 关键差异一览

| # | 论文设计 | 我们的实现 | 差异类型 |
|---|---------|-----------|---------|
| 1 | 单轮 Q&A | 多轮 Agent 循环 | 架构适配 |
| 2 | QVA 过滤无关查询 | 未实现 | 不适用 |
| 3 | 数据湖查询 24h 遥测 | Orchestrator tool dispatch | 架构适配 |
| 4 | Embedding 选择 top-3 相关指标 | 预定义标准指标列表 | 简化（环境指标有限） |
| 5 | 专用 change point 算法 | 滚动均值 + 1.5σ | 轻量替代 |
| 6 | text-embedding-ada-002 | all-MiniLM-L6-v2 + keyword fallback | 本地化 + 降级 |
| 7 | 外部行为模型估计影响 | LLM + 启发式规则 | 无外部模型 |
| 8 | 用户显式反馈 | 自动记录交互结果 | Benchmark 无人工环节 |
| 9 | 失败后输出失败消息 | 用尽重试仍提交 | Benchmark 评分需要 |
| 10 | 逐字匹配归因 | 词重叠/embedding 相似度 | 放宽匹配（LLM 改写） |

**忠实复现的核心设计**:
- Verification premise = 检索文档（非工具结果）
- Verification 重试 = 重新生成诊断（非收集更多证据）
- T2T 提取 trend/mean/p95/change_points/seasonality/correlation
- Feedback 区分 positive/negative 反馈
- Source Attribution 句子级内联引用
- Affordance 高风险操作标记
