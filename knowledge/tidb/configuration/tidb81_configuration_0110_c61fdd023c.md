# Disable EXPLAIN pre-execution of scalar subqueries

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-walkthrough.md`
- Source Title: `EXPLAIN Walkthrough`
- Source Heading Path: ``EXPLAIN` Walkthrough > Disable the early execution of subqueries`
- Source Line Ranges: `218-268`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `explain`, `subquery`, `scalar-subquery`, `system-variable`, `query-optimization`, `troubleshooting`, `execution-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0110_c61fdd023c`
- Source ID: `tidb-docs-8.1:explain-walkthrough.md#disable-the-early-execution-of-subqueries`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0a9c20baee6134597c634cc9cf50f1919f6634e8ae1598412c64c8e7eebdce93`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-walkthrough#disable-the-early-execution-of-subqueries
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-walkthrough.md

## Retrieval Guidance

- Use When: Use this chunk when you need the EXPLAIN behavior for scalar subqueries, including how to disable early subquery execution with `tidb_opt_enable_non_eval_scalar_subquery` and how the plan output changes.
- Retrieval Keywords: Disable the early execution of subqueries, tidb_opt_enable_non_eval_scalar_subquery, EXPLAIN SELECT * FROM t2 WHERE a = (SELECT a FROM t1), SET @@tidb_opt_enable_non_eval_scalar_subquery = ON, ScalarSubQuery_10, ScalarQueryCol#5, eq(test.t2.a, 1), eq(test.t2.a, ScalarQueryCol#5), TableFullScan_12, TableFullScan_14, TableFullScan_8, MaxOneRow_6, Selection_13, TableReader_15, EXPLAIN ANALYZE
- Follow-up Guidance: The official note states that `tidb_opt_enable_non_eval_scalar_subquery` only affects `EXPLAIN`, while `EXPLAIN ANALYZE` still pre-executes the subquery in advance.
- Classification Note: This is classified as configuration because the official content centers on the `tidb_opt_enable_non_eval_scalar_subquery` system variable and its effect on EXPLAIN output for scalar subqueries.

## Official Source Content

## Disable the early execution of subqueries

During query optimization, TiDB pre-executes subqueries that can be directly calculated. For example:

```sql
CREATE TABLE t1(a int);
INSERT INTO t1 VALUES(1);
CREATE TABLE t2(a int);
EXPLAIN SELECT * FROM t2 WHERE a = (SELECT a FROM t1);
```

```sql
+--------------------------+----------+-----------+---------------+--------------------------------+
| id                       | estRows  | task      | access object | operator info                  |
+--------------------------+----------+-----------+---------------+--------------------------------+
| TableReader_14           | 10.00    | root      |               | data:Selection_13              |
| └─Selection_13           | 10.00    | cop[tikv] |               | eq(test.t2.a, 1)               |
|   └─TableFullScan_12     | 10000.00 | cop[tikv] | table:t2      | keep order:false, stats:pseudo |
+--------------------------+----------+-----------+---------------+--------------------------------+
3 rows in set (0.00 sec)
```

In the preceding example, the `a = (SELECT a FROM t1)` subquery is calculated during optimization and rewritten as `t2.a=1`. This allows more optimizations such as constant propagation and folding during optimization. However, it affects the execution time of the `EXPLAIN` statement. When the subquery itself takes a long time to execute, the `EXPLAIN` statement might not be completed, which could affect online troubleshooting.

Starting from v7.3.0, TiDB introduces the [`tidb_opt_enable_non_eval_scalar_subquery`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_non_eval_scalar_subquery-new-in-v730) system variable, which controls whether to disable the pre-execution of such subqueries in `EXPLAIN`. The default value of this variable is `OFF`, which means that the subquery is pre-calculated. You can set this variable to `ON` to disable the pre-execution of subqueries:

```sql
SET @@tidb_opt_enable_non_eval_scalar_subquery = ON;
EXPLAIN SELECT * FROM t2 WHERE a = (SELECT a FROM t1);
```

```sql
+---------------------------+----------+-----------+---------------+---------------------------------+
| id                        | estRows  | task      | access object | operator info                   |
+---------------------------+----------+-----------+---------------+---------------------------------+
| Selection_13              | 8000.00  | root      |               | eq(test.t2.a, ScalarQueryCol#5) |
| └─TableReader_15          | 10000.00 | root      |               | data:TableFullScan_14           |
|   └─TableFullScan_14      | 10000.00 | cop[tikv] | table:t2      | keep order:false, stats:pseudo  |
| ScalarSubQuery_10         | N/A      | root      |               | Output: ScalarQueryCol#5        |
| └─MaxOneRow_6             | 1.00     | root      |               |                                 |
|   └─TableReader_9         | 1.00     | root      |               | data:TableFullScan_8            |
|     └─TableFullScan_8     | 1.00     | cop[tikv] | table:t1      | keep order:false, stats:pseudo  |
+---------------------------+----------+-----------+---------------+---------------------------------+
7 rows in set (0.00 sec)
```

As you can see, the scalar subquery is not expanded during the execution, which makes it easier to understand the specific execution process of such SQL.

> **Note:**
>
> [`tidb_opt_enable_non_eval_scalar_subquery`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_non_eval_scalar_subquery-new-in-v730) only affects the behavior of the `EXPLAIN` statement, and the `EXPLAIN ANALYZE` statement still pre-executes the subquery in advance.
