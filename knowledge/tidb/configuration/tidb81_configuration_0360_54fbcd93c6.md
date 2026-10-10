# Enable MPP mode with tidb_enforce_mpp

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Forcibly enable the MPP mode`
- Source Line Ranges: `58-68`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`
- Topic Tags: `mpp`, `session-variables`, `sql-commands`, `query-execution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0360_54fbcd93c6`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#forcibly-enable-the-mpp-mode`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9ea9490c0dc190ce1719baf0208224b44457e8b4675c4652fd6e1a72f23f56d9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#forcibly-enable-the-mpp-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the SQL statement that forcibly enables MPP mode for query execution in TiDB with TiFlash.
- Retrieval Keywords: set @@tidb_enforce_mpp = ON, tidb_enforce_mpp, Enable MPP mode, Forcibly enable the MPP mode, MPP mode, TiDB parameters, TiFlash
- Follow-up Guidance: After MPP mode is enabled, the source continues with content about the enabled state.
- Classification Note: This is classified as configuration because the official content shows setting the session variable tidb_enforce_mpp using a SQL command in TiDB.

## Official Source Content

Enable MPP mode:

```sql
mysql> set @@tidb_enforce_mpp = ON;

Query OK, 0 rows affected (0.00 sec)
```

After MPP mode is enabled:
