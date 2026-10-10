# TiDB Cloud alert subscription via Zoom

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-alert-zoom.md`
- Source Title: `Subscribe via Zoom`
- Source Heading Path: `Subscribe via Zoom | Subscribe via Zoom > Prerequisites | Subscribe via Zoom > Subscribe to alert notifications | Subscribe via Zoom > Subscribe to alert notifications > Step 1. Add the Zoom Incoming Webhook app | Subscribe via Zoom > Subscribe to alert notifications > Step 2. Generate a Zoom webhook URL | Subscribe via Zoom > Subscribe to alert notifications > Step 3. Subscribe from TiDB Cloud | Subscribe via Zoom > Unsubscribe from alert notifications`
- Source Line Ranges: `5-75`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `alerting`, `notifications`, `zoom`, `webhook`, `subscription`, `project-settings`, `prerequisites`, `unsubscription`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0090_68b4e91ca3`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-alert-zoom.md#subscribe-via-zoom`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `99bce920432e331b93a0f45d0d57f62b7dfaab186c44399296a396d2f02489c3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-zoom#subscribe-via-zoom
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-alert-zoom.md

## Retrieval Guidance

- Use When: Use this when the question is about subscribing or unsubscribing TiDB Cloud alert notifications through Zoom using a webhook in Project Settings.
- Retrieval Keywords: Subscribe via Zoom, TiDB Cloud alert notifications, Zoom, Incoming Webhook app, Zoom App Marketplace, Team Chat, /inc connect ${connectionName}, Endpoint, Verification Token, Project Settings > Alert Subscription, Add Subscriber, Subscriber Type, Test Connection, Unsubscribe, TiDB Cloud Dedicated, Enterprise support plan, Premium support plan, Organization Owner, Project Owner
- Follow-up Guidance: The content also covers prerequisites, generating the Zoom webhook URL and verification token, testing the connection, project-wide alert scope, repeated notifications every three hours when an alert condition remains unchanged, and the unsubscribe steps.
- Classification Note: This is classified as observability for the cloud component because it describes alert subscription and notification management in TiDB Cloud using Zoom webhooks.

## Official Source Content

# Subscribe via Zoom

TiDB Cloud provides you with an easy way to subscribe to alert notifications via [Zoom](https://www.zoom.com/), [Slack](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-slack), and [email](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-email). This document describes how to subscribe to alert notifications via Zoom.

> **Note:**
>
> Currently, alert subscription is only available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.
## Prerequisites

- The subscribing via Zoom feature is only available for organizations that subscribe to the **Enterprise** or **Premium** support plan.

- To subscribe to alert notifications of TiDB Cloud, you must have the `Organization Owner` access to your organization or `Project Owner` access to the target project in TiDB Cloud.

- To add and configure the Incoming Webhook Chatbot in Zoom, you need to have admin permissions on your Zoom account.
## Subscribe to alert notifications
### Step 1. Add the Zoom Incoming Webhook app

1. Sign in to the [Zoom App Marketplace](https://marketplace.zoom.us/) as the account administrator.
2. Go to the [Incoming Webhook App](https://marketplace.zoom.us/apps/eH_dLuquRd-VYcOsNGy-hQ) page in the Zoom App Marketplace, and then click **Add** to add this app. If the app is not pre-approved, contact your Zoom admin to approve this app for your account. For more information, see [Approving apps and managing app requests](https://support.zoom.us/hc/en-us/articles/360027829671). 
3. Confirm the permissions the app requires, then click **Authorize** to add the Incoming Webhook app.
### Step 2. Generate a Zoom webhook URL

1. Sign in to the Zoom desktop client.
2. Click the **Team Chat** tab.
3. Under **Apps**, find and select **Incoming Webhook**, or select a chat channel from above that you would like to receive messages in.
4. Enter the following command to make a new connection. You need to replace `${connectionName}` with your desired connection name, for example, `tidbcloud-alerts`:

    ```shell
    /inc connect ${connectionName}
    ```

5. The command will return the following details:

   - **Endpoint**. It will provide a webhook URL in the format: `https://integrations.zoom.us/chat/webhooks/incomingwebhook/XXXXXXXXXXXXXXXXXXXXXXXX`.
   - **Verification Token**
### Step 3. Subscribe from TiDB Cloud

> **Tip:**
>
> The alert subscription is for all alerts in the current project. If you have multiple clusters in the project, you just need to subscribe once.

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Alert Subscription**.
3. On the **Alert Subscription** page, click **Add Subscriber** in the upper-right corner.
4. Select **Zoom** from the **Subscriber Type** drop-down list.
5. Enter a name in the **Name** field, your Zoom webhook URL in the **URL** field, and the verification token in the **Token** field.
6. Click **Test Connection**.

    - If the test succeeds, the **Save** button is displayed.
    - If the test fails, an error message is displayed. Follow the message for troubleshooting and retry the connection.

7. Click **Save** to complete the subscription.

Alternatively, you can also click **Subscribe** in the upper-right corner of the **Alert** page of the cluster. You will be directed to the **Alert Subscriber** page.

If an alert condition remains unchanged, the alert sends notifications every three hours.
## Unsubscribe from alert notifications

If you no longer want to receive alert notifications of clusters in your project, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Alert Subscription**.
3. On the **Alert Subscription** page, locate the row of your target subscriber to be deleted, and then click **...** > **Unsubscribe**.
4. Click **Unsubscribe** to confirm the unsubscription.
