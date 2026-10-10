# MODIFY COLUMN syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-modify-column.md`
- Source Title: `MODIFY COLUMN | TiDB SQL Statement Reference`
- Source Heading Path: `MODIFY COLUMN | MODIFY COLUMN > Synopsis | MODIFY COLUMN > Examples | MODIFY COLUMN > Examples > Meta-Only Change | MODIFY COLUMN > Examples > Reorg-Data Change | MODIFY COLUMN > MySQL compatibility | MODIFY COLUMN > See also`
- Source Line Ranges: `5-221`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `alter-table`, `modify-column`, `ddl`, `column-types`, `meta-only-change`, `reorg-data`, `mysql-compatibility`, `generated-columns`, `partitioned-tables`, `primary-key-limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0612_5b9da35729`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-modify-column.md#modify-column`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1382d4a8da1e36babc79344ea0b636858a999b2c41f8811c4db83ec0160a42de`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-modify-column#modify-column
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-modify-column.md

## Retrieval Guidance

- Use When: Use this chunk when looking for ALTER TABLE MODIFY COLUMN syntax, examples of meta-only versus reorg-data type changes, or documented unsupported modify-column cases in TiDB.
- Retrieval Keywords: ALTER TABLE .. MODIFY COLUMN, MODIFY COLUMN syntax, ModifyColumnSpec, ALTER TABLE t1 MODIFY col1 BIGINT, ALTER TABLE t1 MODIFY col1 VARCHAR(5), Meta-Only Change, Reorg-Data Change, CHANGE COLUMN, Data Too Long, ERROR 1406 (22001), Unsupported modify column: column has primary key flag, Unsupported modify column: column is generated, Unsupported modify column: table is partition table, Unsupported modify column: change from original type decimal(13,7) to datetime is currently unsupported yet, generated columns, partitioned tables, Async Commit, SHOW CREATE TABLE
- Follow-up Guidance: For renaming a column at the same time, the content says to use the CHANGE COLUMN statement instead.
- Classification Note: This is reference content because it defines the MODIFY COLUMN grammar, shows exact SQL examples and outputs, and lists MySQL compatibility limitations and errors from the official documentation.

## Official Source Content

# MODIFY COLUMN

The `ALTER TABLE.. MODIFY COLUMN` statement modifies a column on an existing table. The modification can include changing the data type and attributes. To rename at the same time, use the [`CHANGE COLUMN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-column) statement instead.

Since v5.1.0, TiDB has supported changes of data types for Reorg data, including but not limited to:

- Changing `VARCHAR` to `BIGINT`
- Modifying the `DECIMAL` precision
- Compressing the length of `VARCHAR(10)` to `VARCHAR(5)`
## Synopsis

```ebnf+diagram
AlterTableStmt
         ::= 'ALTER' 'IGNORE'? 'TABLE' TableName ModifyColumnSpec ( ',' ModifyColumnSpec )*

ModifyColumnSpec
         ::= 'MODIFY' ColumnKeywordOpt 'IF EXISTS' ColumnName ColumnType ColumnOption* ( 'FIRST' | 'AFTER' ColumnName )?

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
### Meta-Only Change

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
ALTER TABLE t1 MODIFY col1 BIGINT;
```

```
Query OK, 0 rows affected (0.09 sec)
```

```sql
SHOW CREATE TABLE t1\G
```

```sql
*************************** 1. row ***************************
       Table: t1
Create Table: CREATE TABLE `t1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `col1` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin AUTO_INCREMENT=30001
1 row in set (0.00 sec)
```
### Reorg-Data Change

```sql
CREATE TABLE t1 (id int not null primary key AUTO_INCREMENT, col1 INT);
```

```
Query OK, 0 rows affected (0.11 sec)
```

```sql
INSERT INTO t1 (col1) VALUES (12345),(67890);
```

```
Query OK, 2 rows affected (0.00 sec)
Records: 2  Duplicates: 0  Warnings: 0
```

```sql
ALTER TABLE t1 MODIFY col1 VARCHAR(5);
```

```
Query OK, 0 rows affected (2.52 sec)
```

```sql
SHOW CREATE TABLE t1\G
```

```sql
*************************** 1. row ***************************
       Table: t1
CREATE TABLE `t1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `col1` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin AUTO_INCREMENT=30001
1 row in set (0.00 sec)
```

> **Note:**
>
> - TiDB returns an error when the changed data type conflicts with an existing data row. In the above example, TiDB returns the following error:
>
>    ```
>    alter table t1 modify column col1 varchar(4);
>    ERROR 1406 (22001): Data Too Long, field len 4, data len 5
>    ```
>
> - Due to the compatibility with the Async Commit feature, the DDL statement waits for a period of time (about 2.5s) before starting to process into Reorg Data.
>
>    ```
>    Query OK, 0 rows affected (2.52 sec)
>    ```
## MySQL compatibility

* Does not support modifying the Reorg-Data types on the primary key columns but supports modifying the Meta-Only types. For example:

    ```sql
    CREATE TABLE t (a int primary key);
    ALTER TABLE t MODIFY COLUMN a VARCHAR(10);
    ERROR 8200 (HY000): Unsupported modify column: column has primary key flag
    ```

    ```sql
    CREATE TABLE t (a int primary key);
    ALTER TABLE t MODIFY COLUMN a INT(10) UNSIGNED;
    ERROR 8200 (HY000): Unsupported modify column: column has primary key flag
    ```

    ```sql
    CREATE TABLE t (a int primary key);
    ALTER TABLE t MODIFY COLUMN a bigint;
    Query OK, 0 rows affected (0.01 sec)
    ```

* Does not support modifying the column types on generated columns. For example:

    ```sql
    CREATE TABLE t (a INT, b INT as (a+1));
    ALTER TABLE t MODIFY COLUMN b VARCHAR(10);
    ERROR 8200 (HY000): Unsupported modify column: column is generated
    ```

* Does not support modifying the column types on the partitioned tables. For example:

    ```sql
    CREATE TABLE t (c1 INT, c2 INT, c3 INT) partition by range columns(c1) ( partition p0 values less than (10), partition p1 values less than (maxvalue));
    ALTER TABLE t MODIFY COLUMN c1 DATETIME;
    ERROR 8200 (HY000): Unsupported modify column: table is partition table
    ```

* Does not support modifying from some data types (for example, some TIME types, BIT, SET, ENUM, JSON) to some other types due to some compatibility issues of the `cast` function's behavior between TiDB and MySQL.

    ```sql
    CREATE TABLE t (a DECIMAL(13, 7));
    ALTER TABLE t MODIFY COLUMN a DATETIME;
    ERROR 8200 (HY000): Unsupported modify column: change from original type decimal(13,7) to datetime is currently unsupported yet
    ```
## See also

* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [SHOW CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table)
* [ADD COLUMN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-column)
* [DROP COLUMN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-column)
* [CHANGE COLUMN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-column)
