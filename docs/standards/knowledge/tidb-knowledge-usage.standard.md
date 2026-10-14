---
doc_id: standard.knowledge.tidb-knowledge-usage
doc_type: standard
status: canonical
audience: [runtime_agent, maintainer, authoring, reviewer]
exposure: public
scope: [tidb, knowledge]
summary: Defines how to use the existing TiDB unified knowledge base, including lazy embedding startup, explicit service startup, query interfaces, test scripts, and failure behavior.
source_of_truth: code
related: [standard.knowledge.tidb-knowledge-construction]
language: en
---

# TiDB Unified Knowledge Base Usage Standard

This document defines only how to use the current TiDB unified knowledge base. Its intended
readers are the Agent runtime that needs to query the knowledge base, maintainers running smoke
tests, and developers integrating the unified retrieval interface in knowledge-driven scenarios.

This document does not describe how the raw corpus is merged, how the three corpus layers are
materialized, or how indexes are generated; those are defined by the
[TiDB Knowledge Base Construction Principles and Implementation Standard](./tidb-knowledge-construction.standard.md).
It also does not define the knowledge-driven scenario design philosophy, concrete fault mechanisms,
or DP/OP/SP contracts.

## 1. First Distinguish the Two Kinds of "Startup"

In the current system, "starting the knowledge base" is not starting a standalone database
service. The official knowledge base consists of two parts:

| Part | Actual form | Created automatically by a query |
|---|---|---:|
| Knowledge index | A SQLite file or Chroma persisted collection in the main repository | No |
| Embedding service | A local HTTP service, default 127.0.0.1:8765 | Can be auto-started for Chroma queries |

Therefore:

- Before first use, the index must already be built, with a manifest.json in the corresponding
  directory;
- Chroma queries need the embedding service. Requests check the service through the unified
  runtime; when the service does not exist, the local endpoint is started as a detached background
  process under a lock;
- SQLite queries do not need the embedding service;
- Queries never build the index automatically and never fall back to a stale index, SQLite, web
  documents, or hardcoded summaries;
- TiDBKnowledgeBase is an index-and-query object, not a daemon that must be kept running in the
  foreground separately.

This boundary matters: if the index is missing, complete the build first per the
[construction standard](./tidb-knowledge-construction.standard.md); if the Chroma embedding
service is missing, queries may auto-start it following the rules below.

## 2. Default Runtime Configuration

All default paths are resolved through REPOSITORY_ROOT in src/project_paths.py. Linked WorkTrees
and the main WorkTree share the corpus, indexes, logs, and runtime files in the main repository.

The current hierarchical TiDB knowledge base defaults are:

| Configuration item | Default value |
|---|---|
| knowledge mode | hierarchical |
| serving source | knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl |
| collection | tidb81_unified_docs |
| Chroma persist dir | data/knowledge_bases/tidb81_unified_chroma |
| SQLite persist dir | data/knowledge_bases/tidb81_unified_docs |
| embedding model | Qwen/Qwen3-Embedding-4B |
| embedding device | cuda |
| embedding endpoint | http://127.0.0.1:8765 |

Relative paths in the table above are relative to the main repository root (`<repo-root>`, i.e.
the checkout root of this repository).

The current official TiDB Agent entry point always uses hierarchical. general is a legacy
configuration for the generic directory source and must not be used as the entry point for new
knowledge-driven scenarios.

## 3. Automatic and Explicit Startup

### 3.1 Automatic behavior during normal queries

The call chain is:

~~~
TiDBKnowledgeBase.query()
  -> Chroma query
  -> request_embeddings()
  -> ensure_embedding_model()
  -> GET /health
  -> reuse the ready service
     or start the local detached service under a lock
~~~

ensure_embedding_model() lives in src/knowledge/embedding_model_runtime.py and is the only
automatic startup entry point.

Automatic behavior has these strict boundaries:

- /health returns status=ready and the model name matches: reuse directly and do not load the
  model again;
- the local endpoint is unreachable: take the per-port lock, start
  scripts/start_embedding_model.py --serve, and wait for ready;
- the endpoint returns a model mismatch: fail immediately and do not overwrite the running
  service;
- the endpoint is occupied by another service or returns an invalid health response: fail
  immediately and do not replace it;
- the endpoint is remote and unreachable: fail immediately and do not attempt to log in or start
  remotely;
- the started process exits, the wait times out, or the GPU is unavailable: fail immediately;
- no automatic switch to CPU, no automatic switch to an older model, and no automatic switch to
  SQLite.

The query script does not swallow these errors. The Agent tool returns the error, together with
the mode, query, filters, and parameters, to the caller; a Scenario evaluator must not disguise
tool errors as ordinary diagnosis results.

### 3.2 Explicit startup for pre-warming

To explicitly ensure the service is ready before bulk experiments, index builds, or manual
queries, run:

