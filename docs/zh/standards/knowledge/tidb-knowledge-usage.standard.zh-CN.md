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
language: zh-CN
---

# TiDB 统一知识库使用规范

本文只定义当前 TiDB 统一知识库的使用方法。目标读者是需要查询知识库的 Agent
runtime、运行烟测的维护者，以及在知识驱动场景中接入统一检索接口的开发者。

本文不描述 raw corpus 如何合并、三层语料如何物化或索引如何生成；这些内容由
[TiDB 知识库构建原理与实现规范](../../../standards/knowledge/tidb-knowledge-construction.standard.md)定义。
本文也不定义知识驱动场景的设计哲学、具体故障机制或 DP/OP/SP 合同。

## 1. 先区分两个“启动”

当前系统中“启动知识库”不是启动一个独立的数据库服务。正式知识库由两部分组成：

| 部分 | 实际形态 | 是否由查询自动创建 |
|---|---|---:|
| 知识索引 | 主仓库中的 SQLite 文件或 Chroma 持久化 collection | 否 |
| Embedding service | 本机 HTTP 服务，默认 127.0.0.1:8765 | Chroma 查询时可以自动拉起 |

因此：

- 第一次使用前，索引必须已经构建，并且对应目录中有 manifest.json；
- Chroma 查询需要 embedding service。请求经过统一 runtime 检查服务，服务不存在时，
  本机 endpoint 会在锁保护下以脱离当前命令的后台进程启动；
- SQLite 查询不需要 embedding service；
- 查询不会自动构建索引，不会从旧索引、SQLite、网络文档或硬编码摘要中回退；
- TiDBKnowledgeBase 是索引和查询对象，不是一个需要单独保持前台运行的 daemon。

这个边界很重要：如果索引缺失，必须先按
[构建规范](../../../standards/knowledge/tidb-knowledge-construction.standard.md)完成构建；如果 Chroma 的
embedding service 缺失，查询可以按下文的规则自动拉起它。

## 2. 默认运行配置

所有默认路径通过 src/project_paths.py 的 REPOSITORY_ROOT 解析。linked WorkTree
和主 WorkTree 共享主仓库中的语料、索引、日志和 runtime 文件。

当前 hierarchical TiDB 知识库的默认配置如下：

| 配置项 | 默认值 |
|---|---|
| 知识模式 | hierarchical |
| serving source | knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl |
| collection | tidb81_unified_docs |
| Chroma persist dir | data/knowledge_bases/tidb81_unified_chroma |
| SQLite persist dir | data/knowledge_bases/tidb81_unified_docs |
| embedding model | Qwen/Qwen3-Embedding-4B |
| embedding device | cuda |
| embedding endpoint | http://127.0.0.1:8765 |

上表中的相对路径均相对于主仓库根目录（`<repo-root>`，即本仓库的 checkout 根）。

当前正式 TiDB Agent 入口固定使用 hierarchical。general 是通用目录源的历史配置，
不应作为新的知识驱动场景入口。

## 3. 自动启动与显式启动

### 3.1 正常查询时的自动行为

调用链是：

~~~
TiDBKnowledgeBase.query()
  -> Chroma query
  -> request_embeddings()
  -> ensure_embedding_model()
  -> GET /health
  -> 复用 ready service
     或锁保护下启动本机 detached service
~~~

ensure_embedding_model() 位于 src/knowledge/embedding_model_runtime.py，是唯一的自动启动
入口。

自动行为有以下严格边界：

- /health 返回 status=ready 且模型名匹配：直接复用，不重复加载模型；
- 本机 endpoint 不可达：取得按端口区分的锁后启动
  scripts/start_embedding_model.py --serve，等待 ready；
- endpoint 返回模型不匹配：直接失败，不覆盖正在运行的服务；
- endpoint 被其他服务占用或返回非法健康响应：直接失败，不替换；
- endpoint 是远端且不可达：直接失败，不尝试登录或远程启动；
- 启动进程退出、超过等待时间或 GPU 不可用：直接失败；
- 不自动切换到 CPU、不自动切换旧模型、不自动切换 SQLite。

查询脚本不会吞掉这些错误。Agent 工具会把带有 mode、query、过滤器和参数的错误返回给
调用方，Scenario evaluator 不得把工具错误伪装成普通诊断结果。

### 3.2 需要提前预热时的显式启动

如果要在批量实验、建库或人工查询前明确确保服务 ready，执行：

~~~
conda run -n aiops python scripts/start_embedding_model.py \
  --model Qwen/Qwen3-Embedding-4B \
  --device cuda \
  --host 127.0.0.1 \
  --port 8765
~~~

该命令默认也是“检查并确保”的入口：

