# Instance logging, connection, DDL, and statement summary settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > instance | TiDB Configuration File > instance > `tidb_enable_collect_execution_info` | TiDB Configuration File > instance > `tidb_enable_slow_log` | TiDB Configuration File > instance > `tidb_slow_log_threshold` | TiDB Configuration File > instance > `in-mem-slow-query-topn-num` <span class="version-mark">New in v7.3.0</span> | TiDB Configuration File > instance > `in-mem-slow-query-recent-num` <span class="version-mark">New in v7.3.0</span> | TiDB Configuration File > instance > `tidb_expensive_query_time_threshold` | TiDB Configuration File > instance > `tidb_record_plan_in_slow_log` | TiDB Configuration File > instance > `tidb_force_priority` | TiDB Configuration File > instance > `max_connections` | TiDB Configuration File > instance > `tidb_enable_ddl` | TiDB Configuration File > instance > `tidb_stmt_summary_enable_persistent` <span class="version-mark">New in v6.6.0</span> | TiDB Configuration File > instance > `tidb_stmt_summary_filename` <span class="version-mark">New in v6.6.0</span> | TiDB Configuration File > instance > `tidb_stmt_summary_file_max_days` <span class="version-mark">New in v6.6.0</span> | TiDB Configuration File > instance > `tidb_stmt_summary_file_max_size` <span class="version-mark">New in v6.6.0</span> | TiDB Configuration File > instance > `tidb_stmt_summary_file_max_backups` <span class="version-mark">New in v6.6.0</span>`
- Source Line Ranges: `908-1038`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `instance-settings`, `slow-log`, `expensive-query-log`, `execution-info`, `statement-priority`, `connection-limits`, `ddl-owner`, `statement-summary`, `persistence`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0326_c94e7e8263`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#instance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `625f44c59016201829a864621e80b646c048f85bbc641087899bf62ce1635cdf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#instance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when you need instance-level TiDB configuration settings for slow logs, expensive query logs, execution info, statement priority, connection limits, DDL ownership, or statement summary persistence.
- Retrieval Keywords: instance, tidb_enable_collect_execution_info, slow query log, usage statistics of indexes, tidb_enable_slow_log, tidb_slow_log_threshold, log.level, debug, in-mem-slow-query-topn-num, in-mem-slow-query-recent-num, tidb_expensive_query_time_threshold, expensive query logs, tidb_record_plan_in_slow_log, tidb_force_priority, NO_PRIORITY, LOW_PRIORITY, DELAYED, HIGH_PRIORITY, Resource Control, max_connections, tidb_enable_ddl, DDL owner, tidb_stmt_summary_enable_persistent, tidb_stmt_summary_filename, tidb_stmt_summary_file_max_days, tidb_stmt_summary_file_max_size, tidb_stmt_summary_file_max_backups, Persist statements summary
- Follow-up Guidance: The content notes that when resource control is enabled, statement priority no longer takes effect, and it also marks statements summary persistence as an experimental feature.
- Classification Note: This is classified as configuration because it lists TiDB instance configuration items, defaults, ranges, and initialization behavior for related system variables.

## Official Source Content

## instance
### `tidb_enable_collect_execution_info`

- This configuration controls whether to record the execution information of each operator in the slow query log and whether to record the [usage statistics of indexes](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-index-usage).
- Default value: `true`
- Before v6.1.0, this configuration is set by `enable-collect-execution-info`.
### `tidb_enable_slow_log`

- This configuration is used to control whether to enable the slow log feature.
- Default value: `true`
- Value options: `true` or `false`
- Before v6.1.0, this configuration is set by `enable-slow-log`.
### `tidb_slow_log_threshold`

