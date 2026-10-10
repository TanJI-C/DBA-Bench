# ticloud serverless authorized-network create command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-serverless-authorized-network-create.md`
- Source Title: `ticloud serverless authorized-network create`
- Source Heading Path: `ticloud serverless authorized-network create | ticloud serverless authorized-network create > Examples | ticloud serverless authorized-network create > Flags | ticloud serverless authorized-network create > Inherited flags | ticloud serverless authorized-network create > Feedback`
- Source Line Ranges: `5-50`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `authorized-network`, `create`, `interactive-mode`, `non-interactive-mode`, `flags`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0880_84449db667`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-serverless-authorized-network-create.md#ticloud-serverless-authorized-network-create`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a8af31f72b071d528eec6f4b0ff8aa5af26335e4f0592ea0d0371fe39e3e29e1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-authorized-network-create#ticloud-serverless-authorized-network-create
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-serverless-authorized-network-create.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command syntax, examples, and flags to create a serverless authorized network in interactive or non-interactive mode.
- Retrieval Keywords: ticloud serverless authorized-network create, Create an authorized network, interactive mode, non-interactive mode, -c, --cluster-id, --display-name, --start-ip-address, --end-ip-address, --no-color, --profile, --debug, authorized network
- Follow-up Guidance: For questions or suggestions on the TiDB Cloud CLI, the source points to creating an issue in the tidbcloud-cli GitHub repository.
- Classification Note: This is reference content because it provides command usage, examples, required flags, inherited flags, and help-related details for the cloud CLI command.

## Official Source Content

# ticloud serverless authorized-network create

Create an authorized network:

```shell
ticloud serverless authorized-network create [flags]
```
## Examples

Create an authorized network in interactive mode:

```shell
ticloud serverless authorized-network create
```

Create an authorized network in non-interactive mode:

```shell
ticloud serverless authorized-network create -c <cluster-id> --display-name <display-name> --start-ip-address <start-ip-address> --end-ip-address <end-ip-address>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                              | Required | Note                                                 |
|-------------------------|------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.         | Yes      | Only works in non-interactive mode.                  |
| --display-name string       | Specifies the name of the authorized network.            | Yes       | Only works in non-interactive mode.                  |
| --start-ip-address string          | Specifies the start IP address of the authorized network.             | Yes       | Only works in non-interactive mode.                  |
| --end-ip-address string          | Specifies the end IP address of the authorized network.             | Yes       | Only works in non-interactive mode.   |
| -h, --help              | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
