# TiCDC architecture and deployment best practices

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-overview.md`
- Source Title: `TiCDC Overview`
- Source Heading Path: `TiCDC Overview > TiCDC architecture | TiCDC Overview > Best practices`
- Source Line Ranges: `55-88`
- Source Scope: `all`
- Primary Component: `ticdc`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `architecture`, `etcd`, `change-log`, `changefeed`, `downstream`, `high-availability`, `deployment-location`, `network-latency`, `valid-index`, `redo-log`, `disaster-recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0067_34dae0915c`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-overview.md#ticdc-architecture`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2cf31d29a188837dcc03c5150ded9dc28107e8f45928c76aed77504c8b5bc327`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview#ticdc-architecture
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiCDC architecture details, metadata storage in PD's etcd, supported downstream systems, or best practices for deployment location, valid indexes, and redo log in disaster recovery.
- Retrieval Keywords: TiCDC architecture, PD's etcd, changefeed, KV change logs, TiKV Server, PD, metadata, node status information, changefeed configurations, downstream systems, deploy TiCDC in upstream region, deploy TiCDC in downstream region, network latency higher than 100 ms, valid index, PRIMARY KEY, UNIQUE INDEX, NOT NULL, VIRTUAL GENERATED COLUMNS, redo log, disaster recovery, eventual consistency
- Follow-up Guidance: The content provides a follow-up to configure redo log and ensure the storage system where the redo log is written can be read normally when a disaster occurs in the upstream.
- Classification Note: This is classified as architecture because the content explains TiCDC components and replication flow, then adds deployment and schema prerequisites tied to that architecture.

## Official Source Content

## TiCDC architecture

TiCDC is an incremental data replication tool for TiDB, which is highly available through PD's etcd. The replication process consists of the following steps:

1. Multiple TiCDC processes pull data changes from TiKV nodes.
2. TiCDC sorts and merges the data changes.
3. TiCDC replicates the data changes to multiple downstream systems through multiple replication tasks (changefeeds).

The architecture of TiCDC is illustrated in the following figure:

![TiCDC architecture](/media/ticdc/cdc-architecture.png)

The components in the architecture diagram are described as follows:

- TiKV Server: TiKV nodes in a TiDB cluster. When data changes occur, TiKV nodes send the changes as change logs (KV change logs) to TiCDC nodes. If TiCDC nodes detect that the change logs are not continuous, they will actively request the TiKV nodes to provide change logs.
- TiCDC: TiCDC nodes where TiCDC processes run. Each node runs a TiCDC process. Each process pulls data changes from one or more tables in TiKV nodes and replicates the changes to the downstream system through the sink component.
- PD: The scheduling module in a TiDB cluster. This module is responsible for scheduling cluster data and usually consists of three PD nodes. PD provides high availability through the etcd cluster. In the etcd cluster, TiCDC stores its metadata, such as node status information and changefeed configurations.

As shown in the architecture diagram, TiCDC supports replicating data to TiDB, MySQL, Kafka, and storage services.
## Best practices

- When you use TiCDC to replicate data between two TiDB clusters, if the network latency between the two clusters is higher than 100 ms:

    - For TiCDC versions earlier than v6.5.2, it is recommended to deploy TiCDC in the region (IDC) where the downstream TiDB cluster is located.
    - With a series of improvements introduced starting from TiCDC v6.5.2, it is recommended to deploy TiCDC in the region (IDC) where the upstream TiDB cluster is located.

- TiCDC only replicates tables that have at least one valid index. A valid index is defined as follows:

    - A primary key (`PRIMARY KEY`) is a valid index.
    - A unique index (`UNIQUE INDEX`) is valid if every column of the index is explicitly defined as non-nullable (`NOT NULL`) and the index does not have a virtual generated column (`VIRTUAL GENERATED COLUMNS`).

- To ensure eventual consistency when using TiCDC for disaster recovery, you need to configure [redo log](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-mysql#eventually-consistent-replication-in-disaster-scenarios) and ensure that the storage system where the redo log is written can be read normally when a disaster occurs in the upstream.
