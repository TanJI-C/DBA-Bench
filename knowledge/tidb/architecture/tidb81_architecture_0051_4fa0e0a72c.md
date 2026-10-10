# Partitioned Raft KV overview and application scenarios

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-raft-kv.md`
- Source Title: `Partitioned Raft KV`
- Source Heading Path: `Partitioned Raft KV | Partitioned Raft KV > Application scenarios`
- Source Line Ranges: `5-29`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `experimental`, `storage-engine`, `rocksdb`, `regions`, `scalability`, `write-performance`, `scale-out`, `memory`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0051_4fa0e0a72c`
- Source ID: `tidb-docs-8.1:partitioned-raft-kv.md#partitioned-raft-kv`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ee0b46087dc7bc1e8649e7e837619e8d02e328af0ed4bf7f3d7c4624e4c24d7f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-raft-kv#partitioned-raft-kv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-raft-kv.md

## Retrieval Guidance

- Use When: Use this chunk when answering what Partitioned Raft KV is, why TiKV introduced it, or which workload characteristics and benefits are described for this experimental storage engine.
- Retrieval Keywords: Partitioned Raft KV, experimental feature, TiKV storage engine, single RocksDB instance, multiple RocksDB instances, each Region is independently stored in a separate RocksDB instance, physical isolation of data operations between Regions, support larger clusters more stably, single TiKV instance needs to support more data, many write requests, scale-in and scale-out operations are frequent, read and write amplification, TiKV has sufficient memory, better write performance, faster scaling speed, larger volume of data supported with the same hardware
- Follow-up Guidance: The source also states that Partitioned Raft KV is experimental, not recommended for production environment use, and might be changed or removed without prior notice.
- Classification Note: This is classified as architecture because the content explains the TiKV storage engine design change from one RocksDB instance to multiple partitioned RocksDB instances and the scenarios it targets.

## Official Source Content

# Partitioned Raft KV

> **Warning:**
>
> Partitioned Raft KV is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

Before v6.6.0, TiKV's Raft-based storage engine used a single RocksDB instance to store the data of all Regions of the TiKV instance.

To support larger clusters more stably, starting from TiDB v6.6.0, a new TiKV storage engine is introduced, which uses multiple RocksDB instances to store TiKV Region data, and the data of each Region is independently stored in a separate RocksDB instance.

The new engine can better control the number and level of files in each RocksDB instance, achieve physical isolation of data operations between Regions, and support stably managing more data. You can see it as TiKV managing multiple RocksDB instances through partitioning, which is why the feature is named Partitioned Raft KV.
## Application scenarios

You can use this feature if your TiKV cluster has the following characteristics:

* A single TiKV instance needs to support more data.
* There are many write requests.
* Scale-in and scale-out operations are frequent.
* The workload has a serious read and write amplification.
* TiKV has sufficient memory.

Advantages of this feature are better write performance, faster scaling speed, and larger volume of data supported with the same hardware. It can also support larger cluster scale.
