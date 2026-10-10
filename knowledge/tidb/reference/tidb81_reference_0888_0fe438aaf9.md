# ticloud serverless export download command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-export-download.md`
- Source Title: `ticloud serverless export download`
- Source Heading Path: `ticloud serverless export download | ticloud serverless export download > Examples | ticloud serverless export download > Flags | ticloud serverless export download > Inherited flags | ticloud serverless export download > Feedback`
- Source Line Ranges: `5-51`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `export`, `download`, `flags`, `interactive-mode`, `non-interactive-mode`, `profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0888_0fe438aaf9`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-export-download.md#ticloud-serverless-export-download`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `713329818943f769f6cae54c5c271636340e98edfdbcefc6b9d1795c7ff340cb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-export-download#ticloud-serverless-export-download
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-export-download.md

## Retrieval Guidance

- Use When: Use this when looking up the TiDB Cloud CLI command syntax, examples, and flags for downloading exported data from a TiDB Cloud Serverless cluster to local storage.
- Retrieval Keywords: ticloud serverless export download, Download the exported data from a TiDB Cloud Serverless cluster to your local storage, interactive mode, non-interactive mode, -c, --cluster-id, -e, --export-id, --output-path, --concurrency, --force, -P, --profile, -D, --debug, --no-color
- Follow-up Guidance: The source also points to the TiDB Cloud CLI issue tracker for questions, suggestions, and contributions.
- Classification Note: This is reference content because it lists the command usage, examples, required and optional flags, inherited flags, and mode-specific behavior for `ticloud serverless export download`.

## Official Source Content

# ticloud serverless export download

Download the exported data from a TiDB Cloud Serverless cluster to your local storage:

```shell
ticloud serverless export download [flags]
```
## Examples

Download the exported data in interactive mode:

```shell
ticloud serverless export download
```

Download the exported data in non-interactive mode:

```shell
ticloud serverless export download -c <cluster-id> -e <export-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                                                                                       | Required | Note                                                 |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.                                                                                                  | Yes      | Only works in non-interactive mode.                  |
| -e, --export-id string  | Specifies the ID of the export task.                                                                                              | Yes      | Only works in non-interactive mode.                  |
| --output-path string    | Specifies the destination path for saving the downloaded data. If not specified, the data is downloaded to the current directory. | No       | Only works in non-interactive mode.                  |
| --concurrency int       | Specifies the download concurrency. The default value is `3`.                                                                                                 | No       | Works in both non-interactive and interactive modes. |
| --force                 | Downloads the exported data without confirmation.                                                                                 | No       | Works in both non-interactive and interactive modes. |
| -h, --help              | Shows help information for this command.                                                                                          | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
