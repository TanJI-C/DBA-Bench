# Improvements across TiDB, TiKV, PD, TiFlash, BR, TiCDC, and Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.4.md`
- Source Title: `TiDB 7.1.4 Release Notes`
- Source Heading Path: `TiDB 7.1.4 Release Notes > Improvements`
- Source Line Ranges: `19-60`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dashboard`, `lightning`
- Topic Tags: `release-notes`, `improvements`, `query-optimization`, `startup`, `statistics`, `monitoring`, `sst`, `cluster-status`, `gc`, `latency`, `restore`, `backup`, `checkpoint`, `kafka`, `changefeed`, `dashboard`, `import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0470_78dbb01fc8`
- Source ID: `tidb-docs-8.1:releases/release-7.1.4.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8bbfc91e38d4c33e61f8de3595157a83e108fc93e5897828c8f7fd880a0a6d03`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.4#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.4.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.1.4 improvements across TiDB, TiKV, PD, TiFlash, BR, TiCDC, Dashboard, and TiDB Lightning.
- Retrieval Keywords: TiDB 7.1.4 Improvements, OUTER JOIN to INNER JOIN, force-init-stats true, startup HTTP servers monitoring, corrupted SST files specific reasons, PD automatically updating cluster status backup cluster disconnected, TiFlash background GC tasks latency, disk performance jitter read latency, BR RESTORE batch create databases, RESTORE statement table creation performance, merging SST files during data restore, ingesting SST files in batch, slowest Region global checkpoint advancement, log backups logs and metrics, Google Cloud Storage GCS external storage compatibility check, br log truncate lock mechanism, TiCDC Kafka topic expression schema optional, query downstream synchronization status of a changefeed, searching TiCDC logs in the TiDB Dashboard, TiDB Lightning multiple tables imported ALTER TABLE lock operation
- Follow-up Guidance: The official content includes a link for querying the downstream synchronization status of a changefeed in TiCDC OpenAPI v2.
- Classification Note: This is an improvements section because the official content lists enhancement items for multiple components and tools in TiDB 7.1.4.

## Official Source Content

## Improvements

+ TiDB

    - Enhance the ability to convert `OUTER JOIN` to `INNER JOIN` in specific scenarios [#49616](https://github.com/pingcap/tidb/issues/49616) @[qw4990](https://github.com/qw4990)
    - When `force-init-stats` is set to `true`, TiDB waits for statistics initialization to finish before providing services during TiDB startup. This setting no longer blocks the startup of HTTP servers, which enables users to continue monitoring [#50854](https://github.com/pingcap/tidb/issues/50854) @[hawkingrei](https://github.com/hawkingrei)

+ TiKV

    - When TiKV detects the existence of corrupted SST files, it logs the specific reasons for the corruption [#16308](https://github.com/tikv/tikv/issues/16308) @[overvenus](https://github.com/overvenus)

+ PD

    - Improve the speed of PD automatically updating cluster status when the backup cluster is disconnected [#6883](https://github.com/tikv/pd/issues/6883) @[disksing](https://github.com/disksing)

+ TiFlash

    - Reduce the impact of background GC tasks on read and write task latency [#8650](https://github.com/pingcap/tiflash/issues/8650) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Reduce the impact of disk performance jitter on read latency [#8583](https://github.com/pingcap/tiflash/issues/8583) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - Support creating databases in batch during data restore [#50767](https://github.com/pingcap/tidb/issues/50767) @[Leavrth](https://github.com/Leavrth)
        - Improve the table creation performance of the `RESTORE` statement in scenarios with large datasets [#48301](https://github.com/pingcap/tidb/issues/48301) @[Leavrth](https://github.com/Leavrth)
        - Improve the speed of merging SST files during data restore by using a more efficient algorithm [#50613](https://github.com/pingcap/tidb/issues/50613) @[Leavrth](https://github.com/Leavrth)
        - Support ingesting SST files in batch during data restore [#16267](https://github.com/tikv/tikv/issues/16267) @[3pointer](https://github.com/3pointer)
        - Print the information of the slowest Region that affects global checkpoint advancement in logs and metrics during log backups [#51046](https://github.com/pingcap/tidb/issues/51046) @[YuJuncen](https://github.com/YuJuncen)
        - Remove an outdated compatibility check when using Google Cloud Storage (GCS) as the external storage [#50533](https://github.com/pingcap/tidb/issues/50533) @[lance6716](https://github.com/lance6716)
        - Implement a lock mechanism to avoid executing multiple log backup truncation tasks (`br log truncate`) simultaneously [#49414](https://github.com/pingcap/tidb/issues/49414) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC

        - When the downstream is Kafka, the topic expression allows `schema` to be optional and supports specifying a topic name directly [#9763](https://github.com/pingcap/tiflow/issues/9763) @[3AceShowHand](https://github.com/3AceShowHand)
        - Support [querying the downstream synchronization status of a changefeed](https://docs.pingcap.com/tidb/v7.1/ticdc-open-api-v2#query-whether-a-specific-replication-task-is-completed), which helps you determine whether the upstream data changes received by TiCDC have been synchronized to the downstream system completely [#10289](https://github.com/pingcap/tiflow/issues/10289) @[hongyunyan](https://github.com/hongyunyan)
        - Support searching TiCDC logs in the TiDB Dashboard [#10263](https://github.com/pingcap/tiflow/issues/10263) @[CharlesCheung96](https://github.com/CharlesCheung96)

    + TiDB Lightning

        - Improve the performance in scenarios where multiple tables are imported by removing the lock operation when executing `ALTER TABLE` [#50105](https://github.com/pingcap/tidb/issues/50105) @[D3Hunter](https://github.com/D3Hunter)
