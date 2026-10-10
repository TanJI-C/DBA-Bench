# Subquery rewrite overview for ALL and ANY comparisons

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/subquery-optimization.md`
- Source Title: `Subquery Related Optimizations`
- Source Heading Path: `Subquery Related Optimizations | Subquery Related Optimizations > `... < ALL (SELECT ... FROM ...)` or `... > ANY (SELECT ... FROM ...)` | Subquery Related Optimizations > `... != ANY (SELECT ... FROM ...)` | Subquery Related Optimizations > `... = ALL (SELECT ... FROM ...)``
- Source Line Ranges: `5-40`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `subquery`, `optimization`, `rewrite`, `semi-join`, `all`, `any`, `max`, `min`, `distinct`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0189_c809de1740`
- Source ID: `tidb-docs-8.1:subquery-optimization.md#subquery-related-optimizations`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `50922045a2180eef738d92a39b60134eaa2e3f57fc55b054a60b6dd15060516b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/subquery-optimization#subquery-related-optimizations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/subquery-optimization.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiDB logically rewrites non-correlated subqueries with ALL or ANY comparison operators and what SQL forms are produced.
- Retrieval Keywords: subquery related optimizations, semi join, correlated subquery, correlated column, t.id < all (select s.id from s), t.id > any (select s.id from s), t.id != any (select s.id from s), t.id = all (select s.id from s), MAX(EXPR), MIN(EXPR), sum(s.id is null), count(distinct s.id) as cnt_distinct, ALL and ANY rewrite, distinct values in subquery
- Follow-up Guidance: For optimizations about correlated subquery, the content points to Decorrelation of correlated subquery.
- Classification Note: This is classified as performance because the official content describes logical rewrite rules that TiDB applies to special subqueries to get better performance.

## Official Source Content

# Subquery Related Optimizations

This article mainly introduces subquery related optimizations.

Subqueries usually appear in the following situations:

- `NOT IN (SELECT ... FROM ...)`
- `NOT EXISTS (SELECT ... FROM ...)`
- `IN (SELECT ... FROM ..)`
- `EXISTS (SELECT ... FROM ...)`
- `... >/>=/</<=/=/!= (SELECT ... FROM ...)`

Sometimes a subquery contains non-subquery columns, such as `select * from t where t.a in (select * from t2 where t.b=t2.b)`. The `t.b` column in the subquery does not belong to the subquery, it is introduced from the outside of the subquery. This kind of subquery is usually called a "correlated subquery", and the externally introduced column is called a "correlated column". For optimizations about correlated subquery, see [Decorrelation of correlated subquery](https://docs.pingcap.com/tidb/stable/correlated-subquery-optimization). This article focuses on subqueries that do not involve correlated columns.

By default, subqueries use `semi join` mentioned in [Understanding TiDB Execution Plan](https://docs.pingcap.com/tidb/stable/explain-overview) as the execution method. For some special subqueries, TiDB do some logical rewrite to get better performance.
## `... < ALL (SELECT ... FROM ...)` or `... > ANY (SELECT ... FROM ...)`

In this case, `ALL` and `ANY` can be replaced by `MAX` and `MIN`. When the table is empty, the result of `MAX(EXPR)` and `MIN(EXPR)` is NULL. It works the same when the result of `EXPR` contains `NULL`. Whether the result of `EXPR` contains `NULL` may affect the final result of the expression, so the complete rewrite is given in the following form:

- `t.id < all (select s.id from s)` is rewritten as `t.id < min(s.id) and if(sum(s.id is null) != 0, null, true)`
- `t.id > any (select s.id from s)` is rewritten as `t.id > max(s.id) or if(sum(s.id is null) != 0, null, false)`
## `... != ANY (SELECT ... FROM ...)`

In this case, if all the values from the subquery are distinct, it is enough to compare the query with them. If the number of different values in the subquery is more than one, then there must be inequality. Therefore, such subqueries can be rewritten as follows:

- `select * from t where t.id != any (select s.id from s)` is rewritten as `select t.* from t, (select s.id, count(distinct s.id) as cnt_distinct from s) where (t.id != s.id or cnt_distinct > 1)`
## `... = ALL (SELECT ... FROM ...)`

In this case, when the number of different values in the subquery is more than one, then the result of this expression must be false. Therefore, such subquery is rewritten into the following form in TiDB:

- `select * from t where t.id = all (select s.id from s)` is rewritten as `select t.* from t, (select s.id, count(distinct s.id) as cnt_distinct from s ) where (t.id = s.id and cnt_distinct <= 1)`
