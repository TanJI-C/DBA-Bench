# Sysbench benchmark results for point select, update, and read write workloads

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v5.2.0-vs-v5.1.1.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test results | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test results > Point Select performance | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test results > Update Non-index performance | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test results > Update Index performance | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test results > Read Write performance`
- Source Line Ranges: `126-186`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`
- Topic Tags: `sysbench`, `benchmark-results`, `qps`, `latency`, `point-select`, `update-non-index`, `update-index`, `read-write`, `workload-comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0014_4e7fcfbffb`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v5.2.0-vs-v5.1.1.md#test-results`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `63ce33d3d1facd0bcf9ab94cab94832d5229ba96cdd9f196594dfc7a3c1cd60a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v5.2.0-vs-v5.1.1#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v5.2.0-vs-v5.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the Sysbench test results comparing v5.2.0 and v5.1.1 for point_select, update_non_index, update_index, or read_write, including QPS, 95% latency, and reported percentage change by thread count.
- Retrieval Keywords: Sysbench test results, Point Select performance, Update Non-index performance, Update Index performance, Read Write performance, QPS improvement, 95% latency (ms), threads 150 300 600 900 1200 1500, Compared with v5.1.1, the Point Select performance of v5.2.0 is improved by 11.03%, Update Non-index performance of v5.2.0 is reduced by 1.98%, sysbench_v511vsv520_point_select.png, sysbench_v511vsv520_update_non_index.png, sysbench_v511vsv520_update_index.png, sysbench_v511vsv520_read_write.png
- Follow-up Guidance: The source includes the benchmark setup, configuration, and Sysbench commands used to produce these result tables.
- Classification Note: This chunk is classified as performance because it reports workload throughput and latency measurements for multiple Sysbench OLTP scenarios across TiDB versions.

## Official Source Content

## Test results
### Point Select performance

| Threads   | v5.1.1 QPS   | v5.1.1 95% latency (ms)   | v5.2.0 QPS   | v5.2.0 95% latency (ms)   | QPS improvement   |
|:----------|:----------|:----------|:----------|:----------|:----------|
|150|143014.13|2.35|174402.5|1.23|21.95%|
|300|199133.06|3.68|272018|1.64|36.60%|
|600|389391.65|2.18|393536.4|2.11|1.06%|
|900|468338.82|2.97|447981.98|3.3|-4.35%|
|1200|448348.52|5.18|468241.29|4.65|4.44%|
|1500|454376.79|7.04|483888.42|6.09|6.49%|

Compared with v5.1.1, the Point Select performance of v5.2.0 is improved by 11.03%.

![Point Select](/media/sysbench_v511vsv520_point_select.png)
### Update Non-index performance

| Threads   | v5.1.1 QPS   | v5.1.1 95% latency (ms)   | v5.2.0 QPS   | v5.2.0 95% latency (ms)   | QPS improvement   |
|:----------|:----------|:----------|:----------|:----------|:----------|
|150|31198.68|6.43|30714.73|6.09|-1.55%|
|300|43577.15|10.46|42997.92|9.73|-1.33%|
|600|57230.18|17.32|56168.81|16.71|-1.85%|
|900|65325.11|23.1|64098.04|22.69|-1.88%|
|1200|71528.26|28.67|69908.15|28.67|-2.26%|
|1500|76652.5|33.12|74371.79|33.72|-2.98%|

Compared with v5.1.1, the Update Non-index performance of v5.2.0 is reduced by 1.98%.

![Update Non-index](/media/sysbench_v511vsv520_update_non_index.png)
### Update Index performance

| Threads   | v5.1.1 QPS   | v5.1.1 95% latency (ms)   | v5.2.0 QPS   | v5.2.0 95% latency (ms)   | QPS improvement   |
|:----------|:----------|:----------|:----------|:----------|:----------|
|150|15641.04|13.22|15320|13.46|-2.05%|
|300|19787.73|21.89|19161.35|22.69|-3.17%|
|600|24566.74|36.89|23616.07|38.94|-3.87%|
|900|27516.57|50.11|26270.04|54.83|-4.53%|
|1200|29421.10|63.32|28002.65|69.29|-4.82%|
|1500|30957.84|77.19|28624.44|95.81|-7.54%|

Compared with v5.0.2, the Update Index performance of v5.1.0 is reduced by 4.33%.

![Update Index](/media/sysbench_v511vsv520_update_index.png)
### Read Write performance

| Threads   | v5.1.1 QPS   | v5.1.1 95% latency (ms)   | v5.2.0 QPS   | v5.2.0 95% latency (ms)   | QPS improvement   |
|:----------|:----------|:----------|:----------|:----------|:----------|
|150|68471.02|57.87|69246|54.83|1.13%|
|300|86573.09|97.55|85340.42|94.10|-1.42%|
|600|101760.75|176.73|102221.31|173.58|0.45%|
|900|111877.55|248.83|109276.45|257.95|-2.32%|
|1200|117479.4|337.94|114231.33|344.08|-2.76%|
|1500|119662.91|419.45|116663.28|434.83|-2.51%|

Compared with v5.0.2, the Read Write performance of v5.1.0 is reduced by 1.24%.

![Read Write](/media/sysbench_v511vsv520_read_write.png)
