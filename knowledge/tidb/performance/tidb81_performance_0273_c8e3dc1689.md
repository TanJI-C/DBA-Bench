# Scalability test plan and results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-performance-test.md`
- Source Title: `TiProxy Performance Test Report`
- Source Heading Path: `TiProxy Performance Test Report > Scalability test | TiProxy Performance Test Report > Scalability test > Test plan | TiProxy Performance Test Report > Scalability test > Test results`
- Source Line Ranges: `222-251`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: `tidb`
- Topic Tags: `scalability`, `benchmark-plan`, `sysbench`, `vcpu`, `threads`, `qps`, `cpu-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0273_c8e3dc1689`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-performance-test.md#scalability-test`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4743208b39e9df0a2e5af88588b7ff2a1e343187a375f4b233f842adfd887002`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-performance-test#scalability-test
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-performance-test.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiProxy scalability test plan, the sysbench oltp_point_select command, or QPS results across different vCPU and thread counts.
- Retrieval Keywords: Scalability test, Test plan, Test results, sysbench oltp_point_select, --threads=$threads, --time=1200, --report-interval=10, --rand-type=uniform, --db-driver=mysql, --mysql-db=sbtest, --mysql-host=$host, --mysql-port=$port, run --tables=32 --table-size=1000000, vCPU, Threads, QPS, TiProxy CPU usage, TiDB overall CPU usage
- Follow-up Guidance: The test results table compares 2, 4, 6, and 8 vCPU configurations with corresponding thread counts and QPS, latency, and CPU usage metrics.
- Classification Note: This chunk is classified as performance because it describes a scalability benchmark and records TiProxy throughput and latency under different specifications.

## Official Source Content

## Scalability test
### Test plan

This test aims to verify that the performance of TiProxy is proportional to its specifications, to ensure that upgrading the specifications of TiProxy can improve its QPS upper limit. This test uses TiProxy instances with different vCPU numbers and concurrency to compare the QPS.

The following command is used to perform the test:

```bash
sysbench oltp_point_select \
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
### Test results

| vCPU | Threads | QPS     | Avg latency (ms) | P95 latency (ms) | TiProxy CPU usage | TiDB overall CPU usage |
|------|---------|---------|------------------|------------------|-------------------|------------------------|
| 2    | 40      | 58508   | 0.68             | 0.97             | 190%              | 1200%                  |
| 4    | 80      | 104890  | 0.76             | 1.16             | 390%              | 2000%                  |
| 6    | 120     | 155520  | 0.77             | 1.14             | 590%              | 2900%                  |
| 8    | 160     | 202134  | 0.79             | 1.18             | 800%              | 3900%                  |
