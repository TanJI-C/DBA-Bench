# ticloud serverless sql-user delete command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-sql-user-delete.md`
- Source Title: `ticloud serverless sql-user delete`
- Source Heading Path: `ticloud serverless sql-user delete | ticloud serverless sql-user delete > Examples | ticloud serverless sql-user delete > Flags | ticloud serverless sql-user delete > Inherited flags | ticloud serverless sql-user delete > Feedback`
- Source Line Ranges: `5-48`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `cli`, `serverless`, `sql-user`, `delete`, `flags`, `interactive-mode`, `non-interactive-mode`, `authentication`, `profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0894_3e84a79312`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-sql-user-delete.md#ticloud-serverless-sql-user-delete`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fe8acb41435336936d208e8ee466dacfb61e9791315ec221aa50061c4727f21d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-sql-user-delete#ticloud-serverless-sql-user-delete
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-sql-user-delete.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI reference to delete a TiDB Cloud Serverless SQL user, including interactive and non-interactive usage and supported flags.
- Retrieval Keywords: ticloud serverless sql-user delete, Delete a TiDB Cloud Serverless SQL user, ticloud serverless sql-user delete [flags], ticloud serverless sql-user delete -c <cluster-id> --user <user-name>, --cluster-id, --force, --help, --profile, --debug, --no-color, interactive mode, non-interactive mode, cluster ID, SQL user
- Follow-up Guidance: The source also points users with questions or suggestions on the TiDB Cloud CLI to create an issue in the tidbcloud-cli GitHub repository.
- Classification Note: This is a command reference for the cloud CLI command `ticloud serverless sql-user delete`, covering examples, flags, inherited flags, and feedback information.

## Official Source Content

# ticloud serverless sql-user delete

Delete a TiDB Cloud Serverless SQL user:

```shell
ticloud serverless sql-user delete [flags]
```
## Examples

Delete a TiDB Cloud Serverless SQL user in interactive mode:

```shell
ticloud serverless sql-user delete
```

Delete a TiDB Cloud Serverless SQL user in non-interactive mode:

```shell
ticloud serverless sql-user delete -c <cluster-id> --user <user-name>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                              | Required | Note                                                 |
|-------------------------|------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.         | Yes      | Only works in non-interactive mode.                  |
| --force                 | Deletes a SQL user without confirmation.  | No       | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
