# Data migration and backup features

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.2.0.md`
- Source Title: `TiDB 6.2.0 Release Notes`
- Source Heading Path: `TiDB 6.2.0 Release Notes > New features > Data migration`
- Source Line Ranges: `177-231`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `lightning`, `dm`
- Topic Tags: `backup`, `restore`, `pitr`, `continuous validation`, `amazon s3`, `disk quota`, `physical import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0035_b36a6f0eb3`
- Source ID: `tidb-docs-8.1:releases/release-6.2.0.md#data-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d8bcd2838e855c5d76609f87ea0148d6beb4fe44e9c8f80d34aa3adc7715c419`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.2.0#data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.2.0 data migration, backup, restore, PITR, DM validation, S3 region detection, or TiDB Lightning import enhancements.
- Retrieval Keywords: Data migration, BR, restore user and privilege data, --with-sys-table, mysql schema, point-in-time recovery, PITR, backup and restoration of log and snapshot, RPO less than 20 minutes, history data auditing, DM continuous data validation, upstream binlog, downstream, inconsistent data, missing records, Amazon S3 buckets, automatically identify the region, TiDB Lightning, disk_quota, sorted-kv-dir, physical import mode, backend='local', production clusters, pausing the scheduling of tables, local backend, physical import mode, tidb backend, logical import mode
- Follow-up Guidance: The source links to user documents for BR restore of mysql schema tables, backup and restore overview, DM continuous data validation, and TiDB Lightning physical import mode and overview.
- Classification Note: This is classified under recovery with BR as the primary component because the content centers on backup and restore capabilities while also covering related migration features in Lightning and DM.

## Official Source Content

### Data migration

* BR supports restoring user and privilege data

    BR supports restoring user and privilege data when it performs a normal restoration. You do not need any additional restoration plan to restore user and privilege data. To enable this feature, specify the `--with-sys-table` parameter when you use BR to restore data.

    [User document](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#restore-tables-in-the-mysql-schema) [#35395](https://github.com/pingcap/tidb/issues/35395) @[D3Hunter](https://github.com/D3Hunter)

* Support point-in-time recovery (PITR) based on backup and restoration of log and snapshot

    PITR is implemented based on the backup and restoration of log and snapshot. It allows you to restore the snapshots of a cluster at any point in history to a new cluster. This feature satisfies the following needs:

    - Reduce the RPO in disaster recovery to less than 20 minutes.
    - Handle the cases of incorrect writes from applications by, for example, rolling back data to before the error event.
    - Perform history data auditing to meet the requirements of laws and regulations.

    This feature has usage limitations. For details, refer to the user document.

    [User document](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview) [#29501](https://github.com/pingcap/tidb/issues/29501) @[joccau](https://github.com/joccau)

* DM supports continuous data validation (experimental)

    Continuous data validation is used to continuously compare the upstream binlog with the data written into the downstream during data migration. The validator identifies data exceptions, such as inconsistent data and missing records.

    This feature solves the issues of lagging validation and excessive resource consumption in common full data validation schemes.

    [User document](https://docs.pingcap.com/tidb/stable/dm/dm-continuous-data-validation) [#4426](https://github.com/pingcap/tiflow/issues/4426) @[D3Hunter](https://github.com/D3Hunter) @[buchuitoudegou](https://github.com/buchuitoudegou)

* Automatically identify the region of Amazon S3 buckets

    Data migration tasks can automatically identify the region of Amazon S3 buckets. You do not need to explicitly pass the region parameter.

    [#34275](https://github.com/pingcap/tidb/issues/34275) @[WangLe1321](https://github.com/WangLe1321)

* Support configuring disk quota for TiDB Lightning (experimental)

    When TiDB Lightning imports data in the physical import mode (backend='local'), sorted-kv-dir must have enough space to store the source data. Insufficient disk space might cause the import task to fail. Now you can use the new `disk_quota` configuration to limit the total amount of disk space used by TiDB Lightning, so that the import task can be completed normally even when sorted-kv-dir does not have enough storage space.

    [User document](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#configure-disk-quota-new-in-v620) [#446](https://github.com/pingcap/tidb-lightning/issues/446) @[buchuitoudegou](https://github.com/buchuitoudegou)

* TiDB Lightning supports importing data to production clusters in the physical import mode

    Previously, the physical import mode of TiDB Lightning (backend='local') had a significant impact on the target cluster. For example, during the migration, PD global scheduling is paused. Therefore, the previous physical import mode is only suitable for initial data import.

    TiDB Lightning improves the existing physical import mode. By allowing pausing the scheduling of tables, the impact of import is reduced from cluster level to table level. That is, you can read and write tables that are not being imported.

    This feature does not need manual configuration. If your TiDB cluster is v6.1.0 or later versions and TiDB Lightning is v6.2.0 or later versions, the new physical import mode takes effect automatically.

    [User document](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#scope-of-pausing-scheduling-during-import) [#35148](https://github.com/pingcap/tidb/issues/35148) @[sleepymole](https://github.com/sleepymole)

* Refactor the [user documentation of TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) to make its structure more reasonable and clear. The terms for "backend" is also modified to lower the understanding barrier for new users:

    - Replace "local backend" with "physical import mode".
    - Replace "tidb backend" with "logical import mode".
