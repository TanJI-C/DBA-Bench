---
doc_id: docs.baseline.dbaiops-implementation
doc_type: guide
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: public
scope: [shared]
summary: DBAIOps baseline 的当前实现契约：两阶段图演化、ADF 时序采样、异常方程确认、结构化诊断报告与框架适配差异。
source_of_truth: code
related: [docs.index.public]
---

# DBAIOps Baseline 实现文档

本文档描述 DBAIOps (VLDB 2026) 论文 baseline 的当前实现。DBAIOps 原始系统的 GitHub 仓库仅包含浏览器扩展前端，核心后端未开源；本实现基于论文 Section 3-6 的算法描述复现，并适配到 DBA-Bench 的交互式 Agent 框架。论文原文见 `paper/related_paper/DBAIOps.md`。

### 1.1 论文核心架构

```
Alert → AnomalyModel (检测方程) → ExperienceGraph (知识图谱遍历)
     → Two-Stage Graph Evolution (图演化) → RootCauseAnalyser (LLM推理)
     → Diagnosis Report
```

### 1.2 我们的实现架构

```
Alert → Trigger 匹配 (关键词) → ExperienceRetriever 两阶段图演化
     → 每轮: 收集路径上 Metric/Tool 节点 + 重采样 SQL 快照指标
     → ADF 时序评估 + 触发器检测方程 M/N 频率确认
     → LLM 修复循环 (native tool calling)
     → RootCauseAnalyser 结构化诊断报告 (⟨Sa,Sl,Sm,Se,So⟩) → submit
```

---

## 2. Adaptive Detector Function (ADF) — 论文 Section 6.1

### 2.1 论文算法

论文定义了一个 5 步自适应异常检测函数，用于判断指标序列是否异常：

**Step 1: 波动性计算** — σ（样本标准差）与 CV（波动自相关 ρV / 随机基准 ρR）。

**Step 2: 动态基线 Bt 与偏差 D** — D = |x_t − B_t|；论文按小时更新基线。

**Step 3: 状态函数 F_state**

```
F_state = 1 − D/σ   (x_t 接近 B_t, D ≤ σ)
F_state = D/σ       (x_t 远离 B_t, D > σ)
```

**Step 4: 权重** — w1 = σ/(σ+θ)，w2 = 1−w1（θ 默认 10.0，可配置）。

**Step 5: 加权评分** — S = w1·σ + w2·F_state；S 超过阈值判为异常。

### 2.2 我们的实现

文件: `src/agents/baselines/dbaiops/adf.py`，公式与论文逐步一致。

关键数学性质（决定阈值取值）：F_state 在指标**正常**时接近 1（D 小 → 1−D/σ 大），在偏离时大于 1（D/σ）。因此：

- `score_threshold=1.2`（默认）是正确标尺：S ≤ ~1 视为正常，S > 1.2 判异常。
- 取 0.7 会把正常指标判为异常，导致演化永不提前终止。禁止回退到 0.7。

实现细节（论文未公开部分的自选）：

| 细节 | 论文描述 | 我们的选择 |
|------|---------|-----------|
| Bt 计算 | "按小时更新" | 截尾均值（去掉序列末端最新值后上下 25%） |
| CV 的 ρV 输入 | "波动序列自相关" | 相邻差绝对值序列的 lag-1 自相关 |
| CV 的 ρR 基准 | "随机序列自相关" | 1/√n（白噪声渐近值） |

### 2.3 采样要求

ADF 需要时间序列输入。2 个样本时 σ = D/√2 < D 恒成立，任何差异都判异常；因此 `retriever.ADF_MIN_SAMPLES = 3`，样本数不足 3 的指标序列跳过评估。指标序列的来源见第 5 节。

---

## 3. AnomalyModel — 论文 Section 5.1

### 3.1 论文算法

