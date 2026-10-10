# TiSpark overview, requirements, and Spark deployment guidance

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tispark-overview.md`
- Source Title: `TiSpark User Guide`
- Source Heading Path: `TiSpark User Guide | TiSpark User Guide > TiSpark vs TiFlash | TiSpark User Guide > Requirements | TiSpark User Guide > Recommended deployment configurations of Spark`
- Source Line Ranges: `6-70`
- Source Scope: `shared`
- Primary Component: `ecosystem`
- Related Components: `pd`, `tikv`, `tidb`, `tiflash`, `tiup`
- Topic Tags: `overview`, `architecture`, `htap`, `compatibility`, `requirements`, `spark`, `deployment`, `deprecated`, `hardware-sizing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0117_bcbae68251`
- Source ID: `tidb-docs-8.1:tispark-overview.md#tispark-user-guide`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fc63bd1411380edcd617cdd8d899e33447c2f3ac714f8510c5f94a8cac314ef5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tispark-overview#tispark-user-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tispark-overview.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs a TiSpark overview, its relationship with TiFlash, compatibility warnings, runtime requirements, or recommended Spark deployment configuration examples.
- Retrieval Keywords: TiSpark User Guide, TiSpark vs TiFlash, TiSpark does not guarantee compatibility with TiDB v7.0.0 and later versions, TiSpark does not guarantee compatibility with Spark v3.4.0 and later versions, TiSpark depends on the TiKV cluster and the PD cluster, Spark Catalyst Engine, index seek, TiDB built-in statistics, HTAP, TiSpark supports Spark >= 2.3, JDK 1.8, Scala 2.11/2.12, YARN, Mesos, Standalone, Deploying TiSpark using TiUP has been deprecated, SPARK_EXECUTOR_MEMORY = 32g, SPARK_WORKER_MEMORY = 32g, SPARK_WORKER_CORES = 8
- Follow-up Guidance: The source also points readers to the Spark official hardware provisioning guidance for detailed hardware recommendations.
- Classification Note: This is classified as architecture because the content explains TiSpark architecture, dependencies, HTAP positioning, and deployment-related requirements and guidance.

## Official Source Content

# TiSpark User Guide

> **Warning:**
>
> - TiSpark does not guarantee compatibility with TiDB v7.0.0 and later versions.
> - TiSpark does not guarantee compatibility with Spark v3.4.0 and later versions.

TiSpark depends on the TiKV cluster and the PD cluster. You also need to set up a Spark cluster. This document provides a brief introduction to how to setup and use TiSpark. It requires some basic knowledge of Apache Spark. For more information, see [Apache Spark website](https://spark.apache.org/docs/latest/index.html).

Deeply integrating with Spark Catalyst Engine, TiSpark provides precise control on computing. This allows Spark to read data from TiKV efficiently. TiSpark also supports index seek, which enables high-speed point query. TiSpark accelerates data queries by pushing computing to TiKV so as to reduce the volume of data to be processed by Spark SQL. Meanwhile, TiSpark can use TiDB built-in statistics to select the best query plan.

With TiSpark and TiDB, you can run both transaction and analysis tasks on the same platform without building and maintaining ETLs. This simplifies the system architecture and reduces the cost of maintenance.

You can use tools of the Spark ecosystem for data processing on TiDB:

- TiSpark: Data analysis and ETLs
- TiKV: Data retrieval
- Scheduling system: Report generation

Also, TiSpark supports distributed writes to TiKV. Compared with writes to TiDB by using Spark and JDBC, distributed writes to TiKV can implement transactions (either all data are written successfully or all writes fail), and the writes are faster.

> **Warning:**
>
> Because TiSpark accesses TiKV directly, the access control mechanisms used by TiDB Server are not applicable to TiSpark. Since TiSpark v2.5.0, TiSpark supports user authentication and authorization, for more information, see [Security](https://docs.pingcap.com/tidb/stable/tispark-overview#security).

The following diagram shows the architecture of TiSpark.

![TiSpark architecture](/media/tispark-architecture.png)
## TiSpark vs TiFlash

[TiSpark](https://github.com/pingcap/tispark) is a thin layer built for running Apache Spark on top of TiDB/TiKV to answer complex OLAP queries. It takes advantage of both the Spark platform and the distributed TiKV cluster and seamlessly integrates with TiDB, the distributed OLTP database, to provide a Hybrid Transactional/Analytical Processing (HTAP) solution to serve as a one-stop solution for both online transactions and analysis.

[TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview) is another tool that enables HTAP. Both TiFlash and TiSpark allow the use of multiple hosts to execute OLAP queries on OLTP data. TiFlash stores data in a columnar format, which allows more efficient analytical queries. TiFlash and TiSpark can be used together.
## Requirements

+ TiSpark supports Spark >= 2.3.
+ TiSpark requires JDK 1.8 and Scala 2.11/2.12.
+ TiSpark runs in any Spark mode such as `YARN`, `Mesos`, and `Standalone`.
## Recommended deployment configurations of Spark

> **Warning:**
>
> Deploying TiSpark using TiUP as described in this [doc](https://docs.pingcap.com/tidb/stable/tispark-deployment-topology) has been deprecated.

Since TiSpark is a TiDB connector of Spark, to use it, a running Spark cluster is required.

This document provides basic advice on deploying Spark. Please turn to the [Spark official website](https://spark.apache.org/docs/latest/hardware-provisioning.html) for detailed hardware recommendations.

For independent deployment of Spark cluster:

+ It is recommended to allocate 32 GB memory for Spark. Reserve at least 25% of the memory for the operating system and the buffer cache.
+ It is recommended to provision at least 8 to 16 cores per machine for Spark. First, you must assign all the CPU cores to Spark.

The following is an example based on the `spark-env.sh` configuration:

```
SPARK_EXECUTOR_MEMORY = 32g
SPARK_WORKER_MEMORY = 32g
SPARK_WORKER_CORES = 8
```
