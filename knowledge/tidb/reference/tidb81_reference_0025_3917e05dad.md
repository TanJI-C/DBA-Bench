# BR version compatibility and reference links

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/backup-and-restore-overview.md`
- Source Title: `TiDB Backup & Restore Overview`
- Source Heading Path: `TiDB Backup & Restore Overview > Compatibility > Version compatibility | TiDB Backup & Restore Overview > Compatibility > Version compatibility > BR version compatibility matrix before TiDB v6.6.0 | TiDB Backup & Restore Overview > Compatibility > Version compatibility > BR version compatibility matrix between TiDB v6.5.0 and v8.1.0 | TiDB Backup & Restore Overview > See also`
- Source Line Ranges: `120-175`
- Source Scope: `shared`
- Primary Component: `br`
- Related Components: `tidb`, `shared`
- Topic Tags: `version-compatibility`, `backup`, `restore`, `log-backup`, `system-tables`, `compatibility-matrix`, `requirements-check`, `references`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0025_3917e05dad`
- Source ID: `tidb-docs-8.1:br/backup-and-restore-overview.md#version-compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `54016c8f01cbafc89aaddfacee3f17c8e8a0b31c8a310abcd6f333fad665b440`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview#version-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/backup-and-restore-overview.md

## Retrieval Guidance

- Use When: Use this chunk when checking BR and TiDB backup or restore version compatibility, major-version matching, system table restore compatibility, or related BR backup and restore reference links.
- Retrieval Keywords: BR version compatibility, BR version compatibility matrix before TiDB v6.6.0, BR version compatibility matrix between TiDB v6.5.0 and v8.1.0, same major version as your TiDB cluster, --check-requirements=false, --with-sys-table, --with-sys-table=false, [BR:Restore:ErrRestoreIncompatibleSys]incompatible system table, full backup compatibility matrix, log backup compatibility matrix, mysql system tables, Issue #43717, known issue #36379, non-system tables compatibility, TiDB Snapshot Backup and Restore Guide, TiDB Log Backup and PITR Guide, Backup Storages
- Follow-up Guidance: The source also points to the TiDB Snapshot Backup and Restore Guide, the TiDB Log Backup and PITR Guide, and Backup Storages for related backup and restore references.
- Classification Note: This is reference content because it provides compatibility rules, matrices, option names, error text, and links for BR backup and restore behavior across TiDB versions.

## Official Source Content

### Version compatibility

> **Note:**
>
> It is recommended to use the BR of the same major version as your TiDB cluster for backup and restoration.

Before performing backup and restore, BR compares the TiDB cluster version with its own and checks their compatibility. If the versions are incompatible, BR reports an error and exits. To forcibly skip the version check, you can set `--check-requirements=false`. Note that skipping the version check might introduce incompatibility in data.

Starting from v7.0.0, TiDB gradually supports performing backup and restore operations through SQL statements. Therefore, it is strongly recommended to use the BR tool of the same major version as the TiDB cluster when backing up and restoring cluster data, and avoid performing data backup and restore operations across major versions. This helps ensure smooth execution of restore operations and data consistency. Starting from v7.6.0, BR restores data in some `mysql` system tables by default, that is, the `--with-sys-table` option is set to `true` by default. When restoring data to a TiDB cluster with a different version, if you encounter an error similar to `[BR:Restore:ErrRestoreIncompatibleSys]incompatible system table` due to different schemas of system tables, you can set `--with-sys-table=false` to skip restoring the system tables and avoid this error.
#### BR version compatibility matrix before TiDB v6.6.0

The compatibility information for BR before TiDB v6.6.0 is as follows:

| Backup version (vertical) \ Restore version (horizontal)   | Restore to TiDB v6.0 | Restore to TiDB v6.1 | Restore to TiDB v6.2 | Restore to TiDB v6.3, v6.4, or v6.5 | Restore to TiDB v6.6 |
|  ----  |  ----  | ---- | ---- | ---- | ---- |
| TiDB v6.0, v6.1, v6.2, v6.3, v6.4, or v6.5 snapshot backup | Compatible (known issue [#36379](https://github.com/pingcap/tidb/issues/36379): if backup data contains an empty schema, BR might report an error.) | Compatible | Compatible | Compatible | Compatible (BR must be v6.6) |
| TiDB v6.3, v6.4, v6.5, or v6.6 log backup| Incompatible | Incompatible | Incompatible | Compatible | Compatible |
#### BR version compatibility matrix between TiDB v6.5.0 and v8.1.0

This section introduces the BR compatibility information for all [Long-Term Support (LTS)](https://docs.pingcap.com/tidb/stable/releases/versioning#long-term-support-releases) versions between TiDB v6.5.0 and v8.1.0 (including v6.5.0, v7.1.0, v7.5.0, v8.1.0):

> **Note:**
>
> Known issue: Starting from version v7.2.0, some system table fields in newly created clusters are case-insensitive. However, for clusters that are **upgraded online** from versions earlier than v7.2.0 to v7.2.0 or later, the corresponding system table fields remain case-sensitive. Backup and restore operations involving system tables between these two types of clusters might fail. For more details, see [Issue #43717](https://github.com/pingcap/tidb/issues/43717).

The following table lists the compatibility matrix for full backups. Note that all information in the table applies to newly created clusters. For clusters upgraded from a version earlier than v7.2.0 to v7.2.0 or later, their behavior is consistent with that of backups from v7.1.0.

| Backup version | Compatible restore versions | Incompatible restore versions |
|:--|:--|:--|
| v6.5.0 | 7.1.0 | v7.5.0 and later |
| v7.1.0 | - | v7.5.0 and later |
| v7.5.0 | v7.5.0 and later | - |
| v8.1.0 | v8.1.0 and later | - |

The following table lists the compatibility matrix for log backups. Note that all information in the table applies to newly created clusters. For clusters upgraded from a version earlier than v7.2.0 to v7.2.0 or later, their behavior is consistent with that of backups from v7.1.0.

| Backup version | Compatible restore versions | Incompatible restore versions |
|:--|:--|:--|
| v6.5.0 | 7.1.0 | v7.5.0 and later |
| v7.1.0 | - | v7.5.0 and later |
| v7.5.0 | v7.5.0 and later | - |
| v8.1.0 | v8.1.0 and later | - |

> **Note:**
>
> - When only data of non-system tables is backed up (full backup or log backup), all versions are compatible with each other.
> - In scenarios where restoring the `mysql` system table is incompatible, you can resolve the problem by setting `--with-sys-table=false` to skip restoring all system tables, or use a more fine-grained filter to just skip incompatible system tables, for example: `--filter '*.*' --filter "__TiDB_BR_Temporary_*.*" --filter '!mysql.*' --filter 'mysql.bind_info' --filter 'mysql.user' --filter 'mysql.global_priv' --filter 'mysql.global_grants' --filter 'mysql.default_roles' --filter 'mysql.role_edges' --filter '!sys.*' --filter '!INFORMATION_SCHEMA.*' --filter '!PERFORMANCE_SCHEMA.*' --filter '!METRICS_SCHEMA.*' --filter '!INSPECTION_SCHEMA.*'`.
> - `-` means that there are no compatibility restrictions for the corresponding scenario.
## See also

- [TiDB Snapshot Backup and Restore Guide](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide)
- [TiDB Log Backup and PITR Guide](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide)
- [Backup Storages](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages)
