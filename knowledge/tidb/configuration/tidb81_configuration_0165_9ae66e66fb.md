# DDL execution and accelerated table creation variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_ddl_error_count_limit | System Variables > Variable reference > tidb_ddl_flashback_concurrency <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_ddl_reorg_batch_size | System Variables > Variable reference > tidb_ddl_reorg_priority | System Variables > Variable reference > tidb_ddl_reorg_worker_cnt | System Variables > Variable reference > `tidb_enable_fast_create_table` <span class="version-mark">New in v8.0.0</span>`
- Source Line Ranges: `1646-1734`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`, `cloud`
- Topic Tags: `system-variables`, `ddl`, `flashback-cluster`, `add-index`, `reorg`, `concurrency`, `batch-size`, `priority`, `fast-create-table`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0165_9ae66e66fb`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-ddl-error-count-limit`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `df38eb9b89a1bd695c9dc77c61afbf65e59637b41fe709dff228b928f9d9bf4e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-ddl-error-count-limit
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving DDL-related system variables for retry limits, FLASHBACK CLUSTER concurrency, ADD INDEX re-organize batch size, worker count, execution priority, or the accelerated CREATE TABLE feature.
- Retrieval Keywords: tidb_ddl_error_count_limit, tidb_ddl_flashback_concurrency, FLASHBACK CLUSTER, tidb_ddl_reorg_batch_size, tidb_ddl_reorg_priority, tidb_ddl_reorg_worker_cnt, ADD INDEX, re-organize phase, PRIORITY_LOW, PRIORITY_NORMAL, PRIORITY_HIGH, tidb_enable_fast_create_table, TiDB Accelerated Table Creation, CREATE TABLE, tidb_ddl_version
- Follow-up Guidance: The content also states that tidb_enable_fast_create_table is an experimental feature and that tidb_ddl_version no longer takes effect starting from v8.0.0.
- Classification Note: This is classified as configuration because the content lists system variables that control DDL retries, concurrency, batch sizing, priority, and whether accelerated table creation is enabled.

## Official Source Content

### tidb_ddl_error_count_limit

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `512`
- Range: `[0, 9223372036854775807]`
- This variable is used to set the number of retries when the DDL operation fails. When the number of retries exceeds the parameter value, the wrong DDL operation is canceled.
### tidb_ddl_flashback_concurrency New in v6.3.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `64`
- Range: `[1, 256]`
- This variable controls the concurrency of [`FLASHBACK CLUSTER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster).
### tidb_ddl_reorg_batch_size

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `256`
- Range: `[32, 10240]`
- Unit: Rows
- This variable is used to set the batch size during the `re-organize` phase of the DDL operation. For example, when TiDB executes the `ADD INDEX` operation, the index data needs to backfilled by `tidb_ddl_reorg_worker_cnt` (the number) concurrent workers. Each worker backfills the index data in batches.
    - If `tidb_ddl_enable_fast_reorg` is set to `OFF`, `ADD INDEX` is executed as a transaction. If there are many update operations such as `UPDATE` and `REPLACE` in the target columns during the `ADD INDEX` execution, a larger batch size indicates a larger probability of transaction conflicts. In this case, it is recommended that you set the batch size to a smaller value. The minimum value is 32.
    - If the transaction conflict does not exist, or if `tidb_ddl_enable_fast_reorg` is set to `ON`, you can set the batch size to a large value. This makes data backfilling faster but also increases the write pressure on TiKV. For a proper batch size, you also need to refer to the value of `tidb_ddl_reorg_worker_cnt`. See [Interaction Test on Online Workloads and `ADD INDEX` Operations](https://docs.pingcap.com/tidb/dev/online-workloads-and-add-index-operations) for reference.
### tidb_ddl_reorg_priority

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `PRIORITY_LOW`
- Value options: `PRIORITY_LOW`, `PRIORITY_NORMAL`, `PRIORITY_HIGH`
- This variable is used to set the priority of executing the `ADD INDEX` operation in the `re-organize` phase.
- You can set the value of this variable to `PRIORITY_LOW`, `PRIORITY_NORMAL` or `PRIORITY_HIGH`.
### tidb_ddl_reorg_worker_cnt

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `4`
- Range: `[1, 256]`
- Unit: Threads
- This variable is used to set the concurrency of the DDL operation in the `re-organize` phase.
### `tidb_enable_fast_create_table` New in v8.0.0

> **Warning:**
>
> This variable is currently an experimental feature and it is not recommended to use in a production environment. This feature might change or be removed without prior notice. If you find a bug, please give feedback by raising an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to control whether to enable [TiDB Accelerated Table Creation](https://docs.pingcap.com/tidb/stable/accelerated-table-creation).
- Starting from v8.0.0, TiDB supports accelerating table creation by the [`CREATE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table) statement using `tidb_enable_fast_create_table`.
- This variable is renamed from the variable [`tidb_ddl_version`](https://docs.pingcap.com/tidb/v7.6/system-variables#tidb_ddl_version-new-in-v760) that is introduced in v7.6.0. Starting from v8.0.0, `tidb_ddl_version` no longer takes effect.
