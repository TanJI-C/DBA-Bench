# TiDB Cloud Prometheus and Grafana integration setup

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-prometheus-and-grafana-integration.md`
- Source Title: `Integrate TiDB Cloud with Prometheus and Grafana (Beta)`
- Source Heading Path: `Integrate TiDB Cloud with Prometheus and Grafana (Beta) | Integrate TiDB Cloud with Prometheus and Grafana (Beta) > Prerequisites | Integrate TiDB Cloud with Prometheus and Grafana (Beta) > Limitation | Integrate TiDB Cloud with Prometheus and Grafana (Beta) > Steps | Integrate TiDB Cloud with Prometheus and Grafana (Beta) > Steps > Step 1. Get a scrape_config file for Prometheus | Integrate TiDB Cloud with Prometheus and Grafana (Beta) > Steps > Step 2. Integrate with Prometheus | Integrate TiDB Cloud with Prometheus and Grafana (Beta) > Steps > Step 3. Use Grafana GUI dashboards to visualize the metrics | Integrate TiDB Cloud with Prometheus and Grafana (Beta) > Best practice of rotating scrape_config`
- Source Line Ranges: `5-77`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `prometheus`, `grafana`, `integration`, `scrape_config`, `bearer-token`, `prerequisites`, `limitations`, `dashboard`, `token-rotation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0250_dca760ac8a`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-prometheus-and-grafana-integration.md#integrate-tidb-cloud-with-prometheus-and-grafana-beta`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fc5f522b5efd73171416868b1e8b6175d98ef5dd9bc2e05450bbfb5719c6119b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-prometheus-and-grafana-integration#integrate-tidb-cloud-with-prometheus-and-grafana-beta
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-prometheus-and-grafana-integration.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented setup, prerequisites, limitations, scrape_config handling, Grafana dashboard import, or bearer token rotation process for integrating TiDB Cloud with Prometheus and Grafana.
- Retrieval Keywords: Integrate TiDB Cloud with Prometheus and Grafana (Beta), Prometheus API endpoint (beta), scrape_config, bearer token, Project Settings > Integrations, Integration to Prometheus (BETA), Status > Targets, /etc/prometheus/prometheus.yml, Grafana dashboard JSON, rotate scrape_config, TiDB Cloud Serverless, CREATING RESTORING PAUSED RESUMING
- Follow-up Guidance: The source also includes the best practice of rotating scrape_config by creating a new file, confirming Prometheus can still read from TiDB Cloud, removing the old file content, and deleting the old scrape_config file from the Integrations page.
- Classification Note: This is classified as configuration because the content describes prerequisites, integration limitations, console navigation, Prometheus scrape_configs changes, Grafana dashboard import, and scrape_config bearer token management for TiDB Cloud.

## Official Source Content

# Integrate TiDB Cloud with Prometheus and Grafana (Beta)

TiDB Cloud provides a [Prometheus](https://prometheus.io/) API endpoint (beta). If you have a Prometheus service, you can monitor key metrics of TiDB Cloud from the endpoint easily.

This document describes how to configure your Prometheus service to read key metrics from the TiDB Cloud endpoint and how to view the metrics using [Grafana](https://grafana.com/).
## Prerequisites

- To integrate TiDB Cloud with Prometheus, you must have a self-hosted or managed Prometheus service.

- To edit third-party integration settings of TiDB Cloud, you must have the `Organization Owner` access to your organization or `Project Member` access to the target project in TiDB Cloud.
## Limitation

- You cannot use the Prometheus and Grafana integration in [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

- Prometheus and Grafana integrations are not available when the cluster status is **CREATING**, **RESTORING**, **PAUSED**, or **RESUMING**.
## Steps
### Step 1. Get a scrape_config file for Prometheus

Before configuring your Prometheus service to read metrics of TiDB Cloud, you need to generate a `scrape_config` YAML file in TiDB Cloud first. The `scrape_config` file contains a unique bearer token that allows the Prometheus service to monitor any database clusters in the current project.

To get the `scrape_config` file for Prometheus, do the following:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Integrations**.
3. On the **Integrations** page, click **Integration to Prometheus (BETA)**.
4. Click **Add File** to generate and show the scrape_config file for the current project.

5. Make a copy of the `scrape_config` file content for later use.

    > **Note:**
    >
    > For security reasons, TiDB Cloud only shows a newly generated `scrape_config` file once. Ensure that you copy the content before closing the file window. If you forget to do so, you need to delete the `scrape_config` file in TiDB Cloud and generate a new one. To delete a `scrape_config` file, select the file, click **...**, and then click **Delete**.
### Step 2. Integrate with Prometheus

1. In the monitoring directory specified by your Prometheus service, locate the Prometheus configuration file.

    For example, `/etc/prometheus/prometheus.yml`.

2. In the Prometheus configuration file, locate the `scrape_configs` section, and then copy the `scrape_config` file content obtained from TiDB Cloud to the section.

3. In your Prometheus service, check **Status** > **Targets** to confirm that the new `scrape_config` file has been read. If not, you might need to restart the Prometheus service.
### Step 3. Use Grafana GUI dashboards to visualize the metrics

After your Prometheus service is reading metrics from TiDB Cloud, you can use Grafana GUI dashboards to visualize the metrics as follows:

1. Download the Grafana dashboard JSON of TiDB Cloud [here](https://github.com/pingcap/docs/blob/master/tidb-cloud/monitor-prometheus-and-grafana-integration-grafana-dashboard-UI.json).

2. [Import this JSON to your own Grafana GUI](https://grafana.com/docs/grafana/v8.5/dashboards/export-import/#import-dashboard) to visualize the metrics. 
    
    > **Note:**
    >
    > If you are already using Prometheus and Grafana to monitor TiDB Cloud and want to incorporate the newly available metrics, it is recommended that you create a new dashboard instead of directly updating the JSON of the existing one.

3. (Optional) Customize the dashboard as needed by adding or removing panels, changing data sources, and modifying display options.

For more information about how to use Grafana, see [Grafana documentation](https://grafana.com/docs/grafana/latest/getting-started/getting-started-prometheus/).
## Best practice of rotating scrape_config

To improve data security, it is a general best practice to periodically rotate `scrape_config` file bearer tokens.

1. Follow [Step 1](#step-1-get-a-scrape_config-file-for-prometheus) to create a new `scrape_config` file for Prometheus.
2. Add the content of the new file to your Prometheus configuration file.
3. Once you have confirmed that your Prometheus service is still able to read from TiDB Cloud, remove the content of the old `scrape_config` file from your Prometheus configuration file.
4. On the **Integrations** page of your project, delete the corresponding old `scrape_config` file to block anyone else from using it to read from the TiDB Cloud Prometheus endpoint.
