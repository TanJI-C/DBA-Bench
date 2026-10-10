# Max/Min elimination optimization rules and execution plans

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/max-min-eliminate.md`
- Source Title: `Eliminate Max/Min`
- Source Heading Path: `Eliminate Max/Min | Eliminate Max/Min > One `max`/`min` function | Eliminate Max/Min > Multiple `max`/`min` functions`
- Source Line Ranges: `5-117`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `query-optimizer`, `max-min`, `topn`, `index-scan`, `execution-plan`, `sql-rewrite`, `aggregate-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0440_9d8bb067ba`
- Source ID: `tidb-docs-8.1:max-min-eliminate.md#eliminate-max-min`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `edd570ef7c297b7771f41882f388a82eb71c1400f11868fd0df68ee8e1e62a0d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/max-min-eliminate#eliminate-max-min
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/max-min-eliminate.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiDB rewrites SQL with `max` or `min` into TopN-based plans and what execution plans appear for single or multiple aggregate functions without `group by`.
- Retrieval Keywords: Eliminate Max/Min, max/min optimization rule, TopN operator, select max(a) from t, select max(a)-min(a) from t, one max/min function, multiple max/min functions, no related group by clause, order by a desc limit 1, order by a asc limit 1, a is not null, Cartesian product of two subqueries, HashJoin CARTESIAN inner join, StreamAgg, Limit, IndexReader, IndexFullScan, keep order:true, desc, index:idx_a(a), full table scan, prefix of some composite index
- Follow-up Guidance: The content also shows the rewritten SQL forms and example `explain` plans, including `StreamAgg`, `Limit`, `IndexReader`, and `IndexFullScan` operators for both single-function and multiple-function cases.
- Classification Note: This is reference content because it explains the optimizer conditions, SQL rewrites, and example execution plans for the `max`/`min` elimination rule in TiDB.

## Official Source Content

# Eliminate Max/Min

When a SQL statement contains `max`/`min` functions, the query optimizer tries to convert the `max`/`min` aggregate functions to the TopN operator by applying the `max`/`min` optimization rule. In this way, TiDB can perform the query more efficiently through indexes.

This optimization rule is divided into the following two types according to the number of `max`/`min` functions in the `select` statement:

- [The statement with only one `max`/`min` function](#one-maxmin-function)
- [The statement with multiple `max`/`min` functions](#multiple-maxmin-functions)
## One `max`/`min` function

When a SQL statement meets the following conditions, this rule is applied:

- The statement contains only one aggregate function, which is `max` or `min`.
- The aggregate function has no related `group by` clause.

For example:

```sql
select max(a) from t
```

The optimization rule rewrites the statement as follows:

```sql
select max(a) from (select a from t where a is not null order by a desc limit 1) t
```

When column `a` has an index, or when column `a` is the prefix of some composite index, with the help of index, the new SQL statement can find the maximum or minimum value by scanning only one row of data. This optimization avoids full table scan.

The example statement has the following execution plan:

```sql
mysql> explain select max(a) from t;
+------------------------------+---------+-----------+-------------------------+-------------------------------------+
| id                           | estRows | task      | access object           | operator info                       |
+------------------------------+---------+-----------+-------------------------+-------------------------------------+
| StreamAgg_13                 | 1.00    | root      |                         | funcs:max(test.t.a)->Column#4       |
| └─Limit_17                   | 1.00    | root      |                         | offset:0, count:1                   |
|   └─IndexReader_27           | 1.00    | root      |                         | index:Limit_26                      |
|     └─Limit_26               | 1.00    | cop[tikv] |                         | offset:0, count:1                   |
|       └─IndexFullScan_25     | 1.00    | cop[tikv] | table:t, index:idx_a(a) | keep order:true, desc, stats:pseudo |
+------------------------------+---------+-----------+-------------------------+-------------------------------------+
5 rows in set (0.00 sec)
```
## Multiple `max`/`min` functions

When a SQL statement meets the following conditions, this rule is applied:

- The statement contains multiple aggregate functions, which are all `max` or `min` functions.
- None of the aggregate functions has a related `group by` clause.
- The columns in each `max`/`min` function has indexes to preserve the order.

For example:

```sql
select max(a) - min(a) from t
```

The optimization rule first checks whether column `a` has an index to preserve its order. If yes, the SQL statement is rewritten as the Cartesian product of two subqueries:

```sql
select max_a - min_a
from
    (select max(a) as max_a from t) t1,
    (select min(a) as min_a from t) t2
```

Through the rewrite, the optimizer can apply the rule for statements with only one `max`/`min` function to the two subqueries respectively. The statement is then rewritten as follows:

```sql
select max_a - min_a
from
    (select max(a) as max_a from (select a from t where a is not null order by a desc limit 1) t) t1,
    (select min(a) as min_a from (select a from t where a is not null order by a asc limit 1) t) t2
```

Similarly, if column `a` has an index to preserve its order, the optimized execution only scans two rows of data instead of the whole table. However, if column `a` does not have an index to preserve its order, this rule results in two full table scans, but the execution only needs one full table scan if it is not rewritten. Therefore, in such cases, this rule is not applied.

The final execution plan is as follows:

```sql
mysql> explain select max(a)-min(a) from t;
+------------------------------------+---------+-----------+-------------------------+-------------------------------------+
| id                                 | estRows | task      | access object           | operator info                       |
+------------------------------------+---------+-----------+-------------------------+-------------------------------------+
| Projection_17                      | 1.00    | root      |                         | minus(Column#4, Column#5)->Column#6 |
| └─HashJoin_18                      | 1.00    | root      |                         | CARTESIAN inner join                |
|   ├─StreamAgg_45(Build)            | 1.00    | root      |                         | funcs:min(test.t.a)->Column#5       |
|   │ └─Limit_49                     | 1.00    | root      |                         | offset:0, count:1                   |
|   │   └─IndexReader_59             | 1.00    | root      |                         | index:Limit_58                      |
|   │     └─Limit_58                 | 1.00    | cop[tikv] |                         | offset:0, count:1                   |
|   │       └─IndexFullScan_57       | 1.00    | cop[tikv] | table:t, index:idx_a(a) | keep order:true, stats:pseudo       |
|   └─StreamAgg_24(Probe)            | 1.00    | root      |                         | funcs:max(test.t.a)->Column#4       |
|     └─Limit_28                     | 1.00    | root      |                         | offset:0, count:1                   |
|       └─IndexReader_38             | 1.00    | root      |                         | index:Limit_37                      |
|         └─Limit_37                 | 1.00    | cop[tikv] |                         | offset:0, count:1                   |
|           └─IndexFullScan_36       | 1.00    | cop[tikv] | table:t, index:idx_a(a) | keep order:true, desc, stats:pseudo |
+------------------------------------+---------+-----------+-------------------------+-------------------------------------+
12 rows in set (0.01 sec)
```
