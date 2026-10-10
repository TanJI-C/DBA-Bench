# tiup cluster reload command syntax, flags, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-reload.md`
- Source Title: `tiup cluster reload`
- Source Heading Path: `tiup cluster reload | tiup cluster reload > Syntax | tiup cluster reload > Options | tiup cluster reload > Options > --force | tiup cluster reload > Options > --transfer-timeout | tiup cluster reload > Options > --ignore-config-check | tiup cluster reload > Options > -N, --node | tiup cluster reload > Options > -R, --role | tiup cluster reload > Options > --skip-restart | tiup cluster reload > Options > -h, --help | tiup cluster reload > Options > --pre-restart-script | tiup cluster reload > Options > --post-restart-script | tiup cluster reload > Output`
- Source Line Ranges: `5-106`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `cluster-reload`, `command-syntax`, `flags`, `config-deployment`, `service-restart`, `leader-transfer`, `config-check`, `node-selection`, `role-selection`, `skip-restart`, `experimental-scripts`, `command-output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1010_cd19d352a4`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-reload.md#tiup-cluster-reload`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4ad583883250243f187138204cd25d442eef964c883ba899c6d9ec8c35fb0641`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-reload#tiup-cluster-reload
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-reload.md

## Retrieval Guidance

- Use When: Use this when looking up how `tiup cluster reload <cluster-name> [flags]` applies modified cluster configuration, restarts services in upgrade order, or supports node, role, restart, config-check, and leader-transfer related flags.
- Retrieval Keywords: tiup cluster reload, tiup cluster reload <cluster-name> [flags], --force, --transfer-timeout, --ignore-config-check, -N, --node, -R, --role, --skip-restart, --pre-restart-script, --post-restart-script, <binary> --config-check <config-file>, tiup cluster display, cluster status table, leader migrated to other nodes first, execution log of the tiup-cluster
- Follow-up Guidance: The content notes that node IDs come from the first column and roles from the second column of the cluster status table returned by `tiup cluster display`, and that `--skip-restart` makes `-N`, `-R`, and the restart scripts ineffective.
- Classification Note: This is reference content because it defines the `tiup cluster reload` command syntax, documents each flag and default, and states the command output behavior from the official content.

## Official Source Content

# tiup cluster reload

After [modifying the cluster configuration](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-edit-config), the cluster needs to be reloaded using the `tiup cluster reload` command for the configuration to take effect. This command publishes the configuration of the control machine to the remote machine where the service is running, and follows the upgrade process to restart the services in order according to the upgrade process. The cluster is still available during the restart process.
## Syntax

```shell
tiup cluster reload <cluster-name> [flags]
```

`<cluster-name>`: the cluster name to operate on.
## Options
### --force

- Ignores errors in the reloading process and forces reload.
- Data type: `BOOLEAN`
- Default: false
### --transfer-timeout

- When restarting PD or TiKV, the leader of the restarted node is migrated to other nodes first, and the migration process takes some time. You can set the maximum wait time (in seconds) by setting `-transfer-timeout`. After the timeout, the service can be restarted directly without waiting.
- Data type: `UINT`
- Default: 600

> **Note:**
>
> In the case of skipping the waiting and restarting directly, the service performance might jitter.
### --ignore-config-check

- After the binary files of components are deployed, the configurations of TiDB, TiKV, and PD components are checked using `<binary> --config-check <config-file>`. `<binary>` is the path of the deployed binary file. `<config-file>` is the configuration file generated based on the user configuration. If you want to skip this check, you can use this option.
- Data type: `BOOLEAN`
- Default: false
### -N, --node

- Specifies the nodes to be restarted. If not specified, all nodes are restarted. The value of this option is a comma-separated list of node IDs. You can get the node IDs from the first column of the cluster status table returned by the [`tiup cluster display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, all nodes are selected by default.

> **Note:**
>
> + If the `-R, --role` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are restarted.
> + If the `--skip-restart` option is specified, the `-N, --node` option is invalid.
### -R, --role

- Specifies the roles to be restarted. If not specified, all roles are restarted. The value of this option is a comma-separated list of node roles. The role is the second column of the [cluster status](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display) table.
- Data type: `STRINGS`
- If this option is not specified in the command, all roles are selected by default.

> **Note:**
>
> 1. If the `-N, --node` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are restarted.
> 2. If the `--skip-restart` option is specified, the `-R, --role` option is invalid.
### --skip-restart

The `tiup cluster reload` command performs two operations:

- Refreshes all node configurations
- Restarts the specified node

After you specify the `--skip-restart` option, it only refreshes the configuration without restarting any nodes, so that the refreshed configuration is not applied and does not take effect until the next restart of the corresponding service.

- Data type: `BOOLEAN`
- Default: false
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
### --pre-restart-script

> **Warning:**
>
> This option is experimental and is not recommended for production deployments.

- Runs a script before the reload.
- Data type: `STRINGS`
- This option specifies the path of a script to be run on the node that is to be reloaded. It does not take effect when `--skip-restart` is set to `true`.
### --post-restart-script

> **Warning:**
>
> This option is experimental and is not recommended for production deployments.

- Runs a script after the reload.
- Data type: `STRINGS`
- This option specifies the path of a script to be run after the reload of a node. It does not take effect when `--skip-restart` is set to `true`.
## Output

The execution log of the tiup-cluster.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
