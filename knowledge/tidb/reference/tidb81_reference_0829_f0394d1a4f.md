# Serverless billing, RU metering, quotas, and usage behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-faqs.md`
- Source Title: `TiDB Cloud Serverless FAQs`
- Source Heading Path: `TiDB Cloud Serverless FAQs > Billing and metering FAQs | TiDB Cloud Serverless FAQs > Billing and metering FAQs > What are Request Units? | TiDB Cloud Serverless FAQs > Billing and metering FAQs > Is there any free plan available for TiDB Cloud Serverless? | TiDB Cloud Serverless FAQs > Billing and metering FAQs > What are the limitations of the free plan? | TiDB Cloud Serverless FAQs > Billing and metering FAQs > How can I estimate the number of RUs required by my workloads and plan my monthly budget? | TiDB Cloud Serverless FAQs > Billing and metering FAQs > How can I optimize my workload to minimize the number of RUs consumed? | TiDB Cloud Serverless FAQs > Billing and metering FAQs > How storage is metered for TiDB Cloud Serverless？ | TiDB Cloud Serverless FAQs > Billing and metering FAQs > Why does the storage usage size remain unchanged after dropping a table or database immediately? | TiDB Cloud Serverless FAQs > Billing and metering FAQs > Why are there RU consumptions when I'm not actively running any queries? | TiDB Cloud Serverless FAQs > Billing and metering FAQs > Why is there a spike in RU usage when my workload is steady? | TiDB Cloud Serverless FAQs > Billing and metering FAQs > What happens when my cluster exhausts its free quota or exceeds its spending limit? | TiDB Cloud Serverless FAQs > Billing and metering FAQs > Why do I observe spikes in RU usage while importing data?`
- Source Line Ranges: `68-123`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `billing`, `request-units`, `free-plan`, `quotas`, `spending-limit`, `storage-metering`, `ru-optimization`, `background-jobs`, `import-usage`, `flashback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0829_f0394d1a4f`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-faqs.md#billing-and-metering-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6bb809d2c46c57e82efddf95291d74b9199a0edf5eca35a00aa65acb61d55875`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-faqs#billing-and-metering-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-faqs.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB Cloud Serverless billing, Request Units, free-plan quotas and limits, storage metering, unexplained RU usage, spending limits, or import-related RU spikes.
- Retrieval Keywords: Billing and metering FAQs, Request Units, RUs, pay-as-you-go, TiDB Cloud Serverless Pricing Details, free usage quota, 50 million RUs per month, 5 GiB row-based storage, 5 GiB columnar storage, free cluster, scalable cluster, 256 MiB per query, EXPLAIN ANALYZE, RU consumption, egress RUs, Usage this month, spending limit, Diagnosis, SQL Statements, Total RU, Mean RU, Statement Analysis, Optimizing SQL Performance, storage is metered, GiB per month, tables and indexes, excluding data compression or replicas, FLASHBACK TABLE, FLASHBACK DATABASE, background queries, schema changes, loading schemas, automatically analyzing tables, rebuilding statistics, denies any new connection attempts, existing connections remain active but throttled, data import spikes
- Follow-up Guidance: The source refers to EXPLAIN ANALYZE, the Usage this month pane, Diagnosis and Statement Analysis, usage quota documentation, and FLASHBACK TABLE or FLASHBACK DATABASE for related details.
- Classification Note: This is reference content because it defines RU and quota behavior, describes billing and storage measurement, and explains observed usage patterns and connection behavior at quota limits.

## Official Source Content

## Billing and metering FAQs
### What are Request Units?

