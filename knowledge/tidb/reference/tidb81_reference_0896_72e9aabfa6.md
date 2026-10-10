# ticloud serverless sql-user update command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-sql-user-update.md`
- Source Title: `ticloud serverless sql-user update`
- Source Heading Path: `ticloud serverless sql-user update | ticloud serverless sql-user update > Examples | ticloud serverless sql-user update > Flags | ticloud serverless sql-user update > Inherited flags | ticloud serverless sql-user update > Feedback`
- Source Line Ranges: `5-52`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `cli`, `serverless`, `sql-user`, `user-management`, `flags`, `interactive-mode`, `non-interactive-mode`, `roles`, `password`, `profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0896_72e9aabfa6`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-sql-user-update.md#ticloud-serverless-sql-user-update`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `61525d6e19c35b61cf3d2a8b6672effebcf34496e701c7051863db253f5f4c8d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-sql-user-update#ticloud-serverless-sql-user-update
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-sql-user-update.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI reference for updating a Serverless SQL user, including interactive and non-interactive usage and supported flags.
- Retrieval Keywords: ticloud serverless sql-user update, Update a TiDB Cloud Serverless SQL user, ticloud serverless sql-user update [flags], ticloud serverless sql-user update -c <cluster-id> --user <user-name> --password <password> --role <role>, --cluster-id, --user, --password, --role, --add-role, --delete-role, interactive mode, non-interactive mode, --profile, --debug, --no-color
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is a command reference for the cloud component because the content lists the command syntax, examples, command-specific flags, and inherited flags for the TiDB Cloud Serverless SQL user update CLI command.

## Official Source Content

# ticloud serverless sql-user update

Update a TiDB Cloud Serverless SQL user:

```shell
ticloud serverless sql-user update [flags]
```
## Examples

Update a TiDB Cloud Serverless SQL user in interactive mode:

```shell
ticloud serverless sql-user update
```

Update a TiDB Cloud Serverless SQL user in non-interactive mode:

```shell
ticloud serverless sql-user update -c <cluster-id> --user <user-name> --password <password> --role <role>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                                   | Required | Note                                                 |
|-------------------------|-------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.                                              | Yes      | Only works in non-interactive mode.                  |
| --password string       | Specifies the new password of the SQL user.                                             | No       | Only works in non-interactive mode.                  |
| --role strings          | Specifies the new roles of the SQL user. Passing this flag replaces existing roles. | No       | Only works in non-interactive mode.                  |
| --add-role strings      | Specifies the roles to be added to the SQL user.                                      | No       | Only works in non-interactive mode.                  |
| --delete-role strings   | Specifies the roles to be deleted from the SQL user.                                  | No       | Only works in non-interactive mode.                  |
| -u, --user string       | Specifies the name of the SQL user to be updated.                                       | No       | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command.                                      | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
