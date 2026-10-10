# tiup cluster stop command syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-stop.md`
- Source Title: `tiup cluster stop`
- Source Heading Path: `tiup cluster stop | tiup cluster stop > Syntax | tiup cluster stop > Options | tiup cluster stop > Options > -N, --node | tiup cluster stop > Options > -R, --role | tiup cluster stop > Options > -h, --help | tiup cluster stop > Output`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `cluster-stop`, `service-stop`, `command-syntax`, `node-selection`, `role-selection`, `help-option`, `command-output`, `service-availability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0506_6fc946d7fc`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-stop.md#tiup-cluster-stop`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `511666a19d2204c42fbd98581a6ecadcec12ac8e59aebe8debd3f0924104c561`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-stop#tiup-cluster-stop
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-stop.md

## Retrieval Guidance

- Use When: Use this when you need the syntax and options for stopping a TiDB cluster or selected nodes and roles with `tiup cluster stop`.
- Retrieval Keywords: tiup cluster stop, tiup cluster stop <cluster-name> [flags], -N, --node, -R, --role, -h, --help, cluster status table, node IDs, roles of nodes, log of stopping the service
- Follow-up Guidance: Check `tiup cluster list` for the cluster name, and `tiup cluster display` for node IDs and roles.
- Classification Note: This chunk documents the `tiup cluster stop` operation, including its command syntax, node and role selection options, and the stopping log output.

## Official Source Content

# tiup cluster stop

The `tiup cluster stop` command is used to stop all services or some services of the specified cluster.

> **Note:**
>
> If the core services of a cluster are stopped, the cluster cannot provide services anymore.
## Syntax

```shell
tiup cluster stop <cluster-name> [flags]
```

`<cluster-name>` is the name of the cluster to operate on. If you forget the cluster name, you can check it using the [`tiup cluster list`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-list) command.
## Options
### -N, --node

- Specifies the nodes to be stopped. The value of this option is a comma-separated list of node IDs. You can get the node IDs from the first column of the [cluster status table](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display) returned by the `tiup cluster display` command.
- Data type: `STRINGS`
- If this option is not specified in the command, the command stops all the nodes by default.

> **Note:**
>
> If the `-R, --role` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are stopped.
### -R, --role

- Specifies the roles of nodes to be stopped. The value of this option is a comma-separated list of the roles of the nodes. You can get the roles of the nodes from the second column of the [cluster status table](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display) returned by the `tiup cluster display` command.
- Data type: `STRINGS`
- If this option is not specified in the command, the command stops all the roles by default.

> **Note:**
>
> If the `-N, --node` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are stopped.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Output

The log of stopping the service.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
