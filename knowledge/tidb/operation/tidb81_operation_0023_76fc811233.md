# Partial snapshot backup for databases, tables, and filters

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-snapshot-manual.md`
- Source Title: `TiDB Snapshot Backup and Restore Command Manual`
- Source Heading Path: `TiDB Snapshot Backup and Restore Command Manual > Back up a database or a table | TiDB Snapshot Backup and Restore Command Manual > Back up a database or a table > Back up a database | TiDB Snapshot Backup and Restore Command Manual > Back up a database or a table > Back up a table | TiDB Snapshot Backup and Restore Command Manual > Back up a database or a table > Back up multiple tables with table filter`
- Source Line Ranges: `59-112`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tiup`, `pd`
- Topic Tags: `partial-backup`, `database-backup`, `table-backup`, `table-filter`, `filtering`, `s3-storage`, `backup-command`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0023_76fc811233`
- Source ID: `tidb-docs-8.1:br/br-snapshot-manual.md#back-up-a-database-or-a-table`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7587d46af48babd25a6072039571257fa87a3c59b9047a9f18cfb23676591bc3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#back-up-a-database-or-a-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-snapshot-manual.md

## Retrieval Guidance

- Use When: Use this chunk when looking for BR commands to back up a specific database, a specific table, or multiple tables matched by table filters from snapshot or incremental backup scope.
- Retrieval Keywords: tiup br backup db, tiup br backup table, tiup br backup full --filter, --db, --table, --filter, -f, table filter, db*.tbl*, Back up a database, Back up a table, Back up multiple tables with table filter
- Follow-up Guidance: It explains that `--db` specifies the database name, `--table` specifies the table name, and other parameters are the same as those in cluster snapshot backup.
- Classification Note: This is classified as an operation chunk because the content provides concrete BR backup commands for database-level, table-level, and filtered multi-table backup scenarios.

## Official Source Content

## Back up a database or a table

Backup & Restore (BR) supports backing up partial data of a specified database or table from a cluster snapshot or incremental data backup. This feature allows you to filter out unwanted data from snapshot backup and incremental data backup, and back up only business-critical data.
### Back up a database

To back up a database in a cluster, run the `tiup br backup db` command.

The following example backs up the `test` database to Amazon S3:

```shell
tiup br backup db \
    --pd "${PD_IP}:2379" \
    --db test \
    --storage "s3://${backup_collection_addr}/snapshot-${date}?access-key=${access-key}&secret-access-key=${secret-access-key}" \
    --ratelimit 128 \
    --log-file backuptable.log
```

In the preceding command, `--db` specifies the database name, and other parameters are the same as those in [Back up TiDB cluster snapshots](#back-up-cluster-snapshots).
### Back up a table

To back up a table in a cluster, run the `tiup br backup table` command.

The following example backs up the `test.usertable` table to Amazon S3:

```shell
tiup br backup table \
    --pd "${PD_IP}:2379" \
    --db test \
    --table usertable \
    --storage "s3://${backup_collection_addr}/snapshot-${date}?access-key=${access-key}&secret-access-key=${secret-access-key}" \
    --ratelimit 128 \
    --log-file backuptable.log
```

In the preceding command, `--db` and `--table` specify the database name and table name respectively, and other parameters are the same as those in [Back up TiDB cluster snapshots](#back-up-cluster-snapshots).
### Back up multiple tables with table filter

To back up multiple tables with more criteria, run the `tiup br backup full` command and specify the [table filters](https://docs.pingcap.com/tidb/stable/table-filter) with `--filter` or `-f`.

The following example backs up tables that match the `db*.tbl*` filter rule to Amazon S3:

```shell
tiup br backup full \
    --pd "${PD_IP}:2379" \
    --filter 'db*.tbl*' \
    --storage "s3://${backup_collection_addr}/snapshot-${date}?access-key=${access-key}&secret-access-key=${secret-access-key}" \
    --ratelimit 128 \
    --log-file backupfull.log
```
