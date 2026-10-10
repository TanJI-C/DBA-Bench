# Sysbench benchmark results by workload

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v6.0.0-vs-v5.4.0.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test results | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test results > Point Select performance | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test results > Update Non-index performance | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test results > Update Index performance | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test results > Read Write performance`
- Source Line Ranges: `151-199`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `test-results`, `point-select`, `update-non-index`, `update-index`, `read-write`, `tps`, `latency`, `performance-comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0023_6bbe452aa3`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v6.0.0-vs-v5.4.0.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e4b2073dd1d5ae7500b2e24fa895ee30dfb3893f29963e2f2c187831791cd777`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v6.0.0-vs-v5.4.0#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v6.0.0-vs-v5.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching for workload-specific Sysbench results, including TPS, 95% latency, thread counts, and the reported performance differences between TiDB v6.0.0 and v5.4.0.
- Retrieval Keywords: Test results, Point Select performance, Update Non-index performance, Update Index performance, Read Write performance, v5.4.0 TPS, v6.0.0 TPS, 95% latency (ms), TPS improvement (%), 300 threads, 600 threads, 900 threads, Point Select performance of v6.0.0 is slightly dropped by 1.79%, Update Non-index performance of v6.0.0 is slightly dropped by 1.98%, Update Index performance of v6.0.0 is dropped by 3.05%, Read Write performance of v6.0.0 is significantly improved by 16.17%
- Follow-up Guidance: 
- Classification Note: This is classified as performance content because it contains the measured benchmark outcomes by workload, including TPS, latency, and percentage improvement.

## Official Source Content

## Test results
### Point Select performance

| Threads   | v5.4.0 TPS | v6.0.0 TPS  | v5.4.0 95% latency (ms) | v6.0.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|260085.19|265207.73|1.82|1.93|1.97|
|600|378098.48|365173.66|2.48|2.61|-3.42|
|900|441294.61|424031.23|3.75|3.49|-3.91|

Compared with v5.4.0, the Point Select performance of v6.0.0 is slightly dropped by 1.79%.

![Point Select](/media/sysbench_v540vsv600_point_select.png)
### Update Non-index performance

| Threads   | v5.4.0 TPS | v6.0.0 TPS  | v5.4.0 95% latency (ms) | v6.0.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|41528.7|40814.23|11.65|11.45|-1.72|
|600|53220.96|51746.21|19.29|20.74|-2.77|
|900|59977.58|59095.34|26.68|28.16|-1.47|

Compared with v5.4.0, the Update Non-index performance of v6.0.0 is slightly dropped by 1.98%.

![Update Non-index](/media/sysbench_v540vsv600_update_non_index.png)
### Update Index performance

| Threads   | v5.4.0 TPS | v6.0.0 TPS  | v5.4.0 95% latency (ms) | v6.0.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|18659.11|18187.54|23.95|25.74|-2.53|
|600|23195.83|22270.81|40.37|44.17|-3.99|
|900|25798.31|25118.78|56.84|57.87|-2.63|

Compared with v5.4.0, the Update Index performance of v6.0.0 is dropped by 3.05%.

![Update Index](/media/sysbench_v540vsv600_update_index.png)
### Read Write performance

| Threads   | v5.4.0 TPS  | v6.0.0 TPS | v5.4.0 95% latency (ms) | v6.0.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|4141.72|4829.01|97.55|82.96|16.59|
|600|4892.76|5693.12|173.58|153.02|16.36|
|900|5217.94|6029.95|257.95|235.74|15.56|

Compared with v5.4.0, the Read Write performance of v6.0.0 is significantly improved by 16.17%.

![Read Write](/media/sysbench_v540vsv600_read_write.png)
