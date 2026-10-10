# Columnar storage pricing and cost-effectiveness FAQs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-faqs.md`
- Source Title: `TiDB Cloud Serverless FAQs`
- Source Heading Path: `TiDB Cloud Serverless FAQs > Billing and metering FAQs > What costs are involved when using columnar storage in TiDB Cloud Serverless? | TiDB Cloud Serverless FAQs > Billing and metering FAQs > Is using columnar storage more expensive?`
- Source Line Ranges: `124-137`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tiflash`
- Topic Tags: `billing`, `metering`, `columnar-storage`, `pricing`, `analytics`, `storage-costs`, `request-units`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0830_74997ec326`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-faqs.md#what-costs-are-involved-when-using-columnar-storage-in-tidb-cloud-serverless`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f95cf746a29fc898ddc817cd974f5a6f9076cac32ea49c800ed19afa386844ad`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-faqs#what-costs-are-involved-when-using-columnar-storage-in-tidb-cloud-serverless
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-faqs.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about TiDB Cloud Serverless columnar storage pricing, extra replica costs, replication charges, or whether analytics on columnar storage are more cost-effective than row-based storage.
- Retrieval Keywords: TiDB Cloud Serverless columnar storage pricing, columnar storage extra replica, row-based storage pricing similar, replication of data from row-based to columnar storage does not incur extra charges, Is using columnar storage more expensive, analytical queries cost-effective, TPC-H benchmark one-third cost, TiFlash, TiDB Cloud Serverless pricing details
- Follow-up Guidance: For detailed pricing information, see TiDB Cloud Serverless pricing details.
- Classification Note: This is reference content because it states billing and metering facts about columnar storage costs, extra replica impact, and analytics cost-effectiveness in TiDB Cloud Serverless.

## Official Source Content

### What costs are involved when using columnar storage in TiDB Cloud Serverless?

The pricing for columnar storage in TiDB Cloud Serverless is similar to that for row-based storage. When you use columnar storage, an additional replica is created to store your data (without indexes). The replication of data from row-based to columnar storage does not incur extra charges.

For detailed pricing information, see [TiDB Cloud Serverless pricing details](https://www.pingcap.com/tidb-serverless-pricing-details/).
### Is using columnar storage more expensive?

Columnar storage in TiDB Cloud Serverless incurs additional costs due to the extra replica, which requires more storage and resources for data replication. However, columnar storage becomes more cost-effective when running analytical queries.

According to the TPC-H benchmark test, the cost of running analytic queries on columnar storage is about one-third of the cost when using row-based storage.

Therefore, while there might be an initial cost due to the extra replica, the reduced computational costs during analytics can make it more cost-effective for specific use cases. Especially for users with analytical demands, columnar storage can significantly reduce costs, offering considerable cost savings opportunities.
