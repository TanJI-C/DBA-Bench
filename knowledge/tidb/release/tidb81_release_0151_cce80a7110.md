# RC.1 overview, compatibility changes, important fixes, and new features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.0-rc.1.md`
- Source Title: `TiDB 4.0 RC.1 Release Notes`
- Source Heading Path: `TiDB 4.0 RC.1 Release Notes | TiDB 4.0 RC.1 Release Notes > Compatibility Changes | TiDB 4.0 RC.1 Release Notes > Important Bug Fixes | TiDB 4.0 RC.1 Release Notes > New Features`
- Source Line Ranges: `5-100`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `ticdc`, `br`, `pd`
- Topic Tags: `release-notes`, `compatibility`, `important-bug-fixes`, `new-features`, `data-consistency`, `deadlock`, `replication`, `encryption`, `kms`, `coprocessor`, `split-region`, `diagnostics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0151_cce80a7110`
- Source ID: `tidb-docs-8.1:releases/release-4.0.0-rc.1.md#tidb-4-0-rc-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `95856abdd3f20e01395c38cfb2532f78499e85ba0ed721c0927f34a67e4a89bd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.0-rc.1#tidb-4-0-rc-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.0-rc.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 4.0.0-rc.1 overview covering compatibility changes, important bug fixes, and new features across TiDB, TiKV, TiFlash, TiCDC, BR, and PD.
- Retrieval Keywords: TiDB 4.0.0-rc.1, RC.1 Release Notes, Compatibility Changes, Important Bug Fixes, New Features, Hibernate Region, Drainer sequence DDL, INSERT ... ON DUPLICATE UPDATE, MemBuffer, data inconsistency duplicated keys, probe request deadlock, minimum commit timestamp overflow, rename table, recover table, flashback table, TiCDC replication failure, prewrite event, checksum disabled, auto-random, alter-pk, SHOW CONFIG, Coprocessor cache, Coprocessor requests to TiFlash in batches, user-owned KMS key, split region, AWS KMS, config manager, DeltaTree engine, INFORMATION_SCHEMA.CLUSTER_INFO, Kafka sink module, resolve lock, GC safe point, S3/GCS storage URL
- Follow-up Guidance: The chunk also groups the release notes into Compatibility Changes, Important Bug Fixes, and New Features for the affected components.
- Classification Note: This is a release-notes summary chunk because the official content lists version-wide compatibility changes, notable fixes, and added features for TiDB 4.0.0-rc.1.

## Official Source Content

# TiDB 4.0 RC.1 Release Notes

Release date: April 28, 2020

TiDB version: 4.0.0-rc.1
## Compatibility Changes

