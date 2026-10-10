# Short connection performance test

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-performance-test.md`
- Source Title: `TiProxy Performance Test Report`
- Source Heading Path: `TiProxy Performance Test Report > Short connection test | TiProxy Performance Test Report > Short connection test > Test plan | TiProxy Performance Test Report > Short connection test > Test results`
- Source Line Ranges: `287-314`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: `tidb`
- Topic Tags: `short-connections`, `connection-churn`, `sysbench`, `qps`, `latency`, `cpu-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0275_b013b0419e`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-performance-test.md#short-connection-test`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a85a6c7058b11d9d4a4033038e409a92de0b019311df71ac52748f6badb0da8c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-performance-test#short-connection-test
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-performance-test.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiProxy short connection benchmark results under frequent connection creation and destruction during sysbench execution.
- Retrieval Keywords: Short connection test, frequent creation and destruction of connections, 100 short connections per second, 200 short connections per second, 300 short connections per second, new connections per second, sysbench oltp_point_select, --threads=50, run --tables=32 --table-size=1000000, QPS, Avg latency (ms), P95 latency (ms), TiProxy CPU usage, TiDB overall CPU usage
- Follow-up Guidance: The test results table lists QPS, latency, TiProxy CPU usage, and TiDB overall CPU usage for 100, 200, and 300 new connections per second.
- Classification Note: This chunk is classified as performance because it measures TiProxy throughput and latency while short connections are frequently created and disconnected.

## Official Source Content

## Short connection test
### Test plan

This test aims to verify that frequent creation and destruction of connections have minimal impact on the QPS when the client uses short connections. This test starts another client program to create and disconnect 100, 200, and 300 short connections per second while executing `sysbench`.

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

| New connections per second | QPS    | Avg latency (ms) | P95 latency (ms) | TiProxy CPU usage | TiDB overall CPU usage |
|----------------------------|--------|------------------|------------------|-------------------|------------------------|
| 100                        | 95597  | 0.52             | 0.65             | 330%              | 1800%                  |
| 200                        | 94692  | 0.53             | 0.67             | 330%              | 1800%                  |
| 300                        | 94102  | 0.53             | 0.68             | 330%              | 1900%                  |
