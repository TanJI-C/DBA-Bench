# TiKV storage engine metrics: RocksDB, Raft Engine, and Titan

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-tikv-dashboard.md`
- Source Title: `Key Monitoring Metrics of TiKV`
- Source Heading Path: `Key Monitoring Metrics of TiKV > TiKV-Details dashboard > RocksDB - kv/raft | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Raft Engine | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Titan - All`
- Source Line Ranges: `321-411`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `grafana`, `metrics`, `storage-engine`, `rocksdb`, `raft-engine`, `titan`, `io`, `compaction`, `cache`, `wal`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0061_95fe172298`
- Source ID: `tidb-docs-8.1:grafana-tikv-dashboard.md#rocksdb-kv-raft`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8edeebda0c0e9fd6482ba19629cf7edf00ce9bf10e5f1047e9dde160c894b76b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#rocksdb-kv-raft
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-tikv-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV-Details Grafana metrics for TiKV storage engine behavior across RocksDB - kv/raft, Raft Engine, or Titan - All panels.
- Retrieval Keywords: TiKV-Details dashboard, RocksDB - kv/raft, Raft Engine, Titan - All, Get operations, Get duration, Seek operations, Write operations, WAL sync operations, Write WAL duration, WAL sync duration, Compaction operations, Compaction duration, SST read duration, Write stall duration, Memtable size, Memtable hit, Block cache size, Block cache hit, Block cache flow, Keys flow, Total keys, Read flow, Write flow, Compaction pending bytes, Read amplification, Compression ratio, Number of snapshots, Oldest snapshots duration, Number files at each level, Ingest SST duration seconds, Stall conditions changed of each CF, read_entry, read_message, Write Duration Breakdown (99%), WAL Duration Breakdown (P99%), Bytes/Written, File Count, Entry Count, Blob file count, Blob file size, Live blob size, Blob cache hit, Blob get operations, Blob get duration, Blob file read duration, Blob file write duration, Blob file sync operations, Blob GC action, Blob GC duration
- Follow-up Guidance: 
- Classification Note: The official content classifies these items as observability metrics on the TiKV-Details dashboard for TiKV storage engines, covering RocksDB, Raft Engine, and Titan IO, compaction, cache, WAL, and blob-related measurements.

## Official Source Content

### RocksDB - kv/raft

- Get operations: The count of get operations per second
- Get duration: The time consumed when executing get operations
- Seek operations: The count of seek operations per second
- Seek duration: The time consumed when executing seek operations
- Write operations: The count of write operations per second
- Write duration: The time consumed when executing write operations
- WAL sync operations: The count of WAL sync operations per second
- Write WAL duration: The time consumed for writing WAL
- WAL sync duration: The time consumed when executing WAL sync operations
- Compaction operations: The count of compaction and flush operations per second
- Compaction duration: The time consumed when executing the compaction and flush operations
- SST read duration: The time consumed when reading SST files
- Write stall duration: Write stall duration. It should be `0` in normal case.
- Memtable size: The memtable size of each column family
- Memtable hit: The hit rate of memtable
- Block cache size: The block cache size. Broken down by column family if shared block cache is disabled.
- Block cache hit: The hit rate of block cache
- Block cache flow: The flow rate of block cache operations per type
- Block cache operations: The count of block cache operations per type
- Keys flow: The flow rate of operations on keys per type
- Total keys: The count of keys in each column family
- Read flow: The flow rate of read operations per type
- Bytes / Read: The bytes per read operation
- Write flow: The flow rate of write operations per type
- Bytes / Write: The bytes per write operation
- Compaction flow: The flow rate of compaction operations per type
- Compaction pending bytes: The pending bytes to be compacted
- Read amplification: The read amplification per TiKV instance
- Compression ratio: The compression ratio of each level
- Number of snapshots: The number of snapshots per TiKV instance
- Oldest snapshots duration: The time that the oldest unreleased snapshot survivals
- Number files at each level: The number of SST files for different column families in each level
- Ingest SST duration seconds: The time consumed to ingest SST files
- Stall conditions changed of each CF: Stall conditions changed of each column family
### Raft Engine

- Operations
    - write: the number of write operations by Raft Engine per second
    - read_entry: the number of raft log read operations by Raft Engine per second
    - read_message: the number of raft metadata read operations by Raft Engine per second
- Write duration: the duration of write operations by Raft Engine. This duration is close to the sum of the latency of disk IOs involved in writing these data.
- Flow
    - write: the write traffic of Raft Engine
    - rewrite append: the traffic of rewriting append logs
    - rewrite rewrite: the traffic of rewriting rewrite logs
- Write Duration Breakdown (99%)
    - wal: the latency of writing Raft Engine WAL
    - wait: the waiting time before writing
    - apply: the time consumed for applying data to memory
- Bytes/Written: the bytes written by Raft Engine every time
- WAL Duration Breakdown (P99%): the time consumed for each stage of writing Raft Engine WAL
- File Count
    - append: the number of files used for appending data by Raft Engine
    - rewrite: the number of files used for rewriting data by Raft Engine (rewrite is similar to RocksDB compaction)
- Entry Count
    - rewrite: the number of entries rewritten by Raft Engine
    - append: the number of entries appended by Raft Engine
### Titan - All

- Blob file count: The number of Titan blob files
- Blob file size: The total size of Titan blob file
- Live blob size: The total size of valid blob record
- Blob cache hit: The hit rate of Titan block cache
- Iter touched blob file count: The number of blob file involved in a single iterator
- Blob file discardable ratio distribution: The ratio distribution of blob record failure of blob files
- Blob key size: The size of Titan blob keys
- Blob value size: The size of Titan blob values
- Blob get operations: The count of get operations in Titan blob
- Blob get duration: The time consumed when executing get operations in Titan blob
- Blob iter operations: The time consumed when executing iter operations in Titan blob
- Blob seek duration: The time consumed when executing seek operations in Titan blob
- Blob next duration: The time consumed when executing next operations in Titan blob
- Blob prev duration: The time consumed when executing prev operations in Titan blob
- Blob keys flow: The flow rate of operations on Titan blob keys
- Blob bytes flow: The flow rate of bytes on Titan blob keys
- Blob file read duration: The time consumed when reading Titan blob file
- Blob file write duration: The time consumed when writing Titan blob file
- Blob file sync operations: The count of blob file sync operations
- Blob file sync duration: The time consumed when synchronizing blob file
- Blob GC action: The count of Titan GC actions
- Blob GC duration: The Titan GC duration
- Blob GC keys flow: The flow rate of keys read and written by Titan GC
- Blob GC bytes flow: The flow rate of bytes read and written by Titan GC
- Blob GC input file size: The size of Titan GC input file
- Blob GC output file size: The size of Titan GC output file
- Blob GC file count: The count of blob files involved in Titan GC
