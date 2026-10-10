# Performance feature updates in TiDB 7.4.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.4.0.md`
- Source Title: `TiDB 7.4.0 Release Notes`
- Source Heading Path: `TiDB 7.4.0 Release Notes > Feature details > Performance`
- Source Line Ranges: `95-124`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `sql`, `cloud`
- Topic Tags: `performance`, `pushdown`, `json`, `window-functions`, `global-sort`, `add-index`, `import-into`, `plan-cache`, `non-prepared-statements`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0505_bae4d952b6`
- Source ID: `tidb-docs-8.1:releases/release-7.4.0.md#performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0415a432e2e5c9c1b3589b8ffe6c3cb53500b49264ad603c2898f0bf673d3227`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.4.0#performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.4.0 performance changes involving pushdown, Global Sort for DXF tasks, or non-prepared statement plan cache behavior.
- Retrieval Keywords: TiDB 7.4.0 Performance, MEMBER OF pushdown to TiKV, value MEMBER OF(json_array), window functions pushdown to TiFlash, PRECEDING FOLLOWING TiFlash, Global Sort, cloud storage-based global sort, ADD INDEX, IMPORT INTO, Distributed eXecution Framework, DXF, non-prepared plan cache, caching execution plans for non-prepared statements, tidb_enable_non_prepared_plan_cache, tidb_session_plan_cache_size, Restrictions
- Follow-up Guidance: The source points to documentation for expressions pushed down, TiDB Global Sort, and SQL non-prepared plan cache restrictions and system variables.
- Classification Note: This is a release-note performance section summarizing shared feature updates across TiDB, TiKV, TiFlash, SQL, and cloud-related capabilities in TiDB 7.4.0.

## Official Source Content

### Performance

* Support pushing down the JSON operator `MEMBER OF` to TiKV [#46307](https://github.com/pingcap/tidb/issues/46307) @[wshwsh12](https://github.com/wshwsh12)

    * `value MEMBER OF(json_array)`

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/functions-and-operators/expressions-pushed-down).

* Support pushing down window functions with any frame definition type to TiFlash [#7376](https://github.com/pingcap/tiflash/issues/7376) @[xzhangxian1008](https://github.com/xzhangxian1008)

    Before v7.4.0, TiFlash does not support window functions containing `PRECEDING` or `FOLLOWING`, and all window functions containing such frame definitions cannot be pushed down to TiFlash. Starting from v7.4.0, TiFlash supports frame definitions of all window functions. This feature is enabled automatically, and window functions containing frame definitions will be automatically pushed down to TiFlash for execution when the related requirements are met.

* Introduce cloud storage-based global sort capability to improve the performance and stability of `ADD INDEX` and `IMPORT INTO` tasks in parallel execution (experimental) [#45719](https://github.com/pingcap/tidb/issues/45719) @[wjhuang2016](https://github.com/wjhuang2016)

    Before v7.4.0, when executing tasks like `ADD INDEX` or `IMPORT INTO` in the Distributed eXecution Framework (DXF), each TiDB node needs to allocate a significant amount of local disk space for sorting encoded index KV pairs and table data KV pairs. However, due to the lack of global sorting capability, there might be overlapping data between different TiDB nodes and within each individual node during the process. As a result, TiKV has to constantly perform compaction operations while importing these KV pairs into its storage engine, which impacts the performance and stability of `ADD INDEX` and `IMPORT INTO`.

    In v7.4.0, TiDB introduces the [Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort) feature. Instead of writing the encoded data locally and sorting it there, the data is now written to cloud storage for global sorting. Once sorted, both the indexed data and table data are imported into TiKV in parallel, thereby improving performance and stability.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-global-sort).

* Support caching execution plans for non-prepared statements (GA) [#36598](https://github.com/pingcap/tidb/issues/36598) @[qw4990](https://github.com/qw4990)

    TiDB v7.0.0 introduces non-prepared plan cache as an experimental feature to improve the load capacity of concurrent OLTP. In v7.4.0, this feature becomes GA. The execution plan cache will be applied to more scenarios, thereby improving the concurrent processing capacity of TiDB.

    Enabling the non-prepared plan cache might incur additional memory and CPU overhead and might not be suitable for all situations. Starting from v7.4.0, this feature is disabled by default. You can enable it using [`tidb_enable_non_prepared_plan_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_non_prepared_plan_cache) and control the cache size using [`tidb_session_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_session_plan_cache_size-new-in-v710).

    Additionally, this feature does not support DML statements by default and has certain restrictions on SQL statements. For more details, see [Restrictions](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache#restrictions).

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache).
