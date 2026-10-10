# CREATE VIEW syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-view.md`
- Source Title: `CREATE VIEW | TiDB SQL Statement Reference`
- Source Heading Path: `CREATE VIEW | CREATE VIEW > Synopsis | CREATE VIEW > Examples | CREATE VIEW > MySQL compatibility | CREATE VIEW > See also`
- Source Line Ranges: `5-101`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `create view`, `views`, `syntax`, `examples`, `mysql compatibility`, `non-materialized views`, `create or replace`, `check option`, `algorithm`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0565_ca45b14238`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-view.md#create-view`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5465352408af156ed08da99abc918896ecd89f3a1b20aeef23ac6b2500362629`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-view#create-view
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-view.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB CREATE VIEW syntax, non-materialized view behavior, examples of querying a view, or MySQL compatibility limits for views.
- Retrieval Keywords: CREATE VIEW, CreateViewStmt, OR REPLACE, ALGORITHM, DEFINER, SQL SECURITY, VIEW, WITH CHECK OPTION, non-materialized views, internally rewrite the query, CREATE VIEW v1 AS SELECT * FROM t1 WHERE c1 > 2, insert into view v1 is not supported now, ALTER VIEW, MERGE algorithm, INSERT VIEW, UPDATE VIEW
- Follow-up Guidance: Related statements listed here are DROP VIEW, CREATE TABLE, SHOW CREATE TABLE, and DROP TABLE.
- Classification Note: This is reference content because it provides the CREATE VIEW grammar, SQL examples, and explicit MySQL compatibility notes such as unsupported INSERT VIEW, UPDATE VIEW, and ALTER VIEW behavior.

## Official Source Content

# CREATE VIEW

The `CREATE VIEW` statement saves a `SELECT` statement as a queryable object, similar to a table. Views in TiDB are non-materialized. This means that as a view is queried, TiDB will internally rewrite the query to combine the view definition with the SQL query.
## Synopsis

```ebnf+diagram
CreateViewStmt ::=
    'CREATE' OrReplace ViewAlgorithm ViewDefiner ViewSQLSecurity 'VIEW' ViewName ViewFieldList 'AS' CreateViewSelectOpt ViewCheckOption

OrReplace ::=
    ( 'OR' 'REPLACE' )?

ViewAlgorithm ::=
    ( 'ALGORITHM' '=' ( 'UNDEFINED' | 'MERGE' | 'TEMPTABLE' ) )?

ViewDefiner ::=
    ( 'DEFINER' '=' Username )?

ViewSQLSecurity ::=
    ( 'SQL' 'SECURITY' ( 'DEFINER' | 'INVOKER' ) )?

ViewName ::= TableName

ViewFieldList ::=
    ( '(' Identifier ( ',' Identifier )* ')' )?

ViewCheckOption ::=
    ( 'WITH' ( 'CASCADED' | 'LOCAL' ) 'CHECK' 'OPTION' )?
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

mysql> INSERT INTO t1 (c1) VALUES (6);
Query OK, 1 row affected (0.01 sec)

mysql> SELECT * FROM v1;
+----+----+
| id | c1 |
+----+----+
|  3 |  3 |
|  4 |  4 |
|  5 |  5 |
|  6 |  6 |
+----+----+
4 rows in set (0.00 sec)

mysql> INSERT INTO v1 (c1) VALUES (7);
ERROR 1105 (HY000): insert into view v1 is not supported now.
```
## MySQL compatibility

* Currently, any view in TiDB cannot be inserted or updated (that is, `INSERT VIEW` and `UPDATE VIEW` are not supported). `WITH CHECK OPTION` is only syntactically compatible but does not take effect.
* Currently, the view in TiDB does not support `ALTER VIEW`, but you can use `CREATE OR REPLACE` instead.
* Currently, the `ALGORITHM` field is only syntactically compatible in TiDB but does not take effect. TiDB currently only supports the MERGE algorithm.
## See also

* [DROP VIEW](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-view)
* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [SHOW CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table)
* [DROP TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-table)
