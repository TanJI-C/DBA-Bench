# SHOW WARNINGS syntax, examples, and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-warnings.md`
- Source Title: `SHOW WARNINGS | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW WARNINGS | SHOW WARNINGS > Synopsis | SHOW WARNINGS > Examples | SHOW WARNINGS > MySQL compatibility | SHOW WARNINGS > See also`
- Source Line Ranges: `5-83`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show warnings`, `sql mode`, `warnings`, `mysql compatibility`, `syntax`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0688_5e45cfec79`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-warnings.md#show-warnings`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a610d32698c9974c26c34e20adad5af0c496791d76a04177673203d18d7aec14`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-warnings#show-warnings
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-warnings.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax and behavior of `SHOW WARNINGS` for warnings produced by previously executed statements in the current client connection, including how `sql_mode` affects errors versus warnings.
- Retrieval Keywords: SHOW WARNINGS, ShowWarningsStmt, SHOW WARNINGS syntax, current client connection, sql_mode, warnings, MySQL compatibility, Division by 0, Warning 1365, Out of range value for column, ERROR 1264 (22003), constant -1 overflows int, Warning 1690, SET sql_mode=''
- Follow-up Guidance: The source also points to `SHOW ERRORS` in the See also section.
- Classification Note: This is a SQL reference chunk because it defines the `SHOW WARNINGS` statement syntax, provides SQL examples, and states TiDB MySQL compatibility.

## Official Source Content

# SHOW WARNINGS

This statement shows a list of warnings that occurred for previously executed statements in the current client connection. As in MySQL, the `sql_mode` impacts which statements will cause errors vs. warnings considerably.
## Synopsis

```ebnf+diagram
ShowWarningsStmt ::=
    "SHOW" "WARNINGS"
```
## Examples

```sql
mysql> CREATE TABLE t1 (a INT UNSIGNED);
Query OK, 0 rows affected (0.11 sec)

mysql> INSERT INTO t1 VALUES (0);
Query OK, 1 row affected (0.02 sec)

mysql> SELECT 1/a FROM t1;
+------+
| 1/a  |
+------+
| NULL |
+------+
1 row in set, 1 warning (0.00 sec)

mysql> SHOW WARNINGS;
+---------+------+---------------+
| Level   | Code | Message       |
+---------+------+---------------+
| Warning | 1365 | Division by 0 |
+---------+------+---------------+
1 row in set (0.00 sec)

mysql> INSERT INTO t1 VALUES (-1);
ERROR 1264 (22003): Out of range value for column 'a' at row 1
mysql> SELECT * FROM t1;
+------+
| a    |
+------+
|    0 |
+------+
1 row in set (0.00 sec)

mysql> SET sql_mode='';
Query OK, 0 rows affected (0.00 sec)

mysql> INSERT INTO t1 VALUES (-1);
Query OK, 1 row affected, 1 warning (0.01 sec)

mysql> SHOW WARNINGS;
+---------+------+---------------------------+
| Level   | Code | Message                   |
+---------+------+---------------------------+
| Warning | 1690 | constant -1 overflows int |
+---------+------+---------------------------+
1 row in set (0.00 sec)

mysql> SELECT * FROM t1;
+------+
| a    |
+------+
|    0 |
|    0 |
+------+
2 rows in set (0.00 sec)

```
## MySQL compatibility

The `SHOW WARNINGS` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [SHOW ERRORS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-errors)
