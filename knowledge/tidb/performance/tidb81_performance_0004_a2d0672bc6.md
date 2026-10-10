# Sysbench v2 benchmark results for Select, OLTP, and Insert

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v2.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test result | TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test result > Standard `Select` test | TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test result > Standard OLTP test | TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test result > Standard `Insert` test`
- Source Line Ranges: `84-129`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `benchmark-results`, `select`, `oltp`, `insert`, `qps`, `tps`, `latency`, `version-comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0004_a2d0672bc6`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v2.md#test-result`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `066d6c8d37e384e95d3c62b25707d0d33449a81c6f1c537320ccd395186a86c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v2#test-result
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v2.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Sysbench benchmark results comparing v2.0.0-rc6 and v1.0.8 for Standard Select, Standard OLTP, and Standard Insert with QPS, TPS, latency, table count, table size, and thread counts.
- Retrieval Keywords: Test result, Standard Select test, Standard OLTP test, Standard Insert test, QPS, TPS, Latency (avg/.95), 32, 10 million, 128 * 3, 256 * 3, 512 * 3, 1024 * 3, Select query performance, OLTP performance, Insert query performance, v2.0.0-rc6, v1.0.8
- Follow-up Guidance: The official content concludes that Select performance increased by about 10% at most, OLTP performance is almost the same, and Insert performance increased slightly for TiDB 2.0 GA compared with TiDB 1.0 GA.
- Classification Note: This chunk is classified as performance because the official content reports measured benchmark results and comparative throughput and latency statistics.

## Official Source Content

## Test result
### Standard `Select` test

| Version | Table count | Table size | Sysbench threads |QPS | Latency (avg/.95) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| v2.0.0-rc6 | 32 | 10 million | 128 * 3 |  201936 | 1.9033 ms/5.67667 ms |
| v2.0.0-rc6 | 32 | 10 million | 256 * 3 | 208130 | 3.69333 ms/8.90333 ms  |
| v2.0.0-rc6 | 32 | 10 million | 512 * 3 |  211788 | 7.23333 ms/15.59 ms |
| v2.0.0-rc6 | 32 | 10 million | 1024 * 3 |  212868 | 14.5933 ms/43.2133 ms |
| v1.0.8  | 32 | 10 million | 128 * 3 |  188686 | 2.03667 ms/5.99 ms  |
| v1.0.8  | 32 | 10 million | 256 * 3 |  195090  |3.94 ms/9.12 ms  |
| v1.0.8  | 32 | 10 million | 512 * 3 |  203012 | 7.57333 ms/15.3733 ms  |
| v1.0.8  | 32 | 10 million | 1024 * 3 |  205932 | 14.9267 ms/40.7633 ms |

According to the statistics above, the `Select` query performance of TiDB 2.0 GA has increased by about 10% at most than that of TiDB 1.0 GA.
### Standard OLTP test

| Version | Table count | Table size | Sysbench threads | TPS | QPS | Latency (avg/.95) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---:|
| v2.0.0-rc6 | 32 | 10 million | 128 * 3 | 5404.22 | 108084.4 | 87.2033 ms/110 ms |
| v2.0.0-rc6 | 32 | 10 million | 256 * 3 | 5578.165 | 111563.3 | 167.673 ms/275.623 ms |
| v2.0.0-rc6 | 32 | 10 million | 512 * 3 | 5874.045 | 117480.9 | 315.083 ms/674.017 ms |
| v2.0.0-rc6 | 32 | 10 million | 1024 * 3 | 6290.7 | 125814 | 529.183 ms/857.007 ms |
| v1.0.8 | 32 | 10 million | 128 * 3 | 5523.91 | 110478 | 69.53 ms/88.6333 ms |
| v1.0.8 | 32 | 10 million | 256 * 3 | 5969.43 | 119389 |128.63 ms/162.58 ms |
| v1.0.8 | 32 | 10 million | 512 * 3 | 6308.93 | 126179 | 243.543 ms/310.913 ms |
| v1.0.8 | 32 | 10 million | 1024 * 3 | 6444.25 | 128885 | 476.787ms/635.143 ms |

According to the statistics above, the OLTP performance of TiDB 2.0 GA and TiDB 1.0 GA is almost the same.
### Standard `Insert` test

| Version | Table count | Table size | Sysbench threads | QPS | Latency (avg/.95) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| v2.0.0-rc6 | 32 | 10 million | 128 * 3 | 31707.5 | 12.11 ms/21.1167 ms |
| v2.0.0-rc6 | 32 | 10 million | 256 * 3 | 38741.2 | 19.8233 ms/39.65 ms |
| v2.0.0-rc6 | 32 | 10 million | 512 * 3 | 45136.8 | 34.0267 ms/66.84 ms |
| v2.0.0-rc6 | 32 | 10 million | 1024 * 3 | 48667 | 63.1167 ms/121.08 ms |
| v1.0.8 | 32 | 10 million | 128 * 3 | 31125.7 | 12.3367 ms/19.89 ms |
| v1.0.8 | 32 | 10 million | 256 * 3 | 36800 | 20.8667 ms/35.3767 ms |
| v1.0.8 | 32 | 10 million | 512 * 3 | 44123 | 34.8067 ms/63.32 ms |
| v1.0.8 | 32 | 10 million | 1024 * 3 | 48496 | 63.3333 ms/118.92 ms |

According to the statistics above, the `Insert` query performance of TiDB 2.0 GA has increased slightly than that of TiDB 1.0 GA.
