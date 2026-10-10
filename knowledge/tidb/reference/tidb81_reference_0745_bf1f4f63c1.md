# TiDB system variables for read-only mode, internal concurrency, Top SQL, TSO, and TTL

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_streamagg_concurrency | System Variables > Variable reference > tidb_super_read_only <span class="version-mark">New in v5.3.1</span> | System Variables > Variable reference > tidb_sysdate_is_now <span class="version-mark">New in v6.0.0</span> | System Variables > Variable reference > tidb_sysproc_scan_concurrency <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > tidb_table_cache_lease <span class="version-mark">New in v6.0.0</span> | System Variables > Variable reference > tidb_tmp_table_max_size <span class="version-mark">New in v5.3.0</span> | System Variables > Variable reference > tidb_top_sql_max_meta_count <span class="version-mark">New in v6.0.0</span> | System Variables > Variable reference > tidb_top_sql_max_time_series_count <span class="version-mark">New in v6.0.0</span> | System Variables > Variable reference > tidb_track_aggregate_memory_usage | System Variables > Variable reference > tidb_tso_client_batch_max_wait_time <span class="version-mark">New in v5.3.0</span> | System Variables > Variable reference > tidb_ttl_delete_rate_limit <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > tidb_ttl_delete_batch_size <span class="version-mark">New in v6.5.0</span>`
- Source Line Ranges: `5628-5819`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `dashboard`, `cloud`
- Topic Tags: `system-variables`, `read-only`, `concurrency`, `top-sql`, `tso`, `ttl`, `temporary-tables`, `cached-tables`, `memory-tracking`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0745_bf1f4f63c1`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-streamagg-concurrency`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8c7eaafd8c96d98bc360fb0840be8a25ae3cd8c3239a7e68c94e2bfbced0781f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-streamagg-concurrency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables related to read-only mode, internal scan concurrency, temporary or cached table limits, Top SQL collection limits, TSO batch wait time, TTL delete controls, or aggregate memory tracking.
- Retrieval Keywords: tidb_streamagg_concurrency, StreamAgg operator concurrency, tidb_super_read_only, read-only status of the entire cluster, RESTRICTED_REPLICA_WRITER_ADMIN, tidb_sysdate_is_now, SYSDATE replaced by NOW, tidb_sysproc_scan_concurrency, internal SQL statements automatic update of statistics, tidb_table_cache_lease, cached tables lease time, tidb_tmp_table_max_size, temporary table maximum size causes error, tidb_top_sql_max_meta_count, Top SQL maximum number of SQL statement types per minute, tidb_top_sql_max_time_series_count, Top SQL top N recorded per minute, tidb_track_aggregate_memory_usage, tracks the memory usage of aggregate functions, tidb_tso_client_batch_max_wait_time, maximum waiting time for a batch operation when TiDB requests TSO from PD, PD Client batch merge TSO requests, tidb_ttl_delete_rate_limit, limit the rate of DELETE statements in TTL jobs, tidb_ttl_delete_batch_size, maximum number of rows deleted in a single DELETE transaction in a TTL job
- Follow-up Guidance: The content also points to related details for tidb_restricted_read_only, cached tables, temporary tables, Top SQL, and Time to Live.
- Classification Note: This is reference content because it lists system variable definitions, scopes, defaults, ranges, notes, and behavior for TiDB variables.

## Official Source Content

### tidb_streamagg_concurrency

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1`
- This variable sets the concurrency of the `StreamAgg` operator when queries are executed.
- It is **NOT recommended** to set this variable. Modifying the variable value might cause data correctness issues.
### tidb_super_read_only New in v5.3.1

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- `tidb_super_read_only` aims to be implemented as a replacement of the MySQL variable `super_read_only`. However, because TiDB is a distributed database, `tidb_super_read_only` does not make the database read-only immediately after execution, but eventually.
- Users with the `SUPER` or `SYSTEM_VARIABLES_ADMIN` privilege can modify this variable.
- This variable controls the read-only status of the entire cluster. When the variable is `ON`, all TiDB servers in the entire cluster are in the read-only mode. In this case, TiDB only executes the statements that do not modify data, such as `SELECT`, `USE`, and `SHOW`. For other statements such as `INSERT` and `UPDATE`, TiDB rejects executing those statements in the read-only mode.
- Enabling the read-only mode using this variable only ensures that the entire cluster finally enters the read-only status. If you have changed the value of this variable in a TiDB cluster but the change has not yet propagated to other TiDB servers, the un-updated TiDB servers are still **not** in the read-only mode.
- TiDB checks the read-only flag before SQL statements are executed. Since v6.2.0, the flag is also checked before SQL statements are committed. This helps prevent the case where long-running [auto commit](https://docs.pingcap.com/tidb/stable/transaction-overview#autocommit) statements might modify data after the server has been placed in read-only mode.
- When this variable is enabled, TiDB handles the uncommitted transactions in the following ways:
    - For uncommitted read-only transactions, you can commit the transactions normally.
    - For uncommitted transactions that are not read-only, SQL statements that perform write operations in these transactions are rejected.
    - For uncommitted read-only transactions with modified data, the commit of these transactions is rejected.
- After the read-only mode is enabled, all users (including the users with the `SUPER` privilege) cannot execute the SQL statements that might write data unless the user is explicitly granted the `RESTRICTED_REPLICA_WRITER_ADMIN` privilege.
- When the [`tidb_restricted_read_only`](#tidb_restricted_read_only-new-in-v520) system variable is set to `ON`, `tidb_super_read_only` is affected by [`tidb_restricted_read_only`](#tidb_restricted_read_only-new-in-v520) in some cases. For detailed impact, see the description of [`tidb_restricted_read_only`](#tidb_restricted_read_only-new-in-v520).
### tidb_sysdate_is_now New in v6.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to control whether the `SYSDATE` function can be replaced by the `NOW` function. This configuration item has the same effect as the MySQL option [`sysdate-is-now`](https://dev.mysql.com/doc/refman/8.0/en/server-options.html#option_mysqld_sysdate-is-now).
### tidb_sysproc_scan_concurrency New in v6.5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1`
- Range: `[1, 4294967295]`. The maximum value for v7.5.0 and earlier versions is `256`.
- This variable is used to set the concurrency of scan operations performed when TiDB executes internal SQL statements (such as an automatic update of statistics).
### tidb_table_cache_lease New in v6.0.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `3`
- Range: `[1, 10]`
- Unit: Seconds
- This variable is used to control the lease time of [cached tables](https://docs.pingcap.com/tidb/stable/cached-tables) with a default value of `3`. The value of this variable affects the modification to cached tables. After a modification is made to cached tables, the longest waiting time might be `tidb_table_cache_lease` seconds. If the table is read-only or can accept a high write latency, you can increase the value of this variable to increase the valid time for caching tables and to reduce the frequency of lease renewal.
### tidb_tmp_table_max_size New in v5.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `67108864`
- Range: `[1048576, 137438953472]`
- Unit: Bytes
- This variable is used to set the maximum size of a single [temporary table](https://docs.pingcap.com/tidb/stable/temporary-tables). Any temporary table with a size larger than this variable value causes error.
### tidb_top_sql_max_meta_count New in v6.0.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `5000`
- Range: `[1, 10000]`

- This variable is used to control the maximum number of SQL statement types collected by [Top SQL](https://docs.pingcap.com/tidb/stable/dashboard/top-sql) per minute.

- This variable is used to control the maximum number of SQL statement types collected by [Top SQL](https://docs.pingcap.com/tidb/stable/top-sql) per minute.
### tidb_top_sql_max_time_series_count New in v6.0.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

> **Note:**
>
> Currently, the Top SQL page in TiDB Dashboard only displays the top 5 types of SQL queries that contribute the most to the load, which is irrelevant with the configuration of `tidb_top_sql_max_time_series_count`.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `100`
- Range: `[1, 5000]`

- This variable is used to control how many SQL statements that contribute the most to the load (that is, top N) can be recorded by [Top SQL](https://docs.pingcap.com/tidb/stable/dashboard/top-sql) per minute.

- This variable is used to control how many SQL statements that contribute the most to the load (that is, top N) can be recorded by [Top SQL](https://docs.pingcap.com/tidb/stable/top-sql) per minute.
### tidb_track_aggregate_memory_usage

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether TiDB tracks the memory usage of aggregate functions.

> **Warning:**
>
> If you disable this variable, TiDB might not accurately track the memory usage and cannot control the memory usage of the corresponding SQL statements.
### tidb_tso_client_batch_max_wait_time New in v5.3.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Float
- Default value: `0`
- Range: `[0, 10]`
- Unit: Milliseconds
- This variable is used to set the maximum waiting time for a batch operation when TiDB requests TSO from PD. The default value is `0`, which means no extra waiting time.
- When obtaining TSO requests from PD each time, PD Client, used by TiDB, collects as many TSO requests received at the same time as possible. Then, PD Client merges the collected requests in batch into one RPC request and sends the request to PD. This helps reduce the pressure on PD.
- After setting this variable to a value greater than `0`, TiDB waits for the maximum duration of this value before the end of each batch merge. This is to collect more TSO requests and improve the effect of batch operations.
- Scenarios for increasing the value of this variable:
    * Due to the high pressure of TSO requests, the CPU of the PD leader reaches a bottleneck, which causes high latency of TSO RPC requests.
    * There are not many TiDB instances in the cluster, but every TiDB instance is in high concurrency.
- It is recommended to set this variable to a value as small as possible.

> **Note:**
>
> Suppose that the TSO RPC latency increases for reasons other than a CPU usage bottleneck of the PD leader (such as network issues). In this case, increasing the value of `tidb_tso_client_batch_max_wait_time` might increase the execution latency in TiDB and affect the QPS performance of the cluster.
### tidb_ttl_delete_rate_limit New in v6.5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `0`
- Range: `[0, 9223372036854775807]`
- This variable is used to limit the rate of `DELETE` statements in TTL jobs on each TiDB node. The value represents the maximum number of `DELETE` statements allowed per second in a single node in a TTL job. When this variable is set to `0`, no limit is applied. For more information, refer to [Time to Live](https://docs.pingcap.com/tidb/stable/time-to-live).
### tidb_ttl_delete_batch_size New in v6.5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `100`
- Range: `[1, 10240]`
- This variable is used to set the maximum number of rows that can be deleted in a single `DELETE` transaction in a TTL job. For more information, refer to [Time to Live](https://docs.pingcap.com/tidb/stable/time-to-live).
