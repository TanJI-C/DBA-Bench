# TiDB Cloud Serverless audit-log filter-rule list command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-auditlog-filter-list.md`
- Source Title: `ticloud serverless audit-log filter-rule list`
- Source Heading Path: `ticloud serverless audit-log filter-rule list | ticloud serverless audit-log filter-rule list > Examples | ticloud serverless audit-log filter-rule list > Flags | ticloud serverless audit-log filter-rule list > Inherited flags | ticloud serverless audit-log filter-rule list > Feedback`
- Source Line Ranges: `5-60`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `audit-log`, `filter-rules`, `command-syntax`, `examples`, `flags`, `interactive-mode`, `non-interactive-mode`, `output-format`, `profiles`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0851_9f4571690e`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-auditlog-filter-list.md#ticloud-serverless-audit-log-filter-rule-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ebdf7335388bb8c166eddaf7030bb49bdb090e375c5dda2ce0f5c72f43c261e4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-filter-list#ticloud-serverless-audit-log-filter-rule-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-auditlog-filter-list.md

## Retrieval Guidance

- Use When: Use this when you need the CLI syntax, alias, examples, flags, and output options for listing audit log filter rules for a TiDB Cloud Serverless cluster.
- Retrieval Keywords: ticloud serverless audit-log filter-rule list, ticloud serverless audit-log filter list, List audit log filter rules for a TiDB Cloud Serverless cluster, -c --cluster-id, -o --output, human, json, interactive mode, non-interactive mode, --no-color, -P --profile, -D --debug
- Follow-up Guidance: The source also points to TiDB Cloud CLI feedback through the GitHub issue link and notes the user profile reference for the --profile flag.
- Classification Note: This is a reference command page because the official content provides command syntax, alias, examples, command-specific flags, inherited flags, and related usage notes for the cloud CLI.

## Official Source Content

# ticloud serverless audit-log filter-rule list

List audit log filter rules for a TiDB Cloud Serverless cluster.

```shell
ticloud serverless audit-log filter-rule list [flags]
```

Or use the following alias command:

```shell
ticloud serverless audit-log filter list [flags]
```
## Examples

List all audit log filter rules in interactive mode:

```shell
ticloud serverless audit-log filter list
```

List all audit log filter rules in non-interactive mode:

```shell
ticloud serverless audit-log filter list -c <cluster-id>
```

List all audit log filter rules with JSON format in non-interactive mode:

```shell
ticloud serverless audit-log filter list -c <cluster-id> -o json
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                                                       | Required | Note                                                 |
|-------------------------|---------------------------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | The ID of the cluster whose audit log filter rules you want to list.                                        | No       | Only works in non-interactive mode.                  |
| -o, --output string     | Specifies the output format (`human` by default). Valid values are `human` or `json`. To get a complete result, use the `json` format. | No       | Works in both non-interactive and interactive modes. |
| -h, --help              | Shows help information for this command.                                                          | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
