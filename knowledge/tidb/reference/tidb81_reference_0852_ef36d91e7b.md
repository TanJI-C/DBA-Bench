# TiDB Cloud Serverless audit-log filter-rule template command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-auditlog-filter-template.md`
- Source Title: `ticloud serverless audit-log filter-rule template`
- Source Heading Path: `ticloud serverless audit-log filter-rule template | ticloud serverless audit-log filter-rule template > Examples | ticloud serverless audit-log filter-rule template > Flags | ticloud serverless audit-log filter-rule template > Inherited flags | ticloud serverless audit-log filter-rule template > Feedback`
- Source Line Ranges: `5-53`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `audit-log`, `filter-rule`, `template`, `flags`, `interactive-mode`, `non-interactive-mode`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0852_ef36d91e7b`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-auditlog-filter-template.md#ticloud-serverless-audit-log-filter-rule-template`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b9598a92d4b1fa2dc98bd7fe0e6bf30fb6a2858eee3bc90590e6e7e35121d833`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-filter-template#ticloud-serverless-audit-log-filter-rule-template
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-auditlog-filter-template.md

## Retrieval Guidance

- Use When: Use this content when looking up the TiDB Cloud Serverless CLI command that shows audit log filter rule templates, including its alias, examples, and supported flags in interactive or non-interactive mode.
- Retrieval Keywords: ticloud serverless audit-log filter-rule template, ticloud serverless audit-log filter template, Show audit log filter rule templates for a TiDB Cloud Serverless cluster, --cluster-id, -c, --cluster-id string, interactive mode, non-interactive mode, --no-color, -P, --profile string, -D, --debug, user profile
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue tracker for questions, suggestions, and contributions.
- Classification Note: This is reference content because it documents the command syntax, alias, examples, flags, and inherited flags for the TiDB Cloud Serverless audit-log filter-rule template command.

## Official Source Content

# ticloud serverless audit-log filter-rule template

Show audit log filter rule templates for a TiDB Cloud Serverless cluster.

```shell
ticloud serverless audit-log filter-rule template [flags]
```

Or use the following alias command:

```shell
ticloud serverless audit-log filter template [flags]
```
## Examples

Show filter templates in interactive mode:

```shell
ticloud serverless audit-log filter template
```

Show filter templates in non-interactive mode:

```shell
ticloud serverless audit-log filter template --cluster-id <cluster-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                  | Required | Note                                                 |
|-------------------------|------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | The ID of the cluster (optional, for context if templates might become cluster-specific).       | No       | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
