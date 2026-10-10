# DELETE statement syntax, example, compatibility, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-delete.md`
- Source Title: `DELETE | TiDB SQL Statement Reference`
- Source Heading Path: `DELETE | DELETE > Synopsis | DELETE > Examples | DELETE > MySQL compatibility | DELETE > See also`
- Source Line Ranges: `5-63`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `delete`, `dml`, `syntax`, `examples`, `mysql-compatibility`, `see-also`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0567_92c353aec1`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-delete.md#delete`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `52ac66f44d9d7c59adac69d0efabc03bde28c94c2f1b27ab34f6222ae1cd30b4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-delete#delete
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-delete.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB SQL reference for the DELETE statement, including syntax, a basic WHERE example, MySQL compatibility, or related DML statements.
- Retrieval Keywords: DELETE, DeleteFromStmt, DELETE FROM, TableOptimizerHints, PriorityOpt, QuickOptional, IgnoreOptional, TableName, TableAliasRefList, USING, WhereClauseOptional, OrderByOptional, LimitClause, DELETE FROM t1 WHERE id = 4, MySQL compatibility, INSERT, SELECT, UPDATE, REPLACE
- Follow-up Guidance: The source also points to related statements: INSERT, SELECT, UPDATE, and REPLACE.
- Classification Note: This is reference content because it defines the DELETE statement syntax, shows a concrete example, states MySQL compatibility, and lists related SQL statements.

## Official Source Content

# DELETE

The `DELETE` statement removes rows from a specified table.
## Synopsis

```ebnf+diagram
DeleteFromStmt ::=
    'DELETE' TableOptimizerHints PriorityOpt QuickOptional IgnoreOptional ( 'FROM' ( TableName TableAsNameOpt IndexHintListOpt WhereClauseOptional OrderByOptional LimitClause | TableAliasRefList 'USING' TableRefs WhereClauseOptional ) | TableAliasRefList 'FROM' TableRefs WhereClauseOptional )
```
## Examples

```sql
mysql> CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, c1 INT NOT NULL);
Query OK, 0 rows affected (0.11 sec)

mysql> INSERT INTO t1 (c1) VALUES (1),(2),(3),(4),(5);
Query OK, 5 rows affected (0.03 sec)
Records: 5  Duplicates: 0  Warnings: 0

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

mysql> DELETE FROM t1 WHERE id = 4;
Query OK, 1 row affected (0.02 sec)

mysql> SELECT * FROM t1;
+----+----+
| id | c1 |
+----+----+
|  1 |  1 |
|  2 |  2 |
|  3 |  3 |
|  5 |  5 |
+----+----+
4 rows in set (0.00 sec)
```
## MySQL compatibility

The `DELETE` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [INSERT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-insert)
* [SELECT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select)
* [UPDATE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update)
* [REPLACE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-replace)
