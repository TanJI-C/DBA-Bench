# TiKV FastTune dashboard overview

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-tikv-dashboard.md`
- Source Title: `Key Monitoring Metrics of TiKV`
- Source Heading Path: `Key Monitoring Metrics of TiKV > TiKV-FastTune dashboard`
- Source Line Ranges: `568-578`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tikv`, `tidb`
- Topic Tags: `fasttune`, `performance`, `diagnostics`, `qps`, `latency`, `write-workload`, `storage-side`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0044_7636ea1130`
- Source ID: `tidb-docs-8.1:grafana-tikv-dashboard.md#tikv-fasttune-dashboard`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d3191c90343c54a04ab05b069be4a44e5437265febc6376fa8b549421ddacd97`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#tikv-fasttune-dashboard
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-tikv-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing TiKV performance issues such as QPS jitter, latency jitter, or increasing latency and you need the overview of what the TiKV-FastTune dashboard is for.
- Retrieval Keywords: TiKV-FastTune dashboard, QPS jitter, latency jitter, latency increasing trend, write workload, storage side, write-RPC QPS, possible cause, left-Y-axis, right-Y-axis, graphs drawn upside down, dashboard user manual
- Follow-up Guidance: The source says to first check TiDB-related dashboards for write-related performance issues, and if the issues are at the storage side, open the TiKV-FastTune page and browse every panel.
- Classification Note: This is classified as diagnosis content because it describes how the TiKV-FastTune dashboard helps investigate TiKV performance problems and interpret its graphs.

## Official Source Content

## TiKV-FastTune dashboard

If performance issues of TiKV occur, such as QPS jitter, latency jitter, and latency increasing trend, you can check the **TiKV-FastTune** dashboard. This dashboard contains a set of panels that help you with diagnostics, especially when the write workload in your cluster is medium or large.

When write-related performance issues occur, you can first check the TiDB-related dashboards. If the issues are at the storage side, open the **TiKV-FastTune** page, browse and check every panel on it.

In the **TiKV-FastTune** dashboard, you can see a title that suggests a possible cause of the performance issues. To check whether the suggested cause is true, check the graph on the page.

The left-Y-axis of the graph represents the write-RPC QPS of the storage side, and a set of graphs on the right-Y-axis are drawn upside down. If the shape of the left graph matches that of the right graphs, the suggested cause is true.

For detailed metrics and descriptions, see the dashboard [user manual](https://docs.google.com/presentation/d/1aeBF2VCKf7eo4-3TMyP7oPzFWIih6UBA53UI8YQASCQ/edit#slide=id.gab6b984c2a_1_352).
