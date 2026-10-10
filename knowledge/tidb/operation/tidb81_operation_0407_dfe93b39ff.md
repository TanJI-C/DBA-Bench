# Manage audit logging rules, access, and shutdown

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-auditing.md`
- Source Title: `TiDB Cloud Dedicated Database Audit Logging`
- Source Heading Path: `TiDB Cloud Dedicated Database Audit Logging > Specify auditing filter rules | TiDB Cloud Dedicated Database Audit Logging > View audit logs | TiDB Cloud Dedicated Database Audit Logging > Disable audit logging`
- Source Line Ranges: `249-285`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `audit-logging`, `filter-rules`, `regular-expressions`, `log-access`, `cloud-storage`, `disable`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0407_dfe93b39ff`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-auditing.md#specify-auditing-filter-rules`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `acbcff446b720310da376bdcaa592189f31ec3deb3e7ce228209daabc36d7048`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-auditing#specify-auditing-filter-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-auditing.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how TiDB Cloud audit filter rules work, where audit logs are stored or downloaded, or how to disable audit logging.
- Retrieval Keywords: Specify auditing filter rules, Add Filter Rule, Log Filter Rules, regular expressions, case-sensitive, .*, View audit logs, Audit Log Access, Database Audit Logging, cluster ID, Pod ID, tidb-audit-2022-04-21T18-16-29.529.log, Disable audit logging, Settings > Audit Settings, 10 MiB, cloud storage bucket, PingCAP support
- Follow-up Guidance: The content notes that if audit logging is disabled and the remaining log file is smaller than 10 MiB, it will not be automatically pushed to the cloud storage bucket and you need to contact PingCAP support to get it.
- Classification Note: This is operation content because it covers ongoing rule management, viewing stored audit logs, and turning audit logging off.

## Official Source Content

## Specify auditing filter rules

After enabling audit logging, you must specify auditing filter rules to control which user access events to capture and write to audit logs. If no filter rules are specified, TiDB Cloud does not log anything.

To specify auditing filter rules for a cluster, take the following steps:

1. On the **DB Audit Logging** page, click **Add Filter Rule** in the **Log Filter Rules** section to add an audit filter rule.

    You can add one audit rule at a time. Each rule specifies a user expression, database expression, table expression, and access type. You can add multiple audit rules to meet your auditing requirements.

2.In the **Log Filter Rules** section, click **>** to expand and view the list of audit rules you have added.

> **Note:**
>
> - The filter rules are regular expressions and case-sensitive. If you use the wildcard rule `.*`, all users, databases, or table events in the cluster are logged.
> - Because audit logging consumes cluster resources, be prudent when specifying filter rules. To minimize the consumption, it is recommended that you specify filter rules to limit the scope of audit logging to specific database objects, users, and actions, where possible.
## View audit logs

By default, TiDB Cloud stores database audit log files in your storage service, so you need to read the audit log information from your storage service.

> **Note:**
>
> If you have requested and chosen to store audit log files in TiDB Cloud, you can download them from the **Audit Log Access** section on the **Database Audit Logging** page.

TiDB Cloud audit logs are readable text files with the cluster ID, Pod ID, and log creation date incorporated into the fully qualified filenames.

For example, `13796619446086334065/tidb-0/tidb-audit-2022-04-21T18-16-29.529.log`. In this example, `13796619446086334065` indicates the cluster ID and `tidb-0` indicates the Pod ID.
## Disable audit logging

If you no longer want to audit a cluster, go to the page of the cluster, click **Settings** > **Audit Settings**, and then toggle the audit setting in the upper-right corner to **Off**.

> **Note:**
>
> Each time the size of the log file reaches 10 MiB, the log file will be pushed to the cloud storage bucket. Therefore, after the audit log is disabled, the log file whose size is smaller than 10 MiB will not be automatically pushed to the cloud storage bucket. To get the log file in this situation, contact [PingCAP support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
