# TiDB 4.0.13 release overview, new features, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.13.md`
- Source Title: `TiDB 4.0.13 Release Notes`
- Source Heading Path: `TiDB 4.0.13 Release Notes | TiDB 4.0.13 Release Notes > New Features | TiDB 4.0.13 Release Notes > Improvements`
- Source Line Ranges: `5-53`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`, `tiflash`, `br`, `ticdc`
- Topic Tags: `release-notes`, `new-features`, `improvements`, `auto-random`, `infoschema`, `statistics`, `tso`, `dashboard`, `backup`, `flow-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0166_7b758bba5f`
- Source ID: `tidb-docs-8.1:releases/release-4.0.13.md#tidb-4-0-13-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `455e1144a3918657f828d7dec62e4443b445ff34377789aa1b9d7bb3bfbd1518`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.13#tidb-4-0-13-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.13.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 4.0.13 release overview or specific new features and improvements across TiDB, TiKV, PD, TiFlash, BR, and TiCDC.
- Retrieval Keywords: TiDB 4.0.13 Release Notes, TiDB 4.0.13, AUTO_INCREMENT to AUTO_RANDOM, infoschema.client_errors_summary, mysql.stats_histograms, store used size, EpochNotMatch, TSO processing time, dashboard v2021.03.12.1, Automatically clean archived data, BR mysql schema user tables, checkVersion, TiKV node failures during backup, TiCDC processor flow control, Unified Sorter, sort-dir, cdc server, HTTP handler for the failpoint
- Follow-up Guidance: This chunk is followed by bug fixes in the same TiDB 4.0.13 release notes.
- Classification Note: The content is classified as a release note overview because it lists the release date, new features, and improvements for multiple components in TiDB 4.0.13.

## Official Source Content

# TiDB 4.0.13 Release Notes

Release date: May 28, 2021

TiDB version: 4.0.13
## New Features

+ TiDB

    - Support changing an `AUTO_INCREMENT` column to an `AUTO_RANDOM` one [#24608](https://github.com/pingcap/tidb/pull/24608)
    - Add the `infoschema.client_errors_summary` tables to help users keep track of the errors that have been returned to clients [#23267](https://github.com/pingcap/tidb/pull/23267)
## Improvements

+ TiDB

    - Avoid frequently reading the `mysql.stats_histograms` table if the cached statistics is up-to-date to avoid high CPU usage [#24352](https://github.com/pingcap/tidb/pull/24352)

+ TiKV

    - Make the calculation process of `store used size` more precise [#9904](https://github.com/tikv/tikv/pull/9904)
    - Set more Regions in the `EpochNotMatch` message to reduce Region misses [#9731](https://github.com/tikv/tikv/pull/9731)
    - Speed up freeing the memory accumulated in the long-running cluster [#10035](https://github.com/tikv/tikv/pull/10035)

+ PD

    - Optimize the metrics of TSO processing time to help users determine whether the TSO processing time at the PD side is too long [#3524](https://github.com/pingcap/pd/pull/3524)
    - Update the dashboard version to v2021.03.12.1 [#3469](https://github.com/pingcap/pd/pull/3469)

+ TiFlash

    - Automatically clean archived data to free up disk space

+ Tools

    + Backup & Restore (BR)

        - Support backing up user tables created in the `mysql` schema [#1077](https://github.com/pingcap/br/pull/1077)
        - Update `checkVersion` to check the cluster data and the backup data [#1090](https://github.com/pingcap/br/pull/1090)
        - Tolerate a small number of TiKV node failures during backup [#1062](https://github.com/pingcap/br/pull/1062)

    + TiCDC

        - Implement the processor flow control to avoid memory overflow (OOM) [#1751](https://github.com/pingcap/tiflow/pull/1751)
        - Support cleaning up stale temporary files in Unified Sorter and prevent multiple `cdc server` instances from sharing the same `sort-dir` directory [#1741](https://github.com/pingcap/tiflow/pull/1741)
        - Add the HTTP handler for the failpoint [#1732](https://github.com/pingcap/tiflow/pull/1732)
