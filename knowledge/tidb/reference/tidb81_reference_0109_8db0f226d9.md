# Additional join types, implicit joins, algorithms, and join order

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-join-tables.md`
- Source Title: `Multi-table Join Queries`
- Source Heading Path: `Multi-table Join Queries > Join types > RIGHT OUTER JOIN | Multi-table Join Queries > Join types > CROSS JOIN | Multi-table Join Queries > Join types > LEFT SEMI JOIN | Multi-table Join Queries > Implicit join | Multi-table Join Queries > Join related algorithms | Multi-table Join Queries > Join orders | Multi-table Join Queries > See also`
- Source Line Ranges: `190-256`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `right outer join`, `cross join`, `semi join`, `implicit join`, `hash join`, `merge join`, `index join`, `optimizer hints`, `explain`, `straight_join`, `join reorder`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0109_8db0f226d9`
- Source ID: `tidb-docs-8.1:develop/dev-guide-join-tables.md#right-outer-join`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cd56d549f209cd6339e9041c135ac86f8f10469a6ae3ebd8084aa75e3255f5bb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-join-tables#right-outer-join
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-join-tables.md

## Retrieval Guidance

- Use When: Use this chunk when you need join reference material about additional join types, implicit joins, join algorithms, optimizer hints, `EXPLAIN`, or controlling join order with `STRAIGHT_JOIN`.
- Retrieval Keywords: RIGHT OUTER JOIN, CROSS JOIN, LEFT SEMI JOIN, implicit join, FROM t1, t2, WHERE t1.id = t2.id, Index Join, Hash Join, Merge Join, EXPLAIN, Optimizer Hints, HASH_JOIN(b, r), MERGE_JOIN, INL_JOIN, INL_HASH_JOIN, join reorder, STRAIGHT_JOIN, semi join, subquery-related optimizations
- Follow-up Guidance: It points to related material on `Explain Statements That Use Joins` and `Introduction to Join Reorder`, and includes an `EXPLAIN SELECT /*+ HASH_JOIN(b, r) */ ...` example plus a `STRAIGHT_JOIN` example.
- Classification Note: This is reference content because it summarizes supported join forms, explains optimizer-selected join algorithms and hints, and describes join order behavior and syntax.

## Official Source Content

### RIGHT OUTER JOIN

A right outer join returns all the records in the right table and the values ​​in the left table that match the join condition. If there is no matching value, it is filled with `NULL`.

![Right Outer Join](/media/develop/right-outer-join.png)
### CROSS JOIN

When the join condition is constant, the inner join between the two tables is called a [cross join](https://en.wikipedia.org/wiki/Join_(SQL)#Cross_join). A cross join joins every record of the left table to all the records of the right table. If the number of records in the left table is `m` and the number of records in the right table is `n`, then `m \* n` records will be generated in the result set.
### LEFT SEMI JOIN

TiDB does not support `LEFT SEMI JOIN table_name` at the SQL syntax level. But at the execution plan level, [subquery-related optimizations](https://docs.pingcap.com/tidb/stable/subquery-optimization) will use `semi join` as the default join method for rewritten equivalent JOIN queries.
## Implicit join

Before the `JOIN` statement that explicitly declared a join was added to the SQL standard, it was possible to join two or more tables in a SQL statement using the `FROM t1, t2` clause, and specify the conditions for the join using the `WHERE t1.id = t2.id` clause. You can understand it as an implicit join, which uses the inner join to join tables.
## Join related algorithms

TiDB supports the following general table join algorithms.

- [Index Join](https://docs.pingcap.com/tidb/stable/explain-joins#index-join)
- [Hash Join](https://docs.pingcap.com/tidb/stable/explain-joins#hash-join)
- [Merge Join](https://docs.pingcap.com/tidb/stable/explain-joins#merge-join)

The optimizer selects an appropriate join algorithm to execute based on the factors such as the data volume in the joined table. You can see which algorithm the query uses for Join by using the `EXPLAIN` statement.

If the optimizer of TiDB does not execute according to the optimal join algorithm, you can use [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints) to force TiDB to use a better join algorithm.

For example, assuming the example for the left join query above executes faster using the Hash Join algorithm, which is not chosen by the optimizer, you can append the hint `/*+ HASH_JOIN(b, r) */` after the `SELECT` keyword. Note that If the table has an alias, use the alias in the hint.

```sql
EXPLAIN SELECT /*+ HASH_JOIN(b, r) */ b.id AS book_id, ANY_VALUE(b.title) AS book_title, AVG(r.score) AS average_score
FROM books b
LEFT JOIN ratings r ON b.id = r.book_id
GROUP BY b.id
ORDER BY b.published_at DESC
LIMIT 10;
```

Hints related to join algorithms:

- [MERGE_JOIN(t1_name [, tl_name ...])](/optimizer-hints.md#merge_joint1_name--tl_name-)
- [INL_JOIN(t1_name [, tl_name ...])](/optimizer-hints.md#inl_joint1_name--tl_name-)
- [INL_HASH_JOIN(t1_name [, tl_name ...])](/optimizer-hints.md#inl_hash_join)
- [HASH_JOIN(t1_name [, tl_name ...])](/optimizer-hints.md#hash_joint1_name--tl_name-)
## Join orders

In real business scenarios, join statements of multiple tables are very common. The execution efficiency of join is related to the order of each table in join. TiDB uses the Join Reorder algorithm to determine the order in which multiple tables are joined.

If the join order selected by the optimizer is not optimal as expected, you can use `STRAIGHT_JOIN` to enforce TiDB to join queries in the order of the tables used in the `FROM` clause.

```sql
EXPLAIN SELECT *
FROM authors a STRAIGHT_JOIN book_authors ba STRAIGHT_JOIN books b
WHERE b.id = ba.book_id AND ba.author_id = a.id;
```

For more information about the implementation details and limitations of this Join Reorder algorithm, see [Introduction to Join Reorder Algorithm](https://docs.pingcap.com/tidb/stable/join-reorder).
## See also

- [Explain Statements That Use Joins](https://docs.pingcap.com/tidb/stable/explain-joins)
- [Introduction to Join Reorder](https://docs.pingcap.com/tidb/stable/join-reorder)
