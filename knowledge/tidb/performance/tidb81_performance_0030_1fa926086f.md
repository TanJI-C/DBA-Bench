# CH-benCHmark overview and data loading

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-tidb-using-ch.md`
- Source Title: `How to Run CH-benCHmark Test on TiDB`
- Source Heading Path: `How to Run CH-benCHmark Test on TiDB | How to Run CH-benCHmark Test on TiDB > Load data | How to Run CH-benCHmark Test on TiDB > Load data > Load TPC-C data | How to Run CH-benCHmark Test on TiDB > Load data > Load additional tables and views required for TPC-H`
- Source Line Ranges: `5-64`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tiflash`, `tikv`
- Topic Tags: `benchmark`, `ch-benchmark`, `tpcc`, `tpch`, `data-loading`, `validation`, `htap`, `tiflash-replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0030_1fa926086f`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-tidb-using-ch.md#how-to-run-ch-benchmark-test-on-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `867155f9519f0133f1fdc2cb6afb02e59d024c486883d3c1aab2c9ae5c17d70d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-tidb-using-ch#how-to-run-ch-benchmark-test-on-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-tidb-using-ch.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about CH-benCHmark setup on TiDB, including loading TPC-C data, preparing additional TPC-H tables and views, validating loaded data, or installing the bench tool with TiUP.
- Retrieval Keywords: CH-benCHmark, How to Run CH-benCHmark Test on TiDB, TiFlash, HTAP, go-tpc, tiup install bench, TiUP Bench, tiup bench tpcc -H 172.16.5.140 -P 4000 -D tpcc --warehouses 1000 prepare -T 32, tiup bench tpcc --warehouses 1000 check, Load TPC-C data, Load additional tables and views required for TPC-H, tiup bench ch -H 172.16.5.140 -P 4000 -D tpcc prepare, creating nation, creating region, creating supplier, creating view revenue1
- Follow-up Guidance: The same document also includes creating TiFlash replicas and collecting statistics after data loading.
- Classification Note: This is classified as performance because the official content describes running the CH-benCHmark mixed workload and the benchmark data loading and validation process using TiUP Bench.

## Official Source Content

# How to Run CH-benCHmark Test on TiDB

This document describes how to test TiDB using CH-benCHmark.

CH-benCHmark is a mixed workload containing both [TPC-C](http://www.tpc.org/tpcc/) and [TPC-H](http://www.tpc.org/tpch/) tests. It is the most common workload to test HTAP systems. For more information, see [The mixed workload CH-benCHmark](https://research.tableau.com/sites/default/files/a8-cole.pdf).

Before running the CH-benCHmark test, you need to deploy [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview) first, which is a TiDB's HTAP component. After you deploy TiFlash and [create TiFlash replicas](#create-tiflash-replicas), TiKV will replicate the latest data of TPC-C online transactions to TiFlash in real time, and the TiDB optimizer will automatically push down OLAP queries from TPC-H workload to the MPP engine of TiFlash for efficient execution.

The CH-benCHmark test in this document is implemented based on [go-tpc](https://github.com/pingcap/go-tpc). You can download the test program using the following [TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-overview) command:

```shell
tiup install bench
```

For detailed usage of the TiUP Bench component, see [TiUP Bench](https://docs.pingcap.com/tidb/stable/tiup/tiup-bench).
## Load data
### Load TPC-C data

**Loading data is usually the most time-consuming and problematic stage of the entire TPC-C test.**

Taking 1000 warehouses as an example, you can execute the following TiUP command in shell for data load and test. Note that you need to replace `172.16.5.140` and `4000` in this document with your TiDB host and port values.

```shell
tiup bench tpcc -H 172.16.5.140 -P 4000 -D tpcc --warehouses 1000 prepare -T 32
```

Depending on different machine configurations, this loading process might take a few hours. If the cluster size is small, you can use a smaller warehouse value for the test.

After the data is loaded, you can execute the `tiup bench tpcc -H 172.16.5.140 -P 4000 -D tpcc --warehouses 1000 check` command to validate the data correctness.
### Load additional tables and views required for TPC-H

Run the following TiUP command in the shell:

```shell
tiup bench ch -H 172.16.5.140 -P 4000 -D tpcc prepare
```

The following is the log output:

```
creating nation
creating region
creating supplier
generating nation table
generate nation table done
generating region table
generate region table done
generating suppliers table
generate suppliers table done
creating view revenue1
```
