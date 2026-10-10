# Improvements across TiDB, TiKV, TiFlash, BR, TiCDC, and Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.1.md`
- Source Title: `TiDB 7.5.1 Release Notes`
- Source Heading Path: `TiDB 7.5.1 Release Notes > Improvements`
- Source Line Ranges: `24-77`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `br`, `ticdc`, `dashboard`, `lightning`, `pd`
- Topic Tags: `improvements`, `ddl`, `resource-control`, `observability`, `import-jobs`, `flashback-cluster`, `type-conversion`, `optimizer`, `indexing`, `slow-store-detection`, `request-unit`, `restore-performance`, `log-backup`, `changefeed-status`, `object-storage`, `import-performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0525_6fef01820e`
- Source ID: `tidb-docs-8.1:releases/release-7.5.1.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c8782d262d9258b07cef2ad2edbabc0b90b2ed0e8a366c2ed631f8b1b97c3f84`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.1#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.1.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.5.1 improvements across TiDB, TiKV, TiFlash, BR, TiCDC, and Lightning, including resource control observability, DDL and restore performance, changefeed status, and object storage replication performance.
- Retrieval Keywords: Improvements, tikv_client_read_timeout, DDL schema reload, Meta Region Leader read unavailability, resource control observability, resource groups, Slow Queries, Statement Summary Tables, tidb_last_query_info, ru_consumption, Request Unit RU, QPS TPS execution time P999 P99 P95, CANCEL IMPORT JOB synchronous, FLASHBACK CLUSTER TO TSO, type conversions, LIKE, IndexRangeScan, OUTER JOIN to INNER JOIN, multiple accelerated ADD INDEX DDL tasks, adding indexes to empty tables, slow store detection algorithm, TiFlash RU values more stable, disk performance jitter read latency, background GC tasks latency, BR merging SST files, creating databases in batch during data restore, ingesting SST files in batch, global checkpoint advancement, slowest Region, RESTORE statement, merge-schedule-limit, TiCDC logs in the TiDB Dashboard, querying the downstream synchronization status of a changefeed, specific replication task is completed, replicating data to object storage by increasing parallelism, TiDB Lightning, ALTER TABLE importing a large number of small tables
- Follow-up Guidance: The chunk includes a linked TiCDC OpenAPI v2 capability for querying whether a specific replication task is completed.
- Classification Note: This is classified as a release improvements chunk because it enumerates enhancement items for multiple components in TiDB 7.5.1 rather than a single feature guide.

## Official Source Content

## Improvements

