# ticloud serverless region command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-region.md`
- Source Title: `ticloud serverless region`
- Source Heading Path: `ticloud serverless region | ticloud serverless region > Examples | ticloud serverless region > Flags | ticloud serverless region > Inherited flags | ticloud serverless region > Feedback`
- Source Line Ranges: `6-48`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `serverless`, `regions`, `flags`, `output-format`, `profiles`, `debug`, `help`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0890_a0ad498c34`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-region.md#ticloud-serverless-region`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a452b71c471064cc6546202e034afce0c18b65672a27c600c4c703be17b9dda2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-region#ticloud-serverless-region
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-region.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the CLI reference to list all available regions for TiDB Cloud Serverless and the supported output and inherited flags for that command.
- Retrieval Keywords: ticloud serverless region, List all available regions for TiDB Cloud Serverless, ticloud serverless region -o json, --output, -o json, human, json, --help, --no-color, --profile, --debug, user profile, non-interactive mode, interactive mode
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is a reference command page for the cloud CLI command `ticloud serverless region`, including examples, flags, and inherited flags.

## Official Source Content

# ticloud serverless region

List all available regions for TiDB Cloud Serverless:

```shell
ticloud serverless region [flags]
```
## Examples

List all available regions for TiDB Cloud Serverless:

```shell
ticloud serverless region
```

List all available regions for TiDB Cloud Serverless clusters in the JSON format:

```shell
ticloud serverless region -o json
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                | Description                                                                                                              | Required | Note                                                 |
|---------------------|--------------------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -o, --output string | Specifies the output format (`human` by default). Valid values are `human` or `json`. To get a complete result, use the `json` format. | No       | Works in both non-interactive and interactive modes. |
| -h, --help          | Shows help information for this command.                                                                                       | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                | Required | Note                                                                                                             |
|----------------------|--------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                  | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                         | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
