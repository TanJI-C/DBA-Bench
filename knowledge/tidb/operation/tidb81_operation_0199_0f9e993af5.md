# HTAP quick start concepts and environment setup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/quick-start-with-htap.md`
- Source Title: `Quick start with HTAP`
- Source Heading Path: `Quick Start Guide for TiDB HTAP | Quick Start Guide for TiDB HTAP > Basic concepts | Quick Start Guide for TiDB HTAP > Steps | Quick Start Guide for TiDB HTAP > Steps > Step 1. Deploy a local test environment | Quick Start Guide for TiDB HTAP > Steps > Step 2. Prepare test data`
- Source Line Ranges: `5-103`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiup`, `tidb`
- Topic Tags: `htap`, `concepts`, `tikv`, `tiflash`, `mpp`, `test-environment`, `deployment`, `tpch`, `data-generation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0199_0f9e993af5`
- Source ID: `tidb-docs-8.1:quick-start-with-htap.md#quick-start-guide-for-tidb-htap`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f2aa983e641ca3ed9ca82e468fe88bd03d4f0ff39d1ebc0bbe9ae4e61aa03b7b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/quick-start-with-htap#quick-start-guide-for-tidb-htap
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/quick-start-with-htap.md

## Retrieval Guidance

- Use When: Use this chunk when the request is about TiDB HTAP basic concepts, setting up a local test environment with TiUP playground, or preparing TPC-H test data and verifying the generated tables in the test schema.
- Retrieval Keywords: Hybrid Transactional and Analytical Processing, HTAP, TiKV, TiFlash, MPP, tiup playground, Quick Start Guide for the TiDB Database Platform, TPC-H, tiup install bench, tiup bench tpch --sf=1 prepare, information_schema.TABLES, table_schema='test', test.nation, test.region, test.part, test.supplier, test.partsupp, test.customer, test.orders, test.lineitem, Finished
- Follow-up Guidance: The next steps in the source query data with the row-based storage engine and then replicate specific tables to TiFlash for HTAP analysis.
- Classification Note: This chunk is classified as operation because the official content introduces HTAP concepts and gives test-environment deployment and data-preparation commands and SQL for a local self-managed setup.

## Official Source Content

# Quick Start Guide for TiDB HTAP

This guide walks you through the quickest way to get started with TiDB's one-stop solution of Hybrid Transactional and Analytical Processing (HTAP).

