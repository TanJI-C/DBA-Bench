# Improvements across TiDB, TiKV, PD, dashboard, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.14.md`
- Source Title: `TiDB 4.0.14 Release Notes`
- Source Heading Path: `TiDB 4.0.14 Release Notes > Improvements`
- Source Line Ranges: `36-79`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `dashboard`, `br`, `dumpling`, `ticdc`
- Topic Tags: `stable result mode`, `push down`, `scheduler conflict`, `memory consumption`, `restore speed`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0171_8c3691cb54`
- Source ID: `tidb-docs-8.1:releases/release-4.0.14.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `da5b04265fa682afaca2a160b04981889166cfbb8df039a298db1584ebe0bd54`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.14#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.14.md

## Retrieval Guidance

- Use When: Use this chunk when searching for improvement items in TiDB 4.0.14 across TiDB, TiKV, PD, TiDB Dashboard, BR, Dumpling, and TiCDC.
- Retrieval Keywords: Improvements, point get, batch point get, UPDATE reads, LOCK record into PUT record, init_connect, stable result mode, json_unquote(), push down to TiKV, SQL Plan Management, SPM not affected by the character set, shutdown the status server first, stale peers, TiCDC sink memory consumption, even split, Region is too large, multiple schedulers, TiDB Dashboard v2021.07.17.1, read-only session, BR merging small backup files, Dumpling _tidb_rowid, TiDB v3.x cluster, PD endpoint misses the certificate, sorter I/O errors, Region incremental scan concurrency limit, table memory consumption metrics, capture-session-ttl
- Follow-up Guidance: The chunk groups the improvements by component, including TiDB, TiKV, PD, TiDB Dashboard, and Tools such as BR, Dumpling, and TiCDC.
- Classification Note: This is classified as a release improvements section because the official content enumerates behavior, performance, usability, and configuration improvements across multiple components.

## Official Source Content

## Improvements

+ TiDB

    - Change the `LOCK` record into the `PUT` record for the index keys using `point get` or `batch point get` for `UPDATE` reads [#26223](https://github.com/pingcap/tidb/pull/26223)
    - Support the MySQL system variable `init_connect` and its associated features [#26031](https://github.com/pingcap/tidb/pull/26031)
    - Support the stable result mode to make the query results more stable [#26003](https://github.com/pingcap/tidb/pull/26003)
    - Support pushing down the built-in function `json_unquote()` to TiKV [#25721](https://github.com/pingcap/tidb/pull/25721)
    - Make the SQL Plan Management (SPM) not affected by the character set [#23295](https://github.com/pingcap/tidb/pull/23295)

+ TiKV

    - Shutdown the status server first to make sure that the client can correctly check the shutdown status [#10504](https://github.com/tikv/tikv/pull/10504)
    - Always respond to stale peers to make sure that these peers are cleared quicker [#10400](https://github.com/tikv/tikv/pull/10400)
    - Limit the TiCDC sink's memory consumption [#10147](https://github.com/tikv/tikv/pull/10147)
    - When a Region is too large, use the even split to speed up the split process [#10275](https://github.com/tikv/tikv/pull/10275)

+ PD

    - Reduce the conflicts among multiple schedulers that run at the same time [#3858](https://github.com/pingcap/pd/pull/3858) [#3854](https://github.com/tikv/pd/pull/3854)

+ TiDB Dashboard

    - Update TiDB Dashboard to v2021.07.17.1 [#3882](https://github.com/pingcap/pd/pull/3882)
    - Support sharing the current session as a read-only session to avoid further modification to it [#960](https://github.com/pingcap/tidb-dashboard/pull/960)

+ Tools

    + Backup & Restore (BR)

        - Speed up restore by merging small backup files [#655](https://github.com/pingcap/br/pull/655)

    + Dumpling

        - Always split tables using `_tidb_rowid` when the upstream is a TiDB v3.x cluster, which helps reduce TiDB's memory usage [#306](https://github.com/pingcap/dumpling/pull/306)

    + TiCDC

        - Improve the error message returned when a PD endpoint misses the certificate [#1973](https://github.com/pingcap/tiflow/issues/1973)
        - Make the sorter I/O errors more user-friendly [#1976](https://github.com/pingcap/tiflow/pull/1976)
        - Add a concurrency limit on the Region incremental scan in the KV client to reduce the pressure of TiKV [#1926](https://github.com/pingcap/tiflow/pull/1926)
        - Add metrics for the table memory consumption [#1884](https://github.com/pingcap/tiflow/pull/1884)
        - Add `capture-session-ttl` to the TiCDC server configuration [#2169](https://github.com/pingcap/tiflow/pull/2169)
