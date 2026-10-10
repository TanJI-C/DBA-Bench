# Distinct optimization for SELECT DISTINCT and aggregate DISTINCT pushdown

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/agg-distinct-optimization.md`
- Source Title: `Distinct Optimization`
- Source Heading Path: `Distinct Optimization | Distinct Optimization > `DISTINCT` modifier in `SELECT` statements | Distinct Optimization > `DISTINCT` option in aggregate functions`
- Source Line Ranges: `5-68`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiflash`, `sql`
- Topic Tags: `distinct`, `query-optimizer`, `select-distinct`, `group-by`, `aggregate-functions`, `pushdown`, `coprocessor`, `system-variables`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0002_cf4c2c89cd`
- Source ID: `tidb-docs-8.1:agg-distinct-optimization.md#distinct-optimization`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b1fe361ac5fcf8ae906f099d7842dad5fa88e25a5f7ddf9b7669bb51049816fa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/agg-distinct-optimization#distinct-optimization
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/agg-distinct-optimization.md

## Retrieval Guidance

- Use When: Use this chunk when explaining how TiDB optimizes `SELECT DISTINCT` by transforming it to `GROUP BY`, or when checking how `count(distinct a)` can be rewritten and pushed to the TiKV or TiFlash Coprocessor.
- Retrieval Keywords: Distinct Optimization, SELECT DISTINCT, GROUP BY, DISTINCT modifier in SELECT statements, DISTINCT option in aggregate functions, count(distinct a), tidb_opt_distinct_agg_push_down, distinct-agg-push-down, TiKV Coprocessor, TiFlash Coprocessor, HashAgg, StreamAgg, EXPLAIN, DESC
- Follow-up Guidance: The source shows example `EXPLAIN` and `DESC` output before and after `set session tidb_opt_distinct_agg_push_down = 1`, including `HashAgg_5` in `cop[tikv]` for duplicate removal on column `a`.
- Classification Note: This is classified as performance content because it describes optimizer behavior and pushdown of distinct aggregation that can reduce computation overhead in the TiDB layer.

## Official Source Content

# Distinct Optimization

This document introduces the `distinct` optimization in the TiDB query optimizer, including `SELECT DISTINCT` and `DISTINCT` in the aggregate functions.
## `DISTINCT` modifier in `SELECT` statements

The `DISTINCT` modifier specifies removal of duplicate rows from the result set. `SELECT DISTINCT` is transformed to `GROUP BY`, for example:

```sql
mysql> explain SELECT DISTINCT a from t;
+--------------------------+---------+-----------+---------------+-------------------------------------------------------+
| id                       | estRows | task      | access object | operator info                                         |
+--------------------------+---------+-----------+---------------+-------------------------------------------------------+
| HashAgg_6                | 2.40    | root      |               | group by:test.t.a, funcs:firstrow(test.t.a)->test.t.a |
| └─TableReader_11         | 3.00    | root      |               | data:TableFullScan_10                                 |
|   └─TableFullScan_10     | 3.00    | cop[tikv] | table:t       | keep order:false, stats:pseudo                        |
+--------------------------+---------+-----------+---------------+-------------------------------------------------------+
3 rows in set (0.00 sec)
```
## `DISTINCT` option in aggregate functions

Usually, aggregate functions with the `DISTINCT` option is executed in the TiDB layer in a single-threaded execution model.

The [`tidb_opt_distinct_agg_push_down`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_distinct_agg_push_down) system variable or the [`distinct-agg-push-down`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#distinct-agg-push-down) configuration item in TiDB controls whether to rewrite the distinct aggregate queries and push them to the TiKV or TiFlash Coprocessor.

The [`tidb_opt_distinct_agg_push_down`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_distinct_agg_push_down) system variable in TiDB controls whether to rewrite the distinct aggregate queries and push them to the TiKV or TiFlash Coprocessor.

Take the following queries as an example of this optimization. `tidb_opt_distinct_agg_push_down` is disabled by default, which means the aggregate functions are executed in the TiDB layer. After enabling this optimization by setting its value to `1`, the `distinct a` part of `count(distinct a)` is pushed to TiKV or TiFlash Coprocessor: there is a HashAgg_5 to remove the duplicated values on column a in the TiKV Coprocessor. It might reduce the computation overhead of `HashAgg_8` in the TiDB layer.

```sql
mysql> desc select count(distinct a) from test.t;
+-------------------------+----------+-----------+---------------+------------------------------------------+
| id                      | estRows  | task      | access object | operator info                            |
+-------------------------+----------+-----------+---------------+------------------------------------------+
| StreamAgg_6             | 1.00     | root      |               | funcs:count(distinct test.t.a)->Column#4 |
| └─TableReader_10        | 10000.00 | root      |               | data:TableFullScan_9                     |
|   └─TableFullScan_9     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo           |
+-------------------------+----------+-----------+---------------+------------------------------------------+
3 rows in set (0.01 sec)

mysql> set session tidb_opt_distinct_agg_push_down = 1;
Query OK, 0 rows affected (0.00 sec)

mysql> desc select count(distinct a) from test.t;
+---------------------------+----------+-----------+---------------+------------------------------------------+
| id                        | estRows  | task      | access object | operator info                            |
+---------------------------+----------+-----------+---------------+------------------------------------------+
| HashAgg_8                 | 1.00     | root      |               | funcs:count(distinct test.t.a)->Column#3 |
| └─TableReader_9           | 1.00     | root      |               | data:HashAgg_5                           |
|   └─HashAgg_5             | 1.00     | cop[tikv] |               | group by:test.t.a,                       |
|     └─TableFullScan_7     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo           |
+---------------------------+----------+-----------+---------------+------------------------------------------+
4 rows in set (0.00 sec)
```
