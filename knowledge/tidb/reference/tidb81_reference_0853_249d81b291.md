# TiDB Cloud Serverless audit-log filter-rule update CLI reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-auditlog-filter-update.md`
- Source Title: `ticloud serverless audit-log filter-rule update`
- Source Heading Path: `ticloud serverless audit-log filter-rule update | ticloud serverless audit-log filter-rule update > Examples | ticloud serverless audit-log filter-rule update > Flags | ticloud serverless audit-log filter-rule update > Inherited flags | ticloud serverless audit-log filter-rule update > Feedback`
- Source Line Ranges: `5-68`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `audit-log`, `filter-rule`, `update`, `flags`, `interactive-mode`, `non-interactive-mode`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0853_249d81b291`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-auditlog-filter-update.md#ticloud-serverless-audit-log-filter-rule-update`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6084f50f2025716a311ffa328df32a2bfc8fe166f0fe0cb286f9a41b4b3fde5e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-filter-update#ticloud-serverless-audit-log-filter-rule-update
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-auditlog-filter-update.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI reference to update an audit log filter rule for a TiDB Cloud Serverless cluster, including command aliases, examples, and required flags for interactive or non-interactive mode.
- Retrieval Keywords: ticloud serverless audit-log filter-rule update, ticloud serverless audit-log filter update, TiDB Cloud Serverless audit log filter rule update, --cluster-id, --name, --enabled, --enabled=false, --rule, interactive mode, non-interactive mode, filter templates, ticloud serverless audit-log filter template, --no-color, --profile, --debug
- Follow-up Guidance: For filter rule expression templates, the source points to `ticloud serverless audit-log filter template`, and for CLI questions or suggestions it points to the TiDB Cloud CLI GitHub issue page.
- Classification Note: This is reference content because it defines the `ticloud serverless audit-log filter-rule update` command syntax, examples, flags, inherited flags, and alias usage for TiDB Cloud Serverless.

## Official Source Content

# ticloud serverless audit-log filter-rule update

Update an audit log filter rule for a TiDB Cloud Serverless cluster.

```shell
ticloud serverless audit-log filter-rule update [flags]
```

Or use the following alias command:

```shell
ticloud serverless audit-log filter update [flags]
```
## Examples

Update an audit log filter rule in interactive mode:

```shell
ticloud serverless audit-log filter update
```

Enable an audit log filter rule in non-interactive mode:

```shell
ticloud serverless audit-log filter update --cluster-id <cluster-id> --name <rule-name> --enabled
```

Disable an audit log filter rule in non-interactive mode:

```shell
ticloud serverless audit-log filter update --cluster-id <cluster-id> --name <rule-name> --enabled=false
```

Update filters of an audit log filter rule in non-interactive mode:

```shell
ticloud serverless audit-log filter update --cluster-id <cluster-id> --name <rule-name> --rule '{"users":["%@%"],"filters":[{"classes":["QUERY"],"tables":["test.t"]}]}'
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                                                                 | Required | Note                                                 |
|-------------------------|-------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | The ID of the cluster.                                                                                      | Yes      | Only works in non-interactive mode.                  |
| --name string           | The name of the filter rule to update.                                                                      | Yes      | Only works in non-interactive mode.                  |
| --enabled               | Enables or disables the filter rule.                                                                          | No       | Only works in non-interactive mode.                  |
| --rule string           | The new, complete filter rule expression. Use `ticloud serverless audit-log filter template` to see filter templates. | No       | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command.                                                                    | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
