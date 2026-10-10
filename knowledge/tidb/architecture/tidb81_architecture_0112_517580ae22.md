# TiFlash architecture and key features

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-overview.md`
- Source Title: `TiFlash Overview`
- Source Heading Path: `TiFlash Overview | TiFlash Overview > Architecture | TiFlash Overview > Key features | TiFlash Overview > Key features > Asynchronous replication | TiFlash Overview > Key features > Consistency | TiFlash Overview > Key features > Intelligent choice | TiFlash Overview > Key features > Computing acceleration`
- Source Line Ranges: `5-82`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `tikv`, `pd`
- Topic Tags: `htap`, `columnar-storage`, `raft-learner`, `snapshot-isolation`, `mvcc`, `coprocessor`, `replication`, `consistency`, `query-optimization`, `pushdown`, `workload-isolation`, `placement-rules`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0112_517580ae22`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-overview.md#tiflash-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b62e1a8ba6fbccf878a8b070a147af2983072699646de2601ee5bea3f6d5a269`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#tiflash-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-overview.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving an overview of TiFlash architecture, consistency, replication, optimizer behavior, and deployment characteristics in an HTAP TiDB cluster.
- Retrieval Keywords: TiFlash Overview, TiFlash architecture, HTAP, columnar storage extension of TiKV, Raft Learner, asynchronous replication, Snapshot Isolation, MVCC, Multi-Raft, Region replica, coprocessor, ClickHouse, placement rules, PD, TiDB optimizer, Intelligent choice, Computing acceleration, pushdown calculations, AVX2, ARMv8, workload isolation, TiSpark compatibility
- Follow-up Guidance: For table-level replication setup and pushed-down computation details, the content points to Create TiFlash replicas for tables and Supported pushdown calculations.
- Classification Note: The classification is architecture because the content explains TiFlash design, major components, replication and consistency mechanisms, optimizer selection, and how TiFlash integrates with TiDB, TiKV, PD, and TiSpark.

## Official Source Content

# TiFlash Overview

[TiFlash](https://github.com/pingcap/tiflash) is the key component that makes TiDB essentially a Hybrid Transactional/Analytical Processing (HTAP) database. As a columnar storage extension of TiKV, TiFlash provides both good isolation level and strong consistency guarantee.

In TiFlash, the columnar replicas are asynchronously replicated according to the Raft Learner consensus algorithm. When these replicas are read, the Snapshot Isolation level of consistency is achieved by validating Raft index and multi-version concurrency control (MVCC).

With TiDB Cloud, you can create an HTAP cluster easily by specifying one or more TiFlash nodes according to your HTAP workload. If the TiFlash node count is not specified when you create the cluster or you want to add more TiFlash nodes, you can change the node count by [scaling the cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/scale-tidb-cluster).
## Architecture

![TiFlash Architecture](/media/tidb-storage-architecture-1.png)

The above figure is the architecture of TiDB in its HTAP form, including TiFlash nodes.

TiFlash provides the columnar storage, with a layer of coprocessors efficiently implemented by ClickHouse. Similar to TiKV, TiFlash also has a Multi-Raft system, which supports replicating and distributing data in the unit of Region (see [Data Storage](https://www.pingcap.com/blog/tidb-internal-data-storage/) for details).

TiFlash conducts real-time replication of data in the TiKV nodes at a low cost that does not block writes in TiKV. Meanwhile, it provides the same read consistency as in TiKV and ensures that the latest data is read. The Region replica in TiFlash is logically identical to those in TiKV, and is split and merged along with the Leader replica in TiKV at the same time.

To deploy TiFlash under the Linux AMD64 architecture, the CPU must support the AVX2 instruction set. Ensure that `cat /proc/cpuinfo | grep avx2` has output. To deploy TiFlash under the Linux ARM64 architecture, the CPU must support the ARMv8 instruction set architecture. Ensure that `cat /proc/cpuinfo | grep 'crc32' | grep 'asimd'` has output. By using the instruction set extensions, TiFlash's vectorization engine can deliver better performance.

TiFlash is compatible with both TiDB and TiSpark, which enables you to freely choose between these two computing engines.

It is recommended that you deploy TiFlash in different nodes from TiKV to ensure workload isolation. It is also acceptable to deploy TiFlash and TiKV in the same node if no business isolation is required.

Currently, data cannot be written directly into TiFlash. You need to write data in TiKV and then replicate it to TiFlash, because it connects to the TiDB cluster as a Learner role. TiFlash supports data replication in the unit of table, but no data is replicated by default after deployment. To replicate data of a specified table, see [Create TiFlash replicas for tables](https://docs.pingcap.com/tidb/stable/tiflash/create-tiflash-replicas#create-tiflash-replicas-for-tables).

TiFlash consists of two main components: the columnar storage component, and the TiFlash proxy component. The TiFlash proxy component is responsible for the communication using the Multi-Raft consensus algorithm.

After receiving a DDL command to create replicas for a table in TiFlash, TiDB automatically creates the corresponding [placement rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules) in PD, and then PD performs the corresponding data scheduling based on these rules.
## Key features

TiFlash has the following key features:

- [Asynchronous replication](#asynchronous-replication)
- [Consistency](#consistency)
- [Intelligent choice](#intelligent-choice)
- [Computing acceleration](#computing-acceleration)
### Asynchronous replication

The replica in TiFlash is asynchronously replicated as a special role, Raft Learner. This means when the TiFlash node is down or high network latency occurs, applications in TiKV can still proceed normally.

This replication mechanism inherits two advantages of TiKV: automatic load balancing and high availability.

- TiFlash does not rely on additional replication channels, but directly receives data from TiKV in a many-to-many manner.
- As long as the data is not lost in TiKV, you can restore the replica in TiFlash at any time.
### Consistency

TiFlash provides the same Snapshot Isolation level of consistency as TiKV, and ensures that the latest data is read, which means that you can read the data previously written in TiKV. Such consistency is achieved by validating the data replication progress.

Every time TiFlash receives a read request, the Region replica sends a progress validation request (a lightweight RPC request) to the Leader replica. TiFlash performs the read operation only after the current replication progress includes the data covered by the timestamp of the read request.
### Intelligent choice

TiDB can automatically choose to use TiFlash (column-wise) or TiKV (row-wise), or use both of them in one query to ensure the best performance.

This selection mechanism is similar to that of TiDB which chooses different indexes to execute query. TiDB optimizer makes the appropriate choice based on statistics of the read cost.
### Computing acceleration

TiFlash accelerates the computing of TiDB in two ways:

- The columnar storage engine is more efficient in performing read operation.
- TiFlash shares part of the computing workload of TiDB.

TiFlash shares the computing workload in the same way as the TiKV Coprocessor does: TiDB pushes down the computing that can be completed in the storage layer. Whether the computing can be pushed down depends on the support of TiFlash. For details, see [Supported pushdown calculations](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations).
