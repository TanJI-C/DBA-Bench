# TiDB 2.0 RC5 release notes for TiDB, PD, and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.0-rc.5.md`
- Source Title: `TiDB 2.0 RC5 Release Notes`
- Source Heading Path: `TiDB 2.0 RC5 Release Notes | TiDB 2.0 RC5 Release Notes > TiDB | TiDB 2.0 RC5 Release Notes > PD | TiDB 2.0 RC5 Release Notes > TiKV`
- Source Line Ranges: `5-46`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `sql`
- Topic Tags: `release-notes`, `mysql-compatibility`, `sql-optimization`, `stability`, `topn-pushdown`, `batchget`, `add-index`, `memory-usage`, `raft-learner`, `scheduler`, `schedule-limit`, `rawkvclient`, `tikv-ctl`, `coprocessor`, `importer`, `grpc`, `rocksdb`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0026_ec83e0936a`
- Source ID: `tidb-docs-8.1:releases/release-2.0-rc.5.md#tidb-2-0-rc5-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `67d60f555cd0b3971b82bec583ace815e33f94e1a0892a63f35f194628c9fc61`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.0-rc.5#tidb-2-0-rc5-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.0-rc.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 2.0 RC5 release summary and the specific TiDB, PD, or TiKV changes introduced in this release.
- Retrieval Keywords: TiDB 2.0 RC5 Release Notes, On April 17, 2018, TiDB 2.0 RC5 is released, MySQL compatibility, SQL optimization, stability, Top-N pushdown, BatchGet, Add Index, insert on duplicate key update, UNIX_TIMESTAMP, Show Process List, Alter Table Modify Column, table comment, Raft Learner, Balance Region Scheduler, schedule-limit, tikv-ctl, RawKVClient, OOM issue caused by too many snapshots, Coprocessor, block-cache-size, importer, ImportSST::Upload, gRPC keepalive, tikv-importer, RocksDB metric, overflow as warning
- Follow-up Guidance: The source groups the changes by component under the TiDB, PD, and TiKV sections of the TiDB 2.0 RC5 release notes.
- Classification Note: This is a release-notes chunk because the official content announces TiDB 2.0 RC5 and enumerates fixes, optimizations, and new support items for TiDB, PD, and TiKV.

## Official Source Content

# TiDB 2.0 RC5 Release Notes

On April 17, 2018, TiDB 2.0 RC5 is released. This release has great improvement in MySQL compatibility, SQL optimization and stability.
## TiDB

- Fix the issue about applying the `Top-N` pushdown rule
- Fix the estimation of the number of rows for the columns that contain NULL values
- Fix the zero value of the Binary type
- Fix the `BatchGet` issue within a transaction
- Clean up the written data while rolling back the `Add Index` operation, to reduce consumed space
- Optimize the `insert on duplicate key update` statement to improve the performance by 10 times
- Fix the issue about the type of the results returned by the `UNIX_TIMESTAMP` function
- Fix the issue that the NULL value is inserted while adding NOT NULL columns
- Support showing memory usage of the executing statements in the `Show Process List` statement
- Fix the issue that `Alter Table Modify Column` reports an error in extreme conditions
- Support setting the table comment using the `Alter` statement
## PD

- Add support for Raft Learner
- Optimize the Balance Region Scheduler to reduce scheduling overhead
- Adjust the default value of `schedule-limit` configuration
- Fix the issue of allocating ID frequently
- Fix the compatibility issue when adding a new scheduler
## TiKV

- Support the Region specified by `compact` in `tikv-ctl`
- Support Batch Put, Batch Get, Batch Delete and Batch Scan in the RawKVClient
- Fix the OOM issue caused by too many snapshots
- Return more detailed error information in Coprocessor
- Support dynamically modifying the `block-cache-size` in TiKV through `tikv-ctl`
- Further improve `importer`
- Simplify the `ImportSST::Upload` interface
- Configure the `keepalive` property of gRPC
- Split `tikv-importer` from TiKV as an independent binary
- Provide statistics about the number of rows scanned by each `scan range` in Coprocessor
- Fix the compilation issue on the macOS system
- Fix the issue of misusing a RocksDB metric
- Support the `overflow as warning` option in Coprocessor
