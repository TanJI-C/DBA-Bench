# TiDB 2.1.2 release notes across TiDB, PD, TiKV, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.2.md`
- Source Title: `TiDB 2.1.2 Release Notes`
- Source Heading Path: `TiDB 2.1.2 Release Notes | TiDB 2.1.2 Release Notes > TiDB | TiDB 2.1.2 Release Notes > PD | TiDB 2.1.2 Release Notes > TiKV | TiDB 2.1.2 Release Notes > Tools`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `lightning`
- Topic Tags: `release-notes`, `compatibility`, `stability`, `rolling-update`, `region-merge`, `kafka`, `lightning`, `binlog`, `bug-fixes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0070_7d94a6aed7`
- Source ID: `tidb-docs-8.1:releases/release-2.1.2.md#tidb-2-1-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b1c745f4705b980bf776991cffb9e9d01f79c5949bd1cbca9e2c0256a81856d4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.2#tidb-2-1-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the official TiDB 2.1.2 release notes that summarize compatibility and stability changes across TiDB, PD, TiKV, TiDB Lightning, and TiDB Binlog.
- Retrieval Keywords: TiDB 2.1.2 Release Notes, TiDB Ansible 2.1.2, rolling update, TiDB Binlog Kafka version, TIDB_SMJ Hint, AntiSemiJoin, utf8 character set, generated column index panic, Region merge, Approximate Size Split, DAY d configuration format, TiDB Lightning minimum cluster version 2.1.0, Too many open engines, Drainer writing data to Kafka
- Follow-up Guidance: The source lists component-specific fixes and compatibility items for TiDB, PD, TiKV, TiDB Lightning, and TiDB Binlog in this release.
- Classification Note: This is a release-notes chunk because the content officially enumerates version 2.1.2 changes, fixes, and compatibility updates across multiple components.

## Official Source Content

# TiDB 2.1.2 Release Notes

On December 22, 2018, TiDB 2.1.2 is released. The corresponding TiDB Ansible 2.1.2 is also released. Compared with TiDB 2.1.1, this release has great improvement in system compatibility and stability.
## TiDB

- Make TiDB compatible with TiDB Binlog of the Kafka version [#8747](https://github.com/pingcap/tidb/pull/8747)
- Improve the exit mechanism of TiDB in a rolling update [#8707](https://github.com/pingcap/tidb/pull/8707)
- Fix the panic issue caused by adding the index for the generated column in some cases [#8676](https://github.com/pingcap/tidb/pull/8676)
- Fix the issue that the optimizer cannot find the optimal query plan when `TIDB_SMJ Hint` exists in the SQL statement in some cases [#8729](https://github.com/pingcap/tidb/pull/8729)
- Fix the issue that `AntiSemiJoin` returns an incorrect result in some cases [#8730](https://github.com/pingcap/tidb/pull/8730)
- Improve the valid character check of the `utf8` character set [#8754](https://github.com/pingcap/tidb/pull/8754)
- Fix the issue that the field of the time type might return an incorrect result when the write operation is performed before the read operation in a transaction [#8746](https://github.com/pingcap/tidb/pull/8746)
## PD

- Fix the Region information update issue about Region merge [#1377](https://github.com/pingcap/pd/pull/1377)
## TiKV

- Support the configuration format in the unit of `DAY` (`d`) and fix the configuration compatibility issue [#3931](https://github.com/tikv/tikv/pull/3931)
- Fix the possible panic issue caused by `Approximate Size Split` [#3942](https://github.com/tikv/tikv/pull/3942)
- Fix two issues about Region merge [#3822](https://github.com/tikv/tikv/pull/3822), [#3873](https://github.com/tikv/tikv/pull/3873)
## Tools

+ TiDB Lightning
    - Make TiDB 2.1.0 the minimum cluster version supported by Lightning
    - Fix the content error of the file involving parsed `JSON` data in Lightning [#144](https://github.com/pingcap/tidb-tools/issues/144)
    - Fix the issue that `Too many open engines` occurs after the checkpoint is used to restart Lightning
+ TiDB Binlog
    - Eliminate some bottlenecks of Drainer writing data to Kafka
    - Support the Kafka version of TiDB Binlog
