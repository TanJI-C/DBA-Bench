# TiDB 4.0.5 release notes: compatibility changes, new features, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.5.md`
- Source Title: `TiDB 4.0.5 Release Notes`
- Source Heading Path: `TiDB 4.0.5 Release Notes | TiDB 4.0.5 Release Notes > Compatibility Changes | TiDB 4.0.5 Release Notes > New Features | TiDB 4.0.5 Release Notes > Improvements`
- Source Line Ranges: `5-101`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `ticdc`, `pd`, `br`, `dumpling`, `lightning`
- Topic Tags: `release-notes`, `compatibility-changes`, `new-features`, `improvements`, `ddl`, `partitioning`, `error-codes`, `logging`, `kafka-ssl`, `old-value`, `column-flags`, `ddl-output`, `performance`, `gc`, `metrics`, `explain`, `memory-usage`, `region-scheduling`, `tso`, `gcsafepoint`, `grafana`, `encryption-at-rest`, `tls`, `backup-restore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0184_fd5255d62b`
- Source ID: `tidb-docs-8.1:releases/release-4.0.5.md#tidb-4-0-5-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `283b3ac3ce68611e9928f0c5fc0a3a21b9fa340b28dae488893ad728d6eafe1b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.5#tidb-4-0-5-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.5 release-note details about compatibility changes, new features, or improvements across TiDB, TiKV, TiFlash, PD, TiCDC, BR, Dumpling, and TiDB Lightning.
- Retrieval Keywords: TiDB 4.0.5 Release Notes, 4.0.5 compatibility changes, drop partition truncate partition job arguments multiple partitions, add partition delete-only state replicas, TiKV define error code for errors, TiFlash unified log format, TiCDC Kafka SSL connection, TiCDC old value, TiCDC column flags, TiCDC outputting DDL statements and table schema of the previous version, DecodePlan big union queries, Region cache miss GC lock scans, HTTP API to generate the TiDB metric profile, scattering partitioned tables, Grafana detailed memory usage of each instance, EXPLAIN BatchPointGet runtime information, EXPLAIN PointGet runtime information, TableReader memory usage, ALTER TABLE algorithms compatibility, single partitioned table IndexJoin inner side, PD Region HTTP API prioritize Region scheduling of a given key range, querying the GC safepoint service, TiFlash encryption at rest, TiFlash TLS for data transfer, BR optimize some logs, Dumpling release FTWRL after connections are created, TiDB Lightning optimize some logs
- Follow-up Guidance: The source groups the changes under Compatibility Changes, New Features, and Improvements, with entries organized by component such as TiDB, PD, TiFlash, TiCDC, BR, Dumpling, and TiDB Lightning.
- Classification Note: This chunk is classified as a self-managed release note because the official content is the TiDB 4.0.5 Release Notes summarizing compatibility changes, new features, and improvements for multiple components.

## Official Source Content

# TiDB 4.0.5 Release Notes

Release date: August 31, 2020

TiDB version: 4.0.5
## Compatibility Changes

