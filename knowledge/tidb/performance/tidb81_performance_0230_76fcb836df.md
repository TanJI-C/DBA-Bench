# pipelined dml batch processing

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.5-performance-highlights.md`
- Source Title: `TiDB Cloud Performance Highlights for TiDB v8.5.0`
- Source Heading Path: `TiDB Cloud Performance Highlights for TiDB v8.5.0 > Batch processing | TiDB Cloud Performance Highlights for TiDB v8.5.0 > Batch processing > Challenge | TiDB Cloud Performance Highlights for TiDB v8.5.0 > Batch processing > Solution | TiDB Cloud Performance Highlights for TiDB v8.5.0 > Batch processing > Test environment | TiDB Cloud Performance Highlights for TiDB v8.5.0 > Batch processing > Test results`
- Source Line Ranges: `163-202`
- Source Scope: `cloud`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `batch processing`, `dml`, `memory usage`, `oom`, `pipelined dml`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0230_76fcb836df`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.5-performance-highlights.md#batch-processing`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0c5071f5198ee8a1382bd80385f822023685ab328a6c7483f4b5dee6fe5a5431`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.5-performance-highlights#batch-processing
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.5-performance-highlights.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving batch processing performance details for large transactions and the impact of Pipelined DML on execution speed and memory usage.
- Retrieval Keywords: Batch processing, Pipelined DML, tidb_dml_type, large-scale transactions, bulk data updates, system migrations, ETL workflows, Out of Memory (OOM), red-black trees, O(N log N), INSERT, UPDATE, DELETE, execution speed increases by 2x, maximum TiDB memory usage decreases by 50%, TiKV write flow becomes much smoother
- Follow-up Guidance: The chunk includes YCSB 10 million row test results comparing Standard DML and Pipelined DML for latency and TiDB memory usage peak across insert, update, and delete workloads.
- Classification Note: This is classified as TiDB performance content because it focuses on the Pipelined DML feature, transaction memory behavior, and DML workload benchmarks.

## Official Source Content

## Batch processing
### Challenge

Large-scale transactions, such as bulk data updates, system migrations, and ETL workflows, involve processing millions of rows and are vital for supporting critical operations. While TiDB excels as a distributed SQL database, handling such transactions at scale presents two significant challenges:

- Memory limits: in versions earlier than TiDB v8.1.0, all transaction mutations are held in memory throughout the transaction lifecycle, which strains resources and reduces performance. For operations involving millions of rows, this could lead to excessive memory usage and, in some cases, Out of Memory (OOM) errors when resources are insufficient.

- Performance slowdowns: managing large in-memory buffers relies on red-black trees, which introduces computational overhead. As buffers grow, their operations slow down due to the *O(N log N)* complexity inherent in these data structures.
### Solution

These challenges highlight a clear opportunity to improve scalability, reduce complexity, and enhance reliability. With the rise of modern data workloads, TiDB introduces the [Pipelined DML](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_type-new-in-v800) feature, designed to optimize the handling of large transactions, and improve resource utilization and overall performance.
### Test environment

- Cluster topology: TiDB (16 vCPU, 32 GiB) \* 1 + TiKV (16 vCPU, 32 GiB) \* 3
- Dataset: YCSB non-clustered table with 10 million rows (about 10 GiB of data). Primary keys are selectively removed in certain tests to isolate and evaluate the impact of hotspot patterns.
- Workload: DML operations including `INSERT`, `UPDATE`, and `DELETE`.
### Test results

The execution speed increases by 2x, the maximum TiDB memory usage decreases by 50%, and the TiKV write flow becomes much smoother.

- Latency (in seconds)

    | Workload (10 GiB) | Standard DML | Pipelined DML | Improvement |
    | --- |  --- |  --- |  --- |
    | YCSB-insert-10M | 368 | 159 | 131.45% |
    | YCSB-update-10M | 255 | 131 | 94.66% |
    | YCSB-delete-10M | 136 | 42 | 223.81% |

- TiDB memory usage peak (GiB)

    | Workload (10 GiB) | Standard DML | Pipelined DML | Reduction |
    | --- |  --- |  --- |  --- |
    | YCSB-insert-10M | 25.8 | 12 | 53.49% |
    | YCSB-update-10M | 23.1 | 12.9 | 44.16% |
    | YCSB-delete-10M | 10.1 | 8.08 | 20.00% |
