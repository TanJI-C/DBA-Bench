---
language: en
---

# Andromeda Baseline Implementation Document

## 1. Original Paper Algorithm

### 1.1 Overview

Andromeda (SIGMOD 2025) is a retrieval-augmented generation (RAG)-based DBMS configuration debugging system.
Given a natural-language problem description from the user, the system automatically diagnoses misconfigured knobs and generates remediation suggestions.

**Paper information:**
- Title: Automatic Database Configuration Debugging using Retrieval-Augmented Language Models
- Authors: Sibei Chen, Ju Fan, Bin Wu, Nan Tang, et al.
- Affiliation: Renmin University of China + Alibaba
- Published: SIGMOD 2025 (DOI: 10.1145/3709663)
- arXiv: 2412.07548

### 1.2 System Architecture (Two Stages)

#### Offline Stage

**1. Unified Embedding Learning for Heterogeneous Documents**

The paper trains a contrastive-learning encoder that maps three types of heterogeneous documents into a unified vector space:
- Historical questions (StackOverflow, MySQL Forum): describe "what went wrong"
- Troubleshooting manuals (MySQL/PostgreSQL Manual): describe "how to fix it"
- Configuration knob documentation: describes parameter meanings and valid value ranges

Contrastive learning objective:
```
L = -log(exp(sim(q, d+)/τ) / Σ exp(sim(q, d-)/τ))
```
where q is the encoded user question, d+ is a positive sample document, d- is a negative sample document, and τ is the temperature parameter.

**2. Logic-Chain Data Synthesis (Logic-Chain-Based Task Decomposition)**

To address the lack of annotated data, the paper designs a logic-chain synthesis strategy:
```
Triggering action → Problem-causing behavior → Problem-solving functionality → Corresponding evidence
```
By traversing this logic chain in reverse, GPT-4 is used to generate diverse training samples.

**3. LLM Fine-Tuning**

Based on Qwen2-7B:
- Continual Pre-Training (CPT): injects database domain knowledge (DBMS manuals, SQL documentation, StackOverflow Q&A)
- Supervised Fine-Tuning (SFT): trains evidence reasoning capability (using logic-chain-synthesized annotated data)

#### Online Stage

The paper's online inference is a **single-shot pipeline** consisting of three steps:

**Step 1: Multi-Source Evidence Retrieval**

```
Input: user natural-language question Q
Output: set of top-k relevant documents D = {d1, d2, ..., dk}

Algorithm:
1. Encode Q into a vector with the trained encoder E: v_q = E(Q)
2. Heterogeneous document retrieval:
   a. Historical question retrieval: compute sim(v_q, E(h_i)) for all historical questions {h_i}, take top-5
   b. Manual passage retrieval: compute sim(v_q, E(m_j)) for all manual passages {m_j}, take top-5
3. Merge results: D = top-5(historical questions) ∪ top-5(manual passages)
```

Key point: the encoder aligns the semantic spaces of "problem descriptions" and "solutions" through contrastive learning,
so that a query describing a problem can retrieve manual passages describing solutions.

**Step 2: Troublesome Telemetry Retrieval**

```
Input: time series data of 557 performance metrics (Prometheus, 1s sampling)
Output: top-k relevant anomaly descriptions T = {t1, t2, ..., tk}

Algorithm:
1. Anomalous Telemetry Detection (anomaly detection):
   For the time series X_i of each metric m_i:
   a. STL decomposition: X_i = Trend_i + Seasonal_i + Residual_i
      - Uses LOESS (Locally Estimated Scatterplot Smoothing)
      - period is set according to the sampling frequency
   b. Anomaly decision: if |Residual_i[t]| > threshold × σ(Residual_i),
      mark (m_i, t) as an anomaly point

2. Telemetry-to-Text Transformation (textualization):
   Generate a natural-language description for each anomaly point:
   t_j = "Metric {name} is anomalous at {timestamp},
          observed value {value}, deviates from the normal range by {deviation}"

3. Relevant Telemetry Selection (relevance ranking):
   a. Encode the anomaly descriptions with the same encoder E: v_t = E(t_j)
   b. Compute similarity to the user question: score_j = sim(v_q, v_t)
   c. Take the top-k most relevant anomaly descriptions
```

**Step 3: Configuration Reasoning**

```
Input: user question Q, retrieved documents D, anomaly descriptions T
Output: configuration change recommendations R = {(knob, value, rationale)}

Algorithm (two-stage prompting):

Phase 1 — Knob Identification:
  prompt = "Given the following evidence [Q + D + T], identify the configuration knobs relevant to the problem"
  knobs = LLM(prompt)  → ["shared_buffers", "work_mem", ...]

Phase 2 — Value Recommendation:
  prompt = "For knobs={knobs} with current values={current},
           recommend specific configuration values based on evidence [D + T]"
  recommendations = LLM(prompt)  → [{knob, value, rationale}, ...]
```

