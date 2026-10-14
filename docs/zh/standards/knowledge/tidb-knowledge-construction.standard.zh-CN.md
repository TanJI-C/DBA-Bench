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
language: zh-CN
---

# TiDB 统一知识库构建原理与实现规范

本文是当前 TiDB 8.1 统一知识库的构建规范，面向语料维护者、知识库实现者和需要开发
知识驱动场景的工程师。重点不是某次构建的结果，而是构建链路为什么分层、每一层保存什么、
代码如何把层间数据转换，以及 SQLite、Chroma 和 Agent projection 如何共享同一份 serving
corpus。

知识库的实际查询方法、embedding service 的显式启动命令、CLI/Python/Agent 接口和烟测入口
见 [TiDB 统一知识库使用规范](../../../standards/knowledge/tidb-knowledge-usage.standard.md)。本文不定义场景合同和评估合同。

## 1. 构建目标与不变量

统一知识库要同时满足三个要求：

1. 维护侧能知道每个 chunk 的真实来源，能够审计、更新和重建；
2. 官方语料与 curated 语料进入同一套检索空间，不让 Agent 因物理路径看到来源差异；
3. serving 和索引只接收经过校验、哈希可追踪、来源中立的内容。

因此，来源身份不能简单地全部删除，也不能直接暴露给 Agent。当前实现把它分成：

~~~
原始层（身份清楚）
  knowledge/tidb
  knowledge/tidb/curated
          |
          | merge_tidb_curated_knowledge.py
          v
processed 层（统一 chunk + provenance）
  knowledge/tidb_unified/mappings/tidb81_chunks.jsonl
  knowledge/tidb_unified/provenance/tidb81_provenance.jsonl
  knowledge/tidb_unified/manifests/tidb81_unified_manifest.json
          |
          | serving projection
          v
serving 层（来源中立）
  knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl
          |
          +--> SQLite FTS5
          |      data/knowledge_bases/tidb81_unified_docs
          |
          +--> Chroma vector index
                 data/knowledge_bases/tidb81_unified_chroma
~~~

三层不是三份可任选的知识库，而是一条单向生成链：

| 层 | 生成方式 | 主要读者 | 是否可作为 Agent 默认输入 | 是否保留物理来源 |
|---|---|---|---:|---:|
| 原始层 | 官方处理产物和审核后的 curated source | 语料作者、评审者 | 否 | 是 |
| processed 层 | merge 脚本合并并补充 provenance | 构建器、审计工具 | 否 | 是 |
| serving 层 | 从 processed 投影并清洗 | 索引构建器、runtime | 是，通过索引 | 否 |

正式索引只能从 serving 层构建。不能直接把 raw source、provenance 或某个场景目录建成
正式 Agent index。

## 2. 原始层：两类内容先分开

### 2.1 官方语料

当前官方 TiDB 处理语料的 chunk 输入是：

~~~
knowledge/tidb/mappings/tidb81_chunks.jsonl
~~~

这份文件已经是官方文档处理后的结构化 chunk，不是 Agent runtime 直接读取的最终 serving
projection。每条记录包含标题、分类、组件、部署范围、版本、检索字段、正文和内容 hash，
并且保留官方 source id、source file、source URL 等维护信息。

### 2.2 curated 语料

审核后的扩展内容位于：

~~~
knowledge/tidb/curated/
~~~

当前 merge 实现读取：

