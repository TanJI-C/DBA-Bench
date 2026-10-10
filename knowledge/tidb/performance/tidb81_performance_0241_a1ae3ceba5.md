# Physical import mode performance tuning and concurrency settings

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-physical-import-mode-usage.md`
- Source Title: `Use Physical Import Mode`
- Source Heading Path: `Use Physical Import Mode > Performance tuning`
- Source Line Ranges: `234-278`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tikv`
- Topic Tags: `performance-tuning`, `concurrency`, `hardware`, `parallel-import`, `cpu`, `io`, `threads`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0241_a1ae3ceba5`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-physical-import-mode-usage.md#performance-tuning`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ae76dd152e88c108e4728bf8de07e2becb0764b60725835acd59f009bb5fce89`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#performance-tuning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-physical-import-mode-usage.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about improving physical import mode performance, understanding Lightning concurrency settings, or how `region-concurrency`, `table-concurrency`, `index-concurrency`, `io-concurrency`, and TiKV `num-threads` affect import behavior.
- Retrieval Keywords: Performance tuning, parallel import, sorted-key-dir, index-concurrency, table-concurrency, region-concurrency, io-concurrency, num-threads, physical import mode, data engines, index engine, 100 GiB, number of logical CPUs, CPU cores
- Follow-up Guidance: The content states that the most direct ways to improve performance are upgrading the Lightning node hardware, especially CPU and `sorted-key-dir` storage, and using parallel import for horizontal scaling.
- Classification Note: This is classified as performance because the content focuses on import throughput tuning, hardware factors, and concurrency parameters that influence physical import efficiency.

## Official Source Content

## Performance tuning

**The most direct and effective ways to improve import performance of the physical import mode are as follows:**

- **Upgrade the hardware of the node where Lightning is deployed, especially the CPU and the storage device of `sorted-key-dir`.**
- **Use the [parallel import](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-distributed-import) feature to achieve horizontal scaling.**

TiDB Lightning provides some concurrency-related configurations to affect import performance in the physical import mode. However, from long-term experience, it is recommended to keep the following four configuration items in the default value. Adjusting the four configuration items does not bring significant performance boost.

```
[lightning]
# The maximum concurrency of engine files.
# Each table is split into one "index engine" to store indices, and multiple
# "data engines" to store row data. These settings control the maximum
# concurrent number for each type of engines.
# The two settings controls the maximum concurrency of the two engine files.
index-concurrency = 2
table-concurrency = 6

# The concurrency of data. The default value is the number of logical CPUs.
region-concurrency =

# The maximum concurrency of I/O. When the concurrency is too high, the disk
# cache may be frequently refreshed, causing the cache miss and read speed
# to slow down. For different storage mediums, this parameter may need to be
# adjusted to achieve the best performance.
io-concurrency = 5
```

During the import, each table is split into one "index engine" to store indices, and multiple "data engines" to store row data.

`index-concurrency` controls the maximum concurrency of the index engine. When you adjust `index-concurrency`, make sure that `index-concurrency * the number of source files of each table > region-concurrency` to ensure that the CPU is fully utilized. The ratio is usually between 1.5 ~ 2. Do not set `index-concurrency` too high and not lower than 2 (default). Too high `index-concurrency` causes too many pipelines to be built, which causes the index-engine import stage to pile up.

The same goes for `table-concurrency`. Make sure that `table-concurrency * the number of source files of each table > region-concurrency` to ensure that the CPU is fully utilized. A recommended value is around `region-concurrency * 4 / the number of source files of each table` and not lower than 4.

If the table is large, Lightning will split the table into multiple batches of 100 GiB. The concurrency is controlled by `table-concurrency`.

`index-concurrency` and `table-concurrency` has little effect on the import speed. You can leave them in the default value.

`io-concurrency` controls the concurrency of file read. The default value is 5. At any given time, only 5 handles are performing read operations. Because the file read speed is usually not a bottleneck, you can leave this configuration in the default value.

After the file data is read, Lightning needs to do some post-processing, such as encoding and sorting the data locally. The concurrency of these operations is controlled by `region-concurrency`. The default value is the number of CPU cores. You can leave this configuration in the default value. It is recommended to deploy Lightning on a separate server from other components. If you must deploy Lightning together with other components, you need to lower the value of `region-concurrency` according to the load.

The [`num-threads`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#num-threads) configuration of TiKV can also affect the performance. For new clusters, it is recommended to set `num-threads` to the number of CPU cores.
