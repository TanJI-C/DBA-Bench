# TiDB 7.5.3 release overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.3.md`
- Source Title: `TiDB 7.5.3 Release Notes`
- Source Heading Path: `TiDB 7.5.3 Release Notes | TiDB 7.5.3 Release Notes > Compatibility changes | TiDB 7.5.3 Release Notes > Improvements`
- Source Line Ranges: `5-47`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `br`, `ticdc`
- Topic Tags: `release-notes`, `compatibility`, `system-tables`, `configuration-scope`, `grpc-compression`, `performance-improvements`, `tls`, `concurrency`, `log-backup`, `pitr`, `mq`, `cloud-storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0538_b90fc93670`
- Source ID: `tidb-docs-8.1:releases/release-7.5.3.md#tidb-7-5-3-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `aa5d7d26d646013fdc76fbc6360e3c96c4726feae7e55f9a4fbce80435ee33b0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.3#tidb-7-5-3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.3.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.5.3 release-note information about compatibility changes and component improvements across TiDB, TiFlash, BR, and TiCDC.
- Retrieval Keywords: TiDB 7.5.3 Release Notes, Compatibility changes, Improvements, INFORMATION_SCHEMA.KEYWORDS, server.grpc-compression-type, gRPC response messages sent from TiKV to TiDB, TRUNCATE, DROP, partitioned tables, TiFlash placement rules, TLS, updating certificates, highly concurrent data read operations, short query performance, br log restore, br log subcommands, TiDB domain, memory consumption, log backup tasks, checkpoint lag, blocking GC, DNS errors, PITR, adding index acceleration, absence of a leader in a Region, Alibaba Cloud access credentials, environment variables, raw events, Message Queue, MQ, cloud storage
- Follow-up Guidance: The chunk also points to Quick start and Production deployment links for TiDB v7.5.
- Classification Note: The content is classified as a release chunk because it summarizes the TiDB 7.5.3 release date, compatibility changes, and improvements for multiple components.

## Official Source Content

# TiDB 7.5.3 Release Notes

Release date: August 5, 2024

TiDB version: 7.5.3

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.5/production-deployment-using-tiup)
## Compatibility changes

- Add a new system table [`INFORMATION_SCHEMA.KEYWORDS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-keywords) to display the information of all keywords supported by TiDB [#48801](https://github.com/pingcap/tidb/issues/48801) @[dveeden](https://github.com/dveeden)
- Change the scope of the TiKV configuration item [`server.grpc-compression-type`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#grpc-compression-type):

    - In v7.5.x versions earlier than v7.5.3, this configuration item only affects the compression algorithm of gRPC messages between TiKV nodes.
    - Starting from v7.5.3, this configuration item also affects the compression algorithm of gRPC response messages sent from TiKV to TiDB. Enabling compression might consume more CPU resources. [#17176](https://github.com/tikv/tikv/issues/17176) @[ekexium](https://github.com/ekexium)
## Improvements

+ TiDB

    - By batch deleting TiFlash placement rules, improve the processing speed of data GC after performing the `TRUNCATE` or `DROP` operation on partitioned tables [#54068](https://github.com/pingcap/tidb/issues/54068) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)

+ TiFlash

    - Mitigate the issue that TiFlash might panic due to updating certificates after TLS is enabled [#8535](https://github.com/pingcap/tiflash/issues/8535) @[windtalker](https://github.com/windtalker)
    - Reduce lock conflicts under highly concurrent data read operations and optimize short query performance [#9125](https://github.com/pingcap/tiflash/issues/9125) @[JinheLin](https://github.com/JinheLin)

+ Tools

    + Backup & Restore (BR)

        - Except for the `br log restore` subcommand, all other `br log` subcommands support skipping the loading of the TiDB `domain` data structure to reduce memory consumption [#52088](https://github.com/pingcap/tidb/issues/52088) @[Leavrth](https://github.com/Leavrth)
        - Support automatically abandoning log backup tasks when encountering a large checkpoint lag, to avoid prolonged blocking GC and potential cluster issues [#50803](https://github.com/pingcap/tidb/issues/50803) @[RidRisR](https://github.com/RidRisR)
        - Increase the number of retries for failures caused by DNS errors [#53029](https://github.com/pingcap/tidb/issues/53029) @[YuJuncen](https://github.com/YuJuncen)
        - Add PITR integration test cases to cover compatibility testing for log backup and adding index acceleration [#51987](https://github.com/pingcap/tidb/issues/51987) @[Leavrth](https://github.com/Leavrth)
        - Increase the number of retries for failures caused by the absence of a leader in a Region [#54017](https://github.com/pingcap/tidb/issues/54017) @[Leavrth](https://github.com/Leavrth)
        - Support setting Alibaba Cloud access credentials through environment variables [#45551](https://github.com/pingcap/tidb/issues/45551) @[RidRisR](https://github.com/RidRisR)

    + TiCDC

        - Support directly outputting raw events when the downstream is a Message Queue (MQ) or cloud storage [#11211](https://github.com/pingcap/tiflow/issues/11211) @[CharlesCheung96](https://github.com/CharlesCheung96)
