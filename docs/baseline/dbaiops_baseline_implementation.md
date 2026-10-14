---
doc_id: docs.baseline.dbaiops-implementation
doc_type: guide
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: public
scope: [shared]
summary: Current implementation contract of the DBAIOps baseline: two-stage graph evolution, ADF time-series sampling, anomaly equation confirmation, structured diagnosis report, and framework adaptation differences.
source_of_truth: code
related: [docs.index.public]
language: en
---

# DBAIOps Baseline Implementation Document

This document describes the current implementation of the DBAIOps (VLDB 2026) paper baseline. The GitHub repository of the original DBAIOps system contains only the browser-extension frontend; the core backend was not open-sourced. This implementation is reproduced from the algorithm descriptions in Sections 3-6 of the paper and adapted to DBA-Bench's interactive Agent framework. The original paper text is at `paper/related_paper/DBAIOps.md`.

### 1.1 Paper Core Architecture

```
Alert → AnomalyModel (detection equations) → ExperienceGraph (knowledge graph traversal)
     → Two-Stage Graph Evolution (graph evolution) → RootCauseAnalyser (LLM reasoning)
     → Diagnosis Report
```

### 1.2 Our Implementation Architecture

```
Alert → Trigger matching (keywords) → ExperienceRetriever two-stage graph evolution
     → Each round: collect Metric/Tool nodes along the path + resample SQL snapshot metrics
     → ADF time-series evaluation + M/N frequency confirmation of the trigger detection equations
     → LLM remediation loop (native tool calling)
     → RootCauseAnalyser structured diagnosis report (⟨Sa,Sl,Sm,Se,So⟩) → submit
```

---

## 2. Adaptive Detector Function (ADF) — Paper Section 6.1

### 2.1 Paper Algorithm

The paper defines a 5-step adaptive anomaly detection function used to decide whether a metric series is anomalous:

**Step 1: Volatility computation** — σ (sample standard deviation) and CV (volatility autocorrelation ρV / random baseline ρR).

**Step 2: Dynamic baseline Bt and deviation D** — D = |x_t − B_t|; the paper updates the baseline hourly.

**Step 3: State function F_state**

```
F_state = 1 − D/σ   (x_t close to B_t, D ≤ σ)
F_state = D/σ       (x_t far from B_t, D > σ)
```

**Step 4: Weights** — w1 = σ/(σ+θ), w2 = 1−w1 (θ defaults to 10.0, configurable).

**Step 5: Weighted score** — S = w1·σ + w2·F_state; S above the threshold is judged anomalous.

### 2.2 Our Implementation

File: `src/agents/baselines/dbaiops/adf.py`; the formulas match the paper step by step.

Key mathematical property (which determines the threshold value): when a metric is **normal**, F_state is close to 1 (small D → large 1−D/σ), and when it deviates, F_state is greater than 1 (D/σ). Therefore:

- `score_threshold=1.2` (default) is the correct yardstick: S ≤ ~1 is treated as normal, and S > 1.2 is judged anomalous.
- Using 0.7 would flag normal metrics as anomalous, so evolution would never terminate early. Never fall back to 0.7.

Implementation details (our own choices for parts the paper does not disclose):

| Detail | Paper description | Our choice |
|------|---------|-----------|
| Bt computation | "updated hourly" | Trimmed mean (after dropping the newest value at the end of the series, trim the top and bottom 25%) |
| ρV input for CV | "autocorrelation of the volatility series" | Lag-1 autocorrelation of the series of absolute successive differences |
| ρR baseline for CV | "autocorrelation of a random series" | 1/√n (white-noise asymptotic value) |

### 2.3 Sampling Requirements

ADF requires time-series input. With 2 samples, σ = D/√2 < D always holds, so any difference is judged anomalous; therefore `retriever.ADF_MIN_SAMPLES = 3`, and metric series with fewer than 3 samples skip evaluation. Where the metric series come from is described in Section 5.

