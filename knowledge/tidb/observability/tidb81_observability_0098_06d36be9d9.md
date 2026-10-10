# View monitoring metrics pages in TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-tidb-cluster.md`
- Source Title: `Monitor a TiDB Cluster`
- Source Heading Path: `Monitor a TiDB Cluster > Monitoring metrics | Monitor a TiDB Cluster > Monitoring metrics > Overview page | Monitor a TiDB Cluster > Monitoring metrics > Metrics page`
- Source Line Ranges: `55-90`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `monitoring`, `metrics`, `overview page`, `metrics page`, `navigation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0098_06d36be9d9`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-tidb-cluster.md#monitoring-metrics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f05510591b02cb2f7afbd845da6aba2b62f3b8fe07b16956cb21b12ca49bbe85`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-tidb-cluster#monitoring-metrics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-tidb-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when locating where to view cluster monitoring metrics in TiDB Cloud on the Overview page or the Metrics page.
- Retrieval Keywords: Monitoring metrics, Overview page, Metrics page, Clusters page, Core Metrics, Monitoring > Metrics, TiDB Cloud Built-in Metrics, cluster overview page
- Follow-up Guidance: The source points to TiDB Cloud Built-in Metrics for more information.
- Classification Note: This is classified as observability for TiDB Cloud because it describes the navigation paths and pages used to view cluster metrics.

## Official Source Content

## Monitoring metrics

In TiDB Cloud, you can view the commonly used metrics of a cluster from the following pages:

- **Overview** page
- **Metrics** page
### Overview page

The **Overview** page provides general metrics of a cluster.

To view metrics on the cluster overview page, take the following steps:

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target cluster to go to its overview page.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Check the **Core Metrics** section.
### Metrics page

The **Metrics** page provides a full set of metrics of a cluster. By viewing these metrics, you can easily identify performance issues and determine whether your current database deployment meets your requirements.

To view metrics on the **Metrics** page, take the following steps:

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target cluster to go to its overview page.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. In the left navigation pane, click **Monitoring** > **Metrics**.

For more information, see [TiDB Cloud Built-in Metrics](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring).
