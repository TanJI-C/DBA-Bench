# Read Committed behavior, MySQL differences, and isolation level settings

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/transaction-isolation-levels.md`
- Source Title: `TiDB Transaction Isolation Levels`
- Source Heading Path: `TiDB Transaction Isolation Levels > Read Committed isolation level | TiDB Transaction Isolation Levels > Difference between TiDB and MySQL Read Committed | TiDB Transaction Isolation Levels > View and modify transaction isolation levels`
- Source Line Ranges: `64-118`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `read-committed`, `pessimistic-transactions`, `system-variables`, `timestamp-acquisition`, `read-write-conflicts`, `point-write`, `session-configuration`, `transaction-isolation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1051_f85b728f8d`
- Source ID: `tidb-docs-8.1:transaction-isolation-levels.md#read-committed-isolation-level`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `49151126a618284f3ce9d915a1a9359159030c1508b00c53b8b2182c703a4300`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#read-committed-isolation-level
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/transaction-isolation-levels.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB `READ-COMMITTED` behavior, its differences from MySQL, timestamp optimization variables for pessimistic transactions, or the SQL used to view and modify the session transaction isolation level.
- Retrieval Keywords: READ-COMMITTED, Read Committed isolation level, Difference between TiDB and MySQL Read Committed, transaction_isolation, SHOW VARIABLES LIKE 'transaction_isolation';, SET SESSION transaction_isolation = 'READ-COMMITTED';, tidb_rc_read_check_ts, tidb_rc_write_check_ts, tidb_init_chunk_size, tidb_max_chunk_size, pessimistic transaction mode, optimistic transaction mode, point-write statements, POINT-GET, SELECT FOR UPDATE, semi-consistent read
- Follow-up Guidance: The source explains that `tidb_rc_read_check_ts` and `tidb_rc_write_check_ts` optimize timestamp acquisition in `READ-COMMITTED` scenarios, and it lists `UPDATE`, `DELETE`, and `SELECT ...... FOR UPDATE` as applicable point-write statement types.
- Classification Note: This is reference content because it documents Read Committed semantics, exact system variables, MySQL behavior differences, and the SQL statements for checking or setting transaction isolation.

## Official Source Content

## Read Committed isolation level

Starting from TiDB v4.0.0-beta, TiDB supports the Read Committed isolation level.

For historical reasons, the Read Committed isolation level of current mainstream databases is essentially the [Consistent Read isolation level defined by Oracle](https://docs.oracle.com/cd/B19306_01/server.102/b14220/consist.htm). In order to adapt to this situation, the Read Committed isolation level in TiDB pessimistic transactions is also a consistent read behavior in essence.

> **Note:**
>
> The Read Committed isolation level only takes effect in the [pessimistic transaction mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction). In the [optimistic transaction mode](https://docs.pingcap.com/tidb/stable/optimistic-transaction), setting the transaction isolation level to `Read Committed` does not take effect and transactions still use the Repeatable Read isolation level.

Starting from v6.0.0, TiDB supports using the [`tidb_rc_read_check_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_rc_read_check_ts-new-in-v600) system variable to optimize the timestamp acquisition in scenarios where read-write conflicts are rare. After enabling this variable, TiDB will try to use the previous valid timestamp to read data when `SELECT` is executed. The initial value of this variable is the `start_ts` of the transaction.

- If TiDB does not encounter any data update during the read process, it returns the result to the client and the `SELECT` statement is successfully executed.
- If TiDB encounters data update during the read process:
    - If TiDB has not yet sent the result to the client, TiDB tries to acquire a new timestamp and retry this statement.
    - If TiDB has already sent partial data to the client, TiDB reports an error to the client. The amount of data sent to the client each time is controlled by [`tidb_init_chunk_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_init_chunk_size) and [`tidb_max_chunk_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_chunk_size).

In scenarios where the `READ-COMMITTED` isolation level is used, the `SELECT` statements are many, and read-write conflicts are rare, enabling this variable can avoid the latency and cost of getting the global timestamp.

Since v6.3.0, TiDB supports optimizing the acquisition of timestamps by enabling the system variable [`tidb_rc_write_check_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_rc_write_check_ts-new-in-v630) in scenarios where point-write conflicts are few. After enabling this variable, during the execution of point-write statements, TiDB will try to use valid timestamps of the current transaction to read and lock data. TiDB will read data in the same way when [`tidb_rc_read_check_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_rc_read_check_ts-new-in-v600) is enabled.

Currently, the applicable types of point-write statements include `UPDATE`, `DELETE`, and `SELECT ...... FOR UPDATE`. A point-write statement refers to a write statement that uses the primary key or unique key as a filter condition and the final execution operator contains `POINT-GET`. Currently, the three types of point-write statements have these in common: they first perform a point query based on the key value. If the key exists, they lock the key. If the key does not exist, they return an empty set.

- If the entire read process of a point-write statement does not encounter an updated data version, TiDB continues to use the timestamp of the current transaction to lock the data.
    - If a write conflict occurs due to an old timestamp during the lock acquisition process, TiDB retries the lock acquisition process by obtaining the latest global timestamp.
    - If no write conflicts or other errors occur during the lock acquisition process, the lock is acquired successfully.
- If an updated data version is encountered during the read process, TiDB tries to acquire a new timestamp and retries this statement.

In transactions with many point-write statements but a few point-write conflicts in the `READ-COMMITTED` isolation level, enabling this variable can avoid the latency and overhead of getting the global timestamp.
## Difference between TiDB and MySQL Read Committed

The MySQL Read Committed isolation level is in line with the Consistent Read features in most cases. There are also exceptions, such as [semi-consistent read](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html). This special behavior is not supported in TiDB.
## View and modify transaction isolation levels

You can view and modify the transaction isolation level as follows.

View the transaction isolation level of the current session:

```sql
SHOW VARIABLES LIKE 'transaction_isolation';
```

Modify the transaction isolation level of the current session:

```sql
SET SESSION transaction_isolation = 'READ-COMMITTED';
```

For more information on configuring and using transaction isolation levels, see the following documents:

- [The system variable `transaction_isolation`](https://docs.pingcap.com/tidb/stable/system-variables#transaction_isolation)
- [Isolation level](https://docs.pingcap.com/tidb/stable/pessimistic-transaction#isolation-level)
- [`SET TRANSACTION`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-transaction)
