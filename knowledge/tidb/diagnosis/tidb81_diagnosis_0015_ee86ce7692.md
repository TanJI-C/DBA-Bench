# Dashboard UI metrics and slow query errors

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-faq.md`
- Source Title: `TiDB Dashboard FAQs`
- Source Heading Path: `TiDB Dashboard FAQs > UI-related FAQ | TiDB Dashboard FAQs > UI-related FAQ > A `prometheus_not_found` error is shown in **QPS** and **Latency** sections on the Overview page | TiDB Dashboard FAQs > UI-related FAQ > An `invalid connection` error is shown on the **Slow Queries** page`
- Source Line Ranges: `26-60`
- Source Scope: `shared`
- Primary Component: `dashboard`
- Related Components: `pd`, `tidb`, `tiup`, `operator`
- Topic Tags: `ui`, `prometheus`, `metrics`, `overview`, `qps`, `latency`, `slow-queries`, `prepared-plan-cache`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0015_ee86ce7692`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-faq.md#ui-related-faq`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6f09677a08269981b1ebb5837a88986d9934e0c0cf2a7ab64edcca54d8da798b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-faq#ui-related-faq
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-faq.md

## Retrieval Guidance

- Use When: Use this chunk when TiDB Dashboard shows `prometheus_not_found` in the Overview page QPS or Latency sections, or `invalid connection` on the Slow Queries page.
- Retrieval Keywords: prometheus_not_found, Overview page, QPS, Latency, Prometheus deployed, metrics addresses, TiUP, TiDB Operator, tiup update --self, tiup update cluster --force, tiup cluster start CLUSTER_NAME, Slow Queries page, invalid connection, Prepared Plan Cache, tidb_enable_prepared_plan_cache = OFF
- Follow-up Guidance: The source includes TiUP commands to update TiUP and TiUP Cluster and to run `tiup cluster start CLUSTER_NAME`, and it identifies `tidb_enable_prepared_plan_cache = OFF` as the related system variable for the Slow Queries error.
- Classification Note: This is classified as diagnosis because the content maps specific Dashboard UI errors to missing Prometheus metrics reporting or Prepared Plan Cache behavior and provides troubleshooting context.

## Official Source Content

## UI-related FAQ
### A `prometheus_not_found` error is shown in **QPS** and **Latency** sections on the Overview page

The **QPS** and **Latency** sections on the **Overview** page require a cluster with Prometheus deployed. Otherwise, the error is shown. You can solve this problem by deploying a Prometheus instance in the cluster.

If you still encounter this problem when the Prometheus instance has been deployed, the possible reason is that your deployment tool is out of date (TiUP or TiDB Operator), and your tool does not automatically report metrics addresses, which makes TiDB Dashboard unable to query metrics. You can upgrade your deployment tool to the latest version and try again.

If your deployment tool is TiUP, take the following steps to solve this problem. For other deployment tools, refer to the corresponding documents of those tools.

1. Upgrade TiUP and TiUP Cluster:

    ```bash
    tiup update --self
    tiup update cluster --force
    ```

2. After the upgrade, when a new cluster is deployed with Prometheus instances, the metrics can be displayed normally.

3. After the upgrade, for an existing cluster, you can restart this cluster to report the metrics addresses. Replace `CLUSTER_NAME` with the actual cluster name:

    ```bash
    tiup cluster start CLUSTER_NAME
    ```

   Even if the cluster has been started, still execute this command. This command does not affect the normal application in the cluster, but refreshes and reports the metrics addresses, so that the monitoring metrics can be displayed normally in TiDB Dashboard.
### An `invalid connection` error is shown on the **Slow Queries** page

The possible reason is that you have enabled the Prepared Plan Cache feature of TiDB. As an experimental feature, when enabled, Prepared Plan Cache might not function properly in specific TiDB versions, which could cause this problem in TiDB Dashboard (and other applications). You can disable Prepared Plan Cache by setting the system variable [`tidb_enable_prepared_plan_cache = OFF`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_prepared_plan_cache-new-in-v610).
