# HTAP overview, use cases, and architecture

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explore-htap.md`
- Source Title: `Explore HTAP`
- Source Heading Path: `Explore HTAP | Explore HTAP > Use cases | Explore HTAP > Architecture`
- Source Line Ranges: `5-57`
- Source Scope: `all`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `htap`, `use-cases`, `oltp`, `olap`, `hybrid-workload`, `stream-processing`, `data-hub`, `strong-consistency`, `architecture`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0036_eb1f7ee9a6`
- Source ID: `tidb-docs-8.1:explore-htap.md#explore-htap`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e8ee752d937c405f8ea901570c4798da5d882d817b21d5e133c3a89aaa42ad46`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explore-htap#explore-htap
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explore-htap.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for an overview of TiDB HTAP, its typical use cases, or how TiKV and TiFlash work together for strongly consistent OLTP and OLAP.
- Retrieval Keywords: Explore HTAP, TiDB HTAP, Hybrid Transactional and Analytical Processing, hybrid workload, real-time stream processing, data hub, strongly consistent analysis, TiKV, TiFlash, OLTP, OLAP, row-based storage engine, columnar storage engine, replicate data automatically, keep strong consistency, architecture of TiDB HTAP
- Follow-up Guidance: If the user is new to TiDB HTAP and wants to start quickly, the source points to Quick start with HTAP.
- Classification Note: This chunk is classified as architecture because it explains HTAP use cases and the core architecture in which TiKV and TiFlash co-exist with automatic replication and strong consistency.

## Official Source Content

# Explore HTAP

This guide describes how to explore and use the features of TiDB Hybrid Transactional and Analytical Processing (HTAP).

> **Note:**
>
> If you are new to TiDB HTAP and want to start using it quickly, see [Quick start with HTAP](https://docs.pingcap.com/tidb/stable/quick-start-with-htap).
## Use cases

TiDB HTAP can handle the massive data that increases rapidly, reduce the cost of DevOps, and be deployed in either self-hosted or cloud environments easily, which brings the value of data assets in real time.

The following are the typical use cases of HTAP:

- Hybrid workload

    When using TiDB for real-time Online Analytical Processing (OLAP) in hybrid load scenarios, you only need to provide an entry point of TiDB to your data. TiDB automatically selects different processing engines based on the specific business.

- Real-time stream processing

    When using TiDB in real-time stream processing scenarios, TiDB ensures that all the data flowed in constantly can be queried in real time. At the same time, TiDB also can handle highly concurrent data workloads and Business Intelligence (BI) queries.

- Data hub

    When using TiDB as a data hub, TiDB can meet specific business needs by seamlessly connecting the data for the application and the data warehouse.

For more information about use cases of TiDB HTAP, see [blogs about HTAP on the PingCAP website](https://www.pingcap.com/blog/?tag=htap).

To enhance the overall performance of TiDB, it is recommended to use HTAP in the following technical scenarios:

- Improve analytical processing performance

    If your application involves complex analytical queries, such as aggregation and join operations, and these queries are performed on a large amount of data (more than 10 million rows), the row-based storage engine [TiKV](https://docs.pingcap.com/tidb/stable/tikv-overview) might not meet your performance requirements if the tables in these queries cannot effectively use indexes or have low index selectivity.

- Hybrid workload isolation

   While dealing with high-concurrency Online Transactional Processing (OLTP) workloads, your system might also need to handle some OLAP workloads. To ensure the overall system stability, you expect to avoid the impact of OLAP queries on OLTP performance.

- Simplify the ETL technology stack

    When the amount of data to be processed is of medium scale (less than 100 TB), the data processing and scheduling processes are relatively simple, and the concurrency is not high (less than 10), you might want to simplify the technology stack of your system. By replacing multiple different technology stacks used in OLTP, ETL, and OLAP systems with a single database, you can meet the requirements of both transactional systems and analytical systems. This reduces technical complexity and the need for maintenance personnel.

- Strongly consistent analysis

    To achieve real-time, strongly consistent data analysis and calculation, and ensure the analysis results to be completely consistent with the transactional data, you need to avoid data latency and inconsistency issues.
## Architecture

In TiDB, a row-based storage engine [TiKV](https://docs.pingcap.com/tidb/stable/tikv-overview) for Online Transactional Processing (OLTP) and a columnar storage engine [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview) for Online Analytical Processing (OLAP) co-exist, replicate data automatically, and keep strong consistency.

For more information about the architecture, see [architecture of TiDB HTAP](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#architecture).
