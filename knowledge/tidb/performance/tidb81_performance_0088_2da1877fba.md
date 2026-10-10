# TopN or Limit derivation with PARTITION BY

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/derive-topn-from-window.md`
- Source Title: `Derive TopN or Limit from Window Functions`
- Source Heading Path: `Derive TopN or Limit from Window Functions > Usage examples > Window functions with PARTITION BY | Derive TopN or Limit from Window Functions > Usage examples > Window functions with PARTITION BY > Example 3: window functions without ORDER BY`
- Source Line Ranges: `94-126`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `window-functions`, `partition-by`, `row-number`, `limit`, `optimizer`, `clustered-index`, `primary-key`, `pushdown`, `explain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0088_2da1877fba`
- Source ID: `tidb-docs-8.1:derive-topn-from-window.md#window-functions-with-partition-by`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `97cbd0d13667da0cd0cec5574590fd7bead75d49a15c74752a2fbc0e6ecbbca6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/derive-topn-from-window#window-functions-with-partition-by
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/derive-topn-from-window.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the conditions and EXPLAIN behavior for deriving a partition Limit from a ROW_NUMBER() window function with PARTITION BY.
- Retrieval Keywords: window functions with PARTITION BY, ROW_NUMBER() OVER (PARTITION BY id1), partition column is a prefix of the primary key, primary key is a clustered index, primary key(id1,id2) clustered, partition Limit, tidb_opt_derive_topn, EXPLAIN, Limit_23, partition by test.t.id1, offset:0, count:3, Shuffle_26, Sort_25, TableReader_24, TiKV pushdown
- Follow-up Guidance: The source notes that this derived Limit is a partition Limit, meaning the Limit is applied to each group of data with the same id1 value.
- Classification Note: This is classified as performance for SQL because it documents an optimizer rewrite for PARTITION BY window queries and the primary-key conditions required for pushdown of a partition Limit.

## Official Source Content

### Window functions with PARTITION BY

> **Note:**
>
> For a window function containing `PARTITION BY`, the optimization rule only takes effect when the partition column is a prefix of the primary key and the primary key is a clustered index.
#### Example 3: window functions without ORDER BY

```sql
CREATE TABLE t(id1 int, id2 int, value1 int, value2 int, primary key(id1,id2) clustered);
SET tidb_opt_derive_topn=on;
EXPLAIN SELECT * FROM (SELECT ROW_NUMBER() OVER (PARTITION BY id1) AS rownumber FROM t) dt WHERE rownumber <= 3;
```

The result is as follows:

```
+------------------------------------+---------+-----------+---------------+-----------------------------------------------------------------------------------------------+
| id                                 | estRows | task      | access object | operator info                                                                                 |
+------------------------------------+---------+-----------+---------------+-----------------------------------------------------------------------------------------------+
| Projection_10                      | 2.40    | root      |               | Column#6                                                                                      |
| └─Selection_11                     | 2.40    | root      |               | le(Column#6, 3)                                                                               |
|   └─Shuffle_26                     | 3.00    | root      |               | execution info: concurrency:2, data sources:[TableReader_24]                                  |
|     └─Window_12                    | 3.00    | root      |               | row_number()->Column#6 over(partition by test.t.id1 rows between current row and current row) |
|       └─Sort_25                    | 3.00    | root      |               | test.t.id1                                                                                    |
|         └─TableReader_24           | 3.00    | root      |               | data:Limit_23                                                                                 |
|           └─Limit_23               | 3.00    | cop[tikv] |               | partition by test.t.id1, offset:0, count:3                                                    |
|             └─TableFullScan_22     | 3.00    | cop[tikv] | table:t       | keep order:false, stats:pseudo                                                                |
+------------------------------------+---------+-----------+---------------+-----------------------------------------------------------------------------------------------+
```

In this query, the optimizer derives the Limit operator from the window function and pushes it down to TiKV. Note that this Limit is actually a partition Limit, which means that the Limit will be applied to each group of data with the same `id1` value.
