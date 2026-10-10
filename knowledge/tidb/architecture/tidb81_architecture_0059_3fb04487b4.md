# RocksDB overview, TiKV architecture, resource usage, compaction, and WriteStall

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/storage-engine/rocksdb-overview.md`
- Source Title: `RocksDB Overview`
- Source Heading Path: `RocksDB Overview | RocksDB Overview > TiKV architecture | RocksDB Overview > RocksDB memory usage | RocksDB Overview > RocksDB space usage | RocksDB Overview > RocksDB background threads and compaction | RocksDB Overview > WriteStall`
- Source Line Ranges: `6-69`
- Source Scope: `shared`
- Primary Component: `tikv`
- Related Components: `tidb`, `shared`
- Topic Tags: `rocksdb`, `lsm-tree`, `wal`, `memtable`, `sst`, `column-families`, `tikv-architecture`, `raftdb`, `kvdb`, `mvcc`, `block-cache`, `memory-usage`, `space-amplification`, `background-threads`, `compaction`, `writestall`, `l0-files`, `grafana`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0059_3fb04487b4`
- Source ID: `tidb-docs-8.1:storage-engine/rocksdb-overview.md#rocksdb-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `93613ce83d0155240db19c90a2a993932afe6c8582dccd811ec2b91d0479b60b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/storage-engine/rocksdb-overview#rocksdb-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/storage-engine/rocksdb-overview.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving an overview of RocksDB in TiKV, including kvdb and raftdb architecture, Column Families, BlockCache and MemTable resource usage, space amplification, background compaction threads, and WriteStall caused by too many L0 files.
- Retrieval Keywords: RocksDB Overview, TiKV architecture, raftdb, kvdb, raft CF, lock CF, default CF, write CF, WAL, MemTable, SST, LSM-tree, BlockCache, storage.block-cache.capacity, rocksdb/max-background-jobs, background thread pool, compaction, space amplification, MVCC metadata, WriteStall, L0 files, WriteStall Reason, Grafana RocksDB KV panel, rocksdb.defaultcf.level0-slowdown-writes-trigger, rocksdb.writecf.level0-slowdown-writes-trigger, rocksdb.lockcf.level0-slowdown-writes-trigger, rocksdb.defaultcf.level0-stop-writes-trigger, rocksdb.writecf.level0-stop-writes-trigger, rocksdb.lockcf.level0-stop-writes-trigger
- Follow-up Guidance: If the issue is a sudden sharp increase in write delay, the source says to first check the WriteStall Reason metric on the Grafana RocksDB KV panel and, for WriteStall caused by too many L0 files, the listed level0 slowdown and stop write trigger configurations can be adjusted to 64.
- Classification Note: The chunk is classified as architecture because the official content explains how TiKV uses two RocksDB instances and multiple Column Families, and it also summarizes related resource usage, compaction behavior, and WriteStall characteristics.

## Official Source Content

# RocksDB Overview

