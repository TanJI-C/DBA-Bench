# TiUP telemetry command overview and subcommands

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-telemetry.md`
- Source Title: `tiup telemetry`
- Source Heading Path: `tiup telemetry | tiup telemetry > Syntax | tiup telemetry > Commands | tiup telemetry > Commands > status | tiup telemetry > Commands > reset | tiup telemetry > Commands > enable | tiup telemetry > Commands > disable`
- Source Line Ranges: `5-53`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `telemetry`, `cli`, `syntax`, `status`, `reset`, `enable`, `disable`, `usage-data`, `identifiers`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0997_8f771777de`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-telemetry.md#tiup-telemetry`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7aefa5e181c3459286c53fccbbf38ed863b9372d673f48d8cb578e50088c489b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-telemetry#tiup-telemetry
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-telemetry.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about the `tiup telemetry` command, its `status`, `reset`, `enable`, or `disable` subcommands, or what telemetry information TiUP shares or does not share.
- Retrieval Keywords: tiup telemetry, tiup telemetry status, tiup telemetry reset, tiup telemetry enable, tiup telemetry disable, telemetry identifiers, uuid, status enable disable, usage information shared with PingCAP, execution status of the TiUP command, target machine hardware information, component version number, modified deployment configuration name, accurate name of the cluster, cluster topology, cluster configuration file, Starting from v1.11.3 telemetry is disabled by default
- Follow-up Guidance: The source states that `tiup telemetry status` outputs `status` and `uuid`, and that `tiup telemetry reset` replaces the current telemetry identifier with a new random identifier.
- Classification Note: This is a TiUP CLI reference chunk because it defines the `tiup telemetry <command>` syntax, lists supported subcommands, and describes the telemetry data scope and defaults mentioned in the page.

## Official Source Content

# tiup telemetry

Starting from v1.11.3, the telemetry is disabled by default in newly deployed TiUP, and usage information is not collected and shared with PingCAP. In versions earlier than v1.11.3, the telemetry is enabled by default in TiUP, and usage information is collected and shared with PingCAP to improve the product.

When TiUP telemetry is enabled, usage information is shared with PingCAP when TiUP commands are executed, including (but not limited to):

- Randomly generated telemetry identifiers.
- The execution status of the TiUP command, such as whether the command execution is successful and the duration of command execution.
- Situations using TiUP for deployment, such as target machine hardware information, component version number, and modified deployment configuration name.

The information below is not shared:

- The accurate name of the cluster
- The cluster topology
- The cluster configuration file

TiUP uses the `tiup telemetry` command to control telemetry.
## Syntax

```shell
tiup telemetry <command>
```

`<command>` stands for sub-commands. For the list of supported sub-commands, refer to the commands section below.
## Commands
### status

The `tiup telemetry status` command is used to view the current telemetry settings and output the following information:

- `status`: specifies enabling or disabling the telemetry `(enable|disable)`.
- `uuid`: specifies the randomly generated telemetry identifiers.
### reset

The `tiup telemetry reset` command is used to reset the current telemetry identifier and replaces it with a new random identifier.
### enable

The `tiup telemetry enable` command is used to enable the telemetry.
### disable

The `tiup telemetry disable` command is used to disable the telemetry.

[<< Back to the previous page - TiUP Reference command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-reference#command-list)
