# Result set test plan

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-performance-test.md`
- Source Title: `TiProxy Performance Test Report`
- Source Heading Path: `TiProxy Performance Test Report > Result set test | TiProxy Performance Test Report > Result set test > Test plan`
- Source Line Ranges: `174-201`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: `tidb`
- Topic Tags: `result-set`, `sysbench`, `qps`, `concurrency`, `range-query`, `haproxy-comparison`, `test-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0271_55969d0161`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-performance-test.md#result-set-test`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `350a6c52a1241e7aa90de2ca144993ddf4130ea88065aee9f27634c9dd30fc30`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-performance-test#result-set-test
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-performance-test.md

## Retrieval Guidance

- Use When: Use this chunk when searching for the result set test methodology that compares TiProxy and HAProxy performance across different result set row numbers.
- Retrieval Keywords: Result set test, Test plan, different result set row numbers, 100 concurrency, row numbers of 10 100 1000 and 10000, sysbench oltp_read_only, --threads=100, --skip_trx=true, --point_selects=0, --sum_ranges=0, --order_ranges=0, --distinct_ranges=0, --simple_ranges=1, --range_size=$range_size, run --tables=32 --table-size=1000000
- Follow-up Guidance: 
- Classification Note: This chunk is classified as performance because it defines the benchmark plan and exact Sysbench command for testing how result set row count affects TiProxy and HAProxy QPS.

## Official Source Content

## Result set test
### Test plan

This test aims to compare the performance of TiProxy and HAProxy under different result set row numbers. This test uses 100 concurrency, and compares the QPS of TiProxy and HAProxy with result set row numbers of 10, 100, 1000, and 10000.

The following command is used to perform the test:

```bash
sysbench oltp_read_only \
    --threads=100 \
    --time=1200 \
    --report-interval=10 \
    --rand-type=uniform \
    --db-driver=mysql \
    --mysql-db=sbtest \
    --mysql-host=$host \
    --mysql-port=$port \
    --skip_trx=true \
    --point_selects=0 \
    --sum_ranges=0 \
    --order_ranges=0 \
    --distinct_ranges=0 \
    --simple_ranges=1 \
    --range_size=$range_size
    run --tables=32 --table-size=1000000
```
