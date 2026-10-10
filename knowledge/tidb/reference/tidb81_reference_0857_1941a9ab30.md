# ticloud serverless branch create command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-branch-create.md`
- Source Title: `ticloud serverless branch create`
- Source Heading Path: `ticloud serverless branch create | ticloud serverless branch create > Examples | ticloud serverless branch create > Flags | ticloud serverless branch create > Inherited flags | ticloud serverless branch create > Feedback`
- Source Line Ranges: `5-56`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `serverless`, `branch`, `create`, `flags`, `interactive-mode`, `non-interactive-mode`, `examples`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0857_1941a9ab30`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-branch-create.md#ticloud-serverless-branch-create`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ab732eed9981b151add846a305509df4292e65a168404da7f6b75b58f416d758`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-branch-create#ticloud-serverless-branch-create
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-branch-create.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI syntax, examples, and flags for creating a branch in a TiDB Cloud Serverless cluster with `ticloud serverless branch create`.
- Retrieval Keywords: ticloud serverless branch create, Create a branch for a TiDB Cloud Serverless cluster, --cluster-id, --display-name, --parent-id, --parent-timestamp, RFC3339 format, interactive mode, non-interactive mode, --profile, --debug, --no-color
- Follow-up Guidance: The source also points to the TiDB Cloud CLI issue tracker for questions or suggestions.
- Classification Note: This is reference content because it lists the command syntax, examples, required flags, inherited flags, and mode-specific notes for `ticloud serverless branch create`.

## Official Source Content

# ticloud serverless branch create

Create a [branch](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-overview) for a TiDB Cloud Serverless cluster:

```shell
ticloud serverless branch create [flags]
```
## Examples

Create a branch for a TiDB Cloud Serverless cluster in interactive mode:

```shell
ticloud serverless branch create
```

Create a branch for a TiDB Cloud Serverless cluster in non-interactive mode:

```shell
ticloud serverless branch create --cluster-id <cluster-id> --display-name <branch-name>
```

Create a branch from another branch with a specified timestamp in non-interactive mode:

```shell
ticloud serverless branch create --cluster-id <cluster-id> --display-name <branch-name> --parent-id <parent-branch-id> --parent-timestamp <parent-timestamp>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                      | Description                                                                                               | Required | Note                                                |
|---------------------------|-----------------------------------------------------------------------------------------------------------|----------|-----------------------------------------------------|
| -c, --cluster-id string   | Specifies the ID of the cluster, in which the branch will be created.                                     | Yes      | Only works in non-interactive mode.                 |
| -n, --display-name string | Specifies the name of the branch to be created.                                                           | Yes      | Only works in non-interactive mode.                 |
| --parent-id string        | Specifies the ID of the branch parent. The default value is the cluster ID.                                                       | No       | Only works in non-interactive mode.                 |
| --parent-timestamp string | Specifies the timestamp of the parent branch in RFC3339 format, such as `2024-01-01T00:00:00Z`. The default value is the current time.  | No       | Only works in non-interactive mode.                 |
| -h, --help                | Shows help information for this command.                                                                  | No       | Works in both non-interactive and interactive modes |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
