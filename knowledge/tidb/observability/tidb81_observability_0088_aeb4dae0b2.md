# Serverless cluster metrics and FAQ

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/built-in-monitoring.md`
- Source Title: `TiDB Cloud Built-in Metrics`
- Source Heading Path: `TiDB Cloud Built-in Metrics > Metrics for TiDB Cloud Serverless clusters | TiDB Cloud Built-in Metrics > Metrics for TiDB Cloud Serverless clusters > Cluster Status | TiDB Cloud Built-in Metrics > Metrics for TiDB Cloud Serverless clusters > Database Status | TiDB Cloud Built-in Metrics > FAQ`
- Source Line Ranges: `82-129`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`
- Topic Tags: `metrics`, `serverless-clusters`, `cluster-status`, `database-status`, `qps`, `request-units`, `storage`, `faq`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0088_aeb4dae0b2`
- Source ID: `tidb-docs-8.1:tidb-cloud/built-in-monitoring.md#metrics-for-tidb-cloud-serverless-clusters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d147a9fc8936f41b1be9d4ab4e399a8dfd3ef04e453ec901f999ca97afb136da`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring#metrics-for-tidb-cloud-serverless-clusters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/built-in-monitoring.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about built-in metrics for TiDB Cloud Serverless clusters, the Cluster Status and Database Status tabs, or the FAQ about empty panes and discontinuous metrics.
- Retrieval Keywords: Metrics for TiDB Cloud Serverless clusters, Cluster Status, Database Status, Request Units, RU per second, Used Storage Size, Row-based storage, Columnar storage, Query Per Second, Average Query Duration, Failed Query, Transaction Per Second, Average Transaction Duration, Total Connection, QPS Per DB, Average Query Duration Per DB, Failed Query Per DB, some panes empty, metrics discontinuous, cluster version is low, upgrade it to the latest version of TiDB, PingCAP support team, PingCAP Support
- Follow-up Guidance: The FAQ says empty panes can occur when the workload does not trigger a metric or the cluster version is low, and rare discontinuous metrics can happen when the metrics system experiences high pressure.
- Classification Note: This is observability content because it describes serverless metrics views and includes troubleshooting-oriented FAQ items for missing or discontinuous metrics.

## Official Source Content

## Metrics for TiDB Cloud Serverless clusters

The **Metrics** page provides two tabs for metrics of TiDB Cloud Serverless clusters:

- **Cluster Status**: displays the cluster-level main metrics.
- **Database Status**: displays the database-level main metrics.
### Cluster Status

The following table illustrates the cluster-level main metrics under the **Cluster Status** tab.

| Metric name  | Labels | Description                                   |
| :------------| :------| :-------------------------------------------- |
| Request Units | RU per second | The Request Unit (RU) is a unit of measurement used to track the resource consumption of a query or transaction. In addition to queries that you run, Request Units can be consumed by background activities, so when the QPS is 0, the Request Units per second might not be zero. |
| Used Storage Size | Row-based storage, Columnar storage | The size of the row store and the size of the column store. |
| Query Per Second | All, {SQL type} | The number of SQL statements executed per second, which are collected by SQL types, such as `SELECT`, `INSERT`, and `UPDATE`. |
| Average Query Duration | All, {SQL type} | The duration from receiving a request from the client to the TiDB Cloud Serverless cluster until the cluster executes the request and returns the result to the client. |
| Failed Query | All | The number of SQL statement execution errors per second. |
| Transaction Per Second | All | The number of transactions executed per second. |
| Average Transaction Duration | All | The average execution duration of transactions. |
| Total Connection | All | The number of connections to the TiDB Cloud Serverless cluster. |
### Database Status

The following table illustrates the database-level main metrics under the **Database Status** tab.

| Metric name  | Labels | Description                                   |
| :------------| :------| :-------------------------------------------- |
| QPS Per DB | All, {Database name} | The number of SQL statements executed per second on every database, which are collected by SQL types, such as `SELECT`, `INSERT`, and `UPDATE`. |
| Average Query Duration Per DB | All, {Database name} | The duration from receiving a request from the client to a database until the database executes the request and returns the result to the client.|
| Failed Query Per DB | All, {Database name} | The statistics of error types according to the SQL statement execution errors per second on every database.|
## FAQ

**1. Why are some panes empty on this page?**

If a pane does not provide any metrics, the possible reasons are as follows:

- The workload of the corresponding cluster does not trigger this metric. For example, the failed query metric is always empty in the case of no failed queries.
- The cluster version is low. You need to upgrade it to the latest version of TiDB to see these metrics.

If all these reasons are excluded, you can contact the [PingCAP support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for troubleshooting.

**2. Why might metrics be discontinuous in rare cases?**

In some rare cases, metrics might be lost, such as when the metrics system experiences high pressure.

If you encounter this problem, you can contact [PingCAP Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for troubleshooting.
