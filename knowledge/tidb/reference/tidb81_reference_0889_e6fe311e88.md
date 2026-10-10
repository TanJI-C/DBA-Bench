# TiDB Cloud Serverless export list command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-export-list.md`
- Source Title: `ticloud serverless export list`
- Source Heading Path: `ticloud serverless export list | ticloud serverless export list > Examples | ticloud serverless export list > Flags | ticloud serverless export list > Inherited flags | ticloud serverless export list > Feedback`
- Source Line Ranges: `5-60`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `export`, `list`, `serverless`, `flags`, `examples`, `profiles`, `debug`, `output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0889_e6fe311e88`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-export-list.md#ticloud-serverless-export-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9e0e970565ee2c81c9d31da351f31f2c7b6b4592f0a526a245135feb41c5989d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-export-list#ticloud-serverless-export-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-export-list.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the TiDB Cloud CLI command syntax, alias, flags, or examples for listing data export tasks of TiDB Cloud Serverless clusters.
- Retrieval Keywords: ticloud serverless export list, ticloud serverless export ls, List data export tasks of TiDB Cloud Serverless clusters, -c --cluster-id, -o --output, human, json, --no-color, -P --profile, -D --debug, interactive mode, non-interactive mode
- Follow-up Guidance: The source also points to the TiDB Cloud CLI feedback issue link and mentions the user profile reference for the --profile flag.
- Classification Note: This is a cloud reference command page for the TiDB Cloud CLI that documents usage, examples, command flags, and inherited flags for serverless export list.

## Official Source Content

# ticloud serverless export list

List data export tasks of TiDB Cloud Serverless clusters:

```shell
ticloud serverless export list [flags]
```

Or use the following alias command:

```shell
ticloud serverless export ls [flags]
```
## Examples

List all export tasks in interactive mode:

```shell
ticloud serverless export list
```

List export tasks for a specified cluster in non-interactive mode:

```shell
ticloud serverless export list -c <cluster-id>
```

List export tasks for a specified cluster in the JSON format in non-interactive mode:

```shell
ticloud serverless export list -c <cluster-id> -o json
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                                                                              | Required | Note                                                 |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.                                                                                 | Yes      | Only works in non-interactive mode.                  |
| -o, --output string     | Specifies the output format (`human` by default). Valid values are `human` or `json`. To get a complete result, use the `json` format. | No       | Works in both non-interactive and interactive modes. |
| -h, --help              | Shows help information for this command.                                                                                        | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
