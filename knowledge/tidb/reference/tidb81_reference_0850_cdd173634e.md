# TiDB Cloud Serverless audit-log filter-rule describe command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-auditlog-filter-describe.md`
- Source Title: `ticloud serverless audit-log filter-rule describe`
- Source Heading Path: `ticloud serverless audit-log filter-rule describe | ticloud serverless audit-log filter-rule describe > Examples | ticloud serverless audit-log filter-rule describe > Flags | ticloud serverless audit-log filter-rule describe > Inherited flags | ticloud serverless audit-log filter-rule describe > Feedback`
- Source Line Ranges: `5-54`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `audit-log`, `filter-rule`, `describe`, `flags`, `interactive-mode`, `non-interactive-mode`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0850_cdd173634e`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-auditlog-filter-describe.md#ticloud-serverless-audit-log-filter-rule-describe`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0df65412cfe1c923c84f3ed0753c89c5f3f91030fab02a2b3cd480ea0b21a5f3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-filter-describe#ticloud-serverless-audit-log-filter-rule-describe
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-auditlog-filter-describe.md

## Retrieval Guidance

- Use When: Use this content when looking up the TiDB Cloud Serverless CLI command syntax, alias, examples, and flags for describing an audit log filter rule.
- Retrieval Keywords: ticloud serverless audit-log filter-rule describe, ticloud serverless audit-log filter describe, Describe an audit log filter rule for a TiDB Cloud Serverless cluster, --cluster-id, --name, interactive mode, non-interactive mode, --no-color, --profile, --debug, user profile
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is a command reference for the cloud CLI because it documents the syntax, alias command, examples, required flags, and inherited flags for describing an audit log filter rule.

## Official Source Content

# ticloud serverless audit-log filter-rule describe

Describe an audit log filter rule for a TiDB Cloud Serverless cluster.

```shell
ticloud serverless audit-log filter-rule describe [flags]
```

Or use the following alias command:

```shell
ticloud serverless audit-log filter describe [flags]
```
## Examples

Describe an audit log filter rule in interactive mode:

```shell
ticloud serverless audit-log filter describe
```

Describe an audit log filter rule in non-interactive mode:

```shell
ticloud serverless audit-log filter describe --cluster-id <cluster-id> --name <rule-name>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                  | Required | Note                                                 |
|-------------------------|------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | The ID of the cluster.       | Yes      | Only works in non-interactive mode.                  |
| --name string           | The name of the filter rule. | Yes      | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
