# tiup dm enable command syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-enable.md`
- Source Title: `tiup dm enable`
- Source Heading Path: `tiup dm enable | tiup dm enable > Syntax | tiup dm enable > Options | tiup dm enable > Options > -N, --node | tiup dm enable > Options > -R, --role | tiup dm enable > Options > -h, --help | tiup dm enable > Output`
- Source Line Ranges: `5-48`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `service-auto-enable`, `systemctl`, `command-syntax`, `node-selection`, `role-selection`, `help-output`, `execution-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1024_c72057e018`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-enable.md#tiup-dm-enable`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a64db5db941d2a2817ac1e82fc861732ccd85e397999929bb2e7ce499c258b5b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-enable#tiup-dm-enable
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-enable.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, flags, and behavior of `tiup dm enable` for enabling DM cluster service auto-enabling with `systemctl enable <service>` after machine restart.
- Retrieval Keywords: tiup dm enable, tiup dm enable <cluster-name> [flags], systemctl enable <service>, auto-enabling of the cluster service, after a machine is restarted, -N --node, -R --role, -h --help, comma-separated list of node IDs, comma-separated list of node roles, tiup dm display, cluster status table, execution log of tiup-dm
- Follow-up Guidance: Node IDs come from the first column and node roles come from the second column of the cluster status table returned by `tiup dm display`, and when `-N, --node` and `-R, --role` are both specified, only services matching both are enabled.
- Classification Note: This is reference content because it defines the `tiup dm enable` command purpose, command syntax, option semantics, defaults, and output.

## Official Source Content

# tiup dm enable

The `tiup dm enable` command is used to set the auto-enabling of the cluster service after a machine is restarted. This command enables the auto-enabling of the service by executing `systemctl enable <service>` at the specified node.
## Syntax

```shell
tiup dm enable <cluster-name> [flags]
```

`<cluster-name>` is the cluster whose service auto-enabling is to be enabled.
## Options
### -N, --node

- Specifies the nodes whose service auto-enabling is to be enabled. The value of this option is a comma-separated list of node IDs. You can get the node IDs from the first column of the cluster status table returned by the [`tiup dm display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, the auto-enabling of all nodes is enabled by default.

> **Note:**
>
> If the `-R, --role` option is specified at the same time, the auto-enabling of services that match both the specifications of `-N, --node` and `-R, --role` is enabled.
### -R, --role

- Specifies the roles whose service auto-enabling is to be enabled. The value of this option is a comma-separated list of node roles. You can get the roles of nodes from the second column of the cluster status table returned by the [`tiup dm display`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display) command.
- Data type: `STRINGS`
- If this option is not specified in the command, the auto-enabling of all roles is enabled by default.

> **Note:**
>
> If the `-N, --node` option is specified at the same time, the auto-enabling of services that match both the specifications of `-N, --node` and `-R, --role` is enabled.
### -h, --help

Prints the help information.
## Output

the execution log of tiup-dm.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
