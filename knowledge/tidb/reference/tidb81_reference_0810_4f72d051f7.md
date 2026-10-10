# TiDB Cloud Dedicated cluster limits and organization quotas

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/limitations-and-quotas.md`
- Source Title: `TiDB Cloud Dedicated Limitations and Quotas`
- Source Heading Path: `TiDB Cloud Dedicated Limitations and Quotas | TiDB Cloud Dedicated Limitations and Quotas > Cluster Limits | TiDB Cloud Dedicated Limitations and Quotas > Cluster Quotas`
- Source Line Ranges: `5-35`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `limits`, `quotas`, `cluster-sizing`, `organization-resources`, `availability-zones`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0810_4f72d051f7`
- Source ID: `tidb-docs-8.1:tidb-cloud/limitations-and-quotas.md#tidb-cloud-dedicated-limitations-and-quotas`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `63d368321979f24974795deb0a03d307c49e8279eed66432f5fcd53c759fed56`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/limitations-and-quotas#tidb-cloud-dedicated-limitations-and-quotas
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/limitations-and-quotas.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiDB Cloud Dedicated cluster limits or organization-level quotas for component counts, availability zones, or data region copies.
- Retrieval Keywords: TiDB Cloud Dedicated Limitations and Quotas, Cluster Limits, Cluster Quotas, Number of copies for each data region, 3 copies, Number of Availability Zones for a cross-zone deployment, 3 availability zones, Maximum number of total TiDB nodes for all clusters in your organization, 10, Maximum number of total TiKV nodes for all clusters in your organization, 15, Maximum number of total TiFlash nodes for all clusters in your organization, 5, organization quotas, cluster sizing
- Follow-up Guidance: If these limits or quotas present a problem for your organization, contact TiDB Cloud Support; for common usage limitations of TiDB, refer to TiDB Limitations.
- Classification Note: This is reference content because it provides fixed TiDB Cloud Dedicated limits and default organization quotas in tables.

## Official Source Content

# TiDB Cloud Dedicated Limitations and Quotas

TiDB Cloud limits how many of each kind of component you can create in a [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster, and the common usage limitations of TiDB. In addition, there are some organization-level quotas to limit the amount of resources created by users to prevent from creating more resources than you actually need. These tables outline limits and quotas.

> **Note:**
>
> If any of these limits or quotas present a problem for your organization, please contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
## Cluster Limits

| Component | Limit |
|:-|:-|
| Number of copies for each [data region](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#region) | 3 |
| Number of Availability Zones for a cross-zone deployment | 3 |

> **Note:**
>
> If you want to learn more about common usage limitations of TiDB, please refer to [TiDB Limitations](https://docs.pingcap.com/tidb/stable/tidb-limitations).
## Cluster Quotas

| Component | Quota (default) |
|:-|:-|
| Maximum number of total TiDB nodes for all clusters in your organization | 10 |
| Maximum number of total TiKV nodes for all clusters in your organization | 15 |
| Maximum number of total TiFlash nodes for all clusters in your organization | 5 |

> **Note:**
>
> If any of these limits or quotas present a problem for your organization, please contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
