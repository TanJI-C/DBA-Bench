# Serverless general FAQs and columnar storage basics

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-faqs.md`
- Source Title: `TiDB Cloud Serverless FAQs`
- Source Heading Path: `TiDB Cloud Serverless FAQs | TiDB Cloud Serverless FAQs > General FAQs | TiDB Cloud Serverless FAQs > General FAQs > What is TiDB Cloud Serverless? | TiDB Cloud Serverless FAQs > General FAQs > How do I get started with TiDB Cloud Serverless? | TiDB Cloud Serverless FAQs > General FAQs > How many TiDB Cloud Serverless clusters can I create in TiDB Cloud? | TiDB Cloud Serverless FAQs > General FAQs > Are all TiDB Cloud features fully supported on TiDB Cloud Serverless? | TiDB Cloud Serverless FAQs > General FAQs > When will TiDB Cloud Serverless be available on cloud platforms other than AWS, such as Google Cloud or Azure? | TiDB Cloud Serverless FAQs > General FAQs > I created a Developer Tier cluster before TiDB Cloud Serverless was available. Can I still use my cluster? | TiDB Cloud Serverless FAQs > General FAQs > What is columnar storage in TiDB Cloud Serverless? | TiDB Cloud Serverless FAQs > General FAQs > When should I use columnar storage in TiDB Cloud Serverless? | TiDB Cloud Serverless FAQs > General FAQs > How to use columnar storage in TiDB Cloud Serverless?`
- Source Line Ranges: `6-67`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tiflash`
- Topic Tags: `serverless`, `getting-started`, `cluster-limits`, `feature-support`, `cloud-platforms`, `developer-tier-migration`, `columnar-storage`, `htap`, `tiflash-replicas`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0828_2254914c5f`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-faqs.md#tidb-cloud-serverless-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `92881efd826582929b38846fe78e0ce56d5b739f22c65dd161fa5135f68e10fc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-faqs#tidb-cloud-serverless-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-faqs.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for TiDB Cloud Serverless basics, cluster count limits, feature support status, Developer Tier migration, or how columnar storage and TiFlash replicas work in Serverless.
- Retrieval Keywords: TiDB Cloud Serverless, full HTAP capabilities, fully managed auto-scaling deployment, TiDB Cloud Quick Start, maximum of five free clusters, scalable clusters, Serverless Limitations and Quotas, Developer Tier cluster automatically migrated, columnar storage, row-based storage, strong consistency, Hybrid Transactional and Analytical Processing, HTAP, TiFlash engine, optimizer automatically decide, TiFlash replica, table level, database level, Create TiFlash replicas
- Follow-up Guidance: For setup details, the source points to TiDB Cloud Quick Start, TiDB Cloud Serverless Limitations and Quotas, and Create TiFlash replicas.
- Classification Note: This is reference content because it answers FAQ-style questions about TiDB Cloud Serverless behavior, limits, availability notes, and columnar storage concepts without providing a procedural workflow.

## Official Source Content

# TiDB Cloud Serverless FAQs

This document lists the most frequently asked questions about TiDB Cloud Serverless.
## General FAQs
### What is TiDB Cloud Serverless?

TiDB Cloud Serverless offers the TiDB database with full HTAP capabilities for you and your organization. It is a fully managed, auto-scaling deployment of TiDB that lets you start using your database immediately, develop and run your application without caring about the underlying nodes, and automatically scale based on your application's workload changes.
### How do I get started with TiDB Cloud Serverless?

Get started with the 5-minute [TiDB Cloud Quick Start](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-quickstart).
### How many TiDB Cloud Serverless clusters can I create in TiDB Cloud?

For each organization in TiDB Cloud, you can create a maximum of five [free clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#free-cluster-plan) by default. To create more TiDB Cloud Serverless clusters, you need to add a credit card and create [scalable clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#scalable-cluster-plan) for the usage.
### Are all TiDB Cloud features fully supported on TiDB Cloud Serverless?

Some of TiDB Cloud features are partially supported or not supported on TiDB Cloud Serverless. For more information, see [TiDB Cloud Serverless Limitations and Quotas](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-limitations).
### When will TiDB Cloud Serverless be available on cloud platforms other than AWS, such as Google Cloud or Azure?

We are actively working on expanding TiDB Cloud Serverless to other cloud platforms, including Google Cloud and Azure. However, we do not have an exact timeline for now as we currently focus on filling gaps and ensuring seamless functionality across all environments. Rest assured, we are working hard to make TiDB Cloud Serverless available on more cloud platforms, and we will keep our community updated as we progress.
### I created a Developer Tier cluster before TiDB Cloud Serverless was available. Can I still use my cluster?

Yes, your Developer Tier cluster has been automatically migrated to the TiDB Cloud Serverless cluster, providing you with an improved user experience without any disruptions to your prior usage.
### What is columnar storage in TiDB Cloud Serverless?

Columnar storage in TiDB Cloud Serverless acts as an additional replica of row-based storage, ensuring strong consistency. Unlike traditional row-based storage, which stores data in rows, columnar storage organizes data in columns, optimizing it for data analytics tasks.

Columnar storage is a key feature that enables the Hybrid Transactional and Analytical Processing (HTAP) capabilities of TiDB by seamlessly blending transactional and analytical workloads.

To efficiently manage columnar storage data, TiDB Cloud Serverless uses a separate elastic TiFlash engine. During query execution, the optimizer guides the cluster to automatically decide whether to retrieve data from row-based or columnar storage.
### When should I use columnar storage in TiDB Cloud Serverless?

Consider using columnar storage in TiDB Cloud Serverless in the following scenarios:

- Your workload involves analytical tasks that require efficient data scanning and aggregation.
- You prioritize improved performance, especially for analytics workloads.
- You want to isolate analytical processing from transactional processing to prevent performance impact on your transactional processing (TP) workload. The separate columnar storage helps optimize these distinct workload patterns.

In these scenarios, columnar storage can significantly improve query performance and provide a seamless experience for mixed workloads in your system.
### How to use columnar storage in TiDB Cloud Serverless?

Using columnar storage in TiDB Cloud Serverless is similar to using it in TiFlash. You can enable columnar storage at both the table and database levels:

- Table level: Assign a TiFlash replica to a table to enable columnar storage for that specific table.
- Database level: Configure TiFlash replicas for all tables in a database to use columnar storage across the entire database.

Once a TiFlash replica is set up for a table, TiDB automatically replicates data from the row-based storage to the columnar storage for that table. This ensures data consistency and optimizes performance for analytical queries.

For more information about how to set up TiFlash replicas, see [Create TiFlash replicas](https://docs.pingcap.com/tidb/stable/tiflash/create-tiflash-replicas).
