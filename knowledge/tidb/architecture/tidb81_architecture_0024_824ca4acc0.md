# DM safe mode purpose and SQL rewrite principle

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-safe-mode.md`
- Source Title: `DM Safe Mode`
- Source Heading Path: `DM Safe Mode | DM Safe Mode > Working principle`
- Source Line Ranges: `5-50`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `sql`
- Topic Tags: `safe-mode`, `incremental-replication`, `binlog`, `idempotency`, `checkpoints`, `sql-rewrite`, `insert`, `update`, `replace`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0024_824ca4acc0`
- Source ID: `tidb-docs-8.1:dm/dm-safe-mode.md#dm-safe-mode`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `91367dd10490c28bb8ce0c06ec131b6e68e8b1774db5edd3fb8e0e2465a44b0c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-safe-mode#dm-safe-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-safe-mode.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how DM safe mode makes repeated incremental replication binlog events idempotent by rewriting DML after resuming from a checkpoint.
- Retrieval Keywords: DM Safe Mode, safe mode, incremental replication, binlog events, checkpoint, idempotence, rewrite SQL statements, INSERT to REPLACE, UPDATE to DELETE + REPLACE, REPLACE statement, primary key, unique index, replication failure
- Follow-up Guidance: The source also includes repeated-execution examples on `dummydb.dummytbl` showing `INSERT` rewritten to `REPLACE` and `UPDATE` rewritten to `DELETE` plus `REPLACE`.
- Classification Note: This is classified as architecture because the content explains the working principle and purpose of DM safe mode and how SQL rewrite guarantees idempotency.

## Official Source Content

# DM Safe Mode

Safe mode is a special operation mode for DM to perform incremental replication. In safe mode, when the DM incremental replication component replicates binlog events, DM forcibly rewrites all the `INSERT` and `UPDATE` statements before executing them in the downstream.

During safe mode, one binlog event can be replicated repeatedly to the downstream with idempotence guaranteed. Thus, the incremental replication is *safe*.

After resuming a data replication task from a checkpoint, DM might repeatedly replicate some binlog events, which leads to the following issues:

- During incremental replication, the operation of executing DML and the operation of writing checkpoints are not simultaneous. The operation of writing checkpoints and writing data into the downstream database is not atomic. Therefore, **when DM exits abnormally, checkpoints might only record the restoration point before the exit point**.
- When DM restarts a replication task and resumes incremental replication from a checkpoint, some data between the checkpoint and the exit point might already be processed before the abnormal exit. This causes **some SQL statements to be executed repeatedly**.
- If an `INSERT` statement is executed repeatedly, the primary key or the unique index might encounter a conflict, which leads to a replication failure. If an `UPDATE` statement is executed repeatedly, the filter condition might not be able to locate the previously updated records.

In safe mode, DM can rewrite SQL statements to resolve the preceding issues.
## Working principle

In safe mode, DM guarantees the idempotency of binlog events by rewriting SQL statements. Specifically, the following SQL statements are rewritten:

* `INSERT` statements are rewritten to `REPLACE` statements.
* `UPDATE` statements are analyzed to obtain the value of the primary key or the unique index of the row updated. `UPDATE` statements are then rewritten to `DELETE` + `REPLACE` statements in the following two steps: DM deletes the old record using the primary key or unique index, and inserts the new record using the `REPLACE` statement.

`REPLACE` is a MySQL-specific syntax for inserting data. When you insert data using `REPLACE`, and the new data and existing data have a primary key or unique constraint conflict, MySQL deletes all the conflicting records and executes the insert operation, which is equivalent to "force insert". For details, see [`REPLACE` statement](https://dev.mysql.com/doc/refman/8.0/en/replace.html) in MySQL documentation.

Assume that a `dummydb.dummytbl` table has a primary key `id`. Execute the following SQL statements repeatedly on this table:

```sql
INSERT INTO dummydb.dummytbl (id, int_value, str_value) VALUES (123, 999, 'abc');
UPDATE dummydb.dummytbl SET int_value = 888999 WHERE int_value = 999;   -- Suppose there is no other record with int_value = 999
UPDATE dummydb.dummytbl SET id = 999 WHERE id = 888;    -- Update the primary key
```

With safe mode enabled, when the preceding SQL statements are executed again in the downstream, they are rewritten as follows:

```sql
REPLACE INTO dummydb.dummytbl (id, int_value, str_value) VALUES (123, 999, 'abc');
DELETE FROM dummydb.dummytbl WHERE id = 123;
REPLACE INTO dummydb.dummytbl (id, int_value, str_value) VALUES (123, 888999, 'abc');
DELETE FROM dummydb.dummytbl WHERE id = 888;
REPLACE INTO dummydb.dummytbl (id, int_value, str_value) VALUES (999, 888888, 'abc888');
```

In the preceding statements, `UPDATE` is rewritten as `DELETE` + `REPLACE`, rather than `DELETE` + `INSERT`. If `INSERT` is used here, when you insert a duplicate record with `id = 999`, the database reports a primary key conflict. This is why `REPLACE` is used instead. The new record will replace the existing record.

By rewriting SQL statements, DM overwrites the existing row data using the new row data when performing duplicate insert or update operations. This guarantees that insert and update operations are executed repeatedly.
