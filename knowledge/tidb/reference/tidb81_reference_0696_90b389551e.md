# TRUNCATE statement syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-truncate.md`
- Source Title: `TRUNCATE | TiDB SQL Statement Reference`
- Source Heading Path: `TRUNCATE | TRUNCATE > Synopsis | TRUNCATE > Examples | TRUNCATE > MySQL compatibility | TRUNCATE > See also`
- Source Line Ranges: `5-67`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `truncate`, `sql-syntax`, `table-data-removal`, `non-transactional`, `mysql-compatibility`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0696_90b389551e`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-truncate.md#truncate`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e09deefdff3c3e6cb56097e9dc6d606e9ff91169703198748362f369112a5395`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-truncate#truncate
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-truncate.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the TiDB SQL syntax and behavior of TRUNCATE for removing all rows from a table while keeping the previous table definition.
- Retrieval Keywords: TRUNCATE, TRUNCATE TABLE, TruncateTableStmt, TableName, non-transactional, DROP TABLE + CREATE TABLE, TRUNCATE t1, TRUNCATE TABLE t1, MySQL compatibility
- Follow-up Guidance: The source also points to related statements: DROP TABLE, DELETE, CREATE TABLE, and SHOW CREATE TABLE.
- Classification Note: This is reference content because it defines TRUNCATE statement syntax, describes its semantics, shows example SQL usage, and notes MySQL compatibility.

## Official Source Content

# TRUNCATE

The `TRUNCATE` statement removes all data from the table in a non-transactional way. `TRUNCATE` can be thought of as semantically the same as `DROP TABLE` + `CREATE TABLE` with the previous definition.

Both `TRUNCATE TABLE tableName` and `TRUNCATE tableName` are valid syntax.
## Synopsis

```ebnf+diagram
TruncateTableStmt ::=
    "TRUNCATE" ( "TABLE" )? TableName

TableName ::=
    (Identifier ".")? Identifier
```
## Examples

```sql
mysql> CREATE TABLE t1 (a INT NOT NULL PRIMARY KEY);
Query OK, 0 rows affected (0.11 sec)

mysql> INSERT INTO t1 VALUES (1),(2),(3),(4),(5);
Query OK, 5 rows affected (0.01 sec)
Records: 5  Duplicates: 0  Warnings: 0

mysql> SELECT * FROM t1;
+---+
| a |
+---+
| 1 |
| 2 |
| 3 |
| 4 |
| 5 |
+---+
5 rows in set (0.00 sec)

mysql> TRUNCATE t1;
Query OK, 0 rows affected (0.11 sec)

mysql> SELECT * FROM t1;
Empty set (0.00 sec)

mysql> INSERT INTO t1 VALUES (1),(2),(3),(4),(5);
Query OK, 5 rows affected (0.01 sec)
Records: 5  Duplicates: 0  Warnings: 0

mysql> TRUNCATE TABLE t1;
Query OK, 0 rows affected (0.11 sec)
```
## MySQL compatibility

The `TRUNCATE` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [DROP TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-table)
* [DELETE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-delete)
* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [SHOW CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table)
