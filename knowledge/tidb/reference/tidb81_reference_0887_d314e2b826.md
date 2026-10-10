# TiDB Cloud Serverless export describe command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-export-describe.md`
- Source Title: `ticloud serverless export describe`
- Source Heading Path: `ticloud serverless export describe | ticloud serverless export describe > Examples | ticloud serverless export describe > Flags | ticloud serverless export describe > Inherited flags | ticloud serverless export describe > Feedback`
- Source Line Ranges: `5-54`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `serverless`, `export`, `describe`, `flags`, `interactive-mode`, `non-interactive-mode`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0887_d314e2b826`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-export-describe.md#ticloud-serverless-export-describe`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `33d062f23f0070028584f126674206197f3924f46cc9ba1b2ab7a23ef9baea2f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-export-describe#ticloud-serverless-export-describe
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-export-describe.md

## Retrieval Guidance

- Use When: Use this when looking up the TiDB Cloud CLI command syntax, alias, examples, and flags for describing export information of a TiDB Cloud Serverless cluster.
- Retrieval Keywords: ticloud serverless export describe, ticloud serverless export get, Get the export information of a TiDB Cloud Serverless cluster, interactive mode, non-interactive mode, -c --cluster-id, -e --export-id, --no-color, -P --profile, -D --debug, user profile, help information
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is reference content because it lists the command purpose, alias, usage examples, required flags, and inherited flags for the cloud CLI command.

## Official Source Content

# ticloud serverless export describe

Get the export information of a TiDB Cloud Serverless cluster:

```shell
ticloud serverless export describe [flags]
```

Or use the following alias command:

```shell
ticloud serverless export get [flags]
```
## Examples

Get the export information in interactive mode:

```shell
ticloud serverless export describe
```

Get the export information in non-interactive mode:

```shell
ticloud serverless export describe -c <cluster-id> -e <export-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                  | Required | Note                                                 |
|-------------------------|----------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster. | Yes      | Only works in non-interactive mode.                  |
| -e, --export-id string  | Specifies the ID of the export task.         | Yes      | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command.           | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
