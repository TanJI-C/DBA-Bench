# Foreign key compatibility across TiDB versions

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/foreign-key.md`
- Source Title: `FOREIGN KEY Constraints`
- Source Heading Path: `FOREIGN KEY Constraints > Compatibility | FOREIGN KEY Constraints > Compatibility > Compatibility between TiDB versions`
- Source Line Ranges: `285-302`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `foreign-keys`, `compatibility`, `version-upgrade`, `invalid-constraints`, `show-create-table`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0002_7d27d2eeb1`
- Source ID: `tidb-docs-8.1:foreign-key.md#compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4d089048c8ac890abd64488688c8de6c637123911d347f1f8970f24955b55ae8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/foreign-key#compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/foreign-key.md

## Retrieval Guidance

- Use When: Use this chunk when you need version compatibility details for foreign keys created before and after v6.6.0, including how invalid foreign keys appear in table definitions.
- Retrieval Keywords: Compatibility between TiDB versions, before v6.6.0, v6.6.0 or later, foreign keys are ineffective, SHOW CREATE TABLE, FOREIGN KEY INVALID, /* FOREIGN KEY INVALID */, invalid foreign key, upgrade a TiDB cluster
- Follow-up Guidance: The source states that SHOW CREATE TABLE can be used to check whether foreign keys are effective, and invalid foreign keys include the /* FOREIGN KEY INVALID */ comment.
- Classification Note: This is release-related content because it explains foreign key behavior changes across TiDB versions and the compatibility state of foreign keys created before v6.6.0.

## Official Source Content

## Compatibility
### Compatibility between TiDB versions

Before v6.6.0, TiDB supports the syntax of creating foreign keys, but the created foreign keys are ineffective. If you upgrade a TiDB cluster created before v6.6.0 to v6.6.0 or later, the foreign keys created before the upgrade are still ineffective. Only the foreign keys created in v6.6.0 or later versions are effective. You can delete the invalid foreign key and create a new one to make the foreign key constraints effective. You can use the `SHOW CREATE TABLE` statement to check whether the foreign keys are effective. The invalid foreign key has a `/* FOREIGN KEY INVALID */` comment.

```sql
mysql> SHOW CREATE TABLE child\G
***************************[ 1. row ]***************************
Table        | child
Create Table | CREATE TABLE `child` (
  `id` int(11) DEFAULT NULL,
  `pid` int(11) DEFAULT NULL,
  KEY `idx_pid` (`pid`),
  CONSTRAINT `fk_1` FOREIGN KEY (`pid`) REFERENCES `test`.`parent` (`id`) ON DELETE CASCADE /* FOREIGN KEY INVALID */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
```
