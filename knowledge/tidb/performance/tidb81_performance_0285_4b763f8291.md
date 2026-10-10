# TiKV memory usage and recommended hardware configuration

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tune-tikv-memory-performance.md`
- Source Title: `Tune TiKV Memory Parameter Performance`
- Source Heading Path: `Tune TiKV Memory Parameter Performance > Parameter specification | Tune TiKV Memory Parameter Performance > TiKV memory usage | Tune TiKV Memory Parameter Performance > Recommended configuration of TiKV`
- Source Line Ranges: `241-256`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `memory-usage`, `block-cache`, `write-buffer`, `page-cache`, `large-queries`, `hardware-sizing`, `write-throughput`, `read-write-latency`, `ssd`, `iops`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0285_4b763f8291`
- Source ID: `tidb-docs-8.1:tune-tikv-memory-performance.md#parameter-specification`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `90752bb79f746afc8bf9c5ef0626e46d48d7f1fee67c25214a77c299fb155128`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tune-tikv-memory-performance#parameter-specification
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tune-tikv-memory-performance.md

## Retrieval Guidance

- Use When: Use this chunk when explaining what consumes TiKV memory beyond block cache and write buffer, or when locating the documented TiKV hardware recommendations for production, write throughput, and low read-write latency.
- Retrieval Keywords: TiKV memory usage, block cache, write buffer, system page cache, select * from ..., large queries, TiKV occupies some of the memory, Recommended configuration of TiKV, CPU cores less than 8, memory less than 32GB, high write throughput, disk with good throughput capacity, very low read-write latency, SSD with high IOPS
- Follow-up Guidance: The same source states that large queries such as `select * from ...` can make TiKV read data, generate corresponding data structures in memory, and return them to TiDB.
- Classification Note: This is classified as performance for TiKV in a self-managed scope because the content describes TiKV memory usage factors and recommended hardware characteristics affecting throughput and latency.

## Official Source Content

## TiKV memory usage

Besides `block cache` and `write buffer` which occupy the system memory, the system memory is occupied in the following scenarios:

+ Some of the memory is reserved as the system's page cache.

+ When TiKV processes large queries such as `select * from ...`, it reads data, generates the corresponding data structure in the memory, and returns this structure to TiDB. During this process, TiKV occupies some of the memory.
## Recommended configuration of TiKV

+ In production environments, it is not recommended to deploy TiKV on the machine whose CPU cores are less than 8 or the memory is less than 32GB.

+ If you demand a high write throughput, it is recommended to use a disk with good throughput capacity.

+ If you demand a very low read-write latency, it is recommended to use SSD with high IOPS.
