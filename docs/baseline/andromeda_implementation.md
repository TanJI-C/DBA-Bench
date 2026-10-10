# Andromeda Baseline 实现文档

## 1. 论文原始算法

### 1.1 概述

Andromeda (SIGMOD 2025) 是一个基于检索增强生成（RAG）的 DBMS 配置调试系统。
给定用户的自然语言问题描述，系统自动诊断配置不当的 knobs 并生成修复建议。

**论文信息：**
- 标题：Automatic Database Configuration Debugging using Retrieval-Augmented Language Models
- 作者：Sibei Chen, Ju Fan, Bin Wu, Nan Tang 等
- 单位：中国人民大学 + 阿里巴巴
- 发表：SIGMOD 2025 (DOI: 10.1145/3709663)
- arXiv：2412.07548

### 1.2 系统架构（两阶段）

#### Offline Stage（离线阶段）

**1. 异构文档统一嵌入学习**

论文训练了一个对比学习编码器，将三类异构文档映射到统一向量空间：
- 历史问题（StackOverflow, MySQL Forum）：描述"什么出了问题"
- 故障排除手册（MySQL/PostgreSQL Manual）：描述"如何修复"
- 配置 knob 文档：描述参数含义和取值范围

对比学习目标：
```
L = -log(exp(sim(q, d+)/τ) / Σ exp(sim(q, d-)/τ))
```
其中 q 为用户问题编码，d+ 为正样本文档，d- 为负样本文档，τ 为温度参数。

**2. 逻辑链数据合成（Logic-Chain-Based Task Decomposition）**

为解决标注数据不足问题，论文设计了逻辑链合成策略：
```
触发行为 → 导致问题的行为 → 解决问题的功能 → 对应的证据
```
反向遍历此逻辑链，利用 GPT-4 生成多样化的训练样本。

**3. LLM 微调**

基于 Qwen2-7B 进行：
- Continual Pre-Training (CPT)：注入数据库领域知识（DBMS 手册、SQL 文档、StackOverflow Q&A）
- Supervised Fine-Tuning (SFT)：训练证据推理能力（使用逻辑链合成的标注数据）

#### Online Stage（在线阶段）

论文的在线推理是一个 **single-shot pipeline**，包含三个步骤：

**Step 1: Multi-Source Evidence Retrieval（多源证据检索）**

```
输入: 用户自然语言问题 Q
输出: top-k 相关文档集合 D = {d1, d2, ..., dk}

算法:
1. 用训练好的编码器 E 将 Q 编码为向量: v_q = E(Q)
2. 异构文档检索:
   a. 历史问题检索: 对所有历史问题 {h_i} 计算 sim(v_q, E(h_i))，取 top-5
   b. 手册段落检索: 对所有手册段落 {m_j} 计算 sim(v_q, E(m_j))，取 top-5
3. 合并结果: D = top-5(历史问题) ∪ top-5(手册段落)
```

关键点：编码器通过对比学习对齐了"问题描述"和"解决方案"的语义空间，
使得描述问题的 query 能检索到描述解决方案的手册段落。

**Step 2: Troublesome Telemetry Retrieval（异常遥测检索）**

```
输入: 557 个性能指标的时间序列数据（Prometheus, 1s 采样）
输出: top-k 相关异常描述 T = {t1, t2, ..., tk}

算法:
1. Anomalous Telemetry Detection（异常检测）:
   对每个指标 m_i 的时间序列 X_i:
   a. STL 分解: X_i = Trend_i + Seasonal_i + Residual_i
      - 使用 LOESS (Locally Estimated Scatterplot Smoothing)
      - period 根据采样频率设定
   b. 异常判定: 若 |Residual_i[t]| > threshold × σ(Residual_i)
      则标记 (m_i, t) 为异常点

2. Telemetry-to-Text Transformation（文本化）:
   对每个异常点生成自然语言描述:
   t_j = "指标 {name} 在 {timestamp} 出现异常，
          观测值 {value}，偏离正常范围 {deviation}"

3. Relevant Telemetry Selection（相关性排序）:
   a. 用同一编码器 E 编码异常描述: v_t = E(t_j)
   b. 计算与用户问题的相似度: score_j = sim(v_q, v_t)
   c. 取 top-k 最相关的异常描述
```

**Step 3: Configuration Reasoning（配置推理）**

```
输入: 用户问题 Q, 检索文档 D, 异常描述 T
输出: 配置修改建议 R = {(knob, value, rationale)}

算法（两阶段 prompting）:

Phase 1 — Knob Identification:
  prompt = "给定以下证据 [Q + D + T]，识别与问题相关的配置 knobs"
  knobs = LLM(prompt)  → ["shared_buffers", "work_mem", ...]

Phase 2 — Value Recommendation:
  prompt = "对于 knobs={knobs}，当前值={current}，
           基于证据 [D + T] 推荐具体配置值"
  recommendations = LLM(prompt)  → [{knob, value, rationale}, ...]
```

