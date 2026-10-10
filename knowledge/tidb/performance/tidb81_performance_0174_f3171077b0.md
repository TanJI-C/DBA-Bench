# Execution plan stages and optimization workflow

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide > Understand execution plans | A Practical Guide for SQL Tuning > SQL tuning guide > Understand execution plans > How TiDB builds an execution plan | A Practical Guide for SQL Tuning > SQL tuning guide > Understand execution plans > How TiDB builds an execution plan > 1. Pre-processing | A Practical Guide for SQL Tuning > SQL tuning guide > Understand execution plans > How TiDB builds an execution plan > 2. Logical transformation | A Practical Guide for SQL Tuning > SQL tuning guide > Understand execution plans > How TiDB builds an execution plan > 3. Cost-based optimization`
- Source Line Ranges: `268-323`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiflash`, `sql`
- Topic Tags: `execution plans`, `pre-processing`, `point get`, `batch point get`, `logical optimization`, `cost-based optimization`, `cop tasks`, `mpp tasks`, `query processing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0174_f3171077b0`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#understand-execution-plans`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9a85ad35f3d10e176dc5588b60ac9debdea8d51c84f37dd14fa747e262842bde`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#understand-execution-plans
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how TiDB builds an execution plan, including pre-processing with Point_Get or Batch_Point_Get, logical transformation, and cost-based optimization across TiDB, TiKV, and TiFlash.
- Retrieval Keywords: execution plan, How TiDB builds an execution plan, pre-processing, logical transformation, cost-based optimization, Point_Get, Batch_Point_Get, EXPLAIN SELECT id, name FROM emp WHERE id = 901, column pruning, partition pruning, join reordering, SQL Logical Optimization, SQL Physical Optimization, index scans, full table scans, TiKV, TiFlash, HashAgg, StreamAgg, HashJoin, MergeJoin, IndexJoin, Root tasks, Cop tasks, MPP tasks, physical optimization, push down expressions, push down operators
- Follow-up Guidance: The source further explains that if a query qualifies for Point_Get or Batch_Point_Get, TiDB skips logical transformation and cost-based optimization because direct key lookup is the most efficient access method.
- Classification Note: This is classified as performance for TiDB because the official content describes optimizer stages, plan selection, and task distribution that determine SQL execution efficiency.

## Official Source Content

### Understand execution plans

An execution plan details the steps that TiDB will follow to execute a SQL query. This section explains how TiDB builds an execution plan and how to generate, display, and interpret execution plans.
#### How TiDB builds an execution plan

A SQL statement undergoes three main optimization stages in the TiDB optimizer:

1. [Pre-processing](#1-pre-processing)
2. [Logical transformation](#2-logical-transformation)
3. [Cost-based optimization](#3-cost-based-optimization)
##### 1. Pre-processing

During pre-processing, TiDB determines whether the SQL statement can be executed using [`Point_Get`](https://docs.pingcap.com/tidb/stable/explain-indexes#point_get-and-batch_point_get) or [`Batch_Point_Get`](https://docs.pingcap.com/tidb/stable/explain-indexes#point_get-and-batch_point_get). These operations use a primary or unique key to read directly from TiKV through an exact key lookup. If a plan qualifies for `Point_Get` or `Batch_Point_Get`, the optimizer skips the logical transformation and cost-based optimization steps because direct key lookup is the most efficient way to access the row.

The following is an example of a `Point_Get` query:

```sql
EXPLAIN SELECT id, name FROM emp WHERE id = 901;
```

```
+-------------+---------+------+---------------+---------------+
| id          | estRows | task | access object | operator info |
+-------------+---------+------+---------------+---------------+
| Point_Get_1 | 1.00    | root | table:emp     | handle:901    |
+-------------+---------+------+---------------+---------------+
```
##### 2. Logical transformation

During logical transformation, TiDB optimizes SQL statements based on the `SELECT` list, `WHERE` predicates, and other conditions. It generates a logical execution plan to annotate and rewrite the query. This logical plan is used in the next stage, cost-based optimization. The transformation applies rule-based optimizations such as column pruning, partition pruning, and join reordering. Because this process is rule-based and automatic, manual adjustments are usually unnecessary.

For more information, see [SQL Logical Optimization](https://docs.pingcap.com/tidb/stable/sql-logical-optimization).
##### 3. Cost-based optimization

The TiDB optimizer uses statistics to estimate the number of rows processed in each step of a SQL statement and assigns a cost to each step. During cost-based optimization, the optimizer evaluates all possible plan choices, including index accesses and join methods, and calculates the total cost for each plan. The optimizer then selects the execution plan with the minimal total cost.

The following figure illustrates various data access paths and row set operations considered during cost-based optimization. For data retrieval paths, the optimizer determines the most efficient method between index scans and full table scans, and decides whether to retrieve data from row-based TiKV storage or columnar TiFlash storage.

The optimizer also evaluates operations that manipulate row sets, such as aggregation, join, and sorting. For example, the aggregation operator might use either `HashAgg` or `StreamAgg`, while the join method can select from `HashJoin`, `MergeJoin`, or `IndexJoin`.

Additionally, the physical optimization phase includes pushing down expressions and operators to the physical storage engines. The physical plan is distributed to different components based on the underlying storage engines as follows:

- Root tasks are executed on the TiDB server.
- Cop (Coprocessor) tasks are executed on TiKV.
- MPP tasks are executed on TiFlash.

This distribution enables cross-component collaboration for efficient query processing.

![cost-based-optimization](/media/sql-tuning/cost-based-optimization.png)

For more information, see [SQL Physical Optimization](https://docs.pingcap.com/tidb/stable/sql-physical-optimization).
