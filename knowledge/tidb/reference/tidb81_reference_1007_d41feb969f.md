# tiup cluster help command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-help.md`
- Source Title: `tiup cluster help`
- Source Heading Path: `tiup cluster help | tiup cluster help > Syntax | tiup cluster help > Syntax > -h, --help | tiup cluster help > Output`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `help`, `syntax`, `flag`, `output`, `command`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1007_d41feb969f`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-help.md#tiup-cluster-help`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ff4a8315f759c4da64444220664431cd57b8c86a814ffb1f3bca52cc1f3a000d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-help#tiup-cluster-help
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-help.md

## Retrieval Guidance

- Use When: Use this chunk when you need the command reference for viewing TiUP Cluster CLI help information or the equivalence between the help command and the --help option.
- Retrieval Keywords: tiup cluster help, tiup cluster help [command] [flags], tiup cluster <command> --help, -h, --help, help information of tiup-cluster, command list
- Follow-up Guidance: If [command] is not specified, the help information of tiup-cluster is viewed.
- Classification Note: This is reference content because it defines the syntax, flag, and output of the tiup cluster help command.

## Official Source Content

# tiup cluster help

tiup-cluster provides a wealth of help information for users in the command line interface. You can obtain it via the `help` command or the `--help` option. `tiup cluster help <command>` is basically equivalent to `tiup cluster <command> --help`.
## Syntax

```shell
tiup cluster help [command] [flags]
```

`[command]` is used to specify the help information of which command that users need to view. If it is not specified, the help information of tiup-cluster is viewed.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
## Output

The help information of the `[command]` or tiup-cluster.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
