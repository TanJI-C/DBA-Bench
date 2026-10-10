# tiup cluster disable syntax options and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-disable.md`
- Source Title: `tiup cluster disable`
- Source Heading Path: `tiup cluster disable | tiup cluster disable > Syntax | tiup cluster disable > Options | tiup cluster disable > Options > -N, --node | tiup cluster disable > Options > -R, --role | tiup cluster disable > Options > -h, --help | tiup cluster disable > Output`
- Source Line Ranges: `5-50`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `service-auto-enable`, `systemctl`, `node-selection`, `role-selection`, `command-syntax`, `help-flag`, `execution-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1003_31f55837cf`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-disable.md#tiup-cluster-disable`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d4371a80ec12b147ea05c56b9e5f04b5580162b5806b72e36eb847fac77566f3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-disable#tiup-cluster-disable
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-disable.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, flags, node or role selection behavior, or output of the `tiup cluster disable` command that disables service auto-enabling for a cluster.
- Retrieval Keywords: tiup cluster disable, tiup cluster disable <cluster-name> [flags], systemctl disable <service>, disable the auto-enabling of cluster service, -N, --node, -R, --role, -h, --help, comma-separated list of node IDs, comma-separated list of node roles, tiup cluster display, cluster status table, execution log of the tiup-cluster
- Follow-up Guidance: The source notes that node IDs and node roles can be obtained from the cluster status table returned by `tiup cluster display`.
- Classification Note: This is reference content because it defines the command purpose, exact syntax, option semantics, selection rules for `-N` and `-R`, and the stated output.

## Official Source Content

# tiup cluster disable

After restarting the machine on which the cluster service is located, the cluster service will be automatically enabled. To disable the auto-enabling of cluster service, you can use the `tiup cluster disable` command. This command executes `systemctl disable <service>` on the specified node to disable the auto-enabling of the service.
## Syntax

```shell
tiup cluster disable <cluster-name> [flags]
```

`<cluster-name>`: the cluster whose service auto-enabling is to be disabled.
## Options
### -N, --node

- Specifies the nodes whose service auto-enabling is to be disabled. The value of this option is a comma-separated list of node IDs. You can get the node IDs from the first column of the cluster status table returned by the [`tiup cluster display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, the auto-enabling of all nodes is disabled by default.

> **Note:**
>
> If the `-R, --role` option is specified at the same time, the auto-enabling of services that match both the specifications of `-N, --node` and `-R, --role` is disabled.
### -R, --role

- Specifies the roles whose service auto-enabling is to be disabled. The value of this option is a comma-separated list of node roles. You can get the roles of nodes from the second column of the cluster status table returned by the [`tiup cluster display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, the auto-enabling of all roles is disabled by default.

> **Note:**
>
> If the `-N, --node` option is specified at the same time, the auto-enabling of services that match both the specifications of `-N, --node` and `-R, --role` is disabled.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Output

The execution log of the tiup-cluster.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
