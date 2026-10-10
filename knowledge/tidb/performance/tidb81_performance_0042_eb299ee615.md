# TPC-H benchmark purpose and test environment setup

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v4.0-performance-benchmarking-with-tpch.md`
- Source Title: `TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0`
- Source Heading Path: `TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test purpose | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Hardware configuration | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Software version | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration > v3.0 | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration > v3.0 > Variable configuration | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration > v4.0 | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration > v4.0 > TiKV configuration | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration > v4.0 > PD configuration | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration > v4.0 > TiFlash configuration | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration > v4.0 > Variable configuration`
- Source Line Ranges: `5-108`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiflash`, `pd`, `tiup`
- Topic Tags: `tpch`, `benchmarking`, `olap`, `htap`, `aws-ec2`, `hardware-configuration`, `software-version`, `parameter-configuration`, `session-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0042_eb299ee615`
- Source ID: `tidb-docs-8.1:benchmark/v4.0-performance-benchmarking-with-tpch.md#tidb-tpc-h-performance-test-report-v4-0-vs-v3-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `69f2810a8a468db97046b1e20f67adb0be66a2f263b5013130a613121856e68b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v4.0-performance-benchmarking-with-tpch#tidb-tpc-h-performance-test-report-v4-0-vs-v3-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v4.0-performance-benchmarking-with-tpch.md

## Retrieval Guidance

- Use When: Use this chunk when the request asks for the purpose, AWS EC2 environment, software versions, or parameter and session variable settings used in the TiDB v4.0 versus v3.0 TPC-H benchmark.
- Retrieval Keywords: TPC-H Performance Test Report -- v4.0 vs. v3.0, Test purpose, Test environment (AWS EC2), Hardware configuration, Software version, Parameter configuration, tiup-bench 0.2, tidb_distsql_scan_concurrency, tidb_projection_concurrency, tidb_hashagg_partial_concurrency, tidb_hashagg_final_concurrency, tidb_hash_join_concurrency, tidb_index_lookup_concurrency, tidb_index_lookup_join_concurrency, tidb_allow_batch_cop, tidb_opt_distinct_agg_push_down, readpool.storage.use-unified-pool, readpool.coprocessor.use-unified-pool, replication.enable-placement-rules, logger.level, learner_config.log-level, TiFlash, HTAP
- Follow-up Guidance: The source notes that there might be session variable(s) and recommends that all queries are executed in the current session.
- Classification Note: This is classified as performance because the content defines the benchmark goal and the exact environment and parameter settings used for OLAP TPC-H performance comparison.

## Official Source Content

# TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0
## Test purpose

This test aims to compare the TPC-H performance of TiDB 4.0 and TiDB 3.0 in the online analytical processing (OLAP) scenario.

Because [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview) is introduced in TiDB v4.0, which enhances TiDB's Hybrid Transactional and Analytical Processing (HTAP) capabilities, test objects in this report are as follows:

+ TiDB v3.0 that reads data only from TiKV.
+ TiDB v4.0 that reads data only from TiKV.
+ TiDB v4.0 that reads data from TiKV and TiFlash automatically based on intelligent choice.
## Test environment (AWS EC2)
### Hardware configuration

| Service type         | EC2 type     | Instance count |
|:----------------|:------------|:----|
| PD              | m5.xlarge   |  3  |
| TiDB            | c5.4xlarge  |  2  |
| TiKV & TiFlash  | i3.4xlarge  |  3  |
| TPC-H           | m5.xlarge   |  1  |
### Software version

| Service type   | Software version   |
|:----------|:-----------|
| PD        | 3.0 and 4.0   |
| TiDB      | 3.0 and 4.0   |
| TiKV      | 3.0 and 4.0   |
| TiFlash   | 4.0        |
| tiup-bench | 0.2      |
### Parameter configuration
#### v3.0

For v3.0, TiDB, TiKV, and PD use the default parameter configuration.
##### Variable configuration

```sql
set global tidb_distsql_scan_concurrency = 30;
set global tidb_projection_concurrency = 16;
set global tidb_hashagg_partial_concurrency = 16;
set global tidb_hashagg_final_concurrency = 16;
set global tidb_hash_join_concurrency = 16;
set global tidb_index_lookup_concurrency = 16;
set global tidb_index_lookup_join_concurrency = 16;
```
#### v4.0

For v4.0, TiDB uses the default parameter configuration.
##### TiKV configuration

```yaml
readpool.storage.use-unified-pool: false
readpool.coprocessor.use-unified-pool: true
```
##### PD configuration

```yaml
replication.enable-placement-rules: true
```
##### TiFlash configuration

```yaml
logger.level: "info"
learner_config.log-level: "info"
```
##### Variable configuration

> **Note:**
>
> There might be session variable(s). It is recommended that all queries are executed in the current session.

```sql
set global tidb_allow_batch_cop = 1;
set session tidb_opt_distinct_agg_push_down = 1;
set global tidb_distsql_scan_concurrency = 30;
set global tidb_projection_concurrency = 16;
set global tidb_hashagg_partial_concurrency = 16;
set global tidb_hashagg_final_concurrency = 16;
set global tidb_hash_join_concurrency = 16;
set global tidb_index_lookup_concurrency = 16;
set global tidb_index_lookup_join_concurrency = 16;
```