- 服务已经 ready 时快速返回；
- 服务不存在时在后台启动并等待 ready；
- 命令返回后，embedding service 继续脱离当前终端运行；
- 日志写入主仓库的 logs/embedding_model.log。

只做只读检查时使用：

~~~
conda run -n aiops python scripts/start_embedding_model.py \
  --status \
  --model Qwen/Qwen3-Embedding-4B \
  --host 127.0.0.1 \
  --port 8765
~~~

--status 不会启动服务；ready 时退出码为 0，其他状态退出码为 1。

### 3.3 额外端口或额外 endpoint

需要另一台本机服务或另一端口时，必须明确给出端口、模型和 device。例如：

~~~
conda run -n aiops python scripts/start_embedding_model.py \
  --model Qwen/Qwen3-Embedding-4B \
  --device cuda \
  --host 127.0.0.1 \
  --port 8766
~~~

然后让显式查询指向该 endpoint：

~~~
conda run -n aiops python scripts/query_tidb_unified_knowledge.py \
  --embedding-url http://127.0.0.1:8766 \
  --embedding-model Qwen/Qwen3-Embedding-4B \
  --query "Online Unsafe Recovery failed stores Finished"
~~~

也可以在 Python 进程启动前设置：

~~~
export AIOPS_EMBEDDING_MODEL_URL=http://127.0.0.1:8766
~~~

每个端口使用独立的 lock 文件 /tmp/aiopsbench-embedding-model-<port>.lock。额外 endpoint
不会改变 Agent 默认入口；查询 CLI 会清除 AIOPS_EMBEDDING_MODEL_URLS，确保一次查询只使用
一个明确的 endpoint。AIOPS_EMBEDDING_MODEL_URLS 只用于受控的批量 Chroma 建库并行请求，
详见构建规范。

--serve 是 runtime 内部拉起 detached service 的实现入口，不应作为调用方的第二套启动
逻辑。需要显式启动时使用上面的默认命令，让检查、锁、等待和错误处理仍由同一个 runtime
实现完成。

### 3.4 机器重启后的行为

当前后台进程是脱离当前命令的持久化进程，不是 systemd 或开机服务。机器重启后：

- 索引文件仍在主仓库，除非被主动删除；
- embedding service 不会自动由操作系统拉起；
- 第一次 Chroma 查询或显式运行 start_embedding_model.py 会再次按上述规则启动；
- 若要求机器开机即 ready，应由外部进程管理器托管，但不要在知识库代码里再实现第二套启动器。

## 4. 访问接口

### 4.1 命令行查询脚本

人工查询、召回验证和延迟测量使用：

~~~
conda run -n aiops python scripts/query_tidb_unified_knowledge.py \
  --query "alloc-id recovery high-water"
~~~

脚本默认使用 Chroma hierarchical index。常用参数如下：

| 参数 | 作用 |
|---|---|
| --query | 必填，自然语言问题、配置名、SQL 标识符或组件概念 |
| --backend chroma\|sqlite | 显式选择索引后端，默认 chroma |
| --top-k 1..20 | 返回片段数量，默认 5 |
| --source-scope | self_managed、cloud、kubernetes、developer、shared 或 all |
| --kb-type | architecture、configuration、observability、diagnosis、operation、performance、recovery、data_pipeline、reference、release |
| --component | TiDB、TiKV、PD、TiFlash、TiCDC、BR、Lightning 等组件 |
| --max-chars-per-result | 每条正文长度，范围 200..8000 |
| --embedding-url | Chroma 使用的 endpoint |
| --embedding-model | 期望的模型名 |
| --json | 只输出来源中立 JSON |

例如：

~~~
conda run -n aiops python scripts/query_tidb_unified_knowledge.py \
  --query "Online Unsafe Recovery failed stores Finished" \
  --top-k 5 \
  --kb-type recovery \
  --component pd \
  --json
~~~

--backend sqlite 只在明确需要 FTS5 查询或检查索引合同的时候使用：

~~~
conda run -n aiops python scripts/query_tidb_unified_knowledge.py \
  --backend sqlite \
  --query "tidb_server_memory_limit tidb_mem_oom_action" \
  --json
~~~

脚本输出的 Agent-facing 结果字段固定为：

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

CLI 脚本本身可以保留延迟信息供人工观察，但 Scenario runtime 不应通过 subprocess 调用
它来查询知识库。

### 4.2 Python API

维护脚本、测试和 runtime 内部直接使用 TiDBKnowledgeBase：

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

构造函数会从 src/project_paths.py 取得主仓库路径，并使用 hierarchical 默认 source、
collection 和 persist dir。调用方不得自行：

