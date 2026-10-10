# PD server, security, logging, and metrics configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-configuration-file.md`
- Source Title: `PD Configuration File`
- Source Heading Path: `PD Configuration File > pd-server | PD Configuration File > pd-server > `server-memory-limit` <span class="version-mark">New in v6.6.0</span> | PD Configuration File > pd-server > `server-memory-limit-gc-trigger` <span class="version-mark">New in v6.6.0</span> | PD Configuration File > pd-server > `enable-gogc-tuner` <span class="version-mark">New in v6.6.0</span> | PD Configuration File > pd-server > `gc-tuner-threshold` <span class="version-mark">New in v6.6.0</span> | PD Configuration File > pd-server > `flow-round-by-digit` <span class="version-mark">New in TiDB 5.1</span> | PD Configuration File > pd-server > `min-resolved-ts-persistence-interval` <span class="version-mark">New in v6.0.0</span> | PD Configuration File > security | PD Configuration File > security > `cacert-path` | PD Configuration File > security > `cert-path` | PD Configuration File > security > `key-path` | PD Configuration File > security > `redact-info-log` <span class="version-mark">New in v5.0</span> | PD Configuration File > `log` | PD Configuration File > `log` > `level` | PD Configuration File > `log` > `format` | PD Configuration File > `log` > `disable-timestamp` | PD Configuration File > `log.file` | PD Configuration File > `log.file` > `max-size` | PD Configuration File > `log.file` > `max-days` | PD Configuration File > `log.file` > `max-backups` | PD Configuration File > `metric``
- Source Line Ranges: `128-266`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `shared`
- Topic Tags: `memory-limits`, `gc`, `experimental-features`, `flow-statistics`, `upgrade-behavior`, `resolved-ts`, `tls`, `certificate-paths`, `log-redaction`, `logging`, `log-rotation`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0125_fe61a85386`
- Source ID: `tidb-docs-8.1:pd-configuration-file.md#pd-server`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e21b5933a6310103574f89976d804d900a8d8891b1bd4ab2a1bf890de85ed24d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-configuration-file#pd-server
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for PD pd-server, security, logging, log rotation, or monitoring configuration items, including memory limit, GC tuner, TLS certificate paths, log redaction, and metrics settings.
- Retrieval Keywords: pd-server, server-memory-limit, server-memory-limit-gc-trigger, enable-gogc-tuner, gc-tuner-threshold, flow-round-by-digit, trace-region-flow, min-resolved-ts-persistence-interval, security, cacert-path, cert-path, key-path, redact-info-log, log, level, format, disable-timestamp, log.file, max-size, max-days, max-backups, metric, GOGC Tuner, resolved timestamp, X509 certificate, PEM file
- Follow-up Guidance: The source notes upgrade-related default behavior for flow-round-by-digit and min-resolved-ts-persistence-interval, including that older upgraded clusters can retain previous defaults.
- Classification Note: This chunk is classified as PD configuration because it documents PD server runtime options, security certificate paths, logging and log file retention settings, and monitoring-related configuration headings.

## Official Source Content

## pd-server

Configuration items related to pd-server
### `server-memory-limit` New in v6.6.0

> **Warning:**
>
> This configuration is an experimental feature. It is not recommended to use it in production environments.

+ The memory limit ratio for a PD instance. The value `0` means no memory limit.
+ Default value: `0`
+ Minimum value: `0`
+ Maximum value: `0.99`
### `server-memory-limit-gc-trigger` New in v6.6.0

> **Warning:**
>
> This configuration is an experimental feature. It is not recommended to use it in production environments.

+ The threshold ratio at which PD tries to trigger GC. When the memory usage of PD reaches the value of `server-memory-limit` * the value of `server-memory-limit-gc-trigger`, PD triggers a Golang GC. Only one GC is triggered in one minute.
+ Default value: `0.7`
+ Minimum value: `0.5`
+ Maximum value: `0.99`
### `enable-gogc-tuner` New in v6.6.0

> **Warning:**
>
> This configuration is an experimental feature. It is not recommended to use it in production environments.

+ Controls whether to enable the GOGC Tuner.
+ Default value: `false`
### `gc-tuner-threshold` New in v6.6.0

> **Warning:**
>
> This configuration is an experimental feature. It is not recommended to use it in production environments.

+ The maximum memory threshold ratio for tuning GOGC. When the memory exceeds this threshold, i.e. the value of `server-memory-limit` * the value of `gc-tuner-threshold`, GOGC Tuner stops working.
+ Default value: `0.6`
+ Minimum value: `0`
+ Maximum value: `0.9`
### `flow-round-by-digit` New in TiDB 5.1

+ Default value: 3
+ PD rounds the lowest digits of the flow number, which reduces the update of statistics caused by the changes of the Region flow information. This configuration item is used to specify the number of lowest digits to round for the Region flow information. For example, the flow `100512` will be rounded to `101000` because the default value is `3`. This configuration replaces `trace-region-flow`.

> **Note:**
>
> If you have upgraded your cluster from a TiDB 4.0 version to the current version, the behavior of `flow-round-by-digit` after the upgrading and the behavior of `trace-region-flow` before the upgrading are consistent by default. This means that if the value of `trace-region-flow` is false before the upgrading, the value of `flow-round-by-digit` after the upgrading is 127; if the value of `trace-region-flow` is `true` before the upgrading, the value of `flow-round-by-digit` after the upgrading is `3`.
### `min-resolved-ts-persistence-interval` New in v6.0.0

+ Determines the interval at which the minimum resolved timestamp is persistent to the PD. If this value is set to `0`, it means that the persistence is disabled.
+ Default value: Before v6.3.0, the default value is `"0s"`. Starting from v6.3.0, the default value is `"1s"`, which is the smallest positive value.
+ Minimum value: `0`
+ Unit: second

> **Note:**
>
> For clusters upgraded from v6.0.0~v6.2.0, the default value of `min-resolved-ts-persistence-interval` does not change after the upgrade, which means that it will remain `"0s"`. To enable this feature, you need to manually change the value of this configuration item.
## security

Configuration items related to security
### `cacert-path`

+ The path of the CA file
+ Default value: ""
### `cert-path`

+ The path of the Privacy Enhanced Mail (PEM) file that contains the X509 certificate
+ Default value: ""
### `key-path`

+ The path of the PEM file that contains the X509 key
+ Default value: ""
### `redact-info-log` New in v5.0

+ Controls whether to enable log redaction in the PD log
+ When you set the configuration value to `true`, user data is redacted in the PD log.
+ Default value: `false`
## `log`

Configuration items related to log
### `level`

+ Specifies the level of the output log
+ Optional value: `"debug"`, `"info"`, `"warn"`, `"error"`, `"fatal"`
+ Default value: `"info"`
### `format`

+ The log format
+ Optional value: `"text"`, `"json"`
+ Default value: `"text"`
### `disable-timestamp`

+ Whether to disable the automatically generated timestamp in the log
+ Default value: `false`
## `log.file`

Configuration items related to the log file
### `max-size`

+ The maximum size of a single log file. When this value is exceeded, the system automatically splits the log into several files.
+ Default value: `300`
+ Unit: MiB
+ Minimum value: `1`
### `max-days`

+ The maximum number of days in which a log is kept
+ If the configuration item is not set, or the value of it is set to the default value 0, PD does not clean log files.
+ Default value: `0`
### `max-backups`

+ The maximum number of log files to keep
+ If the configuration item is not set, or the value of it is set to the default value 0, PD keeps all log files.
+ Default value: `0`
## `metric`

Configuration items related to monitoring
