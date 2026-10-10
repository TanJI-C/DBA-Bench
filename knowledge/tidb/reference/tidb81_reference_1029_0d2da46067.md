# tiup dm replay command syntax options and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-replay.md`
- Source Title: `tiup dm replay`
- Source Heading Path: `tiup dm replay | tiup dm replay > Syntax | tiup dm replay > Option | tiup dm replay > Option > -h, --help | tiup dm replay > Output`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `command-line`, `retry`, `audit-id`, `failed-operations`, `help`, `output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1029_0d2da46067`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-replay.md#tiup-dm-replay`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b0e66d2240ebebca69d5aa3061e80b59bc1608d84117bf89c5d9a3f626e9468e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-replay#tiup-dm-replay
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-replay.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, purpose, options, or output of the `tiup dm replay` command for retrying failed DM cluster operations with an `audit-id`.
- Retrieval Keywords: tiup dm replay, tiup dm replay <audit-id> [flags], audit-id, tiup dm audit, retry the failed commands, skip the successfully performed steps, -h, --help, prints the help information, output of the command corresponding to <audit-id>, failed operations, upgrade, restart
- Follow-up Guidance: The content states that historical commands and their `audit-id`s can be viewed using the `tiup dm audit` command.
- Classification Note: This is reference content because it defines the `tiup dm replay` command syntax, the `-h, --help` option, and the command output description.

## Official Source Content

# tiup dm replay

When you perform a cluster operation such as upgrade or restart, the operation might fail due to cluster environment issues. If you re-perform the operation, you need to perform all the steps from the very beginning. If the cluster is large, re-performing these steps will take a long time. In this case, you can use the `tiup dm replay` command to retry the failed commands and skip the successfully performed steps.
## Syntax

```shell
tiup dm replay <audit-id> [flags]
```

- `<audit-id>`: the `audit-id` of the command to be retried. You can view the historical commands and their `audit-id`s using the [`tiup dm audit`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-audit) command.
## Option
### -h, --help

Prints the help information.
## Output

The output of the command corresponding to `<audit-id>`.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
