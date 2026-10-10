# Scale TiDB Cloud cluster resources

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/scale-tidb-cluster.md`
- Source Title: `Scale Your TiDB Cluster`
- Source Heading Path: `Scale Your TiDB Cluster | Scale Your TiDB Cluster > Change node number | Scale Your TiDB Cluster > Change vCPU and RAM | Scale Your TiDB Cluster > Change storage`
- Source Line Ranges: `5-102`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `scaling`, `node-count`, `vcpu`, `memory`, `storage`, `cluster-modification`, `api`, `console`, `restrictions`, `cooldown`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0356_adadfeb9d1`
- Source ID: `tidb-docs-8.1:tidb-cloud/scale-tidb-cluster.md#scale-your-tidb-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `df1ac03d7962747b767487f15b467b391c2dfdd1e4844550acc7a993a97cfe7b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/scale-tidb-cluster#scale-your-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/scale-tidb-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to scale a TiDB Cloud cluster in the console or API, including changing node number, vCPU and RAM, or storage, and wants to know the stated restrictions or cooldown periods.
- Retrieval Keywords: Scale Your TiDB Cluster, Change node number, Change vCPU and RAM, Change storage, TiDB Cloud Serverless scales automatically, cannot manually scale a TiDB Cloud Serverless cluster, MODIFYING status, Modify Cluster, Clusters page, TiDB Cloud API, Modify a TiDB Cloud Dedicated cluster, UpdateCluster, node number of TiDB TiKV and TiFlash, vCPU and RAM of TiDB TiKV and TiFlash, storage of TiKV and TiFlash, 4 vCPU 16 GiB restrictions, TiFlash is unavailable, AWS cooldown period, six hours, in-place storage capacity downgrade
- Follow-up Guidance: The source also points to Determine Your TiDB Size and the TiDB Cloud API Documentation for sizing details and the UpdateCluster endpoint.
- Classification Note: This is an operation chunk because the official content describes how to modify TiDB Cloud cluster resources and lists the platform-specific restrictions and cooldown conditions for scaling.

## Official Source Content

# Scale Your TiDB Cluster

> **Note:**
>
> - [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) scales automatically based on your application's workload changes. However, you cannot manually scale a TiDB Cloud Serverless cluster.
> - When a cluster is in the **MODIFYING** status, you cannot perform any new scaling operations on it.

You can scale a TiDB cluster in the following dimensions:

- Node number of TiDB, TiKV, and TiFlash
- vCPU and RAM of TiDB, TiKV, and TiFlash
- Storage of TiKV and TiFlash

For information about how to determine the size of your TiDB cluster, see [Determine Your TiDB Size](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster).

> **Note:**
>
> If the vCPU and RAM size of TiDB or TiKV is set as **4 vCPU, 16 GiB**, note the following restrictions. To bypass these restrictions, you can [increase the vCPU and RAM](#change-vcpu-and-ram) first.
>
> - The node number of TiDB can only be set to 1 or 2, and the node number of TiKV is fixed to 3.
> - 4 vCPU TiDB can only be used with 4 vCPU TiKV, and 4 vCPU TiKV can only be used with 4 vCPU TiDB.
> - TiFlash is unavailable.
## Change node number

You can increase or decrease the number of TiDB, TiKV, or TiFlash nodes.

> **Warning:**
>
> Decreasing TiKV or TiFlash node number can be risky, which might lead to insufficient storage space, excessive CPU usage, or excessive memory usage on remaining nodes.

To change the number of TiDB, TiKV, or TiFlash nodes, take the following steps:

1. In the TiDB Cloud console, navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.
2. In the row of the cluster that you want to scale, click **...**.

    > **Tip:**
    >
    > Alternatively, you can also click the name of the cluster that you want to scale on the **Clusters** page and click **...** in the upper-right corner.

3. Click **Modify** in the drop-down menu. The **Modify Cluster** page is displayed.
4. On the **Modify Cluster** page, change the number of TiDB, TiKV, or TiFlash nodes.
5. Review the cluster size in the right pane, and then click **Confirm**.

You can also change the number of TiDB, TiKV, or TiFlash nodes using TiDB Cloud API through the [Modify a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/UpdateCluster) endpoint. Currently, TiDB Cloud API is still in beta. For more information, see [TiDB Cloud API Documentation](https://docs.pingcap.com/tidbcloud/api/v1beta).
## Change vCPU and RAM

You can increase or decrease vCPU and RAM of TiDB, TiKV, or TiFlash nodes.

> **Note:**
>
> - Changing vCPU and RAM is only available to the following clusters:
>     - Hosted on AWS and created after 2022/12/31.
>     - Hosted on Google Cloud and created after 2023/04/26.
>     - Hosted on Azure.
> - AWS has a cooldown period of vCPU and RAM changes. If your TiDB cluster is hosted on AWS, after changing the vCPU and RAM of TiKV or TiFlash, you must wait at least six hours before you can change it again.
> - Before you decrease the vCPU, make sure that the current node storage of TiKV or TiFlash does not exceed the maximum node storage for the target vCPU. For details, see [TiKV node storage](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#tikv-node-storage-size) and [TiFlash node storage](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#tiflash-node-storage). If the current storage of any component exceeds its limit, you cannot decrease the vCPU.

To change the vCPU and RAM of TiDB, TiKV, or TiFlash nodes, take the following steps:

1. In the TiDB Cloud console, navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.
2. In the row of the cluster that you want to scale, click **...**.

    > **Tip:**
    >
    > Alternatively, you can also click the name of the cluster that you want to scale on the **Clusters** page and click **...** in the upper-right corner.

3. Click **Modify** in the drop-down menu. The **Modify Cluster** page is displayed.
4. On the **Modify Cluster** page, change the vCPU and RAM of TiDB, TiKV, or TiFlash nodes.
5. Review the cluster size in the right pane, and then click **Confirm**.

You can also change the vCPU and RAM of a TiDB, TiKV, or TiFlash node using TiDB Cloud API through the [Modify a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/UpdateCluster) endpoint. Currently, TiDB Cloud API is still in beta. For more information, see [TiDB Cloud API Documentation](https://docs.pingcap.com/tidbcloud/api/v1beta).
## Change storage

You can increase the storage of TiKV or TiFlash.

> **Warning:**
>
> - For a running cluster, AWS, Azure, and Google Cloud do not allow in-place storage capacity downgrade.
> - AWS and Azure have a cooldown period of storage changes. If your TiDB cluster is hosted on AWS or Azure, after changing the storage or vCPU and RAM of TiKV or TiFlash, you must wait at least six hours before you can change it again.

To change the storage of TiKV or TiFlash, take the following steps:

1. In the TiDB Cloud console, navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.
2. In the row of the cluster that you want to scale, click **...**.

    > **Tip:**
    >
    > Alternatively, you can also click the name of the cluster that you want to scale on the **Clusters** page and click **...** in the upper-right corner.

3. Click **Modify** in the drop-down menu. The **Modify Cluster** page is displayed.
4. On the **Modify Cluster** page, change the storage of each TiKV or TiFlash node.
5. Review the cluster size in the right pane, and then click **Confirm**.

You can also change the storage of a TiKV or TiFlash node using TiDB Cloud API through the [Modify a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/UpdateCluster) endpoint. Currently, TiDB Cloud API is still in beta. For more information, see [TiDB Cloud API Documentation](https://docs.pingcap.com/tidbcloud/api/v1beta).
