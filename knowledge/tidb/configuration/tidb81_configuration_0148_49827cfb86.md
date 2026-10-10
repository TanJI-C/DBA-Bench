# Ignore close and deallocate for prepared cache reuse

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-prepared-plan-cache.md`
- Source Title: `SQL Prepared Execution Plan Cache`
- Source Heading Path: `SQL Prepared Execution Plan Cache > Ignore the `COM_STMT_CLOSE` command and the `DEALLOCATE PREPARE` statement | SQL Prepared Execution Plan Cache > Ignore the `COM_STMT_CLOSE` command and the `DEALLOCATE PREPARE` statement > Monitoring`
- Source Line Ranges: `277-352`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`, `cloud`, `shared`
- Topic Tags: `prepared-plan-cache`, `prepared-statements`, `deallocate-prepare`, `close-stmt`, `system-variables`, `plan-reuse`, `monitoring`, `grafana`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0148_49827cfb86`
- Source ID: `tidb-docs-8.1:sql-prepared-plan-cache.md#ignore-the-com-stmt-close-command-and-the-deallocate-prepare-statement`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9da3b1edf45fe278daddff0de7b26c944a54f69c2688979465ef2a49291b1f59`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache#ignore-the-com-stmt-close-command-and-the-deallocate-prepare-statement
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-prepared-plan-cache.md

## Retrieval Guidance

- Use When: Use this when searching for how TiDB handles `COM_STMT_CLOSE` or `DEALLOCATE PREPARE` in relation to prepared plan cache reuse and how to monitor whether plan cache is being used.
- Retrieval Keywords: tidb_ignore_prepared_cache_close_stmt, COM_STMT_CLOSE, DEALLOCATE PREPARE, @@last_plan_from_cache, Queries Using Plan Cache OPS, Plan Cache Miss OPS, Prepared Statement Count, ignore prepared cache close stmt
- Follow-up Guidance: The content shows that setting `tidb_ignore_prepared_cache_close_stmt` to `ON` lets TiDB ignore close commands for prepared statements and lists Grafana and TiDB Cloud monitoring metrics related to plan cache usage.
- Classification Note: This is classified as configuration because the official content centers on the `tidb_ignore_prepared_cache_close_stmt` system variable and related monitoring for plan cache behavior.

## Official Source Content

## Ignore the `COM_STMT_CLOSE` command and the `DEALLOCATE PREPARE` statement

To reduce the syntax parsing cost of SQL statements, it is recommended that you run `prepare stmt` once, then `execute stmt` multiple times before running `deallocate prepare`:

```sql
MySQL [test]> prepare stmt from '...'; -- Prepare once
MySQL [test]> execute stmt using ...;  -- Execute once
MySQL [test]> ...
MySQL [test]> execute stmt using ...;  -- Execute multiple times
MySQL [test]> deallocate prepare stmt; -- Release the prepared statement
```

In real practice, you may be used to running `deallocate prepare` each time after running `execute stmt`, as shown below:

```sql
MySQL [test]> prepare stmt from '...'; -- Prepare once
MySQL [test]> execute stmt using ...;
MySQL [test]> deallocate prepare stmt; -- Release the prepared statement
MySQL [test]> prepare stmt from '...'; -- Prepare twice
MySQL [test]> execute stmt using ...;
MySQL [test]> deallocate prepare stmt; -- Release the prepared statement
```

In such practice, the plan obtained by the first executed statement cannot be reused by the second executed statement.

To address the problem, you can set the system variable [`tidb_ignore_prepared_cache_close_stmt`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ignore_prepared_cache_close_stmt-new-in-v600) to `ON` so TiDB ignores commands to close `prepare stmt`:

```sql
mysql> set @@tidb_ignore_prepared_cache_close_stmt=1;  -- Enable the variable
Query OK, 0 rows affected (0.00 sec)

mysql> prepare stmt from 'select * from t'; -- Prepare once
Query OK, 0 rows affected (0.00 sec)

mysql> execute stmt;                        -- Execute once
Empty set (0.00 sec)

mysql> deallocate prepare stmt;             -- Release after the first execute
Query OK, 0 rows affected (0.00 sec)

mysql> prepare stmt from 'select * from t'; -- Prepare twice
Query OK, 0 rows affected (0.00 sec)

mysql> execute stmt;                        -- Execute twice
Empty set (0.00 sec)

mysql> select @@last_plan_from_cache;       -- Reuse the last plan
+------------------------+
| @@last_plan_from_cache |
+------------------------+
|                      1 |
+------------------------+
1 row in set (0.00 sec)
```
### Monitoring

In [the Grafana dashboard](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard) on the TiDB page in the **Executor** section, there are the "Queries Using Plan Cache OPS" and "Plan Cache Miss OPS" graphs. These graphs can be used to check if both TiDB and the application are configured correctly to allow the SQL Plan Cache to work correctly. The **Server** section on the same page provides the "Prepared Statement Count" graph. This graph shows a non-zero value if the application uses prepared statements, which is required for the SQL Plan Cache to function correctly.

![`sql_plan_cache`](/media/performance/sql_plan_cache.png)

On the [**Monitoring**](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring) page of the [TiDB Cloud console](https://tidbcloud.com/), you can check the `Queries Using Plan Cache OPS` metric to get the number of queries using or missing plan cache per second in all TiDB instances.
