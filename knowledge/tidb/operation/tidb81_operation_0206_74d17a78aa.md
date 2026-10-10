# Reliability and resource control

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Feature details > Reliability`
- Source Line Ranges: `122-159`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `resource control`, `resource groups`, `resource quotas`, `bindings`, `optimizer hints`, `ddl resource management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0206_74d17a78aa`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#reliability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bccbdd93550cff9c75d746d88339dd0a13f5de7ec19c51650bb76b7d8f0dd7ef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#reliability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.6.0 reliability and operation features involving resource control with resource groups, historical execution plan bindings, LIMIT-related optimizer hints, or DDL resource management.
- Retrieval Keywords: resource control, resource groups, tidb_enable_resource_control, resource-control.enabled, Request Unit, RU, bind different database users to corresponding resource groups, Grafana dashboards, CREATE GLOBAL BINDING, CREATE SESSION BINDING, historical execution plan, SQL binding, ORDER_INDEX(), NO_ORDER_INDEX(), LIMIT operations, resource usage of DDL operations, DDL distributed parallel execution framework, tidb_ddl_distribute_reorg
- Follow-up Guidance: The content states that resource control in v6.6 requires both tidb_enable_resource_control and resource-control.enabled, and that DDL resource management is effective only after tidb_ddl_distribute_reorg is enabled.
- Classification Note: This is classified as operation because the official content focuses on reliability-oriented controls for cluster resource allocation, plan stability, optimizer intervention, and managing the impact of DDL on online applications.

## Official Source Content

### Reliability

* Support resource control based on resource groups (experimental) [#38825](https://github.com/pingcap/tidb/issues/38825) @[nolouch](https://github.com/nolouch) @[BornChanger](https://github.com/BornChanger) @[glorv](https://github.com/glorv) @[tiancaiamao](https://github.com/tiancaiamao) @[Connor1996](https://github.com/Connor1996) @[JmPotato](https://github.com/JmPotato) @[hnes](https://github.com/hnes) @[CabinfeverB](https://github.com/CabinfeverB) @[HuSharp](https://github.com/HuSharp)

    Now you can create resource groups for a TiDB cluster, bind different database users to corresponding resource groups, and set quotas for each resource group according to actual needs. When the cluster resources are limited, all resources used by sessions in the same resource group will be limited to the quota. In this way, even if a resource group is over-consumed, the sessions in other resource groups are not affected. TiDB provides a built-in view of the actual usage of resources on Grafana dashboards, assisting you to allocate resources more rationally.

    The introduction of the resource control feature is a milestone for TiDB. It can divide a distributed database cluster into multiple logical units. Even if an individual unit overuses resources, it does not crowd out the resources needed by other units.

    With this feature, you can:

    - Combine multiple small and medium-sized applications from different systems into a single TiDB cluster. When the workload of an application grows larger, it does not affect the normal operation of other applications. When the system workload is low, busy applications can still be allocated the required system resources even if they exceed the set read and write quotas, so as to achieve the maximum utilization of resources.
    - Choose to combine all test environments into a single TiDB cluster, or group the batch tasks that consume more resources into a single resource group. It can improve hardware utilization and reduce operating costs while ensuring that critical applications can always get the necessary resources.

  In addition, the rational use of the resource control feature can reduce the number of clusters, ease the difficulty of operation and maintenance, and save management costs.

  In v6.6, you need to enable both TiDB's global variable [`tidb_enable_resource_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_resource_control-new-in-v660) and the TiKV configuration item [`resource-control.enabled`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#resource-control) to enable resource control. Currently, the supported quota method is based on "[Request Unit (RU)](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru)". RU is TiDB's unified abstraction unit for system resources such as CPU and IO.

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-resource-control).

* Binding historical execution plans is GA [#39199](https://github.com/pingcap/tidb/issues/39199) @[fzzf678](https://github.com/fzzf678)

    In v6.5.0, TiDB extends the binding targets in the [`CREATE [GLOBAL | SESSION] BINDING`](/sql-statements/sql-statement-create-binding.md) statements and supports creating bindings according to historical execution plans. In v6.6.0, this feature is GA. The selection of execution plans is not limited to the current TiDB node. Any historical execution plan generated by any TiDB node can be selected as the target of [SQL binding](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-binding), which further improves the feature usability.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-plan-management#create-a-binding-according-to-a-historical-execution-plan).

* Add several optimizer hints [#39964](https://github.com/pingcap/tidb/issues/39964) @[Reminiscent](https://github.com/Reminiscent)

    TiDB adds several optimizer hints in v6.6.0 to control the execution plan selection of `LIMIT` operations.

    - [`ORDER_INDEX()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#order_indext1_name-idx1_name--idx2_name-): tells the optimizer to use the specified index, to keep the order of the index when reading data, and generates plans similar to `Limit + IndexScan(keep order: true)`.
    - [`NO_ORDER_INDEX()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_order_indext1_name-idx1_name--idx2_name-): tells the optimizer to use the specified index, not to keep the order of the index when reading data, and generates plans similar to `TopN + IndexScan(keep order: false)`.

  Continuously introducing optimizer hints provides users with more intervention methods, helps solve SQL performance issues, and improves the stability of overall performance.

* Support dynamically managing the resource usage of DDL operations (experimental) [#38025](https://github.com/pingcap/tidb/issues/38025) @[hawkingrei](https://github.com/hawkingrei)

    TiDB v6.6.0 introduces resource management for DDL operations to reduce the impact of DDL changes on online applications by automatically controlling the CPU usage of these operations. This feature is effective only after the [DDL distributed parallel execution framework](https://docs.pingcap.com/tidb/v6.6/system-variables#tidb_ddl_distribute_reorg-new-in-v660) is enabled.
