# tiup cluster meta restore command syntax options and output

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-meta-restore.md`
- Source Title: `tiup cluster meta restore`
- Source Heading Path: `tiup cluster meta restore | tiup cluster meta restore > Syntax | tiup cluster meta restore > Options | tiup cluster meta restore > Options > -h, --help | tiup cluster meta restore > Output`
- Source Line Ranges: `5-35`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `meta-file`, `restore`, `command-syntax`, `flags`, `help`, `output`, `backup-file`, `overwrite-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0067_3c0e7df448`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-meta-restore.md#tiup-cluster-meta-restore`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `655cf60dd13d54c82e494a22bc4c3912dedbd21053226dae94fa3249c871efbe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-meta-restore#tiup-cluster-meta-restore
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-meta-restore.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, arguments, help flag, overwrite note, or output description of the TiUP meta restore command.
- Retrieval Keywords: tiup cluster meta restore, tiup cluster meta restore <cluster-name> <backup-file> [flags], <cluster-name>, <backup-file>, TiUP meta backup file, meta file restore, overwrite the current meta file, restore the meta file only when it is lost, -h, --help, Prints the help information, execution logs of tiup-cluster
- Follow-up Guidance: The source states that the restore operation overwrites the current meta file and recommends restoring the meta file only when it is lost.
- Classification Note: This is classified as recovery for the self-managed TiUP component because it describes restoring the TiUP meta file from a backup file.

## Official Source Content

# tiup cluster meta restore

To restore the TiUP meta file, you can use the `tiup cluster meta restore` command to restore from the backup file.
## Syntax

```shell
tiup cluster meta restore <cluster-name> <backup-file> [flags]
```

- `<cluster-name>` is the name of the cluster to be operated on.
- `<backup-file>` is the path to the TiUP meta backup file.

> **Note:**
>
> The restore operation overwrites the current meta file. It is recommended to restore the meta file only when it is lost.
## Options
### -h, --help

- Prints the help information.
- Data type: `Boolean`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Output

The execution logs of tiup-cluster.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
