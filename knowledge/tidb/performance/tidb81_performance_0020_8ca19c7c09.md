# Sysbench benchmark results by workload

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v5.4.0-vs-v5.3.0.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test results | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test results > Point Select performance | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test results > Update Non-index performance | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test results > Update Index performance | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test results > Read Write performance`
- Source Line Ranges: `155-203`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `sysbench`, `test-results`, `tps`, `latency`, `point-select`, `update-non-index`, `update-index`, `read-write`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0020_8ca19c7c09`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v5.4.0-vs-v5.3.0.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8b4f1e5efce1b0a8edccd93b714ed881138fb580dac4f1e13af1f2905a57a70e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v5.4.0-vs-v5.3.0#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v5.4.0-vs-v5.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving benchmark result tables for Point Select, Update Non-index, Update Index, or Read Write workloads, including TPS, 95% latency, thread counts, and improvement percentages between v5.3.0 and v5.4.0.
- Retrieval Keywords: Test results, Point Select performance, Update Non-index performance, Update Index performance, Read Write performance, v5.3.0 TPS, v5.4.0 TPS, 95% latency (ms), Threads 300 600 900, Point Select performance of v5.4.0 is slightly improved by 0.64%, Update Non-index performance of v5.4.0 is improved by 2.59%, Update Index performance of v5.4.0 is improved by 4.85%, Read Write performance of v5.4.0 is improved by 3.30%
- Follow-up Guidance: 
- Classification Note: This is classified as performance because it contains the measured Sysbench throughput and latency results for multiple workloads and concurrency levels.

## Official Source Content

## Test results
### Point Select performance

| Threads   | v5.3.0 TPS | v5.4.0 TPS  | v5.3.0 95% latency (ms) | v5.4.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|266041.84|264345.73|1.96|2.07|-0.64|
|600|351782.71|348715.98|3.43|3.49|-0.87|
|900|386553.31|399777.11|5.09|4.74|3.42|

Compared with v5.3.0, the Point Select performance of v5.4.0 is slightly improved by 0.64%.

![Point Select](/media/sysbench_v530vsv540_point_select.png)
### Update Non-index performance

| Threads   | v5.3.0 TPS | v5.4.0 TPS  | v5.3.0 95% latency (ms) | v5.4.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|40804.31|41187.1|11.87|11.87|0.94|
|600|51239.4|53172.03|20.74|19.65|3.77|
|900|57897.56|59666.8|27.66|27.66|3.06|

Compared with v5.3.0, the Update Non-index performance of v5.4.0 is improved by 2.59%.

![Update Non-index](/media/sysbench_v530vsv540_update_non_index.png)
### Update Index performance

| Threads   | v5.3.0 TPS | v5.4.0 TPS  | v5.3.0 95% latency (ms) | v5.4.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|17737.82|18716.5|26.2|24.83|5.52|
|600|21614.39|22670.74|44.98|42.61|4.89|
|900|23933.7|24922.05|62.19|61.08|4.13|

Compared with v5.3.0, the Update Index performance of v5.4.0 is improved by 4.85%.

![Update Index](/media/sysbench_v530vsv540_update_index.png)
### Read Write performance

| Threads   | v5.3.0 TPS  | v5.4.0 TPS | v5.3.0 95% latency (ms) | v5.4.0 95% latency (ms)   | TPS improvement (%)  |
|:----------|:----------|:----------|:----------|:----------|:----------|
|300|3810.78|3929.29|108.68|106.75|3.11|
|600|4514.28|4684.64|193.38|186.54|3.77|
|900|4842.49|4988.49|282.25|277.21|3.01|

Compared with v5.3.0, the Read Write performance of v5.4.0 is improved by 3.30%.

![Read Write](/media/sysbench_v530vsv540_read_write.png)
