# tiup dm audit syntax, help option, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-audit.md`
- Source Title: `tiup dm audit`
- Source Heading Path: `tiup dm audit | tiup dm audit > Syntax | tiup dm audit > Option | tiup dm audit > Option > -h, --help | tiup dm audit > Output`
- Source Line Ranges: `5-35`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `audit`, `command-history`, `execution-log`, `syntax`, `help`, `output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1019_d9ba66d5a0`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-audit.md#tiup-dm-audit`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d31f5b658d4000cef8a16b84e29d106121fe814524a43c3812863d1f1a43e8b1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-audit#tiup-dm-audit
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-audit.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the syntax, help flag, or output behavior of `tiup dm audit` for viewing historical commands on all clusters or the execution log for a specific `audit-id`.
- Retrieval Keywords: tiup dm audit, tiup dm audit [audit-id] [flags], audit-id, historical commands executed on all clusters, execution log, reverse chronological order, -h, --help, ID Time Command output
- Follow-up Guidance: If `[audit-id]` is not specified, the output is a table whose first column is the `audit-id`; if `[audit-id]` is specified, the corresponding execution log is output.
- Classification Note: This is reference content because it defines the `tiup dm audit` command syntax, the `-h, --help` option, and the exact output fields and behavior.

## Official Source Content

# tiup dm audit

The `tiup dm audit` command is used to view historical commands executed on all clusters and the execution log of each command.
## Syntax

```shell
tiup dm audit [audit-id] [flags]
```

- If you do not fill in the `[audit-id]`, the table of operation records is output in reverse chronological order. The first column is the `audit-id`.
- If you fill in the `[audit-id]`, the execution log of the specified `audit-id` is checked.
## Option
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
## Output

- If `[audit-id]` is specified, the corresponding execution log is output.
- If `[audit-id]` is not specified, a table with the following fields is output:
    - ID: the `audit-id` corresponding to this record
    - Time: the execution time of the command corresponding to the record
    - Command: the command corresponding to the record

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
