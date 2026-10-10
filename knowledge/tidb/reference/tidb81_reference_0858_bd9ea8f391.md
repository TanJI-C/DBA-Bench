# ticloud serverless branch delete command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-branch-delete.md`
- Source Title: `ticloud serverless branch delete`
- Source Heading Path: `ticloud serverless branch delete | ticloud serverless branch delete > Examples | ticloud serverless branch delete > Flags | ticloud serverless branch delete > Inherited flags | ticloud serverless branch delete > Feedback`
- Source Line Ranges: `5-55`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `serverless`, `branch`, `delete`, `flags`, `interactive-mode`, `non-interactive-mode`, `examples`, `inherited-flags`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0858_bd9ea8f391`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-branch-delete.md#ticloud-serverless-branch-delete`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fa2f4e48058b0a6a592b299e9247ab41588383756107e18415fd9a0585f1059c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-branch-delete#ticloud-serverless-branch-delete
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-branch-delete.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the TiDB Cloud CLI command syntax, alias, examples, and flags for deleting a Serverless branch from a TiDB Cloud cluster.
- Retrieval Keywords: ticloud serverless branch delete, ticloud serverless branch rm, Delete a branch from your TiDB Cloud Serverless cluster, --branch-id, --cluster-id, --force, interactive mode, non-interactive mode, inherited flags, --no-color, --profile, --debug
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is reference content because it lists the command form, alias command, examples, required flags, inherited flags, and feedback link for the CLI operation.

## Official Source Content

# ticloud serverless branch delete

Delete a branch from your TiDB Cloud Serverless cluster:

```shell
ticloud serverless branch delete [flags]
```

Or use the following alias command:

```shell
ticloud serverless branch rm [flags]
```
## Examples

Delete a TiDB Cloud Serverless branch in interactive mode:

```shell
ticloud serverless branch delete
```

Delete a TiDB Cloud Serverless branch in non-interactive mode:

```shell
ticloud branch delete --branch-id <branch-id> --cluster-id <cluster-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                | Required | Note                                                 |
|-------------------------|--------------------------------------------|----------|------------------------------------------------------|
| -b, --branch-id string  | Specifies the ID of the branch to be deleted.         | Yes      | Only works in non-interactive mode.                  |
| --force                 | Deletes a branch without confirmation.      | No       | Works in both non-interactive and interactive modes. |
| -h, --help              | Shows help information for this command.         | No       | Works in both non-interactive and interactive modes. |
| -c, --cluster-id string | Specifies the ID of the cluster. | Yes      | Only works in non-interactive mode.                  |
## Inherited flags

| Flag                 | Description                                                                                | Required | Note                                                                                                             |
|----------------------|--------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                  | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                         | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
