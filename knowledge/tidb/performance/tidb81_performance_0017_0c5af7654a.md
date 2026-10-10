# Sysbench performance results for v5.3.0 vs v5.2.2

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v5.3.0-vs-v5.2.2.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v5.3.0 vs. v5.2.2`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v5.3.0 vs. v5.2.2 > Test results | TiDB Sysbench Performance Test Report -- v5.3.0 vs. v5.2.2 > Test results > Point Select performance | TiDB Sysbench Performance Test Report -- v5.3.0 vs. v5.2.2 > Test results > Update Non-index performance | TiDB Sysbench Performance Test Report -- v5.3.0 vs. v5.2.2 > Test results > Update Index performance | TiDB Sysbench Performance Test Report -- v5.3.0 vs. v5.2.2 > Test results > Read Write performance`
- Source Line Ranges: `155-203`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `sysbench`, `test-results`, `tps`, `latency`, `point-select`, `update-non-index`, `update-index`, `read-write`, `version-comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0017_0c5af7654a`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v5.3.0-vs-v5.2.2.md#test-results`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a04f296c81c32515e276b6bac76785926cb54e73335ac5ef9889f3da46f9a6d5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v5.3.0-vs-v5.2.2#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v5.3.0-vs-v5.2.2.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Sysbench test results comparing TPS and 95% latency between TiDB v5.3.0 and v5.2.2 for point_select, update_non_index, update_index, and read_write workloads.
- Retrieval Keywords: Sysbench test results TiDB v5.3.0 vs v5.2.2, Point Select performance, Update Non-index performance, Update Index performance, Read Write performance, v5.2.2 TPS, v5.3.0 TPS, 95% latency ms, Threads 300 600 900, Point Select reduced slightly by 0.81%, Update Non-index improved slightly by 0.95%, Update Index improved slightly by 1.83%, Read Write reduced slightly by 0.62%, sysbench_v522vsv530_point_select.png, sysbench_v522vsv530_update_non_index.png, sysbench_v522vsv530_update_index.png, sysbench_v522vsv530_read_write.png
- Follow-up Guidance: 
- Classification Note: This is classified as performance content because it reports benchmark throughput and latency results for multiple Sysbench workloads across the two TiDB versions.

## Official Source Content

## Test results
### Point Select performance

| Threads   | v5.2.2 TPS | v5.3.0 TPS | v5.2.2 95% latency (ms) | v5.3.0 95% latency (ms) | TPS improvement (%) |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|267673.17|267516.77|1.76|1.67|-0.06|
|600|369820.29|361672.56|2.91|2.97|-2.20|
|900|417143.31|416479.47|4.1|4.18|-0.16|

Compared with v5.2.2, the Point Select performance of v5.3.0 is reduced slightly by 0.81%.

![Point Select](/media/sysbench_v522vsv530_point_select.png)
### Update Non-index performance

| Threads   | v5.2.2 TPS | v5.3.0 TPS  | v5.2.2 95% latency (ms) | v5.3.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|39715.31|40041.03|11.87|12.08|0.82|
|600|50239.42|51110.04|20.74|20.37|1.73|
|900|57073.97|57252.74|28.16|27.66|0.31|

Compared with v5.2.2, the Update Non-index performance of v5.3.0 is improved slightly by 0.95%.

![Update Non-index](/media/sysbench_v522vsv530_update_non_index.png)
### Update Index performance

| Threads   | v5.2.2 TPS | v5.3.0 TPS  | v5.2.2 95% latency (ms) | v5.3.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|17634.03|17821.1|25.74|25.74|1.06|
|600|20998.59|21534.13|46.63|45.79|2.55|
|900|23420.75|23859.64|64.47|62.19|1.87|

Compared with v5.2.2, the Update Index performance of v5.3.0 is improved slightly by 1.83%.

![Update Index](/media/sysbench_v522vsv530_update_index.png)
### Read Write performance

| Threads   | v5.2.2 TPS  | v5.3.0 TPS | v5.2.2 95% latency (ms) | v5.3.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|3872.01|3848.63|106.75|106.75|-0.60|
|600|4514.17|4471.77|200.47|196.89|-0.94|
|900|4877.05|4861.45|287.38|282.25|-0.32|

Compared with v5.2.2, the Read Write performance of v5.3.0 is reduced slightly by 0.62%.

![Read Write](/media/sysbench_v522vsv530_read_write.png)
