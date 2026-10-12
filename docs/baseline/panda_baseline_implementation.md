---
language: en
---

# Panda Baseline Implementation Document

## Paper Overview

**Paper**: "Panda: Performance Debugging for Databases using LLM Agents" (AWS AI Labs)

**Core idea**: Provide context to a pre-trained LLM through Context Grounding so that it generates actionable diagnosis recommendations tailored to the specific database problem, rather than generic, boilerplate advice.

**The paper's 5 components**:
1. Question Verification Agent (QVA) — filters out irrelevant queries
2. Grounding Mechanism — document retrieval + T2T + context aggregation
3. Verification Mechanism — NLI verification + source attribution
4. Feedback Mechanism — vector-store feedback cache
5. Affordance Mechanism — impact estimation + high-risk flagging

---

## 1. Grounding Mechanism (Context Construction)

### 1.1 Paper Algorithm

**Document Retriever**:
- Uses an embedding model to vectorize the user query and the document library (troubleshooting docs + historical tickets)
- Retrieves the top-K relevant documents by cosine similarity
- Splits long documents into chunks, keeping only the top-3 relevant chunks

**Feature Extractor (Telemetry-to-Text)**:
- From the provided list of metric names, identifies the top-K (K=3) relevant metrics via embedding similarity
- Queries the data lake for raw time series (last 24 hours by default)
- Uses a change point detection algorithm to split the time series into a "problem interval" and a "baseline interval"
- Extracts interpretable features: trend, seasonality, mean, p95, correlation score
- Identifies anomalous metrics (metrics with at least one anomalous statistic)
- Identifies anomalous SQL queries (SQL statements with at least one anomalous query statistic)
- Collects the raw text of the anomalous SQL + Database/Information Schema

**Context Aggregator**:
- Stores all extracted features as JSON-structured text
- Merges them with the retrieved documents and tickets
- Limits prompt size: keeps only the top-3 relevant document chunks + top-3 anomalous SQL statements

### 1.2 Our Implementation

**File**: `src/control/baselines/panda_grounding.py`

**PandaDocumentRetriever**:
- Uses `sentence-transformers` (all-MiniLM-L6-v2) for embeddings
- Document loading: supports .txt/.md/.json files, chunked by paragraph
- Retrieval: cosine similarity top-K
- Fallback: keyword matching (word-overlap counting) when sentence-transformers is unavailable

**PandaTelemetryToText**:
- `extract_features(metric_name, values)`: extracts features for a single metric
  - Trend: first-half mean vs second-half mean; relative_change > 0.15 is judged increasing/decreasing
  - Mean / P95: computed with numpy statistics
  - Change Points: rolling-mean comparison with a threshold of 1.5*std
  - Seasonality: autocorrelation detection (lag = len/4)
- `compute_correlations(features)`: cross-metric Pearson correlation (|r| > 0.7 counts as correlated)
- `identify_problematic_metrics(features)`: identifies metrics with anomalous trends or high correlation

**PandaContextAggregator**:
- Aggregates alert + telemetry_text + documents + schema_info + feedback into a JSON prompt

### 1.3 Differences from the Paper

| Aspect | Paper | Our implementation | Reason |
|------|------|-----------|------|
| Metric selection | Embedding similarity identifies the top-3 relevant metrics from documents | A predefined list of standard metrics (cpu, memory, slow_queries, etc.), all collected | DBA-Bench environment metrics are limited and known; dynamic selection is unnecessary |
| Time series source | Queries the data lake for 24h raw data | Gets the environment-returned data via the `query_metrics` API | Adapts to the Orchestrator's tool dispatch mechanism |
| Change point algorithm | A dedicated algorithm from reference [21] | Rolling-mean comparison + 1.5σ threshold | Lightweight implementation, no external dependencies |
| Anomalous SQL identification | Anomaly detection based on query statistics | Relies on the `slow_queries` metric + LLM analysis | The environment API does not directly expose per-query statistics |
| Document source | 2.5K troubleshooting docs + historical tickets | Configurable local document paths (knowledge_paths) | The benchmark environment has no AWS document library |

