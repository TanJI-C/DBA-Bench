# TiCDC replication capabilities, scope, downstreams, and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-data-replication-capabilities.md`
- Source Title: `TiCDC Data Replication Capabilities`
- Source Heading Path: `TiCDC Data Replication Capabilities | TiCDC Data Replication Capabilities > How TiCDC works | TiCDC Data Replication Capabilities > Supported downstream systems | TiCDC Data Replication Capabilities > Scope of data replication | TiCDC Data Replication Capabilities > Limitations`
- Source Line Ranges: `5-64`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tikv`, `tidb`
- Topic Tags: `change-data-capture`, `replication`, `downstream-sinks`, `ddl`, `dml`, `limitations`, `eventual-consistency`, `redo-log`, `syncpoint`, `foreign-key-checks`, `classic-architecture`, `new-architecture`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0763_cdd77611f1`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-data-replication-capabilities.md#ticdc-data-replication-capabilities`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4cb1e85be0406603ea450dc59fb87c1b5cf8e8dcd64e48c8bfb1e7a8f3739a91`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-data-replication-capabilities#ticdc-data-replication-capabilities
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-data-replication-capabilities.md

## Retrieval Guidance

- Use When: Use this chunk when asking what TiCDC replicates, which downstream systems it supports, how it handles DDL and DML from TiKV change logs, or what replication limitations and consistency guarantees are documented.
- Retrieval Keywords: TiCDC Data Replication Capabilities, TiCDC listens to TiKV change logs, Raft logs, row-level data changes, INSERT, UPDATE, DELETE, logical operations equivalent to SQL semantics, eventual consistency, redo log, Syncpoint, supported downstream systems, TiDB database, MySQL-compatible databases, Apache Kafka, Pulsar, storage services, Amazon S3, GCS, Azure Blob Storage, NFS, Snowflake, ksqlDB, SQL Server via Confluent Cloud integration, Apache Flink, scope of data replication, DDL and DML statements excluding system tables, ADD INDEX, CREATE INDEX, asynchronous execution, ADD FOREIGN KEY, foreign_key_checks, SET SESSION foreign_key_checks = OFF;, mysql.*, information_schema.*, temporary tables, DQL, DCL, unsupported scenarios, schema mismatches, DROP COLUMN, changefeed filter out all DDL events, classic architecture, new architecture, recommended number of tables to be replicated, partitioned tables treated as separate table, more than one million tables per changefeed
- Follow-up Guidance: The source also points to related documentation for how TiCDC processes data changes, downstream sink guides, unsupported scenarios, and architecture-specific scaling guidance.
- Classification Note: This is reference content because it summarizes TiCDC replication behavior, supported downstream targets, replicated statement scope, and documented limitations rather than giving a step-by-step procedure.

## Official Source Content

# TiCDC Data Replication Capabilities

[TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) (TiDB Change Data Capture) is a core component in the TiDB ecosystem for real-time data replication. This document provides a detailed explanation of TiCDC data replication capabilities.
## How TiCDC works

- TiCDC listens to TiKV change logs (Raft logs) and converts row-level data changes (`INSERT`, `UPDATE`, and `DELETE` operations) into downstream-compatible SQL statements. TiCDC does not rely on the original SQL statements executed on the upstream database. For details, see [how TiCDC processes data changes](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview#implementation-of-processing-data-changes).

- TiCDC generates logical operations (such as `INSERT`, `UPDATE`, and `DELETE`) equivalent to SQL semantics, rather than restoring the original SQL statements executed on the upstream database one by one. For details, see [how TiCDC processes data changes](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview#implementation-of-processing-data-changes).

- TiCDC ensures eventual consistency of transactions. With [redo log](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-mysql#eventually-consistent-replication-in-disaster-scenarios) enabled, TiCDC can guarantee eventual consistency in disaster recovery scenarios. With [Syncpoint](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-upstream-downstream-check#enable-syncpoint) enabled, TiCDC supports consistent snapshot reads and data consistency validation.
## Supported downstream systems

TiCDC supports replicating data to various downstream systems, including the following:

- [TiDB database or other MySQL-compatible databases](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-mysql)
- [Apache Kafka](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka)
- Message Queue (MQ)-type sinks, such as [Pulsar](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-pulsar)
- [Storage services (Amazon S3, GCS, Azure Blob Storage, and NFS)](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-cloud-storage)
- [Snowflake, ksqlDB, SQL Server via Confluent Cloud integration](https://docs.pingcap.com/tidb/stable/ticdc/integrate-confluent-using-ticdc)
- [Apache Flink for consuming Kafka-replicated data](https://docs.pingcap.com/tidb/stable/replicate-data-to-kafka)
## Scope of data replication

TiCDC supports the following types of upstream data changes:

+ **Supported:**

    - DDL and DML statements (excluding system tables).
    - Index operations (`ADD INDEX`, `CREATE INDEX`): to reduce the impact on changefeed replication latency, if the downstream is TiDB, TiCDC [asynchronously executes the `ADD INDEX` and `CREATE INDEX` DDL operations](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-ddl#asynchronous-execution-of-add-index-and-create-index-ddls).
    - Foreign key constraint DDL statements (`ADD FOREIGN KEY`): TiCDC does **not** replicate upstream system variable settings. You need to manually configure [`foreign_key_checks`](https://docs.pingcap.com/tidb/stable/system-variables#foreign_key_checks) in the downstream to determine whether the downstream foreign key constraint check is enabled. Additionally, when writing data to the downstream, TiCDC automatically enables the session-level setting `SET SESSION foreign_key_checks = OFF;`. Therefore, even if global foreign key checks are enabled in the downstream, the data written by TiCDC will not trigger foreign key constraint validation.

+ **Not supported**:

    - DDL and DML statements executed in upstream system tables (including `mysql.*` and `information_schema.*`).
    - DDL and DML statements executed in upstream temporary tables.
    - DQL (Data Query Language) and DCL (Data Control Language) statements.
## Limitations

- TiCDC does not support certain scenarios. For details, see [unsupported scenarios](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview#unsupported-scenarios).
- TiCDC only verifies the integrity of upstream data changes. It does not validate whether the changes conform to upstream or downstream constraints. If the data violates downstream constraints, TiCDC will return an error when writing to the downstream.

    For example: When a changefeed is configured to filter out all DDL events, if the upstream executes a `DROP COLUMN` operation but continues to write `INSERT` statements involving that column, TiCDC will fail to replicate these DML changes to the downstream because of table schema mismatches.

- For the TiCDC [classic architecture](https://docs.pingcap.com/tidb/stable/ticdc-classic-architecture/), when the number of tables replicated by a single TiCDC cluster exceeds the following recommended values, TiCDC might not work stably:

    | TiCDC version | Recommended number of tables to be replicated |
    |---|:---:|
    | v5.4.0 - v6.4.x | 2000 |
    | v6.5.x - v7.4.x | 4000 |
    | v7.5.x - v8.5.x | 40000 |

    > **Note:**
    >
    > When replicating partitioned tables, TiCDC treats each partition as a separate table. Therefore, the partition count is included when TiCDC calculates the total number of tables to be replicated.

    If the number of tables to be replicated exceeds the preceding recommended values, it is recommended to use the [TiCDC new architecture](https://docs.pingcap.com/tidb/stable/ticdc-architecture/). The new architecture supports replicating more than one million tables per changefeed, making it suitable for large-scale replication scenarios.
