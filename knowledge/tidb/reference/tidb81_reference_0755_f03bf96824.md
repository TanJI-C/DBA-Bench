# Global temporary tables and memory limits

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/temporary-tables.md`
- Source Title: `Temporary Tables`
- Source Heading Path: `Temporary Tables > Global temporary tables | Temporary Tables > Global temporary tables > Usage examples of global temporary tables | Temporary Tables > Limit the memory usage of temporary tables`
- Source Line Ranges: `170-292`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `global-temporary-tables`, `transaction-scope`, `autocommit`, `memory-limit`, `system-variables`, `usage-examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0755_f03bf96824`
- Source ID: `tidb-docs-8.1:temporary-tables.md#global-temporary-tables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f4a97ab733be07312672acff50b1f2062f3169aec97f49aaa93ac2d09adceb40`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/temporary-tables#global-temporary-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/temporary-tables.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about global temporary tables, transaction-scoped data visibility, autocommit behavior, or the memory limit controlled by a system variable.
- Retrieval Keywords: global temporary table, CREATE GLOBAL TEMPORARY TABLE, ON COMMIT DELETE ROWS, transaction visible only, non-autocommit transactions, COMMIT clears data, tidb_tmp_table_max_size, SET GLOBAL tidb_tmp_table_max_size=268435456, 64MB default, temporary table memory limit
- Follow-up Guidance: The source notes that temporary table data is stored only in TiDB instance memory and is not persisted.
- Classification Note: This is reference content because it specifies global temporary table semantics, required SQL form, example transaction behavior, and the exact system variable for limiting temporary table size.

## Official Source Content

## Global temporary tables

The global temporary table is an extension of TiDB. The characteristics are as follows:

- The table definition of a global temporary table is persistent and visible to all sessions.
- The data of a global temporary table is visible only in the current transaction. When the transaction ends, the data is automatically cleared.
- A global temporary table cannot have the same name as an ordinary table.

To create a global temporary table, you can use the `CREATE GLOBAL TEMPORARY TABLE` statement ended with `ON COMMIT DELETE ROWS`. To drop a global temporary table, you can use the `DROP TABLE` or `DROP GLOBAL TEMPORARY TABLE` statement.
### Usage examples of global temporary tables

> **Note:**
>
> - Before you use the temporary table in TiDB, pay attention to the [compatibility restrictions with other TiDB features](#compatibility-restrictions-with-other-tidb-features).
> - If you have created global temporary tables on a TiDB cluster of v5.3.0 or later, when the cluster is downgraded to a version earlier than v5.3.0, these tables are handled as ordinary tables. In this case, a data error occurs.

Create a global temporary table `users` in session A:

```sql
CREATE GLOBAL TEMPORARY TABLE users (
    id BIGINT,
    name VARCHAR(100),
    city VARCHAR(50),
    PRIMARY KEY(id)
) ON COMMIT DELETE ROWS;
```

```
Query OK, 0 rows affected (0.01 sec)
```

The data written to `users` is visible to the current transaction:

```sql
BEGIN;
```

```
Query OK, 0 rows affected (0.00 sec)
```

```sql
INSERT INTO users(id, name, city) VALUES(1001, 'Davis', 'LosAngeles');
```

```
Query OK, 1 row affected (0.00 sec)
```

```sql
SELECT * FROM users;
```

```
+------+-------+------------+
| id   | name  | city       |
+------+-------+------------+
| 1001 | Davis | LosAngeles |
+------+-------+------------+
1 row in set (0.00 sec)
```

After the transaction ends, the data is automatically cleared:

```sql
COMMIT;
```

```
Query OK, 0 rows affected (0.00 sec)
```

```sql
SELECT * FROM users;
```

```
Empty set (0.00 sec)
```

After `users` is created in session A, session B can also read from and write to the `users` table:

```sql
SELECT * FROM users;
```

```
Empty set (0.00 sec)
```

> **Note:**
>
> If the transaction is automatically committed, after the SQL statement is executed, the inserted data is automatically cleared and unavailable to subsequent SQL executions. Therefore, you should use non-autocommit transactions to read from and write to global temporary tables.
## Limit the memory usage of temporary tables

No matter which storage engine is declared as `ENGINE` when you define a table, the data of local temporary tables and global temporary tables is only stored in the memory of TiDB instances. This data is not persisted.

To avoid memory overflow, you can limit the size of each temporary table using the [`tidb_tmp_table_max_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_tmp_table_max_size-new-in-v530) system variable. Once a temporary table is larger than the `tidb_tmp_table_max_size` threshold value, TiDB reports an error. The default value of `tidb_tmp_table_max_size` is `64MB`.

For example, set the maximum size of a temporary table to `256MB`:

```sql
SET GLOBAL tidb_tmp_table_max_size=268435456;
```
