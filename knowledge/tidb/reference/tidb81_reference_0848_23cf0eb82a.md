# TiDB Cloud Serverless audit-log filter-rule create command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-auditlog-filter-create.md`
- Source Title: `ticloud serverless audit-log filter-rule create`
- Source Heading Path: `ticloud serverless audit-log filter-rule create | ticloud serverless audit-log filter-rule create > Examples | ticloud serverless audit-log filter-rule create > Flags | ticloud serverless audit-log filter-rule create > Inherited flags | ticloud serverless audit-log filter-rule create > Feedback`
- Source Line Ranges: `5-61`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `audit-log`, `filter-rule`, `serverless`, `examples`, `flags`, `interactive-mode`, `non-interactive-mode`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0848_23cf0eb82a`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-auditlog-filter-create.md#ticloud-serverless-audit-log-filter-rule-create`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d8e95c1053c785a05ff79850d7007dfb97b53d816f4cb5c6ab0b01a48b36424`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-filter-create#ticloud-serverless-audit-log-filter-rule-create
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-auditlog-filter-create.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud Serverless CLI reference to create an audit-log filter rule, including command aliases, examples, and required flags for interactive or non-interactive mode.
- Retrieval Keywords: ticloud serverless audit-log filter-rule create, ticloud serverless audit-log filter create, Create an audit log filter rule for a TiDB Cloud Serverless cluster, --cluster-id, --name, --rule, interactive mode, non-interactive mode, audit log filter rule, filter templates, ticloud serverless audit-log filter template, QUERY, EXECUTE, test.t, --no-color, --profile, --debug
- Follow-up Guidance: The source also points to `ticloud serverless audit-log filter template` to see filter templates and includes a feedback link for TiDB Cloud CLI issues and contributions.
- Classification Note: This is a command reference for the TiDB Cloud CLI that documents syntax, examples, required flags, inherited flags, and mode-specific behavior for creating Serverless audit-log filter rules.

## Official Source Content

# ticloud serverless audit-log filter-rule create

Create an audit log filter rule for a TiDB Cloud Serverless cluster.

```shell
ticloud serverless audit-log filter-rule create [flags]
```

Or use the following alias command:

```shell
ticloud serverless audit-log filter create [flags]
```
## Examples

Create a filter rule in interactive mode:

```shell
ticloud serverless audit-log filter create
```

Create a filter rule that captures all audit logs in non-interactive mode:

```shell
ticloud serverless audit-log filter create --cluster-id <cluster-id> --name <rule-name> --rule '{"users":["%@%"],"filters":[{}]}'
```

Create a filter rule that filters `QUERY` and `EXECUTE` events for the `test.t` table and filters `QUERY` events for all tables in non-interactive mode:

```shell
ticloud serverless audit-log filter create --cluster-id <cluster-id> --name <rule-name> --rule '{"users":["%@%"],"filters":[{"classes":["QUERY","EXECUTE"],"tables":["test.t"]},{"classes":["QUERY"]}]}'
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                                                                 | Required | Note                                                 |
|-------------------------|-------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | The ID of the cluster.                                                                                      | Yes      | Only works in non-interactive mode.                  |
| --name string           | The name of the filter rule.                                                                                | Yes      | Only works in non-interactive mode.                  |
| --rule string           | Filter rule expressions. Use `ticloud serverless audit-log filter template` to see filter templates.        | Yes      | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command.                                                                    | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
