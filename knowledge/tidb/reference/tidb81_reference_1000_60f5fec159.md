# TiUP cluster audit cleanup command syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-audit-cleanup.md`
- Source Title: `tiup cluster audit cleanup`
- Source Heading Path: `tiup cluster audit cleanup | tiup cluster audit cleanup > Syntax | tiup cluster audit cleanup > Options | tiup cluster audit cleanup > Options > --retain-days | tiup cluster audit cleanup > Options > -h, --help | tiup cluster audit cleanup > Output`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `command-line`, `audit-log`, `log-cleanup`, `syntax`, `flags`, `retention`, `help`, `output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1000_60f5fec159`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-audit-cleanup.md#tiup-cluster-audit-cleanup`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c0c666fed64e3cad748fb60ef64bd0d2ef2be28114079d418c74170206a6b934`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-audit-cleanup#tiup-cluster-audit-cleanup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-audit-cleanup.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, flags, retention behavior, or output of the `tiup cluster audit cleanup` command for TiUP cluster audit logs.
- Retrieval Keywords: tiup cluster audit cleanup, Syntax, tiup cluster audit cleanup [flags], --retain-days, retain days, logs retained, 60 days, -h, --help, clean audit log successfully, audit cleanup command
- Follow-up Guidance: The source also points back to the TiUP Cluster command list page.
- Classification Note: This is classified as reference content because it lists the command syntax, option definitions, default values, and command output for `tiup cluster audit cleanup`.

## Official Source Content

# tiup cluster audit cleanup

The `tiup cluster audit cleanup` command is used to clean up the logs generated in executing the `tiup cluster`command.
## Syntax

```shell
tiup cluster audit cleanup [flags]
```
## Options
### --retain-days

- Specifies the days for which logs are retained.
- Data type: `INT`
- Default value: `60`, in the unit of day.
- By default, logs generated within the last 60 days are retained, which means logs generated before 60 days are removed.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default value: `false`
- To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Output

```shell
clean audit log successfully
```

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
