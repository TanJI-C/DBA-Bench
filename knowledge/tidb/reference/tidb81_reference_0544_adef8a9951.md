# CHANGE COLUMN syntax, examples, and compatibility limits

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-change-column.md`
- Source Title: `CHANGE COLUMN | TiDB SQL Statement Reference`
- Source Heading Path: `CHANGE COLUMN | CHANGE COLUMN > Synopsis | CHANGE COLUMN > Examples | CHANGE COLUMN > MySQL compatibility | CHANGE COLUMN > See also`
- Source Line Ranges: `5-162`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `alter-table`, `change-column`, `ddl`, `column-rename`, `column-type-change`, `syntax`, `examples`, `mysql-compatibility`, `limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0544_adef8a9951`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-change-column.md#change-column`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b0ae6cc1c5ff5ab022fd729d4723a161a8de6ce6041f10a09347315b8118eeef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-column#change-column
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-change-column.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB ALTER TABLE CHANGE COLUMN syntax, examples of renaming a column or changing it to a compatible type, and documented compatibility limits or errors for unsupported type changes.
- Retrieval Keywords: ALTER TABLE .. CHANGE COLUMN, CHANGE COLUMN syntax, ChangeColumnSpec, ALTER TABLE t1 CHANGE col1 col2 INT, ALTER TABLE t1 CHANGE col2 col3 BIGINT, ALGORITHM=INSTANT, can't run multi schema change, ERROR 1105 (HY000), ERROR 8200 (HY000): Unsupported modify column: column has primary key flag, ERROR 8200 (HY000): Unsupported modify column: table is partition table, ERROR 8200 (HY000): Unsupported modify column: column is generated, ERROR 8200 (HY000): Unsupported modify column: change from original type decimal(13,7) to datetime is currently unsupported yet, Reorg data type, VARCHAR to BIGINT, DECIMAL precision, VARCHAR(10) to VARCHAR(5), MySQL compatibility, partitioned tables, generated columns, CAST function behavior between TiDB and MySQL
- Follow-up Guidance: The source also points to related statements CREATE TABLE, SHOW CREATE TABLE, ADD COLUMN, DROP COLUMN, and MODIFY COLUMN.
- Classification Note: This is reference content because it defines the CHANGE COLUMN grammar, shows exact SQL examples and returned errors, and lists explicit MySQL compatibility limitations from the official documentation.

## Official Source Content

# CHANGE COLUMN

The `ALTER TABLE.. CHANGE COLUMN` statement changes a column on an existing table. The change can include both renaming the column, and changing the data type to a compatible type.

Since v5.1.0, TiDB has supported changing the Reorg data type, including but not limited to:

- Changing `VARCHAR` to `BIGINT`
- Modifying the `DECIMAL` precision
- Compressing the length of `VARCHAR(10)` to `VARCHAR(5)`
## Synopsis

```ebnf+diagram
AlterTableStmt
         ::= 'ALTER' 'IGNORE'? 'TABLE' TableName ChangeColumnSpec ( ',' ChangeColumnSpec )*

ChangeColumnSpec
         ::= 'CHANGE' ColumnKeywordOpt 'IF EXISTS' ColumnName ColumnName ColumnType ColumnOption* ( 'FIRST' | 'AFTER' ColumnName )?

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

ColumnName ::=
    Identifier ( '.' Identifier ( '.' Identifier )? )?
```
## Examples

```sql
CREATE TABLE t1 (id int not null primary key AUTO_INCREMENT, col1 INT);
```

```
Query OK, 0 rows affected (0.11 sec)
```

```sql
INSERT INTO t1 (col1) VALUES (1),(2),(3),(4),(5);
```

```
Query OK, 5 rows affected (0.02 sec)
Records: 5  Duplicates: 0  Warnings: 0
```

```sql
ALTER TABLE t1 CHANGE col1 col2 INT;
```

```
Query OK, 0 rows affected (0.09 sec)
```

```sql
ALTER TABLE t1 CHANGE col2 col3 BIGINT, ALGORITHM=INSTANT;
```

```
Query OK, 0 rows affected (0.08 sec)
```

```sql
ALTER TABLE t1 CHANGE col3 col4 BIGINT, CHANGE id id2 INT NOT NULL;
```

```
ERROR 1105 (HY000): can't run multi schema change
```

```sql
CREATE TABLE t (a int primary key);
ALTER TABLE t CHANGE COLUMN a a VARCHAR(10);
```

```
ERROR 8200 (HY000): Unsupported modify column: column has primary key flag
```

```sql
CREATE TABLE t (c1 INT, c2 INT, c3 INT) partition by range columns(c1) ( partition p0 values less than (10), partition p1 values less than (maxvalue));
ALTER TABLE t CHANGE COLUMN c1 c1 DATETIME;
```

```
ERROR 8200 (HY000): Unsupported modify column: table is partition table
```

```sql
CREATE TABLE t (a INT, b INT as (a+1));
ALTER TABLE t CHANGE COLUMN b b VARCHAR(10);
```

```
ERROR 8200 (HY000): Unsupported modify column: column is generated
```

```sql
CREATE TABLE t (a DECIMAL(13, 7));
ALTER TABLE t CHANGE COLUMN a a DATETIME;
```

```
ERROR 8200 (HY000): Unsupported modify column: change from original type decimal(13,7) to datetime is currently unsupported yet
```
## MySQL compatibility

* Changes of [Reorg-Data](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-modify-column#reorg-data-change) types on primary key columns are not supported.
* Changes of column types on partitioned tables are not supported.
* Changes of column types on generated columns are not supported.
* Changes from some data types (for example, TIME, BIT, SET, ENUM, and JSON types) to some other types are not supported due to the compatibility issues of the `CAST` function's behavior between TiDB and MySQL.
## See also

* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [SHOW CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table)
* [ADD COLUMN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-column)
* [DROP COLUMN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-column)
* [MODIFY COLUMN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-modify-column)
