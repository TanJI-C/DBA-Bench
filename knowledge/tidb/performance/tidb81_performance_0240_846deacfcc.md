# Logical import performance tuning

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-logical-import-mode-usage.md`
- Source Title: `Use Logical Import Mode`
- Source Heading Path: `Use Logical Import Mode > Performance tuning`
- Source Line Ranges: `63-76`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`
- Topic Tags: `write performance`, `region-concurrency`, `raftstore`, `apply pool`, `store pool`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0240_846deacfcc`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-logical-import-mode-usage.md#performance-tuning`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `acf8c67ff1be0dfabba08832bfc9e9ad4c0efc8570a9f319dab3e4222827bef3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode-usage#performance-tuning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-logical-import-mode-usage.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how to tune TiDB Lightning logical import mode performance, especially write concurrency and related target cluster settings.
- Retrieval Keywords: Performance tuning, region-concurrency, write concurrency, Highly Concurrent Write Best Practices, raftstore.apply-pool-size, raftstore.store-pool-size, logical import mode, target TiDB cluster write performance
- Follow-up Guidance: If the target TiDB cluster does not hit a write bottleneck, consider increasing region-concurrency; adjusting raftstore.apply-pool-size and raftstore.store-pool-size might improve import speed.
- Classification Note: This is classified as performance because the content focuses on import speed, write bottlenecks, concurrency, and target cluster tuning items.

## Official Source Content

## Performance tuning

- In the logical import mode, the performance of TiDB Lightning largely depends on the write performance of the target TiDB cluster. If the cluster hits a performance bottleneck, refer to [Highly Concurrent Write Best Practices](https://docs.pingcap.com/tidb/stable/best-practices/high-concurrency-best-practices).

- If the target TiDB cluster does not hit a write bottleneck, consider increasing the value of `region-concurrency` in TiDB Lightning configuration. The default value of `region-concurrency` is the number of CPU cores. The meaning of `region-concurrency` is different between the physical import mode and the logical import mode. In the logical import mode, `region-concurrency` is the write concurrency.

    Example configuration:

    ```toml
    [lightning]
    region-concurrency = 32
    ```

- Adjusting the `raftstore.apply-pool-size` and `raftstore.store-pool-size` configuration items in the target TiDB cluster might improve the import speed.
