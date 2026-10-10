# PRIMARY KEY rules and FOREIGN KEY support

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/constraints.md`
- Source Title: `Constraints`
- Source Heading Path: `Constraints > PRIMARY KEY | Constraints > FOREIGN KEY`
- Source Line Ranges: `346-454`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `primary-key`, `composite-primary-key`, `clustered-index`, `nonclustered`, `foreign-key`, `ddl`, `alter-table`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0066_f632c80d3b`
- Source ID: `tidb-docs-8.1:constraints.md#primary-key`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bdc667d659b74b08ac46b4ce248be8ee27c849bfa461477058d917715204fac2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/constraints#primary-key
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/constraints.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about PRIMARY KEY rules, dropping primary keys on `CLUSTERED` versus `NONCLUSTERED` tables, or creating, dropping, and inspecting `FOREIGN KEY` constraints.
- Retrieval Keywords: PRIMARY KEY, All parts of a PRIMARY KEY must be NOT NULL, ERROR 1171 (42000), Multiple primary key defined, ERROR 1068 (42000), composite primary key, CLUSTERED, NONCLUSTERED, ALTER TABLE DROP PRIMARY KEY, ERROR 8200 (HY000), FOREIGN KEY, ALTER TABLE DROP FOREIGN KEY, ALTER TABLE ADD FOREIGN KEY, information_schema.key_column_usage, fk_user_id
- Follow-up Guidance: The content shows example `CREATE TABLE`, `ALTER TABLE`, and `SELECT ... FROM information_schema.key_column_usage` statements for verifying primary key and foreign key definitions.
- Classification Note: This is classified as a reference topic because it states SQL constraint rules, supported DDL syntax, and specific error outcomes for primary keys and foreign keys.

## Official Source Content

## PRIMARY KEY

Like MySQL, primary key constraints contain unique constraints, that is, creating a primary key constraint is equivalent to having a unique constraint. In addition, other primary key constraints of TiDB are also similar to those of MySQL.

For example:

```sql
CREATE TABLE t1 (a INT NOT NULL PRIMARY KEY);
```

```
Query OK, 0 rows affected (0.12 sec)
```

```sql
CREATE TABLE t2 (a INT NULL PRIMARY KEY);
```

```
ERROR 1171 (42000): All parts of a PRIMARY KEY must be NOT NULL; if you need NULL in a key, use UNIQUE instead
```

```sql
CREATE TABLE t3 (a INT NOT NULL PRIMARY KEY, b INT NOT NULL PRIMARY KEY);
```

```
ERROR 1068 (42000): Multiple primary key defined
```

```sql
CREATE TABLE t4 (a INT NOT NULL, b INT NOT NULL, PRIMARY KEY (a,b));
```

```
Query OK, 0 rows affected (0.10 sec)
```

* Table `t2` failed to be created, because column `a` is defined as the primary key and does not allow NULL values.
* Table `t3` failed to be created, because a table can only have one primary key.
* Table `t4` was created successfully, because even though there can be only one primary key, TiDB supports defining multiple columns as the composite primary key.

In addition to the rules above, TiDB currently only supports adding and deleting the primary keys of the `NONCLUSTERED` type. For example:

```sql
CREATE TABLE t5 (a INT NOT NULL, b INT NOT NULL, PRIMARY KEY (a,b) CLUSTERED);
ALTER TABLE t5 DROP PRIMARY KEY;
```

```
ERROR 8200 (HY000): Unsupported drop primary key when the table is using clustered index
```

```sql
CREATE TABLE t5 (a INT NOT NULL, b INT NOT NULL, PRIMARY KEY (a,b) NONCLUSTERED);
ALTER TABLE t5 DROP PRIMARY KEY;
```

```
Query OK, 0 rows affected (0.10 sec)
```

For more details about the primary key of the `CLUSTERED` type, refer to [clustered index](https://docs.pingcap.com/tidb/stable/clustered-indexes).
## FOREIGN KEY

> **Note:**
>
> Starting from v6.6.0, TiDB supports the [FOREIGN KEY constraints](https://docs.pingcap.com/tidb/stable/foreign-key) as an experimental feature. Before v6.6.0, TiDB supports creating and deleting foreign key constraints, but the constraints are not actually effective. After upgrading TiDB to v6.6.0, you can delete the invalid foreign key and create a new one to make the foreign key constraints effective.

TiDB supports creating `FOREIGN KEY` constraints in DDL commands.

For example:

```sql
CREATE TABLE users (
 id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
 doc JSON
);
CREATE TABLE orders (
 id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
 user_id INT NOT NULL,
 doc JSON,
 FOREIGN KEY fk_user_id (user_id) REFERENCES users(id)
);
```

```sql
SELECT table_name, column_name, constraint_name, referenced_table_name, referenced_column_name
FROM information_schema.key_column_usage WHERE table_name IN ('users', 'orders');
```

```
+------------+-------------+-----------------+-----------------------+------------------------+
| table_name | column_name | constraint_name | referenced_table_name | referenced_column_name |
+------------+-------------+-----------------+-----------------------+------------------------+
| users      | id          | PRIMARY         | NULL                  | NULL                   |
| orders     | id          | PRIMARY         | NULL                  | NULL                   |
| orders     | user_id     | fk_user_id      | users                 | id                     |
+------------+-------------+-----------------+-----------------------+------------------------+
3 rows in set (0.00 sec)
```

TiDB also supports the syntax to `DROP FOREIGN KEY` and `ADD FOREIGN KEY` via the `ALTER TABLE` command.

```sql
ALTER TABLE orders DROP FOREIGN KEY fk_user_id;
ALTER TABLE orders ADD FOREIGN KEY fk_user_id (user_id) REFERENCES users(id);
```
