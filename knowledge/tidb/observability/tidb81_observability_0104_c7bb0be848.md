# TiDB Cloud console audit logging setup and usage

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-console-auditing.md`
- Source Title: `Console Audit Logging`
- Source Heading Path: `Console Audit Logging | Console Audit Logging > Prerequisites | Console Audit Logging > Enable console audit logging | Console Audit Logging > Disable console audit logging | Console Audit Logging > View console audit logs | Console Audit Logging > Export console audit logs | Console Audit Logging > Console audit log storage policy | Console Audit Logging > Console audit event types`
- Source Line Ranges: `5-72`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `audit-logging`, `organization-roles`, `enablement`, `disablement`, `log-viewing`, `log-export`, `retention`, `event-types`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0104_c7bb0be848`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-console-auditing.md#console-audit-logging`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `84ed1bccd88608d4b3f43b703c3dca4e810932ef869a5d73349315cd86f9f990`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-console-auditing#console-audit-logging
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-console-auditing.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about enabling, disabling, viewing, exporting, retention, permissions, or event coverage for TiDB Cloud console audit logs at the organization level.
- Retrieval Keywords: Console Audit Logging, TiDB Cloud console audit logging, Organization Owner, Organization Console Audit Manager, enable console audit logging, disable console audit logging, view console audit logs, export console audit logs, Download logs, JSON, CSV, Advanced filter, event type, operation status, time range, 90 days, console audit log storage policy, console audit event types, organization
- Follow-up Guidance: The source also states that logs can be filtered by event type, operation status, time range, and additional fields via Advanced filter, and exported in JSON or CSV.
- Classification Note: The classification is observability for the cloud component because the content describes tracking and reviewing user activities in the TiDB Cloud console through audit logs.

## Official Source Content

# Console Audit Logging

TiDB Cloud provides the console audit logging feature to help you track various behaviors and operations of users on the [TiDB Cloud console](https://tidbcloud.com). For example, you can track operations, such as inviting a user to join your organization and creating a cluster.
## Prerequisites

- You must be in the `Organization Owner` or `Organization Console Audit Manager` role of your organization in TiDB Cloud. Otherwise, you cannot see the console audit logging-related options in the TiDB Cloud console.
- You can only enable and disable the console audit logging for your organization. You can only track the actions of users in your organization.
- After the console audit logging is enabled, all event types of the TiDB Cloud console will be audited, and you cannot specify only auditing some of them.
## Enable console audit logging

The console audit logging feature is disabled by default. To enable it, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Console Audit Logging**.
3. Click **Settings** in the upper-right corner, enable console audit logging, and then click **Update**.
## Disable console audit logging

To disable console audit logging, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Console Audit Logging**.
3. Click **Settings** in the upper-right corner, disable console audit logging, and then click **Update**.
## View console audit logs

You can only view the console audit logs of your organization.

> **Note:**
>
> - If it is the first time your organization enables console audit logging, the console audit logs are empty. After any audited events are performed, you will see the corresponding logs.
> - If it has been more than 90 days since console audit logging was disabled, you cannot see any logs.

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Console Audit Logging**.
3. To get a specific part of audit logs, you can filter the event type, operation status, and time range.
4. (Optional) To filter more fields, click **Advanced filter**, add more filters, and then click **Apply**.
5. Click the row of a log to view its detailed information in the right pane.
## Export console audit logs

To export the console audit logs of your organization, take the following step:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Console Audit Logging**.
3. (Optional) If you need to export a specific part of console audit logs, you can filter through various conditions. Otherwise, skip this step.
4. Click **Download logs** and select the desired export format in JSON or CSV.
## Console audit log storage policy

The storage time of console audit logs is 90 days, after which the logs will be automatically cleaned up.

> **Note:**
>
> - You cannot specify the storage location of console audit logs in TiDB Cloud.
> - You cannot manually delete audit logs.
## Console audit event types

The console audit logs record various user activities on the TiDB Cloud console through event types.

> **Note:**
>
> Currently, most event types on the TiDB Cloud console can be audited, and you can find them in the following table. For the remaining event types that are not covered yet, TiDB Cloud will continuously work on including them as well.
