# TopN and Limit pushdown behavior and examples

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/topn-limit-push-down.md`
- Source Title: `TopN and Limit Operator Push Down`
- Source Heading Path: `TopN and Limit Operator Push Down | TopN and Limit Operator Push Down > Examples | TopN and Limit Operator Push Down > Examples > Example 1: Push down to the Coprocessors in the storage layer | TopN and Limit Operator Push Down > Examples > Example 2: TopN can be pushed down into Join (the sorting rule only depends on the columns in the outer table) | TopN and Limit Operator Push Down > Examples > Example 3: TopN cannot be pushed down before Join | TopN and Limit Operator Push Down > Examples > Example 4: Convert TopN to Limit`
- Source Line Ranges: `5-126`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `topn`, `limit`, `pushdown`, `execution-plan`, `optimizer`, `join`, `coprocessor`, `order-by`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0277_df93270fb3`
- Source ID: `tidb-docs-8.1:topn-limit-push-down.md#topn-and-limit-operator-push-down`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3c11d3f132428e4438367e1aca6d9dc4922fd066ee87640a488b67e50cb8b9e8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/topn-limit-push-down#topn-and-limit-operator-push-down
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/topn-limit-push-down.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how TiDB pushes down TopN or Limit in execution plans, including pushdown to coprocessors, pushdown around Join, cases where pushdown is not allowed, and when TopN is converted to Limit.
- Retrieval Keywords: TopN and Limit Operator Push Down, LIMIT clause, ORDER BY clause, TopN operator, Limit operator, Sort operator, predicate pushdown, execution plan tree, cop[tikv], Coprocessors in the storage layer, TableReader, TableFullScan, HashJoin, left outer join, inner join, outer table, inner table, sorting rule only depends on the columns in the outer table, TopN cannot be pushed down before Join, t.a+s.a, Convert TopN to Limit, keep order:true, keep order:false, offset:0, count:10, explain select * from t order by a limit 10, explain select * from t left join s on t.a = s.a order by t.a limit 10, explain select * from t join s on t.a = s.a order by t.id limit 10, explain select * from t left join s on t.a = s.a order by t.id limit 10, Optimization Rules and Blocklist for Expression Pushdown
- Follow-up Guidance: The source also states that this rule can be disabled by referring to Optimization Rules and Blocklist for Expression Pushdown.
- Classification Note: This is classified as performance because the content explains optimizer pushdown rules that reduce data transmission and calculation overhead in TiDB execution plans.

## Official Source Content

# TopN and Limit Operator Push Down

This document describes the implementation of TopN and Limit operator pushdown.

In the TiDB execution plan tree, the `LIMIT` clause in SQL corresponds to the Limit operator node, and the `ORDER BY` clause corresponds to the Sort operator node. The adjacent Limit operator and Sort operator are combined as the TopN operator node, which means that the top N records are returned according to a certain sorting rule. That is to say, a Limit operator is equivalent to a TopN operator node with a null sorting rule.

Similar to predicate pushdown, TopN and Limit are pushed down in the execution plan tree to a position as close to the data source as possible so that the required data is filtered at an early stage. In this way, the pushdown significantly reduces the overhead of data transmission and calculation.

