# DDL interruption handling, post-migration validation, and long-term replication metadata backup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-best-practices.md`
- Source Title: `TiDB Data Migration (DM) Best Practices`
- Source Heading Path: `TiDB Data Migration (DM) Best Practices > Best practices during migration > Interrupted migration task due to failed DDL | TiDB Data Migration (DM) Best Practices > Data validation after data migration | TiDB Data Migration (DM) Best Practices > Long-term data replication`
- Source Line Ranges: `220-234`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `shared`
- Topic Tags: `failed-ddl`, `task-interruption`, `data-validation`, `consistency-check`, `incremental-replication`, `metadata-backup`, `long-term-replication`, `configuration-export`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0085_7b321f0bcb`
- Source ID: `tidb-docs-8.1:dm/dm-best-practices.md#interrupted-migration-task-due-to-failed-ddl`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bdf7fe8be2c88bbfcccff0c9467c086048f3ed556ebe4e2e875e6cac85d8a404`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-best-practices#interrupted-migration-task-due-to-failed-ddl
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-best-practices.md

## Retrieval Guidance

- Use When: You need guidance for a DM migration task interrupted by a failed DDL statement, post-migration data consistency validation, or backing up metadata for long-term data replication.
- Retrieval Keywords: DM supports skipping or replacing DDL statements, failed DDL statements, Handle Failed DDL Statements, data migration, validate the consistency of data, sync-diff-inspector, Data Check in the DM Replication Scenario, automatic manage the table list, continuous data validation for incremental replication, Continuous Data Validation in DM, back up the metadata, rebuild the migration cluster, version control of the migration task, Export and Import Data Sources and Task Configuration of Clusters
- Follow-up Guidance: See the linked DM and sync-diff-inspector documentation for failed DDL handling, data validation, continuous validation, and metadata export/import details.
- Classification Note: This chunk covers DM best practices for interrupted migrations due to failed DDL, validation after migration, continuous validation for incremental replication, and metadata backup for long-term replication.

## Official Source Content

### Interrupted migration task due to failed DDL

DM supports skipping or replacing DDL statements that cause a migration task to interrupt. For details, see [Handle Failed DDL Statements](https://docs.pingcap.com/tidb/stable/dm/handle-failed-ddl-statements#usage-examples).
## Data validation after data migration

It is recommended that you validate the consistency of data after data migration. TiDB provides [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview) to help you complete the data validation.

Now sync-diff-inspector can automatically manage the table list to be checked for data consistency through DM tasks. Compared with the previous manual configuration, it is more efficient. For details, see [Data Check in the DM Replication Scenario](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/dm-diff).

Since DM v6.2.0, DM supports continuous data validation for incremental replication. For details, see [Continuous Data Validation in DM](https://docs.pingcap.com/tidb/stable/dm/dm-continuous-data-validation).
## Long-term data replication

If you use DM to perform a long-term data replication task, it is necessary to back up the metadata. On the one hand, it ensures the ability to rebuild the migration cluster. On the other hand, it can implement the version control of the migration task. For details, see [Export and Import Data Sources and Task Configuration of Clusters](https://docs.pingcap.com/tidb/stable/dm/dm-export-import-config).
