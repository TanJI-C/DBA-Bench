# Force replicate tables without a valid index

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-manage-changefeed.md`
- Source Title: `Manage Changefeeds`
- Source Heading Path: `Manage Changefeeds > Replicate tables without a valid index`
- Source Line Ranges: `261-272`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `changefeed`, `force-replicate`, `valid-index`, `data-consistency`, `data-redundancy`, `warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0180_13402e20f7`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-manage-changefeed.md#replicate-tables-without-a-valid-index`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `114c2154bd00df71e623ebd9368807f5b10ffb1f9862cbaa7a7325c3811d6bd5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed#replicate-tables-without-a-valid-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-manage-changefeed.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiCDC changefeed configuration that allows replicating tables without a valid index and its documented consistency warning.
- Retrieval Keywords: force-replicate = true, Replicate tables without a valid index, tables without a valid index, data consistency is not guaranteed, data redundancy, INSERT, REPLACE, at least once, effective index, primary key, AUTO RANDOM
- Follow-up Guidance: The content states that if data redundancy is unacceptable, an effective index can be added, such as a primary key column with the `AUTO RANDOM` attribute.
- Classification Note: This is classified as configuration because the content centers on enabling the `force-replicate` option in the changefeed configuration file and explains its consequences.

## Official Source Content

## Replicate tables without a valid index

Since v4.0.8, TiCDC supports replicating tables that have no valid index by modifying the task configuration. To enable this feature, configure in the changefeed configuration file as follows:

```toml
force-replicate = true
```

> **Warning:**
>
> When `force-replicate` is set to `true`, data consistency is not guaranteed. For tables without a valid index, operations such as `INSERT` and `REPLACE` are not reentrant, so there is a risk of data redundancy. TiCDC guarantees that data is distributed only at least once during the replication process. Therefore, enabling this feature to replicate tables without a valid index will definitely cause data redundancy. If you do not accept data redundancy, it is recommended to add an effective index, such as adding a primary key column with the `AUTO RANDOM` attribute.
