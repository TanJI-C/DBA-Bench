# BACKUP statement examples and options

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-backup.md`
- Source Title: `BACKUP | TiDB SQL Statement Reference`
- Source Heading Path: `BACKUP > Examples | BACKUP > Examples > Back up databases | BACKUP > Examples > Back up tables | BACKUP > Examples > Back up the entire cluster | BACKUP > Examples > External storages | BACKUP > Examples > Performance fine-tuning | BACKUP > Examples > Snapshot | BACKUP > Examples > Incremental backup`
- Source Line Ranges: `50-191`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `br`, `tidb`, `tikv`
- Topic Tags: `backup`, `examples`, `database-backup`, `table-backup`, `full-backup`, `external-storage`, `s3`, `gcs`, `rate-limit`, `checksum`, `concurrency`, `snapshot`, `incremental-backup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0538_43dec7497e`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-backup.md#examples`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `14e6d5ce4a772149fa5e77a6427a28f88fad29f01ef291637258907212c1bd81`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-backup#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-backup.md

## Retrieval Guidance

- Use When: Use this chunk when you need concrete `BACKUP` SQL examples, option usage, result columns, external storage syntax, snapshot backup forms, or incremental backup examples.
- Retrieval Keywords: BACKUP DATABASE `test` TO 'local:///mnt/backup/2020/04/', BACKUP TABLE `test`.`sbtest01`, BACKUP TABLE sbtest02, sbtest03, sbtest04, BACKUP DATABASE *, system tables will not be included into the backup, Destination, Size, BackupTS, Queue Time, Execution Time, s3://example-bucket-2020/backup-05/, URI Formats of External Storage Services, SEND_CREDENTIALS_TO_TIKV = FALSE, RATE_LIMIT = 120 MB/SECOND, CONCURRENCY = 8, CHECKSUM = FALSE, SNAPSHOT = 36 HOUR AGO, SNAPSHOT = '2020-04-01 12:00:00', SNAPSHOT = 415685305958400, MICROSECOND, SECOND, MINUTE, HOUR, DAY, WEEK, LAST_BACKUP = '2020-04-01 12:00:00', LAST_BACKUP = 415685305958400, incremental backup
- Follow-up Guidance: The source explains that `BackupTS` is the TSO of the snapshot and is useful for incremental backup, and that relative time units for `SNAPSHOT` are always singular.
- Classification Note: This is reference content because it provides official examples and option descriptions for database, table, full-cluster, external-storage, performance, snapshot, and incremental backup usage.

## Official Source Content

## Examples
### Back up databases

```sql
BACKUP DATABASE `test` TO 'local:///mnt/backup/2020/04/';
```

```sql
+------------------------------+-----------+-----------------+---------------------+---------------------+
| Destination                  | Size      | BackupTS        | Queue Time          | Execution Time      |
+------------------------------+-----------+-----------------+---------------------+---------------------+
| local:///mnt/backup/2020/04/ | 248665063 | 416099531454472 | 2020-04-12 23:09:48 | 2020-04-12 23:09:48 |
+------------------------------+-----------+-----------------+---------------------+---------------------+
1 row in set (58.453 sec)
```

In the example above, the `test` database is backed up into the local filesystem. The data is saved as SST files in the `/mnt/backup/2020/04/` directories distributed among all TiDB and TiKV nodes.

The first row of the result above is described as follows:

| Column | Description |
| :-------- | :--------- |
| `Destination` | The destination URL |
| `Size` |  The total size of the backup archive, in bytes |
| `BackupTS` | The TSO of the snapshot when the backup is created (useful for [incremental backup](#incremental-backup)) |
| `Queue Time` | The timestamp (in current time zone) when the `BACKUP` task is queued. |
| `Execution Time` | The timestamp (in current time zone) when the `BACKUP` task starts to run. |
### Back up tables

```sql
BACKUP TABLE `test`.`sbtest01` TO 'local:///mnt/backup/sbtest01/';
```

```sql
BACKUP TABLE sbtest02, sbtest03, sbtest04 TO 'local:///mnt/backup/sbtest/';
```
### Back up the entire cluster

```sql
BACKUP DATABASE * TO 'local:///mnt/backup/full/';
```

Note that the system tables (`mysql.*`, `INFORMATION_SCHEMA.*`, `PERFORMANCE_SCHEMA.*`, …) will not be included into the backup.
### External storages

BR supports backing up data to S3 or GCS:

```sql
BACKUP DATABASE `test` TO 's3://example-bucket-2020/backup-05/?access-key={YOUR_ACCESS_KEY}&secret-access-key={YOUR_SECRET_KEY}';
```

The URL syntax is further explained in [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).

When running on cloud environment where credentials should not be distributed, set the `SEND_CREDENTIALS_TO_TIKV` option to `FALSE`:

```sql
BACKUP DATABASE `test` TO 's3://example-bucket-2020/backup-05/'
    SEND_CREDENTIALS_TO_TIKV = FALSE;
```
### Performance fine-tuning

Use `RATE_LIMIT` to limit the average upload speed per TiKV node to reduce network bandwidth.

Before the backup is completed, `BACKUP` would perform a checksum against the data on the cluster to verify correctness. If you are confident that this verification is unnecessary, you can disable the check by setting the `CHECKSUM` parameter to `FALSE`.

To specify the number of concurrent tasks that BR can execute for backing up tables and indices, use the `CONCURRENCY` parameter. This parameter controls the thread pool size within BR, optimizing the performance and efficiency of backup operations.

One task represents one table range or one index range, according to the backup schemas. For one table with one index, two tasks are used to back up this table. The default value of `CONCURRENCY` is `4`. If you need to back up lots of tables or indices, increase its value.

```sql
BACKUP DATABASE `test` TO 's3://example-bucket-2020/backup-06/'
    RATE_LIMIT = 120 MB/SECOND
    CONCURRENCY = 8
    CHECKSUM = FALSE;
```
### Snapshot

Specify a timestamp, TSO or relative time to backup historical data.

```sql
-- relative time
BACKUP DATABASE `test` TO 'local:///mnt/backup/hist01'
    SNAPSHOT = 36 HOUR AGO;

-- timestamp (in current time zone)
BACKUP DATABASE `test` TO 'local:///mnt/backup/hist02'
    SNAPSHOT = '2020-04-01 12:00:00';

-- timestamp oracle
BACKUP DATABASE `test` TO 'local:///mnt/backup/hist03'
    SNAPSHOT = 415685305958400;
```

The supported units for relative time are:

* MICROSECOND
* SECOND
* MINUTE
* HOUR
* DAY
* WEEK

Note that, following SQL standard, the units are always singular.
### Incremental backup

Supply the `LAST_BACKUP` option to only backup the changes between the last backup to the current snapshot.

```sql
-- timestamp (in current time zone)
BACKUP DATABASE `test` TO 'local:///mnt/backup/hist02'
    LAST_BACKUP = '2020-04-01 12:00:00';

-- timestamp oracle
BACKUP DATABASE `test` TO 'local:///mnt/backup/hist03'
    LAST_BACKUP = 415685305958400;
```
