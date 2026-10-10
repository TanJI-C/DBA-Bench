# TiDB Cloud metrics page access and retention

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/built-in-monitoring.md`
- Source Title: `TiDB Cloud Built-in Metrics`
- Source Heading Path: `TiDB Cloud Built-in Metrics | TiDB Cloud Built-in Metrics > View the Metrics page | TiDB Cloud Built-in Metrics > Metrics retention policy | TiDB Cloud Built-in Metrics > Metrics for TiDB Cloud Dedicated clusters`
- Source Line Ranges: `5-29`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`
- Topic Tags: `metrics`, `monitoring`, `retention`, `navigation`, `dedicated-clusters`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0087_243a1f6b48`
- Source ID: `tidb-docs-8.1:tidb-cloud/built-in-monitoring.md#tidb-cloud-built-in-metrics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e8a3a0ff1b920e57ee336392599a3fe44b066b1a4e8522b93bc5282334da121`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring#tidb-cloud-built-in-metrics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/built-in-monitoring.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs to find how to open the TiDB Cloud Metrics page or asks about metrics retention for TiDB Cloud Dedicated clusters and TiDB Cloud Serverless clusters.
- Retrieval Keywords: Metrics page, Clusters page, Monitoring > Metrics, combo box in the upper-left corner, switch between organizations, projects, and clusters, metrics retention policy, 7 days, TiDB Cloud Dedicated clusters, TiDB Cloud Serverless clusters
- Follow-up Guidance: It also states that the following sections illustrate the metrics on the Metrics page for TiDB Cloud Dedicated clusters.
- Classification Note: This is observability guidance because the content explains navigation to the Metrics page and states the retention period for collected metrics in TiDB Cloud.

## Official Source Content

# TiDB Cloud Built-in Metrics

TiDB Cloud collects and displays a full set of standard metrics of your cluster on the Metrics page. By viewing these metrics, you can easily identify performance issues and determine whether your current database deployment meets your requirements.
## View the Metrics page

To view the metrics on the **Metrics** page, take the following steps:

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target cluster to go to its overview page.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. In the left navigation pane, click **Monitoring** > **Metrics**.
## Metrics retention policy

For TiDB Cloud Dedicated clusters and TiDB Cloud Serverless clusters, the metrics data is kept for 7 days.
## Metrics for TiDB Cloud Dedicated clusters

The following sections illustrate the metrics on the **Metrics** page for TiDB Cloud Dedicated clusters.
