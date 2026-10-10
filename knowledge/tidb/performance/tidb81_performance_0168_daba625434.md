# Prepared plan cache behavior, limits, and cache-hit verification

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-prepared-plan-cache.md`
- Source Title: `SQL Prepared Execution Plan Cache`
- Source Heading Path: `SQL Prepared Execution Plan Cache`
- Source Line Ranges: `5-130`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `prepared-statements`, `plan-cache`, `execution-plans`, `cache-invalidation`, `lru`, `session-cache`, `query-optimization`, `sql-bindings`, `system-variables`, `cache-hit-verification`, `sql-hints`, `limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0168_daba625434`
- Source ID: `tidb-docs-8.1:sql-prepared-plan-cache.md#sql-prepared-execution-plan-cache`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1479bedf58a4503274397f2bca00df5f451eb69ff79dd492b10d984db26f39bb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache#sql-prepared-execution-plan-cache
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-prepared-plan-cache.md

## Retrieval Guidance

- Use When: Use this content when checking how TiDB prepared statement execution plan cache works, why a prepared query is not cached or misses the cache, what invalidates cached plans, or how to verify a cache hit for `Prepare`/`Execute` statements.
- Retrieval Keywords: SQL Prepared Execution Plan Cache, COM_STMT_PREPARE, COM_STMT_EXECUTE, PREPARE, EXECUTE, tidb_enable_prepared_plan_cache, last_plan_from_cache, ignore_plan_cache(), set_var, Prepared statement contains too many placeholders, 65535 ?, LRU linked list, session-level cache, schema version, sql_select_limit, time_zone, SQL mode, tidb_partition_prune_mode, static, PhysicalApply, TableDual, UnionScan, TiFlash, information_schema.columns, SQL bindings, cache invalidation, cache miss, cache hit verification
- Follow-up Guidance: The content also points to `SQL Non-Prepared Execution Plan Cache` for normal queries and shows using `@@last_plan_from_cache` to verify whether the previous `Execute` used a cached plan.
- Classification Note: This is classified as performance because the official content explains execution plan caching, cache-hit behavior, invalidation conditions, and cases where caching can improve or hurt query execution performance.

## Official Source Content

# SQL Prepared Execution Plan Cache

TiDB supports execution plan caching for `Prepare` and `Execute` queries. This includes both forms of prepared statements:

- Using the `COM_STMT_PREPARE` and `COM_STMT_EXECUTE` protocol features.
- Using the SQL statements `PREPARE` and `EXECUTE`.

The TiDB optimizer handles these two types of queries in the same way: when preparing, the parameterized query is parsed into an AST (Abstract Syntax Tree) and cached; in later execution, the execution plan is generated based on the stored AST and specific parameter values.

When the execution plan cache is enabled, in the first execution every `Prepare` statement checks whether the current query can use the execution plan cache, and if the query can use it, then put the generated execution plan into a cache implemented by LRU (Least Recently Used) linked list. In the subsequent `Execute` queries, the execution plan is obtained from the cache and checked for availability. If the check succeeds, the step of generating an execution plan is skipped. Otherwise, the execution plan is regenerated and saved in the cache.

TiDB also supports execution plan caching for some non-`PREPARE` statements, similar to the `Prepare`/`Execute` statements. For more details, refer to [Non-prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache).

In the current version of TiDB, if a `Prepare` statement meets any of the following conditions, the query or the plan is not cached:

