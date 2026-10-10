# DROP COLUMN syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-drop-column.md`
- Source Title: `DROP COLUMN | TiDB SQL Statement Reference`
- Source Heading Path: `DROP COLUMN | DROP COLUMN > Synopsis | DROP COLUMN > Examples | DROP COLUMN > MySQL compatibility | DROP COLUMN > See also`
- Source Line Ranges: `5-83`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `ddl`, `alter-table`, `drop-column`, `syntax`, `examples`, `mysql-compatibility`, `online-ddl`, `schema-change`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0573_4cdd46b789`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-drop-column.md#drop-column`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9baad7ce06fe78634c663eebcb4fc63f200a5a14576f33222fb83b65a0aa2f8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-column#drop-column
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-drop-column.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB ALTER TABLE DROP COLUMN syntax, online DDL behavior, examples of dropping a column, or the error shown for multi schema change when dropping multiple columns.
- Retrieval Keywords: DROP COLUMN, ALTER TABLE, DropColumnSpec, ALTER TABLE t1 DROP COLUMN col1, ALTER TABLE t1 DROP COLUMN col1, DROP COLUMN col2, ERROR 1105 (HY000): can't run multi schema change, online in TiDB, does not block read or write operations, IF EXISTS, RESTRICT, CASCADE, MySQL compatibility, Dropping primary key columns, composite index
- Follow-up Guidance: See also ADD COLUMN, SHOW CREATE TABLE, and CREATE TABLE.
- Classification Note: This is reference content because it defines the DROP COLUMN syntax, shows example SQL and output, and states MySQL compatibility limitations from the official documentation.

## Official Source Content

# DROP COLUMN

This statement drops a column from a specified table. `DROP COLUMN` is online in TiDB, which means that it does not block read or write operations.
## Synopsis

```ebnf+diagram
AlterTableStmt
         ::= 'ALTER' 'IGNORE'? 'TABLE' TableName DropColumnSpec ( ',' DropColumnSpec )*

DropColumnSpec
         ::= 'DROP' 'COLUMN'? 'IF EXISTS'? ColumnName ( 'RESTRICT' | 'CASCADE' )?

ColumnName
         ::= Identifier ( '.' Identifier ( '.' Identifier )? )?
```
## Examples

```sql
mysql> CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, col1 INT NOT NULL, col2 INT NOT NULL);
Query OK, 0 rows affected (0.12 sec)

mysql> INSERT INTO t1 (col1,col2) VALUES (1,1),(2,2),(3,3),(4,4),(5,5);
Query OK, 5 rows affected (0.02 sec)
Records: 5  Duplicates: 0  Warnings: 0

mysql> SELECT * FROM t1;
+----+------+------+
| id | col1 | col2 |
+----+------+------+
|  1 |    1 |    1 |
|  2 |    2 |    2 |
|  3 |    3 |    3 |
|  4 |    4 |    4 |
|  5 |    5 |    5 |
+----+------+------+
5 rows in set (0.01 sec)

mysql> ALTER TABLE t1 DROP COLUMN col1, DROP COLUMN col2;
ERROR 1105 (HY000): can't run multi schema change
mysql> SELECT * FROM t1;
+----+------+------+
| id | col1 | col2 |
+----+------+------+
|  1 |    1 |    1 |
|  2 |    2 |    2 |
|  3 |    3 |    3 |
|  4 |    4 |    4 |
|  5 |    5 |    5 |
+----+------+------+
5 rows in set (0.00 sec)

mysql> ALTER TABLE t1 DROP COLUMN col1;
Query OK, 0 rows affected (0.27 sec)

mysql> SELECT * FROM t1;
+----+------+
| id | col2 |
+----+------+
|  1 |    1 |
|  2 |    2 |
|  3 |    3 |
|  4 |    4 |
|  5 |    5 |
+----+------+
5 rows in set (0.00 sec)
```
## MySQL compatibility

* Dropping primary key columns or columns covered by the composite index is not supported.
## See also

* [ADD COLUMN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-column)
* [SHOW CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table)
* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
