# TiDB 6.1.1 improvements across TiDB, TiKV, PD, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.1.md`
- Source Title: `TiDB 6.1.1 Release Notes`
- Source Heading Path: `TiDB 6.1.1 Release Notes > Improvements`
- Source Line Ranges: `38-69`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `lightning`, `dm`, `ticdc`
- Topic Tags: `optimizer`, `metrics-compression`, `simplify-metrics`, `rocksdb`, `scheduling`, `import-retry`, `loader-concurrency`, `changefeed`, `mysql-sink`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0306_8c78787afc`
- Source ID: `tidb-docs-8.1:releases/release-6.1.1.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `934fd007985200a40bf641f9a47c48058fd86ed748b56479cc01936d7f4ab99e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.1#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.1.1 improvements across TiDB, TiKV, PD, TiDB Lightning, DM, and TiCDC, especially optimizer, metrics, scheduling, import, and changefeed enhancements.
- Retrieval Keywords: TiDB 6.1.1 Improvements, SEMI_JOIN_REWRITE, EXISTS queries, #35323, gzip metrics response, server.simplify-metrics, simplify-metrics new in v6.1.1, rocksdb.max-sub-compactions, Balance Region scheduling speed, #4990, stale command retry, TiDB Lightning retry mechanism, #36877, lightning loader concurrency, DM manually set concurrency, #5505, transaction-atomicity, split large transaction in a changefeed, TiCDC multi-Region runtime context switching, #5610, MySQL sink safe mode automatically off, #5611
- Follow-up Guidance: The source identifies the exact configuration items and sink uri parameter names for the listed improvements.
- Classification Note: This chunk is classified as a release improvement summary because it lists new optimizations, configuration capabilities, and tool enhancements introduced in TiDB 6.1.1.

## Official Source Content

## Improvements

+ TiDB

    - Add a new optimizer `SEMI_JOIN_REWRITE` to improve the performance of `EXISTS` queries [#35323](https://github.com/pingcap/tidb/issues/35323) @[winoros](https://github.com/winoros)

+ TiKV

    - Support compressing the metrics response using gzip to reduce the HTTP body size [#12355](https://github.com/tikv/tikv/issues/12355) @[winoros](https://github.com/winoros)
    - Support reducing the amount of data returned for each request by filtering out some metrics using the [`server.simplify-metrics`](https://docs.pingcap.com/tidb/v6.1/tikv-configuration-file#simplify-metrics-new-in-v611) configuration item [#12355](https://github.com/tikv/tikv/issues/12355) @[glorv](https://github.com/glorv)
    - Support dynamically modifying the number of sub-compaction operations performed concurrently in RocksDB (`rocksdb.max-sub-compactions`) [#13145](https://github.com/tikv/tikv/issues/13145) @[ethercflow](https://github.com/ethercflow)

+ PD

    - Improve the scheduling speed of Balance Region in specific stages [#4990](https://github.com/tikv/pd/issues/4990) @[bufferflies](https://github.com/bufferflies)

+ Tools

    + TiDB Lightning

        - Add a retry mechanism on errors such as `stale command` to improve import success rate [#36877](https://github.com/pingcap/tidb/issues/36877) @[D3Hunter](https://github.com/D3Hunter)

    + TiDB Data Migration (DM)

        - Users can manually set the amount of concurrency for lightning loader [#5505](https://github.com/pingcap/tiflow/issues/5505) @[buchuitoudegou](https://github.com/buchuitoudegou)

    + TiCDC

        - Add a sink uri parameter `transaction-atomicity` to support splitting the large transaction in a changefeed. This can greatly reduce the latency and memory consumption of large transactions [#5231](https://github.com/pingcap/tiflow/issues/5231) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Reduce performance overhead caused by runtime context switching in multi-Region scenarios [#5610](https://github.com/pingcap/tiflow/issues/5610) @[hicqu](https://github.com/hicqu)
        - Enhance the MySQL sink to turn off the safe mode automatically [#5611](https://github.com/pingcap/tiflow/issues/5611) @[overvenus](https://github.com/overvenus)
