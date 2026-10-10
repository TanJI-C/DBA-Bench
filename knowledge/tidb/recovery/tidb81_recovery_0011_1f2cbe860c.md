# Snapshot restore for full cluster and database-level recovery

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-snapshot-manual.md`
- Source Title: `TiDB Snapshot Backup and Restore Command Manual`
- Source Heading Path: `TiDB Snapshot Backup and Restore Command Manual > Restore cluster snapshots | TiDB Snapshot Backup and Restore Command Manual > Restore a database or a table | TiDB Snapshot Backup and Restore Command Manual > Restore a database or a table > Restore a database`
- Source Line Ranges: `165-214`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tikv`, `tidb`, `tiup`
- Topic Tags: `snapshot-restore`, `full-restore`, `database-restore`, `with-sys-table`, `system-tables`, `sql-bindings`, `statistics-restore`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0011_1f2cbe860c`
- Source ID: `tidb-docs-8.1:br/br-snapshot-manual.md#restore-cluster-snapshots`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ad60fa72cbbf5c963bb000587c9aa1c19bba0d0a80809bf46d0b023334b883b0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#restore-cluster-snapshots
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-snapshot-manual.md

## Retrieval Guidance

- Use When: Use this chunk when looking for BR snapshot restore commands for a full cluster or a single database, including `--with-sys-table`, restore rate limiting, verification behavior, and the same-name requirement for database restore.
- Retrieval Keywords: tiup br restore full, tiup br restore db, --with-sys-table, system tables, SQL bindings, mysql.stat_*, mysql.tidb, mysql.global_variables, --db, backupmeta, restorefull.log, restore_db.log, Full Restore, verify the restored data
- Follow-up Guidance: It also states that restoring a database requires the `--db` name to match the database name recorded in the `backupmeta` file, otherwise the restore fails.
- Classification Note: This is classified as a recovery chunk because the content describes snapshot restore procedures and restore-specific constraints for full-cluster and database-level recovery.

## Official Source Content

## Restore cluster snapshots

You can restore a TiDB cluster snapshot by running the `tiup br restore full` command.

```shell
tiup br restore full \
    --pd "${PD_IP}:2379" \
    --with-sys-table \
    --storage "s3://${backup_collection_addr}/snapshot-${date}?access-key=${access-key}&secret-access-key=${secret-access-key}" \
    --ratelimit 128 \
    --log-file restorefull.log
```

In the preceding command:

- `--with-sys-table`: BR restores **data in some system tables**, including account permission data and SQL bindings, and statistics (see [Back up statistics](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#back-up-statistics)). However, it does not restore statistics tables (`mysql.stat_*`) and system variable tables (`mysql.tidb` and `mysql.global_variables`). For more information, see [Restore tables in the `mysql` schema](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#restore-tables-in-the-mysql-schema).
- `--ratelimit`: The maximum speed **per TiKV** performing restore tasks. The unit is in MiB/s.
- `--log-file`: The target file where the `br` log is written.

During restore, a progress bar is displayed in the terminal as shown below. When the progress bar advances to 100%, the restore task is completed. Then `br` will verify the restored data to ensure data security.

```shell
Full Restore <---------/...............................................> 17.12%.
```
## Restore a database or a table

You can use `br` to restore partial data of a specified database or table from backup data. This feature allows you to filter out data that you do not need during the restore.
### Restore a database

To restore a database to a cluster, run the `tiup br restore db` command.

The following example restores the `test` database from the backup data to the target cluster:

```shell
tiup br restore db \
    --pd "${PD_IP}:2379" \
    --db "test" \
    --ratelimit 128 \
    --storage "s3://${backup_collection_addr}/snapshot-${date}?access-key=${access-key}&secret-access-key=${secret-access-key}" \
    --log-file restore_db.log
```

In the preceding command, `--db` specifies the name of the database to be restored and other parameters are the same as those in [Restore TiDB cluster snapshots](#restore-cluster-snapshots).

> **Note:**
>
> When you restore the backup data, the database name specified by `--db` must be the same as the one specified by `-- db` in the backup command. Otherwise, the restore fails. This is because the metafile of the backup data (`backupmeta` file) records the database name, and you can only restore data to the database with the same name. The recommended method is to restore the backup data to the database with the same name in another cluster.
