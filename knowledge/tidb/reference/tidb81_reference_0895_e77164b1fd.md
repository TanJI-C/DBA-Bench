# ticloud serverless sql-user list command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-sql-user-list.md`
- Source Title: `ticloud serverless sql-user list`
- Source Heading Path: `ticloud serverless sql-user list | ticloud serverless sql-user list > Examples | ticloud serverless sql-user list > Flags | ticloud serverless sql-user list > Inherited flags | ticloud serverless sql-user list > Feedback`
- Source Line Ranges: `5-48`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `shared`
- Topic Tags: `cli`, `serverless`, `sql-users`, `list`, `flags`, `interactive-mode`, `non-interactive-mode`, `output-format`, `profiles`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0895_e77164b1fd`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-sql-user-list.md#ticloud-serverless-sql-user-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7969eda14ea094fa549106c983ff9e1dd7d306222efd8f7ca95381c41211bcb8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-sql-user-list#ticloud-serverless-sql-user-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-sql-user-list.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI reference for listing TiDB Cloud Serverless SQL users, including interactive and non-interactive usage, required flags, and output format options.
- Retrieval Keywords: ticloud serverless sql-user list, List TiDB Cloud Serverless SQL users, ticloud serverless sql-user list [flags], interactive mode, non-interactive mode, -c, --cluster-id, -o, --output, human, json, --no-color, -P, --profile, -D, --debug
- Follow-up Guidance: The source also points users with TiDB Cloud CLI questions or suggestions to create an issue in the tidbcloud-cli GitHub repository.
- Classification Note: This is a cloud CLI command reference for the `ticloud serverless sql-user list` command, documenting syntax, examples, command flags, and inherited flags.

## Official Source Content

# ticloud serverless sql-user list

List TiDB Cloud Serverless SQL users:

```shell
ticloud serverless sql-user list [flags]
```
## Examples

List TiDB Cloud Serverless SQL users in interactive mode:

```shell
ticloud serverless sql-user list
```

List TiDB Cloud Serverless SQL users in non-interactive mode:

```shell
ticloud serverless sql-user list -c <cluster-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                                                                 | Required | Note                                                 |
|-------------------------|-------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.                                                                            | Yes      | Only works in non-interactive mode.                  |
| -o, --output string     | Specifies the output format, one of ["human" "json"]. To get a complete result, use "json" format. (default "human"). | No       | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command.                                                                    | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
