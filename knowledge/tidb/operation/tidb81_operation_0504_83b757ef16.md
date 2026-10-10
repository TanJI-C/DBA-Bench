# tiup cluster restart command syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-restart.md`
- Source Title: `tiup cluster restart`
- Source Heading Path: `tiup cluster restart | tiup cluster restart > Syntax | tiup cluster restart > Options | tiup cluster restart > Options > -N, --node | tiup cluster restart > Options > -R, --role | tiup cluster restart > Options > -h, --help | tiup cluster restart > Outputs`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `cluster-restart`, `service-availability`, `command-syntax`, `node-selection`, `role-selection`, `help-option`, `command-output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0504_83b757ef16`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-restart.md#tiup-cluster-restart`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bd4e972f7936cf281f1ecf633c83a56e9e082b10975145373916a445c91a52a8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-restart#tiup-cluster-restart
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-restart.md

## Retrieval Guidance

- Use When: Use this content when looking for the syntax, flags, scope, or output of the `tiup cluster restart` command for restarting all or selected services in a specified cluster.
- Retrieval Keywords: tiup cluster restart, tiup cluster restart <cluster-name> [flags], -N, --node, -R, --role, -h, --help, cluster-name, tiup cluster display, cluster status table, node IDs, roles of nodes, service restart process log, related services are unavailable
- Follow-up Guidance: If the cluster name, node IDs, or node roles are needed, the content points to `cluster list` and `tiup cluster display` for that information.
- Classification Note: This is classified as an operation topic because the content defines how to run `tiup cluster restart`, its selection options, and the resulting restart-process output.

## Official Source Content

# tiup cluster restart

The command `tiup cluster restart` is used to restart all or some of the services of the specified cluster.

> **Note:**
>
> During the restart process, the related services are unavailable for a period of time.
## Syntax

```shell
tiup cluster restart <cluster-name> [flags]
```

`<cluster-name>`: the name of the cluster to operate on. If you forget the cluster name, you can check it with the [cluster list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-list) command.
## Options
### -N, --node

- Specifies the nodes to be restarted. The value of this option is a comma-separated list of node IDs. You can get the node IDs from the first column of the [cluster status table](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display) returned by the `tiup cluster display` command.
- Data type: `STRING`
- If this option is not specified, TiUP restarts all nodes by default.

> **Note:**
>
> If the option `-R, --role` is specified at the same time, TiUP restarts service nodes that match both the requirements of `-N, --node` and `-R, --role`.
### -R, --role

- Specified the roles of nodes to be restarted. The value of this option is a comma-separated list of the roles of the nodes. You can get the roles of the nodes from the second column of the [cluster status table](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display) returned by the `tiup cluster display` command.
- Data type: `STRING`
- If this option is not specified, TiUP restarts nodes of all roles by default.

> **Note:**
>
> If the option `-N, --node` is specified at the same time, TiUP restarts service nodes that match both the requirements of `-N, --node` and `-R, --role`.
### -h, --help

- Prints help information.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Outputs

The log of the service restart process.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
