# Improvements across TiDB, TiKV, PD, BR, Dumpling, Lightning, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.15.md`
- Source Title: `TiDB 4.0.15 Release Notes`
- Source Heading Path: `TiDB 4.0.15 Release Notes > Improvements`
- Source Line Ranges: `33-84`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `br`, `dumpling`, `lightning`, `ticdc`
- Topic Tags: `release-notes`, `improvements`, `auto-analyze`, `latency`, `logging`, `bandwidth`, `restore-speed`, `export`, `import`, `changefeed`, `metrics`, `version-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0174_f18a657ded`
- Source ID: `tidb-docs-8.1:releases/release-4.0.15.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b3be8dc4c90274311f2bc5a9ac0da8cd9bb6c93b25a0558d471e18b7f1afa427`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.15#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.15.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 4.0.15 Improvements section across TiDB, TiKV, PD, BR, Dumpling, TiDB Lightning, and TiCDC.
- Retrieval Keywords: TiDB 4.0.15 Improvements, Trigger auto-analyze based on the histogram row count, #24237, Handle read ready and write ready separately to reduce read latency, #10475, slow log of TiKV coprocessor only considers the time spent on processing requests, #10841, Drop log instead of blocking threads when the slogger thread is overloaded and the queue is filled up, #10841, Reduce the size of Resolved TS messages to save network bandwidth, #2448, Improve the performance of synchronizing Region information between PDs, #3932, Split and scatter Regions concurrently to improve restore speed, #1363, Retry BR tasks when encountering the PD request error or the TiKV I/O timeout error, #27787, Reduce empty Regions when restoring many small tables, #1374, rebase auto id, #1424, SHOW TABLE STATUS, #337, SHOW FULL TABLES, #322, START TRANSACTION ... WITH CONSISTENT SNAPSHOT, #309, SHOW CREATE TABLE, #309, Support importing data into tables that have expression index, #1404, virtual generated columns, #1404, Always pulls old values from TiKV internally, #2397, Execute DDL statements asynchronously, #2295, global gRPC connection pool, #2531, Fail fast for unrecoverable DML errors, #1724, Add Prometheus metrics for DDL executions, #2595, #2669, Prohibit operating TiCDC clusters across major or minor versions, #2601, Remove file sorter, #2325, Clean up changefeed metrics, #2156, Optimize the lock-resolving algorithm after a Region is initialized, #2188
- Follow-up Guidance: The same release notes file also includes Compatibility changes and Bug fixes sections for this release.
- Classification Note: This chunk is classified as release improvements because it enumerates performance, usability, logging, restore, export, import, metrics, and version-compatibility improvements across multiple components.

## Official Source Content

## Improvements

+ TiDB

    - Trigger auto-analyze based on the histogram row count [#24237](https://github.com/pingcap/tidb/issues/24237)

+ TiKV

    - Handle read ready and write ready separately to reduce read latency [#10475](https://github.com/tikv/tikv/issues/10475)
    - The slow log of TiKV coprocessor only considers the time spent on processing requests. [#10841](https://github.com/tikv/tikv/issues/10841)
    - Drop log instead of blocking threads when the slogger thread is overloaded and the queue is filled up [#10841](https://github.com/tikv/tikv/issues/10841)
    - Reduce the size of Resolved TS messages to save network bandwidth [#2448](https://github.com/pingcap/tiflow/issues/2448)

+ PD

    - Improve the performance of synchronizing Region information between PDs [#3932](https://github.com/tikv/pd/pull/3932)

+ Tools

    + Backup & Restore (BR)

        - Split and scatter Regions concurrently to improve restore speed [#1363](https://github.com/pingcap/br/pull/1363)
        - Retry BR tasks when encountering the PD request error or the TiKV I/O timeout error [#27787](https://github.com/pingcap/tidb/issues/27787)
        - Reduce empty Regions when restoring many small tables to avoid affecting cluster operations after the restore [#1374](https://github.com/pingcap/br/issues/1374)
        - Perform the `rebase auto id` operation while creating tables, which saves the separate `rebase auto id` DDL operation and speeds up restore [#1424](https://github.com/pingcap/br/pull/1424)

    + Dumpling

        - Filter the skipped databases before getting the table information to improve the filtering efficiency of `SHOW TABLE STATUS` [#337](https://github.com/pingcap/dumpling/pull/337)
        - Use `SHOW FULL TABLES` to get table information for tables to be exported, because `SHOW TABLE STATUS` cannot work properly in some MySQL versions [#322](https://github.com/pingcap/dumpling/issues/322)
        - Support backing up MySQL-compatible databases that do not support the `START TRANSACTION ... WITH CONSISTENT SNAPSHOT` or the `SHOW CREATE TABLE` syntax [#309](https://github.com/pingcap/dumpling/issues/309)
        - Refine the Dumpling warning log to avoid the misleading information that a dump fails [#340](https://github.com/pingcap/dumpling/pull/340)

    + TiDB Lightning

        - Support importing data into tables that have expression index or the index that depends on virtual generated columns [#1404](https://github.com/pingcap/br/issues/1404)

    + TiCDC

        - Always pulls old values from TiKV internally to improve usability [#2397](https://github.com/pingcap/tiflow/pull/2397)
        - Reduce the goroutine usage when a table's Regions are all transferred away from a TiKV node [#2284](https://github.com/pingcap/tiflow/issues/2284)
        - Optimize workerpool for fewer goroutines when concurrency is high [#2211](https://github.com/pingcap/tiflow/issues/2211)
        - Execute DDL statements asynchronously to avoid affecting other changefeeds [#2295](https://github.com/pingcap/tiflow/issues/2295)
        - Add a global gRPC connection pool and share gRPC connections among KV clients [#2531](https://github.com/pingcap/tiflow/pull/2531)
        - Fail fast for unrecoverable DML errors [#1724](https://github.com/pingcap/tiflow/issues/1724)
        - Optimize memory management when the Unified Sorter is using memory to sort data [#2553](https://github.com/pingcap/tiflow/issues/2553)
        - Add Prometheus metrics for DDL executions [#2595](https://github.com/pingcap/tiflow/issues/2595) [#2669](https://github.com/pingcap/tiflow/issues/2669)
        - Prohibit operating TiCDC clusters across major or minor versions [#2601](https://github.com/pingcap/tiflow/pull/2601)
        - Remove `file sorter` [#2325](https://github.com/pingcap/tiflow/pull/2325)
        - Clean up changefeed metrics when a changefeed is removed, and clean up processor metrics when a processor exits [#2156](https://github.com/pingcap/tiflow/issues/2156)
        - Optimize the lock-resolving algorithm after a Region is initialized [#2188](https://github.com/pingcap/tiflow/issues/2188)
