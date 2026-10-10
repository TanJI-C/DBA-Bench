# Data Migration RCU specifications and performance limits

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-billing-dm.md`
- Source Title: `Data Migration Billing`
- Source Heading Path: `Data Migration Billing | Data Migration Billing > Specifications for Data Migration`
- Source Line Ranges: `5-33`
- Source Scope: `cloud`
- Primary Component: `dm`
- Related Components: `cloud`
- Topic Tags: `billing`, `rcu`, `specifications`, `full-migration`, `incremental-migration`, `performance`, `table-limits`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0900_194f220ca5`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-billing-dm.md#data-migration-billing`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `004109527f007815c5fcc9407d86efebecb199e5050e1643658cee390ec08bf8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing-dm#data-migration-billing
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-billing-dm.md

## Retrieval Guidance

- Use When: Use this chunk when comparing Data Migration RCU specifications by full data migration throughput, incremental data migration throughput, and maximum number of tables in TiDB Cloud billing documentation.
- Retrieval Keywords: Data Migration Billing, Specifications for Data Migration, Replication Capacity Units, RCUs, 2 RCUs, 4 RCUs, 8 RCUs, 16 RCUs, Full data migration, Incremental data migration, Maximum number of tables, 25 MiB/s, 35 MiB/s, 40 MiB/s, 45 MiB/s, 10,000 rows/s, 20,000 rows/s, 40,000 rows/s, 80,000 rows/s, 500 tables, 10000 tables, 30000 tables, 60000 tables, job could become unstable or even fail, MiB/s, rows/s, INSERT, UPDATE, DELETE, Data Migration Cost
- Follow-up Guidance: For pricing of Data Migration RCUs, the source points to the Data Migration Cost page.
- Classification Note: This is reference content because it defines Data Migration capacity in RCUs and lists specification limits, throughput figures, units, and table-count constraints.

## Official Source Content

# Data Migration Billing

This document describes the billing for Data Migration in TiDB Cloud.
## Specifications for Data Migration

TiDB Cloud measures the capacity of Data Migration in Replication Capacity Units (RCUs). When you create a Data Migration job, you can select an appropriate specification. The higher the RCU, the better the migration performance. You will be charged for these Data Migration RCUs.

The following table lists the corresponding performance and the maximum number of tables that each Data Migration specification can migrate.

| Specification | Full data migration | Incremental data migration | Maximum number of tables |
|---------------|---------------------|----------------------------|-----------------------|
| 2 RCUs  | 25 MiB/s | 10,000 rows/s | 500   |
| 4 RCUs  | 35 MiB/s | 20,000 rows/s | 10000 |
| 8 RCUs  | 40 MiB/s | 40,000 rows/s | 30000 |
| 16 RCUs | 45 MiB/s | 80,000 rows/s | 60000 |

For more information about the prices of Data Migration RCUs, see [Data Migration Cost](https://www.pingcap.com/tidb-dedicated-pricing-details/#dm-cost).

> **Note:**
>
> - If the number of tables to be migrated exceeds the maximum number of tables, the Data Migration job might still run, but the job could become unstable or even fail.
> - All the performance values in this table are maximum and optimal ones. It is assumed that there are no performance, network bandwidth, or other bottlenecks in the upstream and downstream databases. The performance values are for reference only and might vary in different scenarios.

The Data Migration job measures full data migration performance in MiB/s. This unit indicates the amount of data (in MiB) that is migrated per second by the Data Migration job.

The Data Migration job measures incremental data migration performance in rows/s. This unit indicates the number of rows that are migrated to the target database per second. For example, if the upstream database executes `INSERT`, `UPDATE`, or `DELETE` statements of 10,000 rows in about 1 second, the Data Migration job of the corresponding specification can replicate the 10,000 rows to the downstream in about 1 second.
