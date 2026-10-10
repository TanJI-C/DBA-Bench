# Basic workload performance comparison results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-performance-test.md`
- Source Title: `TiProxy Performance Test Report`
- Source Heading Path: `TiProxy Performance Test Report > Basic workload test | TiProxy Performance Test Report > Basic workload test > Test plan | TiProxy Performance Test Report > Basic workload test > Point Select | TiProxy Performance Test Report > Basic workload test > Read Only | TiProxy Performance Test Report > Basic workload test > Write Only | TiProxy Performance Test Report > Basic workload test > Read Write`
- Source Line Ranges: `81-173`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: `tidb`
- Topic Tags: `sysbench`, `oltp`, `qps`, `latency`, `concurrency`, `point-select`, `read-only`, `write-only`, `read-write`, `haproxy-comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0270_d862932ef9`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-performance-test.md#basic-workload-test`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e5f320401a5b89b9456a4e05f230cf4afe22ccde65b23d7f1f37072079fda90e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-performance-test#basic-workload-test
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-performance-test.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TiProxy and HAProxy benchmark results for Sysbench basic workloads such as point select, read only, write only, and read write at different concurrency levels.
- Retrieval Keywords: Basic workload test, Point Select, Read Only, Write Only, Read Write, sysbench $testname, --threads=$threads, --time=1200, --report-interval=10, --rand-type=uniform, --db-driver=mysql, --mysql-db=sbtest, QPS, Avg latency (ms), P95 latency (ms), TiProxy CPU usage, HAProxy CPU usage, TiDB overall CPU usage, point select QPS, read only QPS, write only QPS, read write QPS
- Follow-up Guidance: The report also includes a result set test that compares QPS under different result set row numbers using 100 concurrency.
- Classification Note: This chunk is classified as performance because it provides measured QPS, latency, and CPU usage results for TiProxy and HAProxy under multiple Sysbench OLTP workloads.

## Official Source Content

## Basic workload test
### Test plan

This test aims to compare the QPS of TiProxy and HAProxy under four types of workloads: point select, read only, write only, and read write. Each type of workload is tested with different concurrency to compare the QPS of TiProxy and HAProxy.

The following command is used to perform the test:

```bash
sysbench $testname \
    --threads=$threads \
    --time=1200 \
    --report-interval=10 \
    --rand-type=uniform \
    --db-driver=mysql \
    --mysql-db=sbtest \
    --mysql-host=$host \
    --mysql-port=$port \
    run --tables=32 --table-size=1000000
```
### Point Select

TiProxy test results:

| Threads | QPS     | Avg latency (ms) | P95 latency (ms) | TiProxy CPU usage | TiDB overall CPU usage |
|---------|---------|------------------|------------------|-------------------|------------------------|
| 20      | 41273   | 0.48             | 0.64             | 190%              | 900%                   |
| 50      | 100255  | 0.50             | 0.62             | 330%              | 1900%                  |
| 100     | 137688  | 0.73             | 1.01             | 400%              | 2600%                  |

HAProxy test results:

| Threads | QPS    | Avg latency (ms) | P95 latency (ms) | HAProxy CPU usage | TiDB overall CPU usage |
|---------|--------|------------------|------------------|-------------------|------------------------|
| 20      | 44833  | 0.45             | 0.61             | 140%              | 1000%                  |
| 50      | 103631 | 0.48             | 0.61             | 270%              | 2100%                  |
| 100     | 163069 | 0.61             | 0.77             | 360%              | 3100%                  |
### Read Only

TiProxy test results:

| Threads | QPS    | Avg latency (ms) | P95 latency (ms) | TiProxy CPU usage | TiDB overall CPU usage |
|---------|--------|------------------|------------------|-------------------|------------------------|
| 50      | 72076  | 11.09            | 12.75            | 290%              | 2500%                  |
| 100     | 109704 | 14.58            | 17.63            | 370%              | 3800%                  |
| 200     | 117519 | 27.21            | 32.53            | 400%              | 4100%                  |

HAProxy test results:

| Threads | QPS     | Avg latency (ms) | P95 latency (ms) | HAProxy CPU usage | TiDB overall CPU usage |
|---------|---------|------------------|------------------|-------------------|------------------------|
| 50      | 75760   | 10.56            | 12.08            | 250%              | 2600%                  |
| 100     | 121730  | 13.14            | 15.83            | 350%              | 4200%                  |
| 200     | 131712  | 24.27            | 30.26            | 370%              | 4500%                  |
### Write Only

TiProxy test results:

| Threads | QPS     | Avg latency (ms) | P95 latency (ms) | TiProxy CPU usage | TiDB overall CPU usage |
|---------|---------|------------------|------------------|-------------------|------------------------|
| 100     | 81957   | 7.32             | 10.27            | 290%              | 3900%                  |
| 300     | 103040  | 17.45            | 31.37            | 330%              | 4700%                  |
| 500     | 104869  | 28.59            | 52.89            | 340%              | 4800%                  |

HAProxy test results:

| Threads | QPS     | Avg latency (ms) | P95 latency (ms) | HAProxy CPU usage | TiDB overall CPU usage |
|---------|---------|------------------|------------------|-------------------|------------------------|
| 100     | 81708   | 7.34             | 10.65            | 240%              | 3700%                  |
| 300     | 106008  | 16.95            | 31.37            | 320%              | 4800%                  |
| 500     | 122369  | 24.45            | 47.47            | 350%              | 5300%                  |
### Read Write

TiProxy test results:

| Threads | QPS    | Avg latency (ms) | P95 latency (ms) | TiProxy CPU usage | TiDB overall CPU usage |
|---------|--------|------------------|------------------|-------------------|------------------------|
| 50      | 58571  | 17.07            | 19.65            | 250%              | 2600%                  |
| 100     | 88432  | 22.60            | 29.19            | 330%              | 3900%                  |
| 200     | 108758 | 36.73            | 51.94            | 380%              | 4800%                  |

HAProxy test results:

| Threads | QPS     | Avg latency (ms) | P95 latency (ms) | HAProxy CPU usage | TiDB overall CPU usage |
|---------|---------|------------------|------------------|-------------------|------------------------|
| 50      | 61226   | 16.33            | 19.65            | 190%              | 2800%                  |
| 100     | 96569   | 20.70            | 26.68            | 290%              | 4100%                  |
| 200     | 120163  | 31.28            | 49.21            | 340%              | 5200%                  |
