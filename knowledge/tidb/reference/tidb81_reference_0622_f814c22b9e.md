# RENAME INDEX syntax, example, compatibility, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-rename-index.md`
- Source Title: `RENAME INDEX | TiDB SQL Statement Reference`
- Source Heading Path: `RENAME INDEX | RENAME INDEX > Synopsis | RENAME INDEX > Examples | RENAME INDEX > MySQL compatibility | RENAME INDEX > See also`
- Source Line Ranges: `5-62`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `rename-index`, `alter-table`, `index-management`, `syntax`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0622_f814c22b9e`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-rename-index.md#rename-index`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `56e3f13a8bf30e25c4d054b1160cc776fa9ac1ea8fa2bd13c6b3616601d02088`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rename-index#rename-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-rename-index.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB syntax, example, or compatibility details for renaming an existing index with ALTER TABLE .. RENAME INDEX.
- Retrieval Keywords: ALTER TABLE .. RENAME INDEX, RENAME INDEX, RENAME KEY, RenameIndexSpec, ALTER TABLE t1 RENAME INDEX col1 TO c1, SHOW CREATE TABLE, CREATE INDEX, DROP INDEX, SHOW INDEXES, ALTER INDEX, instant, meta data change, MySQL compatibility
- Follow-up Guidance: The source also points to related statements: SHOW CREATE TABLE, CREATE INDEX, DROP INDEX, SHOW INDEXES, and ALTER INDEX.
- Classification Note: This is reference content because it defines the synopsis, shows a SQL example, states that the operation is instant and only changes meta data, and notes MySQL compatibility.

## Official Source Content

# RENAME INDEX

The statement `ALTER TABLE .. RENAME INDEX` renames an existing index to a new name. This operation is instant in TiDB, and requires only a meta data change.
## Synopsis

```ebnf+diagram
AlterTableStmt
         ::= 'ALTER' 'IGNORE'? 'TABLE' TableName RenameIndexSpec ( ',' RenameIndexSpec )*

RenameIndexSpec
         ::= 'RENAME' ( 'KEY' | 'INDEX' ) Identifier 'TO' Identifier
```
## Examples

```sql
mysql> CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, c1 INT NOT NULL, INDEX col1 (c1));
Query OK, 0 rows affected (0.11 sec)

mysql> SHOW CREATE TABLE t1\G
*************************** 1. row ***************************
       Table: t1
Create Table: CREATE TABLE `t1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `c1` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `col1` (`c1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
1 row in set (0.00 sec)

mysql> ALTER TABLE t1 RENAME INDEX col1 TO c1;
Query OK, 0 rows affected (0.09 sec)

mysql> SHOW CREATE TABLE t1\G
*************************** 1. row ***************************
       Table: t1
Create Table: CREATE TABLE `t1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `c1` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `c1` (`c1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
1 row in set (0.00 sec)
```
## MySQL compatibility

The `RENAME INDEX` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [SHOW CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table)
* [CREATE INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index)
* [DROP INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-index)
* [SHOW INDEXES](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-indexes)
* [ALTER INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-index)
