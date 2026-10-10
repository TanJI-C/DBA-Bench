# TiDB Cloud Datadog integration setup and dashboard access

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-datadog-integration.md`
- Source Title: `Integrate TiDB Cloud with Datadog (Beta)`
- Source Heading Path: `Integrate TiDB Cloud with Datadog (Beta) | Integrate TiDB Cloud with Datadog (Beta) > Prerequisites | Integrate TiDB Cloud with Datadog (Beta) > Limitation | Integrate TiDB Cloud with Datadog (Beta) > Steps | Integrate TiDB Cloud with Datadog (Beta) > Steps > Step 1. Integrate with your Datadog API Key | Integrate TiDB Cloud with Datadog (Beta) > Steps > Step 2. Install TiDB Cloud Integration in Datadog | Integrate TiDB Cloud with Datadog (Beta) > Pre-built dashboard`
- Source Line Ranges: `5-48`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`, `ecosystem`
- Topic Tags: `datadog`, `integration`, `api-key`, `prerequisites`, `limitations`, `project-settings`, `installation`, `dashboard`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0248_bb250ddce2`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-datadog-integration.md#integrate-tidb-cloud-with-datadog-beta`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e1b5080102bbbdf42112ba78a903485125e0323bccf4d2d3ba034aef8249d52`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-datadog-integration#integrate-tidb-cloud-with-datadog-beta
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-datadog-integration.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Cloud Datadog integration prerequisites, setup steps, limitations, or how to access the pre-built dashboard.
- Retrieval Keywords: Integrate TiDB Cloud with Datadog (Beta), Datadog API key, Project Settings > Integrations, Integration to Datadog (BETA), Test Integration, Confirm, TiDB Cloud Integration, Install Integration, TiDBCloud Cluster Overview, Dashboard List, Organization Owner, Project Member, TiDB Cloud Serverless, CREATING, RESTORING, PAUSED, RESUMING, pre-built dashboard
- Follow-up Guidance: After confirming the API key in TiDB Cloud, install the TiDB Cloud Integration in Datadog so the TiDBCloud Cluster Overview dashboard appears in Dashboard List.
- Classification Note: This is classified as configuration because the content describes required access, integration prerequisites, explicit setup steps, and availability limitations for connecting TiDB Cloud to Datadog.

## Official Source Content

# Integrate TiDB Cloud with Datadog (Beta)

TiDB Cloud supports Datadog integration (beta). You can configure TiDB Cloud to send metric data about your TiDB clusters to [Datadog](https://www.datadoghq.com/). After that, you can view these metrics in your Datadog dashboards directly.
## Prerequisites

- To integrate TiDB Cloud with Datadog, you must have a Datadog account and a [Datadog API key](https://app.datadoghq.com/organization-settings/api-keys). Datadog grants you an API key when you first create a Datadog account.

    If you do not have a Datadog account, sign up at [https://app.datadoghq.com/signup](https://app.datadoghq.com/signup).

- To edit third-party integration settings of TiDB Cloud, you must have the `Organization Owner` access to your organization or `Project Member` access to the target project in TiDB Cloud.
## Limitation

- You cannot use the Datadog integration in [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

- Datadog integrations are not available when the cluster status is **CREATING**, **RESTORING**, **PAUSED**, or **RESUMING**.
## Steps
### Step 1. Integrate with your Datadog API Key

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Integrations**.
3. On the **Integrations** page, click **Integration to Datadog (BETA)**.
4. Enter your API key of Datadog and choose the site of Datadog.
5. Click **Test Integration**.

    - If the test successes, the **Confirm** button is displayed.
    - If the test fails, an error message is displayed. Follow the message for troubleshooting and retry the integration.

6. Click **Confirm** to complete the integration.
### Step 2. Install TiDB Cloud Integration in Datadog

1. Log in to [Datadog](https://app.datadoghq.com).
2. Go to the **TiDB Cloud Integration** page ([https://app.datadoghq.com/account/settings#integrations/tidb-cloud](https://app.datadoghq.com/account/settings#integrations/tidb-cloud)) in Datadog.
3. In the **Configuration** tab, click **Install Integration**. The [**TiDBCloud Cluster Overview**](https://app.datadoghq.com/dash/integration/30586/tidbcloud-cluster-overview) dashboard is displayed in your [**Dashboard List**](https://app.datadoghq.com/dashboard/lists).
## Pre-built dashboard

Click the **Dashboard** link in the **Datadog** card of the integrations. You can see the pre-built dashboard of your TiDB clusters.