**Interactive and Adaptive Debugging（交互式调试）**

论文还训练了一个判断模型，决定是否需要向用户请求更多信息：
- 输入：用户问题 + 当前可用证据
- 输出：(需要更多信息?, 具体收集步骤)
- 训练数据来源：StackOverflow 中回答者要求提问者补充信息的交互

### 1.3 评估结果

| 数据集 | 指标 | Andromeda | Best Baseline |
|--------|------|-----------|---------------|
| MySQL SO (174) | F1 | 0.441 | 0.332 |
| MySQL Forum (49) | F1 | 0.398 | 0.301 |
| PostgreSQL SO (57) | F1 | 0.425 | 0.310 |
| MySQL Runnable (100) | SuccessRate | 0.79 | 0.57 |

端到端运行时间：~5-7 秒/问题

---

## 2. 我们的实现逻辑

### 2.1 整体架构

将 Andromeda 的 single-shot pipeline 适配为 DBA-Bench 的交互式 Agent：

```
┌─────────────────────────────────────────────────────────┐
│                    AndromedaAgent                         │
│                                                          │
│  State Machine:                                          │
│  ┌──────────────┐    ┌──────────────────┐               │
│  │ COLLECT      │───→│ COLLECT_LOGS     │               │
│  │ TELEMETRY    │    │ _CONFIG          │               │
│  └──────────────┘    └────────┬─────────┘               │
│                               │                          │
│                    ┌──────────▼─────────┐               │
│                    │ ANALYZE_AND_REASON │               │
│                    │ (内部执行完整pipeline)│               │
│                    └──────────┬─────────┘               │
│                               │                          │
│                    ┌──────────▼─────────┐               │
│                    │     SUBMIT         │               │
│                    └────────────────────┘               │
│                                                          │
│  Components:                                             │
│  ├── AndromedaTelemetry  (STL 异常检测)                  │
│  ├── AndromedaRetriever  (Dense Retrieval)               │
│  └── LLMAgent            (两阶段推理)                    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 状态机各阶段

**Turn 1: COLLECT_TELEMETRY**
```python
# 发出 7 个 query_metrics 调用
actions = [
    {"api": "query_metrics", "args": {"metric_type": "cpu"}},
    {"api": "query_metrics", "args": {"metric_type": "memory"}},
    {"api": "query_metrics", "args": {"metric_type": "disk_io"}},
    {"api": "query_metrics", "args": {"metric_type": "slow_queries"}},
    {"api": "query_metrics", "args": {"metric_type": "cache_hit_ratio"}},
    {"api": "query_metrics", "args": {"metric_type": "qps"}},
    {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
]
# 结果通过 _pending_metric_queue 按顺序关联到对应 metric_type
```

**Turn 2: COLLECT_LOGS_CONFIG**
```python
actions = [
    {"api": "read_log", "args": {"log_type": "pg_log", "lines": 100}},
    {"api": "manage_instance", "args": {"action": "get_config"}},
]
```

**Turn 3: ANALYZE_AND_REASON（核心，内部执行完整 pipeline）**
```python
def _do_analyze_and_reason(self):
    # Step 1: STL 异常检测
    anomalies = self._telemetry.detect_anomalies()

    # Step 2: Telemetry-to-Text
    anomaly_texts = self._telemetry.get_anomaly_texts()

    # Step 3: 按语义相似度排序异常描述
    ranked_texts = self._retriever.rank_telemetry_texts(alert, anomaly_texts)

    # Step 4: 文档检索 (历史 Q&A + 手册)
    qa_docs = self._retriever.retrieve_by_type(alert, "historical_qa")
    manual_docs = self._retriever.retrieve_by_type(alert, "manual")

    # Step 5: Phase 1 LLM — 识别相关 knobs
    phase1_result = self._call_llm(PHASE1_PROMPT.format(...))
    knobs = parse_knobs(phase1_result)

    # Step 6: Phase 2 LLM — 推荐具体值
    phase2_result = self._call_llm(PHASE2_PROMPT.format(...))
    diagnosis = parse_diagnosis(phase2_result)
```

**Turn 4: SUBMIT**
```python
actions = [{"api": "submit", "args": {"diagnosis": diagnosis_text}}]
```

### 2.3 STL 异常检测实现

```python
class AndromedaTelemetry:
    def _stl_anomaly_detection(self, metric_type, values, timestamps):
        # 使用 statsmodels.tsa.seasonal.STL（与论文相同的算法）
        stl = STL(values, period=self.period, robust=True)
        result = stl.fit()
        residuals = result.resid

        # 异常判定：残差超过 ±threshold × σ
        std = np.std(residuals)
        mean = np.mean(residuals)
        for i, r in enumerate(residuals):
            severity = abs(r - mean) / std
            if severity >= self.anomaly_threshold:  # 默认 2.0
                # 标记为异常
                ...
```

降级策略：
- 时间序列长度 < 2×period → 退化为简单 z-score 检测
- 标量指标（非时间序列）→ 与已知健康阈值比较
- statsmodels 不可用 → 退化为 z-score 检测

### 2.4 文档检索实现

```python
class AndromedaRetriever:
    def retrieve(self, query):
        # 使用 sentence-transformers 编码 query
        query_emb = model.encode([query], normalize_embeddings=True)

        # 计算与所有文档的 cosine 相似度
        scores = np.dot(self._embeddings, query_emb.T).flatten()

        # 返回 top-k
        top_indices = np.argsort(scores)[::-1][:self.top_k]
        return [self._documents[i] for i in top_indices]

    def rank_telemetry_texts(self, alert, telemetry_texts):
        # 对异常描述按与 alert 的语义相似度排序
        alert_emb = model.encode([alert], normalize_embeddings=True)
        text_embs = model.encode(telemetry_texts, normalize_embeddings=True)
        scores = np.dot(text_embs, alert_emb.T).flatten()
        return [telemetry_texts[i] for i in np.argsort(scores)[::-1]]
```

降级策略：
- sentence-transformers 不可用 → 退化为关键词匹配

### 2.5 文件结构

```
src/control/baselines/
    andromeda_agent.py       # 主 Agent 状态机
    andromeda_telemetry.py   # STL 异常检测 + Telemetry-to-Text
    andromeda_retriever.py   # Dense Retrieval (sentence-transformers)
    andromeda_prompts.py     # 两阶段推理 Prompt 模板
    andromeda_types.py       # 数据类型定义

knowledge/andromeda/
    pg_manual/               # PostgreSQL 手册段落
    historical_qa/           # 历史 Q&A 对
```

---

## 3. 与原始论文的差异

### 3.1 差异总览

| 组件 | 论文实现 | 我们的实现 | 差异类型 | 影响 |
|------|---------|-----------|---------|------|
| 文档编码器 | 对比学习训练的统一嵌入模型 | sentence-transformers (bge-base-en-v1.5) | **必要替换** | 检索质量可能下降 |
| 推理 LLM | Qwen2-7B (CPT + SFT) | 通用 LLM (GPT-4/Claude) | **必要替换** | 推理能力不同 |
| STL 异常检测 | STL (LOESS) | statsmodels.tsa.seasonal.STL | **忠实复现** | 无 |
| 异常指标排序 | 对比学习编码器 + cosine | sentence-transformers + cosine | **近似替换** | 排序质量可能略有差异 |
| 知识库来源 | StackOverflow + MySQL Forum + MySQL Manual | PostgreSQL Manual + 构造的配置 Q&A | **环境适配** | 覆盖范围不同 |
| 交互式调试 | 微调模型判断是否需要更多信息 | 固定收集策略（总是收集所有指标） | **简化** | 失去自适应能力 |
| 执行模式 | Single-shot pipeline | 多轮状态机 | **必要适配** | 增加了 turn 开销 |
| 逻辑链数据合成 | GPT-4 生成训练数据 | 不实现（无微调） | **省略** | 与推理 LLM 替换相关 |
| Continual Pre-Training | 在 DBMS 文档上继续预训练 | 不实现 | **省略** | 与推理 LLM 替换相关 |

### 3.2 详细差异分析

#### 差异 1: 文档编码器（必要替换）

**论文方法：**
- 训练对比学习编码器，显式对齐"问题描述"和"解决方案"的语义空间
- 使用 InfoNCE loss，正样本为 (问题, 对应解决方案)，负样本为 batch 内其他文档
- 编码器能理解"INSERT 很慢"和"增大 wal_buffers"之间的语义关联

**我们的实现：**
- 使用预训练的 bge-base-zh-v1.5（通用中文语义检索模型）
- 未针对 DBMS 配置调试任务做微调
- 依赖模型的通用语义理解能力

**替换理由：**
论文的 GitHub 仓库不可访问（404），无法获取预训练的编码器权重。
bge-base 是当前最接近的替代——同为 dense retrieval 模型，支持语义检索。

**影响评估：**
- 跨类型检索能力下降：论文编码器能将"问题"映射到"解决方案"附近，
  通用模型只能做字面语义相似度匹配
- 对于描述明确的问题（如"shared_buffers 太小"）影响较小
- 对于隐含性问题（如"查询很慢"→ 需要检索 work_mem 相关文档）影响较大

#### 差异 2: 推理 LLM（必要替换）

**论文方法：**
- 基于 Qwen2-7B 做 Continual Pre-Training + Supervised Fine-Tuning
- CPT 数据：DBMS 手册、SQL 文档、StackOverflow Q&A
- SFT 数据：逻辑链合成的 (问题, 证据, 推荐) 三元组
- 模型学会了"给定证据 → 输出结构化推荐"的映射

**我们的实现：**
- 使用通用 LLM（GPT-4 或 Claude）
- 通过 prompt engineering 模拟两阶段推理结构
- 依赖 LLM 的通用推理能力和预训练知识

**替换理由：**
无法获取论文的训练数据和训练代码。逻辑链数据合成需要大量人工标注的种子数据。

**影响评估：**
- 通用 LLM（GPT-4）的推理能力可能强于微调的 Qwen2-7B
- 但缺乏针对性训练，对 DBMS 配置的专业知识可能不如微调模型精确
- 输出格式的稳定性可能不如微调模型（需要更强的 prompt 约束）

#### 差异 3: 执行模式（必要适配）

**论文方法：**
- Single-shot：接收问题 → 一次性输出诊断和建议
- 延迟 5-7 秒
- 不与数据库交互

**我们的实现：**
- 多轮状态机：4 个 turn 完成完整 pipeline
- Turn 1: 收集遥测数据（与数据库交互）
- Turn 2: 收集日志和配置
- Turn 3: 内部执行分析和推理
- Turn 4: 提交诊断

**适配理由：**
DBA-Bench 的 Orchestrator 要求 Agent 通过 `get_next_input()` → `dispatch()` →
`add_tool_result()` 循环与环境交互。Andromeda 的 pipeline 必须拆分为多个 turn。

**影响评估：**
- 增加了 turn 开销，但不影响诊断质量
- 实际上增强了论文方法：论文假设遥测数据已经可用，
  我们的实现主动从环境收集数据，更接近真实场景

#### 差异 4: 交互式调试（简化）

**论文方法：**
- 训练一个判断模型，决定是否需要向用户请求更多信息
- 如果信息不足，生成具体的数据收集指令（如"请执行 SHOW INDEX..."）
- 基于 StackOverflow 交互数据训练

**我们的实现：**
- 固定收集策略：总是收集所有可用指标、日志和配置
- 不做"是否需要更多信息"的判断

**简化理由：**
1. 无训练数据
2. DBA-Bench 环境中所有指标都可直接获取，不需要"请求用户"
3. 固定收集策略在 benchmark 场景中更公平（不依赖判断模型质量）

#### 差异 5: 知识库（环境适配）

**论文方法：**
- 174 条 MySQL StackOverflow 问题
- 49 条 MySQL Forum 问题
- 57 条 PostgreSQL StackOverflow 问题
- MySQL/PostgreSQL 完整手册分句

**我们的实现：**
- PostgreSQL 配置手册摘要
- 构造的常见配置问题 Q&A

**适配理由：**
DBA-Bench 主要使用 PostgreSQL 环境，知识库需要匹配目标数据库。
论文的完整知识库未公开。

### 3.3 保留的核心方法论

以下论文核心方法论被忠实保留：

1. **STL 季节性分解检测异常** — 使用相同的 statsmodels STL 算法
2. **Telemetry-to-Text 转换** — 将异常转为自然语言描述供 LLM 推理
3. **语义相似度排序异常** — 按与问题的相关性选择 top-k 异常
4. **两阶段推理结构** — Phase 1 识别 knobs → Phase 2 推荐值
5. **多源证据融合** — 历史 Q&A + 手册 + 遥测数据三路证据输入 LLM
6. **Dense Retrieval 检索** — 语义向量检索（虽然编码器不同）

### 3.4 对评估结果的预期影响

| 因素 | 预期影响方向 | 原因 |
|------|------------|------|
| 通用 LLM 替代微调模型 | ↑ 或 → | GPT-4 推理能力强，但缺乏专业微调 |
| 通用编码器替代对比学习 | ↓ | 跨类型检索能力下降 |
| 主动收集遥测数据 | ↑ | 论文假设数据已有，我们主动获取 |
| 固定收集策略 | → | benchmark 中信息总是可获取的 |
| 知识库规模较小 | ↓ | 检索命中率可能下降 |

**总体预期：** 在配置调试类场景上，性能应接近论文报告水平，
但在需要精确跨类型检索的场景中可能有所下降。