~~~
conda run -n aiops python scripts/start_embedding_model.py \
  --model Qwen/Qwen3-Embedding-4B \
  --device cuda \
  --host 127.0.0.1 \
  --port 8765
~~~

By default this command is also the "check and ensure" entry point:

- it returns quickly when the service is already ready;
- it starts the service in the background and waits for ready when it does not exist;
- after the command returns, the embedding service keeps running detached from the current
  terminal;
- logs are written to logs/embedding_model.log in the main repository.

For a read-only check only, use:

~~~
conda run -n aiops python scripts/start_embedding_model.py \
  --status \
  --model Qwen/Qwen3-Embedding-4B \
  --host 127.0.0.1 \
  --port 8765
~~~

--status does not start the service; the exit code is 0 when ready and 1 in any other state.

### 3.3 Extra ports or extra endpoints

When another local service or another port is needed, the port, model, and device must be given
explicitly. For example:

~~~
conda run -n aiops python scripts/start_embedding_model.py \
  --model Qwen/Qwen3-Embedding-4B \
  --device cuda \
  --host 127.0.0.1 \
  --port 8766
~~~

Then point an explicit query at that endpoint:

~~~
conda run -n aiops python scripts/query_tidb_unified_knowledge.py \
  --embedding-url http://127.0.0.1:8766 \
  --embedding-model Qwen/Qwen3-Embedding-4B \
  --query "Online Unsafe Recovery failed stores Finished"
~~~

You can also set it before the Python process starts:

~~~
export AIOPS_EMBEDDING_MODEL_URL=http://127.0.0.1:8766
~~~

Each port uses its own lock file /tmp/aiopsbench-embedding-model-<port>.lock. Extra endpoints do
not change the Agent's default entry point; the query CLI clears AIOPS_EMBEDDING_MODEL_URLS to
ensure that one query uses exactly one explicit endpoint. AIOPS_EMBEDDING_MODEL_URLS is only for
controlled parallel requests during bulk Chroma index builds; see the construction standard for
details.

--serve is the runtime's internal entry point for raising the detached service and must not become
a second startup path for callers. When an explicit start is needed, use the default command above
so that checking, locking, waiting, and error handling remain with the same runtime
implementation.

### 3.4 Behavior after a machine restart

The current background process is a persistent process detached from the invoking command, not a
systemd or boot-time service. After a machine restart:

- index files remain in the main repository unless actively deleted;
- the embedding service is not started automatically by the operating system;
- the first Chroma query, or an explicit run of start_embedding_model.py, starts it again per the
  rules above;
- if the service must be ready at boot, host it with an external process manager, but do not
  implement a second launcher inside the knowledge base code.

## 4. Access Interfaces

### 4.1 Command-line query script

For manual queries, recall verification, and latency measurement, use:

~~~
conda run -n aiops python scripts/query_tidb_unified_knowledge.py \
  --query "alloc-id recovery high-water"
~~~

The script uses the Chroma hierarchical index by default. Common parameters:

| Parameter | Purpose |
|---|---|
| --query | required; a natural-language question, configuration name, SQL identifier, or component concept |
| --backend chroma\|sqlite | explicitly choose the index backend; default chroma |
| --top-k 1..20 | number of returned snippets; default 5 |
| --source-scope | self_managed, cloud, kubernetes, developer, shared, or all |
| --kb-type | architecture, configuration, observability, diagnosis, operation, performance, recovery, data_pipeline, reference, release |
| --component | components such as TiDB, TiKV, PD, TiFlash, TiCDC, BR, and Lightning |
| --max-chars-per-result | body length per result, range 200..8000 |
| --embedding-url | the endpoint used by Chroma |
| --embedding-model | the expected model name |
| --json | output only source-neutral JSON |

For example:

~~~
conda run -n aiops python scripts/query_tidb_unified_knowledge.py \
  --query "Online Unsafe Recovery failed stores Finished" \
  --top-k 5 \
  --kb-type recovery \
  --component pd \
  --json
~~~

Use --backend sqlite only when FTS5 queries or index-contract checks are explicitly needed:

~~~
conda run -n aiops python scripts/query_tidb_unified_knowledge.py \
  --backend sqlite \
  --query "tidb_server_memory_limit tidb_mem_oom_action" \
  --json
~~~

The Agent-facing result fields of the script output are fixed:

~~~
status
query
latency_ms
count
results[].rank
results[].score
results[].title
results[].version
results[].kb_type
results[].component
results[].source_scope
results[].content
~~~

The CLI script itself may keep latency information for human observation, but the Scenario runtime
must not query the knowledge base by calling it through subprocess.

### 4.2 Python API

Maintenance scripts, tests, and runtime internals use TiDBKnowledgeBase directly:

~~~
from src.knowledge.tidb_knowledge_base import TiDBKnowledgeBase

kb = TiDBKnowledgeBase(
    backend="chroma",
    knowledge_base_mode="hierarchical",
)
result = kb.query(
    "alloc-id recovery high-water",
    source_scope="all",
    top_k=5,
    kb_type="recovery",
    component="pd",
    max_chars_per_result=1600,
)
~~~