```
Is_Anomaly = METRIC_raw > threshold₁
             ∨ (METRIC_composite = trend ∧ METRIC_raw > threshold₂)
trend ∈ {0(stable), 1(sharp_decline), 2(slow_decline), 3(sharp_rise), 4(slow_rise), 5(fluctuating)}
```

M/N 频率控制：最近 N 次评估中 M 次为 True 才确认异常，防止瞬时抖动。

### 3.2 我们的实现

文件: `src/agents/baselines/dbaiops/anomaly_model.py`

```python
class AnomalyModel:
    def __init__(self, model_id, trigger_vertex_id, equations)  # M/N 从 equations 派生（取最严格值）
    def evaluate(self, metric_values) -> bool        # 方程评估 + M/N 频率控制
    def evaluate_raw(self, metric_values) -> bool    # 仅方程评估，不累计频率历史

def compute_trend(values, sharp_threshold=0.3, slow_threshold=0.1, fluctuation_cv=0.5) -> int
```

接入方式（`DbaiopsAgent._record_trigger_anomaly_evaluation`）：

1. 每个演化轮次对匹配 Trigger 的检测方程评估一次；
2. `METRIC_raw` 取该指标累积序列的最新值（`_resolve_metric_series` 负责名称映射）；
3. `METRIC_composite` 由 `METRIC_raw` 自身序列经 `compute_trend` 派生，键名为 `{metric_raw}#trend`（图谱 Trigger 属性不携带 composite 顶点，论文中 composite 即 raw 的 10 分钟窗口趋势）；
4. 每轮评估结果（原始判定 + M/N 确认判定）记录在 `_anomaly_evaluations`，随 trace 导出并写入诊断 prompt 的 Anomaly Detection Verdict 一节。

初始触发匹配仍是关键词匹配（见 7.3）：交互式入口没有指标可评估，方程用于演化过程中**确认**触发器，而非发现触发器。

### 3.3 与论文的差异

| 方面 | 论文 | 我们的实现 | 原因 |
|------|------|-----------|------|
| 趋势分析算法 | "10分钟窗口波动性分析" | 前后半对比 + 变化率计算 | 论文未给出具体算法 |
| METRIC_composite 来源 | 监控系统持续计算 | 按需对累积序列调用 compute_trend() | 适配交互式采样 |
| 阈值方向 | 仅 ">" | 支持 inverted（"<"，如 cache_hit_ratio） | 图谱含反向指标 |
| 触发器发现 | 方程评估（数据驱动） | 关键词匹配（文本驱动）+ 方程确认 | Agent 入口无指标历史 |

---

## 4. ExperienceGraph — 论文 Section 4

### 4.1 论文算法

6 种顶点（Trigger / Experience / Tool / Metric / Tag / Auxiliary）+ 4 种边（Containment / Relevance / Diagnosis / Synonym）构成的异构有向图；诊断路径是图上的遍历路径。

### 4.2 我们的实现

文件: `src/agents/baselines/dbaiops/graph.py`

```python
class ExperienceGraph:
    def __init__(self, graph_path)                 # 加载 JSON 图谱
    def get_trigger_vertices(self) -> List[GraphNode]
    def get_neighbors(self, node_id, edge_type=None)
    def get_incoming_neighbors(self, node_id)
    def find_overlapping_models(self, trigger_id)   # Proximity Discovery 的重叠模型发现
    def create_cross_edge(self, source_id, target_id, edge_type)
    def get_diagnosis_paths(self, trigger_id, max_depth)  # BFS 限深
```

知识图谱数据: `data/knowledge_graph/pg_experience_graph.json`（56 节点 / 87 边，12 Trigger）。该文件的 sha256 由 factory 的 `_verify_artifact` 校验，改动图谱必须同步更新实验 manifest 的 `graph_sha256`。

### 4.3 与论文的差异

