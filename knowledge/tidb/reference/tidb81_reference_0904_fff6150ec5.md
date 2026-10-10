# TiDB Cloud changefeed billing, RCU sizing, pricing, and private data link cost

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-billing-ticdc-rcu.md`
- Source Title: `Changefeed Billing`
- Source Heading Path: `Changefeed Billing | Changefeed Billing > RCU cost | Changefeed Billing > RCU cost > Number of TiCDC RCUs | Changefeed Billing > RCU cost > Price | Changefeed Billing > Private Data Link cost`
- Source Line Ranges: `6-39`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`
- Topic Tags: `changefeed`, `billing`, `rcu`, `pricing`, `replication-performance`, `private-link`, `private-service-connect`, `data-transfer-cost`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0904_fff6150ec5`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-billing-ticdc-rcu.md#changefeed-billing`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8ddf0b0288adef7a7b94bd24904d3a20eb01e02c910c7cef10cc2b7074888813`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing-ticdc-rcu#changefeed-billing
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-billing-ticdc-rcu.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about TiDB Cloud changefeed billing, TiCDC RCU sizing versus replication performance, changefeed pricing references, or Private Data Link charges for Private Link or Private Service Connect.
- Retrieval Keywords: Changefeed Billing, TiCDC Replication Capacity Units, RCU cost, Number of TiCDC RCUs, Maximum replication performance, 2 RCUs 5,000 rows/s, 4 RCUs 10,000 rows/s, 8 RCUs 20,000 rows/s, 16 RCUs 40,000 rows/s, 24 RCUs 60,000 rows/s, 32 RCUs 80,000 rows/s, 40 RCUs 100,000 rows/s, Changefeed Cost, Private Data Link cost, Private Link, Private Service Connect, Data Transfer Cost, $0.01/GiB
- Follow-up Guidance: The content points to Changefeed Cost for supported regions and per-RCU pricing, and notes that performance data is for reference only with a recommendation to conduct a real workload test and contact TiDB Cloud support for assistance.
- Classification Note: This is a cloud reference chunk because it lists TiDB Cloud changefeed billing details, RCU-to-performance specifications, pricing references, and Private Data Link cost information.

## Official Source Content

# Changefeed Billing
## RCU cost

TiDB Cloud measures the capacity of [changefeeds](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview) in TiCDC Replication Capacity Units (RCUs). When you [create a changefeed](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview#create-a-changefeed) for a cluster, you can select an appropriate specification. The higher the RCU, the better the replication performance. You will be charged for these TiCDC changefeed RCUs.
### Number of TiCDC RCUs

The following table lists the specifications and corresponding replication performances for changefeeds:

| Specification | Maximum replication performance |
|---------------|---------------------------------|
| 2 RCUs        | 5,000 rows/s                    |
| 4 RCUs        | 10,000 rows/s                   |
| 8 RCUs        | 20,000 rows/s                   |
| 16 RCUs       | 40,000 rows/s                   |
| 24 RCUs       | 60,000 rows/s                   |
| 32 RCUs       | 80,000 rows/s                   |
| 40 RCUs       | 100,000 rows/s                  |

> **Note:**
>
> The preceding performance data is for reference only and might vary in different scenarios. It is strongly recommended that you conduct a real workload test before using the changefeed feature in a production environment. For further assistance, contact [TiDB Cloud support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
### Price

To learn about the supported regions and the price of TiDB Cloud for each TiCDC RCU, see [Changefeed Cost](https://www.pingcap.com/tidb-cloud-pricing-details/#changefeed-cost).
## Private Data Link cost

If you choose the **Private Link** or **Private Service Connect** network connectivity method, additional **Private Data Link** costs will be incurred. These charges fall under the [Data Transfer Cost](https://www.pingcap.com/tidb-dedicated-pricing-details/#data-transfer-cost) category.

The price of **Private Data Link** is **$0.01/GiB**, the same as **Data Processed** of [AWS Interface Endpoint pricing](https://aws.amazon.com/privatelink/pricing/#Interface_Endpoint_pricing), **Consumer data processing** of [Google Cloud Private Service Connect pricing](https://cloud.google.com/vpc/pricing#psc-forwarding-rules), and **Inbound/Outbound Data Processed** of [Azure Private Link pricing](https://azure.microsoft.com/en-us/pricing/details/private-link/).
