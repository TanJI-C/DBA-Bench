# Overview, usage scenarios, and prerequisites for non-transactional DML

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/non-transactional-dml.md`
- Source Title: `Non-Transactional DML Statements`
- Source Heading Path: `Non-Transactional DML Statements | Non-Transactional DML Statements > Usage scenarios | Non-Transactional DML Statements > Prerequisites`
- Source Line Ranges: `5-73`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `non-transactional-dml`, `batch-processing`, `atomicity`, `isolation`, `idempotency`, `concurrency`, `shard-column`, `restrictions`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0172_318ae012e7`
- Source ID: `tidb-docs-8.1:non-transactional-dml.md#non-transactional-dml-statements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c32c2da0a3d432dceecea827dcec4edfbd3c807c3566be52c6b47e716881186d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/non-transactional-dml#non-transactional-dml-statements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/non-transactional-dml.md

## Retrieval Guidance

- Use When: Use this content when you need the overview, applicable scenarios, and prerequisites for TiDB non-transactional DML statements and their limits around atomicity, isolation, idempotency, concurrency, and shard-column behavior.
- Retrieval Keywords: non-transactional DML statements, BATCH, DRY RUN, INSERT INTO ... SELECT, REPLACE INTO .. SELECT, UPDATE, DELETE, transaction size limit, atomicity, isolation, idempotent, tidb_redact_log, tidb_nontransactional_ignore_error, concurrent writes, shard column, AUTO_INCREMENT, INSERT ... ON DUPLICATE KEY UPDATE, REPLACE INTO, Join key, missing writes, wrong writes
- Follow-up Guidance: The content points to the detailed syntax in the BATCH SQL statement reference and notes that DRY RUN can preview the split statements.
- Classification Note: This is classified as an operation topic because the official content explains when non-transactional DML is suitable and lists the conditions and warnings required before running it.

## Official Source Content

# Non-Transactional DML Statements

This document describes the usage scenarios, usage methods, and restrictions of non-transactional DML statements in TiDB. In addition, the implementation principle and common issues are also explained.

A non-transactional DML statement is a DML statement split into multiple SQL statements (which is, multiple batches) to be executed in sequence. It enhances the performance and ease of use in batch data processing at the expense of transactional atomicity and isolation.

Usually, memory-consuming transactions need to be split into multiple SQL statements to bypass the transaction size limit. Non-transactional DML statements integrate this process into the TiDB kernel to achieve the same effect. It is helpful to understand the effect of non-transactional DML statements by splitting SQL statements. The `DRY RUN` syntax can be used to preview the split statements.

Non-transactional DML statements include:

- `INSERT INTO ... SELECT`
- `REPLACE INTO .. SELECT`
- `UPDATE`
- `DELETE`

For detailed syntax, see [`BATCH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-batch).

> **Note:**
>
> - A non-transactional DML statement does not guarantee the atomicity and isolation of the statement, and is not equivalent to the original DML statement.
> - After a DML statement is rewritten into a non-transactional DML statement, you cannot assume that its behavior is consistent with that of the original statement.
> - Before using a non-transactional DML, you need to analyze whether the split statements will affect each other.
## Usage scenarios

In the scenarios of large data processing, you might often need to perform same operations on a large batch of data. If the operation is performed directly using a single SQL statement, the transaction size might exceed the limit and affect the execution performance.

Batch data processing often has no overlap of time or data with the online application operations. Isolation (I in ACID) is unnecessary when no concurrent operations exist. Atomicity is also unnecessary if bulk data operations are idempotent or easily retryable. If your application needs neither data isolation nor atomicity, you can consider using non-transactional DML statements.

Non-transactional DML statements are used to bypass the size limit on large transactions in certain scenarios. One statement is used to complete tasks that would otherwise require manually splitting of transactions, with higher execution efficiency and less resource consumption.

For example, to delete expired data, if you ensure that no application will access the expired data, you can use a non-transactional DML statement to improve the `DELETE` performance.
## Prerequisites

Before using non-transactional DML statements, make sure that the following conditions are met:

- The statement does not require atomicity, which permits some rows to be modified and some rows to remain unmodified in the execution result.
- The statement is idempotent, or you are prepared to retry on a part of the data according to the error message. If the system variables are set to `tidb_redact_log = 1` and `tidb_nontransactional_ignore_error = 1`, this statement must be idempotent. Otherwise, when the statement partially fails, the failed part cannot be accurately located.
- The data to be operated on has no other concurrent writes, which means it is not updated by other statements at the same time. Otherwise, unexpected results such as missing writes, wrong writes, and modifying the same line multiple times might occur.
- The statement does not modify the data to be read by the statement itself. Otherwise, the following batch will read the data written by the previous batch and easily causes unexpected results.

    - Avoid modifying the shard column when you select from and modify the same table within a non-transactional `INSERT INTO ... SELECT` statement. Otherwise, multiple batches might read the same row and insert data multiple times:
        - It is not recommended to use `BATCH ON test.t.id LIMIT 10000 INSERT INTO t SELECT id+1, value FROM t;`.
        - It is recommended to use `BATCH ON test.t.id LIMIT 10000 INSERT INTO t SELECT id, value FROM t;`.
        - If the shard column `id` has the `AUTO_INCREMENT` attribute, it is recommended to use `BATCH ON test.t.id LIMIT 10000 INSERT INTO t(value) SELECT value FROM t;`.
    - Avoid updating the shard column in the non-transactional `UPDATE`, `INSERT ... ON DUPLICATE KEY UPDATE`, or `REPLACE INTO` statement:
        - For example, for a non-transactional `UPDATE` statement, the split SQL statements are executed in sequence. The modification of the previous batch is read by the next batch after the previous batch is committed, which causes the same line of data to be modified multiple times.
        - These statements do not support `BATCH ON test.t.id LIMIT 10000 UPDATE t SET test.t.id = test.t.id-1;`.
        - It is not recommended to use `BATCH ON test.t.id LIMIT 1 INSERT INTO t SELECT id+1, value FROM t ON DUPLICATE KEY UPDATE id = id + 1;`.
    - The shard column should not be used as a Join key. For example, the following example uses the shard column `test.t.id` as a Join key, which causes a non-transactional `UPDATE` statement to modify the same line multiple times:

        ```sql
        CREATE TABLE t(id int, v int, key(id));
        CREATE TABLE t2(id int, v int, key(id));
        INSERT INTO t VALUES (1, 1), (2, 2), (3, 3);
        INSERT INTO t2 VALUES (1, 1), (2, 2), (4, 4);
        BATCH ON test.t.id LIMIT 1 UPDATE t JOIN t2 ON t.id = t2.id SET t2.id = t2.id+1;
        SELECT * FROM t2; -- (4, 1) (4, 2) (4, 4)
        ```

- The statement meets the [restrictions](#restrictions).
- It is not recommended to perform concurrent DDL operations on the table to be read or written by this DML statement.

> **Warning:**
>
> If `tidb_redact_log` and `tidb_nontransactional_ignore_error` are enabled at the same time, you might not get the complete error information of each batch, and you cannot retry the failed batch only. Therefore, if both of the system variables are turned on, the non-transactional DML statement must be idempotent.
