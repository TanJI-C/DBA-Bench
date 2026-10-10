# Prepare TiFlash and process HTAP workloads

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explore-htap.md`
- Source Title: `Explore HTAP`
- Source Heading Path: `Explore HTAP > Environment preparation | Explore HTAP > Data preparation | Explore HTAP > Data processing`
- Source Line Ranges: `58-97`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `tiup`
- Topic Tags: `deployment`, `environment-preparation`, `tiflash`, `tispark`, `scaling`, `replication`, `data-migration`, `mpp`, `optimizer`, `sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0137_d6e360b0d1`
- Source ID: `tidb-docs-8.1:explore-htap.md#environment-preparation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `431e6f050e95a3484da50e79994634174e004b0b765d19fb5bf77e5ca4b83727`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explore-htap#environment-preparation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explore-htap.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to prepare TiFlash for HTAP, how table replication to TiFlash starts, or how TiDB chooses and controls TiFlash MPP execution.
- Retrieval Keywords: Environment preparation, Data preparation, Data processing, TiFlash, TiSpark, MPP, Massively Parallel Processing, Scale out a TiFlash cluster, Deploy a TiDB Cluster using TiUP, topology of TiFlash, data migration, Use TiFlash, TiFlash replicas, tidb_allow_mpp, tidb_enforce_mpp, EXPLAIN, ExchangeSender, ExchangeReceiver, front-end optimizer
- Follow-up Guidance: The source says to use EXPLAIN Statements in the MPP Mode to verify MPP, and that ExchangeSender and ExchangeReceiver in EXPLAIN output indicate MPP is in use.
- Classification Note: This chunk is classified as operation because it covers deployment preparation, manual TiFlash replica setup, data migration context, and execution behavior settings for TiFlash MPP.

## Official Source Content

## Environment preparation

Before exploring the features of TiDB HTAP, you need to deploy TiDB and the corresponding storage engines according to the data volume. If the data volume is large (for example, 100 T), it is recommended to use TiFlash Massively Parallel Processing (MPP) as the primary solution and TiSpark as the supplementary solution.

- TiFlash

    - If you have deployed a TiDB cluster with no TiFlash node, add the TiFlash nodes in the current TiDB cluster. For detailed information, see [Scale out a TiFlash cluster](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-out-a-tiflash-cluster).
    - If you have not deployed a TiDB cluster, see [Deploy a TiDB Cluster using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup). Based on the minimal TiDB topology, you also need to deploy the [topology of TiFlash](https://docs.pingcap.com/tidb/stable/tiflash-deployment-topology).
    - When deciding how to choose the number of TiFlash nodes, consider the following scenarios:

        - If your use case requires OLTP with small-scale analytical processing and Ad-Hoc queries, deploy one or several TiFlash nodes. They can dramatically increase the speed of analytic queries.
        - If the OLTP throughput does not cause significant pressure to I/O usage rate of the TiFlash nodes, each TiFlash node uses more resources for computation, and thus the TiFlash cluster can have near-linear scalability. The number of TiFlash nodes should be tuned based on expected performance and response time.
        - If the OLTP throughput is relatively high (for example, the write or update throughput is higher than 10 million lines/hours), due to the limited write capacity of network and physical disks, the I/O between TiKV and TiFlash becomes a bottleneck and is also prone to read and write hotspots. In this case, the number of TiFlash nodes has a complex non-linear relationship with the computation volume of analytical processing, so you need to tune the number of TiFlash nodes based on the actual status of the system.

- TiSpark

    - If your data needs to be analyzed with Spark, deploy TiSpark. For specific process, see [TiSpark User Guide](https://docs.pingcap.com/tidb/stable/tispark-overview).

<!--    - Real-time stream processing
  - If you want to build an efficient and easy-to-use real-time data warehouse with TiDB and Flink, you are welcome to participate in Apache Flink x TiDB meetups.-->
## Data preparation

After TiFlash is deployed, TiKV does not replicate data to TiFlash automatically. You need to manually specify which tables need to be replicated to TiFlash. After that, TiDB creates the corresponding TiFlash replicas.

- If there is no data in the TiDB Cluster, migrate the data to TiDB first. For detailed information, see [data migration](https://docs.pingcap.com/tidb/stable/migration-overview).
- If the TiDB cluster already has the replicated data from upstream, after TiFlash is deployed, data replication does not automatically begin. You need to manually specify the tables to be replicated to TiFlash. For detailed information, see [Use TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#use-tiflash).
## Data processing

With TiDB, you can simply enter SQL statements for query or write requests. For the tables with TiFlash replicas, TiDB uses the front-end optimizer to automatically choose the optimal execution plan.

> **Note:**
>
> The MPP mode of TiFlash is enabled by default. When an SQL statement is executed, TiDB automatically determines whether to run in the MPP mode through the optimizer.
>
> - To disable the MPP mode of TiFlash, set the value of the [tidb_allow_mpp](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_mpp-new-in-v50) system variable to `OFF`.
> - To forcibly enable MPP mode of TiFlash for query execution, set the values of [tidb_allow_mpp](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_mpp-new-in-v50) and [tidb_enforce_mpp](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enforce_mpp-new-in-v51) to `ON`.
> - To check whether TiDB chooses the MPP mode to execute a specific query, see [Explain Statements in the MPP Mode](https://docs.pingcap.com/tidb/stable/explain-mpp#explain-statements-in-the-mpp-mode). If the output of `EXPLAIN` statement includes the `ExchangeSender` and `ExchangeReceiver` operators, the MPP mode is in use.
