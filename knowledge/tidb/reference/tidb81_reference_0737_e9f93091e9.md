# TiDB system variables: plan cache, placement, concurrency, logging, and RC timestamp checks

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_pessimistic_txn_fair_locking <span class="version-mark">New in v7.0.0</span> | System Variables > Variable reference > tidb_placement_mode <span class="version-mark">New in v6.0.0</span> | System Variables > Variable reference > `tidb_plan_cache_invalidation_on_fresh_stats` <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > `tidb_plan_cache_max_plan_size` <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > tidb_pprof_sql_cpu <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_prefer_broadcast_join_by_exchange_data_size <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > tidb_prepared_plan_cache_memory_guard_ratio <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_prepared_plan_cache_size <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_projection_concurrency | System Variables > Variable reference > tidb_query_log_max_len | System Variables > Variable reference > tidb_rc_read_check_ts <span class="version-mark">New in v6.0.0</span>`
- Source Line Ranges: `4763-4908`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tiflash`
- Topic Tags: `system-variables`, `plan-cache`, `placement-rules`, `pessimistic-transactions`, `mpp-join`, `prepared-plan-cache`, `concurrency`, `query-logging`, `read-committed`, `timestamp-optimization`, `deprecated`, `version-dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0737_e9f93091e9`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-pessimistic-txn-fair-locking-span-class-version-mark-new-in-v7-0-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5a03b6c6241443e9eb5e0b19c0bbd5ac6ffb17b0b4700f5b878b27c96b92aade`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-pessimistic-txn-fair-locking-span-class-version-mark-new-in-v7-0-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables related to pessimistic transaction fair locking, placement rule handling, plan cache invalidation and size limits, prepared plan cache settings, MPP broadcast-versus-shuffle join choice, Projection concurrency, query log truncation, SQL CPU profiling marks, or read-committed timestamp check optimization.
- Retrieval Keywords: tidb_pessimistic_txn_fair_locking, pessimistic lock retry limit reached, single-point pessimistic locking conflicts, enhanced pessimistic locking wake-up model, tidb_placement_mode, STRICT, IGNORE, placement rules specified in SQL, logical dump restore tools, tidb_plan_cache_invalidation_on_fresh_stats, invalidate plan cache automatically when statistics are updated, tidb_plan_cache_max_plan_size, prepared or non-prepared plan cache, 2 MiB, tidb_pprof_sql_cpu, profile output, mark the corresponding SQL statement, tidb_prefer_broadcast_join_by_exchange_data_size, MPP Hash Join algorithm, Broadcast Hash Join, Shuffled Hash Join, tidb_broadcast_join_threshold_count, tidb_broadcast_join_threshold_size, tidb_prepared_plan_cache_memory_guard_ratio, prepared plan cache triggers a memory protection mechanism, tidb_prepared_plan_cache_size, tidb_session_plan_cache_size, tidb_projection_concurrency, tidb_executor_concurrency, Projection operator, tidb_query_log_max_len, statement is truncated to output, tidb_rc_read_check_ts, read-committed isolation level, optimize the timestamp acquisition, replica-read incompatible
- Follow-up Guidance: The content also notes deprecation or replacement for `tidb_prepared_plan_cache_size` and `tidb_projection_concurrency`, incompatibility between `tidb_rc_read_check_ts` and `replica-read`, and instance-only scope for `tidb_pprof_sql_cpu` and `tidb_rc_read_check_ts`.
- Classification Note: This is reference content because it enumerates TiDB system variables with their scope, defaults, ranges, persistence behavior, warnings, and exact effects.

## Official Source Content

### tidb_pessimistic_txn_fair_locking New in v7.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- Determines whether to use enhanced pessimistic locking wake-up model for pessimistic transactions. This model strictly controls the wake-up order of pessimistic transactions in the pessimistic locking single-point conflict scenarios to avoid unnecessary wake-ups. It greatly reduces the uncertainty brought by the randomness of the existing wake-up mechanism. If you encounter frequent single-point pessimistic locking conflicts in your business scenario (such as frequent updates to the same row of data), and thus cause frequent statement retries, high tail latency, or even occasional `pessimistic lock retry limit reached` errors, you can try to enable this variable to solve the problem.
- This variable is disabled by default for TiDB clusters that are upgraded from versions earlier than v7.0.0 to v7.0.0 or later versions.

> **Note:**
>
> - Depending on the specific business scenario, enabling this option might cause a certain degree of throughput reduction (average latency increase) for transactions with frequent lock conflicts.
> - This option only takes effect on statements that need to lock a single key. If a statement needs to lock multiple rows at the same time, this option will not take effect on such statements.
> - This feature is introduced in v6.6.0 by the [`tidb_pessimistic_txn_aggressive_locking`](https://docs.pingcap.com/tidb/v6.6/system-variables#tidb_pessimistic_txn_aggressive_locking-new-in-v660) variable, which is disabled by default.
### tidb_placement_mode New in v6.0.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `STRICT`
- Possible values: `STRICT`, `IGNORE`
- This variable controls whether DDL statements ignore the [placement rules specified in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql). When the variable value is `IGNORE`, all placement rule options are ignored.
- It is intended to be used by logical dump/restore tools to ensure that tables can always be created even if invalid placement rules are assigned. This is similar to how mysqldump writes `SET FOREIGN_KEY_CHECKS=0;` to the start of every dump file.
### `tidb_plan_cache_invalidation_on_fresh_stats` New in v7.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether to invalidate the plan cache automatically when statistics on related tables are updated.
- After enabling this variable, plan cache can make use of statistics more sufficiently to generate execution plans. For example:
    - If execution plans are generated before statistics are available, plan cache re-generates execution plans once the statistics are available.
    - If the data distribution of a table changes, causing the previously optimal execution plan to become non-optimal, plan cache re-generates execution plans after the statistics are re-collected.
- This variable is disabled by default for TiDB clusters that are upgraded from a version earlier than v7.1.0 to v7.1.0 or later.
### `tidb_plan_cache_max_plan_size` New in v7.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: `2097152` (which is 2 MiB)
- Range: `[0, 9223372036854775807]`, in bytes. The memory format with the units "KiB|MiB|GiB|TiB" is also supported. `0` means no limit.
- This variable controls the maximum size of a plan that can be cached in prepared or non-prepared plan cache. If the size of a plan exceeds this value, the plan will not be cached. For more details, see [Memory management of prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache#memory-management-of-prepared-plan-cache) and [Non-prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-plan-management#usage).
### tidb_pprof_sql_cpu New in v4.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 1]`
- This variable is used to control whether to mark the corresponding SQL statement in the profile output to identify and troubleshoot performance issues.
### tidb_prefer_broadcast_join_by_exchange_data_size New in v7.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: `OFF`
- This variable controls whether to use the algorithm with the minimum overhead of network transmission when TiDB selects the [MPP Hash Join algorithm](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode#algorithm-support-for-the-mpp-mode). If this variable is enabled, TiDB estimates the size of the data to be exchanged in the network using `Broadcast Hash Join` and `Shuffled Hash Join` respectively, and then chooses the one with the smaller size.
- [`tidb_broadcast_join_threshold_count`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_count-new-in-v50) and [`tidb_broadcast_join_threshold_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_size-new-in-v50) will not take effect after this variable is enabled.
### tidb_prepared_plan_cache_memory_guard_ratio New in v6.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Float
- Default value: `0.1`
- Range: `[0, 1]`
- The threshold at which the prepared plan cache triggers a memory protection mechanism. For details, see [Memory management of Prepared Plan Cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache).
- This setting was previously a `tidb.toml` option (`prepared-plan-cache.memory-guard-ratio`), but changed to a system variable starting from TiDB v6.1.0.
### tidb_prepared_plan_cache_size New in v6.1.0

> **Warning:**
>
> Starting from v7.1.0, this variable is deprecated. Instead, use [`tidb_session_plan_cache_size`](#tidb_session_plan_cache_size-new-in-v710) for setting.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `100`
- Range: `[1, 100000]`
- The maximum number of plans that can be cached in a session. For details, see [Memory management of Prepared Plan Cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache).
- This setting was previously a `tidb.toml` option (`prepared-plan-cache.capacity`), but changed to a system variable starting from TiDB v6.1.0.
### tidb_projection_concurrency

> **Warning:**
>
> Since v5.0, this variable is deprecated. Instead, use [`tidb_executor_concurrency`](#tidb_executor_concurrency-new-in-v50) for setting.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `-1`
- Range: `[-1, 256]`
- Unit: Threads
- This variable is used to set the concurrency of the `Projection` operator.
- A value of `-1` means that the value of `tidb_executor_concurrency` will be used instead.
### tidb_query_log_max_len

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `4096` (4 KiB)
- Range: `[0, 1073741824]`
- Unit: Bytes
- The maximum length of the SQL statement output. When the output length of a statement is larger than the `tidb_query_log_max_len` value, the statement is truncated to output.
- This setting was previously also available as a `tidb.toml` option (`log.query-log-max-len`), but is only a system variable starting from TiDB v6.1.0.
### tidb_rc_read_check_ts New in v6.0.0

> **Warning:**
>
> - This feature is incompatible with [`replica-read`](#tidb_replica_read-new-in-v40). Do not enable `tidb_rc_read_check_ts` and `replica-read` at the same time.
> - If your client uses a cursor, it is not recommended to enable `tidb_rc_read_check_ts` in case that the previous batch of returned data has already been used by the client and the statement eventually fails.
> - Starting from v7.0.0, this variable is no longer valid for the cursor fetch read mode that uses the prepared statement protocol.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to optimize the timestamp acquisition, which is suitable for scenarios with read-committed isolation level where read-write conflicts are rare. Enabling this variable can avoid the latency and cost of getting the global timestamp, and can optimize the transaction-level read latency.
- If read-write conflicts are severe, enabling this feature will increase the cost and latency of getting the global timestamp, and might cause performance regression. For details, see [Read Committed isolation level](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#read-committed-isolation-level).
