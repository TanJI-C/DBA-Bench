# Restore mysql schema system tables

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-snapshot-guide.md`
- Source Title: `Snapshot Backup and Restore Guide`
- Source Heading Path: `Snapshot Backup and Restore Guide > Restore cluster snapshots > Restore tables in the `mysql` schema`
- Source Line Ranges: `127-181`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tidb`, `sql`
- Topic Tags: `system-tables`, `mysql-schema`, `restore`, `privileges`, `compatibility`, `version-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0010_ac1e6f19ab`
- Source ID: `tidb-docs-8.1:br/br-snapshot-guide.md#restore-tables-in-the-mysql-schema`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9e9d67901b4851ec2910491081ed6cf167dabeb4500d8c4625797394301803a8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#restore-tables-in-the-mysql-schema
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-snapshot-guide.md

## Retrieval Guidance

- Use When: Use this when you need the restore rules for `mysql` schema system tables, including which tables BR restores and the compatibility checks for system privilege data.
- Retrieval Keywords: Restore tables in the `mysql` schema, mysql.columns_priv, mysql.db, mysql.default_roles, mysql.global_grants, mysql.global_priv, mysql.role_edges, mysql.tables_priv, mysql.user, mysql.bind_info, mysql.stat_*, mysql.tidb, mysql.global_variables, system privilege, compatible, number of columns, ENUM values
- Follow-up Guidance: BR checks target-cluster and backup-data compatibility before restoring system privilege data.
- Classification Note: This chunk is a recovery guide for BR behavior when restoring `mysql` schema system tables and lists both restorable and non-restorable system tables.

## Official Source Content

### Restore tables in the `mysql` schema

- Starting from BR v5.1.0, when you back up snapshots, BR automatically backs up the **system tables** in the `mysql` schema, but does not restore these system tables by default. 
- Starting from v6.2.0, BR lets you specify `--with-sys-table` to restore **data in some system tables**. 
- Starting from v7.6.0, BR enables `--with-sys-table` by default, which means that BR restores **data in some system tables** by default.

**BR can restore data in the following system tables:**

```
+----------------------------------+
| mysql.columns_priv               |
| mysql.db                         |
| mysql.default_roles              |
| mysql.global_grants              |
| mysql.global_priv                |
| mysql.role_edges                 |
| mysql.tables_priv                |
| mysql.user                       |
| mysql.bind_info                  |
+----------------------------------+
```

**BR does not restore the following system tables:**

- Statistics tables (`mysql.stat_*`). But statistics can be restored. See [Back up statistics](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#back-up-statistics).
- System variable tables (`mysql.tidb` and `mysql.global_variables`)
- [Other system tables](https://github.com/pingcap/tidb/blob/release-8.1/br/pkg/restore/systable_restore.go#L31)

```
+-----------------------------------------------------+
| capture_plan_baselines_blacklist                    |
| column_stats_usage                                  |
| gc_delete_range                                     |
| gc_delete_range_done                                |
| global_variables                                    |
| stats_buckets                                       |
| stats_extended                                      |
| stats_feedback                                      |
| stats_fm_sketch                                     |
| stats_histograms                                    |
| stats_history                                       |
| stats_meta                                          |
| stats_meta_history                                  |
| stats_table_locked                                  |
| stats_top_n                                         |
| tidb                                                |
+-----------------------------------------------------+
```

When you restore data related to system privilege, note that before restoring data, BR checks whether the system tables in the target cluster are compatible with those in the backup data. "Compatible" means that all the following conditions are met:

- The target cluster has the same system tables as the backup data.
- The **number of columns** in the system privilege table of the target cluster is the same as that in the backup data. The column order is not important.
- The columns in the system privilege table of the target cluster are compatible with that in the backup data. If the data type of the column is a type with a length (such as integer and string), the length in the target cluster must be >= the length in the backup data. If the data type of the column is an `ENUM` type, the number of `ENUM` values in the target cluster must be a superset of that in the backup data.
