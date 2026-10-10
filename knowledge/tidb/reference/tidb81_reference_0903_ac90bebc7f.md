# Recovery group billing and pricing reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-billing-recovery-group.md`
- Source Title: `Recovery Group Billing`
- Source Heading Path: `Recovery Group Billing | Recovery Group Billing > Pricing`
- Source Line Ranges: `5-14`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tikv`
- Topic Tags: `billing`, `pricing`, `recovery-group`, `tikv-size`, `data-processing`, `regions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0903_ac90bebc7f`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-billing-recovery-group.md#recovery-group-billing`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d4ffd8247f9607094392f80b1cb1dff478d2492fe5bb9f280b70fc7614da0e09`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing-recovery-group#recovery-group-billing
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-billing-recovery-group.md

## Retrieval Guidance

- Use When: Use this chunk when asking how TiDB Cloud bills a recovery group, including TiKV node size in the primary cluster and per-GiB data processing costs across same-region or cross-region replication.
- Retrieval Keywords: Recovery Group Billing, Pricing, TiDB Cloud recovery groups, recovery group billing, deployed size of your TiKV nodes, primary cluster of the recovery group, data processing per GiB basis, secondary cluster in another region, within the same region, Recovery Group Cost, supported regions
- Follow-up Guidance: For supported regions and detailed pricing, see the Recovery Group Cost page linked from this content.
- Classification Note: This is reference content because it states the billing basis and pricing lookup location for recovery groups in TiDB Cloud.

## Official Source Content

# Recovery Group Billing

TiDB Cloud bills for recovery groups based on the deployed size of your TiKV nodes in the primary cluster of the recovery group. When you [create a recovery group](https://docs.pingcap.com/tidb/stable/tidb-cloud/recovery-group-get-started) for a cluster, you can select the primary cluster for the recovery group. The larger the TiKV configuration, the higher the cost for recovery group protection.

TiDB Cloud also bills for data processing per GiB basis. The data processing price varies depending on whether the data is replicated to a secondary cluster in another region, or within the same region.
## Pricing

To learn about the supported regions and the pricing for TiDB Cloud recovery groups, see [Recovery Group Cost](https://www.pingcap.com/tidb-cloud-pricing-details/#recovery-group-cost).