+ TiKV

    - Disable the Hibernate Region feature by default [#7618](https://github.com/tikv/tikv/pull/7618)

+ TiDB Binlog

    - Support the sequence DDL operation in Drainer [#950](https://github.com/pingcap/tidb-binlog/pull/950)
## Important Bug Fixes

+ TiDB

    - Fix the issue that the `INSERT ... ON DUPLICATE UPDATE` statement might be incorrectly executed on multiple rows in an explicit transaction because `MemBuffer` is not checked [#16689](https://github.com/pingcap/tidb/pull/16689)
    - Fix the data inconsistency when locking duplicated keys on multiple rows [#16769](https://github.com/pingcap/tidb/pull/16769)
    - Fix the panic that occurs when recycling the non-superbatch idle connection between TiDB instances [#16303](https://github.com/pingcap/tidb/pull/16303)

+ TiKV

    - Fix the deadlock issue caused by the probe request from TiDB [#7540](https://github.com/tikv/tikv/pull/7540)
    - Fix the issue that the minimum commit timestamp of a transaction might overflow which affects data correctness [#7638](https://github.com/tikv/tikv/pull/7638)

+ TiFlash

    - Fix the data loss issue caused by the `rename table` operation when multiple data paths are configured
    - Fix the issue that an error occurs when reading data from a merged Region
    - Fix the issue that an error occurs when reading data from a Region that is in the abnormal state
    - Modify the mapping of table names in TiFlash to correctly support `recover table`/`flashback table`
    - Modify the storage path to fix the potential data loss issue that occurs when renaming the table
    - Fix the potential panic of TiDB when Super Batch is enabled
    - Modify the read mode in the online update scenario to improve the read performance

+ TiCDC

    - Fix the replication failure that occurs because the schema internally maintained in TiCDC fails to correctly handle the timing issue of read and write operations [#438](https://github.com/pingcap/tiflow/pull/438) [#450](https://github.com/pingcap/tiflow/pull/450) [#478](https://github.com/pingcap/tiflow/pull/478) [#496](https://github.com/pingcap/tiflow/pull/496)
    - Fix the bug that the TiKV client fails to correctly maintain the internal resources when encountering some TiKV anomalies [#499](https://github.com/pingcap/tiflow/pull/499) [#492](https://github.com/pingcap/tiflow/pull/492)
    - Fix the bug that meta data is not correctly cleaned up and abnormally remains in the TiCDC nodes [#488](https://github.com/pingcap/tiflow/pull/488) [#504](https://github.com/pingcap/tiflow/pull/504)
    - Fix the issue that the TiKV client fails to correctly handle the repeated sending of the prewrite event [#446](https://github.com/pingcap/tiflow/pull/446)
    - Fix the issue that the TiKV client fails to correctly handle the redundant prewrite events received before the initialization [#448](https://github.com/pingcap/tiflow/pull/448)

+ Backup & Restore (BR)

    - Fix the issue that checksum is still executed when checksum is disabled [#223](https://github.com/pingcap/br/pull/223)
    - Fix the incremental replication failure when `auto-random` or `alter-pk` is enabled in TiDB [#230](https://github.com/pingcap/br/pull/230) [#231](https://github.com/pingcap/br/pull/231)
## New Features

+ TiDB

    - Support sending Coprocessor requests to TiFlash in batches [#16226](https://github.com/pingcap/tidb/pull/16226)
    - Enable the Coprocessor cache feature by default [#16710](https://github.com/pingcap/tidb/pull/16710)
    - Parse only the registered sections of a statement in the special comment of the SQL statement [#16157](https://github.com/pingcap/tidb/pull/16157)
    - Support using the `SHOW CONFIG` syntax to show the configurations of PD and TiKV instances [#16475](https://github.com/pingcap/tidb/pull/16475)

+ TiKV

    - Support using the user-owned KMS key for the server-side encryption when backing up data to S3 [#7630](https://github.com/tikv/tikv/pull/7630)
    - Enable the load-based `split region` operation [#7623](https://github.com/tikv/tikv/pull/7623)
    - Support validating common names [#7468](https://github.com/tikv/tikv/pull/7468)
    - Add the file lock check to avoid starting multiple TiKV instances that are bound to the same address [#7447](https://github.com/tikv/tikv/pull/7447)
    - Support AWS KMS in encryption at rest [#7465](https://github.com/tikv/tikv/pull/7465)

+ Placement Driver (PD)

    - Remove `config manager` to let other components control their component configurations [#2349](https://github.com/pingcap/pd/pull/2349)

+ TiFlash

    - Add the metrics report related to the read and write workloads of DeltaTree engine
    - Cache the `handle` and `version` columns to reduce the disk I/O of a single read or write request
    - Support pushing down the `fromUnixTime` and `dateFormat` functions
    - Evaluate the global state according to the first disk and report this evaluation
    - Add the graphics in Grafana related to the read and write workloads of DeltaTree engine
    - Optimize the decimal data encoding in the `Chunk` codec
    - Implement the gRPC API of Diagnostics (SQL diagnosis) to support querying system tables such as `INFORMATION_SCHEMA.CLUSTER_INFO`

+ TiCDC

    - Support sending messages in batches in the Kafka sink module [#426](https://github.com/pingcap/tiflow/pull/426)
    - Support file sorting in the processor [#477](https://github.com/pingcap/tiflow/pull/477)
    - Support automatic `resolve lock` [#459](https://github.com/pingcap/tiflow/pull/459)
    - Add the feature that automatically updates the TiCDC service GC safe point to PD [#487](https://github.com/pingcap/tiflow/pull/487)
    - Add the timezone setting for data replication [#498](https://github.com/pingcap/tiflow/pull/498)

+ Backup and Restore (BR)

    - Support configuring S3/GCS in the storage URL [#246](https://github.com/pingcap/br/pull/246)
