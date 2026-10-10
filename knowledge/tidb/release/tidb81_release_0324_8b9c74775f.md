# Performance features in TiDB and TiFlash

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.2.0.md`
- Source Title: `TiDB 6.2.0 Release Notes`
- Source Heading Path: `TiDB 6.2.0 Release Notes > New features > Performance`
- Source Line Ranges: `75-142`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `sql`, `tidb`, `tiflash`
- Topic Tags: `optimizer-hints`, `join-order`, `exists-queries`, `cte`, `aggregation`, `concurrent-ddl`, `string-matching`, `window-functions`, `fine-grained-shuffle`, `storage-format`, `fastscan`, `experimental`, `downgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0324_8b9c74775f`
- Source ID: `tidb-docs-8.1:releases/release-6.2.0.md#performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `95a38496431c1b441ba890c2ab10facb64d0643a6a23064af7219c9f44030c0d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.2.0#performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.2.0 performance release-note details about optimizer hints, TiFlash execution improvements, concurrent DDL, storage format changes, FastScan, or scanning behavior.
- Retrieval Keywords: TiDB 6.2.0 Performance, LEADING optimizer hint outer join ordering, SEMI_JOIN_REWRITE EXISTS queries, MERGE optimizer hint CTE TiFlash MPP, COUNT(DISTINCT) single column skew distinct agg, tidb_opt_skew_distinct_agg, concurrent DDL framework, string matching selectivity like '%xyz' regex(), tidb_default_string_match_selectivity, window functions pushed down to TiFlash multiple threads, Fine Grained Shuffle, tiflash_fine_grained_shuffle_batch_size, TiFlash newer version of storage format, cannot perform in-place downgrade on TiFlash, TiFlash Upgrade Guide, TiFlash data scanning performance multiple concurrency experimental, FastScan skipping consistency checks, tiflash use-fastscan
- Follow-up Guidance: The content also points to related user documents such as optimizer hints, system variables, the TiFlash Upgrade Guide, TiFlash configuration, and FastScan usage.
- Classification Note: This is classified as a release chunk because it summarizes new performance features introduced in TiDB 6.2.0 across TiDB and TiFlash.

## Official Source Content

### Performance