To disable this rule, refer to [Optimization Rules and Blocklist for Expression Pushdown](https://docs.pingcap.com/tidb/stable/blocklist-control-plan).
## Examples

This section illustrates TopN pushdown through some examples.
### Example 1: Push down to the Coprocessors in the storage layer

```sql
create table t(id int primary key, a int not null);
explain select * from t order by a limit 10;
```

```
+----------------------------+----------+-----------+---------------+--------------------------------+
| id                         | estRows  | task      | access object | operator info                  |
+----------------------------+----------+-----------+---------------+--------------------------------+
| TopN_7                     | 10.00    | root      |               | test.t.a, offset:0, count:10   |
| └─TableReader_15           | 10.00    | root      |               | data:TopN_14                   |
|   └─TopN_14                | 10.00    | cop[tikv] |               | test.t.a, offset:0, count:10   |
|     └─TableFullScan_13     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo |
+----------------------------+----------+-----------+---------------+--------------------------------+
4 rows in set (0.00 sec)
```

In this query, the TopN operator node is pushed down to TiKV for data filtering, and each Coprocessor returns only 10 records to TiDB. After TiDB aggregates the data, the final filtering is performed.
### Example 2: TopN can be pushed down into Join (the sorting rule only depends on the columns in the outer table)

```sql
create table t(id int primary key, a int not null);
create table s(id int primary key, a int not null);
explain select * from t left join s on t.a = s.a order by t.a limit 10;
```

```
+----------------------------------+----------+-----------+---------------+-------------------------------------------------+
| id                               | estRows  | task      | access object | operator info                                   |
+----------------------------------+----------+-----------+---------------+-------------------------------------------------+
| TopN_12                          | 10.00    | root      |               | test.t.a, offset:0, count:10                    |
| └─HashJoin_17                    | 12.50    | root      |               | left outer join, equal:[eq(test.t.a, test.s.a)] |
|   ├─TopN_18(Build)               | 10.00    | root      |               | test.t.a, offset:0, count:10                    |
|   │ └─TableReader_26             | 10.00    | root      |               | data:TopN_25                                    |
|   │   └─TopN_25                  | 10.00    | cop[tikv] |               | test.t.a, offset:0, count:10                    |
|   │     └─TableFullScan_24       | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo                  |
|   └─TableReader_30(Probe)        | 10000.00 | root      |               | data:TableFullScan_29                           |
|     └─TableFullScan_29           | 10000.00 | cop[tikv] | table:s       | keep order:false, stats:pseudo                  |
+----------------------------------+----------+-----------+---------------+-------------------------------------------------+
8 rows in set (0.01 sec)
```

In this query, the sorting rule of the TopN operator only depends on the columns in the outer table `t`, so a calculation can be performed before pushing down TopN to Join, to reduce the calculation cost of the Join operation. Besides, TiDB also pushes TopN down to the storage layer.
### Example 3: TopN cannot be pushed down before Join

```sql
create table t(id int primary key, a int not null);
create table s(id int primary key, a int not null);
explain select * from t join s on t.a = s.a order by t.id limit 10;
```

```
+-------------------------------+----------+-----------+---------------+--------------------------------------------+
| id                            | estRows  | task      | access object | operator info                              |
+-------------------------------+----------+-----------+---------------+--------------------------------------------+
| TopN_12                       | 10.00    | root      |               | test.t.id, offset:0, count:10              |
| └─HashJoin_16                 | 12500.00 | root      |               | inner join, equal:[eq(test.t.a, test.s.a)] |
|   ├─TableReader_21(Build)     | 10000.00 | root      |               | data:TableFullScan_20                      |
|   │ └─TableFullScan_20        | 10000.00 | cop[tikv] | table:s       | keep order:false, stats:pseudo             |
|   └─TableReader_19(Probe)     | 10000.00 | root      |               | data:TableFullScan_18                      |
|     └─TableFullScan_18        | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo             |
+-------------------------------+----------+-----------+---------------+--------------------------------------------+
6 rows in set (0.00 sec)
```

TopN cannot be pushed down before `Inner Join`. Taking the query above as an example, if you get 100 records after Join, then you can have 10 records left after TopN. However, if TopN is performed first to get 10 records, only 5 records are left after Join. In such cases, the pushdown results in different results. 

Similarly, TopN can neither be pushed down to the inner table of Outer Join, nor can it be pushed down when its sorting rule is related to columns on multiple tables, such as `t.a+s.a`. Only when the sorting rule of TopN exclusively depends on columns on the outer table, can TopN be pushed down. 
### Example 4: Convert TopN to Limit

```sql
create table t(id int primary key, a int not null);
create table s(id int primary key, a int not null);
explain select * from t left join s on t.a = s.a order by t.id limit 10;
```

```
+----------------------------------+----------+-----------+---------------+-------------------------------------------------+
| id                               | estRows  | task      | access object | operator info                                   |
+----------------------------------+----------+-----------+---------------+-------------------------------------------------+
| TopN_12                          | 10.00    | root      |               | test.t.id, offset:0, count:10                   |
| └─HashJoin_17                    | 12.50    | root      |               | left outer join, equal:[eq(test.t.a, test.s.a)] |
|   ├─Limit_21(Build)              | 10.00    | root      |               | offset:0, count:10                              |
|   │ └─TableReader_31             | 10.00    | root      |               | data:Limit_30                                   |
|   │   └─Limit_30                 | 10.00    | cop[tikv] |               | offset:0, count:10                              |
|   │     └─TableFullScan_29       | 10.00    | cop[tikv] | table:t       | keep order:true, stats:pseudo                   |
|   └─TableReader_35(Probe)        | 10000.00 | root      |               | data:TableFullScan_34                           |
|     └─TableFullScan_34           | 10000.00 | cop[tikv] | table:s       | keep order:false, stats:pseudo                  |
+----------------------------------+----------+-----------+---------------+-------------------------------------------------+
8 rows in set (0.00 sec)

```

In the query above, TopN is first pushed to the outer table `t`. TopN needs to sort by `t.id`, which is the primary key and can be directly read in order  (`keep order: true`) without extra sorting in TopN. Therefore, TopN is simplified as Limit.
