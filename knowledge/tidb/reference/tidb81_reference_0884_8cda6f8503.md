# ticloud serverless export cancel command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-export-cancel.md`
- Source Title: `ticloud serverless export cancel`
- Source Heading Path: `ticloud serverless export cancel | ticloud serverless export cancel > Examples | ticloud serverless export cancel > Flags | ticloud serverless export cancel > Inherited flags | ticloud serverless export cancel > Feedback`
- Source Line Ranges: `5-49`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `export`, `cancel`, `interactive-mode`, `non-interactive-mode`, `flags`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0884_8cda6f8503`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-export-cancel.md#ticloud-serverless-export-cancel`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3c8c5d3ae07a84c5bcfe10294b48c2c9584981df40f14f60322b725c2cf9f7ca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-export-cancel#ticloud-serverless-export-cancel
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-export-cancel.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI syntax, examples, and flags for canceling a Serverless data export task with `ticloud serverless export cancel`.
- Retrieval Keywords: ticloud serverless export cancel, Cancel a data export task, Cancel an export task in interactive mode, Cancel an export task in non-interactive mode, -c --cluster-id, -e --export-id, --force, --no-color, -P --profile, -D --debug, user profile
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is a command reference for the cloud CLI because the content defines the `ticloud serverless export cancel` command, shows example invocations, and lists command-specific and inherited flags.

## Official Source Content

# ticloud serverless export cancel

Cancel a data export task:

```shell
ticloud serverless export cancel [flags]
```
## Examples

Cancel an export task in interactive mode:

```shell
ticloud serverless export cancel
```

Cancel an export task in non-interactive mode:

```shell
ticloud serverless export cancel -c <cluster-id> -e <export-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                  | Required | Note                                                 |
|-------------------------|----------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster. | Yes      | Only works in non-interactive mode.                  |
| -e, --export-id string  | Specifies the ID of the export task.       | Yes      | Only works in non-interactive mode.                  |
| --force                 | Cancels an export task without confirmation        | No       | Works in both non-interactive and interactive modes. |
| -h, --help              | Shows help information for this command.           | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
