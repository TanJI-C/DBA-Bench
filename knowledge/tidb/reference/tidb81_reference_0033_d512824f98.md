# RawKV backup and restore overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/rawkv-backup-and-restore.md`
- Source Title: `Back Up and Restore RawKV`
- Source Heading Path: `Back Up and Restore RawKV`
- Source Line Ranges: `5-10`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`, `pd`
- Topic Tags: `rawkv`, `backup`, `restore`, `overview`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0033_d512824f98`
- Source ID: `tidb-docs-8.1:br/rawkv-backup-and-restore.md#back-up-and-restore-rawkv`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4ce4e9cc97e19fb96dfbc3f257a05739884a03e265bdb6d08c74db3cb7443c59`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/rawkv-backup-and-restore#back-up-and-restore-rawkv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/rawkv-backup-and-restore.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about whether BR supports backup and restore for a deployment that uses TiKV and PD as RawKV without TiDB.
- Retrieval Keywords: Back Up and Restore RawKV, RawKV, TiKV-BR, backup and restore, TiKV and PD without TiDB, KV database
- Follow-up Guidance: For more details, see TiKV-BR User Docs.
- Classification Note: This is reference content because it gives an overview definition of RawKV and states that TiKV-BR supports backup and restore for products that use RawKV.

## Official Source Content

# Back Up and Restore RawKV

TiKV and PD can constitute a KV database when used without TiDB, which is called RawKV. TiKV-BR supports data backup and restore for products that use RawKV. 

For more details, see [TiKV-BR User Docs](https://tikv.org/docs/latest/concepts/explore-tikv-features/backup-restore/).
