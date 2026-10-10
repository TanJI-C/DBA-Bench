# Diagnose why prepared plan cache is skipped

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-prepared-plan-cache.md`
- Source Title: `SQL Prepared Execution Plan Cache`
- Source Heading Path: `SQL Prepared Execution Plan Cache > Diagnostics of Prepared Plan Cache`
- Source Line Ranges: `131-170`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `prepared-plan-cache`, `diagnostics`, `show-warnings`, `cache-skip`, `subqueries`, `type-conversion`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0067_924cf2ef1a`
- Source ID: `tidb-docs-8.1:sql-prepared-plan-cache.md#diagnostics-of-prepared-plan-cache`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e168af27cdcf560ff70a99a3427f3a97f1bb3d582442558d152283f767fcf924`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache#diagnostics-of-prepared-plan-cache
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-prepared-plan-cache.md

## Retrieval Guidance

- Use When: Use this when diagnosing why a prepared statement or execution plan was not cached and you need the warning message that explains the skip reason.
- Retrieval Keywords: SHOW WARNINGS, skip plan-cache, sub-queries are un-cacheable, may be converted to INT, PREPARE st FROM, execute st using, prepared plan cache diagnostics
- Follow-up Guidance: The content shows using `SHOW WARNINGS` after `PREPARE` or `EXECUTE` to see the reason such as subqueries or type conversion.
- Classification Note: This is classified as diagnosis because the official content explains how to inspect cache skip reasons with warning output.

## Official Source Content

## Diagnostics of Prepared Plan Cache

Some queries or plans cannot be cached. You can use the `SHOW WARNINGS` statement to check whether the query or plan is cached. If it is not cached, you can check the reason for the failure in the result. For example:

```sql
mysql> PREPARE st FROM 'SELECT * FROM t WHERE a > (SELECT MAX(a) FROM t)';  -- The query contains a subquery and cannot be cached.

Query OK, 0 rows affected, 1 warning (0.01 sec)

mysql> show warnings;  -- Checks the reason why the query plan cannot be cached.

+---------+------+-----------------------------------------------+
| Level   | Code | Message                                       |
+---------+------+-----------------------------------------------+
| Warning | 1105 | skip plan-cache: sub-queries are un-cacheable |
+---------+------+-----------------------------------------------+
1 row in set (0.00 sec)

mysql> prepare st from 'select * from t where a<?';

Query OK, 0 rows affected (0.00 sec)

mysql> set @a='1';

Query OK, 0 rows affected (0.00 sec)

mysql> execute st using @a;  -- The optimization converts a non-INT type to an INT type, and the execution plan might change with the change of the parameter, so TiDB does not cache the plan.

Empty set, 1 warning (0.01 sec)

mysql> show warnings;

+---------+------+----------------------------------------------+
| Level   | Code | Message                                      |
+---------+------+----------------------------------------------+
| Warning | 1105 | skip plan-cache: '1' may be converted to INT |
+---------+------+----------------------------------------------+
1 row in set (0.00 sec)
```
