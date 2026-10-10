# Monitoring FAQ metrics, retention, and dashboard meanings

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/monitor-faq.md`
- Source Title: `TiDB Monitoring FAQs`
- Source Heading Path: `TiDB Monitoring FAQs | TiDB Monitoring FAQs > Is there a better way of monitoring the key metrics? | TiDB Monitoring FAQs > The Prometheus monitoring data is deleted every 15 days by default. Could I set it to two months or delete the monitoring data manually? | TiDB Monitoring FAQs > Region Health monitor | TiDB Monitoring FAQs > What is the meaning of `selectsimplefull` in Statement Count monitor? | TiDB Monitoring FAQs > What is the difference between `QPS` and `Statement OPS` in the monitor?`
- Source Line Ranges: `5-37`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `pd`
- Topic Tags: `monitoring`, `prometheus`, `grafana`, `metrics`, `retention`, `region-health`, `statement-count`, `qps`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0046_62bb9d8d8e`
- Source ID: `tidb-docs-8.1:faq/monitor-faq.md#tidb-monitoring-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `43a474511b556973533cf930cad695256e6e5f093b67e477e2a2c2a717ff81d6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/monitor-faq#tidb-monitoring-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/monitor-faq.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiDB monitoring basics in Grafana and Prometheus, Prometheus retention settings, PD Region Health meanings, or the difference between QPS and Statement OPS.
- Retrieval Keywords: Prometheus, Grafana, Overview of the Monitoring Framework, Key Metrics, --storage.tsdb.retention="60d", Prometheus monitoring data deleted every 15 days by default, Region Health, PD metric monitoring page, miss, extra, label, level-1, level-0, location label, selectsimplefull, full table scan, Statement Count monitor, QPS, Statement OPS, use database, load data, begin, commit, set, show, insert, select, update
- Follow-up Guidance: The source also points to Overview of the Monitoring Framework and Key Metrics for more details about the Prometheus monitoring framework and key monitoring metrics.
- Classification Note: This chunk is classified as observability because it explains monitoring with Prometheus and Grafana, metric meanings on dashboards, and retention-related monitoring data settings.

## Official Source Content

# TiDB Monitoring FAQs

This document summarizes the FAQs related to TiDB monitoring.

- For details of Prometheus monitoring framework, see [Overview of the Monitoring Framework](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework).
- For details of key metrics of monitoring, see [Key Metrics](https://docs.pingcap.com/tidb/stable/grafana-overview-dashboard).
## Is there a better way of monitoring the key metrics?

The monitoring system of TiDB consists of Prometheus and Grafana. From the dashboard in Grafana, you can monitor various running metrics of TiDB which include the monitoring metrics of system resources, of client connection and SQL operation, of internal communication and Region scheduling. With these metrics, the database administrator can better understand the system running status, running bottlenecks and so on. In the practice of monitoring these metrics, we list the key metrics of each TiDB component. Generally you only need to pay attention to these common metrics. For details, see [official documentation](https://docs.pingcap.com/tidb/stable/grafana-overview-dashboard).
## The Prometheus monitoring data is deleted every 15 days by default. Could I set it to two months or delete the monitoring data manually?

Yes. Find the startup script on the machine where Prometheus is started, edit the startup parameter and restart Prometheus.

```
--storage.tsdb.retention="60d"
```
## Region Health monitor

In TiDB 2.0, Region health is monitored in the PD metric monitoring page, in which the `Region Health` monitoring item shows the statistics of all the Region replica status. `miss` means shortage of replicas and `extra` means the extra replica exists. In addition, `Region Health` also shows the isolation level by `label`. `level-1` means the Region replicas are isolated physically in the first `label` level. All the Regions are in `level-0` when `location label` is not configured.
## What is the meaning of `selectsimplefull` in Statement Count monitor?

It means full table scan but the table might be a small system table.
## What is the difference between `QPS` and `Statement OPS` in the monitor?

The `QPS` statistics is about all the SQL statements, including `use database`, `load data`, `begin`, `commit`, `set`, `show`, `insert` and `select`.

The `Statement OPS` statistics is only about applications related SQL statements, including `select`, `update` and `insert`, therefore the `Statement OPS` statistics matches the applications better.
