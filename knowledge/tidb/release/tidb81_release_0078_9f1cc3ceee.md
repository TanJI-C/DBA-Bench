# TiDB 2.1.6 release notes across TiDB, TiKV, and Tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.6.md`
- Source Title: `TiDB 2.1.6 Release Notes`
- Source Heading Path: `TiDB 2.1.6 Release Notes | TiDB 2.1.6 Release Notes > TiDB | TiDB 2.1.6 Release Notes > TiKV | TiDB 2.1.6 Release Notes > Tools`
- Source Line Ranges: `5-40`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `lightning`
- Topic Tags: `release-notes`, `stability`, `sql-optimizer`, `executor`, `statistics`, `server`, `ddl`, `binlog`, `transactions`, `etcd`, `protobuf`, `import`, `csv`, `memory-usage`, `region-split`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0078_9f1cc3ceee`
- Source ID: `tidb-docs-8.1:releases/release-2.1.6.md#tidb-2-1-6-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b7318869d0a8c77311f6553c8f6c418c82b82b493f5238aef01a465d04e80878`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.6#tidb-2-1-6-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for what changed in TiDB 2.1.6 release notes across TiDB, TiKV, and Lightning, including optimizer, server, DDL, protobuf parsing, and import behavior updates.
- Retrieval Keywords: TiDB 2.1.6 Release Notes, TiDB Ansible 2.1.6, TIDB_INLJ, IndexScan, show stats_histograms, log_bin, Binlog, false transaction commit, Create Table Like, AutoSync, etcd clients, protobuf parsing failure, StoreNotMatch, Lightning, region-split-size, 512 MiB, SST, RocksDB, CSV, non-alphanumeric characters in schema names
- Follow-up Guidance: The source also groups the changes by TiDB, TiKV, and Tools > Lightning within the TiDB 2.1.6 Release Notes.
- Classification Note: This is classified as a release chunk because the official content is a versioned release note summarizing fixes and improvements for TiDB 2.1.6, TiKV, and Lightning.

## Official Source Content

# TiDB 2.1.6 Release Notes

On March 15, 2019, TiDB 2.1.6 is released. The corresponding TiDB Ansible 2.1.6 is also released. Compared with TiDB 2.1.5, this release has greatly improved the stability, the SQL optimizer, statistics, and the execution engine.
## TiDB

+ SQL Optimizer/Executor
    - Optimize planner to select the outer table based on cost when both tables are specified in Hint of `TIDB_INLJ` [#9615](https://github.com/pingcap/tidb/pull/9615)
    - Fix the issue that `IndexScan` cannot be selected correctly in some cases [#9587](https://github.com/pingcap/tidb/pull/9587)
    - Fix incompatibility with MySQL of check in the `agg` function in subqueries [#9551](https://github.com/pingcap/tidb/pull/9551)
    - Make `show stats_histograms` only output valid columns to avoid panics [#9502](https://github.com/pingcap/tidb/pull/9502)

+ Server
    - Support the `log_bin` variable to enable/disable Binlog [#9634](https://github.com/pingcap/tidb/pull/9634)
    - Add a sanity check for transactions to avoid false transaction commit [#9559](https://github.com/pingcap/tidb/pull/9559)
    - Fix the issue that setting variables may lead to panic  [#9539](https://github.com/pingcap/tidb/pull/9539)

+ DDL
    - Fix the issue that the `Create Table Like` statement causes panic in some cases [#9652](https://github.com/pingcap/tidb/pull/9652)
    - Enable the `AutoSync` feature of etcd clients to avoid connection issues between TiDB and etcd in some cases [#9600](https://github.com/pingcap/tidb/pull/9600)
## TiKV

- Fix the issue that a `protobuf` parsing failure would in some cases cause a `StoreNotMatch` error [#4303](https://github.com/tikv/tikv/pull/4303)
## Tools

+ Lightning
    - Change the default `region-split-size` of importer to 512 MiB [#4369](https://github.com/tikv/tikv/pull/4369)
    - Save the intermediate SST previously cached in memory to the local disk to reduce memory usage [#4369](https://github.com/tikv/tikv/pull/4369)
    - Limit the memory usage of RocksDB [#4369](https://github.com/tikv/tikv/pull/4369)
    - Fix the issue that Regions are scattered before scheduling is finished [#4369](https://github.com/tikv/tikv/pull/4369)
    - Separate importing of data and indexes for large tables to effectively reduce time consumption when importing in batches [#132](https://github.com/pingcap/tidb-lightning/pull/132)
    - Support CSV [#111](https://github.com/pingcap/tidb-lightning/pull/111)
    - Fix the error of import failure due to non-alphanumeric characters in schema names [#9547](https://github.com/pingcap/tidb/pull/9547)