[RocksDB](https://github.com/facebook/rocksdb) is an LSM-tree storage engine that provides key-value store and read-write functions. It is developed by Facebook and based on LevelDB. Key-value pairs written by the user are firstly inserted into Write Ahead Log (WAL) and then written to the SkipList in memory (a data structure called MemTable). LSM-tree engines convert the random modification (insertion) to sequential writes to the WAL file, so they provide better write throughput than B-tree engines.

Once the data in memory reaches a certain size, RocksDB flushes the content into a Sorted String Table (SST) file in the disk. SST files are organized in multiple levels (the default is up to 6 levels). When the total size of a level reaches the threshold, RocksDB chooses part of the SST files and merges them into the next level. Each subsequent level is 10 times larger than the previous one, so 90% of the data is stored in the last layer.

RocksDB allows users to create multiple Column Families (CFs). CFs have their own SkipList and SST files, and they share the same WAL file. In this way, different CFs can have different settings according to the application characteristics. It does not increase the number of writes to WAL at the same time.
## TiKV architecture

The architecture of TiKV is illustrated as follows:

![TiKV RocksDB](/media/tikv-rocksdb.png)

As the storage engine of TiKV, RocksDB is used to store Raft logs and user data. All data in a TiKV node shares two RocksDB instances. One is for Raft log (often called raftdb), and the other is for user data and MVCC metadata (often called kvdb). There are four CFs in kvdb: raft, lock, default, and write:

* raft CF: Store metadata of each Region. It occupies only a very small amount of space, and users do not need to care.
* lock CF: Store the pessimistic lock of pessimistic transactions and the Prewrite lock for distributed transactions. After the transaction is committed, the corresponding data in lock CF is deleted quickly. Therefore, the size of data in lock CF is usually very small (less than 1 GB). If the data in lock CF increases a lot, it means that a large number of transactions are waiting to be committed, and that the system meets a bug or failure.
* write CF: Store the user's real written data and MVCC metadata (the start timestamp and commit timestamp of the transaction to which the data belongs). When the user writes a row of data, it is stored in the write CF if the data length is less than or equal to 255 bytes. Otherwise, it is stored in the default CF. In TiDB, the secondary index only occupies the space of write CF, since the value stored in the non-unique index is empty and the value stored in the unique index is the primary key index.
* default CF: Store data longer than 255 bytes.
## RocksDB memory usage

To improve the reading performance and reduce the reading operations to the disk, RocksDB divides the files stored on the disk into blocks based on a certain size (the default is 64 KB). When reading a block, it first checks if the data already exists in BlockCache in memory. If true, it can read the data directly from memory without accessing the disk.

BlockCache discards the least recently used data according to the LRU algorithm. By default, TiKV devotes 45% of the system memory to BlockCache. Users can also modify the `storage.block-cache.capacity` configuration to an appropriate value by themselves. However, it is not recommended to exceed 60% of the total system memory.

The data written to RocksDB is written to MemTable firstly. When the size of a MemTable exceeds 128 MB, it switches to a new MemTable. There are 2 RocksDB instances in TiKV, a total of 4 CFs. The size limit of a single MemTable for each CF is 128 MB. A maximum of 5 MemTables can exist at the same time; otherwise, the foreground writes is blocked. The memory occupied by this part is at most 2.5 GB (4 x 5 x 128 MB). It is not recommended to change this limit since it costs less memory.
## RocksDB space usage

* Multi-version: As RocksDB is a key-value storage engine with LSM-tree structure, the data in MemTable is flushed to L0 first. Because the file is arranged in the order of which they are generated, there might be overlap between the ranges of SSTs at the L0. As a result, the same key might have multiple versions in L0. When a file is merged from L0 to L1, it is cut into multiple files in a certain size (the default is 8 MB). The key range of each file on the same level does not overlap with each other, so there is only one version for each key on L1 and subsequent levels.
* Space amplification: The total size of files on each level is x (the default is 10) times that of the previous level, so 90% of the data is stored in the last level. It also means that the space amplification of RocksDB does not exceed 1.11 (L0 has fewer data and can be ignored).
* Space amplification of TiKV: TiKV has it's own MVCC strategy. When a user writes a key, the real data written to RocksDB is key + commit_ts, that is to say, the update and deletion also write a new key to RocksDB. TiKV deletes the old version of the data (through the Delete interface of RocksDB) at intervals, so it can be considered that the actual space of the data stored by the user on TiKV is enlarged to 1.11 plus the data written in the last 10 minutes (assuming that TiKV cleans up the old data promptly).
## RocksDB background threads and compaction

In RocksDB, operations such as converting the MemTable into SST files and merging SST files at various levels are performed in the background thread pool. The default size of the background thread pool is 8. When the number of CPUs in the machine is less than or equal to 8, the default size of the background thread pool is the number of CPUs minus one.

Generally speaking, users do not need to change this configuration. If the user deploys multiple TiKV instances on a machine, or the machine has a relatively high read load and a low write load, you can adjust the `rocksdb/max-background-jobs` to 3 or 4 as appropriate.
## WriteStall

> **Note:**
>
> This section is for TiDB and not applicable to TiDB Cloud.

The L0 of RocksDB is different from other levels. The SSTs of L0 are arranged in the order of generation. The key ranges between the SSTs can overlap. Therefore, each SST in L0 must be queried in turn when a query is performed. In order not to affect query performance, WriteStall is triggered to block writing when there are too many files in L0.

When encountering a sudden sharp increase in write delay, you can first check the **WriteStall Reason** metric on the Grafana RocksDB KV panel. If it is a WriteStall caused by too many L0 files, you can adjust the following configurations to 64.

```
rocksdb.defaultcf.level0-slowdown-writes-trigger
rocksdb.writecf.level0-slowdown-writes-trigger
rocksdb.lockcf.level0-slowdown-writes-trigger
rocksdb.defaultcf.level0-stop-writes-trigger
rocksdb.writecf.level0-stop-writes-trigger
rocksdb.lockcf.level0-stop-writes-trigger
```
