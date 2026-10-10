# Monitoring page access and dashboard overview

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-monitoring.md`
- Source Title: `TiDB Dashboard Monitoring Page`
- Source Heading Path: `TiDB Dashboard Monitoring Page | TiDB Dashboard Monitoring Page > Access the page | TiDB Dashboard Monitoring Page > Key Metrics on Performance Overview`
- Source Line Ranges: `5-31`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `pd`, `tikv`, `tiup`
- Topic Tags: `monitoring`, `performance-overview`, `dashboard-access`, `grafana`, `metrics-overview`, `workload-profile`, `latency-breakdown`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0028_adfed671a1`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-monitoring.md#tidb-dashboard-monitoring-page`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d93cede6823dab14a80cfea12d8f9976cfbec6107bff2a9b37d73583ec1bb9c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-monitoring#tidb-dashboard-monitoring-page
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-monitoring.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants to access the TiDB Dashboard Monitoring page or understand what the Performance Overview dashboard shows across TiDB, PD, and TiKV.
- Retrieval Keywords: TiDB Dashboard Monitoring Page, Monitoring, Performance Overview dashboard, Access the page, Grafana, TiUP, TiDB Monitoring Framework Overview, database time overview, workload profile, SQL latency breakdown, Overview, Load profile, Top-down latency breakdown
- Follow-up Guidance: If the user needs the specific metrics in Overview, Load profile, or Top-down latency breakdown, continue to the sections that list those key metrics on Performance Overview.
- Classification Note: The content is classified as observability for the dashboard component because it describes how to open the Monitoring page and what monitoring sections and performance views it provides.

## Official Source Content

# TiDB Dashboard Monitoring Page

On the monitoring page, you can view the Performance Overview dashboard, a performance analysis and tuning tool introduced in TiDB v6.1.0. With the Performance Overview dashboard, you can analyze performance efficiently, and confirm whether the bottleneck of user response time is in the database. If the bottleneck is in the database, you can identify the bottleneck inside the database, with database time overview, workload profile and SQL latency breakdown. For details, see [Performance Analysis and Tuning](https://docs.pingcap.com/tidb/stable/performance-tuning-methods).
## Access the page

Log in to TiDB dashboard and click **Monitoring** from the left navigation bar. The Performance Overview dashboard is displayed.

![Monitoring page](/media/dashboard/dashboard-monitoring.png)

If the TiDB cluster is deployed using TiUP, you can also view the Performance Overview dashboard on Grafana. In this deployment mode, the monitoring system (Prometheus & Grafana) is deployed at the same time. For more information, see [TiDB Monitoring Framework Overview](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework).

![performance overview](/media/performance/grafana_performance_overview.png)
## Key Metrics on Performance Overview

The Performance Overview dashboard orchestrates the metrics of TiDB, PD, and TiKV, and presents each of them in the following sections:

- Overview: Database time and SQL execution time summary. By checking different colors in the overview, you can quickly identify the database workload profile and the performance bottleneck.

- Load profile: Key metrics and resource usage, including database QPS, connection information, the MySQL command types the application interacts with TiDB, database internal TSO and KV request OPS, and resource usage of the TiKV and TiDB.

- Top-down latency breakdown: Query latency versus connection idle time ratio, query latency breakdown, TSO/KV request latency during execution, breakdown of write latency within TiKV.

The following sections illustrate the metrics on the Performance Overview dashboard.
