# DROP TABLE syntax, temporary tables, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-drop-table.md`
- Source Title: `DROP TABLE | TiDB SQL Statement Reference`
- Source Heading Path: `DROP TABLE | DROP TABLE > Synopsis | DROP TABLE > Drop temporary tables | DROP TABLE > Examples | DROP TABLE > MySQL compatibility | DROP TABLE > See also`
- Source Line Ranges: `5-73`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `drop-table`, `ddl`, `temporary-tables`, `if-exists`, `syntax`, `examples`, `mysql-compatibility`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0581_b8c7088b6b`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-drop-table.md#drop-table`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fe22d58720dab42e3afddda023c20bf8ba5d804ff7537135d1e11401fb4170a9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-table#drop-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-drop-table.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the TiDB SQL reference for `DROP TABLE` syntax, `IF EXISTS` behavior, temporary table variants, example errors and warnings, or MySQL compatibility notes.
- Retrieval Keywords: DROP TABLE, DROP TABLES, DROP TEMPORARY TABLE, DROP GLOBAL TEMPORARY TABLE, IF EXISTS, ERROR 1051 (42S02), Unknown table, SHOW WARNINGS, RESTRICT, CASCADE, DROP TABLE v1, temporary tables, MySQL compatibility
- Follow-up Guidance: The source also links to `CREATE TABLE`, `SHOW CREATE TABLE`, and `SHOW TABLES` in the See also section.
- Classification Note: This is a SQL reference chunk because the official content defines the `DROP TABLE` statement syntax, supported temporary-table forms, examples, and compatibility behavior.

## Official Source Content

# DROP TABLE

This statement drops a table from the currently selected database. An error is returned if the table does not exist, unless the `IF EXISTS` modifier is used.
## Synopsis

```ebnf+diagram
DropTableStmt ::=
    'DROP' OptTemporary TableOrTables IfExists TableNameList RestrictOrCascadeOpt

OptTemporary ::=
    ( 'TEMPORARY' | ('GLOBAL' 'TEMPORARY') )?

TableOrTables ::=
    'TABLE'
|   'TABLES'

TableNameList ::=
    TableName ( ',' TableName )*
```
## Drop temporary tables

You can use the following syntax to drop ordinary tables and temporary tables:

- Use `DROP TEMPORARY TABLE` to drop local temporary tables.
- Use `DROP GLOBAL TEMPORARY TABLE` to drop global temporary tables.
- Use `DROP TABLE` to drop ordinary tables or temporary tables.
## Examples

```sql
mysql> CREATE TABLE t1 (a INT);
Query OK, 0 rows affected (0.11 sec)

mysql> DROP TABLE t1;
Query OK, 0 rows affected (0.22 sec)

mysql> DROP TABLE table_not_exists;
ERROR 1051 (42S02): Unknown table 'test.table_not_exists'

mysql> DROP TABLE IF EXISTS table_not_exists;
Query OK, 0 rows affected, 1 warning (0.01 sec)

mysql> SHOW WARNINGS;
+-------+------+---------------------------------------+
| Level | Code | Message                               |
+-------+------+---------------------------------------+
| Note  | 1051 | Unknown table 'test.table_not_exists' |
+-------+------+---------------------------------------+
1 row in set (0.01 sec)

mysql> CREATE VIEW v1 AS SELECT 1;
Query OK, 0 rows affected (0.10 sec)

mysql> DROP TABLE v1;
Query OK, 0 rows affected (0.23 sec)
```
## MySQL compatibility

Currently, `RESTRICT` and `CASCADE` are only supported syntactically.
## See also

* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [SHOW CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table)
* [SHOW TABLES](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-tables)
