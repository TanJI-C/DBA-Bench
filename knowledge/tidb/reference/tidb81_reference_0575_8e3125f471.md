# DROP INDEX syntax, example, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-drop-index.md`
- Source Title: `DROP INDEX | TiDB SQL Statement Reference`
- Source Heading Path: `DROP INDEX | DROP INDEX > Synopsis | DROP INDEX > Examples | DROP INDEX > MySQL compatibility | DROP INDEX > See also`
- Source Line Ranges: `5-69`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `drop-index`, `sql-syntax`, `examples`, `mysql-compatibility`, `clustered-indexes`, `index-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0575_8e3125f471`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-drop-index.md#drop-index`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `329779929114766012bede155297098ff472d9ecf1eb479a82bd3fe577d1d2e7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-index#drop-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-drop-index.md

## Retrieval Guidance

- Use When: Use this content when looking for the TiDB SQL syntax, example, or compatibility notes for removing an index from a table with DROP INDEX.
- Retrieval Keywords: DROP INDEX, DropIndexStmt, IF EXISTS, ON TableName, IndexLockAndAlgorithmOpt, DROP INDEX c1 ON t1, CREATE INDEX c1 ON t1 (c1), EXPLAIN SELECT * FROM t1 WHERE c1 = 3, IndexRangeScan_5, TableFullScan_5, table:t1, index:c1(c1), marking space as free in TiKV, dropping the primary key of the CLUSTERED type is not supported, clustered index, SHOW INDEXES, CREATE INDEX, ADD INDEX, RENAME INDEX, ALTER INDEX
- Follow-up Guidance: The source also points to SHOW INDEXES, CREATE INDEX, ADD INDEX, RENAME INDEX, and ALTER INDEX as related SQL statements.
- Classification Note: This is reference content because it defines the DROP INDEX statement syntax, shows a SQL example with EXPLAIN output, and states a MySQL compatibility limitation for CLUSTERED primary keys.

## Official Source Content

# DROP INDEX

This statement removes an index from a specified table, marking space as free in TiKV.
## Synopsis

```ebnf+diagram
DropIndexStmt ::=
    "DROP" "INDEX" IfExists Identifier "ON" TableName IndexLockAndAlgorithmOpt

IfExists ::=
    ( 'IF' 'EXISTS' )?

IndexLockAndAlgorithmOpt ::=
    ( LockClause AlgorithmClause? | AlgorithmClause LockClause? )?
```
## Examples

```sql
mysql> CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, c1 INT NOT NULL);
Query OK, 0 rows affected (0.10 sec)

mysql> INSERT INTO t1 (c1) VALUES (1),(2),(3),(4),(5);
Query OK, 5 rows affected (0.02 sec)
Records: 5  Duplicates: 0  Warnings: 0

mysql> EXPLAIN SELECT * FROM t1 WHERE c1 = 3;
+-------------------------+----------+-----------+---------------+--------------------------------+
| id                      | estRows  | task      | access object | operator info                  |
+-------------------------+----------+-----------+---------------+--------------------------------+
| TableReader_7           | 10.00    | root      |               | data:Selection_6               |
| └─Selection_6           | 10.00    | cop[tikv] |               | eq(test.t1.c1, 3)              |
|   └─TableFullScan_5     | 10000.00 | cop[tikv] | table:t1      | keep order:false, stats:pseudo |
+-------------------------+----------+-----------+---------------+--------------------------------+
3 rows in set (0.00 sec)

mysql> CREATE INDEX c1 ON t1 (c1);
Query OK, 0 rows affected (0.30 sec)

mysql> EXPLAIN SELECT * FROM t1 WHERE c1 = 3;
+------------------------+---------+-----------+------------------------+---------------------------------------------+
| id                     | estRows | task      | access object          | operator info                               |
+------------------------+---------+-----------+------------------------+---------------------------------------------+
| IndexReader_6          | 0.01    | root      |                        | index:IndexRangeScan_5                      |
| └─IndexRangeScan_5     | 0.01    | cop[tikv] | table:t1, index:c1(c1) | range:[3,3], keep order:false, stats:pseudo |
+------------------------+---------+-----------+------------------------+---------------------------------------------+
2 rows in set (0.00 sec)

mysql> DROP INDEX c1 ON t1;
Query OK, 0 rows affected (0.30 sec)
```
## MySQL compatibility

* Dropping the primary key of the `CLUSTERED` type is not supported. For more details about the primary key of the `CLUSTERED` type, refer to [clustered index](https://docs.pingcap.com/tidb/stable/clustered-indexes).
## See also

* [SHOW INDEXES](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-indexes)
* [CREATE INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index)
* [ADD INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index)
* [RENAME INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rename-index)
* [ALTER INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-index)
