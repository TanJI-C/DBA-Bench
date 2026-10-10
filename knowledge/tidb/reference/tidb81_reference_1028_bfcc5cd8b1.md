# tiup dm reload command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-reload.md`
- Source Title: `tiup dm reload`
- Source Heading Path: `tiup dm reload | tiup dm reload > Syntax | tiup dm reload > Options | tiup dm reload > Options > -N, --node | tiup dm reload > Options > -R, --role | tiup dm reload > Options > --skip-restart | tiup dm reload > Options > -h, --help | tiup dm reload > Output`
- Source Line Ranges: `5-64`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `reload`, `cluster configuration`, `restart`, `node selection`, `role selection`, `skip restart`, `help`, `output log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1028_bfcc5cd8b1`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-reload.md#tiup-dm-reload`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7afa39ba1c017034d81ded8ad3521584c31af6e43514da199a4f89e895c82fb3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-reload#tiup-dm-reload
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-reload.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the command syntax, option behavior, or output of `tiup dm reload` after modifying DM cluster configuration.
- Retrieval Keywords: tiup dm reload, reload <cluster-name> [flags], modifying the cluster configuration, control machine to the remote machine, restarts the service in order according to the upgrade process, cluster remains available during the restart process, -N, --node, node IDs, tiup dm display, cluster status table, -R, --role, node roles, --skip-restart, refreshes all node configurations, without restarting any nodes, -h, --help, execution log of the tiup-dm
- Follow-up Guidance: The source also states that node IDs and node roles can be obtained from the cluster status table returned by `tiup dm display`.
- Classification Note: This is a command reference for the self-managed TiUP DM `reload` operation, covering syntax, flags, restart and refresh behavior, and output.

## Official Source Content

# tiup dm reload

After [modifying the cluster configuration](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-edit-config), the cluster needs to be reloaded using the `tiup dm reload` command for the configuration to take effect. This command publishes the configuration of the control machine to the remote machine where the service is running and restarts the service in order according to the upgrade process. The cluster remains available during the restart process.
## Syntax

```shell
tiup dm reload <cluster-name> [flags]
```

`<cluster-name>`: the name of the cluster to operate on.
## Options
### -N, --node

- Specifies the nodes to be restarted. If not specified, all nodes are restarted. The value of this option is a comma-separated list of node IDs. You can get the node IDs from the first column of the cluster status table returned by the [`tiup dm display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, all nodes are selected by default.

> **Note:**
>
> + If the `-R, --role` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are restarted.
> + If the `--skip-restart` option is specified, the `-N, --node` option is invalid.
### -R, --role

- Specifies the roles to be restarted. If not specified, all roles are restarted. The value of this option is a comma-separated list of node roles. You can get the roles of nodes from the second column of the cluster status table returned by the [`tiup dm display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, all roles are selected by default.

> **Note:**
>
> + If the `-N, --node` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are restarted.
> + If the `--skip-restart` option is specified, the `-R, --role` option is invalid.
### --skip-restart

The `tiup dm reload` command performs two operations:

- Refreshes all node configurations
- Restarts the specified node

After you specify the `--skip-restart` option, it only refreshes the configuration without restarting any nodes, so that the refreshed configuration is not applied and does not take effect until the next restart of the corresponding service.

- Data type: `BOOLEAN`
- Default: false
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
## Output

The execution log of the tiup-dm.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
