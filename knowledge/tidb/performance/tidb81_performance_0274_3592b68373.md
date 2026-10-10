# Long connection performance test

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-performance-test.md`
- Source Title: `TiProxy Performance Test Report`
- Source Heading Path: `TiProxy Performance Test Report > Long connection test | TiProxy Performance Test Report > Long connection test > Test plan | TiProxy Performance Test Report > Long connection test > Test results`
- Source Line Ranges: `252-286`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: `tidb`
- Topic Tags: `long-connections`, `idle-connections`, `sysbench`, `conn-buffer-size`, `qps`, `latency`, `memory-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0274_3592b68373`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-performance-test.md#long-connection-test`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5766af10152680b041cba0d44046e873e84a5e26abe6386b1482c1b480c8963e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-performance-test#long-connection-test
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-performance-test.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiProxy long connection benchmark results with idle connections, default conn-buffer-size, sysbench command details, or memory usage by connection count.
- Retrieval Keywords: Long connection test, idle long connections, 5000 idle connections, 10000 idle connections, 15000 idle connections, conn-buffer-size, proxy.conn-buffer-size: 32768, sysbench oltp_point_select, --threads=50, run --tables=32 --table-size=1000000, Connection count, QPS, Avg latency (ms), P95 latency (ms), TiProxy CPU usage, TiProxy memory usage (MB), TiDB overall CPU usage
- Follow-up Guidance: The results table shows QPS, latency, TiProxy CPU usage, TiProxy memory usage, and TiDB overall CPU usage for 5000, 10000, and 15000 idle long connections.
- Classification Note: This chunk is classified as performance because it benchmarks TiProxy behavior under many idle long connections and reports throughput, latency, CPU, and memory metrics.

## Official Source Content

## Long connection test
### Test plan

This test aims to verify that a large number of idle connections have minimal impact on the QPS when the client uses long connections. This test creates 5000, 10000, and 15000 idle long connections, and then executes `sysbench`.

This test uses the default value for the `conn-buffer-size` configuration:

```yaml
proxy.conn-buffer-size: 32768
```

Use the following command to perform the test:

```bash
sysbench oltp_point_select \
    --threads=50 \
    --time=1200 \
    --report-interval=10 \
    --rand-type=uniform \
    --db-driver=mysql \
    --mysql-db=sbtest \
    --mysql-host=$host \
    --mysql-port=$port \
    run --tables=32 --table-size=1000000
```
### Test results

| Connection count | QPS   | Avg latency (ms) | P95 latency (ms) | TiProxy CPU usage | TiProxy memory usage (MB) | TiDB overall CPU usage |
|------------------|-------|------------------|------------------|-------------------|---------------------------|------------------------|
| 5000             | 96620 | 0.52             | 0.64             | 330%              | 920                       | 1800%                  |
| 10000            | 96143 | 0.52             | 0.65             | 330%              | 1710                      | 1800%                  |
| 15000            | 96048 | 0.52             | 0.65             | 330%              | 2570                      | 1900%                  |
