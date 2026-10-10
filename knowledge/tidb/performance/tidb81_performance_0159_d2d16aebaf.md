# Non-prepared plan cache overview, principle, setup, and example

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-non-prepared-plan-cache.md`
- Source Title: `SQL Non-Prepared Execution Plan Cache`
- Source Heading Path: `SQL Non-Prepared Execution Plan Cache | SQL Non-Prepared Execution Plan Cache > Principle | SQL Non-Prepared Execution Plan Cache > Usage | SQL Non-Prepared Execution Plan Cache > Example`
- Source Line Ranges: `5-70`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `plan-cache`, `non-prepared`, `session-level`, `parameterization`, `system-variables`, `lru`, `memory-overhead`, `cpu-overhead`, `cache-hit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0159_d2d16aebaf`
- Source ID: `tidb-docs-8.1:sql-non-prepared-plan-cache.md#sql-non-prepared-execution-plan-cache`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f06fd6bba12f0965307c6f64fb3cef4d78c0cbb53e09d283cd1f520e8e2e692b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache#sql-non-prepared-execution-plan-cache
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-non-prepared-plan-cache.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for what the SQL non-prepared execution plan cache is, how it works, how to enable or size it, or how to verify a cache hit for a non-PREPARE query.
- Retrieval Keywords: SQL Non-Prepared Execution Plan Cache, non-prepared plan cache, prepared plan cache, session-level feature, AST parameterization, tidb_enable_non_prepared_plan_cache, tidb_session_plan_cache_size, tidb_plan_cache_max_plan_size, least recently used, LRU, @@last_plan_from_cache, SET tidb_enable_non_prepared_plan_cache = ON, SELECT * FROM t WHERE b < 10 AND a = 1, SELECT * FROM t WHERE b < 5 AND a = 2
- Follow-up Guidance: It also notes that the cache memory controlled by tidb_session_plan_cache_size is shared with the prepared and non-prepared plan cache, so enabling the non-prepared plan cache can reduce the hit rate of the original prepared plan cache.
- Classification Note: This is classified as performance because the content explains a feature that skips the optimization phase for some non-PREPARE statements to improve performance, while also describing its memory and CPU overhead.

## Official Source Content

# SQL Non-Prepared Execution Plan Cache

TiDB supports execution plan caching for some non-`PREPARE` statements, similar to the [`Prepare`/`Execute` statements](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache). This feature allows these statements to skip the optimization phase and improve performance.

Enabling the non-prepared plan cache might incur additional memory and CPU overhead and might not be suitable for all situations. To determine whether to enable this feature in your scenario, refer to the [Performance benefits](#performance-benefits) and [Memory monitoring](#monitoring) sections.
## Principle

The non-prepared plan cache is a session-level feature that shares a cache with the [prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache). The basic principle of the non-prepared plan cache is as follows:

1. After you enable the non-prepared plan cache, TiDB first parameterizes the query based on the abstract syntax tree (AST). For example, `SELECT * FROM t WHERE b < 10 AND a = 1` is parameterized as `SELECT * FROM t WHERE b < ? and a = ?`.
2. Then, TiDB uses the parameterized query to search the plan cache.
3. If a reusable plan is found, it is directly used and the optimization phase is skipped.
4. Otherwise, the optimizer generates a new plan and adds it back into the cache for reuse in the subsequent query.
## Usage

To enable or disable the non-prepared plan cache, you can set the [`tidb_enable_non_prepared_plan_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_non_prepared_plan_cache) system variable. You can also control the size of the non-prepared plan cache using the [`tidb_session_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_session_plan_cache_size-new-in-v710) system variable. When the number of cached plans exceeds `tidb_session_plan_cache_size`, TiDB evicts plans using the least recently used (LRU) strategy.

Starting from v7.1.0, you can control the maximum size of a plan that can be cached using the system variable [`tidb_plan_cache_max_plan_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_plan_cache_max_plan_size-new-in-v710). The default value is 2 MB. If the size of a plan exceeds this value, the plan will not be cached.

> **Note:**
>
> The memory specified by `tidb_session_plan_cache_size` is shared between the prepared and non-prepared plan cache. If you have enabled the prepared plan cache for the current cluster, enabling the non-prepared plan cache might reduce the hit rate of the original prepared plan cache.
## Example

The following example shows how to use the non-prepared plan cache:

1. Create a table `t` for testing:

    ```sql
    CREATE TABLE t (a INT, b INT, KEY(b));
    ```

2. Enable the non-prepared plan cache:

    ```sql
    SET tidb_enable_non_prepared_plan_cache = ON;
    ```

3. Execute the following two queries:

    ```sql
    SELECT * FROM t WHERE b < 10 AND a = 1;
    SELECT * FROM t WHERE b < 5 AND a = 2;
    ```

4. Check whether the second query hits the cache:

    ```sql
    SELECT @@last_plan_from_cache;
    ```

    If the value of `last_plan_from_cache` in the output is `1`, it means that the execution plan of the second query comes from the cache:

    ```sql
    +------------------------+
    | @@last_plan_from_cache |
    +------------------------+
    |                      1 |
    +------------------------+
    1 row in set (0.00 sec)
    ```
