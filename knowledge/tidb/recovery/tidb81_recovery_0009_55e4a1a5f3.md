# Snapshot restore commands, version-specific restore behavior, and partial restore options

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-snapshot-guide.md`
- Source Title: `Snapshot Backup and Restore Guide`
- Source Heading Path: `Snapshot Backup and Restore Guide > Restore cluster snapshots | Snapshot Backup and Restore Guide > Restore cluster snapshots > Restore a database or a table`
- Source Line Ranges: `62-126`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `snapshot-restore`, `full-restore`, `database-restore`, `table-restore`, `table-filter`, `region-scattering`, `restore-performance`, `version-specific`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0009_55e4a1a5f3`
- Source ID: `tidb-docs-8.1:br/br-snapshot-guide.md#restore-cluster-snapshots`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `45f20193416ec0c2e7721d795616c0d2d61eb1e9b3c58914c5e84366fd736b98`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#restore-cluster-snapshots
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-snapshot-guide.md

## Retrieval Guidance

- Use When: Use this chunk when looking for BR snapshot restore commands for full, database, table, or filtered table restores, or for version-specific notes about coarse-grained Region scattering and restore speed.
- Retrieval Keywords: tiup br restore full, tiup br restore db, tiup br restore table, --db, --table, --filter, -f, table filter, coarse-grained Region scattering algorithm, --granularity="coarse-grained", BR v7.5.0, BR v7.6.0, BR v8.0.0, Full Restore success summary, restore-data-size(after-compressed), BackupTS
- Follow-up Guidance: The source further includes examples for restoring the `test` database, restoring the `test.usertable` table, and restoring multiple tables matching the `db*.tbl*` filter rule.
- Classification Note: This is classified as a recovery chunk because the content focuses on restoring snapshot backups and partial data with BR restore commands and related restore behavior notes.

## Official Source Content

## Restore cluster snapshots

> **Note:**
>
> - For BR v7.5.0 and earlier versions, the snapshot restore speed per TiKV node is approximately 100 MiB/s.
> - Starting from BR v7.6.0, to address potential restore bottlenecks in scenarios with large-scale Regions, BR supports accelerating restore through the coarse-grained Region scattering algorithm (experimental). You can enable this feature by specifying the command-line parameter `--granularity="coarse-grained"`.
> - Starting from BR v8.0.0, the snapshot restore through the coarse-grained Region scattering algorithm is generally available (GA) and enabled by default. BR improves the snapshot restore speed significantly by implementing various optimizations such as adopting the coarse-grained Region scattering algorithm, creating databases and tables in batches, reducing the mutual impact between SST file downloads and ingest operations, and accelerating the restore of table statistics. According to test results from real-world cases, the SST file download speed for snapshot restore is improved by approximately up to 10 times, the data restore speed per TiKV node stabilizes at 1.2 GiB/s, the end-to-end restore speed is improved by approximately 1.5 to 3 times, and 100 TiB of data can be restored within one hour.

You can restore a snapshot backup by running the `tiup br restore full` command. Run `tiup br restore full --help` to see the help information:

The following example restores the [preceding backup snapshot](#back-up-cluster-snapshots) to a target cluster:

```shell
tiup br restore full --pd "${PD_IP}:2379" \
--storage "s3://backup-101/snapshot-202209081330?access-key=${access-key}&secret-access-key=${secret-access-key}"
```

During restore, a progress bar is displayed in the terminal as shown below. When the progress bar advances to 100%, the restore task is completed and statistics such as total restore time, average restore speed, and total data size are displayed.

```shell
Full Restore <------------------------------------------------------------------------------> 100.00%
*** ["Full Restore success summary"] *** [total-take=4.344617542s] [total-kv=5] [total-kv-size=327B] [average-speed=75.27B/s] [restore-data-size(after-compressed)=4.813kB] [Size=4813] [BackupTS=435844901803917314]
```
### Restore a database or a table

BR supports restoring partial data of a specified database or table from backup data. This feature allows you to filter out unwanted data and back up only a specific database or table.

**Restore a database**

To restore a database to a cluster, run the `tiup br restore db` command. The following example restores the `test` database from the backup data to the target cluster:

```shell
tiup br restore db \
--pd "${PD_IP}:2379" \
--db "test" \
--storage "s3://backup-101/snapshot-202209081330?access-key=${access-key}&secret-access-key=${secret-access-key}"
```

In the preceding command, `--db` specifies the name of the database to be restored.

**Restore a table**

To restore a single table to a cluster, run the `tiup br restore table` command. The following example restores the `test.usertable` table from the backup data to the target cluster:

```shell
tiup br restore table --pd "${PD_IP}:2379" \
--db "test" \
--table "usertable" \
--storage "s3://backup-101/snapshot-202209081330?access-key=${access-key}&secret-access-key=${secret-access-key}"
```

In the preceding command, `--db` specifies the name of the database to be restored, and `--table` specifies the name of the table to be restored.

**Restore multiple tables with table filter**

To restore multiple tables with more complex filter rules, run the `tiup br restore full` command and specify the [table filters](https://docs.pingcap.com/tidb/stable/table-filter) with `--filter` or `-f`. The following example restores tables that match the `db*.tbl*` filter rule from the backup data to the target cluster:

```shell
tiup br restore full \
--pd "${PD_IP}:2379" \
--filter 'db*.tbl*' \
--storage "s3://backup-101/snapshot-202209081330?access-key=${access-key}&secret-access-key=${secret-access-key}"
```
