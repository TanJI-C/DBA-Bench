# USE statement syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-use.md`
- Source Title: `USE | TiDB SQL Statement Reference`
- Source Heading Path: `USE | USE > Synopsis | USE > Examples | USE > MySQL compatibility | USE > See also`
- Source Line Ranges: `5-82`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `use statement`, `current database`, `session`, `syntax`, `examples`, `mysql compatibility`, `show tables`, `create database`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0699_00dbc87e10`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-use.md#use`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7a6d9af0c01de21cf6759506d6d003da9b490b9689d195cd2a969575680e6518`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-use#use
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-use.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about selecting the current database for a user session with the SQL USE statement, including syntax or example behavior before running SHOW TABLES or CREATE TABLE.
- Retrieval Keywords: USE, USE DBName, UseStmt ::= "USE" DBName, current database, user session, Identifier, USE mysql, USE newtest, SHOW TABLES, CREATE DATABASE newtest, CREATE TABLE t1 (a int), Database changed, MySQL compatibility
- Follow-up Guidance: The source also points to related statements CREATE DATABASE and SHOW TABLES.
- Classification Note: This is reference content because it defines the USE statement syntax, states that it selects the current database for the session, and shows examples plus MySQL compatibility.

## Official Source Content

# USE

The `USE` statement selects a current database for the user session.
## Synopsis

```ebnf+diagram
UseStmt ::=
    "USE" DBName

DBName ::=
    Identifier
```
## Examples

```sql
mysql> USE mysql;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> SHOW TABLES;
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
20 rows in set (0.01 sec)

mysql> CREATE DATABASE newtest;
Query OK, 0 rows affected (0.10 sec)

mysql> USE newtest;
Database changed
mysql> SHOW TABLES;
Empty set (0.00 sec)

mysql> CREATE TABLE t1 (a int);
Query OK, 0 rows affected (0.10 sec)

mysql> SHOW TABLES;
+-------------------+
| Tables_in_newtest |
+-------------------+
| t1                |
+-------------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

The `USE` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [CREATE DATABASE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-database)
* [SHOW TABLES](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-tables)
