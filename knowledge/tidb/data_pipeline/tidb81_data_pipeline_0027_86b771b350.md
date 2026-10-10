# TiCDC data integration overview and example targets

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/integration-overview.md`
- Source Title: `Data Integration Overview`
- Source Heading Path: `Data Integration Overview | Data Integration Overview > Integrate with Confluent Cloud and Snowflake | Data Integration Overview > Integrate with Apache Kafka and Apache Flink`
- Source Line Ranges: `5-16`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `shared`, `ecosystem`
- Topic Tags: `data-integration`, `incremental-replication`, `change-data-capture`, `confluent-cloud`, `snowflake`, `kafka`, `flink`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0027_86b771b350`
- Source ID: `tidb-docs-8.1:integration-overview.md#data-integration-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5e177baaf03b8aaa5c2cc08a5d3d55c9c16edf7e6a8c2a4dc6dd5fd76f544228`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/integration-overview#data-integration-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/integration-overview.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an overview of TiCDC data integration options for replicating TiDB incremental data change logs to external platforms and example target combinations.
- Retrieval Keywords: TiCDC data integration overview, replicate TiDB incremental data change logs, incremental data from TiDB, Integrate with Confluent Cloud and Snowflake, Confluent Cloud, Snowflake, ksqlDB, SQL Server, Integrate with Apache Kafka and Apache Flink, Apache Kafka, Apache Flink, data silos
- Follow-up Guidance: The source points to the detailed documents "Integrate with Confluent Cloud and Snowflake" and "Integrate with Apache Kafka and Apache Flink" for those integration paths.
- Classification Note: This is classified as data_pipeline for the ticdc component because the content describes TiCDC replicating TiDB incremental data changes to downstream data platforms.

## Official Source Content

# Data Integration Overview

Data integration means the flow, transfer, and consolidation of data among various data sources. As data grows exponentially in volume and data value is more profoundly explored, data integration has become increasingly popular and urgent. To avoid the situation that TiDB becomes data silos and to integrate data with different platforms, TiCDC offers the capability to replicate TiDB incremental data change logs to other data platforms. This document describes the data integration applications using TiCDC. You can choose an integration solution that suits your business scenarios.
## Integrate with Confluent Cloud and Snowflake

You can use TiCDC to replicate incremental data from TiDB to Confluent Cloud, and replicate the data to Snowflake, ksqlDB, and SQL Server via Confluent Cloud. For details, see [Integrate with Confluent Cloud and Snowflake](https://docs.pingcap.com/tidb/stable/ticdc/integrate-confluent-using-ticdc).
## Integrate with Apache Kafka and Apache Flink

You can use TiCDC to replicate incremental data from TiDB to Apache Kafka, and consume the data using Apache Flink. For details, see [Integrate with Apache Kafka and Apache Flink](https://docs.pingcap.com/tidb/stable/replicate-data-to-kafka).