---

## 2. Verification Mechanism

### 2.1 Paper Algorithm

**Answer Verification (NLI)**:
- Frames verification as a Natural Language Inference (NLI) task
- Hypothesis = the generated diagnosis answer
- Premise = the retrieved documents and tickets (NOT tool execution results)
- The LLM acts as the verifier producing a label: accept / reject / neutral
- If reject or neutral: re-run the generation process to get a new answer and verify again
- After K=3 failures, output a failure message + a list of relevant documents
- Tickets are removed from the documents shown to the user (they contain sensitive data)

**Source Attribution**:
- After verification passes, provides the retrieved document passages as reference sources
- Splits the output and the reference passages into individual sentences
- If an output sentence matches a reference passage verbatim, provides an inline citation [s_N]

### 2.2 Our Implementation

**File**: `src/control/baselines/panda_verification.py`

**PandaVerifier**:
- `verify(hypothesis, retrieved_docs, telemetry_summary)`:
  - Premise = the retrieved documents (`retrieved_docs`) + the telemetry summary text
  - Hypothesis = the agent-generated root_cause diagnosis
  - Builds an NLI prompt asking the LLM to judge entail / contradict / neutral
  - Parses the LLM response to extract the verdict + reasoning
- Retry logic is implemented as a while loop inside `PandaAgent.get_next_input()`:
  - Verification fails → append a retry prompt to the LLM → regenerate the diagnosis → verify again
  - At most K=3 retries

**PandaSourceAttribution**:
- `attribute(output_text, source_docs)`:
  - Splits the output text into sentences by periods
  - Splits each source document into sentences by periods
  - Computes similarity between output sentences and source-document sentences (embeddings or word overlap)
  - Adds an inline citation `[s_N]` when the similarity exceeds the threshold
  - Fallback: uses the word-overlap ratio when sentence-transformers is unavailable

### 2.3 Differences from the Paper

| Aspect | Paper | Our implementation | Reason |
|------|------|-----------|------|
| Premise composition | Retrieved documents + historical tickets | Retrieved documents + telemetry summary text | No ticket data source; the telemetry summary is used instead |
| Behavior after failure | Outputs a failure message + relevant document list | Still submits the last generated diagnosis after retries are exhausted | The benchmark requires the agent to always submit a result for scoring |
| Attribution granularity | "taken verbatim" (word-for-word match) | Word-overlap ratio > 0.3 or embedding similarity > 0.7 | Verbatim matching is too strict; the LLM rephrases statements |
| Ticket filtering | Removes tickets from what is shown to the user (sensitive data) | No distinction between documents and tickets | The benchmark environment has no sensitive ticket data |

---

## 3. Feedback Mechanism

### 3.1 Paper Algorithm

- The user provides binary feedback on each generated response: "Helpful" or "Not Helpful"
- Feedback + user query + response are stored in a vector store, indexed by the embedding of the user query
- When generating a new response, the top-K similar historical responses are retrieved by embedding similarity
- Retrieval rule: at least 1 and at most 3 positive feedback items + at least 1 and at most 3 negative feedback items
- Added to the prompt as few-shot in-context learning examples

### 3.2 Our Implementation

**File**: `src/control/baselines/panda_feedback.py`

**PandaFeedbackStore**:
- Stores `FeedbackEntry` objects (query, actions_taken, observations, outcome)
- `store(entry)`: stores the entry + computes the embedding (when available)
- `store_interaction(query, actions, observations, outcome)`: convenience method
- `retrieve_similar(query, top_k)`:
  - Embedding path: cosine similarity retrieval, separating positive/negative
  - Keyword path: word-overlap counting (with stopword filtering)
- `get_recent(n)`: fetches the most recent N interaction records

### 3.3 Differences from the Paper

