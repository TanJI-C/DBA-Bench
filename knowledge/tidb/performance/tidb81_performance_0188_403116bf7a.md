# Titan GC range merge, scaling behavior, and min-blob-size performance impact

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/storage-engine/titan-overview.md`
- Source Title: `Titan Overview`
- Source Heading Path: `Titan Overview > Garbage Collection > Level Merge > Range Merge | Titan Overview > Garbage Collection > Scale out and scale in | Titan Overview > Garbage Collection > Impact of `min-blob-size` on performance`
- Source Line Ranges: `119-153`
- Source Scope: `shared`
- Primary Component: `tikv`
- Related Components: `shared`
- Topic Tags: `garbage-collection`, `level-merge`, `range-merge`, `scaling`, `snapshots`, `rocksdb-format`, `compaction`, `blob-files`, `min-blob-size`, `ycsb`, `qps`, `scan-workloads`, `point-reads`, `write-workloads`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0188_403116bf7a`
- Source ID: `tidb-docs-8.1:storage-engine/titan-overview.md#range-merge`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d8e1bfda2ebde97c77338430f4e2acebb9e298f9e60ae21e3b8f144201321bfe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/storage-engine/titan-overview#range-merge
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/storage-engine/titan-overview.md

## Retrieval Guidance

- Use When: Use this chunk when asking about Titan Range Merge in GC, TiKV scaling snapshot format compatibility, or how `min-blob-size` affects Titan versus RocksDB performance in YCSB point read, scan, and write workloads.
- Retrieval Keywords: Range Merge, Garbage Collection, Level Merge, OnCompactionComplete, sorted runs, ToMerge, level_compaction_dynamic_level_bytes, LSM-tree, blob file, Scale out and scale in, TiKV snapshots, RocksDB format, Titan format, compaction, higher compression rate, write amplification, min-blob-size, Point_Get, scan100, scan10000, UPDATE, YCSB, row width, Dumpling
- Follow-up Guidance: The content also states that with row width `16KB`, Titan outperforms RocksDB in all YCSB workloads in the table, while heavy scan loads such as Dumpling can reduce Titan performance by 10%, and it gives `min-blob-size` guidance for write and point-read workloads versus scan-heavy workloads.
- Classification Note: This chunk is classified as performance because it explains GC range-merge behavior, scaling-related storage format characteristics, and benchmarked QPS impact of the `min-blob-size` setting across read, scan, and write workloads.

## Official Source Content

#### Range Merge

Range Merge is an optimized approach of GC based on Level Merge. However, the bottom level of LSM-tree might be in poorer order in the following situations:

- When `level_compaction_dynamic_level_bytes` is enabled, data volume at each level of LSM-tree dynamically increases, and the sorted runs at the bottom level keep increasing.
- A specific range of data is frequently compacted, and this causes a lot of sorted runs in that range.

![RangeMerge](/media/titan/titan-7.png)

Therefore, the Range Merge operation is needed to keep the number of sorted runs within a certain level. At the time of OnCompactionComplete, Titan counts the number of sorted runs in a range. If the number is large, Titan marks the corresponding blob file as ToMerge and rewrites it in the next compaction.
### Scale out and scale in

For backward compatibility, the TiKV snapshots are still in the RocksDB format during scaling. Because the scaled nodes are all from RocksDB at the beginning, they carry the characteristics of RocksDB, such as higher compression rate than the old TiKV nodes, smaller store size, and relatively larger write amplification in compaction. These SST files in RocksDB format will be gradually converted to Titan format after compaction.
### Impact of `min-blob-size` on performance

[`min-blob-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#min-blob-size) determines whether a value is stored in Titan. If the value is greater than or equal to `min-blob-size`, it is stored in Titan. Otherwise, it is stored in the native RocksDB format. If `min-blob-size` is too small or too large, the performance will be affected.

The following table lists the QPS comparison of the YCSB workload based on different `min-blob-size` values. In each round of testing, the row width of the test data is equal to `min-blob-size`, so that the data is stored in Titan when Titan is enabled.

| Row width (Bytes)      | `Point_Get` |  `Point_Get` (Titan)| scan100 | scan100 (Titan)| scan10000 | scan10000 (Titan)| `UPDATE` | `UPDATE` (Titan) |
| ---------------- | ---------| -------------- | --------| ------------- | --------- | --------------- | ------ | ------------ |
| 1KB  | 139255 | 140486 | 25171 | 21854 | 533 | 175 | 17913 | 30767 |
| 2KB | 114201 |124075 | 12466 |11552 |249 |131 |10369 | 27188 |
| 4KB | 92385   | 103811 | 7918 | 5937 | 131 | 87 | 5327  | 22653 |
| 8KB  |104380  | 130647 | 7365 | 5402 | 86.6 | 68 | 3180 | 16745 |
| 16KB | 54234  | 54600  | 4937 | 5174 | 55.4 | 58.9 |1753 | 10120 |
| 32KB | 31035  |31052  | 2705 | 3422 | 38 | 45.3 | 984 | 5844 |

> **Note:**
>
> `scan100` means scanning 100 records, and `scan10000` means scanning 10000 records.

From the table, you can see that when the row width is `16KB`, Titan outperforms RocksDB in all YCSB workloads. However, in some extreme scenarios with heavy scan loads, such as running Dumpling, Titan's performance with a row width of `16KB` decreases by 10%. Therefore, if the workload is mainly write and point read, it is recommended that you set `min-blob-size` to `1KB`. If the workload contains a large number of scans, it is recommended that you set `min-blob-size` to at least `16KB`.
