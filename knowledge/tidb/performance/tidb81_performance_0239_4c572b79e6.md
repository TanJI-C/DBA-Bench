# Comparison of sort method, performance, availability, and scalability

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/import-into-vs-tidb-lightning.md`
- Source Title: `IMPORT INTO vs. TiDB Lightning`
- Source Heading Path: `IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Global Sort vs. local sort | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Global Sort vs. local sort > `IMPORT INTO` | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Global Sort vs. local sort > TiDB Lightning | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Performance | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > High availability | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > High availability > `IMPORT INTO` | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > High availability > TiDB Lightning | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Scalability | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Scalability > `IMPORT INTO` | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Scalability > TiDB Lightning`
- Source Line Ranges: `66-112`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `sql`, `tidb`, `tikv`, `shared`
- Topic Tags: `global-sort`, `local-sort`, `performance`, `throughput`, `high-availability`, `manual-recovery`, `scalability`, `compaction`, `s3`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0239_4c572b79e6`
- Source ID: `tidb-docs-8.1:tidb-lightning/import-into-vs-tidb-lightning.md#global-sort-vs-local-sort`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `175e1d24f4f4cd29462921b729c21888a9f36dfec5001537d917ae9f41bdcca2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/import-into-vs-tidb-lightning#global-sort-vs-local-sort
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/import-into-vs-tidb-lightning.md

## Retrieval Guidance

- Use When: Use this chunk when comparing `IMPORT INTO` and TiDB Lightning for global sort versus local sort, import performance data, high availability after node failure, or scalability effects from TiKV compaction.
- Retrieval Keywords: Global Sort vs. local sort, TiDB Global Sort, local sort, Amazon S3, TiKV compaction, RocksDB, write performance, high availability, manual recovery, checkpoints, scalability, 40 TiB data, 10 TiB data, average import speed per TiDB node, 222 GiB/h, 307 GiB/h
- Follow-up Guidance: It includes the official `IMPORT INTO` performance table for Amazon S3 global sorting and states that failed `IMPORT INTO` tasks are automatically transferred to remaining TiDB nodes, while TiDB Lightning requires manual recovery based on checkpoints.
- Classification Note: The chunk is classified as performance because the official content focuses on sort method impact, measured import speed, TiKV compaction effects, availability behavior, and scalability.

## Official Source Content

### Global Sort vs. local sort
#### `IMPORT INTO`

With TiDB Global Sort, `IMPORT INTO` can transmit tens of TiB of source data to multiple TiDB nodes, encode the data KV pairs and index KV pairs, and then transfer these pairs to Amazon S3 for global sorting before writing them into TiKV.

Because these KV pairs are globally sorted, data imported from various TiDB nodes into TiKV does not overlap, allowing it to be written directly into the RocksDB. This eliminates the need for TiKV to perform compaction operations, resulting in significant improvement in both write performance and stability of TiKV.

After the import is completed, the data used for global sorting on Amazon S3 will be automatically deleted, saving storage costs.
#### TiDB Lightning

TiDB Lightning only supports local sort. For example, for tens of TiB of source data, if TiDB Lightning does not have large local disks configured, or if multiple TiDB Lightning instances are used for parallel import, each TiDB Lightning instance can only use local disks to sort the data to be imported. Due to the inability to perform global sort, there will be an overlap between the data imported into TiKV by multiple TiDB Lightning instances, especially in scenarios where index data is more prevalent, triggering TiKV to perform compaction operations. Compaction operations are resource-intensive, which will lead to a decrease in TiKV's write performance and stability.

If you want to continue importing data later, you will need to keep the TiDB Lightning server and the disks on the server for the next import. The cost of using preallocated disks is relatively high, compared with `IMPORT INTO` using Amazon S3 on a pay-as-you-go basis.
### Performance

Currently, there are no performance test comparison results under equivalent test environments between `IMPORT INTO` and TiDB Lightning.

When Amazon S3 is used as the storage for global sorting, the performance test results for `IMPORT INTO` are as follows:

| Source dataset                    | Node configuration                                           | Average import speed per TiDB node |
|------------------------------------|--------------------------------------------------------------|------------------------------------|
| 40 TiB data (2.26 billion rows, 19 KiB per row) | 10 TiDB (16C32G) nodes and 20 TiKV (16C27G) nodes | 222 GiB/h |
| 10 TiB data (565 million rows, 19 KiB per row) | 5 TiDB (16C32G) nodes and 10 TiKV (16C27G) nodes | 307 GiB/h |
### High availability
#### `IMPORT INTO`

After a TiDB node fails, tasks on that node are automatically transferred to the remaining TiDB nodes to continue running.
#### TiDB Lightning

After a TiDB Lightning instance node fails, you need to perform manual recovery of tasks on a new node based on previously recorded checkpoints.
### Scalability
#### `IMPORT INTO`

Due to the use of Global Sort, data imported into TiKV does not overlap, resulting in better scalability compared with TiDB Lightning.
#### TiDB Lightning

Due to only supporting local sort, data imported into TiKV might overlap when new TiDB Lightning instances are added, resulting in more compaction operations for TiKV and limiting scalability relative to `IMPORT INTO`.
