# tiup dm help command syntax and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-help.md`
- Source Title: `tiup dm help`
- Source Heading Path: `tiup dm help | tiup dm help > Syntax | tiup dm help > Syntax > -h, --help | tiup dm help > Output`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `help`, `cli`, `syntax`, `flags`, `output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1025_d28b32382c`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-help.md#tiup-dm-help`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `63ccfdc4e870ca7ba8836bef28af4142fde71f56dcd271bbf619fe2a6dec4edc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-help#tiup-dm-help
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-help.md

## Retrieval Guidance

- Use When: Use this when looking for the syntax, flags, or output of the TiUP DM help command or when confirming how to view help for a specific tiup dm subcommand.
- Retrieval Keywords: tiup dm help, tiup dm help [command] [flags], tiup dm <command> --help, -h, --help, tiup-dm help information, help information of [command] or tiup-dm
- Follow-up Guidance: The source states that `tiup dm help <command>` is equivalent to `tiup dm <command> --help`.
- Classification Note: This is reference content because it defines the `tiup dm help` command syntax, the `-h, --help` flag, and the command output description.

## Official Source Content

# tiup dm help

tiup-dm command-line interface provides users with a wealth of help information. You can view it via the `help` command or the `--help` option. Basically, `tiup dm help <command>` is equivalent to `tiup dm <command> --help`.
## Syntax

```shell
tiup dm help [command] [flags]
```

`[command]` is used to specify the help information of which command that users need to view. If it is not specified, the help information of `tiup-dm` is viewed.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
## Output

The help information of `[command]` or `tiup-dm`.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
