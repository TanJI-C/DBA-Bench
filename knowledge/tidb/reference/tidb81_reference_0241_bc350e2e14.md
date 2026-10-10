# TiDB error codes overview and unique codes 8001-8051

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/error-codes.md`
- Source Title: `Error Codes and Troubleshooting`
- Source Heading Path: `Error Codes and Troubleshooting | Error Codes and Troubleshooting > Error codes`
- Source Line Ranges: `5-165`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `shared`
- Topic Tags: `error-codes`, `mysql-compatibility`, `memory-quota`, `transaction-retry`, `write-conflict`, `data-corruption`, `plugin`, `table-lock`, `schema-version`, `metadata-lock`, `isolation-level`, `privileges`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0241_bc350e2e14`
- Source ID: `tidb-docs-8.1:error-codes.md#error-codes-and-troubleshooting`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1edc663dded138d4a9080e017d97168656c1a0cf91a9881e0b5766a5110feb28`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/error-codes#error-codes-and-troubleshooting
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/error-codes.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB-specific error codes 8001-8051, their meanings, and the documented handling notes alongside MySQL compatibility context.
- Retrieval Keywords: Error Codes and Troubleshooting, TiDB error codes, MySQL 8.0 Error Message Reference, Error Number: 8001, tidb_mem_quota_query, Error Number: 8002, SELECT FOR UPDATE, commit conflict, Error Number: 8003, ADMIN CHECK TABLE, data corruption, Error Number: 8004, transaction too large, Error Number: 8005, ERROR 8005 (HY000): Write Conflict, txnStartTS is stale, write conflict, Error Number: 8018, plugin reload, Error Number: 8019, plugin version, Error Number: 8020, table is locked, Error Number: 8021, key to be read from TiKV does not exist, Error Number: 8022, transaction commit fails and has been rolled back, Error Number: 8024, invalid transactions, Start Timestamp, Error Number: 8025, txn-entry-size-limit, 6 MB, Error Number: 8027, table schema version is outdated, PD Leader, Error Number: 8028, Metadata lock, Read Committed, lossy column type change, Error Number: 8032, Invalid year format, Error Number: 8033, Invalid year value, Error Number: 8037, week function mode, Error Number: 8040, unsupported operations, Error Number: 8047, system variable is not supported, Error Number: 8048, unsupported database isolation level, tidb_skip_isolation_level_check, set @@tidb_skip_isolation_level_check = 1, Error Number: 8050, unsupported privilege type
- Follow-up Guidance: The source points to related references such as support, the `transaction too large` FAQ, Metadata lock, `tidb_mem_quota_query`, `txn-entry-size-limit`, `tidb_skip_isolation_level_check`, and Privileges required for TiDB operations for specific cases.
- Classification Note: This chunk is reference content because it enumerates TiDB unique error codes and states the corresponding meanings, internal-use notes, and linked handling guidance.

## Official Source Content

# Error Codes and Troubleshooting

This document describes the problems encountered during the use of TiDB and provides the solutions.
## Error codes

TiDB is compatible with the error codes in MySQL, and in most cases returns the same error code as MySQL. For a list of error codes for MySQL, see [MySQL 8.0 Error Message Reference](https://dev.mysql.com/doc/mysql-errors/8.0/en/). In addition, TiDB has the following unique error codes:

> **Note:**
>
> Some error codes stand for internal errors. Normally, TiDB handles the error rather than return it to the user, so some error codes are not listed here.
>
> If you encounter an error code that is not listed here, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

* Error Number: 8001

    The memory used by the request exceeds the threshold limit for the TiDB memory usage.

    Increase the memory limit for a single SQL statement by configuring the system variable [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query).

* Error Number: 8002

    To guarantee consistency, a transaction with the `SELECT FOR UPDATE` statement cannot be retried when it encounters a commit conflict. TiDB rolls back the transaction and returns this error.

    The application can safely retry the whole transaction.

* Error Number: 8003

    If the data in a row is not consistent with the index when executing the [`ADMIN CHECK TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-check-table-index) command, TiDB returns this error. This error is commonly seen when you check the data corruption in the table.

    You can [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

* Error Number: 8004

    A single transaction is too large.

    See [the error message `transaction too large`](https://docs.pingcap.com/tidb/stable/faq/migration-tidb-faq#the-error-message-transaction-too-large-is-displayed) for the cause and solution.

* Error Number: 8005

    The complete error message: `ERROR 8005 (HY000): Write Conflict, txnStartTS is stale`

    Transactions in TiDB encounter write conflicts. Check your application logic and retry the write operation.

* Error Number: 8018

    When you reload a plugin, if the plugin has not been loaded before, this error is returned.

    You can execute an initial load of the plugin.

* Error Number: 8019

    The version of the plugin that is being reloaded is different from the previous version. Therefore, the plugin cannot be reloaded, and this error is returned.

    You can reload the plugin by ensuring that the plugin version is the same as the previous one.

* Error Number: 8020

    When the table is locked, if you perform a write operation on the table, this error is returned.

    Unlock the table and retry the write operation.

* Error Number: 8021

    When the key to be read from TiKV does not exist, this error is returned. This error is used internally, and the external result is an empty read.

* Error Number: 8022

    The transaction commit fails and has been rolled back.

    The application can safely retry the whole transaction.

* Error Number: 8023

    If you set an empty value when writing the transaction cache, this error is returned. This error is used and dealt with internally, and is not returned to the application.

* Error Number: 8024

    Invalid transactions. If TiDB finds that no transaction ID (Start Timestamp) is obtained for the transaction that is being executed, which means this transaction is invalid, this error is returned.

    Usually this error does not occur. If you encounter this error, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

* Error Number: 8025

    The single Key-Value pair being written is too large. The largest single Key-Value pair supported in TiDB is 6 MB by default.

    If a pair exceeds this limit, you need to properly adjust the [`txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500) configuration value to relax the limit.

* Error Number: 8026

    The interface function being used has not been implemented. This error is only used internally, and is not returned to the application.

* Error Number: 8027

    The table schema version is outdated. TiDB applies schema changes online. When the table schema version of the TiDB server is earlier than that of the entire system, this error is returned if you execute a SQL statement.

    When this error occurs, check the network between the TiDB server and the PD Leader.

* Error Number: 8028

    Since v6.3.0, TiDB introduces the [Metadata lock](https://docs.pingcap.com/tidb/stable/metadata-lock) feature. When the metadata lock is disabled and a transaction is executed, the transaction cannot recognize the table schema changes. Therefore, when the transaction is committed, TiDB checks the table schema related to the transaction. If the related table schema has been changed during the execution, the transaction commit fails with this error. At this time, the application can safely retry the whole transaction.

    When the metadata lock is enabled not in the Read Committed isolation level, if a lossy column type change occurs on a table (for example, changing from `INT` to `CHAR` is lossy, and changing from `TINYINT` to `INT` is not lossy because overwriting data is not required) from a transaction start to access the table for the first time, then the query fails while the transaction will not roll back automatically. You can continue to execute other statements and decide whether to roll back or commit the transaction.

* Error Number: 8029

    This error occurs when numeric conversion within the database encounters an error. This error is only used internally and is converted to a specific type of error for external applications.

* Error Number: 8030

    After an unsigned positive integer is converted to a signed integer, it exceeds the maximum value and displays as a negative integer. This error mostly occurs in the alert message.

* Error Number: 8031

    When being converted to an unsigned integer, a negative integer is converted to a positive integer. This error mostly occurs in the alert message.

* Error Number: 8032

    Invalid `year` format is used. `year` only accepts 1, 2 or 4 digits.

* Error Number: 8033

    Invalid `year` value is used. The valid range of `year` is (1901, 2155).

* Error Number: 8037

    Invalid `mode` format is used in the `week` function. `mode` must be 1 digit within [0, 7].

* Error Number: 8038

    The field fails to obtain the default value. This error is usually used internally, and is converted to a specific type of error for external applications.

* Error Number: 8040

    Unsupported operations are performed. For example, you perform a table locking operation on a view or a sequence.

* Error Number: 8047

    The value of the system variable is not supported. This error usually occurs in the alarm information when the user sets a variable value that is not supported in the database.

* Error Number: 8048

    An unsupported database isolation level is set.

    If you cannot modify the codes because you are using a third-party tool or framework, consider using [`tidb_skip_isolation_level_check`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_skip_isolation_level_check) to bypass this check.

    ```sql
    set @@tidb_skip_isolation_level_check = 1;
    ```

* Error Number: 8050

    An unsupported privilege type is set.

    See [Privileges required for TiDB operations](https://docs.pingcap.com/tidb/stable/privilege-management#privileges-required-for-tidb-operations) for the solution.

* Error Number: 8051
