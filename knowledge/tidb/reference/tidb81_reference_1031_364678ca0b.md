# tiup dm start syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-start.md`
- Source Title: `tiup dm start`
- Source Heading Path: `tiup dm start | tiup dm start > Syntax | tiup dm start > Options | tiup dm start > Options > -N, --node | tiup dm start > Options > -R, --role | tiup dm start > Options > -h, --help | tiup dm start > Output`
- Source Line Ranges: `5-50`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `command-line`, `cluster-start`, `node-selection`, `role-selection`, `help`, `output-logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1031_364678ca0b`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-start.md#tiup-dm-start`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c1bafcec6b575b425be86ca8bce73ce2e61efaa403a25a62a7794e67326bbbbf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-start#tiup-dm-start
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-start.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how to start all or part of a DM cluster with `tiup dm start`, including syntax, node or role filtering, help, and command output.
- Retrieval Keywords: tiup dm start, tiup dm start <cluster-name> [flags], -N, --node, -R, --role, -h, --help, cluster-name, tiup dm display, cluster status table, node IDs, node roles, start all nodes, start all roles, log of starting the service
- Follow-up Guidance: If the cluster name is unknown, the content says it can be checked with `cluster list`, and node IDs or roles can be obtained from the `tiup dm display` cluster status table.
- Classification Note: This is reference content because it defines the `tiup dm start` command syntax, option semantics, and output behavior for TiUP DM.

## Official Source Content

# tiup dm start

The `tiup dm start` command is used to start all or part of the services of the specified cluster.
## Syntax

```shell
tiup dm start <cluster-name> [flags]
```

`<cluster-name>`: the name of the cluster to operate on. If you forget the cluster name, you can check it with the [cluster list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-list) command.
## Options
### -N, --node

- Specifies the nodes to be started. If not specified, all nodes are started. The value of this option is a comma-separated list of node IDs. You can get the node IDs from the first column of the cluster status table returned by the [`tiup dm display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, all nodes are started.

> **Note:**
>
> If the `-R, --role` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are started.
### -R, --role

- Specifies the roles to be started. If not specified, all roles are started. The value of this option is a comma-separated list of node roles. You can get the roles of nodes from the second column of the cluster status table returned by the [`tiup dm display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, all roles are started.

> **Note:**
>
> If the `-N, --node` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are started.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
## Output

The log of starting the service.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
