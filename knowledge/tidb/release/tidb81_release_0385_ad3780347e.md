# TiDB 6.5.12 overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.12.md`
- Source Title: `TiDB 6.5.12 Release Notes`
- Source Heading Path: `TiDB 6.5.12 Release Notes | TiDB 6.5.12 Release Notes > Compatibility changes | TiDB 6.5.12 Release Notes > Improvements`
- Source Line Ranges: `5-46`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `br`, `lightning`
- Topic Tags: `release-notes`, `compatibility`, `operating-system-support`, `http-api`, `ddl`, `indexing`, `read-timestamp`, `max-ts`, `garbage-collection`, `backup`, `restore`, `log-restore`, `memory-consumption`, `checksum`, `csv`, `oom-prevention`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0385_ad3780347e`
- Source ID: `tidb-docs-8.1:releases/release-6.5.12.md#tidb-6-5-12-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `43c002322ead9287a20da4d9a90efa23303f784a3e254f6c416d40ae47b3a3c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.12#tidb-6-5-12-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.12.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 6.5.12 release overview, compatibility changes, and improvements across TiDB, TiKV, TiFlash, BR, and TiDB Lightning.
- Retrieval Keywords: TiDB 6.5.12 Release Notes, Compatibility changes, Improvements, openEuler 22.03 LTS SP3/SP4, TiDB HTTP API, DDL historical tasks, default limit 2048, OOM issues, tidb_ddl_reorg_max_write_speed, adding indexes, read timestamps, max_ts, TiFlash garbage collection, clustered indexes, BR full restore empty cluster check, non-full restore same name table check, br log restore, br log subcommands, domain data structure, memory consumption, --checksum=false, full backups, TiDB Lightning, CSV files, row width check
- Follow-up Guidance: The chunk also points to OS and platform requirements and quick access links for quick start and production deployment.
- Classification Note: This is a release-notes overview chunk because the official content summarizes TiDB 6.5.12 compatibility changes and improvements for multiple components.

## Official Source Content

# TiDB 6.5.12 Release Notes

Release date: February 27, 2025

TiDB version: 6.5.12

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.5/production-deployment-using-tiup)
## Compatibility changes

- Support the openEuler 22.03 LTS SP3/SP4 operating system. For more information, see [OS and platform requirements](https://docs.pingcap.com/tidb/v6.5/hardware-and-software-requirements#os-and-platform-requirements).
- Set a default limit of 2048 for DDL historical tasks retrieved through the [TiDB HTTP API](https://github.com/pingcap/tidb/blob/release-6.5/docs/tidb_http_api.md) to prevent OOM issues caused by excessive historical tasks [#55711](https://github.com/pingcap/tidb/issues/55711) @[joccau](https://github.com/joccau)
- Add a new system variable [`tidb_ddl_reorg_max_write_speed`](https://docs.pingcap.com/tidb/v6.5/system-variables#tidb_ddl_reorg_max_write_speed-new-in-v6512) to limit the maximum speed of the ingest phase when adding indexes [#57156](https://github.com/pingcap/tidb/issues/57156) @[CbcWestwolf](https://github.com/CbcWestwolf)
## Improvements

+ TiDB

    - Enhance the validity check for read timestamps [#57786](https://github.com/pingcap/tidb/issues/57786) @[MyonKeminta](https://github.com/MyonKeminta)

+ TiKV

    - Add the detection mechanism for invalid `max_ts` updates [#17916](https://github.com/tikv/tikv/issues/17916) @[ekexium](https://github.com/ekexium)

+ TiFlash

    - Improve the garbage collection speed of outdated data in the background for tables with clustered indexes [#9529](https://github.com/pingcap/tiflash/issues/9529) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - Add a check to verify whether the target cluster is an empty cluster for full restore [#35744](https://github.com/pingcap/tidb/issues/35744) @[3pointer](https://github.com/3pointer)
        - Add a check to verify whether the target cluster contains a table with the same name for non-full restore [#55087](https://github.com/pingcap/tidb/issues/55087) @[RidRisR](https://github.com/RidRisR)
        - Except for the `br log restore` subcommand, all other `br log` subcommands support skipping the loading of the TiDB `domain` data structure to reduce memory consumption [#52088](https://github.com/pingcap/tidb/issues/52088) @[Leavrth](https://github.com/Leavrth)
        - Disable the table-level checksum calculation during full backups by default (`--checksum=false`) to improve backup performance [#56373](https://github.com/pingcap/tidb/issues/56373) @[Tristan1900](https://github.com/Tristan1900)

    + TiDB Lightning

        - Add a row width check when parsing CSV files to prevent OOM issues [#58590](https://github.com/pingcap/tidb/issues/58590) @[D3Hunter](https://github.com/D3Hunter)
