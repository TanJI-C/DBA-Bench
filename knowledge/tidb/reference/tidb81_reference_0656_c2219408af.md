# SHOW DATABASES syntax and usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-databases.md`
- Source Title: `SHOW DATABASES | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW DATABASES | SHOW DATABASES > Synopsis | SHOW DATABASES > Examples | SHOW DATABASES > MySQL compatibility | SHOW DATABASES > See also`
- Source Line Ranges: `5-62`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show databases`, `show schemas`, `privileges`, `syntax`, `examples`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0656_c2219408af`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-databases.md#show-databases`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4f6c74b0a2f3012208fb391bc6e616429ef7d7f645a4d485e04588fbdce0fd1c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-databases#show-databases
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-databases.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the syntax, behavior, alias, examples, or MySQL compatibility of `SHOW DATABASES` or `SHOW SCHEMAS` in TiDB.
- Retrieval Keywords: SHOW DATABASES, SHOW SCHEMAS, ShowDatabasesStmt, SHOW DATABASES LIKE, SHOW DATABASES WHERE, current user privileges, hidden databases, information_schema always appears first, INFORMATION_SCHEMA, PERFORMANCE_SCHEMA, CREATE DATABASE mynewdb, MySQL compatibility, INFORMATION_SCHEMA.SCHEMATA
- Follow-up Guidance: Related official references listed here are `SHOW SCHEMAS`, `DROP DATABASE`, `CREATE DATABASE`, and `INFORMATION_SCHEMA.SCHEMATA`.
- Classification Note: This is a SQL reference chunk because the content defines `SHOW DATABASES` syntax, privilege-based visibility, alias behavior, examples, and compatibility notes.

## Official Source Content

# SHOW DATABASES

This statement shows a list of databases that the current user has privileges to. Databases which the current user does not have access to will appear hidden from the list. The `information_schema` database always appears first in the list of databases.

`SHOW SCHEMAS` is an alias of this statement.
## Synopsis

```ebnf+diagram
ShowDatabasesStmt ::=
    "SHOW" "DATABASES" ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

```sql
mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| INFORMATION_SCHEMA |
| PERFORMANCE_SCHEMA |
| mysql              |
| test               |
+--------------------+
4 rows in set (0.00 sec)

mysql> CREATE DATABASE mynewdb;
Query OK, 0 rows affected (0.10 sec)

mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| INFORMATION_SCHEMA |
| PERFORMANCE_SCHEMA |
| mynewdb            |
| mysql              |
| test               |
+--------------------+
5 rows in set (0.00 sec)
```
## MySQL compatibility

The `SHOW DATABASES` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [SHOW SCHEMAS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-schemas)
* [DROP DATABASE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-database)
* [CREATE DATABASE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-database)
* [`INFORMATION_SCHEMA.SCHEMATA`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-schemata)
