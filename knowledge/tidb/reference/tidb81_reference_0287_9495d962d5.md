# Foreign key compatibility with TiDB tools

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/foreign-key.md`
- Source Title: `FOREIGN KEY Constraints`
- Source Heading Path: `FOREIGN KEY Constraints > Compatibility > Compatibility with TiDB tools`
- Source Line Ranges: `303-322`
- Source Scope: `all`
- Primary Component: `shared`
- Related Components: `br`, `dm`, `dumpling`, `lightning`, `ticdc`
- Topic Tags: `foreign-keys`, `compatibility`, `replication`, `backup-restore`, `import`, `binlog`, `data-consistency`, `foreign_key_checks`, `version-compatibility`, `tooling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0287_9495d962d5`
- Source ID: `tidb-docs-8.1:foreign-key.md#compatibility-with-tidb-tools`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c784e100c3facbc740693a5a107e5f59d151e09bdb9c117eb38ab5d78d644591`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/foreign-key#compatibility-with-tidb-tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/foreign-key.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether foreign keys are supported or require special handling with TiDB Binlog, DM, TiCDC, BR, TiDB Lightning, Dumpling, or sync-diff-inspector.
- Retrieval Keywords: TiDB Binlog does not support foreign keys, DM does not support foreign keys, foreign_key_checks, cascading operations are not replicated, data inconsistency, TiCDC v6.6.0 compatible with foreign keys, earlier than v6.6.0 might report an error, BR v6.6.0 compatible with foreign keys, restoring tables with foreign keys, TiDB Lightning foreign key target table, REFERENCES privilege, manually create the target table, Dumpling is compatible with foreign keys, sync-diff-inspector table schema inconsistent error, FOREIGN KEY INVALID
- Follow-up Guidance: The content also notes that sync-diff-inspector might report a table schema inconsistent error when database versions differ and the downstream TiDB has an invalid foreign key marked with the `/* FOREIGN KEY INVALID */` comment.
- Classification Note: This is reference content because it lists tool-by-tool compatibility behavior and exact foreign key related conditions across replication, restore, import, export, and comparison tools.

## Official Source Content

### Compatibility with TiDB tools

- [TiDB Binlog](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview) does not support foreign keys.
- [DM](https://docs.pingcap.com/tidb/stable/dm/dm-overview) does not support foreign keys. DM disables the [`foreign_key_checks`](https://docs.pingcap.com/tidb/stable/system-variables#foreign_key_checks) of the downstream TiDB when replicating data to TiDB. Therefore, the cascading operations caused by foreign keys are not replicated from the upstream to the downstream, which might cause data inconsistency.
- [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) v6.6.0 is compatible with foreign keys. The previous versions of TiCDC might report an error when replicating tables with foreign keys. It is recommended to disable the `foreign_key_checks` of the downstream TiDB cluster when using a TiCDC version earlier than v6.6.0.
- [BR](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview) v6.6.0 is compatible with foreign keys. The previous versions of BR might report an error when restoring tables with foreign keys to a v6.6.0 or later cluster. It is recommended to disable the `foreign_key_checks` of the downstream TiDB cluster before restoring the cluster when using a BR earlier than v6.6.0.
- When you use [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview), if the target table uses a foreign key, it is recommended to disable the `foreign_key_checks` of the downstream TiDB cluster before importing data. For versions earlier than v6.6.0, disabling this system variable does not take effect, and you need to grant the `REFERENCES` privilege for the downstream database user, or manually create the target table in the downstream database in advance to ensure smooth data import.

- [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) is compatible with foreign keys.

- When you use [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview) to compare data between the upstream and downstream databases, if the database versions are different and there is [an invalid foreign key in the downstream TiDB](#compatibility-between-tidb-versions), sync-diff-inspector might report a table schema inconsistent error. This is because TiDB v6.6.0 adds a `/* FOREIGN KEY INVALID */` comment for the invalid foreign key.
