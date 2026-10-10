# Transaction control and plan baseline variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_txn_assertion_level <span class="version-mark">New in v6.0.0</span> | System Variables > Variable reference > tidb_txn_commit_batch_size <span class="version-mark">New in v6.2.0</span> | System Variables > Variable reference > tidb_txn_entry_size_limit <span class="version-mark">New in v7.6.0</span> | System Variables > Variable reference > tidb_txn_mode | System Variables > Variable reference > tidb_use_plan_baselines <span class="version-mark">New in v4.0</span>`
- Source Line Ranges: `5912-6000`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `tikv`, `cloud`, `sql`
- Topic Tags: `transactions`, `assertion-checks`, `commit-batching`, `entry-size-limit`, `transaction-mode`, `plan-baselines`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0170_c30e6cb306`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-txn-assertion-level-span-class-version-mark-new-in-v6-0-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1714900bac8ebc6b75fdf6686b94a3d80ef57011365662ebba5d43c63465e540`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-txn-assertion-level-span-class-version-mark-new-in-v6-0-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about TiDB system variables for transaction assertion checks, transaction commit batch size, transaction entry size limit, transaction mode, or enabling execution plan binding.
- Retrieval Keywords: tidb_txn_assertion_level, OFF FAST STRICT, assertion level, consistency check between data and indexes, tidb_txn_commit_batch_size, batch size of transaction commit requests, raft-entry-max-size, maximum size of a single log, tidb_txn_entry_size_limit, performance.txn-entry-size-limit, single row of data in TiDB, SESSION | GLOBAL, tidb_txn_mode, pessimistic, optimistic, tidb_use_plan_baselines, execution plan binding, plan baselines
- Follow-up Guidance: The content links to Troubleshoot Inconsistency Between Data and Indexes for assertion details and to Execution Plan Binding for the execution plan binding feature.
- Classification Note: This is classified as configuration because the content defines TiDB system variables that govern transaction behavior, size limits, transaction mode, and plan baseline usage.

## Official Source Content

### tidb_txn_assertion_level New in v6.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `FAST`
- Possible values: `OFF`, `FAST`, `STRICT`
- This variable is used to control the assertion level. Assertion is a consistency check between data and indexes, which checks whether a key being written exists in the transaction commit process. For more information, see [Troubleshoot Inconsistency Between Data and Indexes](https://docs.pingcap.com/tidb/stable/troubleshoot-data-inconsistency-errors).

    - `OFF`: Disable this check.
    - `FAST`: Enable most of the check items, with almost no impact on performance.
    - `STRICT`: Enable all check items, with a minor impact on pessimistic transaction performance when the system workload is high.

- For new clusters of v6.0.0 or later versions, the default value is `FAST`. For existing clusters that upgrade from versions earlier than v6.0.0, the default value is `OFF`.
### tidb_txn_commit_batch_size New in v6.2.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `16384`
- Range: `[1, 1073741824]`
- Unit: Bytes

- This variable is used to control the batch size of transaction commit requests that TiDB sends to TiKV. If most of the transactions in the application workload have a large number of write operations, adjusting this variable to a larger value can improve the performance of batch processing. However, if this variable is set to too large a value and exceeds the limit of TiKV's [`raft-entry-max-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raft-entry-max-size), the commits might fail.

- This variable is used to control the batch size of transaction commit requests that TiDB sends to TiKV. If most of the transactions in the application workload have a large number of write operations, adjusting this variable to a larger value can improve the performance of batch processing. However, if this variable is set to too large a value and exceeds the limit of TiKV's maximum size of a single log (which is 8 MiB by default), the commits might fail.
### tidb_txn_entry_size_limit New in v7.6.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 125829120]`
- Unit: Bytes

- This variable is used to dynamically modify the TiDB configuration item [`performance.txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500). It limits the size of a single row of data in TiDB, which is equivalent to the configuration item. The default value of this variable is `0`, which means that TiDB uses the value of the configuration item `txn-entry-size-limit` by default. When this variable is set to a non-zero value, `txn-entry-size-limit` is also set to the same value.

- This variable is used to dynamically modify the TiDB configuration item [`performance.txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500). It limits the size of a single row of data in TiDB, which is equivalent to the configuration item. The default value of this variable is `0`, which means that TiDB uses the value of the configuration item `txn-entry-size-limit` by default. When this variable is set to a non-zero value, `txn-entry-size-limit` is also set to the same value.

> **Note:**
>
> Modifying this variable with the SESSION scope only affects the current user session, not the internal TiDB session. This might lead to transaction failure if the entry size of an internal TiDB transaction exceeds the limit of the configuration item. Therefore, to dynamically increase the limit, it is recommended that you modify the variable with the GLOBAL scope.
### tidb_txn_mode

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `pessimistic`
- Possible values: `pessimistic`, `optimistic`
- This variable is used to set the transaction mode. TiDB 3.0 supports the pessimistic transactions. Since TiDB 3.0.8, the [pessimistic transaction mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction) is enabled by default.
- If you upgrade TiDB from v3.0.7 or earlier versions to v3.0.8 or later versions, the default transaction mode does not change. **Only the newly created clusters use the pessimistic transaction mode by default**.
- If this variable is set to "optimistic" or "", TiDB uses the [optimistic transaction mode](https://docs.pingcap.com/tidb/stable/optimistic-transaction).
### tidb_use_plan_baselines New in v4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to enable the execution plan binding feature. It is enabled by default, and can be disabled by assigning the `OFF` value. For the use of the execution plan binding, see [Execution Plan Binding](https://docs.pingcap.com/tidb/stable/sql-plan-management#create-a-binding).
