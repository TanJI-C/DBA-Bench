# Compatibility changes for system variables in v6.2.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.2.0.md`
- Source Title: `TiDB 6.2.0 Release Notes`
- Source Heading Path: `TiDB 6.2.0 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `248-266`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `tikv`
- Topic Tags: `system-variables`, `compatibility-changes`, `cost-model`, `concurrent-ddl`, `analyze`, `execution-plan`, `optimizer`, `paging`, `transaction-commit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0328_f6e041f13d`
- Source ID: `tidb-docs-8.1:releases/release-6.2.0.md#system-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f47db6866b0548afe6d1372811dea25db32a31dc439d3eeeea1bf61018639b73`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.2.0#system-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiDB 6.2.0 system variable compatibility changes, including newly added, deleted, or modified variables and their meanings.
- Retrieval Keywords: TiDB 6.2.0 system variables, compatibility changes, tidb_enable_new_cost_interface, tidb_cost_model_version, Cost Model Version 2, tidb_enable_concurrent_ddl, DO NOT modify this variable, tiflash_fine_grained_shuffle_stream_count, tiflash_fine_grained_shuffle_batch_size, tidb_default_string_match_selectivity, like rlike regexp, tidb_enable_analyze_snapshot, ANALYZE historical data latest data, tidb_generate_binary_plan, binary-encoded execution plans, slow logs and statement summaries, tidb_opt_skew_distinct_agg, COUNT(DISTINCT a), two-level aggregate functions, tidb_enable_noop_variables, SHOW GLOBAL VARIABLES, tidb_min_paging_size, coprocessor paging request, tidb_txn_commit_batch_size, transaction commit requests, TiKV, tidb_enable_change_multi_schema deleted, ALTER TABLE statement by default, tidb_enable_outer_join_reorder, Outer Join, default value OFF in v6.2.0
- Follow-up Guidance: The chunk also states that tidb_enable_change_multi_schema is deleted in v6.2.0 and that tidb_enable_outer_join_reorder changes its default value from ON in v6.1.0 to OFF in v6.2.0.
- Classification Note: This is a release-note compatibility summary for TiDB system variables in v6.2.0, covering added variables plus deleted and modified behavior.

## Official Source Content

### System variables

| Variable name | Change type | Description |
| --- | --- | --- |
| [tidb_enable_new_cost_interface](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_new_cost_interface-new-in-v620) | Newly added | This variable controls whether to enable the [refactored Cost Model implementation](https://docs.pingcap.com/tidb/stable/cost-model#cost-model-version-2). |
| [tidb_cost_model_version](https://docs.pingcap.com/tidb/stable/system-variables#tidb_cost_model_version-new-in-v620) | Newly added | TiDB uses a cost model to choose an index and operator during physical optimization. This variable is used to select the cost model version. TiDB v6.2.0 introduces the Cost Model Version 2, which is more accurate than the previous version in internal tests. |
| tidb_enable_concurrent_ddl | Newly added | This variable controls whether to allow TiDB to use concurrent DDL statements. DO NOT modify this variable. The risk of disabling this variable is unknown and might corrupt the metadata of the cluster. |
| [tiflash_fine_grained_shuffle_stream_count](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_fine_grained_shuffle_stream_count-new-in-v620) | Newly added | This variable controls the concurrency level of the window function execution When the window function is pushed down to TiFlash for execution. |
| [tiflash_fine_grained_shuffle_batch_size](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_fine_grained_shuffle_batch_size-new-in-v620) | Newly added | When Fine Grained Shuffle is enabled, the window function pushed down to TiFlash can be executed in parallel. This variable controls the batch size of the data sent by the sender. The sender will send data once the cumulative number of rows exceeds this value. |
| [tidb_default_string_match_selectivity](https://docs.pingcap.com/tidb/stable/system-variables#tidb_default_string_match_selectivity-new-in-v620) | Newly added | This variable is used to set the default selectivity of `like`, `rlike`, and `regexp` functions in the filter condition when estimating the number of rows. This variable also controls whether to enable TopN to help estimate these functions. |
| [tidb_enable_analyze_snapshot](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_analyze_snapshot-new-in-v620) | Newly added | This variable controls whether to read historical data or the latest data when performing `ANALYZE`. |
| [tidb_generate_binary_plan](https://docs.pingcap.com/tidb/stable/system-variables#tidb_generate_binary_plan-new-in-v620) | Newly added | This variable controls whether to generate binary-encoded execution plans in slow logs and statement summaries. |
| [tidb_opt_skew_distinct_agg](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_skew_distinct_agg-new-in-v620) | Newly added | This variable sets whether the optimizer rewrites the aggregate functions with `DISTINCT` to the two-level aggregate functions, such as rewriting `SELECT b, COUNT(DISTINCT a) FROM t GROUP BY b` to `SELECT b, COUNT(a) FROM (SELECT b, a FROM t GROUP BY b, a) t GROUP BY b`. |
| [tidb_enable_noop_variables](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_noop_variables-new-in-v620) | Newly added | This variable controls whether to show `noop` variables in the result of `SHOW [GLOBAL] VARIABLES`. |
| [tidb_min_paging_size](https://docs.pingcap.com/tidb/stable/system-variables#tidb_min_paging_size-new-in-v620) | Newly added | This variable is used to set the maximum number of rows during the coprocessor paging request process. |
| [tidb_txn_commit_batch_size](https://docs.pingcap.com/tidb/stable/system-variables#tidb_txn_commit_batch_size-new-in-v620) | Newly added | This variable is used to control the batch size of transaction commit requests that TiDB sends to TiKV. |
| tidb_enable_change_multi_schema | Deleted | This variable is deleted because, starting from v6.2.0, you can alter multiple columns or indexes in one `ALTER TABLE` statement by default. |
| [tidb_enable_outer_join_reorder](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_outer_join_reorder-new-in-v610) | Modified | This variable controls whether the Join Reorder algorithm of TiDB supports Outer Join. In v6.1.0, the default value is `ON`, which means the Join Reorder's support for Outer Join is enabled by default. From v6.2.0, the default value is `OFF`, which means the support is disabled by default. |
