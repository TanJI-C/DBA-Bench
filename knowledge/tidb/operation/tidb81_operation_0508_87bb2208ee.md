# TiUP DM import command for upgrading DM v1.0 clusters

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-import.md`
- Source Title: `tiup dm import`
- Source Heading Path: `tiup dm import <span class="version-mark">Only for upgrading DM v1.0</span> | tiup dm import <span class="version-mark">Only for upgrading DM v1.0</span> > Syntax | tiup dm import <span class="version-mark">Only for upgrading DM v1.0</span> > Options | tiup dm import <span class="version-mark">Only for upgrading DM v1.0</span> > Options > -v, --cluster-version | tiup dm import <span class="version-mark">Only for upgrading DM v1.0</span> > Options > -d, --dir | tiup dm import <span class="version-mark">Only for upgrading DM v1.0</span> > Options > --inventory | tiup dm import <span class="version-mark">Only for upgrading DM v1.0</span> > Options > --rename | tiup dm import <span class="version-mark">Only for upgrading DM v1.0</span> > Options > -h, --help | tiup dm import <span class="version-mark">Only for upgrading DM v1.0</span> > Outputs`
- Source Line Ranges: `5-69`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `import`, `upgrade`, `command`, `flags`, `ansible`, `inventory`, `cluster-version`, `rename`, `help`, `outputs`, `dm-master`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0508_87bb2208ee`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-import.md#tiup-dm-import-span-class-version-mark-only-for-upgrading-dm-v1-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `771ae67d73aaea10a0ea07b5b70f696ecaee04c564bbf19cf1c454bc40d50b9e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-import#tiup-dm-import-span-class-version-mark-only-for-upgrading-dm-v1-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-import.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiUP command and flags to import a DM v1.0 cluster and redeploy it as a new DM v2.0 or later cluster.
- Retrieval Keywords: tiup dm import, upgrading DM v1.0, import v1.0 clusters, redeploy the clusters in DM v2.0, Only for upgrading DM v1.0, --cluster-version, -v, --dir, --inventory, --rename, inventory.ini, cluster_name, DM Portal, stop-task, tiup update --self && tiup update dm, scale out, DM-master
- Follow-up Guidance: The content notes related follow-up references for manually upgrading data migration tasks to an existing v2.0 cluster and for using the `scale out` command to add DM-master nodes after import.
- Classification Note: This is classified as an operation topic because the content defines the `tiup dm import` command syntax, required and optional flags, prerequisites, limitations, and output for importing a DM v1.0 cluster.

## Official Source Content

# tiup dm import Only for upgrading DM v1.0

> **Note:**
>

This command is used only for upgrading DM clusters from v1.0 to v2.0 or later versions.

In DM v1.0, the cluster is basically deployed using TiDB Ansible. TiUP DM provides the `import` command to import v1.0 clusters and redeploy the clusters in DM v2.0.

> **Note:**
>
> - The command does not support importing DM Portal components from DM v1.0 clusters.
> - Before importing the cluster, stop running the original cluster first.
> - For data migration tasks that need to be upgraded to v2.0, do not execute `stop-task` on these tasks.
> - The command only supports importing to DM v2.0.0-rc.2 and later versions.
> - The `import` command is used to import a DM v1.0 cluster to a new DM v2.0 cluster. If you need to import data migration tasks to an existing v2.0 cluster, refer to [Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+](https://docs.pingcap.com/tidb/stable/dm/manually-upgrade-dm-1.0-to-2.0)
> - The deployment directories of some components might be different from those in the original cluster. You can check it with the `display` command.
> - Before importing the cluster, run `tiup update --self && tiup update dm` to upgrade TiUP DM components to the latest version.
> - After the cluster is imported, there is only one DM-master node in the cluster. You can refer to [the `scale out` command](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-scale-out) to scale out the DM-master node.
## Syntax

```shell
tiup dm import [flags]
```
## Options
### -v, --cluster-version

- Specifies the version number for redeploying. You must use a version later than v2.0.0-rc.2 (including v2.0.0-rc.2).
- Data type: `STRING`
- This option is **required** to execute the command.
### -d, --dir

- Specifies the directory of TiDB Ansible.
- Data type: `STRING`
- If this option is not specified in the command, the current directory is the default directory.
### --inventory

- Specifies the name of the Ansible inventory file.
- Data type: `STRING`
- If this option is not specified in the command, the default file name is `"inventory.ini"`.
### --rename

- Renames the imported cluster.
- Data type: `STRING`
- If this option is not specified in the command, the default cluster name is the `cluster_name` specified in the inventory file.
### -h, --help

- Prints help information.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Outputs

The log of the importing process.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
