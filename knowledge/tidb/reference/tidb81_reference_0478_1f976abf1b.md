# Differences from MySQL InnoDB and supported isolation levels

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pessimistic-transaction.md`
- Source Title: `TiDB Pessimistic Transaction Mode`
- Source Heading Path: `TiDB Pessimistic Transaction Mode > Difference with MySQL InnoDB | TiDB Pessimistic Transaction Mode > Isolation level`
- Source Line Ranges: `84-142`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `mysql-compatibility`, `gap-locking`, `ddl-conflicts`, `autocommit`, `gc`, `repeatable-read`, `read-committed`, `isolation-levels`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0478_1f976abf1b`
- Source ID: `tidb-docs-8.1:pessimistic-transaction.md#difference-with-mysql-innodb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9fffe6689d3cc3ea5390bc7d474fb13dcd39922e6bc5682c2b86b7b0d86479e4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pessimistic-transaction#difference-with-mysql-innodb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pessimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB pessimistic transaction differences from MySQL InnoDB or which isolation levels are supported.
- Retrieval Keywords: Difference with MySQL InnoDB, gap locking, does not support SELECT LOCK IN SHARE MODE, Information schema is changed. [try again later], table doesn't exist, START TRANSACTION WITH CONSISTENT SNAPSHOT, autocommit transactions prefer the optimistic locking, Write Conflict, tidb_retry_limit, EMBEDDED SELECT, GC, max-txn-ttl, Repeatable Read, Read Committed, SET TRANSACTION
- Follow-up Guidance: It also states that TiDB supports Repeatable Read by default and Read Committed via the SET TRANSACTION statement in pessimistic transaction mode.
- Classification Note: This is classified as reference because the content lists compatibility differences, specific error behaviors, and supported isolation levels.

## Official Source Content

## Difference with MySQL InnoDB

1. When TiDB executes DML or `SELECT FOR UPDATE` statements that use range in the WHERE clause, concurrent DML statements within the range are not blocked.

    For example:

    ```sql
    CREATE TABLE t1 (
     id INT NOT NULL PRIMARY KEY,
     pad1 VARCHAR(100)
    );
    INSERT INTO t1 (id) VALUES (1),(5),(10);
    ```

    ```sql
    BEGIN /*T! PESSIMISTIC */;
    SELECT * FROM t1 WHERE id BETWEEN 1 AND 10 FOR UPDATE;
    ```

    ```sql
    BEGIN /*T! PESSIMISTIC */;
    INSERT INTO t1 (id) VALUES (6); -- blocks only in MySQL
    UPDATE t1 SET pad1='new value' WHERE id = 5; -- blocks waiting in both MySQL and TiDB
    ```

    This behavior is because TiDB does not currently support _gap locking_.

2. TiDB does not support `SELECT LOCK IN SHARE MODE`.

    When `SELECT LOCK IN SHARE MODE` is executed, it has the same effect as that without the lock, so the read or write operation of other transactions is not blocked.

3. DDL may result in failure of the pessimistic transaction commit.

    When DDL is executed in MySQL, it might be blocked by the transaction that is being executed. However, in this scenario, the DDL operation is not blocked in TiDB, which leads to failure of the pessimistic transaction commit: `ERROR 1105 (HY000): Information schema is changed. [try again later]`. TiDB executes the `TRUNCATE TABLE` statement during the transaction execution, which might result in the `table doesn't exist` error.

4. After executing `START TRANSACTION WITH CONSISTENT SNAPSHOT`, MySQL can still read the tables that are created later in other transactions, while TiDB cannot.

5. The autocommit transactions prefer the optimistic locking.

    When using the pessimistic model, the autocommit transactions first try to commit the statement using the optimistic model that has less overhead. If a write conflict occurs, the pessimistic model is used for transaction retry. Therefore, if `tidb_retry_limit` is set to `0`, the autocommit transaction still reports the `Write Conflict` error when a write conflict occurs.

    The autocommit `SELECT FOR UPDATE` statement does not wait for lock.

6. The data read by `EMBEDDED SELECT` in the statement is not locked.

7. Open transactions in TiDB do not block garbage collection (GC). By default, this limits the maximum execution time of pessimistic transactions to 1 hour. You can modify this limit by editing `max-txn-ttl` under `[performance]` in the TiDB configuration file.
## Isolation level

TiDB supports the following two isolation levels in the pessimistic transaction mode:

- [Repeatable Read](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#repeatable-read-isolation-level) by default, which is the same as MySQL.

    > **Note:**
    >
    > In this isolation level, DML operations are performed based on the latest committed data. The behavior is the same as MySQL, but differs from the optimistic transaction mode in TiDB. See [Difference between TiDB and MySQL Repeatable Read](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#difference-between-tidb-and-mysql-repeatable-read).

- [Read Committed](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#read-committed-isolation-level). You can set this isolation level using the [`SET TRANSACTION`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-transaction) statement.
