# Troubleshooting inapplicable index join hints

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Troubleshoot common issues that hints do not take effect > `INL_JOIN` hint does not take effect > `INL_JOIN` hint does not take effect when built-in functions are used on columns for joining tables | Optimizer Hints > Troubleshoot common issues that hints do not take effect > `INL_JOIN` hint does not take effect > `INL_JOIN`, `INL_HASH_JOIN`, and `INL_MERGE_JOIN` hints do not take effect due to collation incompatibility`
- Source Line Ranges: `938-1039`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `optimizer-hints`, `indexjoin`, `inl_join`, `inl_hash_join`, `inl_merge_join`, `collation`, `query-plan`, `show-warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0058_4ebc6ba497`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#inl-join-hint-does-not-take-effect-when-built-in-functions-are-used-on-columns-for-joining-tables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `54ee2a5413e9e4115f6d744d1c71780cd33254f0779df44d15b29fe945ddab6d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#inl-join-hint-does-not-take-effect-when-built-in-functions-are-used-on-columns-for-joining-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing why `INL_JOIN`, `INL_HASH_JOIN`, or `INL_MERGE_JOIN` is inapplicable, especially when `EXPLAIN` shows `HashJoin`, `SHOW WARNINGS` returns warning 1815, built-in functions like `SUBSTR` appear on join columns, or the join keys have incompatible collations.
- Retrieval Keywords: INL_JOIN hint does not take effect, INL_HASH_JOIN, INL_MERGE_JOIN, TIDB_INLJ, IndexJoin, HashJoin, SHOW WARNINGS, Warning 1815, Optimizer Hint is inapplicable, SUBSTR, built-in function on join columns, Projection as probe side of IndexJoin, Selection operator as probe side of IndexJoin, tidb_enable_inl_join_inner_multi_pattern, collation incompatibility, utf8mb4_general_ci, utf8mb4_bin, EXPLAIN SELECT /*+ INL_JOIN(t1, t2) */, EXPLAIN SELECT /*+ tidb_inlj(t1) */
- Follow-up Guidance: The content also shows that starting from TiDB v8.0.0, setting `tidb_enable_inl_join_inner_multi_pattern` to `ON` can avoid the built-in-function case, and it demonstrates checking `EXPLAIN` and `SHOW WARNINGS` for the inapplicable hint.
- Classification Note: This is classified as diagnosis for TiDB because the official content explains why index join hints are inapplicable and how that appears in execution plans and warning messages.

## Official Source Content

#### `INL_JOIN` hint does not take effect when built-in functions are used on columns for joining tables

In some cases, if you use a built-in function on a column that joins tables, the optimizer might fail to choose the `IndexJoin` plan, resulting in the `INL_JOIN` hint not taking effect either.

For example, the following query uses the built-in function `substr` on the column `tname` that joins tables:

```sql
CREATE TABLE t1 (id varchar(10) primary key, tname varchar(10));
CREATE TABLE t2 (id varchar(10) primary key, tname varchar(10));
EXPLAIN SELECT /*+ INL_JOIN(t1, t2) */ * FROM t1, t2 WHERE t1.id=t2.id and SUBSTR(t1.tname,1,2)=SUBSTR(t2.tname,1,2);
```

The execution plan is as follows:

```sql
+------------------------------+----------+-----------+---------------+-----------------------------------------------------------------------+
| id                           | estRows  | task      | access object | operator info                                                         |
+------------------------------+----------+-----------+---------------+-----------------------------------------------------------------------+
| HashJoin_12                  | 12500.00 | root      |               | inner join, equal:[eq(test.t1.id, test.t2.id) eq(Column#5, Column#6)] |
| ├─Projection_17(Build)       | 10000.00 | root      |               | test.t2.id, test.t2.tname, substr(test.t2.tname, 1, 2)->Column#6      |
| │ └─TableReader_19           | 10000.00 | root      |               | data:TableFullScan_18                                                 |
| │   └─TableFullScan_18       | 10000.00 | cop[tikv] | table:t2      | keep order:false, stats:pseudo                                        |
| └─Projection_14(Probe)       | 10000.00 | root      |               | test.t1.id, test.t1.tname, substr(test.t1.tname, 1, 2)->Column#5      |
|   └─TableReader_16           | 10000.00 | root      |               | data:TableFullScan_15                                                 |
|     └─TableFullScan_15       | 10000.00 | cop[tikv] | table:t1      | keep order:false, stats:pseudo                                        |
+------------------------------+----------+-----------+---------------+-----------------------------------------------------------------------+
7 rows in set, 1 warning (0.01 sec)
```

```sql
SHOW WARNINGS;
```

