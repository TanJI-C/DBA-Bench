# Regions, MVCC, and distributed transaction concepts

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-storage.md`
- Source Title: `TiDB Storage`
- Source Heading Path: `TiDB Storage > Region | TiDB Storage > MVCC | TiDB Storage > Distributed ACID transaction`
- Source Line Ranges: `45-109`
- Source Scope: `all`
- Primary Component: `tikv`
- Related Components: `pd`
- Topic Tags: `region`, `range-sharding`, `replica`, `raft-group`, `leader-follower`, `pd-scheduling`, `mvcc`, `versioned-keys`, `acid-transactions`, `percolator`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0108_b9253a8beb`
- Source ID: `tidb-docs-8.1:tidb-storage.md#region`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bd595737b632544b5f841009ed8f34405b4017d6c87b21412d39f778d6bacd88`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-storage#region
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-storage.md

## Retrieval Guidance

- Use When: Use this chunk when describing how TiKV shards data into Regions, uses PD to track and spread Regions, applies MVCC with versioned keys, and bases distributed transactions on Percolator.
- Retrieval Keywords: Region, [StartKey, EndKey), 96 MiB, range sharding, PD, Region distribution, exact Region of a Key, Replica, Raft Group, Leader, Follower, all reads and writes are processed through the Leader, MVCC, multi-version concurrency control, Key_Version, SeekPrefix(Key_Version), Distributed ACID transaction, Percolator
- Follow-up Guidance: For the underlying ordered Key-Value model, RocksDB storage, and Raft basics referenced by this section, see the earlier TiDB Storage sections.
- Classification Note: This is classified as architecture because the content explains TiKV's data distribution, replication, concurrency control, and transaction model at a system-design level.

## Official Source Content

## Region

To make it easy to understand, let's assume that all data only has one replica. As mentioned earlier, TiKV can be regarded as a large, orderly KV Map, so data is distributed across multiple machines in order to achieve horizontal scalability. For a KV system, there are two typical solutions to distributing data across multiple machines:

* Hash: Create Hash by Key and select the corresponding storage node according to the Hash value.
* Range: Divide ranges by Key, where a segment of serial Key is stored on a node.

TiKV chooses the second solution that divides the whole Key-Value space into a series of consecutive Key segments. Each segment is called a Region. Each Region can be described by `[StartKey, EndKey)`, a left-closed and right-open interval. The default size limit for each Region is 96 MiB and the size can be configured.

![Region in TiDB](/media/tidb-storage-2.png)

Note that the Region here has nothing to do with the table in SQL. In this document, forget about SQL and focus on KV for now. After dividing data into Regions, TiKV will perform two important tasks:

* Distributing data to all nodes in the cluster and use Region as the basic unit. Try its best to ensure that the number of Regions on each node is roughly similar.
* Performing Raft replication and membership management in Region.

These two tasks are very important and will be introduced one by one.

* First, data is divided into many Regions according to Key, and the data for each Region is stored on only one node (ignoring multiple replicas). The TiDB system has a PD component that is responsible for spreading Regions as evenly as possible across all nodes in the cluster. In this way, on one hand, the storage capacity is scaled horizontally (Regions on the other nodes are automatically scheduled to the newly added node); on the other hand, load balancing is achieved (the situation where one node has a lot of data while the others have little will not occur).

    At the same time, in order to ensure that the upper client can access the needed data, there is a component (PD) in the system to record the distribution of Regions on the node, that is, the exact Region of a Key and the node of that Region placed through any Key.

* For the second task, TiKV replicates data in Regions, which means that data in one Region will have multiple replicas with the name "Replica". Multiple Replicas of a Region are stored on different nodes to form a Raft Group, which is kept consistent through the Raft algorithm.

    One of the Replicas serves as the Leader of the Group and other as the Follower. By default, all reads and writes are processed through the Leader, where reads are done and write are replicated to followers. The following diagram shows the whole picture about Region and Raft group.

![TiDB Storage](/media/tidb-storage-3.png)

As we distribute and replicate data in Regions, we have a distributed Key-Value system that, to some extent, has the capability of disaster recovery. You no longer need to worry about the capacity, or disk failure and data loss.
## MVCC

TiKV supports multi-version concurrency control (MVCC). Consider a scenario where Client A is writing to a key simultaneously as Client B is reading the same key. Without the MVCC mechanism, these read and write operations would be mutually exclusive, posing performance issues and deadlocks in a distributed scenario. However, With MVCC, as long as Client B performs a read operation at a logical time earlier than the Client A write operation, then Client B can correctly read the original value at the same time Client A performs the write operation. Even if the key is modified multiple times by multiple write operations, Client B can still read the old value according to its logical time.

TiKV MVCC is implemented by appending a version number to the key. Without MVCC, the Key-Value pairs of TiKV are as follows:

```
Key1 -> Value
Key2 -> Value
……
KeyN -> Value
```

With MVCC, the Key-Value pairs of TiKV are as follows:

```
Key1_Version3 -> Value
Key1_Version2 -> Value
Key1_Version1 -> Value
……
Key2_Version4 -> Value
Key2_Version3 -> Value
Key2_Version2 -> Value
Key2_Version1 -> Value
……
KeyN_Version2 -> Value
KeyN_Version1 -> Value
……
```

Note that for multiple versions of the same Key, versions with larger numbers are placed first (see the [Key-Value](#key-value-pairs) section where Keys are arranged in order), so that when you obtain Value through Key + Version, the Key of MVCC can be constructed with Key and Version, which is `Key_Version`. Then you can directly locate the first position greater than or equal to this `Key_Version` through RocksDB's `SeekPrefix(Key_Version)` API.
## Distributed ACID transaction

Transaction of TiKV adopts the model used by Google in BigTable: [Percolator](https://research.google/pubs/large-scale-incremental-processing-using-distributed-transactions-and-notifications/). TiKV's implementation is inspired by this paper, with a lot of optimizations. See [transaction overview](https://docs.pingcap.com/tidb/stable/transaction-overview) for details.