- Outputs the threshold value of the time consumed by the slow log.
- Default value: `300`
- Range: `[-1, 9223372036854775807]`
- Unit: Milliseconds
- When the time consumed by a query is larger than this value, this query is considered as a slow query and its log is output to the slow query log. Note that when the output level of [`log.level`](#level) is `"debug"`, all queries are recorded in the slow query log, regardless of the setting of this parameter.
- Before v6.1.0, this configuration is set by `slow-threshold`.
### `in-mem-slow-query-topn-num` New in v7.3.0

+ The configuration controls the number of slowest queries that are cached in memory.
+ Default value: 30
### `in-mem-slow-query-recent-num` New in v7.3.0

+ The configuration controls the number of recently used slow queries that are cached in memory.
+ Default value: 500
### `tidb_expensive_query_time_threshold`

- This configuration is used to set the threshold value that determines whether to print expensive query logs. The difference between expensive query logs and slow query logs is:
    - Slow logs are printed after the statement is executed.
    - Expensive query logs print the statements that are being executed, with execution time exceeding the threshold value, and their related information.
- Default value: `60`
- Range: `[10, 2147483647]`
- Unit: Seconds
- Before v5.4.0, this configuration is set by `expensive-threshold`.
### `tidb_record_plan_in_slow_log`

- This configuration is used to control whether to include the execution plan of slow queries in the slow log.
- Default value: `1`
- Value options: `1` (enabled, default) or `0` (disabled).
- The value of this configuration will initialize the value of system variable [`tidb_record_plan_in_slow_log`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_record_plan_in_slow_log)
- Before v6.1.0, this configuration is set by `record-plan-in-slow-log`.
### `tidb_force_priority`

- This configuration is used to change the default priority for statements executed on a TiDB server.
- Default value: `NO_PRIORITY`
- The default value `NO_PRIORITY` means that the priority for statements is not forced to change. Other options are `LOW_PRIORITY`, `DELAYED`, and `HIGH_PRIORITY` in ascending order.
- Before v6.1.0, this configuration is set by `force-priority`.

> **Note:**
>
> Starting from v6.6.0, TiDB supports [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control). You can use this feature to execute SQL statements with different priorities in different resource groups. By configuring proper quotas and priorities for these resource groups, you can gain better scheduling control for SQL statements with different priorities. When resource control is enabled, statement priority will no longer take effect. It is recommended that you use [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) to manage resource usage for different SQL statements.
### `max_connections`

- The maximum number of connections permitted for a single TiDB instance. It can be used for resources control.
- Default value: `0`
- Range: `[0, 100000]`
- The default value `0` means no limit. When the value of this variable is larger than `0`, and the number of connections reaches the value, the TiDB server will reject new connections from clients.
- The value of this configuration will initialize the value of system variable [`max_connections`](https://docs.pingcap.com/tidb/stable/system-variables#max_connections)
- Before v6.2.0, this configuration is set by `max-server-connections`.
### `tidb_enable_ddl`

- This configuration controls whether the corresponding TiDB instance can become a DDL owner or not.
- Default value: `true`
- Possible values: `OFF`, `ON`
- The value of this configuration will initialize the value of the system variable [`tidb_enable_ddl`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_ddl-new-in-v630)
- Before v6.3.0, this configuration is set by `run-ddl`.
### `tidb_stmt_summary_enable_persistent` New in v6.6.0

> **Warning:**
>
> Statements summary persistence is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

+ Controls whether to enable statements summary persistence.
+ Default value: `false`
+ For more details, see [Persist statements summary](https://docs.pingcap.com/tidb/stable/statement-summary-tables#persist-statements-summary).
### `tidb_stmt_summary_filename` New in v6.6.0

> **Warning:**
>
> Statements summary persistence is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

+ When statements summary persistence is enabled, this configuration specifies the file to which persistent data is written.
+ Default value: `tidb-statements.log`
### `tidb_stmt_summary_file_max_days` New in v6.6.0

> **Warning:**
>
> Statements summary persistence is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

+ When statements summary persistence is enabled, this configuration specifies the maximum number of days to keep persistent data files.
+ Default value: `3`
+ Unit: day
+ You can adjust the value based on the data retention requirements and disk space usage.
### `tidb_stmt_summary_file_max_size` New in v6.6.0

> **Warning:**
>
> Statements summary persistence is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

+ When statements summary persistence is enabled, this configuration specifies the maximum size of a persistent data file.
+ Default value: `64`
+ Unit: MiB
+ You can adjust the value based on the data retention requirements and disk space usage.
### `tidb_stmt_summary_file_max_backups` New in v6.6.0

> **Warning:**
>
> Statements summary persistence is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

+ When statements summary persistence is enabled, this configuration specifies the maximum number of data files that can be persisted. `0` means no limit on the number of files.
+ Default value: `0`
+ You can adjust the value based on the data retention requirements and disk space usage.
