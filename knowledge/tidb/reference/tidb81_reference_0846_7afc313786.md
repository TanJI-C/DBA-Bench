# ticloud serverless audit-log describe command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-auditlog-describe.md`
- Source Title: `ticloud serverless audit-log describe`
- Source Heading Path: `ticloud serverless audit-log describe | ticloud serverless audit-log describe > Examples | ticloud serverless audit-log describe > Flags | ticloud serverless audit-log describe > Inherited flags | ticloud serverless audit-log describe > Feedback`
- Source Line Ranges: `5-52`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `audit-log`, `serverless`, `command-syntax`, `examples`, `flags`, `interactive-mode`, `non-interactive-mode`, `cluster-id`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0846_7afc313786`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-auditlog-describe.md#ticloud-serverless-audit-log-describe`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fd7a66fc220f7e0c3d07152ee62c666aaa81bc2dcec37b318e48bfd33613fc26`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-describe#ticloud-serverless-audit-log-describe
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-auditlog-describe.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI reference for describing the database audit logging configuration of a TiDB Cloud Serverless cluster, including command syntax, alias, examples, and flags.
- Retrieval Keywords: ticloud serverless audit-log describe, ticloud serverless audit-log get, Describe the database audit logging configuration, TiDB Cloud Serverless cluster, -c, --cluster-id, interactive mode, non-interactive mode, --no-color, -D, --debug
- Follow-up Guidance: The source also points to the TiDB Cloud CLI issue tracker for questions, suggestions, and contributions.
- Classification Note: This is reference content because it defines the command syntax, alias command, usage examples, required flags, and inherited flags for the cloud CLI command.

## Official Source Content

# ticloud serverless audit-log describe

Describe the database audit logging configuration for a TiDB Cloud Serverless cluster.

```shell
ticloud serverless audit-log describe [flags]
```

Or use the following alias command:

```shell
ticloud serverless audit-log get [flags]
```
## Examples

Get the database audit logging configuration in interactive mode:

```shell
ticloud serverless audit-log describe
```

Get the database audit logging configuration in non-interactive mode:

```shell
ticloud serverless audit-log describe -c <cluster-id>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                | Required | Note                                                 |
|-------------------------|----------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | The cluster ID.            | Yes      | Only works in non-interactive mode.                  |
| -h, --help              | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
