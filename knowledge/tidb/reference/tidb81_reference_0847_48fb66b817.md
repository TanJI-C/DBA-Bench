# ticloud serverless audit-log download command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-auditlog-download.md`
- Source Title: `ticloud serverless audit-log download`
- Source Heading Path: `ticloud serverless audit-log download | ticloud serverless audit-log download > Examples | ticloud serverless audit-log download > Flags | ticloud serverless audit-log download > Inherited flags | ticloud serverless audit-log download > Feedback`
- Source Line Ranges: `5-52`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `audit-log`, `download`, `serverless`, `flags`, `interactive-mode`, `non-interactive-mode`, `examples`, `user-profile`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0847_48fb66b817`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-auditlog-download.md#ticloud-serverless-audit-log-download`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1bd759a16022716802aa44b19ef42205c67e609e71121e57a911ddd88a0e1336`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-download#ticloud-serverless-audit-log-download
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-auditlog-download.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud CLI command syntax, examples, or flags for downloading database audit logs from a TiDB Cloud Serverless cluster.
- Retrieval Keywords: ticloud serverless audit-log download, Download the database audit logs from a TiDB Cloud Serverless cluster, interactive mode, non-interactive mode, -c, --cluster-id, --start-date, --end-date, --output-path, --concurrency, --force, --no-color, --profile, --debug, user profile, download the database audit logs
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue tracker for questions, suggestions, and contributions.
- Classification Note: This is a cloud CLI reference entry because the content defines the ticloud serverless audit-log download command, its examples, and its flags for TiDB Cloud Serverless.

## Official Source Content

# ticloud serverless audit-log download

Download the database audit logs from a TiDB Cloud Serverless cluster.

```shell
ticloud serverless audit-log download [flags]
```
## Examples

Download the database audit logs in interactive mode:

```shell
ticloud serverless audit-log download
```

Download the database audit logs in non-interactive mode:

```shell
ticloud serverless audit-log download -c <cluster-id> --start-date <start-date> --end-date <end-date>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                                                                         | Required | Note                                                 |
|-------------------------|---------------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -c, --cluster-id string | Cluster ID.                                                                                                         | Yes      | Only works in non-interactive mode.                  |
| --start-date string     | The start date of the audit log you want to download in the format of `YYYY-MM-DD`, for example `2025-01-01`.              | Yes      | Only works in non-interactive mode.                  |
| --end-date string       | The end date of the audit log you want to download in the format of `YYYY-MM-DD`, for example `2025-01-01`.                | Yes      | Only works in non-interactive mode.                  |
| --output-path string    | The path where you want to download the audit logs. If not specified, logs are downloaded to the current directory. | No       | Only works in non-interactive mode.                  |
| --concurrency int       | Download concurrency (`3` by default).                                                                              | No       | Works in both non-interactive and interactive modes. |
| --force                 | Download without confirmation.                                                                                      | No       | Works in both non-interactive and interactive modes. |
| -h, --help              | Shows help information for this command.                                                                            | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
