# TiDB Cloud New Relic integration setup and dashboard access

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-new-relic-integration.md`
- Source Title: `Integrate TiDB Cloud with New Relic (Beta)`
- Source Heading Path: `Integrate TiDB Cloud with New Relic (Beta) | Integrate TiDB Cloud with New Relic (Beta) > Prerequisites | Integrate TiDB Cloud with New Relic (Beta) > Limitation | Integrate TiDB Cloud with New Relic (Beta) > Steps | Integrate TiDB Cloud with New Relic (Beta) > Steps > Step 1. Integrate with your New Relic API Key | Integrate TiDB Cloud with New Relic (Beta) > Steps > Step 2. Add TiDB Cloud Dashboard in New Relic | Integrate TiDB Cloud with New Relic (Beta) > Pre-built dashboard`
- Source Line Ranges: `5-46`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`, `ecosystem`
- Topic Tags: `new relic`, `integration`, `api key`, `prerequisites`, `limitations`, `project settings`, `dashboard`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0249_31cbb7e380`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-new-relic-integration.md#integrate-tidb-cloud-with-new-relic-beta`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c043fa2f9b979697631c300d5ad6d28a20b70208fe65b461022ad224cf40e019`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-new-relic-integration#integrate-tidb-cloud-with-new-relic-beta
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-new-relic-integration.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Cloud New Relic integration prerequisites, limitation, setup steps, or how to access the pre-built dashboard.
- Retrieval Keywords: Integrate TiDB Cloud with New Relic (Beta), New Relic API key, Organization Owner, Project Member, Project Settings > Integrations, Integration to New Relic (BETA), Test Integration, Confirm, Add Data, TiDB Cloud Monitoring, Dashboard, TiDB Cloud Serverless clusters
- Follow-up Guidance: If the integration is added, you can log in to New Relic to create the TiDB Cloud dashboard or click the Dashboard link in the New Relic card of the integrations to view the pre-built dashboard.
- Classification Note: This is classified as configuration because the content describes prerequisites, access requirements, a limitation, and the console steps to integrate TiDB Cloud with New Relic and open its dashboard.

## Official Source Content

# Integrate TiDB Cloud with New Relic (Beta)

TiDB Cloud supports New Relic integration (beta). You can configure TiDB Cloud to send metric data of your TiDB clusters to [New Relic](https://newrelic.com/). After that, you can directly view these metrics in your New Relic dashboards.
## Prerequisites

- To integrate TiDB Cloud with New Relic, you must have a New Relic account and a [New Relic API key](https://one.newrelic.com/admin-portal/api-keys/home?). New Relic grants you an API key when you first create a New Relic account.

    If you do not have a New Relic account, sign up [here](https://newrelic.com/signup).

- To edit third-party integration settings for TiDB Cloud, you must have the **Organization Owner** access to your organization or **Project Member** access to the target project in TiDB Cloud.
## Limitation

You cannot use the New Relic integration in [TiDB Cloud Serverless clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless).
## Steps
### Step 1. Integrate with your New Relic API Key

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Integrations**.
3. On the **Integrations** page, click **Integration to New Relic (BETA)**.
4. Enter your API key of New Relic and choose the site of New Relic.
5. Click **Test Integration**.

    - If the test succeeds, the **Confirm** button is displayed.
    - If the test fails, an error message is displayed. Follow the message for troubleshooting and retry the integration.

6. Click **Confirm** to complete the integration.
### Step 2. Add TiDB Cloud Dashboard in New Relic

1. Log in to [New Relic](https://one.newrelic.com/).
2. Click **Add Data**, search for `TiDB Cloud`, and then go to the **TiDB Cloud Monitoring** page. Alternatively, you can click the [link](https://one.newrelic.com/marketplace?state=79bf274b-0c01-7960-c85c-3046ca96568e) to directly access the page.
3. Choose your account ID and create the dashboard in New Relic.
## Pre-built dashboard

Click the **Dashboard** link in the **New Relic** card of the integrations. You can see the pre-built dashboard of your TiDB clusters.
