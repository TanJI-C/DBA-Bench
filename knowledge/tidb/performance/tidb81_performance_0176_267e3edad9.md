# Reading execution plans with first-child-first traversal

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide > Understand execution plans > Read execution plans: first child first`
- Source Line Ranges: `398-488`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `execution-plans`, `plan-tree`, `operator-traversal`, `first-child-first`, `recursive-descent`, `joins`, `topn`, `aggregation`, `coprocessor`, `query-analysis`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0176_267e3edad9`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#read-execution-plans-first-child-first`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `131f1d40a1d4306dea57b9774d563d3c8cd0f1c1d16797312fbc8bf56f66a643`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#read-execution-plans-first-child-first
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when you need to interpret a TiDB EXPLAIN plan for a slow query by following the plan tree in first-child-first recursive descent order and understanding how operators consume child output.
- Retrieval Keywords: Read execution plans: first child first, first child first – recursive descent, execution plan, EXPLAIN, postorder traversal, Left Right Root, parent-child interaction, blocking vs. non-blocking operators, TopN, HashAgg, IndexLookup, IndexJoin, HashJoin_44, Projection_16, TopN_19, TopN_26, IndexReader_48, IndexRangeScan_47, TableReader_46, TableFullScan_45, StreamAgg_20, StreamAgg_9, Selection_19, TableFullScan_18, cop[tikv], ge(trips.start_date, le(trips.start_date, table:s, index:name(name)
- Follow-up Guidance: The chunk includes two EXPLAIN examples that show how to trace operator order from root to leaf and how pushed-down operators in cop[tikv] relate to data flow back to root operators.
- Classification Note: This is classified as performance for the SQL component because the official content explains how to analyze execution plans to diagnose slow SQL queries and understand operator traversal across TiDB and TiKV.

## Official Source Content

#### Read execution plans: first child first

To diagnose slow SQL queries, you need to understand how to read execution plans. The key principle is **"first child first – recursive descent"**. Each operator in the plan generates a set of rows, and the execution order determines how these rows flow through the plan tree.

The "first child first" rule means that an operator must retrieve rows from all its child operators before producing output. For example, a join operator requires rows from both its child operators to perform the join. The "recursive descent" rule means you analyze the plan from top to bottom, although actual data flows from bottom to top, as each operator depends on its children's output.

Consider these two important concepts when reading execution plans:

- Parent-child interaction: a parent operator calls its child operators sequentially but might cycle through them multiple times. For example, in an index lookup or nested loop join, the parent fetches a batch of rows from the first child, then retrieves zero or more rows from the second child. This process repeats until the first child's result set is fully processed.

- Blocking vs. non-blocking operators: operators can be either blocking or non-blocking:
    - Blocking operators, such as `TopN` and `HashAgg`, must create their entire result set before passing data to their parent.
    - Non-blocking operators, such as `IndexLookup` and `IndexJoin`, produce and pass rows incrementally as needed.

When reading an execution plan, start from the top and work downward. In the following example, the leaf node of the plan tree is `TableFullScan_18`, which performs a full table scan. The rows from this scan are consumed by the `Selection_19` operator, which filters the data based on `ge(trips.start_date, 2017-07-01 00:00:00.000000), le(trips.start_date, 2017-07-01 23:59:59.000000)`. Then, the group-by operator `StreamAgg_9` performs the final aggregation `COUNT(*)`.

These three operators (`TableFullScan_18`, `Selection_19`, and `StreamAgg_9`) are pushed down to TiKV (marked as `cop[tikv]`), enabling early filtering and aggregation in TiKV to reduce data transfer between TiKV and TiDB. Finally, `TableReader_21` reads the data from `StreamAgg_9`, and `StreamAgg_20` performs the final aggregation `count(*)`.

```sql
EXPLAIN SELECT COUNT(*) FROM trips WHERE start_date BETWEEN '2017-07-01 00:00:00' AND '2017-07-01 23:59:59';
```

```
+--------------------------+-------------+--------------+-------------------+----------------------------------------------------------------------------------------------------+
| id                       | estRows     | task         | access object     | operator info                                                                                      |
+--------------------------+-------------+--------------+-------------------+----------------------------------------------------------------------------------------------------+
| StreamAgg_20             | 1.00        | root         |                   | funcs:count(Column#13)->Column#11                                                                  |
| └─TableReader_21         | 1.00        | root         |                   | data:StreamAgg_9                                                                                   |
|   └─StreamAgg_9          | 1.00        | cop[tikv]    |                   | funcs:count(1)->Column#13                                                                          |
|     └─Selection_19       | 250.00      | cop[tikv]    |                   | ge(trips.start_date, 2017-07-01 00:00:00.000000), le(trips.start_date, 2017-07-01 23:59:59.000000) |
|       └─TableFullScan_18 | 10000.00    | cop[tikv]    | table:trips       | keep order:false, stats:pseudo                                                                     |
+--------------------------+-------------+--------------+-------------------+----------------------------------------------------------------------------------------------------+
5 rows in set (0.00 sec)
```

In the following example, start by examining `IndexRangeScan_47`, the first leaf node of the plan tree. The optimizer selects only the `name` and `id` columns from the `stars` table, which can be retrieved from the `name(name)` index. As a result, the root reader for `stars` is `IndexReader_48`, not `TableReader`.

The join between `stars` and `planets` is a hash join (`HashJoin_44`). The `planets` table is accessed using a full table scan (`TableFullScan_45`). After the join, `TopN_26` and `TopN_19` apply the `ORDER BY` and `LIMIT` clauses, respectively. The final operator, `Projection_16`, selects the final column `t5.name`.

```sql
EXPLAIN 
SELECT t5.name 
FROM (
    SELECT p.name, p.gravity, p.distance_from_sun 
    FROM universe.planets p 
    JOIN universe.stars s
        ON s.id = p.sun_id 
        AND s.name = 'Sun'
    ORDER BY p.distance_from_sun ASC 
    LIMIT 5
) t5
ORDER BY t5.gravity DESC 
LIMIT 3;
```

```
+-----------------------------------+----------+-----------+---------------------------+
| id                                | estRows  | task      | access object             |
+-----------------------------------+----------+-----------+---------------------------+
| Projection_16                     | 3.00     | root      |                           |
| └─TopN_19                         | 3.00     | root      |                           |
|   └─TopN_26                       | 5.00     | root      |                           |
|     └─HashJoin_44                 | 5.00     | root      |                           |
|       ├─IndexReader_48(Build)     | 1.00     | root      |                           |
|       │ └─IndexRangeScan_47       | 1.00     | cop[tikv] | table:s, index:name(name) |
|       └─TableReader_46(Probe)     | 10.00    | root      |                           |
|         └─TableFullScan_45        | 10.00    | cop[tikv] | table:p                   |
+-----------------------------------+----------+-----------+---------------------------+
```

The following figure illustrates the plan tree for the second execution plan:

![execution-plan-traverse](/media/sql-tuning/execution-plan-traverse.png)

The execution plan follows a top-to-bottom, first-child-first traversal, corresponding to a postorder traversal (Left, Right, Root) of the plan tree.

You can read this plan in the following order:

1. Start at the top with `Projection_16`.
2. Move to its child, `TopN_19`.
3. Continue to `TopN_26`.
4. Proceed to `HashJoin_44`.
5. For `HashJoin_44`, process its left (Build) child first:
    - `IndexReader_48`
    - `IndexRangeScan_47`
6. For `HashJoin_44`, process its right (Probe) child:
    - `TableReader_46`
    - `TableFullScan_45`

This traversal ensures that each operator's inputs are processed before the operator itself, enabling efficient query execution.
