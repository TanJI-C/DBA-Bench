# TiKV storage model, RocksDB, and Raft basics

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-storage.md`
- Source Title: `TiDB Storage`
- Source Heading Path: `TiDB Storage | TiDB Storage > Key-Value pairs | TiDB Storage > Local storage (RocksDB) | TiDB Storage > Raft protocol`
- Source Line Ranges: `5-44`
- Source Scope: `all`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `storage-model`, `key-value`, `ordered-keys`, `rocksdb`, `local-storage`, `raft`, `replication`, `leader-election`, `log-replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0107_6f47017bed`
- Source ID: `tidb-docs-8.1:tidb-storage.md#tidb-storage`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `35ab95e219a572884dec45f1bf09be4f45c4f9fb316ed753c5a46e342add406b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-storage#tidb-storage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-storage.md

## Retrieval Guidance

- Use When: Use this chunk when explaining TiKV's basic storage design, including the ordered Key-Value model, RocksDB as local persistent storage, and Raft-based replication concepts.
- Retrieval Keywords: TiKV storage model, Key-Value pairs, ordered traversal, Keys' binary order, Seek, Next, RocksDB, local storage, persistent Key-Value Map, Raft protocol, consensus algorithm, leader election, membership changes, log replication, Raft log, majority of nodes
- Follow-up Guidance: For sharding and replica management at the Region level, see the Region section with PD scheduling and Raft Group concepts.
- Classification Note: This is classified as architecture because the content describes core TiKV storage concepts and how RocksDB and Raft together form distributed Key-Value storage.

## Official Source Content

# TiDB Storage

This document introduces some design ideas and key concepts of [TiKV](https://github.com/tikv/tikv).

![storage-architecture](/media/tidb-storage-architecture-1.png)
## Key-Value pairs

The first thing to decide for a data storage system is the data storage model, that is, in what form the data is saved. TiKV's choice is the Key-Value model and provides an ordered traversal method. There are two key points for TiKV data storage model:

+ This is a huge Map (similar to `std::Map` in C++) , which stores Key-Value pairs.
+ The Key-Value pair in the Map is ordered according to Keys' binary order, which means you can Seek the position of a particular Key and then call the Next method to get the Key-Value pairs larger than this Key in incremental order.

Note that the KV storage model for TiKV described in this document has nothing to do with tables of SQL. This document does not discuss any concepts related to SQL and only focuses on how to implement a high-performance, high-reliability, distributed Key-Value storage such as TiKV.
## Local storage (RocksDB)

For any persistent storage engine, data is eventually saved on disk, and TiKV is no exception. TiKV does not write data directly on the disk, but stores data in RocksDB, which is responsible for the data storage. The reason is that it costs a lot to develop a standalone storage engine, especially a high-performance standalone engine that requires careful optimization.

RocksDB is an excellent standalone storage engine open-sourced by Facebook. This engine can meet various requirements of TiKV for a single engine. Here, you can simply consider RocksDB as a single persistent Key-Value Map.
## Raft protocol

What's more, the implementation of TiKV faces a more difficult thing: to secure data safety in case a single machine fails.

A simple way is to replicate data to multiple machines, so that even if one machine fails, the replicas on other machines are still available. In other words, you need a data replication scheme that is reliable, efficient, and able to handle the situation of a failed replica. All of these are made possible by the Raft algorithm.

Raft is a consensus algorithm. This document only briefly introduces Raft. For more details, you can see [In Search of an Understandable Consensus Algorithm](https://raft.github.io/raft.pdf). The Raft has several important features:

- Leader election
- Membership changes (such as adding replicas, deleting replicas, and transferring leaders)
- Log replication

TiKV use Raft to perform data replication. Each data change will be recorded as a Raft log. Through Raft log replication, data is safely and reliably replicated to multiple nodes of the Raft group. However, according to Raft protocol, successful writes only need that data is replicated to the majority of nodes.

![Raft in TiDB](/media/tidb-storage-1.png)

In summary, TiKV can quickly store data on disk via the standalone machine RocksDB, and replicate data to multiple machines via Raft in case of machine failure. Data is written through the interface of Raft instead of to RocksDB. With the implementation of Raft, TiKV becomes a distributed Key-Value storage. Even with a few machine failures, TiKV can automatically complete replicas by virtue of the native Raft protocol, which does not impact the application.
