# IN subquery rewrite to join and aggregation

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/subquery-optimization.md`
- Source Title: `Subquery Related Optimizations`
- Source Heading Path: `Subquery Related Optimizations > `... IN (SELECT ... FROM ...)``
- Source Line Ranges: `41-67`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `subquery`, `in`, `join`, `aggregation`, `distinct`, `index-join`, `explain`, `system-variable`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0190_550ff6b6a0`
- Source ID: `tidb-docs-8.1:subquery-optimization.md#in-select-from`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `75efee55a3fa8b2f9e985c3b27207712f15d22700faf2116ddc94f47aa2fd0f0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/subquery-optimization#in-select-from
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/subquery-optimization.md

## Retrieval Guidance

- Use When: Use this chunk when searching for the IN subquery rewrite into GROUP BY or DISTINCT plus JOIN, the resulting execution plan shape, or the system variable that controls the optimization.
- Retrieval Keywords: ... IN (SELECT ... FROM ...), IN subquery rewrite to join and aggregation, select * from t1 where t1.a in (select t2.a from t2), select distinct(a) a from t2, IndexJoin_12, HashAgg_21(Build), IndexReader_28, IndexFullScan_27, TableReader_11(Probe), TableRangeScan_10, index join, tidb_opt_insubq_to_join_and_agg, UNIQUE attribute, group by:test.t2.a
- Follow-up Guidance: The source states that tidb_opt_insubq_to_join_and_agg controls this optimization and that it can be manually disabled when the optimization is not suitable.
- Classification Note: This is classified as performance because the official content explains a rewrite intended to improve query performance and discusses when it helps or hurts execution.

## Official Source Content

## `... IN (SELECT ... FROM ...)`

In this case, the subquery of `IN` is rewritten into `SELECT ... FROM ... GROUP ...`, and then rewritten into the normal form of `JOIN`.

For example, `select * from t1 where t1.a in (select t2.a from t2)` is rewritten as `select t1.* from t1, (select distinct(a) a from t2) t2 where t1.a = t2. The form of a`. The `DISTINCT` attribute here can be eliminated automatically if `t2.a` has the `UNIQUE` attribute.

```sql
explain select * from t1 where t1.a in (select t2.a from t2);
```

```sql
+------------------------------+---------+-----------+------------------------+----------------------------------------------------------------------------+
| id                           | estRows | task      | access object          | operator info                                                              |
+------------------------------+---------+-----------+------------------------+----------------------------------------------------------------------------+
| IndexJoin_12                 | 9990.00 | root      |                        | inner join, inner:TableReader_11, outer key:test.t2.a, inner key:test.t1.a |
| ├─HashAgg_21(Build)          | 7992.00 | root      |                        | group by:test.t2.a, funcs:firstrow(test.t2.a)->test.t2.a                   |
| │ └─IndexReader_28           | 9990.00 | root      |                        | index:IndexFullScan_27                                                     |
| │   └─IndexFullScan_27       | 9990.00 | cop[tikv] | table:t2, index:idx(a) | keep order:false, stats:pseudo                                             |
| └─TableReader_11(Probe)      | 7992.00 | root      |                        | data:TableRangeScan_10                                                     |
|   └─TableRangeScan_10        | 7992.00 | cop[tikv] | table:t1               | range: decided by [test.t2.a], keep order:false, stats:pseudo              |
+------------------------------+---------+-----------+------------------------+----------------------------------------------------------------------------+
```

This rewrite gets better performance when the `IN` subquery is relatively small and the external query is relatively large, because without rewriting, using `index join` with t2 as the driving table is impossible. However, the disadvantage is that when the aggregation cannot be automatically eliminated during the rewrite and the `t2` table is relatively large, this rewrite affects the performance of the query. Currently, the variable [tidb\_opt\_insubq\_to\_join\_and\_agg](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_insubq_to_join_and_agg) is used to control this optimization. When this optimization is not suitable, you can manually disable it.
