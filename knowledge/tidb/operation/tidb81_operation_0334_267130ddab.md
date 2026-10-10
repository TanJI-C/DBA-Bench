# TiDB Cloud Serverless spending limits, usage quota, and update steps

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/manage-serverless-spend-limit.md`
- Source Title: `Manage Spending Limit for TiDB Cloud Serverless Scalable Clusters`
- Source Heading Path: `Manage Spending Limit for TiDB Cloud Serverless Scalable Clusters | Manage Spending Limit for TiDB Cloud Serverless Scalable Clusters > Usage quota | Manage Spending Limit for TiDB Cloud Serverless Scalable Clusters > Update spending limit`
- Source Line Ranges: `5-47`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `spending-limit`, `usage-quota`, `serverless`, `scalable-clusters`, `billing`, `cost-control`, `cluster-upgrade`, `payment-method`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0334_267130ddab`
- Source ID: `tidb-docs-8.1:tidb-cloud/manage-serverless-spend-limit.md#manage-spending-limit-for-tidb-cloud-serverless-scalable-clusters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0bb685faaac2dd321039fa15391025fc54a564e66a0d57c5cbde4ce68989390d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-serverless-spend-limit#manage-spending-limit-for-tidb-cloud-serverless-scalable-clusters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/manage-serverless-spend-limit.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Cloud Serverless scalable cluster spending limits, free usage quota, quota enforcement behavior, or the UI steps to upgrade or edit the monthly spending limit.
- Retrieval Keywords: TiDB Cloud Serverless scalable clusters, spending limit, usage quota, Update spending limit, Usage This Month, Upgrade to Scalable Cluster, Edit, Update Cluster Plan, free clusters, credit card, payment method, Request Units (RUs), 50 million RUs per month, Row-based storage 5 GiB, Columnar storage 5 GiB, new connection attempts denied, existing connections remain active but throttled
- Follow-up Guidance: The source also points to TiDB Cloud Serverless Pricing Details for RU consumption, pricing details, and throttled information.
- Classification Note: This is classified as a cloud operation topic because the content describes TiDB Cloud Serverless quota limits, billing-related constraints, and console steps for updating a cluster plan.

## Official Source Content

# Manage Spending Limit for TiDB Cloud Serverless Scalable Clusters

> **Note:**
>
> The spending limit is only applicable to TiDB Cloud Serverless [scalable clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#scalable-cluster-plan).

Spending limit refers to the maximum amount of money that you are willing to spend on a particular workload in a month. It is a cost-control mechanism that allows you to set a budget for your TiDB Cloud Serverless scalable clusters.

For each organization in TiDB Cloud, you can create a maximum of five [free clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#free-cluster-plan) by default. To create more TiDB Cloud Serverless clusters, you need to add a credit card and create scalable clusters for the usage. But if you delete some of your previous clusters before creating more, the new cluster can still be created without a credit card.
## Usage quota

For the first five TiDB Cloud Serverless clusters in your organization, whether they are free or scalable, TiDB Cloud provides a free usage quota for each of them as follows:

- Row-based storage: 5 GiB
- Columnar storage: 5 GiB
- [Request Units (RUs)](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#request-unit): 50 million RUs per month

Once a cluster reaches its usage quota, it immediately denies any new connection attempts until you [increase the quota](#update-spending-limit) or the usage is reset upon the start of a new month. Existing connections established before reaching the quota will remain active but will experience throttling. For example, when the row-based storage of a cluster exceeds 5 GiB for a free cluster, the cluster automatically restricts any new connection attempts.

To learn more about the RU consumption of different resources (including read, write, SQL CPU, and network egress), the pricing details, and the throttled information, see [TiDB Cloud Serverless Pricing Details](https://www.pingcap.com/tidb-cloud-serverless-pricing-details).

If you want to create a TiDB Cloud Serverless cluster with an additional quota, you can edit the spending limit on the cluster creation page. For more information, see [Create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless).
## Update spending limit

For a TiDB Cloud Serverless free cluster, you can increase the usage quota by upgrading it to a scalable cluster. For an existing scalable cluster, you can adjust the monthly spending limit directly.

To update the spending limit for a TiDB Cloud Serverless cluster, perform the following steps:

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target cluster to go to its overview page.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. In the **Usage This Month** area, click **Upgrade to Scalable Cluster**.

    To adjust the spending limit for an existing scalable cluster, click <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M11 3.99998H6.8C5.11984 3.99998 4.27976 3.99998 3.63803 4.32696C3.07354 4.61458 2.6146 5.07353 2.32698 5.63801C2 6.27975 2 7.11983 2 8.79998V17.2C2 18.8801 2 19.7202 2.32698 20.362C2.6146 20.9264 3.07354 21.3854 3.63803 21.673C4.27976 22 5.11984 22 6.8 22H15.2C16.8802 22 17.7202 22 18.362 21.673C18.9265 21.3854 19.3854 20.9264 19.673 20.362C20 19.7202 20 18.8801 20 17.2V13M7.99997 16H9.67452C10.1637 16 10.4083 16 10.6385 15.9447C10.8425 15.8957 11.0376 15.8149 11.2166 15.7053C11.4184 15.5816 11.5914 15.4086 11.9373 15.0627L21.5 5.49998C22.3284 4.67156 22.3284 3.32841 21.5 2.49998C20.6716 1.67156 19.3284 1.67155 18.5 2.49998L8.93723 12.0627C8.59133 12.4086 8.41838 12.5816 8.29469 12.7834C8.18504 12.9624 8.10423 13.1574 8.05523 13.3615C7.99997 13.5917 7.99997 13.8363 7.99997 14.3255V16Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg> **Edit**.

3. Edit the monthly spending limit as needed. If you have not added a payment method, you will need to add a credit card after editing the limit.
4. Click **Update Cluster Plan**.
