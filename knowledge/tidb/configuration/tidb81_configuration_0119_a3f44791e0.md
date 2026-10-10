# Optimistic transaction retries, automatic retry settings, and retry limits

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimistic-transaction.md`
- Source Title: `TiDB Optimistic Transaction Model`
- Source Heading Path: `TiDB Optimistic Transaction Model > Transaction retries | TiDB Optimistic Transaction Model > Transaction retries > Automatic retry | TiDB Optimistic Transaction Model > Transaction retries > Limits of retry`
- Source Line Ranges: `65-137`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `transaction-retries`, `automatic-retry`, `system-variables`, `repeatable-read`, `write-conflicts`, `deprecated-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0119_a3f44791e0`
- Source ID: `tidb-docs-8.1:optimistic-transaction.md#transaction-retries`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6dfdf2d9b3cde1b26ca48c1ff1de97784b8d61ef9c9c5aefd32df886270575c9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimistic-transaction#transaction-retries
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving information about optimistic transaction retries, the `tidb_disable_txn_auto_retry` and `tidb_retry_limit` settings, deprecation of automatic retry, and retry effects on `REPEATABLE READ` isolation.
- Retrieval Keywords: Transaction retries, Automatic retry, Limits of retry, tidb_disable_txn_auto_retry, tidb_retry_limit, SET tidb_disable_txn_auto_retry = OFF, SET GLOBAL tidb_disable_txn_auto_retry = OFF, SET tidb_retry_limit = 10, SET GLOBAL tidb_retry_limit = 10, try again later, REPEATABLE READ, write-write conflict, automatic retries of optimistic transactions are no longer supported
- Follow-up Guidance: The source states that starting from v8.0.0 `tidb_disable_txn_auto_retry` is deprecated and TiDB no longer supports automatic retries of optimistic transactions, and conflicting transactions can report failures to the application layer.
- Classification Note: This is classified as configuration because the content centers on system variables, SQL `SET` statements, retry limits, and behavior controlled by configuration.

## Official Source Content

## Transaction retries

> **Note:**
>
> Starting from v8.0.0, the [`tidb_disable_txn_auto_retry`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_disable_txn_auto_retry) system variable is deprecated, and TiDB no longer supports automatic retries of optimistic transactions. It is recommended to use the [Pessimistic transaction mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction). If you encounter optimistic transaction conflicts, you can capture the error and retry transactions in your application.

In the optimistic transaction model, transactions might fail to be committed because of write–write conflict in heavy contention scenarios. Starting from v3.0.8, TiDB uses the [pessimistic transaction mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction) by default, the same as MySQL. This means that TiDB and MySQL add locks during the execution of write-type SQL statements, and its Repeatable Read isolation level allows for current reads, so commits generally do not encounter exceptions.
### Automatic retry

> **Note:**
>
> - Starting from TiDB v3.0.0, the automatic retry of transactions is disabled by default, because it can **break the transaction isolation level**. 
> - Starting from TiDB v8.0.0, automatic retries of optimistic transactions are no longer supported.

If a write-write conflict occurs during the transaction commit, TiDB automatically retries the SQL statement that includes write operations. You can enable the automatic retry by setting `tidb_disable_txn_auto_retry` to `OFF` and set the retry limit by configuring `tidb_retry_limit`:

```toml
# Whether to disable automatic retry. ("on" by default)
tidb_disable_txn_auto_retry = OFF
# Set the maximum number of the retires. ("10" by default)
# When "tidb_retry_limit = 0", automatic retry is completely disabled.
tidb_retry_limit = 10
```

You can enable the automatic retry in either session level or global level:

1. Session level:

    ```sql
    SET tidb_disable_txn_auto_retry = OFF;
    ```

    ```sql
    SET tidb_retry_limit = 10;
    ```

2. Global level:

    ```sql
    SET GLOBAL tidb_disable_txn_auto_retry = OFF;
    ```

    ```sql
    SET GLOBAL tidb_retry_limit = 10;
    ```

> **Note:**
>
> The `tidb_retry_limit` variable decides the maximum number of retries. When this variable is set to `0`, none of the transactions automatically retries, including the implicit single statement transactions that are automatically committed. This is the way to completely disable the automatic retry mechanism in TiDB. After the automatic retry is disabled, all conflicting transactions report failures (including the `try again later` message) to the application layer in the fastest way.
### Limits of retry

By default, TiDB will not retry transactions because this might lead to lost updates and damaged [`REPEATABLE READ` isolation](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels).

The reason can be observed from the procedures of retry:

1. Allocate a new timestamp and mark it as `start_ts`.
2. Retry the SQL statements that contain write operations.
3. Implement the two-phase commit.

In Step 2, TiDB only retries SQL statements that contain write operations. However, during retrying, TiDB receives a new version number to mark the beginning of the transaction. This means that TiDB retries SQL statements with the data in the new `start_ts` version. In this case, if the transaction updates data using other query results, the results might be inconsistent because the `REPEATABLE READ` isolation is violated.

If your application can tolerate lost updates, and does not require `REPEATABLE READ` isolation consistency, you can enable this feature by setting `tidb_disable_txn_auto_retry = OFF`.