+ TiDB

    - Use `tikv_client_read_timeout` during the DDL schema reload process to reduce the impact of Meta Region Leader read unavailability on the cluster [#48124](https://github.com/pingcap/tidb/issues/48124) @[cfzjywxk](https://github.com/cfzjywxk)
    - Enhance observability related to resource control [#49318](https://github.com/pingcap/tidb/issues/49318) @[glorv](https://github.com/glorv) @[bufferflies](https://github.com/bufferflies) @[nolouch](https://github.com/nolouch)

        As more and more users use resource groups to isolate application workloads, Resource Control provides enhanced data based on resource groups. This helps you monitor resource group workloads and settings, ensuring that you can quickly identify and accurately diagnose problems, including:

        - [Slow Queries](https://docs.pingcap.com/tidb/stable/identify-slow-queries): add the resource group name, resource unit (RU) consumption, and time for waiting for resources.
        - [Statement Summary Tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables): add the resource group name, RU consumption, and time for waiting for resources.
        - In the system variable [`tidb_last_query_info`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_last_query_info-new-in-v4014), add a new entry `ru_consumption` to indicate the consumed [RU](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru) by SQL statements. You can use this variable to get the resource consumption of the last statement in the session.
        - Add database metrics based on resource groups: QPS/TPS, execution time (P999/P99/P95), number of failures, and number of connections.

    - Modify the `CANCEL IMPORT JOB` statement to a synchronous statement [#48736](https://github.com/pingcap/tidb/issues/48736) @[D3Hunter](https://github.com/D3Hunter)
    - Support the [`FLASHBACK CLUSTER TO TSO`](https://docs.pingcap.com/tidb/v7.5/sql-statement-flashback-cluster) syntax [#48372](https://github.com/pingcap/tidb/issues/48372) @[BornChanger](https://github.com/BornChanger)
    - Optimize the TiDB implementation when handling some type conversions and fix related issues [#47945](https://github.com/pingcap/tidb/issues/47945) [#47864](https://github.com/pingcap/tidb/issues/47864) [#47829](https://github.com/pingcap/tidb/issues/47829) [#47816](https://github.com/pingcap/tidb/issues/47816) @[YangKeao](https://github.com/YangKeao) @[lcwangchao](https://github.com/lcwangchao)
    - When a non-binary collation is set and the query includes `LIKE`, the optimizer generates an `IndexRangeScan` to improve the execution efficiency [#48181](https://github.com/pingcap/tidb/issues/48181) [#49138](https://github.com/pingcap/tidb/issues/49138) @[time-and-fate](https://github.com/time-and-fate)
    - Enhance the ability to convert `OUTER JOIN` to `INNER JOIN` in specific scenarios [#49616](https://github.com/pingcap/tidb/issues/49616) @[qw4990](https://github.com/qw4990)
    - Support multiple accelerated `ADD INDEX` DDL tasks to be queued for execution, instead of falling back to normal `ADD INDEX` tasks [#47758](https://github.com/pingcap/tidb/issues/47758) @[tangenta](https://github.com/tangenta)
    - Improve the speed of adding indexes to empty tables [#49682](https://github.com/pingcap/tidb/issues/49682) @[zimulala](https://github.com/zimulala)

+ TiKV

    - Enhance the slow store detection algorithm by improving its sensitivity and reducing the false-positive rate, especially in intensive read and write load scenarios [#15909](https://github.com/tikv/tikv/issues/15909) @[LykxSassinator](https://github.com/LykxSassinator)

+ TiFlash

    - Improve the calculation method for [Request Unit (RU)](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru) to make RU values more stable [#8391](https://github.com/pingcap/tiflash/issues/8391) @[guo-shaoge](https://github.com/guo-shaoge)
    - Reduce the impact of disk performance jitter on read latency [#8583](https://github.com/pingcap/tiflash/issues/8583) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Reduce the impact of background GC tasks on read and write task latency [#8650](https://github.com/pingcap/tiflash/issues/8650) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - Improve the speed of merging SST files during data restore by using a more efficient algorithm [#50613](https://github.com/pingcap/tidb/issues/50613) @[Leavrth](https://github.com/Leavrth)
        - Support creating databases in batch during data restore [#50767](https://github.com/pingcap/tidb/issues/50767) @[Leavrth](https://github.com/Leavrth)
        - Support ingesting SST files in batch during data restore [#16267](https://github.com/tikv/tikv/issues/16267) @[3pointer](https://github.com/3pointer)
        - Print the information of the slowest Region that affects global checkpoint advancement in logs and metrics during log backups [#51046](https://github.com/pingcap/tidb/issues/51046) @[YuJuncen](https://github.com/YuJuncen)
        - Improve the table creation performance of the `RESTORE` statement in scenarios with large datasets [#48301](https://github.com/pingcap/tidb/issues/48301) @[Leavrth](https://github.com/Leavrth)
        - BR can pause Region merging by setting the `merge-schedule-limit` configuration to `0` [#7148](https://github.com/tikv/pd/issues/7148) @[BornChanger](https://github.com/3pointer)
        - Refactor the BR exception handling mechanism to increase tolerance for unknown errors [#47656](https://github.com/pingcap/tidb/issues/47656) @[3pointer](https://github.com/3pointer)

    + TiCDC

        - Support searching TiCDC logs in the TiDB Dashboard [#10263](https://github.com/pingcap/tiflow/issues/10263) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Support [querying the downstream synchronization status of a changefeed](https://docs.pingcap.com/tidb/v7.5/ticdc-open-api-v2#query-whether-a-specific-replication-task-is-completed), which helps you determine whether the upstream data changes received by TiCDC have been synchronized to the downstream system completely [#10289](https://github.com/pingcap/tiflow/issues/10289) @[hongyunyan](https://github.com/hongyunyan)
        - Improve the performance of TiCDC replicating data to object storage by increasing parallelism [#10098](https://github.com/pingcap/tiflow/issues/10098) @[CharlesCheung96](https://github.com/CharlesCheung96)

    + TiDB Lightning

        - Improve the performance of `ALTER TABLE` when importing a large number of small tables [#50105](https://github.com/pingcap/tidb/issues/50105) @[D3Hunter](https://github.com/D3Hunter)
