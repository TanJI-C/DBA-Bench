# Release overview, compatibility changes, and important bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.0-rc.2.md`
- Source Title: `TiDB 4.0 RC.2 Release Notes`
- Source Heading Path: `TiDB 4.0 RC.2 Release Notes | TiDB 4.0 RC.2 Release Notes > Compatibility Changes | TiDB 4.0 RC.2 Release Notes > Important Bug Fixes`
- Source Line Ranges: `5-51`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `lightning`, `tiflash`
- Topic Tags: `release-notes`, `compatibility`, `bug-fixes`, `transactions`, `binlog`, `configuration`, `partitioning`, `encryption`, `sql-mode`, `logging`, `gc`, `performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0153_c9660aed2d`
- Source ID: `tidb-docs-8.1:releases/release-4.0.0-rc.2.md#tidb-4-0-rc-2-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e4d7a26fc341c6fd4682fc593a5815b9ca8c8ae58147caffef74fdeb76ce19a8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.0-rc.2#tidb-4-0-rc-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.0-rc.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.0-rc.2 compatibility changes or important bug fixes involving transaction size limits, CLUSTER_LOG behavior, partitioned table creation, TiKV encryption config paths, or TiDB Lightning default behavior.
- Retrieval Keywords: TiDB 4.0.0-rc.2, Compatibility Changes, Important Bug Fixes, txn-total-size-limit, TiDB Binlog, Kafka, CLUSTER_LOG, specified time range, CREATE TABLE, sub-partition, linear hash, [encryption], [security.encryption], TiDB Lightning, ONLY_FULL_GROUP_BY,NO_AUTO_CREATE_USER, tidb-backend mode, tmp file, wrong partition, WHERE clause has only one equivalent condition, incorrect Index range, PointGet, DELETE, GC worker deadlock, RegionMiss retry, MySQL protocol, DEBUG, PRE_SPLIT_REGIONS, TRUNCATE, two-phase commit, IndexMerge, wide_table, Memory Trackers, special characters
- Follow-up Guidance: This chunk also lists release-note bug fixes for TiDB and TiFlash, including PointGet after DELETE, GC worker deadlock, PRE_SPLIT_REGIONS after TRUNCATE, and startup failure after upgrade when database or table names contain special characters.
- Classification Note: The official content is classified as release information because it enumerates compatibility changes and important bug fixes in TiDB 4.0 RC.2 across TiDB, TiKV, TiDB Lightning, and TiFlash.

## Official Source Content

# TiDB 4.0 RC.2 Release Notes

Release date: May 15, 2020

TiDB version: 4.0.0-rc.2
## Compatibility Changes

+ TiDB

    - Remove the size limit for a single transaction (100 MB) when TiDB Binlog is enabled. Now the size limit for a transaction is 10 GB. However, if TiDB Binlog is enabled and the downstream is Kafka, configure the `txn-total-size-limit` parameter according to the message size limit of 1 GB in Kafka [#16941](https://github.com/pingcap/tidb/pull/16941)
    - Change the behavior from querying the default time range to returning an error and requesting a specified time range if the time range is not specified when querying the `CLUSTER_LOG` table [#17003](https://github.com/pingcap/tidb/pull/17003)
    - If the unsupported `sub-partition` or `linear hash` option is specified when creating the partitioned table using the `CREATE TABLE` statement, the normal table is created rather than the partitioned table with the options ignored [#17197](https://github.com/pingcap/tidb/pull/17197)

+ TiKV

    - Move the encryption-related configuration to the security-related configuration, which means changing `[encryption]` in the TiKV configuration file to `[security.encryption]` [#7810](https://github.com/tikv/tikv/pull/7810)

+ Tools

    - TiDB Lightning

        - Change the default SQL mode to `ONLY_FULL_GROUP_BY,NO_AUTO_CREATE_USER` when importing data to improve compatibility [#316](https://github.com/pingcap/tidb-lightning/pull/316)
        - Disallow accessing the PD or TiKV port in the tidb-backend mode [#312](https://github.com/pingcap/tidb-lightning/pull/312)
        - Print the log information to the tmp file by default, and print the path of the tmp file when TiDB Lightning is started [#313](https://github.com/pingcap/tidb-lightning/pull/313)
## Important Bug Fixes

+ TiDB

    - Fix the issue that the wrong partition is chosen when the `WHERE` clause has only one equivalent condition [#17054](https://github.com/pingcap/tidb/pull/17054)
    - Fix the issue of wrong results caused by building the incorrect Index range when the `WHERE` clause only contains the string column [#16660](https://github.com/pingcap/tidb/pull/16660)
    - Fix the panic issue that occurs when executing the `PointGet` query in the transaction after the `DELETE` operation [#16991](https://github.com/pingcap/tidb/pull/16991)
    - Fix the issue that the GC worker might encounter the deadlock when an error occurs [#16915](https://github.com/pingcap/tidb/pull/16915)
    - Avoid the unnecessary RegionMiss retry when the TiKV response is slow but not down [#16956](https://github.com/pingcap/tidb/pull/16956)
    - Change the log level in the client in the handshake phase of the MySQL protocol to `DEBUG` to solve the problem that interferes with log output [#16881](https://github.com/pingcap/tidb/pull/16881)
    - Fix the issue that the Region is not pre-split according to the `PRE_SPLIT_REGIONS` information defined by the table after the `TRUNCATE` operation [#16776](https://github.com/pingcap/tidb/pull/16776)
    - Fix the issue of soaring goroutine caused by retry when TiKV is unavailable during the second phase of the two-phase commit [#16876](https://github.com/pingcap/tidb/pull/16876)
    - Fix the panic issue of statement execution when some expressions cannot be pushed down [#16869](https://github.com/pingcap/tidb/pull/16869)
    - Fix the wrong execution result of the IndexMerge operation on the partitioned table [#17124](https://github.com/pingcap/tidb/pull/17124)
    - Fix the performance reduction of `wide_table` caused by the mutex contention of Memory Trackers [#17234](https://github.com/pingcap/tidb/pull/17234)

+ TiFlash

    - Fix the issue that the system cannot start normally after the upgrade if the name of the database or table contains special characters
