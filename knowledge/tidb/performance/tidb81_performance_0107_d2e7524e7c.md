# DM performance test setup and benchmark schema

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-performance-test.md`
- Source Title: `DM Cluster Performance Test`
- Source Heading Path: `DM Cluster Performance Test | DM Cluster Performance Test > Migration data flow | DM Cluster Performance Test > Deploy test environment | DM Cluster Performance Test > Performance test | DM Cluster Performance Test > Performance test > Table schema`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `tidb`
- Topic Tags: `performance-testing`, `migration-flow`, `environment-deployment`, `table-schema`, `sysbench-benchmark`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0107_d2e7524e7c`
- Source ID: `tidb-docs-8.1:dm/dm-performance-test.md#dm-cluster-performance-test`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c163f49f73bc8d16cfd088bb47eb842484b0baf5594e8fce35dad53f1b5581b5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-performance-test#dm-cluster-performance-test
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-performance-test.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented DM performance test setup, migration data flow, or the benchmark table schema used for testing data migration speed and latency.
- Retrieval Keywords: DM Cluster Performance Test, MySQL -> DM -> TiDB, TiUP, ROW mode for binlog, DM-worker, DM-master, performance test, speed test, latency test, CREATE TABLE `sbtest`, sbtest, k_1, utf8mb4_bin
- Follow-up Guidance: The source also lists the test environment deployment items: deploy the TiDB test cluster using TiUP with default configurations, deploy MySQL with binlog `ROW` mode, and deploy a DM cluster with a DM-worker and a DM-master.
- Classification Note: This is classified as performance content because it defines the benchmark environment, migration flow, and `sbtest` table schema for DM cluster performance testing.

## Official Source Content

# DM Cluster Performance Test

This document describes how to build a test scenario to do a performance test on the DM cluster, including the speed test and latency test regarding data migration.
## Migration data flow

You can use a simple migration data flow, that is, MySQL -> DM -> TiDB, to test the data migration performance of the DM cluster.
## Deploy test environment

- Deploy the TiDB test cluster using TiUP, with all default configurations.
- Deploy the MySQL service. Enable the `ROW` mode for binlog, and use default configurations for other configuration items.
- Deploy a DM cluster, with a DM-worker and a DM-master.
## Performance test
### Table schema

Use tables with the following schema for the performance test:

```sql
CREATE TABLE `sbtest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `k` int(11) NOT NULL DEFAULT '0',
  `c` char(120) CHARSET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '',
  `pad` char(60) CHARSET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `k_1` (`k`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
```