* Improve the `LEADING` optimizer hint to support outer join ordering

    In v6.1.0, the optimizer hint `LEADING` was introduced to modify the join order of tables. But this hint was not applicable to queries that contain outer joins. For more information, see [`LEADING` document](https://docs.pingcap.com/tidb/stable/optimizer-hints#leadingt1_name--tl_name-). In v6.2.0, TiDB lifts this restriction. In a query that contains outer join, now you can use this hint to specify the join order of tables to get better SQL execution performance and to avoid the sudden change of execution plans.

    [User document](https://docs.pingcap.com/tidb/stable/optimizer-hints#leadingt1_name--tl_name-) [#29932](https://github.com/pingcap/tidb/issues/29932) @[Reminiscent](https://github.com/Reminiscent)

* Add a new optimizer `SEMI_JOIN_REWRITE` to improve the performance of `EXISTS` queries

    In some scenarios, queries with `EXISTS` cannot have the optimal execution plan and might be executed for too long. In v6.2.0, the optimizer adds rewriting rules for such scenarios, and you can use `SEMI_JOIN_REWRITE` in queries to forcibly make the optimizer rewrite the query and get better query performance.

    [User document](https://docs.pingcap.com/tidb/stable/optimizer-hints#semi_join_rewrite) [#35323](https://github.com/pingcap/tidb/issues/35323) @[winoros](https://github.com/winoros)

* Add a new optimizer hint `MERGE` to improve the performance of analytical queries

    Common table expression (CTE) is an effective way to simplify the query logic. It is widely used to write complex queries. Before v6.2.0, CTE cannot be automatically expanded in TiFlash environments, which, to some extent, limits the execution efficiency of MPP. In v6.2.0, a MySQL-compatible optimizer hint `MERGE` is introduced. With this hint, the optimizer now allows CTE inlines to be expanded, so that the consumers of the CTE query results can concurrently execute the query in TiFlash, which improves the performance of some analytical queries.

    [User document](https://docs.pingcap.com/tidb/stable/optimizer-hints#merge) [#36122](https://github.com/pingcap/tidb/issues/36122) @[dayicklp](https://github.com/dayicklp)

* Optimize the performance of aggregation operations in some analytical scenarios

    When you use TiFlash to perform aggregation operations on a column in an OLAP scenario, if serious data skew exists due to uneven distribution of the aggregated column, and if the aggregated column has many different values, the execution efficiency of `COUNT(DISTINCT)` queries on the column is low. In v6.2.0, new rewriting rules are introduced to improve the performance of `COUNT(DISTINCT)` queries on a single column.

    [User document](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_skew_distinct_agg-new-in-v620) [#36169](https://github.com/pingcap/tidb/issues/36169) @[fixdb](https://github.com/fixdb)

* TiDB supports concurrent DDL operations

    TiDB v6.2.0 introduces a new concurrent DDL framework, which enables DDL statements to be concurrently executed on different table objects and fixes the issue that DDL operations are blocked by DDL operations on other tables. In addition, TiDB supports concurrent DDL execution when adding an index on multiple tables or changing a column type. This improves the efficiency of DDL execution.

    [#32031](https://github.com/pingcap/tidb/issues/32031) @[wjhuang2016](https://github.com/wjhuang2016)

* Optimizer enhances the estimation of string matching

    In the string matching scenario, if the optimizer cannot accurately estimate the number of rows, it affects the generation of the optimal execution plan. For example, the condition is `like '%xyz'` or using a regular expression `regex ()`. To improve the estimation accuracy in such scenarios, TiDB v6.2.0 enhances the estimation method. The new method combines the TopN information of statistics and system variables to improve the accuracy and makes it possible to modify the match selectivity manually, thus improving the SQL performance.

    [User document](https://docs.pingcap.com/tidb/stable/system-variables#tidb_default_string_match_selectivity-new-in-v620) [#36209](https://github.com/pingcap/tidb/issues/36209) @[time-and-fate](https://github.com/time-and-fate)

* Window functions pushed down to TiFlash can be executed in multiple threads

    After the Fine Grained Shuffle feature is enabled, window functions can be executed in multiple threads, instead of in a single thread. This feature reduces the query response time significantly without changing user behavior. You can control the granularity of the shuffle by adjusting the value of the variables.

    [User document](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_fine_grained_shuffle_batch_size-new-in-v620) [#4631](https://github.com/pingcap/tiflash/issues/4631) @[guo-shaoge](https://github.com/guo-shaoge)

* TiFlash supports a newer version of storage format

    The new storage format relieves high CPU usage caused by GC in high-concurrency and heavy workload scenarios. This significantly reduces IO traffic of background tasks, thereby boosting stability under high concurrencies and heavy workloads. At the same time, space amplification and disk waste can be significantly reduced.

    In TiDB v6.2.0, data is stored in the new storage format by default. Note that if TiFlash is upgraded from earlier versions to v6.2.0, you cannot perform in-place downgrade on TiFlash, because earlier TiFlash versions cannot recognize the new storage format.

    For more information about upgrading TiFlash, see [TiFlash Upgrade Guide](https://docs.pingcap.com/tidb/stable/tiflash-upgrade-guide).

    [User document](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) [#3594](https://github.com/pingcap/tiflash/issues/3594) @[JaySon-Huang](https://github.com/JaySon-Huang) @[lidezhu](https://github.com/lidezhu) @[jiaqizho](https://github.com/jiaqizho)

* TiFlash optimizes data scanning performance in multiple concurrency scenarios (experimental)

    TiFlash reduces duplicate reads of the same data by merging read operations of the same data, and optimizes the resource overhead in the case of multiple concurrent tasks to improve data scanning performance. It avoids the situation where the same data has to be read separately in each task, or even the same data may be read multiple times at the same time, if the same data is involved in multiple concurrent tasks.

    [User document](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) [#5376](https://github.com/pingcap/tiflash/issues/5376) @[JinheLin](https://github.com/JinheLin)

* TiFlash adds FastScan for data scanning to increase read and write speed by sacrificing data consistency (experimental)

    TiDB introduces FastScan in v6.2.0. It supports skipping consistency checks to increase the speed significantly. FastScan is suitable for scenarios that do not require high accuracy and consistency of data such as offline analysis tasks. Previously, to ensure data consistency, TiFlash needed to perform data consistency checks during the data scanning process to find the required data from multiple different versions.

    When you upgrade from an earlier version to TiDB v6.2.0, FastScan is not enabled by default for all tables, which ensures data consistency. You can enable FastScan for each table independently. If the table is set to FastScan in TiDB v6.2.0, it will be disabled when you downgrade to a lower version, but this does not affect the normal data read. In this case, it is equivalent to strong consistency read.
    [User document](https://docs.pingcap.com/tidb/stable/tiflash/use-fastscan) [#5252](https://github.com/pingcap/tiflash/issues/5252) @[hongyunyan](https://github.com/hongyunyan)
