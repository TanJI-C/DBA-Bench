# TPC-C benchmark results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.5-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0`
- Source Heading Path: `TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0 > Test results`
- Source Line Ranges: `113-123`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `tpcc`, `benchmark-results`, `tpmc`, `throughput`, `threads`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0226_d60bfca0c9`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.5-performance-benchmarking-with-tpcc.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `aee9b7b488f56a3fe84f0ede6f7f71f6640ca29b1102d344f40543ad63dde034`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.5-performance-benchmarking-with-tpcc#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.5-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for the published TPC-C throughput results or tpmC values for TiDB v8.5.0 under the documented test environment.
- Retrieval Keywords: Test results, v8.5.0 tpmC, Threads 50 43146, Threads 100 73875, Threads 200 103395, TPC-C performance of v8.5.0, tpmC results
- Follow-up Guidance: The source presents the TPC-C performance table for 50, 100, and 200 threads in the documented test environment.
- Classification Note: This is classified as performance content because it reports measured TPC-C throughput results as tpmC values by thread count.

## Official Source Content

## Test results

The TPC-C performance of v8.5.0 in the [test environment](#test-environment) is as follows:

| Threads |  v8.5.0 tpmC |
|:--------|:----------|
| 50  | 43,146  |
| 100 | 73,875  |
| 200 | 103,395  |

![TPC-C](/media/tidb-cloud/v8.5.0_tpcc.png)
