# Release overview and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.1.md`
- Source Title: `TiDB 6.5.1 Release Notes`
- Source Heading Path: `TiDB 6.5.1 Release Notes | TiDB 6.5.1 Release Notes > Compatibility changes`
- Source Line Ranges: `5-29`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `pd`, `tidb`, `tikv`, `tiup`
- Topic Tags: `release-date`, `version`, `telemetry`, `upgrade-impact`, `default-values`, `compatibility`, `partitioned-tables`, `stale-read`, `cdc`, `network-traffic`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0373_27377ab37d`
- Source ID: `tidb-docs-8.1:releases/release-6.5.1.md#tidb-6-5-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d36faeb1a0cb5387af3199fee0b9d82c1cff7d28f35c6584b7444999be326d86`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.1#tidb-6-5-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.1.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.5.1 release-note details about compatibility changes, default value changes, telemetry behavior after upgrade, partitioned table column type support, or Stale Read and CDC timing defaults.
- Retrieval Keywords: TiDB 6.5.1 Release Notes, Compatibility changes, Release date March 10, 2023, TiDB version 6.5.1, telemetry feature disabled by default, tidb_enable_telemetry, enable-telemetry, PD enable-telemetry, TiUP v1.11.3 telemetry, modifying column types on partitioned tables, advance-ts-interval, Stale Read latency, cdc.min-ts-interval, network traffic
- Follow-up Guidance: The source also points to TiDB Release Timeline for specific versions and to Reduce Stale Read latency for details about advance-ts-interval.
- Classification Note: This is classified as a release chunk because it summarizes TiDB 6.5.1 compatibility changes and default behavior changes across TiDB, PD, TiKV, and TiUP.

## Official Source Content

# TiDB 6.5.1 Release Notes

Release date: March 10, 2023

TiDB version: 6.5.1

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.5/production-deployment-using-tiup)
## Compatibility changes

- Starting from February 20, 2023, the [telemetry feature](https://docs.pingcap.com/tidb/stable/telemetry) is disabled by default in new versions of TiDB and TiDB Dashboard, including v6.5.1, and usage information is not collected and shared with PingCAP. Before upgrading to these versions, if the cluster uses the default telemetry configuration, the telemetry feature is disabled after the upgrade. See [TiDB Release Timeline](https://docs.pingcap.com/tidb/stable/releases/release-timeline) for specific versions.

    - The default value of the [`tidb_enable_telemetry`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_telemetry-new-in-v402-and-deprecated-in-v810) system variable is changed from `ON` to `OFF`.
    - The default value of the TiDB [`enable-telemetry`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-telemetry-new-in-v402-and-deprecated-in-v810) configuration item is changed from `true` to `false`.
    - The default value of the PD [`enable-telemetry`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-telemetry) configuration item is changed from `true` to `false`.

- Starting from v1.11.3, the telemetry feature is disabled by default in newly deployed TiUP, and usage information is not collected. If you upgrade from a TiUP version earlier than v1.11.3 to v1.11.3 or a later version, the telemetry feature keeps the same status as before the upgrade.

- No longer support modifying column types on partitioned tables because of potential correctness issues. [#40620](https://github.com/pingcap/tidb/issues/40620) @[mjonss](https://github.com/mjonss)

- The default value of the TiKV [`advance-ts-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#advance-ts-interval) configuration item is changed from `1s` to `20s`. You can modify this configuration item to reduce the latency and improve the timeliness of the Stale Read data. See [Reduce Stale Read latency](https://docs.pingcap.com/tidb/stable/stale-read#reduce-stale-read-latency) for details.

- The default value of the TiKV [`cdc.min-ts-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#min-ts-interval) configuration item is changed from `"200ms"` to `"1s"` to reduce network traffic.
