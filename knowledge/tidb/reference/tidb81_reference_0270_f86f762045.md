# EXPLAIN plans for semi join and anti semi join subqueries

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-subqueries.md`
- Source Title: `Explain Statements That Use Subqueries`
- Source Heading Path: `Explain Statements That Use Subqueries > Semi join (correlated subquery) | Explain Statements That Use Subqueries > Anti semi join (`NOT IN` subquery)`
- Source Line Ranges: `99-148`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `subqueries`, `semi-join`, `anti-semi-join`, `correlated-subquery`, `decorrelation`, `merge-join`, `index-join`, `execution-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0270_f86f762045`
- Source ID: `tidb-docs-8.1:explain-subqueries.md#semi-join-correlated-subquery`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4ca0e4af03e281fa6dcdfd82ad2a63d5a37738ad3583518d5b8896b16e5e06ba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-subqueries#semi-join-correlated-subquery
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-subqueries.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting EXPLAIN output for correlated subqueries with IN or NOT IN that show semi join or anti semi join behavior after subquery decorrelation.
- Retrieval Keywords: EXPLAIN correlated subquery, semi join, anti semi join, NOT IN subquery, MergeJoin_9, IndexJoin_16, subquery decorrelation optimization, Selection_21, t1_id != t1.int_col, t1.id != t1.int_col, Merge Join, Index Join, TableRangeScan_10, PRIMARY KEY probe
- Follow-up Guidance: The source explains that EXPLAIN shows the plan after decorrelation, including the rewrite from `t1_id != t1.int_col` to `t1.id != t1.int_col`, and contrasts semi join duplicate elimination with anti semi join rejection for `NOT IN`.
- Classification Note: This is reference content because it explains specific EXPLAIN plan shapes and operator semantics for semi join and anti semi join subqueries in TiDB SQL execution plans.

## Official Source Content

## Semi join (correlated subquery)

In the previous two examples, TiDB is able to perform an `INNER JOIN` operation after the data inside the subquery is made unique (via `StreamAgg`) or guaranteed unique. Both joins are performed using an Index Join.

In this example, TiDB chooses a different execution plan:

```sql
EXPLAIN SELECT * FROM t1 WHERE id IN (SELECT t1_id FROM t2 WHERE t1_id != t1.int_col);
```

```sql
+-----------------------------+----------+-----------+------------------------------+--------------------------------------------------------------------------------------------------------+
| id                          | estRows  | task      | access object                | operator info                                                                                          |
+-----------------------------+----------+-----------+------------------------------+--------------------------------------------------------------------------------------------------------+
| MergeJoin_9                 | 45446.40 | root      |                              | semi join, left key:test.t1.id, right key:test.t2.t1_id, other cond:ne(test.t2.t1_id, test.t1.int_col) |
| ├─IndexReader_24(Build)     | 90000.00 | root      |                              | index:IndexFullScan_23                                                                                 |
| │ └─IndexFullScan_23        | 90000.00 | cop[tikv] | table:t2, index:t1_id(t1_id) | keep order:true                                                                                        |
| └─TableReader_22(Probe)     | 56808.00 | root      |                              | data:Selection_21                                                                                      |
|   └─Selection_21            | 56808.00 | cop[tikv] |                              | ne(test.t1.id, test.t1.int_col)                                                                        |
|     └─TableFullScan_20      | 71010.00 | cop[tikv] | table:t1                     | keep order:true                                                                                        |
+-----------------------------+----------+-----------+------------------------------+--------------------------------------------------------------------------------------------------------+
```

From the result above, you can see that TiDB uses a `Semi Join` algorithm. Semi-join differs from inner join: semi-join only permits the first value on the right key (`t2.t1_id`), which means that the duplicates are eliminated as a part of the join operator task. The join algorithm is also Merge Join, which is like an efficient zipper-merge as the operator reads data from both the left and the right side in sorted order.

The original statement is considered a _correlated subquery_, because the subquery refers to a column (`t1.int_col`) that exists outside of the subquery. However, the output of `EXPLAIN` shows the execution plan after the [subquery decorrelation optimization](https://docs.pingcap.com/tidb/stable/correlated-subquery-optimization) has been applied. The condition `t1_id != t1.int_col` is rewritten to `t1.id != t1.int_col`. TiDB can perform this in `└─Selection_21` as it is reading data from the table `t1`, so this decorrelation and rewriting make the execution a lot more efficient.
## Anti semi join (`NOT IN` subquery)

In the following example, the query semantically returns all rows from the table `t3` _unless_ `t3.t1_id` is in the subquery:

```sql
EXPLAIN SELECT * FROM t3 WHERE t1_id NOT IN (SELECT id FROM t1 WHERE int_col < 100);
```

```sql
+-----------------------------+---------+-----------+---------------+-------------------------------------------------------------------------------------------------------------------------------+
| id                          | estRows | task      | access object | operator info                                                                                                                 |
+-----------------------------+---------+-----------+---------------+-------------------------------------------------------------------------------------------------------------------------------+
| IndexJoin_16                | 799.20  | root      |               | anti semi join, inner:TableReader_12, outer key:test.t3.t1_id, inner key:test.t1.id, equal cond:eq(test.t3.t1_id, test.t1.id) |
| ├─TableReader_28(Build)     | 999.00  | root      |               | data:TableFullScan_27                                                                                                         |
| │ └─TableFullScan_27        | 999.00  | cop[tikv] | table:t3      | keep order:false                                                                                                              |
| └─TableReader_12(Probe)     | 999.00  | root      |               | data:Selection_11                                                                                                             |
|   └─Selection_11            | 999.00  | cop[tikv] |               | lt(test.t1.int_col, 100)                                                                                                      |
|     └─TableRangeScan_10     | 999.00  | cop[tikv] | table:t1      | range: decided by [test.t3.t1_id], keep order:false                                                                           |
+-----------------------------+---------+-----------+---------------+-------------------------------------------------------------------------------------------------------------------------------+
```

This query starts by reading the table `t3` and then probes the table `t1` based on the `PRIMARY KEY`. The join type is an _anti semi join_; anti because this example is for the non-existence of the value (`NOT IN`) and semi-join because only the first row needs to match before the join is rejected.
