# Release overview and new features section start

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.4.0.md`
- Source Title: `TiDB 6.4.0 Release Notes`
- Source Heading Path: `TiDB 6.4.0 Release Notes | TiDB 6.4.0 Release Notes > New features`
- Source Line Ranges: `5-35`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `dashboard`, `br`, `dm`
- Topic Tags: `release-notes`, `overview`, `new-features`, `archive-note`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0347_38dd65d01f`
- Source ID: `tidb-docs-8.1:releases/release-6.4.0.md#tidb-6-4-0-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ae830bd0279849ba1aeb8182297676bd98ea18c64e2d3e576258e04ae8b08a18`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.4.0#tidb-6-4-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 6.4.0-DMR release overview, release date, archive note, quick start link, or the top-level list of new features and improvements across components.
- Retrieval Keywords: TiDB 6.4.0 Release Notes, 6.4.0-DMR, Release date November 17 2022, archived documentation, latest LTS version, Quick start, New features, FLASHBACK CLUSTER TO TIMESTAMP, tracking the global memory usage, Linear Hash partitioning syntax, globally monotonic AUTO_INCREMENT, JSON type range selection of array data, dynamic planning algorithm, NO_DECORRELATE, cluster diagnostics becomes GA, SM4 encryption at rest, ALTER TABLE COMPACT, EBS volume snapshots, DM extended columns
- Follow-up Guidance: The source lists feature areas including SQL, Security, and Observability with more detailed descriptions in later sections.
- Classification Note: This is a release overview chunk because it states the release metadata and summarizes the main new features introduced in TiDB 6.4.0-DMR.

## Official Source Content

# TiDB 6.4.0 Release Notes

Release date: November 17, 2022

TiDB version: 6.4.0-DMR

> **Note:**
>
> The TiDB 6.4.0-DMR documentation has been [archived](https://docs-archive.pingcap.com/tidb/v6.4/). PingCAP encourages you to use [the latest LTS version](https://docs.pingcap.com/tidb/stable) of the TiDB database.

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.4/quick-start-with-tidb)

In v6.4.0-DMR, the key new features and improvements are as follows:

- Support restoring a cluster to a specific point in time by using [`FLASHBACK CLUSTER TO TIMESTAMP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster) (experimental).
- Support [tracking the global memory usage](https://docs.pingcap.com/tidb/stable/configure-memory-usage) of TiDB instances (experimental).
- Be compatible with [the Linear Hash partitioning syntax](https://docs.pingcap.com/tidb/stable/partitioned-table#how-tidb-handles-linear-hash-partitions).
- Support a high-performance and globally monotonic [`AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment#mysql-compatibility-mode) (experimental).
- Support range selection of array data in [the JSON type](https://docs.pingcap.com/tidb/stable/data-type-json).
- Accelerate fault recovery in extreme situations such as disk failures and stuck I/O.
- Add the [dynamic planning algorithm](https://docs.pingcap.com/tidb/stable/join-reorder#example-the-dynamic-programming-algorithm-of-join-reorder) to determine table join order.
- Introduce [a new optimizer hint `NO_DECORRELATE`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_decorrelate) to control whether to perform decorrelation for correlated subqueries.
- The [cluster diagnostics](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-access) feature becomes GA.
- TiFlash supports the SM4 algorithm for [encryption at rest](https://docs.pingcap.com/tidb/stable/encryption-at-rest#tiflash).
- Support using a SQL statement to [compact TiFlash replicas of specified partitions in a table immediately](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact#compact-tiflash-replicas-of-specified-partitions-in-a-table).
- Support [backing up a TiDB cluster using EBS volume snapshots](https://docs.pingcap.com/tidb-in-kubernetes/v1.4/backup-to-aws-s3-by-snapshot).
- DM supports [writing upstream data source information to the extended columns of the downstream merged table](https://docs.pingcap.com/tidb/stable/dm/dm-table-routing#extract-table-schema-and-source-information-and-write-into-the-merged-table).
## New features
