# TiKV global and log configuration options

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File | TiKV Configuration File > Global configuration | TiKV Configuration File > Global configuration > `abort-on-panic` | TiKV Configuration File > Global configuration > `slow-log-file` | TiKV Configuration File > Global configuration > `slow-log-threshold` | TiKV Configuration File > Global configuration > `memory-usage-limit` | TiKV Configuration File > log <span class="version-mark">New in v5.4.0</span> | TiKV Configuration File > log <span class="version-mark">New in v5.4.0</span> > `level` <span class="version-mark">New in v5.4.0</span> | TiKV Configuration File > log <span class="version-mark">New in v5.4.0</span> > `format` <span class="version-mark">New in v5.4.0</span> | TiKV Configuration File > log <span class="version-mark">New in v5.4.0</span> > `enable-timestamp` <span class="version-mark">New in v5.4.0</span> | TiKV Configuration File > log.file <span class="version-mark">New in v5.4.0</span> | TiKV Configuration File > log.file <span class="version-mark">New in v5.4.0</span> > `filename` <span class="version-mark">New in v5.4.0</span> | TiKV Configuration File > log.file <span class="version-mark">New in v5.4.0</span> > `max-size` <span class="version-mark">New in v5.4.0</span> | TiKV Configuration File > log.file <span class="version-mark">New in v5.4.0</span> > `max-days` <span class="version-mark">New in v5.4.0</span> | TiKV Configuration File > log.file <span class="version-mark">New in v5.4.0</span> > `max-backups` <span class="version-mark">New in v5.4.0</span>`
- Source Line Ranges: `5-106`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `global-configuration`, `logging`, `slow-log`, `memory-limit`, `log-rotation`, `log-format`, `versioned-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0365_aa6fedf37c`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#tikv-configuration-file`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `da9ade03503c8cf8272301f755036812c78273dc3987c9d35633b67599e05872`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#tikv-configuration-file
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiKV global or log configuration behavior such as panic exit handling, slow log output, memory usage limit, or log file rotation settings.
- Retrieval Keywords: abort-on-panic, slow-log-file, slow-log-threshold, memory-usage-limit, log.level, log.format, log.enable-timestamp, log.file.filename, log.file.max-size, log.file.max-days, log.file.max-backups, log-rotation-timespan, log-level, log-format, log-file, log-rotation-size, stderr, core dump files
- Follow-up Guidance: The content also points to the default file `etc/config-template.toml`, the `config.toml` name, command-line parameter documentation, and `Modify the configuration` guidance.
- Classification Note: This chunk is classified as TiKV configuration because it defines configurable global and logging parameters, defaults, optional values, and deprecated-to-new item mappings.

## Official Source Content

# TiKV Configuration File

The TiKV configuration file supports more options than command-line parameters. You can find the default configuration file in [etc/config-template.toml](https://github.com/tikv/tikv/blob/release-8.1/etc/config-template.toml) and rename it to `config.toml`.

This document only describes the parameters that are not included in command-line parameters. For more details, see [command-line parameter](https://docs.pingcap.com/tidb/stable/command-line-flags-for-tikv-configuration).

> **Tip:**
>
> If you need to adjust the value of a configuration item, refer to [Modify the configuration](https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#modify-the-configuration).
## Global configuration
### `abort-on-panic`

+ Sets whether to call `abort()` to exit the process when TiKV panics. This option affects whether TiKV allows the system to generate core dump files.

    + If the value of this configuration item is `false`, when TiKV panics, it calls `exit()` to exit the process.
    + If the value of this configuration item is `true`, when TiKV panics, TiKV calls `abort()` to exit the process. At this time, TiKV allows the system to generate core dump files when exiting. To generate the core dump file, you also need to perform the system configuration related to core dump (for example, setting the size limit of the core dump file via `ulimit -c` command, and configure the core dump path. Different operating systems have different related configurations). To avoid the core dump files occupying too much disk space and causing insufficient TiKV disk space, it is recommended to set the core dump generation path to a disk partition different to that of TiKV data.

+ Default value: `false`
### `slow-log-file`

+ The file that stores slow logs
+ If this configuration item is not set, but `log.file.filename` is set, slow logs are output to the log file specified by `log.file.filename`.
+ If neither `slow-log-file` nor `log.file.filename` are set, all logs are output to "stderr" by default.
+ If both configuration items are set, ordinary logs are output to the log file specified by `log.file.filename`, and slow logs are output to the log file set by `slow-log-file`.
+ Default value: `""`
### `slow-log-threshold`

+ The threshold for outputting slow logs. If the processing time is longer than this threshold, slow logs are output.
+ Default value: `"1s"`
### `memory-usage-limit`

+ The limit on memory usage of the TiKV instance. When the memory usage of TiKV almost reaches this threshold, internal cache will be evicted to release memory.
+ In most cases, the TiKV instance is set to use 75% of the total available system memory, so you do not need to explicitly specify this configuration item. The rest 25% of the memory is reserved for the OS page cache. See [`storage.block-cache.capacity`](#capacity) for details.
+ When deploying multiple TiKV nodes on a single physical machine, you still do not need to set this configuration item. In this case, the TiKV instance uses `5/3 * block-cache.capacity` of memory.
+ The default value for different system memory capacity is as follows:

    + system=8G    block-cache=3.6G    memory-usage-limit=6G   page-cache=2G
    + system=16G   block-cache=7.2G    memory-usage-limit=12G  page-cache=4G
    + system=32G   block-cache=14.4G   memory-usage-limit=24G  page-cache=8G
## log New in v5.4.0

+ Configuration items related to the log.

+ From v5.4.0, to make the log configuration items of TiKV and TiDB consistent, TiKV deprecates the former configuration item `log-rotation-timespan` and changes `log-level`, `log-format`, `log-file`, `log-rotation-size` to the following ones. If you only set the old configuration items, and their values are set to non-default values, the old items remain compatible with the new items. If both old and new configuration items are set, the new items take effect.
### `level` New in v5.4.0

+ The log level
+ Optional values: `"debug"`, `"info"`, `"warn"`, `"error"`, `"fatal"`
+ Default value: `"info"`
### `format` New in v5.4.0

+ The log format
+ Optional values: `"json"`, `"text"`
+ Default value: `"text"`
### `enable-timestamp` New in v5.4.0

+ Determines whether to enable or disable the timestamp in the log
+ Optional values: `true`, `false`
+ Default value: `true`
## log.file New in v5.4.0

+ Configuration items related to the log file.
### `filename` New in v5.4.0

+ The log file. If this configuration item is not set, logs are output to "stderr" by default. If this configuration item is set, logs are output to the corresponding file.
+ Default value: `""`
### `max-size` New in v5.4.0

+ The maximum size of a single log file. When the file size is larger than the value set by this configuration item, the system automatically splits the single file into multiple files.
+ Default value: `300`
+ Maximum value: `4096`
+ Unit: MiB
### `max-days` New in v5.4.0

+ The maximum number of days that TiKV keeps log files.
    + If the configuration item is not set, or the value of it is set to the default value `0`, TiKV does not clean log files.
    + If the parameter is set to a value other than `0`, TiKV cleans up the expired log files after `max-days`.
+ Default value: `0`
### `max-backups` New in v5.4.0

+ The maximum number of log files that TiKV keeps.
    + If the configuration item is not set, or the value of it is set to the default value `0`, TiKV keeps all log files.
    + If the configuration item is set to a value other than `0`, TiKV keeps at most the number of old log files specified by `max-backups`. For example, if the value is set to `7`, TiKV keeps up to 7 old log files.
+ Default value: `0`
