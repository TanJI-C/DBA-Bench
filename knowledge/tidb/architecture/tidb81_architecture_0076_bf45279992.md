# TiDB Cloud node types: TiDB, TiKV, and TiFlash

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/architecture-concepts.md`
- Source Title: `Architecture`
- Source Heading Path: `Architecture > Nodes | Architecture > Nodes > TiDB node | Architecture > Nodes > TiKV node | Architecture > Nodes > TiFlash node`
- Source Line Ranges: `54-104`
- Source Scope: `cloud`
- Primary Component: `shared`
- Related Components: `cloud`, `tidb`, `tikv`, `tiflash`, `tiproxy`
- Topic Tags: `nodes`, `sql-layer`, `storage`, `columnar-storage`, `regions`, `transactions`, `replication`, `scalability`, `high-availability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0076_bf45279992`
- Source ID: `tidb-docs-8.1:tidb-cloud/architecture-concepts.md#nodes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `891c8f7fe1cc33a853be21c36f5ebc9d900b0a8794c24fa61b0c78d68381f159`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/architecture-concepts#nodes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/architecture-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when describing the roles of TiDB, TiKV, and TiFlash nodes in a TiDB Cloud cluster or how node management differs between Dedicated and Serverless.
- Retrieval Keywords: Nodes, TiDB node, TiKV node, TiFlash node, TiDB Cloud Dedicated cluster, TiDB Cloud Serverless cluster, stateless SQL layer, MySQL-compatible endpoint, distributed execution plans, TiProxy, HAProxy, row-based storage, columnar storage, distributed transactional key-value storage engine, Regions, Key Range, StartKey, EndKey, Snapshot Isolation, default isolation level, three replicas, automatic failover, high availability, analytical acceleration, vector search index, TiFlash replicas
- Follow-up Guidance: For more information about managing node number and size in TiDB Cloud Dedicated, the source refers to Scalability.
- Classification Note: This is classified as architecture because the content explains the cluster node types and their storage, SQL processing, replication, scalability, and analytical roles in TiDB Cloud.

## Official Source Content

## Nodes

In TiDB Cloud, each cluster consists of TiDB, TiKV, and TiFlash nodes.

- In a TiDB Cloud Dedicated cluster, you can fully manage the number and size of your dedicated TiDB, TiKV, and TiFlash nodes according to your performance requirements. For more information, see [Scalability](https://docs.pingcap.com/tidb/stable/tidb-cloud/scalability-concepts).
- In a TiDB Cloud Serverless cluster, the number and size of TiDB, TiKV, and TiFlash nodes are automatically managed. This ensures seamless scaling, eliminating the need for users to handle node configuration or management tasks.
### TiDB node

A [TiDB node](https://docs.pingcap.com/tidb/stable/tidb-computing) is a stateless SQL layer that connects to applications using a MySQL-compatible endpoint. It handles tasks like parsing, optimizing, and creating distributed execution plans for SQL queries.

You can deploy multiple TiDB nodes to scale horizontally and manage higher workloads. These nodes work with load balancers, such as TiProxy or HAProxy, to provide a seamless interface. TiDB nodes do not store data themselves---they forward data requests to TiKV nodes for row-based storage or TiFlash nodes for columnar storage.
### TiKV node

A [TiKV node](https://docs.pingcap.com/tidb/stable/tikv-overview) is the backbone of data storage in the TiDB architecture, serving as a distributed transactional key-value storage engine that delivers reliability, scalability, and high availability.

**Key features:**

- **Region-based data storage**

    - Data is divided into [Regions](https://docs.pingcap.com/tidb/dev/glossary#regionpeerraft-group), each covering a specific Key Range (left-closed, right-open interval: `StartKey` to `EndKey`).
    - Multiple Regions coexist within each TiKV node to ensure efficient data distribution.

- **Transactional support**

    - TiKV nodes provide native distributed transaction support at the key-value level, ensuring Snapshot Isolation as the default isolation level.
    - The TiDB node translates SQL execution plans into calls to the TiKV node API, enabling seamless SQL-level transaction support.

- **High availability**

    - All data in TiKV nodes is replicated (default: three replicas) for durability.
    - TiKV ensures native high availability and supports automatic failover, safeguarding against node failures.

- **Scalability and reliability**

    - TiKV nodes are designed to handle expanding datasets while maintaining distributed consistency and fault tolerance.
### TiFlash node

A [TiFlash node](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview) is a specialized type of storage node within the TiDB architecture. Unlike ordinary TiKV nodes, TiFlash is designed for analytical acceleration with a columnar storage model.

**Key features:**

- **Columnar storage**

    TiFlash nodes store data in a columnar format, making them optimized for analytical queries and significantly improving performance for read-intensive workloads.

- **Vector search index support**

    The vector search index feature uses TiFlash replicas for tables, enabling advanced search capabilities and improving efficiency in complex analytical scenarios.
