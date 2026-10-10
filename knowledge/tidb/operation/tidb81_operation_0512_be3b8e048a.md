# tiup dm scale-in command syntax options and output

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-scale-in.md`
- Source Title: `tiup dm scale-in`
- Source Heading Path: `tiup dm scale-in | tiup dm scale-in > Syntax | tiup dm scale-in > Options | tiup dm scale-in > Options > -N, --node | tiup dm scale-in > Options > --force | tiup dm scale-in > Options > -h, --help | tiup dm scale-in > Output`
- Source Line Ranges: `5-42`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `scale-in`, `node-removal`, `cluster-operations`, `command-syntax`, `command-options`, `force-removal`, `help-output`, `logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0512_be3b8e048a`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-scale-in.md#tiup-dm-scale-in`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9975626ca17779ac99159a6eb855a683fce1f0f579a1cd63f9918b5463e4a7dc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-scale-in#tiup-dm-scale-in
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-scale-in.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, required node option, force removal behavior, help flag, or output description of the `tiup dm scale-in` command.
- Retrieval Keywords: tiup dm scale-in, scale in the cluster, taking the service offline, removes the specified node from the cluster, deletes the remaining related files, tiup dm scale-in <cluster-name> [flags], -N, --node, specifies the nodes to be scaled in, split them by commas, --force, impossible to connect to the node through SSH, forcibly removed, -h, --help, The log of scaling in, cluster list
- Follow-up Guidance: If the cluster name is forgotten, the content says it can be checked with the `cluster list` command.
- Classification Note: This is classified as an operation chunk because it defines the `tiup dm scale-in` command usage, flags, and command output for removing DM cluster nodes.

## Official Source Content

# tiup dm scale-in

The `tiup dm scale-in` command is used to scale in the cluster. Scaling in the cluster means taking the service offline, which eventually removes the specified node from the cluster and deletes the remaining related files.
## Syntax

```shell
tiup dm scale-in <cluster-name> [flags]
```

`<cluster-name>`: the name of the cluster to operate on. If you forget the cluster name, you can check it with the [cluster list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-list) command.
## Options
### -N, --node

- Specifies the nodes to be scaled in. If you need to scale in multiple nodes, split them by commas.
- Data type: `STRINGS`
- Default: no. This option is mandatory and the value must be not null.
### --force

- In some cases, some scale-in nodes in the cluster have been down, making it impossible to connect to the node through SSH for operation. At this time, you can use the `--force` option to remove these nodes from the cluster.
- Data type: `BOOLEAN`
- Default: false. If this option is not specified in the command, the specified nodes are not forcibly removed.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
## Output

The log of scaling in.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
