# Result set test results for TiProxy and HAProxy

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-performance-test.md`
- Source Title: `TiProxy Performance Test Report`
- Source Heading Path: `TiProxy Performance Test Report > Result set test > Test results`
- Source Line Ranges: `202-221`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: `tidb`
- Topic Tags: `benchmark-results`, `result-set`, `qps`, `latency`, `cpu-usage`, `network-throughput`, `haproxy-comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0272_de38bf3b97`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-performance-test.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2ac34258de3223b1afdbaf758b55abb5660d4decf3eac4f6e9c6dfb7f9d0e019`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-performance-test#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-performance-test.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TiProxy and HAProxy result set benchmark results by range size, QPS, latency, CPU usage, and network throughput.
- Retrieval Keywords: TiProxy test results, HAProxy test results, Result set test, Range size, QPS, Avg latency (ms), P95 latency (ms), TiProxy CPU usage, HAProxy CPU usage, TiDB overall CPU usage, Inbound network (MiB/s), Outbound network (MiB/s), range size 10 100 1000 10000
- Follow-up Guidance: 
- Classification Note: This chunk is classified as performance because it reports benchmark test results for TiProxy and HAProxy using QPS, latency, CPU usage, and network throughput metrics.

## Official Source Content

### Test results

TiProxy test results:

| Range size | QPS     | Avg latency (ms) | P95 latency (ms) | TiProxy CPU usage | TiDB overall CPU usage | Inbound network (MiB/s) | Outbound network (MiB/s) |
|------------|---------|------------------|------------------|-------------------|------------------------|-------------------------|--------------------------|
| 10         | 80157   | 1.25             | 1.61             | 340%              | 2600%                  | 140                     | 140                      |
| 100        | 55936   | 1.79             | 2.43             | 370%              | 2800%                  | 820                     | 820                      |
| 1000       | 10313   | 9.69             | 13.70            | 310%              | 1500%                  | 1370                    | 1370                     |
| 10000      | 1064    | 93.88            | 142.39           | 250%              | 600%                   | 1430                    | 1430                     |

HAProxy test results:

| Range size | QPS    | Avg latency (ms) | P95 latency (ms) | HAProxy CPU usage | TiDB overall CPU usage | Inbound network (MiB/s) | Outbound network (MiB/s) |
|------------|--------|------------------|------------------|-------------------|------------------------|-------------------------|--------------------------|
| 10         | 94376  | 1.06             | 1.30             | 250%              | 4000%                  | 150                     | 150                      |
| 100        | 70129  | 1.42             | 1.76             | 270%              | 3300%                  | 890                     | 890                      |
| 1000       | 9501   | 11.18            | 14.73            | 240%              | 1500%                  | 1180                    | 1180                     |
| 10000      | 955    | 104.61           | 320.17           | 180%              | 1200%                  | 1200                    | 1200                     |
