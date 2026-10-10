# TiDB 6.5.0 release overview and new features introduction

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.0.md`
- Source Title: `TiDB 6.5.0 Release Notes`
- Source Heading Path: `TiDB 6.5.0 Release Notes | TiDB 6.5.0 Release Notes > New features`
- Source Line Ranges: `5-40`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `ticdc`, `br`, `dm`, `lightning`, `dumpling`, `sql`
- Topic Tags: `release-notes`, `lts`, `new-features`, `compatibility`, `performance`, `security`, `observability`, `data-migration`, `backup-restore`, `replication`, `ttl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0362_36aa55bd3b`
- Source ID: `tidb-docs-8.1:releases/release-6.5.0.md#tidb-6-5-0-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e1fca0024caf2d8fa44233df895c8794744ec6cec8a34789961b3cbdae6bf2e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.0#tidb-6-5-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for the TiDB 6.5.0 LTS release overview or a summary of key new features and improvements introduced in TiDB 6.5.0.
- Retrieval Keywords: TiDB 6.5.0 Release Notes, TiDB 6.5.0, Long-Term Support Release, LTS, New features, index acceleration, tidb_ddl_enable_fast_reorg, tidb_server_memory_limit, global memory control, AUTO_INCREMENT, FLASHBACK CLUSTER TO TIMESTAMP, TiCDC, PITR, Cost Model version 2, INDEX MERGE, JSON_EXTRACT(), TiFlash, password management, TiDB Lightning, Dumpling, compressed SQL and CSV files, DM continuous data validation, snapshot checkpoint backup, replicating data to Kafka, Time to live, TTL, replicating changed logs to object storage
- Follow-up Guidance: The source also points to the 6.2.0-DMR, 6.3.0-DMR, and 6.4.0-DMR release notes and the TiDB features page for comparisons with the previous 6.1.0 LTS.
- Classification Note: This is a release-notes overview chunk because it announces TiDB 6.5.0 as an LTS release and enumerates cross-component feature, performance, compatibility, security, observability, migration, backup, replication, and TTL updates.

## Official Source Content

# TiDB 6.5.0 Release Notes

Release date: December 29, 2022

TiDB version: 6.5.0

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.5/production-deployment-using-tiup)

TiDB 6.5.0 is a Long-Term Support Release (LTS).

Compared with TiDB [6.4.0-DMR](https://docs.pingcap.com/tidb/stable/releases/release-6.4.0), TiDB 6.5.0 introduces the following key features and improvements:

> **Tip:**
>
> Compared with the previous LTS 6.1.0, TiDB 6.5.0 also includes new features, improvements, and bug fixes released in [6.2.0-DMR](https://docs.pingcap.com/tidb/stable/releases/release-6.2.0), [6.3.0-DMR](https://docs.pingcap.com/tidb/stable/releases/release-6.3.0), and [6.4.0-DMR](https://docs.pingcap.com/tidb/stable/releases/release-6.4.0).
>
> - To get a full list of changes between the 6.1.0 LTS and 6.5.0 LTS versions, in addition to this release notes, also see [6.2.0-DMR release notes](https://docs.pingcap.com/tidb/stable/releases/release-6.2.0), [6.3.0-DMR release notes](https://docs.pingcap.com/tidb/stable/releases/release-6.3.0), and [6.4.0-DMR release notes](https://docs.pingcap.com/tidb/stable/releases/release-6.4.0).
> - To have a quick comparison of key features between the 6.1.0 LTS and 6.5.0 LTS versions, you can check the `v6.1` and `v6.5` columns in [TiDB features](https://docs.pingcap.com/tidb/stable/basic-features).

- The [index acceleration](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630) feature becomes generally available (GA), which improves the performance of adding indexes by about 10 times compared with v6.1.0.
- The TiDB global memory control becomes GA, and you can control the memory consumption threshold via [`tidb_server_memory_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit-new-in-v640).
- The high-performance and globally monotonic [`AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment#mysql-compatibility-mode) column attribute becomes GA, which is compatible with MySQL.
- [`FLASHBACK CLUSTER TO TIMESTAMP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster) is now compatible with TiCDC and PITR and becomes GA.
- Enhance TiDB optimizer by making the more accurate [Cost Model version 2](https://docs.pingcap.com/tidb/stable/cost-model#cost-model-version-2) generally available and supporting expressions connected by `AND` for [INDEX MERGE](https://docs.pingcap.com/tidb/stable/explain-index-merge).
- Support pushing down the `JSON_EXTRACT()` function to TiFlash.
- Support [password management](https://docs.pingcap.com/tidb/stable/password-management) policies that meet password compliance auditing requirements.
- TiDB Lightning and Dumpling support [importing](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-data-source) and [exporting](https://docs.pingcap.com/tidb/stable/dumpling-overview#improve-export-efficiency-through-concurrency) compressed SQL and CSV files.
- TiDB Data Migration (DM) [continuous data validation](https://docs.pingcap.com/tidb/stable/dm/dm-continuous-data-validation) becomes GA.
- TiDB Backup & Restore supports snapshot checkpoint backup, improves the recovery performance of [PITR](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide#run-pitr) by 50%, and reduces the RPO in common scenarios to as short as 5 minutes.
- Improve the TiCDC throughput of [replicating data to Kafka](https://docs.pingcap.com/tidb/stable/replicate-data-to-kafka) from 4000 rows/s to 35000 rows/s, and reduce the replication latency to 2s.
- Provide row-level [Time to live (TTL)](https://docs.pingcap.com/tidb/stable/time-to-live) to manage data lifecycle (experimental).
- TiCDC supports [replicating changed logs to object storage](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-cloud-storage) such as Amazon S3, Azure Blob Storage, and NFS (experimental).
## New features
