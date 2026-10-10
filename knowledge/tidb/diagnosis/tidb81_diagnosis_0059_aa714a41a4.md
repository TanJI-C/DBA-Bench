# Troubleshooting INL_JOIN join order and physical plan hint errors

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Troubleshoot common issues that hints do not take effect > `INL_JOIN` hint does not take effect > `INL_JOIN` hint does not take effect due to join order | Optimizer Hints > Troubleshoot common issues that hints do not take effect > Using hints causes the `Can't find a proper physical plan for this query` error`
- Source Line Ranges: `1040-1104`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `optimizer-hints`, `inl_join`, `join-order`, `leading-hint`, `indexjoin`, `physical-plan-errors`, `order_index`, `join-methods`, `hash-join`, `explain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0059_aa714a41a4`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#inl-join-hint-does-not-take-effect-due-to-join-order`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c5d484fcb69ec20cca829c78bf317640fe854ee9545e7c161b905be5d9f40545`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#inl-join-hint-does-not-take-effect-due-to-join-order
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing why an `INL_JOIN` or `TIDB_INLJ` hint does not directly join the intended tables, or when `EXPLAIN` returns `Can't find a proper physical plan for this query` after applying optimizer hints.
- Retrieval Keywords: INL_JOIN hint does not take effect due to join order, TIDB_INLJ, LEADING(t1, t3), inl_join(t3), IndexJoin, join order, EXPLAIN, Can't find a proper physical plan for this query, ORDER_INDEX, NO_HASH_JOIN, NO_MERGE_JOIN, NO_JOIN related hints, tidb_opt_enable_hash_join, set tidb_opt_enable_hash_join=off
- Follow-up Guidance: The content shows that `LEADING(t1, t3)` can be combined with `INL_JOIN` to enforce the join order before specifying the join algorithm, and it lists `ORDER_INDEX`, `NO_JOIN` related hints, and `tidb_opt_enable_hash_join=OFF` as situations that can trigger the physical plan error.
- Classification Note: This is classified as diagnosis content because it explains why optimizer hints do not take effect and enumerates grounded error scenarios for `Can't find a proper physical plan for this query`.

## Official Source Content

#### `INL_JOIN` hint does not take effect due to join order

