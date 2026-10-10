# tiup dm stop syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-stop.md`
- Source Title: `tiup dm stop`
- Source Heading Path: `tiup dm stop | tiup dm stop > Syntax | tiup dm stop > Options | tiup dm stop > Options > -N, --node | tiup dm stop > Options > -R, --role | tiup dm stop > Options > -h, --help | tiup dm stop > Output`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `stop-service`, `cluster-operations`, `command-syntax`, `node-selection`, `role-selection`, `help-option`, `command-output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1032_57d60d4740`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-stop.md#tiup-dm-stop`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `99e395ffa9bc1c00832ab3cce0be462267a78d9d4aea7d7251c529f545f95226`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-stop#tiup-dm-stop
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-stop.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, flags, selection behavior, or output of the `tiup dm stop` command for a specified DM cluster.
- Retrieval Keywords: tiup dm stop, tiup dm stop <cluster-name> [flags], -N, --node, -R, --role, -h, --help, stop all or part of the services, cluster-name, node IDs, node roles, tiup dm display, cluster status table, log of stopping the service
- Follow-up Guidance: If the cluster name is forgotten, the content says it can be checked with the `cluster list` command, and node IDs or roles can be obtained from the cluster status table returned by `tiup dm display`.
- Classification Note: This is reference content because it defines the `tiup dm stop` command purpose, syntax, options, option interaction, and output.

## Official Source Content

# tiup dm stop

The `tiup dm stop` command is used to stop all or part of the services of the specified cluster.

> **Note:**
>
> The cluster cannot provide services after the core service is stopped.
## Syntax

```shell
tiup dm stop <cluster-name> [flags]
```

`<cluster-name>`: the name of the cluster to operate on. If you forget the cluster name, you can check it with the [cluster list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-list) command.
## Options
### -N, --node

- Specifies the nodes to be stopped. If not specified, all nodes are stopped. The value of this option is a comma-separated list of node IDs. You can get the node IDs from the first column of the cluster status table returned by the [`tiup dm display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, all nodes are selected by default.

> **Note:**
>
> If the `-R, --role` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are stopped.
### -R, --role

- Specifies the roles to be stopped. If not specified, all roles are stopped. The value of this option is a comma-separated list of node roles. You can get the roles of nodes from the second column of the cluster status table returned by the [`tiup dm display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, all roles are selected by default.

> **Note:**
>
> If the `-N, --node` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are stopped.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
## Output

The log of stopping the service.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
