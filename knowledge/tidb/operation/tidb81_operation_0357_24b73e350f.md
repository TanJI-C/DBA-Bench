# Configure redaction, rotation, and access for audit logs

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-audit-logging.md`
- Source Title: `TiDB Cloud Serverless Database Audit Logging`
- Source Heading Path: `TiDB Cloud Serverless Database Audit Logging (Beta) > Configure audit logging | TiDB Cloud Serverless Database Audit Logging (Beta) > Configure audit logging > Data redaction | TiDB Cloud Serverless Database Audit Logging (Beta) > Configure audit logging > Log file rotation | TiDB Cloud Serverless Database Audit Logging (Beta) > Access audit logging`
- Source Line Ranges: `109-165`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `audit-logging`, `data-redaction`, `log-rotation`, `retention`, `download`, `cli`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0357_24b73e350f`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-audit-logging.md#configure-audit-logging`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `efc4aeb5ac84fb6af511655d1f3f5c51b8de972a2d69ccd56dc0ef33b73ac479`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-audit-logging#configure-audit-logging
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-audit-logging.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about audit log redaction behavior, log file rotation conditions, retention period, file naming, download commands, or ordering caveats for TiDB Cloud Serverless audit logs.
- Retrieval Keywords: Data redaction, ticloud serverless audit-log config --cluster-id <cluster-id> --unredacted, Log file rotation, 100 MiB, one hour has passed since the previous log generation, YYYY-MM-DD-<index>.log, 365 days, ticloud serverless audit-log download --cluster-id <cluster-id> --output-path <output-path> --start-date <start-date> --end-date <end-date>, start-date, end-date, TIME field, does not guarantee sequential ordering of audit logs, external storage, AWS S3, Azure Blob Storage, Google Cloud Storage
- Follow-up Guidance: The source states that if you want to retrieve all logs from a specific date, using the next day as --end-date usually works, but under extreme conditions you might need to download all log files and order them by the TIME field.
- Classification Note: This is classified as operation because the content covers runtime audit log handling, including redaction settings, automatic rotation behavior, retention, and log download access.

## Official Source Content

## Configure audit logging
### Data redaction

TiDB Cloud Serverless redacts sensitive data in the audit logs by default. Take the following SQL statement as an example:

```sql 
INSERT INTO `test`.`users` (`id`, `name`, `password`) VALUES (1, 'Alice', '123456');
```

It is redacted as follows:

```sql
INSERT INTO `test`.`users` (`id`, `name`, `password`) VALUES ( ... );
```

If you want to disable redaction, use the [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-config).

```shell
ticloud serverless audit-log config --cluster-id <cluster-id> --unredacted
```
### Log file rotation

TiDB Cloud Serverless generates a new audit log file when either of the following conditions is met:

- The size of the current log file reaches 100 MiB.
- One hour has passed since the previous log generation. Depending on the internal scheduling mechanism, log generation might be delayed by a few minutes.

> **Note:**
>
> Currently, Log file rotation settings are not configurable. TiDB Cloud Serverless automatically rotates the audit log files based on the preceding conditions.
## Access audit logging

TiDB Cloud Serverless audit logs are stored as readable text files named `YYYY-MM-DD-<index>.log`.

Currently, audit logs are stored within TiDB Cloud for 365 days. After this period, logs are automatically deleted.

> **Note:**
>
> Contact [TiDB Cloud Support](https://docs.pingcap.com/tidbcloud/tidb-cloud-support) if you need to save audit logs in external storage (such as AWS S3, Azure Blob Storage, and Google Cloud Storage).

To view and download audit logs, use the [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auditlog-download):

```shell
ticloud serverless audit-log download --cluster-id <cluster-id> --output-path <output-path> --start-date <start-date> --end-date <end-date>
```

- `start-date`: The start date of the audit log you want to download in the format of `YYYY-MM-DD`, for example `2025-01-01`.
- `end-date`: The end date of the audit log you want to download in the format of `YYYY-MM-DD`, for example `2025-01-01`.

> **Note:**
>
> TiDB Cloud Serverless does not guarantee sequential ordering of audit logs. The log file named `YYYY-MM-DD-<index>.log` might contain the audit logs in previous days.
> If you want to retrieve all logs from a specific date (for example, January 1, 2025), specifying `--start-date 2025-01-01` and `--end-date 2025-01-02` usually works. But under extreme conditions, you might need to download all log files and order them by the `TIME` field.
