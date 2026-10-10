# SHOW GLOBAL or SESSION VARIABLES syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-variables.md`
- Source Title: `SHOW [GLOBAL|SESSION] VARIABLES | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW [GLOBAL|SESSION] VARIABLES | SHOW [GLOBAL|SESSION] VARIABLES > Synopsis | SHOW [GLOBAL|SESSION] VARIABLES > Examples | SHOW [GLOBAL|SESSION] VARIABLES > MySQL compatibility | SHOW [GLOBAL|SESSION] VARIABLES > See also`
- Source Line Ranges: `5-80`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `show variables`, `global scope`, `session scope`, `syntax`, `examples`, `mysql compatibility`, `system variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0687_5c3d3bc881`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-variables.md#show-global-session-variables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `37d98d6936e1f9218a1d3b411986e40487af9d9b14948bd3726eede9c03f858e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-variables#show-global-session-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-variables.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about the syntax, scope behavior, filtering options, or examples for `SHOW [GLOBAL|SESSION] VARIABLES` in TiDB.
- Retrieval Keywords: SHOW GLOBAL VARIABLES, SHOW SESSION VARIABLES, SHOW VARIABLES, ShowVariablesStmt, ShowLikeOrWhere, LIKE SimpleExpr, WHERE Expression, default scope of SESSION, SHOW GLOBAL VARIABLES LIKE 'tidb_stmt_summary%', SHOW GLOBAL VARIABLES LIKE 'time_zone%', SHOW VARIABLES WHERE Variable_name="tidb_window_concurrency", SHOW VARIABLES WHERE Value=300, MySQL compatibility, system variables
- Follow-up Guidance: The source also points to `SET [GLOBAL|SESSION]` and mentions System Variables for detailed descriptions of the variables.
- Classification Note: This is a SQL reference chunk because it defines the statement syntax, scope rules, example queries, and MySQL compatibility for `SHOW [GLOBAL|SESSION] VARIABLES`.

## Official Source Content

# SHOW [GLOBAL|SESSION] VARIABLES

This statement shows a list of variables for the scope of either `GLOBAL` or `SESSION`. If no scope is specified, the default scope of `SESSION` will apply.
## Synopsis

```ebnf+diagram
ShowVariablesStmt ::=
    "SHOW" ("GLOBAL" | "SESSION")? VARIABLES ShowLikeOrWhere?
    
ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

The following example demonstrates how to use the `SHOW [GLOBAL|SESSION] VARIABLES` statement to show variables whose names or values match a specific pattern. For detailed descriptions of these variables, see [System Variables](https://docs.pingcap.com/tidb/stable/system-variables).

```sql
mysql> SHOW GLOBAL VARIABLES LIKE 'tidb_stmt_summary%';
+-------------------------------------+---------------------+
| Variable_name                       | Value               |
+-------------------------------------+---------------------+
| tidb_stmt_summary_enable_persistent | OFF                 |
| tidb_stmt_summary_file_max_backups  | 0                   |
| tidb_stmt_summary_file_max_days     | 3                   |
| tidb_stmt_summary_file_max_size     | 64                  |
| tidb_stmt_summary_filename          | tidb-statements.log |
| tidb_stmt_summary_history_size      | 24                  |
| tidb_stmt_summary_internal_query    | OFF                 |
| tidb_stmt_summary_max_sql_length    | 4096                |
| tidb_stmt_summary_max_stmt_count    | 3000                |
| tidb_stmt_summary_refresh_interval  | 1800                |
+-------------------------------------+---------------------+
10 rows in set (0.001 sec)

mysql> SHOW GLOBAL VARIABLES LIKE 'time_zone%';
+---------------+--------+
| Variable_name | Value  |
+---------------+--------+
| time_zone     | SYSTEM |
+---------------+--------+
1 row in set (0.00 sec)

mysql> SHOW VARIABLES WHERE Variable_name="tidb_window_concurrency";
+-------------------------+-------+
| Variable_name           | Value |
+-------------------------+-------+
| tidb_window_concurrency | -1    |
+-------------------------+-------+
1 row in set (0.00 sec)

mysql> SHOW VARIABLES WHERE Value=300;
+--------------------------------+-------+
| Variable_name                  | Value |
+--------------------------------+-------+
| ddl_slow_threshold             | 300   |
| delayed_insert_timeout         | 300   |
| innodb_purge_batch_size        | 300   |
| key_cache_age_threshold        | 300   |
| slave_checkpoint_period        | 300   |
| tidb_slow_log_threshold        | 300   |
| tidb_wait_split_region_timeout | 300   |
+--------------------------------+-------+
7 rows in set (0.00 sec)
```
## MySQL compatibility

The `SHOW [GLOBAL|SESSION] VARIABLES` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [`SET [GLOBAL|SESSION]`](/sql-statements/sql-statement-set-variable.md)
