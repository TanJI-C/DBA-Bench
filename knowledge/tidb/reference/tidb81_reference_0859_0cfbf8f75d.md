# ticloud serverless branch describe command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-branch-describe.md`
- Source Title: `ticloud serverless branch describe`
- Source Heading Path: `ticloud serverless branch describe | ticloud serverless branch describe > Examples | ticloud serverless branch describe > Flags | ticloud serverless branch describe > Inherited flags | ticloud serverless branch describe > Feedback`
- Source Line Ranges: `5-54`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `branch`, `describe`, `flags`, `interactive-mode`, `non-interactive-mode`, `profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0859_0cfbf8f75d`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-branch-describe.md#ticloud-serverless-branch-describe`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `97f55e0ab8cb2c1edd40d9aa91eb21c7dad7a347bf2e385e20a665521959405e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-branch-describe#ticloud-serverless-branch-describe
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-branch-describe.md

## Retrieval Guidance

- Use When: Use this when looking up the TiDB Cloud CLI command that gets information about a Serverless branch, including endpoints, user name prefix, and usages, in interactive or non-interactive mode.
- Retrieval Keywords: ticloud serverless branch describe, ticloud serverless branch get, Get information about a branch, endpoints, user name prefix, usages, --branch-id, --cluster-id, interactive mode, non-interactive mode, --profile, --debug, --no-color
- Follow-up Guidance: The source also lists the alias command `ticloud serverless branch get [flags]` and shows example usage for both interactive and non-interactive modes.
- Classification Note: This is a command reference for the TiDB Cloud CLI `ticloud serverless branch describe` command, including examples, required flags, and inherited flags for Serverless branch description in cloud scope.

## Official Source Content

# ticloud serverless branch describe

Get information about a branch (such as the endpoints, [user name prefix](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#user-name-prefix), and usages):

```shell
ticloud serverless branch describe [flags]
```

Or use the following alias command:

```shell
ticloud serverless branch get [flags]
```
## Examples

Get branch information of a TiDB Cloud Serverless cluster in interactive mode:

```shell
ticloud serverless branch describe
```

Get branch information of a TiDB Cloud Serverless cluster in non-interactive mode:

```shell
ticloud serverless branch describe --branch-id <branch-id> --cluster-id <cluster-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                       | Required | Note                                                 |
|-------------------------|-----------------------------------|----------|------------------------------------------------------|
| -b, --branch-id string  | Specifies the ID of the branch.              | Yes      | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
| -c, --cluster-id string | Specifies the ID of the cluster.      | Yes      | Only works in non-interactive mode.                  |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
