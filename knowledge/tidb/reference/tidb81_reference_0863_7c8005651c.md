# ticloud serverless delete command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-cluster-delete.md`
- Source Title: `ticloud serverless cluster delete`
- Source Heading Path: `ticloud serverless delete | ticloud serverless delete > Examples | ticloud serverless delete > Flags | ticloud serverless delete > Inherited flags | ticloud serverless delete > Feedback`
- Source Line Ranges: `5-54`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `serverless`, `cluster-deletion`, `flags`, `interactive-mode`, `non-interactive-mode`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0863_7c8005651c`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-cluster-delete.md#ticloud-serverless-delete`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6758863827a115801f5034424b2387abaf54797f870748c0b36d06487a594095`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-cluster-delete#ticloud-serverless-delete
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-cluster-delete.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI reference to delete a TiDB Cloud Serverless cluster, including command syntax, alias, flags, and interactive versus non-interactive usage.
- Retrieval Keywords: ticloud serverless delete, ticloud serverless rm, Delete a TiDB Cloud Serverless cluster, --cluster-id, -c, --force, interactive mode, non-interactive mode, --profile, --debug, --no-color
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is reference content because it lists the command syntax, examples, flags, inherited flags, and alias for the cloud CLI delete command.

## Official Source Content

# ticloud serverless delete

Delete a TiDB Cloud Serverless cluster from your project:

```shell
ticloud serverless delete [flags]
```

Or use the following alias command:

```shell
ticloud serverless rm [flags]
```
## Examples

Delete a TiDB Cloud Serverless cluster in interactive mode:

```shell
ticloud serverless delete
```

Delete a TiDB Cloud Serverless cluster in non-interactive mode:

```shell
ticloud serverless delete --cluster-id <cluster-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                            | Required | Note                                                 |
|-------------------------|----------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster to be deleted.    | Yes      | Only works in non-interactive mode.                  |
| --force                 | Deletes a cluster without confirmation. | No       | Works in both non-interactive and interactive modes. |
| -h, --help              | Shows help information for this command.     | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                | Required | Note                                                                                                             |
|----------------------|--------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                  | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                          | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
