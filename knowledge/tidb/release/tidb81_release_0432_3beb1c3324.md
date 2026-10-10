# Reliability features: resource control, Fast Online DDL checkpoints, TiFlash spill, statistics, and optimizer hints

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.0.0.md`
- Source Title: `TiDB 7.0.0 Release Notes`
- Source Heading Path: `TiDB 7.0.0 Release Notes > Feature details > Reliability`
- Source Line Ranges: `147-205`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `tiflash`, `sql`
- Topic Tags: `release-notes`, `reliability`, `resource-control`, `fast-online-ddl`, `checkpoints`, `spill-to-disk`, `statistics`, `optimizer-hints`, `mpp`, `join-order`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0432_3beb1c3324`
- Source ID: `tidb-docs-8.1:releases/release-7.0.0.md#reliability`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ba9c0c0fda24bb58871beb1d7ab5450f71d4c8a181ceb4b6bc011eaf39491854`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.0.0#reliability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 7.0.0 reliability release notes about resource control, Fast Online DDL checkpoints, TiFlash spill to disk, statistics collection improvements, or optimizer hint changes for MPP and join planning.
- Retrieval Keywords: TiDB 7.0.0 Reliability, resource control, resource groups, PRIORITY, CREATE USER, ALTER USER, SET RESOURCE GROUP, RESOURCE_GROUP(), Resource Control Dashboard, Grafana, Fast Online DDL, checkpoint mechanism, TiDB DDL Owner, tidb_ddl_enable_fast_reorg, TiFlash spilling to disk, tidb_max_bytes_before_tiflash_external_group_by, tidb_max_bytes_before_tiflash_external_sort, tidb_max_bytes_before_tiflash_external_join, collecting statistics, optimizer hints, MPP optimization, SHUFFLE_JOIN(), BROADCAST_JOIN(), MPP_1PHASE_AGG(), MPP_2PHASE_AGG(), LEADING(), join methods, join orders, tidb_opt_advanced_join_hint
- Follow-up Guidance: The content points to documentation for tidb-resource-control, ddl-introduction, tiflash-spill-disk, and optimizer-hints for more information.
- Classification Note: This is a release-notes reliability section describing TiDB 7.0.0 enhancements in resource governance, DDL fault tolerance, TiFlash memory handling, statistics collection efficiency, and optimizer hint behavior.

## Official Source Content

### Reliability

* Enhance the resource control feature (experimental) [#38825](https://github.com/pingcap/tidb/issues/38825) @[nolouch](https://github.com/nolouch) @[BornChanger](https://github.com/BornChanger) @[glorv](https://github.com/glorv) @[tiancaiamao](https://github.com/tiancaiamao) @[Connor1996](https://github.com/Connor1996) @[JmPotato](https://github.com/JmPotato) @[hnes](https://github.com/hnes) @[CabinfeverB](https://github.com/CabinfeverB) @[HuSharp](https://github.com/HuSharp)

    TiDB enhances the resource control feature based on resource groups. This feature significantly improves the resource utilization efficiency and performance of TiDB clusters. The introduction of the resource control feature is a milestone for TiDB. You can divide a distributed database cluster into multiple logical units, map different database users to corresponding resource groups, and set the quota for each resource group as needed. When the cluster resources are limited, all resources used by sessions in the same resource group are limited to the quota. In this way, even if a resource group is over-consumed, the sessions in other resource groups are not affected.

    With this feature, you can combine multiple small and medium-sized applications from different systems into a single TiDB cluster. When the workload of an application grows larger, it does not affect the normal operation of other applications. When the system workload is low, busy applications can still be allocated the required system resources even if they exceed the set quotas, so as to achieve the maximum utilization of resources. In addition, the rational use of the resource control feature can reduce the number of clusters, ease the difficulty of operation and maintenance, and save management costs.

    This feature provides a built-in Resource Control Dashboard for the actual usage of resources in Grafana, assisting you to allocate resources more rationally. It also supports dynamic resource management capabilities based on both session and statement levels (Hint). The introduction of this feature will help you gain more precise control over the resource usage of your TiDB cluster, and dynamically adjust quotas based on actual needs.

    In TiDB v7.0.0, you can set the absolute scheduling priority (`PRIORITY`) for resource groups to guarantee that important services can get resources. It also extends the way to set resource groups.

    You can use resource groups in the following ways:

    - User level. Bind a user using the [`CREATE USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user) or [`ALTER USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-user) statements to a specific resource group. After binding a resource group to a user, sessions newly created by the user are automatically bound to the corresponding resource group.
    - Session level. Set the resource group used by the current session via [`SET RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-resource-group).
    - Statement level. Set the resource group used by the current statement via [`RESOURCE_GROUP()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#resource_groupresource_group_name).

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-resource-control).

* Support a checkpoint mechanism for Fast Online DDL, improving fault tolerance and automatic recovery capability [#42164](https://github.com/pingcap/tidb/issues/42164) @[tangenta](https://github.com/tangenta)

    TiDB v7.0.0 introduces a checkpoint mechanism for [Fast Online DDL](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630), which significantly improves its fault tolerance and automatic recovery capabilities. By periodically recording and synchronizing the DDL progress, ongoing DDL operations can continue to be executed in Fast Online DDL mode even if there is a TiDB DDL Owner failure or switch. This makes the execution of DDL more stable and efficient.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction).

* TiFlash supports spilling to disk [#6528](https://github.com/pingcap/tiflash/issues/6528) @[windtalker](https://github.com/windtalker)

    To improve execution performance, TiFlash runs data entirely in memory as much as possible. When the amount of data exceeds the total size of memory, TiFlash terminates the query to avoid system crashes caused by running out of memory. Therefore, the amount of data that TiFlash can handle is limited by the available memory.

    Starting from v7.0.0, TiFlash supports spilling to disk. By adjusting the threshold of memory usage for operators ([`tidb_max_bytes_before_tiflash_external_group_by`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_bytes_before_tiflash_external_group_by-new-in-v700), [`tidb_max_bytes_before_tiflash_external_sort`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_bytes_before_tiflash_external_sort-new-in-v700), and [`tidb_max_bytes_before_tiflash_external_join`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_bytes_before_tiflash_external_join-new-in-v700)), you can control the maximum amount of memory that an operator can use. When the memory used by the operator exceeds the threshold, it automatically writes data to disk. This sacrifices some performance but allows for processing of more data.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-spill-disk).

* Improve the efficiency of collecting statistics [#41930](https://github.com/pingcap/tidb/issues/41930) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)

    In v7.0.0, TiDB further optimizes the logic of collecting statistics, reducing the collection time by about 25%. This optimization improves the operational efficiency and stability of large database clusters, reducing the impact of statistics collection on cluster performance.

* Add new optimizer hints for MPP optimization [#39710](https://github.com/pingcap/tidb/issues/39710) @[Reminiscent](https://github.com/Reminiscent)

    In v7.0.0, TiDB adds a series of optimizer hints to influence the generation of MPP execution plans.

    - [`SHUFFLE_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#shuffle_joint1_name--tl_name-): takes effect on MPP. It hints the optimizer to use the Shuffle Join algorithm for the specified table.
    - [`BROADCAST_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#broadcast_joint1_name--tl_name-): takes effect on MPP. It hints the optimizer to use the Broadcast Join algorithm for the specified table.
    - [`MPP_1PHASE_AGG()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#mpp_1phase_agg): takes effect on MPP. It hints the optimizer to use the one-phase aggregation algorithm for all aggregate functions in the specified query block.
    - [`MPP_2PHASE_AGG()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#mpp_2phase_agg): takes effect on MPP. It hints the optimizer to use the two-phase aggregation algorithm for all aggregate functions in the specified query block.

  MPP optimizer hints can help you intervene in HTAP queries, improving performance and stability for HTAP workloads.

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/optimizer-hints).

* Optimizer hints support specifying join methods and join orders [#36600](https://github.com/pingcap/tidb/issues/36600) @[Reminiscent](https://github.com/Reminiscent)
    In v7.0.0, the optimizer hint [`LEADING()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#leadingt1_name--tl_name-) can be used in conjunction with hints that affect the join method, and their behaviors are compatible. In the case of multi-table joins, you can effectively specify the optimal join method and join order, thereby enhancing the control of optimizer hints over execution plans.

    The new hint behavior has minor changes. To ensure forward compatibility, TiDB introduces the system variable [`tidb_opt_advanced_join_hint`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_advanced_join_hint-new-in-v700). When this variable is set to `OFF`, the optimizer hint behavior is compatible with earlier versions. When you upgrade your cluster from earlier versions to v7.0.0 or later versions, this variable will be set to `OFF`. To obtain more flexible hint behavior, after you confirm that the behavior does not cause a performance regression, it is strongly recommended to set this variable to `ON`.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/optimizer-hints).
