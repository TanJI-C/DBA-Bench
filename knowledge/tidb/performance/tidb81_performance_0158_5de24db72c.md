# SQL logical optimization overview and rewrite topics

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-logical-optimization.md`
- Source Title: `SQL Logical Optimization`
- Source Heading Path: `SQL Logical Optimization`
- Source Line Ranges: `5-20`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `logical-optimization`, `query-plan`, `query-rewrite`, `subquery-optimization`, `column-pruning`, `decorrelation`, `predicate-pushdown`, `partition-pruning`, `topn`, `limit`, `join-reorder`, `window-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0158_5de24db72c`
- Source ID: `tidb-docs-8.1:sql-logical-optimization.md#sql-logical-optimization`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1d8f8b66c85db2922271b49a922cbe0aa99e1db7de1293f3128ec4858b09f5ca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-logical-optimization#sql-logical-optimization
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-logical-optimization.md

## Retrieval Guidance

- Use When: Use this chunk when you need an overview of TiDB SQL logical optimization and the rewrite topics it covers.
- Retrieval Keywords: SQL Logical Optimization, logical rewrites, final query plan, IN sub-query, Subquery Related Optimizations, Column Pruning, Decorrelation of Correlated Subquery, Eliminate Max/Min, Predicates Push Down, Partition Pruning, TopN and Limit Operator Push Down, Join Reorder, Derive TopN or Limit from Window Functions
- Follow-up Guidance: See the linked sections for details on each rewrite topic.
- Classification Note: The content is an overview chapter that introduces TiDB logical query rewrites and lists the optimization topics covered in the chapter.

## Official Source Content

# SQL Logical Optimization

This chapter explains some key logic rewrites to help you understand how TiDB generates the final query plan. For example, when you execute the `select * from t where t.a in (select t1.a from t1 where t1.b=t.b)` query in TiDB, you will find that the `IN` sub-query `t.a in (select t1.a from t1 where t1.b=t.b)` does not exist because TiDB has made some rewrites here.

This chapter introduces the following key rewrites:

- [Subquery Related Optimizations](https://docs.pingcap.com/tidb/stable/subquery-optimization)
- [Column Pruning](https://docs.pingcap.com/tidb/stable/column-pruning)
- [Decorrelation of Correlated Subquery](https://docs.pingcap.com/tidb/stable/correlated-subquery-optimization)
- [Eliminate Max/Min](https://docs.pingcap.com/tidb/stable/max-min-eliminate)
- [Predicates Push Down](https://docs.pingcap.com/tidb/stable/predicate-push-down)
- [Partition Pruning](https://docs.pingcap.com/tidb/stable/partition-pruning)
- [TopN and Limit Operator Push Down](https://docs.pingcap.com/tidb/stable/topn-limit-push-down)
- [Join Reorder](https://docs.pingcap.com/tidb/stable/join-reorder)
- [Derive TopN or Limit from Window Functions](https://docs.pingcap.com/tidb/stable/derive-topn-from-window)