**Interactive and Adaptive Debugging**

The paper also trains a decision model that determines whether more information needs to be requested from the user:
- Input: user question + currently available evidence
- Output: (need more information?, specific collection steps)
- Training data source: StackOverflow interactions in which answerers ask questioners to provide more information

### 1.3 Evaluation Results

| Dataset | Metric | Andromeda | Best Baseline |
|--------|------|-----------|---------------|
| MySQL SO (174) | F1 | 0.441 | 0.332 |
| MySQL Forum (49) | F1 | 0.398 | 0.301 |
| PostgreSQL SO (57) | F1 | 0.425 | 0.310 |
| MySQL Runnable (100) | SuccessRate | 0.79 | 0.57 |

End-to-end runtime: ~5-7 seconds per question

---

## 2. Our Implementation Logic

### 2.1 Overall Architecture

Adapts Andromeda's single-shot pipeline into DBA-Bench's interactive Agent:

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
│                    │ (runs full pipeline│               │
│                    │  internally)       │               │
│                    └──────────┬─────────┘               │
│                               │                          │
│                    ┌──────────▼─────────┐               │
│                    │     SUBMIT         │               │
│                    └────────────────────┘               │
│                                                          │
│  Components:                                             │
│  ├── AndromedaTelemetry  (STL anomaly detection)         │
│  ├── AndromedaRetriever  (Dense Retrieval)               │
│  └── LLMAgent            (two-stage reasoning)           │
└─────────────────────────────────────────────────────────┘
```

### 2.2 State Machine Stages

**Turn 1: COLLECT_TELEMETRY**
```python
# Issue 7 query_metrics calls
actions = [
    {"api": "query_metrics", "args": {"metric_type": "cpu"}},
    {"api": "query_metrics", "args": {"metric_type": "memory"}},
    {"api": "query_metrics", "args": {"metric_type": "disk_io"}},
    {"api": "query_metrics", "args": {"metric_type": "slow_queries"}},
    {"api": "query_metrics", "args": {"metric_type": "cache_hit_ratio"}},
    {"api": "query_metrics", "args": {"metric_type": "qps"}},
    {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
]
# Results are associated with the corresponding metric_type in order via _pending_metric_queue
```

**Turn 2: COLLECT_LOGS_CONFIG**
```python
actions = [
    {"api": "read_log", "args": {"log_type": "pg_log", "lines": 100}},
    {"api": "manage_instance", "args": {"action": "get_config"}},
]
```

**Turn 3: ANALYZE_AND_REASON (core; runs the full pipeline internally)**
```python
def _do_analyze_and_reason(self):
    # Step 1: STL anomaly detection
    anomalies = self._telemetry.detect_anomalies()

    # Step 2: Telemetry-to-Text
    anomaly_texts = self._telemetry.get_anomaly_texts()

    # Step 3: Rank anomaly descriptions by semantic similarity
    ranked_texts = self._retriever.rank_telemetry_texts(alert, anomaly_texts)

    # Step 4: Document retrieval (historical Q&A + manual)
    qa_docs = self._retriever.retrieve_by_type(alert, "historical_qa")
    manual_docs = self._retriever.retrieve_by_type(alert, "manual")

    # Step 5: Phase 1 LLM — identify relevant knobs
    phase1_result = self._call_llm(PHASE1_PROMPT.format(...))
    knobs = parse_knobs(phase1_result)

    # Step 6: Phase 2 LLM — recommend specific values
    phase2_result = self._call_llm(PHASE2_PROMPT.format(...))
    diagnosis = parse_diagnosis(phase2_result)
```

**Turn 4: SUBMIT**
```python
actions = [{"api": "submit", "args": {"diagnosis": diagnosis_text}}]
```

### 2.3 STL Anomaly Detection Implementation

```python
class AndromedaTelemetry:
    def _stl_anomaly_detection(self, metric_type, values, timestamps):
        # Uses statsmodels.tsa.seasonal.STL (the same algorithm as the paper)
        stl = STL(values, period=self.period, robust=True)
        result = stl.fit()
        residuals = result.resid

        # Anomaly decision: residual exceeds ±threshold × σ
        std = np.std(residuals)
        mean = np.mean(residuals)
        for i, r in enumerate(residuals):
            severity = abs(r - mean) / std
            if severity >= self.anomaly_threshold:  # default 2.0
                # mark as anomalous
                ...
```

Fallback strategy:
- Time series length < 2×period → falls back to simple z-score detection
- Scalar metrics (non-time-series) → compared against known health thresholds
- statsmodels unavailable → falls back to z-score detection

### 2.4 Document Retrieval Implementation

```python
class AndromedaRetriever:
    def retrieve(self, query):
        # Encode the query with sentence-transformers
        query_emb = model.encode([query], normalize_embeddings=True)

        # Compute cosine similarity against all documents
        scores = np.dot(self._embeddings, query_emb.T).flatten()

        # Return top-k
        top_indices = np.argsort(scores)[::-1][:self.top_k]
        return [self._documents[i] for i in top_indices]

    def rank_telemetry_texts(self, alert, telemetry_texts):
        # Rank anomaly descriptions by semantic similarity to the alert
        alert_emb = model.encode([alert], normalize_embeddings=True)
        text_embs = model.encode(telemetry_texts, normalize_embeddings=True)
        scores = np.dot(text_embs, alert_emb.T).flatten()
        return [telemetry_texts[i] for i in np.argsort(scores)[::-1]]
```

Fallback strategy:
- sentence-transformers unavailable → falls back to keyword matching

### 2.5 File Structure

```
src/control/baselines/
    andromeda_agent.py       # Main Agent state machine
    andromeda_telemetry.py   # STL anomaly detection + Telemetry-to-Text
    andromeda_retriever.py   # Dense Retrieval (sentence-transformers)
    andromeda_prompts.py     # Two-stage reasoning prompt templates
    andromeda_types.py       # Data type definitions

knowledge/andromeda/
    pg_manual/               # PostgreSQL manual passages
    historical_qa/           # Historical Q&A pairs
```

---

## 3. Differences from the Original Paper

### 3.1 Difference Overview

| Component | Paper implementation | Our implementation | Difference type | Impact |
|------|---------|-----------|---------|------|
| Document encoder | Contrastively trained unified embedding model | sentence-transformers (bge-base-en-v1.5) | **Necessary substitution** | Retrieval quality may degrade |
| Reasoning LLM | Qwen2-7B (CPT + SFT) | General-purpose LLM (GPT-4/Claude) | **Necessary substitution** | Different reasoning capability |
| STL anomaly detection | STL (LOESS) | statsmodels.tsa.seasonal.STL | **Faithful reproduction** | None |
| Anomalous metric ranking | Contrastive-learning encoder + cosine | sentence-transformers + cosine | **Approximate substitution** | Ranking quality may differ slightly |
| Knowledge base source | StackOverflow + MySQL Forum + MySQL Manual | PostgreSQL Manual + constructed configuration Q&A | **Environment adaptation** | Different coverage |
| Interactive debugging | Fine-tuned model decides whether more information is needed | Fixed collection strategy (always collects all metrics) | **Simplification** | Loss of adaptivity |
| Execution mode | Single-shot pipeline | Multi-turn state machine | **Necessary adaptation** | Added turn overhead |
| Logic-chain data synthesis | GPT-4 generates training data | Not implemented (no fine-tuning) | **Omission** | Related to the reasoning LLM substitution |
| Continual Pre-Training | Continued pre-training on DBMS documents | Not implemented | **Omission** | Related to the reasoning LLM substitution |

### 3.2 Detailed Difference Analysis

#### Difference 1: Document Encoder (Necessary Substitution)

**Paper approach:**
- Trains a contrastive-learning encoder that explicitly aligns the semantic spaces of "problem descriptions" and "solutions"
- Uses InfoNCE loss, with (question, corresponding solution) as positive pairs and other documents in the batch as negatives
- The encoder understands the semantic association between "INSERT is slow" and "increase wal_buffers"

**Our implementation:**
- Uses the pre-trained bge-base-en-v1.5 (a general-purpose semantic retrieval model, matching `BAAI/bge-base-en-v1.5` in `src/agents/baselines/andromeda/`)
- Not fine-tuned for the DBMS configuration debugging task
- Relies on the model's general semantic understanding capability

**Reason for substitution:**
The paper's GitHub repository is inaccessible (404), so the pre-trained encoder weights cannot be obtained.
bge-base is currently the closest substitute — also a dense retrieval model supporting semantic retrieval.

**Impact assessment:**
- Cross-type retrieval capability degrades: the paper's encoder can map a "problem" near its "solution",
  whereas a general-purpose model can only perform literal semantic similarity matching
- For explicitly described problems (e.g. "shared_buffers is too small"), the impact is small
- For implicit problems (e.g. "queries are slow" → work_mem-related documents need to be retrieved), the impact is larger

#### Difference 2: Reasoning LLM (Necessary Substitution)

**Paper approach:**
- Performs Continual Pre-Training + Supervised Fine-Tuning on Qwen2-7B
- CPT data: DBMS manuals, SQL documentation, StackOverflow Q&A
- SFT data: logic-chain-synthesized (question, evidence, recommendation) triples
- The model learns the mapping "given evidence → output structured recommendations"

**Our implementation:**
- Uses a general-purpose LLM (GPT-4 or Claude)
- Emulates the two-stage reasoning structure via prompt engineering
- Relies on the LLM's general reasoning capability and pre-trained knowledge

**Reason for substitution:**
The paper's training data and training code are unavailable. Logic-chain data synthesis requires a large amount of manually annotated seed data.

**Impact assessment:**
- A general-purpose LLM (GPT-4) may reason better than the fine-tuned Qwen2-7B
- But lacking targeted training, its specialized knowledge of DBMS configuration may be less precise than the fine-tuned model
- Output format stability may be worse than the fine-tuned model (requiring stronger prompt constraints)

#### Difference 3: Execution Mode (Necessary Adaptation)

**Paper approach:**
- Single-shot: receives the question → outputs the diagnosis and recommendations in one pass
- Latency of 5-7 seconds
- Does not interact with the database

**Our implementation:**
- Multi-turn state machine: the full pipeline completes in 4 turns
- Turn 1: collect telemetry data (interacts with the database)
- Turn 2: collect logs and configuration
- Turn 3: perform analysis and reasoning internally
- Turn 4: submit the diagnosis

**Reason for adaptation:**
DBA-Bench's Orchestrator requires the Agent to interact with the environment through the `get_next_input()` → `dispatch()` →
`add_tool_result()` loop. Andromeda's pipeline must be split into multiple turns.

**Impact assessment:**
- Adds turn overhead, but does not affect diagnosis quality
- Actually strengthens the paper's approach: the paper assumes telemetry data is already available,
  while our implementation actively collects data from the environment, which is closer to a real scenario

#### Difference 4: Interactive Debugging (Simplification)

**Paper approach:**
- Trains a decision model to determine whether more information must be requested from the user
- If information is insufficient, generates concrete data collection instructions (e.g. "please run SHOW INDEX...")
- Trained on StackOverflow interaction data

**Our implementation:**
- Fixed collection strategy: always collects all available metrics, logs, and configuration
- Does not decide "whether more information is needed"

**Reason for simplification:**
1. No training data
2. In the DBA-Bench environment all metrics are directly accessible, so there is no need to "ask the user"
3. A fixed collection strategy is fairer in a benchmark scenario (does not depend on decision-model quality)

#### Difference 5: Knowledge Base (Environment Adaptation)

**Paper approach:**
- 174 MySQL StackOverflow questions
- 49 MySQL Forum questions
- 57 PostgreSQL StackOverflow questions
- Sentence-split complete MySQL/PostgreSQL manuals

**Our implementation:**
- PostgreSQL configuration manual excerpts
- Constructed Q&A for common configuration problems

**Reason for adaptation:**
DBA-Bench primarily uses PostgreSQL environments, so the knowledge base must match the target database.
The paper's complete knowledge base has not been released.

### 3.3 Core Methodology Retained

The following core methodology from the paper is faithfully retained:

1. **STL seasonal decomposition for anomaly detection** — uses the same statsmodels STL algorithm
2. **Telemetry-to-Text transformation** — converts anomalies into natural-language descriptions for LLM reasoning
3. **Semantic similarity ranking of anomalies** — selects the top-k anomalies by relevance to the question
4. **Two-stage reasoning structure** — Phase 1 identifies knobs → Phase 2 recommends values
5. **Multi-source evidence fusion** — historical Q&A + manual + telemetry data, three evidence streams fed into the LLM
6. **Dense Retrieval** — semantic vector retrieval (albeit with a different encoder)

### 3.4 Expected Impact on Evaluation Results

| Factor | Expected impact direction | Reason |
|------|------------|------|
| General-purpose LLM replaces the fine-tuned model | ↑ or → | GPT-4 reasons strongly, but lacks specialized fine-tuning |
| General-purpose encoder replaces contrastive learning | ↓ | Cross-type retrieval capability degrades |
| Actively collecting telemetry data | ↑ | The paper assumes the data already exists; we actively obtain it |
| Fixed collection strategy | → | Information is always accessible in the benchmark |
| Smaller knowledge base | ↓ | Retrieval hit rate may drop |

**Overall expectation:** On configuration debugging scenarios, performance should approach the level reported in the paper,
but it may drop on scenarios requiring precise cross-type retrieval.
