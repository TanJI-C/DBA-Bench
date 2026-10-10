# Resource allocation options for TiDB Cloud Dedicated

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/optimize-resource-allocation.md`
- Source Title: `Optimize Resource Allocation for TiDB Cloud Dedicated`
- Source Heading Path: `Optimize Resource Allocation for TiDB Cloud Dedicated | Optimize Resource Allocation for TiDB Cloud Dedicated > Use Resource Control | Optimize Resource Allocation for TiDB Cloud Dedicated > Use TiDB Node Group | Optimize Resource Allocation for TiDB Cloud Dedicated > Choose between Resource Control and TiDB Node Group`
- Source Line Ranges: `5-38`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`, `sql`
- Topic Tags: `resource-allocation`, `resource-control`, `node-groups`, `qos`, `resource-isolation`, `workload-isolation`, `sql-bindings`, `runaway-queries`, `endpoints`, `comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0197_cd11e4abaf`
- Source ID: `tidb-docs-8.1:tidb-cloud/optimize-resource-allocation.md#optimize-resource-allocation-for-tidb-cloud-dedicated`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fd019f7da638a4bc9fcef8e4acb85250495cf6b075b5908b89b56211a088b603`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/optimize-resource-allocation#optimize-resource-allocation-for-tidb-cloud-dedicated
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/optimize-resource-allocation.md

## Retrieval Guidance

- Use When: Use this chunk when comparing resource isolation options in TiDB Cloud Dedicated, especially Resource Control versus TiDB Node Group for mixed workloads with different QoS requirements.
- Retrieval Keywords: TiDB Cloud Dedicated, Optimize Resource Allocation, Resource Control, TiDB Node Group, QoS, resource isolation, workload isolation, mixed workloads, logical groups, physical groups, TiKV, TiFlash, TiDB layer, connection endpoints, SQL bindings, runaway queries, resource groups, user level, session level, statement level, flow control, configured using SQL statements, configured through the TiDB Cloud console
- Follow-up Guidance: The content also states that Resource Control can be combined with SQL bindings or runaway query management to temporarily limit the resource consumption of specific SQL statements.
- Classification Note: This chunk is classified under performance because it explains how Resource Control and TiDB Node Group allocate and isolate cluster resources to meet latency and QoS needs in TiDB Cloud Dedicated.

## Official Source Content

# Optimize Resource Allocation for TiDB Cloud Dedicated

As a Hybrid Transactional and Analytical Processing (HTAP) database, [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters can support multiple business applications, each with different quality of service (QoS) requirements. In some cases, you might need to allocate more resources to high-priority applications to maintain acceptable latency levels.

TiDB Cloud Dedicated offers resource optimization features, including [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) and the [TiDB Node Group](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-overview) feature. These features help you allocate resources efficiently in multi-business scenarios.
## Use Resource Control

[Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) lets you divide the storage nodes (TiKV or TiFlash) of a TiDB Cloud Dedicated cluster into multiple logical groups. In systems with mixed workloads, you can assign workloads to separate resource groups to ensure resource isolation and meet QoS requirements.

If the cluster experiences unexpected SQL performance issues, you can use [SQL bindings](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-binding) or [manage runaway queries](https://docs.pingcap.com/tidb/stable/tidb-resource-control#manage-queries-that-consume-more-resources-than-expected-runaway-queries) alongside resource groups to temporarily limit the resource consumption of specific SQL statements.

By using Resource Control effectively, you can reduce the number of clusters, simplify operations and maintenance, and lower management costs.
## Use TiDB Node Group

The [TiDB Node Group](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-overview) feature physically groups the computing nodes (TiDB layer) of a TiDB Cloud Dedicated cluster. Each group is configured with a specific number of TiDB nodes, ensuring the physical separation of computing resources between groups.

You can divide computing nodes into multiple TiDB node groups based on business requirements and assign unique connection endpoints to each group. Your applications connect to the cluster through their respective endpoints, and requests route to the corresponding node group for processing. This ensures that resource overuse in one group does not affect other groups.
## Choose between Resource Control and TiDB Node Group

You can use Resource Control, the TiDB Node Group feature, or a combination of both based on your application needs and budget to achieve resource isolation.

The following table compares the features of Resource Control and TiDB Node Group:

| Comparison item           | Resource Control         | TiDB Node Group         |
|--------------------------|---------------------------|------------------------|
| Isolation level   | TiKV or TiFlash logical layer    | TiDB node physical layer   |
| Flow control        | Controls the flow of user read and write requests based on quotas set for resource groups. | Not supported. |
| Configuration method  | Configured using SQL statements  | Configured through the TiDB Cloud console |
| Distinguishing workloads | Supports binding resources at the following levels: <ul><li>User level.</li><li>Session level (set the resource group per session). </li><li>Statement level (set the resource group per statement).</li></ul>| Provides different connection endpoints for different workloads.   |
| Cost       | No extra cost     | Cost associated with adding TiDB nodes, but no extra cost for creating TiDB node groups.       |
