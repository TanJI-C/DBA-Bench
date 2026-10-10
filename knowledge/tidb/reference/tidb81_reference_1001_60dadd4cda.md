# tiup cluster audit syntax options and outputs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-audit.md`
- Source Title: `tiup cluster audit`
- Source Heading Path: `tiup cluster audit | tiup cluster audit > Syntax | tiup cluster audit > Option | tiup cluster audit > Option > -h, --help | tiup cluster audit > Outputs`
- Source Line Ranges: `5-35`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `audit`, `command-history`, `execution-log`, `syntax`, `help-option`, `outputs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1001_60dadd4cda`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-audit.md#tiup-cluster-audit`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ef5d92fbe5c99da37a24d04eade7dd9cf3a8bc564236c61877fc81d6795ea4b0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-audit#tiup-cluster-audit
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-audit.md

## Retrieval Guidance

- Use When: Use this when looking up how `tiup cluster audit` shows command history, how to inspect the execution log for a specific `audit-id`, or what output fields the command returns.
- Retrieval Keywords: tiup cluster audit, audit-id, execution log, history, operation records, reverse chronological order, ID, Time, Command, -h, --help, tiup cluster audit [audit-id] [flags]
- Follow-up Guidance: If `[audit-id]` is not specified, the output is a table in reverse chronological order whose first column is the `audit-id`; if `[audit-id]` is specified, the corresponding execution log is output.
- Classification Note: This is reference content because it defines the command syntax, the `-h, --help` option, and the exact outputs of `tiup cluster audit`.

## Official Source Content

# tiup cluster audit

The `tiup cluster audit` command is used to view commands executed on all clusters in the history and the execution log of each command.
## Syntax

```shell
tiup cluster audit [audit-id] [flags]
```

- If you do not fill in the `[audit-id]`, the table of operation records is output in reverse chronological order. The first column is the `audit-id`.
- If you fill in the `[audit-id]`, it means checking the execution log of the specified `audit-id`.
## Option
### -h, --help

- Prints the help information.
- Data type: `Boolean`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Outputs

- If `[audit-id]` is specified, the corresponding execution log is output.
- If `[audit-id]` is not specified, a table with the following fields is output:
    - ID: the `audit-id` corresponding to the record
    - Time: the execution time of the command corresponding to the record
    - Command: the command corresponding to the record

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
