# GC, logging, plan cache, GOGC, consistency, and hash execution variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_gc_scan_lock_mode <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_general_log | System Variables > Variable reference > tidb_non_prepared_plan_cache_size | System Variables > Variable reference > tidb_generate_binary_plan <span class="version-mark">New in v6.2.0</span> | System Variables > Variable reference > tidb_gogc_tuner_max_value <span class="version-mark">New in v7.5.0</span> | System Variables > Variable reference > tidb_gogc_tuner_min_value <span class="version-mark">New in v7.5.0</span> | System Variables > Variable reference > tidb_gogc_tuner_threshold <span class="version-mark">New in v6.4.0</span> | System Variables > Variable reference > tidb_guarantee_linearizability <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_hash_exchange_with_new_collation | System Variables > Variable reference > tidb_hash_join_concurrency | System Variables > Variable reference > tidb_hashagg_final_concurrency`
- Source Line Ranges: `3013-3207`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `dashboard`, `sql`, `tiflash`
- Topic Tags: `system-variables`, `gc`, `green-gc`, `logging`, `general-log`, `plan-cache`, `binary-plan`, `gogc`, `memory-tuning`, `linearizability`, `async-commit`, `mpp`, `hash-join`, `hash-aggregation`, `deprecated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0724_1af143ad54`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-gc-scan-lock-mode-span-class-version-mark-new-in-v5-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `38e095d5559ef146caf0011e8257a2c2c2d48e3d9463765c296bf8f4b0b3e65c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-gc-scan-lock-mode-span-class-version-mark-new-in-v5-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB system variable reference details for GC lock scan mode, general SQL logging, non-prepared plan cache size, binary plan generation, GOGC tuner limits and threshold, async commit linearizability, MPP hash exchange with new collation, or deprecated hash execution concurrency settings.
- Retrieval Keywords: tidb_gc_scan_lock_mode, GREEN GC, PHYSICAL, LEGACY, Resolve Locks step of GC, Hibernate Region, tidb_general_log, GENERAL_LOG, command dispatched failed, log.general-log-file, log.format, tidb_redact_log, log.level, tidb_non_prepared_plan_cache_size, Non-prepared plan cache, tidb_session_plan_cache_size, tidb_generate_binary_plan, slow logs, statement summaries, TiDB Dashboard, SELECT tidb_decode_binary_plan('xxx...'), tidb_gogc_tuner_max_value, tidb_gogc_tuner_min_value, tidb_gogc_tuner_threshold, GOGC Tuner, tidb_guarantee_linearizability, async commit, PD server, linearizability, causal consistency, tidb_hash_exchange_with_new_collation, MPP hash partition exchange operator, new collation, tidb_hash_join_concurrency, hash join, tidb_executor_concurrency, tidb_hashagg_final_concurrency, hash aggregation final phase
- Follow-up Guidance: The content also points to related identifiers and follow-up references including tidb_session_plan_cache_size, tidb_decode_binary_plan, tidb_executor_concurrency, Hibernate Region, and log configuration items such as log.general-log-file, log.format, and log.level.
- Classification Note: This chunk is classified as a TiDB reference entry because it enumerates variable scopes, defaults, ranges, deprecation notes, and behavior for multiple system variables.

## Official Source Content

### tidb_gc_scan_lock_mode New in v5.0

> **Warning:**
>
> Currently, Green GC is an experimental feature. It is not recommended that you use it in production environments.

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `LEGACY`
- Possible values: `PHYSICAL`, `LEGACY`
    - `LEGACY`: Uses the old way of scanning, that is, disable Green GC.
    - `PHYSICAL`: Uses the physical scanning method, that is, enable Green GC.

- This variable specifies the way of scanning locks in the Resolve Locks step of GC. When the variable value is set to `LEGACY`, TiDB scans locks by Regions. When the value `PHYSICAL` is used, it enables each TiKV node to bypass the Raft layer and directly scan data, which can effectively mitigate the impact of GC wakening up all Regions when the [Hibernate Region](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#hibernate-regions) feature is enabled, thus improving the execution speed in the Resolve Locks step.

- This variable specifies the way of scanning locks in the Resolve Locks step of GC. When the variable value is set to `LEGACY`, TiDB scans locks by Regions. When the value `PHYSICAL` is used, it enables each TiKV node to bypass the Raft layer and directly scan data, which can effectively mitigate the impact of GC wakening up all Regions, thus improving the execution speed in the Resolve Locks step.
### tidb_general_log

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`

- This variable is used to set whether to record all SQL statements in the log. This feature is disabled by default. If you need to trace all SQL statements when locating issues, enable this feature.

