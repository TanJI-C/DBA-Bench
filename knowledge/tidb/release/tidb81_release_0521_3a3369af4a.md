# 7.5.0 improvements across TiDB, TiKV, PD, and BR

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.0.md`
- Source Title: `TiDB 7.5.0 Release Notes`
- Source Heading Path: `TiDB 7.5.0 Release Notes > Improvements`
- Source Line Ranges: `212-235`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `pd`, `tidb`, `tikv`
- Topic Tags: `improvements`, `performance`, `statistics`, `analyze`, `placement-policies`, `ddl`, `scheduler`, `backup`, `restore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0521_3a3369af4a`
- Source ID: `tidb-docs-8.1:releases/release-7.5.0.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `de164c541630dc24b645db96da450a6ab757cb96d5298d225c7f75c8fcbd6cc3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.0 improvements in performance, statistics, ANALYZE, placement policies, DDL, PD scheduling, TiKV internals, or BR backup and restore behavior.
- Retrieval Keywords: TiDB 7.5.0 improvements, tidb_enable_async_merge_global_stats, GlobalStats, partitioned tables, tidb_build_sampling_stats_concurrency, ANALYZE concurrency, placement policies global range, tidb_ddl_enable_fast_reorg, adding indexes performance, Titan manifest files mutex, evict-slow-trend scheduler, BR table-concurrency, snapshot backups, statistics backup, data validation, BR retries network errors during restore
- Follow-up Guidance: The chunk provides improvement details for TiDB, TiKV, PD, and BR, including new system variables and the new BR parameter `table-concurrency` for snapshot backups.
- Classification Note: This is a release-notes improvements section because the content summarizes product enhancements and performance or usability changes shipped in TiDB 7.5.0.

## Official Source Content

## Improvements

+ TiDB

    - Optimize the concurrency model of merging GlobalStats: introduce [`tidb_enable_async_merge_global_stats`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_async_merge_global_stats-new-in-v750) to enable simultaneous loading and merging of statistics, which speeds up the generation of GlobalStats on partitioned tables. Optimize the memory usage of merging GlobalStats to avoid OOM and reduce memory allocations. [#47219](https://github.com/pingcap/tidb/issues/47219) @[hawkingrei](https://github.com/hawkingrei)
    - Optimize the `ANALYZE` process: introduce [`tidb_build_sampling_stats_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_build_sampling_stats_concurrency-new-in-v750) to better control the `ANALYZE` concurrency to reduce resource consumption. Optimize the memory usage of `ANALYZE` to reduce memory allocation and avoid frequent GC by reusing some intermediate results. [#47275](https://github.com/pingcap/tidb/issues/47275) @[hawkingrei](https://github.com/hawkingrei)
    - Optimize the use of placement policies: support configuring the range of a policy to global and improve the syntax support for common scenarios. [#45384](https://github.com/pingcap/tidb/issues/45384) @[nolouch](https://github.com/nolouch)
    - Improve the performance of adding indexes with `tidb_ddl_enable_fast_reorg` enabled. In internal tests, v7.5.0 improves the performance by up to 62.5% compared with v6.5.0. [#47757](https://github.com/pingcap/tidb/issues/47757) @[tangenta](https://github.com/tangenta)

+ TiKV

    - Avoid holding mutex when writing Titan manifest files to prevent affecting other threads [#15351](https://github.com/tikv/tikv/issues/15351) @[Connor1996](https://github.com/Connor1996)

+ PD

    - Improve the stability and usability of the `evict-slow-trend` scheduler [#7156](https://github.com/tikv/pd/issues/7156) @[LykxSassinato](https://github.com/LykxSassinator)

+ Tools

    + Backup & Restore (BR)

        - Add a new inter-table backup parameter `table-concurrency` for snapshot backups. This parameter is used to control the inter-table concurrency of meta information such as statistics backup and data validation [#48571](https://github.com/pingcap/tidb/issues/48571) @[3pointer](https://github.com/3pointer)
        - During restoring a snapshot backup, BR retries when it encounters certain network errors [#48528](https://github.com/pingcap/tidb/issues/48528) @[Leavrth](https://github.com/Leavrth)
