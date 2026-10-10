# ADD INDEX syntax, examples, compatibility, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-add-index.md`
- Source Title: `ADD INDEX | TiDB SQL Statement Reference`
- Source Heading Path: `ADD INDEX | ADD INDEX > Synopsis | ADD INDEX > Examples | ADD INDEX > MySQL compatibility | ADD INDEX > See also`
- Source Line Ranges: `5-104`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `shared`
- Topic Tags: `add-index`, `alter-table`, `ddl`, `online-ddl`, `syntax`, `examples`, `mysql-compatibility`, `index-types`, `fulltext`, `cluster-upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0504_a25bb24e21`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-add-index.md#add-index`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3968d2f3603d847645ec9835962c76e223474438a31332b7a9e24f14ed892d98`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index#add-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-add-index.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB SQL reference for ALTER TABLE ... ADD INDEX syntax, online DDL behavior, examples, and MySQL compatibility limits for index types and related statements.
- Retrieval Keywords: ALTER TABLE ADD INDEX, ADD INDEX, AddIndexSpec, IndexPartSpecification, IndexOption, IndexType, ALTER TABLE t1 ADD INDEX (c1), online in TiDB, reads or writes to the table are blocked, ADMIN SHOW DDL, ADMIN CANCEL DDL, DXF, TiDB Distributed eXecution Framework, FULLTEXT, SPATIAL indexes are not supported, descending indexes are not supported, HASH BTREE RTREE, CLUSTERED type primary key, EXPLAIN SELECT * FROM t1 WHERE c1 = 3, CREATE INDEX, DROP INDEX, RENAME INDEX, ALTER INDEX
- Follow-up Guidance: The source also points to related material including Index Selection, Wrong Index Solution, CREATE INDEX, DROP INDEX, RENAME INDEX, ALTER INDEX, ADD COLUMN, CREATE TABLE, EXPLAIN, and TiDB Distributed eXecution Framework (DXF).
- Classification Note: This is a SQL reference chunk because it defines the ADD INDEX statement with formal syntax, executable examples, compatibility notes, and links to related SQL statements.

## Official Source Content

# ADD INDEX

The `ALTER TABLE.. ADD INDEX` statement adds an index to an existing table. This operation is online in TiDB, which means that neither reads or writes to the table are blocked by adding an index.

> **Tip:**
>
> The [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework) can be used to speed up the operation of this statement.

> **Warning:**
>
> - **DO NOT** upgrade a TiDB cluster when a DDL statement is being executed in the cluster (usually for the time-consuming DDL statements such as `ADD INDEX` and the column type changes).
> - Before the upgrade, it is recommended to use the [`ADMIN SHOW DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl) command to check whether the TiDB cluster has an ongoing DDL job. If the cluster has a DDL job, to upgrade the cluster, wait until the DDL execution is finished or use the [`ADMIN CANCEL DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl) command to cancel the DDL job before you upgrade the cluster.
> - In addition, during the cluster upgrade, **DO NOT** execute any DDL statement. Otherwise, the issue of undefined behavior might occur.
>
> When you upgrade TiDB from v7.1.0 to a later version, you can ignore the preceding limitations. For details, see [the limitations of TiDB smooth upgrade](https://docs.pingcap.com/tidb/stable/smooth-upgrade-tidb).
## Synopsis

```ebnf+diagram
AlterTableStmt
         ::= 'ALTER' 'IGNORE'? 'TABLE' TableName AddIndexSpec ( ',' AddIndexSpec )*

AddIndexSpec
         ::= 'ADD' ( ( 'PRIMARY' 'KEY' | ( 'KEY' | 'INDEX' ) 'IF NOT EXISTS'? | 'UNIQUE' ( 'KEY' | 'INDEX' )? ) ( ( Identifier? 'USING' | Identifier 'TYPE' ) IndexType )? | 'FULLTEXT' ( 'KEY' | 'INDEX' )? IndexName ) '(' IndexPartSpecification ( ',' IndexPartSpecification )* ')' IndexOption*

IndexPartSpecification
         ::= ( ColumnName ( '(' LengthNum ')' )? | '(' Expression ')' ) ( 'ASC' | 'DESC' )

IndexOption
         ::= 'KEY_BLOCK_SIZE' '='? LengthNum
           | IndexType
           | 'WITH' 'PARSER' Identifier
           | 'COMMENT' stringLit
           | 'VISIBLE'
           | 'INVISIBLE'

IndexType
         ::= 'BTREE'
           | 'HASH'
           | 'RTREE'
```
## Examples

```sql
mysql> CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, c1 INT NOT NULL);
Query OK, 0 rows affected (0.11 sec)

mysql> INSERT INTO t1 (c1) VALUES (1),(2),(3),(4),(5);
Query OK, 5 rows affected (0.03 sec)
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

mysql> ALTER TABLE t1 ADD INDEX (c1);
Query OK, 0 rows affected (0.30 sec)

mysql> EXPLAIN SELECT * FROM t1 WHERE c1 = 3;
+------------------------+---------+-----------+------------------------+---------------------------------------------+
| id                     | estRows | task      | access object          | operator info                               |
+------------------------+---------+-----------+------------------------+---------------------------------------------+
| IndexReader_6          | 0.01    | root      |                        | index:IndexRangeScan_5                      |
| └─IndexRangeScan_5     | 0.01    | cop[tikv] | table:t1, index:c1(c1) | range:[3,3], keep order:false, stats:pseudo |
+------------------------+---------+-----------+------------------------+---------------------------------------------+
2 rows in set (0.00 sec)
```
## MySQL compatibility

* TiDB accepts index types such as `HASH`, `BTREE` and `RTREE` in syntax for compatibility with MySQL, but ignores them.
* `SPATIAL` indexes are not supported.
* TiDB supports parsing the `FULLTEXT` syntax but does not support using the `FULLTEXT` indexes.
* Descending indexes are not supported (similar to MySQL 5.7).
* Adding the primary key of the `CLUSTERED` type to a table is not supported. For more details about the primary key of the `CLUSTERED` type, refer to [clustered index](https://docs.pingcap.com/tidb/stable/clustered-indexes).
## See also

* [Index Selection](https://docs.pingcap.com/tidb/stable/choose-index)
* [Wrong Index Solution](https://docs.pingcap.com/tidb/stable/wrong-index-solution)
* [CREATE INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index)
* [DROP INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-index)
* [RENAME INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rename-index)
* [ALTER INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-index)
* [ADD COLUMN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-column)
* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [EXPLAIN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain)
* [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework)