> **Note:**
>
> The steps provided in this guide is ONLY for quick start in the test environment. For production environments, [explore HTAP](https://docs.pingcap.com/tidb/stable/explore-htap) is recommended.
## Basic concepts

Before using TiDB HTAP, you need to have some basic knowledge about [TiKV](https://docs.pingcap.com/tidb/stable/tikv-overview), a row-based storage engine for TiDB Online Transactional Processing (OLTP), and [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview), a columnar storage engine for TiDB Online Analytical Processing (OLAP).

- Storage engines of HTAP: The row-based storage engine and the columnar storage engine co-exist for HTAP. Both storage engines can replicate data automatically and keep strong consistency. The row-based storage engine optimizes OLTP performance, and the columnar storage engine optimizes OLAP performance.
- Data consistency of HTAP: As a distributed and transactional key-value database, TiKV provides transactional interfaces with ACID compliance, and guarantees data consistency between multiple replicas and high availability with the implementation of the [Raft consensus algorithm](https://raft.github.io/raft.pdf). As a columnar storage extension of TiKV, TiFlash replicates data from TiKV in real time according to the Raft Learner consensus algorithm, which ensures that data is strongly consistent between TiKV and TiFlash.
- Data isolation of HTAP: TiKV and TiFlash can be deployed on different machines as needed to solve the problem of HTAP resource isolation.
- MPP computing engine: [MPP](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode#control-whether-to-select-the-mpp-mode) is a distributed computing framework provided by the TiFlash engine since TiDB 5.0, which allows data exchange between nodes and provides high-performance, high-throughput SQL algorithms. In the MPP mode, the run time of the analytic queries can be significantly reduced.
## Steps

In this document, you can experience the convenience and high performance of TiDB HTAP by querying an example table in a [TPC-H](http://www.tpc.org/tpch/) dataset. TPC-H is a popular decision support benchmark that consists of a suite of business oriented ad-hoc queries with large volumes of data and a high degree of complexity. To experience 22 complete SQL queries using TPC-H, visit [tidb-bench repo](https://github.com/pingcap/tidb-bench/tree/master/tpch/queries) or [TPC-H](http://www.tpc.org/tpch/) for instructions on how to generate query statements and data.
### Step 1. Deploy a local test environment

Before using TiDB HTAP, follow the steps in the [Quick Start Guide for the TiDB Database Platform](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb) to prepare a local test environment, and run the following command to deploy a TiDB cluster:

```shell
tiup playground
```

> **Note:**
>
> `tiup playground` command is ONLY for quick start, NOT for production.
### Step 2. Prepare test data

In the following steps, you can create a [TPC-H](http://www.tpc.org/tpch/) dataset as the test data to use TiDB HTAP. If you are interested in TPC-H, see [General Implementation Guidelines](http://tpc.org/tpc_documents_current_versions/pdf/tpc-h_v3.0.0.pdf).

> **Note:**
>
> If you want to use your existing data for analytic queries, you can [migrate your data to TiDB](https://docs.pingcap.com/tidb/stable/migration-overview). If you want to design and create your own test data, you can create it by executing SQL statements or using related tools.

1. Install the test data generation tool by running the following command:

    ```shell
    tiup install bench
    ```

2. Generate the test data by running the following command:

    ```shell
    tiup bench tpch --sf=1 prepare
    ```

    If the output of this command shows `Finished`, it indicates that the data is created.

3. Execute the following SQL statement to view the generated data:

    ```sql
    SELECT
      CONCAT(table_schema,'.',table_name) AS 'Table Name',
      table_rows AS 'Number of Rows',
      FORMAT_BYTES(data_length) AS 'Data Size',
      FORMAT_BYTES(index_length) AS 'Index Size',
      FORMAT_BYTES(data_length+index_length) AS'Total'
    FROM
      information_schema.TABLES
    WHERE
      table_schema='test';
    ```

    As you can see from the output, eight tables are created in total, and the largest table has 6.5 million rows (the number of rows created by the tool depends on the actual SQL query result because the data is randomly generated).

    ```sql
    +---------------+----------------+-----------+------------+-----------+
    |  Table Name   | Number of Rows | Data Size | Index Size |   Total   |
    +---------------+----------------+-----------+------------+-----------+
    | test.nation   |             25 | 2.44 KiB  | 0 bytes    | 2.44 KiB  |
    | test.region   |              5 | 416 bytes | 0 bytes    | 416 bytes |
    | test.part     |         200000 | 25.07 MiB | 0 bytes    | 25.07 MiB |
    | test.supplier |          10000 | 1.45 MiB  | 0 bytes    | 1.45 MiB  |
    | test.partsupp |         800000 | 120.17 MiB| 12.21 MiB  | 132.38 MiB|
    | test.customer |         150000 | 24.77 MiB | 0 bytes    | 24.77 MiB |
    | test.orders   |        1527648 | 174.40 MiB| 0 bytes    | 174.40 MiB|
    | test.lineitem |        6491711 | 849.07 MiB| 99.06 MiB  | 948.13 MiB|
    +---------------+----------------+-----------+------------+-----------+
    8 rows in set (0.06 sec)
    ```

    This is a database of a commercial ordering system. In which, the `test.nation` table indicates the information about countries, the `test.region` table indicates the information about regions, the `test.part` table indicates the information about parts, the `test.supplier` table indicates the information about suppliers, the `test.partsupp` table indicates the information about parts of suppliers, the `test.customer` table indicates the information about customers, the `test.customer` table indicates the information about orders, and the `test.lineitem` table indicates the information about online items.
