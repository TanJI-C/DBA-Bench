# TiDB monitoring framework components overview

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-monitoring-framework.md`
- Source Title: `TiDB Monitoring Framework Overview`
- Source Heading Path: `TiDB Monitoring Framework Overview | TiDB Monitoring Framework Overview > About Prometheus in TiDB | TiDB Monitoring Framework Overview > About Grafana in TiDB | TiDB Monitoring Framework Overview > TiDB Dashboard`
- Source Line Ranges: `5-57`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `pd`, `tidb`, `tikv`, `br`, `lightning`, `ticdc`, `tiproxy`
- Topic Tags: `monitoring`, `metrics`, `prometheus`, `grafana`, `dashboard`, `alerting`, `visualization`, `observability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0111_87cb38ae8f`
- Source ID: `tidb-docs-8.1:tidb-monitoring-framework.md#tidb-monitoring-framework-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `428eb24d5aaa9b4541f10aa36e4be3fa2d94e8f5d022ebb0e3dede25ae146760`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework#tidb-monitoring-framework-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-monitoring-framework.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for the overall TiDB monitoring framework, including which tools store metrics, visualize metrics, provide alerting, and offer built-in cluster monitoring and diagnosis.
- Retrieval Keywords: TiDB monitoring framework overview, Prometheus in TiDB, Grafana in TiDB, TiDB Dashboard, Prometheus Server, Alertmanager, client libraries, time series data, monitoring and performance metrics, visualize metrics, monitoring and alerting, {TiDB_Cluster_name}-Overview, {TiDB_Cluster_name}-PD, {TiDB_Cluster_name}-TiDB, {TiDB_Cluster_name}-TiKV-Summary, {TiDB_Cluster_name}-TiKV-Details, {TiDB_Cluster_name}-TiKV-Trouble-Shooting, {TiDB_Cluster_name}-TiCDC, {TiDB_Cluster_name}-TiProxy-Summary, {TiDB_Cluster_name}-Lightning, {TiDB_Cluster_name}-Backup-Restore, {TiDB_Cluster_name}-Node_exporter, {TiDB_Cluster_name}-Disk-Performance, {TiDB_Cluster_name}-Blackbox_exporter
- Follow-up Guidance: The source also lists Grafana monitoring groups such as {TiDB_Cluster_name}-Overview, {TiDB_Cluster_name}-PD, {TiDB_Cluster_name}-TiDB, {TiDB_Cluster_name}-TiKV-Summary, {TiDB_Cluster_name}-TiCDC, and {TiDB_Cluster_name}-TiProxy-Summary.
- Classification Note: This chunk is classified as observability for self-managed TiDB because it describes Prometheus, Grafana, Alertmanager, and TiDB Dashboard as the cluster monitoring and visualization framework.

## Official Source Content

# TiDB Monitoring Framework Overview

The TiDB monitoring framework adopts two open source projects: Prometheus and Grafana. TiDB uses [Prometheus](https://prometheus.io) to store the monitoring and performance metrics and [Grafana](https://grafana.com/grafana) to visualize these metrics. TiDB also provides a built-in [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro) for monitoring and diagnosing TiDB clusters.
## About Prometheus in TiDB

As a time series database, Prometheus has a multi-dimensional data model and flexible query language. As one of the most popular open source projects, Prometheus has been adopted by many companies and organizations and has a very active community. PingCAP is one of the active developers and adopters of Prometheus for monitoring and alerting in TiDB, TiKV and PD.

Prometheus consists of multiple components. Currently, TiDB uses the following of them:

- The Prometheus Server to scrape and store time series data
- The client libraries to customize necessary metrics in the application
- An Alertmanager for the alerting mechanism

The diagram is as follows:

![diagram](/media/prometheus-in-tidb.png)
## About Grafana in TiDB

Grafana is an open source project for analyzing and visualizing metrics. TiDB uses Grafana to display the performance metrics as follows:

![Grafana monitored_groups](/media/grafana-monitored-groups.png)

- {TiDB_Cluster_name}-Backup-Restore: Monitoring metrics related to backup and restore.
- {TiDB_Cluster_name}-Binlog: Monitoring metrics related to TiDB Binlog.
- {TiDB_Cluster_name}-Blackbox_exporter: Monitoring metrics related to network probe.
- {TiDB_Cluster_name}-Disk-Performance: Monitoring metrics related to disk performance.
- {TiDB_Cluster_name}-Kafka-Overview: Monitoring metrics related to Kafka.
- {TiDB_Cluster_name}-Lightning: Monitoring metrics related to TiDB Lightning.
- {TiDB_Cluster_name}-Node_exporter: Monitoring metrics related to the operating system.
- {TiDB_Cluster_name}-Overview: Monitoring overview related to important components.
- {TiDB_Cluster_name}-PD: Monitoring metrics related to the PD server.
- {TiDB_Cluster_name}-Performance-Read: Monitoring metrics related to read performance.
- {TiDB_Cluster_name}-Performance-Write: Monitoring metrics related to write performance.
- {TiDB_Cluster_name}-TiDB: Detailed monitoring metrics related to the TiDB server.
- {TiDB_Cluster_name}-TiDB-Summary: Monitoring overview related to TiDB.
- {TiDB_Cluster_name}-TiFlash-Proxy-Summary: Monitoring overview of the proxy server that is used to replicate data to TiFlash.
- {TiDB_Cluster_name}-TiFlash-Summary: Monitoring overview related to TiFlash.
- {TiDB_Cluster_name}-TiKV-Details: Detailed monitoring metrics related to the TiKV server.
- {TiDB_Cluster_name}-TiKV-Summary: Monitoring overview related to the TiKV server.
- {TiDB_Cluster_name}-TiKV-Trouble-Shooting: Monitoring metrics related to the TiKV error diagnostics.
- {TiDB_Cluster_name}-TiCDC: Detailed monitoring metrics related to TiCDC.
- {TiDB_Cluster_name}-TiProxy-Summary: Monitoring overview related to TiProxy.

Each group has multiple panel labels of monitoring metrics, and each panel contains detailed information of multiple monitoring metrics. For example, the **Overview** monitoring group has five panel labels, and each labels corresponds to a monitoring panel. See the following UI:

![Grafana Overview](/media/grafana-monitor-overview.png)
## TiDB Dashboard

TiDB Dashboard is a web UI for monitoring, diagnosing, and managing the TiDB cluster, which is introduced in v4.0. It is built into the PD component and does not require an independent deployment. For more information, see [TiDB Dashboard introduction](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro).
