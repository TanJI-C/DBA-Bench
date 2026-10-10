# Serverless usage quota and quota behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-limitations.md`
- Source Title: `TiDB Cloud Serverless Limitations and Quotas`
- Source Heading Path: `TiDB Cloud Serverless Limitations and Quotas > Usage quota`
- Source Line Ranges: `60-78`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `quotas`, `free-tier`, `scalable-clusters`, `request-units`, `billing`, `throttling`, `connections`, `spending-limit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0832_a16aae469d`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-limitations.md#usage-quota`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9b5a3a7295e8b9a169baea8e31a1f27b7250da9e48160191723b82c3fc4b09fe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-limitations#usage-quota
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-limitations.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB Cloud Serverless usage quotas, free cluster limits, Request Units, spending limits, or what happens after a cluster reaches its quota.
- Retrieval Keywords: TiDB Cloud Serverless usage quota, maximum of five free clusters, free cluster plan, scalable cluster plan, Row-based storage 5 GiB, Columnar storage 5 GiB, 50 million RUs per month, Request Units RU, billing unit, reaches its usage quota denies new connection attempts, existing connections remain active but will experience throttling, increase the quota, update spending limit, Manage Spending Limit for TiDB Cloud Serverless Clusters
- Follow-up Guidance: The content points to create a scalable cluster and edit the spending limit during creation or later on the cluster overview page for additional quota.
- Classification Note: This is reference content because it defines quota amounts, the RU concept, organization cluster limits, and the documented quota behavior for connections and throttling.

## Official Source Content

## Usage quota

For each organization in TiDB Cloud, you can create a maximum of five [free clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#free-cluster-plan) by default. To create more TiDB Cloud Serverless clusters, you need to add a credit card and create [scalable clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#scalable-cluster-plan) for the usage.

For the first five TiDB Cloud Serverless clusters in your organization, whether they are free or scalable, TiDB Cloud provides a free usage quota for each of them as follows:

- Row-based storage: 5 GiB
- Columnar storage: 5 GiB
- [Request Units (RUs)](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#request-unit): 50 million RUs per month

The Request Unit (RU) is a unit of measurement used to track the resource consumption of a query or transaction. It is a metric that allows you to estimate the computational resources required to process a specific request in the database. The request unit is also the billing unit for TiDB Cloud Serverless service.

Once a cluster reaches its usage quota, it immediately denies any new connection attempts until you [increase the quota](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-serverless-spend-limit#update-spending-limit) or the usage is reset upon the start of a new month. Existing connections established before reaching the quota will remain active but will experience throttling.

To learn more about the RU consumption of different resources (including read, write, SQL CPU, and network egress), the pricing details, and the throttled information, see [TiDB Cloud Serverless Pricing Details](https://www.pingcap.com/tidb-cloud-serverless-pricing-details).

If you want to create a TiDB Cloud Serverless cluster with an additional quota, you can select the scalable cluster plan and edit the spending limit on the cluster creation page. For more information, see [Create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless).

After creating a TiDB Cloud Serverless cluster, you can still check and edit the spending limit on your cluster overview page. For more information, see [Manage Spending Limit for TiDB Cloud Serverless Clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-serverless-spend-limit).
