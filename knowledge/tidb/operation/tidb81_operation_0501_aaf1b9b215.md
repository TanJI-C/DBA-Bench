# tiup cluster meta backup command syntax options and output

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-meta-backup.md`
- Source Title: `tiup cluster meta backup`
- Source Heading Path: `tiup cluster meta backup | tiup cluster meta backup > Syntax | tiup cluster meta backup > Options | tiup cluster meta backup > Options > --file (string, defaults to the current directory) | tiup cluster meta backup > Options > -h, --help | tiup cluster meta backup > Output`
- Source Line Ranges: `5-34`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `meta-backup`, `cluster-management`, `command-syntax`, `options`, `help`, `output`, `backup-directory`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0501_aaf1b9b215`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-meta-backup.md#tiup-cluster-meta-backup`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6eac7400bd1e808a85a1a717c00f7cc398bdb960cdea7207a9041fca76c4e6e6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-meta-backup#tiup-cluster-meta-backup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-meta-backup.md

## Retrieval Guidance

- Use When: Use this content when looking for the TiUP command syntax, options, or output for backing up a cluster's TiUP meta file used for operation and maintenance.
- Retrieval Keywords: tiup cluster meta backup, tiup cluster meta backup <cluster-name> [flags], --file, target directory to store the TiUP meta backup file, -h, --help, execution logs of tiup-cluster, TiUP meta file, tiup cluster list
- Follow-up Guidance: If the cluster name is unknown, the content says you can check it using the `tiup cluster list` command.
- Classification Note: This is classified as an operation topic because the official content describes a TiUP cluster management command, its flags, and its execution output for meta backup.

## Official Source Content

# tiup cluster meta backup

The TiUP meta file is used for cluster operation and maintenance (OM). If this file is lost, you cannot use TiUP to manage the cluster. To avoid this situation, you can use the `tiup cluster meta backup` command to back up the TiUP meta file regularly.
## Syntax

```shell
tiup cluster meta backup <cluster-name> [flags]
```

`<cluster-name>` is the name of the cluster to be operated on. If you forget the cluster name, you can check it using the [`tiup cluster list`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-list) command.
## Options
### --file (string, defaults to the current directory)

Specifies the target directory to store the TiUP meta backup file.
### -h, --help

- Prints the help information.
- Data type: `Boolean`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Output

The execution logs of tiup-cluster.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