| 方面 | 论文 | 我们的实现 | 原因 |
|------|------|-----------|------|
| 图谱规模 | 生产级（数十万边） | 56 节点 | 覆盖 DBA-Bench 已有场景即可 |
| 图存储 | 图数据库 | JSON + 内存邻接表 | 场景规模不需要图数据库 |
| Cross-Edge | 运行时持久化 | 仅当前会话内有效 | Agent 每次运行独立加载图谱 |

---

## 5. Two-Stage Graph Evolution — 论文 Section 6.1

### 5.1 论文算法

```
repeat:
    Stage 1: Proximity Discovery → 扩展图 → 收集演化路径上的所有 Metrics
    Stage 2: ADF(指标序列) → 存在异常? 扩展 : 终止
until: 终止 or max_depth
```

### 5.2 我们的实现

文件: `src/agents/baselines/dbaiops/retriever.py`

```python
class ExperienceRetriever:
    def __init__(self, graph, adf, max_depth=4, top_k=5, exclude_metric_types=None)
    def initialize(self, trigger_id) -> EvolutionState
    def take_pending_actions(self) -> List[(GraphNode, action)]      # 收集路径上所有未查 Metric/Tool 节点
    def take_snapshot_resample_actions(self) -> List[(GraphNode, action)]  # 重采样 SQL 快照指标
    def evolve(self) -> EvolutionState                                # ADF 裁剪 + 扩展决策（无参数）
    def should_terminate(self) -> bool
    def get_experience_evidence(self) -> List[str]
```

**每个演化轮次（`DbaiopsAgent.solve` 主循环）:**

1. `take_pending_actions()`：收集扩展路径上全部未查询的 Metric/Tool 节点并执行（论文 Stage 1 的"收集演化路径上的指标"）；
2. `take_snapshot_resample_actions()`：重查询已查过的 SQL 快照指标（`SQL_BACKED_METRIC_QUERIES` 中的 slow_queries / topsql / dead_tuples，经 `execute_sql` 获取）。快照型指标每轮只新增一个样本，重采样使其序列随轮次增长；query_metrics 类指标自带完整时间序列（series 结果整体替换存储），无需重采样；
3. `_record_trigger_anomaly_evaluation()`：AnomalyModel 检测方程确认（第 3 节）；
4. `evolve()`：对累积序列中长度 ≥ `ADF_MIN_SAMPLES`(3) 的指标运行 ADF；存在异常且未达 max_depth → 从异常指标关联的 Trigger 扩展路径，否则终止。

**指标样本提取（`_extract_metrics_from_result`，按结果 kind 分派）:**

| 结果类型 | 提取规则 | 累积键 |
|---------|---------|--------|
| series (query_metrics) | 整条序列替换 | `{metric_type}[{target}].{field}` |
| records / rows | 行数 + 声明的 value 列求和 | `{metric_type}.row_count`、`{metric_type}.{value_column}` |
| snapshot | 数值字段逐个追加 | `{metric_type}.{field}` |

`SQL_BACKED_METRIC_QUERIES` 中 value_column 语义：slow_queries/topsql 为 None（触发阈值按计数定义，取行数），dead_tuples 为 `n_dead_tup`（各表死元组合计，阈值 10000 按总量定义）。

### 5.3 与论文的差异

| 方面 | 论文 | 我们的实现 | 原因 |
|------|------|-----------|------|
| 演化触发 | 持续监控系统自动触发 | Agent 演化循环逐轮驱动 | 交互式评估框架 |
| Metric 收集 | 直接访问监控系统 | query_metrics / execute_sql API | DBA-Bench 工具面限制；SQL 细节不入 query_metrics 面 |
| 指标时间序列 | 监控系统历史窗口 | series 直接可用；快照指标按演化轮次重采样累积 | 交互模式下无独立采集通道 |
| 终止条件 | ADF 全部正常 OR 超时 | ADF 全部正常 OR max_depth OR turn 预算耗尽 | 无实时超时概念 |
| 不支持指标 | — | `exclude_metric_types` 在选节点时跳过并标记已查 | TiDB 面无 cache_hit_ratio 等 |

