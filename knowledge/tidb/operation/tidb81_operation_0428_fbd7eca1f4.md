# TiDB node groups overview, prerequisites, and creation

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-node-group-management.md`
- Source Title: `Manage TiDB Node Groups`
- Source Heading Path: `Manage TiDB Node Groups | Manage TiDB Node Groups > Terms | Manage TiDB Node Groups > Prerequisites | Manage TiDB Node Groups > Create a TiDB node group`
- Source Line Ranges: `5-60`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `node-groups`, `prerequisites`, `creation`, `endpoints`, `billing`, `resource-isolation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0428_fbd7eca1f4`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-node-group-management.md#manage-tidb-node-groups`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d868ea68f03fdec2da2518508b7826a6c7690c5d34a32def0c39b7f432c4f289`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-management#manage-tidb-node-groups
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-node-group-management.md

## Retrieval Guidance

- Use When: Use this when someone needs the overview, prerequisites, limits, or creation flow for TiDB node groups in TiDB Cloud Dedicated.
- Retrieval Keywords: Manage TiDB Node Groups, TiDB Node Group, Default Group, TiDB Cloud Dedicated, AWS, Google Cloud, Organization Owner, Project Owner, Available state, Modify Cluster, Nodes, DefaultGroup, 8 vCPU and 16 GiB memory, up to five TiDB node groups, billing, resource isolation, endpoints
- Follow-up Guidance: The content also notes that after creating a new TiDB node group, you need a new connection to the TiDB nodes in that group and refers to Connect to a TiDB node group.
- Classification Note: This is classified as an operation chunk because the official content defines TiDB node groups, lists prerequisites, and provides the console procedure for creating a node group.

## Official Source Content

# Manage TiDB Node Groups

This document describes how to manage TiDB node groups and their endpoints to isolate your business workload using the [TiDB Cloud console](https://tidbcloud.com/).

> **Note**:
>
> The TiDB Node Group feature is **NOT** available for TiDB Cloud Serverless clusters.
## Terms

- TiDB Node Group: A TiDB node group manages the grouping of TiDB nodes and maintains the mapping between endpoints and TiDB nodes.

    - Each TiDB node group has a unique endpoint. 
    - When you delete a TiDB node group, the related network setting (such as private link and IP access list) will be deleted too. 

- Default Group: When a cluster is created, a default TiDB node group is created. Therefore, each cluster has a default group. The default group cannot be deleted. 
## Prerequisites

- You have a [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster deployed on AWS or Google Cloud.
- You are in the **Organization Owner** or **Project Owner** role of your organization. For more information, see [User roles](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#user-roles).

> **Note**:
>
> The TiDB node groups cannot be created during cluster creation. You need to add the groups after the cluster is created and in the **Available** state. 
## Create a TiDB node group

To create a TiDB node group, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com/), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, and then click the name of your target cluster to go to its overview page.
2. In the left navigation pane, click **Nodes**.
3. Click **Modify** in the upper-right corner. The **Modify Cluster** page is displayed.
4. On the **Modify Cluster** page, click **+** to add a new TiDB node group as follows. You can also use the default group directly.

    - TiDB
        - **vCPU + RAM**: choose the [TiDB size](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#size-tidb) you need. Only TiDB nodes with 8 vCPU and 16 GiB memory or higher specifications are supported.
        - **Node Groups**: click **+** to create a new TiDB node group. You can also use the default group and enter the number of TiDB nodes in the **DefaultGroup** field.
    
    - TiKV
        - **vCPU + RAM**: choose the [TiKV size](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#size-tikv) you need.
        - **Storage x Nodes**: choose the storage size and the number of TiKV nodes.
    
    - TiFlash (optional)
        - **vCPU + RAM**: choose the [TiFlash size](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#size-tiflash) you need.
        - **Storage x Nodes**: choose the storage size and the number of TiFlash nodes.

    ![Create TiDB Node Group](/media/tidb-cloud/tidb-node-group-create.png)

5. New TiDB nodes are added along with the new TiDB node group, which affects the cluster's billing. Review the cluster size in the right pane, then click **Confirm**.

By default, you can create up to five TiDB node groups for a TiDB Cloud Dedicated cluster. If you need more groups, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support). 

If you create a TiDB node group but still use the endpoint of the default group to connect to the cluster, the TiDB nodes in the TiDB node group will not take any workload, which is a waste of the resource. You need to create new connection to the TiDB nodes in the new TiDB node group. See [Connect to a TiDB node group](#connect-to-a-tidb-node-group).