| Aspect | Paper | Our implementation | Reason |
|------|------|-----------|------|
| Feedback source | The user explicitly provides "Helpful/Not Helpful" | Each interaction is recorded automatically, with the outcome field marking the result | The benchmark has no human feedback step; automatic recording is used instead |
| Storage medium | Persistent vector store | In-memory List + numpy array | Single-run scenario; persistence is unnecessary |
| Retrieval strategy | At least 1 and at most 3 positive + at least 1 and at most 3 negative | Same as the paper: positive[:top_k] + negative[:top_k] | Faithful reproduction |
| Embedding model | text-embedding-ada-002 (OpenAI) | all-MiniLM-L6-v2 (sentence-transformers) | Runs locally, no API cost |

---

## 4. Affordance Mechanism

### 4.1 Paper Algorithm

**Impact Estimation**:
- Goal: estimate how database performance changes after executing a given remediation action
- Two approaches:
  - Generic (imprecise): infer the usual impact on similar databases from the retrieved documents and tickets
  - Specific: use an external behavioral model to predict performance changes (e.g. OtterTune, MB2)
- The paper currently relies mainly on the Generic approach
- Uses a simple statistical behavioral model for major operations (instance type changes, engine version changes, etc.)

**High-Risk Action Flagging**:
- Maintains a prior list of high-risk operations (DROP, DELETE, isolation level changes, etc.)
- If a recommendation contains a high-risk operation, it is highlighted in the output

### 4.2 Our Implementation

**File**: `src/control/baselines/panda_affordance.py`

**PandaAffordance**:
- `assess_action(action, context)`:
  - Rule layer: quickly classifies the risk level based on the SQL pattern and API type
    - `query_metrics`, `read_log` → no-risk, always passes
    - `execute_sql` + SELECT/EXPLAIN → low-risk, passes
    - `execute_sql` + DDL (CREATE INDEX, VACUUM, ANALYZE) → medium-risk
    - `execute_sql` + DROP/DELETE/TRUNCATE/ALTER → high-risk
    - `manage_instance` + restart/stop/reboot → high-risk
  - LLM layer: for medium/high-risk operations, calls the LLM to estimate the concrete impact
    - Input: operation description + current context (telemetry + documents)
    - Output: expected impact description + risk assessment
  - Heuristic layer: fallback estimates when the LLM is unavailable
    - CREATE INDEX → "May cause brief lock, improves query performance"
    - VACUUM → "Reclaims dead tuple space, brief I/O spike"
    - restart → "Service interruption 10-30s, clears all connections"
- `filter_actions(actions, evidence_count, context)`:
  - Filters out high-risk operations with insufficient evidence
  - `require_evidence_for_high_risk`: high-risk operations require at least 2 pieces of supporting evidence

### 4.3 Differences from the Paper

| Aspect | Paper | Our implementation | Reason |
|------|------|-----------|------|
| Impact estimation precision | External behavioral models (OtterTune, MB2) predict concrete metric changes | LLM estimation + heuristic rules | No external behavioral model available |
| Degree of quantification | Predicts concrete performance metric deltas (e.g. active sessions decrease by X%) | Qualitative descriptions ("brief I/O spike", "improves query performance") | Lacks historical data to train a behavioral model |
| High-risk list | Maintained as a prior | Regex matching on SQL patterns + API type rules | Equivalent implementation, easier to extend |
| Action filtering | Only highlights, does not block | Configurable blocking (require_evidence_for_high_risk) | The benchmark must prevent the agent from executing destructive operations |

---

## 5. Question Verification Agent (QVA)

### 5.1 Paper Algorithm

- Embeds the user query and runs a similarity search against the document library
- If the highest similarity < λ=0.85, the query is judged "out-of-context"
- For out-of-context queries, further matches AWS service description documents and recommends related services
- For completely irrelevant queries (e.g. "how is the weather today"), the user is asked to revise the query

### 5.2 Our Implementation

**Not implemented**.

### 5.3 Difference Notes

QVA is not applicable in DBA-Bench. The benchmark's Orchestrator sends predefined alert messages directly to the agent; there is no scenario in which the user inputs an irrelevant query. All queries are valid database performance problems.

