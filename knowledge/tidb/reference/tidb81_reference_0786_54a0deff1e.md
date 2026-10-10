# Pulsar changefeed overview and restrictions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-apache-pulsar.md`
- Source Title: `Sink to Apache Pulsar`
- Source Heading Path: `Sink to Apache Pulsar | Sink to Apache Pulsar > Restrictions`
- Source Line Ranges: `5-22`
- Source Scope: `cloud`
- Primary Component: `ticdc`
- Related Components: `cloud`
- Topic Tags: `changefeed`, `pulsar`, `restrictions`, `version`, `tls`, `duplicates`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0786_54a0deff1e`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-apache-pulsar.md#sink-to-apache-pulsar`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2994562cd1b24122d369531eee5a910b50ca20ccf9df202f7e2a6204279d6b8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-pulsar#sink-to-apache-pulsar
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-apache-pulsar.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether TiDB Cloud supports creating a changefeed to Apache Pulsar and what built-in restrictions apply.
- Retrieval Keywords: Sink to Apache Pulsar, Restrictions, TiDB Cloud Dedicated cluster version v7.5.1 or later, TiDB Cloud Serverless clusters changefeed feature is unavailable, up to 100 changefeeds, self-signed TLS certificates, TiCDC restrictions as TiCDC unsupported scenarios, primary key or non-null unique index, duplicated data inserted downstream, TiCDC does not automatically create Pulsar topics
- Follow-up Guidance: If topic creation or connectivity setup is needed, the document also includes prerequisites for network, ACL authorization, and manual topic creation in Apache Pulsar.
- Classification Note: This is reference content because it lists support scope and restrictions for TiDB Cloud changefeeds to Apache Pulsar, including version, cluster tier, TLS, TiCDC limitations, duplicate-risk conditions, and topic creation behavior.

## Official Source Content

# Sink to Apache Pulsar

This document describes how to create a changefeed to stream data from TiDB Cloud to Apache Pulsar.

> **Note:**
>
> - To replicate data to Apache Pulsar using the changefeed feature, make sure that your TiDB Cloud Dedicated cluster version is v7.5.1 or later.
> - For [TiDB Cloud Serverless clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless), the changefeed feature is unavailable.
## Restrictions

- For each TiDB Cloud cluster, you can create up to 100 changefeeds.
- Currently, TiDB Cloud does not support uploading self-signed TLS certificates to connect to Pulsar brokers.
- Because TiDB Cloud uses TiCDC to establish changefeeds, it has the same [restrictions as TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview#unsupported-scenarios).
- If the table to be replicated does not have a primary key or a non-null unique index, the absence of a unique constraint during replication could result in duplicated data being inserted downstream in some retry scenarios.
- Currently, TiCDC does not automatically create Pulsar topics. Before dispatching events to a topic, ensure the topic exists in Pulsar.
