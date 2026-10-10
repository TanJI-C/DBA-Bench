# Release overview, compatibility changes, and telemetry default change

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.2.md`
- Source Title: `TiDB 4.0.2 Release Notes`
- Source Heading Path: `TiDB 4.0.2 Release Notes | TiDB 4.0.2 Release Notes > Compatibility Changes | TiDB 4.0.2 Release Notes > New Change`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `dashboard`
- Topic Tags: `release-notes`, `compatibility`, `telemetry`, `slow-query-log`, `statement-summary`, `sequence-cache`, `cluster-info`, `diagnostic-rules`, `store-limit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0177_8f13016a0e`
- Source ID: `tidb-docs-8.1:releases/release-4.0.2.md#tidb-4-0-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8318132f39c3b7b263f74126e141eacea91971263f9b7ba01ecf1f432ae86d71`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.2#tidb-4-0-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.2 release-note changes about compatibility adjustments or the default telemetry behavior in TiDB, PD, and TiDB Dashboard.
- Retrieval Keywords: TiDB 4.0.2 Release Notes, Compatibility Changes, New Change, slow query log, statement summary table, sequence cache, negative value, CLUSTER_INFO, tombstone TiKV, tombstone TiFlash, diagnostic rule, current-load, node-check, PD store-limit, store-balance-rate, telemetry, TiDB Dashboard, share usage details with PingCAP
- Follow-up Guidance: The source points to Telemetry for details about what is shared and how to disable the sharing.
- Classification Note: This is classified as a release chunk because the official content summarizes TiDB 4.0.2 compatibility changes and a new default telemetry-related change across components.

## Official Source Content

# TiDB 4.0.2 Release Notes

Release date: July 1, 2020

TiDB version: 4.0.2
## Compatibility Changes

+ TiDB

    - Remove sensitive information in the slow query log and the statement summary table [#18130](https://github.com/pingcap/tidb/pull/18130)
    - Forbid negative value in the sequence cache [#18103](https://github.com/pingcap/tidb/pull/18103)
    - Remove tombstone TiKV and TiFlash stores from the `CLUSTER_INFO` table [#17953](https://github.com/pingcap/tidb/pull/17953)
    - Change the diagnostic rule from `current-load` to `node-check` [#17660](https://github.com/pingcap/tidb/pull/17660)

+ PD

    - Persist `store-limit` and remove `store-balance-rate` [#2557](https://github.com/pingcap/pd/pull/2557)
## New Change

- By default, TiDB and TiDB Dashboard share usage details with PingCAP to help understand how to improve the product [#18180](https://github.com/pingcap/tidb/pull/18180). For details about what is shared and how to disable the sharing, see [Telemetry](https://docs.pingcap.com/tidb/stable/telemetry).
