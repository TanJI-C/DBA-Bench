# Grafana and Prometheus monitoring architecture and metric flow

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/grafana-monitor-best-practices.md`
- Source Title: `Best Practices for Monitoring TiDB Using Grafana`
- Source Heading Path: `Best Practices for Monitoring TiDB Using Grafana | Best Practices for Monitoring TiDB Using Grafana > Monitoring architecture | Best Practices for Monitoring TiDB Using Grafana > Source and display of monitoring data`
- Source Line Ranges: `5-68`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiup`, `dashboard`
- Topic Tags: `grafana`, `prometheus`, `monitoring-architecture`, `metrics`, `http-interface`, `ports`, `query-expressions`, `qps`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0009_05d619de16`
- Source ID: `tidb-docs-8.1:best-practices/grafana-monitor-best-practices.md#best-practices-for-monitoring-tidb-using-grafana`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2bbf3263a40eaa188c2a379896032f58a33f6ea33474b527a70f7f25eb8668c7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/grafana-monitor-best-practices#best-practices-for-monitoring-tidb-using-grafana
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/grafana-monitor-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Grafana + Prometheus monitoring architecture, the metrics flow from component HTTP interfaces to Prometheus and Grafana, or the exact ports and metric example used to inspect SQL QPS.
- Retrieval Keywords: Grafana + Prometheus monitoring platform, Monitoring architecture, Source and display of monitoring data, TiDB server 10080, TiKV server 20180, PD server 2379, HTTP interface, curl http://__tidb_ip__:10080/metrics, tidb_executor_statement_total, QPS of a SQL statement, rate[1m], sum by type, Legend format, Resolution
- Follow-up Guidance: It also shows that the Grafana panel query expression uses the metric name `tidb_executor_statement_total` and explains items such as `rate[1m]`, `sum`, `by type`, `Legend format`, and `Resolution`.
- Classification Note: This chunk is classified as observability because it describes how TiDB, TiKV, and PD metrics are collected through HTTP interfaces and displayed through Prometheus and Grafana.

## Official Source Content

# Best Practices for Monitoring TiDB Using Grafana

When you [deploy a TiDB cluster using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) and have added Grafana and Prometheus in the topology configuration, a set of [Grafana + Prometheus monitoring platform](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework) is deployed simultaneously to collect and display metrics for various components and machines in the TiDB cluster. This document describes best practices for monitoring TiDB using Grafana. It aims to help you use metrics to analyze the status of the TiDB cluster and diagnose problems.
## Monitoring architecture

[Prometheus](https://prometheus.io/) is a time series database with a multi-dimensional data model and a flexible query language. [Grafana](https://grafana.com/) is an open source monitoring system for analyzing and visualizing metrics.

![The monitoring architecture in the TiDB cluster](/media/prometheus-in-tidb.png)

For TiDB 2.1.3 or later versions, TiDB monitoring supports the pull method. It is a good adjustment with the following benefits:

- There is no need to restart the entire TiDB cluster if you need to migrate Prometheus. Before adjustment, migrating Prometheus requires restarting the entire cluster because the target address needs to be updated.
- You can deploy 2 separate sets of Grafana + Prometheus monitoring platforms (not highly available) to prevent a single point of monitoring.
- The Pushgateway which might become a single point of failure is removed.
## Source and display of monitoring data

The three core components of TiDB (TiDB server, TiKV server and PD server) obtain metrics through the HTTP interface. These metrics are collected from the program code, and the default ports are as follows:

| Component   | Port  |
| :---------- |:----- |
| TiDB server | 10080 |
| TiKV server | 20180 |
| PD server   | 2379  |

Execute the following command to check the QPS of a SQL statement through the HTTP interface. Take the TiDB server as an example:

```bash
curl http://__tidb_ip__:10080/metrics |grep tidb_executor_statement_total
```

```
# Check the real-time QPS of different types of SQL statements. The numbers below are the cumulative values of counter type (scientific notation).
tidb_executor_statement_total{type="Delete"} 520197
tidb_executor_statement_total{type="Explain"} 1
tidb_executor_statement_total{type="Insert"} 7.20799402e+08
tidb_executor_statement_total{type="Select"} 2.64983586e+08
tidb_executor_statement_total{type="Set"} 2.399075e+06
tidb_executor_statement_total{type="Show"} 500531
tidb_executor_statement_total{type="Use"} 466016
```

The data above is stored in Prometheus and displayed on Grafana. Right-click the panel and then click the **Edit** button (or directly press the <kbd>E</kbd> key) shown in the following figure:

![The Edit entry for the Metrics tab](/media/best-practices/metric-board-edit-entry.png)

After clicking the **Edit** button, you can see the query expression with the `tidb_executor_statement_total` metric name on the Metrics tab. The meanings of some items on the panel are as follows:

- `rate[1m]`: The growth rate in one minute. It can only be used for the data of counter type.
- `sum`: The sum of values.
- `by type`: The summed data is grouped by type in the original metric value.
- `Legend format`: The format of the metric name.
- `Resolution`: The step width defaults to 15 seconds. Resolution means whether to generate one data point for multiple pixels.

The query expression on the **Metrics** tab is as follows:

![The query expression on the Metrics tab](/media/best-practices/metric-board-expression.jpeg)

Prometheus supports many query expressions and functions. For more details, refer to [Prometheus official website](https://prometheus.io/docs/prometheus/latest/querying).
