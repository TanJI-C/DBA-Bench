# Log and log file configuration options

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > log > `record-plan-in-slow-log` | TiDB Configuration File > log > `expensive-threshold` | TiDB Configuration File > log > `general-log-file` <span class="version-mark">New in v8.0.0</span> | TiDB Configuration File > log > `timeout` <span class="version-mark">New in v7.1.0</span> | TiDB Configuration File > log.file | TiDB Configuration File > log.file > `filename` | TiDB Configuration File > log.file > `max-size` | TiDB Configuration File > log.file > `max-days` | TiDB Configuration File > log.file > `max-backups` | TiDB Configuration File > log.file > `compression` <span class="version-mark">New in v8.0.0</span>`
- Source Line Ranges: `323-387`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `logging`, `slow-log`, `general-log`, `log-rotation`, `compression`, `timeout`, `deprecated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0318_5deef873ec`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#record-plan-in-slow-log`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `864464dad8991ae1c41facb9c16eb38ccf21d8bd72fe67341012711f6170ef31`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#record-plan-in-slow-log
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB log configuration items for slow log plan recording, expensive query logging, general log output files, log write timeout, log rotation, retention, backups, or compression.
- Retrieval Keywords: record-plan-in-slow-log, instance.tidb_record_plan_in_slow_log, tidb_record_plan_in_slow_log, expensive-threshold, tidb_expensive_query_time_threshold, [EXPENSIVE_QUERY], general-log-file, tidb_general_log, timeout, log.file, filename, max-size, max-days, max-backups, compression, gzip, slow-query-file
- Follow-up Guidance: The content notes precedence and replacement details, such as `instance.tidb_record_plan_in_slow_log` taking effect when set together with `record-plan-in-slow-log`, and `expensive-threshold` being deprecated in favor of `tidb_expensive_query_time_threshold`.
- Classification Note: This is classified as TiDB configuration content because it defines logging-related configuration options, defaults, value meanings, and deprecation notes in the TiDB configuration file.

## Official Source Content

### `record-plan-in-slow-log`

- Determines whether to record execution plans in the slow log.
- Default value: `1`
- Since v6.1.0, whether to record execution plans in the slow log is determined by the TiDB configuration item [`instance.tidb_record_plan_in_slow_log`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_record_plan_in_slow_log) or the system variable [`tidb_record_plan_in_slow_log`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_record_plan_in_slow_log). `record-plan-in-slow-log` still takes effect. But if `record-plan-in-slow-log` and `instance.tidb_record_plan_in_slow_log` are set at the same time, the latter takes effect.
### `expensive-threshold`

> **Warning:**
>
> Starting from v5.4.0, the `expensive-threshold` configuration item is deprecated and replaced by the system variable [`tidb_expensive_query_time_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_expensive_query_time_threshold).

- Outputs the threshold value of the number of rows for the `expensive` operation.
- Default value: `10000`
- When the number of query rows (including the intermediate results based on statistics) is larger than this value, it is an `expensive` operation and outputs log with the `[EXPENSIVE_QUERY]` prefix.
### `general-log-file` New in v8.0.0

+ The filename of the [general log](https://docs.pingcap.com/tidb/stable/system-variables#tidb_general_log).
+ Default value: `""`
+ If you specify a filename, the general log is written to this specified file. If the value is blank, the general log is written to the server log of the TiDB instance. You can specify the name of the server log using [`filename`](#filename).
### `timeout` New in v7.1.0

- Sets the timeout for log-writing operations in TiDB. In case of a disk failure that prevents logs from being written, this configuration item can trigger the TiDB process to panic instead of hang.
- Default value: `0`, indicating no timeout is set.
- Unit: second
- In some user scenarios, TiDB logs might be stored on hot-pluggable or network-attached disks, which might become permanently unavailable. In these cases, TiDB cannot recover automatically from such disaster and the log-writing operations will be permanently blocked. Although the TiDB process might seem to be running, it does not respond to any requests. This configuration item is designed to handle such situations.
## log.file

Configuration items related to log files.
#### `filename`

- The file name of the general log file.
- Default value: ""
- If you set it, the log is output to this file.
#### `max-size`

- The size limit of the log file.
- Default value: 300
- Unit: MB
- The maximum value is 4096.
#### `max-days`

- The maximum number of days that the log is retained.
- Default value: `0`
- The log is retained by default. If you set the value, the expired log is cleaned up after `max-days`.
#### `max-backups`

- The maximum number of retained logs.
- Default value: `0`
- All the log files are retained by default. If you set it to `7`, seven log files are retained at maximum.
#### `compression` New in v8.0.0

+ The compression method for the log.
+ Default value: `""`
+ Value options: `""`, `"gzip"`
+ The default value is `""`, which means no compression. To enable the gzip compression, set this value to `"gzip"`. After compression is enabled, all log files are affected, such as [`slow-query-file`](#slow-query-file) and [`general-log-file`](#general-log-file-new-in-v800).