The [`INL_JOIN(t1, t2)`](#inl_joint1_name--tl_name-) or `TIDB_INLJ(t1, t2)` hint semantically instructs `t1` and `t2` to act as inner tables in an `IndexJoin` operator to join with other tables, rather than directly joining them using an `IndexJoin` operator. For example:

```sql
EXPLAIN SELECT /*+ inl_join(t1, t3) */ * FROM t1, t2, t3 WHERE t1.id = t2.id AND t2.id = t3.id AND t1.id = t3.id;
+---------------------------------+----------+-----------+---------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| id                              | estRows  | task      | access object | operator info                                                                                                                                                           |
+---------------------------------+----------+-----------+---------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| IndexJoin_16                    | 15625.00 | root      |               | inner join, inner:TableReader_13, outer key:test.t2.id, test.t1.id, inner key:test.t3.id, test.t3.id, equal cond:eq(test.t1.id, test.t3.id), eq(test.t2.id, test.t3.id) |
| ├─IndexJoin_34(Build)           | 12500.00 | root      |               | inner join, inner:TableReader_31, outer key:test.t2.id, inner key:test.t1.id, equal cond:eq(test.t2.id, test.t1.id)                                                     |
| │ ├─TableReader_40(Build)       | 10000.00 | root      |               | data:TableFullScan_39                                                                                                                                                   |
| │ │ └─TableFullScan_39          | 10000.00 | cop[tikv] | table:t2      | keep order:false, stats:pseudo                                                                                                                                          |
| │ └─TableReader_31(Probe)       | 10000.00 | root      |               | data:TableRangeScan_30                                                                                                                                                  |
| │   └─TableRangeScan_30         | 10000.00 | cop[tikv] | table:t1      | range: decided by [test.t2.id], keep order:false, stats:pseudo                                                                                                          |
| └─TableReader_13(Probe)         | 12500.00 | root      |               | data:TableRangeScan_12                                                                                                                                                  |
|   └─TableRangeScan_12           | 12500.00 | cop[tikv] | table:t3      | range: decided by [test.t2.id test.t1.id], keep order:false, stats:pseudo                                                                                               |
+---------------------------------+----------+-----------+---------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
```

In the preceding example, `t1` and `t3` are not directly joined together by an `IndexJoin`.

To perform a direct `IndexJoin` between `t1` and `t3`, you can first use [`LEADING(t1, t3)` hint](#leadingt1_name--tl_name-) to specify the join order of `t1` and `t3`, and then use the `INL_JOIN` hint to specify the join algorithm. For example:

```sql
EXPLAIN SELECT /*+ leading(t1, t3), inl_join(t3) */ * FROM t1, t2, t3 WHERE t1.id = t2.id AND t2.id = t3.id AND t1.id = t3.id;
+---------------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------------------------------+
| id                              | estRows  | task      | access object | operator info                                                                                                       |
+---------------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------------------------------+
| Projection_12                   | 15625.00 | root      |               | test.t1.id, test.t1.name, test.t2.id, test.t2.name, test.t3.id, test.t3.name                                        |
| └─HashJoin_21                   | 15625.00 | root      |               | inner join, equal:[eq(test.t1.id, test.t2.id) eq(test.t3.id, test.t2.id)]                                           |
|   ├─TableReader_36(Build)       | 10000.00 | root      |               | data:TableFullScan_35                                                                                               |
|   │ └─TableFullScan_35          | 10000.00 | cop[tikv] | table:t2      | keep order:false, stats:pseudo                                                                                      |
|   └─IndexJoin_28(Probe)         | 12500.00 | root      |               | inner join, inner:TableReader_25, outer key:test.t1.id, inner key:test.t3.id, equal cond:eq(test.t1.id, test.t3.id) |
|     ├─TableReader_34(Build)     | 10000.00 | root      |               | data:TableFullScan_33                                                                                               |
|     │ └─TableFullScan_33        | 10000.00 | cop[tikv] | table:t1      | keep order:false, stats:pseudo                                                                                      |
|     └─TableReader_25(Probe)     | 10000.00 | root      |               | data:TableRangeScan_24                                                                                              |
|       └─TableRangeScan_24       | 10000.00 | cop[tikv] | table:t3      | range: decided by [test.t1.id], keep order:false, stats:pseudo                                                      |
+---------------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------------------------------+
9 rows in set (0.01 sec)
```
### Using hints causes the `Can't find a proper physical plan for this query` error

The `Can't find a proper physical plan for this query` error might occur in the following scenarios:

- A query itself does not require reading indexes in order. That is, for this query, the optimizer does not generate a plan to read indexes in order in any case without using hints. In this case, if the `ORDER_INDEX` hint is specified, this error occurs. To resolve this issue, remove the corresponding `ORDER_INDEX` hint.
- A query excludes all possible join methods by using the `NO_JOIN` related hints.

```sql
CREATE TABLE t1 (a INT);
CREATE TABLE t2 (a INT);
EXPLAIN SELECT /*+ NO_HASH_JOIN(t1), NO_MERGE_JOIN(t1) */ * FROM t1, t2 WHERE t1.a=t2.a;
ERROR 1815 (HY000): Internal : Can't find a proper physical plan for this query
```

- The system variable [`tidb_opt_enable_hash_join`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_hash_join-new-in-v656-v712-and-v740) is set to `OFF`, and all other join types are also excluded.

```sql
CREATE TABLE t1 (a INT);
CREATE TABLE t2 (a INT);
set tidb_opt_enable_hash_join=off;
EXPLAIN SELECT /*+ NO_MERGE_JOIN(t1) */ * FROM t1, t2 WHERE t1.a=t2.a;
ERROR 1815 (HY000): Internal : Can't find a proper physical plan for this query
```
