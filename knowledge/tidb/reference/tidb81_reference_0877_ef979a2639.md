# ticloud serverless import list command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-import-list.md`
- Source Title: `ticloud serverless import list`
- Source Heading Path: `ticloud serverless import list | ticloud serverless import list > Examples | ticloud serverless import list > Flags | ticloud serverless import list > Inherited flags | ticloud serverless import list > Feedback`
- Source Line Ranges: `5-60`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `import`, `list`, `flags`, `interactive-mode`, `non-interactive-mode`, `json-output`, `profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0877_ef979a2639`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-import-list.md#ticloud-serverless-import-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `820207be4ae9d1f71eb31bef0bb83557bd7b997829643059c6d14ed4c216fc01`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-import-list#ticloud-serverless-import-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-import-list.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the TiDB Cloud CLI command syntax, alias, flags, or examples for listing data import tasks in serverless import.
- Retrieval Keywords: ticloud serverless import list, ticloud serverless import ls, List data import tasks, --cluster-id, --output json, interactive mode, non-interactive mode, human or json, To get a complete result, use the json format, --no-color, --profile, --debug
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue tracker for questions, suggestions, and contributions.
- Classification Note: This is a command reference for the cloud CLI because the content defines command usage, examples, command-specific flags, and inherited flags for ticloud serverless import list.

## Official Source Content

# ticloud serverless import list

List data import tasks:

```shell
ticloud serverless import list [flags]
```

Or use the following alias command:

```shell
ticloud serverless import ls [flags]
```
## Examples

List import tasks in interactive mode:

```shell
ticloud serverless import list
```

List import tasks in non-interactive mode:

```shell
ticloud serverless import list --cluster-id <cluster-id>
```

List import tasks for a specified cluster in the JSON format:

```shell
ticloud serverless import list --cluster-id <cluster-id> --output json
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                                                                              | Required | Note                                                 |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.                                                                                                               | Yes      | Only works in non-interactive mode.                  |
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
