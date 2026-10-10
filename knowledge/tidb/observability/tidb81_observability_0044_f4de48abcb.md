# Monitor, troubleshoot, and maintain HTAP components

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explore-htap.md`
- Source Title: `Explore HTAP`
- Source Heading Path: `Explore HTAP > Performance monitoring | Explore HTAP > Troubleshooting | Explore HTAP > What's next`
- Source Line Ranges: `98-122`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `tidb`, `pd`, `tikv`, `tiflash`, `ticdc`, `tiup`
- Topic Tags: `monitoring`, `dashboard`, `prometheus`, `grafana`, `alerting`, `slow-queries`, `expensive-queries`, `hotspot`, `troubleshooting`, `maintenance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0044_f4de48abcb`
- Source ID: `tidb-docs-8.1:explore-htap.md#performance-monitoring`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a4cdce2a611a05ad2b53956c29500263934f4101981609b1cd31aa2fc97f8239`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explore-htap#performance-monitoring
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explore-htap.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks where to monitor HTAP cluster status, which troubleshooting guides to consult for query or hotspot problems, or where to find TiFlash maintenance references.
- Retrieval Keywords: Performance monitoring, Troubleshooting, What's next, TiDB Dashboard, Monitoring system (Prometheus & Grafana), Grafana overview dashboard, alert rules, TiDB cluster alert rules, TiFlash alert rules, Analyze slow queries, Identify expensive queries, Troubleshoot hotspot issues, TiDB cluster troubleshooting guide, Troubleshoot a TiFlash Cluster, Maintain a TiFlash cluster, critical logs, system tables
- Follow-up Guidance: The source also points to Maintain a TiFlash cluster for checking TiFlash version, critical logs, and system tables, and to the TiFlash scale-out page for removing a specific TiFlash node.
- Classification Note: This chunk is classified as observability because it focuses on monitoring entry points, alert rules, troubleshooting references, and maintenance-oriented follow-up documents.

## Official Source Content

## Performance monitoring

When using TiDB, you can monitor the TiDB cluster status and performance metrics in either of the following ways:

- [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro): you can see the overall running status of the TiDB cluster, analyse distribution and trends of read and write traffic, and learn the detailed execution information of slow queries.
- [Monitoring system (Prometheus & Grafana)](https://docs.pingcap.com/tidb/stable/grafana-overview-dashboard): you can see the monitoring parameters of TiDB cluster-related components including PD, TiDB, TiKV, TiFlash, TiCDC, and Node_exporter.

To see the alert rules of TiDB cluster and TiFlash cluster, see [TiDB cluster alert rules](https://docs.pingcap.com/tidb/stable/alert-rules) and [TiFlash alert rules](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-alert-rules).
## Troubleshooting

If any issue occurs during using TiDB, refer to the following documents:

- [Analyze slow queries](https://docs.pingcap.com/tidb/stable/analyze-slow-queries)
- [Identify expensive queries](https://docs.pingcap.com/tidb/stable/identify-expensive-queries)
- [Troubleshoot hotspot issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues)
- [TiDB cluster troubleshooting guide](https://docs.pingcap.com/tidb/stable/troubleshoot-tidb-cluster)
- [Troubleshoot a TiFlash Cluster](https://docs.pingcap.com/tidb/stable/tiflash/troubleshoot-tiflash)

You are also welcome to create [GitHub Issues](https://github.com/pingcap/tiflash/issues) or ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs).
## What's next

- To check the TiFlash version, critical logs, system tables, see [Maintain a TiFlash cluster](https://docs.pingcap.com/tidb/stable/tiflash/maintain-tiflash).
- To remove a specific TiFlash node, see [Scale out a TiFlash cluster](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-out-a-tiflash-cluster).
