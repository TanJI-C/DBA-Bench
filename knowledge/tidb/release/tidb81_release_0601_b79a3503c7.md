# TiDB 8.1.1 improvements across TiDB, PD, TiFlash, BR, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.1.md`
- Source Title: `TiDB 8.1.1 Release Notes`
- Source Heading Path: `TiDB 8.1.1 Release Notes > Improvements`
- Source Line Ranges: `28-60`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tiflash`, `br`, `ticdc`, `tikv`
- Topic Tags: `release-notes`, `improvements`, `gc`, `truncate`, `drop-table`, `mpp`, `statistics`, `redact-log`, `http-client`, `tls`, `short-query`, `log-backup`, `encryption`, `disk-space-check`, `simple-protocol`, `bootstrap-messages`, `raw-events`, `message-queue`, `cloud-storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0601_b79a3503c7`
- Source ID: `tidb-docs-8.1:releases/release-8.1.1.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a2003f4442dfd4a5124d9e9984e1f33cd19699f87378b498a4e190621e8a8f0f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.1#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 8.1.1 improvements across TiDB, PD, TiFlash, BR, and TiCDC, including GC, MPP, statistics loading, redact log behavior, TLS, log backup, disk space checks, and changefeed message output.
- Retrieval Keywords: TiDB 8.1.1 Release Notes, Improvements, TRUNCATE, DROP, partitioned tables, TiFlash placement rules, data GC, MPP load balancing, Remove stores without Regions, statistics synchronously loading tasks, widespread timeouts, TiKV high loads, EXPLAIN, tidb_redact_log, PD HTTP client retry logic, TiFlash panic, updating certificates, TLS is enabled, lock conflicts, highly concurrent data read operations, short query performance, BR log backup, encryption of temporary files, br log restore, br log subcommands, TiDB domain, reduce memory consumption, Alibaba Cloud access credentials, environment variables, disk space in TiKV, downloads each SST file, restore returns an error, TiCDC, BOOTSTRAP messages, all tables, downstream, Simple Protocol, raw events, Message Queue, MQ, cloud storage
- Follow-up Guidance: The source also groups the improvements by component: TiDB, PD, TiFlash, Backup & Restore (BR), and TiCDC.
- Classification Note: This is a release-notes improvements chunk because the official content enumerates product improvements introduced in TiDB 8.1.1 across multiple components.

## Official Source Content

## Improvements

+ TiDB

    - By batch deleting TiFlash placement rules, improve the processing speed of data GC after performing the `TRUNCATE` or `DROP` operation on partitioned tables [#54068](https://github.com/pingcap/tidb/issues/54068) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Remove stores without Regions during MPP load balancing [#52313](https://github.com/pingcap/tidb/issues/52313) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Temporarily adjust the priority of statistics synchronously loading tasks to high to avoid widespread timeouts during TiKV high loads, as these timeouts might result in statistics not being loaded [#50332](https://github.com/pingcap/tidb/issues/50332) @[winoros](https://github.com/winoros)
    - The `EXPLAIN` statement supports applying the `tidb_redact_log` setting and further optimizes the log handling logic.
    - Support applying the `tidb_redact_log` setting to the output of `EXPLAIN` statements and further optimize the logic in processing logs [#54565](https://github.com/pingcap/tidb/issues/54565) @[hawkingrei](https://github.com/hawkingrei)

+ PD

    - Improve the retry logic of the HTTP client [#8142](https://github.com/tikv/pd/issues/8142) @[JmPotato](https://github.com/JmPotato)

+ TiFlash

    - Mitigate the issue that TiFlash might panic due to updating certificates after TLS is enabled [#8535](https://github.com/pingcap/tiflash/issues/8535) @[windtalker](https://github.com/windtalker)
    - Reduce lock conflicts under highly concurrent data read operations and optimize short query performance [#9125](https://github.com/pingcap/tiflash/issues/9125) @[JinheLin](https://github.com/JinheLin)

+ Tools

    + Backup & Restore (BR)

        - Support encryption of temporary files generated during log backup [#15083](https://github.com/tikv/tikv/issues/15083) @[YuJuncen](https://github.com/YuJuncen)
        - Except for the `br log restore` subcommand, all other `br log` subcommands support skipping the loading of the TiDB `domain` data structure to reduce memory consumption [#52088](https://github.com/pingcap/tidb/issues/52088) @[Leavrth](https://github.com/Leavrth)
        - Support setting Alibaba Cloud access credentials through environment variables [#45551](https://github.com/pingcap/tidb/issues/45551) @[RidRisR](https://github.com/RidRisR)
        - Support checking whether the disk space in TiKV is sufficient before TiKV downloads each SST file. If the space is insufficient, BR terminates the restore and returns an error [#17224](https://github.com/tikv/tikv/issues/17224) @[RidRisR](https://github.com/RidRisR)

    + TiCDC

        - Support sending BOOTSTRAP messages of all tables to the downstream in one go when a changefeed using Simple Protocol starts [#11315](https://github.com/pingcap/tiflow/issues/11315) @[asddongmen](https://github.com/asddongmen)
        - Support directly outputting raw events when the downstream is a Message Queue (MQ) or cloud storage [#11211](https://github.com/pingcap/tiflow/issues/11211) @[CharlesCheung96](https://github.com/CharlesCheung96)
