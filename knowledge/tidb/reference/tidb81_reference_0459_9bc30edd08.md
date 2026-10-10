# Whole-query optimizer hints and execution controls

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Hints that take effect in the whole query | Optimizer Hints > Hints that take effect in the whole query > NO_INDEX_MERGE() | Optimizer Hints > Hints that take effect in the whole query > USE_TOJA(boolean_value) | Optimizer Hints > Hints that take effect in the whole query > MAX_EXECUTION_TIME(N) | Optimizer Hints > Hints that take effect in the whole query > MEMORY_QUOTA(N) | Optimizer Hints > Hints that take effect in the whole query > READ_CONSISTENT_REPLICA() | Optimizer Hints > Hints that take effect in the whole query > IGNORE_PLAN_CACHE() | Optimizer Hints > Hints that take effect in the whole query > STRAIGHT_JOIN() | Optimizer Hints > Hints that take effect in the whole query > NTH_PLAN(N)`
- Source Line Ranges: `722-849`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `optimizer-hints`, `whole-query`, `index-merge`, `subquery-rewrite`, `execution-timeout`, `memory-quota`, `replica-read`, `plan-cache`, `join-order`, `physical-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0459_9bc30edd08`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#hints-that-take-effect-in-the-whole-query`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1081f03cfc2bbea36f2ebb35f8eda3603202a888d8b6c82db6999dbef0dbb15d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#hints-that-take-effect-in-the-whole-query
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when you need whole-query optimizer hint behavior, placement rules after the first `SELECT`/`UPDATE`/`DELETE`, and exact meanings of execution-control and plan-selection hints.
- Retrieval Keywords: Hints that take effect in the whole query, NO_INDEX_MERGE(), USE_TOJA(TRUE), USE_TOJA(FALSE), MAX_EXECUTION_TIME(N), MEMORY_QUOTA(N), READ_CONSISTENT_REPLICA(), IGNORE_PLAN_CACHE(), STRAIGHT_JOIN(), NTH_PLAN(N), tidb_enable_index_merge, tidb_opt_insubq_to_join_and_agg, global.max_execution_time, tidb_mem_quota_query, tidb_replica_read, prepare-plan-cache
- Follow-up Guidance: The source also records priority and scope notes such as `NO_INDEX_MERGE` over `USE_INDEX_MERGE`, `STRAIGHT_JOIN` over `LEADING`, and that `NTH_PLAN(N)` does not take effect when the cascades planner is enabled.
- Classification Note: This is reference content because it enumerates whole-query hints, their exact syntax and examples, and related system-variable or planner-scope notes from the official documentation.

## Official Source Content

## Hints that take effect in the whole query

This category of hints can only follow behind the **first** `SELECT`, `UPDATE` or `DELETE` keyword, which is equivalent to modifying the value of the specified system variable when this query is executed. The priority of the hint is higher than that of existing system variables.

> **Note:**
>
> This category of hints also has an optional hidden variable `@QB_NAME`, but the hint takes effect in the whole query even if you specify the variable.
### NO_INDEX_MERGE()

The `NO_INDEX_MERGE()` hint disables the index merge feature of the optimizer.

For example, the following query will not use index merge:

```sql
select /*+ NO_INDEX_MERGE() */ * from t where t.a > 0 or t.b > 0;
```

In addition to this hint, setting the `tidb_enable_index_merge` system variable also controls whether to enable this feature.

> **Note:**
>
> - `NO_INDEX_MERGE` has a higher priority over `USE_INDEX_MERGE`. When both hints are used, `USE_INDEX_MERGE` does not take effect.
> - For a subquery, `NO_INDEX_MERGE` only takes effect when it is placed at the outermost level of the subquery.
### USE_TOJA(boolean_value)

The `boolean_value` parameter can be `TRUE` or `FALSE`. The `USE_TOJA(TRUE)` hint enables the optimizer to convert an `in` condition (containing a sub-query) to join and aggregation operations. Comparatively, the `USE_TOJA(FALSE)` hint disables this feature.

For example, the following query will convert `in (select t2.a from t2) subq` to corresponding join and aggregation operations:

```sql
select /*+ USE_TOJA(TRUE) */ t1.a, t1.b from t1 where t1.a in (select t2.a from t2) subq;
```

In addition to this hint, setting the `tidb_opt_insubq_to_join_and_agg` system variable also controls whether to enable this feature.
### MAX_EXECUTION_TIME(N)

The `MAX_EXECUTION_TIME(N)` hint places a limit `N` (a timeout value in milliseconds) on how long a statement is permitted to execute before the server terminates it. In the following hint, `MAX_EXECUTION_TIME(1000)` means that the timeout is 1000 milliseconds (that is, 1 second):

```sql
select /*+ MAX_EXECUTION_TIME(1000) */ * from t1 inner join t2 where t1.id = t2.id;
```

In addition to this hint, the `global.max_execution_time` system variable can also limit the execution time of a statement.
### MEMORY_QUOTA(N)

The `MEMORY_QUOTA(N)` hint places a limit `N` (a threshold value in MB or GB) on how much memory a statement is permitted to use. When a statement's memory usage exceeds this limit, TiDB produces a log message based on the statement's over-limit behavior or just terminates it.

In the following hint, `MEMORY_QUOTA(1024 MB)` means that the memory usage is limited to 1024 MB:

```sql
select /*+ MEMORY_QUOTA(1024 MB) */ * from t;
```

In addition to this hint, the [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query) system variable can also limit the memory usage of a statement.
### READ_CONSISTENT_REPLICA()

The `READ_CONSISTENT_REPLICA()` hint enables the feature of reading consistent data from the TiKV follower node. For example:

```sql
select /*+ READ_CONSISTENT_REPLICA() */ * from t;
```

In addition to this hint, setting the `tidb_replica_read` environment variable to `'follower'` or `'leader'` also controls whether to enable this feature.
### IGNORE_PLAN_CACHE()

The `IGNORE_PLAN_CACHE()` hint reminds the optimizer not to use the Plan Cache when handling the current `prepare` statement.

This hint is used to temporarily disable the Plan Cache for a certain type of queries when [prepare-plan-cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache) is enabled.

In the following example, the Plan Cache is forcibly disabled when executing the `prepare` statement.

```sql
prepare stmt from 'select  /*+ IGNORE_PLAN_CACHE() */ * from t where t.id = ?';
```
### STRAIGHT_JOIN()

The `STRAIGHT_JOIN()` hint reminds the optimizer to join tables in the order of table names in the `FROM` clause when generating the join plan.

```sql
SELECT /*+ STRAIGHT_JOIN() */ * FROM t t1, t t2 WHERE t1.a = t2.a;
```

> **Note:**
>
> - `STRAIGHT_JOIN` has higher priority over `LEADING`. When both hints are used, `LEADING` does not take effect.
> - It is recommended to use the `LEADING` hint, which is more general than the `STRAIGHT_JOIN` hint.
### NTH_PLAN(N)

The `NTH_PLAN(N)` hint reminds the optimizer to select the `N`th physical plan found during the physical optimization. `N` must be a positive integer.

If the specified `N` is beyond the search range of the physical optimization, TiDB will return a warning and select the optimal physical plan based on the strategy that ignores this hint.

This hint does not take effect when the cascades planner is enabled.

In the following example, the optimizer is forced to select the third physical plan found during the physical optimization:

```sql
SELECT /*+ NTH_PLAN(3) */ count(*) from t where a > 5;
```

> **Note:**
>
> `NTH_PLAN(N)` is mainly used for testing, and its compatibility is not guaranteed in later versions. Use this hint **with caution**.
