# Coprocessor Cache overview, configuration, and behavior

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/coprocessor-cache.md`
- Source Title: `Coprocessor Cache`
- Source Heading Path: `Coprocessor Cache | Coprocessor Cache > Configuration | Coprocessor Cache > Feature description`
- Source Line Ranges: `5-45`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `coprocessor-cache`, `pushdown`, `cache-behavior`, `cache-invalidation`, `memory-cache`, `configuration`, `region-cache`, `sql-execution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0085_1a36d9eaa1`
- Source ID: `tidb-docs-8.1:coprocessor-cache.md#coprocessor-cache`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6bbc01cc5e26175d3eb9973efcf62d3887e8fb3c5c60a148c56e7865c60c3e46`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/coprocessor-cache#coprocessor-cache
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/coprocessor-cache.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about what Coprocessor Cache is, how `tikv-client.copr-cache` is configured, and when push-down calculation results are cached or invalidated on a TiDB instance.
- Retrieval Keywords: Coprocessor Cache, tikv-client.copr-cache, pushed down to TiKV, enabled by default, 1000 MB, cache is not shared among TiDB instances, cache is in the unit of Region, Writing data to a Region causes the Region cache to be invalid, same SQL statement is executed repeatedly, compound index column, primary key of the table or the partition
- Follow-up Guidance: The source also states that cache effect can be checked by `EXPLAIN ANALYZE` or the Grafana **copr-cache** panel.
- Classification Note: This is classified as performance because the supplied content explains a TiDB caching feature that accelerates pushed-down calculation and affects SQL execution time without changing results.

## Official Source Content

# Coprocessor Cache

Starting from v4.0, the TiDB instance supports caching the results of the calculation that is pushed down to TiKV (the Coprocessor Cache feature), which can accelerate the calculation process in some scenarios.
## Configuration

You can configure Coprocessor Cache via the `tikv-client.copr-cache` configuration items in the TiDB configuration file. For details about how to enable and configure Coprocessor Cache, see [TiDB Configuration File](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tikv-clientcopr-cache-new-in-v400).

The Coprocessor Cache feature is enabled by default. The maximum size of the data that can be cached is 1000 MB.
## Feature description

+ When a SQL statement is executed on a single TiDB instance for the first time, the execution result is not cached.
+ Calculation results are cached in the memory of TiDB. If the TiDB instance is restarted, the cache becomes invalid.
+ The cache is not shared among TiDB instances.
+ Only push-down calculation result is cached. Even if cache is hit, TiDB still need to perform subsequent calculation.
+ The cache is in the unit of Region. Writing data to a Region causes the Region cache to be invalid. For this reason, the Coprocessor Cache feature mainly takes effect on the data that rarely changes.
+ When push-down calculation requests are the same, the cache is hit. Usually in the following scenarios, the push-down calculation requests are the same or partially the same:
    - The SQL statements are the same. For example, the same SQL statement is executed repeatedly.

        In this scenario, all the push-down calculation requests are consistent, and all requests can use the push-down calculation cache.

    - The SQL statements contain a changing condition, and the other parts are consistent. The changing condition is the primary key of the table or the partition.

        In this scenario, some of the push-down calculation requests are the same with some previous requests, and these calculation requests can use the cached (previous) push-down calculation result.

    - The SQL statements contain multiple changing conditions and the other parts are consistent. The changing conditions exactly match a compound index column.

        In this scenario, some of the push-down calculation requests are the same with some previous requests, and these calculation requests can use the cached (previous) push-down calculation result.

+ This feature is transparent to users. Enabling or disabling this feature does not affect the calculation result and only affects the SQL execution time.
