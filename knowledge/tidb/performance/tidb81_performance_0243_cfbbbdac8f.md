# YCSB benchmark for optimized large-record workloads

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-performance-tuning-config.md`
- Source Title: `Configure TiDB for Optimal Performance`
- Source Heading Path: `Configure TiDB for Optimal Performance > Benchmark | Configure TiDB for Optimal Performance > Benchmark > YCSB workloads on large record value | Configure TiDB for Optimal Performance > Benchmark > YCSB workloads on large record value > Test environment | Configure TiDB for Optimal Performance > Benchmark > YCSB workloads on large record value > Performance comparison | Configure TiDB for Optimal Performance > Benchmark > YCSB workloads on large record value > Performance analysis | Configure TiDB for Optimal Performance > Benchmark > YCSB workloads on large record value > Test workload`
- Source Line Ranges: `162-212`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`
- Topic Tags: `benchmark`, `ycsb`, `throughput`, `titan`, `compaction`, `large records`, `test environment`, `workload commands`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0243_cfbbbdac8f`
- Source ID: `tidb-docs-8.1:tidb-performance-tuning-config.md#benchmark`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `613a821c4940a4e450407f6f121894f491ee3482d0ab279382a34773dfef36b2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-performance-tuning-config#benchmark
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-performance-tuning-config.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the documented YCSB benchmark setup and measured throughput differences between baseline settings and optimized large-record-value settings using Titan-related tuning.
- Retrieval Keywords: Benchmark, YCSB workloads on large record value, go-ycsb workloada, go-ycsb load mysql, go-ycsb run mysql, Baseline (OPS), Optimized (OPS), Load data 2858.5 5074.3, +77.59%, Workloada 2243.0 12804.3, +470.86%, Titan is enabled by default starting from v7.6.0, min-blob-size, 32KiB, 1KiB, 31KiB, RocksDB compaction exceeds 1 GiB/s, peak throughput remains below 100 MiB/s, 3 TiDB servers, 3 TiKV servers, v8.1.0
- Follow-up Guidance: The chunk includes the exact test environment, the explanation that lowering Titan min-blob-size from 32KiB to 1KiB causes 31KiB records to be stored in Titan, and the full go-ycsb load and run commands.
- Classification Note: This is classified as performance because the content reports benchmark environment, throughput results, and performance analysis for optimized versus baseline settings.

## Official Source Content

## Benchmark 

This section compares performance between default settings (baseline) and optimized settings based on the preceding [key settings for common loads](#key-settings-for-common-workloads).
### YCSB workloads on large record value
#### Test environment

The test environment is as follows:

- 3 TiDB servers (16 cores, 64 GiB)
- 3 TiKV servers (16 cores, 64 GiB)
- TiDB version: v8.1.0
- Workload: [go-ycsb workloada](https://github.com/pingcap/go-ycsb/blob/master/workloads/workloada)
#### Performance comparison

The following table compares throughput (operations per second) between the baseline and optimized settings.

| Item | Baseline (OPS) | Optimized (OPS) | Improvement |
| ---------| ---- | ----| ----|
| Load data | 2858.5 | 5074.3  | +77.59%  |
| Workloada | 2243.0 | 12804.3 | +470.86% |
#### Performance analysis

Titan is enabled by default starting from v7.6.0 and the default `min-blob-size` of Titan in TiDB v8.1.0 is `32KiB`. The baseline configuration uses a record size of `31KiB` to ensure data is stored in RocksDB. In contrast, for the key settings configuration, set `min-blob-size` to `1KiB`, causing data to be stored in Titan.

The performance improvement observed in the key settings is primarily attributed to Titan's ability to reduce RocksDB compactions. As shown in the following figures:

- Baseline: The total throughput of RocksDB compaction exceeds 1 GiB/s, with peaks over 3 GiB/s.
- Key settings: The peak throughput of RocksDB compaction remains below 100 MiB/s.

This significant reduction in compaction overhead contributes to the overall throughput improvement seen in the key settings configuration.

![Titan RocksDB compaction:](/media/performance/titan-rocksdb-compactions.png)
#### Test workload

The following `go-ycsb load` command loads data:

```bash
go-ycsb load mysql -P /ycsb/workloads/workloada -p {host} -p mysql.port={port} -p threadcount=100 -p recordcount=5000000 -p operationcount=5000000 -p workload=core -p requestdistribution=uniform -pfieldcount=31 -p fieldlength=1024
```

The following `go-ycsb run` command runs workload:

```bash
go-ycsb run mysql -P /ycsb/workloads/workloada -p {host} -p mysql.port={port} -p mysql.db=test -p threadcount=100 -p recordcount=5000000 -p operationcount=5000000 -p workload=core -prequestdistribution=uniform -p fieldcount=31 -p fieldlength=1024
```
