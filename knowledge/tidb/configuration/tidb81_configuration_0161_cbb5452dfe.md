# Auto analyze thresholds and backoff timing variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_auto_analyze_ratio | System Variables > Variable reference > tidb_auto_analyze_start_time | System Variables > Variable reference > tidb_auto_build_stats_concurrency <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > tidb_backoff_lock_fast | System Variables > Variable reference > tidb_backoff_weight`
- Source Line Ranges: `1229-1285`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`
- Topic Tags: `auto-analyze`, `statistics`, `analyze-concurrency`, `backoff`, `lock-wait`, `retry-timeout`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0161_cbb5452dfe`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-auto-analyze-ratio`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b32f439f3a21ac0f827a349266f18ff416bbab01abb54f1737a08dbce3226d6e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-auto-analyze-ratio
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB system variables that control auto analyze thresholds or time windows, manual versus auto statistics build concurrency, or backoff timing for lock waits and retry timeout behavior involving TiKV or PD.
- Retrieval Keywords: tidb_auto_analyze_ratio, tidb_auto_analyze_start_time, tidb_auto_build_stats_concurrency, tidb_backoff_lock_fast, tidb_backoff_weight, ANALYZE TABLE, auto analyze threshold, automatic update of statistics permitted time window, building statistics during auto ANALYZE, backoff time when the read request meets a lock, maximum retry time, taking TSO from PD
- Follow-up Guidance: The content also notes that auto analyze requires tidb_enable_auto_analyze to be ON and can be limited by tidb_auto_analyze_start_time and tidb_auto_analyze_end_time.
- Classification Note: This is classified as configuration because each section defines a TiDB system variable with scope, type, default value, range, and its effect on statistics or backoff behavior.

## Official Source Content

### tidb_auto_analyze_ratio

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Float
- Default value: `0.5`
- Range: `(0, 1]`. The range for v8.0.0 and earlier versions is `[0, 18446744073709551615]`.
- This variable is used to set the threshold when TiDB automatically executes [`ANALYZE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) in a background thread to update table statistics. For example, a value of 0.5 means that auto-analyze is triggered when greater than 50% of the rows in a table have been modified. Auto-analyze can be restricted to only execute during certain hours of the day by specifying `tidb_auto_analyze_start_time` and `tidb_auto_analyze_end_time`.

> **Note:**
>
> This feature requires the system variable `tidb_enable_auto_analyze` set to `ON`.
### tidb_auto_analyze_start_time

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Time
- Default value: `00:00 +0000`
- This variable is used to restrict the time window that the automatic update of statistics is permitted. For example, to only allow automatic statistics updates between 1 AM and 3 AM in UTC time, set `tidb_auto_analyze_start_time='01:00 +0000'` and `tidb_auto_analyze_end_time='03:00 +0000'`.
### tidb_auto_build_stats_concurrency New in v6.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1`
- Range: `[1, 256]`
- This variable controls the concurrency for building statistics during auto `ANALYZE`, such as the number of table or partition analysis tasks that can be processed simultaneously.
### tidb_backoff_lock_fast

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `10`
- Range: `[1, 2147483647]`
- This variable is used to set the `backoff` time when the read request meets a lock.
### tidb_backoff_weight

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `2`
- Range: `[0, 2147483647]`
- This variable is used to increase the weight of the maximum time of TiDB `backoff`, that is, the maximum retry time for sending a retry request when an internal network or other component (TiKV, PD) failure is encountered. This variable can be used to adjust the maximum retry time and the minimum value is 1.

    For example, the base timeout for TiDB to take TSO from PD is 15 seconds. When `tidb_backoff_weight = 2`, the maximum timeout for taking TSO is: *base time \* 2 = 30 seconds*.

    In the case of a poor network environment, appropriately increasing the value of this variable can effectively alleviate error reporting to the application end caused by timeout. If the application end wants to receive the error information more quickly, minimize the value of this variable.
