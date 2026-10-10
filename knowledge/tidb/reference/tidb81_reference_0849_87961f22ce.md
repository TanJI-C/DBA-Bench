# TiDB Cloud Serverless audit log filter rule delete command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-auditlog-filter-delete.md`
- Source Title: `ticloud serverless audit-log filter-rule delete`
- Source Heading Path: `ticloud serverless audit-log filter-rule delete | ticloud serverless audit-log filter-rule delete > Examples | ticloud serverless audit-log filter-rule delete > Flags | ticloud serverless audit-log filter-rule delete > Inherited flags | ticloud serverless audit-log filter-rule delete > Feedback`
- Source Line Ranges: `5-55`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `audit-log`, `filter-rule`, `delete`, `interactive-mode`, `non-interactive-mode`, `flags`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0849_87961f22ce`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-auditlog-filter-delete.md#ticloud-serverless-audit-log-filter-rule-delete`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f9463f123f4bcb8e6601817b4213102d44a86639fe5d60c0fa5bfcf7fc1e5bd3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-filter-delete#ticloud-serverless-audit-log-filter-rule-delete
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-auditlog-filter-delete.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command reference to delete an audit log filter rule for a TiDB Cloud Serverless cluster, including interactive and non-interactive usage and supported flags.
- Retrieval Keywords: ticloud serverless audit-log filter-rule delete, ticloud serverless audit-log filter delete, Delete an audit log filter rule for a TiDB Cloud Serverless cluster, --cluster-id, --name, --force, interactive mode, non-interactive mode, --profile, --debug, --no-color
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is a reference chunk because it defines the command syntax, alias, examples, required flags, inherited flags, and command-specific notes for deleting an audit log filter rule.

## Official Source Content

# ticloud serverless audit-log filter-rule delete

Delete an audit log filter rule for a TiDB Cloud Serverless cluster.

```shell
ticloud serverless audit-log filter-rule delete [flags]
```

Or use the following alias command:

```shell
ticloud serverless audit-log filter delete [flags]
```
## Examples

Delete an audit log filter rule in interactive mode:

```shell
ticloud serverless audit-log filter delete
```

Delete an audit log filter rule in non-interactive mode:

```shell
ticloud serverless audit-log filter delete --cluster-id <cluster-id> --name <rule-name>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                         | Required | Note                                                 |
|-------------------------|-----------------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | The ID of the cluster.                              | Yes      | Only works in non-interactive mode.                  |
| --name string           | The name of the filter rule.                        | Yes      | Only works in non-interactive mode.                  |
| --force                 | Deletes the filter rule without confirmation.              | No       | Works in both non-interactive and interactive modes. |
| -h, --help              | Shows help information for this command.            | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
