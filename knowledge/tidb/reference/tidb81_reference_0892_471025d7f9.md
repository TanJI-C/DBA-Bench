# ticloud serverless spending-limit command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-spending-limit.md`
- Source Title: `ticloud serverless spending-limit`
- Source Heading Path: `ticloud serverless spending-limit | ticloud serverless spending-limit > Examples | ticloud serverless spending-limit > Flags | ticloud serverless spending-limit > Inherited flags | ticloud serverless spending-limit > Feedback`
- Source Line Ranges: `5-48`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `serverless`, `spending-limit`, `flags`, `interactive-mode`, `non-interactive-mode`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0892_471025d7f9`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-spending-limit.md#ticloud-serverless-spending-limit`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6c0e855ef0540e66599d9094c14f15de6b18f423b886409780a34be9200c3f0c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-spending-limit#ticloud-serverless-spending-limit
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-spending-limit.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command syntax, examples, and flags for setting the maximum monthly spending limit of a TiDB Cloud Serverless cluster.
- Retrieval Keywords: ticloud serverless spending-limit, TiDB Cloud Serverless spending limit, maximum monthly spending limit, --monthly, -c, --cluster-id, USD cents, interactive mode, non-interactive mode, --no-color, --profile, --debug
- Follow-up Guidance: The source also points to the spending limit documentation page and the TiDB Cloud CLI issue tracker for questions or suggestions.
- Classification Note: This is a command reference for the cloud CLI because it defines the command usage, examples, required flags, inherited flags, and feedback link for ticloud serverless spending-limit.

## Official Source Content

# ticloud serverless spending-limit

Set the maximum monthly [spending limit](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-serverless-spend-limit) for a TiDB Cloud Serverless cluster:

```shell
ticloud serverless spending-limit [flags]
```
## Examples

Set the spending limit for a TiDB Cloud Serverless cluster in interactive mode:

```shell
ticloud serverless spending-limit
```

Set the spending limit for a TiDB Cloud Serverless cluster in non-interactive mode:

```shell
ticloud serverless spending-limit -c <cluster-id> --monthly <spending-limit-monthly>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                 | Required | Note                                                 |
|-------------------------|---------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.                       | Yes      | Only works in non-interactive mode.                  |
| --monthly int32         | Specifies the maximum monthly spending limit in USD cents. | Yes      | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command.          | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                | Required | Note                                                                                                             |
|----------------------|--------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                  | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                          | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
