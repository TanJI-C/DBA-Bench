# Diagnostic report configuration information and change history tables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-diagnostics-report.md`
- Source Title: `TiDB Dashboard Diagnostic Report`
- Source Heading Path: `TiDB Dashboard Diagnostic Report > View report > Configuration information`
- Source Line Ranges: `287-319`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `configuration`, `change-history`, `diagnostic-report`, `current-config`, `initial-config`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0068_c63756bfb2`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-diagnostics-report.md#configuration-information`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1d5bafcb470f3e901060bf1d96187728dd53441e2122271b973e97f2fefa32f6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-report#configuration-information
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-diagnostics-report.md

## Retrieval Guidance

- Use When: Use this chunk when you need to interpret configuration information in a TiDB Dashboard diagnostic report, including which tables show start-of-range values, change history within the report time range, and current values at report generation time.
- Retrieval Keywords: Configuration information, Scheduler Initial Config, TiDB GC Initial Config, TiKV RocksDB Initial Config, TiKV RaftStore Initial Config, Scheduler Config Change History, TiDB GC Config Change History, TiKV RocksDB Config Change History, TiKV RaftStore Config Change History, TiDB's Current Config, PD's Current Config, TiKV's Current Config, leader-schedule-limit, report time range, current config, change history
- Follow-up Guidance: The example explains that `leader-schedule-limit` shown at the report start time is the initial value at that time, while a later record such as `2020-05-22T20:07:00+08:00` indicates the configuration was modified around that time.
- Classification Note: This is reference content because it defines how diagnostic report configuration tables represent initial values, modified configuration records, and current configuration snapshots.

## Official Source Content

### Configuration information

In the configuration information, the configuration values of some modules are shown within the report time range. But the historical values of some other configurations of these modules cannot be obtained, so the shown values of these configurations are the current (when the report is generated) values .

Within the report time range, the following tables include items whose values are configured at the start time of the report time range:

* `Scheduler Initial Config`: The initial value of PD scheduling-related configuration at the report's start time.
* `TiDB GC Initial Config`: The initial value of TiDB GC related-configuration at the report's start time
* `TiKV RocksDB Initial Config`: The initial value of TiKV RocksDB-related configuration at the report's start time
* `TiKV RaftStore Initial Config`: The initial value of TiKV RaftStore-related configuration at the report's start time

Within the report time range, if some configurations have been modified, the following tables include records of some configurations that have been modified:

* `Scheduler Config Change History`
* `TiDB GC Config Change History`
* `TiKV RocksDB Config Change History`
* `TiKV RaftStore Config Change History`

Example:

![Scheduler Config Change History report](/media/dashboard/dashboard-diagnostics-config-change.png)

The table above shows that the `leader-schedule-limit` configuration parameter has been modified within the report time range:

* `2020-05-22T20:00:00+08:00`: At the start time of the report, the configuration value of `leader-schedule-limit` is `4`, which does not mean that the configuration has been modified, but that at the start time in the report time range, its configuration value is `4`.
* `2020-05-22T20:07:00+08:00`: The `leader-schedule-limit` configuration value is `8`, which indicates that the value of this configuration has been modified around `2020-05-22T20:07:00+08:00`.

The following tables show the current configuration of TiDB, PD, and TiKV at the time when the report is generated:

* `TiDB's Current Config`
* `PD's Current Config`
* `TiKV's Current Config`
