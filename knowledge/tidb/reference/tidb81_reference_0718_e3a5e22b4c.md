# Transaction retry, DML mode, scan concurrency, and 1PC variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_disable_txn_auto_retry | System Variables > Variable reference > tidb_distsql_scan_concurrency | System Variables > Variable reference > tidb_dml_batch_size | System Variables > Variable reference > tidb_dml_type <span class="version-mark">New in v8.0.0</span> | System Variables > Variable reference > tidb_enable_1pc <span class="version-mark">New in v5.0</span>`
- Source Line Ranges: `1749-1861`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `ticdc`, `tiflash`, `br`
- Topic Tags: `system-variables`, `transactions`, `optimistic-transactions`, `retry`, `dml`, `bulk-write`, `scan-concurrency`, `olap`, `oltp`, `one-phase-commit`, `deprecated`, `experimental`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0718_e3a5e22b4c`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-disable-txn-auto-retry`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `88d0d076c9f863b7bf4db1d9417b12c031ef1384a7cdb508f07bea45f87a6068`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-disable-txn-auto-retry
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB system variable reference details for optimistic transaction auto retry deprecation, scan concurrency tuning, deprecated batch DML sizing, experimental bulk DML mode, or one-phase commit behavior.
- Retrieval Keywords: tidb_disable_txn_auto_retry, optimistic transactions, automatic retries of optimistic transactions, COMMIT statements might return errors, tidb_retry_limit, max_retry_count, tidb_distsql_scan_concurrency, scan concurrency, OLAP scenarios, OLTP scenarios, LIMIT value is less than 100000, SELECT MAX/MIN(col) FROM ..., tidb_dml_batch_size, batch-dml feature, tidb_enable_batch_dml, tidb_batch_insert, tidb_batch_delete, LOAD DATA statement, tidb_dml_type, bulk DML execution mode, standard, bulk, INSERT IGNORE ... ON DUPLICATE UPDATE ..., Duplicate entry error, pessimistic-auto-commit, metadata lock, temporary tables, cached tables, foreign_key_checks = ON, tidb_last_txn_info, pipelined field, max-txn-ttl, tidb_gc_max_wait_time, txn-total-size-limit, Pipelined DML, #50215, tidb_enable_1pc, one-phase commit, transactions that only affect one Region, two-phase commit, TiDB Binlog, TiCDC
- Follow-up Guidance: The content also points to related identifiers and checks such as tidb_last_txn_info.pipelined for verifying bulk mode usage, tidb_retry_limit and max_retry_count for retry behavior, and TiCDC when TiDB Binlog is enabled.
- Classification Note: This is reference content because it defines TiDB system variables with scope, type, defaults, value options, warnings, and exact behavior notes for transactions, DML execution, scan concurrency, and 1PC.

## Official Source Content

### tidb_disable_txn_auto_retry

