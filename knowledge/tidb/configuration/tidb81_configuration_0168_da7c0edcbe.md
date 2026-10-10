# TiDB memory quota and memory alarm system variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_mem_quota_query | System Variables > Variable reference > tidb_memory_debug_mode_alarm_ratio | System Variables > Variable reference > tidb_memory_debug_mode_min_heap_inuse | System Variables > Variable reference > tidb_memory_usage_alarm_ratio | System Variables > Variable reference > tidb_memory_usage_alarm_keep_record_num <span class="version-mark">New in v6.4.0</span>`
- Source Line Ranges: `3725-3819`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `memory`, `quota`, `oom`, `session`, `global`, `alarm`, `debug`, `cluster-persistence`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0168_da7c0edcbe`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-mem-quota-query`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0662ea2c4db34a818df80b61ae7b28f8c1e86bd6040790cc19bd49e052bee3e7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-mem-quota-query
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB system variables for session or query memory quota behavior, memory debug mode, or the tidb-server memory alarm threshold and retained alarm records.
- Retrieval Keywords: tidb_mem_quota_query, tidb_mem_oom_action, tidb_memory_debug_mode_alarm_ratio, tidb_memory_debug_mode_min_heap_inuse, tidb_memory_usage_alarm_ratio, tidb_memory_usage_alarm_keep_record_num, tidb_server_memory_limit, memory quota for a session, memory quota for a query, tidb-server memory alarm, positive infinity, recent 5 alarms
- Follow-up Guidance: The content also points to tidb_mem_oom_action for behavior after exceeding the quota, txn-total-size-limit for transaction memory usage in v6.5.0 and later, and configure-memory-usage for alarm conditions.
- Classification Note: This is classified as configuration because the content defines TiDB system variables, including scope, defaults, ranges, persistence, and alarm or debug settings related to memory management.

## Official Source Content

### tidb_mem_quota_query

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1073741824` (1 GiB)
- Range: `[-1, 9223372036854775807]`
- Unit: Bytes

- For versions earlier than TiDB v6.1.0, this is a session scope variable and uses the value of `mem-quota-query` from `tidb.toml` as an initial value. Starting from v6.1.0, `tidb_mem_quota_query` is a `SESSION | GLOBAL` scope variable.
- For versions earlier than TiDB v6.5.0, this variable is used to set the threshold value of memory quota for **a query**. If the memory quota of a query during execution exceeds the threshold value, TiDB performs the operation defined by [`tidb_mem_oom_action`](#tidb_mem_oom_action-new-in-v610).
- For TiDB v6.5.0 and later versions, this variable is used to set the threshold value of memory quota for **a session**. If the memory quota of a session during execution exceeds the threshold value, TiDB performs the operation defined by [`tidb_mem_oom_action`](#tidb_mem_oom_action-new-in-v610). Note that starting from TiDB v6.5.0, the memory usage of a session contains the memory consumed by the transactions in the session. For the control behavior of transaction memory usage in TiDB v6.5.0 and later versions, see [`txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit).
- When you set the variable value to `0` or `-1`, the memory threshold is positive infinity. When you set a value smaller than 128, the value will be defaulted to `128`.

- For versions earlier than TiDB v6.1.0, this is a session scope variable. Starting from v6.1.0, `tidb_mem_quota_query` is a `SESSION | GLOBAL` scope variable.
- For versions earlier than TiDB v6.5.0, this variable is used to set the threshold value of memory quota for **a query**. If the memory quota of a query during execution exceeds the threshold value, TiDB performs the operation defined by [`tidb_mem_oom_action`](#tidb_mem_oom_action-new-in-v610).
- For TiDB v6.5.0 and later versions, this variable is used to set the threshold value of memory quota for **a session**. If the memory quota of a session during execution exceeds the threshold value, TiDB performs the operation defined by [`tidb_mem_oom_action`](#tidb_mem_oom_action-new-in-v610). Note that starting from TiDB v6.5.0, the memory usage of a session contains the memory consumed by the transactions in the session.
- When you set the variable value to `0` or `-1`, the memory threshold is positive infinity. When you set a value smaller than 128, the value will be defaulted to `128`.
### tidb_memory_debug_mode_alarm_ratio

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Float
- Default value: `0`
- This variable represents the memory statistics error value allowed in the TiDB memory debug mode.
- This variable is used for the internal testing of TiDB. It is **NOT recommended** to set this variable.
### tidb_memory_debug_mode_min_heap_inuse

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- This variable is used for the internal testing of TiDB. It is **NOT recommended** to set this variable. Enabling this variable will affect the performance of TiDB.
- After configuring this parameter, TiDB will enter the memory debug mode to analyze the accuracy of memory tracking. TiDB will frequently trigger GC during the execution of subsequent SQL statements, and compare the actual memory usage and memory statistics. If the current memory usage is greater than `tidb_memory_debug_mode_min_heap_inuse` and the memory statistics error exceeds `tidb_memory_debug_mode_alarm_ratio`, TiDB will output the relevant memory information to the log and file.
### tidb_memory_usage_alarm_ratio

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Float
- Default value: `0.7`
- Range: `[0.0, 1.0]`

- This variable sets the memory usage ratio that triggers the tidb-server memory alarm. By default, TiDB prints an alarm log when TiDB memory usage exceeds 70% of its total memory and any of the [alarm conditions](https://docs.pingcap.com/tidb/stable/configure-memory-usage#trigger-the-alarm-of-excessive-memory-usage) is met.
- When this variable is configured to `0` or `1`, it means the memory threshold alarm feature is disabled.
- When this variable is configured to a value greater than `0` and less than `1`, it means that the memory threshold alarm feature is enabled.

    - If the value of the system variable [`tidb_server_memory_limit`](#tidb_server_memory_limit-new-in-v640) is `0`, the memory alarm threshold is `tidb_memory-usage-alarm-ratio * system memory size`.
    - If the value of the system variable `tidb_server_memory_limit` is set to greater than 0, the memory alarm threshold is `tidb_memory-usage-alarm-ratio * tidb_server_memory_limit`.

- This variable sets the memory usage ratio that triggers the [tidb-server memory alarm](https://docs.pingcap.com/tidb/stable/configure-memory-usage#trigger-the-alarm-of-excessive-memory-usage).
- When this variable is configured to `0` or `1`, it means the memory threshold alarm feature is disabled.
- When this variable is configured to a value greater than `0` and less than `1`, it means that the memory threshold alarm feature is enabled.
### tidb_memory_usage_alarm_keep_record_num New in v6.4.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `5`
- Range: `[1, 10000]`
- When the tidb-server memory usage exceeds the memory alarm threshold and triggers an alarm, TiDB only retains the status files generated during the recent 5 alarms by default. You can adjust this number with this variable.
