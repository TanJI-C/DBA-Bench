# TiDB index strategy guidelines and indexing costs

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide > Index strategy in TiDB | A Practical Guide for SQL Tuning > SQL tuning guide > Index strategy in TiDB > Composite index strategy guidelines | A Practical Guide for SQL Tuning > SQL tuning guide > Index strategy in TiDB > The cost of indexing`
- Source Line Ranges: `563-629`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `indexing`, `composite-indexes`, `covering-indexes`, `sorting`, `kv-rpc`, `write-performance`, `hotspots`, `index-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0178_926211e3b8`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#index-strategy-in-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5c90196e36cb676e8bd1d6a7d33399c091e8e5598a2f1d7d5b984ed7dd9bc402`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#index-strategy-in-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB index strategy guidance about reducing KV RPC requests, designing composite indexes, using covering indexes, and understanding indexing costs.
- Retrieval Keywords: Index strategy in TiDB, Composite index strategy guidelines, The cost of indexing, KV RPC requests, Point_Get, Batch_Point_Get, Coprocessor, Avoid full table scans, Avoid sorting operations, covering indexes, composite index, index prefix columns, equivalent conditions, IS NULL, IN (1), sort and limit pushdown to TiKV, multi-value IN conditions, SELECT list, aggregation, non-clustered index, single-phase commit optimization, INSERT, UPDATE, DELETE, write hotspot, monotonically increasing datetime index, TIDB_INDEX_USAGE, information_schema.tidb_index_usage, write/read ratio
- Follow-up Guidance: The source also notes reviewing index usage statistics using `TIDB_INDEX_USAGE` and considering the write/read ratio when designing indexes.
- Classification Note: The official content is classified as performance because it explains how index design affects query efficiency, KV RPC requests, write performance, resource consumption, and hotspot risk.

## Official Source Content

### Index strategy in TiDB

TiDB is a distributed SQL database that separates the SQL layer (TiDB Server) from the storage layer (TiKV). Unlike traditional databases, TiDB does not use a buffer pool to cache data on compute nodes. As a result, SQL query performance and overall cluster performance depend on the number of key-value (KV) RPC requests that need to be processed. Common KV RPC requests include `Point_Get`, `Batch_Point_Get`, and Coprocessor.

To optimize performance in TiDB, it is essential to use indexes effectively, as they can significantly reduce the number of KV RPC requests. Fewer KV RPC requests improve query performance and system efficiency. The following lists some key strategies that help optimize indexing:

- Avoid full table scans.
- Avoid sorting operations.
- Use covering indexes or exclude unnecessary columns to reduce row lookups.

This section explains general indexing strategies and indexing costs. It also provides three practical examples of effective indexing in TiDB, with a focus on composite and covering indexes for SQL tuning.
#### Composite index strategy guidelines

To create an efficient composite index, order your columns strategically. The column order directly affects how efficiently the index filters and sorts data.

Follow these recommended column order guidelines for a composite index:

1. Start with index prefix columns for direct access:
    - Columns with equivalent conditions
    - Columns with `IS NULL` conditions
    - Columns with `IN` conditions that contain a single value, such as `IN (1)`

2. Add columns for sorting next:
    - Let the index handle sorting operations
    - Enable sort and limit pushdown to TiKV
    - Preserve the sorted order

3. Include additional filtering columns to reduce row lookups:
    - `IN` conditions with multiple values
    - Time range conditions on datetime columns
    - Other non-equivalent conditions, such as `!=`, `<>`, `NOT IN`, and `IS NOT NULL`

4. Add columns from the `SELECT` list or used in aggregation to fully utilize a covering index.

**Special consideration: `IN` conditions**

When designing composite indexes, you need to handle `IN` conditions carefully.

- Single value: an `IN` clause with a single value (such as `IN (1)`) works similarly to an equality condition and can be placed at the beginning of the index.
- Multiple values: an `IN` clause with multiple values generates multiple ranges. If you place such a column before columns used for sorting, it can break the sorting order. To maintain the sorting order, make sure to place columns used for sorting before columns with multi-value `IN` conditions in the composite index.
#### The cost of indexing

While indexes can improve query performance, they also introduce costs you should consider:

- Performance impact on writes:
    - A non-clustered index reduces the chance of single-phase commit optimization.
    - Each additional index slows down write operations (such as `INSERT`, `UPDATE`, and `DELETE`).
    - When data is modified, all affected indexes must be updated.
    - The more indexes a table has, the greater the write performance impact.

- Resource consumption:
    - Indexes require additional disk space.
    - More memory is needed to cache frequently accessed indexes.
    - Backup and recovery operations take longer.

- Write hotspot risk:
    - Secondary indexes can create write hotspots. For example, a monotonically increasing datetime index will cause hotspots on table writes.
    - Hotspots can lead to significant performance degradation.

The following lists some best practices:

- Create indexes only when they provide clear performance benefits.
- Regularly review index usage statistics using [`TIDB_INDEX_USAGE`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-index-usage).
- Consider the write/read ratio of your workload when designing indexes.
