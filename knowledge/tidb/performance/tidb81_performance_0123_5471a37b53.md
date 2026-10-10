# NO_DECORRELATE correlated subquery behavior

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Hints that take effect in query blocks > NO_DECORRELATE()`
- Source Line Ranges: `301-366`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `optimizer-hints`, `correlated-subquery`, `decorrelation`, `apply-operator`, `execution-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0123_5471a37b53`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#no-decorrelate`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2d7df5991d88b5601b23fe30a4ffe687f15efb686d1bd0a78be25fc8f1b7b592`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#no-decorrelate
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how the NO_DECORRELATE() optimizer hint affects correlated subqueries and whether TiDB keeps an Apply operator instead of decorrelating the subquery.
- Retrieval Keywords: NO_DECORRELATE(), correlated subquery, decorrelation, Apply operator, EXISTS, IN, ANY, ALL, SOME, scalar subqueries, execution plan, HashJoin, Apply_12, t2.b = t1.b
- Follow-up Guidance: The examples compare EXPLAIN plans with and without NO_DECORRELATE(), showing a decorrelated plan with join operations versus a plan that still contains the Apply operator.
- Classification Note: This is classified as performance content because it explains an optimizer hint that changes correlated subquery execution plans and execution efficiency.

## Official Source Content

### NO_DECORRELATE()

The `NO_DECORRELATE()` hint tells the optimizer not to try to perform decorrelation for the correlated subquery in the specified query block. This hint is applicable to the `EXISTS`, `IN`, `ANY`, `ALL`, `SOME` subqueries and scalar subqueries that contain correlated columns (that is, correlated subqueries).

When this hint is used in a query block, the optimizer will not try to perform decorrelation for the correlated columns between the subquery and its outer query block, but always use the Apply operator to execute the query.

By default, TiDB tries to [perform decorrelation](https://docs.pingcap.com/tidb/stable/correlated-subquery-optimization) for correlated subqueries to achieve higher execution efficiency. However, in [some scenarios](https://docs.pingcap.com/tidb/stable/correlated-subquery-optimization#restrictions), decorrelation might actually reduce the execution efficiency. In this case, you can use this hint to manually tell the optimizer not to perform decorrelation. For example:

```sql
create table t1(a int, b int);
create table t2(a int, b int, index idx(b));
```

```sql
-- Not using NO_DECORRELATE().
explain select * from t1 where t1.a < (select sum(t2.a) from t2 where t2.b = t1.b);
```

```sql
+----------------------------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------------------+
| id                               | estRows  | task      | access object | operator info                                                                                                |
+----------------------------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------------------+
| HashJoin_11                      | 9990.00  | root      |               | inner join, equal:[eq(test.t1.b, test.t2.b)], other cond:lt(cast(test.t1.a, decimal(10,0) BINARY), Column#7) |
| ├─HashAgg_23(Build)              | 7992.00  | root      |               | group by:test.t2.b, funcs:sum(Column#8)->Column#7, funcs:firstrow(test.t2.b)->test.t2.b                      |
| │ └─TableReader_24               | 7992.00  | root      |               | data:HashAgg_16                                                                                              |
| │   └─HashAgg_16                 | 7992.00  | cop[tikv] |               | group by:test.t2.b, funcs:sum(test.t2.a)->Column#8                                                           |
| │     └─Selection_22             | 9990.00  | cop[tikv] |               | not(isnull(test.t2.b))                                                                                       |
| │       └─TableFullScan_21       | 10000.00 | cop[tikv] | table:t2      | keep order:false, stats:pseudo                                                                               |
| └─TableReader_15(Probe)          | 9990.00  | root      |               | data:Selection_14                                                                                            |
|   └─Selection_14                 | 9990.00  | cop[tikv] |               | not(isnull(test.t1.b))                                                                                       |
|     └─TableFullScan_13           | 10000.00 | cop[tikv] | table:t1      | keep order:false, stats:pseudo                                                                               |
+----------------------------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------------------+
```

From the preceding execution plan, you can see that the optimizer has automatically performed decorrelation. The decorrelated execution plan does not have the Apply operator. Instead, the plan has join operations between the subquery and the outer query block. The original filter condition (`t2.b = t1.b`) with the correlated column becomes a regular join condition.

```sql
-- Using NO_DECORRELATE().
explain select * from t1 where t1.a < (select /*+ NO_DECORRELATE() */ sum(t2.a) from t2 where t2.b = t1.b);
```

```sql
+------------------------------------------+-----------+-----------+------------------------+--------------------------------------------------------------------------------------+
| id                                       | estRows   | task      | access object          | operator info                                                                        |
+------------------------------------------+-----------+-----------+------------------------+--------------------------------------------------------------------------------------+
| Projection_10                            | 10000.00  | root      |                        | test.t1.a, test.t1.b                                                                 |
| └─Apply_12                               | 10000.00  | root      |                        | CARTESIAN inner join, other cond:lt(cast(test.t1.a, decimal(10,0) BINARY), Column#7) |
|   ├─TableReader_14(Build)                | 10000.00  | root      |                        | data:TableFullScan_13                                                                |
|   │ └─TableFullScan_13                   | 10000.00  | cop[tikv] | table:t1               | keep order:false, stats:pseudo                                                       |
|   └─MaxOneRow_15(Probe)                  | 10000.00  | root      |                        |                                                                                      |
|     └─StreamAgg_20                       | 10000.00  | root      |                        | funcs:sum(Column#14)->Column#7                                                       |
|       └─Projection_45                    | 100000.00 | root      |                        | cast(test.t2.a, decimal(10,0) BINARY)->Column#14                                     |
|         └─IndexLookUp_44                 | 100000.00 | root      |                        |                                                                                      |
|           ├─IndexRangeScan_42(Build)     | 100000.00 | cop[tikv] | table:t2, index:idx(b) | range: decided by [eq(test.t2.b, test.t1.b)], keep order:false, stats:pseudo         |
|           └─TableRowIDScan_43(Probe)     | 100000.00 | cop[tikv] | table:t2               | keep order:false, stats:pseudo                                                       |
+------------------------------------------+-----------+-----------+------------------------+--------------------------------------------------------------------------------------+
```

From the preceding execution plan, you can see that the optimizer does not perform decorrelation. The execution plan still contains the Apply operator. The filter condition (`t2.b = t1.b`) with the correlated column is still the filter condition when accessing the `t2` table.
