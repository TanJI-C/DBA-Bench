# tiup dm restart command syntax, options, and outputs

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-restart.md`
- Source Title: `tiup dm restart`
- Source Heading Path: `tiup dm restart | tiup dm restart > Syntax | tiup dm restart > Options | tiup dm restart > Options > -N, --node | tiup dm restart > Options > -R, --role | tiup dm restart > Options > -h, --help | tiup dm restart > Outputs`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `restart`, `service-availability`, `cluster-management`, `command-syntax`, `node-selection`, `role-selection`, `help-option`, `logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0511_7cdf5280d0`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-restart.md#tiup-dm-restart`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `01e892d0ac15b28c4ea2ec17be07beeaf2f49e60ab2e52c7e63bb132ed76104f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-restart#tiup-dm-restart
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-restart.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to restart all or selected services in a specified DM cluster with TiUP, including command syntax, node or role filtering, service unavailability during restart, and what output is produced.
- Retrieval Keywords: tiup dm restart, tiup dm restart <cluster-name> [flags], restart all or some of the services, specified cluster, -N, --node, comma-separated list of node IDs, node IDs from the first column, tiup dm display, -R, --role, comma-separated list of the roles of the nodes, second column of the cluster status table, match both the requirements of -N and -R, -h, --help, prints help information, service restart process log, related services are unavailable for a period of time, cluster list
- Follow-up Guidance: If the cluster name, node IDs, or node roles are needed, the content points to `cluster list` and `tiup dm display` for that information.
- Classification Note: This is classified as an operation chunk because the content defines the `tiup dm restart` command usage, its flags for selecting nodes or roles, and the restart process output.

## Official Source Content

# tiup dm restart

The command `tiup dm restart` is used to restart all or some of the services of the specified cluster.

> **Note:**
>
> During the restart process, the related services are unavailable for a period of time.
## Syntax

```shell
tiup dm restart <cluster-name> [flags]
```

`<cluster-name>`: the name of the cluster to operate on. If you forget the cluster name, you can check it with the [cluster list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-list) command.
## Options
### -N, --node

- Specifies the nodes to be restarted. The value of this option is a comma-separated list of node IDs. You can get the node IDs from the first column of the cluster status table returned by the `[tiup dm display](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display)` command.
- Data type: `STRING`
- If this option is not specified, TiUP restarts all nodes by default.

> **Note:**
>
> If the option `-R, --role` is specified at the same time, TiUP restarts service nodes that match both the requirements of `-N, --node` and `-R, --role`.
### -R, --role

- Specifies the roles of nodes to be restarted. The value of this option is a comma-separated list of the roles of the nodes. You can get the roles of the nodes from the second column of the cluster status table returned by the `[tiup dm display](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display)` command.
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

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
