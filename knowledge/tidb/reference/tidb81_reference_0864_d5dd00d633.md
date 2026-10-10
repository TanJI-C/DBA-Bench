# ticloud serverless describe command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-cluster-describe.md`
- Source Title: `ticloud serverless cluster describe`
- Source Heading Path: `ticloud serverless describe | ticloud serverless describe > Examples | ticloud serverless describe > Flags | ticloud serverless describe > Inherited flags | ticloud serverless describe > Feedback`
- Source Line Ranges: `5-53`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `serverless`, `cluster`, `describe`, `get`, `interactive-mode`, `non-interactive-mode`, `flags`, `profile`, `debug`, `help`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0864_d5dd00d633`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-cluster-describe.md#ticloud-serverless-describe`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1c54db88654866f3e9d81029b240f73283a5e198a668e69e37f89249194b24ad`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-cluster-describe#ticloud-serverless-describe
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-cluster-describe.md

## Retrieval Guidance

- Use When: Use this when looking up the TiDB Cloud CLI command that gets information about a TiDB Cloud Serverless cluster, including cluster configurations and cluster status, in interactive or non-interactive mode.
- Retrieval Keywords: ticloud serverless describe, ticloud serverless get, TiDB Cloud Serverless cluster, cluster configurations, cluster status, --cluster-id, -c, interactive mode, non-interactive mode, --profile, -P, --debug, -D, --no-color
- Follow-up Guidance: The source also points to TiDB Cloud CLI feedback through the GitHub issue link and notes the user profile reference for the --profile flag.
- Classification Note: This is a command reference for the cloud CLI because the content defines syntax, alias, examples, command flags, inherited flags, and feedback for ticloud serverless describe.

## Official Source Content

# ticloud serverless describe

Get information about a TiDB Cloud Serverless cluster (such as the cluster configurations and cluster status):

```shell
ticloud serverless describe [flags]
```

Or use the following alias command:

```shell
ticloud serverless get [flags]
```
## Examples

Get information about a TiDB Cloud Serverless cluster in interactive mode:

```shell
ticloud serverless describe
```

Get information about a TiDB Cloud Serverless cluster in non-interactive mode:

```shell
ticloud serverless describe --cluster-id <cluster-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                       | Required | Note                                                 |
|-------------------------|-----------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.             | Yes      | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                    | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