---

## 6. 结构化 Prompt — 论文 Section 6.2

### 6.1 论文算法

prompt = ⟨Sa, Sl, Sm, Se, So⟩：Sa 症状描述、Sl 检测条件、Sm 指标关键统计、Se 图经验、So 报告组件（Anomaly Validation / Root Cause Analysis ≤5 / Recovery Solution / Summary / SQL Context）。

### 6.2 我们的实现

文件: `src/agents/baselines/dbaiops/prompts.py`

```python
DBAIOPS_SYSTEM_PROMPT       # LLM 角色设定
DBAIOPS_DIAGNOSIS_PROMPT    # ⟨Sa, Sl, Sm, Se, So⟩ 结构化诊断报告 Prompt（RootCauseAnalyser 终局生成）
DBAIOPS_REMEDIATION_PROMPT  # 修复循环入口 Prompt（含检测方程判定 + ADF 证据）
DBAIOPS_FALLBACK_PROMPT     # 无图谱路径时的 LLM Prompt（工具契约由 native tool schema 提供）
```

**修复循环入口（`_build_diagnosis_prompt`）填充:**

| 组件 | 来源 |
|------|------|
| Anomaly Description | `self._alert` |
| Detection Condition | `_get_detection_condition()`（Trigger 属性构建） |
| Anomaly Detection Verdict | `_format_anomaly_verdict()`（M/N 频率确认结果 + 最新评估值） |
| Metric Statistics & ADF Evidence | `_format_metric_evidence()`（每个累积指标的 n/latest/mean/min/max + ADF score/σ/baseline/abnormal） |
| Collected Observations | `_format_observations()`（最近 10 条原始结果，各截断 200 字符） |
| O&M Experience | `retriever.get_experience_evidence()` |

**终局报告（`_finalize_submission`）**: 所有终止路径（纯文本回复 / LLM submit / final-turn 强制提交）统一调用 `call_text(DBAIOPS_DIAGNOSIS_PROMPT…)` 生成论文式五段报告，作为 `structured_submission` 的 factor 与 summary 提交；`outcome.changes` 取 `_executed_changes`（修复循环中实际执行的非只读动作，SQL 按 SELECT/EXPLAIN/SHOW 前缀判只读，manage_instance 按 set_config/restart 判定），无修复时明确标注 "No explicit remediation was reported"。

### 6.3 与论文的差异

| 方面 | 论文 | 我们的实现 | 原因 |
|------|------|-----------|------|
| Sm 内容 | 指标名+时间范围+阈值 | 每指标关键统计 + ADF 判定（原始观测另附截断样本） | 交互模式无统一时间范围概念 |
| 报告后处理 | 结构化解析 + 存储 | `structured_submission` 结构化提交 | DBA-Bench 评估接口 |
| 修复执行 | 论文仅产出报告 | 修复循环实际执行变更后再生成报告 | DBA-Bench Outcome 评估要求真实修复 |

---

## 7. 主 Agent 集成 — 论文 Section 3 整体流程

### 7.1 论文流程

```
1. Alert 输入 → AnomalyModel 评估 → 匹配 Trigger Vertex
2. Two-Stage Graph Evolution 循环
3. RootCauseAnalyser (LLM) 生成诊断报告
```

### 7.2 我们的实现

文件: `src/agents/baselines/dbaiops/agent.py`

```python
class DbaiopsAgent(BaseAgent):
    use_native_tools = True
    mode = "dbaiops"

    def solve(self):
        # 1. _ensure_initialized: 加载图谱 + 构建 ADF/Retriever/AnomalyModels
        # 2. TiDB: 预取 query_history 契约窗口 + 排除不支持指标
        # 3. _match_trigger_by_keywords; 无匹配 → _run_llm_loop(fallback prompt)
        # 4. 演化主循环（第 5 节）
        # 5. _run_llm_loop(修复 prompt) → 修复 + 终局报告 → structured submission
```

