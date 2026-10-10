# Sysbench comparative performance results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v5.1.0-vs-v5.0.2.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test results | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test results > Point Select performance | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test results > Update Non-index performance | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test results > Update Index performance | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test results > Read Write performance`
- Source Line Ranges: `126-186`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `sysbench`, `benchmark-results`, `qps`, `latency`, `point-select`, `update-non-index`, `update-index`, `read-write`, `version-comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0012_8148b0403d`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v5.1.0-vs-v5.0.2.md#test-results`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e0c4c74914e98028064375f8ab1891cb6cd6c702f4f256ee2b69dcfa4cf019a3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v5.1.0-vs-v5.0.2#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v5.1.0-vs-v5.0.2.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the measured Sysbench comparison results between TiDB v5.1.0 and v5.0.2, including QPS improvement and 95% latency for Point Select, Update Non-index, Update Index, and Read Write workloads.
- Retrieval Keywords: Sysbench comparative performance results, Test results, Point Select performance, Update Non-index performance, Update Index performance, Read Write performance, QPS improvement, 95% latency, v5.0.2 QPS, v5.1.0 QPS, Compared with v5.0.2, the Point Select performance of v5.1.0 is improved by 19.4%, Compared with v5.0.2, the Update Non-index performance of v5.1.0 is reduced by 0.8%, Compared with v5.0.2, the Update Index performance of v5.1.0 is reduced by 1.8%, Compared with v5.0.2, the Read Write performance of v5.1.0 is reduced by 2.7%, 150 threads, 300 threads, 600 threads, 900 threads, 1200 threads, 1500 threads
- Follow-up Guidance: The same document also contains the benchmark environment, parameter configuration, and Sysbench commands used to produce these results.
- Classification Note: This chunk is classified as performance because it reports workload throughput and latency measurements across multiple concurrency levels for a version-to-version Sysbench comparison.

## Official Source Content

## Test results
### Point Select performance

| Threads   | v5.0.2 QPS   | v5.0.2 95% latency (ms)   | v5.1.0 QPS   | v5.1.0 95% latency (ms)   | QPS improvement   |
|:----------|:----------|:----------|:----------|:----------|:----------|
|150|137732.27|1.86|158861.67|2|15.34%|
|300|201420.58|2.91|238038.44|2.71|18.18%|
|600|303631.52|3.49|428573.21|2.07|41.15%|
|900|383628.13|3.55|464863.22|3.89|21.18%|
|1200|391451.54|5.28|413656.74|13.46|5.67%|
|1500|410276.93|7.43|471418.78|10.65|14.90%|

Compared with v5.0.2, the Point Select performance of v5.1.0 is improved by 19.4%.

![Point Select](/media/sysbench_v510vsv502_point_select.png)
### Update Non-index performance

| Threads   | v5.0.2 QPS   | v5.0.2 95% latency (ms)   | v5.1.0 QPS   | v5.1.0 95% latency (ms)   | QPS improvement   |
|:----------|:----------|:----------|:----------|:----------|:----------|
|150|29248.2|7.17|29362.7|8.13|0.39%|
|300|40316.09|12.52|39651.52|13.7|-1.65%|
|600|51011.11|22.28|47047.9|27.66|-7.77%|
|900|58814.16|27.66|59331.84|28.67|0.88%|
|1200|65286.52|32.53|67745.39|31.37|3.77%|
|1500|68300.86|39.65|67899.17|44.17|-0.59%|

Compared with v5.0.2, the Update Non-index performance of v5.1.0 is reduced by 0.8%.

![Update Non-index](/media/sysbench_v510vsv502_update_non_index.png)
### Update Index performance

| Threads   | v5.0.2 QPS   | v5.0.2 95% latency (ms)   | v5.1.0 QPS   | v5.1.0 95% latency (ms)   | QPS improvement   |
|:----------|:----------|:----------|:----------|:----------|:----------|
|150|15066.54|14.73|14829.31|14.73|-1.57%|
|300|18535.92|24.83|17401.01|29.72|-6.12%|
|600|22862.73|41.1|21923.78|44.98|-4.11%|
|900|25286.74|57.87|24916.76|58.92|-1.46%|
|1200|27566.18|70.55|27800.62|69.29|0.85%|
|1500|28184.76|92.42|28679.72|86|1.76%|

Compared with v5.0.2, the Update Index performance of v5.1.0 is reduced by 1.8%.

![Update Index](/media/sysbench_v510vsv502_update_index.png)
### Read Write performance

| Threads   | v5.0.2 QPS   | v5.0.2 95% latency (ms)   | v5.1.0 QPS   | v5.1.0 95% latency (ms)   | QPS improvement   |
|:----------|:----------|:----------|:----------|:----------|:----------|
|150|66415.33|56.84|66591.49|57.87|0.27%|
|300|82488.39|97.55|81226.41|101.13|-1.53%|
|600|99195.36|173.58|97357.86|179.94|-1.85%|
|900|107382.76|253.35|101665.95|267.41|-5.32%|
|1200|112389.23|337.94|107426.41|350.33|-4.42%|
|1500|113548.73|450.77|109805.26|442.73|-3.30%|

Compared with v5.0.2, the Read Write performance of v5.1.0 is reduced by 2.7%.

![Read Write](/media/sysbench_v510vsv502_read_write.png)