- This variable is used to set whether to record all SQL statements in the [log](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#logfile). This feature is disabled by default. If maintenance personnel needs to trace all SQL statements when locating issues, they can enable this feature.

- If the [`log.general-log-file`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#general-log-file-new-in-v800) configuration item is specified, the general log is written to the specified file separately. 

- The [`log.format`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#format) configuration item enables you to configure the log message format, whether the general log is in a separate file or combined with other logs.

- The [`tidb_redact_log`](#tidb_redact_log) variable enables you to redact SQL statements recorded in the general log.

- Only successfully executed statements are logged in the general log. Failed statements are not recorded in the general log but are instead logged in the TiDB log with a `command dispatched failed` message.

- To see all records of this feature in the log, you need to set the TiDB configuration item [`log.level`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#level) to `"info"` or `"debug"` and then query the `"GENERAL_LOG"` string. The following information is recorded:
    - `time`: The time of the event.
    - `conn`: The ID of the current session.
    - `user`: The current session user.
    - `schemaVersion`: The current schema version.
    - `txnStartTS`: The timestamp at which the current transaction starts.
    - `forUpdateTS`: In the pessimistic transactional mode, `forUpdateTS` is the current timestamp of the SQL statement. When a write conflict occurs in the pessimistic transaction, TiDB retries the SQL statement currently being executed and updates this timestamp. You can configure the number of retries via [`max-retry-count`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#max-retry-count). In the optimistic transactional model, `forUpdateTS` is equivalent to `txnStartTS`.
    - `isReadConsistency`: Indicates whether the current transactional isolation level is Read Committed (RC).
    - `current_db`: The name of the current database.
    - `txn_mode`: The transactional mode. Value options are `OPTIMISTIC` and `PESSIMISTIC`.
    - `sql`: The SQL statement corresponding to the current query.
### tidb_non_prepared_plan_cache_size

> **Warning:**
>
> Starting from v7.1.0, this variable is deprecated. Instead, use [`tidb_session_plan_cache_size`](#tidb_session_plan_cache_size-new-in-v710) for setting.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `100`
- Range: `[1, 100000]`
- This variable controls the maximum number of execution plans that can be cached by [Non-prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache).
### tidb_generate_binary_plan New in v6.2.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether to generate binary-encoded execution plans in slow logs and statement summaries.
- When this variable is set to `ON`, you can view visual execution plans in TiDB Dashboard. Note that TiDB Dashboard only provides visual display for execution plans generated after this variable is enabled.
- You can execute the [`SELECT tidb_decode_binary_plan('xxx...')`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb_decode_binary_plan) statement to parse the specific plan from a binary plan.
### tidb_gogc_tuner_max_value New in v7.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `500`
- Range: `[10, 2147483647]`
- The variable is used to control the maximum value of GOGC that the GOGC Tuner can adjust.
### tidb_gogc_tuner_min_value New in v7.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `100`
- Range: `[10, 2147483647]`
- The variable is used to control the minimum value of GOGC that the GOGC Tuner can adjust.
### tidb_gogc_tuner_threshold New in v6.4.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `0.6`
- Range: `[0, 0.9)`
- This variable specifies the maximum memory threshold for tuning GOGC. When the memory exceeds this threshold, GOGC Tuner stops working.
### tidb_guarantee_linearizability New in v5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls the way commit TS is calculated for async commit. By default (with the `ON` value), the two-phase commit requests a new TS from the PD server and uses the TS to calculate the final commit TS. In this situation, linearizability is guaranteed for all the concurrent transactions.
- If you set this variable to `OFF`, the process of fetching TS from the PD server is skipped, with the cost that only causal consistency is guaranteed but not linearizability. For more details, see the blog post [Async Commit, the Accelerator for Transaction Commit in TiDB 5.0](https://www.pingcap.com/blog/async-commit-the-accelerator-for-transaction-commit-in-tidb-5-0/).
- For scenarios that require only causal consistency, you can set this variable to `OFF` to improve performance.
### tidb_hash_exchange_with_new_collation

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether the MPP hash partition exchange operator is generated in a cluster with new collation enabled. `true` means to generate the operator, and `false` means not to generate it.
- This variable is used for the internal operation of TiDB. It is **NOT recommended** to set this variable.
### tidb_hash_join_concurrency

> **Warning:**
>
> Since v5.0, this variable is deprecated. Instead, use [`tidb_executor_concurrency`](#tidb_executor_concurrency-new-in-v50) for setting.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `-1`
- Range: `[1, 256]`
- Unit: Threads
- This variable is used to set the concurrency of the `hash join` algorithm.
- A value of `-1` means that the value of `tidb_executor_concurrency` will be used instead.
### tidb_hashagg_final_concurrency

> **Warning:**
>
> Since v5.0, this variable is deprecated. Instead, use [`tidb_executor_concurrency`](#tidb_executor_concurrency-new-in-v50) for setting.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `-1`
- Range: `[1, 256]`
- Unit: Threads
- This variable is used to set the concurrency of executing the concurrent `hash aggregation` algorithm in the `final` phase.
- When the parameter of the aggregate function is not distinct, `HashAgg` is run concurrently and respectively in two phases - the `partial` phase and the `final` phase.
- A value of `-1` means that the value of `tidb_executor_concurrency` will be used instead.
