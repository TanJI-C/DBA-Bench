# Reliability features: resource control, checkpointing, stats loading, TiCDC, and Lightning stability

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.0.md`
- Source Title: `TiDB 7.1.0 Release Notes`
- Source Heading Path: `TiDB 7.1.0 Release Notes > Feature details > Reliability`
- Source Line Ranges: `143-201`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `dashboard`, `br`, `ticdc`, `lightning`, `pd`
- Topic Tags: `reliability`, `resource-control`, `capacity-planning`, `checkpoint`, `fast-online-ddl`, `restore`, `statistics`, `startup`, `data-integrity`, `kafka`, `avro`, `ddl-replication`, `data-import`, `region-split`, `pd-scheduling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0444_c575a7e98a`
- Source ID: `tidb-docs-8.1:releases/release-7.1.0.md#reliability`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2208dda35138aabb0dd73a3fe0cede102792af01547171ed5f648721fb393806`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.0#reliability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.1.0 reliability release notes about Resource Control GA, Fast Online DDL checkpoints, BR checkpoint restore, statistics loading behavior, TiCDC integrity and DDL replication improvements, or TiDB Lightning stability for TiB-level imports.
- Retrieval Keywords: TiDB 7.1.0 Reliability, Resource Control GA, resource groups, Resource Manager page, estimate cluster capacity, capacity planning, Fast Online DDL checkpoint mechanism, tidb_ddl_enable_fast_reorg, BR checkpoint restore, snapshot restore, log restore, lightweight statistics initialization, lite-init-stats, force-init-stats, load statistics during startup, TiCDC data integrity validation, single-row data, Kafka downstream, Avro protocol, TiCDC optimizes DDL replication operations, downstream latency, TiDB Lightning TiB-level data, tikv-importer.region-split-batch-size, tikv-importer.region-split-concurrency, tikv-importer.region-check-backoff-limit, tikv-importer.pause-pd-scheduler-scope, PD scheduling
- Follow-up Guidance: The source points to related documentation for tidb-resource-control, dashboard Resource Manager, Fast Online DDL, BR checkpoint restore, statistics loading, TiCDC integrity check and FAQ, and TiDB Lightning configuration.
- Classification Note: This chunk is classified as a self-managed release note because it summarizes reliability features and configuration additions introduced in TiDB 7.1.0 across TiDB, Dashboard, BR, TiCDC, Lightning, and PD.

## Official Source Content

### Reliability

* Resource Control becomes generally available (GA) [#38825](https://github.com/pingcap/tidb/issues/38825) @[nolouch](https://github.com/nolouch) @[BornChanger](https://github.com/BornChanger) @[glorv](https://github.com/glorv) @[tiancaiamao](https://github.com/tiancaiamao) @[Connor1996](https://github.com/Connor1996) @[JmPotato](https://github.com/JmPotato) @[hnes](https://github.com/hnes) @[CabinfeverB](https://github.com/CabinfeverB) @[HuSharp](https://github.com/HuSharp)

    TiDB enhances the resource control feature based on resource groups, which becomes GA in v7.1.0. This feature significantly improves the resource utilization efficiency and performance of TiDB clusters. The introduction of the resource control feature is a milestone for TiDB. You can divide a distributed database cluster into multiple logical units, map different database users to corresponding resource groups, and set the quota for each resource group as needed. When the cluster resources are limited, all resources used by sessions in the same resource group are limited to the quota. In this way, even if a resource group is over-consumed, the sessions in other resource groups are not affected.

    With this feature, you can combine multiple small and medium-sized applications from different systems into a single TiDB cluster. When the workload of an application grows larger, it does not affect the normal operation of other applications. When the system workload is low, busy applications can still be allocated the required system resources even if they exceed the set quotas, which can achieve the maximum utilization of resources. In addition, the rational use of the resource control feature can reduce the number of clusters, ease the difficulty of operation and maintenance, and save management costs.

    In TiDB v7.1.0, this feature introduces the ability to estimate system capacity based on actual workload or hardware deployment. The estimation ability provides you with a more accurate reference for capacity planning and assists you in better managing TiDB resource allocation to meet the stability needs of enterprise-level scenarios.

    To improve user experience, TiDB Dashboard provides the [Resource Manager page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-resource-manager). You can view the resource group configuration on this page and estimate cluster capacity in a visual way to facilitate reasonable resource allocation.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-resource-control).