内部 LLM 通过 `LLMAgent` 复用 native tool calling 与 token 记账（`_next_llm_actions` / `_feed_tool_result` / `_next_final_submission` / `call_text`）；终止路径统一走 `_finalize_submission`。`exit` 动作抛 `RuntimeError`（与 LLMAgent 行为一致，不静默吞掉）。

### 7.3 与论文的差异

| 方面 | 论文 | 我们的实现 | 原因 |
|------|------|-----------|------|
| 执行模式 | 管道式一次性执行 | 交互式多轮 Agent 循环 | DBA-Bench BaseAgent 接口 |
| Trigger 匹配 | AnomalyModel 方程评估 | 关键词匹配入口 + 方程每轮确认 | Agent 首轮无指标历史 |
| 修复 | 仅产出报告 | LLM 修复循环实际执行变更 | Outcome 评估要求 |
| 无图谱匹配 | 未提及 | Fallback prompt（工具契约来自 native schema） | 鲁棒性 |
| TiDB 适配 | 论文面向多数据库产品 | query_history 窗口重写 + 指标面排除 | 复用 PG 经验图谱 |

---

## 8. 总体差异总结

### 8.1 架构层面的适配

论文 DBAIOps 是持续运行的监控系统，DBA-Bench 是离散 Agent 评估框架：持续监控 → 离散查询；管道执行 → 交互循环；实时数据 → API 调用。此外论文系统只产出诊断报告，DBA-Bench 要求真实修复，故在报告生成前插入 LLM 修复循环。

### 8.2 算法层面的忠实度

| 组件 | 忠实度 | 说明 |
|------|--------|------|
| ADF 5步算法 | ★★★★★ | 公式逐步一致；≥3 样本才评估；threshold=1.2 由 F_state 数学行为推导 |
| AnomalyModel 检测方程 | ★★★★☆ | 方程 + M/N 频率控制 + 趋势派生已接入演化循环；入口匹配仍是关键词 |
| ExperienceGraph 结构 | ★★★★★ | 6 顶点 + 4 边类型一致 |
| Two-Stage Evolution | ★★★★☆ | 批量收集 + ADF 裁剪 + 异常扩展一致；快照指标按轮重采样近似时序 |
| 结构化 Prompt | ★★★★★ | ⟨Sa, Sl, Sm, Se, So⟩ 用于终局报告；Sm 为关键统计 + ADF 证据 |
| Proximity Discovery | ★★★★☆ | 逻辑一致，Cross-Edge 仅会话内有效 |

### 8.3 论文未公开的实现细节（需自行选择）

| 细节 | 论文描述 | 我们的选择 |
|------|---------|-----------|
| θ (波动性阈值) | 未给出 | 10.0 (可配置) |
| score_threshold | 未给出 | 1.2 (可配置；由 F_state 数学行为推导，勿改 0.7) |
| Bt 计算方法 | "按小时更新" | trimmed mean（去除上下 25%） |
| CV 的 ρV 输入 | "波动序列自相关" | 相邻差绝对值序列 lag-1 自相关 |
| CV 的 ρR 基准 | "随机序列自相关" | 1/√n（白噪声渐近值） |
| 趋势分析算法/阈值 | 未给出 | 前后半对比 + 变化率；sharp=0.3, slow=0.1, cv=0.5 (可配置) |
| 路径数量限制 | 未提及 | top_k=5，重叠模型取 2 条 (可配置) |

### 8.4 框架适配（非论文内容的必要补充）

| 补充机制 | 原因 |
|---------|------|
| Keyword-based trigger matching | Agent 首轮无指标历史，方程在演化轮次中确认 |
| LLM fallback prompt | 图谱无法匹配告警时的路径 |
| 指标样本提取（series/records/snapshot 分派） | 适配 DBA-Bench 工具结果格式 |
| excluded metric types | 图谱指标可能不在目标系统工具面上 |
| outcome.changes 跟踪 | DBA-Bench Outcome 评估需要真实修复记录 |

