# TiDB Cloud Serverless branch list command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-branch-list.md`
- Source Title: `ticloud serverless branch list`
- Source Heading Path: `ticloud serverless branch list | ticloud serverless branch list > Examples | ticloud serverless branch list > Flags | ticloud serverless branch list > Inherited flags | ticloud serverless branch list > Feedback`
- Source Line Ranges: `5-60`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `serverless`, `branch`, `list`, `flags`, `interactive-mode`, `non-interactive-mode`, `json-output`, `profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0860_08c9cea3fd`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-branch-list.md#ticloud-serverless-branch-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `56e24021e5e2f2d6fecbe6b09010a0390ad7daa8d1fe49ebdd9cc369c01c2468`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-branch-list#ticloud-serverless-branch-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-branch-list.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the TiDB Cloud CLI command syntax, examples, flags, alias, or output options for listing branches of a TiDB Cloud Serverless cluster.
- Retrieval Keywords: ticloud serverless branch list, ticloud serverless branch ls, List all branches for a TiDB Cloud Serverless cluster, ticloud serverless branch list <cluster-id> [flags], -c, --cluster-id, -o, --output, human, json, interactive mode, non-interactive mode, --no-color, -P, --profile, -D, --debug
- Follow-up Guidance: The source also points to the TiDB Cloud CLI issue tracker for questions, suggestions, and contributions.
- Classification Note: This is reference content because it defines the command, alias, examples, flags, inherited flags, and output behavior for the TiDB Cloud Serverless branch list CLI command.

## Official Source Content

# ticloud serverless branch list

List all branches for a TiDB Cloud Serverless cluster:

```shell
ticloud serverless branch list <cluster-id> [flags]
```

Or use the following alias command:

```shell
ticloud serverless branch ls <cluster-id> [flags]
```
## Examples

List all branches for a TiDB Cloud Serverless cluster in interactive mode:

```shell
ticloud serverless branch list
```

List all branches for a specific TiDB Cloud Serverless cluster in non-interactive mode:

```shell
ticloud serverless branch list -c <cluster-id>
```

List all branches for a specific TiDB Cloud Serverless cluster in the JSON format:

```shell
ticloud serverless branch list <cluster-id> -o json
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                                                                              | Required | Note                                                 |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.                                                                                                    | Yes      | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command.                                                                                       | No       | Works in both non-interactive and interactive modes. |
| -o, --output string     | Specifies the output format (`human` by default). Valid values are `human` or `json`. To get a complete result, use the `json` format. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
