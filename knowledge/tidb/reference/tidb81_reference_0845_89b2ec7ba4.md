# TiDB Cloud Serverless audit-log config command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-auditlog-config.md`
- Source Title: `ticloud serverless audit-log config`
- Source Heading Path: `ticloud serverless audit-log config | ticloud serverless audit-log config > Examples | ticloud serverless audit-log config > Flags | ticloud serverless audit-log config > Inherited flags | ticloud serverless audit-log config > Feedback`
- Source Line Ranges: `5-61`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `audit-log`, `serverless`, `flags`, `interactive-mode`, `non-interactive-mode`, `redaction`, `profiles`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0845_89b2ec7ba4`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-auditlog-config.md#ticloud-serverless-audit-log-config`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `91c58e90d2af9aa5037af50df6a401d196f5ebf3b725dc7773c11c1d2ac04885`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-config#ticloud-serverless-audit-log-config
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-auditlog-config.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command syntax, examples, and flags for configuring database audit logging on a TiDB Cloud Serverless cluster.
- Retrieval Keywords: ticloud serverless audit-log config, TiDB Cloud Serverless audit-log config, configure database audit logging, -c --cluster-id, --enabled, --enabled=false, --unredacted, interactive mode, non-interactive mode, --no-color, --profile, --debug
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is a reference chunk because it documents the command usage, examples, flags, inherited flags, and mode-specific behavior for the CLI command.

## Official Source Content

# ticloud serverless audit-log config

Configure the database audit logging for a TiDB Cloud Serverless cluster.

```shell
ticloud serverless audit-log config [flags]
```
## Examples

Configure the database audit logging in interactive mode:

```shell
ticloud serverless audit-log config
```

Enable the database audit logging in non-interactive mode:

```shell
ticloud serverless audit-log config -c <cluster-id> --enabled
```

Disable the database audit logging in non-interactive mode:

```shell
ticloud serverless audit-log config -c <cluster-id> --enabled=false
```

Unredact the database audit logging in non-interactive mode:

```shell
ticloud serverless audit-log config -c <cluster-id> --unredacted
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                                 | Required | Note                                                 |
|-------------------------|-----------------------------------------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | The ID of the cluster.                                       | Yes      | Only works in non-interactive mode.                  |
| --enabled               | Enable or disable the database audit logging.                              | No       | Only works in non-interactive mode.                  |
| --unredacted            | Enable or disable data redaction in audit logs.                             | No       | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command.                                   | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
