# TiDB best practices introduction and core distributed concepts

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/tidb-best-practices.md`
- Source Title: `TiDB Best Practices`
- Source Heading Path: `TiDB Best Practices | TiDB Best Practices > Preface | TiDB Best Practices > Basic concepts | TiDB Best Practices > Basic concepts > Raft | TiDB Best Practices > Basic concepts > Distributed transactions | TiDB Best Practices > Basic concepts > Data sharding | TiDB Best Practices > Basic concepts > Load balancing | TiDB Best Practices > Basic concepts > SQL on KV`
- Source Line Ranges: `5-80`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `sql`
- Topic Tags: `best-practices`, `distributed-systems`, `raft`, `transactions`, `optimistic-transactions`, `pessimistic-transactions`, `transaction-limits`, `data-sharding`, `region`, `load-balancing`, `sql-to-kv`, `secondary-indexes`, `hotspot`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0007_e19e8d6894`
- Source ID: `tidb-docs-8.1:best-practices/tidb-best-practices.md#tidb-best-practices`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7370b2153beab5cafd02a99a4bbd6a20423b5d2e4bdc850c457671dd72b20213`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/tidb-best-practices#tidb-best-practices
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/tidb-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when explaining TiDB basic distributed concepts such as Raft replication, distributed transactions, Region-based sharding, PD load balancing, or how SQL data and indexes map to KV and create hotspots.
- Retrieval Keywords: TiDB Best Practices, Raft, distributed transactions, optimistic transaction model, pessimistic transaction mode, SELECT FOR UPDATE, transaction size limit, 5,000 SQL statements, 6 MB, 10 GB, Data sharding, Region, [StartKey, EndKey), Load balancing, Placement Driver, PD, SQL on KV, TableID, IndexID, secondary indexing, write hotspot, access hotspot
- Follow-up Guidance: For detailed information, the source points to PingCAP blog posts about data storage, computing, and scheduling.
- Classification Note: This chunk is classified as architecture because it introduces TiDB core distributed design concepts including Raft replication, Percolator-based distributed transactions, Region sharding, PD scheduling, and SQL-to-KV mapping.

## Official Source Content

# TiDB Best Practices

This document summarizes the best practices of using TiDB, including the use of SQL and optimization tips for Online Analytical Processing (OLAP) and Online Transactional Processing (OLTP) scenarios, especially the optimization options specific for TiDB.

Before you read this document, it is recommended that you read three blog posts that introduce the technical principles of TiDB:

* [TiDB Internal (I) - Data Storage](https://www.pingcap.com/blog/tidb-internal-data-storage/)
* [TiDB Internal (II) - Computing](https://www.pingcap.com/blog/tidb-internal-computing/)
* [TiDB Internal (III) - Scheduling](https://www.pingcap.com/blog/tidb-internal-scheduling/)
## Preface

Database is a generic infrastructure system. It is important to consider various user scenarios during the development process and to modify the data parameters or the way to use according to actual situations in specific business scenarios.

TiDB is a distributed database compatible with the MySQL protocol and syntax. But with the internal implementation and supporting of distributed storage and transactions, the way of using TiDB is different from MySQL.
## Basic concepts

The best practices are closely related to its implementation principles. It is recommended that you learn some of the basic mechanisms, including the Raft consensus algorithm, distributed transactions, data sharding, load balancing, the mapping solution from SQL to Key-Value (KV), the implementation method of secondary indexing, and distributed execution engines.

This section is an introduction to these concepts. For detailed information, refer to [PingCAP blog posts](https://pingcap.com/blog/).
### Raft

Raft is a consensus algorithm that ensures data replication with strong consistency. At the bottom layer, TiDB uses Raft to replicate data. TiDB writes data to the majority of the replicas before returning the result of success. In this way, even though a few replicas might get lost, the system still has the latest data. For example, if there are three replicas, the system does not return the result of success until data has been written to two replicas. Whenever a replica is lost, at least one of the remaining two replicas have the latest data.

To store three replicas, compared with the replication of Source-Replica, Raft is more efficient. The write latency of Raft depends on the two fastest replicas, instead of the slowest one. Therefore, the implementation of geo-distributed and multiple active data centers becomes possible by using the Raft replication. In the typical scenario of three data centers distributing in two sites, to guarantee the data consistency, TiDB just needs to successfully write data into the local data center and the closer one, instead of writing to all three data centers. However, this does not mean that cross-data center deployment can be implemented in any scenario. When the amount of data to be written is large, the bandwidth and latency between data centers become the key factors. If the write speed exceeds the bandwidth or the latency is too high, the Raft replication mechanism still cannot work well.
### Distributed transactions

TiDB provides complete distributed transactions and the model has some optimizations on the basis of [Google Percolator](https://research.google/pubs/large-scale-incremental-processing-using-distributed-transactions-and-notifications/). This document introduces the following features:

* Optimistic transaction model

    TiDB's optimistic transaction model does not detect conflicts until the commit phase. If there are conflicts, the transaction needs retry. But this model is inefficient if the conflict is severe, because operations before retry are invalid and need to repeat.

    Assume that the database is used as a counter. High access concurrency might lead to severe conflicts, resulting in multiple retries or even timeouts. Therefore, in the scenario of severe conflicts, it is recommended to use the pessimistic transaction mode or to solve problems at the system architecture level, such as placing counter in Redis. Nonetheless, the optimistic transaction model is efficient if the access conflict is not very severe.

* Pessimistic transaction mode

    In TiDB, the pessimistic transaction mode has almost the same behavior as in MySQL. The transaction applies a lock during the execution phase, which avoids retries in conflict situations and ensures a higher success rate. By applying the pessimistic locking, you can also lock data in advance using `SELECT FOR UPDATE`.

    However, if the application scenario has fewer conflicts, the optimistic transaction model has better performance.

* Transaction size limit

    As distributed transactions need to conduct two-phase commit and the bottom layer performs Raft replication, if a transaction is very large, the commit process would be quite slow, and the following Raft replication process is thus stuck. To avoid this problem, the transaction size is limited:

    - A transaction is limited to 5,000 SQL statements (by default)
    - Each Key-Value entry is no more than 6 MB (by default)
    - The total size of Key-Value entries is no more than 10 GB.

    You can find similar limits in [Google Cloud Spanner](https://cloud.google.com/spanner/quotas).
### Data sharding

TiKV automatically shards bottom-layered data according to the range of keys. Each Region is a range of keys, which is a left-closed and right-open interval, `[StartKey, EndKey)`. When the amount of Key-Value pairs in a Region exceeds a certain value, the Region automatically splits into two.
### Load balancing

Placement Driver (PD) balances the load of the cluster according to the status of the entire TiKV cluster. The unit of scheduling is Region and the logic is the strategy configured by PD.
### SQL on KV

TiDB automatically maps the SQL structure into Key-Value structure. For details, see [TiDB Internal (II) - Computing](https://www.pingcap.com/blog/tidb-internal-computing/).

Simply put, TiDB performs the following operations:

* A row of data is mapped to a Key-Value pair. The key is prefixed with `TableID` and suffixed with the row ID.
* An index is mapped as a Key-Value pair. The key is prefixed with `TableID+IndexID` and suffixed with the index value.

The data or indexes in the same table have the same prefix. These Key-Values are at adjacent positions in the key space of TiKV. Therefore, when the amount of data to be written is large and all is written to one table, the write hotspot is created. The situation gets worse when some index values of the continuous written data is also continuous (for example, fields that increase with time, like `update time`), which creates a few write hotspots and becomes the bottleneck of the entire system.

Similarly, if all data is read from a focused small range (for example, the continuous tens or hundreds of thousands of rows of data), an access hotspot of data is likely to occur.