- The query contains SQL statements other than `SELECT`, `UPDATE`, `INSERT`, `DELETE`, `Union`, `Intersect`, and `Except`.
- The query accesses temporary tables, or a table that contains generated columns, or uses static mode (that is, [`tidb_partition_prune_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_partition_prune_mode-new-in-v51) is set to `static`) to access partitioning tables.
- The query contains non-correlated sub-queries, such as `SELECT * FROM t1 WHERE t1.a > (SELECT 1 FROM t2 WHERE t2.b < 1)`.
- The query contains correlated sub-queries with `PhysicalApply` operators in the execution plan, such as `SELECT * FROM t1 WHERE t1.a > (SELECT a FROM t2 WHERE t1.b > t2.b)`.
- The query contains the `ignore_plan_cache` or `set_var` hint, such as `SELECT /*+ ignore_plan_cache() */ * FROM t` or `SELECT /*+ set_var(max_execution_time=1) */ * FROM t`.
- The query contains variables other than `?` (including system variables or user-defined variables), such as `select * from t where a>? and b>@x`.
- The query contains the functions that cannot be cached: `database()`, `current_user`, `current_role`, `user`, `connection_id`, `last_insert_id`, `row_count`, `version`, and `like`.
- The query uses a variable as the `LIMIT` parameter (such as `LIMIT ?` and `LIMIT 10, ?`) and the variable value is greater than 10000.
- The query contains `?` after `Order By`, such as `Order By ?`. Such queries sort data based on the column specified by `?`. If the queries targeting different columns use the same execution plan, the results will be wrong. Therefore, such queries are not cached. However, if the query is a common one, such as `Order By a+?`, it is cached.
- The query contains `?` after `Group By`, such as `Group By?`. Such queries group data based on the column specified by `?`. If the queries targeting different columns use the same execution plan, the results will be wrong. Therefore, such queries are not cached. However, if the query is a common one, such as `Group By a+?`, it is cached.
- The query contains `?` in the definition of the `Window Frame` window function, such as `(partition by year order by sale rows ? preceding)`. If `?` appears elsewhere in the window function, the query is cached.
- The query contains parameters for comparing `int` and `string`, such as `c_int >= ?` or `c_int in (?, ?)`, in which `?` indicates the string type, such as `set @x='123'`. To ensure that the query result is compatible with MySQL, parameters need to be adjusted in each query, so such queries are not cached.
- The plan attempts to access `TiFlash`.
- In most cases, the plan that contains `TableDual` is not cached, unless the current `Prepare` statement does not have parameters.
- The query accesses TiDB system views, such as `information_schema.columns`. It is not recommended to use `Prepare` and `Execute` statements to access system views.

TiDB has a limitation on the number of `?` in a query. If a query contains more than 65535 `?`, an error `Prepared statement contains too many placeholders` is reported.

The LRU linked list is designed as a session-level cache because `Prepare`/`Execute` cannot be executed across sessions. Each element of the LRU list is a key-value pair. The value is the execution plan, and the key is composed of the following parts:

- The name of the database where `Execute` is executed
- The identifier of the `Prepare` statement, that is, the name after the `PREPARE` keyword
- The current schema version, which is updated after every successfully executed DDL statement
- The SQL mode when executing `Execute`
- The current time zone, which is the value of the `time_zone` system variable
- The value of the `sql_select_limit` system variable

Any change in the preceding information (for example, switching databases, renaming `Prepare` statement, executing DDL statements, or modifying the value of SQL mode/`time_zone`), or the LRU cache elimination mechanism causes the execution plan cache miss when executing.

After the execution plan cache is obtained from the cache, TiDB first checks whether the execution plan is still valid. If the current `Execute` statement is executed in an explicit transaction, and the referenced table is modified in the transaction pre-order statement, the cached execution plan accessing this table does not contain the `UnionScan` operator, then it cannot be executed.

After the validation test is passed, the scan range of the execution plan is adjusted according to the current parameter values, and then used to perform data querying.

There are several points worth noting about execution plan caching and query performance:
- No matter an execution plan is cached or not, it is affected by SQL bindings. For execution plans that have not been cached (the first `Execute`), these plans are affected by existing SQL bindings. For execution plans that have been cached, if new SQL Bindings are created, these plans become invalid.
- Cached plans are not affected by changes in statistics, optimization rules, and blocklist pushdown by expressions.
- Considering that the parameters of `Execute` are different, the execution plan cache prohibits some aggressive query optimization methods that are closely related to specific parameter values to ensure adaptability. This causes that the query plan may not be optimal for certain parameter values. For example, the filter condition of the query is `where a > ? And a < ?`, the parameters of the first `Execute` statement are `2` and `1` respectively. Considering that these two parameters maybe be `1` and `2` in the next execution time, the optimizer does not generate the optimal `TableDual` execution plan that is specific to current parameter values;
- If cache invalidation and elimination are not considered, an execution plan cache is applied to various parameter values, which in theory also results in non-optimal execution plans for certain values. For example, if the filter condition is `where a < ?` and the parameter value used for the first execution is `1`, then the optimizer generates the optimal `IndexScan` execution plan and puts it into the cache. In the subsequent executions, if the value becomes `10000`, the `TableScan` plan might be the better one. But due to the execution plan cache, the previously generated `IndexScan` is used for execution. Therefore, the execution plan cache is more suitable for application scenarios where the query is simple (the ratio of compilation is high) and the execution plan is relatively fixed.

Starting from v6.1.0, the execution plan cache is enabled by default. You can control prepared plan cache via the system variable [`tidb_enable_prepared_plan_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_prepared_plan_cache-new-in-v610).

> **Note:**
>
> The [`tidb_enable_prepared_plan_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_prepared_plan_cache-new-in-v610) system variable controls the execution plan cache only for `Prepare`/`Execute` queries, not for normal queries. For the execution plan cache for normal queries, see [SQL Non-Prepared Execution Plan Cache](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache).

After the execution plan cache feature is enabled, you can use the session-level system variable [`last_plan_from_cache`](https://docs.pingcap.com/tidb/stable/system-variables#last_plan_from_cache-new-in-v40) to see whether the previous `Execute` statement used the cached execution plan, for example:

```sql
MySQL [test]> create table t(a int);
Query OK, 0 rows affected (0.00 sec)
MySQL [test]> prepare stmt from 'select * from t where a = ?';
Query OK, 0 rows affected (0.00 sec)
MySQL [test]> set @a = 1;
Query OK, 0 rows affected (0.00 sec)

-- The first execution generates an execution plan and saves it in the cache.
MySQL [test]> execute stmt using @a;
Empty set (0.00 sec)
MySQL [test]> select @@last_plan_from_cache;
+------------------------+
| @@last_plan_from_cache |
+------------------------+
| 0                      |
+------------------------+
1 row in set (0.00 sec)

-- The second execution hits the cache.
MySQL [test]> execute stmt using @a;
Empty set (0.00 sec)
MySQL [test]> select @@last_plan_from_cache;
+------------------------+
| @@last_plan_from_cache |
+------------------------+
| 1                      |
+------------------------+
1 row in set (0.00 sec)
```

If you find that a certain set of `Prepare`/`Execute` has unexpected behavior due to the execution plan cache, you can use the `ignore_plan_cache()` SQL hint to skip using the execution plan cache for the current statement. Still, use the preceding statement as an example:

```sql
MySQL [test]> prepare stmt from 'select /*+ ignore_plan_cache() */ * from t where a = ?';
Query OK, 0 rows affected (0.00 sec)
MySQL [test]> set @a = 1;
Query OK, 0 rows affected (0.00 sec)
MySQL [test]> execute stmt using @a;
Empty set (0.00 sec)
MySQL [test]> select @@last_plan_from_cache;
+------------------------+
| @@last_plan_from_cache |
+------------------------+
| 0                      |
+------------------------+
1 row in set (0.00 sec)
MySQL [test]> execute stmt using @a;
Empty set (0.00 sec)
MySQL [test]> select @@last_plan_from_cache;
+------------------------+
| @@last_plan_from_cache |
+------------------------+
| 0                      |
+------------------------+
1 row in set (0.00 sec)
```
