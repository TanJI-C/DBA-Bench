# TiDB log and slow query log configuration

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > log | TiDB Configuration File > log > `level` | TiDB Configuration File > log > `format` | TiDB Configuration File > log > `enable-timestamp` | TiDB Configuration File > log > `enable-slow-log` | TiDB Configuration File > log > `slow-query-file` | TiDB Configuration File > log > `slow-threshold``
- Source Line Ranges: `273-322`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `logging`, `log-level`, `log-format`, `timestamps`, `slow-log`, `slow-query`, `thresholds`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0108_650daac6a6`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#log`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dc2b7b0971ee61f7dad4e0e43579515b42f0c581763cfe19c1dcc3f92e6d9d9a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#log
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB log configuration or slow query log settings such as log level, log format, timestamps, slow log enablement, slow log file, or slow query threshold.
- Retrieval Keywords: log.level, level, log.format, format, enable-timestamp, disable-timestamp, enable-slow-log, slow-query-file, slow-threshold, tidb-slow.log, slow query log, slow log threshold, instance.tidb_enable_slow_log, tidb_enable_slow_log, instance.tidb_slow_log_threshold, tidb_slow_log_threshold, debug, info, warn, error, fatal, json, text
- Follow-up Guidance: The content notes that since v6.1.0, `instance.tidb_enable_slow_log` and `instance.tidb_slow_log_threshold`, or the corresponding system variables, take effect when set together with `enable-slow-log` or `slow-threshold`.
- Classification Note: This chunk is classified as observability because it covers TiDB logging output and slow query log behavior, including levels, formats, timestamp output, and slow query thresholds.

## Official Source Content

## log

Configuration items related to log.
### `level`

+ Specifies the log output level.
+ Value options: `debug`, `info`, `warn`, `error`, and `fatal`.
+ Default value: `info`
### `format`

- Specifies the log output format.
- Value options: `json` and `text`.
- Default value: `text`
### `enable-timestamp`

- Determines whether to enable timestamp output in the log.
- Default value: `null`
- If you set the value to `false`, the log does not output timestamp.

> **Note:**
>
> - To be backward compatible, the initial `disable-timestamp` configuration item remains valid. But if the value of `disable-timestamp` semantically conflicts with the value of `enable-timestamp` (for example, if both `enable-timestamp` and `disable-timestamp` are set to `true`), TiDB ignores the value for `disable-timestamp`.
> - Currently, TiDB use `disable-timestamp` to determine whether to output timestamps in the log. In this situation, the value of `enable-timestamp` is `null`.
> - In later versions, the `disable-timestamp` configuration will be removed. Discard `disable-timestamp` and use `enable-timestamp` which is semantically easier to understand.
### `enable-slow-log`

- Determines whether to enable the slow query log.
- Default value: `true`
- To enable the slow query log, set `enable-slow-log` to `true`. Otherwise, set it to `false`.
- Since v6.1.0, whether to enable slow query log is determined by the TiDB configuration item [`instance.tidb_enable_slow_log`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_enable_slow_log) or the system variable [`tidb_enable_slow_log`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_slow_log). `enable-slow-log` still takes effect. But if `enable-slow-log` and `instance.tidb_enable_slow_log` are set at the same time, the latter takes effect.
### `slow-query-file`

- The file name of the slow query log.
- Default value: `tidb-slow.log`
- The format of the slow log is updated in TiDB v2.1.8, so the slow log is output to the slow log file separately. In versions before v2.1.8, this variable is set to "" by default.
- After you set it, the slow query log is output to this file separately.
### `slow-threshold`

- Outputs the threshold value of consumed time in the slow log.
- Default value: `300`
- Unit: Milliseconds
- When the time consumed by a query is larger than this value, this query is considered as a slow query and its log is output to the slow query log. Note that when the output level of [`log.level`](#level) is `"debug"`, all queries are recorded in the slow query log, regardless of the setting of this parameter.
- Since v6.1.0, the threshold value of consumed time in the slow log is specified by the TiDB configuration item [`instance.tidb_slow_log_threshold`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_slow_log_threshold) or the system variable [`tidb_slow_log_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_slow_log_threshold). `slow-threshold` still takes effect. But if `slow-threshold` and `instance.tidb_slow_log_threshold` are set at the same time, the latter takes effect.