```
+---------+------+------------------------------------------------------------------------------------+
| Level   | Code | Message                                                                            |
+---------+------+------------------------------------------------------------------------------------+
| Warning | 1815 | Optimizer Hint /*+ INL_JOIN(t1, t2) */ or /*+ TIDB_INLJ(t1, t2) */ is inapplicable |
+---------+------+------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

As you can see from the preceding example, the `INL_JOIN` hint does not take effect. This is due to a limitation of the optimizer that prevents using the `Projection` or `Selection` operator as the probe side of `IndexJoin`.

Starting from TiDB v8.0.0, you can avoid this issue by setting [`tidb_enable_inl_join_inner_multi_pattern`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_inl_join_inner_multi_pattern-new-in-v700) to `ON`.

```sql
SET @@tidb_enable_inl_join_inner_multi_pattern=ON;
Query OK, 0 rows affected (0.00 sec)

EXPLAIN SELECT /*+ INL_JOIN(t1, t2) */ * FROM t1, t2 WHERE t1.id=t2.id AND SUBSTR(t1.tname,1,2)=SUBSTR(t2.tname,1,2);
+------------------------------+--------------+-----------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------+
| id                           | estRows      | task      | access object | operator info                                                                                                                              |
+------------------------------+--------------+-----------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------+
| IndexJoin_18                 | 12500.00     | root      |               | inner join, inner:Projection_14, outer key:test.t1.id, inner key:test.t2.id, equal cond:eq(Column#5, Column#6), eq(test.t1.id, test.t2.id) |
| ├─Projection_32(Build)       | 10000.00     | root      |               | test.t1.id, test.t1.tname, substr(test.t1.tname, 1, 2)->Column#5                                                                           |
| │ └─TableReader_34           | 10000.00     | root      |               | data:TableFullScan_33                                                                                                                      |
| │   └─TableFullScan_33       | 10000.00     | cop[tikv] | table:t1      | keep order:false, stats:pseudo                                                                                                             |
| └─Projection_14(Probe)       | 100000000.00 | root      |               | test.t2.id, test.t2.tname, substr(test.t2.tname, 1, 2)->Column#6                                                                           |
|   └─TableReader_13           | 10000.00     | root      |               | data:TableRangeScan_12                                                                                                                     |
|     └─TableRangeScan_12      | 10000.00     | cop[tikv] | table:t2      | range: decided by [eq(test.t2.id, test.t1.id)], keep order:false, stats:pseudo                                                             |
+------------------------------+--------------+-----------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------+
7 rows in set (0.00 sec)
```
#### `INL_JOIN`, `INL_HASH_JOIN`, and `INL_MERGE_JOIN` hints do not take effect due to collation incompatibility

When the collation of the join key is incompatible between two tables, the `IndexJoin` operator cannot be utilized to execute the query. In this case, the [`INL_JOIN`](#inl_joint1_name--tl_name-), [`INL_HASH_JOIN`](#inl_hash_join), and [`INL_MERGE_JOIN`](#inl_merge_join) hints do not take effect. For example:

```sql
CREATE TABLE t1 (k varchar(8), key(k)) COLLATE=utf8mb4_general_ci;
CREATE TABLE t2 (k varchar(8), key(k)) COLLATE=utf8mb4_bin;
EXPLAIN SELECT /*+ tidb_inlj(t1) */ * FROM t1, t2 WHERE t1.k=t2.k;
```

The execution plan is as follows:

```sql
+-----------------------------+----------+-----------+----------------------+----------------------------------------------+
| id                          | estRows  | task      | access object        | operator info                                |
+-----------------------------+----------+-----------+----------------------+----------------------------------------------+
| HashJoin_19                 | 12487.50 | root      |                      | inner join, equal:[eq(test.t1.k, test.t2.k)] |
| ├─IndexReader_24(Build)     | 9990.00  | root      |                      | index:IndexFullScan_23                       |
| │ └─IndexFullScan_23        | 9990.00  | cop[tikv] | table:t2, index:k(k) | keep order:false, stats:pseudo               |
| └─IndexReader_22(Probe)     | 9990.00  | root      |                      | index:IndexFullScan_21                       |
|   └─IndexFullScan_21        | 9990.00  | cop[tikv] | table:t1, index:k(k) | keep order:false, stats:pseudo               |
+-----------------------------+----------+-----------+----------------------+----------------------------------------------+
5 rows in set, 1 warning (0.00 sec)
```

In the preceding statements, the collations of `t1.k` and `t2.k` are incompatible (`utf8mb4_general_ci` and `utf8mb4_bin` respectively), which prevents the `INL_JOIN` or `TIDB_INLJ` hint from taking effect.

```sql
SHOW WARNINGS;
+---------+------+----------------------------------------------------------------------------+
| Level   | Code | Message                                                                    |
+---------+------+----------------------------------------------------------------------------+
| Warning | 1815 | Optimizer Hint /*+ INL_JOIN(t1) */ or /*+ TIDB_INLJ(t1) */ is inapplicable |
+---------+------+----------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
