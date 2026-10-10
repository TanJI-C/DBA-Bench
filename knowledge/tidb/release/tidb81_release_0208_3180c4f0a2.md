# TiDB 5.0.2 release overview, compatibility changes, new features, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.2.md`
- Source Title: `TiDB 5.0.2 Release Notes`
- Source Heading Path: `TiDB 5.0.2 Release Notes | TiDB 5.0.2 Release Notes > Compatibility Changes | TiDB 5.0.2 Release Notes > New Features | TiDB 5.0.2 Release Notes > Improvements`
- Source Line Ranges: `5-62`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `ticdc`, `br`, `dumpling`
- Topic Tags: `release-notes`, `compatibility-changes`, `new-features`, `improvements`, `tooling`, `monitoring`, `memory-usage`, `cpu-usage`, `region-splitting`, `backup-restore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0208_3180c4f0a2`
- Source ID: `tidb-docs-8.1:releases/release-5.0.2.md#tidb-5-0-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9a04b5c2b7f55b0f60820b912b9ea41b5fa819a795a34c88ead6523a991a0038`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.2#tidb-5-0-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 5.0.2 release overview, including compatibility changes, new features, and improvements across TiDB, TiKV, TiFlash, TiCDC, BR, and Dumpling.
- Retrieval Keywords: TiDB 5.0.2 Release Notes, Compatibility Changes, New Features, Improvements, cdc cli changefeed --sort-dir, cdc server --sort-dir, Hibernate Region, mysql.stats_histograms, high CPU usage, S3-compatible storage virtual-host addressing mode, TiCDC scan speed back pressure, TiCDC initial scan memory usage, TiCDC Old Value pessimistic transaction, Split Regions more evenly, hotspot writes, TiFlash table lock, casting INTEGER or REAL to REAL, monitoring metrics table memory consumption, sorting stage memory and CPU usages, BR cluster version of a backup, mysql schema system tables, Dumpling no error is output when a backup operation fails
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release note overview because the official content summarizes TiDB 5.0.2 compatibility changes, newly enabled features, and component-specific improvements.

## Official Source Content

# TiDB 5.0.2 Release Notes

Release date: June 10, 2021

TiDB version: 5.0.2
## Compatibility Changes

+ Tools

    + TiCDC

        - Deprecate `--sort-dir` in the `cdc cli changefeed` command. Instead, users can set `--sort-dir` in the `cdc server` command. [#1795](https://github.com/pingcap/tiflow/pull/1795)
## New Features

+ TiKV

    - Enable the Hibernate Region feature by default [#10266](https://github.com/tikv/tikv/pull/10266)
## Improvements

+ TiDB

    - Avoid frequently reading the `mysql.stats_histograms` table if the cached statistics is up-to-date to avoid high CPU usage [#24317](https://github.com/pingcap/tidb/pull/24317)

+ TiKV

    - BR now supports the S3-compatible storage using the virtual-host addressing mode [#10243](https://github.com/tikv/tikv/pull/10243)
    - Support the back pressure for TiCDC's scan speed [#10151](https://github.com/tikv/tikv/pull/10151)
    - Reduce the memory usage of TiCDC's initial scan [#10133](https://github.com/tikv/tikv/pull/10133)
    - Improve the cache hit ratio of the TiCDC's Old Value feature in the pessimistic transaction [#10089](https://github.com/tikv/tikv/pull/10089)
    - Split Regions more evenly to mitigate the issue that the growth of Region size exceeds the splitting speed when there are hotspot writes [#9785](https://github.com/tikv/tikv/issues/9785)

+ TiFlash

    - Optimize the table lock to prevent DDL jobs and data reads from blocking each other
    - Support casting the `INTEGER` or `REAL` type to `REAL` type

+ Tools

    + TiCDC

        - Add monitoring metrics for the table memory consumption [#1885](https://github.com/pingcap/tiflow/pull/1885)
        - Optimize the memory and CPU usages during the sorting stage [#1863](https://github.com/pingcap/tiflow/pull/1863)
        - Delete some useless log information that might cause user confusion [#1759](https://github.com/pingcap/tiflow/pull/1759)

    + Backup & Restore (BR)

        - Clarify some ambiguous error messages [#1132](https://github.com/pingcap/br/pull/1132)
        - Support checking the cluster version of a backup [#1091](https://github.com/pingcap/br/pull/1091)
        - Support backing up and restoring system tables in the `mysql` schema [#1143](https://github.com/pingcap/br/pull/1143) [#1078](https://github.com/pingcap/br/pull/1078)

    + Dumpling

        - Fix the issue that no error is output when a backup operation fails [#280](https://github.com/pingcap/dumpling/pull/280)
