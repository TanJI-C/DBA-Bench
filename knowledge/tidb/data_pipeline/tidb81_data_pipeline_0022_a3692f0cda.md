# Replication, validation, and OLAP query tools

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ecosystem-tool-user-guide.md`
- Source Title: `TiDB Tools Overview`
- Source Heading Path: `TiDB Tools Overview > Data management tools > Incremental data replication - TiCDC | TiDB Tools Overview > Data management tools > Incremental log replication - TiDB Binlog | TiDB Tools Overview > Data management tools > sync-diff-inspector | TiDB Tools Overview > OLAP Query tool - TiSpark`
- Source Line Ranges: `115-148`
- Source Scope: `all`
- Primary Component: `ecosystem`
- Related Components: `ticdc`, `tidb`, `tikv`, `sql`
- Topic Tags: `incremental-replication`, `change-data-capture`, `binlog`, `validation`, `data-repair`, `olap`, `spark`, `htap`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0022_a3692f0cda`
- Source ID: `tidb-docs-8.1:ecosystem-tool-user-guide.md#incremental-data-replication-ticdc`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f826327f8fa7c51077a5379e1c07df54e2d029cb5227b1e30e7705f0dbaaff1b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ecosystem-tool-user-guide#incremental-data-replication-ticdc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ecosystem-tool-user-guide.md

## Retrieval Guidance

- Use When: Use this chunk when looking for tools for incremental replication from TiDB, binlog-based replication and backup, data comparison and repair, or Spark-based OLAP queries on TiKV.
- Retrieval Keywords: TiCDC, TiCDC Open Protocol, incremental data replication, pulling change logs from TiKV, TSO, TiDB Binlog, nearly real-time data replication, incremental backup files, sync-diff-inspector, compare data stored in the MySQL or TiDB databases, repair data, TiSpark, OLAP queries, HTAP, Spark, TiKV
- Follow-up Guidance: The chunk states that TiCDC targets TiDB clusters, MySQL, Kafka, and Confluent, TiDB Binlog targets TiDB clusters, MySQL, Kafka, or incremental backup files, and sync-diff-inspector compares MySQL or TiDB databases.
- Classification Note: This is classified as data_pipeline because most of the content covers replication, validation, and repair tools, while also including TiSpark as the OLAP query tool.

## Official Source Content

### Incremental data replication - TiCDC

[TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) is a tool used for replicating incremental data of TiDB by pulling change logs from TiKV. It can restore data to a state consistent with any TSO in upstream. TiCDC also provides the TiCDC Open Protocol to support other systems to subscribe to data changes.

The following are the basics of TiCDC:

- Source: TiDB clusters
- Target: TiDB clusters, MySQL, Kafka, and Confluent
- Supported TiDB versions: v4.0.6 and later versions
### Incremental log replication - TiDB Binlog

[TiDB Binlog](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview) is a tool that collects binlog for TiDB clusters and provides nearly real-time data replication and backup. You can use it for incremental data replication between TiDB clusters, such as making a TiDB cluster the secondary cluster of the primary TiDB cluster.

The following are the basics of TiDB Binlog:

- Source: TiDB clusters
- Target: TiDB clusters, MySQL, Kafka, or incremental backup files
- Supported TiDB versions: v2.1 and later versions
- Kubernetes support: Yes. See [TiDB Binlog Cluster Operations](https://docs.pingcap.com/tidb-in-kubernetes/stable/deploy-tidb-binlog) and [TiDB Binlog Drainer Configurations on Kubernetes](https://docs.pingcap.com/tidb-in-kubernetes/stable/configure-tidb-binlog-drainer) for details.
### sync-diff-inspector

[sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview) is a tool that compares data stored in the MySQL or TiDB databases. In addition, you can also use sync-diff-inspector to repair data in the scenario where a small amount of data is inconsistent.

The following are the basics of sync-diff-inspector:

- Source: MySQL/TiDB clusters
- Target: MySQL/TiDB clusters
- Supported TiDB versions: all versions
## OLAP Query tool - TiSpark

[TiSpark](https://docs.pingcap.com/tidb/stable/tispark-overview) is a product developed by PingCAP to address the complexity of OLAP queries. It combines strengths of Spark, and the features of distributed TiKV clusters and TiDB to provide a one-stop Hybrid Transactional and Analytical Processing (HTAP) solution.
