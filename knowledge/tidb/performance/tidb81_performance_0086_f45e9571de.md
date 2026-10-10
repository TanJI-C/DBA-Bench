# Correlated subquery decorrelation behavior, restrictions, and EXPLAIN examples

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/correlated-subquery-optimization.md`
- Source Title: `Decorrelation of Correlated Subquery`
- Source Heading Path: `Decorrelation of Correlated Subquery | Decorrelation of Correlated Subquery > Introduction | Decorrelation of Correlated Subquery > Restrictions | Decorrelation of Correlated Subquery > Example`
- Source Line Ranges: `5-103`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `correlated-subquery`, `decorrelation`, `join-rewrite`, `optimizer-hints`, `sql-plan-management`, `blocklist`, `explain`, `index-range-scan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0086_f45e9571de`
- Source ID: `tidb-docs-8.1:correlated-subquery-optimization.md#decorrelation-of-correlated-subquery`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f85babaa1bb3de679d1b3a9bf0520e75ea011c3caea656d13b8a18f505d312b5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/correlated-subquery-optimization#decorrelation-of-correlated-subquery
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/correlated-subquery-optimization.md

## Retrieval Guidance

- Use When: Use this chunk when searching for how TiDB decorrelates a correlated subquery into JOIN, what restrictions apply, and how EXPLAIN differs when NO_DECORRELATE or the decorrelate rule blacklist is used.
- Retrieval Keywords: Decorrelation of Correlated Subquery, correlated subquery, decorrelation, JOIN rewrite, NO_DECORRELATE, subquery decorrelation, optimizer hint, SQL Plan Management, opt_rule_blacklist, decorrelate, admin reload opt_rule_blacklist, EXPLAIN, HashJoin_11, Apply_12, IndexRangeScan_42, range: decided by [eq(test.t2.b, test.t1.b)], index idx(b), t1.a < (select sum(t2.a) from t2 where t2.b = t1.b)
- Follow-up Guidance: The examples show that after disabling decorrelation with NO_DECORRELATE or by inserting "decorrelate" into mysql.opt_rule_blacklist and reloading it, EXPLAIN changes from HashJoin to Apply and shows IndexRangeScan with range decided by eq(test.t2.b, test.t1.b).
- Classification Note: This is classified as performance for SQL because the content explains an optimizer rewrite for correlated subqueries, its execution-plan impact in TiDB and TiKV, and how it affects index range query usage.

## Official Source Content

# Decorrelation of Correlated Subquery

[Subquery related optimizations](https://docs.pingcap.com/tidb/stable/subquery-optimization) describes how TiDB handles subqueries when there are no correlated columns. Because decorrelation of correlated subquery is complex, this article introduces some simple scenarios and the scope to which the optimization rule applies.
## Introduction

Take `select * from t1 where t1.a < (select sum(t2.a) from t2 where t2.b = t1.b)` as an example. The subquery `t1.a < (select sum(t2.a) from t2 where t2.b = t1.b)` here refers to the correlated column in the query condition `t2.b=t1.b`, this condition happens to be an equivalent condition, so the query can be rewritten as `select t1.* from t1, (select b, sum(a) sum_a from t2 group by b) t2 where t1.b = t2.b and t1.a < t2.sum_a;`. In this way, a correlated subquery is rewritten into `JOIN`.

The reason why TiDB needs to do this rewriting is that the correlated subquery is bound to its external query result every time the subquery is executed. In the above example, if `t1.a` has 10 million values, this subquery would repeat 10 million times, because the condition `t2.b=t1.b` varies with the value of `t1.a`. When the correlation is lifted somehow, this subquery would execute only once.
## Restrictions

The disadvantage of this rewriting is that when the correlation is not lifted, the optimizer can use the index on the correlated column. That is, although this subquery may repeat many times, the index can be used to filter data each time. After using the rewriting rule, the position of the correlated column usually changes. Although the subquery is only executed once, the single execution time would be longer than that without decorrelation.

Therefore, when there are few external values, do not perform decorrelation, which might bring better execution performance. In this case, you can disable this optimization by using the [`NO_DECORRELATE`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_decorrelate) optimizer hint or by disabling the "subquery decorrelation" optimization rule in the [blocklist of optimization rules and expression pushdown](https://docs.pingcap.com/tidb/stable/blocklist-control-plan). In most cases, it is recommended to use the optimizer hint along with [SQL Plan Management](https://docs.pingcap.com/tidb/stable/sql-plan-management) to disable the decorrelation.
## Example

```sql
create table t1(a int, b int);
create table t2(a int, b int, index idx(b));
explain select * from t1 where t1.a < (select sum(t2.a) from t2 where t2.b = t1.b);
```

```sql
+----------------------------------+----------+-----------+---------------+-----------------------------------------------------------------------------------------+
| id                               | estRows  | task      | access object | operator info                                                                           |
+----------------------------------+----------+-----------+---------------+-----------------------------------------------------------------------------------------+
| HashJoin_11                      | 9990.00  | root      |               | inner join, equal:[eq(test.t1.b, test.t2.b)], other cond:lt(cast(test.t1.a), Column#7)  |
| ├─HashAgg_23(Build)              | 7992.00  | root      |               | group by:test.t2.b, funcs:sum(Column#8)->Column#7, funcs:firstrow(test.t2.b)->test.t2.b |
| │ └─TableReader_24               | 7992.00  | root      |               | data:HashAgg_16                                                                         |
| │   └─HashAgg_16                 | 7992.00  | cop[tikv] |               | group by:test.t2.b, funcs:sum(test.t2.a)->Column#8                                      |
| │     └─Selection_22             | 9990.00  | cop[tikv] |               | not(isnull(test.t2.b))                                                                  |
| │       └─TableFullScan_21       | 10000.00 | cop[tikv] | table:t2      | keep order:false, stats:pseudo                                                          |
| └─TableReader_15(Probe)          | 9990.00  | root      |               | data:Selection_14                                                                       |
|   └─Selection_14                 | 9990.00  | cop[tikv] |               | not(isnull(test.t1.b))                                                                  |
|     └─TableFullScan_13           | 10000.00 | cop[tikv] | table:t1      | keep order:false, stats:pseudo                                                          |
+----------------------------------+----------+-----------+---------------+-----------------------------------------------------------------------------------------+

```

The above is an example where the optimization takes effect. `HashJoin_11` is a normal `inner join`.

Then, you can use the `NO_DECORRELATE` optimizer hint to tell the optimizer not to perform decorrelation for the subquery:

```sql
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

Disabling the decorrelation rule can also achieve the same effect:

```sql
insert into mysql.opt_rule_blacklist values("decorrelate");
admin reload opt_rule_blacklist;
explain select * from t1 where t1.a < (select sum(t2.a) from t2 where t2.b = t1.b);
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

After disabling the subquery decorrelation rule, you can see `range: decided by [eq(test.t2.b, test.t1.b)]` in `operator info` of `IndexRangeScan_42(Build)`. It means that the decorrelation of correlated subquery is not performed and TiDB uses the index range query.
