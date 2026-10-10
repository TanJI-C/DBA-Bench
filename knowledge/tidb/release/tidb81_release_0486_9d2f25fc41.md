# TiFlash bug fixes in 7.1.6 release notes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.6.md`
- Source Title: `TiDB 7.1.6 Release Notes`
- Source Heading Path: `TiDB 7.1.6 Release Notes > Bug fixes`
- Source Line Ranges: `231-254`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `pd`, `br`, `lightning`
- Topic Tags: `bug-fixes`, `upgrade`, `metadata`, `late-materialization`, `query-errors`, `tls`, `network-partition`, `fastscan`, `schema-sync`, `partition-exchange`, `drop-table`, `oom`, `query-correctness`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0486_9d2f25fc41`
- Source ID: `tidb-docs-8.1:releases/release-7.1.6.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `82e0aaae8a0ca0dfdb3bf78849a4daf8437111531b6a08342deb66ee09f3064a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiFlash bug fixes in the 7.1.6 release notes related to upgrade metadata corruption, late materialization query errors, TLS startup failure, PD network partition read timeouts, FastScan duplicate rows after BR or TiDB Lightning import, schema synchronization, query correctness, or OOM during DROP TABLE.
- Retrieval Keywords: TiDB 7.1.6 Release Notes, TiFlash bug fixes, metadata might become corrupted, panic when upgrading a cluster from a version earlier than v6.5.0 to v6.5.0 or later, late materialization, column type mismatch error, JSON functions unsupported by TiFlash are pushed down to TiFlash, SSL certificate configuration to an empty string, incorrectly enables TLS, TiFlash to fail to start, network partition between TiFlash and any PD, read request timeout errors, FastScan mode, duplicate rows, BR, TiDB Lightning, Bit-type columns, invalid characters, ALTER TABLE ... EXCHANGE PARTITION, across databases, DROP TABLE, OOM, CAST(), datetime with a time zone, SUBSTRING_INDEX(), SUBSTRING(), CAST AS DECIMAL, high-concurrency read scenarios, empty key range, read tasks on TiFlash, block TiFlash queries
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a self-managed TiFlash release-note bug-fix summary because the official content lists resolved TiFlash issues in TiDB 7.1.6 and references related components such as PD, BR, and TiDB Lightning.

## Official Source Content

- Fix the issue that TiFlash metadata might become corrupted and cause the process to panic when upgrading a cluster from a version earlier than v6.5.0 to v6.5.0 or later [#9039](https://github.com/pingcap/tiflash/issues/9039) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that some queries might report a column type mismatch error after late materialization is enabled [#9175](https://github.com/pingcap/tiflash/issues/9175) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that some queries might report errors when late materialization is enabled [#9472](https://github.com/pingcap/tiflash/issues/9472) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that some JSON functions unsupported by TiFlash are pushed down to TiFlash [#9444](https://github.com/pingcap/tiflash/issues/9444) @[windtalker](https://github.com/windtalker)
    - Fix the issue that setting the SSL certificate configuration to an empty string in TiFlash incorrectly enables TLS and causes TiFlash to fail to start [#9235](https://github.com/pingcap/tiflash/issues/9235) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that a network partition (network disconnection) between TiFlash and any PD might cause read request timeout errors [#9243](https://github.com/pingcap/tiflash/issues/9243) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that a large number of duplicate rows might be read in FastScan mode after importing data via BR or TiDB Lightning [#9118](https://github.com/pingcap/tiflash/issues/9118) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that TiFlash fails to parse the table schema when the table contains Bit-type columns with a default value that contains invalid characters [#9461](https://github.com/pingcap/tiflash/issues/9461) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that queries with virtual generated columns might return incorrect results after late materialization is enabled [#9188](https://github.com/pingcap/tiflash/issues/9188) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that TiFlash might fail to synchronize schemas after executing `ALTER TABLE ... EXCHANGE PARTITION` across databases [#7296](https://github.com/pingcap/tiflash/issues/7296) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash might panic when a database is deleted shortly after creation [#9266](https://github.com/pingcap/tiflash/issues/9266) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that when using the `CAST()` function to convert a string to a datetime with a time zone or invalid characters, the result is incorrect [#8754](https://github.com/pingcap/tiflash/issues/8754) @[solotzg](https://github.com/solotzg)
    - Fix the issue that TiFlash might return transiently incorrect results in high-concurrency read scenarios [#8845](https://github.com/pingcap/tiflash/issues/8845) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that the `SUBSTRING_INDEX()` function might cause TiFlash to crash in some corner cases [#9116](https://github.com/pingcap/tiflash/issues/9116) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that frequent `EXCHANGE PARTITION` and `DROP TABLE` operations over a long period in a cluster might slow down the replication of TiFlash table metadata and degrade the query performance [#9227](https://github.com/pingcap/tiflash/issues/9227) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that a query with an empty key range fails to correctly generate read tasks on TiFlash, which might block TiFlash queries [#9108](https://github.com/pingcap/tiflash/issues/9108) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that the sign in the result of the `CAST AS DECIMAL` function is incorrect in certain cases [#9301](https://github.com/pingcap/tiflash/issues/9301) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the `SUBSTRING()` function does not support the `pos` and `len` arguments for certain integer types, causing query errors [#9473](https://github.com/pingcap/tiflash/issues/9473) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that executing `DROP TABLE` on large tables might cause TiFlash OOM [#9437](https://github.com/pingcap/tiflash/issues/9437) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)
