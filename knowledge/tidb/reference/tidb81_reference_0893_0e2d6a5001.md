# ticloud serverless sql-user create command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-sql-user-create.md`
- Source Title: `ticloud serverless sql-user create`
- Source Heading Path: `ticloud serverless sql-user create | ticloud serverless sql-user create > Examples | ticloud serverless sql-user create > Flags | ticloud serverless sql-user create > Inherited flags | ticloud serverless sql-user create > Feedback`
- Source Line Ranges: `5-50`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `shared`
- Topic Tags: `cli`, `serverless`, `sql-user`, `user-management`, `flags`, `interactive-mode`, `non-interactive-mode`, `authentication`, `profiles`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0893_0e2d6a5001`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-sql-user-create.md#ticloud-serverless-sql-user-create`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7951d3138f10c8edddffbe1963998e1332c00b93fa98a2336bfde729fc345fba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-sql-user-create#ticloud-serverless-sql-user-create
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-sql-user-create.md

## Retrieval Guidance

- Use When: Use this when looking for the TiDB Cloud CLI reference for creating a Serverless SQL user, including interactive and non-interactive usage and the available flags.
- Retrieval Keywords: ticloud serverless sql-user create, Create a TiDB Cloud Serverless SQL user, interactive mode, non-interactive mode, --user, --password, --role, --cluster-id, -c, -u, --no-color, --profile, --debug, TiDB Cloud Serverless SQL user
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is a command reference for the cloud CLI command `ticloud serverless sql-user create`, with examples, flags, and inherited flags for Serverless SQL user management.

## Official Source Content

# ticloud serverless sql-user create

Create a TiDB Cloud Serverless SQL user:

```shell
ticloud serverless sql-user create [flags]
```
## Examples

Create a TiDB Cloud Serverless SQL user in interactive mode:

```shell
ticloud serverless sql-user create
```

Create a TiDB Cloud Serverless SQL user in non-interactive mode:

```shell
ticloud serverless sql-user create --user <user-name> --password <password> --role <role> --cluster-id <cluster-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                              | Required | Note                                                 |
|-------------------------|------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.         | Yes      | Only works in non-interactive mode.                  |
| --password string       | Specifies the password of the SQL user.            | No       | Only works in non-interactive mode.                  |
| --role strings          | Specifies the roles of the SQL user.             | No       | Only works in non-interactive mode.                  |
| -u, --user string       | Specifies the name of the SQL user.                | No       | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
