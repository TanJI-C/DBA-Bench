# TiDB Cloud CLI serverless import describe command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-import-describe.md`
- Source Title: `ticloud serverless import describe`
- Source Heading Path: `ticloud serverless import describe | ticloud serverless import describe > Examples | ticloud serverless import describe > Flags | ticloud serverless import describe > Inherited flags | ticloud serverless import describe > Feedback`
- Source Line Ranges: `5-54`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `serverless`, `import`, `describe`, `flags`, `interactive-mode`, `non-interactive-mode`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0876_be76919841`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-import-describe.md#ticloud-serverless-import-describe`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9bbd7559158f56cdc9708c6fa18d9a20378072cd7b34448b45673b8d648ebc80`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-import-describe#ticloud-serverless-import-describe
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-import-describe.md

## Retrieval Guidance

- Use When: Use this when looking for the TiDB Cloud CLI reference for describing a serverless data import task, including the alias command, examples, and supported flags in interactive or non-interactive mode.
- Retrieval Keywords: ticloud serverless import describe, ticloud serverless import get, Describe a data import task, --cluster-id, --import-id, interactive mode, non-interactive mode, --profile, --debug, --no-color
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is a command reference for the cloud CLI because it defines the syntax, alias, examples, required flags, and inherited flags for `ticloud serverless import describe`.

## Official Source Content

# ticloud serverless import describe

Describe a data import task:

```shell
ticloud serverless import describe [flags]
```

Or use the following alias command:

```shell
ticloud serverless import get [flags]
```
## Examples

Describe an import task in interactive mode:

```shell
ticloud serverless import describe
```

Describe an import task in non-interactive mode:

```shell
ticloud serverless import describe --cluster-id <cluster-id> --import-id <import-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                       | Required | Note                                                 |
|-------------------------|-----------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.                        | Yes      | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
| --import-id string      | Specifies the ID of the import task.         | Yes      | Only works in non-interactive mode.                  |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