The constructor takes the main repository paths from src/project_paths.py and uses the
hierarchical default source, collection, and persist dir. Callers must not, on their own:

- assemble knowledge/tidb_unified paths;
- initialize SentenceTransformer;
- probe or start the embedding endpoint;
- read SQLite/Chroma internal files;
- switch to SQLite after a Chroma error.

Internal results returned by kb.query() include maintenance fields such as index, persist_dir,
source commit, and materialized corpus hash. They can be used for maintenance and audit but must
not be exposed directly to the Agent.

### 4.3 TiDB Agent tool

The TiDB Agent uses one unified tool:

~~~
search_knowledge(
  query,
  source_scope="all",
  top_k=5,
  kb_type=null,
  component=null,
)
~~~

The tool always calls with knowledge_base_mode="hierarchical" and fixes max_chars_per_result to
1600 on every call. The tool returns only these top-level and result fields:

~~~
status
query
source_scope
kb_type
component
top_k
count
results[].rank
results[].score
results[].title
results[].version
results[].kb_type
results[].component
results[].source_scope
results[].content
~~~

The runtime implementation lives in _search_tidb_knowledge() and search_knowledge() in
src/execution/environments/tidb.py; the tool schema is in src/execution/tidb_tool_definitions.py.

Knowledge results provide only general TiDB product knowledge — never the current run's Stores,
Regions, tables, checkpoints, TSO, dynamic objects, remediation results, or evaluator conclusions.
The Agent must re-bind knowledge results to live evidence from execute_sql, query_metrics,
read_log, manage_cluster, and the like.

## 5. Using from a WorkTree

When commands run from a linked WorkTree, the default behavior still points at the main
repository:

- serving source, SQLite, Chroma, and manifest use the main repository paths;
- the embedding lock and logs use the main repository or the per-port shared paths;
- queries never generate a second official index in the WorkTree;
- raw corpus not yet merged into the main repository from a WorkTree never appears in official
  query results.

You can query from any WorkTree:

~~~
conda run -n aiops python scripts/query_tidb_unified_knowledge.py \
  --query "placement policy inheritance FOLLOWERS"
~~~

Do not bypass this singleton rule by copying data/knowledge_bases or setting an undeclared
relative directory. Temporary experiments must explicitly use absolute source, persist dir, and
collection paths, and must not be read by default by the official Agent runtime.

## 6. Test and Smoke-test Entry Points

### 6.1 Unified GPU smoke test

For the full serving, embedding, recall, and Agent projection smoke test, use:

~~~
AIOPS_EMBEDDING_MODEL_URL=http://127.0.0.1:8765 \
conda run -n aiops python scripts/smoke_tidb_unified_knowledge.py
~~~

The script:

1. checks the serving source;
2. ensures Qwen/Qwen3-Embedding-4B is ready at the CUDA endpoint;
3. runs one cold query and three rounds of standard queries;
4. records min, p50, p95, max, and mean latency;
5. checks marker recall of the standard queries;
6. checks the Agent projection through TiDBEnv._search_tidb_knowledge();
7. confirms that source/provenance/index fields do not leak;
8. writes results to `logs/tidb_unified_kb_smoke.json` (not committed; subsequent runs overwrite it).

### 6.2 Targeted tests

Knowledge-base behavior regression:

~~~
conda run -n aiops pytest -q \
  tests/tidb/test_tidb_knowledge_base.py \
  tests/knowledge/test_tidb_knowledge_retrieval_quality.py \
  tests/tidb/test_tidb_knowledge_tool.py \
  tests/tidb/test_embedding_model_runtime.py
~~~

Where:

- test_tidb_knowledge_base.py validates configuration, indexing, and query contracts;
- tests/knowledge/test_tidb_knowledge_retrieval_quality.py validates recall of the standard
  queries;
- test_tidb_knowledge_tool.py validates Agent tool parameters and the source-neutral projection;
- test_embedding_model_runtime.py validates health, locks, auto-start, and error boundaries.

## 7. Error Boundaries When in Use

| Situation | Behavior the caller should see |
|---|---|
| serving source missing | error immediately; complete the build first |
| manifest missing | error immediately; build the corresponding backend first |
| source hash changed | report stale index and rebuild |
| Chroma collection missing | error immediately; do not switch to SQLite |
| local embedding endpoint missing | auto-start and wait for ready |
| remote embedding endpoint missing | fail immediately |
| endpoint model mismatch | fail immediately; do not overwrite the running process |
| GPU unavailable | fail immediately; do not switch to CPU |
| query has no results | return the real empty result; do not fabricate answers |
| Agent tool query error | return an error with context |

For the detailed reasons behind index building, the three corpus layers, and stale indexes, see
the [TiDB Knowledge Base Construction Principles and Implementation Standard](./tidb-knowledge-construction.standard.md).
