# TiDB Cloud alert viewing, rule editing, and notification subscription

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-built-in-alerting.md`
- Source Title: `TiDB Cloud Built-in Alerting`
- Source Heading Path: `TiDB Cloud Built-in Alerting | TiDB Cloud Built-in Alerting > View alerts | TiDB Cloud Built-in Alerting > Edit alert rules | TiDB Cloud Built-in Alerting > Subscribe to alert notifications`
- Source Line Ranges: `5-50`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `alerts`, `console`, `alert-rules`, `thresholds`, `notifications`, `email`, `slack`, `zoom`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0091_fbfc6a9010`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-built-in-alerting.md#tidb-cloud-built-in-alerting`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `59a54aa88b44e3aceab08505ba2de17f47f25bd31e1bceb11145be8a5c76160e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-built-in-alerting#tidb-cloud-built-in-alerting
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-built-in-alerting.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs TiDB Cloud console steps to view active or closed alerts, edit alert rules or thresholds, or subscribe to alert notifications for a cluster.
- Retrieval Keywords: TiDB Cloud Built-in Alerting, Alerts page, View alerts, Edit Rules, Status drop-down list, Closed, All, alert threshold, disable or enable alert rules, subscribe to alert notifications, Email, Slack, Zoom, TiDB Cloud console, Clusters page, TiDB Cloud Dedicated
- Follow-up Guidance: The source also notes that alert rule editing has limited capabilities, some alert rules do not support editing, and third-party monitoring and alerting integration can be considered for different trigger conditions, frequency, or downstream actions.
- Classification Note: This is classified under observability for the cloud component because it describes how TiDB Cloud users view alerts, modify built-in alert rules, and manage alert notification subscriptions in the console.

## Official Source Content

# TiDB Cloud Built-in Alerting

TiDB Cloud provides you with an easy way to view alerts, edit alert rules, and subscribe to alert notifications.

This document describes how to do these operations and provides the TiDB Cloud built-in alert conditions for your reference.

> **Note:**
>
> Currently, the alert feature is only available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.
## View alerts

In TiDB Cloud, you can view both active and closed alerts on the **Alerts** page.

1. In the [TiDB Cloud console](https://tidbcloud.com/), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Click the name of the target cluster. The cluster overview page is displayed.
3. Click **Alerts** in the left navigation pane.
4. The **Alerts** page displays the active alerts by default. You can view the information of each active alert such as the alert name, trigger time, and duration.
5. If you also want to view the closed alerts, just click the **Status** drop-down list and select **Closed** or **All**.
## Edit alert rules

In TiDB Cloud, you can edit the alert rules by disabling or enabling the alerts or updating the alert threshold.

1. On the **Alerts** page, click **Edit Rules**.
2. Disable or enable alert rules as needed.
3. Click **Edit** to update the threshold of an alert rule.

    > **Tip:**
    >
    > Currently, TiDB Cloud provides limited capabilities for alert rule editing. Some alert rules do not support editing. If you would like to configure different trigger conditions or frequency, or have alerts automatically trigger actions in downstream services like [PagerDuty](https://www.pagerduty.com/docs/guides/datadog-integration-guide/), consider using a [third-party monitoring and alerting integration](https://docs.pingcap.com/tidb/stable/tidb-cloud/third-party-monitoring-integrations).
## Subscribe to alert notifications

In TiDB Cloud, you can subscribe to alert notifications via one of the following methods:

- [Email](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-email)
- [Slack](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-slack)
- [Zoom](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-zoom)
