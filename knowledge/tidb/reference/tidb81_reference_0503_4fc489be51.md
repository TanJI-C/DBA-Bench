# ADD COLUMN statement syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-add-column.md`
- Source Title: `ADD COLUMN | TiDB SQL Statement Reference`
- Source Heading Path: `ADD COLUMN | ADD COLUMN > Synopsis | ADD COLUMN > Examples | ADD COLUMN > MySQL compatibility | ADD COLUMN > See also`
- Source Line Ranges: `5-95`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `alter-table`, `add-column`, `ddl`, `syntax`, `examples`, `mysql-compatibility`, `online-ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0503_4fc489be51`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-add-column.md#add-column`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `84118eb369b06d62912a0c9acb62a970214f6c93a901b9029d322a87220f6585`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-column#add-column
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-add-column.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB syntax, examples, online DDL behavior, or MySQL compatibility notes for ALTER TABLE ADD COLUMN.
- Retrieval Keywords: ALTER TABLE.. ADD COLUMN, ALTER TABLE ADD COLUMN, ADD COLUMN, AddColumnSpec, IF NOT EXISTS, FIRST, AFTER ColumnName, online in TiDB, neither reads or writes to the table are blocked, adding a column, ALTER TABLE t1 ADD COLUMN c1 INT NOT NULL, ALTER TABLE t1 ADD c2 INT NOT NULL AFTER c1, PRIMARY KEY not supported, AUTO_INCREMENT not supported, generated column limitations, MySQL compatibility
- Follow-up Guidance: The source also points to ADD INDEX, CREATE TABLE, and generated column limitations for related details.
- Classification Note: This is reference content because it provides the formal synopsis, SQL examples, and explicit compatibility limitations for the ADD COLUMN statement.

## Official Source Content

# ADD COLUMN

The `ALTER TABLE.. ADD COLUMN` statement adds a column to an existing table. This operation is online in TiDB, which means that neither reads or writes to the table are blocked by adding a column.
## Synopsis

```ebnf+diagram
AlterTableStmt
         ::= 'ALTER' 'IGNORE'? 'TABLE' TableName AddColumnSpec ( ',' AddColumnSpec )*

TableName ::=
    Identifier ('.' Identifier)?

AddColumnSpec
         ::= 'ADD' 'COLUMN' 'IF NOT EXISTS'? ColumnName ColumnType ColumnOption+ ( 'FIRST' | 'AFTER' ColumnName )?

ColumnType
         ::= NumericType
           | StringType
           | DateAndTimeType
           | 'SERIAL'

ColumnOption
         ::= 'NOT'? 'NULL'
           | 'AUTO_INCREMENT'
           | 'PRIMARY'? 'KEY' ( 'CLUSTERED' | 'NONCLUSTERED' )?
           | 'UNIQUE' 'KEY'?
           | 'DEFAULT' ( NowSymOptionFraction | SignedLiteral | NextValueForSequence )
           | 'SERIAL' 'DEFAULT' 'VALUE'
           | 'ON' 'UPDATE' NowSymOptionFraction
           | 'COMMENT' stringLit
           | ( 'CONSTRAINT' Identifier? )? 'CHECK' '(' Expression ')' ( 'NOT'? ( 'ENFORCED' | 'NULL' ) )?
           | 'GENERATED' 'ALWAYS' 'AS' '(' Expression ')' ( 'VIRTUAL' | 'STORED' )?
           | 'REFERENCES' TableName ( '(' IndexPartSpecificationList ')' )? Match? OnDeleteUpdateOpt
           | 'COLLATE' CollationName
           | 'COLUMN_FORMAT' ColumnFormat
           | 'STORAGE' StorageMedia
           | 'AUTO_RANDOM' ( '(' LengthNum ')' )?
```
## Examples

```sql
mysql> CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT);
Query OK, 0 rows affected (0.11 sec)

mysql> INSERT INTO t1 VALUES (NULL);
Query OK, 1 row affected (0.02 sec)

mysql> SELECT * FROM t1;
+----+
| id |
+----+
|  1 |
+----+
1 row in set (0.00 sec)

mysql> ALTER TABLE t1 ADD COLUMN c1 INT NOT NULL;
Query OK, 0 rows affected (0.28 sec)

mysql> SELECT * FROM t1;
+----+----+
| id | c1 |
+----+----+
|  1 |  0 |
+----+----+
1 row in set (0.00 sec)

mysql> ALTER TABLE t1 ADD c2 INT NOT NULL AFTER c1;
Query OK, 0 rows affected (0.28 sec)

mysql> SELECT * FROM t1;
+----+----+----+
| id | c1 | c2 |
+----+----+----+
|  1 |  0 |  0 |
+----+----+----+
1 row in set (0.00 sec)
```
## MySQL compatibility

* Adding a new column and setting it to the `PRIMARY KEY` is not supported.
* Adding a new column and setting it to `AUTO_INCREMENT` is not supported.
* There are limitations on adding generated columns, refer to: [generated column limitations](https://docs.pingcap.com/tidb/stable/generated-columns#limitations).
## See also

* [ADD INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index)
* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
