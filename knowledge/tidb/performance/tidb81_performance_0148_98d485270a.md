# Performance optimization overview and TiFlash MPP architecture

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0.md`
- Source Title: `What's New in TiDB 5.0`
- Source Heading Path: `What's New in TiDB 5.0 > Performance optimization | What's New in TiDB 5.0 > Performance optimization > MPP architecture`
- Source Line Ranges: `151-173`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`
- Topic Tags: `performance optimization`, `mpp`, `distributed execution`, `analytic queries`, `pushdown`, `join acceleration`, `limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0148_98d485270a`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0.md#performance-optimization`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1bae299f3aa791d3811b8bfe8015269ae302ac0b24038b42482689234bcdcd9e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0#performance-optimization
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching for the TiFlash MPP architecture, how TiDB distributes join computation with `Exchange`, analytic query acceleration, or current MPP feature limitations.
- Retrieval Keywords: MPP architecture, TiFlash MPP, MPP mode, `Exchange` operation, distributed execution, large join queries, aggregation pushdown, analytic queries, calculation cost, reading data from TiKV, table partitioning, Window Function, Collation, OOM spill, Union, Full Outer Join, Use TiFlash
- Follow-up Guidance: The content also enumerates unsupported MPP features including Table partitioning, Window Function, Collation, some built-in functions, Reading data from TiKV, OOM spill, Union, and Full Outer Join.
- Classification Note: This is classified as a performance chunk because it describes TiFlash MPP as a performance optimization for distributed analytic query execution and join acceleration.

## Official Source Content

## Performance optimization
### MPP architecture

[User document](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode)

TiDB introduces the MPP architecture through TiFlash nodes. This architecture allows multiple TiFlash nodes to share the execution workload of large join queries.

When the MPP mode is on, TiDB determines whether to send a query to the MPP engine for computation based on the calculation cost. In the MPP mode, TiDB distributes the computation of table joins to each running TiFlash node by redistributing the join key during data calculation (`Exchange` operation), and thus accelerates the calculation. Furthermore, with the aggregation computing feature that TiFlash has already supported, TiDB can pushdown the computation of a query to the TiFlash MPP cluster. Then the distributed environment can help accelerate the entire execution process and dramatically increase the speed of analytic queries.

In the TPC-H 100 benchmark test, TiFlash MPP delivers significant processing speed over analytic engines of traditional analytic databases and SQL on Hadoop. With this architecture, you can perform large-scale analytic queries directly on the latest transaction data, with a higher performance than traditional offline analytic solutions. According to the benchmark, with the same cluster resource, TiDB 5.0 MPP shows 2 to 3 times of speedup over Greenplum 6.15.0 and Apache Spark 3.1.1, and some queries have 8 times better performance.

Currently, the main features that the MPP mode does not support are as follows (For details, refer to [Use TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode)):

+ Table partitioning
+ Window Function
+ Collation
+ Some built-in functions
+ Reading data from TiKV
+ OOM spill
+ Union
+ Full Outer Join
