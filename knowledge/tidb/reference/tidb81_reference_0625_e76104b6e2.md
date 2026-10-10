# REPLACE statement syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-replace.md`
- Source Title: `REPLACE | TiDB SQL Statement Reference`
- Source Heading Path: `REPLACE | REPLACE > Synopsis | REPLACE > Examples | REPLACE > MySQL compatibility | REPLACE > See also`
- Source Line Ranges: `5-82`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `replace`, `sql-syntax`, `delete-insert-semantics`, `examples`, `mysql-compatibility`, `resource-control`, `statement-priority`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0625_e76104b6e2`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-replace.md#replace`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1328375a3987f2a9866c6aecdadf3ef93b48394ee31ba564c90d21de7f92776c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-replace#replace
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-replace.md

## Retrieval Guidance

- Use When: Use this when the question asks about the TiDB SQL `REPLACE` statement syntax, its combined `DELETE`+`INSERT` semantics, example behavior, or MySQL compatibility.
- Retrieval Keywords: REPLACE, REPLACE INTO, ReplaceIntoStmt, DELETE+INSERT, PriorityOpt, LOW_PRIORITY, HIGH_PRIORITY, DELAYED, PartitionNameListOpt, InsertValues, SET ColumnSetValue, REPLACE statement syntax, REPLACE examples, MySQL compatibility, statement priority, Resource Control
- Follow-up Guidance: The source also points to related statements: `DELETE`, `INSERT`, `SELECT`, and `UPDATE`, and notes that when Resource Control is enabled, statement priority (`PriorityOpt`) no longer takes effect.
- Classification Note: This is reference content because it defines the `REPLACE` statement grammar, documents exact syntax elements and options, and shows an official SQL example and compatibility note.

## Official Source Content

# REPLACE

The `REPLACE` statement is semantically a combined `DELETE`+`INSERT` statement. It can be used to simplify application code.
## Synopsis

```ebnf+diagram
ReplaceIntoStmt ::=
    'REPLACE' PriorityOpt IntoOpt TableName PartitionNameListOpt InsertValues

PriorityOpt ::=
    ( 'LOW_PRIORITY' | 'HIGH_PRIORITY' | 'DELAYED' )?

IntoOpt ::= 'INTO'?

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
```

> **Note:**
>
> Starting from v6.6.0, TiDB supports [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control). You can use this feature to execute SQL statements with different priorities in different resource groups. By configuring proper quotas and priorities for these resource groups, you can gain better scheduling control for SQL statements with different priorities. When resource control is enabled, statement priority (`PriorityOpt`) will no longer take effect. It is recommended that you use [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) to manage resource usage for different SQL statements.
## Examples

```sql
mysql> CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, c1 INT NOT NULL);
Query OK, 0 rows affected (0.12 sec)

mysql> INSERT INTO t1 (c1) VALUES (1), (2), (3);
Query OK, 3 rows affected (0.02 sec)
Records: 3  Duplicates: 0  Warnings: 0

mysql> SELECT * FROM t1;
+----+----+
| id | c1 |
+----+----+
|  1 |  1 |
|  2 |  2 |
|  3 |  3 |
+----+----+
3 rows in set (0.00 sec)

mysql> REPLACE INTO t1 (id, c1) VALUES(3, 99);
Query OK, 2 rows affected (0.01 sec)

mysql> SELECT * FROM t1;
+----+----+
| id | c1 |
+----+----+
|  1 |  1 |
|  2 |  2 |
|  3 | 99 |
+----+----+
3 rows in set (0.00 sec)
```
## MySQL compatibility

The `REPLACE` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [DELETE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-delete)
* [INSERT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-insert)
* [SELECT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select)
* [UPDATE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update)