> **Warning:**
>
> Starting from v8.0.0, this variable is deprecated, and TiDB no longer supports automatic retries of optimistic transactions. As an alternative, when encountering optimistic transaction conflicts, you can capture the error and retry transactions in your application, or use the [Pessimistic transaction mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction) instead.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to set whether to disable the automatic retry of explicit optimistic transactions. The default value of `ON` means that transactions will not automatically retry in TiDB and `COMMIT` statements might return errors that need to be handled in the application layer.

    Setting the value to `OFF` means that TiDB will automatically retry transactions, resulting in fewer errors from `COMMIT` statements. Be careful when making this change, because it might result in lost updates.

    This variable does not affect automatically committed implicit transactions and internally executed transactions in TiDB. The maximum retry count of these transactions is determined by the value of `tidb_retry_limit`.

    For more details, see [limits of retry](https://docs.pingcap.com/tidb/stable/optimistic-transaction#limits-of-retry).

    This variable only applies to optimistic transactions, not to pessimistic transactions. The number of retries for pessimistic transactions is controlled by [`max_retry_count`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#max-retry-count).

    This variable only applies to optimistic transactions, not to pessimistic transactions. The number of retries for pessimistic transactions is 256.
### tidb_distsql_scan_concurrency

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `15`
- Range: `[1, 256]`
- Unit: Threads
- This variable is used to set the concurrency of the `scan` operation.
- Use a bigger value in OLAP scenarios, and a smaller value in OLTP scenarios.
- For OLAP scenarios, the maximum value should not exceed the number of CPU cores of all the TiKV nodes.
- If a table has a lot of partitions, you can reduce the variable value appropriately (determined by the size of the data to be scanned and the frequency of the scan) to avoid TiKV becoming out of memory (OOM).
- For a simple query with only a `LIMIT` clause, if the `LIMIT` value is less than 100000, the scan operation pushed down to TiKV treats the value of this variable as `1` to enhance execution efficiency.
- For the `SELECT MAX/MIN(col) FROM ...` query, if the `col` column has an index sorted in the same order required by the `MAX(col)` or `MIN(col)` function, TiDB will rewrite the query to `SELECT col FROM ... LIMIT 1` for processing, and the value of this variable will also be processed as `1`. For example, for `SELECT MIN(col) FROM ...`, if the `col` column has an ascending index, TiDB can quickly obtain the `MIN(col)` value by rewriting the query to `SELECT col FROM ... LIMIT 1` and directly reading the first row of the index.
### tidb_dml_batch_size

> **Warning:**
>
> This variable is associated with the deprecated batch-dml feature, which might cause data corruption. Therefore, it is not recommended to enable this variable for batch-dml. Instead, use [non-transactional DML](https://docs.pingcap.com/tidb/stable/non-transactional-dml).

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 2147483647]`
- Unit: Rows
- When this value is greater than `0`, TiDB will batch commit statements such as `INSERT` into smaller transactions. This reduces memory usage and helps ensure that the `txn-total-size-limit` is not reached by bulk modifications.
- Only the value `0` provides ACID compliance. Setting this to any other value will break the atomicity and isolation guarantees of TiDB.
- To make this variable work, you also need to enable `tidb_enable_batch_dml` and at least one of `tidb_batch_insert` and `tidb_batch_delete`.

> **Note:**
>
> Starting from v7.0.0, `tidb_dml_batch_size` no longer takes effect on the [`LOAD DATA` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data).
### tidb_dml_type New in v8.0.0

> **Warning:**
>
> The bulk DML execution mode (`tidb_dml_type = "bulk"`) is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues). In the current version, when TiDB performs large transactions using the bulk DML mode, it might affect the memory usage and execution efficiency of TiCDC, TiFlash, and the resolved-ts module of TiKV, and might cause OOM issues. Additionally, BR might be blocked and fail to process when encountering locks. Therefore, it is not recommended to use this mode when these components or features are enabled.

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: String
- Default value: `"standard"`
- Value options: `"standard"`, `"bulk"`
- This variable controls the execution mode of DML statements.
    - `"standard"` indicates the standard DML execution mode, where TiDB transactions are cached in memory before being committed. This mode is suitable for high-concurrency transaction scenarios with potential conflicts and is the default recommended execution mode.
    - `"bulk"` indicates the bulk DML execution mode, which is suitable for scenarios where a large amount of data is written, causing excessive memory usage in TiDB.
        - During the execution of TiDB transactions, the data is not fully cached in the TiDB memory, but is continuously written to TiKV to reduce memory usage and smooth the write pressure.
        - Only `INSERT`, `UPDATE`, `REPLACE`, and `DELETE` statements are affected by the `"bulk"` mode. Due to the pipelined execution in `"bulk"` mode, the usage of `INSERT IGNORE ... ON DUPLICATE UPDATE ...` might result in a `Duplicate entry` error when updates cause conflicts. In contrast, in `"standard"` mode, because the `IGNORE` keyword is set, this error would be ignored and not be returned to the user.
        - `"bulk"` mode is only suitable for scenarios where a large amount of **data is written without conflicts**. This mode is not efficient for handling write conflicts, as write-write conflicts might cause large transactions to fail and be rolled back.
        - `"bulk"` mode only takes effect on statements with auto-commit enabled, and requires the [`pessimistic-auto-commit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#pessimistic-auto-commit-new-in-v600) configuration item to be set to `false`.
        - When using the `"bulk"` mode to execute statements, ensure that the [metadata lock](https://docs.pingcap.com/tidb/stable/metadata-lock) remains enabled during the execution process.
        - `"bulk"` mode cannot be used on [temporary tables](https://docs.pingcap.com/tidb/stable/temporary-tables) and [cached tables](https://docs.pingcap.com/tidb/stable/cached-tables).
        - `"bulk"` mode cannot be used on tables containing foreign keys and tables referenced by foreign keys when the foreign key constraint check is enabled (`foreign_key_checks = ON`).
        - In situations that the environment does not support or is incompatible with the `"bulk"` mode, TiDB falls back to the `"standard"` mode and returns a warning message. To verify if the `"bulk"` mode is used, you can check the `pipelined` field using [`tidb_last_txn_info`](#tidb_last_txn_info-new-in-v409). A `true` value indicates that the `"bulk"` mode is used.
        - When executing large transactions in the `"bulk"` mode, the transaction duration might be long. For transactions in this mode, the maximum TTL of the transaction lock is the greater value between [`max-txn-ttl`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#max-txn-ttl) and 24 hours. Additionally, if the transaction execution time exceeds the value set by [`tidb_gc_max_wait_time`](#tidb_gc_max_wait_time-new-in-v610), the GC might force a rollback of the transaction, leading to its failure.
        - When TiDB executes transactions in the `"bulk"` mode, transaction size is not limited by the TiDB configuration item [`txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit).
        - This mode is implemented by the Pipelined DML feature. For detailed design and GitHub issues, see [Pipelined DML](https://github.com/pingcap/tidb/blob/release-8.1/docs/design/2024-01-09-pipelined-DML.md) and [#50215](https://github.com/pingcap/tidb/issues/50215).
### tidb_enable_1pc New in v5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to specify whether to enable the one-phase commit feature for transactions that only affect one Region. Compared with the often-used two-phase commit, one-phase commit can greatly reduce the latency of transaction commit and increase the throughput.

> **Note:**
>
> - The default value of `ON` only applies to new clusters. if your cluster was upgraded from an earlier version of TiDB, the value `OFF` will be used instead.
> - If you have enabled TiDB Binlog, enabling this variable cannot improve the performance. To improve the performance, it is recommended to use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview) instead.
> - Enabling this parameter only means that one-phase commit becomes an optional mode of transaction commit. In fact, the most suitable mode of transaction commit is determined by TiDB.