---

## 6. Overall Architecture Adaptation

### 6.1 Paper Architecture vs DBA-Bench Architecture

**Paper**: Panda is a single-turn Q&A system
- User question → Grounding → LLM generation → Verification → answer returned
- All information is collected and processed in a single call

**DBA-Bench**: multi-turn Agent loop
- Orchestrator-driven: `get_next_input()` → `dispatch(action)` → `add_tool_result()` → loop
- The Agent must proactively collect information (it cannot fetch all telemetry data at once)

### 6.2 Adaptation Design

```
Turn 1 (Proactive Grounding):
  └── Return the predefined metric collection + schema query actions (no LLM needed)

Turn 2+ (After receiving metric results):
  ├── T2T: convert the received numeric metrics into text features
  ├── Correlation: compute cross-metric correlations
  ├── Anomaly: identify anomalous metrics
  ├── RAG: retrieve documents based on the alert + anomaly summary
  ├── Aggregate: build the JSON-structured context
  ├── LLM: generate diagnosis + actions after injecting the context
  ├── Affordance: assess action risks and filter high-risk operations
  └── Return the action list

Submit Turn:
  ├── Verification: NLI check of whether the diagnosis is supported by the documents
  │   ├── entail → Source Attribution → submit
  │   └── reject/neutral → regenerate (up to K=3 times)
  └── Submit root_cause + solution (with inline citations)
```

### 6.3 Progressive Mode Design

| Mode | Components | Purpose |
|------|------|------|
| `panda_basic` | LLM + T2T | Ablation: grounding only, no RAG |
| `panda_rag` | + Document Retriever | Ablation: adds document retrieval |
| `panda_verified` | + Verification + Attribution | Ablation: adds the verification mechanism |
| `panda_full` | + Affordance + Feedback | The complete Panda pipeline |

---

## 7. File Structure

```
src/control/baselines/
├── panda_agent.py          # Main Agent class, coordinates all components
├── panda_grounding.py      # Document Retriever + T2T + Context Aggregator
├── panda_verification.py   # NLI Verifier + Source Attribution
├── panda_affordance.py     # Impact Estimation + Risk Flagging
├── panda_feedback.py       # Vector Store Feedback Cache
├── panda_prompts.py        # All prompt templates
├── panda_types.py          # Data class definitions

examples/
├── run_panda_baseline.py   # Example run script
```

---

## 8. Summary: Key Differences at a Glance

| # | Paper design | Our implementation | Difference type |
|---|---------|-----------|---------|
| 1 | Single-turn Q&A | Multi-turn Agent loop | Architecture adaptation |
| 2 | QVA filters irrelevant queries | Not implemented | Not applicable |
| 3 | Data lake queries 24h telemetry | Orchestrator tool dispatch | Architecture adaptation |
| 4 | Embedding selects the top-3 relevant metrics | Predefined standard metric list | Simplification (limited environment metrics) |
| 5 | Dedicated change point algorithm | Rolling mean + 1.5σ | Lightweight substitute |
| 6 | text-embedding-ada-002 | all-MiniLM-L6-v2 + keyword fallback | Localized + fallback |
| 7 | External behavioral model estimates impact | LLM + heuristic rules | No external model |
| 8 | Explicit user feedback | Automatic recording of interaction outcomes | Benchmark has no human step |
| 9 | Outputs a failure message after failure | Still submits after retries are exhausted | Required for benchmark scoring |
| 10 | Verbatim-match attribution | Word overlap / embedding similarity | Relaxed matching (LLM rephrasing) |

**Core designs faithfully reproduced**:
- Verification premise = retrieved documents (not tool results)
- Verification retry = regenerate the diagnosis (not collect more evidence)
- T2T extracts trend/mean/p95/change_points/seasonality/correlation
- Feedback distinguishes positive/negative feedback
- Source Attribution provides sentence-level inline citations
- Affordance flags high-risk operations
