# TiDB Cloud Slack alert subscription setup and removal

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-alert-slack.md`
- Source Title: `Subscribe via Slack`
- Source Heading Path: `Subscribe via Slack | Subscribe via Slack > Prerequisites | Subscribe via Slack > Subscribe to alert notifications | Subscribe via Slack > Subscribe to alert notifications > Step 1. Generate a Slack webhook URL | Subscribe via Slack > Subscribe to alert notifications > Step 2. Subscribe from TiDB Cloud | Subscribe via Slack > Unsubscribe from alert notifications`
- Source Line Ranges: `5-65`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `alerts`, `slack`, `webhook`, `subscription`, `prerequisites`, `project-settings`, `notifications`, `unsubscribe`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0089_236108db2a`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-alert-slack.md#subscribe-via-slack`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fb96aabe5844e181d23b204201f24f287580ffdff92ab4b9f9b8f0f4d9afc42e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-slack#subscribe-via-slack
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-alert-slack.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud procedure, prerequisites, or scope for subscribing or unsubscribing alert notifications via Slack webhook.
- Retrieval Keywords: Subscribe via Slack, TiDB Cloud Slack alert notifications, Alert Subscription, Project Settings > Alert Subscription, Add Subscriber, Subscriber Type, Slack webhook URL, Incoming Webhooks, Activate Incoming Webhooks, Add New Webhook to Workspace, Test Connection, Save, Unsubscribe, TiDB Cloud Dedicated, Enterprise support plan, Premium support plan, Organization Owner, Project Owner
- Follow-up Guidance: The source also states that the subscription applies to all alerts in the current project, that you can alternatively start from the cluster Alert page via Subscribe, and that unchanged alert conditions send notifications every three hours.
- Classification Note: This is observability content for the cloud component because it describes TiDB Cloud alert notification subscription and removal through Slack in the TiDB Cloud console.

## Official Source Content

# Subscribe via Slack

TiDB Cloud provides you with an easy way to subscribe to alert notifications via [Slack](https://slack.com/), [email](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-email), and [Zoom](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-zoom). This document describes how to subscribe to alert notifications via Slack.

The following screenshot shows two example alerts.

![TiDB Cloud Alerts in Slack](/media/tidb-cloud/tidb-cloud-alert-subscription.png)

> **Note:**
>
> Currently, alert subscription is only available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.
## Prerequisites

- The subscribing via Slack feature is only available for organizations that subscribe to the **Enterprise** or **Premium** support plan.

- To subscribe to alert notifications of TiDB Cloud, you must have the `Organization Owner` access to your organization or `Project Owner` access to the target project in TiDB Cloud.
## Subscribe to alert notifications
### Step 1. Generate a Slack webhook URL

1. [Create a Slack app](https://api.slack.com/apps/new), if you do not have one already. Click **Create New App**, and choose **From scratch**. Enter a name, choose a workspace to associate your app with, and then click **Create App**.
2. Go to the settings page for your app. You can load its settings via your [app's management dashboard](https://api.slack.com/apps).
3. Click the **Incoming Webhooks** tab, and then toggle **Activate Incoming Webhooks** to **ON**.
4. Click **Add New Webhook to Workspace**.
5. Select a channel that you want to receive alert notifications in, and then select **Authorize**. If you need to add the incoming webhook to a private channel, you must first be in that channel.

You can see a new entry under the **Webhook URLs for Your Workspace** section in the following format: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`.
### Step 2. Subscribe from TiDB Cloud

> **Tip:**
>
> The alert subscription is for all alerts in the current project. If you have multiple clusters in the project, you just need to subscribe once.

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Alert Subscription**.
3. On the **Alert Subscription** page, click **Add Subscriber** in the upper-right corner.
4. Select **Slack** from the **Subscriber Type** drop-down list.
5. Enter a name in the **Name** field and your Slack webhook URL in the **URL** field.
6. Click **Test Connection**.

    - If the test succeeds, the **Save** button is displayed.
    - If the test fails, an error message is displayed. Follow the message to troubleshoot the issue and retry the connection.

7. Click **Save** to complete the subscription.

Alternatively, you can also click **Subscribe** in the upper-right corner of the **Alert** page of the cluster. You will be directed to the **Alert Subscriber** page.

If an alert condition remains unchanged, the alert sends notifications every three hours.
## Unsubscribe from alert notifications

If you no longer want to receive alert notifications of clusters in your project, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Alert Subscription**.
3. On the **Alert Subscription** page, locate the row of your target subscriber to be deleted, and then click **...** > **Unsubscribe**.
4. Click **Unsubscribe** to confirm the unsubscription.
