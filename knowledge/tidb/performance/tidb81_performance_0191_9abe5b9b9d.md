# EXISTS and comparison subquery pre-evaluation and semi-join rewrite

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/subquery-optimization.md`
- Source Title: `Subquery Related Optimizations`
- Source Heading Path: `Subquery Related Optimizations > `EXISTS` subquery and `... >/>=/</<=/=/!= (SELECT ... FROM ...)``
- Source Line Ranges: `68-96`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `subquery`, `exists`, `comparison`, `optimization`, `pre-evaluation`, `semi-join`, `hash-join`, `index-join`, `optimizer-hint`, `explain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0191_9abe5b9b9d`
- Source ID: `tidb-docs-8.1:subquery-optimization.md#exists-subquery-and-select-from`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `23538be259f741933260678baba6ce24fbf26c2f520d9851a9a4e78f6cd1d230`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/subquery-optimization#exists-subquery-and-select-from
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/subquery-optimization.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB behavior that pre-evaluates non-correlated EXISTS or comparison subqueries during optimization, or for SEMI_JOIN_REWRITE and its effect on plan choices.
- Retrieval Keywords: EXISTS subquery, ... >/>=/</<=/=/!= (SELECT ... FROM ...), non-correlated subquery, evaluates it in advance in the optimization stage, result set, SEMI_JOIN_REWRITE, optimizer hint, hash join, index join, semi-join query, explain select * from t1 where exists (select * from t2), TableReader_12, TableFullScan_11
- Follow-up Guidance: The content says that using SEMI_JOIN_REWRITE() lets the optimizer extend the selection range to select a better execution plan.
- Classification Note: This is classified as performance because the official content focuses on optimizer-stage evaluation and semi-join rewrite choices that affect execution speed and plan selection.

## Official Source Content

## `EXISTS` subquery and `... >/>=/</<=/=/!= (SELECT ... FROM ...)`

At present, for a subquery in such scenarios, if the subquery is not a correlated subquery, TiDB evaluates it in advance in the optimization stage, and directly replaces it with a result set. As shown in the figure below, the `EXISTS` subquery is evaluated to `TRUE` in the optimization stage in advance, so it does not show in the final execution result.

```sql
create table t1(a int);
create table t2(a int);
insert into t2 values(1);
explain select * from t1 where exists (select * from t2);
```

```sql
+------------------------+----------+-----------+---------------+--------------------------------+
| id                     | estRows  | task      | access object | operator info                  |
+------------------------+----------+-----------+---------------+--------------------------------+
| TableReader_12         | 10000.00 | root      |               | data:TableFullScan_11          |
| └─TableFullScan_11     | 10000.00 | cop[tikv] | table:t1      | keep order:false, stats:pseudo |
+------------------------+----------+-----------+---------------+--------------------------------+
```

In the preceding optimization, the optimizer automatically optimizes the statement execution. In addition, you can also add the [`SEMI_JOIN_REWRITE`](https://docs.pingcap.com/tidb/stable/optimizer-hints#semi_join_rewrite) hint to further rewrite the statement.

If this hint is not used to rewrite the query, when the hash join is selected in the execution plan, the semi-join query can only use the subquery to build a hash table. In this case, when the result of the subquery is bigger than that of the outer query, the execution speed might be slower than expected.

Similarly, when the index join is selected in the execution plan, the semi-join query can only use the outer query as the driving table. In this case, when the result of the subquery is smaller than that of the outer query, the execution speed might be slower than expected.

When `SEMI_JOIN_REWRITE()` is used to rewrite the query, the optimizer can extend the selection range to select a better execution plan.
