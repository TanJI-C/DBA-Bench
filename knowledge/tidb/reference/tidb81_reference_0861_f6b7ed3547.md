# ticloud serverless branch shell command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-branch-shell.md`
- Source Title: `ticloud serverless branch shell`
- Source Heading Path: `ticloud serverless branch shell | ticloud serverless branch shell > Examples | ticloud serverless branch shell > Flags | ticloud serverless branch shell > Inherited flags | ticloud serverless branch shell > Feedback`
- Source Line Ranges: `6-63`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `serverless`, `branch`, `shell`, `interactive-mode`, `non-interactive-mode`, `flags`, `authentication`, `profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0861_f6b7ed3547`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-branch-shell.md#ticloud-serverless-branch-shell`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5df3d6d546e43888632037e683b41b7a6060105c2762ffad244d23a7f904fcd5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-branch-shell#ticloud-serverless-branch-shell
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-branch-shell.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the ticloud command syntax, examples, and flags to connect to a TiDB Cloud Serverless branch in interactive or non-interactive mode.
- Retrieval Keywords: ticloud serverless branch shell, TiDB Cloud Serverless branch, interactive mode, non-interactive mode, -c --cluster-id, -b --branch-id, -u --user, --password, --no-color, -P --profile, -D --debug, Connect to a branch of a TiDB Cloud Serverless cluster
- Follow-up Guidance: If you have questions or suggestions on the TiDB Cloud CLI, the source points to creating an issue in the tidbcloud-cli GitHub repository.
- Classification Note: This is a reference chunk because it documents the ticloud serverless branch shell command, its examples, and its command flags for the cloud CLI.

## Official Source Content

# ticloud serverless branch shell

Connect to a branch of a TiDB Cloud Serverless cluster:

```shell
ticloud serverless branch shell [flags]
```
## Examples

Connect to a TiDB Cloud Serverless branch in interactive mode:

```shell
ticloud serverless branch shell
```

Connect to a TiDB Cloud Serverless branch with the default user in non-interactive mode:

```shell
ticloud serverless branch shell -c <cluster-id> -b <branch-id>
```

Connect to a TiDB Cloud Serverless branch with the default user and password in non-interactive mode:

```shell
ticloud serverless branch shell -c <cluster-id> -b <branch-id> --password <password>
```

Connect to a TiDB Cloud Serverless branch with a specific user and password in non-interactive mode:

```shell
ticloud serverless branch shell -c <cluster-id> -b <branch-id> -u <user-name> --password <password>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                       | Required | Note                                                 |
|-------------------------|-----------------------------------|----------|------------------------------------------------------|
| -b, --branch-id string  | Specifies the ID of the branch.                         | Yes      | Only works in non-interactive mode.                  |
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
