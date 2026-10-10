# Sysbench benchmark results across OLTP workloads

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v6.1.0-vs-v6.0.0.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v6.1.0 vs. v6.0.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v6.1.0 vs. v6.0.0 > Test results | TiDB Sysbench Performance Test Report -- v6.1.0 vs. v6.0.0 > Test results > Point Select performance | TiDB Sysbench Performance Test Report -- v6.1.0 vs. v6.0.0 > Test results > Update Non-index performance | TiDB Sysbench Performance Test Report -- v6.1.0 vs. v6.0.0 > Test results > Update Index performance | TiDB Sysbench Performance Test Report -- v6.1.0 vs. v6.0.0 > Test results > Read Write performance`
- Source Line Ranges: `151-199`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `ecosystem`
- Topic Tags: `sysbench`, `benchmark-results`, `tps`, `latency`, `point-select`, `update-non-index`, `update-index`, `read-write`, `oltp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0026_ef644fd827`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v6.1.0-vs-v6.0.0.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a0ef79bfbe7b8d658a2a4ebd50f07522ae2add54501153a9b7ae435f98ebb6d8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v6.1.0-vs-v6.0.0#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v6.1.0-vs-v6.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the Sysbench OLTP benchmark results comparing TiDB v6.1.0 and v6.0.0 across Point Select, Update Non-index, Update Index, and Read Write workloads.
- Retrieval Keywords: Test results, Point Select performance, Update Non-index performance, Update Index performance, Read Write performance, v6.0.0 TPS, v6.1.0 TPS, 95% latency, TPS improvement (%), Compared with v6.0.0, the Point Select performance of v6.1.0 slightly drops by 2.1%, Compared with v6.0.0, the Update Non-index performance of v6.1.0 is improved by 3.88%, Compared with v6.0.0, the Update Index performance of v6.1.0 is improved by 4.61%, Compared with v6.0.0, the Read Write performance of v6.1.0 is improved by 2.23%
- Follow-up Guidance: The source summarizes that v6.1.0 improves write-heavy workload performance by 2.33% to 4.61%.
- Classification Note: This chunk is classified as performance because it reports TPS and 95% latency benchmark outcomes for multiple OLTP workloads and compares the two TiDB versions.

## Official Source Content

## Test results
### Point Select performance

| Threads   | v6.0.0 TPS | v6.1.0 TPS  | v6.0.0 95% latency (ms) | v6.1.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|268934.84|265353.15|1.89|1.96|-1.33|
|600|365217.96|358976.94|2.57|2.66|-1.71|
|900|420799.64|407625.11|3.68|3.82|-3.13|

Compared with v6.0.0, the Point Select performance of v6.1.0 slightly drops by 2.1%.

![Point Select](/media/sysbench_v600vsv610_point_select.png)
### Update Non-index performance

| Threads   | v6.0.0 TPS | v6.1.0 TPS  | v6.0.0 95% latency (ms) | v6.1.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|41778.95|42991.9|11.24|11.45|2.90 |
|600|52045.39|54099.58|20.74|20.37|3.95|
|900|59243.35|62084.65|27.66|26.68|4.80|

Compared with v6.0.0, the Update Non-index performance of v6.1.0 is improved by 3.88%.

![Update Non-index](/media/sysbench_v600vsv610_update_non_index.png)
### Update Index performance

| Threads   | v6.0.0 TPS | v6.1.0 TPS  | v6.0.0 95% latency (ms) | v6.1.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|18085.79|19198.89|25.28|23.95|6.15|
|600|22210.8|22877.58|42.61|41.85|3.00|
|900|25249.81|26431.12|55.82|53.85|4.68|

Compared with v6.0.0, the Update Index performance of v6.1.0 is improved by 4.61%.

![Update Index](/media/sysbench_v600vsv610_update_index.png)
### Read Write performance

| Threads   | v6.0.0 TPS  | v6.1.0 TPS | v6.0.0 95% latency (ms) | v6.1.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|4856.23|4914.11|84.47|82.96|1.19|
|600|5676.46|5848.09|161.51|150.29|3.02|
|900|6072.97|6223.95|240.02|223.34|2.49|

Compared with v6.0.0, the Read Write performance of v6.1.0 is improved by 2.23%.

![Read Write](/media/sysbench_v600vsv610_read_write.png)
