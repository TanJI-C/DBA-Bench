# tiup cluster replay command usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-replay.md`
- Source Title: `tiup cluster replay`
- Source Heading Path: `tiup cluster replay | tiup cluster replay > Syntax | tiup cluster replay > Option | tiup cluster replay > Option > -h, --help | tiup cluster replay > Output`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `command syntax`, `audit id`, `retry operations`, `failed operations`, `help option`, `command output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1011_e86bd6685c`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-replay.md#tiup-cluster-replay`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b404e8ea53f4386b903c0a96f6f430cfafe686fa6c414dc0cace6102c9f95a8e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-replay#tiup-cluster-replay
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-replay.md

## Retrieval Guidance

- Use When: Use this when looking for the TiUP command that retries failed cluster operations by reusing an existing audit record and skipping successfully performed steps.
- Retrieval Keywords: tiup cluster replay, tiup cluster replay <audit-id> [flags], audit-id, tiup cluster audit, retry the failed commands, skip the successfully performed steps, cluster operation such as upgrade or restart, -h, --help, output of the command corresponding to <audit-id>
- Follow-up Guidance: You can view the historical commands and their audit-ids using the tiup cluster audit command.
- Classification Note: This is reference content because it defines the syntax, option, parameter meaning, and output for the tiup cluster replay command.

## Official Source Content

# tiup cluster replay

When you perform a cluster operation such as upgrade or restart, the operation might fail due to cluster environment issues. If you re-perform the operation, you need to perform all the steps from the very beginning. If the cluster is large, re-performing these steps will take a long time. In this case, you can use the `tiup cluster replay` command to retry the failed commands and skip the successfully performed steps.
## Syntax

```shell
tiup cluster replay <audit-id> [flags]
```

- `<audit-id>`: the `audit-id` of the command to be retried. You can view the historical commands and their `audit-id`s using the [`tiup cluster audit`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-audit) command.
## Option
### -h, --help

Prints the help information.
## Output

The output of the command corresponding to `<audit-id>`.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
