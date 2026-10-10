# TiDB 2.0.4 release notes for TiDB, PD, and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.0.4.md`
- Source Title: `TiDB 2.0.4 Release Notes`
- Source Heading Path: `TiDB 2.0.4 Release Notes | TiDB 2.0.4 Release Notes > TiDB | TiDB 2.0.4 Release Notes > PD | TiDB 2.0.4 Release Notes > TiKV`
- Source Line Ranges: `5-41`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `release-notes`, `compatibility`, `stability`, `sql-syntax`, `optimizer`, `monitoring`, `configuration`, `scheduling`, `debugging`, `gc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0032_5ed0861d98`
- Source ID: `tidb-docs-8.1:releases/release-2.0.4.md#tidb-2-0-4-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bf660f2f0f82089d1bd1e804d7c2c8dd563953e4f7176289291abba777a70042`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.0.4#tidb-2-0-4-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.0.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for what changed in TiDB 2.0.4 across TiDB, PD, and TiKV, including added syntax support, configuration changes, monitoring refinements, optimizer and compatibility fixes, scheduling behavior, debugging interfaces, and GC logging.
- Retrieval Keywords: TiDB 2.0.4 Release Notes, TiDB 2.0.4, ALTER TABLE t DROP COLUMN a CASCADE, tidb_snapshot, TSO, statement types in monitoring items, query cost estimation, backoff max delay, gRPC, memory threshold of a single statement, Optimizer error, Cast Decimal, Merge Join, Union + OrderBy, Limit/OrderBy, Union All, For Update, concat_ws, max-pending-peer-count, PendingPeer, RocksDB PerfContext, import-mode, region-properties, tikv-ctl, reverse-seek, RocksDB tombstones, do_sub, GC encounters many versions of data
- Follow-up Guidance: 
- Classification Note: This is a release-notes chunk summarizing compatibility and stability improvements in TiDB 2.0.4 for the TiDB, PD, and TiKV components.

## Official Source Content

# TiDB 2.0.4 Release Notes

On June 15, 2018, TiDB 2.0.4 is released. Compared with TiDB 2.0.3, this release has great improvement in system compatibility and stability.
## TiDB

- Support the `ALTER TABLE t DROP COLUMN a CASCADE` syntax
- Support configuring the value of `tidb_snapshot` to TSO
- Refine the display of statement types in monitoring items
- Optimize the accuracy of query cost estimation
- Configure the `backoff max delay` parameter of gRPC
- Support configuring the memory threshold of a single statement in the configuration file
- Refactor the error of Optimizer
- Fix the side effects of the `Cast Decimal` data
- Fix the wrong result issue of the `Merge Join` operator in specific scenarios
- Fix the issue of converting the Null object to String
- Fix the issue of casting the JSON type of data to the JSON type
- Fix the issue that the result order is not consistent with MySQL in the condition of `Union` + `OrderBy`
- Fix the compliance rules issue when the `Union` statement checks the `Limit/OrderBy` clause
- Fix the compatibility issue of the `Union All` result
- Fix a bug in predicate pushdown
- Fix the compatibility issue of the `Union` statement with the `For Update` clause
- Fix the issue that the `concat_ws` function mistakenly truncates the result
## PD

- Improve the behavior of the unset scheduling argument `max-pending-peer-count` by changing it to no limit for the maximum number of `PendingPeer`s
## TiKV

- Add the RocksDB `PerfContext` interface for debugging
- Remove the `import-mode` parameter
- Add the `region-properties` command for `tikv-ctl`
- Fix the issue that `reverse-seek` is slow when many RocksDB tombstones exist
- Fix the crash issue caused by `do_sub`
- Make GC record the log when GC encounters many versions of data
