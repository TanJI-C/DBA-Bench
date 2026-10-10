# ticloud serverless update command reference and flags

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-update.md`
- Source Title: `ticloud serverless update`
- Source Heading Path: `ticloud serverless update | ticloud serverless update > Examples | ticloud serverless update > Flags | ticloud serverless update > Inherited flags | ticloud serverless update > Feedback`
- Source Line Ranges: `5-56`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `serverless`, `cluster-update`, `interactive-mode`, `non-interactive-mode`, `flags`, `labels`, `public-endpoint`, `profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0897_43c04263c2`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-update.md#ticloud-serverless-update`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fc052ecaed47a87f0341ac6d2ccb0198b6e49e13447da8b04707db631bb414a0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-update#ticloud-serverless-update
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-update.md

## Retrieval Guidance

- Use When: Use this when looking for the TiDB Cloud CLI command syntax, examples, and flags for updating a TiDB Cloud Serverless cluster in interactive or non-interactive mode.
- Retrieval Keywords: ticloud serverless update, Update a TiDB Cloud Serverless cluster, interactive mode, non-interactive mode, -c, --cluster-id, -n, --display-name, --labels, --disable-public-endpoint, --no-color, -P, --profile, -D, --debug, ticloud serverless update -c <cluster-id> --display-name <new-display-mame>, ticloud serverless update -c <cluster-id> --labels "{\"label1\":\"value1\"}"
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is reference content because it lists the command purpose, example invocations, flag definitions, inherited flags, and mode-specific notes for `ticloud serverless update`.

## Official Source Content

# ticloud serverless update

Update a TiDB Cloud Serverless cluster:

```shell
ticloud serverless update [flags]
```
## Examples

Update a TiDB Cloud Serverless cluster in interactive mode:

```shell
ticloud serverless update
```

Update the name of a TiDB Cloud Serverless cluster in non-interactive mode:

```shell
ticloud serverless update -c <cluster-id> --display-name <new-display-mame>
```

Update labels of a TiDB Cloud Serverless cluster in non-interactive mode

```shell
ticloud serverless update -c <cluster-id> --labels "{\"label1\":\"value1\"}"
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                      | Description                                 | Required | Note                                                 |
|---------------------------|---------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string   | Specifies the ID of the cluster.            | Yes      | Only works in non-interactive mode.                  |
| -n --display-name string  | Specifies a new name for the cluster.       | No       | Only works in non-interactive mode.                  |.
| --labels string           | Specifies new labels for the cluster.       | No       | Only works in non-interactive mode.                  |
| --disable-public-endpoint | Disables the public endpoint of the cluster. | No       | Only works in non-interactive mode.                  |
| -h, --help                | Shows help information for this command.    | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                    | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
