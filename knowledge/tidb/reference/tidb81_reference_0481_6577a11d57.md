# Placement policy compatibility with features and tools

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/placement-rules-in-sql.md`
- Source Title: `Placement Rules in SQL`
- Source Heading Path: `Placement Rules in SQL > Compatibility with other features | Placement Rules in SQL > Compatibility with tools`
- Source Line Ranges: `455-482`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `lightning`, `ticdc`, `tiflash`, `tidb`
- Topic Tags: `compatibility`, `temporary-tables`, `data-at-rest`, `data-in-transit`, `tiflash-replicas`, `primary-region`, `regions`, `backup-restore`, `lightning-import`, `replication-tools`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0481_6577a11d57`
- Source ID: `tidb-docs-8.1:placement-rules-in-sql.md#compatibility-with-other-features`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `73798dead0c79d84f71597f877fae4a45a5a559237ee75be392ebce2692313c3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/placement-rules-in-sql#compatibility-with-other-features
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/placement-rules-in-sql.md

## Retrieval Guidance

- Use When: Use this chunk when asking about placement policy compatibility with temporary tables, data-at-rest versus data-in-transit behavior, TiFlash replicas, PRIMARY_REGION or REGIONS syntax, or tool support in BR, TiDB Lightning, TiCDC, and TiDB Binlog.
- Retrieval Keywords: temporary tables do not support placement policies, data at rest, data in transit, TiFlash replicas, create TiFlash replicas, PRIMARY_REGION, REGIONS, Backup & Restore (BR) 6.0, before v6.0 BR does not support backing up and restoring placement policies, TiDB Lightning not compatible yet, error when TiDB Lightning imports backup data that contains placement policies, TiCDC 6.0 ignores placement policies, TiDB Binlog 6.0 ignores placement policies, does not replicate the policies to the downstream
- Follow-up Guidance: For BR restore errors involving placement rules, the content points to the FAQ entry "Why does an error occur when I restore placement rules to a cluster".
- Classification Note: This is reference content because it summarizes stated compatibility limits and minimum supported versions for placement policies across features and tools.

## Official Source Content

## Compatibility with other features

- Temporary tables do not support placement policies.
- Placement policies only ensure that data at rest resides on the correct TiKV nodes but do not guarantee that data in transit (via either user queries or internal operations) only occurs in a specific region.
- To configure TiFlash replicas for your data, you need to [create TiFlash replicas](https://docs.pingcap.com/tidb/stable/tiflash/create-tiflash-replicas) rather than using placement policies.
- Syntactic sugar rules are permitted for setting `PRIMARY_REGION` and `REGIONS`. In the future, we plan to add varieties for `PRIMARY_RACK`, `PRIMARY_ZONE`, and `PRIMARY_HOST`. See [issue #18030](https://github.com/pingcap/tidb/issues/18030).
## Compatibility with tools

| Tool Name | Minimum supported version | Description |
| --- | --- | --- |
| Backup & Restore (BR) | 6.0 | Before v6.0, BR does not support backing up and restoring placement policies. For more information, see [Why does an error occur when I restore placement rules to a cluster](https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq#why-does-an-error-occur-when-i-restore-placement-rules-to-a-cluster). |
| TiDB Lightning | Not compatible yet | An error is reported when TiDB Lightning imports backup data that contains placement policies  |
| TiCDC | 6.0 | Ignores placement policies, and does not replicate the policies to the downstream |
| TiDB Binlog | 6.0 | Ignores placement policies, and does not replicate the policies to the downstream |

| Tool Name | Minimum supported version | Description |
| --- | --- | --- |
| TiDB Lightning | Not compatible yet | An error is reported when TiDB Lightning imports backup data that contains placement policies  |
| TiCDC | 6.0 | Ignores placement policies, and does not replicate the policies to the downstream |
