# tiup cluster enable command syntax options and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-enable.md`
- Source Title: `tiup cluster enable`
- Source Heading Path: `tiup cluster enable | tiup cluster enable > Syntax | tiup cluster enable > Options | tiup cluster enable > Options > -N, --node | tiup cluster enable > Options > -R, --role | tiup cluster enable > Options > -h, --help | tiup cluster enable > Output`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `command syntax`, `systemctl enable`, `service startup order`, `node selection`, `role selection`, `help option`, `execution log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1006_ce14609efb`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-enable.md#tiup-cluster-enable`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a040cfcc3207495be74cb3825b85d1466e64a5b31795dc1961c619f32d667b5f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-enable#tiup-cluster-enable
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-enable.md

## Retrieval Guidance

- Use When: Use this when looking up how to enable cluster service auto-enabling after machine restart with the TiUP command, including syntax, node or role filtering, help output, and startup-order notes.
- Retrieval Keywords: tiup cluster enable, systemctl enable <service>, auto-enabling of the cluster service, tiup cluster enable <cluster-name> [flags], -N, --node, -R, --role, -h, --help, tiup cluster display, cluster status table, node IDs, node roles, execution log of the tiup-cluster, service startup order, TiKV is started first but PD is not started, systemd gives up
- Follow-up Guidance: The source notes that when all clusters are shut down and restarted, service startup follows the node operating system startup order, and an incorrect order can leave the restarted cluster unable to provide services.
- Classification Note: This is reference content because it defines the purpose, syntax, options, notes, and output of the `tiup cluster enable` command.

## Official Source Content

# tiup cluster enable

The `tiup cluster enable` command is used to set the auto-enabling of the cluster service after a machine is restarted. This command enables the auto-enabling of the service by executing `systemctl enable <service>` at the specified node.

> **Note:**
>
> When all clusters are shut down and restarted, the order of service startup is determined by the node's operating system startup order. When the restart order is incorrect, in some cases, the restarted cluster still cannot provide services. For example, if TiKV is started first but PD is not started, systemd gives up if TiKV is restarted multiple times while PD is not found.
## Syntax

```shell
tiup cluster enable <cluster-name> [flags]
```

`<cluster-name>`: the cluster whose service auto-enabling is to be enabled.
## Options
### -N, --node

- Specifies the nodes whose service auto-enabling is to be enabled. The value of this option is a comma-separated list of node IDs. You can get the node IDs from the first column of the cluster status table returned by the [`tiup cluster display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, the auto-enabling of all nodes is enabled by default.

> **Note:**
>
> If the `-R, --role` option is specified at the same time, the auto-enabling of services that match both the specifications of `-N, --node` and `-R, --role` is enabled.
### -R, --role

- Specifies the roles whose service auto-enabling is to be enabled. The value of this option is a comma-separated list of node roles. You can get the roles of nodes from the second column of the cluster status table returned by the [`tiup cluster display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, the auto-enabling of all roles is enabled by default.

> **Note:**
>
> If the `-N, --node` option is specified at the same time, the auto-enabling of services that match both the specifications of `-N, --node` and `-R, --role` is enabled.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Output

The execution log of the tiup-cluster.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
