# TiDB Cloud email alert subscriptions

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-alert-email.md`
- Source Title: `Subscribe via Email`
- Source Heading Path: `Subscribe via Email | Subscribe via Email > Prerequisites | Subscribe via Email > Subscribe to alert notifications | Subscribe via Email > Unsubscribe from alert notifications`
- Source Line Ranges: `5-49`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `alert subscription`, `email notifications`, `project settings`, `unsubscribe`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0350_5eaa67192d`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-alert-email.md#subscribe-via-email`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9b940d4accc765d7a67b4af52e311007fc5aec03e3258028a43bb4ab7b825122`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-email#subscribe-via-email
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-alert-email.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about subscribing or unsubscribing to TiDB Cloud alert notifications via email in the console, including permissions, navigation, and notification behavior.
- Retrieval Keywords: Subscribe via Email, TiDB Cloud email alert subscriptions, Alert Subscription, Project Settings, Add Subscriber, Subscriber Type, Email, Test Connection, Save, Unsubscribe, Project Owner, Organization Owner, TiDB Cloud Dedicated, Subscribe, Alert page, alert sends email notifications every three hours
- Follow-up Guidance: The source also states that alert subscription is for all alerts in the current project, a single subscription covers multiple clusters in the project, and you can also start from the cluster Alert page by clicking Subscribe.
- Classification Note: The classification is operation/cloud because the content describes TiDB Cloud console procedures for managing email alert subscriptions at the project level for TiDB Cloud Dedicated clusters.

## Official Source Content

# Subscribe via Email

TiDB Cloud provides you with an easy way to subscribe to alert notifications via email, [Slack](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-slack), and [Zoom](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-zoom). This document describes how to subscribe to alert notifications via email.

> **Note:**
>
> Currently, alert subscription is only available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.
## Prerequisites

- To subscribe to alert notifications of TiDB Cloud, you must have the `Organization Owner` access to your organization or `Project Owner` access to the target project in TiDB Cloud.
## Subscribe to alert notifications

> **Tip:**
>
> The alert subscription is for all alerts in the current project. If you have multiple clusters in the project, you just need to subscribe once.

To get alert notifications of clusters in your project, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Alert Subscription**.
3. On the **Alert Subscription** page, click **Add Subscriber** in the upper-right corner.
4. Select **Email** from the **Subscriber Type** drop-down list.
5. Enter your email address.
6. Click **Test Connection**.

    - If the test succeeds, the **Save** button is displayed.
    - If the test fails, an error message is displayed. Follow the message to troubleshoot the issue and then retry the connection.

7. Click **Save** to complete the subscription.

Alternatively, you can also click **Subscribe** in the upper-right corner of the [**Alert**](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-built-in-alerting#view-alerts) page of the cluster. You will be directed to the **Alert Subscriber** page.

If an alert condition remains unchanged, the alert sends email notifications every three hours.
## Unsubscribe from alert notifications

If you no longer want to receive alert notifications of clusters in your project, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Alert Subscription**.
3. On the **Alert Subscription** page, locate the row of your target subscriber to be deleted, and then click **...** > **Unsubscribe**.
4. Click **Unsubscribe** to confirm the unsubscription.
