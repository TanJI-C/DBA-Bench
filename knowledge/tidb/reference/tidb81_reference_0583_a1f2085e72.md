# DROP VIEW syntax, example, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-drop-view.md`
- Source Title: `DROP VIEW | TiDB SQL Statement Reference`
- Source Heading Path: `DROP VIEW | DROP VIEW > Synopsis | DROP VIEW > Examples | DROP VIEW > MySQL compatibility | DROP VIEW > See also`
- Source Line Ranges: `5-81`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `drop-view`, `views`, `sql-syntax`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0583_a1f2085e72`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-drop-view.md#drop-view`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1282f613c858bcf18db30d1cd6e32e130abe02dc4f651b11196d824afa10d025`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-view#drop-view
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-drop-view.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for the TiDB SQL syntax, example behavior, or MySQL compatibility of dropping a view from the currently selected database.
- Retrieval Keywords: DROP VIEW, DropViewStmt, DROP VIEW IF EXISTS, TableNameList, RestrictOrCascadeOpt, TableName, drop a view object, does not affect any base tables, DROP VIEW v1, MySQL compatibility, CREATE VIEW, DROP TABLE
- Follow-up Guidance: The source also links to related statements CREATE VIEW and DROP TABLE.
- Classification Note: This is reference content because it defines the DROP VIEW statement syntax, shows an example, and states MySQL compatibility information from the official SQL documentation.

## Official Source Content

# DROP VIEW

This statement drops a view object from the currently selected database. It does not affect any base tables that a view references.
## Synopsis

```ebnf+diagram
DropViewStmt ::=
    'DROP' 'VIEW' ( 'IF' 'EXISTS' )? TableNameList RestrictOrCascadeOpt

TableNameList ::=
    TableName ( ',' TableName )*

TableName ::=
    Identifier ('.' Identifier)?
```
## Examples

```sql
mysql> CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, c1 INT NOT NULL);
Query OK, 0 rows affected (0.11 sec)

mysql> INSERT INTO t1 (c1) VALUES (1),(2),(3),(4),(5);
Query OK, 5 rows affected (0.03 sec)
Records: 5  Duplicates: 0  Warnings: 0

mysql> CREATE VIEW v1 AS SELECT * FROM t1 WHERE c1 > 2;
Query OK, 0 rows affected (0.11 sec)

mysql> SELECT * FROM t1;
+----+----+
| id | c1 |
+----+----+
|  1 |  1 |
|  2 |  2 |
|  3 |  3 |
|  4 |  4 |
|  5 |  5 |
+----+----+
5 rows in set (0.00 sec)

mysql> SELECT * FROM v1;
+----+----+
| id | c1 |
+----+----+
|  3 |  3 |
|  4 |  4 |
|  5 |  5 |
+----+----+
3 rows in set (0.00 sec)

mysql> DROP VIEW v1;
Query OK, 0 rows affected (0.23 sec)

mysql> SELECT * FROM t1;
+----+----+
| id | c1 |
+----+----+
|  1 |  1 |
|  2 |  2 |
|  3 |  3 |
|  4 |  4 |
|  5 |  5 |
+----+----+
5 rows in set (0.00 sec)
```
## MySQL compatibility

The `DROP VIEW` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [CREATE VIEW](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-view)
* [DROP TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-table)
