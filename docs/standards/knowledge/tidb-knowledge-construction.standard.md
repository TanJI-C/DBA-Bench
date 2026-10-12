---
doc_id: standard.knowledge.tidb-knowledge-construction
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: public
scope: [tidb, knowledge]
summary: Defines the TiDB unified knowledge-base construction model, three corpus layers, provenance projection, index builders, manifest validation, and code-level ownership boundaries.
source_of_truth: code
related: [standard.knowledge.tidb-knowledge-usage]
language: en
---

# TiDB Unified Knowledge Base Construction Principles and Implementation Standard

This document is the construction standard for the current TiDB 8.1 unified knowledge base,
aimed at corpus maintainers, knowledge-base implementers, and engineers who need to develop
knowledge-driven scenarios. The focus is not the result of any particular build, but why the
construction pipeline is layered, what each layer stores, how the code transforms data between
layers, and how SQLite, Chroma, and the Agent projection share the same serving corpus.

For the actual query methods of the knowledge base, the explicit embedding service startup
command, the CLI/Python/Agent interfaces, and the smoke-test entry point, see the
[TiDB Unified Knowledge Base Usage Standard](./tidb-knowledge-usage.standard.md). This document
does not define scenario contracts or evaluation contracts.

## 1. Construction Goals and Invariants

The unified knowledge base must satisfy three requirements at once:

1. The maintenance side can know the true provenance of every chunk and can audit, update, and
   rebuild;
2. Official and curated corpora enter the same retrieval space, so the Agent never sees provenance
   differences through physical paths;
3. Serving and indexes only receive validated, hash-traceable, source-neutral content.

Therefore, source identity can neither be simply deleted outright nor exposed directly to the
Agent. The current implementation splits it into:

~~~
Raw layer (identity clear)
  knowledge/tidb
  knowledge/tidb/curated
          |
          | merge_tidb_curated_knowledge.py
          v
processed layer (unified chunks + provenance)
  knowledge/tidb_unified/mappings/tidb81_chunks.jsonl
  knowledge/tidb_unified/provenance/tidb81_provenance.jsonl
  knowledge/tidb_unified/manifests/tidb81_unified_manifest.json
          |
          | serving projection
          v
serving layer (source neutral)
  knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl
          |
          +--> SQLite FTS5
          |      data/knowledge_bases/tidb81_unified_docs
          |
          +--> Chroma vector index
                 data/knowledge_bases/tidb81_unified_chroma
~~~

The three layers are not three interchangeable knowledge bases; they are a one-way generation
chain:

| Layer | How it is generated | Primary consumers | Usable as Agent default input | Keeps physical provenance |
|---|---|---|---:|---:|
| Raw layer | Official processing artifacts and reviewed curated sources | Corpus authors, reviewers | No | Yes |
| processed layer | Merged by the merge script and enriched with provenance | Builders, audit tooling | No | Yes |
| serving layer | Projected from processed and sanitized | Index builders, runtime | Yes, via the indexes | No |

Official indexes can only be built from the serving layer. Do not build an official Agent index
directly from raw sources, provenance, or a scenario directory.

## 2. Raw Layer: Separate the Two Kinds of Content First

### 2.1 Official corpus

The chunk input of the current official TiDB processed corpus is:

~~~
knowledge/tidb/mappings/tidb81_chunks.jsonl
~~~

This file already contains structured chunks produced by official-document processing; it is not
the final serving projection read directly by the Agent runtime. Each record contains the title,
category, component, deployment scope, version, retrieval fields, body, and content hash, and
keeps maintenance information such as the official source id, source file, and source URL.

### 2.2 Curated corpus

The reviewed extended content lives in:

~~~
knowledge/tidb/curated/
~~~

The current merge implementation reads:

