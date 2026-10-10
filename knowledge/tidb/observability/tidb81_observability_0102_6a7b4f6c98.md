# TiDB Cloud third-party metrics integrations overview and available providers

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/third-party-monitoring-integrations.md`
- Source Title: `Third-Party Metrics Integrations（Beta）`
- Source Heading Path: `Third-Party Metrics Integrations（Beta） | Third-Party Metrics Integrations（Beta） > Required access | Third-Party Metrics Integrations（Beta） > View or modify third-party integrations | Third-Party Metrics Integrations（Beta） > Limitation | Third-Party Metrics Integrations（Beta） > Available integrations | Third-Party Metrics Integrations（Beta） > Available integrations > Datadog integration (beta) | Third-Party Metrics Integrations（Beta） > Available integrations > Prometheus and Grafana integration (beta) | Third-Party Metrics Integrations（Beta） > Available integrations > New Relic integration (beta)`
- Source Line Ranges: `5-45`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `metrics`, `integrations`, `alerts`, `access-control`, `project-settings`, `limitations`, `datadog`, `prometheus`, `grafana`, `new-relic`, `beta`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0102_6a7b4f6c98`
- Source ID: `tidb-docs-8.1:tidb-cloud/third-party-monitoring-integrations.md#third-party-metrics-integrations-beta`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `555a50a01cb014d6ce89c7adcc94da725058734a6da0403a58dbb850ce9349e2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/third-party-monitoring-integrations#third-party-metrics-integrations-beta
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/third-party-monitoring-integrations.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiDB Cloud third-party metrics integrations, including required access, where to view or modify integrations in Project Settings, limitations by cluster tier or status, and which providers are available in beta.
- Retrieval Keywords: Third-Party Metrics Integrations (Beta), TiDB Cloud third-party metrics integrations, Organization Owner, Project Owner, Project Settings, Integrations, TiDB Cloud Serverless, CREATING, RESTORING, PAUSED, RESUMING, Datadog integration (beta), Prometheus and Grafana integration (beta), scrape_config, New Relic integration (beta), alerts, metrics services
- Follow-up Guidance: For detailed setup steps and metric lists, the source points to Integrate TiDB Cloud with Datadog, Integrate TiDB Cloud with Prometheus and Grafana, and Integrate TiDB Cloud with New Relic.
- Classification Note: The classification is observability for the cloud component because the content is about sending TiDB Cloud alert and metric data to external monitoring services and viewing cluster performance metrics.

## Official Source Content

# Third-Party Metrics Integrations（Beta）

You can integrate TiDB Cloud with third-party metrics services to receive TiDB Cloud alerts and view the performance metrics of your TiDB cluster using the metrics services. The third-party metrics integrations are currently in beta.
## Required access

To edit third-party integration settings, you must be in the `Organization Owner` role of your organization or the `Project Owner` role of the target project.
## View or modify third-party integrations

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Integrations**.

The available third-party integrations are displayed.
## Limitation

- For [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters, third-party metrics integrations are not supported.

- Third-party metrics integrations are not available when the cluster status is **CREATING**, **RESTORING**, **PAUSED**, or **RESUMING**.
## Available integrations
### Datadog integration (beta)

With the Datadog integration, you can configure TiDB Cloud to send metric data about your TiDB clusters to [Datadog](https://www.datadoghq.com/) and view these metrics in your Datadog dashboards.

For the detailed integration steps and a list of metrics that Datadog tracks, refer to [Integrate TiDB Cloud with Datadog](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-datadog-integration).
### Prometheus and Grafana integration (beta)

With the Prometheus and Grafana integration, you can get a `scrape_config` file for Prometheus from TiDB Cloud and use the content from the file to configure Prometheus. You can view these metrics in your Grafana dashboards.

For the detailed integration steps and a list of metrics that Prometheus tracks, see [Integrate TiDB Cloud with Prometheus and Grafana](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-prometheus-and-grafana-integration).
### New Relic integration (beta)

With the New Relic integration, you can configure TiDB Cloud to send metric data about your TiDB clusters to [New Relic](https://newrelic.com/) and view these metrics in your New Relic dashboards.

For the detailed integration steps and a list of metrics that New Relic tracks, see [Integrate TiDB Cloud with New Relic](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-new-relic-integration).
