# Foreign key constraints overview, restrictions, DDL, checks, and locking

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/foreign-key.md`
- Source Title: `FOREIGN KEY Constraints`
- Source Heading Path: `FOREIGN KEY Constraints | FOREIGN KEY Constraints > Naming | FOREIGN KEY Constraints > Restrictions | FOREIGN KEY Constraints > Reference operations | FOREIGN KEY Constraints > Usage examples of foreign keys | FOREIGN KEY Constraints > Create a foreign key constraint | FOREIGN KEY Constraints > Delete a foreign key constraint | FOREIGN KEY Constraints > Foreign key constraint check | FOREIGN KEY Constraints > Locking`
- Source Line Ranges: `5-184`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `foreign-key`, `referential-integrity`, `constraints`, `naming`, `restrictions`, `reference-operations`, `create-table`, `alter-table`, `drop-foreign-key`, `foreign_key_checks`, `locking`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0285_78a57bcca7`
- Source ID: `tidb-docs-8.1:foreign-key.md#foreign-key-constraints`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a84fb49dd782956220188f9eddb5765f695133173664649c844f74ecae56b9f8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/foreign-key#foreign-key-constraints
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/foreign-key.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB foreign key constraint syntax, naming rules, restrictions, reference operations, ALTER TABLE add or drop statements, foreign_key_checks behavior, or locking semantics.
- Retrieval Keywords: FOREIGN KEY Constraints, ForeignKeyDef, ReferenceOption, CONSTRAINT identifier, FOREIGN KEY identifier, ERROR 1826: Duplicate foreign key constraint name 'fk', ERROR 1822: Failed to add the foreign key constraint. Missing index for constraint 'fk' in the referenced table 't', REFERENCES privilege, ON DELETE CASCADE, ON UPDATE CASCADE, RESTRICT, NO ACTION, SET NULL, SET DEFAULT, STORED GENERATED COLUMN, ALTER TABLE table_name ADD CONSTRAINT FOREIGN KEY, ALTER TABLE table_name DROP FOREIGN KEY fk_identifier, SHOW CREATE TABLE, foreign_key_checks, SELECT FOR UPDATE, LOCK IN SHARE MODE
- Follow-up Guidance: The source also notes that foreign key checks are controlled by the GLOBAL and SESSION system variable foreign_key_checks, and that parent-row locking during child-table INSERT or UPDATE is equivalent to SELECT FOR UPDATE.
- Classification Note: This is a SQL reference chunk because the official content defines foreign key syntax, supported behaviors, restrictions, SQL statements, system variable effects, and related errors in TiDB.

## Official Source Content

# FOREIGN KEY Constraints

Starting from v6.6.0, TiDB supports the foreign key feature, which allows cross-table referencing of related data, and foreign key constraints to maintain data consistency.

