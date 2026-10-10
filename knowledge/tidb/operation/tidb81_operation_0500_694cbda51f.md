# tiup cluster import command usage, restrictions, options, and output

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-import.md`
- Source Title: `tiup cluster import`
- Source Heading Path: `tiup cluster import | tiup cluster import > Syntax | tiup cluster import > Options | tiup cluster import > Options > -d, --dir | tiup cluster import > Options > --ansible-config | tiup cluster import > Options > --inventory | tiup cluster import > Options > --no-backup | tiup cluster import > Options > --rename | tiup cluster import > Options > -h, --help | tiup cluster import > Output`
- Source Line Ranges: `5-71`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`
- Topic Tags: `cluster-import`, `ansible-migration`, `command-syntax`, `command-options`, `backup`, `rename`, `help`, `logs`, `prerequisites`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0500_694cbda51f`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-import.md#tiup-cluster-import`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a8d01eb0efc82841719a3984d2a36968388cdc84c8647f439a9f534f0d60541f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-import#tiup-cluster-import
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-import.md

## Retrieval Guidance

- Use When: Use this when looking for the `tiup cluster import` command syntax, supported options, import restrictions, backup behavior, or the warning about migrating a TiDB Ansible-managed cluster to TiUP Cluster management.
- Retrieval Keywords: tiup cluster import, import command, TiUP Cluster, TiDB Ansible, tiup cluster import [flags], --dir, --ansible-config, --inventory, --no-backup, --rename, --help, ansible-backup, ${TIUP_HOME}/.tiup/storage/cluster/clusters/{cluster-name}/ansible-backup, inventory.ini, ansible.cfg, cluster_name, TLS encryption enabled, Pure KV clusters, Kafka enabled, Spark enabled, TiDB Lightning, TiKV Importer, push mode, node_exporter_port, blackbox_exporter_port, monitored_servers, deploy.yaml, logs of the import process
- Follow-up Guidance: The source also states that after importing the TiDB Ansible configuration to TiUP for management, TiDB Ansible should no longer be used for cluster operations, and it lists unsupported cluster situations and monitoring prerequisites involving `monitored_servers` and `deploy.yaml`.
- Classification Note: This is classified as an operation topic because the content defines the `tiup cluster import` command usage, flags, restrictions, and output for transferring cluster management from TiDB Ansible to TiUP Cluster.

## Official Source Content

# tiup cluster import

Before TiDB v4.0, TiDB clusters were mainly deployed using TiDB Ansible. For TiDB v4.0 and later releases, TiUP Cluster provides the `import` command to transfer the clusters to the tiup-cluster component for management.

> **Note:**
>
> + After importing the TiDB Ansible configuration to TiUP for management, **DO NOT** use TiDB Ansible for cluster operations anymore. Otherwise, conflicts might be caused due to inconsistent meta information.
> + If the clusters deployed using TiDB Ansible are in any of the following situations, do not use the `import` command.
>     + Clusters with TLS encryption enabled
>     + Pure KV clusters (clusters without TiDB instances)
>     + Clusters with Kafka enabled
>     + Clusters with Spark enabled
>     + Clusters with TiDB Lightning/TiKV Importer enabled
>     + Clusters still using the old `push` mode to collect monitoring metrics (if you keep the default mode `pull` unchanged, using the `import` command is supported)
>     + Clusters in which the non-default ports (the ports configured in the `group_vars` directory are compatible) are separately configured in the `inventory.ini` configuration file using `node_exporter_port` / `blackbox_exporter_port`
> + If some nodes in the cluster deployed using TiDB Ansible are deployed without monitoring components, you should first use TiDB Ansible to add the corresponding node information in the `monitored_servers` section of the `inventory.ini` file, and then use the `deploy.yaml` playbook to fully deploy monitoring components. Otherwise, when you perform maintenance operations after the cluster is imported into TiUP, errors might occur due to the lack of monitoring components.
## Syntax

```shell
tiup cluster import [flags]
```
## Options
### -d, --dir

- Specifies the directory where TiDB Ansible is located.
- Data type: `STRING`
- The option is enabled by default with the current directory (the default value) passed in.
### --ansible-config

- Specifies the path of the Ansible configuration file.
- Data type: `STRING`
- The option is enabled by default with `. /ansible.cfg` (the default value) passed in.
### --inventory

- Specifies the name of the Ansible inventory file.
- Data type: `STRING`
- The option is enabled by default with `inventory.ini` (the default value) passed in.
### --no-backup

- Controls whether to disable the backup of files in the directory where TiDB Ansible is located.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. After a successful import, everything in the directory specified by the `-dir` option is backed up to the `${TIUP_HOME}/.tiup/storage/cluster/clusters/{cluster-name}/ansible-backup` directory. If there are multiple inventory files (when multiple clusters are deployed) in this directory, it is recommended to enable this option. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
### --rename

- Renames the imported cluster.
- Data type: `STRING`
- Default: NULL. If this option is not specified in the command, the cluster_name specified in inventory is used as the cluster name.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Output

Shows the logs of the import process.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
