# tiup cluster rename command usage

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-rename.md`
- Source Title: `tiup cluster rename`
- Source Heading Path: `tiup cluster rename | tiup cluster rename > Syntax | tiup cluster rename > Options | tiup cluster rename > Options > -h, --help | tiup cluster rename > Outputs`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dashboard`
- Topic Tags: `cluster-rename`, `command-syntax`, `help-option`, `grafana-dashboard`, `reload`, `execution-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0503_a78ff3b457`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-rename.md#tiup-cluster-rename`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b6f5eeb5c8b3ead8bb0ace4e58ea4b59a26a5e8e6d294fe08eed7022789c6596`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-rename#tiup-cluster-rename
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-rename.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiUP command syntax, help option, or related Grafana dashboard notes for renaming an already deployed cluster.
- Retrieval Keywords: tiup cluster rename, tiup cluster rename <old-cluster-name> <new-cluster-name> [flags], old-cluster-name, new-cluster-name, -h, --help, dashboard_dir, grafana_servers, datasource, tiup cluster reload -R grafana, execution log of the tiup-cluster
- Follow-up Guidance: If the TiUP cluster configures the `dashboard_dir` field of `grafana_servers`, the source says to update the `datasource` field in local `*.json` dashboard files to the new cluster name and then execute `tiup cluster reload -R grafana`.
- Classification Note: The classification is operation because the content documents the `tiup cluster rename` command usage, syntax, option, and output for changing a deployed cluster name.

## Official Source Content

# tiup cluster rename

The cluster name is specified when [the cluster is deployed](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-deploy). If you want to change the cluster name after the cluster is deployed, you can use the command `tiup cluster rename`.

> **Note:**
>
> If the `dashboard_dir` field of `grafana_servers` is configured for the TiUP cluster, after you execute the command `tiup cluster rename` to rename the cluster, the following additional steps are required:
>
> + For the `*.json` files in the local dashboards directory, update the `datasource` field of each file to the new cluster name, because the value of `datasource` must be the name of the cluster.
> + Execute the command `tiup cluster reload -R grafana`.
## Syntax

```shell
tiup cluster rename <old-cluster-name> <new-cluster-name> [flags]
```

- `<old-cluster-name>`: The old cluster name.
- `<new-cluster-name>`: The new cluster name.
## Options
### -h, --help

- Prints help information.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Outputs

The execution log of the tiup-cluster.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
