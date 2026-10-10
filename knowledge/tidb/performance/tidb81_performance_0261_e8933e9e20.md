# Set TiFlash execution concurrency

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Set a greater execution concurrency`
- Source Line Ranges: `297-310`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `concurrency`, `threads`, `system-variable`, `query-performance`, `cpu`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0261_e8933e9e20`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#set-a-greater-execution-concurrency`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a521e4429d729a3ab68a057919dfc9292b7eedcb0ce4f9e083a005e61528aed5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#set-a-greater-execution-concurrency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to set TiFlash execution concurrency with the tidb_max_tiflash_threads system variable and the documented thread-count example.
- Retrieval Keywords: tidb_max_tiflash_threads, Set a greater execution concurrency, maximum concurrency for TiFlash to execute a request, threads, set @@tidb_max_tiflash_threads = 20, single TiFlash instance is 8 threads, 3 TiFlash instances, 20 × 3, 60 threads, query performance, CPU resources
- Follow-up Guidance: The official example states that changing tidb_max_tiflash_threads from 8 to 20 raises total request execution threads across 3 TiFlash instances from 24 to 60.
- Classification Note: This is classified as performance content because the official content explains a TiDB system variable that increases TiFlash execution concurrency to improve query performance.

## Official Source Content

### Set a greater execution concurrency

A greater execution concurrency allows TiFlash to occupy more CPU resources of the system, thereby improving query performance.

The [`tidb_max_tiflash_threads`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_tiflash_threads-new-in-v610) variable is used to set the maximum concurrency for TiFlash to execute a request. The unit is threads.

```sql
set @@tidb_max_tiflash_threads = 20;
```

The following example shows the query result before and after `tidb_max_tiflash_threads` is re-configured. Before `tidb_max_tiflash_threads` is set, the concurrency of request execution for a single TiFlash instance is 8 threads. Since the cluster has a total of 3 TiFlash instances, the total number of threads for request execution on all TiFlash instances is 24 (8 × 3). After `tidb_max_tiflash_threads` is set to `20`, the total number of threads for request execution on all TiFlash instances is 60 (20 × 3).

Before `tidb_max_tiflash_threads` is re-configured:
