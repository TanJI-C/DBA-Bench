# TopN or Limit derivation overview and non-partitioned examples

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/derive-topn-from-window.md`
- Source Title: `Derive TopN or Limit from Window Functions`
- Source Heading Path: `Derive TopN or Limit from Window Functions | Derive TopN or Limit from Window Functions > Limitations | Derive TopN or Limit from Window Functions > Usage examples | Derive TopN or Limit from Window Functions > Usage examples > Window functions without PARTITION BY | Derive TopN or Limit from Window Functions > Usage examples > Window functions without PARTITION BY > Example 1: window functions without ORDER BY | Derive TopN or Limit from Window Functions > Usage examples > Window functions without PARTITION BY > Example 2: window functions with ORDER BY`
- Source Line Ranges: `5-93`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `window-functions`, `row-number`, `topn`, `limit`, `optimizer`, `sql-rewrite`, `session-variable`, `pushdown`, `explain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0087_3dbd93de1b`
- Source ID: `tidb-docs-8.1:derive-topn-from-window.md#derive-topn-or-limit-from-window-functions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3ff5ecffba23d56215eecee717642fccedea0e30f8209c6fefa5c99fff810288`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/derive-topn-from-window#derive-topn-or-limit-from-window-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/derive-topn-from-window.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how TiDB derives a TopN or Limit from ROW_NUMBER() window queries, including enabling tidb_opt_derive_topn, supported filter forms, and EXPLAIN plans without PARTITION BY.
- Retrieval Keywords: Derive TopN or Limit from Window Functions, tidb_opt_derive_topn, ROW_NUMBER(), RANK(), rownumber <= 3, filter on the ROW_NUMBER() results, < or <=, TopN operator, Limit operator, window functions without PARTITION BY, window functions without ORDER BY, window functions with ORDER BY, EXPLAIN, TopN pushdown, Limit pushdown, TiKV, TiFlash, WITH t_topN AS (SELECT a FROM t1 ORDER BY a LIMIT 3), Selection_10, Window_11, Limit_15, TopN_24
- Follow-up Guidance: The source also states that deriving TopN or Limit from window functions is disabled by default, can be enabled with SET tidb_opt_derive_topn=ON, and can be disabled by setting it to OFF or using the optimization rule blocklist.
- Classification Note: This is classified as performance for SQL because the content describes an optimizer SQL rewrite that converts ROW_NUMBER() filtering into TopN or Limit operators and shows pushdown in EXPLAIN plans.

## Official Source Content

# Derive TopN or Limit from Window Functions

[Window Functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions) are a common type of SQL function. When you use a window function for row numbering, such as `ROW_NUMBER()` or `RANK()`, it is common to filter the results after the window function is evaluated. For example:

```sql
SELECT * FROM (SELECT ROW_NUMBER() OVER (ORDER BY a) AS rownumber FROM t) dt WHERE rownumber <= 3
```

In a typical SQL execution process, TiDB first sorts all data in the table `t`, then calculates the `ROW_NUMBER()` result for each row, and finally filters with `rownumber <= 3`.

Starting from v7.0.0, TiDB supports deriving the TopN or Limit operator from window functions. With this optimization rule, TiDB can rewrite the original SQL into an equivalent form as follows:

```sql
WITH t_topN AS (SELECT a FROM t1 ORDER BY a LIMIT 3) SELECT * FROM (SELECT ROW_NUMBER() OVER (ORDER BY a) AS rownumber FROM t_topN) dt WHERE rownumber <= 3
```

After rewriting, TiDB can derive a TopN operator from the window function and the subsequent filter condition. Compared with the Sort operator in the original SQL (`ORDER BY`), the TopN operator has a much higher execution efficiency. In addition, both TiKV and TiFlash support pushing down the TopN operator, which further improves the performance of the rewritten SQL.

Deriving TopN or Limit from window functions is disabled by default. To enable this feature, you can set the session variable [tidb_opt_derive_topn](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_derive_topn-new-in-v700) to `ON`.

After enabling this feature, you can disable it by performing one of the following operations:

* Set the session variable [tidb_opt_derive_topn](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_derive_topn-new-in-v700) to `OFF`.
* Follow the steps described in [The blocklist of optimization rules and expression pushdown](https://docs.pingcap.com/tidb/stable/blocklist-control-plan).
## Limitations

* Only the `ROW_NUMBER()` window function is supported for SQL rewriting.
* TiDB can only rewrite SQL when filtering on the `ROW_NUMBER()` results and the filter condition is `<` or `<=`.
## Usage examples

The following examples demonstrate how to use the optimization rule.
### Window functions without PARTITION BY
#### Example 1: window functions without ORDER BY

```sql
CREATE TABLE t(id int, value int);
SET tidb_opt_derive_topn=on;
EXPLAIN SELECT * FROM (SELECT ROW_NUMBER() OVER () AS rownumber FROM t) dt WHERE rownumber <= 3;
```

The result is as follows:

```
+----------------------------------+---------+-----------+---------------+-----------------------------------------------------------------------+
| id                               | estRows | task      | access object | operator info                                                         |
+----------------------------------+---------+-----------+---------------+-----------------------------------------------------------------------+
| Projection_9                     | 2.40    | root      |               | Column#5                                                              |
| └─Selection_10                   | 2.40    | root      |               | le(Column#5, 3)                                                       |
|   └─Window_11                    | 3.00    | root      |               | row_number()->Column#5 over(rows between current row and current row) |
|     └─Limit_15                   | 3.00    | root      |               | offset:0, count:3                                                     |
|       └─TableReader_26           | 3.00    | root      |               | data:Limit_25                                                         |
|         └─Limit_25               | 3.00    | cop[tikv] |               | offset:0, count:3                                                     |
|           └─TableFullScan_24     | 3.00    | cop[tikv] | table:t       | keep order:false, stats:pseudo                                        |
+----------------------------------+---------+-----------+---------------+-----------------------------------------------------------------------+
```

In this query, the optimizer derives the Limit operator from the window function and pushes it down to TiKV.
#### Example 2: window functions with ORDER BY

```sql
CREATE TABLE t(id int, value int);
SET tidb_opt_derive_topn=on;
EXPLAIN SELECT * FROM (SELECT ROW_NUMBER() OVER (ORDER BY value) AS rownumber FROM t) dt WHERE rownumber <= 3;
```

The result is as follows:

```
+----------------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------+
| id                               | estRows  | task      | access object | operator info                                                                               |
+----------------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------+
| Projection_10                    | 2.40     | root      |               | Column#5                                                                                    |
| └─Selection_11                   | 2.40     | root      |               | le(Column#5, 3)                                                                             |
|   └─Window_12                    | 3.00     | root      |               | row_number()->Column#5 over(order by test.t.value rows between current row and current row) |
|     └─TopN_13                    | 3.00     | root      |               | test.t.value, offset:0, count:3                                                             |
|       └─TableReader_25           | 3.00     | root      |               | data:TopN_24                                                                                |
|         └─TopN_24                | 3.00     | cop[tikv] |               | test.t.value, offset:0, count:3                                                             |
|           └─TableFullScan_23     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo                                                              |
+----------------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------+
```

In this query, the optimizer derives the TopN operator from the window function and pushes it down to TiKV.
