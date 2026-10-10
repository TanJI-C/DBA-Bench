# Parameters, restrictions, failure handling, and internal behavior of non-transactional DML

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/non-transactional-dml.md`
- Source Title: `Non-Transactional DML Statements`
- Source Heading Path: `Non-Transactional DML Statements > Parameter description | Non-Transactional DML Statements > Parameter description > How to select a shard column | Non-Transactional DML Statements > Parameter description > How to set batch size | Non-Transactional DML Statements > Restrictions | Non-Transactional DML Statements > Control batch execution failure | Non-Transactional DML Statements > How it works`
- Source Line Ranges: `258-314`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `non-transactional dml`, `shard column`, `batch size`, `restrictions`, `autocommit`, `memory quota`, `error handling`, `execution model`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0449_1a5ee339a6`
- Source ID: `tidb-docs-8.1:non-transactional-dml.md#parameter-description`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e0475259988f87da23ebc9ab9ea14262b584919886dfd522462136946a52b319`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/non-transactional-dml#parameter-description
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/non-transactional-dml.md

## Retrieval Guidance

- Use When: Use this content when you need the reference details for non-transactional DML parameters, shard column and batch size selection, hard restrictions, error-handling behavior, memory quota interaction, or the internal batch-splitting execution model.
- Retrieval Keywords: Parameter description, Shard column, Batch size, How to select a shard column, How to set batch size, Restrictions, Control batch execution failure, How it works, autocommit, batch-dml, tidb_snapshot, prepare statement, temporary tables, Common Table Expression, ENUM, BIT, SET, JSON, clustered index, _tidb_rowid, tidb_mem_quota_query, tidb_mem_oom_action, tidb_nontransactional_ignore_error, first batch fails, BATCH ON $C$ LIMIT $N$ DELETE FROM ... WHERE $P$, WHERE ($P_i$) AND ($P$), DRY RUN QUERY, DRY RUN
- Follow-up Guidance: The source explains that batch information is stored in memory under the limit of tidb_mem_quota_query, error handling is controlled by tidb_nontransactional_ignore_error, and the generated query and split statements can be viewed through DRY RUN QUERY and DRY RUN.
- Classification Note: This chunk is classified as reference content because it defines parameter meanings, recommended values, restrictions, failure semantics, and the internal execution principle of non-transactional DML statements.

## Official Source Content

## Parameter description

| Parameter | Description | Default value | Required or not | Recommended value |
| :-- | :-- | :-- | :-- | :-- |
| Shard column | The column used to shard batches, such as the `id` column in the above non-transactional DML statement `BATCH ON id LIMIT 2 DELETE FROM t WHERE v < 6`. | TiDB tries to automatically select a shard column (not recommended). | No | Select a column that can meet the `WHERE` condition in the most efficient way. |
| Batch size | Used to control the size of each batch. The number of batches is the number of SQL statements into which DML operations are split, such as `LIMIT 2` in the above non-transactional DML statement `BATCH ON id LIMIT 2 DELETE FROM t WHERE v < 6`. The more batches, the smaller the batch size. | N/A | Yes | 1000-1000000. Too small or too large a batch will lead to performance degradation. |
### How to select a shard column

A non-transactional DML statement uses a column as the basis for data batching, which is the shard column. For higher execution efficiency, a shard column is required to use index. The execution efficiency brought by different indexes and shard columns might vary by dozens of times. When choosing the shard column, consider the following suggestions:

- If you know the application data distribution, according to the `WHERE` condition, choose the column that divides data with smaller ranges after the batching.
    - Ideally, the `WHERE` condition can take advantage of the index of the shard column to reduce the amount of data to be scanned per batch. For example, there is a transaction table that records the start and end time of each transaction, and you want to delete all transaction records whose end time is before one month. If there is an index on the start time of the transaction, and the start and end times of the transaction are relatively close, then you can choose the start time column as the shard column.
    - In a less-than-ideal case, the data distribution of the shard column is completely independent of the `WHERE` condition, and the index of the shard column cannot be used to reduce the scope of the data scan.
- When a clustered index exists, it is recommended to use the primary key (including an `INT` primary key and `_tidb_rowid`) as the shard column, so that the execution efficiency is higher.
- Choose the column with fewer duplicate values.

You can also choose not to specify a shard column. Then, TiDB will use the first column of `handle` as the shard column by default. But if the first column of the primary key of the clustered index is of a data type not supported by non-transactional DML statements (which is `ENUM`, `BIT`, `SET`, `JSON`), TiDB will report an error. You can choose an appropriate shard column according to your application needs.
### How to set batch size

In non-transactional DML statements, the larger the batch size, the fewer SQL statements are split and the slower each SQL statement is executed. The optimal batch size depends on the workload. It is recommended to start from 50000. Either too small or too large batch sizes will cause decreased execution efficiency.

The information of each batch is stored in memory, so too many batches can significantly increase memory consumption. This explains why the batch size cannot be too small. The upper limit of memory consumed by non-transactional statements for storing batch information is the same as [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query), and the action triggered when this limit is exceeded is determined by the configuration item [`tidb_mem_oom_action`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_oom_action-new-in-v610).
## Restrictions

The following are hard restrictions on non-transactional DML statements. If these restrictions are not met, TiDB will report an error.

- The DML statements cannot contain `ORDER BY` or `LIMIT` clauses.
- Subqueries or set operations are not supported.
- The shard column must be indexed. The index can be a single-column index, or the first column of a joint index.
- Must be used in the [`autocommit`](https://docs.pingcap.com/tidb/stable/system-variables#autocommit) mode.
- Cannot be used when batch-dml is enabled.
- Cannot be used when [`tidb_snapshot`](https://docs.pingcap.com/tidb/stable/read-historical-data) is set.
- Cannot be used with the `prepare` statement.
- `ENUM`, `BIT`, `SET`, `JSON` types are not supported as the shard columns.
- Not supported for [temporary tables](https://docs.pingcap.com/tidb/stable/temporary-tables).
- [Common Table Expression](https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-common-table-expression) is not supported.
## Control batch execution failure

Non-transactional DML statements do not satisfy atomicity. Some batches might succeed and some might fail. The system variable [`tidb_nontransactional_ignore_error`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_nontransactional_ignore_error-new-in-v610) controls how the non-transactional DML statements handle errors.

An exception is that if the first batch fails, there is a high probability that the statement itself is wrong. In this case, the entire non-transactional statement will directly return an error.
## How it works

The working principle of non-transactional DML statements is to build into TiDB the automatic splitting of SQL statements. Without non-transactional DML statements, you will need to manually split the SQL statements. To understand the behavior of a non-transactional DML statement, think of it as a user script doing the following tasks:

For the non-transactional DML `BATCH ON $C$ LIMIT $N$ DELETE FROM ... WHERE $P$`, $C$ is the column used for dividing, $N$ is the batch size, and $P$ is the filter condition.

1. According to the filter condition $P$ of the original statement and the specified column $C$ for dividing, TiDB queries all $C$ that satisfy $P$. TiDB sorts these $C$ into groups $B_1 \dots B_k$ according to $N$. For each of all $B_i$, TiDB keeps its first and last $C$ as $S_i$ and $E_i$. The query statement executed in this step can be viewed through [`DRY RUN QUERY`](https://docs.pingcap.com/tidb/stable/non-transactional-dml#query-the-batch-dividing-statement).
2. The data involved in $B_i$ is a subset that satisfies $P_i$: $C$ BETWEEN $S_i$ AND $E_i$. You can use $P_i$ to narrow down the range of data that each batch needs to process.
3. For $B_i$, TiDB embeds the above condition into the `WHERE` condition of the original statement, which makes it WHERE ($P_i$) AND ($P$). The execution result of this step can be viewed through [`DRY RUN`](https://docs.pingcap.com/tidb/stable/non-transactional-dml#query-the-statements-corresponding-to-the-first-and-the-last-batches).
4. For all batches, execute new statements in sequence. The errors for each grouping are collected and combined, and returned as the result of the entire non-transactional DML statement after all groupings are complete.
