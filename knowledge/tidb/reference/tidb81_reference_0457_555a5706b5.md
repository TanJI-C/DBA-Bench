# Query block and global hints for join order, CTE merge, and views

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Hints that take effect in query blocks > LEADING(t1_name [, tl_name ...]) | Optimizer Hints > Hints that take effect in query blocks > MERGE() | Optimizer Hints > Hints that take effect globally`
- Source Line Ranges: `559-626`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `optimizer-hints`, `join-order`, `leading-hint`, `cte`, `view-hints`, `query-blocks`, `global-hints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0457_555a5706b5`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#leading-t1-name-tl-name`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fbd1a62890019cb02e4f57becebab0f207a0cee20bbd86c72d090c3a78a6753a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#leading-t1-name-tl-name
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when looking for optimizer hints that control multi-table join order with `LEADING`, disable CTE materialization with `MERGE()` for non-recursive CTE, or apply global hints inside views by combining `QB_NAME` with `ViewName@QueryBlockName`.
- Retrieval Keywords: LEADING, MERGE(), QB_NAME, ViewName@QueryBlockName, show warnings, We can only use one leading hint at most, join order, multi-table joins, outer join, Cartesian product, non-recursive CTE, materialization, views, global hint, STRAIGHT_JOIN
- Follow-up Guidance: The content says that when `LEADING` does not take effect, a warning is generated and `SHOW WARNINGS` can be executed to learn why the hint fails to take effect.
- Classification Note: This is a SQL optimizer hint reference section because it describes query block and global hints, their valid and invalid situations, and their behavior in joins, CTEs, and views.

## Official Source Content

### LEADING(t1_name [, tl_name ...])

The `LEADING(t1_name [, tl_name ...])` hint reminds the optimizer that, when generating the execution plan, to determine the order of multi-table joins according to the order of table names specified in the hint. For example:

```sql
SELECT /*+ LEADING(t1, t2) */ * FROM t1, t2, t3 WHERE t1.id = t2.id and t2.id = t3.id;
```

In the above query with multi-table joins, the order of joins is determined by the order of table names specified in the `LEADING()` hint. The optimizer will first join `t1` and `t2` and then join the result with `t3`. This hint is more general than [`STRAIGHT_JOIN`](#straight_join).

The `LEADING` hint does not take effect in the following situations:

+ Multiple `LEADING` hints are specified.
+ The table name specified in the `LEADING` hint does not exist.
+ A duplicated table name is specified in the `LEADING` hint.
+ The optimizer cannot perform join operations according to the order as specified by the `LEADING` hint.
+ The `straight_join()` hint already exists.
+ The query contains an outer join together with the Cartesian product.

In the preceding situations, a warning is generated.

```sql
-- Multiple `LEADING` hints are specified.
SELECT /*+ LEADING(t1, t2) LEADING(t3) */ * FROM t1, t2, t3 WHERE t1.id = t2.id and t2.id = t3.id;

-- To learn why the `LEADING` hint fails to take effect, execute `show warnings`.
SHOW WARNINGS;
```

```sql
+---------+------+-------------------------------------------------------------------------------------------------------------------+
| Level   | Code | Message                                                                                                           |
+---------+------+-------------------------------------------------------------------------------------------------------------------+
| Warning | 1815 | We can only use one leading hint at most, when multiple leading hints are used, all leading hints will be invalid |
+---------+------+-------------------------------------------------------------------------------------------------------------------+
```

> **Note:**
>
> If the query statement includes an outer join, in the hint you can specify only the tables whose join order can be swapped. If there is a table in the hint whose join order cannot be swapped, the hint will be invalid. For example, in `SELECT * FROM t1 LEFT JOIN (t2 JOIN t3 JOIN t4) ON t1.a = t2.a;`, if you want to control the join order of `t2`, `t3`, and `t4` tables, you cannot specify `t1` in the `LEADING` hint.
### MERGE()

Using the `MERGE()` hint in queries with common table expressions (CTE) can disable the materialization of the subqueries and expand the subquery inlines into CTE. This hint is only applicable to non-recursive CTE. In some scenarios, using `MERGE()` brings higher execution efficiency than the default behavior of allocating a temporary space. For example, pushing down query conditions or in nesting CTE queries:

```sql
-- Uses the hint to push down the predicate of the outer query.
WITH CTE AS (SELECT /*+ MERGE() */ * FROM tc WHERE tc.a < 60) SELECT * FROM CTE WHERE CTE.a < 18;

-- Uses the hint in a nested CTE query to expand a CTE inline into the outer query.
WITH CTE1 AS (SELECT * FROM t1), CTE2 AS (WITH CTE3 AS (SELECT /*+ MERGE() */ * FROM t2), CTE4 AS (SELECT * FROM t3) SELECT * FROM CTE3, CTE4) SELECT * FROM CTE1, CTE2;
```

> **Note:**
>
> `MERGE()` is only applicable to simple CTE queries. It is not applicable in the following situations:
>
> - [Recursive CTE](https://docs.pingcap.com/tidb/stable/dev-guide-use-common-table-expression#recursive-cte)
> - Subqueries with inlines that cannot be expanded, such as aggregate operators, window functions, and `DISTINCT`.
>
> When the number of CTE references is too high, the query performance might be lower than the default materialization behavior.
## Hints that take effect globally

The global hint works in [views](https://docs.pingcap.com/tidb/stable/views). When specified as a global hint, the hint defined in a query can take effect inside the view. To specify a global hint, first use the `QB_NAME` hint to define a query block name, and then add the target hints in the form of `ViewName@QueryBlockName`.
