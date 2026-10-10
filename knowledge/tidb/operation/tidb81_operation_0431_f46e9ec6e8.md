# Delete a TiDB node group

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-node-group-management.md`
- Source Title: `Manage TiDB Node Groups`
- Source Heading Path: `Manage TiDB Node Groups > Delete a TiDB node group`
- Source Line Ranges: `147-160`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `node-groups`, `deletion`, `network-configuration`, `private-endpoint`, `public-access`, `cluster-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0431_f46e9ec6e8`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-node-group-management.md#delete-a-tidb-node-group`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d9187e95f44dc08ad49a654dc8465df882b75b7023cdf2fb8cb4919db56c1035`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-management#delete-a-tidb-node-group
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-node-group-management.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the TiDB Cloud UI steps to delete a TiDB node group and understand what associated network settings are removed.
- Retrieval Keywords: Delete a TiDB node group, TiDB node group deletion, Clusters page, Nodes, Node Map, Modify Cluster, delete the TiDB node group, private endpoint connections, IP list for public access, network configurations are also removed
- Follow-up Guidance: The content notes that deleting a TiDB node group also removes its nodes and network configurations, including private endpoint connections and the IP list for public access.
- Classification Note: This is an operation chunk because it provides the procedure in TiDB Cloud to delete a TiDB node group and describes the deletion effect on related network configuration.

## Official Source Content

## Delete a TiDB node group

> **Note**:
>
> When you delete a TiDB node group, its nodes and network configurations are also removed, including private endpoint connections and the IP list for public access.

To delete a TiDB node group, perform the following steps:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.
2. In the left navigation pane, click **Nodes**.
3. On the **Node Map** page, click **Modify** in the upper-right corner. The **Modify Cluster** page is displayed.
4. On the **Modify Cluster** page, click <svg width="24" height="24" viewBox="0 0 24 24" stroke-width="1.5" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M16 6V5.2C16 4.0799 16 3.51984 15.782 3.09202C15.5903 2.71569 15.2843 2.40973 14.908 2.21799C14.4802 2 13.9201 2 12.8 2H11.2C10.0799 2 9.51984 2 9.09202 2.21799C8.71569 2.40973 8.40973 2.71569 8.21799 3.09202C8 3.51984 8 4.0799 8 5.2V6M10 11.5V16.5M14 11.5V16.5M3 6H21M19 6V17.2C19 18.8802 19 19.7202 18.673 20.362C18.3854 20.9265 17.9265 21.3854 17.362 21.673C16.7202 22 15.8802 22 14.2 22H9.8C8.11984 22 7.27976 22 6.63803 21.673C6.07354 21.3854 5.6146 20.9265 5.32698 20.362C5 19.7202 5 18.8802 5 17.2V6" stroke="currentColor" stroke-width="inherit" stroke-linecap="round" stroke-linejoin="round"/></svg> to delete the TiDB node group.

![Delete the TiDB node group](/media/tidb-cloud/tidb-node-group-delete.png)
