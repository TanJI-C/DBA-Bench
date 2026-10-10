# ticloud serverless authorized-network list command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-authorized-network-list.md`
- Source Title: `ticloud serverless authorized-network list`
- Source Heading Path: `ticloud serverless authorized-network list | ticloud serverless authorized-network list > Examples | ticloud serverless authorized-network list > Flags | ticloud serverless authorized-network list > Inherited flags | ticloud serverless authorized-network list > Feedback`
- Source Line Ranges: `5-48`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `authorized-network`, `list`, `flags`, `interactive-mode`, `non-interactive-mode`, `output`, `profile`, `debug`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0882_48dbe4266a`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-authorized-network-list.md#ticloud-serverless-authorized-network-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `54fce93462a9ba637ce5bc0a2ce75e3ae29f723d43def3c110c175955c3b72be`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-authorized-network-list#ticloud-serverless-authorized-network-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-authorized-network-list.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI syntax, examples, and flags for listing all authorized networks for a serverless cluster.
- Retrieval Keywords: ticloud serverless authorized-network list, List all authorized networks, -c, --cluster-id, --output human json, interactive mode, non-interactive mode, --no-color, -P, --profile, -D, --debug
- Follow-up Guidance: The source also points to the TiDB Cloud CLI issue tracker for questions, suggestions, and contributions.
- Classification Note: This is reference content because it documents the command usage, examples, required flags, inherited flags, and output options for `ticloud serverless authorized-network list`.

## Official Source Content

# ticloud serverless authorized-network list

List all authorized networks:

```shell
ticloud serverless authorized-network list [flags]
```
## Examples

List all authorized networks in interactive mode:

```shell
ticloud serverless authorized-network list
```

List all authorized networks in non-interactive mode:

```shell
ticloud serverless authorized-network list -c <cluster-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                              | Required | Note                                                 |
|-------------------------|------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.         | Yes      | Only works in non-interactive mode.                  |
| --output string       |  Specifies the output format (`human` by default). Valid values are `human` or `json`. To get a complete result, use the `json` format.            | No       | Works in both non-interactive and interactive modes.                  |
| -h, --help              | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
