# Titan architecture, BlobFile, and TitanTableBuilder

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/storage-engine/titan-overview.md`
- Source Title: `Titan Overview`
- Source Heading Path: `Titan Overview > Architecture and implementation | Titan Overview > Architecture and implementation > BlobFile | Titan Overview > Architecture and implementation > TitanTableBuilder`
- Source Line Ranges: `38-71`
- Source Scope: `shared`
- Primary Component: `tikv`
- Related Components: `shared`
- Topic Tags: `architecture`, `blobfile`, `titantablebuilder`, `sst`, `blob-index`, `compression`, `min-blob-size`, `downgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0060_915117edd4`
- Source ID: `tidb-docs-8.1:storage-engine/titan-overview.md#architecture-and-implementation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bf72ef20f45d9a823dc069912ca93093e0f39df2a983f72737b1b17ae0a5965a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/storage-engine/titan-overview#architecture-and-implementation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/storage-engine/titan-overview.md

## Retrieval Guidance

- Use When: Use this chunk when looking for Titan internal architecture details such as BlobFile structure, blob record compression, TitanTableBuilder behavior, min_blob_size, or downgrade behavior back to RocksDB during compaction.
- Retrieval Keywords: Architecture and implementation, BlobFile, blob records, meta blocks, meta index block, footer, Key-Value pairs stored in order, prefetching, Garbage Collection GC user key copy, compression at the blob record level, Snappy, lz4, zstd, official Snappy format, default compression algorithm, TitanTableBuilder, key-value separation, min_blob_size, writes index into the SST, writes value directly into the SST, downgraded to RocksDB, compactions
- Follow-up Guidance: If the user is asking how outdated values are reclaimed or how blob files are selected for cleanup, the same source has a Garbage Collection section covering regular GC and Level Merge.
- Classification Note: This is architecture content because it explains the official internal data structures and write-path components used by Titan.

## Official Source Content

## Architecture and implementation

The following figure shows the architecture of Titan:

![Titan Architecture](/media/titan/titan-1.png)

During flush and compaction operations, Titan separates values from the LSM-tree. The advantage of this approach is that the write process is consistent with RocksDB, which reduces the chance of invasive changes to RocksDB.
### BlobFile

When Titan separates the value file from the LSM-tree, it stores the value file in the BlobFile. The following figure shows the BlobFile format:

![BlobFile Format](/media/titan/titan-2.png)

A blob file mainly consists of blob records, meta blocks, a meta index block, and a footer. Each block record stores a Key-Value pair. The meta blocks are used for scalability, and store properties related to the blob file. The meta index block is used for meta block searching.

> **Note:**
>
> + The Key-Value pairs in the blob file are stored in order, so that when the Iterator is implemented, the sequential reading performance can be improved via prefetching.
> + Each blob record keeps a copy of the user key corresponding to the value. This way, when Titan performs Garbage Collection (GC), it can query the user key and identify whether the corresponding value is outdated. However, this process introduces some write amplification.
> + BlobFile supports compression at the blob record level. Titan supports several compression algorithms, such as [Snappy](https://github.com/google/snappy), [`lz4`](https://github.com/lz4/lz4), and [`zstd`](https://github.com/facebook/zstd). In versions prior to v7.6.0, the default compression algorithm is `lz4`. Starting from v7.6.0, the default compression algorithm is `zstd`.
> + The Snappy compressed file must be in the [official Snappy format](https://github.com/google/snappy). Other variants are not supported.
### TitanTableBuilder

![TitanTableBuilder](/media/titan/titan-3.png)

TitanTableBuilder is the key to achieving Key-Value separation. TitanTableBuilder determines the Key-Pair value size, and based on that, decides whether to separate the value from the Key-Value pair and store it in the blob file.

+ If the value size is greater than or equal to `min_blob_size`, TitanTableBuilder separates the value and stores it in the blob file. TitanTableBuilder also generates an index and writes it into the SST.
+ If the value size is smaller than `min_blob_size`, TitanTableBuilder writes the value directly into the SST.

Titan can also be downgraded to RocksDB in the process above. When RocksDB is performing compactions, the separated value can be written back to the newly generated SST files.
