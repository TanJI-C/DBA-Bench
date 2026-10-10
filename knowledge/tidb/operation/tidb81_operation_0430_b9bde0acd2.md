# View and modify TiDB node groups

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-node-group-management.md`
- Source Title: `Manage TiDB Node Groups`
- Source Heading Path: `Manage TiDB Node Groups > View TiDB node groups | Manage TiDB Node Groups > Modify a TiDB node group | Manage TiDB Node Groups > Modify a TiDB node group > Change the group name | Manage TiDB Node Groups > Modify a TiDB node group > Update the node configuration`
- Source Line Ranges: `111-146`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `viewing`, `modification`, `group-name`, `node-configuration`, `scaling`, `node-map`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0430_b9bde0acd2`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-node-group-management.md#view-tidb-node-groups`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `60c65ceb3bb194f200979b774f3cc6c8e144551ab20d8cc61aa782df425a5358`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-management#view-tidb-node-groups
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-node-group-management.md

## Retrieval Guidance

- Use When: Use this when someone needs the console steps to view TiDB node groups or modify a group name and node configurations.
- Retrieval Keywords: View TiDB node groups, Modify a TiDB node group, Change the group name, Update the node configuration, Nodes, Node Map, Modify Cluster, TiDB node group, Change the number of TiDB nodes, Add new node groups, Storage x Nodes, TiKV, TiFlash
- Follow-up Guidance: The content specifies that on the Modify Cluster page you can change the number of TiDB nodes, add new node groups, and update the size and Storage x Nodes configuration for TiKV and TiFlash nodes.
- Classification Note: This is classified as an operation chunk because the official content gives UI steps for viewing node groups and modifying names and node configurations.

## Official Source Content

## View TiDB node groups

To view the details of TiDB node groups, perform the following steps:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.
2. In the left navigation pane, click **Nodes** to view the list of TiDB node groups.

    To switch to the table view, click <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 -4 24 24" stroke-width="1.5"><path d="M3 9.5H21M3 14.5H21M7.8 4.5H16.2C17.8802 4.5 18.7202 4.5 19.362 4.82698C19.9265 5.1146 20.3854 5.57354 20.673 6.13803C21 6.77976 21 6.61984 21 8.3V15.7C21 17.3802 21 17.2202 20.673 17.862C20.3854 18.4265 19.9265 18.8854 19.362 19.173C18.7202 19.5 17.8802 19.5 16.2 19.5H7.8C6.11984 19.5 5.27976 19.5 4.63803 19.173C4.07354 18.8854 3.6146 18.4265 3.32698 17.862C3 17.2202 3 17.3802 3 15.7V8.3C3 6.61984 3 6.77976 3.32698 6.13803C3.6146 5.57354 4.07354 5.1146 4.63803 4.82698C5.27976 4.5 6.11984 4.5 7.8 4.5Z" stroke="currentColor" stroke-width="inherit" stroke-linecap="round" stroke-linejoin="round"></path></svg>.
## Modify a TiDB node group

You can modify the group name and node configurations in the group.
### Change the group name

To change the group name, perform the following steps:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.
2. In the left navigation pane, click **Nodes**.
3. Click <svg width="16" height="16" viewBox="0 -2 24 24" stroke-width="1.5" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 20H21M3.00003 20H4.67457C5.16376 20 5.40835 20 5.63852 19.9447C5.84259 19.8957 6.03768 19.8149 6.21663 19.7053C6.41846 19.5816 6.59141 19.4086 6.93732 19.0627L19.5001 6.49998C20.3285 5.67156 20.3285 4.32841 19.5001 3.49998C18.6716 2.67156 17.3285 2.67156 16.5001 3.49998L3.93729 16.0627C3.59139 16.4086 3.41843 16.5816 3.29475 16.7834C3.18509 16.9624 3.10428 17.1574 3.05529 17.3615C3.00003 17.5917 3.00003 17.8363 3.00003 18.3255V20Z" stroke="currentColor" stroke-width="inherit" stroke-linecap="round" stroke-linejoin="round"/></svg> and enter a new name for the TiDB node group.
### Update the node configuration

To update TiDB, TiKV, or TiFlash node configurations in the group, perform the following steps:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.
2. In the left navigation pane, click **Nodes**.
3. On the **Node Map** page, click **Modify** in the upper-right corner. The **Modify Cluster** page is displayed.
4. On the **Modify Cluster** page, you can:

    - Change the number of TiDB nodes.
    - Add new node groups.
    - Update the size and **Storage x Nodes** configuration for TiKV and TiFlash nodes.

![Change TiDB node group node count](/media/tidb-cloud/tidb-node-group-change-node-count.png)
