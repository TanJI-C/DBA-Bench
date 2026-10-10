# TPC-H benchmark results for v4.0 versus v3.0

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v4.0-performance-benchmarking-with-tpch.md`
- Source Title: `TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0`
- Source Heading Path: `TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test result`
- Source Line Ranges: `163-208`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiflash`
- Topic Tags: `test-results`, `query-latency`, `comparison`, `optimizer`, `tiflash-replica`, `htap`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0044_2c3c9e83d4`
- Source ID: `tidb-docs-8.1:benchmark/v4.0-performance-benchmarking-with-tpch.md#test-result`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `50da09f3a6bed2ee4d99a5ba410b0cdf9b6119dc152d61085c2b59cef3c534c0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v4.0-performance-benchmarking-with-tpch#test-result
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v4.0-performance-benchmarking-with-tpch.md

## Retrieval Guidance

- Use When: Use this chunk when the request asks for the measured TPC-H query execution times or the summarized performance comparison between v3.0, v4.0 TiKV Only, and v4.0 TiKV/TiFlash Automatically.
- Retrieval Keywords: Test result, Query ID, v3.0, v4.0 TiKV Only, v4.0 TiKV/TiFlash Automatically, TPC-H, query execution time, The tables only have primary keys and do not have secondary indexes, TiDB optimizer, TiFlash replica, cost estimation, about 100% on average, 22 queries, tpch-v4vsv3.png
- Follow-up Guidance: The source explains that v4.0 TiKV Only reflects reading only from TiKV, while v4.0 TiKV/TiFlash Automatically reflects optimizer-based selection of the TiFlash replica according to cost estimation.
- Classification Note: This is classified as performance because it contains the benchmark latency results and the official summary of performance improvement across the 22 TPC-H queries.

## Official Source Content

## Test result

> **Note:**
>
> The tables on which SQL statements are executed in this test only have primary keys and do not have secondary indexes. Therefore, the test result below is not influenced by indexes.

| Query ID |  v3.0  |  v4.0 TiKV Only |  v4.0 TiKV/TiFlash Automatically |
| :-------- | :----------- | :------------ | :-------------- |
| 1       |    7.78 s   |      7.45 s  |      2.09 s    |
| 2       |    3.15 s   |      1.71 s  |      1.71 s    |
| 3       |    6.61 s   |      4.10 s  |      4.05 s    |
| 4       |    2.98 s   |      2.56 s  |      1.87 s    |
| 5       |   20.35 s   |      5.71 s  |      8.53 s    |
| 6       |    4.75 s   |      2.44 s  |      0.39 s    |
| 7       |    7.97 s   |      3.72 s  |      3.59 s    |
| 8       |    5.89 s   |      3.22 s  |      8.59 s    |
| 9       |   34.08 s   |     11.87 s  |     15.41 s    |
| 10      |    4.83 s   |      2.75 s  |      3.35 s    |
| 11      |    3.98 s   |      1.60 s  |      1.59 s    |
| 12      |    5.63 s   |      3.40 s  |      1.03 s    |
| 13      |    5.41 s   |      4.56 s  |      4.02 s    |
| 14      |    5.19 s   |      3.10 s  |      0.78 s    |
| 15      |   10.25 s   |      1.82 s  |      1.26 s    |
| 16      |    2.46 s   |      1.51 s  |      1.58 s    |
| 17      |   23.76 s   |     12.38 s  |      8.52 s    |
| 18      |   17.14 s   |     16.38 s  |     16.06 s    |
| 19      |    5.70 s   |      4.59 s  |      3.20 s    |
| 20      |    4.98 s   |      1.89 s  |      1.29 s    |
| 21      |   11.12 s   |      6.23 s  |      6.26 s    |
| 22      |    4.49 s   |      3.05 s  |      2.31 s    |

![TPC-H](/media/tpch-v4vsv3.png)

In the performance diagram above:

+ Blue lines represent v3.0;
+ Red lines represent v4.0 (data read only from TiKV);
+ Yellow lines represent v4.0 (data read from TiKV and TiFlash automatically based on intelligent choice).
+ The y-axis represents the execution time of the query. The less the time, the better the performance.

Result description:

+ **v4.0 TiKV Only** means that TiDB reads data only from TiKV. The result shows that the TPC-H performance increased after TiDB and TiKV are upgraded to v4.0.
+ **v4.0 TiKV/TiFlash Automatically** means that the TiDB optimizer automatically determines whether to read data from the TiFlash replica according to the cost estimation. The result shows that the TPC-H performance increased in the full HTAP form of v4.0.

From the diagram above, you can see that TPC-H performance increases by about 100% on average over a set of 22 queries.
