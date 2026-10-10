# TiCDC overview, usage scenarios, and replication features

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-overview.md`
- Source Title: `TiCDC Overview`
- Source Heading Path: `TiCDC Overview | TiCDC Overview > Usage scenarios | TiCDC Overview > Major features | TiCDC Overview > Major features > Key capabilities | TiCDC Overview > Major features > Replication order | TiCDC Overview > Major features > Replication consistency`
- Source Line Ranges: `5-54`
- Source Scope: `all`
- Primary Component: `ticdc`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `overview`, `usage-scenarios`, `incremental-replication`, `changefeed`, `mysql-sink`, `kafka-sink`, `replication-order`, `replication-consistency`, `redo-log`, `eventual-consistency`, `high-availability`, `open-api`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0075_c3d3d0c45f`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-overview.md#ticdc-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7d8a878d7cb79faf17d055b1eab0be809a57476d5b5239ecb1af445b81938887`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview#ticdc-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you need an overview of TiCDC usage scenarios, supported downstream targets, changefeed-related capabilities, or the documented replication order and consistency behavior of MySQL sink and Kafka sink.
- Retrieval Keywords: TiCDC Overview, usage scenarios, incremental data replication, changefeed, MySQL sink, Kafka sink, Canal-JSON, Avro, Debezium, Open API, at least once, Resolved TS, replication order, replication consistency, redo log, eventual consistency, second-level RPO, minute-level RTO, bidirectional replication, multi-active TiDB
- Follow-up Guidance: For detailed replication capabilities, Open API, sink protocols, or the transaction-atomicity sink URI parameter, the content points to the corresponding TiCDC documentation pages.
- Classification Note: This is classified as data_pipeline because the content describes how TiCDC replicates incremental changes to downstream systems and explains ordering and consistency properties of that replication.

## Official Source Content

# TiCDC Overview

[TiCDC](https://github.com/pingcap/tiflow/tree/release-8.1/cdc) is a tool used to replicate incremental data from TiDB. Specifically, TiCDC pulls TiKV change logs, sorts captured data, and exports row-based incremental data to downstream databases. For detailed data replication capabilities, see [TiCDC Data Replication Capabilities](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-data-replication-capabilities).
## Usage scenarios

TiCDC has multiple usage scenarios, including:

- Providing high availability and disaster recovery solutions for multiple TiDB clusters. TiCDC ensures eventual data consistency between primary and secondary clusters in case of a disaster.
- Replicating real-time data changes to homogeneous systems. This provides data sources for various scenarios, such as monitoring, caching, global indexing, data analysis, and primary-secondary replication between heterogeneous databases.
## Major features
### Key capabilities

TiCDC has the following key capabilities:

- Replicating incremental data between TiDB clusters with second-level RPO and minute-level RTO.
- Bidirectional replication between TiDB clusters, allowing the creation of a multi-active TiDB solution using TiCDC.
- Replicating incremental data from a TiDB cluster to a MySQL database or other MySQL-compatible databases with low latency.
- Replicating incremental data from a TiDB cluster to a Kafka cluster. The recommended data format includes [Canal-JSON](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-canal-json), [Avro](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-avro-protocol), and [Debezium](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-debezium).
- Replicating incremental data from a TiDB cluster to storage services, such as Amazon S3, GCS, Azure Blob Storage, and NFS.
- Replicating tables with the ability to filter databases, tables, DMLs, and DDLs.
- High availability with no single point of failure, supporting dynamically adding and deleting TiCDC nodes.
- Cluster management through [Open API](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2), including querying task status, dynamically modifying task configuration, and creating or deleting tasks.
### Replication order

- For all DDL or DML statements, TiCDC outputs them **at least once**.
- When the TiKV or TiCDC cluster encounters a failure, TiCDC might send the same DDL/DML statement repeatedly. For duplicated DDL/DML statements:

    - The MySQL sink can execute DDL statements repeatedly. For DDL statements that can be executed repeatedly in the downstream, such as `TRUNCATE TABLE`, the statement is executed successfully. For those that cannot be executed repeatedly, such as `CREATE TABLE`, the execution fails, and TiCDC ignores the error and continues with the replication process.
    - The Kafka sink provides different strategies for data distribution.
        - You can distribute data to different Kafka partitions based on the table, primary key, or timestamp. This ensures that the updated data of a row is sent to the same partition in order.
        - All these distribution strategies send `Resolved TS` messages to all topics and partitions periodically. This indicates that all messages earlier than the `Resolved TS` have already been sent to the topics and partitions. The Kafka consumer can use the `Resolved TS` to sort the messages received.
        - The Kafka sink sometimes sends duplicated messages, but these duplicated messages do not affect the constraints of `Resolved Ts`. For example, if a changefeed is paused and then resumed, the Kafka sink might send `msg1`, `msg2`, `msg3`, `msg2`, and `msg3` in order. You can filter out the duplicated messages from Kafka consumers.
### Replication consistency

- MySQL sink

    - TiCDC enables the redo log to ensure eventual consistency of data replication.
    - TiCDC ensures that the order of single-row updates is consistent with the upstream.
    - TiCDC does not ensure that the downstream transactions are executed in the same order as the upstream transactions.

    > **Note:**
    >
    > Since v6.2, you can use the sink URI parameter [`transaction-atomicity`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-mysql#configure-sink-uri-for-mysql-or-tidb) to control whether to split single-table transactions. Splitting single-table transactions can greatly reduce the latency and memory consumption of replicating large transactions.