---

## 3. AnomalyModel — Paper Section 5.1

### 3.1 Paper Algorithm

```
Is_Anomaly = METRIC_raw > threshold₁
             ∨ (METRIC_composite = trend ∧ METRIC_raw > threshold₂)
trend ∈ {0(stable), 1(sharp_decline), 2(slow_decline), 3(sharp_rise), 4(slow_rise), 5(fluctuating)}
```

M/N frequency control: an anomaly is confirmed only when M of the last N evaluations are True, preventing transient jitter.

### 3.2 Our Implementation

File: `src/agents/baselines/dbaiops/anomaly_model.py`

```python
class AnomalyModel:
    def __init__(self, model_id, trigger_vertex_id, equations)  # M/N derived from equations (taking the strictest value)
    def evaluate(self, metric_values) -> bool        # Equation evaluation + M/N frequency control
    def evaluate_raw(self, metric_values) -> bool    # Equation evaluation only, no frequency history accumulation

def compute_trend(values, sharp_threshold=0.3, slow_threshold=0.1, fluctuation_cv=0.5) -> int
```

Integration point (`DbaiopsAgent._record_trigger_anomaly_evaluation`):

1. Each evolution round evaluates the detection equations of the matched Trigger once;
2. `METRIC_raw` takes the latest value of the metric's accumulated series (`_resolve_metric_series` handles name mapping);
3. `METRIC_composite` is derived from the `METRIC_raw` series itself via `compute_trend`, keyed as `{metric_raw}#trend` (the graph's Trigger attributes do not carry composite vertices; in the paper, composite is the 10-minute window trend of raw);
4. Each round's evaluation results (raw verdict + M/N confirmed verdict) are recorded in `_anomaly_evaluations`, exported with the trace and written into the Anomaly Detection Verdict section of the diagnosis prompt.

Initial trigger matching is still keyword matching (see 7.3): the interactive entry point has no metrics to evaluate, so the equations are used to **confirm** triggers during evolution, not to discover them.

### 3.3 Differences from the Paper

| Aspect | Paper | Our implementation | Reason |
|------|------|-----------|------|
| Trend analysis algorithm | "10-minute window volatility analysis" | First-half vs second-half comparison + change-rate computation | The paper gives no concrete algorithm |
| METRIC_composite source | Continuously computed by the monitoring system | compute_trend() called on demand over the accumulated series | Adapts to interactive sampling |
| Threshold direction | Only ">" | Supports inverted ("<", e.g. cache_hit_ratio) | The graph contains inverse metrics |
| Trigger discovery | Equation evaluation (data-driven) | Keyword matching (text-driven) + equation confirmation | The Agent entry point has no metric history |

---

## 4. ExperienceGraph — Paper Section 4

### 4.1 Paper Algorithm

A heterogeneous directed graph of 6 vertex types (Trigger / Experience / Tool / Metric / Tag / Auxiliary) + 4 edge types (Containment / Relevance / Diagnosis / Synonym); a diagnosis path is a traversal path on the graph.

### 4.2 Our Implementation

File: `src/agents/baselines/dbaiops/graph.py`

```python
class ExperienceGraph:
    def __init__(self, graph_path)                 # Load the JSON graph
    def get_trigger_vertices(self) -> List[GraphNode]
    def get_neighbors(self, node_id, edge_type=None)
    def get_incoming_neighbors(self, node_id)
    def find_overlapping_models(self, trigger_id)   # Overlapping-model discovery for Proximity Discovery
    def create_cross_edge(self, source_id, target_id, edge_type)
    def get_diagnosis_paths(self, trigger_id, max_depth)  # Depth-limited BFS
```

Knowledge graph data: `data/knowledge_graph/pg_experience_graph.json` (56 nodes / 87 edges, 12 Triggers). The file's sha256 is verified by the factory's `_verify_artifact`; any change to the graph must also update `graph_sha256` in the experiment manifest.

### 4.3 Differences from the Paper

| Aspect | Paper | Our implementation | Reason |
|------|------|-----------|------|
| Graph scale | Production grade (hundreds of thousands of edges) | 56 nodes | Covering DBA-Bench's existing scenarios is sufficient |
| Graph storage | Graph database | JSON + in-memory adjacency lists | The scenario scale does not require a graph database |
| Cross-Edge | Persisted at runtime | Valid only within the current session | The Agent loads the graph independently on each run |

---

## 5. Two-Stage Graph Evolution — Paper Section 6.1

### 5.1 Paper Algorithm

```
repeat:
    Stage 1: Proximity Discovery → expand the graph → collect all Metrics on the evolution path
    Stage 2: ADF(metric series) → anomalies present? expand : terminate
until: terminated or max_depth
```

### 5.2 Our Implementation

File: `src/agents/baselines/dbaiops/retriever.py`

```python
class ExperienceRetriever:
    def __init__(self, graph, adf, max_depth=4, top_k=5, exclude_metric_types=None)
    def initialize(self, trigger_id) -> EvolutionState
    def take_pending_actions(self) -> List[(GraphNode, action)]      # Collect all unqueried Metric/Tool nodes on the path
    def take_snapshot_resample_actions(self) -> List[(GraphNode, action)]  # Resample SQL snapshot metrics
    def evolve(self) -> EvolutionState                                # ADF pruning + expansion decision (no arguments)
    def should_terminate(self) -> bool
    def get_experience_evidence(self) -> List[str]
```

**Each evolution round (the `DbaiopsAgent.solve` main loop):**

1. `take_pending_actions()`: collects and executes all unqueried Metric/Tool nodes on the expansion path (the paper's Stage 1 "collect metrics on the evolution path");
2. `take_snapshot_resample_actions()`: re-queries SQL snapshot metrics that have already been queried (slow_queries / topsql / dead_tuples from `SQL_BACKED_METRIC_QUERIES`, fetched via `execute_sql`). Snapshot-style metrics add only one sample per round; resampling lets their series grow with each round. query_metrics-style metrics already carry complete time series (series results replace the stored series wholesale) and need no resampling;
3. `_record_trigger_anomaly_evaluation()`: AnomalyModel detection-equation confirmation (Section 3);
4. `evolve()`: runs ADF on accumulated series of length ≥ `ADF_MIN_SAMPLES` (3); if anomalies exist and max_depth has not been reached → expand the path from the Triggers associated with the anomalous metrics, otherwise terminate.

**Metric sample extraction (`_extract_metrics_from_result`, dispatched by result kind):**

| Result type | Extraction rule | Accumulation key |
|---------|---------|--------|
| series (query_metrics) | The whole series replaces the stored one | `{metric_type}[{target}].{field}` |
| records / rows | Row count + sum of the declared value column | `{metric_type}.row_count`, `{metric_type}.{value_column}` |
| snapshot | Numeric fields appended one by one | `{metric_type}.{field}` |

Semantics of value_column in `SQL_BACKED_METRIC_QUERIES`: None for slow_queries/topsql (the trigger threshold is defined on counts, so row count is taken), and `n_dead_tup` for dead_tuples (sum of dead tuples across tables; the threshold of 10000 is defined on the total).

### 5.3 Differences from the Paper

| Aspect | Paper | Our implementation | Reason |
|------|------|-----------|------|
| Evolution trigger | Automatically triggered by a continuously running monitoring system | Driven round by round by the Agent evolution loop | Interactive evaluation framework |
| Metric collection | Direct access to the monitoring system | query_metrics / execute_sql APIs | DBA-Bench tool-surface limits; SQL details are not part of the query_metrics surface |
| Metric time series | Monitoring system's historical window | series directly available; snapshot metrics accumulated via per-round resampling | No independent collection channel in interactive mode |
| Termination condition | All ADF normal OR timeout | All ADF normal OR max_depth OR turn budget exhausted | No real-time timeout concept |
| Unsupported metrics | — | `exclude_metric_types` skips them when selecting nodes and marks them as queried | The TiDB surface lacks cache_hit_ratio etc. |

---

## 6. Structured Prompt — Paper Section 6.2

### 6.1 Paper Algorithm

prompt = ⟨Sa, Sl, Sm, Se, So⟩: Sa symptom description, Sl detection conditions, Sm key metric statistics, Se graph experience, So report components (Anomaly Validation / Root Cause Analysis ≤5 / Recovery Solution / Summary / SQL Context).

### 6.2 Our Implementation

File: `src/agents/baselines/dbaiops/prompts.py`

```python
DBAIOPS_SYSTEM_PROMPT       # LLM role definition
DBAIOPS_DIAGNOSIS_PROMPT    # Structured ⟨Sa, Sl, Sm, Se, So⟩ diagnosis report prompt (final generation by RootCauseAnalyser)
DBAIOPS_REMEDIATION_PROMPT  # Remediation loop entry prompt (includes detection-equation verdicts + ADF evidence)
DBAIOPS_FALLBACK_PROMPT     # LLM prompt when no graph path exists (tool contract provided by the native tool schema)
```

**Remediation loop entry (`_build_diagnosis_prompt`) fill-ins:**

| Component | Source |
|------|------|
| Anomaly Description | `self._alert` |
| Detection Condition | `_get_detection_condition()` (built from Trigger attributes) |
| Anomaly Detection Verdict | `_format_anomaly_verdict()` (M/N frequency confirmation results + latest evaluation values) |
| Metric Statistics & ADF Evidence | `_format_metric_evidence()` (n/latest/mean/min/max per accumulated metric + ADF score/σ/baseline/abnormal) |
| Collected Observations | `_format_observations()` (the last 10 raw results, each truncated to 200 characters) |
| O&M Experience | `retriever.get_experience_evidence()` |

**Final report (`_finalize_submission`)**: every termination path (plain-text reply / LLM submit / final-turn forced submission) uniformly calls `call_text(DBAIOPS_DIAGNOSIS_PROMPT…)` to generate the paper-style five-part report, which is submitted as the factor and summary of `structured_submission`; `outcome.changes` comes from `_executed_changes` (non-read-only actions actually executed during the remediation loop; SQL is judged read-only by SELECT/EXPLAIN/SHOW prefixes, manage_instance by set_config/restart), and when no remediation occurred it is explicitly labeled "No explicit remediation was reported".

### 6.3 Differences from the Paper

| Aspect | Paper | Our implementation | Reason |
|------|------|-----------|------|
| Sm content | Metric names + time range + thresholds | Key statistics per metric + ADF verdicts (truncated raw observation samples attached separately) | Interactive mode has no unified time-range concept |
| Report post-processing | Structured parsing + storage | Structured submission via `structured_submission` | DBA-Bench evaluation interface |
| Remediation execution | The paper only produces a report | The remediation loop actually executes changes before the report is generated | DBA-Bench Outcome evaluation requires real remediation |

---

## 7. Main Agent Integration — Paper Section 3 Overall Flow

### 7.1 Paper Flow

```
1. Alert input → AnomalyModel evaluation → match Trigger Vertex
2. Two-Stage Graph Evolution loop
3. RootCauseAnalyser (LLM) generates the diagnosis report
```

### 7.2 Our Implementation

File: `src/agents/baselines/dbaiops/agent.py`

```python
class DbaiopsAgent(BaseAgent):
    use_native_tools = True
    mode = "dbaiops"

    def solve(self):
        # 1. _ensure_initialized: load the graph + build ADF/Retriever/AnomalyModels
        # 2. TiDB: prefetch the query_history contract window + exclude unsupported metrics
        # 3. _match_trigger_by_keywords; no match → _run_llm_loop(fallback prompt)
        # 4. Evolution main loop (Section 5)
        # 5. _run_llm_loop(remediation prompt) → remediation + final report → structured submission
```

The internal LLM reuses native tool calling and token accounting through `LLMAgent` (`_next_llm_actions` / `_feed_tool_result` / `_next_final_submission` / `call_text`); all termination paths go through `_finalize_submission`. The `exit` action raises `RuntimeError` (consistent with LLMAgent behavior; not silently swallowed).

### 7.3 Differences from the Paper

| Aspect | Paper | Our implementation | Reason |
|------|------|-----------|------|
| Execution mode | One-shot pipeline execution | Interactive multi-turn Agent loop | DBA-Bench BaseAgent interface |
| Trigger matching | AnomalyModel equation evaluation | Keyword-matching entry + per-round equation confirmation | The Agent's first turn has no metric history |
| Remediation | Only produces a report | The LLM remediation loop actually executes changes | Outcome evaluation requirement |
| No graph match | Not mentioned | Fallback prompt (tool contract from the native schema) | Robustness |
| TiDB adaptation | The paper targets multiple database products | query_history window rewriting + metric-surface exclusion | Reuses the PG experience graph |

---

## 8. Overall Difference Summary

### 8.1 Architecture-Level Adaptations

The paper's DBAIOps is a continuously running monitoring system, while DBA-Bench is a discrete Agent evaluation framework: continuous monitoring → discrete queries; pipeline execution → interactive loops; real-time data → API calls. In addition, the paper's system only produces a diagnosis report, whereas DBA-Bench requires real remediation, so an LLM remediation loop is inserted before report generation.

### 8.2 Algorithm-Level Fidelity

| Component | Fidelity | Notes |
|------|--------|------|
| ADF 5-step algorithm | ★★★★★ | Formulas match step by step; evaluation only with ≥3 samples; threshold=1.2 derived from the mathematical behavior of F_state |
| AnomalyModel detection equations | ★★★★☆ | Equations + M/N frequency control + trend derivation wired into the evolution loop; entry matching is still keyword-based |
| ExperienceGraph structure | ★★★★★ | 6 vertex types + 4 edge types match |
| Two-Stage Evolution | ★★★★☆ | Batch collection + ADF pruning + anomaly-driven expansion match; snapshot metrics approximate time series via per-round resampling |
| Structured Prompt | ★★★★★ | ⟨Sa, Sl, Sm, Se, So⟩ used for the final report; Sm is key statistics + ADF evidence |
| Proximity Discovery | ★★★★☆ | Logic matches; Cross-Edges are valid only within a session |

### 8.3 Implementation Details Not Disclosed by the Paper (Our Own Choices)

| Detail | Paper description | Our choice |
|------|---------|-----------|
| θ (volatility threshold) | Not given | 10.0 (configurable) |
| score_threshold | Not given | 1.2 (configurable; derived from the mathematical behavior of F_state — do not change it to 0.7) |
| Bt computation method | "updated hourly" | Trimmed mean (drop the top and bottom 25%) |
| ρV input for CV | "autocorrelation of the volatility series" | Lag-1 autocorrelation of the series of absolute successive differences |
| ρR baseline for CV | "autocorrelation of a random series" | 1/√n (white-noise asymptotic value) |
| Trend analysis algorithm/thresholds | Not given | First-half vs second-half comparison + change rate; sharp=0.3, slow=0.1, cv=0.5 (configurable) |
| Path count limit | Not mentioned | top_k=5; 2 paths for overlapping models (configurable) |

### 8.4 Framework Adaptations (Necessary Additions beyond the Paper)

| Added mechanism | Reason |
|---------|------|
| Keyword-based trigger matching | The Agent's first turn has no metric history; equations confirm during the evolution rounds |
| LLM fallback prompt | The path taken when the graph cannot match the alert |
| Metric sample extraction (series/records/snapshot dispatch) | Adapts to DBA-Bench tool result formats |
| Excluded metric types | Graph metrics may not be on the target system's tool surface |
| outcome.changes tracking | DBA-Bench Outcome evaluation requires records of real remediation |

### 8.5 Known Limitations

1. **No historical baseline**: the paper's Bt is based on hourly historical data; we approximate it with statistics of the current series
2. **Limited graph scale**: covers only DBA-Bench's existing scenarios
3. **Snapshot metric time series are approximate**: one sample per evolution round; series length is limited by evolution depth and the turn budget
4. **No continuous learning**: the graph is static, and Cross-Edges do not persist across runs
5. **TiDB reuses the PG graph**: experience knowledge is not split by system

---

## 9. File Inventory

```
src/agents/baselines/dbaiops/
├── types.py            # GraphNode, GraphEdge, AnomalyEquation, ADFResult, DiagnosticPath, EvolutionState
├── adf.py              # ADF 5-step algorithm
├── anomaly_model.py    # AnomalyModel (equations + M/N frequency control) + compute_trend
├── graph.py            # ExperienceGraph heterogeneous graph
├── retriever.py        # ExperienceRetriever two-stage graph evolution + SQL_BACKED_METRIC_QUERIES
├── prompts.py          # SYSTEM / DIAGNOSIS / REMEDIATION / FALLBACK prompts
├── agent.py            # DbaiopsAgent main class + MockDbaiopsAgent
└── __init__.py         # Exports DbaiopsAgent, MockDbaiopsAgent

data/knowledge_graph/
└── pg_experience_graph.json   # PostgreSQL experience graph (sha256 verified by the factory)

tests/
└── test_dbaiops_agent.py      # Unit/integration tests (fully mocked, no real LLM calls)

examples/
├── run_dbaiops_baseline.py             # PG scenario entry script
└── run_mock_baseline_agents_trace.py   # MockDbaiopsAgent trace export smoke script
```

Factory registration: `DBAIOPS_SETTING_KEYS` in `src/agents/factory.py` (adf_score_threshold / adf_theta / frequency_m / frequency_n / graph_path / graph_sha256 / max_evolution_depth / top_k); settings is an exact key set.

---

## 10. TiDB Knowledge Graph

`data/knowledge_graph/tidb_experience_graph.json` (sha256 `249ce41f…`) is built uniformly from the TiDB 8.1 official documentation corpus
(`knowledge/tidb`, 3518 documents) plus scenario-targeted corpus (`knowledge/tidb/curated`, 34 documents): the corpus is processed uniformly through
the `tidb_unified` intermediate layer, and the final graph exposes no source identity to the Agent; chunk-level provenance lives in
`data/knowledge_graph/tidb_graph_provenance.jsonl` (a sidecar, for auditing only).

Composition: 210 triggers / 564 experiences / 114 tools / 22 metrics (exactly covering the full TiDB metric catalog,
`src/execution/tidb_metrics.py`) / 32 tags / 25 auxiliaries; 2067 edges (902 containment /
931 diagnosis / 234 relevance). Build discipline: only fault-class-level knowledge is included (mechanisms + differential diagnosis + remediation families);
case-instance solutions are not included. Thresholds are written only when the corpus gives an explicit value (currently 16 of 210 triggers carry complete
detection equations; the rest await scenario hardening/rerun calibration).

Selection rule: `DbaiopsAgent._ensure_initialized` picks the graph based on the target system detected via `set_tools` — a TiDB tool surface
(including `query_history` + `manage_cluster`) loads the TiDB graph; everything else loads the PG graph specified by `graph_path`;
the factory experiment configuration pins the target graph explicitly via `graph_path`/`graph_sha256`. On TiDB, snapshot metrics are not resampled
(query_history is a bounded frozen window, so resampling is meaningless), and ADF applies only to series-type metrics. Known gap: some paths of the
cross-shard anchor triggers (e.g. `trigger_slow_query`) do not yet have metric/tool leaves attached, pending additions.