~~~
knowledge/tidb/curated/*/*chunks.jsonl
knowledge/tidb/curated/tidb_system_failure_gc_mvcc_recovery/*.md
knowledge/tidb/curated/tidb_system_failure_pending_offline/*.md
~~~

JSONL source 必须满足统一 required fields；Markdown source 由
scripts/merge_tidb_curated_knowledge.py 中的 markdown_record() 映射到统一结构。
Markdown 的文件名映射决定 title、kb_type、component 和 topic tags，正文本身仍需经过
清洗和 hash。

curated 原始内容应描述可复用的 TiDB 8.1 机制、状态语义、操作前置、危险边界和验收不变量。
它不能依赖某次 run 的动态 Store、Region、表、TSO、secret、fixture 常量或 evaluator 结论。
场景的动态事实必须由 Agent 通过现场工具取得，不能在 source 中预先写成答案。

## 3. processed 层：merge 的代码路径

构建入口是：

~~~bash
conda run -n aiops python scripts/merge_tidb_curated_knowledge.py
~~~

脚本默认：

~~~
official input:
  knowledge/tidb/mappings/tidb81_chunks.jsonl

output root:
  knowledge/tidb_unified
~~~

核心实现位于 scripts/merge_tidb_curated_knowledge.py，转换过程如下。

### 3.1 读取与校验官方记录

official_records() 逐行读取官方 JSONL：

- 检查 required fields 是否齐全；
- 拒绝空行和非法 JSON；
- 重新计算 content 的 SHA-256；
- content_sha256 不匹配时直接抛错；
- 记录 source class 为 official；
- 把原始 source_id、source_file、source_url 和 pinned URL 写入 provenance sidecar。

官方记录的 chunk_id 保持不变，便于追踪同一个官方 chunk 在 processed 和 serving 层的
对应关系。

### 3.2 读取与规范化 curated 记录

load_existing_records() 读取现有 curated JSONL，load_markdown_records() 读取受支持的
Markdown 目录。每一条扩展记录都带有原始位置的 path 和 line metadata，供 provenance 使用。

对于 curated 内容，脚本会：

1. 用 title、原始 source id 和清洗后的 content 计算稳定 digest；
2. 生成统一的 tidb81 chunk id 和 source id；
3. 强制 version 为 8.1；
4. 保留 kb_type、component、related_components、source_scope、topic_tags、
   use_when、retrieval_keywords 和 follow_up；
5. 标记 source_kind 为 curated；
6. 把原始 source path、source id 和 URL 写入 provenance，而不是写进 serving 正文。

如果新 chunk 与已有 chunk_id 冲突，脚本直接失败。这里不做覆盖式兼容，也不静默选取其中
一条记录。

### 3.3 生成 processed JSONL 和 provenance

processed 输出：

~~~
knowledge/tidb_unified/mappings/tidb81_chunks.jsonl
knowledge/tidb_unified/provenance/tidb81_provenance.jsonl
~~~

processed chunk 仍然拥有完整的维护字段，并额外包含：

~~~
source_kind
source_origin_id
source_origin_path
source_origin_url
source_origin_pinned_url
~~~

provenance 一条一条地记录：

~~~
chunk_id
source_kind
source_origin_id
source_origin_path
source_origin_url
~~~

这使得官方语料和 curated 语料已经在第二层混合，但它们的身份仍然可审计。processed 层
不直接交给 Agent。

## 4. serving 层：来源中立投影

### 4.1 字段投影

serving 输出是：

~~~
knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl
~~~

脚本只从 unified record 中取统一 required fields，然后执行以下投影：

- source_id 置为空；
- source_file 置为空；
- source_url 置为空；
- pinned_source_url 置为空；
- title、heading path、use_when、retrieval_keywords、follow_up 和 content 清洗；
- 重新计算 content_sha256；
- 检查清洗后的全部语义字段是否仍包含禁止 token。

serving 仍保留影响检索和使用判断的语义字段：

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

source identity 与 semantic metadata 必须区分：version、component 和 source_scope 会改变
知识适用范围，不能为了隐藏来源而删除；source_file、source_url 和 source class 只是维护
身份，不能进入 Agent-facing 内容。

### 4.2 泄漏检查

scripts/merge_tidb_curated_knowledge.py 的 FORBIDDEN_SERVING_TOKENS 会拒绝常见的
benchmark、场景编号、source class、物理路径和 provenance 标识。清洗会去除 Markdown URL、
HTTP URL 和 file URL，并把已知内部 case token 改写成一般语义。

这不是把答案改写成另一种答案的机制。清洗的目标是移除来源和 benchmark 身份；如果正文仍
依赖本题动态对象、固定答案或 evaluator 条件，应当直接修改 raw source，而不是继续扩展
sanitize_serving_text() 的替换表。

### 4.3 manifest

merge 会生成：

~~~
knowledge/tidb_unified/manifests/tidb81_unified_manifest.json
~~~

manifest 至少记录：

- schema_version、corpus_id、target_version；
- processed 和 serving 的相对路径、记录数和 SHA-256；
- provenance 的 SHA-256；
- official 和 curated 的数量；
- 官方输入文件及其 SHA-256；
- Agent projection 允许的字段集合。

serving hash、processed hash 和 provenance hash 是构建证据，不是 Agent 知识答案。

## 5. TiDBKnowledgeBase 的配置和路径解析

### 5.1 主仓库路径

src/project_paths.py 在模块加载时运行：

~~~bash
git rev-parse --git-common-dir
~~~

再由 Git common directory 得到主仓库根目录。resolve_project_path() 将所有相对 source、
persist dir 和脚本路径解析到这个根目录。因此 linked WorkTree 不会生成第二份正式语料或
索引。

### 5.2 TiDB 默认配置

src/knowledge/tidb_knowledge_base.py 定义：

| 常量或配置 | 默认值 |
|---|---|
| DEFAULT_COLLECTION_NAME | tidb81_unified_docs |
| hierarchical source | knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl |
| hierarchical SQLite | data/knowledge_bases/tidb81_unified_docs |
| hierarchical Chroma | data/knowledge_bases/tidb81_unified_chroma |
| embedding model | Qwen/Qwen3-Embedding-4B |
| embedding device | cuda |
| knowledge mode | hierarchical |

运行时可以通过明确的环境变量覆盖：

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

正式 TiDB Agent 不通过环境变量切换到 general mode，也不创建场景私有 collection。

### 5.3 source mode 的边界

TiDBKnowledgeBase 的 hierarchical mode 读取 serving JSONL，general mode 才会读取
`knowledge/tidb_src` 目录（上游 PingCAP docs 固定 commit 的本地镜像，不随仓库分发，见 `knowledge/tidb/ATTRIBUTION.md`）并结合官方 inventory、source lock 和 Markdown parser 生成 section
records。两种 mode 的 source schema 和用途不同。

知识驱动场景使用 hierarchical mode，因为 curated 内容已经由 merge 脚本进入统一 serving
corpus。不要把 curated Markdown 直接放进 general 目录，绕过三层合并和 serving 清洗。

## 6. 索引构建的代码实现

统一 CLI 是：

~~~
scripts/build_tidb_knowledge_base.py
~~~

它解析 backend、knowledge mode、source file、persist dir、collection、embedding model、
device、batch size 和 workers，然后实例化 TiDBKnowledgeBase 并调用 build()。build() 的
共同前置步骤是：

1. resolve source path；
2. _load_records() 逐行校验字段、分类、组件、范围、正文 hash 和 chunk id 唯一性；
3. 按 backend 调用 SQLite 或 Chroma builder；
4. 写入索引目录下的 manifest.json；
5. 按 verify-query 运行一次查询验证。

### 6.1 SQLite FTS5

SQLite builder 在 src/knowledge/markdown_knowledge_base.py 的 _build_sqlite()：

- 创建 chunks 表保存完整 serving record；
- 创建 chunks_fts FTS5 虚拟表，索引 title、use_when、retrieval_keywords 和 content；
- 默认 reset 时删除旧数据库并重建；
- 每条 chunk 以 chunk_id 作为主键；
- 在 FTS 表中使用同一个 chunk_id 与正文建立关联。

查询由 _query_sqlite() 执行：

- 将 query 拆成可索引 token；
- 以 OR 组合 FTS5 MATCH；
- 按 source_scope、kb_type 和 component 添加过滤；
- 用 bm25 distance 排序；
- 将 distance 转成统一 score；
- 返回截断后的 content。

SQLite 不需要 embedding service。它是明确选择的全文检索后端，不是 Chroma 失败时的 fallback。

### 6.2 Chroma 向量索引

Chroma builder 在 _build_chroma()：

1. 创建 PersistentClient，路径是 hierarchical Chroma persist dir；
2. reset 时删除同名 collection；
3. 按 embedding_text 长度排序，降低批处理中的长度差异；
4. 按 embed_batch_size 和 embed_workers 组织请求；
5. 通过 request_embeddings() 调用共享 embedding service；
6. 用 chunk_id、embedding、正文 document 和 metadata upsert 到 collection。

KnowledgeRecord.embedding_text 由以下信息组成：

~~~
title
use_when
Keywords: retrieval_keywords
follow_up
content 的前 2048 个字符
~~~

正文完整内容作为 Chroma document 保存，但 embedding 输入只取前 2048 个字符。这个差异是
有意的：标题、适用条件、关键词和后续检查先进入向量，返回结果仍然保留完整正文。

Chroma metadata 包含 chunk_id、source identity 字段、title、分类、组件、范围、版本和
has_component_* 过滤字段。由于正式输入是 serving projection，source_id、source_file、
source_url 和 pinned_source_url 在这里为空；即使内部索引 metadata 存在，Agent projection
也不会把它们返回。

查询由 _query_chroma() 执行：

- 先通过 request_embeddings() 生成 query vector；
- 根据 source_scope、kb_type、component 生成 Chroma where；
- 请求 top_k、metadatas、distances 和 documents；
- 将 distance 转换成统一 score；
- 返回来源中立的结果。

正式 Agent-facing 默认是 Chroma hierarchical index。批量建库可以通过
AIOPS_EMBEDDING_MODEL_URLS 显式提供多个 endpoint，但这只是建库并行配置，不是查询时的
后端 fallback。

## 7. manifest 和 stale index

每个 backend 的 persist dir 都有一个 manifest.json。build() 写入的 manifest 合并了：

- backend、collection、knowledge_base_mode；
- source_file、source corpus hash、document_count、node_count；
- source commit、processing prompt hash（如果 source manifest 提供）；
- Chroma 的 embedding model；
- build timestamp。

查询前 _validated_manifest() 必须通过：

1. manifest 文件存在；
2. manifest backend 和 collection 与当前对象一致；
3. manifest source file 仍存在；
4. source file 当前 SHA-256 与构建时一致；
5. 若 manifest 声明 source_commit 且 source lock 存在，commit 仍一致。

任一步骤失败都直接抛出带路径、backend、collection 和 hash 的错误。实现不允许：

- 继续使用旧索引；
- 自动切换另一 backend；
- 自动读取 raw corpus 或网络文档；
- 用硬编码摘要代替空结果；
- 由 Scenario 代码自行修补 manifest。

内容、元数据、serving 清洗规则、embedding model、collection 或 source commit 发生变化时，
应重新 merge（如果是语料或投影变化）并重新构建受影响 backend。

## 8. 标准构建流程

在主仓库或任意 linked WorkTree 执行都可以，但产物最终写入主仓库。

### 8.1 重新物化三层语料

~~~bash
conda run -n aiops python scripts/merge_tidb_curated_knowledge.py
~~~

### 8.2 构建 SQLite

~~~bash
conda run -n aiops python scripts/build_tidb_knowledge_base.py \
  --backend sqlite \
  --knowledge-mode hierarchical \
  --source-file knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl \
  --persist-dir data/knowledge_bases/tidb81_unified_docs \
  --collection tidb81_unified_docs \
  --no-progress
~~~

### 8.3 确保 embedding service 并构建 Chroma

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

### 8.4 验证

~~~bash
AIOPS_EMBEDDING_MODEL_URL=http://127.0.0.1:8765 \
conda run -n aiops python scripts/smoke_tidb_unified_knowledge.py
~~~

验证重点是：

- processed 和 serving 记录数、hash、provenance 数量一致；
- serving 不含 source/provenance/benchmark 泄漏；
- 两个 index 的 manifest 与 serving hash 一致；
- 标准 query 能召回目标语义；
- Agent projection 没有 source_id、source_file、source_url、persist_dir 或 commit；
- embedding health 的 model、device 和 dimension 正确。

## 9. runtime projection 的两道边界

统一知识库有两道来源隔离：

1. serving projection 在物理数据层将 source identity 置空并检查泄漏；
2. src/execution/environments/tidb.py 的 _search_tidb_knowledge() 只允许返回：

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

内部 TiDBKnowledgeBase.query() 仍可返回 index metadata，供维护者检查 manifest 和延迟；
Agent 工具在返回 JSON 前会移除这些字段。Scenario/ScenarioCase 不得绕过这两道边界直接读取
JSONL、SQLite 表、Chroma metadata 或 provenance sidecar。

## 10. 变更边界和代码归属

| 责任 | 当前实现 |
|---|---|
| 主仓库根目录和 WorkTree 解析 | src/project_paths.py |
| TiDB mode、source、collection、persist dir | src/knowledge/tidb_knowledge_base.py |
| record schema、SQLite、Chroma、manifest、query | src/knowledge/markdown_knowledge_base.py |
| embedding health、锁、自动拉起、HTTP client | src/knowledge/embedding_model_runtime.py |
| embedding HTTP server | scripts/start_embedding_model.py |
| raw -> processed -> serving | scripts/merge_tidb_curated_knowledge.py |
| SQLite/Chroma build CLI | scripts/build_tidb_knowledge_base.py |
| 人工查询 CLI | scripts/query_tidb_unified_knowledge.py |
| Agent-facing projection | src/execution/environments/tidb.py |
| 工具 schema | src/execution/tidb_tool_definitions.py |
| 统一 smoke | scripts/smoke_tidb_unified_knowledge.py |

后续开发应遵循以下边界：

- 新增语料修改 raw source 或 merge 规则，不直接编辑 SQLite、Chroma 或 serving 产物；
- 新增字段先修改统一 record schema、merge projection 和 builder，再修改调用方；
- 新的过滤条件必须同时有 serving 字段、SQLite 条件、Chroma metadata 和 Agent 参数合同；
- 新的 embedding 生命周期行为只能进入 embedding_model_runtime.py；
- Scenario 只调用 search_knowledge，不复制构建和查询逻辑；
- 任何 index 产物都只在主仓库保留一份正式副本。

本规范描述的是构建和物理边界，不包含知识驱动场景交付 checklist。场景开发时仍应另行
依据场景合同、知识驱动设计哲学和项目的 Scenario 实现规范完成场景级审查。
