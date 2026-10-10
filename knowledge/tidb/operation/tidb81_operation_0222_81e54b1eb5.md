# Clear session or instance execution plan cache

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-prepared-plan-cache.md`
- Source Title: `SQL Prepared Execution Plan Cache`
- Source Heading Path: `SQL Prepared Execution Plan Cache > Clear execution plan cache`
- Source Line Ranges: `222-276`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `prepared-plan-cache`, `admin-flush`, `session-scope`, `instance-scope`, `cache-clearing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0222_81e54b1eb5`
- Source ID: `tidb-docs-8.1:sql-prepared-plan-cache.md#clear-execution-plan-cache`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6cba291a6fc2e574d13e50fc9303468bdb0881ec76ca63bc5bef4990b575fd49`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache#clear-execution-plan-cache
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-prepared-plan-cache.md

## Retrieval Guidance

- Use When: Use this when you need the exact SQL statement and scope behavior for clearing the prepared execution plan cache in the current session or a TiDB instance.
- Retrieval Keywords: ADMIN FLUSH SESSION PLAN_CACHE, ADMIN FLUSH INSTANCE PLAN_CACHE, ADMIN FLUSH [SESSION | INSTANCE] PLAN_CACHE, @@last_plan_from_cache, admin flush global plan_cache, Do not support the 'admin flush global scope.'
- Follow-up Guidance: The content also states that omitting the scope defaults to `SESSION` and that clearing `GLOBAL` execution plan cache is not supported.
- Classification Note: This is classified as operation because the official content provides the SQL command and scope semantics for clearing execution plan cache.

## Official Source Content

## Clear execution plan cache

You can clear execution plan cache by executing the `ADMIN FLUSH [SESSION | INSTANCE] PLAN_CACHE` statement.

In this statement, `[SESSION | INSTANCE]` specifies whether the plan cache is cleared for the current session or the whole TiDB instance. If the scope is not specified, the preceding statement applies to the `SESSION` cache by default.

The following is an example of clearing the `SESSION` execution plan cache:

```sql
MySQL [test]> create table t (a int);
Query OK, 0 rows affected (0.00 sec)

MySQL [test]> prepare stmt from 'select * from t';
Query OK, 0 rows affected (0.00 sec)

MySQL [test]> execute stmt;
Empty set (0.00 sec)

MySQL [test]> execute stmt;
Empty set (0.00 sec)

MySQL [test]> select @@last_plan_from_cache; -- Select the cached plan
+------------------------+
| @@last_plan_from_cache |
+------------------------+
|                      1 |
+------------------------+
1 row in set (0.00 sec)

MySQL [test]> admin flush session plan_cache; -- Clear the cached plan of the current session
Query OK, 0 rows affected (0.00 sec)

MySQL [test]> execute stmt;
Empty set (0.00 sec)

MySQL [test]> select @@last_plan_from_cache; -- The cached plan cannot be selected again, because it has been cleared
+------------------------+
| @@last_plan_from_cache |
+------------------------+
|                      0 |
+------------------------+
1 row in set (0.00 sec)
```

Currently, TiDB does not support clearing `GLOBAL` execution plan cache. That means you cannot clear the cached plan of the whole TiDB cluster. The following error is reported if you try to clear the `GLOBAL` execution plan cache:

```sql
MySQL [test]> admin flush global plan_cache;
ERROR 1105 (HY000): Do not support the 'admin flush global scope.'
```