### 8.5 已知局限

1. **无历史基线**: 论文的 Bt 基于小时级历史数据；我们用当前序列统计量近似
2. **图谱规模有限**: 仅覆盖 DBA-Bench 已有场景
3. **快照指标时序为近似**: 每演化轮次一个样本，序列长度受演化深度与 turn 预算限制
4. **无持续学习**: 图谱静态，Cross-Edge 不跨运行持久化
5. **TiDB 复用 PG 图谱**: 经验知识未按系统拆分

---

## 9. 文件清单

```
src/agents/baselines/dbaiops/
├── types.py            # GraphNode, GraphEdge, AnomalyEquation, ADFResult, DiagnosticPath, EvolutionState
├── adf.py              # ADF 5 步算法
├── anomaly_model.py    # AnomalyModel（方程 + M/N 频率控制）+ compute_trend
├── graph.py            # ExperienceGraph 异构图
├── retriever.py        # ExperienceRetriever 两阶段图演化 + SQL_BACKED_METRIC_QUERIES
├── prompts.py          # SYSTEM / DIAGNOSIS / REMEDIATION / FALLBACK Prompt
├── agent.py            # DbaiopsAgent 主类 + MockDbaiopsAgent
└── __init__.py         # 导出 DbaiopsAgent, MockDbaiopsAgent

data/knowledge_graph/
└── pg_experience_graph.json   # PostgreSQL 经验图谱（sha256 由 factory 校验）

tests/
└── test_dbaiops_agent.py      # 单元/集成测试（全 mock，不调用真实 LLM）

examples/
├── run_dbaiops_baseline.py             # PG 场景入口脚本
└── run_mock_baseline_agents_trace.py   # MockDbaiopsAgent trace 导出冒烟脚本
```

factory 注册: `src/agents/factory.py` 的 `DBAIOPS_SETTING_KEYS`（adf_score_threshold / adf_theta / frequency_m / frequency_n / graph_path / graph_sha256 / max_evolution_depth / top_k），settings 为精确键集合。

---

## 10. TiDB 知识图谱

`data/knowledge_graph/tidb_experience_graph.json`（sha256 `249ce41f…`）由 TiDB 8.1 官方文档语料
（`knowledge/tidb`，3518 篇）与场景定向语料（`knowledge/tidb/curated`，34 篇）统一构建：语料经
`tidb_unified` 中间层一视同仁处理，最终图谱对 Agent 不暴露任何来源身份；chunk 级溯源在
`data/knowledge_graph/tidb_graph_provenance.jsonl`（sidecar，仅审计用）。

构成：trigger 210 / experience 564 / tool 114 / metric 22（恰好覆盖 TiDB 指标目录全集，
`src/execution/tidb_metrics.py`）/ tag 32 / auxiliary 25；边 2067（containment 902 /
diagnosis 931 / relevance 234）。构建纪律：只收录故障类级别知识（机制 + 鉴别诊断 + 修复族），
不收录 case 实例解法；阈值仅在语料给出明确数值时写入（当前 16/210 个 trigger 带完整检测方程，
其余待场景 hardening/rerun 校准）。

选择规则：`DbaiopsAgent._ensure_initialized` 按 `set_tools` 检测到的目标系统选图——TiDB 工具面
（含 `query_history` + `manage_cluster`）加载 TiDB 图，其余加载 `graph_path` 指定的 PG 图；
factory 实验配置用 `graph_path`/`graph_sha256` 显式 pin 目标图。TiDB 上快照指标不做重采样
（query_history 为有界冻结窗口，重采样无意义），ADF 仅对 series 型指标生效。已知缺口：跨分片
锚点 trigger（如 `trigger_slow_query`）的部分路径尚未挂 metric/tool 叶子，留待增补。
