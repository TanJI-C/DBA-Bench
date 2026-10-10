# ANALYZE memory quota guidance

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Improve collection performance > The memory quota for collecting statistics`
- Source Line Ranges: `253-269`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `analyze`, `memory-quota`, `statistics-collection`, `experimental-feature`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0186_c1b660ff3e`
- Source ID: `tidb-docs-8.1:statistics.md#the-memory-quota-for-collecting-statistics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `580b8bb55aa3a7e5b13b52a67e9ec48fd5875604dd2b7c8af623fd7c01e1b440`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#the-memory-quota-for-collecting-statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when asking how `tidb_mem_quota_analyze` controls memory quota for collecting statistics and what sizing considerations or example memory usage are given for `ANALYZE`.
- Retrieval Keywords: tidb_mem_quota_analyze, ANALYZE memory quota, memory quota for collecting statistics, experimental feature, default sampling rate, 20 columns 800 MiB, 160 columns 5 GiB, available memory when TiDB is not collecting statistics
- Follow-up Guidance: It also states that the `ANALYZE` memory quota is an experimental feature and memory statistics might be inaccurate in production environments.
- Classification Note: This is classified as performance because the content discusses memory quota sizing and memory usage during statistics collection.

## Official Source Content

### The memory quota for collecting statistics

> **Warning:**
>
> Currently, the `ANALYZE` memory quota is an experimental feature, and the memory statistics might be inaccurate in production environments.

Since TiDB v6.1.0, you can use the system variable [`tidb_mem_quota_analyze`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_analyze-new-in-v610) to control the memory quota for collecting statistics in TiDB.

To set a proper value of `tidb_mem_quota_analyze`, consider the data size of the cluster. When the default sampling rate is used, the main considerations are the number of columns, the size of column values, and the memory configuration of TiDB. Consider the following suggestions when you configure the maximum and minimum values:

> **Note:**
>
> The following suggestions are for reference only. You need to configure the values based on the real scenario.

- Minimum value: should be greater than the maximum memory usage when TiDB collects statistics from the table with the most columns. An approximate reference: when TiDB collects statistics from a table with 20 columns using the default configuration, the maximum memory usage is about 800 MiB; when TiDB collects statistics from a table with 160 columns using the default configuration, the maximum memory usage is about 5 GiB.
- Maximum value: should be less than the available memory when TiDB is not collecting statistics.
