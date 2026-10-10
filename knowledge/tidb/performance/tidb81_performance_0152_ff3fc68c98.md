# Performance features: index merge, pushdown, optimizer, and TiFlash improvements

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.0.md`
- Source Title: `TiDB 6.5.0 Release Notes`
- Source Heading Path: `TiDB 6.5.0 Release Notes > New features > Performance`
- Source Line Ranges: `148-191`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `tikv`, `sql`
- Topic Tags: `index-merge`, `optimizer-hints`, `json`, `string-functions`, `pushdown`, `views`, `partitioned-tables`, `cost-model`, `count-star`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0152_ff3fc68c98`
- Source ID: `tidb-docs-8.1:releases/release-6.5.0.md#performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `64090a8a035d026dbd8fe4ca0d0b28a202bc879a26ab9f309f876b5aa4555528`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.0#performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about TiDB 6.5.0 performance enhancements such as INDEX MERGE with AND conditions, TiFlash pushdown support, global optimizer hints in views, partitioned table sort pushdown, Cost Model Version 2, or TiFlash COUNT(*) optimization.
- Retrieval Keywords: INDEX MERGE, AND conditions, USE_INDEX_MERGE, WHERE clause, JSON_EXTRACT(), ->, ->>, regexp_like, regexp_instr, regexp_substr, global optimizer hint, Views, qb_name, partitioned tables, ORDER BY, LIMIT, TiKV pushdown, Cost Model Version 2, tidb_cost_model_version = 2, COUNT(*), TiFlash
- Follow-up Guidance: The source includes follow-up references for Explain Index Merge, optimizer hints that take effect globally, partitioned tables, and Cost Model Version 2 documentation.
- Classification Note: This is classified as performance because all listed changes improve query planning, pushdown execution, storage engine choice, or execution efficiency in TiDB, TiKV, and TiFlash.

## Official Source Content

### Performance

* [INDEX MERGE](https://docs.pingcap.com/tidb/stable/glossary#index-merge) supports expressions connected by `AND` [#39333](https://github.com/pingcap/tidb/issues/39333) @[guo-shaoge](https://github.com/guo-shaoge) @[time-and-fate](https://github.com/time-and-fate) @[hailanwhu](https://github.com/hailanwhu)

    Before v6.5.0, TiDB only supported using index merge for the filter conditions connected by `OR`. Starting from v6.5.0, TiDB has supported using index merge for filter conditions connected by `AND` in the `WHERE` clause. In this way, the index merge of TiDB can now cover more general combinations of query filter conditions and is no longer limited to union (`OR`) relationship. The current v6.5.0 version only supports index merge under `OR` conditions as automatically selected by the optimizer. To enable index merge for `AND` conditions, you need to use the [`USE_INDEX_MERGE`](https://docs.pingcap.com/tidb/stable/optimizer-hints#use_index_merget1_name-idx1_name--idx2_name-) hint.

    For more details about index merge, see [v5.4.0 Release Notes](https://docs.pingcap.com/tidb/stable/releases/release-5.4.0#performance) and [Explain Index Merge](https://docs.pingcap.com/tidb/stable/explain-index-merge).

* Support pushing down the following JSON functions to TiFlash [#39458](https://github.com/pingcap/tidb/issues/39458) @[yibin87](https://github.com/yibin87)

    * `->`
    * `->>`
    * `JSON_EXTRACT()`

  The JSON format provides a flexible way for application data modeling. Therefore, more and more applications are using the JSON format for data exchange and data storage. By pushing down JSON functions to TiFlash, you can improve the efficiency of analyzing data in the JSON type and use TiDB for more real-time analytics scenarios.

* Support pushing down the following string functions to TiFlash [#6115](https://github.com/pingcap/tiflash/issues/6115) @[xzhangxian1008](https://github.com/xzhangxian1008)

    * `regexp_like`
    * `regexp_instr`
    * `regexp_substr`

* Support the global optimizer hint to interfere with the execution plan generation in [Views](https://docs.pingcap.com/tidb/stable/views) [#37887](https://github.com/pingcap/tidb/issues/37887) @[Reminiscent](https://github.com/Reminiscent)

    In some view access scenarios, you need to use optimizer hints to interfere with the execution plan of a query in the view to achieve the optimal performance. Starting from v6.5.0, TiDB supports adding global hints to query blocks in views, making the hints defined in the query effective in the view. This feature provides a way to inject hints into complex SQL statements that contain nested views, enhances the execution plan control, and stabilizes the performance of complex statements. To use global hints, you need to [name the query blocks](https://docs.pingcap.com/tidb/stable/optimizer-hints#step-1-define-the-query-block-name-of-the-view-using-the-qb_name-hint) and [specify hint references](https://docs.pingcap.com/tidb/stable/optimizer-hints#step-2-add-the-target-hints).

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/optimizer-hints#hints-that-take-effect-globally).

* Support pushing down sorting operations of [partitioned tables](https://docs.pingcap.com/tidb/stable/partitioned-table) to TiKV [#26166](https://github.com/pingcap/tidb/issues/26166) @[winoros](https://github.com/winoros)

    Although the [partitioned table](https://docs.pingcap.com/tidb/stable/partitioned-table) feature has been GA since v6.1.0, TiDB is continually improving its performance. In v6.5.0, TiDB supports pushing down sorting operations such as `ORDER BY` and `LIMIT` to TiKV for computation and filtering, which reduces network I/O overhead and improves SQL performance when you use partitioned tables.

* Optimizer introduces a more accurate Cost Model Version 2 (GA) [#35240](https://github.com/pingcap/tidb/issues/35240) @[qw4990](https://github.com/qw4990)

    TiDB v6.2.0 introduces the [Cost Model Version 2](https://docs.pingcap.com/tidb/stable/cost-model#cost-model-version-2) as an experimental feature. This model uses a more accurate cost estimation method to help the optimizer choose the optimal execution plan. Especially when TiFlash is deployed, Cost Model Version 2 automatically helps choose the appropriate storage engine and avoids much manual intervention. After real-scene testing for a period of time, this model becomes GA in v6.5.0. Starting from v6.5.0, newly created clusters use Cost Model Version 2 by default. For clusters upgrade to v6.5.0, because Cost Model Version 2 might cause changes to query plans, you can set the [`tidb_cost_model_version = 2`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_cost_model_version-new-in-v620) variable to use the new cost model after sufficient performance testing.

    Cost Model Version 2 becomes a generally available feature that significantly improves the overall capability of the TiDB optimizer and helps TiDB evolve towards a more powerful HTAP database.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/cost-model#cost-model-version-2).

* TiFlash optimizes the operations of getting the number of table rows [#37165](https://github.com/pingcap/tidb/issues/37165) @[elsa0520](https://github.com/elsa0520)

    In the scenarios of data analysis, It is a common operation to get the actual number of rows of a table through `COUNT(*)` without filter conditions. In v6.5.0, TiFlash optimizes the rewriting of `COUNT(*)` and automatically selects the not-null columns with the shortest column definition to count the number of rows, which can effectively reduce the number of I/O operations in TiFlash and improve the execution efficiency of getting row counts.
