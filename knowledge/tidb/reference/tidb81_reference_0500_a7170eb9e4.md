# Non-prepared plan cache restrictions and unsupported queries

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-non-prepared-plan-cache.md`
- Source Title: `SQL Non-Prepared Execution Plan Cache`
- Source Heading Path: `SQL Non-Prepared Execution Plan Cache > Restrictions | SQL Non-Prepared Execution Plan Cache > Restrictions > Cache suboptimal plans | SQL Non-Prepared Execution Plan Cache > Restrictions > Usage restrictions`
- Source Line Ranges: `71-95`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `restrictions`, `unsupported-queries`, `suboptimal-plans`, `ignore-plan-cache`, `bindings`, `dml`, `for-update`, `parameter-limit`, `operators`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0500_a7170eb9e4`
- Source ID: `tidb-docs-8.1:sql-non-prepared-plan-cache.md#restrictions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6374ea0d7872d281a8abc000249c43551791a626a56d6ceb56dc888f303725bd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache#restrictions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-non-prepared-plan-cache.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks which non-prepared queries are unsupported by the plan cache, why a parameterized query might reuse a suboptimal plan, or how to bypass cached plans.
- Retrieval Keywords: Restrictions, Cache suboptimal plans, ignore_plan_cache(), CREATE BINDING FOR SELECT ... USING SELECT /*+ ignore_plan_cache() */ ..., Window, Having, three or more Join tables, subqueries, ORDER BY 1, GROUP BY a+1, JSON, ENUM, SET, BIT, a is NULL, more than 200 parameters, 44823, tidb_opt_fix_control, virtual columns, temporary tables, views, memory tables, INFORMATION_SCHEMA.COLUMNS, queries with hints or bindings are not supported, FOR UPDATE, tidb_enable_non_prepared_plan_cache_for_dml
- Follow-up Guidance: The content adds that if a query does not meet the support conditions for non-prepared plan cache, it falls back to the regular optimization process.
- Classification Note: This is classified as reference because it enumerates support boundaries, unsupported query patterns, and exact related identifiers for the non-prepared plan cache.

## Official Source Content

## Restrictions
### Cache suboptimal plans

TiDB only caches one plan for a parameterized query. For example, the queries `SELECT * FROM t WHERE a < 1` and `SELECT * FROM t WHERE a < 100000` share the same parameterized form, `SELECT * FROM t WHERE a < ?`, and thus share the same plan.

If this causes performance issues, you can use the `ignore_plan_cache()` hint to ignore plans in the cache, so that the optimizer generates a new execution plan for the SQL every time. If the SQL cannot be modified, you can create a binding to solve the problem. For example, `CREATE BINDING FOR SELECT ... USING SELECT /*+ ignore_plan_cache() */ ...`.
### Usage restrictions

Due to the preceding risks and the fact that the execution plan cache only provides significant benefits for simple queries (if a query is complex and takes a long time to execute, using the execution plan cache might not be very helpful), TiDB has strict restrictions on the scope of non-prepared plan cache. The restrictions are as follows:

- Queries or plans that are not supported by the [Prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache) are also not supported by the non-prepared plan cache.
- Queries that contain complex operators such as `Window` or `Having` are not supported.
- Queries that contain three or more `Join` tables or subqueries are not supported.
- Queries that contain numbers or expressions directly after `ORDER BY` or `GROUP BY` are not supported, such as `ORDER BY 1` and `GROUP BY a+1`. Only `ORDER BY column_name` and `GROUP BY column_name` are supported.
- Queries that filter on columns of `JSON`, `ENUM`, `SET`, or `BIT` type are not supported, such as `SELECT * FROM t WHERE json_col = '{}'`.
- Queries that filter on `NULL` values are not supported, such as `SELECT * FROM t WHERE a is NULL`.
- Queries with more than 200 parameters after parameterization are not supported by default, such as `SELECT * FROM t WHERE a in (1, 2, 3, ... 201)`. Starting from v7.3.0, you can modify this limit by setting the [`44823`](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls#44823-new-in-v730) fix in the [`tidb_opt_fix_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_fix_control-new-in-v653-and-v710) system variable.
- Queries that access virtual columns, temporary tables, views, or memory tables are not supported, such as `SELECT * FROM INFORMATION_SCHEMA.COLUMNS`, where `COLUMNS` is a TiDB memory table.
- Queries with hints or bindings are not supported.
- DML statements or `SELECT` statements with the `FOR UPDATE` clause are not supported by default. To remove this restriction, you can execute `SET tidb_enable_non_prepared_plan_cache_for_dml = ON`.

After you enable this feature, the optimizer quickly evaluates the query. If it does not meet the support conditions for non-prepared plan cache, the query falls back to the regular optimization process.
