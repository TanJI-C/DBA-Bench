# tiup clean command syntax, --all option, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-clean.md`
- Source Title: `tiup clean`
- Source Heading Path: `tiup clean | tiup clean > Syntax | tiup clean > Option | tiup clean > Option > --all | tiup clean > Output`
- Source Line Ranges: `5-32`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `command syntax`, `cleanup`, `operation records`, `flags`, `command output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0980_313f3c3811`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-clean.md#tiup-clean`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7f5b30756d9430c9859a540c86060ac1fa7d9d0a45749059ada727302cf85f5a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-clean#tiup-clean
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-clean.md

## Retrieval Guidance

- Use When: Use this when looking for the syntax, --all behavior, or output format of the tiup clean command that clears data generated during component operation.
- Retrieval Keywords: tiup clean, tiup clean [name] [flags], --all, clear data generated during component operation, clears all operation records, Name field output by the status command, Clean instance of `%s`, directory: %s
- Follow-up Guidance: If [name] is omitted, the official content says you must add the --all option, and [name] is the Name field output by the status command.
- Classification Note: This is reference content because it defines command syntax, a flag, the meaning of the name argument, and the exact command output string for TiUP.

## Official Source Content

# tiup clean

The `tiup clean` command is used to clear the data generated during component operation.
## Syntax

```shell
tiup clean [name] [flags]
```

The value of `[name]` is the `Name` field output by the [`status` command](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-status). If `[name]` is omitted, you must add the `--all` option in the `tiup clean` command.
## Option
### --all

- Clears all operation records
- Data type: Boolean
- Default: false
## Output

```
Clean instance of `%s`, directory: %s
```

[<< Back to the previous page - TiUP Reference command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-reference#command-list)
