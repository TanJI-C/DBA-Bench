# ticloud serverless list command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-cluster-list.md`
- Source Title: `ticloud serverless cluster list`
- Source Heading Path: `ticloud serverless list | ticloud serverless list > Examples | ticloud serverless list > Flags | ticloud serverless list > Inherited flags | ticloud serverless list > Feedback`
- Source Line Ranges: `5-60`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `serverless`, `cluster-listing`, `flags`, `interactive-mode`, `non-interactive-mode`, `json-output`, `project-id`, `profiles`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0865_79a2c131f0`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-cluster-list.md#ticloud-serverless-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `49f912a4393bb8bdbfa576ffca2a098f497f3b93b37faf9d6dba1e22cd4c5e43`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-cluster-list#ticloud-serverless-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-cluster-list.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command to list TiDB Cloud Serverless clusters in a project, including interactive and non-interactive usage and output options.
- Retrieval Keywords: ticloud serverless list, ticloud serverless ls, List all TiDB Cloud Serverless clusters in a project, -p --project-id, -o json, human output, json output, interactive mode, non-interactive mode, --no-color, -P --profile, -D --debug
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is a command reference for the cloud CLI because it defines the ticloud serverless list command syntax, examples, flags, and inherited flags for listing serverless clusters.

## Official Source Content

# ticloud serverless list

List all TiDB Cloud Serverless clusters in a project:

```shell
ticloud serverless list [flags]
```

Or use the following alias command:

```shell
ticloud serverless ls [flags]
```
## Examples

List all TiDB Cloud Serverless clusters in interactive mode:

```shell
ticloud serverless list
```

List all TiDB Cloud Serverless clusters in a specified project in non-interactive mode:

```shell
ticloud serverless list -p <project-id>
```

List all TiDB Cloud Serverless clusters in a specified project with the JSON format in non-interactive mode:

```shell
ticloud serverless list -p <project-id> -o json
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                                                                              | Required | Note                                                 |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -p, --project-id string | Specifies the ID of the project.                                                              | Yes      | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command.                                                                                       | No       | Works in both non-interactive and interactive modes. |
| -o, --output string     | Specifies the output format (`human` by default). Valid values are `human` or `json`. To get a complete result, use the `json` format. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                    | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
