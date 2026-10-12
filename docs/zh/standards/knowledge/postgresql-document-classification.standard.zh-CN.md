---
doc_id: standard.knowledge.postgresql-document-classification
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [postgres, knowledge]
summary: 定义 PostgreSQL 分层知识库的章节级分类规则与物化（materialization）边界。
source_of_truth: code
related: []
language: zh-CN
---

# PostgreSQL 分层分类规则

本文档定义对 PostgreSQL 16 官方文档进行分类时使用的章节级规则，分类结果为 `configuration`、`guide`、`solution` 和 `fact`。

## 来源边界

只有本目录可以用作来源：

```text
`knowledge/pg_src/pg16-docs-md` (a local mirror of the upstream PostgreSQL 16 documentation; not distributed with the repo)
```

不要把现有的 `knowledge/pg` 内容当作来源文本复用。

## 分类单元

默认单元是一个 Markdown 章节。当章节包含多种操作角色时可以进一步拆分。只有当整个文件本身已经是一个狭窄的参考条目（例如单条 SQL 命令或客户端工具）时，才能把整个文件作为一个单元。

## 优先级

当一个章节可能同时符合多个类别时，优先选择：

1. `solution`
2. `guide`
3. `configuration`
4. `fact`

这样可以让具体的处置步骤和诊断证据更容易被检索到。

## `configuration`

用于参数与配置语义。

纳入以下内容：

- 参数含义、单位、默认值、允许取值、作用域或重启/重载行为
- `postgresql.conf`、`postgresql.auto.conf`、`pg_hba.conf`
- `SET`、`SHOW`、`RESET`、`ALTER SYSTEM`
- `ALTER DATABASE`、`ALTER ROLE` 或相关的默认值设置行为
- `pg_settings`、`current_setting`、`set_config`
- WAL、规划器、日志、内存、连接、认证、autovacuum、JIT、复制、SSL 以及操作系统资源设置

## `guide`

用于诊断与根因确认。

纳入那些告诉 agent 在症状出现时应当检查什么的内容：

- 锁等待、阻塞者、死锁、长事务
- `pg_locks`、`pg_stat_activity`、等待事件
- 表膨胀、死元组、vacuum/autovacuum 证据
- 慢查询、`EXPLAIN`、规划器统计、索引使用
- 磁盘使用、WAL 增长、检查点压力、临时文件
- 复制延迟/冲突、进度报告、就绪检查

## `solution`

用于根因确认后的处置。

纳入以下内容：

- `VACUUM`、`ANALYZE`、`REINDEX`、`CLUSTER`、`CHECKPOINT`
- `CREATE INDEX`、`CREATE STATISTICS` 以及文档记载的查询诊断后调优动作
- 备份、恢复、PITR、故障切换、升级、校验和、修复与还原流程
- `pg_dump`、`pg_restore`、`pg_basebackup`、`pg_amcheck`、`pg_resetwal`、`vacuumdb`、`reindexdb`、`clusterdb` 及相关工具

## `fact`

用于上述类别未覆盖的基础事实与参考资料：

- 教程
- SQL 语法与对象语义
- 数据类型、函数、操作符
- 目录、视图与 information_schema 字段参考
- 内部实现、存储、WAL 机制、索引内部结构
- 附录、术语表、错误码、关键字、限制

## 拆分规则

拆分混合型章节：

- 视图字段定义归入 `fact`；用该视图确认问题的操作指引归入 `guide`
- 修复动作的命令语义归入 `solution`；仅涉及语法的通用对象参考可保留为 `fact`
- 参数语义归入 `configuration`；把参数当作证据使用的诊断归入 `guide`

## 映射字段

每个目标片段必须包含：

- `chunk_id`
- `category`
- `target_file`
- `source_file`
- `source_title`
- `source_heading_path`
- `source_line_start`
- `source_line_end`
- `classification_reason`
- `retrieval_keywords`
- `use_when`
- `follow_up`
- `review_status`

对于宽泛或含糊的章节，使用 `review_status = "needs_human_review"`。
