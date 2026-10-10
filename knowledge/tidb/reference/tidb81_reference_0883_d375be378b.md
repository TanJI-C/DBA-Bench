# ticloud serverless authorized-network update command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-authorized-network-update.md`
- Source Title: `ticloud serverless authorized-network update`
- Source Heading Path: `ticloud serverless authorized-network update | ticloud serverless authorized-network update > Examples | ticloud serverless authorized-network update > Flags | ticloud serverless authorized-network update > Inherited flags | ticloud serverless authorized-network update > Feedback`
- Source Line Ranges: `5-52`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `serverless`, `authorized-network`, `update`, `flags`, `interactive-mode`, `non-interactive-mode`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0883_d375be378b`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-authorized-network-update.md#ticloud-serverless-authorized-network-update`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `32a03001fe4425d5749f8f9a5da71576c82c6916154961673fd8470e41d38ea8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-authorized-network-update#ticloud-serverless-authorized-network-update
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-authorized-network-update.md

## Retrieval Guidance

- Use When: Use this content when looking for the TiDB Cloud CLI reference for updating a serverless authorized network, including interactive and non-interactive usage and required flags.
- Retrieval Keywords: ticloud serverless authorized-network update, Update an authorized network, interactive mode, non-interactive mode, -c, --cluster-id, --start-ip-address, --end-ip-address, --new-display-name, --new-start-ip-address, --new-end-ip-address, --no-color, --profile, --debug
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions or suggestions.
- Classification Note: This is reference content because it defines the command syntax, examples, flags, inherited flags, and mode-specific flag behavior for the CLI command.

## Official Source Content

# ticloud serverless authorized-network update

Update an authorized network:

```shell
ticloud serverless authorized-network update [flags]
```
## Examples

Update an authorized network in interactive mode:

```shell
ticloud serverless authorized-network update
```

Update an authorized network in non-interactive mode:

```shell
ticloud serverless authorized-network update -c <cluster-id> --start-ip-address <start-ip-address> --end-ip-address <end-ip-address> --new-start-ip-address <new-start-ip-address> --new-end-ip-address <new-end-ip-address>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                              | Required | Note                                                 |
|-------------------------|------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.         | Yes      | Only works in non-interactive mode.                  |
| --start-ip-address string          | Specifies the starting IP address of the authorized network.             | Yes       | Only works in non-interactive mode.                  |
| --end-ip-address string          | Specifies the ending IP address of the authorized network.             | Yes       | Only works in non-interactive mode.   |
| --new-display-name string       | Specifies the new name of the authorized network.            | No       | Only works in non-interactive mode.                  |
| --new-start-ip-address string          | Specifies the new start IP address of the authorized network.             | No       | Only works in non-interactive mode.                  |
| --new-end-ip-address string          | Specifies the new end IP address of the authorized network.             | No       | Only works in non-interactive mode.   |
| -h, --help              | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