* Support the checkpoint mechanism for Fast Online DDL to improve fault tolerance and automatic recovery capability [#42164](https://github.com/pingcap/tidb/issues/42164) @[tangenta](https://github.com/tangenta)

    TiDB v7.1.0 introduces a checkpoint mechanism for [Fast Online DDL](https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction), which significantly improves the fault tolerance and automatic recovery capability of Fast Online DDL. Even if the TiDB owner node is restarted or changed due to failures, TiDB can still recover progress from checkpoints that are automatically updated on a regular basis, making the DDL execution more stable and efficient.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630).

* Backup & Restore supports checkpoint restore [#42339](https://github.com/pingcap/tidb/issues/42339) @[Leavrth](https://github.com/Leavrth)

    Snapshot restore or log restore might be interrupted due to recoverable errors, such as disk exhaustion and node crash. Before TiDB v7.1.0, the recovery progress before the interruption would be invalidated even after the error is addressed, and you need to start the restore from scratch. For large clusters, this incurs considerable extra cost.

    Starting from TiDB v7.1.0, Backup & Restore (BR) introduces the checkpoint restore feature, which enables you to continue an interrupted restore. This feature can retain most recovery progress of the interrupted restore.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/br/br-checkpoint-restore).

* Optimize the strategy of loading statistics [#42160](https://github.com/pingcap/tidb/issues/42160) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)

   TiDB v7.1.0 introduces lightweight statistics initialization as an experimental feature. Lightweight statistics initialization can significantly reduce the number of statistics that must be loaded during startup, thus improving the speed of loading statistics. This feature increases the stability of TiDB in complex runtime environments and reduces the impact on the overall service when TiDB nodes restart. You can set the parameter [`lite-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#lite-init-stats-new-in-v710) to `true` to enable this feature.

    During TiDB startup, SQL statements executed before the initial statistics are fully loaded might have suboptimal execution plans, thus causing performance issues. To avoid such issues, TiDB v7.1.0 introduces the configuration parameter [`force-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#force-init-stats-new-in-v657-and-v710). With this option, you can control whether TiDB provides services only after statistics initialization has been finished during startup. This parameter is disabled by default.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/statistics#load-statistics).

* TiCDC supports the data integrity validation feature for single-row data [#8718](https://github.com/pingcap/tiflow/issues/8718) [#42747](https://github.com/pingcap/tidb/issues/42747) @[3AceShowHand](https://github.com/3AceShowHand) @[zyguan](https://github.com/zyguan)

    Starting from v7.1.0, TiCDC introduces the data integrity validation feature, which uses a checksum algorithm to validate the integrity of single-row data. This feature helps verify whether any error occurs in the process of writing data from TiDB, replicating it through TiCDC, and then writing it to a Kafka cluster. The data integrity validation feature only supports changefeeds that use Kafka as the downstream and currently supports the Avro protocol.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-integrity-check).

* TiCDC optimizes DDL replication operations [#8686](https://github.com/pingcap/tiflow/issues/8686) @[hi-rustin](https://github.com/Rustin170506)

    Before v7.1.0, when you perform a DDL operation that affects all rows on a large table (such as adding or deleting a column), the replication latency of TiCDC would significantly increase. Starting from v7.1.0, TiCDC optimizes this replication operation and mitigates the impact of DDL operations on downstream latency.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#does-ticdc-replicate-data-changes-caused-by-lossy-ddl-operations-to-the-downstream).

* Improve the stability of TiDB Lightning when importing TiB-level data [#43510](https://github.com/pingcap/tidb/issues/43510) [#43657](https://github.com/pingcap/tidb/issues/43657) @[D3Hunter](https://github.com/D3Hunter) @[lance6716](https://github.com/lance6716)

    Starting from v7.1.0, TiDB Lightning has added four configuration items to improve stability when importing TiB-level data.
    - `tikv-importer.region-split-batch-size` controls the number of Regions when splitting Regions in a batch. The default value is `4096`.
    - `tikv-importer.region-split-concurrency` controls the concurrency when splitting Regions. The default value is the number of CPU cores.
    - `tikv-importer.region-check-backoff-limit` controls the number of retries to wait for the Region to come online after the split and scatter operations. The default value is `1800` and the maximum retry interval is two seconds. The number of retries is not increased if any Region becomes online between retries.
    - `tikv-importer.pause-pd-scheduler-scope` controls the scope in which TiDB Lightning pauses PD scheduling. Value options are `"table"` and `"global"`. The default value is `"table"`. For TiDB versions earlier than v6.1.0, you can only configure the `"global"` option, which pauses global scheduling during data import. Starting from v6.1.0, the `"table"` option is supported, which means that scheduling is only paused for the Region that stores the target table data. It is recommended to set this configuration item to `"global"` in scenarios with large data volumes to improve stability.

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).
