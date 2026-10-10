# Monitoring stack, logs, and TiDB Dashboard

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/tidb-best-practices.md`
- Source Title: `TiDB Best Practices`
- Source Heading Path: `TiDB Best Practices > Scenarios and practices > Monitoring and log`
- Source Line Ranges: `187-198`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tiup`, `tidb`, `tikv`, `pd`
- Topic Tags: `monitoring`, `grafana`, `prometheus`, `logs`, `dashboard`, `cluster-status`, `performance-analysis`, `log-search`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0013_67d3b9d0ef`
- Source ID: `tidb-docs-8.1:best-practices/tidb-best-practices.md#monitoring-and-log`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8019b5c0a5a6c3e4398a06a4b9c872e2efd30d70e3df818d8036eb24975e0633`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/tidb-best-practices#monitoring-and-log
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/tidb-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about the TiDB monitoring stack, Grafana and Prometheus deployment with TiUP, overview panel usage, component log file behavior, or accessing TiDB Dashboard for cluster status, performance analysis, traffic visualization, diagnostics, and log searching.
- Retrieval Keywords: Monitoring and log, Grafana + Prometheus, TiDB monitoring framework, TiUP, overview panel, tidb-server, tikv-server, pd-server, --log-file, stderr, automatically archived on a daily basis, TiDB Dashboard, http://${PD_IP}:${PD_PORT}/dashboard, cluster status, performance analysis, traffic visualization, cluster diagnostics, log searching
- Follow-up Guidance: The source states that TiDB Dashboard can be accessed at `http://${PD_IP}:${PD_PORT}/dashboard` and provides cluster status, performance analysis, traffic visualization, cluster diagnostics, and log searching.
- Classification Note: This is classified as observability for dashboard because the content is about monitoring metrics, logs, and the TiDB Dashboard interface for viewing system and cluster status.

## Official Source Content

### Monitoring and log

The monitoring metrics is the best method to learn the status of the system. It is recommended that you deploy the monitoring system along with your TiDB cluster.

TiDB uses [Grafana + Prometheus](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework) to monitor the system status. The monitoring system is automatically deployed and configured if you deploy TiDB using TiUP.

There are lots of items in the monitoring system, the majority of which are for TiDB developers. You do not have to understand these items without an in-depth knowledge of the source code. Some items that are related to applications or to the state of system key components are selected and put in a separate `overview` panel for users.

In addition to monitoring, you can also view the system logs. The three components of TiDB, tidb-server, tikv-server, and pd-server, each has a `--log-file` parameter. If this parameter has been configured when the cluster is started, logs are stored in the file configured by the parameter and log files are automatically archived on a daily basis. If the `--log-file` parameter has not been configured, the log is output to `stderr`.

Starting from TiDB 4.0, TiDB provides [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro) UI to improve usability. You can access TiDB Dashboard by visiting <http://${PD_IP}:${PD_PORT}/dashboard> in your browser. TiDB Dashboard provides features such as viewing cluster status, performance analysis, traffic visualization, cluster diagnostics, and log searching.