TiDB Cloud Serverless adopts a pay-as-you-go model, meaning that you only pay for the storage space and cluster usage. In this model, all cluster activities such as SQL queries, bulk operations, and background jobs are quantified in [Request Units (RUs)](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#request-unit). RU is an abstract measurement for the size and intricacy of requests initiated on your cluster. For more information, see [TiDB Cloud Serverless Pricing Details](https://www.pingcap.com/tidb-cloud-serverless-pricing-details/).
### Is there any free plan available for TiDB Cloud Serverless?

For the first five TiDB Cloud Serverless clusters in your organization, TiDB Cloud provides a free usage quota for each of them as follows:

- Row-based storage: 5 GiB
- Columnar storage: 5 GiB
- [Request Units (RUs)](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#request-unit): 50 million RUs per month

If you are using a scalable cluster, usage beyond the free quota will be charged. For a free cluster, once the free quota is reached, the read and write operations on this cluster will be throttled until you upgrade to a scalable cluster or the usage is reset upon the start of a new month.

For more information, see [TiDB Cloud Serverless usage quota](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#usage-quota).
### What are the limitations of the free plan?

Under the free plan, cluster performance is limited due to non-scalable resources. This results in a restriction on memory allocation per query to 256 MiB and might cause observable bottlenecks in request units (RUs) per second. To maximize cluster performance and avoid these limitations, you can upgrade to a [scalable cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#scalable-cluster-plan).
### How can I estimate the number of RUs required by my workloads and plan my monthly budget?

To get the RU consumption of individual SQL statements, you can use the [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze#ru-request-unit-consumption) SQL statement. However, it is important to note that the RUs usage returned in `EXPLAIN ANALYZE` does not incorporate egress RUs, as egress usage is measured separately in the gateway, which is unknown to the TiDB server.

To get the RUs and storage used by your cluster, view the **Usage this month** pane on your cluster overview page. With your past resource usage data and real-time resource usage in this pane, you can track your cluster's resource consumption and estimate a reasonable spending limit. If the free quota cannot meet your requirement, you can upgrade to a [scalable cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#scalable-cluster-plan) and edit the spending limit. For more information, see [TiDB Cloud Serverless usage quota](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#usage-quota).
### How can I optimize my workload to minimize the number of RUs consumed?

Ensure that your queries have been carefully optimized for optimal performance by following the guidelines in [Optimizing SQL Performance](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview). To identify the SQL statements that consume the most RUs, navigate to the [**Diagnosis**](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#view-the-diagnosis-page) page of your cluster, and then check the **SQL Statements** tab, where you can observe SQL execution and view the top statements sorted by **Total RU** or **Mean RU**. For more information, see [Statement Analysis](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#statement-analysis). In addition, minimizing the amount of egress traffic is also crucial for reducing RUs consumption. To achieve this, it is recommended to return only the necessary columns and rows in your query, which in turn helps reduce network egress traffic. This can be achieved by carefully selecting and filtering the columns and rows to be returned, thereby optimizing network utilization.
### How storage is metered for TiDB Cloud Serverless？

The storage is metered based on the amount of data stored in a TiDB Cloud Serverless cluster, measured in GiB per month. It is calculated by multiplying the total size of all the tables and indexes (excluding data compression or replicas) with the number of hours the data is stored in that month.
### Why does the storage usage size remain unchanged after dropping a table or database immediately?

This is because TiDB retains dropped tables and databases for a certain period of time. This retention period ensures that transactions dependent on these tables can continue execution without disruption. Additionally, the retention period makes the [`FLASHBACK TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-table)/[`FLASHBACK DATABASE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-database) feature feasible, which allows you to recover dropped tables and databases if they were mistakenly deleted.
### Why are there RU consumptions when I'm not actively running any queries?

RU consumptions can occur in various scenarios. One common scenario is during background queries, such as synchronizing schema changes between TiDB instances. Another scenario is when certain web console features generate queries, like loading schemas. These processes use RUs even without explicit user triggers.
### Why is there a spike in RU usage when my workload is steady?

A spike in RU usage can occur due to necessary background jobs in TiDB. These jobs, such as automatically analyzing tables and rebuilding statistics, are required for generating optimized query plans.
### What happens when my cluster exhausts its free quota or exceeds its spending limit?

Once a cluster reaches its free quota or spending limit, the cluster immediately denies any new connection attempts until the quota is increased or the usage is reset at the start of a new month. Existing connections established before reaching the quota will remain active but will experience throttling. For more information, see [TiDB Cloud Serverless Limitations and Quotas](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-limitations#usage-quota).
### Why do I observe spikes in RU usage while importing data?

During the data import process of a TiDB Cloud Serverless cluster, RU consumption occurs only when the data is successfully imported, which leads to spikes in RU usage.
