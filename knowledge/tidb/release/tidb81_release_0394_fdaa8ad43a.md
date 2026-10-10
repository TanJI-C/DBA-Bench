# TiDB 6.5.3 overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.3.md`
- Source Title: `TiDB 6.5.3 Release Notes`
- Source Heading Path: `TiDB 6.5.3 Release Notes | TiDB 6.5.3 Release Notes > Compatibility changes | TiDB 6.5.3 Release Notes > Compatibility changes > Behavior changes | TiDB 6.5.3 Release Notes > Improvements`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `ticdc`
- Topic Tags: `release-notes`, `compatibility`, `behavior-changes`, `improvements`, `stale-read`, `placement-rules`, `metrics`, `leader-election`, `compression`, `ddl`, `replication`, `kafka`, `oauth`, `tls`, `object-storage`, `binlog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0394_fdaa8ad43a`
- Source ID: `tidb-docs-8.1:releases/release-6.5.3.md#tidb-6-5-3-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7f49977958fef4beef7d3f3ccc6f60c2ca39684665e4f6225ff5999bdc2aa94a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.3#tidb-6-5-3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.3.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.5.3 release-note information about compatibility changes and improvements across TiDB, TiKV, PD, TiCDC, and TiDB Binlog.
- Retrieval Keywords: TiDB 6.5.3 Release Notes, Compatibility changes, Behavior changes, TiCDC splits update event into delete and insert events, primary key or non-null unique index value is modified, TRUNCATE on partitioned tables with Placement Rules, Stale Read OPS, Stale Read MBps, DataIsNotReady, check_leader requests, gzip, PD leader election, separate gRPC connection, TiCDC DDLs do not block other unrelated DML Events, AddKeyValue, replicating data to object storage, Kafka-on-Pulsar, OAuth protocol for validation when replicating data to Kafka, Avro or CSV protocol, split UPDATE into DELETE and INSERT, insecure-skip-verify, enabling TLS, GC TLS, Drainer
- Follow-up Guidance: The source also points to TiCDC split update behavior documentation for transactions containing a single update change.
- Classification Note: This is classified as a release chunk because it summarizes the TiDB 6.5.3 overview, one compatibility behavior change, and component improvements listed in the official release notes.

## Official Source Content

# TiDB 6.5.3 Release Notes

Release date: June 14, 2023

TiDB version: 6.5.3

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.5/production-deployment-using-tiup)
## Compatibility changes
### Behavior changes

- When processing update event, TiCDC splits an event into delete and insert events if the primary key or non-null unique index value is modified in the event. For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-split-update-behavior#transactions-containing-a-single-update-change).
## Improvements

+ TiDB

    - Improve the performance of `TRUNCATE` on partitioned tables with Placement Rules [#43070](https://github.com/pingcap/tidb/issues/43070) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Avoid invalid Stale Read retries after resolving locks [#43659](https://github.com/pingcap/tidb/issues/43659) @[you06](https://github.com/you06)
    - Reduce latency by using leader read when Stale Read encounters the `DataIsNotReady` error [#765](https://github.com/tikv/client-go/pull/765) @[Tema](https://github.com/Tema)
    - Add `Stale Read OPS` and `Stale Read MBps` metrics to track hit rate and traffic when using Stale Read [#43325](https://github.com/pingcap/tidb/issues/43325) @[you06](https://github.com/you06)

+ TiKV

    - Reduce traffic by using gzip to compress `check_leader` requests [#14839](https://github.com/tikv/tikv/issues/14839) @[cfzjywxk](https://github.com/cfzjywxk)

+ PD

    - Use a separate gRPC connection for PD leader election to prevent the impact of other requests [#6403](https://github.com/tikv/pd/issues/6403) @[rleungx](https://github.com/rleungx)

+ Tools

    + TiCDC

        - Optimize the way TiCDC handles DDLs so that DDLs do not block the use of other unrelated DML Events, and reduce memory usage [#8106](https://github.com/pingcap/tiflow/issues/8106) @[asddongmen](https://github.com/asddongmen)
        - Optimize the Decoder interface and add a new method `AddKeyValue` [#8861](https://github.com/pingcap/tiflow/issues/8861) @[3AceShowHand](https://github.com/3AceShowHand)
        - Optimize the directory structure when DDL events occur in the scenario of replicating data to object storage [#8890](https://github.com/pingcap/tiflow/issues/8890) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Support replicating data to the Kafka-on-Pulsar downstream [#8892](https://github.com/pingcap/tiflow/issues/8892) @[hi-rustin](https://github.com/Rustin170506)
        - Support using the OAuth protocol for validation when replicating data to Kafka [#8865](https://github.com/pingcap/tiflow/issues/8865) @[hi-rustin](https://github.com/Rustin170506)
        - Optimize the way TiCDC handles the `UPDATE` statement during data replication using the Avro or CSV protocol, by splitting `UPDATE` into `DELETE` and `INSERT` statements, so that you can get the old value from the `DELETE` statement [#9086](https://github.com/pingcap/tiflow/issues/9086) @[3AceShowHand](https://github.com/3AceShowHand)
        - Add a configuration item `insecure-skip-verify` to control whether to set the authentication algorithm in the scenario of enabling TLS [#8867](https://github.com/pingcap/tiflow/issues/8867) @[hi-rustin](https://github.com/Rustin170506)
        - Optimize DDL replication operations to mitigate the impact of DDL operations on downstream latency [#8686](https://github.com/pingcap/tiflow/issues/8686) @[hi-rustin](https://github.com/Rustin170506)
        - Optimize the method of setting GC TLS for the upstream when the TiCDC replication task fails [#8403](https://github.com/pingcap/tiflow/issues/8403) @[charleszheng44](https://github.com/charleszheng44)

    + TiDB Binlog

        - Optimize the method of retrieving table information to reduce the initialization time and memory usage of Drainer [#1137](https://github.com/pingcap/tidb-binlog/issues/1137) @[lichunzhu](https://github.com/lichunzhu)
