# TiDB 6.5.10 overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.10.md`
- Source Title: `TiDB 6.5.10 Release Notes`
- Source Heading Path: `TiDB 6.5.10 Release Notes | TiDB 6.5.10 Release Notes > Compatibility changes | TiDB 6.5.10 Release Notes > Improvements`
- Source Line Ranges: `5-44`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `br`, `ticdc`, `lightning`, `pd`
- Topic Tags: `release-notes`, `compatibility-changes`, `improvements`, `mysql-sink`, `update-events`, `csv-import`, `show-create-table`, `mpp-load-balancing`, `shutdown`, `metrics`, `cdc`, `backup-restore`, `retries`, `redo-logs`, `replication-performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0378_440bef9332`
- Source ID: `tidb-docs-8.1:releases/release-6.5.10.md#tidb-6-5-10-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0d7b63d9da0639a2e8252b4478ee2ece418c376e7404a77ea9b5af417d42cbeb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.10#tidb-6-5-10-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.10.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.10 release-note changes in compatibility behavior or improvements across TiCDC, TiDB, TiKV, and BR.
- Retrieval Keywords: TiDB 6.5.10 Release Notes, Compatibility changes, Improvements, TiCDC split UPDATE events for MySQL sink, UPDATE change DELETE INSERT events, commitTS, thresholdTS, PD current timestamp, strict-format CSV line terminator, SHOW CREATE TABLE expression default values, MPP load balancing remove stores without Regions, TiKV shutdown speed, CDC event queue time metrics, BR empty SST files, BR DNS retries, absence of a leader in a Region retries, raw events Message Queue cloud storage, redo logs memory stability, transaction conflict scenarios replication performance
- Follow-up Guidance: The chunk points to the TiCDC documentation about split update events for MySQL sinks for more information.
- Classification Note: The official content is a self-managed TiDB 6.5.10 release-notes summary covering compatibility changes and improvements for shared components.

## Official Source Content

# TiDB 6.5.10 Release Notes

Release date: June 20, 2024

TiDB version: 6.5.10

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.5/production-deployment-using-tiup)
## Compatibility changes

- In earlier versions, when processing a transaction containing `UPDATE` changes, if the primary key or non-null unique index value is modified in an `UPDATE` event, TiCDC splits this event into `DELETE` and `INSERT` events. Starting from v6.5.10, when using the MySQL sink, TiCDC splits an `UPDATE` event into `DELETE` and `INSERT` events if the transaction `commitTS` for the `UPDATE` change is less than TiCDC `thresholdTS` (which is the current timestamp fetched from PD when TiCDC starts replicating the corresponding table to the downstream). This behavior change addresses the issue of downstream data inconsistencies caused by the potentially incorrect order of `UPDATE` events received by TiCDC, which can lead to an incorrect order of split `DELETE` and `INSERT` events. For more information, see [documentation](https://docs.pingcap.com/tidb/v6.5/ticdc-split-update-behavior#split-update-events-for-mysql-sinks). [#10918](https://github.com/pingcap/tiflow/issues/10918) @[lidezhu](https://github.com/lidezhu)
- Must set the line terminator when using TiDB Lightning `strict-format` to import CSV files [#37338](https://github.com/pingcap/tidb/issues/37338) @[lance6716](https://github.com/lance6716)
## Improvements

+ TiDB

    - Improve the MySQL compatibility of expression default values displayed in the output of `SHOW CREATE TABLE` [#52939](https://github.com/pingcap/tidb/issues/52939) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Remove stores without Regions during MPP load balancing [#52313](https://github.com/pingcap/tidb/issues/52313) @[xzhangxian1008](https://github.com/xzhangxian1008)

+ TiKV

    - Accelerate the shutdown speed of TiKV [#16680](https://github.com/tikv/tikv/issues/16680) @[LykxSassinator](https://github.com/LykxSassinator)
    - Add monitoring metrics for the queue time for processing CDC events to facilitate troubleshooting downstream CDC event latency issues [#16282](https://github.com/tikv/tikv/issues/16282) @[hicqu](https://github.com/hicqu)

+ Tools

    + Backup & Restore (BR)

        - BR cleans up empty SST files during data recovery [#16005](https://github.com/tikv/tikv/issues/16005) @[Leavrth](https://github.com/Leavrth)
        - Increase the number of retries for failures caused by DNS errors [#53029](https://github.com/pingcap/tidb/issues/53029) @[YuJuncen](https://github.com/YuJuncen)
        - Increase the number of retries for failures caused by the absence of a leader in a Region [#54017](https://github.com/pingcap/tidb/issues/54017) @[Leavrth](https://github.com/Leavrth)

    + TiCDC

        - Support directly outputting raw events when the downstream is a Message Queue (MQ) or cloud storage [#11211](https://github.com/pingcap/tiflow/issues/11211) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Improve memory stability during data recovery using redo logs to reduce the probability of OOM [#10900](https://github.com/pingcap/tiflow/issues/10900) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Significantly improve the stability of data replication in transaction conflict scenarios, with up to 10 times performance improvement [#10896](https://github.com/pingcap/tiflow/issues/10896) @[CharlesCheung96](https://github.com/CharlesCheung96)