+ TiDB

    - Change `drop partition` and `truncate partition`'s job arguments to support the ID array of multiple partitions [#18930](https://github.com/pingcap/tidb/pull/18930)
    - Add the delete-only state for checking `add partition` replicas [#18865](https://github.com/pingcap/tidb/pull/18865)
## New Features

+ TiKV

    - Define error code for errors [#8387](https://github.com/tikv/tikv/pull/8387)

+ TiFlash

    - Support the unified log format with TiDB

+ Tools

    + TiCDC

        - Support Kafka SSL connection [#764](https://github.com/pingcap/tiflow/pull/764)
        - Support outputting the old value [#708](https://github.com/pingcap/tiflow/pull/708)
        - Add the column flags [#796](https://github.com/pingcap/tiflow/pull/796)
        - Support outputting the DDL statements and table schema of the previous version [#799](https://github.com/pingcap/tiflow/pull/799)
## Improvements

+ TiDB

    - Optimize the performance of `DecodePlan` for big union queries [#18941](https://github.com/pingcap/tidb/pull/18941)
    - Reduce the number of GC lock scans when the `Region cache miss` error occurs [#18876](https://github.com/pingcap/tidb/pull/18876)
    - Ease the impact of statistical feedback on cluster performance [#18772](https://github.com/pingcap/tidb/pull/18772)
    - Support canceling operations before the RPC response is returned [#18580](https://github.com/pingcap/tidb/pull/18580)
    - Add the HTTP API to generate the TiDB metric profile [#18531](https://github.com/pingcap/tidb/pull/18531)
    - Support scattering partitioned tables [#17863](https://github.com/pingcap/tidb/pull/17863)
    - Add detailed memory usage of each instance in Grafana [#18679](https://github.com/pingcap/tidb/pull/18679)
    - Show the detailed runtime information of the `BatchPointGet` operator in the result of `EXPLAIN` [#18892](https://github.com/pingcap/tidb/pull/18892)
    - Show the detailed runtime information of the `PointGet` operator in the result of `EXPLAIN` [#18817](https://github.com/pingcap/tidb/pull/18817)
    - Warn the potential deadlock for `Consume` in `remove()` [#18395](https://github.com/pingcap/tidb/pull/18395)
    - Refine the behaviors of `StrToInt` and `StrToFloat` and support converting JSON to the `date`, `time`, and `timestamp` types [#18159](https://github.com/pingcap/tidb/pull/18159)
    - Support limiting the memory usage of the `TableReader` operator [#18392](https://github.com/pingcap/tidb/pull/18392)
    - Avoid too many times of backoff when retrying the `batch cop` request [#18999](https://github.com/pingcap/tidb/pull/18999)
    - Improve compatibility for `ALTER TABLE` algorithms [#19270](https://github.com/pingcap/tidb/pull/19270)
    - Make the single partitioned table support `IndexJoin` on the inner side [#19151](https://github.com/pingcap/tidb/pull/19151)
    - Support searching the log file even when the log includes invalid lines [#18579](https://github.com/pingcap/tidb/pull/18579)

+ PD

    - Support scattering Regions in stores with special engines (such as TiFlash) [#2706](https://github.com/tikv/pd/pull/2706)
    - Support the Region HTTP API to prioritize Region scheduling of a given key range [#2687](https://github.com/tikv/pd/pull/2687)
    - Improve the leader distribution after Region scattering [#2684](https://github.com/tikv/pd/pull/2684)
    - Add more tests and logs for the TSO request [#2678](https://github.com/tikv/pd/pull/2678)
    - Avoid invalid cache updates after the leader of a Region has changed [#2672](https://github.com/tikv/pd/pull/2672)
    - Add an option to allow `store.GetLimit` to return the tombstone stores [#2743](https://github.com/tikv/pd/pull/2743)
    - Support synchronizing the Region leader change between the PD leader and followers [#2795](https://github.com/tikv/pd/pull/2795)
    - Add commands for querying the GC safepoint service [#2797](https://github.com/tikv/pd/pull/2797)
    - Replace the `region.Clone` call in filters to improve performance [#2801](https://github.com/tikv/pd/pull/2801)
    - Add an option to disable updating Region flow cache to improve the performance of the large cluster [#2848](https://github.com/tikv/pd/pull/2848)

+ TiFlash

    - Add more Grafana panels to display metrics of CPU, I/O, RAM usages and metrics of the storage engine
    - Reduce I/O operations by optimizing the processing logic of Raft logs
    - Accelerate Region scheduling for the blocked `add partition` DDL statement
    - Optimize compactions of delta data in DeltaTree to reduce read and write amplification
    - Optimize the performance of applying Region snapshots by preprocessing the snapshots using multiple threads
    - Optimize the number of opening file descriptors when the read load of TiFlash is low to reduce system resource consumption
    - Optimize the number of unnecessary small files created when TiFlash restarts
    - Support encryption at rest for data storage
    - Support TLS for data transfer

+ Tools

    + TiCDC

        - Lower the frequency of getting TSO [#801](https://github.com/pingcap/tiflow/pull/801)

    + Backup & Restore (BR)

        - Optimize some logs [#428](https://github.com/pingcap/br/pull/428)

    + Dumpling

        - Release FTWRL after connections are created to reduce the lock time for MySQL [#121](https://github.com/pingcap/dumpling/pull/121)

    + TiDB Lightning

        - Optimize some logs [#352](https://github.com/pingcap/tidb-lightning/pull/352)
