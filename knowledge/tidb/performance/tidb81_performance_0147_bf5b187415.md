# TiFlash stability and other performance optimizations

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0-rc.md`
- Source Title: `TiDB 5.0 RC Release Notes`
- Source Heading Path: `TiDB 5.0 RC Release Notes > Performance improvements > Improve the stability of TiFlash in Real-time BI / Data Warehousing scenarios | TiDB 5.0 RC Release Notes > Performance improvements > Other performance optimizations`
- Source Line Ranges: `133-143`
- Source Scope: `all`
- Primary Component: `tiflash`
- Related Components: `tidb`
- Topic Tags: `performance`, `stability`, `oom`, `memory`, `io`, `coprocessor`, `concurrency`, `delete`, `local-disks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0147_bf5b187415`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0-rc.md#improve-the-stability-of-tiflash-in-real-time-bi-data-warehousing-scenarios`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `62b562ddfa9282e3d3eb89922124ce40662bfe278c805dddb516e1954dbcea78`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0-rc#improve-the-stability-of-tiflash-in-real-time-bi-data-warehousing-scenarios
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0-rc.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiFlash stability or performance changes involving OOM prevention, memory usage limits, background I/O write traffic, coprocessor task queuing, DELETE performance, or multiple local disks.
- Retrieval Keywords: TiFlash stability, Real-time BI, Data Warehousing, DeltaIndex memory usage, system out of memory OOM, background data sorting task, I/O write traffic, foreground tasks, new thread pools, queue coprocessor tasks, high concurrency, delete from table where id <?, P99 performance improves by four times, multiple local disks, concurrently reading and writing data
- Follow-up Guidance: The source also notes that `delete from table where id <?` execution performance improved and that TiFlash supports concurrent read and write on multiple local disks.
- Classification Note: This is classified as performance because the content describes stability and execution improvements for TiFlash and SQL performance optimizations.

## Official Source Content

### Improve the stability of TiFlash in Real-time BI / Data Warehousing scenarios

+ Limit the memory usage of DeltaIndex to avoid system out of memory (OOM) caused by excessive memory usage in the scenarios of huge data volume.
+ Limit the I/O write traffic used by the background data sorting task to reduce the impact on the foreground tasks.
+ Add new thread pools to queue coprocessor tasks, which avoids system OOM caused by excessive memory usage when processing coprocessors in high concurrency.
### Other performance optimizations

+ Improve the execution performance of `delete from table where id <?` statement. Its P99 performance improves by four times. [#18028](https://github.com/pingcap/tidb/issues/18028)
+ TiFlash supports concurrently reading and writing data in multiple local disks to improve performance.
