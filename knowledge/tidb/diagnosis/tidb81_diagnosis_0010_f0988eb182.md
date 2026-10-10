# PD routing update delays and Prometheus query slowness

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/massive-regions-best-practices.md`
- Source Title: `Best Practices for TiKV Performance Tuning with Massive Regions`
- Source Heading Path: `Best Practices for TiKV Performance Tuning with Massive Regions > Other problems and solutions > PD routing information is not updated in time | Best Practices for TiKV Performance Tuning with Massive Regions > Other problems and solutions > Prometheus is slow to query metrics`
- Source Line Ranges: `164-176`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `dashboard`
- Topic Tags: `region-metadata`, `routing-information`, `pd-worker`, `pending-tasks`, `grafana`, `prometheus`, `metrics-query`, `large-scale-cluster`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0010_f0988eb182`
- Source ID: `tidb-docs-8.1:best-practices/massive-regions-best-practices.md#pd-routing-information-is-not-updated-in-time`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `97558916cecc424830c9e501130f4f23729668b4222c4089f9c3e69e26a1e112`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/massive-regions-best-practices#pd-routing-information-is-not-updated-in-time
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/massive-regions-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing delayed PD routing information updates or slow Grafana metric queries in a large-scale cluster with many Regions or many TiKV instances.
- Retrieval Keywords: PD routing information is not updated in time, Prometheus is slow to query metrics, pd-worker, Region Meta, approximate size / keys, routing information, Worker pending tasks, Task, TiKV Grafana, pending tasks, Region cache, large-scale cluster, metrics pre-calculation, Grafana, Prometheus
- Follow-up Guidance: The content says to check Worker pending tasks under Task in the TiKV Grafana panel to see whether pd-worker tasks are piled up, and notes that metrics pre-calculation is configured since v3.0.
- Classification Note: This is classified as diagnosis because the content describes symptoms, impact, and observable indicators such as pd-worker pending tasks and slow Prometheus queries.

## Official Source Content

### PD routing information is not updated in time

In TiKV, pd-worker regularly reports Region Meta information to PD. When TiKV is restarted or switches the Region leader, PD needs to recalculate Region's `approximate size / keys` through statistics. Therefore, with a large number of Regions, the single-threaded pd-worker might become the bottleneck, causing tasks to be piled up and not processed in time. In this situation, PD cannot obtain certain Region Meta information in time so that the routing information is not updated in time. This problem does not affect the actual reads and writes, but might cause inaccurate PD scheduling and require several round trips when TiDB updates Region cache.

You can check **Worker pending tasks** under **Task** in the **TiKV Grafana** panel to determine whether pd-worker has tasks piled up. Generally, `pending tasks` should be kept at a relatively low value.

![Check pd-worker](/media/best-practices/pd-worker-metrics.png)

pd-worker has been optimized for better performance since [v3.0.5](https://docs.pingcap.com/tidb/stable/releases/release-3.0.5#tikv). If you encounter a similar problem, it is recommended to upgrade to the latest version.
### Prometheus is slow to query metrics

In a large-scale cluster, as the number of TiKV instances increases, Prometheus has greater pressure to query metrics, making it slower for Grafana to display these metrics. To ease this problem, metrics pre-calculation is configured since v3.0.
