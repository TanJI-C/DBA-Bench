# Sysbench v2 benchmark purpose, environment, and test plan

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v2.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 | TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test purpose | TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test version, time, and place | TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test environment | TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test plan | TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test plan > TiDB version information | TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test plan > v1.0.8 | TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test plan > v2.0.0-rc6 | TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test plan > TiKV parameter configuration | TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0 > Test plan > Cluster topology`
- Source Line Ranges: `5-83`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `shared`
- Topic Tags: `benchmarking`, `test-purpose`, `environment`, `version-comparison`, `cluster-topology`, `tikv-parameters`, `githash`, `sysbench`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0003_39e891e24a`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v2.md#tidb-sysbench-performance-test-report-v2-0-0-vs-v1-0-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d73e68325262d746049b27c6da8eadf76b4f7931f6ab2ee92a5ab8f37b810275`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v2#tidb-sysbench-performance-test-report-v2-0-0-vs-v1-0-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v2.md

## Retrieval Guidance

- Use When: Use this chunk when you need the purpose, environment, component GitHash values, TiKV parameter configuration, or cluster topology for the TiDB Sysbench Performance Test Report comparing v2.0.0-rc6 and v1.0.8.
- Retrieval Keywords: TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0, Test purpose, v1.0.8 vs. v2.0.0-rc6, April 2018, Beijing, China, CentOS 7.3.1611, 40 vCPUs, 128GB, Optane 500GB SSD, GitHash, TiKV parameter configuration, sync-log = false, grpc-concurrency = 8, grpc-raft-conn-num = 24, use-delete-range: false, Cluster topology, 172.16.21.1, 1*tidb 1*pd 1*sysbench, 1*tikv
- Follow-up Guidance: The next chunk provides the benchmark test results for Standard Select, Standard OLTP, and Standard Insert tests.
- Classification Note: This chunk is classified as performance because the official content defines the benchmark purpose and records the test environment and plan used for the version comparison.

## Official Source Content

# TiDB Sysbench Performance Test Report -- v2.0.0 vs. v1.0.0
## Test purpose

This test aims to compare the performances of TiDB 1.0 and TiDB 2.0.
## Test version, time, and place

TiDB version: v1.0.8 vs. v2.0.0-rc6

Time: April 2018

Place: Beijing, China
## Test environment

IDC machine

| Type | Name |
| -------- | --------- |
| OS | linux (CentOS 7.3.1611) |
| CPU | 40 vCPUs, Intel(R) Xeon(R) CPU E5-2630 v4 @ 2.20GHz |
| RAM | 128GB |
| DISK | Optane 500GB SSD * 1 |
## Test plan
### TiDB version information
### v1.0.8

| Component | GitHash |
| -------- | --------- |
| TiDB | 571f0bbd28a0b8155a5ee831992c986b90d21ab7 |
| TiKV | 4ef5889947019e3cb55cc744f487aa63b42540e7 |
| PD | 776bcd940b71d295a2c7ed762582bc3aff7d3c0e |
### v2.0.0-rc6

| Component | GitHash |
| :--------: | :---------: |
| TiDB | 82d35f1b7f9047c478f4e1e82aa0002abc8107e7 |
| TiKV | 7ed4f6a91f92cad5cd5323aaebe7d9f04b77cc79 |
| PD | 2c8e7d7e33b38e457169ce5dfb2f461fced82d65 |
### TiKV parameter configuration

- v1.0.8

    ```
    sync-log = false
    grpc-concurrency = 8
    grpc-raft-conn-num = 24
    ```

- v2.0.0-rc6

    ```
    sync-log = false
    grpc-concurrency = 8
    grpc-raft-conn-num = 24
    use-delete-range: false
    ```
### Cluster topology

| Machine IP | Deployment instance |
|--------------|------------|
| 172.16.21.1 | 1*tidb 1*pd 1*sysbench |
| 172.16.21.2 | 1*tidb 1*pd 1*sysbench |
| 172.16.21.3 | 1*tidb 1*pd 1*sysbench |
| 172.16.11.4 | 1*tikv |
| 172.16.11.5 | 1*tikv |
| 172.16.11.6 | 1*tikv |
| 172.16.11.7 | 1*tikv |
| 172.16.11.8 | 1*tikv |
| 172.16.11.9 | 1*tikv |
