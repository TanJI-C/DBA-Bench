# Compatibility changes and system variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.0.md`
- Source Title: `TiDB 7.5.0 Release Notes`
- Source Heading Path: `TiDB 7.5.0 Release Notes > Compatibility changes | TiDB 7.5.0 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `151-169`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `compatibility`, `upgrade`, `system variables`, `deprecated`, `analyze`, `statistics`, `gogc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0142_e85aa7c412`
- Source ID: `tidb-docs-8.1:releases/release-7.5.0.md#compatibility-changes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `762cbac903c941d1cb9082655f347fe45a22ddb472efd9071f30bbd1ebff3201`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.0#compatibility-changes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.0 compatibility changes to system variables related to analyze, statistics concurrency, async global stats merge, or GOGC tuner limits during upgrade review.
- Retrieval Keywords: Compatibility changes, System variables, tidb_enable_fast_analyze, deprecated Fast Analyze, tidb_analyze_partition_concurrency, tidb_build_stats_concurrency, tidb_merge_partition_stats_concurrency, tidb_build_sampling_stats_concurrency, ANALYZE process, tidb_enable_async_merge_global_stats, avoid OOM issues, tidb_gogc_tuner_max_value, tidb_gogc_tuner_min_value
- Follow-up Guidance: The source notes that this compatibility section is for upgrades from v7.4.0 to v7.5.0 and that upgrades from v7.3.0 or earlier might also need intermediate-version compatibility changes.
- Classification Note: The chunk is classified as configuration because it lists system variable deprecations, default-value changes, and newly added variables in the compatibility section.

## Official Source Content

## Compatibility changes

> **Note:**
>
> This section provides compatibility changes you need to know when you upgrade from v7.4.0 to the current version (v7.5.0). If you are upgrading from v7.3.0 or earlier versions to the current version, you might also need to check the compatibility changes introduced in intermediate versions.
### System variables

| Variable name  | Change type    |  Description |
|--------|------------------------------|------|
| [`tidb_enable_fast_analyze`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_fast_analyze) | Deprecated | Controls whether to enable the statistics `Fast Analyze` feature. This feature is deprecated in v7.5.0. |
| [`tidb_analyze_partition_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_analyze_partition_concurrency) |  Modified | Changes the default value from `1` to `2` after further tests. |
| [`tidb_build_stats_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_build_stats_concurrency) | Modified | Changes the default value from `4` to `2` after further tests. |
| [`tidb_merge_partition_stats_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_merge_partition_stats_concurrency)    |  Modified | This system variable takes effect starting from v7.5.0. It specifies the concurrency of merging statistics for a partitioned table when TiDB analyzes the partitioned table. |
| [`tidb_build_sampling_stats_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_build_sampling_stats_concurrency-new-in-v750) | Newly added | Controls the sampling concurrency of the `ANALYZE` process. |
| [`tidb_enable_async_merge_global_stats`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_async_merge_global_stats-new-in-v750) | Newly added | This variable is used by TiDB to merge statistics asynchronously to avoid OOM issues. |
| [`tidb_gogc_tuner_max_value`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gogc_tuner_max_value-new-in-v750) | Newly added | Controls the maximum value of GOGC that the GOGC Tuner can adjust. |
| [`tidb_gogc_tuner_min_value`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gogc_tuner_min_value-new-in-v750) | Newly added | Controls the minimum value of GOGC that the GOGC Tuner can adjust.|
