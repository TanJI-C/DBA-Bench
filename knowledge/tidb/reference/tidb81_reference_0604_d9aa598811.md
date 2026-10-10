# INSERT statement syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-insert.md`
- Source Title: `INSERT | TiDB SQL Statement Reference`
- Source Heading Path: `INSERT | INSERT > Synopsis | INSERT > Examples | INSERT > MySQL compatibility | INSERT > See also`
- Source Line Ranges: `5-111`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `insert`, `syntax`, `ebnf`, `examples`, `mysql-compatibility`, `resource-control`, `statement-priority`, `on-duplicate-key-update`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0604_d9aa598811`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-insert.md#insert`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c160acfb3ac51078c2fa9304adf826ecd889aaa5719362e597db627554dbfbba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-insert#insert
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-insert.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB `INSERT` statement syntax, examples of `VALUES`, `SELECT`, `SET`, `PARTITION`, or `ON DUPLICATE KEY UPDATE`, or wants the MySQL compatibility note for `INSERT`.
- Retrieval Keywords: INSERT, InsertIntoStmt, PriorityOpt, IgnoreOptional, IntoOpt, PartitionNameListOpt, InsertValues, OnDuplicateKeyUpdate, TableOptimizerHints, LOW_PRIORITY, HIGH_PRIORITY, DELAYED, IGNORE, INTO, PARTITION, VALUES, SELECT, UnionStmt, SET, ON DUPLICATE KEY UPDATE, INSERT INTO t1 VALUES (1), INSERT INTO t2 SELECT * FROM t1, INSERT INTO t2 VALUES (2),(3),(4), MySQL compatibility, Resource Control, statement priority
- Follow-up Guidance: The source also points to related SQL statements: `DELETE`, `SELECT`, `UPDATE`, and `REPLACE`.
- Classification Note: This is reference content because it provides the formal EBNF synopsis, concrete SQL examples, and a compatibility note for the `INSERT` statement.

## Official Source Content

# INSERT

This statement inserts new rows into a table.
## Synopsis

```ebnf+diagram
InsertIntoStmt ::=
    'INSERT' TableOptimizerHints PriorityOpt IgnoreOptional IntoOpt TableName PartitionNameListOpt InsertValues OnDuplicateKeyUpdate

TableOptimizerHints ::=
    hintComment?

PriorityOpt ::=
    ( 'LOW_PRIORITY' | 'HIGH_PRIORITY' | 'DELAYED' )?

IgnoreOptional ::=
    'IGNORE'?

IntoOpt  ::= 'INTO'?

TableName ::=
    Identifier ( '.' Identifier )?

PartitionNameListOpt ::=
    ( 'PARTITION' '(' Identifier ( ',' Identifier )* ')' )?

InsertValues ::=
    '(' ( ColumnNameListOpt ')' ( ValueSym ValuesList | SelectStmt | '(' SelectStmt ')' | UnionStmt ) | SelectStmt ')' )
|   ValueSym ValuesList
|   SelectStmt
|   UnionStmt
|   'SET' ColumnSetValue? ( ',' ColumnSetValue )*

OnDuplicateKeyUpdate ::=
    ( 'ON' 'DUPLICATE' 'KEY' 'UPDATE' AssignmentList )?
```

> **Note:**
>
> Starting from v6.6.0, TiDB supports [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control). You can use this feature to execute SQL statements with different priorities in different resource groups. By configuring proper quotas and priorities for these resource groups, you can gain better scheduling control for SQL statements with different priorities. When resource control is enabled, statement priority (`PriorityOpt`) will no longer take effect. It is recommended that you use [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) to manage resource usage for different SQL statements.
## Examples

```sql
mysql> CREATE TABLE t1 (a INT);
Query OK, 0 rows affected (0.11 sec)

mysql> CREATE TABLE t2 LIKE t1;
Query OK, 0 rows affected (0.11 sec)

mysql> INSERT INTO t1 VALUES (1);
Query OK, 1 row affected (0.02 sec)

mysql> INSERT INTO t1 (a) VALUES (1);
Query OK, 1 row affected (0.01 sec)

mysql> INSERT INTO t2 SELECT * FROM t1;
Query OK, 2 rows affected (0.01 sec)
Records: 2  Duplicates: 0  Warnings: 0

mysql> SELECT * FROM t1;
+------+
| a    |
+------+
|    1 |
|    1 |
+------+
2 rows in set (0.00 sec)

mysql> SELECT * FROM t2;
+------+
| a    |
+------+
|    1 |
|    1 |
+------+
2 rows in set (0.00 sec)

mysql> INSERT INTO t2 VALUES (2),(3),(4);
Query OK, 3 rows affected (0.02 sec)
Records: 3  Duplicates: 0  Warnings: 0

mysql> SELECT * FROM t2;
+------+
| a    |
+------+
|    1 |
|    1 |
|    2 |
|    3 |
|    4 |
+------+
5 rows in set (0.00 sec)
```
## MySQL compatibility

The `INSERT` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [DELETE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-delete)
* [SELECT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select)
* [UPDATE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update)
* [REPLACE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-replace)
