# ticloud serverless shell command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-shell.md`
- Source Title: `ticloud serverless shell`
- Source Heading Path: `ticloud serverless shell | ticloud serverless shell > Examples | ticloud serverless shell > Flags | ticloud serverless shell > Inherited flags | ticloud serverless shell > Feedback`
- Source Line Ranges: `6-62`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `serverless`, `shell`, `interactive-mode`, `non-interactive-mode`, `flags`, `authentication`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0891_01729f515e`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-shell.md#ticloud-serverless-shell`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `84c30ba7c47b5ad08232f98cdf40e2ca819224c781f98d3f12cddcb0e72991e6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-shell#ticloud-serverless-shell
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-shell.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command syntax, examples, and flags for connecting to a TiDB Cloud Serverless cluster with `ticloud serverless shell` in interactive or non-interactive mode.
- Retrieval Keywords: ticloud serverless shell, Connect to a TiDB Cloud Serverless cluster, interactive mode, non-interactive mode, -c, --cluster-id, -u, --user, --password, --no-color, -P, --profile, -D, --debug, default user, cluster-id, user profile
- Follow-up Guidance: The source also points to the TiDB Cloud CLI issue tracker for questions, suggestions, and contributions.
- Classification Note: This is a reference chunk because it provides command usage, examples, flags, inherited flags, and notes for the `ticloud serverless shell` CLI command.

## Official Source Content

# ticloud serverless shell

Connect to a TiDB Cloud Serverless cluster:

```shell
ticloud serverless shell [flags]
```
## Examples

Connect to a TiDB Cloud Serverless cluster in interactive mode:

```shell
ticloud serverless shell
```

Connect to a TiDB Cloud Serverless cluster with the default user in non-interactive mode:

```shell
ticloud serverless shell -c <cluster-id>
```

Connect to a TiDB Cloud Serverless cluster with the default user and password in non-interactive mode:

```shell
ticloud serverless shell -c <cluster-id> --password <password>
```

Connect to a TiDB Cloud Serverless cluster with a specific user and password in non-interactive mode:

```shell
ticloud serverless shell -c <cluster-id> -u <user-name> --password <password>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                       | Required | Note                                                 |
|-------------------------|-----------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.                        | Yes      | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
| --password              | Specifies the password of the user.          | No       | Only works in non-interactive mode.                  |
| -u, --user string       | Specifies the user for login.         | No       | Only works in non-interactive mode.                  |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
