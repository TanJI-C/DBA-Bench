# LOAD DATA compatibility and related references

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-load-data.md`
- Source Title: `LOAD DATA | TiDB SQL Statement Reference`
- Source Heading Path: `LOAD DATA > MySQL compatibility | LOAD DATA > See also`
- Source Line Ranges: `182-236`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `cloud`
- Topic Tags: `mysql-compatibility`, `syntax`, `character-set`, `transactions`, `rollback`, `optimistic-transactions`, `pessimistic-transactions`, `version-behavior`, `upgrade`, `transaction-size-limit`, `see-also`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0607_3923b660c7`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-load-data.md#mysql-compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bf7875724b0b99d2b1191ad947fd8e67bb20e1e2511390a16c10265b0aa6fb38`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-load-data.md

## Retrieval Guidance

- Use When: Use this chunk when checking LOAD DATA MySQL compatibility details, transaction and rollback behavior across TiDB versions, or the transaction-size-limit error after upgrades.
- Retrieval Keywords: LOAD DATA, MySQL compatibility, character set options parsed but ignored, tidb_dml_batch_size, txn-total-size-limit, ERROR 8004 (HY000) at line 1: Transaction is too large, size: 100000058, ROLLBACK, optimistic transaction mode, pessimistic transaction, TiDB v4.0.0, v6.6.0, v7.0.0, v7.6.0, INSERT, TiDB Optimistic Transaction Model, TiDB Pessimistic Transaction Mode
- Follow-up Guidance: See also INSERT, TiDB Optimistic Transaction Model, and TiDB Pessimistic Transaction Mode.
- Classification Note: This is reference content because it summarizes official LOAD DATA compatibility notes, version-specific transaction behavior, related error text, and links to related SQL and transaction documentation.

## Official Source Content

## MySQL compatibility

The syntax of the `LOAD DATA` statement is compatible with that of MySQL, except for character set options which are parsed but ignored. If you find any syntax compatibility difference, you can [report a bug](https://docs.pingcap.com/tidb/stable/support).

> **Note:**
>
> - For versions earlier than TiDB v4.0.0, `LOAD DATA` commits every 20000 rows, which cannot be configured.
> - For versions from TiDB v4.0.0 to v6.6.0, TiDB commits all rows in one transaction by default. But if you need the `LOAD DATA` statement to commit every fixed number of rows, you can set [`tidb_dml_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_batch_size) to the desired number of rows.
> - Starting from TiDB v7.0.0, `tidb_dml_batch_size` no longer takes effect on `LOAD DATA`, and TiDB commits all rows in one transaction.
> - After upgrading from TiDB v4.0.0 or earlier versions, `ERROR 8004 (HY000) at line 1: Transaction is too large, size: 100000058` might occur. The recommended way to resolve this error is to increase the [`txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit) value in your `tidb.toml` file.
> - For versions earlier than TiDB v7.6.0, no matter how many rows are committed in a transaction, `LOAD DATA` is not rolled back by the [`ROLLBACK`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rollback) statement in an explicit transaction.
> - For versions earlier than TiDB v7.6.0, the `LOAD DATA` statement is always executed in optimistic transaction mode, regardless of the TiDB transaction mode configuration.
> - Starting from v7.6.0, TiDB processes `LOAD DATA` in transactions in the same way as other DML statements:
>     - The `LOAD DATA` statement does not commit the current transaction or start a new transaction.
>     - The `LOAD DATA` statement is affected by the TiDB transaction mode setting (optimistic or pessimistic transaction).
>     - The `LOAD DATA` statement in a transaction can be rolled back by the [`ROLLBACK`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rollback) statement in the transaction.

> **Note:**
>
> - For versions earlier than TiDB v4.0.0, `LOAD DATA` commits every 20000 rows, which cannot be configured.
> - For versions from TiDB v4.0.0 to v6.6.0, TiDB commits all rows in one transaction by default. But if you need the `LOAD DATA` statement to commit every fixed number of rows, you can set [`tidb_dml_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_batch_size) to the desired number of rows.
> - Starting from v7.0.0, `tidb_dml_batch_size` no longer takes effect on `LOAD DATA`, and TiDB commits all rows in one transaction.
> - After upgrading from TiDB v4.0.0 or earlier versions, `ERROR 8004 (HY000) at line 1: Transaction is too large, size: 100000058` might occur. To resolve this error, you can contact [TiDB Cloud Support](https://docs.pingcap.com/tidbcloud/tidb-cloud-support) to increase the [`txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit) value.
> - For versions earlier than TiDB v7.6.0, no matter how many rows are committed in a transaction, `LOAD DATA` is not rolled back by the [`ROLLBACK`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rollback) statement in an explicit transaction.
> - For versions earlier than TiDB v7.6.0, the `LOAD DATA` statement is always executed in optimistic transaction mode, regardless of the TiDB transaction mode configuration.
> - Starting from v7.6.0, TiDB processes `LOAD DATA` in transactions in the same way as other DML statements:
>     - The `LOAD DATA` statement does not commit the current transaction or start a new transaction.
>     - The `LOAD DATA` statement is affected by the TiDB transaction mode setting (optimistic or pessimistic transaction).
>     - The `LOAD DATA` statement in a transaction can be rolled back by the [`ROLLBACK`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rollback) statement in the transaction.
## See also

* [INSERT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-insert)
* [TiDB Optimistic Transaction Model](https://docs.pingcap.com/tidb/stable/optimistic-transaction)
* [TiDB Pessimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction)

* [INSERT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-insert)
* [TiDB Optimistic Transaction Model](https://docs.pingcap.com/tidb/stable/optimistic-transaction)
* [TiDB Pessimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction)
