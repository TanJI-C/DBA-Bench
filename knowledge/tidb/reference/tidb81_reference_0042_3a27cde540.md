# GBK component compatibility by version

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/character-set-gbk.md`
- Source Title: `GBK`
- Source Heading Path: `GBK > Component compatibility`
- Source Line Ranges: `86-96`
- Source Scope: `all`
- Primary Component: `shared`
- Related Components: `br`, `dm`, `lightning`, `ticdc`, `tiflash`, `tidb`
- Topic Tags: `gbk`, `component-compatibility`, `version-support`, `migration`, `import`, `replication`, `recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0042_3a27cde540`
- Source ID: `tidb-docs-8.1:character-set-gbk.md#component-compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `65c96426ed422fa4e7b9184fee2a134fd379e8c74717c740f1e14cf8b7ba19ca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/character-set-gbk#component-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/character-set-gbk.md

## Retrieval Guidance

- Use When: Use this chunk when verifying which TiDB ecosystem components and versions support GBK tables for migration, import, replication, or recovery.
- Retrieval Keywords: Component compatibility, TiFlash GBK, DM charset=GBK, TiDB Data Migration GBK, TiDB Lightning charset=GBK, TiCDC charset=GBK, BR charset=GBK, Backup & Restore GBK, v5.4.0, v6.1.0, replicating charset=GBK tables, recovering charset=GBK tables, importing charset=GBK tables, migrating charset=GBK tables
- Follow-up Guidance: The source enumerates version limits for TiFlash, DM, TiDB Lightning, TiCDC, and BR when working with `charset=GBK` tables.
- Classification Note: This is a reference chunk because it provides a compatibility matrix by component and version for GBK-related migration, import, replication, and recovery support.

## Official Source Content

## Component compatibility

- Currently, TiFlash does not support the GBK character set.

- TiDB Data Migration (DM) does not support migrating `charset=GBK` tables to TiDB clusters earlier than v5.4.0.

- TiDB Lightning does not support importing `charset=GBK` tables to TiDB clusters earlier than v5.4.0.

- TiCDC versions earlier than v6.1.0 do not support replicating `charset=GBK` tables. No version of TiCDC supports replicating `charset=GBK` tables to TiDB clusters earlier than v6.1.0.

- Backup & Restore (BR) versions earlier than v5.4.0 do not support recovering `charset=GBK` tables. No version of BR supports recovering `charset=GBK` tables to TiDB clusters earlier than v5.4.0.
