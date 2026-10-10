# TiDB 6.1.5 release notes: compatibility changes, improvements, and bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.5.md`
- Source Title: `TiDB 6.1.5 Release Notes`
- Source Heading Path: `TiDB 6.1.5 Release Notes | TiDB 6.1.5 Release Notes > Compatibility changes | TiDB 6.1.5 Release Notes > Improvements | TiDB 6.1.5 Release Notes > Bug fixes`
- Source Line Ranges: `5-51`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `ticdc`, `dm`, `dashboard`, `tiup`
- Topic Tags: `release-notes`, `compatibility-changes`, `telemetry`, `upgrade-impact`, `default-values`, `clustered-index`, `auto-random`, `bug-fixes`, `oom`, `read-committed`, `redo-log`, `checkpoint`, `binlog-schema`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0316_e6bf8fe910`
- Source ID: `tidb-docs-8.1:releases/release-6.1.5.md#tidb-6-1-5-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f9b318e56a3940081f94570cbb372649cd965ba99db6adb93c7c0e680f5423db`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.5#tidb-6-1-5-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.1.5 release-note details about compatibility changes, telemetry default changes, support for AUTO_RANDOM in clustered composite indexes, or fixed issues across TiDB, PD, TiCDC, DM, Dashboard, and TiUP.
- Retrieval Keywords: TiDB 6.1.5 Release Notes, Compatibility changes, Improvements, Bug fixes, telemetry feature disabled by default, tidb_enable_telemetry, enable-telemetry, TiDB Dashboard, PD enable-telemetry, TiUP v1.11.3 telemetry, AUTO_RANDOM column as the first column of the clustered composite index, UPDATE statement might not read the latest data, Read Committed isolation level, data race might cause TiDB to restart, PD OOM, ReportMinResolvedTS, TiCDC redo log OOM, replication lag is excessively high, redo log enabled to write meta, binlog-schema delete, checkpoint does not advance, skipped DDL
- Follow-up Guidance: The content also points to TiDB Release Timeline for a specific version and includes quick access links for Quick start and Production deployment.
- Classification Note: This is a self-managed release-notes chunk for TiDB 6.1.5 that summarizes compatibility changes, one TiDB improvement, and bug fixes affecting TiDB, PD, TiCDC, and DM.

## Official Source Content

# TiDB 6.1.5 Release Notes

Release date: February 28, 2023

TiDB version: 6.1.5

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.1/production-deployment-using-tiup)
## Compatibility changes

- Starting from February 20, 2023, the [telemetry feature](https://docs.pingcap.com/tidb/stable/telemetry) is disabled by default in new versions of TiDB and TiDB Dashboard, including v6.1.5, and usage information is not collected and shared with PingCAP. Before upgrading to these versions, if the cluster uses the default telemetry configuration, the telemetry feature is disabled after the upgrade. See [TiDB Release Timeline](https://docs.pingcap.com/tidb/stable/releases/release-timeline) for a specific version.

    - The default value of the [`tidb_enable_telemetry`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_telemetry-new-in-v402-and-deprecated-in-v810) system variable is changed from `ON` to `OFF`.
    - The default value of the TiDB [`enable-telemetry`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-telemetry-new-in-v402-and-deprecated-in-v810) configuration item is changed from `true` to `false`.
    - The default value of the PD [`enable-telemetry`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-telemetry) configuration item is changed from `true` to `false`.

- Starting from v1.11.3, the telemetry feature is disabled by default in newly deployed TiUP, and usage information is not collected. If you upgrade from a TiUP version earlier than v1.11.3 to v1.11.3 or a later version, the telemetry feature keeps the same status as before the upgrade.
## Improvements

- TiDB

    - Support the `AUTO_RANDOM` column as the first column of the clustered composite index [#38572](https://github.com/pingcap/tidb/issues/38572) @[tangenta](https://github.com/tangenta)
## Bug fixes

+ TiDB

    - Fix the issue that data race might cause TiDB to restart [#27725](https://github.com/pingcap/tidb/issues/27725) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that the `UPDATE` statement might not read the latest data when the Read Committed isolation level is used [#41581](https://github.com/pingcap/tidb/issues/41581) @[cfzjywxk](https://github.com/cfzjywxk)

- PD

    - Fix the PD OOM issue that occurs when the calls of `ReportMinResolvedTS` are too frequent [#5965](https://github.com/tikv/pd/issues/5965) @[HundunDM](https://github.com/HunDunDM)

+ Tools

    + TiCDC

        - Fix the issue that applying redo log might cause OOM when the replication lag is excessively high [#8085](https://github.com/pingcap/tiflow/issues/8085) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that the performance degrades when redo log is enabled to write meta [#8074](https://github.com/pingcap/tiflow/issues/8074) @[CharlesCheung96](https://github.com/CharlesCheung96)

    + TiDB Data Migration (DM)

        - Fix the issue that the `binlog-schema delete` command fails to execute [#7373](https://github.com/pingcap/tiflow/issues/7373) @[liumengya94](https://github.com/liumengya94)
        - Fix the issue that the checkpoint does not advance when the last binlog is a skipped DDL [#8175](https://github.com/pingcap/tiflow/issues/8175) @[D3Hunter](https://github.com/D3Hunter)
