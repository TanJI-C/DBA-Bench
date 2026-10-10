# Partitioned window function TopN derivation examples and non-rewrite cases

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/derive-topn-from-window.md`
- Source Title: `Derive TopN or Limit from Window Functions`
- Source Heading Path: `Derive TopN or Limit from Window Functions > Usage examples > Window functions with PARTITION BY > Example 4: window functions with ORDER BY | Derive TopN or Limit from Window Functions > Usage examples > Window functions with PARTITION BY > Example 5: PARTITION BY column is not a prefix of the primary key | Derive TopN or Limit from Window Functions > Usage examples > Window functions with PARTITION BY > Example 6: PARTITION BY column is a prefix of the primary key but not a clustered index`
- Source Line Ranges: `127-204`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `window-functions`, `topn-derivation`, `partition-by`, `order-by`, `optimizer`, `explain`, `pushdown`, `clustered-index`, `primary-key`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0089_c4ab679329`
- Source ID: `tidb-docs-8.1:derive-topn-from-window.md#example-4-window-functions-with-order-by`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a4f7dfe296c6ae76bfc38c288d0fcf4bb7363478dd9b806a85360eb61db768d6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/derive-topn-from-window#example-4-window-functions-with-order-by
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/derive-topn-from-window.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether TiDB derives and pushes down a partition TopN from a ROW_NUMBER window query with PARTITION BY, ORDER BY, clustered or nonclustered primary keys, and EXPLAIN output differences for rewrite and non-rewrite cases.
- Retrieval Keywords: tidb_opt_derive_topn, ROW_NUMBER() OVER (PARTITION BY id1 ORDER BY value1), ROW_NUMBER() OVER (PARTITION BY value1), rownumber <= 3, EXPLAIN, TopN_19, cop[tikv], partition by test.t.id1 order by test.t.value1, offset:0, count:3, Window_12, Sort_22, TableReader_21, TableFullScan_18, primary key(id1,id2) clustered, primary key(id1,id2) nonclustered, PARTITION BY column is not a prefix of the primary key, PARTITION BY column is a prefix of the primary key but not a clustered index, use index(), partition TopN, pushes it down to TiKV
- Follow-up Guidance: The source shows that rewrite happens for the clustered primary key case with ORDER BY and shows two non-rewrite cases: when the PARTITION BY column is not a prefix of the primary key, and when the primary key is nonclustered.
- Classification Note: This is classified as performance because it explains optimizer TopN derivation and pushdown behavior visible in EXPLAIN plans for window-function queries in TiDB.

## Official Source Content

#### Example 4: window functions with ORDER BY

```sql
CREATE TABLE t(id1 int, id2 int, value1 int, value2 int, primary key(id1,id2) clustered);
SET tidb_opt_derive_topn=on;
EXPLAIN SELECT * FROM (SELECT ROW_NUMBER() OVER (PARTITION BY id1 ORDER BY value1) AS rownumber FROM t) dt WHERE rownumber <= 3;
```

The result is as follows:

```
+------------------------------------+----------+-----------+---------------+----------------------------------------------------------------------------------------------------------------------+
| id                                 | estRows  | task      | access object | operator info                                                                                                        |
+------------------------------------+----------+-----------+---------------+----------------------------------------------------------------------------------------------------------------------+
| Projection_10                      | 2.40     | root      |               | Column#6                                                                                                             |
| └─Selection_11                     | 2.40     | root      |               | le(Column#6, 3)                                                                                                      |
|   └─Shuffle_23                     | 3.00     | root      |               | execution info: concurrency:3, data sources:[TableReader_21]                                                         |
|     └─Window_12                    | 3.00     | root      |               | row_number()->Column#6 over(partition by test.t.id1 order by test.t.value1 rows between current row and current row) |
|       └─Sort_22                    | 3.00     | root      |               | test.t.id1, test.t.value1                                                                                            |
|         └─TableReader_21           | 3.00     | root      |               | data:TopN_19                                                                                                         |
|           └─TopN_19                | 3.00     | cop[tikv] |               | partition by test.t.id1 order by test.t.value1, offset:0, count:3                                                    |
|             └─TableFullScan_18     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo                                                                                       |
+------------------------------------+----------+-----------+---------------+----------------------------------------------------------------------------------------------------------------------+
```

In this query, the optimizer derives the TopN operator from the window function and pushes it down to TiKV. Note that this TopN is actually a partition TopN, which means that the TopN will be applied to each group of data with the same `id1` value.
#### Example 5: PARTITION BY column is not a prefix of the primary key

```sql
CREATE TABLE t(id1 int, id2 int, value1 int, value2 int, primary key(id1,id2) clustered);
SET tidb_opt_derive_topn=on;
EXPLAIN SELECT * FROM (SELECT ROW_NUMBER() OVER (PARTITION BY value1) AS rownumber FROM t) dt WHERE rownumber <= 3;
```

The result is as follows:

```
+----------------------------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------+
| id                               | estRows  | task      | access object | operator info                                                                                    |
+----------------------------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------+
| Projection_9                     | 8000.00  | root      |               | Column#6                                                                                         |
| └─Selection_10                   | 8000.00  | root      |               | le(Column#6, 3)                                                                                  |
|   └─Shuffle_15                   | 10000.00 | root      |               | execution info: concurrency:5, data sources:[TableReader_13]                                     |
|     └─Window_11                  | 10000.00 | root      |               | row_number()->Column#6 over(partition by test.t.value1 rows between current row and current row) |
|       └─Sort_14                  | 10000.00 | root      |               | test.t.value1                                                                                    |
|         └─TableReader_13         | 10000.00 | root      |               | data:TableFullScan_12                                                                            |
|           └─TableFullScan_12     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo                                                                   |
+----------------------------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------+
```

In this query, the SQL is not rewritten because the `PARTITION BY` column is not a prefix of the primary key.
#### Example 6: PARTITION BY column is a prefix of the primary key but not a clustered index

```sql
CREATE TABLE t(id1 int, id2 int, value1 int, value2 int, primary key(id1,id2) nonclustered);
SET tidb_opt_derive_topn=on;
EXPLAIN SELECT * FROM (SELECT ROW_NUMBER() OVER (PARTITION BY id1) AS rownumber FROM t use index()) dt WHERE rownumber <= 3;
```

The result is as follows:

```
+----------------------------------+----------+-----------+---------------+-----------------------------------------------------------------------------------------------+
| id                               | estRows  | task      | access object | operator info                                                                                 |
+----------------------------------+----------+-----------+---------------+-----------------------------------------------------------------------------------------------+
| Projection_9                     | 8000.00  | root      |               | Column#7                                                                                      |
| └─Selection_10                   | 8000.00  | root      |               | le(Column#7, 3)                                                                               |
|   └─Shuffle_15                   | 10000.00 | root      |               | execution info: concurrency:5, data sources:[TableReader_13]                                  |
|     └─Window_11                  | 10000.00 | root      |               | row_number()->Column#7 over(partition by test.t.id1 rows between current row and current row) |
|       └─Sort_14                  | 10000.00 | root      |               | test.t.id1                                                                                    |
|         └─TableReader_13         | 10000.00 | root      |               | data:TableFullScan_12                                                                         |
|           └─TableFullScan_12     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo                                                                |
+----------------------------------+----------+-----------+---------------+-----------------------------------------------------------------------------------------------+
```

In this query, although the `PARTITION BY` column is a prefix of the primary key, the SQL is not rewritten because the primary key is not a clustered index.
