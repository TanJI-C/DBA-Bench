# SQL basics, DDL behavior, plan control, and statement blocking

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/sql-faq.md`
- Source Title: `SQL FAQs`
- Source Heading Path: `SQL FAQs | SQL FAQs > Does TiDB support the secondary key? | SQL FAQs > How does TiDB perform when executing DDL operations on a large table? | SQL FAQs > How to choose the right query plan? Do I need to use hints? Or can I use hints? | SQL FAQs > How to prevent the execution of a particular SQL statement? | SQL FAQs > What are the MySQL variables that TiDB is compatible with?`
- Source Line Ranges: `5-62`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `shared`
- Topic Tags: `secondary-index`, `ddl`, `online-ddl`, `backfill`, `optimizer`, `optimizer-hints`, `sql-binding`, `query-watch`, `statement-timeout`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0150_1f5daf96c4`
- Source ID: `tidb-docs-8.1:faq/sql-faq.md#sql-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `433661dc83190dc0510bd227a5ecdb1968f102dca2b3d050bcca1e81e1b95a84`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/sql-faq#sql-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/sql-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about TiDB SQL basics such as secondary keys, online DDL behavior on large tables, query plan control, blocking a specific SQL statement, or MySQL-compatible system variables.
- Retrieval Keywords: secondary key, NOT NULL constraint, unique secondary index, online DDL, DDL does not block DML, adding indexes backfill, tidb_ddl_reorg_worker_cnt, tidb_ddl_reorg_priority, tidb_ddl_error_count_limit, tidb_ddl_reorg_batch_size, cost-based optimizer, optimizer hints, SQL binding, QUERY WATCH, MAX_EXECUTION_TIME, CREATE GLOBAL BINDING, DROP GLOBAL BINDING, tidb_enable_paging, System Variables
- Follow-up Guidance: The chunk also includes the exact SQL binding example using `CREATE GLOBAL BINDING` with `MAX_EXECUTION_TIME(1)` and the matching `DROP GLOBAL BINDING` statement.
- Classification Note: Classified as operation for the sql component because the content explains SQL behavior and operational controls for DDL, optimizer intervention, statement termination, and system variables.

## Official Source Content

# SQL FAQs

This document summarizes the FAQs related to SQL operations in TiDB.
## Does TiDB support the secondary key?

Yes. You can have the [`NOT NULL` constraint](https://docs.pingcap.com/tidb/stable/constraints#not-null) on a non-primary key column with a unique [secondary index](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-secondary-indexes). In this case, the column works as a secondary key.
## How does TiDB perform when executing DDL operations on a large table?

DDL operations of TiDB on large tables are usually not an issue. TiDB supports online DDL operations, and these DDL operations do not block DML operations.

For some DDL operations such as adding columns, deleting columns or dropping indexes, TiDB can perform these operations quickly.

For some heavy DDL operations such as adding indexes, TiDB needs to backfill data, which takes a longer time (depending on the size of the table) and consumes additional resources. The impact on online traffic is tunable. TiDB can do the backfill with multiple threads, and the resource consumed can be set by the following system variables:

- [`tidb_ddl_reorg_worker_cnt`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_worker_cnt)
- [`tidb_ddl_reorg_priority`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_priority)
- [`tidb_ddl_error_count_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_error_count_limit)
- [`tidb_ddl_reorg_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_batch_size)
## How to choose the right query plan? Do I need to use hints? Or can I use hints?

TiDB includes a cost-based optimizer. In most cases, the optimizer chooses the optimal query plan for you. If the optimizer does not work well, you can still use [optimizer hints](https://docs.pingcap.com/tidb/stable/optimizer-hints) to intervene with the optimizer.

In addition, you can also use the [SQL binding](https://docs.pingcap.com/tidb/stable/sql-plan-management#sql-binding) to fix the query plan for a particular SQL statement.
## How to prevent the execution of a particular SQL statement?

For TiDB v7.5.0 or later versions, you can use the [`QUERY WATCH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-query-watch) statement to terminate specific SQL statements. For more details, see [Manage queries that consume more resources than expected (Runaway Queries)](https://docs.pingcap.com/tidb/stable/tidb-resource-control#query-watch-parameters).

For versions earlier than TiDB v7.5.0, you can create [SQL bindings](https://docs.pingcap.com/tidb/stable/sql-plan-management#sql-binding) with the [`MAX_EXECUTION_TIME`](https://docs.pingcap.com/tidb/stable/optimizer-hints#max_execution_timen) hint to limit the execution time of a particular statement to a small value (for example, 1ms). In this way, the statement is terminated automatically by the threshold.

For example, to prevent the execution of `SELECT * FROM t1, t2 WHERE t1.id = t2.id`, you can use the following SQL binding to limit the execution time of the statement to 1ms:

```sql
CREATE GLOBAL BINDING for
    SELECT * FROM t1, t2 WHERE t1.id = t2.id
USING
    SELECT /*+ MAX_EXECUTION_TIME(1) */ * FROM t1, t2 WHERE t1.id = t2.id;
```

> **Note:**
>
> The precision of `MAX_EXECUTION_TIME` is roughly 100ms. Before TiDB terminates the SQL statement, the tasks in TiKV might be started. To reduce the TiKV resource consumption in such case, it is recommended to set [`tidb_enable_paging`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_paging-new-in-v540) to `ON`.

Dropping this SQL binding will remove the limit.

```sql
DROP GLOBAL BINDING for
    SELECT * FROM t1, t2 WHERE t1.id = t2.id;
```
## What are the MySQL variables that TiDB is compatible with?

See [System Variables](https://docs.pingcap.com/tidb/stable/system-variables).
