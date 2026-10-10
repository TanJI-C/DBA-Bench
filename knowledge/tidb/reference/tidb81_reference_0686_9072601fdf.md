# SHOW [FULL] TABLES syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-tables.md`
- Source Title: `SHOW [FULL] TABLES | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW [FULL] TABLES | SHOW [FULL] TABLES > Synopsis | SHOW [FULL] TABLES > Examples | SHOW [FULL] TABLES > MySQL compatibility | SHOW [FULL] TABLES > See also`
- Source Line Ranges: `5-87`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show tables`, `show full tables`, `syntax`, `examples`, `mysql compatibility`, `views`, `sequences`, `database selection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0686_9072601fdf`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-tables.md#show-full-tables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8a66e4e68f40b42a275619fba5878a7bd39e8389885c490938ba9becb6a64b41`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-tables#show-full-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-tables.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the syntax, behavior, or examples for listing tables or views with `SHOW TABLES`, `SHOW FULL TABLES`, or `SHOW TABLES IN DatabaseName`.
- Retrieval Keywords: SHOW TABLES, SHOW FULL TABLES, SHOW TABLES IN, SHOW TABLES FROM, LIKE, WHERE, BASE TABLE, SEQUENCE, VIEW, currently selected database, Tables_in_test, Table_type, MySQL compatibility, INFORMATION_SCHEMA.TABLES
- Follow-up Guidance: The source also points to related references for `SHOW CREATE TABLE` and `INFORMATION_SCHEMA.TABLES`.
- Classification Note: This is a SQL reference chunk because it defines the `SHOW [FULL] TABLES` statement syntax, describes its output, and provides SQL examples and MySQL compatibility notes.

## Official Source Content

# SHOW [FULL] TABLES

This statement shows a list of tables and views in the currently selected database. The optional keyword `FULL` indicates if a table is of type `BASE TABLE`, `SEQUENCE`, or `VIEW`.

To show tables in a different database, use `SHOW TABLES IN DatabaseName`.
## Synopsis

```ebnf+diagram
ShowTableStmt ::=
    "SHOW" "FULL"? "TABLES" ("FROM" Identifier | "IN" Identifier )? ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

```sql
mysql> CREATE TABLE t1 (a int);
Query OK, 0 rows affected (0.12 sec)

mysql> CREATE VIEW v1 AS SELECT 1;
Query OK, 0 rows affected (0.10 sec)

mysql> SHOW TABLES;
+----------------+
| Tables_in_test |
+----------------+
| t1             |
| v1             |
+----------------+
2 rows in set (0.00 sec)

mysql> SHOW FULL TABLES;
+----------------+------------+
| Tables_in_test | Table_type |
+----------------+------------+
| t1             | BASE TABLE |
| v1             | VIEW       |
+----------------+------------+
2 rows in set (0.00 sec)

mysql> SHOW TABLES IN mysql;
+-------------------------+
| Tables_in_mysql         |
+-------------------------+
| GLOBAL_VARIABLES        |
| bind_info               |
| columns_priv            |
| db                      |
| default_roles           |
| expr_pushdown_blacklist |
| gc_delete_range         |
| gc_delete_range_done    |
| global_priv             |
| help_topic              |
| opt_rule_blacklist      |
| role_edges              |
| stats_buckets           |
| stats_feedback          |
| stats_histograms        |
| stats_meta              |
| stats_top_n             |
| tables_priv             |
| tidb                    |
| user                    |
+-------------------------+
20 rows in set (0.00 sec)
```
## MySQL compatibility

The `SHOW [FULL] TABLES` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [DROP TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-table)
* [SHOW CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table)
* [`INFORMATION_SCHEMA.TABLES`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tables)
