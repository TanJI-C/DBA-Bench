# SQL new features including flashback and TiFlash compaction

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.4.0.md`
- Source Title: `TiDB 6.4.0 Release Notes`
- Source Heading Path: `TiDB 6.4.0 Release Notes > New features > SQL`
- Source Line Ranges: `36-59`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`, `tikv`, `ticdc`
- Topic Tags: `sql`, `flashback-cluster`, `flashback-database`, `point-in-time-restore`, `compaction`, `gc`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0348_8ea59638b8`
- Source ID: `tidb-docs-8.1:releases/release-6.4.0.md#sql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `824fd1e6390b1f2064f4a5a33bb26e1da9b3b6fb0ab093f0bb9346916d3bee77`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.4.0#sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving SQL feature changes in TiDB 6.4.0 related to TiFlash compaction, point-in-time cluster rollback, or restoring a dropped database.
- Retrieval Keywords: SQL, ALTER TABLE table_name COMPACT [PARTITION PartitionNameList] [engine_type REPLICA], compact TiFlash replicas of specified partitions in a table immediately, FLASHBACK CLUSTER TO TIMESTAMP, restore a cluster to a specific point in time, within the Garbage Collection (GC) lifetime, pause PITR, TiCDC replication tasks might fail, FLASHBACK DATABASE, restore a deleted database, DROP, garbage collection (GC) life time
- Follow-up Guidance: Before executing FLASHBACK CLUSTER TO TIMESTAMP, the content says to pause PITR and replication tasks such as TiCDC and restart them after FLASHBACK is completed, otherwise replication tasks might fail.
- Classification Note: This is classified as a SQL release chunk because all listed features are SQL statements or SQL-related restore and compaction capabilities.

## Official Source Content

### SQL

* Support using a SQL statement to compact TiFlash replicas of specified partitions in a table immediately [#5315](https://github.com/pingcap/tiflash/issues/5315) @[hehechen](https://github.com/hehechen)

    Since v6.2.0, TiDB has supported the feature of [compacting physical data immediately](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact#alter-table--compact) on a full-table replica of TiFlash. You can choose the right time to manually execute SQL statements to immediately compact the physical data in TiFlash, which helps to reduce storage space and improve query performance. In v6.4.0, we refine the granularity of TiFlash replica data to be compacted and support compacting TiFlash replicas of specified partitions in a table immediately.

    By executing the SQL statement `ALTER TABLE table_name COMPACT [PARTITION PartitionNameList] [engine_type REPLICA]`, you can immediately compact TiFlash replicas of specified partitions in a table.

    For more information, see [User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact#compact-tiflash-replicas-of-specified-partitions-in-a-table).

* Support restoring a cluster to a specific point in time by using `FLASHBACK CLUSTER TO TIMESTAMP` (experimental) [#37197](https://github.com/pingcap/tidb/issues/37197) [#13303](https://github.com/tikv/tikv/issues/13303) @[Defined2014](https://github.com/Defined2014) @[bb7133](https://github.com/bb7133) @[JmPotato](https://github.com/JmPotato) @[Connor1996](https://github.com/Connor1996) @[HuSharp](https://github.com/HuSharp) @[CalvinNeo](https://github.com/CalvinNeo)

    You can use the `FLASHBACK CLUSTER TO TIMESTAMP` syntax to restore a cluster to a specific point in time quickly within the Garbage Collection (GC) lifetime. This feature helps you to easily and quickly undo DML misoperations. For example, you can use this syntax to restore the original cluster in minutes after mistakenly executing `DELETE` without a `WHERE` clause. This feature does not rely on database backups and supports rolling back data at different time points to determine the exact time when data changes. Note that `FLASHBACK CLUSTER TO TIMESTAMP` cannot replace database backups.

    Before executing `FLASHBACK CLUSTER TO TIMESTAMP`, you need to pause PITR and replication tasks running on such tools as TiCDC and restart them after the `FLASHBACK` is completed. Otherwise, replication tasks might fail.

    For more information, see [User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster).

* Support restoring a deleted database by using `FLASHBACK DATABASE` [#20463](https://github.com/pingcap/tidb/issues/20463) @[erwadba](https://github.com/erwadba)

    By using `FLASHBACK DATABASE`, you can restore a database and its data deleted by `DROP` within the garbage collection (GC) life time. This feature does not depend on any external tools. You can quickly restore data and metadata using SQL statements.

    For more information, see [User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-database).