~~~
knowledge/tidb/curated/*/*chunks.jsonl
knowledge/tidb/curated/tidb_system_failure_gc_mvcc_recovery/*.md
knowledge/tidb/curated/tidb_system_failure_pending_offline/*.md
~~~

JSONL sources must satisfy the unified required fields; Markdown sources are mapped to the unified
structure by markdown_record() in scripts/merge_tidb_curated_knowledge.py. The Markdown file-name
mapping determines the title, kb_type, component, and topic tags; the body itself still goes
through sanitization and hashing.

Curated raw content should describe reusable TiDB 8.1 mechanisms, state semantics, operational
prerequisites, danger boundaries, and acceptance invariants. It must not depend on the dynamic
Stores, Regions, tables, TSO, secrets, fixture constants, or evaluator conclusions of a particular
run. A scenario's dynamic facts must be obtained by the Agent through live tools and must not be
pre-written as answers in the source.

## 3. processed Layer: The Merge Code Path

The build entry point is:

~~~bash
conda run -n aiops python scripts/merge_tidb_curated_knowledge.py
~~~

The script defaults:

~~~
official input:
  knowledge/tidb/mappings/tidb81_chunks.jsonl

output root:
  knowledge/tidb_unified
~~~

The core implementation lives in scripts/merge_tidb_curated_knowledge.py; the transformation
proceeds as follows.

### 3.1 Reading and validating official records

official_records() reads the official JSONL line by line:

- checks that required fields are present;
- rejects empty lines and invalid JSON;
- recomputes the SHA-256 of content;
- raises immediately when content_sha256 does not match;
- records the source class as official;
- writes the original source_id, source_file, source_url, and pinned URL into the provenance
  sidecar.

The chunk_id of official records stays unchanged, making it easy to trace the correspondence of
the same official chunk across the processed and serving layers.

### 3.2 Reading and normalizing curated records

load_existing_records() reads the existing curated JSONL, and load_markdown_records() reads the
supported Markdown directories. Every extended record carries path and line metadata of its
original location, for provenance use.

For curated content, the script:

1. computes a stable digest from the title, the original source id, and the sanitized content;
2. generates the unified tidb81 chunk id and source id;
3. forces version to 8.1;
4. keeps kb_type, component, related_components, source_scope, topic_tags, use_when,
   retrieval_keywords, and follow_up;
5. marks source_kind as curated;
6. writes the original source path, source id, and URL into provenance rather than into the
   serving body.

If a new chunk conflicts with an existing chunk_id, the script fails immediately. There is no
overwrite-style compatibility here, and no record is silently picked over another.

### 3.3 Generating the processed JSONL and provenance

The processed outputs:

~~~
knowledge/tidb_unified/mappings/tidb81_chunks.jsonl
knowledge/tidb_unified/provenance/tidb81_provenance.jsonl
~~~

A processed chunk still carries the complete maintenance fields, plus:

~~~
source_class
source_origin_id
source_origin_path
source_origin_url
source_origin_pinned_url
~~~

provenance records, one entry per chunk:

~~~
chunk_id
source_class
source_origin_id
source_origin_path
source_origin_url
~~~

This means the official and curated corpora are already mixed at the second layer, but their
identities remain auditable. The processed layer is never handed to the Agent directly.

## 4. serving Layer: Source-neutral Projection

### 4.1 Field projection

The serving output is:

~~~
knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl
~~~

The script takes only the unified required fields from the unified record and then applies this
projection:

- source_id is set to empty;
- source_file is set to empty;
- source_url is set to empty;
- pinned_source_url is set to empty;
- title, heading path, use_when, retrieval_keywords, follow_up, and content are sanitized;
- content_sha256 is recomputed;
- all sanitized semantic fields are checked for remaining forbidden tokens.

serving still keeps the semantic fields that affect retrieval and usage decisions:

~~~
chunk_id
title
kb_type
component
related_components
source_scope
topic_tags
version
source_heading_path
use_when
retrieval_keywords
follow_up
content
content_sha256
~~~

Source identity and semantic metadata must be distinguished: version, component, and source_scope
change the applicability of the knowledge and must not be deleted to hide provenance; source_file,
source_url, and source class are only maintenance identity and must not enter Agent-facing
content.

### 4.2 Leakage checks

FORBIDDEN_SERVING_TOKENS in scripts/merge_tidb_curated_knowledge.py rejects common benchmark
names, scenario numbers, source classes, physical paths, and provenance identifiers. Sanitization
removes Markdown URLs, HTTP URLs, and file URLs, and rewrites known internal case tokens into
generic semantics.

This is not a mechanism for rewriting one answer into another. The goal of sanitization is to
remove provenance and benchmark identity; if a body still depends on this problem's dynamic
objects, fixed answers, or evaluator conditions, fix the raw source directly instead of extending
the replacement table of sanitize_serving_text().

### 4.3 manifest

The merge generates:

~~~
knowledge/tidb_unified/manifests/tidb81_unified_manifest.json
~~~

The manifest records at least:

- schema_version, corpus_id, target_version;
- the relative paths, record counts, and SHA-256 of processed and serving;
- the SHA-256 of provenance;
- the counts of official and curated records;
- the official input files and their SHA-256;
- the field set allowed in the Agent projection.

The serving hash, processed hash, and provenance hash are build evidence, not Agent knowledge
answers.

## 5. TiDBKnowledgeBase Configuration and Path Resolution

### 5.1 Main repository path

src/project_paths.py runs at module load time:

~~~bash
git rev-parse --git-common-dir
~~~

and derives the main repository root from the Git common directory. resolve_project_path()
resolves all relative source, persist dir, and script paths against this root. As a result, a
linked WorkTree never produces a second official corpus or index.

### 5.2 TiDB default configuration

src/knowledge/tidb_knowledge_base.py defines:

| Constant or configuration | Default value |
|---|---|
| DEFAULT_COLLECTION_NAME | tidb81_unified_docs |
| hierarchical source | knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl |
| hierarchical SQLite | data/knowledge_bases/tidb81_unified_docs |
| hierarchical Chroma | data/knowledge_bases/tidb81_unified_chroma |
| embedding model | Qwen/Qwen3-Embedding-4B |
| embedding device | cuda |
| knowledge mode | hierarchical |

At runtime these can be overridden through explicit environment variables:

~~~
AIOPS_TIDB_HIERARCHICAL_KB_SOURCE
AIOPS_TIDB_HIERARCHICAL_KB_SQLITE_DIR
AIOPS_TIDB_HIERARCHICAL_KB_CHROMA_DIR
AIOPS_TIDB_KB_COLLECTION
AIOPS_TIDB_KB_BACKEND
AIOPS_TIDB_KB_EMBED_MODEL
AIOPS_TIDB_KB_EMBED_DEVICE
AIOPS_TIDB_KB_EMBED_BATCH_SIZE
AIOPS_TIDB_KB_EMBED_WORKERS
~~~

The official TiDB Agent does not switch to general mode through environment variables, nor does it
create scenario-private collections.

### 5.3 Source mode boundaries

The hierarchical mode of TiDBKnowledgeBase reads the serving JSONL; only general mode reads the
`knowledge/tidb_src` directory (a local mirror of the upstream PingCAP docs at a pinned commit,
not distributed with the repository, see `knowledge/tidb/ATTRIBUTION.md`) and combines the
official inventory, source lock, and Markdown parser to produce section records. The two modes
have different source schemas and purposes.

Knowledge-driven scenarios use hierarchical mode, because curated content has already entered the
unified serving corpus through the merge script. Do not put curated Markdown directly into the
general directory to bypass the three-layer merge and serving sanitization.

## 6. Index Building Code

The unified CLI is:

~~~
scripts/build_tidb_knowledge_base.py
~~~

It parses the backend, knowledge mode, source file, persist dir, collection, embedding model,
device, batch size, and workers, then instantiates TiDBKnowledgeBase and calls build(). The common
prerequisite steps of build() are:

1. resolve the source path;
2. _load_records() validates line by line the fields, category, component, scope, body hash, and
   chunk id uniqueness;
3. invoke the SQLite or Chroma builder according to the backend;
4. write manifest.json into the index directory;
5. run one query verification with verify-query.

### 6.1 SQLite FTS5

The SQLite builder is _build_sqlite() in src/knowledge/markdown_knowledge_base.py:

- creates a chunks table storing the complete serving record;
- creates the chunks_fts FTS5 virtual table indexing title, use_when, retrieval_keywords, and
  content;
- on reset (the default), deletes the old database and rebuilds;
- uses chunk_id as the primary key of every chunk;
- associates with the body through the same chunk_id in the FTS table.

Queries are executed by _query_sqlite():

- splits the query into indexable tokens;
- combines FTS5 MATCH with OR;
- adds filters by source_scope, kb_type, and component;
- orders by bm25 distance;
- converts distance into the unified score;
- returns truncated content.

SQLite needs no embedding service. It is a deliberately chosen full-text retrieval backend, not a
fallback when Chroma fails.

### 6.2 Chroma vector index

The Chroma builder is _build_chroma():

1. creates a PersistentClient whose path is the hierarchical Chroma persist dir;
2. on reset, deletes the same-named collection;
3. sorts by embedding_text length to reduce length variance within batches;
4. organizes requests by embed_batch_size and embed_workers;
5. calls the shared embedding service through request_embeddings();
6. upserts chunk_id, embedding, body document, and metadata into the collection.

KnowledgeRecord.embedding_text consists of:

~~~
title
use_when
Keywords: retrieval_keywords
follow_up
the first 2048 characters of content
~~~

The complete body is stored as the Chroma document, but the embedding input takes only the first
2048 characters. This difference is intentional: the title, applicability conditions, keywords,
and follow-up checks enter the vector first, while returned results still keep the complete body.

Chroma metadata includes chunk_id, the source identity fields, title, category, component, scope,
version, and the has_component_* filter fields. Because the official input is the serving
projection, source_id, source_file, source_url, and pinned_source_url are empty here; even though
the internal index metadata contains them, the Agent projection never returns them.

Queries are executed by _query_chroma():

- first generates the query vector through request_embeddings();
- builds the Chroma where from source_scope, kb_type, and component;
- requests top_k, metadatas, distances, and documents;
- converts distance into the unified score;
- returns source-neutral results.

The official Agent-facing default is the Chroma hierarchical index. Bulk index builds can
explicitly supply multiple endpoints through AIOPS_EMBEDDING_MODEL_URLS, but that is only
build-time parallelism configuration, not a query-time backend fallback.

## 7. manifest and stale index

Every backend's persist dir has a manifest.json. The manifest written by build() merges:

- backend, collection, knowledge_base_mode;
- source_file, source corpus hash, document_count, node_count;
- source commit and processing prompt hash (if the source manifest provides them);
- the Chroma embedding model;
- the build timestamp.

Before querying, _validated_manifest() must pass:

1. the manifest file exists;
2. the manifest backend and collection match the current object;
3. the manifest source file still exists;
4. the source file's current SHA-256 matches the build-time hash;
5. if the manifest declares a source_commit and the source lock exists, the commit still matches.

Any failed step raises an error immediately, carrying the path, backend, collection, and hash. The
implementation must not:

- keep using the stale index;
- switch to another backend automatically;
- read the raw corpus or web documents automatically;
- substitute hardcoded summaries for empty results;
- let Scenario code patch the manifest itself.

When content, metadata, serving sanitization rules, the embedding model, the collection, or the
source commit changes, re-run the merge (for corpus or projection changes) and rebuild the
affected backends.

## 8. Standard Build Procedure

You may execute from the main repository or any linked WorkTree, but the artifacts end up written
to the main repository.

### 8.1 Re-materialize the three corpus layers

~~~bash
conda run -n aiops python scripts/merge_tidb_curated_knowledge.py
~~~

### 8.2 Build SQLite

~~~bash
conda run -n aiops python scripts/build_tidb_knowledge_base.py \
  --backend sqlite \
  --knowledge-mode hierarchical \
  --source-file knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl \
  --persist-dir data/knowledge_bases/tidb81_unified_docs \
  --collection tidb81_unified_docs \
  --no-progress
~~~

### 8.3 Ensure the embedding service and build Chroma

~~~bash
conda run -n aiops python scripts/start_embedding_model.py \
  --model Qwen/Qwen3-Embedding-4B \
  --device cuda \
  --host 127.0.0.1 \
  --port 8765

conda run -n aiops python scripts/build_tidb_knowledge_base.py \
  --backend chroma \
  --knowledge-mode hierarchical \
  --source-file knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl \
  --persist-dir data/knowledge_bases/tidb81_unified_chroma \
  --collection tidb81_unified_docs \
  --embedding-model Qwen/Qwen3-Embedding-4B \
  --embedding-device cuda \
  --embedding-batch-size 4 \
  --embedding-workers 1 \
  --no-progress
~~~

### 8.4 Verification

~~~bash
AIOPS_EMBEDDING_MODEL_URL=http://127.0.0.1:8765 \
conda run -n aiops python scripts/smoke_tidb_unified_knowledge.py
~~~

The verification focuses on:

- processed and serving record counts, hashes, and the provenance count are consistent;
- serving contains no source/provenance/benchmark leakage;
- both indexes' manifests match the serving hash;
- standard queries recall the target semantics;
- the Agent projection has no source_id, source_file, source_url, persist_dir, or commit;
- the embedding health model, device, and dimension are correct.

## 9. The Two Boundaries of the runtime projection

The unified knowledge base has two provenance isolation boundaries:

1. the serving projection blanks source identity at the physical data layer and checks for
   leakage;
2. _search_tidb_knowledge() in src/execution/environment.py only allows returning:

~~~
rank
score
title
version
kb_type
component
source_scope
content
~~~

The internal TiDBKnowledgeBase.query() may still return index metadata for maintainers to inspect
the manifest and latency; the Agent tool removes those fields before returning JSON.
Scenario/ScenarioCase must not bypass these two boundaries to read the JSONL, SQLite tables,
Chroma metadata, or the provenance sidecar directly.

## 10. Change Boundaries and Code Ownership

| Responsibility | Current implementation |
|---|---|
| Main repository root and WorkTree resolution | src/project_paths.py |
| TiDB mode, source, collection, persist dir | src/knowledge/tidb_knowledge_base.py |
| record schema, SQLite, Chroma, manifest, query | src/knowledge/markdown_knowledge_base.py |
| embedding health, locks, auto-start, HTTP client | src/knowledge/embedding_model_runtime.py |
| embedding HTTP server | scripts/start_embedding_model.py |
| raw -> processed -> serving | scripts/merge_tidb_curated_knowledge.py |
| SQLite/Chroma build CLI | scripts/build_tidb_knowledge_base.py |
| manual query CLI | scripts/query_tidb_unified_knowledge.py |
| Agent-facing projection | src/execution/environment.py |
| tool schema | src/execution/tidb_tool_definitions.py |
| unified smoke test | scripts/smoke_tidb_unified_knowledge.py |

Follow these boundaries going forward:

- New corpus goes through raw source or merge rule changes; do not edit SQLite, Chroma, or serving
  artifacts directly;
- New fields change the unified record schema, merge projection, and builder first, then the
  callers;
- New filter conditions must come with a serving field, a SQLite condition, Chroma metadata, and an
  Agent parameter contract at the same time;
- New embedding lifecycle behavior only goes into embedding_model_runtime.py;
- Scenarios only call search_knowledge and do not copy build or query logic;
- Every index artifact keeps exactly one official copy in the main repository.

This standard describes construction and physical boundaries; it does not include the
knowledge-driven scenario delivery checklist. During scenario development, still perform
scenario-level review separately according to the scenario contract, the knowledge-driven design
philosophy, and the project's Scenario implementation standard.