> **Warning:**
>
> - Currently, the foreign key feature is experimental. It is not recommended that you use it in production environments. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.
> - The foreign key feature is typically employed to enforce [referential integrity](https://en.wikipedia.org/wiki/Referential_integrity) constraint checks. It might cause performance degradation, so it is recommended to conduct thorough testing before using it in performance-sensitive scenarios.

The foreign key is defined in the child table. The syntax is as follows:

```ebnf+diagram
ForeignKeyDef
         ::= ( 'CONSTRAINT' Identifier )? 'FOREIGN' 'KEY'
             Identifier? '(' ColumnName ( ',' ColumnName )* ')'
             'REFERENCES' TableName '(' ColumnName ( ',' ColumnName )* ')'
             ( 'ON' 'DELETE' ReferenceOption )?
             ( 'ON' 'UPDATE' ReferenceOption )?

ReferenceOption
         ::= 'RESTRICT'
           | 'CASCADE'
           | 'SET' 'NULL'
           | 'SET' 'DEFAULT'
           | 'NO' 'ACTION'
```
## Naming

The naming of a foreign key follows the following rules:

- If a name is specified in `CONSTRAINT identifier`, the specified name is used.
- If no name is specified in `CONSTRAINT identifier`, but a name is specified in `FOREIGN KEY identifier`, the name specified in the `FOREIGN KEY identifier` is used.
- If neither `CONSTRAINT identifier` nor `FOREIGN KEY identifier` specifies a name, a name is automatically generated, such as `fk_1`, `fk_2`, and `fk_3`.
- The foreign key name must be unique in the current table. Otherwise, an error `ERROR 1826: Duplicate foreign key constraint name 'fk'` is reported when the foreign key is created.
## Restrictions

When creating a foreign key, the following conditions must be met:

- Neither the parent table nor the child table is a temporary table.
- The user has the `REFERENCES` privilege on the parent table.
- The columns referenced by the foreign key in the parent table and the child table are of the same data type and have the same size, precision, length, character set, and collation.
- The columns in the foreign key cannot reference themselves.
- The columns in the foreign key and the columns in the referenced parent table have the same index, and the order of the columns in the index matches that in the foreign key. This is to use the index to avoid full table scans when performing foreign key constraint checks.

    - If there is no corresponding foreign key index in the parent table, an error `ERROR 1822: Failed to add the foreign key constraint. Missing index for constraint 'fk' in the referenced table 't'` is reported.
    - If there is no corresponding foreign key index in the child table, an index is automatically created with the same name as the foreign key.

- It is not supported to create a foreign key on a column of the `BLOB` or `TEXT` type.
- It is not supported to create a foreign key on a partitioned table.
- It is not supported to create a foreign key on a virtual generated column.
## Reference operations

If an `UPDATE` or `DELETE` operation affects a foreign key value in the parent table, the corresponding foreign key value in the child table is determined by the reference operation defined by the `ON UPDATE` or `ON DELETE` clause in the foreign key definition. The reference operations include the following:

- `CASCADE`: automatically updates or deletes the matching rows in the child table when the `UPDATE` or `DELETE` operation affects the parent table. The cascade operation is performed in a depth-first manner.
- `SET NULL`: automatically sets the matching foreign key columns in the child table to `NULL` when the `UPDATE` or `DELETE` operation affects the parent table.
- `RESTRICT`: denies the `UPDATE` or `DELETE` operation if the child table contains matching rows.
- `NO ACTION`: the same as `RESTRICT`.
- `SET DEFAULT`: the same as `RESTRICT`.

If there is no matching foreign key value in the parent table, the `INSERT` or `UPDATE` operation on the child table is denied.

If the foreign key definition does not specify `ON DELETE` or `ON UPDATE`, the default behavior is `NO ACTION`.

If the foreign key is defined on a `STORED GENERATED COLUMN`, the `CASCADE`, `SET NULL`, and `SET DEFAULT` references are not supported.
## Usage examples of foreign keys

The following example uses a single-column foreign key to associate the parent table and the child table:

```sql
CREATE TABLE parent (
    id INT KEY
);

CREATE TABLE child (
    id INT,
    pid INT,
    INDEX idx_pid (pid),
    FOREIGN KEY (pid) REFERENCES parent(id) ON DELETE CASCADE
);
```

The following is a more complex example where the `product_order` table has two foreign keys that reference the other two tables. One foreign key references two indexes on the `product` table, and the other references a single index on the `customer` table:

```sql
CREATE TABLE product (
    category INT NOT NULL,
    id INT NOT NULL,
    price DECIMAL(20,10),
    PRIMARY KEY(category, id)
);

CREATE TABLE customer (
    id INT KEY
);

CREATE TABLE product_order (
    id INT NOT NULL AUTO_INCREMENT,
    product_category INT NOT NULL,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,

    PRIMARY KEY(id),
    INDEX (product_category, product_id),
    INDEX (customer_id),

    FOREIGN KEY (product_category, product_id)
      REFERENCES product(category, id)
      ON UPDATE CASCADE ON DELETE RESTRICT,

    FOREIGN KEY (customer_id)
      REFERENCES customer(id)
);
```
## Create a foreign key constraint

To create a foreign key constraint, you can use the following `ALTER TABLE` statement:

```sql
ALTER TABLE table_name
    ADD [CONSTRAINT [identifier]] FOREIGN KEY
    [identifier] (col_name, ...)
    REFERENCES tbl_name (col_name,...)
    [ON DELETE reference_option]
    [ON UPDATE reference_option]
```

The foreign key can be self-referencing, that is, referencing the same table. When you add a foreign key constraint to a table using `ALTER TABLE`, you need to first create an index on the parent table column that the foreign key references.
## Delete a foreign key constraint

To delete a foreign key constraint, you can use the following `ALTER TABLE` statement:

```sql
ALTER TABLE table_name DROP FOREIGN KEY fk_identifier;
```

If the foreign key constraint is named when it is created, you can reference the name to delete the foreign key constraint. Otherwise, you have to use the constraint name automatically generated to delete the constraint. You can use `SHOW CREATE TABLE` to view the foreign key name:

```sql
mysql> SHOW CREATE TABLE child\G
*************************** 1. row ***************************
       Table: child
Create Table: CREATE TABLE `child` (
  `id` int(11) DEFAULT NULL,
  `pid` int(11) DEFAULT NULL,
  KEY `idx_pid` (`pid`),
  CONSTRAINT `fk_1` FOREIGN KEY (`pid`) REFERENCES `test`.`parent` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
```
## Foreign key constraint check

TiDB supports foreign key constraint check, which is controlled by the system variable [`foreign_key_checks`](https://docs.pingcap.com/tidb/stable/system-variables#foreign_key_checks). By default, this variable is set to `ON`, meaning that the foreign key constraint check is enabled. This variable has two scopes: `GLOBAL` and `SESSION`. Keeping this variable enabled can ensure the integrity of foreign key reference relationships.

The effect of disabling foreign key constraint check is as follows:

- When you delete a parent table referenced by a foreign key, the deletion can succeed only when the foreign key constraint check is disabled.
- When you import data to a database, the order of creating tables might be different from the foreign key dependency order, which might cause the creation of tables to fail. Only when the foreign key constraint check is disabled can the tables be created successfully. In addition, disabling the foreign key constraint check can speed up data import.
- When you import data to a database, if the data of the child table is imported first, an error will be reported. Only when the foreign key constraint check is disabled can the data of the child table be imported successfully.
- If an `ALTER TABLE` operation to be executed involves a change of the foreign key, this operation succeeds only when the foreign key constraint check is disabled.

When the foreign key constraint check is disabled, the foreign key constraint check and reference operation are not executed, except for the following scenarios:

- If the execution of `ALTER TABLE` might result in wrong definition of the foreign key, an error is still reported during the execution.
- When deleting the index required by the foreign key, you should delete the foreign key first. Otherwise, an error is reported.
- When you create a foreign key but it does not meet related conditions or restrictions, an error is reported.
## Locking

When `INSERT` or `UPDATE` a child table, the foreign key constraint checks whether the corresponding foreign key value exists in the parent table, and locks the row in the parent table to avoid the foreign key value being deleted by other operations violating the foreign key constraint. The locking behavior is equivalent to performing a `SELECT FOR UPDATE` operation on the row where the foreign key value is located in the parent table.

Because TiDB currently does not support `LOCK IN SHARE MODE`, if a child table accepts a large number of concurrent writes and most of the referenced foreign key values are the same, there might be serious locking conflicts. It is recommended to disable [`foreign_key_checks`](https://docs.pingcap.com/tidb/stable/system-variables#foreign_key_checks) when writing a large number of child table data.
