# ticloud serverless import cancel command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-import-cancel.md`
- Source Title: `ticloud serverless import cancel`
- Source Heading Path: `ticloud serverless import cancel | ticloud serverless import cancel > Examples | ticloud serverless import cancel > Flags | ticloud serverless import cancel > Inherited flags | ticloud serverless import cancel > Feedback`
- Source Line Ranges: `5-49`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `import`, `cancel`, `interactive-mode`, `non-interactive-mode`, `flags`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0875_bf777e6e7f`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-import-cancel.md#ticloud-serverless-import-cancel`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `25fb5be4530f240f5520bd3b15c9692ff57c228e3ec7bdf0269ba2b76e36fa56`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-import-cancel#ticloud-serverless-import-cancel
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-import-cancel.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI reference for canceling a serverless data import task, including interactive and non-interactive command usage and flags.
- Retrieval Keywords: ticloud serverless import cancel, Cancel a data import task, ticloud serverless import cancel [flags], --cluster-id, --import-id, --force, interactive mode, non-interactive mode, --profile, --debug, --no-color
- Follow-up Guidance: The source also points to the TiDB Cloud CLI feedback issue link and the user profile reference used by the -P, --profile flag.
- Classification Note: This is a reference chunk because it documents the command syntax, examples, required flags, inherited flags, and command-specific options for ticloud serverless import cancel.

## Official Source Content

# ticloud serverless import cancel

Cancel a data import task:

```shell
ticloud serverless import cancel [flags]
```
## Examples

Cancel an import task in interactive mode:

```shell
ticloud serverless import cancel
```

Cancel an import task in non-interactive mode:

```shell
ticloud serverless import cancel --cluster-id <cluster-id> --import-id <import-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                  | Required | Note                                                 |
|-------------------------|----------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Specifies the ID of the cluster.                                  | Yes      | Only works in non-interactive mode.                  |
| --force                 | Cancels an import task without confirmation. | No       | Works in both non-interactive and interactive modes. |
| -h, --help              | Shows help information for this command.     | No       | Works in both non-interactive and interactive modes. |
| --import-id string      | Specifies the ID of the import task.         | Yes      | Only works in non-interactive mode.                  |
## Inherited flags

| Flag                 | Description                                                                               | Required | Note                                                                                                                    |
|----------------------|-------------------------------------------------------------------------------------------|----------|--------------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                  | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                                      |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
