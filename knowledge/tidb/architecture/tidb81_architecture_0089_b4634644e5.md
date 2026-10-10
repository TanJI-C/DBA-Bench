# TiDB Node Group overview, implementation, scenarios, limits, and SLA impact

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-node-group-overview.md`
- Source Title: `Overview of TiDB Node Group`
- Source Heading Path: `Overview of TiDB Node Group | Overview of TiDB Node Group > Implementation | Overview of TiDB Node Group > Scenarios | Overview of TiDB Node Group > Limitations and quotas | Overview of TiDB Node Group > SLA impact`
- Source Line Ranges: `5-61`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `node-groups`, `resource-isolation`, `load-balancing`, `endpoints`, `multi-tenant`, `scaling`, `quotas`, `limitations`, `sla`, `high-availability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0089_b4634644e5`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-node-group-overview.md#overview-of-tidb-node-group`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8e616ed9936f28c5b9784239022f03393bb745d827a061077f537485c7cff1d1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-overview#overview-of-tidb-node-group
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-node-group-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about what TiDB Node Group is in TiDB Cloud Dedicated, how endpoints and load balancers map requests to isolated TiDB computing node groups, what scenarios it supports, and what limits or SLA effects apply.
- Retrieval Keywords: TiDB Node Group, TiDB Cloud Dedicated, TiDB Cloud Serverless not available, computing nodes TiDB layer, physical isolation of computing resources, unique connection endpoints, dedicated load balancer, endpoint to TiDB nodes mapping, public connection, private endpoint, VPC peering, resource isolation, multi-business scenarios, import or DDL tasks, ADD INDEX tasks cannot be isolated, automatic statistics collection tasks on the TiDB owner node, up to five TiDB node groups, total number of TiDB nodes must not exceed 150, 4 vCPUs and 16 GiB of memory do not support, AWS or Google Cloud, Monthly Uptime Percentage, 99.99%, 99.9%, high availability
- Follow-up Guidance: The source also states that for high availability, each TiDB node group should be configured with at least two TiDB nodes.
- Classification Note: This chunk is classified as architecture because it describes the TiDB Node Group design, request routing through dedicated load balancers and endpoints, supported usage scenarios, platform limits, and SLA impact in TiDB Cloud.

## Official Source Content

# Overview of TiDB Node Group

You can create TiDB node groups for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters. A TiDB node group physically groups the computing nodes (TiDB layer) of a cluster, with each group containing a specific number of TiDB nodes. This configuration provides physical isolation of computing resources between groups, enabling efficient resource allocation in multi-business scenarios.

With TiDB node groups, you can divide computing nodes into multiple TiDB node groups based on business requirements and configure unique connection endpoints for each TiDB node group. Your applications connect to the cluster through their respective endpoints, and requests route to the corresponding node group for processing. This ensures that resource overuse in one group does not affect other groups.

> **Note**:
>
> The TiDB Node Group feature is **NOT** available for TiDB Cloud Serverless clusters.
## Implementation

TiDB node groups manage the grouping of TiDB nodes and maintain the mapping between endpoints and their corresponding TiDB nodes.

Each TiDB node group is associated with a dedicated load balancer. When a user sends a SQL request to the endpoint of a TiDB node group, the request first passes through that group's load balancer, which then routes it exclusively to TiDB nodes within the group.

The following diagram illustrates the implementation of the TiDB Node Group feature.

![The implementation of the TiDB Node Group feature](/media/tidb-cloud/implementation-of-tidb-node-group.png)

All nodes in a TiDB node group respond to requests from the corresponding endpoint. You can perform the following tasks:

- Create a TiDB node group and assign TiDB nodes to it.
- Set up connection endpoints for each group. Supported connection types include [public connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-management#connect-via-public-connection), [private endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-management#connect-via-private-endpoint), and [VPC peering](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-management#connect-via-vpc-peering).
- Route applications to specific groups using distinct endpoints to achieve resource isolation.
## Scenarios

The TiDB Node Group feature significantly enhances resource allocation for TiDB Cloud Dedicated clusters. TiDB nodes are dedicated to computation and do not store data. By organizing nodes into multiple physical groups, the feature ensures that resource overuse in one group does not impact other groups.

With this feature, you can:

- Consolidate multiple applications from different systems into a single TiDB Cloud Dedicated cluster. As an application's workload grows, it will not affect the normal operation of other applications. The TiDB Node Group feature ensures that the response time of transactional applications is not impacted by data analysis or batch applications.

- Perform import or DDL tasks on the TiDB Cloud Dedicated cluster without affecting the performance of existing production workloads. You can create a separate TiDB node group for importing or DDL tasks. Even though these tasks consume significant CPU or memory resources, they only use the resources in their own TiDB node group, ensuring the workloads in other TiDB node groups are not impacted. 

- Combine all test environments into a single TiDB cluster or group resource-intensive batch tasks into a dedicated TiDB node group. This approach improves hardware utilization, reduces operating costs, and ensures that critical applications always have access to necessary resources.

In addition, TiDB node groups are easy to scale in or out. For key applications with high performance requirements, you can allocate TiDB nodes to the group as needed. For less demanding applications, you can start with a small number of TiDB nodes and scale out as needed. Efficient use of the TiDB Node Group feature reduces the number of clusters, simplifies operations and maintenance, and lowers management costs.
## Limitations and quotas

Currently, the TiDB Node Group feature is free of charge. The following are limitations and quotas:

- You can only create TiDB node groups for TiDB Cloud Dedicated clusters on AWS or Google Cloud. Support for other cloud providers is planned for the near future.
- TiDB clusters with 4 vCPUs and 16 GiB of memory do not support the TiDB Node Group feature.
- By default, you can create up to five TiDB node groups for a TiDB Cloud Dedicated cluster. If you need more groups, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support). 
- Each TiDB node group must contain at least one TiDB node. While there is no limit to the number of nodes in a group, the total number of TiDB nodes in a TiDB Cloud Dedicated cluster must not exceed 150.
- TiDB Cloud runs automatic statistics collection tasks on the TiDB owner node, regardless of node group boundaries. These tasks cannot be isolated within individual TiDB node groups.
- For TiDB clusters of versions earlier than v8.1.2, `ADD INDEX` tasks cannot be isolated within individual TiDB node groups. 
## SLA impact

According to TiDB Cloud [Service Level Agreement (SLA)](https://www.pingcap.com/legal/service-level-agreement-for-tidb-cloud-services/), the Monthly Uptime Percentage of TiDB Cloud Dedicated clusters with multiple TiDB nodes deployment can reach up to 99.99%. However, after introducing TiDB Node Group, if you create multiple TiDB Node Groups with only 1 TiDB node in each group, you will lose the high availability for the groups and your cluster's monthly uptime percentage will downgrade to a single TiDB node deployment model (namely, up to 99.9%).  

For high availability, it is recommended that you configure at least two TiDB nodes for each TiDB node group.