- 拼接 knowledge/tidb_unified 路径；
- 初始化 SentenceTransformer；
- 探测或启动 embedding endpoint；
- 读取 SQLite/Chroma 内部文件；
- 在 Chroma 出错后切换 SQLite。

kb.query() 返回的内部结果包含 index、persist_dir、source commit 和 materialized
corpus hash 等维护字段。它们可以用于维护和审计，但不能直接暴露给 Agent。

### 4.3 TiDB Agent 工具

TiDB Agent 使用统一工具：

~~~
search_knowledge(
  query,
  source_scope="all",
  top_k=5,
  kb_type=null,
  component=null,
)
~~~

工具固定调用 knowledge_base_mode="hierarchical"，每次将 max_chars_per_result 固定为
1600。工具返回的顶层字段和 result 字段只有：

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

运行时实现位置是 src/execution/environment.py 的 _search_tidb_knowledge() 和
search_knowledge()；工具 schema 位于 src/execution/tidb_tool_definitions.py。

知识结果只提供一般 TiDB 产品知识，不提供当前 run 的 Store、Region、表、checkpoint、
TSO、动态对象、修复结果或 evaluator 结论。Agent 必须把知识结果与 execute_sql、
query_metrics、read_log、manage_cluster 等现场证据重新绑定。

## 5. WorkTree 下使用

从 linked WorkTree 执行命令时，默认行为仍指向主仓库：

- serving source、SQLite、Chroma 和 manifest 使用主仓库路径；
- embedding lock 和日志使用主仓库或按端口约定的共享路径；
- 查询不会在 WorkTree 生成第二份正式 index；
- WorkTree 尚未合入主仓库的 raw corpus 不会出现在正式查询结果中。

可以在任意 WorkTree 查询：

~~~
conda run -n aiops python scripts/query_tidb_unified_knowledge.py \
  --query "placement policy inheritance FOLLOWERS"
~~~

不要通过复制 data/knowledge_bases 或设置一个未声明的相对目录来绕开这个单例规则。
临时实验必须显式使用绝对 source、persist dir 和 collection，并且不能被正式 Agent runtime
默认读取。

## 6. 测试与烟测入口

### 6.1 统一 GPU smoke

完整的 serving、embedding、召回和 Agent projection 烟测使用：

~~~
AIOPS_EMBEDDING_MODEL_URL=http://127.0.0.1:8765 \
conda run -n aiops python scripts/smoke_tidb_unified_knowledge.py
~~~

脚本会：

1. 检查 serving source；
2. 确保 Qwen/Qwen3-Embedding-4B 在 CUDA endpoint ready；
3. 运行一条 cold query 和三轮标准 query；
4. 记录 min、p50、p95、max、mean 延迟；
5. 检查标准 query 的 marker recall；
6. 通过 TiDBEnv._search_tidb_knowledge() 检查 Agent projection；
7. 确认 source/provenance/index 字段没有泄漏；
8. 将结果写入 logs/ 下带时间戳的 JSON 文件（该目录不入库）。

### 6.2 定向测试

知识库行为回归：

~~~
conda run -n aiops pytest -q \
  tests/tidb/test_tidb_knowledge_base.py \
  tests/knowledge/test_tidb_knowledge_retrieval_quality.py \
  tests/tidb/test_tidb_knowledge_tool.py \
  tests/tidb/test_embedding_model_runtime.py
~~~

其中：

- test_tidb_knowledge_base.py 验证配置、索引和查询合同；
- tests/knowledge/test_tidb_knowledge_retrieval_quality.py 验证标准 query 的召回；
- test_tidb_knowledge_tool.py 验证 Agent 工具参数和来源中立投影；
- test_embedding_model_runtime.py 验证 health、锁、自动启动和错误边界。

## 7. 使用时的错误边界

| 情况 | 使用方应看到的行为 |
|---|---|
| serving source 不存在 | 直接报错，先完成构建 |
| manifest 不存在 | 直接报错，先构建对应 backend |
| source hash 变化 | 报 stale index，重新构建 |
| Chroma collection 不存在 | 直接报错，不切换 SQLite |
| 本机 embedding endpoint 不存在 | 自动启动并等待 ready |
| 远程 embedding endpoint 不存在 | 直接失败 |
| endpoint 模型不匹配 | 直接失败，不覆盖现有进程 |
| GPU 不可用 | 直接失败，不切换 CPU |
| query 没有结果 | 返回真实空结果，不伪造答案 |
| Agent 工具查询异常 | 返回带上下文的 error |

索引构建、三层语料和 stale index 的详细原因见
[TiDB 知识库构建原理与实现规范](../../../standards/knowledge/tidb-knowledge-construction.standard.md)。
