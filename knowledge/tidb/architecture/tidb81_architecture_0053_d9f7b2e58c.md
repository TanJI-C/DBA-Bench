# Pessimistic transaction behaviors and lock semantics

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pessimistic-transaction.md`
- Source Title: `TiDB Pessimistic Transaction Mode`
- Source Heading Path: `TiDB Pessimistic Transaction Mode > Behaviors`
- Source Line Ranges: `40-83`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `snapshot-read`, `current-read`, `pessimistic-locks`, `deadlocks`, `lock-wait-timeout`, `nowait`, `mvcc`, `point-get`, `batch-point-get`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0053_d9f7b2e58c`
- Source ID: `tidb-docs-8.1:pessimistic-transaction.md#behaviors`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c591f3577485e57b2d4b8839ad24fecc04b620d437ad34780e3a023ba3403b65`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pessimistic-transaction#behaviors
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pessimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the runtime behavior of pessimistic transactions, including snapshot read, current read, lock waiting, deadlocks, NOWAIT, and locking behavior of Point Get or Batch Point Get.
- Retrieval Keywords: snapshot read, current read, SELECT FOR UPDATE, UPDATE DELETE INSERT latest committed data, pessimistic lock, MVCC, deadlock error 1213, innodb_lock_wait_timeout, lock wait timeout error 1205, FOR UPDATE NOWAIT, error 3572, Point Get, Batch Point Get, FOR UPDATE OF TABLES, tidb_constraint_check_in_place_pessimistic
- Follow-up Guidance: It notes that TiDB supports FOR UPDATE OF TABLES and that Point Get and Batch Point Get still lock the given primary key or unique key even when no data is read.
- Classification Note: This is classified as architecture because the content describes transaction read types, lock semantics, waiting behavior, and concurrency behavior in pessimistic transactions.

## Official Source Content

## Behaviors

Pessimistic transactions in TiDB behave similarly to those in MySQL. See the minor differences in [Difference with MySQL InnoDB](#difference-with-mysql-innodb).

- For pessimistic transactions, TiDB introduces snapshot read and current read.

    - Snapshot read: it is an unlocked read that reads a version committed before the transaction starts. The read in the `SELECT` statement is a snapshot read.
    - Current read: it is a locked read that reads the latest committed version. The read in the `UPDATE`, `DELETE`, `INSERT`, or `SELECT FOR UPDATE` statement is a current read.

    The following examples provide a detailed description of snapshot read and current read.

    | Session 1 | Session 2 | Session 3 |
    | :----| :---- | :---- |
    | CREATE TABLE t (a INT); |  |  |
    | INSERT INTO T VALUES(1); |  |  |
    | BEGIN PESSIMISTIC; |  |
    | UPDATE t SET a = a + 1; |  |  |
    |  | BEGIN PESSIMISTIC; |  |
    |  | SELECT * FROM t;  -- Use the snapshot read to read the version committed before the current transaction starts. The result returns a=1. |  |
    |  |  | BEGIN PESSIMISTIC;
    |  |  | SELECT * FROM t FOR UPDATE; -- Use the current read. Wait for the lock.  |
    | COMMIT; -- Release the lock. The SELECT FOR UPDATE operation of session 3 obtains the lock and TiDB uses the current read to read the latest committed version. The result returns a=2. |  |  |
    |  | SELECT * FROM t; -- Use the snapshot read to read the version committed before the current transaction starts. The result returns a=1. |  |

- When you execute `UPDATE`, `DELETE` or `INSERT` statements, the **latest** committed data is read, data is modified, and a pessimistic lock is applied on the modified rows.

- For `SELECT FOR UPDATE` statements, a pessimistic lock is applied on the latest version of the committed data, instead of on the modified rows.

- Locks will be released when the transaction is committed or rolled back. Other transactions attempting to modify the data are blocked and have to wait for the lock to be released. Transactions attempting to _read_ the data are not blocked, because TiDB uses multi-version concurrency control (MVCC).

- You can set the system variable [`tidb_constraint_check_in_place_pessimistic`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place_pessimistic-new-in-v630) to control whether to skip the pessimistic locks with unique constraint checks. See [constraints](https://docs.pingcap.com/tidb/stable/constraints#pessimistic-transactions) for details.

- If several transactions are trying to acquire each other's respective locks, a deadlock will occur. This is automatically detected, and one of the transactions will randomly be terminated with a MySQL-compatible error code `1213` returned.

- Transactions will wait up to `innodb_lock_wait_timeout` seconds (default: 50) to acquire new locks. When this timeout is reached, a MySQL-compatible error code `1205` is returned. If multiple transactions are waiting for the same lock, the order of priority is approximately based on the `start ts` of the transaction.

- TiDB supports both the optimistic transaction mode and pessimistic transaction mode in the same cluster. You can specify either mode for transaction execution.

- TiDB supports the `FOR UPDATE NOWAIT` syntax and does not block and wait for locks to be released. Instead, a MySQL-compatible error code `3572` is returned.

- If the `Point Get` and `Batch Point Get` operators do not read data, they still lock the given primary key or unique key, which blocks other transactions from locking or writing data to the same primary key or unique key.

- TiDB supports the `FOR UPDATE OF TABLES` syntax. For a statement that joins multiple tables, TiDB only applies pessimistic locks on the rows that are associated with the tables in `OF TABLES`.
