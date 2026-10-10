# Improve data loading speed in TiDB

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/migration-tidb-faq.md`
- Source Title: `Migration FAQs`
- Source Heading Path: `Migration FAQs > Migrate the traffic > How to improve the data loading speed in TiDB?`
- Source Line Ranges: `182-185`
- Source Scope: `all`
- Primary Component: `lightning`
- Related Components: `tidb`, `tikv`
- Topic Tags: `data-loading`, `bulk-import`, `acid`, `metrics`, `disk-usage`, `bottlenecks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0116_b8e9352448`
- Source ID: `tidb-docs-8.1:faq/migration-tidb-faq.md#how-to-improve-the-data-loading-speed-in-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d14e56e849e0bac7322c1d25812ee6e0a7055ef74f2791cf611f850c20514518`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/migration-tidb-faq#how-to-improve-the-data-loading-speed-in-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/migration-tidb-faq.md

## Retrieval Guidance

- Use When: Use this when asking how to improve TiDB data loading speed, what TiDB Lightning is used for in distributed import, or which metrics help analyze import bottlenecks.
- Retrieval Keywords: How to improve the data loading speed in TiDB, TiDB Lightning, distributed data import, ACID constraint, new table, new index, full backup and restoring, truncate the original table and then import data, disk usage rate of the host, TiClient Error, Backoff, Thread CPU, analyze the bottlenecks
- Follow-up Guidance: The content notes that ACID of imported data is guaranteed only after the entire import process ends, and suggests paying attention to disk usage rate of the host, TiClient Error, Backoff, and Thread CPU during loading.
- Classification Note: This is classified as performance for Lightning because the content explains bulk import speed considerations, import scenario constraints, and metrics used to analyze data loading bottlenecks.

## Official Source Content

### How to improve the data loading speed in TiDB?

- The [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) tool is developed for distributed data import. It should be noted that the data import process does not perform a complete transaction process for performance reasons. Therefore, the ACID constraint of the data being imported during the import process cannot be guaranteed. The ACID constraint of the imported data can only be guaranteed after the entire import process ends. Therefore, the applicable scenarios mainly include importing new data (such as a new table or a new index) or the full backup and restoring (truncate the original table and then import data).
- Data loading in TiDB is related to the status of disks and the whole cluster. When loading data, pay attention to metrics like the disk usage rate of the host, TiClient Error, Backoff, Thread CPU and so on. You can analyze the bottlenecks using these metrics.
